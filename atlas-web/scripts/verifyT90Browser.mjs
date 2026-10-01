import {createRequire} from 'node:module';import {mkdir,writeFile,readFile} from 'node:fs/promises';import {resolve} from 'node:path';import {createHash} from 'node:crypto';
const require=createRequire('/Users/daniel/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/t90.cjs');const {chromium}=require('playwright');const sharp=require('sharp');
const out=resolve('../work/evidence/T90/browser');await mkdir(out,{recursive:true});
const browser=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true});let page;const resume=process.argv.includes('--resume-after-attachments');const previous=resume?JSON.parse(await readFile(resolve(out,'checks.json'),'utf8')):null;const checks=previous?previous.checks.filter(c=>c.pass):[],captures=previous?previous.captures.filter(c=>!c.path.endsWith('/failure.png')):[],errors=[],profiles=previous?previous.profiles:{};
const check=(name,pass,detail)=>{const item={name,pass,detail};const old=checks.findIndex(c=>c.name===name);if(old>=0)checks[old]=item;else checks.push(item);if(!pass)throw Error(name+': '+JSON.stringify(detail))};
const wait=async()=>{await page.waitForFunction(()=>{const c=document.querySelector('.whole-body-canvas canvas');return c?.dataset.dataset&&JSON.parse(c.dataset.dataset).pending===0&&!document.querySelector('.whole-body-canvas').inert},null,{timeout:30000});await page.waitForTimeout(250)};
const state=()=>page.locator('.whole-body-canvas canvas').evaluate(c=>JSON.parse(c.dataset.dataset));const scene=()=>page.locator('.whole-body-canvas canvas').evaluate(c=>JSON.parse(c.dataset.scene));
const shot=async name=>{const bytes=await page.screenshot({path:resolve(out,name+'.png')});captures.push({path:'work/evidence/T90/browser/'+name+'.png',sha256:createHash('sha256').update(bytes).digest('hex')});return bytes};
const select=async name=>{await page.getByRole('searchbox',{name:'구조 검색'}).fill(name);await page.locator('.region-structure-list button').filter({hasText:name}).first().click();await wait()};
const button=name=>page.getByRole('button',{name,exact:true});
const same=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
try{
 page=await browser.newPage({viewport:{width:1440,height:1000}});page.on('pageerror',e=>errors.push(String(e)));page.on('console',m=>{if(m.type()==='error')errors.push(m.text())});
 await page.goto('http://127.0.0.1:5184/?regions=neck',{waitUntil:'domcontentloaded'});await wait();
 const runtime=await page.evaluate(async()=>await(await fetch('/__atlas/integration.json')).json());const rows=runtime.objects;const initial=await state();const root=initial.root;
 await writeFile(resolve(out,'runtime.json'),JSON.stringify(runtime));
 if(!resume){
 const names=s=>rows.filter(r=>s.visible.includes(r.sourceKey)).map(r=>r.names.en);
 check('neck core and no full-spine rotators',names(initial).includes('Vertebra C3')&&!names(initial).some(n=>/^Vertebra [TL]/.test(n)||n==='Rotatores'),names(initial));profiles.neck={dataset:initial,scene:await scene()};await shot('1440-neck');
 await button('뼈').click();await wait();const bonesOff=await state();check('bone-off includes contextual bones',rows.filter(r=>r.kind==='bone').every(r=>!bonesOff.visible.includes(r.sourceKey)),bonesOff);await button('뼈').click();await wait();
 // Plain region clicks replace the previous region. Route union remains available through explicit Shift-click.
 const regions=['head','neck','back','shoulder-scapular','thorax','abdomen-lumbar','pelvis-perineum','gluteal-hip','thigh','leg','foot','upper-limb'];
 for(const region of regions){
  await page.locator('.region-grid button').nth(regions.indexOf(region)).click();await wait();
  const s=await state();const actual=new URL(page.url()).searchParams.get('regions');check('region '+region+' single scene and exclusive filter',actual===region&&s.root===root&&s.failed.length===0&&s.visible.length>0,{region:actual,visible:s.visible.length,failed:s.failed,root:s.root});
  if(region==='thorax'){check('thorax rib and thoracic core',names(s).includes('Vertebra T12')&&names(s).includes('First rib')&&!names(s).some(n=>/^Vertebra [CL]/.test(n)),names(s));profiles.thorax={dataset:s,scene:await scene()};}
  if(region==='abdomen-lumbar'){check('lumbar core and attachment context',names(s).includes('Vertebra L5')&&names(s).includes('Hip bone')&&names(s).includes('Twelfth rib')&&names(s).includes('Femur')&&!names(s).some(n=>/^(Atlas|Axis|Vertebra C|Vertebra T(?:[1-9]|10|11))$/.test(n)),names(s));profiles.lumbar={dataset:s,scene:await scene()};}
  await shot('1440-region-'+region);
 }
 await page.locator('.region-grid button').nth(1).click();await page.locator('.region-grid button').nth(4).click({modifiers:['Shift']});await wait();check('explicit region union',new URL(page.url()).searchParams.get('regions')==='neck,thorax',page.url());await page.locator('.region-grid button').nth(5).click();await wait();
 await select('External abdominal oblique muscle');await button('선택 숨기기').click();await wait();const outer=(await state()).selected;
 await select('Internal abdominal oblique muscle');check('hidden outer muscle stays hidden under inner selection',!(await state()).visible.includes(outer),await state());
 await button('보기 복원').click();await wait();check('explicit restore restores outer muscle',(await state()).visible.includes(outer),await state());
 const content=JSON.parse(await readFile(resolve('../atlas-data/terminology/muscle-attachment-content-t90.json'),'utf8'));
 for(const entry of content.records){
  await select(entry.sourceName);
  for(const side of ['left','right']){
   await page.locator('.part-pills button').filter({hasText:side==='left'?'왼쪽':'오른쪽'}).click();await wait();
   const s=await state();const card=await page.locator('#study-tab-panel').innerText();
   check('attachment card '+entry.sourceName+' '+side,entry.sourceKeys.includes(s.selected)&&rows.find(r=>r.sourceKey===s.selected).side===side&&card.includes(entry.origin)&&card.includes(entry.insertion)&&!/(?:https?:\/\/|T90|single_source|not_performed)/.test(card),{selected:s.selected,side,text:card});
  }
 }
 }
 await page.getByRole('searchbox',{name:'구조 검색'}).fill('');await page.locator('.region-grid button').nth(5).click();await wait();await select('Psoas major');await page.locator('.part-pills button').filter({hasText:'왼쪽'}).click();await wait();await shot('1440-psoas-attachment-card');const muscle=(await state()).selected;
 await page.locator('[aria-label="정지 관련 뼈"] button').first().click();await wait();const contextBone=(await state()).selected;
 check('bone link preserves region/side/card',new URL(page.url()).searchParams.get('regions')==='abdomen-lumbar'&&rows.find(r=>r.sourceKey===contextBone).names.en==='Femur'&&rows.find(r=>r.sourceKey===contextBone).side==='left'&&await page.getByRole('heading',{name:'관련 근육',exact:true}).count()===1,{url:page.url(),bone:contextBone});
 await page.goBack();await wait();check('back restores attachment card in region',(await state()).selected===muscle&&new URL(page.url()).searchParams.get('regions')==='abdomen-lumbar',page.url());await page.goForward();await wait();check('forward retains context bone route',(await state()).selected===contextBone,await state());
 await page.getByRole('searchbox',{name:'구조 검색'}).fill('');await page.locator('.region-grid button').nth(9).click();await wait();await button('신경').click();await wait();await select('Deep fibular nerve');await button('선택 맞춤').click();await page.waitForTimeout(600);
 let s=await state();const nerve=s.selected,nerveRow=rows.find(r=>r.sourceKey===nerve);const camera=(await scene()).camera;
 check('native nerve visible in faded context with same-side motor target',s.observingNerves&&s.visible.includes(nerve)&&same(s.highlighted,nerveRow.nerve.muscleKeys),s);profiles.nerve={dataset:s,scene:await scene()};
 const img=await shot('1440-deep-observation');const canvasRect=await page.locator('.whole-body-canvas canvas').boundingBox();const {data,info}=await sharp(img).raw().toBuffer({resolveWithObject:true});
 const points=[];for(let y=Math.ceil(canvasRect.y+10);y<canvasRect.y+canvasRect.height-10;y++)for(let x=Math.ceil(canvasRect.x+10);x<canvasRect.x+canvasRect.width-10;x++){
  const i=(y*info.width+x)*info.channels,[r,g,b]=[data[i],data[i+1],data[i+2]];if(r>70&&r>g*1.7&&b>g*1.3&&g<105)points.push({x,y});
 }
 check('selected nerve has visible contrasting pixels',points.length>50,{pixels:points.length});
 await page.locator('.part-pills button').filter({hasText:'오른쪽'}).click();await wait();const point=points[Math.floor(points.length/2)];await page.mouse.click(point.x,point.y);await wait();check('actual native surface click passes through faded context',(await state()).selected===nerve,{point,selected:(await state()).selected});
 await button('주행 보기').click();await wait();s=await state();check('opaque depth context available without camera reset',!s.observingNerves&&same((await scene()).camera,camera),s);await shot('1440-deep-opaque');await button('되돌리기').click();await wait();check('undo restores nerve observation',(await state()).observingNerves,await state());
 await button('지배근 강조').click();await wait();check('motor highlight can be disabled and restored',!(await state()).highlighted.length&&await button('보기 복원').isEnabled(),await state());await button('보기 복원').click();await wait();check('restore includes motor emphasis',same((await state()).highlighted,nerveRow.nerve.muscleKeys),await state());
 await page.locator('.part-pills button').filter({hasText:'오른쪽'}).click();await wait();const right=await state();check('right selection and highlighted muscle stay right',rows.find(r=>r.sourceKey===right.selected).side==='right'&&right.highlighted.every(k=>rows.find(r=>r.sourceKey===k).side==='right'),right);await shot('1440-deep-right');
 await button('선택 숨기기').click();await wait();s=await state();check('hidden nerve removes highlight and fading',!s.visible.includes(s.selected)&&!s.highlighted.length&&!s.observingNerves,s);
 await page.locator('.part-pills button').filter({hasText:'왼쪽'}).click();await wait();check('other side selection preserves hidden right',!(await state()).visible.includes(s.selected),await state());
 await button('신경').click();await wait();await button('보기 복원').click();await wait();check('restore cannot turn on user-off nerve layer',!(await state()).nerveLayer&&!(await state()).highlighted.length&&!((await state()).observingNerves),await state());
 await button('신경').click();await wait();await button('뼈').click();await wait();await button('근육').click();await wait();const onlyNerves=await state();check('observation cannot resurrect layers',rows.filter(r=>r.kind!=='nerve').every(r=>!onlyNerves.visible.includes(r.sourceKey)),onlyNerves);await shot('1440-nerve-alone');
 await button('뼈').click();await button('근육').click();await wait();await select('Common fibular nerve');await page.locator('.nerve-card button').filter({hasText:'Superficial fibular nerve'}).click();await wait();await button('선택 맞춤').click();await page.waitForTimeout(500);const superficial=await state();check('branch card and unsupported motor extent stay distinct',rows.find(r=>r.sourceKey===superficial.selected).names.en==='Superficial fibular nerve'&&!superficial.highlighted.length,superficial);await shot('1440-superficial');
 await page.locator('.whole-body-canvas canvas').press('Home');await page.waitForTimeout(500);const home=await scene();await button('화면 맞춤').click();await page.waitForTimeout(500);check('keyboard Home frames current region',same(home.target,(await scene()).target),{home:home.camera,fit:(await scene()).camera});
 // Same decoded assets stay within the unchanged budget; warm layer toggles request no new resource.
 const requests=[];page.on('request',r=>{if(/\.glb/.test(r.url()))requests.push(r.url())});for(let i=0;i<3;i++){await button('신경').click();await wait();await button('신경').click();await wait()};const warm=await state();check('warm nerve toggles reuse cache',requests.length===0&&warm.bytes<=96*1024*1024&&warm.root===root&&warm.failed.length===0,{requests,bytes:warm.bytes,lateReleases:warm.lateReleases});
 for(const width of [1024,390]){
  await page.setViewportSize({width,height:width===390?844:900});await page.waitForTimeout(500);await shot(width+'-nerve-card');
  const layout=await page.evaluate(()=>{const rect=s=>{const r=document.querySelector(s).getBoundingClientRect();return{x:r.x,y:r.y,right:r.right,bottom:r.bottom,width:r.width,height:r.height}};return{document:document.documentElement.scrollWidth,canvas:rect('.whole-body-canvas'),tools:rect('.body-tools'),card:rect('.study-details'),info:rect('.app-info-trigger')}});
  const overlap=(a,b)=>Math.min(a.right,b.right)-Math.max(a.x,b.x)>1&&Math.min(a.bottom,b.bottom)-Math.max(a.y,b.y)>1;
  check(width+' responsive containment and small bottom-left attribution',layout.document<=width&&layout.canvas.height>=170&&!overlap(layout.canvas,layout.tools)&&!overlap(layout.canvas,layout.card)&&layout.info.x<=12&&layout.info.width<65&&layout.info.bottom>=(width===390?844:900)-10,layout);
  await button('앱 정보').click();check(width+' app attribution accessible',await page.locator('.app-info-dialog').isVisible(),true);await page.getByRole('button',{name:'앱 정보 닫기'}).click();
  if(width===390){await page.locator('.mobile-detail-summary').click();await page.waitForTimeout(300);await shot('390-card-collapsed');await page.locator('.mobile-detail-summary').click();await page.waitForTimeout(300)}
 }
 check('one renderer throughout changed flows',await page.locator('.whole-body-canvas canvas').count()===1&&(await state()).root===root,await state());check('no console errors',errors.length===0,errors);
}catch(e){errors.push(String(e));if(page)await shot('failure');throw e}
finally{await writeFile(resolve(out,'checks.json'),JSON.stringify({checks,captures,errors,profiles,resumedAfter:resume?'49 checks: 12 regions and 30 attachment cards; unchanged app inputs, automation search-clear correction':null,limitations:['390px desktop Chrome is not mobile hardware.','GPU/VRAM and total-process memory not measured.','Static native source pose only; principal attachment text and whole-bone context do not mark exact surface attachment points.']},null,2)+'\n');await browser.close()}
