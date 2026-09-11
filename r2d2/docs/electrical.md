# Electrical design and wiring

## Architecture

B1 is a protected Bioenno BLF-1206A 12 V, 6 Ah LiFePO4 pack with its matched
14.6 V charger. Adafruit supplies the six required TT motors, wheels,
HUZZAH32 controller, three DRV8833 boards, four 5 V UBECs, logic regulator,
servos and audio hardware. The battery, DC-rated switches, fuses, bearings
and fasteners come from other suppliers where the required rating or
mechanical part is not provided by the selected Adafruit range.

The circuit sheets are point-to-point diagrams with named nets. Each
horizontal line is one electrical connection. Repeated net names join
across sheets. `electronics/wiring.csv` is the full connection schedule,
including all return wires. Do not interpret crossing text as a junction.
Use the power overview for architecture and the detailed sheets for pins.

Six motor bridge channels are used. D1 drives the left pair, D2 the right
pair and D3 the rear pair. Both channels on one driver receive the same
direction signals, but each motor connects to its own output pair. Never
connect two motors in parallel to one output pair. Retain the factory
0.2 ohm sense resistors, which set a nominal 1 A current limit per motor.
Do not solder the current-limit bypass jumpers.

## Power path

B1 positive passes through F1, a 7.5 A fuse within 100 mm of the mating
connector, then S1 MAIN. MAIN powers the logic branch through a 1 A fuse.
S2 RUN switches the input to four separate 2 A fused UBEC branches. P1,
P2 and P3 power left, right and rear drivers. P4 powers both servos and the
signal buffer. All grounds join the battery-negative distribution point.
The positive 5 V outputs remain separate; never parallel them.

The three motor rails each allow 2 A maximum under the driver limits,
which is below the UBEC's nominal 3 A capacity. Allocate up to 2 A for the
two servo actuators as a commissioning budget; their simultaneous loaded
current must be measured. Use the separate 1.2 A logic converter for ESP32
and low-volume audio. Avoid feeding the motors from the Feather USB pin,
3V pin, a solderless breadboard, or a small phone power bank.

At the conservative load budget of 30 W motors + 10 W servos + 5 W logic,
85 percent assumed conversion efficiency and 11.2 V battery voltage, input
current is about 4.73 A. The pack is rated 12 A continuous, and the main
fuse is 7.5 A. These figures size the supply; they do not permit stalled
motors or servos. The 72 Wh pack at an assumed 15-25 W average load gives
roughly 2.0-3.3 hours using 70 percent of nominal energy. This is an
estimate only. Measure real runtime and temperature on the finished robot.

The UBEC input specification is 6-16 V; the fully charged pack is 14.6 V.
Use the specified input capacitors, short power leads and no higher-voltage
pack. Check the actual UBEC label and output polarity before connection.
Output tolerance is about 5 percent; measure 4.75-5.25 V on each unloaded
rail. Stop if a motor rail exceeds 6 V. The Feather logic rail must remain
within its 5 V USB supply requirement; do not apply raw pack voltage.

## Pin map

U1 is the original HUZZAH32 3405, using ESP32 GPIO numbers:

- GPIO14 / 32: left forward / reverse to D1 AIN1+BIN1 / AIN2+BIN2.
- GPIO15 / 33: right forward / reverse to D2 AIN1+BIN1 / AIN2+BIN2.
- GPIO27 / 12: rear forward / reverse to D3 AIN1+BIN1 / AIN2+BIN2.
- GPIO13: all three SLP inputs; external 10k pull-down. Low disables drive.
- GPIO36 / A4: all three open-drain FLT outputs; 10k pull-up to 3.3 V.
- GPIO25 / A1: rear servo pulse through AHCT125 channel 1.
- GPIO26 / A0: head servo pulse through AHCT125 channel 2.
- GPIO39 / A3: RUN power sense from the servo 5 V rail through 10k/15k.
- GPIO34 / A2: battery ADC through 100k/22k from switched MAIN power.
- GPIO18 / 19 / 23: amplifier BCLK / LRC / DIN, respectively.

Each of the six motor input signals has a 10k pull-down. GPIO12 is an
ESP32 boot-configuration pin; do not attach any pull-up to it. GPIO34,36,39
are input-only, which is appropriate here. All logic is 3.3 V. No 5 V or
raw battery line connects directly to a GPIO. The Feather BAT/JST
connector remains empty; it is for a single-cell battery, not this pack.

## Servo and sense circuits

