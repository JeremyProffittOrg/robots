// DALEK ROUND-10. Millimetres; +Y rear, +X right, Z up.
// Ten connected STL designs; pitch carrier is printed twice.
part="assembly";
$fn=64;
wall=1.8; M3=3.4; M4=4.4;
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
module conical_inner(a,b,h){translate([0,0,-.1])cylinder(r1=a-wall,r2=b-wall,h=h+.2);}
module motor_envelope(){translate([-11.2,-57,0])cube([22.4,70,22.44]);}
module wheel_wells(){intersection(){translate([0,0,-1])cylinder(r=147,h=53);union(){for(sx=[-1,1])for(sy=[-1,1])scale([sx,sy,1])translate([80.5,24,-1])cube([37,70,53]);}}}
module base(){difference(){
 union(){
  cylinder(r=150,h=6);ring(150,146,54);translate([0,0,48])ring(150,132,6);tongue(150,54);
  intersection(){cylinder(r=146,h=30);union(){
   for(x=[-59,55])translate([x,-145,5])cube([4,290,21]);
   for(y=[-111,107])translate([-146,y,5])cube([292,4,21]);
  }}
  for(sx=[-1,1])for(sy=[-1,1])scale([sx,sy,1]){
   translate([54.5,-1,5])cube([4,76,28]);translate([82.5,-1,5])cube([3,76,28]);
   for(y=[-3,73])translate([54.5,y,5])cube([31,4,17]);
   for(x=[51.5,88.5])for(y=[6,16])translate([x,y,5])cylinder(d=11,h=24);
  }
  for(x=[-42,38])translate([x,-62,5])cube([4,124,19]);
  for(y=[-62,58])translate([-42,y,5])cube([84,4,19]);
  for(x=[-54,54])for(y=[-93,-69,69,93])translate([x,y,5])cylinder(d=9,h=4);
 }
 wheel_wells();
 for(sx=[-1,1])for(sy=[-1,1])scale([sx,sy,1])translate([70.5,58,17.7])rotate([0,90,0])hole(15,42);
 for(x=[-83.5,56.5])translate([x,-8,6])cube([27,16,25]);
 for(sx=[-1,1])for(sy=[-1,1])scale([sx,sy,1])for(x=[51.5,88.5])for(y=[6,16])translate([x,y,0])hole(M3,70);
 for(x=[-34,34])for(y=[-35,35])translate([x,y,0])cube([4,22,14],center=true);
 translate([-46,-22,10])cube([10,44,22]);
 for(x=[-54,54])for(y=[-93,-69,69,93])translate([x,y,0])slot(12,2.8,24);
 for(z=[8,21,34])translate([0,0,z])ring(151,149.2,1.4);
 joint_holes(150,52);
 }}
module bump(a,b,h,z,ang){rr=a+(b-a)*z/h;rotate([0,0,ang])translate([rr-3,0,z])rotate([0,90,0]){
 cylinder(d=23,h=3,$fn=32);translate([0,0,1.8])scale([1,1,.72])sphere(r=10,$fn=32);
 }}
module skirt(a=150,b=125,h=110){difference(){union(){
 difference(){cylinder(r1=a,r2=b,h=h);conical_inner(a,b,h);}
 ring(a,a-18,6);translate([0,0,h-6])ring(b,b-18,6);tongue(b,h);
 difference(){union(){
  for(z=[26,76])for(ang=[15:30:345])bump(a,b,h,z,ang);
  for(ang=[0:30:330])rotate([0,0,ang])hull(){translate([a-.8,0,8])sphere(r=1,$fn=12);translate([b-.8,0,h-8])sphere(r=1,$fn=12);}
 }conical_inner(a,b,h);}
 }groove(a);joint_holes(a,3);joint_holes(b,h-3);}}
module horn_pattern(){hole(5,18);for(a=[0:90:270])rotate([0,0,a])translate([8,0,0])slot(3,2.2,18);}
module rounded_box(size,r=5){hull()for(x=[r,size[0]-r])for(y=[r,size[1]-r])for(z=[r,size[2]-r])translate([x,y,z])sphere(r=r,$fn=24);}
module gunbox_shell(cx){difference(){
 translate([cx-47,-115,6])rounded_box([94,58,106],6);
 translate([cx-43,-110,10])rounded_box([86,62,98],4);
 translate([cx,-94,77])sphere(r=29.2,$fn=64);
 translate([cx,-113,77])rotate([90,0,0])cylinder(d=44,h=12,center=true,$fn=64);
 }}
