# Assembly and commissioning sequence

Build and test one subsystem at a time. The mechanical chapter gives the exact part filenames, fasteners, bearing fits and assembly order. The electrical chapter and circuit sheets give the exact wire connections. This chapter places those operations in a safe order and defines when each stage is complete. A check is not complete until it has been performed on the physical robot.

## 1. Inventory before printing

Read the whole manual and open the CAD preview. Inventory `bom/electronics.csv`, `bom/hardware.csv`, and `bom/printed-parts.csv`. The quantities in the printed-parts list are quantities to make, not the number of files. Some decorative and structural pieces are used repeatedly. Keep screws in labelled bags by thread and length.

Check the actual board: it must be the original TTGO T-Display ESP32 with the 1.14-inch screen. Check the labels on all five servos, four motors, two driver boards and battery. Do not fit an S3 board or a same-size-looking servo without checking the mechanical drawings and pin assignments. The selected wheel and head servo were listed out of stock during research; obtain those exact parts before declaring the build ready to assemble.

Tools: a digital calliper, metric hex keys, small Phillips drivers, flush cutters, a deburring tool, soldering iron, solder, wire stripper, crimp tool for the selected connectors, heat-shrink tube, digital multimeter, a current-limited bench supply, and a scale. A contact temperature probe and an oscilloscope improve the power and noise tests. Use eye protection when cutting wire or drilling. A threaded fastener, bearing, motor, battery or connector is purchased hardware, not a printed substitute.

Done when every required purchased item is present or its absence is recorded, the board variant is confirmed, and the tools can measure voltage and current. This is an inventory gate. It does not require assembling or energising anything.

## 2. Prove fit with small prints

Print the fit coupon and critical holders first. Use the intended structural material and slicer profile. Check screw-clearance holes, nut pockets, motor fit, servo fit, bearing seat and the T-Display opening using the real hardware. Clean a first-layer edge before concluding that a dimension is wrong. Do not force a bearing or crush a board into a tight print.

If a fit needs adjustment, change the relevant clearance parameter in the OpenSCAD source, export that part again, and test it again. Do not scale the whole model in the slicer. Record the material, nozzle, layer height and clearance that passed. A printer-specific compensation may be needed, but it must preserve the joint centres and part lengths.

Done when fasteners pass without splitting the part, nuts retain their flats, the motor cannot shift in its holder, servo bodies seat without force, and the screen is visible with the USB connector accessible. The rear holder must retain the PCB by its edges without pressing on the glass.

## 3. Print and label the remaining parts

Follow the orientation and quantity fields in `printed-parts.csv`. Start with the chassis, brackets and joining parts. Then print the skirt, shoulders, neck and dome. Use the settings in the mechanical chapter. Keep the supplied model at 100% scale. The delivered orientation is part of the bed-fit check; inspect each part's contact face before slicing.

Use the H2D profile for the nozzle actually installed. A single material can make the whole robot, with paint for the bronze and black surfaces. Colour changes are cosmetic and should not affect a joint. Add a brim where the print notes call for one. Remove supports fully from nut traps, screw holes, grooves and bearing seats. Keep paint out of moving fits.

Weigh each group after support removal. Record total printed mass and the eventual fully assembled mass. Do not use slicer infill percentage as a direct mass estimate for thin shells: most of a thin shell may already be walls. The validation report's solid mesh volume is a useful conservative bound for fully filled material, not a slicer timing estimate.

Done when every manifest quantity is made, identified, free from cracks and checked against its mating piece. Do not close the cosmetic shell yet.

## 4. Assemble the chassis without power

Follow the chassis and motor-holder steps in `mechanical.md`. Fasten printed joins with the listed bolts, washers and nuts. Tighten until the joint is secure; further tightening can crush printed plastic. Do not put liquid thread-locker on printed plastic. Use the locking hardware in the bill of materials.

Seat all four motors in the specified direction. Give their thin motor leads strain relief. Press each wheel onto its TT output shaft while supporting the gearbox body. The wheel's hub fit provides retention; do not drill the motor shaft. Check that tires cannot rub the bumper, a bolt, or a motor cable at any rotation. Check that the assembled chassis does not rock on a flat surface.

