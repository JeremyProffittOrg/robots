# Mechanical design and print guide

## Design envelope

Overall nominal height is 609.6 mm / 24 in, measured from the wheel contact
plane to the dome crown. The body is 260 mm diameter. The side foot plates
span 490 mm across X; covers increase this to 492 mm. The straight rear
foot extends to Y=-290 mm and the body front reaches Y=+132 mm with trim.
Allow about 500 x 430 mm floor space, plus turning clearance. Each exported
part is smaller than 300 mm on every axis. The dome prints as one 260 mm
diameter hemisphere. Revision B uses two complete stackable body prints,
`body_lower` (260 x 260 x 148 mm including the locating lip) and `body_upper`
(260 x 260 x 162 mm including the fixed neck). Each complete side arm is
124 x 68 x 295 mm. The arms include the shoulder bridge and cap. Main body
and arm construction therefore requires four prints, plus the dome.
Total printed quantity is 83 instead of 148; 32 are small PCB spacers.

Coordinates in CAD: X right, Y forward, Z up. Floor is Z=0. Main foot
centers are X=-190/+190, Y=0. Rear steering center is X=0, Y=-180. Wheel
axles are at local Y=-45/+45 and Z=31.5. All wheel axes start parallel to X.
The nominal wheel centers are local X=-33/+33; actual hub insertion depth
must be checked using the purchased wheels. Do not force a wheel against
the yellow gearbox. Motor bodies face the same way within each foot.

## Load and drive limits

Use only a dry, level, hard indoor floor. The design uses low-cost plastic
gearboxes, not load-rated wheelchair drive units. Two wheels on one motor
share its torque. A 63 mm wheel and the specified 0.8 kg.cm stall torque
give about 2.49 N per motor at 6 V stall. Six motors would give 14.94 N at
that unusable operating point. This build runs near 5 V with a 1 A driver
limit, so available force is lower. There is no rated continuous torque
curve or shaft radial-load rating in the product data.

Target a completed mass no greater than 4.5 kg. This is a commissioning
limit to test, not a manufacturer-approved motor load. Read the actual
sliced mass, then add the 0.7 kg battery, 0.456 kg wheels, 0.184 kg motors,
bearings, metal hardware, wiring and boards. The geometry-only solid
plastic bound in `cad/validation.json` is conservative for infilled parts
but excludes support material. Do not add payload, thick filler or ballast.

At 4.5 kg, an assumed rolling resistance coefficient of 0.03 gives about
1.32 N straight-line resistance. Turning also scrubs the tandem wheels.
That coefficient is only an engineering assumption. First test the rolling
frame with securely attached temporary ballast up to the intended final
mass. Require steady motion without stalls and no continuous current above
0.5 A per motor during gentle level travel. Stop a stuck motor promptly.
If the frame cannot pass, reduce mass or revise the transmission before
painting or fitting the decorative parts. The integrated body and arms
are required for the chassis test. Digital geometry cannot certify it.

The rear foot is steered up to 25 degrees each way. The side drive ratio
and rear speed follow the same circular path. Firmware does not request a
zero-radius pivot. The drive ceiling is 110/255 duty and the phone starts
at 35 percent of that ceiling. No encoder is fitted, so commanded speed
and angle are not measured speed or angle. Calibrate steering with a
protractor and observe actual path tracking.

## Purchased fits and adjustable mounts

Motor 3777 uses the manufacturer drawing in the research file. Its gearbox
thickness is about 18.6 mm and axle-tip span about 36.6 mm. The printed
cradle supports the motor case with thin foam and two cable ties. It does
not depend on uncertain case screw positions. The yellow case stays above
the 3 mm floor. Set the axle center at 31.5 mm with the wheels touching a
flat reference surface before tightening the ties. The cradle floor is at
Z=16 and its deck support pillars end at Z=65. Keep all ties off both axles.

