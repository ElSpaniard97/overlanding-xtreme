export const TRAIL_LENGTH = 1500;
import {trailX,trailHeight,surfaceHeight,surfaceAt,obstacles} from './terrain.js';
export {trailX,trailHeight} from './terrain.js';
export const objectives = [
  { name: 'Find the canyon trail', at: 100 },
  { name: 'Collect water · spring one', at: 360, water: true },
  { name: 'Collect water · spring two', at: 830, water: true },
  { name: 'Reach the summit lookout', at: 1430 },
  { name: 'Set up camp', at: 1470, camp: true },
];
export function createState() { return { z: 0, x: trailX(0), speed: 0, heading: Math.atan2(trailX(1)-trailX(0),1), steering: 0, wheelAngle: 0, distance: 0, fuel: 100, water: 68, health: 100, low: false, locked: false, completed: [], won: false, failed: false, elapsed: 0, recoveries: 2, lastSafe: {x:trailX(0),z:0}, impact:0, surface: "PACKED TRAIL" }; }
export function updateState(s, input, dt) {
  if (s.failed || s.won) return;
  dt = Math.min(.05, Math.max(0, dt)); s.elapsed += dt;
  const offroad = Math.abs(s.x - trailX(s.z)) > 10;
  const surface=surfaceAt(s.x,s.z);s.surface=surface.name;s.impact=Math.max(0,s.impact-dt);
  const traction=Math.min(1,surface.grip+(s.locked?.22:0)+(s.low?.18:0));
  const grade=(surfaceHeight(s.x+Math.sin(s.heading),s.z+Math.cos(s.heading))-surfaceHeight(s.x-Math.sin(s.heading),s.z-Math.cos(s.heading)))/2;
  const maxSpeed = s.low ? 8 : 18;
  const throttle = input.w ? 1 : input.s ? -1 : 0;
  const opposing = throttle && Math.sign(s.speed) !== throttle && Math.abs(s.speed) > .15;
  if (opposing) s.speed -= Math.sign(s.speed)*Math.min(Math.abs(s.speed),12*dt);
  else if (!input.brake) s.speed += throttle * (s.low ? 7 : 5) * traction * dt;
  if(!input.brake&&Math.abs(s.speed)>.15)s.speed-=grade*3.5*dt;
  s.speed *= Math.exp(-(input.brake ? 7 : offroad ? (s.locked ? .35 : .7) : throttle ? .12 : .55) * dt);
  if(Math.abs(s.speed)<.04) s.speed=0;
  const limit=maxSpeed*(offroad?.6:1);
  if(s.speed>limit)s.speed=Math.max(limit,s.speed-6*dt);
  s.speed=Math.max(-7,s.speed);
  const steerInput=((input.d ? 1 : 0) - (input.a ? 1 : 0));
  const maxSteer=.5/(1+Math.abs(s.speed)*.035);
  s.steering += (steerInput*maxSteer-s.steering)*(1-Math.exp(-dt*8));
  s.heading += s.speed/2.8*Math.tan(s.steering)*dt*(.7+.3*traction);
  s.heading=Math.atan2(Math.sin(s.heading),Math.cos(s.heading));
  const oldX=s.x,oldZ=s.z;
  s.x += Math.sin(s.heading)*s.speed*dt;
  s.z = Math.max(0, Math.min(TRAIL_LENGTH, s.z + Math.cos(s.heading)*s.speed*dt));
  s.x = Math.max(trailX(s.z)-42, Math.min(trailX(s.z)+48, s.x));
  for(const o of obstacles){const dx=s.x-o.x,dz=s.z-o.z,d=Math.hypot(dx,dz),radius=o.radius+1.05;if(d<radius){const safe=d||1;s.x=o.x+(d?dx/safe:1)*radius;s.z=o.z+(d?dz/safe:0)*radius;if(s.impact===0)s.health=Math.max(0,s.health-Math.max(0,Math.abs(s.speed)-2)*1.6);s.speed*=.12;s.impact=1;}}
  if(!offroad&&Math.abs(s.speed)<12&&s.impact===0)s.lastSafe={x:s.x,z:s.z};
  const travel=Math.hypot(s.x-oldX,s.z-oldZ);
  s.distance+=travel;s.wheelAngle+=(s.speed<0?-1:1)*travel/.55;
  if(travel<.00001&&Math.abs(s.speed)>.1)s.speed=0;
  s.fuel = Math.max(0, s.fuel - Math.abs(s.speed) * dt * .021 - (throttle ? dt * .02 : 0));
  s.water = Math.max(0, s.water - dt * .025);
  if (offroad && Math.abs(s.speed) > 9 && !s.low) s.health = Math.max(0, s.health - dt * 1.3);
  if (s.fuel === 0 || s.health === 0) { s.failed = true; s.speed = 0; }
  for (let i=0;i<objectives.length;i++) if (!objectives[i].water && !objectives[i].camp && s.z >= objectives[i].at && !s.completed.includes(i)) s.completed.push(i);
}
export function interact(s) {
  if(s.failed || s.won) return {message:'Restart the expedition to continue.'};
  if(Math.abs(s.speed)>2) return {message:'Stop the vehicle to interact.'};
  for (let i=0;i<objectives.length;i++) {
    const o=objectives[i];
    if (Math.abs(s.z-o.at)<32 && Math.abs(s.x-trailX(s.z))<20 && !s.completed.includes(i)) {
      if(o.water) { s.completed.push(i); s.water=Math.min(100,s.water+16); return {message:'Water collected. One less thing to worry about.'}; }
      if(o.camp) {
        if(s.completed.length<4) return {message:'Collect both water caches before setting up camp.'};
        s.completed.push(i); s.won=true; return {message:'Camp is ready. You made it.',won:true};
      }
    }
  }
  return {message:'Follow the trail to a water cache or the summit campsite.'};
}

