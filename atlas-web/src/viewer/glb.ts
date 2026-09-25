export interface ExpectedNode {
  meshAssetId: string;
  nodeIndex: number;
  meshIndex: number;
  sourceName: string;
  sourceFileId: string;
  targetEntityId: string | null;
  targetEntityType: string;
  relationStatus: string;
  reviewState: string;
}

export interface MeshBounds {
  min: [number, number, number];
  max: [number, number, number];
}

export interface ViewerMesh extends ExpectedNode {
  positions: Float32Array;
  normals: Float32Array;
  indices: Uint16Array | Uint32Array;
  bounds: MeshBounds;
}

export interface AnnotationSurfaceHit {
  mesh: ViewerMesh;
  triangleId: number;
  position: [number, number, number];
  barycentric: [number, number, number];
}

export interface ProjectedPoint {
  x: number;
  y: number;
  depth: number;
  visible: boolean;
}

interface GlbDocument {
  accessors?: Array<{
    bufferView?: number;
    byteOffset?: number;
    componentType?: number;
    count?: number;
    type?: string;
    sparse?: unknown;
  }>;
  bufferViews?: Array<{ buffer?: number; byteOffset?: number; byteLength?: number; byteStride?: number }>;
  buffers?: Array<{ byteLength?: number; uri?: string }>;
  meshes?: Array<{
    name?: string;
    extras?: Record<string, unknown>;
    primitives?: Array<{
      attributes?: Record<string, number>;
      indices?: number;
      mode?: number;
    }>;
  }>;
  nodes?: Array<{ mesh?: number; name?: string; extras?: Record<string, unknown>; children?: number[]; matrix?: number[]; translation?: number[]; rotation?: number[]; scale?: number[] }>;
  scenes?: Array<{ nodes?: number[] }>;
  scene?: number;
}

const GLB_MAGIC = 0x46546c67;
const JSON_CHUNK = 0x4e4f534a;
const BIN_CHUNK = 0x004e4942;

function accessorData(
  document: GlbDocument,
  binary: Uint8Array,
  accessorIndex: number,
  expectedType: "VEC3" | "SCALAR",
  expectedComponentType: 5126 | 5123 | 5125,
): Float32Array | Uint16Array | Uint32Array {
  const accessor = document.accessors?.[accessorIndex];
  if (!accessor || accessor.type !== expectedType || accessor.componentType !== expectedComponentType) {
    throw new Error(`GLB accessor ${accessorIndex} 형식이 T07 viewer 계약과 다릅니다.`);
  }
  if (accessor.sparse !== undefined) throw new Error("Sparse accessor는 현재 T07 viewer에서 지원하지 않습니다.");
  if (!Number.isInteger(accessor.count) || (accessor.count ?? 0) < 1 || !Number.isInteger(accessor.bufferView)) {
    throw new Error(`GLB accessor ${accessorIndex}의 길이 또는 bufferView가 잘못되었습니다.`);
  }
  const view = document.bufferViews?.[accessor.bufferView as number];
  if (!view || view.buffer !== 0 || !Number.isInteger(view.byteLength)) {
    throw new Error(`GLB accessor ${accessorIndex}가 지원되지 않는 buffer를 참조합니다.`);
  }
  const componentBytes = expectedComponentType === 5126 || expectedComponentType === 5125 ? 4 : 2;
  const componentCount = expectedType === "VEC3" ? 3 : 1;
  const packedStride = componentBytes * componentCount;
  const stride = view.byteStride ?? packedStride;
  const start = (view.byteOffset ?? 0) + (accessor.byteOffset ?? 0);
  const count = accessor.count as number;
  if (stride < packedStride || start < 0 || start + (count - 1) * stride + packedStride > binary.byteLength) {
    throw new Error(`GLB accessor ${accessorIndex}가 binary chunk 범위를 벗어납니다.`);
  }

  const dataView = new DataView(binary.buffer, binary.byteOffset, binary.byteLength);
  if (expectedComponentType === 5126) {
    const output = new Float32Array(count * componentCount);
    for (let row = 0; row < count; row += 1) {
      for (let component = 0; component < componentCount; component += 1) {
        output[row * componentCount + component] = dataView.getFloat32(start + row * stride + component * 4, true);
      }
    }
    return output;
  }
  if (expectedComponentType === 5123) {
    const output = new Uint16Array(count);
    for (let row = 0; row < count; row += 1) output[row] = dataView.getUint16(start + row * stride, true);
    return output;
  }
  const output = new Uint32Array(count);
  for (let row = 0; row < count; row += 1) output[row] = dataView.getUint32(start + row * stride, true);
  return output;
}

