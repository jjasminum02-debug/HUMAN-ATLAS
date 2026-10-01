import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { composeSupplementDataset, composeSupplementRuntime } from './sourceSupplement.ts';
import { resolveSupplementTargetRelations, targetRoutesBySource } from './supplementRelations.ts';
import { buildRuntimeIntegration, datasetRouteQuery, readDatasetRoute, searchStructures } from './integration.ts';
import { DATASET_BUDGET, planLods, validateDataset, type Dataset } from './schema.ts';
import type { SourceSupplement } from './sourceSupplement.ts';

const base=JSON.parse(readFileSync(new URL('../../../../atlas-data/source-cache/datasets/za/compiled/manifest.json',import.meta.url),'utf8')) as Dataset;
const supplement=JSON.parse(readFileSync(new URL('../../../../atlas-data/manifests/bodyparts3d-r4-t100-source-supplement.json',import.meta.url),'utf8')) as SourceSupplement;
const hash=(bytes:Buffer|string)=>createHash('sha256').update(bytes).digest('hex');

test('cached BP3D supplement composes into the existing mixed-frame dataset without changing frozen denominators',()=>{
 const dataset=composeSupplementDataset(base,supplement);
 assert.equal(dataset.namespace,'human-atlas-local');assert.equal(dataset.geometrySpace,'mixed');
 assert.equal(dataset.instances.length,973);assert.equal(dataset.chunks.length,15);
 assert.equal(dataset.instances.filter(row=>row.sourceNamespace==='za-c7010a9').length,960);
 assert.equal(dataset.instances.filter(row=>row.sourceNamespace==='bp3d-r4').length,13);
 assert.equal(supplement.summary.spatiallyAcceptedObjects,0);
 assert.equal(supplement.summary.pelvisSurfaceCandidateObjectsWithoutNamedLandmarkReview,3);
 assert.equal(supplement.summary.crossRegionPlacementUnresolvedObjects,10);
 assert.equal(supplement.objects.filter(row=>row.spatialPlacementStatus==='pelvis_surface_candidate_without_named_landmark_review').length,3);
 assert.equal(supplement.objects.filter(row=>row.spatialPlacementStatus==='cross_region_placement_unresolved').length,10);
 assert.equal((dataset as any).canonicalTargetCount,542);assert.equal((dataset as any).regionMembershipCount,563);
 assert.equal(new Set(dataset.instances.map(row=>row.sourceKey)).size,973);
 assert.equal(dataset.instances.filter(row=>row.sourceNamespace==='bp3d-r4'&&row.geometrySpace==='registered_world'&&row.canonicalConceptId===null&&row.learnerBinding==='source_only_unbound'&&row.defaultLearnerVisible===false&&row.publicRedistribution==='held'&&row.humanReview==='not_performed').length,13);
 assert.equal(supplement.objects.filter(row=>row.targetAssociation.targetId==='TA2:1282').length,3);
 const baseOverview=dataset.chunks.filter(chunk=>chunk.level==='overview'&&!chunk.selectionScoped).reduce((sum,chunk)=>sum+chunk.bytes,0);
 const largestSelectedSupplement=Math.max(...dataset.chunks.filter(chunk=>chunk.selectionScoped).map(chunk=>chunk.bytes));
 assert.ok(baseOverview+largestSelectedSupplement<=DATASET_BUDGET.overviewBytes);
 const hip=dataset.instances.find(row=>row.sourceKey==='BP3D4-FJ3152')!;
 const plan=planLods(dataset,new Set([...dataset.instances.filter(row=>row.sourceNamespace==='za-c7010a9').map(row=>row.sourceKey),hip.sourceKey]),new Set([hip.sourceKey]));
 assert.ok(plan.triangles<=DATASET_BUDGET.triangles);assert.ok(plan.bytes<=DATASET_BUDGET.geometryBytes);
});

