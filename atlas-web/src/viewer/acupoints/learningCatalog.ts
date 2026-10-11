export interface LearningCatalog {channels:{code:string;nameKo:string;midline:boolean}[];concepts:{code:string;nameKo:string;channel:string}[]}
export async function loadLearningCatalog(signal:AbortSignal,cancelled:()=>boolean) {
 const {default:url}=await import('../../../../atlas-data/acupoints/observation/catalog-r1.json?url');if(cancelled())throw new DOMException('Cancelled','AbortError');
 const r=await fetch(url,{signal});if(!r.ok)throw Error('경맥 목록을 열 수 없습니다.');const raw=await r.arrayBuffer();if(cancelled())throw new DOMException('Cancelled','AbortError');const data=JSON.parse(new TextDecoder().decode(raw)) as LearningCatalog;
 if(data.channels.length!==14||data.concepts.length!==361||new Set(data.concepts.map(c=>c.code)).size!==361)throw Error('Invalid learning catalog');return {data,encodedBytes:raw.byteLength};
}
