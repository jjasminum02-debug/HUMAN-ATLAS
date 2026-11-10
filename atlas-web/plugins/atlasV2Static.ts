// Production output for the v2 runtime (ROADMAP 4-1, step 2): the same URLs the dev server answers, written as plain
// files into dist, with brotli siblings. Any static host that can serve `.br` files can serve this folder as it is.
import { createHash } from 'node:crypto';
import { createReadStream } from 'node:fs';
import { copyFile, mkdir, readFile, readdir, stat, writeFile } from 'node:fs/promises';
import type { IncomingMessage, ServerResponse } from 'node:http';
import { dirname, extname, resolve, sep } from 'node:path';
import { promisify } from 'node:util';
import { brotliCompress, constants } from 'node:zlib';
import { projectLegacyRuntime, type V2GeometryFile } from '../src/data/atlasV2.ts';

const compress = promisify(brotliCompress);
/** Learner JSON served as it is. structures.json and relations.json are only inputs to the two projected files. */
export const STATIC_JSON: Record<string, string> = { '/__atlas/v2/cards.json': 'structure-cards.json', '/__atlas/v2/rig.json': 'rig.json',
  '/__atlas/v2/actions.json': 'muscle-actions.json', '/__atlas/v2/attachments.json': 'attachments.json', '/__atlas/v2/muscle-cards.json': 'muscle-cards.json',
  '/__atlas/v2/vessel-branches.json': 'vessel-branches.json' };

export async function projectRuntime(root: string) {
  const runtime = resolve(root, 'atlas-data/runtime'), geometryDir = resolve(root, 'atlas-data/source-cache/datasets/za-v2');
  const [structures, relations, geometry] = await Promise.all([
    readFile(resolve(runtime, 'structures.json'), 'utf8'), readFile(resolve(runtime, 'relations.json'), 'utf8'),
    readFile(resolve(geometryDir, 'geometry.json'), 'utf8')]).then(texts => texts.map(text => JSON.parse(text)));
  const { dataset, integration } = projectLegacyRuntime(structures, relations, geometry);
  return { geometry: geometry as V2GeometryFile, manifest: Buffer.from(JSON.stringify(dataset)), integration: Buffer.from(JSON.stringify(integration)) };
}

async function put(outDir: string, url: string, bytes: Buffer) {
  const file = resolve(outDir, `.${url}`); await mkdir(dirname(file), { recursive: true }); await writeFile(file, bytes);
}

export async function writeStaticRuntime(root: string, outDir: string) {
  const runtime = resolve(root, 'atlas-data/runtime'), geometryDir = resolve(root, 'atlas-data/source-cache/datasets/za-v2');
  const { geometry, manifest, integration } = await projectRuntime(root);
  await put(outDir, '/__atlas/integration.json', integration);
  await put(outDir, '/__atlas/datasets/human-atlas-local/manifest.json', manifest);
  for (const [url, name] of Object.entries(STATIC_JSON)) await put(outDir, url, await readFile(resolve(runtime, name)));
  // The browser checks each chunk against this hash, so a stale cache must fail here rather than on a learner's screen.
  for (const chunk of geometry.chunks) {
    const bytes = await readFile(resolve(geometryDir, 'chunks', `${chunk.sha256}.glb`));
    if (createHash('sha256').update(bytes).digest('hex') !== chunk.sha256) throw Error(`Stale geometry chunk ${chunk.sha256}; rebuild the za-v2 dataset`);
    await put(outDir, `/__atlas/datasets/${chunk.namespace}/${chunk.id}.glb`, bytes);
  }
  for (const [folder, url] of [['skin', '/__atlas/v2/skin'], ['attachments', '/__atlas/v2/attachments']]) {
    await mkdir(resolve(outDir, `.${url}`), { recursive: true });
    for (const name of await readdir(resolve(geometryDir, folder))) await copyFile(resolve(geometryDir, folder, name), resolve(outDir, `.${url}/${name}`));
  }
}

const TEXT = new Set(['.js', '.css', '.html', '.json', '.svg']);
const BINARY = new Set(['.glb', '.bin']);
async function files(dir: string): Promise<string[]> {
  const out: string[] = [];
  for (const entry of await readdir(dir, { withFileTypes: true })) {
    const path = resolve(dir, entry.name);
    if (entry.isDirectory()) out.push(...await files(path)); else out.push(path);
  }
  return out;
}

/** Writes `<file>.br` next to every compressible file. Geometry uses a lower quality: quality 11 costs minutes for ~4% less. */
export async function precompress(outDir: string) {
  const targets = (await files(outDir)).filter(path => TEXT.has(extname(path)) || BINARY.has(extname(path)));
  let raw = 0, encoded = 0, next = 0;
  await Promise.all(Array.from({ length: 4 }, async () => {
    while (next < targets.length) {
      const path = targets[next++], bytes = await readFile(path);
      const br = await compress(bytes, { params: { [constants.BROTLI_PARAM_QUALITY]: TEXT.has(extname(path)) ? 11 : 9, [constants.BROTLI_PARAM_SIZE_HINT]: bytes.length } });
      raw += bytes.length;
      if (br.length < bytes.length * .95) { await writeFile(`${path}.br`, br); encoded += br.length; } else encoded += bytes.length;
    }
  }));
  return { files: targets.length, raw, encoded };
}

const TYPES: Record<string, string> = { '.js': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.glb': 'model/gltf-binary', '.bin': 'application/octet-stream', '.svg': 'image/svg+xml', '.webp': 'image/webp' };
const size = async (path: string) => stat(path).then(info => info.isFile() ? info.size : null, () => null);

/** Local stand-in for a static host: `.br` when the browser accepts it, a real 404 instead of the SPA page for missing data. */
export function staticRuntimeMiddleware(outDir: string) {
  const root = resolve(outDir);
  return async (req: IncomingMessage, res: ServerResponse, next: () => void) => {
    const path = decodeURIComponent((req.url ?? '').split('?')[0]);
    if (!/^\/(__atlas|assets|atlas-data)\//.test(path)) { next(); return; }
    const file = resolve(root, `.${path}`);
    const plain = file.startsWith(root + sep) ? await size(file) : null;
    if (plain === null) { res.statusCode = 404; res.end(); return; }
    const encoded = /\bbr\b/.test(String(req.headers['accept-encoding'] ?? '')) ? await size(`${file}.br`) : null;
    res.setHeader('Content-Type', TYPES[extname(file)] ?? 'application/octet-stream');
    res.setHeader('Vary', 'Accept-Encoding');
    res.setHeader('Cache-Control', path.startsWith('/assets/') || /\/[a-f0-9]{64}\.(glb|bin)$/.test(path) ? 'public, max-age=31536000, immutable' : 'no-cache');
    if (encoded !== null) res.setHeader('Content-Encoding', 'br');
    res.setHeader('Content-Length', String(encoded ?? plain));
    createReadStream(encoded !== null ? `${file}.br` : file).pipe(res);
  };
}
