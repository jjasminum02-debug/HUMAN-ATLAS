import { readFile, writeFile, mkdir, realpath, readdir } from 'node:fs/promises';
import { resolve, dirname, sep } from 'node:path';
import { createHash } from 'node:crypto';
import { createServer } from 'node:http';
const sha=b=>createHash('sha256').update(b).digest('hex');
const authorityOK=a=>a?.sourceOnly===true&&a.publicRedistribution==='held'&&a.humanReview==='not_performed';
const safe=p=>typeof p==='string'&&!p.startsWith('/')&&!p.includes('\\')&&!p.split('/').some(s=>!s||s==='..'||s==='.');
async function bytesAt(root,path){if(!safe(path))throw Error('Invalid package path');const file=await realpath(resolve(root,path));if(!file.startsWith(root+sep))throw Error('Package escape');return readFile(file);}
async function put(root,path,bytes){if(!safe(path))throw Error('Invalid package path');await mkdir(dirname(resolve(root,path)),{recursive:true});await writeFile(resolve(root,path),bytes,{flag:'wx'});}
function validateOrigin(value){const u=new URL(value);if(u.username||u.password||u.search||u.hash||u.pathname!=='/'||!(u.protocol==='https:'||u.protocol==='http:'&&['127.0.0.1','localhost','[::1]'].includes(u.hostname)))throw Error('Use an HTTPS asset origin, or loopback for local preview');return u.origin;}
export async function buildVercelPackage(snapshotRoot,manifest,outputRoot,assetOrigin){
 if(!authorityOK(manifest.authority))throw Error('Authority cannot be promoted');
 const origin=validateOrigin(assetOrigin),root=await realpath(snapshotRoot),files=[],urls={},seen=new Set();
 await mkdir(outputRoot,{recursive:false});
 for(const row of manifest.files){
  if(!['app','projection','motion','anatomy'].includes(row.category)||row.path!=='public'+row.url||!row.url.startsWith('/')||seen.has(row.url))throw Error('Invalid public allowlist');seen.add(row.url);
  const bytes=await bytesAt(root,row.path);if(bytes.length!==row.bytes||sha(bytes)!==row.sha256)throw Error('Snapshot changed');
  const remote=['motion','anatomy'].includes(row.category);
  if(remote&&!row.url.endsWith('.glb'))throw Error('Unsupported remote format');
  const path=remote?`assets-store/${row.sha256}.glb`:`frontend/${row.path}`;
  if(remote){urls[row.url]=`${origin}/${row.sha256}.glb`;if(!files.some(f=>f.path===path))await put(outputRoot,path,bytes);}else await put(outputRoot,path,bytes);
  files.push({...row,path,remote,encoding:'identity',transportSha256:row.sha256,transportBytes:row.bytes});
 }
 const config={revision:manifest.snapshotId,urls,...(origin.startsWith('http:')?{inspection:true}:{})};
 const script=Buffer.from('window.__ATLAS_ASSET_TRANSPORT__='+JSON.stringify(config)+';\n'),scriptUrl=`/assets/asset-transport-${sha(script)}.js`;
 await put(outputRoot,'frontend/public'+scriptUrl,script);
 files.push({url:scriptUrl,path:'frontend/public'+scriptUrl,category:'app',remote:false,encoding:'identity',bytes:script.length,transportBytes:script.length,sha256:sha(script),transportSha256:sha(script),contentType:'text/javascript; charset=utf-8'});
 const html=files.find(f=>f.url==='/index.html');if(!html)throw Error('No entrypoint');
 const original=await readFile(resolve(outputRoot,html.path),'utf8');if(!original.includes('</head>'))throw Error('Invalid entrypoint');
 const injected=Buffer.from(original.replace('</head>',`<script src="${scriptUrl}"></script></head>`));
 await writeFile(resolve(outputRoot,html.path),injected);html.sourceSha256=html.sha256;html.sha256=html.transportSha256=sha(injected);html.bytes=html.transportBytes=injected.length;
 const notFound=Buffer.from('<!doctype html><html lang="ko"><meta charset="utf-8"><title>페이지 없음</title><p>이 주소에는 자료가 없습니다.</p><a href="/">HUMAN ATLAS로 돌아가기</a></html>');
 await put(outputRoot,'frontend/public/404.html',notFound);
 files.push({url:'/404.html',path:'frontend/public/404.html',category:'app',remote:false,encoding:'identity',bytes:notFound.length,transportBytes:notFound.length,sha256:sha(notFound),transportSha256:sha(notFound),contentType:'text/html; charset=utf-8'});
 const common=[{key:'X-Content-Type-Options',value:'nosniff'},{key:'X-Robots-Tag',value:'noindex'},{key:'Referrer-Policy',value:'no-referrer'}];
 const vercel={framework:null,buildCommand:'',installCommand:'',outputDirectory:'public',headers:[{source:'/(.*)',headers:common},{source:'/',headers:[{key:'Cache-Control',value:'no-cache'}]},{source:'/index.html',headers:[{key:'Cache-Control',value:'no-cache'}]},{source:'/__atlas/(.*)',headers:[{key:'Cache-Control',value:'public, max-age=0, must-revalidate'},{key:'Content-Type',value:'application/json'}]},{source:'/assets/(.*)',headers:[{key:'Cache-Control',value:'public, max-age=31536000, immutable'}]}]};
 await put(outputRoot,'frontend/vercel.json',Buffer.from(JSON.stringify(vercel,null,2)+'\n'));
 await put(outputRoot,'frontend/.vercelignore',Buffer.from('node_modules/\n.git/\n.internal/\nwork/\nsource-cache/\nOpenSim_Models/\nassets-store/\n*.log\n'));
 const uploadBytes=files.filter(f=>!f.remote).reduce((n,f)=>n+f.bytes,0)+(await readFile(resolve(outputRoot,'frontend/vercel.json'))).length+(await readFile(resolve(outputRoot,'frontend/.vercelignore'))).length;
 const supportFiles=[];for(const path of ['frontend/vercel.json','frontend/.vercelignore']){const bytes=await readFile(resolve(outputRoot,path));supportFiles.push({path,bytes:bytes.length,sha256:sha(bytes)});}
 const report={supportFiles,schemaVersion:'atlas-vercel-split-v1',snapshotId:manifest.snapshotId,baseHead:manifest.baseHead,deliveryBasis:manifest.deliveryBasis,authority:manifest.authority,files,config,uploadBytes,remoteBytes:files.filter(f=>f.remote).reduce((n,f)=>n+f.bytes,0),cliTargetMet:uploadBytes<=90000000,assetEncoding:'identity',privateInputsUploaded:false,deployed:false,providerVerified:false,requiresLogin:false,sourceDependencies:manifest.sourceDependencies};
 await put(outputRoot,'split-manifest.json',Buffer.from(JSON.stringify(report,null,2)+'\n'));await put(outputRoot,'split-manifest.sha256',Buffer.from(sha(await readFile(resolve(outputRoot,'split-manifest.json')))+'\n'));
 await checkVercelPackage(outputRoot);return report;
}
export async function checkVercelPackage(directory){
 const root=await realpath(directory),bytes=await readFile(resolve(root,'split-manifest.json')),digest=(await readFile(resolve(root,'split-manifest.sha256'),'utf8')).trim();if(sha(bytes)!==digest)throw Error('Split manifest changed');
 const manifest=JSON.parse(bytes);if(manifest.schemaVersion!=='atlas-vercel-split-v1'||!authorityOK(manifest.authority))throw Error('Invalid split authority');
 if(manifest.config?.revision!==manifest.snapshotId||!Array.isArray(manifest.files)||!Array.isArray(manifest.supportFiles))throw Error('Invalid split configuration');
 const urls=new Set();
 for(const row of manifest.files){
  if(!safe(row.path)||!Number.isSafeInteger(row.bytes)||row.bytes<0||!/^\/[\w./-]+$/.test(row.url)||urls.has(row.url)
   ||!/^([a-f0-9]{64})$/.test(row.sha256)||row.encoding!=='identity'||row.transportSha256!==row.sha256||row.transportBytes!==row.bytes)throw Error('Invalid file contract');
  urls.add(row.url);
  if(row.remote!==['motion','anatomy'].includes(row.category)||!['app','projection','motion','anatomy'].includes(row.category)
    ||!row.remote&&row.path!=='frontend/public'+row.url)throw Error('Invalid upload partition');
 }
 if(!urls.has('/index.html')||!urls.has('/404.html')||Object.keys(manifest.config.urls).length!==manifest.files.filter(r=>r.remote).length)throw Error('Incomplete split closure');
 const allowed=new Set(['frontend/vercel.json','frontend/.vercelignore','split-manifest.json','split-manifest.sha256',...manifest.files.map(f=>f.path)]);
 async function walk(path=''){for(const item of await readdir(resolve(root,path),{withFileTypes:true})){const p=path?path+'/'+item.name:item.name;if(item.isSymbolicLink())throw Error('Package symlink');if(item.isDirectory())await walk(p);else if(!allowed.has(p))throw Error('Unexpected upload file: '+p);}}
 await walk();for(const row of manifest.supportFiles??[]){const b=await bytesAt(root,row.path);if(b.length!==row.bytes||sha(b)!==row.sha256)throw Error('Configuration changed');}
 for(const row of manifest.files){const b=await bytesAt(root,row.path);if(b.length!==row.bytes||sha(b)!==row.sha256)throw Error('Package bytes changed');if(row.remote&&(row.contentType!=='model/gltf-binary'||row.path!==`assets-store/${row.sha256}.glb`||manifest.config.urls[row.url]!==`${validateOrigin(new URL(manifest.config.urls[row.url]).origin)}/${row.sha256}.glb`))throw Error('Invalid immutable map');}
 const front=manifest.files.filter(r=>!r.remote).reduce((n,r)=>n+r.bytes,0)+manifest.supportFiles.reduce((n,r)=>n+r.bytes,0);
 if(front!==manifest.uploadBytes||manifest.remoteBytes!==manifest.files.filter(r=>r.remote).reduce((n,r)=>n+r.bytes,0))throw Error('Partition size changed');
 return {root,manifest};
}
/** Cross-origin static transport emulator; no app dev middleware and no cloud validity claim. */
export async function openVercelPreview(directory,assetMode=false){
 const {root,manifest}=await checkVercelPackage(directory);const files=new Map(manifest.files.filter(f=>f.remote===assetMode).map(f=>[assetMode?'/'+f.sha256+'.glb':f.url,f]));
 const server=createServer(async(req,res)=>{
  if(assetMode){res.setHeader('Access-Control-Allow-Origin','*');res.setHeader('Access-Control-Expose-Headers','ETag, Content-Length');res.setHeader('Cross-Origin-Resource-Policy','cross-origin');res.setHeader('Timing-Allow-Origin','*');}
  res.setHeader('X-Content-Type-Options','nosniff');
  try{
   const url=new URL(req.url??'/','http://localhost').pathname,row=files.get(url==='/'?'/index.html':url);
   if(!['GET','HEAD'].includes(req.method)||!row){res.setHeader('Cache-Control','no-store');res.writeHead(404);res.end('Not found');return;}
   const b=await bytesAt(root,row.path);if(b.length!==row.bytes||sha(b)!==row.sha256)throw Error('Integrity changed');
   res.setHeader('Content-Type',row.contentType);res.setHeader('Content-Length',b.length);res.setHeader('ETag','"'+row.sha256+'"');res.setHeader('Cache-Control',row.remote||row.url.startsWith('/assets/')?'public, max-age=31536000, immutable':'public, max-age=0, must-revalidate');
   if(req.headers['if-none-match']==='"'+row.sha256+'"'){res.writeHead(304);res.end();return;}res.writeHead(200);res.end(req.method==='HEAD'?undefined:b);
  }catch{res.writeHead(503);res.end('Package integrity failed');}
 });return {server,manifest};
}
