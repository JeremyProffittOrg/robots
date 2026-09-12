# MOUNT-1 mechanical revision review

Reviewed2026-09-12. Ten STL designs produce fourteen prints with the four motor clamps, or ten prints when motor ties replace those clamps. The round base remains300mm in diameter and the complete robot563.8mm tall. This review describes digital evidence, not a physical load rating.

## Changes and assembly consequences

- Four identical printed hook clamps each use one M3 screw. Each toe slides inward4mm. Two independent longitudinal ties per motor provide the alternative. Front and rear routes are staggered so opposing ties do not touch. Open wheel wells admit the mated motor/wheel units while the outer bumper remains continuous.
- One216mm board platform has a6mm deck and four integral legs. It prints deck down at112mm height. Its installed underside is base-local Z140. The battery rests on the base. PCB hardware projects no more than3mm below the deck; the largest bare SLA terminal envelope ends atZ111, leaving26mm. Attached battery contacts, ties and wiring stay belowZ130.
- The cradle accepts the original Bioenno or the specified Power-Sonic7Ah/14Ah SLA cases. The largest bare envelope is100 x153 x103mm. Two padded long ties retain one battery. Foam blocks locate smaller cases. Capacity labels alone do not establish fit.
- Shoulder and neck form one186mm print. Arm boxes shrink from94 x58 x106 to90 x52 x103mm. Servo cases accept M2 ear screws or ties. Supplied spline screws and horn-to-print fasteners remain mandatory. Small root flats clear the maker-derived servo envelope without changing the shaft axes.
- The speaker uses an open rear frame at upper-local Y52.5..56.5. Its body ends atY81.99. This frees the bottom-entry arm paths. Fit arms and lower-bearing hardware before the speaker and rear controls.
- The fixed head deck and bearing tower are integral with the upper shell. The moving carriage remains separate to preserve3.6mm adjustment. Fit its underside nuts while the upper shell is removed. Retract the tire and leave the head off while fastening that shell.
- Both body joints have captured standard M4 nuts: eight M4x20 screws, eight nuts and eight screwhead washers. No washers go in the nut pockets. Skirt-top bosses use the same6.7mm roof as the base pockets. Four specified driver approaches replace inaccessible loose-nut work.

Full paths, tools, fastener stacks and physical fit gates are in mechanical.md. The source notes are base-mounts-revision.md, upper-mounts-revision.md and battery-options-research.md.

## Reproducible checks

Run from C:/dev/robots/dalek:

    python scripts/export_cad.py --check-only
    python scripts/check_base_mounts.py
    python scripts/check_upper_mounts.py
    python scripts/check_arm_assembly.py
    python scripts/check_mechanical.py
    python scripts/mesh_queries.py

Final records pass ten watertight connected meshes,309 base/platform checks across1,117,361 evaluations,68 upper checks across1,650,576 samples,8 carrier-insertion checks across417,648 samples, and110 general mechanical checks across374,697 samples. Every report mesh hash matches the final file. General checks use the corrected30mm outer fabric radius and include4,800 visibility rays with no visible servo targets.

The point-containment helper compares two independent near-axis parity rays and uses the original trimesh query on disagreements. A4,400-point final-mesh comparison found zero differences:1,269 inside and3,131 outside. It includes points close to surfaces and known solids/voids. Recorded time was11.363seconds for the original query and1.010seconds for the helper. No collision tolerance was relaxed.

The base checker also uses a conservative continuous projection bound for lowering the skirt around the populated chassis. Other motion/tool checks use finite poses. Actual horns, servo offsets, PCB holes, connectors, tie heads, print error, paint and tool handles remain measured fit gates.

## Actual H2D slices

Eight changed parts were actually sliced:01_base,02_skirt,04_shoulder,07_pitch_carrier,08_plunger_arm,09_emitter_arm,11_motor_clamp and12_electronics_platform. The exact unchanged head and carriage slice records were retained. All ten hashes match. The script checks stock machine geometry, complete deposited height and model/support/brim bead bounds in the left325 x320mm area. It never contacts a printer.

    python scripts/slice_h2d.py --parts 01_base 02_skirt 04_shoulder 07_pitch_carrier 08_plunger_arm 09_emitter_arm 11_motor_clamp 12_electronics_platform

The clamp-option total is4,212.07g filament,2,469.59g installed plastic and448,159.36seconds, or124.49hours of sequential printing. The213mm skirt uses1,040.72g PLA and the186mm upper shell1,235.49g PETG. Supply at least1.15kg and1.36kg respectively with reserve. Neither job fits on one1kg spool.

## Limits

No robot was printed, wired, powered or driven during this revision. No physical strength, impact, fatigue, payload or traction rating is established. The14Ah battery adds several kilograms. Its defined fit and electrical compatibility do not establish loaded driving. Complete the hard-floor current, temperature and stop tests; retain the lighter battery if an SLA build fails.

The old FR4 access checker is replaced by the current base/platform checks. The older merged-skirt comparison record is historical ROUND-9 evidence, not a current ten-part verification report.
