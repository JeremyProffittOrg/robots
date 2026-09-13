#pragma once
// Lease and reversal pattern adapted from the sibling Dalek controller.
#include <stdint.h>
#include <stdlib.h>
#include <errno.h>
#include <ctype.h>
#include <math.h>
namespace r2 {
struct PhEnOutput { int direction; unsigned duty; };
// Keep direction history through deadman stops. The board brakes when EN is low.
class PhEnDrive {
 public:
 PhEnOutput output{0,0};
 PhEnOutput tick(int percent,uint32_t now) {
  int wanted=percent>0?1:percent<0?-1:0;
  if(!wanted || (output.direction && wanted!=output.direction)) {
   if(output.duty){output.duty=0;offSince=now;}
   if(!wanted || uint32_t(now-offSince)<100)return output;
  }
  output.direction=wanted;
  unsigned magnitude=unsigned(abs(percent));if(magnitude>100)magnitude=100;
  output.duty=(magnitude*255U+50U)/100U;
  return output;
 }
 private:
 uint32_t offSince=0;
};
constexpr int LIMIT=90; // conservative commissioning duty ceiling, percent
constexpr uint32_t DEADMAN=500; // command heartbeat lease, ms
constexpr float SIDE_FOOT_X_MM=165.0f;
// stance: -1 no request, 2 hold for two-foot stance, 3 hold for three-foot stance.
struct Command {int speed=0,turn=0,head=0,stance=-1;};
inline bool parse(const char *s,long lo,long hi,long &v){
 if(!s||!*s||isspace((unsigned char)*s))return false;
 errno=0;char *end;v=strtol(s,&end,10);return !errno&&!*end&&v>=lo&&v<=hi;
}
inline bool validStance(long s){return s==-1||s==2||s==3;}
inline bool valid(const Command &c){
 return abs(c.speed)<=100&&abs(c.turn)<=100&&abs(c.head)<=100&&validStance(c.stance)&&(c.stance<0||(!c.speed&&!c.turn&&!c.head));
}
struct Mix {int left,right,center;float yaw;};
// Centre foot is in front of the side feet in revision D. turn>0 turns right: left side runs
// faster and the centre foot yaws right (negative yaw). offset is the forward distance, mm.
inline Mix mix(const Command &c,float offset){
 float a=c.turn*.08f,rad=a*.01745329252f;
 float v=c.speed*LIMIT/100.0f;
 float l=v*(1+tanf(rad)*SIDE_FOOT_X_MM/offset),r=v*(1-tanf(rad)*SIDE_FOOT_X_MM/offset),b=v/cosf(rad);
 float peak=fmaxf(fabsf(l),fmaxf(fabsf(r),fabsf(b)));
 float scale=peak>LIMIT?LIMIT/peak:1;
 return {(int)lroundf(l*scale),(int)lroundf(r*scale),(int)lroundf(b*scale),-a};
}
class Controller {public:
 bool armed=false;uint32_t lease=0,sequence=0,last=0;Command command;
 void stop(){armed=false;lease=0;command=Command{};}
 void tick(uint32_t now,bool healthy){if(!healthy||(armed&&uint32_t(now-last)>=DEADMAN))stop();}
 bool fresh(uint32_t now)const{return armed&&uint32_t(now-last)<DEADMAN;}
 bool arm(uint32_t now,uint32_t token,bool healthy){if(armed||!healthy||!token)return false;armed=true;lease=token;last=now;sequence=0;command=Command{};return true;}
 bool accept(uint32_t now,uint32_t token,uint32_t seq,Command next,bool healthy){tick(now,healthy);if(!armed||token!=lease||seq<=sequence||!valid(next))return false;command=next;sequence=seq;last=now;return true;}
};
class Ramp{public:int value=0;uint32_t until=0;bool holding=false;
 int tick(int target,uint32_t now){if(holding){if(int32_t(now-until)<0)return 0;holding=false;}
 bool reverse=(value>0&&target<0)||(value<0&&target>0);int next=reverse?0:target;
 if(value<next)value+=(next-value>3?3:next-value);
 if(value>next)value-=(value-next>3?3:value-next);
 if(reverse&&value==0){holding=true;until=now+100;}return value;}
 void stop(){value=0;holding=false;}
};
}
