# Dalek appearance reference review

The strongest appearance target is the bronze Time War Dalek: a low dark fender, a tapering body with ordered rows of gold hemispheres, a detailed shoulder band, a dark ringed neck, and a domed head with a raised eye cowl. The revised robot should retain that visual order while using a circular base and fully concealed arm actuators. The circular footprint and adjustable TT-motor head drive are project requirements. They are not claims about the construction of a television prop.

This report defines visual requirements for the mechanical revision. It does not certify the final CAD, printed parts, motor performance, bearing fit, or completed robot. The separate mechanical verification records must establish those points.

## Reference inventory and evidence quality

The accompanying [reference-image-review.csv](reference-image-review.csv) records 100 selected, visually inspected reference images. Each row contains its source page, original image URL, pixel dimensions, downloaded-byte SHA256, decoded-pixel SHA256, a 256-bit difference hash, an individual observation, and a proposed design implication. Reference IDs D001-D100 are stable within that inventory. All images were accessed and reviewed on 2026-09-12.

The collection contains 50 photographs from an original-prop restoration, 23 bronze-era construction, exhibition and screen images in the Dalek 63•88 archive, 13 official BBC Studios character/story images, 10 BBC America design-history images, one additional original-prop owner photograph, and three official BBC Studios/Propstore bronze auction photographs. These are 100 distinct images, not 100 distinct props. Several images document separate components and successive assembly stages of the same original prop. That coverage is useful for the hidden joints and stacking requirements as well as the exterior finish.

Seventy-seven selected images come from official BBC publications or the owner/restorer of an original prop. Twenty-three come from a specialist historical archive; that archive's historical account is secondary, and original photographer attribution varies. The archive images support visible shape and finish observations, not independent proof of a manufacturing dimension. No dimension in this robot should be justified by counting pixels in an uncalibrated photograph.

The final set has 100 unique image URLs, 100 unique downloaded-byte hashes and 100 unique decoded-pixel hashes. Visual screening also removed repeated crops, non-Dalek character portraits, packaging images, concept collages and weak views. For example, the narrow bronze publicity crop in the archive was omitted in favor of its wider BBC version, and the wide crop of the official execution Dalek was omitted in favor of the larger portrait. Hash uniqueness alone would not establish that those were different photographs. The closest pair among the selected 256-bit difference hashes differed in 89 positions. That calculation is supporting evidence, not a substitute for the visual review.

The reference images and contact sheets remain in temporary analysis storage. They are not included in the repository, the PDF, the video, or the S3 deliverables. The CSV links to the exact originals so the evidence can be inspected without redistributing a third-party image collection.

## Overall shape and the circular base

