import { readFile, writeFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";
import { learnerStructureText } from "../src/domain/learnerStructureText.ts";
import { projectLearnerMotionActionOptions } from "../src/domain/motionLearning.ts";
import { learnerActionExplanation } from "../src/domain/learnerActionText.ts";
import { hasHanScript } from "../src/domain/search.ts";

const scriptDir = dirname(fileURLToPath(import.meta.url));
const root = resolve(scriptDir, "../..");
const outputPath = resolve(root, "atlas-data/terminology/learner-card-runtime.json");
const checkOnly = process.argv.includes("--check");

async function load(relativePath) {
  return JSON.parse(await readFile(resolve(root, relativePath), "utf8"));
}

const [aiOverlay, legacySummaries, sourceContent, motionBundle, names] = await Promise.all([
  load("atlas-data/terminology/ai-evidence-overlay.json"),
  load("atlas-data/terminology/learning-structure-summaries.json"),
  load("atlas-data/terminology/learner-structure-source-content.json"),
  load("atlas-data/motion/motion-learning.json"),
  load("atlas-data/terminology/learning-names.json"),
]);

const aiBySubjectField = new Map(aiOverlay.items.map((row) => [`${row.subjectId}\u0000${row.field}`, row]));
const legacyBySubjectField = new Map(legacySummaries.map((row) => [`${row.conceptId}\u0000${row.role}`, row]));
const projectField = (subjectId, field) => learnerStructureText(
  aiBySubjectField.get(`${subjectId}\u0000${field}`),
  legacyBySubjectField.get(`${subjectId}\u0000${field}`),
);

const conceptIds = [...new Set([
  ...aiOverlay.items.map((row) => row.subjectId),
  ...legacySummaries.map((row) => row.conceptId),
  ...sourceContent.records.map((row) => row.subjectId).filter(Boolean),
])].sort();
const byConcept = {};
for (const conceptId of conceptIds) {
  const fields = {};
  for (const field of ["origin", "insertion"]) {
    const text = projectField(conceptId, field);
    if (typeof text === "string" && text.trim()) fields[field] = text;
  }
  if (Object.keys(fields).length) byConcept[conceptId] = fields;
}

const bySource = {};
for (const row of sourceContent.records) {
  if (!row.subjectId) continue;
  const fields = {};
  for (const field of ["origin", "insertion"]) {
    const status = row.fieldDisposition?.[field]?.status;
    if (status !== "claim_available" && status !== "conflicted_not_asserted") continue;
    const text = projectField(row.subjectId, field);
    if (typeof text === "string" && text.trim()) fields[field] = text;
  }
  if (!Object.keys(fields).length) continue;
  for (const sourceKey of row.sourceKeys) bySource[sourceKey] = fields;
}

const actionConceptIds = [...new Set(motionBundle.muscleActions.flatMap((row) => row.subjectIds))].sort();
const actions = [];
let optionIndex = 0;
for (const conceptId of actionConceptIds) {
  const options = projectLearnerMotionActionOptions(conceptId, motionBundle, aiOverlay.items);
  for (const option of options) {
    actions.push({
      conceptId,
      key: `option-${String(optionIndex++).padStart(3, "0")}`,
      label: option.text.label,
      explanation: learnerActionExplanation(option.text.explanation),
      sideApplicability: option.sideApplicability === "left" || option.sideApplicability === "right"
        ? option.sideApplicability
        : null,
    });
  }
}

const projected = {
  schemaVersion: "learner-card-runtime-v1",
  names: names.entries.map((row) => ({
    id: row.id,
    label: row.label,
    korean: row.korean,
    english: row.english,
    aliases: (row.aliases ?? []).filter((value) => typeof value === "string" && !hasHanScript(value)),
    parentId: row.parentId,
    entityType: row.entityType,
    lookupOnly: row.lookupOnly,
  })),
  structure: { byConcept, bySource },
  actions,
};

function assertSafeProjection(value) {
  const deniedKeys = new Set([
    "sources", "evidence", "evidenceState", "geometryState", "motionState", "claimId",
    "fieldEvidenceId", "valueHash", "evidenceHash", "sourceHash", "attribution", "url",
    "locator", "accessedOn", "humanReview", "publicRedistribution", "sourceOnly",
    "canonicalBindingCreated", "reviewState", "reviewStatus", "sourceIds", "status",
    "humanReviewed", "hanja", "hanjaNote", "notes", "accessedAt",
  ]);
  const learnerTextKeys = new Set(["label", "korean", "english", "aliases", "explanation", "origin", "insertion"]);
  const forbiddenLearnerText = /(?:https?:\/\/|\bT\d{2,3}[-:]|\bHA-[A-Z]-\d{6}\b|\bZA-c7010a9-[a-f0-9]{24}\b|cross_checked|single_source|needs_review|not_performed|evidenceHash|fieldEvidenceId|sourceHash|locator)/i;
  const visit = (item, path = "$", textValue = false) => {
    if (Array.isArray(item)) return item.forEach((child, index) => visit(child, `${path}[${index}]`, textValue));
    if (item && typeof item === "object") {
      for (const [key, child] of Object.entries(item)) {
        if (deniedKeys.has(key)) throw new Error(`Unsafe learner projection key at ${path}.${key}`);
        visit(child, `${path}.${key}`, learnerTextKeys.has(key));
      }
      return;
    }
    if (textValue && typeof item === "string" && forbiddenLearnerText.test(item)) {
      throw new Error(`Internal evidence text entered learner projection at ${path}`);
    }
  };
  visit(value);
  if (Object.keys(value).sort().join(",") !== "actions,names,schemaVersion,structure") throw new Error("Unexpected top-level learner projection fields");
  if (Object.keys(value.structure).sort().join(",") !== "byConcept,bySource") throw new Error("Unexpected structure projection fields");
  for (const row of value.names) {
    if (Object.keys(row).sort().join(",") !== "aliases,english,entityType,id,korean,label,lookupOnly,parentId") throw new Error(`Unexpected learner name fields at ${row.id}`);
    if (!/^(?:HA-[A-Z]-\d{6}|LOOKUP-[A-Z0-9-]+)$/.test(row.id)) throw new Error(`Invalid learner name key ${row.id}`);
    for (const text of [row.label, row.korean, row.english, ...row.aliases]) {
      if (typeof text === "string" && hasHanScript(text)) throw new Error(`Hanja must not enter the learner name projection for ${row.id}`);
    }
  }
  for (const [key, row] of Object.entries(value.structure.byConcept)) {
    if (!/^HA-[A-Z]-\d{6}$/.test(key) || Object.keys(row).some((field) => !["origin", "insertion"].includes(field))) throw new Error(`Invalid concept projection ${key}`);
  }
  for (const [key, row] of Object.entries(value.structure.bySource)) {
    if (!/^ZA-[a-z0-9]+-[a-f0-9]{24}$/.test(key) || Object.keys(row).some((field) => !["origin", "insertion"].includes(field))) throw new Error(`Invalid source projection ${key}`);
  }
  for (const row of value.actions) {
    if (Object.keys(row).sort().join(",") !== "conceptId,explanation,key,label,sideApplicability") throw new Error(`Unexpected action projection fields at ${row.key}`);
    if (!/^HA-[A-Z]-\d{6}$/.test(row.conceptId) || !/^option-\d{3}$/.test(row.key)) throw new Error(`Invalid learner action key at ${row.key}`);
    if (row.sideApplicability !== null && row.sideApplicability !== "left" && row.sideApplicability !== "right") throw new Error(`Invalid action side applicability at ${row.key}`);
    for (const text of [row.label, row.explanation]) {
      if (typeof text !== "string" || hasHanScript(text)) throw new Error(`Learner action text must be Hangul/Latin only at ${row.key}`);
    }
  }
}

assertSafeProjection(projected);
const bytes = `${JSON.stringify(projected, null, 2)}\n`;
if (checkOnly) {
  const existing = await readFile(outputPath, "utf8").catch(() => null);
  if (existing !== bytes) {
    console.error("Learner card runtime is stale; regenerate with node --experimental-strip-types scripts/buildLearnerCardRuntime.mjs");
    process.exitCode = 1;
  } else {
    console.log(JSON.stringify({ status: "passed", conceptRows: Object.keys(byConcept).length, sourceRows: Object.keys(bySource).length, actionRows: actions.length }));
  }
} else {
  await writeFile(outputPath, bytes);
  console.log(JSON.stringify({ status: "built", conceptRows: Object.keys(byConcept).length, sourceRows: Object.keys(bySource).length, actionRows: actions.length }));
}
