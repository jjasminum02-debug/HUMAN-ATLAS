#!/usr/bin/env node
/**
 * Freeze the current learner-reachable motion inventory for MV1.
 * Read-only against runtime, registration, authoring inputs, and emitted GLBs.
 */
import { createHash } from "node:crypto";
import { readFile, mkdir, writeFile } from "node:fs/promises";
import { dirname, resolve, sep } from "node:path";
import { fileURLToPath } from "node:url";
import runtime from "../../../../atlas-web/src/data/learnerMotionRuntime.generated.ts";
import { motionActionOptionsForLearner } from "../../../../atlas-web/src/data/motionLearningData.ts";
import { searchStructures, validateRuntimeIntegration } from "../../../../atlas-web/src/viewer/datasets/integration.ts";
import { validateDataset } from "../../../../atlas-web/src/viewer/datasets/schema.ts";

const scriptDir = dirname(fileURLToPath(import.meta.url));
const root = resolve(scriptDir, "../../../..");
const runDir = resolve(scriptDir, "../2026-10-11-run-01");
const outPath = resolve(runDir, "inventory.json");
const runtimeBase = process.argv.find((arg) => arg.startsWith("--runtime-base="))?.slice("--runtime-base=".length)
  ?? process.env.MV1_RUNTIME_BASE_URL ?? "http://127.0.0.1:5183";
const sha = (bytes) => createHash("sha256").update(bytes).digest("hex");
const json = async (relative) => JSON.parse(await readFile(resolve(root, relative), "utf8"));
const fileHash = async (relative) => {
  const bytes = await readFile(resolve(root, relative));
  return { sha256: sha(bytes), bytes: bytes.length };
};
const hashValue = (value) => sha(Buffer.from(JSON.stringify(value)));
const sets = (values) => [...new Set(values)];

function readGlb(bytes) {
  if (bytes.length < 20 || bytes.toString("ascii", 0, 4) !== "glTF") throw new Error("invalid_glb_header");
  const version = bytes.readUInt32LE(4);
  const declaredLength = bytes.readUInt32LE(8);
  const jsonLength = bytes.readUInt32LE(12);
  const jsonType = bytes.toString("ascii", 16, 20);
  if (version !== 2 || declaredLength !== bytes.length || jsonType !== "JSON" || 20 + jsonLength > bytes.length) {
    throw new Error("invalid_glb_v2_json_chunk");
  }
  const document = JSON.parse(bytes.subarray(20, 20 + jsonLength).toString("utf8").trim());
  const binHeader = 20 + jsonLength;
  if (binHeader + 8 > bytes.length || bytes.toString("ascii", binHeader + 4, binHeader + 8) !== "BIN\0") {
    throw new Error("missing_glb_bin_chunk");
  }
  const binStart = binHeader + 8;
  const readAccessor = (index) => {
    const accessor = document.accessors[index];
    if (!accessor || accessor.bufferView == null) return [];
    const view = document.bufferViews[accessor.bufferView];
    const component = accessor.componentType;
    const itemSize = ({ SCALAR: 1, VEC2: 2, VEC3: 3, VEC4: 4, MAT2: 4, MAT3: 9, MAT4: 16 })[accessor.type];
    if (!accessor || !view || component !== 5126 || itemSize !== 1) return [];
    const stride = view.byteStride ?? 4;
    const start = binStart + (view.byteOffset ?? 0) + (accessor.byteOffset ?? 0);
    const result = [];
    for (let i = 0; i < accessor.count; i++) result.push(bytes.readFloatLE(start + i * stride));
    return result;
  };
  const clips = (document.animations ?? []).map((animation) => {
    const timeValues = new Set();
    const pathCounts = {};
    const modes = new Set();
    const targets = new Set();
    for (const channel of animation.channels ?? []) {
      const sampler = animation.samplers[channel.sampler];
      const times = readAccessor(sampler.input);
      times.forEach((time) => timeValues.add(Number(time.toFixed(7))));
      pathCounts[channel.target.path] = (pathCounts[channel.target.path] ?? 0) + 1;
      modes.add(sampler.interpolation ?? "LINEAR");
      const node = document.nodes[channel.target.node];
      targets.add(node?.name ?? String(channel.target.node));
    }
    const keyframeTimes = [...timeValues].sort((a, b) => a - b);
    return {
      id: animation.name ?? null,
      channelCount: (animation.channels ?? []).length,
      targetNodeCount: targets.size,
      targetNodeNames: [...targets].sort(),
      channelPaths: pathCounts,
      interpolationModes: [...modes].sort(),
      keyframeTimesSeconds: keyframeTimes,
      durationSeconds: keyframeTimes.length ? keyframeTimes[keyframeTimes.length - 1] : null,
    };
  });
  let meshes = 0, triangleCount = 0, vertexCount = 0, morphTargetCount = 0, indexedPrimitiveCount = 0;
  for (const mesh of document.meshes ?? []) for (const primitive of mesh.primitives ?? []) {
    meshes++;
    const position = document.accessors[primitive.attributes?.POSITION];
    vertexCount += position?.count ?? 0;
    morphTargetCount = Math.max(morphTargetCount, primitive.targets?.length ?? 0);
    const index = primitive.indices == null ? null : document.accessors[primitive.indices];
    if ((primitive.mode ?? 4) === 4) {
      triangleCount += Math.floor((index?.count ?? position?.count ?? 0) / 3);
      if (index) indexedPrimitiveCount++;
    }
  }
  return {
    glbVersion: version,
    nodeCount: document.nodes?.length ?? 0,
    sceneCount: document.scenes?.length ?? 0,
    meshPrimitiveCount: meshes,
    vertexCount,
    triangleCount,
    indexedPrimitiveCount,
    maxMorphTargetCountPerPrimitive: morphTargetCount,
    clips,
    nodes: document.nodes ?? [],
    document,
    binStart,
  };
}

