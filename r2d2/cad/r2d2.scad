// R2-24. Millimetres. X right, Y forward, Z up. Floor Z=0.
// Involute gear generator supplied with OpenSCAD/MCAD, LGPL-2.1.
use <MCAD/involute_gears.scad>
part="assembly";
$fn=64;
M3=3.4; M4=4.5; skin=0.8;
module hole(d=M3,h=40){cylinder(d=d,h=h,center=true,$fn=24);}
module slot(l=8,d=M3,h=40){hull()for(x=[-l/2,l/2])translate([x,0,0])hole(d,h);}
module ring(ro,ri,h){difference(){cylinder(r=ro,h=h);translate([0,0,-.1])cylinder(r=ri,h=h+.2);}}
module horn(){hole(5,40);for(a=[0:90:270])rotate([0,0,a])translate([8,0,0])slot(4,2.2,40);}
module spur(n=40,h=6,bore=8.5){gear(number_of_teeth=n,circular_pitch=270,pressure_angle=20,
 clearance=.25,gear_thickness=h,rim_thickness=h,hub_thickness=h,hub_diameter=20,
 bore_diameter=bore,backlash=.2,involute_facets=8);}
module body_skin(upper=false){difference(){union(){ring(130,130-skin,140);ring(130,120,2);translate([0,0,138])ring(130,120,2);}
 if(upper)for(s=[-1,1])scale([s,1,1])translate([115,-34,-1])cube([25,68,20]);}}
module body_frame(){difference(){union(){ring(130,120,5);
 intersection(){cylinder(r=128,h=5);union(){translate([-130,-4,0])cube([260,8,5]);translate([-4,-130,0])cube([8,260,5]);
 for(s=[-1,1]){translate([-110,s*75-3,0])cube([220,6,5]);translate([s*75-3,-110,0])cube([6,220,5]);translate([-115,s*20-3,0])cube([230,6,5]);}}}
 for(x=[-75,75])for(y=[-75,75])translate([x,y,0])cylinder(d=15,h=5);
 for(x=[-105,105])for(y=[-20,20])translate([x,y,0])cylinder(d=15,h=5);}
 for(x=[-75,75])for(y=[-75,75])translate([x,y,0])hole(M4,14);
 for(x=[-105,105])for(y=[-20,20])translate([x,y,0])hole(M4,14);}}
module rod_support(h){difference(){cylinder(d=10,h=h,$fn=32);translate([0,0,h/2])hole(M4,h+2);}}
module body_lower(){union(){body_frame();translate([0,0,5]){body_skin();deck_adapter();}
 translate([0,0,8])battery_tray();for(x=[-75,75])for(y=[-75,75])translate([x,y,8])rod_support(137);
 // Continuous locating lip: .3mm radial and vertical clearance in upper socket.
 translate([0,0,144])ring(129,127.2,4);}}
module body_upper(){difference(){union(){body_frame();translate([0,0,5]){body_skin(true);deck_adapter();}
 for(x=[-75,75])for(y=[-75,75]){translate([x,y,8])rod_support(97);translate([x,y,109])rod_support(36);}
 translate([0,0,105])head_deck();translate([0,0,145])body_frame();translate([0,0,150])neck();}
 translate([0,0,-.1])ring(129.3,126.9,3.4);}}
