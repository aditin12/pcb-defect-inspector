"""
Evaluates the trained YOLOv8 checkpoint on the held-out test split:
mAP@0.5, mAP@0.5:0.95, per-class precision/recall, and inference speed.

Run:
    cd ml/src
    python evaluate.py
"""
import json
import os
import time

from ultralytics import YOLO

from config import YOLO_DATA_DIR, MODELS_DIR, RESULTS_DIR, CLASS_NAMES


def main():
    weights_path = os.path.join(MODELS_DIR, "pcb_yolov8_best.pt")
    if not os.path.exists(weights_path):
        raise FileNotFoundError(f"No trained weights at {weights_path}. Run train_yolo.py first.")

    model = YOLO(weights_path)
    data_yaml = os.path.join(YOLO_DATA_DIR, "data.yaml")

    metrics = model.val(data=data_yaml, split="test", project=RESULTS_DIR, name="test_eval", exist_ok=True)

    # Per-class AP@0.5 and mean precision/recall are available directly from Ultralytics' metrics object.
    per_class = {}
    for i, class_name in enumerate(CLASS_NAMES):
        per_class[class_name] = {
            "AP50": float(metrics.box.ap50[i]) if i < len(metrics.box.ap50) else None,
            "precision": float(metrics.box.p[i]) if i < len(metrics.box.p) else None,
            "recall": float(metrics.box.r[i]) if i < len(metrics.box.r) else None,
        }

    # Rough inference speed on a handful of test images
    test_images_dir = os.path.join(YOLO_DATA_DIR, "images", "test")
    sample_images = [
        os.path.join(test_images_dir, f) for f in os.listdir(test_images_dir)
    ][:20]
    start = time.time()
    for img_path in sample_images:
        model.predict(img_path, verbose=False)
    elapsed = time.time() - start
    ms_per_image = (elapsed / max(len(sample_images), 1)) * 1000

    summary = {
        "mAP50": float(metrics.box.map50),
        "mAP50_95": float(metrics.box.map),
        "ms_per_image": ms_per_image,
        "per_class": per_class,
    }

    out_path = os.path.join(RESULTS_DIR, "yolo_test_metrics.json")
    with open(out_path, "w") as f:
        json.dump(summary, f, indent=2)

    print("\n" + "=" * 60)
    print("TEST SET RESULTS")
    print("=" * 60)
    print(f"mAP@0.5:      {summary['mAP50']:.4f}")
    print(f"mAP@0.5:0.95: {summary['mAP50_95']:.4f}")
    print(f"Inference:    {ms_per_image:.1f} ms/image")
    print("\nPer-class AP@0.5:")
    for name, m in per_class.items():
        ap = m["AP50"]
        print(f"  {name:<18} {ap:.4f}" if ap is not None else f"  {name:<18} n/a")
    print(f"\nSaved -> {out_path}")
    print(f"Confusion matrix + PR curves also saved under {os.path.join(RESULTS_DIR, 'test_eval')}")


if __name__ == "__main__":
    main()
