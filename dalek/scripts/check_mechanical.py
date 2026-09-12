"""Sample released FACET-1 component, motion and assembly-path clearances.

These are nominal digital envelope checks, not a print-strength or hardware test.
"""
import hashlib
import json
from pathlib import Path
import numpy as np
import trimesh
from mesh_queries import contains, METHOD

ROOT = Path(__file__).resolve().parents[1]
rng = np.random.default_rng(37773766)
meshes = {p.stem: trimesh.load_mesh(p, process=True) for p in (ROOT / "stl").glob("*.stl")}
mesh_hashes = {n:hashlib.sha256((ROOT/"stl"/(n+".stl")).read_bytes()).hexdigest() for n in sorted(meshes)}
for name,mesh in meshes.items():
    if not mesh.is_watertight or not mesh.is_winding_consistent or mesh.volume<=0:
        raise SystemExit(f"Refusing mechanical samples against invalid solid: {name}")
results = []

def record(name, points, hits, expected=0):
    row = dict(check=name, samples=int(points), interior_hits=int(hits), expected_hits=expected, passed=bool(hits == expected))
    results.append(row)
    print(json.dumps(row), flush=True)

def box(lo, hi, count=2500):
    return rng.uniform(lo, hi, (count, 3))

def rot(degrees, axis):
    return trimesh.transformations.rotation_matrix(np.radians(degrees), axis)[:3, :3]

base = meshes["01_base"]
for center in (95.5, 98, 100.5):
    samples = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            a = rng.uniform(0, 2*np.pi, 5000)
            r = np.sqrt(rng.uniform(0, 1, 5000))*31.49
            q = np.column_stack([rng.uniform(-14.49,14.49,5000)+center,58+r*np.cos(a),17.7+r*np.sin(a)])
            q[:,0] *= sx; q[:,1] *= sy
            samples.append(q)
    q = np.concatenate(samples)
    record(f"base-wheel-X{center}",len(q),contains(base,q).sum())
for label, lo, hi in [("gearbox",[-9.25,-30.95,.05],[9.25,12.95,22.39]),("metal-tail",[-11.15,-56.95,.05],[11.15,-31.05,22.39])]:
    samples=[]
    for sx in (-1,1):
        for sy in (-1,1):
            q=box(lo,hi,5000)+[70.5,58,6];q[:,0]*=sx;q[:,1]*=sy;samples.append(q)
    q=np.concatenate(samples);record("base-"+label,len(q),contains(base,q).sum())
for label,size in [('Bioenno',[70,114,76]),('SLA-7Ah',[67,153,102]),('SLA-14Ah',[100,153,103])]:
    q=box([-size[0]/2+.1,-size[1]/2+.1,8.1],[size[0]/2-.1,size[1]/2-.1,8+size[2]-.1],8000)
    record('base-battery-'+label,len(q),contains(base,q).sum())
a=np.linspace(0,2*np.pi,720,endpoint=False)
q=np.concatenate([np.column_stack([149*np.cos(a),149*np.sin(a),np.full(len(a),z)]) for z in (5,15,28,42)])
record("continuous-bumper-missing-material",len(q),len(q)-contains(base,q).sum())

skirt=meshes["02_skirt"]
record("merged-skirt-213mm-height",1,int(abs(skirt.extents[2]-213)>.001))
record("merged-skirt-320mm-height-limit",1,int(skirt.extents[2]>320))
# Four remaining lower bolts use a250mm shaft with an inward16degree tilt.
# The3mm hex shaft has a1.733mm corner radius. Its ball engages at localZ10.
tool_angles=np.linspace(0,2*np.pi,24,endpoint=False)
for azimuth in (0,90,180,270):
    turn=rot(azimuth,[0,0,1]);tilt=rot(-16,[0,1,0])
    section=np.column_stack([1.74*np.cos(tool_angles),1.74*np.sin(tool_angles),np.zeros(24)])@tilt.T
    direction=tilt@np.array([0,0,1])
    q=np.concatenate([section+[137,0,10]+direction*t for t in np.linspace(0,250,150)])@turn.T
    record(f"merged-skirt-250mm-ball-driver-{azimuth}",len(q),contains(skirt,q).sum())
    record(f"merged-skirt-driver-base-{azimuth}",len(q),contains(base,q+[0,0,54]).sum())
    center=np.array([137*np.cos(np.radians(azimuth)),137*np.sin(np.radians(azimuth)),0])
    q=np.concatenate([np.column_stack([1.7*np.cos(tool_angles),1.7*np.sin(tool_angles),np.full(24,z)])+center for z in np.linspace(.05,5.95,30)])
    record(f"merged-skirt-bottom-M4-hole-{azimuth}",len(q),contains(skirt,q).sum())
