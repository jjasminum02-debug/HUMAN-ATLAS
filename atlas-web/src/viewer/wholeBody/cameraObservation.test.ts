import { test } from 'node:test';
import assert from 'node:assert/strict';
import * as THREE from 'three';
import { boundsCamera, interpolateCamera, observationState, OBSERVATION_FRAME } from './cameraObservation.ts';
const state = { position: [2, 3, 4], target: [.2, 1, .3], zoom: 1.2 };
test('anatomical presets preserve orbit height, radius, target and zoom in the verified frame', () => {
  const offset = new THREE.Vector3().fromArray(state.position).sub(new THREE.Vector3().fromArray(state.target));
  for (const direction of ['front', 'back', 'left', 'right'] as const) {
    const next = observationState(state, direction, OBSERVATION_FRAME);
    assert.deepEqual(next.target, state.target); assert.equal(next.position[1], state.position[1]); assert.equal(next.zoom, state.zoom);
    assert.ok(Math.abs(new THREE.Vector3().fromArray(next.position).sub(new THREE.Vector3().fromArray(next.target)).length() - offset.length()) < 1e-12);
    if (direction === 'left') assert.ok(next.position[0] > next.target[0]);
    if (direction === 'right') assert.ok(next.position[0] < next.target[0]);
  }
  assert.throws(() => observationState(state, 'left', 'unverified'));
});
test('opposite-side transition keeps distance and never crosses the orbit target', () => {
  const a = observationState(state, 'front', OBSERVATION_FRAME), b = observationState(state, 'back', OBSERVATION_FRAME);
  const length = new THREE.Vector3().fromArray(a.position).sub(new THREE.Vector3().fromArray(a.target)).length();
  for (let i = 0; i <= 20; i++) {
    const sample = interpolateCamera(a, b, i / 20);
    assert.ok(Math.abs(new THREE.Vector3().fromArray(sample.position).sub(new THREE.Vector3().fromArray(sample.target)).length() - length) < 1e-10);
  }
});
test('common fit retains every corner in front and side view at narrow and wide aspects', () => {
  const box = new THREE.Box3(new THREE.Vector3(-.35, 0, -.22), new THREE.Vector3(.35, 1.8, .22));
  for (const aspect of [.48, 1, 2.2]) for (const direction of ['front', 'back', 'left', 'right'] as const) {
    const fitted = boundsCamera(box, observationState(state, direction, OBSERVATION_FRAME), aspect, 35, 1.25);
    const camera = new THREE.PerspectiveCamera(35, aspect, .005, 50);
    camera.position.fromArray(fitted.position); camera.lookAt(new THREE.Vector3().fromArray(fitted.target)); camera.updateMatrixWorld();
    for (const x of [box.min.x, box.max.x]) for (const y of [box.min.y, box.max.y]) for (const z of [box.min.z, box.max.z]) {
      const point = new THREE.Vector3(x, y, z).project(camera);
      assert.ok(Math.abs(point.x) <= 1 && Math.abs(point.y) <= 1 && point.z < 1);
    }
  }
});
