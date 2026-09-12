# ROUND-9 mechanical verification

Reviewed on 2026-09-12. ROUND-9 combines the two prior skirt sections into one 213 mm print. The circular base, four inset ground wheels, concealed arm actuators and adjustable TT-motor friction head drive retain their geometry. There are nine distinct STL designs and ten printed pieces. `07_pitch_carrier.stl` is printed twice. Every released STL has one connected positive solid, consistent winding and a watertight surface. The robot remains nominally 563.8 mm tall.

These checks establish nominal digital envelopes, sampled assembly paths and tool access. They do not establish physical strength, actual servo-horn fit, tire runout, fabric behavior, traction, motor payload or a certified load rating. The built robot must pass the commissioning gates in `mechanical.md` and `assembly.md`.

## Reproducible release checks

Run from `C:/dev/robots/dalek`:

```text
C:/Python314/python.exe scripts/export_cad.py --check-only
C:/Python314/python.exe scripts/check_mechanical.py
C:/Python314/python.exe scripts/check_arm_assembly.py
C:/Python314/python.exe scripts/check_skirt_access.py
```

The first command writes `cad/validation.json` and `bom/printed-parts.csv`. It checks the exact nine-file inventory, positive volume, one connected positive solid per file, watertightness, winding and H2D bounds with the selected brim allowance. Read the current solid-material volume bound from those files; it is not installed print mass. The mesh count is 9, the physical printed-piece count is 10 and the circular base brim envelope is 316 x 316 mm.

The second command writes `cad/mechanical-checks.json`. It covers base hardware, arm motion, insertion paths, head adjustment, tool paths and ideal opaque-liner visibility. ROUND-9 adds the combined skirt's height limit, lower bolt-driver paths, retained joint features and open middle bore. Its visibility scenes now use the current complete skirt. The JSON contains the exact SHA256 of every sampled STL, the sample count and result of each check, and the limits of the method. It uses existing NumPy, trimesh and rtree packages. No new dependency or test framework was added.

The full ROUND-9 mechanical run returned exit code 0: all 118 checks passed across 554,129 samples. All nine recorded mesh hashes match the released files. This includes newly run tests of the 213 mm skirt and its current exterior in all five opaque-liner scenes: 4,800 visibility rays, zero visible servo targets. The original ROUND-10 count of 101 checks across 507,950 samples is historical evidence only; it is not relabelled as a new run.

The separate assembly-order regression writes `cad/arm-assembly-checks.json`. It passed eight checks across 187,920 samples. Its four recorded mesh hashes match the same released parts, whose geometry is unchanged in ROUND-9. The focused skirt-access regression records plate and battery insertion and the actual deep-tool approaches in `cad/skirt-access-checks.json`.

The focused access report passes all 61 checks across 868,363 sample evaluations. Its final update reran the 20 affected plate and retained-hardware checks for the Z44 insertion route and retained 41 unchanged results on the same exact base/skirt hashes. The retained hardware envelope extends at most 3 mm below each plate and excludes the specified 8 mm-radius mount keepouts. Actual board holes, cured nut retention, screw lengths and purchased tool dimensions remain physical fit gates. This is not a claim that an unspecified PCB hole pattern has been digitally checked.

`cad/h2d-slice-check.json` is separate evidence from actual local Bambu Studio slicing. It records the source hashes, process settings, generated model/support/brim bounds, material and extrusion height. A global slicer setting alone is not proof that the requested brim was generated; the report checks actual deposited paths. Mesh fit and real slicing are different checks and both must match the released meshes.

The ROUND-9 report contains one new actual `02_skirt` slice and eight retained slice records whose exact STL hashes still match. The new slice returned exit code 0 in 34.81 seconds. The complete model deposition runs from Z0.2 to Z213.0. Its conservative deposited bead bounds are X7.7093-317.2917 and Y5.2093-314.7917, within the configured left nozzle area. The generated brim/skirt features consume 0.947 g. The new skirt requires 1,033.8658 g of PLA including supports, predicts 527.879 g of installed model material, and takes 85,539.86 seconds (about 23 hours 46 minutes). One 1 kg spool cannot finish that slice; provide at least 1.14 kg with reserve and plan a compatible supply change before starting.

Release totals are 3,951.62 g of filament, 2,345.25 g of installed printed material and 406,685.32 seconds of predicted printing. Relative to the prior two-skirt release, that saves about 121.44 g of filament, 83.95 g of installed printed material and 3 hours 19 minutes. These are slicer estimates, not measured consumption, finished robot mass or physical strength. The solid-geometry upper bound is 2,995.9 g.

