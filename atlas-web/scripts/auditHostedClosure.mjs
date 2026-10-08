import { readFile, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { createHash } from 'node:crypto';
import { gzipSync } from 'node:zlib';
import { performance } from 'node:perf_hooks';
import { checkVercelPackage } from './vercelPackage.mjs';

const sha = b => createHash('sha256').update(b).digest('hex');
const [snapshot, split, output] = process.argv.slice(2);
if (!output) throw Error('Usage: auditHostedClosure.mjs SNAPSHOT SPLIT OUTPUT.json');
const source = JSON.parse(await readFile(resolve(snapshot, 'snapshot.json'), 'utf8'));
const { manifest: packed } = await checkVercelPackage(split);
if (source.snapshotId !== packed.snapshotId) throw Error('Different snapshot');
const rows = [];
for (const row of source.files) {
  const derivative = packed.files.find(f => f.url === row.url);
  if (!derivative) throw Error('Omitted supported asset: ' + row.url);
  const original = await readFile(resolve(snapshot, row.path));
  const bytes = await readFile(resolve(split, derivative.path));
  if (row.category !== 'app' && !original.equals(bytes)) throw Error('Decoded identity changed');
  rows.push({ url: row.url, category: row.category, bytes: row.bytes, sha256: row.sha256,
    preservedBytes: original.equals(bytes), remote: derivative.remote });
}
const glbs = source.files.filter(r => r.url.endsWith('.glb'));
const largest = glbs.filter(r => r.category === 'motion').sort((a,b) => b.bytes-a.bytes)[0];
const raw = await readFile(resolve(snapshot, largest.path));
if (raw.readUInt32LE(0) !== 0x46546c67 || raw.readUInt32LE(8) !== raw.length) throw Error('GLB header');
const jsonSize = raw.readUInt32LE(12), doc = JSON.parse(raw.subarray(20, 20+jsonSize));
if (doc.extensionsRequired?.length || doc.buffers.length !== 1 || doc.buffers[0].uri) throw Error('Unsupported experiment');
const bin = raw.subarray(28+jsonSize), edited = structuredClone(doc), seen = new Map(), blocks = [];
let offset = 0, duplicateBytes = 0, zeros = 0, morphBytes = 0;
// Small transport-only experiment: share exact bufferView payloads, keeping accessor/node/track metadata.
const started = performance.now();
for (let i=0; i<doc.bufferViews.length; i++) {
  const view = doc.bufferViews[i], bytes = bin.subarray(view.byteOffset ?? 0, (view.byteOffset ?? 0)+view.byteLength);
  const key = sha(bytes), previous = seen.get(key);
  if (previous !== undefined) { edited.bufferViews[i].byteOffset = previous; duplicateBytes += bytes.length; }
  else {
    const padding = Buffer.alloc((4-offset%4)%4); blocks.push(padding); offset += padding.length;
    edited.bufferViews[i].byteOffset = offset; seen.set(key, offset); blocks.push(bytes); offset += bytes.length;
  }
}
edited.buffers[0].byteLength = offset;
let json = Buffer.from(JSON.stringify(edited)); json = Buffer.concat([json, Buffer.alloc((4-json.length%4)%4, 0x20)]);
let binary = Buffer.concat(blocks); binary = Buffer.concat([binary, Buffer.alloc((4-binary.length%4)%4)]);
const header = Buffer.alloc(20), bh = Buffer.alloc(8);
header.writeUInt32LE(0x46546c67); header.writeUInt32LE(2,4); header.writeUInt32LE(28+json.length+binary.length,8);
header.writeUInt32LE(json.length,12); header.writeUInt32LE(0x4e4f534a,16);
bh.writeUInt32LE(binary.length); bh.writeUInt32LE(0x004e4942,4);
const repacked = Buffer.concat([header,json,bh,binary]);
for (let i=0; i<doc.bufferViews.length; i++) {
  const v=doc.bufferViews[i], after=edited.bufferViews[i];
  if (!bin.subarray(v.byteOffset??0,(v.byteOffset??0)+v.byteLength).equals(binary.subarray(after.byteOffset,after.byteOffset+after.byteLength))) throw Error('Experiment changed a bufferView');
}
// All accessors and all transform/material/animation metadata are unchanged. No candidate is registered.
const clean = x => { const y=structuredClone(x); delete y.bufferViews; delete y.buffers; return y; };
if (JSON.stringify(clean(doc)) !== JSON.stringify(clean(edited))) throw Error('Experiment changed semantics');
for (const mesh of doc.meshes ?? []) for (const p of mesh.primitives) for (const t of p.targets ?? []) for (const id of Object.values(t)) {
  const a=doc.accessors[id],v=doc.bufferViews[a.bufferView];
  if (a.componentType===5126 && !v.byteStride && ['VEC3','SCALAR'].includes(a.type)) {
    const size=a.count*(a.type==='VEC3'?3:1), start=(v.byteOffset??0)+(a.byteOffset??0);
    morphBytes+=size*4; for(let j=0;j<size;j++) if(bin.readFloatLE(start+j*4)===0) zeros+=4;
  }
}
const beforeGzip=gzipSync(raw,{level:6}), afterGzip=gzipSync(repacked,{level:6});
const result = {
  snapshotId: source.snapshotId, sourceSnapshotSha256: sha(await readFile(resolve(snapshot,'snapshot.json'))),
  files: rows, closureFiles: rows.length, exactGLBs: glbs.length,
  publicAuthority: packed.authority, privateInputsUploaded: false, geometryModified: false,
  unchangedMeaning: 'All delivered GLB bytes are byte-identical; vertices, normals, topology, source/side/part/frame, materials, tracks, interpolation and contact/outcome inputs remain identical.',
  reusedGeometryQA: '../05-nerve-motion/nerve-motion-audit.json and unchanged emitted GLB key/mid/contact/outcome evidence',
  experiment: { source: largest.url, sourceSha256: largest.sha256, originalBytes:raw.length, repackedBytes:repacked.length,
    duplicateViewBytes:duplicateBytes, originalGzip6Bytes:beforeGzip.length, repackedGzip6Bytes:afterGzip.length,
    morphBytes, zeroMorphBytes:zeros, cpuMs:performance.now()-started, bufferViewsExact:true, nonBufferMetadataExact:true,
    applied:false, reason:'Sharing helps raw storage but does not show a path to the 90 MB whole upload target. Use split hosting and exact original GLBs; no sparse/raw-parser/mesh decoder migration required.' },
  limits: ['Node CPU only; no browser/GPU/VRAM/total-process memory benchmark', 'Experiment is not a registered revision or new anatomy approval'],
  errors: []
};
await writeFile(output,JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify({closureFiles:rows.length,exactGLBs:glbs.length,experiment:result.experiment},null,2));
