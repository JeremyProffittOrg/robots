// Revision D exterior relief, mm. Reference: docs/appearance-research.md.
$fn=96;
R=129.625; H=280; SPLIT=104.7; WALL=1.2;
LIP=12.12; RISE=140.02; BODY_Z=165; DOME_Z=456.8;
WHITE="#e6e8e9"; BLUE="#123b80"; SILVER="#aeb7bf"; DARK="#111820";
module ring(ro,ri,h){difference(){cylinder(r=ro,h=h);translate([0,0,-.05])cylinder(r=ri,h=h+.1);}}
module rounded(w,h,r=2){hull()for(x=[-w/2+r,w/2-r])for(y=[r,h-r])translate([x,y])circle(r=r,$fn=24);}
module panel_shape(theta,z,depth=.6){
 rotate([0,0,theta-90])translate([0,0,z])intersection(){
  ring(R+depth,R-.7,H+20);
  translate([0,R+25,0])rotate([90,0,0])linear_extrude(60)children();
 }
}
module panel(theta,z,w,h,depth=.5,r=1){panel_shape(theta,z,depth)rounded(w,h,r);}
module outline(theta,z,w,h,depth=.7,border=1){panel_shape(theta,z,depth)difference(){rounded(w,h,2);translate([0,border])rounded(w-2*border,h-2*border,1);}}
module radial(theta,z,rad=R){rotate([0,0,theta])translate([rad,0,z])rotate([0,90,0])children();}
module screw_heads(theta,z,w,h){for(x=[-w/2+3,w/2-3])for(y=[3,h-3])panel_shape(theta,z,.95)translate([x,y])circle(d=1.8,$fn=12);}
module octagon_port(theta,z){
 radial(theta,z,R-2){color(SILVER)difference(){cylinder(d=35,h=4,$fn=8);translate([0,0,1])cylinder(d=29,h=5,$fn=8);}
 color(DARK)cylinder(d=29,h=2.8,$fn=8);
 color(SILVER){translate([0,0,2.5])ring(12,10.8,1.8);translate([0,0,2.5])ring(8,5.5,2.7);
 for(a=[22.5:45:337.5])rotate([0,0,a])translate([11,-.8,2.5])cube([4,1.6,2.3]);}
 color(DARK)translate([0,0,2.5])cylinder(d=10,h=1.5);}
}
module coin_return(theta,z){
 color(SILVER)outline(theta,z,27,34,1.4,1.8);
 color(DARK)panel(theta,z+2,22,29,.9);
 // Recessed chute mouth with projecting lower lip, closed to the body skin.
 panel_shape(theta,z+3,3.7)polygon([[-10,0],[10,0],[10,2],[5,10],[-5,10],[-10,2]]);
 color(SILVER)panel(theta,z+3,21,2,4.1,.3);
 for(s=[-1,1])color(SILVER)panel_shape(theta,z+5,2.7)translate([s*8.5,0])square([1.3,19]);
}
module body_panel_channels(){
 // Engrave closed-door perimeters into the cosmetic skin; remaining wall >=0.75mm.
 intersection(){ring(R+.1,R-.45,H);union(){
 for(a=[42,138,195,345])panel_shape(a,103,.1)difference(){rounded(29,153,2);translate([0,.65])rounded(27.7,151.7,1.35);}
 for(a=[238,270,302])panel_shape(a,107,.1)difference(){rounded(37,92,2);translate([0,.65])rounded(35.7,90.7,1.35);}
 }}
}
module power_coupler(theta,z){
 color(BLUE)panel(theta,z-22,49,44,.8);
 radial(theta,z,R-1){color(SILVER){ring(20,17,4);cylinder(d=10,h=4);for(a=[0:60:300])rotate([0,0,a])translate([4,-1.5,1])cube([14,3,3]);}
 color(DARK)cylinder(d=33,h=2.2);color(SILVER)translate([0,0,4])ring(5,3.2,1);}
}
module body_details(){
 // Front large data port and two differently shaped utility arms.
 color(DARK)panel(90,264,140,10,.4);color(SILVER)outline(90,263,143,12,1.2);
 for(z=[234,207]){
  color(SILVER)outline(90,z-4,147,24,.6);
  color(DARK)panel(90,z,140,14,.4);
 }
 color(BLUE)panel_shape(90,234,1.5)polygon([[-68,3],[-56,1],[-36,4],[-18,4],[-18,1],[40,1],[54,4],[68,4],[68,11],[54,11],[40,14],[-18,14],[-18,11],[-36,11],[-56,14],[-68,12]]);
 color(BLUE)panel_shape(90,207,1.5)polygon([[-68,3],[-58,3],[-43,0],[14,0],[14,3],[34,3],[53,0],[68,3],[68,11],[53,14],[34,11],[14,11],[14,14],[-43,14],[-58,11],[-68,11]]);
 // Tall flanking doors, central vent frame and actual raised louvers.
 for(a=[42,138]){color(SILVER)outline(a,101,32,157,.6);color(SILVER)outline(a,106,25,146,.5);}
 color(BLUE)panel(90,111,52,90,.7);
 for(z=[114,159]){
  color(DARK)panel(90,z,39,39,1.0,12);
  color(SILVER)panel_shape(90,z,1.8)difference(){rounded(43,40,12);translate([0,1.8])rounded(39.4,36.4,10);}
  for(v=[9,18,27])color(SILVER)panel(90,z+v,35,2.0,2.3,.4);
 }
 color(SILVER){outline(113,171,39,29,.7);outline(116,109,15,54,.7);outline(62,109,42,91,.7);}
 for(i=[0:5]){color(SILVER)panel(122,112+i*8,15,5,.9);color(DARK)panel(122,113+i*8,11,2.1,1.1,.2);}
 radial(61,167,R-2){color(SILVER){cylinder(d=23,h=4);translate([0,0,4])ring(9,6.5,4);}color(DARK)translate([0,0,4])cylinder(d=12,h=1);}
 // Horizontal lower panel strip wraps round front and sides.
 for(a=[20:25:170])color(SILVER)outline(a,80,41,16,.6);
 for(a=[45,135,225,315])octagon_port(a,38);
 power_coupler(90,34);power_coupler(270,34);
 for(a=[61,119,242,298]){color(SILVER)outline(a,13,24,45,.6);}
 for(a=[153,207]){
  color(DARK)panel(a,13,34,43,.4);color(SILVER)outline(a,12,37,45,.9);
  for(x=[-12,-6,0,6,12])color(SILVER)panel_shape(a,15,1.4)translate([x,0])square([1.6,37]);
 }
 for(a=[113,247,292])coin_return(a,16);
 // Rear is not a copy of the front: broad upper hatch and three long doors.
 color(SILVER){outline(270,210,143,54,.7);outline(270,215,133,43,.6);}
 for(a=[238,270,302]){
  color(SILVER){outline(a,105,40,96,.6);outline(a,110,33,85,.5);outline(a,80,40,16,.6);}
 }
 for(a=[195,345])color(SILVER){outline(a,103,31,157,.6);outline(a,108,24,146,.5);}
 for(a=[10,170,190,350])color(SILVER)outline(a,22,18,42,.6);
 // Small data-port fingers, door hinge leaves and discrete recessed latch faces.
 for(x=[-60:6:60])color(SILVER)panel_shape(90,266,1.1)translate([x,0])square([1.2,5]);
 for(a=[42,138,195,345]){
  for(z=[123,223]){color(SILVER)panel(a-6,z,4,11,1.5,.5);screw_heads(a-6,z,4,11);}
  color(DARK)panel(a,112,5,9,.7,.8);color(SILVER)panel(a,114,1.5,5,1.3,.2);
 }
}
module skirt(){
 color(SILVER)difference(){cylinder(r1=100,r2=R,h=35.2);translate([0,0,-.1])cylinder(r1=98.7,r2=R-1.2,h=35.4);}
 for(a=[0:22.5:337.5])color(SILVER)rotate([0,0,a])rotate_extrude(angle=1.4)polygon([[99,0],[102,0],[R-.1,35.2],[R-1,35.2]]);
}
module body_whole(){
 color(WHITE)difference(){ring(R,R-WALL,H);mirror([1,0,0])body_panel_channels();}
 color(WHITE)ring(R,R-8,3);color(WHITE)translate([0,0,H-3])ring(R,R-8,3);
 translate([0,0,-35])skirt();mirror([1,0,0])body_details();
}
module exterior_body_lower(){intersection(){body_whole();translate([-180,-180,-40])cube([360,360,SPLIT+40]);}}
module exterior_body_upper(){intersection(){body_whole();translate([-180,-180,SPLIT])cube([360,360,H-SPLIT+1]);}
 color(SILVER)translate([0,0,H])ring(R,R-5,DOME_Z-BODY_Z-H-2.5);
}
function dr(z)=R*sqrt(max(0,1-pow(z/RISE,2)));
module ellipse(ro=R,rise=RISE){translate([0,0,LIP])scale([1,1,rise/ro])sphere(r=ro,$fn=128);}
module dome_band(extra=.8){difference(){ellipse(R+extra,RISE+extra);ellipse(R-.4,RISE-.4);translate([-160,-160,-160])cube([320,320,160+LIP]);}}
function dpi(l,j,i,n,m)=l*(n+1)*(m+1)+j*(n+1)+i;
module dome_panel(theta,span,z,h,depth=.7){
 // Direct closed surface patch avoids hundreds of repeated sphere Boolean cuts.
 n=max(1,ceil(span/2));m=max(1,ceil(h/4));
 pts=[for(l=[0,1])for(j=[0:m])for(i=[0:n])let(e=l==0?depth:-.8,zz=z+h*j/m,a=theta-span/2+span*i/n,rr=(R+e)*sqrt(max(0,1-pow(zz/(RISE+e),2))))[rr*cos(a),rr*sin(a),LIP+zz]];
 quads=concat(
 [for(l=[0,1])for(j=[0:m-1])for(i=[0:n-1])let(a=dpi(l,j,i,n,m),b=dpi(l,j,i+1,n,m),c=dpi(l,j+1,i+1,n,m),d=dpi(l,j+1,i,n,m))l==0?[a,b,c,d]:[a,d,c,b]],
 [for(j=[0,m])for(i=[0:n-1])let(a=dpi(0,j,i,n,m),b=dpi(0,j,i+1,n,m),c=dpi(1,j,i+1,n,m),d=dpi(1,j,i,n,m))j==0?[a,d,c,b]:[a,b,c,d]],
 [for(i=[0,n])for(j=[0:m-1])let(a=dpi(0,j,i,n,m),b=dpi(0,j+1,i,n,m),c=dpi(1,j+1,i,n,m),d=dpi(1,j,i,n,m))i==0?[a,b,c,d]:[a,d,c,b]]);
 polyhedron(points=pts,faces=[for(q=quads)each [[q[0],q[1],q[2]],[q[0],q[2],q[3]]]],convexity=4);
}
module dome_radial(theta,z){rotate([0,0,theta])translate([dr(z)-2,0,LIP+z])rotate([0,90-atan(z*R*R/(RISE*RISE*max(dr(z),1))),0])children();}
module holo(){
 color(SILVER){difference(){cylinder(d1=38,d2=31,h=16);translate([0,0,3])cylinder(d=24,h=18);}
  translate([0,0,14])ring(17,12,3);
  for(a=[0:15:345])rotate([0,0,a])translate([15,0,7])cylinder(d=1.5,h=9,$fn=8);
  for(a=[45:90:315])rotate([0,0,a])translate([16,0,0])cylinder(d=2.2,h=2,$fn=12);}
 color(DARK)translate([0,0,3])cylinder(d=24,h=1);
 color(SILVER){translate([0,0,3.8])ring(10,8,2.4);translate([0,0,5.8])ring(8.3,6.8,1.7);
 for(a=[0:90:270])rotate([0,0,a])translate([9,-.65,3.8])cube([3.4,1.3,3]);}
 color(DARK)translate([0,0,3.8])cylinder(d=13,h=2.2);
}
module dome_details(){
 for(a=[30:60:330])color(BLUE)dome_panel(a,56,82,47,.65);
 color(BLUE)intersection(){dome_band(.7);translate([0,0,LIP+133])cylinder(r=50,h=12);}
 // Individually positioned equatorial blue panels, with silver gaps.
 for(a=[12,32,49,145,167,192,216,325,348])color(BLUE)dome_panel(a,12,4,33,.6);
 for(a=[76,102])color(BLUE)dome_panel(a,11,3,34,.6);
 color(BLUE)dome_panel(92,19,3,34,.6);
 color(BLUE)dome_panel(292,19,3,34,.6);
 color(BLUE)dome_panel(244,30,3,34,.6);
 // Front stacked logic displays and their small individual raised light cells.
 for(z=[8,25]){
  color(SILVER)dome_panel(121,15,z-1,15,1.5);
  color(DARK)dome_panel(121,13,z,12,1.9);
  for(a=[116:2:126])for(v=[2,5,8])color(a%4==0?"#8eb8d4":"#e4e8df")dome_panel(a,.6,z+v,1.2,2.2);
 }
 color(DARK)dome_panel(244,28,18,11,1.3);
 for(a=[232:2:256])for(z=[20,24,27])color(a%4==0?"#739b60":"#b6c6b9")dome_panel(a,.7,z,1.2,1.7);
 // PSI lenses are geometry, colored as display targets for painting.
 dome_radial(92,20){color(SILVER)ring(12,10.8,4);color("#b8c4e5")cylinder(d=21.5,h=4.5);}
 dome_radial(292,20){color(SILVER)ring(12,10.8,4);color("#d9b373")cylinder(d=21.5,h=4.5);}
 for(a=[288,296])dome_radial(a,55)color(BLUE)cylinder(d=7,h=2);
 dome_radial(62,23)holo();dome_radial(270,23)holo();dome_radial(218,111)holo();
 // Angular radar-eye housing, curved attachment depth and convex lens.
 color(BLUE)difference(){hull(){translate([-48,73,63])cube([68,12,55]);translate([-45,119,66])cube([61,5,49]);}
  translate([-14,132,91])rotate([90,0,0])cylinder(d=44,h=70);
  translate([-48,118,61])cube([68,10,3]);}
 color(DARK)translate([-14,115,91])sphere(r=22,$fn=96);
 color(SILVER)translate([-14,121.8,91])rotate([90,0,0])ring(23,21.8,1.1);
 // Radar housing shelf and the narrow shadow slot visible below the eye.
 color(BLUE)translate([-43,119,63])cube([59,7,2]);
 color(DARK)translate([-37,124,63.5])cube([47,2.3,.8]);
 color(SILVER)translate([0,0,1])ring(R+.1,R-1,4);
 color(BLUE)translate([0,0,LIP-3])ring(R+.15,R-.4,2.4);
}
module exterior_dome(){
 color(SILVER)difference(){union(){ellipse();cylinder(r=R,h=LIP+1);}
  ellipse(R-WALL,RISE-WALL);translate([0,0,-1])cylinder(r=R-WALL,h=LIP+1);
  translate([-160,-160,-160])cube([320,320,160]);}
 color(SILVER)ring(R,R-8,3);mirror([1,0,0])dome_details();
}
module side_plane(x=0){translate([x,0,0])multmatrix([[0,0,1,0],[1,0,0,0],[0,1,0,0],[0,0,0,1]])children();}
module leg_outline(){union(){circle(r=43);hull(){translate([0,-29])circle(r=36);translate([0,-220])circle(r=21);}hull(){translate([-17,-275])circle(r=18);translate([17,-275])circle(r=18);translate([0,-226])circle(r=22);}}}
module exterior_leg(){
 color(WHITE)side_plane(-20)difference(){linear_extrude(40)leg_outline();translate([0,0,-.1])linear_extrude(38.3)offset(delta=-1.8)leg_outline();}
 // Layered horseshoe shoulder; the visible hub is distinct from its rim.
 color(WHITE)side_plane(20)linear_extrude(3)difference(){circle(r=43);circle(r=32);translate([-24,-65])square([48,40]);}
 color(SILVER)side_plane(20)linear_extrude(5)difference(){circle(r=29);circle(r=22);}
 color(WHITE)side_plane(19.7)linear_extrude(4.3)circle(r=21);
 color(SILVER)side_plane(23.9)linear_extrude(1.3)circle(r=9);
 color(BLUE)side_plane(20)linear_extrude(3)translate([0,-224])rounded(30,138,2);
 color(BLUE)side_plane(22)linear_extrude(5)translate([0,-129])rounded(34,54,5);
 for(y=[-17,17])color(SILVER)translate([25,y,-220])cylinder(d=4,h=142,$fn=24);
 for(z=[-215,-82])color(SILVER)side_plane(20)linear_extrude(6)translate([0,z])rounded(39,7,1);
 color(WHITE)side_plane(20)linear_extrude(6)translate([0,-247])rounded(60,13,2);
 for(y=[-18,18])color(BLUE)side_plane(23)linear_extrude(2)translate([y,-263])rounded(9,16,1);
 color(SILVER)translate([24,-34,-274])rotate([-90,0,0])cylinder(d=14,h=68,$fn=40);
 for(y=[-31,31])color(SILVER)side_plane(20)linear_extrude(5)translate([y,-59])circle(d=7);
 for(y=[-23,23])for(z=[-242,-279])color(SILVER)side_plane(25)linear_extrude(2)translate([y,z])circle(d=3,$fn=12);
 // Horseshoe stepped rim, end blocks, booster caps and ankle wedge fittings.
 color(WHITE)side_plane(22.8)linear_extrude(1.4)difference(){circle(r=40.5);circle(r=37);translate([-24,-65])square([48,40]);}
 for(y=[-28,28])color(WHITE)side_plane(20)linear_extrude(5)translate([y-5,-47])rounded(10,18,1);
 for(z=[-125,-119,-113])color(SILVER)side_plane(27)linear_extrude(1.3)translate([0,z])rounded(27,2,.3);
 for(y=[-17,17])for(z=[-211,-89])color(SILVER)translate([25,y,z])cylinder(d=6.5,h=6,$fn=32);
 for(y=[-22,22])color(WHITE)side_plane(20)linear_extrude(8)translate([y,-276])polygon([[-5,0],[5,0],[4,22],[-3,15]]);
}
module pipe_segment(a,b,r=3){hull(){translate(a)sphere(r=r,$fn=12);translate(b)sphere(r=r,$fn=12);}}
module exterior_foot(center=false){
 // Wedge-shaped shell with inset toe strips and rounded power-cell housing.
 color(WHITE)difference(){
  hull(){translate([-54,-98,-60])cube([108,196,3]);translate([-54,-98,-16])cube([108,2,2]);translate([-49,-38,22])cube([98,2,2]);translate([-33,-12,34])cube([66,24,2]);translate([-49,36,26])cube([98,2,2]);}
  hull(){translate([-52.5,-96.5,-61])cube([105,193,3]);translate([-52.5,-96.5,-17.5])cube([105,1,1]);translate([-47.5,-37,20.5])cube([95,1,1]);translate([-31.5,-11,32.5])cube([63,22,1]);translate([-47.5,36,24.5])cube([95,1,1]);}
 }
 for(x=[-30,0,30])color(DARK)translate([x-10,97.5,-59])cube([20,1.1,1.4]);
 // Integral side-panel frames follow the sloping foot instead of a flat decal.
 for(s=[-1,1])scale([s,1,1]){
  color(SILVER)side_plane(52.8)linear_extrude(1.8)difference(){
   polygon([[-90,-52],[75,-52],[-35,-20],[-90,-20]]);
   polygon([[-87,-49],[54,-49],[-36,-23],[-87,-23]]);}
  for(y=[-83,-48])color(SILVER)translate([53,y,-45])rotate([0,90,0])difference(){cylinder(d=7,h=2.4,$fn=32);translate([0,0,1.7])cylinder(d=4.5,h=1);}
 }
 color(SILVER)translate([-4,13,34.8])rotate([-atan(7/24),0,0])cube([8,25,1.5]);
 color(SILVER)translate([-4,37,27.8])rotate([-atan(85/61),0,0])cube([8,sqrt(85*85+61*61),1.5]);
 if(!center){
  color(WHITE)difference(){hull(){translate([-62,-48,-5])rotate([90,0,0])cylinder(d=30,h=32);translate([-62,-48,55])rotate([90,0,0])cylinder(d=30,h=32);}
   hull(){translate([-62,-49.8,-5])rotate([90,0,0])cylinder(d=26.4,h=28.4);translate([-62,-49.8,55])rotate([90,0,0])cylinder(d=26.4,h=28.4);}
   translate([-72,-74,-25])cube([20,20,30]);}
  color(SILVER)translate([-62,-80,49])rotate([90,0,0])ring(14,12.7,1.8);
  // Battery-box face insert and distinct hose-end collars are part of the same print.
  color(SILVER)side_plane(-78)linear_extrude(2.8)translate([-70,-1])rounded(18,42,2);
  for(y=[-73,-56])for(z=[4,34])color(SILVER)translate([-77,y,z])xhole(2.8,1.5);
  for(p=[[-35,40,15],[-10,40,15]])color(SILVER)translate(p)difference(){sphere(r=5,$fn=24);translate([0,0,3])cube([12,12,8],center=true);}
  for(k=[0:11])let(t=k/11,t2=(k+1)/11){
   a=[-35+25*t,40+15*sin(180*t),15+25*sin(180*t)];b=[-35+25*t2,40+15*sin(180*t2),15+25*sin(180*t2)];
   color(SILVER)pipe_segment(a,b,3.3);color(DARK)translate(a)sphere(r=3.6,$fn=12);
  }
 }
}
