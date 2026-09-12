"""Check the supported three-foot rear-post model and conservative load cases.
Screening calculations, not a material certificate or physical strength test.
"""
from pathlib import Path
import json,math,csv,re,xml.etree.ElementTree as ET
import numpy as np
from scipy.spatial import ConvexHull
ROOT=Path(__file__).resolve().parents[1]
ALPHA=math.radians(35);HIP=390.;ANKLE=113.;ZERO=150.
MIN=(HIP-ANKLE-150)/math.cos(ALPHA)-ZERO;MAX=72.;MASS=9.;G=9.81
def pose(s):
 L=ZERO+s;A=40+L*math.sin(ALPHA);B=150+L*math.cos(ALPHA);D=HIP-ANKLE
 angle=math.atan2(A,B)-math.acos(D/math.hypot(A,B))
 return angle,-math.sqrt(A*A+B*B-D*D),HIP-A*math.sin(angle)-B*math.cos(angle)

def mass_budget():
 rows=[]
 def add(name,grams,basis):rows.append({'component':name,'estimated_g':round(grams,1),'basis':basis})
 profiles=json.loads((ROOT/'cad/metal/manifest.json').read_text())
 for name,r in profiles.items():
  area=0
  for e in ET.parse(ROOT/'cad/metal'/f'{name}.svg').getroot().iter():
   if e.tag.rsplit('}',1)[-1]!='path':continue
   d=e.attrib['d'];assert not re.sub(r'[MLmz\s,0-9.eE+\-]','',d),'Unexpected SVG path command'
   for poly in re.split('[Mm]',d)[1:]:
    v=[float(n) for n in re.findall(r'[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?',poly)];assert len(v)%2==0
    p=list(zip(v[::2],v[1::2]));area+=sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(p,p[1:]+p[:1]))/2
  density={'6061-T6':2.7,'steel':7.85,'G10 insulating sheet':1.85}[r['material']]
  add(name,abs(area)*r['thickness_mm']*r['quantity']*density/1000,'Current cut-profile area x stock thickness x assumed density; all installed copies')
 sliced=json.loads((ROOT/'cad/h2d-structure-check.json').read_text())
 assert len(sliced['rows'])==10
 add('All installed prints',sum(r['installed_model_g']*r['quantity'] for r in sliced['rows']),'G-code labelled model extrusion; excludes supports/brim; not measured mass')
 for name,grams in [
  ('Outer and inner guide tubes',343),('Two guide crossbars',308),('Moving adapter',162),('Eight corner blocks',104),
  ('Six steel foot stanchions',83),('Rear servo platform and step',52),('Fixed actuator clevis',15),('Three moving yoke ears',32),
  ('Limit-rail clamp block',4),('Two shoulder shafts',160),('Two aluminum split hubs',76),('Four aluminum bearing housings',178),
  ('Four6001 bearings',128),('Two608 bearings',36),('Four steel shaft collars',68),('Aluminum carrier spacers',76),
  ('Four electronics support rods',82),('SKFSA12E',78),('P16 actuator allowance',150),('Acetal guide pads',13),
  ('Fasteners horn links shims and nylon standoffs',600),('Battery BLF-1206A',700),('Thirteen3766 wheels',13*38),
  ('Seven3777 motors',7*30.6),('MG-995 servo',62.41),('Electronics fuse holders connectors and installed wiring',600),('Paint foam straps and ties',100)]:
  add(name,grams,'Component envelope/stock estimate or stated allowance; weigh actual installed parts')
 with (ROOT/'bom/mass-budget.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
 total=sum(r['estimated_g'] for r in rows)
 report={'estimated_total_g':round(total,1),'design_limit_g':MASS*1000,'estimated_reserve_g':round(MASS*1000-total,1),
         'physical_mass_measured':False,'initial_6kg_assumption_met':False,'method':'Current cut areas and model extrusion plus named stock/component allowances; no payload budget'}
 (ROOT/'cad/mass-budget.json').write_text(json.dumps(report,indent=2))
 print(f'Estimated assembled mass {total/1000:.3f}kg; design limit {MASS:g}kg; actual weighing required')
def main():
 rows=[];min_margin=1e9;max_force=0;max_side=0
 maximum_link_skew=0
 for yaw in np.linspace(-8,8,65):
  a=math.radians(yaw);x=30-30*math.cos(a);y=60+30*math.sin(a);d=math.hypot(x,y)
  horn=math.atan2(y,x)+math.acos((d*d+144-3744)/(24*d))
  cx=-30+12*math.cos(horn);cy=-60+12*math.sin(horn)
  wx=cx*math.cos(a)-cy*math.sin(a);wy=cx*math.sin(a)+cy*math.cos(a)
  assert abs(math.hypot(wx+30,wy)-math.sqrt(3744))<1e-8
  skew=math.degrees(math.asin(abs(wx+30)/math.sqrt(3744)));maximum_link_skew=max(maximum_link_skew,skew)
 assert maximum_link_skew<30
 for s in np.linspace(MIN,MAX,101):
  theta,ry,rz=pose(s);assert abs(rz-ANKLE)<1e-8
  overlap=min(50,ZERO+s-62.5)-max(-150,ZERO+s-62.5-270)
  assert overlap>=100
  inner_lo=ZERO+s-332.5;inner_hi=ZERO+s-62.5
  for pad in [-90,30]:assert inner_lo<=pad-10 and inner_hi>=pad+10
  A=40+(ZERO+s)*math.sin(ALPHA);B=150+(ZERO+s)*math.cos(ALPHA)
  deriv=-math.cos(ALPHA-theta)/abs(ry)
  foot_deriv=-(A*math.sin(ALPHA)+B*math.cos(ALPHA))/abs(ry)
  for yaw in [-8,0,8]:
   a=math.radians(yaw);points=[]
   for side in [-165,165]:
    for x in [-26,26]: # nominal29mm, reduced3mm for hub-seating tolerance
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
 guide_stress=300/area+(F*(ZERO+MAX-30)+300*38)*(outer/2)/I
 assert shaft_vm<100 and guide_stress<80
 result={'configuration':'rear deployment, all three feet down; side ankle joints rigid; shoulders pivot',
 'assumed_max_mass_kg':MASS,'dynamic_factor':3,'additional_alignment_friction_factor':1.25,
 'post_min_mm':MIN,'post_max_mm':MAX,'max_calculated_actuator_force_N':max_force,
 'actuator_dynamic_rating_N':300,'actuator_static_rating_N':500,
 'min_support_margin_mm':min_margin,'pad_centers_mm':[-90,30],'pad_length_mm':20,
 'all_pads_fully_engaged':True,'max_steering_link_skew_deg':maximum_link_skew,'steering_rod_end_limit_deg':30,
 'wheel_half_track_checked_mm':26,'wheel_half_track_nominal_mm':29,
 'shaft_nominal_von_mises_MPa':shaft_vm,
 'guide_nominal_combined_stress_MPa':guide_stress,'rows':rows,'physical_tested':False}
 (ROOT/'cad/kinematic-check.json').write_text(json.dumps(result,indent=2))
 print(f'PASS: 101 post positions; rear pivot stays at113mm; support margin>={min_margin:.1f}mm')
 print(f'Calculated actuator demand {max_force:.1f}N <300N; nominal shaft {shaft_vm:.1f}MPa; guide {guide_stress:.1f}MPa')
 print('Physical CG, rolling drag, strength and motion tests remain required.')
 if (ROOT/'cad/metal/manifest.json').exists():mass_budget()
if __name__=='__main__':main()