function transformDescriptor(asset) {
  const binding = asset.sourceBinding;
  const members = (binding?.members ?? []).map((member) => ({
    nodeId: member.nodeId,
    geometrySha256: member.geometrySha256,
    instanceMatrix: member.instanceMatrix,
  })).sort((a, b) => a.nodeId.localeCompare(b.nodeId) || a.geometrySha256.localeCompare(b.geometrySha256));
  const staticBinding = { ...asset.staticBinding };
  delete staticBinding.side;
  return {
    staticBinding,
    rigNodeIds: (asset.rig?.nodeBindings ?? []).map((row) => row.nodeId).sort(),
    frameId: binding?.frameId ?? asset.staticBinding.frameId,
    units: binding?.units ?? asset.staticBinding.units,
    deformation: binding?.deformation ?? null,
    members,
  };
}

function playbackDescriptor(candidate, clip) {
  const pose = candidate.asset.poseControl ?? null;
  return {
    clipId: candidate.asset.clip.id,
    declaredDurationSeconds: candidate.asset.clip.durationSeconds,
    glbDurationSeconds: clip?.durationSeconds ?? null,
    actionDirection: pose?.actionDirection ?? "forward",
    startDegrees: pose?.startDegrees ?? null,
    endDegrees: pose?.endDegrees ?? null,
    interpolationModes: clip?.interpolationModes ?? [],
    channelPaths: clip?.channelPaths ?? {},
    keyframeTimesSeconds: clip?.keyframeTimesSeconds ?? [],
    animationTargetNodeNames: clip?.targetNodeNames ?? [],
  };
}

