import * as THREE from "../../../atlas-web/node_modules/three/build/three.module.js";
import { GLTFLoader } from "../../../atlas-web/node_modules/three/examples/jsm/loaders/GLTFLoader.js";

const canvas = document.querySelector("#canvas");
const status = document.querySelector("#status");
const list = document.querySelector("#list");
const selectedText = document.querySelector("#selected");
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: false });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.setClearColor(0x111922, 1);
renderer.outputColorSpace = THREE.SRGBColorSpace;

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x111922);
const camera = new THREE.PerspectiveCamera(35, 1, 0.01, 35);
const anatomySceneRoot = new THREE.Group();
anatomySceneRoot.name = "AnatomySceneRoot";
scene.add(anatomySceneRoot);
scene.add(new THREE.HemisphereLight(0xdceeff, 0x35414b, 2));
const keyLight = new THREE.DirectionalLight(0xffffff, 2.4);
keyLight.position.set(1.5, 2, 2.6);
scene.add(keyLight);
const fillLight = new THREE.DirectionalLight(0xa9caff, 1.2);
fillLight.position.set(-2.2, 1, -1.6);
scene.add(fillLight);

const loader = new GLTFLoader();
const byId = new Map();
const targetById = new Map();
const originalMaterials = new Map();
const targetIds = ["FJ1520", "FJ1520M", "FJ1554", "FJ1554M", "FJ1521", "FJ1521M"];
const proof = {
  task: "T92",
  privatePreview: true,
  loaded: false,
  rendererCount: 1,
  rootName: anatomySceneRoot.name,
  canvasCount: document.querySelectorAll("canvas").length,
  rootCount: 1,
  frame: "HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR",
  pose: "bodyparts3d-r4-static-reference",
  packages: [],
  deduplicatedSourceIds: [],
  targetIds,
  targetMeshCount: 0,
  learnerDefaultVisibilityChanged: false,
  learnerBindingsAdded: 0,
  visibleOnlyForPrivateQa: true,
  views: [],
  errors: [],
};
window.t92QaProof = proof;

function reportError(value) {
  proof.errors.push(String(value));
  status.dataset.pageErrorEvents = String(proof.errors.length);
  status.textContent = `Page error events: ${proof.errors.length} · ${String(value)}`;
  document.body.dataset.qaProof = JSON.stringify(proof);
}
window.addEventListener("error", event => reportError(event.message || event.error || "window error"));
window.addEventListener("unhandledrejection", event => reportError(event.reason || "unhandled rejection"));

