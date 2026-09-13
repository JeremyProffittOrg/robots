// Host tests for the revision D stance state machine, interlocks, sensor conditioning and posture estimate.
// Build: g++ -std=c++11 -Wall -Wextra -Werror -I firmware/include firmware/test/stance_test.cpp
#include "config.h"
#include "control.h"
#include "inputs.h"
#include "posture.h"
#include "stance.h"
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <initializer_list>

using namespace r2;

static int checks = 0;
#define CHECK(cond) do { ++checks; if (!(cond)) { std::printf("FAIL %s:%d: %s\n", __FILE__, __LINE__, #cond); std::exit(1); } } while (0)

static const StanceLimits &L = calibration::STANCE;
static const float BUSHING3 = L.threeFootMm + 0.2f; // real bushing slightly off nominal: exercises the seek

// Physical plant: non-backdrivable lead-screw post and a spring-return pin with two bushings.
struct Plant : StanceHal {
 float mm = BUSHING3;
 int seated = 3; // 0 none, 2 two-foot bushing, 3 three-foot bushing
 bool release = false;
 int drive = 0;
 float speed = calibration::POST_NO_LOAD_SPEED_MM_S / 1000.0f; // mm per ms at 100%
 bool power = true, heartbeat = true, positionOk = true, lockOk = true, limitsClosed = true;
 bool stalled = false, jammed = false, stuckSeated = false, reversedFeedback = false, sensorSaysEngaged = false, sensorSaysReleased = false;
 uint32_t seatDelay = 60, pullDelay = 250, changeAt = 0; bool pending = false;
 bool unsafe = false;     // pin out while the centre foot is raised
 bool movedPinned = false; // post driven while a seated pin blocked it
 bool readPositionMm(float &out) override { out = mm; return positionOk; }
 bool readLockEngaged(bool &out) override { out = sensorSaysEngaged ? true : sensorSaysReleased ? false : seated != 0; return lockOk; }
 bool travelLimitsClosed() override { return limitsClosed; }
 bool powerHealthy() override { return power; }
 bool heartbeatFresh(uint32_t) override { return heartbeat; }
 void driveActuator(int percent) override { drive = percent; }
 void commandLockRelease(bool r) override { release = r; }
 int aligned() const {
  if (mm <= L.contactMm + 0.3f) return 2;
  if (std::fabs(mm - BUSHING3) <= 0.3f) return 3;
  return 0;
 }
 void physics(uint32_t now, uint32_t dt) {
  if (drive && power && !stalled) {
   float d = (drive / 100.0f) * speed * dt * (reversedFeedback ? -1.0f : 1.0f);
   float next = mm + d;
   bool blocked = (seated == 2 && next > L.contactMm + 0.3f) || (seated == 3 && std::fabs(next - BUSHING3) > 0.3f);
   if (blocked) movedPinned = true; else mm = next;
  }
  int want = seated;
  if (stuckSeated) want = seated;
  else if (release) want = 0;
  else if (seated == 0 && !jammed) want = aligned();
  if (want != seated) {
   if (!pending) { pending = true; changeAt = now + (want ? seatDelay : pullDelay); }
   else if (int32_t(now - changeAt) >= 0) { seated = want; pending = false; }
  } else pending = false;
  if (mm < L.contactMm - L.lockWindowMm && seated == 0) unsafe = true;
 }
};

struct Rig {
 Stance stance{L};
 Plant plant;
 uint32_t t = 1000;
 StanceTarget request = StanceTarget::NONE;
 bool idle = true;
 bool driveAllowedWhileNotParked = false, actuatorDuringUnlock = false, actuatorDuringSettle = false;
 void run(uint32_t ms) {
  for (uint32_t i = 0; i < ms; i += 10) {
   plant.physics(t, 10);
   t += 10;
   stance.tick(t, plant, request, idle);
   if (stance.state != StanceState::THREE_FOOT && stance.driveAllowed()) driveAllowedWhileNotParked = true;
   if (stance.phase == StancePhase::UNLOCKING && plant.drive != 0) actuatorDuringUnlock = true;
  }
 }
 bool runUntil(StanceState s, uint32_t limit) {
  for (uint32_t i = 0; i < limit && stance.state != s; i += 10) run(10);
  return stance.state == s;
 }
 bool runUntilPhase(StancePhase p, uint32_t limit) {
  for (uint32_t i = 0; i < limit && stance.phase != p; i += 10) run(10);
  return stance.phase == p;
 }
 void release() { request = StanceTarget::NONE; run(20); }
 void cool() { request = StanceTarget::NONE; run(400000); }
};