function variantSummary(candidate, runtimeSource, selector, liveRow, getterMatch) {
  const binding = candidate.asset.sourceBinding;
  const subject = binding?.members?.find((member) => member.sourceKey === binding.subjectSourceKey);
  return {
    targetId: runtimeSource + "|" + selector + "|" + candidate.asset.id + "|" + (binding?.subjectSourceKey ?? "missing-subject"),
    runtimeSource,
    selector,
    optionId: candidate.option.actionKey ?? candidate.option.id ?? null,
    learnerActionKey: candidate.option.learnerActionKey ?? null,
    label: candidate.option.label,
    learningIntent: candidate.option.learningIntent ?? null,
    subjectKind: binding?.subjectKind ?? "muscle",
    sourceKey: binding?.subjectSourceKey ?? null,
    sourceKeySide: subject?.side ?? null,
    selectedRowKind: liveRow?.kind ?? null,
    selectedRowSide: liveRow?.side ?? null,
    selectedRowEnglishName: liveRow?.names?.en ?? null,
    selectedRowSearchGroupKey: liveRow?.searchGroupKey ?? null,
    sideApplicability: candidate.option.sideApplicability ?? null,
    selectedMemberRole: subject?.role ?? null,
    memberRoleSet: sets((binding?.members ?? []).map((member) => member.role)).sort(),
    movingStructureIds: candidate.definition.movingStructureIds ?? [],
    fixedStructureIds: candidate.definition.fixedStructureIds ?? [],
    poseControl: candidate.asset.poseControl ?? null,
    sourceBinding: candidate.asset.sourceBinding ?? null,
    assetId: candidate.asset.id,
    uri: candidate.asset.uri,
    sha256: candidate.asset.sha256,
    clipId: candidate.asset.clip.id,
    definitionId: candidate.definition.id,
    transformFingerprint: hashValue(transformDescriptor(candidate.asset)),
    playbackFingerprint: hashValue(playbackDescriptor(candidate, candidate.clipMeta)),
    liveLoaderCandidateMatch: getterMatch,
    liveRouteReachable: Boolean(liveRow && liveRow.routeAudience === "learner" && liveRow.localDisplayEligible && liveRow.inspectionEligible),
    liveSearchListedDirectly: candidate.liveSearchListedDirectly,
    liveSidePickerReachable: candidate.liveSidePickerReachable,
    inspectionStatus: "not_checked",
    checkedPhases: [],
    visualEvidence: null,
    automaticMetricsEvidence: null,
  };
}

const start = await json("work/evidence/MV1/preservation/start.json");
const [bundle, delivery, waveRegistration, intents, authoringRegistry, attachmentContext, learnerCards, compiledManifest, assetSources] = await Promise.all([
  json("atlas-data/motion/motion-learning.json"),
  json("atlas-data/motion/local-motion-delivery-index.json"),
  json("atlas-data/motion/t66-wave1-registration.json"),
  json("atlas-data/motion/t66-motion-learning-intents.json"),
  json("atlas-data/motion/authoring/registry.json"),
  json("atlas-data/terminology/learner-attachment-context.json"),
  json("atlas-data/terminology/learner-card-runtime.json"),
  json("atlas-data/source-cache/datasets/za/compiled/manifest.json"),
  json("atlas-data/motion/motion-asset-sources.json"),
]);

const runtimeInputSources = ["actions", "wave1Actions"];
const rawCandidates = [];
for (const runtimeSource of runtimeInputSources) {
  const collection = runtime[runtimeSource] ?? {};
  for (const [selector, rows] of Object.entries(collection)) for (const option of rows) {
    if (!option.candidate) continue;
    const candidate = { option, definition: option.candidate.definition, asset: option.candidate.asset };
    rawCandidates.push({ runtimeSource, selector, candidate });
  }
}