Install the empty battery cradle and its straps. The battery remains disconnected. Keep the pack low and centred. It must not rest on screw points or sharp layer edges. Mount the electronics deck and insulating standoffs. Keep the deck removable until commissioning is complete.

Done when all wheels rotate by hand without body contact, motors cannot slide, the chassis rests evenly, and the battery can be removed without cutting wires. The mechanical chapter defines the exact floor and wheel clearances.

## 5. Build the power harness on the bench

Make the harness from the circuit sheets and `electronics/wiring.csv`, using the listed wire gauges and connector ratings. Put the main fuse close to the battery connector. Put the physical actuator switch in the feed to both movement converters. Keep the logic branch separately powered from the main switch. Terminate returns at the common ground point. Do not use a solderless breadboard or loose Dupont contacts for motor, servo or battery current.

Label every connector at both ends. Use a different keyed connector, or a clearly different connector size, for battery voltage and 5 V. Insulate exposed terminals and add strain relief. Confirm electrolytic capacitor polarity. Fit the motor noise capacitors close to the motor terminals. Never place a diode directly across a bidirectional motor as though it were a relay coil.

With the battery disconnected, check continuity of every wire against the net list. Check for shorts between each supply and ground. Inspect the physical switch and fuse ratings; an AC-only current rating is not a sufficient DC switch rating. Check the ADC resistor values with the meter before connecting an ESP32 input.

Done when every net has been checked, no supply is shorted, the battery connector polarity is correct, and the actuator switch interrupts both movement branches. Keep all downstream boards disconnected for the next stage.

## 6. Check the three supplies before connecting boards

Energise the harness from a current-limited bench supply at a voltage in the battery's operating range. Check each converter's unloaded output. Each 5 V branch must be within its specified tolerance and suitable for the attached devices. Then test each branch with an appropriate known load. Do not connect the battery voltage to a 5 V rail to make a failed converter test pass.

Confirm the actuator switch makes the motor and servo outputs fall to zero after stored capacitor charge has decayed. Confirm the logic output remains available. Check the external pack divider voltage against the calculation in the electrical chapter. At the maximum charge voltage it must remain below the ESP32 input limit. A reversed divider is a board-damaging error.

Done when the motor, servo and logic rails pass unloaded and loaded checks, the pack divider passes, and the physical actuator switch has the intended effect. A warm regulator alone does not prove a safe load; measure its temperature and voltage under load.

## 7. Flash and start the controller on USB only

Disconnect the battery and external controller 5 V supply. Leave all actuator supplies off. Connect the T-Display to the computer using USB. Do not back-feed the USB supply from an external 5 V source. Use the complete flashing procedure in `firmware.md`, including both the program and the LittleFS image. A program upload alone does not install the audio files.

After boot, check that the rear display is readable and shows network and safety status. Join the robot's access point using the credentials shown by the controller. Open the displayed local address. Check that the interface loads with the phone's Internet access disabled. It must display the sound list and controls without fetching a web font or script from a public website.

Store home Wi-Fi settings only through the local setup form. Use a 2.4 GHz network supported by the ESP32. Check the displayed station address after joining. If the home network is unavailable, follow the fallback procedure. Do not put Wi-Fi passwords in source files, a screenshot, this manual, or Git.

Done when the firmware and filesystem load, the TFT is readable, direct AP control works, station setup works on the intended network, and startup does not arm movement. Hardware-dependent status may correctly block arming until the next stages are complete.

## 8. Verify logic and hardware disable states

With USB removed, reconnect the external logic supply and the low-voltage control harness. Keep movement power off. Confirm the ground is common before connecting signal wires. Check the PCA9685 address and the buffer connections. Verify the motor sleep line is low and the servo output-enable line is in its disabled state at reset.

The servo buffers operate from the switched servo supply. Each PWM path, buffer output and ground must match the circuit sheet. The servo power cable must never connect to the ESP32's 3.3 V pin. Check the ADC display against a meter and apply the documented calibration factor if needed.

Done when reset leaves actuators disabled, the controller detects the actuator switch state, the PCA9685 responds, and battery voltage agrees with the meter to the stated tolerance. A blocked arm command is the correct outcome while power or sensor checks fail.

