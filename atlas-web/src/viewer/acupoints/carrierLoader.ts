import { decodeCarrierChunk, validateCarrierManifest, type CarrierManifest, type CarrierSample, type CarrierFamily } from './carrierSample.ts';
import type { AnchorContext } from './anchorAdapter.ts';
const directories=[
  {name:'education-r1',manifest:()=>import('../../../../atlas-data/acupoints/carriers/runtime-registry-r1/education-r1.json?url'),urls:import.meta.glob('../../../../atlas-data/acupoints/carriers/education-r1/*.bin',{query:'?url',import:'default'})},
  {name:'lung-AT6-r2',manifest:()=>import('../../../../atlas-data/acupoints/carriers/runtime-registry-r1/lung-AT6-r2.json?url'),urls:import.meta.glob('../../../../atlas-data/acupoints/carriers/lung-AT6-r2/*.bin',{query:'?url',import:'default'})},
  {name:'upper-yang-final-AT8-r18',manifest:()=>import('../../../../atlas-data/acupoints/carriers/runtime-registry-r1/upper-yang-final-AT8-r18.json?url'),urls:import.meta.glob('../../../../atlas-data/acupoints/carriers/upper-yang-final-AT8-r18/*.bin',{query:'?url',import:'default'})},
] as const;
/** One abortable registry/decoder path. Allocate only requested immutable chunks, never retain geometry between sessions. */
export async function loadCarrierSet(family:'all'|CarrierFamily|readonly string[],context:AnchorContext,signal:AbortSignal,cancelled:()=>boolean) {
  const samples:CarrierSample[]=[],registered=new Set<string>();let encodedBytes=0;
  const pending=Array.isArray(family)?new Set(family):null;
  for(const directory of directories) {
    // Development family sampling retains the original registry; learner requests explicit accepted carrier IDs.
    if(directory.name!=='education-r1'&&(!pending||!pending.size))break;
    if(cancelled())throw new DOMException('Cancelled','AbortError');
    const {default:url}=await directory.manifest();if(cancelled())throw new DOMException('Cancelled','AbortError');
    const response=await fetch(url,{signal});if(!response.ok)throw Error('체표 목록을 읽을 수 없습니다.');
    const encoded=await response.arrayBuffer();if(cancelled())throw new DOMException('Cancelled','AbortError');
    const manifest=JSON.parse(new TextDecoder().decode(encoded)) as CarrierManifest;validateCarrierManifest(manifest,context);encodedBytes+=encoded.byteLength;
    for(const c of manifest.chunks){if(registered.has(c.id))throw Error('Duplicate registered carrier identity');registered.add(c.id);}
    for(const chunk of manifest.chunks.filter(c=>pending?pending.has(c.id):family==='all'||c.family===family)) {
      if(cancelled())throw new DOMException('Cancelled','AbortError');
      const resolve=(directory.urls as Record<string,()=>Promise<string>>)[`../../../../atlas-data/acupoints/carriers/${directory.name}/${chunk.file}`];if(!resolve)throw Error('Missing registered carrier chunk');
      const asset=await resolve();if(cancelled())throw new DOMException('Cancelled','AbortError');
      const r=await fetch(asset,{signal});if(!r.ok)throw Error('체표 부위를 읽을 수 없습니다.');
      const data=await r.arrayBuffer();if(cancelled())throw new DOMException('Cancelled','AbortError');
      const sample=await decodeCarrierChunk(manifest,chunk,data);if(cancelled())throw new DOMException('Cancelled','AbortError');
      samples.push(sample);encodedBytes+=data.byteLength;pending?.delete(chunk.id);
    }
  }
  if(pending?.size)throw Error('Unregistered carrier reference');
  if(cancelled())throw new DOMException('Cancelled','AbortError');return {samples,encodedBytes};
}
