# Assembly and commissioning

## Tools and build order

Use a Bambu H2D with 0.4 mm nozzle, dry PETG/PLA, calipers, square, flat
reference surface, protractor, metric drivers/spanners, torque tools,
multimeter, soldering equipment, ferrules, heatshrink and a current-limited
12 V bench supply. Metal fabrication also needs the machining/welding
capability specified in fabrication.md. A spring/luggage scale measures
rolling drag. Three platform scales help check balance. Use a temperature
probe for the loaded motor test.

Build and test the metal structure before committing to finish work.
The STL covers are not a substitute for the metal spines, shafts or foot
frames. Keep a build log with actual part masses, measured clearances,
calibration values, current, temperature and each acceptance result.

## Stage 1 - inspect and fabricate

1. Read the mechanical, fabrication and electrical chapters together.
   Inventory the actual motors, wheels, bearings, P16 and servo against
   the BOM. Check stock and dimensions before placing any order. All
   prices in the hardware list are allowances, not a fabrication quote.

2. Open the main CAD and the 18 PNG drawings. Mark forward Y on all three
   foot assemblies. Side-foot centers are X+/-165; rear placement is
   behind the body. The back foot must not be built as a forward foot.

3. Import the 13 cutting profiles in millimetres. Verify one known span
   with CAD measurement before cutting. Use the manifest's material,
   thickness and quantity. Apply the secondary operations in the
   fabrication worksheet rather than treating pilot holes as threads.

4. Make the two paired shoulder carriers, spines, guide crossbars,
   adapter and foot frames. Keep matching sets together. Check carrier
   hole alignment with a straight 12 mm reference shaft before coating.

5. Weld the steel T soles, stanchions, bridges and ankle/fork pieces in
   a square fixture. Keep weld beads out of the wheel envelopes. Check
   that both side uprights are square and the rear fork's gap is 16 mm.
   Correct metal distortion before installing plastic or bearings.

6. Finish the adapter socket, threads, crush sleeves, plain actuator pins
   and shaft hubs. Check all blind-hole depths and screw projection.
   Trial-fit the rod end to 21.5 mm engagement, then mark that position.

7. Dry-assemble the chassis base, side plates, corner blocks and head
   floor. Align all eight corner blocks before tightening. The head
   floor has separate motor and wheel clearances. Pass the actual head
   wheel through its intended swept space by hand.

8. Fit the two guide crossbars and square U-bolts. Install guide pads,
   then slide the inner tube by hand over the full intended range.
   There must be no hard spot or visible tube crushing. Retain each pad
   without any screw touching the sliding tube.

## Stage 2 - first-fit prints and feet

9. Print one drive cassette, head bearing tower/cap and head motor holder
   using the recorded H2D settings. Clear their supports and holes. Seat
   the actual components by hand. Correct a tight hole locally rather
   than scaling the whole part.

10. Set a steel foot frame on blocks with its wheel locations accessible.
    Bolt the cassette to the T sole with three M3x14 screws, washers and
    nuts. Keep the cable-tie slots open through both metal and plastic.

11. Put both TT motor cans toward negative Y, with axles at Y=-37/+37.
    Add thin foam beneath each case. Fit two cable ties per motor, away
    from rotating shafts and electrical terminals. Leave the ties loose
    until axle height has been set.

12. Press one specified wheel onto each shaft end while supporting the
    opposite end. Do not hammer the gearbox. Keep equal hub engagement
    and clearance to the case. The drawing uses nominal X+/-29 wheel
    centers; record the actual seating depth.

13. Place all four wheels on a flat reference surface. Adjust foam
    compression until both axles are at 31.5 mm. Tighten the ties without
    deforming the motor case. Turn every wheel and check the complete
    tire envelope, including the stanchion gap and power-cell cover.

14. Repeat for the other two feet. Mark motors M1/M2 left, M3/M4 right,
    M5/M6 rear. Each motor will have its own driver output pair, even
    though two motors on one foot share a direction command.

15. Bolt each metal side spine to its ankle upright with two M6 screws.
    Check the datum holes are at Z119/139. Tighten these as rigid joints.
    The shoulder, not the ankle, is the side-leg pivot.

