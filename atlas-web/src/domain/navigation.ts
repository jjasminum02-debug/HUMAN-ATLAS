export type Laterality = "left" | "right" | "midline" | "unpaired";
export type SelectionKind = "muscle" | "bone" | "landmark";

export interface NavigationCategory {
  id: string;
  order: number;
  labelKo: string;
  labelEn: string;
}

export interface RegionMembership {
  id: string;
  categoryId: string;
  entityKind: "muscle" | "bone";
  entityId: string;
  reason: string;
  productDecisionRef: string;
  status: "decision_only" | "held";
}

export interface SelectionBase {
  kind: SelectionKind;
  conceptId: string;
  instanceId?: string;
  meshId?: string;
}

export interface MuscleSelection extends SelectionBase {
  kind: "muscle";
  partId?: string;
}

export interface BoneSelection extends SelectionBase {
  kind: "bone";
}

export interface LandmarkSelection extends SelectionBase {
  kind: "landmark";
}

export type Selection = MuscleSelection | BoneSelection | LandmarkSelection;

export interface SceneSelectableBinding {
  meshAssetId: string;
  sourceMappingId: string;
  reviewState: "needs_review" | "held" | "reviewed" | "stale";
  selection: Selection;
  stateDimensions: SceneStateDimensions;
}

export interface SceneContextBinding {
  meshAssetId: string;
  modelId: string;
  selection: null;
  reasonCode: string;
  stateDimensions: SceneStateDimensions;
}

export interface SceneStateDimensions {
  sourceRelation: string;
  humanAnatomyReview: "not_reviewed" | "pending" | "reviewed";
  staticGeometry: string;
  attachmentLocation: "none" | "text_only" | "candidate" | "reviewed_surface";
  motion: "absent" | "text_ready" | "clip_draft" | "educational_ready";
}

export interface SceneManifest {
  id: string;
  categoryId: string;
  modelId: string;
  availability: "available" | "partial" | "unavailable";
  assetRefs: Array<{ modelId: string; uri: string; sha256: string; meshAssetIds: string[] }>;
  selectableBindings: SceneSelectableBinding[];
  contextBindings: SceneContextBinding[];
  defaultView: { side: Laterality; selection: Selection | null };
  frameId: string;
  units: "m" | "mm" | "cm";
  poseId: string;
  stateDimensions: SceneStateDimensions;
}

export interface NavigationContract {
  schemaVersion: "T15b-navigation-v1";
  status: "partial_pilot_contract" | "contract_only";
  categories: NavigationCategory[];
  memberships: RegionMembership[];
  structureInstances: Array<{ id: string; structureId: string; side: Laterality; variantId: string | null }>;
  structureMeshMappings: Array<{ id: string; structureInstanceId: string; meshIds: string[]; reviewState: string }>;
  sceneManifests: SceneManifest[];
}

export interface SelectionReferences {
  muscles: ReadonlyMap<string, { entityType: string }>;
  muscleInstances: ReadonlyMap<string, { conceptId: string; side: Laterality }>;
  muscleParts: ReadonlyMap<string, { parentId: string }>;
  structures: ReadonlyMap<string, { kind: string; parentId?: string }>;
  structureInstances: ReadonlyMap<string, { structureId: string; side: Laterality }>;
  meshAssets: ReadonlyMap<string, { laterality?: string }>;
  muscleMeshMappings: ReadonlyMap<string, { instanceIds: string[]; partIds: string[]; meshIds: string[] }>;
  structureMeshMappings: ReadonlyMap<string, { structureInstanceId: string; meshIds: string[] }>;
}

export type ScenePickResult =
  | { status: "selection"; selection: Selection }
  | { status: "context"; reasonCode: string }
  | { status: "unbound" };

const CATEGORY_IDS = [
  "head", "neck", "back", "shoulder-scapular", "thorax", "abdomen-lumbar",
  "pelvis-perineum", "gluteal-hip", "thigh", "leg", "foot", "upper-limb",
] as const;
const ID_PATTERN = /^[A-Za-z0-9][A-Za-z0-9._:/-]*$/;

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function allowedKeys(value: Record<string, unknown>, allowed: readonly string[]): boolean {
  return Object.keys(value).every((key) => allowed.includes(key));
}

