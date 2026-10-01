import {createRequire} from 'node:module';import {writeFile,mkdir} from 'node:fs/promises';import {resolve} from 'node:path';
const require=createRequire('/Users/daniel/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/t58.cjs');const {chromium}=require('playwright');const out=resolve('../work/evidence/T58/app-finish-2026-10-01');const browser=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true});const results=[];
for(const width of [1440,1024,390]){
 const page=await browser.newPage({viewport:{width,height:width===390?844:1000}}),errors=[];page.on('pageerror',e=>errors.push(String(e)));await page.goto('http://127.0.0.1:5178/?regions=upper-limb');
 await page.waitForFunction(()=>document.querySelector('.whole-body-canvas')?.inert===false);
 const search=page.getByRole('searchbox');await search.fill('위팔두갈래');await page.locator('.region-structure-list button').filter({hasText:'장두'}).first().click();await page.waitForTimeout(400);const previous=page.url();
 await search.fill('위팔세갈래');await page.locator('.region-structure-list button').filter({hasText:'내측두'}).first().click();await page.waitForTimeout(400);const next=page.url();
 await page.goBack();await page.waitForTimeout(300);const back={url:page.url(),query:await search.inputValue(),card:await page.locator('#study-details h2').innerText()};
 await page.goForward();await page.waitForTimeout(300);const forward={url:page.url(),query:await search.inputValue(),card:await page.locator('#study-details h2').innerText()};
 const pass=back.url===previous&&back.query==='위팔두갈래'&&back.card.includes('상완이두근 장두')&&forward.url===next&&forward.query==='위팔세갈래'&&forward.card.includes('상완삼두근 내측두')&&errors.length===0;
 results.push({width,pass,back,forward,errors});await page.close();
}
await browser.close();await writeFile(resolve(out,'history-final.json'),JSON.stringify({taskId:'T58',results},null,2)+'\n');console.log(JSON.stringify(results));if(results.some(r=>!r.pass))process.exitCode=1;
