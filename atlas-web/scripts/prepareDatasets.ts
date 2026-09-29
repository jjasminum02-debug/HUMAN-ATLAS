import { mkdir, writeFile, readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { createHash } from 'node:crypto';
import { prepareLegacyBody } from './legacyBodyAdapter.ts';
const root=fileURLToPath(new URL('../../',import.meta.url));
const cache=`${root}atlas-data/source-cache/datasets`;
const output=await prepareLegacyBody(root);
await mkdir(`${cache}/bp3d`,{recursive:true});
await writeFile(`${cache}/bp3d/registry.json`,JSON.stringify(output)+'\n');
// The delivery contract is shared. BP3D is a byte-preserving compatibility adapter;
// ZA resources use the new indexed two-LOD contract without rewriting historical GLBs.
const zaPath=`${cache}/za/compiled/manifest.json`;
const zaRaw=await readFile(zaPath);const za=JSON.parse(zaRaw.toString());
const {instances:original,exclusions:_excluded,targetOverlay:_targets,rightsScope:_rights,...rest}=za;
const fields=['sourceKey','sourceName','sourceLabelSide','kind','matrix','lods','canonicalConceptId','learnerBinding','defaultLearnerVisible',
  'appDisplayRights','publicRedistribution','humanReview','sourceHiddenStatePreserved'];
const compact={...rest,instances:original.map((i:Record<string,unknown>)=>Object.fromEntries(fields.map(k=>[k,i[k]])))};
await writeFile(`${cache}/za/registry.json`,JSON.stringify({schemaVersion:1,namespace:za.namespace,manifest:compact,
  dependencies:[{path:zaPath,sha256:createHash('sha256').update(zaRaw).digest('hex')}],
  files:za.chunks.map((c:{id:string})=>({...c,path:`${cache}/za/compiled/${c.id}.glb`}))})+'\n');
await writeFile(`${cache}/index.json`,JSON.stringify({schemaVersion:1,aliases:{body:'bp3d-r4'},datasets:{'bp3d-r4':'bp3d/registry.json',[za.namespace]:'za/registry.json'}})+'\n');
console.log(`Prepared ${output.files.length} verified BP3D chunks; ${output.manifest.chunks.reduce((n,c)=>n+c.assets.length,0)} unchanged asset records; ZA ${za.instances.length} instances`);
