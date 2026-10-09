import * as THREE from 'three';
// Deterministic mineral grains, embedded gravel and erosion. No downloaded textures.
export function createGroundMaterial(){
 const size=1024,canvas=document.createElement('canvas'),height=document.createElement('canvas');canvas.width=canvas.height=height.width=height.height=size;
 const c=canvas.getContext('2d'),h=height.getContext('2d');let seed=391;const random=()=>{seed=(seed*1664525+1013904223)>>>0;return seed/4294967296;};
 c.fillStyle='#b09a7d';c.fillRect(0,0,size,size);h.fillStyle='#808080';h.fillRect(0,0,size,size);
 for(let i=0;i<85000;i++){const x=random()*size,y=random()*size,r=.3+random()*1.7,v=90+random()*90;c.fillStyle=`rgba(${v+25},${v+12},${v},.24)`;c.fillRect(x,y,r,r);h.fillStyle=`rgb(${v},${v},${v})`;h.fillRect(x,y,r,r);}
 for(let i=0;i<1600;i++){const x=random()*size,y=random()*size,r=1+random()*7,angle=random()*Math.PI;const v=85+random()*55;for(const [ctx,color] of [[c,`rgb(${v+26},${v+12},${v})`],[h,'#b0b0b0']]){ctx.fillStyle=color;ctx.beginPath();ctx.ellipse(x,y,r,r*.55,angle,0,Math.PI*2);ctx.fill();}c.strokeStyle='#e2ccaa88';c.lineWidth=.7;c.stroke();}
 for(let i=0;i<55;i++){const x=random()*size,y=random()*size;for(const [ctx,color] of [[c,'#5d4d3b25'],[h,'#666666']]){ctx.strokeStyle=color;ctx.lineWidth=.7+random();ctx.beginPath();ctx.moveTo(x,y);for(let j=1;j<6;j++)ctx.lineTo(x+j*9,y+Math.sin(j*2+i)*5+j*3);ctx.stroke();}}
 const texture=new THREE.CanvasTexture(canvas),bump=new THREE.CanvasTexture(height);for(const t of [texture,bump]){t.wrapS=t.wrapT=THREE.RepeatWrapping;t.anisotropy=8;}texture.colorSpace=THREE.SRGBColorSpace;
 const material=new THREE.MeshStandardMaterial({vertexColors:true,map:texture,bumpMap:bump,bumpScale:.065,roughness:.96});
 material.onBeforeCompile=shader=>{
 shader.vertexShader=shader.vertexShader.replace('#include <common>','#include <common>\nvarying vec2 groundWorld;').replace('#include <begin_vertex>','#include <begin_vertex>\ngroundWorld=position.xz;');
 shader.fragmentShader=shader.fragmentShader.replace('#include <common>',`#include <common>
 varying vec2 groundWorld;
 float groundHash(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
 float groundNoise(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(groundHash(i),groundHash(i+vec2(1,0)),f.x),mix(groundHash(i+vec2(0,1)),groundHash(i+vec2(1)),f.x),f.y);}`);
 shader.fragmentShader=shader.fragmentShader.replace('#include <map_fragment>',`#include <map_fragment>
 float mineral=groundNoise(groundWorld*.09)*.65+groundNoise(groundWorld*.31)*.35;
 vec3 detail=texture2D(map,vMapUv*5.7).rgb;
 diffuseColor.rgb*=mix(vec3(.76,.72,.67),vec3(1.18,1.13,1.04),mineral);
 diffuseColor.rgb*=mix(vec3(.82),detail*1.65,.22);`);
 };material.customProgramCacheKey=()=> 'layered-desert-ground-v1';return material;
}