module foot_deck(){
 difference(){union(){translate([-55,-110,0])cube([110,220,5]);translate([0,0,5])cylinder(d=32,h=5);}
  for(y=[-45,45]){for(x=[-18,18])translate([x,y-50,0])hole(M3,25);translate([0,y+20,0])hole(M3,25);}
  for(y=[-20,20])translate([0,y,0])hole(M4,25);
  hole(8.5,30);translate([0,0,-.1])cylinder(d=13.4,h=6.5,$fn=6);
  for(x=[-46,46])for(y=[-90,90])translate([x,y,0])hole(M3,20);
  for(x=[-37,37])for(y=[-70,-35,0,35,70])translate([x,y,0])cube([18,22,16],center=true);
 }
}
module foot_cover(){
 difference(){union(){translate([-56,-111,0])difference(){cube([112,222,28]);translate([1.2,1.2,-1])cube([109.6,219.6,27.8]);}
  for(x=[-46,46])for(y=[-90,90])translate([x,y,0])cylinder(d=9,h=28);}
  translate([0,0,15])cube([58,68,40],center=true);
  for(x=[-46,46])for(y=[-90,90])translate([x,y,14])hole(M3,40);
 }
}
module motor_cradle(){
 difference(){union(){translate([-11,-60,0])cube([22,74,3]);
  for(x=[-11,9.8])translate([x,-57,3])cube([1.2,64,5]);
  for(x=[-18,18]){translate([x,-50,0])cylinder(d=8,h=49);hull(){translate([x,-50,0])cylinder(d=8,h=3);translate([0,-50,0])cylinder(d=8,h=3);}}
  translate([0,20,0])cylinder(d=9,h=49);translate([-4.5,8,0])cube([9,13,3]);}
  for(x=[-18,18])translate([x,-50,24])hole(M3,70);translate([0,20,24])hole(M3,70);
  for(x=[-7,7])for(y=[-40,-15])translate([x,y,0])cube([3.5,5,14],center=true);
 }
}
module side_arm(){difference(){union(){
 difference(){translate([-25,-30,0])cube([50,60,250]);translate([-23.8,-28.8,-1])cube([47.6,57.6,252]);}
 for(z=[0,246])translate([-25,-30,z])cube([50,60,4]);
 translate([-190,0,250])shoulder_bridge();
 translate([0,0,255])difference(){translate([-29,-34,0])cube([58,68,40]);translate([-27.8,-32.8,-1])cube([55.6,65.6,39.8]);}
 }
 for(y=[-20,20])translate([0,y,137])hole(M4,280);
 translate([0,0,125])cube([28,20,252],center=true);
 // Windows allow a wrench to reach the leg-rod nuts inside the shoulder.
 for(y=[-34,34])translate([0,y,263])cube([24,8,16],center=true);
}}
module shoulder_bridge(){
 difference(){union(){translate([95,-32,0])cube([120,64,5]);for(y=[-32,28])translate([95,y,0])cube([120,4,18]);}
  for(x=[105,190])for(y=[-20,20])translate([x,y,0])hole(M4,50);
  translate([148,0,0])cube([55,44,40],center=true);}
}
module rear_bracket(){
 // World-relative origin is rear spindle at (0,-180,110).
 difference(){union(){translate([-45,-38,0])cube([120,146,4]);
  for(x=[-45,71])translate([x,65,0])cube([4,43,55]);translate([-45,65,50])cube([120,43,5]);
  for(x=[-45,71])translate([x,-38,0])cube([4,146,12]);}
  translate([0,0,0])hole(16,20);for(a=[45:90:315])rotate([0,0,a])translate([24,0,0])hole(M3,15);
  translate([45,0,0])cube([36.4,60.4,30],center=true);
  for(x=[32.5,57.5])for(y=[-35,35])translate([x,y,0])slot(6,M3,20);
  for(x=[-35,35])for(y=[77,98])translate([x,y,52])hole(M4,20);
  translate([0,60,0])cube([55,25,30],center=true);
 }
}
module rear_attach(){
 difference(){translate([-80,-108,0])cube([160,42,5]);for(x=[-75,75])translate([x,-75,0])hole(M4,20);
  for(x=[-35,35])for(y=[-103,-82])translate([x,y,0])hole(M4,20);}
}
module bearing_tower(){difference(){union(){cylinder(d=58,h=3);cylinder(d=34,h=26);}
 hole(12,70);translate([0,0,-.1])cylinder(d=22.2,h=7.1);translate([0,0,19])cylinder(d=22.2,h=8);
 for(a=[45:90:315])rotate([0,0,a])translate([24,0,0])hole(M3,12);
 for(a=[0,120,240])rotate([0,0,a])translate([14,0,24])hole(2.6,10);}}
module bearing_cap(){difference(){cylinder(d=34,h=3);hole(16,14);for(a=[0,120,240])rotate([0,0,a])translate([14,0,0])hole(M3,14);}}
module race_spacer(){difference(){cylinder(d=11.5,h=12);hole(8.4,30);}}
module spindle_sleeve(){difference(){cylinder(d=12,h=38);hole(8.5,100);}}
module gear_hub(){difference(){union(){cylinder(d=12,h=11);translate([0,0,10])spur();translate([0,0,16])cylinder(d=36,h=3);}
 hole(8.5,60);translate([0,0,16])cylinder(d=13.4,h=5,$fn=6);for(a=[0:90:270])rotate([0,0,a])translate([12,0,17])hole(M3,12);}}
module servo_pinion(){difference(){spur(20,6,5);horn();}}
module servo_mount(){difference(){union(){translate([-18,-30,-8])cube([36,60,3]);for(y=[-40,29])translate([-18,y,0])cube([36,11,3]);for(x=[-18,14])translate([x,-30,-8])cube([4,60,26]);}
 for(x=[-12.5,12.5])for(y=[-35,35])translate([x,y,0])slot(6,M3,14);
 for(x=[-10,10])for(y=[-22,-4])translate([x,y,-6])cube([4,5,14],center=true);}}
