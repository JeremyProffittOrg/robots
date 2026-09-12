# Firmware and Wi-Fi controller

This firmware targets the original 1.14-inch LilyGO TTGO T-Display with a classic ESP32, 135 × 240 ST7789 display and 4 MB flash. It does not target the T-Display S3 or the AMOLED version. The display faces outward through the robot's rear window. Landscape rotation is 1; use rotation 3 in `src/main.cpp` if the finished mount is reversed.

The software builds for the specified hardware. Its physical operation must be commissioned on the assembled robot. A successful compiler check does not establish stopping distance, servo centre, current draw, Wi-Fi range, speaker level or battery measurement accuracy.

## Build and load

1. Install PlatformIO Core or the PlatformIO extension for Visual Studio Code. The pinned packages in `firmware/platformio.ini` install on the first build. Internet access is required for that build only.
2. Turn the physical actuator stop switch OFF. Disconnect the battery before connecting USB. Do not connect two 5 V sources to the board together unless the circuit diagram's power isolation is in place.
3. Use a data-capable USB cable. From the project directory run:

   ```powershell
   Set-Location C:\dev\robots\dalek\firmware
   pio run
   pio run -t buildfs
   pio device list
   ```

4. Read the ESP32 serial port from the last command. Replace `COM7` below with that port:

   ```powershell
   pio run -t upload --upload-port COM7
   pio run -t uploadfs --upload-port COM7
   ```

5. Reset the board. The display must show DISARMED. If automatic flashing does not start, hold the board's BOOT button, start upload and release BOOT after the connection begins. The other button, GPIO35, is the stop/setup button.
6. Disconnect USB before restoring the normal battery supply. Keep the wheels off the floor until all commissioning checks below pass.

There is one factory application partition, 0x10000–0x1fffff (2,031,616 bytes). LittleFS occupies 0x200000–0x3fffff (2,097,152 bytes). Uploading LittleFS replaces the web assets and MP3 files in that partition. Network credentials are in a separate NVS partition. There is no wireless firmware update, cloud service, internet dependency or scheduled background job.

Pinned dependencies: Espressif32 PlatformIO platform 6.5.0, Arduino-ESP32 2.0.14, TFT_eSPI 2.5.43, Adafruit PWM Servo Driver Library 3.0.2, Adafruit BusIO 1.16.1 and ESP8266Audio 1.9.7. The audio dependency is GPL-3.0; retain its notices and supply corresponding source with redistributed firmware binaries. Later ESP8266Audio releases use different ESP32 I2S APIs, so update the platform and audio library together only after testing.

## First connection

The board makes a WPA2 access point named `DALEK-xxxx`. It generates a device-specific 12-character key on first boot and saves it locally. The rear display shows the key. Firmware does not print keys or station passwords to the serial terminal. Join this access point using the displayed key, then open `http://192.168.4.1`. Enter the same key in the control page.

To join a router, open Wi-Fi network settings on the page. Enter the exact network name and its 8–63-byte WPA2 password. This classic ESP32 uses 2.4 GHz Wi-Fi. The password is sent in an authenticated POST request and saved in local NVS. Read the LAN address on the rear display and browse to that address from the same local network. No credentials are present in the repository.

The setup AP remains available while the robot connects to a router. This also provides fallback if the router is missing or its credentials change. Moving between AP and router connections, or losing either connection, disarms motion. Reconnecting never arms the robot. The AP supports two clients, but only one control lease can be active. Keep one control browser open.

Press the rear GPIO35 button to disarm. Hold it for five seconds to erase only the saved router credentials and return to AP operation. The device access key stays the same. The rear key also authorizes robot control for users on the router network. Do not share it widely or expose port 80 to the internet. The local interface uses HTTP; Wi-Fi encryption protects the wireless link, but this is not an end-to-end encrypted service.

## Controls

Press Arm controls, then hold a movement button. Forward uses PWM 110/255, reverse 90/255 and turns use 50/255 on the inside wheel pair and 120/255 on the outside pair. Release disarms. Arm again for the next movement. Tight pivots are omitted from the supplied interface because four rubber wheels can scrub heavily against the floor. The requested TT motors have limited torque. Use a smooth, level indoor floor and gentle arcs.

