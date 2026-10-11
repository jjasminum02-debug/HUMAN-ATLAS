import { readFile, writeFile, mkdir, rename } from 'node:fs/promises';
import { resolve, join } from 'node:path';
import { pathToFileURL } from 'node:url';
import { compilePlacementBatch, projectCompiledBatch, type CompilerInputs, type CompilerLedger, type PlacementUnit } from '../src/viewer/acupoints/anchorCompiler.ts';
import { sha256 } from '../src/viewer/acupoints/placementMigration.ts';
import type { AnchorContext } from '../src/viewer/acupoints/anchorAdapter.ts';

export interface RuleDocument {schemaVersion:2;context:AnchorContext;units:PlacementUnit[];inputs:CompilerInputs}
async function atomic(path:string,value:unknown) {
  const tmp=path+'.pending';await writeFile(tmp,JSON.stringify(value,null,2)+'\n');await rename(tmp,path);
}
/** Reusable offline entry. Raw input editions and failed attempts are immutable files, outside the learner bundle. */
export async function runAnchorCompiler(inputPath:string,outputDirectory:string,resume=false) {
  const path=resolve(inputPath),out=resolve(outputDirectory),bytes=await readFile(path),sourceSha256=await sha256(bytes);
  const doc=JSON.parse(bytes.toString('utf8')) as RuleDocument;
  if(doc.schemaVersion!==2||!Array.isArray(doc.units)||!doc.context||!doc.inputs)throw Error('Unsupported compiler input document');
  await mkdir(join(out,'inputs'),{recursive:true});
  const preserved=join(out,'inputs',sourceSha256+'.json');
  try {const existing=await readFile(preserved);if(await sha256(existing)!==sourceSha256)throw Error('Preserved original hash mismatch');}
  catch(error) {if((error as NodeJS.ErrnoException).code!=='ENOENT')throw error;await writeFile(preserved,bytes,{flag:'wx'});}
  let previous:CompilerLedger|undefined;
  if(resume)previous=JSON.parse(await readFile(join(out,'ledger.json'),'utf8')) as CompilerLedger;
  const result=await compilePlacementBatch(doc.units,doc.inputs,previous);
  const projection=await projectCompiledBatch(result.ledger,doc.inputs,{...doc.context,motionActive:false});
  await mkdir(join(out,'attempts'),{recursive:true});
  for(const attempt of result.history) {
    const hash=await sha256(new TextEncoder().encode(JSON.stringify(attempt)));
    const file=join(out,'attempts',hash+'.json');
    try {await writeFile(file,JSON.stringify(attempt,null,2)+'\n',{flag:'wx'});}catch(error){if((error as NodeJS.ErrnoException).code!=='EEXIST')throw error;}
  }
  await atomic(join(out,'ledger.json'),result.ledger);await atomic(join(out,'runtime-projection.json'),projection);
  const receipt={sourceSha256,originalPreserved:await sha256(await readFile(preserved))===sourceSha256,
    executed:result.executed,reused:result.reused,failed:Object.values(result.ledger.units).filter(u=>u.status==='failed').map(u=>({id:u.id,errors:u.errors})),
    localLearnerEligible:projection.reduce((n,p)=>n+p.instances.length,0),fixtureExports:projection.flatMap(p=>p.instances).filter(i=>i.code.startsWith('FIXTURE-')).length,
    runtimeBytes:Buffer.byteLength(JSON.stringify(projection,null,2)+'\n')};
  await atomic(join(out,'receipt.json'),receipt);return receipt;
}
if(process.argv[1]&&import.meta.url===pathToFileURL(resolve(process.argv[1])).href) {
  const args=process.argv.slice(2),input=args[args.indexOf('--input')+1],out=args[args.indexOf('--out')+1];
  if(!args.includes('--input')||!args.includes('--out')||!input||!out)throw Error('Usage: --input rules.json --out evidence-directory [--resume]');
  console.log(JSON.stringify(await runAnchorCompiler(input,out,args.includes('--resume'))));
}
