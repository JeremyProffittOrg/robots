# Metal fabrication worksheet

## Drawing conventions and stock

All dimensions are millimetres. The 13 files in cad/metal are 1:1 DXF/SVG
cut profiles. Set imported DXF units to mm. PNGs and PDF figures are
identification drawings, not paper drilling templates. Profiles contain
through-cut outlines and pilot/clearance holes. This worksheet adds
thickness, depth, thread, fit and weld requirements. Do not infer a thread
from the diameter of a rendered cylinder. Purchased parts in the 3D views
are dimensional envelopes.

Use the thicknesses and quantities in bom/hardware.csv and the metal
manifest. Flat frames, carriers, spines, crossbars and guide parts use
6061-T6 aluminum. Foot load frames and the moving yoke use weldable steel
with a documented minimum 250MPa yield. Ground shoulder shafts require
at least 350MPa yield. Insulating electronics panels use 3 mm G10 sheet.
Do not mix steel and aluminum in a welded joint; use the bolted interfaces.

General cut dimensions: aim for+/-0.2 mm; mating hole centers+/-0.1 mm.
Critical bearing bores use the stated fit, not the general cut tolerance.
Deburr to a small smooth edge without enlarging bearing/shaft seats.
Keep paired carrier and fork holes coaxial. Final reaming after assembly
is preferred to trying to correct misalignment with loose fasteners.
Maintain at least 1 mm measured clearance to moving hardware and shells.

## Shoulder carriers and leg spines

metal_chassis is a160x255x4 side-plate profile, with the world Z170-425
datum retained in the drawing. Cut two identical plates. The window is
interrupted by integral webs at both guide-crossbar mounts. Do not remove
those webs: they carry the rear-post force into the chassis. Shoulder
axis is Y0,Z390. The right plate occupies X95-99; mirror this location
for the left. Four electronics support rods use Y+/-70,Z275/365.

metal_carrier is 64x64x4 with chamfered corners. Cut four. The center 26 mm
opening clears the 22 mm collars. Two 5.5 mm housing fastener holes are
Y0,Z+/-21 about the shaft. Four 4.5 mm carrier holes are Y+/-25,Z+/-22.
Right carrier faces are X101.5-105.5 and 158.5-162.5. Four 53 mm spacers join
them. Four 2.5 mm spacers separate the inner carrier from the chassis.
M4x75 screws, washers and nuts clamp that stack. Repeat on the left.

Use four MISUMI BACA6001ZZ housings,52x36x13. The bearing centers are
X112 and 152 on the right, a40 mm span. Mount each housing separately
with two M5x16 screws through its carrier. Do not run one screw through
two independently tapped housings. If relying on the cited SKF bearing
data, replace the housing bearings with actual SKF6001-2RSH12x28x8 units.
Retain the proper housing rings and shoulders. A replacement bearing
must seat squarely; do not clamp a loose bearing with adhesive.

Cut two 12h5 ground steel shafts 90 mm long. Right-hand shaft ends are
X92 and 182. Its inner collar spans 97.5-105.5; outer collar 158.5-166.5.
Collars rotate inside the 26 mm plate openings. There is 1.5 mm nominal
clearance from the outer collar to the leg pad. Use split collars of
the listed envelope; verify bolt heads also clear the plate openings.

metal_spine is a4 mm plate with a60 mm shoulder pad and 25 mm wide lower
spine. Cut two. Right spine is X168-172. Its ankle ends at Z106, with
two 6.5 mm holes at Z119 and 139. Six skin-retention holes across the two
spines are 3.4 mm, at 45,155,225 mm below the shoulder. The lower skin screw
is at Z165, above the rigid ankle. Use M3x25 skin screws, allowing for
the raised blue face on the middle mount. The four pad holes
are 4.5 mm on 32 mm PCD at 45 degree increments. Countersink these on the
inboard face for flush M4 screws. Do not remove more material than the
actual screw-head angle and height require.

