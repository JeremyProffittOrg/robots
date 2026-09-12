# Electronics components — verified facts

Fetch date for every price and stock figure: 2026-09-12.
Each number is marked `[read]` (quoted from the linked page or file on the fetch date) or `[est]` (estimated by the author; not on any page).
Prices are single-unit USD as shown on the page. Stock is the page's own wording.
Pages that could not be fetched are listed in the "Fetch failures" section; no figure in this file comes from a page that failed.

Column key for the table: `Dims` = key dimensions in mm; `Holes` = mounting holes; `Electrical` = voltage, current, interface.

## Primary parts table

| # | Part (role) | Product number | Supplier URL | Price | Stock (2026-09-12) | Dims (mm) | Holes | Electrical |
|---|---|---|---|---|---|---|---|---|
| E01 | Raspberry Pi 4 Model B 4 GB (main computer, Wi-Fi, displays, audio) | Adafruit 4296 | https://www.adafruit.com/product/4296 | $120.00 [read] (list price 4 GB $100 [read] product brief) | In stock [read] | Board 85 x 56, corner R 3.0 [read, mechanical drawing] | 4 holes, Ø2.7 [read, product brief]; pattern 58 x 49, hole centres 3.5 from each edge [read, mechanical drawing] | 5 V DC via USB-C, minimum 3 A [read]; 40-pin GPIO; 802.11ac 2.4/5 GHz, BT 5.0 [read] |
| E02 | Adafruit KB2040 (motor and NeoPixel controller) | Adafruit 5302 | https://www.adafruit.com/product/5302 | $8.95 [read] | In stock [read] | 35.0 x 17.8 x 4.9 [read] | None listed on page; Pro Micro footprint, 2 x 12 castellated pads [read] | RP2040, 20 GPIO (18 pads + 2 STEMMA QT), 16 PWM, 4 ADC, 2 I2C, 2 SPI, 2 UART, USB-C, 3.3 V 500 mA regulator, RAW 5 V jumper for 2 A [read] |
| E03 | DRV8833 dual H-bridge (x4 for 7 motors) | Adafruit 3297 | https://www.adafruit.com/product/3297 | $5.95 [read] | In stock [read] | 26 x 18 x 3 [read] | None listed on page [read] | 2.7-10.8 V motor, 1.2 A per channel (2 A peak), on-board sense resistors give 1 A per motor limit [read] |
| E04 | 12 V to 5 V regulator for Pi and 5 V loads | Pololu D36V50F5, item 4091 | https://www.pololu.com/product/4091 | $39.95 [read] | "Rationed (Active and Preferred)" [read] | 25.4 x 25.4 x 9.5 [read] | Three 0.086 in (2.2 mm) holes for #2 or M2 [read] | In 5.5-50 V, out 5 V 4 %, 5.5 A continuous typical; pins VIN, VRP, VOUT, GND, EN, PG [read] |
| E05 | 12 V to 6 V regulator for TT motors (x2, one per motor group) | Pololu D36V50F6, item 4092 | https://www.pololu.com/product/4092 | $39.95 [read] | "Rationed (Active and Preferred)" [read] | 25.4 x 25.4 x 9.5 [read] | Three 0.086 in holes for #2 or M2 [read] | In 6.5-50 V, out 6 V, 5.5 A continuous typical [read] |
| E06 | Slip ring, 12 wire (dome power and signals) | Adafruit 1195 (Prosper SRC012C-12) | https://www.adafruit.com/product/1195 | $24.95 [read] | In stock [read] | Body Ø12.4, L 19.5, rotor stub Ø4 x 2.8 [read, SRC012 datasheet]; Adafruit page says 12 mm dia, 20 mm long [read] | No flange on the C type [read, datasheet drawing]; clamp the body in a printed bore [est] | 12 wires, 2 A per wire, 240 V, 28 AWG leads, 6 in long, 300 RPM [read] |
| E07 | Front logic display, left and right (two windows about 42 x 20 mm) | Adafruit 872 Mini 0.8" 8x8 LED matrix + I2C backpack, yellow-green; 2 per window, 4 total | https://www.adafruit.com/product/872 | $9.95 each [read] | 19 in stock [read] | Backpack PCB 20 x 28 x 4; matrix 20 x 20 x 6 [read] | 12 x 22 hole pattern [read] | I2C HT16K33, address 0x70-0x77 by jumpers [read]; 5 V |
| E08 | Rear logic display (window about 90 x 20 mm) | Adafruit 870 Mini 8x8 LED matrix + I2C backpack, red; 4 in a row | https://www.adafruit.com/product/870 | $9.95 each [read] | 100 in stock [read] | Backpack PCB 20 x 28 x 4; matrix 20 x 20 [read] | 12 x 22 hole pattern [read] | I2C HT16K33, page states address 0x70-0x73 by jumpers [read] |
| E09 | I2C multiplexer for 8 matrix backpacks | Adafruit 5626 PCA9548 8-channel STEMMA QT | https://www.adafruit.com/product/5626 | $6.95 [read] | 68 in stock [read] | 40.6 x 20.2 x 4.8 [read] | Not listed on page | 8 channels, own address 0x70-0x77, 3.3 V 500 mA regulator, JST SH 1 mm ports [read] |
| E10 | PSI (front and rear), 2 pcs | Adafruit 2226 NeoPixel Jewel 7 x 5050 | https://www.adafruit.com/product/2226 | $5.95 [read] | In stock [read] | Ø23 x 2 [read] | None listed | 5 V, about 18 mA per LED channel, chainable [read] |
| E11 | Holoprojector LEDs, 3 pcs | Adafruit 1734 NeoPixel diffused 8 mm through-hole, 5 pack | https://www.adafruit.com/product/1734 | $4.95 per 5 [read] | Out of stock [read] | Ø8 at base, 11 high, pins 27 [read] | Through-hole, 4 legs | 5 V, RGB order, WS2812B or SK6812 [read] |
| E12 | Radar-eye LCD (behind 42.6 mm lens opening) | Adafruit 6178 1.28" 240x240 round TFT GC9A01A, EYESPI | https://www.adafruit.com/product/6178 | $17.50 [read] | 24 in stock [read] | PCB 42.4 x 36.2 x 5.4; page quotes "38.1mm x 35.6mm" for the display [read] | Two 2.5 mm holes 22.8 apart [read] | 4-wire SPI, 3.3 V or 5 V logic (level shifter), microSD, 18-pin EYESPI [read] |
| E13 | Audio amplifier (Pi 3.5 mm out to speaker) | Adafruit 2130 PAM8302 mono 2.5 W class D | https://www.adafruit.com/product/2130 | $3.95 [read] | In stock [read] | 15 x 24 x 2 [read] | Not listed on page | 2.0-5.5 V, 2.5 W at 4 ohm, fixed 24 dB gain, volume trim pot [read] |
| E14 | Speaker 3 inch | Adafruit 1314, 3" 4 ohm 3 W | https://www.adafruit.com/product/1314 | $1.95 [read] | Out of stock [read] | Ø77.8, depth 25.49 [read] | 4 tabs, 60 mm apart [read] | 4 ohm, 3 W [read] |
| E15 | Battery 12 V 7 Ah SLA, F2 terminals | Power-Sonic PS-1270 F2 | https://www.trcelectronics.com/products/powersonic-ps-1270-f2 ; datasheet https://www.power-sonic.com/wp-content/uploads/datasheets/ps-1270.pdf | $19.00 [read, TRC] | 1,970 available [read, TRC] | L 151.0, W 65.0, H 94.0, total height 100.0, tolerance +/- 2 [read, datasheet]; weight 1.97 kg (4.34 lb) [read, datasheet]; TRC lists 4.8 lb [read] | F2 = 0.250 in (6.35 mm) blade [read, TRC "F2 terminal"] | 12 V, 7.0 Ah at 20 h; cycle charge 14.1-14.7 V, float 13.5-13.8 V, initial current under C/5 (1.4 A) [read, datasheet] |
| E16 | SLA charger, 3-stage, barrel plug | PowerStream PST-P2012-A12B | https://www.powerstream.com/12V-car-charger.htm | $22 [read] | Page lists price; stock wording not shown | 84 x 45 x 36, 100 g [read] | n/a | Stage 1 constant current 1500 mA +/-100 mA; stage 2 14.75 V +/-0.25; stage 3 float 13.75 +/-0.20 V; 5.5 mm OD x 2.1 mm ID barrel, center positive; input 90-264 VAC [read] |
| E17 | Panel charge port, 5.5 x 2.1 mm | Switchcraft L722A (DigiKey SC1151-ND) | https://www.digikey.com/en/products/detail/switchcraft-inc/L722A/241928 | $6.65 [read] | 4,596 in stock [read] | 5.50 OD barrel; 5/16-32 threaded bushing with nut [read] | One round panel hole for a 5/16 in (7.9 mm) bushing [read thread size; hole size est] | 5 A, 48 V, solder eyelets, DigiKey lists 2.00 mm ID [read] |
| E18 | Main power switch | Carling V1D2S00B-GZCXX-1XX-XFWD1 rocker | https://www.digikey.com/en/products/detail/carling-technologies/V1D2S00B-GZCXX-1XX-XFWD1/11587384 | $8.63 [read] | 412 in stock [read] | Panel cutout 36.83 x 21.08 rectangular, snap-in [read] | Snap-in, no screws [read] | SPST on-off, 20 A DC, 12 V DC, 0.250 in quick-connect terminals [read] |
| E19 | ATO in-line fuse holder, 5 pcs | Littelfuse FHAC0001ZXJ (DigiKey F3209-ND) | https://www.digikey.com/en/products/detail/littelfuse-commercial-vehicle-products/FHAC0001ZXJ/2004062 | $7.37 [read] | 9,324 in stock [read] | Fits ATO/ATC 19.1 x 5.1 blade fuses [read] | Free-hanging in-line [read] | 20 A, 32 V [read]; 16 AWG leads 89.5 mm [read, Littelfuse listing via search result; product page returned 403] |
| E20 | Fuse, main 15 A | Littelfuse 0287015.PXCN (DigiKey F4200-ND) | https://www.digikey.com/en/products/detail/littelfuse-inc/0287015.PXCN/2519816 | $0.44 [read] | 53,568 in stock [read] | ATO blade | n/a | 15 A, 32 V DC, blue [read] |
| E21 | Fuse, charge port 3 A and Pi 5 V feed 3 A (2 pcs) | Littelfuse 0287003.PXCN | https://www.digikey.com/en/products/detail/littelfuse-inc/0287003-PXCN/3102553 | $0.44 [read] | 34,473 in stock [read] | ATO blade | n/a | 3 A, 32 V DC [read] |
| E22 | Fuse, motor regulators 5 A (2 pcs) | Littelfuse 0287005.PXCN | https://www.digikey.com/en/products/detail/littelfuse-inc/0287005-PXCN/2519811 | $0.44 [read] | 76,765 in stock [read] | ATO blade | n/a | 5 A, 32 V DC [read] |
| E23 | F2 spade terminals, 0.250 in female, crimp (battery, switch; 6 pcs) | TE 3-520408-2 | https://www.digikey.com/en/products/detail/te-connectivity-amp-connectors/3-520408-2/14800982 | $0.59 [read] | 1,259 in stock [read] | 0.250 in (6.35 mm) tab [read] | n/a | 14-16 AWG, fully insulated, brass tin [read] |
| E24 | 16 AWG silicone wire, red and black (battery, switch, fuses, regulators) | BNTECHGO 16 AWG kit 50 ft (25 ft each colour) | https://bntechgo.com/bntechgo-16-gauge-silicone-wire-kit-ultra-flexible-50-ft-black-and-red-each-color-25-ft-high-temp-200-c-600v-16-awg-silicone-wire-252-strands-of-tinned-copper-wire-stranded-wire-stranded-wire-for-model-battery/ | $19.68 [read] | In stock [read] | Outer diameter not on page | n/a | 16 AWG, 252 strands tinned copper, 200 C, 600 V [read] |
| E25 | 22 AWG silicone wire, 6 colours (motors, LEDs, signals) | BNTECHGO 22 AWG kit, 6 colours x 30 ft | https://bntechgo.com/bntechgo-22-gauge-silicone-wire-kit-ultra-flexible-6-colors-each-30-ft-high-temp-200-c-600v-22-awg-silicone-wire-60-strands-of-tinned-copper-wire-stranded-wire-for-model-battery/ | $19.68 [read] | In stock [read] | OD 1.7 +/-0.1 [read] | n/a | 22 AWG, 60 strands 0.08 mm, 200 C, 600 V [read] |
| E26 | Motor connectors, JST-XH 2-pin (7 motors) | Adafruit 4872 2.5 mm pitch 2-pin cable matching pair | https://www.adafruit.com/product/4872 | $0.95 per pair [read] | In stock [read] | 20 cm each cable [read] | n/a | 2.5 mm pitch, 26 AWG, "carry a couple amps" [read] |
| E27 | Battery lead connector | Anderson Powerpole 15 A: housing 1327-BK red, black housing 1327G6 (same series), contacts 1332-BK | https://www.digikey.com/en/products/detail/anderson-power-products-inc/1327-BK/10650475 ; https://www.digikey.com/en/products/detail/anderson-power-products-inc/1332-BK/10650021 | Housing $0.64, contact $0.43 [read] | Housing 51,714, contact 68,600 in stock [read] | Standard PP15/45 housing, stackable [read] | n/a | Housing rated 55 A 600 V [read]; contact 1332 for 16-20 AWG, silver crimp [read]; 15 A per pole [read, Anderson listing via search] |
| E28 | Pi to KB2040 link cable | Adafruit 4474 USB A to USB C, 1 m | https://www.adafruit.com/product/4474 | $4.95 [read] | In stock [read] | 1 m [read] | n/a | USB 2.0 data + 5 V power to KB2040 [read connector types] |
| E29 | TT motor (7 pcs, verified earlier in plan.md) | Adafruit 3777 | https://www.adafruit.com/product/3777 | $2.95 [read, plan.md 2026-09-12] | In stock [read, plan.md] | 70 x 22 x 18; two Ø3.0 holes 17.6 apart; rear tab Ø3.0 [read, plan.md drawing] | as stated | 3-6 V, 1:48, 200 RPM at 6 V, stall 1.5 A at 6 V [read, plan.md] |
| E30 | Wheel (14 pcs, verified earlier in plan.md) | Adafruit 3766 | https://www.adafruit.com/product/3766 | $1.50 [read, plan.md] | Out of stock [read, plan.md] | Ø63 x 29, 38 g [read, plan.md] | Press fit on TT D-shaft | n/a |

