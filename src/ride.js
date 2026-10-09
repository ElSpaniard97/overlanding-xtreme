// Critically damped suspension: stable across different rendering frame rates.
export function dampSpring(value,velocity,target,frequency,dt){
 const offset=value-target,decay=Math.exp(-frequency*dt),term=(velocity+frequency*offset)*dt;
 return {value:target+(offset+term)*decay,velocity:(velocity-frequency*term)*decay};
}
export function followAngle(value,target,rate,dt){
 const difference=Math.atan2(Math.sin(target-value),Math.cos(target-value));
 return value+difference*(1-Math.exp(-rate*dt));
}
export function createRide(){return {x:0,z:0,y:0,velocity:0,pitch:0,roll:0,heading:0,initialized:false};}
export function updateRide(ride,target,dt){
 const snap=!ride.initialized||Math.hypot(target.x-ride.x,target.z-ride.z)>15;
 if(snap){Object.assign(ride,target,{velocity:0,initialized:true});return ride;}
 const blend=1-Math.exp(-18*dt);ride.x+=(target.x-ride.x)*blend;ride.z+=(target.z-ride.z)*blend;
 const spring=dampSpring(ride.y,ride.velocity,target.y,10,dt);ride.y=spring.value;ride.velocity=spring.velocity;
 ride.pitch=followAngle(ride.pitch,target.pitch,5,dt);ride.roll=followAngle(ride.roll,target.roll,5,dt);ride.heading=followAngle(ride.heading,target.heading,14,dt);
 return ride;
}