Machine two split hubs,44 mm OD,10 mm thick, with a12H7 clamp bore. Tap
the four pad holes M4, matching the 32 mm PCD. A1.2 mm radial saw slit runs
from the bore to the outer edge at Y positive,Z0 in the hub's face.
The M4 clamp bolt crosses this slit at Y17, along Z. Machine flat 8 mm
spotfaces near Z+/-5 for its washer and nut, leaving the clamp ligaments
intact. Use the M4x20 bolt and locking nut. Pad screws are M4x10. The
right hub spans X172-182. Check the shaft slips in before tightening,
then mark the shaft/hub with a witness line to reveal later movement.

## Base, top floor and electronics panels

metal_base is 3 mm aluminum at Z170-173. metal_headfloor is 2 mm aluminum
at Z413-415. Cut one each. Their four main mounting holes are X+/-89,
Y+/-55. Eight 12x20x20 aluminum corner blocks occupy X83-95 on the right
and-95 to-83 on the left, Y45-65 or-65 to-45, at Z173-193 and 393-413.
Cross-drill 4.5 mm at each block center in X and Z. The side-plate holes
are Z183/403. Use M4x25 for horizontal joints and M4x30 for vertical
joints, with accessible nuts. Clamp the frame square before tightening.

The base's rear notch clears the guide/actuator. Battery strap slots
are at X+/-35,Y-7/47. Four shell tabs on radius 119 align with the extra
M3 base holes. Keep those screws accessible until the lower shell is
installed. Add a thin insulating/padding layer under the battery; do
not use foam as a structural spacer at the chassis bolts.

The head-floor center hole is 16 mm. Four 3.4 mm holes on radius 24 at 45 degree
increments mount the bearing tower. The rectangular window X30-64,
Y-65 to 53 accepts the dropped motor holder. A separate wheel opening
is X59-91,Y+/-32. Holder holes are X23/69,Y-50/45, outside the tire.
The 190x160 floor terminates at the chassis inner faces. The holder's
wings sit on top of the floor. No broad foot or
head deck from an older revision belongs in this assembly.

panel_front and panel_rear are 160x100x3 G10 sheets. Their 10 mm grids are
general mounting locations; the rear has a69 mm speaker opening. Four
M4x206 support rods cross the chassis at Y+/-70,Z275/365. Nuts and
washers secure each rod to the side plates. Tie each panel independently
to its two rods through the large corner slots. Panel planes are at
Y70-73 and-73 to-70, centered on Z320. Use redundant ties and strain
relief so harness pull cannot move a panel.

Use 6 mm nylon standoffs under boards. Arrange the Feather and low-current
audio/sensor boards on the front panel. Place drive converters/drivers
on the rear panel around the speaker and on available front-panel space.
Keep tall items near the panel center: the cylindrical shell reduces
available depth near its corners. Keep outer component faces within
Y+/-100 and X+/-80, with additional corner clearance to the actual shell.
Match-drill board holes using the purchased board after checking both
faces for tracks/components. The grid is not a claim that every factory
PCB uses 10 mm mounting pitch. UBECs and inline fuse holders use retained
straps/ties; do not cover their heat-producing surfaces.

## Welded four-wheel foot frames

Each foot begins with metal_sole, a4 mm steel T profile. Its narrow part
is 16x151, at X+/-8,Y-96 to 55,Z12-16. The transverse 44x8 feature at Y0 is
part of the same cut profile. Do not replace it with a wide plate under
the wheels. The motor-cassette screws are at X0,Y-90,-23,52. The paired
motor-tie slots must remain open after coating.

Weld two 4x8x55 stanchions to each T sole: X=-21 to-17 and 17 to 21,
Y-4 to 4,Z16-71. Weld metal_bridge on top at Z71-75, centered X/Y.
It is 64x50x4, with cover holes X+/-27,Y+/-17. Its lower face clears the
63 mm tires. The stanchions occupy the 11 mm longitudinal gap between axle
rows; maintain at least 1 mm clearance after wheel tolerances and welds.
Use controlled welds without large beads in the tire gap. Check each
frame flat and square before fitting plastic or motors.

For each outer foot, weld metal_ankle vertically at X=-1 to 3,Y+/-12.5,
Z75-152. Its two holes are 44 and 64 mm above its lower edge. The leg
spine sits against its outboard face and bolts with two M6x20 screws.
The left assembly is reflected across X. The side ankles are rigid;
do not leave these bolts loose to make another pivot.