let live = { available: false, reason: "runtime_endpoint_not_checked" };
try {
  const [integrationResponse, datasetResponse] = await Promise.all([
    fetch(runtimeBase + "/__atlas/integration.json"),
    fetch(runtimeBase + "/__atlas/datasets/human-atlas-local/manifest.json"),
  ]);
  if (!integrationResponse.ok || !datasetResponse.ok) throw new Error("live_runtime_http_" + integrationResponse.status + "_" + datasetResponse.status);
  const [integrationBytes, datasetBytes] = await Promise.all([integrationResponse.arrayBuffer(), datasetResponse.arrayBuffer()]);
  const integrationRaw = JSON.parse(Buffer.from(integrationBytes).toString("utf8"));
  const datasetRaw = JSON.parse(Buffer.from(datasetBytes).toString("utf8"));
  const dataset = validateDataset(datasetRaw);
  const integration = validateRuntimeIntegration(integrationRaw, dataset);
  const records = integration.objects;
  const byKey = new Map(records.map((row) => [row.sourceKey, row]));
  const defaultSearch = searchStructures(records, "", [], "learner");
  const defaultSearchKeys = new Set(defaultSearch.map((row) => row.sourceKey));
  const byEnglishName = new Map();
  for (const row of records) if (row.routeAudience === "learner" && row.localDisplayEligible && row.inspectionEligible && row.side) {
    const list = byEnglishName.get(row.names.en) ?? [];
    list.push(row); byEnglishName.set(row.names.en, list);
  }
  const totalSearchableByLabel = new Map();
  live = {
    available: true,
    baseUrl: runtimeBase,
    integrationHttpStatus: integrationResponse.status,
    integrationSha256: sha(Buffer.from(integrationBytes)),
    integrationBytes: integrationBytes.byteLength,
    integrationSchemaVersion: integration.schemaVersion,
    integrationObjectCount: records.length,
    integrationScope: integration.scope,
    integratedRowKinds: Object.fromEntries(sets(records.map((row) => row.kind)).sort().map((kind) =>
      [kind, records.filter((row) => row.kind === kind).length])),
    defaultSearchChoiceCount: defaultSearch.length,
    datasetHttpStatus: datasetResponse.status,
    datasetSha256: sha(Buffer.from(datasetBytes)),
    datasetBytes: datasetBytes.byteLength,
    datasetNamespace: dataset.namespace,
    datasetRevision: dataset.revision,
    datasetInstanceCount: dataset.instances.length,
    selectedTargetRows: 0,
    exactGetterMatchRows: 0,
    discoverableBySearchOrSidePickerRows: 0,
    undiscoverableTargetKeys: [],
  };
  for (const raw of rawCandidates) {
    const asset = raw.candidate.asset;
    const subjectKey = asset.sourceBinding?.subjectSourceKey;
    const row = byKey.get(subjectKey);
    const side = row?.side ?? raw.candidate.option.sideApplicability;
    const options = motionActionOptionsForLearner(row?.haConceptId ?? null, side, subjectKey);
    raw.liveRow = row ?? null;
    raw.liveGetterMatch = options.some((option) =>
      option.candidate?.asset.id === asset.id && option.candidate?.definition.id === raw.candidate.definition.id);
    raw.liveSearchListedDirectly = defaultSearchKeys.has(subjectKey);
    const sideRows = row ? byEnglishName.get(row.names.en) ?? [] : [];
    raw.liveSidePickerReachable = Boolean(row?.side && sideRows.some((choice) => choice.side !== row.side && defaultSearchKeys.has(choice.sourceKey)));
    let labelSearchReachable = false;
    if (row && !totalSearchableByLabel.has(row.label)) {
      try {
        totalSearchableByLabel.set(row.label,
          searchStructures(records, row.label, [], "learner").some((choice) => choice.sourceKey === subjectKey));
      } catch { totalSearchableByLabel.set(row.label, false); }
    }
    labelSearchReachable = totalSearchableByLabel.get(row?.label) === true;
    raw.liveLearnerDiscoverable = Boolean(row?.routeAudience === "learner" && row.localDisplayEligible
      && row.inspectionEligible && row.kind === (asset.sourceBinding?.subjectKind ?? "muscle")
      && (raw.liveSearchListedDirectly || raw.liveSidePickerReachable || labelSearchReachable));
    live.selectedTargetRows++;
    if (raw.liveGetterMatch) live.exactGetterMatchRows++;
    if (raw.liveLearnerDiscoverable) live.discoverableBySearchOrSidePickerRows++;
    if (!raw.liveLearnerDiscoverable && !live.undiscoverableTargetKeys.some((key) => key === subjectKey)) live.undiscoverableTargetKeys.push(subjectKey);
  }
}
catch (error) {
  live = { available: false, baseUrl: runtimeBase, error: String(error?.message ?? error) };
}

