/** Typed, provenance-bound action/motion domain. MotionSession is runtime-only. */
export type Laterality = "right" | "left" | "bilateral" | "midline" | "not_applicable";
export type ContractionRole = "concentric" | "eccentric" | "isometric" | "stabilizing" | "unspecified";
export type ActionRole = "agonist" | "antagonist" | "synergist" | "fixator" | "stabilizer" | "unspecified";

export interface EvidenceRef {
  layer: "canonical_claim" | "ai_field" | "authoring_record";
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
  subjectKind?: "muscle" | "bone";
  id: string;
  subjectIds: string[];
  /** Exact source instance subjects are allowed when no canonical HA concept exists. */
  sourceSubjectKeys?: string[];
  /** Explicit bridge to a learner-card action. Never inferred from a label. */
  learnerActionKey?: string;
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
  representationType: "rigged_mesh" | "illustrative_path" | "bone_motion_with_illustrative_path" | "source_bound_surface";
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
  /** Exact current-scene source instance bindings for derived surface motion. */
  sourceBinding?: SourceMotionBinding | null;
  /** Technical validation only. It is not human review or educational release. */
  technicalStatus: "candidate" | "binding_verified";
  poseControl?: { label: string; startDegrees: number; endDegrees: number; combination: "single_dof_only" };
}

export interface SourceMotionBindingMember {
  sourceKey: string;
  nodeId: string;
  sourceNamespace: string;
  role: "deforming_muscle_surface" | "deforming_passive_surface" | "moving_structure" | "co_moving_context" | "fixed_structure" | "passive_context";
  side: Laterality;
  resourceKey: string;
  lod: "overview" | "detail";
  sourceChunkSha256: string;
  geometrySha256: string;
  instanceMatrix: number[];
}

export interface SourceMotionBinding {
  contractVersion: "t59-source-motion-binding-v1" | "t66-typed-source-motion-v2";
  subjectKind?: "muscle" | "bone";
  datasetNamespace: string;
  datasetRevision: string;
  integrationRevision: string;
  sourceOverlaySha256: string;
  subjectSourceKey: string;
  frameId: string;
  units: "m";
  referencePoseId: string;
  deformation: "morph_targets" | "skinning" | "morph_and_skinning";
  members: SourceMotionBindingMember[];
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
    : asset.representationType === "bone_motion_with_illustrative_path" || asset.representationType === "source_bound_surface"
      ? asset.rig?.nodeBindings.map((row) => row.structureId).sort() ?? []
      : asset.illustration?.trajectoryBindings.map((row) => row.structureId).sort() ?? [];
  const pathSubjects = asset.illustration?.trajectoryBindings.map((row) => row.structureId).sort() ?? [];
  const expectedPathSubjects = [...action.subjectIds].sort();
  const sourceBinding = asset.sourceBinding;
  const sourceBindingCompatible = asset.representationType !== "source_bound_surface" || Boolean(sourceBinding
    && ["t59-source-motion-binding-v1", "t66-typed-source-motion-v2"].includes(sourceBinding.contractVersion)
    && sourceBinding.frameId === binding.frameId && sourceBinding.units === binding.units
    && sourceBinding.referencePoseId === binding.referencePoseId
    && sourceBinding.subjectSourceKey === definition.instanceId
    && action.sourceSubjectKeys?.includes(definition.instanceId)
    && (sourceBinding.subjectKind ?? "muscle") === (action.subjectKind ?? "muscle")
    && sourceBinding.members.some((member) => member.sourceKey === definition.instanceId
      && member.role === (sourceBinding.subjectKind === "bone" ? "moving_structure" : "deforming_muscle_surface") && member.side === definition.side)
    && new Set(sourceBinding.members.map((member) => member.sourceKey)).size === sourceBinding.members.length
    && new Set(sourceBinding.members.map((member) => member.nodeId)).size === sourceBinding.members.length);
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
    && sourceBindingCompatible
    && definition.startPoseId === ref.poseId
    && asset.clip.startPoseId === definition.startPoseId
    && asset.clip.endPoseId === definition.endPoseId
    && JSON.stringify(expectedMoving) === JSON.stringify(actualMoving);
  return { hasActionText, hasTechnicallyCompatibleClip: compatible };
}

export interface LearnerMotionActionOption {
  /** Internal key for in-memory selection; do not project it into learner-facing text. */
  id: string;
  label: string;
  text: LearnerActionText;
  subjectIds: string[];
  /** Text applicability follows the authored action scope, independently of clip readiness. */
  sideApplicability: Laterality | null;
  candidate: { definition: MotionDefinition; asset: MotionAsset } | null;
}

export interface LearnerMotionCandidateRelation {
  learnerActionKey: string | null;
  sideApplicability: Laterality;
  candidate: LearnerMotionActionOption["candidate"];
}

/** A card receives a motion candidate only through an explicit action key, never label similarity. */
export function resolveLearnerMotionCandidate(
  learnerActionKey: string,
  selectedSide: string | null | undefined,
  projected: readonly LearnerMotionCandidateRelation[],
): LearnerMotionActionOption["candidate"] {
  const matches = projected.filter((row) => row.learnerActionKey === learnerActionKey
    && (row.sideApplicability === "bilateral" || row.sideApplicability === "midline"
      || row.sideApplicability === "not_applicable" || row.sideApplicability === selectedSide));
  return matches.length === 1 ? matches[0].candidate : null;
}

/** Project only authored actions and exactly compatible, technically bound clips. */
export function projectLearnerMotionActionOptions(
  conceptId: string,
  bundle: MotionLearningBundle,
  fields: readonly ActionCitationEvidenceField[],
  selectedSide?: Laterality | null,
): LearnerMotionActionOption[] {
  return bundle.muscleActions.flatMap((action) => {
    if (!action.subjectIds.includes(conceptId) && !action.sourceSubjectKeys?.includes(conceptId)) return [];
    if ((selectedSide === "left" || selectedSide === "right")
      && (action.sideApplicability === "left" || action.sideApplicability === "right")
      && action.sideApplicability !== selectedSide) return [];
    const text = projectLearnerActionCard(action, fields);
    if (!text) return [];
    const compatible = bundle.motionDefinitions.flatMap((definition) => {
      if (definition.actionId !== action.id) return [];
      return bundle.motionAssets.flatMap((asset) => asset.motionDefinitionId === definition.id &&
        asset.representationType === "source_bound_surface" && asset.sourceBinding != null &&
        assessMotionCapability(action, definition, asset).hasTechnicallyCompatibleClip
        ? [{ definition, asset }]
        : []);
    });
    return [{
      id: action.learnerActionKey ?? action.id,
      label: text.label,
      text,
      subjectIds: action.subjectIds.length ? [...action.subjectIds] : [...(action.sourceSubjectKeys ?? [])],
      sideApplicability: action.sideApplicability,
      candidate: compatible.length === 1 ? compatible[0] : null,
    }];
  });
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
