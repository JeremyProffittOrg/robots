'use strict';
// Execute the real phone code with a small simulated DOM and network.
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const elements=new Map(),intervals=new Map(),events=new Map(),requests=[];
function element(id){if(!elements.has(id))elements.set(id,{id,value:({speed:'35',turn:'0',sound:'1'})[id]||'',textContent:'',disabled:false,dataset:{},append(){},setPointerCapture(){}});return elements.get(id);}
const buttons=[{speed:'1'},{speed:'-1'},{head:'-1'},{head:'1'},{stance:'2'},{stance:'3'}].map(dataset=>({dataset,disabled:true,setPointerCapture(){}}));
const [forward,,headLeft,,twoFoot,threeFoot]=buttons;
let armed=false,token=100,fail=false,deferred=null,refuse=null;
const base={healthy:true,volts:12.8,post_mm:98.1,lock_valid:true,lock_engaged:true,limits_closed:true,pitch_deg:13.0,pitch_source:'three-foot post kinematics',fault:'NONE',phase:'NONE'};
let robot={...base,stance:'THREE_FOOT',reason:'on three feet',drive_allowed:true,head_allowed:true,can_two_foot:true,can_three_foot:false,two_foot_block:null,three_foot_block:'already on three feet'};
const context=vm.createContext({console,URLSearchParams,AbortController,AbortSignal,
 document:{hidden:false,getElementById:element,querySelectorAll:()=>buttons,createElement:()=>({}),addEventListener:(k,f)=>events.set(k,f)},
 window:{addEventListener:(k,f)=>events.set(k,f)},navigator:{sendBeacon:()=>{armed=false;}},
 setInterval:(f,ms)=>intervals.set(ms,f),setTimeout:()=>1,clearTimeout(){},
 fetch:async(url,options={})=>{const body=options.body?Object.fromEntries(options.body):{};requests.push({url,body});let value={};
  if(url.endsWith('/arm')){armed=true;value={lease:++token};if(deferred)await new Promise(resolve=>{deferred.resolve=resolve;});}
  if(url.endsWith('/stop'))armed=false;
  if(url.endsWith('/command')&&fail)throw Error('disconnected');
  if(url.endsWith('/command')&&refuse)return {ok:false,text:async()=>refuse,json:async()=>({})};
  if(url.endsWith('/status'))value={...robot,armed};
  return {ok:true,text:async()=>'OK',json:async()=>value};}});
