# Proportions basis for the fable-r2d2 CAD (scale 0.68386, body diameter 317.0 mm)

Written 2026-09-12. This file is the dimensional basis for `cad/params.scad`.
Every full-size number states where it came from. Scaled values are full-size x 0.68386.
Full-size reference: club-standard body and dome diameter 463.55 mm (18.250 in).
317.0 / 463.55 = 0.68386.

## How to read this file

- `callout` means the number is printed on the drawing sheet. `vector` means the number was
  measured from the PDF line geometry with PyMuPDF (script `research/drawings/` notes below).
  `derived` means arithmetic on callout or vector numbers. `estimated` means read from a
  photograph or from proportions; treat those as +/- 10 %.
- Angles around the dome: 0 deg is the front centreline, positive is toward the viewer's right
  when facing the droid, negative toward the viewer's left. 1 deg = 4.0452 mm at the outer dome
  bottom edge (callout, dome sheet 1 of 5).
- Body skin coordinates: `s` is arc distance along the skin from the front (or rear) centreline,
  positive to the viewer's right when facing that side; `y` is distance down from the top edge of
  the body skin. Body angle = s / 231.775 mm (radians) full size.
- Heights inside the dome are measured up from the bottom of the dome mounting ring.

## Source files (all downloaded 2026-09-12 into `research/drawings/`)

| File | URL | Content |
|---|---|---|
| `dome.pdf` (6 pages) | https://drive.google.com/uc?export=download&id=1fAxIsXaZ4BRMuzGLnUxOrCqwdlohrtTK | CuriousMarc dome plans: overall + section C-C (page 1), top view (page 2), front (3), left (4), rear (5), right (6). Scale 1:3 on paper, callouts in mm and inches. |
| `radar-eye.pdf` (5 pages) | https://drive.google.com/uc?export=download&id=1OhXXVwif-kEkqneUvaADvfwZNuPA_GXG | CuriousMarc radar eye, inches. |
| `outer-ellipse.jpg` | https://drive.google.com/uc?export=download&id=1RLd9V_hdf1VzVRctENI3pKB1yJAXX6SS | SolidWorks sketch of the outer dome profile (463.55, 250.37, 21.67, 1.59). |
| `csr.anh.skins.rev2.zip` | https://r2d2.media-conversions.net/images/csr.anh.skins/csr.anh.skins.rev2.zip | Front/rear inner/outer skin cut files (PDF + DWG). No callouts; measured by vector. |
| `mc.box.beam.legs.v4.zip` | https://r2d2.media-conversions.net/document.pkgs/doc.zips/mc.box.beam.legs.v4.zip | Box-beam legs, 5 sheets, 1:1, inches. |
| `mc.outer.foot.shell.zip` | https://r2d2.media-conversions.net/document.pkgs/doc.zips/mc.outer.foot.shell.zip | Outer foot shell, 2 sheets, 1:1. |
| `mc.SAK.CSR.ctr.foot.v1.zip` | https://r2d2.media-conversions.net/document.pkgs/doc.zips/mc.SAK.CSR.ctr.foot.v1.zip | CS:R centre foot, 4 sheets, 1:1, plus STL trims (mm). |
| `mc.csr.horseshoes.zip` | https://r2d2.media-conversions.net/document.pkgs/doc.zips/mc.csr.horseshoes.zip | CS:R horseshoe layers (1:1, with a printed 1 in x 1 in check square) and the R2 Builders Club `CSR SHOULDER - HORSESHOE 20140601.PDF` (dimensioned). |
| `mc.skirt.v2.zip` | https://r2d2.media-conversions.net/document.pkgs/doc.zips/mc.skirt.v2.zip | Skirt base ring and skirt bottom, dimensioned. |
| `mc.3leg.fixed.shoulder.zip`, `mc.2leg.fixed.shoulder.zip` | https://r2d2.media-conversions.net/document.pkgs/doc.zips/ | Shoulder hubs, 6.560 in dia. |
| `mc.NextGen.Frame.v2.zip` | https://r2d2.media-conversions.net/document.pkgs/doc.zips/mc.NextGen.Frame.v2.zip | CS:R NextGen frame rings, ribs, shoulder plates (1:1). |
| `mc.eggcrate.frame.zip`, `mc.center.ankle.zip`, `MC.Hex.Center.Ankle.doc.set.v2.zip`, `mc.battery.box.zip`, `mc.octagon.port.zip`, `mc.util.arm.box.zip`, `mc.util.arm.zip`, `mc.center.foot.zip`, `mc.dome.motivator.zip` | https://r2d2.media-conversions.net/R2.Document.Packages.html | Supporting packages, all 1:1. |
| `curiousmarc-2-3-2-overview.pdf` | https://astromech.net/gallery2/main.php?g2_view=core.DownloadItem&g2_itemId=47918 | Marc Verdiell, 2-3-2 system overview (leg angles). |
| `photos/` | https://www.printed-droid.com/wp-content/uploads/2020/01/ (Body-Full, Body-Full-Back, Leg-1, Dome-Terms, R2-D2-Terminology-v1.2-2020-01.pdf) | Photographs used only for feature identification and for values marked estimated. |

Scale checks performed on the Media-Conversions sheets (all plotted 1:1): leg outline measured
26.205 in against the 26.205 callout; skirt base ring measured 18.015 in against R9.008; shoulder
hub measured 6.560 in against the 6.560 callout; the printed 1 in x 1 in square on the horseshoe
sheet measured 1.000 in. The ANH skin PDFs carry no callouts. Their plot scale was fixed from the
creator's own statement (https://r2d2.media-conversions.net/R2.CSR.ANH.skins.html): outer skin
circumference 57.3340 in, plus 0.125 in overlap at each end and 0.0625 in at top and bottom.
The outer profile measures 36.948 x 25.155 sheet-inches; 36.948 / (57.334/2 + 0.25) = 1.27773.
At that scale every panel comes out on clean fractions (3.000 x 13.000 doors, 1.500 x 0.375 coin
slots, 12.313 x 2.375 arm bays) and the skin height is 19.688 - 0.125 = 19.563 in, which is the
CS:L body height quoted by Make: (https://makezine.com/projects/building-your-first-r2/:
"the body height specification for CS:L is 19.563\", and for CS:R it's 19.35\"").

## 1. Dome

### 1.1 Envelope and profile

