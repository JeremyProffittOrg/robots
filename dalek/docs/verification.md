# Digital verification and physical limits

The software and fabrication files were checked on the design machine. These checks establish digital consistency, not operation of a completed robot. The first physical build must complete every gate in `assembly.md`.

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

The exporter checks closed surfaces, consistent mesh winding, positive volume, connected physical solids and the conservative 300 x 300 x 300 mm print envelope. Closed internal cavities are distinguished from loose external solids. The final report records the actual results and solid-material mass bound for every part. Original CAD and every final STL are included.

Final check result: `mesh_count: 35`, `all_pass: true`, `printed_piece_count: 151`, `solid_material_upper_bound_g: 1988.1`. The complete listed print set includes a fit coupon and spare standoffs. Overall CAD height is 541 mm. The base diameter is 360 mm. Each STL is exported in pieces that fit the stated printer envelope. No printed weight or assembled weight is claimed as measured.

An actual Bambu Studio H2D slice of `fit_coupon.stl` also passed. The isolated one-time command, full profile names, Bambu Studio version 02.08.02.61 and exact STL SHA-256 are in `cad/h2d-slice-check.json`. The slicer returned `return_code: 0`, `error_string: Success`, and no warnings. It generated G-code at 0.20 mm layers, two walls and 15% infill. Predicted material was 12.1266 g and predicted total time was 1456.8 seconds. This was a PLA preflight slice; the functional fit coupon must still be printed in the material used for its matching structural parts. No printer was connected, and no actual print was made. The remaining parts were checked as meshes; they have not all been sliced during this run.

Independent coordinate reviews checked the chassis hole pattern, wheel and motor-mount clearance, plunger connectivity, rear board retention, arm attachment faces, and head bearing/hub stack. Identified geometric errors were corrected before the final export. These checks cannot replace test printing: the exact gearbox moulding, servo horn pattern, screen fit, layer shrinkage, bearing press fit and fastener access require physical checks.

## What remains unverified

No physical robot was fabricated, wired, powered, flashed or driven during this run. Actual print duration, completed mass, fit, stability, motor current, servo current, noise, temperature, battery runtime, head friction, wireless range and stopping distance remain unverified. Availability of the specified wheels and head servo also requires procurement. The manual provides explicit staged checks for all of these items.

No cloud deployment was performed because the robot operates locally and this repository has no deployment workflow for the design package. Delivery consists of source and fabrication files committed and pushed to `main`, plus the reviewed design PDF sent by email.
