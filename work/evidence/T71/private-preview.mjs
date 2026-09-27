import * as THREE from "../../../atlas-web/node_modules/three/build/three.module.js";
import { GLTFLoader } from "../../../atlas-web/node_modules/three/examples/jsm/loaders/GLTFLoader.js";

const canvas = document.querySelector("#canvas");
const status = document.querySelector("#status");
const list = document.querySelector("#list");
const selectedText = document.querySelector("#selected");
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: false });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.setClearColor(0x10151b, 1);
renderer.outputColorSpace = THREE.SRGBColorSpace;

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x10151b);
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

const loader = new GLTFLoader();
const targetById = new Map();
const originalMaterials = new Map();
const meshByObject = new Map();
let targetRows = [];
let selectedMesh = null;
let selectedIndex = -1;
let currentView = "front";
let center = new THREE.Vector3();
let cameraDistance = 2;

const packageSpecs = [
  { id: "T53", label: "T53 trunk/pelvis", glb: "../../../atlas-data/source-cache/bodyparts3d-r4/converted/t53/T53-trunk-pelvis-static-source.glb", manifest: "../../../atlas-data/manifests/bodyparts3d-r4-t53/source-manifest.json" },
  { id: "T55", label: "T55 bilateral lower limbs", glb: "../../../atlas-data/source-cache/bodyparts3d-r4/converted/t55/T55-bilateral-lower-limb-static-source.glb", manifest: "../../../atlas-data/manifests/bodyparts3d-r4-t55/source-manifest.json" },
  { id: "T71", label: "T71 trunk skeleton", glb: "../../../atlas-data/source-cache/bodyparts3d-r4/converted/t71/T71-trunk-skeleton-static-source.glb", manifest: "../../../atlas-data/manifests/bodyparts3d-r4-t71/source-manifest.json", targets: true },
];

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
  const dirs = {
    front: new THREE.Vector3(0, 0.10, 1),
    back: new THREE.Vector3(0, 0.10, -1),
    side: new THREE.Vector3(1, 0.10, 0),
  };
  camera.position.copy(center).addScaledVector(dirs[view], cameraDistance);
  camera.lookAt(center);
  for (const button of document.querySelectorAll("[data-view]")) {
    button.setAttribute("aria-pressed", String(button.dataset.view === view));
  }
  if (window.t71QaProof) window.t71QaProof.views.push(view);
  render();
}

function restoreSelection() {
  if (selectedMesh && originalMaterials.has(selectedMesh)) selectedMesh.material = originalMaterials.get(selectedMesh);
  selectedMesh = null;
  selectedIndex = -1;
}

function selectTargetByIndex(index) {
  if (!targetRows.length) return;
  restoreSelection();
  selectedIndex = (index + targetRows.length) % targetRows.length;
  const row = targetRows[selectedIndex];
  selectedMesh = row.mesh;
  const before = originalMaterials.get(selectedMesh);
  selectedMesh.material = new THREE.MeshStandardMaterial({ color: 0xffd45e, roughness: 0.62, metalness: 0.0, side: THREE.DoubleSide });
  selectedText.textContent = `${row.sourceElementFileId} · ${row.sourceNameEnglishExactHeader}\nFMA ${row.sourceFmaConceptId} · ${row.lateralityFromExactSourceName}\n${row.productCandidateRegion} · source only · no human anatomy review`;
  for (const button of list.querySelectorAll("button")) {
    button.setAttribute("aria-pressed", String(button.dataset.sourceId === row.sourceElementFileId));
  }
  document.body.dataset.selectedSourceId = row.sourceElementFileId;
  window.t71QaProof.selection = { sourceElementFileId: row.sourceElementFileId, stableMeshAssetId: row.stableMeshAssetId, view: currentView, highlightApplied: Boolean(before) };
  render();
}

function resize() { render(); }
new ResizeObserver(resize).observe(document.querySelector("#stage"));
window.addEventListener("resize", resize);

for (const button of document.querySelectorAll("[data-view]")) {
  button.addEventListener("click", () => face(button.dataset.view));
}
document.addEventListener("keydown", event => {
  if (event.key === "ArrowDown") { event.preventDefault(); selectTargetByIndex(selectedIndex + 1); }
  else if (event.key === "ArrowUp") { event.preventDefault(); selectTargetByIndex(selectedIndex < 0 ? targetRows.length - 1 : selectedIndex - 1); }
  else if (event.key === "1") face("front");
  else if (event.key === "2") face("back");
  else if (event.key === "3") face("side");
});

function loadGlb(path) {
  return new Promise((resolve, reject) => loader.load(path, resolve, undefined, reject));
}