module servo_shim(h=1){cube([20,40,h]);}
module head_deck(){difference(){union(){ring(128,117,4);for(a=[45:90:315])rotate([0,0,a])translate([0,-7,0])cube([124,14,4]);cylinder(d=62,h=4);translate([20,-38,0])cube([50,76,4]);}
 hole(16,20);for(a=[45:90:315])rotate([0,0,a])translate([24,0,0])hole(M3,14);
 for(x=[32.5,57.5])for(y=[-35,35])translate([x,y,0])slot(6,M3,14);
 for(a=[45:90:315])rotate([0,0,a])translate([sqrt(75*75*2),0,0])hole(M4,14);
 translate([45,0,0])cube([36.4,60.4,20],center=true);
}}
module neck(){union(){ring(130,128.4,12);ring(130,119,2);}}
module head_plate(){difference(){union(){cylinder(d=36,h=3);for(a=[0:90:270])rotate([0,0,a])translate([0,-6,0])cube([123,12,3]);}
 hole(16,16);for(a=[0:90:270])rotate([0,0,a])for(r=[12,119])translate([r,0,0])hole(M3,14);}}
module dome_spacer(){difference(){cylinder(d=8,h=6.6);hole(M3,20);}}
module dome(){difference(){union(){difference(){sphere(r=130);sphere(r=129.2);translate([-140,-140,-140])cube([280,280,140]);}
 ring(130,119,3);for(a=[0:90:270])rotate([0,0,a])translate([119,0,0])cylinder(d=12,h=5);}
 for(a=[0:90:270])rotate([0,0,a])translate([119,0,0]){hole(M3,20);translate([0,0,1.5])cylinder(d=6.4,h=4,$fn=6);}
}}
module eye(){difference(){union(){cylinder(d=32,h=3);translate([0,0,3])cylinder(d1=28,d2=23,h=17);}translate([0,0,3])cylinder(d=18,h=20);}}
module detail_panel(){difference(){cube([72,32,2]);for(y=[5,13,21])translate([5,y,1])cube([62,4,3]);}}
module battery_tray(){difference(){union(){translate([-62,-40,0])cube([124,80,3]);for(x=[-62,58])translate([x,-40,0])cube([4,80,15]);for(y=[-40,36])translate([-62,y,0])cube([124,4,15]);}
 for(x=[-35,35])for(y=[-35,35])translate([x,y,0])cube([22,4,12],center=true);
 for(x=[-45,45])for(y=[-30,30])translate([x,y,0])hole(M3,14);translate([0,38,12])cube([36,10,20],center=true);}}
module utility_deck(){difference(){translate([-85,-60,0])cube([170,120,3]);
 for(x=[-75,75])for(y=[-45,45])translate([x,y,0])hole(M3,16);
 for(x=[-70:14:70])for(y=[-40:20:40])translate([x,y,0])slot(8,3.4,14);}}
module deck_adapter(){difference(){translate([-85,-80,0])cube([170,160,3]);
 for(x=[-75,75])for(y=[-75,75])translate([x,y,0])hole(M4,14);
 for(x=[-45,45])for(y=[-30,30])translate([x,y,0])hole(M3,14);
 for(x=[-75,75])for(y=[-45,45])translate([x,y,0])hole(M3,14);
 for(x=[-25,25])for(y=[-58,0,58])translate([x,y,0])cube([32,28,20],center=true);}}
module pcb_spacer(){difference(){cylinder(d=7,h=6);hole(2.8,20);}}
module speaker_mount(){difference(){union(){translate([-44,-44,0])cube([88,88,3]);for(x=[-44,40])translate([x,-44,0])cube([4,88,12]);}
 hole(69,30);for(x=[-39,39])for(y=[-33,33])translate([x,y,0])cube([4,8,15],center=true);
 for(x=[-30,30])for(y=[-30,30])translate([x,y,0])hole(M3,15);}}
