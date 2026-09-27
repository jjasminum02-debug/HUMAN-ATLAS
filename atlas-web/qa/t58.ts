import * as THREE from 'three';
import { AnatomySceneController } from '../src/viewer/wholeBody/AnatomySceneController';
import { type BodyManifest, type BodyView } from '../src/viewer/wholeBody/contract';
import upper from '../../atlas-data/manifests/bodyparts3d-r4-t54/upper-limb.json';
if (!import.meta.env.DEV) throw Error('Local QA only');
const m = await (await fetch('/__atlas/body/manifest.json')).json() as BodyManifest;
const host = document.querySelector<HTMLElement>('#scene')!;
const output = document.querySelector<HTMLElement>('#result')!;
const picker = document.querySelector<HTMLSelectElement>('#view')!;
const run = document.querySelector<HTMLButtonElement>('#run')!;
const c = new AnatomySceneController(host,m,()=>{},()=>{});
const sleep = (ms:number) => new Promise(r=>setTimeout(r,ms));
const base:BodyView = {region:null,bones:true,muscles:true,supplements:false,selectedId:null,dim:true};
let heading=0;
async function ready() { const start=performance.now(); while(c.queue.pending.size || [...c.queue.wanted].some(id=>!c.queue.loaded.has(id))) { if(performance.now()-start>20000)throw Error('Asset readiness timeout');await sleep(25); } await new Promise(requestAnimationFrame); await new Promise(requestAnimationFrame); }
function orient() { const offset=c.camera.position.clone().sub(c.controls.target);const radius=offset.length();c.camera.position.copy(c.controls.target).add(new THREE.Vector3(Math.sin(heading)*radius,0,Math.cos(heading)*radius));c.controls.update(); }
function frame() {
 c.focus(picker.value==='whole'?null:picker.value==='hand'?'upper-limb':picker.value);
 if(picker.value==='hand') {
  // Original T54 hand target set, source names only; not new learner bindings.
  const ids=new Set<string>(upper.handPickTargetIds);
  const box=new THREE.Box3();
  for(const a of c.assets.values()) if(ids.has(a.nodeId) && a.side==='right' && a.defaultVisible) {box.expandByPoint(new THREE.Vector3().fromArray(a.bounds[0]));box.expandByPoint(new THREE.Vector3().fromArray(a.bounds[1]));}
  if(box.isEmpty())throw Error('No source hand bounds');
  const extent=box.getSize(new THREE.Vector3());const center=box.getCenter(new THREE.Vector3());
  const distance=Math.max(extent.y,extent.x/c.camera.aspect)/(2*Math.tan(THREE.MathUtils.degToRad(17.5)))*1.18+extent.z/2;
  c.controls.target.copy(center);c.camera.position.copy(center).add(new THREE.Vector3(0,0,distance));c.controls.update();
 }
 orient();
}
async function show() { c.setView({...base,region:picker.value==='whole'?null:picker.value==='hand'?'upper-limb':picker.value});await ready();frame(); }
picker.onchange=()=>void show();
for(const [id,angle] of [['front',0],['side',Math.PI/2],['back',Math.PI]] as const) document.querySelector<HTMLButtonElement>('#'+id)!.onclick=()=>{heading=angle;frame();};
run.onclick=async()=>{
 run.disabled=true;picker.disabled=true;
 try {
 const records=[];
 for(const view of ['whole','leg','head','hand']) {
  picker.value=view;heading=0;const start=performance.now();await show();const readyMs=performance.now()-start;
  const intervals:number[]=[];const submit:number[]=[];let previous=performance.now();let frames=0;
  const original=c.renderer.render.bind(c.renderer);
  c.renderer.render=(...args)=>{const start=performance.now();original(...args);submit.push(performance.now()-start);};
  const startCamera=c.camera.position.clone();
  const off=c.addUpdate(()=>{ const now=performance.now();if(frames++>5)intervals.push(now-previous);previous=now;
   const offset=c.camera.position.clone().sub(c.controls.target).applyAxisAngle(new THREE.Vector3(0,1,0),.003);c.camera.position.copy(c.controls.target).add(offset);
  });
  try {while(intervals.length<90)await sleep(30);}finally{off();c.renderer.render=original;c.camera.position.copy(startCamera);c.controls.update();}
  const arrays=new Set<ArrayBufferLike>();let materialCount=0;let opaque=true;const geometries=new Set<THREE.BufferGeometry>();
  c.root.traverse(o=>{if(o instanceof THREE.Mesh){geometries.add(o.geometry);materialCount++;const mat=o.material as THREE.Material;opaque&&=!mat.transparent&&mat.opacity===1;}});
  for(const g of geometries){for(const a of Object.values(g.attributes))arrays.add(a.array.buffer);if(g.index)arrays.add(g.index.array.buffer);}
  const pct=(values:number[],p:number)=>{const sorted=values.slice().sort((a,b)=>a-b);return sorted[Math.min(sorted.length-1,Math.floor(sorted.length*p))];};
  records.push({view,visibility:document.visibilityState,viewport:[innerWidth,innerHeight],canvas:[host.clientWidth,host.clientHeight],devicePixelRatio:c.renderer.getPixelRatio(),readyMs,frames:intervals.length,frameMedianMs:pct(intervals,.5),frameP95Ms:pct(intervals,.95),cpuSubmitP95Ms:pct(submit,.95),calls:c.renderer.info.render.calls,triangles:c.renderer.info.render.triangles,loadedChunks:c.queue.loaded.size,geometries:geometries.size,materialCount,geometryArrayBytes:[...arrays].reduce((n,a)=>n+a.byteLength,0),opaque,wantedBytes:m.chunks.filter(x=>c.queue.wanted.has(x.id)).reduce((n,x)=>n+x.bytes,0),cacheBytes:m.chunks.filter(x=>c.queue.loaded.has(x.id)).reduce((n,x)=>n+x.bytes,0),root:c.root.uuid});
 }
 output.textContent=JSON.stringify({status:'measured',environment:'Local desktop browser at responsive viewport sizes; not mobile hardware or cold network',records},null,2);
 }catch(error){output.textContent=JSON.stringify({status:'failed',error:String(error)});}finally{run.disabled=false;picker.disabled=false;}
};
await show();output.textContent='준비 완료';
window.addEventListener('pagehide',()=>c.dispose(),{once:true});
