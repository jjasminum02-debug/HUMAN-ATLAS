import {createRequire} from 'node:module';
import {mkdir,writeFile,readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {resolve} from 'node:path';
import * as THREE from 'three';
const require=createRequire('/Users/daniel/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/t58.cjs');
const {chromium}=require('playwright');
const out=resolve('../work/evidence/T58/app-finish-2026-10-01/browser');await mkdir(out,{recursive:true});
const nav=JSON.parse(await readFile('../atlas-data/navigation/atlas-navigation.json','utf8')).categories;
const browser=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true});
const results=[], captures=[], checks=[];let page;
const assert=(name,pass,detail)=>{checks.push({name,pass,detail});if(!pass)throw Error(name+': '+JSON.stringify(detail));};
const wait=async()=>{await page.waitForFunction(()=>{const c=document.querySelector('.whole-body-canvas canvas');if(!c?.dataset.dataset)return false;const s=JSON.parse(c.dataset.dataset);return s.visible.length>0&&s.pending===0&&!document.querySelector('.whole-body-canvas').inert;},null,{timeout:30000});await page.waitForTimeout(600);};
const state=()=>page.locator('.whole-body-canvas canvas').evaluate(c=>({dataset:JSON.parse(c.dataset.dataset),scene:JSON.parse(c.dataset.scene||'{}')}));
const shot=async(name)=>{const bytes=await page.screenshot({path:resolve(out,name+'.png')});captures.push({path:name+'.png',sha256:createHash('sha256').update(bytes).digest('hex')});};
const region=async(id)=>{if(await page.locator('.explore-trigger').isVisible())await page.locator('.explore-trigger').click();await page.locator('.region-all-toggle').click();await page.getByRole('button',{name:nav.find(c=>c.id===id).labelKo,exact:true}).click();if(await page.locator('.explore-close').isVisible())await page.locator('.explore-close').click();await wait();};
const search=async(q)=>{await page.getByRole('searchbox',{name:'구조 검색'}).fill(q);};
const pickSearch=async(text)=>{await page.locator('.region-structure-list button').filter({hasText:text}).first().click();await wait();};
const layout=async(label)=>{const rects=await page.evaluate(()=>{const rect=sel=>{const r=document.querySelector(sel)?.getBoundingClientRect();return r?{x:r.x,y:r.y,right:r.right,bottom:r.bottom,width:r.width,height:r.height}:null;};return {viewport:{width:innerWidth,height:innerHeight},documentWidth:document.documentElement.scrollWidth,canvas:rect('.whole-body-canvas'),tools:rect('.body-tools'),card:rect('.study-details'),sidebar:rect('.study-sidebar'),status:rect('.body-status'),buttonOverlaps:[...document.querySelectorAll('.body-tools button')].filter(e=>{const r=e.getBoundingClientRect();return r.right>innerWidth||r.bottom>innerHeight}).length}});
 const overlap=(a,b)=>a&&b&&Math.min(a.right,b.right)-Math.max(a.x,b.x)>1&&Math.min(a.bottom,b.bottom)-Math.max(a.y,b.y)>1;
 assert(label+' layout',rects.documentWidth<=rects.viewport.width&&rects.canvas.height>=170&&rects.canvas.width>=260&&!overlap(rects.canvas,rects.tools)&&!overlap(rects.canvas,rects.card)&&!overlap(rects.tools,rects.card)&&!overlap(rects.tools,rects.status)&&!overlap(rects.status,rects.card)&&rects.buttonOverlaps===0,rects);return rects;};
