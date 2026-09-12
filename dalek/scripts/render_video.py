"""Render the current Dalek assembly and illustrative operation as a 120-second MP4.

Existing local tools: Python/trimesh/Playwright/Pillow, Chrome, FFmpeg, Windows speech.
No user browser profile, network account, printer or robot is accessed.
"""
import argparse
import base64
from functools import partial
import hashlib
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import io
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import threading
import time

import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright
import trimesh
from render_drawings import NAMES, BOARD_LAYOUT

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/video'
CHROME=Path('C:/Program Files/Google/Chrome/Application/chrome.exe')
FPS=24
WIDTH,HEIGHT=1920,1080
DURATION=120
KEYFRAMES=[0,11,18,24,29,35,40,49,53,56,63,67,72,75,79,83,87.5,91,94.5,97,99,106,110,111.1,113,114.5,119]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def shifted(mesh,xyz):
    mesh=mesh.copy();mesh.apply_translation(xyz);return mesh


def bolt(diameter,length,head_diameter,head_height):
    shaft=shifted(trimesh.creation.cylinder(radius=diameter/2,height=length,sections=20),(0,0,-length/2))
    head=shifted(trimesh.creation.cylinder(radius=head_diameter/2,height=head_height,sections=6),(0,0,head_height/2))
    return trimesh.util.concatenate([shaft,head])


def tube(points,radius=1.5,sides=8,closed=False):
    points=np.asarray(points,dtype=float)
    if closed:
        tangents=np.roll(points,-1,axis=0)-np.roll(points,1,axis=0)
    else:
        tangents=np.gradient(points,axis=0)
    tangents/=np.linalg.norm(tangents,axis=1)[:,None]
    reference=np.tile([0.,0.,1.],(len(points),1))
    reference[np.abs(tangents[:,2])>.9]=[1,0,0]
    normals=np.cross(tangents,reference);normals/=np.linalg.norm(normals,axis=1)[:,None]
    binormals=np.cross(tangents,normals)
    angles=np.arange(sides)*2*np.pi/sides
    vertices=(points[:,None,:]+radius*(np.cos(angles)[None,:,None]*normals[:,None,:]+np.sin(angles)[None,:,None]*binormals[:,None,:])).reshape(-1,3)
    faces=[]
    for j in range(len(points) if closed else len(points)-1):
        next_j=(j+1)%len(points)
        for k in range(sides):
            a=j*sides+k;b=j*sides+(k+1)%sides;c=next_j*sides+k;d=next_j*sides+(k+1)%sides
            faces.extend([[a,c,b],[b,c,d]])
    return trimesh.Trimesh(vertices=vertices,faces=faces,process=False)


