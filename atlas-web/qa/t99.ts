import * as THREE from 'three';
import { AnatomySceneController } from '../src/viewer/wholeBody/AnatomySceneController.ts';
import { validateDataset } from '../src/viewer/datasets/schema.ts';
import { DatasetResources } from '../src/viewer/datasets/DatasetResources.ts';
import type { BodyManifest } from '../src/viewer/wholeBody/contract.ts';
if(!import.meta.env.DEV)throw Error('Local QA only');
const started=performance.now();
const dataset=validateDataset(await(await fetch('/__atlas/datasets/za-c7010a9/manifest.json')).json());
const legacy=await(await fetch('/__atlas/body/manifest.json')).json() as BodyManifest;
const c=new AnatomySceneController(document.querySelector('#scene')!,{...legacy,chunks:[]},()=>{},()=>{});
const r=new DatasetResources(dataset,c.root,true,()=>c.requestRender());
const all=dataset.instances.map(i=>i.sourceKey);const output=document.querySelector('#result')!;
const sleep=(ms:number)=>new Promise(resolve=>setTimeout(resolve,ms));
const ready=async()=>{const start=performance.now();while(r.queue.pending.size||[...r.queue.wanted].some(id=>!r.queue.loaded.has(id))){if(r.queue.failed.size||performance.now()-start>30000)throw Error('readiness/failed budget');await sleep(20);}await new Promise(requestAnimationFrame);};
function orient(angle:number){c.controls.target.set(0,.9,0);c.camera.position.set(Math.sin(angle)*3.4,.9,Math.cos(angle)*3.4);c.controls.update();}
for(const [id,angle]of [['front',0],['side',Math.PI/2],['back',Math.PI]]as const)document.querySelector<HTMLButtonElement>('#'+id)!.onclick=()=>orient(angle);
document.querySelector<HTMLButtonElement>('#core')!.onclick=async()=>{r.demand(dataset.instances.filter(i=>i.kind!=='musculoskeletal_accessory').map(i=>i.sourceKey));await ready();output.textContent=JSON.stringify(record());};
const record=()=>({nodes:r.nodes.size,uniqueNodes:new Set([...r.nodes.values()].map(n=>n.name)).size,root:c.root.uuid,canvases:document.querySelectorAll('canvas').length,triangles:c.renderer.info.render.triangles,bytes:r.queue.bytes,chunks:r.queue.loaded.size,pending:r.queue.pending.size,failures:[...r.queue.failed],evictions:r.queue.evictions,viewport:[innerWidth,innerHeight]});
r.demand(all);await ready();orient(0);await sleep(100);output.textContent=JSON.stringify({status:'ready',coldMs:performance.now()-started,...record()});
document.querySelector<HTMLButtonElement>('#cycle')!.onclick=async()=>{
  const rows=[];const root=c.root.uuid;const camera=c.camera.position.toArray();
  try{
    for(let k=0;k<20;k++){
      // Superseded detail request followed by a disjoint demand exercises in-flight cancellation.
      r.demand(all,all.slice(k*40,k*40+40));r.demand(all,all.slice((k+1)*40,(k+1)*40+40));await ready();
      rows.push(record());if(c.root.uuid!==root||r.nodes.size!==960||r.queue.bytes>96*1024*1024)throw Error('lifecycle invariant');
    }
    r.demand(all);await ready();
    output.textContent=JSON.stringify({status:'passed',cycles:rows,cameraPreserved:JSON.stringify(camera)===JSON.stringify(c.camera.position.toArray()),...record()});
  }catch(e){output.textContent=JSON.stringify({status:'failed',error:String(e),rows,...record()});}
};
window.addEventListener('pagehide',()=>{r.dispose();c.dispose();},{once:true});