static void threeFoot(Rig &r) { r.plant.mm = BUSHING3; r.plant.seated = 3; r.run(10); }
static void twoFoot(Rig &r) { r.plant.mm = L.twoFootMm; r.plant.seated = 2; r.run(10); }
static bool contains(const char *text, const char *part) { return text && std::strstr(text, part); }

static void sensorConditioning() {
 const PotCalibration &c = calibration::POT; float mm = -99;
 CHECK(!potPosition(0.0f, c, mm)); CHECK(!potPosition(3.0f, c, mm));  // open wiper or ref+
 CHECK(!potPosition(3250.0f, c, mm));                                 // open ref-
 CHECK(!potPosition(NAN, c, mm));
 CHECK(potPosition(1375.0f, c, mm) && std::fabs(mm - 50.0f) < 0.01f);
 CHECK(potPosition(55.0f, c, mm) && std::fabs(mm - 2.0f) < 0.01f);
 // Pot tolerance +/-50% with the 2.2k top resistor keeps full stroke inside the valid window.
 for (float kohm : {5.5f, 11.0f, 16.5f}) { float full = 3300.0f * kohm / (kohm + 2.2f); CHECK(full < c.maxValidMv && full > 2000.0f); }
 ContactPair p(calibration::LOCK_LEGAL_MS, calibration::LOCK_ILLEGAL_MS);
 p.update(0, true, false); CHECK(!p.settled());
 p.update(20, true, false); CHECK(!p.settled());
 p.update(30, true, false); CHECK(p.settled() && p.valid && p.engaged);
 p.update(40, false, false); p.update(140, false, false); CHECK(p.valid && p.engaged);       // changeover gap keeps last legal state
 p.update(150, false, true); p.update(185, false, true); CHECK(p.valid && !p.engaged);       // released after debounce
 p.update(200, false, false); p.update(360, false, false); CHECK(!p.valid);                  // broken COM or wire
 p.update(370, true, true); p.update(530, true, true); CHECK(!p.valid);                      // short
 p.update(540, true, false); p.update(575, true, false); CHECK(p.valid && p.engaged);
}

static void limitsAndBoot() {
 CHECK(Stance(L).consistentLimits());
 CHECK(std::fabs(L.contactMm - postContactMm()) < 0.01f);
 // The release drops only after the pin has swept a full bore diameter plus margin off its receiver.
 const float arcPerDeg = geometry::LOCK_RADIUS_MM * DEG;
 CHECK(threeFootPitchDegrees(L.releaseDropDeployMm) * arcPerDeg >= geometry::LOCK_CLEAR_ARC_MM);
 CHECK((threeFootPitchDegrees(L.threeFootMm) - threeFootPitchDegrees(L.releaseDropRetractMm)) * arcPerDeg >= geometry::LOCK_CLEAR_ARC_MM);
 { Rig a; threeFoot(a); CHECK(a.stance.state == StanceState::THREE_FOOT); CHECK(a.stance.driveAllowed()); CHECK(!a.plant.release); }
 { Rig b; twoFoot(b); CHECK(b.stance.state == StanceState::TWO_FOOT); CHECK(!b.stance.driveAllowed()); CHECK(b.stance.headAllowed()); }
 { Rig c; c.plant.mm = 70; c.plant.seated = 0; c.run(10);
   CHECK(c.stance.state == StanceState::HELD); CHECK(!c.stance.driveAllowed()); CHECK(!c.stance.headAllowed()); }
 { Rig d; d.plant.mm = L.threeFootMm; d.plant.seated = 0; d.run(10); CHECK(d.stance.state == StanceState::HELD); } // endpoint without seated pin is not a stance
 { Rig e; e.plant.mm = 20; e.plant.seated = 0; e.run(10); CHECK(e.stance.fault == StanceFault::LOCK_DISAGREES); }
 { Rig f; f.plant.mm = 70; f.plant.sensorSaysEngaged = true; f.plant.seated = 0; f.run(10); CHECK(f.stance.fault == StanceFault::LOCK_DISAGREES); }
 { Rig g; g.plant.positionOk = false; g.run(10); CHECK(g.stance.fault == StanceFault::FEEDBACK); }
 { Rig h; h.plant.mm = 101.5f; h.run(10); CHECK(h.stance.fault == StanceFault::FEEDBACK); }
 { Rig k; k.plant.mm = 99.8f; k.run(10); CHECK(k.stance.fault == StanceFault::OVERTRAVEL); }
 { Rig m; m.plant.limitsClosed = false; m.run(10); CHECK(m.stance.fault == StanceFault::TRAVEL_LIMIT); }
 { Rig n; n.plant.lockOk = false; n.run(10); CHECK(n.stance.fault == StanceFault::LOCK_SENSOR); }
}

