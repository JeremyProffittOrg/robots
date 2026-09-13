'use strict';
const names=['Hello','Curious','Happy','Concerned','Agree','Disagree','Excited','Sleepy','Thinking','Surprised','Searching','Playful','Low energy','Ready','Goodbye','Long story'];
const stanceLabels={THREE_FOOT:'Three feet',TWO_FOOT:'Two feet',DEPLOYING:'Deploying centre foot',RETRACTING:'Retracting centre foot',HELD:'Held between stances',FAULT:'FAULT',STARTING:'Starting'};
let lease=0,seq=0,drive=0,head=0,stance=-1,pending=false,generation=0,status=null;
const $=id=>document.getElementById(id);
const controls=[...document.querySelectorAll('[data-speed],[data-head],[data-stance]')];
async function post(path,data={}){const c=new AbortController(),t=setTimeout(()=>c.abort(),350);try{const r=await fetch(path,{method:'POST',body:new URLSearchParams(data),signal:c.signal});if(!r.ok)throw Error(await r.text());return r;}finally{clearTimeout(t);}}
function reset(){lease=0;drive=0;head=0;stance=-1;generation++;}
function stop(){reset();post('/api/stop').catch(()=>{});}
// Steering is only sent while ground drive is allowed; stance commands always carry zero drive, turn and head.
function turnValue(){return stance<0&&status&&status.drive_allowed?$('turn').value:0;}
async function send(){if(!lease||pending)return;pending=true;const g=generation;try{await post('/api/command',{lease,seq:++seq,speed:drive*Number($('speed').value),turn:turnValue(),head:head*60,stance});}catch(e){if(g===generation){reset();$('status').textContent='Stopped: '+(e.message||'connection lost')+'. Arm again.';}}finally{pending=false;}}
$('arm').onclick=async()=>{reset();const g=generation;try{const r=await post('/api/arm'),j=await r.json();if(g!==generation){post('/api/stop').catch(()=>{});return;}lease=j.lease;seq=0;await send();}catch(e){$('status').textContent=e.message;}};
$('stop').onclick=stop;
$('clear').onclick=async()=>{if(!lease){$('fault').textContent='Arm first, then clear the fault.';return;}try{await post('/api/stance/clear',{lease});$('fault').textContent='Fault cleared.';}catch(e){$('fault').textContent=e.message;}};
for(const b of controls){
 b.onpointerdown=e=>{if(!lease||b.disabled)return;e.preventDefault();b.setPointerCapture(e.pointerId);
  if(b.dataset.stance!==undefined){drive=0;head=0;stance=Number(b.dataset.stance);$('turn').value=0;$('turnLabel').textContent='0°';}
  else{stance=-1;if(b.dataset.speed)drive=Number(b.dataset.speed);else head=Number(b.dataset.head);}send();};
 const release=()=>{if(b.dataset.stance!==undefined)stance=-1;else if(b.dataset.speed)drive=0;else head=0;send();};
 b.onpointerup=release;b.onpointercancel=stop;b.onlostpointercapture=release;
}
function render(s){
 status=s;
 $('status').textContent=`${s.volts.toFixed(1)} V · ${s.armed?'Armed':s.healthy?'Ready to arm':'Check RUN power / battery'}`;
 const moving=s.stance==='DEPLOYING'||s.stance==='RETRACTING';
 $('stanceState').textContent=`${stanceLabels[s.stance]||s.stance}${s.phase&&s.phase!=='NONE'?' · '+s.phase:''} · ${s.reason}`;
 $('pose').textContent=`Post ${s.post_mm===null?'unavailable':s.post_mm.toFixed(1)+' mm'} · lock ${!s.lock_valid?'sensor invalid':s.lock_engaged?'engaged':'released'}${s.limits_closed?'':' · travel limit open'} · pitch ${s.pitch_deg===null?'unknown':s.pitch_deg.toFixed(1)+'°'} (${s.pitch_source})`;
 $('fault').textContent=s.stance==='FAULT'?`Fault ${s.fault}: ${s.reason}`:'';
 const blocks=[];
 for(const b of controls){
  if(b.dataset.stance!==undefined){
   const two=b.dataset.stance==='2',ok=two?s.can_two_foot:s.can_three_foot,why=two?s.two_foot_block:s.three_foot_block;
   b.disabled=!(ok||(moving&&stance===Number(b.dataset.stance)));
   if(b.disabled&&why)blocks.push(`${two?'Two feet':'Three feet'}: ${why}`);
  }else if(b.dataset.speed)b.disabled=!s.drive_allowed&&drive===0;
  else b.disabled=!s.head_allowed&&head===0;
 }
 $('stanceBlocks').textContent=blocks.join(' · ');
 $('driveNote').textContent=s.drive_allowed?'':'Driving is available only on three feet with the lock engaged.';
 $('clear').disabled=s.stance!=='FAULT';
 if(!s.drive_allowed&&$('turn').value!=='0'){$('turn').value=0;$('turnLabel').textContent='0°';}
 if(!s.armed&&lease)reset();
}
window.addEventListener('blur',stop);document.addEventListener('visibilitychange',()=>{if(document.hidden)stop();});window.addEventListener('pagehide',()=>{reset();navigator.sendBeacon('/api/stop');});
$('speed').oninput=()=>{$('speedLabel').textContent=$('speed').value+'%';};
$('turn').oninput=()=>{$('turnLabel').textContent=(Number($('turn').value)*.08).toFixed(1)+'°';};
$('center').onclick=()=>{$('turn').value=0;$('turn').oninput();};
names.forEach((name,i)=>{const o=document.createElement('option');o.value=i+1;o.textContent=name;$('sound').append(o);});
$('play').onclick=()=>post('/api/sound',{id:$('sound').value}).catch(e=>{$('status').textContent=e.message;});
setInterval(send,100);
setInterval(async()=>{try{const r=await fetch('/api/status',{cache:'no-store',signal:AbortSignal.timeout(500)});render(await r.json());}catch(e){stop();$('status').textContent='Disconnected. The motion lease expires after 0.5 seconds.';}},1000);
