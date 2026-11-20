// 4-3 U8: screen-space name tags over the 3D view. Each tag points at its spot on the model with a leader line;
// a tag that cannot find free room around its spot is hidden rather than drawn over another one.
import * as THREE from 'three';

export type LabelKind = 'selected' | 'origin' | 'insertion' | 'hover';
export interface SceneLabel { id: string; text: string; sub?: string; kind: LabelKind; anchor: THREE.Vector3; priority: number }
type Rect = { x: number; y: number; w: number; h: number };

/** Leader offsets tried in order (screen px): right-up, left-up, right-down, left-down, straight up, straight down. */
const OFFSETS: [number, number][] = [[46, -30], [-46, -30], [46, 30], [-46, 30], [0, -52], [0, 52], [80, 0], [-80, 0]];
const overlaps = (a: Rect, b: Rect, pad = 4) => a.x < b.x + b.w + pad && b.x < a.x + a.w + pad && a.y < b.y + b.h + pad && b.y < a.y + a.h + pad;

/** Place tags greedily by priority; returns the chosen box per id (null = hidden). Pure, for tests. */
export function placeLabels(items: { id: string; at: { x: number; y: number } | null; w: number; h: number; leader: boolean }[], bounds: { w: number; h: number }) {
  const placed: Rect[] = [], out = new Map<string, (Rect & { ox: number; oy: number }) | null>();
  for (const item of items) {
    if (!item.at) { out.set(item.id, null); continue; }
    let chosen: (Rect & { ox: number; oy: number }) | null = null;
    for (const [dx, dy] of item.leader ? OFFSETS : [[14, -18] as [number, number]]) {
      const x = dx > 0 ? item.at.x + dx : dx < 0 ? item.at.x + dx - item.w : item.at.x - item.w / 2;
      const y = item.at.y + dy - item.h / 2;
      const r = { x, y, w: item.w, h: item.h };
      if (r.x < 2 || r.y < 2 || r.x + r.w > bounds.w - 2 || r.y + r.h > bounds.h - 2) continue;
      if (placed.some(p => overlaps(p, r))) continue;
      chosen = { ...r, ox: dx, oy: dy }; break;
    }
    if (chosen) placed.push(chosen);
    out.set(item.id, chosen);
  }
  return out;
}

export class LabelLayer {
  readonly root: HTMLDivElement;
  private readonly svg: SVGSVGElement;
  private labels: SceneLabel[] = [];
  private readonly nodes = new Map<string, { tag: HTMLDivElement; line: SVGLineElement; dot: SVGCircleElement }>();
  private readonly projected = new THREE.Vector3();

  constructor(host: HTMLElement) {
    this.root = document.createElement('div'); this.root.className = 'scene-labels'; this.root.setAttribute('aria-hidden', 'true');
    this.svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg'); this.svg.classList.add('scene-label-lines');
    this.root.append(this.svg); host.append(this.root);
  }

  set(labels: SceneLabel[]) {
    this.labels = [...labels].sort((a, b) => b.priority - a.priority);
    const ids = new Set(this.labels.map(l => l.id));
    for (const [id, n] of this.nodes) if (!ids.has(id)) { n.tag.remove(); n.line.remove(); n.dot.remove(); this.nodes.delete(id); }
    for (const l of this.labels) {
      let n = this.nodes.get(l.id);
      if (!n) {
        const tag = document.createElement('div'), line = document.createElementNS('http://www.w3.org/2000/svg', 'line'), dot = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        dot.setAttribute('r', '3.5');
        this.svg.append(line, dot); this.root.append(tag); n = { tag, line, dot }; this.nodes.set(l.id, n);
      }
      n.tag.className = `scene-label is-${l.kind}`;
      n.tag.dataset.label = l.id;
      n.tag.innerHTML = '';
      const name = document.createElement('b'); name.textContent = l.text; n.tag.append(name);
      if (l.sub) { const sub = document.createElement('small'); sub.textContent = l.sub; n.tag.append(sub); }
      n.line.setAttribute('class', `is-${l.kind}`); n.dot.setAttribute('class', `is-${l.kind}`);
    }
  }

