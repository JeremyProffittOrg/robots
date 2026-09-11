# Digital verification and physical limits

The fabrication package passed digital checks. No printer, completed robot,
motor load, battery runtime or physical wireless link was tested during
this run. The staged commissioning tests remain necessary before operation.

## CAD

`python scripts/export_cad.py` produced 39 different STL meshes and a
manifest for 148 pieces, including first-fit parts and shim options. All
meshes passed closed surface, consistent winding, positive volume, one
connected solid and 300 mm per-axis checks. The geometry-only solid plastic
bound is 2924.6 g. This is not a measured print mass or the total robot mass.

`python scripts/verify.py` also evaluated OpenSCAD intersections for the
shoulder bridge/upper shell, head plate/neck, rear spindle sleeve/bracket,
and a 20/40 tooth gear pair at five mesh phases. Each intersection was
empty. These selected checks do not establish clearance for every purchased
part revision, every fastener projection or a misrouted harness.

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

Machine-readable digital check output is in `docs/verification.json`.
