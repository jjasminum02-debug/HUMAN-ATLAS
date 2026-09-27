import * as THREE from "../../../atlas-web/node_modules/three/build/three.module.js";
import { GLTFLoader } from "../../../atlas-web/node_modules/three/examples/jsm/loaders/GLTFLoader.js";

const canvas = document.querySelector("#canvas");
const status = document.querySelector("#status");
const list = document.querySelector("#list");
const selected = document.querySelector("#selected");
const regionSelect = document.querySelector("#region");
const filter = document.querySelector("#filter");
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: false });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.setClearColor(0x111922, 1);
renderer.outputColorSpace = THREE.SRGBColorSpace;
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x111922);
const camera = new THREE.PerspectiveCamera(35, 1, 0.01, 30);
const anatomySceneRoot = new THREE.Group();
anatomySceneRoot.name = "AnatomySceneRoot";
scene.add(anatomySceneRoot);
scene.add(new THREE.HemisphereLight(0xdceeff, 0x35414b, 2.0));
const keyLight = new THREE.DirectionalLight(0xffffff, 2.4);
keyLight.position.set(1.5, 2.0, 2.6);
scene.add(keyLight);
const fillLight = new THREE.DirectionalLight(0xa9caff, 1.2);
fillLight.position.set(-2.2, 1.0, -1.6);
scene.add(fillLight);
const pick = new THREE.Raycaster();
const pointer = new THREE.Vector2();
let meshRows = [];
let selectedMesh = null;
let center = new THREE.Vector3();
let cameraDistance = 1.7;
let currentView = "front";
const originalMaterials = new Map();

function label(row) {
  return `${row.sourceElementFileId} · ${row.sourceName ?? "source name missing"} · ${row.lateralityFromExactSourceHeader}`;
}

function render() {
  const width = canvas.clientWidth;
  const height = canvas.clientHeight;
  if (!width || !height) return;
  renderer.setSize(width, height, false);
  camera.aspect = width / height;
  camera.updateProjectionMatrix();
  renderer.render(scene, camera);
}

function face(view) {
  currentView = view;
  document.body.dataset.cameraView = view;
  const dirs = { front: new THREE.Vector3(0, 0.13, 1), back: new THREE.Vector3(0, 0.13, -1), side: new THREE.Vector3(1, 0.13, 0) };
  camera.position.copy(center).addScaledVector(dirs[view], cameraDistance);
  camera.lookAt(center);
  for (const button of document.querySelectorAll("[data-view]")) button.setAttribute("aria-pressed", String(button.dataset.view === view));
  render();
}

function drawList() {
  const q = filter.value.trim().toLowerCase();
  list.replaceChildren();
  for (const row of meshRows) {
    const extras = row.mesh.userData.source;
    const searchable = `${extras.sourceElementFileId} ${extras.sourceName ?? ""} ${extras.sourceIdentityState}`.toLowerCase();
    if (regionSelect.value !== "all" && !extras.regionMemberships.includes(regionSelect.value)) continue;
    if (q && !searchable.includes(q)) continue;
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = label(extras);
    button.addEventListener("click", () => selectMesh(row.mesh));
    list.append(button);
  }
}

function selectMesh(mesh) {
  if (selectedMesh && originalMaterials.has(selectedMesh)) selectedMesh.material = originalMaterials.get(selectedMesh);
  selectedMesh = mesh;
  const source = mesh.userData.source;
  mesh.material = new THREE.MeshStandardMaterial({ color: 0xffde59, roughness: 0.68, metalness: 0.0, side: THREE.DoubleSide });
  selected.textContent = `${source.sourceElementFileId}\n${source.sourceIdentityState}\n이름: ${source.sourceName ?? "미확인(원본 header blank)"}\n좌우: ${source.lateralityFromExactSourceHeader}\n지역: ${source.regionMemberships.join(", ")}\nBone/Muscle context: ${Object.entries(source.regionContextKinds).filter(([, value]) => value.boneContext || value.muscleContext).map(([key, value]) => `${key}:${value.boneContext ? "bone" : ""}${value.muscleContext ? " muscle" : ""}`).join("; ")}`;
  document.querySelectorAll("#list button").forEach(button => button.setAttribute("aria-pressed", String(button.textContent.startsWith(source.sourceElementFileId))));
  window.t53QaProof.selection = { sourceElementFileId: source.sourceElementFileId, stableMeshAssetId: source.stableMeshAssetId, view: currentView, oneRoot: scene.children.filter(x => x.name === "AnatomySceneRoot").length === 1 };
  document.body.dataset.selectedSourceId = source.sourceElementFileId;
  render();
}

