// Host tests for the doorbot state machine. Run with:  pio test -e native
// These test behaviour that would otherwise only be observable by standing at a real door:
// the wave and kick gestures, the obstacle retry policy the operator specified verbatim, the
// stall handling that tells "shut" apart from "blocked", and manual opening.

#include <unity.h>

#include "controller.h"

using namespace doorbot;

namespace {

struct Rig {
    Controller c;
    Inputs in;
    Outputs out;
    int32_t edges = 0;

    Rig() {
        c.set_cable_mm_per_edge(0.0812f);
        c.set_travel_mm(105.9f);
    }
    // Advance time, optionally winding cable in at the analysed rate.
    Outputs tick(uint32_t dt_ms, bool winding_moves = true) {
        in.now_ms += dt_ms;
        if (winding_moves && out.motor == Motor::Wind) {
            // 21.8 s for 105.9 mm is 4.86 mm/s, i.e. 59.8 edges per second.
            edges += (int32_t)(dt_ms * 0.0598f);
        } else if (winding_moves && out.motor == Motor::Payout) {
            edges -= (int32_t)(dt_ms * 0.0598f);
        }
        in.encoder_edges = edges;
        in.impact = false;
        out = c.update(in);
        return out;
    }
    Outputs run(uint32_t total_ms, uint32_t step = 20, bool moves = true) {
        for (uint32_t t = 0; t < total_ms; t += step) tick(step, moves);
        return out;
    }
    void wave() {
        in.wave_mm = 120;
        tick(20);
        tick(20);
        in.wave_mm = 0;
    }
    void kick(uint32_t gap_ms) {
        in.impact = true;
        in.now_ms += 20;
        out = c.update(in);
        in.impact = false;
        run(gap_ms - 20, 20);
        in.impact = true;
        in.now_ms += 20;
        out = c.update(in);
        in.impact = false;
    }
};

// A hand passing the wave window twice commands a close.
void test_wave_commands_close() {
    Rig r;
    r.run(200);
    TEST_ASSERT_EQUAL(State::Homing, r.out.state);
    r.wave();
    r.tick(20);
    TEST_ASSERT_EQUAL(State::Closing, r.out.state);
    TEST_ASSERT_EQUAL(Motor::Wind, r.out.motor);
}

// A single brush past the sensor must not close a door on anyone.
void test_single_sample_does_not_command() {
    Rig r;
    r.run(200);
    r.in.wave_mm = 120;
    r.tick(20);
    r.in.wave_mm = 0;
    r.tick(20);
    TEST_ASSERT_EQUAL(State::Homing, r.out.state);
}

// Two kicks inside the window command a close; two far apart do not.
void test_double_kick_commands_close() {
    Rig r;
    r.run(200);
    r.kick(400);
    TEST_ASSERT_EQUAL(State::Closing, r.out.state);
}

void test_slow_second_kick_is_ignored() {
    Rig r;
    r.run(200);
    r.kick(2000);
    TEST_ASSERT_EQUAL(State::Homing, r.out.state);
}

// A body in the doorway blocks the command outright.
void test_obstacle_blocks_command() {
    Rig r;
    r.run(200);
    r.in.guard_mm = 800;
    r.wave();
    r.tick(20);
    TEST_ASSERT_EQUAL(State::Blocked, r.out.state);
    TEST_ASSERT_EQUAL(Motor::Coast, r.out.motor);
}

// The operator's policy, verbatim: retry every 19 seconds for a minute, then alert.
void test_retry_every_19s_then_alert() {
    Rig r;
    r.run(200);
    r.in.guard_mm = 800;          // obstacle never clears
    r.wave();
    r.tick(20);
    TEST_ASSERT_EQUAL(State::Blocked, r.out.state);

    r.run(18000);
    TEST_ASSERT_EQUAL(0, r.out.retries);
    r.run(1500);                  // past 19 s
    TEST_ASSERT_EQUAL(1, r.out.retries);
    TEST_ASSERT_EQUAL(State::Blocked, r.out.state);
    r.run(19000);
    TEST_ASSERT_EQUAL(2, r.out.retries);
    r.run(19000);
    TEST_ASSERT_EQUAL(3, r.out.retries);
    r.run(3000);                  // now past the 60 s window
    TEST_ASSERT_EQUAL(State::Alert, r.out.state);
    TEST_ASSERT_EQUAL(Motor::Coast, r.out.motor);
}

// If the way clears before the window expires, the retry actually closes the door.
void test_retry_closes_when_cleared() {
    Rig r;
    r.run(200);
    r.in.guard_mm = 800;
    r.wave();
    r.tick(20);
    TEST_ASSERT_EQUAL(State::Blocked, r.out.state);
    r.run(10000);
    r.in.guard_mm = 0;            // person walks away
    r.run(10000);
    TEST_ASSERT_EQUAL(State::Closing, r.out.state);
}

// Winding until the motor stalls after real travel is what "shut" means on the first close,
// and that is also where the cable reference gets set.
void test_first_close_homes_and_shuts() {
    Rig r;
    r.run(200);
    r.wave();
    r.tick(20);
    TEST_ASSERT_EQUAL(State::Closing, r.out.state);
    r.run(22000);                 // the analysed close takes 21.8 s
    TEST_ASSERT_EQUAL(State::Closing, r.out.state);
    r.run(400, 20, false);        // encoder stops: the leaf is against the magnets
    TEST_ASSERT_EQUAL(State::Shut, r.out.state);
    TEST_ASSERT_FLOAT_WITHIN(0.01f, 0.0f, r.out.cable_mm);
}

// A stall with the door still well open is an obstacle, not a closed door - this is the check
// that stops it pushing 151 N into a foot until the timeout.
void test_early_stall_is_treated_as_blocked() {
    Rig r;
    r.run(200);
    r.wave();
    r.tick(20);
    r.run(400);                   // barely any travel
    r.run(400, 20, false);        // then nothing moves
    TEST_ASSERT_EQUAL(State::Blocked, r.out.state);
}

// After shutting, a little cable is paid out so the magnets hold the door, not the motor.
void test_shut_pays_out_slack() {
    Rig r;
    r.run(200);
    r.wave();
    r.tick(20);
    r.run(22000);
    r.run(400, 20, false);
    TEST_ASSERT_EQUAL(State::Shut, r.out.state);
    r.tick(20);
    TEST_ASSERT_EQUAL(Motor::Payout, r.out.motor);
    r.run(1200);
    TEST_ASSERT_EQUAL(Motor::Coast, r.out.motor);
}

// Pulling the door open by hand must be noticed, and must not be fought.
void test_manual_open_is_detected() {
    Rig r;
    r.run(200);
    r.wave();
    r.tick(20);
    r.run(22000);
    r.run(400, 20, false);
    r.run(1200);
    TEST_ASSERT_EQUAL(State::Shut, r.out.state);
    r.edges -= 600;               // the door is pulled open, free-spooling the drum
    r.tick(20, false);
    TEST_ASSERT_EQUAL(State::Open, r.out.state);
    TEST_ASSERT_EQUAL(Motor::Coast, r.out.motor);
}

// With the doorway clear for long enough, it closes on its own.
void test_auto_close_after_clear_delay() {
    Rig r;
    r.run(200);
    r.wave();
    r.tick(20);
    r.run(22000);
    r.run(400, 20, false);
    r.run(1200);
    r.edges -= 600;
    r.tick(20, false);
    TEST_ASSERT_EQUAL(State::Open, r.out.state);
    // Step until it decides for itself, and stop the moment it does: running on past that
    // point with a frozen encoder would only be testing the stall detector again.
    for (int i = 0; i < 2000 && r.out.state == State::Open; i++) r.tick(20, false);
    TEST_ASSERT_EQUAL(State::Closing, r.out.state);
    r.tick(20);                   // the deciding tick returns Coast; winding starts the next
    TEST_ASSERT_EQUAL(Motor::Wind, r.out.motor);
}

// A driver fault stops the motor and latches until it clears.
void test_driver_fault_stops_everything() {
    Rig r;
    r.run(200);
    r.wave();
    r.tick(20);
    TEST_ASSERT_EQUAL(State::Closing, r.out.state);
    r.in.driver_fault = true;
    r.tick(20);
    TEST_ASSERT_EQUAL(State::Fault, r.out.state);
    TEST_ASSERT_EQUAL(Motor::Coast, r.out.motor);
    r.run(1000);
    TEST_ASSERT_EQUAL(State::Fault, r.out.state);
}

}  // namespace

void setUp() {}
void tearDown() {}

int main(int, char **) {
    UNITY_BEGIN();
    RUN_TEST(test_wave_commands_close);
    RUN_TEST(test_single_sample_does_not_command);
    RUN_TEST(test_double_kick_commands_close);
    RUN_TEST(test_slow_second_kick_is_ignored);
    RUN_TEST(test_obstacle_blocks_command);
    RUN_TEST(test_retry_every_19s_then_alert);
    RUN_TEST(test_retry_closes_when_cleared);
    RUN_TEST(test_first_close_homes_and_shuts);
    RUN_TEST(test_early_stall_is_treated_as_blocked);
    RUN_TEST(test_shut_pays_out_slack);
    RUN_TEST(test_manual_open_is_detected);
    RUN_TEST(test_auto_close_after_clear_delay);
    RUN_TEST(test_driver_fault_stops_everything);
    return UNITY_END();
}
