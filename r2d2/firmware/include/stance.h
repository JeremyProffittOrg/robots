#pragma once
// Revision D stance change: THREE_FOOT <-> TWO_FOOT with a sensed spring-return shoulder lock.
// The GN817 plunger seats in one bushing for each stance, so the lock is engaged at BOTH
// endpoints and withdrawn only while the body tilts. Lock state always comes from the lock
// sensor, never from post position. Pure C++11, no Arduino headers: host tests run this code.
// Position is centre-post stroke in mm (cad/kinematics.scad s), 0 = fully retracted.
#include <stdint.h>
#include <math.h>

namespace r2 {

enum class StanceState : uint8_t { THREE_FOOT, DEPLOYING, RETRACTING, TWO_FOOT, HELD, FAULT };
// UNLOCKING: post stopped at a bushing while the release servo withdraws the pin.
// TILT: pin withdrawn, centre foot on the floor, post changes body pitch.
// LOCKING: release dropped, post creeps through the bushing position until the pin seats.
// LIFT/LOWER: pin seated in the two-foot bushing, body upright, post raises/lowers the foot.
enum class StancePhase : uint8_t { NONE, TILT, LOCKING, LIFT, LOWER, UNLOCKING };
enum class StanceTarget : int8_t { NONE = -1, TWO_FOOT = 2, THREE_FOOT = 3 };
enum class StanceFault : uint8_t {
 NONE, POWER, FEEDBACK, LOCK_SENSOR, TRAVEL_LIMIT, STALL, TRAVEL_TIMEOUT, LOCK_TIMEOUT, LOCK_DISAGREES, DRIFT, OVERTRAVEL, REVERSED_FEEDBACK
};

struct StanceLimits {
 float sensorMinMm, sensorMaxMm;        // readings outside this band are a feedback fault
 float twoFootMm, contactMm, threeFootMm;
 float stopToleranceMm;                 // a movement goal counts as reached inside this band
 float holdToleranceMm;                 // a stable stance faults if the post drifts further
 float lockWindowMm;                    // band at contact and at three-foot where either lock state is legal
 float seekMm;                          // tilt stops this far before a bushing, then LOCKING creeps
 float overshootMm;                     // LOCKING creeps this far past the nominal bushing position
 float overtravelMm;                    // beyond an endpoint by this much is a fault
 float progressMm; uint32_t progressMs; // stall detection
 uint32_t travelTimeoutMs, lockSettleMs, lockTimeoutMs, reverseDwellMs;
 uint32_t restPerRunMs;                 // cooldown ms per ms of travel (actuator duty cycle)
 int seekDutyPercent;
};

// Hardware abstraction: firmware binds Romeo pins; host tests bind a plant model.
class StanceHal {
 public:
 virtual ~StanceHal() {}
 virtual bool readPositionMm(float &mm) = 0;        // false: no valid reading
 virtual bool readLockEngaged(bool &engaged) = 0;   // false: sensor state invalid
 virtual bool readLockWithdrawn(bool &withdrawn) = 0; // independent full-withdrawal endpoint
 virtual bool travelLimitsClosed() = 0;             // both NC hardware travel limits closed
 virtual bool powerHealthy() = 0;                   // RUN power present and battery inside limits
 virtual bool heartbeatFresh(uint32_t now) = 0;     // an armed operator command is inside its lease
 virtual void driveActuator(int percent) = 0;       // -100 retract .. 0 stop .. +100 extend
 virtual void commandLockRelease(bool release) = 0; // true pulls the pin; false lets the spring seat it
};

inline const char *stanceName(StanceState s) {
 switch (s) {
  case StanceState::THREE_FOOT: return "THREE_FOOT";
  case StanceState::DEPLOYING: return "DEPLOYING";
  case StanceState::RETRACTING: return "RETRACTING";
  case StanceState::TWO_FOOT: return "TWO_FOOT";
  case StanceState::HELD: return "HELD";
  default: return "FAULT";
 }
}
inline const char *phaseName(StancePhase p) {
 switch (p) {
  case StancePhase::TILT: return "TILT";
  case StancePhase::LOCKING: return "LOCKING";
  case StancePhase::LIFT: return "LIFT";
  case StancePhase::LOWER: return "LOWER";
  case StancePhase::UNLOCKING: return "UNLOCKING";
  default: return "NONE";
 }
}
inline const char *faultName(StanceFault f) {
 switch (f) {
  case StanceFault::NONE: return "NONE";
  case StanceFault::POWER: return "POWER";
  case StanceFault::FEEDBACK: return "FEEDBACK";
  case StanceFault::LOCK_SENSOR: return "LOCK_SENSOR";
  case StanceFault::TRAVEL_LIMIT: return "TRAVEL_LIMIT";
  case StanceFault::STALL: return "STALL";
  case StanceFault::TRAVEL_TIMEOUT: return "TRAVEL_TIMEOUT";
  case StanceFault::LOCK_TIMEOUT: return "LOCK_TIMEOUT";
  case StanceFault::LOCK_DISAGREES: return "LOCK_DISAGREES";
  case StanceFault::DRIFT: return "DRIFT";
  case StanceFault::OVERTRAVEL: return "OVERTRAVEL";
  default: return "REVERSED_FEEDBACK";
 }
}

// LIFT: pin must be seated (foot raised). TILT: no bushing, pin cannot be seated.
// CONTACT and DEPLOYED: bushing positions, either state is legal.
enum class PostRegion : uint8_t { LIFT, CONTACT, TILT, DEPLOYED };

class Stance {
 public:
 explicit Stance(const StanceLimits &limits) : lim(limits) {}

