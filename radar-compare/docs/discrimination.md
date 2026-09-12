# Telling a human from a pet from a box

The discriminant that works on this budget is **height above the floor, gated by warmth**. Thermal
answers "is it alive". An absolute height answers "is it a person". Nothing cheap answers "is it a
cat or a dog", and the published methods that come closest need raw radar data that no module in
this catalogue emits. Design to that and the robot behaves correctly. Design to respiration rate, or
to a pet-immune motion sensor, and it will call a calm adult a dog. Five physically independent
discriminants exist at this price: surface temperature, sub-centimetre periodic body motion, gross
motion kinematics, geometry, and learned appearance.

## mmWave micro-Doppler: excellent in the literature, unavailable in the parts

Wavelength sets what a radar can see. Doppler shift for a radial velocity `v` is `f_d = 2v/lambda`,
and the phase written by a chest displacement `dx` is `4*pi*dx/lambda`:

| Band | Wavelength | Doppler per 1 m/s | Phase per 1 mm of chest motion |
| --- | --- | --- | --- |
| 24 GHz | 12.49 mm | 160 Hz | 1.01 rad (57.6 deg) |
| 60 GHz | 4.997 mm | 400 Hz | 2.51 rad (144 deg) |
| 77 GHz | 3.893 mm | 514 Hz | 3.23 rad (185 deg) |

Exact arithmetic from `c = 299 792 458 m/s`. That ratio is why 60 GHz displaced 24 GHz for
vital-signs work: an assumed 0.5 mm cardiac displacement - assumed, see the folklore note below -
writes a 72 deg phase excursion at 60 GHz against 29 deg at 24 GHz.

