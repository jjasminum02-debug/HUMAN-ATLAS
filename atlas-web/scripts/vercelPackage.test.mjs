import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp,mkdir,writeFile,readFile,symlink } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { resolve,dirname } from 'node:path';
import { createHash } from 'node:crypto';
import { buildVercelPackage,checkVercelPackage,openVercelPreview } from './vercelPackage.mjs';
const sha=b=>createHash('sha256').update(b).digest('hex');
async function fixture(){const root=await mkdtemp(resolve(tmpdir(),'atlas-vercel-')),source=resolve(root,'snapshot'),output=resolve(root,'split');const files=[];
 for(const [url,text,category] of [['/index.html','<html><head></head><body>app</body></html>','app'],['/model.glb','exact source geometry','anatomy'],['/motion.glb','exact keys and animation','motion'],['/__atlas/integration.json','{}','projection']]){const bytes=Buffer.from(text),path='public'+url;await mkdir(dirname(resolve(source,path)),{recursive:true});await writeFile(resolve(source,path),bytes);files.push({url,path,category,bytes:bytes.length,sha256:sha(bytes),contentType:url.endsWith('.glb')?'model/gltf-binary':'text/html'});}
 return {root,source,output,manifest:{snapshotId:'fixture',baseHead:'fixture',files,deliveryBasis:'preserved_working_tree_snapshot_not_commit_only',authority:{sourceOnly:true,publicRedistribution:'held',humanReview:'not_performed'}}};}
test('split closure preserves GLB bytes and authority, one config before app, no private upload',async()=>{const f=await fixture(),built=await buildVercelPackage(f.source,f.manifest,f.output,'https://store.example');assert.equal(built.files.length,6);assert.equal(built.cliTargetMet,true);assert.equal(built.deployed,false);
 for(const row of built.files.filter(r=>r.remote)){assert.equal(sha(await readFile(resolve(f.output,row.path))),row.sha256);assert.equal(row.encoding,'identity');assert.equal(built.config.urls[row.url],`https://store.example/${row.sha256}.glb`);}
 const html=await readFile(resolve(f.output,'frontend/public/index.html'),'utf8');assert.match(html,/<script src="\/assets\/asset-transport-[a-f0-9]+.js"><\/script><\/head>/);
 const vercel=JSON.parse(await readFile(resolve(f.output,'frontend/vercel.json'),'utf8'));assert.equal(vercel.outputDirectory,'public');assert.equal(vercel.rewrites,undefined);assert.equal(vercel.headers.some(r=>r.headers.some(h=>h.key==='Content-Encoding')),false);
 await writeFile(resolve(f.output,'frontend/public/private.txt'),'unexpected');await assert.rejects(checkVercelPackage(f.output),/Unexpected/);});
test('invalid origin, changed sources, symlinks and promoted authority reject',async()=>{
 let f=await fixture();await assert.rejects(buildVercelPackage(f.source,f.manifest,f.output,'http://external.example'),/HTTPS/);
 f=await fixture();f.manifest.authority.publicRedistribution='approved';await assert.rejects(buildVercelPackage(f.source,f.manifest,f.output,'https://store.example'),/Authority/);
 f=await fixture();await writeFile(resolve(f.source,'public/model.glb'),'changed');await assert.rejects(buildVercelPackage(f.source,f.manifest,f.output,'https://store.example'),/changed/);
 f=await fixture();await writeFile(resolve(f.root,'outside'),'outside');await symlink(resolve(f.root,'outside'),resolve(f.source,'public/escape.glb'));f.manifest.files.push({url:'/escape.glb',path:'public/escape.glb',category:'motion'});await assert.rejects(buildVercelPackage(f.source,f.manifest,f.output,'https://store.example'),/escape/);
});
test('cross-origin identity HTTP, 404 isolation, abort/retry and verify before ETag',async()=>{
 const f=await fixture(),built=await buildVercelPackage(f.source,f.manifest,f.output,'https://store.example');const {server}=await openVercelPreview(f.output,true);await new Promise(ok=>server.listen(0,'127.0.0.1',ok));try{
 const row=built.files.find(r=>r.remote),url='http://127.0.0.1:'+server.address().port+'/'+row.sha256+'.glb';const response=await fetch(url);assert.equal(response.headers.get('access-control-allow-origin'),'*');assert.equal(response.headers.get('content-encoding'),null);assert.equal(sha(Buffer.from(await response.arrayBuffer())),row.sha256);const etag=response.headers.get('etag');assert.equal((await fetch(url,{headers:{'if-none-match':etag}})).status,304);
 const controller=new AbortController();controller.abort();await assert.rejects(fetch(url,{signal:controller.signal}),/abort/i);assert.equal((await fetch(url)).status,200);
 assert.equal((await fetch('http://127.0.0.1:'+server.address().port+'/work/EXECUTION.json')).status,404);
 await writeFile(resolve(f.output,row.path),'tampered');assert.equal((await fetch(url,{headers:{'if-none-match':etag}})).status,503);
 }finally{await new Promise(ok=>server.close(ok));}
});
test('new revision invalidates only the frontend config while exact SHA assets stay immutable',async()=>{
 const f=await fixture(),first=await buildVercelPackage(f.source,f.manifest,f.output,'https://store.example');
 const second=await buildVercelPackage(f.source,{...f.manifest,snapshotId:'fixture-r2'},resolve(f.root,'split-r2'),'https://store.example');
 assert.deepEqual(first.config.urls,second.config.urls);
 const configFile=manifest=>manifest.files.find(r=>r.url.startsWith('/assets/asset-transport-'));
 assert.notEqual(configFile(first).url,configFile(second).url);
 assert.notEqual(first.files.find(r=>r.url==='/index.html').sha256,second.files.find(r=>r.url==='/index.html').sha256);
 const {server}=await openVercelPreview(resolve(f.root,'split-r2'));
 await new Promise(ok=>server.listen(0,'127.0.0.1',ok));
 try{const origin='http://127.0.0.1:'+server.address().port;
  assert.match((await fetch(origin+'/')).headers.get('cache-control'),/max-age=0, must-revalidate/);
  assert.match((await fetch(origin+configFile(second).url)).headers.get('cache-control'),/immutable/);
  assert.equal((await fetch(origin+'/missing.glb')).status,404);
  assert.match((await fetch(origin+'/missing.glb')).headers.get('cache-control'),/no-store/);
 }finally{await new Promise(ok=>server.close(ok));}
});