## Alternates table (one per primary)

| Primary | Alternate | Product number | Supplier URL | Price | Stock (2026-09-12) | Dims (mm) | Holes | Electrical | Why it is second choice |
|---|---|---|---|---|---|---|---|---|---|
| E01 | Raspberry Pi 4 Model B 2 GB | Adafruit 4292 | https://www.adafruit.com/product/4292 | $63.25 [read] | Out of stock [read] | Same board as E01 | Same | Same | Less RAM; out of stock |
| E02 | Adafruit Feather RP2040 | Adafruit 4884 | https://www.adafruit.com/product/4884 | $11.95 [read] | In stock [read] | 51.0 x 23.0 x 7.5 [read] | Feather 4 holes (not on fetched text) | 21 GPIO, 16 PWM, STEMMA QT, USB-C [read] | Bigger; operator asked for 5302 |
| E03 | Adafruit TB6612 1.2 A dual H-bridge | Adafruit 2448 | https://www.adafruit.com/product/2448 | $6.95 [read] | In stock [read] | 27 x 19 x 3 [read] | Not listed | 4.5-13.5 V motor, 1.2 A per channel, 2.7-5 V logic [read] | Needs 3 pins per motor; no current limit |
| E04 | Pololu D24V50F5 | Pololu 2851 | https://www.pololu.com/product/2851 | $32.95 [read] | "Rationed (Active)" [read] | 17.8 x 20.3 x 8.8 [read] | Two 0.086 in holes [read] | In 6-38 V, out 5 V, 5 A [read] | Lower current margin |
| E05 (both) | Pololu D24V150F6, one unit feeds all seven motors | Pololu 2882 | https://www.pololu.com/product/2882 | $79.95 [read] | "Rationed (Active)" [read] | 43.2 x 31.8 x 11 [read] | Four 0.086 in holes [read] | In 4.5-40 V, out 6 V, 15 A [read] | Single point of failure; same cost as two 4092 |
| E06 | Slip ring with flange, 6 wire | Adafruit 736 | https://www.adafruit.com/product/736 | $14.95 [read] | In stock [read] | Ø22 body, Ø44 flange with holes [read] | Flange holes (count not on page) | 6 wires, 2 A each, 26 AWG, 300 RPM [read] | Six wires only carry 5 V, GND and one data link; see slip-ring note |
| E07/E08 | Adafruit 0.8" 8x16 LED Matrix FeatherWing, white (2 per rear window, 1 per front window) | Adafruit 3149 (white); 3152 red | https://www.adafruit.com/product/3149 ; https://www.adafruit.com/product/3152 | $19.95 (3149), $11.95 (3152) [read] | 3149: 2 in stock; 3152: out of stock; 3150/3151/3154: "No longer stocked"; 3153: out of stock [read] | PCB 51 x 23 x 5; LED area 40 x 20 (two 20 x 20 matrices) [read] | FeatherWing holes (not on fetched text) | I2C HT16K33, 0x70-0x77 [read] | Fits the 42 x 20 window exactly but stock is nearly gone |
| E09 | Adafruit 16x8 HT16K33 driver backpack (bare driver, wire your own matrices) | Adafruit 1427 | https://www.adafruit.com/product/1427 | $7.95 [read] | In stock [read] | 35.77 x 20.37 x 4.03 [read] | Not listed | 8 selectable addresses, drives 16x8 [read] | More wiring |
| E10 | NeoPixel Ring 12 | Adafruit 1643 | https://www.adafruit.com/product/1643 | $8.95 [read] | In stock [read] | OD 36.8, ID 23.3, 6.7 thick [read] | None | 5 V, 12 LEDs, 18 mA per LED [read] | Bigger than the PSI lens; hollow centre |
| E11 | NeoPixel 5050 with driver, 10 pack (breakout style, solder to a 3-pad carrier) | Adafruit 1655 | https://www.adafruit.com/product/1655 | $4.50 per 10 [read] | In stock [read] | 5 x 5 [read] | None | 5 V, 18 mA per channel [read] | Needs a carrier PCB or careful hand soldering; 5 mm through-hole 1938 is also out of stock [read] |
| E12 | Adafruit 1.3" 240x240 square TFT ST7789 (rectangular alternate) | Adafruit 4313 | https://www.adafruit.com/product/4313 | $16.95 [read] | In stock [read] | PCB 35.8 x 35.8 x 5.3; screen 26 x 26 [read] | Four 0.1 in holes, 33 x 30 pattern [read] | 4-wire SPI, EYESPI, 3.3/5 V [read] | Square image behind a round lens |
| E13 | Adafruit MAX98357A I2S 3 W amp (digital audio; skips the Pi analog jack) | Adafruit 3006 | https://www.adafruit.com/product/3006 | $5.95 [read] | In stock [read] | 19.4 x 17.8 x 3.0 [read] | Not listed | 2.7-5.5 V, 3.2 W at 4 ohm, I2S DIN/BCLK/LRC [read] | Needs I2S overlay on the Pi |
| E14 | Speaker 3" 8 ohm 1 W | Adafruit 1313 | https://www.adafruit.com/product/1313 | $1.95 [read] | In stock [read] | 77.8 x 77.8 x 25.49 [read] | 4 tabs, 60 mm apart [read] | 8 ohm, 1 W [read] | Lower power; same footprint |
| E15 | Mighty Max ML7-12F2 | ML7-12F2 | https://www.mightymaxbattery.com/shop/12v-sla-batteries/12-volt-7-2-ah-f2-terminal-sla-battery/ | $19.99 [read] | Sold in 1-10 packs [read] | 5.88 x 2.50 x 3.88 in (page converts to about 149.4 x 63.5 x 98.6) [read]; 4.50 lb (about 2.04 kg) [read] | F2 [read] | 12 V, 7.2 Ah [read] | Total height with terminals not stated |
| E16 | Power-Sonic PSC-121000ACX (alligator clips) | PSC-121000ACX | https://www.power-sonic.com/product/psc-121000a-c/ | Not shown [read] | Not shown | 80 x 57 x 50 [read] | n/a | 12 V, 1.0 A, peak 14.7 V, float 13.3 V, dual-rate [read] | Alligator clips need a barrel adapter lead |
| E17 | Adafruit panel-mount 2.1 mm DC jack | Adafruit 610 | https://www.adafruit.com/product/610 | $2.95 [read] | Out of stock [read] | Panel up to 8 mm thick [read] | One round hole (size on datasheet, not on page) | Current rating not on page | Out of stock; rating unknown |
| E18 | SparkFun toggle switch SPST 20 A 12 V, illuminated | SparkFun COM-11310 (DigiKey 1568-11310-ND) | https://www.digikey.com/en/products/detail/sparkfun-electronics/11310/17828278 | $5.85 [read] | Not in stock at DigiKey, 12-week lead [read] | 12.00 mm round panel hole [read] | Round hole | SPST, 20 A DC, 12 V DC, quick connect [read] | Not in stock |
| E26 | JST-XH 560-piece kit (crimp your own) | Adafruit 4423 | https://www.adafruit.com/product/4423 | $24.95 [read] | 19 in stock [read] | 2.5 mm pitch | n/a | Wire gauge not on page | More work, more parts |
| E27 | XT30 pairs (5 pairs) | ServoCity 3803-0102-0505 | https://www.servocity.com/male-xt30-female-xt30-connectors-5-pair/ | $4.99 per 5 pairs [read] | InStock [read] | About 13.7 x 10.2 x 5.2 [read, Out of Darts page] | n/a | 30 A, wire up to 18 AWG [read, Out of Darts page] | 16 AWG lead is above the 18 AWG cup size |

