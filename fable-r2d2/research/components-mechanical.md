# Mechanical components and materials — verified facts

Date of fetch: 2026-09-12. All prices are USD unless marked. Every figure in the tables
was read from the page at the URL in the same row on that date, unless the row says
"estimated". Prices on Amazon change often; treat them as the price on the fetch date.

How each row was verified: the page was downloaded with `curl` (browser user-agent) or
fetched with WebFetch, and the quoted text was extracted from the page HTML. Where a
page could not be fetched, the row says so and a different source is used.

Design context from `plan.md` (not re-verified here): body diameter 317.0 mm, body
wall 4 mm, dome inside diameter about 309 mm, battery 151 x 65 x 94 mm / 2.26 kg,
seven Adafruit 3777 TT motors, thirteen Adafruit 3766 wheels.

## Summary table — primary choices

| Part | Supplier | URL | Price (read) | Key dims (read) | Rating (read) |
|---|---|---|---|---|---|
| Dome ring bearing: Triangle Mfg 9C steel round lazy susan, 9 in | Triangle Manufacturing (maker page) / WW Hardware (price) | https://www.triangleoshkosh.com/lazy-susan-turntable-bearing-9c and https://www.wwhardware.com/triangle-flat-lazy-susan-bearing-9-round-tr09c | $6.79 each (WW Hardware, SKU TR09C; 25+ $6.24) | "Overall Length: 9"" (228.6 mm OD), "Center Hole Diameter: 4.5"" (114.3 mm), "Mount Hole Center to Center: 6.176"" (156.9 mm), "22 Gauge" steel, "5/16" thick" (7.9 mm, from the Amazon 9CW listing title) | "Load Capacity: 750 lbs" (340 kg) |
| Pivot ball bearings 6001-2RS, 12 x 28 x 8 mm, 10 pack | PGN Bearings via Amazon | https://www.amazon.com/dp/B07GVQ8G23 | $11.45 per 10 ($1.15 each) | "12x28x8mm", "Chrome Steel Sealed" | Rating from VXB single-bearing page: "Dynamic load rating: 5,100 N", "Static load rating: 2,390 N", "18,000 RPM" (https://vxb.com/products/6001-2rs-sealed-bearing-12x28x8) |
| Small bearings 608-2RS, 8 x 22 x 7 mm, 10 pack | PGN Bearings via Amazon | https://www.amazon.com/dp/B07XVPGMXQ | $9.95 per 10 ($1.00 each) | "8x22x7mm", chrome steel, double rubber seal | Rating from VXB 608-2RS Amazon listing: "Static load rating of 141 kgf and dynamic load rating of 336 kgf" (https://www.amazon.com/dp/B002BBCX0Q) |
| Shoulder pivot bolt: M12-1.75 x 100 mm hex bolt, zinc plated class 8.8 | Bolt Depot | https://www.boltdepot.com/Metric_hex_bolts_Zinc_plated_class_8.8_steel_12mm_x_1.75mm.aspx | Prod. # 6269, 100 mm: "$1.89 / ea", "$31.58 / 25"; 110 mm # 6270 $2.26; 120 mm # 6271 $2.44; 130 mm # 6272 $2.83; 150 mm # 6274 $3.53 | M12 x 1.75, "Wrench size 19mm" | Class 8.8 (page title) |
| M12 nylon-insert lock nuts, 20 pack | BNUOK via Amazon | https://www.amazon.com/dp/B0F8GZP628 | $8.99 per 20 | "M12-1.75", "DIN 985", 304 stainless A2-70 | not stated |
| M12 hex nuts, zinc class 8.8 | Bolt Depot | https://boltdepot.com/Product-List?Units=Metric&Category=Nuts&Subcategory=Hex_nuts&F_Diameter=12mm&F_Thread_pitch=1.75mm&Material=Steel&Plating=Zinc&Grade=Class_8.8 | Prod. # 4790: "$0.24 / ea", "$9.13 / 50" | 12 mm x 1.75 mm | class 8.8 |
| M12 flat washers, zinc | Bolt Depot | https://boltdepot.com/Product-List?Units=Metric&Category=Washers&Subcategory=Flat_washers&F_Size=12mm&Material=Steel&Plating=Zinc | Prod. # 4531: "$0.08 / ea", "$5.15 / 100" | 12 mm | n/a |
| M12 fender (large) washers, zinc | Bolt Depot | https://boltdepot.com/Product-List?Units=Metric&Category=Washers&Subcategory=Fender_washers&F_Size=12mm&Material=Steel&Plating=Zinc | Prod. # 17834: "12mm x 37mm", "$0.56 / ea", "$37.83 / 100" | 12 mm ID x 37 mm OD | n/a |
| Flanged bronze bushings for 12 mm pivot, 2 pack | HARFINGTON via Amazon | https://www.amazon.com/dp/B0CGDV5C3F | $12.99 per 2 | "Bore Diameter: 12mm, Outer Diameter: 16mm, Total Length: 20mm, Flange Diameter: 20mm, Flange Thickness: 2mm" | "Coefficient of Friction: 0.12-0.18"; load not stated |
| Index dowel pins 6 x 30 mm steel, 50 pack | Fabory via Amazon | https://www.amazon.com/dp/B076GVC92R | $34.90 per 50 | "6x30mm", "Material steel" | hardness not stated (see notes) |
| Threaded rod M8 x 1.25 x 1 m, zinc steel | Bolt Depot | https://boltdepot.com/Threaded_rod_Zinc_plated_steel_8mm_x_1.25mm | Prod. # 23774: "$11.25 / ea", "$308.50 / 35" | 1 m length, 8 mm x 1.25 mm | low carbon zinc plated steel |
| M8 coupling nuts, zinc class 6 | Bolt Depot (same rod page) | https://boltdepot.com/Threaded_rod_Zinc_plated_steel_8mm_x_1.25mm | Prod. # 15801: "$0.62 / ea", "$37.29 / 100" | "8mm x 1.25mm x 24mm" | class 6 |
| M8 hex nuts, zinc class 8.8 | Bolt Depot | https://boltdepot.com/Product-List?Units=Metric&Category=Nuts&Subcategory=Hex_nuts&F_Diameter=8mm&F_Thread_pitch=1.25mm&Material=Steel&Plating=Zinc&Grade=Class_8.8 | Prod. # 4788: "$0.06 / ea", "$4.84 / 100" | 8 mm x 1.25 mm, "Wrench size 13mm" | class 8.8 |
| M8 nylon-insert lock nuts, 50 pack | Yinpecly via Amazon | https://www.amazon.com/dp/B0F1YGKBSL | $6.99 per 50 | "M8x1.25mm", "Hex Width: 12.8mm", "Nut thickness: 7.64mm", carbon steel zinc plated | not stated |
| M8 flat washers, zinc | Bolt Depot | https://boltdepot.com/Product-List?Units=Metric&Category=Washers&Subcategory=Flat_washers&F_Size=8mm&Material=Steel&Plating=Zinc | Prod. # 4529: "$0.05 / ea", "$2.33 / 100" | 8 mm | n/a |
| M8 fender washers, zinc | Bolt Depot | https://boltdepot.com/Product-List?Units=Metric&Category=Washers&Subcategory=Fender_washers&F_Size=8mm&Material=Steel&Plating=Zinc | Prod. # 17832: "8mm x 24mm", "$0.28 / ea", "$14.45 / 100" | 8 mm ID x 24 mm OD | n/a |
| M2/M3/M4 socket-head screw, nut and washer kit, 1080 pcs | Amazon (brand not named in title) | https://www.amazon.com/dp/B0CHMKL1DF | $12.99 per kit | "M2 M3 M4 Hex Button Socket Head Cap Screws Bolts Nuts Flat Washers", alloy steel, black | grade not stated |
| M4 socket head cap screws, 12.9 alloy, 50 pack (example length 12 mm; 4-50 mm offered) | Amazon | https://www.amazon.com/dp/B074TFLBFQ | $7.29 per 50 | "Thread Dia. 4mm, Thread Pitch: 0.7mm", "Head Diameter: 7mm, Head Height: 4mm" | "12.9 Grade Alloy Steel" |
| M4 hex nuts, zinc class 8.8 | Bolt Depot | https://boltdepot.com/Product-List?Units=Metric&Category=Nuts&Subcategory=Hex_nuts&F_Diameter=4mm&F_Thread_pitch=0.7mm&Material=Steel&Plating=Zinc&Grade=Class_8.8 | Prod. # 4784: "$0.05 / ea", "$2.54 / 100" | 4 mm x 0.7 mm | class 8.8 |
| M3 hex nuts, zinc class 8.8 | Bolt Depot | https://boltdepot.com/Product-List?Units=Metric&Category=Nuts&Subcategory=Hex_nuts&F_Diameter=3mm&F_Thread_pitch=0.5mm&Material=Steel&Plating=Zinc&Grade=Class_8.8 | Prod. # 4783: "$0.05 / ea", "$2.30 / 100" | 3 mm x 0.5 mm | class 8.8 |
| M4 flat washers, zinc | Bolt Depot | https://boltdepot.com/Product-List?Units=Metric&Category=Washers&Subcategory=Flat_washers&F_Size=4mm&Material=Steel&Plating=Zinc | Prod. # 4525: "$0.05 / ea", "$1.28 / 100" | 4 mm | n/a |
| Heat-set inserts M3 x 4 mm, 50 pack | Adafruit 4255 | https://www.adafruit.com/product/4255 | $5.95 per 50 (10-99: $5.36) | "M3 x 4mm", outer diameter 4.2 mm (read from page) | brass |
| Heat-set inserts M3 x 3 mm, 50 pack | Adafruit 4256 | https://www.adafruit.com/product/4256 | $5.95 per 50 | "M3 x 3mm" | brass |
| Heat-set inserts M4 x 8.1 mm, 50 pack (ruthex RX-M4x8.1) | ruthex via Amazon | https://www.amazon.com/dp/B07YSV66Y5 | $9.99 per 50 | "Height (mm) 8,1", "Insert hole (mm) 5,6" (comparison table on the page) | brass, lead free |
| Heat-set inserts M5 x 9.5 mm, 50 pack (ruthex RX-M5x9.5) | ruthex via Amazon | https://www.amazon.com/dp/B07YSVXWS8 | $9.99 per 50 | "Height (mm) 9,5", "Insert hole (mm) 6,4" (comparison table on the page) | brass, lead free |
| Head-drive tensioner spring: compression spring 10 mm OD x 25 mm free length, 0.6 mm wire, 304 stainless, 5 pack | Amazon (Haul listing) | https://us.amazon.com/Compression-Spring-Stainless-Length-Silver/dp/B0DK9C5YT5 | $2.24 per 5 | "10mm OD, 0.6mm Wire Size, 25mm Free Length" | spring rate not stated (see notes) |
| Tensioner adjuster: M5 knurled thumb nuts, 304 stainless, 10 pack | uxcell via Amazon | https://www.amazon.com/dp/B0D7PWCDWK | $9.39 per 10 | "Thread Size: M5-0.8; Head Dia: 16mm", "Height: 4mm" | 304 stainless |
| Battery tie-down: 25 mm hook-and-loop cinch straps, 6 pack | MECCANIXITY via Amazon | https://www.amazon.com/dp/B0F43TNSM2 | $7.59 per 6 | "Length: 400mm/16 inch; Width: 25mm/1 inch", nylon | not stated |
| Filament: Bambu PETG HF 1 kg | Bambu Lab US store | https://us.store.bambulab.com/products/petg-hf | "$19.99" per spool at MSRP ("$12.99 USD /roll (Lowest price for 10+ rolls)"); page says "PETG HF is discontinued and will not be restocked once sold out" | 1.75 mm, 1 kg net (TDS) | TDS: tensile X-Y 34 ± 4 MPa, Z 23 ± 4 MPa; bending X-Y 64 ± 3 MPa (https://store.bblcdn.com/ce12d65176a94f1086e6aefa238e62e2.pdf) |
| Filament: Bambu PETG Basic 1 kg (the replacement Bambu links from the PETG HF page) | Bambu Lab US store | https://us.store.bambulab.com/products/petg-basic | "$17.99" per spool at MSRP ("$11.69 USD /roll (Lowest price for 10+ rolls)") | 1.75 mm, 1 kg | TDS: tensile X-Y 51 ± 1 MPa, Z 35 ± 6 MPa; bending X-Y 75 ± 3 MPa, Z 56 ± 4 MPa; impact X-Y 34.2 ± 4.1 kJ/m2 (https://store.bblcdn.com/s1/default/cb94589bf7994fdcbfa833badefae9cd/Bambu_PETG_Basic_Technical_Data_Sheet.pdf) |
| Filament: Bambu PETG-CF 1 kg | Bambu Lab US store | https://us.store.bambulab.com/products/petg-cf | "From $31.99 USD" | 1.75 mm, 1 kg | TDS V2.0: tensile X-Y 59 ± 4 MPa, Z 38 ± 3 MPa; bending X-Y 83 ± 4 MPa, Z 62 ± 3 MPa; impact X-Y 41.2 ± 2.6 kJ/m2 (https://sourcegraphics.com/wp-content/uploads/2023/08/Bambu_PETG-CF-Technical_Data_Sheet.pdf) |
| Filament: Bambu PLA Basic 1 kg (dome option) | Bambu Lab US store | https://us.store.bambulab.com/products/pla-basic-filament | "$19.99" per spool at MSRP ("$12.99 USD /roll (Lowest price for 10+ rolls)") | 1.75 mm, 1 kg | not read |
| Cable ties 8 in, 100 pack | Skalon via Amazon | https://www.amazon.com/dp/B09PJ8L58G | $3.99 per 100 | "Length: 8" \| Width : 0.14" \| Max Dia: 2"" | "Tensile Strength: 40lbs" |
| Adhesive zip-tie mounts 3/4 in, 100 pack | GTSE via Amazon | https://www.amazon.com/dp/B0877BD2SH | $14.99 per 100 | "3/4" x 3/4"", nylon 6/6, adhesive plus screw hole | "working temperature -40°F to +185°F" |
| M3 nylon standoff kit, 260 pcs | HVAZI via Amazon | https://www.amazon.com/dp/B01HDR72Q2 | $9.99 per kit | "hex size:5.5mm", "Male length:6mm; Female lengths:6mm to 20mm", M3 x 0.5 | nylon |
| Closed-cell foam tape, 3/4 in x 3/8 in x 17 ft | Simply Conserve (AM Conservation) via Amazon | https://www.amazon.com/dp/B00TRUC19C | price not confirmed (page loaded, buy-box price not extractable; first listed price $4.99) | "Dimensions: 0.75" x 0.375" x 17'", PVC sponge foam, acrylic adhesive | n/a |