function sideMatches(asset: { laterality?: string } | undefined, side: Laterality): boolean {
  return !asset?.laterality || asset.laterality === "unknown" || asset.laterality === side;
}

export function validateSelection(value: unknown, refs: SelectionReferences): Selection | null {
  if (!isRecord(value) || typeof value.kind !== "string" || typeof value.conceptId !== "string" || !ID_PATTERN.test(value.conceptId)) return null;
  const commonKeys = ["kind", "conceptId", "instanceId", "meshId"] as const;
  const optionalIdFields = ["instanceId", "meshId"] as const;
  if (optionalIdFields.some((key) => value[key] !== undefined && (typeof value[key] !== "string" || !ID_PATTERN.test(value[key] as string)))) return null;

  if (value.kind === "muscle") {
    if (!allowedKeys(value, [...commonKeys, "partId"]) || (value.partId !== undefined && (typeof value.partId !== "string" || !ID_PATTERN.test(value.partId)))) return null;
    const concept = refs.muscles.get(value.conceptId);
    if (!concept || !["individual_muscle", "muscle_group"].includes(concept.entityType)) return null;
    const instanceId = value.instanceId as string | undefined;
    const meshId = value.meshId as string | undefined;
    const partId = value.partId as string | undefined;
    if (meshId && !refs.meshAssets.has(meshId)) return null;
    if (instanceId) {
      const instance = refs.muscleInstances.get(instanceId);
      if (!instance || instance.conceptId !== value.conceptId) return null;
      if (meshId && !sideMatches(refs.meshAssets.get(meshId), instance.side)) return null;
    }
    if (partId) {
      const part = refs.muscleParts.get(partId);
      if (!part || part.parentId !== value.conceptId) return null;
    }
    return {
      kind: "muscle", conceptId: value.conceptId,
      ...(instanceId ? { instanceId } : {}), ...(partId ? { partId } : {}), ...(meshId ? { meshId } : {}),
    };
  }

  if (value.kind === "bone") {
    if (!allowedKeys(value, commonKeys)) return null;
    const structure = refs.structures.get(value.conceptId);
    if (!structure || structure.kind !== "bone") return null;
    const instanceId = value.instanceId as string | undefined;
    const meshId = value.meshId as string | undefined;
    if (meshId && !refs.meshAssets.has(meshId)) return null;
    if (instanceId) {
      const instance = refs.structureInstances.get(instanceId);
      if (!instance || instance.structureId !== value.conceptId) return null;
      if (meshId && !sideMatches(refs.meshAssets.get(meshId), instance.side)) return null;
    }
    return { kind: "bone", conceptId: value.conceptId, ...(instanceId ? { instanceId } : {}), ...(meshId ? { meshId } : {}) };
  }

  if (value.kind === "landmark") {
    if (!allowedKeys(value, commonKeys)) return null;
    const structure = refs.structures.get(value.conceptId);
    if (!structure || structure.kind !== "landmark") return null;
    const instanceId = value.instanceId as string | undefined;
    const meshId = value.meshId as string | undefined;
    if (meshId && !refs.meshAssets.has(meshId)) return null;
    if (instanceId) {
      const instance = refs.structureInstances.get(instanceId);
      if (!instance || instance.structureId !== structure.parentId) return null;
      if (meshId && !sideMatches(refs.meshAssets.get(meshId), instance.side)) return null;
    }
    return { kind: "landmark", conceptId: value.conceptId, ...(instanceId ? { instanceId } : {}), ...(meshId ? { meshId } : {}) };
  }
  return null;
}

