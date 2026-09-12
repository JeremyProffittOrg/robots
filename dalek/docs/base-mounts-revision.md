# MOUNT-1: base, motor fastening and battery bridge

This revision keeps the four Adafruit3777 TT motors, Adafruit3766 wheels,
300mm circular base and6mm base floor. The axle positions do not change.
The battery load goes directly into that floor and its surrounding ribs.
The printed electronics platform carries the boards, not the battery.

## Printed parts and hardware choices

`11_motor_clamp.stl` is one39.5×14×5mm design printed four times.
Each clamp uses one M3×16 screw, one M3 washer and one standard M3 nut.
This is four screws total for all four drive motors. The fifth, head motor
has its own adjustable drive mounting in the upper body.

The alternative drive-motor fastening uses two cable ties per motor. With
that option, omit all four printed clamps and their four screws/nuts/washers.
Use4.8mm ties at least250mm long, with a manufacturer stated loop tensile
rating of at least222N. Use genuine parts with a stated rating. The rating
of a cable tie is not a load rating for the printed robot.

`12_electronics_platform.stl` is one216×216×112mm connected print. It includes
the6mm deck, four legs, four feet, rim, braces and mounting slots. Print it
as exported, with its deck on the bed and legs up. Enable normal automatic
supports for the foot overhangs. Print the clamps as exported with automatic
supports under their raised bridge and toe. Use PETG, four walls and30%
infill for these two parts. Remove every support from a fastening slot.
The base retains six walls, six top/bottom layers and40% gyroid infill.
These settings are a prototype specification; load strength is not yet
measured. Use the current H2D slice report for actual material and time.

The platform feet use eight M3×12 screws, eight M3 washers and eight M3 nuts,
two sets per foot. The alternative uses eight4.8mm ties at least150mm long,
two per foot, with the same minimum222N stated rating. All eight foot ties
can be cut for service. Replace a cut tie; do not reuse it.

## Motor assembly

1. Remove supports and smooth the edges of all tie passages. Keep the motor
   disconnected. Check that the shaft turns and that no wire touches it.
2. For the screw option, insert one standard M3 nut into the side opening of
   each outer boss before fitting the motor. The pocket is at base X±88.5,
   Y±11, Z22..24.8. Seat the nut square. A small piece of removable tape can
   retain it during assembly. Keep tape outside the thread and bearing face.
3. Seat each motor in its cradle at X±70.5, Y±58, with the motor case bottom
   at base Z6. Put a2mm EPDM pad under the clamp bridge. Keep the pad off the
   motor vents, wire terminals, shaft and moving gearbox parts.
4. Point the clamp toe inward, toward the battery. Slide the toe into the
   reinforced inner rail window, then align the outer round ear with its boss.
   The nominal assembled clamp origin is [±70.5,±11,29]. Rotate the same
   printed clamp180degrees about Z on the left side of the base.
5. Fit the M3×16 screw and washer. Tighten by hand until the outer ear seats
   and the pad grips the case. The nominal1.56mm bridge-to-case gap compresses
   the2mm pad by about0.44mm. The actual case and pad control the fit. Stop
   if the case bends or the gearbox becomes stiff. Confirm two full exposed
   threads past the nut and no moving-part contact. Do not assign an
   untested torque value to the printed clamp.

For the tie option, omit the clamp and captive motor nut. Each motor has two
longitudinal strap routes. Use |X|62 and74 for the +Y rear motors, and |X|68
and80 for the −Y front motors. The stagger leaves at least1.2mm between
opposed4.8mm ties. Each route passes through the
base-floor slots at local Y−0.2 and72.2. Mirror the coordinates for the other
quadrants. These6.2×3.4mm slots put the tie ends beyond the motor case ends.
They avoid the small gap between the wheel and the motor. Put a1mm EPDM
strip beneath each tie on the case. Feed the tie through one floor slot,
under the floor, up through the other slot, and across the top of the motor.
Place each locking head at the inner motor end, in the central lead channel,
clear of the battery and platform foot. Tighten the two loops evenly. Do
not crush the case. Cut the tails flush and cover any sharp cut end. Check
that all four wheels rotate freely and each motor is held in its cradle.