static void normalRetractThenDeploy() {
 Rig r; threeFoot(r);
 r.request = StanceTarget::TWO_FOOT; r.run(10);
 CHECK(r.stance.state == StanceState::RETRACTING); CHECK(r.stance.phase == StancePhase::UNLOCKING);
 CHECK(r.plant.release); CHECK(r.plant.drive == 0); CHECK(!r.stance.driveAllowed()); CHECK(!r.stance.headAllowed());
 CHECK(r.runUntilPhase(StancePhase::TILT, 1000)); CHECK(r.plant.seated == 0);
 r.run(20); CHECK(r.plant.drive == -100); CHECK(r.plant.release);
 while (r.stance.phase == StancePhase::TILT && r.plant.mm > L.releaseDropRetractMm + 1.0f) { r.run(10); CHECK(r.plant.release); }
 r.run(600); CHECK(r.stance.phase == StancePhase::TILT); CHECK(!r.plant.release); CHECK(r.plant.seated == 0); // pin rides the ring face
 CHECK(r.runUntilPhase(StancePhase::LOCKING, 30000));
 CHECK(!r.plant.release); CHECK(r.plant.drive == 0);
 r.run(L.lockSettleMs - 20); CHECK(r.plant.drive == 0); // pin drops before the creep starts
 r.run(60); CHECK(r.plant.drive == -L.seekDutyPercent);
 CHECK(r.runUntilPhase(StancePhase::LIFT, 5000)); CHECK(r.plant.seated == 2);
 CHECK(r.plant.mm >= L.contactMm - L.overshootMm - L.stopToleranceMm);
 CHECK(r.runUntil(StanceState::TWO_FOOT, 30000));
 CHECK(r.plant.drive == 0); CHECK(r.plant.seated == 2); CHECK(!r.plant.release);
 CHECK(!r.plant.unsafe); CHECK(!r.plant.movedPinned); CHECK(!r.driveAllowedWhileNotParked); CHECK(!r.actuatorDuringUnlock);
 CHECK(!r.stance.driveAllowed()); CHECK(r.stance.headAllowed());
 PostureEstimate p = estimatePosture(r.stance);
 CHECK(p.valid && p.pitchDeg == 0.0f && p.source == PitchSource::SHOULDER_LOCK);
 r.run(2000); CHECK(r.stance.state == StanceState::TWO_FOOT); CHECK(r.plant.drive == 0); // holding after arrival does nothing
 r.release();
 CHECK(contains(r.stance.blocked(StanceTarget::THREE_FOOT, r.t, true), "cooling"));
 r.request = StanceTarget::THREE_FOOT; r.run(50); CHECK(r.stance.state == StanceState::TWO_FOOT);
 r.cool();
 CHECK(r.stance.blocked(StanceTarget::THREE_FOOT, r.t, true) == nullptr);
 r.request = StanceTarget::THREE_FOOT; r.run(20);
 CHECK(r.stance.state == StanceState::DEPLOYING); CHECK(r.stance.phase == StancePhase::LOWER);
 CHECK(!r.plant.release); CHECK(r.plant.drive == 100);
 CHECK(r.runUntilPhase(StancePhase::UNLOCKING, 20000)); CHECK(r.plant.drive == 0); CHECK(r.plant.release);
 CHECK(r.plant.seated == 2); // still seated until the sensor reports it out
 CHECK(r.runUntilPhase(StancePhase::TILT, 1000)); CHECK(r.plant.seated == 0);
 r.run(20); CHECK(r.plant.release);
 while (r.stance.phase == StancePhase::TILT && r.plant.mm < L.releaseDropDeployMm) r.run(10);
 r.run(20); CHECK(r.stance.phase == StancePhase::TILT); CHECK(!r.plant.release); CHECK(r.plant.seated == 0);
 CHECK(r.runUntilPhase(StancePhase::LOCKING, 30000)); CHECK(!r.plant.release);
 CHECK(r.runUntil(StanceState::THREE_FOOT, 10000));
 CHECK(r.plant.seated == 3); CHECK(r.stance.driveAllowed()); CHECK(!r.plant.unsafe); CHECK(!r.plant.movedPinned);
 CHECK(!r.driveAllowedWhileNotParked); CHECK(!r.actuatorDuringUnlock);
 PostureEstimate q = estimatePosture(r.stance);
 CHECK(q.valid && q.source == PitchSource::THREE_FOOT_KINEMATICS && std::fabs(q.pitchDeg - threeFootPitchDegrees(r.plant.mm)) < 0.001f);
}

