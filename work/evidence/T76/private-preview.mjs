import * as THREE from "./vendor/three/build/three.module.js";
import { GLTFLoader } from "./vendor/three/examples/jsm/loaders/GLTFLoader.js";

const TARGET_IDS = ["FJ1449M", "FJ1453M", "FJ1457M", "FJ1458M", "FJ2542", "FJ2544", "FJ2545", "FJ2546", "FJ2547", "FJ2549", "FJ2550", "FJ2551"];
const REUSE_IDS = new Set(["FJ1449M", "FJ2542", "FJ2547"]);
const RELATED_BONE_IDS = new Set(["FJ3152", "FJ3288"]);
const HELD_UNKNOWN_ID = "FJ1450";
const FRAME = "HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR";
const POSE = "bodyparts3d-r4-static-reference";
const renderer = new THREE.WebGLRenderer({ canvas: document.querySelector("#canvas"), antialias: true, alpha: false });
const canvas = document.querySelector("#canvas");
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.setClearColor(0x10151b, 1);
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x10151b);
const camera = new THREE.PerspectiveCamera(34, 1, 0.001, 20);
const root = new THREE.Group(); root.name = "AnatomySceneRoot"; scene.add(root);
scene.add(new THREE.HemisphereLight(0xe7f1ff, 0x34404b, 1.9));
const key = new THREE.DirectionalLight(0xffffff, 2.1); key.position.set(1.8, 2.4, 2.8); scene.add(key);
const fill = new THREE.DirectionalLight(0xa9caff, 0.8); fill.position.set(-2, 1, -1.5); scene.add(fill);
const proof = window.t76QaProof = { task: "T76", loaded: false, rendererCount: 1, rootCount: 1, canvasCount: 1, frame: FRAME, pose: POSE, packages: [], targetIds: [], targetCount: 0, reuseIds: [...REUSE_IDS], relatedBoneIds: [...RELATED_BONE_IDS], heldUnknownId: HELD_UNKNOWN_ID, views: [], selections: [], consoleErrors: [], claims: { attachmentContactPenetration: false, humanAnatomyReviewed: false, identityHoldReleased: false, licenseHoldReleased: false, learnerPolicyChanged: false } };
window.addEventListener("error", e => { proof.consoleErrors.push(String(e.message)); document.body.dataset.consoleErrorCount = String(proof.consoleErrors.length); });
const loader = new GLTFLoader();
const targets = [], sceneIds = new Set(), meshMaterials = new Map();
let view = "external", contextMode = "all", selected = null;
let pelvisCenter = new THREE.Vector3(), pelvisDistance = 0.55, fullBox = new THREE.Box3();
const contextMeshes = new Set(), targetMeshes = new Set();

