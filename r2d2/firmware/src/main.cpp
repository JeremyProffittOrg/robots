// R2-24 revision D controller for the DFRobot Romeo ESP32-S3 (DFR0994).
#include <Arduino.h>
#include <WiFi.h>
#include <WebServer.h>
#include <Preferences.h>
#include <LittleFS.h>
#include <AudioFileSourceLittleFS.h>
#include <AudioGeneratorMP3.h>
#include <AudioOutputI2S.h>
#include <esp_task_wdt.h>
#include "config.h"
#include "control.h"
#include "inputs.h"
#include "posture.h"
#include "stance.h"

// ESP32-S3 LEDC: eight channels; channels n and n+1 share one timer, so pairs share frequency and resolution.
namespace ch { constexpr int LEFT=0, RIGHT=1, CENTER=2, HEAD=3, STEER=4, LOCK=5, EXTEND=6, RETRACT=7; }
constexpr uint32_t SERVO_BITS=14; // S3 LEDC maximum resolution

WebServer server(80); Preferences prefs;
AudioFileSourceLittleFS soundFile; AudioGeneratorMP3 mp3; AudioOutputI2S audioOut;
r2::Controller controller; portMUX_TYPE mutex=portMUX_INITIALIZER_UNLOCKED;
bool ready=false, healthy=false, fsReady=false;

struct Snapshot {
 float volts=0; const char *state="STARTING", *phase="NONE", *fault="NONE", *reason="starting";
 bool positionValid=false, lockValid=false, lockEngaged=false, limitsClosed=false;
 float postMm=0; bool pitchValid=false; float pitchDeg=0; const char *pitchSource="unknown";
 bool driveAllowed=false, headAllowed=false; const char *twoBlock="starting", *threeBlock="starting";
};
Snapshot snap;
int clearState=0; // 0 idle, 1 requested, 2 cleared, 3 refused

class RomeoHal : public r2::StanceHal {
 public:
 bool positionOk=false, lockOk=false, lockEngaged=false, lockWithdrawn=false, limits=false, power=false, fresh=false;
 float mm=0; int actuator=0; bool release=false;
 bool readPositionMm(float &out) override { out=mm; return positionOk; }
 bool readLockEngaged(bool &out) override { out=lockEngaged; return lockOk; }
 bool readLockWithdrawn(bool &out) override { out=lockWithdrawn; return lockOk; }
 bool travelLimitsClosed() override { return limits; }
 bool powerHealthy() override { return power; }
 bool heartbeatFresh(uint32_t) override { return fresh; }
 void driveActuator(int percent) override { actuator=percent; }
 void commandLockRelease(bool r) override { release=r; }
};

void stop(){portENTER_CRITICAL(&mutex);controller.stop();portEXIT_CRITICAL(&mutex);}

// DRV8876 PH/EN: input is signed percent. EN=0 brakes both outputs low.
int phaseLevel[4]={-1,-1,-1,-1};
r2::PhEnDrive bridgeState[4];
const int PH_PIN[4]={pins::LEFT_PH,pins::RIGHT_PH,pins::CENTER_PH,pins::HEAD_PH};
void bridge(int channel,int value){
 auto output=bridgeState[channel].tick(value,millis());
 if(!output.duty){ledcWrite(channel,0);return;}
 int level=output.direction>0?HIGH:LOW;
 if(phaseLevel[channel]!=level){
  ledcWrite(channel,0);
  delayMicroseconds(120); // More than two18kHz periods: let LEDC's zero duty latch.
  digitalWrite(PH_PIN[channel],level);phaseLevel[channel]=level;
 }
 ledcWrite(channel,output.duty);
}
void servo(int channel,int us){ledcWrite(channel,(uint32_t)us*(1UL<<SERVO_BITS)/20000UL);}
void actuatorOutput(int percent){
 uint32_t duty=(uint32_t)abs(percent)*255UL/100UL;
 if(percent>0){ledcWrite(ch::RETRACT,0);ledcWrite(ch::EXTEND,duty);}
 else if(percent<0){ledcWrite(ch::EXTEND,0);ledcWrite(ch::RETRACT,duty);}
 else{ledcWrite(ch::EXTEND,0);ledcWrite(ch::RETRACT,0);}
}

