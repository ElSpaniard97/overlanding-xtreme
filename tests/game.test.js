import {test} from 'node:test';
import assert from 'node:assert/strict';
import {createState,updateState,interact,trailX,objectives} from '../src/game.js';
test('driving consumes fuel and brakes reduce speed',()=>{const s=createState();for(let i=0;i<100;i++)updateState(s,{w:true},.05);assert.ok(s.z>0);assert.ok(s.fuel<100);const before=s.speed;updateState(s,{brake:true},.05);assert.ok(s.speed<before);});
test('water requires proximity and a stopped vehicle and cannot be collected twice',()=>{const s=createState();assert.equal(interact(s).won,undefined);s.z=360;s.x=trailX(s.z);s.speed=5;interact(s);assert.equal(s.completed.length,0);s.speed=0;interact(s);assert.equal(s.water,84);interact(s);assert.equal(s.water,84);});
test('camp requires every prior objective and completes expedition',()=>{const s=createState();s.z=1470;s.x=trailX(s.z);interact(s);assert.equal(s.won,false);s.completed=[0,1,2,3];assert.equal(interact(s).won,true);assert.equal(s.completed.length,objectives.length);});
test('low range protects suspension while fast offroad driving damages it',()=>{const s=createState();s.x=40;s.speed=15;updateState(s,{},.05);assert.ok(s.health<100);s.health=100;s.low=true;updateState(s,{},.05);assert.equal(s.health,100);});
test('resource exhaustion stops driving',()=>{const s=createState();s.fuel=.001;s.speed=12;updateState(s,{w:true},.05);assert.equal(s.failed,true);assert.equal(s.speed,0);});
