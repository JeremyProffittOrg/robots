# fable-r2d2 — detailed printable R2-D2 fabrication package

Requested 2026-09-12 by the operator (verbatim request kept in `## Locked decisions`).
Working directory: `C:/dev/robots/fable-r2d2`. Everything for this task lives under this
directory. The sibling `C:/dev/robots/r2d2` and `C:/dev/robots/dalek` packages are earlier,
separate designs and are read only for tooling patterns and research; they are not modified.
The repository root `plan.md` belongs to concurrent sessions and is not edited by this task.

## revision-d — motorized, interlocked two-foot / three-leg stance change

Revision C (every section after this one) is frozen as git tag `fable-r2d2-revision-c`. The hashes of its
STLs, manual, video, mock-up and drawing ZIP are in `docs/revision-c.json`. Restore it with
`git checkout fable-r2d2-revision-c -- fable-r2d2`. Revision D outputs replace the files in place,
with revision D labels.

### Revision D locked decisions (user-confirmed; do not revisit)

- 2026-09-12, operator, verbatim: "save this as verison c and build out a version d" ("this" = the
  fable-r2d2 final build mock-up).
- 2026-09-12, operator answers, verbatim: transition "Motorized, interlocked (Recommended)";
  controller "Keep Pi 4 + KB2040 (Recommended)"; delivery "Email PDF + video link (Recommended)".
- 2026-09-12, operator, verbatim: "NO!!!  copy your work and only write to fable-r2d3". Then: "make
  the copy, and coninue wsorking in fable-r2d2". Then the operator chose "fable-r2d2" as the place
  where revision D continues.
  - The copy is `C:/dev/robots/fable-r2d3` (commit aab24c3, see its COPY.md).
  - This run writes only in `C:/dev/robots/fable-r2d2`.
  - It never writes to `C:/dev/robots/r2d2`, the root `plan.md`, `.github`, or other packages.
- Derived, recorded so it is not re-litigated:
  - The DFRobot DFR0994 confirmation was for the sibling r2d2 package only.
  - fable-r2d2 revision D keeps the Raspberry Pi 4 + Adafruit KB2040 architecture.
  - The r2d2 revision D work is design input only: the interlock state machine and its tests, and
    the sensed lock, actuator and sensor selections.
- Revision D requirements:
  - The centre leg deploys toward the front for the three-leg stance.
  - For a stationary two-foot stance, it fully retracts so its wheels lift. There is no two-foot
    driving.
  - A linear actuator moves the centre leg and the body tilt, 0 deg to 18 deg.
  - A positive shoulder lock holds each endpoint. A sensor reads its engaged state; it is never
    inferred from actuator position.
  - Drive is refused during a transition, in the two-foot stance, and in any unknown or fault state.
  - Command loss, a power or feedback fault, or an interrupted transition stops the actuator and
    leaves a held, reported state.
- Unchanged from revision C:
  - 317 mm body, nine-STL minimum, H2D Z limit 315 mm, 3 mm XY buffer.
  - Six 3777 ground motors and twelve 3766 wheels, the head drive, and the 12 V 7 Ah SLA with its
    charge port.
  - No purchases, no physical-test claims, no scheduled automation.
- The purchased-piece total is reported but not gated. The 199-piece ceiling belongs to r2d2.

### Revision D verified facts (read 2026-09-12)

- `cad/params.scad`:
  - Shoulder: `shoulder_index_r = 45`, `shoulder_index_d = 6.2`, `shoulder_index_angles = [0, 18]`
    (hand-set 6 mm dowels), `shoulder_bolt_m = 12`.
  - Stance: `body_tilt = 18`, `leg_lean = 18`, `leg_len = 375.9`, `ankle_z = 105.5`.
  - Centre leg: `center_leg_y_in_body = -45`, `caster_trail = 35`, `center_leg_flange = [140, 100, 8]`
    with four M8 bolts.
  - The centre leg is unbolted for the two-leg stance (`docs/mechanical.md` section 1.4).
- `docs/stability.json`:
  - Mass 11818.7 g, CG [0.0, 55.2, 303.6] mm.
  - Three-leg tip-back margin 81.0 mm / 14.9 deg; tip-forward margin 105.9 mm / 19.2 deg.