void motion(void*){
 esp_task_wdt_add(nullptr);
 r2::Ramp ramps[3],headRamp; r2::Stance stance(calibration::STANCE); RomeoHal hal;
 r2::ContactPair lock(calibration::LOCK_LEGAL_MS,calibration::LOCK_ILLEGAL_MS);
 r2::ContactPair withdrawn(calibration::LOCK_LEGAL_MS,calibration::LOCK_ILLEGAL_MS);
 TickType_t wake=xTaskGetTickCount();
 bool battery=false,lowTiming=false,initialized=false,wasFault=false;uint32_t lowSince=0,lastSample=0,bootAt=millis();float filtered=0,angle=0;
 portENTER_CRITICAL(&mutex);ready=true;portEXIT_CRITICAL(&mutex);
 for(;;){uint32_t now=millis();
  if(now-lastSample>=100){lastSample=now;
   float raw=analogReadMilliVolts(pins::PACK)*.001f*calibration::PACK_SCALE*calibration::PACK_CORRECTION;
   filtered=initialized?.8f*filtered+.2f*raw:raw;initialized=true;
   if(filtered<calibration::CUTOFF){if(!lowTiming){lowTiming=true;lowSince=now;}}else lowTiming=false;
   if(raw<1||filtered>calibration::MAX_PACK||(lowTiming&&now-lowSince>=1000))battery=false;
   else if(filtered>=calibration::REARM&&filtered<=calibration::MAX_PACK)battery=true;
  }
  uint32_t sum=0;for(int i=0;i<8;i++)sum+=analogReadMilliVolts(pins::POST_POSITION);
  hal.positionOk=r2::potPosition(sum/8.0f,calibration::POT,hal.mm);
  lock.update(now,digitalRead(pins::LOCK_NO)==LOW,digitalRead(pins::LOCK_NC)==LOW);
  withdrawn.update(now,digitalRead(pins::WITHDRAWN_NO)==LOW,digitalRead(pins::WITHDRAWN_NC)==LOW);
  hal.lockOk=lock.valid&&withdrawn.valid;hal.lockEngaged=lock.engaged;hal.lockWithdrawn=withdrawn.engaged;
  hal.limits=digitalRead(pins::LIMIT_EXTEND_OPEN)==LOW&&digitalRead(pins::LIMIT_RETRACT_OPEN)==LOW;
  bool powered=digitalRead(pins::POWER)==HIGH;
  hal.power=powered&&battery;
  bool good=powered&&battery&&fsReady;
  now=millis();
  portENTER_CRITICAL(&mutex);healthy=good;controller.tick(now,good);bool armed=controller.armed;r2::Command command=controller.command;
  hal.fresh=controller.fresh(now);bool clear=clearState==1;portEXIT_CRITICAL(&mutex);
  r2::StanceTarget request=armed&&command.stance>=0?(r2::StanceTarget)command.stance:r2::StanceTarget::NONE;
  bool driveIdle=!command.speed&&!command.turn&&!command.head&&fabsf(angle)<.2f&&!ramps[0].value&&!ramps[1].value&&!ramps[2].value&&!headRamp.value;
  bool inputsReady=(lock.settled()&&withdrawn.settled())||uint32_t(now-bootAt)>=1000;
  int cleared=0;
  if(inputsReady){
   if(clear)cleared=stance.clearFault(now)?2:3;
   stance.tick(now,hal,request,driveIdle);
  }
  actuatorOutput(hal.actuator);
  if(powered)servo(ch::LOCK,hal.release?calibration::LOCK_RELEASE_US:calibration::LOCK_ENGAGE_US);else ledcWrite(ch::LOCK,0);
  bool fault=stance.state==r2::StanceState::FAULT;
  if(fault&&!wasFault){stop();armed=false;} // a new fault disarms; the operator re-arms to clear it
  wasFault=fault;
  bool drive=armed&&stance.driveAllowed()&&command.stance<0;
  float offset=r2::centerFootOffsetMm(hal.positionOk?hal.mm:calibration::STANCE.threeFootMm);
  r2::Mix target=r2::mix(drive?command:r2::Command{},offset);
  if(powered){float wanted=drive?target.yaw:0;angle+=constrain(wanted-angle,-.3f,.3f);}
  if(drive){
   // Let the steering settle before driving. Recenter/reversal never bypasses this gate.
   int outputs[3]={target.left,target.right,target.center};bool aligned=fabsf(target.yaw-angle)<2;
   for(int i=0;i<3;i++)bridge(i,ramps[i].tick(aligned?outputs[i]:0,now)*calibration::DIRECTION[i]);
  }else for(int i=0;i<3;i++){ramps[i].stop();bridge(i,0);}
  if(powered)servo(ch::STEER,constrain((int)(calibration::STEER_CENTER_US+r2::steeringServoDegrees(angle)*calibration::STEER_US_PER_DEGREE),1100,1900));
  else ledcWrite(ch::STEER,0);
  bool headOk=armed&&stance.headAllowed()&&command.stance<0;
  if(headOk)bridge(ch::HEAD,headRamp.tick(command.head*calibration::HEAD_LIMIT/100,now));else{headRamp.stop();bridge(ch::HEAD,0);}
  r2::PostureEstimate pose=r2::estimatePosture(stance);
  const char *two=stance.blocked(r2::StanceTarget::TWO_FOOT,now,driveIdle),*three=stance.blocked(r2::StanceTarget::THREE_FOOT,now,driveIdle);
  portENTER_CRITICAL(&mutex);
  snap.volts=filtered;snap.state=stance.started()?r2::stanceName(stance.state):"STARTING";snap.phase=r2::phaseName(stance.phase);
  snap.fault=r2::faultName(stance.fault);snap.reason=stance.reason;snap.positionValid=stance.positionValid;snap.postMm=stance.positionValid?stance.positionMm:0;
  snap.lockValid=stance.lockValid;snap.lockEngaged=stance.lockEngaged;snap.limitsClosed=stance.limitsClosed;
  snap.pitchValid=pose.valid;snap.pitchDeg=pose.pitchDeg;snap.pitchSource=r2::pitchSourceName(pose.source);
  snap.driveAllowed=stance.driveAllowed();snap.headAllowed=stance.headAllowed();snap.twoBlock=two;snap.threeBlock=three;
  if(cleared)clearState=cleared;
  healthy=good;portEXIT_CRITICAL(&mutex);
  esp_task_wdt_reset();vTaskDelayUntil(&wake,pdMS_TO_TICKS(10));
 }
}

