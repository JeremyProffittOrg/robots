"""MATLAB-style engineering PNGs from the current Revision B STL meshes.
No CAD/firmware changes. Purchased parts are explicitly schematic envelopes.
"""
from pathlib import Path
import hashlib,json,zipfile
import numpy as np
import trimesh
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.patches import Patch
from matplotlib.colors import to_rgba
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/drawings'
BLUE='#0072BD';ORANGE='#D95319';GOLD='#EDB120';GRAY='#AAB7C4';INK='#23384D'
plt.rcParams.update({'font.family':'Arial','font.size':10,'axes.titlesize':13,
 'axes.labelsize':10,'axes.edgecolor':'#63788C','axes.linewidth':.7,
 'grid.color':'#CED7E0','grid.alpha':.65,'grid.linewidth':.5,
 'figure.facecolor':'white','axes.facecolor':'white','savefig.facecolor':'white','figure.dpi':170})
DATA=json.loads((ROOT/'cad/validation.json').read_text())
ROWS={r['part']:r for r in DATA['rows']}
MESH={n:trimesh.load_mesh(ROOT/'stl'/f'{n}.stl') for n in ROWS}
ARTIFACTS=[]

def transformed(mesh,xyz=(0,0,0),rx=0,ry=0,rz=0):
 m=mesh.copy()
 for angle,axis in [(rx,[1,0,0]),(ry,[0,1,0]),(rz,[0,0,1])]:
  if angle:m.apply_transform(trimesh.transformations.rotation_matrix(np.deg2rad(angle),axis))
 m.apply_translation(xyz);return m

def item(name,xyz=(0,0,0),color=GRAY,**rot):return (transformed(MESH[name],xyz,**rot),color,name)
def box(size,xyz,color,name):
 m=trimesh.creation.box(size);m.apply_translation(np.asarray(xyz)+np.asarray(size)/2);return m,color,name
def wheel(xyz):return transformed(trimesh.creation.cylinder(radius=31.5,height=29,sections=48),xyz,ry=90),ORANGE,'Wheel envelope'
def bearing(xyz):return transformed(trimesh.creation.annulus(r_min=4,r_max=11,height=7,sections=40),(xyz[0],xyz[1],xyz[2]+3.5)),GOLD,'608 bearing'

def foot(center=(0,0,0),exploded=False,cover=False):
 x,y,z=center;parts=[]
 parts.append(item('foot_deck',(x,y,z+65+(45 if exploded else 0)),GRAY))
 if cover:parts.append(item('foot_cover',(x,y,z+70+(85 if exploded else 0)),'#D9E4ED'))
 for dy in [-45,45]:
  parts.append(item('motor_cradle',(x,y+dy,z+16),BLUE))
  parts.append(box((18.6,70,22.44),(x-9.3,y+dy-57,z+20.3+(30 if exploded else 0)),GOLD,'3777 motor envelope'))
  for dx in [-1,1]:parts.append(wheel((x+dx*(75 if exploded else 33),y+dy,z+31.5)))
 return parts

def head(base=0,exploded=False):
 gap=14 if exploded else 0
 parts=[item('bearing_tower',(0,0,424+base),BLUE),bearing((0,0,424+base)),bearing((0,0,443+base)),
  item('bearing_cap',(0,0,450+base+gap),GRAY),item('gear_hub',(0,0,451+base+gap*2),BLUE),
  item('head_plate',(0,0,470+base+gap*3),GRAY),item('servo_mount',(45,0,416+base),BLUE),
  box((20,40,37),(35,-30,419+base),INK,'Servo envelope'),
  item('servo_pinion',(45,0,461+base+gap*2),GOLD,rz=9)]
 for a in [0,90,180,270]:
  parts.append(item('dome_spacer',(119*np.cos(np.deg2rad(a)),119*np.sin(np.deg2rad(a)),473+base+gap*3),GRAY))
 parts.append(item('dome',(0,0,479.6+base+gap*4),'#BCCCDC'))
 parts.append(item('eye',(0,114,535+base+gap*4),BLUE,rx=-65))
 return parts

