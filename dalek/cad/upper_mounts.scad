// MOUNT-1 upper structure. Included by dalek.scad after shared helpers.
// Shoulder + neck is one186mm print. Arms install through its open bottom.
// MG92B maker A35, B22.6, D12, E31.5, F22.8mm; actual shaft offset and
// ear-hole coordinates are not dimensioned. Slots accept a measured fit.
// Yaw body center nominal X-5 from shaft; pitch body center Z30 from shaftZ35.
module arm_servo_relief(){
 // The fixed pitch case begins4mm beyond the arm attachment plane.
 // A short flat gives0.5mm nominal case clearance; the printed root is
 // 9.5mm thick and12mm wide before the existing horn holes.
 translate([0,6.1,0])rotate([90,0,0])linear_extrude(height=12.2)
 polygon([[0,-7],[14,-7],[14,-6],[8,-3.5],[0,-3.5]]);
}
module speaker_mount_frame(){union(){
 // The rear speaker mounts after both arms; its frame leaves the front clear.
 // Eight-mm uprights and the bottom beam carry the unchanged four mounts.
 translate([-43,52.5,4])cube([86,4,4]);
 for(x=[-30,30]){
  translate([x-4,52.5,4])cube([8,4,69]);
  for(z=[13,73])translate([x,56.5,z])rotate([90,0,0])cylinder(d=8,h=4,$fn=32);
 }
}}
module yaw_servo_support(){union(){
 // Nominal servo baseZ7 aligns35mm overall height with existing shaftZ42.
 translate([-26,-13,4])cube([44,26,3]);
 // Side walls locate padded case; ledges carry servo ears with M2 hardware.
 for(x=[-27,14])translate([x,-13,6])cube([4,26,20]);
 for(x=[-26,6.8]){
  translate([x,-7,25.8])cube([9.2,14,4]);
  for(y=[-13,7])translate([x,y,6])cube([9.2,6,23.8]);
 }
}}
module yaw_servo_clearance(){
 translate([-17.3,-6.5,7])cube([24.6,13,32]);
 // Slots align the actual ear holes; screw from above, nut held below.
 for(x=[-20,10])translate([x,0,28])slot(3,2.2,10);
 // Existing alternative: two case loops, tie tails face inward.
 for(x=[-11,3])for(y=[-10,10])translate([x,y,6])cube([5,3,14],center=true);
 // Buried return tunnels keep ties above the mating skirt flange.
 for(x=[-11,3])translate([x-2.5,-12,2])cube([5,24,2]);
 // Narrow rear windows admit a measured nut-holding tool under each ledge.
 for(x=[-19.5,9.5])translate([x-3.3,6.5,22.8])cube([6.6,7.5,3.2]);
}
module pitch_carrier(){difference(){union(){
 translate([-14,-10,0])cube([49.5,30,4]);translate([32.5,-10,0])cube([3,27,49]);
 for(y=[-10,13])translate([5,y,3])cube([30.5,4,9]);
 // Ear supports are behind the servo ears, clear of the off-center body.
 for(z=[11.5,41.8]){
  translate([9.2,-7,z])cube([4,14,6.7]);
  for(y=[-10,7])translate([9.2,y,z])cube([26.3,3,6.7]);
 }
 }horn_pattern();
 for(z=[24,36])for(y=[-7,13])translate([34,y,z])cube([12,4,5],center=true);
 for(z=[15,45])translate([11.2,0,z])rotate([0,90,0])slot(2,2.2,12);
}}
module gunbox_shell(cx){difference(){
 translate([cx-45,-113,6])rounded_box([90,52,103],6);
 translate([cx-41,-109,10])rounded_box([82,58,95],4);
 translate([cx,-94,77])sphere(r=29.2,$fn=64);
 translate([cx,-113,77])rotate([90,0,0])cylinder(d=44,h=12,center=true,$fn=64);
 }}
module shoulder_body(){difference(){union(){
 difference(){ring(110,110-wall,shoulder_h);for(cx=[-50,50])translate([cx-41,-109,11])cube([82,50,95]);}
 ring(110,92,6);translate([0,0,shoulder_h-6])ring(110,103,6);
 for(cx=[-50,50])gunbox_shell(cx);
 translate([-12,-111,9])cube([24,5,94]);
 speaker_mount_frame();
 for(s=[-1,1])intersection(){
  hull(){translate([s*40,54.5,4])cylinder(d=8,h=4);translate([s*96,45,4])cylinder(d=8,h=4);}
  translate([-120,-120,0])cube([240,176.5,10]);
 }
 for(x=[-47,53])translate([x,-94,0])yaw_servo_support();
 for(a=[-15:15:195])rotate([0,0,a]){
  translate([109,-4,17])cube([3,8,79]);
  for(z=[23,90])translate([111.5,0,z])rotate([0,90,0])cylinder(d=3.2,h=1.5,$fn=16);
 }
 for(z=[9,103])difference(){translate([0,0,z])ring(113,108,4);for(cx=[-50,50])translate([cx-39,-115,0])cube([78,58,120]);}
 translate([-41,98,40])cube([82,16,48]);
 for(cx=[-50,50])for(dx=[-28,28])for(z=[48,104])translate([cx+dx,-112.5,z])rotate([90,0,0])cylinder(d=4.2,h=1.7,$fn=16);
 }
 groove(110);joint_holes(110,3);
 for(x=[-7,0,7])for(z=[28,35,42,49,56,63,70,77,84])translate([x,-108,z])rotate([90,0,0])hole(4.2,12);
 for(x=[-30,30])for(z=[13,73])translate([x,54.5,z])rotate([90,0,0])hole(M3,12);
 for(x=[-47,53])translate([x,-94,0])yaw_servo_clearance();
 translate([-24.5,108,53])cube([49,16,23]);translate([-26.1,95,51.5])cube([52.2,15,26]);translate([-41,95,57])cube([19,15,14]);
 for(x=[-34,34])for(z=[56,73])translate([x,106,z])rotate([90,0,0])hole(M3,26);
 for(x=[-30,30])translate([x,104,23])rotate([90,0,0])hole(12.5,30);
 }}
module neck(){difference(){union(){
 ring(110,103,6);for(z=[15,30,44])translate([0,0,z])ring(106,99,4);
 for(a=[45:90:315])rotate([0,0,a])translate([98,-4,0])cube([7,8,48]);
 for(a=[7.5:15:352.5])rotate([0,0,a])translate([99,-.8,5])cube([2,1.6,43]);
 // Opaque inner grille liner hides the motor; deliberate service ports remain.
 translate([0,0,5])ring(100.3,99.1,46);
 for(a=[7.5:15:352.5])for(z=[15,30,44])rotate([0,0,a])translate([99.1,-.8,z])cube([1.9,1.6,2]);
 for(a=[45,135,225])rotate([0,0,a])translate([0,-6,40])cube([103,12,4]);
 translate([0,0,40])cylinder(d=38,h=26);
 intersection(){cylinder(r=103,h=40);translate([38,-63,25.2])cube([50,85,4]);}
 for(y=[-59,16])translate([46,y,5])cube([38,4,24.2]);
 translate([30,-41,25.2])cube([18,12,4]);translate([30,-41,25.2])cube([8,12,17.8]);
 translate([84,-4,25.2])cube([10.1,10,4]);translate([90.1,-4,25.2])cube([4,10,9.1]);
 }

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
module shoulder(){union(){shoulder_body();translate([0,0,120])neck();}}
