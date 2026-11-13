import type { Carrier, PointInstance } from './schema.ts';
import { resolveAnchor, validateCarrier, verifyCarrierHash, type AnchorContext } from './anchorAdapter.ts';

export function anchorBinding(i: PointInstance): string {
  const a=i.assessment;
  return JSON.stringify([i.code,i.side,i.carrierId,i.carrierRevision,i.carrierHash,i.frameId,i.unit,i.poseId,i.triangle,i.barycentric,i.aiProposal,
    a&&[a.scope,a.inputDomain,a.author,a.inputSha256,a.compilerVersion,a.precision,a.basis,a.landmarks,a.relation,a.checks]]);
}
/** AI author, professor review and public rights are independent of local location eligibility. */
export function localLearnerEligible(c: Carrier, i: PointInstance): boolean {
  try {
  const a=i.assessment;
  if(!a || a.schemaVersion!==2 || a.policyVersion!=='landmark-evidence-v2' || a.scope!=='real_input'||a.inputDomain!=='real_input'
    || a.technical!=='passed' || a.precision!=='educational_approximation'
    || !['landmark','B-cun','F-cun'].includes(a.basis) || a.checkedBinding!==anchorBinding(i)
    || !/^[a-f0-9]{64}$/.test(a.inputSha256) || !a.compilerVersion
    || !a.landmarks.length || a.landmarks.some(l=>!l.anatomy.trim() || !l.sourceKey || !/^[a-f0-9]{64}$/.test(l.evidenceSha256))
    || !a.relation.length || a.relation.some(s=>!s.id || !s.title || !s.locator)
    || !(['side','pose','frame','topology','surface','anatomicalRelation'] as const).every(k=>a.checks[k]===true)
    || a.failures.length || i.missing.length || i.locationValidation!=='landmarks_verified'
    || c.rights.localObservation!=='supported' || a.rights?.localObservation!=='supported' || !a.rights.sourceIds.length
    || (i.aiProposal && a.author!=='ai')) return false;
  validateCarrier(c,{datasetRevision:c.datasetRevision,frameId:c.frameId,unit:c.unit,poseId:c.poseId});resolveAnchor(c,i);return true;
  } catch { return false; }
}

/** Small projection: no source text/history/geometry duplication, no fixture export, no deforming pose. */
export async function projectLearnerInstances(c: Carrier, instances: PointInstance[], context: AnchorContext & {motionActive:boolean}, cancelled:()=>boolean=()=>false) {
  if(context.motionActive)throw Error('Static anchor projection requires restored source pose');
  validateCarrier(c,context);await verifyCarrierHash(c);
  if(cancelled())throw new DOMException('Cancelled','AbortError');
  return {schemaVersion:2 as const,usage:'local_learner_eligible' as const,datasetRevision:c.datasetRevision,carrierId:c.id,carrierRevision:c.revision,carrierHash:c.topologySha256,
    frameId:c.frameId,unit:c.unit,poseId:c.poseId,
    instances:instances.filter(i=>localLearnerEligible(c,i)).map(i=>({code:i.code,side:i.side,triangle:i.triangle,barycentric:i.barycentric,
      originScope:'real_input' as const,precision:i.assessment!.precision,author:i.assessment!.author,inputSha256:i.assessment!.inputSha256,professorReview:i.professorReview,
      publicRedistribution:c.rights.publicRedistribution==='supported'&&i.assessment!.rights.publicRedistribution==='supported'?'supported':'held'}))};
}
export type LearnerProjection=Awaited<ReturnType<typeof projectLearnerInstances>>;
/** Runtime replay shares the existing anchor adapter. No landmark search or evidence graph import per frame. */
export async function resolveLearnerProjection(c:Carrier,p:LearnerProjection,context:AnchorContext&{motionActive:boolean},cancelled:()=>boolean=()=>false) {
  if(context.motionActive)throw Error('Static anchor projection requires restored source pose');
  validateCarrier(c,context);await verifyCarrierHash(c);
  if(cancelled())throw new DOMException('Cancelled','AbortError');
  if(p.schemaVersion!==2||p.usage!=='local_learner_eligible'||p.datasetRevision!==c.datasetRevision
    ||p.carrierId!==c.id||p.carrierRevision!==c.revision||p.carrierHash!==c.topologySha256||p.frameId!==c.frameId||p.unit!==c.unit||p.poseId!==c.poseId)throw Error('Stale runtime projection');
  const seen=new Set<string>();
  return p.instances.map(i=>{
    const key=`${i.code}:${i.side}`;
    if(i.originScope!=='real_input'||i.precision!=='educational_approximation'||!['ai','human','unknown'].includes(i.author)
      ||!/^[a-f0-9]{64}$/.test(i.inputSha256)||seen.has(key))throw Error('Ineligible runtime projection');
    seen.add(key);
    const anchor=resolveAnchor(c,{...i,carrierId:p.carrierId,carrierRevision:p.carrierRevision,carrierHash:p.carrierHash,frameId:p.frameId,unit:p.unit,poseId:p.poseId});
    if(i.side==='midline'&&Math.abs(anchor.position.x)>1e-5)throw Error('Off-midline runtime point');
    return {point:i,...anchor};
  });
}