export function decodeT07Glb(buffer: ArrayBuffer, expectedNodes: readonly ExpectedNode[]): ViewerMesh[] {
  if (buffer.byteLength < 20) throw new Error("GLB 파일이 너무 짧습니다.");
  const header = new DataView(buffer, 0, 12);
  if (header.getUint32(0, true) !== GLB_MAGIC || header.getUint32(4, true) !== 2 || header.getUint32(8, true) !== buffer.byteLength) {
    throw new Error("GLB header가 T07의 glTF 2.0 형식과 일치하지 않습니다.");
  }
  let offset = 12;
  let document: GlbDocument | null = null;
  let binary: Uint8Array | null = null;
  while (offset < buffer.byteLength) {
    if (offset + 8 > buffer.byteLength) throw new Error("GLB chunk header가 잘렸습니다.");
    const chunkHeader = new DataView(buffer, offset, 8);
    const length = chunkHeader.getUint32(0, true);
    const type = chunkHeader.getUint32(4, true);
    offset += 8;
    if (length % 4 !== 0 || offset + length > buffer.byteLength) throw new Error("GLB chunk 정렬 또는 길이가 잘못되었습니다.");
    const bytes = new Uint8Array(buffer, offset, length);
    if (type === JSON_CHUNK && document === null) {
      document = JSON.parse(new TextDecoder().decode(bytes)) as GlbDocument;
    } else if (type === BIN_CHUNK && binary === null) {
      binary = bytes;
    } else {
      throw new Error("T07 GLB에 예상하지 못한 중복/추가 chunk가 있습니다.");
    }
    offset += length;
  }
  if (!document || !binary) throw new Error("GLB JSON 또는 BIN chunk가 없습니다.");
  if (document.buffers?.length !== 1 || document.buffers[0]?.uri !== undefined || (document.buffers[0]?.byteLength ?? 0) > binary.byteLength) {
    throw new Error("T07 GLB가 단일 embedded binary buffer 계약과 다릅니다.");
  }
  if (!Array.isArray(document.nodes) || !Array.isArray(document.meshes) || document.nodes.length !== expectedNodes.length || document.meshes.length !== expectedNodes.length) {
    throw new Error("GLB node/mesh 개수가 manifest의 11개 stable ID와 맞지 않습니다.");
  }
  const sceneNodes = document.scenes?.[document.scene ?? 0]?.nodes;
  if (!sceneNodes || sceneNodes.length !== expectedNodes.length || new Set(sceneNodes).size !== expectedNodes.length) {
    throw new Error("GLB scene node 목록이 T07 manifest와 맞지 않습니다.");
  }

  return expectedNodes.map((expected) => {
    const node = document.nodes?.[expected.nodeIndex];
    const mesh = document.meshes?.[expected.meshIndex];
    if (!node || !mesh || sceneNodes.includes(expected.nodeIndex) === false) throw new Error(`${expected.meshAssetId}: node/mesh index가 없습니다.`);
    if (node.mesh !== expected.meshIndex || node.name !== expected.meshAssetId || mesh.name !== expected.meshAssetId) {
      throw new Error(`${expected.meshAssetId}: GLB node/mesh ID가 manifest와 다릅니다.`);
    }
    if (node.matrix || node.translation || node.rotation || node.scale || (node.children?.length ?? 0) > 0) {
      throw new Error(`${expected.meshAssetId}: 알 수 없는 node transform/hierarchy를 적용할 수 없습니다.`);
    }
    if (node.extras?.stableMeshAssetId !== expected.meshAssetId || mesh.extras?.stableMeshAssetId !== expected.meshAssetId) {
      throw new Error(`${expected.meshAssetId}: GLB extras stable ID가 manifest와 다릅니다.`);
    }
    const primitive = mesh.primitives?.[0];
    if (!primitive || mesh.primitives?.length !== 1 || primitive.mode !== 4 || primitive.indices === undefined) {
      throw new Error(`${expected.meshAssetId}: 단일 triangle primitive가 아닙니다.`);
    }
    const attributes = primitive.attributes;
    if (!attributes || attributes.POSITION === undefined || attributes.NORMAL === undefined) {
      throw new Error(`${expected.meshAssetId}: position 또는 normal accessor가 없습니다.`);
    }
    const positions = accessorData(document, binary, attributes.POSITION, "VEC3", 5126) as Float32Array;
    const normals = accessorData(document, binary, attributes.NORMAL, "VEC3", 5126) as Float32Array;
    const indexAccessor = document.accessors?.[primitive.indices];
    if (!indexAccessor || indexAccessor.type !== "SCALAR" || (indexAccessor.componentType !== 5123 && indexAccessor.componentType !== 5125)) {
      throw new Error(`${expected.meshAssetId}: triangle index 형식이 지원되지 않습니다.`);
    }
    const indices = accessorData(document, binary, primitive.indices, "SCALAR", indexAccessor.componentType) as Uint16Array | Uint32Array;
    if (positions.length !== normals.length || positions.length % 3 !== 0 || indices.length % 3 !== 0) {
      throw new Error(`${expected.meshAssetId}: position/normal/triangle 수가 맞지 않습니다.`);
    }
    const vertexCount = positions.length / 3;
    let min: [number, number, number] = [Infinity, Infinity, Infinity];
    let max: [number, number, number] = [-Infinity, -Infinity, -Infinity];
    for (let i = 0; i < positions.length; i += 3) {
      min = [Math.min(min[0], positions[i]), Math.min(min[1], positions[i + 1]), Math.min(min[2], positions[i + 2])];
      max = [Math.max(max[0], positions[i]), Math.max(max[1], positions[i + 1]), Math.max(max[2], positions[i + 2])];
    }
    for (const index of indices) if (index >= vertexCount) throw new Error(`${expected.meshAssetId}: index가 vertex 범위를 벗어납니다.`);
    for (const value of normals) if (!Number.isFinite(value)) throw new Error(`${expected.meshAssetId}: normal에 유효하지 않은 수가 있습니다.`);
    return { ...expected, positions, normals, indices, bounds: { min, max } };
  });
}

