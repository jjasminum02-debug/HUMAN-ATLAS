import { readFile, writeFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";
import { projectLearnerActionText, projectLearnerMotionActionOptions } from "../src/domain/motionLearning.ts";

const scriptDir = dirname(fileURLToPath(import.meta.url));
const root = resolve(scriptDir, "../..");
const inputPath = resolve(root, "atlas-data/motion/motion-learning.json");
const cardRuntimePath = resolve(root, "atlas-data/terminology/learner-card-runtime.json");
const outputPath = resolve(scriptDir, "../src/data/learnerMotionRuntime.generated.ts");
const checkOnly = process.argv.includes("--check");

const bundle = JSON.parse(await readFile(inputPath, "utf8"));
const cardRuntime = JSON.parse(await readFile(cardRuntimePath, "utf8"));

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
    const options = projectLearnerMotionActionOptions(selector, bundle, [], null)
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

const projected = {
  schemaVersion: "learner-motion-runtime-v1",
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
inspect(projected);

const output = `const learnerMotionRuntime = ${JSON.stringify(projected, null, 2)} as const;\n\nexport default learnerMotionRuntime;\n`;
if (checkOnly) {
  const existing = await readFile(outputPath, "utf8").catch(() => "");
  if (existing !== output) throw new Error("Learner motion runtime is stale; rebuild from validated motion content");
  console.log(JSON.stringify({ status: "passed", selectors: Object.keys(projected.actions).length,
    actions: Object.values(projected.actions).reduce((count, rows) => count + rows.length, 0),
    playableSourceBoundCandidates: Object.values(projected.actions).flat().filter((row) => row.candidate).length }));
} else {
  await writeFile(outputPath, output);
  console.log(JSON.stringify({ status: "built", selectors: Object.keys(projected.actions).length,
    actions: Object.values(projected.actions).reduce((count, rows) => count + rows.length, 0),
    playableSourceBoundCandidates: Object.values(projected.actions).flat().filter((row) => row.candidate).length }));
}
