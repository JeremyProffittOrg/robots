#pragma once
#include <stdint.h>
#include <stdlib.h>
#include <errno.h>
#include <ctype.h>

namespace dalek {
constexpr uint32_t DEADMAN_MS = 500;
constexpr int DRIVE_LIMIT = 150; // 150/255, deliberately reduced commissioning speed.
constexpr int HEAD_LIMIT = 100; // 100/255 maximum; no speed feedback.
constexpr int ARM_RADIUS_LIMIT = 8; // Concealed gimbal clearance limit in degrees.

inline bool parseInteger(const char *text, long low, long high, long &value) {
  if (!text || !*text || isspace(static_cast<unsigned char>(*text))) return false;
  errno = 0;
  char *end;
  long parsed = strtol(text, &end, 10);
  if (errno || *end || parsed < low || parsed > high) return false;
  value = parsed;
  return true;
}

struct Command {
  int left = 0, right = 0, head = 0;
  bool arms = false;
  int radius = 8; // degrees, software bounded to 0..8.
  int frequency = 40; // hundredths of Hz, 10..80.
};

inline bool valid(const Command &c) {
  return c.left >= -DRIVE_LIMIT && c.left <= DRIVE_LIMIT &&
         c.right >= -DRIVE_LIMIT && c.right <= DRIVE_LIMIT &&
         c.head >= -100 && c.head <= 100 &&
         c.radius >= 0 && c.radius <= ARM_RADIUS_LIMIT &&
         c.frequency >= 10 && c.frequency <= 80;
}

class Controller {
 public:
  bool armed = false;
  uint32_t lease = 0, sequence = 0, lastCommand = 0;
  Command command;

  void stop() {
    armed = false;
    lease = 0;
    command = Command{};
  }

  bool arm(uint32_t now, uint32_t newLease, bool healthy) {
    if (armed || !healthy || newLease == 0) return false;
    command = Command{};
    sequence = 0;
    lease = newLease;
    lastCommand = now;
    armed = true;
    return true;
  }

  void tick(uint32_t now, bool healthy) {
    if (!healthy || (armed && static_cast<uint32_t>(now - lastCommand) >= DEADMAN_MS)) stop();
  }

  bool accept(uint32_t now, uint32_t givenLease, uint32_t nextSequence,
              const Command &next, bool healthy) {
    tick(now, healthy); // An expired lease cannot be revived by a late heartbeat.
    if (!armed || givenLease != lease || nextSequence <= sequence || !valid(next)) return false;
    command = next;
    sequence = nextSequence;
    lastCommand = now;
    return true;
  }
};

class Ramp {
 public:
  int value = 0;
  uint32_t reverseHoldUntil = 0;
  bool holding = false;
  int tick(int target, uint32_t now) {
    if (holding) {
      if (static_cast<int32_t>(now - reverseHoldUntil) < 0) return 0;
      holding = false;
    }
    const bool reverse = (value > 0 && target < 0) || (value < 0 && target > 0);
    int next = reverse ? 0 : target;
    if (value < next) value += (next - value > 5 ? 5 : next - value);
    if (value > next) value -= (value - next > 5 ? 5 : value - next);
    if (reverse && value == 0) {
      reverseHoldUntil = now + 100;
      holding = true;
    }
    return value;
  }
  void stop() { value = 0; holding = false; }
};

class HeadMotor {
 public:
  Ramp ramp;
  int lastDirection = 0;
  uint32_t zeroSince = 0;

  void stop(uint32_t now) {
    if (ramp.value != 0) zeroSince = now;
    ramp.stop();
  }

  int tick(int percent, uint32_t now, bool permitted) {
    if (!permitted || percent == 0) { stop(now); return 0; }
    if (percent > 100) percent = 100;
    if (percent < -100) percent = -100;
    const int target = percent * HEAD_LIMIT / 100;
    const int direction = target > 0 ? 1 : -1;
    if (ramp.value != 0 && direction != lastDirection) {
      if (ramp.tick(0, now) == 0) zeroSince = now;
      return ramp.value;
    }
    // A slider passing through zero, or a quick disarm/re-arm, cannot bypass
    // the same 100ms coast interval required for a direct reversal.
    if (ramp.value == 0 && lastDirection != 0 && direction != lastDirection &&
        static_cast<uint32_t>(now - zeroSince) < 100) return 0;
    const int result = ramp.tick(target, now);
    if (result != 0) lastDirection = direction;
    return result;
  }
};
}
