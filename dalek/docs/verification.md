# Digital verification and physical limits

ROUND-9 combines the lower and upper skirts into one 213 mm print. The robot remains nominally 563.8 mm tall. The revision removes one printed piece and one bolted interface; it does not establish a measured increase in strength. Physical fit, adhesion, base strength, loaded driving and stopping still require the commissioning gates in `assembly.md`.

## Reference review and preserved behavior

The existing 100-image reference inventory and appearance review remain applicable. Each source has its original URL, dimensions, file/pixel hashes, observation and design implication. No reference image has been redistributed with the package.

Eight other STL designs are byte-identical to ROUND-10. They account for nine physical prints because the pitch carrier is used twice. Firmware, circuits, original MP3s, the four ground drives, rear T-Display, concealed arm mechanisms and adjustable head friction drive are unchanged. PCB mounting hardware and access instructions are updated for the deeper shell.

## Printable geometry

Command:

```powershell
python scripts/export_cad.py --check-only
```

Result: nine watertight, consistently wound STL designs, each one connected positive solid, for ten printed pieces. The total solid-material upper bound is 2995.9 g. This is a mesh-volume calculation, not measured or sliced print mass.

The new `02_skirt.stl` is 300.331848 x 300.331848 x 213 mm. Its SHA256 is `ff1baa0536e36c0730d69f5cf8004e069f4fe4e430026d6f3e6bc734a125146e`. All 39,728 faces are nondegenerate and every edge has two adjacent faces. The final mesh replaced a rejected export with a microscopic internal surface at the old rib-cone junction. A single revolved polygon now forms the reinforcing rib.

The old lower and upper skirt STLs are removed. The new part retains both outer slopes, all four hemisphere rows, trim and the visible middle band. It retains the base and shoulder interfaces but replaces the middle bolted flanges with an integral tapered rib. Comparison of 8,496 exterior rays against the former pair differed by at most 0.000004554 mm. The other eight STL hashes are unchanged.

The 213 mm part is below the 320 mm maximum-minus-5 mm height target. Its requested 5 mm brim allowance also fits the H2D footprint. The full printer envelope is not stretched or scaled to obtain this result. See `cad/validation.json` and `bom/printed-parts.csv`.

## Mechanical and assembly access checks

Commands:

```powershell
python scripts/check_mechanical.py
python scripts/check_skirt_access.py
```

The complete current mechanical run passed 118 checks across 554,129 samples against the nine current STL hashes. This includes merged-skirt height, interfaces, bore and long-driver checks, unchanged mechanisms and 4,800 current-body sight rays with no visible servo targets. These finite samples are not an exact continuous collision proof. Results and limits are in `cad/mechanical-checks.json` and `docs/revision-review.md`.

The focused access report passes 61 checks across 868,363 sample evaluations. Twenty affected plate/retained-hardware checks were rerun after the final insertion-height change; 41 unchanged tool and battery checks were retained only after their mesh hashes matched. The final incremental command was `python scripts/check_skirt_access.py --plates-only`. A full run remains available. See `cad/skirt-access-checks.json`.

Access relies on the specified 250 mm driver, crowfoot, universal joint and extension. The crowfoot holds the M4 nut while the screw turns. The M2.5 plate nuts require a 5 mm socket. Actual tool profiles must fit the documented conservative envelopes; a tool name alone does not prove clearance.

Retained PCB nuts, washers and adhesive must project no more than 3 mm below the FR4. The plate underside travels at base-local Z44 before moving outward, then lowers to Z34. All underside fittings must remain within the plate outline and wholly outside the 8 mm-radius keepouts around the eight plate-to-base mounting axes. Actual PCB hole locations are a physical template-fit gate. The checker does not invent mounting-hole coordinates from board outlines or certify arbitrary populated plates.

Boards are fitted from above after the plates are seated, with the battery absent. Fasteners must match the actual board holes. The Pololu 4091 regulators have three M2 mounting holes per board. Pre-retained nuts and measured screw lengths avoid inaccessible underside work. Verify the specified motor-case clearance, thread engagement, absence of trace contact and service access before final assembly.

The separate eight arm-order checks across 187,920 samples are retained from ROUND-10. Their four relevant STL hashes are unchanged. `cad/arm-assembly-checks.json` preserves that provenance. The required order still feeds and supports the arms before installing pitch-servo carriers; horns and opaque fabric liners follow.

## Actual H2D slicing

Command:

```powershell
python scripts/slice_h2d.py --parts 02_skirt
```

The merged skirt passed an actual Bambu Studio 02.08.02.61 slice using the installed H2D 0.4 mm machine profile in isolated temporary state. Supported assembly-list input places it at X162.5,Y160 without changing the printer/nozzle geometry. Exact triangle count, rigid transform, full 213 mm deposited height, material, process settings and all deposited model/support/brim paths were checked.

The new skirt's bead bounds are X7.7093..317.2917 and Y5.2093..314.7917 mm, within the left 325 x 320 mm area. It predicts 527.879 g of installed model and about 1033.87 g total PLA including supports and brim, with a 23 hour 45 minute 40 second print time. One 1 kg spool is insufficient; allow at least 1.14 kg for this job with reserve and plan filament capacity or a compatible change procedure.

The release report combines this new slice with eight unchanged slice records whose exact STL hashes were checked. It covers nine designs and ten physical prints:

- Installed printed model: 2345.25 g.
- Total filament including support and brim: 3951.62 g.
- Sequential print time: 406685.32 seconds, about 112.97 hours.
- Compared with ROUND-10: 83.95 g less installed plastic, 121.44 g less filament and 3 hours 18 minutes 57 seconds less predicted print time.

The BOM keeps 3 kg each of PETG and PLA as supply allowances, including reserve for the long skirt print. These quantities are not claimed deposited mass. Bambu omitted a separate Brim feature on some retained supported parts despite the requested brim setting; that behavior remains explicitly recorded. All actual generated deposition fits. Inspect adhesion paths before printing.

## Controls, wiring and media

The unchanged firmware and filesystem builds retain their prior passing results: RAM 45,416 bytes, application flash 995,025 bytes and a 2,097,152-byte LittleFS image. Native controls and browser tests already cover the 8-degree arm limit, head PWM cap, reversal delay, fault stop, command leases and no automatic restart. These checks were not needlessly rerun for an unchanged electrical design. All 24 original MP3 hashes remain unchanged. The wiring schedule remains 185 rows with four SVG circuit sheets.

The drawing package now has 15 PNGs: six overview/mechanism sheets and nine component drawings. Five additional CAD previews serve the PDF. Their manifest verifies current source hashes and ZIP contents. The video shows one skirt installation and the plate-first, battery-last sequence, with nine designs and ten prints. Full FFmpeg decoding and FFprobe validate 120 seconds, 2880 frames, 1920 x 1080, 24 fps and AAC audio. Operation is labelled as simulation.

The PDF is rendered and visually reviewed before delivery. The existing GitHub Actions/OIDC workflow publishes the committed PDF and video to private S3 storage and verifies downloaded file hashes. The final email contains the PDF and a signed video link with an explicit expiry. Workflow and SES acceptance identifiers are recorded in the execution plan.

## Physical limits

No robot was printed, wired, powered or driven during this revision. The predicted 2.345 kg of installed plastic excludes the battery, motors, wheels, servos, electronics, fasteners, fabric and finish. Weigh the finished robot and complete the physical checks. A continuous printed skirt and fewer joints do not by themselves prove higher strength, reliable traction or a payload rating.