 StanceState state = StanceState::HELD;
 StancePhase phase = StancePhase::NONE;
 StanceFault fault = StanceFault::NONE;
 StanceTarget target = StanceTarget::NONE;
 const char *reason = "starting";
 int actuator = 0;
 bool release = false;
 // Last sample, published to the status API.
 bool positionValid = false, lockValid = false, lockEngaged = false, lockWithdrawn = false, limitsClosed = false, power = false, heartbeat = false;
 float positionMm = NAN;

 const StanceLimits &limits() const { return lim; }
 bool consistentLimits() const {
  const float t = lim.stopToleranceMm;
  return lim.sensorMinMm < lim.twoFootMm - lim.overtravelMm && lim.threeFootMm + lim.overtravelMm < lim.sensorMaxMm &&
   lim.seekMm + t <= lim.lockWindowMm && lim.overshootMm + t < lim.lockWindowMm && lim.overshootMm + t < lim.overtravelMm &&
   lim.lockWindowMm <= lim.holdToleranceMm &&
   lim.twoFootMm + lim.holdToleranceMm < lim.contactMm - lim.lockWindowMm &&
   lim.contactMm + lim.lockWindowMm < lim.threeFootMm - lim.lockWindowMm &&
   lim.progressMm > 0 && lim.progressMs > 0 && lim.travelTimeoutMs > lim.progressMs && lim.lockTimeoutMs > 0 &&
   lim.seekDutyPercent > 0 && lim.seekDutyPercent <= 100;
 }
 bool started() const { return begun; }
 bool driveAllowed() const { return state == StanceState::THREE_FOOT; }  // stationary two-foot standing only
 bool headAllowed() const { return state == StanceState::THREE_FOOT || state == StanceState::TWO_FOOT; }
 bool transitioning() const { return state == StanceState::DEPLOYING || state == StanceState::RETRACTING; }

 PostRegion region(float mm) const {
  if (mm < lim.contactMm - lim.lockWindowMm) return PostRegion::LIFT;
  if (mm <= lim.contactMm + lim.lockWindowMm) return PostRegion::CONTACT;
  if (mm < lim.threeFootMm - lim.lockWindowMm) return PostRegion::TILT;
  return PostRegion::DEPLOYED;
 }

 // nullptr when a request for this stance would start now; otherwise the interlock that forbids it.
 const char *blocked(StanceTarget wanted, uint32_t now, bool driveIdle) const {
  if (!begun) return "starting";
  if (wanted == StanceTarget::NONE) return "no stance selected";
  if (state == StanceState::FAULT) return "fault latched; clear it first";
  if (transitioning()) return target == wanted ? "stance change in progress" : "release the active stance control first";
  if (wanted == StanceTarget::TWO_FOOT && state == StanceState::TWO_FOOT) return "already standing on two feet";
  if (wanted == StanceTarget::THREE_FOOT && state == StanceState::THREE_FOOT) return "already on three feet";
  if (!power) return "RUN power off or battery outside limits";
  if (!heartbeat) return "arm control first";
  if (!driveIdle) return "stop wheels and head and centre steering first";
  if (!released) return "release the stance control, then press again";
  if (uint32_t(now - restStart) < restMs) return "actuator cooling down";
  return nullptr;
 }