test('supplement rejects unverified frame, identity, rights, bindings, and transfer budget',()=>{
 for(const mutate of [
  (x:any)=>x.projectFrame='unknown',
  (x:any)=>x.objects[0].spatialPlacementStatus='anatomically_registered',
  (x:any)=>x.objects[0].sourceIdentity.compiledChunkSha256='0'.repeat(64),
  (x:any)=>x.objects[0].rights.publicRedistribution='approved',
  (x:any)=>x.summary.newCanonicalHaBindings=1,
  (x:any)=>x.chunks[0].bytes=DATASET_BUDGET.chunkBytes+1,
 ]) {
  const copy=structuredClone(supplement);mutate(copy);
  assert.throws(()=>composeSupplementDataset(base,copy));
 }
});

test('composite manifest rejects a bad mixed-coordinate declaration and duplicate source keys',()=>{
 const valid=composeSupplementDataset(base,supplement);
 const badFrame=structuredClone(valid);badFrame.instances.find(row=>row.sourceNamespace==='bp3d-r4')!.geometrySpace='source_local';
 assert.throws(()=>validateDataset(badFrame));
 const duplicate=structuredClone(valid);duplicate.instances.push(duplicate.instances.at(-1)!);
 assert.throws(()=>validateDataset(duplicate));
});

test('supplement relations create opaque target/member routes from exact frozen evidence without HA bindings',()=>{
 const scope=JSON.parse(readFileSync(new URL('../../../../atlas-data/catalog/target-scope-t96.json',import.meta.url),'utf8'));
 const sources=JSON.parse(readFileSync(new URL('../../../../work/evidence/T78/source-elements.json',import.meta.url),'utf8'));
 const relations=resolveSupplementTargetRelations(supplement,{targets:scope.targets,sourceElements:sources,
  evidenceHashes:{targetScope:'a'.repeat(64),sourceElements:'b'.repeat(64)}});
 assert.equal(relations.length,supplement.objects.reduce((n,row)=>n+row.regionIds.length,0));
 assert.equal(new Set(relations.map(row=>row.targetRouteKey)).size,relations.length);
 assert.equal(relations.every(row=>!row.targetRouteKey.includes(row.targetId)&&row.targetRouteKey.startsWith('TR-')),true);
 assert.equal(new Set(relations.map(row=>row.targetId)).size,supplement.summary.targetCount);
 assert.equal(relations.filter(row=>row.targetId==='TA2:1282').length,supplement.sourceGroupMembership!.FMA16580.memberElementFileIds.length);
 assert.equal(relations.filter(row=>row.scope==='bounded_source_group_member').length,supplement.sourceGroupMembership!.FMA16580.memberElementFileIds.length);
 const targetRoutes=targetRoutesBySource(relations);
 const rows=supplement.objects.map(object=>({sourceKey:object.sourceKey,label:object.label,
  routeAudience:'inspection' as const,names:object.names,aliases:object.aliases,localDisplayEligible:true,regionIds:object.regionIds,
  haConceptId:null,side:object.side,targetRoutes:targetRoutes.get(object.sourceKey)!}));
 for(const relation of relations) {
  const route=readDatasetRoute(`?targetPathKey=${relation.targetRouteKey}`,rows,scope.regions.map((r:any)=>r.regionId),'inspection');
  assert.equal(route.selected,relation.sourceKey);assert.equal(route.targetPathKey,relation.targetRouteKey);
  assert.deepEqual(readDatasetRoute('?'+datasetRouteQuery(route),rows,scope.regions.map((r:any)=>r.regionId),'inspection'),route);
  assert.equal(JSON.stringify(route).includes(relation.targetId),false);
 }
 const bad=structuredClone(supplement);bad.objects.find((row:any)=>row.sourceIdentity.sourceElementFileId==='FJ2741')!.side='right';
 assert.throws(()=>resolveSupplementTargetRelations(bad,{targets:scope.targets,sourceElements:sources,evidenceHashes:{x:'a'.repeat(64)}}));
});

