# Assembly and commissioning

## Tools and first checks

Use a Bambu H2D, 0.4 mm nozzle, dry PETG and PLA, calipers, a flat reference
surface, small square, protractor, M2/M3/M4 drivers, 7 mm and 13 mm spanners,
side cutters, wire stripper, soldering iron, heatshrink, multimeter and a
current-limited bench supply. A small luggage scale helps measure pulling
force. A thermocouple or infrared thermometer helps check motor/regulator
temperature. Eye protection is needed when drilling or cutting rods.

Read the mechanical height stack and electrical chapter before assembling.
Inspect purchased items against the BOM. Print and test the fit parts first.
Keep the battery disconnected until the electrical checks reach the
specified connection step. Do not start with the complete shell installed;
the first chassis test determines whether the chosen motors can move the
actual weight on your floor.

## Stage 1 - feet and motors

1. Label foot plates L, R and B. Mark their forward Y direction. Both
   motors on each plate use the same orientation, with the motor cans
   toward negative Y and shafts at local Y=-45 and +45.
2. Smooth the six cradle floors and remove support from the slots. Put
   thin foam under each motor. Feed two 3 mm cable ties through the slots
   at local Y=-40 and -15. Leave them loose.
3. Fit one wheel on each motor shaft. Support the opposite axle while
   pressing by hand. Do not hammer or grip the gearbox with pliers. Keep
   equal insertion depth on the two sides and leave clearance to the case.
4. Place each cradle at Z=16 with wheels on a flat reference plane. Adjust
   the thin padding so both axle centers are about 31.5 mm above that plane.
   Rotate both wheels by hand; they must clear rails, ties and the case.
5. Fasten each cradle under its foot deck with three M3x60 bolts, washers
   and nuts. Pillar holes are at X=-18/+18,Y=-50 and X=0,Y=+20 relative to
   each shaft. Pillar tops meet the deck underside at Z=65. Do not crush
   the pillars; tighten until the washers stop moving.
6. Tighten the case ties only enough to prevent motion. Check shaft and
   wheel clearance again. Motor M1/M2 belong to L, M3/M4 to R, M5/M6 to B.
   Solder each suppression capacitor across its motor tabs and label leads.
7. Fit the two side foot covers. Their four integral posts land on the
   deck. Use four M3x35 bolts per cover at X=+/-46,Y=+/-90 with washers
   and nuts. Leave the center leg openings clear. The rear foot has no
   cover so the steering spindle and harness remain accessible.

## Stage 2 - body frame and side legs

8. Build three body rings from four `frame_quarter` pieces each. Mirror
   pieces across X/Y as shown by the assembly view. The paired seam holes
   are 10 mm apart across each seam at radii 40 and 95. Fit two splice
   plates per seam, each with two M3x16 bolts, washers and nuts. Use eight
   splices per ring, twenty-four total. Assemble on a flat surface.
9. Put the bottom ring at Z=170. Place `rear_attach` under its rear edge
   at Z=165..170. Its outer holes join the rear body rods at X=+/-75,Y=-75.
   Put the lower `deck_adapter` on the ring at Z=175..178.
10. Cut four M4 body rods to 315 mm and deburr both ends. Fit nuts and
    washers under the bottom ring, including the rear attachment plate on
    the rear two rods. Add four 137 mm `body_post` sleeves above the lower
    adapter. Add the middle ring at Z=315..320 and the second adapter at
    Z=320..323. Snug the lower nuts; do not preload the frame heavily.
11. Add four 97 mm `head_support` sleeves, the `head_deck` at Z=420..424,
    four 36 mm `top_post` sleeves and the upper body ring at Z=460..465.
    Use the diagonal rod holes in the head deck, not its servo slots.
    Fit washers and double nuts above the top ring. Check all three rings
    are parallel, centered and square to the rods before locking the nuts.
12. Cut four M4 leg rods to 280 mm. Two go through each side foot at
    X=0,Y=+/-20. Stack two `leg_segment` parts over each pair from Z=70 to
    320. The 1.2 mm skins are covers around the rod structure; do not clamp
    or lift the robot by squeezing them.
