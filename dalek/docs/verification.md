# Digital verification and physical limits

The ROUND-10 package is a design for a first physical prototype. Mesh, slicer, firmware, wiring and media checks establish digital consistency. They do not establish real print strength, traction, stopping distance or battery runtime. The builder must complete the physical gates in `assembly.md`.

## Reference review

`docs/reference-image-review.csv` contains 100 distinct visually reviewed images, each with its original URL, dimensions, byte and decoded-pixel hashes, observation and design implication. Duplicate crops and unrelated images were excluded after visual inspection. The source inventory has 100 unique image URLs, file hashes, pixel hashes and individual observations. The appearance report cites 18 exact images. Reference images remain outside the repository and deliverables.

## Printable geometry

Command:

```powershell
python scripts/export_cad.py --check-only
```

Result: ten watertight, consistently wound STL designs, one connected positive solid per design, eleven printed pieces and a 3157.3 g solid-material upper bound. The shared pitch carrier is printed twice. The circular base is 300 mm in diameter, with a 6 mm floor and a continuous bumper. Nominal assembled height is 563.8 mm. All parts fit the checked H2D envelope upright with their requested brim allowance.

The solid-material bound comes from closed mesh volume and assumed material density. It is not a slicer estimate or a measured robot mass. The exact released dimensions and source hashes are in `cad/validation.json` and `bom/printed-parts.csv`.

## Mechanical checks

Command:

```powershell
python scripts/check_mechanical.py
```

All 101 checks passed across 507,950 samples against the final ten STL hashes. The repeatable check samples wheel seating, motor envelopes, the rotated battery, electronics plates, bumper continuity, arm motion, insertion paths, head-wheel contact, carriage travel and tool access. This includes 4,800 exterior sight rays with no visible servo targets through the modelled opaque liners. Its mesh-specific results are in `cad/mechanical-checks.json`; the method and resolved findings are in `docs/revision-review.md`. These are finite samples and mesh-vertex checks, not exact continuous collision proofs.

An independent carrier-insertion review checked 87 poses and 26,100 vertices per side against the final shoulder, with zero interior hits. The earlier diagonal route intersected the gunbox. The corrected route lowers the carrier through the central opening at Y-44, shifts sideways, moves forward and then seats on the horn. A separate check sampled 7,200 driver-shaft points for each of the lower skirt, upper skirt and shoulder; all four joint approaches in each part had zero interior hits.

The PDF review also caught an assembly-order error: an already installed pitch servo blocked the arm-feed path. The instructions now feed and support the arms first, then insert the pitch-servo carriers. `python scripts/check_arm_assembly.py` passes eight additional checks across 187,920 samples, including both actual supported arm meshes and the shoulder as obstacles. Its result is `cad/arm-assembly-checks.json`. This correction changes the instructions; it does not change the STL geometry.

The final arm limit is 8 degrees in the interface and firmware. Opaque flexible socket liners complete concealment around the spherical roots. The friction carriage uses an M3 jackscrew for contact adjustment and four accessible guide clamps with nyloc nuts for locking. There is no inaccessible separate jam nut. Real fabric folds, horn dimensions, pads, print shrinkage and loaded tire deformation require physical checks.

## Actual H2D slicing

Command:

```powershell
python scripts/slice_h2d.py
```

All ten final mesh hashes and all eleven print instances passed actual Bambu Studio 02.08.02.61 slicing. The runner uses installed H2D 0.4 mm machine settings in an isolated temporary profile. Its supported assembly-list input places the full object at X162.5,Y160. It does not change the machine or nozzle geometry, access a user profile, connect to a printer or start a print.

The checks verify the original triangle count, rigid transforms, complete bounding box and printed height, material, process settings, selected left nozzle and every deposited model/support/generated-brim path. Those paths fit the left X0..325 by Y0..320 mm area. The 350 mm combined machine width is not used as an individual-nozzle allowance.

The final report predicts:

- Installed printed model: 2429.20 g.
- Total filament including removable support and brim: 4073.06 g.
- Sequential printing time: 418622.09 seconds, or about 116.28 hours.
- PETG filament: 2176.60 g; PLA filament: 1896.46 g.

The hardware BOM allows three 1 kg spools of each material. This rounds the material-specific estimate plus 10% allowance to complete spools. Actual waste, failed prints and finishing are not measured.

Bambu omitted a separate Brim feature on the base, shoulder, plunger and emitter despite the recorded requested brim settings. This is explicitly recorded per part. Generated support and all remaining deposition still fit the nozzle area. Inspect the actual adhesion preview before printing; a configured brim width alone is not proof that a brim was generated.

The base's complete 57 mm printed height and 10,340 source triangles were preserved. It predicts 737.780 g of installed plastic and 886.285 g total filament. Its actual deposited footprint, including bead width, is X7.7445..317.2565 and Y5.2445..314.7565 mm. These are software results. No physical adhesion or strength test has been performed.

## Controls, wiring and audio

Commands:

```powershell
pio run -d firmware
pio run -d firmware -t buildfs
node firmware/test/test_ui.js
```

Firmware and filesystem builds pass. RAM is 45,416 bytes and application flash is 995,025 bytes. The original LilyGO T-Display board definition and pinned Arduino-ESP32 platform remain in use. The 2,097,152-byte LittleFS image contains the local interface and all 24 original MP3 files. No firmware has been flashed to a physical board during this revision.

The existing native C++ control test passes with compiler warnings treated as errors. It covers boot lockout, lease replay, timeout, faults, rollover and wheel ramps, plus the new head PWM cap, immediate stop, 100 ms reversal coast through zero/re-arm/rollover, and acceptance of 8-degree arm motion with rejection above that limit. The browser test covers fresh commands, release/cancel, blur, connection loss, late replies and no automatic restart.

`python electronics/generate.py` produces 185 point-to-point wiring rows and four SVG circuit sheets. An independent audit checked the GPIO2/U9/PCA9685 direction routing, powered-off inputs, pull-downs and reset/fault states. Startup now writes and reads back PCA MODE2=0x06 so global output disable makes both head gates inactive. Each of the five motors has its own used current-limited bridge; one bridge on the third DRV8833 remains unused. Estimated peak output allowance is 50 W including rail bleeders.

All 24 original MP3 hashes remain unchanged. The assembly video adds local speech narration and reuses six original robot cues. The soundtrack is 120 seconds, 48 kHz mono and has no overlapping clips. The video is labelled as CAD animation and simulated operation throughout.

## Delivery checks and remaining physical work

The drawing manifest records the current STL/source hashes, 16 engineering PNGs, their ZIP and five PDF preview PNGs. The video manifest records its exact input hashes, frame evidence and media checks. The delivered MP4 must pass full FFmpeg decoding and FFprobe checks for 1920 x 1080, 24 fps, 2880 frames, 120 seconds and AAC audio.

The PDF is rendered and visually checked before delivery. GitHub Actions uses OIDC to upload the exact committed video and PDF to private S3 storage, downloads both objects and compares their SHA256 hashes. The final HTML email includes a signed video link with an explicit expiry and the PDF attachment. The delivery log records the workflow result and SES MessageId; acceptance by SES does not prove the recipient opened the message.

No physical robot was printed, wired, powered, flashed or driven. The 2.429 kg installed-plastic prediction excludes the battery, all motors/wheels, servos, boards, bearings, fasteners, wiring, fabric and finish. Weigh the finished robot. Test fit, base strength, loaded driving, head contact and locking, fabric clearance, supply sag, noise, temperatures, Wi-Fi loss and every stop case before use.