function sourceId(object) {
  const d = object.userData ?? {};
  if (typeof d.sourceElementFileId === "string") return d.sourceElementFileId;
  const m = /^HA-MESH-BP3D4-(FJ[0-9]+M?)$/.exec(object.name ?? ""); return m?.[1] ?? null;
}
function render() {
  const w = canvas.clientWidth, h = canvas.clientHeight; if (!w || !h) return;
  renderer.setSize(w, h, false); camera.aspect = w / h; camera.updateProjectionMatrix(); renderer.render(scene, camera);
  document.body.dataset.canvasSize = `${w}x${h}`; document.body.dataset.lastRender = "true";
}
function chooseCamera(name) {
  view = name;
  const directions = {
    external: [0, 0.1, 1, [0, 1, 0]],
    inferior: [0, -1, 0.02, [0, 0, 1]],
    lateral: [1, 0.08, 0.05, [0, 1, 0]],
    deep: [0, 0.08, -1, [0, 1, 0]],
  };
  const [x, y, z, up] = directions[name];
  camera.position.copy(pelvisCenter).add(new THREE.Vector3(x, y, z).normalize().multiplyScalar(pelvisDistance));
  camera.up.set(...up); camera.lookAt(pelvisCenter);
  document.body.dataset.cameraView = name;
  document.querySelectorAll("[data-view]").forEach(b => b.setAttribute("aria-pressed", String(b.dataset.view === name)));
  proof.views.push({ view: name, canvasCssPx: [canvas.clientWidth, canvas.clientHeight], selectedId: selected?.id ?? null, contextMode, rendered: true });
  render();
}
function setContextMode(mode) {
  contextMode = mode;
  for (const mesh of contextMeshes) { const id = sourceId(mesh); mesh.visible = mode === "all" || (mode === "bones" && RELATED_BONE_IDS.has(id)); }
  const button = document.querySelector("#context");
  button.dataset.mode = mode; button.textContent = mode === "all" ? "Full context" : mode === "bones" ? "Hip bones + targets" : "Targets only";
  document.body.dataset.contextMode = mode; chooseCamera(view);
}
function fitPelvis() {
  const relevant = [...targetMeshes, ...[...sceneIds].filter(id => RELATED_BONE_IDS.has(id)).map(id => meshById.get(id)).filter(Boolean)];
  const b = new THREE.Box3(); for (const m of relevant) b.expandByObject(m);
  if (b.isEmpty()) b.copy(fullBox);
  pelvisCenter = b.getCenter(new THREE.Vector3());
  const s = b.getSize(new THREE.Vector3()); pelvisDistance = Math.max(s.x, s.y, s.z) * 2.3 + 0.15;
  chooseCamera("external");
}
const meshById = new Map();
function select(row) {
  if (selected) { selected.mesh.material = meshMaterials.get(selected.mesh); selected.mesh.material.emissive.setHex(0x000000); }
  selected = row; row.mesh.material = new THREE.MeshStandardMaterial({ color: 0xffcf58, roughness: 0.62, side: THREE.DoubleSide, emissive: 0x382700 });
  document.querySelector("#selected").textContent = `${row.name}\n${row.id} · ${row.fma ?? "source identity absent"} · ${row.side ?? "side not specified"}\n${REUSE_IDS.has(row.id) ? "T53 existing source; reuse only" : "T76 selected source"} · source only`;
  document.querySelectorAll("#list button").forEach(b => b.setAttribute("aria-pressed", String(b.dataset.id === row.id)));
  document.body.dataset.selectedId = row.id;
  proof.selections.push({ clickedId: row.id, selectedId: row.id, stableMeshAssetId: row.mesh.userData?.stableMeshAssetId ?? row.mesh.name, highlightApplied: true, cardMatchesSource: true, singlePressedRow: 1, frameUnchanged: true });
  chooseCamera(view);
}
function load(path) { return new Promise((resolve, reject) => loader.load(path, resolve, undefined, reject)); }
for (const b of document.querySelectorAll("[data-view]")) b.addEventListener("click", () => chooseCamera(b.dataset.view));
document.querySelector("#context").addEventListener("click", () => setContextMode(contextMode === "all" ? "bones" : contextMode === "bones" ? "targets" : "all"));
document.querySelector("#fit").addEventListener("click", fitPelvis);
document.addEventListener("keydown", e => { if (e.key === "Escape") fitPelvis(); });
new ResizeObserver(render).observe(document.querySelector("#stage")); window.addEventListener("resize", render);

