export interface LearningCatalog {channels:{code:string;nameKo:string;midline:boolean}[];concepts:{code:string;nameKo:string;channel:string}[]}
const counts:Record<string,number>={LU:11,LI:20,ST:45,SP:21,HT:9,SI:19,BL:67,KI:27,PC:9,TE:23,GB:44,LR:14,CV:24,GV:28};
export function validateLearningCatalog(data:LearningCatalog){
 if(!Array.isArray(data.channels)||!Array.isArray(data.concepts)||data.channels.length!==14||data.concepts.length!==361
   ||new Set(data.channels.map(c=>c.code)).size!==14||new Set(data.concepts.map(c=>c.code)).size!==361)throw Error('Invalid learning catalog');
 for(const channel of data.channels){const actual=data.concepts.filter(c=>c.channel===channel.code);
  if(!counts[channel.code]||!channel.nameKo.trim()||channel.midline!==(channel.code==='CV'||channel.code==='GV')
    ||actual.length!==counts[channel.code]||actual.some((c,i)=>c.code!==`${channel.code}${i+1}`||!c.nameKo.trim()))throw Error('Invalid catalog identity/side/order');}
}
export async function loadLearningCatalog(signal:AbortSignal,cancelled:()=>boolean) {
 const {default:url}=await import('../../../../atlas-data/acupoints/observation/catalog-r1.json?url');if(cancelled())throw new DOMException('Cancelled','AbortError');
 const r=await fetch(url,{signal});if(!r.ok)throw Error('경맥 목록을 열 수 없습니다.');const raw=await r.arrayBuffer();if(cancelled())throw new DOMException('Cancelled','AbortError');const data=JSON.parse(new TextDecoder().decode(raw)) as LearningCatalog;
 validateLearningCatalog(data);return {data,encodedBytes:raw.byteLength};
}