// Substeps preserve elapsed movement on slower rendering frames.
export function updateFrame(state,input,dt){
  for(let remaining=Math.min(.25,Math.max(0,dt));remaining>1e-8;remaining-=.01)
    updateState(state,input,Math.min(.01,remaining));
}

export function recover(s){
  if(s.won||s.failed)return {message:'Restart the expedition to continue.'};
  if(Math.abs(s.speed)>1)return {message:'Stop before using recovery gear.'};
  if(s.recoveries<=0)return {message:'No recovery kits left. Restart or drive back to the trail.'};
  s.x=s.lastSafe.x;s.z=s.lastSafe.z;s.heading=Math.atan2(trailX(s.z+1)-trailX(s.z),1);s.speed=0;s.recoveries--;return {message:`Recovered to your last safe trail position. ${s.recoveries} kits left.`};
}
export function restoreState(value){
  if(!value||value.version!==2||!value.state)return null;
  const s=value.state,base=createState();
  for(const k of ['z','x','speed','heading','steering','wheelAngle','distance','fuel','water','health','elapsed'])if(!Number.isFinite(s[k]))return null;
  if(s.z<0||s.z>TRAIL_LENGTH||Math.abs(s.x-trailX(s.z))>50||[s.fuel,s.water,s.health].some(v=>v<0||v>100)||s.elapsed<0||s.distance<0)return null;
  if(!Array.isArray(s.completed)||s.completed.some(i=>!Number.isInteger(i)||i<0||i>=objectives.length)||new Set(s.completed).size!==s.completed.length)return null;
  if(!Number.isInteger(s.recoveries)||s.recoveries<0||s.recoveries>2)return null;
  const restored={...base};for(const k of ['z','x','heading','wheelAngle','distance','fuel','water','health','elapsed','recoveries'])restored[k]=s[k];return {...restored,completed:[...s.completed],failed:s.fuel===0||s.health===0,won:s.completed.includes(4),lastSafe:{x:trailX(s.z),z:s.z},low:!!s.low,locked:!!s.locked};
}
