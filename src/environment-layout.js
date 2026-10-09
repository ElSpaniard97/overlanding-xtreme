import {trailX,surfaceHeight,obstacles} from './terrain.js';
// Keep new decorative trunks outside the drivable corridor. Near-trail trees
// use the existing collision positions, so changing their art does not move hazards.
export function environmentLayout(){
 let seed=2871;const random=()=>{seed=(seed*1664525+1013904223)>>>0;return seed/4294967296;};
 const cliffs=[],junipers=[],pines=[];
 for(let z=-35;z<=1550;z+=38){const h=17+random()*9,x=trailX(z)-48-h*1.15;cliffs.push({x,z,y:surfaceHeight(x,z)-3,height:h,rotation:random()*Math.PI*2});}
 for(let i=0;i<30;i++){const z=20+random()*1510,x=trailX(z)+(i%4===0?-1:1)*(235+random()*170);cliffs.push({x,z,y:surfaceHeight(x,z)-6,height:30+random()*32,rotation:random()*Math.PI*2});}
 for(const o of obstacles.filter(o=>o.type==='tree'))junipers.push({x:o.x,z:o.z,y:surfaceHeight(o.x,o.z),height:4.5+random()*2,rotation:random()*Math.PI*2,collisionId:o.id});
 for(let i=0;i<125;i++){const z=-20+random()*1570,side=random()>.45?1:-1,x=trailX(z)+side*(54+random()*60);junipers.push({x,z,y:surfaceHeight(x,z),height:2.5+random()*4.5,rotation:random()*Math.PI*2});}
 for(let i=0;i<28;i++){const ridge=i%2===0,cliff=cliffs[2+i],z=ridge?cliff.z:80+random()*1460,x=ridge?cliff.x:trailX(z)+54+random()*36;pines.push({x,z,y:surfaceHeight(x,z),height:9+random()*6,rotation:random()*Math.PI*2,ridge});}
 return {cliffs,junipers,pines};
}