export function validateNavigationContract(value: unknown, refs: SelectionReferences): string[] {
  if (!isRecord(value) || !Array.isArray(value.categories) || !Array.isArray(value.memberships) || !Array.isArray(value.structureInstances) || !Array.isArray(value.structureMeshMappings) || !Array.isArray(value.sceneManifests)) return ["navigation_document_shape"];
  const issues: string[] = [];
  const categories = value.categories as NavigationCategory[];
  if (categories.length !== CATEGORY_IDS.length || categories.some((category, i) => category.id !== CATEGORY_IDS[i] || category.order !== i + 1)) issues.push("category_order_or_count");
  const categorySet = new Set(categories.map((category) => category.id));
  const memberships = value.memberships as RegionMembership[];
  const relationKeys = memberships.map((row) => `${row.categoryId}\u0000${row.entityKind}\u0000${row.entityId}`);
  if (new Set(relationKeys).size !== relationKeys.length) issues.push("duplicate_membership");
  for (const row of memberships) {
    if (!categorySet.has(row.categoryId)) issues.push(`membership_category:${row.id}`);
    if (row.entityKind === "muscle") {
      const concept = refs.muscles.get(row.entityId);
      if (!concept || !["individual_muscle", "muscle_group"].includes(concept.entityType)) issues.push(`membership_muscle:${row.id}`);
    } else if (row.entityKind === "bone") {
      if (refs.structures.get(row.entityId)?.kind !== "bone") issues.push(`membership_bone:${row.id}`);
    } else {
      issues.push(`membership_kind:${row.id}`);
    }
    if (row.status === "decision_only" && !row.productDecisionRef) issues.push(`membership_provenance:${row.id}`);
  }

  const structureInstances = value.structureInstances as NavigationContract["structureInstances"];
  const structureInstanceMap = new Map(structureInstances.map((instance) => [instance.id, instance]));
  for (const instance of structureInstances) {
    if (refs.structures.get(instance.structureId)?.kind !== "bone") issues.push(`structure_instance_kind:${instance.id}`);
    const expectedPrefix = instance.side === "right" ? "R" : instance.side === "left" ? "L" : instance.side === "midline" ? "M" : "U";
    if (instance.id !== `HA-SI-${expectedPrefix}-${instance.structureId}`) issues.push(`structure_instance_id:${instance.id}`);
  }

  const structureMappings = value.structureMeshMappings as NavigationContract["structureMeshMappings"];
  const structureMappingMap = new Map(structureMappings.map((mapping) => [mapping.id, mapping]));
  for (const mapping of structureMappings) {
    if (!structureInstanceMap.has(mapping.structureInstanceId)) issues.push(`mapping_instance:${mapping.id}`);
    if (mapping.reviewState === "reviewed") issues.push(`mapping_review_promotion:${mapping.id}`);
  }

  const scenes = value.sceneManifests as SceneManifest[];
  for (const scene of scenes) {
    if (!categorySet.has(scene.categoryId)) issues.push(`scene_category:${scene.id}`);
    if (scene.assetRefs.some((asset) => asset.modelId !== scene.modelId)) issues.push(`scene_model_mix:${scene.id}`);
    const meshIds = new Set(scene.assetRefs.flatMap((asset) => asset.meshAssetIds));
    const bound = new Set<string>();
    for (const binding of scene.selectableBindings) {
      if (!meshIds.has(binding.meshAssetId) || bound.has(binding.meshAssetId)) issues.push(`scene_mesh_binding:${scene.id}:${binding.meshAssetId}`);
      bound.add(binding.meshAssetId);
      const selection = validateSelection(binding.selection, refs);
      if (!selection) {
        issues.push(`selection_type_or_reference:${scene.id}:${binding.meshAssetId}`);
        continue;
      }
      if (selection.meshId && selection.meshId !== binding.meshAssetId) issues.push(`selection_mesh:${scene.id}:${binding.meshAssetId}`);
      if (selection.kind === "muscle") {
        const source = refs.muscleMeshMappings.get(binding.sourceMappingId);
        if (!source || !source.meshIds.includes(binding.meshAssetId) || !source.instanceIds.includes(selection.instanceId ?? "")) issues.push(`muscle_mapping:${scene.id}:${binding.meshAssetId}`);
        if (selection.partId && !source?.partIds.includes(selection.partId)) issues.push(`muscle_part_mapping:${scene.id}:${binding.meshAssetId}`);
      } else if (selection.kind === "bone") {
        const source = structureMappingMap.get(binding.sourceMappingId);
        if (!source || source.structureInstanceId !== selection.instanceId || !source.meshIds.includes(binding.meshAssetId)) issues.push(`bone_mapping:${scene.id}:${binding.meshAssetId}`);
      }
      if (binding.stateDimensions?.humanAnatomyReview === "reviewed" || binding.stateDimensions?.motion !== "absent" || binding.stateDimensions?.attachmentLocation === "reviewed_surface") issues.push(`promoted_or_motion_state:${scene.id}:${binding.meshAssetId}`);
    }
    for (const binding of scene.contextBindings) {
      if (!meshIds.has(binding.meshAssetId) || bound.has(binding.meshAssetId) || binding.selection !== null) issues.push(`context_binding:${scene.id}:${binding.meshAssetId}`);
      bound.add(binding.meshAssetId);
    }
    if (bound.size !== meshIds.size) issues.push(`unbound_scene_mesh:${scene.id}`);
  }
  return issues;
}

