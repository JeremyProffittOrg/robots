// Machined/welded metal parts. Dimensions in mm; no printed load-bearing pivots.
// Include after exterior.scad and kinematics.scad.
module xhole(d,h=300){rotate([0,90,0])cylinder(d=d,h=h,center=true,$fn=32);}
module hole(d,h=20){cylinder(d=d,h=h,center=true,$fn=32);}
module carrier_profile(){difference(){intersection(){square([64,64],center=true);rotate(45)square([76.37,76.37],center=true);}
 circle(d=26);for(z=[-21,21])translate([0,z])circle(d=5.5);for(y=[-25,25])for(z=[-22,22])translate([y,z])circle(d=4.5);}}
function guide_y(t,n=0)=GUIDE_Y-t*sin(GUIDE_ANGLE)+n*cos(GUIDE_ANGLE);
function guide_z(t,n=0)=GUIDE_Z-t*cos(GUIDE_ANGLE)-n*sin(GUIDE_ANGLE);
module chassis_profile(){difference(){union(){difference(){translate([-80,170])square([160,255]);translate([-62,190])square([124,165]);}
 for(t=[-75,0])let(y=guide_y(t,-30.875),z=guide_z(t,-30.875))hull(){translate([y,z])circle(r=12);translate([-72,z])circle(r=8);}}
 translate([0,HIP_Z])circle(d=26);for(y=[-25,25])for(z=[-22,22])translate([y,HIP_Z+z])circle(d=4.5);
 for(t=[-75,0])translate([guide_y(t,-30.875),guide_z(t,-30.875)])circle(d=6.5);
 for(y=[-55,55])for(z=[183,403])translate([y,z])circle(d=4.5);
 for(y=[-70,70])for(z=[275,365])translate([y,z])circle(d=4.5);}}
module electronics_profile(speaker=false){difference(){square([160,100],center=true);
 if(speaker)circle(d=69);
 for(x=[-70:10:70])for(z=[-40:10:40])if(!speaker||sqrt(x*x+z*z)>39)translate([x,z])circle(d=3.2);
 for(x=[-65,65])for(z=[-43,43])translate([x,z])square([5,8],center=true);}}
module spine_profile(){difference(){union(){circle(d=60);translate([-12.5,106-HIP_Z])square([25,HIP_Z-106]);}
 circle(d=12.5);for(a=[45:90:315])rotate(a)translate([16,0])circle(d=4.5);
 for(z=[119,139])translate([0,z-HIP_Z])circle(d=6.5);
 for(z=[-45,-155,-225])translate([0,z])circle(d=3.4);}}
module hub(){difference(){xhole(44,10);xhole(12,12);translate([-6,0,-.6])cube([12,23,1.2]);
 for(a=[45:90:315])rotate([a,0,0])translate([0,16,0])xhole(3.3,12);
 translate([0,17,0])hole(4.5,50);}}
module bearing_housing(){difference(){translate([-6.5,-18,-26])cube([13,36,52]);
 xhole(28,16);for(z=[-21,21])translate([0,0,z])xhole(4.2,16);}
 color("#505963")translate([-4,0,0])rotate([0,90,0])ring(14,6,8);}
module shoulders(){for(s=[-1,1])scale([s,1,1]){
 color(SILVER)side_plane(95)linear_extrude(4)chassis_profile();
 color(SILVER)for(x=[101.5,158.5])translate([0,0,HIP_Z])side_plane(x)linear_extrude(4)carrier_profile();
 color("#566473")for(x=[112,152])translate([x,0,HIP_Z])bearing_housing();
 color(SILVER)for(y=[-25,25])for(z=[-22,22])translate([132,y,HIP_Z+z])difference(){xhole(10,53);xhole(4.5,54);}
 }}
module side_spine(){color(SILVER){side_plane(3)linear_extrude(4)spine_profile();translate([12,0,0])hub();
 translate([-28,0,0])xhole(12,90);for(x=[-63.5,-2.5])translate([x,0,0])difference(){xhole(22,8);xhole(12,9);}}
}
module tube(od,wall,length){difference(){translate([-od/2,-od/2,0])cube([od,od,length]);translate([-od/2+wall,-od/2+wall,-.1])cube([od-2*wall,od-2*wall,length+.2]);}}
module yoke_profile(){difference(){union(){translate([-34,-85])square([81,92]);translate([-72.5,-75])square([38.6,30]);translate([-37.5,-7])square([3.6,14]);}
 for(x=[-11,11])for(t=[-80,-68])translate([x,t])circle(d=4.5);
 translate([-20,-55])square([40,36]);}}
