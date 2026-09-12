# R2-24 fabrication package — revision C

A detailed, nominally609.6mm/24inch R2-D2 robot design for the Bambu H2D.
Ten STL designs make14 printed pieces around a metal load frame: two
whole stackable body sections, one dome, one print per side leg and
whole foot covers. The dome/body/leg details are modeled relief.

Each foot has two Adafruit3777 motors and four3766 wheels: six ground
motors and twelve ground wheels. A separate seventh motor and internal
wheel rotate the head. A guided rear post changes body tilt while the
side legs pivot relative to the torso and all three feet remain down.
Phone control uses the robot's local Wi-Fi AP. Sixteen original MP3
sounds are included.

This is a digital prototype, not a physically tested robot. The metal
frame requires machining and welding. The early6kg assumption was not
met; the current mass estimate is about8.95kg against a9kg build limit.
There is little reserve. Actual mass, CG, frame strength and loaded
driving with the specified TT motors must pass commissioning.

## Deliverables

- [Design and assembly PDF](output/pdf/r2d2-design-and-assembly.pdf)
- [CAD motion video](https://d1lftyhk9r30k1.cloudfront.net/r2d2/revision-c/motion.mp4)
- [Hosted PDF](https://d1lftyhk9r30k1.cloudfront.net/r2d2/revision-c/design.pdf)
- [18 MATLAB-style PNG drawings](output/drawings), including every printed component
- [10 STL files](stl) and [print manifest](bom/printed-parts.csv)
- [13 metal/G10 cutting profiles](cad/metal) and [fabrication worksheet](docs/fabrication.md)
- [60 assembly steps](docs/assembly.md), [mechanical guide](docs/mechanical.md) and [electrical guide](docs/electrical.md)
- [BOM, mass and fastener worksheets](bom), [circuit sheets and wiring](electronics)
- [Firmware, phone UI and original MP3 files](firmware), [sound catalog](audio/catalog.csv)
- [Verification methods and physical limits](docs/verification.md)

The video is a30second CAD simulation, with illustrative timing. S3
stores the PDF/MP4 privately; CloudFront serves their stable HTTPS links.
The robot itself does not need cloud connectivity.

Use the original Adafruit HUZZAH32/3405. The exact wheels, servo, bearings
and actuator must be fitted before the full print/finish run. Check the
current BOM stock notes; no component purchase was made for this design.

## Rebuild

Run from `C:/dev/robots/r2d2`, using the installed OpenSCAD, Bambu Studio,
Python, PlatformIO, FFmpeg and Node tools:

```powershell
python scripts/export_cad.py
python scripts/slice_structure.py
python scripts/electronics.py
pio run -d firmware
pio run -d firmware -t buildfs
python scripts/draw_robot.py
python scripts/render_video.py
python scripts/verify.py
python scripts/build_manual.py
# Inspect output/pdf/rendered before sharing the regenerated manual.
python scripts/package.py
```

Do not change CAD/STLs while a render or verification run is active.
The scripts check hashes to prevent mixing revisions. The supplied
audio is original; `scripts/generate_audio.py` reproduces it when needed.
No recurring automation or printer connection is created by these scripts.

Publication runs only through `.github/workflows/publish-r2d2.yml` after
a push to main. It checks the final manifest, uploads the two files,
invalidates their cache entries and verifies anonymous byte-for-byte
downloads plus MP4 range delivery. There is no local deployment path.