## Notes

### Raspberry Pi 4 Model B mechanical
Source: mechanical drawing https://pip.raspberrypi.com/documents/RP-008343-DS-raspberry-pi-4-mechanical-drawing.pdf (redirect target of https://datasheets.raspberrypi.com/rpi4/raspberry-pi-4-mechanical-drawing.pdf), read as an image. Product brief https://datasheets.raspberrypi.com/rpi4/raspberry-pi-4-product-brief.pdf (April 2026 edition), text extracted.
- Board 85 x 56 mm, "CORNER RADIUS = 3.0mm" [read].
- Mounting holes: 4, centres 3.5 mm from the left edge and 3.5 mm from the top and bottom edges; pattern 58 mm (x) by 49 mm (y) [read]. Hole diameter "Ø2.7" [read, product brief drawing]. Use M2.5 screws [est].
- Component heights above the board, from the drawing's Z labels [read]: GPIO header Z=8.5; SoC Z=2.4; Ethernet jack Z=13.5; two USB stacks Z=16.0; USB-C power Z=3.2; micro HDMI x2 Z=3.0; audio jack Z=6.0; camera and display FPC connectors Z=5.5.
- Connector layout: Ethernet and the two USB stacks are on the 56 mm edge opposite the SD slot; USB-C, two micro HDMI and audio are on one 85 mm edge. The drawing's bottom-edge chain reads "7.7, 14.8, 13.5, 7.5, 11.5, 6, 2.7" [read]. The USB and Ethernet housings are drawn past the board edge; the overhang is not dimensioned. Allow 3 mm past the 85 mm board length and 2 mm past the 56 mm width in the tray cutouts [est].
- Power: "5V DC via USB-C connector (minimum 3A)" [read]. Product brief adds that a 2.5 A supply works if USB peripherals draw under 500 mA [read].
- Wi-Fi: "2.4 GHz and 5.0 GHz IEEE 802.11b/g/n/ac wireless LAN, Bluetooth 5.0, BLE" [read, product brief]. No USB Wi-Fi dongle is needed.
- List prices in the product brief: 1 GB $35, 2 GB $55, 4 GB $100, 8 GB $165 [read]. Adafruit's 4 GB price is $120 [read].

