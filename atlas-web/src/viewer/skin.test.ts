import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import * as THREE from 'three';
import { parseSkinChunk, posedCopy, skinGeometry, type SkinChunk } from './skin.ts';

const data = (path: string) => new URL(`../../../atlas-data/${path}`, import.meta.url);
const structures = JSON.parse(readFileSync(data('runtime/structures.json'), 'utf8')).structures as
  { id: string; names: { en: string }; side: string; layer: string | null; learner: { visible: boolean };
    geometry: { lods: Record<'overview' | 'detail', { resource: string; chunk: string; vertices: number }> } }[];
const chunks = new Map<string, SkinChunk>();
const weightsOf = (resource: string, chunk: string) => {
  if (!chunks.has(chunk)) { const bytes = readFileSync(data(`source-cache/datasets/za-v2/skin/${chunk}.bin`)); chunks.set(chunk, parseSkinChunk(bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength))); }
  return chunks.get(chunk)!.get(resource);
};
const soft = structures.filter(s => s.learner.visible && ['muscle', 'fascia', 'joint'].includes(s.layer ?? ''));
const roleShare = (en: string, side: string, role: string) => {
  const s = structures.find(x => x.names.en === en && x.side === side && x.learner.visible)!, lod = s.geometry.lods.overview;
  const w = weightsOf(lod.resource, lod.chunk)!, slot = w.roles.indexOf(role);
  let total = 0;
  for (const packed of w.data) total += ((packed >> 12) === slot ? (packed & 255) / 255 : 0) + (((packed >> 8) & 15) === slot && (packed >> 12) !== slot ? 1 - (packed & 255) / 255 : 0);
  return { share: total / w.data.length, roles: w.roles };
};

test('every visible soft-tissue mesh has weights matching its vertex count at both LODs', () => {
  for (const s of soft) for (const level of ['overview', 'detail'] as const) {
    const lod = s.geometry.lods[level], w = weightsOf(lod.resource, lod.chunk);
    assert.ok(w, `${s.id} ${level}`);
    assert.equal(w.data.length, lod.vertices, `${s.id} ${level}`);
    for (const packed of w.data) assert.ok((packed >> 12) < w.roles.length && ((packed >> 8) & 15) < w.roles.length, s.id);
  }
});

test('rest pose leaves the geometry unchanged', () => {
  const rest = new THREE.BufferGeometry();
  rest.setAttribute('position', new THREE.BufferAttribute(new Float32Array([0, 1, 2, 3, 4, 5]), 3));
  rest.setAttribute('normal', new THREE.BufferAttribute(new Float32Array([0, 0, 1, 1, 0, 0]), 3));
  const target = posedCopy(rest);
  skinGeometry(rest, new Uint16Array([0 << 12 | 1 << 8 | 128, 1 << 12 | 0 << 8 | 255]), [new THREE.Matrix4(), new THREE.Matrix4()], target);
  assert.deepEqual([...target.getAttribute('position').array], [0, 1, 2, 3, 4, 5]);
  assert.deepEqual([...target.getAttribute('normal').array], [0, 0, 1, 1, 0, 0]);
});

test('thigh muscle follows the femur; the ACL blends femur and tibia', () => {
  const vastus = roleShare('Vastus lateralis muscle', 'right', 'femur');
  assert.ok(vastus.share > .6, JSON.stringify(vastus));
  const acl = structures.find(s => s.names.en === 'Anterior cruciate ligament' && s.side === 'left' && s.learner.visible)!.geometry.lods.overview;
  const w = weightsOf(acl.resource, acl.chunk)!;
  assert.deepEqual(w.roles, ['femur', 'tibia']);
  assert.ok(roleShare('Anterior cruciate ligament', 'left', 'femur').share > .1 && roleShare('Anterior cruciate ligament', 'left', 'tibia').share > .1);
});

test('volume preservation: a shortened cylinder bulges at mid-belly by about sqrt(L0/L), ends stay, limits clamp', async () => {
  const { volumeProfile, preserveVolume } = await import('./skin.ts');
  const rings = 21, sides = 12, radius = .02, length = .3, points: number[] = [];
  for (let r = 0; r < rings; r++) for (let s = 0; s < sides; s++) {
    const a = s / sides * Math.PI * 2; points.push(Math.cos(a) * radius, r / (rings - 1) * length, Math.sin(a) * radius);
  }
  const rest = new Float32Array(points), profile = volumeProfile(rest)!;
  assert.ok(Math.abs(profile.restLength - length * .85) < .02, `rest length ${profile.restLength}`);
  const posed = (scale: number) => { const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(rest.map((v, i) => i % 3 === 1 ? v * scale : v), 3)); return g; };
  const ringRadius = (g: THREE.BufferGeometry, ring: number) => { const p = g.getAttribute('position').array; return Math.hypot(p[ring * sides * 3], p[ring * sides * 3 + 2]); };
  const short = posed(.8), k = preserveVolume(profile, short);
  assert.ok(Math.abs(k - Math.sqrt(1 / .8)) < .02, `k ${k}`);
  assert.ok(Math.abs(ringRadius(short, 10) - radius * k) < 1e-3, 'mid-belly radius');
  assert.ok(Math.abs(ringRadius(short, 0) - radius) < 1e-4 && Math.abs(ringRadius(short, rings - 1) - radius) < 1e-4, 'ends stay on their attachments');
  assert.ok(preserveVolume(profile, posed(1.15)) < 1, 'stretched muscle thins');
  assert.equal(preserveVolume(profile, posed(.3)), 1.25, 'clamped');
  assert.equal(preserveVolume(profile, posed(1)), 1, 'rest length: untouched');
});
