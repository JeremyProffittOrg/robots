# R2-24 MATLAB-style drawings

Eight PNG sheets, rendered from the current Revision B meshes:

1. `01-robot-isometric.png` - assembled robot with labelled millimetre axes.
2. `02-robot-orthographic.png` - front, right-side and top views.
3. `03-robot-exploded.png` - separated body, head, arms and feet.
4. `04-mechanisms-exploded.png` - drive foot and rotating-head mechanism.
5. `05-body-and-arm-components.png` - whole body prints, arms, dome and eye.
6. `06-foot-and-steering-components.png` - feet, cradles and rear supports.
7. `07-head-drive-components.png` - bearing mounts, gears and head plate.
8. `08-mounts-and-small-components.png` - boards/deck mounts, shims and coupon.

All 29 printed components are included with quantities and bounding sizes.
Panel scales differ where stated. Purchased motors, wheels, bearings,
battery and servo shapes are schematic envelopes, not manufacturing CAD.
Exploded offsets are for viewing, not installation dimensions.

`r2d2-matlab-style-drawings.zip` contains every PNG and `index.json`.
The index records source-mesh and output-image SHA256 values and pixel sizes.
Rebuild with `python scripts/draw_robot.py` from the R2-D2 directory.
This is a MATLAB visual style made with Matplotlib; no MATLAB license is required.
