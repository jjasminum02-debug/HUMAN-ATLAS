import test from 'node:test';
import assert from 'node:assert/strict';
import * as THREE from 'three';
import { AnatomyMaterials, anatomyMaterialParameters, ANATOMY_PALETTE, type MaterialMode } from './anatomyMaterials.ts';

test('palette sharing and disposal are owned by the cache, not source mesh eviction', () => {
  const cache = new AnatomyMaterials();
  const shared = cache.get('muscle');
  assert.equal(cache.get('muscle'), shared);
  assert.equal(cache.get('muscle', {mode:'normal'}), shared);
  assert.notEqual(cache.get('bone'), shared);
  assert(cache.owns(shared)); assert(!cache.owns(new THREE.MeshStandardMaterial()));
  let disposed = 0; shared.addEventListener('dispose', () => disposed++);
  assert.equal(cache.size, 2); assert.equal(disposed, 0);
  cache.dispose(); assert.equal(disposed, 1); assert.equal(cache.size, 0);
  assert.notEqual(cache.get('muscle'), shared); cache.dispose();
});

test('all presentation and motion tones keep real depth and avoid textures or fake tendon partition', () => {
  const cache = new AnatomyMaterials();
  const modes: MaterialMode[] = ['normal','selected','dim','translucent','nerveContext','motorContext','innervated','observationContext','motionContext'];
  for (const tissue of ['bone','muscle','nerve','accessory','tendon'] as const) for (const mode of modes) for (const phase of [null,'action','return'] as const) {
    const m = cache.get(tissue,{mode,phase,contextOpacity:.25});
    assert.equal(m.depthTest, true); assert.equal(m.depthWrite, !m.transparent);
    assert.equal(m.map,null); assert.equal(m.normalMap,null); assert.equal(m.aoMap,null);
    assert.equal(m.metalness,0);
  }
  assert.equal(cache.get('muscle').color.getHexString(),new THREE.Color(ANATOMY_PALETTE.muscle).getHexString());
  assert.notEqual(cache.get('accessory').color.getHexString(),cache.get('tendon').color.getHexString());
  const normal = cache.get('nerve'), selected = cache.get('nerve',{mode:'selected'});
  // Yellow identity survives selection; luminance/specular response provide additional cues.
  assert(selected.emissiveIntensity > normal.emissiveIntensity);
  assert(selected.roughness < normal.roughness);
  assert(cache.get('nerve',{hovered:true}).emissiveIntensity > normal.emissiveIntensity);
  assert(cache.get('muscle',{hovered:true}).emissiveIntensity > cache.get('muscle').emissiveIntensity);
  assert.equal(cache.get('muscle',{mode:'translucent',phase:'action'}).opacity,.3);
  assert.equal(anatomyMaterialParameters('muscle',{mode:'motionContext',contextOpacity:2}).opacity,.6);
  cache.dispose();
});

test('muscle microrelief shares a program across states and follows rest coordinates through deformation', () => {
  const cache = new AnatomyMaterials();
  const modes: MaterialMode[] = ['normal', 'selected', 'translucent', 'innervated', 'motionContext'];
  const keys = new Set<string>();
  for (const mode of modes) for (const phase of [null, 'action', 'return'] as const) {
    const material = cache.get('muscle', { mode, phase });
    keys.add(material.customProgramCacheKey());
    const shader = {
      vertexShader: THREE.ShaderLib.standard.vertexShader,
      fragmentShader: THREE.ShaderLib.standard.fragmentShader,
      uniforms: {},
    };
    material.onBeforeCompile(shader as Parameters<typeof material.onBeforeCompile>[0], {} as THREE.WebGLRenderer);
    assert(shader.vertexShader.indexOf('vAtlasMuscleRest = position;') < shader.vertexShader.indexOf('#include <morphtarget_vertex>'));
    assert(shader.vertexShader.includes('#include <skinning_vertex>'));
    assert(shader.fragmentShader.includes('float atlasDetail = 1.0 - smoothstep'));
    assert(shader.fragmentShader.includes('dot(atlasNormal, atlasNormal) > 1e-20'));
    assert(!shader.fragmentShader.includes('sampler2D atlas'));
  }
  assert.equal(keys.size, 1);
  const boneShader = {vertexShader: THREE.ShaderLib.standard.vertexShader, fragmentShader: THREE.ShaderLib.standard.fragmentShader, uniforms: {}};
  const bone = cache.get('bone');
  bone.onBeforeCompile(boneShader as Parameters<typeof bone.onBeforeCompile>[0], {} as THREE.WebGLRenderer);
  assert.equal(boneShader.fragmentShader, THREE.ShaderLib.standard.fragmentShader);
  cache.dispose();
});
