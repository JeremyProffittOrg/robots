# Revision C mechanism design basis

The rear-post configuration follows the user's explicit rear-foot wording.
All three feet remain down. Side ankles are rigid metal connections; the
body rotates on two metal-supported shoulder pivots. The side legs swing
relative to the body as the rear actuator changes posture. This is not
independent walking or a two-foot balancing robot.

The design target is a 6 kg maximum assembled mass, with a 3x gravity load
case. This is not a tested working-load rating. The selected drive motors
remain the requested Adafruit3777 units. Their plastic output gearboxes and
press-fit wheels still limit drive durability and usable weight. Structural
joint strength does not establish motor performance.

## Selected load paths

- Shoulder pivots: 12 mm precision-ground steel shafts, two 6001 metal
  bearing housings per side on a metal carrier with 40 mm bearing-center
  spacing. Use the researched MISUMI BACA6001 housing dimensions. Any bearing
  capacity used for calculation must match the bearings actually fitted.
  Shaft material certificate must support at least350 MPa yield strength;
  do not infer a heat-treatment rating from a generic shaft listing.
- Side legs: 6061-T6 aluminum spines,25 x4 mm, with a60 mm shoulder pad,
  a split-clamp metal shaft hub, and two M6 ankle bolts. Printed horseshoe,
  booster, strut and ankle details cover this load path.
- Guide: outer6061-T6 square tube31.75 x31.75 x3.175 mm,200 mm long;
  inner6061-T6 square tube19.05 x19.05 x3.175 mm,270 mm long. Nominal guide
  pad thickness3.175 mm per face; fit replaceable acetal pads to measured
  tubes. Maintain at least100 mm overlap in every allowed position.
- Actuator: Actuonix P16-100-256-12-P.100 mm stroke,300 N lifted,500 N static,
  20 percent duty. Its4.25 mm eyes accept the supplied hardware or M4.
  The rear body envelope is36 x20 mm; reserve the full147-247 mm eye range.
  It has feedback but no internal end switches. Use external direction-aware
  hardware limits and a local position/current/timeout interlock.
- Rear-foot articulation: SKF SA12E steel rod end,12 mm bore, M12 thread,
 10 mm inner-ring width, maximum35 mm head diameter,54 mm eye-to-thread-tip
  length, minimum28 mm thread length. The SKF-generated sheet lists10.8 kN
  dynamic and24.5 kN static basic ratings and10 degree misalignment. Rear
  steering is limited to8 degrees, leaving a small allowance for alignment.
  The pitch motion rotates around the transverse axle, rather than consuming
  the yaw misalignment allowance. Operation is restricted to a level floor.
  The complete clevis, fasteners and guide still require proof testing.

