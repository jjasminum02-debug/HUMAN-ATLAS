import assert from 'node:assert/strict';
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { resolve, join } from 'node:path';
import { compilerFixture } from './anchorCompilerFixtures.ts';
import { runAnchorCompiler, type RuleDocument } from './compileAcupointAnchors.ts';
import { compilePlacementUnit, type PlacementUnit } from '../src/viewer/acupoints/anchorCompiler.ts';
import { migratePlacementDocument, sha256 } from '../src/viewer/acupoints/placementMigration.ts';
import { projectLearnerInstances } from '../src/viewer/acupoints/placementPolicy.ts';
import type { Carrier, PointConcept, PointInstance } from '../src/viewer/acupoints/schema.ts';

const out=resolve('../work/evidence/AT5');await mkdir(out,{recursive:true});
const receipts:unknown[]=[];
for(const side of ['right','left']) {
  const source=resolve(`../work/evidence/acupoint-AC2/${side}-learning.json`),bytes=await readFile(source);
  const original=JSON.parse(bytes.toString()) as {carrier:Carrier;instances:PointInstance[];concepts:PointConcept[]};
  const migration=await migratePlacementDocument(bytes),carrier=original.carrier;
  await writeFile(join(out,`${side}-learning-v2.json`),JSON.stringify(migration.document,null,2)+'\n');
  const context={datasetRevision:carrier.datasetRevision,frameId:carrier.frameId,unit:carrier.unit,poseId:carrier.poseId};
  const units:PlacementUnit[]=original.instances.map(i=>{
    const concept=original.concepts.find(c=>c.code===i.code)!;
    return {id:`${i.code}-${side}`,scope:'real_input',code:i.code,side:i.side,revision:'AT5-legacy-assessment',context,carrierId:carrier.id,
      originalText:concept.location!.text,originalSources:concept.location!.sources,author:i.aiProposal?'ai':'human',professorReview:i.professorReview,
      landmarks:[],rule:{kind:'bounds'},relationEvidenceId:'not-yet-verified',surfaceEvidenceId:'not-yet-verified'};
  });
  const doc:RuleDocument={schemaVersion:2,context,units,inputs:{domain:'real_input',carriers:{[carrier.id]:carrier},native:{},evidence:[]}};
  const input=join(out,`${side}-rules.json`);await writeFile(input,JSON.stringify(doc,null,2)+'\n');
  const receipt=await runAnchorCompiler(input,join(out,`${side}-compiler`));
  assert.equal(receipt.failed.length,11);assert.equal(receipt.localLearnerEligible,0);
  const resumed=await runAnchorCompiler(input,join(out,`${side}-compiler`),true);assert.equal(resumed.executed.length,11);assert.equal(resumed.reused.length,0);
  const projection=await projectLearnerInstances(carrier,migration.document.instances,{...context,motionActive:false});
  assert.equal(projection.instances.length,0);assert.equal(await sha256(await readFile(source)),migration.sourceSha256);
  receipts.push({side,sourceSha256:migration.sourceSha256,originalUnchanged:true,realInputCount:11,localLearnerEligible:0,receipt});
}
const fixtureReceipts=[];
for(const kind of ['landmark','B-cun','F-cun','midline'] as const) {
  const f=await compilerFixture(kind),r=await compilePlacementUnit(f.unit,f.inputs);assert.equal(r.status,'passed');
  const input=join(out,`fixture-${kind}-rules.json`),doc:RuleDocument={schemaVersion:2,context:f.context,units:[f.unit],inputs:f.inputs};
  await writeFile(input,JSON.stringify(doc,null,2)+'\n');
  const receipt=await runAnchorCompiler(input,join(out,`fixture-${kind}-compiler`));assert.equal(receipt.localLearnerEligible,0);
  fixtureReceipts.push({kind,status:r.status,basis:r.assessment.basis,fixtureOnly:true,receipt});
}
const f=await compilerFixture('B-cun'),bad={...structuredClone(f.unit),id:'failed-retry',rule:{kind:'unresolved' as const}};
const resumeInput=join(out,'resume-rules.json');
await writeFile(resumeInput,JSON.stringify({schemaVersion:2,context:f.context,units:[f.unit,bad],inputs:f.inputs},null,2)+'\n');
const first=await runAnchorCompiler(resumeInput,join(out,'resume-compiler'));
await writeFile(resumeInput,JSON.stringify({schemaVersion:2,context:f.context,units:[f.unit,{...bad,rule:f.unit.rule}],inputs:f.inputs},null,2)+'\n');
const second=await runAnchorCompiler(resumeInput,join(out,'resume-compiler'),true);
assert.deepEqual(second.executed,['failed-retry']);assert.deepEqual(second.reused,[f.unit.id]);
assert.equal(first.originalPreserved,true);assert.equal(second.originalPreserved,true);
const summary={passed:true,compiler:'explicit-landmarks-2.0',realInputCount:22,realInputAccepted:0,legacyUnresolvedPreserved:22,
  positiveTechnicalFixtures:4,fixturesExported:0,actual:receipts,fixtures:fixtureReceipts,resume:{first,second},
  remainingLocationInputs:['LU1–11 each side: point-specific annotated landmarks, source relation and surface registration; no bounds promotion',
    'B-cun: actual crease/segment endpoint annotations with source denominator and connected surface path',
    'F-cun: actual model finger-cun calibration, radial nail corner orientation and supported skin',
    'oral/perineum: supported target surface and meaningful native landmark, never substitute another envelope']};
await writeFile(join(out,'compiler-validation.json'),JSON.stringify(summary,null,2)+'\n');console.log(JSON.stringify({passed:true,realInputCount:22,realInputAccepted:0,positiveTechnicalFixtures:4,failedOnlyResume:true}));
