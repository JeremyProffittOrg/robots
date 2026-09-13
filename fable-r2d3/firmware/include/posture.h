#pragma once
// Revision D posture estimate. The Romeo DFR0994 has no IMU (DFRobot wiki, product page and V1.1.0
// schematic list none), so pitch is state-based: a seated 0 deg receiver fixes the body upright, and
// with the centre foot on the floor three-foot post kinematics give pitch. Contradictions report unknown.
// Geometry: the provisional block in config.h, mirroring cad/kinematics.scad.
#include <stdint.h>
#include <math.h>
#include "config.h"
#include "stance.h"

namespace r2 {
constexpr float DEG = .01745329252f;

inline float postContactMm() {
 return (geometry::GUIDE_Z_MM - geometry::ANKLE_Z_MM) / cosf(geometry::GUIDE_ANGLE_DEG * DEG) - geometry::POST_ZERO_MM;
}
inline float postA(float s) { return geometry::GUIDE_Y_MM + (geometry::POST_ZERO_MM + s) * sinf(geometry::GUIDE_ANGLE_DEG * DEG); }
inline float postB(float s) { return (geometry::HIP_Z_MM - geometry::GUIDE_Z_MM) + (geometry::POST_ZERO_MM + s) * cosf(geometry::GUIDE_ANGLE_DEG * DEG); }

// Body pitch with all three feet on the floor; 0 at or below floor contact (body_pitch in kinematics.scad).
inline float threeFootPitchDegrees(float s) {
 if (s <= postContactMm()) return 0.0f;
 const float a = postA(s), b = postB(s);
 return (acosf((geometry::HIP_Z_MM - geometry::ANKLE_Z_MM) / sqrtf(a * a + b * b)) - atan2f(a, b)) / DEG;
}
// Forward distance from the side-foot contact line to the centre foot (center_y in kinematics.scad).
inline float centerFootOffsetMm(float s) {
 const float p = threeFootPitchDegrees(s) * DEG;
 return postA(s) * cosf(p) + postB(s) * sinf(p);
}

inline float steeringServoDegrees(float yawDegrees) {
 // Metal linkage: fixed guide point(-30,0), foot servo(-30,-60),12mm crank.
 const float a = yawDegrees * DEG;
 const float x = 30 - 30 * cosf(a), y = 60 + 30 * sinf(a), d = sqrtf(x * x + y * y);
 float cosine = (d * d + 144 - 3744) / (24 * d);
 cosine = fmaxf(-1, fminf(1, cosine));
 return (atan2f(y, x) + acosf(cosine)) * 57.29577951f - 180;
}

enum class PitchSource : uint8_t { UNKNOWN, SHOULDER_LOCK, THREE_FOOT_KINEMATICS };
struct PostureEstimate { bool valid; float pitchDeg; PitchSource source; };

inline const char *pitchSourceName(PitchSource s) {
 switch (s) {
  case PitchSource::SHOULDER_LOCK: return "shoulder lock geometry";
  case PitchSource::THREE_FOOT_KINEMATICS: return "three-foot post kinematics";
  default: return "unknown";
 }
}

inline PostureEstimate estimatePosture(const Stance &stance) {
 const PostureEstimate unknown = {false, 0.0f, PitchSource::UNKNOWN};
 if (stance.state == StanceState::FAULT || !stance.positionValid || !stance.lockValid) return unknown;
 const float s = stance.positionMm;
 const PostRegion r = stance.region(s);
 if (stance.lockEngaged) {
  if (r == PostRegion::LIFT || r == PostRegion::CONTACT) { const PostureEstimate locked = {true, 0.0f, PitchSource::SHOULDER_LOCK}; return locked; }
  if (r == PostRegion::TILT) return unknown; // contradictory: no receiver there
 } else if (r == PostRegion::LIFT) {
  return unknown; // contradictory: foot raised without a seated lock
 }
 const PostureEstimate floor = {true, threeFootPitchDegrees(s), PitchSource::THREE_FOOT_KINEMATICS};
 return floor;
}
}
