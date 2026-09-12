// doorbot firmware for the LilyGO TTGO T-Display (ESP32).
//
// Hardware glue only: every behavioural decision lives in include/controller.h, which is
// compiled and tested on the host by firmware/test/test_controller.cpp.
//
// Boot order matters. Both VL53 boards answer on 0x29 out of reset, so they are held in
// reset by their XSHUT lines and brought up one at a time, the first moved to 0x2A. The bus
// is then scanned and the sketch refuses to run blind if either sensor is missing.

#include <Arduino.h>
#include <Wire.h>
#include <TFT_eSPI.h>
#include <Adafruit_VL53L1X.h>
#include <Adafruit_LIS3DH.h>
#include <Adafruit_Sensor.h>

#include "config.h"
#include "controller.h"

static TFT_eSPI tft;
static Adafruit_VL53L1X tof_wave(PIN_TOF_WAVE_XSHUT);
static Adafruit_VL53L1X tof_guard(PIN_TOF_GUARD_XSHUT);
static Adafruit_LIS3DH accel;
static doorbot::Controller controller;

static volatile int32_t encoder_edges = 0;
static volatile uint32_t impact_count = 0;
static uint32_t impact_seen = 0;
static bool sensors_ok = false;
static char fault_text[48] = "";

void IRAM_ATTR on_encoder() { encoder_edges++; }
void IRAM_ATTR on_impact() { impact_count++; }

// ---------------------------------------------------------------- motor
static void motor_apply(doorbot::Motor mode, uint16_t permille) {
    const uint32_t full = (1u << LEDC_BITS) - 1u;
    uint32_t duty = (uint32_t)((uint64_t)full * permille / 1000u);
    switch (mode) {
    case doorbot::Motor::Wind:
        ledcWrite(LEDC_CH_IN1, duty);
        ledcWrite(LEDC_CH_IN2, 0);
        break;
    case doorbot::Motor::Payout:
        ledcWrite(LEDC_CH_IN1, 0);
        ledcWrite(LEDC_CH_IN2, duty);
        break;
    case doorbot::Motor::Brake:
        ledcWrite(LEDC_CH_IN1, full);
        ledcWrite(LEDC_CH_IN2, full);
        break;
    case doorbot::Motor::Coast:
    default:
        ledcWrite(LEDC_CH_IN1, 0);
        ledcWrite(LEDC_CH_IN2, 0);
        break;
    }
    digitalWrite(PIN_MOTOR_SLEEP, mode == doorbot::Motor::Coast ? LOW : HIGH);
}

// ---------------------------------------------------------------- sensors
static bool bus_has(uint8_t addr) {
    Wire.beginTransmission(addr);
    return Wire.endTransmission() == 0;
}

static bool start_sensors() {
    pinMode(PIN_TOF_WAVE_XSHUT, OUTPUT);
    pinMode(PIN_TOF_GUARD_XSHUT, OUTPUT);
    digitalWrite(PIN_TOF_WAVE_XSHUT, LOW);
    digitalWrite(PIN_TOF_GUARD_XSHUT, LOW);
    delay(10);

    digitalWrite(PIN_TOF_WAVE_XSHUT, HIGH);
    delay(20);
    if (!tof_wave.begin(0x29, &Wire)) {
        snprintf(fault_text, sizeof fault_text, "wave ToF not found");
        return false;
    }
    if (!tof_wave.VL53L1X_SetI2CAddress(ADDR_TOF_WAVE << 1)) {
        snprintf(fault_text, sizeof fault_text, "wave ToF address move failed");
        return false;
    }
    tof_wave.VL53L1X_SetDistanceMode(1);          // short: best at the 20-250 mm window
    tof_wave.setTimingBudget(20);
    tof_wave.startRanging();

    digitalWrite(PIN_TOF_GUARD_XSHUT, HIGH);
    delay(20);
    if (!tof_guard.begin(ADDR_TOF_GUARD, &Wire)) {
        snprintf(fault_text, sizeof fault_text, "guard ToF not found");
        return false;
    }
    tof_guard.VL53L1X_SetDistanceMode(2);         // medium: covers the 1.8 m doorway
    tof_guard.setTimingBudget(33);
    tof_guard.startRanging();

    if (!bus_has(ADDR_TOF_WAVE) || !bus_has(ADDR_TOF_GUARD)) {
        snprintf(fault_text, sizeof fault_text, "ToF addresses 0x2A/0x29 missing");
        return false;
    }
    if (!accel.begin(ADDR_ACCEL)) {
        snprintf(fault_text, sizeof fault_text, "LIS3DH not found");
        return false;
    }
    accel.setRange(LIS3DH_RANGE_8_G);
    accel.setDataRate(LIS3DH_DATARATE_400_HZ);
    // One click, high-passed so gravity and a slowly swinging door do not reach the
    // comparator. The threshold is a starting register value: no published figure exists for
    // what a kick delivers to a jamb, so docs/commissioning.md calibrates it on the door.
    accel.setClick(1, 40, 10, 20, 255);
    pinMode(PIN_ACCEL_INT, INPUT);
    attachInterrupt(PIN_ACCEL_INT, on_impact, RISING);
    return true;
}

