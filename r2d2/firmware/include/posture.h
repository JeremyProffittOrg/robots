#pragma once
#include <stdint.h>
#include <math.h>

namespace r2 {
constexpr float POST_MIN_MM=5.03832f;
constexpr float POST_MAX_MM=72.0f;
inline float pitchDegrees(float s){
 const float alpha=35*.01745329252f,L=150+s,A=40+L*sinf(alpha),B=150+L*cosf(alpha);
 return (atan2f(A,B)-acosf(277/sqrtf(A*A+B*B)))*57.29577951f;
}
inline float rearOffset(float s){
 const float a=35*.01745329252f,L=150+s,A=40+L*sinf(a),B=150+L*cosf(a);
 return sqrtf(A*A+B*B-277*277);
}
inline float steeringServoDegrees(float yawDegrees){
 // Metal linkage: fixed guide point(-30,0), foot servo(-30,-60),12mm crank.
 const float a=yawDegrees*.01745329252f;
 const float x=30-30*cosf(a),y=60+30*sinf(a),d=sqrtf(x*x+y*y);
 float cosine=(d*d+144-3744)/(24*d);
 cosine=fmaxf(-1,fminf(1,cosine));
 return (atan2f(y,x)+acosf(cosine))*57.29577951f-180;
}
class Posture {
 public:
 bool moving=false,fault=false;
 int output=0;
 uint32_t restUntil=0;
 const char *reason="ready";
 private:
 bool released=true,overload=false,resting=false;
 uint32_t start=0,progressAt=0,overloadAt=0;
 float target=POST_MIN_MM,progressPosition=0;
 void halt(uint32_t now){
  if(moving){restUntil=now+4*(uint32_t)(now-start);resting=true;} // >=80% off-time
  moving=false;output=0;
 }
 void fail(uint32_t now,const char *why){halt(now);fault=true;reason=why;}
 public:
 int tick(uint32_t now,bool enabled,int request,float mm,float amps,bool sensorOkay){
  if(fault){output=0;return 0;}
  if(!sensorOkay||!isfinite(mm)||!isfinite(amps)||mm<1.5f||mm>85.0f){fail(now,"feedback fault");return 0;}
  if(!enabled||request<0){halt(now);released=true;reason="stopped";return 0;}
  if(request>100){fail(now,"invalid posture");return 0;}
  if(!moving){
   if(!released){output=0;return 0;}
   released=false;
   if(resting&&(int32_t)(now-restUntil)<0){reason="cooldown; release and press again";return 0;}
   resting=false;
   target=POST_MIN_MM+(POST_MAX_MM-POST_MIN_MM)*request/100.0f;
   if(fabsf(target-mm)<=.6f){reason="position reached";return 0;}
   start=progressAt=now;progressPosition=mm;moving=true;overload=false;
  }
  const float wanted=POST_MIN_MM+(POST_MAX_MM-POST_MIN_MM)*request/100.0f;
  if(fabsf(wanted-target)>.01f){halt(now);reason="release before reversing posture";return 0;}
  if(now-start>=30000){fail(now,"travel timeout");return 0;}
  if(fabsf(mm-progressPosition)>=.15f){progressAt=now;progressPosition=mm;}
  if(now-progressAt>=750){fail(now,"post not moving");return 0;}
  if(fabsf(amps)>.75f){if(!overload){overload=true;overloadAt=now;}else if(now-overloadAt>=200){fail(now,"post overcurrent");return 0;}}
  else overload=false;
  if(fabsf(target-mm)<=.6f){halt(now);reason="position reached";return 0;}
  if((target>mm&&mm>=POST_MAX_MM+.7f)||(target<mm&&mm<=POST_MIN_MM-.7f)){fail(now,"travel envelope");return 0;}
  output=target>mm?255:-255;reason="moving";return output;
 }
};
}
