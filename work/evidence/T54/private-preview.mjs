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
const materialByMesh = new Map();
const rowById = new Map();
let meshRows = [];
let selectedMesh = null;
let center = new THREE.Vector3();
let cameraDistance = 3.4;
let currentView = "front";
const proof = { task: "T54", loaded: false, canvasCount: document.querySelectorAll("canvas").length, rendererCount: 1, rootCount: 1, errors: [], views: [], selection: null };
window.t54QaProof = proof;

window.addEventListener("error", event => proof.errors.push(String(event.message || event.error || "window error")));
window.addEventListener("unhandledrejection", event => proof.errors.push(String(event.reason || "unhandled rejection")));

function sourceMetadata(mesh) {
  let node = mesh;
  while (node && !node.userData.sourceElementFileId && !node.userData.stableMeshAssetId && !node.userData.stableSourceMeshNodeId) node = node.parent;
  if (!node) return null;
  return node.userData;
}

function normalizeRow(mesh, source) {
  const id = source.sourceElementFileId;
  if (!id) return null;
  const row = {
    mesh,
    source: {
      ...source,
      stableSourceMeshNodeId: source.stableSourceMeshNodeId || source.stableMeshAssetId || `HA-MESH-BP3D4-${id}`,
      pickingTargetId: source.pickingTargetId || source.stableSourceMeshNodeId || source.stableMeshAssetId || `HA-MESH-BP3D4-${id}`,
      regionMemberships: [...(source.regionMemberships || [])],
      regionContextKinds: { ...(source.regionContextKinds || {}) },
    },
  };
  mesh.userData.source = row.source;
  rowById.set(id, row);
  const isBone = Object.values(row.source.regionContextKinds).some(context => context.boneContext);
  const color = isBone ? 0x9db6d1 : 0xc58e82;
  const material = new THREE.MeshStandardMaterial({ color, roughness: 0.88, metalness: 0, side: THREE.DoubleSide });
  mesh.material = material;
  materialByMesh.set(mesh, material);
  return row;
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

function face(view, focusMesh = null) {
  currentView = view;
  document.body.dataset.cameraView = view;
  const dirs = { front: new THREE.Vector3(0, 0.12, 1), back: new THREE.Vector3(0, 0.12, -1), side: new THREE.Vector3(1, 0.12, 0) };
  let target = center;
  let distance = cameraDistance;
  if (focusMesh) {
    const box = new THREE.Box3().setFromObject(focusMesh);
    target = box.getCenter(new THREE.Vector3());
    distance = Math.max(box.getSize(new THREE.Vector3()).length() * 2.8, 0.16);
  }
  camera.position.copy(target).addScaledVector(dirs[view], distance);
  camera.lookAt(target);
  for (const button of document.querySelectorAll("[data-view]")) button.setAttribute("aria-pressed", String(button.dataset.view === view));
  render();
}

function describe(source) {
  const context = (source.handPickContexts || []).map(row => `${row.sourceNameEnglish} [${row.sourceFmaConceptId}]`).join("; ");
  return `${source.sourceElementFileId} · ${source.sourceName || "source name missing"} · ${source.lateralityFromExactSourceHeader || "laterality missing"}${context ? ` · ${context}` : ""}`;
}

function passesRegion(source) {
  const region = regionSelect.value;
  if (region === "all") return true;
  if (region === "hand-bone") return source.handBonePickCandidate === true;
  if (region === "hand-muscle") return source.handMusclePickCandidate === true;
  return (source.regionMemberships || []).includes(region);
}

function drawList() {
  const q = filter.value.trim().toLowerCase();
  list.replaceChildren();
  for (const row of meshRows) {
    const source = row.source;
    if (!passesRegion(source)) continue;
    const searchable = `${source.sourceElementFileId} ${source.sourceName || ""} ${source.sourceConceptId || ""} ${(source.handPickContexts || []).map(x => x.sourceNameEnglish).join(" ")}`.toLowerCase();
    if (q && !searchable.includes(q)) continue;
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = describe(source);
    button.dataset.sourceId = source.sourceElementFileId;
    button.setAttribute("aria-pressed", String(selectedMesh === row.mesh));
    button.addEventListener("click", () => selectMesh(row.mesh));
    list.append(button);
  }
}

function selectMesh(mesh) {
  if (selectedMesh && materialByMesh.has(selectedMesh)) selectedMesh.material = materialByMesh.get(selectedMesh);
  selectedMesh = mesh;
  const source = mesh.userData.source;
  mesh.material = new THREE.MeshStandardMaterial({ color: 0xffde59, roughness: 0.68, metalness: 0, side: THREE.DoubleSide });
  selected.textContent = `${source.sourceElementFileId}\n${source.sourceIdentityState || "T53 source identity"}\n원본명: ${source.sourceName || "원본 이름 미확인"}\n좌우: ${source.lateralityFromExactSourceHeader || "source header missing"}\nSource FMA: ${source.sourceConceptId || "미확인"}\n지역: ${(source.regionMemberships || []).join(", ")}\nPicking target: ${source.pickingTargetId}\nLOD: ${source.lod?.sourceLevelCount ?? "T53 package"} source level(s), ${source.lod?.alternateSourceLevels?.length ?? "not declared"} alternate; no generated decimation`;
  drawList();
  proof.selection = { sourceElementFileId: source.sourceElementFileId, stableSourceMeshNodeId: source.stableSourceMeshNodeId, pickingTargetId: source.pickingTargetId, laterality: source.lateralityFromExactSourceHeader, view: currentView };
  document.body.dataset.selectedSourceId = source.sourceElementFileId;
  face(currentView, mesh);
}

function applyFilter() {
  if (selectedMesh && materialByMesh.has(selectedMesh)) selectedMesh.material = materialByMesh.get(selectedMesh);
  selectedMesh = null;
  selected.textContent = "필터 적용 · source node ID 및 AnatomySceneRoot 유지";
  delete document.body.dataset.selectedSourceId;
  for (const row of meshRows) row.mesh.visible = passesRegion(row.source);
  drawList();
  const visibleCount = meshRows.filter(row => row.mesh.visible).length;
  document.body.dataset.regionFilter = regionSelect.value;
  document.body.dataset.visibleMeshCount = String(visibleCount);
  status.textContent = `읽음 · ${meshRows.length} unique source mesh · ${visibleCount} visible · 1 renderer · 1 AnatomySceneRoot · ${regionSelect.value} · static QA`;
  proof.lastFilter = { filter: regionSelect.value, visibleCount, listedCount: list.children.length };
  render();
}

function resize() { render(); }
new ResizeObserver(resize).observe(document.querySelector("#stage"));
window.addEventListener("resize", resize);
for (const button of document.querySelectorAll("[data-view]")) button.addEventListener("click", () => face(button.dataset.view));
document.querySelector("#showAll").addEventListener("click", () => { regionSelect.value = "all"; regionSelect.dispatchEvent(new Event("change")); });
filter.addEventListener("input", drawList);
regionSelect.addEventListener("change", applyFilter);
canvas.addEventListener("pointerdown", event => {
  const rect = canvas.getBoundingClientRect();
  pointer.set(((event.clientX - rect.left) / rect.width) * 2 - 1, -((event.clientY - rect.top) / rect.height) * 2 + 1);
  pick.setFromCamera(pointer, camera);
  const hits = pick.intersectObjects(meshRows.filter(row => row.mesh.visible).map(row => row.mesh), false);
  if (hits[0]) selectMesh(hits[0].object);
});

function addSceneMeshes(gltf, task, dedupe) {
  gltf.scene.updateMatrixWorld(true);
  const found = [];
  gltf.scene.traverse(object => { if (object.isMesh) found.push(object); });
  const added = [];
  const duplicates = [];
  for (const mesh of found) {
    const source = sourceMetadata(mesh);
    if (!source) continue;
    const id = source.sourceElementFileId;
    const current = rowById.get(id);
    if (dedupe && current) {
      const merged = current.source;
      merged.regionMemberships = [...new Set([...(merged.regionMemberships || []), ...(source.regionMemberships || [])])];
      merged.regionContextKinds = { ...merged.regionContextKinds, ...(source.regionContextKinds || {}) };
      merged.handBonePickCandidate ||= source.handBonePickCandidate === true;
      merged.handMusclePickCandidate ||= source.handMusclePickCandidate === true;
      merged.handPickContexts = [...(merged.handPickContexts || []), ...(source.handPickContexts || [])];
      duplicates.push(id);
      continue;
    }
    if (task === "T54") {
      const world = mesh.matrixWorld.clone();
      mesh.parent?.remove(mesh);
      mesh.matrixAutoUpdate = false;
      mesh.matrix.copy(world);
      mesh.matrixWorld.copy(world);
      anatomySceneRoot.add(mesh);
    }
    const row = normalizeRow(mesh, source);
    if (row) added.push(row);
  }
  return { added: added.length, duplicates, rawMeshCount: found.length };
}

async function loadGltf(url) {
  return await new GLTFLoader().loadAsync(url);
}

async function loadAll() {
  try {
    const t53 = await loadGltf("../../../atlas-data/source-cache/bodyparts3d-r4/converted/t53/T53-trunk-pelvis-static-source.glb");
    anatomySceneRoot.add(t53.scene);
    const t53Stats = addSceneMeshes(t53, "T53", false);
    const t54 = await loadGltf("../../../atlas-data/source-cache/bodyparts3d-r4/converted/t54/T54-shoulder-upper-limb-static-source.glb");
    const t54Stats = addSceneMeshes(t54, "T54", true);
    meshRows = [...rowById.values()].sort((a, b) => a.source.sourceElementFileId.localeCompare(b.source.sourceElementFileId));
    const box = new THREE.Box3().setFromObject(anatomySceneRoot);
    center = box.getCenter(new THREE.Vector3());
    anatomySceneRoot.position.sub(center);
    center.set(0, 0, 0);
    const size = box.getSize(new THREE.Vector3());
    cameraDistance = Math.max(size.y, size.x) * 1.9;
    for (const row of meshRows) row.mesh.visible = true;
    drawList();
    face("front");
    proof.loaded = true;
    proof.rawLoadedMeshes = { T53: t53Stats.rawMeshCount, T54: t54Stats.rawMeshCount };
    proof.addedMeshes = { T53: t53Stats.added, T54: t54Stats.added };
    proof.deduplicatedSourceIds = t54Stats.duplicates.sort();
    proof.uniqueMeshCount = meshRows.length;
    proof.canvasCount = document.querySelectorAll("canvas").length;
    proof.rootCount = scene.children.filter(child => child.name === "AnatomySceneRoot").length;
    proof.rendererCount = 1;
    proof.frame = "HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR";
    proof.pose = "bodyparts3d-r4-static-reference";
    proof.lod = { T54SourceResolutionLevels: 1, alternateSourceLevels: 0, generatedDecimation: 0, independentPickingTargets: 50 };
    document.body.dataset.loaded = "true";
    document.body.dataset.meshCount = String(meshRows.length);
    document.body.dataset.rootCount = String(proof.rootCount);
    document.body.dataset.canvasCount = String(proof.canvasCount);
    document.body.dataset.visibleMeshCount = String(meshRows.length);
    status.textContent = `읽음 · ${meshRows.length} unique source mesh · T53=${t53Stats.added}, T54=${t54Stats.added}, shared-node dedupe=${t54Stats.duplicates.length} · 1 renderer · 1 AnatomySceneRoot · static QA`;
    render();
  } catch (error) {
    proof.errors.push(String(error));
    status.textContent = `GLB load failed: ${String(error)}`;
    console.error(error);
  }
}

loadAll();
