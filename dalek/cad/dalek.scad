// DALEK FACET-1. Millimetres; +Y rear, +X right, Z up.
// Ten STL designs; two pitch carriers and four optional motor clamps.
part="assembly";
$fn=64;
wall=1.8; M3=3.4; M4=4.4;
skirt_sides=12;
motor_axle_height=11.7;
base_z=31.5-6-motor_axle_height;
shoulder_h=120;
neck_z=384;
head_shift=15;
module hole(d=M3,h=100){cylinder(d=d,h=h,center=true,$fn=24);}
module slot(l=8,d=M3,h=30){hull()for(x=[-l/2,l/2])translate([x,0,0])hole(d,h);}
module ring(ro,ri,h){difference(){cylinder(r=ro,h=h);translate([0,0,-.1])cylinder(r=ri,h=h+.2);}}
module joint_holes(r=150,z=0){for(a=[0:90:270])rotate([0,0,a])translate([r-13,0,z])hole(M4,18);}
module tongue(r=150,z=0){translate([0,0,z])ring(r-4.5,r-6.5,3);}
module groove(r=150){translate([0,0,-.1])ring(r-4.2,r-6.8,3.4);}
module conical_inner(a,b,h){
 dr=(b-a)/h; cp=cos(180/skirt_sides);
 inset=wall*sqrt(1+dr*dr*cp*cp)/cp;
 translate([0,0,-.1])cylinder(r1=a-inset-.1*dr,r2=b-inset+.1*dr,h=h+.2,$fn=skirt_sides);
}
module motor_envelope(){translate([-11.2,-57,0])cube([22.4,70,22.44]);}
module wheel_wells(){intersection(){translate([0,0,-1])cylinder(r=147,h=59);union(){for(sx=[-1,1])for(sy=[-1,1])scale([sx,sy,1])translate([80.5,24,-1])cube([37,70,59]);}}}
include <base_mounts.scad>;
module bump(a,b,h,z,ang){
 rr=(a+(b-a)*z/h)*cos(180/skirt_sides);
 tilt=atan((a-b)*cos(180/skirt_sides)/h);
 rotate([0,0,ang])translate([rr,0,z])rotate([0,90-tilt,0])translate([0,0,-3]){
 cylinder(d=23,h=4,$fn=32);translate([0,0,1.8])scale([1,1,.72])sphere(r=10,$fn=32);
 }}
module skirt_skin(a,b,h){union(){
 difference(){cylinder(r1=a,r2=b,h=h,$fn=skirt_sides);conical_inner(a,b,h);}
 difference(){union(){
  for(z=[26,76,136,186])for(ang=[15:30:345])bump(a,b,h,z,ang);
  for(ang=[0:30:330])rotate([0,0,ang])hull(){
   translate([a+(b-a)*8/h-.3,0,8])sphere(r=.8,$fn=12);
   translate([b-(b-a)*8/h-.3,0,h-8])sphere(r=.8,$fn=12);
  }
 }conical_inner(a,b,h);}
 }}
module skirt_rib(){
 cp=cos(180/skirt_sides); dr=-40/210;
 inset=wall*sqrt(1+dr*dr*cp*cp)/cp;
 rotate_extrude($fn=skirt_sides)polygon([
  [150+dr*106,106],[150+dr*110,110],[150+dr*114,114],
  [150+dr*114-inset+.1,114],[120/cp,110],[150+dr*106-inset+.1,106]
 ]);
}
module skirt(){union(){difference(){union(){
 skirt_skin(150,110,210);ring(150,132,6);skirt_rib();
 translate([0,0,204])ring(110,92,6);tongue(110,210);
 // Captured upper-joint nuts use the same proven pocket and roof as the base.
 for(a=[0:90:270])rotate([0,0,a])translate([97,0,199])cylinder(d=16,h=11);
 }groove(150);joint_holes(150,3);joint_holes(110,207);
 for(a=[0:90:270])rotate([0,0,a])translate([97,0,156])captive_base_nut_pocket();
 }
 for(a=[0:90:270])rotate([0,0,a])translate([97,0,199])
  for(x=[-3.55,3.55])translate([x-.3,-1.8,0])cube([.6,3.6,.6]);
}}
module horn_pattern(){hole(5,18);for(a=[0:90:270])rotate([0,0,a])translate([8,0,0])slot(3,2.2,18);}
module rounded_box(size,r=5){hull()for(x=[r,size[0]-r])for(y=[r,size[1]-r])for(z=[r,size[2]-r])translate([x,y,z])sphere(r=r,$fn=24);}
include <upper_mounts.scad>;
module arm(kind="plunger"){difference(){union(){
 cylinder(d=28,h=4,center=true);rotate([0,90,0])cylinder(d=12,h=108);
 intersection(){difference(){sphere(r=28,$fn=64);sphere(r=25.5,$fn=64);}translate([12,-35,-35])cube([30,70,70]);}
 for(x=[31,58,86])translate([x,0,0])rotate([0,90,0])cylinder(d=kind=="emitter"?14:15,h=3,$fn=32);
 if(kind=="plunger")translate([104,0,0])rotate([0,90,0])difference(){cylinder(d1=15,d2=40,h=20);translate([0,0,2.5])cylinder(d1=10,d2=35,h=20);}
 else{
  translate([78,0,0])rotate([0,90,0])cylinder(d=21,h=3);
  translate([117,0,0])rotate([0,90,0])ring(11,7,4);
  for(a=[0,90])translate([117,0,0])rotate([a,0,0])translate([0,-10,-1])cube([4,20,2]);
  for(a=[0:45:315])translate([79,0,0])rotate([a,0,0])translate([0,9,0])rotate([0,90,0])cylinder(d=3,h=41,$fn=16);
  translate([117,0,0])rotate([0,90,0])cylinder(d=11,h=8);
 }
 }horn_pattern();arm_servo_relief();}}
