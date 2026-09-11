// DALEK STACK-10. Millimetres; +Y rear, +X right, Z up.
// Exactly ten connected printable designs; pitch carrier is printed twice.
part="assembly";
$fn=64;
wall=1.6;
M3=3.4;
M4=4.4;
motor_axle_height=11.7; // Drawing-derived nominal; verify actual case and pad.
base_z=31.5-6-motor_axle_height;
module hole(d=M3,h=100){cylinder(d=d,h=h,center=true,$fn=24);}
module slot(l=8,d=M3,h=30){hull()for(x=[-l/2,l/2])translate([x,0,0])hole(d,h);}
module ring(ro,ri,h){difference(){cylinder(r=ro,h=h);translate([0,0,-.1])cylinder(r=ri,h=h+.2);}}
module outline(r=150,rect=false,inset=0){
 if(rect)hull()for(x=[-115,115])for(y=[-105,105])translate([x,y])circle(r=35-inset);
 else circle(r=r-inset);
}
module rim(r=150,rect=false,inset=0,t=4,h=6){linear_extrude(h)difference(){outline(r,rect,inset);outline(r,rect,inset+t);}}
module joint_holes(r=150,rect=false,z=0){
 for(a=[0:90:270])rotate([0,0,a])translate([rect?(a==0||a==180?137:127):r-13,0,z])hole(M4,18);
}
module tongue(r=150,rect=false,z=0){translate([0,0,z])rim(r,rect,4.5,2,3);}
module groove(r=150,rect=false){translate([0,0,-.1])rim(r,rect,4.2,2.6,3.4);}
module conical_shell(a,b,h,rect=false){
 difference(){hull(){linear_extrude(.1)outline(a,rect);translate([0,0,h-.1])cylinder(r=b,h=.1);}
 conical_inner(a,b,h,rect);}
}
module conical_inner(a,b,h,rect=false){translate([0,0,-.1])hull(){linear_extrude(.1)outline(a,rect,wall);translate([0,0,h+.1])cylinder(r=b-wall,h=.1);}}
module motor_envelope(){translate([-11.2,-57,0])cube([22.4,70,22.44]);}
// Inboard relief permits actual press-fit wheel centre X120..125; gearbox floor
// remains6mm thick through its full X85.7..104.3 support width.
module wheel_wells(){for(sx=[-1,1])for(sy=[-1,1])scale([sx,sy,1])translate([105,26,-1])cube([37,70,53]);}
module base(){
 difference(){
  union(){
   linear_extrude(6)outline(150,true);
   rim(150,true,0,4,54);
   translate([0,0,48])rim(150,true,0,18,6);
   tongue(150,true,54);
   // Continuous central longitudinal beams and transverse bulkheads.
   for(x=[-70,66])translate([x,-128,5])cube([4,256,21]);
   for(y=[-108,-2,104])translate([-142,y,5])cube([284,4,21]);
   // Four integrated open-top saddles; case bottoms rest on the main floor.
   for(sx=[-1,1])for(sy=[-1,1])scale([sx,sy,1]){
    translate([79,1,5])cube([4,76,28]);
    translate([107,1,5])cube([3,76,28]);
    for(y=[-1,75])translate([79,y,5])cube([31,4,17]);
    // Clamp bosses are beside the metal motor end, well ahead of wheel wells.
    for(x=[76,113])for(y=[8,18])translate([x,y,5])cylinder(d=11,h=24);
   }
   // Battery pocket:116x76 clear, low walls, rear connector gap.
   for(x=[-62,58])translate([x,-42,5])cube([4,84,19]);
   for(y=[-42,38])translate([-62,y,5])cube([124,4,19]);
   // Electronics mount to the floor fore/aft of the battery using purchased spacers.
   for(x=[-54,-18,18,54])for(y=[-91,-63,65,93])translate([x,y,5])cylinder(d=9,h=4);
  }
  wheel_wells();
  // Both axle ends have unobstructed openings through the saddle sidewalls.
  for(sx=[-1,1])for(sy=[-1,1])scale([sx,sy,1])translate([95,60,17.7])rotate([0,90,0])hole(15,42);
  // Open wire exits at the motor tails; main6mm floor remains continuous.
  for(x=[-108,81])translate([x,-6,6])cube([27,12,25]);
  for(sx=[-1,1])for(sy=[-1,1])scale([sx,sy,1])for(x=[76,113])for(y=[8,18])translate([x,y,0])hole(M3,70);
  for(x=[-35,35])for(y=[-34,34])translate([x,y,0])cube([22,4,14],center=true);
  translate([-22,36,10])cube([44,10,22]);
  for(x=[-54,-18,18,54])for(y=[-91,-63,65,93])translate([x,y,0])slot(12,2.8,24);
  for(x=[-36.85,36.85])for(y=[-97,97])translate([x,y,0])hole(2.8,24);
  for(x=[-82,-57,57,82])for(y=[-114,-89,89,114])translate([x,y,0])slot(8,2.8,24);
  joint_holes(150,true,52);
 }
}
function rect_ray(a)=let(c=abs(cos(a)),s=abs(sin(a)),dp=115*c+105*s,cr=115*s-105*c) s*150<=105*c?150/c:c*140<=115*s?140/s:dp+sqrt(35*35-cr*cr);
module bumps(a,b,h,rect=false){
 for(z=[26,76])for(ang=[15:30:345]){
  rr=a+(b-a)*z/h;
  // Elliptical lower skirt has flatter sides; radial hull is evaluated analytically.
  rrect=rect?rect_ray(ang):a;
  rad=rect?rrect+(b-rrect)*z/h:rr;
  rotate([0,0,ang])translate([rad-4,0,z])scale([.85,1,1])sphere(r=10,$fn=24);
 }
}
module skirt(a=150,b=125,h=110,rect=false){
 difference(){union(){
  conical_shell(a,b,h,rect);
  rim(a,rect,0,18,6);
  translate([0,0,h-6])ring(b,b-18,6);
  tongue(b,false,h);
  // Integrated bumps intersect and join the shell; no loose hemisphere files.
  difference(){bumps(a,b,h,rect);conical_inner(a,b,h,rect);}
 }
 groove(a,rect);
 joint_holes(a,rect,3);joint_holes(b,false,h-3);
 }
}
module horn_pattern(){hole(5,40);for(a=[0:90:270])rotate([0,0,a])translate([8,0,0])slot(3,2.2,40);}
module shoulder(){
 difference(){union(){
  ring(110,110-wall,100);ring(110,92,6);translate([0,0,94])ring(110,92,6);tongue(110,false,100);
  // Integrated flat speaker baffle closes onto circular front wall.
  translate([-45,-110,7])cube([90,12,86]);
  // Integral arm yaw shelves and cheeks, one on each side of speaker.
  for(x=[-48,48]){
   translate([x-22,-148,54])cube([44,51,4]);
   for(dx=[-22,18])translate([x+dx,-145,57])cube([4,39,18]);
   for(dx=[-22,18])translate([x+dx,0,0])rotate([90,0,90])linear_extrude(4)polygon([[-145,54],[-106,28],[-106,54]]);
   translate([x-22,-112,28])cube([44,8,30]);
  }
  // Board pocket/frame is part of rear shell, inserted from inside.
  translate([-41,98,40])cube([82,16,48]);
 }
 groove(110);joint_holes(110,false,3);joint_holes(110,false,97);
 translate([0,-97,10])hole(9,8);
 translate([0,-105,50])rotate([90,0,0])hole(69,28);
 for(x=[-30,30])for(z=[20,80])translate([x,-106,z])rotate([90,0,0])hole(M3,28);
 for(x=[-48,48])for(dx=[-17,17])for(y=[-137,-116])translate([x+dx,y,56])cube([4,5,12],center=true);
 // Screen glass and buttons visible. PCB recess from inside; USB-C notch left.
 translate([-24.5,108,53])cube([49,16,23]);
 translate([-26.1,95,51.5])cube([52.2,15,26]);
 translate([-41,95,57])cube([19,15,14]);
 for(x=[-34,34])for(z=[56,73])translate([x,106,z])rotate([90,0,0])hole(M3,26);
 for(x=[-30,30])translate([x,104,23])rotate([90,0,0])hole(12.5,30);
 }
}
module pitch_carrier(){difference(){union(){
 translate([-14,-24,0])cube([49,48,4]);translate([31,-20,0])cube([4,40,44]);
 for(y=[-20,16])translate([5,y,3])cube([30,4,9]);
 }horn_pattern();for(z=[13,32])for(y=[-15,15])translate([33,y,z])cube([12,4,5],center=true);}}
