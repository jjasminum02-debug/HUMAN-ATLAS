import * as THREE from "./vendor/three/build/three.module.js";
import { GLTFLoader } from "./vendor/three/examples/jsm/loaders/GLTFLoader.js";

const EXPECTED = ["FJ3274", "FJ3386", "FJ3281", "FJ3392", "FJ3287", "FJ3375", "FJ3269", "FJ3378", "FJ3272"];
const CONTEXT = new Set(["FJ3380", "FJ3200", "FJ3289", "FJ3309"]);
const FRAME = "HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR";
const POSE = "bodyparts3d-r4-static-reference";
const canvas = document.querySelector("#canvas");
const status = document.querySelector("#status");
const list = document.querySelector("#list");
const selectedLabel = document.querySelector("#selected");
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: false });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.setClearColor(0x10151b, 1);
renderer.outputColorSpace = THREE.SRGBColorSpace;
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x10151b);
const camera = new THREE.PerspectiveCamera(35, 1, 0.01, 30);
const root = new THREE.Group();
root.name = "AnatomySceneRoot";
scene.add(root);
scene.add(new THREE.HemisphereLight(0xe7f1ff, 0x34404b, 1.8));
const key = new THREE.DirectionalLight(0xffffff, 2.1);
key.position.set(1.6, 2.2, 2.5);
scene.add(key);
const fill = new THREE.DirectionalLight(0xa9caff, 1.0);
fill.position.set(-2, 1, -1.6);
scene.add(fill);

const loader = new GLTFLoader();
const targets = [];
const meshes = new Map();
const materials = new Map();
let selectedIndex = -1;
let center = new THREE.Vector3();
let distance = 1;
let wholeBounds = new THREE.Box3();
const proof = window.t74QaProof = {
  loaded: false, rendererCount: 1, rootName: root.name, rootCount: 1, canvasCount: 1,
  packages: [], visibleSourceIds: [], targetCount: 0, views: [], selections: [],
  consoleErrors: [], frame: FRAME, pose: POSE, recentring: false, mirroring: false,
};
window.addEventListener("error", e => {
  proof.consoleErrors.push(String(e.message));
  document.body.dataset.consoleErrorCount = String(proof.consoleErrors.length);
});

const sources = [
  { package: "T52", path: "./assets/T52-B09.glb", allowed: new Set(["FJ3380"]), role: "reuse" },
  { package: "T72", path: "./assets/T72-first-pass-residual-static-source.glb", allowed: new Set(["FJ3200", "FJ3289", "FJ3309"]), role: "reuse" },
  { package: "T74", path: "./assets/T74-bilateral-skull-static-source.glb", allowed: new Set(EXPECTED), role: "target" },
];

function sourceId(object) {
  const extras = object.userData ?? {};
  if (typeof extras.sourceElementFileId === "string") return extras.sourceElementFileId;
  const match = /^HA-MESH-BP3D4-(FJ\d+)$/.exec(object.name ?? "");
  return match?.[1] ?? null;
}

function render() {
  const width = canvas.clientWidth, height = canvas.clientHeight;
  if (!width || !height) return;
  renderer.setSize(width, height, false);
  camera.aspect = width / height;
  camera.updateProjectionMatrix();
  renderer.render(scene, camera);
  document.body.dataset.canvasSize = `${width}x${height}`;
  document.body.dataset.lastRender = "true";
}

function face(view) {
  const directions = {
    front: new THREE.Vector3(0, 0.08, 1),
    back: new THREE.Vector3(0, 0.08, -1),
    side: new THREE.Vector3(1, 0.08, 0),
  };
  camera.position.copy(center).addScaledVector(directions[view], distance);
  camera.up.set(0, 1, 0);
  camera.lookAt(center);
  document.body.dataset.cameraView = view;
  for (const button of document.querySelectorAll("[data-view]")) button.setAttribute("aria-pressed", String(button.dataset.view === view));
  proof.views.push({ view, canvasSize: document.body.dataset.canvasSize ?? null });
  document.body.dataset.viewHistory = proof.views.map(row => row.view).join(",");
  render();
}

function focus(object) {
  const box = new THREE.Box3().setFromObject(object);
  center = box.getCenter(new THREE.Vector3());
  const size = box.getSize(new THREE.Vector3());
  distance = Math.max(size.x, size.y, size.z) * 2.2 + 0.05;
}

function fitAll() {
  center = wholeBounds.getCenter(new THREE.Vector3());
  const size = wholeBounds.getSize(new THREE.Vector3());
  distance = Math.max(size.x, size.y, size.z) * 1.75;
  face("front");
  document.body.dataset.focus = "all";
}

function select(index) {
  if (!targets.length) return;
  if (selectedIndex >= 0) {
    const previous = targets[selectedIndex];
    previous.mesh.material = materials.get(previous.mesh);
  }
  selectedIndex = (index + targets.length) % targets.length;
  const row = targets[selectedIndex];
  row.mesh.material = new THREE.MeshStandardMaterial({ color: 0xffcf58, roughness: 0.68, side: THREE.DoubleSide });
  selectedLabel.textContent = `${row.sourceElementFileId} · ${row.sourceNameEnglishExactHeader}\nFMA ${row.sourceFmaConceptId} · BP ${row.sourceRepresentationId} · ${row.explicitSourceSide}\nsource-only · learner default hidden`;
  for (const button of list.querySelectorAll("button")) button.setAttribute("aria-pressed", String(button.dataset.id === row.sourceElementFileId));
  document.body.dataset.selectedSourceId = row.sourceElementFileId;
  document.body.dataset.focus = row.sourceElementFileId;
  proof.selections.push({ sourceElementFileId: row.sourceElementFileId, stableMeshAssetId: row.stableMeshAssetId, highlightApplied: true, frameUnchanged: true });
  face(document.body.dataset.cameraView ?? "front");
}