for label,rr,zz,target in [("bottom-tongue-groove",(143.51,145.49),(.01,2.99),skirt),
                            ("top-tongue-groove",(103.51,105.49),(.01,2.99),meshes["04_shoulder"])]:
    a=rng.uniform(0,2*np.pi,5000);radius=rng.uniform(*rr,5000)
    q=np.column_stack([radius*np.cos(a),radius*np.sin(a),rng.uniform(*zz,5000)])
    record("merged-skirt-"+label,len(q),contains(target,q).sum())
# The former middle flanges occupied inward radii down to107mm. Only a
# tapered integral rib remains, with120mm minimum internal radius.
a=np.linspace(0,2*np.pi,180,endpoint=False)
q=np.concatenate([np.column_stack([119.75*np.cos(a),119.75*np.sin(a),np.full(len(a),z)]) for z in np.linspace(104,116,25)])
record("merged-skirt-middle-nominal240mm-bore",len(q),contains(skirt,q).sum())

shoulder=meshes["04_shoulder"]
carrier=meshes["07_pitch_carrier"]
arm=meshes["08_plunger_arm"]
arm_vertices=(arm.vertices-[0,0,28])@(rot(-90,[0,0,1])@rot(90,[1,0,0])).T
for x in (-47,53):
    q=box([-16.25,-5.95,7.05],[6.25,5.95,37.95],3000)+[x,-94,0]
    record(f"yaw-case-{x}",len(q),contains(shoulder,q).sum())
    for yaw in (-8,0,8):
        rz=rot(yaw,[0,0,1]);q=carrier.vertices@rz.T+[x,-94,42]
        record(f"carrier-{x}-yaw{yaw}",len(q),contains(shoulder,q).sum())
        q=box([1.05,-5.95,18.75],[31.95,5.95,41.25],1500)@rz.T+[x,-94,42]
        record(f"pitch-case-{x}-yaw{yaw}",len(q),contains(shoulder,q).sum())
        for pitch in (-8,0,8):
            p=arm_vertices@rot(pitch,[1,0,0]).T
            q=(p+[-3,0,35])@rz.T+[x,-94,42]
            record(f"arm-{x}-yaw{yaw}-pitch{pitch}",len(q),contains(shoulder,q).sum())
            record(f"cap-case-{x}-{yaw}-{pitch}",len(p),((p>[4,-6,-16.3])&(p<[35,6,6.3])).all(axis=1).sum())

# Bottom insertion is covered by check_arm_assembly.py and check_upper_mounts.py.
neck=meshes["04_shoulder"].copy();neck.apply_translation([0,0,-120])
slide=meshes["10_head_motor_carriage"];head=meshes["06_head"]
for cx in (61.5,64.5,65.1):
    for label,lo,hi in [("gearbox",[-9.25,-30.95,.05],[9.25,12.95,22.39]),("metal-tail",[-11.15,-56.95,.05],[11.15,-31.05,22.39])]:
        p=box(lo,hi);q=np.column_stack([cx+p[:,2]-11.7,p[:,1],43.5+p[:,0]])
        record(f"head-{label}-neck-{cx}",len(q),contains(neck,q).sum())
        record(f"head-{label}-slide-{cx}",len(q),contains(slide,q-[cx,0,29.2]).sum())
    q=slide.vertices[slide.vertices[:,2]>.01]+[cx,0,29.2]
    record(f"slide-neck-{cx}",len(q),contains(neck,q).sum())
    a=rng.uniform(0,2*np.pi,5000);r=np.sqrt(rng.uniform(0,1,5000))*31.49
    q=np.column_stack([cx+r*np.cos(a),r*np.sin(a),rng.uniform(56.51,85.49,5000)])
    record(f"head-wheel-neck-{cx}",len(q),contains(neck,q).sum())
    if cx<64.5:record(f"released-wheel-drum-{cx}",len(q),contains(head,q-[0,0,52]).sum())
    else:
        h=contains(head,q-[0,0,52]);outside=(q[h,0]<95.3)|(q[h,2]>=91)
        record("outward-contact-outside-intended-track",int(h.sum()),outside.sum())