module shoulder(){difference(){union(){
 difference(){ring(110,110-wall,shoulder_h);for(cx=[-50,50])translate([cx-43,-110,11])cube([86,51,97]);}
 ring(110,92,6);translate([0,0,shoulder_h-6])ring(110,92,6);tongue(110,shoulder_h);
 for(cx=[-50,50])gunbox_shell(cx);
 translate([-12,-111,9])cube([24,5,94]);
 translate([-43,-20,4])cube([86,4,81]);
 for(s=[-1,1])hull(){translate([s*40,-18,4])cylinder(d=8,h=4);translate([s*105,-28,4])cylinder(d=8,h=4);}
 for(x=[-47,53]){
  translate([x-21,-107,4])cube([42,30,4]);
  for(dx=[-21,17])translate([x+dx,-107,7])cube([4,30,18]);
  translate([x-21,-81,4])cube([42,4,24]);
 }
 for(a=[-15:15:195])rotate([0,0,a]){
  translate([109,-4,17])cube([3,8,79]);
  for(z=[23,90])translate([111.5,0,z])rotate([0,90,0])cylinder(d=3.2,h=1.5,$fn=16);
 }
 for(z=[9,103])difference(){translate([0,0,z])ring(113,108,4);for(cx=[-50,50])translate([cx-39,-115,0])cube([78,58,120]);}
 translate([-41,98,40])cube([82,16,48]);
 for(cx=[-50,50])for(dx=[-28,28])for(z=[48,104])translate([cx+dx,-114.5,z])rotate([90,0,0])cylinder(d=4.2,h=1.7,$fn=16);
 }
 groove(110);joint_holes(110,3);joint_holes(110,shoulder_h-3);
 for(x=[-7,0,7])for(z=[28,35,42,49,56,63,70,77,84])translate([x,-108,z])rotate([90,0,0])hole(4.2,12);
 translate([0,-18,43])rotate([90,0,0])hole(69,12);
 for(x=[-30,30])for(z=[13,73])translate([x,-18,z])rotate([90,0,0])hole(M3,12);
 for(x=[-47,53])for(dx=[-17,17])for(y=[-102,-84])translate([x+dx,y,6])cube([4,4,12],center=true);
 // Case pocket clears the rounded gunbox floor while retaining theZ8 support.
 for(x=[-47,53]){
  translate([x-12.5,-100.5,8])cube([25,13,33]);
  translate([x-18.5,-100.5,32])cube([37,13,10]);
 }
 translate([-24.5,108,53])cube([49,16,23]);translate([-26.1,95,51.5])cube([52.2,15,26]);translate([-41,95,57])cube([19,15,14]);
 for(x=[-34,34])for(z=[56,73])translate([x,106,z])rotate([90,0,0])hole(M3,26);
 for(x=[-30,30])translate([x,104,23])rotate([90,0,0])hole(12.5,30);
 }}
module pitch_carrier(){difference(){union(){
 translate([-14,-10,0])cube([49,30,4]);translate([31,-10,0])cube([4,27,49]);
 for(y=[-10,13])translate([5,y,3])cube([30,4,9]);
 }horn_pattern();for(z=[18,37])for(y=[-7,13])translate([33,y,z])cube([12,4,5],center=true);}}
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
 }horn_pattern();}}