def geometry():
    meshes={name:trimesh.load_mesh(ROOT/'stl'/f'{name}.stl',process=True) for name in NAMES}
    # Split existing triangles into paint regions; no surface or STL is changed.
    for name in ['08_plunger_arm','09_emitter_arm']:
        mesh=meshes[name];centers=mesh.triangles_center
        radial=np.hypot(centers[:,1],centers[:,2]-28)
        cap=(centers[:,0]>=7.99)&(centers[:,0]<=28.01)&(radial>6.1)
        if name=='08_plunger_arm':
            cap|=centers[:,0]>=104
        meshes['finish_'+name]=mesh.submesh([cap],append=True,repair=False)
        meshes[name]=mesh.submesh([~cap],append=True,repair=False)
    mesh=meshes['06_head'];centers=mesh.triangles_center
    drum=(centers[:,2]<39)&(np.hypot(centers[:,0],centers[:,1])>98.8)
    eye=(centers[:,1]<-112)&(np.hypot(centers[:,0],centers[:,2]-63)<16)
    discs=eye&(centers[:,1]>-152)&(np.hypot(centers[:,0],centers[:,2]-63)>8)
    lens=eye&(centers[:,1]<=-152)&(centers[:,1]>=-174.5)
    face=eye&(centers[:,1]<-174.5)
    for name,mask in [('finish_eye_discs',discs),('finish_eye_lens',lens),('finish_eye_face',face)]:
        meshes[name]=mesh.submesh([mask],append=True,repair=False)
    meshes['finish_head_drum']=mesh.submesh([drum],append=True,repair=False)
    meshes['06_head']=mesh.submesh([~(drum|discs|lens|face)],append=True,repair=False)
    mesh=meshes['05_neck'];centers=mesh.triangles_center
    radial=np.hypot(centers[:,0],centers[:,1])
    liner=(radial>94)&(radial<98.8)&(centers[:,2]<53)
    meshes['finish_neck_liner']=mesh.submesh([liner],append=True,repair=False)
    meshes['05_neck']=mesh.submesh([~liner],append=True,repair=False)
    meshes['cube']=trimesh.creation.box(extents=[1,1,1])
    meshes['cylinder']=trimesh.creation.cylinder(radius=1,height=1,sections=40)
    for name,inner,outer,height,sections in [
        ('wheel',27.5,31.5,29,48),('bearing608',4,11,7,48),('spacer12',4.05,6,12,32),
        ('shim8',4,6,1,32),('top_washer8',4.2,8,1.6,32),('retaining_washer',1.7,4.5,1,24),
        ('washer3',1.7,3.5,1,24),('guide_washer3',1.7,3,1,24),('washer4',2.2,4.5,1.2,24),
        ('nut3',1.5,3.17,2.4,6),('nut4',2,4.04,3.2,6),('nut8',4,7.5,6.5,6),('spacer25',1.25,3.5,25,24),
        ('socket_liner',22,33,.7,48)]:
        meshes[name]=trimesh.creation.annulus(r_min=inner,r_max=outer,height=height,sections=sections)
    meshes['head_wheel']=meshes['wheel'].copy()
    meshes['wheel'].apply_transform(trimesh.transformations.rotation_matrix(np.pi/2,[0,1,0]))
    meshes['bolt3']=bolt(3,40,5.5,3)
    meshes['bolt4']=bolt(4,20,7,4)
    meshes['screw8']=bolt(3,8,5.5,3)
    meshes['guide16']=bolt(3,16,5.5,3)
    meshes['adjust25']=bolt(3,25,5.5,3)
    meshes['spindle8']=trimesh.util.concatenate([
        shifted(trimesh.creation.cylinder(radius=4,height=70,sections=24),(0,0,35)),
        shifted(trimesh.creation.cylinder(radius=7.5,height=5,sections=6),(0,0,-2.5))])
    meshes['power_wires']=trimesh.util.concatenate([
        tube([[0,38,82],[0,50,82],[32,70,67],[32,92,61]],1.4),
        tube([[32,92,61],[55,92,61],[70,80,63],[90,42,52]],1.2),
        tube([[32,-95,61],[55,-95,61],[70,-80,63],[90,-42,52]],1.2)])
    meshes['ground_wires']=tube([[-32,-95,61],[-50,-75,61],[-50,75,61],[-32,95,61]],1.2)
    meshes['upper_harness']=tube([[45,75,62],[45,75,140],[45,75,260],[15,92,315],[0,105,340]],1.8)
    return meshes


def export_scene(target):
    source_paths=[ROOT/'cad/dalek.scad',ROOT/'firmware/include/config.h',ROOT/'firmware/include/control.h',
                  ROOT/'firmware/src/main.cpp',ROOT/'scripts/render_drawings.py',ROOT/'scripts/video_scene.js',
                  ROOT/'scripts/video_storyboard.json',ROOT/'bom/electronics.csv',ROOT/'bom/hardware.csv',
                  *[ROOT/'stl'/f'{name}.stl' for name in NAMES],*sorted((ROOT/'firmware/data/audio').glob('*.mp3'))]
    hashes={p.relative_to(ROOT).as_posix():sha(p) for p in source_paths}
    data={'meshes':{},'sources':hashes,'board_layout':BOARD_LAYOUT,
          'storyboard':json.loads((ROOT/'scripts/video_storyboard.json').read_text())}
    for name,mesh in geometry().items():
        positions=mesh.triangles.reshape(-1,3)
        normals=np.repeat(mesh.face_normals,3,axis=0)
        packed=np.concatenate([positions,normals],axis=1).astype('<f4')
        data['meshes'][name]={'count':len(positions),'buffer':base64.b64encode(packed.tobytes()).decode('ascii')}
    (target/'scene.json').write_text(json.dumps(data,separators=(',',':')),encoding='utf-8')
    shutil.copyfile(ROOT/'scripts/video_scene.js',target/'video_scene.js')
    (target/'index.html').write_text('<!doctype html><html><head><meta charset="utf-8"><style>html,body{margin:0;background:#fff;overflow:hidden}</style></head><body><canvas id="output"></canvas><script src="video_scene.js"></script></body></html>',encoding='utf-8')
    return data,hashes