The arm checkbox enables two-axis circles. Radius is 0–8 degrees and frequency is 0.10–0.80 Hz. The default is 8 degrees at 0.40 Hz. Eight degrees is the concealed gimbal's clearance limit; the browser and API reject a larger radius. One side runs half a cycle behind the other. The head slider commands the TT friction motor's drive level and direction; zero removes PWM. Displayed 100% maps to the conservative 100/255 PWM ceiling. It is not a measured speed. Hold Arms / head only to animate without ground-wheel movement. These settings also apply while a drive button is held. Sliders alone do not cause movement.

Speak plays a selected MP3 locally. Silence stops the decoder. Audio operates while the robot is disarmed. All audio stays in the fixed body, so the head can turn indefinitely without twisting an electrical cable. There is no head position sensor or automatic front-facing home position.

The browser must stay visible and focused. Releasing a pointer, losing pointer capture, cancelling a touch, changing tabs, locking the screen, closing the page or pressing Escape requests a stop. Loss of a command response also disarms the interface. Browsers can delay or discard stop packets; the board's independent timeout covers that case.

## Electrical contract

Read [electronics-research.md](electronics-research.md) and [the power circuit](../electronics/01-power.svg), [controller, drive and audio wiring](../electronics/02-controller-drive-audio.svg), [servo wiring](../electronics/03-servos.svg) and [circuit details](../electronics/04-circuit-details.svg) before wiring. All ESP32 signal pins are 3.3 V. Servo signals pass through the specified 74AHCT125 buffers to reach 5 V logic. Never feed 5 V into an ESP32 input.

| Function | ESP32 GPIO | Connection |
| --- | --- | --- |
| I2C data / clock | 21 / 22 | PCA9685 SDA / SCL, logic VCC 3.3 V |
| Servo disable | 27 | PCA9685 OE and U8 arm-buffer active-low output enables; U9 uses PCA4/5 |
| Left forward / reverse | 25 / 26 | Left DRV8833 AIN1+BIN1 / AIN2+BIN2 |
| Right forward / reverse | 32 / 33 | Right DRV8833 AIN1+BIN1 / AIN2+BIN2 |
| Motor enable | 12 | All three DRV8833 SLP pins; 10 kΩ pull-down |
| Head PWM | 2 | 20 kHz to U9 inputs2/5;10 kΩ pull-down |
| Audio bit clock / word clock / data | 17 / 13 / 15 | MAX98357A BCLK / LRC / DIN |
| Actuator power sense | 36 | 5 V actuator rail through 10 kΩ top / 15 kΩ bottom divider |
| Battery voltage sense | 39 | Battery through 100 kΩ top / 22 kΩ bottom divider, 100 nF from ADC to ground |
| Stop / forget router | 35 | Existing rear board button |

PCA9685 address is0x40. Servo channels0–3 are left yaw, left pitch, right yaw and right pitch. Channels4/5 are static active-low head gate enables, not servo connectors. U8 buffers the four servo signals from5V_SERVO. U9, powered from5V_MOTOR, routes GPIO2 PWM to the selected U11 bridge input. PCA4/5 HIGH disables the corresponding U9 gate; LOW enables it. Each gate has a10k pull-up to3V3. U9 outputs reach U11 AIN1/AIN2 through220ohm resistors, with10k pull-downs at the driver. See circuit sheet03 for physical DIP pins. The PCA stays at50Hz; the motor receives20kHz hardware PWM from the ESP32.

U5/U6 each run two ground motors, with input pairs joined. U11 bridgeA runs the head; tie BIN1/BIN2 low and leave BOUT1/BOUT2 open. Every used bridge retains its stock1A current limit. Never parallel bridge outputs.

Startup writes and verifies PCA MODE2=0x06: OUTDRV=1 and OUTNE=10. Global OE HIGH then makes PCA outputs high-impedance. R7/R8 pull both head-gate enables HIGH. The default OUTNE=00 would instead enable both active-low gates. A failed write or readback prevents arming. Keep this setting when changing PCA libraries.

GPIO27 needs a10k pull-up to3.3V. Remove the PCA breakout's onboard OE pull-down as specified in the electronics guide. GPIO12 and GPIO2 each need10k pull-downs because they are boot strap pins and must default to disabled motion. GPIO15 connects only to the amplifier DIN input without external bias. GPIO36/39 are input-only and use the specified dividers.

The firmware reserves GPIO5/16/18/19/23/4 for the integrated display. GPIO0 is the existing BOOT button. GPIO34/14 remain reserved for the board's original battery measurement circuitry. The robot's external 12 V pack does not connect to the board's single-cell battery socket.

