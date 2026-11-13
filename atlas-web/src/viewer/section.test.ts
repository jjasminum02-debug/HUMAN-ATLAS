import assert from 'node:assert/strict';
import test from 'node:test';
import * as THREE from 'three';
import { installSectionCap, keptBySection, sectionCoordinate, sectionPlane, sectionViewDirection, type Bounds } from './section.ts';
import { AnatomyMaterials } from './anatomyMaterials.ts';

const body: Bounds = [[-.4, 0, -.2], [.4, 1.8, .2]];
const p = (x: number, y: number, z: number) => new THREE.Vector3(x, y, z);

test('the default half is the lower, subject-right or posterior one; flip keeps the other', () => {
  const axial = sectionPlane({ axis: 'axial', position: .5, flip: false }, body);
  assert.ok(keptBySection(axial, p(0, .5, 0)) && !keptBySection(axial, p(0, 1.2, 0)));
  const up = sectionPlane({ axis: 'axial', position: .5, flip: true }, body);
  assert.ok(!keptBySection(up, p(0, .5, 0)) && keptBySection(up, p(0, 1.2, 0)));
  const sagittal = sectionPlane({ axis: 'sagittal', position: .5, flip: false }, body); // x = subject left
  assert.ok(keptBySection(sagittal, p(-.1, 1, 0)) && !keptBySection(sagittal, p(.1, 1, 0)));
  const coronal = sectionPlane({ axis: 'coronal', position: .5, flip: false }, body); // z = anterior
  assert.ok(keptBySection(coronal, p(0, 1, -.1)) && !keptBySection(coronal, p(0, 1, .1)));
  assert.equal(sectionCoordinate({ axis: 'axial', position: .25, flip: false }, body), .45);
  assert.equal(sectionCoordinate({ axis: 'axial', position: 2, flip: false }, body), 1.8);
  assert.ok(keptBySection(null, p(9, 9, 9)));
});

test('the camera looks at the cut face from the removed side', () => {
  for (const axis of ['axial', 'sagittal', 'coronal'] as const) for (const flip of [false, true]) {
    const plane = sectionPlane({ axis, position: .5, flip }, body), direction = sectionViewDirection(plane);
    assert.ok(plane.normal.dot(direction) < -.8, `${axis} ${flip}`);
    assert.ok(Math.abs(direction.y) < .95, 'orbit up stays defined');
  }
});

test('materials become double-sided while sectioned, with the cut-face shader; translucent ones stay front-sided', () => {
  const materials = new AnatomyMaterials();
  const muscle = materials.get('muscle'), fascia = materials.get('fascia');
  assert.equal(muscle.side, THREE.FrontSide);
  materials.setSectioned(true);
  assert.equal(muscle.side, THREE.DoubleSide); assert.equal(fascia.side, THREE.FrontSide);
  assert.equal(materials.get('bone').side, THREE.DoubleSide, 'materials created during a section');
  materials.setSectioned(false);
  assert.equal(muscle.side, THREE.FrontSide);
  const shader = { fragmentShader: '#include <opaque_fragment>\n', vertexShader: '#include <common>\n#include <begin_vertex>', uniforms: {} } as unknown as THREE.WebGLProgramParametersWithUniforms;
  muscle.onBeforeCompile(shader, {} as THREE.WebGLRenderer);
  assert.match(shader.fragmentShader, /gl_FrontFacing/);
  assert.match(muscle.customProgramCacheKey(), /atlas-muscle-microrelief-v1\|atlas-section-cap-v1/);
  const plain = new THREE.MeshStandardMaterial(); installSectionCap(plain);
  assert.match(plain.customProgramCacheKey(), /atlas-section-cap-v1$/);
});
