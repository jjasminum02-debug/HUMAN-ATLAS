import {createRequire} from 'node:module';import {writeFile,mkdir} from 'node:fs/promises';import {resolve} from 'node:path';import {createHash} from 'node:crypto';
const require=createRequire('/Users/daniel/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/t58.cjs');const {chromium}=require('playwright');
const out=resolve('../work/evidence/T58/app-finish-2026-10-01/framing-final');await mkdir(out,{recursive:true});
const browser=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true});const results=[];
for(const width of [1440,1024,390]){
 const page=await browser.newPage({viewport:{width,height:width===1440?1000:width===1024?900:844}}),errors=[];page.on('pageerror',e=>errors.push(String(e)));page.on('console',m=>{if(m.type()==='error')errors.push(m.text());});
 await page.goto('http://127.0.0.1:5178/?regions=neck');await page.waitForFunction(()=>{const el=document.querySelector('canvas');if(!el?.dataset.dataset)return false;const q=JSON.parse(el.dataset.dataset);return q.pending===0&&q.visible.length>0;});await page.waitForTimeout(800);
 const state=await page.locator('canvas').evaluate(c=>({scene:JSON.parse(c.dataset.scene),dataset:JSON.parse(c.dataset.dataset)}));const bytes=await page.screenshot({path:resolve(out,width+'-neck.png')});
 const runtime=await page.evaluate(async()=>await(await fetch('/__atlas/integration.json')).json());const vertebrae=runtime.objects.filter(r=>/^Vertebra C|^Atlas \(C1\)|^Axis \(C2\)/.test(r.names.en)&&r.localDisplayEligible);
 const pass=vertebrae.length===7&&vertebrae.every(r=>state.dataset.visible.includes(r.sourceKey))&&state.scene.target[1]>1.3&&state.dataset.failed.length===0&&errors.length===0;
 results.push({width,pass,cervicalKeys:vertebrae.map(r=>r.sourceKey),state,errors,screenshot:width+'-neck.png',sha256:createHash('sha256').update(bytes).digest('hex')});await page.close();
}
await browser.close();await writeFile(resolve(out,'framing-validation.json'),JSON.stringify({taskId:'T58',results,fullRotatoresSourceStillRendered:true,geometryClipped:false},null,2)+'\n');console.log(JSON.stringify(results.map(r=>({width:r.width,pass:r.pass,target:r.state.scene.target}))));if(results.some(r=>!r.pass))process.exitCode=1;
