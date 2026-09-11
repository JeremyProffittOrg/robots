#include "control.h"
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
 for(int speed=-100;speed<=100;speed+=5)for(int turn=-100;turn<=100;turn+=5){Command n;n.speed=speed;n.turn=turn;auto m=mix(n);assert(abs(m.left)<=LIMIT&&abs(m.right)<=LIMIT&&abs(m.rear)<=LIMIT);assert(fabs(m.angle)<=25);if(!speed)assert(!m.left&&!m.right&&!m.rear);if(speed>0)assert(m.left>=0&&m.right>=0&&m.rear>=0);}
 Command n;n.speed=100;n.turn=100;auto m=mix(n);assert(m.left>m.right&&m.rear>m.right);
 Ramp ramp;for(int t=0;t<100;t+=10)ramp.tick(100,t);assert(ramp.value==30);for(int t=100;t<200;t+=10)assert(ramp.tick(-100,t)>=0);assert(ramp.tick(-100,250)==0);assert(ramp.tick(-100,300)<0);
 puts("PASS: parsing, arming, stale leases, replay, timeout, fault, rollover, arc limits and reversal");}
