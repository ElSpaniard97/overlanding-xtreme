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
