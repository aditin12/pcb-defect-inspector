# Open Circuit

## What it is
A complete break in a copper trace, via, or pad that was meant to be
continuous -- the two sides of the intended conductor are fully
disconnected, unlike a mouse bite where some copper still bridges the gap.

## Typical causes
- Over-etching that fully removed copper at a narrow trace section
- A crack propagating through a via barrel (common at thermal stress points)
- Physical damage during handling, testing, or depanelization
- A design rule violation that left a trace too thin to survive etching tolerances

## Risk if unaddressed
The net is fully disconnected. Depending on what that net does, this
ranges from a single non-critical LED or indicator failing to a complete
functional failure of the board if it affects power delivery, a clock
line, or a data bus. An open circuit almost always fails functional test
outright rather than degrading gracefully.

## General inspection response
- Verify with continuity testing (not just visual/image inspection) to
  confirm the break is electrical, not a solder-mask or silkscreen
  artifact that only looks like a gap.
- For accessible, low-density boards, a wire-jumper or solder-bridge
  repair across the break is a standard prototype rework.
- For breaks inside a via barrel or under a component, board-level repair
  is often impractical -- reject/replace is the usual production response.

## Severity notes
Open circuits are treated as high severity by default, since -- unlike a
mouse bite -- there is no partial conduction cushioning the failure. The
main severity differentiator in practice is how critical the affected net
is (power/ground/clock vs. a single non-essential LED).
