import {createRequire} from 'node:module';
import {mkdir,writeFile} from 'node:fs/promises';
import {resolve} from 'node:path';
const require=createRequire('/Users/daniel/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/t58.cjs');
const {chromium}=require('playwright');
const phase=process.argv[2]||'before', out=resolve('../work/evidence/T58/app-finish-2026-10-01',phase);
await mkdir(out,{recursive:true});
const browser=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true});
const page=await browser.newPage({viewport:{width:1440,height:1000}});
const errors=[];page.on('pageerror',e=>errors.push(String(e)));page.on('console',m=>{if(m.type()==='error')errors.push(m.text());});
const state=()=>page.evaluate(()=>{const c=document.querySelector('.whole-body-canvas canvas');return {dataset:JSON.parse(c?.dataset.dataset||'{}'),scene:JSON.parse(c?.dataset.scene||'{}')}});
const settled=()=>page.waitForFunction(()=>{const c=document.querySelector('.whole-body-canvas canvas');if(!c?.dataset.dataset)return false;const s=JSON.parse(c.dataset.dataset);return s.visible.length>0&&s.pending===0&&document.querySelector('.whole-body-canvas')?.inert===false;},{timeout:45000});
const loads=[];
for(const mode of ['cold','warm']) {
 const begin=Date.now();await page.goto('http://127.0.0.1:5178/',{waitUntil:'domcontentloaded'});await settled();const assetReadyMs=Date.now()-begin;await page.waitForTimeout(700);
 loads.push({mode,assetReadyMs,settleDelayMs:700,readyMs:Date.now()-begin,resources:await page.evaluate(()=>{const entries=performance.getEntriesByType('resource');return {count:entries.length,transferBytes:entries.reduce((n,r)=>n+r.transferSize,0),encodedBodyBytes:entries.reduce((n,r)=>n+r.encodedBodySize,0),geometry:entries.filter(r=>r.name.endsWith('.glb')).map(r=>({name:r.name.split('/').pop(),transfer:r.transferSize,encoded:r.encodedBodySize,duration:r.duration}))}}),...await state()});
}
await page.screenshot({path:resolve(out,'whole.png')});
const box=await page.locator('.whole-body-canvas canvas').boundingBox();
await page.mouse.move(box.x+box.width/2,box.y+box.height/2);await page.mouse.down();for(let i=0;i<36;i++){await page.mouse.move(box.x+box.width/2+i*3,box.y+box.height/2+i*.8);await page.waitForTimeout(17);}await page.mouse.up();await page.waitForTimeout(1000);
const interaction=await state();
const labels=['목','가슴우리','배·허리','머리','팔·손','발','등','넙다리','종아리','어깨·어깨뼈'];
const cycles=[];
for(let i=0;i<20;i++){
 const begin=Date.now();await page.locator('.region-all-toggle').click();await page.getByRole('button',{name:labels[i%labels.length],exact:true}).click();await settled();await page.waitForTimeout(60);cycles.push({i,region:labels[i%labels.length],ms:Date.now()-begin,...await state()});
}
await page.locator('.region-all-toggle').click();await settled();await page.waitForTimeout(1000);
const end=await state();const gpu=await page.evaluate(()=>{const gl=document.querySelector('canvas')?.getContext('webgl2');const ext=gl?.getExtension('WEBGL_debug_renderer_info');return ext?{vendor:gl.getParameter(ext.UNMASKED_VENDOR_WEBGL),renderer:gl.getParameter(ext.UNMASKED_RENDERER_WEBGL)}:null});
await writeFile(resolve(out,'profile.json'),JSON.stringify({phase,viewport:{width:1440,height:1000},loads,interaction,cycles,end,gpu,errors,limitations:['CPU render call timing is not GPU duration.','GPU/VRAM/total-process memory is not observed.','Cold refers to a fresh browser context; OS disk cache is uncontrolled.']},null,2)+'\n');
console.log(JSON.stringify({phase,loads:loads.map(x=>({mode:x.mode,readyMs:x.readyMs,bytes:x.resources.transferBytes})),renderCpuP95Ms:interaction.scene.renderCpuP95Ms,frameIntervalP95Ms:interaction.scene.frameIntervalP95Ms,cacheBytes:end.dataset.bytes,pending:end.dataset.pending,errors}));await browser.close();
