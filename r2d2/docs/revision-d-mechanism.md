# Revision D centre-leg mechanism

Status: digital prototype under integration, 2026-09-13. No physical fit, proof load, measured centre of gravity or motor radial-load qualification has been completed. Current source is cad/kinematics.scad, cad/printed-frame.scad, cad/stance-lock.scad, cad/post-limits.scad and cad/ground-contact.scad. The GN412/30-degree proposal is retired.

## Geometry and load path

Coordinates are millimetres: X across the shoulders, Y forward, Z up. The shoulder axis is Z390; wheel axes are Z31.5 when on the floor. Centre ankle Z113; side feet X−165 and X165. Each foot has four Adafruit3766 wheels on two Adafruit3777 motors. The head uses one additional motor and wheel.

One printed chassis holds four228mm HFS5-2020 rails at X±72,Y±52. Printed keys and cross-pins retain them. Two180mm rails reinforce the whole side-leg prints. A366mm long,12mm steel shaft joins both legs. Four SKF6201 bearings support the chassis on the shaft. Steel collars and spacers locate the shaft; printed caps retain the outer races. Shoulders rotate together. They do not provide independent walking motion.

The centre guide begins at Y40,Z240 and inclines35degrees forward from vertical. A296mm HFS5-2020 post slides through four acetal liners,18×178×2.8mm. Guide stations are centred at local−130 and−20mm. Integral end lips retain the liners. There is no separate guide cap or guide-cap screw.

The Actuonix P16-100-256-12-P lies parallel to the guide at local X55. Fixed eye local−37; moving eye gives147mm eye spacing at zero stroke. Use its100mm stroke only from2 to98mm. Independent NC switches stop retraction at0.8mm and extension at99.2mm. These are adjustment targets, not tolerances obtained automatically from a print.

Upright ankle floor contact occurs at45.038373mm stroke. At98mm the body pitches12.832480degrees back. Below contact the shoulder stays locked upright and the foot rises. Two-foot mode is stationary standing; firmware refuses wheel drive.

SKF SA12E dimensions:12mm bore,35mm maximum head diameter,10mm inner-ring width,8.5mm outer-ring width,54mm centre-to-end length and18mm raceway diameter. Its last28mm is guaranteed threaded: centre distances26–54mm. The printed heel stop touches only the28–32mm shank band. Lifted foot pitch is3degrees heel-down. In-plane axle rotation differs from SKF's10degree out-of-plane misalignment limit. See rod-end-interface-review.md for dimensional evidence and envelope uncertainty.

## Positive shoulder lock

Use GN817-6-6-M12X1.5-GK. Its6mm steel pin faces+X. Tip-exit face X141.3; steel12×28×22mm receiver begins X141.8. Two6.2mm bores at45mm radius select the upright and deployed angles. The receiver seats in the right leg, behind a separate printed keeper. Drill pilots with lock_drill_jig.stl, then finish and inspect actual bores. The jig does not replace alignment or reaming.

Gross pin engagement is5.5mm. Screening reserves0.5mm tip allowance,0.12mm sensor setting,0.10mm switch differential and0.05mm additional clearance. Remaining indicated engagement must exceed4mm. Measure the actual tip and receiver; reject the assembly if allowances do not hold. Generic plunger load charts do not establish this exact part's certified working load.

The goBILDA2000-0025-0002 servo pulls a carriage from the GN817 M5 draw stud. A1mm washer and2.7mm thin nut fit on the7mm stud. The carriage carries spring force; steel pin, receiver and reinforced shoulder carry stance load. A trimmed goBILDA1900-0025-0104 horn drives a9mm follower at16mm radius. The open-sided slot permits withdrawal force only. Cam return cannot force the pin into a misaligned receiver; the spring seats it.

Two OmronSS-01 direct-plunger SPDT switches independently report fully engaged and fully withdrawn. Do not substitute SS-01GL lever switches. Set0.10±0.02mm overtravel at each endpoint. Measure actual operating and return positions. Separate NO/NC checks validate both switches. Neither post position nor loss of engagement proves full withdrawal.

Keep the carriage withdrawn throughout tilt. At the target receiver, stop, return the servo and creep within the search window until engagement is stable. The unpowered P16 supplies interim holding. A restrained prototype must verify back-drive resistance and pin seating/withdrawal under actual shoulder torque.

