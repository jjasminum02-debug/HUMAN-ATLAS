import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { type BodyAsset, type BodyManifest, type BodyView, visible, pickable, selected } from './contract';
import { ResourceQueue } from './resources';
import { entranceFrame } from './sceneEntrance.ts';

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
  readonly updates = new Set<(seconds: number) => boolean | void>();
  private observer: ResizeObserver;
  private view: BodyView = { region: null, bones: true, muscles: true, supplements: false, selectedId: null, dim: true };
  private lost = false;
  private dead = false;
  private dirty = true;
  private previous = 0;
  private renderedFrames = 0;
  private entrance: { elapsed: number; target: THREE.Vector3; offset: THREE.Vector3 } | null = null;
  private readonly reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  private readonly frameIntervalsMs: number[] = [];
  private readonly renderDurationsMs: number[] = [];
  private pointer = { x: 0, y: 0 };
  private lastReport = 0;
  private hoverId: string | null = null;
  private hoverPoint: { x: number; y: number } | null = null;
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
    this.scene.add(new THREE.HemisphereLight(0xffffff, 0xa4a79e, 1.7));
    const light = new THREE.DirectionalLight(0xffffff, 2.0); light.position.set(-2, 3, 4); this.scene.add(light);
    const rim = new THREE.DirectionalLight(0xd3e6e5, 0.9); rim.position.set(2, 1, -3); this.scene.add(rim);
    this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
    this.renderer.setPixelRatio(Math.min(devicePixelRatio, 1.75));
    this.renderer.outputColorSpace = THREE.SRGBColorSpace;
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 1.05;
    const canvas = this.renderer.domElement;
    canvas.id = `anatomy-${this.root.uuid}`;
    canvas.tabIndex = 0; canvas.setAttribute('aria-label', '해부학 모형. 방향키로 회전, 더하기와 빼기로 확대, Home으로 전체 보기');
    host.append(canvas);
    this.controls = new OrbitControls(this.camera, canvas);
    this.controls.enableDamping = true; this.controls.dampingFactor = 0.12;
    this.controls.minDistance = 0.06; this.controls.maxDistance = 8;
    this.controls.addEventListener('change', this.invalidate);
    this.controls.addEventListener('start', this.stopEntrance);
    this.reducedMotion.addEventListener('change', this.stopEntrance);
    // Fetch cancellation must reach both the network and the late parse guard.
    this.queue = new ResourceQueue((id, signal) => this.load(id, signal), group => this.release(group), () => this.sync(), 2, {maxBytes:96*1024*1024,measure:group=>{
      const buffers=new Set<ArrayBufferLike>();
      group.traverse(o=>{if(o instanceof THREE.Mesh){for(const a of Object.values(o.geometry.attributes) as THREE.BufferAttribute[])buffers.add(a.array.buffer);if(o.geometry.index)buffers.add(o.geometry.index.array.buffer);}});
      return [...buffers].reduce((n,b)=>n+b.byteLength,0);
    }});
    const resize = () => {
      const { width, height } = host.getBoundingClientRect();
      if (!width || !height) return;
      this.size = { width, height }; this.camera.aspect = width / height; this.camera.updateProjectionMatrix();
      this.renderer.setSize(width, height); this.dirty = true;
    };
    resize(); // Measure the mounted host before the initial fit, not the old 1:1 placeholder.
    this.observer = new ResizeObserver(resize);
    this.observer.observe(host);
    document.addEventListener('visibilitychange', this.invalidate);
    window.addEventListener('pageshow', this.invalidate);
    canvas.addEventListener('focus', this.invalidate);
    canvas.addEventListener('webglcontextlost', this.onLost);
    canvas.addEventListener('webglcontextrestored', this.onRestored);
    canvas.addEventListener('pointermove', this.onMove);
    canvas.addEventListener('pointerleave', this.onLeave);
    canvas.addEventListener('pointerdown', this.onDown);
    canvas.addEventListener('pointerup', this.onUp);
    canvas.addEventListener('keydown', this.onKey);
    this.focus(null);
    this.renderer.setAnimationLoop(this.frame);
  }

  requestRender() { this.dirty = true; }
  /** One opening presentation on the existing frame clock; input always takes over. */
  startEntrance() {
    this.stopEntrance();
    if (this.reducedMotion.matches || this.dead || this.lost) return;
    this.entrance = { elapsed: 0, target: this.controls.target.clone(),
      offset: this.camera.position.clone().sub(this.controls.target) };
    this.renderer.domElement.style.opacity = String(entranceFrame(0).opacity);
    this.renderer.domElement.setAttribute('data-entrance', 'active');
    this.dirty = true;
  }
  stopEntrance = () => {
    this.entrance = null;
    this.renderer.domElement.style.opacity = '1';
    this.renderer.domElement.removeAttribute('data-entrance');
    this.dirty = true;
  };
  private updateEntrance(dt: number) {
    const entrance = this.entrance;
    if (!entrance) return false;
    entrance.elapsed += dt;
    const frame = entranceFrame(entrance.elapsed);
    const offset = entrance.offset.clone().applyAxisAngle(THREE.Object3D.DEFAULT_UP, frame.yaw);
    this.camera.position.copy(entrance.target).add(offset);
    this.renderer.domElement.style.opacity = String(frame.opacity);
    if (frame.finished) this.stopEntrance();
    return true;
  }
  private invalidate = () => { this.dirty = true; };
  /** Future pose controllers register updates here, never create a second RAF/renderer. */
  addUpdate(update: (seconds: number) => boolean | void) { this.updates.add(update); return () => { this.updates.delete(update); this.dirty = true; }; }
  private frame = (time: number) => {
    if (this.dead || this.lost) return;
    const intervalMs = this.previous ? time - this.previous : 0;
    if (import.meta.env.DEV && intervalMs > 0) {
      this.frameIntervalsMs.push(intervalMs);
      if (this.frameIntervalsMs.length > 240) this.frameIntervalsMs.shift();
    }
    const dt = Math.min(intervalMs / 1000, 0.05); this.previous = time;
    let poseChanged = false;
    // false means an idle player; legacy callbacks without a return still render.
    for (const update of this.updates) if (update(dt) !== false) poseChanged = true;
    // A real pose update owns framing; the opening orbit must not fight playback.
    if (poseChanged && this.entrance) this.stopEntrance();
    const entranceChanged = this.updateEntrance(dt);
    this.controls.update();
    if (this.hoverPoint) { const p = this.hoverPoint; this.hoverPoint = null; this.setHover(this.pick(p.x, p.y)?.nodeId ?? null); }
    if (this.dirty || poseChanged || entranceChanged) {
      const started = import.meta.env.DEV ? performance.now() : 0;
      this.renderer.render(this.scene, this.camera); this.dirty = false; this.renderedFrames += 1;
      if (import.meta.env.DEV) {
        this.renderDurationsMs.push(performance.now() - started);
        if (this.renderDurationsMs.length > 240) this.renderDurationsMs.shift();
      }
    }
    if (time - this.lastReport > 500) { this.report(); this.lastReport = time; }
  };
  setView(view: BodyView) {
    this.view = { ...view, ...(view.regionIds ? { regionIds: [...view.regionIds] } : {}) };
    this.sync(); this.demand();
  }
  private demand() {
    this.queue.demand(this.lost ? [] : this.manifest.chunks.filter(c => c.assets.some(a => visible(a, this.view))).map(c => c.id));
  }
  retry() { this.queue.retry(); this.demand(); }
  focus(regionIds: readonly string[] | string | null = []) {
    const selectedRegions = typeof regionIds === 'string' ? [regionIds] : regionIds ?? [];
    const box = new THREE.Box3();
    for (const a of this.assets.values()) if ((a.defaultVisible || (a.supplement && this.view.supplements))
      && (selectedRegions.length === 0 || selectedRegions.some((regionId) => a.regions.includes(regionId)))) {
      box.expandByPoint(new THREE.Vector3().fromArray(a.bounds[0])); box.expandByPoint(new THREE.Vector3().fromArray(a.bounds[1]));
    }
    this.fitBounds(box);
  }
  /** Explicit user framing command; never invoked by a pick or panel change. */
  focusSelection() {
    const box = new THREE.Box3();
    for (const a of this.assets.values()) if (visible(a, this.view) && selected(a, this.view)) {
      box.expandByPoint(new THREE.Vector3().fromArray(a.bounds[0]));
      box.expandByPoint(new THREE.Vector3().fromArray(a.bounds[1]));
    }
    this.fitBounds(box);
  }
  private fitBounds(box: THREE.Box3) {
    this.stopEntrance();
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
        obj.material = new THREE.MeshStandardMaterial({ color: a.layer === 'bone' ? '#e7dec7' : '#b87969', roughness: 0.76, metalness: 0 });
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
        const isSelected = selected(a, this.view);
        const material = obj.material as THREE.MeshStandardMaterial;
        material.color.set(isSelected ? '#398b80' : a.layer === 'bone' ? '#e7dec7' : '#b87969');
        material.emissive.set(a.nodeId === this.hoverId && !isSelected ? '#68897e' : '#000000');
        material.emissiveIntensity = 0.22;
        const translucentSelection = isSelected && this.view.selectedPresentation === 'translucent' || Boolean(this.view.translucentSourceKeys?.some(key => key === a.id || key === a.nodeId || a.stableIds.includes(key)));
        if (material.transparent !== translucentSelection || material.depthWrite === translucentSelection) material.needsUpdate = true;
        material.transparent = translucentSelection;
        material.opacity = translucentSelection ? 0.28 : 1;
        material.depthWrite = !translucentSelection;
        // Opaque context avoids transparency sorting artifacts and excessive mobile overdraw.
        if (this.view.selectedId && this.view.dim && !isSelected) material.color.lerp(new THREE.Color('#e5e5dd'), 0.38);
      });
    }
    this.dirty = true; this.report();
  }
  private report() {
    if (this.dead) return;
    const wanted = [...this.queue.wanted];
    if (import.meta.env.DEV) {
      const intervals = [...this.frameIntervalsMs].sort((a, b) => a - b);
      const percentile = (fraction: number) => intervals.length
        ? intervals[Math.min(intervals.length - 1, Math.ceil(fraction * (intervals.length - 1)))]
        : null;
      const renderTimes = [...this.renderDurationsMs].sort((a, b) => a - b);
      const renderPercentile = (fraction: number) => renderTimes.length
        ? renderTimes[Math.ceil(fraction * (renderTimes.length - 1))] : null;
      const geometries = new Set<THREE.BufferGeometry>();
      const materials = new Set<THREE.Material>();
      let visibleMeshes = 0;
      let geometryBuffersBytes = 0;
      this.root.traverse(object => {
        if (!(object instanceof THREE.Mesh)) return;
        if (object.visible) visibleMeshes += 1;
        if (!geometries.has(object.geometry)) {
          geometries.add(object.geometry);
          for (const attribute of Object.values(object.geometry.attributes) as THREE.BufferAttribute[]) {
            geometryBuffersBytes += attribute.array.byteLength;
          }
          if (object.geometry.index) geometryBuffersBytes += object.geometry.index.array.byteLength;
        }
        for (const material of Array.isArray(object.material) ? object.material : [object.material]) materials.add(material);
      });
      this.renderer.domElement.dataset.scene = JSON.stringify({
        root: this.root.uuid, renderer: this.renderer.domElement.id, selectedId: this.view.selectedId,
        camera: this.camera.position.toArray(), target: this.controls.target.toArray(),
        loaded: [...this.queue.loaded.keys()], pending: [...this.queue.pending.keys()],
        visible: [...this.root.children].flatMap(g => g.children.filter(o => o.visible).map(o => o.name)),
        calls: this.renderer.info.render.calls, triangles: this.renderer.info.render.triangles,
        geometries: this.renderer.info.memory.geometries, visibleMeshes, materials: materials.size, geometryBuffersBytes,
        renderedFrames: this.renderedFrames, registeredUpdates: this.updates.size,
        renderSampleCount: renderTimes.length, renderCpuP50Ms: renderPercentile(0.5), renderCpuP95Ms: renderPercentile(0.95),
        frameSampleCount: intervals.length, frameIntervalP50Ms: percentile(0.5), frameIntervalP95Ms: percentile(0.95),
        canvasWidth: this.size.width, canvasHeight: this.size.height, pixelRatio: this.renderer.getPixelRatio(),
      });
    }
    this.notify({ loaded: wanted.filter(id => this.queue.loaded.has(id)).length, total: wanted.length,
      failed: wanted.filter(id => this.queue.failed.has(id)).length, contextLost: this.lost,
      selectedAvailable: !this.view.selectedId || [...this.queue.loaded.values()].some(g => g.children.some(obj => obj.visible && this.assets.get(obj.name)?.stableIds.some(id => (this.view.selectedIds ?? [this.view.selectedId]).includes(id)))),
      calls: this.renderer.info.render.calls, triangles: this.renderer.info.render.triangles, geometries: this.renderer.info.memory.geometries });
  }
  private onLost = (event: Event) => { event.preventDefault(); this.stopEntrance(); this.lost = true; this.demand(); this.report(); };
  private onRestored = () => { this.lost = false; this.dirty = true; this.demand(); this.report(); };
  private onDown = (event: PointerEvent) => { this.stopEntrance(); this.pointer = { x: event.clientX, y: event.clientY }; };
  private onUp = (event: PointerEvent) => {
    if (Math.hypot(event.clientX - this.pointer.x, event.clientY - this.pointer.y) > 5 || event.button !== 0) return;
    const asset = this.pick(event.clientX, event.clientY);
    if (asset) this.select(asset.stableIds[0], asset.side);
  };
  private pick(x: number, y: number): BodyAsset | undefined {
    if (this.assets.size === 0) return undefined; // A dataset adapter owns eligible picking on this root.
    const rect = this.renderer.domElement.getBoundingClientRect();
    const ray = new THREE.Raycaster();
    ray.setFromCamera(new THREE.Vector2((x - rect.left) / rect.width * 2 - 1, -(y - rect.top) / rect.height * 2 + 1), this.camera);
    const hit = ray.intersectObject(this.root, true).find(h => h.object.visible);
    const asset = hit && this.assets.get(hit.object.name);
    return asset && pickable(asset) ? asset : undefined;
  }
  private setHover(id: string | null) {
    if (this.hoverId === id) return;
    this.hoverId = id; this.renderer.domElement.style.cursor = id ? 'pointer' : 'grab'; this.sync();
  }
  private onMove = (event: PointerEvent) => {
    if (event.buttons || event.pointerType === 'touch') { this.onLeave(); return; }
    this.hoverPoint = { x: event.clientX, y: event.clientY };
  };
  private onLeave = () => { this.hoverPoint = null; this.setHover(null); };
  private onKey = (event: KeyboardEvent) => {
    this.stopEntrance();
    const offset = this.camera.position.clone().sub(this.controls.target);
    const spherical = new THREE.Spherical().setFromVector3(offset);
    switch (event.key) {
      case 'ArrowLeft': spherical.theta -= 0.12; break;
      case 'ArrowRight': spherical.theta += 0.12; break;
      case 'ArrowUp': spherical.phi -= 0.12; break;
      case 'ArrowDown': spherical.phi += 0.12; break;
      case '+': case '=': spherical.radius *= 0.9; break;
      case '-': spherical.radius *= 1.1; break;
      case 'Home': this.focus(this.view.regionIds ?? (this.view.region ? [this.view.region] : [])); event.preventDefault(); return;
      default: return;
    }
    event.preventDefault(); spherical.makeSafe(); spherical.radius = THREE.MathUtils.clamp(spherical.radius, 0.06, 8);
    this.camera.position.copy(this.controls.target).add(new THREE.Vector3().setFromSpherical(spherical)); this.controls.update(); this.dirty = true;
  };
  private release(group: THREE.Group) {
    group.removeFromParent(); group.traverse(obj => { if (obj instanceof THREE.Mesh) { obj.geometry.dispose(); (Array.isArray(obj.material) ? obj.material : [obj.material]).forEach(m => m.dispose()); } });
  }
  dispose() {
    this.stopEntrance();
    this.dead = true; this.renderer.setAnimationLoop(null); this.queue.dispose(); this.updates.clear(); this.observer.disconnect();
    this.controls.removeEventListener('start', this.stopEntrance);
    this.reducedMotion.removeEventListener('change', this.stopEntrance);
    this.controls.dispose();
    const canvas = this.renderer.domElement;
    document.removeEventListener('visibilitychange', this.invalidate);
    window.removeEventListener('pageshow', this.invalidate);
    canvas.removeEventListener('focus', this.invalidate);
    canvas.removeEventListener('webglcontextlost', this.onLost); canvas.removeEventListener('webglcontextrestored', this.onRestored);
    canvas.removeEventListener('pointermove', this.onMove); canvas.removeEventListener('pointerleave', this.onLeave);
    canvas.removeEventListener('pointerdown', this.onDown); canvas.removeEventListener('pointerup', this.onUp); canvas.removeEventListener('keydown', this.onKey);
    this.renderer.dispose(); canvas.remove();
  }
}
