/** Typed, provenance-bound action/motion domain. MotionSession is runtime-only. */
export type Laterality = "right" | "left" | "bilateral" | "midline" | "not_applicable";
export type ContractionRole = "concentric" | "eccentric" | "isometric" | "stabilizing" | "unspecified";
export type ActionRole = "agonist" | "antagonist" | "synergist" | "fixator" | "stabilizer" | "unspecified";

export interface EvidenceRef {
  layer: "canonical_claim" | "ai_field";
  field: string;
  appliesTo: "action_explanation" | "posture_condition" | "stabilization_condition" | "context_role" | "motion_pose_range";
  contextId: string | null;
  claimId: string;
  valueHash: string;
  evidenceId: string;
  fieldEvidenceId: string | null;
}

export interface ActionCondition {
  description: string;
  structureIds: string[];
}

export interface ActionContextRole {
  contextId: string;
  role: ActionRole;
  contractionRole: ContractionRole;
  explanation: string;
}

export interface MuscleAction {
  id: string;
  subjectIds: string[];
  sideApplicability: Laterality;
  jointBindingState: "canonical_bound" | "unmapped";
  jointBindingNote: string | null;
  targetJointIds: string[];
  actionLabel: string;
  explanation: string;
  postureConditions: string[];
  stabilizationConditions: ActionCondition[];
  stabilizationNote: string | null;
  contextRoles: ActionContextRole[];
  sourceRefs: EvidenceRef[];
  legacyJointActionId?: string | null;
}

export interface StaticReference {
  sceneId: string;
  sceneRevision: string;
  modelId: string;
  sourceAssetSha256: string;
  frameId: string;
  units: "m" | "mm";
  poseId: string;
}

export interface MotionDefinition {
  id: string;
  actionId: string;
  instanceId: string;
  side: Laterality;
  targetJointIds: string[];
  movingStructureIds: string[];
  fixedStructureIds: string[];
  staticReference: StaticReference;
  startPoseId: string;
  endPoseId: string;
  poseSourceRefs: EvidenceRef[];
}

export interface MotionAsset {
  id: string;
  motionDefinitionId: string;
  uri: string;
  revision: string;
  sha256: string;
  sourceId: string;
  licenseId: string;
  representationType: "rigged_mesh" | "illustrative_path";
  staticBinding: {
    sceneId: string;
    sceneRevision: string;
    modelId: string;
    sourceAssetSha256: string;
    frameId: string;
    units: "m" | "mm";
    side: Laterality;
    referencePoseId: string;
  };
  rig: { id: string; nodeBindings: Array<{ structureId: string; nodeId: string }> } | null;
  illustration: { id: string; trajectoryBindings: Array<{ structureId: string; trajectoryId: string }> } | null;
  clip: { id: string; durationSeconds: number; startPoseId: string; endPoseId: string };
  /** Technical validation only. It is not human review or educational release. */
  technicalStatus: "candidate" | "binding_verified";
}

export interface MotionLearningBundle {
  schemaVersion: "1.0.0";
  revision: string;
  muscleActions: MuscleAction[];
  motionDefinitions: MotionDefinition[];
  motionAssets: MotionAsset[];
}

/** Safe explanatory text projection. It contains no review codes or authoring IDs. */
export interface LearnerActionText {
  label: string;
  explanation: string;
  postureConditions: string[];
  stabilizationConditions: string[];
}

export function projectLearnerActionText(action: MuscleAction | undefined): LearnerActionText | null {
  if (!action || !action.explanation.trim()) return null;
  return {
    label: action.actionLabel,
    explanation: action.explanation,
    postureConditions: [...action.postureConditions],
    stabilizationConditions: action.stabilizationConditions.map((condition) => condition.description),
  };
}

export interface MotionCapability {
  hasActionText: boolean;
  hasTechnicallyCompatibleClip: boolean;
}

/** A technical capability check, not a review or release decision. */
export function assessMotionCapability(
  action: MuscleAction | undefined,
  definition: MotionDefinition | undefined,
  asset: MotionAsset | undefined,
): MotionCapability {
  const hasActionText = Boolean(action?.explanation.trim());
  if (!action || !definition || !asset || asset.technicalStatus !== "binding_verified") {
    return { hasActionText, hasTechnicallyCompatibleClip: false };
  }
  const ref = definition.staticReference;
  const binding = asset.staticBinding;
  const expectedMoving = [...definition.movingStructureIds].sort();
  const actualMoving = asset.representationType === "rigged_mesh"
    ? asset.rig?.nodeBindings.map((row) => row.structureId).sort() ?? []
    : asset.illustration?.trajectoryBindings.map((row) => row.structureId).sort() ?? [];
  const compatible = definition.actionId === action.id
    && asset.motionDefinitionId === definition.id
    && definition.side === asset.staticBinding.side
    && binding.sceneId === ref.sceneId
    && binding.sceneRevision === ref.sceneRevision
    && binding.modelId === ref.modelId
    && binding.sourceAssetSha256 === ref.sourceAssetSha256
    && binding.frameId === ref.frameId
    && binding.units === ref.units
    && binding.referencePoseId === ref.poseId
    && definition.startPoseId === ref.poseId
    && asset.clip.startPoseId === definition.startPoseId
    && asset.clip.endPoseId === definition.endPoseId
    && JSON.stringify(expectedMoving) === JSON.stringify(actualMoving);
  return { hasActionText, hasTechnicallyCompatibleClip: compatible };
}

export type MotionSessionStatus = "idle" | "loading" | "ready" | "playing" | "paused" | "error";

/** Runtime state only; never serialize this interface into content data. */
export interface MotionSession {
  status: MotionSessionStatus;
  definitionId: string | null;
  assetId: string | null;
  currentTimeSeconds: number;
  playbackSpeed: number;
  selectedStructureIds: string[];
  errorMessage: string | null;
}

export function createIdleMotionSession(selectedStructureIds: readonly string[] = []): MotionSession {
  return {
    status: "idle",
    definitionId: null,
    assetId: null,
    currentTimeSeconds: 0,
    playbackSpeed: 1,
    selectedStructureIds: [...selectedStructureIds],
    errorMessage: null,
  };
}
