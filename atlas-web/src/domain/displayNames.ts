/** Small learner-facing anatomical detail; source identity and part extent remain unchanged. */
export function anatomicalPartSubtitle(english: string): string | null {
  return ({
    'Rotatores': '등과 목의 돌림근군을 함께 표시합니다.',
    'Clavicular part of deltoid muscle': '삼각근 · 쇄골부 (빗장부분)',
    'Acromial part of deltoid muscle': '삼각근 · 견봉부 (봉우리부분)',
    'Scapular spinal part of deltoid muscle': '삼각근 · 견갑극부 (어깨뼈가시부분)',
  } as Record<string, string>)[english] ?? null;
}
