// R2-24 revision C. mm, X shoulders / Y forward / Z up. Native STL bed orientations below.
include <exterior.scad>
include <kinematics.scad>
include <loadframe.scad>
part="assembly";
stroke=POST_MIN;
head_angle=0;
rear_yaw=0;
explode=part=="exploded"?80:0;
module shoulder_clearance(){for(s=[-1,1])scale([s,1,1])translate([0,0,HIP_Z-BODY_Z])side_plane(90)linear_extrude(60)circle(r=40);}
module rear_clearance(){translate([0,0,-BODY_Z])guide_frame(){
 translate([-23,-23,42])cube([98,46,108]);
 translate([-36,-23,42])cube([14,8,108]);
 translate([-75,-23,60])cube([43,8,90]);
 translate([-79,-47,42])cube([14,34,108]);
 }}
module seam_clearance(){
 intersection(){translate([0,0,SPLIT-5])cylinder(r=R-WALL-.05,h=10);
 for(s=[-1,1])for(k=[-1,1])scale([s,k,1])translate([94,63,SPLIT-5])cube([6,19,10]);}
 translate([0,0,-BODY_Z])guide_frame()translate([-96,-46.875,-6])cube([192,32,12]);
}
module case_tabs(z){for(a=[45,135,225,315])rotate([0,0,a])translate([119,0,z])difference(){hull(){cylinder(d=12,h=4);translate([6,0,0])cylinder(d=12,h=4);}hole(3.4,12);}}
module body_lower(){difference(){union(){exterior_body_lower();translate([0,0,SPLIT-3])ring(R-1.3,R-3.3,6);
 translate([0,0,SPLIT-4])ring(R-1,R-11,4);case_tabs(8);case_tabs(SPLIT-4);}
 rear_clearance();seam_clearance();for(a=[45,135,225,315])rotate([0,0,a])translate([119,0,SPLIT-2]){hole(3.4,12);translate([0,0,-2.1])cylinder(d=6.8,h=2.7,$fn=6);}
 }}
module body_upper(){difference(){union(){exterior_body_upper();translate([0,0,SPLIT])ring(R-1,R-11,4);case_tabs(SPLIT);}
 translate([0,0,SPLIT-.1])ring(R-1,R-3.6,3.4);shoulder_clearance();seam_clearance();
 for(a=[45,135,225,315])rotate([0,0,a])translate([119,0,SPLIT+2])hole(3.4,12);
 for(x=[-18,18])translate([x,-R,H-35])rotate([90,0,0])hole(12.5,16);
 }}
module dome(){difference(){union(){exterior_dome();color(SILVER){ring(88,65,3);cylinder(d=38,h=9);translate([0,0,-15])cylinder(d=14,h=16);
 for(a=[45:90:315])rotate([0,0,a])translate([0,-5,0])cube([R-5,10,3]);}}
 translate([0,0,-5])hole(8.5,45);translate([0,0,3])cylinder(d=15.4,h=7,$fn=6);
 }}
module leg(){difference(){union(){exterior_leg();for(z=[-45,-155,-225])color(WHITE)translate([7,-6,z-6])cube([13.1,12,12]);}
 for(z=[-45,-155,-225])translate([14,0,z])xhole(3.4,40);
 translate([-17,0,0])xhole(34,10);
 }}
module foot(center=false){difference(){union(){exterior_foot(center);
 for(x=[-27,27])for(y=[-17,17])color(WHITE)translate([x,y,10])cylinder(d=9,h=26);
 if(center)color(WHITE)difference(){hull(){translate([-43,-82,8])cube([26,62,1]);translate([-43,-82,48])cube([26,62,1]);}
 translate([-41.2,-80.2,7])cube([22.4,58.4,45]);}
 }
 for(x=[-27,27])for(y=[-17,17])translate([x,y,23])hole(3.4,40);
 if(center){translate([-15,-18,8])cube([30,36,80]);translate([-45,-26,40])cube([30,8,15]);
 translate([-41.2,-80.2,1])cube([22.4,58.4,52]);translate([-48,-81,.1])cube([36,62,6]);
 translate([-50,-74,40])cube([12,40,16]);
 translate([-33,-26,5.9])cube([66,52,4.1]);}
 else translate([-22,-39,29])cube([44,78,100]);
 }}
module drive_cassette(){difference(){union(){translate([-11.3,-96,0])cube([22.6,151,3.8]);
 for(y=[-37,37])for(x=[-11.3,9.7])translate([x,y-56,3.7])cube([1.6,66,6]);
 }
 for(y=[-37,37])for(yy=[-42,-15])for(x=[-6,6])translate([x,y+yy,0])cube([3.2,4.5,12],center=true);
 for(y=[-90,-23,52])translate([0,y,2])hole(3.4,14);
 }}
module bearing_tower(){difference(){union(){cylinder(d=58,h=3);cylinder(d=34,h=26);}
 hole(12,70);translate([0,0,-.1])cylinder(d=22.2,h=7.1);translate([0,0,19])cylinder(d=22.2,h=8);
 for(a=[45:90:315])rotate([0,0,a])translate([24,0,0])hole(3.4,12);
 for(a=[0,120,240])rotate([0,0,a])translate([14,0,24])hole(2.6,10);}}