test('registered same-bone display alternatives suppress only their ZA counterpart on selected source routes',()=>{
 const scopeBytes=readFileSync(new URL('../../../../atlas-data/catalog/target-scope-t96.json',import.meta.url));
 const scope=JSON.parse(scopeBytes.toString());
 const sources=JSON.parse(readFileSync(new URL('../../../../work/evidence/T78/source-elements.json',import.meta.url),'utf8'));
 const overlayBytes=readFileSync(new URL('../../../../atlas-data/overlays/za-local-integration.json',import.meta.url));
 const zaOverlay=JSON.parse(overlayBytes.toString());
 const supportBytes=readFileSync(new URL('../../../../work/evidence/T78/reference/ta2-scope.json',import.meta.url));
 const supportContext=JSON.parse(supportBytes.toString());
 const rightsBytes=readFileSync(new URL('../../../../'+zaOverlay.policy.rightsEvidence,import.meta.url));
 const dataset=composeSupplementDataset(base,supplement);
 const relationEvidence=resolveSupplementTargetRelations(supplement,{targets:scope.targets,sourceElements:sources,
  evidenceHashes:{...supplement.inputSha256,'atlas-data/source-cache/bodyparts3d-r4/metadata/partof_element_parts.txt':hash(readFileSync(new URL('../../../../atlas-data/source-cache/bodyparts3d-r4/metadata/partof_element_parts.txt',import.meta.url)))}});
 const baseRuntime=buildRuntimeIntegration(zaOverlay,base,hash(overlayBytes),hash(rightsBytes),
  {sha256:hash(scopeBytes),supportContext:{sha256:hash(supportBytes),terms:supportContext},targets:scope.targets});
 const runtime=composeSupplementRuntime(baseRuntime,dataset,supplement,targetRoutesBySource(relationEvidence),'d'.repeat(64),'e'.repeat(64));
 assert.equal(runtime.objects.some(row=>'spatialPlacementStatus' in row),false);
 assert.equal(runtime.objects.filter(row=>row.routeAudience==='inspection').length,13);
 assert.equal(runtime.objects.filter(row=>row.routeAudience==='learner').length,960);
 assert.equal(searchStructures(runtime.objects,'levator veli palatini',[]).some(row=>row.sourceKey.startsWith('BP3D4-')),false);
 assert.equal(searchStructures(runtime.objects,'levator veli palatini',[],'inspection').some(row=>row.sourceKey==='BP3D4-FJ2741'),true);
 for(const row of runtime.objects.filter(row=>row.routeAudience==='inspection')) {
  assert.equal(readDatasetRoute(`?source=${encodeURIComponent(row.sourceKey)}`,runtime.objects,['head','neck','back','thorax','abdomen-lumbar','pelvis-perineum','gluteal-hip','upper-limb','forearm-hand','thigh','leg','foot']).selected,null);
  for(const path of row.targetRoutes) {
   assert.equal(readDatasetRoute(`?regions=${path.regionId}&targetPathKey=${path.key}`,runtime.objects,['head','neck','back','thorax','abdomen-lumbar','pelvis-perineum','gluteal-hip','upper-limb','forearm-hand','thigh','leg','foot']).selected,null);
   const inspected=readDatasetRoute(`?regions=${path.regionId}&targetPathKey=${path.key}`,runtime.objects,['head','neck','back','thorax','abdomen-lumbar','pelvis-perineum','gluteal-hip','upper-limb','forearm-hand','thigh','leg','foot'],'inspection');
   assert.equal(inspected.selected,row.sourceKey);assert.equal(inspected.audience,'inspection');
  }
 }
 const expected=new Map([
  ['BP3D4-FJ3152','ZA-c7010a9-74a765dc396d690d1642153e'],
  ['BP3D4-FJ3288','ZA-c7010a9-ecb65ff4cc3da710e5a2d157'],
  ['BP3D4-FJ3393','ZA-c7010a9-95b8d859c84ae9e56cacdafc'],
 ]);
 for(const [sourceKey,alternativeKey] of expected) {
  const selected=runtime.objects.find(row=>row.sourceKey===sourceKey)!;
  assert.deepEqual(selected.selectionSuppressSourceKeys,[alternativeKey]);
  assert.deepEqual(runtime.objects.find(row=>row.sourceKey===alternativeKey)!.selectionSuppressSourceKeys??[],[]);
 }
 assert.equal(runtime.objects.filter(row=>row.selectionSuppressSourceKeys?.length).length,3);
 const forged=structuredClone(supplement);forged.objects[0].selectionDisplayAlternative!.sourceKeys=['BP3D4-FJ3288'];
 assert.throws(()=>composeSupplementRuntime(baseRuntime,dataset,forged,targetRoutesBySource(relationEvidence),'d'.repeat(64),'e'.repeat(64)));
});
