// Acupoint markers that stay readable at any zoom (2026-11-20): a fixed on-screen size, a white ring that
// separates the point from red muscle, a thick channel line, and a name tag on the chosen point.
import * as THREE from 'three';
import { Line2 } from 'three/examples/jsm/lines/Line2.js';
import { LineGeometry } from 'three/examples/jsm/lines/LineGeometry.js';
import { LineMaterial } from 'three/examples/jsm/lines/LineMaterial.js';

export const POINT_COLOR = '#e8590c', POINT_SELECTED = '#9a3412', LINE_COLOR = 0xe8590c;
/** On-screen diameters in CSS pixels. */
export const POINT_PX = 13, POINT_SELECTED_PX = 22;
/**
 * 4-3 V3: one style per overlay role (widths and dots in CSS pixels, so they read the same at any zoom).
 * Channel orange, sinew teal, landmarks purple; the chosen item is larger and darker (amber for landmarks and 結).
 */
export const OVERLAY = {
  channel: { line: 3, opacity: .85 },
  channelOther: { color: 0xa3aaa7, fill: '#a3aaa7', line: 1.5, opacity: .55, point: 7 },
  sinew: { color: 0x0f766e, line: 3.5, opacity: .9 },
  sinewCompanion: { color: 0x14b8a6, line: 2.5, opacity: .75 },
  knot: { fill: '#0f766e', px: 9 },
  binding: { fill: '#d39a2c', px: 15, companionPx: 11 },
  landmark: { fill: '#6d4fb3', px: 14, selected: '#d39a2c', selectedPx: 21 },
  measure: { color: 0x8b6fd0, line: 2, opacity: .9 },
} as const;

const textures = new Map<string, THREE.CanvasTexture>();
/** A filled dot with a white ring and a thin dark edge (reads on muscle, bone and skin alike). */
export function dotTexture(fill: string) {
  let t = textures.get(fill);
  if (!t) {
    const c = document.createElement('canvas'); c.width = c.height = 64;
    const g = c.getContext('2d')!;
    g.beginPath(); g.arc(32, 32, 30, 0, Math.PI * 2); g.fillStyle = 'rgba(20,20,20,.45)'; g.fill();
    g.beginPath(); g.arc(32, 32, 28, 0, Math.PI * 2); g.fillStyle = '#fff'; g.fill();
    g.beginPath(); g.arc(32, 32, 19, 0, Math.PI * 2); g.fillStyle = fill; g.fill();
    t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; textures.set(fill, t);
  }
  return t;
}

/** A diamond with the same white ring and dark edge as the dots (landmarks: bony points, not acupoints). */
export function diamondTexture(fill: string) {
  const key = `diamond:${fill}`;
  let t = textures.get(key);
  if (!t) {
    const c = document.createElement('canvas'); c.width = c.height = 64;
    const g = c.getContext('2d')!;
    const diamond = (r: number) => { g.beginPath(); g.moveTo(32, 32 - r); g.lineTo(32 + r, 32); g.lineTo(32, 32 + r); g.lineTo(32 - r, 32); g.closePath(); };
    diamond(31); g.fillStyle = 'rgba(20,20,20,.45)'; g.fill();
    diamond(29); g.fillStyle = '#fff'; g.fill();
    diamond(20); g.fillStyle = fill; g.fill();
    t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; textures.set(key, t);
  }
  return t;
}

const size = new THREE.Vector2();
/** Sprite scale that gives `px` CSS pixels of height for a sprite without size attenuation. */
function screenScale(renderer: THREE.WebGLRenderer, camera: THREE.Camera, px: number) {
  renderer.getSize(size);
  const p11 = (camera as THREE.PerspectiveCamera).projectionMatrix.elements[5] || 1;
  return 2 * px / (size.y * p11);
}

/** A sprite drawn at a fixed screen size (`userData.px`, height; width follows `userData.aspect`). */
export function screenSprite(map: THREE.Texture, px: number, aspect = 1) {
  const sprite = new THREE.Sprite(new THREE.SpriteMaterial({ map, depthTest: false, depthWrite: false, transparent: true, sizeAttenuation: false }));
  sprite.userData.px = px; sprite.userData.aspect = aspect;
  sprite.onBeforeRender = (renderer, _scene, camera) => {
    const s = screenScale(renderer, camera, sprite.userData.px);
    sprite.scale.set(s * sprite.userData.aspect, s, 1); sprite.updateMatrixWorld();
  };
  return sprite;
}

/** A name tag to the right of a point: white rounded box, dark text. */
export function labelSprite(text: string) {
  const c = document.createElement('canvas'), g = c.getContext('2d')!, font = '600 30px system-ui, -apple-system, sans-serif';
  g.font = font; const w = Math.ceil(g.measureText(text).width) + 28;
  c.width = w; c.height = 46;
  g.font = font; g.fillStyle = 'rgba(255,255,255,.94)'; g.strokeStyle = 'rgba(154,52,18,.55)'; g.lineWidth = 2;
  g.beginPath(); g.roundRect(1, 1, w - 2, 44, 10); g.fill(); g.stroke();
  g.fillStyle = '#7c2d12'; g.textBaseline = 'middle'; g.fillText(text, 14, 24);
  const map = new THREE.CanvasTexture(c); map.colorSpace = THREE.SRGBColorSpace;
  const sprite = screenSprite(map, 23, w / 46);
  sprite.center.set(-.16, .5); // starts just right of the point
  sprite.renderOrder = 13;
  return sprite;
}

/** A channel line a few pixels wide (WebGL lines are 1 px). Update with `setLinePoints`. */
export function wideLine(color: number, widthPx: number, opacity: number) {
  const material = new LineMaterial({ color, linewidth: widthPx, transparent: true, opacity, depthTest: false, depthWrite: false });
  const line = new Line2(new LineGeometry(), material);
  line.frustumCulled = false;
  line.onBeforeRender = renderer => { renderer.getSize(size); material.resolution.set(size.x, size.y); };
  return line;
}
export function setLinePoints(line: Line2, points: THREE.Vector3[]) {
  if (points.length < 2) { line.visible = false; return; }
  line.geometry.setPositions(points.flatMap(p => [p.x, p.y, p.z]));
  line.computeLineDistances();
}
