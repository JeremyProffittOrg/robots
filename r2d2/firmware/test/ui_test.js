'use strict';
// Execute the real phone code with a small simulated DOM and network.
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const elements=new Map(),intervals=new Map(),events=new Map(),requests=[];
function element(id){if(!elements.has(id))elements.set(id,{value:({speed:'35',turn:'0',sound:'1'})[id]||'',textContent:'',dataset:{},append(){},setPointerCapture(){}});return elements.get(id);}
const buttons=[{speed:'1'},{speed:'-1'},{head:'-1'},{head:'1'},{posture:'0'},{posture:'100'}].map(dataset=>({dataset,setPointerCapture(){}}));
let armed=false,token=100,fail=false,deferred=null;
const context=vm.createContext({console,URLSearchParams,AbortController,AbortSignal,
 document:{hidden:false,getElementById:element,querySelectorAll:()=>buttons,createElement:()=>({}),addEventListener:(k,f)=>events.set(k,f)},
 window:{addEventListener:(k,f)=>events.set(k,f)},navigator:{sendBeacon:()=>{armed=false;}},
 setInterval:(f,ms)=>intervals.set(ms,f),setTimeout:()=>1,clearTimeout(){},
 fetch:async(url,options={})=>{const body=options.body?Object.fromEntries(options.body):{};requests.push({url,body});let value={};
  if(url.endsWith('/arm')){armed=true;value={lease:++token};if(deferred)await new Promise(resolve=>{deferred.resolve=resolve;});}
  if(url.endsWith('/stop'))armed=false;
  if(url.endsWith('/command')&&fail)throw Error('disconnected');
  if(url.endsWith('/status'))value={armed,healthy:true,volts:12.8,post_mm:5.04,estimated_tilt:0,post_status:'stopped'};
  return {ok:true,json:async()=>value};}});
vm.runInContext(fs.readFileSync(path.join(__dirname,'../data/app.js'),'utf8'),context);
const state=s=>vm.runInContext(s,context),settle=async()=>{for(let i=0;i<15;i++)await Promise.resolve();};
const last=()=>requests.filter(r=>r.url.endsWith('/command')).at(-1).body;
(async()=>{
 await element('arm').onclick();assert.equal(last().speed,'0');assert.equal(last().head,'0');
 buttons[0].onpointerdown({preventDefault(){},pointerId:1});await settle();assert.equal(last().speed,'35');assert.deepEqual(Object.keys(last()).sort(),['head','lease','posture','seq','speed','turn']);
 buttons[0].onpointerup();await settle();assert.equal(last().speed,'0');
 buttons[2].onpointerdown({preventDefault(){},pointerId:1});await settle();assert.equal(last().head,'-60');
 buttons[2].onpointercancel();await settle();assert.equal(state('lease'),0);assert.equal(armed,false);
 await intervals.get(1000)();assert.equal(state('lease'),0);
 await element('arm').onclick();element('turn').value='50';buttons[5].onpointerdown({preventDefault(){},pointerId:2});await settle();assert.equal(last().posture,'100');assert.equal(last().speed,'0');assert.equal(last().head,'0');assert.equal(last().turn,'0');buttons[5].onpointerup();await settle();assert.equal(last().posture,'-1');element('stop').onclick();await settle();
 await element('arm').onclick();events.get('blur')();await settle();assert.equal(state('lease'),0);
 deferred={};const old=element('arm').onclick();await settle();element('stop').onclick();await settle();deferred.resolve();await old;assert.equal(state('lease'),0);assert.equal(armed,false);deferred=null;
 await element('arm').onclick();fail=true;await intervals.get(100)();assert.equal(state('lease'),0);fail=false;
 await intervals.get(1000)();assert.equal(state('lease'),0);
 console.log('PASS: fresh commands, release, cancel, blur, late arm response, disconnect and no automatic re-arm');
})().catch(e=>{console.error(e);process.exitCode=1;});
