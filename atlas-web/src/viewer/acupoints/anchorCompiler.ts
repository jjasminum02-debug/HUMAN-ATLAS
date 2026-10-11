import { resolveAnchor, validateCarrier, validateTopology, verifyCarrierHash, type AnchorContext, type AnchorTopology, type TopologyAnchor } from './anchorAdapter.ts';
import { anchorBinding, localLearnerEligible, projectLearnerInstances } from './placementPolicy.ts';
import { sha256 } from './placementMigration.ts';
import type { Carrier, PlacementAssessment, PointInstance, Side, SourceRef, Vec3 } from './schema.ts';

export const ANCHOR_COMPILER_VERSION='explicit-landmarks-2.0';
type Address={triangle:number;barycentric:Vec3};
export interface LandmarkInput {
  id:string; anatomy:string; acquisition:'anatomical_annotation'|'bounds'|'nearest'|'mirror'|'unresolved';
  side:Side; sourceKey:string; native:TopologyAnchor; surface:Address; evidenceId:string;
  role:'anatomical_landmark'|'finger_cun_reference';
}
export interface RuleEvidence {
  id:string; purpose:'landmark_annotation'|'location_relation'|'surface_registration'|'proportion';
  source:SourceRef; originalText:string; author:'ai'|'human'|'source_summary';
  status:'confirmed'|'unresolved'; method:'anatomical_correspondence'|'bounds'|'nearest'|'mirror'|'none';
  side:Side; frameId:string; poseId:string; carrierHash:string; pointCode:string;
  /** Explicit replay tolerance for the annotated surface/native correspondence, never a nearest search. */
  maxRegistrationGapMetres?:number;
  measurement?:{kind:'B-cun'|'F-cun';value:number};
  rights:{localObservation:'supported'|'held';publicRedistribution:'held'|'supported'};
}
export type PlacementRule =
  | {kind:'landmark';landmark:string}
  | {kind:'B-cun';from:string;to:string;value:number;totalCun:number;path:SurfaceSegment[];evidenceId:string}
  | {kind:'F-cun';from:string;directionTo:string;value:number;calibration:{from:string;to:string;cun:number};path:SurfaceSegment[];evidenceId:string}
  | {kind:'bounds'|'nearest'|'unresolved'};
export interface SurfaceSegment {triangle:number;from:Vec3;to:Vec3}
export interface PlacementUnit {
  id:string; scope:'real_input'|'technical_fixture'; code:string; side:Side; revision:string;
  context:AnchorContext; carrierId:string; originalText:string; originalSources:SourceRef[];
  author:'ai'|'human'; professorReview:PointInstance['professorReview'];
  landmarks:LandmarkInput[]; rule:PlacementRule; relationEvidenceId:string; surfaceEvidenceId:string;
}
export interface CompilerInputs { domain:'real_input'|'technical_fixture';carriers:Record<string,Carrier>; native:Record<string,AnchorTopology & {rights:Carrier['rights']}>; evidence:RuleEvidence[] }
export interface CompiledUnit {
  id:string; fingerprint:string; status:'passed'|'failed'; inputSha256:string;
  originalText:string; originalSources:SourceRef[]; instance:PointInstance|null;
  assessment:PlacementAssessment; errors:string[];
}
export interface CompilerLedger {version:2;compilerVersion:string;units:Record<string,CompiledUnit>}
const encode=(v:unknown)=>new TextEncoder().encode(JSON.stringify(v));
const fail=(message:string):never=>{throw Error(message);};
const address=(c:AnchorTopology,a:Address):TopologyAnchor=>({carrierId:c.id,carrierRevision:c.revision,carrierHash:c.topologySha256,
  side:c.side,frameId:c.frameId,unit:c.unit,poseId:c.poseId,...a});
const vector=(c:AnchorTopology,a:Address)=>resolveAnchor(c,address(c,a)).position;
const blank=(unit:PlacementUnit,inputSha256:string):PlacementAssessment=>({schemaVersion:2,policyVersion:'landmark-evidence-v2',scope:unit.scope,inputDomain:unit.scope,
  technical:'not_checked',precision:'unresolved',basis:'legacy_unresolved',author:unit.author,inputSha256,
  compilerVersion:ANCHOR_COMPILER_VERSION,checkedBinding:null,landmarks:[],relation:[],
  checks:{side:false,pose:false,frame:false,topology:false,surface:false,anatomicalRelation:false},failures:[],
  rights:{localObservation:'held',publicRedistribution:'held',sourceIds:[]}});
