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
uniform mat4 model;uniform mat4 vp;out vec3 n;out vec3 world;out vec3 localPosition;
void main(){vec4 p=model*vec4(position,1.);world=p.xyz;localPosition=position;n=mat3(model)*normal;gl_Position=vp*p;}`;
const fs=`#version 300 es
precision highp float;in vec3 n;in vec3 world;in vec3 localPosition;uniform vec3 color;uniform int cut;uniform int upperPaint;
out vec4 frag;void main(){if(cut==1&&world.x>0.)discard;if(cut==2&&world.y< -5.)discard;
if(cut==3&&world.y< -5.&&localPosition.z>=120.)discard;
vec3 paint=color;
if(upperPaint==1){paint=localPosition.z>=120.?vec3(.41,.42,.40):vec3(.65,.46,.25);
float r=length(localPosition.xy);if(r>98.8&&r<100.6&&localPosition.z>=125.&&localPosition.z<171.)paint=vec3(.12,.14,.16);}
float light=.40+.60*max(dot(normalize(n),normalize(vec3(-.3,-.6,1.))),0.);
frag=vec4(paint*light,1.);}`;
function shader(type,source){const s=gl.createShader(type);gl.shaderSource(s,source);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))throw new Error(gl.getShaderInfoLog(s));return s;}
const program=gl.createProgram();gl.attachShader(program,shader(gl.VERTEX_SHADER,vs));gl.attachShader(program,shader(gl.FRAGMENT_SHADER,fs));gl.linkProgram(program);
if(!gl.getProgramParameter(program,gl.LINK_STATUS))throw new Error(gl.getProgramInfoLog(program));
const U={};for(const n of ['model','vp','color','cut','upperPaint'])U[n]=gl.getUniformLocation(program,n);
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
const meshes={};let story,boardLayout,globalPose=I(),hero=false,printedDraws=[];
function draw(key,matrix,color,cut=0,world=false){const mesh=meshes[key];if(/^\d{2}_/.test(key))printedDraws.push(key);gl.bindVertexArray(mesh.vao);gl.uniformMatrix4fv(U.model,false,world?matrix:mul(globalPose,matrix));gl.uniform3fv(U.color,color);gl.uniform1i(U.cut,cut);gl.uniform1i(U.upperPaint,key==='04_shoulder'?1:0);gl.drawArrays(gl.TRIANGLES,0,mesh.count);}
const cube=(center,size,color,extra=I(),world=false)=>draw('cube',chain(extra,T(...center),S(...size)),color,0,world);
const cylinder=(center,radius,height,color,rotation=I(),extra=I())=>draw('cylinder',chain(extra,T(...center),rotation,S(radius,radius,height)),color);
function arrival(t,start,end,offset){if(hero)return[0,0,0];const k=1-smooth(t,start,end);return offset.map(v=>v*k);}
const visible=(t,start)=>hero||t>=start;
function placed(t,start,end,target,offset=[0,0,150]){return T(...target.map((v,i)=>v+arrival(t,start,end,offset)[i]));}
function via(t,start,turn,end,from,through,target){
  if(hero)return T(...target);
  const a=t<turn?from:through,b=t<turn?through:target,f=smooth(t,t<turn?start:turn,t<turn?turn:end);
  return T(...a.map((v,i)=>lerp(v,b[i],f)));
}

function drive(t){
  if(t<104)return{x:0,y:0,yaw:0,left:0,right:0,action:'STOPPED'};
  let x=0,y=0,yaw=0,left=0,right=0;
  const d=180*smooth(t,104,107);
  y-=d;left+=d;right+=d;
  yaw=.4*smooth(t,107,111);
  x=600*(1-Math.cos(yaw));y-=600*Math.sin(yaw);
  left+=yaw*(600+98);right+=yaw*(600-98);
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
  if(t>=5&&t<19){focus=95;height=465;az=-48;elev=33;}
  else if(t>=19&&t<25){focus=125;height=450;az=-48;elev=37;}
  else if(t>=25&&t<36){focus=180;height=555;az=-38;elev=36;}
  else if(t>=36&&t<41){focus=260;height=690;elev=27;}
  else if(t>=41&&t<51){focus=395;height=735;az=lerp(-55,112,smooth(t,42,49));elev=21;}
  else if(t>=51&&t<57){focus=500;height=565;az=-38;elev=21;}
  else if(t>=57&&t<64){focus=560;height=565;az=-55;elev=17;}
  else if(t>=64&&t<73){focus=380;height=795;az=-38;elev=27;}
  else if(t>=73&&t<80){focus=465;height=355;az=-25;elev=42;}
  else if(t>=80&&t<83){focus=490;height=480;az=-55;elev=30;}
  else if(t>=83&&t<89){focus=470;height=335;az=-55;elev=34;}
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
  const start=5.5+step*.8,base=placed(t,start,start+2,[sx*98,sy*58,31.5],[sx*15,0,145]);
  if(!visible(t,start))return;
  const rotation=chain(base,RX(roll));
  draw('wheel',rotation,orange);
  cylinder([0,0,0],25,27,[.49,.55,.58],RY(Math.PI/2),rotation);
  for(let j=0;j<12;j++)cube([0,0,31.6],[28,3,.8],[.35,.20,.12],chain(rotation,RX(j*Math.PI/6)));
  const motor=placed(t,start,start+2,[sx*70.5,sy*36,31.02],[sx*15,0,145]);
  draw('cube',chain(motor,S(22.4,70,22.44)),[.89,.70,.13]);
  cylinder([sx*84.5,sy*58,31.5],3,13,steel,RY(Math.PI/2),T(...arrival(t,start,start+2,[sx*15,0,145])));
}
function stackBolts(t,start,end,kind,z){
  if(!visible(t,start))return;
  for(let j=0;j<4;j++){
    const a=j*Math.PI/2,r=kind===0?137:97,x=r*Math.cos(a),y=r*Math.sin(a);
    const m=placed(t,start+j*.14,end+j*.14,[x,y,z],[0,0,48]);
    draw('bolt4',chain(m,RZ((1-smooth(t,start,end))*Math.PI*6)),steel);
    draw('washer4',mul(m,T(0,0,-.6)),steel);
    draw('nut4',T(x,y,z-15.5),gray);
  }
}
function assemble(t,pose,motion){
  draw('01_base',T(0,0,13.8),bronze[0]);
  let order=0;for(const sx of [-1,1])for(const sy of [-1,1])wheel(t,sx,sy,order++,sx<0?pose.left:pose.right);
  const motorTies=!hero&&t>=17.3&&t<19;
  if(visible(t,13))for(const sx of [-1,1])for(const sy of [-1,1]){
    if(!motorTies){
      draw('11_motor_clamp',chain(via(t,13,14.3,15.1,[sx*74.5,sy*11,127.8],[sx*74.5,sy*11,42.8],[sx*70.5,sy*11,42.8]),RZ(sx<0?Math.PI:0)),gray);
      if(visible(t,15.1)){
        const m=placed(t,15.1,17.1,[sx*88.5,sy*11,48.3],[0,0,55]);
        draw('guide16',chain(m,RZ((1-smooth(t,15.1,17.1))*Math.PI*6)),steel);
        draw('washer3',mul(m,T(0,0,-.5)),gray);draw('nut3',T(sx*88.5,sy*11,37),gray);
      }
    }else for(const x of (sy>0?[62,74]:[68,80])){
      cube([sx*x,sy*36,44.8],[4.8,74,1],black);
      cube([sx*x,sy*36,12.8],[4.8,74,1],black);
      for(const y of [-.2,72.2])cube([sx*x,sy*y,28.8],[4.8,1,32],black);
    }
  }
  if(visible(t,19)){
    // The final assembly uses the largest supported bare SLA envelope.
    // Earlier chapter frames compare the retained LiFePO4 and7Ah options.
    const size=!hero&&t<20.6?[70,114,76]:!hero&&t<22?[67,153,102]:[100,153,103];
    const d=T(...arrival(t,19,20.5,[0,0,130]));
    cube([0,0,21.8+size[2]/2],size,[.19,.29,.38],d);
    if(visible(t,22.5))for(const y of [-25,25]){
      cube([0,y,125.5],[104,4.8,1],black);cube([0,y,12.7],[104,4.8,1],black);
      for(const x of [-51.5,51.5])cube([x,y,69],[1,4.8,113],black);
    }
  }
  if(visible(t,25)){
    const lift=hero?0:105*(1-smooth(t,29,31));
    draw('12_electronics_platform',chain(T(0,0,159.8+lift),RX(Math.PI)),[.37,.44,.45]);
    if(visible(t,26))for(const [name,[x,y],[w,h,height]] of boardLayout){
      const d=T(0,0,lift+(hero?0:42*(1-smooth(t,26,28.8))));
      cube([x,y,166.6],[w,h,1.6],green,d);
      cube([x,y,168.8],[Math.min(w*.55,20),Math.min(h*.55,15),Math.max(3,height-1.6)],black,d);
    }
    if(visible(t,31.1))for(const x of [-56.5,56.5])for(const y of [-56,-40,40,56]){
      const d=T(...arrival(t,31.1,33,[0,0,35]));
      cylinder([x,y,54.8],2.8,3,steel,I(),d);
    }
    if(visible(t,34)){
      draw('power_wires',T(),[.75,.13,.10]);draw('ground_wires',T(),black);
    }
  }
  if(visible(t,36))draw('02_skirt',placed(t,36,38.5,[0,0,67.8],[0,0,160]),bronze[1]);
  stackBolts(t,38.5,40.5,0,75.0);
  const shoulderOffset=hero?0:160*(1-smooth(t,66,70.5));
  const shoulder=T(0,0,277.8+shoulderOffset);
  if(visible(t,41)){
    const bodyCut=!hero&&t>=43&&t<64?1:0;
    const neckCut=bodyCut||(!hero&&t>=73&&t<89?3:0);
    draw('04_shoulder',shoulder,bronze[3],neckCut);
  }
  if(visible(t,64)){
    const d=arrival(t,64,65.5,[0,40,-95]);
    cylinder([d[0],69.245+d[1],43+d[2]],34,25.49,black,RX(Math.PI/2),shoulder);
    for(const z of [6.1,79.9])cube([d[0],57.5+d[1],z+d[2]],[77.8,2,4],gray,shoulder);
    for(const x of [-36.9,36.9])cube([x+d[0],57.5+d[1],43+d[2]],[4,2,77.8],gray,shoulder);
  }
  if(visible(t,64.2)){
    const d=T(...arrival(t,64.2,65,[0,-60,50]));
    cube([0,109,64.52],[51.52,2,25.04],green,mul(shoulder,d));
    cube([0,114.8,65.5],[26,1,15],[.13,.59,.73],mul(shoulder,d));
  }
  if(visible(t,65))for(const x of [-34,34])for(const z of [56,73]){
    const d=T(...arrival(t,65,65.6,[0,-55,25]));
    cube([x-Math.sign(x)*5,97.5,z],[20,1,8],[.61,.65,.67],mul(shoulder,d));
    cube([Math.sign(x)*24.5,103,z],[3,10,4],[.39,.43,.46],mul(shoulder,d));
  }
  if(visible(t,65.2))for(const x of [-30,30]){
    const m=mul(shoulder,T(...arrival(t,65.2,65.9,[0,65,0])));
    cylinder([x,110,23],6,5,steel,RX(Math.PI/2),m);cylinder([x,119,23],2.3,15,gray,RX(Math.PI/2),m);
  }
  if(visible(t,70.5))draw('upper_harness',T(0,0,0),black);
  stackBolts(t,70.5,72.8,2,285.0);
  const neckLift=shoulderOffset;
  if(visible(t,43)){
    const z=441.3-(hero?0:200*(1-smooth(t,43,44.2)));
    draw('bearing608',T(0,0,z+neckLift),steel);
  }
  if(visible(t,44.2))draw('spacer12',placed(t,44.2,45,[0,0,450.8+neckLift],[0,0,55]),gray);
  if(visible(t,45))draw('bearing608',placed(t,45,46,[0,0,460.3+neckLift],[0,0,55]),steel);
  if(visible(t,46))for(const z of [437.3,464.3])for(let j=0;j<3;j++){
    const a=j*Math.PI*2/3,x=14*Math.cos(a),y=14*Math.sin(a),offset=z<450?-16:25;
    draw('retaining_washer',placed(t,46,47,[x,y,z+neckLift],[0,0,offset]),steel);
    draw('screw8',chain(placed(t,46.6,47.3,[x,y,z+neckLift+(z<450?-.5:.5)],[0,0,offset]),z<450?RX(Math.PI):I()),steel);
  }
  if(visible(t,47.5)){
    draw('spindle8',chain(placed(t,47.5,49,[0,0,436.8+neckLift],[0,0,-260]),RZ(motion.head)),steel);
    draw('shim8',placed(t,47.5,48.7,[0,0,437.3+neckLift],[0,0,-35]),gray);
    draw('shim8',placed(t,48.7,49.5,[0,0,464.3+neckLift],[0,0,38]),gray);
  }
  // Fit the entire friction drive before lowering the head around it.
  const headLift=hero?0:110*(1-smooth(t,73,76));
  if(visible(t,73)){
    const transform=chain(T(0,0,449.8+headLift),RZ(motion.head)),cut=!hero&&t>=80&&t<89?2:0;
    draw('06_head',transform,bronze[5],cut);draw('finish_head_drum',transform,black,cut);
    draw('finish_eye_discs',transform,[.83,.85,.83],cut);draw('finish_eye_lens',transform,black,cut);
    draw('finish_eye_face',transform,[.12,.45,.65],cut);
  }
  if(visible(t,76)){
    draw('top_washer8',placed(t,76,77,[0,0,492.6],[0,0,80]),gray);
    draw('nut8',chain(placed(t,77,78,[0,0,496.4],[0,0,85]),RZ(motion.head)),steel);
  }
  const contactX=hero?64.5:t<63.5?64.5:t<64?lerp(64.5,61.5,smooth(t,63.5,64)):61.5+3*smooth(t,83.4,85.3);
  if(visible(t,57)){
    const mount=placed(t,57,59.5,[contactX,0,427+shoulderOffset],[0,0,100]);
    draw('10_head_motor_carriage',mount,bronze[9]);
    cube([-.48,-22,14.3],[22.44,70,22.4],[.89,.70,.13],mount);
    const w=chain(mount,T(0,0,41.8),RZ(motion.head*96/31.5));
    draw('head_wheel',w,orange);cylinder([0,0,0],25,27,gray,I(),w);
    for(let j=0;j<12;j++)cube([30.6,0,0],[2,3,28],[.35,.20,.12],chain(w,RZ(j*Math.PI/6)));
  }
  if(visible(t,60))for(const [x,y] of [[43,-50],[43,8],[83.5,-40],[83.5,8]]){
    draw('guide16',chain(placed(t,60,61,[x,y,431.0+shoulderOffset],[0,0,35]),RZ(smooth(t,85.4,87)*Math.PI*4)),steel);
    draw('guide_washer3',T(x,y,430.5+shoulderOffset),gray);draw('washer3',T(x,y,422.5+shoulderOffset),gray);
    draw('nut3',T(x,y,420.8+shoulderOffset),gray);
  }
  if(visible(t,62)){
    draw('adjust25',chain(placed(t,62,63,[contactX-48,-35,435.8+shoulderOffset],[-65,0,0]),RY(-Math.PI/2),RZ(smooth(t,83.4,85.3)*Math.PI*8)),steel);
    draw('nut3',chain(T(34.35,-35,435.8+shoulderOffset),RY(Math.PI/2)),gray);
  }
  for(const [side,x] of [[-1,-47],[1,53]]){
    const yaw=motion.yaw,pitch=side<0?motion.pitch:-motion.pitch;
    const top=277.8+shoulderOffset;
    if(visible(t,55.5))draw('socket_liner',chain(placed(t,55.5,56,[x-3,-105,354.8+shoulderOffset],[0,45,45]),RX(Math.PI/2)),black);
    if(visible(t,50.4)){
      let yy=0,zz;
      if(hero||t>=50.95){yy=-94;zz=22.5;}
      else if(t<50.65)zz=lerp(-24.5,60.5,smooth(t,50.4,50.65));
      else if(t<50.82){zz=60.5;yy=lerp(0,-94,smooth(t,50.65,50.82));}
      else{yy=-94;zz=lerp(60.5,22.5,smooth(t,50.82,50.95));}
      draw('cube',chain(T(x-5,yy,top+zz),S(22.6,12,31)),black);
    }
    const pivot=chain(T(x,-94,319.8+shoulderOffset),RZ(yaw));
    if(visible(t,53.25))cylinder([0,0,-.5],12,1,gray,I(),chain(pivot,T(...arrival(t,53.25,53.4,[0,0,25]))));
    if(visible(t,53.4)){
      let m;
      if(hero||t>=54.9)m=T(x,-94,top+42);
      else if(t<53.8)m=T(-29,25,top+lerp(-55,88,smooth(t,53.4,53.8)));
      else if(t<54.1)m=T(-29,lerp(25,-44,smooth(t,53.8,54.1)),top+88);
      else if(t<54.3)m=T(-29,-44,top+lerp(88,46,smooth(t,54.1,54.3)));
      else if(t<54.5)m=T(lerp(-29,x,smooth(t,54.3,54.5)),-44,top+46);
      else if(t<54.75)m=T(x,lerp(-44,-94,smooth(t,54.5,54.75)),top+46);
      else m=T(x,-94,top+lerp(46,42,smooth(t,54.75,54.9)));
      draw('07_pitch_carrier',chain(m,RZ(yaw)),bronze[6]);
      draw('cube',chain(m,RZ(yaw),T(16.5,0,30),S(31,12,22.6)),black);
    }
    if(visible(t,55.1))cylinder([-2,0,35],12,2,gray,RY(Math.PI/2),chain(pivot,T(...arrival(t,55.1,55.5,[-25,0,0]))));
    if(visible(t,55.5)){
      const tieOption=!hero&&t>=55.9&&t<57;
      if(tieOption){
        for(const xx of [-11,3]){
          cube([x+xx,-94,top+39],[2.5,21,1],black);
          cube([x+xx,-94,top+3.3],[2.5,21,1],black);
          for(const yy of [-10,10])cube([x+xx,-94+yy,top+21],[2.5,1,36],black);
        }
        for(const z of [24,36]){
          for(const yy of [-7,13])cube([18.25,yy,z],[36.5,1,2.5],black,pivot);
          for(const xx of [0,36.5])cube([xx,3,z],[1,20,2.5],black,pivot);
        }
      }else{
        for(const xx of [-19.5,9.5]){
          cylinder([x+xx,-94,top+28.5],1,10,steel);
          cylinder([x+xx,-94,top+33.5],2,2,steel);
        }
        for(const z of [15.75,44.25]){
          cylinder([11.5,0,z],1,10,steel,RY(Math.PI/2),pivot);
          cylinder([6,0,z],2,2,steel,RY(Math.PI/2),pivot);
        }
      }
    }
    if(visible(t,51)){
      const rest=chain(RZ(-Math.PI/2),RX(Math.PI/2));
      let m;
      if(!hero&&t<52.4){
        let y=25,angle=radians(90),z=110;
        if(t<51.23){y=10;z=lerp(-35,45,smooth(t,51,51.23));}
        else if(t<51.32){y=lerp(10,25,smooth(t,51.23,51.32));z=45;}
        else if(t<51.5)z=lerp(45,110,smooth(t,51.32,51.5));
        else if(t<51.8)angle=radians(lerp(90,13.5,smooth(t,51.5,51.8)));
        else if(t<51.9){angle=radians(13.5);z=lerp(110,77+140*Math.tan(angle),smooth(t,51.8,51.9));}
        else if(t<52.15){angle=radians(13.5);y=lerp(25,-20,smooth(t,51.9,52.15));z=77+(y+115)*Math.tan(angle);}
        else if(t<52.3){y=-20;angle=radians(13.5)*(1-smooth(t,52.15,52.3));z=77+95*Math.tan(angle);}
        else{y=lerp(-20,-94,smooth(t,52.3,52.4));angle=0;z=77;}
        m=chain(T(x-3,y,top+z),RX(angle),rest,T(0,0,-28));
      }else m=chain(pivot,T(-3,0,35),RX(-pitch),rest,T(0,0,-28));
      draw(side<0?'08_plunger_arm':'09_emitter_arm',m,bronze[side<0?7:8]);
      draw(side<0?'finish_08_plunger_arm':'finish_09_emitter_arm',m,black);
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
  text('MOUNT-1   |   Original 1.14-inch T-Display   |   Bronze finish',54,87,20,'#586976');
  ctx.fillStyle='#243541';ctx.fillRect(1485,24,382,62);
  text('CAD ANIMATION',1502,49,21,'#ffffff');text('SIMULATED OPERATION',1502,74,18,'#a9d6e8');
  const index=story.chapters.findIndex(c=>t>=c.start&&t<c.end),chapter=story.chapters[index<0?story.chapters.length-1:index];
  text(`STAGE ${String((index<0?15:index)+1).padStart(2,'0')} / 16`,1460,159,17,'#657d8e');
  const last=wrap(chapter.title,1460,203,390,35,'27px Arial','#20303d');
  wrap(chapter.instruction,1460,last+18,390,25,'19px Arial','#435768');
  const count=printedDraws.length;
  text(`${count} / 14 maximum prints shown`,1460,480,20,'#2d607c');
  text('10 STL designs; motor ties omit4 clamps',1460,508,17,'#657480');
  if(t>=13&&t<19){
    ctx.fillStyle='#dceef5';ctx.fillRect(1460,526,385,155);
    wrap(t<17.3?'OPTION A / FOUR SCREWS':'OPTION B / MOTOR TIES',1475,555,355,27,'21px Arial','#234c65');
    wrap(t<17.3?'Hook the inner toe, then tighten one screw per motor. Four printed clamps total.':'Omit all four clamps and screws. Two ties per motor follow the dedicated floor slots.',1475,590,350,25,'18px Arial','#31556b');
  }
  if(t>=19&&t<25){
    ctx.fillStyle='#dceef5';ctx.fillRect(1460,526,385,238);
    wrap(t<20.6?'BIOENNO6Ah / LiFePO4':t<22?'12V7Ah / LEAD ACID':'12V14Ah / LEAD ACID',1475,555,355,27,'21px Arial','#234c65');
    wrap('One battery at a time. Use its matching charger outside the robot. The14Ah case is shown in the remaining assembly.',1475,597,350,25,'18px Arial','#31556b');
    wrap('The heavier SLA options need loaded driving tests.',1475,717,350,24,'17px Arial','#31556b');
  }
  if(t>=25&&t<36){
    ctx.fillStyle='#dceef5';ctx.fillRect(1460,526,385,120);
    wrap('ONE-PIECE PLATFORM',1475,555,355,27,'21px Arial','#234c65');
    wrap('Printed legs leave the battery on the base. Fit the boards before securing the platform feet.',1475,590,350,24,'17px Arial','#31556b');
  }
  if(t>=51&&t<57){
    ctx.fillStyle='#dceef5';ctx.fillRect(1460,526,385,155);
    wrap('SHOULDER CUTAWAY',1475,555,355,27,'21px Arial','#234c65');
    wrap('Smaller90 x52 x103mm boxes. Screws or ties retain the cases. Horn screws and opaque liners stay required.',1475,590,350,25,'18px Arial','#31556b');
  }
  if(t>=41&&t<51){
    ctx.fillStyle='#dceef5';ctx.fillRect(1460,526,385,155);
    wrap('INTEGRATED HEAD SUPPORT',1475,555,355,27,'21px Arial','#234c65');
    wrap('The fixed head support prints with the shoulder. Prepare the lower bearing before installing the speaker.',1475,590,350,25,'18px Arial','#31556b');
  }
  if(t>=57&&t<64){
    ctx.fillStyle='#dceef5';ctx.fillRect(1460,526,385,180);
    wrap('ADJUSTABLE HEAD CARRIAGE',1475,555,355,27,'21px Arial','#234c65');
    wrap('Lower the motor and wheel together. Secure the underside nuts before seating the upper shell. Retract the tyre for head installation.',1475,590,350,25,'18px Arial','#31556b');
  }
  if(t>=73&&t<89){
    ctx.fillStyle='#dceef5';ctx.fillRect(1460,526,385,155);
    wrap('HEAD / NECK CUTAWAY',1475,555,355,27,'21px Arial','#234c65');
    wrap('Screw adjustment moves the tyre toward the internal drum. Lock light contact and check free rotation.',1475,590,350,25,'18px Arial','#31556b');
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
  const data=await(await fetch('/scene.json')).json();story=data.storyboard;boardLayout=data.board_layout;
  for(const [name,mesh] of Object.entries(data.meshes)){
    const bytes=Uint8Array.from(atob(mesh.buffer),c=>c.charCodeAt(0));const array=new Float32Array(bytes.buffer);
    const vao=gl.createVertexArray();gl.bindVertexArray(vao);const buffer=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,buffer);gl.bufferData(gl.ARRAY_BUFFER,array,gl.STATIC_DRAW);
    gl.enableVertexAttribArray(0);gl.vertexAttribPointer(0,3,gl.FLOAT,false,24,0);gl.enableVertexAttribArray(1);gl.vertexAttribPointer(1,3,gl.FLOAT,false,24,12);
    meshes[name]={vao,count:mesh.count};
  }
  window.ready=true;
})().catch(error=>{window.renderError=String(error);});
