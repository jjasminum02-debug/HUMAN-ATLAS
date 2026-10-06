import { readFile, writeFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";
import { createHash } from "node:crypto";
import { projectLearnerActionText, projectLearnerMotionActionOptions } from "../src/domain/motionLearning.ts";

import { projectT66Wave1MotionOptions } from "../src/domain/t66Wave1Motion.ts";
import { serializeLearnerMotionRuntime } from "./serializeLearnerMotionRuntime.mjs";

const scriptDir = dirname(fileURLToPath(import.meta.url));
const root = resolve(scriptDir, "../..");
const inputPath = resolve(root, "atlas-data/motion/motion-learning.json");
const cardRuntimePath = resolve(root, "atlas-data/terminology/learner-card-runtime.json");
const outputPath = resolve(scriptDir, "../src/data/learnerMotionRuntime.generated.ts");
const checkOnly = process.argv.includes("--check");

const bundleBytes = await readFile(inputPath);
const bundle = JSON.parse(bundleBytes.toString("utf8"));
const cardRuntime = JSON.parse(await readFile(cardRuntimePath, "utf8"));
const acceptedSourceActions = {};
const acceptance = JSON.parse(await readFile(resolve(root, "atlas-data/motion/t66-priority-action-acceptance.json"), "utf8"));
if (acceptance.publicRedistribution !== "held" || acceptance.humanReview !== "not_performed") {
  throw new Error("Local source action acceptance cannot promote rights or human review");
}
for (const row of acceptance.rows) {
  const outcomeBytes = await readFile(resolve(root, row.outcomePath));
  const authoringBytes = await readFile(resolve(root, row.authoringPath));
  const digest = bytes => createHash("sha256").update(bytes).digest("hex");
  const outcome = JSON.parse(outcomeBytes).find(item => item.sourceKey === row.sourceKey && item.assetId === row.assetId);
  const authoring = JSON.parse(authoringBytes);
  const action = bundle.muscleActions.find(item => item.id === row.actionId);
  const asset = bundle.motionAssets.find(item => item.id === row.assetId);
  if (digest(outcomeBytes) !== row.outcomeSha256 || digest(authoringBytes) !== row.authoringSha256
      || !outcome?.passed || outcome.motionSha256 !== row.motionSha256 || outcome.side !== row.side
      || authoring.motionSha256 !== row.motionSha256 || !authoring.motorRoleSourceKeys?.includes(row.sourceKey)
      || action?.sourceSubjectKeys?.length !== 1 || action.sourceSubjectKeys[0] !== row.sourceKey
      || action.sideApplicability !== row.side
      || asset?.poseControl?.actionDirection !== authoring.poseRange?.actionDirection
      || (asset?.poseControl?.actionDirection === "reverse" && outcome.actionDirection !== "reverse")) {
    throw new Error(`Source action acceptance has drifted: ${row.actionId}`);
  }
  for (const member of asset.sourceBinding?.members ?? []) if (member.passiveCorrectiveMaxMetres != null) {
    const qcPath = authoring.glbInterpolationQcPaths?.[member.sourceKey];
    const dependency = authoring.verificationDependencies?.find(item => item.path === qcPath);
    if (!qcPath || !dependency) throw new Error("Passive contact corrective lacks emitted geometry verification");
    const qcBytes = await readFile(resolve(root, qcPath));
    const qc = JSON.parse(qcBytes);
    if (digest(qcBytes) !== dependency.sha256 || qc.motionGlbSha256 !== asset.sha256
        || qc.targetSourceKey !== member.sourceKey || !qc.passed || !qc.geometry?.passed || !qc.contact?.passed
        || member.role !== "co_moving_context" || !(member.passiveCorrectiveMaxMetres > 0 && member.passiveCorrectiveMaxMetres <= .001)) {
      throw new Error("Passive contact corrective verification has drifted");
    }
  }
  acceptedSourceActions[row.actionId] = row;
}

function safeCandidate(candidate) {
  if (!candidate) return null;
  const { definition, asset } = candidate;
  if (asset.representationType !== "source_bound_surface" || !asset.sourceBinding) {
    throw new Error("Learner candidate must be an exact source-bound surface package");
  }
  const { poseSourceRefs: _poseRefs, ...safeDefinition } = definition;
  return {
    definition: safeDefinition,
    asset,
  };
}

const actionsBySelector = new Map();
let projectedActionCount = 0;
const optionsBySelector = new Map();
for (const action of bundle.muscleActions ?? []) {
  if (typeof action.learnerActionKey === "string") {
    const linkedCards = (cardRuntime.actions ?? []).filter((row) => row.key === action.learnerActionKey
      && action.subjectIds?.includes(row.conceptId));
    if (linkedCards.length !== 1) {
      throw new Error(`Explicit learnerActionKey must resolve to exactly one card for a subject: ${action.id}`);
    }
  }
  const selectors = [...new Set([...(action.subjectIds ?? []), ...(action.sourceSubjectKeys ?? [])])];
  for (const selector of selectors) {
    const actionKey = action.learnerActionKey ?? action.id;
    if (!optionsBySelector.has(selector)) optionsBySelector.set(selector,
      projectLearnerMotionActionOptions(selector, bundle, [], null, acceptedSourceActions));
    const options = optionsBySelector.get(selector)
      .filter((option) => option.id === actionKey && option.subjectIds.includes(selector));
    for (const option of options) {
      const text = projectLearnerActionText(action, []);
      if (!text) continue;
      const row = {
        actionKey: `motion-option-${String(projectedActionCount++).padStart(3, "0")}`,
        learnerActionKey: typeof action.learnerActionKey === "string" ? action.learnerActionKey : null,
        label: text.label,
        text,
        sideApplicability: action.sideApplicability,
        learningIntent: option.learningIntent,
        candidate: safeCandidate(option.candidate),
      };
      const rows = actionsBySelector.get(selector) ?? [];
      if (!rows.some((existing) => existing.actionKey === row.actionKey)) {
        rows.push(row);
      }
      actionsBySelector.set(selector, rows);
    }
  }
}

// The wave registration is authoring input, not a second runtime projector.
// Expand each exact source once and share its family contracts with the main rows.
const waveBytes = await readFile(resolve(root, "atlas-data/motion/t66-wave1-registration.json"));
const waveRegistration = JSON.parse(waveBytes.toString("utf8"));
const intents = JSON.parse(await readFile(resolve(root, "atlas-data/motion/t66-motion-learning-intents.json"), "utf8"));
if (waveRegistration.schemaVersion !== "t66-wave1-source-motion-registration-v2"
  || waveRegistration.authority?.sourceOnly !== true || waveRegistration.authority?.publicRedistribution !== "held"
  || waveRegistration.authority?.humanReview !== "not_performed" || waveRegistration.authority?.canonicalTargetMembershipApproved !== false) {
  throw new Error("Wave motion registration cannot promote authority");
}
const wave1Actions = Object.fromEntries([...new Set(waveRegistration.selectors.map(row => row.sourceSubjectKey))].sort().map(sourceKey =>
  [sourceKey, projectT66Wave1MotionOptions(waveRegistration, sourceKey, null, intents.byActionId)
    .map(option => ({ ...option, candidate: safeCandidate(option.candidate) }))]));

const projected = {
  schemaVersion: "learner-motion-runtime-v1",
  wave1Actions,
  actions: Object.fromEntries([...actionsBySelector.entries()].sort(([a], [b]) => a.localeCompare(b))),
};

const forbiddenKey = /^(?:sources|sourceRefs|poseSourceRefs|evidence|evidenceState|geometryState|motionState|claimId|fieldEvidenceId|valueHash|evidenceHash|sourceHash|attribution|humanReview|publicRedistribution|sourceOnly|canonicalBindingCreated|reviewState|reviewStatus|humanReviewed|notes|accessedAt|locator|accessedOn)$/i;
const forbiddenText = /(?:https?:\/\/|\bT\d{2,3}[-:]|\bHA-[A-Z]-\d{6}\b|\bZA-c7010a9-[a-f0-9]{24}\b|cross_checked|single_source|needs_review|not_performed|evidenceHash|fieldEvidenceId|sourceHash|locator)/i;
function inspect(value, path = "$", key = "") {
  if (forbiddenKey.test(key)) throw new Error(`Internal provenance key in learner motion projection at ${path}.${key}`);
  if (Array.isArray(value)) return value.forEach((child, index) => inspect(child, `${path}[${index}]`, key));
  if (value && typeof value === "object") return Object.entries(value).forEach(([childKey, child]) => inspect(child, path, childKey));
  if (typeof value === "string" && forbiddenText.test(value)) throw new Error(`Internal provenance text in learner motion projection at ${path}`);
}
// Identity/buffer bindings are private control data consumed by the player, not rendered text.
// Inspect every learner-visible field; retain exact IDs in the separately validated candidate.
for (const rows of [...Object.values(projected.actions), ...Object.values(projected.wave1Actions)]) for (const row of rows) {
  inspect(row.label); inspect(row.text);
}

const output = serializeLearnerMotionRuntime(projected);
const deliveryPath = resolve(root, "atlas-data/motion/local-motion-delivery-index.json");
const delivered = new Map();
for (const row of [...bundle.motionAssets, ...waveRegistration.packages]) {
  if (delivered.has(row.uri) && delivered.get(row.uri).sha256 !== row.sha256) throw new Error("Conflicting motion delivery hashes");
  delivered.set(row.uri, { uri: row.uri, sha256: row.sha256 });
}
const deliveryOutput = JSON.stringify({ schemaVersion: "local-motion-delivery-index-v1", authority: waveRegistration.authority,
  dependencies: [
    { path: "atlas-data/motion/motion-learning.json", bytes: bundleBytes.length, sha256: createHash("sha256").update(bundleBytes).digest("hex") },
    { path: "atlas-data/motion/t66-wave1-registration.json", bytes: waveBytes.length, sha256: createHash("sha256").update(waveBytes).digest("hex") },
  ], entries: [...delivered.values()].sort((a, b) => a.uri.localeCompare(b.uri)) }, null, 2) + "\n";
if (checkOnly) {
  const existingDelivery = await readFile(deliveryPath, "utf8").catch(() => "");
  if (existingDelivery !== deliveryOutput) throw new Error("Local motion delivery index is stale; rebuild from validated motion content");
  const existing = await readFile(outputPath, "utf8").catch(() => "");
  if (existing !== output) throw new Error("Learner motion runtime is stale; rebuild from validated motion content");
  console.log(JSON.stringify({ status: "passed", selectors: Object.keys(projected.actions).length,
    actions: Object.values(projected.actions).reduce((count, rows) => count + rows.length, 0),
    playableSourceBoundCandidates: Object.values(projected.actions).flat().filter((row) => row.candidate).length }));
} else {
  await writeFile(outputPath, output);
  await writeFile(deliveryPath, deliveryOutput);
  console.log(JSON.stringify({ status: "built", selectors: Object.keys(projected.actions).length,
    actions: Object.values(projected.actions).reduce((count, rows) => count + rows.length, 0),
    playableSourceBoundCandidates: Object.values(projected.actions).flat().filter((row) => row.candidate).length }));
}
