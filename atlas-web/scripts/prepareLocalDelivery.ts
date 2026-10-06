import { readFile, writeFile, mkdir, readdir, copyFile, rename, realpath } from 'node:fs/promises';
import { resolve, relative, sep, dirname, extname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { wholeBodyPlugin } from '../plugins/wholeBody.ts';
import { streamDigest, openLocalDelivery } from './localDeliveryServer.mjs';

const root=fileURLToPath(new URL('../../',import.meta.url));
const web=resolve(root,'atlas-web'), output=resolve(web,'dist-local');
const sha=(bytes:Buffer)=>createHash('sha256').update(bytes).digest('hex');
const authority={sourceOnly:true,publicRedistribution:'held',humanReview:'not_performed',canonicalTargetMembershipApproved:false};
const head=execFileSync('git',['rev-parse','HEAD'],{cwd:root,encoding:'utf8'}).trim();
const record=JSON.parse(await readFile(resolve(root,'work/EXECUTION.json'),'utf8'));
const records=record.tasks ?? record.records;
const t85=Array.isArray(records) ? records.find((r:any)=>r.id==='T85') : records?.T85;
if(t85?.executionStatus!=='completed'||t85?.acceptance!=='passed')throw Error('T85 is not completed/passed. Resume T85 before local delivery.');
const verdict=t85.progress?.productAcceptance;
if(!verdict||verdict.unresolvedProductBlockers?.length!==0||t85.unresolvedProductBlockers?.length!==0
  ||!Array.isArray(verdict.evidence)||verdict.evidence.length===0)throw Error('T85 supported product acceptance is incomplete.');
for(const path of [t85.report,...verdict.evidence]){
  const file=await realpath(resolve(root,path));if(!file.startsWith(root))throw Error('T85 evidence escaped workspace');
  await readFile(file);
}
for(const script of ['buildLearnerCardRuntime.mjs','buildLearnerMotionRuntime.mjs'])
  execFileSync(process.execPath,['--experimental-strip-types',resolve(web,'scripts',script),'--check'],{cwd:web,stdio:'inherit'});
// Explicit reuse is allowed only when every captured build dependency and emitted bundle is unchanged.
if(process.argv.length===3&&process.argv[2]==='--reuse-validated-build'){
  const pointer=JSON.parse(await readFile(resolve(output,'CURRENT.json'),'utf8'));
  const old=await openLocalDelivery(resolve(output,pointer.snapshotDirectory));
  if(old.manifestSha256!==pointer.manifestSha256)throw Error('Ready pointer is stale.');
  for(const row of old.manifest.sourceDependencies){
    const actual=await streamDigest(resolve(root,row.path));
    if(actual.bytes!==row.bytes||actual.sha256!==row.sha256)throw Error('Build dependency changed: '+row.path);
  }
  for(const row of old.manifest.files.filter((r:any)=>['app','motion'].includes(r.category))){
    const actual=await streamDigest(resolve(web,'dist',row.url.slice(1)));
    if(actual.bytes!==row.bytes||actual.sha256!==row.sha256)throw Error('Build output changed: '+row.url);
  }
  console.log('Reused the verified, unchanged production bundle.');
}else{
  if(process.argv.length>2)throw Error('Unknown preparation option.');
  execFileSync(process.execPath,[resolve(web,'node_modules/vite/bin/vite.js'),'build'],{cwd:web,stdio:'inherit'});
}

let handler:any;
const watcher:any={add:()=>{},on:()=>watcher,off:()=>watcher};
const plugin:any=wholeBodyPlugin(root);
plugin.configureServer({watcher,middlewares:{use:(...args:any[])=>{handler=args.at(-1);}},httpServer:{once:()=>{}}});
async function capture(url:string):Promise<Buffer>{
  return new Promise((ok,fail)=>{
    const res:any={statusCode:200,setHeader:()=>{},end:(value:any)=>res.statusCode===200?ok(Buffer.from(value??'')):fail(Error('Validated projection failed '+url+' '+res.statusCode))};
    Promise.resolve(handler({url,headers:{},destroyed:false},res,()=>fail(Error('Unknown projection '+url)))).catch(fail);
  });
}
const integration=await capture('/__atlas/integration.json');
const datasetBytes=await capture('/__atlas/datasets/human-atlas-local/manifest.json');
const dataset=JSON.parse(datasetBytes.toString());
const indexPath='atlas-data/motion/local-motion-delivery-index.json';
const index=JSON.parse(await readFile(resolve(root,indexPath),'utf8'));
const snapshotId='local-'+new Date().toISOString().replace(/[^0-9]/g,'').slice(0,17)+'-'+sha(integration).slice(0,8);
await mkdir(output,{recursive:true});
const staging=resolve(output,snapshotId+'-incomplete'), destination=resolve(output,snapshotId);
await mkdir(staging); // Never overwrite an earlier package or failed attempt.
const files:any[]=[],privateInputs:any[]=[],sourceDependencies:any[]=[];
function contentType(path:string){return ({'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.css':'text/css; charset=utf-8','.json':'application/json','.glb':'model/gltf-binary','.svg':'image/svg+xml','.png':'image/png','.webp':'image/webp','.ico':'image/x-icon','.wasm':'application/wasm','.woff2':'font/woff2'} as Record<string,string>)[extname(path)]??'application/octet-stream';}
async function put(url:string,body:Buffer,category:string){
  if(!url.startsWith('/')||url.split('/').some(p=>p==='..'||p==='.')||url.includes('\\'))throw Error('Unsafe snapshot URL');
  const path='public'+url;if(files.some(row=>row.url===url))throw Error('Duplicate delivery URL '+url);
  await mkdir(dirname(resolve(staging,path)),{recursive:true});await writeFile(resolve(staging,path),body);
  files.push({url,path,category,bytes:body.length,sha256:sha(body),contentType:contentType(url)});
}
async function walk(directory:string):Promise<string[]>{
  const rows:string[]=[];
  for(const e of await readdir(directory,{withFileTypes:true})){
    if(e.isSymbolicLink())throw Error('Unexpected symbolic link '+directory+'/'+e.name);
    const path=resolve(directory,e.name);if(e.isDirectory())rows.push(...await walk(path));else if(e.isFile())rows.push(path);
  }return rows.sort();
}
for(const path of await walk(resolve(web,'dist'))){
  const rel=relative(resolve(web,'dist'),path).split(sep).join('/'),url='/'+rel;
  const body=await readFile(path);
  const motion=index.entries.find((row:any)=>row.uri===rel);
  if(motion&&sha(body)!==motion.sha256)throw Error('Bundle motion hash differs '+rel);
  await put(url,body,motion?'motion':'app');
}
for(const entry of index.entries){
  const source=await streamDigest(resolve(root,entry.uri));
  const packed=files.find(row=>row.url==='/'+entry.uri);
  if(!packed||packed.sha256!==entry.sha256||source.sha256!==entry.sha256||packed.bytes!==source.bytes)throw Error('Missing current registered asset '+entry.uri);
}
await put('/__atlas/integration.json',integration,'projection');
await put('/__atlas/datasets/human-atlas-local/manifest.json',datasetBytes,'projection');
for(const chunk of dataset.chunks){
  const body=await capture(chunk.url);
  if(sha(body)!==chunk.sha256||body.length!==chunk.bytes)throw Error('Chunk mismatch '+chunk.id);
  await put(chunk.url,body,'anatomy');
}
for(const sourcePath of [indexPath,...index.dependencies.map((row:any)=>row.path)]){
  const path='.internal/'+sourcePath;
  await mkdir(dirname(resolve(staging,path)),{recursive:true});await copyFile(resolve(root,sourcePath),resolve(staging,path));
  privateInputs.push({path,sourcePath,...await streamDigest(resolve(staging,path))});
}
const dependencyPaths=new Set<string>([
  ...index.dependencies.map((row:any)=>row.path),indexPath,
  'atlas-data/overlays/za-local-integration.json','atlas-data/manifests/bodyparts3d-r4-t100-source-supplement.json',
  'atlas-data/manifests/nerve-scene-t66.json','atlas-data/catalog/target-scope-t96.json',
  'atlas-web/package.json','atlas-web/pnpm-lock.yaml',
]);
for(const dir of ['atlas-web/src','atlas-web/plugins','atlas-data/terminology'])
  for(const path of await walk(resolve(root,dir)))dependencyPaths.add(relative(root,path).split(sep).join('/'));
for(const file of ['atlas-data/manifests/nerve-scene-t66.json','atlas-data/manifests/bodyparts3d-r4-t100-source-supplement.json']){
  const obj=JSON.parse(await readFile(resolve(root,file),'utf8'));
  for(const path of Object.keys(obj.inputSha256??{}))dependencyPaths.add(path);
  for(const key of ['registryPath','datasetPath','rightsPath'])if(obj[key])dependencyPaths.add(obj[key]);
}
for(const sourcePath of [...dependencyPaths].sort()){
  const path=await realpath(resolve(root,sourcePath));if(!path.startsWith(root))throw Error('Source dependency escaped workspace');
  const actual=await streamDigest(path);let committedSha256:string|null=null;
  try{committedSha256=sha(execFileSync('git',['show',head+':'+sourcePath],{cwd:root,maxBuffer:150*1024*1024,stdio:['ignore','pipe','ignore']}));}catch{}
  sourceDependencies.push({path:sourcePath,...actual,committedSha256,workingTreeOnly:actual.sha256!==committedSha256,
    ownership:sourcePath==='atlas-web/package.json'?'T40_owned_local_delivery_scripts':actual.sha256===committedSha256?'existing_checkpoint':'preserved_existing_WIP_owner_not_assigned_by_T40'});
}
await copyFile(resolve(web,'scripts/localDeliveryServer.mjs'),resolve(staging,'serve.mjs'));
await writeFile(resolve(staging,'start.command'),'#!/bin/sh\ncd "$(dirname "$0")" || exit 1\nif command -v node >/dev/null 2>&1; then exec node serve.mjs "$@"; fi\nexec '+"'"+process.execPath.replaceAll("'","'\\''")+"'"+' serve.mjs "$@"\n',{mode:0o755});
await writeFile(resolve(staging,'README.txt'),'HUMAN ATLAS — 로컬 전용 고정 패키지\nNode.js 24 이상 필요. start.command를 실행하고 http://127.0.0.1:5180/ 를 엽니다.\n검사: node serve.mjs --verify-only / 포트 변경: node serve.mjs --port 5181\n종료: 터미널 Ctrl+C. 다시 실행하면 원래 패키지를 재검사합니다.\n일부 콘텐츠만 지원합니다. 공개 재배포 권리 held, 사람 검토 not_performed.\npublic/.internal/snapshot 파일을 따로 삭제하거나 수정하지 마세요.\n오류 시 패키지를 확인하거나 원래 보존된 작업 트리에서 local:prepare로 새 패키지를 만드세요.\n이 폴더 전체와 Node.js만으로 실행하며 개발 서버/원본 자료/네트워크는 필요하지 않습니다.\n');
const launcherFiles=[];
for(const path of ['serve.mjs','start.command'])launcherFiles.push({path,...await streamDigest(resolve(staging,path))});
const manifest={schemaVersion:'human-atlas-local-delivery-v1',snapshotId,createdAt:new Date().toISOString(),baseHead:head,
  deliveryBasis:'preserved_working_tree_snapshot_not_commit_only',authority,
  prerequisite:{T85:'completed/passed',report:'work/evidence/T85/motion-context-2026-10-06/REPORT.md'},
  scope:JSON.parse(integration.toString()).scope,files,privateInputs,sourceDependencies,launcherFiles,
  standaloneDependencies:{runtime:'Node.js >=24',repositoryRequired:false,developmentMiddlewareRequired:false,networkRequired:false},
  contentCompleteness:'partial',wholeAnatomyCompleted:false};
const bytes=Buffer.from(JSON.stringify(manifest,null,2)+'\n'),manifestSha256=sha(bytes);
await writeFile(resolve(staging,'snapshot.json'),bytes);await writeFile(resolve(staging,'snapshot.sha256'),manifestSha256+'\n');
await openLocalDelivery(staging); // Ready only after the same verifier used for restart passes.
await rename(staging,destination);
await writeFile(resolve(output,'CURRENT.json.tmp'),JSON.stringify({snapshotDirectory:snapshotId,manifestSha256},null,2)+'\n');
await rename(resolve(output,'CURRENT.json.tmp'),resolve(output,'CURRENT.json'));
console.log(JSON.stringify({status:'ready',snapshotDirectory:destination,manifestSha256,publicFiles:files.length,
  publicBytes:files.reduce((s,r)=>s+r.bytes,0),privateBytes:privateInputs.reduce((s,r)=>s+r.bytes,0),workingTreeDependencies:sourceDependencies.filter(r=>r.workingTreeOnly).length},null,2));
