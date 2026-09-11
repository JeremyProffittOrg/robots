'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');

const elements = new Map();
function element(id) {
  if (!elements.has(id)) elements.set(id, {
    value:({key:'ABCDEFGHIJKL', radius:'8', frequency:'40', head:'0'})[id] || '',
    checked:false, disabled:false, handlers:new Map(), textContent:'',
    classList:{add(){}, remove(){}}, setPointerCapture(){}, replaceChildren(){},
    addEventListener(type, handler) { this.handlers.set(type, handler); }
  });
  return elements.get(id);
}
const windowHandlers = new Map(), documentHandlers = new Map();
const intervals = new Map(), timeouts = new Map(), requests = [];
let timeoutId = 0, robotArmed = false, nextLease = 101, deferArm = null, failCommand = false;
const context = vm.createContext({
  URLSearchParams, AbortController, console,
  document:{hidden:false, hasFocus:() => true, getElementById:element,
    createElement:() => element('option'), addEventListener:(type, handler) => documentHandlers.set(type,handler)},
  window:{addEventListener:(type, handler) => windowHandlers.set(type,handler)},
  setInterval:(fn, ms) => intervals.set(ms,fn),
  setTimeout:(fn) => { timeouts.set(++timeoutId,fn); return timeoutId; },
  clearTimeout:id => timeouts.delete(id),
  fetch:async (url, options) => {
    const body = options.body ? Object.fromEntries(options.body) : {};
    requests.push({url, body});
    let result = {};
    if (url.endsWith('/login')) result = {token:'test-token'};
    if (url.endsWith('/stop')) robotArmed = false;
    if (url.endsWith('/arm')) {
      robotArmed = true; result = {lease:nextLease++};
      if (deferArm) await new Promise(resolve => { deferArm.resolve = resolve; });
    }
    if (url.endsWith('/command') && failCommand) throw new Error('network disconnected');
    if (url.endsWith('/sounds')) result = ['ready.mp3'];
    if (url.endsWith('/status')) result = {armed:robotArmed, volts:12.9, power:true, i2c:true, battery:true, filesystem:true, station:'192.0.2.1'};
    return {ok:true, json:async () => result};
  }
});
vm.runInContext(fs.readFileSync(path.join(__dirname, '../data/app.js'), 'utf8'), context);
const state = expression => vm.runInContext(expression, context);
const event = (overrides = {}) => ({preventDefault(){}, pointerId:1, pointerType:'touch', button:0, ...overrides});
const emit = async (id, type, value = event()) => {
  await element(id).handlers.get(type)(value);
  await settle();
};
const settle = async () => { for (let i=0;i<12;i++) await Promise.resolve(); };
const commands = () => requests.filter(request => request.url.endsWith('/command'));

(async () => {
  await emit('loginForm', 'submit');
  assert.equal(state('lease'), 0);
  assert.equal(robotArmed, false);
  await emit('arm', 'click');
  const firstLease = state('lease');
  assert.equal(commands().at(-1).body.left, '0');
  assert.equal(commands().at(-1).body.head, '0');
  await emit('forward', 'pointerdown');
  assert.equal(commands().at(-1).body.left, '110');
  element('head').value = '30'; element('arms').checked = true;
  await intervals.get(100)();
  assert.equal(commands().at(-1).body.head, '30');
  assert.equal(commands().at(-1).body.arms, '1');
  assert.deepEqual(Object.keys(commands().at(-1).body).sort(), ['arms','frequency','head','lease','left','radius','right','sequence']);
  await emit('forward', 'pointercancel');
  assert.equal(state('lease'), 0);
  assert.equal(robotArmed, false);
  const stoppedCount = commands().length;
  await intervals.get(100)();
  assert.equal(commands().length, stoppedCount);
  await intervals.get(1000)(); // Reconnected status must not arm.
  assert.equal(state('lease'), 0);
  await emit('arm', 'click');
  assert.notEqual(state('lease'), firstLease);
  assert.equal(commands().at(-1).body.left, '0');
  assert.equal(commands().at(-1).body.head, '0');
  await emit('left', 'pointerdown');
  assert.equal(commands().at(-1).body.left, '50');
  assert.equal(commands().at(-1).body.right, '120');
  windowHandlers.get('blur')(); await settle();
  assert.equal(state('lease'), 0);
  deferArm = {};
  const armPending = emit('arm', 'click');
  await settle();
  await emit('stop', 'click');
  deferArm.resolve(); await armPending;
  assert.equal(state('lease'), 0); // A late arm reply cannot resume a cancelled session.
  assert.equal(robotArmed, false);
  deferArm = null;
  await emit('arm', 'click');
  failCommand = true;
  await emit('animate', 'pointerdown');
  assert.equal(state('lease'), 0);
  assert.equal(robotArmed, false);
  console.log('PASS: complete fresh commands, pointer cancel, blur, connection loss, late arm reply, no replay or auto-arm');
})().catch(error => { console.error(error); process.exitCode = 1; });