The low fender and broad lower skirt carry much of the recognizable Dalek outline. Official bridge and classic-prop images show the wheels hidden behind the lower body, while the upper body becomes narrower toward the neck. The restored original also shows a small outward ledge below its lowest hemisphere row. These observations support a substantial perimeter bumper, concealed wheels and a clear taper. [D089, BBC bridge photograph](https://images.amcnetworks.com/bbcamerica.com/wp-content/uploads/2015/11/Mark-2-Daleks-1920x1080-1.jpg); [D050, original restoration front view](https://www.thepropgallery.com/media/wysiwyg/Dalek/TPG-original-dalek-restoration-50.png).

The photographed bronze props generally have faceted fenders and skirt panels. A perfectly circular base is therefore a deliberate adaptation. It should read as a round version of the same broad fender: a continuous dark lower band, a shallow ledge or bevel above it, and the decorated skirt rising inside that perimeter. A round cylinder with no transition to the body would lose this structure. [D057, bronze full-body view](https://www.dalek6388.co.uk/wp-content/uploads/2015/04/e733ccdb9836ca3f0a54b81de2a375c4.jpg).

For this robot, the circular base must be a real geometric boundary in the STL and plan view. Rounded corners on a rectangular base do not meet the requirement. Wheel openings should face downward and inward so they do not create four large exterior notches. The base must still provide independent motor saddles, a continuous structural floor and a clear load path to the stack fasteners. Decorative roundness does not establish strength; the base still needs the mechanical checks and physical commissioning specified elsewhere.

FACET-1 follows the user's request for actual flat panels. The skirt has twelve continuous planar faces and one linear taper, with four aligned hemisphere rows and narrow relief at the panel edges. It remains one complete print. The base and mating collars stay circular. This replaces the earlier curved skirt skin; the reference images themselves were not re-reviewed for this shape-only revision.

## Arms and concealed servos

The visible appendage joint is a ball or rounded pivot in a socket surround. An original restoration close-up shows a tube emerging from a ball inside a raised box; another view shows that the surrounding shoulder conceals the rest of the joint. The newer bronze design adds an ornate square plate around a dark circular pivot. [D013, original arm socket](https://www.thepropgallery.com/media/wysiwyg/Dalek/TPG-original-dalek-restoration-13.png); [D037, shoulder socket box](https://www.thepropgallery.com/media/wysiwyg/Dalek/TPG-original-dalek-restoration-37.png); [D080, official bronze front view](https://cms.doctorwho.tv//sites/default/files/2022-03/Doomsday%20-%20446x666.jpg).

All four arm servo cases, horns, fixing straps and wire loops should sit behind the shoulder skin. The finished exterior should expose only the round socket, the arm stem and the plunger or emitter. A servo-shaped cover on the end of an arm would hide its label but would still spoil the silhouette. The mechanism belongs inside the body. A socket surround integral to the shoulder and a moving spherical cover integral to an existing moving part can preserve the ten-STL limit.

Concealment must hold while the arms move. At every permitted yaw and pitch combination, the socket cover must overlap the shoulder opening. The visible joint must not reveal a servo through an open side or underneath the arm. It must also clear the shoulder, the adjacent arm and the central body panel. The arm stems should remain slim; placing an entire servo in an enlarged external arm shaft would not match the reference.

The proposed circular wiggle needs two coordinated internal axes for each arm. The appearance evidence does not establish the linkage, angle limit or torque. Those are engineering decisions. The operating animation should use the same pivot locations and limits as the CAD and firmware. Show internal mechanisms only during an explicitly marked assembly cutaway, then restore the complete shoulder surface before the exterior operating sequence.

## Detail priorities by component

The skirt should retain four ordered levels of hemispheres. Several construction images show that these are repeated shell details, while the bronze examples add dark rims around their roots. Shallow integral annular bezels offer much of that distinction without requiring separate printed rings. Use a consistent diameter within a row and align the columns through the stack joints. The golden dome of each hemisphere should stand out against its darker root and bronze body panel. [D004, skirt construction](https://www.thepropgallery.com/media/wysiwyg/Dalek/TPG-original-dalek-restoration-4.png); [D056, nearly finished bronze body](https://www.dalek6388.co.uk/wp-content/uploads/2015/04/large.gallery_377_18_29585.jpg.d85a4b9d555af3a31577b54337be76f3.jpg).

The shoulder benefits most from physical relief. Bronze references show thick rectangular slats with inset faces and round fastener heads. The front central panel is wider than the flanking slats. Side slats are longer where the shoulder offers more height. Their spacing should continue around the back, with only the necessary interruption for the confirmed TTGO T-Display opening. [D058, close slat and appendage photograph](https://www.dalek6388.co.uk/wp-content/uploads/2015/04/vlcsnap-57999-2.jpg); [D086, official side photograph](https://cms.doctorwho.tv//sites/default/files/2024-12/Website_Thumbnail_dalek-0b981cb219.jpg).

The neck should have three clearly projecting rings over a darker recessed drum. Thin vertical posts and horizontal grille bars give depth to the gaps. Open black space alone can make the neck appear hollow; an unbroken solid bronze drum loses the contrast. A printed dark grille or a dark finish behind integral bars can supply the visual effect. Keep enough service and ventilation access for the actual mechanism. [D015, restored neck structure](https://www.thepropgallery.com/media/wysiwyg/Dalek/TPG-original-dalek-restoration-14.png); [D039, neck ring and grille detail](https://www.thepropgallery.com/media/wysiwyg/Dalek/TPG-original-dalek-restoration-39.png).

The dome needs a smooth crown, a short lower lip and a raised eye cowl. Shallow panel grooves can run from the cowl region toward the sides. The eye should have a narrow stem, a group of pale concentric discs and a darker larger lens head. A small central recess and several concentric rings give the lens a convincing face. Keep the two dome lamps visibly separate and angled outward. Fine lamp ribbing should be robust enough to survive support removal and handling. [D063, bronze cowl close-up](https://www.dalek6388.co.uk/wp-content/uploads/2015/04/MT1.jpg); [D100, official lens and lamp close-up](https://cms.doctorwho.tv/sites/default/files/2026-02/dwtv-gallery-module-watermark-502a2980-18d60c7987.jpg).

The plunger should have a shallow cup, a defined rim and a smooth stem. The emitter should read as a central tube surrounded by an open cage of rods. Thin movie-prop rods cannot simply be scaled down without regard to print strength. Use fewer or thicker robust rods if needed, but preserve the open cage and muzzle silhouette. Do not add projectile or effect hardware to this decorative component. [D033, assembled cage](https://www.thepropgallery.com/media/wysiwyg/Dalek/TPG-original-dalek-restoration-33.png); [D034, muzzle close-up](https://www.thepropgallery.com/media/wysiwyg/Dalek/TPG-original-dalek-restoration-34.png).

These details have a clear priority. First preserve the body taper, fender, ringed neck and dome outline. Then add socket covers, hemispheres, slat relief and the eye cowl. Finally add shallow grooves, bolt-head cues and lamp ribs. Small detail should not create more STL files, obstruct a fastener, expose a servo, block airflow or reduce an essential wall thickness.

## Color and finish

Use a darker bronze body with warmer gold slats and hemisphere faces. Use near-black in the neck grille, socket balls, hemisphere bezels, plunger cup and lower bumper. Silver appendage stems and cage rods provide a separate material cue. Pale eyestalk discs and a dark lens ring keep the eye legible. These distinctions are directly visible in the official bronze auction side view. [D099, BBC Studios/Propstore side photograph](https://cms.doctorwho.tv/sites/default/files/2026-02/dwtv-gallery-module-watermark-5w9a6592-560d367d1e.jpg).

Use restrained shading in grooves and around bolt heads. Avoid large artificial damage holes or exposed cables. Different studio lighting can make the same bronze prop appear yellow, brown or purple, so the photographs do not justify a single measured paint color. Select actual paints from dry sample pieces under ordinary room light. A decorative blue eye color can suggest the reference without implying that the current head contains a powered lamp. Any functioning light requires a separately documented electrical implementation.

## Hidden adjustable friction head drive

The new TT motor and tyre must remain inside the neck and head envelope. Their external visibility is not required to communicate head motion. The prop reference confirms the broader appearance principle: its dome can be lifted separately, and its internal manual control disappears when assembled. [D068, interior dome photograph](https://www.dalek6388.co.uk/wp-content/uploads/2015/04/2.jpg).

The adjustable friction contact is a custom robot mechanism. A service drawing should show the motor, wheel, smooth driven surface, adjustment direction and locking fasteners. The assembled exterior should show none of those details. The adjustment needs a repeatable way to move the tyre into contact and then lock the setting without distorting the neck or forcing the bearing axis off-center. A separate bearing path must carry the dome's weight; tyre pressure should not become the only head support.

The reference review does not determine the correct tyre compression or slip torque. Those depend on the actual Adafruit tyre, printed surface finish, assembled head mass and bearing friction. Commission the mechanism at low power, increase contact only enough for reliable motion, and verify it in both directions. The assembly PDF and video should show how the builder reaches and locks the adjustment after the surrounding parts are fitted. A decorative slot that cannot be reached with a tool does not satisfy adjustability.

## Print and assembly implications

Keep each body level as one complete vertically stackable print. Integrate shallow detail into those existing pieces. Preserve a single strong base that fits wholly inside the H2D's usable length and width, including the selected brim and print orientation. A dimensioned plan view must show the new circular outside diameter and the actual wheel envelopes. Slicer checks should be run on the released STL hashes, not on a separate attractive preview model.

Use ordinary purchased fasteners and measured mounting clearances for the hidden hardware. The ten-file limit allows repeated instances of one universal moving part, but the inventory must state both the number of distinct STL designs and the number of physical prints. Avoid using invisible extra printed brackets to make the mechanism work. The video, CAD and assembly instructions must agree about which part carries each servo, head motor and bearing.

Finish recessed neck and socket areas before final stacking. Confirm motor access before installing electronics above the base. Align bump columns and shoulder details before tightening stack bolts. Route the arm leads entirely inside the shoulder, with slack for the permitted motion. Keep the original rear T-Display readable and its controls accessible. The display opening is a functional adaptation and should be a neat rear panel rather than a feature on the front chest.

## Visual acceptance for the revised deliverables

The exterior views should prove the intended result from the front, rear, both sides, above and a low angle. A plan view must show a circular base. The wheels should remain concealed in ordinary standing views. The rear view must show the original TTGO display. The shoulders must show only the intended socket surfaces and arm stems at neutral and at the extremes of the complete allowed motion.

An exploded or cutaway view should show both internal arm mechanisms and the head friction drive. A close view should show the adjustment fasteners and tool path. The completed operating view must restore all covers and shoulder walls. Its arm, head and chassis movements must come from the actual revised geometry. No external servo should disappear merely because a camera angle hides it.

Digital visual acceptance is separate from physical proof. The design remains subject to printed fit, supported load, head traction, motor current, heat, clearance and stop-response tests. The report provides a specific and traceable appearance standard; it does not report any of those tests as completed.

## Source register

1. The Prop Gallery, [Doctor Who — restoring an original Dalek](https://www.thepropgallery.com/dalek-restoration). Primary owner/restoration account; 50 individual restoration photographs selected. Publication date not stated on the page. The CSV links to each full image.
2. Dalek 63•88, [The New Series: Series One](https://www.dalek6388.co.uk/the-new-series-series-one/). Specialist archive; 23 individual bronze-era construction, exhibition and screen images selected. Photographer and copyright holder vary. Publication date not treated as a manufacturing date.
3. BBC Studios, [Daleks — Explore the Whoniverse](https://www.doctorwho.tv/characters/daleks). Official character and story image index; 13 selected images. Each exact original asset URL is recorded.
4. BBC America Editors, [Doctor Who Gallery: The Evolution of Dalek Design](https://www.bbcamerica.com/blogs/doctor-who-gallery-the-evolution-of-dalek-design--1015666), 2020-12-31. Ten selected photographs and screen stills; credited BBC.
5. The Prop Gallery, [Doctor Who — Original Dalek](https://www.thepropgallery.com/original-dalek). One selected close photograph of the restored original prop. Publication date not stated on the page.
6. BBC Studios / Propstore, [Everything available in the Doctor Who x Propstore auction](https://www.doctorwho.tv/news-and-features/here-is-every-item-available-in-the-doctor-who-auction), 2026 auction coverage. Three selected photographs of the bronze prop, including front, side and lens detail.

All source pages and individual image assets were accessed on 2026-09-12. Direct visible observations are distinguished from proposed design implications in the CSV. The reference count describes the reviewed inventory and does not imply permission to redistribute its copyrighted contents.
