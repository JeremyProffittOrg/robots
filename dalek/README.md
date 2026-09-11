# Printable Wi-Fi Dalek

A complete digital design package for a 541 mm (21.3 inch) tall Dalek robot, with four Adafruit 3777 TT motors and 3766 wheels. An original TTGO T-Display ESP32 shows its screen at the back. A local browser controls driving, circular movement of both arms, continuous head rotation and 24 original robot voice MP3s. The robot can join a 2.4 GHz Wi-Fi network or operate through its own access point.

Start with [the design and assembly PDF](output/pdf/dalek-design-and-assembly.pdf). This is a design for a first physical prototype. Digital verification is recorded in [verification.md](docs/verification.md); actual fit, traction, current, temperature and stopping tests remain part of commissioning.

## Files to use

- [Assembly sequence and physical tests](docs/assembly.md).
- [Exact mechanical assembly, dimensions, fasteners and print settings](docs/mechanical.md).
- [STL files](stl/) and [print quantities/orientations](bom/printed-parts.csv). Print at 100% scale.
- [Editable OpenSCAD source](cad/dalek.scad), [assembly view](cad/assembly.png), [section](cad/section.png), [exploded view](cad/exploded.png) and [rear view](cad/rear.png).
- [Four circuit diagrams](electronics/), [wire-by-wire schedule](electronics/wiring.csv) and [electrical design notes](docs/electronics-research.md).
- [Electrical BOM](bom/electronics.csv) and [mounting hardware BOM](bom/hardware.csv). Hardware such as bearings, metal screws and battery straps must be purchased.
- [Firmware and flashing instructions](docs/firmware.md), with [PlatformIO project](firmware/).
- [24 MP3s](firmware/data/audio/), [transcripts and provenance](audio/README.md), [audio catalog](audio/catalog.json).
- [Research and cited design decisions](docs/research.md).

## Key design choices

The four small TT motors set the weight and floor limits. The supplied interface uses gentle moving arcs rather than stationary pivot turns. Use a level, smooth indoor floor and follow the loaded-mass and temperature gates. Each motor gets its own current-limited H-bridge on two DRV8833 boards. Removing current protection is not a remedy for poor turning.

Four MG92B positional servos give the two arms perpendicular axes. An FS5103R continuous servo drives the bearing-supported head. The head carries no electrical wires. The speaker stays in the body. The battery is a protected Bioenno BLF-1206A 12 V, 6 Ah pack, with separate regulated 5 V supplies for motors, servos and controller/audio. The pack requires its specified charger and must not connect to the T-Display battery socket.

The required Adafruit 3766 wheels and selected Adafruit 154 head servo were out of stock when checked on 2026-09-11. The parts lists retain the exact selected parts. Secure those parts before printing their final fit-dependent assemblies.

The 35 STL designs cover 151 listed pieces, including repeat parts, the fit coupon and spare standoffs. Every exported design passes the closed-mesh and 300 mm print-envelope check. The solid-plastic upper mass bound is 1,988.1 g for the entire listed print set. That is not the assembled robot mass. Purchased components and hardware add weight; the actual build must meet the 3 kg commissioning gate before driving. Electrical parts total $443.48 including allowances, before mechanical hardware, filament, shipping and tax.

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
```

The firmware guide gives the native safety-test command and the USB upload commands. OpenSCAD preview rendering commands and view coordinates are in the mechanical guide. The PDF builder needs those final preview images and the final BOMs. Do not regenerate only some of the STLs after changing shared CAD dimensions and then treat the older meshes as current.

No cloud service is part of robot operation. GitHub contains the design source. Firmware flashing is a local hardware assembly step. The repository has no cloud deployment workflow for this package.
