"""
Runs the full setup after the dataset has been prepared:
train the detector, evaluate it, and build the RAG index.

Run:
    cd ml/src
    python run_all.py
"""
import subprocess
import sys
import os

STEPS = [
    ("Training YOLOv8 detector", ["python", "train_yolo.py"], os.path.dirname(os.path.abspath(__file__))),
    ("Evaluating on test set", ["python", "evaluate.py"], os.path.dirname(os.path.abspath(__file__))),
]


def main():
    for label, cmd, cwd in STEPS:
        print("\n" + "=" * 70)
        print(f"STEP: {label}")
        print("=" * 70)
        result = subprocess.run(cmd, cwd=cwd)
        if result.returncode != 0:
            print(f"\nStep failed: {label}. Stopping.")
            sys.exit(result.returncode)

    rag_src = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__)))), "rag", "src")
    print("\n" + "=" * 70)
    print("STEP: Building RAG index")
    print("=" * 70)
    result = subprocess.run(["python", "build_index.py"], cwd=rag_src)
    if result.returncode != 0:
        sys.exit(result.returncode)

    print("\nAll done. Start the backend (uvicorn app.main:app) and frontend (npm run dev) next.")


if __name__ == "__main__":
    main()