module neck(){difference(){union(){
 ring(110,92,6);for(z=[15,30,44])translate([0,0,z])ring(106,99,4);
 for(a=[45:90:315])rotate([0,0,a])translate([98,-4,0])cube([7,8,48]);
 for(a=[7.5:15:352.5])rotate([0,0,a])translate([99,-.8,5])cube([2,1.6,43]);
 // Opaque inner grille liner hides the motor; deliberate service ports remain.
 translate([0,0,5])ring(97.5,96.3,46);
 for(a=[7.5:15:352.5])for(z=[15,30,44])rotate([0,0,a])translate([96.3,-.8,z])cube([4.7,1.6,2]);
 for(a=[45,135,225])rotate([0,0,a])translate([0,-6,40])cube([103,12,4]);
 translate([0,0,40])cylinder(d=38,h=26);
 intersection(){cylinder(r=103,h=40);translate([38,-63,25.2])cube([50,85,4]);}
 for(y=[-59,16])translate([46,y,5])cube([38,4,24.2]);
 translate([30,-41,25.2])cube([18,12,4]);translate([30,-41,25.2])cube([8,12,17.8]);
 translate([84,-4,25.2])cube([10.1,10,4]);translate([90.1,-4,25.2])cube([4,10,9.1]);
 }
 groove(110);joint_holes(110,3);
 for(a=[0:90:270])rotate([0,0,a])translate([97,0,6])cylinder(d=9.2,h=49,$fn=24);
 translate([0,0,52])hole(12.5,45);translate([0,0,39.9])cylinder(d=22.2,h=7.1);translate([0,0,59])cylinder(d=22.2,h=8);
 for(a=[0,120,240])rotate([0,0,a]){translate([14,0,65])hole(2.6,14);translate([14,0,41])hole(2.6,12);}
 for(p=[[43,-50],[43,8],[83.5,-40],[83.5,8]])translate([p[0],p[1],27])hole(M3,14);
 translate([63.3,0,27])slot(3.6,15,16);
 translate([34,-35,38])rotate([0,90,0])hole(3.4,20);
 translate([33,-38.05,36.25])cube([2.7,6.1,10]);
 // Slide edge clearance below middle neck ring; access uses narrow top ports.
 intersection(){translate([0,0,28.7])ring(105,95.8,5);translate([40,-65,28.7])cube([64,86,5]);}
 for(x=[43,83.5])for(s=[-1,1])translate([x-3,s<0?-106:45,48.1])cube([6,61,3.8]);
 translate([80,5,48.1])cube([26,6,3.8]);
 translate([-106,-40,34.5])cube([20,10,7]);
 }}
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
 color("#273443")translate([-35,-57,base_z+6])cube([70,114,76]);
 for(p=[["02_lower_skirt",54,"#947042"],["03_upper_skirt",164,"#aa8350"],["04_shoulder",264,"#957044"],["05_neck",neck_z,"#484641"],["06_head",neck_z+52,"#b48c51"]])color(p[2])translate([0,0,base_z+p[1]+explode*(p[1]/100)])print_mesh(p[0]);
 color("#79766a")translate([64.5,0,base_z+neck_z+29.2])print_mesh("10_head_motor_carriage");
 color("#d49820")translate([64.5,0,base_z+neck_z+71])cylinder(d=63,h=29,center=true);
 for(x=[-47,53]){
  color("#707070")translate([x,-94,base_z+264+42])print_mesh("07_pitch_carrier");
  color("#a9a7a0")translate([x-3,-94,base_z+264+77])rotate([90,0,-90])translate([0,0,-28])print_mesh(x<0?"08_plunger_arm":"09_emitter_arm");
 }
 }}
module mesh_section(){for(p=[["01_base",0],["02_lower_skirt",54],["03_upper_skirt",164],["04_shoulder",264],["05_neck",neck_z],["06_head",neck_z+52]])color("#947042")difference(){translate([0,0,base_z+p[1]])print_mesh(p[0]);translate([0,-400,-10])cube([450,800,1300]);}}
if(part=="01_base")base();
else if(part=="02_lower_skirt")skirt(150,125,110);
else if(part=="03_upper_skirt")skirt(125,110,100);
else if(part=="04_shoulder")shoulder();
else if(part=="05_neck")neck();
else if(part=="06_head")head();
else if(part=="07_pitch_carrier")pitch_carrier();
else if(part=="08_plunger_arm")translate([0,0,28])arm("plunger");
else if(part=="09_emitter_arm")translate([0,0,28])arm("emitter");
else if(part=="10_head_motor_carriage")head_motor_carriage();
else if(part=="assembly"||part=="rear")assembly();
else if(part=="exploded")assembly(44);
else if(part=="section")mesh_section();
else if(part=="base_view")color("#70706b")print_mesh("01_base");
else assert(false,str("Unknown part: ",part));
