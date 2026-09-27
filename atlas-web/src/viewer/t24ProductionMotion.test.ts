import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import { Mesh, Vector3 } from "three";
import type { MotionAsset } from "../domain/motionLearning.ts";
import { AnimationPlaybackController } from "./animationPlayback.ts";
import { loadAnimationScene } from "./animationSceneAdapter.ts";

const root = new URL("../../../", import.meta.url);
const bundle = JSON.parse(readFileSync(new URL("atlas-data/motion/motion-learning.json", root), "utf8"));
const manifest = JSON.parse(readFileSync(new URL("atlas-data/assets/motion/t24-right-tibialis-anterior/ankle-dorsiflexion.json", root), "utf8"));
const asset = bundle.motionAssets.find((row: MotionAsset) => row.id === "HA-ASSET-T24-R-TIBANT-ANKLE-DF-V1") as MotionAsset;

test("actual T44-derived production GLB loads, rotates the right ankle, and keeps the path endpoint on the moving body", async () => {
  assert.ok(asset);
  const raw = readFileSync(new URL(asset.uri, root));
  const bytes = raw.buffer.slice(raw.byteOffset, raw.byteOffset + raw.byteLength);
  const resource = await loadAnimationScene(bytes, asset);
  let pending: ((timestamp: number) => void) | null = null;
  const player = new AnimationPlaybackController(resource, asset.clip.id, {
    repeat: true,
    scheduler: { request(callback) { pending = callback; return 1; }, cancel() { pending = null; } },
  });
  const frame = (timestamp: number) => { const callback = pending; assert.ok(callback); pending = null; callback(timestamp); };
  try {
    assert.equal(resource.animations.length, 1);
    assert.equal(resource.animations[0].tracks.length, 2);
    assert.equal(resource.skinnedMeshCount, 0);
    assert.equal(resource.rigNodes.get("HA-S-TALUS")?.name, "ankle_r_pivot_q0");
    const path = resource.pathNodes.get("HA-M-000003") as Mesh;
    assert.equal(path.name, "tib_ant_r_model_path_q0");
    assert.ok(path.geometry.morphAttributes.position);
    assert.equal(path.geometry.morphAttributes.position.length, 2);
    const position = path.geometry.getAttribute("position");
    const targets = path.geometry.morphAttributes.position!;
    const toePivot = resource.scene.getObjectByName("mtp_r_pivot_q0");
    const fixedTibia = resource.scene.getObjectByName("tibia_r_fixed");
    assert.ok(toePivot && fixedTibia);
    const toeY: number[] = [];
    const fixedY: number[] = [];
    for (let sample = 0; sample < 3; sample++) {
      player.seek(sample);
      resource.scene.updateMatrixWorld(true);
      toeY.push(toePivot.getWorldPosition(new Vector3()).y);
      fixedY.push(fixedTibia.getWorldPosition(new Vector3()).y);
      const influences = path.morphTargetInfluences ?? [];
      const endpoint = new Vector3(
        position.getX(2) + targets[0].getX(2) * (influences[0] ?? 0) + targets[1].getX(2) * (influences[1] ?? 0),
        position.getY(2) + targets[0].getY(2) * (influences[0] ?? 0) + targets[1].getY(2) * (influences[1] ?? 0),
        position.getZ(2) + targets[0].getZ(2) * (influences[0] ?? 0) + targets[1].getZ(2) * (influences[1] ?? 0),
      );
      const expected = new Vector3(...manifest.endpointSceneM[sample]);
      assert.ok(endpoint.distanceTo(expected) < 2e-6, `sample ${sample} path endpoint gap`);
    }
    assert.ok(toeY[0] < toeY[1] && toeY[1] < toeY[2], `anterior foot must rise in +dorsiflexion: ${toeY}`);
    assert.ok(toeY[2] - toeY[0] > 0.01);
    assert.deepEqual(fixedY, [0, 0, 0]);
    player.play();
    frame(0);
    frame(1000);
    frame(2200);
    assert.equal(player.isPlaying, true);
    assert.ok(Math.abs(player.currentTime - 0.2) < 1e-6, `actual clip should wrap after 2 s: ${player.currentTime}`);
    player.resetPose();
    assert.equal(player.currentTime, 0);
    assert.ok(Math.abs(toePivot.getWorldPosition(new Vector3()).y - toeY[0]) < 1e-6);
  } finally {
    player.dispose();
  }
});
