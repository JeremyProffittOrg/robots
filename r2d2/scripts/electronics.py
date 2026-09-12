"""Single wiring schedule and readable, named-net circuit sheets."""
from pathlib import Path
import csv, html
ROOT=Path(__file__).resolve().parents[1]
rows=[]
def wire(net,source,target,gauge='26',note=''):
 rows.append(dict(net=net,source=source,target=target,awg=gauge,note=note))
def write_csv(path,items):
 with path.open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=items[0]);w.writeheader();w.writerows(items)

def power_overview():
 svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="880" viewBox="0 0 1400 880"><rect width="1400" height="880" fill="#ffffff"/>']
 def label(x,y,value,size=18,anchor='middle'):
  svg.append(f'<text x="{x}" y="{y}" font-family="sans-serif" font-size="{size}" text-anchor="{anchor}" fill="#142337">{html.escape(value)}</text>')
 def path(d):svg.append(f'<path d="{d}" fill="none" stroke="#173e73" stroke-width="3"/>')
 def box(x,y,w,h,lines):
  svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="5" fill="#e5effb" stroke="#173e73" stroke-width="2"/>')
  for i,line in enumerate(lines):label(x+w/2,y+23+i*24,line)
 label(30,38,'R2-24 | revision C power distribution',28,'start')
 label(30,70,'Architecture view. Follow wiring.csv and the connection sheets for exact pins, returns and capacitor polarity.',17,'start')
 path('M190 150 H240 M340 150 H390 M490 150 H600 M700 150 H740 V710 M520 150 V105 H760 V230 H790')
 box(20,105,170,90,['Protected B1','12 V / 6 Ah','LiFePO4'])
 box(240,115,100,70,['F1','7.5 A']);box(390,115,100,70,['S1','MAIN']);box(600,115,100,70,['S2','RUN'])
 branches=[
  (230,['F6 1 A + U6','5 V / 1.2 A logic'],['HUZZAH32 + audio + sensors','Removable J_USB power link']),
  (310,['F2 2 A + P1','5 V / 3 A LEFT'],['D1 DRV8833','M1 / M2 separate outputs']),
  (390,['F3 2 A + P2','5 V / 3 A RIGHT'],['D2 DRV8833','M3 / M4 separate outputs']),
  (470,['F4 2 A + P3','5 V / 3 A REAR'],['D3 DRV8833','M5 / M6 separate outputs']),
  (550,['F5 2 A + P4','5 V / 3 A steering'],['SV1 rear steering','U7 AHCT125 signal buffer']),
  (630,['F7 2 A + P5','5 V / 3 A HEAD'],['D4 DRV8833 channel A','M7 internal friction wheel']),
  (710,['F8 2 A + P6','Regulated 12 V post'],['INA219 > D5 DRV8871','P16 feedback actuator'])]
 for y,reg,load in branches:
  if y!=230:
   path(f'M740 {y} H790');svg.append(f'<circle cx="740" cy="{y}" r="4" fill="#173e73"/>')
  path(f'M1010 {y} H1080');box(790,y-30,220,60,reg);box(1080,y-30,300,60,load)
 svg.append('<circle cx="520" cy="150" r="4" fill="#173e73"/>')
 for i,line in enumerate(['Five UBEC positive outputs remain separate.','TT motors never connect to the 12 V post rail.','Seven DRV8833 channels retain nominal 1 A limits.','D5 uses replacement R1 = 71.5k.','NC limits independently gate post direction inputs.','Ground drive and head stop during posture changes.','Unplug the pack before charging or USB service.','Remove J_USB before connecting computer USB.']):label(35,295+i*49,line,18,'start')
 path('M105 195 V810 H1360')
 label(160,793,'GND: common battery, regulator, driver, controller and servo returns.',18,'start')
 label(30,858,'Fuses are on converter inputs. MAIN off removes all supply power. RUN off removes every motor and servo branch.',17,'start')
 svg.append('</svg>');(ROOT/'electronics/00-power-overview.svg').write_text('\n'.join(svg))
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
 for item in ['SV1 steering red','U7 AHCT125 pin14','CS 1000uF10V +','CB 100nF pin1','R_POWER_TOP 10k pin1']:
  wire('5V_SERVO','P4 UBEC OUT red',item,'22' if 'red' in item or '1000' in item else '26')
 for item in ['SV1 brown/black','U7 pin7','U7 pin1 / 1OE','U7 pin4 / 2OE','U7 pin10 / 3OE','U7 pin12 / 4A','CS -','CB pin2','R_POWER_BOTTOM 15k pin2']:
  wire('GND','B1 PP30 -',item,'22' if 'brown' in item else '26')
 for item in ['U7 pin13 / 4OE']:wire('5V_SERVO','P4 UBEC OUT red',item)
 for name,gpio,apin,ypin,servo in [('STEER',25,2,3,1)]:
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
 # Head friction motor has its own converter and current-limited bridge.
 wire('RUN+','S2 output','F7 2A input','18');wire('HEAD_BUCK_IN','F7 output','P5 UBEC IN red','22')
 wire('HEAD_BUCK_IN','F7 output','CI6 220uF25V +','22')
 for item in ['P5 IN black','P5 OUT black','CI6 -','CO5 -','D4 GND','D4 BIN1','D4 BIN2']:wire('GND','B1 PP30 -',item,'22')
 for item in ['D4 VMotor +','CO5 470uF10V +']:wire('5V_HEAD','P5 OUT red',item,'22')
 wire('ENABLE','U1 GPIO13','D4 SLP');wire('FAULT','U1 GPIO36 / A4','D4 FLT')
 for name,pin,inp in [('HEAD_FWD',26,'AIN1'),('HEAD_REV',17,'AIN2')]:
  wire(name,f'U1 GPIO{pin}',f'D4 {inp}');wire(name,f'U1 GPIO{pin}',f'R_{name} 10k pin1');wire('GND','B1 PP30 -',f'R_{name} pin2')
 for net,out,lead,cap in [('M7+','AOUT1','red','pin1'),('M7-','AOUT2','black','pin2')]:
  wire(net,f'D4 {out}',f'M7 {lead}','22');wire(net,f'M7 {lead}',f'CM7 100nF {cap}')
 # Regulated 12V actuator branch, measured on the supply side of D5.
 wire('RUN+','S2 output','F8 2A input','18');wire('POST_BUCK_IN','F8 output','P6 S13V25F12 VIN','22')
 wire('POST_BUCK_IN','F8 output','CI7 220uF25V +','22')
 wire('12V_POST_RAW','P6 VOUT','U10 INA219 VIN+','22');wire('12V_POST','U10 VIN-','D5 DRV8871 VM','22')
 wire('12V_POST','U10 VIN-','CO6 470uF25V +','22')
 for item in ['P6 GND','CI7 -','CO6 -','D5 GND','U10 GND','U9 ADS1115 GND','U9 ADDR','U10 A0','U10 A1','U9 AIN1','U9 AIN2','U9 AIN3']:
  wire('GND','B1 PP30 -',item,'22' if item.startswith(('P6','CI7','CO6','D5')) else '26')
 for name,pin,inp,apin,ypin,limit in [('POST_EXTEND',4,'IN1',5,6,'LS_EXT'),('POST_RETRACT',16,'IN2',9,8,'LS_RET')]:
  wire(name,f'U1 GPIO{pin}',f'U7 pin{apin}');wire(name,f'U1 GPIO{pin}',f'R_{name} 10k pin1');wire('GND','B1 PP30 -',f'R_{name} pin2')
  wire(name+'_5V',f'U7 pin{ypin}',f'{limit} COM');wire(name+'_LIMITED',f'{limit} NC',f'D5 {inp}')
  wire(name+'_LIMITED',f'D5 {inp}',f'R_{limit} 4.7k pin1');wire('GND','B1 PP30 -',f'R_{limit} pin2')
 wire('POST_RED','D5 OUT1','ACT red / pin3','22');wire('POST_BLACK','D5 OUT2','ACT black / pin4','22')
 wire('POST_ILIM','D5 ILIM / IC pin4','D5 replacement R1 71.5k pin2','26','Remove factory30k first; replace through provided resistor pads')
 wire('GND','B1 PP30 -','D5 replacement R1 pin1')
 wire('3V3','U1 3V','U9 VDD');wire('3V3','U1 3V','U10 VCC')
 wire('3V3','U1 3V','ACT yellow / pin5');wire('GND','B1 PP30 -','ACT orange / pin1')
 wire('POT_WIPER','ACT purple / pin2','R_POT 1k pin1');wire('POST_ADC','R_POT pin2','U9 AIN0')
 wire('POST_ADC','U9 AIN0','R_POT_FAIL 470k pin1');wire('GND','B1 PP30 -','R_POT_FAIL pin2')
 wire('POST_ADC','U9 AIN0','C_POT 100nF pin1');wire('GND','B1 PP30 -','C_POT pin2')
 for name,pin in [('SDA',21),('SCL',22)]:
  wire('I2C_'+name,f'U1 GPIO{pin}',f'U9 {name}');wire('I2C_'+name,f'U1 GPIO{pin}',f'U10 {name}')
 # Use the breakout's installed I2C pullups, both boards powered at3.3V.
 write_csv(ROOT/'electronics/wiring.csv',rows)
 # Each circuit sheet shows actual point-to-point connections; labels are net names.
 groups=[('01-power',rows[:27]),('02-drive',[r for r in rows if any(k in r['net'] for k in ['LEFT','RIGHT','REAR','ENABLE','FAULT']) or r['net'].startswith('M') and r['net'][1:2].isdigit()]),
 ('03-servo-and-sense',[r for r in rows if any(k in r['net'] for k in ['SERVO','STEER','HEAD','SENSE','ADC']) or any(k in r['target'] for k in ['U7','SV','R_POWER','R_PACK','CA ','CP '])]),
 ('04-logic-and-audio',[r for r in rows if any(k in r['net'] for k in ['LOGIC','I2S','GAIN','SPK']) or r['target'] in ['U1 GND','U8 GND','CO4 -','U6 GND','CI5 -']]),
 ('05-posture',[r for r in rows if any(k in r['net'] for k in ['POST','POT','I2C']) or any(k in r['target'] for k in ['U9','U10','ACT '])])]
 assigned=[r for _,rs in groups for r in rs]
 groups.append(('06-remaining-power-and-grounds',[r for r in rows if r not in assigned]))
 assert all(r in [item for _,rs in groups for item in rs] for r in rows)
 for p in (ROOT/'electronics').glob('0[1-6]-*.svg'):p.unlink()
 for name,rs in groups:
  # Split long sheets into readable 22-line circuit pages.
  for start in range(0,len(rs),22):
   items=rs[start:start+22];height=130+len(items)*38
   svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="{height}" viewBox="0 0 1100 {height}"><rect width="1100" height="{height}" fill="white"/>',f'<text x="30" y="34" font-family="sans-serif" font-size="22" fill="#122439">R2-24 circuit: {name[3:]} / {start//22+1}</text>', '<text x="30" y="65" font-family="sans-serif" font-size="14" fill="#374151">Each horizontal line is one connection. Identical named nets join across sheets. See wiring.csv for all grounds.</text>']
   for i,r in enumerate(items):
    y=100+i*38;escape=html.escape
    svg += [f'<text x="30" y="{y}" font-family="monospace" font-size="14" fill="#142337">{escape(r["source"])}</text>',f'<path d="M 365 {y-5} H 725" stroke="#163d72" stroke-width="2" fill="none"/>',f'<circle cx="365" cy="{y-5}" r="3" fill="#163d72"/><circle cx="725" cy="{y-5}" r="3" fill="#163d72"/>',f'<rect x="420" y="{y-17}" width="260" height="22" fill="white"/>',f'<text x="550" y="{y}" text-anchor="middle" font-family="monospace" font-size="13" fill="#163d72">{escape(r["net"])} ({r["awg"]} AWG)</text>',f'<text x="744" y="{y}" font-family="monospace" font-size="14" fill="#142337">{escape(r["target"])}</text>']
   svg.append('</svg>');(ROOT/'electronics'/f'{name}-{start//22+1}.svg').write_text('\n'.join(svg))
 power_overview()
 print(f'PASS: {len(rows)} wire connections; {sum((len(rs)+21)//22 for _,rs in groups)} connection sheets and one power overview')
if __name__=='__main__':main()
