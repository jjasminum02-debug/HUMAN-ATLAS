import {
  AmbientLight, Box3, BufferAttribute, BufferGeometry, Color, DirectionalLight, DoubleSide,
  Mesh, MeshPhongMaterial, PerspectiveCamera, Raycaster, Scene, Triangle,
  Vector2, Vector3, WebGLRenderer,
} from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import type { AnnotationSurfaceHit, ProjectedPoint, ViewerMesh } from "./glb";
import { isFocusDimmed, pickThroughTransparent, visibilityAfterRestore, type MeshVisibility } from "./visibilityPolicy";

type Preset = "front" | "back" | "lateral";
type DisplayMesh = Mesh<BufferGeometry, MeshPhongMaterial>;

const PALETTE = [0xaa594a, 0xb86654, 0xa6574a, 0xba6b59, 0xb16152, 0xc2705c, 0xad5c4d];
const SELECTED_COLOR = new Color(0xcf7a61);

export class ThreeViewer {
  private readonly renderer: WebGLRenderer;
  private readonly scene = new Scene();
  private readonly camera = new PerspectiveCamera(45, 1, 0.002, 100);
  private readonly controls: OrbitControls;
  private readonly raycaster = new Raycaster();
  private readonly observer: ResizeObserver;
  private readonly meshes = new Map<string, ViewerMesh>();
  private readonly display = new Map<string, DisplayMesh>();
  private readonly visibility = new Map<string, MeshVisibility>();
  private readonly baseColors = new Map<string, Color>();
  private selectedIds = new Set<string>();
  private focusIds = new Set<string>();
  private focusFadeEnabled = false;
  private pickThroughTransparent = false;
  private isolatedIds: Set<string> | null = null;
  private onAnnotationPick: ((hit: AnnotationSurfaceHit) => void) | null = null;
  private onFrame: (() => void) | null = null;
  private pointerStart: { id: number; x: number; y: number } | null = null;
  private readonly onDown = (event: PointerEvent) => {
    if (event.button === 0) this.pointerStart = { id: event.pointerId, x: event.clientX, y: event.clientY };
  };
  private readonly onUp = (event: PointerEvent) => {
    const start = this.pointerStart;
    this.pointerStart = null;
    if (start && start.id === event.pointerId && Math.hypot(event.clientX - start.x, event.clientY - start.y) <= 4) this.pick(event);
  };
  private readonly onKey = (event: KeyboardEvent) => {
    if (event.key === "Home") {
      event.preventDefault();
      this.fitAll();
      return;
    }
    if (event.key === "ArrowLeft" || event.key === "ArrowRight") {
      event.preventDefault();
      this.controls.rotateLeft(event.key === "ArrowLeft" ? 0.12 : -0.12);
      this.controls.update();
    } else if (event.key === "ArrowUp" || event.key === "ArrowDown") {
      event.preventDefault();
      this.controls.rotateUp(event.key === "ArrowUp" ? 0.12 : -0.12);
      this.controls.update();
    }
  };

  constructor(private readonly canvas: HTMLCanvasElement, private readonly onPick: (mesh: ViewerMesh) => void) {
    this.renderer = new WebGLRenderer({ canvas, antialias: true, alpha: false, preserveDrawingBuffer: true });
    this.renderer.setClearColor(0xf1f2f3);
    this.scene.add(new AmbientLight(0xffffff, 1.6));
    const key = new DirectionalLight(0xffffff, 2.0);
    key.position.set(0.32, 0.82, 0.65);
    this.scene.add(key);
    const fill = new DirectionalLight(0xffffff, 0.7);
    fill.position.set(-0.7, 0.2, -0.7);
    this.scene.add(fill);
    this.controls = new OrbitControls(this.camera, canvas);
    this.controls.enablePan = false;
    this.controls.minDistance = 0.06;
    this.controls.maxDistance = 12;
    this.controls.addEventListener("change", () => this.render());
    canvas.addEventListener("pointerdown", this.onDown);
    canvas.addEventListener("pointerup", this.onUp);
    canvas.addEventListener("pointercancel", this.onUp);
    canvas.addEventListener("keydown", this.onKey);
    this.observer = new ResizeObserver(() => this.render());
    this.observer.observe(canvas);
  }

