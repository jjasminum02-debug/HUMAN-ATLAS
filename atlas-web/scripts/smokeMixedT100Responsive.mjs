/** Actual learner-app smoke for mixed T100 routes at desktop/tablet/mobile widths. */
import { createRequire } from 'node:module';
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const args=process.argv.slice(2);
const arg=(key,fallback)=>{const i=args.indexOf(key);return i<0?fallback:args[i+1];};
if(!arg('--packages')||!arg('--chrome')||!arg('--base-url'))throw Error('Pass bundled Playwright modules, Chrome executable and local app URL.');
const require=createRequire(resolve(arg('--packages'),'t100-responsive-smoke.cjs'));
const {chromium}=require('playwright');
const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
const root=resolve(fileURLToPath(new URL('../..',import.meta.url)));
const routePath=arg('--route-validation','work/evidence/T100/source-completion-2026-10-01/integration/runtime-v6/mixed-runtime-route-validation.json');
const relationPath=arg('--relations','work/evidence/T100/source-completion-2026-10-01/integration/runtime-v6/supplement-target-relation-ledger.json');
const relations=JSON.parse(await readFile(resolve(root,relationPath),'utf8')).relations;
const routes=JSON.parse(await readFile(resolve(root,routePath),'utf8'));
const supplement=JSON.parse(await readFile(resolve(root,'atlas-data/manifests/bodyparts3d-r4-t100-source-supplement.json'),'utf8'));
const expectedRuntime=routes.runtimeEndpoint;
const sourceByKey=new Map(supplement.objects.map(row=>[row.sourceKey,row]));
const queryFor=sourceKey=>{
 const relation=relations.find(row=>row.sourceKey===sourceKey);
 if(!relation)throw Error(`missing exact current target route for ${sourceKey}`);
 return `/?regions=${encodeURIComponent(relation.regionId)}&targetPathKey=${encodeURIComponent(relation.targetRouteKey)}`;
};
const widths=[{width:1440,height:1000},{width:1024,height:900},{width:390,height:844}];
const out=resolve(root,arg('--out','work/evidence/T100/source-completion-2026-10-01/integration/browser-responsive-v6'));
await mkdir(resolve(out,'screenshots'),{recursive:true});
const browser=await chromium.launch({headless:true,executablePath:arg('--chrome')});
const results=[];
try{
 for(const viewport of widths){
  const page=await browser.newPage({viewport,deviceScaleFactor:1});
  const consoleErrors=[],resourceErrors=[],failedRequests=[];page.on('pageerror',e=>consoleErrors.push({kind:'pageerror',message:String(e)}));page.on('console',m=>{if(m.type()==='error')consoleErrors.push({kind:'console',message:m.text(),location:m.location()});});
  page.on('response',r=>{if(r.status()>=400)resourceErrors.push({status:r.status(),url:r.url()});});
  page.on('requestfailed',r=>failedRequests.push({url:r.url(),error:r.failure()?.errorText??null}));
  const sourceKey=viewport.width===1024?'BP3D4-FJ2741':viewport.width===390?'BP3D4-FJ1538':'BP3D4-FJ3152';
  const url=arg('--base-url')+queryFor(sourceKey);
  await page.goto(url,{waitUntil:'domcontentloaded',timeout:30000});
  const delivered=await page.evaluate(async()=>{const bytes=await(await fetch('/__atlas/integration.json')).arrayBuffer();return{bytes:bytes.byteLength,sha256:[...new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))].map(x=>x.toString(16).padStart(2,'0')).join('')}});
  if(delivered.sha256!==expectedRuntime.sha256||delivered.bytes!==expectedRuntime.bytes)throw Error('browser runtime response differs from current route snapshot');
  await page.locator('.whole-body-canvas canvas').waitFor({timeout:30000});
  await page.waitForFunction(key=>{const canvas=document.querySelector('.whole-body-canvas canvas');if(!canvas?.dataset.dataset)return false;const state=JSON.parse(canvas.dataset.dataset);return state.selected===key&&state.visible.includes(key)&&state.pending===0&&!state.failed.length;},sourceKey,{timeout:30000});
  const state=await page.locator('.whole-body-canvas canvas').evaluate(el=>JSON.parse(el.dataset.dataset));
  const item=sourceByKey.get(sourceKey);const card=await page.locator('#study-details').innerText();
  const cardMatch=[item.names.en,item.names.koModern,item.names.koTraditional].filter(Boolean).every(value=>card.includes(value))
    && card.includes(item.side==='right'?'오른쪽':item.side==='left'?'왼쪽':'좌우 구분 없음');
  const overflow=await page.evaluate(()=>({document:document.documentElement.scrollWidth,body:document.body.scrollWidth,viewport:innerWidth,canvas:document.querySelector('.whole-body-canvas canvas')?.getBoundingClientRect().width}));
  let alternativeSuppression=null;
  if(sourceKey==='BP3D4-FJ3152'){
   const suppressed='ZA-c7010a9-74a765dc396d690d1642153e';
   alternativeSuppression={expected:suppressed,visible:state.visible.includes(suppressed),pass:!state.visible.includes(suppressed)};
  }
  let keyboardTabs=null;
  if(item.kind==='muscle'||item.kind==='muscle_surface_or_part'){
   const tabs=page.getByRole('tablist',{name:'학습 내용'});if(await tabs.count()){
    const structure=page.getByRole('tab',{name:'구조'});await structure.focus();await page.keyboard.press('ArrowRight');
    const featureSelected=await page.getByRole('tab',{name:'기능'}).getAttribute('aria-selected');
    await page.keyboard.press('ArrowLeft');const structureSelected=await structure.getAttribute('aria-selected');
    keyboardTabs={arrowRightToFeature:featureSelected==='true',arrowLeftToStructure:structureSelected==='true'};
   }
  }
  let searchCheck=null;
  if(viewport.width===1440){
   const search=page.getByRole('searchbox',{name:'구조 검색'});
   await search.fill(item.names.koModern??item.names.en);
   const visibleRows=await page.locator('.region-structure-list button').allTextContents();
   searchCheck={query:item.names.koModern??item.names.en,returnedSelectedSource:visibleRows.some(value=>value.includes(item.label)),resultCount:visibleRows.length};
   await search.fill('');
  }
  let history=null;
  if(viewport.width===1440){
   const nextUrl=arg('--base-url')+queryFor('BP3D4-FJ2741');await page.goto(nextUrl,{waitUntil:'domcontentloaded'});
   await page.waitForFunction(()=>JSON.parse(document.querySelector('.whole-body-canvas canvas')?.dataset.dataset??'{}').selected==='BP3D4-FJ2741',{timeout:20000});
   await page.goBack();await page.waitForFunction(()=>JSON.parse(document.querySelector('.whole-body-canvas canvas')?.dataset.dataset??'{}').selected==='BP3D4-FJ3152',{timeout:20000});
   await page.goForward();await page.waitForFunction(()=>JSON.parse(document.querySelector('.whole-body-canvas canvas')?.dataset.dataset??'{}').selected==='BP3D4-FJ2741',{timeout:20000});
   history={backRestoresPelvis:true,forwardRestoresHeadMuscle:true};
  }
  const screenshotName=`viewport-${viewport.width}.png`;
  const png=await page.screenshot({path:resolve(out,'screenshots',screenshotName),fullPage:true});
  results.push({viewport,sourceKey,targetId:relations.find(r=>r.sourceKey===sourceKey)?.targetId,selected:state.selected,visibleSourceCount:state.visible.length,
   cardMatch,side:item.side,cardFields:{english:item.names.en,modern:item.names.koModern,traditional:item.names.koTraditional},alternativeSuppression,
   keyboardTabs,searchCheck,history,runtime:delivered,overflow,consoleErrors,resourceErrors,failedRequests,screenshot:`screenshots/${screenshotName}`,screenshotSha256:hash(png)});
  await page.close();
 }
}finally{await browser.close();}
const result={schemaVersion:'t100-mixed-responsive-browser-smoke-v1',taskId:'T100',checkedAt:new Date().toISOString(),runtime:expectedRuntime,
 results,summary:{viewports:results.length,cardMatches:results.filter(r=>r.cardMatch).length,consoleErrors:results.reduce((n,r)=>n+r.consoleErrors.length,0),
 allNoHorizontalOverflow:results.every(r=>r.overflow.document<=r.overflow.viewport&&r.overflow.body<=r.overflow.viewport),
 exactPelvisCounterpartSuppression:results.find(r=>r.alternativeSuppression)?.alternativeSuppression.pass===true,
 keyboardPass:results.filter(r=>r.keyboardTabs).every(r=>r.keyboardTabs.arrowRightToFeature&&r.keyboardTabs.arrowLeftToStructure),
 searchPass:results.filter(r=>r.searchCheck).every(r=>r.searchCheck.returnedSelectedSource),
 historyPass:results.find(r=>r.history)?.history.backRestoresPelvis&&results.find(r=>r.history)?.history.forwardRestoresHeadMuscle}};
await writeFile(resolve(out,'responsive-browser-smoke.json'),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify(result.summary));
if(result.summary.cardMatches!==3||result.summary.consoleErrors!==0||!result.summary.allNoHorizontalOverflow
 ||!result.summary.exactPelvisCounterpartSuppression||!result.summary.keyboardPass||!result.summary.searchPass||!result.summary.historyPass)process.exitCode=1;
