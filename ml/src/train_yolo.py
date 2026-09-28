"""
Trains a YOLOv8 object detector on the PCB defect dataset.

Uses Ultralytics' training loop directly (it already implements
augmentation, LR scheduling, checkpointing, and early stopping internally
and well) rather than reimplementing a training loop from scratch --
for object detection specifically, hand-rolling YOLO's loss/anchor
machinery would be reinventing a very well-tested wheel for no benefit.
What we control and own here is the *data prep*, the *severity scoring*,
and the *RAG explanation layer* built on top of its output.

Run:
    cd ml/src
    python train_yolo.py
"""
import os
import shutil

from ultralytics import YOLO

from config import YOLO_DATA_DIR, MODELS_DIR, RESULTS_DIR, EPOCHS, BATCH_SIZE, IMAGE_SIZE, BASE_MODEL


def main():
    data_yaml = os.path.join(YOLO_DATA_DIR, "data.yaml")
    if not os.path.exists(data_yaml):
        raise FileNotFoundError(
            f"No dataset found at {data_yaml}. Run prepare_data.py first."
        )

    model = YOLO(BASE_MODEL)  # loads COCO-pretrained weights -- this IS the transfer learning step

    results = model.train(
        data=data_yaml,
        epochs=EPOCHS,
        batch=BATCH_SIZE,
        imgsz=IMAGE_SIZE,
        patience=15,                # early stopping
        project=RESULTS_DIR,
        name="pcb_yolov8_run",
        exist_ok=True,
        seed=42,
        # Augmentation tuned down from YOLO's aggressive defaults: PCB defects
        # are small, precisely-located features -- heavy mosaic/mixup can
        # blend them into unrecognizable noise on a dataset this size (693 images).
        mosaic=0.3,
        mixup=0.0,
        degrees=10,
        translate=0.05,
        scale=0.2,
        fliplr=0.5,
        flipud=0.5,
    )

    # Copy the best checkpoint to the stable path the backend expects.
    best_weights = os.path.join(RESULTS_DIR, "pcb_yolov8_run", "weights", "best.pt")
    stable_path = os.path.join(MODELS_DIR, "pcb_yolov8_best.pt")
    shutil.copy2(best_weights, stable_path)

    print(f"\nTraining complete. Best weights copied to: {stable_path}")
    print(f"Full training run (curves, confusion matrix, sample predictions) saved under: "
          f"{os.path.join(RESULTS_DIR, 'pcb_yolov8_run')}")
    print("\nNext: run evaluate.py for a held-out test-set report.")


if __name__ == "__main__":
    main()
