# General PCB Inspection & Quality Control Practices

## Purpose of automated optical inspection (AOI)
Automated optical inspection compares a fabricated or assembled board
against expected geometry to catch defects early -- ideally right after
fabrication (bare-board AOI) and again after assembly (post-reflow AOI) --
because the cost of finding a defect rises sharply the further downstream
it's caught: cheap to fix at bare-board stage, expensive after a component
is soldered on top of it, very expensive if it reaches a customer.

## How to read a confidence score
A detector's confidence score reflects how strongly the visual pattern
matched what the model learned to recognize as that defect type -- it is
not a direct measure of how severe the defect is. A high-confidence,
clearly-visible spur can still be low severity; a low-confidence,
partially-obscured short is still a short and warrants a closer manual
look rather than being dismissed for its lower confidence number.

## Why severity and confidence are reported separately
Conflating "the model is sure this is a defect" with "this defect is
dangerous" leads to bad triage -- a high-confidence but low-criticality
defect (say, a small spurious copper island) shouldn't out-rank a
lower-confidence detection of a short, given how much more consequential
a short is if real. Reporting them separately lets a human reviewer weigh
both signals rather than trusting one blended number.

## When to escalate to manual inspection
- Any detection classified as high severity, regardless of confidence
- Any short or open circuit on what appears to be a power or ground net
- Clusters of multiple defects in the same board region, which often
  indicate a localized process problem worth investigating at the
  fabrication step rather than treating each defect independently
- Any detection the reviewer visually disagrees with -- automated
  inspection is a triage aid, not a final authority

## Documentation practice
Recording defect type, location, severity, and the batch/panel identifier
for every flagged board supports two things beyond the immediate
accept/reject decision: traceability if a downstream failure is later
linked back to this board, and trend analysis across a production run to
catch a drifting fabrication process before it produces a large batch of
defective boards.
