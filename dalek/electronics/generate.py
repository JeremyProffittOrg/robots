"""Generate the Dalek harness, circuit sheets, and design calculations. No dependencies."""
from pathlib import Path
import csv
import json
import math
import xml.etree.ElementTree as ET
from html import escape

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
ROWS = []

def wire(net, origin, destination, gauge="26", color="signal", note=""):
    ROWS.append(dict(net=net, origin=origin, destination=destination,
                     wire_awg=gauge, color=color, note=note))

def link(net, *pins, gauge="26", color="signal", note=""):
    for pin in pins[1:]:
        wire(net, pins[0], pin, gauge, color, note)

def passive(ref, value, net1, net2):
    wire(net1, net1, ref + ".1", "component", "", value)
    wire(net2, net2, ref + ".2", "component", "", value)

link("BAT_POS", "B1.PP30+", "F1.IN", gauge="18", color="red", note="7.5A fuse within 100mm of pack")
link("BAT_FUSED", "F1.OUT", "S1.1", gauge="18", color="red")
link("PACK_SW", "S1.3", "S2.1", "F4.IN", "R10.1", gauge="18", color="red", note="NKK S1A ON connects terminals1 and3")
link("ACT_IN", "S2.3", "F2.IN", "F3.IN", gauge="18", color="orange", note="Physical actuator power disconnect; logic stays powered")
link("MOTOR_IN", "F2.OUT", "U2.VIN", gauge="18", color="orange", note="F2 3A")
link("SERVO_IN", "F3.OUT", "U3.VIN", gauge="18", color="orange", note="F3 3A")
link("LOGIC_IN", "F4.OUT", "U4.IN", gauge="22", color="red", note="F4 1A")
link("5V_MOTOR", "U2.VOUT", "U5.VMotor", "U6.VMotor", "U11.VMotor", "U9.14", "R12.1", gauge="18", color="orange")
link("5V_SERVO", "U3.VOUT", "J_SERVO.2", "U8.14", gauge="18", color="red", note="Four separate arm-servo branches; never feed through PCA9685 V+ traces")
link("5V_LOGIC", "U4.OUT", "J_USB_ISO.1", "U7.VIN", "R14.1", gauge="22", color="red")
link("ESP_5V", "J_USB_ISO.2", "U1.5V", gauge="22", color="red", note="Removable run-power link; OPEN and unplug battery before USB")
link("3V3", "U1.3V3", "U10.VCC", "R6.1", gauge="26", color="red")
link("GND", "B1.PP30-", "U2.GND", "U3.GND", "U4.GND", "U5.GND", "U6.GND", "U11.GND", "J_SERVO.1", gauge="18", color="black", note="Star ground; power returns do not pass through ESP32 or PCA board")
link("GND", "GROUND_STAR", "U1.GND", "U7.GND", "U8.7", "U9.7", "U10.GND", gauge="22", color="black")
wire("GND", "B1.PP30-", "GROUND_STAR", "18", "black")
for gpio, net, pins in [(25,"LEFT_IN1",["U5.AIN1","U5.BIN1"]),
                        (26,"LEFT_IN2",["U5.AIN2","U5.BIN2"]),
                        (32,"RIGHT_IN1",["U6.AIN1","U6.BIN1"]),
                        (33,"RIGHT_IN2",["U6.AIN2","U6.BIN2"])]:
    link(net, f"U1.GPIO{gpio}", *pins)
for i, net in enumerate(["LEFT_IN1","LEFT_IN2","RIGHT_IN1","RIGHT_IN2","MOTOR_ENABLE"],1):
    passive(f"R{i}","10k 1% 0.25W pull-down",net,"GND")
