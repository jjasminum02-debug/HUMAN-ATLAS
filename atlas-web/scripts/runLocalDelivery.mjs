import { readFile, realpath } from 'node:fs/promises';
import { resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';
import { runLocalDelivery } from './localDeliveryServer.mjs';
const output=fileURLToPath(new URL('../dist-local/',import.meta.url));
try {
  const current=JSON.parse(await readFile(resolve(output,'CURRENT.json'),'utf8'));
  if(!/^[a-zA-Z0-9-]+$/.test(current.snapshotDirectory))throw Error('Invalid snapshot pointer.');
  const root=await realpath(output), snapshot=await realpath(resolve(root,current.snapshotDirectory));
  if(!snapshot.startsWith(root+sep))throw Error('Snapshot pointer escaped its output directory.');
  const sidecar=(await readFile(resolve(snapshot,'snapshot.sha256'),'utf8')).trim();
  if(sidecar!==current.manifestSha256)throw Error('Snapshot pointer/hash mismatch.');
  await runLocalDelivery(snapshot,process.argv.slice(2));
} catch(error) {console.error(error.message+'\nPrepare a validated snapshot with pnpm local:prepare.');process.exitCode=1;}