| Item | Full size | Scaled mm | Source |
|---|---|---|---|
| Outer dome diameter | 463.55 mm (18.250 in) | 317.0 | callout, dome page 2 and page 1 note; outer-ellipse.jpg |
| Outer dome ellipse, vertical semi-axis | 250.37 mm (9.857 in) | 171.2 | callout, dome page 1 note, radar-eye page 1, outer-ellipse.jpg |
| Outer dome ellipse, horizontal semi-axis | 231.77 mm (9.125 in) | 158.5 | callout, same |
| Inner dome ellipse (R x r) | 248.78 x 230.19 mm | 170.1 x 157.4 | callout, dome page 1 |
| Cylindrical lip under the ellipse | 21.67 mm (0.853 in) | 14.8 | callout, dome pages 1,3,4,5,6; outer-ellipse.jpg |
| Outer dome shell height (lip + ellipse) | 272.04 mm | 186.0 | derived 21.67 + 250.37 |
| Dome sheet thickness (aluminium) | 1.59 mm (0.063 in) | n/a (print wall instead) | callout, dome page 1 |
| Assembled dome height, bottom of mounting ring to top | 287.82 mm (11.332 in) | 196.8 | callout, dome page 3 |
| Ellipse rise from lip top to dome top | 249.94 mm (9.840 in) | 170.9 | callout, dome page 3 |
| Height of lip top above mounting-ring bottom | 37.88 mm | 25.9 | derived 287.82 - 249.94 |
| Height of side-panel bottom edge above mounting-ring bottom | 51.27 mm (2.018 in) | 35.1 | callout, dome pages 3-6 |
| Bottom mounting ring height | 24.77 mm (0.975 in) | 16.9 | callout, dome pages 1,3 |
| Bottom mounting ring outer diameter | 462.98 mm (18.228 in) | 316.6 | callout, dome page 1 C-C |
| Bottom mounting ring inner diameter | 412.11 mm (16.225 in) | 281.8 | callout, dome page 1 C-C |
| PTFE inner-dome ring diameter / thickness | 380.31 mm (14.973 in) / 4.76 mm (0.188 in) | 260.1 / 3.3 | callout, dome page 1 C-C |
| Gap ring between mounting ring and decorative ring | 3.18 mm (0.125 in) | 2.2 | callout, dome page 3 |
| Decorative ring (part 5) height | 16 mm (0.630 in) | 10.9 | callout, dome page 3 |
| Radial step lip to ring | 4.20 mm (0.165 in) | 2.9 | callout, dome page 1 C-C |
| Ring stack top (24.77 + 3.18 + 16) | 43.95 mm | 30.1 | derived; vector outline of the outer dome in the front view starts 46.5 mm above the ring bottom |
| Callout 38.16 mm (1.502 in) in C-C and 26.50 mm (1.043 in) in the front view | as stated | 26.1 / 18.1 | callouts, dome pages 1 and 3; their datum is not resolved, listed for completeness |

Profile for the CAD (full size, z measured up from the lip bottom, r = radius):
r = 231.77 for 0 <= z <= 21.67; r(z) = 231.77 * sqrt(1 - ((z - 21.67)/250.37)^2) for 21.67 < z <= 272.04.
Scaled: r = 158.5 for 0 <= z <= 14.8; r(z) = 158.5 * sqrt(1 - ((z - 14.8)/171.2)^2) up to z = 186.0.
The dome sits on a ring stack 43.95 mm (scaled 30.1) tall; the printed dome should
include this ring as its base so the assembled height is 287.82 mm (scaled 196.8).

### 1.2 Top: disc and pie panels (dome page 2, top view)

| Item | Full size | Scaled mm | Source |
|---|---|---|---|
| Centre hole / top button diameter | 27.40 mm (1.079 in) | 18.7 | callout; vector circle 27.31 |
| Top disc diameter | 92.20 mm (3.630 in) | 63.1 | callout; vector circle 92.20 |
| Top disc opening diameter (disc + 2 mm gap) | 96.31 mm (3.792 in) | 65.9 | callout; vector circle 96.39 |
| Pie panel inner edge diameter | 123 mm (4.843 in) | 84.1 | callout; vector: pie edges run r 61.5 to 135 |
| Pie panel outer edge diameter | 270 mm (10.630 in) | 184.6 | callout |
| Pie panel count and sector | 6 panels of 60 deg | 6 x 60 deg | vector: dividers at 0, +-60, +-120, 180 deg |
| Divider strip width between pie panels | 8.70 mm (0.343 in) | 5.9 | callout; vector: edges offset +-4.38 from the radial |
| Pie panel cut clearance | 2.5 mm typ (0.098 in) | 1.7 | callout |
| Side panel cut clearance | 2 mm (0.5 deg) typ | 1.4 | callout |
| Top holoprojector HP3 opening diameter | 64.50 mm (2.539 in) | 44.1 | callout, view facing HP3 |
| HP3 opening offsets in the HP3 view | 40 mm (1.575 in) and 5 mm (0.197 in) | 27.4 and 3.4 | callouts, view facing HP3 (offsets from the pie-panel edges) |
| HP3 angular position | 146.85 deg (in pie panel PP3, 120-180 deg) | 146.85 deg | callout |
| HP3 centre, horizontal offset seen in the left view | 84.60 mm (3.331 in) | 57.9 | callout, dome page 4; centre radius = 84.60/cos(33.15 deg) = 101 mm derived |

Pie panel identities (dome page 1 legend): PP1 saber launcher 0 to +60 deg, PP2 life-form scanner
+60 to +120, PP3 top holoprojector +120 to 180, PP4 periscope 180 to -120, PP5 -120 to -60,
PP6 -60 to 0. Assignment of names to sectors is inferred from the labelled top view.

### 1.3 Side panel angular layout (dome page 2 callouts, degrees from the front centreline)

