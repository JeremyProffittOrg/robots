# STACK-10 independent mechanical review

Reviewed on 2026-09-11. The revised CAD has one base, full stackable body sections and ten distinct STL files. The universal pitch carrier is printed twice, for eleven printed pieces. Each STL is checked separately for one connected positive solid by `scripts/export_cad.py`.

The checks below found no sampled interference in the final listed parts. They establish nominal geometry and tool access. They do not establish printed strength, actual component fit, traction, or a load rating.

## Exact reviewed meshes

SHA256 values are for the files under `C:/dev/robots/dalek/stl`.

```text
01_base.stl          40a076687c45c4f8de67554f14a7ba382395e333e479f36c5acdbfd35ba62955
02_lower_skirt.stl   dfcf92bff7aa7db46451d0d82994102d1963fc492ad26a40dd076a2e85a74d5c
03_upper_skirt.stl   3693c825c18a91228aa893ebc82572126315ecb8c10062c029e5fadabb8c7590
04_shoulder.stl      c0e7d360d83daafcf8514e0d120f01d9a3e91fad118a31a4a05ba42c7b204c55
05_neck.stl          be168b3f1fd1abf81758478ea58f483ddcd44f1bd5bbe97e5dd200b3b0fb4793
06_head.stl          9def0e13c9499554883a6714d3dd01a2a5d54ca15a4bedaa9de8d56614a28669
```

## Component envelope checks

Commands ran from `C:/dev/robots/dalek` as PowerShell here-strings piped into `C:/Python314/python.exe -`. Existing `trimesh 4.12.2`, NumPy and rtree supplied the point-in-mesh checks. No dependency or test framework was added.

The final base check used `numpy.random.default_rng(37773766)`. Each of four wheels had 6,000 interior samples at each of three candidate axle-direction centres: X +/-120, +/-122.5 and +/-125 mm. Y centres are +/-60 mm. In the base's print coordinates, Z centre is 17.7 mm. Wheel diameter is 63 mm and width is 29 mm; sampled points stop 0.01 mm inside their envelope. The drawing's 18.6 mm gearbox width and 22.4 mm metal-end width were checked separately with 6,000 samples per motor for each envelope. The case-bottom datum is base-local Z6.

```text
base SHA256 40a076687c45c4f8de67554f14a7ba382395e333e479f36c5acdbfd35ba62955
wheel centre abs X 120 samples24000 hits 0
wheel centre abs X 122.5 samples24000 hits 0
wheel centre abs X 125 samples24000 hits 0
gearbox samples24000 hits 0
metal-tail samples24000 hits 0
```

The exact base sampling body is below. Pipe it into the Python command above to repeat the check.

```python
import trimesh, numpy as np, hashlib
m = trimesh.load_mesh('stl/01_base.stl', process=True)
rng = np.random.default_rng(37773766)
print('base SHA256', hashlib.sha256(open('stl/01_base.stl', 'rb').read()).hexdigest())
for centre in (120, 122.5, 125):
    total = 0
    for sx in (-1, 1):
        for sy in (-1, 1):
            a = rng.uniform(0, 2*np.pi, 6000)
            r = np.sqrt(rng.uniform(0, 1, 6000))*31.49
            q = np.column_stack([rng.uniform(-14.49, 14.49, 6000)+centre,
                                 60+r*np.cos(a), 17.7+r*np.sin(a)])
            q[:, 0] *= sx
            q[:, 1] *= sy
            total += int(m.contains(q).sum())
    print('wheel centre abs X', centre, 'samples24000', 'hits', total)
for label, lo, hi in [
    ('gearbox', [-9.25, -30.95, .05], [9.25, 12.95, 22.39]),
    ('metal-tail', [-11.15, -56.95, .05], [11.15, -31.05, 22.39])]:
    total = 0
    for sx in (-1, 1):
        for sy in (-1, 1):
            q = rng.uniform(lo, hi, (6000, 3))+[95, 60, 6]
            q[:, 0] *= sx
            q[:, 1] *= sy
            total += int(m.contains(q).sum())
    print(label, 'samples24000', 'hits', total)
```

The shoulder PCB was sampled inside X[-25.71,25.71], Y[108.05,109.95], Z[52.05,77.00]. The FS5103R case was sampled inside neck-local X[62.475,82.525], Y[-9.975,30.075], Z[34.05,71.15]. A fresh generator with seed 3777 sampled those boxes in that order, 6,000 samples each; both returned zero interior hits. The board's edges sit behind an integrated lip rather than floating outside the shell. The head servo's lowered floor leaves space for its shaft and supplied horn.

## Stack bolt tool access

A straight vertical driver does not reach every bottom flange through the smaller opening above it. The assembly requires a 150 mm long, 3 mm ball-end hex driver rated for at least a 20-degree working angle, plus a 7 mm open-end spanner for M4 nuts.

