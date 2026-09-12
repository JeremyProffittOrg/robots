# FACET-1 mechanical design and assembly

The robot has a 300 mm circular reinforced base, four ground wheels, a one-piece skirt with twelve full-height flat faces, a combined shoulder and neck, concealed arm servos and an adjustable TT-wheel head drive. The package has ten STL designs. Print the pitch carrier twice and the hook clamp four times for fourteen printed pieces. The motor-tie option omits all four hook clamps and needs ten prints. Each delivered STL is one connected part. Nominal height remains 563.8 mm, below the requested 914.4 mm limit. The 213 mm skirt and 186 mm upper shell stay below the 320 mm maximum-minus-5 mm print height target.

The reference review covers 100 distinct photographs. Retained details include the dark circular fender, four hemisphere rows, raised bezels, skirt relief, shoulder slats and rivets, smaller rounded arm boxes, spherical roots, three neck rings, dark grille liner, eyestalk discs, ribbed lamps and decorative arm stems. See `appearance-research.md` and `reference-image-review.csv`.

This is a first-prototype design. No physical strength, payload, traction, runtime, bearing fit or finished robot operation has been measured. Match each generated validation and H2D report to the released FACET-1 mesh hashes. Complete the physical assembly, load and motion gates before operation.

## Print inventory