angle=np.linspace(0,2*np.pi,24,endpoint=False)
for x,y in [(43,-50),(43,8),(83.5,-40),(83.5,8)]:
    samples=[]
    for z in np.linspace(34.9,49.9,32):samples.append(np.column_stack([x+1.445*np.cos(angle),y+1.445*np.sin(angle),np.full(24,z)]))
    for yy in np.linspace(-112 if y<0 else 112,y,120):samples.append(np.column_stack([x+1.445*np.cos(angle),np.full(24,yy),49.9+1.445*np.sin(angle)]))
    q=np.concatenate(samples)
    record(f"slide-L-key-neck-{x}-{y}",len(q),contains(neck,q).sum())
    record(f"slide-L-key-carriage-{x}-{y}",len(q),contains(slide,q-[64.5,0,29.2]).sum())
# Ideal opaque fabric annulus: fixed radius30 atY-111, radius24 attached
# inside the moving spherical-cap rear rim. Actual folds and opacity are a
# physical acceptance gate. These rays check a continuous nominal liner.
occlusion_rng=np.random.default_rng(101)
a=np.linspace(0,2*np.pi,96,endpoint=False)
fabric_faces=[]
for i in range(96):
    j=(i+1)%96;fabric_faces.extend([[i,j,96+j],[i,96+j,96+i]])
arm_rotation=rot(-90,[0,0,1])@rot(90,[1,0,0])
for yaw,pitch in [(-8,-8),(-8,8),(0,0),(8,-8),(8,8)]:
    rz=rot(yaw,[0,0,1]);rp=rot(pitch,[1,0,0]);chunks=[shoulder]
    for name,z in [("06_head",172),("02_skirt",-210)]:
        m=meshes[name].copy();m.apply_translation([0,0,z]);chunks.append(m)
    targets=[]
    for x,name in [(-47,"08_plunger_arm"),(53,"09_emitter_arm")]:
        m=meshes[name].copy();m.vertices=(((m.vertices-[0,0,28])@arm_rotation.T)@rp.T+[-3,0,35])@rz.T+[x,-94,42];chunks.append(m)
        outer=np.column_stack([x-3-30*np.sin(a),np.full(96,-111),77+30*np.cos(a)])
        inner=(np.column_stack([np.full(96,12),24*np.cos(a),24*np.sin(a)])@arm_rotation.T@rp.T+[-3,0,35])@rz.T+[x,-94,42]
        chunks.append(trimesh.Trimesh(vertices=np.concatenate([outer,inner]),faces=fabric_faces,process=False))
        targets.extend(occlusion_rng.uniform([-16,-5,8],[6,5,37],(16,3))+[x,-94,0])
        targets.extend(occlusion_rng.uniform([2,-5,19],[31,5,41],(16,3))@rz.T+[x,-94,42])
    scene=trimesh.util.concatenate(chunks);targets=np.array(targets);visible=total=0
    for azimuth in (-100,-60,0,60,100):
        for elevation in (-30,0,45):
            aa,ee=np.radians([azimuth,elevation])
            origin=np.array([0,-70,50])+700*np.array([np.sin(aa)*np.cos(ee),-np.cos(aa)*np.cos(ee),np.sin(ee)])
            origins=np.tile(origin,(len(targets),1));directions=targets-origins;distance=np.linalg.norm(directions,axis=1);directions/=distance[:,None]
            hit,ray_index,_=scene.ray.intersects_location(origins,directions,multiple_hits=False)
            blocked=np.zeros(len(targets),bool);blocked[ray_index]=np.linalg.norm(hit-origins[ray_index],axis=1)<distance[ray_index]-.01
            visible+=int((~blocked).sum());total+=len(targets)
    record(f"opaque-liner-visible-servo-rays-{yaw}-{pitch}",total,visible)

assert mesh_hashes=={n:hashlib.sha256((ROOT/"stl"/(n+".stl")).read_bytes()).hexdigest() for n in sorted(meshes)},"Mesh changed during mechanical checks"
report={"design":"FACET-1","method":METHOD+"; deterministic nominal samples and mesh-vertex paths; no physical test","seed":37773766,"all_pass":all(r["passed"] for r in results),"mesh_sha256":mesh_hashes,"checks":results,"limits":["Finite sampling is not an exact collision proof.","Paint, tire runout, real horns, cable ties, fabric folds and print strength require builder checks.","Fabric liners must be opaque and remain attached throughout the permitted eight-degree motion."]}
(ROOT/"cad/mechanical-checks.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
raise SystemExit(0 if report["all_pass"] else "Mechanical sampling failed; see cad/mechanical-checks.json")
