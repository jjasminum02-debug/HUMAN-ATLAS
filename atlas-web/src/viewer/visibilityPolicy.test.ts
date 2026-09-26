import assert from "node:assert/strict";
import test from "node:test";
import { isFocusDimmed, pickThroughTransparent, visibilityAfterRestore, type MeshVisibility } from "./visibilityPolicy.ts";

const hit = (meshAssetId: string) => ({ meshAssetId });

test("pointer passes through a transparent muscle to the first solid deep structure", () => {
  const hits = [hit("surface-muscle"), hit("deep-muscle"), hit("bone")];
  const visibility: Record<string, MeshVisibility> = {
    "surface-muscle": "transparent",
    "deep-muscle": "visible",
    bone: "visible",
  };
  assert.equal(pickThroughTransparent(hits, (id) => visibility[id])?.meshAssetId, "deep-muscle");
});

test("pointer can reach the deepest dimmed muscle when all intersected muscles are faded", () => {
  const hits = [hit("outer"), hit("middle"), hit("deep"), hit("outer")];
  assert.equal(pickThroughTransparent(hits, () => "transparent")?.meshAssetId, "deep");
});

test("hidden candidates are skipped and never become a fallback", () => {
  const hits = [hit("hidden"), hit("transparent")];
  assert.equal(pickThroughTransparent(hits, (id) => id === "hidden" ? "hidden" : "transparent")?.meshAssetId, "transparent");
  assert.equal(pickThroughTransparent([hit("hidden")], () => "hidden"), undefined);
});

test("focus fade affects surrounding muscles only while enabled and preserves related bones", () => {
  const focused = new Set(["selected-muscle"]);
  assert.equal(isFocusDimmed("other-muscle", "muscle", focused, true), true);
  assert.equal(isFocusDimmed("selected-muscle", "muscle", focused, true), false);
  assert.equal(isFocusDimmed("bone", "structure", focused, true), false);
  assert.equal(isFocusDimmed("other-muscle", "muscle", focused, false), false);
  assert.equal(isFocusDimmed("other-muscle", "muscle", new Set(), true), false);
});

test("learner restore preserves hidden and transparent base state while author restore shows all", () => {
  assert.equal(visibilityAfterRestore("hidden", true), "hidden");
  assert.equal(visibilityAfterRestore("transparent", true), "transparent");
  assert.equal(visibilityAfterRestore("hidden", false), "visible");
});