For the rear foot, weld two metal_fork ears at X=-12 to-8 and 8 to 12,
Y+/-15,Z75-128. Their 12.1 mm bores are at Z113. Finish the inside gap to
16 mm and keep both bores coaxial. Two 3 mm inner-race spacers plus the
rod end's10 mm inner ring fill this gap. The outside rod-end head is
only 8.5 mm wide, leaving room for its limited yaw.

The rear axle is Norelem 07534-12X25: steel 12.9,12 mm shoulder,25 mm shoulder
length, M10x16 threaded tail and 18x9 head. Place a1.3 mm total head-side
shim between head and the first ear. This makes the clamp stack 25.3 mm,
slightly longer than the shoulder, so the nut clamps the inner race
rather than bottoming against the shoulder end. Use the 2 mm M10 washer
and locking nut outside the far ear. Keep at least two full threads
beyond the nut and at least 1 mm clearance to the adjacent actuator ear
through the full yaw range. Dress only unused thread if needed; never
shorten the load-bearing shoulder. Check free pitch/yaw after clamping.

The rear servo platform is 34x60x4 steel at X=-47 to-13,Y-80 to-20,
Z66.1-70.1. Cut its 21.7x42.7 body opening at X=-40.85 to-19.15,
Y=-71 to-28.3. Its 15x5x5 step joins it to the bridge at X=-32 to-17,
Y-25 to-20,Z70-75. Four 3.4 mm-wide fore/aft slots are centered at
X=-35/-25,Y=-74.4/-24.9. Their 4 mm travel allows setup against the
actual servo flanges. Four 20 mm steel M3 standoffs support the servo ears.
Use uniform shims to set the horn's top face at Z109.5, centered at
X=-30,Y=-60. The link's ball-center plane is Z113, not the case top.
Measure the actual ear/shim/washer grip, then trim the M3x20 ear screws
to give 5 mm thread engagement without meeting the opposite standoff screw.
The dimensions of the actual servo flange and horn must be checked;
the CAD case is an envelope. Verify a1 mm gap from the linkage to the
cover opening and from the servo to all wheel tops.

## Telescoping guide, adapter and actuator

Guide coordinates are X transverse, N across its sloping face and T
along the post, positive downward/rearward. The origin in body coordinates
is(0,-40,240). T slopes 35 degrees rearward from vertical. Thus
Y=-40+N*cos 35-T*sin 35 and Z=240-N*sin 35-T*cos 35 before body tilt.
The outer guide spans T=-150 to 50. The inner tube ends at L-62.5,
where L=150+actuator stroke, and is 270 mm long.

Use 31.75square x3.175wall outer tube and 19.05square x3.175wall inner
tube. Fit four acetal pads per station near T=-90 and 30. Both complete
20 mm pad stations remain engaged even at maximum extension. Start with
3.175 mm pad thickness, then fit to actual tube corner radii and straightness.
Target smooth, low-play sliding without a hard spot over the entire
working range. Retain pads mechanically with two M2x5 countersunk fasteners per pad,
at each station center plus/minus 5 mm along T. Keep at least 0.5 mm tip
clearance to the sliding face. These are short retaining fasteners
that stop inside the pad, clear of the sliding tube. Check actual wall
and pad thickness before drilling. Do not drive a screw into the inner
tube from the stationary outer guide.

Two 190x30x10 crossbars lie at T=-75 and 0. Their centers are N=-30.875.
This puts their front face at N=-15.875 against the tube. Blind-drill 5 mm
at each X end,15 mm deep, and tap at least 12 mm usable M6 thread, for the chassis screws. Do not drill
one 190 mm-long axial hole. Add 6.5 mm U-bolt holes along N at X+/-21,T0
relative to each bar. M6 square U-bolts have 36 mm inside width and 75 mm
legs. Their curved/back portion bears across the outer tube; nuts and
washers sit behind the crossbar. Tighten evenly without distorting the
guide until the inner tube still slides freely.

On the T0 bar only, mill a4 mm-deep front-face pocket at X24-52 across
the 10 mm axial height. This receives the fixed actuator bracket flush.
From the pocket bottom, drill and tap M4 at X32/44,T0, to 22 mm depth.
Use M4x25 screws through the 4 mm bracket and washers, leaving tip clearance.