Outer guide tube source: [OnlineMetals18015](https://www.onlinemetals.com/en/buy/aluminum/1-25-x-0-125-aluminum-square-tube-6061-t6-extruded/pid/18015).
Inner tube specification: [6061 square tube range](https://store.buymetal.com/aluminum/square-tube.html).
Rod-end dimensions and ratings: [SKF-generated SA12E sheet](https://docs.rs-online.com/0820/A700000008261043.pdf).
Actuator dimensions/wiring: [Actuonix P16 datasheet](https://www.actuonix.com/assets/images/datasheets/ActuonixP16Datasheet.pdf).

## Motion geometry

World X is along the shoulder shafts, Y forward and Z upward. Shoulder
axis is Z390; rear joint is Z113. The guide reference is(0,-40,240), with
its axis35 degrees rearward from down. At actuator stroke s, the shoulder-
relative rear point is Y=-(40+(150+s)sin35), Z=-(150+(150+s)cos35).
Rotating the body about its shoulder axis solves the floor-height constraint.
`cad/kinematics.scad` and `scripts/check_kinematics.py` record the equations.

Outer guide occupies axial coordinates-150..50. The inner guide terminates
at L-62.5, where L=150+s; its270 mm length provides the overlap checked by
the script. A separate moving metal adapter joins the tube to the rod end.
Allow21.5 mm rod-end thread engagement plus a6 mm jam nut, within the
manufacturer's minimum28 mm thread length. Do not put transverse fasteners
through the stationary guide where they would obstruct its moving member.

The load calculation evaluates101 positions. It uses a measured rear-foot
rolling-drag acceptance ceiling of10 N, not an invented motor gearbox drag
rating. The horizontal loaded CG must remain in X+/-35 mm and body-relative
Y-60..+20 mm, with its vertical coordinate80-170 mm below the shoulder axis.
Weigh and balance the real robot. Move the battery or reduce weight if the
measured CG falls outside that envelope.

## Controls and head rotation

Retain phone Wi-Fi, stop-on-lost-command behavior and original MP3 sounds.
Posture changes require stopped drive and centered steering. Read actuator
position locally; stop on missing/stale/out-of-range feedback, excess
current, blocked travel, time limit or operator stop. Respect actuator duty
and cooldown. Do not restart movement after a power or network interruption.

The head uses a separate internal TT motor and Adafruit3766 friction wheel,
running against an integral underside track. That is twelve ground wheels
plus one internal head wheel. Head weight runs through bearings, not the
motor shaft. The motor mounting plane must allow tire-preload adjustment.
Head rotation does not require a wire crossing the rotating bearing.

## Integration geometry selected for the metal drawings

These dimensions are the chosen design, not a manufacturer's assembly rating.
The complete fabrication release must include their drawings and fit checks.

Shoulders are at X+/-165,Y0,Z390. Each right-hand carrier has two metal
bearing-support plates at X101.5..105.5 and158.5..162.5, mirrored for the
left. BACA6001 housing centers are X112 and152:40 mm apart. Carrier plate
outline is64 x64 x4 mm with10 mm chamfered corners, a26 mm shaft/collar
opening, housing mount holes at Y0,Z+/-21 and four carrier holes at
Y+/-25,Z+/-22 relative to the shoulder axis. Four metal standoffs10 mm OD,
4.5 mm ID and53 mm long join the plates. Inner spacers are2.5 mm long.
Use separate opposing M5 screws for the tapped housing holes; do not run
one screw through two independently tapped housings. Four M4x75 carrier
bolts pass through clear holes, standoffs and chassis plate.

The right chassis side plate occupies X95..99,Y-80..80,Z170..425. Its large
lightening window spans Y-62..62,Z190..355. The shoulder shaft/collar hole
is26 mm. Match the carrier holes above. Mirror for the left chassis side.
The right ground shaft occupies X92..182,12 mm diameter; mirror for left.
Its inner collar occupies X97.5..105.5 and outer collar158.5..166.5,
22 mm OD,8 mm width. These rotate with the leg shaft and clear the26 mm
plate bores. The leg pad is X168..172,60 mm diameter, integral/fastened to
the25 x4 mm spine. The split metal hub is44 mm OD x10 mm axial thickness,
X172..182,12H7 clamp bore, four M4 mounting holes on32 mm PCD at45-degree
increments. A radial clamp screw is placed away from those mounting bores.
Use flush countersunk leg-pad screws to preserve moving clearances.

Rigid side-ankle connections use two M6 bolts at Z119 and139. The spine
ends at Z106, giving at least13 mm lower edge distance. Printed side-leg
cases need open inboard service backs and do not carry these ankle loads.

The stationary guide spans axial-150..50. Its two chassis clamps are at
axial-75 and0. Crossbars run across X between chassis plates. Their centers
are offset-30.875 mm along the guide's perpendicular direction, so their
30 mm face contacts the31.75 mm tube without intersecting it. Use square
U-bolts, crush-safe backing faces and metal-to-metal clamping; nothing crosses
the moving tube's path. Minimum calculated overlap is more than150 mm.

The moving adapter is34 x34 x65 mm, from axial L-97.5 to L-32.5. It has
a19.2 mm square socket35 mm deep from its proximal face and an M12x1.75
tapped bore24 mm deep from its distal face. The19.05 mm inner tube ends
at L-62.5. The SA12E eye is at axial L; its54 mm shank gives21.5 mm thread
engagement and room for a6 mm jam nut, with0.5 mm thread allowance.
Do not bottom the rod end against the thread drilling.

The rear-foot transverse axle is12 mm steel through the10 mm-wide SA12E
inner ring. The fork inner faces are16 mm apart, with3 mm inner-race
spacers each side; this leaves clearance for the outer head at8-degree yaw.
Steel fork ears are4 mm thick and finish at Z128, clearing the threaded
shank and jam nut through the pitch range. The actuator fore eye is at
X38,axial L; its rear eye at X38,axial3, giving147+s mm eye spacing.
The actuator bracket and guide carry different loads; its pin-ended rod
must not be used as the lateral guide.

Rear steering uses a metal guide arm ending at X-30 relative to the rod-end
eye, at the same Y/Z as that eye. The foot-mounted servo axis is at
X-30,Y-60,Z113 relative to the foot's eye datum. Its12 mm crank points
along negative X at neutral; the metal connecting link has61.188 mm
center spacing. Articulated link ends permit the small linkage misalignment.
The solver in firmware/include/posture.h maps an8-degree foot yaw command
to the required roughly20-degree servo motion. This requires gentle arcs,
not pivot turns. The vertical robot load bypasses the steering servo.

Ground-wheel centers are nominally X+/-26 relative to each foot and
Y+/-37; actual hub seating must be confirmed using the purchased wheels.
Leave the motor-shaft fit unchanged. Structural material below the wheel
tops stays in the center strip or the11 mm gap between the two axle rows.
The side stanchions pass outside the motor cases at that inter-axle gap.
Do not retain the old wide overhead foot deck if it intersects the newly
sloped toe shell. The upper bearing/servo fixtures clear the63 mm wheel tops.

Head bearing tower datum is Z415. Its26 mm bearing stack, approximately
1.5 mm shim and15 mm integrated dome stem place the dome at457.5 mm, within
0.1 mm of the609.6 mm nominal height target. The fixed neck ends2.5 mm
below the dome. The new dome integrates its support spokes and an underside
friction track at65-88 mm radius. The internal TT wheel contacts near X75;
its motor/plate must be vertically adjustable. A separate factory1A-limited
DRV8833 channel drives this head motor from its own5 V UBEC.

Firmware already implements held posture commands, local ADS1115 feedback,
INA219 current checks,750 ms no-progress shutdown,30 second travel timeout,
latched faults and4x off-time cooldown. Missing feedback blocks motion.
The initial detached actuator must be commissioned to approximately5 mm
before it is installed; a factory-retracted zero reading is not accepted
as a healthy in-range installed posture. These routines have host tests
and compile, but have not been uploaded to or tested on hardware.

Next integration: generate the selected metal drawings, add the real
mounting/clearance features to the detailed printable shells, update the
wiring/BOM, validate/export the final small STL inventory, regenerate the
manual, render the labelled CAD animation, and publish MP4/PDF via GitHub
OIDC to S3. This design-basis document alone is not the fabrication release.
