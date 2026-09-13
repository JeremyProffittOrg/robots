# Factory control assembly — procurement candidate

This is a specification for quotation, not an available retail SKU, supplier acceptance, purchase order or tested assembly. BESTProto documents single-unit box builds with supplied boards, harnesses and power modules; exact acceptance and price are unconfirmed. See the first-party sources in printed-frame-research.md. No supplier has been contacted.

## Counting boundary

The 197-piece candidate requires one delivered, fully wired control assembly and seven Adafruit3777 motor assemblies with suppression capacitors fitted before delivery. The robot builder must not buy the internal loose components and count them as one piece. If built from loose parts at home, count every internal part and wire separately; that route exceeds the199-piece requirement.

The control assembly includes the populated printed carrier, attached power-switch pair in the supplied upper shell, regulators, drivers, amplifier, speaker, buffers, passives, fuse holders/fuses and complete terminated wiring. Supply the printed carrier and upper shell to the assembler after physical fit checks. All internal fasteners and insulation must arrive installed. The motor vendor or assembler must fit each100nF capacitor directly across its motor terminals and supply the motor as a finished assembly. Motor quantities remain seven; wheel quantities remain thirteen.

The full internal bill and wiring.csv remain part of the manufacturing package. This boundary does not conceal internal components. It defines what must actually arrive assembled for the external purchase count to apply. A bag of parts is not a finished assembly. Do not use the candidate count as a final completeness result until mating connectors, mounting hardware and the harness route are accepted against the actual robot.

## Required content

Use DFRobot Romeo DFR0994, ICStation11060, Pololu4984 and5573, Adafruit3190 and3006, Adafruit1313 speaker,74AHCT125 and Adafruit1609 Perma-Proto. Preserve the exact electronics/wiring.csv connections, wire gauges and polarities. Mount modules on cad/control-carrier.scad; its purchased envelopes allocate connector and component space and require checks against the delivered board versions.

Remove the Romeo VIN/VM link JP6 and fit PH/EN mode. Replace Romeo R9 with5.60k1% and R10 with2.00k1%; verify actual footprints before rework. Replace DRV8871 ILIM with71.5k1%. Document removed parts, replacement reference designators and resistance measurements. Set the motor regulator to5.70V before connecting Romeo VM. Servos use the separate6V Pololu5573, not the Romeo servo rail.

F1 and F2 are10A; F3 is2A. Fit strain relief near the battery connector and each moving foot. Provide separate labelled connectors for left/right/centre foot motor pairs, head motor, both servos, actuator drive/feedback, two travel limits, two lock sensors and floor probe. Connector housings, terminals, seals, sleeves and fastening parts belong in the internal manufacturing BOM even when included in the finished purchased assembly.

Use the five OmronSS-01 sensors specified in the mechanical ledger. Sensor mounting remains separate mechanical work. The loom must include mating terminations without requiring the builder to purchase additional loose contacts. GPIO43's1k resistor must be between the MCU and the switch-side pull-up. Keep camera, GDI and microSD disconnected. Include a photograph of every labelled Romeo header connection and JP6/PMODE configuration.

## Mechanical acceptance

The printed carrier occupies X±50,Y70..73,Z286..440. It installs in frame channels at X±47..57. Romeo sits at Y78; the motor regulator reaches Y106. The rear speaker envelope reaches Y40. Installed connectors, wire bends and restraints must fit the shell and clear the shoulder shaft, post, limit flag, lock carriage and head drive through their complete movements.

The supplier must return exact wire cut lengths and termination part numbers after a trial fit with the printed chassis and covers. Leave service loops only where the verified movement needs them. Do not route a loop across a guide, gear, pin or bearing. The final carrier is retained by two external M3x16 screws, counted separately. No new purchased piece may be added outside the finished assembly without updating the197-piece candidate.

## Electrical acceptance record

With motors disconnected, record every continuity and isolation result from wiring.csv. Verify MAIN off, RUN off, each fuse branch and VIN/VM isolation. Verify supply polarity before fitting boards. Test supply rails at battery-input voltages covering the operating range and record loaded voltage, input current and thermal rise. Do not infer output capability solely from a regulator's headline rating.

Open each travel switch and its cable in turn. Confirm the associated actuator direction is inhibited in hardware. Check both lock contact pairs, including both-open and both-closed faults. Check the floor input. Check GPIO43 during reset without driving the switch node outside its ratings. Verify P16 reference/wiper open-wire detection. Leave firmware potentiometer calibration marked uncommissioned; actual post measurements are completed on the robot.

Record oscilloscope checks of motor direction reversal, current regulation and the servo power rail. Test current sharing and motor temperature with the specified motors; one pair's current limit does not guarantee equal motor currents. A fuse protects wiring, not the printed mechanism or each parallel motor. Physical robot load, stability and endurance tests are separate from this electrical acceptance.

Deliver the finished assembly, final internal bill, as-built wiring and connector drawings, board revision photographs and signed test results. Until these exist, availability, price, fit and the completed under199-piece build remain unverified.