 void tick(uint32_t now, StanceHal &hal, StanceTarget request, bool driveIdle) {
  sample(now, hal);
  if (request == StanceTarget::NONE) released = true;
  if (!begun) {
   begun = true;
   derive(now);
   apply(hal);
   return;
  }
  if (state != StanceState::FAULT && checkSensors(now)) {
   if (transitioning()) {
    if (!power) fail(now, StanceFault::POWER, "RUN power or battery lost during stance change; actuator stopped");
    else if (!heartbeat) hold(now, "command heartbeat lost; actuator stopped and stance held");
    else if (request == StanceTarget::NONE) hold(now, "stance control released before completion; held");
    else if (request != target) hold(now, "opposite stance requested mid-change; held");
    else if (!driveIdle) hold(now, "drive, head or steering command during stance change; held");
    else step(now);
   } else if ((state == StanceState::HELD || checkStable(now)) && request != StanceTarget::NONE &&
              !blocked(request, now, driveIdle)) {
    begin(now, request);
   }
  }
  apply(hal);
 }

 // Operator acknowledgement. Succeeds only if fresh sensors describe a consistent mechanism.
 bool clearFault(uint32_t now) {
  if (state != StanceState::FAULT) return false;
  derive(now);
  if (state == StanceState::FAULT) return false;
  released = false;
  return true;
 }

 private:
 StanceLimits lim;
 bool begun = false, released = true, seekReached = false;
 uint32_t phaseStart = 0, moveStart = 0, progressAt = 0, lastStopAt = 0, restStart = 0, restMs = 0, runMs = 0, seekReachedAt = 0;
 float progressPos = 0, phasePos = 0;
 int lastDirection = 0;

 void sample(uint32_t now, StanceHal &hal) {
  float mm = NAN;
  positionValid = hal.readPositionMm(mm) && isfinite(mm) && mm >= lim.sensorMinMm && mm <= lim.sensorMaxMm;
  positionMm = positionValid ? mm : NAN;
  bool engaged = false;
  lockValid = hal.readLockEngaged(engaged);
  lockEngaged = lockValid && engaged;
  bool withdrawn = false;
  lockValid = hal.readLockWithdrawn(withdrawn) && lockValid;
  lockWithdrawn = lockValid && withdrawn;
  if (lockEngaged && lockWithdrawn) lockValid = false;
  limitsClosed = hal.travelLimitsClosed();
  power = hal.powerHealthy();
  heartbeat = hal.heartbeatFresh(now);
 }

 void apply(StanceHal &hal) {
  hal.driveActuator(actuator);
  hal.commandLockRelease(release);
 }

 void stopActuator(uint32_t now) {
  if (actuator != 0) {
   runMs += uint32_t(now - moveStart);
   lastStopAt = now;
  }
  actuator = 0;
 }

 // Cooldown only ever extends; a later event never shortens remaining rest.
 void startRest(uint32_t now) {
  uint32_t elapsed = uint32_t(now - restStart);
  uint32_t remaining = elapsed < restMs ? restMs - elapsed : 0;
  uint32_t wanted = runMs * lim.restPerRunMs;
  restStart = now;
  restMs = wanted > remaining ? wanted : remaining;
  runMs = 0;
 }

 void fail(uint32_t now, StanceFault why, const char *text) {
  stopActuator(now);
  startRest(now);
  state = StanceState::FAULT; phase = StancePhase::NONE; fault = why; reason = text; target = StanceTarget::NONE;
  released = false;
  // The lock command is left unchanged: a fault never moves the lock.
 }

 void hold(uint32_t now, const char *text) {
  stopActuator(now);
  startRest(now);
  state = StanceState::HELD; phase = StancePhase::NONE; reason = text; target = StanceTarget::NONE;
  released = false;
 }

 bool checkSensors(uint32_t now) {
  if (!positionValid) { fail(now, StanceFault::FEEDBACK, "centre-post position feedback invalid"); return false; }
  if (!lockValid) { fail(now, StanceFault::LOCK_SENSOR, "shoulder lock sensor invalid"); return false; }
  if (!limitsClosed) { fail(now, StanceFault::TRAVEL_LIMIT, "hardware travel limit open"); return false; }
  if (positionMm < lim.twoFootMm - lim.overtravelMm || positionMm > lim.threeFootMm + lim.overtravelMm) {
   fail(now, StanceFault::OVERTRAVEL, "centre post beyond its stance endpoints"); return false;
  }
  PostRegion r = region(positionMm);
  if (r == PostRegion::LIFT && !lockEngaged) {
   fail(now, StanceFault::LOCK_DISAGREES, "centre foot raised but shoulder lock sensor not engaged"); return false;
  }
  if (r == PostRegion::TILT && lockEngaged) {
   fail(now, StanceFault::LOCK_DISAGREES, "lock sensor engaged where no lock bushing exists"); return false;
  }
  return true;
 }

