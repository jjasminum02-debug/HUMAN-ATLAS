import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import { assessMotionCapability, createIdleMotionSession, projectLearnerActionText, projectLearnerMotionActionOptions, resolveLearnerMotionCandidate, type MotionAsset, type MotionDefinition, type MuscleAction, type MotionLearningBundle } from "./motionLearning.ts";

const production = JSON.parse(readFileSync(new URL("../../../atlas-data/motion/motion-learning.json", import.meta.url), "utf8")) as {
  muscleActions: unknown[]; motionDefinitions: unknown[]; motionAssets: unknown[];
};

const action: MuscleAction = {
  id: "FX-ACTION-1", subjectIds: ["FX-MUSCLE-1"], sideApplicability: "right", jointBindingState: "canonical_bound", jointBindingNote: null, targetJointIds: ["FX-JOINT-1"],
  actionLabel: "fixture-only action", explanation: "fixture-only text; not an anatomical claim", postureConditions: ["fixture-only position"],
  stabilizationConditions: [{ description: "fixture-only stabilization", structureIds: ["FX-BONE-FIXED"] }], stabilizationNote: null,
  contextRoles: [
    { contextId: "FX-CONTEXT-1", role: "agonist", contractionRole: "concentric", explanation: "fixture-only role" },
    { contextId: "FX-CONTEXT-2", role: "stabilizer", contractionRole: "isometric", explanation: "fixture-only role in a separate context" },
  ],
  sourceRefs: [
    { layer: "ai_field", field: "fixture_action", appliesTo: "action_explanation", contextId: null },
    { layer: "ai_field", field: "fixture_action", appliesTo: "posture_condition", contextId: null },
    { layer: "ai_field", field: "fixture_action", appliesTo: "stabilization_condition", contextId: null },
    { layer: "ai_field", field: "fixture_action", appliesTo: "context_role", contextId: "FX-CONTEXT-1" },
    { layer: "ai_field", field: "fixture_action", appliesTo: "context_role", contextId: "FX-CONTEXT-2" },
  ].map((row) => ({ ...row, claimId: "FX-CLAIM-1", valueHash: "a".repeat(64), evidenceId: "FX-EVIDENCE-1", fieldEvidenceId: "FX-FIELD-1" })) as MuscleAction["sourceRefs"],
};
const definition: MotionDefinition = {
  id: "FX-DEFINITION-1", actionId: action.id, instanceId: "FX-INSTANCE-R", side: "right", targetJointIds: ["FX-JOINT-1"],
  movingStructureIds: ["FX-BONE-MOVING"], fixedStructureIds: ["FX-BONE-FIXED"],
  staticReference: { sceneId: "FX-SCENE-1", sceneRevision: "fixture-rev", modelId: "FX-MODEL-1", sourceAssetSha256: "b".repeat(64), frameId: "FX-FRAME", units: "m", poseId: "FX-STATIC-POSE" },
  startPoseId: "FX-STATIC-POSE", endPoseId: "FX-MOTION-POSE", poseSourceRefs: [{ layer: "ai_field", field: "fixture_pose", appliesTo: "motion_pose_range", contextId: null, claimId: "FX-POSE-CLAIM", valueHash: "c".repeat(64), evidenceId: "FX-POSE-EVIDENCE", fieldEvidenceId: "FX-POSE-FIELD" }],
};
const asset: MotionAsset = {
  id: "FX-ASSET-1", motionDefinitionId: definition.id, uri: "fixture://assets/fixture-motion.bin", revision: "fixture-asset-rev", sha256: "d".repeat(64), sourceId: "FX-SOURCE-1",
  licenseId: "FX-LICENSE-1", representationType: "rigged_mesh",
  staticBinding: { sceneId: definition.staticReference.sceneId, sceneRevision: definition.staticReference.sceneRevision, modelId: definition.staticReference.modelId, sourceAssetSha256: definition.staticReference.sourceAssetSha256, frameId: definition.staticReference.frameId, units: "m", side: "right", referencePoseId: definition.staticReference.poseId },
  rig: { id: "FX-RIG-1", nodeBindings: [{ structureId: "FX-BONE-MOVING", nodeId: "node-1" }] },
  illustration: null,
  clip: { id: "FX-CLIP-1", durationSeconds: 1, startPoseId: definition.startPoseId, endPoseId: definition.endPoseId },
  technicalStatus: "binding_verified",
};

