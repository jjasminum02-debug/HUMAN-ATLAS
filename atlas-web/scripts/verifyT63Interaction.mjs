import {createRequire} from 'node:module';
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {resolve} from 'node:path';
import * as THREE from 'three';
const require=createRequire('/Users/daniel/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/t63.cjs');
const {chromium}=require('playwright');
const out=resolve('../work/evidence/T63/interaction');await mkdir(out,{recursive:true});
const browser=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true});
const page=await browser.newPage({viewport:{width:1440,height:1000}});const checks=[],captures=[],errors=[];
page.on('pageerror',e=>errors.push(String(e)));page.on('console',m=>{if(m.type()==='error')errors.push(m.text())});
const check=(name,pass,detail)=>{checks.push({name,pass,detail});if(!pass)throw Error(name+': '+JSON.stringify(detail));};
const wait=async()=>{await page.waitForFunction(()=>{const c=document.querySelector('canvas');return c?.dataset.dataset&&JSON.parse(c.dataset.dataset).pending===0&&!document.querySelector('.whole-body-canvas').inert});await page.waitForTimeout(500);};
const state=()=>page.locator('canvas').evaluate(c=>({dataset:JSON.parse(c.dataset.dataset),scene:JSON.parse(c.dataset.scene)}));
const shot=async(name)=>{const b=await page.screenshot({path:resolve(out,name+'.png')});captures.push({path:'work/evidence/T63/interaction/'+name+'.png',sha256:createHash('sha256').update(b).digest('hex')});};
try{
 await page.goto('http://127.0.0.1:5183/?regions=leg');await wait();const root=(await state()).dataset.root;
 const runtime=await page.evaluate(async()=>await(await fetch('/__atlas/integration.json')).json());
 await page.getByRole('button',{name:'신경',exact:true}).click();await page.getByRole('button',{name:'뼈',exact:true}).click();await page.getByRole('button',{name:'근육',exact:true}).click();await wait();
 await page.getByRole('searchbox',{name:'구조 검색'}).fill('Common fibular nerve');const result=page.locator('.region-structure-list button').filter({hasText:'Common fibular nerve'}).first();await result.focus();await page.keyboard.press('Enter');await wait();
 const selected=(await state()).dataset.selected;check('keyboard search result opens typed nerve card',await page.locator('.nerve-card').count()===1&&Boolean(selected),selected);
 await page.getByRole('button',{name:'선택 맞춤',exact:true}).click();await page.waitForTimeout(600);await shot('keyboard-selected-common');
 await page.getByRole('button',{name:'선택 해제',exact:true}).click();await wait();
 const before=await state();const box=await page.locator('canvas').boundingBox();
 const assets=JSON.parse(await readFile('../atlas-data/manifests/nerve-scene-t63.json','utf8'));const object=assets.objects.find(o=>o.sourceKey===selected);
 const b=await readFile('../'+object.path);const size=b.readUInt32LE(12),doc=JSON.parse(b.subarray(20,20+size));const a=doc.accessors[0],v=doc.bufferViews[a.bufferView],bin=28+size+(v.byteOffset??0);
 const camera=new THREE.PerspectiveCamera(35,box.width/box.height,.005,50);camera.position.fromArray(before.scene.camera);camera.lookAt(new THREE.Vector3().fromArray(before.scene.target));camera.updateMatrixWorld();camera.updateProjectionMatrix();
 let clicked=null;
 for(let i=0;i<a.count;i++){
  const x=b.readFloatLE(bin+i*12),y=b.readFloatLE(bin+i*12+4),z=b.readFloatLE(bin+i*12+8);if(z<.48||z>.51)continue;
  const p=new THREE.Vector3(x,z,-y).project(camera);if(Math.abs(p.x)>.9||Math.abs(p.y)>.9)continue;
  await page.mouse.click(box.x+(p.x+1)*box.width/2,box.y+(1-p.y)*box.height/2);await page.waitForTimeout(100);
  if((await state()).dataset.selected===selected){clicked={x:box.x+(p.x+1)*box.width/2,y:box.y+(1-p.y)*box.height/2};break;}
 }
 check('real source-surface ray picking opens matching nerve card',Boolean(clicked)&&(await state()).dataset.selected===selected,{clicked,selected});
 await page.locator('canvas').focus();await page.keyboard.press('ArrowLeft');await page.waitForTimeout(650);
 const moved=await state();check('shared keyboard camera rotates nerve scene without reset',JSON.stringify(moved.scene.camera)!==JSON.stringify(before.scene.camera)&&moved.dataset.root===root,{before:before.scene.camera,after:moved.scene.camera});
 await page.getByRole('button',{name:'뼈',exact:true}).click();await page.getByRole('button',{name:'근육',exact:true}).click();await page.getByRole('button',{name:'선택 해제',exact:true}).click();
 await page.getByRole('searchbox',{name:'구조 검색'}).fill('');
 const nav=JSON.parse(await readFile('../atlas-data/navigation/atlas-navigation.json','utf8')).categories;
 for(const c of nav){
  await page.locator('.region-all-toggle').click();await page.getByRole('button',{name:c.labelKo,exact:true}).click();await wait();const s=await state();
  const expected=runtime.objects.filter(r=>r.localDisplayEligible&&r.defaultVisible&&r.kind!=='accessory'&&r.regionIds.includes(c.id)).map(r=>r.sourceKey);
  check('region '+c.id+' visible policy and same scene',expected.length===s.dataset.visible.length&&expected.every(key=>s.dataset.visible.includes(key))&&s.dataset.root===root,{expected:expected.length,visible:s.dataset.visible.length});
 }
 await page.locator('.region-all-toggle').click();await wait();await shot('whole-with-optional-nerve-layer');
 check('no UI errors',errors.length===0,errors);
}finally{await writeFile(resolve(out,'checks.json'),JSON.stringify({checks,captures,errors},null,2)+'\n');await browser.close();}
