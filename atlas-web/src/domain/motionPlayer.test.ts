import assert from "node:assert/strict";
import test from "node:test";
import {
  acceptMotionAssetLoad,
  beginMotionAssetLoad,
  changeMotionContext,
  createMotionPlayerState,
  failMotionAssetLoad,
  pauseMotion,
  playMotion,
  resetMotionPose,
  seekMotionProgress,
  selectMotionAction,
  setMotionSpeed,
  setMotionTime,
  syncMotionPlaybackTime,
  setReducedMotionPreference,
  suspendMotionForHiddenPage,
} from "./motionPlayer.ts";

function readyState(reduced = false) {
  const started = beginMotionAssetLoad(createMotionPlayerState("action-1", reduced));
  assert.notEqual(started.requestToken, null);
  const ready = acceptMotionAssetLoad(started.state, started.requestToken!, {
    actionId: "action-1", definitionId: "definition-1", assetId: "asset-1", durationSeconds: 2,
    structureIds: ["muscle-1", "bone-1"],
  });
  return { ready, token: started.requestToken! };
}

test("a muscle action can be selected without loading or autoplaying a clip", () => {
  const state = createMotionPlayerState("action-1");
  assert.equal(state.session.status, "idle");
  assert.equal(state.session.assetId, null);
  assert.equal(state.session.currentTimeSeconds, 0);
  assert.deepEqual(state.session.selectedStructureIds, []);
});

test("a fake clock advances clip time at selected playback speed and clamps at the end", () => {
  const { ready } = readyState();
  const playing = playMotion(setMotionSpeed(ready, 0.5));
  assert.equal(playing.session.status, "playing");
  assert.deepEqual(playing.session.selectedStructureIds, ["muscle-1", "bone-1"]);
  const halfSecond = setMotionTime(playing, playing.session.currentTimeSeconds + 1 * playing.session.playbackSpeed);
  assert.equal(halfSecond.session.currentTimeSeconds, 0.5);
  assert.equal(halfSecond.session.status, "playing");
  const ended = setMotionTime(halfSecond, 2);
  assert.equal(ended.session.currentTimeSeconds, 2);
  assert.equal(ended.session.status, "paused");
});

test("action and region changes invalidate late loads and clear emphasis", () => {
  const loading = beginMotionAssetLoad(createMotionPlayerState("action-1"));
  const changedAction = selectMotionAction(loading.state, "action-2");
  assert.equal(changedAction.session.status, "idle");
  assert.equal(changedAction.session.assetId, null);
  assert.deepEqual(changedAction.session.selectedStructureIds, []);
  assert.equal(acceptMotionAssetLoad(changedAction, loading.requestToken!, {
    actionId: "action-1", definitionId: "definition-1", assetId: "asset-1", durationSeconds: 2, structureIds: ["muscle-1"],
  }), changedAction);
  const ready = readyState().ready;
  const playing = playMotion(ready);
  const changedRegion = changeMotionContext(playing);
  assert.equal(changedRegion.session.status, "idle");
  assert.deepEqual(changedRegion.session.selectedStructureIds, []);
});

test("load errors stop playback and clear selected structure emphasis", () => {
  const { ready } = readyState();
  const playing = playMotion(ready);
  const pending = beginMotionAssetLoad(playing);
  const failed = failMotionAssetLoad(pending.state, pending.requestToken!);
  assert.equal(failed.session.status, "error");
  assert.equal(failed.session.assetId, null);
  assert.deepEqual(failed.session.selectedStructureIds, []);
  assert.equal(failed.session.errorMessage, "시범 자료를 불러오지 못했습니다. 글 설명은 계속 확인할 수 있습니다.");
});

test("reduced motion prevents play and keeps a loaded clip at its initial pose", () => {
  const { ready } = readyState();
  const preference = setReducedMotionPreference(ready, true);
  assert.equal(playMotion(preference).session.status, "paused");
  assert.equal(seekMotionProgress(preference, 0.6).session.currentTimeSeconds, 1.2);
  const staticPose = resetMotionPose(seekMotionProgress(preference, 0.6));
  assert.equal(staticPose.session.currentTimeSeconds, 0);
  assert.equal(staticPose.session.status, "ready");
  assert.equal(staticPose.prefersReducedMotion, true);
});