Machine the 34x34x65 adapter with a19.2 mm square socket 35 mm deep from
its proximal face. The opposite face has an M12x1.75 tapped bore 24 mm
deep. Use the appropriate tap-drill diameter and thread gauge; the CAD
pilot is not a finished thread. Two 5.5 mm cross holes are 10 and 26 mm from
the proximal face. They also pass through the moving tube. Put 12.7 mm
long steel crush sleeves inside that tube before tightening the M5x45
bolts. The stationary outer guide is not drilled for these bolts.

Four M4 blind holes on the adapter's rear N face hold the yoke. Their
X coordinates are+/-11, with axial positions 17.5 and 29.5 from the
proximal face. Drill to 7 mm and finish usable threads to 6.5 mm with a
bottoming tap. M4x10 through the 4 mm yoke engages 6 mm. Confirm that no
screw projects into the square socket or M12 bore.

Fit the SKF SA12E so its eye is 54 mm from the thread tip, with 21.5 mm
thread engagement and the 6 mm jam nut seated. The eye then lies at T=L.
The nut and adapter must clear the fork top through all body positions.
Hold the rod end while tightening the jam nut; do not use the spherical
joint as a wrench reaction point.

The actuator eye line is X38,N0. The fixed eye is T3 and moving eye T=L,
giving 147+stroke millimetres between eyes. Its black case lies outside
the guide, not inside it. Mount the fixed aluminum clevis to the T0
crossbar with two M4 screws. It has 10 mm inside spacing. Center the 8 mm
rear eye with 1 mm spacers. Center the 6 mm front eye with 2 mm spacers in
the moving yoke clevis. Use plain 4 mm steel pins 24 mm long, with 1 mm
crossholes 1.5 mm from each end, outer washers and positive retaining clips.
Do not use threads as the running surface inside an actuator eye.

metal_yoke is 4 mm steel. Its plate is behind the actuator at N=-21 to-17,
not through the motor case. Weld the two 4x24x14 actuator ears at X29-33
and 43-47, N=-17 to 7,T=L-7 toL+7. Their pin holes lie at N0,T=L.
Weld the 3.2 mm steering-link ear at X=-37.5 to-33.5 in the same N/T range.
Machine the yoke's four mounting holes and cam tab from its DXF. Bevel
the two axial cam-entry edges lightly and remove sharp burrs.

## Limit rail and rear steering link

metal_limit_rail is 3 mm aluminum, in the X=-76 to-73 plane. Its drawing
axes are N and T, spanning N=-45 to-15,T6-205. It remains outside the
rear-foot shell. Its 12x13x10 clamp block occupies X=-73 to-61,N=-45
to-32,T5-15. A M5 screw along T at X=-67,N=-38.5 attaches the block to
the crossbar. Two M3x6 screws through the rail engage short blind holes
in the block at N=-42/-35,T10. Keep those blind holes clear of the M5
through bore; do not drill them through the block.

The actual SS-01GL mounting bores run across its 6.4 mm thickness, along
X in this assembly. They do not run along N. Switch bodies are 19.8 mm
along T and 10.2 mm along N. Their nominal mounting-hole line is N=-29.3.
For nominal cam contact at T77 or 185, the two mounting holes are at
T=contact-14.5 and contact-5. The rail slots permit N adjustment to set
lever depression. Use M2x14 screws, washers and locking nuts.

The 30 mm moving cam spans T=L-75 toL-45, and reaches X=-72.5. At stroke 2,
its retract-side edge reaches T77. At stroke 80, its extend-side edge
reaches 185. Its length keeps the appropriate switch actuated throughout
the remaining travel to either physical endpoint. Set the actual trigger
with a meter and detached actuator. Aim near 2/80 mm, with normal 5.04-72 mm
travel fully clear. Adjust to a small measured overtravel within Omron's
1.2 mm allowance; do not force the lever against the switch body.

