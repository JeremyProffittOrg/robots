# fable-r2d2 — detailed printable R2-D2 fabrication package

Requested 2026-09-12 by the operator (verbatim request kept in `## Locked decisions`).
Working directory: `C:/dev/robots/fable-r2d2`. Everything for this task lives under this
directory. The sibling `C:/dev/robots/r2d2` and `C:/dev/robots/dalek` packages are earlier,
separate designs and are read only for tooling patterns and research; they are not modified.
The repository root `plan.md` belongs to concurrent sessions and is not edited by this task.

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
- [ ] deliver — upload the video to S3, presign 7 days, email it with the PDF attached

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
  `python scripts/verify.py` ALL PASS.
