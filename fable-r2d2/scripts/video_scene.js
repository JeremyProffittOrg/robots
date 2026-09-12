'use strict';
// fable-r2d2 assembly and simulated operation renderer.
// Every printed piece is the delivered STL, already transformed into the assembly frame by
// scripts/render_video.py using scripts/assembly_layout.py (the same placement cad/r2d2.scad
// uses). Left-hand pieces were re-wound in Python because their Layout matrix has a negative
// determinant. Purchased hardware is a nominal envelope built from cad/params.scad values.
// Nothing here connects to a robot, a printer or a network.

const W = 1920, H = 1080;
const VIEW_X = 0, VIEW_Y = 76, VIEW_W = 1400, VIEW_H = 930;
const PANEL_X = 1415, TX = 1450, TW = 442;

const output = document.getElementById('output');
output.width = W; output.height = H;
const ctx = output.getContext('2d');
const canvas = document.createElement('canvas');
canvas.width = W; canvas.height = H;
const gl = canvas.getContext('webgl2', { antialias: true, alpha: false, preserveDrawingBuffer: true });
if (!gl) throw new Error('WebGL2 is required');

const vs = `#version 300 es
layout(location=0) in vec3 position;layout(location=1) in vec3 normal;
uniform mat4 model;uniform mat4 vp;out vec3 n;out vec3 world;
void main(){vec4 p=model*vec4(position,1.);world=p.xyz;n=mat3(model)*normal;gl_Position=vp*p;}`;
const fs = `#version 300 es
precision highp float;in vec3 n;in vec3 world;
uniform vec3 color;uniform int cut;uniform mat4 cutM;uniform float emissive;
out vec4 frag;
void main(){
  vec3 c=(cutM*vec4(world,1.)).xyz;
  if(cut==1&&c.y>0.)discard;
  if(cut==2&&c.y<0.)discard;
  if(cut==3&&c.x>0.)discard;
  if(cut==4&&c.z>0.)discard;
  vec3 nn=normalize(n); if(!gl_FrontFacing) nn=-nn;
  float key=max(dot(nn,normalize(vec3(0.38,0.52,0.76))),0.);
  float fill=max(dot(nn,normalize(vec3(-0.62,-0.38,0.35))),0.);
  float light=0.30+0.62*key+0.20*fill;
  light=mix(light,1.0,clamp(emissive,0.,1.));
  frag=vec4(min(color*light,vec3(1.)),1.);
}`;
function shader(type, source) {
  const s = gl.createShader(type); gl.shaderSource(s, source); gl.compileShader(s);
  if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(s));
  return s;
}
const program = gl.createProgram();
gl.attachShader(program, shader(gl.VERTEX_SHADER, vs));
gl.attachShader(program, shader(gl.FRAGMENT_SHADER, fs));
gl.linkProgram(program);
if (!gl.getProgramParameter(program, gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(program));
const U = {};
for (const name of ['model', 'vp', 'color', 'cut', 'cutM', 'emissive']) U[name] = gl.getUniformLocation(program, name);
gl.useProgram(program); gl.enable(gl.DEPTH_TEST); gl.disable(gl.CULL_FACE);

// ---------- matrix helpers (column major, chain(A,B,C) = A*B*C) ----------
const I = () => [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1];
function mul(a, b) {
  const r = new Array(16).fill(0);
  for (let c = 0; c < 4; c++) for (let row = 0; row < 4; row++) for (let k = 0; k < 4; k++) r[c * 4 + row] += a[k * 4 + row] * b[c * 4 + k];
  return r;
}
const chain = (...m) => m.reduce(mul, I());
function T(x = 0, y = 0, z = 0) { const m = I(); m[12] = x; m[13] = y; m[14] = z; return m; }
function S(x = 1, y = 1, z = 1) { const m = I(); m[0] = x; m[5] = y; m[10] = z; return m; }
function RX(a) { const c = Math.cos(a), s = Math.sin(a); return [1, 0, 0, 0, 0, c, s, 0, 0, -s, c, 0, 0, 0, 0, 1]; }
function RY(a) { const c = Math.cos(a), s = Math.sin(a); return [c, 0, -s, 0, 0, 1, 0, 0, s, 0, c, 0, 0, 0, 0, 1]; }
function RZ(a) { const c = Math.cos(a), s = Math.sin(a); return [c, s, 0, 0, -s, c, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]; }
const radians = d => d * Math.PI / 180;
const degrees = r => r * 180 / Math.PI;
const clamp01 = v => Math.max(0, Math.min(1, v));
const smooth = (t, a, b) => { const v = clamp01((t - a) / (b - a)); return v * v * (3 - 2 * v); };
const lerp = (a, b, t) => a + (b - a) * t;
const lerp3 = (a, b, t) => [lerp(a[0], b[0], t), lerp(a[1], b[1], t), lerp(a[2], b[2], t)];
const norm = v => { const q = Math.hypot(...v); return v.map(x => x / q); };
const dot = (a, b) => a.reduce((v, x, i) => v + x * b[i], 0);
const cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
function lookAt(eye, target) {
  const z = norm(eye.map((v, i) => v - target[i])), x = norm(cross([0, 0, 1], z)), y = cross(z, x);
  return [x[0], y[0], z[0], 0, x[1], y[1], z[1], 0, x[2], y[2], z[2], 0, -dot(x, eye), -dot(y, eye), -dot(z, eye), 1];
}
function ortho(width, height, near = 1, far = 6000) {
  return [2 / width, 0, 0, 0, 0, 2 / height, 0, 0, 0, 0, -2 / (far - near), 0, 0, 0, -(far + near) / (far - near), 1];
}
const posOf = m => [m[12], m[13], m[14]];

// ---------- scene state ----------
let scene = null, story = null, P = null, F = null, CH = null;
const meshes = {};
let globalPose = I(), hero = false, shown = new Set(), labels = [], currentVP = I();
let cutNote = '', shotAz = 0;

// ---------- palette ----------
const C = {
  bodyLower: [0.93, 0.94, 0.95], bodyUpper: [0.90, 0.92, 0.94], dome: [0.80, 0.84, 0.88],
  leg: [0.95, 0.96, 0.97], foot: [0.85, 0.88, 0.91], drive: [0.42, 0.47, 0.53],
  steel: [0.70, 0.74, 0.78], gray: [0.55, 0.59, 0.63], dark: [0.16, 0.18, 0.21],
  motor: [0.88, 0.70, 0.14], tyre: [0.24, 0.26, 0.29], tread: [0.14, 0.15, 0.17],
  battery: [0.20, 0.22, 0.26], strap: [0.30, 0.33, 0.38], green: [0.13, 0.42, 0.26],
  blue: [0.14, 0.45, 0.72], red: [0.78, 0.16, 0.14], amber: [0.99, 0.72, 0.25],
  copper: [0.72, 0.45, 0.22], white: [0.96, 0.97, 0.98], lens: [0.11, 0.16, 0.24],
  brass: [0.78, 0.62, 0.25],
};
const partColour = { body_lower: C.bodyLower, body_upper: C.bodyUpper, dome: C.dome, head_drive: C.drive,
  leg_upper: C.leg, leg_lower: C.leg, leg_center: C.leg, foot_outer: C.foot, foot_center: C.foot };

// ---------- draw ----------
function draw(key, matrix, color, cut, cutM, emissive) {
  const mesh = meshes[key];
  if (!mesh) return;
  gl.bindVertexArray(mesh.vao);
  gl.uniformMatrix4fv(U.model, false, mul(globalPose, matrix));
  gl.uniform3fv(U.color, color);
  gl.uniform1i(U.cut, cut || 0);
  gl.uniformMatrix4fv(U.cutM, false, cutM || I());
  gl.uniform1f(U.emissive, emissive || 0);
  gl.drawArrays(gl.TRIANGLES, 0, mesh.count);
}
const box = (centre, size, color, extra) => draw('cube', chain(extra || I(), T(...centre), S(...size)), color);
const cyl = (centre, r, h, color, rot, extra) => draw('cylinder', chain(extra || I(), T(...centre), rot || I(), S(r, r, h)), color);
const disc = (centre, r, h, color, rot, extra) => draw('disc', chain(extra || I(), T(...centre), rot || I(), S(r, r, h)), color);
const ring = (centre, rOut, h, color, rot, extra, key) => draw(key || 'ring', chain(extra || I(), T(...centre), rot || I(), S(rOut, rOut, h)), color);
const lamp = (centre, r, h, color, rot, extra) => draw('disc', chain(extra || I(), T(...centre), rot || I(), S(r, r, h)), color, 0, null, 0.85);

function frameOffset(f, o) { return chain(f.m, T(o[0], o[1], o[2]), f.inv); }
function frameRotZ(f, a) { return chain(f.m, RZ(a), f.inv); }

// Visibility + arrival slide for one sub-assembly, expressed in a named frame's axes.
function fit(t, t0, t1, frameName, offset) {
  if (hero) return { show: true, m: I(), k: 0 };
  if (t < t0) return { show: false, m: I(), k: 1 };
  const k = 1 - smooth(t, t0, t1);
  const f = F[frameName] || F.world;
  return { show: true, k, m: k > 0 ? frameOffset(f, [offset[0] * k, offset[1] * k, offset[2] * k]) : I() };
}
function tint(base, t, t0, t1) {
  if (hero) return base;
  const w = t < t0 ? 0 : 1 - smooth(t, t1, t1 + 0.9);
  if (w <= 0) return base;
  return base.map((v, i) => lerp(v, C.amber[i], 0.55 * w));
}
function piece(name, t, t0, t1, frameName, offset, extra) {
  const part = (scene.printed.find(p => p.name === name) || {}).part;
  if (!part) return null;
  const state = fit(t, t0, t1, frameName, offset);
  if (!state.show) return null;
  const m = extra ? mul(state.m, extra) : state.m;
  shown.add(name);
  return { m, part, colour: tint(partColour[part] || C.white, t, t0, t1) };
}
function drawPiece(name, t, t0, t1, frameName, offset, extra, cut, cutM) {
  const s = piece(name, t, t0, t1, frameName, offset, extra);
  if (!s) return;
  draw('p_' + name, s.m, s.colour, cut, cutM);
}
const vis = (t, t0) => hero || t >= t0;

// ---------- cut planes ----------
// Half section through a point, normal to the current camera azimuth: the half of the part
// between the camera and that point is discarded, so the interior always faces the lens.
function sectionAt(x, y, bias) {
  const a = radians(shotAz);
  const offset = x * Math.cos(a) + y * Math.sin(a) + (bias || 0);
  return { mode: 3, m: chain(T(-offset, 0, 0), RZ(-a)) };
}
function bodyCut(t) {
  if (hero) return { mode: 0, m: I() };
  if (t >= 55 && t < 141) return sectionAt(0, 0, 6);
  return { mode: 0, m: I() };
}

// ---------- motion ----------
const FOOT_C_Y = () => P.skirt_bottom_y - P.caster_trail;
const TURN_R = 420, TURN_A = radians(75), FWD = 400, BACK = 150, WHEEL_R = 31.5;

function drive(t) {
  const ay = P.ankle_y, cy = FOOT_C_Y();
  let yaw = 0, refx = 0, refy = ay, dR = 0, dL = 0, dC = 0, caster = 0, action = 'STOPPED';
  if (!hero && t >= 149.6) {
    const forward = FWD * smooth(t, 149.6, 153.6);
    refy = ay + forward; dR = forward; dL = forward; dC = forward;
    const u2 = smooth(t, 153.6, 158.4);
    if (u2 > 0) {
      yaw = TURN_A * u2;
      const cxc = -TURN_R, cyc = ay + FWD;
      refx = cxc + TURN_R * Math.cos(yaw);
      refy = cyc + TURN_R * Math.sin(yaw);
      dR = FWD + (TURN_R + P.leg_offset_x) * yaw;
      dL = FWD + (TURN_R - P.leg_offset_x) * yaw;
      dC = FWD + Math.hypot(TURN_R, ay - cy) * yaw;
      caster = -Math.atan2(ay - cy, TURN_R) * u2;
    }
    const back = BACK * smooth(t, 159.2, 161.6);
    if (back > 0) {
      refx += Math.sin(yaw) * back;
      refy -= Math.cos(yaw) * back;
      dR -= back; dL -= back; dC -= back;
      caster *= 1 - smooth(t, 159.2, 160.8);
    }
    action = t < 153.6 ? 'FORWARD' : t < 158.4 ? 'LEFT ARC' : t < 159.2 ? 'STOP' : t < 161.6 ? 'REVERSE' : 'STOPPED';
  }
  return {
    x: refx + ay * Math.sin(yaw), y: refy - ay * Math.cos(yaw), yaw,
    yaw_deg: +degrees(yaw).toFixed(2), right: dR, left: dL, centre: dC, caster,
    caster_deg: +degrees(caster).toFixed(2), action,
    path_mm: +(Math.max(dR, dL) + Math.min(dR, dL)).toFixed(0) / 2,
  };
}
function domeMotion(t) {
  if (hero) return { spin: 0, spinning: false, nudge: false };
  if (t < 142.5) return { spin: 0, spinning: false, nudge: false };
  if (t < 162.2) return { spin: 2 * Math.PI * 0.35 * (t - 142.5), spinning: true, nudge: false };
  const held = 2 * Math.PI * 0.35 * (162.2 - 142.5);
  return { spin: held + radians(28) * Math.sin(2 * Math.PI * (t - 162.2) / 1.8) * (1 - smooth(t, 163.4, 164.0)), spinning: false, nudge: t < 164 };
}
function footLift(t) {
  if (hero || t >= 24.6) return 0;
  return 150 * (1 - smooth(t, 22.6, 24.6));
}
function casterDemo(t) {
  if (hero || t < 53 || t >= 55) return { angle: 0, active: false };
  return { angle: radians(P.caster_stop_deg * 0.92) * Math.sin(2 * Math.PI * (t - 53) / 2), active: true };
}
function lights(t) {
  const on = !hero && t >= 141.6;
  const phase = on ? (t - 141.6) : 0;
  return { on, phase };
}

// ---------- dome placement (bench -> seated) ----------
function domeFrame(t) {
  const rest = posOf(F.dome.m), tilt = radians(P.body_tilt);
  const lie = [420, -60, P.dome_r], up = [420, -60, 0];
  if (hero || t >= 138.6) return chain(T(...rest), RX(tilt), RZ(domeMotion(t).spin));
  if (t < 119.5) return chain(T(...lie), RX(-Math.PI / 2));
  if (t < 121.0) { const u = smooth(t, 119.5, 121.0); return chain(T(...lerp3(lie, up, u)), RX(lerp(-Math.PI / 2, 0, u))); }
  if (t < 132.5) return chain(T(...up), RX(0));
  const high = [up[0], up[1], 640], over = [rest[0], rest[1], rest[2] + 200];
  if (t < 134.2) { const u = smooth(t, 132.5, 134.2); return chain(T(...lerp3(up, high, u)), RX(lerp(0, tilt, u))); }
  if (t < 136.6) return chain(T(...lerp3(high, over, smooth(t, 134.2, 136.6))), RX(tilt));
  return chain(T(...lerp3(over, rest, smooth(t, 136.6, 138.6))), RX(tilt));
}

// ---------- floor ----------
function floorGrid() {
  draw('cube', chain(T(0, 300, -1.4), S(7600, 7600, 1)), [0.975, 0.982, 0.99]);
  for (let i = -3400; i <= 3400; i += 100) {
    draw('cube', chain(T(i, 300, -0.7), S(1.1, 7600, 0.1)), [0.845, 0.875, 0.912]);
    draw('cube', chain(T(0, i + 300, -0.7), S(7600, 1.1, 0.1)), [0.845, 0.875, 0.912]);
  }
}

// ---------- sub-assemblies ----------
function motorsAndWheels(t, pose, swivel) {
  const start = { r: 12.0, l: 12.4, c: 12.8 };
  const roll = { r: pose.right, l: pose.left, c: pose.centre };
  const lift = T(0, 0, footLift(t));
  const seat = key => (key === 'c' ? mul(lift, swivel) : lift);
  for (const m of scene.motors) {
    const state = fit(t, start[m.foot], start[m.foot] + 3.4, 'foot_' + m.foot, [0, 0, -140]);
    if (!state.show) continue;
    const base = chain(state.m, seat(m.foot), m.m);  // arrival * lift * caster swivel * envelope
    draw('motor', base, tint(C.motor, t, start[m.foot], start[m.foot] + 3.4));
    // two M3 tab bolts through the gearbox, fitted after the motor seats
    if (vis(t, 19)) {
      const bolts = fit(t, 19, 22.6, 'foot_' + m.foot, [0, 0, -40]);
      for (const x of [-8.8, 8.8]) {
        draw('bolt3', chain(bolts.m, seat(m.foot), m.m, T(x, -P.tt_thick / 2 - 2.6, 0), RX(Math.PI / 2),
          RZ(bolts.k * Math.PI * 8)), C.steel);
      }
    }
  }
  for (const w of scene.wheels) {
    const t0 = start[w.foot] + 3.0, t1 = t0 + 3.6;
    const state = fit(t, t0, t1, 'foot_' + w.foot, [0, 0, -170]);
    if (!state.show) continue;
    const angle = w.spin_sign * (-roll[w.foot] / WHEEL_R) + state.k * Math.PI * 3;
    const m = chain(state.m, seat(w.foot), w.m, RZ(angle));
    draw('wheel', m, tint(C.tyre, t, t0, t1));
    for (let j = 0; j < 6; j++) draw('wheel_mark', mul(m, RZ(j * Math.PI / 3)), C.tread);
  }
}

function feet(t, swivel) {
  const rise = footLift(t);
  const lift = T(0, 0, rise);
  if (rise > 2) {
    // assembly blocks: the three feet are held clear of the floor while the drives load in
    for (const [x, y, w, d] of [[P.leg_offset_x, P.ankle_y, 190, 250], [-P.leg_offset_x, P.ankle_y, 190, 250],
      [0, FOOT_C_Y(), 130, 190]]) {
      box([x, y, (rise + P.foot_clear) / 2], [w, d, rise + P.foot_clear], [0.73, 0.77, 0.81]);
    }
  }
  const cutR = sectionAt(P.leg_offset_x, P.ankle_y, -14);
  const cutC = sectionAt(0, FOOT_C_Y(), -14);
  const open = !hero && t < 25;
  drawPiece('foot_outer_right', t, 8.2, 11.0, 'foot_r', [0, 0, 260], lift, open ? cutR.mode : 0, cutR.m);
  drawPiece('foot_outer_left', t, 8.6, 11.4, 'foot_l', [0, 0, 260], lift);
  drawPiece('foot_center', t, 9.2, 12.0, 'foot_c', [0, 0, 260], mul(lift, swivel), open ? cutC.mode : 0, cutC.m);
  if (open && t >= 8) {
    cutNote = 'The right and centre feet are cut at a vertical plane, and all three are raised on blocks, so the two motors and four wheels that load through each sole stay visible.';
  }
}

function legs(t) {
  for (const [side, frame] of [['right', 'leg_r'], ['left', 'leg_l']]) {
    const d = side === 'right' ? 0 : 0.35;
    drawPiece('leg_lower_' + side, t, 25.5 + d, 29.0 + d, frame, [0, 0, 300]);
    drawPiece('leg_upper_' + side, t, 29.0 + d, 32.6 + d, frame, [0, 0, 340]);
    const f = F[frame];
    // two full-length M8 rods inside the strut
    const rods = fit(t, 32.6, 36.0, frame, [0, 0, 280]);
    if (rods.show) for (const y of [-P.leg_rod_offset, P.leg_rod_offset]) {
      const z0 = P.leg_rod_bottom_z, z1 = P.leg_rod_top_z;
      cyl([P.lg_rod_x, y, (z0 + z1) / 2], 4, z1 - z0, tint(C.steel, t, 32.6, 36.0), I(), mul(rods.m, f.m));
      draw('nut8', chain(rods.m, f.m, T(P.lg_rod_x, y, z1 + 3), RZ(rods.k * Math.PI * 10)), C.gray);
    }
    // four M4 splice bolts across the lap joint
    const splice = fit(t, 36.0, 38.5, frame, [0, 0, 0]);
    if (splice.show) for (const x of P.lg_splice_x) for (const z of P.lg_splice_z) {
      draw('bolt4l', chain(f.m, T(x, -42, z), RX(Math.PI / 2), RZ(splice.k * Math.PI * 12)), tint(C.steel, t, 36.0, 38.5));
      draw('nut4', chain(f.m, T(x, 40, z), RX(Math.PI / 2)), C.gray);
    }
    // ankle pivot and lock bolts, through the foot block
    const footFrame = F[side === 'right' ? 'foot_r' : 'foot_l'];
    const ankle = fit(t, 38.5, 41.6, side === 'right' ? 'foot_r' : 'foot_l', [0, 0, 0]);
    if (ankle.show) for (const [y, z] of [[0, P.ft_pivot_z], [P.ft_lock_r, P.ft_pivot_z - 25]]) {
      draw('bolt8m', chain(footFrame.m, T(33, y, z), RY(Math.PI / 2), RZ(ankle.k * Math.PI * 9)), tint(C.steel, t, 38.5, 41.6));
      draw('nut8', chain(footFrame.m, T(-31, y, z), RY(Math.PI / 2)), C.gray);
    }
  }
}

function centreLeg(t, swivel) {
  const fc = F.foot_c;
  // two caster bearings on the stem, then the printed centre leg over them
  const bearings = fit(t, 43.5, 46.5, 'center_leg', [0, 0, 150]);
  if (bearings.show) for (const z of [P.lg_bearing1_z, P.lg_bearing2_z]) {
    draw('bearing', chain(bearings.m, F.center_leg.m, T(0, 0, z)), tint(C.steel, t, 43.5, 46.5));
  }
  drawPiece('leg_center', t, 46.5, 50.0, 'center_leg', [0, 0, 210]);
  const bolt = fit(t, 50.0, 52.0, 'center_leg', [0, 0, 120]);
  if (bolt.show) {
    draw('bolt12', chain(bolt.m, F.center_leg.m, T(0, 0, 84), RZ(bolt.k * Math.PI * 10)), tint(C.steel, t, 50.0, 52.0));
    draw('nut12', chain(bolt.m, F.center_leg.m, T(0, 0, -52)), C.gray);
  }
  const pin = fit(t, 52.0, 53.0, 'foot_c', [0, 0, 60]);
  if (pin.show) cyl([P.ft_stop_r, P.caster_trail, P.foot_center_h + P.ft_pin_h / 2], P.ft_pin_d / 2, P.ft_pin_h, tint(C.gray, t, 52, 53), I(), mul(swivel, fc.m));
}

function bodyLower(t, cut) {
  drawPiece('body_lower', t, 55.8, 59.8, 'body', [0, 0, 300], null, cut.mode, cut.m);
  const b = F.body.m, tilt = radians(P.body_tilt);
  // four M8 bolts down through the centre-leg flange into the body floor
  const flange = fit(t, 59.8, 62.0, 'body', [0, 0, 60]);
  if (flange.show) for (const [x, y] of P.center_leg_bolts || [[-50, -32], [50, -32], [-50, 32], [50, 32]]) {
    const base = chain(F.center_leg.m, T(0, 0, P.lg_center_plane_z), RX(tilt), T(x, y, 8));
    draw('bolt8s', chain(flange.m, base, RZ(flange.k * Math.PI * 9)), tint(C.steel, t, 59.8, 62.0));
  }
  // 12 V 7 Ah sealed lead-acid battery on its shelf
  const batt = fit(t, 62.0, 65.0, 'body', [0, 0, 190]);
  if (batt.show) {
    const z = P.battery_shelf_z + P.battery[2] / 2;
    box([0, P.battery_y, z], P.battery, tint(C.battery, t, 62, 65), mul(batt.m, b));
    for (const [x, col] of [[-45, C.red], [45, C.dark]]) {
      cyl([x, P.battery_y + 30, P.battery_shelf_z + P.battery[2] + 5], 6, 10, col, I(), mul(batt.m, b));
    }
  }
  const strap = fit(t, 65.0, 66.5, 'body', [0, 0, 90]);
  if (strap.show) for (const x of [-48, 48]) {
    const colour = tint(C.strap, t, 65, 66.5), sm = mul(strap.m, b);
    const top = P.battery_shelf_z + P.battery[2];
    box([x, P.battery_y, top + 2], [P.battery_strap_w, P.battery[1] + 8, 4], colour, sm);
    for (const sy of [-1, 1]) {
      box([x, P.battery_y + sy * (P.battery[1] / 2 + 2), top - P.battery[2] / 2],
        [P.battery_strap_w, 4, P.battery[2] + 4], colour, sm);
    }
  }
  const speaker = fit(t, 66.5, 68.0, 'body', [0, 90, 0]);
  if (speaker.show) {
    disc([0, 104, 62], P.speaker_d / 2, P.speaker_depth, tint(C.dark, t, 66.5, 68), RX(Math.PI / 2), mul(speaker.m, b));
    disc([0, 112, 62], P.speaker_d / 2 - 14, 6, C.gray, RX(Math.PI / 2), mul(speaker.m, b));
  }
  const port = fit(t, 68.0, 69.0, 'body', [0, -70, 0]);
  if (port.show) {
    disc([62, -140, 58], 9, 18, tint(C.dark, t, 68, 69), RX(Math.PI / 2), mul(port.m, b));
    disc([62, -147, 58], 5, 8, C.brass, RX(Math.PI / 2), mul(port.m, b));
  }
  const sw = fit(t, 69.0, 70.0, 'body', [0, -70, 0]);
  if (sw.show) {
    box([-62, -138, 58], [26, 18, 26], tint(C.dark, t, 69, 70), mul(sw.m, b));
    box([-62, -148, 62], [12, 6, 14], C.red, mul(sw.m, b));
  }
}

function bodyUpper(t, cut) {
  drawPiece('body_upper', t, 71.0, 75.0, 'body_upper', [0, 0, 280], null, cut.mode, cut.m);
  const b = F.body.m;
  const zsh = P.shoulder_z;
  const bush = fit(t, 75.0, 76.5, 'body', [0, 0, 0]);
  if (bush.show) for (const s of [-1, 1]) {
    disc([s * (P.body_r + P.shoulder_spacer / 2), 0, zsh], 16, P.shoulder_spacer, tint(C.gray, t, 75, 76.5), RY(Math.PI / 2), mul(bush.m, b));
  }
  const pins = fit(t, 76.5, 78.5, 'body', [0, 0, 0]);
  if (pins.show) for (const s of [-1, 1]) for (const a of P.shoulder_index_angles) {
    const ang = radians(a + 90);
    cyl([s * (P.body_r + 2), P.shoulder_index_r * Math.cos(ang), zsh + P.shoulder_index_r * Math.sin(ang)],
      P.shoulder_index_d / 2, 20, tint(C.copper, t, 76.5, 78.5), RY(Math.PI / 2), mul(pins.m, b));
  }
  const bolts = fit(t, 78.5, 81.5, 'body', [0, 0, 0]);
  if (bolts.show) for (const s of [-1, 1]) {
    const x = s * (P.body_r + P.shoulder_spacer + P.leg_strut_t + 6);
    draw('bolt12', chain(bolts.m, b, T(x, 0, zsh), RY(s > 0 ? Math.PI / 2 : -Math.PI / 2), RZ(bolts.k * Math.PI * 12)),
      tint(C.steel, t, 78.5, 81.5));
    draw('nut12', chain(bolts.m, b, T(s * 42, 0, zsh), RY(Math.PI / 2)), C.gray);
  }
}

const DECK = [
  ['Raspberry Pi 4', [-58, 30], [85, 56, 20], 'green', 83.5, 86.0],
  ['KB2040', [20, 64], [35, 17.8, 5], 'blue', 86.0, 87.5],
  ['DRV8833 #1', [16, 32], [26, 18, 3], 'red', 87.5, 88.3],
  ['DRV8833 #2', [52, 32], [26, 18, 3], 'red', 88.3, 89.1],
  ['DRV8833 #3', [16, 4], [26, 18, 3], 'red', 89.1, 89.9],
  ['DRV8833 #4', [52, 4], [26, 18, 3], 'red', 89.9, 90.7],
  ['5 V regulator', [-62, -42], [25.4, 25.4, 9.5], 'gray', 90.7, 91.6],
  ['6 V regulator', [-26, -42], [25.4, 25.4, 9.5], 'gray', 91.6, 92.5],
  ['ADS1115', [16, -28], [25, 18, 3], 'blue', 92.5, 93.3],
  ['Main fuse', [58, -40], [22, 14, 20], 'dark', 93.3, 93.9],
  ['Charge fuse', [84, -40], [22, 14, 20], 'dark', 93.9, 94.5],
];
function deck(t) {
  const zDeck = P.body_lower_h + P.tray_z_upper;
  const b = F.body.m;
  for (const [name, [x, y], size, colourKey, t0, t1] of DECK) {
    const state = fit(t, t0, t1, 'body', [0, 0, 150]);
    if (!state.show) continue;
    const m = mul(state.m, b);
    box([x, y, zDeck + size[2] / 2], size, tint(C[colourKey] || C.gray, t, t0, t1), m);
    if (size[2] > 8) box([x, y, zDeck + size[2] + 1.5], [size[0] * 0.5, size[1] * 0.5, 3], C.dark, m);
    if (!hero && t >= 83 && t < 95) labels.push({ p: posOf(chain(m, T(x, y, zDeck + size[2] + 6))), text: name });
  }
}

function ringsJoined(t) {
  const b = F.body.m;
  if (!vis(t, 95)) return;
  if (!hero && t >= 95.5 && t < 98) {
    ring([0, 0, P.body_lower_h + P.seam_lip_h / 2], P.body_r - P.body_wall, P.seam_lip_h, C.amber, I(), b, 'ring_thin');
  }
  const rods = fit(t, 97.0, 100.5, 'body', [0, 0, 280]);
  if (rods.show) for (let j = 0; j < P.rod_n; j++) {
    const a = radians(P.rod_angle0 + j * 360 / P.rod_n);
    const x = P.rod_r * Math.cos(a), y = P.rod_r * Math.sin(a);
    cyl([x, y, 195], P.rod_d / 2, 350, tint(C.steel, t, 97, 100.5), I(), mul(rods.m, b));
    draw('nut8', chain(rods.m, b, T(x, y, 372), RZ(rods.k * Math.PI * 10)), C.gray);
  }
  const seam = fit(t, 100.5, 104.0, 'body', [0, 0, 40]);
  if (seam.show) for (let j = 0; j < P.seam_bolt_n; j++) {
    const a = radians(j * 360 / P.seam_bolt_n + 22.5);
    const r = P.body_r - P.body_wall - P.seam_flange_w / 2;
    draw('bolt4', chain(seam.m, b, T(r * Math.cos(a), r * Math.sin(a), P.body_lower_h + 18), RZ(seam.k * Math.PI * 12)),
      tint(C.steel, t, 100.5, 104));
    draw('nut4', chain(seam.m, b, T(r * Math.cos(a), r * Math.sin(a), P.body_lower_h - 16)), C.gray);
  }
}

function headDrive(t, cut) {
  drawPiece('head_drive', t, 106.0, 109.5, 'head_drive', [0, 0, -90], null, 0, null);
  const hdm = F.head_drive.m;
  const motorY = P.hd_hinge_y + P.hd_motor_y, z = P.hd_hinge_z;
  const dm = domeMotion(t);
  const wheelRoll = dm.spin * (P.head_wheel_r / WHEEL_R);
  const motor = fit(t, 109.5, 112.0, 'head_drive', [0, 0, -70]);
  if (motor.show) draw('motor', chain(motor.m, hdm, T(0, motorY, z)), tint(C.motor, t, 109.5, 112));
  const wheel = fit(t, 112.0, 114.0, 'head_drive', [0, -60, 0]);
  if (wheel.show) {
    const m = chain(wheel.m, hdm, T(0, -P.head_wheel_r, z), RX(-Math.PI / 2), RZ(-wheelRoll));
    draw('wheel', m, tint(C.tyre, t, 112, 114));
    for (let j = 0; j < 6; j++) draw('wheel_mark', mul(m, RZ(j * Math.PI / 3)), C.tread);
  }
  const spring = fit(t, 114.0, 115.5, 'head_drive', [0, 0, -60]);
  if (spring.show) {
    const [tx, ty] = P.hd_tension_xy;
    draw('spring', chain(spring.m, hdm, T(tx, ty, -14)), tint(C.steel, t, 114, 115.5));
    draw('bolt5', chain(spring.m, hdm, T(tx, ty, 20)), C.steel);
    cyl([P.hd_stop_xy[0], P.hd_stop_xy[1], -8], 2.6, 20, C.steel, I(), mul(spring.m, hdm));
  }
  const nut = fit(t, 115.5, 117.0, 'head_drive', [0, 0, 40]);
  if (nut.show) {
    const [tx, ty] = P.hd_tension_xy;
    const travel = hero ? 4 : lerp(14, 4, smooth(t, 138.5, 140.5));
    draw('thumbnut', chain(nut.m, hdm, T(tx, ty, travel), RZ(hero ? 0 : smooth(t, 138.5, 140.5) * Math.PI * 8)), C.brass);
  }
}

const DOME_PARTS = [
  ['Slip ring (12 wire)', 'hub', 0, 0, 117.5, 119.5],
  ['Round TFT radar eye', 'tft', 0, 108, 119.5, 121.5],
  ['Front logic matrix', 'matrix', -24.7, 48, 121.5, 122.6],
  ['Front logic matrix', 'matrix', -24.7, 74, 122.6, 123.7],
  ['Rear logic matrix', 'matrix2', -135.2, 52, 123.7, 125.0],
  ['Front PSI jewel', 'psi27', 7.19, 53.4, 125.0, 125.9],
  ['Rear PSI jewel', 'psi34', 159.5, 62.8, 125.9, 126.8],
  ['Holoprojector LED', 'hp', 25.5, 63.4, 126.8, 127.2],
  ['Holoprojector LED', 'hp', -170.8, 68.2, 127.2, 127.6],
  ['Holoprojector LED', 'hp3', 146.85, 0, 127.6, 128.0],
];
function domeRadius(z) {
  if (z <= P.dome_band_h) return P.dome_b;
  const k = (z - P.dome_band_h) / P.dome_a;
  return P.dome_b * Math.sqrt(Math.max(0, 1 - k * k));
}
function onDome(dm, angleDeg, z, inset) {
  return chain(dm, RZ(-radians(angleDeg)), T(0, domeRadius(z) - inset, z));
}
function domeElectronics(t, dm) {
  const L = lights(t), pulse = Math.sin(L.phase * 5.0) * 0.5 + 0.5;
  for (const [name, kind, angle, z, t0, t1] of DOME_PARTS) {
    const state = fit(t, t0, t1, 'world', [0, 0, 0]);
    if (!state.show) continue;
    const highlight = tint([0.25, 0.28, 0.33], t, t0, t1);
    let anchor = null;
    if (kind === 'hub') {
      const m = chain(dm, T(0, 0, P.dome_plate_t));
      cyl([0, 0, P.slip_ring_l / 2], P.slip_ring_d / 2, P.slip_ring_l, highlight, I(), m);
      cyl([0, 0, P.slip_ring_l + 4], 9, 8, C.gray, I(), m);
      anchor = posOf(chain(m, T(0, 0, P.slip_ring_l + 20)));
    } else if (kind === 'tft') {
      const m = onDome(dm, angle, z, 7);
      box([0, 0, 0], [P.dome_eye_lcd_pcb[0], P.dome_eye_lcd_pcb[2], P.dome_eye_lcd_pcb[1]], tint(C.green, t, t0, t1), m);
      disc([0, 3.2, 0], P.dome_eye_lens_d / 2 - 8, 3, L.on ? [0.20, 0.55, 0.95] : C.lens, RX(Math.PI / 2), m);
      if (L.on) lamp([0, 4.4, 0], P.dome_eye_lens_d / 2 - 9, 2, [0.30, 0.62, 0.98], RX(Math.PI / 2), m);
      anchor = posOf(chain(m, T(0, 12, 24)));
    } else if (kind === 'matrix' || kind === 'matrix2') {
      const wide = kind === 'matrix2';
      const m = onDome(dm, angle, z, 6);
      const cols = wide ? 2 : 1;
      for (let c = 0; c < cols; c++) {
        const ox = wide ? (c === 0 ? -11 : 11) : 0;
        box([ox, 0, 0], [P.dome_matrix_pcb[0], P.dome_matrix_pcb[2], P.dome_matrix_pcb[1]], tint(C.dark, t, t0, t1), m);
        if (L.on) for (let i = 0; i < 4; i++) for (let j = 0; j < 4; j++) {
          const k = Math.sin(L.phase * 6 + i * 1.7 + j * 2.3 + (wide ? 3 : 0)) * 0.5 + 0.5;
          const on = k > 0.45;
          box([ox - 7.5 + i * 5, 2.6, -7.5 + j * 5], [4, 1.6, 4], on ? [0.35, 0.72, 1.0] : [0.05, 0.09, 0.16],
            m);
        }
      }
      anchor = posOf(chain(m, T(0, 12, 18)));
    } else if (kind === 'psi27' || kind === 'psi34') {
      const d = kind === 'psi27' ? 23 : 30;
      const m = onDome(dm, angle, z, 5);
      disc([0, 0, 0], d / 2 + 3, 4, tint(C.dark, t, t0, t1), RX(Math.PI / 2), m);
      const colour = kind === 'psi27' ? (pulse > 0.5 ? [0.20, 0.45, 0.98] : [0.95, 0.30, 0.22])
        : (pulse > 0.5 ? [0.98, 0.72, 0.15] : [0.20, 0.80, 0.45]);
      if (L.on) lamp([0, 2.6, 0], d / 2, 2.4, colour, RX(Math.PI / 2), m);
      else disc([0, 2.6, 0], d / 2, 2.4, C.lens, RX(Math.PI / 2), m);
      anchor = posOf(chain(m, T(0, 12, 16)));
    } else if (kind === 'hp' || kind === 'hp3') {
      let m;
      if (kind === 'hp3') {
        const r = P.dome_hp3_r, zz = P.dome_band_h + P.dome_a * Math.sqrt(Math.max(0, 1 - (r / P.dome_b) * (r / P.dome_b)));
        m = chain(dm, RZ(-radians(angle)), T(0, r, zz - 8));
      } else {
        m = onDome(dm, angle, z, 8);
      }
      disc([0, 0, 0], P.dome_hp_d / 2 - 6, 8, tint(C.gray, t, t0, t1), kind === 'hp3' ? I() : RX(Math.PI / 2), m);
      if (L.on) lamp([0, kind === 'hp3' ? 0 : 4, kind === 'hp3' ? 5 : 0], 7, 3, [0.98, 0.97, 0.90], kind === 'hp3' ? I() : RX(Math.PI / 2), m);
      anchor = posOf(chain(m, T(0, 10, 14)));
    }
    if (!hero && t >= 117 && t < 128 && anchor) labels.push({ p: anchor, text: name });
  }
}

function domeAndSusan(t, cut) {
  const b = F.body.m;
  const susan = fit(t, 128.5, 131.0, 'body', [0, 0, 130]);
  if (susan.show) {
    ring([0, 0, P.body_top_plate_z + P.susan_t / 2], P.susan_od / 2, P.susan_t, tint(C.steel, t, 128.5, 131), I(), mul(susan.m, b));
  }
  const screws = fit(t, 131.0, 132.5, 'body', [0, 0, 40]);
  if (screws.show) for (const a of P.susan_hole_angles) {
    const ang = radians(a), r = P.susan_hole_r;
    draw('bolt5', chain(screws.m, b, T(r * Math.cos(ang), r * Math.sin(ang), P.body_top_plate_z + P.susan_t),
      RZ(screws.k * Math.PI * 12)), tint(C.steel, t, 131, 132.5));
  }
  const dm = domeFrame(t);
  const domeCut = (!hero && t >= 138.0 && t < 141) ? sectionAt(0, 0, 0) : { mode: 0, m: I() };
  const extra = mul(dm, F.dome.inv);
  drawPiece('dome', t, 117.0, 118.2, 'world', [0, 0, 150], extra, domeCut.mode, domeCut.m);
  domeElectronics(t, dm);
  if (!hero && t >= 138.0 && t < 141) cutNote = 'The dome is cut at its centre plane so the drive wheel contact with the dome plate is visible.';
}

// ---------- assembly ----------
function assemble(t, pose) {
  const cut = bodyCut(t);
  const demo = casterDemo(t);
  const swivel = frameRotZ(F.caster, hero ? 0 : (t >= 149 ? pose.caster : demo.angle));
  feet(t, swivel);
  motorsAndWheels(t, pose, swivel);
  if (vis(t, 25)) legs(t);
  if (vis(t, 42)) centreLeg(t, swivel);
  if (vis(t, 55)) bodyLower(t, cut);
  if (vis(t, 70)) bodyUpper(t, cut);
  if (vis(t, 83)) deck(t);
  if (vis(t, 95)) ringsJoined(t);
  if (vis(t, 105)) headDrive(t, cut);
  if (vis(t, 117)) domeAndSusan(t, cut);
  if (!hero) {
    if (t >= 55 && t < 105) cutNote = 'The body rings are complete prints. The half nearest the camera is cut away so the battery, the deck and the joint hardware stay visible.';
    else if (t >= 105 && t < 117) cutNote = 'The body rings are cut at the camera side so the head friction drive under the top plate stays visible.';
    else if (t >= 128 && t < 138) cutNote = 'The body rings are cut at the camera side so the head friction drive under the top plate stays visible.';
  }
}

// ---------- camera ----------
const SHOTS = [
  { at: 0, target: [0, 40, 370], height: 950, az: 118, elev: 16, azTo: 38, from: 0.3, to: 8 },
  { at: 8, target: [0, 108, 78], height: 560, az: 52, elev: 22, lift: true },
  { at: 12, target: [178, 116, 64], height: 360, az: 66, elev: 16, lift: true },
  { at: 19, target: [0, 108, 74], height: 560, az: 56, elev: 22, azTo: 36, from: 19, to: 25, lift: true },
  { at: 25, target: [0, 95, 275], height: 720, az: 48, elev: 13 },
  { at: 38, target: [0, 115, 125], height: 470, az: 58, elev: 18 },
  { at: 42, target: [0, 95, 145], height: 430, az: 30, elev: 22 },
  { at: 53, target: [0, 95, 130], height: 560, az: 34, elev: 32 },
  { at: 55, target: [0, 55, 260], height: 700, az: 52, elev: 18 },
  { at: 61, target: [0, 40, 215], height: 560, az: 52, elev: 26 },
  { at: 70, target: [0, 30, 400], height: 830, az: 58, elev: 16, azTo: 34, from: 74, to: 83 },
  { at: 83, target: [0, 40, 330], height: 470, az: 34, elev: 50 },
  { at: 95, target: [0, 25, 330], height: 700, az: 46, elev: 20 },
  { at: 105, target: [0, -70, 500], height: 500, az: -128, elev: 20 },
  { at: 117, target: [420, 10, 140], height: 430, az: -88, elev: 12 },
  { at: 119.5, target: [420, -30, 105], height: 480, az: -92, elev: 14 },
  { at: 121, target: [420, -60, 105], height: 370, az: -95, elev: 14, azTo: 95, from: 121.5, to: 128 },
  { at: 128, target: [0, -30, 470], height: 760, az: -72, elev: 14 },
  { at: 136, target: [0, -100, 514], height: 250, az: -84, elev: 5 },
  { at: 141, target: [0, 40, 420], height: 920, az: 78, elev: 12 },
  { at: 149, target: [0, 60, 350], height: 1180, az: 40, elev: 24 },
  { at: 164, target: [0, 40, 370], height: 950, az: 40, elev: 16, azTo: -6, from: 164, to: 170 },
];
function camera(t, pose) {
  let shot = SHOTS[0];
  for (const s of SHOTS) if (t >= s.at) shot = s;
  let az = shot.az;
  if (shot.azTo !== undefined) az = lerp(shot.az, shot.azTo, smooth(t, shot.from, shot.to));
  shotAz = az;
  const follow = t >= 149 ? lerp(0.75, 1.0, smooth(t, 162.5, 165)) : 0;
  const target = [shot.target[0] + follow * pose.x, shot.target[1] + follow * pose.y,
    shot.target[2] + (shot.lift ? footLift(t) : 0)];
  const distance = 2600, a = radians(az), e = radians(shot.elev);
  const eye = [target[0] + distance * Math.cos(e) * Math.cos(a),
    target[1] + distance * Math.cos(e) * Math.sin(a),
    target[2] + distance * Math.sin(e)];
  return mul(ortho(shot.height * (VIEW_W / VIEW_H), shot.height), lookAt(eye, target));
}

// ---------- overlay ----------
function wrap(text, x, y, width, line = 27, font = '20px Arial', colour = '#22303c') {
  ctx.font = font; ctx.fillStyle = colour;
  const words = String(text).split(/\s+/);
  let buffer = '';
  for (const word of words) {
    const next = buffer ? buffer + ' ' + word : word;
    if (ctx.measureText(next).width > width && buffer) { ctx.fillText(buffer, x, y); y += line; buffer = word; }
    else buffer = next;
  }
  if (buffer) ctx.fillText(buffer, x, y);
  return y + line;
}
function text(value, x, y, size = 20, colour = '#22303c', weight = '') {
  ctx.font = `${weight} ${size}px Arial`.trim(); ctx.fillStyle = colour; ctx.fillText(value, x, y);
}
function project(p) {
  const v = [p[0], p[1], p[2], 1];
  const m = mul(currentVP, globalPose);
  const x = m[0] * v[0] + m[4] * v[1] + m[8] * v[2] + m[12];
  const y = m[1] * v[0] + m[5] * v[1] + m[9] * v[2] + m[13];
  return [VIEW_X + (x * 0.5 + 0.5) * VIEW_W, H - (VIEW_Y + (y * 0.5 + 0.5) * VIEW_H)];
}
function drawLabels() {
  if (!labels.length) return;
  ctx.save();
  ctx.beginPath(); ctx.rect(VIEW_X, H - VIEW_Y - VIEW_H, VIEW_W, VIEW_H); ctx.clip();
  const used = [];
  for (const label of labels) {
    const [x, y] = project(label.p);
    if (x < 20 || x > VIEW_W - 20 || y < 90 || y > H - 100) continue;
    let ly = y;
    while (used.some(v => Math.abs(v - ly) < 24)) ly -= 24;
    used.push(ly);
    ctx.font = '17px Arial';
    const w = ctx.measureText(label.text).width + 14;
    const lx = Math.min(x + 14, VIEW_W - w - 10);
    ctx.strokeStyle = '#2c6f92'; ctx.lineWidth = 1.4;
    ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(lx, ly - 6); ctx.stroke();
    ctx.fillStyle = 'rgba(255,255,255,.93)'; ctx.fillRect(lx, ly - 20, w, 24);
    ctx.strokeStyle = '#8fb4c6'; ctx.strokeRect(lx + .5, ly - 19.5, w - 1, 23);
    text(label.text, lx + 7, ly - 3, 17, '#1d4f6b');
    ctx.fillStyle = '#2c6f92';
    ctx.beginPath(); ctx.arc(x, y, 3.2, 0, Math.PI * 2); ctx.fill();
  }
  ctx.restore();
}
function overlay(t, pose, dm, chapter, index) {
  ctx.clearRect(0, 0, W, H);
  ctx.drawImage(canvas, 0, 0);
  drawLabels();
  ctx.fillStyle = 'rgba(255,255,255,.965)';
  ctx.fillRect(0, 0, W, 108);
  ctx.fillRect(PANEL_X, 108, W - PANEL_X, 888);
  ctx.fillStyle = '#e3e9ee'; ctx.fillRect(PANEL_X, 108, 2, 888); ctx.fillRect(0, 106, W, 2);

  text('R2-D2  /  ASSEMBLY + SIMULATED OPERATION', 52, 48, 29, '#1d2c38', 'bold');
  text('Printed in PETG  |  317 mm body  |  Adafruit 3777 motors and 3766 wheels  |  Raspberry Pi 4 + KB2040', 54, 84, 19, '#4e606e');

  ctx.fillStyle = '#1d2c38'; ctx.fillRect(1470, 20, 420, 68);
  text('CAD ANIMATION', 1486, 46, 21, '#ffffff', 'bold');
  text('SIMULATED OPERATION - not physical footage', 1486, 71, 15, '#a9d2e6');

  text(`STAGE ${String(index + 1).padStart(2, '0')} / ${story.chapters.length}`, TX, 150, 17, '#5f7789', 'bold');
  let y = wrap(chapter.title, TX, 192, TW, 33, '26px Arial', '#17242e');
  y = wrap(chapter.instruction.replace('{HEIGHT}', String(Math.round(scene.overall_height_mm))), TX, y + 14, TW, 26, '19px Arial', '#3d5261');

  y = Math.max(y + 22, 452);
  const total = scene.counts.instances;
  ctx.fillStyle = '#eef4f8'; ctx.fillRect(TX - 12, y - 30, TW + 22, 62);
  text(`${shown.size} / ${total} printed pieces placed`, TX, y - 6, 21, '#1d4f6b', 'bold');
  text(`${scene.counts.designs} STL files  -  legs, feet and lower legs print twice`, TX, y + 20, 16, '#5a6f7d');
  y += 58;

  if (cutNote) {
    ctx.fillStyle = '#dceef5'; ctx.fillRect(TX - 12, y - 8, TW + 22, 112);
    text('CUTAWAY VIEW', TX, y + 18, 20, '#1c4d66', 'bold');
    wrap(cutNote, TX, y + 44, TW - 6, 22, '16px Arial', '#2a5670');
    y += 126;
  }
  if (!hero && t >= 141 && t < 164) {
    ctx.fillStyle = '#edf4f7'; ctx.fillRect(TX - 12, y - 8, TW + 22, 186);
    text('DRIVE: ' + pose.action, TX, y + 22, 23, '#1d5877', 'bold');
    text(`Path travelled: ${Math.round((pose.right + pose.left) / 2)} mm`, TX, y + 52, 18, '#33505f');
    text(`Heading: ${pose.yaw_deg.toFixed(1)} deg   Centre foot: ${pose.caster_deg.toFixed(1)} deg`, TX, y + 78, 18, '#33505f');
    text(`Wheel roll  R ${(pose.right / WHEEL_R).toFixed(2)} rad   L ${(pose.left / WHEEL_R).toFixed(2)} rad`, TX, y + 104, 18, '#33505f');
    text(`Dome: ${dm.spinning ? 'rotating' : (dm.nudge ? 'nudge left / right' : 'stopped')}  ${(degrees(dm.spin) % 360).toFixed(0)} deg`, TX, y + 130, 18, '#33505f');
    text('Speeds and light patterns are illustrative.', TX, y + 160, 16, '#5a6f7d');
    y += 200;
  }
  if (!hero && t >= 164) {
    ctx.fillStyle = '#edf4f7'; ctx.fillRect(TX - 12, y - 8, TW + 22, 176);
    text('STILL REQUIRED', TX, y + 22, 21, '#1d5877', 'bold');
    wrap('Print and fit check, joint strength under load, loaded driving, battery runtime, charging and thermal checks.',
      TX, y + 50, TW - 6, 24, '18px Arial', '#33505f');
    text('Follow the assembly manual and the wiring sheets.', TX, y + 148, 16, '#5a6f7d');
  }

  ctx.fillStyle = 'rgba(255,255,255,.965)'; ctx.fillRect(0, 996, W, 84);
  text('Printed pieces are the delivered STL meshes. Purchased hardware is a nominal envelope. This is not physical test footage.',
    52, 1032, 18, '#51646f');
  const total_s = story.total_seconds;
  text(`${String(Math.floor(t / 60)).padStart(2, '0')}:${String(Math.floor(t % 60)).padStart(2, '0')} / `
    + `${String(Math.floor(total_s / 60)).padStart(2, '0')}:${String(Math.floor(total_s % 60)).padStart(2, '0')}`,
    1742, 1032, 20, '#2a4a5e', 'bold');
  ctx.fillStyle = '#d9e2e8'; ctx.fillRect(52, 1052, 1816, 6);
  ctx.fillStyle = '#1f7aa3'; ctx.fillRect(52, 1052, 1816 * clamp01(t / total_s), 6);
  for (const c of story.chapters) {
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(52 + 1816 * (c.start / total_s), 1052, 1.6, 6);
  }
}

function chapterAt(t) {
  let index = story.chapters.findIndex(c => t >= c.start && t < c.end);
  if (index < 0) index = story.chapters.length - 1;
  return [story.chapters[index], index];
}

window.renderFrame = t => {
  if (!window.ready) throw new Error('Renderer not ready');
  shown = new Set(); labels = []; cutNote = '';
  hero = t < story.chapters[0].end;
  const pose = drive(t), dm = domeMotion(t);
  globalPose = chain(T(pose.x, pose.y, 0), RZ(pose.yaw));
  gl.viewport(0, 0, W, H);
  gl.clearColor(0.90, 0.93, 0.96, 1);
  gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);
  gl.viewport(VIEW_X, VIEW_Y, VIEW_W, VIEW_H);
  currentVP = camera(t, pose);
  gl.uniformMatrix4fv(U.vp, false, currentVP);
  const savedPose = globalPose;
  globalPose = I();
  floorGrid();
  globalPose = savedPose;
  assemble(t, pose);
  if (gl.getError() !== gl.NO_ERROR) throw new Error('WebGL rendering error');
  const [chapter, index] = chapterAt(t);
  overlay(t, pose, dm, chapter, index);
  return output.toDataURL('image/jpeg', 0.93).split(',')[1];
};

