# Dalek fabrication package

## Outcome

Create a complete digital fabrication package in C:/dev/robots/dalek for a printed Dalek below 914.4 mm tall, with four Adafruit 3777 motors and 3766 wheels, rear TTGO T-Display ESP32 screen, Wi-Fi station/AP control, circular arm motion, continuous head rotation, original MP3 voices, wiring diagrams, mounting parts, bill of materials, and extensive assembly instructions.

## Non-goals

No purchase, physical fabrication, remote firmware flashing, cloud application, scheduled automation, television audio extraction, or claim of hardware validation. No unrelated repository changes.

## Files

C:/dev/robots/plan.md; C:/dev/robots/dalek/{README.md,docs,cad,stl,electronics,bom,firmware,audio,scripts}. Generated output is part of the requested deliverable. Use existing OpenSCAD, PlatformIO, FFmpeg and Python tools.

## Locked decisions (user-confirmed; do not revisit)

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
- Use Adafruit parts where suitable; a rated prebuilt battery and power converter can come from another vendor if Adafruit ratings do not meet motor/servo demand. Do not buy anything.

## Workstreams

- [~] Mechanical, agent /root/mechanical: complete parametric CAD, real mounts/joins, STLs, print manifest, hardware list and mechanical instructions. Depends on electrical component dimensions. Done: export script succeeds; all meshes closed, positive volume, each orientation inside conservative H2D bounds; illustrated assembly review.
- [~] Electrical, agent /root/electronics: primary-source research, rated battery/power plan, BOM, pin/net wiring, circuit SVGs, calculations. Depends on firmware pin contract and mechanical envelopes. Done: exact net/pin comparison against firmware and review of motor/servo power ratings pass.
- [~] Firmware, agent /root/firmware: station/AP Wi-Fi, rear display, drive, circular arms, rotating head, MP3 playback, stop on lost command. Depends on electrical pin contract and root audio files. Done: `pio run -d C:/dev/robots/dalek/firmware` and focused existing project tests pass.
- [~] Integration, root: research synthesis, original audio generation, extensive assembly instructions, cross-check, packaging and delivery. Depends on all above. Done: audio decode and package validation commands pass; focused commit pushed to main; any triggered workflow reaches a terminal result.

## Stop conditions (only these)

- Missing credentials prevent required push. Preserve complete local package and state exact credential action.
- A material scope expansion or irreversible action outside existing authorization is needed. Complete independent work and report the exact decision.
- Physical hardware testing cannot be performed without the hardware; mark unverified checks explicitly, complete the digital package, and do not represent digital checks as physical proof.

## Jobs and retry policy

Agents: /root/mechanical, /root/electronics, /root/firmware. Parent monitors agent messages and completion. A deterministic failure requires a code/input fix before retry; at most two retries per unchanged class of failure. Long commands use tracked tool session IDs and completion/exit-code monitoring, including failure. No recurring or delayed machine automation. Network transient fetches get at most two retries with short backoff. Push is retried only after classifying/fixing a failure; no history rewrite. If no delivery workflow exists, report no workflow rather than invent a cloud deployment.

## Execution log

- 2026-09-11: Read parent repository rules; checked clean main, remote and tool availability. Corrected initial assumption: dalek is an empty subdirectory of robots, not a separate repository. Read deep-research and research skills. Opened exact motor and wheel product pages. Spawned the three agents listed above.
