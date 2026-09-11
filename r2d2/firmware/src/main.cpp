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
WebServer server(80);Preferences prefs;
AudioFileSourceLittleFS soundFile;AudioGeneratorMP3 mp3;AudioOutputI2S audioOut;
r2::Controller controller;portMUX_TYPE mutex=portMUX_INITIALIZER_UNLOCKED;
bool ready=false,healthy=false,fsReady=false;float volts=0;
void stop(){portENTER_CRITICAL(&mutex);controller.stop();portEXIT_CRITICAL(&mutex);}
void motor(int i,int value){int f=i*2,r=f+1;
 if(value>0){ledcWrite(r,0);ledcWrite(f,value);}else{ledcWrite(f,0);ledcWrite(r,-value);}}
void pulse(int channel,int us){ledcWrite(channel,(uint32_t)us*65536UL/20000UL);}
void motion(void*){
 esp_task_wdt_add(nullptr);r2::Ramp ramps[3];TickType_t wake=xTaskGetTickCount();
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
  bool powered=digitalRead(pins::POWER)==HIGH;
  bool good=powered&&battery&&digitalRead(pins::FAULT)==HIGH&&fsReady;
  portENTER_CRITICAL(&mutex);healthy=good;volts=filtered;controller.tick(now,good);
  bool armed=controller.armed;r2::Command command=controller.command;portEXIT_CRITICAL(&mutex);
  r2::Mix target=r2::mix(command);
  if(armed){float delta=target.angle-angle;angle+=constrain(delta,-.3f,.3f);
   // Let the steering settle before driving. Recenter/reversal never bypasses this gate.
   int outputs[3]={target.left,target.right,target.rear};bool aligned=fabsf(target.angle-angle)<2;
   for(int i=0;i<3;i++)motor(i,ramps[i].tick(aligned?outputs[i]:0,now)*calibration::DIRECTION[i]);
   digitalWrite(pins::SLEEP,HIGH);
  }else{digitalWrite(pins::SLEEP,LOW);for(int i=0;i<3;i++){motor(i,0);ramps[i].stop();}}
  if(powered){pulse(6,constrain((int)(calibration::STEER_CENTER_US+angle*calibration::STEER_US_PER_DEGREE),1100,1900));
   pulse(7,calibration::HEAD_NEUTRAL_US+(armed?command.head*calibration::HEAD_DELTA_US/100:0));
  }else{ledcWrite(6,0);ledcWrite(7,0);}
  esp_task_wdt_reset();vTaskDelayUntil(&wake,pdMS_TO_TICKS(10));
 }
}
bool number(const char *key,long low,long high,long &v){return server.hasArg(key)&&r2::parse(server.arg(key).c_str(),low,high,v);}
void routes(){
 server.on("/",HTTP_GET,[]{File f=LittleFS.open("/index.html");server.sendHeader("Cache-Control","no-store");server.streamFile(f,"text/html");f.close();});
 server.on("/app.js",HTTP_GET,[]{File f=LittleFS.open("/app.js");server.sendHeader("Cache-Control","no-store");server.streamFile(f,"application/javascript");f.close();});
 server.on("/api/status",HTTP_GET,[]{portENTER_CRITICAL(&mutex);bool a=controller.armed,h=healthy&&ready;float v=volts;portEXIT_CRITICAL(&mutex);
  server.sendHeader("Cache-Control","no-store");server.send(200,"application/json",String("{\"armed\":")+(a?"true":"false")+",\"healthy\":"+(h?"true":"false")+",\"volts\":"+String(v,2)+"}");});
 server.on("/api/arm",HTTP_POST,[]{uint32_t token=esp_random()&0x7fffffff;if(!token)token=1;
  portENTER_CRITICAL(&mutex);bool ok=controller.arm(millis(),token,healthy&&ready);portEXIT_CRITICAL(&mutex);
  server.send(ok?200:409,"application/json",ok?String("{\"lease\":")+String(token)+"}":"{\"error\":\"Check RUN switch, battery and faults\"}");});
 server.on("/api/stop",HTTP_POST,[]{stop();server.send(200,"text/plain","Stopped");});
 server.on("/api/command",HTTP_POST,[]{long token,seq,speed,turn,head;
  if(!number("lease",1,2147483647,token)||!number("seq",1,2147483647,seq)||!number("speed",-100,100,speed)||!number("turn",-100,100,turn)||!number("head",-100,100,head)){stop();server.send(400,"text/plain","Invalid command");return;}
  r2::Command c;c.speed=speed;c.turn=turn;c.head=head;
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
 ledcSetup(6,50,16);ledcSetup(7,50,16);ledcAttachPin(pins::STEER,6);ledcAttachPin(pins::HEAD,7);ledcWrite(6,0);ledcWrite(7,0);
 pinMode(pins::FAULT,INPUT);pinMode(pins::POWER,INPUT);pinMode(pins::PACK,INPUT);analogSetPinAttenuation(pins::PACK,ADC_11db);
 Serial.begin(115200);fsReady=LittleFS.begin(false);
 audioOut.SetPinout(pins::BCLK,pins::LRCLK,pins::AUDIO);audioOut.SetGain(.22f);
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