- Reference selections for the larger robot are in `fable-r2d3/docs/revision-d-mechanism.md` and
  `fable-r2d3/docs/revision-d-controls.md`:
  - Actuonix P16-100-256-12-P actuator.
  - J.W. Winco GN 412-6-35-B-1 plunger with two GN 412.2-M12X1.5-B6.2 receivers.
  - Omron SS-01GL lock sensor, MG995 release servo, Adafruit DRV8871 actuator driver.
  - Stance state machine in `fable-r2d3/firmware/include/stance.h`.
- Firmware layout:
  - KB2040 runs CircuitPython (`firmware/kb2040/code.py`, `protocol.py`, `test_protocol.py`).
  - Pi server is `firmware/pi/server.py`, tested by `test_mixing.py`.
  - `scripts/verify.py` runs nine checks.

### stance-mechanism — actuator, sensed lock and centre-leg retraction as real CAD, proven by a transition check

- [~] stance-mechanism — owner: background agent a9a5298ea055bf0d4 (commits eb9270e, b56a868, cbfa78a).
  Status: all DoD checks pass except the body_upper/body_lower H2D slice. Both timed out at the 300 s
  bound. The ring slice bound is raised to 3600 s (the revision C value) and the re-run is in progress.
  - Owned files: `cad/**`, `stl/**`, `scripts/export_cad.py`, `slice_check.py`, `stability.py`,
    `parts.json`, `check_stance.py`, `tests/test_stance*.py`, `bom/hardware.csv`,
    `bom/printed-parts.csv`, `docs/mechanical.md`, `docs/stability.json`, `docs/stance-check.json`.
  - `scripts/verify.py`: small anchored changes in `check_cad` only.
  - Done when, run from `C:/dev/robots/fable-r2d2`:
    - `python scripts/check_stance.py` exits 0 across the sampled transition. The check fails on:
      lifted-wheel clearance, support margin (both stances and transition poses), actuator load
      above rating, lock not engaged at an endpoint, or interference.
    - `python -m unittest discover -s tests -p "test_stance*.py"` passes.
    - `python scripts/export_cad.py` and `python scripts/slice_check.py` pass.
    - `python scripts/stability.py` reports both stances.

### stance-controls — Pi 4 + KB2040 interlocked stance change, wiring and electronics BOM

- [x] stance-controls — owner: background agent afe574ec95dfd2461 (commits a9d6cd8, 0206b0d).
  - Owned files: `firmware/**`, `scripts/electronics.py`, `electronics/**`, `bom/electronics.csv`,
    `docs/electrical.md`, `docs/firmware.md`.
  - `scripts/verify.py`: small anchored changes in `check_wiring` and `check_firmware` only.
  - Actuator and sensor values are bound when stance-mechanism messages them.
  - Done when:
    - `python -m unittest discover -s firmware/kb2040` passes.
    - `python -m unittest discover -s firmware/pi` passes.
    - The new stance tests cover: both transitions, command loss, power or feedback fault, stall or
      timeout, lock disagreement, drive refusal, fault latch and clear.
    - `python scripts/electronics.py` exits 0.
    - `check_wiring()` and `check_firmware()` pass.

### revision-d-integration — regenerate the package with revision D labels

- [ ] revision-d-integration — depends on: stance-mechanism, stance-controls.
  - Update the labels and asserts in `scripts/build_bom.py`, `draw_robot.py`, `build_manual.py`,
    `render_video.py`, `render_mockup.py`, `assembly_layout.py` and `verify.py`.
  - `render_mockup.py` must show both stances and the transition.
  - Done when `python scripts/verify.py` writes `docs/verification.json` with `"all_pass": true` and
    `"revision": "D"`, and the endpoint and transition renders have been inspected.

### revision-d-delivery — one email with the manual attached and the video link

- [ ] revision-d-delivery — depends on: revision-d-integration.
  - Commit and push `fable-r2d2`.
  - From a subagent, run `python scripts/deliver.py`. It uses the private bucket
    `robots-deliverables-759775734231`, a 7-day presigned link and SESv2.
  - Done when the accepted MessageId is in `output/delivery-receipt.json`. An accepted MessageId
    ends all retries.

### Revision D stop conditions (only these)

- A purchase, a physical action, or a write outside `C:/dev/robots/fable-r2d2` would be required.
- Credentials are missing for the push or the SES send.

### Revision D jobs and restart policy