## Alternates — one per part

| Part | Alternate | URL | Price (read) | Key dims / rating (read) |
|---|---|---|---|---|
| Dome ring bearing | VXB 9 inch lazy susan bearing, white zinc plated steel | https://vxb.com/products/9-inch-lazy-susan-bearing-176lb-capacity | page shows "$35.99" and "you save $21.00" (sale mark-up text; regular price shown as $14.99 by WebFetch) | "Dia. 9 inches, Height: 9mm", "23/64" Thick", "176 lbs. max". Bolt pattern not given on the page. Second alternate with a price on Amazon: Triangle 9CW, https://www.amazon.com/dp/B01N48S7JE, $33.99, "center hole diameter: 4.595", nominal balanced load capacity: 750 lbs." |
| 6001-2RS bearings | VXB 10-pack premium 6001-2RS | https://vxb.com/products/6001-2rs-12x28x8-sealed-bearing-pack-of-10 | "Regular $29.99 / Sale $48.00" as displayed (VXB shows odd sale text) | "12mm x 28mm x 8mm", chrome steel, 18,000 RPM. Cheaper 2-pack: uxcell 6001-2RS, https://www.amazon.com/dp/B07FF14FQH, $5.99 per 2 |
| 608-2RS bearings | VXB 10-pack skateboard 608-2RS | https://vxb.com/products/10-pack-skateboard-bearing-608-2rs-sealed-8x22x7mm-miniature | "Regular price $14.99; Sale price $19.99" as displayed | "8mm x 22mm x 7mm", double rubber sealed |
| M12 x 100 bolt | Everbilt M12-1.75 x 100 mm class 8.8 zinc, 2-pack (Home Depot) | https://www.homedepot.com/p/Everbilt-M12-1-75-x-100-mm-Class-8-8-Zinc-Plated-Hex-Bolt-2-Pack-801988/204281899 | $4.75 per 2-pack (from search snippet; product page returned HTTP 403 to the fetch, so the price is not confirmed) | M12-1.75 x 100 mm class 8.8 |
| 12 mm pivot shaft instead of a bolt | 12 mm x 100 mm case-hardened chrome linear rod, 2 pack | https://www.amazon.com/dp/B0CW9JGWGG | $8.99 per 2 | "Diameter:12MM. length:100MM. tolerance ± 0.5", "C45 carbon steel（surface chromium plating）". Circlips: 12 mm external DIN 471, 30 pcs, https://www.amazon.com/dp/B0DQH1YYRD, $8.68 |
| Flanged bushings | uxcell wrapped oilless sleeve bushing 12 x 16 x 20 mm (no flange) | https://www.amazon.com/dp/B07SKVFW88 | $6.49 | "Bore: 12mm, Outside Diameter: 16mm, Length: 20mm", "Carbon steel base with Bronze Sintered and composite coating" |
| 6 mm dowel pins | M6 x 30 mm dowel pins, 10 pack (InStock Fasteners) | https://www.amazon.com/dp/B009TE3LYU | price not confirmed (buy-box not extractable; listed prices $12.49 / $9.49 / $9.29 on the page) | "Material - STEEL", "M6 X 30MM" |
| Threaded rod M8 | none verified other than Bolt Depot (Home Depot and Fasteners Direct pages returned 403/404) | — | — | — |
| M8 nyloc | Bolt Depot metric nylon insert lock nuts (category exists; the product list page returned an index instead of prices) | https://boltdepot.com/Browse?Units=Metric&Category=Nuts&Subcategory=Nylon_insert_lock_nuts&F_Diameter=8mm&F_Thread_pitch=1.25mm | not read | — |
| Small screws | uxcell M4 x 40 mm 12.9 alloy socket cap, 20 pcs | https://www.amazon.com/Alloy-Steel-Socket-Screws-Black/dp/B015A36ICK | not read (search result only) | M4 x 40 mm, 22 mm thread |
| Heat-set inserts | CNC Kitchen US store: M3 x 3 (short) 100 pcs $10.90, https://cnckitchenus.store/products/heat-set-insert-m3-x-3-short-version-100-pieces ; M4 x 4 (short) 50 pcs $10.90, https://cnckitchenus.store/products/heat-set-insert-m4-x-4-short-version-100-pieces | as listed | as listed | brass, lead and cadmium free. Hole sizes for these are not on the store pages. |
| Tensioner spring | Use an M5 adjuster screw and a Bolt Depot M5 wing nut instead of a spring: Bolt Depot metric wing nuts, zinc, Prod. # 29212 | https://boltdepot.com/Product-List?Units=Metric&Category=Nuts&Subcategory=Wing_nuts&F_Diameter=5mm&F_Thread_pitch=0.8mm&Material=Steel&Plating=Zinc | "$0.16 / ea", "$12.19 / 100" | 5 mm x 0.8 mm |
| Battery tie-down | Voltage VT-100 aluminium battery tray with hook-and-loop strap (fits "12V 7-9 ah ... sideways") | https://www.amazon.com/dp/B09L2WFQVZ | $17.99 | "Marine Grade Aluminum 5052", "5.94 x 4.94 x 1.06 inches", "3.8 ounces", includes "Hook and Loop Nylon battery hold down strap" |
| Hook-and-loop stock | VELCRO Brand ONE-WRAP roll 12 ft x 3/4 in | https://www.amazon.com/dp/B000078CUB | $7.34 | "12ft x 3/4in" |
| Structural filament | Bambu PETG Basic (listed above) is the drop-in if PETG HF sells out | — | — | — |
| Cable ties | Commercial Electric 8 in, 100 pack (Home Depot) | https://www.homedepot.com/p/Commercial-Electric-8in-Standard-50lb-Tensile-Strength-UL-21S-Rated-Cable-Zip-Ties-100-Pack-UV-Black-GT-200STCB/203531910 | $12.46 (search snippet, not fetched) | 50 lb tensile (title) |

