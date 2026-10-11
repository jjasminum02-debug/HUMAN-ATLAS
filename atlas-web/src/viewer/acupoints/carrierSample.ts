import type { Carrier } from './schema.ts';
import { validateCarrier, verifyCarrierHash, type AnchorContext } from './anchorAdapter.ts';

export interface CarrierSample {
  schemaVersion: 1; usage: 'development_review_only'; carrier: Carrier;
  referencePositions: number[]; referenceHash: string; label: string; clearanceMetres: number;
  acceptedAcupoints: 0;
}
export type CarrierFamily='trunk'|'arm'|'leg'|'head'|'hand'|'foot'|'nail'|'oral'|'perineum';
export interface CarrierChunk {
  id:string; family:CarrierFamily; label:string; side:Carrier['side']; revision:string;
  topologySha256:string; referenceHash:string; file:string; sha256:string; bytes:number;
  vertices:number; triangles:number; geometryBufferBytes:number; bounds:number[][]; clearanceMetres:number;
}
export interface CarrierManifest {
  schemaVersion:1; usage:'development_review_only'; revision:string; kind:Carrier['kind']; precision:Carrier['precision'];
  datasetRevision:string; frameId:string; unit:'m'; poseId:string; rights:Carrier['rights']; acceptedAcupoints:0;
  chunks:CarrierChunk[]; totalBytes:number; totalTriangles:number; totalGeometryBufferBytes:number;
}
export function validateCarrierManifest(m:CarrierManifest, context:AnchorContext) {
  if(m.schemaVersion!==1||m.usage!=='development_review_only'||m.acceptedAcupoints!==0||m.kind!=='authored_teaching_surface'||m.precision!=='coarse_not_skin'
    ||m.frameId!==context.frameId||m.poseId!==context.poseId||m.datasetRevision!==context.datasetRevision||m.unit!=='m'||context.unit!=='m'
    ||m.rights.localObservation!=='supported'||!m.chunks.length||new Set(m.chunks.map(c=>c.id)).size!==m.chunks.length)throw Error('Invalid carrier manifest');
  for(const c of m.chunks)if(!/^[a-z0-9-]+\.bin$/.test(c.file)||!['right','left','midline'].includes(c.side)||!['trunk','arm','leg','head','hand','foot','nail','oral','perineum'].includes(c.family)
    ||![c.sha256,c.topologySha256,c.referenceHash].every(h=>/^[a-f0-9]{64}$/.test(h))||!Number.isInteger(c.vertices)||c.vertices<3||c.vertices>=65536
    ||!Number.isInteger(c.triangles)||c.triangles<1||c.bytes!==c.vertices*24+c.triangles*6||c.bytes>8*1024*1024
    ||c.geometryBufferBytes!==c.bytes)throw Error('Invalid carrier chunk');
  for(const [key,item] of [['totalBytes','bytes'],['totalTriangles','triangles'],['totalGeometryBufferBytes','geometryBufferBytes']] as const)
    if(m[key]!==m.chunks.reduce((n,c)=>n+c[item],0))throw Error('Carrier manifest total mismatch');
}
export async function decodeCarrierChunk(m:CarrierManifest,c:CarrierChunk,bytes:ArrayBuffer):Promise<CarrierSample> {
  if(bytes.byteLength!==c.bytes)throw Error('Carrier chunk length');
  const hash=[...new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))].map(n=>n.toString(16).padStart(2,'0')).join('');
  if(hash!==c.sha256)throw Error('Carrier chunk hash');
  // Explicit little-endian decode; topology hash remains existing Float32/Uint32 contract.
  const view=new DataView(bytes),count=c.vertices*3;
  const positions=Array.from({length:count},(_,i)=>view.getFloat32(i*4,true));
  const referencePositions=Array.from({length:count},(_,i)=>view.getFloat32(count*4+i*4,true));
  const indices=Array.from({length:c.triangles*3},(_,i)=>view.getUint16(count*8+i*2,true));
  return {schemaVersion:1,usage:'development_review_only',acceptedAcupoints:0,label:c.label,clearanceMetres:c.clearanceMetres,
    referencePositions,referenceHash:c.referenceHash,carrier:{id:c.id,revision:c.revision,topologySha256:c.topologySha256,
      datasetRevision:m.datasetRevision,frameId:m.frameId,unit:m.unit,poseId:m.poseId,side:c.side,kind:m.kind,precision:m.precision,rights:m.rights,positions,indices}};
}
/** The native basis is fascia/muscle, not skin. Both modes retain one fixed sampled topology. */
export async function validateCarrierSample(data: CarrierSample, context: AnchorContext) {
  if (data.schemaVersion !== 1 || data.usage !== 'development_review_only' || data.acceptedAcupoints !== 0
    || data.carrier.kind !== 'authored_teaching_surface' || data.carrier.precision !== 'coarse_not_skin'
    || !Number.isFinite(data.clearanceMetres) || data.clearanceMetres <= 0 || data.clearanceMetres > .01
    || data.referencePositions.length !== data.carrier.positions.length) throw Error('Invalid bounded surface sample');
  validateCarrier(data.carrier, context);
  await verifyCarrierHash(data.carrier);
  const reference = { ...data.carrier, positions: data.referencePositions, topologySha256: data.referenceHash };
  validateCarrier(reference, context);
  await verifyCarrierHash(reference);
  for (let i=0;i<data.referencePositions.length;i+=3) {
    const distance=Math.hypot(...[0,1,2].map(k=>data.carrier.positions[i+k]-data.referencePositions[i+k]));
    if (Math.abs(distance-data.clearanceMetres) > 1e-6) throw Error('Surface sample offset/unit mismatch');
  }
}