static void commandLossMidTransition() {
 { // Heartbeat lost while the seated lock carries the raised foot.
  Rig r; threeFoot(r); r.request = StanceTarget::TWO_FOOT;
  CHECK(r.runUntilPhase(StancePhase::LIFT, 40000)); r.run(1000);
  float before = r.plant.mm;
  r.plant.heartbeat = false; r.run(10);
  CHECK(r.stance.state == StanceState::HELD); CHECK(r.plant.drive == 0); CHECK(!r.plant.release);
  CHECK(contains(r.stance.reason, "heartbeat"));
  r.run(3000); CHECK(std::fabs(r.plant.mm - before) < 0.2f); CHECK(r.plant.seated == 2); CHECK(!r.stance.driveAllowed());
  PostureEstimate p = estimatePosture(r.stance); CHECK(p.valid && p.source == PitchSource::SHOULDER_LOCK);
  r.plant.heartbeat = true; r.run(1000); CHECK(r.stance.state == StanceState::HELD); CHECK(r.plant.drive == 0); // no automatic restart
  r.cool(); r.request = StanceTarget::TWO_FOOT; r.run(20);
  CHECK(r.stance.phase == StancePhase::LIFT); CHECK(r.runUntil(StanceState::TWO_FOOT, 30000)); CHECK(!r.plant.unsafe);
 }
 { // Heartbeat lost mid-tilt: held, lock command unchanged, posture still known.
  Rig s; threeFoot(s); s.request = StanceTarget::TWO_FOOT;
  CHECK(s.runUntilPhase(StancePhase::TILT, 2000)); s.run(3000);
  s.plant.heartbeat = false; s.run(10);
  CHECK(s.stance.state == StanceState::HELD); CHECK(s.plant.drive == 0); CHECK(s.plant.release);
  PostureEstimate q = estimatePosture(s.stance); CHECK(q.valid && q.source == PitchSource::THREE_FOOT_KINEMATICS && q.pitchDeg > 0);
 }
 { // Heartbeat lost while the pin is being pulled at the three-foot bushing.
  Rig u; threeFoot(u); u.request = StanceTarget::TWO_FOOT; u.run(100);
  CHECK(u.stance.phase == StancePhase::UNLOCKING);
  u.plant.heartbeat = false; u.run(10);
  CHECK(u.stance.state == StanceState::HELD); CHECK(u.plant.drive == 0);
 }
 { // Operator release mid-change.
  Rig v; twoFoot(v); v.cool(); v.request = StanceTarget::THREE_FOOT; v.run(1000); CHECK(v.stance.state == StanceState::DEPLOYING);
  v.release(); CHECK(v.stance.state == StanceState::HELD); CHECK(v.plant.drive == 0); CHECK(contains(v.stance.reason, "released"));
 }
 // The controller lease is the firmware heartbeat source.
 Controller c; CHECK(c.arm(100, 7, true));
 Command stanceCommand; stanceCommand.stance = 2;
 CHECK(c.accept(150, 7, 1, stanceCommand, true)); CHECK(c.fresh(150 + DEADMAN - 1)); CHECK(!c.fresh(150 + DEADMAN));
}