**Respiration rate does not separate a human from a dog.** Measured by IR-UWB radar against a contact
reference ([PMC7070589](https://pmc.ncbi.nlm.nih.gov/articles/PMC7070589/)), four resting beagles
breathe at 0.219-0.412 Hz, or **13-25 per minute**; five cats at 0.447-0.556 Hz, or **27-33 per
minute**. A resting adult sits near 0.35 Hz, about 21 per minute
([PMC6888617](https://pmc.ncbi.nlm.nih.gov/articles/PMC6888617/)). The popular "human 12-20, pet
20-40" heuristic holds for cats and panting dogs only, so `if respiration_rate > 20 then pet`
mislabels in both directions. The rate is *measured* well - over 95 percent against a contact
pressure sensor - but it is not discriminative. Heart rate separates better (human 60-100 bpm, dog
98-126, cat 119-173), yet it needs a sub-millimetre displacement, and the 1.54 percent error against
ECG came from **one beagle under isoflurane anaesthesia**; those authors state the method fails on
animals in motion. The chest displacements everyone repeats, 5-10 mm respiration and 0.5-1 mm
cardiac, are **unverified folklore**: the cited paper contains neither them nor the filter bands.

**Two published methods do separate a human from a pet, and both need the radar and the target
still.** The respiratory-and-heartbeat energy ratio (RHER) exploits the fact that a biped thorax
couples cardiac motion to the body surface differently from a quadruped one; humans scored
significantly higher than dogs, cats and rabbits on a XeThru/Novelda X4M02 IR-UWB radar, 7.29 GHz
centre, 1.4 GHz bandwidth, every subject at **1 m** - 10 humans, 5 dogs, 5 cats, 5 rabbits
([PMC6888617](https://pmc.ncbi.nlm.nih.gov/articles/PMC6888617/)). Those authors state it cannot
separate a person and a pet sleeping together. The second is a 19-feature set - energy, frequency,
wavelet entropy, correlation coefficient - cut to the top 8 by recursive feature elimination and fed
to an SVM ([EURASIP JASP 2021](https://asp-eurasipjournals.springeropen.com/articles/10.1186/s13634-021-00738-2));
its headline accuracy could not be retrieved past the publisher's auth redirect, so no accuracy
figure is quoted for it here.

**Gait classification works and costs time you do not have.** For a moving target the discriminant is
the limb spectrogram, not a rate. FMCW micro-Doppler reached **97.66 percent** on human versus dog,
horse and cow ([UCT MSc](https://open.uct.ac.za/items/a65e9cb0-dbae-4a9d-a830-5a1177c08b90)) -
outdoors, single-target, large animals. In a cluttered operational environment a GMM plus HMM on
mel-cepstrum coefficients reached **75 percent at 250 ms of dwell, rising to only about 90 percent at
1.25 s** ([Expert Syst. Appl. 2018](https://doi.org/10.1016/j.eswa.2018.02.019)). A robot braking
before a collision has 200-400 ms, the 75 percent end of that curve. Cadence alone is weaker again -
about 2 Hz human step rate against roughly 4 Hz footfall for a trotting small dog, with a jogger, a
walking dog and a child all inside the ambiguity band.

Three hard limits sit on top:

- **Static-clutter rejection deletes still people.** Every FMCW pipeline opens with a moving-target
  indicator that removes the zero-Doppler bin, where a standing person lives. On an Infineon
  BGT60TR13C, CA-CFAR after MTI detected quasi-static humans at **68.3 / 51.3 / 57.7 percent** across
  three subjects, OS-CFAR at 78.8 / 68.3 / 69.9 percent
  ([arXiv 2602.14001](https://arxiv.org/html/2602.14001)). One still person in three is missed, and
  the same filter deletes a sleeping cat.
- **Small animals fall below the detection floor.** A TI IWR6843ISK against a 3 kg, 400 mm dog in a
  4 m room: **46.1 percent sensitivity for one radar without tracking**, 75.2 percent tuned, 97.10
  percent only with **four radars fused and tracked**
  ([PMC10975529](https://pmc.ncbi.nlm.nih.gov/articles/PMC10975529/)). For scale, human RCS at 77 GHz
  is **-6.86 to -3.51 dBsm** (frequency-and-azimuth average, 2 adults, 4 garments, anechoic chamber,
  3.4 m, antennas 0.8 m, [JRC78619](https://publications.jrc.ec.europa.eu/repository/handle/JRC78619)).
  No published mmWave RCS for a cat or small dog was found by the source lane, which records the
  result of a search and not a proven absence; either way, do not invent one by scaling for mass.
- **A moving robot invalidates all of it.** MTI assumes a static sensor; on a driving robot every
  wall has Doppler, and the hobby modules run a fixed, non-compensated MTI in closed firmware.

**The blunt point: no DFRobot module exposes the raw data any of this needs.** From the output column
of `data/sensors.csv`, the C4001 family ($12.90-$13.90) emits target count, range, radial speed and
energy; the Fermion C4002 ($8.90) adds a per-gate energy bitmap; the C1001 60 GHz module ($29.00)
emits a posture, a fall flag and a **scalar** breathing and heart rate. The only spectral output in
the catalogue, from the 24 GHz 20 m distance sensor ($65.90), is a 126-bin range-FFT on a part marked
as not detecting static humans at all. **None emits a range-Doppler map, a slow-time IQ stream or a
spectrogram**, so every result above is unreachable from these modules at any budget.

## Thermal: says alive, and little about which

Thermal has one decisive advantage over radar and PIR: **it sees a motionless target.** A sleeping
cat is invisible to MTI radar and to PIR, and plain to a thermal array.

| Surface | Temperature | Condition |
| --- | --- | --- |
| Human forehead, bare | 36.2 +/- 0.16 degC at 20 degC ambient; 36.0-36.5 degC over 14-32 degC ambient | climate chamber, handheld IR imager |
| Dog femoral, short hair | 31.77 +/- 0.19 degC | 21 degC room |
| Dog femoral, long double coat | 28.14 +/- 0.31 degC | 21 degC room |
| Dog / cat ocular region | 32.3-36.9 / 33.9-37.3 degC | min/max **within one image of one animal**, not a cohort |
| Emissivity used in canine IRT | 0.95 | standard assumption |

Human [PMC9740153](https://pmc.ncbi.nlm.nih.gov/articles/PMC9740153/), animals
[PMC8944468](https://pmc.ncbi.nlm.nih.gov/articles/PMC8944468/), emissivity
[PMC10497125](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10497125/); all paper-verified.

**Fur is insulation, so a pet is barely warm.** A long-coated dog's flank at 28.1 degC is 6 K above a
22 degC room and **2 K** above a 26 degC summer room. Only eyes, nose, inner ear and paw pads run
near core temperature, and those are a few square centimetres. A human is easier only because bare
skin holds 36.2 degC almost independently of ambient - and a robot mostly sees clothing, not skin.
**Fill-factor dilution finishes the job**: a pixel reports about
`T_apparent = f * T_target + (1 - f) * T_background`, so a 30 degC cat filling a quarter of a pixel
against a 22 degC room reads 24 degC - inside the AMG8833's +/-2.5 degC accuracy band, and
indistinguishable from a laptop or a sunlit floor patch.

**Pixel count is therefore the whole specification.** Applying the simplified Johnson criteria (about
1 cycle to detect, 3 to recognise, 6 to identify; 1 cycle is about 2 pixels across the critical
dimension) to the computed footprint tables:

| Task | Grid-EYE 8x8, 60 x 60 deg, $44.95 | MLX90640 32x24, 55 x 35 deg, $74.95 |
| --- | --- | --- |
| Detect a human (2 px on a 400 mm torso) | out to about 5 ft | well beyond 10 ft |
| Recognise a human as human-shaped (6 px) | never, at any range | beyond 3 ft, comfortably at 10 ft |
| Detect a cat (2 px on 230 mm) | out to about 3 ft | out to about 10 ft |
| Recognise a cat as a cat (6 px) | never | out to about 5 ft |

**An 8x8 array is a warm-blob presence detector, not a classifier.** A 32x24 array is the cheapest
thermal part carrying a height-and-aspect classifier. Both fields of view above are horizontal by
vertical, not diagonal.

## Multizone ToF: the silhouette, and the zone counts it needs

ToF supplies the metric quantity everything else lacks: **absolute height above the floor**, from the
zone elevation angle and the measured range. Three discriminants follow, most robust first.

1. **Full-column occupancy.** Below about 5 ft a human returns depth in every row of an 8x8 grid; a
   cat returns depth in the bottom one or two rows with free space above. A row-histogram threshold,
   not machine learning, and the most reliable cheap human/pet discriminant available. It needs the
   sensor low and pitched up, which a 600-1200 mm robot can do.
2. **Depth-profile rigidity.** A box gives a flat depth plane with near-zero frame-to-frame variance;
   a living body gives a curved surface with 10-40 mm of per-zone jitter from breathing and
   micro-sway. Per-zone variance over 1 s separates furniture from creature with no temperature or
   Doppler information at all.
3. **Top-of-return height**, which makes "is the top of this above 1.0 m" directly answerable.

Zone counts from `data/capability.json`, using the working figure of **45 x 45 deg horizontal by
vertical** (63 deg diagonal for the VL53L5CX, 65 deg for the VL53L8CX; the diagonal is separately
measured and cannot be converted):

| Part | 1 ft | 3 ft | 5 ft | 8 ft |
| --- | --- | --- | --- | --- |
| VL53L5CX 8x8, $19.95 | human 7.1 x 26.9 zones; cat 2.2 x 4.0 | human 2.4 x 9.0; cat 0.74 zone | past 1.30 m dark reach | - |
| VL53L8CX 8x8, $24.95 | human 7.1 x 26.9; cat 2.2 x 4.0 | human 2.4 x 9.0; cat 0.74 | human 1.4 x 5.4; cat 0.44 | human 0.89 zone |
| VL53L9CX 2268 zones, $80.39 | human 38 x 196; cat 11.9 x 28.8 | cat 4.0 x 9.6 zones | cat 2.4 x 5.8 | human 4.8 x 24.5 |

**8x8 gives a height profile, not a silhouette, past about 3 ft; a cat drops below one zone at 3 ft
and is unresolvable by 8 ft.** The 4x4 mode is a collision sensor only. ST's own people-counting case
study on this hardware reports 98.14 percent on a three-class problem - but from **32 successive
frames at 15 Hz**, a 2.1 s window, not a single frame.

Every reach in that table is the catalogue's **dark-room figure on a real target, not on a white
88 percent chart**: 1.30 m for the VL53L5CX and 2.45 m for the VL53L8CX, falling to 1.10 m and
1.55 m in sunlight (`data/sensors.csv`). The 4 m datasheet maximum belongs to a white 88 percent
target filling the field of view in the dark, and is not a room figure. A black cat is a
low-reflectance target and shortens all of them again.

## PIR: a wake-up, and a masking trick that does not transfer

A pyroelectric element outputs one scalar voltage proportional to the rate of change of incident
long-wave IR flux: no image, no range, no rate, no direction. It cannot classify, and it is *least*
sensitive to radial motion, so a person walking straight at the robot is its worst case. It also
does not see through glass, must not be aimed at a window, and responds to warm airflow - on a
mobile robot its own motor and driver heat, and the draught past the lens, are false-trigger
sources.

Alarm-industry "pet immunity" is a **geometric** trick, not a classification one, and it costs
nothing to copy: the Fresnel lens omits the lowest floor-looking beam layers, so an animal below the
lowest beam cannot trigger. The Bosch Blue Line Gen2 ISC-BPR2-WP12 rates two animals to 45 lb total
on a 77-zone, 7-layer lens - **mounted at 2.2-2.75 m**; the Resideo IS335 rates 80 lb. The mechanism
is entirely the mounting height: at 2.2 m, with the lowest retained beam taken to meet the floor at
12 m - an illustrative intercept, not a Bosch specification - that beam is still 1.10 m up at 6 m
range - above any dog, while catching a 1700 mm human.

**At 1.0 m on a robot the trick inverts.** The beam is then 0.50 m up at 3 m range, so a cat and a
human knee subtend similar depression angles, and the human's torso and head sit *above* the sensor,
outside a downward-fanning lens entirely: a pet-immune PIR on a low robot can see the pet and miss
the person. **Buy a plain PIR at $1.95-$3.95 as a near-zero-power wake-up, and put the height gate in
the ToF domain where a real elevation measurement exists.** The concept transfers; the part does not.

## Camera plus a person model: the only cheap true classifier

The advantage nobody states plainly: **COCO contains `person`, `cat` and `dog` as separate classes.**
Any stock YOLO or MobileNet detector trained on COCO does the whole discrimination out of the box,
with no custom dataset and no signal processing.

| Tier | Model and result | Compute cost |
| --- | --- | --- |
| MCU, no accelerator | TFLite-Micro person detection, MobileNetV1 a=0.25, 96x96, 325 KB: **about 86 percent** on Visual Wake Words (MLPerf Tiny floor 80 percent) | $5-15 |
| Purpose-built module | DFRobot SEN0626: faces and upper bodies to 3 m, 85 deg diagonal, offline | **$14.90** |
| SBC, CPU only | Pi 5, YOLO-nano class at 640x640 via NCNN: **7-8 FPS** | $80 |
| SBC plus NPU | Pi 5 + Hailo-8L, YOLOv8n: **136.7 FPS** at batch 8 | +$70 |

Three honest costs. **The MCU tier cannot do this**: the 325 KB model is binary person / no-person
with no pet class, and the SEN0626 outputs faces, upper bodies and gestures only. **Light**: a camera
in a dark room returns nothing, disqualifying at night unless IR illumination is added. **Privacy**:
a camera on a home robot is a materially different product, legally and socially. Copy the retired
Person Sensor's architecture - run the model on-device, emit only `{class, bbox, confidence}`, never
store or transmit frames - and write that constraint down before any code.

## Fusion: the decision table

Assumed stack: an 8x8 ToF pitched up with the sensor at 400 mm, a co-boresighted MLX90640 32x24, and
optionally a 60 GHz radar used **only after the robot has been stationary for 3 s**. Every threshold
is a calibration starting point, not a published value.

```
TOF    r       = median cluster range, m
       h_top   = h_sensor + r * sin(theta_zone_top)      # absolute height, m
       w       = cluster angular width * r               # m
       jitter  = stddev of per-zone range over a 1.0 s window, mm
       planar  = best-fit plane residual < 15 mm
THERM  dT      = peak cluster temperature minus 10th-percentile scene temperature, K
RADAR  rr      = dominant spectral peak, 0.1-0.7 Hz band, breaths/min   (stationary only)
```

| Class | h_top | w | jitter | dT | Robot action |
| --- | --- | --- | --- | --- | --- |
| COLLISION | any | any | any | any | Stop. `r < braking_distance`. ToF alone, never gated on class |
| OBJECT | any | any | < 8 mm and planar | < 1.5 K | Plan around it, no announce |
| HUMAN | > 1.20 m | > 0.25 m | any | >= 2.0 K | Yield, announce, slow to 0.3 m/s |
| PET | < 0.75 m | < 0.60 m | > 8 mm | >= 1.5 K | Slow, do not announce, widen clearance |
| UNKNOWN_LIVING | 0.75-1.20 m | any | any | >= 1.5 K | **Treat as HUMAN.** Crouching adult, toddler, large dog |
| UNKNOWN | any | any | any | < 1.5 K | Treat as obstacle, keep tracking |

Radar, when valid, only raises confidence on an existing call: `8 <= rr <= 26` with adequate peak SNR
confirms *alive*. The rate never selects the class, for the reason at the top of this chapter.

Three rules are embedded there. **Collision avoidance never waits on classification** - it runs on
raw ToF at frame rate, and classification changes behaviour, never braking. **Height is the primary
human/pet discriminant**, not temperature and not breathing rate. **The ambiguous band defaults to
human**, because the safe failure is over-classifying.

| Scenario | What fools it | Mitigation |
| --- | --- | --- |
| Person sitting still on a sofa | Radar MTI deletes them; PIR sees nothing | Thermal sees them; never trust radar or PIR for a still human |
| Long-haired dog, warm room | Flank only 2 K above ambient | Fall back to ToF height plus jitter |
| Laptop, radiator, sunlit floor | dT > 2 K defeats a thermal-only rule | Require `jitter > 8 mm` before calling anything living |
| Black cat | Low ToF reflectance, small thermal area | Accept reduced range; claim no untested dark-target distance |
| Robot's own motor heat | Thermal baseline drift | Use scene-relative dT, never absolute temperature |
| Robot in motion | All Doppler features void | Gate every radar feature on `robot_stationary` |

## The pairing that wins per dollar

**Multizone ToF plus a 32x24 thermal array: VL53L5CX at $19.95 plus MLX90640-D55 at $74.95, about
$95.** ToF gives metric height, width and rigidity but cannot tell warm from cold; thermal gives
alive-or-not but has no range and poor geometry. Together they answer will-I-hit-it, is-it-alive,
is-it-a-human and a usable is-it-a-pet, in darkness, with no camera and no privacy exposure. The
decision table runs entirely on that pair.

One disagreement to flag: the research lane's fusion table prices this pair at "about $20 plus about
$45", which is the AMG8833 8x8 - yet the same document's Johnson analysis concludes an 8x8 can
*never* recognise a human or a cat at any range. **Prefer the 32x24.** The 8x8 stays defensible as a
pure alive-or-not gate feeding ToF geometry, but only if described that way.

The runner-up is **ToF plus a camera running a COCO detector**, about $20 plus $150 of Pi 5 and
Hailo-8L. It wins on absolute capability - the only option here that separates cat from dog - and
loses on three counts: $150 of compute alone, about 1.6 times the price of the whole winning pair;
nothing returned in a dark room; and it
turns a home robot into a camera product. Choose it only if night operation is not required and the
privacy architecture is designed in from the start. Skip **radar plus ToF**, the weakest pair here:
both are geometric, and radar adds only closing velocity that frame differencing already gives.
**Thermal plus radar** does show a real gain - thermal-only mAP 0.527, radar-only 0.194, fused 0.644
([arXiv 2307.03623](https://arxiv.org/html/2307.03623)) - but from over $1000 of FLIR Boson 640 and
Vayyar vTrigB hardware.

## What is not achievable on this budget

1. **Cat versus dog without a camera.** No combination of ToF, a 32x24 thermal array and one hobby
   radar will do it; the published species work uses labelled datasets and per-installation training.
2. **Radar vital signs on a moving robot.** Ego-motion writes a Doppler bias orders of magnitude
   larger than a chest excursion. Stationary-robot feature only.
3. **Reliable small-animal detection from one mmWave radar.** 46.1 percent against a 3 kg dog, 75.2
   percent tuned, 97.10 percent only with four fused radars.
4. **Human detection through a standard static-clutter filter.** CFAR after MTI misses a still person
   roughly a third of the time.
5. **Any classification at collision-avoidance latency.** 75 percent at 250 ms of micro-Doppler
   dwell; 2.1 s for ST's ToF people counter; about 200 ms for the Person Sensor before filtering.
6. **A pet-immune PIR that is pet-immune on a robot.** The geometry needs 2.2 m of mounting height a
   600-1200 mm robot does not have.
7. **Raw radar signal processing from any module in this catalogue.** Every micro-Doppler result
   cited here needs a development board such as the IWR6843ISK or BGT60TR13C and the processing to
   go with it.