test("production bundle retains six original texts and adds one right ankle source-bound clip", () => {
  assert.equal((production.muscleActions as MuscleAction[]).filter(a => a.subjectKind !== "bone" && !a.sourceFamilyId).length, 8);
  assert.equal((production.muscleActions as MuscleAction[]).filter(a => a.subjectKind === "bone" && !a.sourceFamilyId).length, 27);
  assert.equal(production.motionDefinitions.length, 275);
  assert.equal(production.motionAssets.length, 275);
  const actions = production.muscleActions as MuscleAction[];
  assert.deepEqual(actions.slice(0, 6).map((row) => row.subjectIds[0]), [
    "HA-M-000001", "HA-M-000002", "HA-M-000003", "HA-M-000004", "HA-M-000005", "HA-M-000006",
  ]);
  assert.ok(actions.slice(0, 6).every((row) => row.jointBindingState === "unmapped" && row.targetJointIds.length === 0 && row.sourceRefs.length > 0));
  assert.equal(actions[6].sideApplicability, "right");
  assert.deepEqual(actions[6].targetJointIds, ["HA-S-JOINT-R-ANKLE-TALOCRURAL"]);
  assert.equal((production.motionAssets[0] as MotionAsset).representationType, "bone_motion_with_illustrative_path");
  const authored = production.motionAssets[1] as MotionAsset;
  assert.equal(authored.representationType, "source_bound_surface");
  assert.equal(authored.sourceBinding?.subjectSourceKey, "ZA-c7010a9-54ae5266082b61f48ed8e83e");
  assert.equal(authored.staticBinding.side, "right");
  assert.equal(authored.technicalStatus, "binding_verified");
});

test("text can be present while there is no compatible motion clip", () => {
  assert.deepEqual(projectLearnerActionText(action)?.explanation, action.explanation);
  assert.deepEqual(assessMotionCapability(action, undefined, undefined), { hasActionText: true, hasTechnicallyCompatibleClip: false });
  const textOnlyUnmapped = { ...action, jointBindingState: "unmapped" as const, jointBindingNote: "fixture-only; canonical joint unavailable", targetJointIds: [] };
  assert.deepEqual(assessMotionCapability(textOnlyUnmapped, undefined, undefined), { hasActionText: true, hasTechnicallyCompatibleClip: false });
});

test("learner card motion linking requires an explicit action key and compatible side", () => {
  const candidate = { definition, asset };
  const projected = [
    { learnerActionKey: "option-3", sideApplicability: "right" as const, candidate },
    { learnerActionKey: null, sideApplicability: "right" as const, candidate },
    { learnerActionKey: "option-4", sideApplicability: "right" as const, candidate },
  ];
  assert.deepEqual(resolveLearnerMotionCandidate("option-3", "right", projected), candidate);
  assert.equal(resolveLearnerMotionCandidate("option-3", "left", projected), null);
  assert.equal(resolveLearnerMotionCandidate("option-unknown", "right", projected), null, "label similarity is not an association");
  assert.equal(resolveLearnerMotionCandidate("option-3", "right", [projected[0], projected[0]]), null, "duplicate action links fail closed");
});

test("clip capability requires exact static scene, side, frame, reference pose, and rig-node binding", () => {
  assert.deepEqual(assessMotionCapability(action, definition, asset), { hasActionText: true, hasTechnicallyCompatibleClip: true });
  const pathAsset: MotionAsset = { ...asset, representationType: "illustrative_path", rig: null, illustration: { id: "FX-ILLUSTRATION-1", trajectoryBindings: [{ structureId: "FX-BONE-MOVING", trajectoryId: "trajectory-1" }] } };
  assert.deepEqual(assessMotionCapability(action, definition, pathAsset), { hasActionText: true, hasTechnicallyCompatibleClip: true });
  const boneAndPathDefinition: MotionDefinition = { ...definition, movingStructureIds: ["FX-BONE-MOVING"] };
  const boneAndPathAsset: MotionAsset = {
    ...asset,
    representationType: "bone_motion_with_illustrative_path",
    illustration: { id: "FX-ILLUSTRATION-2", trajectoryBindings: [{ structureId: action.subjectIds[0], trajectoryId: "path-node-1" }] },
  };
  assert.deepEqual(assessMotionCapability(action, boneAndPathDefinition, boneAndPathAsset), { hasActionText: true, hasTechnicallyCompatibleClip: true });
  assert.equal(assessMotionCapability(action, boneAndPathDefinition, { ...boneAndPathAsset, illustration: null }).hasTechnicallyCompatibleClip, false);
  const wrongPose = { ...asset, staticBinding: { ...asset.staticBinding, referencePoseId: "FX-OTHER-POSE" } };
  assert.equal(assessMotionCapability(action, definition, wrongPose).hasTechnicallyCompatibleClip, false);
  const wrongSide = { ...asset, staticBinding: { ...asset.staticBinding, side: "left" as const } };
  assert.equal(assessMotionCapability(action, definition, wrongSide).hasTechnicallyCompatibleClip, false);
  const wrongFrame = { ...asset, staticBinding: { ...asset.staticBinding, frameId: "FX-OTHER-FRAME" } };
  assert.equal(assessMotionCapability(action, definition, wrongFrame).hasTechnicallyCompatibleClip, false);
  const wrongSceneRevision = { ...asset, staticBinding: { ...asset.staticBinding, sceneRevision: "FX-OTHER-REVISION" } };
  assert.equal(assessMotionCapability(action, definition, wrongSceneRevision).hasTechnicallyCompatibleClip, false);
  const missingRigNode = { ...asset, rig: { id: asset.rig!.id, nodeBindings: [] } };
  assert.equal(assessMotionCapability(action, definition, missingRigNode).hasTechnicallyCompatibleClip, false);
});