Bearings are 608-2RS, 8 x 22 x 7 mm. Tower pockets are 22.2 mm diameter.
Print the fit coupon and one tower first. Seat bearings with hand pressure;
ream uniformly if necessary. Do not drive a tight bearing into a printed
tower with a hammer. Bearing shims are 8 mm ID, 12 mm OD, 1 mm thick so they
contact only the inner race. Ordinary large M8 washers can bind the seals.

Both gear sets use module 1.5, 20 degree pressure angle, 20/40 teeth, 6 mm
face width, and nominal 45 mm center distance. MCAD supplies an involute
tooth profile. The servo mounting slots permit mesh adjustment. The 20
tooth pinion attaches to the supplied servo horn with M2 hardware; no
printed spline is used. The 40 tooth hub has an M8 nut pocket to transmit
torque to the spindle. Use two jam nuts to lock the shaft after preload.

The servo mount drops its floor 8 mm below the deck. Set the horn/pinion
height with the included 1, 2 and 4 mm shims. Keep the two gear faces aligned
within 0.5 mm. The head pinion base is Z=461; rear pinion base Z=151. Servo
case and horn revisions vary; check the actual height before final wiring.
The rear bracket and head deck have clearance openings for the dropped
cradle. Use 1 mm side foam to prevent movement, then tighten two ties.

## Height stack and mating surfaces

The side foot deck is Z=65..70. Each one-piece arm starts at Z=70, with a
250 mm stem, integral bridge at Z=320..325, ribs to338 and a40 mm shoulder
cap ending at365. The shoulder cap was shortened15 mm so the entire arm
fits below300 mm print height. Two M4 rods still carry each arm's load.
The front/back shoulder windows admit a wrench to the upper rod nuts.
Inner bridge holes at X=+/-105,Y=+/-20 attach to the upper body's base frame.
The complete left/right arm STLs are supplied; do not mirror them again.

Body frame lower faces are Z=170,315,460; each frame is 5 mm thick.
Battery adapter is Z=175..178. Its 137 mm posts reach the middle frame at
315. The second adapter is Z=320..323. Four 97 mm posts reach the head deck
at 420. Head deck is Z=420..424. Four 36 mm posts reach the upper frame at
460. The body rods at X=+/-75,Y=+/-75 pass through this complete stack.
The utility deck sits on four 6 mm spacers at Z=329..332. All listed body
frames, rod sleeves, adapters, the head deck, neck and battery tray are
integral features of the two body prints. They are not separate print jobs.

The lower body sits at Z=170 and carries a full-circumference locating lip
up to Z=318. The upper body sits at Z=315; its socket clears that lip by
0.3 mm radially and vertically. The load-bearing faces meet at Z=315.
Four M4 body rods clamp the stack. No vertical seams, splice plates or
perimeter shell screws are needed. The upper body retains its side slots
for the integral arm bridges. Align the rear switch location before
lowering the upper body onto the lip; do not force a tight printed fit.

Rear attachment plate is Z=165..170, under the bottom frame. It picks up
the two rear body rods. The bracket is centered at (0,-180,110); its upper
flange ends at Z=165 and bolts under that attachment plate. Bearing tower
starts at Z=114 and ends at 140; cap ends at 143. A 38 mm spindle sleeve
starts on the rear foot boss at Z=75 and ends at 113. Add one 1 mm inner
race shim before the lower bearing. Bearing-to-bearing sleeve is 12 mm.
The upper bearing ends at 140, followed by one 1 mm inner shim and the hub
at 141..160. Its teeth occupy Z=151..157. Adjust jam nuts for free rotation
without axial play. The stationary cap clears the 12 mm rotating hub neck.

Head bearing tower is Z=424..450. The same inner race stack and upper shim
put its hub at 451..470. Head plate sits at 470..473. Four 6.6 mm spacers
at radius 119 mm carry the dome bottom at 479.6. The fixed neck ring is
Z=465..477; it has 2.6 mm clearance below the dome. Head plate tips stay
inside radius 124 mm. No light, speaker or wire is mounted on the spinning
dome. Keep loose wiring below Z=420 and away from both gear pairs.

