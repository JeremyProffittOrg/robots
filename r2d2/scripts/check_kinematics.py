"""Check the supported three-foot rear-post model and conservative load cases.
Screening calculations, not a material certificate or physical strength test.
"""
from pathlib import Path
import json,math
import numpy as np
from scipy.spatial import ConvexHull
ROOT=Path(__file__).resolve().parents[1]
ALPHA=math.radians(35);HIP=390.;ANKLE=113.;ZERO=150.
MIN=(HIP-ANKLE-150)/math.cos(ALPHA)-ZERO;MAX=72.;MASS=6.;G=9.81
def pose(s):
 L=ZERO+s;A=40+L*math.sin(ALPHA);B=150+L*math.cos(ALPHA);D=HIP-ANKLE
 angle=math.atan2(A,B)-math.acos(D/math.hypot(A,B))
 return angle,-math.sqrt(A*A+B*B-D*D),HIP-A*math.sin(angle)-B*math.cos(angle)
def main():
 rows=[];min_margin=1e9;max_force=0;max_side=0
 for s in np.linspace(MIN,MAX,101):
  theta,ry,rz=pose(s);assert abs(rz-ANKLE)<1e-8
  overlap=min(50,ZERO+s-62.5)-max(-150,ZERO+s-62.5-270)
  assert overlap>=100
  A=40+(ZERO+s)*math.sin(ALPHA);B=150+(ZERO+s)*math.cos(ALPHA)
  deriv=-math.cos(ALPHA-theta)/abs(ry)
  foot_deriv=-(A*math.sin(ALPHA)+B*math.cos(ALPHA))/abs(ry)
  for yaw in [-8,0,8]:
   a=math.radians(yaw);points=[]
   for side in [-165,165]:
    for x in [-26,26]:
     for y in [-37,37]:points.append([side+x,y])
   for x in [-26,26]:
    for y in [-37,37]:points.append([x*math.cos(a)-y*math.sin(a),ry+x*math.sin(a)+y*math.cos(a)])
   hull=ConvexHull(np.array(points))
   for x in [-35,35]:
    for y in [-60,20]:
     for z in [-170,-80]:
      cy=y*math.cos(theta)-z*math.sin(theta)
      signed=hull.equations[:,:2]@np.array([x,cy])+hull.equations[:,2]
      margin=-float(signed.max());assert margin>=10;min_margin=min(min_margin,margin)
      gravity=MASS*G*abs((y*math.cos(theta)-z*math.sin(theta))*deriv)
      # 10N is a commissioning ceiling for measured rear-foot rolling drag.
      force=(gravity+10*abs(foot_deriv))*3*1.25
      max_force=max(max_force,force);assert force<300
  rows.append({'stroke_mm':round(float(s),3),'body_pitch_deg':round(math.degrees(theta),3),'rear_foot_y_mm':round(ry,3),'rear_pivot_z_mm':round(rz,3),'guide_overlap_mm':round(overlap,3)})
 F=MASS*G*3;shaft_d=12;moment=F*.030;torque=F*.060
 bend=32*moment/(math.pi*(shaft_d/1000)**3)/1e6
 shear=16*torque/(math.pi*(shaft_d/1000)**3)/1e6
 shaft_vm=math.sqrt(bend*bend+3*shear*shear)
 outer=19.05;inner=12.7;area=outer**2-inner**2;I=(outer**4-inner**4)/12
 guide_stress=300/area+(F*100+300*38)*(outer/2)/I
 assert shaft_vm<100 and guide_stress<80
 result={'configuration':'rear deployment, all three feet down; side ankle joints rigid; shoulders pivot',
 'assumed_max_mass_kg':MASS,'dynamic_factor':3,'additional_alignment_friction_factor':1.25,
 'post_min_mm':MIN,'post_max_mm':MAX,'max_calculated_actuator_force_N':max_force,
 'actuator_dynamic_rating_N':300,'actuator_static_rating_N':500,
 'min_support_margin_mm':min_margin,'shaft_nominal_von_mises_MPa':shaft_vm,
 'guide_nominal_combined_stress_MPa':guide_stress,'rows':rows,'physical_tested':False}
 (ROOT/'cad/kinematic-check.json').write_text(json.dumps(result,indent=2))
 print(f'PASS: 101 post positions; rear pivot stays at113mm; support margin>={min_margin:.1f}mm')
 print(f'Calculated actuator demand {max_force:.1f}N <300N; nominal shaft {shaft_vm:.1f}MPa; guide {guide_stress:.1f}MPa')
 print('Physical CG, rolling drag, strength and motion tests remain required.')
if __name__=='__main__':main()
