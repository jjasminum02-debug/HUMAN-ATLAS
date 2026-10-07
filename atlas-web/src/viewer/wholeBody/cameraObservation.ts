import * as THREE from 'three';
export type ObservationDirection = 'front' | 'back' | 'left' | 'right';
export type CameraState = { position: number[]; target: number[]; zoom: number };
export const OBSERVATION_FRAME = 'HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR';
/** Canonical target frame is established by the source transform contract, not screen position. */
export function observationState(state: CameraState, direction: ObservationDirection, frame: string): CameraState {
  if (frame !== OBSERVATION_FRAME) throw new Error('Unsupported observation frame');
  const offset = new THREE.Vector3().fromArray(state.position).sub(new THREE.Vector3().fromArray(state.target));
  const radius = Math.hypot(offset.x, offset.z);
  const axes = { front: [0, 1], back: [0, -1], left: [1, 0], right: [-1, 0] };
  const [x, z] = axes[direction];
  return { ...state, target: [...state.target], position: [state.target[0] + x * radius, state.target[1] + offset.y, state.target[2] + z * radius] };
}
/** Interpolate on an orbit, so a 180-degree turn never travels through the anatomy. */
export function interpolateCamera(from: CameraState, to: CameraState, fraction: number): CameraState {
  const t = THREE.MathUtils.clamp(fraction, 0, 1), eased = t * t * (3 - 2 * t);
  const a = new THREE.Spherical().setFromVector3(new THREE.Vector3().fromArray(from.position).sub(new THREE.Vector3().fromArray(from.target)));
  const b = new THREE.Spherical().setFromVector3(new THREE.Vector3().fromArray(to.position).sub(new THREE.Vector3().fromArray(to.target)));
  const delta = Math.atan2(Math.sin(b.theta - a.theta), Math.cos(b.theta - a.theta));
  const target = new THREE.Vector3().fromArray(from.target).lerp(new THREE.Vector3().fromArray(to.target), eased);
  const offset = new THREE.Vector3().setFromSpherical(new THREE.Spherical(THREE.MathUtils.lerp(a.radius, b.radius, eased), THREE.MathUtils.lerp(a.phi, b.phi, eased), a.theta + delta * eased));
  return { target: target.toArray(), position: target.clone().add(offset).toArray(), zoom: THREE.MathUtils.lerp(from.zoom, to.zoom, eased) };
}
/** Fit all eight bounds corners in the current camera orientation, including side views. */
export function boundsCamera(box: THREE.Box3, state: CameraState, aspect: number, fov: number, padding: number): CameraState {
  const center = box.getCenter(new THREE.Vector3());
  const direction = new THREE.Vector3().fromArray(state.position).sub(new THREE.Vector3().fromArray(state.target)).normalize();
  if (direction.lengthSq() < .1) direction.set(0, 0, 1);
  const right = new THREE.Vector3().crossVectors(new THREE.Vector3(0, 1, 0), direction).normalize();
  if (right.lengthSq() < .1) right.set(1, 0, 0);
  const up = new THREE.Vector3().crossVectors(direction, right).normalize();
  const tan = Math.tan(THREE.MathUtils.degToRad(fov / 2));
  let distance = .06;
  for (const x of [box.min.x, box.max.x]) for (const y of [box.min.y, box.max.y]) for (const z of [box.min.z, box.max.z]) {
    const point = new THREE.Vector3(x, y, z).sub(center);
    distance = Math.max(distance, point.dot(direction) + padding * Math.max(Math.abs(point.dot(up)) / tan, Math.abs(point.dot(right)) / (tan * aspect)));
  }
  return { position: center.clone().addScaledVector(direction, distance).toArray(), target: center.toArray(), zoom: 1 };
}