### KB2040 pinout and pin budget
Source: https://learn.adafruit.com/adafruit-kb2040/pinouts and https://www.adafruit.com/product/5302.
- Pads: D0/TX GPIO0, D1/RX GPIO1, D2 GPIO2, D3 GPIO3, D4 GPIO4, D5 GPIO5, D6 GPIO6, D7 GPIO7, D8 GPIO8, D9 GPIO9, D10 GPIO10, A0 GPIO26, A1 GPIO27, A2 GPIO28, A3 GPIO29, plus SCK, MISO, MOSI [read pin names]. The fetch summary gave conflicting GPIO numbers for SCK/MISO/MOSI (it listed them as GPIO10-12, which collide with D10 and the STEMMA QT pins); treat the SCK/MISO/MOSI GPIO numbers as unverified in this document and read them from the silkscreen or `board` module before wiring.
- STEMMA QT: SDA = GPIO12, SCL = GPIO13 (I2C0) [read]. These are the only two GPIO not on pads.
- Power: RAW is 5 V from USB through a 500 mA fuse; a solder jumper on the back bypasses it for 2 A [read]. 3.3 V out 500 mA [read].
- Every RP2040 GPIO can drive PWM, but the chip has 8 slices x 2 channels = 16 outputs, and GPIO n and GPIO n+16 share one channel (same duty) [est, from the RP2040 architecture; not on the fetched page].
- Pin budget for this robot:
  - 14 motor PWM inputs (7 motors x 2 DRV8833 inputs): GPIO0-GPIO9 (PWM 0A-4B), GPIO10 (5A), GPIO27 (5B), GPIO28 (6A), GPIO29 (6B). These are 14 distinct PWM channels [est, mapping from the RP2040 rule above].
  - 1 NeoPixel data pin: MOSI pad (any spare pad works; NeoPixel timing is PIO-driven) [est].
  - STEMMA QT I2C0 on GPIO12/13 for optional body-side I2C sensors [read pins].
  - Spares: GPIO26/A0 (ADC0, reserved for battery voltage sense through a divider), SCK, MISO pads, and the DRV8833 SLP lines if tied to 3.3 V instead of a GPIO [est].