13. Put each shoulder bridge on its leg at Z=320. Mirror the left bridge.
    Fit the outer rod nuts and washers. Its inner two holes at X=+/-105,
    Y=+/-20 bolt to the matching middle ring holes with M4x20 hardware.
    Keep both feet parallel. Add the decorative shoulder caps only after
    the structure passes the rolling test; use small removable adhesive
    pads rather than glue on the load-bearing joints.
14. Bolt the battery tray to the lower adapter with four M3x12 bolts at
    X=+/-45,Y=+/-30. Leave the battery out. Add two straps through the tray
    slots and verify the discharge and charge leads have a free exit.

## Stage 3 - rear steering and bearings

15. Fit the `rear_bracket` under `rear_attach` using the four M4x20 joints
    at X=+/-35,global Y=-103/-82. The rear bracket origin is (0,-180,110).
    Its 5 mm top flange ends at Z=165. Check the bracket is square to the
    body and the spindle center is exactly 180 mm behind the main feet.
16. Press two 608 bearings into a `bearing_tower`, one from each end.
    Insert the 12 mm `race_spacer` between their inner races. Mount the
    tower on the rear bracket at Z=114 using four M3x16 bolts through
    radius-24 holes. Add the cap with three M3x8 thread-forming screws in
    the 2.6 mm pilot holes. Do not use machine screws in these pilots.
17. Insert the M8x120 rear spindle bolt from below the rear foot, seating
    its head in the hex recess. Fit the 38 mm `spindle_sleeve` on top of
    the foot's 10 mm central boss, then one 1 mm inner-race shim. Feed
    the shaft through the lower bearing, internal spacer and upper bearing.
18. Add a 1 mm inner-race shim above the upper bearing, then `gear_hub`.
    Seat one thin M8 nut in its hex pocket and add a second jam nut.
    Snug the stack until axial play disappears while the foot turns freely.
    Hold the inner nut and lock the outer one. Do not tighten against the
    bearing outer rings or seals. Trim excess bolt projection if needed,
    keeping at least two full threads beyond the final nut.
19. Power the steering servo alone with a suitable 5 V bench supply and
    a 1500 microsecond test pulse, or use the firmware with all drive
    motor plugs disconnected. Center the servo before attaching its horn.
    Do not move the servo by forcing the horn against the gearbox.
20. Bolt its supplied horn to a `servo_pinion` with M2 bolts/nuts through
    the radial slots. Use the supplied spline center screw. Place the
    servo in its dropped cradle and set the pinion base to Z=151 with
    the 1/2/4 mm shims. Secure two ties and foam pads without crushing it.
21. Bolt the cradle into the rear bracket slots. Align the rear foot
    straight ahead before meshing the gears. Slide the cradle to obtain
    free mesh with slight backlash and no tooth bottoming. Nominal center
    distance is 45 mm. Tighten the four mounting bolts only after checking
    the full intended steering range.
22. With motors still unplugged, command rear steering slowly in each
    direction. At phone +100/-100 the actual foot must reach +25/-25
    degrees, within about two degrees. Adjust STEER_CENTER_US and
    STEER_US_PER_DEGREE in config.h to the measured horn/servo response.
    Gear inversion is already accounted for by the negative pulse slope.
    If the foot binds or stalls, stop and fix the geometry before travel.
23. Route rear motor wires through a restrained service loop that permits
    plus/minus 30 degrees without touching the gears. The loop must not
    tighten at the command limits. Do not route wires through the spindle.

## Stage 4 - rotating head

24. Assemble the second tower and bearing spacer as in step 16. Mount it
    on `head_deck` at Z=424. Its cap ends at Z=453. Keep cap screw ends
    away from the bearing shields.
25. Insert the M8x65 bolt from below the lower bearing, with a 1 mm
    inner-race shim under its head. Add the upper shim and gear hub. Fit
    the captured nut and jam nut. The hub starts at Z=451 and ends at
    470. It must rotate freely without rocking; adjust preload by hand.
