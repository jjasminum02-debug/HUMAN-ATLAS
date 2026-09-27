import test from 'node:test';
import assert from 'node:assert/strict';
import { visible, pickable, validateManifest, type BodyAsset, type BodyView } from './contract.ts';
import { ResourceQueue } from './resources.ts';
const asset: BodyAsset = { id: 'FJ1', nodeId: 'HA-MESH-BP3D4-FJ1', sourceSha256: 'a'.repeat(64), regions: ['leg'], side: 'right', layer: 'muscle', defaultVisible: true, supplement: false, pickState: 'source_only_unbound', stableIds: [], holdReasons: [], humanReviewed: false, bounds: [[0,0,0],[1,1,1]] };
const view: BodyView = { region: null, bones: true, muscles: true, supplements: false, selectedId: null, dim: true };
test('source-only context never becomes selectable', () => { assert(visible(asset, view)); assert(!pickable(asset)); });
test('supplements require explicit opt-in, stay unbound', () => { const a = {...asset, defaultVisible:false, supplement:true}; assert(!visible(a, view)); assert(visible(a, {...view,supplements:true})); assert(!pickable(a)); });
test('held identity cannot be revealed through layer/opt-in', () => { const a = {...asset, defaultVisible:false, pickState:'held', holdReasons:['identity']}; assert(!visible(a, {...view,supplements:true})); assert(!pickable(a)); });
test('region/layer demand excludes unrelated geometry', () => { assert(!visible(asset, {...view,region:'head'})); assert(!visible(asset,{...view,muscles:false})); });
test('reject conflicting duplicate IDs and source-only binding promotion', () => {
 const m = { version:1,localOnly:true,publicRedistribution:'held',frame:'HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR',unit:'m',lodLevels:1,chunks:[{id:'a',url:'/__atlas/body/a.glb',sha256:'a'.repeat(64),bytes:10,assets:[asset]}] };
 validateManifest(m); assert.throws(()=>validateManifest({...m,unit:'mm'})); assert.throws(()=>validateManifest({...m,chunks:[m.chunks[0],m.chunks[0]]}));
 assert.throws(()=>validateManifest({...m,chunks:[{...m.chunks[0],assets:[{...asset,stableIds:['invented']}]}]}));
});
const tick = () => new Promise(resolve => setTimeout(resolve, 0));
test('late parse after cancellation is disposed; same-id new demand can recover', async () => {
 const completions: ((value:string)=>void)[]=[]; const released:string[]=[];
 const q = new ResourceQueue<string>(()=>new Promise(resolve=>completions.push(resolve)),v=>released.push(v),()=>{},1);
 q.demand(['a']); q.demand([]); q.demand(['a']); completions[0]('stale'); await tick();
 assert.deepEqual(released,['stale']); assert.equal(completions.length,2); completions[1]('fresh'); await tick(); assert.equal(q.loaded.get('a'),'fresh'); q.dispose(); assert.deepEqual(released,['stale','fresh']);
});
test('failure retains successful resources; explicit retry only failed asset', async()=>{
 let attempts=0;const q=new ResourceQueue<string>(async id=>{if(id==='b' && ++attempts===1)throw Error();return id},()=>{},()=>{});
 q.demand(['a','b']);await tick();assert.equal(q.loaded.get('a'),'a');assert(q.failed.has('b'));q.retry();await tick();assert.equal(q.loaded.size,2);assert.equal(attempts,2);q.dispose();
});
test('dispose releases completed and late resources exactly once',async()=>{
 let finish:(v:string)=>void=()=>{};const released:string[]=[];
 const q=new ResourceQueue<string>(()=>new Promise(r=>finish=r),v=>released.push(v),()=>{});q.demand(['a']);q.dispose();finish('late');await tick();assert.deepEqual(released,['late']);assert.equal(q.loaded.size,0);
});
test('isolation never promotes source-only or held nodes and respects layer switches', () => {
  const bound = {...asset,pickState:'existing_binding_unreviewed',stableIds:['known']};
  const isolated = {...view,selectedId:'known',isolate:true};
  assert(visible(bound,isolated)); assert(!visible(asset,isolated));
  assert(!visible({...bound,pickState:'held',defaultVisible:false,holdReasons:['identity']},isolated));
  assert(!visible(bound,{...isolated,muscles:false}));
  assert(!visible(bound,{...isolated,selectedIds:[]}));
  assert(visible(asset,{...isolated,selectedId:null}));
});
