"""Render the actual CAD poses, then encode a labelled MP4. No hardware footage."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse, hashlib, json, math, subprocess, tempfile
from PIL import Image, ImageDraw, ImageFont
from export_cad import ROOT, EXE

FPS=12
SECONDS=30
OUT=ROOT/'output/delivery'
SMIN=5.03832
SMAX=72
FONT='C:/Windows/Fonts/arial.ttf'

def smooth(x):return (1-math.cos(math.pi*min(1,max(0,x))))/2
def scene(t):
    if t<6:
        return 'assembly',SMIN,120*math.sin(t*math.pi/6),(1000,1600,900,0,-40,305),'Detailed shell and powered head','Two whole body prints; one print per side leg.'
    if t<14:
        return 'assembly',SMIN+(SMAX-SMIN)*smooth((t-6)/8),0,(1100,-1600,950,0,-50,305),'Rear post extends; body tilts','Supported three-foot motion. Timing is illustrative.'
    if t<22:
        return 'section',SMAX-(SMAX-SMIN)*smooth((t-14)/8),0,(1100,-1600,950,0,-50,305),'Metal frame and rear guide exposed','12 mm shoulder shafts; separate actuator and sliding guide.'
    if t<26:
        return 'exploded',SMIN,0,(1300,1800,1200,0,-40,365),'Printed covers separated for assembly','10 STL designs / 14 printed pieces. Metal frame stays assembled.'
    return 'assembly',SMIN,90*math.sin((t-26)*math.pi/4),(1000,1600,900,0,-40,305),'R2-24 | revision C','609.6 mm nominal height; twelve ground wheels; phone Wi-Fi.'

def frame(index,tmp):
    t=index/FPS;part,stroke,head,camera,title,caption=scene(t)
    camera=tuple(camera[i+3]+1.2*(camera[i]-camera[i+3]) for i in range(3))+camera[3:]
    raw=tmp/f'raw-{index:04}.png';dest=tmp/f'frame-{index:04}.png'
    args=[EXE,'-o',str(raw),'--imgsize=1920,1080','--colorscheme=Tomorrow','--projection=o',
          '--camera='+','.join(map(str,camera)),'-D',f'part="{part}"','-D',f'stroke={stroke:.8f}',
          '-D',f'head_angle={head:.6f}',str(ROOT/'cad/r2d2.scad')]
    r=subprocess.run(args,capture_output=True,text=True,timeout=90)
    if r.returncode or 'ERROR:' in r.stderr or 'WARNING:' in r.stderr:raise RuntimeError(f'Frame {index}: {r.stderr}')
    im=Image.open(raw).convert('RGB');draw=ImageDraw.Draw(im)
    draw.rectangle((0,0,1920,122),fill='#ffffff')
    draw.text((48,23),title,font=ImageFont.truetype(FONT,37),fill='#133858')
    draw.text((50,75),caption,font=ImageFont.truetype(FONT,25),fill='#40556a')
    draw.rectangle((0,998,1920,1080),fill='#0f172a')
    draw.text((48,1010),'CAD SIMULATION — NOT A HARDWARE TEST',font=ImageFont.truetype(FONT,27),fill='#ffffff')
    draw.text((48,1048),'Purchased components are dimensional envelopes. Motion timing is not a measured speed.',font=ImageFont.truetype(FONT,19),fill='#e2e8f0')
    im.save(dest);raw.unlink()
    return index

def main():
    p=argparse.ArgumentParser();p.add_argument('--preview',action='store_true');a=p.parse_args()
    OUT.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='r2-video-') as name:
        tmp=Path(name);indices=[0,120,210,285] if a.preview else list(range(FPS*SECONDS))
        with ThreadPoolExecutor(max_workers=4) as pool:
            for done,f in enumerate(as_completed([pool.submit(frame,i,tmp) for i in indices]),1):
                f.result()
                if done%12==0 or done==len(indices):print(f'Rendered {done}/{len(indices)} CAD frames',flush=True)
        if a.preview:
            sheet=Image.new('RGB',(1920,1080),'white')
            for n,i in enumerate(indices):
                with Image.open(tmp/f'frame-{i:04}.png') as im:sheet.paste(im.resize((960,540)),((n%2)*960,(n//2)*540))
            sheet.save(ROOT/'tmp/reference/video-preview.png');return
        result=subprocess.run(['ffmpeg','-y','-v','error','-framerate',str(FPS),'-i',str(tmp/'frame-%04d.png'),
                               '-c:v','libx264','-preset','medium','-crf','19','-pix_fmt','yuv420p','-r','24','-movflags','+faststart',str(OUT/'motion.mp4')],capture_output=True,text=True,timeout=180)
        if result.returncode:raise RuntimeError(result.stderr)
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(OUT/'motion.mp4')]))
    v=next(s for s in probe['streams'] if s['codec_type']=='video')
    assert v['width']==1920 and v['height']==1080 and abs(float(probe['format']['duration'])-SECONDS)<.1
    subprocess.run(['ffmpeg','-v','error','-i',str(OUT/'motion.mp4'),'-f','null','-'],check=True,timeout=120)
    report={'simulation':True,'physical_test':False,'duration_s':SECONDS,'width':1920,'height':1080,'fps':24,
            'rendered_frames':FPS*SECONDS,'sha256':hashlib.sha256((OUT/'motion.mp4').read_bytes()).hexdigest(),
            'source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'cad').glob('*.scad'))}}
    (OUT/'video.json').write_text(json.dumps(report,indent=2))
    print(f'PASS: {SECONDS}s 1920x1080 MP4; full decode; current CAD source hashes recorded')

if __name__=='__main__':main()
