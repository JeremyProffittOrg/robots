#include <Arduino.h>
#include <WiFi.h>
#include <WebServer.h>
#include <Preferences.h>
#include <LittleFS.h>
#include <Wire.h>
#include <TFT_eSPI.h>
#include <Adafruit_PWMServoDriver.h>
#include <AudioFileSourceLittleFS.h>
#include <AudioGeneratorMP3.h>
#include <AudioOutputI2S.h>
#include <esp_task_wdt.h>
#include <math.h>
#include "config.h"
#include "control.h"

WebServer server(80);
Preferences preferences;
TFT_eSPI display;
Adafruit_PWMServoDriver servos(0x40);
AudioGeneratorMP3 mp3;
AudioFileSourceLittleFS audioFile;
AudioOutputI2S audioOutput;
dalek::Controller controller;
portMUX_TYPE stateMutex = portMUX_INITIALIZER_UNLOCKED;
String apName, accessKey, sessionToken;
bool filesystemReady = false;
bool servoReady = false, actuatorPower = false, batteryReady = false, controlTaskReady = false;
float packVolts = 0;
String playing;

String randomText(size_t length) {
  const char alphabet[] = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789";
  String value;
  value.reserve(length);
  for (size_t i = 0; i < length; ++i) value += alphabet[esp_random() % 32];
  return value;
}

bool healthyLocked() { return servoReady && actuatorPower && batteryReady && controlTaskReady; }

void disarm() {
  portENTER_CRITICAL(&stateMutex);
  controller.stop();
  portEXIT_CRITICAL(&stateMutex);
}

void motorWrite(int forwardChannel, int reverseChannel, int value) {
  // Make inactive input low before enabling the other input; no dynamic braking.
  if (value > 0) { ledcWrite(reverseChannel, 0); ledcWrite(forwardChannel, value); }
  else { ledcWrite(forwardChannel, 0); ledcWrite(reverseChannel, -value); }
}

bool servoPulse(uint8_t channel, int microseconds) {
  return servos.setPWM(channel, 0, static_cast<uint16_t>(microseconds * 4096UL / 20000UL)) == 0;
}

bool headWrite(int value) {
  static int selectedDirection = 2; // Force both gates disabled on first call.
  const int direction = value > 0 ? 1 : value < 0 ? -1 : 0;
  if (direction != selectedDirection) {
    ledcWrite(4, 0); // Remove energy BEFORE any I2C direction change.
    // U9 /OE pins: PCA full-on = disabled; full-off = enabled.
    if (servos.setPWM(4, 4096, 0) != 0 || servos.setPWM(5, 4096, 0) != 0) return false;
    if (direction && servos.setPWM(direction > 0 ? 4 : 5, 0, 4096) != 0) return false;
    selectedDirection = direction;
  }
  ledcWrite(4, abs(value));
  return true;
}

void motionFault() {
  ledcWrite(4, 0);
  digitalWrite(pins::MOTOR_SLEEP, LOW);
  digitalWrite(pins::SERVO_OE, HIGH);
  motorWrite(0, 1, 0); motorWrite(2, 3, 0);
  portENTER_CRITICAL(&stateMutex);
  servoReady = false; // Latched I2C fault: fix wiring and reboot.
  controller.stop();
  portEXIT_CRITICAL(&stateMutex);
}

