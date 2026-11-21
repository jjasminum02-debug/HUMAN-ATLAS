// 4-3 U9: the fibre axis is the mesh's long direction.
import assert from 'node:assert/strict';
import test from 'node:test';
import * as THREE from 'three';
import { attachFiberAxis, principalAxis } from './muscleSurface.ts';

test('principal axis of a long box is its length', () => {
  const g = new THREE.BoxGeometry(.02, .02, .3, 2, 2, 12).rotateX(.4);
  const axis = principalAxis(g), expected = new THREE.Vector3(0, 0, 1).applyAxisAngle(new THREE.Vector3(1, 0, 0), .4);
  assert.ok(Math.abs(axis.dot(expected)) > .99, `${axis.toArray()}`);
});
test('the axis rides as one shared attribute on rest and posed copies', () => {
  const rest = new THREE.BoxGeometry(.3, .02, .02), posed = rest.clone(); posed.userData.skinRest = rest;
  const mesh = new THREE.Mesh(posed);
  attachFiberAxis(mesh);
  const a = rest.getAttribute('fiberAxis');
  assert.ok(a && posed.getAttribute('fiberAxis') === a && Math.abs(a.getX(0)) > .95);
});