vm.runInContext(fs.readFileSync(path.join(__dirname,'../data/app.js'),'utf8'),context);
const state=s=>vm.runInContext(s,context),settle=async()=>{for(let i=0;i<15;i++)await Promise.resolve();};
const commands=()=>requests.filter(r=>r.url.endsWith('/command'));
const last=()=>commands().at(-1).body;
const poll=async()=>{await intervals.get(1000)();await settle();};
const press=async(b,id=1)=>{b.onpointerdown({preventDefault(){},pointerId:id});await settle();};
(async()=>{
 // Controls stay disabled until the robot reports its stance.
 await element('arm').onclick();assert.equal(last().speed,'0');assert.equal(last().stance,'-1');
 const before=commands().length;await press(twoFoot);assert.equal(commands().length,before,'disabled stance button sends nothing');
 await poll();
 assert.equal(forward.disabled,false);assert.equal(twoFoot.disabled,false);assert.equal(threeFoot.disabled,true);
 assert.match(element('stanceBlocks').textContent,/Three feet: already on three feet/);assert.equal(element('clear').disabled,true);
 // Driving on three feet.
 await press(forward);assert.equal(last().speed,'35');assert.deepEqual(Object.keys(last()).sort(),['head','lease','seq','speed','stance','turn']);
 forward.onpointerup();await settle();assert.equal(last().speed,'0');
 await press(headLeft);assert.equal(last().head,'-60');
 headLeft.onpointercancel();await settle();assert.equal(state('lease'),0);assert.equal(armed,false);
 await poll();assert.equal(state('lease'),0,'no automatic re-arm');
 // Stance request: zero drive, turn and head, even with the steering slider set.
 await element('arm').onclick();element('turn').value='50';
 await press(twoFoot,2);assert.equal(last().stance,'2');assert.equal(last().speed,'0');assert.equal(last().head,'0');assert.equal(last().turn,'0');
 robot={...base,stance:'RETRACTING',phase:'TILT',reason:'retracting to two-foot stance',drive_allowed:false,head_allowed:false,can_two_foot:false,can_three_foot:false,two_foot_block:'stance change in progress',three_foot_block:'release the active stance control first'};
 await poll();
 assert.equal(twoFoot.disabled,false,'the held stance button stays enabled during its own change');
 assert.equal(threeFoot.disabled,true);assert.equal(forward.disabled,true);assert.equal(headLeft.disabled,true);
 assert.match(element('stanceState').textContent,/Retracting centre foot · TILT/);
 const during=commands().length;await press(forward,3);assert.equal(commands().length,during,'drive refused during a transition');assert.equal(state('drive'),0);
 twoFoot.onpointerup();await settle();assert.equal(last().stance,'-1');
 // Two-foot stance: drive disabled, head allowed, steering forced to zero.
 robot={...base,post_mm:2.0,pitch_deg:0,pitch_source:'shoulder lock geometry',stance:'TWO_FOOT',reason:'standing on two feet',drive_allowed:false,head_allowed:true,can_two_foot:false,can_three_foot:true,two_foot_block:'already standing on two feet',three_foot_block:null};
 element('turn').value='40';await poll();
 assert.equal(forward.disabled,true);assert.equal(headLeft.disabled,false);assert.equal(threeFoot.disabled,false);assert.equal(twoFoot.disabled,true);
 assert.equal(element('turn').value,0);await intervals.get(100)();await settle();assert.equal(last().turn,'0');
 assert.match(element('pose').textContent,/pitch 0\.0° \(shoulder lock geometry\)/);
 assert.match(element('driveNote').textContent,/three feet/);
 // A refused command (for example a race with a stance change) disarms the phone.
 refuse='Drive refused in stance TWO_FOOT';await intervals.get(100)();await settle();assert.equal(state('lease'),0);
 assert.match(element('status').textContent,/Drive refused/);refuse=null;
 // Fault: reason shown, clear enabled and sent with the lease after re-arming.
 robot={...base,post_mm:null,pitch_deg:null,pitch_source:'unknown',lock_engaged:false,stance:'FAULT',fault:'LOCK_TIMEOUT',reason:'post passed the lock position but lock sensor not engaged',drive_allowed:false,head_allowed:false,can_two_foot:false,can_three_foot:false,two_foot_block:'fault latched; clear it first',three_foot_block:'fault latched; clear it first'};
 await poll();
 assert.equal(element('clear').disabled,false);assert.match(element('fault').textContent,/LOCK_TIMEOUT/);
 assert.equal(twoFoot.disabled,true);assert.equal(threeFoot.disabled,true);
 assert.match(element('pose').textContent,/Post unavailable/);assert.match(element('pose').textContent,/pitch unknown/);
 await element('clear').onclick();assert.equal(requests.filter(r=>r.url.endsWith('/stance/clear')).length,0,'clear needs an armed lease');
 await element('arm').onclick();await element('clear').onclick();
 const clearRequest=requests.filter(r=>r.url.endsWith('/stance/clear')).at(-1);assert.equal(clearRequest.body.lease,String(state('lease')));
 element('stop').onclick();await settle();
 // Existing lease protections.
 robot={...base,stance:'THREE_FOOT',reason:'on three feet',drive_allowed:true,head_allowed:true,can_two_foot:true,can_three_foot:false,two_foot_block:null,three_foot_block:'already on three feet'};
 await element('arm').onclick();await poll();events.get('blur')();await settle();assert.equal(state('lease'),0);
 deferred={};const old=element('arm').onclick();await settle();element('stop').onclick();await settle();deferred.resolve();await old;assert.equal(state('lease'),0);assert.equal(armed,false);deferred=null;
 await element('arm').onclick();fail=true;await intervals.get(100)();assert.equal(state('lease'),0);fail=false;
 await poll();assert.equal(state('lease'),0);
 console.log('PASS: stance controls gated by interlocks, held button during its own change, drive refused in transitions and on two feet, fault display and lease-bound clear, release, cancel, blur, late arm response, disconnect and no automatic re-arm');
})().catch(e=>{console.error(e);process.exitCode=1;});
