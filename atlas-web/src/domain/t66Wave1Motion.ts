import {
  projectLearnerMotionActionOptions,
  type LearnerMotionActionOption,
  type Laterality,
  type MotionLearningBundle,
} from "./motionLearning.ts";

export interface T66Wave1Selector {
  actionId: string;
  definitionId: string;
  packageId: string;
  subjectKind: "muscle" | "bone";
  sourceSubjectKey: string;
  side: Laterality;
  learnerActionKey: string;
  label: string;
  explanation: string;
  evidenceRefs?: string[];
}

export interface T66Wave1Package {
  id: string;
  familyId: string;
  uri: string;
  revision: string;
  sha256: string;
  sourceId: string;
  licenseId: string;
  representationType: "source_bound_surface";
  technicalStatus: "binding_verified";
  staticBinding: MotionLearningBundle["motionAssets"][number]["staticBinding"];
  rig: NonNullable<MotionLearningBundle["motionAssets"][number]["rig"]>;
  illustration: null;
  clip: MotionLearningBundle["motionAssets"][number]["clip"];
  poseControl?: MotionLearningBundle["motionAssets"][number]["poseControl"] | null;
  sourceBindingTemplate: Omit<NonNullable<MotionLearningBundle["motionAssets"][number]["sourceBinding"]>, "subjectKind" | "subjectSourceKey">;
  definitionTemplate: Omit<MotionLearningBundle["motionDefinitions"][number], "id" | "actionId" | "instanceId" | "side">;
}

export interface T66Wave1Registration {
  schemaVersion: "t66-wave1-source-motion-registration-v2";
  revision: string;
  authority: {
    sourceOnly: true;
    publicRedistribution: "held";
    humanReview: "not_performed";
    canonicalTargetMembershipApproved: false;
  };
  packages: T66Wave1Package[];
  selectors: T66Wave1Selector[];
}

/** Expand only the selected exact source key through the shared motion projection path. */
export function projectT66Wave1MotionOptions(
  registration: T66Wave1Registration,
  sourceKey: string,
  selectedSide?: string | null,
  intentByAction: Readonly<Record<string, LearnerMotionActionOption["learningIntent"]>> = {},
): LearnerMotionActionOption[] {
  if (registration.schemaVersion !== "t66-wave1-source-motion-registration-v2"
    || registration.authority.sourceOnly !== true
    || registration.authority.publicRedistribution !== "held"
    || registration.authority.humanReview !== "not_performed"
    || registration.authority.canonicalTargetMembershipApproved !== false) return [];

  const packageById = new Map(registration.packages.map((row) => [row.id, row]));
  const selectors = registration.selectors.filter((row) => row.sourceSubjectKey === sourceKey
    && (!selectedSide || row.side === "bilateral" || row.side === "midline" || row.side === selectedSide));
  const muscleActions: MotionLearningBundle["muscleActions"] = [];
  const motionDefinitions: MotionLearningBundle["motionDefinitions"] = [];
  const motionAssets: MotionLearningBundle["motionAssets"] = [];

  for (const selector of selectors) {
    const template = packageById.get(selector.packageId);
    if (!template) continue;
    const definition = {
      ...template.definitionTemplate,
      id: selector.definitionId,
      actionId: selector.actionId,
      instanceId: selector.sourceSubjectKey,
      side: selector.side,
    };
    const action: MotionLearningBundle["muscleActions"][number] = {
      subjectKind: selector.subjectKind,
      id: selector.actionId,
      subjectIds: [],
      sourceSubjectKeys: [selector.sourceSubjectKey],
      learnerActionKey: selector.learnerActionKey,
      sideApplicability: selector.side,
      jointBindingState: "source_family_bound",
      sourceFamilyId: template.familyId,
      jointBindingNote: null,
      targetJointIds: [],
      actionLabel: selector.label,
      explanation: selector.explanation,
      postureConditions: [],
      stabilizationConditions: [],
      stabilizationNote: null,
      contextRoles: [],
      sourceRefs: [],
    };
    const asset: MotionLearningBundle["motionAssets"][number] = {
      id: `${template.id}:${selector.actionId}`,
      motionDefinitionId: selector.definitionId,
      uri: template.uri,
      revision: template.revision,
      sha256: template.sha256,
      sourceId: template.sourceId,
      licenseId: template.licenseId,
      representationType: template.representationType,
      staticBinding: template.staticBinding,
      rig: template.rig,
      illustration: template.illustration,
      clip: template.clip,
      sourceBinding: {
        ...template.sourceBindingTemplate,
        subjectKind: selector.subjectKind,
        subjectSourceKey: selector.sourceSubjectKey,
      },
      technicalStatus: template.technicalStatus,
      ...(template.poseControl ? { poseControl: template.poseControl } : {}),
    };
    muscleActions.push(action);
    motionDefinitions.push(definition);
    motionAssets.push(asset);
  }
  const bundle: MotionLearningBundle = { schemaVersion: "1.0.0", revision: registration.revision, muscleActions, motionDefinitions, motionAssets };
  return projectLearnerMotionActionOptions(sourceKey, bundle, [], (selectedSide as Laterality | null | undefined) ?? null).map<LearnerMotionActionOption>(option => {
    const selector = selectors.find(row => row.learnerActionKey === option.id);
    const member = option.candidate?.asset.sourceBinding?.members.find(row => row.sourceKey === sourceKey);
    // Geometry and citation presence alone never establish action intent.
    // Only the writer-reviewed exact selector can teach a muscle action.
    return { ...option, learningIntent: selector?.subjectKind === "bone" ? "bone_motion"
      : member?.role === "deforming_muscle_surface" && selector && intentByAction[selector.actionId] === "muscle_action"
        ? "muscle_action" : "posture_observation" };
  });
}
