#pragma once
// doorbot behaviour, as a pure state machine with no Arduino dependency so that
// firmware/test/test_controller.cpp can compile and run it on the host.
//
// The obstacle policy is the operator's, verbatim: "Retry every 19 seconds for a minute,
// then alert". RETRY_INTERVAL_MS and RETRY_WINDOW_MS below are that sentence.

#include <stdint.h>

namespace doorbot {

enum class State : uint8_t {
    Homing,      // cable position not yet known; the first close command establishes it
    Open,        // door is away from shut, drum free-spooling, nothing commanded
    Closing,     // winding cable in
    Blocked,     // something is in the way; waiting out the retry interval
    Alert,       // the retry window expired with the door still not shut
    Shut,        // closed and held by the magnets; a little slack paid out
    Fault,       // driver fault latched
};

enum class Motor : uint8_t { Coast, Wind, Payout, Brake };

struct Config {
    uint32_t retry_interval_ms = 19000;   // user-locked
    uint32_t retry_window_ms = 60000;     // user-locked
    uint32_t auto_close_clear_ms = 30000; // doorway must be clear this long before auto-close
    uint32_t stall_timeout_ms = 250;      // no encoder edge for this long while driving
    uint32_t wave_debounce_ms = 1500;
    uint32_t kick_min_gap_ms = 120;       // two impacts closer than this are one impact
    uint32_t kick_max_gap_ms = 900;       // and further apart than this are unrelated
    uint32_t close_timeout_ms = 45000;    // hard ceiling: 21.8 s is the analysed close time
    uint32_t slack_payout_ms = 900;       // pay a little cable out once the magnets have it
    uint16_t wave_near_mm = 20;           // hand-wave window
    uint16_t wave_far_mm = 250;
    uint16_t guard_near_mm = 120;         // doorway obstacle window
    uint16_t guard_far_mm = 1800;
    float shut_tolerance_mm = 12.0f;      // how close to the reference counts as shut
    float min_useful_travel_mm = 15.0f;   // a stall before this much travel is an obstacle
};

struct Inputs {
    uint32_t now_ms = 0;
    uint16_t wave_mm = 0;        // 0 = no valid reading
    uint16_t guard_mm = 0;
    bool impact = false;         // one accelerometer click event this tick
    int32_t encoder_edges = 0;   // cumulative, positive = cable wound in
    bool driver_fault = false;
    bool button = false;         // manual close/cancel request
};

struct Outputs {
    Motor motor = Motor::Coast;
    uint16_t duty_permille = 0;
    bool buzzer = false;
    State state = State::Homing;
    const char *reason = "boot";
    uint8_t retries = 0;
    float cable_mm = 0.0f;       // 0 = shut reference, positive = paid out
    float door_deg_estimate = 0.0f;
};

class Controller {
public:
    explicit Controller(const Config &cfg = Config()) : cfg_(cfg) {}

    void set_cable_mm_per_edge(float v) { mm_per_edge_ = v; }
    void set_travel_mm(float v) { travel_mm_ = v; }

    State state() const { return state_; }
    uint8_t retries() const { return retries_; }
    float cable_mm() const { return cable_mm_; }

