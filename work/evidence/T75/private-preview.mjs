import * as THREE from "./vendor/three/build/three.module.js";
import { GLTFLoader } from "./vendor/three/examples/jsm/loaders/GLTFLoader.js";

const EXPECTED = ["FJ1468", "FJ1468M", "FJ1467", "FJ1467M", "FJ1513", "FJ1513M"];
const DUPLICATE_CONTEXT_IDS = new Set(["FJ3237", "FJ3279"]);
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
const camera = new THREE.PerspectiveCamera(32, 1, 0.01, 20);
const root = new THREE.Group();
root.name = "AnatomySceneRoot";
scene.add(root);
scene.add(new THREE.HemisphereLight(0xe7f1ff, 0x34404b, 1.8));
const keyLight = new THREE.DirectionalLight(0xffffff, 2.0);
keyLight.position.set(1.6, 2.2, 2.5);
scene.add(keyLight);
const fillLight = new THREE.DirectionalLight(0xa9caff, 0.9);
fillLight.position.set(-2, 1, -1.6);
scene.add(fillLight);

const proof = window.t75QaProof = {
  loaded: false, rendererCount: 1, rootName: root.name, rootCount: 1, canvasCount: 1,
  packages: [], visibleSourceIds: [], targetSourceIds: [], targetCount: 0,
  duplicateContextIdsSuppressed: [...DUPLICATE_CONTEXT_IDS], views: [], selections: [],
  consoleErrors: [], frame: FRAME, pose: POSE, mirroring: false, recentering: false,
};
window.addEventListener("error", event => {
  proof.consoleErrors.push(String(event.message));
  document.body.dataset.consoleErrorCount = String(proof.consoleErrors.length);
});

const loader = new GLTFLoader();
const targetRows = [];
const materialByMesh = new Map();
const loadedSourceIds = new Set();
let selectedIndex = -1;
let cameraCenter = new THREE.Vector3();
let cameraDistance = 1.3;
let allBounds = new THREE.Box3();
const sources = [
  { package: "T53", path: "./assets/T53-trunk-pelvis-static-source.glb", role: "context", allowedCount: 138, unitEvidence: "T53 source manifest + T50 transform validator" },
  { package: "T54", path: "./assets/T54-shoulder-upper-limb-static-source.glb", role: "context", allowedCount: 142, unitEvidence: "T54 source manifest + T50 transform validator" },
  { package: "T75", path: "./assets/T75-deltoid-bilateral-static-source.glb", role: "target", allowed: new Set(EXPECTED), allowedCount: 6, unitEvidence: "T75 GLB extras + source manifest" },
];

function sourceId(object) {
  const extras = object.userData ?? {};
  if (typeof extras.sourceElementFileId === "string") return extras.sourceElementFileId;
  const match = /^HA-MESH-BP3D4-(FJ[0-9]+M?)$/.exec(object.name ?? "");
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
    front: new THREE.Vector3(0, 0.04, 1),
    back: new THREE.Vector3(0, 0.04, -1),
    side: new THREE.Vector3(1, 0.04, 0),
  };
  camera.position.copy(cameraCenter).addScaledVector(directions[view], cameraDistance);
  camera.up.set(0, 1, 0);
  camera.lookAt(cameraCenter);
  document.body.dataset.cameraView = view;
  for (const button of document.querySelectorAll("[data-view]")) button.setAttribute("aria-pressed", String(button.dataset.view === view));
  proof.views.push({ view, selectedSourceElementFileId: selectedIndex >= 0 ? targetRows[selectedIndex].sourceElementFileId : null, canvasSize: document.body.dataset.canvasSize ?? null });
  document.body.dataset.viewHistory = proof.views.map(row => row.view).join(",");
  render();
}

function focusTarget(row) {
  const box = new THREE.Box3().setFromObject(row.mesh);
  cameraCenter = box.getCenter(new THREE.Vector3());
  const size = box.getSize(new THREE.Vector3());
  cameraDistance = Math.max(size.x, size.y, size.z) * 4.2 + 0.22;
}

function fitAll() {
  cameraCenter = allBounds.getCenter(new THREE.Vector3());
  const size = allBounds.getSize(new THREE.Vector3());
  cameraDistance = Math.max(size.x, size.y, size.z) * 1.7;
  document.body.dataset.focus = "all-source-context";
  face("front");
}

function select(index) {
  if (!targetRows.length) return;
  if (selectedIndex >= 0) {
    const old = targetRows[selectedIndex];
    old.mesh.material = materialByMesh.get(old.mesh);
  }
  selectedIndex = (index + targetRows.length) % targetRows.length;
  const row = targetRows[selectedIndex];
  row.mesh.material = new THREE.MeshStandardMaterial({ color: 0xffcf58, roughness: 0.68, side: THREE.DoubleSide });
  selectedLabel.textContent = `${row.sourceNameEnglishExactHeader}\n${row.sourceFmaConceptId} · ${row.sourceRepresentationId} · ${row.explicitSourceSide} · ${row.sourceDeltoidPart} part\nsource-only · learner default hidden`;
  for (const button of list.querySelectorAll("button")) button.setAttribute("aria-pressed", String(button.dataset.id === row.sourceElementFileId));
  document.body.dataset.selectedSourceId = row.sourceElementFileId;
  document.body.dataset.focus = row.sourceElementFileId;
  proof.selections.push({ sourceElementFileId: row.sourceElementFileId, stableMeshAssetId: row.stableMeshAssetId, highlightApplied: true, frameUnchanged: true });
  focusTarget(row);
  face(document.body.dataset.cameraView ?? "front");
}

function load(path) {
  return new Promise((resolve, reject) => loader.load(path, resolve, undefined, reject));
}