test("progress seeks are clamped and pose reset is independent from speed and camera state", () => {
  const { ready } = readyState();
  const slow = setMotionSpeed(ready, 0.5);
  const end = seekMotionProgress(slow, 4);
  assert.equal(end.session.currentTimeSeconds, 2);
  assert.equal(end.session.status, "paused");
  const reset = resetMotionPose(end);
  assert.equal(reset.session.currentTimeSeconds, 0);
  assert.equal(reset.session.playbackSpeed, 0.5);
  assert.deepEqual(reset.session.selectedStructureIds, []);
});

test("pause keeps the sampled pose and can resume without returning to rest", () => {
  const { ready } = readyState();
  const playing = playMotion(setMotionTime(playMotion(ready), 0.7));
  const paused = pauseMotion(playing);
  assert.equal(paused.session.status, "paused");
  assert.equal(paused.session.currentTimeSeconds, playing.session.currentTimeSeconds);
  assert.deepEqual(paused.session.selectedStructureIds, playing.session.selectedStructureIds);
  const resumed = playMotion(paused);
  assert.equal(resumed.session.status, "playing");
  assert.equal(resumed.session.currentTimeSeconds, paused.session.currentTimeSeconds);
});

test("stale errors and malformed duration cannot replace a newer session", () => {
  const first = beginMotionAssetLoad(createMotionPlayerState("action-1"));
  const second = beginMotionAssetLoad(selectMotionAction(first.state, "action-2"));
  assert.equal(failMotionAssetLoad(second.state, first.requestToken!), second.state);
  const malformed = acceptMotionAssetLoad(second.state, second.requestToken!, {
    actionId: "action-2", definitionId: "definition-2", assetId: "asset-2", durationSeconds: 0,
    structureIds: ["muscle-2"],
  });
  assert.equal(malformed.session.status, "error");
});

test("reset while loading invalidates the pending response", () => {
  const loading = beginMotionAssetLoad(createMotionPlayerState("action-1"));
  const reset = resetMotionPose(loading.state);
  assert.equal(reset.session.status, "idle");
  assert.notEqual(reset.generation, loading.requestToken);
  assert.equal(acceptMotionAssetLoad(reset, loading.requestToken!, {
    actionId: "action-1", definitionId: "definition-1", assetId: "asset-1", durationSeconds: 2, structureIds: ["muscle-1"],
  }), reset);
});

test("hiding the page cancels a pending load and clears active playback emphasis", () => {
  const loading = beginMotionAssetLoad(createMotionPlayerState("action-1"));
  const hiddenLoading = suspendMotionForHiddenPage(loading.state);
  assert.equal(hiddenLoading.session.status, "idle");
  assert.notEqual(hiddenLoading.generation, loading.requestToken);
  assert.equal(acceptMotionAssetLoad(hiddenLoading, loading.requestToken!, {
    actionId: "action-1", definitionId: "definition-1", assetId: "asset-1", durationSeconds: 2, structureIds: ["muscle-1"],
  }), hiddenLoading);

  const { ready } = readyState();
  const playing = playMotion(ready);
  const hiddenPlaying = suspendMotionForHiddenPage(playing);
  assert.equal(hiddenPlaying.session.status, "paused");
  assert.deepEqual(hiddenPlaying.session.selectedStructureIds, []);
  assert.equal(hiddenPlaying.session.assetId, "asset-1");
});

test("the renderer loop stays playing at exact endpoints and return/scrub cannot restart it", () => {
  const playing = playMotion(readyState().ready);
  const sampledEnd = syncMotionPlaybackTime(playing, 2, true);
  assert.equal(sampledEnd.session.status, "playing");
  assert.equal(syncMotionPlaybackTime(sampledEnd, 1, true).session.status, "playing");
  const stalePausedUi = pauseMotion(sampledEnd);
  assert.equal(syncMotionPlaybackTime(stalePausedUi, 1, true).session.status, "playing");
  const returning = syncMotionPlaybackTime(sampledEnd, 1, false);
  assert.equal(returning.session.status, "paused");
  assert.deepEqual(returning.session.selectedStructureIds, []);
  assert.equal(syncMotionPlaybackTime(returning, 0, false).session.status, "ready");
});