module arm(kind="plunger"){
 difference(){union(){cylinder(d=28,h=4);translate([0,-6,0])cube([106,12,12]);
 if(kind=="plunger")translate([102,0,6])rotate([0,90,0])difference(){cylinder(d1=15,d2=38,h=18);translate([0,0,2])cylinder(d1=11,d2=33,h=18);}
 else{translate([92,0,6])rotate([0,90,0])cylinder(d=17,h=24);for(a=[0:90:270])translate([73,0,6])rotate([a,0,0])translate([0,7,0])rotate([0,90,0])cylinder(d=3,h=43,$fn=20);}
 }horn_pattern();translate([53,0,6])cube([82,6,6],center=true);}
}
module neck(){difference(){union(){
 ring(110,92,6);for(z=[15,30])translate([0,0,z])ring(104,99,4);
 for(a=[45:90:315])rotate([0,0,a])translate([98,-4,0])cube([7,8,44]);
 translate([0,0,40])ring(104,95,4);
 for(a=[0:90:270])rotate([0,0,a])translate([0,-6,40])cube([103,12,4]);
 translate([0,0,40])cylinder(d=38,h=26);
 translate([48,-24,40])cube([48,67,4]);
 translate([54,-20,32])cube([38,62,2]);
 for(x=[53,89])translate([x,-20,32])cube([4,62,25]);
 }
 groove(110);joint_holes(110,false,3);
 translate([0,0,52])hole(12.5,45);
 translate([0,0,39.9])cylinder(d=22.2,h=7.1);
 translate([0,0,59])cylinder(d=22.2,h=8);
 for(a=[0,120,240])rotate([0,0,a]){
  translate([14,0,65])hole(2.6,14);translate([14,0,41])hole(2.6,12);
 }
 // FS5103R:40.15x20.15 case,54 ears,shaft10.05 offset;42.85 spline height.
 // Floor34 permits horn face79; shim to actual supplied horn thickness.
 translate([59,-18,34])cube([29,58,30]);
 for(x=[57,89])for(y=[-11,32])translate([x,y,33])cube([3.5,6,9],center=true);
 }}