## 9. Test drive direction with wheels lifted

Support the chassis so all tires are clear of the bench. Keep hands away from the wheels. Connect the movement supplies and explicitly arm through the interface. Apply a brief, low command to both sides. Each wheel must turn in the direction that would move the robot forward. The right-side motors are physically mirrored, so their lead polarity must be checked, not copied by wire colour.

If one motor on a side turns backward, disarm, isolate power and reverse only that motor's two output leads. Do not connect two driver outputs together. Once directions are correct, test a slow forward command, a stop, a slow reverse command and a stop. Listen for rubbing and inspect driver temperature. Do not hold a stopped wheel against power to measure stall behavior.

Done when all four directions are correct, release stops the command, reversing passes through zero, and no tire or wire rubs. Leave final turning and loaded traction tests for the floor stage.

## 10. Centre servos before attaching the arms

Keep the arm horns and head drive connection detached. Command the positional channels to their documented centre pulse. Check that each servo stops and does not buzz against a hard limit. Fit the supplied horns at the neutral positions shown in the mechanical chapter. Retain each horn with its own centre screw. Do not print a replacement servo spline.

Assemble each gimbal using its exact brackets and retaining hardware. Route the servo lead with a free loop for the full small-angle movement. Do not tie that loop across a hinge. Fit the lightweight arm shaft and decorative end. Check by hand that each axis can move through its intended range before applying power.

Start the circular motion at a small radius and low frequency. Check one arm at a time. Correct a reversed axis using the calibration setting, not a cable swap on a three-wire servo. Increase only to the supplied bounded operating range. The tip should trace a near-circle without the arm touching the shoulder or pulling a wire.

Done when both arms can complete repeated circles quietly, every fastener remains secure, no servo stalls, and the supply stays within tolerance. Continuous buzzing, a hot servo or a distorted orbit calls for a mechanical or calibration correction before proceeding.

## 11. Assemble and test the head

Follow the bearing, shaft, belt and retention sequence in `mechanical.md`. Check all bearing seats before fitting the dome. Turn the assembly through several full revolutions by hand. Check the eye-stalk sweep against the arms and the surrounding area. Keep the head drive lightly tensioned as specified; excessive belt tension loads both the servo and bearing.

With the drive disconnected, adjust the continuous servo's neutral setting until it stops. Connect the drive and test low speed in each direction. The rotating structure carries no wires. Secure the fixed servo lead below the rotating interface. Fit the final dome fasteners only after checking that no screw touches the moving ring.

Done when the head turns repeatedly through full revolutions in both directions, neutral stops creep, and the dome remains retained when gently lifted by its intended service points. Do not use the eye stalk as a lifting handle. The controller sets head speed, not a measured head angle.

## 12. Install and check audio

Fix the speaker to its body mount with the specified retainer. Keep both speaker terminals isolated from chassis ground. Wire the MAX98357A exactly as shown; its bridge speaker output has no grounded speaker lead. Confirm the gain resistor before applying power.

Play `hello.mp3` at low gain. Then test every sound button. Check for distortion, controller resets and motion pauses while audio plays. Keep gain within the speaker's 1 W limit and the logic supply budget. Warning phrases in the collection are available as sound effects; their filenames do not prove automatic event playback.

Done when all 24 files play on demand, speech is intelligible, sound does not reset the ESP32, and amplifier/speaker temperature stays acceptable during repeated use. Keep the speaker and amplifier wiring fixed in the body.

## 13. Run the stop tests before floor driving

Keep wheels lifted for this complete test. Arm and command slow motion. Release the drive button and confirm the command stops. Repeat and change browser tabs. Repeat and close the page. Repeat and disable the phone's Wi-Fi. Repeat and turn off the access point or station connection used for control. Measure the delay to removal of the drive signal; the firmware lease is 500 ms, and the exact task and I/O delay must be checked on hardware. Tire coasting after removal of power is not the same as a continued drive signal.

Turn the actuator switch off during a slow command. Both drive and servo power must be removed. Turn it on again. Movement must not resume until the operator explicitly arms again. Reset the ESP32 during a slow command and verify the same no-restart behavior. Check that a second browser cannot revive a stale command after a stop.

