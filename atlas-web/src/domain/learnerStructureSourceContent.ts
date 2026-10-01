export type SourceStructureContentRecord = {
  sourceKeys: string[];
  subjectId: string | null;
  fieldDisposition: Record<string, { status: string; evidenceState: string | null }>;
};

/** Project a source-specific view of an existing attachment field without changing canonical binding. */
export function learnerStructureSourceText(
  record: SourceStructureContentRecord | undefined,
  field: "origin" | "insertion",
  projectExistingClaim: (subjectId: string, field: "origin" | "insertion") => string | null,
): string | null {
  if (!record?.subjectId) return null;
  const status = record.fieldDisposition[field]?.status;
  if (status !== "claim_available" && status !== "conflicted_not_asserted") return null;
  return projectExistingClaim(record.subjectId, field);
}

/** Learner copy for a field with no validated source sentence. */
export function learnerStructureUnavailability(field: "origin" | "insertion" | "motorNerve" | "sensoryProprioception") {
  if (field === "origin") return "확인된 기시 설명이 없습니다.";
  if (field === "insertion") return "확인된 정지 설명이 없습니다.";
  if (field === "motorNerve") return "확인된 운동신경 설명이 없습니다.";
  return "별도로 확인된 감각·고유감각 설명이 없습니다.";
}
