"""
Severity scoring engine -- the "grade" step between raw CV detections and
the RAG explanation layer.

WHY RULE-BASED, NOT A TRAINED MODEL
The PCB Defects dataset provides bounding boxes and defect *type* labels,
but no severity/urgency ground truth -- there is no "this short is critical,
that one is minor" annotation to train against. Rather than fabricate a
severity classifier with no real labels behind it, this is implemented as
an explicit, documented rule engine. This is also a more honest and more
defensible design in an interview: it's a real engineering decision, not
a corner cut. (See README "Future Improvements" for how this would upgrade
to a learned model if failure/inspection outcome data became available.)

SCORING LOGIC
severity_score = criticality(defect_type) * confidence * size_factor

- criticality: fixed per defect type (config.DEFECT_CRITICALITY), reflecting
  how likely that defect class is to cause functional board failure
  (e.g. a short is far more dangerous than excess spur copper).
- confidence: the detector's own confidence for that box -- a low-confidence
  detection is graded more cautiously (pulled toward "review needed"
  rather than an extreme label).
- size_factor: the defect's bounding-box area relative to the board image,
  clipped and mildly compressed (sqrt) -- a large open circuit or short is
  treated as more severe than a pinpoint one, without letting box size alone
  dominate the score.

The combined score is bucketed into Low / Medium / High for the UI and the
RAG layer (which explanation prompt gets used depends on the bucket).
"""
import math

from config import DEFECT_CRITICALITY


def compute_severity(defect_type: str, confidence: float, box_area_fraction: float) -> dict:
    """
    defect_type: one of config.CLASS_NAMES
    confidence: detector confidence, 0-1
    box_area_fraction: (box width * box height) / (image width * image height), 0-1

    Returns: {"score": float 0-1, "level": "low"|"medium"|"high"}
    """
    criticality = DEFECT_CRITICALITY.get(defect_type, 0.5)

    # sqrt compresses the size effect so a defect 4x the area is only ~2x
    # the size contribution, not 4x -- avoids a single large box dominating
    # the score purely due to image scale/resolution artifacts.
    size_factor = min(math.sqrt(max(box_area_fraction, 0.0)) * 6, 1.0)
    size_factor = 0.4 + 0.6 * size_factor   # floor at 0.4 so tiny defects aren't scored near-zero

    raw_score = criticality * confidence * size_factor
    score = max(0.0, min(1.0, raw_score))

    if score >= 0.55:
        level = "high"
    elif score >= 0.28:
        level = "medium"
    else:
        level = "low"

    return {"score": round(score, 3), "level": level}


def summarize_board(detections: list) -> dict:
    """
    detections: list of {"class_name":..., "confidence":..., "severity": {"score":..., "level":...}}
    Returns an overall board-level verdict: worst individual severity level,
    plus counts per level, used for the top-line pass/fail-style summary.
    """
    if not detections:
        return {"overall_level": "pass", "counts": {"high": 0, "medium": 0, "low": 0}, "total_defects": 0}

    counts = {"high": 0, "medium": 0, "low": 0}
    for d in detections:
        counts[d["severity"]["level"]] += 1

    if counts["high"] > 0:
        overall = "high"
    elif counts["medium"] > 0:
        overall = "medium"
    else:
        overall = "low"

    return {"overall_level": overall, "counts": counts, "total_defects": len(detections)}
