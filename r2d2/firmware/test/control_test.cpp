#include "control.h"
#include "posture.h"
#include <assert.h>
#include <stdio.h>
#include <initializer_list>
int main(){using namespace r2;long v;
 for(const char*s:{""," 1","1x","nan","101","99999999999999999999"})assert(!parse(s,-100,100,v));
 Controller c;Command moving;moving.speed=75;
 assert(!c.accept(0,1,1,moving,true));assert(!c.arm(0,1,false));assert(c.arm(100,1,true));
 assert(c.accept(110,1,1,moving,true));assert(!c.accept(111,1,1,moving,true));
 assert(!c.accept(112,2,2,moving,true));assert(!c.accept(610,1,2,moving,true));assert(!c.armed);
 assert(c.arm(700,2,true));assert(!c.accept(701,1,3,moving,true));c.tick(702,false);assert(!c.armed);
 assert(c.arm(0xfffffff0,3,true));c.tick(0x100,true);assert(c.armed);c.tick(0x1e4,true);assert(!c.armed);
 const float offset=centerFootOffsetMm(100);
 for(int speed=-100;speed<=100;speed+=5)for(int turn=-100;turn<=100;turn+=5){Command n;n.speed=speed;n.turn=turn;auto m=mix(n,offset);assert(abs(m.left)<=LIMIT&&abs(m.right)<=LIMIT&&abs(m.center)<=LIMIT);assert(fabs(m.yaw)<=8.01f);if(!speed)assert(!m.left&&!m.right&&!m.center);if(speed>0)assert(m.left>=0&&m.right>=0&&m.center>=0);}
 Command n;n.speed=100;n.turn=100;auto m=mix(n,offset);assert(m.left>m.right&&m.center>m.right&&m.yaw<0);
 Ramp ramp;for(int t=0;t<100;t+=10)ramp.tick(100,t);assert(ramp.value==30);for(int t=100;t<200;t+=10)assert(ramp.tick(-100,t)>=0);assert(ramp.tick(-100,250)==0);assert(ramp.tick(-100,300)<0);
 for(int y=-8;y<=8;y++){assert(fabsf(steeringServoDegrees(y))<25);}
 assert(fabsf(postContactMm()-36.647f)<.01f&&centerFootOffsetMm(0)>90);
 puts("PASS: lease/replay/timeout/fault, drive limits, front centre-foot mixing, ramp reversal and linkage geometry");}