module limit_rail_profile(){difference(){translate([-45,6])square([30,199]);
 for(tip=[77,185])for(t=[tip-14.5,tip-5])hull()for(n=[-31.3,-27.3])translate([n,t])circle(d=2.4);
 for(n=[-42,-35])translate([n,10])circle(d=3.4);}}
module ankle_profile(){difference(){translate([-12.5,0])square([25,77]);for(z=[44,64])translate([0,z])circle(d=6.5);}}
module fork_profile(){difference(){translate([-15,0])square([30,53]);translate([0,38])circle(d=12.1);}}
module rodend(){color(SILVER){rotate([0,90,0])difference(){cylinder(d=35,h=8.5,center=true);cylinder(d=17,h=10,center=true);}
 rotate([0,90,0])difference(){sphere(d=17,$fn=48);cylinder(d=12,h=25,center=true);}
 translate([0,0,-54])cylinder(d=12,h=40);translate([0,0,-38.5])cylinder(d=19,h=6,$fn=6);}}
module rear_guide(s){L=POST_ZERO+s;guide_frame(){
 color(SILVER)translate([0,0,-150])tube(31.75,3.175,200);
 color("#697d91")translate([0,0,L-332.5])tube(19.05,3.175,270);
 for(t=[-90,30])for(a=[0,90,180,270])color("#444c55")rotate([0,0,a])translate([9.525,-9,t-10])cube([3.175,18,20]);
 // Fixed limit rail stays outside the rear-foot cover at X<-54.
 color(SILVER){side_plane(-76)linear_extrude(3)limit_rail_profile();
 difference(){translate([-73,-45,5])cube([12,13,10]);translate([-67,-38.5,10])hole(5.5,25);}
 }
 for(tip=[77,185]){
  // SS-01GL:19.8 along guide;10.2 high;6.4 across its actual mounting bores.
  color("#171f28")difference(){translate([-73,-31.8,tip-19.6])cube([6.4,10.2,19.8]);
   for(t=[tip-14.5,tip-5])translate([-70,-29.3,t])xhole(2.4,10);}
  color(SILVER)translate([-71.6,-21.5,tip-14.5])cube([3.6,.3,14.5]);
 }
 for(t=[-75,0]){
  color(SILVER)translate([-95,-45.875,t-5])difference(){cube([190,30,10]);
   for(x=[-.1,175])translate([x,15,5])rotate([0,90,0])cylinder(d=5,h=15.2);
   for(x=[74,116])translate([x,-.1,5])rotate([-90,0,0])cylinder(d=6.5,h=30.2);
   if(t==0){translate([119,26,-.1])cube([28,4.1,10.2]);for(x=[127,139])translate([x,26.1,5])rotate([90,0,0])cylinder(d=3.3,h=22.1);}}
  color("#545e66")for(x=[-21,21])translate([x,18.875,t])rotate([90,0,0])cylinder(d=6,h=75);
  color("#545e66")translate([0,18.875,t])xhole(6,42);
 }
 color(SILVER)translate([0,0,L-97.5])difference(){translate([-17,-17,0])cube([34,34,65]);translate([-9.6,-9.6,-.1])cube([19.2,19.2,35.1]);translate([0,0,40.9])cylinder(d=10.2,h=25);for(z=[10,26])translate([0,0,z])xhole(5.5,36);
 for(x=[-11,11])for(z=[17.5,29.5])translate([x,-17.1,z])rotate([-90,0,0])cylinder(d=3.3,h=7.1);}
 translate([0,0,L])rodend();
 // Independent P16 case and rod, X38 eye line, 147+s pin spacing.
 color("#262e38")translate([27.5,-10,11])cube([36,20,112]);
 color(SILVER){translate([38,0,3])xhole(9,8);translate([38,0,123])cylinder(d=8,h=L-123);translate([38,0,L])xhole(9,6);}
 // Stationary aluminum clevis fastens to the t=0 crossbar, clear of the case.
 color(SILVER){difference(){translate([24,-19.875,-10])cube([28,4,24]);
  for(x=[32,44])translate([x,-17,0])rotate([90,0,0])hole(4.5,12);}
 for(x=[29,43])difference(){translate([x,-15.875,-4])cube([4,22.875,14]);translate([x+2,0,3])xhole(4.5,8);}}
 // Steel moving yoke: offset behind the actuator case, not through it.
 color(SILVER){translate([0,-17,L])rotate([90,0,0])linear_extrude(4)yoke_profile();
 for(x=[29,43])difference(){translate([x,-17,L-7])cube([4,24,14]);translate([x+2,0,L])xhole(4.5,8);}
 difference(){translate([-37.5,-17,L-7])cube([4,24,14]);translate([-35.5,0,L])xhole(3.2,8);}
 }
}}
module foot_arch(rear=false){
 // Steel welded T frame; loads bypass all motor mounts and covers.
 color(SILVER){difference(){translate([-8,-96,12])cube([16,151,4]);
 for(y=[-37,37])for(yy=[-42,-15])for(x=[-6,6])translate([x,y+yy,14])cube([3.2,4.5,8],center=true);
 for(y=[-90,-23,52])translate([0,y,14])hole(3.4,8);}
 translate([-22,-4,12])cube([44,8,4]);
 for(x=[-21,17])translate([x,-4,16])cube([4,8,55]);
 difference(){translate([-32,-25,71])cube([64,50,4]);for(x=[-27,27])for(y=[-17,17])translate([x,y,73])hole(3.4,8);}
 if(rear){for(x=[-12,8])translate([0,0,75])side_plane(x)linear_extrude(4)fork_profile();
 difference(){translate([-47,-80,66.1])cube([34,60,4]);translate([-40.85,-71,65])cube([21.7,42.7,6]);for(x=[-35,-25])for(y=[-74.4,-24.9])hull()for(dy=[-2,2])translate([x,y+dy,68])hole(3.4,8);}
 for(x=[-35,-25])for(y=[-74.4,-24.9])translate([x,y,70.1])difference(){cylinder(d=5,h=20);hole(2.5,45);}
 translate([-32,-25,70])cube([15,5,5]);
 // Norelem07534-12X25:25mm shoulder,16mmM10 thread,18x9mm head.
 translate([-13.3,0,113])rotate([0,90,0]){
  cylinder(d=12,h=25);translate([0,0,25])cylinder(d=10,h=16);
  translate([0,0,-9])cylinder(d=18,h=9);
 }
 translate([-13.3,0,113])rotate([0,90,0])ring(9,6.1,1.3);
 translate([12,0,113])rotate([0,90,0])ring(10,5.25,2);
 translate([14,0,113])rotate([0,90,0])difference(){cylinder(d=19.63,h=10,$fn=6);cylinder(d=10,h=11);}
 }else translate([0,0,75])side_plane(-1)linear_extrude(4)ankle_profile();
 }}
