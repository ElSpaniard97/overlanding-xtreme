import {NodeIO} from '@gltf-transform/core';
import {ALL_EXTENSIONS} from '@gltf-transform/extensions';
import {flatten,transformMesh,weld,simplify,dedup,prune,meshopt,getBounds} from '@gltf-transform/functions';
import {MeshoptEncoder,MeshoptSimplifier} from 'meshoptimizer';
import sharp from 'sharp';
import {mkdir,writeFile,stat} from 'node:fs/promises';
const source='.tools/assets/sketchfab-environment',out='public/models/environment';
await mkdir(out,{recursive:true});await Promise.all([MeshoptEncoder.ready,MeshoptSimplifier.ready]);
const io=new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({'meshopt.encoder':MeshoptEncoder});
const definitions=[
 {name:'desert-cliff',file:'cliff',nodes:['P6DesertCliff-High_P6DesertCliffM_0'],author:'WireframeArt',url:'https://sketchfab.com/3d-models/desert-cliff-6-ed2e9c7e976e4768868481e4a5c63f6f',ratio:.4},
 {name:'juniper',file:'trees',nodes:['Object_14','Object_16'],author:'Jagobo',url:'https://sketchfab.com/3d-models/mountain-trees-b914384f931d4b3585bd4f0bf48f0da3',ratio:.4},
 {name:'ponderosa',file:'trees',nodes:['Object_18','Object_20'],author:'Jagobo',url:'https://sketchfab.com/3d-models/mountain-trees-b914384f931d4b3585bd4f0bf48f0da3',ratio:.18},
];
const report=[];
for(const asset of definitions){
 const d=await io.read(`${source}/${asset.file}.glb`);await d.transform(flatten());
 const selected=d.getRoot().listNodes().filter(n=>asset.nodes.includes(n.getName()));if(selected.length!==asset.nodes.length)throw new Error(`Missing parts for ${asset.name}`);
 for(const node of d.getRoot().listNodes())if(!selected.includes(node))node.dispose();
 // Bake world transforms, then normalize height and put the trunk/cliff base at zero.
 for(const n of selected){transformMesh(n.getMesh(),n.getWorldMatrix());n.setTranslation([0,0,0]).setRotation([0,0,0,1]).setScale([1,1,1]);}
 const bounds=getBounds(d.getRoot().getDefaultScene()),height=bounds.max[1]-bounds.min[1],cx=(bounds.max[0]+bounds.min[0])/2,cz=(bounds.max[2]+bounds.min[2])/2;
 for(const n of selected)for(const p of n.getMesh().listPrimitives()){const positions=p.getAttribute('POSITION');for(let i=0;i<positions.getCount();i++){const v=positions.getElement(i,[]);positions.setElement(i,[(v[0]-cx)/height,(v[1]-bounds.min[1])/height,(v[2]-cz)/height]);}}
 await d.transform(weld(),simplify({simplifier:MeshoptSimplifier,ratio:asset.ratio,error:.015}),dedup(),prune());
 const normalTextures=new Set(d.getRoot().listMaterials().flatMap(m=>[m.getNormalTexture(),m.getMetallicRoughnessTexture(),m.getOcclusionTexture()]).filter(Boolean));
 for(const m of d.getRoot().listMaterials()){if(m.getAlphaMode()==='BLEND')m.setAlphaMode('MASK').setAlphaCutoff(.45).setDoubleSided(true);for(const e of m.listExtensions())m.setExtension(e.extensionName,null);}
 for(const t of d.getRoot().listTextures()){const normal=normalTextures.has(t),size=asset.name==='desert-cliff'&&!normal?1024:512;const image=sharp(t.getImage()).resize({width:size,height:size,fit:'inside',withoutEnlargement:true});const bytes=await(normal?image.png({compressionLevel:9}):image.webp({quality:85,alphaQuality:100})).toBuffer();t.setImage(bytes).setMimeType(normal?'image/png':'image/webp');}
 d.getRoot().getAsset().copyright=`${asset.author} · CC BY 4.0 · optimized for Overlanding Xtreme`;
 d.getRoot().setExtras({author:asset.author,source:asset.url,license:'https://creativecommons.org/licenses/by/4.0/',changes:'Selected tree species, normalized scale and pivot, simplified geometry, resized/compressed textures, changed foliage to alpha masking.'});
 await d.transform(prune(),meshopt({encoder:MeshoptEncoder,level:'high'}));await io.write(`${out}/${asset.name}.glb`,d);
 const triangles=d.getRoot().listMeshes().reduce((sum,m)=>sum+m.listPrimitives().reduce((n,p)=>n+p.getIndices().getCount()/3,0),0);
 report.push({name:asset.name,triangles,bytes:(await stat(`${out}/${asset.name}.glb`)).size,bounds:getBounds(d.getRoot().getDefaultScene()),author:asset.author,source:asset.url});
}
await writeFile(`${out}/manifest.json`,JSON.stringify(report,null,2));console.log(report);
