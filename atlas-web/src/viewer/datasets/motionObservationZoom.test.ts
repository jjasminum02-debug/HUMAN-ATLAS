import test from 'node:test';
import assert from 'node:assert/strict';
import * as THREE from 'three';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
const read = (path: string) => JSON.parse(readFileSync(new URL('../../../../' + path, import.meta.url), 'utf8'));
test('trunk observation zoom increases actual projected displacement without changing source motion or angles', () => {
  const current = read('atlas-data/motion/motion-learning.json');
  const before = read('work/evidence/T66/priority-integration-2026-10-05/trunk-display-baseline.json');
  const rows = current.motionAssets.filter((a: {id: string}) => a.id.startsWith('T66-PRIORITY-S04-'));
  assert.equal(rows.length, 4);
  for (const row of rows) {
    const old = before.assets.find((a: {id: string}) => a.id === row.id);
    assert.equal(row.sha256, old.sha256);
    assert.equal(row.poseControl.endDegrees, 14);
    assert.equal(row.poseControl.observationZoom, 1.3);
    assert.deepEqual(row.sourceBinding, old.sourceBinding);
    assert.equal(createHash('sha256').update(readFileSync(new URL('../../../../' + row.uri, import.meta.url))).digest('hex'), old.sha256);
  }
  const camera = new THREE.PerspectiveCamera(35, 1.4, .005, 50);
  camera.position.set(.8, .2, 1.5); camera.lookAt(0, 0, 0); camera.updateMatrixWorld();
  const start = new THREE.Vector3(.04, .02, .01), end = new THREE.Vector3(.08, -.01, .02);
  // Screen displacement concerns x/y only: depth is not a screen coordinate.
  const a = start.clone().project(camera), b = end.clone().project(camera);
  const screenBefore = Math.hypot(a.x - b.x, a.y - b.y);
  camera.zoom = 1.3; camera.updateProjectionMatrix();
  const c = start.clone().project(camera), d = end.clone().project(camera);
  assert.ok(Math.abs(Math.hypot(c.x - d.x, c.y - d.y) / screenBefore - 1.3) < 1e-12);
});
