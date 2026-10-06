import { readFile, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createHash } from 'node:crypto';
import runtime from '../src/data/learnerMotionRuntime.generated.ts';
import { resolveLearnerMotionCandidate } from '../src/domain/motionLearning.ts';
const root=fileURLToPath(new URL('../../',import.meta.url));
const read=async(p:string)=>JSON.parse(await readFile(resolve(root,p),'utf8'));
const pointer=await read('atlas-web/dist-local/CURRENT.json');
const packagePath='atlas-web/dist-local/'+pointer.snapshotDirectory;
const manifest=await read(packagePath+'/snapshot.json');
const integration=await read(packagePath+'/public/__atlas/integration.json');
const card=await read('atlas-data/terminology/learner-card-runtime.json');
const sourceCourse=await read('work/evidence/T66/implementation-2026-10-02/nerve-course-and-entrapment-ledger.json');
const currentCourse=await read('atlas-data/terminology/nerve-learning-t66.json');
const courseEvidence=await read('work/evidence/T66/nerve-learning-2026-10-05/nerve-relation-ledger.json');
const additionalCourseNames=Object.entries(courseEvidence.learnerFieldEvidence).filter(([key])=>key.endsWith(':courseContext')).map(([key,row]:[string,any])=>{
  const name=key.slice(0,-':courseContext'.length),text=currentCourse[name]?.courseContext;
  if(createHash('sha256').update(text??'').digest('hex')!==row.valueSha256)throw Error('Changed nerve course field '+name);
  return name;
});
const courseNames=new Set([...sourceCourse.rows.filter((r:any)=>r.courseTextSupport!=='observed_static_model_context').map((r:any)=>r.sourceNativeName),...additionalCourseNames]);
const graph=await read('atlas-data/terminology/learner-nerve-graph-t66.json');
const priority=await read('work/evidence/T66/priority-integration-2026-10-05/runtime-scope-audit.json');
const accepts=(side:string|null,row:any)=>!side||!row.sideApplicability||['bilateral','midline',side].includes(row.sideApplicability);
const main=(runtime as any).actions,wave=(runtime as any).wave1Actions;
const rows:any[]=[];
for(const object of integration.objects.filter((r:any)=>r.localDisplayEligible)){
  const source=object.sourceKey,concept=object.haConceptId,side=object.side;
  const selector=main[source]?.length?source:concept??source;
  const projected=(main[selector]??[]).filter((r:any)=>!r.candidate||r.candidate.asset.sourceBinding?.subjectSourceKey===source);
  const sourceRows=projected.filter((r:any)=>accepts(side,r)).map((r:any)=>({...r,id:r.actionKey}));
  const conceptRows=card.actions.filter((r:any)=>r.conceptId===concept&&accepts(side,r)).map((r:any)=>({
    id:r.key,label:r.label,learningIntent:'muscle_action',text:{explanation:r.explanation},candidate:resolveLearnerMotionCandidate(r.key,side,projected)}));
  const options=[...new Map([...(concept&&selector===concept?conceptRows:sourceRows),...(wave[source]??[]).filter((r:any)=>accepts(side,r))].map((r:any)=>[r.id,r])).values()];
  const text=card.structure.bySource[source]??card.structure.byConcept[concept]??{};
  rows.push({sourceKey:source,kind:object.kind,side,searchGroupKey:object.searchGroupKey,regionIds:object.regionIds,
    text:{origin:!!text.origin,insertion:!!text.insertion,actionOptionsWithExplanation:options.filter((r:any)=>!!r.text?.explanation).length},
    options:options.map((r:any)=>({id:r.id,label:r.label,learningIntent:r.learningIntent??'posture_observation',
      playable:!!r.candidate,uri:r.candidate?.asset.uri??null,sha256:r.candidate?.asset.sha256??null,
      subjectSourceKey:r.candidate?.asset.sourceBinding?.subjectSourceKey??null,
      representation:r.candidate?.asset.representationType??null,
      poseControl:r.candidate?.asset.poseControl??null,
      moving:r.candidate?.definition.movingStructureIds??[],fixed:r.candidate?.definition.fixedStructureIds??[]}))});
}
const uniques=(values:any[])=>new Set(values).size;
const summarize=(kind:string)=>{
  const subjects=rows.filter(r=>r.kind===kind),bound=subjects.flatMap(s=>s.options.filter((o:any)=>o.playable).map((o:any)=>({...o,sourceKey:s.sourceKey,side:s.side})));
  const actions=bound.filter(o=>o.learningIntent==='muscle_action');
  return {localEligibleSourceSurfaces:subjects.length,nativeSearchGroups:uniques(subjects.map(s=>s.searchGroupKey)),
    originTextSurfaces:subjects.filter(s=>s.text.origin).length,insertionTextSurfaces:subjects.filter(s=>s.text.insertion).length,
    actionOrPostureTextSurfaces:subjects.filter(s=>s.text.actionOptionsWithExplanation).length,
    reachablePlayableSurfaces:uniques(bound.map(b=>b.sourceKey)),reachableSourceOptionBindings:bound.length,
    actualMuscleActionSurfaces:uniques(actions.map(b=>b.sourceKey)),actualMuscleActionBindings:actions.length,
    postureOrBoneObservationBindings:bound.length-actions.length,uniqueRegisteredGlbs:uniques(bound.map(b=>b.sha256)),
    oneDirectionPoseControlBindings:bound.filter(b=>b.poseControl).length,
    independentNormalJointDofCount:null,normalDofCountNote:'Teaching single-direction controls are not independent normal anatomical DOFs.',
    withoutPlayableSurfaces:subjects.filter(s=>!s.options.some((o:any)=>o.playable)).map(s=>({sourceKey:s.sourceKey,side:s.side,searchGroupKey:s.searchGroupKey})),
    sourceRoles:kind==='bone'?{moving:uniques(bound.filter(b=>b.moving.includes(b.sourceKey)).map(b=>b.sourceKey)),fixed:uniques(bound.filter(b=>b.fixed.includes(b.sourceKey)).map(b=>b.sourceKey)),
      note:'Moving/fixed roles can coexist in different demonstrations; they are not disjoint anatomical classifications.'}:undefined};
};
const output={schemaVersion:'t40-local-delivery-feature-coverage-v1',snapshotId:manifest.snapshotId,manifestSha256:pointer.manifestSha256,
  deliveryBasis:manifest.deliveryBasis,denominators:{targets:542,memberships:563,regions:12,muscleTargets:429,muscleMemberships:447,
    baseMuscleSourceConcepts:232,baseMuscleSourceSurfaces:462,boneTargets:113,haLinks:130,historicalClasses:[6,20,135,2]},
  muscle:summarize('muscle'),bone:summarize('bone'),
  priorityAcceptance:{groups:priority.groups,sourceSurfaces:20,actualActionBindings:22,uniqueGlbs:13,
    note:'Scoped product acceptance, distinct from all reachable candidate/posture bindings.'},
  nerve:{localEligibleSourceSurfaces:rows.filter(r=>r.kind==='nerve').length,nativeLabelGroups:sourceCourse.nativeLabelGroups,
    independentAnatomicalConceptCount:sourceCourse.independentAnatomicalConceptCount,
    observedModelContextRows:sourceCourse.rows.length-courseNames.size,
    documentedOrReusedCourseRows:courseNames.size,documentedCourseNames:[...courseNames],
    olderImplementationLedgerCourseRows:8,currentHashVerifiedAdditionalCourseRows:additionalCourseNames.length,
    entrapmentTextSupportedRows:sourceCourse.rows.filter((r:any)=>r.entrapmentTextSupported).length,
    entrapmentTextUnsupportedRows:sourceCourse.rows.filter((r:any)=>!r.entrapmentTextSupported).length,
    staticGeometrySourceSurfaces:sourceCourse.rows.reduce((n:number,r:any)=>n+r.staticGeometry,0),dynamicPoseSurfaces:0,entrapmentCoordinateBindings:0,
    geometryMotorRelations:graph.motorRelations.filter((r:any)=>r.basis==='exact_geometry_motor_relation').length,
    motorRelationRows:graph.motorRelations.length,relationRows:graph.motorRelations,
    note:'Native label groups and relationship rows are not independent nerve concepts; generic missing-evidence messages are not supported course/entrapment text.'},
  sourceRows:rows.map(r=>({...r,options:r.options.map((o:any)=>({...o,
    subjectRole:{moving:o.moving.includes(r.sourceKey),fixed:o.fixed.includes(r.sourceKey)},
    movingStructureCount:o.moving.length,fixedStructureCount:o.fixed.length,moving:undefined,fixed:undefined,
    poseControl:o.poseControl?{label:o.poseControl.label,startDegrees:o.poseControl.startDegrees,
      endDegrees:o.poseControl.endDegrees,combination:o.poseControl.combination}:null}))})),
  contentCompleteness:'partial',authority:manifest.authority,
  reproductionDependencies:manifest.sourceDependencies.filter((r:any)=>r.workingTreeOnly),
  provenanceNote:'Actual WIP-derived data and frozen bytes are retained in the ignored package, not staged into T40.'};
await writeFile(resolve(root,'work/evidence/T40/local-delivery-2026-10-06/feature-coverage.json'),JSON.stringify(output,null,2)+'\n');
console.log(JSON.stringify({muscle:{...output.muscle,withoutPlayableSurfaces:output.muscle.withoutPlayableSurfaces.length},bone:{...output.bone,withoutPlayableSurfaces:output.bone.withoutPlayableSurfaces.length},nerve:{...output.nerve,relationRows:undefined}},null,2));
