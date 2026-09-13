#pragma once
// Sensor conditioning shared by firmware and host tests. No Arduino headers.
#include <stdint.h>
#include <math.h>

namespace r2 {

// Actuonix P16 potentiometer: yellow ref+ through R_POT_TOP to 3.3 V, orange ref- through1k to GND,
// purple wiper to an ADC1 pin with a 470k pulldown. An open wiper or open ref+ reads near 0 mV;
// an open ref- reads near 3.3 V. Both fall outside the valid window.
struct PotCalibration { float zeroMv, fullMv, strokeMm, minValidMv, maxValidMv; bool commissioned; };

inline bool potPosition(float mv, const PotCalibration &c, float &mm) {
 if (!c.commissioned || !isfinite(mv) || c.fullMv <= c.zeroMv || mv < c.minValidMv || mv > c.maxValidMv) return false;
 mm = (mv - c.zeroMv) * c.strokeMm / (c.fullMv - c.zeroMv);
 return true;
}

// Omron SS-01GL SPDT lock switch: COM to GND, NO and NC each to a pulled-up GPIO.
// Exactly one contact closed is a legal reading. Both open (broken COM or wire) or both
// closed (short) is invalid once it persists longer than a normal changeover.
class ContactPair {
 public:
 ContactPair(uint32_t legalMs, uint32_t illegalMs) : legalMs_(legalMs), illegalMs_(illegalMs) {}
 bool valid = false, engaged = false;
 bool settled() const { return decided; }
 void update(uint32_t now, bool noClosed, bool ncClosed) {
  uint8_t code = uint8_t((noClosed ? 1 : 0) | (ncClosed ? 2 : 0));
  if (!primed || code != candidate) { primed = true; candidate = code; since = now; }
  bool legal = candidate == 1 || candidate == 2;
  if (uint32_t(now - since) >= (legal ? legalMs_ : illegalMs_)) {
   valid = legal;
   engaged = candidate == 1;
   decided = true;
  }
 }
 private:
 uint32_t legalMs_, illegalMs_, since = 0;
 uint8_t candidate = 0;
 bool primed = false, decided = false;
};

}