static void powerAndFeedbackFaults() {
 { Rig r; threeFoot(r); r.request = StanceTarget::TWO_FOOT; r.run(3000);
   CHECK(r.stance.state == StanceState::RETRACTING);
   r.plant.power = false; r.run(10);
   CHECK(r.stance.fault == StanceFault::POWER); CHECK(r.plant.drive == 0);
   CHECK(!r.stance.driveAllowed()); CHECK(!estimatePosture(r.stance).valid);
   CHECK(contains(r.stance.blocked(StanceTarget::TWO_FOOT, r.t, true), "fault"));
   r.plant.power = true; r.release();
   CHECK(r.stance.clearFault(r.t)); CHECK(r.stance.state == StanceState::HELD);
   r.run(10); CHECK(r.stance.state == StanceState::HELD); CHECK(!r.plant.release); // recovery output reaches the HAL on the next tick
   r.cool(); r.request = StanceTarget::TWO_FOOT; CHECK(r.runUntil(StanceState::TWO_FOOT, 60000)); CHECK(!r.plant.unsafe); }
 { Rig f; twoFoot(f); f.cool(); f.request = StanceTarget::THREE_FOOT; f.run(2000); CHECK(f.stance.state == StanceState::DEPLOYING);
   f.plant.positionOk = false; f.run(10);
   CHECK(f.stance.fault == StanceFault::FEEDBACK); CHECK(f.plant.drive == 0); CHECK(!f.plant.release);
   f.release(); CHECK(!f.stance.clearFault(f.t)); CHECK(f.stance.state == StanceState::FAULT);
   f.plant.positionOk = true; f.run(10); CHECK(f.stance.clearFault(f.t)); CHECK(f.stance.state == StanceState::HELD); }
 { Rig g; threeFoot(g); CHECK(g.stance.driveAllowed()); g.plant.positionOk = false; g.run(10);
   CHECK(g.stance.fault == StanceFault::FEEDBACK); CHECK(!g.stance.driveAllowed()); }
 { Rig h; twoFoot(h); h.plant.lockOk = false; h.run(10); CHECK(h.stance.fault == StanceFault::LOCK_SENSOR); CHECK(!h.stance.headAllowed()); }
 { Rig k; threeFoot(k); k.request = StanceTarget::TWO_FOOT; k.run(4000); k.plant.limitsClosed = false; k.run(10);
   CHECK(k.stance.fault == StanceFault::TRAVEL_LIMIT); CHECK(k.plant.drive == 0); }
 { Rig m; threeFoot(m); m.plant.reversedFeedback = true; m.request = StanceTarget::TWO_FOOT; m.run(2500);
   CHECK(m.stance.fault == StanceFault::REVERSED_FEEDBACK); CHECK(m.plant.drive == 0); }
 { Rig n; twoFoot(n); n.plant.mm = L.twoFootMm + L.holdToleranceMm + 0.5f; n.run(10); CHECK(n.stance.fault == StanceFault::DRIFT); }
}

