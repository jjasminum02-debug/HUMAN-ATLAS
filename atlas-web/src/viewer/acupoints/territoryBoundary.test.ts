import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import type {Carrier} from './schema.ts';
import type {TerritoryBoundaryDraft} from './territoryBoundary.ts';
import {validateTerritoryBoundary} from './territoryBoundary.ts';
const root=fileURLToPath(new URL('../../../../',import.meta.url));
const read=(p:string)=>JSON.parse(readFileSync(root+p,'utf8'));
const draft=read('atlas-data/acupoints/territories/AT20-r1/lung-forearm-right-boundary-r1.json') as TerritoryBoundaryDraft;
const rules=read('work/evidence/AT6/resume-r1/bilateral-rules-r9.json');
const carrier=rules.inputs.carriers[draft.carrierBinding.id] as Carrier;
const check=(d=draft,c=carrier)=>validateTerritoryBoundary(d,c,rules.context);
test('real LU boundary resolves 65 controls and encloses 351 faces; emits no mask',async()=>{
 const out=await check();assert.deepEqual(out.componentCounts,[351]);assert.equal(out.controlPositions.length,65);
 assert.equal(out.faceSetSha256,(draft as typeof draft&{handoff:{candidateFaceSetSha256:string}}).handoff.candidateFaceSetSha256);
 assert.equal(out.maskCreated,false);assert.equal(out.sourceBoundaryConfirmed,false);
});
const cases:[string,(d:TerritoryBoundaryDraft,c:Carrier)=>void][]=[
 ['stale frame',d=>{d.context.frameId='wrong';}],['stale pose',d=>{d.context.poseId='wrong';}],
 ['stale topology',d=>{d.carrierBinding.topologySha256='0'.repeat(64);}],
 ['changed geometry bytes',(_,c)=>{c.positions[0]+=.001;}],['wrong side',d=>{d.side='left';}],
 ['rights held',d=>{d.rights.localObservation='held';}],['carrier rights held',(_,c)=>{c.rights.localObservation='held';}],
 ['absent author',d=>{delete (d as Partial<TerritoryBoundaryDraft>).author;}],
 ['source certainty relabel',d=>{Object.assign(d,{canonicalBoundaryClaim:true});}],
 ['theory conflation',d=>{d.basisKind='cutaneous';}],
 ['unknown channel',d=>{d.channel='EX';}],
 ['CV fictitious jingjin',d=>{d.channel='CV';d.basisKind='sinew_projection';}],
 ['missing hole',d=>{d.components[0].loops.pop();}],['wrong outside seed',d=>{d.components[0].seedTriangle=1800;}],
 ['unsupported shortcut',d=>{d.components[0].loops[0].controls.splice(2,3);}],
 ['duplicate pinched vertex',d=>{d.components[0].loops[0].controls.push(d.components[0].loops[0].controls[0]);}],
 ['moved control anchor',d=>{d.components[0].loops[0].controls[0].anchor.barycentric=[1/3,1/3,1/3];}],
 ['unregistered component',d=>{d.components[0].carrierId='finger-right-1-0';}],
];
for(const [name,mutate] of cases)test(`reject ${name}`,async()=>{const d=structuredClone(draft),c=structuredClone(carrier);mutate(d,c);await assert.rejects(check(d,c));});
test('professor/public state is independent of local AI boundary technical replay',async()=>{const d=structuredClone(draft);d.professorReview='not_performed';d.rights.publicRedistribution='held';assert.equal((await check(d)).componentCounts[0],351);assert.equal(d.author,'ai');});