const runtimeAssetRecords = new Map(bundle.motionAssets.map((asset) => [asset.id, asset]));
const wavePackages = new Map((waveRegistration.packages ?? []).map((asset) => [asset.id, asset]));
const deliveryPairs = new Set((delivery.entries ?? []).map((entry) => entry.uri + "|" + entry.sha256));
const glbByPair = new Map();
for (const row of rawCandidates) {
  const asset = row.candidate.asset;
  const pair = asset.uri + "|" + asset.sha256;
  if (glbByPair.has(pair)) continue;
  const relative = asset.uri.replaceAll("\\\\", "/");
  const record = {
    uri: asset.uri,
    expectedSha256: asset.sha256,
    pathExists: false,
    actualSha256: null,
    hashMatches: false,
    bytes: null,
    inDeliveryIndex: deliveryPairs.has(pair),
    glbStatus: "not_checked",
    glbError: null,
    glbMetadata: null,
  };
  try {
    const bytes = await readFile(resolve(root, relative));
    record.pathExists = true;
    record.actualSha256 = sha(bytes);
    record.hashMatches = record.actualSha256 === asset.sha256;
    record.bytes = bytes.length;
    if (!record.hashMatches) throw new Error("registered_glb_hash_mismatch");
    record.glbMetadata = readGlb(bytes);
    record.glbStatus = "pass";
  } catch (error) {
    record.glbStatus = record.pathExists ? "error" : "error";
    record.glbError = String(error?.message ?? error);
  }
  glbByPair.set(pair, record);
}

const groupsByDedupeKey = new Map();
const inventoryRows = [];
for (const raw of rawCandidates) {
  const { runtimeSource, selector, candidate } = raw;
  const asset = candidate.asset;
  const kind = asset.sourceBinding?.subjectKind ?? "muscle";
  const file = glbByPair.get(asset.uri + "|" + asset.sha256);
  const clipMeta = file?.glbMetadata?.clips?.find((clip) => clip.id === asset.clip.id) ?? null;
  candidate.clipMeta = clipMeta;
  const transform = transformDescriptor(asset);
  const playback = playbackDescriptor(candidate, clipMeta);
  const transformFingerprint = hashValue(transform);
  const playbackFingerprint = hashValue(playback);
  const dedupeKey = hashValue({
    sha256: asset.sha256,
    clipId: asset.clip.id,
    transformFingerprint,
    playbackFingerprint,
  });
  const variant = variantSummary(candidate, runtimeSource, selector, raw.liveRow, raw.liveGetterMatch);
  variant.liveSearchListedDirectly = Boolean(raw.liveSearchListedDirectly);
  variant.liveSidePickerReachable = Boolean(raw.liveSidePickerReachable);
  variant.liveLearnerDiscoverable = Boolean(raw.liveLearnerDiscoverable);
  variant.glbStatus = file?.glbStatus ?? "error";
  variant.glbHashMatches = Boolean(file?.hashMatches);
  variant.clipExists = Boolean(clipMeta);
  variant.clipDurationMatches = Boolean(clipMeta && Math.abs(clipMeta.durationSeconds - asset.clip.durationSeconds) <= 1e-4);
  variant.inventoryScope = kind === "muscle" ? "in_scope_muscle" : "out_of_scope_bone_motion_context";
  variant.inspectionStatus = "not_checked";
  inventoryRows.push(variant);
  const group = groupsByDedupeKey.get(dedupeKey) ?? {
    dedupeKey,
    sourceScopes: [],
    sha256: asset.sha256,
    uri: asset.uri,
    clipId: asset.clip.id,
    transformFingerprint,
    playbackFingerprint,
    transform,
    playback,
    variantIds: [],
    sourceKeys: [],
    selectedRoles: [],
    memberRoleSets: [],
    sides: [],
    sideApplicability: [],
    inspectionStatus: "not_checked",
    checkedPhases: [],
    visualEvidence: null,
    automaticMetricsEvidence: null,
  };
  group.sourceScopes.push(kind === "muscle" ? "muscle" : "bone");
  group.variantIds.push(variant.targetId);
  if (variant.sourceKey) group.sourceKeys.push(variant.sourceKey);
  if (variant.selectedMemberRole) group.selectedRoles.push(variant.selectedMemberRole);
  group.memberRoleSets.push(variant.memberRoleSet.join("|"));
  if (variant.sourceKeySide) group.sides.push(variant.sourceKeySide);
  if (variant.sideApplicability) group.sideApplicability.push(variant.sideApplicability);
  groupsByDedupeKey.set(dedupeKey, group);
}