type Vec3 = [number, number, number];
type CameraPreset = "front" | "back" | "lateral";
type Visibility = "visible" | "transparent" | "hidden";

interface GpuMesh {
  mesh: ViewerMesh;
  positionBuffer: WebGLBuffer;
  normalBuffer: WebGLBuffer;
  indexBuffer: WebGLBuffer;
  count: number;
  indexType: number;
  color: [number, number, number];
}

const surfaceVertexShader = `#version 300 es
in vec3 a_position;
in vec3 a_normal;
uniform mat4 u_mvp;
uniform mat4 u_view;
out vec3 v_normal;
void main() { v_normal = mat3(u_view) * a_normal; gl_Position = u_mvp * vec4(a_position, 1.0); }
`;
const surfaceFragmentShader = `#version 300 es
precision highp float;
in vec3 v_normal;
uniform vec4 u_color;
out vec4 outColor;
void main() {
  vec3 n = normalize(v_normal);
  float diffuse = abs(dot(n, normalize(vec3(0.32, 0.82, 0.48))));
  float light = 0.42 + 0.58 * diffuse;
  outColor = vec4(u_color.rgb * light, u_color.a);
}
`;
const pickVertexShader = `#version 300 es
in vec3 a_position;
uniform mat4 u_mvp;
void main() { gl_Position = u_mvp * vec4(a_position, 1.0); }
`;
const pickFragmentShader = `#version 300 es
precision highp float;
uniform vec4 u_pick_color;
out vec4 outColor;
void main() { outColor = u_pick_color; }
`;

function compileShader(gl: WebGL2RenderingContext, type: number, source: string): WebGLShader {
  const shader = gl.createShader(type);
  if (!shader) throw new Error("WebGL shader를 생성할 수 없습니다.");
  gl.shaderSource(shader, source);
  gl.compileShader(shader);
  if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
    const log = gl.getShaderInfoLog(shader) ?? "unknown shader error";
    gl.deleteShader(shader);
    throw new Error(`WebGL shader compilation 실패: ${log}`);
  }
  return shader;
}

function createProgram(gl: WebGL2RenderingContext, vertexSource: string, fragmentSource: string): WebGLProgram {
  const vertex = compileShader(gl, gl.VERTEX_SHADER, vertexSource);
  const fragment = compileShader(gl, gl.FRAGMENT_SHADER, fragmentSource);
  const program = gl.createProgram();
  if (!program) throw new Error("WebGL program을 생성할 수 없습니다.");
  gl.attachShader(program, vertex);
  gl.attachShader(program, fragment);
  gl.linkProgram(program);
  gl.deleteShader(vertex);
  gl.deleteShader(fragment);
  if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
    const log = gl.getProgramInfoLog(program) ?? "unknown program error";
    gl.deleteProgram(program);
    throw new Error(`WebGL program link 실패: ${log}`);
  }
  return program;
}

function normalize(v: Vec3): Vec3 {
  const length = Math.hypot(v[0], v[1], v[2]) || 1;
  return [v[0] / length, v[1] / length, v[2] / length];
}
function subtract(a: Vec3, b: Vec3): Vec3 { return [a[0] - b[0], a[1] - b[1], a[2] - b[2]]; }
function cross(a: Vec3, b: Vec3): Vec3 { return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]; }
function dot(a: Vec3, b: Vec3): number { return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]; }

