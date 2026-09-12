# What is detectable at 1, 3, 5, 8 and 10 feet

Capability falls off in steps, not smoothly. Each step has a different physical cause, and each
removes a whole class of sensor at once. This chapter walks the five survey distances in order: what
still reaches, what it resolves, what just dropped out, and what the distance is good for.

Three reference targets are used throughout, from
[range-capability-modelling.md](../research/range-capability-modelling.md): a human torso
450 x 700 mm, a cat or small dog 250 x 200 mm in side profile, and a chair leg 40 x 400 mm. Every
range figure below is for one of those targets, not for a wall filling the field of view. That
distinction is the whole chapter. Fields of view are horizontal x vertical unless "diagonal" appears.

## 1 ft / 305 mm - every optical modality works, radar does not

Every optical candidate returns something useful at 305 mm, with one standing exception: a thermal
array never sees the chair leg, at this or any distance, because furniture sits at room temperature.
A VL53L1X at about 19 deg horizontal
(27 deg diagonal) covers 103 x 103 mm here, so all three reference targets fill its field of view -
fill fraction 1.000 for human, cat and chair leg alike - and the reading is taken under the same
condition ST specifies for its 3.60 m dark-room figure (datasheet-verified,
[ST DocID031281 Rev 3](https://www.pololu.com/file/0J1506/vl53l1x.pdf) Table 6: white 88 percent,
100 ms timing budget, dark, target covers full FoV). That full-FoV condition is what 1 ft buys, and
it does not survive to 3 ft. The wider multizone fields are already partly unfilled at 305 mm: a cat
fills 0.78 of the VL53L5CX field and 0.40 of the VL53L7CX field.

- SPAD 8x8 multizone (VL53L5CX / L8CX, 45 x 45 deg): a human is 7.1 x 26.9 zones, a depth silhouette.
  A cat is 2.2 x 4.0 zones. A chair leg fills 0.48 of a zone - a valid range, no shape (computed,
  `data/capability.json`).
- Thermal AMG8833 (8x8, 60 x 60 deg): the pixel is 44 mm, so a human torso is 10.2 x 15.9 pixels and
  a cat 5.7 x 4.5 pixels. Both are full silhouettes.
- Scanning lidar (RPLIDAR C1, 0.72 deg at 10 Hz): 3.8 mm arc spacing gives about 65 returns across a
  cat and 29 across a human shin - but only if the scan plane sits below 250 mm.
- 24 GHz radar: a dead loss. The 250 MHz ISM allocation forces a 600 mm range cell
  ([Hilink LD2410 manual V1.03](https://www.hlktech.net/index.php?id=988), "Distance resolution
  0.75 m"), so 1 ft sits inside the first bin, and the DFRobot C4001's vendor-stated 1.2 m minimum
  measurable distance means it reports nothing here at all. A 60 GHz MIMO part (IWR6843 / IWRL6432)
  is the exception: a 4 GHz sweep gives a 37.5 mm range cell and a 51-77 mm cross-range spot at 1 ft,
  with micro-Doppler on top.

Use 1 ft for the emergency-stop ring, built on short-mode SPAD ToF: VL53L1X short mode holds 136 cm
dark and 135 cm at 200 kcps/SPAD, roughly full sun, because its narrow histogram window rejects most
ambient photons (datasheet-verified, Table 4).

## 3 ft / 914 mm - the flood illuminators start to thin

The VL53L0X (0.80 m on a real target in the dark), VL53L4CD (0.45 m) and wide-field VL53L7CX / L7CH
(0.80 m) all drop out before 3 ft, and the cause is fill factor, not raw sensitivity. Once a target
is smaller than the field of view, the fraction it fills falls as 1/d^2, so returned signal falls as
1/d^4 - the fourth-power law radar obeys. The crossover model gives a real reach of
`sqrt(d_cross * d_full)`. Against ST's dark-room numbers (dark, white 88 percent, long mode,
100 ms), a VL53L1X sold as a 4 m sensor reaches 2.45 m on a human torso, 1.55 m on a cat and 1.16 m
on a chair leg. Wide fields are worse, not better: the VL53L7CX spreads the same VCSEL power over
60 x 60 deg and manages 1.32 m on a torso under that same dark, white 88 percent condition.

Ambient light compresses all of it. ST Table 7 (long mode, 100 ms, full FoV) measures white
88 percent reach falling 360 cm dark, 166 cm at 50 kcps/SPAD ("a sunny day from behind a window"),
73 cm at 200 kcps/SPAD (the same with direct illumination on the sensor, about 100 klux equivalent).
On 17 percent grey it runs 170, 114, 68 cm - bright and dark targets converge on one 70 cm floor once
ambient dominates. In a sunbeam, no SPAD part here reaches 3 ft on anything in long mode. Short mode
is the single exception: it holds 135 cm at 200 kcps/SPAD, and it is capped there.

Thermal and lidar are untroubled: an AMG8833 puts a human at 3.4 x 5.3 pixels and a cat at
1.9 x 1.5 pixels, so aspect ratio still separates them; an MLX90640 55 x 35 deg gives 15 x 29 pixels
on the human; the C1 draws about 10 returns per shin.

Radar does not change across this step. A 60 GHz MIMO part still gives a human range, angle and
micro-Doppler, with a 37.5 mm range cell and a 153-230 mm cross-range spot at 3 ft. A 24 GHz ISM
module still has one 600 mm bin and, in the LD2410 class, no angle estimate at all.

Use 3 ft as the classification handoff - the last distance at which a cheap suite calls human versus
pet versus object with high confidence.

## 5 ft / 1524 mm - 8x8 thermal stops classifying

Two things end here. The AMG8833 falls to 2.05 x 3.18 pixels on a human and 1.14 x 0.91 pixels on a
cat, a one-pixel blob. The VL53L5CX is out on real targets, at 1.30 m reach in the dark.

| Sensor | Human | Cat | Chair leg |
|---|---|---|---|
| VL53L1X (19 deg H) | obstacle + range, dark only | marginal, dark only | out |
| VL53L8CX / L8CH (45 x 45 deg) | 1.4 x 5.4 zones, living vs not | 0.44 zone, range only | 0.10 zone, range only |
| VL53L9CX (55 x 42 deg, 2268 zones) | 7.7 x 39.2 zones, silhouette | 2.4 x 5.8 zones, living vs not | 0.51 zone, range only |
| MLX90640 BAB (55 x 35 deg) | 9.1 x 17.5 px | 5.0 x 5.0 px, pet vs human | not thermal |
| MLX90640 BAA (110 x 75 deg) | 3.3 x 7.2 px, pet vs human | 1.8 x 2.1 px, size only | not thermal |
| RPLIDAR C1 | about 6 hits per shin | about 13 hits | 2.1 hits |

Radar is not range-limited here. Received power scales with radar cross section to the first power
but maximum range only to its fourth root, so a 15 dB RCS deficit costs a factor of 2.37 in range,
not 30: a module rated 12 m on a human still makes 4.9 m on a 0.01 m^2 pet and 7.3 m on a 0.05 m^2
pet. What stops a hobby radar seeing a pet is the elevation pattern. A C4001 with a vendor-stated
100 x 40 deg beam, mounted 600 mm up and aimed level, puts its lower half-power edge on the floor at
1.65 m; a nearer cat is below the beam.

The sources disagree on RCS. `data/capability.json` carries 0.7 m^2 for an adult; the research lane
uses the EU Joint Research Centre's measured frequency-averaged mean of -4.3 dBsm, about 0.37 m^2, at
23-28 GHz ([JRC78619](https://publications.jrc.ec.europa.eu/repository/handle/JRC78619)). Prefer the
JRC figure: it is measured, where 1.0 m^2 is the top of RFbeam's vendor pedestrian band of 0.1 to
1 m^2, and 0.7 m^2 sits inside that band with no measurement behind it. No
measured pet RCS at 24 or 60 GHz was found, so every cat RCS here is inferred.

Use 5 ft for approach planning and for "is a person in the room", not for shape.

## 8 ft / 2438 mm - optical shape information is essentially gone

The VL53L1X and VL53L3CX drop out at 1.70 m on real targets in the dark. Only a white 88 percent
torso in a dark room takes a VL53L1X to 8 ft at all, and its 2.45 m clears 2438 mm by 12 mm, which
is not a margin to design to. What remains optically is single-zone
range from the TMF8801 and TMF8806, sub-zone fill from the TMF8820 / 8821 and VL53L8CX, and the
VL53L9CX, which still shows a human at 4.8 x 24.5 zones and a cat at 1.5 x 3.6 zones. Treat the
VL53L8CX row with suspicion: the catalogue credits it with 2.45 m dark-room reach, but the research lane could
not obtain ST's VL53L8CX ranging tables at all, so that figure is interpolated between the L5CX and
L7CX rather than datasheet-verified. Do not design to it.

Thermal splits cleanly. The MLX90640 55 x 35 deg holds a human at 5.7 x 10.9 pixels and a cat at
3.1 x 3.1 pixels, and still classifies. The AMG8833 does not: a cat covers 0.40 of one pixel, so the
pixel averages cat against cooler floor and the apparent rise falls to 3.23 K against an 8 K true
contrast. That clears the 0.05 C NETD easily, so the cat is detected - but it is indistinguishable
from a sunlit carpet patch or a laptop charger, and +/-2.5 C absolute accuracy gives no help. Reality
is worse: fur insulates, so coat surface temperature in a 22 C room is nearer 26-29 C than 34 C skin,
true contrast nearer 4-6 K, and the 8 ft apparent rise nearer 1.6-2.4 K once the same 0.40 fill
fraction is applied (inferred; the research lane states this case at 10 ft as 1.0-1.6 K).

Lidar thins the same way: 3.6 returns across a shin and 1.3 across a 40 mm chair leg, so any cluster
filter with a two-point minimum deletes the chair leg.

Use 8 ft for room-level awareness and path pre-planning, never for anything the robot must act on
inside a second. Thermal arrays are slow - the AMG8833 caps at 10 fps and the MLX90640's 0.1 K NETD
is specified at 1 Hz, which is 500 mm of travel per frame at 0.5 m/s.

## 10 ft / 3048 mm - presence, plus exactly one honest classifier

At 3048 mm an AMG8833 pixel covers 440 mm, so a 450 mm human torso is 1.02 pixels wide and 1.59 tall.
No shape survives; the array reports "something warm in that direction", which is what a two-dollar
PIR reports. Panasonic's "human detection distance: 7 m or less (reference value)" is not wrong. It
answers detection, not classification.

- SPAD ToF: gone, except the VL53L9CX at 3.8 x 19.6 zones on a human and one zone on a cat, and
  single-zone parts such as the TMF8806 that return a range with no shape.
- MLX90640 BAB: human 4.5 x 8.7 px, cat 2.5 x 2.5 px - the only thermal option in the study that
  classifies at 3 m. A 360 deg ring needs 7 units at $74.95, or $524.65 (vendor-stated, 2026-09-12).
  The 110 deg BAA variant needs 4 units but puts a cat at 0.92 x 1.03 px, sub-pixel, and was out of
  stock on the same date.
- Lidar: about 2.9 returns per shin, 6.5 across a cat, 1.0 on a chair leg - and it is a horizontal
  slice carrying no class information. A 110 mm circular return is a shin, a table leg or a sitting
  cat.
- Radar: 24 GHz gives presence and a 600 mm range gate, 1.7 robot widths. A 60 GHz MIMO part gives
  range to about 37.5 mm and a cross-range spot of 509-766 mm here. Classification needs a
  velocity-resolved micro-Doppler spectrogram and a trained classifier, which TI offers only in its
  high-performance mode, and which stops working the moment the animal holds still.

**The honest statement.** At 10 ft a hobby budget can know that something warm and low is over there
and roughly in which direction, and a $525 MLX90640 55 deg ring can add that the blob is pet-sized
rather than person-sized - but nothing in this price class can confirm that a stationary, sleeping
cat at 10 ft is a cat rather than a sunlit cushion, because the one channel that separates them, gait
micro-Doppler, requires the cat to move.
