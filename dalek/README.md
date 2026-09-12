# Printable Wi-Fi Dalek

A digital design package for a 543.8 mm (21.4 inch) tall Dalek robot, with a single-piece reinforced motor base and complete body sections that stack vertically. The revised print set has ten STL files. It keeps four Adafruit 3777 TT motors and 3766 wheels, a rear-facing original TTGO T-Display ESP32, circular arm motion, continuous head rotation and 24 original MP3 voices. A local browser controls it through a 2.4 GHz Wi-Fi network or the robot's own access point.

Start with [the design and assembly PDF](output/pdf/dalek-design-and-assembly.pdf). This is a design for a first physical prototype. Digital verification is recorded in [verification.md](docs/verification.md); actual fit, traction, current, temperature and stopping tests remain part of commissioning.

## Files to use

- [Assembly and operation video (MP4)](output/video/dalek-assembly-and-operation.mp4): two minutes at 1080p with narration, component assembly, original robot sounds and simulated operation. [Captions](output/video/assembly-captions.srt) and [video verification](output/video/video-manifest.json) are included. The head stays loose while its belt is fitted; cutaways expose hidden components. This is CAD animation, not physical test footage.
- [MATLAB-style PNG set (ZIP)](output/drawings/dalek-matlab-style-pngs.zip), with [assembled robot](output/drawings/01_robot_assembled.png), [exploded assembly](output/drawings/02_robot_exploded.png), [orthographic views](output/drawings/03_robot_orthographic.png), [component sheet](output/drawings/04_printed_components.png), [base hardware breakout](output/drawings/05_base_drive_breakout.png), and [ten individual component drawings](output/drawings/components/).
- [Assembly sequence and physical tests](docs/assembly.md).
- [Exact mechanical assembly, dimensions, fasteners and print settings](docs/mechanical.md).
- [STL files](stl/) and [print quantities/orientations](bom/printed-parts.csv). Print at 100% scale.
- [Editable OpenSCAD source](cad/dalek.scad), [base detail](cad/base.png), [assembly view](cad/assembly.png), [section](cad/section.png), [exploded view](cad/exploded.png) and [rear view](cad/rear.png).
- [Four circuit diagrams](electronics/), [wire-by-wire schedule](electronics/wiring.csv) and [electrical design notes](docs/electronics-research.md).
- [Electrical BOM](bom/electronics.csv) and [mounting hardware BOM](bom/hardware.csv). Hardware such as bearings, metal screws and battery straps must be purchased.
- [Firmware and flashing instructions](docs/firmware.md), with [PlatformIO project](firmware/).
- [24 MP3s](firmware/data/audio/), [transcripts and provenance](audio/README.md), [audio catalog](audio/catalog.json).
- [Research and cited design decisions](docs/research.md).

## Key design choices

The four small TT motors set the weight and floor limits. The supplied interface uses gentle moving arcs rather than stationary pivot turns. Use a level, smooth indoor floor and follow the loaded-mass and temperature gates. Each motor gets its own current-limited H-bridge on two DRV8833 boards. Removing current protection is not a remedy for poor turning.

Four MG92B positional servos give the two arms perpendicular axes. An FS5103R continuous servo drives the bearing-supported head. The head carries no electrical wires. The speaker stays in the body. The battery is a protected Bioenno BLF-1206A 12 V, 6 Ah pack, with separate regulated 5 V supplies for motors, servos and controller/audio. The pack requires its specified charger and must not connect to the T-Display battery socket.

The required Adafruit 3766 wheels and selected Adafruit 154 head servo were out of stock when checked on 2026-09-11. The parts lists retain the exact selected parts. Secure those parts before printing their final fit-dependent assemblies.

The ten STL designs produce eleven pieces because the same pitch carrier is printed twice. The six body pieces are the base, lower skirt, upper skirt, shoulder, neck and head. Each is one connected print. The base has a 300 x 280 mm footprint, a 6 mm floor, a continuous reinforced perimeter and built-in motor pockets. Rotate the base and lower ring 90 degrees about vertical Z for slicing. The base plus its 8 mm brim then occupies 296 x 316 mm; the recorded H2D slice proves the complete footprint fits. The body has integrated decoration and positive stacking registers.

All ten meshes and actual H2D slices passed. The [mesh validation](cad/validation.json) and [H2D slice record](cad/h2d-slice-check.json) give exact dimensions, hashes and settings. Slicer predictions total 2.189 kg of installed plastic, 3.031 kg of filament including support/brim, and about 100.5 hours of sequential printing. Known purchased components bring the planning subtotal above 3.33 kg before all remaining hardware, exceeding the earlier 3 kg target. Base strength and loaded driving still require the physical tests in the manual. Electrical parts total $443.48 including allowances, before mechanical hardware, filament, shipping and tax.

## Rebuild the deliverables

The design was generated on Windows with existing OpenSCAD 2021.01, Python 3.14, PlatformIO and FFmpeg. The CAD exporter needs Python `trimesh` and `numpy`. The voice generator needs Windows System.Speech, `numpy` and FFmpeg. The PDF builder uses `reportlab`, PyMuPDF and the installed Arial/Consolas fonts. These tools were already available on the design machine; the scripts do not install software or register automation.

```powershell
Set-Location C:/dev/robots/dalek
python scripts/export_cad.py
python electronics/generate.py
pio run -d firmware
pio run -d firmware -t buildfs
node firmware/test/test_ui.js
python scripts/build_manual.py
python scripts/render_drawings.py
python scripts/render_video.py
```

The firmware guide gives the native safety-test command and the USB upload commands. OpenSCAD preview rendering commands and view coordinates are in the mechanical guide. The PDF builder needs those final preview images and the final BOMs. Do not regenerate only some of the STLs after changing shared CAD dimensions and then treat the older meshes as current.

The MATLAB-style drawings use the installed Matplotlib, NumPy, trimesh and Pillow tools. They render the delivered STL geometry without changing it. The assembled and orthographic views show the bronze finish; exploded and component views use part colours for identification. Gray purchased hardware is drawn as nominal envelopes. The drawing manifest records source hashes and PNG dimensions. The original 1.14-inch TTGO T-Display board was confirmed on 2026-09-12.

The video reuses those meshes with the installed Python Playwright, Chrome/WebGL and FFmpeg tools. `render_video.py --preview` makes review keyframes. A full render creates local speech narration, reuses existing robot MP3s, and writes the MP4, poster, captions and manifest. The temporary local renderer never connects to a printer, robot, user browser profile or network account. Video motion and speed are illustrative; the existing physical commissioning gates still apply.

No cloud service is part of robot operation. GitHub contains the design source. Firmware flashing is a local hardware assembly step. The repository has no cloud deployment workflow for this package.