Use the released STL files at 100 percent scale with a 0.4 mm nozzle, 0.20 mm layers and the recorded single-nozzle H2D profile. Its single-nozzle envelope is 325 x 320 x 325 mm. The 300 mm base plus an 8 mm brim allowance occupies 316 x 316 mm. Other parts request 5 mm brims. Normal automatic supports must be inspected in the actual sliced job. Do not substitute an orientation or auto-arrangement without checking its full toolpath bounds. [Bambu H2D specification](https://cdn1.bambulab.com/documentation/h2d/en/H2D_Laser_Full_Combo_20250305.pdf).

1. `01_base.stl`: PETG, floor down. Six walls, six top/bottom layers, 40 percent gyroid. Diameter 300 mm, body 54 mm high plus 3 mm register, 6 mm floor and integral ribs. Clear supports from the wheel wells, clamp pockets, captive nuts and tie passages. The opened wheel wells admit fully seated motor/wheel units from above while the outside bumper stays continuous.
2. `02_skirt.stl`: PLA, large opening down. Four walls and 15 percent infill. Twelve flat panels taper in one straight line from 300 mm to 220 mm across opposite vertices over 210 mm. Across opposing flat faces, the body spans 300 x cos(15 degrees) = 289.78 mm at its lower end and 220 x cos(15 degrees) = 212.50 mm at its upper end. Round joint collars remain, with a maximum 300 mm outside diameter. The 3 mm top register makes a 213 mm print. Panel centers are at 15, 45 and subsequent 30-degree intervals. Each panel carries four domed details at local Z26, Z76, Z136 and Z186, with 23 mm bezels raised 1 mm from the face. Their axes follow the panel normal, tilted approximately 10.425 degrees upward from horizontal. The exterior middle band is removed. The integral internal faceted rib retains 240 mm clearance across opposing flats. The round bottom opening remains 264 mm and the main top opening 184 mm. Captive nut bosses project locally into that top opening, so do not use its nominal diameter alone to plan an insertion. Lift the whole skirt for battery/platform service. There is no bolted middle joint.
3. `04_shoulder.stl`: PETG, bottom flange down. Four walls and 25 percent infill. The shoulder and neck are one 186 mm print. Arm boxes, servo supports, open speaker mounting frame, display frame, grille, bearing tower, fixed head-drive deck and adjustment lug are integral. Clear every support through the open bottom before fitting hardware. Assemble its internal mechanisms on the bench before seating it on the skirt.
4. `06_head.stl`: PLA, drum rim down. Four walls and 15 percent infill. Friction drum, hub, spokes, dome, eye and lamps form one print. Remove supports through the drum and crown openings. Keep the inner drum track free of paint, glue and support scars.
5. `07_pitch_carrier.stl`: two PETG prints, floor down. Four walls and 30 percent infill. Each is 49.5 x 30 x 49 mm. Its Y bounds are -10 to +20 mm. Check the actual servo ears, shaft offset, ties and supplied horn before accepting fit.
6. `08_plunger_arm.stl`: PLA, as exported on the bed. Four walls and 15 percent infill. Spherical root, stem bands and cup are integral. Preserve the small servo-side stem clearance flat.
7. `09_emitter_arm.stl`: PLA, as exported on the bed. Four walls and 15 percent infill. Preserve the matching stem clearance flat. The eight rods and muzzle are decorative; there is no projectile mechanism.
8. `10_head_motor_carriage.stl`: PETG, floor down. Four walls and 30 percent infill. Retain its radial slots, motor saddle, tie routes and travel limits.
9. `11_motor_clamp.stl`: four PETG prints for the clamp option. Four walls and 30 percent infill. Print as exported with automatic supports under the bridge/toe. Omit all four for the drive-motor tie option.
10. `12_electronics_platform.stl`: PETG, deck down and legs up as exported. Four walls and 30 percent infill. The 216 mm deck, four legs and four feet are one 112 mm-high print. Clear supports and every foot fastening groove. No extra printed board spacers are required.

Identifiers 03 and 05 are retired. The four stacked body pieces are base, faceted skirt, combined upper shell and head. Use the current printed-parts manifest for all quantities and dimensions. Paint external surfaces only. Keep bearing seats, registers, sliding faces, horn seats, tie passages and the friction track clean. Use one bronze finish along each full-height skirt panel, silver stems and near-black bumper, liner, roots and cup.

The current FACET-1 skirt slice uses 1009.47 g of PLA including supports and brim, with a predicted print time of 23 hours 55 minutes 37 seconds. Its predicted installed plastic mass is 536.20 g after support removal. Have at least 1.12 kg available with a 10 percent reserve. The unchanged combined upper shell uses 1235.49 g of PETG and predicts 39 hours 10 minutes 11 seconds; allow at least 1.36 kg including reserve. Each job exceeds one 1 kg spool. Arrange compatible filament changes or sufficient spool capacity before starting. The full clamp-option package predicts 4180.82 g of filament, 2473.98 g of installed printed plastic and 124.28 hours of sequential printing. These are slicer estimates, not measured consumption or finished robot mass. Match every actual job to its released mesh hash.

## Coordinate map and body joints

All coordinates are millimetres. Positive Y is rear, positive X is right and world Z0 is the floor. Base-local Z0 is world Z13.8, derived from the 31.5 mm wheel radius, 6 mm floor and nominal 11.7 mm case-bottom-to-axle datum. Measure actual motor padding and axle height.

- Base origin: world Z13.8; base body top Z67.8.
- Faceted skirt origin: Z67.8; one straight taper to body top Z277.8; register top Z280.8. Its internal rib center is Z177.8; there is no exterior slope change there.
- Combined upper origin: Z277.8. Its neck datum is an internal coordinate reference at upper-local Z120, world Z397.8; it is not a separate joint.
- Lower bearing seat: upper-local Z160..167. Upper bearing seat: Z179..186.
- Head STL origin: world Z449.8, upper-local Z172. Hub foot is world Z464.8, dome rim Z488.8 and lamp tops approximately Z563.8.
- Ground-wheel axes: X +/-98, Y +/-58, world Z31.5. The fully seated hub accommodation range is abs(X) 95.5..100.5. Never leave a wheel partly seated to obtain clearance.
- Arm yaw origins: upper-local (-47,-94,42) and (53,-94,42). Pitch-axis offsets are (-3,0,35). Neutral spherical centers are world (-50,-94,354.8) and (50,-94,354.8).
- Head carriage origin at nominal contact: upper-local (64.5,0,149.2). Head-wheel center: (64.5,0,191).
- Platform deck: base-local Z140..146; PCB undersides Z152; platform feet sit at Z36. Invert the exported platform with a 180-degree X rotation, then translate by base-local Z146.
- Battery bottom: base-local Z8 including the 2 mm pad. Maximum terminal envelope top: Z111. Keep attached contacts and leads below Z130.

There are two bolted body joints and eight M4x20 screws total. The base/skirt holes are at radius 137 mm. The skirt/upper holes are at radius 97 mm. Each set has four holes at 0, 90, 180 and 270 degrees. Use eight standard M4 hex nuts: four in the base's captive pockets and four below the skirt's upper flange. Use one washer under each screwhead, eight washers total. Do not put washers inside either set of nut pockets. Align the front relief and fully seat each register before tightening. The register locates the joint; screws retain it.

Before lowering the skirt around the chassis, turn it on a padded bench support and seat its four upper-joint nuts from below. Their reinforced supports are at skirt-local radius 97 mm, Z199..210. Seat each nut square and test it with a real M4 screw. Small insertion nibs retain the nut during handling; the pocket roof carries the screw load. Trim only a nib that prevents full seating. Do not remove the roof, widen the pocket or force a tilted nut. Use removable tape only to retain a seated nut during handling, with tape clear of the thread and bearing face. Leave the head off and keep the carriage retracted while fastening the merged upper shell through its specified driver routes.

Use a 250 mm exposed-shaft 3 mm ball-end driver rated for at least 20 degrees at the base/skirt joint. Its route tilts 16 degrees inward toward the center and clears the 184 mm upper opening. Keep bulky couplers out of the route. Captive base nuts remove the former deep underside nut-tool operation. A documented driver option is [Stahlwille 10507N KK, article 73103003](https://stahlwille.com/de_de/products/detail/879352), with a 300 mm blade and listed 25-degree swivel angle. Dry-fit the actual tool before closing the shell.

## Purchased part checks

The five [Adafruit 3777 TT motors](https://www.adafruit.com/product/3777) and five [3766 wheels](https://www.adafruit.com/product/3766) retain their original duties: four ground pairs and one head-drive pair. The wheel is nominally 63 mm diameter and 29 mm wide. The [motor drawing](https://cdn-shop.adafruit.com/product-files/3777/3777_diagram.jpg) gives a 22.44 mm case height, 70 mm length, 22.4 mm metal-end width and 36.6 mm across shaft ends. Measure actual cases, seated hubs, both shafts, leads and loaded tire deformation.

The original TTGO T-Display PCB is nominally 51.52 x 25.04 mm. Insert it from inside its 52.2 x 26 mm recess behind the rear lip. Keep the display, buttons, antenna and USB clear. Use the confirmed original 1.14-inch ESP32 board. [Original board files](https://github.com/Xinyuan-LilyGO/TTGO-T-Display).

The Adafruit 1313 speaker is 77.8 x 77.8 x 25.49 mm with 60 mm mounting centers. Its rear open mounting frame is at upper-local Y52.5..56.5, with four holes at X +/-30, Z13 and Z73. The speaker envelope extends from Y56.5 to Y81.99, centered at Y69.245/Z43. Its rear edge clears the display frame at Y95. Install the speaker after the arm insertion paths are complete. Use four M3x12 screws, washers and nuts. Retain the rear board with four padded 20 x 8 x 1 mm tabs and M3x25 screws, washers and nuts. Pads touch bare PCB edges only. [Speaker drawing](https://cdn-shop.adafruit.com/product-files/1313/C2464-001_datasheet.pdf).

## Base, motor fastening and battery platform

This revision keeps the four Adafruit3777 TT motors, Adafruit3766 wheels,
300mm circular base and6mm base floor. The axle positions do not change.
The battery load goes directly into that floor and its surrounding ribs.
The printed electronics platform carries the boards, not the battery.

### Printed parts and hardware choices

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

### Motor assembly

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

### Battery fit and fastening

The clear cradle is104mm across X and157mm along Y. The three checked
envelopes are Bioenno BLF1206A70×114×76mm, Power-Sonic PS1270 7Ah
67×153×102mm, and Power-Sonic PS12140 14Ah100×153×103mm. The two SLA
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

### Build the platform on the bench

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

### Close the chassis and retain service access

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
6. Pre-seat the four standard M4 upper-joint nuts in the skirt's underside
   pockets as described in the body-joint section. Then lower the complete
   skirt around the assembled chassis. The264mm lower
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

### Verification

Run `python scripts/check_base_mounts.py` after exporting the current meshes.
The result is `cad/base-mounts-checks.json`. It covers connected solids,
motor cases, the four single-screw clamps and insertion paths, both tie
options, three battery envelopes,29mm printed/26mm populated terminal
headroom, the populated platform, mated motor/wheel insertion, side-key
access, skirt installation and the four long-driver corridors. These are
finite digital samples. Physical print tolerances, board connectors, tie
heads, adhesive pads, battery leads and strength still require inspection.

## Battery wiring, charging and discharge handling

The specified battery-tie example is [KSS CV-500W](https://www.kss.com.tw/index_en.php?action=products4&cid=17&fid=3&id=8461&sid=14): 500 mm long, 4.8 mm wide and minimum 222 N stated loop strength. The mounting samples use a ribbon no more than 1.2 mm thick. Ribbon thickness and latch size are not published for that example, so measure the actual tie and verify its complete route before use. A width or strength rating alone does not prove fit. The current slots do not accept a 7.6 mm-wide tie without a separate CAD change.

Only one battery is installed and connected at a time. The default Bioenno BLF-1206A is 12 V, 6 Ah, 72 Wh and approximately 0.7 kg. Preserve its protection circuit and factory PP30 discharge connector. Use its BPC-1502DC 14.6 V, 2 A LiFePO4 charger. [Bioenno pack and charger](https://www.bioennopower.com/products/12v-6ah-lifepo4-battery-pvc).

The specific SLA alternatives are Power-Sonic PS-1270 F2 7 Ah and PS-12140 F2 14 Ah. The maximum combined fit envelope is 100 X x 153 Y x 103 Z mm, including terminal blades and dimensional tolerance but excluding attached connectors. It does not cover every battery sold as 7 Ah or 14 Ah. The current PS-1270 sheet gives about 1.97 kg; PS-12140 gives 3.78 kg, with an older official version at 4.2 kg. Record the actual pack's dimensions and mass. These are heavier fit and electrical options whose loaded drive performance remains unproved. [PS-1270 sheet](https://www.power-sonic.com/wp-content/uploads/datasheets/ps-1270.pdf), [PS-12140 sheet](https://www.power-sonic.com/wp-content/uploads/datasheets/ps-12140.pdf).

Make one labelled SLA adapter from its matching terminals to the existing PP30 input. F2 uses a 6.35 x 0.8 mm blade; F1 uses 4.75 x 0.8 mm. Use matching insulated female contacts rated at least 10 A DC with the specified 18 AWG copper wire. Insulate each terminal separately and measure PP30 polarity before connection. Keep the single 7.5 A main fuse F1 within 100 mm of the SLA positive terminal, including all adapter and unfused lead length. For Bioenno, keep it within 100 mm of the intact factory PP30. Preserve the existing 3 A motor, 3 A servo and 1 A logic branch fuses. Do not increase motor voltage or current limits for a heavier battery. Use the five circuit sheets and wire schedule for exact connections.

Keep all battery contacts, boots and bent leads below base-local Z130. This leaves at least 10 mm below the printed deck and at least 7 mm below the permitted 3 mm PCB hardware projection. The larger battery's 29 mm bare-deck allowance is reduced to 26 mm by that hardware; it is not a verified fit for every connector. Keep ventilation open and both battery ties away from terminals. The battery always rests on the base, not on a platform leg or PCB.

Switch MAIN off, unplug and remove the battery before charging. Use the Power-Sonic PSC-121000ACX 12 V SLA charger for either selected SLA pack; PSC-12500ACX is also specified for PS-1270. Keep SLA and LiFePO4 chargers clearly labelled and separate. Follow the exact charger instructions and polarity. No onboard charging is provided. Never connect a 12 V pack to the T-Display battery socket. [PSC-121000ACX](https://www.power-sonic.com/product/psc-121000acx/?preview=true), [PSC-12500ACX](https://www.power-sonic.com/product/psc-12500acx/?preview=true).

Firmware stops motion at 11.2 V and permits explicit re-arm at 12.0 V, but the controller and audio supply remain powered. An SLA battery has no Bioenno-style internal protection. After a low-battery stop, switch MAIN off and unplug the battery. Store it unplugged and recharge SLA after use. AGM sealed lead-acid batteries are not gas-tight; do not operate or charge them in an airtight enclosure. [Power-Sonic technical manual](https://cdn.power-sonic.com/documents/SLA_Technical_Manual.pdf). Full sources and electrical calculations are in `battery-options-research.md`.

## Combined upper shell and concealed arm mounts

The shoulder and neck are one 186 mm PETG print, `04_shoulder.stl`. The former `05_neck.stl` is removed. The head, spindle, two bearings, friction drum and the separate adjustable `10_head_motor_carriage.stl` keep their existing locations. The upper shell remains removable at the skirt joint. This removes the shoulder-to-neck joint and its four M4 screws, four M4 nuts and eight washers. It does not increase overall height.

Each rounded arm box is now 90 x 52 x 103 mm, down from 94 x 58 x 106 mm. Width decreases 4.3 percent, depth 10.3 percent and height 2.8 percent. The nominal box envelope decreases 16.6 percent; that is not a measured reduction in plastic or print time. The box front moves from shoulder-local Y-115 to Y-113. Its socket centers stay X-50/+50, Y-94, Z77. The original 8-degree yaw and pitch limits stay unchanged. Do not reduce these boxes further without checking the carrier sweep, painted spherical roots and actual servos.

The fixed neck liner now has a 99.1 mm inside radius and a 100.3 mm outside radius. This leaves a nominal 1.1 mm gap around the existing 98 mm-radius carriage foot at its X64.5 contact position. The liner still ends at shoulder-local Z171. The rotating drum still starts at Z172. No new opening exposes the arm servos. The neck grille, three horizontal rings, bearing support, radial deck, jackscrew lug and travel stop are integral with the shoulder.

### Servo dimensions and acceptance gates

[Tower Pro's MG92B table](https://towerpro.com.tw/product/mg92b/) and its [dimension diagram](https://towerpro.com.tw/wp-content/uploads/2014/07/%E5%B0%8F%E9%A6%AC%E9%81%94%E5%B0%BA%E5%AF%B8%E6%A8%99%E7%A4%BA%E5%9C%96B.jpg) give A35, B22.6, C31, D12, E31.5 and F22.8 mm. The diagram identifies A as base-to-shaft height, B as case length, D as width, E as the complete ear span and F as base-to-ear underside. These do not specify the mounting-hole centers, shaft offset along the case or ear thickness. [Adafruit 2307](https://www.adafruit.com/product/2307) also gives an overall envelope of 36 x 12 x 31 mm. These descriptions are not interchangeable detailed drawings.

The CAD preserves the existing shaft axes. It uses a nominal 5 mm offset between case center and shaft along the case length. This offset and the nominal 2 mm ear thickness must be checked against the actual four servos. Do not assume that the simplified drawing measures these dimensions. Use the real servo, horn and screws before accepting a printed fit. Align the shaft first, then check the case, ear holes, output boss and wire exit. A supplied horn and its center screw remain mandatory for every servo.

Yaw support is shoulder-local Z7. The target shaft/horn datum stays Z42. Relative to each yaw axis, the nominal case occupies X-16.3..6.3, Y-6..6 and Z7..38. The clearance pocket is X-17.3..7.3 and Y-6.5..6.5. Ear support tops are Z29.8. The two nominal ear regions are X-20.75..-16.3 and X6.3..10.75, Y-6..6, Z29.8..31.8. Pads must not move the required shaft datum. Reject an interference or a loose case that cannot be padded while retaining the shaft location.

The pitch carrier is now 49.5 x 30 x 49 mm. Its back wall starts at X32.5, leaving 0.5 mm behind the nominal servo-back plane X32. The pitch shaft remains at carrier-local (-3,0,35). The nominal case is X1..32, Y-6..6 and Z18.7..41.3. Its ear underside is X9.2. The two ear regions lie at Z14.25..18.7 and Z41.3..45.75. Again, measure the real offset and ear geometry before accepting this fit.

Both arm stems now have a small flat on the side nearest the servo. The flat is 8 mm long and blends back to the full round stem by 14 mm. In the printed part, it leaves a nominal 9.5 mm thickness and 12 mm width before the existing horn holes are subtracted. This removes the collision between the actual case-front envelope and the former round stem without moving a shaft or socket. Use the revised arm STLs with the revised holders. The checker samples 47 cross sections between 0.25 and 11.75 mm from the root. Its minimum sampled net area is about 73.4 square millimetres, including the existing horn holes. This is a geometric measurement, not an arm-load rating.

### Option A: retain the servos with screws

Use two M2x10 socket-head screws per servo: eight screws for all four servos. Use DIN 912 / ISO 4762 heads with a 1.5 mm hex socket, no more than 3.8 mm diameter and 2 mm height. Add eight M2 hex nuts no more than 1.6 mm thick and sixteen M2 washers no more than 0.3 mm thick. Use washers no more than 5 mm outside diameter. These are additional servo-ear fasteners. Keep all existing horn-to-print screws and all four supplied horn-center screws.

The yaw supports have 2.2 mm-wide slots along X, centered at X-20 and X10, Y0 relative to the yaw axis. Their straight slot length is 3 mm, plus the rounded ends. The pitch supports have 2.2 mm-wide slots along Z, centered at Z15 and Z45, Y0; their straight slot length is 2 mm. The pitch screws point along positive X, from the servo ear toward the printed carrier. Fit actual holes within these slots while keeping the shaft in its fixed position. Do not enlarge the servo ears or force a screw through an offset hole.

Fit the yaw servo screws before installing a carrier. Introduce a short L-key through the open bottom, then approach each screw from the rear inside the gunbox. A straight driver from above is blocked by the roof. [Wiha 01121](https://www2.wiha.com/files/asia-pacific/EN-Asia-Pacific_catalogue.pdf) is the checked nominal key: 1.5 mm hex, 46 mm long leg and 15 mm short leg. Keep the long leg pointing rearward. Start with the elbow at the screw X, Y-34 and Z-20; raise it to Z51. Move forward to Y-94, then lower the elbow to Z48 so the short end enters the socket. Turn in 60-degree arcs, lift, re-index and repeat. Keep the carrier, horn and arm out during this operation.

Each ear ledge has a rear nut-tool window. Hold the nut with a fine gripping tool whose working tip, while gripping a 4 mm-across-flats nut, stays within 6 mm width and 2.4 mm thickness for the first 24 mm of reach. The tool must fit the actual printed window and clear the servo case. These are acceptance bounds, not a claim that every pair of needle-nose pliers fits. The nominal tip center is at the nut X, Y-94 and Z24.5. Introduce it through the bottom with its front at Y-34; raise the center to Z24.5, then advance it through the rear window to the nut. Keep the tool steady while the L-key turns the screw. Check actual jaws and handles on the bare shell before choosing the screw option.

Fit each pitch servo and its two screws to its carrier on the bench before inserting the carrier. The printed ledge is 4 mm thick. With a nominal 2 mm ear, two 0.3 mm washers and a 1.6 mm nut, an M2x10 screw leaves about 1.8 mm beyond the nut. Measure the actual stack. Require at least two complete exposed threads and no contact between the screw, nut, servo case, horn or moving arm. Trim and deburr a screw only when the actual stack requires it.

Tighten only until the ear is seated on the ledge. The printed pocket and pads locate the case. The screws retain the ears. Do not bend an ear to make the body touch its support. Check all fasteners through the complete 8-degree motion range before power is applied.

### Option B: retain the servos with cable ties

Use two independent 2.5 mm-wide nylon cable ties per servo: eight ties total. These replace the servo-ear screws only. They do not replace the supplied horn-center screws or the fasteners that connect an arm or carrier to a horn. Use thin nonconductive pads where a tie touches the metal case. Keep tie heads and trimmed ends inward, away from the socket liner, moving horn and leads.

Each yaw pocket has two loops through its floor. The slot pairs are at X-11 and X3, with each pair at Y-10 and Y10 relative to the yaw shaft. Each loop goes under the printed floor, rises at the front and rear of the case and crosses the case top. Keep the loop below the horn and clear of the shaft. The slots accept a 2.5 mm ribbon; choose a tie whose actual thickness and latch fit the open route.

The yaw loops return through enclosed channels at shoulder-local Z2..4. Clear these channels with a blunt tie before installing a servo. The return stays above the skirt mating face. Do not route a tie below the shoulder flange, where it would stop the joint from seating.

Each pitch carrier has two loop positions at Z24 and Z36. The slots pass through its back wall at Y-7 and Y13. Wrap each loop around the fixed servo case and back wall. Keep the tie away from the shaft at (-3,0,35). Fit the ties before inserting the carrier. Tighten evenly without crushing a case or moving the shaft datum. The modeled loops establish nominal access; the actual tie head, bend radius and pad thickness need a hand fit.

### Assemble the merged upper shell through its bottom

Keep the upper shell off the skirt and leave the speaker, rear board, arm carriers, head carriage and head off during this sequence. Support the shell on a padded stand that leaves its full lower opening and both front sockets accessible. Do not rest it on the display lip, neck grille or lamp parts. Remove every internal print support before fitting any hardware.

1. Clean both bearing seats. From below, insert the lower 608 bearing into shoulder-local Z160..167. Insert the upper bearing from above into Z179..186. Use the existing 12 mm metal inner-race spacer, narrow shims and six outer-race retainers. A straight lower driver approaches each of the three lower retainer positions through the open bottom. Fit the M8 spindle from below. Keep the assembly free to rotate. The lower bearing cannot be serviced with the upper shell seated on the skirt.

2. Center the four servos electrically. Introduce each yaw servo through the lower opening at its final X, with its center Y0. Raise its case base to Z45, move forward to Y-94, then lower its base to Z7 into the pocket. Retain it using Option A or B. Leave the carriers out. Fit and check the yaw horns at their existing neutral datums after the retaining tools are removed. Keep wires loose but clear of the next insertion paths.

3. Feed each detached arm through the lower opening. All following coordinates are shoulder-local. Keep its root X at -50 or +50. Start with root Y10, the stem pointing vertically down and root Z-35. Raise the root to Z45, move rearward to Y25, then raise it to Z110 with the arm still vertical. Turn the stem toward the front until it points 13.5 degrees down from horizontal, keeping the root at Y25/Z110. Raise the root to Z110.611, then move it from Y25 to Y-20 while keeping Z = 77 + (Y + 115) x tan(13.5 degrees). At Y-20, reduce the angle from 13.5 to zero and keep Z = 77 + 95 x tan(angle). Finally, move the horizontal root from Y-20 to Y-94 at Z77. The stem and decorative tip pass outward through the front socket; the spherical root stays inside. The 40 mm plunger cup is still the limiting tip. Use a caliper on the finished cup and never force it through a painted socket.

4. Support both exposed stems on padded blocks, keeping their roots at (-50,-94,77) and (50,-94,77). Assemble each pitch servo on its carrier outside the shell. Fit the screws or ties now. Keep the arm supported while its carrier enters from below through the rear portion of the opening.

5. For both carriers, start at origin X-29/Y25 in the left part of the lower opening. The right part is blocked above by the integrated head-deck support. Raise each carrier floor from Z-55 to Z88. Move forward from Y25 to Y-44 at Z88. Lower the floor to Z46, then move X to its final value of -47 or +53. Move forward to Y-94 and lower to Z42 onto the centered yaw horn. Fit the horn-center screw and existing two horn-to-carrier M2 fasteners. This is a lower-entry path. The old straight approach through a detached neck joint does not apply.

6. Attach each supported arm to its pitch horn with its existing two M2 fasteners and supplied center screw. Remove a stem support only after the horn retains the arm. Fit the opaque stretch-fabric socket liners with loose folds. The nominal visibility model uses a 30 mm fixed outer radius at Y-111 and a 24 mm moving inner radius. The former 33 mm outer radius would extend above the smaller gunbox. Bond the real fabric to the available inner curved surfaces around the aperture, with continuous overlap. Keep it inside the box's top edge. Keep both moving and fixed attachment edges secure. Inspect front, side and lower views through all four yaw/pitch extremes. A servo, tie, horn or lead must not be visible through either finished socket.

7. Fit the rear speaker, acoustic cloth, rear T-Display and switches after the arm routes are clear. The speaker frame is now at Y52.5..56.5, with unchanged mounting X-30/+30 and Z13/73. It has two 8 mm uprights, a bottom beam and two integral struts to the shell. The speaker faces the existing front grille. Its nominal body is X-38.9..38.9, Y56.5..81.99 and Z4.1..81.9. Keep its terminals insulated and route its leads upward. This leaves nominal 13.01 mm before the rear display recess at Y95; inspect the actual tabs, connectors and wires. The frame was moved rearward to leave an open arm-insertion route. Keep a labelled disconnect and a service loop for each harness. Run the arm motion checks on the bench before placing the upper shell on the skirt.

### Fit and adjust the head drive

The fifth TT motor, existing radial carriage and 63 mm wheel stay a separate serviceable assembly. The printed fixed deck and adjustment lug are now part of the merged upper shell. Keep the original 3.6 mm slide range, the jackscrew, all four M3 slide clamps and the hard stop. Combining the fixed supports does not remove friction adjustment.

Fit the motor, pads, ties and fully seated wheel to the carriage on the bench. With the head off, lower that assembly vertically at shoulder-local carriage origin X64.5/Y0/Z149.2. The nominal head-wheel center is X64.5/Y0/Z191. The revised liner lets the complete assembly pass from above. Install the four M3x16 slide screws and washers from above, and their underside washers and nuts through the open lower shell. Fit the jackscrew nut and screw while access remains open.

Retract the carriage to X61.5 before seating the upper shell on the skirt. The skirt's four new captured M4 nuts retain the upper joint and resist tightening torque. Seat them before placing the upper shell. The captured pockets replace the need to hold loose nuts inside the closed joint. Use the specified four M4x20 screws and washers, and check that the tongue seats fully.

Keep the dome off while tightening these four screws. Use the specified 250 mm bare-shaft, ball-end 3 mm driver, rated for at least a 20-degree angle. The sampled shaft has a 1.74 mm corner radius. Its ball enters each screw socket near upper-local Z9.2. At the front and left screws, lean the shaft 16 degrees toward the center. At the rear screw, lean it only 6.5 degrees toward the front. That route passes between the speaker and the rear display frame. At the right screw, lean the shaft 16 degrees toward the rear-left diagonal: equal negative-X and positive-Y motion as the shaft rises. This route passes behind the fixed deck and clears the retracted head wheel. Keep the handle and all large bit holders above the clear top opening. Check the real tool, final wiring and actual hardware before tightening; do not force a shaft against a board, wheel or printed edge.

Then follow the original bearing, spindle and crown-retention procedure. The head STL origin remains shoulder-local Z172. Adjust contact through the existing left service port with the head in place. Nominal contact remains X64.5, with a hard outer limit of X65.1. This is a geometric position, not a force setting. Lock all four carriage screws using the original short L-key routes. Check full hand rotation before powered tests.

When servicing an arm, lower bearing or underside slide nut, remove the complete upper shell from the skirt and unplug its labelled harnesses. Isolate battery power first. The former neck joint is no longer a service opening.

### Verification scope

`scripts/check_arm_assembly.py` checks the new carrier entry path against the printed upper shell and both supported arms. `scripts/check_upper_mounts.py` checks the new ear supports, optional screw stacks and tie routes, yaw-servo entry, screw and nut tools, detached-arm lower entry, complete head-drive top entry, lower-bearing tools, speaker clearance and four upper-joint driver routes. `scripts/check_mechanical.py` checks the unchanged 8-degree mechanism range against the new upper geometry. The generated reports identify the exact STL hashes used.

The common query helper compares two independent near-axis ray results and sends disagreements to the original `trimesh.contains` query. `python scripts/mesh_queries.py` compares the method against the original on 4,400 deterministic inside, outside and surface-adjacent points. It does not change geometric tolerances or permit collisions.

These are finite digital samples. They do not prove print strength, real servo dimensions, cable flexibility, fabric folds, tire grip or physical assembly. Use the stated fit gates, then complete the bench motion, retention and stop tests on the actual robot.

## Detailed bearing and friction-drive hardware

Fit the bearing stack while the merged upper shell is off the skirt. The lower 608 bearing is at upper-local Z160..167 and the upper bearing at Z179..186. Use the 12 mm-long metal spacer with 8.1 mm bore and 12 mm outside diameter between the inner races. Add the two narrow 8 x 12 x 1 mm shims, one below and one above. Six M3x8 plastic thread-forming screws and 9 mm washers retain only the outer races, three per end. Fit the lower retainers through the open bottom. Insert the M8x70 spindle from below without forcing either 8 mm bore. Bearings must rotate freely before continuing.

The following head-drive coordinates use the internal neck datum at upper-local Z120. Add 120 mm for upper-local coordinates, or 397.8 mm for world Z. The datum names geometry within the combined print. Fit the complete head carriage and all underside slide nuts before seating the upper shell. The head load passes through the spindle and bearings; the tire supplies tangential drive only.

1. Fit the fifth TT motor on its side in the head carriage. Its axle is vertical; the metal tail points toward negative Y. Use measured thin pads and two ties through the saddle. The nominal motor transform from the original drawing frame (x,y,z) is neck-local (64.5+z-11.7,y,43.5+x). The metal-end bottom is Z32.3 and the carriage floor top is 32.2. Support the narrower gearbox with measured padding rather than forcing it down. The unused lower shaft has a 15 mm-wide radial clearance slot through both carriage and fixed deck.
2. Fit its wheel fully. Nominal wheel center is neck-local (64.5,0,71). Measure actual seating; use appropriate case-height shims to keep the 29 mm tire within Z56.5-85.5 and clear of the head spokes at Z91. Both shaft ends and the hub must remain free. Keep motor wires fixed below the rotating drum.
3. Install the carriage on the fixed deck using four M3x16 screws. Fixed screw axes are (43,-50),(43,8),(83.5,-40),(83.5,8). Use 6 mm-OD, 1 mm-thick washers above the carriage and standard washers and M3 nyloc nuts below the deck. The small top washer diameter is required for the full slide travel. Leave the screws just loose enough to slide; retain all nuts. The deck is Z25.2-29.2; carriage floor is 29.2-32.2.
4. Insert one M3 nut into the open-top adjustment-lug pocket. Fit the M3x25 jackscrew along positive X through Y-35, Z38. The screw tip bears on the carriage pad. Start with carriage X61.5, nominally 3 mm clear of the inside track. Radial slots permit movement to X65.1; the fixed stop at X90.1 limits the outward plate edge. Do not enlarge slots or bypass that stop to cure a binding head.
5. Lower the head over the spindle with the tire released. The drum is 192 mm inside diameter and 198 mm outside diameter. Its bottom is neck-local Z52 and the spokes start at Z91. Fit the M8 washer above the printed hub and the nyloc nut using a 13 mm socket no more than 23 mm outside diameter through the 24 mm crown hole. Set retention while keeping free bearing rotation. Do not tighten until the head binds.
6. Turn the dome by hand through two complete revolutions while the tire remains released. Check drum roundness, axial runout, crown retention, eye sweep and clearance from the stationary liner. The liner ends at Z51, giving nominal 1 mm clearance below the rotating drum.
7. With power off and the head seated, reach the jackscrew from the left through its service port at Y-40..-30,Z34.5..41.5. Advance it only until the tire makes light, reliable contact. Nominal geometric contact is X64.5. The final 0.6 mm travel is a geometric allowance, not a measured force setting or a required amount of compression. Excess pressure loads the motor shaft and head bearings.
8. Hold the adjustment while tightening all four slide clamps against their M3 nyloc nuts. These clamps lock the setting; there is no separate jackscrew jam nut. The clamp screws remain accessible with a 2.5 mm L-key whose short leg is 15 mm. Its horizontal shaft runs near neck-local Z49.9 through the 3.8 mm-high ports; the short leg reaches the screw socket near Z34.9. Approach the two negative-Y screws from the front and the two positive-Y screws from the rear at their specified X coordinates. Use a correctly sized tool; do not pry open a printed port.
9. Recheck two full hand turns after locking. Start powered tests at low duty in each direction. Increase contact only enough to avoid unwanted slip, then lock and repeat. Do not increase pressure to overcome an eccentric drum, tight spindle nut or snagged liner. Recheck after the motor and PETG mount warm during the short commissioning run.

The head controller commands speed and direction; it has no measured angle feedback. The rolling ratio is approximately 96/31.5=3.05 motor-wheel turns per head turn when there is no slip. Actual slip, speed and stopping distance must be measured. The eye and dome lights are decorative and contain no moving wires, so no slip ring is required.

## Physical acceptance and service

- Before motor installation, support all four motor-floor regions on equal rigid blocks. Apply twice the intended complete robot mass across the battery and stack load points for ten minutes, close to the floor. Unload and inspect for cracks or permanent distortion. This is a proposed proof test, not a verified rating.
- Verify fully seated wheels and free rotation unloaded and under the intended mass. Check clamp, tie, platform-foot, bumper and ground clearances with actual tire deformation.
- Weigh the complete robot. Four wide tires resist tight turns. Start on a level hard floor with slow starts and broad moving arcs. Measure current and temperatures. Do not assume these small TT motors can pivot in place, climb thresholds or run on carpet because the base is reinforced.
- Run twenty arm circles while inspecting every socket from low, side and frontal angles. The fabric must remain opaque, loose and clear of moving hardware at all permitted poses.
- Run a full head turn in each direction, check runout and repeat all contact/lock checks warm. A slipping drive is preferable to forcing a bound bearing with excessive pressure.
- Complete the electrical stop, Wi-Fi-loss, power-switch and simultaneous-load tests in `assembly.md`. The physical actuator switch must remain reachable.

## Service and regeneration

Isolate battery power and unplug labelled harnesses before removing body screws. Remove the complete upper shell from the skirt to service an arm, lower bearing or underside slide nut. Support it on a padded stand with its lower opening free. Remove the speaker and rear display before reversing an arm insertion path. Back off head contact before removing the crown nut with a 13 mm socket no more than 23 mm outside diameter; lift the dome by its rim, never the eye or lamps.

Lift the complete skirt off the base for battery or platform service. Disconnect the platform harnesses, remove its eight screws or cut its eight foot ties, and lift it clear before cutting the two battery ties. Replace every cut tie. Refit foam blocks, terminal boots and service loops, then repeat retention and motion checks. Do not lift the robot by its arms, dome or electronics platform.

Regenerate meshes with `python scripts/export_cad.py --jobs 3`, then run `python scripts/export_cad.py --check-only`. Run the current mount, arm-assembly, mechanical and H2D checks after any geometry change. Use `python scripts/render_drawings.py` to refresh the PDF illustrations from those final meshes. Never treat a report for earlier hashes as verification of a new part.
