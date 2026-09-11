# R2-24 fabrication package

A 609.6 mm (24 inch) R2-D2-inspired robot, designed for a Bambu Lab H2D.
Six Adafruit 3777 motors drive twelve Adafruit 3766 wheels: two motors and
four wheels per foot. The rear foot steers through gears. The head rotates
continuously without wires crossing its bearing. Phone control uses the
robot's local Wi-Fi access point. Sixteen original MP3 chirps are included.

This is a digital prototype package, not a physically validated robot.
Complete the fit, rolling-load, electrical and stopping tests in the manual
before printing every cosmetic part or operating the finished robot.

Revision B reduces the printed count from 148 to 83. The body is two
complete stackable prints (260 x 260 x 148 mm and 260 x 260 x 162 mm),
with frames, posts, adapters and battery tray built in. Each side arm and
its shoulder is one 124 x 68 x 295 mm print. The head remains one dome.
The 83-piece count includes 32 small PCB spacers and the moving mechanisms.
Overall height stays 609.6 mm; no scaling of motor, wheel or bearing fits.

## Start here

- `output/pdf/r2d2-design-and-assembly.pdf`: illustrated design and build manual.
- `docs/assembly.md`: detailed assembly and commissioning sequence.
- `docs/mechanical.md`: dimensions, print settings, fits and load limits.
- `docs/electrical.md`: power design and electrical assembly.
- `cad/r2d2.scad`: editable source; `stl/` contains actual exported meshes.
- `bom/`: purchased parts, fasteners and per-STL print quantities.
- `electronics/`: circuit SVG sheets and a complete point-to-point wiring CSV.
- `firmware/`: buildable ESP32 program, phone interface and MP3 filesystem.
- `audio/catalog.csv`: names, durations and checksums of all sounds.
- `docs/verification.md`: measured digital results and unverified physical tests.

Use the original Adafruit HUZZAH32 3405. Do not use a Feather V2 or S3 board
without changing the pin map and build configuration. Wheels 3766 were
listed out of stock during research; fit the specified wheels before the
full print run. Other wheel diameters change the ground clearances.

## Rebuild

Run commands from `C:/dev/robots/r2d2`:

```powershell
python scripts/export_cad.py
python scripts/export_cad.py --views
python scripts/slice_structure.py
python scripts/generate_audio.py
python scripts/electronics.py
pio run -d firmware
pio run -d firmware -t buildfs
python scripts/verify.py
python scripts/build_manual.py
```

Existing tools used: OpenSCAD 2021.01 and its MCAD gear library, Python
NumPy/trimesh/ReportLab/PyMuPDF, FFmpeg, PlatformIO and Node.js. The exporter
accepts an `OPENSCAD` executable environment variable. The compiled motor
control test uses MinGW g++. No cloud service or recurring job is required.

This package includes no purchased parts and no factory credentials.
The CAD and synthesized sounds were created for this build. The gear
generator comes from OpenSCAD's MCAD library under LGPL-2.1; it is referenced
by the source and is not copied into this repository.
