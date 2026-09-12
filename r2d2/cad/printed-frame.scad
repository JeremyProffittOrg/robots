// Revision D printed frame development. mm; X shoulders, Y forward, Z up.
// Nominal fits require a material-specific fit check before the loaded prototype.
// This module replaces custom chassis plates; no printed strength rating is implied.
FRAME_RAIL_X=72; FRAME_RAIL_Y=52; FRAME_RAIL_BOTTOM=178; FRAME_RAIL_LENGTH=228;
RAIL_SOCKET=21.2;
module pf_xhole(d,h){rotate([0,90,0])cylinder(d=d,h=h,center=true);}
module pf_yhole(d,h){rotate([90,0,0])cylinder(d=d,h=h,center=true);}
module pf_shaft_tunnel(h){rotate([0,90,0])linear_extrude(h,center=true)union(){circle(d=12.2);polygon([[-4.32,-4.32],[-8.64,0],[-4.32,4.32]]);}}
module pf_round_box(w,d,h,r=3){linear_extrude(h)hull()for(x=[-w/2+r,w/2-r])for(y=[-d/2+r,d/2-r])translate([x,y])circle(r=r);}
module extrusion_2020(length){
 // MISUMI HFS5-2020 section. Slot openings are real geometry, not a solid bar.
 linear_extrude(length)difference(){square([20,20],center=true);circle(d=4.2);
 for(a=[0:90:270])rotate(a){translate([-3,8])square([6,3]);translate([-6,4])square([12,4.01]);}}
}
module pf_rail_socket(x,y,z,h){translate([x,y,z])translate([-RAIL_SOCKET/2,-RAIL_SOCKET/2,-.1])cube([RAIL_SOCKET,RAIL_SOCKET,h+.2]);}
module frame_lower(){
 difference(){union(){
  // Open-front battery tray; ribs connect the four extrusion sockets.
  translate([0,0,166])pf_round_box(176,150,8);
  for(x=[-FRAME_RAIL_X,FRAME_RAIL_X])for(y=[-FRAME_RAIL_Y,FRAME_RAIL_Y])
   translate([x,y,174])pf_round_box(33.2,33.2,44,3);
  for(x=[-FRAME_RAIL_X,FRAME_RAIL_X])translate([x-5,-68,174])cube([10,136,15]);
  translate([-82,-67,174])cube([164,10,15]);
  for(x=[-60,60])translate([x-4,-40,174])cube([8,80,8]);
 }
 for(x=[-FRAME_RAIL_X,FRAME_RAIL_X])for(y=[-FRAME_RAIL_Y,FRAME_RAIL_Y])pf_rail_socket(x,y,174,45);
 // Front post opening; battery sits behind this bay.
 translate([-28,27,165])cube([56,49,65]);
 for(x=[-38,38])for(y=[-35,-5])translate([x,y,165])linear_extrude(11)pf_round_slot(23,4);
 for(a=[45,135,225,315])rotate([0,0,a])translate([80,0,165])cylinder(d=3.4,h=12);
 }
}
module pf_round_slot(w,d){hull()for(x=[-(w-d)/2,(w-d)/2])translate([x,0])circle(d=d,$fn=24);}
module frame_upper(){
 difference(){union(){
  translate([0,0,406])pf_round_box(176,150,9);
  for(x=[-FRAME_RAIL_X,FRAME_RAIL_X])for(y=[-FRAME_RAIL_Y,FRAME_RAIL_Y])
   translate([x,y,350])pf_round_box(33.2,33.2,56,3);
  for(s=[-1,1])scale([s,1,1]){
   translate([80,-66,350])cube([8,132,65]);
   for(y=[-27,27])translate([61,y-5,350])cube([27,10,65]);
  }
  translate([-82,-67,386])cube([164,10,20]);
 }
 for(x=[-FRAME_RAIL_X,FRAME_RAIL_X])for(y=[-FRAME_RAIL_Y,FRAME_RAIL_Y])pf_rail_socket(x,y,349,57.1);
 // Keep the proven head bearing and friction-wheel locations.
 translate([0,0,405])cylinder(d=16,h=12);
 translate([30,-65,405])cube([34,118,12]);
 translate([59,-32,405])cube([34,64,12]);
 for(a=[45:90:315])rotate([0,0,a])translate([24,0,405])cylinder(d=3.4,h=12);
 for(x=[23,69])for(y=[-50,45])translate([x,y,405])cylinder(d=3.4,h=12);
 }
}
module shoulder_carrier(){
 // Integral right shoulder support; reflect X for the left. Shared axle interface remains under development.
 difference(){union(){
  translate([88,-35,350])cube([8,70,68]);
  translate([96,0,390])rotate([0,90,0])cylinder(d=60,h=40);
  for(y=[-27,27])hull(){translate([88,y-4,361])cube([8,8,48]);translate([130,y-4,380])cube([6,8,20]);}
 }
 translate([112,0,390])pf_shaft_tunnel(52);
 }
}
module printed_foot_core(center=false){
 // Printed compression columns bridge the wheel-row gap; no welded foot frame.
 difference(){union(){
  translate([-11.3,-96,12])cube([22.6,151,8]);
  for(y=[-37,37])for(x=[-11.3,9.7])translate([x,y-56,19.7])cube([1.6,66,6]);
  for(x=[-23,15])translate([x,-4,19])cube([8,8,47]);
  translate([-23,-4,12])cube([46,8,8]);
  translate([-32,-25,65])cube([64,50,12]);
  if(center){
   for(x=[-20,8])translate([x,-15,76])cube([12,30,52]);
   translate([-47,-80,65])cube([34,60,8]);
   translate([-32,-25,65])cube([20,15,12]);
   for(x=[-35,-25])for(y=[-74.4,-24.9])translate([x,y,73])cylinder(d=7,h=17.1);
  }else translate([-11,-15,76])cube([8,30,76]);
 }
 for(y=[-37,37])for(yy=[-42,-15])for(x=[-6,6])translate([x,y+yy,16])cube([3.2,4.5,12],center=true);
 for(x=[-27,27])for(y=[-17,17])translate([x,y,64])cylinder(d=3.4,h=15);
 if(center){
  translate([0,0,113])pf_xhole(12.2,44);
  translate([-40.85,-71,64])cube([21.7,42.7,12]);
  for(x=[-35,-25])for(y=[-74.4,-24.9])translate([x,y,64])cylinder(d=3.4,h=28);
 }else for(z=[119,139])translate([-7,0,z])pf_xhole(5.5,12);
 }
}
module printed_frame_assembly(){
 color("#c6d9e7")frame_chassis();
 color("#b5bdc6")for(x=[-FRAME_RAIL_X,FRAME_RAIL_X])for(y=[-FRAME_RAIL_Y,FRAME_RAIL_Y])
 translate([x,y,FRAME_RAIL_BOTTOM])extrusion_2020(FRAME_RAIL_LENGTH);
 color("#a3adb7")translate([-180,0,390])rotate([0,90,0])cylinder(d=12,h=360);
 for(x=[-72,72])for(y=[-52,52])color("#365e82")translate([x,y,170])rail_key();
}
module frame_chassis(){
 // One H2D-sized print replaces tray/deck, bolted carriers and column clamps.
 difference(){union(){
  frame_lower();frame_upper();
  printed_post_guide();pf_front_guide_frame()printed_post_mount();
  for(s=[-1,1])scale([s,1,1])shoulder_carrier();
  for(x=[-72,72])for(y=[-52,52])translate([x,y,166])pf_round_box(33.2,33.2,240,3);
  translate([-136,0,390])rotate([0,90,0])cylinder(d=36,h=272);
 }
 translate([0,0,390])pf_shaft_tunnel(276);
 for(x=[-72,72])for(y=[-52,52]){
  pf_rail_socket(x,y,165,241.01);
  translate([x-12.2,y-23,170])cube([24.4,46,8.3]);
 }
 // Head mount/cable openings remain clear where the frame members merge.
 translate([0,0,404])cylinder(d=16,h=12);
 translate([30,-65,405])cube([34,118,12]);translate([59,-32,405])cube([34,64,12]);
 }
}
module rail_key(){
 // Printed captive key: vertical rail load bears on broad solid chassis ledges.
 // A separate printed cross-pin blocks withdrawal; it does not carry rail weight.
 difference(){union(){translate([-12,-16.6,0])cube([24,39.6,8]);translate([-15,-18.6,0])cube([30,2,10]);}
 translate([0,18.8,4])pf_xhole(4.2,27);
 }
}
module rail_key_pin(){
 // Print flat: hexagonal shaft has a stable lower face, with a split detent tip.
 difference(){union(){rotate([0,90,0])cylinder(d=4,h=42,$fn=6);
 translate([-2,0,0])rotate([0,90,0])cylinder(d=8,h=2.1,$fn=6);
 translate([39,0,0])rotate([0,90,0])cylinder(d1=4.6,d2=3.6,h=3,$fn=6);}
 translate([33,-.45,-4])cube([10,.9,8]);}
}
module pf_front_guide_frame(){
 translate([0,40,240])multmatrix([[1,0,0,0],[0,cos(35),sin(35),0],[0,sin(35),-cos(35),0],[0,0,0,1]])children();
}
module printed_post_guide(){
 difference(){union(){
  pf_front_guide_frame()translate([-23,-23,-180])cube([46,46,180]);
  pf_front_guide_frame(){
   translate([-23,-47,-54])cube([82,18,34]);
   translate([-23,-30,-54])cube([46,9,34]);
  }
  // Two diagonal support levels tie directly to opposite pairs of2020 uprights.
  for(level=[[260,52],[340,-52]])for(x=[-72,72]){
   translate([x,level[1],level[0]-14])pf_round_box(33.2,33.2,28,3);
   hull(){translate([x-5,level[1]-10,level[0]-10])cube([10,20,20]);
    translate([-23,40+(240-level[0])*tan(35)-10,level[0]-10])cube([46,20,20]);}
  }
 }
 pf_front_guide_frame()translate([-13,-13,-181])cube([26,26,182]);
 pf_front_guide_frame()for(x=[32,50])for(t=[-46,-28])translate([x,-38,t])pf_yhole(4.5,24);
 for(level=[[260,52],[340,-52]])for(x=[-72,72]){
  pf_rail_socket(x,level[1],level[0]-15,30);
 }
 // Pad screws stay behind the sliding faces; heads sit on the guide outside.
 pf_front_guide_frame()for(t=[-130,-20])for(a=[0:90:270])rotate([0,0,a])for(z=[t-5,t+5])
 translate([18,0,z])pf_xhole(2.4,14);
 }
}
module printed_post_adapter(){
 // Guide-local coordinates. Top socket is20mm; M12 nut is mechanically captured.
 difference(){union(){
  translate([-20,-20,-97.5])cube([40,40,65]);
  translate([-20,-29,-85])cube([76,10,88]);
  for(x=[26,44])translate([x,-29,-9])cube([10,39,18]);
 }
 translate([-10.6,-10.6,-97.6])cube([21.2,21.2,35.2]);
 translate([0,0,-56])cylinder(d=12.5,h=24);
 translate([0,0,-49])cylinder(d=22.4,h=10.5,$fn=6);
 // Accessible nut insertion from the side; load bears on an integral10mm ledge.
 translate([-12,-30,-49])cube([24,30,10.5]);
 for(z=[-87,-73])translate([0,0,z])pf_xhole(5.5,44);
 translate([40,0,0])pf_xhole(4.5,36);
 }
}
module printed_post_mount(){
 difference(){union(){translate([23,-29.2,-54])cube([36,8.2,34]);
 for(x=[26,44])translate([x,-29,-46])cube([10,39,18]);}
 translate([40,0,-37])pf_xhole(4.5,40);
 for(x=[32,50])for(t=[-46,-28])translate([x,-25,t])pf_yhole(4.5,12);
 }
}
