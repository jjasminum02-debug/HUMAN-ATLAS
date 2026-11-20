import * as THREE from 'three';

// Illustrative microrelief, not a measured fascicle direction or tendon boundary.
// Rest-space coordinates follow morph/skinned surfaces without UVs or extra buffers.
// 4-3 U9: the grain is stretched along each muscle's long axis (its principal direction), so it reads as fibres.
// Fan-shaped and pennate muscles do not follow one axis; for them the streaks are only a texture.
export function installMuscleSurface(material: THREE.MeshStandardMaterial) {
  material.customProgramCacheKey = () => 'atlas-muscle-fibres-v2';
  material.onBeforeCompile = shader => {
    // A shared material cannot carry a per-mesh value, so the axis rides as a constant vertex attribute (3 bytes).
    shader.vertexShader = shader.vertexShader
      .replace('#include <common>', '#include <common>\nattribute vec3 fiberAxis;\nvarying vec3 vAtlasMuscleRest;\nvarying vec3 vAtlasFiberAxis;')
      .replace('#include <begin_vertex>', 'vAtlasMuscleRest = position;\nvAtlasFiberAxis = fiberAxis;\n#include <begin_vertex>');
    shader.fragmentShader = shader.fragmentShader
      .replace('#include <common>', `#include <common>
varying vec3 vAtlasMuscleRest;
varying vec3 vAtlasFiberAxis;
float atlasGrainHash(vec3 p) {
  p = fract(p * 0.1031);
  p += dot(p, p.yzx + 33.33);
  return fract((p.x + p.y) * p.z);
}
float atlasGrain(vec3 p) {
  vec3 cell = floor(p), f = fract(p);
  f = f * f * (3.0 - 2.0 * f);
  return mix(
    mix(mix(atlasGrainHash(cell), atlasGrainHash(cell + vec3(1,0,0)), f.x),
        mix(atlasGrainHash(cell + vec3(0,1,0)), atlasGrainHash(cell + vec3(1,1,0)), f.x), f.y),
    mix(mix(atlasGrainHash(cell + vec3(0,0,1)), atlasGrainHash(cell + vec3(1,0,1)), f.x),
        mix(atlasGrainHash(cell + vec3(0,1,1)), atlasGrainHash(cell + vec3(1,1,1)), f.x), f.y), f.z);
}`)
      .replace('#include <normal_fragment_maps>', `#include <normal_fragment_maps>
// Fibre frame: along the muscle's axis the noise is stretched 9x, across it the cells are about 1 mm.
vec3 atlasAxis = dot(vAtlasFiberAxis, vAtlasFiberAxis) > 0.01 ? normalize(vAtlasFiberAxis) : vec3(0.0, 1.0, 0.0);
vec3 atlasSide = normalize(cross(atlasAxis, abs(atlasAxis.y) < 0.9 ? vec3(0.0, 1.0, 0.0) : vec3(1.0, 0.0, 0.0)));
vec3 atlasUp = cross(atlasAxis, atlasSide);
vec3 atlasFibre = vec3(dot(vAtlasMuscleRest, atlasAxis) * 110.0, dot(vAtlasMuscleRest, atlasSide) * 1000.0, dot(vAtlasMuscleRest, atlasUp) * 1000.0);
// Fade detail below pixel resolution to avoid distant shimmer and moire.
float atlasFootprint = max(length(dFdx(atlasFibre.yz)), length(dFdy(atlasFibre.yz)));
float atlasDetail = 1.0 - smoothstep(0.45, 1.4, atlasFootprint);
float atlasHeight = (atlasGrain(atlasFibre) * 0.75 + atlasGrain(atlasFibre * vec3(2.0, 2.3, 2.3)) * 0.25 - 0.5) * atlasDetail;
diffuseColor.rgb *= 1.0 + atlasHeight * 0.16;
vec3 atlasDx = dFdx(-vViewPosition), atlasDy = dFdy(-vViewPosition);
vec3 atlasR1 = cross(atlasDy, normal), atlasR2 = cross(normal, atlasDx);
float atlasDet = dot(atlasDx, atlasR1);
vec3 atlasGradient = dFdx(atlasHeight) * atlasR1 + dFdy(atlasHeight) * atlasR2;
vec3 atlasNormal = abs(atlasDet) * normal - sign(atlasDet) * atlasGradient * 0.00016;
if (dot(atlasNormal, atlasNormal) > 1e-20) normal = normalize(atlasNormal);
`);
  };
}

/** A mesh's long axis in its own position space (principal component of sampled vertices). */
export function principalAxis(geometry: THREE.BufferGeometry): THREE.Vector3 {
  const p = geometry.getAttribute('position') as THREE.BufferAttribute | undefined;
  const axis = new THREE.Vector3(0, 1, 0);
  if (!p || p.count < 3) return axis;
  const stride = Math.max(1, Math.floor(p.count / 3000)), mean = new THREE.Vector3(), v = new THREE.Vector3();
  let n = 0;
  for (let i = 0; i < p.count; i += stride) { mean.add(v.fromBufferAttribute(p, i)); n++; }
  mean.divideScalar(n);
  let xx = 0, xy = 0, xz = 0, yy = 0, yz = 0, zz = 0;
  for (let i = 0; i < p.count; i += stride) {
    v.fromBufferAttribute(p, i).sub(mean);
    xx += v.x * v.x; xy += v.x * v.y; xz += v.x * v.z; yy += v.y * v.y; yz += v.y * v.z; zz += v.z * v.z;
  }
  // Power iteration on the 3x3 covariance, started off-axis so a y-aligned guess cannot stall.
  axis.set(.31, .87, .38).normalize();
  for (let k = 0; k < 32; k++) {
    const x = xx * axis.x + xy * axis.y + xz * axis.z, y = xy * axis.x + yy * axis.y + yz * axis.z, z = xz * axis.x + yz * axis.y + zz * axis.z;
    axis.set(x, y, z); const l = axis.length(); if (l < 1e-12) return new THREE.Vector3(0, 1, 0); axis.divideScalar(l);
  }
  return axis;
}

/** Give a muscle mesh its fibre axis as a constant `fiberAxis` attribute on its rest geometry (posed copies share it). */
export function attachFiberAxis(mesh: THREE.Mesh) {
  const current = mesh.geometry, rest = (current.userData.skinRest as THREE.BufferGeometry | undefined) ?? current;
  let attribute = rest.getAttribute('fiberAxis') as THREE.BufferAttribute | undefined;
  if (!attribute) {
    const axis = principalAxis(rest), count = rest.getAttribute('position').count, data = new Int8Array(count * 3);
    const x = Math.round(axis.x * 127), y = Math.round(axis.y * 127), z = Math.round(axis.z * 127);
    for (let i = 0; i < data.length; i += 3) { data[i] = x; data[i + 1] = y; data[i + 2] = z; }
    attribute = new THREE.BufferAttribute(data, 3, true);
    rest.setAttribute('fiberAxis', attribute);
  }
  if (current !== rest && current.getAttribute('fiberAxis') !== attribute) current.setAttribute('fiberAxis', attribute);
}
