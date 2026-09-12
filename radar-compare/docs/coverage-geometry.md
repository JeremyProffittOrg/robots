# Coverage geometry: how many sensors, and where

Four numbers decide a perimeter ring, and all four are geometry rather than part choice: the beam
width at range, the ring count that actually closes, the depth of the near-field blind wedge, and
the mount height that puts a pet inside the beam. This chapter derives each one once. Other chapters
cite these results; the computed appendix carries the full tables.

One rule governs everything below. **Size a ring on the horizontal field of view, never on the
diagonal headline.** The horizontal figures used throughout are: VL53L5CX and VL53L8CX 45 x 45 deg,
VL53L7CX and VL53L7CH 60 x 60 deg, VL53L1X about 19.3 deg horizontal, VL53L9CX 55 x 42 deg. All
except the VL53L9CX are datasheet-verified in `data/sensors.csv`; the VL53L9CX figure is
vendor-page-verified only. Two diagonal figures are confirmed against a primary datasheet: the
VL53L5CX 63 deg, and the VL53L1X 27 deg, which the datasheet labels diagonal and which converts to
19.27 deg horizontal. A "65 deg" diagonal could not be confirmed against any ST primary source, so
it is not used here. Every ST field-of-view figure is a conditioned measurement, not a hard cone.
The VL53L5CX 45 deg is measured against an 88 percent white target at 1 m in darkness, 8x8
resolution, 14 percent sharpener, 15 Hz; against 17 percent grey in bright ambient the usable angle
is smaller, not equal. The VL53L1X 27 deg diagonal is measured with the target covering the full
field of view, long-distance mode, a 100 ms budget, no cover glass, in darkness. The remaining
horizontal figures carry no published measurement condition in the sources, so treat them the same
way.

## Beam footprint: what one sensor covers at range

The illuminated width at range `d` is

```
w = 2 * d * tan(FoV_h / 2)
```

| FoV_h (deg) | 1 ft (305 mm) | 3 ft (914 mm) | 5 ft (1524 mm) | 10 ft (3048 mm) |
|---|---|---|---|---|
| 19.3 (VL53L1X) | 104 mm | 311 mm | 518 mm | 1037 mm |
| 45 (VL53L5CX, VL53L8CX) | 253 mm | 757 mm | 1263 mm | 2525 mm |
| 60 (VL53L7CX) | 352 mm | 1056 mm | 1760 mm | 3520 mm |

The consequence is the whole single-zone-versus-array argument in one line: **a narrow sensor
resolves a thin obstacle, a wide one averages it away.** A single-zone part returns one distance for
the entire footprint. At 5 ft a 60 deg single-zone sensor is integrating a 1760 mm swath, so a chair
leg, a cat and the wall behind them all contribute to one number, and the strongest reflector wins.
A chair leg 35 mm wide subtends 1.32 deg at 5 ft. To report it as an object rather than as a weak
average, the sensor needs angular cells near that size. An 8x8 array at 45 deg horizontal has a zone
pitch of 45/8 = 5.625 deg, which is 90 mm at 3 ft and 150 mm at 5 ft: enough to detect a human leg
as a distinct return, not enough to classify it. Angular resolution comes from zones inside the
field of view, never from more sensors around the ring.

## Ring closure: n x FoV >= 360, full stop

Take `n` sensors evenly spaced, each with full horizontal field of view `FoV`, boresight spacing
`Delta = 360/n`, and angular overlap `Omega = FoV - Delta`. Sensor A's left edge and its neighbour
B's right edge diverge by exactly `-Omega`. When `Omega = 0` those two edges are **parallel**. Two
parallel rays never meet, so the wedge between them is blind to infinite range.

`N = 360/FoV` sets `Delta = FoV`, which is `Omega = 0` exactly. It is not a conservative answer, it
is the one value that must be avoided, and it is the formula every builder reaches for first. The
condition for a ring to close at any finite range is `FoV > 360/n`, that is

```
n * FoV > 360        and in practice        n = ceil( 360 / (FoV - overlap) )
```

where `overlap` is deliberate margin. Ten to twenty degrees is right for consumer time-of-flight
parts, for two reasons outside the geometry. A published field of view is the half-power contour,
not a hard edge, so `Omega = 0` mates the weakest part of one beam to the weakest part of the next.
Boresight error of about +/-2 deg per sensor from board placement and bracket tolerance is normal,
so two neighbours can sit 4 deg further apart than the CAD model says.

| FoV_h (deg) | overlap 0 | overlap 5 | overlap 10 | overlap 20 |
|---|---|---|---|---|
| 19.3 | 19 | 26 | 39 | impossible |
| 45 | 8 (open) | 9 | 11 | 15 |
| 55 | 7 | 8 | 8 | 11 |
| 60 | 6 | 7 | 8 | 9 |

The `overlap 0` column is the naive count, and at 45 deg it is a ring that never closes.

## The near-field blind wedge: the result most builders miss

