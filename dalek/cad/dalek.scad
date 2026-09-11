// DALEK-541, millimetres. Print parts are selected by -D 'part="..."'.
// Original CAD, 2026-09-11. Source dimensions and fit gates: docs/mechanical.md.
// World: +Y rear, +X right, Z up. Floor Z=0. Never scale fit-critical parts.
part = "assembly";
$fn = 64;
wall = 0.8;
clearance = 0.3;
M3 = 3.4;
function radius_at(a,b,h,z) = a+(b-a)*z/h;
module hole(d=M3,h=100) { cylinder(d=d,h=h,center=true,$fn=24); }
module slot(len=10,d=M3,h=100) { hull() for(x=[-len/2,len/2]) translate([x,0,0]) hole(d,h); }
module ring(ro,ri,h) { difference(){ cylinder(r=ro,h=h); translate([0,0,-.1]) cylinder(r=ri,h=h+.2); } }
module sector(ro,ri,h) { rotate_extrude(angle=90,convexity=8) translate([ri,0]) square([ro-ri,h]); }
module radial_hole(a,r,z,d=M3,tilt=0) { rotate([0,0,a]) translate([r,0,z]) rotate([0,90-tilt,0]) hole(d,50); }
module seam(a,b,h,flip=false) {
  translate([0,flip?0:2.4,0]) rotate([90,0,0]) linear_extrude(2.4)
    polygon([[a-14,0],[a,0],[b,h],[b-14,h]]);
}
module shell_quarter(a=180,b=145,h=90,domes=true) {
  difference(){
    union(){
      rotate_extrude(angle=90,convexity=8) polygon([[a-wall,0],[a,0],[b,h],[b-wall,h]]);
      seam(a,b,h); rotate([0,0,90]) seam(a,b,h,true);
      if(domes)sector(a,a-14,2); translate([0,0,h-2]) sector(b,b-14,2);
    }
    for(z=[h/4,h*3/4]) for(ang=[0,90]) rotate([0,0,ang])
      translate([radius_at(a,b,h,z)-10,0,z]) rotate([90,0,0]) hole(M3,14);
    for(ang=[15,45,75]) for(p=[[a-10,0],[b-10,h]]) rotate([0,0,ang]) translate([p[0],0,p[1]]) hole(M3,12);
    if(domes) for(ang=[15,45,75]) for(z=[23,67]) radial_hole(ang,radius_at(a,b,h,z),z,M3,atan((a-b)/h));
  }
}
module chassis_quarter(){
 difference(){
  sector(180,0,5);
  // Through pockets leave a connected 6mm rib grid and protected bolt bosses.
  difference(){
   intersection(){
    sector(172,17,6);
    union(){for(x=[20:30:170])for(y=[20:30:170])translate([x,y,2.5])cube([24,24,8],center=true);}
   }
   for(a=[15,45,75])rotate([0,0,a])translate([170,0,0])cylinder(r=7,h=10);
   for(x=[79,121])for(y=[10,24])translate([x,y,0]){cylinder(r=7.2,h=10);translate([-15,-3,0])cube([30,6,10]);}
   for(x=[45,70])for(y=[30,50])translate([x,y,0]){cylinder(r=7,h=10);translate([-15,-3,0])cube([30,6,10]);}
   translate([0,0,-1])cube([174,14,9]);translate([0,0,-1])cube([14,174,9]);
  }
  // Seam splice plates: common holes across each cut plane.
  for(a=[0,90]) rotate([0,0,a]) for(r=[30,75,150]) translate([r,a==0?8:-8,0]) hole();
  for(a=[15,45,75]) rotate([0,0,a]) translate([170,0,0]) hole();
  // Motor cradle (right-front or right-rear through reflection).
  for(x=[79,121]) for(y=[10,24]) translate([x,y,0]) hole();
  for(x=[45,70]) for(y=[30,50]) translate([x,y,0]) hole();
 }
}
module splice(){ difference(){ translate([-12,-12,0]) cube([24,24,3]); for(y=[-8,8]) translate([0,y,0]) hole(M3,10); } }
module motor_cradle(){
 difference(){
  union(){
   translate([-13,-38,0]) cube([26,76,3]);
   translate([-13,-38,0]) cube([26,3,26]);
   for(x=[-21,21]) for(y=[-30,-16]) {
    translate([x,y,0]) cylinder(d=9,h=55,$fn=24);
    hull(){ translate([x,y,0]) cylinder(d=9,h=3,$fn=24); translate([x<0?-12:12,y,0]) cylinder(d=8,h=3,$fn=24); }
   }
   // Low rails locate the body; output axles pass above them.
   for(x=[-13,11]) translate([x,-35,3]) cube([2,70,6]);
  }
  for(x=[-21,21]) for(y=[-30,-16]) translate([x,y,27]) hole(M3,70);
  for(y=[-22,0]) for(x=[-9,9]) translate([x,y,0]) cube([3.5,5,10],center=true);
 }
}
module battery_tray(){
 difference(){
  union(){ translate([-62,-40,0]) cube([124,80,3]);
   for(x=[-62,58]) translate([x,-40,0]) cube([4,80,15]);
   for(y=[-40,36]) translate([-62,y,0]) cube([124,4,15]);
  }
  // Clear pocket 116 x 72. Two 20mm straps; connector exits rear.
  for(x=[-35,35]) for(y=[-35,35]) translate([x,y,0]) cube([22,4,10],center=true);
  for(x=[-45,45]) for(y=[-30,30]) translate([x,y,0]) hole(M3,10);
  translate([0,38,12]) cube([36,8,20],center=true);
 }
}
module deck_post(){ difference(){ cylinder(d=9,h=95,$fn=32); hole(M3,200); } }
module electronics_deck(){
 difference(){ translate([-90,-60,0]) cube([180,120,3]);
  for(x=[-70,70]) for(y=[-50,50]) translate([x,y,0]) hole(M3,10);
  for(x=[-30,30])translate([x,-50,0])hole(M3,12);
  // Slots accept M2/M2.5/M3 standoffs or cable ties without PCB hole assumptions.
  for(x=[-75:15:75]) for(y=[-40:20:40]) translate([x,y,0]) slot(7,3.4,10);
  for(x=[-67.5:15:67.5])for(y=[-30,-10,10,30])translate([x,y,0])cube([10,10,10],center=true);
 }
}
module pcb_standoff(){ difference(){ cylinder(d=7,h=6,$fn=24); hole(2.8,20); } }
module shoulder_raw(){
 difference(){
  intersection(){ cylinder(r=120,h=110); translate([-130,-100,0]) cube([260,230,110]); }
  translate([0,0,-1]) intersection(){ cylinder(r=120-wall,h=112); translate([-130,-99.2,0]) cube([260,230,112]); }
 }
}
module shoulder_half(rear=false){
 difference(){
  union(){
   intersection(){ shoulder_raw(); translate([-125,rear?0:-125,0]) cube([250,125,110]); }
   intersection(){ union(){ring(120,rear?106:98,2); translate([0,0,108])ring(120,rear?106:98,2);} translate([-125,rear?0:-125,0])cube([250,125,110]); }
   for(x=[-1,1]) translate([x>0?106:-120,rear?0:-2.4,0]) cube([14,2.4,110]);
   if(!rear) for(x=[-43,43]) translate([x-22,-102,8]) cube([44,4,52]);
  }
  for(x=[-110,110]) for(z=[25,85]) translate([x,0,z]) rotate([90,0,0]) hole(M3,16);
  for(a=[15:30:345]) rotate([0,0,a]) translate([110,0,0]) hole(M3,12);
  for(a=[30,150,270]) rotate([0,0,a]) translate([110,0,110]) hole(M3,12);
  if(!rear) for(x=[-43,43]) for(dx=[-14,14]) for(z=[23,43]) translate([x+dx,-100,z]) rotate([90,0,0]) hole(M3,16);
  if(rear){
   // Rear screen opening through curved wall; frame is fixed with radial bolts.
   translate([0,118,66]) cube([64,30,34],center=true);
   for(x=[-37,37]) for(z=[44,88]) translate([x,112,z]) rotate([90,0,0]) hole(M3,30);
   for(x=[-30,30]) translate([x,115,22]) rotate([90,0,0]) hole(12.5,40);
  }
 }
}
module screen_frame(){
 difference(){
  union(){ translate([-44,-3,-26])cube([88,6,52]);
   for(x=[-37,37])for(z=[-22,22])difference(){translate([x,-3,z])rotate([90,0,0])cylinder(d=9,h=3);translate([0,-120,-50])cylinder(r=120.2,h=100);}
   // Rearward-facing board pocket, screen and both buttons remain exposed.
   translate([-29,-12,-16])cube([58,12,32]);
  }
  translate([0,0,0])cube([49,40,23],center=true);
  translate([-26.1,-14,-13])cube([52.2,14,26]);
  translate([-44,-12,-7])cube([20,12,14]); // USB-C plug side clearance.
  for(x=[-37,37])for(z=[-22,22])translate([x,0,z])rotate([90,0,0])hole(M3,30);
 }
}
module screen_clamp(){ difference(){intersection(){union(){translate([-44,-26,0])cube([88,52,3]);for(x=[-37,37])for(y=[-22,22])translate([x,y,0])cylinder(d=9,h=8);}translate([0,0,-104])rotate([90,0,0])cylinder(r=119,h=100,center=true);}for(x=[-37,37])for(y=[-22,22])translate([x,y,4])hole(M3,20);translate([0,0,0])cube([32,15,10],center=true);} }
module arm_base(){
 difference(){
  union(){ translate([-22,-46,0])cube([44,46,4]);translate([-22,-4,0])cube([44,4,48]);
   for(x=[-22,18])translate([x,-43,4])cube([4,32,24]);
  }
  for(x=[-14,14])for(z=[10,30])translate([x,-2,z])rotate([90,0,0])hole(M3,12);
  for(x=[-16,16])translate([x,-27,0])cube([4,5,14],center=true);
 }
}
module horn_pattern(axis="z"){
 hole(5,40);for(a=[0,90,180,270])rotate([0,0,a])translate([8,0,0])slot(3,2.2,40);
}
module pitch_carrier(){
 difference(){
  union(){ translate([-14,-24,0])cube([49,48,3]);
   translate([31,-20,0])cube([4,40,44]);
   for(y=[-20,17])translate([7,y,3])cube([28,3,6]);
  }
  horn_pattern();
  for(z=[12,31])for(y=[-15,15])translate([33,y,z])cube([12,4,5],center=true);
 }
}
module arm(kind="plunger"){
 // Native printing frame: horn lies XY at Z=0, shaft projects along +X.
 difference(){
  union(){ cylinder(d=28,h=3);
   translate([0,-6,0])cube([114,12,12]);
   if(kind=="plunger")translate([110,0,6])rotate([0,90,0])difference(){cylinder(d1=15,d2=42,h=18);translate([0,0,2])cylinder(d1=12,d2=37,h=18);}
   else {translate([95,0,6])rotate([0,90,0])cylinder(d=18,h=25);for(a=[0:90:270])translate([75,0,6])rotate([a,0,0])translate([0,8,0])rotate([0,90,0])cylinder(d=3,h=46,$fn=16);}
  }
  translate([0,0,1])horn_pattern();
  translate([55,0,6])cube([83,7,7],center=true);
 }
}
module neck_ring(){ difference(){ring(108,101,4); for(a=[30,150,270])rotate([0,0,a])translate([104,0,0])hole(M3,12); } }
module neck_post(){ difference(){cylinder(d=9,h=11,$fn=24);hole(M3,30);} }
module neck_adapter(){
 difference(){union(){ring(120,116,4);for(a=[30,150,270])rotate([0,0,a])translate([98,-7,0])cube([22,14,4]);}for(a=[30,150,270])rotate([0,0,a]){translate([110,0,0])hole(M3,12);translate([104,0,0])hole(M3,12);}}
}
module neck_deck(){
 difference(){
  union(){ring(108,99,4);for(a=[30,150,270])rotate([0,0,a])translate([0,-5,0])cube([104,10,4]);cylinder(d=62,h=4);translate([50,-38,0])difference(){cube([48,76,4]);translate([7,15,-1])cube([34,46,6]);}}
  for(a=[30,150,270])rotate([0,0,a])translate([104,0,0])hole(M3,12);
  hole(16,20);for(a=[45:90:315])rotate([0,0,a])translate([24,0,0])hole(M3,15);
  for(x=[60,85])for(y=[-30,30])translate([x,y,0])slot(10,M3,12);
 }
}
module bearing_tower(){
 difference(){ union(){cylinder(d=58,h=3);cylinder(d=34,h=26);}
  hole(12,80);translate([0,0,-.1])cylinder(d=22.2,h=7.1);translate([0,0,19])cylinder(d=22.2,h=8);
  for(a=[45:90:315])rotate([0,0,a])translate([24,0,0])hole(M3,14);
  for(a=[0,120,240])rotate([0,0,a])translate([14,0,24])hole(2.6,10);
 }
}
module bearing_cap(){difference(){cylinder(d=34,h=3);hole(16,12);for(a=[0,120,240])rotate([0,0,a])translate([14,0,0])hole(M3,12);}}
module inner_spacer(){difference(){cylinder(d=11.5,h=12);hole(8.4,30);}}
module head_hub(){
 difference(){
  union(){cylinder(d=12,h=14);translate([0,0,13])cylinder(d=64,h=2);translate([0,0,15])cylinder(d=59,h=5);translate([0,0,20])cylinder(d=64,h=2);translate([0,0,22])cylinder(d=42,h=3);}
  hole(8.5,60);for(a=[0:90:270])rotate([0,0,a])translate([17,0,23])hole(M3,12);
 }
}
module head_servo_mount(){
 difference(){
  union(){translate([-18,-36,0])cube([36,72,3]);for(x=[-18,14])translate([x,-29,3])cube([4,58,18]);}
  for(x=[-12.5,12.5])for(y=[-30,30])translate([x,y,0])slot(8,M3,12);
  for(x=[-10,10])for(y=[-19,19])translate([x,y,0])cube([4,5,12],center=true);
 }
}
module servo_pulley(){difference(){union(){cylinder(d=25,h=2);translate([0,0,2])cylinder(d=20,h=5);translate([0,0,7])cylinder(d=25,h=2);}horn_pattern();}}
module head_plate(){
 difference(){
  union(){cylinder(d=50,h=3);for(a=[0:90:270])rotate([0,0,a])translate([0,-9,0])cube([108,18,3]);}
  hole(9,20);for(a=[0:90:270])rotate([0,0,a]){translate([17,0,0])hole(M3,12);translate([101,0,0])hole(M3,12);}
 }
}
module dome(){
 difference(){
  union(){difference(){scale([1,1,65/110])sphere(r=110);scale([1,1,64.2/109.2])sphere(r=109.2);translate([-120,-120,-120])cube([240,240,120]);}
   ring(110,106,5);for(a=[0:90:270])rotate([0,0,a])translate([101,0,0])cylinder(d=14,h=5);translate([-17,-103,11])cube([34,6,29]);
   for(x=[-61,61])translate([x,0,50])cylinder(d=25,h=9);
  }
  for(a=[0:90:270])rotate([0,0,a])translate([101,0,0]){hole(M3,20);translate([0,0,2])cylinder(d=6.4,h=4,$fn=6);}
  for(x=[-9,9])translate([x,-100,25])rotate([90,0,0])hole(M3,22);
  for(x=[-61,61])translate([x,0,54])hole(M3,30);
 }
}
module eye(){
 difference(){union(){cylinder(d=32,h=3);translate([0,0,3])cylinder(d=12,h=75);translate([0,0,76])cylinder(d=31,h=13);translate([0,0,89])cylinder(d=20,h=3);}
 for(x=[-9,9])translate([x,0,0])hole(M3,12);translate([0,0,6])cylinder(d=7,h=84);
 }
}
module lamp(){difference(){union(){cylinder(d=25,h=3);translate([0,0,3])cylinder(d1=21,d2=13,h=19);}hole(M3,60);translate([0,0,1])cylinder(d=6.4,h=3,$fn=6);}}
module hemisphere(){difference(){union(){difference(){sphere(r=13);sphere(r=11.8);translate([-15,-15,-15])cube([30,30,15]);}cylinder(d=9,h=12);}hole(M3,40);translate([0,0,-.1])cylinder(d=6.4,h=3.3,$fn=6);}}
module speaker_mount(){
 difference(){
  union(){translate([-45,-45,0])cube([90,90,3]);for(x=[-45,41])translate([x,-45,0])cube([4,90,12]);translate([-45,-45,-22])cube([90,3,25]);}
  cylinder(d=69,h=20,center=true);for(x=[-30,30])for(y=[-30,30])translate([x,y,0])hole(M3,12);
  for(x=[-41,41])for(y=[-36,36])translate([x,y,0])cube([4,7,12],center=true);
  for(x=[-30,30])translate([x,-44,-15])rotate([90,0,0])hole(M3,15);
 }
}
module fit_coupon(){difference(){cube([90,50,5]);for(i=[0:3])translate([12+i*20,12,0])hole(3.1+i*.1,14);translate([17,34,0])hole(8.4,14);translate([46,33,0])hole(22.2,14);translate([75,33,0])hole(12.5,14);}}
module assembly(explode=0,section=false){
 difference(){union(){
 for(a=[0:90:270]){
  color("#403733")rotate([0,0,a])translate([0,0,15])shell_quarter(180,180,57,false);
  color("#936b3d")rotate([0,0,a])translate([0,0,77+explode*2])shell_quarter();
  color("#a9804d")rotate([0,0,a])translate([0,0,167+explode*3])shell_quarter(145,120,90,true);
  for(tier=[0,1])for(ang=[15,45,75])for(z=[23,67])rotate([0,0,a+ang])translate([radius_at(tier==0?180:145,tier==0?145:120,90,z),0,77+90*tier+z+explode*(2+tier)])rotate([0,90-atan((tier==0?35:25)/90),0])color("#d3a85d")hemisphere();
 }
 for(sx=[-1,1])for(sy=[-1,1]){
  color("#59514b")scale([sx,sy,1])translate([0,0,72+explode])chassis_quarter();
  color("#d99722")translate([sx*130,sy*65,31.5])rotate([0,90,0])cylinder(d=63,h=29,center=true);
  color("#686868")translate([sx*100,sy*40,17])scale([sx,sy,1])motor_cradle();
 }
 color("#444444")translate([0,0,77])battery_tray();
 color("#222d3d")translate([-56,-33,80])cube([112,66,71]);
 for(x=[-70,70])for(y=[-50,50])color("#777777")translate([x,y,77])deck_post();
 color("#555555")translate([0,0,172])electronics_deck();
 color("#444444")translate([0,-65,220])rotate([90,0,0])speaker_mount();
 color("#957447")translate([0,0,257+explode*4]){shoulder_half();shoulder_half(true);}
 color("#282b2f")translate([0,120,323+explode*4])screen_frame();
 color("#282b2f")translate([0,104,323+explode*4])rotate([-90,0,0])screen_clamp();
 color("#192d38")translate([-25.76,116,310.48+explode*4])cube([51.52,2,25.04]);
 color("#37aed6")translate([-13.5,121,315+explode*4])cube([27,1,16]);
 for(x=[-30,30])color("#aaaaaa")translate([x,117,279+explode*4])rotate([-90,0,0])cylinder(d=5,h=17);
 for(x=[-43,43]){color("#4c4c4c")translate([x,-102,270+explode*4])arm_base();color("#737373")translate([x,-129,305+explode*4])pitch_carrier();color("#bbb7ae")translate([x-3,-129,335+explode*4])rotate([90,0,-90])arm(x<0?"plunger":"gun");}
 for(x=[-43,43]){color("#202226")translate([x-17,-135,274+explode*4])cube([24,12,27]);color("#202226")translate([x+4,-135,312+explode*4])cube([27,12,36]);}
 color("#3d3c39")translate([0,0,367+explode*5])neck_adapter();
 for(z=[371,386])color("#666666")translate([0,0,z+explode*5])neck_ring();
 for(z=[375,390])for(a=[30,150,270])color("#777777")rotate([0,0,a])translate([104,0,z+explode*5])neck_post();
 color("#6c6457")translate([0,0,401+explode*5])neck_deck();
 color("#565655")translate([0,0,405+explode*5])bearing_tower();
 color("#333333")translate([0,0,431+explode*5])bearing_cap();
 color("#666666")translate([72.5,0,405+explode*5])head_servo_mount();
 color("#202226")translate([62.5,-10,408+explode*5])cube([20,40,37]);
 color("#777777")translate([72.5,0,445+explode*5])servo_pulley();
 color("#6e6351")translate([0,0,432+explode*6])head_hub();
 color("#b19055")translate([0,0,457+explode*6])head_plate();
 color("#b18a51")translate([0,0,460+explode*6])dome();
 color("#aeb5b7")translate([0,-103,485+explode*6])rotate([90,0,0])eye();
 for(x=[-61,61])color("#e5e1d2")translate([x,0,519+explode*6])lamp();
 }if(section)translate([0,-400,-10])cube([450,800,1100]);}
}
if(part=="chassis_quarter")chassis_quarter();
else if(part=="bumper_quarter")shell_quarter(180,180,57,false);
else if(part=="skirt_lower_quarter")shell_quarter();
else if(part=="skirt_upper_quarter")shell_quarter(145,120,90,true);
else if(part=="splice")splice();
else if(part=="motor_cradle")motor_cradle();
else if(part=="battery_tray")battery_tray();
else if(part=="deck_post")deck_post();
else if(part=="electronics_deck")electronics_deck();
else if(part=="pcb_standoff")pcb_standoff();
else if(part=="shoulder_front")shoulder_half();
else if(part=="shoulder_rear")shoulder_half(true);
else if(part=="screen_frame")translate([0,26,3])rotate([90,0,0])screen_frame();
else if(part=="screen_clamp")screen_clamp();
else if(part=="arm_base")arm_base();
else if(part=="pitch_carrier")pitch_carrier();
else if(part=="plunger_arm")translate([0,0,15])arm("plunger");
else if(part=="gun_arm")translate([0,0,3])arm("gun");
else if(part=="neck_adapter")neck_adapter();
else if(part=="neck_ring")neck_ring();
else if(part=="neck_post")neck_post();
else if(part=="neck_deck")neck_deck();
else if(part=="bearing_tower")bearing_tower();
else if(part=="bearing_cap")bearing_cap();
else if(part=="inner_spacer")inner_spacer();
else if(part=="head_hub")head_hub();
else if(part=="head_servo_mount")head_servo_mount();
else if(part=="servo_pulley")servo_pulley();
else if(part=="head_plate")head_plate();
else if(part=="dome")dome();
else if(part=="eye")eye();
else if(part=="lamp")lamp();
else if(part=="hemisphere")hemisphere();
else if(part=="speaker_mount")translate([0,0,45])rotate([90,0,0])speaker_mount();
else if(part=="fit_coupon")fit_coupon();
else if(part=="exploded")assembly(32);
else if(part=="section")assembly(0,true);
else if(part=="assembly")assembly();
else assert(false,str("Unknown part: ",part));
