# FACET-1 skirt revision review

The skirt is now twelve full-height planar panels arranged around the existing circular base. Its main faces follow a single linear taper from150mm vertex radius atZ0 to110mm atZ210. Circular collars and the3mm top register keep the existing interfaces; total skirt height remains213mm. The round middle band and old slope break are removed.

The four hemisphere rows remain atZ26,76,136,186, centered on the twelve panel normals at15+30k degrees. Each bezel axis is normal to its sloped panel, tilted10.425026degrees upward from horizontal. The23mm bezel extends1mm above the face. Narrow relief follows the actual panel-edge slope. These are changes to the actual STL surfaces, not rendered shading alone.

## Geometry and fit evidence

The exported skirt is300 x300 x213mm,36,664 nondegenerate faces, one connected watertight positive solid. SHA256:5149241c3c95dc439403d857803fc50b5022a8757f729c8dbcf69a8435757b56. The other nine STL files are byte-identical to the preceding MOUNT-1 release. Hardware, upper assembly, batteries, firmware and all24 original MP3 files retain their design.

python scripts/check_base_mounts.py passed346 checks across1,117,327 evaluations. The37 new checks measure twelve continuous outer planes, their normals, true1.8mm normal wall thickness away from thicker features, and the faceted reinforcing rib. Maximum sampled plane error is0.000005332mm and thickness error0.000007671mm. Rib clearance measures239.999989..239.999991mm across flats. The prior curved skirt failed all36 panel-plane/normal/wall checks in the negative control.

The existing mounting checks also passed, including all eight captured body nuts, battery/platform space and the long-driver paths. A conservative continuous projection bound leaves3.044mm for lowering the skirt around the populated chassis. This bound includes triangle portions above the chassis and is intentionally conservative.

python scripts/check_mechanical.py passed110 checks across374,697 samples against all ten current mesh hashes. Its4,800 sight rays found no exposed servo targets with the specified opaque liners. The68 upper-mount checks,8 carrier-entry checks and4,400-point query comparison are retained on unchanged relevant mesh hashes. They are not relabelled as newly run tests.

## H2D printing

python scripts/export_cad.py --check-only passed all ten connected meshes and their recorded H2D brim envelopes. The part count stays fourteen with motor clamps, or ten with motor ties. The robot remains563.8mm tall.

python scripts/slice_h2d.py --parts 02_skirt passed the complete new skirt in the stock left325 x320mm H2D nozzle area. All model/support/brim paths and full213mm deposited height were checked. Nine unchanged slice records were retained by exact hash.

The skirt predicts1,009.47g PLA including support,536.202g installed model and86,137.406seconds (23hours55minutes37seconds). Allow at least1.12kg with reserve; one1kg spool is insufficient. The full clamp-option package predicts4,180.82g filament,2,473.98g installed plastic and447,407.06seconds (124.28hours sequentially). These are slicer estimates, not physical consumption or finished mass.

## Limits and deliverables

Current PNGs, CAD previews, PDF and video show the actual faceted mesh. Their source hashes identify the generating files. The body still prints as one complete skirt; there are no extra loose panel STLs. The original circular base, collars, mounts, arms, head and battery options are retained.

No physical print, strength, traction or loaded-drive test was performed. The prior physical commissioning gates remain required. Older ROUND-9 and MOUNT-1 records remain historical evidence for their own hashes; use the current FACET-1 geometry/slice reports for this skirt.