async function unitFingerprint(unit:PlacementUnit,inputs:CompilerInputs) {
  const landmarks=Array.isArray(unit.landmarks)?unit.landmarks:[];
  const ids=[unit.relationEvidenceId,unit.surfaceEvidenceId,...landmarks.map(l=>l.evidenceId)];
  if(unit.rule?.kind==='B-cun'||unit.rule?.kind==='F-cun')ids.push(unit.rule.evidenceId);
  return sha256(encode({version:ANCHOR_COMPILER_VERSION,domain:inputs.domain,unit,carrier:inputs.carriers[unit.carrierId],
    native:Object.fromEntries([...new Set(landmarks.map(l=>l.sourceKey))].sort().map(k=>[k,inputs.native[k]])),
    evidence:inputs.evidence.filter(e=>ids.includes(e.id)).sort((a,b)=>a.id.localeCompare(b.id))}));
}

/** Offline compiler. All landmarks are explicitly annotated, source-bound inputs; nothing is detected/mirrored. */
export async function compilePlacementUnit(unit:PlacementUnit,inputs:CompilerInputs):Promise<CompiledUnit> {
  const inputSha256=await sha256(encode(unit));
  // Include actual geometry/evidence bytes, not just claimed hashes. Changed input invalidates a checkpoint.
  const fingerprint=await unitFingerprint(unit,inputs);
  const assessment=blank(unit,inputSha256);assessment.inputDomain=inputs.domain;let instance:PointInstance|null=null;
  try {
    const c=inputs.carriers[unit.carrierId];if(!c)fail('missing carrier');
    if(inputs.domain!==unit.scope)fail('Fixture/source input domain mismatch; no fixture promotion');
    if(!['real_input','technical_fixture'].includes(unit.scope)||!Array.isArray(unit.landmarks)||!unit.id?.trim()||!unit.code?.trim()
      ||!['ai','human'].includes(unit.author))fail('invalid unit scope/identity/authorship/landmarks');
    validateCarrier(c,unit.context);await verifyCarrierHash(c);
    if(unit.side!==c.side)fail('unit subject side mismatch');
    if(!unit.originalText.trim()||!unit.originalSources.length)fail('missing preserved location source');
    assessment.technical='passed';assessment.checks.side=true;assessment.checks.pose=true;
    assessment.checks.frame=true;assessment.checks.topology=true;
    assessment.rights={localObservation:'supported',publicRedistribution:c.rights.publicRedistribution,sourceIds:[c.rights.source]};
    if(['bounds','nearest','unresolved'].includes(unit.rule.kind))fail(`ineligible rule: ${unit.rule.kind}; explicit anatomical landmarks required`);
    const getEvidence=(id:string,purpose:RuleEvidence['purpose'])=>{
      const matches=inputs.evidence.filter(e=>e.id===id);
      if(matches.length!==1)fail(`missing/duplicate evidence: ${id}`);
      const e=matches[0];
      if(e.purpose!==purpose||e.status!=='confirmed'||e.method!=='anatomical_correspondence'
        ||e.side!==unit.side||e.frameId!==c.frameId||e.poseId!==c.poseId||e.carrierHash!==c.topologySha256||e.pointCode!==unit.code
        ||!e.originalText.trim()||!e.source.id||!e.source.title||!e.source.locator)fail(`unconfirmed or stale anatomical evidence: ${id}`);
      if(e.rights?.localObservation!=='supported')fail(`source local rights held: ${id}`);
      if(e.rights.publicRedistribution!=='supported')assessment.rights.publicRedistribution='held';
      assessment.rights.sourceIds.push(e.source.id);
      return e;
    };
    const relation=getEvidence(unit.relationEvidenceId,'location_relation');
    if(!unit.originalSources.some(s=>s.id===relation.source.id))fail('location relation is not bound to original source');
    const surface=getEvidence(unit.surfaceEvidenceId,'surface_registration');
    const gap=surface.maxRegistrationGapMetres;
    if(gap===undefined||!Number.isFinite(gap)||gap<0||gap>.02)fail('explicit surface correspondence tolerance required (0–0.02 m)');
    const annotated=new Map<string,LandmarkInput>();
    for(const l of unit.landmarks) {
      if(annotated.has(l.id))fail(`duplicate landmark: ${l.id}`);
      if(!l.id||!l.anatomy.trim()||l.acquisition!=='anatomical_annotation'||l.side!==unit.side)fail(`unresolved/bounds/nearest/mirrored landmark: ${l.id}`);
      const native=inputs.native[l.sourceKey];if(!native||native.id!==l.sourceKey)fail(`missing native landmark geometry: ${l.id}`);
      try {validateTopology(native,unit.context);await verifyCarrierHash(native);resolveAnchor(native,l.native);vector(c,l.surface);}
      catch(error) {
        assessment.technical='failed';assessment.checks.topology=false;
        assessment.checks.frame=native.frameId===unit.context.frameId;
        assessment.checks.pose=native.poseId===unit.context.poseId;throw error;
      }
      if(native.rights?.localObservation!=='supported')fail(`native source local rights held: ${l.id}`);
      if(native.rights.publicRedistribution!=='supported')assessment.rights.publicRedistribution='held';
      assessment.rights.sourceIds.push(native.rights.source);
      if(native.side!==unit.side||l.native.side!==unit.side){assessment.technical='failed';assessment.checks.side=false;fail(`native landmark side mismatch: ${l.id}`);}
      const evidence=getEvidence(l.evidenceId,'landmark_annotation');
      if(resolveAnchor(native,l.native).position.distanceTo(vector(c,l.surface))>gap!)fail(`surface/native annotation gap exceeds explicit tolerance: ${l.id}`);
      annotated.set(l.id,l);
      assessment.landmarks.push({id:l.id,anatomy:l.anatomy,sourceKey:l.sourceKey,evidenceSha256:await sha256(encode(evidence))});
    }
    const landmark=(id:string)=>annotated.get(id)??fail(`missing meaningful landmark: ${id}`);
    const r=unit.rule;let result:Address|null=null;
    if(r.kind==='landmark') {result=landmark(r.landmark).surface;assessment.basis='landmark';}
    else if(r.kind==='B-cun'||r.kind==='F-cun') {
      const ev=getEvidence(r.evidenceId,'proportion');
      if(!Number.isFinite(r.value)||r.value<0||r.value>64)fail('invalid proportion numerator');
      const start=landmark(r.from),end=landmark(r.kind==='B-cun'?r.to:r.directionTo);
      if(start.id===end.id||vector(c,start.surface).distanceTo(vector(c,end.surface))<1e-6)fail('degenerate proportional landmarks');
      if(!r.path.length)fail('missing explicit surface path');
      const connected=(a:number,b:number)=>a===b||c.indices.slice(a*3,a*3+3).filter(v=>c.indices.slice(b*3,b*3+3).includes(v)).length>=2;
      let previous=vector(c,start.surface),length=0,previousTriangle=start.surface.triangle;
      const lengths:number[]=[];
      for(const segment of r.path) {
        if(!connected(previousTriangle,segment.triangle))fail('surface path crosses disconnected topology/components');
        const from=vector(c,{triangle:segment.triangle,barycentric:segment.from});
        const to=vector(c,{triangle:segment.triangle,barycentric:segment.to});
        if(from.distanceTo(previous)>1e-6)fail('disconnected surface path; no bridging or nearest projection');
        const n=from.distanceTo(to);if(n<1e-9)fail('zero-length surface segment');
        lengths.push(n);length+=n;previous=to;previousTriangle=segment.triangle;
      }
      if(previous.distanceTo(vector(c,end.surface))>1e-6)fail('surface path endpoint does not match annotated landmark');
      if(!connected(previousTriangle,end.surface.triangle))fail('surface endpoint crosses disconnected topology/components');
      let distance:number;
      if(r.kind==='B-cun') {
        if(!Number.isFinite(r.totalCun)||r.totalCun<=0||r.totalCun>64||r.value>r.totalCun
          ||ev.measurement?.kind!=='B-cun'||ev.measurement.value!==r.totalCun)fail('B-cun denominator lacks matching source evidence');
        distance=length*r.value/r.totalCun;assessment.basis='B-cun';
      } else {
        const cal=r.calibration;
        if(landmark(cal.from).role!=='finger_cun_reference'||landmark(cal.to).role!=='finger_cun_reference')fail('F-cun calibration must use annotated finger references');
        if(!Number.isFinite(cal.cun)||cal.cun<=0||cal.cun>4||ev.measurement?.kind!=='F-cun'||ev.measurement.value!==cal.cun)fail('F-cun lacks native finger calibration evidence');
        const width=vector(c,landmark(cal.from).surface).distanceTo(vector(c,landmark(cal.to).surface));
        if(width<1e-6)fail('degenerate finger calibration');
        distance=width*r.value/cal.cun;
        if(distance>length+1e-9)fail('F-cun exceeds supported surface path; no extrapolation');
        assessment.basis='F-cun';
      }
      let remaining=distance,index=0;
      while(index<lengths.length-1&&remaining>lengths[index]){remaining-=lengths[index];index++;}
      const segment=r.path[index],t=Math.min(1,remaining/lengths[index]);
      result={triangle:segment.triangle,barycentric:segment.from.map((x,k)=>x+(segment.to[k]-x)*t) as Vec3};
    } else fail('unresolved rule');
    if(!result)throw Error('No explicit anchor result');
    instance={code:unit.code,side:unit.side,revision:unit.revision,carrierId:c.id,carrierRevision:c.revision,carrierHash:c.topologySha256,
      frameId:c.frameId,unit:c.unit,poseId:c.poseId,...result,landmarkSourceKeys:assessment.landmarks.map(l=>l.sourceKey),
      locationValidation:'landmarks_verified',aiProposal:unit.author==='ai',professorReview:unit.professorReview,missing:[],assessment};
    const position=resolveAnchor(c,instance).position;
    if(unit.side==='midline'&&Math.abs(position.x)>1e-5)fail('midline anchor is not on the anatomical midline');
    if(unit.side==='right'&&position.x>=0||unit.side==='left'&&position.x<=0)fail('anchor subject side mismatch');
    assessment.checks.surface=true;assessment.checks.anatomicalRelation=true;
    assessment.relation=[relation.source];assessment.precision='educational_approximation';assessment.checkedBinding=anchorBinding(instance);
  } catch(error) {
    const message=error instanceof Error?error.message:'invalid input';assessment.failures=[message];
    if(!assessment.checks.topology)assessment.technical='failed';
    assessment.precision='unresolved';assessment.checkedBinding=null;instance=null;
  }
  return {id:unit.id,fingerprint,status:assessment.failures.length?'failed':'passed',inputSha256,
    originalText:unit.originalText,originalSources:structuredClone(unit.originalSources),instance,assessment,errors:[...assessment.failures]};
}

