# Completeness critique — research package

Reviewed 2026-09-12. Scope: `research/image-review-dome.md`, `research/image-review-body.md`,
`research/image-review-legs.md`, `research/proportions.md`, `research/components-electronics.md`,
`research/components-mechanical.md`, and the `research/images/` directory. Nothing was rewritten.
Every count below was measured by a command run on this machine (md5sum, Pillow, grep); none is
estimated.

Overall result: FAIL. Three of four checks pass. Check (b) fails because some rows in the
components tables have no price or no URL.

## Checklist

| Item | Result | Evidence |
|---|---|---|
| (a) At least 30 distinct real images listed; each listed file exists and opens as an image | PASS | 59 files listed (dome 19, body 20, legs 20). All 59 exist in `research/images/`. All 59 open with Pillow (58 JPEG, 1 PNG). 5 files are byte-identical copies of another file (md5sum), and 9 more are the same source photo saved at a different resolution (32x32 signature diff <= 2). Distinct source images: 45. |
| (b) Every product in the electronics and mechanical tables has a URL and a price | FAIL | Electronics: 30 primary rows all have URL and price; 1 of 20 alternate rows has no price. Mechanical: 36 primary rows all have URL and price (1 price marked "not confirmed"); 5 of 16 alternate rows lack a URL or a price. Rows are listed below. |
| (c) proportions.md gives scaled numbers for dome, body, legs, feet and stance | PASS | Sections 1 Dome, 2 Body, 3 Legs, 4 Feet, 5 Stance each carry a full-size and scaled-mm column; section 6 gives 47 scaled parameters for `cad/params.scad` (dome_od 317.0, dome_assembled_height 196.8, body_skin_height 339.8, leg_shoulder_to_ankle 375.9, outer_foot_l_bottom 243.2, three_leg_height 713.9, body tilt 18 deg). |
| (d) loads.md has a mass total, traction margin, runtime and shoulder moment | PASS | Section 1 Total: 13,273 g nominal, range 11,610-14,960 g. Section 2 table: margin at the 1 A limit 3.6x (Crr 0.02) and 1.8x (Crr 0.04). Section 6 table: runtime 5.2 h idle, 1.6 h continuous driving, 2.5 h mixed. Section 7 Shoulder joint: 9.4 N.m per shoulder, 176 N shear. |

## Gaps (file, missing item)

Check (b), blocking:

1. `components-electronics.md`, alternates table, row E16 alternate (Power-Sonic PSC-121000ACX): price cell reads "Not shown [read]". No price.
2. `components-mechanical.md`, alternates table, row "Threaded rod M8": alternate reads "none verified"; URL and price cells are "—". No URL, no price.
3. `components-mechanical.md`, alternates table, row "M8 nyloc": price cell reads "not read". No price.
4. `components-mechanical.md`, alternates table, row "Small screws" (uxcell M4 x 40): price cell reads "not read (search result only)". No price.
5. `components-mechanical.md`, alternates table, row "6 mm dowel pins": price cell reads "price not confirmed"; three candidate prices are quoted from the page but none is confirmed as the buy price.
6. `components-mechanical.md`, alternates table, row "Structural filament": URL and price cells are "—" (it points at the primary PETG Basic row). Acceptable as a cross-reference, but the row itself has no URL or price.

Check (b), weak but present (price given with a caveat):

7. `components-mechanical.md`, primary table, row "Closed-cell foam tape": "price not confirmed ... first listed price $4.99".
8. `components-mechanical.md`, alternates table, row "M12 x 100 bolt" (Everbilt): "$4.75 per 2-pack (from search snippet; product page returned HTTP 403)".
9. `components-mechanical.md`, alternates table, row "Cable ties" (Commercial Electric): "$12.46 (search snippet, not fetched)".
10. `components-mechanical.md`, alternates table, row "Dome ring bearing" (VXB): the page price is described as inconsistent ("$35.99" shown, "$14.99" by WebFetch); the Amazon second alternate carries a clean $33.99.

Check (a), non-blocking notes:

11. `image-review-legs.md` states each file has a "unique MD5". That is true inside the legs set only. `legs-01.jpg`, `legs-02.jpg`, `legs-03.jpg` and `legs-19.jpg` are byte-identical to `dome-07.jpg`, `body-01.jpg`, `dome-16.jpg` and `dome-18.jpg`. `dome-06.jpg` is byte-identical to `body-01.jpg`. The 30-image threshold is still met with 45 distinct sources.
12. `image-review-body.md` rows body-03 to body-11 are the same nine Wikimedia photos as dome-16, dome-07, dome-08 to dome-12, dome-14 and dome-19 at a different download size. Not a failure; noted so nobody counts them twice.

Cross-file consistency (outside the four checks, reported for the next pass):

13. Dome height disagrees between files. `image-review-body.md` finding 9 gives dome height about 0.47 body diameter (about 149 mm). `image-review-dome.md` finding 1 gives 0.60-0.62 D (190-197 mm). `proportions.md` gives dome_assembled_height 196.8 mm from the CuriousMarc sheet. `loads.md` uses 186 mm. The CAD should take the `proportions.md` value; the body review number looks like a pixel-ratio error.
14. Leg length disagrees. `loads.md` uses 430 mm shoulder to ankle; `proportions.md` gives leg_shoulder_to_ankle 375.9 mm. `loads.md` also states "outer legs vertical, body tilted 18 deg" while `proportions.md` gives outer legs 18 deg from vertical with the body tilted 18 deg (36 deg between centre and outer legs). The shoulder-moment and CG numbers in `loads.md` should be re-run on the `proportions.md` geometry.
15. Fuse ratings disagree. `loads.md` section 6 specifies main 7.5 A, charge port 2 A, motor converter 5 A, Pi converter 2 A. `components-electronics.md` buys main 15 A (E20), 3 A for charge port and Pi feed (E21), 5 A for motor regulators (E22). One of the two files must change.
16. Battery mass disagrees. `plan.md` and `loads.md` use 2.26 kg; `components-electronics.md` E15 quotes the Power-Sonic datasheet at 1.97 kg (4.34 lb) and TRC at 4.8 lb (2.18 kg). `loads.md` is conservative, so this is not a safety issue, but the mass budget could drop 0.1-0.3 kg.
17. `components-electronics.md` E19 (fuse holder) quotes the lead gauge and length from a search-result snippet because the Littelfuse page returned 403; the row is marked as such. Not a gap in URL or price.

## Method

- File existence and image validity: `md5sum images/*` and a Pillow script (`Image.open(f).verify()` then `Image.open(f).size`) over all 59 files; every file returned a format and size.
- Near-duplicate detection: each image resized to 32x32 greyscale, thresholded at its mean, and compared by Hamming distance; pairs at distance 0-2 were treated as the same photo.
- Table checks: every `|` row in the primary and alternate tables of both components files was read; a row counts as complete only when the URL cell holds an http(s) link and the price cell holds a currency figure without "not read", "not shown", or "—".
- Proportions and loads: section headings and the summary tables were read directly; the numbers quoted above are copied from those tables.
