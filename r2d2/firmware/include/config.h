#pragma once
// Revision D: DFRobot Romeo ESP32-S3 DFR0994 (ESP32-S3-WROOM-1U-N16R8, four onboard DRV8876, schematic V1.1.0).
// Host-compilable: no Arduino headers.
#include "inputs.h"
#include "stance.h"
namespace pins {
// Onboard DRV8876 channels in PH/EN mode (PMODE link fitted). EN = PWM, PH = direction.
constexpr int LEFT_EN=12, LEFT_PH=13;     // M1: left foot, two 3777 motors in parallel
constexpr int RIGHT_EN=14, RIGHT_PH=21;   // M2: right foot pair
constexpr int CENTER_EN=9, CENTER_PH=10;  // M3: centre foot pair
constexpr int HEAD_EN=47, HEAD_PH=11;     // M4: head friction-wheel motor
constexpr int BCLK=15, LRCLK=16, AUDIO=17; // MAX98357A I2S
constexpr int STEER=40, LOCK_SERVO=41;    // MG995 pulses through 74AHCT125 gates to 5 V
constexpr int POST_EXTEND=38, POST_RETRACT=42; // DRV8871 IN1/IN2 through AHCT125 gates enabled by NC travel limits
constexpr int LIMIT_EXTEND_OPEN=7, LIMIT_RETRACT_OPEN=8; // HIGH = that NC limit is open (direction disabled)
constexpr int LOCK_NO=18, LOCK_NC=5;      // SS-01GL NO and NC contacts, COM to GND; LOW = closed
constexpr int WITHDRAWN_NO=43, WITHDRAWN_NC=44; // second SPDT switch at full6mm withdrawal
constexpr int POST_POSITION=4;            // ADC1_CH3, P16 wiper
constexpr int PACK=6;                     // ADC1_CH5, battery divider 100k/22k
constexpr int POWER=39;                   // 5.7 V RUN rail through 10k/10k divider; HIGH = present
}

// ===== PROVISIONAL MECHANISM CONSTANTS =====
// Source: mechanical agent selection and kinematics draft, 2026-09-12. Provisional until
// scripts/check_kinematics.py passes on the committed CAD; replace every value in this block together.
namespace geometry {
constexpr float HIP_Z_MM=390.0f, ANKLE_Z_MM=113.0f, GUIDE_ANGLE_DEG=35.0f, GUIDE_Y_MM=40.0f, GUIDE_Z_MM=240.0f, POST_ZERO_MM=110.0f;
constexpr float LOCK_RADIUS_MM=45.0f;   // GN817 pin radius from the shoulder axis
}
namespace calibration {
constexpr r2::StanceLimits STANCE={
 -1.0f,101.0f,         // sensor band
 2.0f,45.038373f,98.0f,   // two-foot, upright contact, three-foot12.83248deg receiver
 0.4f,2.5f,2.5f,       // stop tolerance, hold tolerance, lock window
 1.5f,0.8f,1.5f,       // seek, overshoot, overtravel
 0.5f,750,             // stall: 0.5 mm progress within 750 ms
 40000,400,1500,150,   // travel timeout, lock settle, lock timeout, reverse dwell
 4,                    // P16 20% duty: 4 ms rest per ms of travel
 60                    // lock-seek creep duty, percent; lower at commissioning if the pin does not catch
};
constexpr float POST_NO_LOAD_SPEED_MM_S=4.8f; // Actuonix P16-100-256-12-P datasheet
}
// ===== END PROVISIONAL MECHANISM CONSTANTS =====

namespace calibration {
constexpr int DIRECTION[3]={1,1,1}; // left, right, centre; lift robot and change after wheel-direction test
constexpr int HEAD_LIMIT=70;
constexpr float STEER_US_PER_DEGREE=6.666667f; // goBILDA2000-0025-0002:0.15degree per microsecond
constexpr int STEER_CENTER_US=1500;
constexpr float PACK_SCALE=122.0f/22.0f, PACK_CORRECTION=1.0f;
constexpr float CUTOFF=11.2f, REARM=12.0f, MAX_PACK=15.2f;
// MG995 release: 17 mm finger, 28 deg pulls the GN817 knob 7.98 mm. Calibrate both pulses on the lever.
constexpr int LOCK_RELEASE_US=1000, LOCK_ENGAGE_US=1311;
constexpr uint32_t LOCK_LEGAL_MS=30, LOCK_ILLEGAL_MS=150;
// P16-100 pot, nominal 11k with 2.2k top resistor: 0 mV at stroke 0, 2750 mV at stroke 100.
// Measure zeroMv/fullMv on the detached actuator before installation (pot tolerance +/-50%).
constexpr r2::PotCalibration POT={0.0f,2750.0f,100.0f,5.0f,3000.0f};
}