const groups = [...groupsByDedupeKey.values()].map((group) => ({
  ...group,
  sourceScopes: sets(group.sourceScopes).sort(),
  sourceScope: sets(group.sourceScopes).length === 1 ? sets(group.sourceScopes)[0] : "shared",
  variantIds: sets(group.variantIds),
  sourceKeys: sets(group.sourceKeys),
  selectedRoles: sets(group.selectedRoles).sort(),
  memberRoleSets: sets(group.memberRoleSets).sort(),
  sides: sets(group.sides).sort(),
  sideApplicability: sets(group.sideApplicability).sort(),
})).sort((a, b) => a.uri.localeCompare(b.uri) || a.clipId.localeCompare(b.clipId) || a.dedupeKey.localeCompare(b.dedupeKey));

const hashClipGroup = (row) => row.sha256 + "|" + row.clipId;
const muscleRows = inventoryRows.filter((row) => row.inventoryScope === "in_scope_muscle");
const boneRows = inventoryRows.filter((row) => row.inventoryScope !== "in_scope_muscle");
const muscleGroups = groups.filter((group) => group.sourceScopes.includes("muscle"));
const boneGroups = groups.filter((group) => group.sourceScopes.includes("bone"));
const deliveryExtra = (delivery.entries ?? []).filter((entry) =>
  ![...glbByPair.values()].some((file) => file.uri === entry.uri && file.expectedSha256 === entry.sha256));
const runtimeAssetMap = new Map(inventoryRows.map((row) => [row.assetId, row]));
const registeredRecords = bundle.motionAssets.map((asset) => ({
  id: asset.id,
  uri: asset.uri,
  sha256: asset.sha256,
  technicalStatus: asset.technicalStatus,
  representationType: asset.representationType,
  currentLearnerReachable: runtimeAssetMap.has(asset.id),
}));
const authoringFiles = [];
for (const record of authoringRegistry.records ?? []) {
  try {
    const actual = await fileHash(record.path);
    const bytes = await readFile(resolve(root, record.path));
    const doc = JSON.parse(bytes.toString("utf8"));
    const allStrings = [];
    const walk = (value) => {
      if (typeof value === "string") allStrings.push(value);
      else if (Array.isArray(value)) value.forEach(walk);
      else if (value && typeof value === "object") Object.values(value).forEach(walk);
    };
    walk(doc);
    const refSet = new Set(allStrings);
    const matches = inventoryRows.filter((row) => refSet.has(row.assetId) || refSet.has(row.sourceKey)
      || refSet.has(row.uri) || refSet.has(row.sha256) || refSet.has(row.clipId));
    authoringFiles.push({ id: record.id, path: record.path, expectedSha256: record.sha256,
      actualSha256: actual.sha256, bytes: actual.bytes, hashMatches: actual.sha256 === record.sha256,
      referencedLearnerVariants: matches.length, referencedMuscleVariants: matches.filter((row) => row.inventoryScope === "in_scope_muscle").length });
  } catch (error) {
    authoringFiles.push({ id: record.id, path: record.path, expectedSha256: record.sha256,
      actualSha256: null, bytes: null, hashMatches: false, referencedLearnerVariants: 0,
      referencedMuscleVariants: 0, error: String(error?.message ?? error) });
  }
}

const sourceSideCounts = Object.fromEntries(["left", "right", "bilateral", "midline", "not_applicable", "null"].map((side) =>
  [side, muscleRows.filter((row) => (row.sourceKeySide ?? row.sideApplicability ?? "null") === (side === "null" ? "null" : side)).length]));