// ---------------------------------------------------------------- display
static void draw(const doorbot::Outputs &o, uint16_t wave_mm, uint16_t guard_mm) {
    static doorbot::State last = doorbot::State::Fault;
    static uint32_t last_ms = 0;
    if (o.state == last && millis() - last_ms < 250) return;
    last = o.state;
    last_ms = millis();

    uint16_t colour = TFT_DARKGREY;
    switch (o.state) {
    case doorbot::State::Shut: colour = TFT_DARKGREEN; break;
    case doorbot::State::Closing: colour = TFT_BLUE; break;
    case doorbot::State::Blocked: colour = TFT_ORANGE; break;
    case doorbot::State::Alert: colour = TFT_RED; break;
    case doorbot::State::Fault: colour = TFT_MAROON; break;
    default: break;
    }
    tft.fillScreen(TFT_BLACK);
    tft.fillRect(0, 0, 135, 34, colour);
    tft.setTextColor(TFT_WHITE, colour);
    tft.setTextDatum(TL_DATUM);
    tft.drawString(doorbot::state_name(o.state), 6, 8, 4);
    tft.setTextColor(TFT_WHITE, TFT_BLACK);
    tft.drawString(o.reason, 4, 42, 2);
    char line[40];
    snprintf(line, sizeof line, "door %3d deg", (int)o.door_deg_estimate);
    tft.drawString(line, 4, 70, 2);
    snprintf(line, sizeof line, "cable %5.1f mm", o.cable_mm);
    tft.drawString(line, 4, 92, 2);
    snprintf(line, sizeof line, "hand %4u mm", wave_mm);
    tft.drawString(line, 4, 122, 2);
    snprintf(line, sizeof line, "way  %4u mm", guard_mm);
    tft.drawString(line, 4, 144, 2);
    if (o.retries) {
        snprintf(line, sizeof line, "retry %u of 3", o.retries);
        tft.setTextColor(TFT_ORANGE, TFT_BLACK);
        tft.drawString(line, 4, 174, 2);
    }
    if (o.state == doorbot::State::Alert) {
        tft.setTextColor(TFT_RED, TFT_BLACK);
        tft.drawString("CLEAR THE WAY", 4, 200, 2);
    }
    if (fault_text[0]) {
        tft.setTextColor(TFT_YELLOW, TFT_BLACK);
        tft.drawString(fault_text, 4, 220, 1);
    }
}

// ---------------------------------------------------------------- setup / loop
void setup() {
    Serial.begin(115200);
    pinMode(PIN_MOTOR_SLEEP, OUTPUT);
    digitalWrite(PIN_MOTOR_SLEEP, LOW);
    ledcSetup(LEDC_CH_IN1, LEDC_FREQ, LEDC_BITS);
    ledcSetup(LEDC_CH_IN2, LEDC_FREQ, LEDC_BITS);
    ledcAttachPin(PIN_MOTOR_IN1, LEDC_CH_IN1);
    ledcAttachPin(PIN_MOTOR_IN2, LEDC_CH_IN2);
    motor_apply(doorbot::Motor::Coast, 0);

    pinMode(PIN_BUZZER, OUTPUT);
    digitalWrite(PIN_BUZZER, LOW);
    pinMode(PIN_BUTTON_TOP, INPUT_PULLUP);
    pinMode(PIN_MOTOR_FAULT, INPUT);
    pinMode(PIN_ENCODER, INPUT);
    attachInterrupt(PIN_ENCODER, on_encoder, CHANGE);

    pinMode(PIN_TFT_BACKLIGHT, OUTPUT);
    digitalWrite(PIN_TFT_BACKLIGHT, HIGH);
    tft.init();
    tft.setRotation(0);
    tft.fillScreen(TFT_BLACK);
    tft.setTextColor(TFT_WHITE, TFT_BLACK);
    tft.drawString("doorbot", 6, 8, 4);

    Wire.begin(PIN_SDA, PIN_SCL, 400000);
    sensors_ok = start_sensors();
    controller.set_cable_mm_per_edge(CABLE_MM_PER_EDGE);
    controller.set_travel_mm(CABLE_TRAVEL_MM);
    Serial.printf("doorbot ready, sensors_ok=%d, %.4f mm of cable per encoder edge\n",
                  (int)sensors_ok, CABLE_MM_PER_EDGE);
}

void loop() {
    static uint32_t next = 0;
    uint32_t now = millis();
    if (now < next) return;
    next = now + 20;

    doorbot::Inputs in;
    in.now_ms = now;
    if (sensors_ok) {
        if (tof_wave.dataReady()) {
            int16_t d = tof_wave.distance();
            in.wave_mm = d > 0 ? (uint16_t)d : 0;
            tof_wave.clearInterrupt();
        }
        if (tof_guard.dataReady()) {
            int16_t d = tof_guard.distance();
            in.guard_mm = d > 0 ? (uint16_t)d : 0;
            tof_guard.clearInterrupt();
        }
    }
    uint32_t clicks = impact_count;
    in.impact = clicks != impact_seen;
    impact_seen = clicks;
    in.encoder_edges = encoder_edges;
    // nFAULT is active low and open drain; with no sensor bring-up there is nothing to drive
    // the motor anyway, so an unconfigured board reads as a fault rather than running.
    in.driver_fault = !sensors_ok || digitalRead(PIN_MOTOR_FAULT) == LOW;
    in.button = digitalRead(PIN_BUTTON_TOP) == LOW;

    doorbot::Outputs out = controller.update(in);
    motor_apply(out.motor, out.duty_permille);
    digitalWrite(PIN_BUZZER, out.buzzer ? HIGH : LOW);
    draw(out, in.wave_mm, in.guard_mm);

    static doorbot::State reported = doorbot::State::Fault;
    if (out.state != reported) {
        reported = out.state;
        Serial.printf("[%lu] %s: %s (cable %.1f mm, retries %u)\n", (unsigned long)now,
                      doorbot::state_name(out.state), out.reason, out.cable_mm, out.retries);
    }
}
