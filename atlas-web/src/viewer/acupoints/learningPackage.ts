import type { Carrier, PointInstance, Side } from './schema.ts';
import type { AnchorContext } from './anchorAdapter.ts';
import { resolveLearnerProjection, type LearnerProjection } from './placementPolicy.ts';
import { resolveAnchor } from './anchorAdapter.ts';
import { sha256 } from './placementMigration.ts';
import type { ObservationContext } from './observationContext.ts';
import { loadLearningCatalog, type LearningCatalog } from './learningCatalog.ts';
import { assertUniqueInstances, plannedSides, pointKey, selectedSide, validateLearningRegistry, type LearningSide, type LearningRegistry, type PackageRegistration } from './learningRegistry.ts';
export interface LearnerConcept {code:string;nameKo:string;romanization:string;channel:string;location:string;landmarkLabel:string;textbook:'pending'}
export interface LearningPackage extends AnchorContext {
 schemaVersion:2;usage:'local_learner_eligible';channel:string;concepts:LearnerConcept[];projections:LearnerProjection[];
 availability:{code:string;side:Side;display:'unavailable'|'educational_approximation';reason:string}[];
 precisionCounts:{precise:number;educationalApproximation:number;unresolved:number};
}
/** Lossless delivery encoding. Hash the delivered bytes first; bounds, source addresses and coordinates are never quantized. */
export async function decodeLearningDocument(bytes:ArrayBuffer,gzip=false){
 const decoded=gzip?await new Response(new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'))).arrayBuffer():bytes;
 if(decoded.byteLength>8*1024*1024)throw Error('Learning document decoded size exceeds bounded chunk contract');
 return {document:JSON.parse(new TextDecoder().decode(decoded)),decodedBytes:decoded.byteLength};
}
/** Partial package coverage never implies absent coordinates. Catalog identities and real-input placement are checked separately. */
export function validateLearningPackage(p:LearningPackage,context:AnchorContext,catalog:LearningCatalog,registration?:PackageRegistration) {
 const codes=registration?.codes??catalog.concepts.filter(c=>c.channel===p.channel).map(c=>c.code);
 if(p.schemaVersion!==2||p.usage!=='local_learner_eligible'||!catalog.channels.some(c=>c.code===p.channel)||registration&&registration.channel!==p.channel
  ||p.datasetRevision!==context.datasetRevision||p.frameId!==context.frameId||p.poseId!==context.poseId||p.unit!=='m'||context.unit!=='m'
  ||!Array.isArray(p.concepts)||p.concepts.map(c=>c.code).join()!==codes.join()
  ||p.concepts.some(c=>!c.location.trim()||c.channel!==p.channel||catalog.concepts.find(k=>k.code===c.code)?.nameKo!==c.nameKo)
  ||!Array.isArray(p.projections)||!Array.isArray(p.availability))throw Error('Invalid channel learning package');
 const expected=new Set(codes.flatMap(code=>plannedSides(catalog,code).map(side=>pointKey(code,side))));
 const found=new Set<string>();
 for(const projection of p.projections){
  if(projection.schemaVersion!==2||projection.usage!=='local_learner_eligible'||projection.datasetRevision!==p.datasetRevision
   ||projection.frameId!==p.frameId||projection.poseId!==p.poseId||projection.unit!=='m'||!projection.instances.length)throw Error('Invalid point projection');
  for(const i of projection.instances){const id=pointKey(i.code,i.side);
   if(!expected.has(id)||i.originScope!=='real_input'||i.precision!=='educational_approximation'||found.has(id))throw Error('Invalid/duplicate learner point');found.add(id);}
 }
 const seen=new Set<string>();
 for(const a of p.availability){const id=pointKey(a.code,a.side);
  if(!expected.has(id)||seen.has(id)||a.display!==(found.has(id)?'educational_approximation':'unavailable')||(!found.has(id)&&!a.reason.trim()))throw Error('Availability does not match accepted positions');seen.add(id);}
 if(seen.size!==expected.size||p.precisionCounts.precise!==0||p.precisionCounts.educationalApproximation!==found.size||p.precisionCounts.unresolved!==expected.size-found.size)throw Error('Location count mismatch');
}
export function composeLearningPackages(packages:LearningPackage[]){
 assertUniqueInstances(packages.flatMap(p=>p.availability));
 const concepts=packages.flatMap(p=>p.concepts);if(new Set(concepts.map(c=>c.code)).size!==concepts.length)throw Error('Duplicate/conflicting concepts');
 return {concepts,projections:packages.flatMap(p=>p.projections),availability:packages.flatMap(p=>p.availability),precisionCounts:packages.reduce((n,p)=>({precise:n.precise+p.precisionCounts.precise,educationalApproximation:n.educationalApproximation+p.precisionCounts.educationalApproximation,unresolved:n.unresolved+p.precisionCounts.unresolved}),{precise:0,educationalApproximation:0,unresolved:0})};
}
export function validateObservationBindings(contexts:ObservationContext[],points:PointInstance[]){
 assertUniqueInstances(contexts);
 for(const c of contexts){const i=points.find(i=>i.code===c.code&&i.side===c.side),b=c.placementBinding;
  if(!i||!b||b.carrierId!==i.carrierId||b.carrierHash!==i.carrierHash||b.triangle!==i.triangle||b.barycentric.join()!==i.barycentric.join())throw Error('Observation placement binding mismatch');
  if(!c.structures.length||c.structures.some(s=>s.bounds.flat().some(v=>!Number.isFinite(v))))throw Error('Missing actual local structure bounds');}
 if(contexts.length!==points.length)throw Error('Missing accepted point observation');
}
export async function loadLearningPackage(side:LearningSide,context:AnchorContext&{motionActive:boolean},signal:AbortSignal,cancelled:()=>boolean,request:{channel?:string;allPoints?:boolean;catalog?:LearningCatalog}={}) {
 if(context.motionActive)throw Error('정지 자세에서 다시 열어 주세요.');
 const check=()=>{if(cancelled()||signal.aborted)throw new DOMException('Cancelled','AbortError');};
 check();if(!['right','left','midline','both'].includes(side))throw Error('Invalid requested subject side');
 let encodedBytes=0,decodedDocumentBytes=0;const catalog=request.catalog??(await loadLearningCatalog(signal,cancelled)).data;
 const read=async(url:string,expectedHash?:string,gzip=false)=>{check();const r=await fetch(url,{signal});if(!r.ok)throw Error('경혈 자료를 열 수 없습니다.');const b=await r.arrayBuffer();check();if(expectedHash&&await sha256(new Uint8Array(b))!==expectedHash)throw Error('Stale registry package hash');check();encodedBytes+=b.byteLength;const decoded=await decodeLearningDocument(b,gzip);check();decodedDocumentBytes+=decoded.decodedBytes;return decoded.document;};
 const {default:registryUrl}=await import('../../../../atlas-data/acupoints/learner/registry-r1.json?url');check();
 const registry=await read(registryUrl) as LearningRegistry;validateLearningRegistry(registry,catalog);
 const registrations=registry.packages.filter(p=>request.allPoints||p.channel===(request.channel??'LU'));
 // Registry additions are resolved as lazy URL modules, never eager point data.
 const packageUrls=import.meta.glob('../../../../atlas-data/acupoints/learner/*.json',{query:'?url',import:'default'});
 const observationUrls=import.meta.glob('../../../../atlas-data/acupoints/observation/*-context-*.{json,bin}',{query:'?url',import:'default'});
 const resolve=async(urls:Record<string,()=>Promise<unknown>>,path:string)=>{check();const fn=urls[path];if(!fn)throw Error('Unregistered package file');const url=await fn();check();return String(url);};
 const packages:LearningPackage[]=[],documents:{contexts:ObservationContext[];teachingPaths:{side:Side;from:number[];to:number[]}[]}[]=[];
 for(const registration of registrations){
  if(!registration.learnerSha256||!registration.observationSha256)throw Error('Missing registered package hashes');
  const p=await read(await resolve(packageUrls,`../../../../atlas-data/acupoints/learner/${registration.learnerFile}`),registration.learnerSha256) as LearningPackage;validateLearningPackage(p,context,catalog,registration);packages.push(p);
  // Unavailable-only packages have no geometry, path, context fetch or camera ownership.
  if(!p.projections.some(p=>p.instances.some(i=>selectedSide(side,i.side))))continue;
  const doc=await read(await resolve(observationUrls,`../../../../atlas-data/acupoints/observation/${registration.observationFile}`),registration.observationSha256,registration.observationEncoding==='gzip');
  if(doc.datasetRevision!==context.datasetRevision||doc.frameId!==context.frameId||doc.poseId!==context.poseId||doc.unit!=='m')throw Error('Observation frame/pose mismatch');documents.push(doc);
 }
 const data=composeLearningPackages(packages),projections=data.projections.filter(p=>p.instances.some(i=>selectedSide(side,i.side)));
 const carriers:Carrier[]=[],points:PointInstance[]=[];
 if(projections.length){const {loadCarrierSet}=await import('./carrierLoader.ts');check();const set=await loadCarrierSet([...new Set(projections.map(p=>p.carrierId))],context,signal,cancelled);encodedBytes+=set.encodedBytes;carriers.push(...set.samples.map(s=>s.carrier));
  for(const p of projections){const c=carriers.find(c=>c.id===p.carrierId);if(!c)throw Error('Missing point carrier');await resolveLearnerProjection(c,p,context,cancelled);check();
   points.push(...p.instances.filter(i=>selectedSide(side,i.side)).map(i=>({...i,revision:'compiler-runtime',carrierId:p.carrierId,carrierRevision:p.carrierRevision,carrierHash:p.carrierHash,frameId:p.frameId,poseId:p.poseId,unit:p.unit,landmarkSourceKeys:[],locationValidation:'landmarks_verified' as const,aiProposal:i.author==='ai',missing:[]})));}
 }
 assertUniqueInstances(points);const contexts=documents.flatMap(d=>d.contexts.filter(c=>selectedSide(side,c.side)));validateObservationBindings(contexts,points);check();
 for(const doc of documents)for(const raw of doc.teachingPaths){
  const s=raw as typeof raw&{fromCode?:string;toCode?:string;carrierId?:string;carrierHash?:string;triangle?:number;fromBarycentric?:number[];toBarycentric?:number[]};
  if(!selectedSide(side,s.side)||!s.carrierId)continue;
  if(!s.fromCode||!s.toCode||!points.some(p=>p.code===s.fromCode&&p.side===s.side)||!points.some(p=>p.code===s.toCode&&p.side===s.side))throw Error('Route references unavailable points');
  const c=carriers.find(c=>c.id===s.carrierId);if(!c||c.topologySha256!==s.carrierHash)throw Error('Route carrier mismatch');
  for(const [bary,position] of [[s.fromBarycentric,s.from],[s.toBarycentric,s.to]] as const){
   if(!bary||s.triangle===undefined)throw Error('Missing route topology address');
   const anchor=resolveAnchor(c,{carrierId:c.id,carrierRevision:c.revision,carrierHash:c.topologySha256,frameId:c.frameId,unit:c.unit,poseId:c.poseId,side:s.side,triangle:s.triangle,barycentric:bary as [number,number,number]});
   if(Math.hypot(...anchor.position.addScaledVector(anchor.normal,.001).toArray().map((v,i)=>v-position[i]))>1e-6)throw Error('Route coordinates do not replay');
  }
 }
 const route=documents.flatMap(d=>d.teachingPaths.filter(p=>selectedSide(side,p.side)).flatMap(p=>[...p.from,...p.to]));if(!route.every(Number.isFinite)||route.length%6)throw Error('Invalid supported teaching segments');
 return {data,carriers,points,contexts,route,encodedBytes,decodedDocumentBytes,sections:registrations.flatMap(p=>p.sections)};
}
