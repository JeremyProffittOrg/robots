"""Single wiring schedule and readable, named-net circuit sheets."""
from pathlib import Path
import csv, html
ROOT=Path(__file__).resolve().parents[1]
rows=[]
def wire(net,source,target,gauge='26',note=''):
 rows.append(dict(net=net,source=source,target=target,awg=gauge,note=note))
def write_csv(path,items):
 with path.open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=items[0]);w.writeheader();w.writerows(items)
def main():
 for d in ['electronics','bom']:(ROOT/d).mkdir(exist_ok=True)
 wire('PACK+', 'B1 PP30 +','F1 7.5A input','18','Fuse within 100mm of pack plug')
 wire('FUSED+', 'F1 output','S1 MAIN input','18');wire('MAIN+', 'S1 output','S2 RUN input','18')
 wire('MAIN+','S1 output','F6 1A input','22');wire('LOGIC_IN','F6 output','U6 MPM3610 VIN','22')
 for i in range(1,5):
  wire('RUN+','S2 output',f'F{i+1} 2A input','18')
  wire(f'BUCK{i}_IN',f'F{i+1} output',f'P{i} UBEC IN red','22')
  wire(f'BUCK{i}_IN',f'F{i+1} output',f'CI{i} 220uF25V +','22')
  wire('GND','B1 PP30 -',f'P{i} UBEC IN black','18')
  wire('GND','B1 PP30 -',f'P{i} UBEC OUT black','18')
  wire('GND','B1 PP30 -',f'CI{i} -','22')
 for i,side in enumerate(['LEFT','RIGHT','REAR'],1):
  rail=f'5V_{side}'
  wire(rail,f'P{i} UBEC OUT red',f'D{i} DRV8833 VMotor +','22','Never parallel regulator outputs')
  wire(rail,f'P{i} UBEC OUT red',f'CO{i} 470uF10V +','22')
  wire('GND','B1 PP30 -',f'D{i} GND','22');wire('GND','B1 PP30 -',f'CO{i} -','22')
  gpios=[(14,32),(15,33),(27,12)][i-1]
  for direction,pin,suffix in [('FWD',gpios[0],'1'),('REV',gpios[1],'2')]:
   for channel in ['A','B']:wire(f'{side}_{direction}',f'U1 GPIO{pin}',f'D{i} {channel}IN{suffix}')
   wire(f'{side}_{direction}',f'U1 GPIO{pin}',f'R_{side}_{direction} 10k pin1')
   wire('GND','B1 PP30 -',f'R_{side}_{direction} pin2')
  wire('ENABLE','U1 GPIO13',f'D{i} SLP');wire('FAULT','U1 GPIO36 / A4',f'D{i} FLT')
  for j,channel in enumerate(['A','B']):
   motor=(i-1)*2+j+1
   wire(f'M{motor}+ ',f'D{i} {channel}OUT1',f'M{motor} red','22')
   wire(f'M{motor}- ',f'D{i} {channel}OUT2',f'M{motor} black','22')
   wire(f'M{motor}+ ',f'M{motor} red',f'CM{motor} 100nF pin1','26','Capacitor directly across motor tabs')
   wire(f'M{motor}- ',f'M{motor} black',f'CM{motor} pin2','26')
 wire('ENABLE','U1 GPIO13','R_ENABLE 10k pin1');wire('GND','B1 PP30 -','R_ENABLE pin2')
 wire('FAULT','U1 GPIO36 / A4','R_FAULT 10k pin1');wire('3V3','U1 3V','R_FAULT pin2')
 for item in ['SV1 steering red','SV2 head red','U7 AHCT125 pin14','CS 1000uF10V +','CB 100nF pin1','R_POWER_TOP 10k pin1']:
  wire('5V_SERVO','P4 UBEC OUT red',item,'22' if 'red' in item or '1000' in item else '26')
 for item in ['SV1 brown/black','SV2 brown/black','U7 pin7','U7 pin1 / 1OE','U7 pin4 / 2OE','U7 pin9 / 3A','U7 pin12 / 4A','CS -','CB pin2','R_POWER_BOTTOM 15k pin2']:
  wire('GND','B1 PP30 -',item,'22' if 'brown' in item else '26')
 for item in ['U7 pin10 / 3OE','U7 pin13 / 4OE']:wire('5V_SERVO','P4 UBEC OUT red',item)
 for name,gpio,apin,ypin,servo in [('STEER',25,2,3,1),('HEAD',26,5,6,2)]:
  wire(name,f'U1 GPIO{gpio}',f'U7 pin{apin}');wire(name,f'U1 GPIO{gpio}',f'R_{name} 10k pin1');wire('GND','B1 PP30 -',f'R_{name} pin2')
  wire(name+'_5V',f'U7 pin{ypin}',f'RS{servo} 220ohm pin1');wire(name+'_SIG',f'RS{servo} pin2',f'SV{servo} signal')
 wire('RUN_SENSE','R_POWER_TOP pin2','U1 GPIO39 / A3');wire('RUN_SENSE','R_POWER_TOP pin2','R_POWER_BOTTOM pin1');wire('RUN_SENSE','R_POWER_TOP pin2','CP 100nF pin1');wire('GND','B1 PP30 -','CP pin2')
 wire('MAIN+','S1 output','R_PACK_TOP 100k pin1');wire('PACK_ADC','R_PACK_TOP pin2','U1 GPIO34 / A2');wire('PACK_ADC','R_PACK_TOP pin2','R_PACK_BOTTOM 22k pin1');wire('PACK_ADC','R_PACK_TOP pin2','CA 100nF pin1');wire('GND','B1 PP30 -','R_PACK_BOTTOM pin2');wire('GND','B1 PP30 -','CA pin2')
 wire('LOGIC_IN','F6 output','CI5 100uF25V +','22');wire('GND','B1 PP30 -','CI5 -','22');wire('GND','B1 PP30 -','U6 GND','22')
 wire('5V_LOGIC','U6 5V OUT','J_USB removable link input','22');wire('5V_LOGIC_USB','J_USB output','U1 USB pin','22','REMOVE LINK before plugging computer USB; BAT/JST remain empty')
 for item in ['U8 MAX98357A VIN','CO4 470uF10V +','R_GAIN 100k pin1']:wire('5V_LOGIC','U6 5V OUT',item,'22')
 for item in ['U1 GND','U8 GND','CO4 -']:wire('GND','B1 PP30 -',item,'22')
 for pin,target in [(18,'BCLK'),(19,'LRC'),(23,'DIN')]:wire('I2S_'+target,f'U1 GPIO{pin}',f'U8 {target}')
 wire('GAIN','R_GAIN pin2','U8 GAIN');wire('SPK+','U8 speaker +','SP1 +','22');wire('SPK-','U8 speaker -','SP1 -','22','Neither speaker wire connects to GND')
 write_csv(ROOT/'electronics/wiring.csv',rows)
 # Each circuit sheet shows actual point-to-point connections; labels are net names.
 groups=[('01-power',rows[:27]),('02-drive',[r for r in rows if any(k in r['net'] for k in ['LEFT','RIGHT','REAR','ENABLE','FAULT']) or r['net'].startswith('M') and r['net'][1:2].isdigit()]),
 ('03-servo-and-sense',[r for r in rows if any(k in r['net'] for k in ['SERVO','STEER','HEAD','SENSE','ADC']) or any(k in r['target'] for k in ['U7','SV','R_POWER','R_PACK','CA ','CP '])]),
 ('04-logic-and-audio',[r for r in rows if any(k in r['net'] for k in ['LOGIC','I2S','GAIN','SPK']) or r['target'] in ['U1 GND','U8 GND','CO4 -','U6 GND','CI5 -']])]
 for name,rs in groups:
  # Split long sheets into readable 22-line circuit pages.
  for start in range(0,len(rs),22):
   items=rs[start:start+22];height=130+len(items)*38
   svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="{height}" viewBox="0 0 1100 {height}"><rect width="1100" height="{height}" fill="white"/>',f'<text x="30" y="34" font-family="sans-serif" font-size="22" fill="#122439">R2-24 circuit: {name[3:]} / {start//22+1}</text>', '<text x="30" y="65" font-family="sans-serif" font-size="14" fill="#374151">Each horizontal line is one connection. Identical named nets join across sheets. See wiring.csv for all grounds.</text>']
   for i,r in enumerate(items):
    y=100+i*38;escape=html.escape
    svg += [f'<text x="30" y="{y}" font-family="monospace" font-size="14" fill="#142337">{escape(r["source"])}</text>',f'<path d="M 365 {y-5} H 725" stroke="#163d72" stroke-width="2" fill="none"/>',f'<circle cx="365" cy="{y-5}" r="3" fill="#163d72"/><circle cx="725" cy="{y-5}" r="3" fill="#163d72"/>',f'<rect x="420" y="{y-17}" width="260" height="22" fill="white"/>',f'<text x="550" y="{y}" text-anchor="middle" font-family="monospace" font-size="13" fill="#163d72">{escape(r["net"])} ({r["awg"]} AWG)</text>',f'<text x="744" y="{y}" font-family="monospace" font-size="14" fill="#142337">{escape(r["target"])}</text>']
   svg.append('</svg>');(ROOT/'electronics'/f'{name}-{start//22+1}.svg').write_text('\n'.join(svg))
 print(f'PASS: {len(rows)} wire connections and {sum((len(rs)+21)//22 for _,rs in groups)} circuit sheets written')
if __name__=='__main__':main()