def robot(exploded=False):
 parts=[];dx=100 if exploded else 0;upper_gap=95 if exploded else 0
 for sign,name in [(-1,'arm_left'),(1,'arm_right')]:
  x=sign*(190+dx);parts+=foot((x,0,0),cover=True)
  parts.append(item(name,(x,0,70+(35 if exploded else 0)),'#CAD9E8'))
  parts.append(box((40,2,150),(x-20,30,120+(35 if exploded else 0)),BLUE,'Painted stripe'))
 parts+=foot((0,-180-(80 if exploded else 0),0))
 parts += [item('rear_bracket',(0,-180-(80 if exploded else 0),110),BLUE),item('rear_attach',(0,0,165),GRAY),
  item('body_lower',(0,0,170),'#D5E1EB'),item('body_upper',(0,0,315+upper_gap),'#C3D6E7'),
  box((112,66,71),(-56,-33,181),INK,'Battery envelope'),item('utility_deck',(0,0,329+upper_gap),GRAY)]
 for z in [240,290,350,397]:parts.append(item('detail_panel',(-36,130,z+(upper_gap if z>=320 else 0)),BLUE,rx=90))
 parts+=head(upper_gap+(65 if exploded else 0))
 # Rear steering positions match the CAD assembly.
 ry=-180-(80 if exploded else 0)
 parts += [item('bearing_tower',(0,ry,114),BLUE),item('bearing_cap',(0,ry,140),GRAY),
  item('spindle_sleeve',(0,ry,75),GRAY),item('gear_hub',(0,ry,141),BLUE),
  item('servo_mount',(45,ry,106),BLUE),item('servo_pinion',(45,ry,151),GOLD,rz=9)]
 return parts

def draw(ax,parts,edges=False):
 if not hasattr(ax.figure,'r2_surfaces'):ax.figure.r2_surfaces=[]
 ax.figure.r2_surfaces.append((ax,parts,edges))

def raster_surfaces(fig):
 # Use a true depth buffer for the thin closed shells. mplot3d's average
 # triangle ordering otherwise lets interior faces show through the outside.
 fig.canvas.draw()
 for ax,parts,edges in getattr(fig,'r2_surfaces',[]):
  bb=ax.bbox;w,h=int(np.ceil(bb.width)),int(np.ceil(bb.height))
  pixels=np.zeros((h,w,4),dtype=np.uint8);depth=np.full((h,w),np.inf)
  matrix=ax.get_proj()
  el,az=np.deg2rad([ax.elev,ax.azim]);view=np.array([np.cos(el)*np.cos(az),np.cos(el)*np.sin(az),np.sin(el)])
  light=np.array([1.,1.,2.]);light/=np.linalg.norm(light)
  for m,color,_ in parts:
   visible=(m.face_normals@view)>1e-8;t=m.triangles[visible];normals=m.face_normals[visible]
   v=np.concatenate([t.reshape(-1,3),np.ones((len(t)*3,1))],axis=1)@matrix.T
   projected=v[:,:3]/v[:,3:4];xy=ax.transData.transform(projected[:,:2])-np.array([bb.x0,bb.y0])
   screen=np.column_stack([xy,projected[:,2]]).reshape(-1,3,3)
   base=np.array(to_rgba(color)[:3])*255
   for tri,normal in zip(screen,normals):
    x0,y0,z0=tri[0];x1,y1,z1=tri[1];x2,y2,z2=tri[2]
    den=(y1-y2)*(x0-x2)+(x2-x1)*(y0-y2)
    if abs(den)<.01:continue
    xmin=max(0,int(np.floor(tri[:,0].min())));xmax=min(w-1,int(np.ceil(tri[:,0].max())))
    ymin=max(0,int(np.floor(tri[:,1].min())));ymax=min(h-1,int(np.ceil(tri[:,1].max())))
    if xmin>xmax or ymin>ymax:continue
    xx,yy=np.meshgrid(np.arange(xmin,xmax+1)+.5,np.arange(ymin,ymax+1)+.5)
    a=((y1-y2)*(xx-x2)+(x2-x1)*(yy-y2))/den
    b=((y2-y0)*(xx-x2)+(x0-x2)*(yy-y2))/den;c=1-a-b
    zz=a*z0+b*z1+c*z2;region=depth[ymin:ymax+1,xmin:xmax+1]
    mask=(a>=-1e-6)&(b>=-1e-6)&(c>=-1e-6)&(zz<region)
    if not mask.any():continue
    rgb=np.clip(base*(.62+.38*max(0,float(normal@light))),0,255).astype(np.uint8)
    region[mask]=zz[mask];target=pixels[ymin:ymax+1,xmin:xmax+1]
    target[mask,:3]=rgb;target[mask,3]=255
    if edges:
     e=np.minimum(np.minimum(a*abs(den)/max(np.hypot(x1-x2,y1-y2),1e-6),b*abs(den)/max(np.hypot(x2-x0,y2-y0),1e-6)),c*abs(den)/max(np.hypot(x0-x1,y0-y1),1e-6))
     edge=mask&(e<.25);target[edge,:3]=(rgb*.83).astype(np.uint8)
  fig.figimage(pixels,xo=int(bb.x0),yo=int(bb.y0),origin='lower',zorder=3)

