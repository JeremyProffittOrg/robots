"""Revision D wiring schedule and named-net circuit sheets: DFRobot Romeo ESP32-S3 (DFR0994).

One row is one point-to-point connection. Identical net names join across sheets.
Board configuration that is not a wire (remove JP6 VIN/VM link, fit PMODE link for PH/EN,
replace R9/R10 for the lower DRV8876 trip) is stated on the power overview and in
docs/revision-d-controls.md.
"""
from pathlib import Path
import csv, html
ROOT=Path(__file__).resolve().parents[1]
rows=[]
GND='B1 PP30 -'
def wire(net,source,target,gauge='26',note=''):
 rows.append(dict(net=net,source=source,target=target,awg=gauge,note=note))
def write_csv(path,items):
 with path.open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=list(items[0]));w.writeheader();w.writerows(items)

def power_overview():
 svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="900" viewBox="0 0 1400 900"><rect width="1400" height="900" fill="#ffffff"/>']
 def label(x,y,value,size=18,anchor='middle'):
  svg.append(f'<text x="{x}" y="{y}" font-family="sans-serif" font-size="{size}" text-anchor="{anchor}" fill="#142337">{html.escape(value)}</text>')
 def path(d):svg.append(f'<path d="{d}" fill="none" stroke="#173e73" stroke-width="3"/>')
 def box(x,y,w,h,lines):
  svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="5" fill="#e5effb" stroke="#173e73" stroke-width="2"/>')
  for i,line in enumerate(lines):label(x+w/2,y+23+i*24,line)
 label(30,38,'R2-24 | revision D power distribution (DFRobot Romeo ESP32-S3 DFR0994)',28,'start')
 label(30,70,'Architecture view. Follow wiring.csv and the connection sheets for exact pins and returns.',17,'start')
 path('M190 150 H240 M340 150 H390 M490 150 H600 M700 150 H740 V470 M540 150 V250 H790')
 box(20,105,170,90,['Protected B1','12 V / 6 Ah','LiFePO4'])
 box(240,115,100,70,['F1','7.5 A']);box(390,115,100,70,['S1','MAIN']);box(600,115,100,70,['S2','RUN'])
 branches=[
  (250,['Romeo VIN (P23)','7-24 V, onboard 3 A fuse'],['ESP32-S3, 5 V/2 A logic rail','MAX98357A audio, 74AHCT125']),
  (360,['F2 5 A + P1 ICStation 11060','5.70 V motor rail (RUN)'],['Romeo VM (P22): four DRV8876','M1 left, M2 right, M3 centre, M4 head']),
  (470,['F3 2 A + P2 S13V25F12','12 V post rail (RUN)'],['D5 DRV8871, ILIM 71.5k','Actuonix P16-100-256-12-P'])]
 for y,reg,load in branches:
  if y!=250:
   path(f'M740 {y} H790');svg.append(f'<circle cx="740" cy="{y}" r="4" fill="#173e73"/>')
  path(f'M1030 {y} H1080');box(790,y-30,240,60,reg);box(1080,y-30,300,60,load)
 svg.append('<circle cx="540" cy="150" r="4" fill="#173e73"/>')
 label(1380,420,'5.70 V rail also feeds SV1 steering and SV2 lock-release MG995 power',15,'end')
 notes=['Remove the Romeo JP6 VIN/VM link: VIN stays on MAIN, VM only on RUN.',
  'Fit the PMODE link: DRV8876 PH/EN mode (EN = PWM, PH = direction).',
  'Replace R9 20k with 5.60k and R10 1k with 2.00k: pair trip 1.73 A, head 0.86 A.',
  'Romeo 5V_Servo is the 2 A logic buck; servos never draw from it.',
  'NC travel limits gate the 74AHCT125 enables; opening one disables that direction.',
  'Two SS-01GL lock switches separately sense engaged and fully withdrawn; each reads NO and NC.',
  'P16 pot on 3.3 V through 2.2k; open wiper or reference faults the stance.',
  'Ground drive runs only on three feet with the lock sensed seated.']
 for i,line in enumerate(notes):label(135,560+i*38,line,18,'start')
 path('M105 195 V870 H1360')
 label(160,862,'GND: common battery, regulator, driver, controller and servo returns at one distribution point.',17,'start')
 svg.append('</svg>');(ROOT/'electronics/00-power-overview.svg').write_text('\n'.join(svg),encoding='utf-8')

