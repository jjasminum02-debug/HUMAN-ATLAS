import {
  parseAtlasRoute,
  type AtlasRouteState,
  type NavigationContract,
  type Selection,
  type SelectionReferences,
} from "./navigation.ts";

export type LearnerNavigationData = Pick<NavigationContract, "categories" | "memberships" | "sceneManifests">;

export interface ResolvedLearnerRoute {
  route: AtlasRouteState;
  notice: string | null;
  canonicalize: boolean;
}

const muscleSelection = (conceptId: string, partId?: string): Selection => ({
  kind: "muscle",
  conceptId,
  ...(partId ? { partId } : {}),
});

export function categoryMemberships(navigation: LearnerNavigationData, categoryId: string) {
  return navigation.memberships.filter((row) =>
    row.categoryId === categoryId && row.entityKind === "muscle" && row.status === "decision_only",
  );
}

export function categoriesForMuscleConcept(navigation: LearnerNavigationData, conceptId: string): string[] {
  return navigation.memberships
    .filter((row) => row.entityKind === "muscle" && row.status === "decision_only" && row.entityId === conceptId)
    .map((row) => row.categoryId);
}

function defaultSide(navigation: LearnerNavigationData, categoryId: string | null): AtlasRouteState["side"] {
  if (!categoryId) return null;
  return navigation.sceneManifests.find((scene) => scene.categoryId === categoryId)?.defaultView.side ?? null;
}

export function defaultLearnerRoute(navigation: LearnerNavigationData): AtlasRouteState {
  const scene = navigation.sceneManifests.find((candidate) => candidate.availability !== "unavailable" && categoryMemberships(navigation, candidate.categoryId).length > 0);
  const categoryId = scene?.categoryId ?? navigation.categories[0]?.id ?? null;
  const first = categoryId ? categoryMemberships(navigation, categoryId)[0] : undefined;
  return {
    regionId: categoryId,
    side: defaultSide(navigation, categoryId),
    selection: first ? muscleSelection(first.entityId) : null,
    legacyRoute: false,
  };
}

export function routeForCategory(
  navigation: LearnerNavigationData,
  categoryId: string,
  currentSelection: Selection | null,
): AtlasRouteState {
  if (!navigation.categories.some((row) => row.id === categoryId)) return defaultLearnerRoute(navigation);
  const memberships = categoryMemberships(navigation, categoryId);
  const currentId = currentSelection?.kind === "muscle" ? currentSelection.conceptId : null;
  const retained = currentId && memberships.some((row) => row.entityId === currentId) ? currentSelection : null;
  const selected = retained ?? (memberships[0] ? muscleSelection(memberships[0].entityId) : null);
  return { regionId: categoryId, side: selected ? defaultSide(navigation, categoryId) : null, selection: selected, legacyRoute: false };
}

export function routeForMuscleSelection(
  navigation: LearnerNavigationData,
  conceptId: string,
  partId: string | undefined,
  currentRegionId: string | null,
): AtlasRouteState {
  const categoryIds = categoriesForMuscleConcept(navigation, conceptId);
  const categoryId = currentRegionId && categoryIds.includes(currentRegionId)
    ? currentRegionId
    : categoryIds.length === 1 ? categoryIds[0] : null;
  return {
    regionId: categoryId,
    side: defaultSide(navigation, categoryId),
    selection: muscleSelection(conceptId, partId),
    legacyRoute: false,
  };
}

export function resolveLearnerRoute(
  search: string,
  navigation: LearnerNavigationData,
  refs: SelectionReferences,
): ResolvedLearnerRoute {
  const params = new URLSearchParams(search);
  const hasAtlasState = ["region", "kind", "id", "part", "muscle", "side"].some((key) => params.has(key));
  if (!hasAtlasState) return { route: defaultLearnerRoute(navigation), notice: null, canonicalize: true };

  const parsed = parseAtlasRoute(search, new Set(navigation.categories.map((row) => row.id)), refs);
  if (!parsed) {
    return {
      route: { regionId: null, side: null, selection: null, legacyRoute: false },
      notice: "이 주소의 부위 또는 구조를 확인할 수 없습니다. 목록에서 다시 선택해 주세요.",
      canonicalize: false,
    };
  }

  let route = parsed;
  let notice: string | null = null;
  let canonicalize = parsed.legacyRoute;
  let selectionMismatch = false;
  const selection = parsed.selection;

  if (selection?.kind === "muscle") {
    const categoryIds = categoriesForMuscleConcept(navigation, selection.conceptId);
    if (route.regionId && !categoryIds.includes(route.regionId)) {
      route = { ...route, side: null, selection: null, legacyRoute: false };
      notice = "이 근육은 선택한 부위의 구조 목록에 연결되어 있지 않습니다.";
      canonicalize = true;
      selectionMismatch = true;
    } else if (!route.regionId && categoryIds.length === 1) {
      route = { ...route, regionId: categoryIds[0], side: defaultSide(navigation, categoryIds[0]), legacyRoute: false };
      canonicalize = true;
    }
  }

  if (!selectionMismatch && route.regionId && !route.selection && categoryMemberships(navigation, route.regionId).length > 0) {
    route = routeForCategory(navigation, route.regionId, null);
    canonicalize = true;
  }

  return { route, notice, canonicalize };
}