## Combined skirt and retained service access

`02_skirt.stl` replaces `02_lower_skirt.stl` and `03_upper_skirt.stl`. The base remains at world Z13.8, the skirt begins at 67.8 and the shoulder begins at 277.8. The first slope changes radius 150 to 125 over 110 mm, and the second changes radius 125 to 110 over 100 mm. The top tongue adds 3 mm, giving a 213 mm print below the 320 mm ceiling. All four hemisphere rows and the former upper flange's visible 6 mm outer band are retained. The former bolted joint is removed; a tapered integral rib has a nominal 240 mm clear bore. The more restrictive top opening remains nominally 184 mm diameter.

`cad/merged-skirt-review.json` records a first-hit radial ray comparison with the two prior skirt meshes from commit `1f11c3d97a7183b7391ca649071a336a580162f5`. It checked 8,496 exterior rays, including the slope break, retained outer band and all four hemisphere rows. The maximum radius difference was 0.000004554 mm, below the 0.001 mm comparison tolerance. The report also records the exact unchanged hashes of the eight remaining designs and the new skirt hash `ff1baa0536e36c0730d69f5cf8004e069f4fe4e430026d6f3e6bc734a125146e`. This finite exterior comparison does not claim interior equivalence; removing the middle flanges and adding the integral rib is intentional.

The final skirt has 39,728 nonzero-area triangles, consistent winding, one connected positive solid and exactly two faces at every mesh edge. Three extremely narrow triangles can cause a floating-point barycentric warning in trimesh's ray arithmetic; their combined area is approximately 0.000132 square millimetres. No faces were removed and no warnings were suppressed. The finite path checks remain nominal checks with the limits in their reports. A microscopic membrane found in the first trial rib was corrected in the CAD before releasing this watertight mesh.

The remaining body joints use twelve M4x20 screws, twelve nuts and twenty-four washers. The removed middle joint saves four screws, four nuts and eight washers. Eight other printed designs retain their exact released hashes. The change may reduce joint flex, but no physical strength increase is measured or guaranteed.

The deeper skirt requires different assembly tools and order. The M4 driver has a 250 mm exposed shaft, a 3 mm ball end and at least a 20-degree rating. The sampled lower-bolt route tilts inward 16 degrees from radius 137 at skirt-local Z10. The check uses the 1.74 mm corner radius of the hex shaft and tests all four approaches against the current skirt and base.

The M4 nut is below the base flange. A Bahco 677-7 crowfoot offsets the extension inward by 17.5 mm, from nut radius 137 to drive radius 119.5. The 6966 universal joint permits the long extension to tilt inward above base-local Z82. Introduce the tool centrally and slide its jaws outward under the flange after lowering. Verify the actual jaw projection and boss height against the published bounded-tool check; those details are not fully dimensioned by the manufacturer. A straight vertical extension at the nut radius would hit both flanges.

Keep the battery out while fitting the electronics plates. Each bare 160 x 56 x 2 mm plate has an 84.76 mm half-diagonal, below the 92 mm top opening radius. Retain the required thin M2.5 hex nuts, maximum 1.6 mm thick, and their underside washers on the bench (32 sets are allocated including spares) with small cured nonconductive epoxy side fillets, with no more than 3 mm underside projection. Keep all retained hardware and adhesive outside 8 mm-radius keepouts around the eight base-to-plate mounting axes and inside the FR4 outline. Lower the prepared plate centered, hold its FR4 underside at base-local Z44, slide to Y-93 or +93, then lower to Z34. During the slide, the retained hardware clears nominal Z40 screw tips by at least 1 mm and the plate top clears the base flange underside by 2 mm. Fit and wire the boards after seating the prepared plates. M2.5x14 PCB screws enter from above through two 0.5 mm head washers, the unchanged 6 mm spacer and the plate into each retained nut, with one 0.5 mm underside washer. Verify two complete exposed threads and at least 2 mm of actual motor-case clearance. Thin DIN 439 / ISO 4035 PCB nuts increase the nominal available screw-length interval compared with standard nuts. The nominal 14 mm screw tip is base-local Z30.6 with the specified 1 mm head-washer stack and a 1.6 mm PCB; actual stack dimensions and screw length must pass both gates. The eight base-to-plate nuts remain standard. The two Pololu 4091 regulators each have three M2 mounting holes and use six separate M2 screw/nut sets with matched 0.3 mm washers; M2.5 screws must not be forced through those holes. Trim the M2 screw working length to its measured stack and the same thread-exposure and motor-clearance gates. Unknown actual PCB hole positions are a physical fit gate: check actual templates before drilling or bonding and preserve the specified electronics layout unless a new clearance check supports a changed position. Adhesive retains nut position for assembly, while the clamped fastener carries the load. Lower the centered battery last; its half-diagonal is approximately 66.9 mm. Reverse that order for service. Do not treat the smaller top opening as a route for a fully populated plate at its final outer position.