module switch_plate(){difference(){cube([70,42,3]);for(x=[20,50])translate([x,21,0])hole(12.5,14);for(x=[5,65])for(y=[5,37])translate([x,y,0])hole(M3,14);}}
module coupon(){difference(){cube([90,50,5]);for(i=[0:3])translate([12+i*20,12,0])hole(3.1+.1*i,16);translate([15,34,0])hole(4.5,16);translate([40,33,0])hole(22.2,16);translate([66,33,0])hole(8.5,16);}}
module pod(x,y,rear=false){
 color("white")translate([x,y,65])foot_deck();if(!rear)color("white")translate([x,y,70])foot_cover();
 for(dy=[-45,45]){color("gray")translate([x,y+dy,16])motor_cradle();
 color("gold")translate([x-9.3,y+dy-57,20.3])cube([18.6,70,22.44]);
 for(dx=[-33,33])color("darkorange")translate([x+dx,y+dy,31.5])rotate([0,90,0])cylinder(d=63,h=29,center=true);}
}
module assembly(explode=0,cut=false){difference(){union(){
 for(x=[-190,190]){pod(x,0);color("white")translate([x,0,70])scale([x<0?-1:1,1,1])side_arm();
 color("royalblue")translate([x-20,30,120])cube([40,2,150]);
 }
 pod(0,-180,true);color("gray")translate([0,-180,110])rear_bracket();color("gray")translate([0,0,165])rear_attach();
 color("silver")translate([0,-180,114])bearing_tower();color("silver")translate([0,-180,140])bearing_cap();color("steelblue")translate([0,-180,141])gear_hub();
 color("gray")translate([45,-180,114])servo_mount();color("steelblue")translate([45,-180,151])rotate([0,0,9])servo_pinion();
 color("silver")translate([0,-180,75])spindle_sleeve();
 color("white")translate([0,0,170+explode])body_lower();color("white")translate([0,0,315+explode*2])body_upper();
 color("#253342")translate([-56,-33,181])cube([112,66,71]);color("gray")translate([0,0,329])utility_deck();
 for(z=[240,290,350,397])color("royalblue")translate([-36,130,z])rotate([90,0,0])detail_panel();
 color("gray")translate([0,0,424+explode*2])bearing_tower();color("gray")translate([0,0,450+explode*2])bearing_cap();
 color("steelblue")translate([0,0,451+explode*3])gear_hub();color("gray")translate([45,0,424+explode*2])servo_mount();color("steelblue")translate([45,0,461+explode*3])rotate([0,0,9])servo_pinion();
 color("gray")translate([0,0,470+explode*3])head_plate();
 for(a=[0:90:270])rotate([0,0,a])color("gray")translate([119,0,473+explode*3])dome_spacer();
 color("silver")translate([0,0,479.6+explode*4])dome();
 color("#102b58")translate([0,114,535+explode*4])rotate([-65,0,0])eye();
 }if(cut)translate([0,-400,-10])cube([400,800,1000]);}}
if(part=="body_lower")body_lower();else if(part=="body_upper")body_upper();else if(part=="arm_right")side_arm();else if(part=="arm_left")mirror([1,0,0])side_arm();
else if(part=="foot_deck")foot_deck();else if(part=="foot_cover")foot_cover();
else if(part=="motor_cradle")motor_cradle();else if(part=="rear_bracket")rear_bracket();else if(part=="rear_attach")rear_attach();
else if(part=="bearing_tower")bearing_tower();else if(part=="bearing_cap")bearing_cap();else if(part=="race_spacer")race_spacer();
else if(part=="spindle_sleeve")spindle_sleeve();else if(part=="gear_hub")gear_hub();else if(part=="servo_pinion")servo_pinion();
else if(part=="servo_mount")translate([0,0,8])servo_mount();else if(part=="servo_shim_1")servo_shim(1);else if(part=="servo_shim_2")servo_shim(2);else if(part=="servo_shim_4")servo_shim(4);
else if(part=="head_plate")head_plate();else if(part=="dome_spacer")dome_spacer();
else if(part=="dome")dome();else if(part=="eye")eye();else if(part=="detail_panel")detail_panel();
else if(part=="utility_deck")utility_deck();else if(part=="pcb_spacer")pcb_spacer();
else if(part=="speaker_mount")speaker_mount();else if(part=="switch_plate")switch_plate();else if(part=="coupon")coupon();
else if(part=="check_stack")intersection(){translate([0,0,170])body_lower();translate([0,0,315])body_upper();}
else if(part=="check_shoulder")intersection(){translate([0,0,315])body_upper();translate([190,0,70])side_arm();}
else if(part=="check_neck")intersection(){translate([0,0,465])neck();translate([0,0,470])head_plate();}
else if(part=="check_rear_sleeve")intersection(){translate([0,0,110])rear_bracket();translate([0,0,75])spindle_sleeve();}
else if(part=="check_gears")for(a=[0,2,4,6,8])intersection(){rotate([0,0,a])gear_hub();translate([45,0,10])rotate([0,0,9-2*a])servo_pinion();}
else if(part=="section")assembly(0,true);else if(part=="exploded")assembly(25);else if(part=="assembly")assembly();else assert(false,part);