void motionTask(void *) {
  esp_task_wdt_add(nullptr);
  dalek::Ramp left, right;
  dalek::HeadMotor head;
  TickType_t wake = xTaskGetTickCount();
  uint32_t lastBattery = 0, lowSince = 0, lastServo = 0;
  bool lowTiming = false, batteryInitialized = false;
  float filteredBattery = 0, phase = 0;
  portENTER_CRITICAL(&stateMutex);
  controlTaskReady = true;
  portEXIT_CRITICAL(&stateMutex);
  for (;;) {
    const uint32_t now = millis();
    bool powered = digitalRead(pins::ACTUATOR_POWER) == HIGH;
    const bool rearButtonReleased = digitalRead(pins::BUTTON) == HIGH;
    if (now - lastBattery >= 100) {
      lastBattery = now;
      const float sample = analogReadMilliVolts(pins::PACK_ADC) * 0.001f *
                           calibration::PACK_DIVIDER * calibration::PACK_ADC_CORRECTION;
      filteredBattery = batteryInitialized ? filteredBattery * 0.8f + sample * 0.2f : sample;
      batteryInitialized = true;
      if (filteredBattery < calibration::PACK_CUTOFF_V) {
        if (!lowTiming) { lowSince = now; lowTiming = true; }
      } else lowTiming = false;
      portENTER_CRITICAL(&stateMutex);
      packVolts = filteredBattery;
      if (filteredBattery > calibration::PACK_PLAUSIBLE_MAX_V || sample < 1.0f ||
          (lowTiming && now - lowSince >= 1000)) batteryReady = false;
      else if (filteredBattery >= calibration::PACK_REARM_V &&
               filteredBattery <= calibration::PACK_PLAUSIBLE_MAX_V) batteryReady = true;
      portEXIT_CRITICAL(&stateMutex);
    }

    portENTER_CRITICAL(&stateMutex);
    actuatorPower = powered;
    controller.tick(now, healthyLocked() && rearButtonReleased);
    const bool armed = controller.armed;
    const dalek::Command command = controller.command;
    const bool i2cOkay = servoReady;
    portEXIT_CRITICAL(&stateMutex);

    if (!armed) {
      ledcWrite(4, 0);
      digitalWrite(pins::MOTOR_SLEEP, LOW);
      digitalWrite(pins::SERVO_OE, HIGH);
      motorWrite(0, 1, 0); motorWrite(2, 3, 0);
      left.stop(); right.stop(); head.stop(now); phase = 0;
    } else {
      motorWrite(0, 1, left.tick(command.left, now) * calibration::LEFT_DIRECTION);
      motorWrite(2, 3, right.tick(command.right, now) * calibration::RIGHT_DIRECTION);
      if (!headWrite(head.tick(command.head, now, true) * calibration::HEAD_DIRECTION)) {
        head.stop(now); motionFault();
        esp_task_wdt_reset();
        vTaskDelayUntil(&wake, pdMS_TO_TICKS(10));
        continue;
      }
      digitalWrite(pins::MOTOR_SLEEP, HIGH);
    }

    if (i2cOkay && now - lastServo >= 20) {
      const float dt = (now - lastServo) * 0.001f;
      lastServo = now;
      if (armed && command.arms) phase = fmodf(phase + dt * (command.frequency * 0.01f) * 2.0f * PI, 2.0f * PI);
      float offsets[4] = {sinf(phase), cosf(phase), sinf(phase + PI), cosf(phase + PI)};
      bool okay = true;
      for (uint8_t channel = 0; channel < 4; ++channel) {
        if (!armed) {
          if (servos.setPWM(channel, 0, 4096) != 0) { okay = false; break; }
          continue;
        }
        int offset = armed && command.arms ? lroundf(offsets[channel] * command.radius * calibration::ARM_US_PER_DEGREE) : 0;
        int pulse = calibration::ARM_CENTER_US[channel] + calibration::ARM_DIRECTION[channel] * offset;
        pulse = constrain(pulse, calibration::ARM_MIN_US, calibration::ARM_MAX_US);
        if (!servoPulse(channel, pulse)) { okay = false; break; }
      }
      if (!okay) {
        head.stop(now); motionFault();
      } else if (armed) digitalWrite(pins::SERVO_OE, LOW);
    }
    esp_task_wdt_reset();
    vTaskDelayUntil(&wake, pdMS_TO_TICKS(10));
  }
}

void reply(int code, const String &body) {
  server.sendHeader("Cache-Control", "no-store");
  server.send(code, "application/json", body);
}

bool authorized() {
  if (server.header("X-Dalek-Token") == sessionToken) return true;
  reply(401, "{\"error\":\"Enter the access key shown on the rear display\"}");
  return false;
}

bool number(const char *name, long low, long high, long &value) {
  return server.hasArg(name) && dalek::parseInteger(server.arg(name).c_str(), low, high, value);
}

bool soundName(const String &name) {
  if (name.length() < 5 || name.length() > 48 || !name.endsWith(".mp3")) return false;
  for (unsigned int i = 0; i < name.length() - 4; ++i) {
    char c = name[i];
    if (!((c >= 'a' && c <= 'z') || (c >= '0' && c <= '9') || c == '_' || c == '-')) return false;
  }
  return true;
}

void stopSound() {
  if (mp3.isRunning()) mp3.stop();
  audioFile.close();
  playing = "";
}