module base_profile(){difference(){intersection(){circle(r=124);square([190,180],center=true);}translate([-24,-90])square([98,32]);
 for(a=[45,135,225,315])rotate(a)translate([119,0])circle(d=3.4);
 for(x=[-89,89])for(y=[-55,55])translate([x,y])circle(d=4.5);
 for(x=[-35,35])for(y=[-7,47])translate([x,y])square([22,4],center=true);
 for(x=[-65,65])for(y=[-20,50])translate([x,y])circle(d=3.4);}}
module headfloor_profile(){difference(){intersection(){circle(r=124);square([190,160],center=true);}circle(d=16);
 translate([30,-65])square([34,118]);
 translate([59,-32])square([34,64]);
 for(a=[45:90:315])rotate(a)translate([24,0])circle(d=3.4);
 for(x=[23,69])for(y=[-50,45])translate([x,y])circle(d=3.4);
 for(x=[-89,89])for(y=[-55,55])translate([x,y])circle(d=4.5);}}
module metal_chassis(){shoulders();color(SILVER){translate([0,0,170])linear_extrude(3)base_profile();translate([0,0,413])linear_extrude(2)headfloor_profile();
 for(y=[-70,70])for(z=[275,365])translate([0,y,z])xhole(4,206);
 for(x=[-95,83])for(y=[-65,45])for(z=[173,393])difference(){translate([x,y,z])cube([12,20,20]);translate([x+6,y+10,z+10])xhole(4.5,15);translate([x+6,y+10,z+10])hole(4.5,22);}
 }}
module electronics_panels(){color("#b0aa8a"){
 translate([0,73,320])rotate([90,0,0])linear_extrude(3)electronics_profile();
 translate([0,-70,320])rotate([90,0,0])linear_extrude(3)electronics_profile(true);}}