  setScene(meshes: readonly ViewerMesh[]): void {
    for (const object of this.display.values()) {
      this.scene.remove(object);
      object.material.dispose();
      object.geometry.dispose();
    }
    this.meshes.clear();
    this.display.clear();
    this.visibility.clear();
    this.baseColors.clear();
    this.focusIds.clear();
    this.focusFadeEnabled = false;
    meshes.forEach((mesh, index) => {
      const geometry = new BufferGeometry();
      geometry.setAttribute("position", new BufferAttribute(mesh.positions, 3));
      geometry.setAttribute("normal", new BufferAttribute(mesh.normals, 3));
      geometry.setIndex(new BufferAttribute(mesh.indices, 1));
      const material = new MeshPhongMaterial({
        color: mesh.targetEntityType === "structure" ? 0xe0d9bd : PALETTE[index % PALETTE.length],
        side: DoubleSide, shininess: 28,
      });
      const object: DisplayMesh = new Mesh(geometry, material);
      object.name = mesh.meshAssetId;
      this.scene.add(object);
      this.meshes.set(mesh.meshAssetId, mesh);
      this.display.set(mesh.meshAssetId, object);
      this.visibility.set(mesh.meshAssetId, "visible");
      this.baseColors.set(mesh.meshAssetId, material.color.clone());
    });
    this.fitAll();
  }

  getMesh(id: string): ViewerMesh | undefined { return this.meshes.get(id); }
  setAnnotationPickHandler(handler: ((hit: AnnotationSurfaceHit) => void) | null): void { this.onAnnotationPick = handler; }
  setFrameCallback(callback: (() => void) | null): void { this.onFrame = callback; this.onFrame?.(); }

  projectPoint(point: readonly [number, number, number]): ProjectedPoint {
    const rect = this.canvas.getBoundingClientRect();
    const ndc = new Vector3(...point).project(this.camera);
    return {
      x: (ndc.x + 1) * 0.5 * rect.width,
      y: (1 - ndc.y) * 0.5 * rect.height,
      depth: ndc.z,
      visible: ndc.x >= -1 && ndc.x <= 1 && ndc.y >= -1 && ndc.y <= 1 && ndc.z >= -1 && ndc.z <= 1,
    };
  }

  selectMeshes(ids: readonly string[], focus = false): void {
    this.selectedIds = new Set(ids);
    if (this.isolatedIds && ids.length > 0) this.isolatedIds = new Set(ids);
    this.updateDisplay();
    if (focus && ids.length > 0) this.focus(ids, 1.25);
  }

  setVisibility(id: string, value: MeshVisibility): void {
    if (!this.meshes.has(id)) return;
    this.visibility.set(id, value);
    this.updateDisplay();
  }

  getVisibility(id: string): MeshVisibility { return this.visibility.get(id) ?? "visible"; }
  setPickThroughTransparent(enabled: boolean): void { this.pickThroughTransparent = enabled; }
  setSelectionFocus(ids: readonly string[], enabled: boolean): void {
    this.focusIds = new Set(ids);
    this.focusFadeEnabled = enabled;
    this.updateDisplay();
  }
  setIsolation(ids: readonly string[] | null): void {
    this.isolatedIds = ids && ids.length > 0 ? new Set(ids) : null;
    this.updateDisplay();
  }
  isIsolated(id: string): boolean { return this.isolatedIds !== null && !this.isolatedIds.has(id); }
  restoreAll(preserveBaseVisibility = false): void {
    for (const id of this.meshes.keys()) this.visibility.set(id, visibilityAfterRestore(this.getVisibility(id), preserveBaseVisibility));
    this.isolatedIds = null;
    this.updateDisplay();
    this.fitAll();
  }

  private bounds(ids: readonly string[]): Box3 | null {
    const result = new Box3();
    let count = 0;
    for (const id of ids) {
      const mesh = this.meshes.get(id);
      if (!mesh) continue;
      result.expandByPoint(new Vector3(...mesh.bounds.min));
      result.expandByPoint(new Vector3(...mesh.bounds.max));
      count += 1;
    }
    return count ? result : null;
  }

  private frame(bounds: Box3, margin: number, minimum: number): void {
    const center = bounds.getCenter(new Vector3());
    const radius = Math.max(0.025, bounds.getSize(new Vector3()).length() / 2);
    const distance = Math.max(minimum, radius * margin);
    const direction = this.camera.position.clone().sub(this.controls.target).normalize();
    if (direction.lengthSq() === 0) direction.set(0, 0, 1);
    this.controls.target.copy(center);
    this.camera.position.copy(center).addScaledVector(direction, distance);
    this.controls.update();
    this.render();
  }

  fitAll(): void {
    const bounds = this.bounds([...this.meshes.keys()]);
    if (bounds) this.frame(bounds, 3.1, 0.5);
  }
  focus(ids: readonly string[], margin: number): void {
    const bounds = this.bounds(ids);
    if (bounds) this.frame(bounds, 2.414 * margin, 0.11);
  }
  focusSelected(margin: number): void { this.focus([...this.selectedIds], margin); }
  setPreset(preset: Preset): void {
    const direction = preset === "front" ? new Vector3(0, 0, 1) : preset === "back" ? new Vector3(0, 0, -1) : new Vector3(-1, 0, 0);
    const distance = Math.max(this.controls.minDistance, this.camera.position.distanceTo(this.controls.target));
    this.camera.position.copy(this.controls.target).addScaledVector(direction, distance);
    this.controls.update();
    this.render();
  }

