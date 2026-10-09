import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {NodeIO} from '@gltf-transform/core';
import {ALL_EXTENSIONS} from '@gltf-transform/extensions';
import {MeshoptDecoder} from 'meshoptimizer';
test('web 4Runner decodes within its download and triangle budgets with all separate wheels',async()=>{
 const bytes=await readFile(new URL('../public/models/4runner.glb',import.meta.url));assert.ok(bytes.length<2_000_000);
 await MeshoptDecoder.ready;const doc=await new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({'meshopt.decoder':MeshoptDecoder}).readBinary(bytes);
 const parts=doc.getRoot().getDefaultScene().listChildren();assert.deepEqual(parts.map(n=>n.getName()).sort(),['Body','FL','FR','RL','RR']);
 const triangles=doc.getRoot().listMeshes().reduce((sum,m)=>sum+m.listPrimitives().reduce((n,p)=>n+p.getIndices().getCount()/3,0),0);assert.ok(triangles<180_000&&triangles>20_000);
 for(const part of parts.filter(n=>n.getName()!=='Body')){const [x,y,z]=part.getTranslation();assert.ok(Math.abs(x)>.7&&Math.abs(x)<1);assert.ok(y>.4&&y<.5);assert.ok(part.getName().startsWith('F')?z<0:z>0);}
 assert.match(doc.getRoot().getAsset().copyright,/sadiqminhas911/);assert.match(doc.getRoot().getExtras().license,/creativecommons/);
});

import {environmentLayout} from '../src/environment-layout.js';
import {obstacles,trailX} from '../src/terrain.js';
test('textured scenery decodes with small textures, normalized pivots and attribution',async()=>{
 const io=new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({'meshopt.decoder':MeshoptDecoder});await MeshoptDecoder.ready;let total=0;
 for(const name of ['desert-cliff','juniper','ponderosa']){const bytes=await readFile(new URL(`../public/models/environment/${name}.glb`,import.meta.url));total+=bytes.length;const d=await io.readBinary(bytes);assert.match(d.getRoot().getAsset().copyright,/CC BY 4.0/);assert.match(d.getRoot().getExtras().license,/creativecommons/);assert.ok(d.getRoot().listTextures().length>=2);for(const t of d.getRoot().listTextures())assert.ok(t.getSize().every(n=>n<=1024));for(const m of d.getRoot().listMaterials())assert.notEqual(m.getAlphaMode(),'BLEND');const {getBounds}=await import('@gltf-transform/functions');const b=getBounds(d.getRoot().getDefaultScene());assert.ok(Math.abs(b.min[1])<.001);assert.ok(Math.abs(b.max[1]-1)<.001);const triangles=d.getRoot().listMeshes().reduce((sum,m)=>sum+m.listPrimitives().reduce((n,p)=>n+p.getIndices().getCount()/3,0),0);assert.ok(triangles<20000);}
 assert.ok(total<3_500_000);
});
test('scenery tree replacements match every collision tree and keep new trunks outside the driving corridor',()=>{
 const layout=environmentLayout();assert.deepEqual(layout,environmentLayout());const replacement=layout.junipers.filter(p=>p.collisionId!==undefined);assert.equal(replacement.length,obstacles.filter(o=>o.type==='tree').length);for(const p of replacement){const o=obstacles.find(o=>o.id===p.collisionId);assert.equal(p.x,o.x);assert.equal(p.z,o.z);}for(const p of [...layout.junipers.filter(p=>p.collisionId===undefined),...layout.pines])assert.ok(Math.abs(p.x-trailX(p.z))>=54);for(const p of [...layout.cliffs,...layout.junipers,...layout.pines])assert.ok([p.x,p.y,p.z,p.height,p.rotation].every(Number.isFinite));
});