static void stallAndTimeout() {
 { Rig r; threeFoot(r); r.request = StanceTarget::TWO_FOOT;
   CHECK(r.runUntilPhase(StancePhase::TILT, 2000)); r.run(1500);
   r.plant.stalled = true; r.run(L.progressMs + 20);
   CHECK(r.stance.fault == StanceFault::STALL); CHECK(r.plant.drive == 0);
   r.plant.stalled = false; r.release(); CHECK(r.stance.clearFault(r.t)); CHECK(r.stance.state == StanceState::HELD);
   CHECK(contains(r.stance.blocked(StanceTarget::TWO_FOOT, r.t, true), "release")); // a clear needs a fresh press
   r.run(10); CHECK(contains(r.stance.blocked(StanceTarget::TWO_FOOT, r.t, true), "cooling")); }
 { Rig s; threeFoot(s);
   s.plant.speed = (L.progressMm * 1.3f) / L.progressMs; // moving, but far too slowly
   s.request = StanceTarget::TWO_FOOT; s.run(L.travelTimeoutMs + 1000);
   CHECK(s.stance.fault == StanceFault::TRAVEL_TIMEOUT); CHECK(s.plant.drive == 0); }
 { // Pin will not pull out of the three-foot bushing: never starts to tilt.
   Rig t; threeFoot(t); t.plant.stuckSeated = true; t.request = StanceTarget::TWO_FOOT; t.run(L.lockTimeoutMs + 50);
   CHECK(t.stance.fault == StanceFault::LOCK_TIMEOUT); CHECK(t.plant.drive == 0); CHECK(!t.plant.movedPinned);
   CHECK(std::fabs(t.plant.mm - BUSHING3) < 0.01f); }
 { // Pin will not pull out of the two-foot bushing at floor contact.
   Rig u; twoFoot(u); u.cool(); u.request = StanceTarget::THREE_FOOT;
   CHECK(u.runUntilPhase(StancePhase::UNLOCKING, 20000)); u.plant.stuckSeated = true; u.run(L.lockTimeoutMs + 50);
   CHECK(u.stance.fault == StanceFault::LOCK_TIMEOUT); CHECK(u.plant.drive == 0); CHECK(!u.plant.unsafe);
   CHECK(u.plant.mm <= L.contactMm + L.stopToleranceMm + 0.1f); }
}

static void lockSensorDisagreesWithEndpoint() {
 { // Post reaches the two-foot bushing but the pin never seats: the foot is never raised.
   Rig r; threeFoot(r); r.plant.jammed = true; r.request = StanceTarget::TWO_FOOT;
   CHECK(r.runUntilPhase(StancePhase::LOCKING, 40000)); r.run(L.lockSettleMs + 3000 + L.lockTimeoutMs);
   CHECK(r.stance.fault == StanceFault::LOCK_TIMEOUT); CHECK(r.plant.drive == 0);
   CHECK(r.plant.mm >= L.contactMm - L.overshootMm - L.stopToleranceMm - 0.1f); CHECK(!r.plant.unsafe);
   CHECK(contains(r.stance.reason, "not engaged"));
   r.release(); CHECK(r.stance.clearFault(r.t)); CHECK(r.stance.state == StanceState::HELD); }
 { // Deploy reaches the three-foot bushing but the pin never seats: no drive.
   Rig d; twoFoot(d); d.cool(); d.plant.jammed = false; d.request = StanceTarget::THREE_FOOT;
   CHECK(d.runUntilPhase(StancePhase::TILT, 30000)); d.plant.jammed = true;
   CHECK(d.runUntilPhase(StancePhase::LOCKING, 40000)); d.run(L.lockSettleMs + 3000 + L.lockTimeoutMs);
   CHECK(d.stance.fault == StanceFault::LOCK_TIMEOUT); CHECK(!d.stance.driveAllowed()); CHECK(d.plant.drive == 0);
   CHECK(d.plant.mm <= L.threeFootMm + L.overtravelMm); }
 { // Standing on two feet and the sensor reports released.
   Rig a; twoFoot(a); a.plant.sensorSaysReleased = true; a.run(10);
   CHECK(a.stance.fault == StanceFault::LOCK_DISAGREES); CHECK(a.plant.drive == 0); CHECK(!a.stance.headAllowed());
   a.release(); CHECK(!a.stance.clearFault(a.t));
   a.plant.sensorSaysReleased = false; a.run(10); CHECK(a.stance.clearFault(a.t)); CHECK(a.stance.state == StanceState::TWO_FOOT); }
 { // Parked on three feet and the sensor reports released: drive refused.
   Rig b; threeFoot(b); b.plant.sensorSaysReleased = true; b.run(10);
   CHECK(b.stance.fault == StanceFault::LOCK_DISAGREES); CHECK(!b.stance.driveAllowed()); }
 { // Sensor drops out while the lock carries the raised foot.
   Rig c; threeFoot(c); c.request = StanceTarget::TWO_FOOT;
   CHECK(c.runUntilPhase(StancePhase::LIFT, 40000)); c.run(500);
   c.plant.sensorSaysReleased = true; c.run(10);
   CHECK(c.stance.fault == StanceFault::LOCK_DISAGREES); CHECK(c.plant.drive == 0); CHECK(!c.plant.release); }
 { // Sensor claims seated mid-tilt where no bushing exists.
   Rig e; threeFoot(e); e.request = StanceTarget::TWO_FOOT; CHECK(e.runUntilPhase(StancePhase::TILT, 2000)); e.run(3000);
   e.plant.sensorSaysEngaged = true; e.run(10);
   CHECK(e.stance.fault == StanceFault::LOCK_DISAGREES); CHECK(e.plant.drive == 0); }
}

