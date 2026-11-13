/** DEV-only compositing/revision specimens; never in the learner data package. */
import type {TerritoryMask} from './schema.ts';
import {maskContentHash} from './territoryMask.ts';
export async function compositingFixtures(real:TerritoryMask[],variant:'overlap'|'revision') {
  const source=real.find(m=>m.side==='right')??real[0];if(!source)return [];
  const a=structuredClone(source),b=structuredClone(source);
  a.id='technical-overlap-A';b.id='technical-overlap-B';a.scope=b.scope='technical_fixture';
  a.channel='LU';b.channel='QA';a.revision=b.revision=variant==='revision'?'technical-revision-2':'technical-revision-1';
  // Two genuinely overlapping face sets; no new positions and no exclusive anatomy assignment.
  b.triangleIds=b.triangleIds.slice(Math.floor(b.triangleIds.length/3));
  a.vertexWeights=a.vertexWeights.map(([v,w])=>[v,variant==='revision'?w*.4:w]);
  a.contentSha256=await maskContentHash(a);b.contentSha256=await maskContentHash(b);return [a,b];
}
