# Dalek fabrication package

## Outcome

Create a complete digital fabrication package in C:/dev/robots/dalek for a printed Dalek below 914.4 mm tall, with four Adafruit 3777 motors and 3766 wheels, rear TTGO T-Display ESP32 screen, Wi-Fi station/AP control, circular arm motion, continuous head rotation, original MP3 voices, wiring diagrams, mounting parts, bill of materials, and extensive assembly instructions.

## Non-goals

No purchase, physical fabrication, remote firmware flashing, cloud application, scheduled automation, television audio extraction, or claim of hardware validation. No unrelated repository changes.

## Files

C:/dev/robots/plan.md; C:/dev/robots/dalek/{README.md,docs,cad,stl,electronics,bom,firmware,audio,scripts}. Generated output is part of the requested deliverable. Use existing OpenSCAD, PlatformIO, FFmpeg and Python tools.

## Locked decisions (user-confirmed; do not revisit)

2026-09-11: "email me the design pdf when done"

2026-09-11: "extensively research and create a Dalek robot that is 3d printed, controllable via a wifi interface which can be attached to a wifi network or work as an ap, using the ttgo tdisplay esp32, which should have the dxisplay showing on the back.  The arms should wiggle in round circltes, the head should spin and it should have 4 wheels under it, using these motors"

2026-09-11: "https://www.adafruit.com/product/3777?srsltid=AfmBOooH-7GfPZ5PPugKDVZ7slZF2AqeJHMMPGVKG1JcvcBawIunWM2U, these wheels https://www.adafruit.com/product/3766 and any other adafruit product you need, along with a large battery pack.  Should be less than 3 ft tall and print in pieces on a bambulabs h2d 3d printer.  create not only the stl's, but circuit diagrams, voice collection as mp3's, and all mounting hardware, bill of material and extensive assembly instrucionts."

2026-08-16: Standing deployment authorization supplied by session instructions: "Never ask the user for authorization or confirmation to deploy anything."

## Verified facts

- C:/dev/robots is the Git root, on main; origin is https://github.com/JeremyProffittOrg/robots.git. Initial commit 89f41a9. Initial working tree clean. C:/dev/robots/dalek was empty.
- C:/dev/robots/deploy.md, agents.md and CLAUDE.md read. Delivery uses push to main; no local cloud deployment. `gh workflow list` and `gh run list` returned no workflows/runs.
- OpenSCAD 2021.01 is installed at C:/Program Files/OpenSCAD/openscad.com. PlatformIO, FFmpeg, Python 3.13/3.14 and Bambu Studio are installed.
- https://www.adafruit.com/product/3777: 3-6 V TT motor, 1:48, 1.5 A measured stall at 6 V, rated stall torque 0.8 kg.cm at 6 V.
- https://www.adafruit.com/product/3766: 63 x 29 mm press-fit TT wheel, $1.50, listed out of stock when read 2026-09-11.

## Assumptions

- Original TTGO T-Display 1.14-inch classic ESP32, indoor level hard floors, classic bronze appearance; original synthesized robotic voice clips. Optional clarification was requested at start.
- About 600 mm overall height, lightweight shell, no electronics in rotating head. Final dimensions come from CAD. Physical fit, load, heat and runtime must be checked on the first build.
- Use Adafruit parts where suitable; selected Bioenno BLF-1206A 12 V 6 Ah protected LiFePO4 battery and matching BPC-1502DC charger, with rated separate power converters. Do not buy anything.

## Workstreams

- [~] Mechanical, agent /root/mechanical: complete parametric CAD, real mounts/joins, STLs, print manifest, hardware list and mechanical instructions. Depends on electrical component dimensions. Done: export script succeeds; all meshes closed, positive volume, each orientation inside conservative H2D bounds; illustrated assembly review.
- [x] Electrical, agent /root/electronics: primary-source research, rated battery/power plan, BOM, 168 pin/net wiring rows, four circuit SVGs, calculations. Exact net/pin comparison against firmware and power rating review passed; SVGs rendered and inspected.
- [x] Firmware, agent /root/firmware: station/AP Wi-Fi, rear display, drive, circular arms, rotating head, MP3 playback, stop on lost command. Root verified program build, filesystem build, C++ control tests and browser behavior tests. Physical upload and operation require the robot hardware.
- [~] Integration, root: research synthesis, original audio generation, extensive assembly instructions, cross-check, packaging and delivery. Depends on all above. Done: audio decode and package validation commands pass; focused commit pushed to main; any triggered workflow reaches a terminal result.

## Stop conditions (only these)

