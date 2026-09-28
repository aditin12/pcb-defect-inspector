# Missing Hole

## What it is
A drilled hole (via or component mounting hole) specified in the board
design is absent from the fabricated board. This is a fabrication-stage
defect, not an assembly-stage one.

## Typical causes
- Drill program mismatch against the final Gerber/drill file
- Drill bit breakage during panel drilling that went undetected
- Panel misalignment shifting hole positions off the intended pad
- A design-file revision that wasn't propagated to the fabrication data

## Risk if unaddressed
If the missing hole was meant to carry a via, the intended electrical
connection between layers simply does not exist -- the board may fail
functional test on that net. If it was a component mounting hole, the
component cannot be through-hole mounted as designed.

## General inspection response
- Confirm against the original drill file whether a hole was truly expected
  at that location (rule out a false positive from image artifacts).
- If confirmed, the board is generally not reworkable at the fabrication
  level -- a missing hole is normally a scrap/reject decision, or a rework
  via a manual drill + plating touch-up only in low-volume/prototype
  contexts, and only if the connected net can still be verified electrically.
- Flag the finding back to the fabrication vendor with the panel/board ID
  so the drill program can be corrected before the next run.

## Severity notes
Generally treated as high-severity when it affects a via carrying a
critical net (power, ground, high-speed signal), and comparatively lower
severity when it's a non-critical mechanical mounting hole with a
redundant fastening point elsewhere on the board.
