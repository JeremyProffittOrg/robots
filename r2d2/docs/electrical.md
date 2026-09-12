# Electrical design and wiring

## Architecture and power

Revision C uses the original Adafruit HUZZAH32 3405. Six Adafruit 3777
motors drive twelve ground wheels. A seventh 3777 drives one internal 3766
wheel under the dome. The rear steering servo is Adafruit 1142. The rear
post uses an Actuonix P16-100-256-12-P with position feedback. No wire
crosses the rotating dome joint. Its display details are painted relief.

B1 is the protected Bioenno BLF-1206A 12 V / 6 Ah LiFePO4 pack, with its matched
14.6 V charger. Use its factory discharge and charge connectors. F1 is a
7.5 A fuse within 100 mm of the mating discharge plug. S1 MAIN feeds the
logic branch through F6/1 A. S2 RUN feeds six separately fused 2 A branches:
P1 left drive, P2 right drive, P3 rear drive, P4 steering/buffer, P5 head,
and P6 actuator. P1-P5 are separate Adafruit 1385, rated 5 V / 3 A UBECs. P6 is the
Pololu S13V25F12/4984 regulated 12 V converter. Never join converter outputs.

U6 Adafruit 4739 supplies 5 V logic/audio, up to 1.2 A. The Feather and sensors
use its logic branch. Do not power any motor or servo through the Feather.
The Feather BAT/JST socket stays empty. It is not a 12 V battery connector.
Join all ground returns at the battery-negative distribution point. Run
motor current through 18/22 AWG copper, not small PCB signal traces.

D1-D3 each provide two separate nominal 1 A current-limited DRV8833 channels.
Both channels on a foot share direction inputs, but each has its own motor.
Do not parallel motors onto one channel. Do not bypass the factory 0.2 ohm
sense resistors. D4 uses only channel A for the head, also with the factory
limit. Ground its unused B inputs; leave B outputs open. A low GPIO13
disables all four DRV8833 boards. Their open-drain fault outputs join at
GPIO36 with a10k pull-up to 3.3 V.

For supply sizing, allow 1.2 A per nominal 1 A motor channel, including
headroom rather than treating the nominal limit as exact. At5.25 V, seven
channels plus 2 A steering and 1.2 A logic give 60.9 W. With 85 percent assumed
converter efficiency and 11.2 V pack voltage, that is 6.40 A input. The 7.5 A
main fuse and 12 A-continuous pack exceed that budget. Actual branch peaks,
wire temperature and servo current must be measured. A stalled motor is
not a permitted continuous load. During post motion, ground drive and
head power commands are disabled. The actuator's roughly 12 W branch,
steering and logic therefore do not add to simultaneous ground-drive load.

The UBEC input range is 6-16 V, so the 14.6 V fully charged pack is suitable.
Use the input capacitors and short leads. Check every 5 V output is 4.75-5.25 V
before connecting loads. Verify P6 is near 12 V and never connect it to the
TT motors. The 72Wh nominal pack gives an estimated 2.0-3.3 hours at 15-25 W
average and 70 percent usable energy. This is an assumption, not a runtime
test. Measure runtime on the completed robot.

## GPIO and named nets

GPIO numbers refer to the ESP32, not physical header position.

- 14/32: left forward/reverse, D1 AIN1+BIN1/AIN2+BIN2.
- 15/33: right forward/reverse, D2 AIN1+BIN1/AIN2+BIN2.
- 27/12: rear forward/reverse, D3 AIN1+BIN1/AIN2+BIN2.
- 13: D1-D4 SLP. External 10k pull-down; low disables these motors.
- 36/A4: D1-D4 FLT, external 10k pull-up to 3.3 V.
- 25/A1: rear steering, through U7 AHCT125 channel 1.
- 26/A0 and 17/TX: D4 head AIN1/AIN2. Separate 10k pull-downs.
- 4/A5 and 16/RX: post extend/retract through U7 and independent NC limits.
- 21 and 22/SCL: configured I2C SDA/SCL. The default Feather SDA header
  is GPIO23, which this design instead uses for audio DIN.
- 39/A3: RUN sense via 10k/15k from P4 output.
- 34/A2: pack sense via 100k/22k from MAIN.
- 18/19/23: I2S amplifier BCLK/LRC/DIN.

