'use strict';
// Local WebGL renderer. All mesh data comes from the delivered STL files.
// The animation is illustrative; it never connects to the robot or a printer.
const W=1920,H=1080,VIEW_W=1400;
const output=document.getElementById('output'); output.width=W;output.height=H;
const ctx=output.getContext('2d');
const canvas=document.createElement('canvas'); canvas.width=W;canvas.height=H;
const gl=canvas.getContext('webgl2',{antialias:true,alpha:false,preserveDrawingBuffer:true});
if(!gl)throw new Error('WebGL2 is required');
const vs=`#version 300 es
layout(location=0) in vec3 position;layout(location=1) in vec3 normal;
uniform mat4 model;uniform mat4 vp;out vec3 n;out vec3 world;
void main(){vec4 p=model*vec4(position,1.);world=p.xyz;n=mat3(model)*normal;gl_Position=vp*p;}`;
const fs=`#version 300 es
precision highp float;in vec3 n;in vec3 world;uniform vec3 color;uniform int cut;
out vec4 frag;void main(){if(cut==1&&world.x>0.)discard;
float light=.40+.60*max(dot(normalize(n),normalize(vec3(-.3,-.6,1.))),0.);
frag=vec4(color*light,1.);}`;
function shader(type,source){const s=gl.createShader(type);gl.shaderSource(s,source);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))throw new Error(gl.getShaderInfoLog(s));return s;}
const program=gl.createProgram();gl.attachShader(program,shader(gl.VERTEX_SHADER,vs));gl.attachShader(program,shader(gl.FRAGMENT_SHADER,fs));gl.linkProgram(program);
if(!gl.getProgramParameter(program,gl.LINK_STATUS))throw new Error(gl.getProgramInfoLog(program));
const U={};for(const n of ['model','vp','color','cut'])U[n]=gl.getUniformLocation(program,n);
gl.useProgram(program);gl.enable(gl.DEPTH_TEST);gl.disable(gl.CULL_FACE);
const I=()=>[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1];
function mul(a,b){const r=new Array(16).fill(0);for(let c=0;c<4;c++)for(let row=0;row<4;row++)for(let k=0;k<4;k++)r[c*4+row]+=a[k*4+row]*b[c*4+k];return r;}
const chain=(...matrices)=>matrices.reduce(mul,I());
function T(x=0,y=0,z=0){const m=I();m[12]=x;m[13]=y;m[14]=z;return m;}
function S(x=1,y=1,z=1){const m=I();m[0]=x;m[5]=y;m[10]=z;return m;}
function RX(a){const c=Math.cos(a),s=Math.sin(a);return[1,0,0,0,0,c,s,0,0,-s,c,0,0,0,0,1];}
function RZ(a){const c=Math.cos(a),s=Math.sin(a);return[c,s,0,0,-s,c,0,0,0,0,1,0,0,0,0,1];}
function RY(a){const c=Math.cos(a),s=Math.sin(a);return[c,0,-s,0,0,1,0,0,s,0,c,0,0,0,0,1];}
const radians=d=>d*Math.PI/180;
const smooth=(t,a,b)=>{const v=Math.max(0,Math.min(1,(t-a)/(b-a)));return v*v*(3-2*v);};
const lerp=(a,b,t)=>a+(b-a)*t;
function normal(v){const q=Math.hypot(...v);return v.map(x=>x/q);}
const dot=(a,b)=>a.reduce((v,x,i)=>v+x*b[i],0);
const cross=(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];
function lookAt(eye,target){const z=normal(eye.map((v,i)=>v-target[i])),x=normal(cross([0,0,1],z)),y=cross(z,x);return[x[0],y[0],z[0],0,x[1],y[1],z[1],0,x[2],y[2],z[2],0,-dot(x,eye),-dot(y,eye),-dot(z,eye),1];}
function ortho(width,height,near=1,far=4000){return[2/width,0,0,0,0,2/height,0,0,0,0,-2/(far-near),0,0,0,-(far+near)/(far-near),1];}
const bronze=[[.24,.24,.22],[.65,.46,.25],[.69,.50,.28],[.65,.46,.25],[.41,.42,.40],[.76,.57,.31],[.35,.38,.40],[.69,.70,.70],[.69,.70,.70],[.41,.42,.40]];
const gray=[.58,.62,.67],steel=[.68,.72,.76],black=[.12,.14,.16],green=[.17,.42,.29],orange=[.91,.42,.12];
const meshes={};let story,globalPose=I(),hero=false,printedDraws=[];
function draw(key,matrix,color,cut=0,world=false){const mesh=meshes[key];if(/^\d{2}_/.test(key))printedDraws.push(key);gl.bindVertexArray(mesh.vao);gl.uniformMatrix4fv(U.model,false,world?matrix:mul(globalPose,matrix));gl.uniform3fv(U.color,color);gl.uniform1i(U.cut,cut);gl.drawArrays(gl.TRIANGLES,0,mesh.count);}
const cube=(center,size,color,extra=I(),world=false)=>draw('cube',chain(extra,T(...center),S(...size)),color,0,world);
const cylinder=(center,radius,height,color,rotation=I(),extra=I())=>draw('cylinder',chain(extra,T(...center),rotation,S(radius,radius,height)),color);
function arrival(t,start,end,offset){if(hero)return[0,0,0];const k=1-smooth(t,start,end);return offset.map(v=>v*k);}
const visible=(t,start)=>hero||t>=start;
function placed(t,start,end,target,offset=[0,0,150]){return T(...target.map((v,i)=>v+arrival(t,start,end,offset)[i]));}

