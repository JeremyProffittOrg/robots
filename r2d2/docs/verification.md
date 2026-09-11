# Digital verification and physical limits

The fabrication package passed digital checks. No printer, completed robot,
motor load, battery runtime or physical wireless link was tested during
this run. The staged commissioning tests remain necessary before operation.

## CAD

Revision B: `python scripts/export_cad.py` produced 29 different STL meshes
and a manifest for 83 pieces, down from 148. The body is two whole stackable
prints and each arm is one whole print. First-fit parts and shims remain. All
meshes passed closed surface, consistent winding, positive volume, one
connected solid and 300 mm per-axis checks. The geometry-only solid plastic
bound is 2721.2 g, down from 2924.6 g. This is not a measured print mass or
the total robot mass.

`python scripts/verify.py` also evaluated OpenSCAD intersections for the
body lip/socket, integral arm bridge/upper body, head plate/neck, rear spindle
sleeve/bracket, and a 20/40 tooth gear pair at five mesh phases. The body
stack and shoulder allow only their exact zero-height mating planes;
all other intersections must be empty. These checks do not establish clearance for every purchased
part revision, every fastener projection or a misrouted harness.

Bambu Studio also sliced `coupon.stl` with the installed H2D 0.4 mm profile,
0.20 mm Standard process and PLA Basic. It returned code 0, `Success.`,
and no warnings, and produced real H2D G-code inside a sliced 3MF. Its
predictions were 12.36 g and 1436 seconds for that coupon. The test used
isolated temporary settings and never connected to a printer. This one
stock-PLA coupon slice does not validate every structural PETG profile or
predict the full robot's mass. Evidence: `cad/h2d-slice-check.json`.

Revision B also has a dedicated actual-slice check for both body sections
and both complete arms using the H2D 0.4 mm profile, Generic PETG, 0.20 mm
layers, four walls, 20 percent gyroid and automatic normal supports. Exact
results, mesh hashes, predicted support-inclusive mass and time are in
`cad/h2d-structure-check.json`. These are software slices, not physical prints.

## Firmware and sounds

`pio run -d firmware` succeeded for the original Adafruit HUZZAH32 board,
using espressif32 6.5.0 and Arduino-ESP32 2.0.14. `pio run -d firmware -t
buildfs` succeeded with the web UI and sixteen MP3s in a 2 MiB filesystem.
Both binary images fit their declared partitions. They have not been
uploaded to a physical controller as part of this design task.

`python scripts/verify.py` compiles the actual controller header with
MinGW g++ using `-std=c++11 -Wall -Wextra -Werror`, and executes the result.
It protects arming lockout, stale leases, replay rejection, command timeout,
fault response, timer rollover, drive/steering bounds and reversal delay.
The phone test runs the real JavaScript with a simulated page/network and
checks release, cancel, focus loss, delayed arm replies and disconnects.
Node syntax checking also passes.

All sixteen MP3s have matching SHA-256 hashes and fully decode in FFmpeg.
They contain 42.1 seconds of original synthesized robot sounds. MP3 playback
on the physical ESP32 and acoustic output still need the build tests.

## Electrical consistency

The 154-row wiring schedule has six independent motor output channels.
The verification script compares all paired direction pins and control
constants with the firmware. It checks the pack and RUN divider upper
bounds remain below 3.3 V at the stated voltages. These are static checks,
not continuity measurements on a soldered harness. Source parts, ratings,
wire sizes, fuses and mounting consumables are included in the BOM.

## Physical acceptance still required

Measure purchased-part fit, wheel press-fit retention, actual steering
angles, gear mesh, bearing preload, shell mass, completed mass, supply
voltage/current, temperatures, stopping distance and runtime. Require the
rolling chassis to pass with the intended final load before printing and
fitting all skins. Stop if the motor load or thermal tests fail. Do not
describe this package as a tested functioning robot until those tests pass.
