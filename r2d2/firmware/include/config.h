#pragma once
namespace pins {
constexpr int MOTOR[6]={14,32,15,33,27,12}; // left F/R, right F/R, rear F/R
constexpr int SLEEP=13, STEER=25, HEAD=26, FAULT=36, POWER=39, PACK=34;
constexpr int HEAD_REVERSE=17, POST_EXTEND=4, POST_RETRACT=16;
constexpr int SDA=21, SCL=22;
constexpr int BCLK=18, LRCLK=19, AUDIO=23;
}
namespace calibration {
constexpr int DIRECTION[3]={1,1,1}; // lift robot; change after wheel-direction test
constexpr int HEAD_LIMIT=70; // DC friction-wheel head motor, separate bridge
constexpr float STEER_US_PER_DEGREE=5.55556f; // degrees of servo horn, calibrated on bench
constexpr int STEER_CENTER_US=1500;
constexpr float POST_ADC_ZERO=0.0f, POST_ADC_FULL=26400.0f; // measure detached actuator endpoints before installation
constexpr float PACK_SCALE=122.0f/22.0f, PACK_CORRECTION=1.0f;
constexpr float CUTOFF=11.2f, REARM=12.0f, MAX_PACK=15.2f;
}
