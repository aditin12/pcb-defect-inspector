# Mouse Bite

## What it is
A small semicircular or irregular notch bitten out of the edge of a
copper trace or pad, resembling a small bite mark -- distinct from a
clean break (open circuit), since some copper usually remains connecting
the two sides.

## Typical causes
- Etching process variation (over-etch at a trace edge)
- Contamination on the photoresist during the imaging step, causing an
  incomplete copper pattern at that spot
- Mechanical scratching during handling before the solder mask stage

## Risk if unaddressed
A mouse bite reduces the effective cross-sectional area of a trace at
that point. For low-current signal traces this is often survivable
electrically but raises long-term reliability risk (the trace is more
likely to fully separate under thermal cycling or mechanical stress at
the weakened point). For power or high-current traces, the same defect
raises resistive heating risk at the pinch point.

## General inspection response
- Measure the remaining trace width against the original design width;
  compare against the fabricator's minimum acceptable trace-width
  tolerance for that current rating.
- Traces on non-critical, low-current nets with adequate remaining width
  are frequently accepted with a note for monitoring rather than reworked.
- Where the remaining width is marginal or the net carries meaningful
  current, a conductive-epoxy or solder bridge repair over the notch is
  a common prototype/low-volume rework; production volumes typically
  reject the board instead.

## Severity notes
Severity scales with how much copper cross-section remains and what the
trace carries -- a mouse bite on a ground plane pour is usually low risk;
the same defect on a narrow high-current trace is higher risk.