- The 3777 stall current is 1.5 A at 6 V [read, plan.md]; the DRV8833 limits each motor to 1 A by its sense resistors [read], so a stalled motor is chopped, not burned, and the two-motor foot never exceeds 2 A [est].

### KB2040 to Pi link
- Cable: Adafruit 4474 USB A to USB C, 1 m [read]. The Pi's USB 2.0 port powers the KB2040 and carries a CDC serial link; CircuitPython exposes it as a second serial port (`usb_cdc.data`) and the Pi sees `/dev/ttyACM0` [est, standard CircuitPython behaviour; not on a fetched page].
- Protocol proposed: one text line per command, `M<index> <speed -1000..1000>` and `N<index> <rrggbb>`, 115200 baud [est, design choice].
- NeoPixel 5 V power comes from E04, not from the KB2040 RAW pin (500 mA fuse) [read RAW limit].

### DRV8833 pin functions
Source: https://learn.adafruit.com/adafruit-drv8833-dc-stepper-motor-driver-breakout-board/pinouts.
- VMOTOR 2.7-10.8 V; GND shared [read]. Feed VMOTOR from the 6 V regulator, not 12 V.
- AIN1/AIN2 and BIN1/BIN2: one PWM per direction; "PWM the normally-high pin" for slow decay [read].
- SLP: pulled low by 500 k, chip off until SLP is high [read]. Tie to 3.3 V through the KB2040 or a GPIO for an emergency stop.
- FLT: open-drain, low on fault; needs pull-up [read].
- Current limit: two 0.2 ohm resistors give 1 A per motor; `LimitCurrent = 0.2 V / RSENSE` [read].
- Mounting: no holes are stated on the product page. Mount the four boards on a printed carrier with header pins into a small perfboard, or clip them by their edges [est].