try{
for(const width of (process.argv[2] ? [Number(process.argv[2])] : [1440,1024,390])){
 page=await browser.newPage({viewport:{width,height:width===1440?1000:width===1024?900:844}});const errors=[],httpFailures=[];
 page.on('pageerror',e=>errors.push(String(e)));page.on('console',m=>{if(m.type()==='error')errors.push(m.text());});page.on('response',r=>{if(r.status()>=400)httpFailures.push({url:r.url(),status:r.status()});});
 await page.goto('http://127.0.0.1:5178/',{waitUntil:'domcontentloaded'});await wait();
 const runtime=await page.evaluate(async()=>await(await fetch('/__atlas/integration.json')).json());const rows=runtime.objects;
 const first=await state();const root=first.dataset.root;
 const layouts=[await layout(width+' whole')];await shot(width+'-whole');
 if(width===1440){
  for(const c of nav){await region(c.id);const s=await state();const eligible=rows.filter(r=>r.routeAudience==='learner'&&r.localDisplayEligible&&r.defaultVisible&&r.regionIds.includes(c.id));assert('region '+c.id+' exact visible source set',eligible.length===s.dataset.visible.length&&eligible.every(r=>s.dataset.visible.includes(r.sourceKey)),{expected:eligible.length,visible:s.dataset.visible.length});assert('region '+c.id+' single scene',s.dataset.root===root,s.dataset.root);await shot('region-'+c.id);}
  for(const [id,rx,expected] of [['neck',/^Vertebra C|^Atlas \(C1\)|^Axis \(C2\)/,7],['thorax',/^Vertebra T/,12],['abdomen-lumbar',/^Vertebra L/,5]]){await region(id);const s=await state(),bones=rows.filter(r=>r.localDisplayEligible&&rx.test(r.names.en));assert(id+' spine context',bones.length===expected&&bones.every(r=>s.dataset.visible.includes(r.sourceKey)),bones.map(r=>r.names.en));}
 }
 for(const id of ['head','back','thigh','foot']) {await region(id);layouts.push(await layout(width+' '+id));await shot(width+'-'+id);}
 await region('neck');await search('셋째 목뼈');await pickSearch('셋째 목뼈');await page.getByRole('button',{name:'선택만 보기',exact:true}).click();await wait();await page.getByRole('button',{name:'선택 맞춤',exact:true}).click();await page.waitForTimeout(700);await shot(width+'-C3-local-highlight');await page.getByRole('button',{name:'보기 복원',exact:true}).click();await wait();
 await region('upper-limb');await search('제3중수골');await pickSearch('제3중수골');await page.getByRole('button',{name:'선택 맞춤',exact:true}).click();await page.waitForTimeout(700);await page.locator('canvas').focus();for(let i=0;i<8;i++)await page.keyboard.press('-');await page.waitForTimeout(700);await shot(width+'-hand');
 await region('upper-limb');await search('위팔두갈래');
 const found=await page.locator('.region-structure-list button').allTextContents();assert(width+' biceps prefix returns two heads',found.length===2&&found.some(x=>x.includes('장두'))&&found.some(x=>x.includes('단두')),found);
 await pickSearch('장두');const long=await state();assert(width+' long head correct names',(await page.locator('#study-details').innerText()).includes('위팔두갈래근 긴갈래'),null);
 layouts.push(await layout(width+' selected'));await shot(width+'-biceps-long');
 await page.getByRole('button',{name:'오른쪽',exact:true}).click();await wait();const right=await state();assert(width+' right source/card',rows.find(r=>r.sourceKey===right.dataset.selected)?.side==='right'&&(await page.locator('#study-details').innerText()).includes('오른쪽'),right.dataset.selected);
 const cameraBefore=right.scene.camera;
 await page.getByRole('button',{name:'왼쪽',exact:true}).click();await wait();const left=await state();assert(width+' left source/card',rows.find(r=>r.sourceKey===left.dataset.selected)?.side==='left',left.dataset.selected);assert(width+' selection camera continuity',JSON.stringify(cameraBefore)===JSON.stringify(left.scene.camera),{before:cameraBefore,after:left.scene.camera});
 await page.getByRole('tab',{name:'구조',exact:true}).focus();await page.keyboard.press('ArrowRight');assert(width+' keyboard feature tab',(await page.getByRole('tab',{name:'기능',exact:true}).getAttribute('aria-selected'))==='true',null);await page.keyboard.press('ArrowLeft');
 const saved=await page.evaluate(()=>({url:location.href,query:document.querySelector('input[type=search]').value}));
 await search('위팔세갈래');await pickSearch('내측두');const next=await page.evaluate(()=>({url:location.href,query:document.querySelector('input[type=search]').value}));
 await page.goBack();await wait();assert(width+' history back restores query and route',(await page.url())===saved.url&&(await page.getByRole('searchbox').inputValue())===saved.query,saved); // Restore the search associated with the visited card.
 await page.goForward();await wait();assert(width+' history forward restores query and route',(await page.url())===next.url&&(await page.getByRole('searchbox').inputValue())===next.query,next);
 await region('abdomen-lumbar');await search('외복사근');await pickSearch('외복사근');const outer=(await state()).dataset.selected;
 await page.getByRole('button',{name:'선택 숨기기',exact:true}).click();await page.waitForTimeout(300);assert(width+' outer hidden',!(await state()).dataset.visible.includes(outer),outer);
 if(width===1440) {
  const current=await state(), box=await page.locator('canvas').boundingBox();
  const camera=new THREE.PerspectiveCamera(35,box.width/box.height,.005,50);camera.position.fromArray(current.scene.camera);camera.lookAt(new THREE.Vector3().fromArray(current.scene.target));camera.updateMatrixWorld();
  const candidate=rows.find(r=>r.names.en==='Internal abdominal oblique muscle'&&r.side===rows.find(r=>r.sourceKey===outer).side);
  let hit=null;
  for(const fx of [.3,.5,.7]) {for(const fy of [.3,.5,.7]) {
    const p=new THREE.Vector3(...candidate.bounds[0]).lerp(new THREE.Vector3(...candidate.bounds[1]),.5);p.x=candidate.bounds[0][0]+fx*(candidate.bounds[1][0]-candidate.bounds[0][0]);p.y=candidate.bounds[0][1]+fy*(candidate.bounds[1][1]-candidate.bounds[0][1]);p.project(camera);
    if(Math.abs(p.x)>1||Math.abs(p.y)>1)continue;
    await page.mouse.click(box.x+(p.x+1)*box.width/2,box.y+(1-p.y)*box.height/2);await page.waitForTimeout(100);
    const selected=(await state()).dataset.selected;
    if(selected&&selected!==outer) {hit=rows.find(r=>r.sourceKey===selected);break;}
  }if(hit)break;}
  assert('actual pointer accesses surface under hidden outer',Boolean(hit)&&hit.names.en!=='External abdominal oblique muscle'&&!(await state()).dataset.visible.includes(outer),hit&&{sourceKey:hit.sourceKey,name:hit.names.en});
 }
 await search('내복사근');await pickSearch('내복사근');const inner=(await state()).dataset.selected;assert(width+' persistent outer hiding on inner selection',inner!==outer&&!(await state()).dataset.visible.includes(outer),{outer,inner});await shot(width+'-deep-after-hide');
 await page.getByRole('button',{name:'되돌리기',exact:true}).click();await wait();assert(width+' undo restores outer without changing inner',(await state()).dataset.visible.includes(outer)&&(await state()).dataset.selected===inner,null);
 await search('외복사근');await pickSearch('외복사근');await page.getByRole('button',{name:'선택 숨기기',exact:true}).click();
 await search('내복사근');await pickSearch('내복사근');await page.getByRole('button',{name:'보기 복원',exact:true}).click();await wait();assert(width+' restore outer',(await state()).dataset.visible.includes(outer),null);
 await search('외복사근');await pickSearch('외복사근');await page.getByRole('button',{name:'선택 숨기기',exact:true}).click();
 await search('');if(width===390&&!(await page.locator('.study-sidebar').isVisible()))await page.locator('.explore-trigger').click();await page.getByRole('button',{name:'배·허리',exact:true}).click();if(width===390)await page.locator('.explore-close').click();await wait();assert(width+' explicit category reset restores hidden',(await state()).dataset.visible.includes(outer),null);
 await region('upper-limb');await search('삼각근');const deltoids=await page.locator('.region-structure-list button').allTextContents();assert(width+' all requested deltoid labels',['전면삼각근','측면삼각근','후면삼각근'].every(t=>deltoids.some(x=>x.includes(t))),deltoids);
 await search('삼각근 견봉부');await pickSearch('측면삼각근');assert(width+' anatomical deltoid subtitle',(await page.locator('.anatomical-part-subtitle').innerText()).includes('견봉부'),null);await shot(width+'-deltoid');
 await page.getByRole('button',{name:'선택만 보기',exact:true}).click();await wait();const isolated=await state();assert(width+' isolation only selected',isolated.dataset.visible.length===1&&isolated.dataset.visible[0]===isolated.dataset.selected,isolated.dataset.visible);
 await page.getByRole('button',{name:'근육',exact:true}).click();await page.waitForTimeout(500);assert(width+' layer off beats isolation',JSON.parse(await page.locator('canvas').getAttribute('data-dataset')).visible.length===0,null);await page.getByRole('button',{name:'근육',exact:true}).click();await wait();await page.getByRole('button',{name:'보기 복원',exact:true}).click();await wait();
 const canvas=page.locator('canvas');await canvas.focus();const beforeKey=(await state()).scene.camera;await page.keyboard.press('ArrowLeft');await page.waitForTimeout(700);assert(width+' keyboard camera rotation',JSON.stringify(beforeKey)!==JSON.stringify((await state()).scene.camera),null);
 await page.getByRole('button',{name:'앱 정보',exact:true}).click();assert(width+' info dialog',await page.locator('dialog').isVisible(),null);await page.keyboard.press('Escape');assert(width+' info escape',!(await page.locator('dialog').isVisible()),null);
 assert(width+' no console/http errors',errors.length===0&&httpFailures.length===0,{errors,httpFailures});assert(width+' no scene remount',(await state()).dataset.root===root,null);
 results.push({width,layouts,errors,httpFailures,root});await page.close();
}
} finally {await writeFile(resolve(out,process.argv[2] ? 'browser-validation-'+process.argv[2]+'-final.json' : 'browser-validation.json'),JSON.stringify({taskId:'T58',checks,results,captures,limitations:['390px desktop Chrome viewport; not a real mobile device.','Representative visual verification, not full extent or every-target visual acceptance.']},null,2)+'\n');await browser.close();}
console.log(JSON.stringify({checks:checks.length,passed:checks.filter(x=>x.pass).length,captures:captures.length}));
