"""Bound only extrusion paths labelled as sliced features, excluding machine G-code."""
import math
import re

def deposition_bounds(gcode):
    current={'X':None,'Y':None,'Z':None,'E':0.0}
    xyz_absolute=True
    e_absolute=True
    feature='Custom'
    started=False
    bounds=[math.inf,math.inf,-math.inf,-math.inf]
    deposition_z=[math.inf,-math.inf]
    model_z=[math.inf,-math.inf]
    def include(x,y):
        bounds[0]=min(bounds[0],x);bounds[1]=min(bounds[1],y)
        bounds[2]=max(bounds[2],x);bounds[3]=max(bounds[3],y)
    features=set()
    feature_lengths={}
    move_count=0
    tools=set()
    tool=None
    for line in gcode.splitlines():
        if line.startswith('; CHANGE_LAYER'):started=True
        if line.startswith('; FEATURE: '):feature=line.split(': ',1)[1]
        text=line.split(';',1)[0].strip()
        if not text:continue
        command=text.split()[0]
        values={k:float(v) for k,v in re.findall(r'([XYZEFIJP])\s*(-?(?:\d+(?:\.\d*)?|\.\d+))',text)}
        if command=='G90':xyz_absolute=True
        elif command=='G91':xyz_absolute=False
        elif command=='M82':e_absolute=True
        elif command=='M83':e_absolute=False
        elif re.fullmatch(r'T\d+',command):tool=command
        elif command=='G92':
            for axis in current:
                if axis in values:current[axis]=values[axis]
        elif command in {'G0','G1','G2','G3'}:
            previous=current.copy()
            for axis in current:
                if axis in values:
                    absolute=e_absolute if axis=='E' else xyz_absolute
                    current[axis]=values[axis] if absolute else (current[axis] or 0)+values[axis]
            delta=current['E']-previous['E']
            if started and feature not in {'Custom','Flush'} and delta>0 and all(current[k] is not None and previous[k] is not None for k in ['X','Y']):
                if abs(current['X']-previous['X'])>1e-8 or abs(current['Y']-previous['Y'])>1e-8 or command in {'G2','G3'}:
                    feature_lengths[feature]=feature_lengths.get(feature,0.0)+delta
                    if current['Z'] is not None:
                        deposition_z[0]=min(deposition_z[0],current['Z'])
                        deposition_z[1]=max(deposition_z[1],current['Z'])
                        if not feature.startswith('Support') and feature not in {'Brim','Skirt'}:
                            model_z[0]=min(model_z[0],current['Z'])
                            model_z[1]=max(model_z[1],current['Z'])
                move_count+=1
                features.add(feature)
                if tool:tools.add(tool)
                include(previous['X'],previous['Y']);include(current['X'],current['Y'])
                if command in {'G2','G3'} and ('I' in values or 'J' in values):
                    cx=previous['X']+values.get('I',0)
                    cy=previous['Y']+values.get('J',0)
                    radius=math.hypot(previous['X']-cx,previous['Y']-cy)
                    start=math.atan2(previous['Y']-cy,previous['X']-cx)
                    end=math.atan2(current['Y']-cy,current['X']-cx)
                    sign=1 if command=='G3' else -1
                    sweep=(sign*(end-start))%(2*math.pi)
                    if abs(current['X']-previous['X'])<1e-7 and abs(current['Y']-previous['Y'])<1e-7:sweep=2*math.pi
                    for angle in [0,math.pi/2,math.pi,3*math.pi/2]:
                        if (sign*(angle-start))%(2*math.pi)<=sweep+1e-6:
                            include(cx+radius*math.cos(angle),cy+radius*math.sin(angle))
    if not move_count:return {'verified':False,'reason':'No extruding sliced moves found'}
    widths=[float(n) for n in re.findall(r'^; LINE_WIDTH: ([0-9.]+)',gcode,re.MULTILINE)]
    width=max(widths+[0.5])
    bead_bounds=[bounds[0]-width/2,bounds[1]-width/2,bounds[2]+width/2,bounds[3]+width/2]
    fitting=[name for name,x0,x1 in [('left',0,325),('right',25,350)] if bead_bounds[0]>=x0 and bead_bounds[2]<=x1 and bead_bounds[1]>=0 and bead_bounds[3]<=320]
    density_match=re.search(r'^; filament_density: ([0-9.]+)',gcode,re.MULTILINE)
    diameter_match=re.search(r'^; filament_diameter: ([0-9.]+)',gcode,re.MULTILINE)
    density=float(density_match[1]) if density_match else None
    diameter=float(diameter_match[1]) if diameter_match else None
    usage={}
    if density and diameter:
        factor=math.pi*(diameter/2)**2*density/1000
        masses={name:amount*factor for name,amount in feature_lengths.items()}
        support=sum(mass for name,mass in masses.items() if name.startswith('Support'))
        brim=sum(mass for name,mass in masses.items() if name in {'Brim','Skirt'})
        model=sum(masses.values())-support-brim
        usage={'density_g_cm3':density,'filament_diameter_mm':diameter,'filament_length_mm_by_feature':{k:round(v,3) for k,v in sorted(feature_lengths.items())},'filament_mass_g_by_feature':{k:round(v,3) for k,v in sorted(masses.items())},'estimated_installed_printed_model_mass_g':round(model,3),'support_mass_g':round(support,3),'brim_and_skirt_mass_g':round(brim,3),'all_labelled_moving_extrusion_mass_g':round(sum(masses.values()),3),'method':'Sum positive filament extrusion on XY-moving G0/G1/G2/G3 paths labelled after CHANGE_LAYER; exclude Custom/Flush machine commands and stationary unretraction; convert1.75mmfilament length with G-code profile density. Support labels and Brim/Skirt are separated from model labels. This is a G-code prediction, not measured installed mass.'}
    return {'verified':True,'extruding_move_count':move_count,'features':sorted(features),'tools_in_sliced_features':sorted(tools),'extrusion_centerline_bounds_xy_mm':[round(x,4) for x in bounds],'extrusion_centerline_size_xy_mm':[round(bounds[2]-bounds[0],4),round(bounds[3]-bounds[1],4)],'deposition_z_range_mm':[round(z,4) for z in deposition_z],'model_deposition_z_range_mm':[round(z,4) for z in model_z],'maximum_bead_width_used_mm':width,'conservative_bead_bounds_xy_mm':[round(x,4) for x in bead_bounds],'single_nozzle_areas_containing_all_paths':fitting,'within_one_325x320_nozzle_area':bool(fitting),'feature_extrusion_estimates':usage,'excluded_features':['Custom','Flush'],'limitation':'Bounds include sliced model, support and brim paths with half the maximum bead width added. Machine purge/cleaning moves are excluded. Z ranges are actual moving deposition endpoints, separate from slicer header metadata.'}
