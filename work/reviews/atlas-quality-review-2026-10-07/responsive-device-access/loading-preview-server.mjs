// QA only: simulated 8-second GLB latency to observe the real pending UI, not a timing claim.
import {readFile} from 'node:fs/promises';
import {resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {openLocalDelivery} from '../../../../atlas-web/scripts/localDeliveryServer.mjs';
const web=fileURLToPath(new URL('../../../../atlas-web/',import.meta.url));
const pointer=JSON.parse(await readFile(resolve(web,'dist-local/CURRENT.json'),'utf8'));
const app=await openLocalDelivery(resolve(web,'dist-local',pointer.snapshotDirectory));
const handler=app.server.listeners('request')[0];app.server.removeListener('request',handler);
app.server.on('request',(req,res)=>{
  if(req.url?.endsWith('.glb'))setTimeout(()=>{if(!res.destroyed)handler(req,res);},8000);
  else handler(req,res);
});
await new Promise(ok=>app.server.listen(5191,'127.0.0.1',ok));
console.log('Loading UI QA only: http://127.0.0.1:5191/');
for(const signal of ['SIGINT','SIGTERM'])process.once(signal,()=>app.server.close());
