# Printable Wi-Fi Dalek

A digital design package for a bronze Dalek robot under three feet tall, with a circular reinforced base, a one-piece skirt, a combined shoulder and neck, and concealed arm servos. MOUNT-1 has ten STL designs and fourteen printed pieces with the four motor clamps. The motor cable-tie option omits those clamps and needs ten printed pieces. Four Adafruit 3777 TT motors and 3766 wheels drive the base; a fifth motor and wheel turn the head through an adjustable friction drive. The original rear TTGO T-Display ESP32, circular arm motion, Wi-Fi network/access-point controls and 24 original MP3 voices remain.

Start with [the design and assembly PDF](output/pdf/dalek-design-and-assembly.pdf). This is a design for a first physical prototype. Digital verification is recorded in [verification.md](docs/verification.md); actual fit, traction, current, temperature and stopping tests remain part of commissioning.

## Files to use

- [Assembly and operation video (MP4)](output/video/dalek-assembly-and-operation.mp4): two minutes at 1080p with narration, concealed arm assembly, adjustable head-wheel contact, original robot sounds and simulated operation. [Captions](output/video/assembly-captions.srt) and [video verification](output/video/video-manifest.json) are included. Cutaways expose internal parts during assembly. This is CAD animation, not physical test footage.
- [MATLAB-style PNG set (ZIP)](output/drawings/dalek-matlab-style-pngs.zip), with [assembled robot](output/drawings/01_robot_assembled.png), [exploded assembly](output/drawings/02_robot_exploded.png), [orthographic views](output/drawings/03_robot_orthographic.png), [component sheet](output/drawings/04_printed_components.png), [base hardware breakout](output/drawings/05_base_drive_breakout.png), and [ten individual component drawings](output/drawings/components/).
- [Assembly sequence and physical tests](docs/assembly.md).
- [Exact mechanical assembly, dimensions, fasteners and print settings](docs/mechanical.md).
- [STL files](stl/) and [print quantities/orientations](bom/printed-parts.csv). Print at 100% scale.
- [Editable OpenSCAD source](cad/dalek.scad), [base detail](cad/base.png), [assembly view](cad/assembly.png), [section](cad/section.png), [exploded view](cad/exploded.png) and [rear view](cad/rear.png).
- [Five circuit diagrams](electronics/), [wire-by-wire schedule](electronics/wiring.csv) and [electrical design notes](docs/electronics-research.md).
- [Battery options and charger requirements](docs/battery-options-research.md): Bioenno 6 Ah or the specified Power-Sonic 7 Ah/14 Ah SLA models.
- [Electrical BOM](bom/electronics.csv) and [mounting hardware BOM](bom/hardware.csv). Hardware such as bearings, metal screws and battery straps must be purchased.
- [Firmware and flashing instructions](docs/firmware.md), with [PlatformIO project](firmware/).
- [24 MP3s](firmware/data/audio/), [transcripts and provenance](audio/README.md), [audio catalog](audio/catalog.json).
- [Research and cited design decisions](docs/research.md).
- [100-image visual review](docs/appearance-research.md), [individual reference inventory](docs/reference-image-review.csv), and [head friction-drive drawing](output/drawings/06_head_friction_drive.png).
- [S3 video and PDF delivery](docs/video-delivery.md). The final email includes a signed video link and the PDF attachment.

## Key design choices

The four small TT wheel motors set the weight and floor limits. The supplied interface uses gentle moving arcs. Use a level, smooth indoor floor and follow the loaded-mass and temperature gates. Three DRV8833 boards provide five independent used motor bridges with their stock current limits. Removing current protection is not a remedy for poor turning.

Four MG92B positional servos sit inside smaller 90 x 52 x 103 mm arm boxes. Each servo uses two ear screws or two ties; its supplied horn and center screw remain mandatory. A TT motor's horizontal wheel drives an internal head drum. A screw sets contact and locking fasteners retain the carriage. The bearing-supported head carries no electrical wires; the speaker stays in the body.