16. Fit the rear servo to its four steel standoffs. Use uniform shims
    and the platform slots to center the shaft at X=-30,Y=-60. Set the
    installed horn top face to Z109.5 and ball-center plane to Z113.
    Keep the horn off until electrical neutral is set.
    Check servo, standoffs and mounting screws clear the tires.

## Stage 3 - shoulders and rear post

17. Fit the specified bearings in the metal shoulder housings. Bolt each
    housing to its carrier separately. Slide the ground shafts through
    the aligned bearing pairs; they must move without being forced.

18. Fit the inner/outer split collars in the stated locations. Put the
    split hubs and spine pads on the shafts. Check flush pad-screw heads,
    collar clearance and at least 1 mm from moving metal to each shell.
    Tighten clamps and apply witness marks across shaft/hub interfaces.

19. With the chassis supported independently, connect the inner guide
    tube to the adapter using its crush sleeves and two M5 cross bolts.
    Tighten against the sleeves, not the hollow tube walls.

20. Bolt on the moving yoke. Its plate sits behind the actuator's case.
    Fit the SA12E rod end and jam nut, preserving the marked engagement.
    Check both threaded and square sockets remain clear internally.

21. Put the spherical inner ring between the rear fork ears with its
    two 3 mm spacers. Install the specified shoulder axle bolt,1.3 mm head
    shim, outer washer and locking nut. The shoulder must not bottom
    before the spacer/inner-ring stack is clamped.

22. Move the supported frame through the allowed pitch and yaw by hand.
    The spherical joint must turn freely without the bolt, nut or rod-end
    shank striking the yoke. Keep at least two exposed threads beyond the
    nut and 1 mm minimum measured clearance to the neighboring actuator ear.

23. Install the detached P16 between its fixed and moving clevises with
    the stated 1 mm/2 mm eye spacers, plain 4 mm pins, outer washers and four
    retaining clips. Its case is outside the sliding guide. Do not use
    the actuator rod to correct a crooked guide or bracket.

24. Install the stationary limit rail and two SS-01GL switches in their
    actual mounting orientation. Check the 30 mm cam passes their levers
    without hitting the switch cases or fasteners. Leave adjustment
    screws accessible for the bench calibration stage.

25. Do not install the rear steering link yet. The body remains supported
    while the post is calibrated. The factory-retracted actuator is not
    a valid powered operating posture in the installed robot.

## Stage 4 - wire with power disconnected

26. Solder one 100nF capacitor directly across each of the seven motor
    terminals. Extend and twist the short motor leads, add strain relief,
    and fit separately labeled plugs. Insulate every exposed joint.

27. Build the main fuse and MAIN/RUN switch harness. Put F1 close to the
    discharge connector. Check the fuse values and wire gauge. Keep the
    factory battery connector intact and the pack unplugged.

28. Wire the five separate 5 V UBEC branches, logic converter and regulated
    12 V actuator branch. Fit the listed capacitors with correct polarity.
    Use a common ground distribution point. Verify no two positive
    converter outputs have been joined.

29. Wire D1-D4 from the circuit schedule. Keep the factory DRV8833 current
    limits. Connect each ground motor to its own channel and M7 only to
    D4 channel A. Ground unused D4 B inputs and insulate unused outputs.

30. On D5 only, remove factory R1/30k and fit 71.5k1 percent. Inspect and
    measure the replacement before attaching the actuator. A parallel
    resistor would set the wrong current limit.

31. Build U7 on the solderable board. Check DIP orientation, decoupling,
    all output enables and the unused channel. Follow the post NC-limit
    paths exactly, with 4.7k pull-downs at D5 after the switches.

32. Wire ADS1115 and INA219 at 3.3 V logic, addresses 0x48/0x40. Check the
    P16 orange/yellow/purple feedback wires separately from red/black
    motor wires. Measure continuity to each named terminal; do not rely
    on color alone.

33. Wire pack/RUN dividers, the amplifier and speaker. Neither speaker
    wire is ground. Keep the Feather BAT/JST empty. Fit and label the
    removable J_USB power link. Check all GPIOs against config.h.

