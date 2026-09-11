# Digital verification and physical limits

The STACK-10 mechanical revision was checked on the design machine. These checks establish digital consistency, not operation of a completed robot. The first physical build must complete every gate in `assembly.md`. Firmware, circuits and MP3 files are unchanged; their successful earlier build and behavior checks are retained below. The mesh and full-package H2D checks are new for this revision.

## Firmware and controls

Command:

```powershell
pio run -d C:/dev/robots/dalek/firmware
```

Result: SUCCESS. RAM 45,416 / 327,680 bytes. Application flash 994,513 / 2,031,616 bytes. The build uses the original LilyGo T-Display board definition and Arduino-ESP32 2.0.14.

Command:

```powershell
pio run -d C:/dev/robots/dalek/firmware -t buildfs
```

Result: SUCCESS. The filesystem image contains the local HTML/JavaScript interface and all 24 MP3s. It fits the 2,097,152-byte LittleFS partition. It has not been uploaded to a physical board during this run.

Commands:

```powershell
node --check firmware/data/app.js
node firmware/test/test_ui.js
```

Results: JavaScript syntax passed. Browser test returned:

```text
PASS: complete fresh commands, pointer cancel, blur, connection loss, late arm reply, no replay or auto-arm
```

Native test commands:

```powershell
$env:PATH = 'C:/msys64/mingw64/bin;' + $env:PATH
g++ -std=c++11 -Wall -Wextra -Werror -I firmware/include firmware/test/test_control.cpp -o "$env:TEMP/dalek-control-test.exe"
& "$env:TEMP/dalek-control-test.exe"
```

Result:

```text
PASS: parsing, boot lockout, lease replay, timeout, reconnect, fault interlock, rollover, ramp/reversal
```

The C++ test uses the same command-state and ramp code as the ESP32 firmware. The Node test executes the browser JavaScript with a simulated page and network. These tests do not measure Wi-Fi range, real browser timing on a phone, physical stopping distance, or servo response to loss of pulses.

## Audio

Command:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File C:/dev/robots/dalek/scripts/generate_voices.ps1
```

Result:

```text
PASS: 24 MP3s decoded; 407724 bytes; 98.7 seconds
```

Every file was encoded and decoded by FFmpeg. FFprobe checked MP3, mono and 22,050 Hz. Exact durations, file sizes and SHA-256 values are in `audio/catalog.json`. Speaker playback on the actual ESP32 remains a physical commissioning check.

## Electrical consistency

Command:

```powershell
python electronics/generate.py
```

Result: 168 point-to-point wiring rows, four parseable SVG circuit sheets, and calculated power/ADC values. Root and an independent firmware reviewer checked the actual circuit net names against firmware GPIOs, enable polarities, PCA9685 channel order, AHCT buffer pins, ADC ratio and thresholds, and audio wiring. The reviewed values agree.

The circuit sheets were rendered and visually inspected. An initial SVG rendering fault that hid CSS-styled wires was corrected in the generator using explicit SVG presentation attributes. The final diagrams contain visible connections. Electrical behavior, noise, supply sag, and actual servo current are still unmeasured.

## CAD and printing

Use the final machine-readable report at `cad/validation.json` and print list at `bom/printed-parts.csv`. The exact check command is:

```powershell
python scripts/export_cad.py --check-only
```

The exporter checks the exact ten-file inventory, closed surfaces, consistent mesh winding, positive volume, one connected physical solid per STL and the 325 x 320 x 325 mm H2D single-nozzle envelope with brim allowance. Closed internal cavities are distinguished from loose external solids. Original CAD and all ten final STLs are included. The retired split-panel STL files were removed.

Final mesh result: `mesh_count: 10`, `maximum_stl_files: 10`, `all_pass: true`, `printed_piece_count: 11`, `solid_material_upper_bound_g: 2876.1`. The carrier is printed twice. Overall CAD height is 543.8 mm. The base is 300 x 280 mm and is one continuous print with a 6 mm floor and integral motor pockets. Each complete body section prints upright and stacks onto the next. No physical print weight or strength rating is claimed as measured.

All ten final designs also passed actual Bambu Studio H2D slicing. `cad/h2d-slice-check.json` contains the exact STL hashes, Bambu Studio version 02.08.02.61, per-part process overrides, full CLI argument lists, result codes, loaded mesh dimensions, full printed heights, and actual model/support/brim extrusion bounds. Each final result has code 0 and an empty plate warning field. All material and process settings were checked in the generated G-code. No printer was connected or commanded to print.

The base uses PETG, six walls, six top and bottom layers, 40% gyroid infill, normal automatic supports and an 8 mm brim. The base and lower ring are rotated 90 degrees about Z, kept at Z0 with `--ensure-on-bed`, and centred at X175,Y160. This aligns the 300 mm side along printer Y. The base's entire extruded model, support and brim lie at X27.507-322.493 and Y2.507-317.493 mm, within both single-nozzle areas. Its full 57 mm height was preserved. Its predicted installed model mass is 916.956 g; total material including removable supports is 1059.186 g.

For all eleven printed pieces, slicer predictions are 2188.64 g of installed model, 836.50 g of removable support, and 5.67 g of brim. Total filament is 3031.14 g, with approximately 100 hours 30 minutes of sequential printing under the recorded profiles. These are software predictions. Removing support does not remove model mass. Purchased parts are additional.

The installed model estimate plus about 1144.88 g of named catalogue components gives a 3333.52 g subtotal before remaining electronics, bearings, metal clamps, fasteners, wiring and finish. The earlier 3 kg planning target is not met. It was not a manufacturer-rated motor payload. Loaded motion remains unverified and must pass the actual programmed forward, reverse and arc tests with current, temperature and stop measurements. No current limit, voltage limit or stop test was weakened to claim success.

Some failed setup trials were rejected before recording the final successful slices, including a clipped brim and an incorrect below-bed placement. The final checks include complete mesh heights and extrusion bounds. The JSON also records Bambu's parser diagnostics for manufacturer-specific T commands in its stock start/end G-code; these occurred with successful final slice codes and no plate warnings. G-code was not executed on a printer.

Independent checks in `docs/revision-review.md` used the exact delivered mesh hashes. They found zero sampled interference for 72,000 wheel points over three seating positions, 48,000 motor-envelope points, 12,000 PCB/servo points, and all sixteen stack-bolt driver paths. Required ball-end and short L-key tools are specified in the hardware list. These checks do not measure actual tyre deformation, hub engagement, print shrinkage, fastener torque, or strength.

## What remains unverified

No physical robot was fabricated, wired, powered, flashed or driven during this run. Actual print duration, completed mass, fit, stability, motor current, servo current, noise, temperature, battery runtime, head friction, wireless range and stopping distance remain unverified. Availability of the specified wheels and head servo also requires procurement. The manual provides explicit staged checks for all of these items.

No cloud deployment was performed because the robot operates locally and this repository has no deployment workflow for the design package. Delivery consists of source and fabrication files committed and pushed to `main`, plus the reviewed design PDF sent by email.