function sourceMetadata(mesh) {
  let node = mesh;
  while (node && !node.userData.sourceElementFileId && !node.userData.sourceFileId && !node.userData.stableMeshAssetId && !node.userData.stableSourceMeshNodeId) node = node.parent;
  return node?.userData ?? null;
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

function focusBounds(targetOnly) {
  const objects = targetOnly
    ? targetIds.map(id => byId.get(id)?.mesh).filter(Boolean)
    : [...byId.values()].map(row => row.mesh);
  const box = new THREE.Box3();
  for (const object of objects) box.expandByObject(object);
  if (box.isEmpty()) return { center: new THREE.Vector3(), distance: 3 };
  const center = box.getCenter(new THREE.Vector3());
  const size = box.getSize(new THREE.Vector3());
  const distance = targetOnly ? Math.max(size.length() * 2.9, 0.42) : Math.max(size.length() * 0.95, 3.8);
  return { center, distance };
}

let focus = focusBounds(true);
let currentView = "front";
function face(view) {
  currentView = view;
  document.body.dataset.cameraView = view;
  const directions = {
    front: new THREE.Vector3(0, 0.12, 1),
    back: new THREE.Vector3(0, 0.12, -1),
    side: new THREE.Vector3(1, 0.12, 0),
  };
  camera.position.copy(focus.center).addScaledVector(directions[view], focus.distance);
  camera.lookAt(focus.center);
  for (const button of document.querySelectorAll("[data-view]")) {
    button.setAttribute("aria-pressed", String(button.dataset.view === view));
  }
  const viewRecord = {
    view,
    cameraPosition: camera.position.toArray().map(value => Number(value.toFixed(6))),
    lookAt: focus.center.toArray().map(value => Number(value.toFixed(6))),
    targetIdsVisible: targetIds.filter(id => byId.get(id)?.mesh.visible),
    targetMeshCount: targetIds.filter(id => Boolean(byId.get(id)?.mesh)).length,
    anatomySceneRootCount: scene.children.filter(child => child.name === "AnatomySceneRoot").length,
  };
  proof.views.push(viewRecord);
  document.body.dataset.qaProof = JSON.stringify(proof);
  render();
}

function showTargetSelection(id) {
  const row = byId.get(id);
  if (!row) return;
  for (const [mesh, material] of originalMaterials) mesh.material = material;
  row.mesh.material = new THREE.MeshStandardMaterial({ color: 0xffd95a, roughness: 0.62, side: THREE.DoubleSide });
  selectedText.textContent = `${id} · ${row.source.sourceNameEnglishExactHeader ?? row.source.sourceName ?? "source name unavailable"}\nFMA ${row.source.sourceFmaConceptId ?? "unavailable"} · ${row.source.exactSourceSide ?? "side unavailable"}\nStable source node: ${row.source.stableSourceMeshNodeId ?? `HA-MESH-BP3D4-${id}`}\nSource contexts: back; shoulder-scapular\nStatus: source-only · human review pending · redistribution held`;
  document.body.dataset.selectedSourceId = id;
  proof.selection = { sourceElementFileId: id, stableSourceMeshNodeId: row.source.stableSourceMeshNodeId ?? `HA-MESH-BP3D4-${id}`, contexts: ["back", "shoulder-scapular"], currentView };
  document.body.dataset.qaProof = JSON.stringify(proof);
  render();
}

function addPackage(spec, gltf, manifest) {
  const packageFrame = gltf.parser.json.extras?.frame;
  const packagePose = gltf.parser.json.extras?.pose;
  const packageUnit = gltf.parser.json.extras?.unit;
  if (packageFrame !== proof.frame || packagePose !== proof.pose) throw new Error(`${spec.id}: frame/pose contract mismatch`);
  if (spec.id === "T92") {
    const manifestIds = manifest.sourceAssets.map(row => row.sourceElementFileId).sort().join(",");
    if (manifestIds !== [...targetIds].sort().join(",")) throw new Error("T92 manifest is not the exact frozen six-member source set");
  }
  gltf.scene.updateMatrixWorld(true);
  const nodes = [];
  gltf.scene.traverse(object => { if (object.isMesh) nodes.push(object); });
  const manifestById = new Map((manifest?.sourceAssets ?? []).map(row => [row.sourceElementFileId, row]));
  const added = [];
  const duplicates = [];
  for (const mesh of nodes) {
    const sourceNode = sourceMetadata(mesh);
    const id = sourceNode?.sourceElementFileId ?? sourceNode?.sourceFileId;
    if (!id) continue;
    const manifestRow = manifestById.get(id);
    const source = {
      ...sourceNode,
      sourceNameEnglishExactHeader: sourceNode.sourceNameEnglishExactHeader ?? manifestRow?.sourceHeaderIdentity?.sourceEnglishNameHeaderExact,
      sourceFmaConceptId: sourceNode.sourceFmaConceptId ?? manifestRow?.sourceHeaderIdentity?.sourceFmaConceptId,
      sourceRepresentationId: sourceNode.sourceRepresentationId ?? manifestRow?.sourceHeaderIdentity?.sourceRepresentationId,
      exactSourceSide: sourceNode.exactSourceSide ?? manifestRow?.sideFromExactOfficialConceptRelation,
    };
    if (byId.has(id)) {
      const existing = byId.get(id);
      existing.contexts = [...new Set([...existing.contexts, ...(source.regionMemberships ?? []), ...(source.candidateRegionContexts ?? [])])];
      duplicates.push(id);
      continue;
    }
    const sourceTransform = mesh.matrixWorld.clone();
    mesh.parent?.remove(mesh);
    mesh.matrixAutoUpdate = false;
    mesh.matrix.copy(sourceTransform);
    mesh.matrixWorld.copy(sourceTransform);
    anatomySceneRoot.add(mesh);
    const isTarget = spec.id === "T92";
    const material = new THREE.MeshStandardMaterial({ color: isTarget ? 0xc78d76 : 0x96a9bb, roughness: 0.86, metalness: 0, side: THREE.DoubleSide });
    mesh.material = material;
    originalMaterials.set(mesh, material);
    const row = { mesh, source, contexts: [...(source.regionMemberships ?? source.candidateRegionContexts ?? [])], packageId: spec.id };
    byId.set(id, row);
    if (isTarget) targetById.set(id, row);
    added.push(id);
  }
  return { id: spec.id, gltfMeshCount: nodes.length, addedUniqueSourceIds: added, duplicateSourceIds: duplicates, frame: packageFrame, pose: packagePose, unit: packageUnit ?? "not exposed" };
}

async function loadPackage(spec) {
  const gltf = await loader.loadAsync(spec.glb);
  if (!spec.manifest) return { gltf, manifest: null };
  const manifestResponse = await fetch(spec.manifest);
  if (!manifestResponse.ok) throw new Error(`${spec.id} manifest fetch failed: ${manifestResponse.status}`);
  return { gltf, manifest: await manifestResponse.json() };
}

const packages = [
  { id: "T53", glb: "../../../atlas-data/source-cache/bodyparts3d-r4/converted/t53/T53-trunk-pelvis-static-source.glb" },
  { id: "T54", glb: "../../../atlas-data/source-cache/bodyparts3d-r4/converted/t54/T54-shoulder-upper-limb-static-source.glb" },
  { id: "T92", glb: "../../../atlas-data/source-cache/bodyparts3d-r4/converted/t92/T92-trapezius-static-source.glb", manifest: "../../../atlas-data/manifests/bodyparts3d-r4-t92/source-manifest.json" },
];

async function main() {
  try {
    const summaries = [];
    for (const spec of packages) {
      const { gltf, manifest } = await loadPackage(spec);
      const summary = addPackage(spec, gltf, manifest);
      summaries.push(summary);
      proof.packages.push(summary);
    }
    if (targetById.size !== targetIds.length) throw new Error(`Expected six target nodes, found ${targetById.size}`);
    const targetIdsFromManifest = new Set((await fetch("../../../atlas-data/manifests/bodyparts3d-r4-t92/source-manifest.json").then(response => response.json())).sourceAssets.map(row => row.sourceElementFileId));
    if ([...targetIdsFromManifest].sort().join(",") !== [...targetIds].sort().join(",")) throw new Error("Target manifest IDs differ from the T92 freeze");
    const contextManifest = await fetch("../../../atlas-data/manifests/bodyparts3d-r4-t92/integration-extension.json").then(response => response.json());
    for (const id of targetIds) {
      const row = contextManifest.assets.find(asset => asset.sourceElementFileId === id && asset.primaryPackage === "T92");
      if (!row || row.regionMembershipRows.map(item => item.regionId).sort().join(",") !== "back,shoulder-scapular" || new Set(row.regionMembershipRows.map(item => item.renderNodeId)).size !== 1) {
        throw new Error(`${id} does not share one stable node across both source contexts`);
      }
    }
    const sceneBox = new THREE.Box3().setFromObject(anatomySceneRoot);
    const targetBox = new THREE.Box3();
    for (const id of targetIds) targetBox.expandByObject(targetById.get(id).mesh);
    focus = { center: targetBox.getCenter(new THREE.Vector3()), distance: Math.max(targetBox.getSize(new THREE.Vector3()).length() * 2.9, 0.42) };
    proof.loaded = true;
    proof.packages = summaries;
    proof.totalUniqueSourceNodes = byId.size;
    proof.targetMeshCount = targetById.size;
    proof.qaTargetsVisibleInPrivatePreview = true;
    proof.targetNodesInQaScene = [...targetById.keys()].sort();
    proof.targetBoundsM = { min: targetBox.min.toArray(), max: targetBox.max.toArray() };
    proof.loadedContextBoundsM = { min: sceneBox.min.toArray(), max: sceneBox.max.toArray() };
    proof.bodyparts3dSourcePackages = packages.map(item => item.id);
    proof.deduplicatedSourceIds = summaries.flatMap(item => item.duplicateSourceIds).sort();
    proof.rootCount = scene.children.filter(child => child.name === "AnatomySceneRoot").length;
    document.body.dataset.loaded = "true";
    document.body.dataset.rendererCount = "1";
    document.body.dataset.rootCount = String(proof.rootCount);
    document.body.dataset.targetCount = String(targetById.size);
    document.body.dataset.uniqueSourceNodeCount = String(byId.size);
    document.body.dataset.qaProof = JSON.stringify(proof);
    status.textContent = `${byId.size} unique source nodes · T53/T54 context + T92 six targets · one renderer/root · static private QA`;
    for (const id of targetIds) {
      const source = targetById.get(id).source;
      const button = document.createElement("button");
      button.type = "button";
      button.dataset.sourceId = id;
      button.textContent = `${id} · ${source.sourceNameEnglishExactHeader ?? source.sourceName ?? "source name unavailable"}`;
      button.addEventListener("click", () => showTargetSelection(id));
      list.append(button);
    }
    face("front");
    document.querySelector("#focusTrapezius").addEventListener("click", () => {
      const box = new THREE.Box3();
      for (const id of targetIds) box.expandByObject(targetById.get(id).mesh);
      focus = { center: box.getCenter(new THREE.Vector3()), distance: Math.max(box.getSize(new THREE.Vector3()).length() * 2.9, 0.42) };
      face(currentView);
    });
    document.querySelector("#focusScene").addEventListener("click", () => {
      const box = new THREE.Box3().setFromObject(anatomySceneRoot);
      focus = { center: box.getCenter(new THREE.Vector3()), distance: Math.max(box.getSize(new THREE.Vector3()).length() * 0.95, 3.8) };
      face(currentView);
    });
    document.querySelectorAll("[data-view]").forEach(button => button.addEventListener("click", () => face(button.dataset.view)));
    new ResizeObserver(render).observe(document.querySelector("#stage"));
    window.addEventListener("resize", render);
    render();
    window.t92QaProof = proof;
  } catch (error) {
    reportError(error);
    console.error(error);
  }
}

main();