GPIO12 is a boot-configuration pin. Keep its pull-down and add no pull-up.
GPIO34,36,39 are input-only. All GPIO inputs stay within 3.3 V. The 5 V buffer
outputs connect only to the servo and DRV8871, never back to the ESP32.

The 220-row wiring.csv and 12 connection sheets plus one power overview specify every connection,
including grounds. Each horizontal circuit line is one connection;
identical net names join across pages. Wire labels are authoritative.
Some signals are repeated on two functional sheets for context.

## Rear steering and independent post end limits

U7 must be 74AHCT125 DIP14. Pin 14 is P4/5 V, pin 7 ground, with 100nF directly
across them. Output-enable pins 1,4,10 go to ground. Unused enable pin 13
goes to 5 V; unused input pin 12 goes to ground; unused output pin 11 is open.
Do not substitute 74HC125. AHCT accepts 3.3 V control inputs at its 5 V supply.

Steering uses GPIO25 to U7 pin 2; pin 3 through 220ohm to SV1 signal. Servo
red goes to P4, brown/black to ground. Use a metal 25-spline horn with a12 mm
link radius and the supplied center screw. Calibrate the actual neutral
and pulse-to-angle response. Rear yaw is limited to 8 degrees each way.
The software converts this to roughly 20 degrees at the servo using the
61.188 mm linkage, rather than assuming horn angle equals foot angle.

Post extend uses GPIO4 to U7 pin 5, output pin 6 to LS_EXT COM, and LS_EXT
NC to D5 IN1. Post retract uses GPIO16 to U7 pin 9, output pin 8 to LS_RET
COM, and LS_RET NC to D5 IN2. Fit 4.7k from each D5 input to ground AFTER
the switch. Fit 10k pull-downs at both U7 control inputs. Opening a limit
or breaking its signal wire removes only that direction command. The
other direction remains available. This hardware gate does not depend
on the ESP32 reading a switch. Do not put a bypass jumper across a limit.

Use Omron SS-01GL gold-contact switches. They carry about 1.06mA at 5 V
through the 4.7k load, not actuator current. This meets the datasheet's
5 V/1mA reference minimum for the gold-contact family. Set LS_RET to open
near 2 mm actuator stroke and LS_EXT near 80 mm. Both are outside the 5.04-72 mm
normal operating range and inside the actuator's100 mm physical stroke.
NO terminals remain insulated and unused. The separate 30 mm cam stays on
each switch through the remaining end travel. Adjust the bracket and cam
depth so the lever is actuated without bottoming its mechanical travel.

Verify each limit with a meter first. Then, with the actuator detached
from the robot and supported, hold the switch open and request its blocked
direction: the motor must not run. Request the other direction: it must
run away. Repeat for the second switch. Do not swap motor polarity alone:
the named EXT/RET limits must still block their actual directions.

## Actuator driver, feedback and fault response

D5 is Adafruit 3190/DRV8871. Its manufacturer schematic identifies the
factory current-setting resistor as R1/30k. Remove that resistor and fit
71.5k1 percent on the provided resistor pads. Do not parallel the new
resistor with the old one. The TI formula is Itrip=64/Rk, giving 0.895 A
nominal. Using the 59-69kV datasheet range and 1 percent resistor tolerance
gives about 0.817-0.975 A. This limits the driver; it is not a force rating.

P6 VOUT feeds INA219 VIN+. INA219 VIN- feeds D5 VM and the 470uF25 V output
capacitor. D5 OUT1 goes to actuator red/pin 3; OUT2 to black/pin 4. Neither
motor lead is ground. Do not fit a single ordinary flyback diode across
this reversible motor. The driver's bridge provides recirculation.

Actuator orange/pin 1 is potentiometer ground, yellow/pin 5 is 3.3 V, and
purple/pin 2 is the wiper. Wiper goes through 1k to ADS1115 AIN0. Add 100nF
and 470k from AIN0 to ground. The pull-down makes a disconnected wiper
read near zero. Sensor supply and I2C logic are 3.3 V. ADS1115 ADDR is ground
for 0x48; unused analog inputs are grounded. INA219 address straps A0/A1
are ground for 0x40. Use the breakouts' installed I2C pull-ups, not 5 V pulls.