bool number(const char *key,long low,long high,long &v){return server.hasArg(key)&&r2::parse(server.arg(key).c_str(),low,high,v);}
String quoted(const char *text){return text?String("\"")+text+"\"":String("null");}
String flag(bool b){return b?"true":"false";}
void routes(){
 server.on("/",HTTP_GET,[]{File f=LittleFS.open("/index.html");server.sendHeader("Cache-Control","no-store");server.streamFile(f,"text/html");f.close();});
 server.on("/app.js",HTTP_GET,[]{File f=LittleFS.open("/app.js");server.sendHeader("Cache-Control","no-store");server.streamFile(f,"application/javascript");f.close();});
 server.on("/api/status",HTTP_GET,[]{
  portENTER_CRITICAL(&mutex);bool a=controller.armed,h=healthy&&ready;Snapshot s=snap;portEXIT_CRITICAL(&mutex);
  String body=String("{\"armed\":")+flag(a)+",\"healthy\":"+flag(h)+",\"volts\":"+String(s.volts,2)+
   ",\"stance\":"+quoted(s.state)+",\"phase\":"+quoted(s.phase)+",\"fault\":"+quoted(s.fault)+",\"reason\":"+quoted(s.reason)+
   ",\"post_mm\":"+(s.positionValid?String(s.postMm,1):String("null"))+",\"lock_valid\":"+flag(s.lockValid)+",\"lock_engaged\":"+flag(s.lockEngaged)+
   ",\"limits_closed\":"+flag(s.limitsClosed)+",\"pitch_deg\":"+(s.pitchValid?String(s.pitchDeg,1):String("null"))+",\"pitch_source\":"+quoted(s.pitchSource)+
   ",\"drive_allowed\":"+flag(s.driveAllowed)+",\"head_allowed\":"+flag(s.headAllowed)+
   ",\"can_two_foot\":"+flag(!s.twoBlock)+",\"can_three_foot\":"+flag(!s.threeBlock)+
   ",\"two_foot_block\":"+quoted(s.twoBlock)+",\"three_foot_block\":"+quoted(s.threeBlock)+"}";
  server.sendHeader("Cache-Control","no-store");server.send(200,"application/json",body);});
 server.on("/api/arm",HTTP_POST,[]{uint32_t token=esp_random()&0x7fffffff;if(!token)token=1;
  portENTER_CRITICAL(&mutex);bool ok=controller.arm(millis(),token,healthy&&ready);portEXIT_CRITICAL(&mutex);
  server.send(ok?200:409,"application/json",ok?String("{\"lease\":")+String(token)+"}":"{\"error\":\"Check RUN switch and battery\"}");});
 server.on("/api/stop",HTTP_POST,[]{stop();server.send(200,"text/plain","Stopped");});
 server.on("/api/command",HTTP_POST,[]{long token,seq,speed,turn,head,stanceRequest;
  if(!number("lease",1,2147483647,token)||!number("seq",1,2147483647,seq)||!number("speed",-100,100,speed)||!number("turn",-100,100,turn)||
     !number("head",-100,100,head)||!number("stance",-1,3,stanceRequest)||!r2::validStance(stanceRequest)||(stanceRequest>=0&&(speed||turn||head))){
   stop();server.send(400,"text/plain","Invalid command; a stance control carries no drive, turn or head");return;}
  portENTER_CRITICAL(&mutex);bool driveOk=snap.driveAllowed,headOk=snap.headAllowed;const char *state=snap.state;portEXIT_CRITICAL(&mutex);
  if(speed&&!driveOk){server.send(409,"text/plain",String("Drive refused in stance ")+state);return;}
  if(head&&!headOk){server.send(409,"text/plain",String("Head refused in stance ")+state);return;}
  r2::Command c;c.speed=speed;c.turn=turn;c.head=head;c.stance=stanceRequest;
  portENTER_CRITICAL(&mutex);bool ok=controller.accept(millis(),token,seq,c,healthy&&ready);portEXIT_CRITICAL(&mutex);
  server.send(ok?200:409,"text/plain",ok?"OK":"Disarmed; arm again");});
 server.on("/api/stance/clear",HTTP_POST,[]{long token;
  if(!number("lease",1,2147483647,token)){server.send(400,"text/plain","Lease required");return;}
  portENTER_CRITICAL(&mutex);bool ok=controller.armed&&controller.lease==(uint32_t)token;if(ok)clearState=1;portEXIT_CRITICAL(&mutex);
  if(!ok){server.send(409,"text/plain","Arm first");return;}
  int result=1;const char *why="";
  for(int i=0;i<30&&result==1;i++){delay(10);portENTER_CRITICAL(&mutex);result=clearState;why=snap.reason;portEXIT_CRITICAL(&mutex);}
  portENTER_CRITICAL(&mutex);clearState=0;portEXIT_CRITICAL(&mutex);
  if(result==2)server.send(200,"text/plain","Fault cleared");
  else server.send(409,"text/plain",String("Fault not cleared: ")+(result==1?"controller busy":why));});
 server.on("/api/sound",HTTP_POST,[]{long n;if(!number("id",1,16,n)){server.send(400,"text/plain","Invalid sound");return;}
  if(mp3.isRunning())mp3.stop();soundFile.close();char path[32];snprintf(path,sizeof(path),"/audio/%02ld.mp3",n);
  if(!soundFile.open(path)||!mp3.begin(&soundFile,&audioOut)){server.send(500,"text/plain","Sound unavailable");return;}
  server.send(200,"text/plain","Playing");});
 server.onNotFound([]{server.send(404,"text/plain","Not found");});server.begin();
}

