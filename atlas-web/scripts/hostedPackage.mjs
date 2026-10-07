import { readFile, writeFile, mkdir, realpath } from 'node:fs/promises';
import { resolve, dirname, sep } from 'node:path';
import { gzipSync, gunzipSync } from 'node:zlib';
import { createHash } from 'node:crypto';
import { createServer } from 'node:http';

const sha = bytes => createHash('sha256').update(bytes).digest('hex');
const categories = new Set(['app', 'anatomy', 'motion', 'projection']);
export const STATIC_ASSET_LIMIT = 25 * 1024 * 1024;
function filePath(root, path) {
  if (!/^public\//.test(path) || path.includes('\\') || path.split('/').some(part => !part || part === '.' || part === '..'))
    throw Error('Invalid public package path');
  return resolve(root, path);
}

/** Public transport derivative only; decoded GLB bytes, URLs, identities and original hashes stay exact. */
export async function buildHostedPackage(snapshotRoot, manifest, outputRoot) {
  if (manifest.authority?.sourceOnly !== true || manifest.authority?.publicRedistribution !== 'held'
    || manifest.authority?.humanReview !== 'not_performed') throw Error('Hosting cannot promote source authority');
  const sourceRoot = await realpath(snapshotRoot), files = [], urls = new Set();
  await mkdir(resolve(outputRoot, 'public'), { recursive: true });
  for (const row of manifest.files) {
    if (!categories.has(row.category) || row.path !== `public${row.url}` || !row.url.startsWith('/') || urls.has(row.url))
      throw Error('Invalid or repeated public asset');
    urls.add(row.url);
    const source = await realpath(filePath(sourceRoot, row.path));
    if (!source.startsWith(sourceRoot + sep + 'public' + sep)) throw Error('Public source escaped snapshot');
    const bytes = await readFile(source);
    if (bytes.length !== row.bytes || sha(bytes) !== row.sha256) throw Error('Public snapshot asset changed: ' + row.url);
    const encoding = row.url.endsWith('.glb') ? 'gzip' : 'identity';
    const payload = encoding === 'gzip' ? gzipSync(bytes, { level: 6, mtime: 0 }) : bytes;
    if (payload.length > STATIC_ASSET_LIMIT) throw Error('Static file exceeds 25 MiB: ' + row.url);
    if (encoding === 'gzip' && sha(gunzipSync(payload)) !== row.sha256) throw Error('Lossless transport verification failed');
    const target = filePath(outputRoot, row.path);
    await mkdir(dirname(target), { recursive: true });
    await writeFile(target, payload, { flag: 'wx' });
    files.push({ ...row, encoding, transportBytes: payload.length, transportSha256: sha(payload) });
  }
  const headers = '/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: no-referrer\n  X-Robots-Tag: noindex\n\n/\n  Cache-Control: no-cache\n\n/index.html\n  Cache-Control: no-cache\n\n/*.json\n  Cache-Control: public, max-age=0, must-revalidate\n\n/*.glb\n  Content-Type: model/gltf-binary\n  Content-Encoding: gzip\n  Cache-Control: public, max-age=0, must-revalidate\n\n/assets/*\n  Cache-Control: public, max-age=31536000, immutable\n';
  await writeFile(resolve(outputRoot, 'public/_headers'), headers, { flag: 'wx' });
  // A real 404 prevents Pages' default SPA fallback from presenting private/unknown URLs as the app.
  const notFound = '<!doctype html><html lang="ko"><meta charset="utf-8"><title>페이지 없음</title><p>이 주소에는 자료가 없습니다.</p><a href="/">HUMAN ATLAS로 돌아가기</a></html>';
  await writeFile(resolve(outputRoot, 'public/404.html'), notFound, { flag: 'wx' });
  const report = { schemaVersion: 'atlas-hosted-package-v1', snapshotId: manifest.snapshotId,
    deliveryBasis: manifest.deliveryBasis, authority: manifest.authority, requiresLogin: false,
    provider: 'Cloudflare Pages', viewerIndependentOfLaptop: true,
    decodedBytes: files.reduce((n, r) => n + r.bytes, 0), transportBytes: files.reduce((n, r) => n + r.transportBytes, 0),
    files, supportFiles: ['_headers', '404.html'], privateInputsUploaded: false, deployed: false };
  await writeFile(resolve(outputRoot, 'hosting-manifest.json'), JSON.stringify(report, null, 2) + '\n', { flag: 'wx' });
  return report;
}

/** Offline-origin QA of the exact upload directory and HTTP content decoding, not a cloud deployment claim. */
export async function openHostedPreview(outputRoot) {
  const root = await realpath(outputRoot);
  const manifest = JSON.parse(await readFile(resolve(root, 'hosting-manifest.json'), 'utf8'));
  const assets = new Map(manifest.files.map(row => [row.url, row]));
  for (const row of assets.values()) {
    const file = await realpath(filePath(root, row.path));
    if (!file.startsWith(root + sep + 'public' + sep)) throw Error('Hosted asset escaped public directory');
    const payload = await readFile(file);
    if (payload.length !== row.transportBytes || sha(payload) !== row.transportSha256) throw Error('Hosted bytes changed');
    const decoded = row.encoding === 'gzip' ? gunzipSync(payload) : payload;
    if (decoded.length !== row.bytes || sha(decoded) !== row.sha256) throw Error('Hosted original hash changed');
  }
  const server = createServer(async (req, res) => {
    try {
      const path = new URL(req.url ?? '/', 'http://localhost').pathname;
      const row = assets.get(path === '/' ? '/index.html' : path);
      if (!['GET', 'HEAD'].includes(req.method) || !row) { res.writeHead(404); res.end('Not found'); return; }
      const file = await realpath(filePath(root, row.path));
      if (!file.startsWith(root + sep + 'public' + sep)) throw Error('Hosted asset escaped public directory');
      const bytes = await readFile(file);
      if (sha(bytes) !== row.transportSha256) throw Error('Hosted asset changed');
      res.setHeader('Content-Type', row.contentType);
      res.setHeader('Content-Length', bytes.length);
      res.setHeader('Cache-Control', row.category === 'app' && path.startsWith('/assets/') ? 'public, max-age=31536000, immutable' : 'public, max-age=0, must-revalidate');
      res.setHeader('ETag', '"' + row.transportSha256 + '"');
      if (row.encoding === 'gzip') res.setHeader('Content-Encoding', 'gzip');
      if (req.headers['if-none-match'] === '"' + row.transportSha256 + '"') { res.writeHead(304); res.end(); return; }
      res.writeHead(200); res.end(req.method === 'HEAD' ? undefined : bytes);
    } catch { res.writeHead(503); res.end('Hosted package unavailable'); }
  });
  return { server, manifest };
}
