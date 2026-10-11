#!/usr/bin/env node
/** Recheck each live learner muscle mapping against the running integration and dataset manifests. */
import { createHash } from "node:crypto";
import { readFile, writeFile, mkdir } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import runtime from "../../../../atlas-web/src/data/learnerMotionRuntime.generated.ts";
import { motionActionOptionsForLearner } from "../../../../atlas-web/src/data/motionLearningData.ts";
import { searchStructures, validateRuntimeIntegration } from "../../../../atlas-web/src/viewer/datasets/integration.ts";
import { validateDataset } from "../../../../atlas-web/src/viewer/datasets/schema.ts";

const here = dirname(fileURLToPath(import.meta.url));
const root = resolve(here, "../../../..");
const run = resolve(here, "../2026-10-11-run-01");
const output = resolve(run, "runtime/live-binding-validation.json");
const inventory = JSON.parse(await readFile(resolve(run, "inventory.json"), "utf8"));
const expectedMuscleTargets = new Set(inventory.candidateRows.filter(row => row.subjectKind === "muscle").map(row => row.targetId));
const base = process.argv.find(a => a.startsWith("--runtime-base="))?.slice("--runtime-base=".length) ?? "http://127.0.0.1:5183";
const sha = bytes => createHash("sha256").update(bytes).digest("hex");
const [integrationResponse, datasetResponse] = await Promise.all([
  fetch(base + "/__atlas/integration.json"),
  fetch(base + "/__atlas/datasets/human-atlas-local/manifest.json"),
]);
if (!integrationResponse.ok || !datasetResponse.ok) throw new Error("live_runtime_manifest_http_error");
const [integrationBytes, datasetBytes] = await Promise.all([integrationResponse.arrayBuffer(), datasetResponse.arrayBuffer()]);
const dataset = validateDataset(JSON.parse(Buffer.from(datasetBytes).toString("utf8")));
const integration = validateRuntimeIntegration(JSON.parse(Buffer.from(integrationBytes).toString("utf8")), dataset);
const records = new Map(integration.objects.map(row => [row.sourceKey, row]));
const instances = new Map(dataset.instances.map(row => [row.sourceKey, row]));
const chunks = new Map(dataset.chunks.map(row => [row.id, row]));
const defaultSearchSources = new Set(searchStructures(integration.objects, "", [], "learner").map(row => row.sourceKey));
const targets = [];
for (const sourceName of ["actions", "wave1Actions"]) for (const [selector, options] of Object.entries(runtime[sourceName] ?? {})) for (const option of options) {
  const candidate = option.candidate;
  if (!candidate || !candidate.asset.sourceBinding?.subjectSourceKey) continue;
  const asset = candidate.asset, binding = asset.sourceBinding, errors = [];
  const targetId = sourceName + "|" + selector + "|" + asset.id + "|" + binding.subjectSourceKey;
  const subject = records.get(binding.subjectSourceKey);
  if (subject?.kind !== "muscle" && !expectedMuscleTargets.has(targetId)) continue;
  const routeReachable = Boolean(subject?.routeAudience === "learner" && subject.localDisplayEligible && subject.inspectionEligible && subject.kind === "muscle");
  if (!routeReachable) errors.push("subject_not_learner_route_reachable");
  const side = subject?.side ?? option.sideApplicability;
  const getter = motionActionOptionsForLearner(subject?.haConceptId ?? null, side, binding.subjectSourceKey);
  if (!getter.some(row => row.candidate?.asset.id === asset.id && row.candidate?.definition.id === candidate.definition.id)) errors.push("exact_candidate_getter_mismatch");
  if (!asset.sourceBinding || asset.sourceBinding.frameId !== dataset.frameContract?.targetFrameId || binding.frameId !== asset.staticBinding.frameId
      || binding.units !== dataset.unit || asset.staticBinding.modelId !== binding.datasetNamespace
      || asset.staticBinding.sceneRevision !== binding.datasetRevision) errors.push("frame_unit_model_or_revision_mismatch");
  const component = integration.sourceComponents?.[binding.datasetNamespace];
  const componentMatches = component
    ? component.datasetRevision === binding.datasetRevision && component.integrationRevision === binding.integrationRevision
      && component.overlaySha256 === binding.sourceOverlaySha256
      && (dataset.sourceRevisions?.[binding.datasetNamespace] ?? (dataset.namespace === binding.datasetNamespace ? dataset.revision : null)) === binding.datasetRevision
    : binding.datasetNamespace === dataset.namespace && binding.datasetRevision === dataset.revision
      && binding.integrationRevision === integration.revision && binding.sourceOverlaySha256 === integration.sourceOverlaySha256;
  if (!componentMatches) errors.push("integration_component_revision_or_overlay_mismatch");
  const seen = new Set();
  const memberErrors = [];
  for (const member of binding.members ?? []) {
    const reasons = [];
    if (seen.has(member.sourceKey)) reasons.push("duplicate_sourceKey");
    seen.add(member.sourceKey);
    const instance = instances.get(member.sourceKey), row = records.get(member.sourceKey);
    if (!instance || !row) reasons.push("sourceKey_not_in_live_dataset_and_integration");
    else {
      const namespace = instance.sourceNamespace ?? dataset.namespace;
      const lod = instance.lods?.[member.lod];
      const chunk = lod ? chunks.get(lod.chunk) : null;
      if (namespace !== member.sourceNamespace) reasons.push("source_namespace_mismatch");
      if (!lod || lod.resource !== member.resourceKey) reasons.push("LOD_resource_mismatch");
      if (!chunk || chunk.sha256 !== member.sourceChunkSha256) reasons.push("source_chunk_hash_mismatch");
      if (JSON.stringify(instance.matrix) !== JSON.stringify(member.instanceMatrix)) reasons.push("instance_matrix_mismatch");
      if (row.side !== member.side) reasons.push("side_mismatch");
      if (!row.localDisplayEligible || row.hardHoldReasons?.length || row.sourceHiddenStatePreserved?.hideViewport) reasons.push("member_not_runtime_display_eligible");
      if (member.role === "deforming_muscle_surface" && row.kind !== "muscle") reasons.push("deforming_surface_not_muscle");
    }
    if (reasons.length) memberErrors.push({ sourceKey: member.sourceKey, nodeId: member.nodeId, role: member.role, reasons });
  }
  if (memberErrors.length) errors.push("bound_member_mismatch");
  const subjectMember = binding.members?.find(member => member.sourceKey === binding.subjectSourceKey);
  if (!subjectMember || subjectMember.side !== asset.staticBinding.side || subjectMember.role !== "deforming_muscle_surface" && subjectMember.role !== "deforming_passive_surface") errors.push("subject_role_or_side_mismatch");
  const labelSearchMatch = subject ? searchStructures(integration.objects, subject.label, [], "learner").some(row => row.sourceKey === subject.sourceKey) : false;
  const defaultSearchChoice = defaultSearchSources.has(binding.subjectSourceKey);
  targets.push({ targetId,
    sourceName, selector, optionId: option.actionKey ?? option.id ?? null, assetId: asset.id,
    sourceKey: binding.subjectSourceKey, side: subject?.side ?? null, role: subjectMember?.role ?? null,
    uri: asset.uri, sha256: asset.sha256, clipId: asset.clip.id, routeReachable, exactGetterMatch: errors.includes("exact_candidate_getter_mismatch") === false,
    defaultSearchChoice, labelSearchMatch, sideOptionReachable: errors.includes("exact_candidate_getter_mismatch") === false,
    memberCount: binding.members?.length ?? 0, memberErrorCount: memberErrors.length,
    status: errors.length ? "fail" : "pass", errors, memberErrors });
}
const foundIds = new Set(targets.map(row => row.targetId));
for (const missing of [...expectedMuscleTargets].filter(targetId => !foundIds.has(targetId))) {
  targets.push({ targetId: missing, status: "error", errors: ["expected_learner_muscle_target_missing_from_live_runtime"] });
}
targets.sort((a, b) => a.targetId.localeCompare(b.targetId));
const errors = targets.filter(row => row.status !== "pass");
const report = { capturedAt: new Date().toISOString(), runtimeBase: base,
  integration: { httpStatus: integrationResponse.status, sha256: sha(Buffer.from(integrationBytes)), bytes: integrationBytes.byteLength,
    revision: integration.revision, objects: integration.objects.length, searchChoices: searchStructures(integration.objects, "", [], "learner").length },
  dataset: { httpStatus: datasetResponse.status, sha256: sha(Buffer.from(datasetBytes)), bytes: datasetBytes.byteLength,
    namespace: dataset.namespace, revision: dataset.revision, instanceCount: dataset.instances.length, chunkCount: dataset.chunks.length,
    frameId: dataset.frameContract?.targetFrameId, unit: dataset.unit },
  expectedTargets: expectedMuscleTargets.size, targets: targets.length, pass: targets.filter(row => row.status === "pass").length,
  fail: targets.filter(row => row.status === "fail").length, error: targets.filter(row => row.status === "error").length,
  defaultSearchChoiceCount: targets.filter(row => row.defaultSearchChoice).length,
  labelSearchMatchCount: targets.filter(row => row.labelSearchMatch).length,
  sideOptionReachableCount: targets.filter(row => row.sideOptionReachable).length, rows: targets };
await mkdir(dirname(output), { recursive: true });
await writeFile(output, JSON.stringify(report, null, 2) + "\n");
console.log(JSON.stringify({ status: report.fail || report.error ? "partial" : "pass", output, targets: report.targets, pass: report.pass, fail: report.fail, error: report.error,
  integrationObjects: report.integration.objects, datasetInstances: report.dataset.instanceCount }, null, 2));
