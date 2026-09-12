# How each technology actually works, and what that costs you

Each candidate modality fails in a different place for a different physical reason. Each section
below gives the mechanism, separates what is measured from what is inferred, and names the one
advantage and the one defeat. Prices are USD list, one unit, read 2026-09-12. Geometry results are
cited from `coverage-geometry.md`, not re-derived here.

## SPAD direct time of flight, single zone and multizone

A vertical-cavity laser fires a short 940 nm pulse and an array of single-photon avalanche diodes
histograms the arrival times of the returning photons; the histogram peak is the range. Three
photon rates decide everything: signal rate, proportional to `rho * f_fill / d^2`, where `rho` is
reflectance at 940 nm and `f_fill` is the fraction of the cone the target covers; ambient rate,
independent of distance, quoted by ST in kcps/SPAD; and dark count rate, negligible indoors. The
part measures range per zone and nothing else - height, width, rigidity and class are all inferred
from the pattern of zone returns. In the signal-limited case SNR goes as the square root of
signal, so range scales as `sqrt(rho)`.

ST's own dark table confirms that law: the VL53L1X reaches 360 cm on an 88 percent white target and
170 cm on a 17 percent grey one, long distance mode, 100 ms timing budget, target filling the
27 deg diagonal field ([DocID031281 Rev 3, Table 6](https://www.pololu.com/file/0J1506/vl53l1x.pdf),
datasheet-verified). Grey costs 53 percent of the rated range, and ST's VL53L5CX footnote makes it
worse: that 17 percent Munsell chart "measured 13 % in IR at 940 nm". Fill factor compounds it.
Every ST range table except VL53L1X Table 9 specifies a target that fills the field of view, and
once a target is smaller than the cone its signal falls as `1/d^4` - the fourth-power law radar
obeys. The model `d_small = sqrt(d_cross * d_full)` puts the advertised 4 m VL53L1X at about 1.16 m
on a 40 x 400 mm chair leg of 88 percent white in the dark, and 0.52 m on the same leg at
200 kcps/SPAD, which is ST's roughly 100 kLux sunbeam case (computed). Fields of view,
horizontal x vertical: VL53L1X about 19 deg horizontal (27 deg diagonal), VL53L5CX and VL53L8CX
45 x 45 deg, VL53L7CX 60 x 60 deg.

- Best at: metric range at the lowest latency here, 52-147 ms in the stop path, against
  167-200 ms for scanning lidar and 255-380 ms for a thermal array.
- Defeated by: dark matte surfaces. Against black vinyl the VL53L5CX returned 18.8 percent valid
  measurements at 25 cm (peer-reviewed measured, Caroleo, Albini and Maiolino,
  [Sensors 26(5):1639](https://www.mdpi.com/1424-8220/26/5/1639)), and the failure appears as "no
  return", which a naive filter reads as clear floor.

## Scanning lidar

One rangefinder - direct time of flight on the RPLIDAR C1, triangulation on the A1 - is spun behind
a mirror at 8-12 Hz on the C1 and 1-10 Hz on the A1 (datasheet-verified), so all emitter power goes
into one narrow beam at a time instead of flooding a cone. It measures range and bearing in a single
horizontal plane; everything above and below it is unmeasured, not merely unclassified. The
concentrated beam shows up as reflectance
tolerance: the C1 is specified at 12 m on a white object under 70 percent reflection and 6 m on a
black object under 10 percent (datasheet-verified,
[Slamtec C1 rev 1.1](https://bucket-download.slamtec.com/datasheet/RPLIDAR_C1_Datasheet.pdf)), so a
7x reflectance change costs 2x range where `sqrt(rho)` predicts 4.5 m. Its ambient limit is
40,000 lux, against a VL53L1X collapse near a 25,000 lux equivalent - the only part here that
tolerates an indoor sunbeam.

- Best at: dense 360 deg range for the money - 0.72 deg resolution is 38 mm of arc at 10 ft, about
  6.5 hits across a cat (computed).
- Defeated by: the planar slice. No mounting height sees a lying cat at 120 mm, a human torso at
  1000 mm and a table top at 720 mm at once.

## mmWave FMCW radar at 24 and 60 GHz

The transmitter sweeps a linear chirp, the echo mixes with the outgoing sweep, and the beat
frequency is proportional to range while phase change across chirps gives radial velocity. Range
resolution depends on bandwidth alone, `dR = c / (2B)`: the 24.00-24.25 GHz ISM allocation is
250 MHz wide and gives a 600 mm range cell - 1.7 robot widths - while a 4 GHz sweep at 60 GHz gives
37.5 mm (computed; the HLK-LD2410 manual states 250 MHz and 0.75 m resolution,
datasheet-verified). Radar measures range, radial velocity and, with a MIMO array, coarse angle;
species is inferred from a micro-Doppler spectrogram and a trained classifier.

Detection range follows `Pr = Pt*Gt*Gr*lambda^2*sigma / ((4*pi)^3 * R^4 * L)`, so `R_max` scales as
`sigma^(1/4)` and a 15 dB cross-section deficit costs a factor of 2.37 in range, not 30. A module
rated 12 m on an adult still reaches 7.27 m against a 0.05 m^2 pet and 4.86 m against a pessimistic
0.01 m^2 pet (computed). The common claim of 3.5-4 m on a cat needs about a 20 dB deficit; the only
figure the sources put behind a cat is a geometric estimate of 11.3 dB, and the range lane calls
10-15 dB better supported than the pessimistic 15-20 dB. The files also disagree on human
cross-section: the range lane quotes a 79 GHz median of -11.1 dBsm, spread -20.7 to -4.8; the
discrimination lane retrieved both cited
sources, found neither contains those numbers, and withdrew them for
[JRC78619](https://publications.jrc.ec.europa.eu/repository/handle/JRC78619)'s measured
-6.86 to -3.51 dBsm, averaged over 76-81 GHz in an anechoic chamber at 3.4 m. Prefer the
withdrawal: it is a primary-source re-check, not a second assertion. No measured cat or small-dog
cross-section at either band exists in the sources.

- Best at: radial velocity, in the dark, through a chair back.
- Defeated by: its own ego-motion. Every clutter filter is a moving-target indicator that assumes a
  static sensor, and on a driving robot every wall acquires Doppler. Even stationary, conventional
  CFAR after that filter detected quasi-static humans only 51-79 percent of the time
  (paper-verified, [arXiv 2602.14001](https://arxiv.org/html/2602.14001)).

## Thermal infrared arrays

A microbolometer or thermopile array images the 8-14 um long-wave band, and each pixel reports the
apparent radiant temperature of whatever fills it. "Alive" and "human" are inferred from contrast,
shape and aspect ratio. The governing limit is pixel subtense: nothing smaller than one pixel
footprint can be resolved. An AMG8833 is 8x8 over 60 x 60 deg, so each pixel is 7.5 deg and covers
440 mm at 10 ft, making a 450 mm human torso 1.02 pixels wide; an MLX90640-BAB is 32x24 over
55 x 35 deg, 1.72 deg and 99 mm at the same range (computed from datasheet fields of view). Below
one pixel of fill the reading dilutes as `T_apparent ~= f*T_target + (1 - f)*T_background`, so a cat
that has gone sub-pixel on the AMG8833 at 10 ft reads about 2 K above room against the 8 K true
contrast of a clothed body at 30 deg C in a 22 deg C room (computed). Fur compounds that: a
long-coated dog's femoral region measures 28.14 +/- 0.31 deg C in a 21 deg C room
(paper-verified, [Animals 12(6):789](https://pmc.ncbi.nlm.nih.gov/articles/PMC8944468/)), a 6 K
contrast against a 22 deg C room that falls to 2 K against a 26 deg C summer room.

- Best at: seeing a motionless warm body. A sleeping cat is invisible to radar clutter filters and
  invisible to PIR, and plain to thermal.
- Defeated by: a warm room and a window. At 35 deg C ambient the contrast falls inside the
  MLX90640's own +/-2 deg C accuracy band, and long-wave IR does not pass ordinary glass, so the
  part needs a germanium aperture or an open hole in the shell.

## Single-point thermopiles

A single thermopile junction integrates long-wave IR arriving through a wide aperture and outputs
one temperature, or a presence flag derived from it. Unlike PIR it is DC-coupled, so it holds its
reading on a motionless body. It measures one scalar for the whole field: no position, no range, no
shape. ST's STHS34PF80 states its range with the condition attached, which is unusually honest -
"Reach up to 4 meters without lens for objects measuring 70 x 25 cm^2", 80 deg field of view
(datasheet-verified, DS13916 Rev 2). Scaled by the square root of area, a 25 x 20 cm cat comes to
about 2.14 m before any allowance for coat temperature (computed, then inferred).

- Best at: static presence for $14.95 and microamps.
- Defeated by: having one number. It cannot separate a person from a radiator, or say where either
  one is.

## PIR

A pyroelectric element behind a multi-facet Fresnel lens responds to the rate of change of incident
long-wave flux, and fires when a thermal contrast crosses a facet boundary. The output is one
scalar voltage: no image, no range, no direction. It is least sensitive to radial motion, so a
robot driving straight at a standing person is its worst geometry. Alarm-industry "pet immunity" is
a lens cut that removes the lowest floor-looking beams, not classification, and it works only
because the unit sits 2.2-2.75 m up (vendor-page-verified, Bosch ISC-BPR2-WP12). At 1.0 m on a
robot the geometry inverts: the pet stays in the beam and the person's torso rises above it.

- Best at: cost and power as a wake-up trigger, from $1.95.
- Defeated by: structural blindness to a still target, and by ego-motion - on a moving platform
  every scene changes, so the differential principle fires continuously.

## Ultrasonic

A piezo transducer emits a roughly 40 kHz burst and times the echo; range is half the round trip
times the speed of sound. It measures range along a wide cone with no bearing at all, and being
acoustic it does not care whether a surface is optically black, clear or mirrored. That is its
whole reason to be aboard: a ToF ranging through a glass door returns the distance to the pane.

- Best at: transparent and specular targets, for $3.95.
- Defeated by: soft targets and interleave latency. Most HC-SR04 units are unreliable on humans
  beyond about 1 m, below a 50 percent success rate, and crosstalk forces 33 ms between units, so
  eight sensors round-robin take 264 ms per sweep - about 3.8 Hz, far too slow for a stop path
  (vendor-page-verified).

## Camera plus on-device model

A lens forms a visible image on a CMOS sensor and a convolutional network run on-device emits class
labels and boxes. Nothing metric is measured: range, height and even presence are inferred from
pixels. The decisive fact is a dataset one - COCO carries `person`, `cat` and `dog` as separate
classes, so a stock detector discriminates human from pet from object with no custom labelling.
Compute sets the tier: the TFLite-Micro person detector is a 325 KB binary person/not-person model
at about 86 percent on Visual Wake Words (paper-verified), while a Pi 5 runs a YOLO-nano class
model at about 7-8 FPS on CPU and, with a $70 Hailo-8L, YOLOv8n at 136.7 FPS at batch 8
(vendor-page-verified).

- Best at: emitting a class label at all. Nothing else here answers "cat or dog".
- Defeated by: darkness. A camera in an unlit room returns nothing, and near-IR illumination is a
  different product with a different privacy argument.

## Summary

| Modality | Measures directly | Can never tell you | Cost per unit | The failure that ends the argument |
|---|---|---|---|---|
| SPAD dToF single zone | Range in one cone | Shape, class, anything outside the cone | $14.95 | Black matte target reads as empty space |
| SPAD dToF multizone | Range per zone, 8x8 | Temperature, velocity, class | $19.95-24.95 | Same, plus fill-factor range collapse on small targets |
| Scanning lidar | Range and bearing in one plane | Anything above or below the plane | $69-160 | The lying cat below the slice, the table top above it |
| 24 GHz FMCW radar | Presence and coarse range | Position inside a 600 mm range cell | $8.90-13.90 | 600 mm cell, and it detects the neighbour through plasterboard |
| 60 GHz FMCW radar | Range, radial velocity, coarse angle | Species without a trained classifier | $29.00 | Ego-motion Doppler destroys clutter rejection on a moving robot |
| Thermal IR array | Apparent temperature per pixel | Range, and shape below one pixel of fill | $44.95-74.95 | Warm room collapses contrast into the +/-2 deg C error bar |
| Single-point thermopile | One apparent temperature | Position, count, class | $14.95 | One scalar cannot separate a person from a radiator |
| PIR | Rate of change of IR flux | Anything about a still target | $1.95-9.95 | Structural blindness to a motionless person |
| Ultrasonic | Range along a wide cone | Bearing, class, soft targets past 1 m | $3.95-29.95 | 264 ms for an eight-sensor sweep, too slow to stop on |
| Camera plus model | Class label and bounding box | Metric range, anything in the dark | $14.90-150 | No light, no detection |

Read the last column as the design brief: each entry is a fail-to-danger mode with one physical
cause, so every one of them must be covered by a second modality whose physics is different.
