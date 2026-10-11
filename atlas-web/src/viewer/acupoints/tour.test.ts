import test from 'node:test';import assert from 'node:assert/strict';import { PointTour,LUNG_ORDER,sectionFor } from './tour.ts';
test('all eleven points advance in order with four section transitions and one finish',()=>{
 const selected:[number,boolean][]=[];let returned=0;const tour=new PointTour((i,focus)=>selected.push([i,focus]),()=>returned++,()=>{});
 tour.play();for(let i=0;i<11;i++)tour.tick(3.3);
 assert.deepEqual(selected.map(s=>s[0]),Array.from({length:11},(_,i)=>i));assert.deepEqual(selected.filter(s=>s[1]).map(s=>s[0]),[0,2,4,8]);assert.equal(returned,1);assert.equal(tour.state,'ready');assert.equal(LUNG_ORDER[8],'LU9');assert.equal(sectionFor('LU11'),3);
});
test('manual interaction pauses progress and prevents automatic return',()=>{
 let returned=0;const tour=new PointTour(()=>{},()=>returned++,()=>{});tour.play();tour.pause(true);tour.tick(40);assert.equal(tour.index,0);assert.equal(returned,0);assert.equal(tour.autoReturn,false);
});
test('previous next and resume have bounded indices and restart the dwell time',()=>{
 const tour=new PointTour(()=>{},()=>{},()=>{});tour.step(-1);assert.equal(tour.index,0);tour.choose(9);tour.play();tour.tick(3.3);assert.equal(tour.index,10);tour.step(1);assert.equal(tour.index,10);tour.play();assert.equal(tour.index,0);
});
