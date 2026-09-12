#include <Arduino.h>
#include <WiFi.h>
#include <WebServer.h>
#include <Preferences.h>
#include <LittleFS.h>
#include <AudioFileSourceLittleFS.h>
#include <AudioGeneratorMP3.h>
#include <AudioOutputI2S.h>
#include <esp_task_wdt.h>
#include <Wire.h>
#include "config.h"
#include "control.h"
#include "posture.h"
WebServer server(80);Preferences prefs;
AudioFileSourceLittleFS soundFile;AudioGeneratorMP3 mp3;AudioOutputI2S audioOut;
r2::Controller controller;portMUX_TYPE mutex=portMUX_INITIALIZER_UNLOCKED;
bool ready=false,healthy=false,fsReady=false,sensorsReady=false;float volts=0,postMM=0,postAmps=0,tiltDeg=0;
const char *postReason="not initialized";
void stop(){portENTER_CRITICAL(&mutex);controller.stop();portEXIT_CRITICAL(&mutex);}
void motor(int i,int value){int f=i*2,r=f+1;
 if(value>0){ledcWrite(r,0);ledcWrite(f,value);}else{ledcWrite(f,0);ledcWrite(r,-value);}}
void pulse(int channel,int us){ledcWrite(channel,(uint32_t)us*65536UL/20000UL);}
bool write16(uint8_t address,uint8_t reg,uint16_t value){Wire.beginTransmission(address);Wire.write(reg);Wire.write(value>>8);Wire.write(value&255);return Wire.endTransmission()==0;}
bool read16(uint8_t address,uint8_t reg,uint16_t &value){Wire.beginTransmission(address);Wire.write(reg);if(Wire.endTransmission(false)!=0)return false;if(Wire.requestFrom(address,(uint8_t)2)!=2)return false;value=(Wire.read()<<8)|Wire.read();return true;}
void bridge(int forward,int reverse,int value){if(value>0){ledcWrite(reverse,0);ledcWrite(forward,value);}else{ledcWrite(forward,0);ledcWrite(reverse,-value);}}
void motion(void*){
 esp_task_wdt_add(nullptr);r2::Ramp ramps[3];r2::Posture posture;TickType_t wake=xTaskGetTickCount();
 bool battery=false,lowTiming=false;uint32_t lowSince=0,lastSample=0;float filtered=0,angle=0;bool initialized=false;
 portENTER_CRITICAL(&mutex);ready=true;portEXIT_CRITICAL(&mutex);
 for(;;){uint32_t now=millis();
  if(now-lastSample>=100){lastSample=now;
   float raw=analogReadMilliVolts(pins::PACK)*.001f*calibration::PACK_SCALE*calibration::PACK_CORRECTION;
   filtered=initialized?.8f*filtered+.2f*raw:raw;initialized=true;
   if(filtered<calibration::CUTOFF){if(!lowTiming){lowTiming=true;lowSince=now;}}else lowTiming=false;
   if(raw<1||filtered>calibration::MAX_PACK||(lowTiming&&now-lowSince>=1000))battery=false;
   else if(filtered>=calibration::REARM&&filtered<=calibration::MAX_PACK)battery=true;
  }
  uint16_t adc=0,current=0,inaCalibration=0,adcConfig=0;
  bool sensed=sensorsReady&&read16(0x48,0,adc)&&read16(0x40,4,current)&&read16(0x40,5,inaCalibration)&&read16(0x48,1,adcConfig)&&inaCalibration==4096&&(adcConfig&0x7fff)==0x4283;
  now=millis(); // Evaluate command age after bounded I2C transactions.
  float mm=((int16_t)adc-calibration::POST_ADC_ZERO)*100.0f/(calibration::POST_ADC_FULL-calibration::POST_ADC_ZERO);
  float amps=(int16_t)current*.0001f;
  bool powered=digitalRead(pins::POWER)==HIGH;
  bool good=powered&&battery&&digitalRead(pins::FAULT)==HIGH&&fsReady&&sensed&&!posture.fault;
  portENTER_CRITICAL(&mutex);healthy=good;volts=filtered;controller.tick(now,good);
  bool armed=controller.armed;r2::Command command=controller.command;portEXIT_CRITICAL(&mutex);
  r2::Mix target=r2::mix(command,good?r2::rearOffset(mm):129);
  bool postureRequest=command.posture>=0;
  if(armed){float delta=target.angle-angle;angle+=constrain(delta,-.3f,.3f);}
  int postOutput=posture.tick(now,armed&&postureRequest&&command.speed==0&&command.turn==0&&command.head==0&&fabsf(angle)<.2f,command.posture,mm,amps,sensed);
  bridge(10,11,postOutput);
  if(posture.fault){good=false;armed=false;stop();}
  if(armed&&!postureRequest){
   // Let the steering settle before driving. Recenter/reversal never bypasses this gate.
   int outputs[3]={target.left,target.right,target.rear};bool aligned=fabsf(target.angle-angle)<2;
   for(int i=0;i<3;i++)motor(i,ramps[i].tick(aligned?outputs[i]:0,now)*calibration::DIRECTION[i]);
   digitalWrite(pins::SLEEP,HIGH);
  }else{digitalWrite(pins::SLEEP,LOW);for(int i=0;i<3;i++){motor(i,0);ramps[i].stop();}}
  if(powered){pulse(6,constrain((int)(calibration::STEER_CENTER_US+r2::steeringServoDegrees(angle)*calibration::STEER_US_PER_DEGREE),1100,1900));}
  else ledcWrite(6,0);
  bridge(8,9,armed&&!postureRequest?command.head*calibration::HEAD_LIMIT/100:0);
  portENTER_CRITICAL(&mutex);postMM=mm;postAmps=amps;tiltDeg=sensed&&mm>=1.5f&&mm<=85?-r2::pitchDegrees(mm):0;postReason=posture.reason;healthy=good;portEXIT_CRITICAL(&mutex);
  esp_task_wdt_reset();vTaskDelayUntil(&wake,pdMS_TO_TICKS(10));
 }
}
bool number(const char *key,long low,long high,long &v){return server.hasArg(key)&&r2::parse(server.arg(key).c_str(),low,high,v);}
void routes(){
 server.on("/",HTTP_GET,[]{File f=LittleFS.open("/index.html");server.sendHeader("Cache-Control","no-store");server.streamFile(f,"text/html");f.close();});
 server.on("/app.js",HTTP_GET,[]{File f=LittleFS.open("/app.js");server.sendHeader("Cache-Control","no-store");server.streamFile(f,"application/javascript");f.close();});
 server.on("/api/status",HTTP_GET,[]{portENTER_CRITICAL(&mutex);bool a=controller.armed,h=healthy&&ready;float v=volts,p=postMM,t=tiltDeg;const char *why=postReason;portEXIT_CRITICAL(&mutex);
  server.sendHeader("Cache-Control","no-store");server.send(200,"application/json",String("{\"armed\":")+(a?"true":"false")+",\"healthy\":"+(h?"true":"false")+",\"volts\":"+String(v,2)+",\"post_mm\":"+String(p,1)+",\"estimated_tilt\":"+String(t,1)+",\"post_status\":\""+why+"\"}");});
 server.on("/api/arm",HTTP_POST,[]{uint32_t token=esp_random()&0x7fffffff;if(!token)token=1;
  portENTER_CRITICAL(&mutex);bool ok=controller.arm(millis(),token,healthy&&ready);portEXIT_CRITICAL(&mutex);
  server.send(ok?200:409,"application/json",ok?String("{\"lease\":")+String(token)+"}":"{\"error\":\"Check RUN switch, battery and faults\"}");});
 server.on("/api/stop",HTTP_POST,[]{stop();server.send(200,"text/plain","Stopped");});
 server.on("/api/command",HTTP_POST,[]{long token,seq,speed,turn,head,post;
  if(!number("lease",1,2147483647,token)||!number("seq",1,2147483647,seq)||!number("speed",-100,100,speed)||!number("turn",-100,100,turn)||!number("head",-100,100,head)||!number("posture",-1,100,post)||(post>=0&&(speed||turn||head))){stop();server.send(400,"text/plain","Invalid command; stop and center before posture change");return;}
  r2::Command c;c.speed=speed;c.turn=turn;c.head=head;c.posture=post;
  portENTER_CRITICAL(&mutex);bool ok=controller.accept(millis(),token,seq,c,healthy&&ready);portEXIT_CRITICAL(&mutex);
  server.send(ok?200:409,"text/plain",ok?"OK":"Disarmed; arm again");});
 server.on("/api/sound",HTTP_POST,[]{long n;if(!number("id",1,16,n)){server.send(400,"text/plain","Invalid sound");return;}
  if(mp3.isRunning())mp3.stop();soundFile.close();char path[32];snprintf(path,sizeof(path),"/audio/%02ld.mp3",n);
  if(!soundFile.open(path)||!mp3.begin(&soundFile,&audioOut)){server.send(500,"text/plain","Sound unavailable");return;}
  server.send(200,"text/plain","Playing");});
 server.onNotFound([]{server.send(404,"text/plain","Not found");});server.begin();
}
void setup(){
 pinMode(pins::SLEEP,OUTPUT);digitalWrite(pins::SLEEP,LOW);
 for(int i=0;i<6;i++){ledcSetup(i,18000,8);ledcAttachPin(pins::MOTOR[i],i);ledcWrite(i,0);}
 ledcSetup(6,50,16);ledcAttachPin(pins::STEER,6);ledcWrite(6,0);
 for(int channel=8;channel<=11;channel++){ledcSetup(channel,18000,8);ledcWrite(channel,0);}
 ledcAttachPin(pins::HEAD,8);ledcAttachPin(pins::HEAD_REVERSE,9);ledcAttachPin(pins::POST_EXTEND,10);ledcAttachPin(pins::POST_RETRACT,11);
 pinMode(pins::FAULT,INPUT);pinMode(pins::POWER,INPUT);pinMode(pins::PACK,INPUT);analogSetPinAttenuation(pins::PACK,ADC_11db);
 Serial.begin(115200);fsReady=LittleFS.begin(false);
 audioOut.SetPinout(pins::BCLK,pins::LRCLK,pins::AUDIO);audioOut.SetGain(.22f);
 Wire.begin(pins::SDA,pins::SCL);Wire.setTimeOut(20);Wire.setClock(400000);
 sensorsReady=write16(0x48,1,0xc283)&&write16(0x40,0,0x399f)&&write16(0x40,5,4096);delay(12);
 esp_task_wdt_init(2,true);
 if(xTaskCreatePinnedToCore(motion,"motion",4096,nullptr,3,nullptr,1)!=pdPASS){Serial.println("Motion task failed; power off");return;}
 prefs.begin("r2wifi",false);String password=prefs.getString("password","");
 if(password.length()!=16){const char alphabet[]="ABCDEFGHJKLMNPQRSTUVWXYZ23456789";password="";for(int i=0;i<16;i++)password+=alphabet[esp_random()%32];prefs.putString("password",password);}
 prefs.end();WiFi.mode(WIFI_AP);WiFi.softAP("R2-24",password.c_str(),1,false,1);
 // Shown only to the owner on the physical USB serial console; not logged by build tools.
 Serial.println("R2-24 local access point. Save this password privately:");Serial.println(password);
 Serial.println("Open http://192.168.4.1 ; RUN switch OFF until commissioning.");
 if(!fsReady){Serial.println("Missing filesystem: uploadfs required. Motion locked.");return;}routes();
}
void loop(){server.handleClient();if(mp3.isRunning()&&!mp3.loop()){mp3.stop();soundFile.close();}delay(1);}