function perspective(fov: number, aspect: number, near: number, far: number): Float32Array {
  const f = 1 / Math.tan(fov / 2);
  const range = 1 / (near - far);
  return new Float32Array([
    f / aspect, 0, 0, 0,
    0, f, 0, 0,
    0, 0, (near + far) * range, -1,
    0, 0, near * far * 2 * range, 0,
  ]);
}

function lookAt(eye: Vec3, center: Vec3, up: Vec3): Float32Array {
  const z = normalize(subtract(eye, center));
  const x = normalize(cross(up, z));
  const y = cross(z, x);
  return new Float32Array([
    x[0], y[0], z[0], 0,
    x[1], y[1], z[1], 0,
    x[2], y[2], z[2], 0,
    -dot(x, eye), -dot(y, eye), -dot(z, eye), 1,
  ]);
}

function multiply(a: Float32Array, b: Float32Array): Float32Array {
  const output = new Float32Array(16);
  for (let column = 0; column < 4; column += 1) {
    for (let row = 0; row < 4; row += 1) {
      output[column * 4 + row] =
        a[row] * b[column * 4] +
        a[4 + row] * b[column * 4 + 1] +
        a[8 + row] * b[column * 4 + 2] +
        a[12 + row] * b[column * 4 + 3];
    }
  }
  return output;
}

function unionBounds(meshes: readonly ViewerMesh[]): MeshBounds {
  const min: Vec3 = [Infinity, Infinity, Infinity];
  const max: Vec3 = [-Infinity, -Infinity, -Infinity];
  for (const mesh of meshes) {
    for (let i = 0; i < 3; i += 1) {
      min[i] = Math.min(min[i], mesh.bounds.min[i]);
      max[i] = Math.max(max[i], mesh.bounds.max[i]);
    }
  }
  return { min, max };
}

function centerOf(bounds: MeshBounds): Vec3 {
  return [(bounds.min[0] + bounds.max[0]) / 2, (bounds.min[1] + bounds.max[1]) / 2, (bounds.min[2] + bounds.max[2]) / 2];
}

export class T07WebGLViewer {
  private readonly gl: WebGL2RenderingContext;
  private readonly surfaceProgram: WebGLProgram;
  private readonly pickProgram: WebGLProgram;
  private readonly observer: ResizeObserver;
  private readonly meshes = new Map<string, GpuMesh>();
  private readonly visibility = new Map<string, Visibility>();
  private readonly onPick: (mesh: ViewerMesh) => void;
  private onAnnotationPick: ((hit: AnnotationSurfaceHit) => void) | null = null;
  private onFrame: (() => void) | null = null;
  private readonly pointerDown = (event: PointerEvent) => this.handlePointerDown(event);
  private readonly pointerMove = (event: PointerEvent) => this.handlePointerMove(event);
  private readonly pointerUp = (event: PointerEvent) => this.handlePointerUp(event);
  private readonly wheel = (event: WheelEvent) => this.handleWheel(event);
  private readonly keyDown = (event: KeyboardEvent) => this.handleKeyDown(event);
  private center: Vec3 = [0, 0, 0];
  private radius = 0.25;
  private distance = 0.9;
  private yaw = 0;
  private pitch = 0;
  private selectedIds = new Set<string>();
  private isolatedIds: Set<string> | null = null;
  private dragged = false;
  private lastPointer: { id: number; x: number; y: number; startX: number; startY: number } | null = null;

  constructor(private readonly canvas: HTMLCanvasElement, onPick: (mesh: ViewerMesh) => void) {
    const gl = canvas.getContext("webgl2", { antialias: true, alpha: false, preserveDrawingBuffer: true });
    if (!gl) throw new Error("이 브라우저에서 WebGL 2를 사용할 수 없습니다.");
    this.gl = gl;
    this.onPick = onPick;
    this.surfaceProgram = createProgram(gl, surfaceVertexShader, surfaceFragmentShader);
    this.pickProgram = createProgram(gl, pickVertexShader, pickFragmentShader);
    this.observer = new ResizeObserver(() => this.render());
    this.observer.observe(canvas);
    canvas.addEventListener("pointerdown", this.pointerDown);
    canvas.addEventListener("pointermove", this.pointerMove);
    canvas.addEventListener("pointerup", this.pointerUp);
    canvas.addEventListener("pointercancel", this.pointerUp);
    canvas.addEventListener("wheel", this.wheel, { passive: false });
    canvas.addEventListener("keydown", this.keyDown);
    gl.enable(gl.DEPTH_TEST);
    gl.depthFunc(gl.LEQUAL);
    gl.disable(gl.CULL_FACE);
    gl.clearColor(0.965, 0.974, 0.956, 1);
  }

