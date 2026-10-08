export type NerveConceptNameRow = {
  key: string;
  names: { en: string };
  sourceNativeEnglishName: string | null;
};

export type MotorRelationRow = {
  nerveKey: string;
  targetSourceKeys: string[];
  targetSide: "left" | "right" | null;
  scope: string;
};

export const GENERIC_UNLINKED_NERVE_FUNCTION_CONTEXT =
  "확인된 신경 지배 관계가 있는 경우 아래 운동 연결에서 살펴볼 수 있습니다.";

/** Hide only the repeated generic status sentence; keep every specific explanation visible. */
export function shouldDisplayNerveFunctionContext(
  context: string | null | undefined,
  evidenceClass: string | null | undefined,
): boolean {
  if (!context) return false;
  return !(evidenceClass === "relationship_not_linked"
    && context === GENERIC_UNLINKED_NERVE_FUNCTION_CONTEXT);
}

export function nerveActionRouteLabel(hasPlayableCandidate: boolean): string {
  return hasPlayableCandidate ? '이 근육의 움직임 보기' : '이 근육의 작용 설명 보기';
}

/** Resolve only a unique exact native label, with a unique exact display-name fallback. */
export function conceptForExactNerveName<T extends NerveConceptNameRow>(concepts: readonly T[], englishName: string): T | null {
  const sourceMatches = concepts.filter(row => row.sourceNativeEnglishName === englishName);
  if (sourceMatches.length === 1) return sourceMatches[0];
  if (sourceMatches.length > 1) return null;
  const displayMatches = concepts.filter(row => row.names.en === englishName);
  return displayMatches.length === 1 ? displayMatches[0] : null;
}

/** Exact geometry relations follow the selected side; literature concept relations remain unsided. */
export function relationsForNerve<T extends MotorRelationRow>(relations: readonly T[], nerveKey: string, selectedSide?: string | null): T[] {
  return relations.filter(row => row.nerveKey === nerveKey
    && (row.scope !== "exact_side_matched_source_instance" || !selectedSide || row.targetSide === selectedSide));
}

/** Only explanatory action text and true muscle-action bindings belong beside a nerve relation. */
export function isNerveRelatedActionTextIntent(intent: string | undefined): boolean {
  return intent === "muscle_action" || intent === "text_only";
}

export type NerveTargetAction = { id: string; learningIntent?: string; candidate?: unknown; text: { explanation: string } };
/** Preserve verified relations, deduplicate surfaces, put usable learning content first. */
export function nerveLearningTargets<R extends {sourceKey:string;kind:string;side:string|null;localDisplayEligible:boolean;inspectionEligible:boolean}, A extends NerveTargetAction>(
  relations: readonly MotorRelationRow[], rowFor: (key:string)=>R|undefined,
  actionsFor: (row:R)=>readonly A[], side?:string|null,
): Array<{row:R;actions:A[]}> {
  const targets=new Map<string,{row:R;actions:A[]}>();
  for(const relation of relations) for(const key of relation.targetSourceKeys){
    const row=rowFor(key);
    if(!row||row.kind!=='muscle'||!row.localDisplayEligible||!row.inspectionEligible||(side&&row.side!==side)||targets.has(key))continue;
    const actions=[...new Map(actionsFor(row).filter(action=>isNerveRelatedActionTextIntent(action.learningIntent)
      && action.text.explanation.trim()).map(action=>[action.id,action])).values()];
    targets.set(key,{row,actions});
  }
  const rank=(item:{actions:A[]})=>item.actions.some(a=>a.candidate&&a.learningIntent==='muscle_action')?2:item.actions.length?1:0;
  return [...targets.values()].sort((a,b)=>rank(b)-rank(a));
}
