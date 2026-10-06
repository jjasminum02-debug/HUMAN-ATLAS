import { createServer } from 'node:http';
import { createReadStream } from 'node:fs';
import { readFile, realpath, stat } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { resolve, sep, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const digest = bytes => createHash('sha256').update(bytes).digest('hex');
const authorityValid = value => value?.sourceOnly === true && value.publicRedistribution === 'held'
  && value.humanReview === 'not_performed' && value.canonicalTargetMembershipApproved === false;
const safePath = path => typeof path === 'string' && !path.startsWith('/') && !path.includes('\\')
  && !path.split('/').some(part => !part || part === '.' || part === '..');
export async function streamDigest(path) {
  const hash = createHash('sha256'); let bytes = 0;
  for await (const chunk of createReadStream(path)) { hash.update(chunk); bytes += chunk.length; }
  return { bytes, sha256: hash.digest('hex') };
}

/** A frozen, loopback-only delivery package; developer files are never URL-addressable. */
export async function openLocalDelivery(directory) {
  const root = await realpath(directory);
  const bytes = await readFile(resolve(root, 'snapshot.json'));
  const expected = (await readFile(resolve(root, 'snapshot.sha256'), 'utf8')).trim();
  if (digest(bytes) !== expected) throw Error('Snapshot manifest changed; verify or rebuild the local package.');
  const manifest = JSON.parse(bytes);
  if (manifest.schemaVersion !== 'human-atlas-local-delivery-v1' || !authorityValid(manifest.authority)
    || !Array.isArray(manifest.files) || !Array.isArray(manifest.privateInputs)) throw Error('Invalid local delivery contract.');
  async function contained(entry) {
    if (!safePath(entry.path) || !Number.isSafeInteger(entry.bytes) || entry.bytes < 0
      || !/^[a-f0-9]{64}$/.test(entry.sha256)) throw Error('Invalid snapshot entry.');
    const path = await realpath(resolve(root, entry.path));
    if (!path.startsWith(root + sep)) throw Error('Snapshot file escaped its package.');
    return path;
  }
  async function verify(entry) {
    const path = await contained(entry), actual = await streamDigest(path);
    if (actual.bytes !== entry.bytes || actual.sha256 !== entry.sha256) throw Error('Snapshot file is missing or changed: ' + entry.path);
    return path;
  }
  const entries = new Map();
  for (const entry of manifest.files) {
    if (typeof entry.url !== 'string' || !entry.url.startsWith('/') || entry.url.includes('..')
      || entry.url.startsWith('/.internal') || !entry.path.startsWith('public/') || entries.has(entry.url)) throw Error('Invalid public allowlist.');
    await verify(entry); entries.set(entry.url, entry);
  }
  if (!entries.has('/index.html') || !entries.has('/__atlas/integration.json')
    || !entries.has('/__atlas/datasets/human-atlas-local/manifest.json')) throw Error('Incomplete app snapshot.');
  const stamps = new Map();
  const fingerprint = async entry => { const s = await stat(await contained(entry)); return [s.dev,s.ino,s.size,s.mtimeMs,s.ctimeMs].join(':'); };
  for (const entry of manifest.privateInputs) {
    if (!entry.path.startsWith('.internal/')) throw Error('Private dependency must stay internal.');
    await verify(entry); stamps.set(entry.path, await fingerprint(entry));
  }
  const indexEntry = manifest.privateInputs.find(entry => entry.sourcePath === 'atlas-data/motion/local-motion-delivery-index.json');
  if (!indexEntry) throw Error('Missing motion delivery index.');
  const index = JSON.parse(await readFile(await contained(indexEntry), 'utf8'));
  if (index.schemaVersion !== 'local-motion-delivery-index-v1' || !authorityValid(index.authority)
    || index.dependencies?.length !== 2 || !Array.isArray(index.entries)) throw Error('Motion index authority changed.');
  for (const sourcePath of ['atlas-data/motion/motion-learning.json','atlas-data/motion/t66-wave1-registration.json']) {
    const dependency = index.dependencies.find(row => row.path === sourcePath);
    const input = manifest.privateInputs.find(row => row.sourcePath === sourcePath);
    if (!dependency || !input || input.bytes !== dependency.bytes || input.sha256 !== dependency.sha256) throw Error('Stale motion delivery inputs.');
  }
  for (const entry of index.entries) {
    const file = entries.get('/' + entry.uri);
    if (!file || file.category !== 'motion' || file.sha256 !== entry.sha256) throw Error('Missing registered motion asset.');
  }
  for (const entry of manifest.launcherFiles ?? []) await verify(entry);
  async function checkPrivateInputs() {
    for (const entry of manifest.privateInputs) {
      const current = await fingerprint(entry);
      if (current !== stamps.get(entry.path)) { await verify(entry); stamps.set(entry.path, current); }
    }
  }
  const server = createServer(async (req,res) => {
    res.setHeader('X-Content-Type-Options','nosniff');
    res.setHeader('Cross-Origin-Resource-Policy','same-origin');
    if (req.method !== 'GET' && req.method !== 'HEAD') { res.statusCode=405; res.end(); return; }
    let url;
    try {
      url=decodeURIComponent((req.url ?? '').split('?')[0]);
      if (!url.startsWith('/') || url.includes('\\') || /[\u0000-\u001f]/.test(url)
        || url.split('/').some(part => part === '..' || part === '.')) throw Error('Invalid URL');
    } catch { res.statusCode=404;res.end();return; }
    if (url === '/') url='/index.html';
    const entry=entries.get(url);
    if (!entry) {res.statusCode=404;res.end('Not in the validated local snapshot.');return;}
    try {
      await checkPrivateInputs();
      const path=await contained(entry), body=await readFile(path);
      // Current bytes are checked before either a cached response or body delivery.
      if (body.length !== entry.bytes || digest(body) !== entry.sha256) throw Error('Asset integrity changed');
      res.setHeader('Content-Type',entry.contentType);
      res.setHeader('Cache-Control',entry.category === 'projection' ? 'no-store' : 'private, no-cache');
      const etag='"'+entry.sha256+'"';res.setHeader('ETag',etag);
      if (req.headers['if-none-match'] === etag) {res.statusCode=304;res.end();return;}
      res.setHeader('Content-Length',body.length);res.end(req.method === 'HEAD' ? undefined : body);
    } catch {res.statusCode=503;res.end('Local snapshot integrity failed. Stop, verify, and rebuild the package.');}
  });
  return { manifest, manifestSha256: expected, server, verifiedFileCount: entries.size };
}

export async function runLocalDelivery(directory, args = []) {
  if (Number(process.versions.node.split('.')[0]) < 24) throw Error('Node.js 24 or newer is required.');
  let port=5180, verifyOnly=false;
  for(let i=0;i<args.length;i++) {
    if(args[i]==='--verify-only') verifyOnly=true;
    else if(args[i]==='--port') {port=Number(args[++i]);if(!Number.isInteger(port)||port<1024||port>65535)throw Error('Invalid loopback port.');}
    else throw Error('Unknown option: '+args[i]);
  }
  const delivery=await openLocalDelivery(directory);
  if(verifyOnly) {console.log(JSON.stringify({status:'verified',snapshotId:delivery.manifest.snapshotId,files:delivery.verifiedFileCount}));return;}
  await new Promise((ok,fail)=>{delivery.server.once('error',fail);delivery.server.listen(port,'127.0.0.1',ok);});
  console.log('HUMAN ATLAS local app: http://127.0.0.1:'+port+'/');
  for(const signal of ['SIGINT','SIGTERM'])process.once(signal,()=>delivery.server.close(()=>process.exit(0)));
  return delivery;
}
if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  runLocalDelivery(dirname(fileURLToPath(import.meta.url)),process.argv.slice(2)).catch(error=>{console.error(error.message);process.exitCode=1;});
}