## Battery fit and fastening

The clear cradle is104mm across X and157mm along Y. The three checked
envelopes are Bioenno BLF1206A70×114×76mm, Power-Sonic PS1270 7Ah
67 x153 x102mm, and Power-Sonic PS12140 14Ah100×153×103mm. The two SLA
envelopes include the selected products' dimension tolerance and terminal
height. These dimensions do not describe every battery sold as7Ah or14Ah.
Measure another product before using it. Use the battery specification and
electrical instructions for its terminals, fuse, connector and charger.

Put a2mm nonconductive pad on the base floor. Position the battery with its
long dimension along Y. Cut firm, nonconductive foam blocks to remove the
side/end gaps around the smaller Bioenno or7Ah battery. Do not put loose
metal spacers beside battery terminals. Keep the terminal edge and lead
exit away from the two strap lines at Y±25.

Use two4.8mm cable ties at least500mm long, with stated loop tensile rating
at least222N. Each loop uses the floor slots at X±51.5 and one of Y±25.
It passes under the floor and over the battery case. Cover the terminals
with correctly sized insulating boots. Route the ties over insulated case
surfaces; never over a terminal, connector or wire. Use a protective pad
where each tie turns over a case edge. Tighten both loops until the pack
cannot slide. The foam blocks locate the smaller packs; the ties hold them
down. Keep tie heads in the open end space, not beneath a platform leg.
Remove and replace both battery ties whenever the battery is removed.

The maximum checked battery top is base Z111. The full100×153mm footprint
is clear to the printed platform underside at Z140. This provides29mm
before PCB hardware is fitted. Limit all PCB washer, nut and screw-tip
projection to3mm below the deck. The populated platform then has at least
26mm nominal clearance above the terminal-height envelope. Braces point outward and the
underside beams lie outside that footprint. Confirm actual terminal boots
and flexible leads fit in the26mm space without a sharp bend or pressure from
the platform. Disconnect the pack before handling its connectors.

## Build the platform on the bench

The platform's assembled deck is Z140..146. Its legs sit on the base's
raised rail seats at Z36, with centres X±56.5, Y±48. End keys locate each
foot along its seat. Use6mm nonconductive spacers to put the PCB underside
at Z152. The drawing keeps the actual board envelope dimensions and shows
their new centre positions:

- Buffer prototype: X−38,Y−29;81×51mm.
- Divider prototype: X−38,Y29;81×51mm.
- PCA9685: X39,Y−44;62.5×25.4mm.
- Motor regulator: X24,Y−10;25.4×25.4mm.
- Servo regulator: X60,Y−10;25.4×25.4mm.
- Left DRV8833: X23,Y24;26×18mm.
- Right DRV8833: X59,Y24;26×18mm.
- Head DRV8833: X23,Y53;26×18mm.
- Amplifier: X59,Y49;19.4×17.8mm.
- Logic regulator: X81,Y32;10.16×17.145mm.

Use the real boards as drilling templates. The deck has3.2mm-wide slots on
a12mm grid. Use a slot where it matches a PCB hole. Drill a matching hole
where needed. Do not enlarge any PCB hole or cut an underside beam, leg or
rim. Use M2 screws for the two Pololu4091 regulator boards' three mounting
holes each; use M2.5 where the other board's real mounting holes allow it.
Start with20mm screws and trim to the measured6mm deck,6mm spacer, board,
washer and nut stack. For M2.5 use a thin nut no more than1.6mm thick,
one0.3mm underside washer, and one0.5mm head washer. A1.6mm PCB gives a
nominal16.9..17.1mm screw working length. For M2 use a thin nut no more
than1.6mm, one0.3mm underside washer and one0.3mm head washer; that same
PCB thickness gives a nominal16.6..16.9mm length. Actual board thickness
controls the cut length. Leave two full threads past each nut and keep
all underside hardware within3mm of the deck. Relocate a board or use its
tie option if the real mounting holes coincide with a beam or brace.
Deburr holes and remove all chips.

