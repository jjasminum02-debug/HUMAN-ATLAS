import { readFile, mkdir, realpath } from 'node:fs/promises';
import { resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';
import { openLocalDelivery } from './localDeliveryServer.mjs';
import { buildHostedPackage } from './hostedPackage.mjs';

const web = fileURLToPath(new URL('../', import.meta.url));
if (process.argv.length > 2) throw Error('No arguments accepted; the validated CURRENT package is the input');
const pointer = JSON.parse(await readFile(resolve(web, 'dist-local/CURRENT.json'), 'utf8'));
if (!/^[a-zA-Z0-9-]+$/.test(pointer.snapshotDirectory)) throw Error('Invalid snapshot pointer');
const root = await realpath(resolve(web, 'dist-local'));
const snapshot = await realpath(resolve(root, pointer.snapshotDirectory));
if (!snapshot.startsWith(root + sep)) throw Error('Invalid snapshot containment');
const app = await openLocalDelivery(snapshot);
if (app.manifestSha256 !== pointer.manifestSha256) throw Error('Snapshot pointer hash differs');
const output = resolve(web, 'dist-hosted', pointer.snapshotDirectory);
await mkdir(resolve(web, 'dist-hosted'), { recursive: true });
await mkdir(output, { recursive: false });
const result = await buildHostedPackage(snapshot, app.manifest, output);
console.log(JSON.stringify({ publicDirectory: resolve(output, 'public'), fileCount: result.files.length,
  decodedBytes: result.decodedBytes, transportBytes: result.transportBytes,
  maxFileBytes: Math.max(...result.files.map(row => row.transportBytes)), deployed: false }, null, 2));
