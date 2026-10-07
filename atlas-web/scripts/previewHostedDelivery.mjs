import { readFile, realpath } from 'node:fs/promises';
import { resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';
import { openHostedPreview } from './hostedPackage.mjs';
const web = fileURLToPath(new URL('../', import.meta.url));
let port = 5194;
const args = process.argv.slice(2);
if (args.length) {
  if (args.length !== 2 || args[0] !== '--port' || !Number.isInteger(Number(args[1])) || Number(args[1]) < 1024 || Number(args[1]) > 65535)
    throw Error('Usage: previewHostedDelivery.mjs [--port PORT]');
  port = Number(args[1]);
}
const pointer = JSON.parse(await readFile(resolve(web, 'dist-local/CURRENT.json'), 'utf8'));
if (!/^[a-zA-Z0-9-]+$/.test(pointer.snapshotDirectory)) throw Error('Invalid snapshot pointer');
const root = await realpath(resolve(web, 'dist-hosted'));
const directory = await realpath(resolve(root, pointer.snapshotDirectory));
if (!directory.startsWith(root + sep)) throw Error('Hosted directory escaped its root');
const { server } = await openHostedPreview(directory);
await new Promise((ok, fail) => { server.once('error', fail); server.listen(port, '127.0.0.1', ok); });
console.log('Exact hosted package preview: http://127.0.0.1:' + port + '/ (loopback only)');
for (const signal of ['SIGINT', 'SIGTERM']) process.once(signal, () => server.close());
