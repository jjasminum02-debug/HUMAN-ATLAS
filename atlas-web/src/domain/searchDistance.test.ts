import test from 'node:test';
import assert from 'node:assert/strict';
import { distance } from './search.ts';
// Independent full-matrix reference preserves insertion/deletion/substitution and transposition semantics.
function reference(a: string,b: string) {
  const d=Array.from({length:a.length+1},()=>Array(b.length+1).fill(0));
  for(let i=0;i<=a.length;i++) d[i][0]=i;
  for(let j=0;j<=b.length;j++) d[0][j]=j;
  for(let i=1;i<=a.length;i++) for(let j=1;j<=b.length;j++) {
    d[i][j]=Math.min(d[i-1][j]+1,d[i][j-1]+1,d[i-1][j-1]+Number(a[i-1]!==b[j-1]));
    if(i>1&&j>1&&a[i-1]===b[j-2]&&a[i-2]===b[j-1])d[i][j]=Math.min(d[i][j],d[i-2][j-2]+1);
  }
  return d[a.length][b.length];
}
test('rolling rows match full-matrix distance for all short repeated/transposed strings and anatomy terms',()=>{
  const words=['','splenius','spleinus','sternocleidomastoid','sternocledomastoid'];
  for(let length=1;length<=5;length++)for(let n=0;n<2**length;n++)words.push(n.toString(2).padStart(length,'0'));
  for(const a of words)for(const b of words)assert.equal(distance(a,b),reference(a,b),`${a}/${b}`);
});
