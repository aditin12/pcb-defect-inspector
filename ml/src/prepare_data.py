"""
Converts the PCB Defects dataset (Pascal VOC XML annotations) into YOLO
detection format and writes a stratified, seeded train/val/test split plus
the data.yaml Ultralytics needs for training.

DATASET
The Kaggle "PCB Defects" dataset (based on Peking University's open PCB
defect benchmark) ships as:
    images/<board_type>/*.jpg
    Annotations/<board_type>/*.xml   (Pascal VOC format: <object><name>,
                                       <bndbox><xmin>,<ymin>,<xmax>,<ymax>)
Folder naming varies slightly across mirrors, so this script walks the
source directory and pairs images with annotations by filename stem
rather than assuming an exact path.

USAGE
    1. Download "PCB Defects" from Kaggle and unzip it
    2. python prepare_data.py --source /path/to/unzipped/PCB_DATASET
"""
import argparse
import os
import random
import shutil
import xml.etree.ElementTree as ET

from config import CLASS_NAMES, RAW_DIR, YOLO_DATA_DIR, TRAIN_SPLIT, VAL_SPLIT, SPLIT_SEED

CLASS_TO_IDX = {name: i for i, name in enumerate(CLASS_NAMES)}

# Some mirrors of this dataset use slightly different label spellings.
LABEL_ALIASES = {
    "missing_hole": "missing_hole",
    "mousebite": "mouse_bite",
    "mouse_bite": "mouse_bite",
    "open_circuit": "open_circuit",
    "opencircuit": "open_circuit",
    "short": "short",
    "spur": "spur",
    "spurious_copper": "spurious_copper",
    "spurious copper": "spurious_copper",
    "spuriouscopper": "spurious_copper",
}


def find_pairs(source_root: str):
    """Walks source_root, finds every .xml annotation, and pairs it with the
    image of the same filename stem (search by stem since folder layout
    varies across dataset mirrors)."""
    xml_files = {}
    image_files = {}

    for root, _, files in os.walk(source_root):
        for f in files:
            stem, ext = os.path.splitext(f)
            ext = ext.lower()
            if ext == ".xml":
                xml_files[stem] = os.path.join(root, f)
            elif ext in (".jpg", ".jpeg", ".png", ".bmp"):
                image_files[stem] = os.path.join(root, f)

    pairs = [(image_files[stem], xml_files[stem]) for stem in xml_files if stem in image_files]
    return pairs


def parse_voc_xml(xml_path: str):
    """Returns (img_width, img_height, [(class_idx, xmin, ymin, xmax, ymax), ...])"""
    tree = ET.parse(xml_path)
    root = tree.getroot()

    size = root.find("size")
    width = int(size.find("width").text)
    height = int(size.find("height").text)

    boxes = []
    for obj in root.findall("object"):
        raw_name = obj.find("name").text.strip().lower()
        class_name = LABEL_ALIASES.get(raw_name)
        if class_name is None:
            print(f"  Warning: unknown label '{raw_name}' in {xml_path}, skipping this box")
            continue
        class_idx = CLASS_TO_IDX[class_name]

        bnd = obj.find("bndbox")
        xmin = float(bnd.find("xmin").text)
        ymin = float(bnd.find("ymin").text)
        xmax = float(bnd.find("xmax").text)
        ymax = float(bnd.find("ymax").text)
        boxes.append((class_idx, xmin, ymin, xmax, ymax))

    return width, height, boxes


def voc_box_to_yolo_line(class_idx, xmin, ymin, xmax, ymax, img_w, img_h):
    """YOLO format: class_idx x_center y_center width height, all normalized [0,1]."""
    x_center = ((xmin + xmax) / 2) / img_w
    y_center = ((ymin + ymax) / 2) / img_h
    box_w = (xmax - xmin) / img_w
    box_h = (ymax - ymin) / img_h
    return f"{class_idx} {x_center:.6f} {y_center:.6f} {box_w:.6f} {box_h:.6f}"


def main(source: str):
    pairs = find_pairs(source)
    if not pairs:
        raise RuntimeError(
            f"No image/annotation pairs found under {source}. "
            f"Check that the extracted dataset contains both images and .xml annotations."
        )
    print(f"Found {len(pairs)} image/annotation pairs.")

    rng = random.Random(SPLIT_SEED)
    rng.shuffle(pairs)
    n = len(pairs)
    n_train = int(n * TRAIN_SPLIT)
    n_val = int(n * VAL_SPLIT)
    splits = {
        "train": pairs[:n_train],
        "val": pairs[n_train:n_train + n_val],
        "test": pairs[n_train + n_val:],
    }

    class_counts = {name: 0 for name in CLASS_NAMES}

    for split_name, split_pairs in splits.items():
        img_out_dir = os.path.join(YOLO_DATA_DIR, "images", split_name)
        lbl_out_dir = os.path.join(YOLO_DATA_DIR, "labels", split_name)
        os.makedirs(img_out_dir, exist_ok=True)
        os.makedirs(lbl_out_dir, exist_ok=True)

        for img_path, xml_path in split_pairs:
            stem = os.path.splitext(os.path.basename(img_path))[0]
            img_ext = os.path.splitext(img_path)[1]

            shutil.copy2(img_path, os.path.join(img_out_dir, stem + img_ext))

            img_w, img_h, boxes = parse_voc_xml(xml_path)
            lines = []
            for class_idx, xmin, ymin, xmax, ymax in boxes:
                lines.append(voc_box_to_yolo_line(class_idx, xmin, ymin, xmax, ymax, img_w, img_h))
                class_counts[CLASS_NAMES[class_idx]] += 1

            with open(os.path.join(lbl_out_dir, stem + ".txt"), "w") as f:
                f.write("\n".join(lines))

        print(f"{split_name}: {len(split_pairs)} images")

    # Ultralytics data.yaml
    yaml_content = (
        f"path: {YOLO_DATA_DIR}\n"
        f"train: images/train\n"
        f"val: images/val\n"
        f"test: images/test\n"
        f"names:\n" + "".join(f"  {i}: {name}\n" for i, name in enumerate(CLASS_NAMES))
    )
    yaml_path = os.path.join(YOLO_DATA_DIR, "data.yaml")
    with open(yaml_path, "w") as f:
        f.write(yaml_content)

    print("\nDefect instance counts (across all splits):")
    for name, count in class_counts.items():
        print(f"  {name:<18} {count}")
    print(f"\nDone. YOLO-format dataset written to: {YOLO_DATA_DIR}")
    print(f"data.yaml written to: {yaml_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, help="Path to the unzipped PCB Defects dataset")
    args = parser.parse_args()
    main(args.source)