/** Failed units retry; successful unchanged units replay without compilation. History is returned separately. */
export async function compilePlacementBatch(units:PlacementUnit[],inputs:CompilerInputs,previous?:CompilerLedger) {
  if(new Set(units.map(u=>u.id)).size!==units.length)throw Error('Duplicate compiler unit IDs');
  if(previous&&(previous.version!==2||previous.compilerVersion!==ANCHOR_COMPILER_VERSION))throw Error('Checkpoint compiler version mismatch');
  const ledger:CompilerLedger={version:2,compilerVersion:ANCHOR_COMPILER_VERSION,units:{}};
  const executed:string[]=[],reused:string[]=[],history:CompiledUnit[]=[];
  for(const unit of units) {
    const fingerprint=await unitFingerprint(unit,inputs),old=previous?.units[unit.id];
    if(old?.status==='passed'&&old.fingerprint===fingerprint){ledger.units[unit.id]=structuredClone(old);reused.push(unit.id);continue;}
    if(old)history.push(structuredClone(old));
    ledger.units[unit.id]=await compilePlacementUnit(unit,inputs);executed.push(unit.id);
  }
  return {ledger,executed,reused,history};
}

/** Only real eligible placements leave the offline evidence graph. Fixtures remain in the compiler ledger. */
export async function projectCompiledBatch(ledger:CompilerLedger,inputs:CompilerInputs,context:AnchorContext&{motionActive:boolean}) {
  const instances=Object.values(ledger.units).flatMap(u=>u.instance?[u.instance]:[]);
  const projections=[];
  for(const c of Object.values(inputs.carriers)) {
    const eligible=instances.filter(i=>i.carrierId===c.id&&localLearnerEligible(c,i));
    // Invalid/fixture-only carriers remain in their unit ledger, never in a runtime artifact.
    if(eligible.length)projections.push(await projectLearnerInstances(c,eligible,context));
  }
  return projections;
}
