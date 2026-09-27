import { AmbientLight, Box3, DirectionalLight, PerspectiveCamera, Scene, Vector3, WebGLRenderer } from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import bundle from "../../atlas-data/motion/motion-learning.json";
import motionUrl from "../../atlas-data/assets/motion/t24-right-tibialis-anterior/ankle-dorsiflexion.glb?url";
import type { MotionAsset } from "./domain/motionLearning.ts";
import { AnimationPlaybackController } from "./viewer/animationPlayback.ts";
import { loadAnimationScene } from "./viewer/animationSceneAdapter.ts";

const canvas = document.querySelector<HTMLCanvasElement>("#scene")!;
const status = document.querySelector<HTMLElement>("#status")!;
const slider = document.querySelector<HTMLInputElement>("#time")!;
const readout = document.querySelector<HTMLOutputElement>("#readout")!;
const asset = bundle.motionAssets.find((row) => row.id === "HA-ASSET-T24-R-TIBANT-ANKLE-DF-V1") as MotionAsset | undefined;
if (!asset) throw new Error("등록된 T24 시범을 찾지 못했습니다.");

const scene = new Scene();
scene.background = null;
scene.add(new AmbientLight(0xffffff, 2));
const light = new DirectionalLight(0xffffff, 2);
light.position.set(1, 2, 2); scene.add(light);
const camera = new PerspectiveCamera(35, 1, 0.001, 20);
const renderer = new WebGLRenderer({ canvas, antialias: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
const controls = new OrbitControls(camera, canvas);
controls.enableDamping = true;
let player: AnimationPlaybackController | null = null;
let cancelled = false;
function resize() {
  const width = canvas.clientWidth, height = canvas.clientHeight;
  renderer.setSize(width, height, false);
  camera.aspect = width / height; camera.updateProjectionMatrix();
}
new ResizeObserver(resize).observe(canvas);
resize();
function draw() {
  if (cancelled) return;
  controls.update(); renderer.render(scene, camera);
  requestAnimationFrame(draw);
}
draw();

try {
  const response = await fetch(motionUrl);
  if (!response.ok) throw new Error(`GLB ${response.status}`);
  const resource = await loadAnimationScene(await response.arrayBuffer(), asset);
  scene.add(resource.scene);
  const bounds = new Box3().setFromObject(resource.scene);
  const center = bounds.getCenter(new Vector3());
  const extent = bounds.getSize(new Vector3()).length();
  controls.target.copy(center);
  camera.position.copy(center).add(new Vector3(extent * 0.8, extent * 0.35, extent * 1.5));
  camera.lookAt(center); controls.update();
  player = new AnimationPlaybackController(resource, asset.clip.id, {
    onTimeChange: (time) => { slider.value = String(time); readout.value = `${time.toFixed(2)}초`; },
  });
  status.textContent = "시범 준비 완료";
  document.querySelector<HTMLButtonElement>("#play")!.onclick = () => player?.play();
  document.querySelector<HTMLButtonElement>("#pause")!.onclick = () => player?.pause();
  document.querySelector<HTMLButtonElement>("#reset")!.onclick = () => player?.resetPose();
  slider.oninput = () => player?.seek(Number(slider.value));
  window.addEventListener("pagehide", () => { cancelled = true; player?.dispose(); controls.dispose(); renderer.dispose(); });
  // Small, read-only hook for local browser QA. No learner application state is modified.
  Object.assign(window, { __t24qa: { get time() { return player?.currentTime ?? null; }, get ready() { return !!player; }, get bones() { return resource.rigNodes.size; } } });
} catch (error) {
  status.textContent = `시범을 불러오지 못했습니다: ${error instanceof Error ? error.message : String(error)}`;
  throw error;
}