U7 is a 74AHCT125 DIP14, powered from P4 5V_SERVO on pin14, ground pin7.
Pin1 and pin4 output-enables go to ground. GPIO25 enters pin2 and exits
pin3 through 220 ohms to SV1 signal. GPIO26 enters pin5 and exits pin6
through 220 ohms to SV2 signal. Pin10 and pin13 are tied to 5V_SERVO to
disable unused channels. Pin9 and pin12 go to ground; outputs pin8 and
pin11 remain unconnected. Put a 100 nF capacitor at pin14/pin7 and a 10k
pull-down on each input signal. Check the notch before inserting the IC.
Use the exact AHCT type with inputs rated independently of VCC; do not
substitute HC logic or a board with undocumented input clamp circuits.

Servo red wires go to 5V_SERVO, brown/black to ground. Signal wire colors
can vary, so follow the servo label. The board sends neutral head pulses
while disarmed whenever RUN power exists. The rear steering holds its last
angle. A physical RUN-off removes motor and servo power independently of
the phone and firmware. It is a manual disconnect, not a certified safety
system or a brake. Test actual stopping distance at low speed.

For battery sensing, connect MAIN through 100k to GPIO34, then 22k to
ground. Put 100 nF from that junction to ground. At 14.6 V, the ADC sees
2.633 V nominal. Code scales by 122/22, cuts drive below 11.2 V for one
second, and requires at least 12.0 V to re-arm. Calibrate against a
multimeter using PACK_CORRECTION. The pack BMS remains the final battery
protection and must not be bypassed.

For RUN sensing, connect P4 output through 10k to GPIO39, then 15k to
ground, with 100 nF to ground. This makes about 3 V from a 5 V rail.
No movement can be armed until RUN sense, battery and driver-fault status
are healthy. A fault or lost heartbeat clears the movement lease; restored
power or Wi-Fi does not automatically re-arm it.

## Audio and USB

U8 MAX98357A VIN goes to 5V_LOGIC. GND goes to the common return. The
speaker connects only across U8's two speaker terminals. Neither terminal
goes to ground. Leave SD at the board default. Connect GAIN through 100k
to 5V_LOGIC for low gain, and retain firmware gain 0.22 for initial tests.
Use short I2S wires, ideally below 150 mm, and keep them away from motors.

A removable link J_USB connects U6's 5 V output to the Feather USB pin.
Remove that link and unplug the robot battery before connecting a computer
USB cable. Otherwise the two 5 V sources can feed each other. Flash and
read the initial private Wi-Fi password with the controller disconnected
from the robot power harness. Then remove USB, restore J_USB and reconnect
the battery. Label the link clearly. Do not rely on remembering which
source is connected.

## Harness and charging

Use 18 AWG stranded copper for main distribution, 22 AWG for motor/servo
branches and 26 AWG for signals. Fit ferrules to stranded wires in screw
terminals. Twist each motor pair and put a 100 nF capacitor directly across
the motor tabs. Add the listed electrolytics near their rails, observing
polarity. The supplied motor leads are short and thin; strain-relieve the
joint when extending them. Keep the six motors on separately labeled
two-pin plugs M1 through M6.

Leave a restrained service loop at the rear steering pivot for only
plus/minus 25 degrees, with enough slack for plus/minus 30. Route it clear
of the gears and spindle. No conductor crosses the head's rotating joint.
Secure fixed wires to the body rods and keep them away from wheel treads.
Never secure wires to a rotating shaft. No bare conductor may touch a rod.

Turn MAIN and RUN off, unplug and remove the battery before charging.
Use the factory charge connector and matched Bioenno LiFePO4 charger.
Do not charge through the Feather, USB link, motor wiring or a LiPo charger.
Do not open the battery pack or modify its BMS. Strap the battery in the
tray with padding and two independent hook-and-loop straps after charging.

## Sources

Primary references: [DRV8833 pin guide](https://learn.adafruit.com/adafruit-drv8833-dc-stepper-motor-driver-breakout-board/pinouts),
[HUZZAH32 pin guide](https://learn.adafruit.com/adafruit-huzzah32-esp32-feather/pinouts),
[UBEC rating](https://www.adafruit.com/product/1385),
[logic regulator](https://www.adafruit.com/product/4739),
[MAX98357A](https://www.adafruit.com/product/3006),
[Bioenno pack](https://www.bioennopower.com/products/12v-6ah-lifepo4-battery-pvc),
[TI SN74AHCT125 pin functions and ratings](https://www.ti.com/lit/ds/symlink/sn74ahct125.pdf).
Exact purchased parts and price allowances are in the BOM. Prices and
availability were researched on 2026-09-11 and are not a purchase quote.
