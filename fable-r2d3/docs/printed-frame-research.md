# Printed structural frame hardware research

Checked 2026-09-12 for revision D. This is source research, not a released joint design. Read `C:/dev/robots/deploy.md`, `docs/load-hardware-research.md`, `bom/hardware.csv`, and `bom/fastener-stacks.csv`. No purchases or deployments.

Outcome: identify one optional 2020 reinforcement family, standard bearing retention, and a power-off shoulder hold path. Non-goals: assigning printed material strength from metal data, completing linkage CAD, or certifying a 9 kg assembly. Only this research file changes. Proof consists of manufacturer dimensional drawings, catalog ratings, and explicitly labelled screening calculations below.

## Optional reinforcement: one exact family

Recommend MISUMI HFS5-2020 clear-anodized extrusion, with HNTT5-5 pre-insertion M5 nuts. Do not substitute generic “2020,” V-slot, or another slot series. The [2019 manufacturer drawing](https://us.misumi-ec.com/pdf/fa/2019/2019_US_2686.pdf) specifies 20 ×20 mm envelope, 6 mm slot mouth, 12 mm slot cavity width, 2 mm lip depth plus 4 mm cavity depth, and a central 4.2 mm bore. Section area is 183 mm²; both second moments of area are 7,420 mm⁴; mass is 0.5 kg/m. Material is A6N01SS-T5 or 6005A-T5. The matching [2012 drawing](https://us.misumi-ec.com/pdf/fa/2012/p2_0511.pdf) was rendered and visually inspected to resolve slot dimension placement.

The [manufacturer bracket page](https://us.misumi-ec.com/pdf/fa/2019/2019_US_2696.pdf) explicitly pairs HNTT5-5 with CBM5-10 screws for relevant 5-series metal brackets. This verifies the hardware family, not a universal screw length. A printed bracket needs its own stack calculation: screw length minus printed grip and washer thickness must engage the nut without bottoming in the slot. Use a purchased sample to measure the nut's full thread length, slot-bottom clearance, and actual bracket grip before freezing bolt length. Nut exterior manufacturing dimensions were not independently extracted here. The [current clean-packed nut listing](https://us.misumi-ec.com/vona2/detail/110310823409/?HissuCode=SL-HNTT5-5) confirms compatibility with MISUMI 5-series 6 mm slots; clean-packed packaging is unnecessary for this robot.

The [MISUMI material/tolerance sheet](https://us.misumi-ec.com/pdf/fa/2012/p2_0493.pdf) lists A6N01SS-T5 reference tensile strength ≥245 MPa, proof stress ≥205 MPa, and elastic modulus 69,972 MPa. These properties apply to that alloy, not an unidentified substitute or printed carrier. It also lists HFS5-2020 outer dimensional tolerance ±0.41 mm. A nominal 20.0 mm printed pocket is therefore not an established sliding fit. Specify measured clearance and mechanical attachment. Confirm supplied alloy before using the reference proof stress as a design allowable.

Calculated metal-only example: a single simply supported 260 mm beam with a 265 N central load gives nominal bending stress PL/(4Z)=23.2 MPa, where Z=7,420/10=742 mm³. Ideal deflection PL³/(48EI)=0.187 mm. Two 260 mm lengths total 0.26 kg. Joint slip, slot lip pullout, torsion, printed interfaces, fastener preload loss, and actual load sharing are excluded. This calculation cannot establish the strength of a printed frame with optional rails. The unreinforced printed structure needs independent verification.

## Standard shoulder bearings and shaft retention

The [SKF bearing catalog](https://cdn.skfmediahub.skf.com/api/public/094466a66aaba637/pdf_preview_medium/094466a66aaba637_pdf_preview_medium.pdf) lists 6001-2RSH at 12 ×28 ×8 mm, dynamic capacity 5.4 kN and static capacity 2.36 kN. A larger standard alternative is 6201-2RSH, 12 ×32 ×10 mm, dynamic capacity 7.28 kN and static capacity 3.1 kN. The larger outside diameter and width offer more nominal projected housing area, but this is not a printed-seat strength rating. Select only one bearing family for both shoulders; 6201 is a reasonable CAD candidate if its larger seat fits. Existing BACA housings are for 6001 and cannot accept 6201.

Direct printed seats can remove the purchased housings, but require a dedicated fit coupon and loaded joint tests. Proposed construction: continuous cylindrical bearing seat with integral rear shoulder and removable through-bolted front retainer that contacts only the outer race. Do not press on seals. Keep a complete annular seat rather than relying on point clamps. Join carrier halves outside the bearing circumference; use broad ribs, through-bolts, metal washers, and accessible locknuts. Printed bore allowance and retainer contact diameter remain measured design values, not catalog fits.

The [SKF interface guidance](https://www.skf.com/binaries/pub12/Images/0901d196802809de-Rolling-bearings---17000_1-EN_tcm_12-121486.pdf) treats oscillating loads as rotating loads for fit selection. A loose ring can creep on its seat. Therefore a close-looking printed bore and axial cap do not prove suitable radial retention. The [SKF fit discussion](https://cdn.skfmediahub.skf.com/api/public/0901d1968024f02a/pdf_preview_medium/0901d1968024f02a_pdf_preview_medium.pdf) warns that uneven seating distorts rings and that split housings are generally unsuitable where outer-ring interference is needed. Determine ring loading in the actual shoulder before deciding fit. Verify free motion after bolt tightening and again after sustained loaded conditioning.

Use a real ground steel 12 mm shaft. Retain inner races through steel spacers and catalog collars, independently of outer-race caps. A shaft used only as a stationary axle can avoid a separately machined torque-transfer hub if the printed leg and its drive crank are one moving assembly; this is a design option, not a completed geometry here. Do not transmit shoulder torque through an assumed bearing fit or unverified printed shaft clamp.

The [Ruland MCL-12-F](https://www.ruland.com/mcl-12-f.html) one-piece clamping collar has 12 mm bore, 28 mm OD, 11 mm width, and maximum hardware clearance diameter 32 mm. Its supplied screw is M4×12; manufacturer seating torque is 4.6 N·m. Recommended shaft tolerance is +0/−0.013 mm. Listed price was $5.93. This corrects the earlier generic 22 mm OD ×8 mm collar envelope. The collar page does not establish assembled axial holding force. Collars are friction retention, not positive shoulder angle locks. Inner-race spacers must clear bearing seals and outer rings; obtain the selected bearing's abutment dimensions before machining spacers.

## Shoulder actuation and positive locks

Retain one actuator family if possible. The [Actuonix P16-100-256-12-P](https://www.actuonix.com/p16-100-256-12-p) provides 100 mm stroke, 147 mm closed eye spacing, 300 N maximum moving load, 500 N published backdrive force, 110 g mass, and a listed $90 price; it was backordered when checked. Extended eye spacing is calculated as 247 mm. The [P16 datasheet](https://www.actuonix.com/assets/images/datasheets/ActuonixP16Datasheet.pdf) specifies 500 N maximum static force, 20% duty, and 1 A stall current at 12 V. P provides position feedback; it must not be described as including S-model end switches. A backdrive threshold is not a mechanical positive lock.

Calculated screening assumptions: 9 kg complete mass, gravity 9.81 m/s², dynamic factor 3, friction allowance 1.25. Gravity is 88.29 N; factored reaction is 264.87 N. Direct center lift including allowance is 331.09 N, beyond the P16's 300 N moving rating. A 300 N actuator has an 8.15 kg maximum mass under this deliberately conservative direct-lift model. Actual center reaction may be lower, but must be solved from support geometry through the entire transition.

For a 60 mm horizontal center-of-gravity offset, factored total shoulder moment is 15.892 N·m. One P16 carrying all of it needs ≥66.2 mm perpendicular lever arm with the same friction allowance. At 40 mm it would need 496.6 N. Two independent shoulders cannot be credited with perfect equal sharing without analysis. Positive end-position locks remove sustained holding demand after engagement; they do not reduce actuator torque needed during unlocked motion.

A compact positive-lock candidate is [Winco GN 617-6-M12×1.5-AK](https://www.jwwinco.com/en-us/products/3.1-Indexing-locking-blocking-with-pins-and-ball-shaped-elements/Indexing-plungers/GN-617-Steel-Indexing-Plunger-Non-Lock-Out), a spring-return 6 mm indexing pin with threaded body and locknut. For easier attachment to a printed frame, [GN 412](https://www.jwwinco.com/en-us/products/3.1-Indexing-locking-blocking-with-pins-and-ball-shaped-elements/Indexing-plungers/GN-412-Zinc-Die-Cast-Indexing-Plungers-with-Screw-On-Flange) provides a screw-on flange and matching GN 412.2 steel locating bushings. Select one type, not both. No current price was verified for either, so no cost advantage is asserted.

Proposed integration: fixed plunger, steel receiver bushing in a broad through-bolted printed crank, hard stops at each commanded posture, and a sensor that confirms full engagement. A manual knob is not an automatic release mechanism. Powered release needs its own linkage, travel, and force proof, or use an existing actuator-driven release cam whose sequence is mechanically validated. Never claim an automated locked transition with only the manual plunger modeled. The actuator must first unload the pin, then release it, move, seat against the stop, and permit full pin engagement before reducing holding effort.

The [Winco pin-strength note](https://live-catalog.jwwinco.com/pdf/winco/US/rastbolzen_festigkeit.pdf?dispositiontype=attachment) distinguishes pin shear from bending and recommends considering bending when the guide-to-receiver gap is not negligible. Its metal pin capacities cannot rate printed receiver walls, bosses, or complete locks. Spring force is engagement/release force, not allowable side load. Keep guide-to-bushing gap short and calculate receiver bearing stress, edge tearout, and pin bending from the actual lock radius.

## Smallest useful purchased family and acceptance

Recommended procurement structure: one 2020 extrusion type and matching M5 nut; one shoulder bearing size; one 12 mm shaft stock type; one collar; one actuator family; one lock-pin type with steel receiver; and shared M3/M4/M5 bolt lengths wherever completed stacks permit. Existing metal chassis plates, custom housings, welded feet, and hub parts are not automatically retained by this research. Count distinct purchased specifications honestly: different screw lengths remain distinct items even if sold in one assortment. Do not count printed parts as purchased hardware.

Before fabrication release: solve all motion from fully internal center-foot stow to front deployment; check whole foot/wheel and actuator swept volumes; evaluate support-polygon stability; calculate force at every shoulder/center configuration; confirm physical pin release and engagement; weigh the revised robot; and load-test printed carriers, fastener interfaces, and both optional-rail configurations. Test power loss at endpoints and during motion. No material coupon, creep test, loaded transition, or printed-structure working-load rating was established by this research.

## Follow-up: stationary axle and sleeve bearing

For the requested 12 mm ID ×16 mm OD ×20 mm sleeve, use igus GSM-1216-20 as the dimensionally verified candidate. The [manufacturer G sleeve catalog](https://www.igus.com/ContentData/Products/Downloads/iglide_G300_FM_USen.pdf) lists those nominal dimensions, a 16.000–16.018 mm housing bore, 11.957–12.000 mm shaft, and 12.050–12.160 mm installed bearing ID for this particular 2 mm wall part. It recommends a ground shaft surface Ra 0.8 µm and a machined H7 housing. The 20 mm length is h13. An older [igus catalog](https://www.igus.com/contentData/Product_Files/Download/pdf/2016%20iglide%20section.pdf) lists the same part and envelope but a different installed-ID range; use the newer part-specific row and verify the delivered component. Exact current price and local stock were not confirmed.

Do not specify SKF PCM121620E from its plausible-looking name. It was not found in the manufacturer catalog. The verified SKF alternative is PCM121420E, which is 12 ×14 ×20 mm, in the [SKF composite sliding-bearing catalog](https://cdn.skfmediahub.skf.com/api/public/0901d19680229dfc/pdf_preview_medium/0901d19680229dfc_pdf_preview_medium.pdf). It does not fit a 16 mm seat without a separate adapter. Use the igus part to retain the requested 16 mm envelope and avoid another purchased adapter.

Proposed stationary-axle arrangement: ground 12 mm steel axle fixed to chassis supports; sleeve pressed into the moving leg lug; Ruland collars outside the support assembly for axle retention; independent positive lock between leg and chassis for posture torque. This removes a rotating shaft torque hub. Do not tighten collars against the moving lug or sleeve ends so that they become unintended brakes. Provide an explicitly dimensioned axial running clearance and suitable thrust faces. The straight sleeve is a radial bearing; it does not supply a catalog thrust-bearing surface.

A printed 16 mm hole is not automatically a 16 H7 housing. Print a coupon in the final orientation, finish the seat to measured dimensions, and check installed running clearance. Retain the sleeve axially with integral shoulders/caps that leave the shaft free. The [igus FAQ](https://www.igus.com/plastic-bearings/resources/plain-bearings-faq) describes press-fit installation; it does not rate a printed housing. The selected production polymer, print settings, moisture, temperature, housing distortion, and creep still require testing. A metal collar's narrower shaft tolerance should govern shaft procurement: +0/−0.013 mm is compatible with the sleeve catalog's broader h9 range.

Calculated bearing pressure screening: one 20 mm sleeve carrying 265 N gives p=F/(dL)=265/(12×20)=1.10 MPa. This is only mean projected pressure; two sleeves do not automatically share it equally. Include shoulder overhang, actuator and lock-pin forces, alignment, friction, speed, and edge loading. The [igus G material page](https://www.igus.com.mx/plastic-bearings/resources/iglide-material-g300) reports 11,600 psi (about 80 MPa) permissible static surface pressure at 20°C. That is bearing material data under its specified conditions, not a permissible pressure or load for the printed lug. No strength factor for the printed part is claimed.

## Follow-up: exact flange indexing-pin drawing

The [official Winco GN 412 drawing](https://live-catalog.jwwinco.com/pdf/winco/us/412.pdf?dispositiontype=attachment) was downloaded, rendered, and visually read. GN412-6-35-B-1 is the exact 6 mm, non-lock-out, front-mounting part. Drawing dimensions in millimetres: flange width b=35; flange height h=26; mounting pitch k=25; two through-bores d2=4.3 for M4 socket screws; knob d4=25; pin d1=6 with tolerance 0/−0.06; mating bore +0.05/+0.10. Pin-axis height above the flat flange bottom l4=14. Flange thickness along the pin axis s=12. Front mounting counterbore shoulder depth l3=6 from the back face; exact counterbore diameter is not dimensioned in this drawing. Overall body/knob length l1=32 from the pin-exit face; minimum pin extension beyond that face l2=6. Fully pulled pin retracts within the flange. Spring load is approximately 5 N initial and 15 N fully pulled. This is release effort, not holding capacity.

For CAD, reserve an additional measured knob pull stroke and hand/linkage clearance. Do not model the 32 mm closed body as its complete moving envelope. B means no retained retracted position; C intentionally locks retracted and is not the proposed automatic spring-return baseline. The manual plastic knob is not removable per the manufacturer; any powered release linkage must work with its actual shape or choose another documented plunger. This research does not establish that a generic servo horn attached to this knob is a completed release mechanism.

## Follow-up: structural filament and H2D tooling

Select Bambu PETG HF as the common prototype frame material, subject to loaded validation. This is a manufacturing baseline, not a certified structural allowable. The [official H2D manual, February 2026, pages 105–106](https://csm.bblcdn.com/hub/4668d0ca43994ff3bff4b37f1a65c2e7.pdf) confirms a standard 0.4 mm hardened-steel nozzle and PETG HF compatibility with all nozzle sizes, no hardened-nozzle requirement, AMS 2 Pro compatibility, and mandatory drying before use. PETG-CF requires hardened steel and excludes 0.2 mm; it adds a tooling constraint without establishing better complete-frame behavior here. The manual classifies PETG as low-temperature filament and warns against chamber temperatures above 45°C. Installed tooling on the user's actual H2D was not inspected; stock-tool compatibility is verified, local-tool identity is not.

The [Bambu PETG HF Technical Data Sheet V1.0](https://store.bblcdn.com/3a230e260a3a47c2b0db0156e07eef91.pdf) reports printed tensile strength XY 34±4 MPa and Z 23±4 MPa; bending strength XY 64±3 MPa and Z 48±4 MPa. Young's modulus is XY 1,810±190 MPa and Z 1,540±130 MPa. ISO 75 heat-deflection temperatures are 62°C at 1.8 MPa and 69°C at 0.45 MPa; glass transition is 66°C. Specimens used 255°C nozzle, 70°C bed, 200 mm/s, 100% infill, followed by annealing and drying at 75°C for 8 hours before testing. These are conditioned printed-specimen results, not injection-molded properties or untreated-print allowables. The sheet discourages annealing complex prints because they can distort. It specifies filament drying in a forced-air dryer at 65°C for 8 hours and sealed storage below 20% RH. No quantitative long-term creep curve or sustained joint-load allowable is supplied. Its older 35–50°C chamber suggestion conflicts with the newer H2D limit above; follow the newer printer guidance. Layer height, wall count, and exact test-printer model are not stated in the extracted specimen conditions.

Do not anneal the robot frame to claim the catalog numbers. Set the actual process in fabrication instructions and test that process. Proposed evidence: same-orientation joint coupons, complete shoulder static load and cyclic-motion tests, and sustained loading at the highest measured enclosure temperature. Record bore movement, screw preload loss, cracking, and residual deflection. Heat-deflection temperature is not a continuous service-temperature rating. Creep can impair a clamped joint before gross thermal deformation.

The root design's 21.2 mm reinforcement socket is an intentional clearance allowance, not a verified extrusion fit. Against the earlier ±0.41 mm reference extrusion envelope, its calculated total width clearance is 0.79–1.61 mm before print error. It therefore needs a positive clamp/fastener interface and a physical coupon with the actual rail. Neither frictional load transfer nor a precision press fit follows from that nominal clearance.

## Follow-up: standard metal shaft hub

The [ServoCity/goBILDA 1301-0016-0012 hub](https://www.servocity.com/1301-series-clamping-hub-12mm-bore/) is a catalog alternative to a custom shaft hub: 12 mm bore, aluminum, clear anodized, 10 g, listed $6.99 when checked. The official [dimension drawing](https://cdn11.bigcommerce.com/s-f6vfspkkjf/images/stencil/1280x1280/products/3059/29627/y9e9KswWx0ULPc9vBCuvp9jaMTgHL8WIJtgxGGepslSzwYW9t8HE0TjvFPLJtt47__53479.1773180104.png) was downloaded and visually inspected. It specifies four M4×0.7 threaded holes on a 16 mm square pattern; body thickness 8 mm; a 2 mm projecting Ø14 mm register; total axial envelope therefore 10 mm. Body height is 24 mm; the pinch-ear end lies 17.9 mm from shaft center. The drawing shows a Ø39.8 mm dashed rotational envelope. Included pinch screw is M4×0.7×10 mm with 3 mm hex drive. Use the larger rotational envelope rather than treating the part as a 24 mm diameter disc.

The official [STEP assembly download](https://www.servocity.com/content/step_files/1301-0016-0012.zip) is available and was downloaded, but no local CAD import succeeded in this research environment. Thus dimensions above come from the labelled drawing, not measured STEP geometry. The drawing does not assign a torque capacity, axial holding force, tightening torque, or thread engagement tolerance. It also does not dimension an access-tool envelope. Reserve an open path along the pinch-screw axis for the 3 mm hex driver and verify assembly access with the actual hub. Do not claim the adjacent part can cover the pinch bolt merely because the rotating envelope fits.

A printed leg plate can bolt to the four threaded holes and clear or locate on the Ø14 mm register. Select screw lengths from the actual printed grip so screws engage the 8 mm body without crossing moving interfaces. Tighten the shaft pinch screw before fastening a plate that would obstruct the clamp's small closing movement. Confirm the purchased manufacturer's assembly guidance and actual screw engagement before final assembly.

This changes the motion architecture if it rigidly fixes the leg to the shaft: the shaft must rotate in chassis bearings, so it cannot directly replace the sliding sleeve on a stationary axle without moving the rotation interface. Alternatively use the hub to fix the axle to the chassis and retain a moving leg sleeve. Choose one complete arrangement. The independent angle lock still carries sustained posture torque only when fully engaged. The hub may simplify shaft attachment, but no claim is made that it alone replaces all required bearings, thrust clearance, or opposite-end axial retention.

## Follow-up: strict 99 purchased physical pieces

The user clarified that the cap is 99 purchased physical pieces total, not 99 part types. This overrides the earlier procurement-type counting recommendation in this research history. A factory-assembled board or motor with factory leads counts as one assembly. Loose kit headers, screws, capacitors, plugs, and separate cables still count individually. A parts assortment cannot conceal its contents. An electrical budget is incomplete until its actual connection harness and mounting pieces are counted.

The current `bom/electronics.csv` was read for this follow-up. Findings below identify simplification candidates only; no wiring, firmware, or BOM was changed.

### Retain factory motor leads and existing current limiting

[Adafruit motor 3777](https://www.adafruit.com/product/3777) includes two factory-attached 200 mm, 28 AWG leads with 0.1-inch male ends. These do not need another purchased motor lead pair if they reach the board. Seven motors plus thirteen separate wheels are twenty physical assemblies. The motor page reports sample stall current 1.2 A at 4.5 V and 1.5 A at 6 V; these are measurements of one sample, not guaranteed worst-case ratings. Do not parallel two motors on a nominal 1 A channel to reduce the driver count.

Four [Adafruit DRV8833 boards, product 3297](https://www.adafruit.com/product/3297), provide eight channels for seven motors. Their factory current regulation is nominally 1 A per channel. Keep it intact. The product supplies an assembled board plus loose header material; direct soldered connections can omit the loose headers, but actual soldered wire pieces still require counting. The board is listed for approximately 1.2 A per channel, with 2 A only a brief peak when current regulation is disabled. It is compatible with 3.3 V control and a 5 V motor supply.

The [TI DRV8833 datasheet](https://www.ti.com/lit/ds/symlink/drv8833.pdf) specifies internal input pulldowns: nominal 150 kΩ on bridge inputs and 500 kΩ on nSLEEP. Extra pulldowns used only to establish idle-low states can be removed from short, directly driven lines after reset/disconnect testing. Do not remove resistors serving other functions. Minimum logic-high is 2 V on bridge inputs and 2.5 V on nSLEEP. nFAULT is open-drain and needs a pullup when read. Current-trip voltage spans 160–240 mV; with 0.2 Ω sense resistance, the nominal 1 A limit can span about 0.8–1.2 A before resistor tolerance. TI requires system-level verification of local bulk capacitance; braking, wire inductance, and source response determine its size. A supply current limit does not substitute for local transient suppression.

The [official Adafruit Eagle schematic](https://github.com/adafruit/Adafruit-DRV8833-Motor-Driver-Breakout-PCB/blob/master/Adafruit%20DRV8833.sch) was downloaded and parsed directly. C1 and C4 are each 10 µF/16 V from VMOTOR to ground; C2 is 10 µF from VINT to ground; C3 is 0.1 µF between VCP and VMOTOR. R1/R2 are 0.2 Ω current-sense resistors. These are already fitted chip-support components. Do not add a second loose copy of them. The schematic has no external bridge-input pull resistors and no nFAULT pullup. Its 20 µF nominal VM capacitance does not prove that no additional bulk capacitor is needed in the robot. Motor-terminal EMI capacitors serve another location and purpose; retain them unless the final wiring/noise test justifies removal.

### Concrete integrated actuator option

[Actuonix Ext-R configured for P16](https://www.actuonix.com/external-rc-control-board-.html) was listed at $20 with stock available. It is a compact controller with motor drive, position loop, current regulation, and feedback outputs on one board. This can replace the separate actuator driver, external position ADC, current-sensor board, and some associated loose components if the firmware and limit wiring are deliberately updated. It includes a separate RC extension cable and heat-shrink piece; count these separately if purchased/used under the final counting convention.

The [Ext-R datasheet revision C](https://www.actuonix.com/assets/images/datasheets/Actuonix%20Ext%20-R%20Datasheet.pdf) specifies 36×15×6.7 mm, 12-bit position control, adjustable 0–1 A motor current limit, 6–12 V input matching the actuator voltage, and RC commands of 1–2 ms at 50–300 Hz with 5 V amplitude. F1 gives 3.3 V retracted to 0 V extended; F2 gives 0–3.3 V for 0–1 A. Both require high-impedance loads. On command loss it completes the last target before entering low power; it does not stop immediately. Stall shutdown follows several seconds of persistent failure. These behaviors do not replace RUN power isolation, independent travel protection, or firmware communication timeout handling. Retain the regulated 12 V rail. Do not assume ESP32 3.3 V pulses satisfy the specified 5 V amplitude.

An existing AHCT125 can serve multiple servo/Ext-R outputs and avoids multiple separate buffers. Its bypass capacitor remains necessary. For an assembled buffer candidate, [Adafruit NeoPXL8 Friend 3975](https://www.adafruit.com/product/3975) provides eight 3.3-to-5 V outputs, on-board 5 V generation and 100 Ω output series resistors, but was out of stock. It is a level shifter, not an eight-motor driver. No replacement buffer was selected solely to claim the budget passes.

### Why a larger motor board is not automatically simpler

Two [Adafruit motor shields 1438](https://www.adafruit.com/product/1438) provide eight DC channels with I²C control, but their TB6612 channels are rated 1.2 A continuous and 3 A for about 20 ms. They do not preserve the existing DRV8833 regulation. [Adafruit's technical explanation](https://learn.adafruit.com/current-limiting-stepper-driver-with-drv8871) distinguishes the non-current-limiting TB6612 from current-regulating drivers. Saving two boards while permitting repeated TT stalls is not an equivalent electrical design.

[Pimoroni Motor 2040](https://shop.pimoroni.com/products/motor-2040) is a real fully assembled four-channel DRV8833 board with integrated current/voltage sensing. Its factory limit is only 0.5 A per motor; bypassing it also disables current monitoring. It adds another programmable processor and uses six-pin JST-SH motor connectors, so the existing TT leads need adaptation. [Inventor 2040 W](https://shop.pimoroni.com/products/inventor-2040-w) integrates Wi-Fi, audio, and six servo ports but only two DC channels at 425 mA each. Neither is a drop-in seven-motor replacement. The reviewed [Cytron Robo ESP32](https://www.cytron.io/p-robo-esp32) likewise has only two 1 A continuous motor channels. No all-in-one seven-channel, current-regulated, Wi-Fi/audio board was verified in this bounded search.

### Power consolidation and recommended path

Retain the ESP32, original MP3 playback path, four DRV8833 boards, and required servos. Use Ext-R-P16 only as an explicit actuator-interface change. Concentrate piece reduction on duplicated support passives and separately counted power branches, after checking electrical consequences.

One larger 5 V regulator can replace several small UBEC assemblies if its final thermal/load test passes. The [Pololu D24V150F5, product 2881](https://www.pololu.com/product/2881) is a concrete 5 V candidate, nominally 15 A, 43.2×31.8×11 mm, with reverse-polarity, short-circuit, thermal, undervoltage, and soft-start protection. Its actual current depends on input voltage and cooling; listed supply status was rationed with backorders, not verified immediately available. It is not approved here as a production choice. Seven DRV8833 channels can total roughly 8.4 A at the upper trip threshold before tolerances; servo stalls and logic/audio must be budgeted separately. The smaller regulator's nominal nameplate is insufficient evidence.

Do not remove branch protection while retaining thin factory motor leads on an unrestricted high-current bus. Driver regulation limits controlled motor current but does not protect every upstream wiring short. Count the chosen fuse holders, fuses, distribution connectors, individual harnesses, and bulk capacitors explicitly. Converter outputs must not be paralleled. A short, well-placed common supply can reduce wire inductance, but capacitance removal requires measured rail waveforms during start, stall, braking, and servo motion.

This research supports a feasible reduction path, not a verified 99-piece complete build. Acceptance requires an itemized physical-piece count, final pin allocation, retained original MP3 demonstration, power-loss behavior, and full electrical load/noise testing. No firmware dependency, wiring behavior, or safety interlock was changed by this note.

## Follow-up: Romeo ESP32-S3 DFR0994 integration

The [DFRobot DFR0994 product page](https://www.dfrobot.com/product-2743.html) lists four 2.5 A motor channels, an ESP32-S3-WROOM-1U-N16R8 with 16 MB flash/8 MB PSRAM, Wi-Fi SoftAP capability, and a 5 V/2 A peripheral supply. Listed price was $46.90. Shipping contents are board, separate camera, and separate antenna. Under a purchased-piece cap the bundle is not automatically one piece; the external antenna remains needed for normal radio use. Do not infer a board dimension from the inconsistent metric/inch text in the listing.

The [official wiki](https://wiki.dfrobot.com/dfr0994/) specifies separate VIN 7–24 V and VM 5–24 V inputs. The power-link jumper joins them when installed. Thus a regulated 5 V motor supply with a higher-voltage logic input is supported only with that link removed. Four motor control pin pairs are GPIO12/13, GPIO14/21, GPIO9/10, GPIO47/11. The chip exposes I²S, ADC and PWM functions, but these are multiplexed peripheral capabilities, not proof that all features can use every pin at once.

The [official schematic ZIP](https://dfimg.dfrobot.com/wiki/22811/DFR0994_romeo-esp32-s3_schematics_V1.1.zip) contains V1.1.0 and V1.0 drawings. V1.1.0, dated 2025-09-08, was extracted and visually inspected. It has four DRV8876 drivers. Each IPROPI resistor is 1 kΩ; common VREF uses 5.1 kΩ over 20 kΩ from 3.3 V. The drawing calculates VREF=2.629 V and nominal trip=2.629 A. Actual IMODE connections are 0 Ω to ground, despite a conflicting annotation mentioning 20 kΩ. Each channel includes 100 µF/35 V VM bulk capacitance, 100 nF bypass, charge-pump capacitors and output filtering. nFAULT pins are unconnected; IPROPI is not routed to MCU ADC. nSLEEP is pulled high. The power link is JP6 in this revision, so identify it by its VIN/VM function rather than an older silkscreen name. Servo headers provide 5V_Servo/GND with GPIO3,38,40,41,42,43,44; other headers expose GPIO4,5,6,7,8,15,16,17,18 and additional signals at 3.3 V power.

The [TI DRV8876 datasheet](https://www.ti.com/lit/ds/symlink/drv8876.pdf) confirms genuine hardware current chopping. IMODE grounded selects fixed off-time regulation and automatic fault retry; it is not merely thermal protection. The relation is Itrip=VREF/(RIPROPI×0.001), with amperes, volts, and ohms. Separate short-circuit OCP is 3.5–5.5 A. Input pulldowns are internal. Current-mirror accuracy is specified only for VM≥5.5 V, with ±4% in the 0.5–2 A HTSSOP range below 125°C. The chip operates at 4.5 V, but that does not extend the current-accuracy guarantee down to a 5 V motor rail. Regulation cannot be assumed to shut down a permanently stalled motor; it continues current chopping. Junction temperature and board cooling constrain continuous output.

Engineering conclusion: this is a credible integration candidate for three synchronized motor pairs plus one head motor, replacing the separate ESP32 and four dual drivers. It does not meet a ≤2 A channel limit as shipped. Reworking the shared VREF divider could lower all channels; a separate head IPROPI change could retain a lower head limit. Both are deliberate board changes requiring identification of the actual hardware revision and measured limits. No resistor value is released here as a guaranteed ≤2 A design at VM=5 V. Count purchased replacement resistors rather than concealing rework pieces inside the original board assembly.

Parallel motors share voltage, not a guaranteed equal current. One stalled motor can take most of the pair allowance. A 2 A pair limit is therefore not two independent 1 A limits. Before accepting that changed protection model, verify each motor's sustained temperature and worst-case single-motor jam behavior. Three nominal 2 A pairs plus the head also exceed the onboard 5 V/2 A source. An external motor regulator remains necessary, and the three servo/actuator signals are still 3.3 V logic even though their headers provide 5 V power. A signal level shifter remains necessary where the receiving device specifies 5 V amplitude, including Ext-R.

Feasible pin-allocation example, not implemented firmware: GPIO38/40/41 for two stance-lock servos and Ext-R command; GPIO4/5 for high-impedance actuator position/current monitoring; GPIO15/16/17 for external I²S amplifier. This requires no active camera, GDI display, or microSD SPI use on those shared pins. Original MP3 data can remain in flash, subject to actual decoder and build verification on ESP32-S3. Confirm this allocation against the delivered board and existing application before rewiring. The positive motor-power RUN cut must disconnect VM independently of logic power; the board's pulled-high sleep net is not an MCU-controlled global stop as drawn.

The board materially reduces assembly count, but it is a conditional migration candidate, not a verified drop-in or a complete 99-piece result. Needed evidence: correct VIN/VM isolation, measured regulator and channel limits, motor and servo thermal tests, safe single-motor jam behavior, hardware RUN stop, and original MP3/Wi-Fi control demonstration. No purchase, resistor rework, or firmware migration was performed by this research.

## Follow-up: explicit physical-piece ledger

An honest sub-99 inventory was not established with conventional bolted mounts and the listed mechanisms. The following candidate is a conservative planning ledger, not a final BOM or proof that another integrated printed design cannot meet 99. It deliberately counts each installed bolt and nut. It does not treat loose accessory bags as factory assemblies.

The [ServoCity 1620-0001-0004 turntable](https://www.servocity.com/4x4-ball-bearing-turntable/) is a verified head-bearing candidate, listed at $5.99, 4.9 oz, and 110 lb catalog capacity. Its nominal “4 inch” name does not equal its actual envelope. The [official dimensional drawing](https://cdn11.bigcommerce.com/s-f6vfspkkjf/images/stencil/1280x1280/products/1305/23461/1620-0001-0004-Schematic__91232.1736871370.png), downloaded and visually inspected, specifies 94.1 mm square plates, 9 mm assembled height, 0.8 mm plate thickness, 54.7 mm central opening, and four 4.3 mm mounting holes per plate on an 81 mm square. It is slightly smaller than the requested approximate 100–120 mm range. The product prose says 5/16 inch high, which conflicts with the 9 mm drawing; use the drawing and verify the delivered part. The steel bearing's axial catalog rating does not rate its printed mounts or overturning load.

This head choice is one factory assembly, but eight mounting screws and eight nuts make the conventional installed bearing connection seventeen pieces. No reduction versus the earlier central bearing stack follows without a separate mounting design. Its square rotating plate also needs corner sweep clearance, calculated as 94.1×sqrt(2)=133.08 mm diameter before attached-part clearance.

Candidate ledger, quantities of actual pieces:
 20 — Motors and wheels.
 7 — 2020 rails.
 1 — Shaft.
 4 — Shoulder bearings.
 2 — Hubs.
 8 — Hub screws.
 1 — Head turntable.
 8 — Head screws.
 8 — Head nuts.
 1 — Post actuator.
 1 — ExtR.
 2 — Servos.
 2 — Horns.
 2 — Horn screws.
 8 — Servo mount screws.
 8 — Servo mount nuts.
 3 — Limit switches.
 6 — Limit screws.
 6 — Limit nuts.
 6 — Rod-end stack.
 2 — Actuator pins.
 4 — Pin Rclips.
 1 — GN lock.
 1 — Receiver.
 2 — Lock screws.
 2 — Lock nuts.
 1 — Release link.
 2 — Release joints.
 2 — Release joint screws.
 2 — Release joint nuts.
 1 — Steer link.
 2 — Steer joints.
 2 — Steer joint screws.
 2 — Steer joint nuts.
 3 — Romeo board antenna camera.
 1 — Motor regulator.
 1 — Post regulator.
 1 — Amp.
 1 — Speaker.
 1 — Buffer board.
 1 — Battery.
 1 — Charger.
 2 — Main and RUN switches.
 1 — Main fuse holder.
 1 — Main fuse.
 2 — Branch holders.
 2 — Branch fuses.

Calculated subtotal: 148 pieces. The seven rail pieces are four 228 mm body rails, two 180 mm leg rails, and one 310 mm post rail. The rod-end stack row contains one SKF SA12E, one M12 jam nut, one 12 mm shoulder bolt, one M10 locknut, one washer, and one shim. The two hub pinch screws already fitted by the manufacturer are not counted again; the two hub assemblies each include their own factory pinch screw. The eight hub mounting screws remain separate. Servo horns and their center screws are counted separately because they are loose supplied accessories, not factory-attached parts. Actuator pins and their four R-clips are separate pieces.

Head and servo mounting fastener rows assume ordinary through-bolts and nuts, with four mounts per servo. Each limit switch assumes two through-bolts and two nuts. Exact screw lengths remain dependent on printed grip. Release/steering link rows each assume one rod, two articulating ends, two joint screws, and two nuts; a proven direct release cam could replace the release link but has not been released here. The buffer-board row is an assembly allowance using the earlier identified level-shifter class, with actual availability unresolved. Fuses and holders are distinct. Romeo's supplied camera and antenna are counted alongside the board even though the candidate does not use the camera.

Not included in that subtotal: battery mating connector, every separate wire/harness and extension, post feedback lead extensions, power distribution connectors, motor-terminal capacitors if retained, any added rail bulk capacitors, resistor rework pieces, bearing outer-race retainers and their fasteners, metal inner-race spacers if needed, foot attachment fasteners, lock receiver retention, servo-platform shims, battery restraint, and any extra board/speaker retention hardware. These are count gaps, not zero-piece assumptions. Factory TT leads can be reused only where their 200 mm length reaches. A factory preterminated multi-conductor cable counts once; separate wires assembled locally do not become one purchased harness by being tied together. Cut filament, solder, flux, paint, and masking consumables belong in a separate consumables list rather than hardware bundles.

Removing 49 items from 148 would only reach 99 before those gaps. A credible under-99 release therefore needs a revised joint/mounting architecture and an explicit circuit harness, not a different way to group the ledger rows. The root CAD may replace some bolted mounts with continuous printed structure, but every such removal needs a defined load path and verification. Printed alignment keys or clips are not assumed to replace rotating shaft retention or loaded articulating joints. This research does not claim an impossible lower bound; it rejects only the unsupported sub-99 claim for this conventional candidate.
