import test from 'node:test';
import assert from 'node:assert/strict';
import { CameraSessions } from './cameraSessions.ts';
const camera=(n:number)=>({position:[n,1,2],target:[n,0,0],zoom:1});
test('ending suspended anatomy cannot steal the acupoint camera return',()=>{
 const sessions=new CameraSessions();sessions.begin('anatomy',camera(1));sessions.begin('acupoint',camera(2));
 assert.equal(sessions.end('anatomy'),null);assert.equal(sessions.owner,'acupoint');assert.deepEqual(sessions.end('acupoint'),camera(2));
});
test('motion revokes the static guide; late guide release cannot move motion camera',()=>{
 const sessions=new CameraSessions();let revoked=0;sessions.begin('acupoint',camera(2),()=>{revoked++;sessions.end('acupoint',false);});sessions.begin('motion',camera(3));
 assert.equal(revoked,1);assert.equal(sessions.owner,'motion');assert.equal(sessions.end('acupoint'),null);assert.deepEqual(sessions.end('motion'),camera(3));
});
test('repeat begin keeps independent original return values and never aliases camera arrays',()=>{
 const sessions=new CameraSessions(),initial=camera(1);sessions.begin('anatomy',initial);initial.position[0]=99;
 assert.equal(sessions.begin('anatomy',camera(5)),false);assert.deepEqual(sessions.end('anatomy'),camera(1));
});
