import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { type BodyAsset, type BodyManifest, type BodyView, visible, pickable } from './contract';
import { ResourceQueue } from './resources';

export interface BodyProgress { loaded: number; total: number; failed: number; contextLost: boolean; selectedAvailable: boolean; calls: number; triangles: number; geometries: number }
/** Sole owner of renderer, frame loop, camera, controls and the persistent anatomy root. */
export class AnatomySceneController {
  readonly scene = new THREE.Scene();
  readonly root = new THREE.Group();
  readonly camera = new THREE.PerspectiveCamera(35, 1, 0.005, 50);
  readonly renderer: THREE.WebGLRenderer;
  readonly controls: OrbitControls;
  readonly queue: ResourceQueue<THREE.Group>;
  readonly assets: Map<string, BodyAsset>;
  readonly updates = new Set<(seconds: number) => void>();
  private observer: ResizeObserver;
  private view: BodyView = { region: null, bones: true, muscles: true, supplements: false, selectedId: null, dim: true };
  private lost = false;
  private dead = false;
  private dirty = true;
  private previous = 0;
  private pointer = { x: 0, y: 0 };
  private lastReport = 0;
  private size = { width: 1, height: 1 };
  private manifest: BodyManifest;
  private notify: (progress: BodyProgress) => void;
  private select: (id: string, side: string | null) => void;
  private fetchAsset: typeof fetch;

  constructor(host: HTMLElement, manifest: BodyManifest, notify: (progress: BodyProgress) => void, select: (id: string, side: string | null) => void, fetchAsset: typeof fetch = (...args) => fetch(...args)) {
    this.manifest = manifest; this.notify = notify; this.select = select; this.fetchAsset = fetchAsset;
    this.assets = new Map(manifest.chunks.flatMap(c => c.assets.map(a => [a.nodeId, a] as const)));
    this.root.name = 'AnatomySceneRoot'; this.scene.add(this.root);
    this.scene.background = new THREE.Color('#eff1ef');
    this.scene.add(new THREE.HemisphereLight(0xffffff, 0xa4a79e, 2.1));
    const light = new THREE.DirectionalLight(0xffffff, 2.5); light.position.set(-2, 3, 4); this.scene.add(light);
    const rim = new THREE.DirectionalLight(0xd3e6e5, 1.2); rim.position.set(2, 1, -3); this.scene.add(rim);
    this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
    this.renderer.setPixelRatio(Math.min(devicePixelRatio, 1.75));
    this.renderer.outputColorSpace = THREE.SRGBColorSpace;
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 1.2;
    const canvas = this.renderer.domElement;
    canvas.id = `anatomy-${this.root.uuid}`;
    canvas.tabIndex = 0; canvas.setAttribute('aria-label', '해부학 모형. 방향키로 회전, 더하기와 빼기로 확대, Home으로 전체 보기');
    host.append(canvas);
    this.controls = new OrbitControls(this.camera, canvas);
    this.controls.enableDamping = true; this.controls.dampingFactor = 0.12;
    this.controls.minDistance = 0.06; this.controls.maxDistance = 8;
    this.controls.addEventListener('change', this.invalidate);
    // Fetch cancellation must reach both the network and the late parse guard.
    this.queue = new ResourceQueue((id, signal) => this.load(id, signal), group => this.release(group), () => this.sync());
    this.observer = new ResizeObserver(() => {
      const { width, height } = host.getBoundingClientRect();
      if (!width || !height) return;
      this.size = { width, height }; this.camera.aspect = width / height; this.camera.updateProjectionMatrix();
      this.renderer.setSize(width, height); this.dirty = true;
    });
    this.observer.observe(host);
    document.addEventListener('visibilitychange', this.invalidate);
    window.addEventListener('pageshow', this.invalidate);
    canvas.addEventListener('focus', this.invalidate);
    canvas.addEventListener('webglcontextlost', this.onLost);
    canvas.addEventListener('webglcontextrestored', this.onRestored);
    canvas.addEventListener('pointerdown', this.onDown);
    canvas.addEventListener('pointerup', this.onUp);
    canvas.addEventListener('keydown', this.onKey);
    this.focus(null);
    this.renderer.setAnimationLoop(this.frame);
  }