For each skirt/shoulder bolt, the check sampled a 3 mm diameter driver shaft at 120 evenly spaced axial stations and 24 points around each station. Its bottom centre is local Z8 at the bolt radius. Its top centre is at the part's nominal height, moved inward to radius 103 mm for the lower skirt and 88 mm for the upper skirt and shoulder. Rotate that path through 0, 90, 180 and 270 degrees. The lower skirt uses bottom radius 137 mm on X and 127 mm on Y; the upper skirt uses 112 mm; the shoulder uses 97 mm.

```text
02_lower_skirt samples11520 hits 0
03_upper_skirt samples11520 hits 0
04_shoulder samples11520 hits 0
```

Resulting driver angles from vertical are 18.43 degrees at the lower skirt's X bolts, 13.24 degrees at its Y bolts, 14.62 degrees at the upper skirt and 5.59 degrees at the shoulder. Each named part's final mesh was checked after the decorative bumps were hollowed.

The neck uses a different tool path because its integrated servo cradle blocks the long driver. Use a low-profile 3 mm L-key with an 18 mm short leg. The sampled vertical leg runs at radius 97 mm from local Z8 to Z26. Its horizontal leg runs inward at Z26, between the first neck ring's Z19 top and the second ring's Z30 bottom. Thirty-seven vertical stations and 150 horizontal stations, each with 24 surface points on a 3 mm diameter shaft, give 4,488 samples per bolt.

```text
neck L-key angle 0 samples 4488 interior hits 0
neck L-key angle 90 samples 4488 interior hits 0
neck L-key angle 180 samples 4488 interior hits 0
neck L-key angle 270 samples 4488 interior hits 0
```

Attach the lower skirt to the bare base before installing the raised prototype boards. Their components can obstruct the spanner handle at the front and rear base joints. Tighten the neck joint before installing the servo and rotating head. The documented access paths assume those assembly stages. They do not prove clearance for arbitrary wiring or component placement.

## Inspected load and bearing paths

The base has a continuous 6 mm floor, perimeter walls, longitudinal ribs, transverse ribs and integrated motor saddles. Motor clamp connections terminate at the floor; no crossbar intrudes into the motor case. The stack flanges are 18 mm wide, so the 4.4 mm M4 bores remain closed at their inner edges. The wheel-well roof ends at local Z52, above the nominal tire top at Z49.2.

The lower 608 bearing occupies neck-local Z40-47; a purchased 12 mm inner-race spacer occupies Z47-59; the upper bearing occupies Z59-66. Narrow 8x12x1 mm shims at Z39-40 and Z66-67 transmit axial load to the inner races. Three purchased retaining washers and screws at each end retain the outer races. The printed head foot starts at neck-local Z67. The integral hub, spokes and dome rotate together; the fixed bearing tower carries the head load. Both belt grooves have nominal world centre height 461.3 mm. A 24 mm axial access bore admits a socket for the M8 nut. These are dimensional/source inspections, not a measured bearing preload or friction test.

## Physical checks still required

- The 3766 product page gives its outer envelope but no hub-recess depth. The revised well allows a range of inward wheel positions, rather than requiring the illustration's X122.5 centre. Press each real wheel fully onto its shaft and verify retention and clearance. Do not stop insertion early to preserve a nominal track. At X120, the uncompressed outer envelope has only 0.5 mm inboard clearance; check tire deformation under load. If full engagement requires a centre outside X120-125, revise that well before printing the complete set. This fit is not digitally verified.
- The motor drawing's axle-height reading is a nominal 11.7 mm datum. Measure the actual case, shaft and any padding. All four wheels must meet the floor together.
- Confirm the actual T-Display revision, horn dimensions, bearing fits and clearance compensation on the first prints. Do not scale an STL to adjust a local fit.
- Prove the base using the assembly guide's unloaded/loaded tests. For a static print-strength check, support the four motor floors on rigid blocks without motors, apply twice the intended complete robot mass at the actual battery/stack load points for ten minutes, then unload and inspect. No such physical test has been performed here.
- Weigh the sliced and built robot. A mesh material bound is neither installed mass nor a motor payload rating. Current, temperature, steering, stops and free head/arm movement remain physical commissioning gates.

## Primary component evidence

- [Adafruit 3777 dimension drawing](https://cdn-shop.adafruit.com/product-files/3777/3777_diagram.jpg): gearbox, metal end and axle envelopes.
- [Adafruit 3766](https://www.adafruit.com/product/3766): 63x29 mm wheel; press-fit interface.
- [FeeTech FS5103R specification, 2021-07-22, page 5](https://evelta.com/content/datasheets/501-FS5103R.pdf): manufacturer drawing, reproduced by a distributor. The case is 40.15x20.15x37.2 mm, the shaft is 10.05 mm from the case centre, the mounting-ear span is 54 mm and the spline top is 42.85 mm above the case bottom.
- [Adafruit 1609](https://www.adafruit.com/product/1609): 51x81 mm prototype board and 73.7 mm mounting-hole spacing.
