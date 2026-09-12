#include "control.h"
#include <assert.h>
#include <stdio.h>
#include <initializer_list>

int main() {
  using namespace dalek;
  long parsed = 0;
  assert(parseInteger("-150", -150, 150, parsed) && parsed == -150);
  for (const char *bad : {"", " 1", "1x", "1.5", "151", "99999999999999999999", "nan"})
    assert(!parseInteger(bad, -150, 150, parsed));
  Controller c;
  Command moving;
  moving.left = 100;
  moving.head = 75;
  assert(!c.accept(0, 123, 1, moving, true));
  assert(!c.arm(0, 123, false));
  assert(c.arm(100, 123, true));
  assert(c.command.left == 0);
  assert(c.accept(110, 123, 1, moving, true));
  assert(!c.accept(111, 123, 1, moving, true)); // replay does not refresh timeout.
  assert(!c.accept(112, 999, 2, moving, true));
  c.tick(609, true);
  assert(c.armed);
  assert(!c.accept(610, 123, 2, moving, true)); // expires before processing late command.
  assert(!c.armed && c.command.left == 0 && c.command.head == 0);
  c.tick(700, true); // reconnect/healthy cannot arm.
  assert(!c.armed);
  assert(c.arm(800, 456, true));
  assert(!c.accept(801, 123, 99, moving, true)); // stale prior lease.
  assert(c.command.left == 0);
  moving.left = DRIVE_LIMIT + 1;
  assert(!c.accept(802, 456, 1, moving, true));
  moving.left = 100;
  c.tick(803, false);
  assert(!c.armed && c.command.left == 0 && c.command.head == 0);
  assert(c.arm(0xfffffff0u, 789, true));
  c.tick(0x100u, true);
  assert(c.armed);
  c.tick(0x1e4u, true); // millis rollover.
  assert(!c.armed);
  Ramp r;
  for (uint32_t t = 0; t < 100; t += 10) r.tick(100, t);
  assert(r.value == 50);
  for (uint32_t t = 100; t < 200; t += 10) assert(r.tick(-100, t) >= 0);
  assert(r.value == 0);
  assert(r.tick(-100, 250) == 0);
  assert(r.tick(-100, 290) == -5);
  r.stop();
  assert(r.value == 0);
  HeadMotor head;
  for (uint32_t t = 0; t < 500; t += 10) assert(head.tick(100, t, true) <= HEAD_LIMIT);
  assert(head.ramp.value == HEAD_LIMIT);
  for (uint32_t t = 500; t < 700; t += 10) assert(head.tick(-100, t, true) >= 0);
  assert(head.ramp.value == 0 && head.zeroSince == 690);
  assert(head.tick(-100, 789, true) == 0);
  assert(head.tick(-100, 790, true) == -5);
  assert(head.tick(0, 791, true) == 0); // Zero removes PWM immediately.
  assert(head.tick(100, 890, true) == 0); // Brief zero cannot evade reversal hold.
  assert(head.tick(100, 891, true) == 5);
  assert(head.tick(100, 892, false) == 0); // Fault bypasses acceleration ramp.
  assert(head.tick(-100, 991, true) == 0); // Re-arm cannot evade reversal hold.
  assert(head.tick(-100, 992, true) == -5);
  head.stop(0xfffffff0u);
  assert(head.tick(100, 0x53u, true) == 0);
  assert(head.tick(100, 0x54u, true) == 5); // Dead time across millis rollover.
  for (uint32_t t = 1000; t < 2000; t += 10) assert(head.tick(1000, t, true) <= HEAD_LIMIT);
  assert(head.ramp.value == HEAD_LIMIT); // Defense in depth for internal callers.
  puts("PASS: parsing, boot lockout, lease replay, timeout, reconnect, fault interlock, rollover, ramp/reversal; head PWM cap, immediate stop, dead time through zero/re-arm/rollover");
}