class RenderHandler(SimpleHTTPRequestHandler):
    def log_message(self,*args):
        pass

    def do_GET(self):
        if self.path not in ['/','/index.html','/video_scene.js','/scene.json']:
            self.send_error(404);return
        super().do_GET()


def timestamp(seconds):
    milliseconds=int(round(seconds*1000));hours,milliseconds=divmod(milliseconds,3600000)
    minutes,milliseconds=divmod(milliseconds,60000);seconds,milliseconds=divmod(milliseconds,1000)
    return f'{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}'


def run():
    parser=argparse.ArgumentParser();parser.add_argument('--preview',action='store_true');parser.add_argument('--audio',type=Path)
    args=parser.parse_args()
    for executable in ['ffmpeg','ffprobe']:
        if not shutil.which(executable):raise SystemExit(f'Missing installed tool: {executable}')
    if not CHROME.is_file():raise SystemExit('Installed Chrome executable not found.')
    OUT.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='dalek-video-') as temporary:
        directory=Path(temporary).resolve()
        if not directory.is_relative_to(Path(tempfile.gettempdir()).resolve()):raise RuntimeError('Unexpected temporary directory')
        scene,inputs=export_scene(directory)
        story=scene['storyboard']
        assert story['total_seconds']==DURATION
        audio=args.audio
        if not args.preview and audio is None:
            audio=directory/'soundtrack.wav'
            subprocess.run(['powershell','-NoProfile','-ExecutionPolicy','Bypass','-File',str(ROOT/'scripts/build_video_audio.ps1'),'-OutputPath',str(audio)],check=True,timeout=120)
        server=ThreadingHTTPServer(('127.0.0.1',0),partial(RenderHandler,directory=str(directory)))
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        encoder=None;frames=0;began=time.monotonic();evidence=[]
        try:
            with sync_playwright() as playwright:
                browser=playwright.chromium.launch(executable_path=str(CHROME),headless=True)
                try:
                    page=browser.new_page(viewport={'width':WIDTH,'height':HEIGHT},device_scale_factor=1)
                    page.set_default_timeout(30000)
                    page.goto(f'http://127.0.0.1:{server.server_port}/',wait_until='load')
                    page.wait_for_function('window.ready===true||Boolean(window.renderError)')
                    error=page.evaluate('window.renderError||null')
                    if error:raise RuntimeError(error)
                    renderer=page.evaluate('''() => {const c=document.createElement('canvas'),g=c.getContext('webgl2'),e=g.getExtension('WEBGL_debug_renderer_info');return e?g.getParameter(e.UNMASKED_RENDERER_WEBGL):g.getParameter(g.RENDERER);}''')
                    if args.preview:
                        review=OUT/'review';review.mkdir(exist_ok=True)
                        for seconds in KEYFRAMES:
                            jpeg=base64.b64decode(page.evaluate('t=>renderFrame(t)',seconds))
                            Image.open(io.BytesIO(jpeg)).save(review/f'frame-{seconds:06.1f}.png')
                            evidence.append(page.evaluate('t=>frameEvidence(t)',seconds))
                            print(f'PREVIEW {seconds:.1f}s',flush=True)
                        (review/'motion-checks.json').write_text(json.dumps(evidence,indent=2)+'\n')
                    else:
                        if audio is None or not audio.is_file():raise RuntimeError('Soundtrack missing')
                        video=OUT/'dalek-assembly-and-operation.mp4'
                        log=directory/'ffmpeg.log'
                        with log.open('wb') as errors:
                            command=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','image2pipe','-framerate',str(FPS),'-vcodec','mjpeg','-i','pipe:0','-i',str(audio),'-map','0:v:0','-map','1:a:0','-c:v','libx264','-preset','fast','-crf','20','-pix_fmt','yuv420p','-r',str(FPS),'-c:a','aac','-b:a','160k','-t',str(DURATION),'-movflags','+faststart','-metadata','title=Dalek ROUND-9 assembly and simulated operation',str(video)]
                            encoder=subprocess.Popen(command,stdin=subprocess.PIPE,stderr=errors)
                            print(f'RENDER encoder PID {encoder.pid}; {DURATION*FPS} frames; {renderer}',flush=True)
                            for frame in range(DURATION*FPS):
                                if time.monotonic()-began>1200:raise TimeoutError('Render exceeded 20 minutes')
                                if encoder.poll() is not None:raise RuntimeError('Encoder exited early: '+log.read_text(errors='replace'))
                                seconds=frame/FPS
                                jpeg=base64.b64decode(page.evaluate('t=>renderFrame(t)',seconds))
                                encoder.stdin.write(jpeg);frames+=1
                                if frame in [int(v*FPS) for v in KEYFRAMES]:
                                    evidence.append(page.evaluate('t=>frameEvidence(t)',seconds))
                                if frame==int(119*FPS):Image.open(io.BytesIO(jpeg)).save(OUT/'video-poster.png')
                                if frame%(FPS*5)==0:print(f'FRAME {frame}/{DURATION*FPS} | time {seconds:.1f}s | elapsed {time.monotonic()-began:.1f}s',flush=True)
                            encoder.stdin.close()
                            if encoder.wait(timeout=120)!=0:raise RuntimeError(log.read_text(errors='replace'))
                            encoder=None
                finally:
                    browser.close()
        finally:
            if encoder is not None and encoder.poll() is None:
                encoder.terminate();encoder.wait(timeout=30)
            server.shutdown();server.server_close();thread.join(timeout=5)
        assert all(sha(ROOT/path)==value for path,value in inputs.items())
        final_state=evidence[-1]
        assert len(final_state['printed_instances'])==10
        assert set(final_state['printed_instances'])==set(NAMES)
        assert final_state['printed_instances'].count('07_pitch_carrier')==2
        assert final_state['drive']['action']=='STOPPED' and not final_state['motion']['active']
        assert next(e for e in evidence if abs(e['time']-111.1)<.03)['drive']['action']=='PAUSE'
        if args.preview:
            print('PASS: preview frames and unchanged CAD/STL/firmware/audio inputs',flush=True);return
        probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(video)],text=True))
        v=next(s for s in probe['streams'] if s['codec_type']=='video');a=next(s for s in probe['streams'] if s['codec_type']=='audio')
        assert (v['width'],v['height'])==(WIDTH,HEIGHT) and v['codec_name']=='h264'
        assert int(v['nb_frames'])==DURATION*FPS and v['avg_frame_rate']=='24/1'
        assert abs(float(probe['format']['duration'])-DURATION)<.1 and a['codec_name']=='aac'
        subprocess.run(['ffmpeg','-v','error','-i',str(video),'-f','null','-'],check=True,timeout=120)
        subtitles=[]
        for index,chapter in enumerate(story['chapters'],1):
            subtitles.append(f"{index}\n{timestamp(chapter['start'])} --> {timestamp(chapter['end'])}\n{chapter['title']}\n{chapter['instruction']}\n")
        (OUT/'assembly-captions.srt').write_text('\n'.join(subtitles),encoding='utf-8')
        manifest={'design_revision':'ROUND-9','type':'CAD animation and simulated operation, not physical footage','seconds':DURATION,'fps':FPS,
                  'frames':frames,'resolution':[WIDTH,HEIGHT],'video_codec':v['codec_name'],'audio_codec':a['codec_name'],
                  'printed_designs':9,'printed_instances':10,'source_sha256':inputs,'inputs_unchanged':True,
                  'video_sha256':sha(video),'video_bytes':video.stat().st_size,'render_seconds':round(time.monotonic()-began,2),
                  'renderer':renderer,'motion_keyframes':evidence,'audio_source':'Local Zira narration and existing original robot MP3s',
                  'verification':'FFprobe dimensions/rate/count/duration/audio checks and full FFmpeg decode passed',
                  'limitations':['Purchased hardware is simplified.','Assembly motions and speeds are illustrative.','No physical strength, fit, Wi-Fi connection or driving test is depicted.']}
        (OUT/'video-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
        print(f'PASS: {DURATION}s / {DURATION*FPS} frames / 1920x1080 H.264 + AAC; full decode; unchanged inputs',flush=True)
        print(video,flush=True)


if __name__=='__main__':run()