## Centre-foot support and steering

A separate OmronSS-01 reads the floor probe. The free printed probe projects0.4mm below the wheel tangent plane. Floor contact lifts it to that plane. A shoulder stops additional travel at+0.3mm. A SEEGER-Orbis RA3,2 DIN6799 E-clip retains its4mm stem at the3.2mm groove. Count the clip separately and install it before the switch. Adjust actual operation at the wheel tangent plane. Confirm the switch cannot carry robot weight or be overdriven at the stop.

Steering uses the same goBILDA servo and16mm horn hole. Neutral link centres are62.096699mm. Two igus KBRM-03-MH ends connect a fitted M3 rod. A3.8mm K&S9822 brass sleeve adapts the horn's4mm hole to the M3 pivot. Recess the sleeve so clamping does not lock the joint. Yaw is limited to±8degrees.

Motor cases contact printed saddles. Fit0.2mm printed shims to share contact without crushing the cases. Ties retain motors; they are not the only vertical load path. The TT motors have no established whole-robot radial-load qualification in this package. Loaded wheel, shaft and gearbox tests remain mandatory.

## Mechanism assembly order

1. Deburr bearing and sliding surfaces. Measure sockets and bores before inserting purchased parts. Reject cracks, delamination and distorted sockets.
2. Insert all four acetal strips through the empty guide. Shift them sideways between their retaining lips. Insert the post only after all strips are seated. Check free travel without the actuator.
3. Fit body rails, keys and cross-pins. Insert the M8 head bolt from below before the shoulder shaft. Fit battery restraint and fixed actuator clevis.
4. Insert the lower shell45degrees from final orientation. Raise it1.3mm above its seat before rotating into alignment. Lower onto three locating pins and fit the single base screw. Fit upper shell from above, then its single seam screw.
5. Fit shoulder bearings/caps, shaft, steel spacers, collars, hubs and reinforced legs. Fit the right receiver and keeper before closing its hub cover. Support the body externally and confirm free rotation with the lock withdrawn.
6. Install the GN817 mount after the shells. Fit carriage, draw washer/nut, servo, trimmed horn and follower. Calibrate both lock sensors with the body supported and actuator disconnected. Check the complete6mm pull.
7. Assemble centre axle, rod end, steering servo, link and floor probe. Check heel-stop contact over the28–32mm shank band. Check floor clearance through lifting and landing, including±8degree yaw.
8. Fit actuator and travel-limit flag. Secure the flag with its M5 screw into the post end. Adjust hardware cutoffs with a current-limited bench supply before software movement.
9. Install control carrier and wiring. Keep wires away from the post, shaft, carriage and rotating head. Repeat the complete manual sweep with all wires present.
10. Weigh the complete robot and measure its centre of gravity. Perform restrained sensor and drive tests before loaded stance tests and cosmetic finishing.

## Head rotation

Both608 outer races rotate inside the dome neck. Inner races clamp on a stationary M8 bolt. Steel inner-race spacers and washers must not contact the rotating outer spacer or printed cap. The three-screw bottom cap retains the lower bearing. Tightening the top locking nut must not clamp the rotating dome to the frame. Rotate the dome manually through360degrees and check play before powering the internal friction wheel.

## Digital checks and physical limits

python scripts/export_cad.py --check-only requires current hashes and closed, consistently wound, single-positive-solid meshes. python scripts/slice_structure.py uses installed H2D0.4mm/0.20mm profiles, six walls and40% gyroid. Its installed-model mass excludes supports and brim; it is a prediction.

python scripts/check_printed_fit.py screens actual meshes at stated points and insertion poses. It is not a continuous collision proof. python scripts/check_kinematics.py uses current sliced masses, explicit hardware mass allocations,0.5mm samples in both directions and centre-of-gravity uncertainty. It checks floor clearance, static support, guide coverage, receiver geometry and factored actuator load.

Printed strength, friction, motor radial load, lock proof load and actual power-loss behaviour remain physical tests. A digital PASS does not qualify a physical prototype. Component evidence is in printed-frame-research.md and rod-end-interface-review.md. The explicit purchased-piece ledger governs procurement; this note does not authorize purchases.
