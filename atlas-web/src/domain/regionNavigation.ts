import {
  parseAtlasRoute,
  type AtlasRouteState,
  type BoneSelection,
  type NavigationContract,
  type Selection,
  type SelectionReferences,
} from "./navigation.ts";

export type LearnerNavigationData = Pick<NavigationContract, "categories" | "memberships" | "sceneManifests" | "structureInstances" | "structureMeshMappings">;

export interface ResolvedLearnerRoute {
  route: AtlasRouteState;
  selectedRegionIds: string[];
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
  // The home is a durable empty route, never an implicitly selected pilot muscle.
  void navigation;
  return { regionId: null, side: null, selection: null, legacyRoute: false };
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
  const selected = retained;
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

export function boneSelectionForMesh(navigation: LearnerNavigationData, meshId: string): BoneSelection | null {
  const matches = navigation.structureMeshMappings.filter((mapping) => mapping.meshIds.includes(meshId));
  if (matches.length === 0) return null;
  if (matches.length !== 1) throw new Error(`Bone mesh ${meshId} has ambiguous source mappings.`);
  const mapping = matches[0];
  const instance = navigation.structureInstances.find((row) => row.id === mapping.structureInstanceId);
  if (!instance) return null;
  const sceneSelections = navigation.sceneManifests.flatMap((scene) => scene.selectableBindings)
    .filter((binding) => binding.meshAssetId === meshId && binding.selection.kind === "bone");
  if (sceneSelections.length > 1 || (sceneSelections[0] &&
    (sceneSelections[0].selection.conceptId !== instance.structureId || sceneSelections[0].selection.instanceId !== instance.id))) {
    throw new Error(`Scene and source crosswalk disagree for bone mesh ${meshId}.`);
  }
  return {
    kind: "bone",
    conceptId: instance.structureId,
    instanceId: instance.id,
    meshId,
  };
}

function normalizeBoneRoute(navigation: LearnerNavigationData, selection: BoneSelection): AtlasRouteState | null {
  let instance = selection.instanceId
    ? navigation.structureInstances.find((row) => row.id === selection.instanceId)
    : undefined;
  if (!instance) {
    const eligibleInstances = navigation.structureInstances.filter((row) => row.structureId === selection.conceptId &&
      navigation.structureMeshMappings.some((mapping) => mapping.structureInstanceId === row.id));
    if (eligibleInstances.length !== 1) return null;
    instance = eligibleInstances[0];
  }
  if (instance.structureId !== selection.conceptId) return null;
  const mappings = navigation.structureMeshMappings.filter((mapping) => mapping.structureInstanceId === instance!.id);
  if (mappings.length === 0) return null;
  let meshId = selection.meshId;
  if (meshId && !mappings.some((mapping) => mapping.meshIds.includes(meshId!))) return null;
  if (!meshId) {
    const mappedMeshes = [...new Set(mappings.flatMap((mapping) => mapping.meshIds))];
    if (mappedMeshes.length === 1) meshId = mappedMeshes[0];
  }
  return {
    regionId: "leg",
    side: instance.side,
    selection: { kind: "bone", conceptId: instance.structureId, instanceId: instance.id, ...(meshId ? { meshId } : {}) },
    legacyRoute: false,
  };
}

export function routeForBoneSelection(navigation: LearnerNavigationData, selection: BoneSelection): AtlasRouteState {
  return normalizeBoneRoute(navigation, selection) ?? {
    regionId: "leg", side: null, selection: null, legacyRoute: false,
  };
}

export function resolveLearnerRoute(
  search: string,
  navigation: LearnerNavigationData,
  refs: SelectionReferences,
): ResolvedLearnerRoute {
  const params = new URLSearchParams(search);
  const hasAtlasState = ["region", "kind", "id", "part", "muscle", "side"].some((key) => params.has(key));
  if (!hasAtlasState) return { route: defaultLearnerRoute(navigation), selectedRegionIds: [], notice: null, canonicalize: true };

  const categoryOrder = navigation.categories.map((row) => row.id);
  const requestedRegions = params.getAll("region");
  if (requestedRegions.some((regionId) => !categoryOrder.includes(regionId))) {
    return {
      route: defaultLearnerRoute(navigation), selectedRegionIds: [],
      notice: "이 주소의 부위를 확인할 수 없습니다. 목록에서 다시 선택해 주세요.", canonicalize: false,
    };
  }
  const uniqueRequested = [...new Set(requestedRegions)];
  let selectedRegionIds = categoryOrder.filter((regionId) => uniqueRequested.includes(regionId));
  const normalizedRegionQuery = selectedRegionIds.length === requestedRegions.length
    && selectedRegionIds.every((regionId, index) => regionId === requestedRegions[index]);

  const parsed = parseAtlasRoute(search, new Set(navigation.categories.map((row) => row.id)), refs);
  if (!parsed) {
    return {
      route: defaultLearnerRoute(navigation), selectedRegionIds: [],
      notice: "이 주소의 부위 또는 구조를 확인할 수 없습니다. 목록에서 다시 선택해 주세요.",
      canonicalize: false,
    };
  }

  let route = parsed;
  if (selectedRegionIds.length > 0 && route.regionId !== selectedRegionIds[0]) {
    route = { ...route, regionId: selectedRegionIds[0] };
  }
  let notice: string | null = null;
  let canonicalize = parsed.legacyRoute || !normalizedRegionQuery;
  const selection = parsed.selection;
  const explicitWhole = params.get("view") === "whole";

  if (selection?.kind === "muscle") {
    const categoryIds = categoriesForMuscleConcept(navigation, selection.conceptId);
    if (selectedRegionIds.length > 0 && !selectedRegionIds.some((regionId) => categoryIds.includes(regionId))) {
      route = { ...route, regionId: selectedRegionIds[0] ?? null, side: null, selection: null, legacyRoute: false };
      notice = "이 근육은 선택한 부위의 구조 목록에 연결되어 있지 않습니다.";
      canonicalize = true;
    } else if (selectedRegionIds.length === 0 && !explicitWhole && !route.regionId && categoryIds.length === 1) {
      route = { ...route, regionId: categoryIds[0], side: defaultSide(navigation, categoryIds[0]), legacyRoute: false };
      selectedRegionIds = [categoryIds[0]];
      canonicalize = true;
    }
  }

  if (selection?.kind === "bone") {
    const normalized = normalizeBoneRoute(navigation, selection);
    if (!normalized) {
      route = { regionId: route.regionId, side: null, selection: null, legacyRoute: false };
      notice = "이 뼈의 출처 연결을 확인할 수 없습니다. 확인된 구조만 선택할 수 있습니다.";
      canonicalize = true;
    } else if (selectedRegionIds.length === 0) {
      route = explicitWhole ? { ...normalized, regionId: null } : normalized;
      selectedRegionIds = explicitWhole ? [] : normalized.regionId ? [normalized.regionId] : [];
      canonicalize = canonicalize || !explicitWhole || route.side !== parsed.side ||
        route.selection?.kind !== "bone" || route.selection.instanceId !== parsed.selection?.instanceId ||
        route.selection.meshId !== parsed.selection?.meshId;
    } else if (route.regionId !== selectedRegionIds[0] || route.side !== normalized.side ||
      route.selection?.kind !== "bone" || route.selection.instanceId !== normalized.selection?.instanceId ||
      route.selection.meshId !== normalized.selection?.meshId) {
      route = { ...normalized, regionId: selectedRegionIds[0] ?? null };
      canonicalize = true;
    }
  }

  // An explicit empty selection is a durable URL state (clear/back/forward).

  return { route, selectedRegionIds, notice, canonicalize };
}