Right side (viewer's right): 7.19, 13.86, 25.50, 35.75, 47.25, 48.75, 60.25, 61.75, 73.25, 74.75,
99.40, 101.10, 113.50, 118, 145, 146.50, 146.85, 159.50, 169.80, 177.
Left side (viewer's left): 9.38, 10.61, 16.55, 18.03, 31.38, 33.11, 39.04, 42.26, 91.70, 98.62,
120.37, 150.04, 153.25, 159.43, 170.50.

Identified panels (callouts cross-checked against the front-view vector geometry):

| Panel | Angular span | Height | Note |
|---|---|---|---|
| P14 front PSI panel | -9.38 to +13.86 deg (93.2 mm wide vector, centre offset +8.70 mm callout) | 53.50 mm (36.6) | bottom on the 51.27 line |
| P13 small panel | +10.61 to +16.55 deg is the callout pair; vector places the 24.5 mm wide panel at -10.3 to -16.5 deg (left of P14) | 53.5 mm (36.6) | gap to P14 5.73 mm (0.225 in) suggested |
| P12 front logic displays | -18.03 to -31.38 deg (frame edges -16.55 / -33.11) | 81 mm (55.4) | see 1.5 |
| P11 | -33.11 to -39.04 deg (27 mm wide, vector) | 81 mm | narrow strip |
| P10 | starts at -42.26 deg, ends near -91.70 / -98.62 deg | 81 mm | large left panel |
| HP1 front holoprojector | centre +25.50 deg | opening 64.50 mm (44.1) | see 1.5 |
| P1 | +35.75 to +47.25 deg | 81 mm | vector 42.9 mm projected |
| P2 | +48.75 to +60.25 deg | 81 mm | vector 37.6 mm projected |
| P3 | +61.75 to +73.25 deg | 81 mm | vector 30.1 mm projected |
| P4, P5 (magic panel), P6, P7 (metal panel) | +74.75 ... +99.40/101.10, 113.50, 118, 145/146.50 deg | 81 or 88 mm (60.2) | P6 detail B: opening 70.50 x 54 mm (48.2 x 36.9), edge offsets 18, 15.33, 6, 5.50 mm, corner R5 |
| P8 rear PSI panel | centre +159.50 deg | 81 mm | see 1.5 |
| DB1, DB2 dome buttons | +159.50 and +166.80 deg, dia 21 mm (14.4) | - | callouts 9.20 and 6.60 mm spacing, 9.50 / 9.50 / 29 mm vertical callouts in detail C |
| HP2 rear holoprojector | 37 mm to the left of the rear centreline (about -170.8 deg), vector | opening 64.4 mm vector | centre 99.77 mm (68.2) above ring bottom, callout 3.928 in |
| P9 rear logic display | -120.37 to -150.04 deg (frame -153.25) | 77 mm (52.7) | window 64.50 x 26 mm (44.1 x 17.8), 12 mm from the panel bottom, 5.50 mm side offset, 0.50 mm cuts between sub panels (detail D) |
| Callouts -159.43, -170.50, +169.80, +177 deg | edges of the rear panels around HP2 | - | not assigned |

### 1.4 Radar eye (radar-eye.pdf, inches)

| Item | Full size | Scaled mm | Source |
|---|---|---|---|
| Inner surface | ellipsoid 9.125 in short (horizontal) x 9.857 in long (vertical) semi-axes = the dome | same as dome | page 1 note |
| Outer surface | cone, generator 24.09 deg from vertical | 24.09 deg | page 1 note |
| Profile sweep about the dome axis | 31.315 deg (-15.57 to +15.57) | 31.315 deg | page 1 note, page 2 |
| Profile height along the surface | 4.200 in (106.7 mm) | 73.0 | page 1, page 5 |
| Lower edge height above the ellipse base plane (lip top) | 2.647 in (67.2 mm) | 46.0 | page 1 |
| Top face width in profile | 1.130 in (28.7 mm) | 19.6 | page 1 |
| Base flange in profile | 0.823 in (20.9 mm) | 14.3 | page 1 |
| Profile corner angles | 112 deg top, 80 deg bottom | same | page 1 |
| Lens opening diameter | 3.000 in (76.2 mm) | 52.1 | page 2 |
| Lens rim height above the face | 0.250 in (6.3 mm) | 4.3 | page 2 |
| Lower slot | 0.100 in deep x 0.150 in tall, sweep -5 to +10 deg, cut parallel to the base | 1.7 x 2.6 | page 2 |
| Left side trim | 8.5 deg from vertical (171.50 deg corner) | same | page 2 |
| Bottom wedge removed | 14 deg, from 7.89 to 15.57 deg | same | page 3 |
| Right side shelf | extra 4.65 deg sweep (15.57 to 20.22 deg), face milled 0.400 in from the top | 6.9 | page 4 |
| Shelf channels | narrow 0.045 in deep, large 0.125 in deep; steps 0.770, 0.220, 0.087, 0.900, 0.286, 0.094 in | 0.8 / 2.2 | page 4 |
| Linear check dimensions | 4.010, 3.613, 2.942, 3.582, 4.200, 0.546, 0.355, 1.209, 2.811, 3.907 in | x 17.37 mm/in | page 5 (info only) |
| Housing extent in the dome front view | x -63.9 to +67.4 mm projected; 110.5 to 213.3 mm above ring bottom | 75.6 to 145.9 high | vector, dome page 3 |
| Lens centre position | on the front centreline (+0.1 mm), 172.5 mm above ring bottom | 118.0 | vector, dome page 3 |
| Callouts near the eye in the front view | 8.70 mm (P14 offset), 2.50 mm gap, 3.51 mm top offset | 5.9, 1.7, 2.4 | callouts, dome page 3 |

### 1.5 Front and rear openings

| Item | Full size | Scaled mm | Source |
|---|---|---|---|
| HP1 holoprojector opening | 64.50 mm (2.539 in) dia | 44.1 | callout, dome page 3 |
| HP1 centre height above ring bottom | 92.77 mm (68 mm above the mounting ring top) | 63.4 | callout, dome page 3 |
| HP1 centre angle | +25.50 deg (vector +97.2 mm projected) | +25.50 deg | callout, dome page 2 |
| Front PSI opening | 39.50 mm dia | 27.0 | callout, dome page 3 |
| Front PSI centre height | 26.75 mm above the panel bottom line = 78.02 mm above ring bottom | 53.4 | callout + derived |
| Front PSI centre angle | +7.19 deg (vector +28.7 mm projected) | +7.19 deg | callout |
| P14 panel | 93.2 mm wide (vector) x 53.50 mm tall, centre +8.70 mm | 63.7 x 36.6 | vector + callouts |
| Front logic display windows (P12, detail A) | two windows, each 28.50 mm tall, 39.4 mm wide projected (about 43 mm true) | 19.5 tall, 29.4 wide | callout height; vector width |
| P12 detail A offsets | 6.50, 5.50, 8, 4, 2 mm; panel 81 mm tall | 4.4, 3.8, 5.5, 2.7, 1.4 | callouts |
| P12 panel projected width | 53.3 mm at -18.03 to -31.38 deg | 36.4 | vector |
| Rear PSI opening | 49.7 mm dia (no callout; measured) | 34.0 | vector, dome page 5 |
| Rear PSI centre height | 91.77 mm (3.613 in) above ring bottom | 62.8 | callout, dome page 5 |
| Rear PSI panel P8 rounded cutout | 97.4 x 58 mm, corner R5 | 66.6 x 39.7 | vector + callout |
| Rear callout 147.73 mm (5.816 in) | top of the rear panel group above ring bottom | 101.0 | callout, dome page 5 |
| Left view callout 61.77 mm (2.432 in) | width of the small upper panel P6 | 42.2 | callout, dome page 4 |
| Left view callout 273.48 mm (10.767 in) | overall height callout on that sheet | 187.0 | callout, dome page 4 (datum not resolved) |

## 2. Body

### 2.1 Overall

| Item | Full size | Scaled mm | Source |
|---|---|---|---|
| Body diameter over the outer skin | 18.25 in (463.55 mm) | 317.0 | creator statement, skins page; equals the dome |
| Frame diameter under the skins | 18.09 in (459.5 mm) | 314.2 | creator statement, skins page |
| Body height, top ring to bottom of frame (skin height) | 19.563 in (496.9 mm) | 339.8 | vector 19.688 minus 0.125 trim; matches CS:L 19.563 (Make:). CS:R lists 19.35 in |
| Frame rib length (ring 1 bottom to ring 4 top) | 19.375 in (492.1 mm) | 336.5 | vector, NextGen ribs sheet |
| Frame ring 1 outer size | 17.250 x 18.017 in (flats on the sides) | 299.6 x 313.0 | vector, eggcrate ring1 and NextGen ring 0 |
| Ring 4 top ring outer diameter | 18.017 in; inner core 12.288 in | 313.0 / 213.4 | vector, eggcrate ring4 / NextGen ring 4 |
| Dome bearing | Rockler 17-3/8 in lazy susan (client build practice) | 301.8 | Make: article |
| Shoulder hub diameter | 6.560 in (166.6 mm) | 113.9 | callout, 2-leg and 3-leg fixed shoulder sheets |
| Shoulder hub centre bore | 1.180 in (30 mm) | 20.5 | callout |
| Shoulder hub thickness (3-leg fixed) | risers 1.668 in + 2 x 0.25 in plates = 2.168 in | 37.7 | callouts; NextGen hub uses 1.42 in PVC + 2 x 0.1875 plates = 1.795 in |
| Shoulder opening in the skin | diameter 6.63 in (rear skin arc R3.316), 6.51 in (front skin arc) | 115.2 | vector |
| Shoulder centre below the body top edge | 3.87 in (98.3 mm) | 67.2 | vector: arc centre 3.93 in from the untrimmed top, minus 0.0625 trim |
| Shoulder centre above the body bottom (skirt top) | 15.69 in (398.6 mm) | 272.5 | derived 19.563 - 3.87 |
| Shoulder angular position | on the front/rear skin seam, +-90 deg | +-90 deg | vector: half-circle cutouts at both skin side edges |

### 2.2 Skirt (mc.skirt.v2, callouts)

| Item | Full size | Scaled mm | Source |
|---|---|---|---|
| Skirt base ring (ring 0) radius | R9.008 in (diameter 18.016 in) | 312.9 dia | callout; vector 18.015 |
| Skirt vertical height (riser a) | 2.375 in (60.3 mm) | 41.3 | callout |
| Skirt curved side slant height | 2.555 in, between R11.389 and R13.943 (developed) | 44.4 | callouts |
| Skirt bottom plate | 13.420 x 10.920 in; arcs R6.710; inner rectangle 10.788 x 7.324 in | 233.1 x 189.7 | callouts |
| Skirt angled (front/rear) side panel | 2.387 in wide, edges 9.580 in and 7.826 in | 41.5 wide, 166.4 / 135.9 | callouts |
| Skirt straight side strip | 0.500 x 7.826 in | 8.7 x 135.9 | callout |
| Skirt curved edge strip | 12.934 x 0.500 in | 224.7 x 8.7 | callout |
| Skirt ribs | 12 ribs, 0.5 in thick | 8.7 | callout |

Skirt slope: the skirt narrows from R9.008 at the top to about R6.71 at the bottom over 2.375 in
height, i.e. 2.30 in of inset, about 44 deg from vertical (derived). Scaled inset 40.0 mm.

### 2.3 Front skin features (anh.front.outer.plus.v2.pdf, vector at scale 1.27773)

All values are outer-skin cut lines. `s` is arc distance from the front centreline (viewer's right
positive), `y` is down from the top of the body. Full-size inches; scaled mm in the fourth column.
Feature names follow the R2 Builders terminology sheet; names marked (id. from photo) were matched
to the printed-droid front photograph by projected position.

| Feature | Position (full size) | Size (full size) | Scaled mm | Note |
|---|---|---|---|---|
| Outer-skin cut-out for the arm/LDP block | s -6.219 to +6.218 in (-39.0 to +39.0 deg); y -0.062 to 5.875 in | 12.437 x 5.938 in | s -108.0 to +108.0; y -1.1 to 102.1; size 216.0 x 103.1 | the inner skin and arm boxes fill this |
| Large data port (LDP) opening | s -5.282 to +5.281 in (-33.2 to +33.2 deg); y -0.062 to 1.000 in | 10.563 x 1.063 in | s -91.7 to +91.7; y -1.1 to 17.4; size 183.5 x 18.5 | vector; notch at the very top edge |
| Upper utility arm bay | s -6.157 to +6.156 in (-38.7 to +38.7 deg); y 1.000 to 3.376 in | 12.313 x 2.375 in | s -106.9 to +106.9; y 17.4 to 58.6; size 213.9 x 41.3 | bay outline |
| Lower utility arm bay | s -6.157 to +6.156 in (-38.7 to +38.7 deg); y 3.438 to 5.812 in | 12.313 x 2.375 in | s -106.9 to +106.9; y 59.7 to 101.0; size 213.9 x 41.3 | bay outline |
| Upper utility arm outline (decorative) | s -5.282 to +5.281 in (-33.2 to +33.2 deg); y 1.438 to 2.938 in | 10.563 x 1.500 in | s -91.7 to +91.7; y 25.0 to 51.0; size 183.5 x 26.1 | the arm STL is 9.509 x 2.501 x 1.375 in |
| Lower utility arm outline (decorative) | s -5.282 to +5.281 in (-33.2 to +33.2 deg); y 3.876 to 5.375 in | 10.563 x 1.500 in | s -91.7 to +91.7; y 67.3 to 93.4; size 183.5 x 26.1 |  |
| Tall door, left | s -9.844 to -6.844 in (-61.8 to -43.0 deg); y 1.000 to 14.001 in | 3.000 x 13.000 in | s -171.0 to -118.9; y 17.4 to 243.2; size 52.1 x 225.8 | inner lines 2.875 x 12.875 and rounded 2.250 x 12.250 |
| Tall door, right | s +6.843 to +9.843 in (+43.0 to +61.8 deg); y 1.000 to 14.001 in | 3.000 x 13.000 in | s +118.9 to +171.0; y 17.4 to 243.2; size 52.1 x 225.8 | same |
| Panel above the coin slots | s -6.219 to -2.344 in (-39.0 to -14.7 deg); y 6.375 to 8.876 in | 3.875 x 2.500 in | s -108.0 to -40.7; y 110.7 to 154.2; size 67.3 x 43.4 | inner 3.750 x 2.375 |
| Coin slots (6) | s -6.219 to -4.719 in (-39.0 to -29.6 deg); y 9.376 to 13.812 in | 1.500 x 4.437 in | s -108.0 to -82.0; y 162.9 to 239.9; size 26.1 x 77.1 | six slots 1.500 x 0.375 in, top edges at y 9.375, 10.188, 11.000, 11.813, 12.625, 13.438 (pitch 0.8125) |
| Narrow panel right of the coin slots | s -4.219 to -2.344 in (-26.5 to -14.7 deg); y 9.376 to 13.876 in | 1.875 x 4.500 in | s -73.3 to -40.7; y 162.9 to 241.0; size 32.6 x 78.2 | rounded inner 1.125 x 3.750 |
| Vent column panel | s -1.844 to +1.843 in (-11.6 to +11.6 deg); y 6.375 to 13.876 in | 3.687 x 7.500 in | s -32.0 to +32.0; y 110.7 to 241.0; size 64.0 x 130.3 | holds both louvred vents |
| Upper louvred vent opening | s -1.527 to +1.526 in (-9.6 to +9.6 deg); y 6.606 to 10.021 in | 3.053 x 3.415 in | s -26.5 to +26.5; y 114.7 to 174.1; size 53.0 x 59.3 | rounded rectangle |
| Lower louvred vent opening | s -1.527 to +1.526 in (-9.6 to +9.6 deg); y 10.230 to 13.646 in | 3.053 x 3.415 in | s -26.5 to +26.5; y 177.7 to 237.0; size 53.0 x 59.3 | rounded rectangle |
| Panel right of the vents (restraining bolt panel) | s +2.343 to +6.218 in (+14.7 to +39.0 deg); y 6.375 to 13.876 in | 3.875 x 7.500 in | s +40.7 to +108.0; y 110.7 to 241.0; size 67.3 x 130.3 | rounded inner 3.125 x 6.750 |
| Row of short panels: left | s -4.844 to -2.844 in (-30.4 to -17.9 deg); y 14.376 to 15.626 in | 2.000 x 1.250 in | s -84.1 to -49.4; y 249.7 to 271.4; size 34.7 x 21.7 |  |
| Row of short panels: centre | s -1.844 to +1.843 in (-11.6 to +11.6 deg); y 14.376 to 15.626 in | 3.687 x 1.250 in | s -32.0 to +32.0; y 249.7 to 271.4; size 64.0 x 21.7 |  |
| Row of short panels: right | s +2.843 to +6.218 in (+17.9 to +39.0 deg); y 14.376 to 15.626 in | 3.375 x 1.250 in | s +49.4 to +108.0; y 249.7 to 271.4; size 58.6 x 21.7 |  |
| Row of short panels: far right | s +6.843 to +9.843 in (+43.0 to +61.8 deg); y 14.376 to 15.626 in | 3.000 x 1.250 in | s +118.9 to +171.0; y 249.7 to 271.4; size 52.1 x 21.7 |  |
| Pocket vent door (id. from photo) | s -11.344 to -6.844 in (-71.2 to -43.0 deg); y 14.376 to 19.125 in | 4.500 x 4.750 in | s -197.0 to -118.9; y 249.7 to 332.2; size 78.2 x 82.5 | vent louvres are on the inner skin |
| Coin return, left (id. from photo) | s -6.219 to -2.282 in (-39.0 to -14.3 deg); y 16.125 to 19.125 in | 3.937 x 3.000 in | s -108.0 to -39.6; y 280.1 to 332.2; size 68.4 x 52.1 |  |
| Power coupling panel | s -1.532 to +1.531 in (-9.6 to +9.6 deg); y 16.125 to 19.125 in | 3.063 x 3.000 in | s -26.6 to +26.6; y 280.1 to 332.2; size 53.2 x 52.1 | centred on the front; coupling disc diameter estimated 2.4 in |
| Coin return, right (id. from photo) | s +2.312 to +4.062 in (+14.5 to +25.5 deg); y 16.125 to 19.125 in | 1.750 x 3.000 in | s +40.2 to +70.6; y 280.1 to 332.2; size 30.4 x 52.1 | inner 1.625 x 2.875 |
| Small panel | s +4.562 to +5.562 in (+28.6 to +34.9 deg); y 16.125 to 19.125 in | 1.000 x 3.000 in | s +79.3 to +96.6; y 280.1 to 332.2; size 17.4 x 52.1 | inner 0.875 x 2.875 |
| Small panel | s +6.062 to +7.062 in (+38.1 to +44.3 deg); y 16.125 to 19.125 in | 1.000 x 3.000 in | s +105.3 to +122.7; y 280.1 to 332.2; size 17.4 x 52.1 |  |
| Octagon port | s +7.875 to +10.906 in (+49.5 to +68.5 deg); y 16.125 to 19.125 in | 3.031 x 3.000 in | s +136.8 to +189.4; y 280.1 to 332.2; size 52.6 x 52.1 | octagon 3.0 across flats; port body 2.938 across flats, corner cuts 0.75 in |
| Side vent notch (front half) | s -14.334 to -12.084 in (-90.0 to -75.9 deg); y 8.001 to 14.001 in | 2.250 x 6.000 in | s -249.0 to -209.9; y 139.0 to 243.2; size 39.1 x 104.2 | same notch on the rear skin; combined side-vent opening 4.50 x 6.00 in centred on the seam |
| Lower seam notch (front half) | s -14.334 to -11.719 in (-90.0 to -73.6 deg); y 15.562 to 19.625 in | 2.615 x 4.063 in | s -249.0 to -203.6; y 270.3 to 340.9; size 45.4 x 70.6 | same on the rear skin; combined 5.23 x 4.06 in at the bottom of each side |

### 2.4 Rear skin features (anh.rear.outer.plus.v2.pdf, same method)

`s` is measured from the rear centreline, positive to the viewer's right when facing the rear.

| Feature | Position (full size) | Size (full size) | Scaled mm | Note |
|---|---|---|---|---|
| Rear door cut-out in the outer skin | s -6.225 to +6.225 in (-39.1 to +39.1 deg); y 0.992 to 19.634 in | 12.450 x 18.643 in | s -108.1 to +108.1; y 17.2 to 341.1; size 216.3 x 323.8 | removable rear door |
| Upper wide panel | s -5.662 to +5.661 in (-35.6 to +35.5 deg); y 1.556 to 6.309 in | 11.323 x 4.754 in | s -98.3 to +98.3; y 27.0 to 109.6; size 196.7 x 82.6 | inner 11.198 x 4.629, rounded 10.572 x 4.004 |
| Tall panel, left | s -5.662 to -2.283 in (-35.6 to -14.3 deg); y 6.809 to 13.879 in | 3.379 x 7.069 in | s -98.3 to -39.7; y 118.3 to 241.1; size 58.7 x 122.8 | rounded inner 2.627 x 6.318 |
| Tall panel, centre | s -1.533 to +1.533 in (-9.6 to +9.6 deg); y 6.809 to 13.879 in | 3.066 x 7.069 in | s -26.6 to +26.6; y 118.3 to 241.1; size 53.3 x 122.8 | rounded inner 2.315 x 6.318 |
| Tall panel, right | s +2.283 to +5.661 in (+14.3 to +35.5 deg); y 6.809 to 13.879 in | 3.378 x 7.069 in | s +39.7 to +98.3; y 118.3 to 241.1; size 58.7 x 122.8 | rounded inner 2.627 x 6.318 |
| Tall door, left | s -9.853 to -6.850 in (-61.9 to -43.0 deg); y 0.992 to 14.005 in | 3.003 x 13.013 in | s -171.1 to -119.0; y 17.2 to 243.3; size 52.2 x 226.0 | as front |
| Tall door, right | s +6.850 to +9.853 in (+43.0 to +61.9 deg); y 0.992 to 14.005 in | 3.003 x 13.013 in | s +119.0 to +171.1; y 17.2 to 243.3; size 52.2 x 226.0 | as front |
| Row of short panels | s -5.662 to +9.853 in (-35.6 to +61.9 deg); y 14.380 to 15.630 in | 15.515 x 1.251 in | s -98.3 to +171.1; y 249.8 to 271.5; size 269.5 x 21.7 | four panels: 8.810-12.189, 12.939-16.005, 16.755-20.133, 21.322-24.325 |
| Bottom row, left (coin return / pocket vent) | s -5.662 to -2.283 in (-35.6 to -14.3 deg); y 16.131 to 19.134 in | 3.379 x 3.002 in | s -98.3 to -39.7; y 280.2 to 332.3; size 58.7 x 52.1 |  |
| Power coupling panel | s -1.533 to +1.533 in (-9.6 to +9.6 deg); y 16.131 to 19.134 in | 3.066 x 3.002 in | s -26.6 to +26.6; y 280.2 to 332.3; size 53.3 x 52.1 | centred |
| Bottom row, right | s +2.283 to +5.661 in (+14.3 to +35.5 deg); y 16.131 to 19.134 in | 3.378 x 3.002 in | s +39.7 to +98.3; y 280.2 to 332.3; size 58.7 x 52.1 |  |
| Octagon port | s +6.834 to +9.869 in (+42.9 to +62.0 deg); y 16.131 to 19.134 in | 3.035 x 3.002 in | s +118.7 to +171.4; y 280.2 to 332.3; size 52.7 x 52.1 |  |
| Pocket vent door | s -11.354 to -6.850 in (-71.3 to -43.0 deg); y 14.380 to 19.134 in | 4.504 x 4.754 in | s -197.2 to -119.0; y 249.8 to 332.3; size 78.2 x 82.6 |  |
| Side vent notch (rear half) | s -14.347 to -12.095 in (-90.1 to -75.9 deg); y 7.998 to 14.005 in | 2.252 x 6.006 in | s -249.2 to -210.1; y 138.9 to 243.3; size 39.1 x 104.3 |  |
| Lower seam notch (rear half) | s -14.347 to -11.730 in (-90.1 to -73.7 deg); y 15.569 to 19.634 in | 2.617 x 4.066 in | s -249.2 to -203.8; y 270.4 to 341.1; size 45.5 x 70.6 |  |

### 2.5 Body hardware sizes from the 1:1 packages

| Item | Full size | Scaled mm | Source |
|---|---|---|---|
| Octagon port body | 2.938 in across flats, 1.438 in flat length, 0.75 in corner cut | 51.0 / 25.0 / 13.0 | vector, mc.octagon.port |
| Octagon port depth (left/right edge strip) | 3.188 in long strip, 1.067-1.187 in deep | 20.6 deep | vector |
| Octagon port discs | 1.25, 1.50, 1.75 in dia stack | 21.7, 26.1, 30.4 | vector |
| Utility arm box | 8.690 in deep x 2.100 in tall (side), curved top/bottom 10.2 in x 2.1 in | 150.9 x 36.5 | vector, mc.util.arm.box |
| Utility arm (STL bounding box) | 9.509 x 2.501 x 1.375 in | 165.2 x 43.4 x 23.9 | trimesh on utility.arm.stl (inches) |
| Dome drive internal gear | 17.39 in outer ring, gear inside; spur gear 2.10 in | 302.1 | vector, NextGen page 8 (reference only; this project uses a friction drive) |

## 3. Legs

### 3.1 Outer leg (mc.box.beam.legs.v4, 1:1, vector-checked against callouts)

| Item | Full size | Scaled mm | Source |
|---|---|---|---|
| Leg overall length, shoulder disc edge to ankle tip | 26.205 in (665.6 mm) | 455.2 | callout sheet 3; vector 26.205 |
| Shoulder centre to ankle pivot hole | 21.639 in (549.6 mm) | 375.9 | vector: hub hole centre (3.932, 4.596) to 0.375 in hole (25.571, 4.596) |
| Shoulder disc diameter on the leg | 7.865 in (199.8 mm) | 136.6 | callout sheet 3 |
| Hub hole in the leg | 3.385 in (86.0 mm) | 58.8 | vector; matches horseshoe R1.695 opening |
| Leg strut width (main leg) | 4.295 in (109.1 mm) | 74.6 | vector: strut edges 6.49 to 14.16 in from the shoulder centre |
| Taper from disc to strut | 1.345 in long (x 5.15 to 6.49 from shoulder centre) | 23.4 | vector |
| Ankle section width | 4.970 in (126.2 mm) | 86.3 | vector: x 14.16 to 19.50 in from the shoulder centre |
| Ankle section length (leg bottom parts) | 8.110 in (206.0 mm) | 140.9 | callout sheet 1; vector |
| Ankle tip: taper to a 1.000 in flat | taper 2.53 in long, flat 1.0 in at 22.03 in, rounded end at 22.27 in from shoulder centre | 43.9 / 17.4 | vector |
| Ankle pivot hole | 0.375 in (9.5 mm) | 6.5 | vector |
| Leg thickness, shoulder/strut section | 1.750 in (0.125 + 0.125 + 1.250 + 0.125 + 0.125) | 30.4 | callout sheet 1 layer naming |
| Leg thickness, ankle section | 2.500 in | 43.4 | callout sheet 1 |
| Ankle curve (top of the ankle block) parts | AC ring, AC end with 30 deg bevel, AC top inner/outer | - | sheet 4; the ankle block top is a half-round over the 4.97 in width |
| Leg skins | shoulder skin 22.650 x 1.750; under-shoulder 2.235 x 1.750; ankle top 5.336 x 2.500; ankle gap 0.920; ankle plug 3.834 x 1.500; ankle bolt 5.743 x 1.000 (all oversize 0.08 w / 0.5 l) | - | callouts sheet 5 |
| Leg bottom plates | outside 8.110 long (0.25 and 0.125 thick); inside 6.060; bottom inner 2.050 tip plate 0.375 thick | 140.9 / 105.3 / 35.6 | callouts sheet 1 |

### 3.2 Horseshoe and shoulder (CSR SHOULDER - HORSESHOE 20140601.PDF, R2 Builders Club, inches; MC horseshoe layers)

| Item | Full size | Scaled mm | Source |
|---|---|---|---|
| Horseshoe overall width | 8.025 in (203.8 mm) | 139.4 | callout; outer radius R4.013 |
| Horseshoe overall height | 10.526 in (4.013 above the hub centre + 6.513 below) | 182.8 | callouts R4.013 and 6.513; MC layer 10.485 x 7.945 plus 0.040 skin |
| Horseshoe hub opening radius | 1.695 in (43.1 mm) | 29.4 | callout |
| Horseshoe thickness | 0.875 in (recess 0.65) | 15.2 | callout section A-A; MC layers 0.188+0.188+0.125+0.188+0.188 |
| Horseshoe arm width at the bottom | 1.825 in (46.4 mm) | 31.7 | callout |
| Gap between the arms at the bottom | 4.375 in (111.1 mm) | 76.0 | callout |
| Inner cut-out width above the arms | 2.588 in (65.7 mm) | 45.0 | callout |
| Depth of the lower inner cut-out below the hub centre | 4.938 in (125.4 mm) | 85.8 | callout |
| Arm end bevel | 53 deg; inner corner angles 106 deg and 127 deg | same | callouts |
| Square detail pockets | three 1.250 in squares on one arm, 0.625 in spacing | 21.7 | callouts |
| Shoulder button holes | 2.63 / 1.487 / 1.75 in pattern, 0.203 in dia | - | callouts |
| Rectangular pocket on the other arm | 1.075 x 3.945 in (0.538, 0.995 offsets) | 18.7 x 68.5 | callouts |
| Shoulder hub visible disc | 6.560 in dia, plates 0.25 in | 113.9 | MC 2-leg/3-leg shoulder sheets |
| Shoulder flange skin strip | 20.875 x 1.680 in (wraps the hub edge) | 362.6 x 29.2 | callout |
| Booster cover (blue block on the leg under the horseshoe) | about 4.5 in tall x 2.4 in wide x 1.0 in proud | about 78.2 x 41.7 x 17.4 | estimated from photos/leg.png against the 4.295 in strut width |
| Shoulder hydraulics detail | about 1.5 x 0.9 in | about 26.1 x 15.6 | estimated from photos/leg.png |

### 3.3 Ankles

| Item | Full size | Scaled mm | Source |
|---|---|---|---|
| Outer ankle block (leg ankle section) | 4.970 in wide x 2.500 in thick x 8.110 in long | 86.3 x 43.4 x 140.9 | vector + callouts, legs sheets 1,3 |
| Outer ankle cylinders (pair, horizontal) | about 1.25 in dia x 2.5 in long | about 21.7 x 43.4 | estimated from photos/leg.png |
| Ankle cylinder wedges / holders | about 1.2 in wide | about 20.8 | estimated |
| Ankle bracelet band | about 0.5 in tall around the ankle block | about 8.7 | estimated |
| Centre ankle plates (inner inside / inner outside) | 4.795 in wide x 7.982 in tall; 0.25 in thick (eggcrate) or 0.188 (hex) | 83.3 x 138.6 | vector, mc.center.ankle and Hex Center Ankle |
| Centre ankle bottom taper | 37.5 deg from vertical, from 5.233 in down, to a 0.931 in flat | same | vector |
| Centre ankle top slots | two 0.25 x 2.0 in slots at 0.797 and 3.748 in | - | vector |
| Centre ankle ring (curved top) | 5.772 x 4.125 in | 100.3 x 71.7 | vector |
| Centre ankle shelf | 4.795 x 2.457 in | 83.3 x 42.7 | vector |
| Centre ankle skins | bottom 7.5 x 1.05; side 5.3 x 2.5; shelf 5.75 x 0.85; curve 4.875 x 2.253 | - | vector |
| Centre ankle load distribution plate | 2.080 x 6.458 in (Hex set)  | 36.1 x 112.2 | vector |

## 4. Feet

### 4.1 Outer foot shell (mc.outer.foot.shell, 1:1 vector)

| Item | Full size | Scaled mm | Source |
|---|---|---|---|
| Length at the bottom | 14.000 in (355.6 mm) | 243.2 | vector: side door frame bottom edge |
| Length at the top | 7.064 in (179.4 mm) | 122.7 | vector: side door frame top edge; matches the 7.062 top shells |
| Width at the bottom | 7.100 in (180.3 mm) | 123.3 | vector: end panel bottom edge |
| Width at the top | 3.500 in (0.75 + 1.00 slot + 1.75) | 60.8 | vector: top narrow 0.75, ankle slot 1.00, top wide 1.75 |
| Vertical height | 5.02 in | 87.2 | derived: 5.192 x cos(14.9 deg) = 6.033 x cos(33.7 deg) = 5.02 |
| End face slope | 33.7 deg from vertical | 33.7 deg | vector: door frame diagonals |
| Side face slope | 14.9 deg from vertical | 14.9 deg | vector: end panel diagonals (flat pattern) |
| Side door | 12.292 x 4.395 in trapezoid (top 6.502), inner 11.823 x 4.145 | 213.5 x 76.3 | vector |
| Door frame inner opening | 12.543 x 4.645 in | 217.9 x 80.7 | vector |
| Straight side panel (inboard face) | 11.453 x 3.125 in with a 4.0 x 1.5 in notch, 35.1 deg ends | 198.9 x 54.3 | vector |
| Ankle slot in the top | 1.000 in wide, full top length 7.06 in | 17.4 wide | vector |
| End panel ankle notch | 1.000 in wide x 1.820 in deep, plus 0.125 x 3.82 in slit | 17.4 x 31.6 | vector |
| Trim strips | front 3.518 x 1.000 (two 0.625 holes), rear 3.518 x 1.000, panel trim 6.852 x 0.432, corner trims 2.493 x 1.682 | - | vector |
| Half-moon details on the end faces | about 1.7 in wide x 1.0 in tall, two per end face | about 29.5 x 17.4 | estimated from photos |
| Foot stripe (toe slot) | about 5.5 x 0.3 in | - | estimated |

### 4.2 Battery boxes (mc.3D.Printed.Battery.Box, 1:1 vector)

| Item | Full size | Scaled mm | Source |
|---|---|---|---|
| Battery box side panel (length x height) | 6.875 x 4.875 in | 119.4 x 84.7 | vector |
| Battery box width (end panel) | 3.080 in; End 4 obround panel 8.080 x 3.080 with 5.000 in straight | 53.5 | vector |
| End 3 panel | 5.750 x 3.040 in | 99.9 x 52.8 | vector |
| Half-round ends (End 1 / End 2) | 1.205 x 3.007 in (semi-circle of dia 3.0) | 52.1 dia | vector |
| Hose hole in End 1 | 0.500 in dia | 8.7 | callout |
| Position on the foot | two per outer foot, on the inboard side, one at each end, bottom flush with the foot bottom | - | estimated from photos/body-front.jpg and terminology p6 |
| Battery box harness / hoses | hose about 0.5 in dia, knurled fittings about 0.75 in dia | about 8.7 / 13.0 | estimated |

### 4.3 Centre foot (mc.SAK.CSR.ctr.foot.v1 and mc.center.foot, 1:1 vector; STL trims in mm)

| Item | Full size | Scaled mm | Source |
|---|---|---|---|
| Length at the bottom | 10.375 in (263.5 mm) | 180.2 | vector: shell long side outer; STL full.trim set 263.525 mm |
| Width at the bottom | 7.100 in (180.3 mm) | 123.3 | vector: shell short side; STL 180.34 mm |
| Length at the top | 3.375 in (85.7 mm) | 58.6 | vector |
| Width at the top | 3.000 in (0.99 + 1.02 slot + 0.99) | 52.1 | vector |
| Vertical height | 5.00 in | 86.9 | derived: 5.288 x cos(18.9) = 6.002 x cos(33.5) = 5.00 |
| End face slope | 33.5 deg from vertical | 33.5 deg | vector |
| Side face slope | 18.9 deg from vertical | 18.9 deg | vector |
| Ankle slot in the top | 1.020 in wide x 1.770 in deep in the end panels | 17.7 x 30.7 | vector |
| Main structural plate | 9.750 x 4.750 in trapezoid, 35.7 deg sides | 169.4 x 82.5 | vector |
| Bottom plate | 9.750 x 6.630 in with a 5.400 in caster hole | 169.4 x 115.2 | vector |
| Caster used by the club design | Colson 3 in swivel caster, 3/8-16 stem; or 4 in omni wheels | - | callout, SAK page 4 |

### 4.4 Ankle pivot height above the ground

| Item | Full size | Scaled mm | Source |
|---|---|---|---|
| Two-leg overall height | 1.09 m (42.9 in) | 745.4 | https://www.starwars.com/databank/r2-d2 (Lucasfilm databank), also https://www.dimensions.com/element/star-wars-r2-d2 |
| Dome + body + skirt stack | 287.82 + 496.9 + 60.3 = 845.0 mm | 577.9 | derived from sections 1 and 2 |
| Skirt bottom above ground, two-leg | 1090 - 845.0 = 245 mm (9.65 in) | 167.5 | derived |
| Shoulder centre above ground, two-leg | 1090 - 287.82 - 98.3 = 703.9 mm (27.71 in) | 481.4 | derived |
| Ankle pivot above ground | 703.9 - 549.6 = 154.3 mm (6.07 in) | 105.5 | derived: shoulder-to-ankle 21.639 in = 549.6 mm; foot is 127.5 mm tall so the pivot sits about 27 mm above the foot top |

## 5. Stance

| Item | Full size | Scaled mm | Source |
|---|---|---|---|
| Two-leg overall height | 1090 mm (42.9 in) | 745.4 | Lucasfilm databank 1.09 m |
| Angle between centre leg and outer legs, three-leg mode | 36 deg | 36 deg | CuriousMarc 2-3-2 overview: "the angle between the center leg and the outer legs is 36 deg, which is the amount the shoulder ... should be rotated" |
| Shoulder index positions on the club shoulder plate | hole sets 36 deg apart (holes at 0, +-36, +-54, +-90, +-126, +-144, 180 deg on r 2.563 in; +-45, +-135 on r 2.506 in) | 36 deg | vector, NextGen ribs & plates sheet (holes A = 2-leg, C = 3-leg) |
| Body tilt in three-leg mode | 18 deg back (top toward the rear) | 18 deg | inferred: the 36 deg is split equally, the standard club figure; foot-to-leg angle 18 deg per the 2-3-2 overview |
| Outer leg angle from vertical, three-leg mode | 18 deg, feet forward of the shoulders | 18 deg | derived from the two lines above |
| Shoulder centre above ground, three-leg | 154.3 + 549.6 x cos 18 = 677 mm | 463.0 | derived |
| Three-leg overall height | 677 + (98.3 + 287.82) x cos 18 = 1044 mm (41.1 in), +/- 25 mm | 713.9 | estimated (dome top on the tilted axis) |
| Outer ankle pivot forward of the shoulder, three-leg | 549.6 x sin 18 = 169.8 mm | 116.1 | derived |
| Skirt-bottom centre forward of the shoulder, three-leg | 458.9 x sin 18 = 141.8 mm (458.9 mm = 398.6 body below shoulder + 60.3 skirt) | 97.0 | derived |
| Centre foot pivot behind the outer ankle pivots | 169.8 - 141.8 = 28 mm | 19.1 | derived; centre leg is on the body axis |
| Skirt-bottom centre above ground, three-leg | 677 - 458.9 x cos 18 = 240.5 mm | 164.5 | derived; centre leg + foot must span this |
| Centre leg height needed (skirt bottom to ground) | 240.5 mm; foot 127 mm + ankle about 113 mm | 164.5 (86.9 + 77.6) | derived |
| Leg centreline offset from the body axis | about 10.5 in (267 mm) | about 182.4 | estimated from photos/body-front.jpg (body 18.25 in wide = 355 px; leg centres 205 px off axis); the hub sits inside the 6.6 in skin opening |
| Track width, outer foot centre to centre | about 21 in (533 mm) | about 364.8 | estimated, twice the line above |
| Overall width over the outer feet | about 28 in (711 mm); photo measures 27.0 in | about 486.4 | estimated |
| Outer ankle race travel (club actuated designs) | 48 deg: 38 deg back + 10 deg forward | - | CuriousMarc 2-3-2 overview (reference only; this project uses fixed index pins) |

## 6. Scaled summary for `cad/params.scad`

| Parameter | Full size mm | Scaled mm | Note |
|---|---|---|---|
| body_od | 463.55 | 317.0 | 317.0 mm target; 463.55 x 0.68386 = 317.0 |
| body_skin_height | 496.90 | 339.8 | top ring to frame bottom |
| skirt_height | 60.32 | 41.3 |  |
| skirt_bottom_radius | 170.43 | 116.6 | flats 10.92 in apart full size |
| shoulder_center_below_body_top | 98.30 | 67.2 |  |
| shoulder_hub_od | 166.62 | 113.9 |  |
| shoulder_skin_hole | 168.40 | 115.2 |  |
| dome_od | 463.55 | 317.0 |  |
| dome_ellipse_a_vertical | 250.37 | 171.2 |  |
| dome_ellipse_b_horizontal | 231.77 | 158.5 |  |
| dome_lip | 21.67 | 14.8 |  |
| dome_ring_stack | 43.95 | 30.1 | under the shell; assembled height 287.82 full size |
| dome_assembled_height | 287.82 | 196.8 |  |
| panel_bottom_line | 51.27 | 35.1 | above ring bottom |
| side_panel_height | 81.00 | 55.4 |  |
| hp_opening | 64.50 | 44.1 | HP1, HP2, HP3 |
| front_psi_opening | 39.50 | 27.0 | centre 78.02 mm above ring bottom, +7.19 deg |
| rear_psi_opening | 49.70 | 34.0 | centre 91.77 mm above ring bottom, +159.5 deg |
| fld_window | 28.50 | 19.5 | height; two windows in P12 |
| rld_window_w | 64.50 | 44.1 | x 26 tall |
| radar_lens | 76.20 | 52.1 | 3.000 in |
| leg_shoulder_to_ankle | 549.63 | 375.9 |  |
| leg_strut_width | 109.09 | 74.6 |  |
| leg_ankle_width | 126.24 | 86.3 |  |
| leg_thickness_upper | 44.45 | 30.4 |  |
| leg_thickness_ankle | 63.50 | 43.4 |  |
| leg_shoulder_disc | 199.77 | 136.6 |  |
| horseshoe_w | 203.84 | 139.4 |  |
| horseshoe_h | 267.36 | 182.8 |  |
| horseshoe_t | 22.22 | 15.2 |  |
| outer_foot_l_bottom | 355.60 | 243.2 |  |
| outer_foot_l_top | 179.43 | 122.7 |  |
| outer_foot_w_bottom | 180.34 | 123.3 |  |
| outer_foot_w_top | 88.90 | 60.8 |  |
| outer_foot_h | 127.51 | 87.2 |  |
| center_foot_l_bottom | 263.52 | 180.2 |  |
| center_foot_w_bottom | 180.34 | 123.3 |  |
| center_foot_h | 127.00 | 86.9 |  |
| battery_box | - | 119.4 x 84.7 x 53.5 | |
| ankle_pivot_height | 154.30 | 105.5 | above ground, two-leg |
| two_leg_height | 1090.00 | 745.4 |  |
| three_leg_height | 1044.00 | 713.9 | estimated |
| body_tilt_three_leg_deg | - | 18 | |
| leg_angle_three_leg_deg | - | 18 from vertical, 36 from the body axis | |
| track_width | 533.40 | 364.8 | estimated |

## 7. Open points

- The dome ring stack datum: the sheets give 287.82 assembled, 249.94 ellipse rise, 51.27 panel
  bottom line and a 21.67 lip, which do not close arithmetically with the 24.77 + 3.18 + 16 ring
  stack. The CAD uses the assembled height 287.82 and the panel line 51.27 as fixed, and lets the
  lip overlap the printed base ring.
- Body height: the skins are 19.563 in (CS:L). Make: quotes 19.35 in for CS:R. The 0.21 in
  difference is 3.7 mm at model scale; the skin value is used because every feature position
  comes from that skin drawing.
- Leg offset from the body, track width, booster cover, ankle cylinders, half-moons, battery box
  placement and the three-leg heights are estimated or derived, not club callouts.
- The side-panel callouts beyond P3 on the right and P10 on the left are listed but not assigned;
  the dome sheets themselves (`research/drawings/dome-p2.png` to `dome-p6.png`) are the authority
  for those cuts.

Rendered sheets for reference: `research/drawings/dome-p1.png` ... `dome-p6.png`,
`research/drawings/radar-eye-p1.png` ... `p5.png`, `research/drawings/png/*.png` (all packages),
`research/drawings/png/front-skin-crop.png`, `rear-skin-crop.png`.