static void driveDuringTransitionRefused() {
 Rig r; threeFoot(r);
 r.idle = false; r.request = StanceTarget::TWO_FOOT; r.run(100);
 CHECK(r.stance.state == StanceState::THREE_FOOT); CHECK(r.plant.drive == 0); CHECK(!r.plant.release);
 CHECK(contains(r.stance.blocked(StanceTarget::TWO_FOOT, r.t, false), "stop wheels"));
 r.idle = true; r.release(); r.request = StanceTarget::TWO_FOOT;
 CHECK(r.runUntilPhase(StancePhase::TILT, 2000)); r.run(500);
 CHECK(r.stance.state == StanceState::RETRACTING); CHECK(!r.stance.driveAllowed());
 r.idle = false; r.run(10);
 CHECK(r.stance.state == StanceState::HELD); CHECK(r.plant.drive == 0); CHECK(!r.stance.driveAllowed());
 CHECK(contains(r.stance.reason, "drive"));
 Command c; c.stance = 2; c.speed = 10; CHECK(!valid(c));
 c.speed = 0; c.turn = 5; CHECK(!valid(c));
 c.turn = 0; c.head = 1; CHECK(!valid(c));
 c.head = 0; CHECK(valid(c)); c.stance = 1; CHECK(!valid(c));
 // Reversal mid-change holds; the new direction needs a release and a fresh press.
 Rig s; threeFoot(s); s.request = StanceTarget::TWO_FOOT; CHECK(s.runUntilPhase(StancePhase::TILT, 2000)); s.run(2000);
 s.request = StanceTarget::THREE_FOOT; s.run(10);
 CHECK(s.stance.state == StanceState::HELD); CHECK(s.plant.drive == 0);
 s.run(500); CHECK(s.stance.state == StanceState::HELD);
 s.cool(); s.request = StanceTarget::THREE_FOOT;
 CHECK(s.runUntil(StanceState::THREE_FOOT, 40000)); CHECK(s.plant.seated == 3);
}

static void wrapAndPosture() {
 Rig r; r.t = 0xFFFFF000u; threeFoot(r);
 r.request = StanceTarget::TWO_FOOT;
 CHECK(r.runUntil(StanceState::TWO_FOOT, 60000)); CHECK(!r.plant.unsafe);
 // Provisional geometry: GUIDE_ANGLE 30 deg, contact 36.647 mm, 16.163 deg at POST_MAX 98 mm.
 CHECK(std::fabs(threeFootPitchDegrees(98) - 16.1627f) < 0.01f);
 CHECK(std::fabs(threeFootPitchDegrees(50) - 5.0029f) < 0.01f);
 CHECK(threeFootPitchDegrees(20) == 0.0f);
 CHECK(std::fabs(centerFootOffsetMm(98) - 230.206f) < 0.05f);
 for (int s = 0; s <= 100; ++s) CHECK(threeFootPitchDegrees((float)s) >= 0 && threeFootPitchDegrees((float)s) < 17);
 for (int y = -8; y <= 8; y++) CHECK(std::fabs(steeringServoDegrees((float)y)) < 25);
 Command n; n.speed = 60; n.turn = 100; Mix m = mix(n, centerFootOffsetMm(L.threeFootMm));
 CHECK(m.left > m.right); CHECK(m.yaw < 0);
}

int main() {
 sensorConditioning();
 limitsAndBoot();
 normalRetractThenDeploy();
 commandLossMidTransition();
 powerAndFeedbackFaults();
 stallAndTimeout();
 lockSensorDisagreesWithEndpoint();
 driveDuringTransitionRefused();
 wrapAndPosture();
 std::printf("PASS: %d stance checks: transitions both ways, command loss, power/feedback faults, stall/timeout, lock disagreement, drive refusal, sensor conditioning, posture\n", checks);
 return 0;
}