### 12 V power tree and fusing
- Battery 12 V (E15) -> Powerpole lead (E27) -> main fuse 15 A (E19+E20) -> main switch (E18) -> bus.
- Charge port (E17) -> 3 A fuse (E21) -> battery side of the main switch, so the charger reaches the battery with the switch off. PowerStream charger E16 output 1.5 A max fits a 3 A fuse [read current].
- Bus -> 3 A fuse -> D36V50F5 (E04) -> Pi USB-C 5 V, displays, NeoPixels, amp.
- Bus -> 5 A fuse -> D36V50F6 #1 -> DRV8833 pair for left leg (2 motors) and centre leg (2 motors).
- Bus -> 5 A fuse -> D36V50F6 #2 -> DRV8833 pair for right leg (2 motors) and head drive (1 motor).
- Regulator continuous rating 5.5 A each [read] versus a worst case of 4 motors x 1 A (limited) = 4 A [est].
- Note: Pololu shows all three regulators as "Rationed" stock [read]; order early.

### Slip ring wire budget (12 wires, 2 A each)
- Dome loads: two Jewels (14 LEDs), three 8 mm NeoPixels, eight 8x8 matrices, one TFT. NeoPixel worst case 17 x 60 mA = 1.0 A [est, 60 mA per full-white LED is the usual figure; page gives 18 mA per channel]. Matrices about 0.5 A total [est].
- Assignment: 2 x 5 V, 2 x GND (paralleled), NeoPixel data, I2C SDA, I2C SCL, SPI SCK, SPI MOSI, TFT CS, TFT DC, TFT RST = 12 [est]. TFT backlight is tied to 5 V through the board's own regulator [est].
- The 6-wire alternate (E06 alternate) only works if the dome gets its own small controller (for example a second KB2040) and the ring carries 5 V, GND and a UART pair [est].
- Prosper datasheet for the C type: body Ø12.4, L 19.5 for the 12-ring unit, rotor stub Ø4 x 2.8 [read, SRC012 datasheet page 2]. There is no flange; the body is a plain cylinder and must be clamped in a printed bore with a set screw [est].