module servo_pulley(){difference(){union(){cylinder(d=25,h=2);translate([0,0,2])cylinder(d=20,h=5);translate([0,0,7])cylinder(d=25,h=2);}horn_pattern();}}
module head(){difference(){union(){
 cylinder(d=12,h=13);translate([0,0,12])cylinder(d=64,h=2);translate([0,0,14])cylinder(d=59,h=5);
 translate([0,0,19])cylinder(d=64,h=2);translate([0,0,20])cylinder(d=40,h=8);
 for(a=[0:90:270])rotate([0,0,a])translate([0,-5,24])cube([108,10,4]);
 translate([0,0,24])ring(110,106,5);
 translate([0,0,24])difference(){scale([1,1,65/110])sphere(r=110);scale([1,1,63.4/108.4])sphere(r=108.4);translate([-120,-120,-120])cube([240,240,120]);}
 // Eye and lamps are permanently integrated into this single connected dome.
 translate([0,-98,48])rotate([90,0,0]){cylinder(d=15,h=75);translate([0,0,65])cylinder(d=30,h=13);translate([0,0,77])cylinder(d=19,h=2);}
 for(x=[-60,60])translate([x,0,74]){cylinder(d=23,h=7);translate([0,0,6])cylinder(d1=21,d2=13,h=19);}
 }
 hole(8.5,70);translate([0,0,27])cylinder(d=24,h=100);
 // Axial socket access remains open through the dome crown; no extra cap file.
 }}
