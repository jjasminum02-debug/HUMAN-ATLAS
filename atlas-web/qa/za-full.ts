// Dev-only inspector for atlas-data/pipeline/extract_za.py output. Not part of the learner app.
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
if (!import.meta.env.DEV) throw Error('Local QA only');

type Lod = { path: string; triangles: number };
type Structure = { id: string; name: string; sourceName: string; system: string; kind: string | null; side: string; matrix: number[]; lods: { overview: Lod; detail: Lod } };

import structuresUrl from '../../atlas-data/source-cache/datasets/za-full/structures.json?url';
const base = structuresUrl.slice(0, structuresUrl.lastIndexOf('/') + 1);
const COLORS: Record<string, number> = {
  bone: 0xe9e1cc, cartilage: 0xb9d3e6, tooth: 0xf4f1e8, muscle: 0xb4554f, tendon: 0xe6e0d2, fascia: 0xd9d4e8,
  aponeurosis: 0xe0dccc, retinaculum: 0xd7d0bb, sheath: 0x9cc6d9, septum: 0xcfc7de, bursa: 0x8fc4e8, raphe: 0xe0dccc,
  ligament: 0xf2efe4, capsule: 0xc9d8c5, disc: 0x9fb8d8, meniscus: 0xa9c7e0, labrum: 0xa9c7e0, membrane: 0xd6d2c4,
  cartilaginous_joint: 0xa9c7e0, fat_pad: 0xf0d58a, origin: 0xd9443a, insertion: 0x3a6fd9, nerve: 0xf2c94c, cns: 0xe8c6b0,
  sense_organ: 0xd8b4a0,
};
const DEFAULT_ON = new Set(['bone', 'cartilage', 'ligament', 'capsule', 'disc', 'meniscus', 'labrum', 'membrane', 'cartilaginous_joint']);

const scene = new THREE.Scene(); scene.background = new THREE.Color(0xeff1ef);
const host = document.querySelector<HTMLDivElement>('#scene')!;
const renderer = new THREE.WebGLRenderer({ antialias: true }); renderer.setPixelRatio(devicePixelRatio); host.appendChild(renderer.domElement);
const camera = new THREE.PerspectiveCamera(30, 1, 0.01, 50);
const controls = new OrbitControls(camera, renderer.domElement);
scene.add(new THREE.HemisphereLight(0xffffff, 0x8a8f8c, 2.2));
const sun = new THREE.DirectionalLight(0xffffff, 1.6); sun.position.set(1, 2, 3); scene.add(sun);
const resize = () => { renderer.setSize(host.clientWidth, host.clientHeight); camera.aspect = host.clientWidth / host.clientHeight; camera.updateProjectionMatrix(); };
addEventListener('resize', resize); resize();
const view = (pos: [number, number, number], target: [number, number, number]) => { camera.position.set(...pos); controls.target.set(...target); controls.update(); };
const views: Record<string, () => void> = {
  front: () => view([0, 0.95, 4.2], [0, 0.95, 0]), side: () => view([4.2, 0.95, 0], [0, 0.95, 0]),
  back: () => view([0, 0.95, -4.2], [0, 0.95, 0]), knee: () => view([-0.15, 0.5, 0.7], [-0.1, 0.5, 0]),
};
for (const [id, fn] of Object.entries(views)) document.querySelector<HTMLButtonElement>('#' + id)!.onclick = fn;
views.front();

const status = document.querySelector('#status')!;
const doc = await (await fetch(structuresUrl)).json() as { structures: Structure[] };
const byKind = new Map<string, Structure[]>();
for (const s of doc.structures) { const k = s.kind ?? 'unclassified'; byKind.set(k, [...(byKind.get(k) ?? []), s]); }
const groups = new Map<string, THREE.Group>();
const loader = new GLTFLoader();
const materials = new Map<string, THREE.Material>();
const material = (kind: string) => materials.get(kind) ?? (materials.set(kind, new THREE.MeshStandardMaterial({
  color: COLORS[kind] ?? 0x888888, roughness: 0.6, transparent: kind === 'fascia', opacity: kind === 'fascia' ? 0.55 : 1, side: THREE.DoubleSide,
})), materials.get(kind)!);

async function load(kind: string) {
  if (groups.has(kind)) { groups.get(kind)!.visible = true; return; }
  const group = new THREE.Group(); groups.set(kind, group); scene.add(group);
  const items = byKind.get(kind) ?? [];
  let done = 0;
  await Promise.all(items.map(async s => {
    const gltf = await loader.loadAsync(base + s.lods.overview.path);
    gltf.scene.traverse(o => { if ((o as THREE.Mesh).isMesh) { (o as THREE.Mesh).material = material(kind); o.userData.structure = s; } });
    gltf.scene.matrixAutoUpdate = false; gltf.scene.matrix.fromArray(s.matrix);
    group.add(gltf.scene); done++; status.textContent = `${kind} ${done}/${items.length}`;
  }));
  status.textContent = `${doc.structures.length}개 구조 · 표시 ${[...groups].filter(([, g]) => g.visible).map(([k]) => k).join(', ')}`;
}

const kinds = document.querySelector('#kinds')!;
const systems = new Map<string, string[]>();
for (const s of doc.structures) { const k = s.kind ?? 'unclassified'; const list = systems.get(s.system) ?? []; if (!list.includes(k)) list.push(k); systems.set(s.system, list); }
for (const [system, list] of systems) {
  kinds.insertAdjacentHTML('beforeend', `<h3>${system}</h3>`);
  for (const kind of list) {
    const label = document.createElement('label');
    label.innerHTML = `<input type="checkbox" ${DEFAULT_ON.has(kind) ? 'checked' : ''}><i style="background:#${(COLORS[kind] ?? 0x888888).toString(16).padStart(6, '0')}"></i>${kind} (${byKind.get(kind)!.length})`;
    const box = label.querySelector('input')!;
    box.onchange = () => box.checked ? load(kind) : groups.get(kind) && (groups.get(kind)!.visible = false);
    kinds.appendChild(label);
  }
}
await Promise.all([...DEFAULT_ON].filter(k => byKind.has(k)).map(load));

const ray = new THREE.Raycaster(); const pick = document.querySelector('#pick')!;
renderer.domElement.addEventListener('click', e => {
  const r = renderer.domElement.getBoundingClientRect();
  ray.setFromCamera(new THREE.Vector2((e.clientX - r.left) / r.width * 2 - 1, -(e.clientY - r.top) / r.height * 2 + 1), camera);
  const hit = ray.intersectObjects([...groups.values()].filter(g => g.visible), true)[0];
  const s = hit?.object.userData.structure as Structure | undefined;
  pick.textContent = s ? `${s.sourceName} · ${s.system}/${s.kind} · ${s.side}` : '구조를 클릭';
});
renderer.setAnimationLoop(() => renderer.render(scene, camera));
Object.assign(window, { zaQa: { doc, groups, renderer } });