async function main() {
  window.t71QaProof = { loaded: false, rendererCount: 1, rootName: anatomySceneRoot.name, rootCount: 1, canvasCount: document.querySelectorAll("canvas").length, packages: [], meshCount: 0, targetCount: 0, views: [], selection: null, sceneBoundsM: null, consoleErrors: [] };
  window.addEventListener("error", event => window.t71QaProof.consoleErrors.push(String(event.message)));
  const packageData = await Promise.all(packageSpecs.map(async spec => {
    const [gltf, response] = await Promise.all([loadGlb(spec.glb), fetch(spec.manifest)]);
    if (!response.ok) throw new Error(`manifest fetch failed: ${spec.id} ${response.status}`);
    const manifest = await response.json();
    const extras = gltf.parser.json.extras ?? {};
    if (extras.frame !== "HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR" || extras.pose !== "bodyparts3d-r4-static-reference") {
      throw new Error(`${spec.id} frame/pose differs from T50 shared static contract`);
    }
    return { spec, gltf, manifest, extras };
  }));

  const targetPackage = packageData.find(item => item.spec.targets);
  const expectedIds = ["FJ3153", "FJ3157", "FJ3159", "FJ3162", "FJ3165", "FJ3168", "FJ3178", "FJ3290", "FJ3393"];
  const targetManifestRows = targetPackage.manifest.sourceAssets;
  if (targetManifestRows.map(row => row.sourceElementFileId).sort().join(",") !== [...expectedIds].sort().join(",")) {
    throw new Error("T71 source manifest is not exactly the authorized nine source IDs");
  }
  for (const row of targetManifestRows) targetById.set(row.sourceElementFileId, row);

  let nodeCount = 0;
  for (const item of packageData) {
    anatomySceneRoot.add(item.gltf.scene);
    item.gltf.scene.traverse(object => {
      if (!object.isMesh) return;
      nodeCount += 1;
      const source = object.userData.sourceElementFileId ? object.userData : object.parent?.userData ?? object.userData;
      object.userData.source = source;
      const target = targetById.get(source.sourceElementFileId);
      const isBoneContext = Object.values(source.regionContextKinds ?? {}).some(value => value.boneContext) || (source.sourceClassCandidates ?? []).some(value => String(value).includes("bone"));
      const baseColor = target ? 0x68b7d0 : isBoneContext ? 0x9db6d1 : 0xb9907d;
      const material = new THREE.MeshStandardMaterial({ color: baseColor, roughness: 0.86, metalness: 0, side: THREE.DoubleSide });
      object.material = material;
      originalMaterials.set(object, material);
      meshByObject.set(object, source.sourceElementFileId);
      if (target) {
        target.mesh = object;
        targetRows.push(target);
      }
    });
    window.t71QaProof.packages.push({ id: item.spec.id, label: item.spec.label, meshCount: item.gltf.scene.children.length, sourceFrame: item.extras.frame, pose: item.extras.pose, projectUnit: item.extras.unit ?? "m" });
  }
  targetRows.sort((a, b) => a.sourceElementFileId.localeCompare(b.sourceElementFileId));
  if (targetRows.length !== expectedIds.length || targetRows.some(row => !row.mesh)) throw new Error("one or more exact T71 target IDs did not map to a GLB mesh");

  const bounds = new THREE.Box3().setFromObject(anatomySceneRoot);
  center = bounds.getCenter(new THREE.Vector3());
  const size = bounds.getSize(new THREE.Vector3());
  cameraDistance = Math.max(size.x, size.y, size.z) * 1.8;
  const totalRenderable = packageData.reduce((n, item) => n + (item.gltf.parser.json.nodes?.length ?? 0), 0);
  window.t71QaProof = { ...window.t71QaProof, loaded: true, meshCount: nodeCount, targetCount: targetRows.length, gltfNodeCount: totalRenderable, canvasCount: document.querySelectorAll("canvas").length, rootCount: scene.children.filter(x => x.name === "AnatomySceneRoot").length, frame: "HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR", pose: "bodyparts3d-r4-static-reference", sceneBoundsM: { min: bounds.min.toArray(), max: bounds.max.toArray() }, packages: packageData.map(item => ({ id: item.spec.id, label: item.spec.label, gltfNodeCount: item.gltf.parser.json.nodes?.length ?? 0, frame: item.extras.frame, pose: item.extras.pose, publicRelease: false })) };
  for (const row of targetRows) {
    const button = document.createElement("button");
    button.type = "button";
    button.dataset.sourceId = row.sourceElementFileId;
    button.textContent = `${row.sourceNameEnglishExactHeader} · ${row.sourceElementFileId}`;
    button.addEventListener("click", () => selectTargetByIndex(targetRows.indexOf(row)));
    list.append(button);
  }
  document.body.dataset.loaded = "true";
  document.body.dataset.rendererCount = "1";
  document.body.dataset.rootCount = "1";
  document.body.dataset.targetCount = String(targetRows.length);
  document.body.dataset.meshCount = String(nodeCount);
  document.body.dataset.frame = window.t71QaProof.frame;
  document.body.dataset.pose = window.t71QaProof.pose;
  status.textContent = `${nodeCount} mesh nodes · T53/T55/T71 한 scene root · 동일 static frame/pose · T71 target 9개 · 제품 공개/사람 검토 아님`;
  face("front");
  selectTargetByIndex(0);
}

main().catch(error => {
  status.textContent = `QA 로딩 실패: ${String(error)}`;
  console.error(error);
  if (window.t71QaProof) window.t71QaProof.consoleErrors.push(String(error));
});
