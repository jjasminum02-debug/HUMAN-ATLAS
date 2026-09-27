/** Remove the source-scope editorial sentence from learner action copy while preserving the claim text. */
export function learnerActionExplanation(text: string): string {
  return text
    .replace("이 요약은 해당 작용을 다룬 출처에 한정되며, ", "")
    .trim();
}