  private invalidate = () => { this.dirty = true; };
  /** Future pose controllers register updates here, never create a second RAF/renderer. */
  addUpdate(update: (seconds: number) => void) { this.updates.add(update); return () => { this.updates.delete(update); this.dirty = true; }; }
  private frame = (time: number) => {
    if (this.dead || this.lost) return;
    const dt = Math.min((time - this.previous) / 1000, 0.05); this.previous = time;
    for (const update of this.updates) update(dt);
    this.controls.update();
    if (this.dirty || this.updates.size) { this.renderer.render(this.scene, this.camera); this.dirty = false; }
    if (time - this.lastReport > 500) { this.report(); this.lastReport = time; }
  };
  setView(view: BodyView) {
    const regionChanged = view.region !== this.view.region;
    this.view = view; this.sync(); this.demand();
    if (regionChanged) this.focus(view.region);
  }
  private demand() {
    this.queue.demand(this.lost ? [] : this.manifest.chunks.filter(c => c.assets.some(a => visible(a, this.view))).map(c => c.id));
  }
  retry() { this.queue.retry(); this.demand(); }
  focus(region: string | null) {
    const box = new THREE.Box3();
    for (const a of this.assets.values()) if ((a.defaultVisible || (a.supplement && this.view.supplements)) && (!region || a.regions.includes(region))) {
      box.expandByPoint(new THREE.Vector3().fromArray(a.bounds[0])); box.expandByPoint(new THREE.Vector3().fromArray(a.bounds[1]));
    }
    if (box.isEmpty()) return;
    const center = box.getCenter(new THREE.Vector3()); const extent = box.getSize(new THREE.Vector3());
    const aspect = this.size.width / this.size.height;
    const distance = Math.max(extent.y, extent.x / aspect) / (2 * Math.tan(THREE.MathUtils.degToRad(17.5))) * 1.18 + extent.z / 2;
    this.controls.target.copy(center); this.camera.position.copy(center).add(new THREE.Vector3(0, 0, distance));
    this.controls.update(); this.dirty = true;
  }
  private async load(id: string, signal?: AbortSignal) {
    const chunk = this.manifest.chunks.find(c => c.id === id)!;
    const response = await this.fetchAsset(chunk.url, { signal }); if (!response.ok) throw new Error('Asset unavailable');
    const bytes = await response.arrayBuffer();
    const digest = Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256', bytes)), x => x.toString(16).padStart(2, '0')).join('');
    if (digest !== chunk.sha256) throw new Error('Hash mismatch');
    const doc = JSON.parse(new TextDecoder().decode(new Uint8Array(bytes, 20, new DataView(bytes).getUint32(12, true))));
    if (doc.buffers?.some((b: { uri?: string }) => b.uri) || doc.images?.length || doc.animations?.length || doc.skins?.length) throw new Error('Non-static source');
    const gltf = await new GLTFLoader().parseAsync(bytes, '');
    const group = gltf.scene;
    try {
      const found = new Set<string>();
      group.traverse(obj => {
        if (!(obj instanceof THREE.Mesh)) return;
        const a = chunk.assets.find(candidate => candidate.nodeId === obj.name);
        if (!a || found.has(obj.name) || obj.userData.sourceSha256 !== a.sourceSha256) throw new Error('Node identity mismatch');
        found.add(obj.name);
        const old = Array.isArray(obj.material) ? obj.material : [obj.material]; old.forEach(m => m.dispose());
        obj.material = new THREE.MeshStandardMaterial({ color: a.layer === 'bone' ? '#e2d9bb' : '#af7161', roughness: 0.68, metalness: 0 });
      });
      if (found.size !== chunk.assets.length) throw new Error('Missing scene nodes');
    } catch (error) { this.release(group); throw error; }
    return group;
  }
  private sync() {
    if (this.dead) return;
    for (const group of this.queue.loaded.values()) {
      if (!group.parent) this.root.add(group);
      group.traverse(obj => {
        if (!(obj instanceof THREE.Mesh)) return;
        const a = this.assets.get(obj.name)!;
        obj.visible = visible(a, this.view);
        const selected = pickable(a) && a.stableIds.some(id => (this.view.selectedIds ?? [this.view.selectedId]).includes(id));
        const material = obj.material as THREE.MeshStandardMaterial;
        material.color.set(selected ? '#3c9188' : a.layer === 'bone' ? '#e2d9bb' : '#af7161');
        // Opaque context avoids transparency sorting artifacts and excessive mobile overdraw.
        if (this.view.selectedId && this.view.dim && !selected) material.color.lerp(new THREE.Color('#e5e5dd'), 0.55);
      });
    }
    this.dirty = true; this.report();
  }
  private report() {
    if (this.dead) return;
    const wanted = [...this.queue.wanted];
    if (import.meta.env.DEV) this.renderer.domElement.dataset.scene = JSON.stringify({
      root: this.root.uuid, renderer: this.renderer.domElement.id, selectedId: this.view.selectedId,
      camera: this.camera.position.toArray(), target: this.controls.target.toArray(),
      loaded: [...this.queue.loaded.keys()], pending: [...this.queue.pending.keys()],
      visible: [...this.root.children].flatMap(g => g.children.filter(o => o.visible).map(o => o.name)),
      calls: this.renderer.info.render.calls, triangles: this.renderer.info.render.triangles,
      geometries: this.renderer.info.memory.geometries,
    });
    this.notify({ loaded: wanted.filter(id => this.queue.loaded.has(id)).length, total: wanted.length,
      failed: wanted.filter(id => this.queue.failed.has(id)).length, contextLost: this.lost,
      selectedAvailable: !this.view.selectedId || [...this.queue.loaded.values()].some(g => g.children.some(obj => obj.visible && this.assets.get(obj.name)?.stableIds.some(id => (this.view.selectedIds ?? [this.view.selectedId]).includes(id)))),
      calls: this.renderer.info.render.calls, triangles: this.renderer.info.render.triangles, geometries: this.renderer.info.memory.geometries });
  }
  private onLost = (event: Event) => { event.preventDefault(); this.lost = true; this.demand(); this.report(); };
  private onRestored = () => { this.lost = false; this.dirty = true; this.demand(); this.report(); };
  private onDown = (event: PointerEvent) => { this.pointer = { x: event.clientX, y: event.clientY }; };
  private onUp = (event: PointerEvent) => {
    if (Math.hypot(event.clientX - this.pointer.x, event.clientY - this.pointer.y) > 5 || event.button !== 0) return;
    const rect = this.renderer.domElement.getBoundingClientRect();
    const ray = new THREE.Raycaster();
    ray.setFromCamera(new THREE.Vector2((event.clientX - rect.left) / rect.width * 2 - 1, -(event.clientY - rect.top) / rect.height * 2 + 1), this.camera);
    const hit = ray.intersectObject(this.root, true).find(h => h.object.visible);
    const asset = hit && this.assets.get(hit.object.name);
    if (asset && pickable(asset)) this.select(asset.stableIds[0], asset.side);
  };
  private onKey = (event: KeyboardEvent) => {
    const offset = this.camera.position.clone().sub(this.controls.target);
    const spherical = new THREE.Spherical().setFromVector3(offset);
    switch (event.key) {
      case 'ArrowLeft': spherical.theta -= 0.12; break;
      case 'ArrowRight': spherical.theta += 0.12; break;
      case 'ArrowUp': spherical.phi -= 0.12; break;
      case 'ArrowDown': spherical.phi += 0.12; break;
      case '+': case '=': spherical.radius *= 0.9; break;
      case '-': spherical.radius *= 1.1; break;
      case 'Home': this.focus(this.view.region); event.preventDefault(); return;
      default: return;
    }
    event.preventDefault(); spherical.makeSafe(); spherical.radius = THREE.MathUtils.clamp(spherical.radius, 0.06, 8);
    this.camera.position.copy(this.controls.target).add(new THREE.Vector3().setFromSpherical(spherical)); this.controls.update(); this.dirty = true;
  };
  private release(group: THREE.Group) {
    group.removeFromParent(); group.traverse(obj => { if (obj instanceof THREE.Mesh) { obj.geometry.dispose(); (Array.isArray(obj.material) ? obj.material : [obj.material]).forEach(m => m.dispose()); } });
  }
  dispose() {
    this.dead = true; this.renderer.setAnimationLoop(null); this.queue.dispose(); this.updates.clear(); this.observer.disconnect();
    this.controls.dispose();
    const canvas = this.renderer.domElement;
    document.removeEventListener('visibilitychange', this.invalidate);
    window.removeEventListener('pageshow', this.invalidate);
    canvas.removeEventListener('focus', this.invalidate);
    canvas.removeEventListener('webglcontextlost', this.onLost); canvas.removeEventListener('webglcontextrestored', this.onRestored);
    canvas.removeEventListener('pointerdown', this.onDown); canvas.removeEventListener('pointerup', this.onUp); canvas.removeEventListener('keydown', this.onKey);
    this.renderer.dispose(); canvas.remove();
  }
}