The M2.5 plate screws are inserted from below before the shell. Their nuts need the same long extension and universal joint with a 5 mm socket. Start the socket at radius 75, lower its bottom to just above base-local Z45, shift outward and lower onto the nut. Use an 8-degree inward approach above base-local Z82. Keep the unpowered chassis securely supported for below-base screw-head access. The exact nominal paths and limits are in `cad/skirt-access-checks.json` and the assembly guide.

## Circular base and purchased hardware

The base is diameter 300 mm. Wheel-well subtraction is clipped at radius 147 mm so the exterior bumper remains continuous, rather than turning the circular fender into four open vertical notches. The revised tire centers are X +/-98, Y +/-58, Z17.7 in base print coordinates. Fully seated hub accommodation is abs(X) 95.5-100.5. The motor centers are X +/-70.5, Y +/-58, with case bottoms at local Z6.

At each of the three wheel-center positions, the check samples 5,000 interior points in each of four 63 x 29 mm tire envelopes, for 20,000 points per position. Radial samples stop 0.01 mm inside the nominal tire boundary. All three positions returned zero interior hits against the base.

The gearbox and metal motor-end envelopes are sampled separately. Each uses 5,000 points per motor, or 20,000 per envelope. The drawing-frame gearbox limits are X[-9.25,9.25], Y[-30.95,12.95], Z[0.05,22.39]. The metal-end limits are X[-11.15,11.15], Y[-56.95,-31.05], Z[0.05,22.39]. Mirrored placement uses the actual revised centers. Both envelopes returned zero hits.

The pack is rotated to 70 x 114 x 76 mm. The pocket has 76 x 116 mm clear plan space. Eight thousand interior pack samples returned zero hits. The two FR4 plates are 160 x 56 x 2 mm at X0, Y +/-93, with undersides at base-local Z34. Eight thousand points in each plate returned zero hits. Rotating the pack and narrowing the plates removed actual battery/clamp and plate/wheel conflicts found during review.

The outer rim check samples 720 angular positions at radius 149 on each of four heights: Z5,15,28,42. All 2,880 points are inside the base. This establishes sampled continuity of the bumper; it does not establish its impact strength.

The worst nominal tire/plate gap is 1 mm at the most inward accommodated hub. The tire roof clearance is nominally 2.8 mm. These are physical fit gates because the product page does not specify hub-recess depth, rubber deformation or assembled runout. Fully seat every real hub and check clearance under the intended load. Never leave a wheel partly engaged to match a nominal track.

## Concealed arm motion

The yaw origins are shoulder-local (-47,-94,42) and (53,-94,42). Each pitch origin is (-3,0,35) in its yaw frame. Both arm STL meshes include a 28 mm print-coordinate Z offset; remove that offset, rotate 90 degrees about X and -90 degrees about Z, then apply pitch and parent yaw.

The fixed yaw case and moving pitch case are sampled against the shoulder. The carrier vertices and all 2,756 plunger-arm vertices are checked against it at each of the nine independent yaw/pitch combinations -8,0,+8 degrees. The cap vertices are also checked against the pitch-servo case envelope. The final sampling returned zero interference hits in every tested combination.

The operating API, control code and browser slider are limited to 8 degrees. This replaces the former 12-degree allowance. The spherical cap was moved forward at its rear cut to preserve clearance at the tested limit; restoring 12 degrees without a new review is not supported.

The fixed socket has radius 29.2 spherical clearance and an explicit 64-facet, 44 mm front mouth. The moving spherical root has radius 28 and a 2.5 mm wall. The cap's print-local rear plane is X12. The front mouth permits the 40 mm plunger cup to enter from inside while the larger spherical cover remains behind the mouth.

## Assembly insertion paths

Final pose clearance alone did not prove assembly. Two additional checks found and corrected real blocked paths.

