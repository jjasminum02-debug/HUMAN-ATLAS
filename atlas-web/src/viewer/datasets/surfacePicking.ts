import * as THREE from 'three';

/** A one-CSS-pixel picking tolerance for thin native nerve surfaces in transparent observation mode. */
export function pickSurface(camera: THREE.Camera, nodes: THREE.Mesh[], point: { x: number; y: number }, rect: { left: number; top: number; width: number; height: number }, observe: boolean) {
  const ray = new THREE.Raycaster();
  const intersect = (x: number, y: number, candidates = nodes) => {
    ray.setFromCamera(new THREE.Vector2((x - rect.left) / rect.width * 2 - 1, -(y - rect.top) / rect.height * 2 + 1), camera);
    return ray.intersectObjects(candidates, false);
  };
  const hits = intersect(point.x, point.y);
  if (!observe) return hits[0];
  const exact = hits.find(h => !h.object.userData.nerveObservationContext);
  if (exact) return exact;
  // Raster antialiasing can show a subpixel surface even when the pointer's central ray misses it.
  // Every candidate still intersects the original triangle surface; no centerline, enlarged mesh or name-based pick is invented.
  const nerves = nodes.filter(n => !n.userData.nerveObservationContext);
  for (const [dx, dy] of [[.5, .5], [-.5, -.5], [.5, -.5], [-.5, .5], [1, 0], [-1, 0], [0, 1], [0, -1]]) {
    const hit = intersect(point.x + dx, point.y + dy, nerves)[0];
    if (hit) return hit;
  }
  return hits[0];
}
