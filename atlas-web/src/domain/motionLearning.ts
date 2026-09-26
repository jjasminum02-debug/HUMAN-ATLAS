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
  representationType: "rigged_mesh" | "illustrative_path" | "bone_motion_with_illustrative_path";
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
  stabilizationNote: string | null;
  contextNotes: Array<{ label: string; explanation: string }>;
  contractionNote: string;
  citations: LearnerActionCitation[];
}

export interface LearnerActionCitation {
  section: "action" | "posture" | "role" | "stabilization";
  title: string;
  url: string;
  edition: string | null;
  locator: string;
  accessedOn: string;
}

export interface ActionCitationEvidenceField {
  id: string;
  evidence: Array<{ id: string; sourceId: string; locator: string; accessedOn: string }>;
  sources: Array<{ id: string; title: string; url: string; edition: string | null }>;
}

export function projectLearnerActionText(
  action: MuscleAction | undefined,
  citations: readonly LearnerActionCitation[] = [],
): LearnerActionText | null {
  if (!action || !action.explanation.trim()) return null;
  return {
    label: action.actionLabel,
    explanation: action.explanation,
    postureConditions: [...action.postureConditions],
    stabilizationConditions: action.stabilizationConditions.map((condition) => condition.description),
    stabilizationNote: action.stabilizationNote,
    contextNotes: action.contextRoles.map((context) => ({
      label: context.role === "stabilizer" ? "출처가 설명한 지지 역할" : "출처에서 확인한 맥락",
      explanation: context.explanation,
    })),
    contractionNote: action.contextRoles.some((context) => context.contractionRole === "unspecified")
      ? "조사한 자료는 개별 근육의 수축 종류를 따로 구분하지 않았습니다."
      : "",
    citations: [...citations],
  };
}

/** Resolve only citations explicitly referenced by an action; keep review and geometry states private. */
export function projectLearnerActionCard(
  action: MuscleAction | undefined,
  fields: readonly ActionCitationEvidenceField[],
): LearnerActionText | null {
  if (!action) return null;
  const scopeToSection: Record<EvidenceRef["appliesTo"], LearnerActionCitation["section"] | null> = {
    action_explanation: "action",
    posture_condition: "posture",
    context_role: "role",
    stabilization_condition: "stabilization",
    motion_pose_range: null,
  };
  const citations: LearnerActionCitation[] = [];
  for (const ref of action.sourceRefs) {
    const section = scopeToSection[ref.appliesTo];
    if (!section || !ref.fieldEvidenceId) continue;
    const field = fields.find((row) => row.id === ref.fieldEvidenceId);
    const evidence = field?.evidence.find((row) => row.id === ref.evidenceId);
    const source = evidence && field?.sources.find((row) => row.id === evidence.sourceId);
    if (!evidence || !source) continue;
    citations.push({ section, title: source.title, url: source.url, edition: source.edition, locator: evidence.locator, accessedOn: evidence.accessedOn });
  }
  const uniqueCitations = citations.filter((citation, index, rows) => rows.findIndex((row) =>
    row.section === citation.section && row.url === citation.url && row.locator === citation.locator,
  ) === index);
  return projectLearnerActionText(action, uniqueCitations);
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
    : asset.representationType === "bone_motion_with_illustrative_path"
      ? asset.rig?.nodeBindings.map((row) => row.structureId).sort() ?? []
      : asset.illustration?.trajectoryBindings.map((row) => row.structureId).sort() ?? [];
  const pathSubjects = asset.illustration?.trajectoryBindings.map((row) => row.structureId).sort() ?? [];
  const expectedPathSubjects = [...action.subjectIds].sort();
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
    && (asset.representationType !== "bone_motion_with_illustrative_path"
      || JSON.stringify(pathSubjects) === JSON.stringify(expectedPathSubjects))
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