void routes() {
  const char *headers[] = {"X-Dalek-Token"};
  server.collectHeaders(headers, 1);
  server.on("/api/login", HTTP_POST, [] {
    static uint32_t lastAttempt = 0;
    if (millis() - lastAttempt < 1000) { reply(429, "{\"error\":\"Wait one second\"}"); return; }
    lastAttempt = millis();
    if (server.arg("key") != accessKey) { reply(401, "{\"error\":\"Incorrect display key\"}"); return; }
    reply(200, "{\"token\":\"" + sessionToken + "\"}");
  });
  server.on("/api/status", HTTP_GET, [] {
    if (!authorized()) return;
    portENTER_CRITICAL(&stateMutex);
    bool armed = controller.armed, ready = healthyLocked(), i2c = servoReady, power = actuatorPower, battery = batteryReady;
    float volts = packVolts;
    portEXIT_CRITICAL(&stateMutex);
    String body = "{\"armed\":" + String(armed ? "true" : "false") + ",\"ready\":" + String(ready ? "true" : "false");
    body += ",\"i2c\":" + String(i2c ? "true" : "false") + ",\"power\":" + String(power ? "true" : "false");
    body += ",\"battery\":" + String(battery ? "true" : "false") + ",\"volts\":" + String(volts, 2);
    body += ",\"station\":\"" + (WiFi.status() == WL_CONNECTED ? WiFi.localIP().toString() : "offline") + "\"";
    body += ",\"ap\":\"" + WiFi.softAPIP().toString() + "\",\"filesystem\":" + String(filesystemReady ? "true" : "false");
    body += ",\"playing\":\"" + playing + "\"}";
    reply(200, body);
  });
  server.on("/api/arm", HTTP_POST, [] {
    if (!authorized()) return;
    uint32_t lease = (esp_random() & 0x7fffffff) | 1;
    portENTER_CRITICAL(&stateMutex);
    bool okay = controller.arm(millis(), lease, healthyLocked());
    portEXIT_CRITICAL(&stateMutex);
    if (!okay) { reply(409, "{\"error\":\"Not ready or already armed. Check stop switch, battery and PCA9685\"}"); return; }
    reply(200, "{\"lease\":" + String(lease) + "}");
  });
  server.on("/api/stop", HTTP_POST, [] {
    if (!authorized()) return;
    disarm();
    reply(200, "{\"ok\":true}");
  });
  server.on("/api/command", HTTP_POST, [] {
    if (!authorized()) return;
    long lease, sequence, left, right, head, arms, radius, frequency;
    bool parsed = number("lease", 1, 0x7fffffffL, lease) && number("sequence", 1, 0x7fffffffL, sequence) &&
      number("left", -dalek::DRIVE_LIMIT, dalek::DRIVE_LIMIT, left) && number("right", -dalek::DRIVE_LIMIT, dalek::DRIVE_LIMIT, right) &&
      number("head", -100, 100, head) && number("arms", 0, 1, arms) && number("radius", 0, 12, radius) && number("frequency", 10, 80, frequency);
    if (!parsed || server.args() != 8) { disarm(); reply(400, "{\"error\":\"Invalid complete command; disarmed\"}"); return; }
    dalek::Command command;
    command.left = left; command.right = right; command.head = head;
    command.arms = arms; command.radius = radius; command.frequency = frequency;
    portENTER_CRITICAL(&stateMutex);
    bool okay = controller.accept(millis(), lease, sequence, command, healthyLocked());
    portEXIT_CRITICAL(&stateMutex);
    if (!okay) { reply(409, "{\"error\":\"Expired or invalid command lease; release controls and arm again\"}"); return; }
    reply(200, "{\"ok\":true}");
  });
  server.on("/api/sounds", HTTP_GET, [] {
    if (!authorized()) return;
    String body = "[";
    File directory = LittleFS.open("/audio");
    bool first = true;
    if (directory && directory.isDirectory()) {
      File file = directory.openNextFile();
      while (file) {
        String name = file.name();
        name = name.substring(name.lastIndexOf('/') + 1);
        if (!file.isDirectory() && soundName(name)) {
          if (!first) body += ",";
          body += "\"" + name + "\"";
          first = false;
        }
        file = directory.openNextFile();
      }
    }
    reply(200, body + "]");
  });
  server.on("/api/sound", HTTP_POST, [] {
    if (!authorized()) return;
    String name = server.arg("name");
    if (!filesystemReady || !soundName(name) || !LittleFS.exists("/audio/" + name)) { reply(404, "{\"error\":\"MP3 file not found\"}"); return; }
    stopSound();
    String path = "/audio/" + name;
    if (!audioFile.open(path.c_str()) || !mp3.begin(&audioFile, &audioOutput)) { stopSound(); reply(500, "{\"error\":\"MP3 decoder could not start\"}"); return; }
    playing = name;
    reply(200, "{\"ok\":true}");
  });
  server.on("/api/silence", HTTP_POST, [] { if (!authorized()) return; stopSound(); reply(200, "{\"ok\":true}"); });
  server.on("/api/wifi", HTTP_POST, [] {
    if (!authorized()) return;
    String ssid = server.arg("ssid"), password = server.arg("password");
    if (ssid.length() < 1 || ssid.length() > 32 || password.length() < 8 || password.length() > 63) {
      reply(400, "{\"error\":\"Use a 1-32 byte SSID and an 8-63 byte WPA2 password\"}"); return;
    }
    disarm();
    preferences.putString("ssid", ssid);
    preferences.putString("stationpass", password);
    WiFi.disconnect(false, false);
    WiFi.begin(ssid.c_str(), password.c_str());
    reply(200, "{\"ok\":true,\"message\":\"Connecting. Setup AP remains available. Check rear display for station IP\"}");
  });
  server.on("/api/wifi/forget", HTTP_POST, [] {
    if (!authorized()) return;
    disarm();
    preferences.remove("ssid"); preferences.remove("stationpass");
    WiFi.disconnect(false, true);
    reply(200, "{\"ok\":true}");
  });
  server.on("/", HTTP_GET, [] {
    server.sendHeader("Cache-Control", "no-store");
    if (!filesystemReady || !LittleFS.exists("/index.html")) { server.send(503, "text/plain", "Upload LittleFS with: pio run -t uploadfs. Motion is disarmed."); return; }
    File file = LittleFS.open("/index.html", "r");
    server.streamFile(file, "text/html");
  });
  server.on("/app.js", HTTP_GET, [] {
    server.sendHeader("Cache-Control", "no-store");
    File file = LittleFS.open("/app.js", "r");
    if (!file) { server.send(404, "text/plain", "Missing app.js"); return; }
    server.streamFile(file, "application/javascript");
  });
  server.onNotFound([] { reply(404, "{\"error\":\"Unknown route\"}"); });
}

