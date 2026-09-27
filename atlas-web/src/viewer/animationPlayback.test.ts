import assert from "node:assert/strict";
import test from "node:test";
import { AnimationClip, Object3D, VectorKeyframeTrack } from "three";
import { AnimationPlaybackController, SingleAnimationFrameLoop, type AnimationFrameScheduler } from "./animationPlayback.ts";

class FakeFrames implements AnimationFrameScheduler {
  private nextId = 1;
  pending = new Map<number, (timestamp: number) => void>();
  cancelled = new Map<number, (timestamp: number) => void>();
  requests = 0;

  request(callback: (timestamp: number) => void): number {
    const id = this.nextId++;
    this.pending.set(id, callback);
    this.requests++;
    return id;
  }

  cancel(id: number): void {
    const callback = this.pending.get(id);
    if (callback) this.cancelled.set(id, callback);
    this.pending.delete(id);
  }

  frame(timestamp: number): void {
    const next = this.pending.entries().next().value as [number, (timestamp: number) => void] | undefined;
    if (!next) throw new Error("No pending animation frame");
    this.pending.delete(next[0]);
    next[1](timestamp);
  }

  fireCancelled(timestamp: number): void {
    const next = this.cancelled.entries().next().value as [number, (timestamp: number) => void] | undefined;
    if (!next) throw new Error("No cancelled animation frame");
    this.cancelled.delete(next[0]);
    next[1](timestamp);
  }
}

test("single RAF loop updates speed without making a second chain and ignores late callbacks", () => {
  const frames = new FakeFrames();
  const deltas: number[] = [];
  const loop = new SingleAnimationFrameLoop((delta) => { deltas.push(delta); return true; }, frames);
  loop.start(1);
  loop.start(0.5);
  assert.equal(frames.requests, 1);
  assert.equal(frames.pending.size, 1);
  frames.frame(100);
  frames.frame(1100);
  assert.deepEqual(deltas, [0, 0.5]);
  assert.equal(frames.requests, 3);
  loop.stop();
  assert.equal(frames.pending.size, 0);
  const oldDeltaCount = deltas.length;
  frames.fireCancelled(2200);
  assert.equal(deltas.length, oldDeltaCount);
  assert.equal(loop.isRunning, false);
});

function syntheticResource(disposeCalls: { count: number }) {
  const scene = new Object3D();
  const bone = new Object3D();
  bone.name = "SyntheticBone";
  scene.add(bone);
  const camera = new Object3D();
  camera.position.set(5, 2, 8);
  scene.add(camera);
  const clip = new AnimationClip("SyntheticMotion", 1, [new VectorKeyframeTrack(
    "SyntheticBone.position", [0, 1], [0, 0, 0, 0, 1, 0],
  )]);
  return {
    scene,
    bone,
    camera,
    animations: [clip],
    dispose() { disposeCalls.count++; },
  };
}

test("T22 adapter scene is driven by one mixer clock; pose reset does not reset camera", () => {
  const frames = new FakeFrames();
  const disposed = { count: 0 };
  const resource = syntheticResource(disposed);
  const cameraStart = resource.camera.position.toArray();
  const times: number[] = [];
  const player = new AnimationPlaybackController(resource, "SyntheticMotion", {
    scheduler: frames,
    onTimeChange: (time) => times.push(time),
  });
  assert.equal(player.currentTime, 0);
  assert.equal(frames.requests, 0);
  player.play(0.5);
  player.play(0.5);
  assert.equal(frames.pending.size, 1);
  frames.frame(0);
  frames.frame(1000);
  assert.equal(player.currentTime, 0.5);
  assert.ok(Math.abs(resource.bone.position.y - 0.5) < 1e-6);
  player.resetPose();
  assert.equal(player.currentTime, 0);
  assert.ok(Math.abs(resource.bone.position.y) < 1e-6);
  assert.deepEqual(resource.camera.position.toArray(), cameraStart);
  assert.equal(frames.pending.size, 0);
  assert.ok(times.length >= 3);
  player.dispose();
  player.dispose();
  assert.equal(disposed.count, 1);
});

test("clip end clamps at the final pose and cancels its RAF chain", () => {
  const frames = new FakeFrames();
  const disposed = { count: 0 };
  const resource = syntheticResource(disposed);
  let completed = false;
  const player = new AnimationPlaybackController(resource, "SyntheticMotion", {
    scheduler: frames,
    onTimeChange: (_time, done) => { completed ||= done; },
  });
  player.play(1);
  frames.frame(0);
  frames.frame(1100);
  assert.equal(player.currentTime, 1);
  assert.ok(Math.abs(resource.bone.position.y - 1) < 1e-6);
  assert.equal(completed, true);
  assert.equal(frames.pending.size, 0);
  assert.equal(player.isPlaying, false);
  player.dispose();
});

test("missing clip fails closed and releases the imported scene", () => {
  const disposed = { count: 0 };
  const resource = syntheticResource(disposed);
  assert.throws(() => new AnimationPlaybackController(resource, "not-present"), /시범 clip/);
  assert.equal(disposed.count, 1);
});
