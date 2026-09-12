# Digital verification and physical limits

This package contains a digital prototype. No physical robot was printed,
assembled, driven or load-tested during this run. The assembly chapter's
fit, strength, electrical and driving tests remain required.

## Geometry and fabrication checks

The current print set is 10 STL designs and 14 physical prints. Mesh checks
require a closed surface, consistent winding, positive volume, one connected
solid, nonnegative bed Z and less than 300 mm extent on each axis. The actual
H2D slices also check the installed printer profile rather than relying only
on a nominal bounding box.

Fifteen CAD checks cover the body seam, shoulder openings, fixed neck,
head tire/motor/floor, foot wheels and frame, both covers, rear steering
envelopes and rear-post exit. Only explicitly named mating planes are
allowed to touch. The body seam is checked from source with a0.005 mm
contact allowance: the installed CGAL version raised an assertion on
re-imported coplanar STL surfaces. The source Boolean test resolves that
numerical issue; exported STL connectivity and actual slicing are checked
separately. These tests do not prove every physical part revision or
fastener tolerance will fit.

The 22-row fastener worksheet checks nominal grip, washers, full nut
engagement and blind-thread depth. Hex-pocket checks use across-flats
dimensions: the 15.4 mm circumscribed dome pocket accommodates an M8 nut,
and the 6.8 mm body pockets accommodate M3 nuts. The guide and horn hardware
also require the measured rod-end sleeve width and full angular clearance.

The kinematic script evaluates 101 post positions. It keeps the rear
pivot at 113 mm, retains both complete guide-pad stations and checks the
support polygon over the stated CG envelope. Its 9 kg design case includes
3x gravity and the additional actuator alignment/friction allowance.
Calculated demand is 213.7 N versus the actuator's300 N lifting rating;
nominal shaft stress is 93.7MPa and inner-guide stress 68.8MPa. These are
section calculations, not a finite-element, fatigue or weld certification.

The initial 6 kg mass assumption was not met. The current budget uses
cut-profile areas, material-density assumptions, G-code model extrusion
and explicit purchased-component allowances. It is approximately 8.95 kg
against a9 kg limit, with little margin. Read mass-budget.csv/json for
the current figures. Weigh the real parts; there is no payload allowance.
This estimate does not establish that the selected TT motors can drive
that mass on the builder's floor.

## Actual slicer output

All ten parts are sliced with the installed H2D0.4 mm profile,0.20 mm layers,
four walls,20 percent gyroid, normal automatic supports and 5 mm brims.
Each result records its current STL hash, material, full profile hash,
return code, warning status, G-code hash and predicted material/time.
Unchanged matching records can be reused; changed meshes or profiles
are re-sliced. No printer connection or user-profile change is made.

Installed-model mass is separated from support/brim using labeled
moving extrusion in the generated G-code. Machine purge/flush moves
and stationary unretraction are excluded. This is a software estimate,
not a weighing result. The current fourteen-copy model prediction is
about 1.72 kg. Support material is additional filament that is discarded.

## Firmware, wiring and sounds

PlatformIO builds the actual program and its 2MiB filesystem for the
original HUZZAH32. Both fit their partitions. Native C++ tests exercise
arming, lease/replay rejection, command timeout, fault handling, bounds,
reversal, post progress/current/feedback checks, cooldown and linkage
geometry. The JavaScript test runs the actual phone code with a simulated
page/network and checks release, cancel, focus loss, delayed replies and
disconnect behavior. These are not radio-range or on-device tests.

The 220-row connection schedule is compared with firmware GPIOs, motor
channels, head direction, independent NC actuator limits, feedback and
I2C wiring. Divider upper bounds stay below 3.3 V at the stated voltages.
These are static net checks, not continuity measurements on a harness.

All 16 original MP3s have matching SHA256 hashes and fully decode with
FFmpeg. They contain 42.1 seconds of synthesized robot sounds. Physical
ESP32 playback and speaker output remain part of commissioning.

## Drawings, video and publication

The 18 PNGs include the assembled robot, orthographic and separated views,
internal mechanisms, all ten printed components, thirteen cut profiles
and the posture curves. CAD and image hashes identify the current revision.

The 30second1920x1080 video is a CAD simulation. It shows head rotation,
rear-post motion, the exposed frame and separated covers. Its timing is
illustrative. It is not footage of a built or tested robot. Source hashes,
frame count, duration and full decode are checked before publication.

The repository's OIDC GitHub workflow uploads only the final PDF and MP4
to a dedicated private S3 bucket, served through CloudFront HTTPS. It
downloads both anonymously, compares them with the committed bytes,
checks MP4 range delivery and verifies direct anonymous S3 access stays
denied. The final email is sent only after that workflow and PDF review.

## Physical acceptance

The builder must verify purchased fits, head-wheel traction, actual
steering/post positions, loaded mass/CG, joint retention, frame proof load,
motor current, temperature, rolling drag, stopping distance and runtime.
Keep the physical test log with the unit. Do not describe the robot as
physically validated until those tests have passed.
