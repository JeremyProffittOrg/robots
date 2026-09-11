"""Deterministic original droid chirps; no sampled film audio."""
from pathlib import Path
import csv, hashlib, math, subprocess, tempfile, wave
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
NAMES=['Hello','Curious','Happy','Concerned','Agree','Disagree','Excited','Sleepy','Thinking','Surprised','Searching','Playful','Low energy','Ready','Goodbye','Long story']
def synth(index):
 rng=np.random.default_rng(2400+index);sr=22050;chunks=[np.zeros(int(.1*sr))]
 count=4+index%5 if index!=15 else 18
 for j in range(count):
  duration=float(rng.uniform(.12,.42));t=np.arange(int(duration*sr))/sr
  base=float(rng.uniform(280,1600));end=base*float(rng.uniform(.6,1.8))
  if index in [3,5,7,12,14]:end=base*.55
  frequency=base+(end-base)*t/duration+35*np.sin(2*np.pi*(9+j)*t)
  phase=np.cumsum(frequency)*2*np.pi/sr
  signal=np.sin(phase+1.5*np.sin(phase*.503))+.17*np.sin(phase*2.01)
  envelope=np.minimum(t/.012,1)*np.minimum((duration-t)/.04,1)
  signal*=envelope*(.8+.2*np.sin(2*np.pi*16*t))
  chunks.extend([signal,np.zeros(int(sr*rng.uniform(.045,.15)))])
 sound=np.concatenate(chunks);return (sound/max(abs(sound))*.72*32767).astype('<i2')
def main():
 dest=ROOT/'firmware/data/audio';dest.mkdir(parents=True,exist_ok=True);(ROOT/'audio').mkdir(exist_ok=True)
 rows=[]
 with tempfile.TemporaryDirectory(prefix='r2-sounds-') as temp:
  for i,name in enumerate(NAMES):
   samples=synth(i);wav=Path(temp)/'sound.wav';mp3=dest/f'{i+1:02d}.mp3'
   with wave.open(str(wav),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(22050);w.writeframes(samples.tobytes())
   subprocess.run(['ffmpeg','-v','error','-y','-i',str(wav),'-codec:a','libmp3lame','-b:a','64k','-ar','22050','-ac','1','-map_metadata','-1',str(mp3)],check=True,timeout=30)
   subprocess.run(['ffmpeg','-v','error','-i',str(mp3),'-f','null','-'],check=True,timeout=30)
   rows.append(dict(id=i+1,name=name,path='firmware/data/audio/'+mp3.name,duration_seconds=round(len(samples)/22050,3),sha256=hashlib.sha256(mp3.read_bytes()).hexdigest()))
 with (ROOT/'audio/catalog.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
 print(f'PASS: {len(rows)} original MP3s generated and decoded; {sum(r["duration_seconds"] for r in rows):.1f} seconds')
if __name__=='__main__':main()
