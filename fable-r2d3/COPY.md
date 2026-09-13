# fable-r2d3 — copy of the R2-D2 revision D development work

Copied 2026-09-12 on operator instruction: "NO!!!  copy your work and only write to fable-r2d3",
then "make the copy, and coninue wsorking in fable-r2d2". This folder is a reference copy.
Active revision D work continues in `C:/dev/robots/fable-r2d2` (see its `plan.md`).

Source: `git archive 6c799bf r2d2` (committed tree only), which includes this session's
revision D commits 3eba75e, 76d0007, dd5533f (DFR0994 firmware, interlocked stance change,
wiring), 4ff9852 (sensed GN 412 shoulder lock, P16 actuator, transition check),
991c43b, 152d8e3, 6c799bf (revision-aware packaging), on top of the earlier committed
r2d2 revision C/D-development base.

Added from the r2d2 working tree: `bom/development-purchased.csv` (the mechanism agent's
uncommitted ledger update: 290 mm post rail, P16 actuator, GN 412 lock, two receivers).

Excluded: uncommitted edits by the separate Codex session (its GN817 `stance-lock.scad`,
`check_printed_fit.py`, fit review, re-exported STLs), `output/delivery/`, `output/pdf/`
and `output/r2d2-fabrication.zip` (published revision C media, still in `r2d2/`).
Absolute paths in README.md and docs/revision-d-controls.md were changed to this folder.
The GitHub workflow and CloudFront stack still belong to `r2d2/`; this copy has no
publication path of its own.