// Preview views use delivered meshes to avoid OpenCSG occlusion artifacts.
// Regenerate STLs after geometry changes before rendering these views.
module print_mesh(name){import(str("../stl/",name,".stl"),convexity=12);}
module assembly(explode=0){union(){
 color("#45403b")translate([0,0,base_z])print_mesh("01_base");
 for(sx=[-1,1])for(sy=[-1,1]){
  color("#dc9823")translate([sx*122.5,sy*60,31.5])rotate([0,90,0])cylinder(d=63,h=29,center=true);
  color("#f0b72b")translate([sx*95,sy*60,base_z+6])scale([sx,sy,1])motor_envelope();
 }
 color("#273443")translate([-57,-35,base_z+6])cube([114,70,76]);
 color("#947042")translate([0,0,base_z+54+explode])print_mesh("02_lower_skirt");
 color("#aa8350")translate([0,0,base_z+164+explode*2])print_mesh("03_upper_skirt");
 color("#957044")translate([0,0,base_z+264+explode*3])print_mesh("04_shoulder");
 color("#252528")translate([0,-107,base_z+264+50+explode*3])rotate([90,0,0])cylinder(d=68,h=2);
 color("#2c2c30")translate([-25.76,108,base_z+264+52+explode*3])cube([51.52,2,25.04]);
 color("#45badd")translate([-13,114,base_z+264+58+explode*3])cube([26,1,15]);
 for(x=[-48,48]){
  color("#24252a")translate([x-12,-137,base_z+264+58+explode*3])cube([24,12,31]);
  color("#707070")translate([x,-131,base_z+264+90+explode*3])pitch_carrier();
  color("#24252a")translate([x+4,-137,base_z+264+98+explode*3])cube([27,12,36]);
  color("#afb1b2")translate([x-3,-131,base_z+264+120+explode*3])rotate([90,0,-90])arm(x<0?"plunger":"emitter");
 }
 color("#64615a")translate([0,0,base_z+364+explode*4])print_mesh("05_neck");
 color("#22252a")translate([62.425,-10.025,base_z+364+34+explode*4])cube([20.15,40.15,37.2]);
 color("#79766a")translate([72.5,0,base_z+364+79+explode*4])servo_pulley();
 color("#b48c51")translate([0,0,base_z+431+explode*5])print_mesh("06_head");
 }}
module mesh_section(){
 for(p=[["01_base",0,"#45403b"],["02_lower_skirt",54,"#947042"],["03_upper_skirt",164,"#aa8350"],["04_shoulder",264,"#957044"],["05_neck",364,"#64615a"],["06_head",431,"#b48c51"]])color(p[2])difference(){translate([0,0,base_z+p[1]])print_mesh(p[0]);translate([0,-400,-10])cube([450,800,1300]);}
 color("#273443")translate([-57,-35,base_z+6])cube([57,70,76]);
}
if(part=="01_base")base();
else if(part=="02_lower_skirt")skirt(150,125,110,true);
else if(part=="03_upper_skirt")skirt(125,110,100,false);
else if(part=="04_shoulder")shoulder();
else if(part=="05_neck")neck();
else if(part=="06_head")head();
else if(part=="07_pitch_carrier")pitch_carrier();
else if(part=="08_plunger_arm")translate([0,0,13])arm("plunger");
else if(part=="09_emitter_arm")translate([0,0,3])arm("emitter");
else if(part=="10_servo_pulley")servo_pulley();
else if(part=="assembly")assembly();
else if(part=="rear")assembly();
else if(part=="exploded")assembly(44);
else if(part=="section")mesh_section();
else if(part=="base_view")color("#70706b")print_mesh("01_base");
else assert(false,str("Unknown part: ",part));
