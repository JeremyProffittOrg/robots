# Human vs Pet vs Object Discrimination — Theory and Method

**Lane:** `human-pet-object-discrimination`
**Platform assumption:** mobile robot, 350 mm square or 350 mm round footprint, 600–1200 mm tall, sensors mounted somewhere on that body.
**Date of all price and stock reads:** 2026-09-12.
**Document type:** method and theory. Sensor part selection is covered by other lanes; this lane says what each modality can and cannot *contribute to a classification decision*, and what the literature actually measured.

---

## 0. Corrections log — adversarial primary-source re-check, 2026-09-12

Every hard number in this document was re-checked against the manufacturer datasheet or the primary paper, not against the text that first asserted it. Four claims did not survive. They are corrected in place below and listed here so no reader has to find them:

| Claim as first written | Verdict | What the primary source actually says |
| --- | --- | --- |
| Human forehead "33.5–36.9 °C typical; 34.2 °C at 20 °C ambient" (§3.1) | **WRONG** | PMC9740153 measures **36.2 ± 0.16 °C at 20 °C ambient**; range **36.0–36.5 °C** across 14–32 °C ambient. The string "34.2" is not in the paper. |
| Human RCS "median −11.1 dBsm at 6.2 m; 90% between −20.7 and −4.8 dBsm; −7.7 to −3.0 dBsm across clothing" (§2.7) | **WRONG** | Neither cited source contains any of it. JRC78619 gives **−6.86 to −3.51 dBsm** (76–81 GHz freq/azimuth average, 2 adults × 4 garments, anechoic chamber, 3.4 m, antennas 0.8 m). arXiv 1910.13706 gives **−10 to +5 dBsm** co-pol for a *simulated walking* human. |
| "Dual-receiver + CNN, 99% / 83% / 68% at 2–3 / 6 / 10 classes", cited to Expert Syst. Appl. 2018 (§2.4) | **WRONG** | That paper is a **GMM+HMM on mel-cepstrum coefficients**, and reports **75% at 250 ms dwell rising to ≈90% at 1.25 s**. The CNN numbers are untraceable and are withdrawn. |
| Chest displacement "5–10 mm / 0.5–1 mm" and bands "0.1–0.5 / 0.8–3.0 Hz", cited to arXiv 2408.01951 and labelled paper-verified (§2.1) | **UNVERIFIABLE** | The cited paper contains no displacement amplitude and no filter band. Figures retained as folklore, relabelled unverified. |

Two further claims were **MISLEADING** rather than wrong — sourced correctly but stated without the condition that makes them meaningful — and now carry that condition: the dog/cat **ocular** temperature ranges (§3.1, min/max inside a single thermal image of a single animal, not a cohort statistic) and the **1.54% heart-rate error versus ECG** (§2.2, one beagle under isoflurane anaesthesia, not a cohort of anaesthetised dogs).

Everything else re-checked — the Doppler and phase constants, the dog and cat respiration and heart-rate ranges, the X4M02 and RHER study parameters, the 97.66%/97.5% micro-Doppler accuracies, the BGT60TR13C quasi-static CFAR figures, the IWR6843ISK small-dog sensitivities, the canine femoral temperatures and the 0.95 emissivity — **matched the primary source verbatim**.

---

## 1. The problem, stated correctly

"Detect a human, a pet, and an object" is three different questions, and conflating them is the single most common design error in hobby robot perception.

| Question | What it really asks | Cheapest modality that answers it |
| --- | --- | --- |
| (a) Is there something I will hit? | Is there a surface inside my braking distance? | Multizone ToF, ultrasonic, bumper |
| (b) Is it alive? | Does it have a body-temperature surface, or a periodic sub-centimetre motion? | Thermal IR, or radar vital-signs |
| (c) Is it a human? | Is its height profile, thermal area, gait or face consistent with a human? | ToF height profile + thermal area, or camera |
| (d) Is it a pet? | Is it a small, warm, low, fast-moving, non-rectangular thing? | Same fused stack as (c), inverted |

Critically: **no single hobby-budget sensor answers (d) reliably**, and several sensors that answer (a) beautifully contribute *nothing at all* to (b), (c) or (d). The discrimination is a fusion problem by construction, not a sensor-selection problem.

There are only five physically independent discriminants available at this price point:

1. **Surface temperature** relative to the room (thermal IR).
2. **Sub-centimetre periodic body motion** — breathing and heartbeat (radar phase).
3. **Gross motion kinematics** — velocity spread, limb count, cadence (radar micro-Doppler, or optical flow).
4. **Geometry** — height above floor, width, aspect ratio, rigidity (multizone ToF, stereo, structured light).
5. **Appearance** — texture and shape learned from data (camera + CNN).

Everything below is an assessment of how much each of those five carries, and where they fail.

---

## 2. mmWave micro-Doppler

### 2.1 The physics, with the constants

Doppler shift for a radial velocity `v` is `f_d = 2v/λ`. The wavelength sets everything:

| Band | λ | Doppler per 1 m/s | Phase shift per 1 mm of chest displacement (`Δφ = 4πΔx/λ`) |
| --- | --- | --- | --- |
| 24 GHz | 12.49 mm | 160 Hz | 1.01 rad (57.6°) |
| 60 GHz | 4.997 mm | 400 Hz | 2.51 rad (144°) |
| 77 GHz | 3.893 mm | 514 Hz | 3.23 rad (185°) |

*Confidence: derived, exact arithmetic from `c = 299 792 458 m/s`.*

