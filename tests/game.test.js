import {test} from 'node:test';
import assert from 'node:assert/strict';
import {createState,updateState,updateFrame,interact,trailX,objectives} from '../src/game.js';
test('driving consumes fuel and brakes reduce speed',()=>{const s=createState();for(let i=0;i<100;i++)updateState(s,{w:true},.05);assert.ok(s.z>0);assert.ok(s.fuel<100);const before=s.speed;updateState(s,{brake:true},.05);assert.ok(s.speed<before);});
test('water requires proximity and a stopped vehicle and cannot be collected twice',()=>{const s=createState();assert.equal(interact(s).won,undefined);s.z=360;s.x=trailX(s.z);s.speed=5;interact(s);assert.equal(s.completed.length,0);s.speed=0;interact(s);assert.equal(s.water,84);interact(s);assert.equal(s.water,84);});
test('camp requires every prior objective and completes expedition',()=>{const s=createState();s.z=1470;s.x=trailX(s.z);interact(s);assert.equal(s.won,false);s.completed=[0,1,2,3];assert.equal(interact(s).won,true);assert.equal(s.completed.length,objectives.length);});
test('low range protects suspension while fast offroad driving damages it',()=>{const s=createState();s.x=40;s.speed=15;updateState(s,{},.05);assert.ok(s.health<100);s.health=100;s.low=true;updateState(s,{},.05);assert.equal(s.health,100);});
test('resource exhaustion stops driving',()=>{const s=createState();s.fuel=.001;s.speed=12;updateState(s,{w:true},.05);assert.equal(s.failed,true);assert.equal(s.speed,0);});

test("slow render frames advance the same simulation time as fast frames",()=>{const slow=createState(),fast=createState();for(let i=0;i<20;i++)updateFrame(slow,{w:true},.25);for(let i=0;i<100;i++)updateFrame(fast,{w:true},.05);assert.ok(Math.abs(slow.z-fast.z)<1e-8);assert.ok(slow.z>20);assert.ok(Math.abs(slow.elapsed-5)<1e-8);});

test('steering changes heading and movement follows the vehicle direction',()=>{const s=createState();s.speed=8;const heading=s.heading,x=s.x;for(let i=0;i<10;i++)updateState(s,{d:true,w:true},.05);assert.ok(s.heading>heading);assert.ok(s.x>x);assert.ok(s.steering>0);});
test('wheels rotate from distance and reverse rotates them backwards',()=>{const s=createState();s.z=200;s.x=trailX(200);s.heading=0;s.speed=4;updateState(s,{},.05);assert.ok(s.wheelAngle>0);const angle=s.wheelAngle;s.speed=-4;updateState(s,{},.05);assert.ok(s.wheelAngle<angle);});
test('reverse input brakes forward motion before engaging reverse',()=>{const s=createState();s.speed=8;updateState(s,{s:true},.05);assert.ok(s.speed>0&&s.speed<8);for(let i=0;i<50;i++)updateState(s,{s:true},.05);assert.ok(s.speed<0);});
test('braking holds the vehicle without accelerating',()=>{const s=createState();for(let i=0;i<40;i++)updateState(s,{w:true,brake:true},.05);assert.equal(s.speed,0);assert.equal(s.wheelAngle,0);});
test('reverse steering changes heading opposite to forward steering',()=>{const s=createState();s.z=200;s.x=trailX(200);s.heading=0;s.speed=-5;for(let i=0;i<10;i++)updateState(s,{d:true},.05);assert.ok(s.heading<0);});