module bearing_cap(){difference(){cylinder(d=34,h=3);hole(16,14);for(a=[0,120,240])rotate([0,0,a])translate([14,0,0])hole(3.4,14);}}
module head_motor_mount(){difference(){union(){translate([37,-59,0])cube([24,110,3]);translate([40,-56,2.9])cube([18,66,4.7]);for(x=[37,59])translate([x,-59,2.9])cube([2,110,10]);
 translate([17,-55,7.5])cube([22,10,3]);translate([59,-55,7.5])cube([16,10,3]);translate([17,40,7.5])cube([58,10,3]);}
 for(x=[23,69])for(y=[-50,45])translate([x,y,9])hole(3.4,14);
 for(y=[-42,-15])for(x=[43,55])translate([x,y,0])cube([3.2,5,12],center=true);
 }}
module wheel(){color("#d88924")rotate([0,90,0])cylinder(d=63,h=29,center=true,$fn=64);}
module tt(){color("#daa932")translate([-9.3,-57,-11.22])cube([18.6,70,22.44]);color(WHITE)xhole(5.4,38);}
module foot_assembly(center=false,open=false,yaw=rear_yaw){
 if(!open)translate([0,2*explode,65+explode])foot(center);
 foot_arch(center);color("#778ba0")translate([0,0,16])drive_cassette();
 for(y=[-37,37]){translate([0,y,31.5])tt();for(x=[-29,29])translate([x,y,31.5])wheel();}
 if(center){color("#202937")translate([-39.85,-70,66.6])cube([19.7,40.7,42.9]);
 // Link ends have orthogonal studs: X at guide arm, Z at servo horn.
 a=yaw;x=30-30*cos(a);y=60+30*sin(a);d=sqrt(x*x+y*y);
 horn=atan2(y,x)+acos((d*d+144-3744)/(24*d));
 c=[-30+12*cos(horn),-60+12*sin(horn),113];q=[-30*cos(a),30*sin(a),113];
 color(SILVER){pipe_segment([-30,-60,108.5],[c[0],c[1],108.5],1);pipe_segment([c[0],c[1],109.5],c,1.5);pipe_segment(c,q,1.5);}
 //14mm spheres enclose the tilted13x4.5mm housings;7.2mm shanks include flats.
 u=(q-c)/sqrt(3744);
 color("#383c41"){translate(c)sphere(d=14);translate(q)sphere(d=14);
 pipe_segment(c+u*5,c+u*18.5,3.6);pipe_segment(q-u*5,q-u*18.5,3.6);}
 }
}
module head_assembly(show_dome=true){
 color("#63768a")translate([0,0,415])bearing_tower();color(SILVER)translate([0,0,441])bearing_cap();
 color("#63768a")translate([0,0,407.5])head_motor_mount();translate([49,0,426.32])tt();translate([76.5,0,426.32])wheel();
 for(z=[415,434])color("#b9c3cc")translate([0,0,z])ring(11,4,7);
 color(SILVER){translate([0,0,413.5])cylinder(d=8,h=60);translate([0,0,409.1])cylinder(d=13.5,h=4.4);}
 translate([0,0,DOME_Z+2*explode])rotate([0,0,head_angle])
 if(show_dome)dome();else intersection(){dome();translate([0,0,-16])cylinder(r=90,h=26);}
}
module assembly(open=false){
 for(s=[-1,1])translate([s*165,0,0])scale([s,1,1]){
 foot_assembly(false,open);translate([0,0,HIP_Z]){side_spine();if(!open)leg();}}
 translate([0,rear_y(stroke),0])rotate([0,0,rear_yaw])foot_assembly(true,open);
 body_pose(stroke){metal_chassis();rear_guide(stroke);if(!open)electronics_panels();
 color("#1e2a37")translate([-56,-13,180])cube([112,66,71]);
 if(!open){translate([0,0,BODY_Z])body_lower();translate([0,0,BODY_Z+explode])body_upper();head_assembly();}
 else {color("#63768a")translate([0,0,415])bearing_tower();translate([49,0,426.32])tt();translate([76.5,0,426.32])wheel();}
 }}
if(part=="assembly")assembly();
else if(part=="section")assembly(true);
else if(part=="exploded")assembly();
else if(part=="body_lower")translate([0,0,35])body_lower();
else if(part=="body_upper")translate([0,0,-SPLIT])body_upper();
else if(part=="dome")translate([0,0,15])dome();
else if(part=="leg")translate([0,0,20])rotate([0,-90,45])leg();
else if(part=="outer_foot")translate([0,0,60])foot();
else if(part=="rear_foot")translate([0,0,60])foot(true);
else if(part=="drive_cassette")drive_cassette();
else if(part=="head_motor_mount")head_motor_mount();
else if(part=="bearing_tower")bearing_tower();
else if(part=="bearing_cap")bearing_cap();
else if(part=="head_mechanism")head_assembly(false);
else if(part=="foot_mechanism")foot_assembly(false,true);
else if(part=="metal_carrier")carrier_profile();
else if(part=="metal_chassis")chassis_profile();
else if(part=="metal_spine")spine_profile();
else if(part=="metal_base")base_profile();
else if(part=="metal_headfloor")headfloor_profile();
else if(part=="panel_front")electronics_profile();
else if(part=="panel_rear")electronics_profile(true);
else if(part=="metal_yoke")yoke_profile();
else if(part=="metal_limit_rail")limit_rail_profile();
else if(part=="metal_ankle")ankle_profile();
else if(part=="metal_fork")fork_profile();
else if(part=="metal_sole")projection(cut=true)translate([0,0,-14])foot_arch();
else if(part=="metal_bridge")projection(cut=true)translate([0,0,-73])foot_arch();
else assert(false,part);
