import { createHash } from "node:crypto";

export interface LegacyJointAction {
  id: string;
  muscleOrPartIds: string[];
  jointIds: string[];
  action: string;
  postureConditions: string[];
  contractionRole: string;
  taskContext?: string | null;
  roleInTask?: string | null;
  evidenceIds: string[];
  reviewState: string;
}

export interface LegacyJointActionMigrationPreview {
  kind: "legacy_joint_action_preview";
  persistable: false;
  source: {
    id: string;
    snapshotSha256: string;
    originalReviewState: string;
    originalEvidenceIds: string[];
  };
  candidate: {
    previewId: string;
    subjectIds: string[];
    targetJointIds: string[];
    actionLabel: string;
    explanation: string;
    postureConditions: string[];
    contractionRole: string;
    legacyTaskContext: string | null;
    legacyRoleInTask: string | null;
    requiresSourceAndContextReview: true;
  };
}

function stableJson(value: unknown): string {
  if (Array.isArray(value)) return `[${value.map(stableJson).join(",")}]`;
  if (value && typeof value === "object") {
    const record = value as Record<string, unknown>;
    return `{${Object.keys(record).sort().map((key) => `${JSON.stringify(key)}:${stableJson(record[key])}`).join(",")}}`;
  }
  return JSON.stringify(value);
}

/** Preview only: keeps the original review state/hash separate and cannot persist or approve a new action. */
export function previewLegacyJointActionMigration(source: LegacyJointAction): LegacyJointActionMigrationPreview {
  const snapshotSha256 = createHash("sha256").update(stableJson(source), "utf8").digest("hex");
  return {
    kind: "legacy_joint_action_preview",
    persistable: false,
    source: {
      id: source.id,
      snapshotSha256,
      originalReviewState: source.reviewState,
      originalEvidenceIds: [...source.evidenceIds],
    },
    candidate: {
      previewId: `MIGRATION-PREVIEW:${source.id}`,
      subjectIds: [...source.muscleOrPartIds],
      targetJointIds: [...source.jointIds],
      actionLabel: source.action,
      explanation: source.action,
      postureConditions: [...source.postureConditions],
      contractionRole: source.contractionRole,
      legacyTaskContext: source.taskContext ?? null,
      legacyRoleInTask: source.roleInTask ?? null,
      requiresSourceAndContextReview: true,
    },
  };
}
