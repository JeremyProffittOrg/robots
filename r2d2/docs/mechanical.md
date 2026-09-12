# Mechanical design and print guide

## Shape, size and printed parts

Revision C is nominally 609.6 mm high, with a259.25 mm main body diameter.
It has two whole stackable body prints, one complete dome and one print
per side leg. There are 10 STL designs and 14 installed printed pieces.
Small PCB spacers, structural shafts, bearings and strong brackets are
purchased or fabricated in metal. No body quarters or leg segments are
needed. The 13 DXF/SVG profiles are metal or insulating-sheet cutting
files, not additional STLs.

The exterior follows the reference ellipse, radar-eye and body-skin
drawings listed in appearance-research.md. The dome has an elliptical
rise, six crown panels, a top disk, angular eye housing, convex lens,
three projector cups, PSI disks and front/rear logic-display relief.
The body includes utility-arm shapes, louvers, doors, coin slots,
octagonal ports, couplers and a ribbed skirt. The side legs include
horseshoes, hubs, boosters, struts, ankle bracelets and cylinders.
These details are actual mesh relief and paint guides. They are not
functioning display lamps, utility arms or projectors.

This is a scaled, adapted rear-foot robot. It is not a claim of exact
current club-plan compliance. Feature placements without dimensioned
references are image-derived. The rear-foot placement follows the user's
wording; the familiar forward third-foot arrangement is not used here.

Coordinates are X across the shoulders, Y forward and Z up. Floor Z is 0.
Side-foot centers are X+/-165,Y0. Ground axles are local Y+/-37,Z31.5.
Wheel centers are nominally local X+/-29. Check actual hub insertion on
the purchased wheels; the stability calculation conservatively uses+/-26.
The side-foot exterior span is about 438 mm. Allow at least 500x600 mm clear
floor area plus the turning radius. The rear-foot center moves from
Y=-128.926 to-247.785 as posture changes. The front/back footprint also
changes with body tilt and head rotation.

## How the moving structure works

Two metal bearings support each 12 mm shoulder shaft. The aluminum leg
spine clamps to that shaft through a split metal hub. Each side ankle is
a rigid two-bolt metal joint. Extending the rear post therefore turns the
body about the shoulder axis while the side legs remain supported on the
floor. The legs swing relative to the torso. They are not independently
powered walking limbs. All three feet stay down; there is no two-foot
balancing mode.

The rear post has a separate square-tube sliding guide and a pin-ended
P16 actuator. The guide carries sideways bending. The actuator changes
length. A steel rod end and 12 mm transverse axle carry the rear-foot load.
The steering servo operates a separate link and does not carry body weight.
Its 8 degree yaw limit stays inside the rod end's10 degree misalignment
limit on a level floor. Pitch rotates about the axle rather than consuming
that yaw allowance. Use gentle arcs; do not command a pivot turn.

Normal actuator stroke is 5.03832-72 mm. This produces approximately 0-15.054
degrees of body tilt. Both rear joint and side ankles keep their selected
height. The fixed guide overlaps the inner tube by at least 160.5 mm across
that range. Physical NC limits lie outside normal travel, near 2 and 80 mm.
The software also checks position, current, progress, time and duty.

## Load basis and acceptance limits

The design mass ceiling is 9 kg, including battery, finishes and fasteners.
The initial 6 kg assumption was not met. The current estimate is about 8.95 kg,
so there is little reserve and no payload allowance.
This is a prototype commissioning limit, not a motor manufacturer's
payload rating. Shaft calculations use 3x gravity, and actuator demand
also includes a1.25 allowance for alignment/friction. The calculation
evaluates 101 positions and the stated center-of-gravity envelope.
It finds 213.7 N maximum actuator demand versus the selected 300 N lifting
rating,93.7MPa nominal shoulder-shaft equivalent stress and 68.8MPa nominal
inner-guide combined stress. These are screening calculations; they do
not include every weld, surface defect, stress concentration or fatigue
cycle. They do not certify the completed assembly.

Use shaft stock with a material certificate supporting at least 350MPa
yield strength, and 6061-T6 guide/frame stock. Do not substitute a soft
threaded rod for a precision shoulder shaft. If quoting SKF6001 bearing
ratings, fit the actual SKF bearings; the supplied housing bearings were
not assigned those ratings. SKF SA12E data applies to that rod end, not
to the surrounding clevis, welds or printed shell.

The loaded center of gravity used by the check is X+/-35 mm, body-relative
Y=-60 to+20 mm, and 80-170 mm below the shoulder axis. Weigh component groups
and calculate their weighted coordinates. Verify horizontal balance with
one scale under each foot. For level scales, Xcg=165*(right-left)/total
and Ycg=rearY*rear/total, with reactions in the same units. Check upright,
mid travel and maximum tilt. Use the component mass/height calculation
for vertical CG; three level scales alone do not measure CG height.

The requested TT motors remain the limiting drive components. Each has
a plastic gearbox and press-fit output wheels. Two wheels on one motor
share its torque. No continuous torque curve or shaft radial-load rating
was supplied with the cited product data. Strong metal legs do not remove
that limitation. Test the rolling chassis at the actual intended final
mass on a dry, level, hard floor. Require reliable starts, no gearbox
stall and no more than 0.5 A steady current per ground motor during gentle
travel. Measure rear-foot rolling drag and keep it at or below 10 N, the
calculation's acceptance ceiling. Reduce mass or revise the transmission
if those tests fail; do not raise the current limits to force movement.