34. Mount boards on nylon standoffs and the insulating panels. Use actual
    board holes as drilling templates where the general grid does not
    align. Retain UBECs, fuses and speaker independently. Add service
    loops, but keep every conductor away from shafts, wheels and the guide.

## Stage 5 - controller and detached actuator calibration

35. Unplug the pack and remove J_USB before connecting computer USB.
    Build with pio run -d firmware, then upload firmware and filesystem
    using pio run -d firmware -t upload and pio run -d firmware -t uploadfs.
    Use the actual controller's port if auto-detection is ambiguous.

36. Read the private 16-character AP password from the physical serial
    console at 115200 baud. Save it privately. Connect the phone to R2-24
    and open http://192.168.4.1. Test the STOP button. Do not expect
    arming while required sensors or valid actuator position are absent.

37. Remove USB, restore J_USB and use a current-limited 12 V bench supply
    in place of the pack for initial rail checks. Keep all ground motors,
    M7 and the steering servo unplugged. Confirm 5 V rails are 4.75-5.25 V,
    P6 near 12 V and sensor logic near 3.3 V before connecting their loads.

38. Keep the actuator/guide assembly detached from the robot and secured
    on the bench. Record its factory-retracted eye spacing and measure
    voltage at ADS1115 AIN0. Compute the initial zero count as round(V*8000).
    The firmware may latch an expected out-of-range fault at this position;
    do not bypass that installed-motion interlock.

39. For temporary bench control, unplug GPIO4/16 from U7 inputs 5/9.
    Leave their 10k pull-downs, both NC limits and all D5 pull-downs fitted.
    Use two normally-open momentary buttons from 3.3 V to U7 pin 5 or pin 9.
    Pressing one supplies extend or retract through the existing hardware
    limit. Release stops it. Insulate the disconnected ESP32 signal ends.
    Only the detached actuator is connected as a motor load for this test.

40. At low bench current, verify which button extends the rod. If wrong,
    correct the complete motor/direction/limit assignment before continuing.
    Do not merely relabel a reversed switch. Adjust LS_RET to open near 2 mm
    extension and LS_EXT near 80 mm, measured from the factory eye spacing.

41. Hold each limit open by hand and press its blocked-direction button.
    The motor must remain stopped. The opposite button must move away.
    Repeat for both switches. Verify the cam holds the switch open through
    the remaining mechanical travel, without bottoming the lever.

42. Stop at the measured 80 mm point and record AIN0 voltage/count. Set
    POST_ADC_ZERO to the recorded zero count and POST_ADC_FULL to
    ZERO+(COUNT80-ZERO)*100/80. This two-point extrapolation avoids driving
    into the 100 mm mechanical endpoint. Check intermediate 10/40/70 mm
    positions with a ruler; require position error within 1 mm.

43. Return the detached actuator to approximately 5 mm. Remove the temporary
    buttons and restore GPIO4/16 wiring. Disconnect power and reflash the
    calibrated firmware with the USB isolation procedure. Restart at 5 mm
    and verify a healthy status before installing the mechanism under load.

44. Reconnect the steering servo alone, center it electrically, and install
    the metal horn with its supplied center screw. Set the 12 mm crank and
    61.188 mm link length with the rear foot straight. Put the guide-end
    stud along X and horn-end stud along Z. Tighten both link jam nuts.

45. Check actual+/-8 degree rear yaw with a protractor. Adjust STEER_CENTER_US
    and STEER_US_PER_DEGREE to the measured servo, then rebuild if needed.
    Do not enlarge the yaw limit. Check link articulation and cover/harness
    clearance over all permitted body postures.

## Stage 6 - supported structure and motion tests

46. Support the three metal foot bridges on a suitable fixture with all
    TT wheels unloaded. The rear support must be positioned for the
    selected post length. Check the bare metal structure first with a
    small load, then with the intended 9 kg total design load.

47. Have the fabricator check the load path and fixture before a staged
    static proof up to the 27 kg equivalent 3x-gravity load. Apply the load
    through the stated body CG region and keep it supported against a
    tip. Do not apply this proof load through the TT gearboxes. Inspect
    for cracks, slipped witness marks and residual deformation after
    unloading; any such change fails the test.

