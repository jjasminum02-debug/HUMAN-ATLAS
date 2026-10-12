import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {replayTerritoryBoundary} from '../../../../atlas-web/src/viewer/acupoints/territoryBoundary.ts';
import {territoryEdges,maskContentHash,validateTerritoryMask} from '../../../../atlas-web/src/viewer/acupoints/territoryMask.ts';
import type {TerritoryBoundaryDraft} from '../../../../atlas-web/src/viewer/acupoints/territoryBoundary.ts';
import type {TerritoryMask,Carrier} from '../../../../atlas-web/src/viewer/acupoints/schema.ts';
const root=fileURLToPath(new URL('../../../../',import.meta.url));
const read=(p:string)=>JSON.parse(readFileSync(root+p,'utf8')),sha=(p:string)=>createHash('sha256').update(readFileSync(root+p)).digest('hex');
const rules=read('work/evidence/AT6/resume-r1/bilateral-rules-r9.json');const masks:TerritoryMask[]=[],audit=[];
for(const input of ['atlas-data/acupoints/territories/AT20-r1/lung-forearm-right-boundary-r1.json','work/evidence/AT21/run-r1/left-boundary-r1.json']) {
  const d=read(input) as TerritoryBoundaryDraft;const c=rules.inputs.carriers[d.carrierBinding.id] as Carrier;
  const replay=await replayTerritoryBoundary(d,c,rules.context);const original=read(input);
  if(replay.faceSetSha256!==original.handoff.candidateFaceSetSha256||replay.triangleIds.length!==original.handoff.expectedFaceCountForReplay)throw Error('Boundary replay differs');
  const edge=territoryEdges(replay,c),boundary=new Set(edge),used=new Set(replay.triangleIds.flatMap(f=>c.indices.slice(f*3,f*3+3)));
  const neighbors=new Map<number,Set<number>>();for(const f of replay.triangleIds){const t=c.indices.slice(f*3,f*3+3);for(const v of t){const n=neighbors.get(v)??new Set<number>();t.forEach(w=>n.add(w));neighbors.set(v,n);}}
  const vertexWeights:[number,number][]=[...used].sort((a,b)=>a-b).map(v=>[v,boundary.has(v)?.22:[...neighbors.get(v)!].some(w=>boundary.has(w))?.65:1]);
  const m:TerritoryMask={schemaVersion:1,scope:'real_input',id:d.id,channel:d.channel,side:d.side,revision:'lung-surface-r1',kind:d.kind,carrierId:c.id,carrierRevision:c.revision,carrierHash:c.topologySha256,datasetRevision:c.datasetRevision,frameId:c.frameId,unit:'m',poseId:c.poseId,boundaryRevision:d.boundaryRevision,triangleIds:replay.triangleIds,vertexWeights,sources:d.sources.map(s=>({id:s.id,title:s.title,edition:s.edition,locator:s.locator,url:s.url})),interpretation:d.interpretation,professorReview:d.professorReview,basisKind:d.basisKind,author:d.author,precision:d.precision,canonicalBoundaryClaim:false,rights:d.rights,boundaryInputSha256:sha(input),faceSetSha256:replay.faceSetSha256,contentSha256:''};
  m.contentSha256=await maskContentHash(m);await validateTerritoryMask(m,c,rules.context);masks.push(m);
  audit.push({side:d.side,controls:replay.controlPositions.length,faces:m.triangleIds.length,edges:edge.length/2,usedVertices:used.size,input,maskHash:m.contentSha256,carrierHash:c.topologySha256,sourceBoundaryConfirmed:false,pointCoordinatesChanged:0});
}
const out=root+'atlas-data/acupoints/territories/lung-r1';mkdirSync(out,{recursive:true});
writeFileSync(out+'/masks.json',JSON.stringify({schemaVersion:1,usage:'local_learning_areas',...rules.context,masks})+'\n');
writeFileSync(root+'work/evidence/AT21/run-r1/mask-compilation-r1.json',JSON.stringify({masks:audit,finalMasks:2,channels:1,completeLUTerritories:0,fixtureExports:0,originalPointHash:sha('atlas-data/acupoints/learner/lung-r7.json')},null,2)+'\n');
console.log('PASS: shared compiler replay → two independent real-input partial LU masks; no point changes');
