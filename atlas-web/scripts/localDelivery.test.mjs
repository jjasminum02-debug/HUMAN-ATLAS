import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, mkdir, writeFile, readFile, rm, symlink } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { createHash } from 'node:crypto';
import { request } from 'node:http';
import { openLocalDelivery } from './localDeliveryServer.mjs';

const sha=b=>createHash('sha256').update(b).digest('hex');
const authority={sourceOnly:true,publicRedistribution:'held',humanReview:'not_performed',canonicalTargetMembershipApproved:false};
async function fixture(){
  const dir=await mkdtemp(join(tmpdir(),'atlas-delivery-'));
  const files=[],privateInputs=[];
  async function add(path,body,extra={}){
    body=Buffer.from(body);await mkdir(dirname(join(dir,path)),{recursive:true});await writeFile(join(dir,path),body);
    return {path,bytes:body.length,sha256:sha(body),...extra};
  }
  for(const url of ['/index.html','/__atlas/integration.json','/__atlas/datasets/human-atlas-local/manifest.json','/atlas-data/assets/motion/test/motion.glb'])
    files.push(await add('public'+url,url,{url,category:url.endsWith('.glb')?'motion':'projection',contentType:'application/octet-stream'}));
  for(const sourcePath of ['atlas-data/motion/motion-learning.json','atlas-data/motion/t66-wave1-registration.json'])
    privateInputs.push(await add('.internal/'+sourcePath,'{}',{sourcePath}));
  const index={schemaVersion:'local-motion-delivery-index-v1',authority,dependencies:privateInputs.map(e=>({path:e.sourcePath,bytes:e.bytes,sha256:e.sha256})),entries:[{uri:files.at(-1).url.slice(1),sha256:files.at(-1).sha256}]};
  const sourcePath='atlas-data/motion/local-motion-delivery-index.json';
  privateInputs.push(await add('.internal/'+sourcePath,JSON.stringify(index),{sourcePath}));
  const manifest={schemaVersion:'human-atlas-local-delivery-v1',snapshotId:'fixture-not-anatomy-evidence',authority:{...authority},files,privateInputs};
  async function save(){const b=JSON.stringify(manifest);await writeFile(join(dir,'snapshot.json'),b);await writeFile(join(dir,'snapshot.sha256'),sha(b));}
  await save();return {dir,files,privateInputs,manifest,save};
}
async function running(f,t){
  t.after(()=>rm(f.dir,{recursive:true,force:true}));
  const d=await openLocalDelivery(f.dir);await new Promise(ok=>d.server.listen(0,'127.0.0.1',ok));
  t.after(()=>new Promise(ok=>d.server.close(ok)));
  return async(path,headers={},method='GET')=>new Promise((ok,fail)=>{
    const req=request({host:'127.0.0.1',port:d.server.address().port,path,headers,method},res=>{
      const chunks=[];res.on('data',b=>chunks.push(b));res.on('end',()=>ok({status:res.statusCode,headers:res.headers,body:Buffer.concat(chunks).toString()}));
    });req.on('error',fail);req.end();
  });
}
test('frozen package serves verified bytes, HEAD, ETag and restarts independently',async t=>{
  const f=await fixture(),call=await running(f,t);
  const a=await call('/');assert.equal(a.status,200);assert.equal(a.body,'/index.html');
  assert.equal((await call('/',{'if-none-match':a.headers.etag})).status,304);
  assert.equal((await call('/',{},'HEAD')).body,'');assert.equal((await call('/',{},'POST')).status,405);
  const restarted=await openLocalDelivery(f.dir);assert.equal(restarted.verifiedFileCount,4);restarted.server.close();
});
test('private ledgers, developer paths and unknown assets never fall back to app HTML',async t=>{
  const call=await running(await fixture(),t);
  for(const p of ['/.internal/atlas-data/motion/motion-learning.json','/snapshot.json','/src/main.tsx','/missing.glb','/%2e%2e/index.html','/%5csecret','/%'])assert.equal((await call(p)).status,404,p);
});
test('changed public bytes fail before a cached response',async t=>{
  const f=await fixture(),call=await running(f,t),a=await call('/');
  await writeFile(join(f.dir,'public/index.html'),'different');
  assert.equal((await call('/',{'if-none-match':a.headers.etag})).status,503);
  await assert.rejects(openLocalDelivery(f.dir),/missing or changed/);
});
test('private dependency changes invalidate otherwise valid cached assets',async t=>{
  const f=await fixture(),call=await running(f,t),a=await call('/');
  await writeFile(join(f.dir,f.privateInputs[0].path),'{"changed":true}');
  assert.equal((await call('/',{'if-none-match':a.headers.etag})).status,503);
  await assert.rejects(openLocalDelivery(f.dir),/missing or changed/);
});
test('missing registered asset prevents startup, never produces partial-ready delivery',async t=>{
  const f=await fixture();t.after(()=>rm(f.dir,{recursive:true,force:true}));
  await rm(join(f.dir,f.files.at(-1).path));await assert.rejects(openLocalDelivery(f.dir),/ENOENT/);
});
test('manifest tampering and public-rights promotion are rejected',async t=>{
  const f=await fixture();t.after(()=>rm(f.dir,{recursive:true,force:true}));
  await writeFile(join(f.dir,'snapshot.json'),'{}');await assert.rejects(openLocalDelivery(f.dir),/manifest changed/);
  f.manifest.authority.publicRedistribution='approved';await f.save();await assert.rejects(openLocalDelivery(f.dir),/Invalid local delivery contract/);
});
test('stale small index cannot be repaired by rehashing only snapshot metadata',async t=>{
  const f=await fixture();t.after(()=>rm(f.dir,{recursive:true,force:true}));
  const input=f.privateInputs.at(-1),index=JSON.parse(await readFile(join(f.dir,input.path),'utf8'));
  index.dependencies[0].sha256='0'.repeat(64);const b=Buffer.from(JSON.stringify(index));
  await writeFile(join(f.dir,input.path),b);input.bytes=b.length;input.sha256=sha(b);await f.save();
  await assert.rejects(openLocalDelivery(f.dir),/Stale motion delivery inputs/);
});
test('file replacement by an external symlink is rejected',async t=>{
  const f=await fixture();t.after(()=>rm(f.dir,{recursive:true,force:true}));
  await rm(join(f.dir,'public/index.html'));await symlink('/etc/hosts',join(f.dir,'public/index.html'));
  await assert.rejects(openLocalDelivery(f.dir),/escaped its package/);
});
test('packaged launcher integrity is checked on restart',async t=>{
  const f=await fixture();t.after(()=>rm(f.dir,{recursive:true,force:true}));
  const body=Buffer.from('fixture launcher, not anatomy');await writeFile(join(f.dir,'serve.mjs'),body);
  f.manifest.launcherFiles=[{path:'serve.mjs',bytes:body.length,sha256:sha(body)}];await f.save();
  const ready=await openLocalDelivery(f.dir);ready.server.close();
  await writeFile(join(f.dir,'serve.mjs'),'changed launcher');
  await assert.rejects(openLocalDelivery(f.dir),/missing or changed/);
});