test("runtime session is resettable state and exposes no persisted content/review fields", () => {
  assert.deepEqual(createIdleMotionSession(["FX-BONE-MOVING"]), {
    status: "idle", definitionId: null, assetId: null, currentTimeSeconds: 0, playbackSpeed: 1,
    selectedStructureIds: ["FX-BONE-MOVING"], errorMessage: null,
  });
  assert.equal("humanReviewed" in createIdleMotionSession(), false);
  assert.equal("reviewState" in createIdleMotionSession(), false);
});

test("learner text projection omits authoring IDs, JSON, task codes, and review states", () => {
  const output = JSON.stringify(projectLearnerActionText(action));
  assert.doesNotMatch(output, /FX-|reviewed|needs_review|T20|JSON/);
});

test("learner action projection translates roles and unspecified contraction into plain Korean", () => {
  const actionWithUnspecifiedRole = { ...action, contextRoles: [action.contextRoles[0]!, { ...action.contextRoles[1]!, contractionRole: "unspecified" as const }] };
  const output = projectLearnerActionText(actionWithUnspecifiedRole, [{
    section: "action", title: "Source title", url: "https://example.org/source", edition: "Edition",
    locator: "Action column", accessedOn: "2026-09-27",
  }]);
  assert.equal(output?.contextNotes[1]?.label, "출처가 설명한 지지 역할");
  assert.match(output?.contractionNote ?? "", /수축 종류를 따로 구분하지 않았습니다/);
  assert.equal(output?.citations[0]?.locator, "Action column");
  const serialized = JSON.stringify(output);
  assert.doesNotMatch(serialized, /stabilizer|unspecified|FX-|reviewed|needs_review/);
});

test("source-only action and clip resolve by exact sourceKey without creating a canonical subject", () => {
  const sourceKey = "ZA-fixture-muscle-right";
  const sourceAction: MuscleAction = {
    ...action, id: "T59-FIXTURE-SOURCE-ACTION", subjectIds: [], sourceSubjectKeys: [sourceKey],
    learnerActionKey: "option-source-flexion", sideApplicability: "right",
  };
  const sourceDefinition: MotionDefinition = {
    ...definition, id: "T59-FIXTURE-SOURCE-DEFINITION", actionId: sourceAction.id, instanceId: sourceKey,
  };
  const sourceAsset: MotionAsset = {
    ...asset, id: "T59-FIXTURE-SOURCE-ASSET", motionDefinitionId: sourceDefinition.id, representationType: "source_bound_surface",
    sourceBinding: {
      contractVersion: "t59-source-motion-binding-v1", datasetNamespace: "fixture-dataset", datasetRevision: "fixture-revision",
      integrationRevision: "fixture-integration", sourceOverlaySha256: "e".repeat(64), subjectSourceKey: sourceKey,
      frameId: sourceDefinition.staticReference.frameId, units: "m", referencePoseId: sourceDefinition.startPoseId, deformation: "morph_targets",
      members: [{ sourceKey, nodeId: "fixture-surface", sourceNamespace: "za-fixture", role: "deforming_muscle_surface", side: "right",
        resourceKey: "fixture-resource", lod: "detail", sourceChunkSha256: "f".repeat(64), geometrySha256: "1".repeat(64),
        instanceMatrix: [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1] }],
    },
  };
  const bundle: MotionLearningBundle = { schemaVersion: "1.0.0", revision: "fixture", muscleActions: [sourceAction],
    motionDefinitions: [sourceDefinition], motionAssets: [sourceAsset] };
  const [option] = projectLearnerMotionActionOptions(sourceKey, bundle, [], "right");
  assert.equal(option?.id, "option-source-flexion");
  assert.deepEqual(option?.subjectIds, [sourceKey]);
  assert.equal(option?.candidate?.asset.id, sourceAsset.id);
  assert.equal(projectLearnerMotionActionOptions(sourceKey, bundle, [], "left").length, 0);
  assert.equal(projectLearnerMotionActionOptions("ZA-other-source", bundle, [], "right").length, 0);
});