26. Fit the FS5103R continuous servo in its cradle with its supplied horn
    and pinion. Set the pinion base to Z=461 with shims and align the teeth.
    Adjust the servo's neutral trim so 1500 microseconds produces no
    movement. Record any remaining neutral correction in config.h.
27. Attach `head_plate` to the hub's four radius-12 holes with M3x18 bolts,
    washers and nuts. Its central opening clears the spindle nuts. Check
    that no screw head contacts the cap during a full rotation.
28. Fix `neck` above the upper frame at Z=465 with twelve M3x16 joints.
    Fit the dome's four M3 captured nuts. Put four 6.6 mm spacers between
    head plate and dome, centered at radius 119. Use four M3x16 bolts
    from below into the dome nuts. The dome starts at Z=479.6.
29. Turn the head manually through 360 degrees with power off. Require
    at least 2 mm clearance around the fixed neck and no contact between
    rods, screw ends and rotating parts. Then run the head at low speed
    in both directions. No wire belongs inside the dome. The eye and
    blue markings are decorative and unpowered.

## Stage 5 - boards, wiring and inspection

30. Mount the utility deck on four 6 mm spacers above the middle adapter.
    Use four M3x20 through bolts. Place the HUZZAH32 near the service
    opening, with its USB socket accessible. Use M2.5 bolts in board holes
    where provided, and foam plus cable ties on slots where a board has
    no usable hole. No exposed solder joint touches a metal rod or deck.
31. Mount the three driver boards along the utility deck edge, keeping
    each motor plug labeled. Put the buffer/prototype board and amplifier
    away from driver output wires. Keep I2S leads short. Mount the speaker
    in its printed plate using a soft rim pad and two ties through the
    side slots; do not press on the cone. Fasten or tie the speaker plate
    to unused utility-deck slots, cone up, clear of the head mechanism.
32. Place the four UBECs on the lower adapter in pairs near Y=+/-58,
    outside the battery tray. Restrain them with ties through the adapter
    openings. Keep exposed cases apart and allow air around their surfaces.
    The logic buck and fuse holders can use the remaining lower deck edge.
33. Choose the rear upper shell quarter as the removable service panel.
    Use `switch_plate` as the drilling template: two 12.5 mm openings
    centered 30 mm apart, and four M3 attachment holes on a 60 x 32 mm
    rectangle. Place the panel center near global Z=365 and away from a
    seam or rod. Drill the shell only after checking the switch-body and
    wire clearances inside. Use the switch plate as a flat backing face
    with small foam pads at the curved-shell edges. Label MAIN and RUN.
34. Wire every connection in wiring.csv, marking rows complete. Work
    through power first, driver signals next, buffer/servos, sense and
    audio last. Check resistor values with the meter before installation.
    Keep battery positive disconnected and fuses removed during soldering.
35. Inspect every joint, ferrule and capacitor polarity. Check that none
    of the four 5 V UBEC outputs is connected to another positive output.
    Verify all grounds connect. Verify speaker leads are isolated from
    ground. Inspect the AHCT notch and all fourteen pins against the map.
36. With boards and motors unplugged, test power converters using a
    current-limited 12 V bench supply. Measure each 5 V rail, MAIN and RUN
    switch behavior and both divider outputs. Pack-sense ratio is 22/122;
    RUN-sense ratio is 15/25. Disconnect power before attaching boards.
37. Restore the boards, keep motors and servos unplugged, and test again
    at a low current limit. Confirm 3.3 V on the Feather and a high FLT
    input. Correct unexpected current or heating before moving on.

## Stage 6 - firmware and first drive

38. With robot battery disconnected and J_USB removed, connect the
    HUZZAH32 to the computer. Run `pio run -d firmware -t upload`, followed
    by `pio run -d firmware -t uploadfs`. Use `--upload-port COMx` for the
    actual controller port if automatic detection is ambiguous. Do not
    upload to another device connected to the computer.