Sensors sit on the rim, at `r = 175 mm` on a 350 mm platform, not at the centre. A ring that
satisfies `n * FoV > 360` is therefore still blind in a wedge near the body, because the two edge
rays that bound the gap start apart and need range to converge. With `a` the half field of view and
`s = pi/n` the half spacing, the wedge tip sits at

```
u = r * sin(a) / sin(a - s)          measured from the platform CENTRE
blind depth past the skin = u - r
```

This is the same result as `u = r * [cos(s) + sin(s) * cot(a - s)]`; the two collapse into each
other by the sine addition rule. It has one behaviour worth memorising: for small overlap,
`sin(a - s)` is nearly `(a - s)`, so **the blind depth is inversely proportional to the overlap.**
Halving the overlap doubles the blind wedge.

| ring | FoV_h (deg) | overlap (deg) | tip from centre | tip past skin |
|---|---|---|---|---|
| 8 x VL53L5CX | 45 | 0 | never closes | never closes |
| 10 x VL53L5CX | 45 | 9 | 853.6 mm | 678.6 mm |
| 12 x VL53L5CX | 45 | 15 | 513.1 mm | 338.1 mm |
| 16 x VL53L5CX | 45 | 22.5 | 343.3 mm | 168.3 mm |
| 8 x VL53L7CX | 60 | 15 | 670.4 mm | 495.4 mm |
| 12 x VL53L7CX | 60 | 30 | 338.1 mm | 163.1 mm |

Read the first row carefully, because it is the layout people build. Eight VL53L5CX at 45 deg
horizontal total exactly 360 deg. That looks closed on a coverage diagram drawn from the centre. It
is not: it has eight permanently open wedges, and a cat on a wedge bisector 400 mm from the robot is
invisible at every range. Ten sensors close the gap 678 mm out from the skin, twelve at 338 mm,
sixteen inside 168 mm.

Any ring with `n * FoV < 360` never closes at any range. That includes **every** ring of single-zone
VL53L1X sensors a builder would realistically fit: at 19.3 deg horizontal the first ring that closes
at all is n = 19, and even that puts the tip about 10.4 m away; bounding it within 350 mm takes
n = 38. The research lane first read this part's 27 deg as horizontal, which gave 14 sensors; it is
the diagonal, and the corrected answer is 38. Where tables in `research/coverage-geometry.md` are
indexed at 63 deg, that column is the VL53L5CX diagonal: read the 45 deg horizontal row instead. The
65 deg column in that file is unverified against any ST primary source and must not be used at all.

**The platform radius changes where the wedge closes, never whether it closes.** Closure depends
only on `a > s`, which contains no `r`. The radius is a linear scale factor on `u`: moving twelve
45 deg sensors from the 175 mm face radius to the 247.5 mm corner radius moves the tip from 513 mm
to 726 mm. Shrinking the robot does not fix an open ring.

## Vertical coverage: what the robot runs over

Horizontal geometry decides what the robot can see around itself. Vertical geometry decides what it
drives straight over. For a level boresight at mount height `h` with vertical half-angle `av`:

```
z_lo(d) = h - d * tan(av)       lowest height visible at range d
z_hi(d) = h + d * tan(av)       highest height visible at range d
d_floor = h / tan(av)           nearest range at which the beam strikes the floor
```

A standing cat occupies 0 to about 250 mm. It is visible only where `z_lo(d)` is below its head. The
cat columns below are the share of a 250 mm standing cat inside the beam, computed from the 250 mm
catalogue height in `data/geometry.json`; the floor-strike column is the research-lane figure.

| mount h | FoV_v 45 deg, floor strike | cat at 1 ft | cat at 3 ft | cat at 5 ft |
|---|---|---|---|---|
| 100 mm | 241 mm | about 90 percent | full | full |
| 200 mm | 483 mm | about 70 percent | full | full |
| 800 mm | 1931 mm | not visible | not visible | about 33 percent |

The headline is the bottom row. **A ring at 800 mm with a 45 deg vertical field of view cannot see a
standing cat at 1 ft or 3 ft at all** - the beam floor is still 674 mm up at 1 ft and 421 mm up at
3 ft. That is the obvious "mount them high where the wiring is easy" choice, and it is blind at
exactly the ranges where a collision happens. A ring at 100 to 200 mm sees everything from a lying
cat upward, at the price of a floor return from 241 mm or 483 mm outward: past that range the
software must reject a floor plane rather than trust free space. The sources differ on cat height,
200 mm in the research lane and 250 mm in `data/geometry.json`; prefer the 250 mm catalogue figure,
which the computed appendix uses, and note the conclusion holds at either height.

One level ring cannot both see a 250 mm pet at 300 mm and see a standing human's torso at 3 m. That
forces **two tiers**: a low tier near 200 mm for obstacles, pets and the floor plane, and a high
tier near 900 to 1100 mm for human torso detection. Height above the floor is the single most
reliable human-versus-pet discriminator available, and a single ring does not measure it.

## Square versus round, and the 495 mm diagonal

