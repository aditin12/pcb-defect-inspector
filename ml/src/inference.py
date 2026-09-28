"""
Single entry point for running detection + severity scoring on one image.
Both a standalone CLI (for quick testing / generating result plots) and
the FastAPI backend import this module, so there is exactly one definition
of "what happens when you show the model a board image."

Run standalone:
    cd ml/src
    python inference.py --image /path/to/board.jpg
"""
import argparse
import os

from ultralytics import YOLO

from config import MODELS_DIR, CLASS_NAMES
from severity import compute_severity, summarize_board


class PCBInspector:
    def __init__(self, weights_path: str = None, confidence_threshold: float = 0.25):
        self.weights_path = weights_path or os.path.join(MODELS_DIR, "pcb_yolov8_best.pt")
        if not os.path.exists(self.weights_path):
            raise FileNotFoundError(
                f"No trained weights at {self.weights_path}. Run train_yolo.py first."
            )
        self.model = YOLO(self.weights_path)
        self.confidence_threshold = confidence_threshold

    def inspect(self, image_path_or_array) -> dict:
        """Returns {"detections": [...], "board_summary": {...}, "annotated_image": np.ndarray, "inference_time_ms": float}"""
        import time
        start = time.time()
        results = self.model.predict(
            image_path_or_array, conf=self.confidence_threshold, verbose=False
        )[0]

        img_h, img_w = results.orig_shape
        detections = []

        for box in results.boxes:
            class_idx = int(box.cls.item())
            confidence = float(box.conf.item())
            xyxy = box.xyxy[0].tolist()   # [xmin, ymin, xmax, ymax] in pixels
            xmin, ymin, xmax, ymax = xyxy

            box_area_fraction = ((xmax - xmin) * (ymax - ymin)) / (img_w * img_h)
            class_name = CLASS_NAMES[class_idx]
            severity = compute_severity(class_name, confidence, box_area_fraction)

            detections.append({
                "class_name": class_name,
                "confidence": round(confidence, 4),
                "bbox": {"xmin": xmin, "ymin": ymin, "xmax": xmax, "ymax": ymax},
                "severity": severity,
            })

        # Highest-severity, then highest-confidence first -- most actionable items on top.
        severity_rank = {"high": 2, "medium": 1, "low": 0}
        detections.sort(key=lambda d: (severity_rank[d["severity"]["level"]], d["confidence"]), reverse=True)

        board_summary = summarize_board(detections)
        annotated_image = results.plot()  # BGR numpy array with boxes drawn, from Ultralytics
        inference_time_ms = (time.time() - start) * 1000

        return {
            "detections": detections,
            "board_summary": board_summary,
            "annotated_image": annotated_image,
            "image_size": {"width": img_w, "height": img_h},
            "inference_time_ms": inference_time_ms,
        }


if __name__ == "__main__":
    import cv2

    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True)
    parser.add_argument("--conf", type=float, default=0.25)
    args = parser.parse_args()

    inspector = PCBInspector(confidence_threshold=args.conf)
    result = inspector.inspect(args.image)

    print(f"\nBoard summary: {result['board_summary']}")
    for d in result["detections"]:
        print(f"  {d['class_name']:<18} conf={d['confidence']:.2f}  "
              f"severity={d['severity']['level']} ({d['severity']['score']})")

    out_path = "inspection_result.png"
    cv2.imwrite(out_path, result["annotated_image"])
    print(f"\nAnnotated image saved to {out_path}")