The rear link joins guide point Q=(-30,0,113) to a12 mm servo crank about
S=(-30,-60,113), expressed relative to the rear foot's center. Link
center distance is 61.188 mm at neutral. The guide-end stud axis is X;
the horn-end stud axis is Z. This lets pitch rotate about the first stud
while the spherical ends accommodate yaw. Use two Igus KBRM-03-MH rod
ends with stainless-steel inner sleeves. Their verified sleeve clamping
width is 6.1+/-0.2 mm, head diameter 13 mm, housing thickness 4.5 mm, eye-to-
threaded-mouth distance 18.5 mm and minimum usable M3 thread depth 5 mm.
Their 30 degree limit is one-sided misalignment. The neutral guide-end
skew is 11.31 degrees; check the entire yaw sweep with washers fitted.

At the guide ear's X=-33.5 face, use nominally 0.45 mm shims plus half the
actual sleeve width to put the ball center at X=-30. At the horn top
face Z109.5, the same nominal shim puts the ball center at Z113. Adjust
to the measured sleeve width. Use small washers and verify that they
clamp the sleeve without obstructing the housing; sleeve OD was not
verified from the catalog and must not be inferred from housing thickness.

Install the guide M3x20 button-head screw from the bearing side. Its
head faces the rear axle; the locking nut and surplus thread face away
from that axle. Install the horn M3x16 button-head screw from beneath
the horn. Check actual case and full-sweep clearance before tightening.

Two 18.5 mm eye offsets leave 24.188 mm between the threaded mouths. Nominal
rod length 34.188 mm gives 5 mm insertion each side; measure actual usable
depth and avoid bottoming. Adjust the finished assembly to 61.188 mm
centers and lock the two link jam nuts without exceeding the 0.5 Nm
manufacturer thread-torque limit. The sleeve clamping limit is 4 Nm;
do not use that larger value on the M3 female threads.

Igus lists 400 N long-term tensile load along the link, but only 50 N
long-term transverse load. The estimated servo-stall link load is below
70 N along the link. Do not apply the tensile rating to an off-axis load.
Proof-test the detached link to 100 N and check free articulation. Vertical
body load still bypasses this linkage. Set foot yaw to 0 before fixing
the horn, then verify+/-8 degrees with a protractor and firmware calibration.

## Inspection before powered assembly

Measure the carrier span, shaft fits, fork spacing, pin retention,
adapter engagement, guide overlap and moving clearances. Lay each foot
on a flat surface before fitting motors. Correct welding distortion in
metal; do not pull the structure straight with plastic covers. Inspect
all welds and edge ligaments. Proof-load the metal chassis in a supported
fixture before putting the robot's weight through the TT gearboxes.
The assembly chapter specifies that staged test and the later motor test.

Primary dimensional sources:
[MISUMI bearing units](https://es.misumi-ec.com/pdf/fa/2014/P1_0931-0932_F14_EN.pdf),
[SKF SA12E](https://docs.rs-online.com/0820/A700000008261043.pdf),
[P16 datasheet](https://www.actuonix.com/assets/images/datasheets/ActuonixP16Datasheet.pdf),
[Omron switch dimensions](https://omronfs.omron.com/en_US/ecb/products/pdf/en-ss.pdf),
[Norelem shoulder screw07534](https://norelem.co.uk/medias/07534-Datasheet-27418-Shoulder-screws-similar-to-ISO-7379-en.pdf?context=bWFzdGVyfHJvb3R8MTg4MjAxfGFwcGxpY2F0aW9uL3BkZnxhR1psTDJobU1pODVORGN6TmpZNE9UTTVPREEyTHpBM05UTTBYMFJoZEdGemFHVmxkRjh5TnpReE9GOVRhRzkxYkdSbGNsOXpZM0psZDNOZmMybHRhV3hoY2w5MGIxOUpVMDlmTnpNM09TMHRaVzR1Y0dSbXwzNGE2NmQxMzNlMGJiY2E2Nzc4MGRkZmVjMWVlODI1MjRlZWU5NTcyNjNhMzg3YTMwY2Q5YjkzMmU4NWVlZmNh).

[Igus KBRM-03-MH dimensions](https://www.igus.com/contentData/Product_Files/Download/pdf/2016%20igubal%20complete.pdf), [Igus load and angle directions](https://www.igus.com/us/pdf/igubal_rod_end.pdf).