link("MOTOR_ENABLE", "U1.GPIO12", "U5.SLP", "U6.SLP", "U11.SLP")
link("SDA", "U1.GPIO21", "U10.SDA")
link("SCL", "U1.GPIO22", "U10.SCL")
link("SERVO_DISABLE", "U1.GPIO27", "U10.OE", "R6.2", "U8.1", "U8.4", "U8.10", "U8.13", note="R6 10k to3V3; REMOVE PCA board OE pull-down; U9 uses separate direction enables")
link("I2S_BCLK", "U1.GPIO17", "U7.BCLK")
link("I2S_LRC", "U1.GPIO13", "U7.LRC")
link("I2S_DATA", "U1.GPIO15", "U7.DIN", note="GPIO15 strap: amplifier INPUT only; no pull-up/down added")
link("BAT_ADC", "R10.2", "R11.1", "U1.GPIO39", "C10.1")
link("GND", "GROUND_STAR", "R11.2", "C10.2")
link("ACT_OK", "R12.2", "R13.1", "U1.GPIO36", "C11.1")
link("GND", "GROUND_STAR", "R13.2", "C11.2")
link("AMP_GAIN", "R14.2", "U7.GAIN", note="R14 100k to5V_LOGIC sets3dB")
link("SPK_P", "U7.OUT+", "SPK1.+", gauge="24", color="yellow", note="Floating bridge output; NEVER ground speaker leads")
link("SPK_N", "U7.OUT-", "SPK1.-", gauge="24", color="blue")
for side, driver in [("LEFT","U5"),("RIGHT","U6")]:
    for bridge, position in [("A","FRONT"),("B","REAR")]:
        for output, lead in [("OUT1","+"),("OUT2","-")]:
            net=f"{side}_{position}_{lead}"
            link(net, f"{driver}.{bridge}{output}", f"M_{side}_{position}.{lead}", gauge="22", color="yellow" if lead=="+" else "blue", note="Keep supplied 28AWG motor lead short; reverse both leads if forward test disagrees")
        passive(f"C_{side}_{position}","100nF ceramic >=25V across MOTOR tabs",f"{side}_{position}_+",f"{side}_{position}_-")
channels = [("LEFT_YAW","U8",2,3),("LEFT_PITCH","U8",5,6),
            ("RIGHT_YAW","U8",9,8),("RIGHT_PITCH","U8",12,11)]
for channel,(name,chip,a,y) in enumerate(channels):
    link(f"PWM{channel}",f"U10.PWM{channel}",f"{chip}.{a}")
    passive(f"R{20+channel}","10k pull-down at buffer input",f"PWM{channel}","GND")
    link(f"PWM5V_{channel}",f"{chip}.{y}",f"R{30+channel}.1")
    link(f"SERVO_{name}",f"R{30+channel}.2",f"SV{channel}.SIGNAL",note="220ohm series resistor")
    passive(f"R{40+channel}","10k pull-down at servo signal",f"SERVO_{name}","GND")
    wire("5V_SERVO","J_SERVO.2",f"SV{channel}.RED", "22", "red", "Individual branch; retain servo plug center positive")
    wire("GND","J_SERVO.1",f"SV{channel}.GND", "22", "black/brown")
link("HEAD_PWM", "U1.GPIO2", "U9.2", "U9.5", note="20kHz 8bit PWM; low before direction updates; cap100/255")
passive("R24", "10k pull-down: GPIO2 boot-safe and head PWM off on reset", "HEAD_PWM", "GND")
for pca, enable, output, ref, bridge in [(4,1,3,34,1),(5,4,6,35,2)]:
    net = f"HEAD_DISABLE{bridge}"
    link(net, f"U10.PWM{pca}", f"U9.{enable}", note="STATIC HIGH disables this gate; LOW enables; never servo pulses")
    passive(f"R{6+bridge}", "10k pull-up to3V3; AHCT TTL threshold", net, "3V3")
    link(f"HEAD_BUFFER{bridge}", f"U9.{output}", f"R{ref}.1")
    link(f"HEAD_IN{bridge}", f"R{ref}.2", f"U11.AIN{bridge}", note="220ohm series resistor; only one input gets PWM")
    passive(f"R{43+bridge}", "10k pull-down at driver input", f"HEAD_IN{bridge}", "GND")