const roleVariantCounts = {};
for (const role of sets(muscleRows.flatMap((row) => row.memberRoleSet))) {
  roleVariantCounts[role] = muscleRows.filter((row) => row.memberRoleSet.includes(role)).length;
}
const summary = {
  capturedAt: new Date().toISOString(),
  task: "MV1",
  statusMeaning: "technical_hash_and_mapping_checks_do_not_approve_natural_motion_or_human_review",
  startingSnapshotReference: "work/evidence/at6-motion-camera-review-2026-10-11/motion-inventory.json",
  startingSnapshotCounts: { motionActions: 1166, assetRecords: 1160, uniqueUriHashPairs: 46, deliveryIndexEntries: 74 },
  liveRuntime: live,
  learnerGeneratedRuntime: {
    schemaVersion: runtime.schemaVersion,
    actionSelectors: Object.keys(runtime.actions ?? {}).length,
    actionRows: Object.values(runtime.actions ?? {}).reduce((n, rows) => n + rows.length, 0),
    sourceBoundCandidates: Object.values(runtime.actions ?? {}).flat().filter((row) => row.candidate).length,
    wave1Selectors: Object.keys(runtime.wave1Actions ?? {}).length,
    wave1ActionRows: Object.values(runtime.wave1Actions ?? {}).reduce((n, rows) => n + rows.length, 0),
    wave1SourceBoundCandidates: Object.values(runtime.wave1Actions ?? {}).flat().filter((row) => row.candidate).length,
  },
  actualReachableCandidates: {
    total: inventoryRows.length,
    muscleSubjectCandidates: muscleRows.length,
    boneSubjectMotionCandidates: boneRows.length,
    uniqueMuscleSubjectSourceKeys: sets(muscleRows.map((row) => row.sourceKey)).length,
    uniqueBoneSubjectSourceKeys: sets(boneRows.map((row) => row.sourceKey)).length,
    muscleHashClipPairs: new Set(muscleRows.map(hashClipGroup)).size,
    allHashClipPairs: new Set(inventoryRows.map(hashClipGroup)).size,
    musclePlaybackMappingsAfterHashClipTransformPlaybackDedup: muscleGroups.length,
    allPlaybackMappingsAfterHashClipTransformPlaybackDedup: groups.length,
    muscleRoleSideSubjectVariantsKeptSeparate: muscleRows.length,
    muscleSourceSideCounts: sourceSideCounts,
    muscleMemberRoleCoverage: roleVariantCounts,
  },
  glbFiles: [...glbByPair.values()].map(({ glbMetadata, ...file }) => ({ ...file,
    clipCount: glbMetadata?.clips?.length ?? 0,
    clipIds: glbMetadata?.clips?.map((clip) => clip.id) ?? [],
    totalNodes: glbMetadata?.nodeCount ?? null,
    totalMeshPrimitives: glbMetadata?.meshPrimitiveCount ?? null,
    totalVertices: glbMetadata?.vertexCount ?? null,
    totalTriangles: glbMetadata?.triangleCount ?? null,
  })).sort((a, b) => a.uri.localeCompare(b.uri)),
  deliveryIndex: {
    entryCount: delivery.entries?.length ?? 0,
    actualLearnerReachableUriHashPairs: new Set(inventoryRows.map((row) => row.uri + "|" + row.sha256)).size,
    orphanEntriesNotReachedByCurrentRuntime: deliveryExtra,
    currentRuntimePairsMissingFromIndex: [...new Map(inventoryRows.filter((row) =>
      !deliveryPairs.has(row.uri + "|" + row.sha256)).map((row) => [row.uri + "|" + row.sha256, { uri: row.uri, sha256: row.sha256 }])).values()],
  },
  registeredAssetRecords: { count: registeredRecords.length, rows: registeredRecords },
  authoringInputs: { registryPath: "atlas-data/motion/authoring/registry.json",
    registryRecordCount: authoringFiles.length, hashMatches: authoringFiles.filter((row) => row.hashMatches).length,
    records: authoringFiles },
  candidateRows: inventoryRows,
  uniquePlaybackMappings: groups,
};

