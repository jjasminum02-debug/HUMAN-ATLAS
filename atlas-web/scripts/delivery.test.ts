import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFile,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {execFileSync} from 'node:child_process';
import {fileURLToPath,pathToFileURL} from 'node:url';
import ts from 'typescript';
import {wholeBodyPlugin} from '../plugins/wholeBody.ts';
import {readDatasetRoute} from '../src/viewer/datasets/integration.ts';
const root=fileURLToPath(new URL('../../',import.meta.url));
function harness(plugin:any){
 let handler:any;const listeners=new Map<string,Function[]>();
 const watcher={add:()=>{},on:(name:string,f:Function)=>{listeners.set(name,[...(listeners.get(name)??[]),f]);return watcher;},off:()=>{}};
 plugin.configureServer({watcher,middlewares:{use:(...args:any[])=>{handler=args.at(-1);}},httpServer:{once:()=>{}}});
 return {invalidate:()=>{for(const f of listeners.get('change')??[])f(root+'atlas-data/source-cache/datasets/index.json');},
 call:(url:string,requestHeaders:Record<string,string>={})=>new Promise<{status:number,body:string,headers:Record<string,string>}>((resolve,reject)=>{
  const headers:Record<string,string>={};
  const res={statusCode:200,setHeader:(name:string,value:string)=>{headers[name.toLowerCase()]=value;},end:(bytes:any)=>resolve({status:res.statusCode,body:bytes?.toString()??'',headers})};
  Promise.resolve(handler({url,headers:requestHeaders,destroyed:false},res,()=>resolve({status:404,body:''}))).catch(reject);
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
test('local integration route serves the validated compact allowlist, never the developer ledger',async()=>{
 const h=harness(wholeBodyPlugin(root));
 const response=await h.call('/__atlas/integration.json');
 assert.equal(response.status,200);
 assert.equal(response.headers['content-type'],'application/json');
 assert.equal(response.headers['cache-control'],'no-store');
 assert.equal(response.headers['content-length'],String(Buffer.byteLength(response.body)));
 const value=JSON.parse(response.body);
 const rawBytes=await readFile(root+'atlas-data/overlays/za-local-integration.json');
 const raw=JSON.parse(rawBytes.toString());
 assert.equal(value.projectionSchema,'whole-body-local-runtime-v5');
 const supplementBytes=await readFile(root+'atlas-data/manifests/bodyparts3d-r4-t100-source-supplement.json');
 const supplement=JSON.parse(supplementBytes.toString());
 const nerveBytes=await readFile(root+'atlas-data/manifests/nerve-scene-t66.json');const nerve=JSON.parse(nerveBytes.toString());
 const nerveHash=createHash('sha256').update(nerveBytes).digest('hex');
 const nerveRightsHash=createHash('sha256').update(await readFile(root+nerve.rightsPath)).digest('hex');
 const nerveCount=nerve.objects.length;
 const supplementHash=createHash('sha256').update(supplementBytes).digest('hex');
 assert.equal(value.sourceOverlaySha256,createHash('sha256').update([createHash('sha256').update([createHash('sha256').update(rawBytes).digest('hex'),supplementHash].join('\n')).digest('hex'),nerveHash].join('\n')).digest('hex'));
 const supplementRights=await readFile(root+supplement.rightsDecision.evidencePath);
 assert.equal(value.rightsEvidenceSha256,createHash('sha256').update([createHash('sha256').update([raw.policy.rightsEvidenceSha256,createHash('sha256').update(supplementRights).digest('hex')].join('\n')).digest('hex'),nerveRightsHash].join('\n')).digest('hex'));
 assert.equal(value.objects.length,raw.objects.length+supplement.objects.length+nerveCount);
 assert.equal(value.scope.targets,542);assert.equal(value.scope.memberships,563);assert.equal(value.scope.regions,12);
 assert.equal(value.objects.filter((row:any)=>row.localDisplayEligible).length,685+nerveCount);
 assert.equal(value.objects.filter((row:any)=>row.localDisplayEligible&&!row.defaultVisible).length,13);
 assert.equal(value.objects.filter((row:any)=>row.haConceptId!==null).length,raw.objects.filter((row:any)=>row.haConceptId!==null).length);
 assert.equal(value.objects.every((row:any)=>row.humanReview==='not_performed'&&row.publicRedistribution==='held'),true);
 assert.equal(['TA2:','targetTerminologyEvidence','targetRelationEvidence','evidenceSources','nameEvidence','locator','work/evidence','https://'].some(token=>response.body.includes(token)),false);
 const datasetResponse=await h.call('/__atlas/datasets/human-atlas-local/manifest.json');
 assert.equal(datasetResponse.status,200);
 const dataset=JSON.parse(datasetResponse.body);
 assert.equal(dataset.namespace,'human-atlas-local');assert.equal(dataset.geometrySpace,'mixed');
 assert.equal(dataset.instances.length,raw.objects.length+supplement.objects.length+nerveCount);
 assert.equal(dataset.instances.filter((row:any)=>row.sourceNamespace==='za-c7010a9').length,raw.objects.length+nerveCount);
 assert.equal(dataset.instances.filter((row:any)=>row.sourceNamespace==='bp3d-r4').length,supplement.objects.length);
 assert.equal(dataset.instances.filter((row:any)=>row.sourceNamespace==='bp3d-r4'&&row.canonicalConceptId===null&&row.learnerBinding==='source_only_unbound'&&row.defaultLearnerVisible===false).length,supplement.objects.length);
 const scoped=JSON.parse((await readFile(root+'atlas-data/catalog/target-scope-t96.json')).toString());
 const associatedTargets=new Set(supplement.objects.map((row:any)=>row.targetAssociation.targetId));
 assert.equal(associatedTargets.size,supplement.summary.targetCount);
 assert.equal(supplement.objects.length,supplement.summary.uniqueObjects);
 assert.equal([...associatedTargets].every(id=>scoped.targets.some((target:any)=>target.id===id)),true);
 const supplementSourceKeys=new Set(supplement.objects.map((row:any)=>row.sourceKey));
 const paths=value.objects.filter((row:any)=>supplementSourceKeys.has(row.sourceKey));
 assert.equal(paths.reduce((n:number,row:any)=>n+row.targetRoutes.length,0),supplement.objects.reduce((n:number,row:any)=>n+row.regionIds.length,0));
 assert.equal(paths.filter((row:any)=>row.selectionSuppressSourceKeys?.length).length,3);
 const routeKeys=paths.flatMap((row:any)=>row.targetRoutes.map((route:any)=>route.key));
 assert.equal(new Set(routeKeys).size,routeKeys.length);
 assert.equal(routeKeys.every((key:string)=>/^TR-[a-f0-9]{24}$/.test(key)),true);
 const regions=scoped.regions.map((region:any)=>region.regionId);
 for(const row of paths) for(const route of row.targetRoutes) {
  const result=readDatasetRoute(`?targetPathKey=${route.key}`,value.objects,regions,'inspection');
  assert.equal(result.selected,row.sourceKey);
  assert.equal(result.targetPathKey,route.key);
  assert.deepEqual(result.regions,[route.regionId]);
  assert.equal(JSON.stringify(result).includes('TA2:'),false);
 }
 assert.deepEqual(new Set(supplement.objects.filter((row:any)=>row.targetAssociation.targetId==='TA2:1282').map((row:any)=>row.sourceIdentity.sourceElementFileId)),new Set(['FJ3152','FJ3288','FJ3393']));
 assert.equal(supplement.objects.filter((row:any)=>row.targetAssociation.targetId==='TA2:1282'&&row.regionIds.includes('gluteal-hip')).length,0);
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

test('verified GLB uses conditional private cache and changed bytes still fail closed',async()=>{
 const h=harness(wholeBodyPlugin(root));
 const registry=JSON.parse((await readFile(root+'atlas-data/source-cache/datasets/za/registry.json')).toString());
 const entry=registry.files[0],url=`/__atlas/datasets/za-c7010a9/${entry.id}.glb`;
 const first=await h.call(url);assert.equal(first.status,200);assert.equal(first.headers.etag,`"${entry.sha256}"`);
 assert.equal(first.headers['cache-control'],'private, no-cache');
 const warm=await h.call(url,{'if-none-match':first.headers.etag});assert.equal(warm.status,304);assert.equal(warm.body,'');
 const stale=await h.call(url,{'if-none-match':'"stale"'});assert.equal(stale.status,200);
 const original=await readFile(entry.path);
 try{await writeFile(entry.path,Buffer.concat([original,Buffer.from([0])]));assert.equal((await h.call(url,{'if-none-match':first.headers.etag})).status,503);}
 finally{await writeFile(entry.path,original);h.invalidate();}
});