Test low-battery detection with a bench supply, not by repeatedly exhausting the actual battery. Follow the voltage thresholds in the electrical and firmware chapters. Restore normal voltage and confirm recovery still requires explicit arming. Temporarily disconnect the servo-controller communication while safely supported, and confirm the documented fault response. Reconnect with power isolated.

Done only when every stop case passes. Record the measured time and test setup. Do not move to floor testing with any unexpected restart or uncontrolled motion.

## 14. Close the shell and run a short floor test

Install the remaining panels in the mechanical sequence. Check the rear screen opening, switch access and service access. Tie fixed cables clear of wheels, arms, neck rotation, fastener tips and ventilation. Fit strain relief to removable-panel cables. Tighten the battery straps and perform a gentle push test to confirm the pack cannot shift.

Weigh the complete robot. Begin on a clear, level hard floor with an operator beside the physical stop switch. Use low speed and broad forward arcs. Do not begin with a stationary pivot, carpet, ramp or threshold. The specified tires can create more steering resistance than these small motors can overcome. Stop immediately if a wheel stops turning while commanded.

Run for one minute, isolate power and inspect joints, cables, tires, motor temperature and converter temperature. Repeat for five minutes, then fifteen minutes if the earlier test passes. Record battery voltage, mass, floor type, speed setting, current and temperatures. A conservative commissioning gate is to stop testing at 50 C measured on a motor, servo or nearby printed mount, or on any sign of softening, odour or repeated electrical shutdown. This is a build-test threshold, not a replacement for manufacturer component ratings.

Done when the fully dressed robot drives, steers in moving arcs, moves both arms, turns the head, plays audio and stops correctly under the same measured load. This is the first physical proof of the design's operating envelope.

## 15. Charge, maintain and store

Switch off and disconnect the robot from the battery before charging. Use the specified Bioenno charger on the pack's charging connector. Do not charge through the ESP32, an Adafruit single-cell charger, or a converter output. Charge on a stable nonflammable surface with ventilation. Follow the battery manufacturer's limits and instructions.

Before each use, check the straps, wheel fit, arm horns, head retention and exposed wires. Test the physical stop switch and release-to-stop behavior. Stop use if the battery is damaged or swollen, a connector is discoloured, a motor binds, or a printed bracket cracks. Replace a damaged structural part rather than gluing across a loaded fracture.

Do not carry the robot by an arm, the eye, dome decoration or removable panel. Lift from the chassis with battery power isolated. Keep the wheels free of hair and thread. Store the battery disconnected according to its manufacturer's guidance. Keep a copy of the calibrated firmware settings with the robot.

## Fault guide

- Screen works but movement is blocked: check actuator switch state, pack ADC calibration, PCA9685 response, explicit arming and command timeout. Read the displayed fault before changing code.
- Controller resets when a motor starts: check rail sag, common ground, motor capacitors, converter load and connector resistance. Do not disable brownout protection.
- One wheel turns backward: isolate power and swap that motor's two bridge leads. Check all four wheels again while lifted.
- Arms buzz or fail to circle: check horn centres, direction calibration, gimbal contact, servo supply and 5 V signal buffers. Reduce amplitude while diagnosing the fit.
- Head creeps at stop: recalibrate the continuous servo neutral. If it binds only at one angle, inspect bearing alignment, fastener intrusion and dome clearance.
- Robot moves straight but will not pivot: use moving arcs and a lower-friction floor. Measure mass and current. Do not raise motor voltage or remove current limiting.
- Audio is missing: confirm both firmware and LittleFS were flashed, inspect the sound list, verify I2S pins, and check speaker wiring and amplifier gain.
- Home network fails: join the local AP and follow the firmware recovery instructions. Reconnection must not restart motion.

## Physical test record

Record date, builder, firmware commit, slicer profile, material, loaded mass and floor type. For each stage above, write PASS or FAIL with the measured result. Include supply voltages under simultaneous load, pack-voltage calibration error, stop delay, fifteen-minute temperatures and observed runtime. Until that record exists, the package remains a digitally checked design for a first prototype.