Firmware reads ADS1115 AIN0 continuously at 128samples/s with+/-4.096 V
range. INA219 uses the actual 0.1ohm shunt, calibration 4096 and 100uA current
LSB. It also reads back sensor configuration. Calibrate POST_ADC_ZERO and
POST_ADC_FULL with the detached actuator at its measured endpoints;
the defaults 0/26400 represent ideal 0/3.3 V and are not measured values.
Move the detached actuator to approximately 5 mm before installation.
A factory-retracted 0 mm position is deliberately outside the healthy
installed envelope. Disconnect motor power while changing calibration.

A posture button is held to move and released to stop. Motion requires
an armed command lease, healthy sensors/power, stopped drive/head and
centered steering. The controller stops for missing feedback, a position
outside 1.5-85 mm, current above 0.75 A for 200ms, no 0.15 mm progress in 750ms,
or 30 seconds travel. Faults latch until a power restart after the cause is
fixed. Static feedback failure is detected by the no-progress test while
moving; this is not a redundant position measurement.

P16 duty is 20 percent. Every move reserves an off interval four times its
on time. A new press during that cooldown is rejected; release and press
again after cooldown. A changed target during motion stops the actuator
and requires release. No post motion resumes after disarm or Wi-Fi loss.
The 500ms command-age limit is evaluated after bounded I2C transactions.
Loop timing and physical stopping distance must be measured on hardware.
The 2 second task watchdog is a separate response to a hung control task.

## Pack sensing, audio, USB and harness

MAIN through 100k to GPIO34, then 22k to ground, gives 2.633 V at 14.6 V pack
voltage. Add 100nF at the junction. Calibrate PACK_CORRECTION against a
meter. Motion cuts off below 11.2 V for one second and requires 12.0 V to
re-arm. Do not bypass the pack BMS. P4 through 10k to GPIO39, then 15k to
ground, gives 3 V RUN sense. Add 100nF there. Losing P4 power disarms motion.

U8 MAX98357 A VIN is 5V_LOGIC. Its speaker connects only between its two
speaker terminals; neither is grounded. GAIN goes through 100k to 5 V.
Retain initial firmware volume 0.22. Keep I2S wires short and away from
motor wiring. Original MP3s are included in the controller filesystem.

J_USB is a removable link between U6 output and the Feather USB power
pin. Remove this link and unplug the pack BEFORE using computer USB.
Otherwise two 5 V sources can back-feed. Flash and read the private Wi-Fi
password with the controller disconnected from robot power. Remove USB,
restore J_USB, then reconnect the pack. Never copy that password into a
public repository or wiring label. Phone control uses the local R2-24 AP.

Use 18AWG for the main distribution,22AWG for motor/servo branches and 26AWG
for signals. Twist motor pairs; place 100nF at each of the seven motor
terminals. Fit ferrules, insulated plugs, polarity labels and strain relief.
Leave a restrained service loop for 67 mm post travel,15 degree body motion
and 8 degree rear yaw. Verify it through the entire range by hand before
powering. Keep conductors clear of wheels, guide edges and shoulder shafts.

RUN off physically removes all motor and servo branch input power.
MAIN off also removes logic. These are manual disconnects, not brakes.
For charging, turn both off, unplug and remove the pack, then use its
factory charge jack and matched charger. Reinstall with padding and two
independent 20 mm straps. Do not open or modify the battery pack.

## Primary references

[DRV8833 pin guide](https://learn.adafruit.com/adafruit-drv8833-dc-stepper-motor-driver-breakout-board/pinouts),
[HUZZAH32 pin guide](https://learn.adafruit.com/adafruit-huzzah32-esp32-feather/pinouts),
[UBEC](https://www.adafruit.com/product/1385),
[logic regulator](https://www.adafruit.com/product/4739),
[SN74AHCT125](https://www.ti.com/lit/ds/symlink/sn74ahct125.pdf),
[DRV8871 datasheet](https://www.ti.com/lit/ds/symlink/drv8871.pdf),
[Adafruit driver schematic](https://github.com/adafruit/Adafruit-DRV8871-Breakout-PCB),
[Omron SS switch data](https://omronfs.omron.com/en_US/ecb/products/pdf/en-ss.pdf),
[P16 datasheet](https://www.actuonix.com/assets/images/datasheets/ActuonixP16Datasheet.pdf),
[12V converter](https://www.pololu.com/product/4984).
Prices and stock were checked or carried as explicit allowances in the
BOM on September 11-12,2026. No parts were purchased.
