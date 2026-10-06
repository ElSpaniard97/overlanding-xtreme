export const TRAIL_LENGTH = 1500;
export function trailX(z) { return Math.sin(z / 145) * 44 + Math.sin(z / 63) * 13; }
export function trailHeight(z) { return 3 + z * .012 + Math.sin(z / 100) * 5 + Math.sin(z / 32) * 1.1; }
export const objectives = [
  { name: 'Find the canyon trail', at: 100 },
  { name: 'Collect water · spring one', at: 360, water: true },
  { name: 'Collect water · spring two', at: 830, water: true },
  { name: 'Reach the summit lookout', at: 1430 },
  { name: 'Set up camp', at: 1470, camp: true },
];
export function createState() { return { z: 0, x: trailX(0), speed: 0, fuel: 100, water: 68, health: 100, low: false, locked: false, completed: [], won: false, failed: false, elapsed: 0 }; }
export function updateState(s, input, dt) {
  if (s.failed || s.won) return;
  dt = Math.min(.05, Math.max(0, dt)); s.elapsed += dt;
  const offroad = Math.abs(s.x - trailX(s.z)) > 10;
  const maxSpeed = s.low ? 12 : 27;
  const throttle = input.w ? 1 : input.s ? -1 : 0;
  s.speed += throttle * (s.low ? 7 : 5) * dt;
  s.speed *= Math.exp(-(input.brake ? 5 : offroad ? (s.locked ? .35 : .7) : .12) * dt);
  s.speed = Math.max(-7, Math.min(maxSpeed * (offroad ? .6 : 1), s.speed));
  s.x += ((input.d ? 1 : 0) - (input.a ? 1 : 0)) * Math.abs(s.speed) * .6 * dt;
  s.x = Math.max(trailX(s.z)-48, Math.min(trailX(s.z)+48, s.x));
  s.z = Math.max(0, Math.min(TRAIL_LENGTH, s.z + s.speed * dt));
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
  for(let remaining=Math.min(.25,Math.max(0,dt));remaining>1e-8;remaining-=.05)
    updateState(state,input,Math.min(.05,remaining));
}