link("GND", "GROUND_STAR", "U11.BIN1", "U11.BIN2", note="Unused bridge B inputs low; BOUT1/BOUT2 unconnected")
link("HEAD_MOTOR+", "U11.AOUT1", "M_HEAD.+", gauge="22", color="yellow")
link("HEAD_MOTOR-", "U11.AOUT2", "M_HEAD.-", gauge="22", color="blue")
passive("C_HEAD", "100nF ceramic >=25V across MOTOR tabs", "HEAD_MOTOR+", "HEAD_MOTOR-")
for pin in [9,12]:
    wire("GND","GROUND_STAR",f"U9.{pin}","26","black","Unused buffer INPUT tied low")
for pin in [10,13]:
    wire("5V_MOTOR","U2.VOUT",f"U9.{pin}","26","orange","Unused buffer OE high")
for ref,value,rail in [("C1","220uF 25V low-ESR","MOTOR_IN"),("C2","220uF 25V low-ESR","SERVO_IN"),
                       ("C3","100uF 25V","LOGIC_IN"),("C4","470uF 10V low-ESR","5V_MOTOR"),
                       ("C5","470uF 10V low-ESR","5V_MOTOR"),("C6","1000uF 10V low-ESR","5V_SERVO"),
                       ("C7","470uF 10V low-ESR","5V_LOGIC"),("C8","100nF ceramic","5V_SERVO"),("C9","100nF ceramic","5V_MOTOR"),
                       ("C12","470uF 10V low-ESR at head driver","5V_MOTOR")]:
    passive(ref,value,rail,"GND")
passive("R15","100ohm 1W discharge resistor","5V_MOTOR","GND")
passive("R16","100ohm 1W discharge resistor","5V_SERVO","GND")

class Sheet:
    def __init__(self,title,subtitle,w=1600,h=1100):
        self.w,self.h=w,h
        self.items=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
            '<style>text{font-family:Arial,sans-serif;fill:#10263a} .title{font-size:30px;font-weight:bold} .head{font-size:20px;font-weight:bold} .body{font-size:17px} .small{font-size:15px} .net{font-family:monospace;font-size:16px;fill:#004879} .wire{stroke:#155a85;stroke-width:2;fill:none}</style>',
            f'<rect width="{w}" height="{h}" fill="white"/>']
        self.text(35,45,title,"title");self.text(35,77,subtitle,"body")
    def text(self,x,y,t,cls="body"):
        sizes={"title":30,"head":20,"body":17,"small":15,"net":16}
        weight="bold" if cls in {"title","head"} else "normal"
        family="monospace" if cls=="net" else "Arial, sans-serif"
        fill="#004879" if cls=="net" else "#10263a"
        self.items.append(f'<text x="{x}" y="{y}" font-family="{family}" font-size="{sizes[cls]}" font-weight="{weight}" fill="{fill}">{escape(t)}</text>')
    def line(self,x1,y1,x2,y2):
        self.items.append(f'<path d="M{x1},{y1} L{x2},{y2}" stroke="#155a85" stroke-width="2" fill="none"/>')
    def dot(self,x,y):
        self.items.append(f'<circle cx="{x}" cy="{y}" r="4" fill="#155a85"/>')
    def ground(self,x,y):
        self.line(x,y,x,y+12)
        for dy,w in [(12,16),(19,10),(26,4)]:self.line(x-w,y+dy,x+w,y+dy)
    def resistor(self,x,y,ref,value,vertical=False):
        if vertical:
            self.line(x,y,x,y+12)
            self.items.append(f'<rect x="{x-7}" y="{y+12}" width="14" height="35" fill="white" stroke="#155a85" stroke-width="2"/>')
            self.line(x,y+47,x,y+60)
            self.text(x+14,y+25,ref+" "+value,"small")
        else:
            self.line(x,y,x+12,y)
            self.items.append(f'<rect x="{x+12}" y="{y-7}" width="56" height="14" fill="white" stroke="#155a85" stroke-width="2"/>')
            self.line(x+68,y,x+80,y)
            self.text(x,y-18,ref+" "+value,"small")
    def capacitor(self,x,y,ref,value):
        self.line(x,y,x,y+24);self.line(x-14,y+24,x+14,y+24)
        self.line(x-14,y+32,x+14,y+32);self.line(x,y+32,x,y+60)
        self.text(x+18,y+32,ref+" "+value,"small")
    def box(self,x,y,w,h,title,lines):
        self.items.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="#f1f7fb" stroke="#46677d" stroke-width="1.5"/>')
        self.text(x+15,y+28,title,"head")
        for n,l in enumerate(lines):self.text(x+15,y+56+24*n,l,"body")
    def row(self,x,y,left,right,w=590):
        self.text(x,y,left,"net");self.line(x+260,y-6,x+w-160,y-6);self.text(x+w-150,y,right,"net")
    def save(self,name):
        self.text(35,self.h-24,"DALEK ROUND / FRICTION | 2026-09-12 | Circuit + wiring.csv form one drawing set | Physical validation required","small")
        s="\n".join(self.items+["</svg>"])
        ET.fromstring(s)
        (HERE/name).write_text(s,encoding="utf-8")

