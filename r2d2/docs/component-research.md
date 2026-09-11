# R2-D2 component research

Research date: 2026-09-11. Design target: 609.6 mm / 24 in overall height.
This is a digital design task. No hardware has been built or tested.

## Verified component facts

- [Adafruit 3777 TT motor](https://www.adafruit.com/product/3777): 3–6 V,
  1:48 gearbox. Adafruit measured 1.5 A stall current at 6 V. Listed stall
  torque at 6 V is 0.8 kg·cm. No encoder. Dimensions listed as 70 × 22 × 18 mm;
  use the linked mechanical drawing for shaft and mounting geometry.
- [Adafruit 3766 wheel](https://www.adafruit.com/product/3766): TT press fit,
  63 mm diameter, 29 mm width, 38 g per wheel. One wheel per order.
  Listed out of stock at the research date; do not substitute a different
  wheel without checking the CAD fit.
- [Adafruit 3297 DRV8833](https://www.adafruit.com/product/3297): two motor
  channels. Factory current limit is 1 A per channel. Keep that limit enabled.
  A motor pair needs separate channels, not parallel motors on one channel.
  [Pin guide](https://learn.adafruit.com/adafruit-drv8833-dc-stepper-motor-driver-breakout-board/pinouts):
  SLP defaults low; FLT is open drain. VMotor input has polarity protection;
  the VM pin does not. Shared logic and power ground is required.
- [Bambu H2D specifications](https://eu.store.bambulab.com/products/h2d):
  single-nozzle volume 325 × 320 × 325 mm; dual-nozzle volume
  300 × 320 × 325 mm. Use a conservative 300 mm cube per oriented part,
  then check brim clearance and excluded regions in Bambu Studio.

## Engineering implications — calculations, not measured performance

At 6 V the specified stall torque is 0.07845 N·m. Dividing by a 0.0315 m
wheel radius gives 2.49 N tangential force per motor at stall. Two wheels
on the same shaft share this force; they do not double the motor torque.
Stall is not a permitted continuous operating point. The driver current
limit, lower operating voltage, gearbox losses, floor grip, and scrub while
turning all reduce usable performance. A rolling chassis test with ballast
must precede decoration and final operation. Revision B integrates the
shell with the structural body, so it is part of the chassis test itself.

Twelve fixed wheels on three feet would resist turning. The rear support
needs a deliberate steering or swivel mechanism if that layout is selected.
The selected motor count also sets the battery and regulator current rating.
A large mAh label alone does not establish adequate motor power.

## Design assumptions after instruction to continue

2026-09-11, user: "continue". Proceed with six motors/twelve wheels,
phone Wi-Fi control and original synthesized beeps/whistles. These are
stated working assumptions, not verbatim confirmations of the earlier
multiple-choice questions. Detailed architecture and physical acceptance
criteria are in mechanical.md, electrical.md and assembly.md.

## Locked delivery instruction

2026-09-11, user: "email me the design pdf when doee"

Include a design PDF with the completed fabrication package and email the
PDF as an attachment after verification. Do not send a preliminary research
note as the completed design. Record the final email receipt in the shared
repository plan after the send succeeds.

Local Git configuration identifies the operator email as
`proffitt.jeremy@gmail.com`; use this recipient unless the operator supplies
a different address. Use the existing HTML status template and configured
SES identity in us-east-1, with an @jeremy.ninja sender. Delegate the send
and require the returned SES message ID as delivery evidence. No scheduled
task or background automation is authorized by this delivery instruction.

Email delivery is an addition to the original fabrication task. Complete
the digital package and identify physical validation limits in the email.