  private updateDisplay(): void {
    for (const [id, object] of this.display) {
      const state = this.getVisibility(id);
      const focusDimmed = isFocusDimmed(id, this.meshes.get(id)?.targetEntityType ?? "", this.focusIds, this.focusFadeEnabled);
      object.visible = state !== "hidden" && !this.isIsolated(id);
      const transparent = state === "transparent" || focusDimmed;
      object.material.transparent = transparent;
      object.material.opacity = state === "transparent" ? 0.2 : focusDimmed ? 0.28 : 1;
      object.material.depthWrite = !transparent;
      object.material.color.copy(this.selectedIds.has(id) ? SELECTED_COLOR : this.baseColors.get(id) ?? new Color(0x888888));
      object.material.needsUpdate = true;
    }
    this.render();
  }

  private resize(): void {
    const rect = this.canvas.getBoundingClientRect();
    const pixelRatio = Math.min(window.devicePixelRatio || 1, 2);
    const width = Math.max(1, Math.round(rect.width * pixelRatio));
    const height = Math.max(1, Math.round(rect.height * pixelRatio));
    if (this.canvas.width !== width || this.canvas.height !== height) this.renderer.setSize(width, height, false);
    const aspect = width / height;
    if (this.camera.aspect !== aspect) {
      this.camera.aspect = aspect;
      this.camera.updateProjectionMatrix();
    }
  }
  private render(): void {
    if (!this.canvas.isConnected) return;
    this.resize();
    this.renderer.render(this.scene, this.camera);
    this.onFrame?.();
  }

  private pick(event: PointerEvent): void {
    const rect = this.canvas.getBoundingClientRect();
    if (rect.width <= 0 || rect.height <= 0) return;
    const ndc = new Vector2((event.clientX - rect.left) / rect.width * 2 - 1, 1 - (event.clientY - rect.top) / rect.height * 2);
    this.raycaster.setFromCamera(ndc, this.camera);
    const eligible = [...this.display.values()].filter((object) => object.visible);
    const intersections = this.raycaster.intersectObjects(
      this.pickThroughTransparent ? eligible : eligible.filter((object) => this.getVisibility(object.name) === "visible"),
      false,
    );
    let hit: (typeof intersections)[number] | undefined = intersections[0];
    if (this.pickThroughTransparent) {
      const picked = pickThroughTransparent(intersections.map((intersection) => ({ intersection, meshAssetId: intersection.object.name })), (id) => {
        if (this.isIsolated(id)) return "hidden";
        const baseVisibility = this.getVisibility(id);
        if (baseVisibility === "hidden") return "hidden";
        if (baseVisibility === "transparent") return "transparent";
        return isFocusDimmed(id, this.meshes.get(id)?.targetEntityType ?? "", this.focusIds, this.focusFadeEnabled) ? "transparent" : "visible";
      });
      hit = picked?.intersection;
    }
    if (!hit || !(hit.object instanceof Mesh)) return;
    const mesh = this.meshes.get(hit.object.name);
    if (!mesh) return;
    if (!this.onAnnotationPick) { this.onPick(mesh); return; }
    const triangleId = hit.faceIndex;
    if (triangleId == null || triangleId < 0 || triangleId >= mesh.indices.length / 3) return;
    const base = triangleId * 3;
    const vertex = (index: number) => new Vector3(
      mesh.positions[mesh.indices[index] * 3], mesh.positions[mesh.indices[index] * 3 + 1], mesh.positions[mesh.indices[index] * 3 + 2],
    );
    const local = hit.object.worldToLocal(hit.point.clone());
    const barycentric = Triangle.getBarycoord(local, vertex(base), vertex(base + 1), vertex(base + 2), new Vector3());
    if (!barycentric) return;
    this.onAnnotationPick({ mesh, triangleId, position: local.toArray(), barycentric: barycentric.toArray() });
  }

  dispose(): void {
    this.observer.disconnect();
    this.canvas.removeEventListener("pointerdown", this.onDown);
    this.canvas.removeEventListener("pointerup", this.onUp);
    this.canvas.removeEventListener("pointercancel", this.onUp);
    this.canvas.removeEventListener("keydown", this.onKey);
    this.controls.dispose();
    for (const object of this.display.values()) {
      this.scene.remove(object);
      object.material.dispose();
      object.geometry.dispose();
    }
    this.onFrame = null;
    this.onAnnotationPick = null;
    this.renderer.dispose();
    this.renderer.forceContextLoss();
    this.display.clear();
    this.meshes.clear();
  }
}