const output = { ...summary,
  inputHashes: {
    "atlas-data/motion/motion-learning.json": await fileHash("atlas-data/motion/motion-learning.json"),
    "atlas-data/motion/motion-asset-sources.json": await fileHash("atlas-data/motion/motion-asset-sources.json"),
    "atlas-data/motion/motion-scenes.json": await fileHash("atlas-data/motion/motion-scenes.json"),
    "atlas-data/motion/local-motion-delivery-index.json": await fileHash("atlas-data/motion/local-motion-delivery-index.json"),
    "atlas-data/motion/t66-wave1-registration.json": await fileHash("atlas-data/motion/t66-wave1-registration.json"),
    "atlas-data/motion/t66-motion-learning-intents.json": await fileHash("atlas-data/motion/t66-motion-learning-intents.json"),
    "atlas-data/motion/authoring/registry.json": await fileHash("atlas-data/motion/authoring/registry.json"),
    "atlas-data/terminology/learner-card-runtime.json": await fileHash("atlas-data/terminology/learner-card-runtime.json"),
    "atlas-data/terminology/learner-attachment-context.json": await fileHash("atlas-data/terminology/learner-attachment-context.json"),
    "atlas-data/source-cache/datasets/za/compiled/manifest.json": await fileHash("atlas-data/source-cache/datasets/za/compiled/manifest.json"),
    "atlas-web/src/data/learnerMotionRuntime.generated.ts": await fileHash("atlas-web/src/data/learnerMotionRuntime.generated.ts"),
    "atlas-web/src/data/motionLearningData.ts": await fileHash("atlas-web/src/data/motionLearningData.ts"),
    "atlas-web/src/domain/motionLearning.ts": await fileHash("atlas-web/src/domain/motionLearning.ts"),
    "atlas-web/src/ui/MotionLearningPanel.tsx": await fileHash("atlas-web/src/ui/MotionLearningPanel.tsx"),
    "atlas-web/src/viewer/animationSceneAdapter.ts": await fileHash("atlas-web/src/viewer/animationSceneAdapter.ts"),
    "atlas-web/src/viewer/datasets/DatasetSceneAdapter.ts": await fileHash("atlas-web/src/viewer/datasets/DatasetSceneAdapter.ts"),
    "atlas-web/src/viewer/animationPlayback.ts": await fileHash("atlas-web/src/viewer/animationPlayback.ts"),
  },
  excludedAnalysis: {
    outOfScope: "bone motion candidates retained in the inventory as context; MV1 scope is muscle-subject movement",
    notHumanApproval: "no natural-contraction approval, anatomical review, educational release, or clinical claim follows from runtime reachability or numeric metrics",
    exactAttachmentLandmarks: "no authored attachment landmark array was found in the learner candidate contract; attachment drift requires visual review and is not numerically inferred",
  },
};
await mkdir(runDir, { recursive: true });
if (!live.available) {
  const stamp = new Date().toISOString().replaceAll(":", "-");
  const attemptPath = resolve(runDir, "runtime", `inventory-refresh-attempt-${stamp}.json`);
  await mkdir(dirname(attemptPath), { recursive: true });
  await writeFile(attemptPath, JSON.stringify({ ...output,
    runDisposition: "live_runtime_fetch_failed; diagnostic_only; never replaces the frozen inventory",
  }, null, 2) + "\n");
  let priorLiveSnapshot = false;
  try {
    const previous = JSON.parse(await readFile(outPath, "utf8"));
    priorLiveSnapshot = previous.liveRuntime?.available === true;
  } catch { /* no successful inventory exists yet */ }
  console.log(JSON.stringify({
    status: "live_runtime_unavailable",
    diagnosticAttempt: attemptPath,
    preservedFrozenInventory: priorLiveSnapshot ? outPath : null,
    liveRuntimeError: live.error ?? "unknown",
    message: "No live runtime snapshot was created or replaced. Resolve learner runtime access and rerun to freeze learner reachability.",
  }, null, 2));
  process.exitCode = 2;
} else {
  await writeFile(outPath, JSON.stringify(output, null, 2) + "\n");
console.log(JSON.stringify({
  status: "inventory_frozen",
  output: outPath,
  liveRuntimeAvailable: live.available,
  liveRuntimeObjects: live.integrationObjectCount ?? null,
  liveSearchChoices: live.defaultSearchChoiceCount ?? null,
  candidates: inventoryRows.length,
  muscleCandidates: muscleRows.length,
  boneContextCandidates: boneRows.length,
  uniqueMuscleFileClipPairs: new Set(muscleRows.map(hashClipGroup)).size,
  uniqueMusclePlaybackMappings: muscleGroups.length,
  roleSideVariants: muscleRows.length,
  uniqueAllFileClipPairs: new Set(inventoryRows.map(hashClipGroup)).size,
  uniqueAllPlaybackMappings: groups.length,
  uniqueUriHashPairs: glbByPair.size,
  deliveryIndexEntries: delivery.entries?.length ?? 0,
  orphanDeliveryEntries: deliveryExtra.length,
  authoringHashesMatched: authoringFiles.filter((row) => row.hashMatches).length + "/" + authoringFiles.length,
}, null, 2));
}
