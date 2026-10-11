import { decodeCarrierChunk, validateCarrierManifest, type CarrierManifest, type CarrierSample, type CarrierFamily } from './carrierSample.ts';
import type { AnchorContext } from './anchorAdapter.ts';

const chunkUrls=import.meta.glob('../../../../atlas-data/acupoints/carriers/education-r1/*.bin',{query:'?url',import:'default'}) as Record<string,()=>Promise<string>>;
/** One abortable path; browser HTTP cache supplies immutable chunks, no persistent geometry cache. */
export async function loadCarrierSet(family:'all'|CarrierFamily,context:AnchorContext,signal:AbortSignal,cancelled:()=>boolean) {
  const {default:url}=await import('../../../../atlas-data/acupoints/carriers/education-r1/manifest.json?url');
  if(cancelled())throw new DOMException('Cancelled','AbortError');
  const response=await fetch(url,{signal});if(!response.ok)throw Error('체표 목록을 읽을 수 없습니다.');
  const encoded=await response.arrayBuffer();const manifest=JSON.parse(new TextDecoder().decode(encoded)) as CarrierManifest;
  validateCarrierManifest(manifest,context);
  const samples:CarrierSample[]=[];let encodedBytes=encoded.byteLength;
  // Sequential bounded chunks avoid an unbounded transient peak and check cancellation between every import/hash.
  for(const chunk of manifest.chunks.filter(c=>family==='all'||c.family===family)) {
    if(cancelled())throw new DOMException('Cancelled','AbortError');
    const resolve=chunkUrls[`../../../../atlas-data/acupoints/carriers/education-r1/${chunk.file}`];if(!resolve)throw Error('Missing registered carrier chunk');
    const asset=await resolve();if(cancelled())throw new DOMException('Cancelled','AbortError');
    const r=await fetch(asset,{signal});if(!r.ok)throw Error('체표 부위를 읽을 수 없습니다.');
    const data=await r.arrayBuffer();if(cancelled())throw new DOMException('Cancelled','AbortError');
    samples.push(await decodeCarrierChunk(manifest,chunk,data));encodedBytes+=data.byteLength;
  }
  if(cancelled())throw new DOMException('Cancelled','AbortError');
  return {samples,encodedBytes};
}
