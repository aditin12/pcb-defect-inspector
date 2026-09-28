# Short

## What it is
An unintended conductive bridge between two traces, pads, or planes that
were meant to be electrically isolated -- most often excess copper
connecting two adjacent features that should have a gap between them.

## Typical causes
- Under-etching (insufficient copper removal) leaving a bridge between
  closely spaced features
- Solder bridging during assembly (a related but separate defect that
  occurs after fabrication, at the reflow stage)
- Contamination or debris on the board during the imaging/etch process
- Trace spacing pushed below the fabricator's minimum clearance for the
  chosen copper weight

## Risk if unaddressed
This is generally the most severe class of PCB defect: an unintended
connection between, for example, power and ground can draw excessive
current, overheat, damage the power supply, or damage components on
power-up. Even a short between two signal lines can cause unpredictable
logic behavior or damage a driver output actively fighting the short.

## General inspection response
- Never power on a board with a suspected short between power rails
  without first verifying and clearing it -- this is the one defect
  category where inspection should block assembly/power-on, not just log
  a note.
- Confirm the short with a continuity/resistance check between the two
  nets in question.
- If accessible, excess copper can sometimes be carefully removed with a
  hobby knife or micro-router under magnification; if the bridge is under
  a component or between inner layers, the board is normally rejected.

## Severity notes
Treated as the highest-severity defect class by default in this project's
scoring, reflecting the real risk of component or power-supply damage --
particularly when it involves a power net.
