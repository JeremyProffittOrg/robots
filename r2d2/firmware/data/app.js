'use strict';
const names=['Hello','Curious','Happy','Concerned','Agree','Disagree','Excited','Sleepy','Thinking','Surprised','Searching','Playful','Low energy','Ready','Goodbye','Long story'];
let lease=0,seq=0,drive=0,head=0,pending=false,generation=0;
const $=id=>document.getElementById(id);
async function post(path,data={}){const c=new AbortController(),t=setTimeout(()=>c.abort(),350);try{const r=await fetch(path,{method:'POST',body:new URLSearchParams(data),signal:c.signal});if(!r.ok)throw Error(await r.text());return r;}finally{clearTimeout(t);}}
function reset(){lease=0;drive=0;head=0;generation++;}
function stop(){reset();post('/api/stop').catch(()=>{});}
async function send(){if(!lease||pending)return;pending=true;const g=generation;try{await post('/api/command',{lease,seq:++seq,speed:drive*Number($('speed').value),turn:$('turn').value,head:head*60});}catch(e){if(g===generation){reset();$('status').textContent='Stopped: connection lost. Arm again.';}}finally{pending=false;}}
$('arm').onclick=async()=>{reset();const g=generation;try{const r=await post('/api/arm'),j=await r.json();if(g!==generation){post('/api/stop').catch(()=>{});return;}lease=j.lease;seq=0;await send();}catch(e){$('status').textContent=e.message;}};
$('stop').onclick=stop;
for(const b of document.querySelectorAll('[data-speed],[data-head]')){
 b.onpointerdown=e=>{if(!lease)return;e.preventDefault();b.setPointerCapture(e.pointerId);if(b.dataset.speed)drive=Number(b.dataset.speed);else head=Number(b.dataset.head);send();};
 b.onpointerup=()=>{if(b.dataset.speed)drive=0;else head=0;send();};b.onpointercancel=stop;b.onlostpointercapture=()=>{if(b.dataset.speed)drive=0;else head=0;send();};
}
window.addEventListener('blur',stop);document.addEventListener('visibilitychange',()=>{if(document.hidden)stop();});window.addEventListener('pagehide',()=>{reset();navigator.sendBeacon('/api/stop');});
$('speed').oninput=()=>{$('speedLabel').textContent=$('speed').value+'%';};
$('turn').oninput=()=>{$('turnLabel').textContent=(Number($('turn').value)*.25).toFixed(1)+'°';};
$('center').onclick=()=>{$('turn').value=0;$('turn').oninput();};
names.forEach((name,i)=>{const o=document.createElement('option');o.value=i+1;o.textContent=name;$('sound').append(o);});
$('play').onclick=()=>post('/api/sound',{id:$('sound').value}).catch(e=>{$('status').textContent=e.message;});
setInterval(send,100);
setInterval(async()=>{try{const r=await fetch('/api/status',{cache:'no-store',signal:AbortSignal.timeout(500)});const s=await r.json();$('status').textContent=`${s.volts.toFixed(1)} V · ${s.armed?'Armed':s.healthy?'Ready to arm':'Check RUN power / battery / fault'}`;if(!s.armed&&lease)reset();}catch(e){stop();$('status').textContent='Disconnected. Robot stops within 0.5 seconds.';}},1000);
