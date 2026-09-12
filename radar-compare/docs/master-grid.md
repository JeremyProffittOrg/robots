# Master comparison grid

Every candidate part in one place, rated the same way. The tables in this chapter are generated
from `radar-compare/data/sensors.csv` by `radar-compare/scripts/grid.py`. No cell is typed by
hand, so no cell can flatter a part the catalogue does not support.

## How the capability level is decided

Each cell answers one question: at this distance, against this subject, what can this sensor
tell you? The level is computed from the sensor's own published numbers by a fixed rule. The
rules are printed here so that a reader who disagrees can argue with the rule rather than with
the cell.

{{LEVELS}}

The rules, in the order they are applied:

- **Out of range is level 0.** For every optical sensor the rated range is used as published,
  with its stated target reflectance. Where the catalogue carries a dark-target figure, that one
  is used instead, because a black sock and a dark-furred cat are the cases that matter.
- **Radar range is scaled by target size, because the physics says so.** The radar range equation
  makes range proportional to the fourth root of radar cross-section. An adult presents about
  0.70 m2 at these frequencies and a cat about 0.012 m2, so a module rated 25 m on a walking
  adult reaches about 9.0 m on a cat. That scaling is applied to every radar row.
- **A grid imager can only report a shape it can resolve.** The level is set by how many zones or
  pixels the subject spans across, computed from the centre zone, which is the narrowest. Under
  half a zone a ToF imager still returns a valid range but nothing else. Under about a third of a
  pixel a thermal array loses the subject in its own noise.
- **A thermal array and a PIR score 0 against furniture, at every range, forever.** A chair leg
  is at room temperature. There is no contrast to detect and no amount of processing creates one.
- **A presence radar scores 0 against a motionless inanimate object** unless the catalogue
  records that it reports static targets. Suppressing motionless returns is what clutter
  rejection is for; it is the same feature that makes the module immune to a curtain.
- **A 2D scanning lidar sees exactly one horizontal plane.** Anything whose top is below that
  plane or whose bottom is above it is invisible at every range. The catalogue leaves the scan
  plane height empty because it is a mounting decision, not a property of the part.
- **Level 4 needs evidence, not optimism.** A vendor radar module reaches level 4 only where its
  shipped firmware reports an actual class. Telling an adult from a cat on raw range and velocity
  is a micro-Doppler program someone has to write, and none of these modules exposes the data it
  would need.

## Specifications

{{SPEC_GRID}}

## Beam footprint width at each survey distance

Width is `2 d tan(FoV/2)` using the **horizontal** field of view. For a scanning lidar the cone
width is meaningless, so the figure given is the arc between adjacent samples, which is what
actually limits whether a thin object is hit by a beam at all.

{{WIDTH_GRID}}

## Against an adult human, 450 mm wide and 1700 mm tall

{{GRID:human}}

## Against a standing cat, 140 mm wide and 250 mm tall

This is the column that separates a specification sheet from a design. Most parts that look
capable against an adult collapse here, and they collapse for three different reasons: the cat is
too small to fill a zone, too small to return radar energy, or entirely beneath the beam.

{{GRID:cat}}

## Against a 30 mm chair leg

The thin, cold, static obstacle. Thermal and PIR score zero by physics. Presence radar scores
zero by design. What is left is the honest list of parts that will stop the robot hitting
furniture.

{{GRID:object}}
