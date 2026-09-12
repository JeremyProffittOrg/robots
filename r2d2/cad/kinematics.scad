// Supported rear deployment. X shoulders; Y forward; Z up; millimetres.
HIP_Z=390;
ANKLE_Z=113;
GUIDE_ANGLE=35;
GUIDE_Y=-40;
GUIDE_Z=240;
POST_ZERO=150;
POST_MIN=(HIP_Z-ANKLE_Z-150)/cos(GUIDE_ANGLE)-POST_ZERO;
POST_MAX=72;
function post_a(s)=40+(POST_ZERO+s)*sin(GUIDE_ANGLE);
function post_b(s)=150+(POST_ZERO+s)*cos(GUIDE_ANGLE);
function body_pitch(s)=atan2(post_a(s),post_b(s))-acos((HIP_Z-ANKLE_Z)/sqrt(pow(post_a(s),2)+pow(post_b(s),2)));
function rear_y(s)=-sqrt(pow(post_a(s),2)+pow(post_b(s),2)-pow(HIP_Z-ANKLE_Z,2));
module body_pose(s){translate([0,0,HIP_Z])rotate([body_pitch(s),0,0])translate([0,0,-HIP_Z])children();}
module guide_frame(x=0){translate([x,GUIDE_Y,GUIDE_Z])multmatrix([[1,0,0,0],[0,cos(GUIDE_ANGLE),-sin(GUIDE_ANGLE),0],[0,-sin(GUIDE_ANGLE),-cos(GUIDE_ANGLE),0],[0,0,0,1]])children();}
