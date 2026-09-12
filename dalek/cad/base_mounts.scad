// MOUNT-1 base and service platform. Millimetres, base-local assembled coordinates.
// Imported by dalek.scad; uses its hole, ring, tongue, slot and wheel_wells helpers.
// Board deck: diameter216, undersideZ140, topZ146. Four rail seats atZ36.
module captive_base_nut_pocket(){
 translate([0,0,42.9])rotate([0,0,30])cylinder(d=7.4/cos(30),h=4.4,$fn=6);
}
module base(){union(){difference(){
 union(){
  cylinder(r=150,h=6);ring(150,146,54);
  translate([0,0,48])ring(150,132,6);tongue(150,54);
  intersection(){cylinder(r=146,h=30);union(){
   for(x=[-59,55])translate([x,-145,5])cube([4,290,21]);
   for(y=[-111,107])translate([-146,y,5])cube([292,4,21]);
  }}
  for(sx=[-1,1])for(sy=[-1,1])scale([sx,sy,1]){
   // Original motor cradles and axle positions are retained.
   translate([54.5,-1,5])cube([4,76,28]);
   translate([82.5,-1,5])cube([3,76,28]);
   for(y=[-3,73])translate([54.5,y,5])cube([31,4,17]);
   // Roof captures the inner clamp toe; one outer boss receives its screw.
   translate([54.5,3,28])cube([4,16,9.4]);
   translate([88.5,11,5])cylinder(d=12,h=24);
   // Platform foot rests on a widened, raised rail seat.
   // Stop before the motor case atX59.3 so the mated wheel/motor can lower in.
   translate([52.5,36,30])cube([6.5,24,6]);
  }
  // 104 by157 clear battery cradle, for a100 by153 maximum battery case.
  for(x=[-54.5,52])translate([x,-82.5,5])cube([2.5,165,13]);
  for(y=[-82.5,78.5])translate([-54.5,y,5])cube([109,4,13]);
  // Thick roofs carry the four retained M4 stack nuts.
  for(a=[0:90:270])rotate([0,0,a])translate([137,0,43])cylinder(d=16,h=11);
 }
 wheel_wells();
 for(sx=[-1,1])for(sy=[-1,1])scale([sx,sy,1]){
  translate([70.5,58,17.7])rotate([0,90,0])hole(15,42);
  // Clearance below clamp bridge, and captured sliding toe.
  translate([82.4,3,29])cube([3.2,16,8.6]);
  translate([54.3,3.7,29.6])cube([4.4,14.6,3.8]);
  translate([88.5,11,0])hole(M3,70);
  translate([88.5,11,22])rotate([0,0,30])cylinder(d=6.2/cos(30),h=2.8,$fn=6);
  translate([88.5,7.9,22])cube([7,6.2,2.8]);
  // Two longitudinal straps per motor avoid the narrow wheel-side clearance.
  // They rise beyond the two motor case ends, not beside the output axle.
  for(x=sy>0?[62,74]:[68,80])for(y=[-.2,72.2])translate([x,y,18])cube([6.2,3.4,40],center=true);
  // Rail feet: M3 screws with side-loaded nuts OR a tie through the same tunnel.
  for(y=[40,56]){
   translate([56.5,y,0])hole(M3,90);
   translate([56.5,y,31])rotate([0,0,30])cylinder(d=6.2/cos(30),h=2.7,$fn=6);
   translate([56.5,y-3.1,31])cube([6,6.2,2.7]);
   translate([52,y-3.1,30.4])cube([10,6.2,2.2]);
  }
 }
 // Battery straps rise in the side clearance, away from the four platform feet.
 for(x=[-51.5,51.5])for(y=[-25,25])translate([x,y,8])cube([3.2,6.2,20],center=true);
 // Preserve access through the central motor leads channel.
 for(x=[-83.5,56.5])translate([x,-8,6])cube([27,16,25]);
 for(z=[8,21,34])translate([0,0,z])ring(151,149.2,1.4);
 joint_holes(150,52);
 for(a=[0:90:270])rotate([0,0,a])translate([137,0,0])captive_base_nut_pocket();
 }
 // Flexible insertion nibs retain standard M4 nuts; the thick pocket roof takes load.
 for(a=[0:90:270])rotate([0,0,a])translate([137,0,43])
  for(x=[-3.55,3.55])translate([x-.3,-1.8,0])cube([.6,3.6,.6]);
}}

// Four identical clamps. Assembled translation [sx*70.5,sy*11,29].
// Rotate180degrees aboutZ on the left side. The toe points toward the battery.
module motor_clamp(){difference(){union(){
 translate([-11.5,-7,1])cube([31.5,14,4]);
 translate([-15.5,-7,1])cube([5,14,3]);
 translate([18,0,0])cylinder(d=12,h=5,$fn=48);
 }
 translate([18,0,2])hole(M3,14);
}}

module platform_assembled(){difference(){union(){
 translate([0,0,140])cylinder(d=216,h=6);
 // Rim and beams stiffen the deck while leaving terminal space in the centre.
 translate([0,0,132])ring(108,102,8);
 for(y=[-85,85])translate([-60.5,y-3,132])cube([121,6,9]);
 for(x=[-56.5,56.5])translate([x-3,-88,132])cube([6,176,9]);
 for(x=[-56.5,56.5])for(y=[-48,48]){
  translate([x-4,y-6,36])cube([8,12,105]);
  translate([x-4,y-14,36])cube([8,28,5]);
  // End keys engage the raised seat with0.4mm clearance; the long rail below
  // ends atZ33, so keys atZ34 do not cross the rail.
  for(dy=[-14,12.4])translate([x-4,y+dy,34])cube([8,1.6,3]);
  // Knee braces point away from the battery. Its complete100x153 footprint
  // remains clear up to the deck underside atZ140.
  hull(){translate([x-4,y-6,122])cube([8,12,2]);
         translate([x<0?x-20:x-4,y-14,138])cube([24,28,3]);}
 }
 }
 // Slots accept M2/M2.5 fasteners or insulated board ties. Actual PCB templates
 // determine which slots are used, or which additional holes are drilled.
 for(x=[-90:12:90])for(y=[-90:12:90])if(x*x+y*y<94*94)
  translate([x,y,143])slot(5,3.2,12);
 for(x=[-56.5,56.5])for(y=[-48,48])for(dy=[-8,8]){
  translate([x,y+dy,38])hole(M3,12);
  // Shallow transverse grooves stop an optional foot strap walking along the foot.
  translate([x-4.1,y+dy-3.1,40.2])cube([8.2,6.2,2]);
 }
}}

// Printed deck-down, legs-up as one connected part. No platform STL supports
// the weight of the battery: the battery always sits on the six-millimetre base.
// Assembly transform: rotate180degrees aboutX, then translate[0,0,146].
module electronics_platform(){translate([0,0,146])rotate([180,0,0])platform_assembled();}