  /** Re-project and re-place every tag; call after each drawn frame. */
  update(camera: THREE.Camera, width: number, height: number) {
    if (!this.labels.length) return;
    this.svg.setAttribute('width', String(width)); this.svg.setAttribute('height', String(height));
    const items = this.labels.map(l => {
      const n = this.nodes.get(l.id)!;
      this.projected.copy(l.anchor).project(camera);
      const visible = this.projected.z < 1 && Math.abs(this.projected.x) < 1.05 && Math.abs(this.projected.y) < 1.05;
      return { id: l.id, at: visible ? { x: (this.projected.x + 1) / 2 * width, y: (1 - this.projected.y) / 2 * height } : null,
        w: n.tag.offsetWidth || 80, h: n.tag.offsetHeight || 24, leader: l.kind !== 'hover' };
    });
    const boxes = placeLabels(items, { w: width, h: height });
    for (const item of items) {
      const n = this.nodes.get(item.id)!, box = boxes.get(item.id);
      const shown = Boolean(box && item.at);
      n.tag.style.visibility = shown ? 'visible' : 'hidden'; n.line.style.display = shown && item.leader ? '' : 'none'; n.dot.style.display = shown && item.leader ? '' : 'none';
      if (!box || !item.at) continue;
      n.tag.style.transform = `translate(${Math.round(box.x)}px, ${Math.round(box.y)}px)`;
      // The leader ends at the tag's nearest edge.
      const ex = box.ox > 0 ? box.x : box.ox < 0 ? box.x + box.w : box.x + box.w / 2, ey = box.ox === 0 ? (box.oy < 0 ? box.y + box.h : box.y) : box.y + box.h / 2;
      n.line.setAttribute('x1', String(item.at.x)); n.line.setAttribute('y1', String(item.at.y)); n.line.setAttribute('x2', String(ex)); n.line.setAttribute('y2', String(ey));
      n.dot.setAttribute('cx', String(item.at.x)); n.dot.setAttribute('cy', String(item.at.y));
    }
  }

  dispose() { this.root.remove(); this.nodes.clear(); }
}

/** World transform from the mesh's own matrix and its parent's world matrix: a mesh loaded this frame has not been drawn,
 * so its `matrixWorld` is still unset. */
export function worldOf(mesh: THREE.Object3D) {
  const local = mesh.matrixAutoUpdate ? mesh.matrix.compose(mesh.position, mesh.quaternion, mesh.scale) : mesh.matrix;
  return mesh.parent ? new THREE.Matrix4().multiplyMatrices(worldOf(mesh.parent), local) : local.clone();
}
/** A surface point near the middle of a mesh (the vertex closest to its centroid), in world space. */
export function surfaceMiddle(mesh: THREE.Mesh) {
  const p = mesh.geometry.getAttribute('position') as THREE.BufferAttribute | undefined; if (!p) return null;
  const stride = Math.max(1, Math.floor(p.count / 4000)), c = new THREE.Vector3(), v = new THREE.Vector3();
  let n = 0;
  for (let i = 0; i < p.count; i += stride) { c.add(v.fromBufferAttribute(p, i)); n++; }
  c.divideScalar(n || 1);
  let best = Infinity; const out = new THREE.Vector3();
  for (let i = 0; i < p.count; i += stride) { v.fromBufferAttribute(p, i); const d = v.distanceToSquared(c); if (d < best) { best = d; out.copy(v); } }
  return out.applyMatrix4(worldOf(mesh));
}

/** Where two meshes come closest (sampled), on the first mesh, in world space: a muscle's attachment on a bone. */
export function closestApproach(a: THREE.Mesh, b: THREE.Mesh, samples = 1500) {
  const pa = a.geometry.getAttribute('position') as THREE.BufferAttribute | undefined, pb = b.geometry.getAttribute('position') as THREE.BufferAttribute | undefined;
  if (!pa || !pb) return null;
  const sa = Math.max(1, Math.floor(pa.count / samples)), sb = Math.max(1, Math.floor(pb.count / samples));
  const bw: THREE.Vector3[] = [], wa = worldOf(a), wb = worldOf(b);
  for (let j = 0; j < pb.count; j += sb) bw.push(new THREE.Vector3().fromBufferAttribute(pb, j).applyMatrix4(wb));
  let best = Infinity; const out = new THREE.Vector3(), v = new THREE.Vector3();
  for (let i = 0; i < pa.count; i += sa) {
    v.fromBufferAttribute(pa, i).applyMatrix4(wa);
    for (const w of bw) { const d = v.distanceToSquared(w); if (d < best) { best = d; out.copy(v); } }
  }
  return best < Infinity ? out : null;
}
