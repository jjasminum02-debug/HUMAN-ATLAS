import test from 'node:test';
import assert from 'node:assert/strict';
import { visible, pickable, selected, validateManifest, type BodyAsset, type BodyView } from './contract.ts';
import { ResourceQueue } from './resources.ts';
const asset: BodyAsset = { id: 'FJ1', nodeId: 'HA-MESH-BP3D4-FJ1', sourceSha256: 'a'.repeat(64), regions: ['leg'], side: 'right', layer: 'muscle', defaultVisible: true, supplement: false, pickState: 'source_only_unbound', stableIds: [], holdReasons: [], humanReviewed: false, bounds: [[0,0,0],[1,1,1]] };
const view: BodyView = { region: null, bones: true, muscles: true, supplements: false, selectedId: null, dim: true };
test('source-only context never becomes selectable', () => { assert(visible(asset, view)); assert(!pickable(asset)); });
test('supplements require explicit opt-in, stay unbound', () => { const a = {...asset, defaultVisible:false, supplement:true}; assert(!visible(a, view)); assert(visible(a, {...view,supplements:true})); assert(!pickable(a)); });
test('held identity cannot be revealed through layer/opt-in', () => { const a = {...asset, defaultVisible:false, pickState:'held', holdReasons:['identity']}; assert(!visible(a, {...view,supplements:true})); assert(!pickable(a)); });
test('region/layer demand excludes unrelated geometry', () => { assert(!visible(asset, {...view,region:'head'})); assert(!visible(asset,{...view,muscles:false})); });
test('T95 overlapping region union keeps one asset visible and empty filters mean whole body', () => {
 const shared = {...asset,regions:['head','neck']};
 assert(visible(shared,{...view,region:null,regionIds:['head','neck']}));
 assert(visible(shared,{...view,region:null,regionIds:[]}));
 assert(!visible(shared,{...view,region:null,regionIds:['foot']}));
 assert(!visible({...shared,layer:'bone'},{...view,regionIds:['head','neck'],bones:false}));
 assert(!visible({...shared,defaultVisible:false,localDisplay:{beforeDefaultVisible:false,afterDefaultVisible:false,state:'held',sourceSha256:asset.sourceSha256,integrityHolds:['identity'],evidenceIds:[],retainedHoldReasons:['identity'],bindingState:'held',publicRedistribution:'held',humanReviewed:false,basis:'preserved_historical_policy'}},{...view,regionIds:['head','neck'],supplements:true}));
});
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

test('selected transparency preserves eligibility and selection; hide only hides the selected eligible asset', () => {
  const bound = {...asset,pickState:'existing_binding_unreviewed',stableIds:['known']};
  const selectedView = {...view,selectedId:'known'};
  assert(visible(bound,{...selectedView,selectedPresentation:'translucent'}));
  assert(selected(bound,{...selectedView,selectedPresentation:'translucent'}));
  assert(!visible(bound,{...selectedView,selectedPresentation:'hidden'}));
  assert(visible(asset,{...selectedView,selectedPresentation:'hidden'}));
  assert(!visible({...bound,defaultVisible:false,pickState:'held',holdReasons:['identity']},{...selectedView,selectedPresentation:'hidden'}));
  assert(!visible(bound,{...selectedView,muscles:false,selectedPresentation:'translucent'}));
  assert(!visible(bound,{...selectedView,regionIds:['head'],selectedPresentation:'hidden'}));
});

test('v2 local display is independent from learner binding, rights and review holds', () => {
 const reasons=['not_canonical_learner_binding','human_anatomy_review_not_performed','public_redistribution_held'];
 const a:BodyAsset={...asset,supplement:true,holdReasons:reasons,publicRedistribution:'held',localDisplay:{beforeDefaultVisible:false,afterDefaultVisible:true,state:'allowed',sourceSha256:asset.sourceSha256,integrityHolds:[],evidenceIds:['source','validation'],retainedHoldReasons:reasons,bindingState:'source_only_unbound',publicRedistribution:'held',humanReviewed:false,basis:'verified_local_source_context_only'}};
 const m={version:2,localOnly:true,publicRedistribution:'held',frame:'HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR',unit:'m',lodLevels:1,chunks:[{id:'a',url:'/__atlas/body/a.glb',sha256:'a'.repeat(64),bytes:10,assets:[a]}]};
 validateManifest(m); assert(visible(a,view));assert(!pickable(a));assert(!visible(a,{...view,muscles:false}));
 const reject=(modified:BodyAsset)=>assert.throws(()=>validateManifest({...m,chunks:[{...m.chunks[0],assets:[modified]}]}));
 reject({...a,localDisplay:undefined});
 reject({...a,localDisplay:{...a.localDisplay!,evidenceIds:[]}});
 reject({...a,holdReasons:[...reasons,'identity_conflict']});
 reject({...a,stableIds:['invented']});
 reject({...a,publicRedistribution:undefined});
 const hidden={...a,defaultVisible:false,localDisplay:{...a.localDisplay!,afterDefaultVisible:false,state:'held' as const}};
 assert(!visible(hidden,{...view,supplements:true}));
});
