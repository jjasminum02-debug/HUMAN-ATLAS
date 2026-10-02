import type { MotionAsset, SourceMotionBindingMember } from "./motionLearning.ts";

export type MotionSubjectKind = "muscle" | "bone";
export type MotionSubjectRole = SourceMotionBindingMember["role"];

/** Return a learner-safe role only when the exact selected source key and side occur consistently. */
export function selectedMotionSubjectRole(
  asset: MotionAsset | null | undefined,
  sourceContextKey: string | null,
): MotionSubjectRole | null {
  if (!asset?.sourceBinding || !sourceContextKey) return null;
  const rows = asset.sourceBinding.members.filter((row) =>
    row.sourceKey === sourceContextKey && row.side === asset.staticBinding.side,
  );
  if (rows.length === 0) return null;
  const roles = new Set(rows.map((row) => row.role));
  return roles.size === 1 ? rows[0]!.role : null;
}

/** Keep fixed, moving, active-surface, and passive-surface observations distinct in learner copy. */
export function motionSubjectExplanation(kind: MotionSubjectKind, role: MotionSubjectRole | null): string {
  if (kind === "bone" && role === "fixed_structure") {
    return "선택한 뼈는 이 자세에서 고정된 기준 구조입니다. 움직이는 뼈와 주변 표면의 변화를 함께 관찰합니다.";
  }
  if (kind === "bone" && role === "moving_structure") {
    return "선택한 뼈가 이 교육용 관절 자세에서 이동합니다. 정상 운동범위나 개별 관절축을 확정하는 뜻은 아닙니다.";
  }
  if (kind === "muscle" && role === "deforming_passive_surface") {
    return "선택한 근육은 관절 움직임에 따른 주변 표면의 수동 변형으로 표시됩니다. 개별 근육의 활성도나 주작용을 뜻하지 않습니다.";
  }
  if (kind === "muscle" && role === "deforming_muscle_surface") {
    return "선택한 근육 표면의 교육용 변형을 보여 줍니다. 개인의 실제 수축량·활성도·운동 범위를 나타내지 않습니다.";
  }
  return kind === "bone"
    ? "뼈가 관절 동작에 따라 함께 이동하는 교육용 시범입니다. 선택한 뼈에 독립적인 관절이 있다는 뜻은 아닙니다."
    : "교육용 표면 변형은 개인의 실제 수축량이나 운동 범위를 재현하지 않습니다.";
}