function drive(t){
  if(t<104)return{x:0,y:0,yaw:0,left:0,right:0,action:'STOPPED'};
  let x=0,y=0,yaw=0,left=0,right=0;
  const d=180*smooth(t,104,107);
  y-=d;left+=d;right+=d;
  yaw=.4*smooth(t,107,111);
  x=600*(1-Math.cos(yaw));y-=600*Math.sin(yaw);
  left+=yaw*(600+122.5);right+=yaw*(600-122.5);
  // End the forward arc at rest, pause 200 ms, then reverse smoothly.
  const back=120*smooth(t,111.2,114);
  x-=back*Math.sin(yaw);y+=back*Math.cos(yaw);left-=back;right-=back;
  return{x,y,yaw,left:left/31.5,right:right/31.5,action:t<107?'FORWARD':t<111?'BROAD ARC':t<111.2?'PAUSE':t<114?'REVERSE':'STOPPED'};
}
function movement(t){
  const active=t>=96&&t<114,elapsed=Math.max(0,Math.min(t,114)-96),phase=2*Math.PI*.4*elapsed;
  const amplitude=radians(8)*smooth(t,96,96.8)*(1-smooth(t,113.6,114));
  return{head:elapsed*Math.PI/4,yaw:active?amplitude*Math.sin(phase):0,
    pitch:active?amplitude*Math.cos(phase):0,active};
}
function camera(t,pose){
  let focus=270,height=760,az=-55,elev=23;
  if(t>=5&&t<25){focus=95;height=465;az=-48;elev=33;}
  else if(t>=25&&t<36){focus=125;height=455;az=-38;elev=42;}
  else if(t>=36&&t<41){focus=260;height=690;elev=27;}
  else if(t>=41&&t<51){focus=395;height=735;az=lerp(-55,112,smooth(t,42,49));elev=21;}
  else if(t>=51&&t<64){focus=315;height=765;az=lerp(112,-55,smooth(t,51,58));elev=26;}
  else if(t>=64&&t<69.5){focus=453;height=445;az=-38;elev=25;}
  else if(t>=69.5&&t<73){focus=430;height=670;az=-38;elev=25;}
  else if(t>=73&&t<80){focus=465;height=570;az=8;elev=32;}
  else if(t>=80&&t<89){focus=364;height=415;az=-65;elev=24;}
  else if(t>=89&&t<96){focus=280;height=760;az=lerp(-55,96,smooth(t,89,91));elev=19;}
  else if(t>=96&&t<104){focus=295;height=735;az=lerp(96,-55,smooth(t,96,98));elev=21;}
  else if(t>=104&&t<115){focus=255;height=880;az=-45;elev=28;}
  else if(t>=115){focus=275;height=770;az=lerp(-45,-15,smooth(t,115,120));elev=23;}
  const target=[pose.x*.7,pose.y*.7,focus],distance=1500,a=radians(az),e=radians(elev);
  const eye=[target[0]+distance*Math.cos(e)*Math.cos(a),target[1]+distance*Math.cos(e)*Math.sin(a),target[2]+distance*Math.sin(e)];
  return mul(ortho(height*(VIEW_W/930),height),lookAt(eye,target));
}
function floor(){
  cube([0,0,-1.2],[3500,3500,1], [.96,.97,.985],I(),true);
  for(let i=-1500;i<=1500;i+=100){cube([i,0,-.64],[.8,3500,.08],[.84,.87,.90],I(),true);cube([0,i,-.64],[3500,.8,.08],[.84,.87,.90],I(),true);}
}
function wheel(t,sx,sy,step,roll){
  const start=5.5+step*.8,base=placed(t,start,start+2,[sx*122.5,sy*60,31.5],[sx*15,0,145]);
  if(!visible(t,start))return;
  const rotation=chain(base,RX(roll));
  draw('wheel',rotation,orange);
  cylinder([0,0,0],25,27,[.49,.55,.58],RY(Math.PI/2),rotation);
  for(let j=0;j<12;j++)cube([0,0,31.6],[28,3,.8],[.35,.20,.12],chain(rotation,RX(j*Math.PI/6)));
  const motor=placed(t,start,start+2,[sx*95,sy*38,31.02],[sx*15,0,145]);
  draw('cube',chain(motor,S(22.4,70,22.44)),[.89,.70,.13]);
  cylinder([sx*109,sy*60,31.5],3,13,steel,RY(Math.PI/2),T(...arrival(t,start,start+2,[sx*15,0,145])));
}
function stackBolts(t,start,end,kind,z){
  if(!visible(t,start))return;
  for(let j=0;j<4;j++){
    const a=j*Math.PI/2,r=kind===0?(j%2===0?137:127):kind===1?112:97,x=r*Math.cos(a),y=r*Math.sin(a);
    const m=placed(t,start+j*.14,end+j*.14,[x,y,z],[0,0,48]);
    draw('bolt4',chain(m,RZ((1-smooth(t,start,end))*Math.PI*6)),steel);
    draw('washer4',mul(m,T(0,0,-.6)),steel);
    draw('nut4',placed(t,start,end,[x,y,z-14],[0,0,-20]),gray);
  }
}
function assemble(t,pose,motion){
  draw('01_base',T(0,0,13.8),bronze[0]);
  let order=0;for(const sx of [-1,1])for(const sy of [-1,1])wheel(t,sx,sy,order++,sx<0?pose.left:pose.right);
  if(visible(t,13))for(const sx of [-1,1])for(const sy of [-1,1])for(const yy of [8,18]){
    const strip=placed(t,13,15.4,[sx*94.5,sy*yy,43.3],[0,0,85]);
    draw('cube',chain(strip,S(43,8,1)),steel);
    for(const xx of [76,113]){
      const m=placed(t,15.2,18,[sx*xx,sy*yy,44.4],[0,0,68]);
      draw('bolt3',chain(m,RZ((1-smooth(t,15.2,18))*Math.PI*8)),steel);
      draw('washer3',mul(m,T(0,0,-.5)),gray);
      draw('nut3',placed(t,15.2,18,[sx*xx,sy*yy,11.5],[0,0,-6]),gray);
    }
  }
  if(visible(t,19))draw('02_lower_skirt',placed(t,19,22.4,[0,0,67.8],[0,0,160]),bronze[1],!hero&&t>=25&&t<36?1:0);
  stackBolts(t,22.4,24.5,0,74.4);
  if(visible(t,25)){
    for(const [ys,ye] of [[-91,-63],[65,93]])for(const x of [-54,54])for(const y of [ys,ye])
      draw('spacer25',placed(t,25,26.5,[x,y,35.3],[0,0,75]),gray);
    for(const [y,step] of [[-87,0],[87,.3]]){
      const plate=placed(t,26+step,28+step,[0,y,48.8],[0,0,100]);draw('cube',chain(plate,S(180,72,2)),[.37,.44,.45]);
      const boardZ=56.6,delta=arrival(t,28,30,[0,0,100]);
      if(visible(t,28)){
        cube([-35,y,boardZ],[51,81,1.6],green,T(...delta));
        cube([-37,y,61],[8,18,7],black,T(...delta));cube([-24,y+12,59],[10,16,4],black,T(...delta));
        cube([32,y<0?-101:101,boardZ],[25.4,25.4,1.6],green,T(...delta));
        cube([32,y<0?-101:101,61],[11,11,8],[.23,.26,.29],T(...delta));
        cube([65,y<0?-101:101,boardZ],[22,25,1.6],green,T(...delta));
        cube([65,y<0?-101:101,60],[10,11,5],black,T(...delta));
      }
    }
    if(visible(t,28)){
      const d=T(...arrival(t,28,30,[0,0,100]));
      cube([52,-67,56.6],[62,25,1.6],green,d);cube([57,70,56.6],[18,22,1.6],green,d);cube([79,70,56.6],[17,11,1.6],green,d);
    }
    if(visible(t,30))draw('cube',chain(placed(t,30,32.5,[0,0,57.8],[0,0,135]),S(114,70,76)),[.19,.29,.38]);
    if(visible(t,32.5))for(const x of [-35,35]){
      const d=T(...arrival(t,32.5,34.3,[0,0,90]));
      cube([x,0,96.5],[20,72,1],black,d);cube([x,-36,57.5],[20,1,77],black,d);cube([x,36,57.5],[20,1,77],black,d);
    }
    if(visible(t,34)){
      draw('power_wires',T(0,0,0),[.75,.13,.10]);draw('ground_wires',T(0,0,0),black);
    }
  }
  if(visible(t,36))draw('03_upper_skirt',placed(t,36,38.8,[0,0,177.8],[0,0,185]),bronze[2]);
  stackBolts(t,38.8,40.5,1,184.4);
  const shoulderOffset=hero?0:160*(1-smooth(t,51,54.5));
  const shoulder=T(0,0,277.8+shoulderOffset);
  if(visible(t,41))draw('04_shoulder',shoulder,bronze[3]);
  if(visible(t,41.7)){
    const d=arrival(t,41.7,44,[0,-85,0]);
    cylinder([d[0],-108+d[1],50+d[2]],34,2,black,RX(Math.PI/2),shoulder);
  }
  if(visible(t,44.2)){
    const d=T(...arrival(t,44.2,47,[0,-60,50]));
    cube([0,109,64.52],[51.52,2,25.04],green,mul(shoulder,d));
    cube([0,114.8,65.5],[26,1,15],[.13,.59,.73],mul(shoulder,d));
  }
  if(visible(t,47))for(const x of [-34,34])for(const z of [56,73]){
    const d=T(...arrival(t,47,48.7,[0,-55,25]));
    cube([x-Math.sign(x)*5,97.5,z],[20,1,8],[.61,.65,.67],mul(shoulder,d));
    cube([Math.sign(x)*24.5,103,z],[3,10,4],[.39,.43,.46],mul(shoulder,d));
  }
  if(visible(t,48))for(const x of [-30,30]){
    const m=mul(shoulder,T(...arrival(t,48,50,[0,65,0])));
    cylinder([x,110,23],6,5,steel,RX(Math.PI/2),m);cylinder([x,119,23],2.3,15,gray,RX(Math.PI/2),m);
  }
  if(visible(t,53.5))draw('upper_harness',T(0,0,0),black);
  stackBolts(t,54.5,56.5,2,284.4);
  if(visible(t,57))draw('05_neck',placed(t,57,60.5,[0,0,377.8],[0,0,145]),bronze[4]);
  stackBolts(t,60.5,63.1,2,384.4);
  if(visible(t,64)){
    const x=hero?0:120*(1-smooth(t,64,65));
    const z=hero?421.3:lerp(401.8,421.3,smooth(t,65,65.8));
    draw('bearing608',T(x,0,z),steel);
  }
  if(visible(t,65.8))draw('spacer12',placed(t,65.8,66.5,[0,0,430.8],[0,0,65]),gray);
  if(visible(t,66.5))draw('bearing608',placed(t,66.5,67.3,[0,0,440.3],[0,0,65]),steel);
  if(visible(t,67.2))for(const z of [417.3,444.3])for(let j=0;j<3;j++){
    const a=j*Math.PI*2/3,x=14*Math.cos(a),y=14*Math.sin(a),offset=z<430?-16:25;
    draw('retaining_washer',placed(t,67.2,68.2,[x,y,z],[0,0,offset]),steel);
    draw('screw8',chain(placed(t,67.4,68.5,[x,y,z+(z<430?-.5:.5)],[0,0,offset]),z<430?RX(Math.PI):I()),steel);
  }
  if(visible(t,68)){
    draw('spindle8',chain(placed(t,68,69.2,[0,0,416.8],[0,0,-90]),RZ(motion.head)),steel);
    draw('shim8',placed(t,68,69,[0,0,417.3],[0,0,-35]),gray);
    draw('shim8',placed(t,68.6,69.5,[0,0,444.3],[0,0,38]),gray);
  }
  // Keep the head free of the spindle while the closed belt is preloaded on its hub.
  const headLift=hero?0:t<73?140+65*(1-smooth(t,69.5,71.5)):140*(1-smooth(t,77,79.1));
  if(visible(t,69.5))draw('06_head',chain(T(0,0,444.8+headLift),RZ(motion.head)),bronze[5],!hero&&t>=73&&t<80?1:0);
  if(visible(t,79.1)){
    draw('top_washer8',placed(t,79.1,79.4,[0,0,472.6],[0,0,100]),gray);
    draw('nut8',chain(placed(t,79.35,79.9,[0,0,476.4],[0,0,105]),RZ(motion.head)),steel);
  }
  if(visible(t,73))draw('cube',chain(placed(t,73,74.8,[72.5,10.05,430.4],[95,0,50]),S(20.15,40.15,37.2)),black);
  if(visible(t,74.8))draw('10_servo_pulley',chain(placed(t,74.8,75.8,[72.5,0,456.8],[100,0,0]),RZ(motion.head*62/23)),bronze[9]);
  if(visible(t,76))draw('belt',T(0,0,461.3+headLift),black);
  for(const side of [-1,1]){
    const x=side*48,yaw=motion.yaw,pitch=side<0?motion.pitch:-motion.pitch;
    if(visible(t,80))draw('cube',chain(placed(t,80,81.6,[x,-131,351.3],[side*70,-60,30]),S(24,12,31)),black);
    const pivot=chain(T(x,-131,367.8),RZ(yaw));
    if(visible(t,81.3))cylinder([0,0,-.5],12,1,gray,I(),chain(pivot,T(...arrival(t,81.3,81.6,[0,0,25]))));
    if(visible(t,81.6))draw('07_pitch_carrier',chain(pivot,T(...arrival(t,81.6,83,[side*65,-60,35]))),bronze[6]);
    if(visible(t,83))cube([17.5,0,26],[27,12,36],black,chain(pivot,T(...arrival(t,83,84.5,[side*60,-60,30]))));
    if(visible(t,84.3))cylinder([-2,0,30],12,2,gray,RY(Math.PI/2),chain(pivot,T(...arrival(t,84.3,84.6,[-25,0,0]))));
    if(visible(t,84.6)){
      const rest=chain(RZ(-Math.PI/2),RX(Math.PI/2)),offset=side<0?13:3;
      const m=chain(pivot,T(-3,0,30),RX(-pitch),T(...arrival(t,84.6,87.3,[side*45,-95,0])),rest,T(0,0,-offset));
      draw(side<0?'08_plunger_arm':'09_emitter_arm',m,bronze[side<0?7:8]);
    }
  }
}
function wrap(text,x,y,width,line=29,font='22px Arial',color='#263440'){
  ctx.font=font;ctx.fillStyle=color;const words=text.split(/\s+/);let buffer='';
  for(const word of words){const next=buffer?buffer+' '+word:word;if(ctx.measureText(next).width>width&&buffer){ctx.fillText(buffer,x,y);y+=line;buffer=word;}else buffer=next;}
  if(buffer)ctx.fillText(buffer,x,y);return y+line;
}
function text(value,x,y,size=20,color='#263440'){ctx.font=`${size}px Arial`;ctx.fillStyle=color;ctx.fillText(value,x,y);}
function screenInset(t){
  const x=1460,y=526,w=385,h=236;
  ctx.fillStyle='#172633';ctx.fillRect(x,y,w,h);
  text('EXAMPLE REAR DISPLAY',x+16,y+27,18,'#c4d9e8');
  text('DALEK  /  DEMO',x+16,y+61,24,'#67d5ec');
  text('AP: 192.168.4.1',x+16,y+94,23,'#ffffff');
  text(t<93?'LAN: offline':'LAN: 192.0.2.10',x+16,y+128,23,'#ffffff');
  text('Key: [demo]',x+16,y+161,21,'#ffffff');
  text(t<93?'ACCESS POINT':'AP + NETWORK',x+16,y+201,21,'#82dfa6');
  wrap('Illustrative screen state. No live network or robot connection.',x,y+h+26,w,23,'17px Arial','#5b6874');
}
function overlay(t,pose){
  ctx.clearRect(0,0,W,H);ctx.drawImage(canvas,0,0);
  ctx.fillStyle='rgba(255,255,255,.96)';ctx.fillRect(0,0,W,112);ctx.fillRect(1415,112,505,910);
  text('DALEK / ASSEMBLY + OPERATION',52,51,30,'#243541');
  text('STACK-10   |   Original 1.14-inch T-Display   |   Bronze finish',54,87,20,'#586976');
  ctx.fillStyle='#243541';ctx.fillRect(1485,24,382,62);
  text('CAD ANIMATION',1502,49,21,'#ffffff');text('SIMULATED OPERATION',1502,74,18,'#a9d6e8');
  const index=story.chapters.findIndex(c=>t>=c.start&&t<c.end),chapter=story.chapters[index<0?story.chapters.length-1:index];
  text(`STAGE ${String((index<0?15:index)+1).padStart(2,'0')} / 16`,1460,159,17,'#657d8e');
  const last=wrap(chapter.title,1460,203,390,35,'27px Arial','#20303d');
  wrap(chapter.instruction,1460,last+24,390,29,'21px Arial','#435768');
  const count=hero?11:[0,19,36,41,57,69.5,81.6,81.6,84.6,84.6,74.8].filter(s=>t>=s).length;
  text(`${count} / 11 printed pieces shown`,1460,446,20,'#2d607c');
  text('10 STL designs / carrier printed twice',1460,476,17,'#657480');
  if(t>=25&&t<36){
    ctx.fillStyle='#dceef5';ctx.fillRect(1460,526,385,120);
    wrap('CUTAWAY VIEW',1475,555,355,27,'21px Arial','#234c65');
    wrap('The lower skirt is a complete print. It is cut away here to show the electronics.',1475,590,350,24,'17px Arial','#31556b');
  }
  if(t>=73&&t<80){
    ctx.fillStyle='#dceef5';ctx.fillRect(1460,526,385,155);
    wrap('HEAD CUTAWAY',1475,555,355,27,'21px Arial','#234c65');
    wrap('Preload the belt on the loose head hub. Fit the drive, then lower and retain the head.',1475,590,350,25,'18px Arial','#31556b');
  }
  if(t>=89&&t<96)screenInset(t);
  if(t>=96&&t<115){
    ctx.fillStyle='#edf4f7';ctx.fillRect(1460,526,385,208);
    text('DRIVE: '+pose.action,1480,563,25,'#285a74');
    text(t<114?'Head: rotating':'Head: stopped',1480,603,21,'#354d60');
    text(t<114?'Arms: 8 deg / 0.40 Hz':'Arms: stopped',1480,638,21,'#354d60');
    text('Motion speeds are illustrative.',1480,684,18,'#5b6f7d');
  }
  if(t>=115){
    ctx.fillStyle='#edf4f7';ctx.fillRect(1460,526,385,202);
    wrap('Physical tests still required',1480,558,345,29,'23px Arial','#2c5369');
    wrap('Fit, base strength, loaded driving, temperature and stopping.',1480,601,335,29,'20px Arial','#435d6e');
    text('Follow the assembly manual.',1480,698,18,'#435d6e');
  }
  ctx.fillStyle='rgba(255,255,255,.96)';ctx.fillRect(0,996,W,84);
  text('Actual printed meshes. Purchased hardware is simplified. Animation is not physical test footage.',52,1034,19,'#566a77');
  text(`${String(Math.floor(t/60)).padStart(2,'0')}:${String(Math.floor(t%60)).padStart(2,'0')} / 02:00`,1734,1034,20,'#324e61');
  ctx.fillStyle='#dae3e9';ctx.fillRect(52,1054,1815,5);ctx.fillStyle='#2978a0';ctx.fillRect(52,1054,1815*t/120,5);
}
window.renderFrame=t=>{
  if(!window.ready)throw new Error('Renderer not ready');
  printedDraws=[];
  hero=t<5;const pose=drive(t),motion=movement(t);if(hero){pose.x=pose.y=pose.yaw=pose.left=pose.right=0;motion.head=0;motion.yaw=0;motion.pitch=0;}
  globalPose=chain(T(pose.x,pose.y,0),RZ(pose.yaw));
  gl.viewport(0,0,W,H);gl.clearColor(.97,.98,.99,1);gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);
  gl.viewport(0,76,VIEW_W,930);gl.uniformMatrix4fv(U.vp,false,camera(t,pose));floor();assemble(t,pose,motion);
  if(gl.getError()!==gl.NO_ERROR)throw new Error('WebGL rendering error');
  overlay(t,pose);
  return output.toDataURL('image/jpeg',.94).split(',')[1];
};
window.frameEvidence=t=>({time:t,drive:drive(t),motion:movement(t),printed_instances:[...printedDraws],simulation:true});
(async()=>{
  const data=await(await fetch('/scene.json')).json();story=data.storyboard;
  for(const [name,mesh] of Object.entries(data.meshes)){
    const bytes=Uint8Array.from(atob(mesh.buffer),c=>c.charCodeAt(0));const array=new Float32Array(bytes.buffer);
    const vao=gl.createVertexArray();gl.bindVertexArray(vao);const buffer=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,buffer);gl.bufferData(gl.ARRAY_BUFFER,array,gl.STATIC_DRAW);
    gl.enableVertexAttribArray(0);gl.vertexAttribPointer(0,3,gl.FLOAT,false,24,0);gl.enableVertexAttribArray(1);gl.vertexAttribPointer(1,3,gl.FLOAT,false,24,12);
    meshes[name]={vao,count:mesh.count};
  }
  window.ready=true;
})().catch(error=>{window.renderError=String(error);});