void setup(){
 for(int i=0;i<4;i++){pinMode(PH_PIN[i],OUTPUT);digitalWrite(PH_PIN[i],LOW);}
 const int EN[4]={pins::LEFT_EN,pins::RIGHT_EN,pins::CENTER_EN,pins::HEAD_EN};
 for(int i=0;i<4;i++){ledcSetup(i,18000,8);ledcAttachPin(EN[i],i);ledcWrite(i,0);}
 ledcSetup(ch::STEER,50,SERVO_BITS);ledcSetup(ch::LOCK,50,SERVO_BITS);
 ledcAttachPin(pins::STEER,ch::STEER);ledcAttachPin(pins::LOCK_SERVO,ch::LOCK);ledcWrite(ch::STEER,0);ledcWrite(ch::LOCK,0);
 ledcSetup(ch::EXTEND,18000,8);ledcSetup(ch::RETRACT,18000,8);
 ledcAttachPin(pins::POST_EXTEND,ch::EXTEND);ledcAttachPin(pins::POST_RETRACT,ch::RETRACT);actuatorOutput(0);
 for(int pin:{pins::LOCK_NO,pins::LOCK_NC,pins::WITHDRAWN_NO,pins::WITHDRAWN_NC,pins::LIMIT_EXTEND_OPEN,pins::LIMIT_RETRACT_OPEN,pins::POWER})pinMode(pin,INPUT);
 analogSetPinAttenuation(pins::PACK,ADC_11db);analogSetPinAttenuation(pins::POST_POSITION,ADC_11db);
 Serial.begin(115200);fsReady=LittleFS.begin(false);
 audioOut.SetPinout(pins::BCLK,pins::LRCLK,pins::AUDIO);audioOut.SetGain(.11f); // amplifier GAIN pin open: 9 dB
 esp_task_wdt_init(2,true);
 if(xTaskCreatePinnedToCore(motion,"motion",6144,nullptr,3,nullptr,1)!=pdPASS){Serial.println("Motion task failed; power off");return;}
 prefs.begin("r2wifi",false);String password=prefs.getString("password","");
 if(password.length()!=16){const char alphabet[]="ABCDEFGHJKLMNPQRSTUVWXYZ23456789";password="";for(int i=0;i<16;i++)password+=alphabet[esp_random()%32];prefs.putString("password",password);}
 prefs.end();WiFi.mode(WIFI_AP);WiFi.softAP("R2-24",password.c_str(),1,false,1);
 // Shown only to the owner on the physical USB serial console; not logged by build tools.
 Serial.println("R2-24 local access point. Save this password privately:");Serial.println(password);
 Serial.println("Open http://192.168.4.1 ; RUN switch OFF until commissioning.");
 if(!fsReady){Serial.println("Missing filesystem: uploadfs required. Motion locked.");return;}routes();
}
void loop(){server.handleClient();if(mp3.isRunning()&&!mp3.loop()){mp3.stop();soundFile.close();}delay(1);}