The detached arm first enters tip-forward from inside. At X-50 or +50, tilt it 20 degrees downward. Move the pivot from Y+30 to -20 while Z = 77 + (Y + 115) * tan(20 degrees), keeping the arm axis through the front opening at Y-115, Z77. Hold Y-20 while reducing the tilt to zero and use Z = 77 + 95 * tan(tilt). Then advance horizontally from Y-20 to -94 at Z77. The script samples 29 poses and all 2,756 vertices: 79,924 tested vertices per arm. Both sides returned zero hits. A 44 mm, 64-facet mouth replaced the earlier coarse polygon, which had clipped a few cup-edge vertices. The sphere is never pushed from outside through the smaller mouth.

The carrier enters through the central upper opening at X-29 or +29, Y-44. Its actual Y bounds are -10 to +20, so the right-hand entry corner is (64,-54), radius 83.74, within the 92 mm top opening. Lower its floor from Z130 to 46, move sideways to its final X-47 or 53 while keeping Y-44, move forward to Y-94, then lower to Z42. The full internal gunbox opening is 86 mm wide. The old combined diagonal path crossed a side wall and a remnant of the circular body wall.

An independent review checked this final carrier path on shoulder SHA256 `790aabbaea81385830751e0644091a6d3a3bdaf4328a83420313284df890ec16`. Each side used 87 poses times 300 carrier vertices, or 26,100 samples, and returned zero hits. The reproducible release script also checks the separate vertical, lateral, forward and seating stages. Install and connect the mechanism while the shoulder top is open; a straight vertical insertion at the final forward pivot is not the assembly method.

These paths require a specific assembly order. Fit the centered yaw servos, feed both detached arms and support them horizontally at shoulder-local (-50,-94,77) and (50,-94,77). Then insert the carriers with their pitch servos. Attach the arm horns and liners afterward, and install the speaker last. An installed pitch-servo case blocks the arm-feed path, so checking each part against the shoulder alone was insufficient to establish the order.

The focused regression checks each carrier and pitch case against both supported arm meshes and the shoulder at 87 insertion poses. Each side uses 26,100 carrier-vertex samples per obstacle and 20,880 pitch-case grid samples per obstacle. All eight combinations returned zero hits. The case grid spans the interior of X4..31,Y-6..6,Z13..49 relative to the moving carrier. Padded supports stay outside the body; actual horns, cables and support placement still require a careful hand fit.

## Opaque socket liners and visual checks

The fabric liners are functional hardware. Cut a 44 mm central opening in each 80 x 80 mm opaque stretch-fabric blank and use an overlapped radial seam. Bond the inner edge inside the moving spherical-cap rear rim and the outer edge around the fixed socket, leaving folds between them. The liner closes the view around the root without placing a servo-shaped box on the visible arm. Check opacity and clearance on the real assembly before use.

The digital visibility model uses a continuous opaque annulus from a fixed 33 mm radius at shoulder Y-111 to a 24 mm radius on the moving cap's rear rim. It is an idealized fabric surface, not a prediction of real cloth folds. The surrounding shoulder, complete skirt, neck, head and actual arm meshes are included in each ray scene.

The check uses five poses: neutral and the four combinations of +/-8-degree yaw/pitch extremes. At each pose, it casts rays from five azimuths (-100,-60,0,60,100 degrees) and three elevations (-30,0,45 degrees) toward 64 sampled points within the four servo-case envelopes. That gives 960 rays per pose and 4,800 total. The nominal opaque-liner model returned zero visible servo targets. The exterior drawings and operating animation show the opaque liners and complete shoulder skin; internal hardware appears only in labelled assembly cutaways.

This ray result does not prove actual fabric opacity or seam retention. A torn liner, an open seam or a liner trapped in a horn fails the physical acceptance test even if the CAD path is clear. Inspect from both sides, in front and below while running the full permitted circle.

## Adjustable head friction drive

The vertical head spindle and two 608 bearings retain the original separate head-load path. A fifth Adafruit 3777 motor turns a horizontal 63 x 29 mm Adafruit 3766 wheel inside the dome's 192 mm-ID drum. The rotating drum begins at neck-local Z52; the fixed opaque liner ends at Z51. The wheel occupies Z56.5-85.5, below the rotating spokes at Z91.

The carriage floor is neck-local Z29.2-32.2. Its origin moves radially from X61.5 through nominal contact at 64.5 to 65.1. The tire provides compliance. The outward stop at X90.1 and the slide slots limit travel. No calibrated contact force or guaranteed slip torque is claimed.