def main():
 (ROOT/'electronics').mkdir(exist_ok=True)
 # Main switch, fuse and Romeo logic input.
 wire('PACK+','B1 PP30 +','F1 7.5A input','18','Fuse within 100mm of pack plug')
 wire('FUSED+','F1 output','S1 MAIN input','18')
 wire('MAIN+','S1 output','S2 RUN input','18')
 wire('MAIN+','S1 output','U1 VIN+ / P23 pin1','20','Romeo logic input 7-24 V, onboard FUSE1 3 A; remove the JP6 VIN/VM link')
 wire('GND',GND,'U1 VIN- / P23 pin2','20')
 # RUN-switched 5.70 V motor rail for the four onboard DRV8876 channels and both servos.
 wire('RUN+','S2 output','F2 5A input','18')
 wire('MOTOR_BUCK_IN','F2 output','P1 ICStation 11060 IN+','18')
 wire('GND',GND,'P1 IN-','18')
 wire('5V7_MOTOR','P1 OUT+','U1 VM+ / P22 pin1','18','Set 5.70 V with a meter before connecting; accept 5.50-6.00 V at VM')
 wire('GND','P1 OUT-','U1 VM- / P22 pin2','18')
 # RUN-switched 12 V actuator rail.
 wire('RUN+','S2 output','F3 2A input','18')
 wire('POST_BUCK_IN','F3 output','P2 S13V25F12 VIN','20')
 wire('GND',GND,'P2 GND','20')
 wire('12V_POST','P2 VOUT','D5 DRV8871 VM','20')
 wire('GND',GND,'D5 GND','20')
 # Ground motors: each foot's two 3777 motors in parallel on one onboard channel; head on M4.
 for channel,(side,motors) in enumerate([('LEFT',(1,2)),('RIGHT',(3,4)),('CENTER',(5,6)),('HEAD',(7,))],1):
  for m in motors:
   note='Two motors in parallel on one channel' if len(motors)>1 and m==motors[0] else ''
   wire(f'{side}+',f'U1 M{channel} OUT1',f'M{m} red','22',note)
   wire(f'{side}-',f'U1 M{channel} OUT2',f'M{m} black','22')
 # Servo power from the motor rail; Romeo 5V_Servo is its 2 A logic buck.
 for sv,name in [(1,'steering'),(2,'lock release')]:
  wire('5V7_MOTOR','P1 OUT+',f'SV{sv} {name} red','22','MG995 4.8-7.2 V')
  wire('GND',GND,f'SV{sv} brown','22')
 # 74AHCT125 level shifter: 3.3 V GPIO to 5 V servo and DRV8871 inputs.
 wire('5V_LOGIC','U1 5V header','U7 74AHCT125 pin14 / VCC')
 wire('GND','U1 GND header','U7 pin7 / GND')
 wire('5V_LOGIC','U7 74AHCT125 pin14 / VCC','CB 100nF pin1','26','Bypass capacitor at the IC pins')
 wire('GND','U7 pin7 / GND','CB pin2')
 for net,gpio,a,y,target,pulldown in [('POST_EXTEND',38,'pin2 / 1A','pin3 / 1Y','D5 IN1','R_PD_EXT'),('POST_RETRACT',42,'pin5 / 2A','pin6 / 2Y','D5 IN2','R_PD_RET'),
                                      ('STEER',40,'pin9 / 3A','pin8 / 3Y','SV1 signal','R_PD_STEER'),('LOCK_SERVO',41,'pin12 / 4A','pin11 / 4Y','SV2 signal','R_PD_LOCK')]:
  wire(net,f'U1 GPIO{gpio}',f'U7 {a}')
  wire(net,f'U1 GPIO{gpio}',f'{pulldown} 10k pin1','26','Holds the gate input low through reset')
  wire('GND',GND,f'{pulldown} pin2')
  wire(net+'_5V',f'U7 {y}',target)
 for oe in ['pin10 / 3OE','pin13 / 4OE']:wire('GND',GND,f'U7 {oe}')
 # NC travel limits enable each actuator direction in hardware and are read by the MCU.
 for net,oe,limit,resistor,gpio in [('LIMIT_EXTEND','pin1 / 1OE','LS_EXT','R_LIM_EXT',7),('LIMIT_RETRACT','pin4 / 2OE','LS_RET','R_LIM_RET',8)]:
  wire(net,f'U7 {oe}',f'{limit} COM','26','Closed NC enables that direction; an open switch or wire disables it')
  wire('GND',GND,f'{limit} NC')
  wire(net,f'U7 {oe}',f'{resistor} 10k pin1')
  wire('3V3','U1 3V3 header',f'{resistor} pin2')
  wire(net,f'U7 {oe}',f'U1 GPIO{gpio}','26','HIGH = limit open')
 # DRV8871 current limit and the Actuonix P16 motor and potentiometer.
 wire('POST_ILIM','D5 ILIM','R_ILIM 71.5k pin2','26','Remove the factory 30k first; 0.82-0.98 A limit')
 wire('GND',GND,'R_ILIM pin1')
 wire('POST_RED','D5 OUT1','ACT red / pin3','22')
 wire('POST_BLACK','D5 OUT2','ACT black / pin4','22')
 wire('3V3','U1 3V3 header','R_POT_TOP 2.2k pin1')
 wire('POT_REF+','R_POT_TOP 2.2k pin2','ACT yellow / pin5','26','Keeps the full-stroke wiper below 3.0 V for pot tolerance +/-50%')
 wire('GND',GND,'ACT orange / pin1')
 wire('POST_ADC','ACT purple / pin2','U1 GPIO4')
 wire('POST_ADC','ACT purple / pin2','R_POT_FAIL 470k pin1','26','Open wiper reads 0 mV: feedback fault')
 wire('GND',GND,'R_POT_FAIL pin2')
 # Shoulder lock sensor: Omron SS-01GL, both contacts read.
 for switch,net,contacts in [('LS_LOCK','LOCK',[('NO',18),('NC',5)]),
                             ('LS_WITHDRAWN','WITHDRAWN',[('NO',43),('NC',44)])]:
  wire('GND',GND,f'{switch} SS-01GL COM','26','Independent GN817 endpoint: engaged or full6mm withdrawal')
  for contact,gpio in contacts:
   resistor=f'R_{net}_{contact}'
   wire(net+'_'+contact,f'{switch} {contact}',f'U1 GPIO{gpio}')
   wire(net+'_'+contact,f'{switch} {contact}',f'{resistor} 3.3k pin1','26','About1mA closed-contact current')
   wire('3V3','U1 3V3 header',f'{resistor} pin2')
 # RUN presence and battery voltage.
 wire('5V7_MOTOR','P1 OUT+','R_RUN_TOP 10k pin1')
 wire('RUN_SENSE','R_RUN_TOP 10k pin2','U1 GPIO39','26','5.5-6.0 V rail gives 2.75-3.00 V')
 wire('RUN_SENSE','R_RUN_TOP 10k pin2','R_RUN_BOTTOM 10k pin1')
 wire('GND',GND,'R_RUN_BOTTOM pin2')
 wire('MAIN+','S1 output','R_PACK_TOP 100k pin1')
 wire('PACK_ADC','R_PACK_TOP 100k pin2','U1 GPIO6','26','14.6 V pack gives 2.63 V')
 wire('PACK_ADC','R_PACK_TOP 100k pin2','R_PACK_BOTTOM 22k pin1')
 wire('GND',GND,'R_PACK_BOTTOM pin2')
 # Audio.
 wire('5V_LOGIC','U1 5V header','U8 MAX98357A VIN','22')
 wire('GND','U1 GND header','U8 GND','22')
 for gpio,pin in [(15,'BCLK'),(16,'LRC'),(17,'DIN')]:wire('I2S_'+pin,f'U1 GPIO{gpio}',f'U8 {pin}')
 wire('SPK+','U8 speaker +','SP1 +','22')
 wire('SPK-','U8 speaker -','SP1 -','22','Neither speaker wire connects to GND; GAIN pin open (9 dB)')
 wire('GND',GND,'U1 GND header','20','Common ground point for logic-level returns')
 write_csv(ROOT/'electronics/wiring.csv',rows)

 rules=[('01-power',lambda r:r['net'] in ('PACK+','FUSED+','MAIN+','RUN+','MOTOR_BUCK_IN','POST_BUCK_IN','12V_POST') or any(k in r['target'] for k in ['VIN','VM','P1 ','P2 ','D5 GND'])),
  ('02-drive',lambda r:r['net'].rstrip('+-') in ('LEFT','RIGHT','CENTER','HEAD')),
  ('03-buffer-and-servos',lambda r:'U7' in r['source']+r['target'] or 'SV' in r['target'] or 'R_PD' in r['target']),
  ('04-stance-actuator-and-lock',lambda r:any(k in r['source']+r['target'] for k in ['ACT','LS_','R_POT','R_ILIM','R_LIM','R_LOCK','D5'])),
  ('05-logic-and-audio',lambda r:r['net'] in ('5V_LOGIC','SPK+','SPK-') or r['net'].startswith('I2S') or 'U8' in r['target'])]
 groups={name:[] for name,_ in rules};groups['06-sense-and-grounds']=[]
 for r in rows:
  for name,rule in rules:
   if rule(r):groups[name].append(r);break
  else:groups['06-sense-and-grounds'].append(r)
 assert sum(len(v) for v in groups.values())==len(rows)
 for p in (ROOT/'electronics').glob('0[1-6]-*.svg'):p.unlink()
 sheets=0
 for name,rs in groups.items():
  # Split long sheets into readable 22-line circuit pages.
  for start in range(0,len(rs),22):
   items=rs[start:start+22];height=130+len(items)*38;sheets+=1
   svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="{height}" viewBox="0 0 1100 {height}"><rect width="1100" height="{height}" fill="white"/>',f'<text x="30" y="34" font-family="sans-serif" font-size="22" fill="#122439">R2-24 revision D circuit: {name[3:]} / {start//22+1}</text>', '<text x="30" y="65" font-family="sans-serif" font-size="14" fill="#374151">Each horizontal line is one connection. Identical named nets join across sheets. See wiring.csv for notes.</text>']
   for i,r in enumerate(items):
    y=100+i*38;escape=html.escape
    svg += [f'<text x="30" y="{y}" font-family="monospace" font-size="14" fill="#142337">{escape(r["source"])}</text>',f'<path d="M 365 {y-5} H 725" stroke="#163d72" stroke-width="2" fill="none"/>',f'<circle cx="365" cy="{y-5}" r="3" fill="#163d72"/><circle cx="725" cy="{y-5}" r="3" fill="#163d72"/>',f'<rect x="420" y="{y-17}" width="260" height="22" fill="white"/>',f'<text x="550" y="{y}" text-anchor="middle" font-family="monospace" font-size="13" fill="#163d72">{escape(r["net"])} ({r["awg"]} AWG)</text>',f'<text x="744" y="{y}" font-family="monospace" font-size="14" fill="#142337">{escape(r["target"])}</text>']
   svg.append('</svg>');(ROOT/'electronics'/f'{name}-{start//22+1}.svg').write_text('\n'.join(svg),encoding='utf-8')
 power_overview()
 print(f'PASS: {len(rows)} wire connections; {sheets} connection sheets and one power overview')
if __name__=='__main__':main()
