import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFile,writeFile} from 'node:fs/promises';
import {execFileSync} from 'node:child_process';
import {fileURLToPath,pathToFileURL} from 'node:url';
import ts from 'typescript';
import {wholeBodyPlugin} from '../plugins/wholeBody.ts';
const root=fileURLToPath(new URL('../../',import.meta.url));
function harness(plugin:any){
 let handler:any;const listeners=new Map<string,Function[]>();
 const watcher={add:()=>{},on:(name:string,f:Function)=>{listeners.set(name,[...(listeners.get(name)??[]),f]);return watcher;},off:()=>{}};
 plugin.configureServer({watcher,middlewares:{use:(...args:any[])=>{handler=args.at(-1);}},httpServer:{once:()=>{}}});
 return {invalidate:()=>{for(const f of listeners.get('change')??[])f(root+'atlas-data/source-cache/datasets/index.json');},
 call:(url:string)=>new Promise<{status:number,body:string}>((resolve,reject)=>{
  const res={statusCode:200,setHeader:()=>{},end:(bytes:any)=>resolve({status:res.statusCode,body:bytes?.toString()??''})};
  Promise.resolve(handler({url,destroyed:false},res,()=>resolve({status:404,body:''}))).catch(reject);
 })};
}
test('offline BP3D snapshot exactly matches original runtime composition',async()=>{
 const source=execFileSync('git',['show','50736284012c2534fd4be39699768974b5d63e80:atlas-web/plugins/wholeBody.ts'],{cwd:root,encoding:'utf8'});
 const js=ts.transpileModule(source,{compilerOptions:{module:ts.ModuleKind.ESNext,target:ts.ScriptTarget.ES2022}}).outputText
 .replace(/from '(\.\.\/[^']+)'/g,(_,path)=>`from '${pathToFileURL(root+'atlas-web/plugins/'+path).href}'`);
 const old=await import('data:text/javascript;base64,'+Buffer.from(js).toString('base64'));
 const expected=await harness(old.wholeBodyPlugin(root)).call('/manifest.json');
 const actual=await harness(wholeBodyPlugin(root)).call('/__atlas/body/manifest.json');
 assert.equal(expected.status,200);assert.equal(actual.status,200);assert.deepEqual(JSON.parse(actual.body),JSON.parse(expected.body));
});
test('delivery rejects path traversal, stale dependency, and changed derived chunk bytes',async()=>{
 const h=harness(wholeBodyPlugin(root));
 assert.equal((await h.call('/__atlas/datasets/../secret.glb')).status,404);
 const path=root+'atlas-data/source-cache/datasets/za/registry.json';const original=await readFile(path);
 try{
  const data=JSON.parse(original.toString());data.dependencies[0].sha256='0'.repeat(64);
  await writeFile(path,JSON.stringify(data));h.invalidate();assert.equal((await h.call('/__atlas/datasets/za-c7010a9/manifest.json')).status,503);
 }finally{await writeFile(path,original);h.invalidate();}
 const data=JSON.parse(original.toString());const chunk=data.files[0];const bytes=await readFile(chunk.path);
 try{await writeFile(chunk.path,Buffer.concat([bytes,Buffer.from([0])]));assert.equal((await h.call(`/__atlas/datasets/za-c7010a9/${chunk.id}.glb`)).status,503);}
 finally{await writeFile(chunk.path,bytes);h.invalidate();}
 assert.equal((await h.call('/__atlas/datasets/za-c7010a9/manifest.json')).status,200);
});
