import test from 'node:test';
import assert from 'node:assert/strict';
import { resolveAssetUrl, fetchAtlasAsset } from './assetTransport.ts';
const sha='a'.repeat(64), base='https://atlas.example/?source=one';
const config={revision:'fixture',urls:{'/motion.glb':`https://store.example/${sha}.glb`}};
test('exact logical URL only; no metadata rewrite, query loss or foreign origin hijack',()=>{
 assert.equal(resolveAssetUrl('/motion.glb',base,config),config.urls['/motion.glb']);
 for(const path of ['/manifest.json','/motion.glb?variant=2','https://other.example/motion.glb'])assert.equal(resolveAssetUrl(path,base,config),new URL(path,base).href);
 assert.equal(resolveAssetUrl('/motion.glb',base),new URL('/motion.glb',base).href);
});
test('immutable map rejects credentials, mutable paths and external insecure origins',()=>{
 for(const url of ['http://store.example/'+sha+'.glb','https://store.example/model.glb','https://user:pass@store.example/'+sha+'.glb','https://store.example/'+sha+'.glb?token=x'])assert.throws(()=>resolveAssetUrl('/motion.glb',base,{revision:'r',urls:{'/motion.glb':url}}));
 assert.equal(resolveAssetUrl('/motion.glb',base,{revision:'r',urls:{'/motion.glb':`http://127.0.0.1:5199/${sha}.glb`}}),`http://127.0.0.1:5199/${sha}.glb`);
});
test('fetch forwards abort signal; failed retry and late response handling stay with original owner',async()=>{
 const oldFetch=globalThis.fetch, oldWindow=(globalThis as any).window;
 const controller=new AbortController();let calls=0;
 (globalThis as any).window={location:{href:base},__ATLAS_ASSET_TRANSPORT__:config};
 globalThis.fetch=async(input,init)=>{calls++;assert.equal(input,config.urls['/motion.glb']);assert.equal(init?.signal,controller.signal);if(calls===1)return new Response('failure',{status:503});return new Response('retry');};
 try{assert.equal((await fetchAtlasAsset('/motion.glb',{signal:controller.signal})).status,503);assert.equal(await (await fetchAtlasAsset('/motion.glb',{signal:controller.signal})).text(),'retry');assert.equal(calls,2);}finally{globalThis.fetch=oldFetch;(globalThis as any).window=oldWindow;}
});