 bool checkStable(uint32_t now) {
  bool two = state == StanceState::TWO_FOOT;
  float end = two ? lim.twoFootMm : lim.threeFootMm;
  if (fabsf(positionMm - end) > lim.holdToleranceMm) {
   fail(now, StanceFault::DRIFT, two ? "centre post left the two-foot endpoint" : "centre post left the three-foot endpoint");
   return false;
  }
  if (!lockEngaged) {
   fail(now, StanceFault::LOCK_DISAGREES, two ? "two-foot endpoint but lock sensor not engaged" : "three-foot endpoint but lock sensor not engaged");
   return false;
  }
  return true;
 }

 void derive(uint32_t now) {
  state = StanceState::HELD; fault = StanceFault::NONE; phase = StancePhase::NONE; target = StanceTarget::NONE;
  actuator = 0;
  if (!checkSensors(now)) return;
  release = false; // spring-return lock: recovery never holds the pin out
  if (lockEngaged && fabsf(positionMm - lim.twoFootMm) <= lim.holdToleranceMm) {
   state = StanceState::TWO_FOOT; reason = "standing on two feet; shoulder lock engaged";
  } else if (lockEngaged && fabsf(positionMm - lim.threeFootMm) <= lim.holdToleranceMm) {
   state = StanceState::THREE_FOOT; reason = "on three feet; shoulder lock engaged; ready to drive";
  } else {
   reason = "between stances; hold a stance control to finish";
  }
 }

 void enterPhase(uint32_t now, StancePhase next) {
  phase = next; phaseStart = now; phasePos = positionMm;
  progressAt = now; progressPos = positionMm;
  seekReached = false;
  release = next == StancePhase::UNLOCKING || next == StancePhase::TILT;

 }

 void begin(uint32_t now, StanceTarget wanted) {
  target = wanted;
  fault = StanceFault::NONE;
  runMs = 0;
  PostRegion r = region(positionMm);
  StancePhase first;
  if (wanted == StanceTarget::TWO_FOOT) {
   state = StanceState::RETRACTING; reason = "retracting to two-foot stance";
   if (r == PostRegion::LIFT) first = StancePhase::LIFT;
   else if (r == PostRegion::CONTACT) first = lockEngaged ? StancePhase::LIFT : (positionMm <= lim.contactMm + lim.seekMm ? StancePhase::LOCKING : StancePhase::TILT);
   else if (r == PostRegion::TILT) first = StancePhase::TILT;
   else first = lockEngaged ? StancePhase::UNLOCKING : StancePhase::TILT;
  } else {
   state = StanceState::DEPLOYING; reason = "deploying centre foot to three-foot stance";
   if (r == PostRegion::LIFT) first = StancePhase::LOWER;
   else if (r == PostRegion::CONTACT) first = lockEngaged ? (fabsf(positionMm - lim.contactMm) <= lim.stopToleranceMm ? StancePhase::UNLOCKING : StancePhase::LOWER) : StancePhase::TILT;
   else if (r == PostRegion::TILT) first = StancePhase::TILT;
   else if (lockEngaged) { complete(now, StanceState::THREE_FOOT); return; }
   else first = positionMm >= lim.threeFootMm - lim.seekMm ? StancePhase::LOCKING : StancePhase::TILT;
  }
  if (first == StancePhase::TILT && !lockWithdrawn) first = StancePhase::UNLOCKING;
  enterPhase(now, first);
 }

 void complete(uint32_t now, StanceState done) {
  stopActuator(now);
  startRest(now);
  state = done; phase = StancePhase::NONE; target = StanceTarget::NONE;
  reason = done == StanceState::TWO_FOOT ? "standing on two feet; shoulder lock engaged" : "on three feet; shoulder lock engaged; ready to drive";
  release = false;
  released = false;
 }