export interface AtlasRouteState {
  regionId: string | null;
  side: Laterality | null;
  selection: Selection | null;
  legacyRoute: boolean;
}

export function parseAtlasRoute(search: string, validCategoryIds: ReadonlySet<string>, refs: SelectionReferences): AtlasRouteState | null {
  const params = new URLSearchParams(search);
  const regionValue = params.get("region");
  const regionId = regionValue === null ? null : validCategoryIds.has(regionValue) ? regionValue : undefined;
  if (regionId === undefined) return null;
  const sideValue = params.get("side");
  const side = sideValue === null ? null : (["left", "right", "midline", "unpaired"].includes(sideValue) ? sideValue as Laterality : undefined);
  if (side === undefined) return null;
  const kind = params.get("kind");
  const id = params.get("id");
  const partId = params.get("part");
  const legacyMuscle = params.get("muscle");
  if (legacyMuscle && (kind || id || partId)) return null;
  if (legacyMuscle) {
    const selection = validateSelection({ kind: "muscle", conceptId: legacyMuscle }, refs);
    return selection ? { regionId, side, selection, legacyRoute: true } : null;
  }
  if (kind === null && id === null && partId === null) return { regionId, side, selection: null, legacyRoute: false };
  if (kind === null || id === null || (partId !== null && kind !== "muscle")) return null;
  const selection = validateSelection({ kind, conceptId: id, ...(partId ? { partId } : {}) }, refs);
  if (!selection) return null;
  if (side && selection.instanceId) {
    const instanceSide = selection.kind === "muscle"
      ? refs.muscleInstances.get(selection.instanceId)?.side
      : refs.structureInstances.get(selection.instanceId)?.side;
    if (instanceSide !== side) return null;
  }
  return { regionId, side, selection, legacyRoute: false };
}

export function serializeAtlasRoute(search: string, state: AtlasRouteState): string {
  const params = new URLSearchParams(search);
  params.delete("muscle");
  if (state.regionId) params.set("region", state.regionId); else params.delete("region");
  if (state.selection) {
    params.set("kind", state.selection.kind);
    params.set("id", state.selection.conceptId);
    if (state.selection.kind === "muscle" && state.selection.partId) params.set("part", state.selection.partId);
    else params.delete("part");
  } else {
    params.delete("kind");
    params.delete("id");
    params.delete("part");
  }
  if (state.side) params.set("side", state.side); else params.delete("side");
  return params.toString();
}

export function resolveSceneMeshPick(scene: SceneManifest, meshAssetId: string, refs: SelectionReferences): ScenePickResult {
  const selectable = scene.selectableBindings.filter((binding) => binding.meshAssetId === meshAssetId);
  const context = scene.contextBindings.filter((binding) => binding.meshAssetId === meshAssetId);
  if (selectable.length > 1 || context.length > 1 || (selectable.length > 0 && context.length > 0)) throw new Error(`Ambiguous scene binding for ${meshAssetId}`);
  if (context[0]) return { status: "context", reasonCode: context[0].reasonCode };
  if (!selectable[0]) return { status: "unbound" };
  const selection = validateSelection(selectable[0].selection, refs);
  if (!selection) throw new Error(`Invalid typed selection for ${meshAssetId}`);
  return { status: "selection", selection };
}
