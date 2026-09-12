#pragma once

namespace pins {
constexpr int SDA = 21, SCL = 22, SERVO_OE = 27;
constexpr int LEFT_FORWARD = 25, LEFT_REVERSE = 26;
constexpr int RIGHT_FORWARD = 32, RIGHT_REVERSE = 33;
constexpr int MOTOR_SLEEP = 12;
constexpr int HEAD_PWM = 2; // 20kHz PWM routed by U9; external 10k pull-down.
constexpr int I2S_BCLK = 17, I2S_LRC = 13, I2S_DATA = 15;
constexpr int ACTUATOR_POWER = 36, PACK_ADC = 39;
constexpr int BUTTON = 35;
}

namespace calibration {
// Bench-calibrate with horns REMOVED, then attach each arm at its mechanical centre.
// Servo channels 0..3: left yaw, left pitch, right yaw, right pitch.
// PCA channels 4/5 are STATIC active-low head forward/reverse buffer enables.
constexpr int ARM_CENTER_US[4] = {1500, 1500, 1500, 1500};
constexpr int ARM_DIRECTION[4] = {1, 1, -1, 1};
constexpr int ARM_US_PER_DEGREE = 10;
constexpr int ARM_MIN_US = 1200, ARM_MAX_US = 1800;
constexpr int HEAD_DIRECTION = 1;
// Wire both left wheels to rotate forward for IN1=HIGH; mirror wiring on right.
constexpr int LEFT_DIRECTION = 1, RIGHT_DIRECTION = 1;
constexpr float PACK_DIVIDER = 122.0f / 22.0f;
constexpr float PACK_ADC_CORRECTION = 1.0f;
constexpr float PACK_CUTOFF_V = 11.2f, PACK_REARM_V = 12.0f;
constexpr float PACK_PLAUSIBLE_MAX_V = 15.0f;
}
