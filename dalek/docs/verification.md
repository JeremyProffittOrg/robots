# Digital verification and physical limits

FACET-1 has twelve full-height flat skirt panels in one print, within the same ten STL designs: fourteen prints with the four motor clamps, or ten when motor ties replace them. The platform and its legs form one print. Shoulder and neck form one186mm print. The skirt is213mm and the robot remains563.8mm tall. Both motor and servo-case retention options are documented.

## Geometry and access

The following commands passed from C:/dev/robots/dalek. Their reports identify exact current mesh hashes.

- python scripts/export_cad.py --check-only: ten consistently wound, watertight meshes, each one connected positive solid. All fit the stock H2D single-nozzle envelope and recorded brim allowances. Solid-material volume bound:3,202.8g, not sliced or measured mass.
- python scripts/check_base_mounts.py:346 checks and1,117,327 evaluations. Adds actual panel-plane, normal,1.8mm wall and240mm rib measurements to the existing mounting tests. Covers motor/wheel installation, four hook clamps/screws, alternative ties, both platform-foot options, batteries, populated terminal clearance, captured nuts, tools and skirt installation.
- python scripts/check_upper_mounts.py: retained68 checks and1,650,576 samples. Covers servo ears and retention, yaw-servo entry, bounded screw/nut tools, detached-arm paths, head/bearing entry, speaker clearance and all four body-joint driver approaches.
- python scripts/check_arm_assembly.py: retained8 checks and417,648 samples. Both carriers enter through the left lower opening before moving to their final positions. Both supported arms are included.
- python scripts/check_mechanical.py:110 checks and374,697 samples. Includes wheels, batteries, skirt interfaces, arm extremes and head adjustment. The30mm outer fabric radius gives zero visible servo targets in4,800 current-body rays.
- python scripts/mesh_queries.py: retained4,400 samples and zero differences from the original query on the final upper mesh. Two near-axis rays must agree; disagreements use the original query. Tolerances are unchanged.

Only the skirt STL changed. The nine other STL hashes match the MOUNT-1 release; upper, carrier-entry and query-comparison evidence is retained for those exact unchanged meshes. All current general/base/facet checks were rerun. The old curved skirt failed all36 panel-plane, normal and wall tests.

Finite sampling does not prove every possible continuous pose. Skirt lowering separately uses a conservative continuous projection bound. Actual servo shaft offsets and ear holes are not fully dimensioned by the maker. The guide specifies measured fit gates and slotted supports.

## Printing and mass

The H2D script uses isolated installed Bambu Studio settings and never contacts a printer. The complete faceted skirt was newly sliced. Nine unchanged slice records were retained only after verifying their exact STL hashes. All ten source hashes and deposited heights match. All generated deposition fits the stock left325 x320mm area. Requested brim settings do not prove a separate brim was generated; the report records actual feature output.

The clamp option predicts4,180.82g filament,2,473.98g installed plastic and124.28hours of sequential printing. The skirt uses1,009.47g PLA and predicts23 hours55 minutes37 seconds: allow1.12kg with reserve. The upper shell uses1,235.49g PETG and predicts39 hours10 minutes11 seconds: allow1.36kg. Both need sufficient capacity or compatible filament changes.

The electrical generator reads the current installed-plastic prediction. Including only plastic, five motors/wheels, four servos and the battery gives incomplete totals of3.573kg Bioenno,4.843kg7Ah SLA and6.653kg14Ah SLA. Other electronics, bearings, fasteners, wiring, padding and finish must be added. Actual weighing is required.

## Circuits, control and media

python electronics/generate.py passed185 wiring rows, five parseable circuit sheets and three battery cases. All pre-existing nets, endpoints, wire gauges and colors remain unchanged. The battery-input note and fifth sheet explain the single fused SLA adapter and matched chargers. Regulator outputs and the11.2V stop/12.0V re-arm thresholds remain unchanged. Low voltage stops motion but leaves logic powered: switch MAIN off and unplug after a low-battery stop and between uses.

Firmware, pins and24 original MP3 files are unchanged. Prior compile/control-test evidence applies to those same bytes. The earlier build reported45,416bytes RAM,995,025bytes application flash and a2,097,152-byte filesystem image. No new physical control result is claimed.

python scripts/render_drawings.py passed16 engineering PNGs, five CAD previews and the ZIP. It checks quantities, transforms, board separation and unchanged source hashes. All final views were inspected. Paint boundaries use render-plane cuts without changing STL surfaces.

python scripts/render_video.py passed the new120-second assembly and simulated-operation video:2,880frames,1920 x1080,24fps,H.264 video,AAC audio,full FFmpeg decode and47 unchanged source hashes. Narration timing rejects overrunning clips. The video includes both motor options, battery choices, the platform, lower-entry upper assembly, adjustable head drive and simulated motion. It is not physical test footage.

The PDF is built from current guides, BOM and five circuit sheets, then rendered and visually checked before publication. The existing GitHub Actions/OIDC workflow publishes exact committed PDF/video bytes to private S3 and checks full downloaded hashes. The requested HTML email contains the PDF and a tested video link with explicit expiry. Workflow and SES acceptance identifiers are recorded in the root execution plan.

## Physical acceptance

The design is not physically validated. Complete actual fit, supported base proof-load, retention, connector-clearance, opaque-liner, hand-rotation, stop and loaded-driving tests. Four small TT gearmotors have no published robot payload rating. A stronger base and a fitting14Ah case do not establish traction, gearbox life or turning ability. Keep the5V supplies and current limits. Use the lighter battery if the SLA build fails its loaded tests.
