import {readFile,writeFile,mkdir,copyFile} from 'node:fs/promises';
import {resolve} from 'node:path';
import runtime from '../../../../atlas-web/src/data/learnerMotionRuntime.generated.ts';
const root=process.cwd(),e=resolve(root,'work/evidence/MV2/2026-10-12-q01-r1');
const signature=a=>JSON.stringify([a.staticBinding,a.clip,a.poseControl,a.sourceBinding]);
const rows=[],refs=[];
for(const side of ['left','right']){
 const r=JSON.parse(await readFile(resolve(e,side+'-candidate-r2/repair-record.json'),'utf8'));
 if(!Object.values(r.checks).every(c=>c.passed))throw Error('unaccepted geometry');
 const candidates=[];for(const collection of ['actions','wave1Actions'])for(const [selector,options] of Object.entries(runtime[collection]))for(const o of options)if(o.candidate?.asset.sha256===r.originalSha256){candidates.push(o.candidate);refs.push({collection,selector,id:o.actionKey??o.id,assetId:o.candidate.asset.id,side});}
 if(candidates.length!==1)throw Error('unexpected affected reference count');
 const a=candidates[0].asset, uri='atlas-data/assets/motion/mv2-q01-r1-'+side+'/motion.glb';await mkdir(resolve(root,uri,'..'),{recursive:true});await copyFile(resolve(e,side+'-candidate-r2/motion.glb'),resolve(root,uri));
 rows.push({assetId:a.id,baseUri:a.uri,baseSha256:a.sha256,bindingSignature:signature(a),uri,sha256:r.candidateSha256,revision:'mv2-rectus-native-endpoint-r1',bytes:r.bytesAfter});
}
const manifest={schemaVersion:'source-motion-repairs-v1',sourceOnly:true,publicRedistribution:'held',humanReview:'not_performed',rows};
await writeFile(resolve(root,'atlas-data/motion/source-motion-repairs-r1.json'),JSON.stringify(manifest,null,2)+'\n');await writeFile(resolve(e,'affected-runtime-references.json'),JSON.stringify(refs,null,2)+'\n');console.log(refs);
