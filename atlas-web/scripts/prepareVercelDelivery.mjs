import { readFile, realpath } from 'node:fs/promises';
import { resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';
import { openLocalDelivery } from './localDeliveryServer.mjs';
import { buildVercelPackage, checkVercelPackage } from './vercelPackage.mjs';
const web=fileURLToPath(new URL('../',import.meta.url)),args=process.argv.slice(2);
if(args[0]==='--check'&&args.length===2){const result=await checkVercelPackage(resolve(args[1]));console.log(JSON.stringify({snapshotId:result.manifest.snapshotId,files:result.manifest.files.length,verified:true}));}
else{
 if(args.length!==4||args[0]!=='--asset-origin'||args[2]!=='--output')throw Error('Usage: --asset-origin HTTPS_OR_LOOPBACK_ORIGIN --output NEW_DIRECTORY | --check DIRECTORY');
 const pointer=JSON.parse(await readFile(resolve(web,'dist-local/CURRENT.json'),'utf8'));if(!/^[a-zA-Z0-9-]+$/.test(pointer.snapshotDirectory))throw Error('Invalid pointer');
 const localRoot=await realpath(resolve(web,'dist-local'));
 const snapshot=await realpath(resolve(localRoot,pointer.snapshotDirectory));if(!snapshot.startsWith(localRoot+sep))throw Error('Snapshot escaped local output');
 const app=await openLocalDelivery(snapshot);if(app.manifestSha256!==pointer.manifestSha256)throw Error('Stale pointer');
 const result=await buildVercelPackage(snapshot,app.manifest,resolve(args[3]),args[1]);console.log(JSON.stringify({snapshotId:result.snapshotId,frontendUploadBytes:result.uploadBytes,remoteBytes:result.remoteBytes,cliTargetMet:result.cliTargetMet,deployed:false},null,2));
}