48. With normal load and independent support available, test short held
    posture commands. Release must stop movement. Check upright, middle
    and maximum commanded tilt. Verify guide overlap, rod-end clearance,
    stable support and the measured current. Do not increase the current
    thresholds to overcome a jam.

49. Measure on-time and cooldown. A two-second move must reserve at least
    eight seconds off before a fresh press can move again. A target change
    during motion must stop and require release. Verify the phone's
    position/tilt display against measured geometry; tilt is calculated,
    not read from a physical angle sensor.

50. Test STOP, button release, phone focus loss and Wi-Fi disconnect during
    a short supported move. Check no motion resumes after reconnection.
    Disconnect feedback during a supported test and confirm a latched
    stop. Restore it only with power off and correct the cause before
    restarting. Measure actual stopping delay and displacement.

51. Remove proof load and lower only the intended normal robot weight onto
    its wheels. Reconnect ground motors. Lift the wheels for first polarity
    tests. Each pair must propel its foot forward on a forward command;
    correct calibration::DIRECTION or matched motor connections as needed.

52. Test straight motion and gentle turns on a level hard floor at the
    lowest useful speed. Measure each ground motor's steady current and
    temperature. Require no stalls and no more than 0.5 A steady per motor.
    Stop for rapid heat rise, binding, tire rub or abnormal gear noise.

53. Measure rear-foot rolling drag with a spring scale and normal load.
    Require 10 N or less. Check the robot can start repeatedly at the
    intended final mass. Weigh all remaining covers and electronics before
    claiming the final load test is complete.

## Stage 7 - final prints, head and finish

54. Print the remaining quantities in the manifest. Mirror only one outer
    foot in native X. Clean all supports and test each closed mesh's actual
    fastener access. Do not enlarge or cut away load-bearing metal to make
    a poorly cleaned plastic cover fit.

55. Fit the lower shell to the metal base and its captured seam nuts.
    Fit the complete upper shell before the shoulder carriers. Use the
    closed shoulder openings and the correct rear switch orientation.
    Tighten the four seam screws evenly, without crushing the locating lip.

56. Fit both complete leg skins over their metal spines and secure the
    six skin screws. Check the shoulder can swing without rubbing. Fit
    each whole foot cover to its four bridge bosses. Check screw tips,
    the power-cell housing, all tires and the rear linkage again.

57. Install the head bearing tower, both 608 bearings and 12 mm inner spacer.
    Add the nominal 0.8 mm upper inner-race shim stack and bearing cap.
    Fit the M8 bolt, lower inner-race washer and integrated dome rotor's
    captured nut. Adjust for free rotation without vertical play.

58. Fit M7 to its holder with foam and two ties. Fit its internal wheel.
    Bolt the holder to the metal floor, with the front screws beyond the
    wheel at Y45. Adjust tire compression to about 0.5-1 mm against the
    underside track. Turn the head by hand through a complete revolution
    before applying power; no metal plate or screw may enter the tire path.

59. Power M7 at low duty. Test both directions, release, STOP and lost Wi-Fi.
    Check drive traction and current without tightening the tire harder
    than needed. No wire may cross into the rotating dome. The decorative
    eye and display relief stay part of the single dome print.

60. Paint and label the covers, keeping fits and tire/track surfaces clean.
    Play all 16 original MP3s at low volume and check the speaker mount.
    Reweigh the finished robot, verify CG, repeat loaded driving/posture
    and stopping tests, and record runtime and temperatures. Keep the
    completed test log with the PDF. The design files alone do not prove
    that a built robot has passed these physical tests.

## Regular checks

Before each session, check both physical switches, battery straps, wheel
retention, shaft-clamp witness marks, pins, guide pads and harness loops.
Stop and investigate any new play or noise. Disconnect and remove the pack
for charging with its matched charger. Support the body before removing a
shoulder or actuator. Keep the calibrated firmware and recorded mechanical
measurements with the actual unit so replacement parts can be checked.