Ground PWM is capped at 90/255. Head PWM is capped at 70/255. These are
duty commands, not measured speed. The rear-foot steering limit is 8 degrees.
The smallest commanded turn radius is roughly 0.92m in the upright stance
and increases as the rear foot extends. Tires still scrub in a tandem
four-wheel foot. Test path tracking and stopping distance at low speed.

## Body and head stack

The lower body mesh includes the skirt and starts at world Z130. Its
main cylindrical wall starts at 165. The body seam is Z269.7. The upper
body starts there and includes the fixed neck, ending at 454.3. The nominal
dome datum is 456.8, leaving 2.5 mm fixed-neck clearance. The integrated
raised crown reaches approximately 609.6 mm overall.

The lower seam has a3 mm locating lip, with 0.3 mm radial clearance in the
upper socket. Four M3x14 screws on radius 119 clamp the seam into captured
nuts in the lower flange. The lower shell's four tabs sit on the metal
base at Z173. Fit the upper body BEFORE the shoulder carriers, because
its shoulder openings are closed circles rather than long service slots.
Removing the upper body later requires releasing the shoulder assembly.
Routine electronics access is through the removable dome and top plate.

The head floor is Z413-415. The printed bearing tower starts at 415 and
holds 608 bearings at 415-422 and 434-441. A12 mm metal spacer contacts their
inner races. Nominally 0.8 mm of inner-race shims above the upper bearing
places the integrated dome stem at 441.8. The cap surrounds this stem
without touching it. The M8x60 bolt and captured nut connect the dome
rotor through the inner-race stack. Set free rotation without axial play;
do not squeeze the bearing seals with an oversized washer.

The dome underside includes its support spokes and a friction track at
65-88 mm radius. M7's wheel runs near radius 76.5. The holder bolts to the
metal floor and has an open, dropped motor pocket. Its nominal shaft
height is 426.3, giving approximately 1 mm tire compression against the
track. Adjust with thin shims and the actual tire, aiming for 0.5-1 mm
compression and reliable traction. Excess preload bends the shaft and
increases current. Head weight is supported by the bearings, not M7.

Use the metal-fabrication worksheet for all shafts, plates, guides,
clevises, secondary holes and fastener stacks. The CAD renders show
purchased component envelopes; the worksheet defines machining details
not visible in those simplified envelopes.

## Print order and H2D settings

1. Obtain the actual motors, wheels, bearings and servo. Print one
   drive_cassette, bearing_tower, bearing_cap and head_motor_mount first.
   Check fits on the real components. These are installed parts, not
   extra disposable coupon designs.
2. Keep the native STL orientation. Body sections are base-down. The
   dome is supported under its integrated rotor/stem. The leg lies
   diagonally with its open inboard face toward the bed. Remove internal
   supports before inserting the spine. Print two identical leg copies;
   the symmetric leg is turned 180 degrees about world Z for the other side.
3. Print outer_foot twice: one as supplied and one mirrored in native X.
   Keep both toes forward. Rear_foot is a separate whole print. The three
   drive cassettes are identical. Do not mirror or rescale bearing fits.
4. Use the installed H2D0.4 mm profile,0.20 mm layers, four walls, five
   top/bottom layers,20 percent gyroid, automatic normal supports including
   internal supports, and a5 mm outer brim. Dome material is PLA; the
   remaining parts are PETG. The 1.2 mm body skin limits actual perimeter
   count locally. Never use vase mode. Inspect previewed thin relief.
5. All 10 current STL files sliced with those settings without a reported
   warning. The slice report includes exact STL hashes, predicted masses
   and times. Typical single-part predictions including discarded support
   are 519 g lower body,608 g upper body,883 g dome,274 g leg and 258 g outer foot.
   These are software predictions, not physical print measurements.
6. Remove supports with the part fully cooled. Clear every bearing seat,
   lip, screw hole, motor slot and cable-tie slot. Ream a tight hole locally;
   do not scale an entire part to fix it. A bearing must seat by hand
   pressure without splitting its tower. Dry-fit the complete body seam.
7. Each STL fits within 300 mm per axis before brim. The checked H2D slices
   also account for the actual printer profile. Do not move a part into a
   nozzle exclusion area when rearranging a plate. No job was sent to a
   physical printer during this design run.
8. Weigh installed prints after removing supports. The solid-geometry
   plastic bound is recorded in cad/validation.json; it excludes purchased parts and supports.
   Final assembled mass and motor performance remain acceptance gates.

## Finish and service

Paint the relief using the colored CAD sheets: white body and legs,
silver dome and mechanical details, blue panel fields, dark recesses and
the eye lens. There are six crown wedges, not eight generic stripes.
Keep paint off bearings, threads, shaft clamps, wheel sockets, the body
lip and the head friction track. Use thin coats rather than heavy filler.

Switch both supplies off and unplug the battery before service. Support
the metal frame. Remove the dome's captured-nut connection while holding
the lower bolt; then lift the dome. Remove the head-floor fasteners and
unplug M7 to reach the electronics panels. Label each removable harness.
Release panel ties only after supporting the panel. Removing a shoulder
shaft or the rear actuator requires supporting the body independently;
the post is part of its load path.

Before each use, inspect the wheel press fits, gearbox cases, shaft
collars, clamp witness marks, clevis retention, guide pads, welds, wires
and battery straps. Recheck after the first hour. Replace a worn gearbox
or slipping wheel rather than forcing a cracked hub onto the shaft.
Keep lubricant off tire treads, the head track and electronics.
