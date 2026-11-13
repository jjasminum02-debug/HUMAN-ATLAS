/** Development-only ST width specimen on an existing canonical thigh; zero verified ST points. */
import type {Carrier,PointInstance,TerritoryMask} from './schema.ts';
import {resolveAnchor} from './anchorAdapter.ts';
import {jsonHash, type EditBindings} from './territoryEditor.ts';
import {maskContentHash} from './territoryMask.ts';
import type {ObservationContext} from './observationContext.ts';
export const EDITOR_CARRIER='leg-right-1';
export async function widthFixture(c:Carrier) {
  if(c.id!==EDITOR_CARRIER||c.side!=='right')throw Error('Wrong specimen carrier');
  const centers=Array.from({length:c.indices.length/3},(_,f)=>[0,1,2].map(k=>c.indices.slice(f*3,f*3+3).reduce((n,v)=>n+c.positions[v*3+k],0)/3));
  const faces=centers.flatMap((p,f)=>p[1]>.49&&p[1]<.79&&p[0]>-.145&&p[0]<-.055&&p[2]>.015?[f]:[]);if(faces.length<50)throw Error('Insufficient technical face strip');
  const used=[...new Set(faces.flatMap(f=>c.indices.slice(f*3,f*3+3)))].sort((a,b)=>a-b);
  const mask:TerritoryMask={schemaVersion:1,scope:'technical_fixture',id:'ST-width-technical-specimen',channel:'ST',side:'right',revision:'technical-width-r1',kind:'teaching_region',carrierId:c.id,carrierRevision:c.revision,carrierHash:c.topologySha256,datasetRevision:c.datasetRevision,frameId:c.frameId,unit:'m',poseId:c.poseId,boundaryRevision:'technical-width-r1',triangleIds:faces,vertexWeights:used.map(v=>[v,1]),sources:[{id:'technical-ST-width-fixture',title:'위경 폭 편집 기술 표본; 실제 위경 경계 근거 아님',edition:null,locator:null}],interpretation:'ai_proposal',professorReview:'not_performed',basisKind:'surface_learning_connection',author:'ai',precision:'educational_approximation_not_skin',canonicalBoundaryClaim:false,rights:{localObservation:'supported',publicRedistribution:'held',sourceIds:['canonical-native-envelope','technical-ST-width-fixture']},boundaryInputSha256:await jsonHash({scope:'technical_fixture',carrierHash:c.topologySha256,rule:'front thigh width specimen, not anatomical ST'}),faceSetSha256:[...new Uint8Array(await crypto.subtle.digest('SHA-256',new Uint32Array(faces)))].map(v=>v.toString(16).padStart(2,'0')).join(''),contentSha256:''};mask.contentSha256=await maskContentHash(mask);
  const nearest=(y:number)=>faces.reduce((a,b)=>Math.abs(centers[a][1]-y)<Math.abs(centers[b][1]-y)?a:b);
  const points:PointInstance[]=[.52,.75].map((y,i)=>({code:`PROBE-${i+1}`,side:'right',revision:'technical-probes-r1',carrierId:c.id,carrierRevision:c.revision,carrierHash:c.topologySha256,frameId:c.frameId,unit:'m',poseId:c.poseId,triangle:nearest(y),barycentric:[1/3,1/3,1/3],landmarkSourceKeys:[],locationValidation:'unresolved',aiProposal:true,professorReview:'not_performed',missing:['technical_fixture_not_an_acupoint']}));
  // A nonempty immutable connected surface line makes coordinate preservation observable.
  const path=faces.filter(f=>Math.abs(centers[f][0]+.1)<.008).sort((a,b)=>centers[a][1]-centers[b][1]);const route:number[]=[];for(let i=1;i<path.length;i++){if(Math.hypot(...centers[path[i]].map((v,k)=>v-centers[path[i-1]][k]))<.025)route.push(...centers[path[i-1]],...centers[path[i]]);}
  const bindings:EditBindings={carrierHash:c.topologySha256,pointHash:await jsonHash(points),routeHash:await jsonHash(route)};
  const bounds:[number[],number[]]=[[Math.min(...used.map(v=>c.positions[v*3]))-.025,.46,Math.min(...used.map(v=>c.positions[v*3+2]))-.02],[Math.max(...used.map(v=>c.positions[v*3]))+.025,.82,Math.max(...used.map(v=>c.positions[v*3+2]))+.02]];
  const contexts:ObservationContext[]=[{code:'PROBE-1',side:'right',mode:'structures_only',region:'technical_thigh_carrier',structures:[{sourceKey:c.id,name:'넙다리 국소 carrier 기술 표본',bounds:bounds as ObservationContext['structures'][number]['bounds'],samplePositions:points.map(p=>resolveAnchor(c,p).position.toArray()),sourceSha256:c.topologySha256,role:'native_probe'}],preferredNormal:[0,0,1],minimumSpan:.34,limitations:['carrier region only; not anatomical ST context or verified acupoints']}];
  return {mask,points,route,bindings,contexts};
}