def bounds(ax,parts,pad=.08,angles=(22,55)):
 b=np.array([m.bounds for m,_,_ in parts]);lo=b[:,0].min(0);hi=b[:,1].max(0);size=hi-lo
 extent=np.maximum(size,8);center=(lo+hi)/2
 ax.set_xlim(center[0]-extent[0]*(.5+pad),center[0]+extent[0]*(.5+pad))
 ax.set_ylim(center[1]-extent[1]*(.5+pad),center[1]+extent[1]*(.5+pad))
 ax.set_zlim(center[2]-extent[2]*(.5+pad),center[2]+extent[2]*(.5+pad))
 ax.set_box_aspect(extent);ax.set_proj_type('ortho');ax.view_init(*angles)
 ax.set_xlabel('X (mm)',labelpad=8);ax.set_ylabel('Y (mm)',labelpad=8);ax.set_zlabel('Z (mm)',labelpad=8)
 ax.tick_params(labelsize=8,pad=1)
 for axis in [ax.xaxis,ax.yaxis,ax.zaxis]:axis.pane.set_facecolor((.98,.985,.99,1));axis.pane.set_edgecolor('#D7E0E8')
 ax.grid(True)

def footer(fig,text):fig.text(.035,.025,text,fontsize=9,color='#526779')
def save(fig,name):
 path=OUT/(name+'.png');raster_surfaces(fig);fig.savefig(path,dpi=170);plt.close(fig)
 with Image.open(path) as im:assert im.width>=1800 and im.height>=1200;im.verify()
 ARTIFACTS.append(path);print('Rendered '+path.name,flush=True)

def overview():
 p=robot();fig=plt.figure(figsize=(13,10));ax=fig.add_axes([.02,.08,.74,.83],projection='3d');bounds(ax,p);draw(ax,p)
 fig.suptitle('R2-24  |  assembled robot',x=.05,ha='left',fontsize=21,fontweight='bold',y=.97)
 fig.text(.775,.79,'REVISION B',color=BLUE,fontsize=15,fontweight='bold')
 fig.text(.775,.755,'Nominal height: 609.6 mm\nBody diameter: 260 mm\nFoot cover span: 492 mm',linespacing=1.8,fontsize=11,va='top')
 fig.text(.775,.54,'2 stackable body prints\n1 complete print per arm\n6 drive motors / 12 wheels\nPowered rear steering\nContinuously rotating head',linespacing=1.9,fontsize=10.5,va='top')
 fig.legend(handles=[Patch(color='#C3D6E7',label='Printed shell / structure'),Patch(color=BLUE,label='Drive parts / blue trim'),Patch(color=ORANGE,label='Wheel envelopes'),Patch(color=GOLD,label='Motor / bearing envelopes')],loc='lower right',bbox_to_anchor=(.98,.19),frameon=False,fontsize=9)
 footer(fig,'STL-derived surfaces. Purchased parts are schematic envelopes. Dimensions in millimetres; hardware operation untested.');save(fig,'01-robot-isometric')

