import type { Carrier, PointInstance } from './schema.ts';
import type { AnchorContext } from './anchorAdapter.ts';
import { resolveLearnerProjection, type LearnerProjection } from './placementPolicy.ts';
import { LUNG_ORDER } from './tour.ts';
export interface LearnerConcept {code:string;nameKo:string;romanization:string;channel:'LU';location:string;landmarkLabel:string;textbook:'pending'}
export interface LearningPackage extends AnchorContext {
  schemaVersion:2;usage:'local_learner_eligible';channel:'LU';concepts:LearnerConcept[];projections:LearnerProjection[];
  availability:{code:string;side:'right'|'left';display:'unavailable'|'educational_approximation';reason:string}[];
  precisionCounts:{precise:number;educationalApproximation:number;unresolved:number};
}
/** Code/text availability never creates a coordinate. Only AT5 compiler projections are eligible. */
export function validateLearningPackage(p:LearningPackage,context:AnchorContext) {
  if(p.schemaVersion!==2||p.usage!=='local_learner_eligible'||p.channel!=='LU'||p.datasetRevision!==context.datasetRevision
    ||p.frameId!==context.frameId||p.poseId!==context.poseId||p.unit!=='m'||context.unit!=='m'
    ||!Array.isArray(p.concepts)||p.concepts.length!==11||p.concepts.map(c=>c.code).join()!==LUNG_ORDER.join()
    ||p.concepts.some(c=>!c.nameKo.trim()||!c.location.trim()||c.channel!=='LU')
    ||p.concepts.find(c=>c.code==='LU9')?.nameKo!=='태연'||p.concepts.find(c=>c.code==='LU11')?.nameKo!=='소상'
    ||!Array.isArray(p.projections)||!Array.isArray(p.availability)||p.availability.length!==22)throw Error('Invalid lung learning package');
  const found=new Set<string>();
  for(const projection of p.projections) {
    if(projection.schemaVersion!==2||projection.usage!=='local_learner_eligible'||projection.datasetRevision!==p.datasetRevision
      ||projection.frameId!==p.frameId||projection.poseId!==p.poseId||projection.unit!=='m'||!projection.instances.length)throw Error('Invalid point projection');
    for(const i of projection.instances){const id=`${i.code}:${i.side}`;
      if(!LUNG_ORDER.includes(i.code)||!['right','left'].includes(i.side)||i.originScope!=='real_input'||i.precision!=='educational_approximation'||found.has(id))throw Error('Invalid/duplicate learner point');found.add(id);}
  }
  const seen=new Set<string>();
  for(const a of p.availability){const id=`${a.code}:${a.side}`;
    if(!LUNG_ORDER.includes(a.code)||!['right','left'].includes(a.side)||seen.has(id)
      ||a.display!==(found.has(id)?'educational_approximation':'unavailable')||(!found.has(id)&&!a.reason.trim()))throw Error('Availability does not match accepted positions');seen.add(id);}
  if(p.precisionCounts.precise!==0||p.precisionCounts.educationalApproximation!==found.size||p.precisionCounts.unresolved!==22-found.size)throw Error('Location count mismatch');
}
export async function loadLearningPackage(side:'right'|'left',context:AnchorContext&{motionActive:boolean},signal:AbortSignal,cancelled:()=>boolean) {
  if(context.motionActive)throw Error('정지 자세에서 다시 열어 주세요.');
  const {default:url}=await import('../../../../atlas-data/acupoints/learner/lung-r7.json?url');
  if(cancelled())throw new DOMException('Cancelled','AbortError');
  const response=await fetch(url,{signal});if(!response.ok)throw Error('경혈 자료를 열 수 없습니다.');
  const bytes=await response.arrayBuffer();if(cancelled())throw new DOMException('Cancelled','AbortError');
  const data=JSON.parse(new TextDecoder().decode(bytes)) as LearningPackage;validateLearningPackage(data,context);
  const projections=data.projections.filter(p=>p.instances.some(i=>i.side===side));
  const carriers:Carrier[]=[],points:PointInstance[]=[];let encodedBytes=bytes.byteLength;
  // No carrier request/allocation for unavailable points. Load exactly referenced registered chunks.
  if(projections.length){const {loadCarrierSet}=await import('./carrierLoader.ts');const set=await loadCarrierSet([...new Set(projections.map(p=>p.carrierId))],context,signal,cancelled);encodedBytes+=set.encodedBytes;
    for(const p of projections){const c=set.samples.find(s=>s.carrier.id===p.carrierId)?.carrier;if(!c)throw Error('Missing point carrier');
      await resolveLearnerProjection(c,p,context,cancelled);carriers.push(c);
      points.push(...p.instances.filter(i=>i.side===side).map(i=>({...i,revision:'compiler-runtime',carrierId:p.carrierId,carrierRevision:p.carrierRevision,carrierHash:p.carrierHash,
        frameId:p.frameId,poseId:p.poseId,unit:p.unit,landmarkSourceKeys:[],locationValidation:'landmarks_verified' as const,aiProposal:i.author==='ai',missing:[]})));}
  }
  if(cancelled())throw new DOMException('Cancelled','AbortError');return {data,carriers,points,encodedBytes};
}