- Each background agent is tracked by its id in the execution log.
- Failure is detected when an agent returns without its definition-of-done output.
- Restart: re-spawn once with narrower scope, then do the work inline in the parent.
- Bounds: OpenSCAD export 600 s per part; slicing 300 s per part.
- A deterministic failure is fixed before any retry, with at most two corrected attempts per failure
  class. This ceiling governs, and agents add no retry budgets of their own.

### Revision D execution log

- 2026-09-12 21:45:
  - Copied the r2d2 revision D work to `fable-r2d3` (aab24c3).
  - Stopped all of this session's r2d2 writers: the mechanism agent was killed, the controls agent
    had finished, the watcher was stopped.
  - Recorded revision D for fable-r2d2.
  - Launched stance-mechanism (a9a5298ea055bf0d4) and stance-controls (afe574ec95dfd2461).
  - Untracked `c-design.pdf`, `c-motion.mp4` and `.playwright-mcp/` in this folder are download
    checks, not package files. They are left uncommitted.
- 2026-09-12: stance-controls finished (a9d6cd8, 0206b0d).
  - The parent re-ran the tests: `python -m unittest discover -s firmware/kb2040` "Ran 113 tests" OK;
    `python -m unittest discover -s firmware/pi` "Ran 66 tests" OK.
  - The agent reported `scripts/electronics.py` PASS: 184 wires, 20 KB2040 signal pins match
    `code.py`. It also reported that `check_wiring()` and `check_firmware()` pass.
  - stance-mechanism uses two shoulder locks, so the KB2040 needs two lock switches and two release
    servos. All 20 KB2040 pins are now used.
    - Each foot's DRV8833 pair shares one pin pair.
    - DRV8833 SLP is tied to 3V3; arming stays in firmware.
  - 20 purchased pieces added, about $168.65.
  - Open gaps:
    - MG995 (Adafruit 1142) is out of stock, and the P16 is on back order.
    - Pot endpoints, release pulses and SS-01GL reliability at 3.3 V / 1 mA need bench calibration.
    - MG995 stall current of 1.5 A is an assumption.
    - KB2040 memory is not verified on a real board.
  - Launched the revision-d-integration prep agent: label, assert and count changes only, no heavy
    regeneration until stance-mechanism passes.
- 2026-09-12: stance-mechanism reported (eb9270e, b56a868, cbfa78a).
  - Design:
    - The outer legs stay vertical, and the body pitches 0 to 18 deg about the shoulders.
    - The centre leg runs on a 30 deg forward-down guide with two 12 mm shafts and LM12LUU bearings.
    - P16 strokes: 5.0 mm two-foot (wheels 25 mm up), 33.9 mm touchdown, 81.29 mm three-leg, hard stop 86 mm.
    - Two GN 412 plungers, four GN 412.2 receivers, two SS-01GL switches, two MG995 release servos.
    - New printed part `leg_carriage`: 10 STLs, 13 pieces.
    - hardware.csv: 33 -> 44 rows, +66 / -16 pieces.
  - Margins:
    - Two-foot support 28.1 mm; three-leg 75.9 mm, tip-back 15.6 deg.
    - Actuator 38.3 N against a 100 N limit.
    - Interference max 0.150 mm3.
  - Parent re-ran: `python scripts/check_stance.py` "PASS: calculated stance-transition screen...".
    `test_stance*.py` "Ran 7 tests" OK. cad/validation.json all_pass True, 10 parts.
  - Gap: `slice_check.py` exit 1. `body_upper` and `body_lower` "slicer timed out after 300 s", and
    normal supports put G-code outside the printable area.
  - Decision (parent; the 300 s bound was not user-locked): ring slice bound raised to 3600 s,
    matching revision C, with tree supports. At most one corrected attempt.
  - Physical-only gaps:
    - Centre-foot floor drag must be 8 % or less of its load; controls burst-drive the wheels to meet it.
    - Lock seating and switch reliability at 3.3 V.
    - Receiver thread retention.
    - P16 and MG995 are out of stock.
  - stance-controls made two follow-up commits (23ee773, 6902675) to bind the final 30 deg geometry.

## Locked decisions (user-confirmed; do not revisit)

