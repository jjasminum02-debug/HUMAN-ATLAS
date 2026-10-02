import assert from "node:assert/strict";
import test from "node:test";
import type { MotionAsset } from "./motionLearning.ts";
import { motionSubjectExplanation, selectedMotionSubjectRole } from "./motionSubjectPresentation.ts";

const asset = {
  staticBinding: { side: "left" },
  sourceBinding: {
    members: [
      { sourceKey: "left-femur", side: "left", role: "fixed_structure" },
      { sourceKey: "left-tibia", side: "left", role: "moving_structure" },
      { sourceKey: "left-rectus", side: "left", role: "deforming_passive_surface" },
      { sourceKey: "right-tibia", side: "right", role: "moving_structure" },
    ],
  },
} as unknown as MotionAsset;

test("selected source role requires exact key and side", () => {
  assert.equal(selectedMotionSubjectRole(asset, "left-femur"), "fixed_structure");
  assert.equal(selectedMotionSubjectRole(asset, "left-tibia"), "moving_structure");
  assert.equal(selectedMotionSubjectRole(asset, "left-rectus"), "deforming_passive_surface");
  assert.equal(selectedMotionSubjectRole(asset, "right-tibia"), null);
  assert.equal(selectedMotionSubjectRole(asset, "missing"), null);
});

test("learner explanations distinguish fixed bone, moving bone, and passive muscle", () => {
  const fixed = motionSubjectExplanation("bone", "fixed_structure");
  const moving = motionSubjectExplanation("bone", "moving_structure");
  const passive = motionSubjectExplanation("muscle", "deforming_passive_surface");
  assert.match(fixed, /고정된 기준 구조/);
  assert.doesNotMatch(fixed, /선택한 뼈가 .* 이동합니다/);
  assert.match(moving, /선택한 뼈가 .* 이동합니다/);
  assert.match(passive, /수동 변형/);
  assert.match(passive, /활성도나 주작용을 뜻하지 않습니다/);
});