def diagrams():
    s=Sheet("01 / Power distribution and isolation","B1 = Bioenno BLF-1206A + matched BPC-1502DC charger. All grounds join at GROUND_STAR.")
    s.box(35,115,370,150,"B1 / 12V 6Ah LiFePO4",["72Wh nominal; 12A continuous maximum","PP30 discharge + / -; protected pack","Separate factory DC charge connector","REMOVE pack from robot to charge"])
    s.box(470,115,400,150,"F1 + S1 / MAIN",["B1.PP30+ -> F1 7.5A -> S1.1","S1.3 -> PACK_SW","NKK S1A, ON joins 1 and 3","F1 within 100mm of battery lead"])
    s.line(405,185,470,185)
    s.box(930,115,620,150,"S2 / ACTUATORS OFF",["PACK_SW -> S2.1; S2.3 -> ACT_IN","NKK S1A, 20A at 30VDC; label OFF position","Cuts input power to BOTH motion converters","Logic/audio supply bypasses S2; power stays on"])
    s.line(870,185,930,185)
    s.box(35,330,475,255,"U2 / MOTOR 5V",["ACT_IN -> F2 3A -> MOTOR_IN -> VIN","Pololu D36V50F5 #4091","VOUT -> U5/U6/U11.VMotor + U9.14","C1 220uF/25V: VIN(+) to GND(-)","C4/C5/C12 470uF: one per driver","R15 100ohm/1W: output to GND","5A motor allowance + 0.05A bleed","Ground return: 18AWG to star"])
    s.box(555,330,475,255,"U3 / SERVO 5V",["ACT_IN -> F3 3A -> SERVO_IN -> VIN","Pololu D36V50F5 #4091","VOUT -> servo distribution + U8.14","C2 220uF/25V: VIN(+) to GND(-)","C6 1000uF/10V at distribution block","R16 100ohm/1W: output to GND","4A allowance + 0.05A bleed","4 separate 22AWG servo branches"])
    s.box(1075,330,475,255,"U4 / LOGIC 5V",["PACK_SW -> F4 1A -> LOGIC_IN -> IN","Adafruit MPM3610 #4739","OUT -> 5V_LOGIC -> amp + run link","C3 100uF/25V: IN(+) to GND(-)","C7 470uF/10V: OUT(+) to GND(-)","EN: no connection (enabled)","Budget 0.9A; maximum rated 1.2A","Do not connect the three 5V rails"])
    s.box(35,630,715,150,"ADC39 / battery voltage divider",["PACK_SW -> R10 100k -> BAT_ADC -> R11 22k -> GND","BAT_ADC -> GPIO39; C10 100nF BAT_ADC to GND","At 14.6V: ADC = 2.633V. Scale = 122 / 22 = 5.54545","Cutoff 11.2V; re-arm above 12.0V; calibrate with meter"])
    s.box(800,630,750,150,"GPIO36 / actuator power sense",["5V_MOTOR -> R12 10k -> ACT_OK -> R13 15k -> GND","ACT_OK -> GPIO36; C11 100nF ACT_OK to GND","At 5V: GPIO36 = 3.0V. High permits arming; low stops.","Discharge resistors drain stored output energy after OFF"])
    s.box(35,825,715,175,"USB service: prevent two power sources",["J_USB_ISO connects 5V_LOGIC to U1.5V only during RUN.","Before USB: S1 OFF; unplug B1.PP30; open J_USB_ISO.","Connect USB only after external run power is disconnected.","Remove USB before reconnecting run power and the battery.","Never use U1 BAT/JST connector for the 12V pack."])
    s.box(800,825,750,175,"Physical wiring",["18AWG stranded: battery, switches, regulators, motor bus.","22AWG: individual servo branches and logic power.","26AWG: signals. Twisted pairs: each motor; speaker output.","No solderless breadboard for power. Insulate every joint.","Two DC switches are disconnects; this is not a certified E-stop."])
    s.save("01-power.svg")

    s=Sheet("02 / Controller, drive motors and sound","U1 = original LILYGO TTGO T-Display ESP32, 1.14 inch ST7789. GPIO numbers, not header positions.",1600,1250)
    s.box(35,115,740,420,"U1 / exact external pin assignment",[])
    assignments=[("GPIO21","SDA -> U10.SDA"),("GPIO22","SCL -> U10.SCL"),("GPIO27","SERVO_DISABLE / OE"),("GPIO12","MOTOR_ENABLE / SLP"),("GPIO25","LEFT_IN1"),("GPIO26","LEFT_IN2"),("GPIO32","RIGHT_IN1"),("GPIO33","RIGHT_IN2"),("GPIO17","I2S_BCLK"),("GPIO13","I2S_LRC"),("GPIO15","I2S_DATA"),("GPIO39 (SVN)","BAT_ADC"),("GPIO36 (SVP)","ACT_OK"),("GPIO2","HEAD_PWM -> U9.2 + .5")]
    for i,(p,n) in enumerate(assignments):s.row(55,173+24*i,p,n,650)
    s.box(825,115,725,195,"Reserved board connections",["TFT: MOSI19, SCLK18, CS5, DC16, RST23, BL4","Buttons: GPIO0 and GPIO35; reserve both.","Onboard battery ADC34 and power14 are NOT pack sense.","GPIO12 and GPIO2 each have a 10k boot-safe pull-down.","GPIO15 connects only to amplifier DIN; no external bias.","GPIO37, 38 and UART pins: no external connection."])
    s.box(825,340,725,195,"Hardware stopped on reset",["R1..R4: 10k from each wheel input net to GND.","R5: 10k MOTOR_ENABLE to GND; ALL THREE SLP pins join.","R6: 10k SERVO_DISABLE to3V3; R24: HEAD_PWM to GND.","Firmware: SLP low, PWM low, OE high before devices init.","U1.3V3 -> U10.VCC; all GND pins join common ground.","Physical power OFF removes wheel, head and arm power."])
    for x,side,driver in [(35,"LEFT","U5"),(825,"RIGHT","U6")]:
        s.box(x,585,725,255,f"{driver} / Adafruit DRV8833 #3297",[f"{side}_IN1 -> AIN1 AND BIN1 (INPUTS ONLY)",f"{side}_IN2 -> AIN2 AND BIN2 (INPUTS ONLY)","SLP <- MOTOR_ENABLE; VMotor <- 5V_MOTOR; GND <- star",f"AOUT1/AOUT2 -> M_{side}_FRONT +/-",f"BOUT1/BOUT2 -> M_{side}_REAR +/-","Keep BOTH default0.2ohm sense resistors:1A per bridge.","DO NOT parallel the output bridges or two motors on one.","FLT, VM, ASEN, BSEN: no external connection."])
    s.box(35,890,725,225,"U7 / MAX98357A + SPK1",["VIN <- 5V_LOGIC; GND <- common ground","BCLK <- GPIO17; LRC <- GPIO13; DIN <- GPIO15","GAIN -> R14 100k -> 5V_LOGIC (3dB)","SD: leave factory 1Mohm resistor configuration (mono mix)","OUT+ -> SPK1+; OUT- -> SPK1-; NEITHER lead to GND","SPK1: Adafruit 1313, 8ohm 1W; fixed digital gain 0.28","No external DAC, SD card or MP3 trigger module required."])
    s.box(825,890,725,225,"Drive commissioning",["100nF ceramic across each motor's metal tabs.","Use fast-decay PWM: one input PWM, other input low.","Stop both inputs low and SLP low; this is coast, not a brake.","Check each motor forward direction with wheels in air.","Swap that motor's two leads if its direction is wrong.","1A limit protects the driver, not indefinite motor stalls.","Indoor flat surface; no carpet, stairs or sustained wheel jams."])
    s.save("02-controller-drive-audio.svg")

    s=Sheet("03 / Four arm servos and head PWM routing","All chip numbers below are DIP-14 PHYSICAL pin numbers. U8/U9 are 74AHCT125, not 74HC125.",1600,1510)
    s.box(35,115,740,185,"U10 / Adafruit PCA9685 #815",["VCC <-3V3; GND <-common ground; SDA21; SCL22","Address0x40;50Hz pins0..3 ->U8;V+ UNCONNECTED","Remove OE pull-down; R6 10k OE to3V3; GPIO27 ->OE","Firmware sets/reads MODE2=0x06 (OUTDRV1 / OUTNE10)","OE HIGH: outputs high-Z; R7/R8 disable both head gates","Pins4/5 are STATIC direction enables, not servo pulses."])
    s.box(825,115,725,185,"U8 and U9: two DIFFERENT supplies",["U8.14 ->5V_SERVO; U9.14 ->5V_MOTOR; both pin7 ->GND","C8 at U8; C9 at U9:100nF directly across14 and7.","U8 pins1,4,10,13 ->SERVO_DISABLE (GPIO27).","U9 pins1/4 ->PCA4/5; each has10k pull-up to3V3.","U9 unused:9/12 ->GND;10/13 ->5V_MOTOR;8/11 open.","AHCT tolerates 3.3V input with its own supply off."])
    y=355
    for c,(name,chip,a,out) in enumerate(channels):
        s.box(35,y,335,102,f"PWM{c} / {name}",[f"U10.PWM{c} -> {chip} pin{a}",f"R{20+c} 10k: input toGND"])
        s.line(370,y+54,455,y+54)
        s.box(455,y,465,102,f"{chip} 74AHCT125",[f"Input pin{a} -> internal buffer -> output pin{out}",f"pin{out} -> R{30+c} 220ohm -> signal"])
        s.line(920,y+54,1005,y+54)
        s.box(1005,y,545,102,f"SV{c} / MG92B #2307 / inside shoulder",[f"SIGNAL <- R{30+c}; R{40+c} 10k SIGNAL toGND","RED <-5V_SERVO; BLACK/BROWN <-GND"])
        y+=127
    s.box(35,880,740,255,"U9 / head direction selects the PWM route",["GPIO2 -> U9.2 AND U9.5; R24 10k GPIO2 toGND","PCA4 -> U9.1 (/OE); R7 10k PCA4 to3V3","PCA5 -> U9.4 (/OE); R8 10k PCA5 to3V3","U9.3 -> R34 220ohm -> U11.AIN1","U9.6 -> R35 220ohm -> U11.AIN2","R44/R45 10k: each U11 input toGND","Forward: PCA4 LOW / PCA5 HIGH; reverse opposite","PWM=0 before gate changes; both gates disabled first"])
    s.box(825,880,725,255,"U11 / added DRV8833 #3297 / head motor",["VMotor <-5V_MOTOR; GND <-star; SLP <-GPIO12","AOUT1/AOUT2 -> fifth TT3777 motor + / -","C_HEAD 100nF across motor tabs; twist22AWG pair","C12 470uF/10V: VMotor(+) toGND(-) at driver","Keep stock0.2ohm sense resistors:1A bridge limit","BIN1/BIN2 ->GND; BOUT1/BOUT2 left open","FLT/VM/ASEN/BSEN: no external connection","63mm TT wheel contacts head track; mount stays fixed"])
    s.box(35,1170,1515,140,"Head stop, reversal and preload adjustment",["20kHz PWM from GPIO2; maximum100/255. PCA outputs4/5 use full-on/full-off bits, independent of50Hz servo pulses.","Reversal ramps to zero, coasts100ms, then ramps up. Zero command, timeout, physical OFF or I2C fault removes PWM.","Adjust wheel contact with power OFF. Use only enough pressure to turn the dome; retain intentional slip under obstruction.","No position or speed feedback. The head can coast after power removal. No wiring enters the rotating head."])
    s.box(35,1345,1515,105,"Arm calibration",["Test1500us with horns removed; fit horns at center. Begin at +/-2 degrees and0.10Hz; check every hidden linkage.","Default AND maximum radius:8 degrees. Normal frequency0.40Hz. Keep all four servos inside the shoulder."])
    s.save("03-servos.svg")

    s=Sheet("04 / Circuit details: power, sensing and bridge outputs","Conventional connection symbols. Dots are junctions. Matching net labels join all four sheets.",1600,1250)
    s.text(40,140,"A. Battery fuse and independent motion disconnect","head")
    s.box(40,185,200,115,"B1",["BLF-1206A","PP30 + / -"])
    s.line(240,215,285,215);s.resistor(285,215,"F1","7.5A")
    s.line(365,215,450,215);s.dot(450,215);s.line(450,215,490,190)
    s.line(505,215,620,215);s.dot(505,215);s.text(450,175,"S1 MAIN","small")
    s.dot(620,215);s.text(640,255,"PACK_SW","net")
    s.line(620,215,735,215);s.dot(735,215);s.line(735,215,775,190)
    s.dot(790,215);s.line(790,215,890,215);s.text(715,175,"S2 ACTUATORS","small")
    s.dot(890,215);s.text(905,220,"ACT_IN -> F2 -> U2.VIN","net")
    s.line(890,215,890,270);s.text(905,277,"ACT_IN -> F3 -> U3.VIN","net")
    s.line(620,215,620,340);s.text(635,347,"PACK_SW -> F4 -> U4.IN (logic remains on)","net")
    s.line(240,270,310,270);s.ground(310,270)
    s.text(40,385,"S1/S2 are shown OFF. NKK S1A ON joins terminals1 and3. Ground is never switched.","small")

    s.text(40,450,"B. Battery measurement / GPIO39","head")
    s.text(40,500,"PACK_SW","net");s.line(140,495,190,495)
    s.resistor(190,495,"R10","100k 1%");s.line(270,495,360,495);s.dot(360,495)
    s.line(360,495,630,495);s.text(645,500,"U1.GPIO39","net")
    s.resistor(360,495,"R11","22k 1%",True);s.ground(360,555)
    s.dot(550,495);s.capacitor(550,495,"C10","100nF");s.ground(550,555)
    s.text(40,620,"14.6V x22/(100+22) =2.633V; firmware multiplier5.54545","small")

    s.text(825,450,"C. Motion power sense / GPIO36","head")
    s.text(825,500,"5V_MOTOR","net");s.line(935,495,970,495)
    s.resistor(970,495,"R12","10k 1%");s.line(1050,495,1130,495);s.dot(1130,495)
    s.line(1130,495,1410,495);s.text(1420,500,"GPIO36","net")
    s.resistor(1130,495,"R13","15k 1%",True);s.ground(1130,555)
    s.dot(1320,495);s.capacitor(1320,495,"C11","100nF");s.ground(1320,555)
    s.text(825,620,"5V x15/(10+15) =3.0V; low means physical power OFF","small")

    s.text(40,690,"D. Motor output circuit (repeat for all5 motors)","head")
    s.box(40,755,320,180,"U5 DRV8833 / bridge A",["VMotor =5V_MOTOR","GND =GROUND_STAR","AIN1 =LEFT_IN1","AIN2 =LEFT_IN2","SLP =MOTOR_ENABLE"])
    s.line(360,780,660,780);s.line(360,890,660,890)
    s.text(373,767,"AOUT1","net");s.text(373,918,"AOUT2","net")
    s.dot(510,780);s.line(510,780,510,800);s.capacitor(510,800,"C_LF","100nF")
    s.line(510,860,510,890);s.dot(510,890)
    s.line(660,780,660,810);s.line(660,860,660,890)
    s.items.append('<circle cx="660" cy="835" r="25" fill="white" stroke="#155a85" stroke-width="2"/>')
    s.text(650,841,"M","head");s.text(585,960,"LEFT FRONT TT3777","net")
    s.text(40,1010,"U5.B ->LEFT REAR; U6.A/B ->RIGHT FRONT/REAR; U11.A ->HEAD (routing on sheet03).","small")
    s.text(40,1040,"Bridge outputs never join one another. The only shared connections are INPUTS and supplies.","small")

    s.text(870,690,"E. Reset default states","head")
    s.text(870,760,"GPIO12","net");s.line(965,755,1130,755);s.dot(1130,755)
    s.line(1130,755,1300,755);s.text(1310,760,"U5/U6/U11.SLP","net")
    s.resistor(1130,755,"R5","10k",True);s.ground(1130,815)
    s.text(870,900,"3V3","net");s.line(930,895,980,895);s.resistor(980,895,"R6","10k")
    s.line(1060,895,1130,895);s.dot(1130,895);s.text(1170,900,"SERVO_DISABLE","net")
    s.line(1130,895,1130,955);s.text(920,980,"GPIO27 / U10.OE / U8 /OE","net")
    s.text(870,1040,"Remove originalPCAOE pull-down.","small")
    s.text(870,1070,"GPIO2 and head AIN1/AIN2:10k pull-downs.","small")
    s.text(40,1140,"POWER NOTES: F2/F3=3A; F4=1A. Correct capacitor polarity. All connection values also appear in sheets01-03.","body")
    s.save("04-circuit-details.svg")

