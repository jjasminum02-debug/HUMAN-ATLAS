import { resolve } from 'node:path';
import { openVercelPreview } from './vercelPackage.mjs';
const [directory,front,asset]=process.argv.slice(2),ports=[front,asset].map(Number);if(!directory||ports.some(p=>!Number.isInteger(p)||p<1024||p>65535)||ports[0]===ports[1])throw Error('Usage: DIRECTORY FRONTEND_PORT ASSET_PORT');
const previews=[];for(const [i,mode] of [false,true].entries()){
 const p=await openVercelPreview(resolve(directory),mode);await new Promise((ok,fail)=>{p.server.once('error',fail);p.server.listen(ports[i],'127.0.0.1',ok);});previews.push(p);
}
console.log('Loopback split delivery http://127.0.0.1:'+front+' ; assets http://127.0.0.1:'+asset+' (not a Vercel deployment)');
for(const signal of ['SIGINT','SIGTERM'])process.once(signal,()=>previews.forEach(p=>p.server.close()));
