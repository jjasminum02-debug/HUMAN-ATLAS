import test from 'node:test';
import assert from 'node:assert/strict';
import {ResourceQueue} from './resources.ts';
test('a larger motion reserves memory by releasing unused details without removing live context',async()=>{
 const released:string[]=[];
 const q=new ResourceQueue(async id=>({id,bytes:30}),r=>released.push(r.id),()=>{},2,{maxBytes:100,measure:r=>r.bytes});
 q.demand(['old-detail','overview']);
 await new Promise(resolve=>setImmediate(resolve));
 q.demand(['overview','current-detail'],['overview']);
 await new Promise(resolve=>setImmediate(resolve));
 assert.equal(q.bytes,90);
 assert.equal(q.trimUnused(65),true);
 assert.deepEqual(released,['old-detail']);
 assert.deepEqual([...q.loaded.keys()],['overview','current-detail']);
 assert.equal(q.trimUnused(40),false);
 assert.equal(q.bytes,60);
 assert.equal(q.trimUnused(-1),false);
 q.dispose();
});
