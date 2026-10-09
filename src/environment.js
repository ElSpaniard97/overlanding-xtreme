import * as THREE from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {MeshoptDecoder} from 'three/addons/libs/meshopt_decoder.module.js';
import {environmentLayout} from './environment-layout.js';

function instanceAsset(model,placements,parent){
 model.updateMatrixWorld(true);const meshes=[];model.traverse(o=>{if(o.isMesh)meshes.push(o);});
 const tiles=new Map(),dummy=new THREE.Object3D();
 for(const placement of placements){const tile=Math.floor(placement.z/180);if(!tiles.has(tile))tiles.set(tile,[]);tiles.get(tile).push(placement);}
 for(const [tile,points] of tiles){const group=new THREE.Group();group.userData.routeZ=tile*180+90;
 for(const mesh of meshes){const geometry=mesh.geometry.clone().applyMatrix4(mesh.matrixWorld),material=mesh.material.clone();if(material.map)material.map.anisotropy=4;if(material.alphaTest>0){material.transparent=false;material.alphaTest=.3;material.alphaToCoverage=true;material.color.multiply(new THREE.Color('#b8c9a7'));}const instances=new THREE.InstancedMesh(geometry,material,points.length);
 for(let i=0;i<points.length;i++){const p=points[i];dummy.position.set(p.x,p.y,-p.z);dummy.rotation.set(0,p.rotation,0);dummy.scale.setScalar(p.height);dummy.updateMatrix();instances.setMatrixAt(i,dummy.matrix);}instances.castShadow=true;instances.receiveShadow=true;instances.computeBoundingSphere();group.add(instances);}
 parent.add(group);}
}
export function createEnvironment(scene){
 const group=new THREE.Group();group.name='Textured Sketchfab scenery';scene.add(group);let quality='medium',routeZ=0;
 const layout=environmentLayout();const state={cliffs:false,trees:false};
 const loader=new GLTFLoader().setMeshoptDecoder(MeshoptDecoder);const load=name=>loader.loadAsync(`${import.meta.env.BASE_URL}models/environment/${name}.glb`);
 const cliffReady=load('desert-cliff').then(gltf=>{instanceAsset(gltf.scene,layout.cliffs,group);state.cliffs=true;});
 const ready=Promise.allSettled([
 cliffReady,
 Promise.all([load('juniper'),load('ponderosa')]).then(async([juniper,pine])=>{await cliffReady.catch(()=>{});if(state.cliffs){group.updateMatrixWorld(true);const ray=new THREE.Raycaster();for(const p of layout.pines.filter(p=>p.ridge)){ray.set(new THREE.Vector3(p.x,p.y+80,-p.z),new THREE.Vector3(0,-1,0));const hit=ray.intersectObject(group,true)[0];if(hit)p.y=hit.point.y-.08;}}instanceAsset(juniper.scene,layout.junipers,group);instanceAsset(pine.scene,layout.pines,group);state.trees=true;})
 ]).then(results=>{for(const result of results)if(result.status==='rejected')console.warn('Scenery fallback:',result.reason);return {...state};});
 return {ready,state,quality(value){quality=value;},update(z){routeZ=z;const range=quality==='low'?330:quality==='high'?850:550;for(const tile of group.children){tile.visible=Math.abs(tile.userData.routeZ-routeZ)<range;tile.children.forEach(mesh=>mesh.castShadow=quality!=='low');}}};
}