window.frameEvidence = t => {
  const [chapter] = chapterAt(t);
  const pose = drive(t), dm = domeMotion(t), demo = casterDemo(t);
  return {
    time: t, chapter: chapter.name, simulation: true,
    printed_instances: [...shown].sort(),
    drive: {
      action: pose.action, yaw_deg: pose.yaw_deg, caster_deg: pose.caster_deg,
      right_mm: +pose.right.toFixed(1), left_mm: +pose.left.toFixed(1), centre_mm: +pose.centre.toFixed(1),
      right_roll_rad: +(pose.right / WHEEL_R).toFixed(3), left_roll_rad: +(pose.left / WHEEL_R).toFixed(3),
      position_mm: [+pose.x.toFixed(1), +pose.y.toFixed(1)],
    },
    dome: { spin_deg: +degrees(dm.spin).toFixed(1), spinning: dm.spinning, nudge: dm.nudge },
    caster_demo: demo.active,
    lights_on: lights(t).on,
  };
};

(async () => {
  const data = await (await fetch('/scene.json')).json();
  scene = data; story = data.storyboard; P = data.params; F = data.frames; CH = story.chapters;
  for (const [name, mesh] of Object.entries(data.meshes)) {
    const bytes = Uint8Array.from(atob(mesh.buffer), c => c.charCodeAt(0));
    const array = new Float32Array(bytes.buffer);
    const vao = gl.createVertexArray();
    gl.bindVertexArray(vao);
    const buffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
    gl.bufferData(gl.ARRAY_BUFFER, array, gl.STATIC_DRAW);
    gl.enableVertexAttribArray(0); gl.vertexAttribPointer(0, 3, gl.FLOAT, false, 24, 0);
    gl.enableVertexAttribArray(1); gl.vertexAttribPointer(1, 3, gl.FLOAT, false, 24, 12);
    meshes[name] = { vao, count: mesh.count };
  }
  window.ready = true;
})().catch(error => { window.renderError = String(error && error.stack || error); });