The default battery remains the protected Bioenno BLF-1206A 12 V, 6 Ah pack. The named Power-Sonic PS-1270 F2 7 Ah and PS-12140 F2 14 Ah batteries are fit and electrical alternatives. One battery rests on the padded base below a single printed electronics platform with integral legs. Each chemistry needs its specified external charger. The SLA adapter preserves the keyed PP30 input, existing fuse and 5 V supplies. After a low-battery stop, switch MAIN off and unplug the pack; firmware stops motion but leaves the controller powered. Heavier SLA builds must pass the loaded driving tests.

The required Adafruit 3766 wheels were out of stock when checked on 2026-09-11. Five are required, including the head drive wheel. Obtain the exact parts before accepting their printed fits. The former head servo, belt and printed pulley have been removed.

The shared pitch carrier is printed twice and the optional hook clamp four times. Four body pieces stack vertically: base, 213 mm skirt, 186 mm combined shoulder/neck, and head. Both taller body prints stay below the 320 mm maximum-minus-5 mm height target. Overall height remains 563.8 mm. The base stays 300 mm in diameter with a 6 mm floor; its 8 mm brim allowance needs 316 x 316 mm in the H2D single-nozzle area. Four printed motor clamps use four screws total, or two ties retain each motor. The 216 mm board platform is one print with four legs. Fit the battery and populated platform before lowering the complete skirt around them. Assemble the upper mechanisms through the open bottom before seating the upper shell.

The [mesh validation](cad/validation.json), [H2D slice record](cad/h2d-slice-check.json) and [verification notes](docs/verification.md) record dimensions, hashes, settings and digital checks. Match each report to the released MOUNT-1 meshes. Removing a joint does not establish a physical strength rating; base strength, completed mass, friction adjustment and loaded driving require the tests in the manual. Current prices and allowances are in the BOM files.

## Rebuild the deliverables

The design was generated on Windows with existing OpenSCAD 2021.01, Python 3.14, PlatformIO and FFmpeg. The CAD exporter needs Python `trimesh` and `numpy`. The voice generator needs Windows System.Speech, `numpy` and FFmpeg. The PDF builder uses `reportlab`, PyMuPDF and the installed Arial/Consolas fonts. These tools were already available on the design machine; the scripts do not install software or register automation.

```powershell
Set-Location C:/dev/robots/dalek
python scripts/export_cad.py
python scripts/slice_h2d.py
python electronics/generate.py
pio run -d firmware
pio run -d firmware -t buildfs
node firmware/test/test_ui.js
python scripts/render_drawings.py
python scripts/render_video.py
python scripts/build_manual.py
```

The firmware guide gives the native safety-test command and the USB upload commands. OpenSCAD preview rendering commands and view coordinates are in the mechanical guide. The PDF builder needs those final preview images and the final BOMs. Do not regenerate only some of the STLs after changing shared CAD dimensions and then treat the older meshes as current.

The MATLAB-style drawings use the installed Matplotlib, NumPy, trimesh and Pillow tools. They render the delivered STL geometry without changing it. The assembled and orthographic views show the bronze finish; exploded and component views use part colours for identification. Gray purchased hardware is drawn as nominal envelopes. The drawing manifest records source hashes and PNG dimensions. The original 1.14-inch TTGO T-Display board was confirmed on 2026-09-12.

The video reuses those meshes with the installed Python Playwright, Chrome/WebGL and FFmpeg tools. `render_video.py --preview` makes review keyframes. A full render creates local speech narration, reuses existing robot MP3s, and writes the MP4, poster, captions and manifest. The temporary local renderer never connects to a printer, robot, user browser profile or network account. Video motion and speed are illustrative; the existing physical commissioning gates still apply.

Robot operation stays local. GitHub contains the design source, and firmware flashing is a local hardware assembly step. A separate GitHub Actions/OIDC workflow publishes the finished video and PDF to private S3 storage for delivery.
