import {NodeIO,Document} from '@gltf-transform/core';
import {ALL_EXTENSIONS} from '@gltf-transform/extensions';
import {mergeDocuments,weld,simplify,dedup,prune,unpartition,meshopt} from '@gltf-transform/functions';
import {MeshoptEncoder,MeshoptDecoder,MeshoptSimplifier} from 'meshoptimizer';
import {readFile,writeFile} from 'node:fs/promises';
const input='.tools/assets/4runner/prepared',output='public/models/4runner.glb';
await Promise.all([MeshoptEncoder.ready,MeshoptDecoder.ready,MeshoptSimplifier.ready]);
const io=new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({'meshopt.encoder':MeshoptEncoder,'meshopt.decoder':MeshoptDecoder});
const doc=new Document(),scene=doc.createScene('Toyota 4Runner');doc.getRoot().setDefaultScene(scene);
doc.getRoot().getAsset().copyright='Toyota_4runner by sadiqminhas911 · CC BY 4.0 · simplified and adapted';
doc.getRoot().setExtras({author:'sadiqminhas911',source:'https://sketchfab.com/3d-models/toyota-4runner-3afb8daa0a4a4bfea99e1af74eca1bdb',license:'https://creativecommons.org/licenses/by/4.0/',changes:'Separated wheels, simplified geometry, Meshopt compression and material adjustments.'});
const setup=JSON.parse(await readFile(`${input}/setup.json`,'utf8'));
for(const part of ['Body','FL','FR','RL','RR']){
 const source=await io.read(`${input}/FourRunner_${part}.gltf`);
 await source.transform(weld(),simplify({simplifier:MeshoptSimplifier,ratio:part==='Body'?.12:.08,error:.008}));
 const map=mergeDocuments(doc,source),node=map.get(source.getRoot().listNodes()[0]);
 node.setName(part).setRotation([0,Math.sin(Math.PI/4),0,Math.cos(Math.PI/4)]);
 if(part!=='Body'){const [forward,right,up]=setup.wheel_centers_cm[part];node.setTranslation([right/100,up/100,-forward/100]);}
 for(const old of doc.getRoot().listScenes())if(old!==scene)old.dispose();
 scene.addChild(node);
}
for(const m of doc.getRoot().listMaterials()){
 for(const extension of m.listExtensions())m.setExtension(extension.extensionName,null);
 m.setDoubleSided(false);
 if(m.getName()==='Main_Paint')m.setBaseColorFactor([.52,.43,.29,1]).setRoughnessFactor(.38).setMetallicFactor(.25);
 if(m.getName()==='Glass')m.setBaseColorFactor([.025,.055,.065,1]).setAlphaMode('OPAQUE').setRoughnessFactor(.15).setMetallicFactor(.5);
 if(m.getName()==='Tyres'||m.getName()==='Black')m.setBaseColorFactor([.016,.02,.018,1]).setRoughnessFactor(.88).setMetallicFactor(0);
}
await doc.transform(dedup(),prune(),unpartition(),meshopt({encoder:MeshoptEncoder,level:'high'}));
await io.write(output,doc);
const triangles=doc.getRoot().listMeshes().reduce((sum,m)=>sum+m.listPrimitives().reduce((n,p)=>n+p.getIndices().getCount()/3,0),0);
const bytes=(await readFile(output)).length;await writeFile('public/models/4runner-info.json',JSON.stringify({triangles,bytes,sourceTriangles:878504,parts:['Body','FL','FR','RL','RR']},null,2));console.log({output,triangles,bytes});