function load(path) {
  return new Promise((resolve, reject) => loader.load(path, resolve, undefined, reject));
}

for (const button of document.querySelectorAll("[data-view]")) button.addEventListener("click", () => face(button.dataset.view));
document.querySelector("#fit").addEventListener("click", fitAll);
document.addEventListener("keydown", event => {
  if (event.key === "ArrowDown") { event.preventDefault(); select(selectedIndex + 1); }
  else if (event.key === "ArrowUp") { event.preventDefault(); select(selectedIndex < 0 ? targets.length - 1 : selectedIndex - 1); }
  else if (event.key === "1") face("front");
  else if (event.key === "2") face("back");
  else if (event.key === "3") face("side");
  else if (event.key === "Escape") fitAll();
});
new ResizeObserver(render).observe(document.querySelector("#stage"));
window.addEventListener("resize", render);

async function main() {
  let totalMeshes = 0;
  for (const source of sources) {
    const gltf = await load(source.path);
    const extras = gltf.parser.json.extras ?? {};
    if (extras.frame !== FRAME || extras.pose !== POSE) throw new Error(`${source.package} frame/pose mismatch`);
    const accepted = [];
    for (const node of [...gltf.scene.children]) {
      const id = sourceId(node);
      if (!id || !source.allowed.has(id)) { gltf.scene.remove(node); continue; }
      const object = node;
      if (!object.isMesh) throw new Error(`${source.package} source node is not a direct mesh: ${id}`);
      accepted.push({ id, object, data: object.userData ?? {} });
      totalMeshes += 1;
    }
    if (accepted.length !== source.allowed.size) throw new Error(`${source.package} selected ID count differs from reuse/target allowlist`);
    root.add(gltf.scene);
    for (const entry of accepted) {
      const { id, object, data } = entry;
      const material = new THREE.MeshStandardMaterial({ color: source.role === "target" ? 0x82bfd4 : 0xb39a80, roughness: 0.82, side: THREE.DoubleSide });
      object.material = material;
      materials.set(object, material);
      meshes.set(id, object);
      proof.visibleSourceIds.push(id);
      if (source.role === "target") targets.push({ ...data, sourceElementFileId: id, mesh: object });
    }
    proof.packages.push({ package: source.package, path: source.path, frame: extras.frame, pose: extras.pose, acceptedIds: accepted.map(row => row.id), nodeCount: accepted.length });
  }
  targets.sort((a, b) => a.sourceElementFileId.localeCompare(b.sourceElementFileId));
  if (targets.map(row => row.sourceElementFileId).sort().join(",") !== [...EXPECTED].sort().join(",")) throw new Error("T74 exact target ID set mismatch");
  for (const row of targets) {
    const button = document.createElement("button");
    button.type = "button";
    button.dataset.id = row.sourceElementFileId;
    button.textContent = `${row.sourceNameEnglishExactHeader} · ${row.sourceElementFileId}`;
    button.addEventListener("click", () => select(targets.indexOf(row)));
    list.append(button);
  }
  if (proof.visibleSourceIds.length !== 13 || new Set(proof.visibleSourceIds).size !== 13) throw new Error("expected 9 T74 targets plus 4 unique reuse meshes in shared QA root");
  wholeBounds.setFromObject(root);
  proof.loaded = true;
  proof.targetCount = targets.length;
  proof.meshNodeCount = totalMeshes;
  proof.rootChildCount = root.children.length;
  proof.visibleSourceIds.sort();
  proof.sceneBoundsM = { min: wholeBounds.min.toArray(), max: wholeBounds.max.toArray() };
  document.body.dataset.loaded = "true";
  document.body.dataset.rendererCount = "1";
  document.body.dataset.rootCount = String(scene.children.filter(item => item.name === "AnatomySceneRoot").length);
  document.body.dataset.targetCount = String(targets.length);
  document.body.dataset.meshNodeCount = String(totalMeshes);
  document.body.dataset.frame = FRAME;
  document.body.dataset.pose = POSE;
  document.body.dataset.consoleErrorCount = String(proof.consoleErrors.length);
  document.body.dataset.visibleSourceIds = proof.visibleSourceIds.join(",");
  document.body.dataset.targetSourceIds = EXPECTED.join(",");
  document.body.dataset.rootChildCount = String(proof.rootChildCount);
  document.body.dataset.reuseMeshCount = String(proof.visibleSourceIds.length - targets.length);
  status.textContent = `${totalMeshes} same-frame source meshes · 9 T74 targets · 4 reuse context · internal QA`;
  fitAll();
  select(0);
  window.dispatchEvent(new Event("t74-qa-ready"));
}

main().catch(error => {
  status.textContent = `QA load failed: ${String(error)}`;
  console.error(error);
  proof.consoleErrors.push(String(error));
  document.body.dataset.consoleErrorCount = String(proof.consoleErrors.length);
});
