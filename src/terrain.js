// Shared terrain data keeps rendered rocks and driving collisions aligned.
export const trailX=z=>Math.sin(z/145)*44+Math.sin(z/63)*13;
export const trailHeight=z=>3+z*.012+Math.sin(z/100)*5+Math.sin(z/32)*1.1;
export function alternateX(z){return trailX(z)-Math.sin(Math.PI*Math.max(0,Math.min(1,(z-500)/280)))*26;}
export function routeDistance(x,z){return Math.min(Math.abs(x-trailX(z)),z>500&&z<780?Math.abs(x-alternateX(z)):Infinity);}
export function surfaceHeight(x,z){const side=x-trailX(z),shoulder=Math.max(0,routeDistance(x,z)-11);const rockiness=Math.sin(x*.16+z*.12)*Math.cos(z*.18)*Math.min(1.3,shoulder*.12);const rise=side>35?Math.min(18,shoulder*.08)*(1-smooth(35,130,side))-15*smooth(35,130,side):Math.min(22,shoulder*.14);const climb=z>500&&z<780?Math.sin((z-500)/280*Math.PI)*Math.max(0,1-Math.abs(x-alternateX(z))/10)*3:0;return trailHeight(z)+rise+rockiness+climb;}
function smooth(a,b,x){const t=Math.max(0,Math.min(1,(x-a)/(b-a)));return t*t*(3-2*t);}
export function surfaceAt(x,z){const distance=routeDistance(x,z);const loose=distance>9||z>570&&z<660;return {name:loose?'LOOSE ROCK':'PACKED TRAIL',grip:loose?.48:1,roughness:loose?.8:.15};}
let seed=941;const random=()=>{seed=(seed*1664525+1013904223)>>>0;return seed/4294967296;};
export const obstacles=Array.from({length:105},(_,i)=>{const z=80+random()*1370,side=random()<.5?-1:1;const x=trailX(z)+side*(13+random()*30);return {id:i,x,z,radius:.65+random()*1.1,type:i%4===0?'tree':'rock'};}).filter(o=>routeDistance(o.x,o.z)>10);