for (const button of document.querySelectorAll("[data-view]")) button.addEventListener("click", () => face(button.dataset.view));
document.querySelector("#fit").addEventListener("click", fitAll);
document.addEventListener("keydown", event => {
  if (event.key === "ArrowDown") { event.preventDefault(); select(selectedIndex + 1); }
  else if (event.key === "ArrowUp") { event.preventDefault(); select(selectedIndex < 0 ? targetRows.length - 1 : selectedIndex - 1); }
  else if (event.key === "1") face("front");
  else if (event.key === "2") face("back");
  else if (event.key === "3") face("side");
  else if (event.key === "Escape") fitAll();
});
new ResizeObserver(render).observe(document.querySelector("#stage"));
window.addEventListener("resize", render);

async function main() {
  let addedCount = 0;
  const packageIdSets = new Map();
  for (const source of sources) {
    const gltf = await load(source.path);
    const extras = gltf.parser.json.extras ?? {};
    if (extras.frame !== FRAME || extras.pose !== POSE || (extras.unit !== undefined && extras.unit !== "m")) throw new Error(`${source.package} frame/pose/unit mismatch`);
    const accepted = [];
    const suppressed = [];
    for (const node of [...gltf.scene.children]) {
      const id = sourceId(node);
      if (!id) throw new Error(`${source.package} node lacks a stable source file ID: ${node.name}`);
      if (source.role === "target" && !source.allowed.has(id)) throw new Error(`unexpected source ID in T75 GLB: ${id}`);
      if (source.package === "T54" && DUPLICATE_CONTEXT_IDS.has(id)) {
        gltf.scene.remove(node);
        suppressed.push(id);
        continue;
      }
      if (loadedSourceIds.has(id)) throw new Error(`duplicate scene node would be loaded for source ID ${id}`);
      if (!node.isMesh) throw new Error(`${source.package} stable node is not one direct mesh: ${id}`);
      loadedSourceIds.add(id);
      accepted.push({ id, object: node, data: node.userData ?? {} });
    }
    if (source.package === "T75" && new Set(accepted.map(row => row.id)).size !== EXPECTED.length) throw new Error("T75 target ID count differs from frozen six");
    if (source.package !== "T75" && accepted.length + suppressed.length !== source.allowedCount) throw new Error(`${source.package} input node count differs from historical manifest`);
    root.add(gltf.scene);
    for (const entry of accepted) {
      const { id, object, data } = entry;
      const material = new THREE.MeshStandardMaterial({ color: source.role === "target" ? 0x82bfd4 : 0xb39a80, roughness: 0.82, side: THREE.DoubleSide });
      object.material = material;
      materialByMesh.set(object, material);
      addedCount += 1;
      if (source.role === "target") targetRows.push({ ...data, sourceElementFileId: id, mesh: object });
    }
    packageIdSets.set(source.package, accepted.map(row => row.id));
    proof.packages.push({ package: source.package, path: source.path, frame: extras.frame, pose: extras.pose, unit: extras.unit ?? "m", unitEvidence: source.unitEvidence, acceptedIds: accepted.map(row => row.id), suppressedDuplicateIds: suppressed, nodeCount: accepted.length });
  }
  targetRows.sort((a, b) => a.sourceElementFileId.localeCompare(b.sourceElementFileId));
  if (targetRows.map(row => row.sourceElementFileId).join(",") !== EXPECTED.slice().sort().join(",")) throw new Error("T75 target FJ IDs differ from frozen exact set");
  for (const row of targetRows) {
    const button = document.createElement("button");
    button.type = "button";
    button.dataset.id = row.sourceElementFileId;
    button.textContent = `${row.sourceNameEnglishExactHeader} · ${row.explicitSourceSide}`;
    button.addEventListener("click", () => select(targetRows.indexOf(row)));
    list.append(button);
  }
  if (addedCount !== 284 || loadedSourceIds.size !== 284 || EXPECTED.some(id => !packageIdSets.get("T75").includes(id))) throw new Error(`expected 284 unique shared-root nodes including all six T75 surfaces; found ${addedCount}`);
  allBounds.setFromObject(root);
  proof.loaded = true;
  proof.targetCount = targetRows.length;
  proof.meshNodeCount = addedCount;
  proof.rootChildCount = root.children.length;
  proof.visibleSourceIds = [...loadedSourceIds].sort();
  proof.targetSourceIds = targetRows.map(row => row.sourceElementFileId);
  proof.regionMembershipRows = 12;
  proof.sceneBoundsM = { min: allBounds.min.toArray(), max: allBounds.max.toArray() };
  document.body.dataset.loaded = "true";
  document.body.dataset.rendererCount = "1";
  document.body.dataset.rootCount = String(scene.children.filter(item => item.name === "AnatomySceneRoot").length);
  document.body.dataset.targetCount = String(targetRows.length);
  document.body.dataset.meshNodeCount = String(addedCount);
  document.body.dataset.frame = FRAME;
  document.body.dataset.pose = POSE;
  document.body.dataset.consoleErrorCount = String(proof.consoleErrors.length);
  document.body.dataset.targetSourceIds = proof.targetSourceIds.join(",");
  status.textContent = `${addedCount} unique same-frame source meshes · 6 T75 deltoid parts · 1 scene root / 1 renderer · internal QA`;
  select(0);
  document.body.dataset.loaded = "true";
  document.body.dataset.rendererCount = "1";
  document.body.dataset.rootCount = String(scene.children.filter(item => item.name === "AnatomySceneRoot").length);
  window.dispatchEvent(new Event("t75-qa-ready"));
}

main().catch(error => {
  status.textContent = `QA load failed: ${String(error)}`;
  console.error(error);
  proof.consoleErrors.push(String(error));
  document.body.dataset.consoleErrorCount = String(proof.consoleErrors.length);
});