At all three positions, the actual drawing-derived gearbox and metal-end envelopes returned zero sampled hits against both neck and carriage. Carriage vertices above the intentional bottom support face returned zero hits against the neck. Five thousand tire samples at each position returned zero hits against fixed neck geometry. The released tire cleared the rotating drum. At the outward setting, sampled overlap was confined to the intended tire/track contact zone; it was not treated as a rigid-part collision failure.

The unused lower TT axle has a 15 mm-wide radial clearance slot through both carriage and fixed deck. Side walls and their fasteners were checked over the full radial adjustment. The final guide axes are (43,-50),(43,8),(83.5,-40),(83.5,8). Use 6 mm-OD washers above the slide and M3 nyloc nuts below the deck. The four clamps lock the selected setting. The jackscrew uses one captured M3 nut; a separate jam nut was removed because it added an unnecessary, poorly accessible lock.

## Tool and bearing access

Prefit the bearings, spacer, narrow shims, retaining washers and spindle while the neck is on the bench. The lower bearing retainer is not inserted through the finished neck's small service ports. Then fasten the neck to the shoulder through its four vertical tool channels. Install the head only after the motor carriage and released tire are ready.

Each slide clamp uses a 2.5 mm L-key with a 15 mm short leg. The checked tool envelope has radius 1.445 mm. Its vertical leg runs from neck-local Z34.9 to 49.9. The horizontal leg reaches from Y-112 for the front screws, or Y+112 for the rear screws, at Z49.9. Each path uses 32 vertical stations and 120 horizontal stations with 24 surface samples per station: 3,648 points per screw. All four paths returned zero hits against both neck and carriage at the contact setting.

Each neck M4 driver uses a 3 mm-diameter shaft at radius 97, sampled at 70 heights from Z13 to 110 and 24 angular points. All four paths returned zero hits. The printed 9.2 mm channels also provide space for the screw head and washer. The jackscrew is reached along positive X through the left service opening at Y-35, Z38; its captured nut stays fixed.

The remaining skirt and shoulder joints use the long ball-end 3 mm driver described in the assembly guide. The current combined-skirt driver and crowfoot paths supersede the prior two-ring tool approaches. Tighten the skirt before fitting electronics plates and battery so the base-joint nuts remain reachable.

## Remaining physical gates

- Verify actual MG92B case, ears, horn face and supplied-center-screw length. Padding is selected from real measurements.
- Fully seat the five wheel hubs. Check loaded ground-wheel runout and head-wheel height before printing or tightening around an assumed hub offset.
- Inspect the real socket liners in motion. They must hide every case, horn and wire without pulling on the mechanism.
- Set head contact only after free bearing rotation is established. Check two full turns by hand, lock all four clamps and repeat. Retest warm and in both powered directions at low duty.
- Weigh the completed robot and measure current, temperature, stopping and floor behavior. Small TT motors and four wide tires do not imply a proven payload or turning capability.
- Complete the proposed static base proof test and all electrical commissioning gates. No such physical test has been performed for this package.

## Primary component evidence

- [Adafruit 3777 dimension drawing](https://cdn-shop.adafruit.com/product-files/3777/3777_diagram.jpg): case, metal-end and axle envelopes.
- [Adafruit 3766 wheel](https://www.adafruit.com/product/3766): 63 mm diameter, 29 mm width and press-fit interface.
- [Pololu 4091 regulator](https://www.pololu.com/product/4091): three 0.086-inch holes for M2 or #2 screws per board.
- [Adafruit 2307 MG92B](https://www.adafruit.com/product/2307): overall 36 x 12 x 31 mm envelope and supplied-horn requirements.
- [Original TTGO T-Display board files](https://github.com/Xinyuan-LilyGO/TTGO-T-Display): confirmed original ESP32 board family.
- [Adafruit 1313 speaker drawing](https://cdn-shop.adafruit.com/product-files/1313/C2464-001_datasheet.pdf): 77.8 mm frame, 25.49 mm depth and 60 mm hole centers.
- [Bambu H2D specification](https://cdn1.bambulab.com/documentation/h2d/en/H2D_Laser_Full_Combo_20250305.pdf): printer envelope. Actual slicing evidence is recorded separately.
- [Wuerth 032825 thin hex-nut dimensions](https://eshop.wuerth.de/Hexagon-nut-low-profile-DIN-439-A2-stainless-steel-plain-shape-B-NUT-HEX-DIN439-B-A2-WS5-M25/032825.sku/en/US/EUR/): M2.5 thread, 1.6 mm height and 5 mm wrench size for the retained PCB nuts.
