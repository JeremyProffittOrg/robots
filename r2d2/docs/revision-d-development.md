# Revision D development status

This is an incomplete design revision, not a fabrication release. The
current requirement is no more than199 purchased physical pieces, excluding
printed parts. On2026-09-12 the user accepted148 pieces and raised the final
limit to under200, superseding the previous99-piece ceiling.
Every screw, nut, washer, cut rail, motor, wheel, bearing, board and cable
assembly must be accounted for. Factory assemblies are identified as such;
loose hardware cannot be hidden in a kit or allowance row.

## Current geometry

The new chassis is a single printed solid, approximately244 x179.496 x275mm
in its bed orientation. It combines the base, upper deck, shoulder supports,
four reinforced columns, center-post guide and actuator mount. Four228mm
MISUMI HFS5-2020 rails insert through its underside. Printed keys and separate
printed cross-pins retain the rails. The nominal socket is21.2mm square.
These features are actual CAD, not blocks added only to a drawing.

The front-post assembly now includes the printed foot cores, moving adapter,
366mm shared shoulder axle, four6201 bearings, shaft collars, hub access
openings and removable printed shoulder covers. Each side leg remains one
main print. The CAD shows front deployment and a lifted center foot at stow.
The GN817 direct-pull lock mount, steel receiver pocket, keeper and drilling
jig are modelled. Its release carriage and endpoint sensors are not complete.

The cross-session editing conflict is resolved. The user assigned this
session final integration and restricted the other CLI to fable-r2d2.
Reconciliation retains the fitted35degree guide and GN817 direct-pull lock.
The committed controller/checker still contain30degree/GN412 assumptions;
these must be replaced before a fabrication release. Use2/98mm operational
stroke endpoints to retain room for the physical overtravel stops.

Exterior changes add engraved access-panel edges, door hinges and latches,
data-port fingers, shaped coin-return chutes, stepped octagonal ports,
projector inner rings, a radar-eye shelf and trim, layered horseshoes,
booster end details, ankle fittings, foot side frames and hose-end collars.
These are integrated mesh features. Paint and weathering are separate.

## Evidence and limits

`python scripts/export_cad.py --check-development` checks the actual twelve
development STL designs for closed, consistently wound, positive single
solids, bed placement and dimensions below300mm on each axis. Its result
is cad/development-check.json. This does not establish support removal,
actual H2D slicing, mating clearances, assembly access, load strength,
fatigue, creep or completed robot operation.

`python scripts/check_printed_fit.py` passed the new shoulder-hub insertion,
four former center-servo collision witnesses, integral head motor bed, four
shell/frame screw axes, and a sampled shell assembly route. The lower body
must enter from below at45degrees to its final orientation. Raise it0.3mm
above its seated height, rotate to align the tabs, then lower it onto the
mounts. Install the upper ring from above before external shoulder caps and
collars. The15000-point screening is not a continuous collision proof.
Input STL hashes are recorded in cad/printed-fit-check.json.

Fresh OpenSCAD development assembly PNGs are in
output/drawings/development/{front-deployed,front-stowed,frame-deployed}.png.
They show actual meshes and schematic purchased-part envelopes; they are
not the final sourced/verified drawing index or fabrication release.

`python scripts/draw_robot.py --development` makes explicitly labelled
MATLAB-style component PNGs from the actual current meshes. Their input
and image hashes are in output/drawings/development/index.json. These
images are development evidence, not final assembly instructions.

The published PETG HF strength data uses conditioned/annealed specimens.
It cannot be assigned directly to this untreated printed chassis. The
old metal-frame strength calculations likewise do not rate these printed
joints. Material, retention, sustained-load and motion tests are still
required. See printed-frame-research.md for manufacturer sources and
the exact distinctions between dimensions, ratings and assumptions.

## Purchase count and controller decision

No complete final BOM has been verified. The original tables have95
hardware rows and47 electronics rows, with mixed-unit quantity sums624
and133; those sums are not valid physical-piece totals. The research note
also records a conservative148-piece candidate subtotal with additional
unresolved wiring and mounting requirements. It is not a proof that every
possible design needs148 pieces. The user has now accepted that subtotal;
51 pieces remain available for all additional hardware and wiring.

The candidate is itemized in bom/development-purchased.csv. Run
`python scripts/verify.py --bom-only` for the physical-quantity audit.
The check counts quantities, rejects invalid or duplicate rows, and fails
if quantities remain unresolved or the sum exceeds199. Its current result
must be read from the current ledger; concurrent integration is changing
the subtotal. A2026-09-12 read found142 known pieces and7 unresolved
categories. This is still incomplete. The default verification
command also stops at this gate. The checker cannot establish that every
physical joint and wire is represented; that requires the assembly review.

DFRobot Romeo DFR0994 was selected by the user on2026-09-12 to consolidate the MCU and four motor
drivers. Its stock shared current setting, paired-motor protection and
separate logic/motor supplies need deliberate design changes and checks.
The controller-brand question is resolved. The specified Adafruit3777
motors and3766 wheels remain fixed. Do not request that approval again.
The Romeo firmware migration is committed in3eba75e. Its mechanism
constants and sensing still need reconciliation. No component purchase
has occurred. See revision-d-control-review.md for the reviewed faults;
that note is a snapshot of code which another session continues to edit.

The remaining work is to close the counted purchase manifest, complete
and check the mechanism and interfaces, adapt controls and wiring, run
current H2D slices, then regenerate and review the complete manual,
drawings, video and package. No revised PDF or video has been emailed.
