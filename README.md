# PCB Inspector — CV → ML → RAG Defect Detection & Explanation

An end-to-end system that detects defects on printed circuit boards, grades
their severity, and explains each finding in plain language using a
retrieval-augmented generation layer grounded in a PCB defect knowledge base.

> Upload a photo of a bare PCB → get every defect localized with a bounding
> box, a confidence score, a Low/Medium/High severity grade, and a grounded
> explanation of what it means and what to do about it.

---

## Table of Contents

1. [Problem Statement](#problem-statement)
2. [Why CV → ML → RAG](#why-cv--ml--rag)
3. [System Architecture](#system-architecture)
4. [Tech Stack](#tech-stack)
5. [Dataset](#dataset)
6. [Stage 1 — Computer Vision (Detection)](#stage-1--computer-vision-detection)
7. [Stage 2 — ML (Severity Grading)](#stage-2--ml-severity-grading)
8. [Stage 3 — RAG (Explanation)](#stage-3--rag-explanation)
9. [Evaluation Results](#evaluation-results)
10. [Installation](#installation)
11. [Building the System](#building-the-system)
12. [Running the Backend](#running-the-backend)
13. [Running the Frontend](#running-the-frontend)
14. [API Documentation](#api-documentation)
15. [Limitations](#limitations)
16. [Future Improvements](#future-improvements)
17. [Interview Understanding](#interview-understanding)
18. [License](#license)

---

## Problem Statement

Automated optical inspection (AOI) is standard on real PCB fabrication lines,
but most AOI tooling stops at "defect detected, class X" — it doesn't tell an
inspector *how bad* the finding is or *what to do about it* without consulting
separate reference material. This project closes that gap: every detection is
automatically graded and explained, so the tool's output is directly
actionable rather than a bare label.

## Why CV → ML → RAG

This is a genuine three-stage pipeline, not three buzzwords glued together:

1. **CV** (YOLOv8 object detection) answers *where* and *what*: it localizes
   each defect on the board image with a bounding box and a class label.
2. **ML** (a rule-based severity engine) answers *how bad*: it turns the raw
   detection into a Low/Medium/High severity grade using defect-type
   criticality, detector confidence, and defect size.
3. **RAG** (retrieval + LLM) answers *what does this mean and what do I do*:
   it retrieves the relevant reference material for that specific defect type
   and severity, and generates a grounded explanation — not a hallucinated
   one, since the LLM is instructed to use only the retrieved text.

Each stage's output is the next stage's input. This is also why the severity
engine is a transparent rule set rather than a second trained model: the
dataset has bounding boxes and class labels, not severity ground truth, and
faking a severity classifier on labels that don't exist would be a worse
engineering decision than an honest, documented rule engine (see
[Stage 2](#stage-2--ml-severity-grading) for the full reasoning).

## System Architecture

```
┌──────────────┐   upload image    ┌────────────────────────────────────────┐
│   React UI   │ ─────────────────▶│            FastAPI backend              │
│ (Vite, 5173) │                    │                                          │
│              │ ◀───────────────── │  ┌────────────┐  ┌──────────────────┐  │
└──────────────┘   JSON response    │  │ Detection  │  │   RAG Service     │  │
                                     │  │ Service    │  │                    │  │
                                     │  │ (YOLOv8)   │─▶│ retriever.py       │  │
                                     │  │            │  │   (ChromaDB +      │  │
                                     │  │ severity.py│  │    sentence-       │  │
                                     │  │ (rule      │  │    transformers)   │  │
                                     │  │  engine)   │  │        │           │  │
                                     │  └────────────┘  │        ▼           │  │
                                     │                   │ llm_client.py      │  │
                                     │                   │  (Ollama / OpenAI /│  │
                                     │                   │   Anthropic /      │  │
                                     │                   │   template)        │  │
                                     │                   └──────────────────┘  │
                                     └────────────────────────────────────────┘
```

The backend imports `ml/src` and `rag/src` directly (not a reimplementation),
so what's served is guaranteed to match what was trained/indexed.

## Tech Stack

| Layer | Technology |
|---|---|
| Object detection | YOLOv8 (Ultralytics), PyTorch |
| Severity grading | Custom rule engine (pure Python) |
| Embeddings | sentence-transformers (`all-MiniLM-L6-v2`, local, free) |
| Vector store | ChromaDB (local, persistent) |
| LLM | Ollama (local, default) — swappable to OpenAI or Anthropic via env var |
| Backend | FastAPI, Pydantic |
| Frontend | React 18 + Vite (HTML/CSS/JS) |
| Deployment | Docker, docker-compose |

**Everything backend/ML/RAG is Python.** The frontend is React (JavaScript)
with plain CSS, per how this project was scoped.

## Dataset

**PCB Defects** (Kaggle, built on Peking University's open PCB defect
benchmark) — 693 images, Pascal VOC XML bounding-box annotations, 6 defect
classes: `missing_hole, mouse_bite, open_circuit, short, spur, spurious_copper`.

Free, public, purpose-built for exactly this task, and genuinely
*object-detection* labeled (bounding boxes, not just whole-image labels) —
which is what makes real localization possible instead of only "this image
contains a defect somewhere."

`ml/src/prepare_data.py` converts the VOC XML annotations to YOLO format and
writes a stratified, seeded 70/15/15 train/val/test split with zero image
overlap between splits.

## Stage 1 — Computer Vision (Detection)

**Model:** YOLOv8n (nano), COCO-pretrained, fine-tuned on the PCB dataset.
Chosen over a classification-only CNN because it answers *where* the defect
is, not just *that* one exists — the bounding box is what lets the RAG layer
reason about defect size, and what lets the UI draw the finding directly on
the board image instead of a generic warning label.

Augmentation is tuned down from YOLO's aggressive defaults (reduced mosaic,
mixup disabled) because PCB defects are small, precisely-located features on
a 693-image dataset — heavy augmentation risks blending a genuine defect into
unrecognizable noise rather than helping generalization.

## Stage 2 — ML (Severity Grading)

`ml/src/severity.py` implements:

```
severity_score = criticality(defect_type) × confidence × size_factor
```

- **criticality** — fixed per defect type, reflecting real electrical risk
  (a `short` is weighted far more critical than a `spurious_copper` island)
- **confidence** — the detector's own confidence; low-confidence detections
  are pulled toward a more cautious grade
- **size_factor** — the defect's bounding-box area relative to the image,
  square-root compressed so a much larger box doesn't dominate the score
  linearly

**Why this is a rule engine, not a trained model:** the dataset has no
severity ground truth to train against. Building a "severity classifier" on
labels that don't exist would mean either fabricating labels or overstating
what the model learned — a transparent, documented rule set is the more
honest and more defensible engineering choice here, and a natural upgrade
path if real inspection-outcome data became available later (see
[Future Improvements](#future-improvements)).

## Stage 3 — RAG (Explanation)

For every detection, `rag/src/rag_pipeline.py`:
1. Builds a query from the defect type and severity
2. Retrieves the most relevant chunks from a knowledge base of original
   reference documents (one per defect type + general QC practices),
   embedded with `sentence-transformers` and stored in ChromaDB
3. Passes the retrieved text — and only that text — to an LLM with an
   explicit instruction not to invent information beyond it
4. Returns the explanation along with which knowledge-base sections were used,
   so the explanation is auditable, not a black box

**LLM backend is pluggable** via `LLM_PROVIDER`: `ollama` (local, free,
default), `openai`, `anthropic`, or `template` (no LLM at all — deterministic
formatting of the retrieved chunks). If the configured provider is
unreachable, the system automatically falls back to the template mode rather
than failing the request, and reports which backend actually produced each
explanation in the API response.

The frontend also exposes a free-text **"ask about this board"** box, backed
by `answer_board_question()`, which retrieves across every defect type found
on the uploaded board so it can answer cross-cutting questions like *"is this
board safe to assemble?"*

## Evaluation Results

*Populate after running the pipeline (see [Building the System](#building-the-system))
— `evaluate.py` writes this automatically to `results/yolo_test_metrics.json`.*

| Metric | Value |
|---|---|
| mAP@0.5 | — |
| mAP@0.5:0.95 | — |
| Inference speed | — ms/image |

Per-class AP@0.5 and the confusion matrix are saved under `results/test_eval/`.

## Installation

**Prerequisites:** Python 3.10+, Node.js 18+, [Ollama](https://ollama.com) (free, for the RAG LLM — optional, see below).

```bash
git clone <your-repo-url> pcb-inspector
cd pcb-inspector

# ML environment
cd ml && python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cd ..

# RAG environment (can reuse the ml venv, or its own)
cd rag && pip install -r requirements.txt && cd ..

# Backend environment
cd backend && python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cd ..

# Frontend
cd frontend && npm install && cd ..
```

**Optional — local LLM for RAG explanations:**
```bash
# Install Ollama from ollama.com, then:
ollama pull llama3.2
```
If you skip this, the RAG layer automatically falls back to template-based
explanations (still grounded in the retrieved knowledge base text, just not
LLM-phrased) — the app fully works either way.

**Dataset (required before training):**
1. Download **"PCB Defects"** from Kaggle: search "PCB Defects" (Peking
   University PCB defect benchmark) or go to
   `https://www.kaggle.com/datasets/akhatova/pcb-defects`
2. Unzip it anywhere
3. Run:
   ```bash
   cd ml/src
   python prepare_data.py --source /path/to/unzipped/PCB_DATASET
   ```
> **This step needs you** — Kaggle requires an account and can't be
> scripted from here. Everything else below is fully implemented.

## Building the System

```bash
cd ml/src
python run_all.py     # trains YOLOv8, evaluates it, builds the RAG index
```
Or step by step:
```bash
python train_yolo.py                          # ~20-40 min on Colab GPU, longer on CPU
python evaluate.py
cd ../../rag/src && python build_index.py      # embeds the knowledge base, ~1 min
```

**Checkpoint to verify things worked:** `models/pcb_yolov8_best.pt` and
`rag/vector_store/` should both exist. Quick sanity test:
```bash
cd ml/src
python inference.py --image ../data/yolo/images/test/<any_test_image>.jpg
```
This should print detected defects and save `inspection_result.png` with
boxes drawn.

## Running the Backend

```bash
cd backend
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```
Check `http://localhost:8000/health` — should show `model_loaded: true` and
`rag_index_loaded: true` once the steps above are complete.

## Running the Frontend

```bash
cd frontend
cp .env.example .env
npm run dev
```
Visit `http://localhost:5173`.

**Or run everything with Docker:**
```bash
docker-compose up --build
```

## API Documentation

### `POST /inspect`
Multipart upload, field `file`. Query param `explain` (default `true`).
Returns detections (each with bbox, confidence, severity, and a RAG
explanation), a board-level summary, and the annotated image as base64 PNG.

### `POST /ask`
JSON body `{"question": "...", "defect_types": ["short", "spur"]}`.
Returns a grounded answer plus which knowledge-base sections it used.

### `GET /health`
Reports whether the detection model and RAG index are both ready.

## Limitations

- 693-image dataset — generalization to different lighting, board colors, or
  camera setups than the source dataset is unvalidated.
- Severity grading is rule-based by design (see Stage 2) — it encodes
  reasonable engineering judgment, not a model trained on real inspection
  outcomes.
- The RAG knowledge base is original reference content written for this
  project, not a substitute for official fabrication/assembly standards in a
  real production setting.
- Single-class-per-box detection; does not model overlapping/compound defects.

## Future Improvements

- Learn severity from real inspection-outcome data if it becomes available,
  replacing the rule engine with a trained regressor
- Grad-CAM-style explanation for *why* the detector flagged a region, layered
  on top of the RAG explanation of *what it means*
- Multi-image (panel-level) batch inspection with per-board history and trend
  analysis across a production run (see the "documentation practice" section
  of the general QC knowledge-base doc)
- Swap YOLOv8n for YOLOv8s/m if higher accuracy is worth the added inference cost

## Interview Understanding

<details>
<summary><b>Why YOLOv8 instead of a classification CNN?</b></summary>
Classification only answers "does this image contain a defect" — object
detection answers "where, and how many," which is what a real AOI tool needs
and what makes bounding-box size available as a severity input.
</details>

<details>
<summary><b>Why is severity rule-based instead of a trained model?</b></summary>
The dataset provides bounding boxes and class labels, not severity ground
truth. Training a "severity classifier" with no real labels behind it would
mean fabricating training signal. A transparent, documented rule engine is
the more honest choice, and is explicitly designed to be replaced by a
learned model if real outcome data becomes available later.
</details>

<details>
<summary><b>What is RAG, and why use it here instead of just prompting an LLM?</b></summary>
Retrieval-Augmented Generation grounds an LLM's output in retrieved
reference text rather than the model's own unconstrained knowledge. Without
it, an LLM asked to explain a "short" defect might generate plausible-sounding
but ungrounded content. With retrieval, the LLM is instructed to use only the
retrieved knowledge-base text, and the response reports exactly which
sections were used — so the explanation is auditable.
</details>

<details>
<summary><b>Why ChromaDB and sentence-transformers specifically?</b></summary>
Both are free, run entirely locally (no API cost or network dependency for
the retrieval half of the pipeline), and are well-established, simple to
reason about for a knowledge base this size (7 documents, a few dozen
chunks) — a heavier vector database would be solving a scale problem this
project doesn't have.
</details>

<details>
<summary><b>What happens if the LLM (Ollama) isn't running?</b></summary>
`llm_client.py` catches the failure and falls back to a template mode that
formats the retrieved chunks directly into readable text — the pipeline
degrades gracefully instead of the request failing, and the API response
reports which backend actually generated each explanation.
</details>

<details>
<summary><b>How would you evaluate the RAG layer's quality, not just the detector's?</b></summary>
Two angles: retrieval quality (does the retrieved chunk actually match the
defect/question — checkable by inspecting the `sources` field returned with
every explanation) and generation faithfulness (does the LLM's explanation
stay within what the retrieved text actually says, rather than adding
unsupported claims) — the latter is why the prompt explicitly instructs the
LLM not to invent information beyond the provided context.
</details>

<details>
<summary><b>What's the weakest link in this pipeline?</b></summary>
The severity engine, by design — it's principled but not learned, so its
weights (criticality per defect type) reflect reasonable judgment rather
than measured outcomes. That's the most honest answer, and the one flagged
throughout this README rather than hidden.
</details>

## License

MIT — see [LICENSE](LICENSE). The PCB Defects dataset has its own usage
terms; consult the Kaggle listing before any commercial use. Knowledge-base
content in `rag/knowledge_base/` is original writing for this project, not a
reproduction of any official standard.
