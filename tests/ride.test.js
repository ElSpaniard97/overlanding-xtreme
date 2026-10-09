import {test} from 'node:test';
import assert from 'node:assert/strict';
import {dampSpring,followAngle,createRide,updateRide} from '../src/ride.js';
import {surfaceHeight,trailX} from '../src/terrain.js';
import {createState,updateState} from '../src/game.js';
test('suspension settles without overshooting and gives the same result across frame rates',()=>{
 function simulate(dt){let value=0,velocity=0;for(let i=0;i<Math.round(1/dt);i++){const s=dampSpring(value,velocity,1,10,dt);assert.ok(s.value>=value&&s.value<=1);({value,velocity}=s);}return value;}
 assert.ok(Math.abs(simulate(1/30)-simulate(1/120))<1e-9);assert.ok(simulate(1/60)>.99);
});
test('body rotation takes the shortest path across the heading wrap',()=>{const angle=followAngle(Math.PI-.01,-Math.PI+.01,5,.02);assert.ok(angle>Math.PI-.01&&angle<Math.PI+.01);});
test('recovery teleports reset suspension instead of dragging the car across terrain',()=>{const r=createRide();updateRide(r,{x:0,z:0,y:3,pitch:0,roll:0,heading:0},.016);updateRide(r,{x:30,z:50,y:10,pitch:.1,roll:0,heading:1},.016);assert.equal(r.y,10);assert.equal(r.velocity,0);assert.equal(r.x,30);});
test('eastern terrain bank is continuous at the old height seam',()=>{for(const z of [0,100,600,1000]){const x=trailX(z)+35;assert.ok(Math.abs(surfaceHeight(x+.001,z)-surfaceHeight(x-.001,z))<.01);}});
test('entering loose terrain slows progressively rather than clipping speed',()=>{const s=createState();s.z=30;s.x=trailX(30)+11;s.speed=17;updateState(s,{},.01);assert.ok(s.speed>16);});
