// Revision D front-deploying centre leg: stance kinematics and layout masses.
// The sensed shoulder lock constants live in stance-lock-sensed.scad (SL_ prefix).
// X shoulders, Y forward, Z up; millimetres and degrees.
// scripts/check_kinematics.py parses every "NAME=number;" line: keep design numbers literal.
HIP_Z=390;
ANKLE_Z=113;
SIDE_FOOT_X=165;
WHEEL_ROW_Y=37;
WHEEL_AXLE_X=29;
WHEEL_CONTACT_X=26;       // 29 mm nominal, 3 mm hub-seating allowance
WHEEL_AXLE_Z=31.5;
WHEEL_RADIUS=31.5;
// Printed post guide: body-fixed, inclined forward-down from vertical.
GUIDE_ANGLE=30;
GUIDE_Y=40;
GUIDE_Z=240;
GUIDE_LENGTH=150;
GUIDE_LAND_A=-130;        // sliding-land centres along the guide axis
GUIDE_LAND_B=-10;
GUIDE_LAND_LENGTH=20;
// Actuonix P16-100-256-12-P drives the post; endpoints stay inside the 100 mm stroke.
POST_ZERO=110;            // guide origin to rod-end centre at stroke 0
POST_STROKE=100;
POST_MIN=2;               // two-foot endpoint: post fully retracted, centre foot lifted
POST_MAX=98;              // three-foot endpoint: body leaning back on the centre foot
POST_RAIL=290;            // MISUMI HFS5-2020
POST_RAIL_END=62.5;       // rod-end centre to rail bottom
ACTUATOR_Y=40;            // actuator axis offset in front of the post, guide-local Y
ACTUATOR_FIXED_PIN=-70;
ACTUATOR_CLOSED=147;
ACTUATOR_ROD_EYE=-33;     // rod eye pin, guide-local Z relative to the rod-end centre
CENTER_YAW_LIMIT=8;
// Printed ankle stops, relative to flat: heel-down and toe-down limits of the hanging centre foot.
ANKLE_STOP_HEEL=1;
ANKLE_STOP_TOE=17.5;
// Layout masses used by the CG check.
BATTERY_X=60;             // Bioenno BLF-1206A standing 71 x 66 x 112 mm beside the post
BATTERY_Y=0;
BATTERY_Z=245;
ELECTRONICS_X=0;          // controller, regulators and wiring bay centroid, front upper chassis
ELECTRONICS_Y=45;
ELECTRONICS_Z=340;
POST_CONTACT=(GUIDE_Z-ANKLE_Z)/cos(GUIDE_ANGLE)-POST_ZERO;
function post_a(s)=GUIDE_Y+(POST_ZERO+s)*sin(GUIDE_ANGLE);
function post_b(s)=HIP_Z-GUIDE_Z+(POST_ZERO+s)*cos(GUIDE_ANGLE);
function body_pitch(s)=s<=POST_CONTACT?0:acos((HIP_Z-ANKLE_Z)/sqrt(pow(post_a(s),2)+pow(post_b(s),2)))-atan2(post_a(s),post_b(s));
function center_y(s)=post_a(s)*cos(body_pitch(s))+post_b(s)*sin(body_pitch(s));
function center_lift(s)=max(0,HIP_Z-ANKLE_Z+post_a(s)*sin(body_pitch(s))-post_b(s)*cos(body_pitch(s)));
// The heel-heavy centre foot hangs on its heel stop once lifted.
function foot_pitch(s)=center_lift(s)>0.001?ANKLE_STOP_HEEL:0;
module body_pose(s){translate([0,0,HIP_Z])rotate([body_pitch(s),0,0])translate([0,0,-HIP_Z])children();}
module guide_frame(x=0){translate([x,GUIDE_Y,GUIDE_Z])multmatrix([[1,0,0,0],[0,cos(GUIDE_ANGLE),sin(GUIDE_ANGLE),0],[0,sin(GUIDE_ANGLE),-cos(GUIDE_ANGLE),0],[0,0,0,1]])children();}
