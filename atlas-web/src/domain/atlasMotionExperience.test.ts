import assert from "node:assert/strict";
import test from "node:test";
import { buildMotionActionLibrary, muscleActionEmphasis, motionActionLabel, motionLearningIntent, motionLearningTitle, preferredMotionAction } from "./atlasMotionExperience.ts";
import type { LearnerMotionActionOption } from "./motionLearning.ts";

test("a selected muscle's verified action wins over an earlier playable surrounding pose", () => {
  const context = { id: "shoulder-rotation-context", candidate: {} as NonNullable<LearnerMotionActionOption["candidate"]>, learningIntent: "posture_observation" as const };
  const action = { id: "verified-muscle-action", candidate: {} as NonNullable<LearnerMotionActionOption["candidate"]>, learningIntent: "muscle_action" as const };
  assert.equal(preferredMotionAction([context, action])?.id, action.id);
  assert.equal(motionLearningIntent({ candidate: context.candidate }), "posture_observation");
  assert.notEqual(motionLearningTitle(motionLearningIntent(context)), "근육의 작용");
});

test("observation wording is cleaned without expanding a partial or initial movement range", () => {
  assert.equal(motionActionLabel("어깨 벌림 시작 구간 관찰 자세 관찰"), "어깨 벌림 시작 구간");
  assert.equal(motionActionLabel("어깨 앞쪽 굽힘 자세에서 관찰"), "어깨 앞쪽 굽힘");
  assert.equal(motionActionLabel("하부 경추 일부 굽힘 자세에서 관찰"), "하부 경추 일부 굽힘");
});

test("the action library excludes contextual poses and unavailable actions and retains exact sides", () => {
  const action = { id: "thumb-action", label: "엄지 벌림", candidate: {} as NonNullable<LearnerMotionActionOption["candidate"]>, learningIntent: "muscle_action" as const } as LearnerMotionActionOption;
  const subjects = [
    { sourceKey: "left-thumb", name: "엄지벌림근", side: "left", regionIds: ["hand"], action },
    { sourceKey: "right-thumb", name: "엄지벌림근", side: "right", regionIds: ["hand"], action },
    { sourceKey: "context", name: "주변 근육", side: "left", regionIds: ["hand"], action: { ...action, learningIntent: "posture_observation" as const } },
    { sourceKey: "missing", name: "미지원 근육", side: "left", regionIds: ["hand"], action: { ...action, candidate: null } },
  ];
  const library = buildMotionActionLibrary([...subjects, subjects[0]]);
  assert.equal(library.length, 1);
  assert.deepEqual(library[0].subjects.map(row => row.sourceKey), ["left-thumb", "right-thumb"]);
});

test("action emphasis fades smoothly during reset without treating a held pose as activation", () => {
  assert.equal(muscleActionEmphasis("action", 0), 0);
  assert.equal(muscleActionEmphasis("action", 0.2), 1);
  assert.equal(muscleActionEmphasis("return", 1), 1);
  assert.equal(muscleActionEmphasis("return", 0.5), 0.5);
  assert.equal(muscleActionEmphasis("return", 0), 0);
  assert.equal(muscleActionEmphasis("held", 0.8), null);
});
