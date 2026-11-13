// Cross-section view (ROADMAP Q2-2): one clipping plane on the anatomy renderer. App frame: x = subject left,
// y = up, z = anterior, metres. The kept half is the side where normal · p + constant >= 0 (three.js keeps it).
import * as THREE from 'three';

export type SectionAxis = 'axial' | 'sagittal' | 'coronal';
/** position: 0..1 across the body bounds on the axis; flip keeps the other half. */
export interface Section { axis: SectionAxis; position: number; flip: boolean }
export type Bounds = [number[], number[]];

const AXIS_INDEX: Record<SectionAxis, number> = { sagittal: 0, axial: 1, coronal: 2 };
export const SECTION_LABELS: Record<SectionAxis, { name: string; kept: [string, string] }> = {
  axial: { name: '가로면', kept: ['아래쪽', '위쪽'] },
  sagittal: { name: '시상면', kept: ['오른쪽', '왼쪽'] },
  coronal: { name: '관상면', kept: ['뒤쪽', '앞쪽'] },
};

/** Coordinate of the cut on its axis, in metres. */
export function sectionCoordinate(section: Section, bounds: Bounds) {
  const i = AXIS_INDEX[section.axis];
  return bounds[0][i] + Math.min(1, Math.max(0, section.position)) * (bounds[1][i] - bounds[0][i]);
}

/** Default keeps the lower, subject-right or posterior half (cut face toward the viewer's usual side); flip keeps the other. */
export function sectionPlane(section: Section, bounds: Bounds) {
  const i = AXIS_INDEX[section.axis], c = sectionCoordinate(section, bounds);
  const normal = new THREE.Vector3(); normal.setComponent(i, section.flip ? 1 : -1);
  return new THREE.Plane(normal, section.flip ? -c : c);
}

/** Camera direction from the plane toward the viewer: on the removed side, looking at the cut face. Axial views tilt
 * a little toward the front so the orbit controls keep a defined up direction. */
export function sectionViewDirection(plane: THREE.Plane) {
  const direction = plane.normal.clone().negate();
  if (Math.abs(direction.y) > .9) direction.add(new THREE.Vector3(0, 0, .45));
  return direction.normalize();
}

/** Points the user can pick: those on the kept side of the plane. */
export function keptBySection(plane: THREE.Plane | null, point: THREE.Vector3) {
  return !plane || plane.distanceToPoint(point) >= -1e-4;
}

/** Cut faces read as solid tissue: while the section turns materials double-sided, back faces seen through the cut
 * are filled with a flat, darker copy of the tissue colour instead of being lit as the inside wall. */
export function installSectionCap(material: THREE.Material) {
  const previous = material.onBeforeCompile;
  const previousKey = material.customProgramCacheKey.bind(material);
  material.onBeforeCompile = (shader, renderer) => {
    previous.call(material, shader, renderer);
    shader.fragmentShader = shader.fragmentShader.replace('#include <opaque_fragment>', `#include <opaque_fragment>
#ifdef DOUBLE_SIDED
if (!gl_FrontFacing) gl_FragColor.rgb = diffuseColor.rgb * 0.72;
#endif`);
  };
  material.customProgramCacheKey = () => `${previousKey()}|atlas-section-cap-v1`;
}
