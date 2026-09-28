# Spur

## What it is
A small, unintended protrusion of copper extending from a trace or pad,
not (yet) touching another conductive feature -- effectively a partial
short that hasn't fully bridged the gap.

## Typical causes
- Under-etching at a trace edge, similar to a short but caught before the
  bridge fully closed
- A small copper particle or slight photoresist defect during imaging
- Panel-to-panel process variation at the edges of the etch tolerance

## Risk if unaddressed
On its own, a spur that doesn't touch a neighboring feature is often
electrically harmless. The real risk is progression: a spur close to an
adjacent trace can grow into a full short under mechanical stress,
thermal expansion, or during conformal coating/rework handling, or can
collect solder during reflow and bridge that way.

## General inspection response
- Measure the remaining clearance between the spur tip and the nearest
  neighboring conductor; compare against minimum clearance requirements
  for the board's voltage class.
- If clearance is still adequate, spurs are commonly accepted with a note
  rather than reworked, especially on low-voltage digital boards.
- If clearance is marginal or the spur is near a power net, trimming the
  spur under magnification is a low-risk, common rework step.

## Severity notes
Generally lower severity than a full short, scaled up as the remaining
gap to the nearest conductor shrinks and as the affected net becomes more
safety- or power-critical.