## Print order and settings

1. Obtain the actual motors, wheels, servos and bearings. Print `coupon`,
   one `motor_cradle`, one `bearing_tower`, `bearing_cap`, `race_spacer`,
   `servo_mount`, `servo_pinion`, `gear_hub`, and all shim thicknesses first.
2. Check M3 clearance, M4 rod clearance, M8 shaft clearance, the 22.2 mm
   bearing pocket and the actual dual-wheel fit. Never scale an entire part
   to correct a hole; edit the relevant dimension and re-export that part.
3. Print both body sections, both arms and other structural PETG at 0.20 mm layers, four wall lines, five top/bottom
   layers and 20 percent gyroid as the starting settings. Load-bearing
   flanges, towers and gear teeth must contain continuous perimeters. Use
   dry filament. Check that the thin leg skins are fully filled by walls.
4. Print the dome and separate cosmetic parts in PLA at0.20 mm layers
   with a0.4 mm nozzle and two walls. Integrated body skins remain0.8 mm
   PETG, while arm skins are1.2 mm PETG. The slicer fits the requested wall
   count to these thin features. Do not use vase mode or scale whole parts.
5. Print both body sections base-down and arms standing on their lower
   flanges. Use automatic normal support, including internal support, under
   the integral decks, tall arm bridge overhangs and shoulder caps. Remove
   support through the large frame openings and shoulder access windows.
   Inspect every opening before inserting rods or boards. Fewer assembled
   pieces mean longer prints and more support removal inside each piece.
   The verified normal-support H2D slices predict608 g/18.5 h for the
   lower body,1310 g/37.8 h for the upper body, and481 g/about13.5 h for
   each arm. These figures include discarded support and are not the
   installed robot mass. Allow five1 kg PETG spools for these prints,
   remaining mechanisms, first-fit prints and waste; one PLA spool covers
   the dome and separate cosmetic parts. Re-slice for your filament.
6. The left and right arm files already have the correct orientation.
   No shell quarters, separate frames, body posts, splices or arm segments
   remain in the package. Test the lip/socket fit before tightening rods.
7. Print all quantities from `bom/printed-parts.csv`, including small
   spacers and the two side foot covers. Rear foot remains open for gear
   service; keep fingers away from its steering mechanism during operation.
8. Leave at least 5 mm around each part for brims. The H2D has a nominal
   300 x 320 x 325 mm dual-nozzle volume; verify excluded regions in Bambu
   Studio. Do not send jobs to the printer until the first-fit checks pass.
9. Slice the full quantity list and record mass before printing all skins.
   Add real purchased-part mass and keep the completed robot below the
   4.5 kg commissioning limit. The full plate layout was not physically
   printed or validated during this design run.

## Finish and maintenance

Paint the body white, dome silver and trim blue. Mask eight blue dome
panels separated by about 10 mm silver strips, plus a 12 mm blue band near
the dome base. Paint the eye recess black. Use `detail_panel.stl` as a
stencil for the body markings, or glue it with small conforming foam pads;
its flat back needs about 5 mm edge compensation on the cylindrical shell.
Paint the leg strips directly. These cosmetic parts are not structural.

For service, isolate both switches and unplug the battery. Support the
lower body and feet on a work stand. Remove the dome, unplug the labeled
lower-to-upper harness and remove all eight body/arm rod top nuts. Lift
the upper body with its attached arms vertically off the rods with a
second person. Keep the four inner arm bridge bolts assembled; their nuts
are reached from below only when the upper body is off. This also gives
battery access. The dome lifts after its four retaining
screws are removed. Recheck rod nuts, gear mesh, wheel
press fits, cable ties and bearing play after the first hour, then before
each session. Replace worn gearbox units rather than forcing a slipping
wheel onto a cracked shaft. Do not lubricate belts or wheel treads; there
are no drive belts in this design.