function resize() { render(); }
new ResizeObserver(resize).observe(document.querySelector("#stage"));
window.addEventListener("resize", resize);

for (const button of document.querySelectorAll("[data-view]")) button.addEventListener("click", () => face(button.dataset.view));
document.querySelector("#showAll").addEventListener("click", () => { regionSelect.value = "all"; regionSelect.dispatchEvent(new Event("change")); });
filter.addEventListener("input", drawList);
regionSelect.addEventListener("change", () => {
  const region = regionSelect.value;
  if (selectedMesh && originalMaterials.has(selectedMesh)) selectedMesh.material = originalMaterials.get(selectedMesh);
  for (const { mesh } of meshRows) mesh.visible = region === "all" || mesh.userData.source.regionMemberships.includes(region);
  selected.textContent = "지역 필터만 변경 · source node ID 및 scene root 유지";
  selectedMesh = null;
  delete document.body.dataset.selectedSourceId;
  drawList();
  window.t53QaProof.lastRegionFilter = region;
  document.body.dataset.regionFilter = region;
  document.body.dataset.visibleMeshCount = String(meshRows.filter(row => row.mesh.visible).length);
  status.textContent = `읽음 · ${meshRows.length} unique source mesh · ${document.body.dataset.visibleMeshCount} visible · 1 renderer · 1 AnatomySceneRoot · ${region} filter · static QA`;
  render();
});
canvas.addEventListener("pointerdown", event => {
  const rect = canvas.getBoundingClientRect();
  pointer.set(((event.clientX - rect.left) / rect.width) * 2 - 1, -((event.clientY - rect.top) / rect.height) * 2 + 1);
  pick.setFromCamera(pointer, camera);
  const hits = pick.intersectObjects(meshRows.filter(row => row.mesh.visible).map(row => row.mesh), false);
  if (hits[0]) selectMesh(hits[0].object);
});

window.t53QaProof = { rendererCount: 1, rootName: anatomySceneRoot.name, rootCount: 1, meshCount: 0, loaded: false, views: [], selection: null, canvasCount: document.querySelectorAll("canvas").length };
new GLTFLoader().load("../../../atlas-data/source-cache/bodyparts3d-r4/converted/t53/T53-trunk-pelvis-static-source.glb", gltf => {
  anatomySceneRoot.add(gltf.scene);
  const box = new THREE.Box3().setFromObject(anatomySceneRoot);
  center = box.getCenter(new THREE.Vector3());
  anatomySceneRoot.position.sub(center);
  center.set(0, 0, 0);
  const size = box.getSize(new THREE.Vector3());
  cameraDistance = Math.max(size.y, size.x) * 1.9;
  gltf.scene.traverse(object => {
    if (!object.isMesh) return;
    const source = object.userData.sourceElementFileId ? object.userData : object.parent?.userData;
    object.userData.source = source;
    const bone = Object.values(source.regionContextKinds ?? {}).some(value => value.boneContext);
    const color = bone ? 0x9db6d1 : 0xc58e82;
    const material = new THREE.MeshStandardMaterial({ color, roughness: 0.88, metalness: 0.0, side: THREE.DoubleSide });
    object.material = material;
    originalMaterials.set(object, material);
    meshRows.push({ mesh: object });
  });
  drawList();
  face("front");
  const glbExtras = gltf.parser.json.extras;
  window.t53QaProof = { ...window.t53QaProof, loaded: true, rootName: anatomySceneRoot.name, rootCount: scene.children.filter(x => x.name === "AnatomySceneRoot").length, meshCount: meshRows.length, canvasCount: document.querySelectorAll("canvas").length, frame: glbExtras.frame, pose: glbExtras.pose, sceneBoundsM: { min: box.min.toArray(), max: box.max.toArray() }, glbAssetNodeCount: gltf.scene.children.length };
  document.body.dataset.loaded = "true";
  document.body.dataset.canvasCount = String(document.querySelectorAll("canvas").length);
  document.body.dataset.rootCount = String(scene.children.filter(x => x.name === "AnatomySceneRoot").length);
  document.body.dataset.meshCount = String(meshRows.length);
  document.body.dataset.visibleMeshCount = String(meshRows.filter(row => row.mesh.visible).length);
  document.body.dataset.frame = glbExtras.frame;
  document.body.dataset.pose = glbExtras.pose;
  status.textContent = `읽음 · ${meshRows.length} unique source mesh · 1 renderer · 1 AnatomySceneRoot · 5 frozen region filters · static QA only`;
  render();
}, undefined, error => { status.textContent = `GLB load failed: ${String(error)}`; console.error(error); });