The alternative board fastening uses ties through adjacent deck slots and
over insulated, component-free board edges, on the same6mm nonconductive
spacers. Use two independent loops for each board. A tie must not load a
connector, component, solder joint or copper trace. Actual board routing
is a bench-fit requirement; the drawings show envelopes, not certified
connector or hole templates. Keep exposed metal off both PCB faces.

## Close the chassis and retain service access

1. Fit and retain the four M4 nuts in the underside base-flange pockets before
   the battery or motors prevent access. The small pocket nibs hold them
   during assembly; the6.7mm roof above the pocket takes the screw load.
   Verify a real M4 screw threads freely. If a nib prevents full nut seating,
   trim only the nib and retain the nut with removable tape. Never force a
   tilted nut or remove the pocket roof.
2. Lower each already mated motor/wheel unit into its cradle. The wheel wells
   pass through the upper flange to permit this path; the outside bumper is
   continuous. Retain the motors using either option. Fit, pad and tie down the selected
   battery. Keep the master switch off and the battery connector unplugged.
3. For platform screws, insert eight M3 nuts into the rail-seat side pockets.
   A temporary tape strip can hold them during handling. Lower the populated
   platform over the battery and onto all four rail seats. Fit two M3×12
   screws and washers per foot. Use a2.5mm L-hex key from the side of the
   base; the deck prevents a straight driver from above. The checked key
   envelope has an18mm exposed short leg and at least79mm side reach. Its
   horizontal shaft is at base Z61 and runs along Y, away from the adjacent
   leg. Keep its X coordinate at the screw's X±56.5. This approach clears
   the installed wheels. Check full seating and two full threads.
4. For platform ties, omit those screws and nuts. Pass each tie through its
   transverse rail tunnel, around the foot, and into the foot's top groove.
   Use the two routes at each foot's Y centre±8. Place locking heads on the
   outer side at Z35 or above, clear of the motor. Tighten evenly and confirm
   the feet cannot lift or move on the seats.
5. Check free wheel rotation. Secure leads to deck slots with service loops.
   Keep wire bundles within
   the216mm deck outline. Maintain the four cardinal driver corridors outside
   it. Before power is connected, confirm terminal boots, fuse and all ties
   are clear of motors, wheels and live board connections.
6. Lower the complete skirt around the assembled chassis. The264mm lower
   opening passes around the216mm platform. The platform does not pass
   through the184mm upper opening. Fit the four base-to-skirt M4 screws from
   above, using the existing250mm exposed3mm ball-end driver at16degrees
   inward. The captive nuts remove the need for an underside nut tool.
7. For service, remove the four base screws and lift the whole skirt away.
   Remove the platform screws or cut its eight ties, then lift the platform
   clear before removing the battery ties. Never pull on connected wiring.

The base retains its original6mm floor, circular bumper and integrated ribs.
The wider battery cradle, reinforced clamp rail roofs and platform seat
blocks are connected to those ribs. Those are geometric load paths, not
measured strength results. Use a slow first drive test on a level, smooth
floor. Check wheel slip, turning, motor/driver temperature, fastener creep
and emergency stopping with the selected battery. Lift the robot by its
base. Do not use the arms, dome or electronics platform as lifting handles.

## Verification

Run `python scripts/check_base_mounts.py` after exporting the current meshes.
The result is `cad/base-mounts-checks.json`. It covers connected solids,
motor cases, the four single-screw clamps and insertion paths, both tie
options, three battery envelopes,29mm printed/26mm populated terminal
headroom, the populated platform, mated motor/wheel insertion, side-key
access, skirt installation and the four long-driver corridors. These are
finite digital samples. Physical print tolerances, board connectors, tie
heads, adhesive pads, battery leads and strength still require inspection.

The current run passed301 checks with1,117,072 sample evaluations and an
unchanged-input check. The skirt-lowering check also uses a conservative
continuous bound from the actual skirt triangles' XY projections. The
upper-body, motion and H2D checks are recorded separately by the main guide.