def main():
    HERE.mkdir(exist_ok=True)
    with (HERE/"wiring.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(ROWS[0]));w.writeheader();w.writerows(ROWS)
    mass, radius, torque = 3.0, .0315, .8*.0980665
    limit_torque=torque*(1.0-.16)/(1.5-.16)
    results={
        "status":"engineering estimates; not measurements of a built robot",
        "battery_nominal_Wh":72,"battery_design_usable_fraction":.75,
        "battery_max_charge_V":14.6,"battery_adc_V_at_max":14.6*22/122,
        "battery_adc_scale":122/22,"battery_stop_V":11.2,"battery_rearm_V":12.0,
        "actuator_sense_V":5*15/25,"motor_current_limit_each_A":1,
        "drive_motor_count":4,"head_motor_count":1,"total_TT_motor_count":5,
        "motor_rail_design_A":5,"servo_rail_design_peak_A":4,
        "logic_rail_design_peak_A":.9,"actuator_bleeders_W":.5,
        "motor_rail_with_bleeder_A":5.05,"servo_rail_with_bleeder_A":4.05,
        "peak_output_W":5*(5+4+.9)+.5,
        "estimated_peak_pack_A_at_11p2V_85pct":(5*(5+4+.9)+.5)/(11.2*.85),
        "head_pwm_frequency_Hz":20000,"head_pwm_limit_of_255":100,"head_reverse_coast_ms":100,
        "arm_radius_limit_degrees":8,
        "estimated_runtime_h_15W":72*.75/15,"estimated_runtime_h_25W":72*.75/25,
        "previous_planning_mass_target_kg":mass,"wheel_radius_m":radius,
        "catalog_6V_stall_torque_each_Nm":torque,
        "estimated_1A_limit_torque_each_Nm":limit_torque,
        "estimated_4motor_limited_force_N":4*limit_torque/radius,
        "ideal_6V_no_load_speed_m_s_at_250rpm":2*math.pi*radius*250/60,
        "notes":["Stall torque is not continuous torque. Current-to-torque interpolation is an approximation.",
                 "Skid steering scrub can dominate rolling resistance; confirm turns on actual flooring.",
                 "No encoder exists; PWM duty does not prove ground speed.",
                 "Servo current budget is an allowance because authoritative stall-current data is missing."]}
    (HERE/"calculations.json").write_text(json.dumps(results,indent=2)+"\n",encoding="utf-8")
    diagrams()
    print(f"PASS: {len(ROWS)} wiring rows, 4 parseable SVG circuit sheets, calculations.json")

if __name__ == "__main__":main()
