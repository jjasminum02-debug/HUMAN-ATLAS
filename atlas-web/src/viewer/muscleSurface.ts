import type * as THREE from 'three';

// Illustrative microrelief, not a measured fascicle direction or tendon boundary.
// Rest-space coordinates follow morph/skinned surfaces without UVs or extra buffers.
export function installMuscleSurface(material: THREE.MeshStandardMaterial) {
  material.customProgramCacheKey = () => 'atlas-muscle-microrelief-v1';
  material.onBeforeCompile = shader => {
    shader.vertexShader = shader.vertexShader
      .replace('#include <common>', '#include <common>\nvarying vec3 vAtlasMuscleRest;')
      .replace('#include <begin_vertex>', 'vAtlasMuscleRest = position;\n#include <begin_vertex>');
    shader.fragmentShader = shader.fragmentShader
      .replace('#include <common>', `#include <common>
varying vec3 vAtlasMuscleRest;
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
// Fade detail below pixel resolution to avoid distant shimmer and moire.
vec3 atlasGrainPosition = vAtlasMuscleRest * 800.0;
float atlasFootprint = max(length(dFdx(atlasGrainPosition)), length(dFdy(atlasGrainPosition)));
float atlasDetail = 1.0 - smoothstep(0.45, 1.4, atlasFootprint);
float atlasHeight = (atlasGrain(atlasGrainPosition) - 0.5) * atlasDetail;
diffuseColor.rgb *= 1.0 + atlasHeight * 0.10;
vec3 atlasDx = dFdx(-vViewPosition), atlasDy = dFdy(-vViewPosition);
vec3 atlasR1 = cross(atlasDy, normal), atlasR2 = cross(normal, atlasDx);
float atlasDet = dot(atlasDx, atlasR1);
vec3 atlasGradient = dFdx(atlasHeight) * atlasR1 + dFdy(atlasHeight) * atlasR2;
vec3 atlasNormal = abs(atlasDet) * normal - sign(atlasDet) * atlasGradient * 0.00012;
if (dot(atlasNormal, atlasNormal) > 1e-20) normal = normalize(atlasNormal);
`);
  };
}