A 350 mm square platform has an inscribed radius of 175 mm at the face centres and a circumscribed
radius of 247.487 mm at the corners. **The diagonal across the corners is 494.975 mm, 41.4 percent
wider than the face**, and the corner protrudes 72.487 mm beyond the inscribed circle. A design that
reasons about "a 350 mm robot" and forgets the 495 mm diagonal clips door frames with its corners.

Face-centre mounting keeps the mount radius at 175 mm but points every blind bisector at a corner,
the part of the machine that sticks out furthest. Corner mounting pushes the radius to 247.487 mm,
scaling the whole wedge depth up by 41 percent, and aims the bisector at a face centre, which is
where the robot drives into things. Corner mounting is strictly worse at equal field of view. A
flush sensor on a flat face is also self-occluded to a 180 deg half-plane at best, while a flush
tangential sensor on a round body gets a clean 180 deg because a circle curves away from its own
tangent. **Make the platform round if the choice is still open.** If it must be square, mount on
face centres and protect the corners with a bumper, a compliant skirt, or a 45 deg chamfer.

## Cliff sensors: a separate, mandatory, cheap function

Down-canted cliff sensors are not part of the perimeter ring and must not be traded against it. A
sensor at height `h` canted `psi` below horizontal has look-ahead `L = h / tan(psi)`, flat-floor
range `R_f = h / sin(psi)`, and a drop of depth `D` adds `D / sin(psi)`. The contrast `D / h` is
independent of `psi`, so the cant only trades look-ahead against incidence angle. Below about 20 deg
the return on tile or polished wood goes specular and walks away from the receiver, which reads as a
phantom cliff (inferred from reflection geometry, not vendor-published).

At `h = 200 mm` and `psi = 30 deg` the look-ahead is 346 mm, the flat-floor range 400 mm, and a
180 mm stair riser moves the return to 760 mm, so a "greater than 500 mm means cliff" threshold has
wide margin both ways. Required look-ahead is stopping distance plus front overhang: at 0.5 m/s
that is 175 + 175 = 350 mm, met at `psi` of 30 deg or less. Step-**up** detection is not the mirror
case: a 20 mm threshold strip shortens the range by only 40 mm, inside sensor noise, so it needs a
level sensor at 40 to 60 mm or wheel-current and pitch sensing.

## The recess penalty: the field of view you buy is not the one you mount

Every field of view above assumes an unobstructed aperture. A sensor set back `z` mm behind the
skin, looking out through a hole of half-width `a`, is clipped to

```
FoV_eff = 2 * atan(a / z)
```

| setback z | window half-width 3 mm | 5 mm | 8 mm | 12 mm |
|---|---|---|---|---|
| 3 mm | 90.0 deg | 118.1 deg | 138.9 deg | 151.9 deg |
| 5 mm | 61.9 deg | 90.0 deg | 116.0 deg | 134.8 deg |
| 8 mm | 41.1 deg | 64.0 deg | 90.0 deg | 112.6 deg |
| 12 mm | 28.1 deg | 45.2 deg | 67.4 deg | 90.0 deg |
| 20 mm | 17.1 deg | 28.1 deg | 43.6 deg | 61.9 deg |

Read it against the ring counts above. A 60 deg VL53L7CX behind a 5 mm half-width window survives
8 mm of setback, at 64.0 deg, and is destroyed by 12 mm, at 45.2 deg - which moves the part from the
60 deg row of the ring table to the 45 deg row and adds sensors. The same 12 mm of setback clips a
120 deg module to 45.2 deg, turning a four-sensor design into a twelve-sensor problem. **Every
millimetre of recess must be budgeted before the ring is sized**, because the clip is silent: the
part still ranges correctly, it simply stops seeing the edges of its own stated cone.

## Design rules to carry away

- Size the ring on the **horizontal** field of view. The diagonal is a separately measured number
  and cannot be converted into coverage.
- `n * FoV >= 360` is necessary and not sufficient. Use `n = ceil(360 / (FoV - overlap))` with 10 to
  20 deg of overlap.
- The blind wedge is the binding constraint, not the ring count:
  `u = r * sin(a) / sin(a - s)`, and blind depth scales as 1/overlap.
- Carry these four: eight 45 deg sensors never close; ten close 678 mm out; twelve close 338 mm out;
  eight 60 deg sensors close 495 mm out.
- Platform radius sets **where** the wedge closes, never **whether**.
- Mount the obstacle and pet ring at about 200 mm with a vertical field of view of 45 deg or more.
  A ring at 800 mm is blind to a cat inside 5 ft.
- Two tiers are mandatory for human-versus-pet discrimination, because height above the floor is the
  discriminator.
- A square platform is 495 mm across the diagonal. Mount on face centres, protect the corners, or
  make the robot round.
- Fit dedicated cliff sensors at about 200 mm high, canted 25 to 35 deg, with a narrow vertical
  field of view. They are cheap and they are not optional.
- Budget the recess before sizing the ring. `FoV_eff = 2 * atan(a / z)`: 12 mm of setback behind a
  5 mm half-width window clips any wider part to 45.2 deg.
