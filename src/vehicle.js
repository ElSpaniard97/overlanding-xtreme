import * as THREE from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {MeshoptDecoder} from 'three/addons/libs/meshopt_decoder.module.js';
export async function loadFourRunner(car){
 const gltf=await new GLTFLoader().setMeshoptDecoder(MeshoptDecoder).loadAsync(`${import.meta.env.BASE_URL}models/4runner.glb`);
 const visual=gltf.scene,wheels=[];visual.updateMatrixWorld(true);
 for(const name of ['FL','FR','RL','RR']){const node=visual.getObjectByName(name);if(!node)throw new Error('Missing wheel '+name);const pivot=new THREE.Group(),rolling=new THREE.Group();pivot.position.copy(node.position);const baseY=pivot.position.y;node.position.set(0,0,0);visual.remove(node);rolling.add(node);pivot.add(rolling);visual.add(pivot);wheels.push({side:name.endsWith('L')?-1:1,z:pivot.position.z,pivot,rolling,baseY,radius:.421});}
 visual.traverse(o=>{if(o.isMesh){o.castShadow=true;o.receiveShadow=true;}});
 // Keep a roof rack and expedition supplies on the imported rig.
 const gear=new THREE.Group();const metal=new THREE.MeshStandardMaterial({color:'#242c28',roughness:.7,metalness:.3});
 const box=(w,h,d,m,x,y,z)=>{const mesh=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),m);mesh.position.set(x,y,z);mesh.castShadow=true;gear.add(mesh);};
 box(1.5,.09,2,metal,0,1.98,.15);for(const x of [-.72,.72])box(.06,.13,2.05,metal,x,2.05,.15);
 box(.85,.28,1,new THREE.MeshStandardMaterial({color:'#9c8c64',roughness:1}),-.25,2.17,.4);box(.55,.23,.6,new THREE.MeshStandardMaterial({color:'#626b50',roughness:1}),.4,2.15,-.5);visual.add(gear);
 for(const child of [...car.children]){car.remove(child);child.traverse(o=>{o.geometry?.dispose();});}car.add(visual);car.userData.wheels=wheels;car.userData.detailed=true;car.userData.radius=.421;
 const brakeMaterials=[];visual.traverse(o=>{if(o.isMesh&&o.material.name==='Tail_Lights'){o.material=o.material.clone();o.material.emissive.set('#ff2710');brakeMaterials.push(o.material);}});car.userData.brakeMaterials=brakeMaterials;
 return visual;
}
