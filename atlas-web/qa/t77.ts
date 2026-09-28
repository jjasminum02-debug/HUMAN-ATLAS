import { AnatomySceneController, type BodyProgress } from '../src/viewer/wholeBody/AnatomySceneController';
import { type BodyManifest, type BodyView, visible, pickable } from '../src/viewer/wholeBody/contract';

const button = document.querySelector<HTMLButtonElement>('#run')!;
const output = document.querySelector('#result')!;
const sleep = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));
async function until(predicate: () => boolean) { const start = performance.now(); while (!predicate()) { if (performance.now()-start>20000) throw Error('Timeout'); await sleep(50); } }
button.onclick = async () => {
  button.disabled = true;
  let controller: AnatomySceneController | null = null;
  const evidence: Record<string, unknown> = {};
  const checks: string[] = [];
  function check(condition: unknown, name: string) { if (!condition) throw Error(name); checks.push(name); }
  try {
    const m = await (await fetch('/__atlas/body/manifest.json')).json() as BodyManifest;
    const host = document.querySelector<HTMLDivElement>('#scene')!;
    let progress: BodyProgress | null = null;
    let inject = true;
    const fetchAsset: typeof fetch = async (...args) => {
      if (inject && String(args[0]).includes('leg-muscle')) { inject = false; return new Response('', { status: 503 }); }
      return fetch(...args);
    };
    controller = new AnatomySceneController(host, m, p => { progress = p; }, () => {}, fetchAsset);
    const c = controller;
    const root = c.root.uuid, canvas = c.renderer.domElement;
    let view: BodyView = { region:'leg',bones:true,muscles:true,supplements:false,selectedId:'HA-M-000003',dim:true };
    const started = performance.now(); c.setView(view);
    await until(()=>!!progress?.failed && c.queue.pending.size===0);
    check(c.queue.loaded.size>0, 'partial failure retains loaded bones');
    const camera = c.camera.position.toArray(); const target = c.controls.target.toArray();
    c.retry(); await until(()=>c.queue.pending.size===0 && !!progress && progress.loaded===progress.total && !progress.failed);
    evidence.legReadyMs = performance.now()-started;
    check(JSON.stringify(camera)===JSON.stringify(c.camera.position.toArray()), 'retry preserves camera');
    check(progress?.selectedAvailable, 'bound tibialis selection survives retry');
    const lostStart = performance.now(); c.renderer.forceContextLoss(); await until(()=>!!progress?.contextLost);
    c.renderer.forceContextRestore(); await until(()=>!progress?.contextLost); await sleep(250);
    check(c.root.uuid===root && c.renderer.domElement===canvas, 'context restore same root and canvas');
    check(JSON.stringify(camera)===JSON.stringify(c.camera.position.toArray()) && JSON.stringify(target)===JSON.stringify(c.controls.target.toArray()), 'context restore preserves camera/target');
    check(progress?.selectedAvailable, 'context restore preserves selection');
    evidence.contextRestoreMs = performance.now()-lostStart;
    // Rapid demand changes exercise real aborted requests and late parsing.
    c.setView({...view,region:'head'}); c.setView({...view,region:'upper-limb'}); c.setView(view);
    await until(()=>c.queue.pending.size===0);
    const allStart = performance.now(); view={...view,region:null,supplements:false};c.setView(view);
    await until(()=>c.queue.pending.size===0 && !!progress && progress.loaded===progress.total && !progress.failed);
    c.focus(null); await sleep(200);
    evidence.wholeBodyReadyMs = performance.now()-allStart;
    check(c.root.uuid===root && c.renderer.domElement===canvas && host.querySelectorAll('canvas').length===1, 'all regional demands use one root/renderer');
    const nodes = c.root.children.flatMap(g=>g.children);
    const shown = nodes.filter(n=>n.visible);
    check(shown.length===531, '531 default visible; 12 held hidden');
    const a=m.chunks.flatMap(x=>x.assets);
    check(a.filter(pickable).length===10, 'only original 10 bindings selectable');
    check(a.filter(x=>visible(x,view)&&x.supplement).length===50 && a.filter(x=>x.supplement).every(x=>!pickable(x)), 'supplements remain source-only');
    check(new Set(nodes.map(n=>n.name)).size===nodes.length, 'no duplicated shared geometry nodes');
    const beforeLayerCamera = c.camera.position.toArray();
    c.setView({...view,bones:false});
    check(nodes.filter(n=>n.visible).every(n=>a.find(x=>x.nodeId===n.name)?.layer==='muscle'), 'bone layer-off hides original and newly integrated bones');
    check(JSON.stringify(beforeLayerCamera)===JSON.stringify(c.camera.position.toArray()), 'layer toggle preserves camera');
    c.setView(view);
    for (const id of ['FJ3157','FJ3159','FJ3162','FJ3165','FJ3168','FJ3393']) check(nodes.some(n=>n.name===`HA-MESH-BP3D4-${id}`&&n.visible), `${id} visible without supplement opt-in`);
    check(a.filter(x=>x.pickState==='held').every(x=>!nodes.find(n=>n.name===x.nodeId)?.visible), 'all integrity held nodes remain hidden');
    evidence.metrics={...progress,calls:c.renderer.info.render.calls,triangles:c.renderer.info.render.triangles,geometries:c.renderer.info.memory.geometries,bytes:m.chunks.reduce((s,c)=>s+c.bytes,0),nodes:nodes.length};
    const samples:number[]=[]; let last=performance.now();
    const off=c.addUpdate(()=>{const now=performance.now();samples.push(now-last);last=now;});await sleep(1200);off();
    samples.sort((a,b)=>a-b);evidence.frameIntervalsMs={count:samples.length,median:samples[Math.floor(samples.length/2)],p95:samples[Math.floor(samples.length*.95)]};
    c.dispose();controller=null;check(host.querySelectorAll('canvas').length===0&&c.queue.loaded.size===0,'dispose removes canvas and releases loaded groups');
    output.textContent=JSON.stringify({status:'passed',checks,evidence},null,2);
  } catch(error) { output.textContent=JSON.stringify({status:'failed',checks,evidence,error:String(error)},null,2);controller?.dispose(); }
  button.disabled=false;
};