module head_motor_carriage(){difference(){union(){
 intersection(){translate([-64.5,0,0])cylinder(r=98,h=3);translate([-26,-61,0])cube([51,80,3]);}
 intersection(){translate([-64.5,0,0])cylinder(r=95.3,h=24);union(){
 for(x=[-15,11.6])translate([x,-59,2])cube([3.2,76,19]);
 for(y=[-61,15])translate([-15,y,2])cube([30,4,16]);
 translate([-23,-41,2])cube([5,12,13]);
 }}
 }
 for(p=[[-20.3,-50],[-20.3,8],[20.2,-40],[20.2,8]])translate([p[0],p[1],1.5])slot(3.6,M3,10);
 translate([-27,-42,-.1])cube([4,14,3.3]);
 translate([0,0,16])hole(15,45);
 for(x=[-13.5,13])for(y=[-43,-24])translate([x,y,9])cube([8,4,5],center=true);
 translate([-8,-64,4])cube([18,10,19]);
 }}
module head(){translate([0,0,head_shift])difference(){union(){
 cylinder(d=12,h=13);translate([0,0,12])cylinder(d=40,h=16);
 translate([0,0,-15])ring(99,96,43);
 for(a=[0:90:270])rotate([0,0,a])translate([0,-5,24])cube([108,10,4]);
 translate([0,0,24])ring(110,106,5);
 translate([0,0,24])difference(){scale([1,1,65/110])sphere(r=110);scale([1,1,63.2/108.2])sphere(r=108.2);translate([-120,-120,-120])cube([240,240,120]);}
 translate([0,-94,48])rotate([90,0,0]){
  cylinder(d1=26,d2=19,h=13);cylinder(d=13,h=77);
  for(k=[22,30,38,46,54])translate([0,0,k])cylinder(d=24-abs(k-38)/3,h=2.5);
  translate([0,0,66])cylinder(d=30,h=13);translate([0,0,77])cylinder(d=23,h=3);translate([0,0,79])cylinder(d=17,h=2);
 }
 for(x=[-60,60])translate([x,0,74])rotate([0,x<0?-10:10,0]){
  cylinder(d=24,h=6);translate([0,0,5])cylinder(d1=22,d2=16,h=19);
  for(z=[8,18])translate([0,0,z])cylinder(d=22-(z-5)*6/19,h=2);
 }
 for(a=[30,90,150,210,270,330])rotate([0,0,a])intersection(){
  translate([0,-.65,24])cube([112,1.3,66]);
  difference(){translate([0,0,24])scale([1,1,65.8/110.8])sphere(r=110.8);translate([0,0,24])scale([1,1,64.3/109.3])sphere(r=109.3);}
 }
 }hole(8.5,70);translate([0,0,27])cylinder(d=24,h=100);}}
module print_mesh(name){import(str("../stl/",name,".stl"),convexity=12);}
module assembly(explode=0){union(){
 color("#343331")translate([0,0,base_z])print_mesh("01_base");
 for(sx=[-1,1])for(sy=[-1,1]){
  color("#dc9823")translate([sx*98,sy*58,31.5])rotate([0,90,0])cylinder(d=63,h=29,center=true);
  color("#f0b72b")translate([sx*70.5,sy*58,base_z+6])scale([sx,sy,1])motor_envelope();
 }
 color("#273443")translate([-35,-57,base_z+8])cube([70,114,76]);
 color("#607064")translate([0,0,base_z+146])rotate([180,0,0])print_mesh("12_electronics_platform");
 for(sx=[-1,1])for(sy=[-1,1])color("#66706c")translate([sx*70.5,sy*11,base_z+29])rotate([0,0,sx<0?180:0])print_mesh("11_motor_clamp");
 for(p=[["02_skirt",54,"#947042"],["04_shoulder",264,"#957044"],["06_head",neck_z+52,"#b48c51"]])color(p[2])translate([0,0,base_z+p[1]+explode*(p[1]/100)])print_mesh(p[0]);
 color("#79766a")translate([64.5,0,base_z+neck_z+29.2])print_mesh("10_head_motor_carriage");
 color("#d49820")translate([64.5,0,base_z+neck_z+71])cylinder(d=63,h=29,center=true);
 for(x=[-47,53]){
  color("#707070")translate([x,-94,base_z+264+42])print_mesh("07_pitch_carrier");
  color("#a9a7a0")translate([x-3,-94,base_z+264+77])rotate([90,0,-90])translate([0,0,-28])print_mesh(x<0?"08_plunger_arm":"09_emitter_arm");
 }
 }}
module mesh_section(){for(p=[["01_base",0],["02_skirt",54],["04_shoulder",264],["06_head",neck_z+52]])color("#947042")difference(){translate([0,0,base_z+p[1]])print_mesh(p[0]);translate([0,-400,-10])cube([450,800,1300]);}}
if(part=="01_base")base();
else if(part=="02_skirt")skirt();
else if(part=="04_shoulder")shoulder();
else if(part=="06_head")head();
else if(part=="07_pitch_carrier")pitch_carrier();
else if(part=="08_plunger_arm")translate([0,0,28])arm("plunger");
else if(part=="09_emitter_arm")translate([0,0,28])arm("emitter");
else if(part=="10_head_motor_carriage")head_motor_carriage();
else if(part=="11_motor_clamp")motor_clamp();
else if(part=="12_electronics_platform")electronics_platform();
else if(part=="assembly"||part=="rear")assembly();
else if(part=="exploded")assembly(44);
else if(part=="section")mesh_section();
else if(part=="base_view")color("#70706b")print_mesh("01_base");
else assert(false,str("Unknown part: ",part));
