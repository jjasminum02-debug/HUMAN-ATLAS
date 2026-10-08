import { readdir, readFile, lstat, realpath, writeFile } from 'node:fs/promises';
import { resolve, sep } from 'node:path';
import { createHash } from 'node:crypto';
import { gunzipSync } from 'node:zlib';
import { fileURLToPath } from 'node:url';
import { STATIC_ASSET_LIMIT } from './hostedPackage.mjs';

// Offline package audit using documented Pages wildcard/header semantics; not an edge test.
const web = fileURLToPath(new URL('../', import.meta.url));
const args = process.argv.slice(2);
if (args.length && (args.length !== 2 || args[0] !== '--report')) throw Error('Usage: checkCloudflarePackage.mjs [--report FILE]');
const pointer = JSON.parse(await readFile(resolve(web, 'dist-local/CURRENT.json'), 'utf8'));
if (!/^[a-zA-Z0-9-]+$/.test(pointer.snapshotDirectory)) throw Error('Unsafe snapshot pointer');
const root = await realpath(resolve(web, 'dist-hosted', pointer.snapshotDirectory));
const publicRoot = await realpath(resolve(root, 'public'));
if (!publicRoot.startsWith(root + sep)) throw Error('Public root escaped snapshot');
const manifest = JSON.parse(await readFile(resolve(root, 'hosting-manifest.json'), 'utf8'));
const sha = b => createHash('sha256').update(b).digest('hex');
const expected = new Set([...manifest.files.map(r => r.path.slice(7)), ...manifest.supportFiles]);
const paths = [];
async function walk(dir, prefix = '') {
  for (const name of await readdir(dir)) {
    const path = resolve(dir, name), stat = await lstat(path), relative = prefix + name;
    if (stat.isSymbolicLink()) throw Error('Symlink in upload: ' + relative);
    if (stat.isDirectory()) await walk(path, relative + '/');
    else if (stat.isFile()) paths.push({ path: relative, bytes: stat.size });
    else throw Error('Non-file in upload');
  }
}
await walk(publicRoot);
if (paths.length !== expected.size || paths.some(p => !expected.has(p.path))) throw Error('Upload differs from exact public allowlist');
if (!expected.has('404.html') || !expected.has('_headers')) throw Error('Missing 404 or header policy');
const text = await readFile(resolve(publicRoot, '_headers'), 'utf8'), rules = [];
let rule;
for (const line of text.split(/\r?\n/)) {
  if (!line.trim() || line.trim().startsWith('#')) continue;
  if (line.length > 2000) throw Error('Header line exceeds Pages limit');
  if (!/^\s/.test(line)) {
    if (!line.startsWith('/') || (line.match(/\*/g) ?? []).length > 1) throw Error('Unsupported header pattern');
    const pattern = line.replace(/[.+?^${}()|[\]\\]/g, '\\$&').replace('*', '.*');
    rule = { pattern: new RegExp('^' + pattern + '$'), headers: {} }; rules.push(rule);
  } else {
    const match = line.trim().match(/^([^:]+):\s*(.+)$/);
    if (!rule || !match) throw Error('Invalid header syntax');
    const key = match[1].toLowerCase();
    rule.headers[key] = rule.headers[key] ? rule.headers[key] + ', ' + match[2] : match[2];
  }
}
if (rules.length > 100) throw Error('Too many Pages header rules');
function headers(url) {
  const result = {};
  for (const r of rules) if (r.pattern.test(url)) for (const [key, value] of Object.entries(r.headers))
    result[key] = result[key] ? result[key] + ', ' + value : value;
  return result;
}
let decodedGlbs = 0;
for (const row of manifest.files) {
  if (row.path !== 'public' + row.url || !expected.has(row.path.slice(7))) throw Error('Invalid manifest asset path');
  const bytes = await readFile(resolve(root, row.path)), h = headers(row.url);
  if (bytes.length !== row.transportBytes || sha(bytes) !== row.transportSha256) throw Error('Transport hash mismatch');
  const decoded = row.encoding === 'gzip' ? gunzipSync(bytes) : bytes;
  if (decoded.length !== row.bytes || sha(decoded) !== row.sha256) throw Error('Decoded hash mismatch');
  if (row.url.endsWith('.glb')) {
    if (row.encoding !== 'gzip' || h['content-encoding'] !== 'gzip' || h['content-type'] !== 'model/gltf-binary') throw Error('Incorrect compressed GLB headers');
    decodedGlbs++;
  } else if (h['content-encoding']) throw Error('Unexpected compression header');
  if ((row.url.endsWith('.json') || row.url === '/index.html') && !/no-cache|must-revalidate/.test(h['cache-control'] ?? '')) throw Error('Stale mutable document policy');
  if (h['cache-control']?.includes('immutable') && !(row.category === 'app' && /-[\w-]+\.(js|css)$/.test(row.url))) throw Error('Immutable URL is not a hashed app asset');
}
const largest = paths.reduce((a, b) => a.bytes > b.bytes ? a : b);
if (largest.bytes > STATIC_ASSET_LIMIT || paths.length > 20000) throw Error('Pages Free package limit exceeded');
const report = { schemaVersion: 'atlas-cloudflare-audit-v1', snapshotId: manifest.snapshotId,
  publicDirectory: publicRoot, totalFiles: paths.length, runtimeFiles: manifest.files.length,
  uploadBytes: paths.reduce((n, p) => n + p.bytes, 0), largestFile: largest,
  decodedGlbs, exactAllowlist: true, decodedIntegrity: true, headerRules: rules.length,
  documentedHeaderMatching: 'passed', wranglerUploadFits: true, dashboardUploadFits: paths.length <= 1000,
  authority: manifest.authority, deliveryBasis: manifest.deliveryBasis,
  deployed: false, cloudflareEdgeVerified: false };
if (args.length) await writeFile(resolve(args[1]), JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify(report, null, 2));
