/** Remove the source-scope editorial sentence from learner action copy while preserving the claim text. */
export function learnerActionExplanation(text: string): string {
  return text
    .replace("이 요약은 해당 작용을 다룬 출처에 한정되며, ", "")
    .replace("이 시범은 발과 발목의 작용 방향을 보여 주며, ", "")
    .trim();
}

/** Keep authored text applicability separate from whether a clip can play. */
export function learnerActionAppliesToSide(applicableSide: string | null, selectedSide?: string | null): boolean {
  return applicableSide === null || applicableSide === selectedSide;
}

export function learnerFunctionUnavailableText(): string {
  return "현재 확인 가능한 기능 설명이 없습니다.";
}