### Logic display fit
- Front logic windows are about 42 x 20 mm [plan.md]. Two Mini 8x8 backpacks (E07) side by side give a 40 x 20 mm LED area on 20 mm wide PCBs, so the matrices abut with no gap [read PCB width 20 mm]. PCB depth 28 mm sits behind the dome wall [read].
- Rear logic window is about 90 x 20 mm [plan.md]. Four Mini 8x8 backpacks in a row give 80 x 20 mm of LEDs [read]. The window can be reduced to 82 x 22 mm in CAD, or the two end 5 mm strips left dark [est].
- Eight backpacks need eight I2C addresses. Page 872 states 0x70-0x77 [read]; page 870 states 0x70-0x73 [read]. Use the PCA9548 multiplexer (E09) so each backpack sits on its own channel and address collisions do not matter [read channel count].
- The FeatherWing 8x16 alternate fits the front windows in one board (40 x 20 LED area) but stock is 2 white units and every other colour is out or discontinued [read].

### Radar eye LCD fit
- Lens opening 42.6 mm [plan.md]. The 6178 PCB is 42.4 mm wide [read], so the board passes the opening on one axis only; mount it from behind on the two 2.5 mm holes 22.8 mm apart [read] with the round glass centred in the lens.
- Driven from the Pi's SPI0 over the slip ring; the board accepts 3.3 V logic and 5 V power [read].