  setScene(meshes: readonly ViewerMesh[]): void {
    this.disposeMeshes();
    const gl = this.gl;
    const palette: Array<[number, number, number]> = [
      [0.70, 0.43, 0.31], [0.78, 0.54, 0.40], [0.45, 0.62, 0.50], [0.61, 0.69, 0.51],
      [0.55, 0.52, 0.69], [0.42, 0.63, 0.69], [0.68, 0.58, 0.42],
    ];
    meshes.forEach((mesh, index) => {
      const positionBuffer = gl.createBuffer();
      const normalBuffer = gl.createBuffer();
      const indexBuffer = gl.createBuffer();
      if (!positionBuffer || !normalBuffer || !indexBuffer) throw new Error(`${mesh.meshAssetId}: WebGL buffer 생성 실패`);
      gl.bindBuffer(gl.ARRAY_BUFFER, positionBuffer);
      gl.bufferData(gl.ARRAY_BUFFER, mesh.positions, gl.STATIC_DRAW);
      gl.bindBuffer(gl.ARRAY_BUFFER, normalBuffer);
      gl.bufferData(gl.ARRAY_BUFFER, mesh.normals, gl.STATIC_DRAW);
      gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, indexBuffer);
      gl.bufferData(gl.ELEMENT_ARRAY_BUFFER, mesh.indices, gl.STATIC_DRAW);
      this.meshes.set(mesh.meshAssetId, {
        mesh,
        positionBuffer,
        normalBuffer,
        indexBuffer,
        count: mesh.indices.length,
        indexType: mesh.indices instanceof Uint16Array ? gl.UNSIGNED_SHORT : gl.UNSIGNED_INT,
        color: mesh.targetEntityType === "structure" ? [0.72, 0.69, 0.60] : palette[index % palette.length],
      });
      this.visibility.set(mesh.meshAssetId, "visible");
    });
    this.center = centerOf(unionBounds(meshes));
    this.radius = this.boundsRadius(unionBounds(meshes));
    this.distance = Math.max(0.5, this.radius * 3.1);
    this.render();
  }

  setAnnotationPickHandler(handler: ((hit: AnnotationSurfaceHit) => void) | null): void {
    this.onAnnotationPick = handler;
  }

  setFrameCallback(callback: (() => void) | null): void {
    this.onFrame = callback;
    this.onFrame?.();
  }

  getMesh(id: string): ViewerMesh | undefined {
    return this.meshes.get(id)?.mesh;
  }

  projectPoint(point: readonly [number, number, number]): ProjectedPoint {
    const rect = this.canvas.getBoundingClientRect();
    const mvp = this.camera().mvp;
    const [x, y, z] = point;
    const clipX = mvp[0] * x + mvp[4] * y + mvp[8] * z + mvp[12];
    const clipY = mvp[1] * x + mvp[5] * y + mvp[9] * z + mvp[13];
    const clipZ = mvp[2] * x + mvp[6] * y + mvp[10] * z + mvp[14];
    const clipW = mvp[3] * x + mvp[7] * y + mvp[11] * z + mvp[15];
    if (clipW <= 0) return { x: 0, y: 0, depth: Infinity, visible: false };
    const ndcX = clipX / clipW;
    const ndcY = clipY / clipW;
    const ndcZ = clipZ / clipW;
    return {
      x: (ndcX + 1) * 0.5 * rect.width,
      y: (1 - ndcY) * 0.5 * rect.height,
      depth: ndcZ,
      visible: ndcX >= -1 && ndcX <= 1 && ndcY >= -1 && ndcY <= 1 && ndcZ >= -1 && ndcZ <= 1,
    };
  }

  selectMeshes(ids: readonly string[], focus = false): void {
    this.selectedIds = new Set(ids);
    if (this.isolatedIds && ids.length > 0) this.isolatedIds = new Set(ids);
    if (focus && ids.length > 0) this.focus(ids, 1.25);
    else this.render();
  }

  setVisibility(id: string, value: Visibility): void {
    if (!this.meshes.has(id)) return;
    this.visibility.set(id, value);
    this.render();
  }

  getVisibility(id: string): Visibility {
    return this.visibility.get(id) ?? "visible";
  }

  toggleIsolation(ids: readonly string[]): boolean {
    if (ids.length === 0) return false;
    if (this.isolatedIds) {
      this.isolatedIds = null;
      this.render();
      return false;
    }
    this.isolatedIds = new Set(ids);
    this.selectedIds = new Set(ids);
    this.render();
    return true;
  }

  setIsolation(ids: readonly string[] | null): void {
    this.isolatedIds = ids && ids.length > 0 ? new Set(ids) : null;
    this.render();
  }

  isIsolated(id: string): boolean {
    return this.isolatedIds !== null && !this.isolatedIds.has(id);
  }

  restoreAll(): void {
    for (const id of this.meshes.keys()) this.visibility.set(id, "visible");
    this.isolatedIds = null;
    this.fitAll();
  }

  fitAll(): void {
    if (this.meshes.size > 0) {
      const union = unionBounds([...this.meshes.values()].map(({ mesh }) => mesh));
      this.center = centerOf(union);
      this.radius = this.boundsRadius(union);
      this.distance = Math.max(0.5, this.radius * 3.1);
    }
    this.render();
  }

  focus(ids: readonly string[], margin: number): void {
    const selected = ids.flatMap((id) => {
      const mesh = this.meshes.get(id)?.mesh;
      return mesh ? [mesh] : [];
    });
    if (selected.length === 0) return;
    const bounds = unionBounds(selected);
    this.center = centerOf(bounds);
    this.radius = this.boundsRadius(bounds);
    this.distance = Math.max(0.11, this.radius * 2.414 * margin);
    this.render();
  }

  focusSelected(margin: number): void {
    this.focus([...this.selectedIds], margin);
  }

  setPreset(preset: CameraPreset): void {
    this.yaw = preset === "front" ? 0 : preset === "back" ? Math.PI : -Math.PI / 2;
    this.pitch = 0;
    this.render();
  }

  dispose(): void {
    this.observer.disconnect();
    this.canvas.removeEventListener("pointerdown", this.pointerDown);
    this.canvas.removeEventListener("pointermove", this.pointerMove);
    this.canvas.removeEventListener("pointerup", this.pointerUp);
    this.canvas.removeEventListener("pointercancel", this.pointerUp);
    this.canvas.removeEventListener("wheel", this.wheel);
    this.canvas.removeEventListener("keydown", this.keyDown);
    this.disposeMeshes();
    this.gl.deleteProgram(this.surfaceProgram);
    this.gl.deleteProgram(this.pickProgram);
  }

  private disposeMeshes(): void {
    for (const gpu of this.meshes.values()) {
      this.gl.deleteBuffer(gpu.positionBuffer);
      this.gl.deleteBuffer(gpu.normalBuffer);
      this.gl.deleteBuffer(gpu.indexBuffer);
    }
    this.meshes.clear();
    this.visibility.clear();
  }

  private boundsRadius(bounds: MeshBounds): number {
    return Math.max(0.025, Math.hypot(bounds.max[0] - bounds.min[0], bounds.max[1] - bounds.min[1], bounds.max[2] - bounds.min[2]) / 2);
  }

  private resize(): void {
    const rect = this.canvas.getBoundingClientRect();
    const ratio = Math.min(window.devicePixelRatio || 1, 2);
    const width = Math.max(1, Math.round(rect.width * ratio));
    const height = Math.max(1, Math.round(rect.height * ratio));
    if (this.canvas.width !== width || this.canvas.height !== height) {
      this.canvas.width = width;
      this.canvas.height = height;
    }
    this.gl.viewport(0, 0, width, height);
  }

  private camera(): { view: Float32Array; mvp: Float32Array; eye: Vec3 } {
    const horizontal = Math.cos(this.pitch) * this.distance;
    const eye: Vec3 = [
      this.center[0] + Math.sin(this.yaw) * horizontal,
      this.center[1] + Math.sin(this.pitch) * this.distance,
      this.center[2] + Math.cos(this.yaw) * horizontal,
    ];
    const view = lookAt(eye, this.center, [0, 1, 0]);
    const projection = perspective(Math.PI / 4, this.canvas.width / Math.max(1, this.canvas.height), 0.002, 100);
    return { view, mvp: multiply(projection, view), eye };
  }

  private availableMeshes(includeTransparent: boolean): GpuMesh[] {
    return [...this.meshes.values()].filter((gpu) => {
      const visibility = this.visibility.get(gpu.mesh.meshAssetId) ?? "visible";
      if (visibility === "hidden" || (visibility === "transparent" && !includeTransparent)) return false;
      if (this.isolatedIds && !this.isolatedIds.has(gpu.mesh.meshAssetId)) return false;
      return true;
    });
  }

  private bindMesh(gpu: GpuMesh, program: WebGLProgram, mvp: Float32Array, view?: Float32Array): void {
    const gl = this.gl;
    const positionLocation = gl.getAttribLocation(program, "a_position");
    gl.bindBuffer(gl.ARRAY_BUFFER, gpu.positionBuffer);
    gl.enableVertexAttribArray(positionLocation);
    gl.vertexAttribPointer(positionLocation, 3, gl.FLOAT, false, 0, 0);
    if (program === this.surfaceProgram) {
      const normalLocation = gl.getAttribLocation(program, "a_normal");
      gl.bindBuffer(gl.ARRAY_BUFFER, gpu.normalBuffer);
      gl.enableVertexAttribArray(normalLocation);
      gl.vertexAttribPointer(normalLocation, 3, gl.FLOAT, false, 0, 0);
      const viewLocation = gl.getUniformLocation(program, "u_view");
      if (viewLocation && view) gl.uniformMatrix4fv(viewLocation, false, view);
    }
    const mvpLocation = gl.getUniformLocation(program, "u_mvp");
    if (mvpLocation) gl.uniformMatrix4fv(mvpLocation, false, mvp);
    gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, gpu.indexBuffer);
  }

  private render(): void {
    if (!this.canvas.isConnected) return;
    this.resize();
    const gl = this.gl;
    gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);
    if (this.meshes.size === 0) {
      this.onFrame?.();
      return;
    }
    const camera = this.camera();
    const opaque = this.availableMeshes(false);
    const transparent = this.availableMeshes(true).filter((gpu) => this.visibility.get(gpu.mesh.meshAssetId) === "transparent");
    const orderedTransparent = transparent.sort((a, b) => {
      const centerA = centerOf(a.mesh.bounds);
      const centerB = centerOf(b.mesh.bounds);
      return Math.hypot(centerB[0] - camera.eye[0], centerB[1] - camera.eye[1], centerB[2] - camera.eye[2]) -
        Math.hypot(centerA[0] - camera.eye[0], centerA[1] - camera.eye[1], centerA[2] - camera.eye[2]);
    });
    gl.useProgram(this.surfaceProgram);
    const colorLocation = gl.getUniformLocation(this.surfaceProgram, "u_color");
    const selectedColor: [number, number, number] = [0.10, 0.50, 0.39];
    for (const gpu of opaque) {
      this.bindMesh(gpu, this.surfaceProgram, camera.mvp, camera.view);
      const color = this.selectedIds.has(gpu.mesh.meshAssetId) ? selectedColor : gpu.color;
      if (colorLocation) gl.uniform4f(colorLocation, color[0], color[1], color[2], 1);
      gl.drawElements(gl.TRIANGLES, gpu.count, gpu.indexType, 0);
    }
    if (orderedTransparent.length > 0) {
      gl.enable(gl.BLEND);
      gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA);
      gl.depthMask(false);
      for (const gpu of orderedTransparent) {
        this.bindMesh(gpu, this.surfaceProgram, camera.mvp, camera.view);
        const color = this.selectedIds.has(gpu.mesh.meshAssetId) ? selectedColor : gpu.color;
        if (colorLocation) gl.uniform4f(colorLocation, color[0], color[1], color[2], 0.20);
        gl.drawElements(gl.TRIANGLES, gpu.count, gpu.indexType, 0);
      }
      gl.depthMask(true);
      gl.disable(gl.BLEND);
    }
    this.onFrame?.();
  }

  private pick(event: PointerEvent): void {
    const rect = this.canvas.getBoundingClientRect();
    const x = Math.floor((event.clientX - rect.left) * this.canvas.width / Math.max(1, rect.width));
    const y = this.canvas.height - 1 - Math.floor((event.clientY - rect.top) * this.canvas.height / Math.max(1, rect.height));
    if (x < 0 || y < 0 || x >= this.canvas.width || y >= this.canvas.height) return;
    const gl = this.gl;
    this.resize();
    const camera = this.camera();
    gl.disable(gl.BLEND);
    gl.depthMask(true);
    gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);
    gl.useProgram(this.pickProgram);
    const pickColorLocation = gl.getUniformLocation(this.pickProgram, "u_pick_color");
    const available = this.availableMeshes(false);
    available.forEach((gpu) => {
      const number = [...this.meshes.keys()].indexOf(gpu.mesh.meshAssetId) + 1;
      this.bindMesh(gpu, this.pickProgram, camera.mvp);
      if (pickColorLocation) gl.uniform4f(pickColorLocation, (number & 255) / 255, ((number >> 8) & 255) / 255, ((number >> 16) & 255) / 255, 1);
      gl.drawElements(gl.TRIANGLES, gpu.count, gpu.indexType, 0);
    });
    const pixel = new Uint8Array(4);
    gl.readPixels(x, y, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, pixel);
    const index = pixel[0] + pixel[1] * 256 + pixel[2] * 65536 - 1;
    const mesh = index >= 0 ? [...this.meshes.values()][index]?.mesh : undefined;
    this.render();
    if (mesh && this.availableMeshes(false).some((gpu) => gpu.mesh.meshAssetId === mesh.meshAssetId)) {
      if (this.onAnnotationPick) {
        const hit = this.raycastMesh(event, mesh);
        if (hit) this.onAnnotationPick(hit);
      } else {
        this.onPick(mesh);
      }
    }
  }

  private raycastMesh(event: PointerEvent, mesh: ViewerMesh): AnnotationSurfaceHit | null {
    const rect = this.canvas.getBoundingClientRect();
    const ndcX = ((event.clientX - rect.left) / Math.max(1, rect.width)) * 2 - 1;
    const ndcY = 1 - ((event.clientY - rect.top) / Math.max(1, rect.height)) * 2;
    const { eye } = this.camera();
    const forward = normalize(subtract(this.center, eye));
    const right = normalize(cross(forward, [0, 1, 0]));
    const screenUp = cross(right, forward);
    const halfHeight = Math.tan(Math.PI / 8);
    const aspect = this.canvas.width / Math.max(1, this.canvas.height);
    const direction = normalize([
      forward[0] + right[0] * ndcX * halfHeight * aspect + screenUp[0] * ndcY * halfHeight,
      forward[1] + right[1] * ndcX * halfHeight * aspect + screenUp[1] * ndcY * halfHeight,
      forward[2] + right[2] * ndcX * halfHeight * aspect + screenUp[2] * ndcY * halfHeight,
    ]);
    let nearestDistance = Infinity;
    let result: AnnotationSurfaceHit | null = null;
    const indices = mesh.indices;
    const positions = mesh.positions;
    for (let offset = 0; offset < indices.length; offset += 3) {
      const i0 = indices[offset] * 3;
      const i1 = indices[offset + 1] * 3;
      const i2 = indices[offset + 2] * 3;
      const v0: Vec3 = [positions[i0], positions[i0 + 1], positions[i0 + 2]];
      const v1: Vec3 = [positions[i1], positions[i1 + 1], positions[i1 + 2]];
      const v2: Vec3 = [positions[i2], positions[i2 + 1], positions[i2 + 2]];
      const edge1 = subtract(v1, v0);
      const edge2 = subtract(v2, v0);
      const p = cross(direction, edge2);
      const determinant = dot(edge1, p);
      if (Math.abs(determinant) < 1e-10) continue;
      const inverse = 1 / determinant;
      const fromVertex = subtract(eye, v0);
      const u = inverse * dot(fromVertex, p);
      if (u < 0 || u > 1) continue;
      const q = cross(fromVertex, edge1);
      const v = inverse * dot(direction, q);
      if (v < 0 || u + v > 1) continue;
      const distance = inverse * dot(edge2, q);
      if (distance <= 0 || distance >= nearestDistance) continue;
      nearestDistance = distance;
      result = {
        mesh,
        triangleId: offset / 3,
        position: [eye[0] + direction[0] * distance, eye[1] + direction[1] * distance, eye[2] + direction[2] * distance],
        barycentric: [1 - u - v, u, v],
      };
    }
    return result;
  }

  private handlePointerDown(event: PointerEvent): void {
    if (event.button !== 0) return;
    this.lastPointer = { id: event.pointerId, x: event.clientX, y: event.clientY, startX: event.clientX, startY: event.clientY };
    this.dragged = false;
    this.canvas.setPointerCapture(event.pointerId);
  }

  private handlePointerMove(event: PointerEvent): void {
    if (!this.lastPointer || this.lastPointer.id !== event.pointerId) return;
    const deltaX = event.clientX - this.lastPointer.x;
    const deltaY = event.clientY - this.lastPointer.y;
    if (Math.hypot(event.clientX - this.lastPointer.startX, event.clientY - this.lastPointer.startY) > 4) this.dragged = true;
    if (this.dragged) {
      this.yaw -= deltaX * 0.008;
      this.pitch = Math.min(1.48, Math.max(-1.48, this.pitch + deltaY * 0.008));
      this.render();
    }
    this.lastPointer.x = event.clientX;
    this.lastPointer.y = event.clientY;
  }

  private handlePointerUp(event: PointerEvent): void {
    if (!this.lastPointer || this.lastPointer.id !== event.pointerId) return;
    if (!this.dragged) this.pick(event);
    this.lastPointer = null;
  }

  private handleWheel(event: WheelEvent): void {
    event.preventDefault();
    this.distance = Math.max(0.06, Math.min(12, this.distance * Math.exp(event.deltaY * 0.001)));
    this.render();
  }

  private handleKeyDown(event: KeyboardEvent): void {
    if (event.key === "Home") {
      event.preventDefault();
      this.fitAll();
    } else if (event.key === "ArrowLeft" || event.key === "ArrowRight") {
      event.preventDefault();
      this.yaw += event.key === "ArrowLeft" ? -0.12 : 0.12;
      this.render();
    } else if (event.key === "ArrowUp" || event.key === "ArrowDown") {
      event.preventDefault();
      this.pitch = Math.max(-1.48, Math.min(1.48, this.pitch + (event.key === "ArrowUp" ? 0.12 : -0.12)));
      this.render();
    }
  }
}