void drawStatus() {
  portENTER_CRITICAL(&stateMutex);
  bool armed = controller.armed, ready = healthyLocked(), power = actuatorPower, i2c = servoReady;
  float volts = packVolts;
  portEXIT_CRITICAL(&stateMutex);
  display.fillScreen(TFT_BLACK);
  display.setTextFont(2);
  display.setTextColor(TFT_WHITE, TFT_BLACK);
  display.setCursor(0, 0);
  display.println(armed ? "DALEK  ARMED" : ready ? "DALEK  READY / DISARMED" : "DALEK  INTERLOCK / DISARMED");
  display.println("AP: " + WiFi.softAPIP().toString());
  display.println("LAN: " + (WiFi.status() == WL_CONNECTED ? WiFi.localIP().toString() : "offline"));
  display.println(apName);
  display.println("Key: " + accessKey);
  display.printf("%.2f V   POWER %s   I2C %s\n", volts, power ? "ON" : "OFF", i2c ? "OK" : "FAULT");
  display.println("Rear button: STOP / hold 5s AP only");
}

void setup() {
  // External resistors hold these safe before setup and during reset.
  digitalWrite(pins::MOTOR_SLEEP, LOW); pinMode(pins::MOTOR_SLEEP, OUTPUT);
  digitalWrite(pins::SERVO_OE, HIGH); pinMode(pins::SERVO_OE, OUTPUT);
  const int motorPins[] = {pins::LEFT_FORWARD, pins::LEFT_REVERSE, pins::RIGHT_FORWARD, pins::RIGHT_REVERSE};
  for (int channel = 0; channel < 4; ++channel) {
    pinMode(motorPins[channel], OUTPUT); digitalWrite(motorPins[channel], LOW);
    ledcSetup(channel, 20000, 8); ledcAttachPin(motorPins[channel], channel); ledcWrite(channel, 0);
  }
  pinMode(pins::HEAD_PWM, OUTPUT); digitalWrite(pins::HEAD_PWM, LOW);
  ledcSetup(4, 20000, 8); ledcAttachPin(pins::HEAD_PWM, 4); ledcWrite(4, 0);
  pinMode(pins::ACTUATOR_POWER, INPUT); // External 10k/15k divider; no ESP32 internal pull available.
  pinMode(pins::BUTTON, INPUT_PULLUP);
  analogReadResolution(12); analogSetPinAttenuation(pins::PACK_ADC, ADC_11db);
  display.init(); display.setRotation(1);
  Wire.begin(pins::SDA, pins::SCL);
  Wire.setTimeOut(20);
  servoReady = servos.begin();
  if (servoReady) {
    servos.setOscillatorFrequency(25000000);
    servos.setPWMFreq(50);
    servos.setOutputMode(true);
    // MODE2 OUTDRV=1, OUTNE=10: OE HIGH makes every PCA output high-Z.
    // R7/R8 then disable BOTH active-low head gates, including before arming.
    // The library setter does not expose OUTNE or report its I2C result.
    Wire.beginTransmission(0x40); Wire.write(0x01); Wire.write(0x06);
    servoReady = Wire.endTransmission() == 0;
    if (servoReady) {
      Wire.beginTransmission(0x40); Wire.write(0x01);
      servoReady = Wire.endTransmission(false) == 0;
      servoReady = servoReady && Wire.requestFrom(uint8_t(0x40), uint8_t(1)) == 1;
      servoReady = servoReady && Wire.read() == 0x06;
    }
    for (int i = 0; i < 4; ++i) servoReady = servoPulse(i, calibration::ARM_CENTER_US[i]) && servoReady;
    servoReady = headWrite(0) && servoReady;
  }
  filesystemReady = LittleFS.begin(false); // Never erase files on a failed mount.
  preferences.begin("dalek", false);
  accessKey = preferences.getString("accesskey", "");
  if (accessKey.length() != 12) { accessKey = randomText(12); preferences.putString("accesskey", accessKey); }
  sessionToken = randomText(32);
  uint32_t suffix = static_cast<uint32_t>(ESP.getEfuseMac() >> 32);
  char device[24]; snprintf(device, sizeof(device), "DALEK-%04X", suffix & 0xffff);
  apName = device;
  WiFi.persistent(false);
  WiFi.onEvent([](WiFiEvent_t event, WiFiEventInfo_t) {
    if (event == ARDUINO_EVENT_WIFI_STA_DISCONNECTED || event == ARDUINO_EVENT_WIFI_AP_STADISCONNECTED) disarm();
  });
  WiFi.mode(WIFI_AP_STA);
  WiFi.setSleep(false);
  WiFi.softAP(apName.c_str(), accessKey.c_str(), 1, false, 2);
  WiFi.setAutoReconnect(true);
  String ssid = preferences.getString("ssid", ""), password = preferences.getString("stationpass", "");
  if (ssid.length()) WiFi.begin(ssid.c_str(), password.c_str());
  audioOutput.SetPinout(pins::I2S_BCLK, pins::I2S_LRC, pins::I2S_DATA);
  audioOutput.SetOutputModeMono(true);
  audioOutput.SetGain(0.28);
  esp_task_wdt_init(2, true);
  if (xTaskCreatePinnedToCore(motionTask, "motion", 6144, nullptr, 3, nullptr, 1) != pdPASS) {
    digitalWrite(pins::MOTOR_SLEEP, LOW); digitalWrite(pins::SERVO_OE, HIGH);
  }
  routes(); server.begin(); drawStatus();
}

void loop() {
  static uint32_t lastDisplay = 0, buttonSince = 0;
  static bool buttonWasDown = false, forgot = false;
  bool buttonDown = digitalRead(pins::BUTTON) == LOW;
  if (buttonDown) {
    disarm();
    if (!buttonWasDown) { buttonSince = millis(); forgot = false; }
    if (!forgot && millis() - buttonSince >= 5000) {
      preferences.remove("ssid"); preferences.remove("stationpass");
      WiFi.disconnect(false, true); forgot = true;
    }
  }
  buttonWasDown = buttonDown;
  server.handleClient();
  if (mp3.isRunning() && !mp3.loop()) stopSound();
  if (millis() - lastDisplay >= 750) { lastDisplay = millis(); drawStatus(); }
  delay(1);
}
