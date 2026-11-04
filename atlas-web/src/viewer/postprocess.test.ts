import assert from 'node:assert/strict';
import test from 'node:test';
import * as THREE from 'three';
import { acesFilmic, preToneMapped } from './postprocess.ts';
import { AnatomyMaterials } from './anatomyMaterials.ts';

test('the pre-tone-mapped background lands back on the page colour after ACES', () => {
  const target = new THREE.Color('#eff1ef');
  const input = preToneMapped(target);
  const [r, g, b] = acesFilmic([input.r, input.g, input.b], 1);
  for (const [a, e] of [[r, target.r], [g, target.g], [b, target.b]]) assert.ok(Math.abs(a - e) < 2e-3, `${a} vs ${e}`);
});

test('fibrous tissue gets sheen, cartilage-like tissue a clearcoat, without textures or metalness', () => {
  const cache = new AnatomyMaterials();
  for (const tissue of ['joint', 'tendon', 'fascia'] as const) {
    const m = cache.get(tissue) as THREE.MeshPhysicalMaterial;
    assert.ok(m.isMeshPhysicalMaterial && m.sheen > 0, tissue);
    assert.equal(m.metalness, 0); assert.equal(m.map, null); assert.equal(m.depthWrite, !m.transparent);
  }
  assert.ok((cache.get('joint', { variant: 'meniscus' }) as THREE.MeshPhysicalMaterial).clearcoat > 0);
  assert.equal((cache.get('joint', { variant: 'ligament' }) as THREE.MeshPhysicalMaterial).clearcoat, 0);
  assert.ok(!(cache.get('bone') as THREE.MeshPhysicalMaterial).isMeshPhysicalMaterial);
  assert.notEqual(cache.get('joint').color.getHexString(), cache.get('bone').color.getHexString());
  cache.dispose();
});
