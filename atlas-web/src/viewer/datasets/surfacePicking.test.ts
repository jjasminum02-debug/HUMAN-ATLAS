import { test } from 'node:test';
import assert from 'node:assert/strict';
import * as THREE from 'three';
import { pickSurface } from './surfacePicking.ts';
test('transparent observation picks native subpixel surfaces within one pixel; normal depth picking and far misses still pick context', () => {
  const camera = new THREE.PerspectiveCamera(90, 1, .01, 10); camera.position.set(0, 0, 1); camera.updateMatrixWorld();
  const nerve = new THREE.Mesh(new THREE.BoxGeometry(.0003, .2, .001), new THREE.MeshBasicMaterial()); nerve.position.x = .003; nerve.updateMatrixWorld();
  const muscle = new THREE.Mesh(new THREE.BoxGeometry(.5, .5, .1), new THREE.MeshBasicMaterial()); muscle.position.z = .1; muscle.userData.nerveObservationContext = true; muscle.updateMatrixWorld();
  const rect = { left: 0, top: 0, width: 1000, height: 1000 };
  assert.equal(pickSurface(camera, [nerve, muscle], { x: 501, y: 500 }, rect, true)?.object, nerve);
  assert.equal(pickSurface(camera, [nerve, muscle], { x: 501, y: 500 }, rect, false)?.object, muscle);
  assert.equal(pickSurface(camera, [nerve, muscle], { x: 510, y: 500 }, rect, true)?.object, muscle);
  assert.equal(pickSurface(camera, [muscle], { x: 501, y: 500 }, rect, true)?.object, muscle);
  nerve.geometry.dispose(); muscle.geometry.dispose();
});