def ortho():
 p=robot();fig,axes=plt.subplots(1,3,figsize=(18,9),gridspec_kw={'width_ratios':[1,1,1.1]})
 for ax,(horizontal,vertical,depth,title) in zip(axes,[(0,2,1,'Front  |  looking along -Y'),(1,2,0,'Right side  |  looking along -X'),(0,1,2,'Top  |  looking down -Z')]):
  polys=[];colors=[];depths=[]
  for m,color,_ in p:
   t=m.triangles;polys.extend(t[:,:,[horizontal,vertical]]);colors.extend([color]*len(t));depths.extend(t[:,:,depth].mean(1))
  order=np.argsort(depths);ax.add_collection(PolyCollection(np.array(polys)[order],facecolors=np.array(colors)[order],edgecolors='none',rasterized=True))
  ax.autoscale();ax.set_aspect('equal');ax.margins(.15);ax.grid(True);ax.set_axisbelow(True)
  ax.set_xlabel('XYZ'[horizontal]+' (mm)');ax.set_ylabel('XYZ'[vertical]+' (mm)');ax.set_title(title,pad=16)
 axes[0].annotate('',xy=(-275,609.6),xytext=(-275,0),arrowprops={'arrowstyle':'<->','color':BLUE,'lw':1.4})
 axes[0].text(-290,305,'609.6 mm nominal',rotation=90,va='center',ha='right',color=BLUE)
 axes[0].annotate('',xy=(-130,650),xytext=(130,650),arrowprops={'arrowstyle':'<->','color':BLUE});axes[0].text(0,667,'260 mm body',ha='center',color=BLUE)
 axes[0].set_xlim(-330,280);axes[0].set_ylim(-50,700)
 fig.suptitle('R2-24  |  orthographic views',fontsize=22,fontweight='bold',x=.045,ha='left')
 fig.subplots_adjust(left=.05,right=.98,top=.89,bottom=.12,wspace=.27)
 footer(fig,'Revision B. Equal scale within each panel; panel scales differ. Purchased components use schematic envelopes.');save(fig,'02-robot-orthographic')

def exploded():
 p=robot(True);fig=plt.figure(figsize=(13,11));ax=fig.add_axes([.01,.07,.73,.85],projection='3d');bounds(ax,p,pad=.05);draw(ax,p)
 fig.suptitle('R2-24  |  exploded assembly',x=.04,ha='left',fontsize=22,fontweight='bold',y=.97)
 for i,(title,description) in enumerate([('01  Dome and head drive','One dome; separate bearing drive'),('02  Upper body','One print: frame, head deck and neck'),('03  Lower body','One print: base, posts and battery tray'),('04  Left / right arms','One print per arm; shoulder integrated'),('05  Three drive feet','Two motors and four wheels per foot')]):
  y=.82-i*.135;fig.text(.755,y,title,fontsize=12,fontweight='bold',color=BLUE);fig.text(.755,y-.043,description,fontsize=9,color=INK,wrap=True)
 footer(fig,'Parts separated for identification. Exploded offsets are not assembly dimensions. Follow the Revision B manual for fastening.');save(fig,'03-robot-exploded')