## Notes and verbatim quotes

### Dome ring bearing

- Triangle 9C page (maker): "Overall Length: 9"", "Center Hole Diameter: 4.5"",
  "Mount Hole Center to Center: 6.176"", "Gauge: 22 Gauge", "Load Capacity: 750 lbs",
  "Finish: Pre-Plated Electrogalvanized", "Lubrication: Ungreased", "Suggested Turntable
  Diameter: 17" - 35"", "IN STOCK. READY TO SHIP." The maker page shows no price.
- Triangle 9-inch family page lists 9C, 9C9611, 9CG (greased), 9D8496 (8 detents), 9D9237
  (1 detent); all "22" gauge, "750 lbs", "6.176"" mount hole centre-to-centre. No aluminium
  9-inch variant is listed there.
- WW Hardware TR09C: "$6.79 each", "Center hole: 4-9/16"", "750 lb", "Screws not included".
- Amazon 9CW (same bearing, Triangle branded): $33.99; bullet: "Size: 9", shape: Round,
  center hole diameter: 4.595", nominal balanced load capacity: 750 lbs." Title says
  "5/16" Thick".
- Converted (arithmetic, not read): 9 in = 228.6 mm OD; 4.5 in = 114.3 mm centre hole;
  6.176 in = 156.9 mm between mounting holes; 5/16 in = 7.9 mm thick. The 228.6 mm OD is
  inside the 200-260 mm window and clears the 309 mm dome inside diameter by about 40 mm
  radially. The mounting holes on Triangle bearings are on the two square plates, four per
  plate (Triangle catalog convention; hole diameter not read from the page, so size the
  printed bosses for M5 or #10 screws and confirm on the received part).
- The Lee Valley aluminium lazy-susan page returned HTTP 429 on every attempt, so no
  aluminium option is verified. Steel 22-gauge is the verified choice.

### Ball bearings

- VXB single 6001-2RS page: "Dynamic load rating: 5,100 N", "Static load rating: 2,390 N",
  "Maximum speed (greased): 18,000 RPM", "Chrome Steel", price "$10.00" single. The PGN
  10-pack on Amazon is $11.45; PGN's own page does not print load ratings, so use the VXB
  figures, which are the standard 6001 catalogue values.
- VXB 608-2RS on Amazon: "Static load rating of 141 kgf and dynamic load rating of 336 kgf",
  "Chrome steel", price $9.92 single. PGN 608-2RS 10-pack $9.95 ("Chrome Steel Sealed").
- Sizing check (arithmetic): robot mass estimate about 12-15 kg total (estimated, not
  read). The centre-foot caster pivot carries roughly one third of the weight in the
  three-leg stance, about 50 N, far below the 6001 static rating of 2,390 N. Two 6001
  bearings per shoulder are therefore sized by the 12 mm bolt, not by load.

### Shoulder pivot hardware

- Bolt Depot M12-1.75 class 8.8 zinc hex bolts, quoted rows: "6269 100mm $1.89 / ea
  $31.58 / 25", "6270 110mm $2.26 / ea", "6271 120mm $2.44 / ea", "6272 130mm $2.83 / ea",
  "6273 140mm $3.20 / ea", "6274 150mm $3.53 / ea". "Wrench size 19mm".
- The 6001 bearing bore is 12 mm; an M12 hex bolt shank is nominally 12 mm but rolled
  threads run under size, so the bolt fits the bearing bore with clearance. The 12 mm
  chrome linear rod alternate (12 mm ± 0.5 mm stated) with DIN 471 circlips is the tighter
  option if the bolt shank is loose.
- Bushings: HARFINGTON flanged bronze, "Bore Diameter: 12mm, Outer Diameter: 16mm, Total
  Length: 20mm, Flange Diameter: 20mm, Flange Thickness: 2mm". These press into a 16 mm
  printed bore as a low-cost pivot if the 6001 bearings are not used.
- Dowel pins: the Fabory 6 x 30 mm 50-pack states only "steel"; the InStock 10-pack states
  "STEEL". Neither page states a hardness, so the "hardened" property is not verified.
  Use them as index pins in a 6.0 mm printed hole with an M6 bore check.

### Threaded rod and general fasteners

- Bolt Depot 8 mm x 1.25 mm zinc threaded rod: "Threaded rod length is measured from end
  to end", "23774 1m $11.25 / ea $308.50 / 35". Coupling nut on the same page: "15801
  Metric coupling nuts, Zinc plated class 6 steel, 8mm x 1.25mm x 24mm ... $0.62 / ea".
- Bolt Depot M8 class 8.8 hex nut "4788 8mm x 1.25mm $0.06 / ea $4.84 / 100"; M8 flat
  washer "4529 8mm $0.05 / ea $2.33 / 100"; M8 fender washer "17832 8mm x 24mm $0.28 / ea";
  M12 hex nut "4790 12mm x 1.75mm $0.24 / ea $9.13 / 50"; M12 flat washer "4531 12mm
  $0.08 / ea"; M12 fender washer "17834 12mm x 37mm $0.56 / ea"; M4 nut "4784 4mm x 0.7mm
  $0.05 / ea"; M3 nut "4783 3mm x 0.5mm $0.05 / ea"; M4 washer "4525 4mm $0.05 / ea".
- The Bolt Depot nylon-insert lock nut and socket cap screw list pages returned an index
  or HTTP 403 during this session, so those two items are sourced from Amazon instead.

### Heat-set inserts and hole sizes

- ruthex comparison table on the Amazon M4 and M5 pages, quoted verbatim: sizes
  "M2 / M3 / M4 / M5", "Height (mm) 4,0 / 5,7 / 8,1 / 9,5", "Insert hole (mm) 3,2 / 4,0 /
  5,6 / 6,4", "Package contents 70 / 100 / 50 / 50".
- Adafruit 4255 page: outer diameter 4.2 mm for the M3 x 4 mm insert.
- Design rule (read from the Creative3DP chart, a secondary source,
  https://tools.creative3dp.com/blog/heat-set-insert-hole-size-chart/): "M3 short: 4.0mm
  outer diameter, 4.24mm CAD pocket diameter, 4.5mm pocket depth"; "M4: 5.6mm outer
  diameter, 5.83mm CAD pocket diameter, 8.6mm pocket depth"; "M5: 6.4mm outer diameter,
  6.63mm CAD pocket diameter, 10.0mm pocket depth". Model the CAD hole about 0.2 mm over
  the nominal insert hole and 1 mm deeper than the insert.

### Head-drive tensioner

- Verified spring: 10 mm OD, 25 mm free length, 0.6 mm wire, 304 stainless, 5 for $2.24.
  No spring rate is published. Estimated rate for 0.6 mm wire, 9.4 mm mean coil diameter,
  about 8 active coils: about 0.25 N/mm (estimated from the helical spring formula with
  G = 70 GPa; not read). That gives about 2.5 N at 10 mm compression, which is a light
  preload; stack two or choose a 1.0 mm wire spring if more pressure is needed.
- Screw adjuster: an M5 socket cap screw through a printed lug with the uxcell M5 knurled
  thumb nut ("Head Dia: 16mm", "Height: 4mm") or the Bolt Depot M5 wing nut ($0.16) gives
  a tool-free tension stop. M5 x 40 mm 304 stainless socket cap screws are listed on Amazon
  at $3.99 per 10 (https://www.amazon.com/dp/B0DY4HF7N8, search result only, page not
  fetched).

### Battery tie-down

- MECCANIXITY straps: "Length: 400mm/16 inch; Width: 25mm/1 inch", nylon, 6 for $7.59.
  Battery girth around the 151 x 94 mm faces is about 490 mm (arithmetic); one strap is
  too short to circle the battery, so anchor each strap end to a printed slot and cinch
  across the top, or use two straps joined. The Voltage VT-100 tray alternate states the
  12 V 7 Ah battery "will mount sideways" and includes its strap.

### Filament and print guidance

- Bambu Lab US store, PETG HF: "PETG HF $12.99 USD /roll (Lowest price for 10+ rolls)
  MSRP: $19.99 USD"; "PETG HF is discontinued and will not be restocked once sold out. A new
  and improved PETG is available now!" (link target: products/petg-basic).
- PETG Basic store page: "$11.69 USD /roll (Lowest price for 10+ rolls) MSRP: $17.99 USD".
- PETG-CF store page: "From $31.99 USD"; "5. Nozzle Recommendation Due to the addition of
  carbon fiber, PETG-CF requires a more wear-resistant hardened steel nozzle. While a 0.4
  mm hardened steel nozzle can be used, a 0.6 mm hardened steel nozzle is recommended".
  "AMS lite NOT Compatible".
- PLA Basic store page: "$12.99 USD /roll (Lowest price for 10+ rolls) MSRP: $19.99 USD".
- PETG HF TDS V1.0 (store.bblcdn.com): "Nozzle Temperature 230 - 260 °C", "Bed Temperature
  65 - 75 °C", "Nozzle Size 0.2, 0.4, 0.6, 0.8 mm", "Cooling Fan 0 - 60%", "Printing Speed
  < 300 mm/s", "Chamber Temperature 35 - 50 °C", "Drying ... 65 °C, 8 h", density
  "1.28 g/cm³", HDT "62 °C" at 1.8 MPa, "Tensile Strength (X-Y) 34 ± 4 MPa", "(Z) 23 ± 4
  MPa", "Bending Strength (X-Y) 64 ± 3 MPa", "(Z) 48 ± 4 MPa", "Impact Strength (X-Y)
  31.5 ± 2.2 kJ/m²", "Young's Modulus (X-Y) 1810 ± 190 MPa".
- PETG Basic TDS V3.0: "Nozzle Temperature 230 - 260 °C", "Bed Temperature 65 - 75 °C",
  "Cooling Fan 0 - 60%", density "1.25 g/cm³", "Tensile Strength (X-Y) 51 ± 1 MPa",
  "(Z) 35 ± 6 MPa", "Bending Strength (X-Y) 75 ± 3 MPa", "(Z) 56 ± 4 MPa", "Impact Strength
  (X-Y) 34.2 ± 4.1 kJ/m²", HDT "68 °C" at 1.8 MPa, "Bending Modulus (X-Y) 1950 ± 50 MPa".
- PETG-CF TDS V2.0: "Nozzle Temperature 240 - 270 °C", "Bed Temperature 65 - 75 °C",
  "Cooling Fan 100%", "Printing Speed < 200 mm/s", density "1.25 g/cm³", "Tensile Strength
  (X-Y) 59 ± 4 MPa", "(Z) 38 ± 3 MPa", "Bending Strength (X-Y) 83 ± 4 MPa", "(Z) 62 ± 3
  MPa", "Bending Modulus (X-Y) 2890 ± 130 MPa", "Impact Strength (X-Y) 41.2 ± 2.6 kJ/m²",
  HDT "68 °C" at 1.8 MPa, "Young's Modulus (X-Y) 2460 ± 230 MPa".
- Bambu wiki PETG guide (https://wiki.bambulab.com/en/filament/petg): "You can improve
  model strength by adjusting the number of walls and the sparse infill density. It is
  recommended to keep the wall count ≤ 6 and infill density ≤ 50%, and to use a spiral
  pattern for sparse infill"; "Increasing the wall layers and sparse fill density will
  increase the risk of warping". Nozzle compatibility table: "PETG Basic / PETG HF
  Compatible with all standard nozzles"; "PETG CF Compatible with hardened steel nozzles;
  not recommended for use with 0.4 mm high-flow nozzles"; drying "60 - 65 °C, 8 h" oven.
  Line width note: "with a 0.4 mm nozzle, the default inner wall line width is 0.45 mm, and
  the outer wall is 0.42 mm".
- H2D store page specs (https://us.store.bambulab.com/products/h2d): "Nozzle Hardened
  Steel", "Max Nozzle Temperature 350 °C", "Included Nozzle Diameter 0.4 mm", "Supported
  Nozzle Diameter 0.2 mm, 0.4 mm, 0.6 mm, 0.8 mm", "Build Volume (W*D*H) Single Nozzle
  Printing: 325*320*325 mm³", price "$1,749.00 USD" (typical "$1,999.00").
- Recommendation derived from the above (design judgement, not read): structural body
  rings, legs and feet in PETG Basic or PETG-CF, 0.4 mm hardened nozzle (stock on H2D),
  5 walls and 30-40 % gyroid as locked in `plan.md` (inside the wiki's 6-wall / 50 % limit),
  255 °C nozzle (the TDS specimen temperature) and 70 °C bed. PETG-CF gives the highest
  X-Y bending strength (83 MPa) and is the choice for the shoulder bosses and leg cores.
  Dome in PLA Basic for detail is acceptable because the dome carries only its own weight
  on the ring bearing; PLA Basic printed at the profile default is fine for the one-piece
  dome (temperatures not read here).
- Mass estimate (arithmetic, not read): a 317 mm x 4 mm wall body ring 60 mm tall is
  about 0.24 L of wall plus infill; the full body, legs and feet are expected to use
  about 4-5 kg of PETG at the locked settings. Buy five 1 kg spools of PETG and one of
  PLA. This is an estimate until `scripts/slice_check.py` reports real filament use.

### Adafruit 3766 wheel hub geometry

- Motor drawing `research/components/3777_diagram.jpg` (viewed): output shaft "Ø5.40"
  with flat "3.70" across; shaft stubs "9.25" and "8.60" from the gearbox faces; overall
  tip-to-tip "36.60"; gearbox thickness "18.60"; body "70.00" long, "22.44" tall; two
  Ø3.00 mounting holes "17.60" apart; rear tab Ø3.00 hole. (Numbers read from the
  drawing.)
- Adafruit 3766 page: "Wheel body dimensions: 63 x 29mm / 2.4" x 1.1"", "Product Weight:
  38.0g / 1.3oz", "press-fit design", "only for use with 'TT' gearbox DC motors", $1.50,
  "Out of stock". No hub depth is published.
- Adafruit 4205 multi-hub wheel (same motor fit): "TT motor/LEGO hub: 5.4 x 3.5mm".
  KitsGuru 65 mm TT wheel: "Center Shaft Hole: 5.4 mm round edge / 3.5 mm flat edge",
  "Wheel Width: 27 mm", "Load Capacity: 2 kg" (https://kitsguru.com/products/red-65mm-tt-bo-motor-robot-wheel).
- Product photos 3766-00/01/02 (viewed): the hub is a short cylindrical boss on the
  inner face of the five-spoke rim with a D-shaped centre hole and five small holes
  around it. Hub depth estimated 9-10 mm to match the 8.6-9.25 mm shaft stubs; boss
  outer diameter estimated 10-11 mm; rim inner clearance to the motor face estimated
  about 3 mm. These are estimates from photographs, not measurements.
- Design use: the printed foot must leave a 30 mm wide slot per wheel (29 mm wheel plus
  clearance) and place the motor face about 3 mm from the rim edge; the D-flat on the
  3766 hub is 3.5-3.7 mm (wheel pages quote 3.5 mm, motor drawing quotes 3.7 mm; the
  press fit absorbs the difference).

## Fetch log

- Fetched and parsed: Adafruit 3766, 4205, 4255, 4256, 3763; Triangle 9C and 9-inch
  family; WW Hardware TR09C; VXB 9-inch, 6001-2RS single, 6001-2RS 10-pack, 608-2RS
  10-pack; Bolt Depot M12 hex bolt list, M8 rod, M8/M12/M4/M3 hex nuts, M8/M12/M4 flat
  washers, M8/M12 fender washers, M5 wing nuts; Amazon pages listed in the tables;
  Bambu US store PETG HF, PETG Basic, PETG-CF, PLA Basic, H2D; Bambu wiki PETG guide;
  Bambu TDS PDFs for PETG HF, PETG Basic, PETG-CF; ruthex.de M3/M4/M5 pages (EUR prices
  only, no hole data); CNC Kitchen US store M3 x 3 and M4 x 4.
- Failed fetches (source replaced): Lee Valley aluminium lazy susan (HTTP 429),
  McMaster-Carr (not attempted, JavaScript catalogue), Home Depot Everbilt M12 (HTTP 403),
  Fasteners Direct (HTTP 404), SKF product pages (no data returned), Bolt Depot nylon
  insert lock nut and socket cap screw lists (index page or HTTP 403), Amazon search
  pages for socket screw kits and springs (blocked after repeated requests).
