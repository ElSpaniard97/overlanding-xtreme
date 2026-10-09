import * as THREE from 'three';
import {Water} from 'three/addons/objects/Water.js';
export function createReflectiveWater(scene,river){
 const size=128,data=new Uint8Array(size*size*4);for(let y=0;y<size;y++)for(let x=0;x<size;x++){const i=(y*size+x)*4;data[i]=128+Math.sin(x*Math.PI/16+y*Math.PI/32)*22;data[i+1]=128+Math.cos(y*Math.PI/16-x*Math.PI/32)*22;data[i+2]=250;data[i+3]=255;}
 const normals=new THREE.DataTexture(data,size,size);normals.wrapS=normals.wrapT=THREE.RepeatWrapping;normals.needsUpdate=true;
 const water=new Water(river.geometry,{textureWidth:256,textureHeight:256,waterNormals:normals,sunDirection:new THREE.Vector3(-.4,.2,-1).normalize(),sunColor:0xffce93,waterColor:0x426b71,distortionScale:1.8,fog:true});water.position.copy(river.position);water.rotation.copy(river.rotation);water.visible=false;scene.add(water);
 return {quality(value){water.visible=value==='high';river.visible=!water.visible;},update(dt){water.material.uniforms.time.value+=dt*.4;}};
}
