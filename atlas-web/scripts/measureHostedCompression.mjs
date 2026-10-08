import { readFile, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { createHash } from 'node:crypto';
import { gzipSync, gunzipSync, brotliCompressSync, brotliDecompressSync, constants } from 'node:zlib';
import { performance } from 'node:perf_hooks';
const sha=b=>createHash('sha256').update(b).digest('hex');
const [snapshot,output,reusePath]=process.argv.slice(2);if(!snapshot||!output)throw Error('Usage: measureHostedCompression.mjs SNAPSHOT OUTPUT.json [PREVIOUS_EXPERIMENT.json]');
const previous=reusePath?JSON.parse(await readFile(reusePath,'utf8')):null;
const reused=[];
const manifest=JSON.parse(await readFile(resolve(snapshot,'snapshot.json'),'utf8')), files=[];
for(const row of manifest.files){
 const raw=await readFile(resolve(snapshot,row.path));if(raw.length!==row.bytes||sha(raw)!==row.sha256)throw Error('Snapshot changed');
 const old=previous?.files.find(f=>f.url===row.url&&f.sha256===row.sha256&&f.rawBytes===row.bytes);
 if(old&&['gzip6','gzip9','brotli6'].every(k=>old[k]?.exactBytes===true)){files.push(old);reused.push(row.url);continue;}
 const result={url:row.url,category:row.category,rawBytes:raw.length,sha256:row.sha256};
 for(const [name,compress,decode] of [
  ['gzip6',b=>gzipSync(b,{level:6}),gunzipSync],['gzip9',b=>gzipSync(b,{level:9}),gunzipSync],
  ['brotli6',b=>brotliCompressSync(b,{params:{[constants.BROTLI_PARAM_QUALITY]:6}}),brotliDecompressSync]]){
  const start=performance.now(),payload=compress(raw),compressed=performance.now(),decoded=decode(payload);
  result[name]={bytes:payload.length,encodeMs:compressed-start,decodeMs:performance.now()-compressed,exactBytes:decoded.equals(raw)};
  if(!result[name].exactBytes)throw Error('Lossless comparison failed');
 }
 if(row.url.endsWith('.glb')){
  const length=raw.readUInt32LE(12),doc=JSON.parse(raw.subarray(20,20+length)),binStart=28+length;
  const views=doc.bufferViews??[], hashes=new Map();let duplicateViewBytes=0;
  for(const view of views){const bytes=raw.subarray(binStart+(view.byteOffset??0),binStart+(view.byteOffset??0)+view.byteLength),key=sha(bytes);if(hashes.has(key))duplicateViewBytes+=bytes.length;else hashes.set(key,true);}
  result.glb={bufferViews:views.length,accessors:doc.accessors?.length??0,meshes:doc.meshes?.length??0,morphTargets:(doc.meshes??[]).reduce((n,m)=>n+m.primitives.reduce((v,p)=>v+(p.targets?.length??0),0),0),animations:doc.animations?.length??0,duplicateViewBytes,binBytes:doc.buffers?.[0]?.byteLength??0,requiredExtensions:doc.extensionsRequired??[]};
 }
 files.push(result);
}
const totals={};for(const key of ['rawBytes','gzip6','gzip9','brotli6'])totals[key]=files.reduce((n,r)=>n+(typeof r[key]==='number'?r[key]:r[key].bytes),0);
const report={snapshotId:manifest.snapshotId,files,totals,nodeVersion:process.version,measurement:'Node CPU roundtrip; not browser decode/GPU/VRAM',reuse:previous?{path:reusePath,snapshotId:previous.snapshotId,exactSHAReusedUrls:reused,newlyMeasured:files.length-reused.length}:null,exactWholeFileDuplicates:files.length-new Set(files.map(r=>r.sha256)).size,cliTargetBytes:90000000,cliTargetMet:totals.brotli6<=90000000,geometryModified:false};
await writeFile(output,JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({totals,cliTargetMet:report.cliTargetMet,duplicateViewBytes:files.reduce((n,r)=>n+(r.glb?.duplicateViewBytes??0),0)}));