2026-09-12, operator, verbatim: "creeate for me an extensively detailed r2d2 robot which uses
adafruit's tt-motor and wheeles (https://www.adafruit.com/product/3766
https://www.adafruit.com/product/3777), and a raspberry pi 4 along with the
https://www.adafruit.com/product/5302 for any micro controller needs. This needs to be
printable in as little stl's as possible, with the main body fitting the length and width
minus a 3mm buffer on x and y, on a bambulabs h2d, though, you may print multiple horizontal
pieces and stack them. The body needs to be extremely strong, along with very strong legs and
joints. Review atleast 30 r2d2 images to identify joints and movement, the 3 legs all need
two tt-motors and 4 wheels in them. leave room for a 7ah lead acid 12v battery and wire the
robot up so it can be recharged. the head must spin, you cna use another motor and wheel with
a tension adjustment on that to make movement more possible. the head needs to be extremely
detailed and printasble in one piece, it needs cutouts for led and lcd pannels as well.
create a matlab type drawing set, bill of materials along with soruces excel document,
assembly instructions with expanded diagrams for esy instructions, and a detailed assembly
and running video that shows the robot and hwo it moves ultracode"

2026-09-12, operator, verbatim: "email me a link to the video on s3 along with the pdf when done."
Delivery plan: upload `output/video/r2d2-assembly-and-operation.mp4` to a private S3 bucket in
us-east-1 under the local AWS identity, generate a 7-day presigned link, and send one HTML
status email (template `~/.claude/templates/email-status.html`) via SES from an
`@jeremy.ninja` sender to proffitt.jeremy@gmail.com with the assembly-manual PDF attached and
the S3 link in the body. Send from a subagent; require the SES MessageId. Send once.

2026-09-12 (mid-run), operator, verbatim: "make sure you are printing max height -5mm on the 3d
printer to do less parts and make them stronger". Applied: Z limit 315 mm (H2D left extruder 320
minus 5), `env_z = 315` in params and parts.json; the separate electronics tray was folded into
body_upper as an integral deck, giving nine unique STL files; body rings (246 + 135.1 mm) and the
dome (199 mm) each stay below 315 mm; the outer leg (480 mm long) still needs two prints because
no bed axis or diagonal reaches 480 mm, and it prints flat for layer strength.

Derived working decisions (operator unreachable; recorded 2026-09-12 so they are not
re-litigated mid-run):

- Body diameter 317.0 mm: H2D single-extruder printable area is 325 x 320 mm, minus the
  requested 3 mm buffer gives 322 x 317; a cylinder is limited by the 317 mm axis.
- Model scale 0.68386 = 317 / 463.55 (club-standard body and dome diameter 463.55 mm).
- Operating stance is the three-leg (tilted body) stance. Shoulder joints are bolted steel
  pivots with index pins at the two-leg and three-leg angles; they are not motorised.
- The centre leg ankle is a vertical caster pivot on ball bearings so six fixed-axle drive
  motors can turn the robot by differential drive without scrubbing the centre foot.
- Head rotation: friction drive, one Adafruit 3777 motor with one 3766 wheel pressing on the
  inside of the dome lip ring, on a pivoting mount with a screw tension adjuster; dome rides
  on a purchased lazy-susan ring bearing; a 12-wire slip ring (Adafruit 1195) carries power
  and signals into the dome.
- Head displays: front logic and rear logic LED matrices (I2C backpacks), two round PSI
  NeoPixel jewels, three holoprojector NeoPixels, one round SPI TFT LCD behind the radar eye
  lens. The dome is one STL with the cutouts modelled.
- Electronics: Raspberry Pi 4 (Wi-Fi web control, displays, audio); Adafruit KB2040 (product
  5302) drives seven motors through four DRV8833 (3297) boards and the NeoPixel chain.
- Battery: 12 V 7 Ah sealed lead-acid, 151 x 65 x 94 mm (100 mm with terminals), 2.26 kg,
  F2 terminals. Charging: panel charge port wired through its own fuse directly to the battery
  so an external 3-stage SLA charger recharges the robot with the main switch off.
- Printing: PETG (or PETG-CF) structural parts, 0.20 mm layers, 5 walls, 30-40 % gyroid;
  body rings stack with a locating lip and four M8 threaded rods; legs are two prints each
  joined over two full-length M8 threaded rods.
- No purchasing, no physical build, no hardware test claims, no email unless asked, no
  scheduled automation. Commit and push to `main` at milestone boundaries.

## Verified facts

- H2D machine profile `C:/Program Files/Bambu Studio/resources/profiles/BBL/machine/Bambu Lab H2D 0.4 nozzle.json`:
  `printable_area 350x320`, `extruder_printable_area` left `325x320`, right `25..350 x 320`,
  `extruder_printable_height` 320 (left) / 325 (right).