 // Drive toward goal at duty percent. Returns true once the goal band is reached with the actuator stopped.
 bool move(uint32_t now, float goal, int duty) {
  float error = goal - positionMm;
  if (fabsf(error) <= lim.stopToleranceMm) { stopActuator(now); return true; }
  int direction = error > 0 ? 1 : -1;
  if (uint32_t(now - phaseStart) >= lim.travelTimeoutMs) {
   fail(now, StanceFault::TRAVEL_TIMEOUT, "centre-post travel timeout"); return false;
  }
  int current = actuator > 0 ? 1 : actuator < 0 ? -1 : 0;
  if (current != direction) {
   if (current != 0) stopActuator(now);
   progressAt = now; progressPos = positionMm;
   if (lastDirection != 0 && lastDirection != direction && uint32_t(now - lastStopAt) < lim.reverseDwellMs) return false;
   actuator = direction * duty; lastDirection = direction; moveStart = now;
   return false;
  }
  actuator = direction * duty;
  float moved = (positionMm - progressPos) * direction;
  if (moved <= -lim.progressMm) {
   fail(now, StanceFault::REVERSED_FEEDBACK, "centre post moving opposite to its drive"); return false;
  }
  if (moved >= lim.progressMm) { progressAt = now; progressPos = positionMm; }
  else if (uint32_t(now - progressAt) >= lim.progressMs) {
   fail(now, StanceFault::STALL, "centre-post actuator stalled"); return false;
  }
  return false;
 }

 bool stoppedDrift(uint32_t now, const char *text) {
  stopActuator(now);
  if (fabsf(positionMm - phasePos) > lim.stopToleranceMm + lim.progressMm) { fail(now, StanceFault::DRIFT, text); return true; }
  return false;
 }

 void step(uint32_t now) {
  bool retracting = state == StanceState::RETRACTING;
  switch (phase) {
   case StancePhase::UNLOCKING:
    if (stoppedDrift(now, "centre post moved while the lock was releasing")) return;
    if (!lockEngaged && lockWithdrawn) enterPhase(now, StancePhase::TILT);
    else if (uint32_t(now - phaseStart) >= lim.lockTimeoutMs)
     fail(now, StanceFault::LOCK_TIMEOUT, "lock did not reach its independently sensed withdrawn endpoint");
    return;
   case StancePhase::TILT:
    if (lockEngaged) { fail(now, StanceFault::LOCK_DISAGREES, "lock sensor engaged mid-tilt, away from both receivers"); return; }
    if (!lockWithdrawn) { fail(now, StanceFault::LOCK_DISAGREES, "lock withdrawal lost during tilt"); return; }
    if (move(now, retracting ? lim.contactMm + lim.seekMm : lim.threeFootMm - lim.seekMm, 100)) enterPhase(now, StancePhase::LOCKING);
    return;
   case StancePhase::LOCKING:
    if (lockEngaged) {
     stopActuator(now);
     if (retracting) enterPhase(now, StancePhase::LIFT);
     else complete(now, StanceState::THREE_FOOT);
     return;
    }
    if (uint32_t(now - phaseStart) < lim.lockSettleMs) {
     if (stoppedDrift(now, "centre post moved while the lock pin was dropping")) return;
     return;
    }
    if (!seekReached) {
     float goal = retracting ? lim.contactMm - lim.overshootMm : lim.threeFootMm + lim.overshootMm;
     if (move(now, goal, lim.seekDutyPercent)) { seekReached = true; seekReachedAt = now; }
     return;
    }
    stopActuator(now);
    if (uint32_t(now - seekReachedAt) >= lim.lockTimeoutMs)
     fail(now, StanceFault::LOCK_TIMEOUT, "post passed the lock position but lock sensor not engaged");
    return;
   case StancePhase::LIFT:
   case StancePhase::LOWER:
    if (!lockEngaged) { fail(now, StanceFault::LOCK_DISAGREES, "shoulder lock released while it must carry the body"); return; }
    if (retracting) {
     if (phase == StancePhase::LOWER) enterPhase(now, StancePhase::LIFT);
     else if (move(now, lim.twoFootMm, 100)) complete(now, StanceState::TWO_FOOT);
    } else {
     if (phase == StancePhase::LIFT) enterPhase(now, StancePhase::LOWER);
     else if (move(now, lim.contactMm, 100)) enterPhase(now, StancePhase::UNLOCKING);
    }
    return;
   default:
    hold(now, "no stance phase; held");
    return;
  }
 }
};

}