def mechanisms():
 fig=plt.figure(figsize=(16,10));p=foot(exploded=True,cover=True);ax=fig.add_subplot(121,projection='3d');bounds(ax,p,angles=(26,55));draw(ax,p,True);ax.set_title('Drive foot | exploded',pad=18)
 ax2=fig.add_subplot(122,projection='3d');p2=head(-400,True);p2=[x for x in p2 if x[2] not in ['dome','eye']];bounds(ax2,p2,angles=(25,55));draw(ax2,p2,True);ax2.set_title('Head rotation mechanism | dome removed',pad=18)
 fig.suptitle('R2-24  |  mechanisms broken out',x=.04,ha='left',fontsize=22,fontweight='bold')
 fig.text(.09,.13,'Foot: cover -> deck -> 2 motor envelopes -> 2 cradles\nFour wheel envelopes are moved outward for visibility.',fontsize=10,linespacing=1.7)
 fig.text(.55,.13,'Head: spacers -> plate -> driven gear -> cap -> bearings / tower\nServo envelope and 20-tooth pinion sit beside the 40-tooth hub.',fontsize=10,linespacing=1.7)
 fig.subplots_adjust(left=.03,right=.97,top=.9,bottom=.22,wspace=.05)
 footer(fig,'Coordinates are local drawing coordinates, not installation heights. Gold and orange purchased shapes are schematic.');save(fig,'04-mechanisms-exploded')

def catalog():
 groups=[('05-body-and-arm-components',['body_lower','body_upper','arm_left','arm_right','dome','eye']),
 ('06-foot-and-steering-components',['foot_deck','foot_cover','motor_cradle','rear_bracket','rear_attach','spindle_sleeve']),
 ('07-head-drive-components',['bearing_tower','bearing_cap','race_spacer','gear_hub','servo_pinion','servo_mount','head_plate','dome_spacer']),
 ('08-mounts-and-small-components',['utility_deck','speaker_mount','switch_plate','pcb_spacer','servo_shim_1','servo_shim_2','servo_shim_4','detail_panel','coupon'])]
 covered=[]
 for filename,names in groups:
  count=len(names);cols=3 if count in [6,9] else 4;nr=(count+cols-1)//cols
  fig=plt.figure(figsize=(18,11));fig.suptitle('R2-24  |  '+filename[3:].replace('-',' '),x=.035,ha='left',fontsize=22,fontweight='bold',y=.98)
  for i,name in enumerate(names):
   ax=fig.add_subplot(nr,cols,i+1,projection='3d');r=ROWS[name];mesh=MESH[name].copy();mesh.apply_translation(-mesh.bounds[0]);p=[(mesh,BLUE if r['material']=='PETG' else GRAY,name)]
   bounds(ax,p,pad=.10,angles=(28,40));draw(ax,p,True);ax.set_title(name.replace('_',' ')+f'  |  qty {r["quantity"]}',fontsize=12,fontweight='bold',pad=3)
   ax.set_xticks([]);ax.set_yticks([]);ax.set_zticks([]);ax.set_xlabel('');ax.set_ylabel('');ax.set_zlabel('')
   ax.text2D(.5,-.03,f'{r["x_mm"]:g} x {r["y_mm"]:g} x {r["z_mm"]:g} mm  |  {r["material"]}',transform=ax.transAxes,ha='center',fontsize=9,color=INK)
   covered.append(name)
  fig.subplots_adjust(left=.035,right=.965,bottom=.10,top=.91,wspace=.12,hspace=.26)
  footer(fig,'Actual STL geometry. Dimensions: X x Y x Z. Panels scaled independently. Quantities include fit coupon, shim options and spare spacers.');save(fig,filename)
 assert len(covered)==29 and set(covered)==set(ROWS)

def main():
 OUT.mkdir(parents=True,exist_ok=True);overview();ortho();exploded();mechanisms();catalog()
 report={'style':'MATLAB-style Matplotlib surface drawings','revision':'B','printed_components':29,'geometry_changed':False,
 'sources':{n:hashlib.sha256((ROOT/'stl'/f'{n}.stl').read_bytes()).hexdigest() for n in ROWS},
 'pngs':[{ 'file':p.name,'pixels':list(Image.open(p).size),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in ARTIFACTS]}
 (OUT/'index.json').write_text(json.dumps(report,indent=2))
 with zipfile.ZipFile(OUT/'r2d2-matlab-style-drawings.zip','w',zipfile.ZIP_DEFLATED) as z:
  for p in ARTIFACTS:z.write(p,p.name)
  z.write(OUT/'index.json','index.json')
 print('PASS: 8 PNG drawings; all 29 STL components included; source geometry unchanged')
if __name__=='__main__':main()