    Outputs update(const Inputs &in) {
        // --- position from the encoder. Winding in reduces paid-out cable. This is
        // integrated whether or not the shut reference is known yet: before homing it starts
        // from the "assume fully open" prior, and homing then zeroes it on the real stop.
        cable_mm_ -= (in.encoder_edges - last_edges_) * mm_per_edge_;
        if (cable_mm_ < 0) cable_mm_ = 0;
        bool moved = in.encoder_edges != last_edges_;
        if (moved) last_move_ms_ = in.now_ms;
        last_edges_ = in.encoder_edges;

        bool wave = wave_gesture(in);
        bool kick = kick_gesture(in);
        bool obstacle = in.guard_mm >= cfg_.guard_near_mm && in.guard_mm <= cfg_.guard_far_mm;
        if (obstacle) last_obstacle_ms_ = in.now_ms;
        bool commanded = wave || kick || in.button;

        if (in.driver_fault) {
            state_ = State::Fault;
            reason_ = "driver fault";
        }

        switch (state_) {
        case State::Fault:
            if (!in.driver_fault && commanded) { state_ = State::Homing; reason_ = "fault cleared"; }
            return out(Motor::Coast, 0, true);

        case State::Homing:
            if (commanded && !obstacle) { start_close(in, "homing close"); }
            else if (commanded) { enter_blocked(in, "doorway blocked"); }
            return out(Motor::Coast, 0, false);

        case State::Open:
            if (commanded && !obstacle) { start_close(in, wave ? "hand wave" : (kick ? "kick" : "button")); }
            else if (commanded && obstacle) { enter_blocked(in, "doorway blocked"); }
            else if (in.now_ms - last_obstacle_ms_ >= cfg_.auto_close_clear_ms
                     && cable_mm_ > cfg_.shut_tolerance_mm) {
                start_close(in, "auto close, doorway clear");
            }
            return out(Motor::Coast, 0, false);

        case State::Closing: {
            if (obstacle) { enter_blocked(in, "obstacle in the doorway"); return out(Motor::Brake, 0, false); }
            if (in.now_ms - drive_start_ms_ > cfg_.close_timeout_ms) {
                enter_blocked(in, "close timed out");
                return out(Motor::Brake, 0, false);
            }
            bool stalled = in.now_ms - last_move_ms_ >= cfg_.stall_timeout_ms
                           && in.now_ms - drive_start_ms_ > cfg_.stall_timeout_ms;
            if (stalled) {
                // Cable actually wound this attempt, measured straight off the encoder so it
                // is valid even before the shut reference exists.
                float wound = (in.encoder_edges - edges_at_start_) * mm_per_edge_;
                if (!have_ref_) {
                    // First ever close: the stall that follows real travel IS the shut
                    // position, so that is where the reference is set.
                    if (wound >= cfg_.min_useful_travel_mm) {
                        have_ref_ = true;
                        cable_mm_ = 0.0f;
                        enter_shut(in, "homed on the shut stop");
                    } else {
                        enter_blocked(in, "stalled before it moved");
                    }
                } else if (cable_mm_ <= cfg_.shut_tolerance_mm) {
                    enter_shut(in, "shut, magnets holding");
                } else {
                    enter_blocked(in, "stalled against something");
                }
                return out(Motor::Brake, 0, false);
            }
            return out(Motor::Wind, 1000, false);
        }

        case State::Blocked:
            if (in.now_ms - first_block_ms_ >= cfg_.retry_window_ms) {
                state_ = State::Alert;
                reason_ = "still blocked after a minute";
                return out(Motor::Coast, 0, true);
            }
            if (in.now_ms - block_ms_ >= cfg_.retry_interval_ms) {
                if (obstacle) { block_ms_ = in.now_ms; retries_++; reason_ = "retry deferred, still blocked"; }
                else { retries_++; start_close(in, "retry"); }
            }
            return out(Motor::Coast, 0, false);

        case State::Alert:
            if (commanded && !obstacle) { start_close(in, "cleared and commanded"); }
            return out(Motor::Coast, 0, alarm_pattern(in.now_ms));

        case State::Shut:
            if (in.now_ms - shut_ms_ < cfg_.slack_payout_ms) {
                return out(Motor::Payout, 600, false);
            }
            if (cable_mm_ > cfg_.shut_tolerance_mm * 2) {
                state_ = State::Open;
                reason_ = "opened by hand";
                last_obstacle_ms_ = in.now_ms;   // do not auto-close the instant it opens
            }
            return out(Motor::Coast, 0, false);
        }
        return out(Motor::Coast, 0, false);
    }

private:
    void start_close(const Inputs &in, const char *why) {
        state_ = State::Closing;
        reason_ = why;
        drive_start_ms_ = in.now_ms;
        last_move_ms_ = in.now_ms;
        edges_at_start_ = in.encoder_edges;
    }
    void enter_blocked(const Inputs &in, const char *why) {
        if (state_ != State::Blocked) {
            if (retries_ == 0) first_block_ms_ = in.now_ms;
            block_ms_ = in.now_ms;
        }
        state_ = State::Blocked;
        reason_ = why;
    }
    void enter_shut(const Inputs &in, const char *why) {
        state_ = State::Shut;
        reason_ = why;
        shut_ms_ = in.now_ms;
        retries_ = 0;
    }
    bool wave_gesture(const Inputs &in) {
        bool near = in.wave_mm >= cfg_.wave_near_mm && in.wave_mm <= cfg_.wave_far_mm;
        bool fired = false;
        if (near) {
            wave_samples_++;
            // The !waved_ term matters: without it the debounce compares against a
            // last-wave time of zero and swallows the very first gesture after boot.
            if (wave_samples_ == 2
                && (!waved_ || in.now_ms - last_wave_ms_ > cfg_.wave_debounce_ms)) {
                last_wave_ms_ = in.now_ms;
                waved_ = true;
                fired = true;
            }
        } else {
            wave_samples_ = 0;
        }
        return fired;
    }
    bool kick_gesture(const Inputs &in) {
        if (!in.impact) return false;
        // The first impact ever has nothing to pair with. Without this the boot-time zero
        // in last_impact_ms_ makes a single knock look like a double kick.
        if (!impacted_) {
            impacted_ = true;
            last_impact_ms_ = in.now_ms;
            return false;
        }
        uint32_t gap = in.now_ms - last_impact_ms_;
        last_impact_ms_ = in.now_ms;
        if (gap >= cfg_.kick_min_gap_ms && gap <= cfg_.kick_max_gap_ms) {
            impacted_ = false;     // consume the pair so three kicks are not two commands
            return true;
        }
        return false;
    }
    static bool alarm_pattern(uint32_t now) { return (now / 400) % 2 == 0; }

    Outputs out(Motor m, uint16_t duty, bool buzz) {
        Outputs o;
        o.motor = m;
        o.duty_permille = duty;
        o.buzzer = buzz;
        o.state = state_;
        o.reason = reason_;
        o.retries = retries_;
        o.cable_mm = cable_mm_;
        o.door_deg_estimate = travel_mm_ > 0 ? (cable_mm_ / travel_mm_) * 90.0f : 0.0f;
        return o;
    }

    Config cfg_;
    State state_ = State::Homing;
    const char *reason_ = "boot";
    float mm_per_edge_ = 0.0812f;
    float travel_mm_ = 105.9f;
    float cable_mm_ = 105.9f;
    int32_t edges_at_start_ = 0;
    bool have_ref_ = false;
    int32_t last_edges_ = 0;
    uint32_t last_move_ms_ = 0, drive_start_ms_ = 0, block_ms_ = 0, first_block_ms_ = 0;
    uint32_t shut_ms_ = 0, last_wave_ms_ = 0, last_impact_ms_ = 0, last_obstacle_ms_ = 0;
    uint8_t wave_samples_ = 0, retries_ = 0;
    bool waved_ = false, impacted_ = false;
};

inline const char *state_name(State s) {
    switch (s) {
    case State::Homing: return "HOMING";
    case State::Open: return "OPEN";
    case State::Closing: return "CLOSING";
    case State::Blocked: return "BLOCKED";
    case State::Alert: return "ALERT";
    case State::Shut: return "SHUT";
    case State::Fault: return "FAULT";
    }
    return "?";
}

}  // namespace doorbot