### Audio
- Pi 4 has a 4-pole 3.5 mm stereo audio jack [read, product brief]. Sum L+R through two 10 k resistors into the PAM8302 A+ input, A- to ground [est].
- PAM8302 runs from the 5 V rail; 2.5 W at 4 ohm at 5.5 V [read]. Speaker E14 is 4 ohm 3 W [read] but out of stock; E14 alternate 1313 (8 ohm 1 W) is in stock [read].

### PSI and holoprojectors
- NeoPixel Jewel 2226 is Ø23 mm [read]; the PSI lens bore in CAD should be 24 mm [est].
- 8 mm NeoPixels (1734) and 5 mm NeoPixels (1938) are both out of stock [read]. The 5050 10-pack (1655) is in stock [read] and can be soldered to a 3-wire pigtail for each holoprojector.

### Battery and charger
- Power-Sonic datasheet: 151.0 x 65.0 x 94.0 mm, total height 100.0 mm, +/- 2 mm; approximate weight 1.97 kg [read]. plan.md carries 2.26 kg; TRC lists 4.8 lb (2.18 kg) [read]. Keep 2.26 kg in the load calculations as a conservative upper bound [est].
- Charging per datasheet: cyclic 14.1-14.7 V, float 13.5-13.8 V, initial current under C/5 [read]. PowerStream PST-P2012-A12B: 1.5 A bulk, 14.75 V absorb, 13.75 V float [read]; 1.5 A is below C/5 = 1.4 A only slightly above; acceptable for a 7 Ah SLA [est].
- Charge port L722A is rated 5 A [read]. DigiKey lists its inner diameter as 2.00 mm [read]; Switchcraft markets the L7xx series for 2.1 mm plugs, and the PowerStream plug is 2.1 mm ID [read]. Confirm the fit with the physical parts before gluing the port [est].

### Wire, connectors, terminals
- 16 AWG silicone for battery, switch, fuse and regulator input runs [read gauge]; 22 AWG silicone for motor leads, NeoPixel and display signals [read gauge].
- Adafruit sells silicone wire only in 26 and 30 AWG single strands (search of adafruit.com on 2026-09-12); BNTECHGO is the verified source for 16 and 22 AWG.
- F2 battery blades are 0.250 in; the TE 3-520408-2 receptacle is 14-16 AWG fully insulated [read]. Use 6: two battery, two switch, two spare.
- Powerpole 15 A contacts take 16-20 AWG [read]; this matches the 16 AWG battery lead. XT30 cups take up to 18 AWG [read], so XT30 is the alternate, not the primary.
- JST-XH 2-pin pairs (4872) are 26 AWG [read]; the TT motor running current is well under 1 A per motor [est], and the pair is rated "a couple amps" [read].

### Optional items
- USB game controller: optional; any Linux HID gamepad works with the Pi's `evdev` interface [est]. No product chosen.

## Fetch failures (2026-09-12)
- https://www.power-sonic.com/product/ps-1270/ returned the PS-12700 page, and https://www.power-sonic.com/wp-content/uploads/2018/12/PS-1270%20technical%20specifications.pdf redirected to the home page. The datasheet at https://www.power-sonic.com/wp-content/uploads/datasheets/ps-1270.pdf (version 1.2, updated 8/18/2026) was fetched and used.
- https://www.mouser.com/ProductDetail/Power-Sonic/PSC-121000A-C timed out; https://www.power-sonic.com/product/psc-121000a-c/ was used instead.
- https://www.littelfuse.com/... FHAC0001ZXJ product page and datasheet returned 403 / HTML; DigiKey page used for price and rating; lead gauge quoted from the Littelfuse listing text in the search result.
- https://us.rs-online.com/product/power-sonic/ps-1270-f2/70115580/ returned 403; TRC Electronics used.
- https://www.waveshare.com/1.28inch-lcd-module.htm and its wiki returned 403; no Waveshare round LCD is listed.
- https://powerwerx.com/... returned 403; DigiKey pages used for Powerpole parts.
- Adafruit product images (cdn-shop.adafruit.com) returned 9-byte bodies to curl; no product photo was inspected.
- The Adafruit KB2040 pinout fetch produced conflicting GPIO numbers for the SCK/MISO/MOSI pads; those three numbers are marked unverified above.