This single table explains why 60 GHz displaced 24 GHz for vital-signs work: the same 0.5 mm cardiac chest displacement produces a 72° phase excursion at 60 GHz against 29° at 24 GHz. Chest-wall amplitudes of roughly **5–10 mm for respiration and 0.5–1 mm for heartbeat**, with processing bands of **0.1–0.5 Hz for respiration and 0.8–3.0 Hz for heartbeat**, are widely repeated in the radar vital-signs literature. **CORRECTION (adversarial re-check, 2026-09-12): this lane previously cited [arXiv:2408.01951](https://arxiv.org/abs/2408.01951) (Harmonic MUSIC Method for mmWave Radar-based Vital Sign Estimation) as the source and labelled it paper-verified. That paper contains none of these numbers** — it reports accuracy only (respiration-rate error < 3 breaths/min, heart-rate error < 5 bpm) and defines no displacement amplitude and no filter band. The two other papers cited in this lane were also checked: [PMC6888617](https://pmc.ncbi.nlm.nih.gov/articles/PMC6888617/) gives only a 5 Hz low-pass cutoff and example frequencies (respiration 0.35 Hz, heartbeat 1.35 Hz), and [PMC7070589](https://pmc.ncbi.nlm.nih.gov/articles/PMC7070589/) says only "high-pass and low-pass filtering were applied" without cutoffs. **Treat the displacement figures as unverified folklore, not a measured constant.** The commonly cited alternative in the older Doppler-radar literature is 4–12 mm respiration and 0.2–0.5 mm cardiac, which is a factor of two *lower* on the cardiac term than the value used below. *Confidence: **UNVERIFIED — no primary source located in this lane.** The 0.5 mm figure used in the next paragraph is therefore an assumption, and the phase excursion it implies is an upper bound.*

### 2.2 Respiration rate does NOT separate a human from a dog

This is the finding that most robot builders get wrong. Real measured numbers, from radar, against a contact reference:

| Species | Measured respiration | Measured heart rate | Source |
| --- | --- | --- | --- |
| Human (resting adult) | ~0.35 Hz (≈21 /min) | 1.0–1.67 Hz (60–100 bpm), general clinical range | [Sensors/IJERPH PMC6888617](https://pmc.ncbi.nlm.nih.gov/articles/PMC6888617/) |
| Dog (4 beagles, 9–13 kg) | 0.219–0.412 Hz (**13–25 /min**) | 1.63–2.10 Hz (98–126 bpm) | [PMC7070589](https://pmc.ncbi.nlm.nih.gov/articles/PMC7070589/) |
| Cat (5 cats, 2–5 kg) | 0.447–0.556 Hz (**27–33 /min**) | 1.99–2.88 Hz (119–173 bpm) | [PMC7070589](https://pmc.ncbi.nlm.nih.gov/articles/PMC7070589/) |
| Dog / cat, clinical resting | 15–35 /min (dog), 16–40 /min (cat) | — | [PDSA resting respiratory rate guidance](https://www.pdsa.org.uk/pet-help-and-advice/pet-health-hub/other-veterinary-advice/how-to-record-a-resting-respiratory-rate) |

*Confidence: datasheet-grade paper-verified for the radar rows; vendor/clinical-guidance for the last row.*

**A resting beagle breathes at 13–25 breaths/min. A resting human breathes at 12–20 breaths/min. The distributions overlap almost completely.** The commonly repeated "human 12–20, pet 20–40" heuristic is only true for cats and for panting or stressed dogs. Any decision rule of the form `if respiration_rate > 20 then pet` will call a calm human a dog and a calm dog a human.

Respiration rate itself was measured accurately: against a **contact pressure sensor** on an RM6240E acquisition system the paper states "the accuracy rate was over 95%", with per-animal errors of **1.5%, 1.9% and 4.8% for the dogs** and **0.7–2.9% for the cats**. *Confidence: paper-verified verbatim.*

**Heart rate separates far better than respiration rate** — human 60–100 bpm versus dog 98–126 and cat 119–173 — but heart rate requires resolving a sub-millimetre displacement, and the **1.54% error versus ECG was obtained on a single beagle under isoflurane gas anaesthesia**, not on a cohort of anaesthetised dogs. On awake, moving animals the heartbeat channel collapses. The authors state plainly that "the shortcoming of the proposed scheme was its inability to measure vital signs for animals in motion" and that the method's "practicality … was more reflected in the vital signs monitoring of at-rest pets".

Practical consequence for a mobile robot: **a moving robot cannot use vital signs at all.** The radar's own platform motion writes a Doppler bias across the entire scene that is orders of magnitude larger than a 5 mm chest excursion. Vital-signs discrimination is a *stationary-robot* feature only.

### 2.3 Feature-based human/animal separation that does work

Two families of published method, both requiring the radar and target to be still:

- **Respiratory-and-Heartbeat Energy Ratio (RHER).** Exploits the fact that a human thorax couples cardiac motion to the body surface differently from a quadruped. Humans showed significantly higher RHER than dogs, cats and rabbits. Hardware: XeThru/Novelda X4M02 IR-UWB, 7.29 GHz centre, 1.4 GHz bandwidth, subjects at **1 m**; 10 humans (22–35 y), 5 dogs (10–22 kg), 5 cats (1–3.5 kg), 5 rabbits (2–3 kg). Limitation stated by the authors: cannot separate a person and a pet sleeping together. ([PMC6888617](https://pmc.ncbi.nlm.nih.gov/articles/PMC6888617/)) *Confidence: paper-verified.*
- **19-feature / top-8 SVM.** Energy, frequency, wavelet-entropy and correlation-coefficient features, ranked by recursive feature elimination, top 8 fed to an SVM. Explicitly motivated by the fragility of single-feature methods to individual variation. ([EURASIP JASP 2021, 10.1186/s13634-021-00738-2](https://asp-eurasipjournals.springeropen.com/articles/10.1186/s13634-021-00738-2)) *Confidence: abstract-verified; the full accuracy table could not be fetched through the publisher's auth redirect — treat the headline accuracy as unverified in this lane.*

### 2.4 Gait and micro-Doppler classification accuracy

For *moving* targets the discriminant is the spectrogram, not a rate. Published accuracies:

| Study | Classes | Method | Accuracy | Caveat |
| --- | --- | --- | --- | --- |
| [UCT MSc, FMCW micro-Doppler](https://open.uct.ac.za/items/a65e9cb0-dbae-4a9d-a830-5a1177c08b90) | human vs dog, horse, cow | STFT spectrogram → PCA → two-stage SVM-SVM | **97.66%** (best of 16 two-stage combinations); 97.5% multi-class | Outdoor anti-poaching context; large animals, not house pets; radar frequency not stated in the record |
| Operational-environment micro-Doppler ([Expert Syst. Appl. 2018, DOI 10.1016/j.eswa.2018.02.019](https://doi.org/10.1016/j.eswa.2018.02.019)) | slow-moving animals vs humans | **GMM + HMM on mel-cepstrum coefficients** (not a CNN) | **75% at 250 ms dwell, rising to ≈90% at 1.25 s dwell** | Accuracy is a function of continuous time on target; cluttered environment |
| ~~Dual-receiver + CNN on 2D tensors, 99% / 83% / 68% at 2–3 / 6 / 10 classes~~ | — | — | **WITHDRAWN** | See correction below |

**CORRECTION (adversarial re-check, 2026-09-12).** This lane previously attributed a "dual-receiver + CNN on 2D tensors, 99% at 2–3 classes, 83% at 6, 68% at 10" result to the Expert Systems with Applications 2018 paper, and listed GMM+HMM as a secondary "same family" variant. That is backwards and the CNN numbers are not in the paper. The paper's own abstract, retrieved verbatim, reads: *"A combined Gaussian mixture model and hidden Markov model (HMM) is developed to distinguish between slow moving animal and human targets using mel-cepstrum coefficients… Results show that the classification accuracy of the model depends on the continuous observation time on target and ranges from 75% to approximately 90% for times on target between 250 ms and 1.25 s respectively."* The 99/83/68% figures could not be traced to any primary source in this lane and are **withdrawn**. *Confidence: abstract-verified verbatim via Semantic Scholar for the GMM-HMM row; the withdrawn row was **unverifiable**.*

Two honest readings of this table:

1. The 97%+ headline numbers are **human versus large quadruped (dog/horse/cow) in clean, single-target, outdoor scenes with a cooperative dwell**. A 350 mm robot in a cluttered living room is a different problem.
2. **Dwell time is the hidden cost.** Measured: **75% accuracy at 250 ms of dwell, rising to only ≈90% at 1.25 s** — so even a full second and a quarter of standing still buys one error in ten. A robot that must stop before it collides has 200–400 ms, which is the 75% end of that curve. **Micro-Doppler classification and collision avoidance operate on incompatible time budgets.** (The often-quoted "12.8 s / 256 slow-time samples" vital-signs window is a TI reference-flow figure that was **not verified in this lane** — the TI application note could not be located by document number; do not quote it as measured.)

### 2.5 Derived gait numbers — why cadence alone is a weak discriminant

Human preferred overground cadence is ≈120 steps/min = **2 Hz step rate** (stride ≈1 Hz); treadmill step frequency ranges 1.5 Hz slow to 2.4 Hz fast ([Sci Rep, PMC5435734](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5435734/)). *Confidence: paper-verified.*

For a trotting dog: stance time 0.21 ± 0.06 s (forelimb, 6.5 kg dogs at 0.9–1.1 m/s, [PMC5015230](https://pmc.ncbi.nlm.nih.gov/articles/PMC5015230/)) and trot stance fraction ≈42% of stride ([PMC4687030](https://pmc.ncbi.nlm.nih.gov/articles/PMC4687030/)) give stride time ≈0.50 s, i.e. **stride ≈2.0 Hz, footfall rate ≈4 Hz** (trot is two-beat). *Confidence: derived from two paper-verified inputs; not directly measured in either source.*

So the separation is roughly **2 Hz footfall (human) versus 4 Hz footfall (trotting small dog)** — a factor of two, which sounds usable until you notice a jogging human, a walking dog, and a child all land inside the ambiguity band. The literature does not classify on cadence; it classifies on the *whole spectrogram*, where the real discriminants are the number of independent limb Doppler tracks (2 versus 4), the torso-Doppler-to-peak-limb-Doppler ratio, and the envelope shape. That needs a CNN and a labelled dataset you do not have.

### 2.6 Why static-clutter rejection destroys all of this

Every commercial and open-source FMCW presence pipeline begins with a moving-target-indicator (MTI) or DC-removal stage — an exponential moving-average high-pass across slow time — because without it the range-Doppler map is dominated by walls, furniture and the sensor's own radome. That stage is *exactly* a filter that removes the zero-Doppler bin, which is where a standing or sitting person lives.

Measured consequence, on an Infineon XENSIV BGT60TR13C 60 GHz radar (1 TX, 3 RX, 10 Hz frame rate, wall-mounted at ~2.5 m, five quasi-static activities, three subjects): conventional CFAR detectors after MTI achieved only **68.3% / 51.3% / 57.7% (CA-CFAR)** and **78.8% / 68.3% / 69.9% (OS-CFAR)** per subject, while a percentile-gated range–azimuth method reached **93.2% / 92.3% / 94.8%** ([arXiv 2602.14001](https://arxiv.org/html/2602.14001)). *Confidence: paper-verified.*

Read that as: **the standard pipeline misses a still human roughly one time in three.** That is the cost of static-clutter rejection, and it is paid in exactly the situation a robot cares about — a person standing in a doorway not moving.

The same mechanism deletes pets: a cat curled asleep has near-zero bulk Doppler and a small radar cross-section, so it is removed as clutter and then run over.

There is a second, harsher version of this for a *mobile* robot. MTI assumes a static sensor. On a moving robot every wall has Doppler, so the clutter filter either has to be ego-motion compensated (needs good odometry, and is still wrong on rotation) or abandoned. Most hobby 24/60 GHz presence modules (Seeed MR24HPC1, MR60BHA2, DFRobot SEN0395 family) implement a fixed, non-compensated MTI in closed firmware and were never designed to move. **Expect a hobby presence module bolted to a driving robot to output near-continuous false presence.** *Confidence: inferred from the architecture; not measured in this lane.*

### 2.7 Radar cross-section: the small-animal detection floor

**CORRECTION (adversarial re-check, 2026-09-12).** This lane previously stated: *"Human RCS at 77 GHz, standing at 6.2 m: median −11.1 dBsm, with 90% of the fluctuation between −20.7 and −4.8 dBsm; frequency-and-azimuth-averaged across clothing types, −7.7 to −3.0 dBsm"*, cited to the JRC report and arXiv 1910.13706 and labelled paper-verified. **Both cited sources were retrieved in full and neither contains any of those numbers.** The median/percentile figures and the 6.2 m standoff are withdrawn. The corrected, source-quoted numbers are below.

**Measured — JRC / MOSARIM campaign, EMSL anechoic chamber, Ispra, August 2012** ([Fortuny Guasch & Chareau, *Radar Cross Section Measurements of Pedestrian Dummies and Humans in the 24/77 GHz Frequency Bands*, JRC78619](https://publications.jrc.ec.europa.eu/repository/handle/JRC78619), report text extracted directly from `lbna25762enn.pdf`). Conditions that make the numbers meaningful: **quasi-monostatic, vertical polarisation, antenna aperture to turntable axis 3.4 m, antenna height 0.8 m above ground, target rotated 0–360°, values are frequency-and-azimuth averages over the 76–81 GHz band.** Two adult male humans, four garments:

| Garment | Adult #1, 76–81 GHz | Adult #2, 76–81 GHz |
| --- | --- | --- |
| Summer shirt | −6.07 dBsm | −6.86 dBsm |
| Thick yellow PVC-polyester rain coat (250 µm) | −3.51 dBsm | −4.82 dBsm |
| Thin blue PVC-nylon rain coat (150 µm) | −5.22 dBsm | −6.59 dBsm |
| Multilayered winter parka | −5.43 dBsm | −6.43 dBsm |

So the correct frequency-and-azimuth-averaged human RCS range across clothing types at 77 GHz is **−6.86 to −3.51 dBsm**, not −7.7 to −3.0 dBsm. In the 23–28 GHz band the same eight measurements span **−5.60 to −3.76 dBsm**. The report's own conclusion on clothing: *"in most cases clothing did not impact significantly the RCS signatures observed"*, with the exception of very thick garments at 76–81 GHz. *Confidence: **paper-verified verbatim** from the report's Appendix D tables.*

For context on a *walking* human, [arXiv 1910.13706 (Deep et al., *Polarimetric Radar Cross-Sections of Pedestrians at Automotive Radar Frequencies*)](https://arxiv.org/abs/1910.13706) reports, from ray-tracing simulation validated against a 77 GHz automotive radar, that *"the co-polarization (vv and hh) components range from −10 dBsm to +5 dBsm"* over a full walking stride, with cross-polarisation *"weaker by approximately 10 dB"*. **These are simulated, per-frame, aspect-angle-dependent values, not a standing median** — they are not interchangeable with the JRC chamber averages. *Confidence: paper-verified verbatim.*

No published mmWave RCS figure for a domestic cat or small dog was found in this lane. This is an **unprovable negative** — it records the result of a search, not a verified fact, and a later search may find one. What it does license: **do not invent a value**, and do not scale the human figure by body mass.

What *is* measured: with a TI IWR6843ISK (60–64 GHz) in a 4 m × 4 m room, range set to 5 m, against a **3 kg, 400 mm tall small dog**, detection sensitivity was **46.1% for a single radar without tracking, 75.2% for a single radar tuned for both target types, and 97.10% for four radars with optimal fusion and tracking** ([Sensors 2024, 24(6):1901, PMC10975529](https://pmc.ncbi.nlm.nih.gov/articles/PMC10975529/)). The authors state the mechanism directly: small animals "generate fewer reflection points, even with a lower threshold," and a detector optimised for people will classify them as noise. *Confidence: paper-verified.*

That is the number to quote to anyone who says "just add radar": **one 60 GHz radar detects a small dog slightly less than half the time without tracking.** Four radars and a tracker get you to 97%. A 350 mm robot has room for four radars; it does not have room for the four radars *plus* the processing, at hobby cost.

---

## 3. Thermal IR

### 3.1 The temperature facts

| Surface | Temperature | Condition | Source |
| --- | --- | --- | --- |
| Human forehead | **36.0–36.5 °C** across 14–32 °C ambient; **36.2 ± 0.16 °C at 20 °C ambient**, 36.3 ± 0.16 at 24 °C, 36.4 ± 0.15 at 28 °C | bare forehead centre, climate chamber, Hikvision TBC-3117-3/U handheld IR thermal imager | [IJERPH, PMC9740153](https://pmc.ncbi.nlm.nih.gov/articles/PMC9740153/) |
| Human clothed torso | Lower than bare skin; the *clothing outer surface* is what a thermal array sees, not skin | varies with garment insulation and ambient | [Measurement of torso skin temperature under clothing, PubMed 3349991](https://pubmed.ncbi.nlm.nih.gov/3349991/) |
| Dog ocular region | 32.3–36.9 °C — **min/max inside one thermal image of one 4-year-old dog at rest, not a cohort range** | 21 °C controlled room | [Animals 12(6):789, PMC8944468](https://pmc.ncbi.nlm.nih.gov/articles/PMC8944468/) |
| Cat ocular region | 33.9–37.3 °C — **min/max inside one thermal image of one 4-year-old cat at rest, not a cohort range** | 21 °C controlled room | same |
| Dog femoral region, **short hair** | 31.77 ± 0.19 °C | 21 °C controlled room | same |
| Dog femoral region, **long double coat** | 28.14 ± 0.31 / 28.25 ± 0.23 °C | 21 °C controlled room | same |
| Emissivity used in canine IRT studies | 0.95 — *"An emissivity value of 0.95 was used."* | standard assumption | [PMC10497125](https://pmc.ncbi.nlm.nih.gov/articles/PMC10497125/) |

**CORRECTION (adversarial re-check, 2026-09-12).** This lane previously gave human forehead as *"33.5–36.9 °C typical; 34.2 °C measured at 20 °C ambient"* and labelled it paper-verified against PMC9740153. **The cited paper reports neither number.** Its measured forehead temperatures are 36.1 ± 0.07 (14 °C ambient), 36.0 ± 0.14 (16 °C), 36.2 ± 0.16 (20 °C), 36.3 ± 0.16 (24 °C), 36.4 ± 0.15 (28 °C) and 36.5 ± 0.18 °C (32 °C); the string "34.2" does not appear in it. The correction **strengthens** the thermal argument in §3.2 rather than weakening it: a bare human forehead sits at ≈36.2 °C almost independently of room temperature, so against a 22 °C room the forehead contrast is ≈14 K, not ≈12 K. It does not change the fur-insulation argument, which rests on the femoral numbers and those are confirmed.

*Confidence: paper-verified verbatim for every row; the two ocular rows are **MISLEADING as previously stated** and are now labelled with their real measurement condition (single illustrative thermal image, single animal).*

### 3.2 The two problems thermal has with pets

**Problem one — fur is insulation, so a pet is barely warm.** The dog femoral data above is the whole argument: a long-coated dog's flank reads **28.1 °C**, which against a 22 °C room is a **6 K** contrast, and against a 26 °C summer room is **2 K**. Only the eyes, nose, inner ear and paw pads are near core temperature, and those are a handful of square centimetres. A robot cannot count on seeing them.

**Problem two — a pet presents a small area, and small area on a coarse array means fill-factor dilution.** A thermal pixel reports approximately

```
T_apparent ≈ f · T_target + (1 − f) · T_background      (f = fraction of pixel filled)
```

A 30 °C cat filling 25% of a pixel against a 22 °C room reads 24 °C — a **2 K** rise. That is 8× the AMG8833's 0.25 °C temperature resolution but well inside its ±2.5 °C accuracy band, and it is indistinguishable from a laptop, a radiator, a sunlit floor patch, or a mug of tea.

### 3.3 Pixel footprint versus range — computed geometry

Linear footprint of one pixel at distance `d` is `d · 2·tan(FoV/2) / N`.

**Panasonic Grid-EYE AMG8833, 8×8, 60° × 60°** → 0.1443 · d per pixel.

| Range | Pixel footprint | Cat (230 mm tall, 400 mm long) | Human torso (400 mm wide) |
| --- | --- | --- | --- |
| 1 ft (305 mm) | 44 mm | 5.2 × 9.1 px | 9.1 px wide (fills frame) |
| 3 ft (914 mm) | 132 mm | 1.7 × 3.0 px | 3.0 px |
| 5 ft (1524 mm) | 220 mm | 1.0 × 1.8 px | 1.8 px |
| 8 ft (2438 mm) | 352 mm | 0.65 × 1.1 px | 1.1 px |
| 10 ft (3048 mm) | 440 mm | 0.52 × 0.91 px | 0.91 px |

**Melexis MLX90640-D55, 32×24, 55° × 35°** → 0.03255 · d horizontal, 0.02625 · d vertical.

| Range | H × V pixel footprint | Cat height in px | Human height (1700 mm) in px |
| --- | --- | --- | --- |
| 1 ft | 9.9 × 8.0 mm | 29 px | fills / overfills frame |
| 3 ft | 29.8 × 24.0 mm | 9.6 px | 71 px (overfills; V-FoV = 576 mm) |
| 5 ft | 49.6 × 40.0 mm | 5.8 px | 43 px (V-FoV = 960 mm, still overfills) |
| 8 ft | 79.4 × 64.0 mm | 3.6 px | 27 px (V-FoV = 1536 mm) |
| 10 ft | 99.2 × 80.0 mm | 2.9 px | 21 px (V-FoV = 1920 mm — a human just fits) |

*Confidence: derived arithmetic. The MLX90640-D55 55° × 35° FoV is [vendor-page-verified](https://www.adafruit.com/product/4407). The Grid-EYE 60° × 60° viewing angle is a **Panasonic AMG8833 datasheet** figure — re-checked 2026-09-12, the [SparkFun product page](https://www.sparkfun.com/sparkfun-grid-eye-infrared-array-breakout-amg8833-qwiic.html) (in stock, $49.95) does **not** state a viewing angle; it states only "detect human body heat at about 7 meters or less" and ±2.5 °C accuracy. Cite the Panasonic datasheet, not the reseller, for the FoV.*

### 3.4 Applying the Johnson criteria

Modern simplified thresholds are roughly **1 cycle for detection, 3 for recognition, 6 for identification**, at 50% probability; 1 cycle ≈ 2 pixels across the critical dimension ([Kintronics DRI explainer](https://kintronics.com/detection-recognition-and-identification-using-thermal-imaging-vs-optical-ip-camera/), [History and Evolution of the Johnson Criteria, OSTI](https://www.osti.gov/servlets/purl/1222446)). *Confidence: vendor/technical-note-verified; the criteria themselves are heuristics, not a datasheet spec.*

Run the pixel tables against that:

| Task | Grid-EYE 8×8 | MLX90640 32×24 (55°) |
| --- | --- | --- |
| Detect a human (needs ~2 px on 400 mm torso) | out to ~5 ft | well beyond 10 ft |
| Recognise a human as human-shaped (~6 px) | never — 8 rows cannot span a 1700 mm body with 6 px of detail at any useful range | ~beyond 3 ft, comfortably at 10 ft |
| Detect a cat (~2 px on 230 mm) | out to ~3 ft | out to ~10 ft (2.9 px at 10 ft) |
| Recognise a cat as a cat (~6 px on 230 mm) | never | out to ~5 ft (5.8 px) |

**Bottom line: an 8×8 array is a warm-blob presence detector, not a classifier.** It answers "is something warm in that direction" and nothing more. A 32×24 array can genuinely carry a height/aspect-ratio classifier, which is why it is the cheapest thermal part that contributes to discrimination rather than just detection.

Both arrays share a decisive advantage over radar and over PIR: **they see a motionless target.** A sleeping cat is invisible to MTI radar and invisible to PIR, and visible to thermal.

---

## 4. Multizone ToF silhouette

### 4.1 Zone geometry — computed

The ST VL53L5CX is specified at **63° diagonal** on ST's product page and **65° diagonal (45° H/V)** by Pololu; the VL53L8CX is **65° diagonal**. *Confidence: vendor-page-verified, with a genuine discrepancy between ST and Pololu that I have not resolved — treat 45° × 45° square FoV as the working figure.* Range is **up to 4 m**, 8×8 zones, up to 60 Hz; Pololu list price **$19.95** (read 2026-09-12, in stock) ([Pololu 3417](https://www.pololu.com/product/3417)). The datasheet's white-target/grey-target-versus-ambient table could not be extracted in this lane — **not verified here**; the reflectance-conditioned range numbers belong to the ToF hardware lane.

Full-frame width `W(d) = 2·d·tan(22.5°) = 0.828·d`; 8×8 zone pitch `= 0.1036·d`; 4×4 zone pitch `= 0.207·d`.

| Range | Full FoV span | 8×8 zone pitch | 4×4 zone pitch |
| --- | --- | --- | --- |
| 1 ft (305 mm) | 252 mm | 32 mm | 63 mm |
| 3 ft (914 mm) | 757 mm | 95 mm | 189 mm |
| 5 ft (1524 mm) | 1262 mm | 158 mm | 316 mm |
| 8 ft (2438 mm) | 2019 mm | 253 mm | 505 mm |
| 10 ft (3048 mm) | 2524 mm | 316 mm | 631 mm |

*Confidence: derived arithmetic.*

### 4.2 What that resolves

Reference dimensions: human 1500–1900 mm tall, 400–600 mm wide; cat 200–250 mm tall; dog 250–700 mm tall; a cardboard box is static, rectangular, and has a flat constant-depth face.

| Target | 3 ft, 8×8 | 5 ft, 8×8 | 10 ft, 8×8 | 10 ft, 4×4 |
| --- | --- | --- | --- | --- |
| Human height (1700 mm) | 17.9 zones — **overfills the frame**, all 8 rows occupied | 10.8 zones — still overfills | 5.4 zones of 8 | 2.7 of 4 |
| Human width (500 mm) | 5.3 zones | 3.2 zones | 1.6 zones | 0.8 zone |
| Cat height (230 mm) | 2.4 zones | 1.5 zones | 0.73 zone — **sub-zone** | 0.36 zone |
| Medium dog height (500 mm) | 5.3 zones | 3.2 zones | 1.6 zones | 0.8 zone |

The three usable ToF discriminants, in order of robustness:

1. **Full-column occupancy.** At ≤5 ft a human returns depth in *every* row of the 8×8 grid; a cat returns depth in the bottom one or two rows only, with free space above. This is the single most reliable cheap human/pet discriminant available, and it does not need machine learning — it is a row-histogram threshold. It requires the sensor to be mounted **low and pitched up**, which a 600–1200 mm robot can do.
2. **Depth-profile rigidity.** A cardboard box gives a flat depth plane across contiguous zones with near-zero frame-to-frame variance. A living body gives a curved, textured depth surface with 10–40 mm of per-zone jitter from breathing and micro-sway. Variance per zone over a 1 s window separates "furniture" from "creature" without any temperature or Doppler information at all.
3. **Height of the *top* of the return.** Combine the zone's elevation angle with the measured range and you get an absolute height above floor. `h = h_sensor + r·sin(θ_zone)`. This is a real metric quantity, not a learned feature, and it is what makes "is the top of this thing above 1.0 m" answerable.

Where ToF fails: **beyond ~8 ft the 8×8 grid can no longer resolve a cat at all** (sub-zone), and the 4×4 mode is a collision-avoidance sensor only — at 10 ft a whole adult human is under three zones wide. Also, 4 m is a hard ceiling regardless of zone count, and a black cat is a low-reflectance target, which shortens that further.

For comparison, ST's own AI people-counting case study on this hardware reports **98.14%** on a three-class in/out problem using 32 successive 8×8 frames at 15 Hz ([ST Edge AI case study](https://www.st.com/content/st_com/en/st-edge-ai-suite/case-studies/people-counting-with-a-ranging-sensor.html)). *Confidence: vendor-page-verified.* Note the input: a **2.1 s** temporal window, not a single frame.

---

## 5. PIR — detects both, classifies neither

### 5.1 Why it cannot classify

A pyroelectric element responds to the *rate of change* of incident long-wave IR flux on a single (or dual, or quad) element behind a Fresnel lens. Its output is one scalar voltage. There is no image, no range, no rate, no direction. It fires when a thermal contrast crosses a lens facet boundary. That is all the information that exists in the signal.

Two consequences that are frequently misunderstood:

- **PIR is least sensitive to radial motion and most sensitive to tangential motion.** A person walking *straight at* the sensor changes the flux slowly and produces a weak signal; the same person crossing the field at the same speed produces a strong one. A robot driving forward at a stationary person is the worst case for PIR. *Confidence: vendor/technical-note-verified — see the [pyroelectric motion-detection primer](https://www.electronicspecifier.com/products/sensors/motion-detection-using-pyro-electric-and-passive-infrared/) and US5291020.*
- **PIR does not see through glass** and must not be pointed at a window; it also responds to warm airflow. On a mobile robot, its own motor and driver heat, plus airflow past the lens, are false-trigger sources. *Confidence: vendor-guidance-verified.*

### 5.2 The pet-immune trick, and why robot builders should care

Alarm-industry "pet immunity" is a **geometric** trick, not a classification one, plus a secondary amplitude/pulse-count rule. The Fresnel lens is cut so the lowest, floor-looking beam layers are attenuated or simply absent, and the unit must be mounted high. Real product specifications:

| Product | Pet immunity rating | Mounting height | Lens structure | Price/source |
| --- | --- | --- | --- | --- |
| Bosch Blue Line Gen2 ISC-BPR2-WP12 | up to two animals, **45 lb total**, programmable | **2.2–2.75 m (7.5–9 ft)**, 2.2 m recommended | two Fresnel lenses, **77-zone 7-layer pattern**, plus a *selectable* 3-zone lookdown lens | [installation guide](https://manualzz.com/doc/33892839/bosch-blue-line-gen2-isc-bpr2-wp12-motion-detector-instal...) |
| Resideo IS335 | **up to 80 lb**, selectable | not stated on product page | not stated | [Resideo product page](https://www.resideo.com/us/en/pro/products/security/wired-sensors/motion-sensors/is335-pet-immune-pir-detector-40-ft-x-56-ft-is335/) |
| DSC LC-100-PI | pet immunity, weight rating **not extracted** (page returned empty to fetch) | — | — | [DSC](https://www.dsc.com/alarm-security-products/LC-100-PI%20-%20PIR%20Detector%20with%20Pet%20Immunity/93) |

*Confidence: vendor-page-verified for Bosch and Resideo; DSC not verified.*

The geometry, worked: a detector at 2.2 m whose lowest retained beam reaches the floor at 12 m sits at height `h(d) = 2.2·(1 − d/12)` above the floor at horizontal distance `d`:

| Horizontal distance | Lowest beam height | Intersects a 250 mm cat? | Intersects a 600 mm dog? | Intersects a 1700 mm human? |
| --- | --- | --- | --- | --- |
| 1 m | 2.02 m | no | no | no (over the head — the upper layers catch them) |
| 3 m | 1.65 m | no | no | **yes** |
| 6 m | 1.10 m | no | no | **yes** |
| 8 m | 0.73 m | no | **yes** (marginal) | yes |
| 10 m | 0.37 m | no | yes | yes |
| >10.6 m | <0.25 m | **yes** | yes | yes |

*Confidence: derived geometry from the vendor-verified 2.2 m mounting height; the 12 m floor-intercept is an illustrative assumption, not a Bosch specification.*

That table is the whole mechanism: **pet immunity is "the pet is below the lowest beam", and it works only because the sensor is 2.2 m up.**

### 5.3 Why this breaks on a 600–1200 mm robot — the finding this lane exists to state

Put the same lens at 1.0 m on a robot and redo the arithmetic, `h(d) = 1.0·(1 − d/6)` for a lens whose lowest beam meets the floor at 6 m:

| Horizontal distance | Lowest beam height |
| --- | --- |
| 1 m | 0.83 m |
| 2 m | 0.67 m |
| 3 m | 0.50 m |
| 4 m | 0.33 m |
| >4.5 m | <0.25 m |

The elevation separation between "cat at 3 m" and "human legs at 3 m" has collapsed, because at 1.0 m of sensor height both the cat and the human's knees subtend similar depression angles. Worse, the human's *torso and head* are now **above** the sensor and outside a downward-fanning lens entirely, so a pet-immune lens on a low robot can end up seeing the pet and missing the person — the exact inversion of what it was designed for.

**Recommendation:** do not buy a pet-immune PIR for a robot and expect pet immunity. Use a plain PIR as a cheap, low-power *wake-up* for the expensive sensors, and implement the height gate in the ToF or thermal domain where you have an actual elevation measurement. The pet-immune concept transfers to the robot; the pet-immune *part* does not.

---

## 6. Camera plus on-device ML

### 6.1 What each compute tier can actually run

| Tier | Example | Model | Result | Cost of the compute |
| --- | --- | --- | --- | --- |
| MCU, no accelerator | Cortex-M4/M7, ESP32-S3 | TFLite-Micro person detection: MobileNetV1 α=0.25, 96×96 input, 2 classes, **325 KB** model, ≤250 KB peak RAM, ≤60M MACs | **~86%** on the preprocessed MS-COCO Visual Wake Words test set; MLPerf Tiny closed-division floor is **80%** | $5–15 |
| Purpose-built module | DFRobot SEN0626 (Gravity Edge AI gesture + face) | closed on-module model | up to 10 faces / upper bodies, **3 m**, 85° diagonal FoV, I²C + UART, offline | **$14.90** |
| Purpose-built module (**retired**) | Useful Sensors Person Sensor SEN-21231 | ESP32-S3 + GC032A 0.3 MP, 110° FoV | faces only; ~7 Hz without recognition, ~5 Hz with; **~200 ms latency**; ~150 mW; bounding box + 0–100 confidence + ID 0–7 | was **$9.95**, **retired from SparkFun's catalogue**, discontinued at The Pi Hut |
| SBC, CPU only | Raspberry Pi 5 | YOLO-nano class, 640×640, NCNN | **~7–8 FPS** stock | $80 board |
| SBC + NPU | Pi 5 + Hailo-8L AI Kit | YOLOv8n, 640×640 | **136.7 FPS** at batch 8; ~431 FPS quoted for Hailo-8 at batch 1 | +$70 for the AI Kit |

*Confidence: [TFLite-Micro person detection](https://github.com/tensorflow/tflite-micro/blob/main/tensorflow/lite/micro/examples/person_detection/training_a_model.md) and [MLPerf Tiny](https://arxiv.org/pdf/2106.07597) paper-verified; [SEN0626](https://wiki.dfrobot.com/sen0626/) vendor-page-verified; [Person Sensor](https://github.com/usefulsensors/person_sensor_docs) docs-verified and [SparkFun retirement](https://www.sparkfun.com/person-sensor-by-useful-sensors.html) vendor-page-verified at 2026-09-12; [Hailo/Seeed benchmarks](https://wiki.seeedstudio.com/benchmark_on_rpi5_and_cm4_running_yolov8s_with_rpi_ai_kit/) vendor-page-verified.*

### 6.2 The decisive advantage nobody states plainly

**COCO contains `person`, `cat` and `dog` as separate classes.** Any stock YOLO/SSD/MobileNet detector trained on COCO does human-versus-pet-versus-object discrimination *out of the box*, with no custom dataset, no labelling, and no radar signal processing. That is a capability gap of an entirely different order from anything in sections 2–5. A Pi 5 + Hailo-8L at $150 of compute solves the classification problem that four fused mmWave radars solve at 97% and considerably more engineering.

Three honest costs:

1. **The MCU tier cannot do this.** The 325 KB Visual Wake Words model is *binary* person/no-person at ~86%. It has no pet class. Distinguishing cat from dog from box on a Cortex-M is not a solved hobby problem.
2. **Light.** A camera in a dark room returns nothing. The Person Sensor docs state outright that it "requires illumination" and that near-IR LED operation is uncharacterised. Thermal and radar do not care about light; a camera does. On a robot that operates at night this is disqualifying unless you add IR illumination, which then advertises the robot's presence.
3. **Privacy.** A camera on a mobile robot in a home is a materially different product from a thermal array on the same robot, legally and socially. The Person Sensor's design answer — no raw image egress, metadata only — is the right architecture, and it is worth replicating: run the model on-device, emit only `{class, bbox, confidence}`, never store or transmit frames. That is a design constraint to write down before any code, not a feature to add later.

---

## 7. Fusion — which pairs pay, and a concrete decision rule

### 7.1 Pairwise gain

| Pair | What one covers that the other cannot | Added cost | Verdict |
| --- | --- | --- | --- |
| **Multizone ToF + thermal array** | ToF gives metric height, width and rigidity but cannot tell warm from cold; thermal gives alive/not but no range and poor geometry. Together: height-above-floor **and** alive. | ~$20 + ~$45 | **Best discrimination per dollar at the non-camera tier.** Answers (a), (b), (c) and a usable (d). |
| **ToF + camera (COCO detector)** | ToF gives range and works in the dark; camera gives the class label. | ~$20 + ~$150 | Best absolute performance. Highest cost, light-dependent, privacy-loaded. |
| **Thermal + radar** | Measured: thermal-only mAP₅₀:₉₅ **0.527**, radar-only **0.194**, fused **0.644** (FLIR Boson 640 + Vayyar vTrigB 62–69 GHz) — [arXiv 2307.03623](https://arxiv.org/html/2307.03623) | high | Large relative gain, but from a $1000+ sensor pair, and radar-only is very weak on its own. |
| **PIR + anything** | PIR adds a near-zero-power wake-up and nothing else. | ~$3 | Worth it for power, worthless for classification. |
| **Radar + ToF** | Both are geometric; radar adds only "is it moving toward me" that ToF already gives by differencing frames. | ~$25 | **Weakest pair. Skip it.** Highly redundant. |
| **Radar + camera** | Radar adds range and darkness robustness to the camera. | ~$175 | Only if night operation matters *and* you already have the camera. |

Measured fusion anchors worth quoting: **four fused mmWave radars with tracking reached 97.10% small-dog sensitivity against 46.1% for one untracked radar** ([PMC10975529](https://pmc.ncbi.nlm.nih.gov/articles/PMC10975529/)); **infrared + mmWave semantic segmentation reached 83.21%** average accuracy on a 400 000-frame dataset ([MIRaSeg](https://link.springer.com/chapter/10.1007/978-981-95-5764-6_2), *abstract-verified only*).

### 7.2 A concrete decision-logic sketch

For a robot carrying an 8×8 ToF (pitched up, sensor at 400 mm), an MLX90640 32×24 thermal (co-boresighted), and optionally a stationary-only 60 GHz radar. All thresholds below are **starting points to be calibrated in situ**, not published values.

```
# Per frame, per spatially-clustered blob:

TOF:  r        = median range of the cluster, metres
      h_top    = h_sensor + r * sin(theta_zone_top)    # absolute height of top of return, m
      h_bot    = h_sensor + r * sin(theta_zone_bot)
      w        = cluster angular width * r             # metres
      jitter   = stddev of per-zone range over a 1.0 s window, mm
      planar   = true if best-fit plane residual < 15 mm

THERM: dT     = peak cluster temperature minus 10th-percentile scene temperature, K
       area   = count of pixels with dT > 1.5 K
       ar     = thermal blob height / width

RADAR (only while the robot is stationary >= 3 s):
       rr     = dominant spectral peak in 0.1-0.7 Hz band, breaths/min
       conf_v = SNR of that peak

# --- Tier 0: collision (never gated on classification) ---
if r < braking_distance(v_robot):
    STOP                       # ToF alone. No classifier is ever in this path.

# --- Tier 1: inanimate ---
if dT < 1.5 K and jitter < 8 mm and planar:
    class = OBJECT             # box, wall, furniture. Confidence high.

# --- Tier 2: human ---
elif dT >= 2.0 K and h_top > 1.20 m and w > 0.25 m:
    class = HUMAN              # tall + warm. This is the high-confidence human rule.
    if radar_valid and 8 <= rr <= 26 and conf_v > threshold:
        confidence = HIGH      # breathing confirms alive; the RATE does not
                               # separate human from dog, so do not use it to.

# --- Tier 3: pet ---
elif dT >= 1.5 K and h_top < 0.75 m and w < 0.60 m and jitter > 8 mm:
    class = PET                # low + warm + non-rigid
    # cat vs dog is NOT attempted: the thermal pixel count at >1 m does not support it.

# --- Tier 4: warm but ambiguous ---
elif dT >= 1.5 K:
    class = UNKNOWN_LIVING     # a crouching human, a child, a large dog, a heater.
                               # Behave conservatively: treat as HUMAN for safety.

else:
    class = UNKNOWN
```

Three design rules embedded in that sketch, each earned from the sections above:

- **Collision avoidance never waits on classification.** Tier 0 runs on raw ToF at frame rate. Classification runs slower and only changes *behaviour* (announce, yield, avoid), never *braking*.
- **Height is the primary human/pet discriminant, not temperature and not breathing rate.** Temperature says alive; height says which. Section 2.2 showed respiration rate cannot carry this load.
- **The ambiguous class defaults to human.** A crouching adult, a toddler, and a Great Dane all land in Tier 4. The safe failure is to over-classify as human.

### 7.3 The confusion cases that will actually bite

| Scenario | What fools it | Mitigation |
| --- | --- | --- |
| Person sitting still on a sofa | Radar MTI deletes them (68.3%/51.3%/57.7% CFAR detection in the cited study); PIR sees nothing | Thermal sees them. Never rely on radar or PIR for stationary humans. |
| Long-haired dog on a cool floor | Flank reads 28.1 °C — 2 K above a warm room | Increase thermal weight only in cool rooms; fall back on ToF height + jitter |
| Laptop, radiator, sunlit floor patch | dT > 2 K, defeats a thermal-only rule | Require ToF `jitter > 8 mm` (rigidity test) before calling anything living |
| Black cat | Low ToF reflectance shortens range badly; small thermal area | Accept reduced range; do not claim a detection distance you have not measured against a dark target |
| Robot's own motor/driver heat | Baseline drift on the thermal array | Use scene-relative `dT`, never absolute temperature |
| Robot in motion | Radar MTI invalid; all Doppler discriminants void | Gate every radar-derived feature on `robot_stationary` |

---

## 8. What is not achievable on a hobby budget — stated plainly

1. **Cat-versus-dog discrimination without a camera.** No combination of ToF, thermal 32×24 and one hobby radar module will do it. The published radar work that separates species uses labelled multi-hundred-sample datasets, long dwells, and classifiers trained per installation.
2. **Radar-based vital-signs discrimination on a moving robot.** Ego-motion destroys the 5 mm signal. The literature's own systems required at-rest subjects, a static radar, and 12.8 s estimation windows.
3. **Reliable small-animal detection from a single mmWave radar.** 46.1% without tracking, 75.2% tuned. That is the measured number against a 3 kg dog at ≤5 m.
4. **Human detection through a static-clutter filter.** The standard MTI pipeline misses a still person roughly a third of the time under CFAR detection.
5. **Classification at the same latency as collision avoidance.** Micro-Doppler gives **75% at 250 ms of dwell and only ≈90% at 1.25 s**; ST's ToF people-counter uses a 2.1 s window; the Person Sensor's own latency is ~200 ms *before* any temporal filtering. Build the architecture so braking never waits on any of it.
6. **A pet-immune PIR that is pet-immune on a robot.** The geometry that makes it work requires 2.2 m of mounting height you do not have.

---

## 9. Confidence summary

| Claim | Confidence |
| --- | --- |
| Doppler and phase-sensitivity constants (§2.1) | derived, exact |
| Dog 13–25 /min, cat 27–33 /min respiration, measured by X4M02 at 1 m | paper-verified |
| Dog HR 98–126 bpm, cat HR 119–173 bpm | paper-verified |
| Chest displacement 5–10 mm resp / 0.5–1 mm cardiac, bands 0.1–0.5 / 0.8–3.0 Hz | **UNVERIFIED — arXiv 2408.01951 does not contain these numbers; citation withdrawn 2026-09-12** |
| Dog respiration accuracy >95% vs contact pressure sensor, errors 1.5–4.8% (dogs) / 0.7–2.9% (cats) | paper-verified verbatim (PMC7070589) |
| HR error 1.54% vs ECG — **one beagle under isoflurane anaesthesia**, not a cohort | paper-verified verbatim (PMC7070589) |
| Micro-Doppler human-vs-animal 97.66% / 97.5% | abstract-verified (UCT repository record) |
| Operational micro-Doppler GMM+HMM **75% @ 250 ms → ≈90% @ 1.25 s** dwell | abstract-verified verbatim (ESWA 2018, DOI 10.1016/j.eswa.2018.02.019) |
| ~~Dual-receiver CNN 99% / 83% / 68% at 2–3 / 6 / 10 classes~~ | **WITHDRAWN 2026-09-12 — not in the cited paper, untraceable to any primary source** |
| CFAR-after-MTI quasi-static human detection 51–79% | paper-verified (arXiv 2602.14001) |
| Single radar 46.1% / four-radar-fused 97.10% small-dog sensitivity, IWR6843ISK | paper-verified (PMC10975529) |
| ~~Human RCS −11.1 dBsm median at 77 GHz, 6.2 m; 90% between −20.7 and −4.8 dBsm~~ | **WITHDRAWN 2026-09-12 — neither cited source contains these numbers** |
| Human RCS, freq/azimuth average 76–81 GHz, **−6.86 to −3.51 dBsm** across 2 adults × 4 garments, anechoic chamber, 3.4 m range, antennas 0.8 m | paper-verified verbatim (JRC78619 Appendix D) |
| Walking human co-pol RCS **−10 to +5 dBsm** at 77 GHz, ray-tracing simulation over one stride | paper-verified verbatim (arXiv 1910.13706) — *simulated, not a standing median* |
| **Cat / small-dog mmWave RCS** | **no value found — unprovable negative, records a search result not a fact** |
| Dog short-hair 31.77 °C vs long-coat 28.14 °C femoral, 21 °C room | paper-verified verbatim |
| Dog/cat **ocular** 32.3–36.9 / 33.9–37.3 °C | **MISLEADING as first stated** — min/max within a single thermal image of a single animal, not a cohort range |
| ~~Human forehead 33.5–36.9 °C typical; 34.2 °C at 20 °C ambient~~ | **WRONG — WITHDRAWN 2026-09-12.** PMC9740153 measures **36.2 ± 0.16 °C at 20 °C ambient** and 36.0–36.5 °C across 14–32 °C ambient; "34.2" does not appear in the paper |
| Thermal and ToF pixel-footprint tables | derived from vendor-page-verified FoVs |
| Johnson criteria 1/3/6 cycles | technical-note-verified; heuristic by nature |
| Bosch 45 lb pet immunity, 2.2–2.75 m mounting, 77-zone lens | vendor-page-verified |
| Pet-immune beam-height tables | derived; the 12 m and 6 m floor intercepts are illustrative assumptions |
| Visual Wake Words ~86% / MLPerf floor 80% | paper-verified |
| Person Sensor **retired**, was $9.95 (SparkFun, read 2026-09-12) | vendor-page-verified |
| DFRobot SEN0626 $14.90, 3 m, 85° diagonal, 10 faces | vendor-page-verified |
| YOLOv8n 136.7 FPS @ batch 8 on Pi 5 + Hailo-8L; ~7–8 FPS NCNN CPU-only | vendor-page-verified |
| Thermal 0.527 / radar 0.194 / fused 0.644 mAP₅₀:₉₅ | paper-verified (arXiv 2307.03623) |
| ST ToF people-counting 98.14% three-class | vendor-page-verified |
| VL53L5CX reflectance-vs-ambient range table | **not verified in this lane** — datasheet extraction failed |
| EURASIP 19-feature SVM headline accuracy | **not verified** — publisher auth redirect |
| DSC LC-100-PI pet weight rating | **not verified** — page returned no content |
| All decision-logic thresholds in §7.2 | **unverified starting points**, to be calibrated on the robot |

---

## Sources

- [Non-Contact Vital Signs Monitoring of Dog and Cat Using a UWB Radar (PMC7070589)](https://pmc.ncbi.nlm.nih.gov/articles/PMC7070589/)
- [Method for Distinguishing Humans and Animals in Vital Signs Monitoring Using IR-UWB Radar (PMC6888617)](https://pmc.ncbi.nlm.nih.gov/articles/PMC6888617/)
- [A robust multi-feature based method for distinguishing between humans and pets — EURASIP JASP 2021](https://asp-eurasipjournals.springeropen.com/articles/10.1186/s13634-021-00738-2)
- [Human and Small Animal Detection Using Multiple Millimeter-Wave Radars and Data Fusion — Sensors 2024, 24(6):1901 (PMC10975529)](https://pmc.ncbi.nlm.nih.gov/articles/PMC10975529/)
- [Micro-Doppler classification of humans and animals using FMCW radar — UCT](https://open.uct.ac.za/items/a65e9cb0-dbae-4a9d-a830-5a1177c08b90)
- [Micro-Doppler radar classification of humans and animals in an operational environment — Expert Systems with Applications](https://www.sciencedirect.com/science/article/abs/pii/S0957417418300964)
- [Lightweight Range–Angle Imaging Based Algorithm for Quasi-Static Human Detection on Low-Cost FMCW Radar — arXiv 2602.14001](https://arxiv.org/html/2602.14001)
- [Harmonic MUSIC Method for mmWave Radar-based Vital Sign Estimation — arXiv 2408.01951](https://arxiv.org/pdf/2408.01951)
- [Robust Human Detection under Visual Degradation via Thermal and mmWave Radar Fusion — arXiv 2307.03623](https://arxiv.org/html/2307.03623)
- [MIRaSeg: mmWave Radar and Low Resolution Infrared Sensor Fusion](https://link.springer.com/chapter/10.1007/978-981-95-5764-6_2)
- [Thermal and Circulatory Changes in Diverse Body Regions in Dogs and Cats Evaluated by Infrared Thermography — Animals 12(6):789 (PMC8944468)](https://pmc.ncbi.nlm.nih.gov/articles/PMC8944468/)
- [Detection of canine obstructive nasal disease using infrared thermography (PMC10497125)](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10497125/)
- [A Comparative Study of Forehead Temperature and Core Body Temperature (PMC9740153)](https://pmc.ncbi.nlm.nih.gov/articles/PMC9740153/)
- [Measurement of torso skin temperature under clothing — PubMed 3349991](https://pubmed.ncbi.nlm.nih.gov/3349991/)
- [Kinetic and temporospatial gait parameters in a heterogeneous group of dogs (PMC5015230)](https://pmc.ncbi.nlm.nih.gov/articles/PMC5015230/)
- [Quantitative Comparison of the Walk and Trot of Border Collies and Labrador Retrievers (PMC4687030)](https://pmc.ncbi.nlm.nih.gov/articles/PMC4687030/)
- [The role of stride frequency for walk-to-run transition in humans (PMC5435734)](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5435734/)
- [PDSA — How to record a resting respiratory rate](https://www.pdsa.org.uk/pet-help-and-advice/pet-health-hub/other-veterinary-advice/how-to-record-a-resting-respiratory-rate)
- [Polarimetric Radar Cross-Sections of Pedestrians at Automotive Radar Frequencies — arXiv 1910.13706](https://arxiv.org/pdf/1910.13706)
- [RCS Measurements of Pedestrian Dummies and Humans in the 24/77 GHz Bands — JRC](https://publications.jrc.ec.europa.eu/repository/handle/JRC78619)
- [Bosch Blue Line Gen2 ISC-BPR2-WP12 installation guide](https://manualzz.com/doc/33892839/bosch-blue-line-gen2-isc-bpr2-wp12-motion-detector-instal...)
- [Resideo IS335 pet-immune PIR](https://www.resideo.com/us/en/pro/products/security/wired-sensors/motion-sensors/is335-pet-immune-pir-detector-40-ft-x-56-ft-is335/)
- [DSC LC-100-PI PIR detector with pet immunity](https://www.dsc.com/alarm-security-products/LC-100-PI%20-%20PIR%20Detector%20with%20Pet%20Immunity/93)
- [Motion detection using pyro-electric and passive infrared — Electronic Specifier](https://www.electronicspecifier.com/products/sensors/motion-detection-using-pyro-electric-and-passive-infrared/)
- [Pololu VL53L5CX carrier (product 3417)](https://www.pololu.com/product/3417)
- [VL53L5CX datasheet — STMicroelectronics](https://www.st.com/resource/en/datasheet/vl53l5cx.pdf)
- [How to count people with a time-of-flight sensor — ST Edge AI case study](https://www.st.com/content/st_com/en/st-edge-ai-suite/case-studies/people-counting-with-a-ranging-sensor.html)
- [SparkFun Grid-EYE AMG8833 breakout (SEN-14607)](https://www.sparkfun.com/sparkfun-grid-eye-infrared-array-breakout-amg8833-qwiic.html)
- [Adafruit AMG8833 breakout (product 3538)](https://www.adafruit.com/product/3538)
- [Adafruit MLX90640 55° breakout (product 4407)](https://www.adafruit.com/product/4407)
- [MLX90640 datasheet — Melexis](https://www.melexis.com/-/media/files/documents/datasheets/mlx90640-datasheet-melexis.pdf)
- [Person Sensor documentation — Useful Sensors / Moonshine AI](https://github.com/usefulsensors/person_sensor_docs)
- [Person Sensor — SparkFun (retired)](https://www.sparkfun.com/person-sensor-by-useful-sensors.html)
- [Person Sensor — The Pi Hut (discontinued)](https://thepihut.com/products/person-sensor-by-useful-sensors)
- [DFRobot SEN0626 Gravity Offline Edge AI Gesture & Face Detection Sensor — wiki](https://wiki.dfrobot.com/sen0626/)
- [TFLite-Micro person detection — training a model](https://github.com/tensorflow/tflite-micro/blob/main/tensorflow/lite/micro/examples/person_detection/training_a_model.md)
- [MLPerf Tiny Benchmark — arXiv 2106.07597](https://arxiv.org/pdf/2106.07597)
- [Benchmark on RPi5 and CM4 running YOLOv8s with the Raspberry Pi AI Kit — Seeed wiki](https://wiki.seeedstudio.com/benchmark_on_rpi5_and_cm4_running_yolov8s_with_rpi_ai_kit/)
- [Infineon presence detection and zoning with XENSIV BGT60TR13C — AN003623](https://www.infineon.com/dgdl/Infineon-AN003623_Presence_detection_and_zoning_solution_using_XENSIV_BGT60TR13C_radar_and_CYW55913_Wi-Fi_Bluetooth_MCU-ApplicationNotes-v01_00-EN.pdf?fileId=8ac78c8c92416ca501925a36bfa408ad)
- [XENSIV BGT60TR13C radar FAQs — Infineon Developer Community](https://community.infineon.com/t5/Knowledge-Base-Articles/XENSIV-BGT60TR13C-radar-FAQs/ta-p/393702)
- [Seeed MR60BHA2 60 GHz breathing and heartbeat sensor](https://www.seeedstudio.com/MR60BHA2-60GHz-mmWave-Sensor-Breathing-and-Heartbeat-Module-p-5945.html)
- [Detection, Recognition, and Identification using thermal vs optical — Kintronics](https://kintronics.com/detection-recognition-and-identification-using-thermal-imaging-vs-optical-ip-camera/)
- [History and Evolution of the Johnson Criteria — OSTI](https://www.osti.gov/servlets/purl/1222446)
