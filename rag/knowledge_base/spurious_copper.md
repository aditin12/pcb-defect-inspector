# Spurious Copper

## What it is
An isolated island or patch of copper present on the board that was not
part of the intended design -- unlike a spur, it is not necessarily
attached to any legitimate trace or pad; it can be a fully disconnected
"floating" copper feature.

## Typical causes
- Photoresist defects during imaging that left copper where the mask
  should have exposed bare laminate for etching
- Debris or contamination shielding a small area from the etchant
- Artwork/Gerber generation errors leaving an unintended copper shape

## Risk if unaddressed
A fully isolated spurious copper island with no contact to any circuit
feature is typically electrically inert on its own. The risk is the same
as with spurs: proximity to nearby traces creates a shorting risk under
mechanical or thermal stress, and any conductive island near a
high-voltage area is a latent arcing/tracking risk in some applications.

## General inspection response
- Determine whether the copper island is truly isolated or is making
  incidental contact with a neighboring trace (which would reclassify it
  functionally closer to a short).
- Verify clearance to the nearest live conductor against the board's
  voltage-class requirements.
- Isolated copper with adequate clearance is frequently accepted with a
  note; copper encroaching on clearance limits is typically removed
  mechanically or chemically as a rework step.

## Severity notes
Lowest default severity of the six defect classes in this project when
truly isolated with good clearance; severity rises sharply if the island
sits close to a power or high-voltage trace.