39. Open `pio device monitor -b 115200`, reset the board and privately
    save its generated Wi-Fi password. Join network R2-24 from the phone
    and open http://192.168.4.1. This is a local access point; it needs no
    router or Internet account. The initial screen must be disarmed.
40. Disconnect USB, restore J_USB and reconnect robot power with RUN off.
    Strap the battery down with both straps. Compare displayed voltage to
    a meter, then calibrate PACK_CORRECTION if needed. Arming must fail
    while RUN is off. Turn RUN on only with all wheels lifted and clear.
41. Connect one motor pair at a time. Arm, hold forward at minimum speed
    and check that both wheels on each motor move forward at the ground.
    Reverse motor plug polarity if one motor differs within its pair.
    Change the group's DIRECTION in config.h if the complete pair is
    reversed. Disconnect power before changing wiring.
42. Test reverse, release-to-stop, STOP, loss of phone Wi-Fi, page hide,
    browser close and RUN-off. Motion commands expire within 500 ms of
    the last accepted heartbeat. No old command or power restoration may
    restart motion without a new Arm press. Check actual wheel stopping
    time as well as command timeout. Physical RUN-off must always work.
43. Reconnect servos and verify the steering and head calibration from
    stages 3-4. Head motion stops at release and at STOP. The rear foot
    holds its current angle after STOP; it does not snap to center.
    Use Center steering while armed and stopped to align it for handling.
44. Play all sixteen sound clips at low volume. Confirm no controller
    resets when audio starts or motors accelerate. A reset means power
    integrity needs repair, not a reason to disable the fault checks.
45. Place the bare chassis on the intended floor, with a person beside
    the physical RUN switch. Test short straight travel, reverse and large
    arcs at low speed. The rear wheels must follow the curve without
    skidding sideways. Do not test stairs, carpet, slopes or thresholds.
46. Secure temporary ballast low in the tray area to reach the predicted
    completed mass, at most 4.5 kg. Measure current and temperatures during
    several gentle arcs and a ten-minute run. Require no stalls, no driver
    faults, no supply resets, no loose shafts and no continuous motor
    current above 0.5 A during gentle travel. Stop if cases exceed 50 C,
    wiring heats or gears grind. These are conservative build acceptance
    gates, not published component operating ratings.

## Stage 7 - skins and final acceptance

47. Only after the loaded chassis passes, install the lower four shell
    quarters. Use M3x12 at the bottom rim and vertical seams. Use M3x16
    where both shell flanges sandwich the middle frame, and through the
    upper shell/frame/neck stack. Install the four mirrored upper quarters
    around the shoulder slots. Use its eight remaining lower-rim holes;
    the other four middle-ring joints hold only the lower shell with
    M3x12. Use all twelve upper-rim holes. Keep the rear service quarter
    removable. Require full nut engagement and no screw tip touching a
    rotating part; shorten only excess tips after dry assembly.
48. Complete the light paint finish and attach the eye with a small epoxy
    fillet after fitting it to the dome curvature. Use the printed panel
    as a paint stencil or apply with compliant pads. Do not add thick
    resin coatings or filler. Do not glue service screws, bearings or gears.
49. Weigh the completed robot and measure height. Target 609.6 mm, always
    below 914.4 mm. Confirm the measured mass does not exceed the load used
    in the successful chassis test or the 4.5 kg commissioning limit.
50. Repeat the stop, disconnect, steering, sound and ten-minute temperature
    checks with all skins installed. Record current, temperatures, mass,
    stopping distance, steering limits and runtime in a build log. Mark
    the machine ready only after all tests pass. Keep it supervised.

## Fault finding

If the controller will not arm, check RUN sense, pack voltage, the common
ground and open-drain FLT wiring. If it resets under load, inspect power
distribution and USB-source isolation. If a foot turns opposite the others,
check motor polarity before changing the mixer. If the rear foot scrubs,
check its mechanical neutral and servo slope. If the dome drifts at rest,
trim the continuous servo neutral. If a bearing binds, remove oversized
washers or reduce preload. If the robot cannot move the test mass, do not
raise current limits to hide it; revise weight or gearing and repeat the
chassis gate before closing the shell.
