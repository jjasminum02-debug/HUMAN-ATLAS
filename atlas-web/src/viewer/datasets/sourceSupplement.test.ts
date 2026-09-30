import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { composeSupplementDataset } from './sourceSupplement.ts';
import { DATASET_BUDGET, planLods, validateDataset, type Dataset } from './schema.ts';
import type { SourceSupplement } from './sourceSupplement.ts';

const base=JSON.parse(readFileSync(new URL('../../../../atlas-data/source-cache/datasets/za/compiled/manifest.json',import.meta.url),'utf8')) as Dataset;
const supplement=JSON.parse(readFileSync(new URL('../../../../atlas-data/manifests/bodyparts3d-r4-t100-source-supplement.json',import.meta.url),'utf8')) as SourceSupplement;

test('cached BP3D supplement composes into the existing mixed-frame dataset without changing frozen denominators',()=>{
 const dataset=composeSupplementDataset(base,supplement);
 assert.equal(dataset.namespace,'human-atlas-local');assert.equal(dataset.geometrySpace,'mixed');
 assert.equal(dataset.instances.length,973);assert.equal(dataset.chunks.length,15);
 assert.equal(dataset.instances.filter(row=>row.sourceNamespace==='za-c7010a9').length,960);
 assert.equal(dataset.instances.filter(row=>row.sourceNamespace==='bp3d-r4').length,13);
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