- Adafruit 3777: 3-6 V, 1:48, 200 RPM at 6 V, stall 0.8 kg.cm / 1.5 A at 6 V, 70 x 22 x 18 mm,
  dual D-shaft (drawing: 5.4 mm shaft, 3.7 mm flat, 9.3 + 8.7 mm shaft lengths, 36.6 mm tip
  span, 18.6 mm gearbox thickness, 22.44 mm height, two 3.0 mm holes 17.6 mm apart, rear tab
  hole 3.0 mm). Price $2.95, in stock. Drawing saved: `research/components/3777_diagram.jpg`.
- Adafruit 3766: 63 x 29 mm, 38 g, press fit on TT shaft, silicone tread, $1.50, out of stock.
- Adafruit 5302: KB2040, RP2040, 35.0 x 17.8 x 4.9 mm, 20 GPIO, 16 PWM, 2 I2C, 2 SPI,
  STEMMA QT, USB-C, $8.95, in stock.
- Adafruit 3297 DRV8833: 2.7-10.8 V, 1.2 A per channel, 1 A limit, 26 x 18 mm, $5.95.
- Adafruit 1195 slip ring: 12 wires, 2 A each, 12 mm dia x 20 mm, 300 RPM, $24.95.
- Raspberry Pi 4 B: USB-C 5 V 3 A, 40-pin header (official docs).
- Local tools: OpenSCAD 2021.01 (`C:/Program Files/OpenSCAD/openscad.com`), Bambu Studio CLI
  (`C:/Program Files/Bambu Studio/bambu-studio.exe`), Python 3.14 with numpy, trimesh,
  matplotlib, openpyxl, reportlab, PyMuPDF, Pillow, scipy, shapely, cv2, playwright,
  edge_tts; Chrome; FFmpeg 8.1.2; Node 24.

## Workstreams

### image-review — thirty-plus R2-D2 reference images, joints and movement documented
- [x] image-set — 59 files in `research/images/` (45 distinct source photographs after
  duplicate detection, see `research/critique.md`), each viewed by the reviewing agent
- [x] image-review-doc — `research/image-review-dome.md`, `-legs.md`, `-body.md` list every
  image, source URL, joints/movement seen, and "Key findings for CAD"

### component-research — verified purchased parts with sources
- [x] electronics-facts — `research/components-electronics.md` (30 primary parts, URLs, prices)
- [x] mechanical-facts — `research/components-mechanical.md` (36 primary parts)
- [x] proportions — `research/proportions.md` (47 scaled parameters from club drawings)
- [x] load-calculations — `research/loads.md` (13.3 kg nominal mass, 3.6x drive margin at
  Crr 0.02, 2.5 h mixed runtime, 9.4 N.m per shoulder)

### cad — parametric OpenSCAD, fewest STLs, H2D-fit, strong
- [x] params — `cad/params.scad` single source of dimensions
- [x] dome — one-piece detailed dome, 316.8 x 316.8 x 199.1 mm, radar eye per the club
  construction sheets, three holoprojectors, two PSIs, front/rear logic windows, lazy-susan
  inserts, wire anchor
- [~] body — two rings (317 x 317 x 141.1 and 317 x 317 x 264.0) with skirt, battery shelf,
  integral electronics deck, shoulder bosses, top plate; adversarial review returned 4
  blockers and 14 majors, recorded in `cad/review-body-findings.md`, fix in progress
- [x] legs — outer legs in two flat prints on two M8 rods, centre leg with 6001 caster bore;
  ankle lock holes, caster stop and wire route reconciled with the feet (asserts added)
- [x] feet — three feet, two motors and four wheels each, drop-in motor channels
- [x] head-drive — friction drive, spring tension, thumb nut, lift stop, 7 deg release
- [x] stance — centre leg moved 45 mm behind the body axis and caster trail 35 mm after
  `scripts/stability.py` measured only 3.9 deg of tip-back margin
- [x] export-validate — `python scripts/export_cad.py` passes 9/9; `python scripts/slice_check.py`
  passes 9/9 with no warnings: 10,053.9 g of filament and 320.6 h across the twelve pieces

### documents — drawings, BOM, manual, wiring, firmware, video
- [x] drawings — `python scripts/draw_robot.py` writes 25 MATLAB-style PNGs and the ZIP
- [x] bom-xlsx — `python scripts/build_bom.py` writes `bom/bill-of-materials.xlsx`
  (6 sheets, live formulas, 54 electronics + 33 hardware rows)