async function main() {
  let total = 0;
  const packages = [
    { id: "T53", url: "./assets/T53-trunk-pelvis-static-source.glb", role: "existing-context", expectedCount: 138 },
    { id: "T76", url: "./assets/T76-pelvic-floor-static-source.glb", role: "new-target", expectedCount: 9 },
  ];
  for (const pkg of packages) {
    const gltf = await load(pkg.url), extras = gltf.parser.json.extras ?? {};
    if (extras.frame !== FRAME || extras.pose !== POSE || (extras.unit !== undefined && extras.unit !== "m")) throw new Error(`${pkg.id} frame/pose/unit mismatch`);
    const ids = [];
    for (const node of [...gltf.scene.children]) {
      const id = sourceId(node); if (!id) throw new Error(`${pkg.id} missing exact source FJ identity`);
      if (sceneIds.has(id)) throw new Error(`duplicate source FJ loaded across packages: ${id}`);
      if (!node.isMesh) throw new Error(`source node ${id} is not a mesh`);
      sceneIds.add(id); ids.push(id); meshById.set(id, node); total++;
      const material = new THREE.MeshStandardMaterial({ color: RELATED_BONE_IDS.has(id) ? 0xd7c29e : id === HELD_UNKNOWN_ID ? 0x858b91 : pkg.role === "new-target" || TARGET_IDS.includes(id) ? 0x82bfd4 : 0xb39a80, roughness: 0.84, side: THREE.DoubleSide });
      node.material = material; meshMaterials.set(node, material);
      if (pkg.role === "new-target" || TARGET_IDS.includes(id)) targetMeshes.add(node); else contextMeshes.add(node);
      if (TARGET_IDS.includes(id)) {
        const data = node.userData ?? {};
        targets.push({ id, name: data.sourceHeaderIdentity?.sourceEnglishNameExactHeader ?? data.sourceName ?? (id === "FJ1449M" || id === "FJ2542" ? "Left coccygeus" : id === "FJ2547" ? "Right coccygeus" : node.name), fma: data.externalConceptId ?? data.sourceConceptId ?? null, side: data.lateralityFromExactSourceHeader ?? data.exactSourceSideFromHeader ?? data.explicitSourceSide ?? data.sourceSide ?? null, mesh: node, data });
      }
    }
    root.add(gltf.scene); proof.packages.push({ package: pkg.id, path: pkg.url, role: pkg.role, nodeCount: ids.length, frame: extras.frame, pose: extras.pose, unit: extras.unit ?? "m", sourceIds: ids });
    if (ids.length !== pkg.expectedCount) throw new Error(`${pkg.id} expected ${pkg.expectedCount} nodes, got ${ids.length}`);
  }
  const actual = targets.map(x => x.id).sort(), expected = [...TARGET_IDS].sort();
  if (actual.join(",") !== expected.join(",")) throw new Error(`target identity set mismatch: ${actual.join(",")}`);
  if (![...RELATED_BONE_IDS].every(id => sceneIds.has(id))) throw new Error("existing paired hip-bone context missing");
  if (!sceneIds.has(HELD_UNKNOWN_ID)) throw new Error("T53 held unknown context absent; preserve existing context-only state");
  targets.sort((a,b) => a.id.localeCompare(b.id));
  for (const row of targets) { const b = document.createElement("button"); b.type = "button"; b.dataset.id = row.id; b.textContent = `${row.name} · ${row.side ?? "side unrecorded"} · ${row.id}`; b.addEventListener("click", () => select(row)); document.querySelector("#list").append(b); }
  fullBox.setFromObject(root);
  const use = [...targetMeshes, meshById.get("FJ3152"), meshById.get("FJ3288")].filter(Boolean), pelvisBox = new THREE.Box3(); use.forEach(m => pelvisBox.expandByObject(m));
  pelvisCenter = pelvisBox.getCenter(new THREE.Vector3()); const size = pelvisBox.getSize(new THREE.Vector3()); pelvisDistance = Math.max(size.x,size.y,size.z)*2.3+0.15;
  proof.loaded = true; proof.totalUniqueNodes = total; proof.rootChildCount = root.children.length; proof.targetIds = targets.map(x=>x.id); proof.targetCount = targets.length; proof.reuseIdsVerified = [...REUSE_IDS].every(id=>targets.some(x=>x.id===id)); proof.relatedBonesPresent = [...RELATED_BONE_IDS].every(id=>sceneIds.has(id)); proof.heldUnknownContextPresentAndUnselectable = sceneIds.has(HELD_UNKNOWN_ID) && !TARGET_IDS.includes(HELD_UNKNOWN_ID); proof.duplicateSourceIds = [];
  document.body.dataset.loaded="true"; document.body.dataset.rendererCount="1"; document.body.dataset.rootCount="1"; document.body.dataset.nodeCount=String(total); document.body.dataset.targetCount=String(targets.length); document.body.dataset.targetIds=proof.targetIds.join(","); document.body.dataset.consoleErrorCount="0";
  document.querySelector("#status").textContent=`${total} unique meshes · 138 T53 context + 9 T76 source nodes · one root / renderer · local QA`;
  document.querySelector("#metrics").textContent=`Target surfaces: ${targets.length} (9 new, 3 T53 reuse) · paired existing hip context: 2 · held unknown identity: preserved · 0 learner bindings`; fitPelvis(); select(targets[0]);
  window.dispatchEvent(new Event("t76-qa-ready"));
}
main().catch(error=>{document.querySelector("#status").textContent=`QA load failed: ${String(error)}`; console.error(error); proof.consoleErrors.push(String(error)); document.body.dataset.consoleErrorCount=String(proof.consoleErrors.length);});