## Stop behavior and limits

The motion task runs independently of the HTTP server and MP3 decoder, with a nominal 10 ms period. It is watched by the ESP32 two-second task watchdog. External enable resistors keep the actuator signals disabled during reset. This is a hobby control system, not a certified safety controller. The physical stop switch cuts actuator power without relying on Wi-Fi or software.

A command lease is granted only after explicit arming. The robot requires a complete valid command at least every 500 ms. The supplied browser sends a fresh command snapshot every 100 ms and aborts a command request after 300 ms. Each arm uses a new random lease; every command needs a strictly increasing sequence number. Old leases and duplicate commands do not refresh the timeout. An expired lease is checked before accepting another command, so a late request cannot revive movement. Invalid control parameters disarm immediately. Software drive values are limited to ±150/255.

Ordinary wheel speed changes ramp by at most five PWM counts per nominal 10 ms. A requested reversal first ramps to zero, waits 100 ms, then ramps the other way. A stop, fault or disarm immediately drives SLP low and both inputs low; it does not wait for the ramp. This lets the wheels coast. It does not provide a mechanical brake, and stopping distance must be measured with the final mass.

The head motor uses the same five-count ramp step with a100/255 ceiling. Direction reversal ramps to zero, coasts for100ms, then ramps up. A brief zero command or quick disarm/re-arm cannot bypass that interval. A zero head command immediately removes head PWM. Before changing the selected U9 gate, firmware sets GPIO2 PWM to zero, disables both gates using checked I2C writes, enables one gate and then restores bounded PWM. The shared SLP line is held steady during operation; PWM never drives SLP.

The PCA receives four checked servo writes every20ms and checked static-gate writes when head direction changes. Any failed write latches an I2C fault, sets head PWM zero, sets all driver SLP pins low and disables servo OE. Missing PCA at boot prevents arming. No automatic motion recovery follows power, I2C, Wi-Fi or battery faults. Head PWM stops immediately on software disarm; the old head-servo neutral pulse is removed. All motors coast after electrical disable. Physical stopping distance and head coast angle still need measurement.

The specified battery is the Bioenno BLF-1206A 12 V nominal 6 Ah LiFePO4 pack. The software multiplies the ADC voltage by (100 + 22) / 22 = 5.54545 to recover pack voltage. It smooths readings at 10 Hz. Below 11.2 V for one second, it disarms; voltage must recover to at least 12.0 V before re-arming is allowed. A disconnected ADC or an implausible voltage also prevents arming. These thresholds are conservative operating limits, not a battery state-of-charge meter, a charger or a replacement for the pack's protection circuit. Calibrate the ADC against a multimeter before use.

## Servo and sensor calibration

All calibration values are in `firmware/include/config.h`. Keep the wheels lifted and the servo horns removed for initial checks.

1. Check5V rails with actuator power disabled. During ESP32 reset verify all three SLP pins and GPIO2 are low, and PCA OE is high.
2. Measure battery voltage with a multimeter. Read the displayed voltage. Set `PACK_ADC_CORRECTION` to measured voltage divided by displayed voltage, rebuild, and recheck at two battery voltages. Do not lower a cutoff to hide a wiring error.
3. Leave arm and head commands at zero. Enable actuator power, arm, and hold Arms / head only. The four positional servos must settle near their centres. Fit each horn with its joint centred and no mechanical load, then stop before fitting links. The initial centres are 1500 μs; change `ARM_CENTER_US` in small steps only if needed.
4. Keep the head tyre clear of its track and command zero. GPIO2 and both U11 bridge inputs must remain low. Before attaching the motor, scope AIN1/AIN2 at a low head setting: only one input may carry20kHz PWM. Check both directions and a reversal interval of at least100ms with no PWM. There is no neutral pulse or neutral trimmer.
5. Start arm circles at radius 2 degrees and 0.10 Hz. Confirm that yaw and pitch are both active. Confirm that neither joint touches a stop. Increase to 8 degrees and 0.40 Hz. The pulse envelope stays within 1200–1800 μs, but mechanical clearance is the limiting factor. Reduce the maximum radius if the actual links require it.
6. Turn power off. Set the head mount to light tyre contact, then test in each direction. Increase pressure only enough to turn the freely rotating head. Preserve slip if obstructed. `HEAD_DIRECTION` reverses the sign and `dalek::HEAD_LIMIT` is100/255. Do not raise this ceiling to overcome a jam. The slider is a drive-level command, not an angle or measured speed.
7. Lift all wheels. A forward command must rotate all four wheels toward forward travel. If one motor is reversed, swap only that motor's two output wires. `LEFT_DIRECTION` and `RIGHT_DIRECTION` reverse an entire side if necessary. Stop and remove actuator power before rewiring.
8. Play a phrase. The fixed digital gain is 0.28, below the design ceiling of 0.35. MAX98357A hardware gain must be 3 dB as specified in the circuit guide. Do not raise gain above 0.35 with the 8 Ω 1 W speaker and specified logic supply. Digital gain is not a calibrated wattmeter; verify clean sound, supply stability and acceptable speaker temperature.