- [~] wiring — `python scripts/electronics.py` writes SVG sheets and `electronics/wiring.csv`
- [x] firmware — Pi control server and KB2040 CircuitPython; 47 + 44 unit tests pass
  (`docs/firmware.md`); display update to four 8x8 matrices in progress
- [x] manual — `python scripts/build_manual.py` writes a 99-page
  `output/pdf/r2d2-assembly-manual.pdf`, 33 figures embedded, every page rendered
- [x] video — `python scripts/render_video.py` writes a verified 170 s 1920x1080 H.264+AAC
  `output/video/r2d2-assembly-and-operation.mp4`
- [x] verify-all — `python scripts/verify.py` ALL PASS on all nine checks
- [x] deliver — video and manual uploaded to the private, encrypted, public-access-blocked
  bucket `robots-deliverables-759775734231` (us-east-1) with 7-day presigned links; one SES
  email sent to proffitt.jeremy@gmail.com, MessageId
  `010001a097d00729-b3e2c2bc-8943-49ef-8147-e92663a7fb87-000000`, MIME 19,274,937 bytes

## Stop conditions (only these)
- A purchase, physical action, or email would be required.
- Credentials are missing for a required push.

## Execution log
- 2026-09-12 03:15 Scouted sibling packages, verified H2D profile and Adafruit parts.
- 2026-09-12 03:35 Research workflow wf_58c4116a-0e9 (8 agents) completed: 59 images,
  proportions, electronics, mechanical, loads, critique (only alternate rows lack prices).
- 2026-09-12 03:40 Firmware agent completed; 47 KB2040 protocol tests and 44 Pi mixing tests
  pass; pin map corrected for RP2040 PWM slice sharing (docs/firmware.md section 4).
- 2026-09-12 04:12 Commit 9d7290e (research, firmware, params, tooling). Installed portable
  OpenSCAD nightly 2026.09.11 at C:/Users/Jeremy/tools/openscad-nightly (manifold backend).
- 2026-09-12 04:20 CAD workflow wf_91a1b56a-6fd launched (5 builders, integrate, 10 reviews,
  fix, verify). Electronics/BOM agent and firmware display update launched in parallel.
- 2026-09-12 11:42 CAD workflow finished: dome, legs, feet and head drive delivered and
  reviewed; body.scad was lost to a session limit and was authored separately afterwards.
- 2026-09-12 12:20 All nine parts export and validate. Seven interference checks are empty or
  zero-volume contact planes (`cad/interference-final.txt`).
- 2026-09-12 12:35 `scripts/stability.py` (new) measured the mass and centre of gravity from
  the real meshes: 11.7 kg, tip-back margin 20.3 mm / 3.9 deg against a 15 deg criterion.
  Fix applied to params: `center_leg_y_in_body = -45`, `caster_trail = 35`, `battery_y = 45`;
  legs, feet and the lower ring re-cut to match.
- 2026-09-12 12:55 Drawings (25 PNGs), video (170 s, verified) and manual (98 pages) all
  built end to end, then the session limit stopped the agents. Pipelines are proven; all
  three need one more run against the final meshes.
- 2026-09-12 15:15 Session limit reset. Body review fixes and the slicer bed-centring are the
  remaining blockers before the final regeneration.
- 2026-09-12 17:20 Body review fixes landed (4 blockers, 14 majors, plus two faults the fix
  itself found: deleted rod columns and plugged floor openings). Corrected a sign error in the
  centre-leg flange plane that put the flange 27.8 mm inside the body floor, and clipped the
  leg collar clear of the caster stem. All seven interference checks empty or zero-volume.
- 2026-09-12 18:20 Full regeneration against the final meshes: 9/9 export, 9/9 slice with no
  warnings (10,053.9 g / 320.6 h), 25 drawings, 170 s video, 99-page manual, BOM spreadsheet.
  `python scripts/verify.py` ALL PASS. Pushed to main as 72b46ad.
- 2026-09-12 18:49 Delivered. The first send failed deterministically: `scripts/deliver.py`
  guarded at 40 MB but called the SES v1 `send_raw_email`, which caps at 10 MB
  (`InvalidParameterValue: Message length is more than 10485760 bytes long: '19274596'`).
  The script now calls SESv2 `send_email` with raw content, whose limit really is 40 MB.
