# R2-D2 appearance references

Research checked 2026-09-12. Scope: external geometry for a detailed 609.6 mm (24 in) printable model. This note records primary sources and separates drawing dimensions from visual interpretation. It does not certify a particular screen prop or prescribe robot hardware.

## Verified proportions

Lucasfilm lists R2-D2's height as 1.09 m. Scaling that nominal height to 609.6 mm gives a scale factor of 0.559266. This is a design normalization, not proof that every filming prop or stance had that height. [Official character reference](https://www.starwars.com/databank/r2-d2)

Marc Verdiell's outer ellipse drawing gives a 463.55 mm diameter, a 250.37 mm vertical semiaxis, and a 21.67 mm straight lower lip. The horizontal semiaxis is approximately 231.77 mm. The curve is taller than a hemisphere: vertical/horizontal radius is 1.0803. At the chosen scale, diameter is 259.25 mm, curved rise is 140.02 mm, and lip height is 12.12 mm. A useful profile is `r(z) = 231.775 * sqrt(1 - (z/250.37)^2)` above the lip, then scale all coordinates. [Creator's outer ellipse drawing](https://drive.google.com/file/d/1RLd9V_hdf1VzVRctENI3pKB1yJAXX6SS/view)

The six-page dome PDF separately dimensions the assembled front-view height as 287.82 mm. Its lower ring stack must not be confused with the ellipse rise. It specifies 2.5 mm typical pie-panel clearance and 2 mm typical side-panel clearance, equivalent to 1.40 mm and 1.12 mm at this scale. The front holoprojector opening is 64.50 mm; the front PSI opening is 39.50 mm. These become 36.07 mm and 22.09 mm. The front logic panel has two stacked openings, each 28.50 mm high. [Dome drawings, overall and sheets 1–2](https://drive.google.com/file/d/1fAxIsXaZ4BRMuzGLnUxOrCqwdlohrtTK/view)

Frank Pirz independently specifies an 18.25 in finished CS:R body diameter: 463.55 mm, matching the dome. His inner and outer skins have different wrap lengths. The files include trim allowance; their 20 x 30 in stock labels are not finished body dimensions. [Creator's ANH skin explanation](https://r2d2.media-conversions.net/R2.CSR.ANH.skins.html)

Body height, shoulder spacing, shoulder-to-ankle length, and foot bounding dimensions were not verified from explicit dimension callouts in this research. Do not label guessed values as club dimensions. Preserve a single scale across verified parts; adjust final assembled height only after checking stance and ring overlap.

## Feature map

Directions below mean the viewer's left/right when looking at the named view. Placements are observed from drawings and creator photographs, not surveyed coordinates.

The front dome has an angular blue radar-eye housing above the lower band. The dark convex lens sits inside that housing; it is separate from the silver holoprojector to its lower right. Two logic windows stack at lower left. A round PSI sits below the eye. Six crown pie panels and a top disk break up the silver surface. The rear has a different layout: PSI on the left, holoprojector near center, long logic window on the right, and two small buttons above the PSI. A third holoprojector projects from an upper panel. Use the drawing's panel angles instead of evenly repeating identical sectors. [Dome plan](https://drive.google.com/file/d/1fAxIsXaZ4BRMuzGLnUxOrCqwdlohrtTK/view), [creator's dome diagram](https://www.printed-droid.com/wp-content/uploads/2020/01/Dome-Terms.jpg)

The radar-eye drawing defines a curved rear surface, conical front surface, side shelf, bottom wedge, and narrow lower slot. The main profile sweeps 31.315 degrees around the vertical axis; the front cone generator is 24.09 degrees from vertical. Its lens opening is 3.000 in, or 42.62 mm at this model scale. This cannot be represented faithfully by a plain cylinder glued to the dome. [Radar-eye construction drawings](https://drive.google.com/file/d/1OhXXVwif-kEkqneUvaADvfwZNuPA_GXG/view)

The body front has a narrow large data port below the dome, then two blue utility arms in separate horizontal bays. Below are two rounded rectangular louvered vents in a blue frame. A vertical coin-slot bank sits to their left. Lower details include pocket vents, recessed coin returns, a central circular power coupling, and octagonal side ports. Tall access doors flank the center group. The skirt slopes inward with separate ribs. [Creator's front photograph](https://www.printed-droid.com/wp-content/uploads/2020/01/Body-Full-725x1024.jpg)

The rear has a broad upper access panel and three tall central panels below it. Its bottom row has a central coupling and returns on either side; vents and octagonal ports continue toward the sides. Do not duplicate the front utility arms or louver stack onto the rear. [Creator's rear photograph](https://www.printed-droid.com/wp-content/uploads/2020/01/Body-Full-Back-725x1024.jpg)

Side legs need layered horseshoe shoulders, recessed hubs, small buttons and hydraulic details, blue booster covers, and long silver struts. Ankles carry raised bracelets, inset details, horizontal cylinders, and wedge supports. Feet have sloped shells, inset side plates, half-moon details, toe slots, separate rounded battery boxes, and ribbed hoses with fittings. The central foot is narrower and lacks the outer-foot battery-box pair. These terms describe distinct visible forms, not paint marks. [Creator's leg photograph](https://www.printed-droid.com/wp-content/uploads/2020/01/Leg-1-609x1024.png), [six-page terminology reference](https://www.printed-droid.com/wp-content/uploads/2020/01/R2-D2-Terminology-v1.2-2020-01.pdf)

## Public drawing downloads

These were downloaded and parsed successfully without login. They are reference plans, not a third-party STL package.

- [Dome PDF direct download](https://drive.google.com/uc?export=download&id=1fAxIsXaZ4BRMuzGLnUxOrCqwdlohrtTK): six pages, front/rear/side/top views and dimensions.
- [Radar-eye PDF direct download](https://drive.google.com/uc?export=download&id=1OhXXVwif-kEkqneUvaADvfwZNuPA_GXG): five pages, construction geometry and linear checks.
- [ANH skins ZIP](https://r2d2.media-conversions.net/images/csr.anh.skins/csr.anh.skins.rev2.zip): four PDF and four DWG drawings for front/rear and inner/outer skins.
- [Box-beam legs ZIP](https://r2d2.media-conversions.net/document.pkgs/doc.zips/mc.box.beam.legs.v4.zip): five PDF sheets plus CAD drawings.
- [Outer foot shells ZIP](https://r2d2.media-conversions.net/document.pkgs/doc.zips/mc.outer.foot.shell.zip): two PDF sheets plus CAD drawings.
- [Center foot ZIP](https://r2d2.media-conversions.net/document.pkgs/doc.zips/mc.SAK.CSR.ctr.foot.v1.zip): four-page CS:R shell and structural plan.
- [Creator's complete document index](https://r2d2.media-conversions.net/R2.Document.Packages.html): additional shoulders, horseshoes, skirt, battery boxes, utility arms and octagonal ports. These additional archives were located but not dimension-audited here.

## Variant and accuracy limits

Use an original-trilogy exterior with closed doors as the design reference. Do not add prequel rocket deployment or fan-added internal displays merely because a builder offers them. CuriousMarc explains that his dome combines original drawings, photographs and club parts, and that real film domes vary. [Creator's dome research notes](https://www.curiousmarc.com/r2-d2/dome-radar-eye-plans)

The Media-Conversions home page records a rear-skin accuracy correction in January 2021. The downloaded older skin archive is useful geometry evidence but was not verified as the latest corrected club release. The creator permits personal builds and excludes commercial reproduction. [Creator's revision and use notes](https://r2d2.media-conversions.net/)

R2 Builders plans on Astromech.net require free membership according to the club's UK documentation. No login restriction was bypassed. The public sources above are sufficient to replace generic geometry, but do not justify a claim of exact compliance with the latest CS:R release. [DroidBuilders UK](https://droidbuilders.uk/2021/07/03/styrene-astromech-builds/)

For visual checks, compare front, rear and side renders against the linked photographs. Also inspect the [official Lucasfilm photograph](https://lumiere-a.akamaihd.net/v1/images/r2-d2-main_f315b094.jpeg) from the character page. Photographs establish appearance and color relationships; they do not supply exact measurements. Keep printer wall thickness, joints, clearances and supports separate from screen-reference dimensions.
