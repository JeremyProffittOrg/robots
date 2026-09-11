'use strict';
const $ = id => document.getElementById(id);
let token = '', lease = 0, sequence = 0, generation = 0;
let activePointer = null, held = '', pending = false, commandAbort = null;
const driveNames = ['forward', 'left', 'right', 'reverse', 'animate'];
const drive = {forward:[110,110], reverse:[-90,-90], left:[50,120], right:[120,50], animate:[0,0]};

function message(text) { $('message').textContent = text; }
function updateButtons() {
  $('arm').disabled = Boolean(lease);
  for (const id of driveNames) $(id).disabled = !lease;
}
async function api(path, data, signal) {
  const options = {method:data === undefined ? 'GET' : 'POST', headers:{'X-Dalek-Token':token}, cache:'no-store', signal};
  if (data !== undefined) options.body = new URLSearchParams(data);
  const response = await fetch('/api/' + path, options);
  const body = await response.json();
  if (!response.ok) throw new Error(body.error || ('HTTP ' + response.status));
  return body;
}
function localStop() {
  ++generation;
  lease = 0; sequence = 0; activePointer = null; held = '';
  if (commandAbort) commandAbort.abort();
  for (const id of driveNames) $(id).classList.remove('held');
  updateButtons();
}
function stop() {
  localStop();
  if (token) api('stop', {}).catch(() => message('Connection lost. The robot command timeout will disarm motion.'));
}

// Each request contains a fresh snapshot. No retry queue and no motion command cache.
async function heartbeat() {
  if (!lease || pending) return;
  if (document.hidden || !document.hasFocus()) { stop(); return; }
  const epoch = generation;
  const wheels = held ? drive[held] : [0,0];
  const command = {lease, sequence:++sequence, left:wheels[0], right:wheels[1],
    head:held ? Number($('head').value) : 0,
    arms:held && $('arms').checked ? 1 : 0,
    radius:Number($('radius').value), frequency:Number($('frequency').value)};
  pending = true;
  commandAbort = new AbortController();
  const timeout = setTimeout(() => commandAbort?.abort(), 300);
  try { await api('command', command, commandAbort.signal); }
  catch (error) {
    if (epoch === generation) { stop(); message('Motion stopped: ' + error.message + '. Release controls, then arm again.'); }
  } finally { clearTimeout(timeout); pending = false; commandAbort = null; }
}

$('loginForm').addEventListener('submit', async event => {
  event.preventDefault();
  try {
    const result = await api('login', {key:$('key').value.toUpperCase()});
    $('key').value = ''; token = result.token;
    $('loginSection').classList.add('hidden'); $('controls').classList.remove('hidden');
    message('Connected. Controls are disarmed.');
    await api('stop', {});
    const sounds = await api('sounds');
    $('sound').replaceChildren(...sounds.sort().map(name => { const option = document.createElement('option'); option.value = name; option.textContent = name.replace(/\.mp3$/, '').replace(/_/g,' '); return option; }));
    await status();
  } catch (error) { message(error.message); }
});
$('arm').addEventListener('click', async () => {
  const epoch = ++generation;
  $('arm').disabled = true;
  try {
    const result = await api('arm', {});
    if (epoch !== generation || document.hidden || !document.hasFocus()) { stop(); return; }
    lease = result.lease; sequence = 0; held = ''; activePointer = null;
    updateButtons(); message('Armed. Hold a control to move.'); await heartbeat();
  } catch (error) { localStop(); message(error.message); }
});
$('stop').addEventListener('click', stop);
for (const name of driveNames) {
  const button = $(name);
  button.addEventListener('contextmenu', event => event.preventDefault());
  button.addEventListener('pointerdown', event => {
    if (!lease || activePointer !== null || (event.pointerType === 'mouse' && event.button !== 0)) return;
    event.preventDefault(); activePointer = event.pointerId; held = name;
    button.setPointerCapture(event.pointerId); button.classList.add('held'); heartbeat();
  });
  for (const type of ['pointerup','pointercancel','lostpointercapture']) button.addEventListener(type, event => {
    if (event.pointerId === activePointer) stop();
  });
  button.addEventListener('keydown', event => { if (event.key === ' ' || event.key === 'Enter') event.preventDefault(); });
}
window.addEventListener('blur', stop);
window.addEventListener('pagehide', () => {
  localStop();
  if (token) fetch('/api/stop', {method:'POST', headers:{'X-Dalek-Token':token}, keepalive:true}).catch(() => {});
});
document.addEventListener('visibilitychange', () => { if (document.hidden) stop(); });
window.addEventListener('keydown', event => { if (event.key === 'Escape') stop(); });
for (const id of ['radius','frequency','head']) $(id).addEventListener('input', () => {
  $(id + 'Value').textContent = id === 'frequency' ? (Number($(id).value)/100).toFixed(2) : $(id).value;
});
$('play').addEventListener('click', () => api('sound', {name:$('sound').value}).catch(error => message(error.message)));
$('silence').addEventListener('click', () => api('silence', {}).catch(error => message(error.message)));
$('wifiForm').addEventListener('submit', async event => {
  event.preventDefault(); stop();
  try { const result = await api('wifi', {ssid:$('ssid').value, password:$('password').value}); $('password').value = ''; message(result.message); }
  catch (error) { message(error.message); }
});
$('forget').addEventListener('click', async () => {
  stop();
  try { await api('wifi/forget', {}); message('Saved network removed. Connect through the DALEK access point.'); }
  catch (error) { message(error.message); }
});
async function status() {
  if (!token) return;
  try {
    const state = await api('status');
    if (lease && !state.armed) localStop();
    const faults = [!state.power && 'actuator power off', !state.i2c && 'PCA9685 fault: fix then reboot', !state.battery && 'battery interlock', !state.filesystem && 'audio/filesystem missing'].filter(Boolean);
    $('status').textContent = `${state.armed ? 'ARMED' : 'DISARMED'} · ${state.volts.toFixed(2)} V · ${faults.length ? faults.join(' · ') : 'Ready'} · Network ${state.station}`;
  } catch (error) { if (lease) stop(); $('status').textContent = 'Robot connection lost. Controls are disarmed.'; }
}
setInterval(heartbeat, 100);
setInterval(status, 1000);
updateButtons();
