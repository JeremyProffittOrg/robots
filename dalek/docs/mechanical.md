# DALEK-541 mechanical design and assembly

This is a complete printable prototype design. It uses four specified Adafruit TT motors and four specified wheels. It is 541 mm (21.3 in) tall. The bumper is 360 mm in diameter. The eye and arms extend beyond the body. The rear panel exposes the original TTGO T-Display screen, its buttons, and a USB-C cable opening. Two independently controlled joints on each arm trace small circles. A separate bearing-supported head turns continuously. No wire enters the rotating head.

The supplied CAD and STLs are real solids, not a visual concept. Physical fit, traction, print strength, and endurance still require the listed bench tests. No robot has been printed or driven during this design run. Do not treat a passed mesh check as a hardware test.

## Files and verified limits

- `cad/dalek.scad`: editable parametric source; millimetres. Set `part="assembly"`, `part="section"`, or `part="exploded"` to inspect it.
- `stl/`: 35 distinct meshes. `bom/printed-parts.csv` specifies 151 printed pieces including 32 small PCB spacers and one fit coupon.
- `cad/assembly.png`, `cad/rear.png`, `cad/section.png`, `cad/exploded.png`: rendered CAD views. Purchased parts shown as simple blocks are envelope references.
- `cad/validation.json`: all 35 meshes pass watertight, consistent winding, positive-volume, one connected positive solid, and 300 x 300 x 300 mm checks. Negative internal cavity surfaces in the arms and eye are allowed. They are sealed air cavities, not loose parts.
- The combined solid material bound is 1988.1 g for every BOM quantity, including the fit coupon and spare spacers. This is geometry multiplied by 1.24 g/cm3 PLA or 1.27 g/cm3 PETG. It is not a measured print mass. The installed print mass will depend on the slicer. Supports and waste are excluded from this number.
- The design targets a loaded mass at or below 3.0 kg. The 0.7 kg battery, purchased electronics, motors, wheels, bearings, and metal fasteners must be added to the actual sliced print mass. Weigh the finished machine. The solid bound alone does not prove the loaded target. Do not add ballast.