## Acceptance checks on the completed robot

Perform these with a helper at the physical stop switch, first with wheels lifted, then at low speed on a clear floor. Record the results in the assembly commissioning sheet.

- Power up, reset and reconnect USB: no wheel or servo motion before an explicit arm command.
- AP mode: router absent, page and every local voice phrase work through 192.168.4.1.
- Station mode: join the private router, read the rear LAN IP, load the page and drive through that address.
- Release the movement button: wheel outputs disable and the page becomes disarmed. Measure actual coasting distance with the final shell and battery fitted.
- While moving, disable the phone's Wi-Fi: commanded drive must cease within the 500 ms lease timeout plus control-task scheduling delay. The robot must remain disarmed after reconnection.
- While moving, lock the phone or change tabs: motion stops. Unlocking does not resume the prior command.
- Press physical stop: motor and servo supply must lose power even if the ESP32 keeps running. Releasing the switch does not restart movement.
- Press the rear GPIO35 button while holding a browser control: motion stops and does not restart without a new arm.
- With actuator power off, disconnect the PCA9685, then boot: I2C fault appears and Arm is refused. Reconnect only with power removed.
- Use an adjustable current-limited bench supply in place of the pack for the voltage check. At 11.0 V for more than one second the software must disarm. At 11.5 V it must refuse a new arm. Above 12.0 V it may accept a new explicit arm.
- Run arm circles and head motion while playing all phrases; no reset, supply sag, decoder stall or joint contact is acceptable.
- Complete gentle forward arcs on the intended floor. Measure individual motor current, case temperature and stopping distance. Do not accept a stalled inside wheel or prolonged current-limit operation.

## Automated checks

From `firmware/`:

```powershell
pio run
pio run -t buildfs
node --check data/app.js
node test/test_ui.js
$env:PATH = 'C:\msys64\mingw64\bin;' + $env:PATH
g++ -std=c++11 -Wall -Wextra -Werror -I include test/test_control.cpp -o $env:TEMP\dalek-control-test.exe
& $env:TEMP\dalek-control-test.exe
```

The host C++ test runs the same control-state code used by the ESP32. It covers strict parsing, boot lockout, expired/replayed leases, reconnects, unhealthy-input disarm and millisecond rollover. It accepts an 8-degree arm radius and rejects 9 degrees. Head regressions check the PWM ceiling, immediate zero/fault stop, and reversal delay through zero, re-arm and clock rollover. The Node test exercises the actual browser script with a simulated DOM and transport. Hardware routing, timing and stopping still need physical commissioning.

## Sources

- [LilyGO original T-Display board, schematic links and pin allocation](https://github.com/Xinyuan-LilyGO/TTGO-T-Display).
- [PlatformIO LilyGo T-Display board definition](https://docs.platformio.org/en/latest/boards/espressif32/lilygo-t-display.html).
- [TFT_eSPI original T-Display setup](https://github.com/Bodmer/TFT_eSPI/blob/master/User_Setups/Setup25_TTGO_T_Display.h).
- [Adafruit PCA9685 driver source and checked setPWM result](https://github.com/adafruit/Adafruit-PWM-Servo-Driver-Library/blob/3.0.2/Adafruit_PWMServoDriver.cpp).
- [ESP8266Audio version 1.9.7 source and license](https://github.com/earlephilhower/ESP8266Audio/tree/1.9.7).
- [ESP8266Audio current API compatibility notes](https://github.com/earlephilhower/ESP8266Audio#esp32-and-platformio).
