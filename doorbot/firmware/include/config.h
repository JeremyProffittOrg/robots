#pragma once
// doorbot hardware configuration. Pins come from the LilyGO T-Display schematic: the display
// owns GPIO 4, 5, 16, 18, 19 and 23; GPIO 6-11 are flash; GPIO 0, 2, 5, 12 and 15 are
// strapping pins and are left alone; GPIO 34-39 are input-only. Nothing below touches any of
// those except as an input.

// ---- I2C: two VL53 time-of-flight boards and one LIS3DH share one bus
#define PIN_SDA 21
#define PIN_SCL 22
#define PIN_TOF_WAVE_XSHUT 25   // VL53L4CD, hand-wave target
#define PIN_TOF_GUARD_XSHUT 26  // VL53L1X, doorway and closing path
#define PIN_ACCEL_INT 39        // LIS3DH INT1, input-only pin, push-pull source

#define ADDR_TOF_WAVE 0x2A      // moved off the shared 0x29 default at every boot
#define ADDR_TOF_GUARD 0x29
#define ADDR_ACCEL 0x18

// ---- DRV8833 motor driver (Adafruit 3297). Its two 0.2 ohm sense resistors chop each
// channel at 1.0 A in hardware, which is what caps cable tension at 151 N with no firmware
// in the loop.
#define PIN_MOTOR_IN1 32
#define PIN_MOTOR_IN2 33
#define PIN_MOTOR_SLEEP 27      // external 100k pulldown: asleep through reset and boot
#define PIN_MOTOR_FAULT 36      // nFAULT, input-only pin, needs the driver's own pull-up
#define LEDC_CH_IN1 0
#define LEDC_CH_IN2 1
#define LEDC_FREQ 20000         // above audible
#define LEDC_BITS 10

// ---- encoder: Adafruit 3782 wheel on the motor's free shaft, 3986 slot sensor
#define PIN_ENCODER 37          // input-only; the slot sensor drives it push-pull
#define ENCODER_SLOTS 20        // Adafruit 3782 has 20 slots

// ---- buzzer and the two T-Display buttons
#define PIN_BUZZER 17
#define PIN_BUTTON_TOP 35       // on-board, active low
#define PIN_BUTTON_BOTTOM 0     // on-board, active low, also a strapping pin: input only

// ---- display (T-Display ST7789 135x240); pins are set by build_flags in platformio.ini
#define PIN_TFT_BACKLIGHT 4

// ---- geometry needed at runtime, mirrored from cad/params.scad. scripts/verify.py asserts
// these still match that file, so the firmware cannot drift away from the mechanism.
#define GEAR_RATIO 12.0f        // (48/12) * (42/14)
#define DRUM_EFF_R_MM 3.1f      // groove bottom 2.5 plus half the 1.2 mm cable
#define CABLE_TRAVEL_MM 105.9f  // fully open to shut, from check_mechanism.py
#define ARM_MIN_MM 41.6f
#define DOOR_OPEN_DEG 90.0f

// Millimetres of cable per encoder edge: one motor turn is 2 * pi * r / ratio of cable.
#define CABLE_MM_PER_EDGE (2.0f * 3.14159265f * DRUM_EFF_R_MM / (GEAR_RATIO * ENCODER_SLOTS))
