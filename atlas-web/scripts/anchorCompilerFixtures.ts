import { verifyCarrierHash } from '../src/viewer/acupoints/anchorAdapter.ts';
import type { CompilerInputs, LandmarkInput, PlacementUnit, RuleEvidence } from '../src/viewer/acupoints/anchorCompiler.ts';
import type { Carrier, SourceRef } from '../src/viewer/acupoints/schema.ts';
import { sha256 } from '../src/viewer/acupoints/placementMigration.ts';

/** Synthetic engineering input. These coordinates and source references are never anatomy/product data. */
export async function compilerFixture(kind:'landmark'|'B-cun'|'F-cun'|'midline'='B-cun') {
  const source:SourceRef={id:'synthetic-fixture',title:'Technical fixture only; no anatomical authority',edition:null,locator:'synthetic quad'};
  const carrier:Carrier={id:'fixture-surface',revision:'fixture-r1',topologySha256:'',datasetRevision:'fixture-dataset',
    frameId:'fixture-frame',unit:'m',poseId:'fixture-static',side:kind==='midline'?'midline':'right',kind:'authored_teaching_surface',precision:'coarse_not_skin',
    positions:kind==='midline'?[0,1,0,0,1.1,0,.01,1,.01]:[-.2,1,0,-.1,1,0,-.2,1.1,0,-.1,1.1,0],
    indices:kind==='midline'?[0,1,2]:[0,1,2,1,3,2],rights:{source:'synthetic geometry',localObservation:'supported',publicRedistribution:'held',professorReview:'not_performed'}};
  const p=new Float32Array(carrier.positions),idx=new Uint32Array(carrier.indices),bytes=new Uint8Array(p.byteLength+idx.byteLength);
  bytes.set(new Uint8Array(p.buffer));bytes.set(new Uint8Array(idx.buffer),p.byteLength);carrier.topologySha256=await sha256(bytes);await verifyCarrierHash(carrier);
  const context={datasetRevision:carrier.datasetRevision,frameId:carrier.frameId,unit:'m',poseId:carrier.poseId};
  const native={...carrier,id:'fixture-native',rights:{...carrier.rights}};
  const annotation=(id:string,triangle:number,barycentric:LandmarkInput['surface']['barycentric'],role:LandmarkInput['role']='anatomical_landmark'):LandmarkInput=>({id,
    anatomy:`synthetic ${id} landmark (not human anatomy)`,acquisition:'anatomical_annotation',side:carrier.side,sourceKey:native.id,role,
    native:{carrierId:native.id,carrierRevision:native.revision,carrierHash:native.topologySha256,frameId:native.frameId,unit:'m',poseId:native.poseId,side:native.side,triangle,barycentric},
    surface:{triangle,barycentric},evidenceId:`annotation-${id}`});
  const landmarks=kind==='midline'?[annotation('start',0,[1,0,0])]:[
    annotation('start',0,[1,0,0]),annotation('end',1,[0,1,0]),
    annotation('finger-a',0,[1,0,0],'finger_cun_reference'),annotation('finger-b',0,[0,1,0],'finger_cun_reference')];
  const unit:PlacementUnit={id:`fixture-${kind}`,scope:'technical_fixture',code:`FIXTURE-${kind}`,side:carrier.side,revision:'fixture-r1',context,carrierId:carrier.id,
    originalText:'Synthetic source original: engineering only, no actual acupoint location.',originalSources:[source],author:'ai',professorReview:'not_performed',
    landmarks,relationEvidenceId:'relation',surfaceEvidenceId:'surface',rule:{kind:'landmark',landmark:'start'}};
  const path=[{triangle:0,from:[1,0,0] as [number,number,number],to:[0,.5,.5] as [number,number,number]},
    {triangle:1,from:[.5,0,.5] as [number,number,number],to:[0,1,0] as [number,number,number]}];
  if(kind==='B-cun')unit.rule={kind:'B-cun',from:'start',to:'end',value:4,totalCun:12,path,evidenceId:'proportion'};
  if(kind==='F-cun')unit.rule={kind:'F-cun',from:'start',directionTo:'end',value:.1,calibration:{from:'finger-a',to:'finger-b',cun:1},path,evidenceId:'proportion'};
  const e=(id:string,purpose:RuleEvidence['purpose']):RuleEvidence=>({id,purpose,source,originalText:unit.originalText,author:'ai',status:'confirmed',method:'anatomical_correspondence',
    side:unit.side,frameId:carrier.frameId,poseId:carrier.poseId,carrierHash:carrier.topologySha256,pointCode:unit.code,
    rights:{localObservation:'supported',publicRedistribution:'held'}});
  const evidence=[...landmarks.map(l=>e(l.evidenceId,'landmark_annotation')),e('relation','location_relation'),{...e('surface','surface_registration'),maxRegistrationGapMetres:.001},
    {...e('proportion','proportion'),measurement:{kind:kind==='F-cun'?'F-cun' as const:'B-cun' as const,value:kind==='F-cun'?1:12}}];
  const inputs:CompilerInputs={domain:'technical_fixture',carriers:{[carrier.id]:carrier},native:{[native.id]:native},evidence};
  return {unit,inputs,carrier,context};
}