- Missing credentials prevent required push. Preserve complete local package and state exact credential action.
- A material scope expansion or irreversible action outside existing authorization is needed. Complete independent work and report the exact decision.
- Physical hardware testing cannot be performed without the hardware; mark unverified checks explicitly, complete the digital package, and do not represent digital checks as physical proof.

## Jobs and retry policy

Agents: /root/mechanical, /root/electronics, /root/firmware. Parent monitors agent messages and completion. A deterministic failure requires a code/input fix before retry; at most two retries per unchanged class of failure. Long commands use tracked tool session IDs and completion/exit-code monitoring, including failure. No recurring or delayed machine automation. Network transient fetches get at most two retries with short backoff. Push is retried only after classifying/fixing a failure; no history rewrite. If no delivery workflow exists, report no workflow rather than invent a cloud deployment.

## Execution log

- 2026-09-11: Read parent repository rules; checked clean main, remote and tool availability. Corrected initial assumption: dalek is an empty subdirectory of robots, not a separate repository. Read deep-research and research skills. Opened exact motor and wheel product pages. Spawned the three agents listed above.
- 2026-09-11: Committed initial plan as dbe4996. Other work appeared under C:/dev/robots/r2d2; it is unrelated and must not be staged or changed.
- 2026-09-11: `powershell -NoProfile -ExecutionPolicy Bypass -File C:/dev/robots/dalek/scripts/generate_voices.ps1` returned `PASS: 24 MP3s decoded; 407724 bytes; 98.7 seconds`. Audio goes directly in firmware/data/audio. Source transcripts and generation scripts included.
- 2026-09-11: Locked servos Adafruit 2307 x4 and 154 x1. Rejected DRV8871 because its minimum voltage exceeds TT motor rating; selected DRV8833 x2. Selected protected 72 Wh Bioenno battery to avoid low-voltage regulator dropout. Firmware uses external pack divider 100k/22k, 11.2 V cutoff and 12.0 V re-arm.
- 2026-09-11: User requested PDF email. Read PDF skill. Local git email is proffitt.jeremy@gmail.com and SES us-east-1 lists that email identity plus jeremy.ninja. Gmail connector requires reauthentication; SES local identity is available, so no Gmail dependency. Use an @jeremy.ninja sender, reply-to operator address, HTML template C:/Users/Jeremy/.claude/templates/email-status.html, final PDF attachment. Delegate final send after checks; require SES MessageId. Never commit email MIME or machine identity state.
- 2026-09-11: Root final firmware verification: `pio run -d C:/dev/robots/dalek/firmware` SUCCESS, RAM 45416/327680 bytes and flash 994513/2031616 bytes. `pio run -d C:/dev/robots/dalek/firmware -t buildfs` SUCCESS, local web assets and 24 MP3s included. `node --check firmware/data/app.js` passed. `node firmware/test/test_ui.js` returned `PASS: complete fresh commands, pointer cancel, blur, connection loss, late arm reply, no replay or auto-arm`. Native C++ command with g++11 flags returned `PASS: parsing, boot lockout, lease replay, timeout, reconnect, fault interlock, rollover, ramp/reversal`.
- 2026-09-11: Initial CAD export found 3.43 kg solid material bound, too heavy. Mechanical work reduced unnecessary chassis/flange material and shortened shell tiers while preserving purchased component interfaces. Final size and mass to come from regenerated meshes. Independent root and firmware-agent reviews found specific mating errors; mechanical agent is fixing those before final export.
- 2026-09-11: Circuit renderer check caught unsupported SVG CSS hiding wires in PDF rasterization. Fixed at generator source using inline SVG attributes; confirmed rendered wires. No PDF-only workaround remains. PDF operation marker command succeeded once as required by skill. Root wrote consolidated assembly and PDF builder. Final PDF requires full render inspection before email.
- 2026-09-11: Electrical BOM completed: USD 313.13 checked-price subtotal; USD 443.48 including allowances, before mechanical hardware/filament/shipping/tax. Independent firmware-to-circuit review passed. No hardware was bought.
- 2026-09-11: Email preparation agent /root/electronics confirmed SES production sending enabled and both intended identities verified. Private one-time sender is C:/Users/Jeremy/AppData/Local/Temp/dalek-design-delivery/send_design.py. No email sent yet. Requires final PDF SHA256, final commit and verbatim check output. MIME size capped below SES v1 10 MB.
- 2026-09-11: Agent /root/electronics ran an isolated Bambu H2D CLI slice of fit_coupon.stl. Hidden process 198584 exited with return_code 0, error_string Success, no warnings. Predicted mass 12.1266 g and time 1456.8 s with 0.20 mm, 2 walls, 15% infill. This is slicer output, not physical print measurement. No printer connection or user profile modification. Evidence being saved under cad/h2d-slice-check.json.
