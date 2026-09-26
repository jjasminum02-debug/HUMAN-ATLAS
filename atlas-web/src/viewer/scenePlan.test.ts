import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import type { NavigationContract, SceneManifest } from "../domain/navigation.ts";
import { assertCompatibleSceneGroup, sceneRevision } from "./scenePlan.ts";

const navigation = JSON.parse(readFileSync(new URL("../../../atlas-data/navigation/atlas-navigation.json", import.meta.url), "utf8")) as NavigationContract;
const leg = navigation.sceneManifests;
const changed = (scene: SceneManifest, patch: Partial<SceneManifest>): SceneManifest => ({ ...scene, ...patch });

test("both source model scenes share only the verified leg frame and pose", () => {
  assert.equal(leg.length, 2);
  assert.doesNotThrow(() => assertCompatibleSceneGroup(leg));
  assert.equal(leg.flatMap((scene) => scene.assetRefs.flatMap((asset) => asset.meshAssetIds)).length, 20);
  assert.equal(leg.flatMap((scene) => scene.selectableBindings).length, 16);
  assert.equal(leg.flatMap((scene) => scene.contextBindings).length, 4);
});

test("frame, pose, region, side, missing asset, and duplicate model fail closed", () => {
  for (const patch of [{ frameId: "OTHER" }, { poseId: "OTHER" }, { categoryId: "head" }, { defaultView: { side: "left" as const, selection: null } }]) {
    assert.throws(() => assertCompatibleSceneGroup([leg[0], changed(leg[1], patch)]));
  }
  assert.throws(() => assertCompatibleSceneGroup([changed(leg[0], { assetRefs: [] })]), /자산/);
  assert.throws(() => assertCompatibleSceneGroup([leg[0], leg[0]]), /중복/);
});

test("asset revision changes the cache key without changing anatomy IDs", () => {
  const previous = sceneRevision(leg);
  const altered = changed(leg[1], { revision: "next", assetRefs: [{ ...leg[1].assetRefs[0], sha256: "a".repeat(64) }] });
  assert.notEqual(sceneRevision([leg[0], altered]), previous);
});