Official H2D specifications give 325 x 320 x 325 mm for one nozzle and 300 x 320 x 325 mm for dual-nozzle printing. Every exported part is smaller than 300 mm on every axis. Leave room for a brim and do not fill the bed edge with support towers. [Bambu Lab H2D specification sheet](https://cdn1.bambulab.com/documentation/h2d/en/H2D_Laser_Full_Combo_20250305.pdf).

## Researched component interfaces

Adafruit 3777 is a 3–6 V TT gearmotor. Its nominal body is 70 x 22 x 18 mm. The manufacturer drawing shows a 22.44 mm body height, 18.60 mm gearbox thickness and 36.60 mm overall span across the two axle ends. The output axle is near one end of the body. It must remain free on both sides. The cradle uses padded body retention and two cable ties; it does not depend on uncertain case screw holes. [Product](https://www.adafruit.com/product/3777), [dimension drawing](https://cdn-shop.adafruit.com/product-files/3777/3777_diagram.jpg).

Adafruit 3766 is a press-fit TT wheel with a 63 x 29 mm envelope. Each weighs 38 g. It was listed out of stock when researched. Keep this wheel selection; another diameter changes clearance and speed. There is no encoder. [Adafruit 3766](https://www.adafruit.com/product/3766).

The four arm servos are Adafruit 2307 TowerPro MG92B. The listed envelope is 36 x 12 x 31 mm including the mounting features. Use the supplied 20-spline horns and centre screws. The printed parts deliberately do not copy the spline. The manufacturer requires 5 V control signals as well as servo power. The electrical design supplies this. [Adafruit 2307](https://www.adafruit.com/product/2307).

The head servo is Adafruit 154 FeeTech FS5103R, listed at 37 x 54 x 20 mm with a 25-spline output. It is a speed servo, not an angle servo. It was listed out of stock when researched. The slotted cradle and foam pads allow the supplied horn to be aligned with the belt plane. The belt and bearings carry the design load path; the servo shaft does not support the dome weight. [Adafruit 154](https://www.adafruit.com/product/154).

The rear cassette is for the original ESP32 TTGO T-Display, not the T-Display-S3 or an AMOLED variant. LILYGO documents the 1.14 in display, two buttons and USB-C interface. The printable pocket is 52.2x26mm; the design uses a nominal 51.52x25.04mm board envelope. This dimension is a fit assumption until the actual board is measured. If a revision exceeds the pocket, change the pocket and reprint the cassette before printing the rear body. [LILYGO documentation](https://github.com/Xinyuan-LilyGO/documentation/blob/master/en/products/t-display-series/t-display/index.md), [original board design files](https://github.com/Xinyuan-LilyGO/TTGO-T-Display).

The speaker is Adafruit 1313, the 77.8x77.8x25.49mm3 in 8-ohm model. Its mounting tabs use 60 mm spacing. The bracket provides a 69 mm sound opening and a 90 mm square plate. [Speaker](https://www.adafruit.com/product/1313), [manufacturer drawing](https://cdn-shop.adafruit.com/product-files/1313/C2464-001_datasheet.pdf).

The battery tray has 116 x 72 mm clear plan space, 15 mm retaining walls, two 20 mm strap passages and a 36 mm rear connector opening. It accepts the selected Bioenno BLF-1206A6Ah pack with padding. Reserve at least 30 mm behind the battery connector and keep the whole harness below the electronics deck. The battery is removable for charging. Follow the electrical document for the pack and charger; do not connect the 12 V pack to the T-Display battery socket.

## Coordinate and joint map

The floor is Z0. Positive Y is the rear. Positive X is the right side. All distances below are in millimetres.

| Interface | Location | Retention |
|---|---|---|
| Wheel centres, nominal | X±130, Y±65, Z31.5 | Wheels press on the specified TT shafts |
| Motor cradle centres | X±100, Y±40, Z17 | Four M3x65 bolts per cradle |
| Chassis | Z72–77 | Four flat quarters; 12 splice plates |
| Battery tray | Z77–92 | Four bolts at X±45, Y±30 |
| Electronics deck | Z172–175 | Four 95 mm posts at X±70, Y±50 |
| Lower skirt | Z77–167; R180 to R145 | Four quarters; M3 seams and flanges |
| Upper skirt | Z167–257; R145 to R120 | Four quarters; removable rear quarters |
| Shoulder | Z257–367 | Front and rear halves; full front transition ledges |
| Arm bracket backs | Y−102; bases Z270 | Four bolts each; centres X±43 |
| Arm yaw axes, nominal | X±43, Y−129, Z305 | Supplied servo horns |
| Arm pitch axes, nominal | X±43, Y−129, Z335 | Perpendicular supplied servo horns |
| Display centre | Rear Y120, Z323 | Four M3x25 cassette bolts |
| Switch centres | X±30, rear wall, Z279 |12.5 mm panel bores; switch mounting nuts |
| Neck adapter | Z367–371 | Three shoulder bolts at R110 |
| Neck rings | Z371–375 and 386–390 | Six 11 mm spacers; three through bolts |
| Neck deck | Z401–405 | Three M3x45 neck-stack bolts |
| Bearing tower | Z405–431 | Four M3x12 deck bolts |
| Head belt centres | X0 and X72.5; Z449.5 |3 mm round belt; slotted servo adjustment |
| Head plate | Z457–460 | Four M3x16 bolts at R17 |
| Dome | Z460–525 | Four M3x10 bolts at R101 |
| Lamp bases | Z519 | Flat pads on dome; two M3x16 bolts |
| Maximum height | Z541 | Top of decorative lamps |

The two axle centres are 130 mm apart fore-and-aft. The approximate track is 260 mm. Actual press-fit depth affects the final track. Keep both sides equal. At the nominal position, the inner wheel faces are X±115.5. Cradle rails stop at X±113. Outboard pillar centres are Y±10 and±24, with 4.5 mm radius, so they clear the wheel envelope. Do not move pillars back beside the axle; that would intersect the 29 mm-wide wheel.

## Print sequence and settings

1. Print `fit_coupon.stl`, one `motor_cradle.stl`, `arm_base.stl`, `pitch_carrier.stl`, `screen_frame.stl`, `screen_clamp.stl`, `bearing_tower.stl`, `bearing_cap.stl`, and `inner_spacer.stl` first. Use the actual nozzle and filament for the build. The coupon has 3.1/3.2/3.3/3.4 mm bores, 8.4 mm spindle clearance, 22.2 mm bearing clearance and 12.5 mm switch clearance. A3.4 mm clearance hole must freely pass an M3 screw. A bearing must seat by hand pressure without cracking the tower.
2. Fit the actual motors, servos, board, bearings, switch bushings and connector before committing to the large batch. The cradles use foam and ties, which permit small dimensional differences. Do not scale a whole STL to fix one interface. Change that CAD dimension.
3. Print cosmetic shells in PLA with a 0.4 mm nozzle, 0.2 mm layers and two perimeter lines. These shells are 0.8 mm thick. Keep the designed 2 mm flanges and 2.4 mm seam webs. The geometry provides their thickness; high infill does not strengthen an empty shell. Use three top and bottom layers on flat flanges. Handle shell edges carefully until bolted into rings.
4. Print PETG structural parts with four perimeters, 0.2 mm layers, five top and bottom layers, and 20–25% gyroid infill as the starting profile. Use dry filament. The 5 mm chassis is a connected rib grid with integral bolt bosses. Do not enable vase mode or remove its ribs.
5. Print the chassis, decks, rings, tray, splice plates and bracket bases flat. Print the 95 mm posts upright. Keep the exported orientation for the speaker bracket and screen frame. Add supports under the first head-hub pulley rim, under the arm cups/rods, and inside the dome where the slicer shows unsupported roofs. Remove support from every screw hole and bearing bore.
6. The eye can stand on its rear flange. The hemisphere open face goes on the bed. Its centre boss joins the crown; the centre hole remains open. Print several hemispheres in one batch, without merging them into one object.
7. Use a 5–8 mm brim if a tall part lifts. Inspect Bambu Studio layer previews for two continuous shell lines, retained M3 bosses, complete support contact, and no island warnings. Slice all BOM quantities and record filament mass before continuing. The fit-coupon slice evidence is in `cad/h2d-slice-check.json`; that single coupon does not establish a profile for every part.
8. Paint only after a dry assembly. Keep paint out of bearing bores, nut pockets, shaft fits, threads and belt grooves. Keep the metal-coloured finish light. Primer and filler can add substantial mass.

## Assemble the rolling base

1. Put four `chassis_quarter` parts on a flat surface. They have asymmetric mounting holes. Flip the flat plates to obtain the four mirrored quadrants. Do not simply rotate each copy 90 degrees. The finished motor-hole pattern must be X±79/±121 and Y±10/±24. The battery holes must be X±45, Y±30, and the electronics-post holes X±70, Y±50.
2. Fit three `splice` plates under each radial seam, at radii 30, 75 and 150. Each plate straddles a seam. Its two holes lie 8 mm on either side of that seam. Install 24 M3x16 screws, washers and nuts. Leave them loose until the four plate centres meet without a step. Tighten just enough to close the joints.
3. Place one TT motor in each `motor_cradle`, with its long body along Y and the wheel axle pointing outward along X. The yellow gearbox is at the outer fore/aft end. For the rear pair, the axle is toward+Y; for the front pair, toward−Y. The motor body sits on the 3 mm floor. Use thin foam pads on the narrow sides. Start with a 1.7 mm rear stop pad to put the axle near local Y25; verify with the actual drawing and wheel.
4. Put two cable ties through the paired floor slots at local Y−22 and 0. Pass them over the body. Keep them off the axle, motor terminals and gearbox screws. Tighten until the body cannot slide or roll. The ties supply retention; the cradle floor and pillars supply the weight path.
5. Bolt each cradle below the chassis with four M3x65 screws through the 55 mm pillars. Fit a washer under each head and nut. The pillars end at Z72. All four motors must hang to the same height.
6. Press each 3766 wheel squarely onto its TT axle. Hold the gearbox while pressing; do not push against the printed shell. Do not hammer. Verify equal insertion on each side, at least 2 mm clearance from the printed rails, and free hand rotation. The nominal wheel centres are Z31.5, and the 63 mm wheels must clear the chassis at Z72 by 9 mm.
7. Assemble four `bumper_quarter` parts into a ring with eight M3x12 seam screws. Leave the ring off until the electrical drive test has passed. The bottom of the finished bumper is Z15. It must never drag on a flat floor.

## Fit the battery and electronics

1. Bolt `battery_tray` to the chassis using four M3x16 screws at X±45, Y±30. Put the heads inside the tray and nuts below the chassis. Cover the screw heads with thin nonconductive padding before placing the battery. Keep the connector facing the rear opening.
2. Fit two 20 mm hook-and-loop straps through the tray. They must independently restrain the battery. A gentle hand shake must not move the battery or pull on its connector. Keep connector strain off the pack leads. Remove the pack for charging and transport.
3. Install four `deck_post` parts at X±70, Y±50. Put `electronics_deck` on the posts, with its speaker-foot holes toward the front. Fit four M3x110 through bolts, washers and nuts. The deck top must be Z175. The battery top remains below this deck.
4. Mount each board on 6 mm `pcb_standoff` parts using the slotted deck. Use actual board mounting holes. The slot grid accepts M2.5 hardware without assuming that every breakout has the same hole pattern. If a board has no mounting holes, use two ties through adjacent slots with nonconductive padding. Do not clamp an inductor, regulator, crystal or connector. Keep the two motor regulators and drivers separated so air can reach them.
5. Fit `speaker_mount` at the front of the deck. Its horizontal foot reaches inward to Y−50 and its two foot bolts align with deck X±30, Y−50. The speaker plate stands at Y−65, from Z175 to 265. Fit the speaker with four M3x12 bolts on its 60 mm mounting pattern. The cone faces forward. Add a thin foam gasket; do not cover the cone.
6. Route cables against fixed walls. Fit strain relief at every moving servo cable. Keep all wiring below the neck bearing deck and out of the belt. Complete the electrical checks in the main assembly guide before installing the shell.

## Assemble the skirt and body

1. Insert one standard M3 nut into each `hemisphere` bottom pocket. Fix each cap with one M3x8 screw and a washer from inside its skirt quarter. Each quarter has six caps. The lower and upper rows sit 23 and 67 mm above that tier's bottom. The cap axis tilts upward with the cone normal: 21.25 degrees on the lower skirt and 15.52 degrees on the upper skirt. The printed mounting bores already use those angles. Do not force the cap to sit radially horizontal.
2. Join four lower quarters with eight M3x12 seam screws. Join four upper quarters with eight more. Fit washers to spread the load on thin webs. Hold the captive nut with a driver while tightening; never twist the shell to react screw torque.
3. Sandwich the chassis between the bumper's top flanges and the lower skirt's bottom flanges. Install 12 M3x16 bolts on radius 170 at angles 15, 45, 75 degrees in each quadrant. The stack is 2 mm bumper flange, 5 mm chassis and 2 mm skirt flange. These are through bolts with nuts; there are no hidden friction-only joins.
4. Bolt lower to upper skirt with 12 M3x12 screws on radius 135. Fit the shoulder to the upper skirt with 12 M3x12 screws on radius 110. Keep the rear two upper-skirt quarters removable. Remove their seam and flange screws when large service access is needed; no glued seam must block battery removal.
5. Join the shoulder front and rear halves with four M3x12 seam bolts. The flat front has reinforced arm pads. Its full circular transition ledges close the space between the flat face and the skirt/neck. The ledges retain the two front skirt bolts and the front neck bolt.

## Install the rear display and switches

1. Fit the original T-Display into the `screen_frame` pocket from behind, screen outward. The 49 x 23 mm front window overlaps the board edge. The 52.2x26mm rear pocket captures the board plan shape. Orient the USB-C port toward the side notch. Check that both buttons can move and the glass does not carry clamping force.
2. Add small nonconductive foam pads at bare PCB edges on the back. Fit `screen_clamp`, the rear cover. Its central opening gives component clearance. Use padding only where no component or solder joint is loaded. The board must not rattle, bow or be held by its USB connector.
3. The frame's four corner feet are profiled to the curved outer shoulder. The rear cover posts are trimmed to its inner radius. A thin foam washer at each body contact takes up the remaining curved-wall tolerance. Install four M3x25 bolts through the outer frame, shell and cover, with nuts inside. Tighten evenly. The board and screen are visible from the rear at Z323.
4. Connect a USB-C cable through the side notch with the cassette in place. Confirm that the plug can fully seat and can be removed without forcing the board. Leave a service loop on the internal wiring so the entire cassette can be withdrawn.
5. Fit the two NKK S1A switches in the 12.5 mm rear bores at Z279. Use the supplied panel nuts and anti-rotation hardware. Labels must read MAIN and ACTUATORS OFF as specified in the electrical guide. Switch bodies and terminals remain clear of the display. Test access before closing the rear half.

## Build and calibrate the two arms

1. Set the four MG92B servos to their firmware centre pulse before installing horns. Use the specified level-shifted control signals. Keep the arms off during this first power test.
2. Bolt each `arm_base` to its shoulder pad with four M3x16 screws. The bracket back face sits flush on Y−102. The horizontal floor points forward. The bases sit at Z270 and X±43.
3. Place one yaw servo upright in each base. Use foam to centre its shaft at X±43, Y−129. The body rests on the bracket floor. Put two ties through the floor slots and around the body. The shaft must point upward. No tie may cross its moving horn.
4. Use the supplied yaw horn. Attach `pitch_carrier` to it with two M2x10 screws, washers and nuts through opposite radial slots. The slots are centred 8 mm from the shaft. If the supplied horn holes do not align, drill two 2.1 mm holes in that removable plastic horn using the printed carrier as the template. Keep both holes equally spaced from the centre. Do not drill the servo.
5. Secure the horn to the servo with its supplied centre screw, accessed through the 5 mm central hole. At centre, the pitch-carrier upright wall is on the+X side. Set its underside near Z305. Check that it clears the fixed cradle throughout the intended small yaw range.
6. Fit the pitch servo sideways against the carrier's upright wall. Its output shaft points toward−X. Align the output centre 30 mm above the carrier base and on the carrier Y0 line. Use nonconductive foam behind the case and two ties through the upright wall slots. This mount permits body tolerances while fixing the shaft datum. Keep the case firmly seated without loading its output bearing sideways.
7. Attach the supplied pitch horn to `plunger_arm` or `gun_arm` using two M2x10 screws through the opposite slots perpendicular to the arm tube. These slots pass through only the 3 mm disc. The central 5 mm bore provides access to the supplied spline screw. The rods are decorative. The gun-shaped part has no projectile mechanism.
8. Install the arms pointing forward at the centre pulse. Start with ±2 degrees on each axis and 0.10 Hz circular motion. Increase only to the firmware's intended small range after clearance tests. The two axes use sine and cosine commands with a quarter-cycle phase difference. Their tips trace circles; the shafts do not spin continuously.
9. Turn off drive power and observe at least 20 slow circles. Check arm-to-arm, arm-to-shell, horn-to-bracket and cable clearance. Route each pitch cable in a loose U-shaped loop back to the fixed base. Tie both ends so the flex occurs in the loop. Stop if a servo buzzes continuously or a cable becomes tight.

## Build the bearing-supported rotating head

The bearing axial stack is explicit. From bottom to top: M8 bolt head; 8x12x1mm lower shim at Z404–405; lower 608 bearing Z405–412; printed 12 mm inner spacer Z412–424; upper 608 bearing Z424–431; 8x12x1mm upper shim Z431–432; printed head hub Z432–457; head plate Z457–460; standard M8 washer; M8 nyloc nut. The M8x70 bolt must show at least two full threads beyond the nut. Narrow shims touch only the rotating inner races. A standard 16 mm-OD M8 washer must not be substituted inside the 16 mm cap bore.

1. Bolt `neck_adapter` to the shoulder with three M3x12 screws at radius 110 and angles 30, 150, 270 degrees. The larger inner opening faces upward.
2. Stack a `neck_ring`, three 11 mm `neck_post` spacers, the second ring, three more posts, then `neck_deck`. Align the radius 104 holes at the same three angles. Fit three M3x45 through bolts. The adapter starts at Z367 and the neck deck finishes at Z405.
3. Fit the lower 608 into the bearing tower from its bottom. Fit the upper 608 from the top. Put the 12 mm printed inner spacer between their inner races. Bolt the tower to the neck deck with four M3x12 screws at radius 24. The deck retains the lower bearing's outer race.
4. Fit `bearing_cap` using three M3x8 plastic thread-forming screws in the 2.6 mm pilots. The cap retains the upper outer race at Z431. Its centre bore is 16 mm. Do not overtighten or split the thin outer wall.
5. Insert the M8 bolt, lower narrow shim, inner stack, upper narrow shim and hub as listed above. The hub's 12 mm-diameter foot passes through the cap without contact. The hub foot carries the dome load onto the upper inner race. Its pulley groove centre is Z449.5.
6. Attach `head_plate` to the hub with four M3x16 screws at radius 17. Hold nuts underneath the hub flange. Install the M8 washer and nyloc nut above the plate. Tighten only until axial play disappears. Turn the hub by hand: the head must make a full turn freely, while the tower and cap remain stationary. Excess drag means the inner stack, shim or cap is wrong; do not mask it with more servo power.
7. Bolt `head_servo_mount` to the deck. Its nominal output centre is X72.5, Y0. Use the four slots to adjust the centre distance. Fit the FS5103R body with two ties and foam pads, shaft upward. Align the supplied horn top with the pulley mounting face at Z445. The 37 mm listed body height fits above the cradle's Z408 floor. Adjust the pads to the actual case and horn; verify the groove plane before tightening.
8. Bolt `servo_pulley` to its supplied horn with two M2x10 screws. The printed central bore and radial slots are through holes. Use the servo's original centre screw, never a printed spline. Fit the 83 mm-ID, 3 mm-cord NBR O-ring around both pulleys. Adjust the cradle until the belt is lightly tensioned and runs in both grooves. The large groove root diameter is 59 mm; the small is 20 mm. Avoid strong belt tension, which loads the servo bearing.
9. Turn the dome hub by hand through two turns. The belt must track centrally without touching the neck posts or wiring. Then run the servo slowly in both directions with the dome absent. The firmware neutral pulse needs individual calibration; a continuous servo has no position reference.
10. Fit `eye` to the dome's flat front pad with two M3x16 screws and nuts from inside. The eye faces forward. Insert captive nuts in the two lamp bases and fix the lamps to the raised flat dome pads with two M3x16 screws from inside. The lamps are translucent decoration only. No slip ring or head wiring is required.
11. Insert four M3 nuts in the dome flange pockets. Fit the dome to `head_plate` with four M3x10 screws from below at radius 101. Keep access to these screws so the dome can be removed later. The head plate and dome rotate together around the M8 spindle.
12. Test one full slow turn in each direction. The eye sweeps beyond the body; leave clear space. Confirm that nothing touches the fixed neck, no cable enters the head, and the belt can slip under a gentle restrained-head test without distorting the servo mount. Do not hold a powered head for more than an instant.

## Physical acceptance gates

- All STL and envelope checks must pass before slicing. Re-run `C:/Python314/python.exe scripts/export_cad.py --check-only` after any CAD export. To regenerate all parts, run `C:/Python314/python.exe scripts/export_cad.py --jobs 3`. Individual exports have a 180 second timeout and stop on failure.
- Before fitting the shell, run all four wheels on a stand. Verify side polarity, stop response, current limit and that each wheel clears its cradle. Correct a reversed motor in wiring or the documented firmware channel mapping.
- Weigh the loaded robot. At 3 kg or more, do not assume the selected TT motors can turn it on the chosen floor. Reduce print/finish mass or investigate the actual drive load before driving with the shell fitted.
- Start on a level hard floor, at walking-toy speed, with broad arc turns. Do not assume a zero-radius pivot will work. Wide silicone tires scrub during four-wheel steering. Measure current and temperature during repeated starts and turns. Carpet, ramps and thresholds are outside the initial operating envelope.
- The arm tips must clear the shell and each other through the entire allowed cycle. The head must turn 360 degrees without any fixed contact. Recheck fasteners after the first ten minutes of operation.
- With the network interrupted or browser closed, the firmware must stop motion. The operator must be able to reach ACTUATORS OFF from the rear. Complete the electrical and firmware commissioning checklist before a public demonstration.

## Maintenance and access

Remove the four display-cassette screws for USB/board access. Remove the shoulder rear half or the two rear upper-skirt quarters for electronics access. Remove the four dome screws for the bearing and belt. Remove the battery from its straps before transport or charging. Keep shell joins bolted; glue is not part of a service joint. Inspect motor ties, belt condition, bearing play and cable loops before every use.
