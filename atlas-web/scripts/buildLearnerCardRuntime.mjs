import { readFile, writeFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";
import { learnerStructureText } from "../src/domain/learnerStructureText.ts";
import { projectLearnerMotionActionOptions } from "../src/domain/motionLearning.ts";
import { learnerActionExplanation } from "../src/domain/learnerActionText.ts";
import { hasHanScript } from "../src/domain/search.ts";
import { projectSourceAttachments } from "../src/domain/sourceAttachments.ts";
import { createHash } from "node:crypto";

const scriptDir = dirname(fileURLToPath(import.meta.url));
const root = resolve(scriptDir, "../..");
const outputPath = resolve(root, "atlas-data/terminology/learner-card-runtime.json");
const contextOutputPath = resolve(root, "atlas-data/terminology/learner-attachment-context.json");
const checkOnly = process.argv.includes("--check");

async function load(relativePath) {
  return JSON.parse(await readFile(resolve(root, relativePath), "utf8"));
}

const [aiOverlay, legacySummaries, sourceContent, motionBundle, names, t65Attachments, t65NerveLearning, nerveSupport] = await Promise.all([
  load("atlas-data/terminology/ai-evidence-overlay.json"),
  load("atlas-data/terminology/learning-structure-summaries.json"),
  load("atlas-data/terminology/learner-structure-source-content.json"),
  load("atlas-data/motion/motion-learning.json"),
  load("atlas-data/terminology/learning-names.json"),
  load("atlas-data/terminology/muscle-attachment-content-t65.json"),
  load("atlas-data/terminology/nerve-learning-content-t65.json"),
  load("atlas-data/overlays/nerve-support-t63.json"),
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

const attachments = await load("atlas-data/terminology/muscle-attachment-content-t90.json");
const integrationBytes = await readFile(resolve(root, "atlas-data/overlays/za-local-integration.json"));
const integrationHash = createHash('sha256').update(integrationBytes).digest('hex');
if (integrationHash !== attachments.sourceOverlaySha256 || integrationHash !== t65Attachments.sourceOverlaySha256) throw Error('Attachment identity input changed; review before rebuilding');
const attachmentProjection = projectSourceAttachments(attachments, JSON.parse(integrationBytes).objects);
for (const [sourceKey, fields] of Object.entries(attachmentProjection.text)) {
  if (bySource[sourceKey]) throw Error('New attachment text must not override an existing field or conflict');
  bySource[sourceKey] = fields;
}

const reviewNotesPath = resolve(root, t65Attachments.reviewNotesPath ?? "");
const reviewNotesBytes = await readFile(reviewNotesPath);
const reviewNotesHash = createHash("sha256").update(reviewNotesBytes).digest("hex");
if (reviewNotesHash !== t65Attachments.reviewNotesSha256 || reviewNotesHash !== t65NerveLearning.reviewNotesSha256
  || t65NerveLearning.reviewNotesPath !== t65Attachments.reviewNotesPath
  || !t65Attachments.contract.sourceOnly || t65Attachments.contract.humanReview !== "not_performed"
  || t65Attachments.contract.publicRedistribution !== "held" || t65Attachments.contract.canonicalBindingsCreated !== 0
  || t65Attachments.contract.geometryCreated !== 0 || !t65NerveLearning.contract.sourceOnly
  || t65NerveLearning.contract.humanReview !== "not_performed" || t65NerveLearning.contract.publicRedistribution !== "held"
  || t65NerveLearning.contract.newGeometry !== 0 || t65NerveLearning.contract.canonicalBindingsCreated !== 0
  || t65Attachments.sources.some((source) => source.reviewNotesPath !== t65Attachments.reviewNotesPath || source.reviewNotesSha256 !== reviewNotesHash)
  || t65NerveLearning.sources.some((source) => source.originalHtmlSha256 !== null || source.originalHtmlRetrieved !== false
    || source.accessMethod !== "web_reader_opened_fulltext")) throw Error("T65 opened-source review record integrity");
const t65SourceIds = new Set(t65Attachments.sources.map((source) => source.id));
for (const record of t65Attachments.records) for (const field of ["origin", "insertion"]) {
  const value = record[field]; const proof = record.fieldEvidence[field];
  if (proof.sourceIds.some((id) => !t65SourceIds.has(id)) || createHash("sha256").update(value).digest("hex") !== proof.learnerValueSha256
    || proof.reviewNotesSha256 !== reviewNotesHash || !proof.locator) throw Error(`T65 attachment field evidence invalid: ${record.sourceName}/${field}`);
}
const t65AttachmentProjection = projectSourceAttachments(t65Attachments, JSON.parse(integrationBytes).objects, { verifiedWebReaderSourceIds: t65SourceIds });
for (const [sourceKey, fields] of Object.entries(t65AttachmentProjection.text)) {
  if (bySource[sourceKey]) throw Error("T65 attachment must not override an existing field or conflict");
  bySource[sourceKey] = fields;
}
for (const [sourceKey, roles] of Object.entries(t65AttachmentProjection.contexts)) {
  if (attachmentProjection.contexts[sourceKey]) throw Error("T65 attachment context overlaps T90 source scope");
  attachmentProjection.contexts[sourceKey] = roles;
}

const verifiedNerveNames = [...new Set(nerveSupport.instances.filter((row) => row.localSelection === "verified_geometry").map((row) => row.names.en))]
  .filter((name) => ["Common fibular nerve", "Deep fibular nerve", "Superficial fibular nerve"].includes(name));
for (const name of verifiedNerveNames) {
  const sides = new Set(nerveSupport.instances.filter((row) => row.localSelection === "verified_geometry" && row.names.en === name).map((row) => row.side));
  if (sides.size !== 2 || !sides.has("left") || !sides.has("right")) throw Error(`T65 nerve support side mismatch: ${name}`);
}
const nerveLearning = {};
for (const row of t65NerveLearning.records) {
  if (!verifiedNerveNames.includes(row.nerveName) || nerveLearning[row.nerveName]) throw Error(`T65 unsupported/duplicate nerve summary: ${row.nerveName}`);
  for (const field of ["courseContext", "compressionContext", "functionContext"]) {
    const text = row[field]; const evidence = row.fieldEvidence[field];
    if (typeof text !== "string" || !text.trim() || createHash("sha256").update(text).digest("hex") !== evidence.learnerValueSha256
      || !evidence.sourceIds.length || evidence.sourceIds.some((id) => !t65NerveLearning.sources.some((source) => source.id === id
        && source.reviewNotesPath === t65NerveLearning.reviewNotesPath && source.accessMethod === "web_reader_opened_fulltext"))) {
      throw Error(`T65 nerve summary provenance invalid: ${row.nerveName}/${field}`);
    }
    if (evidence.reviewNotesSha256 !== reviewNotesHash) throw Error(`T65 nerve source review hash mismatch: ${row.nerveName}/${field}`);
  }
  nerveLearning[row.nerveName] = { courseContext: row.courseContext, compressionContext: row.compressionContext, functionContext: row.functionContext };
}
if (Object.keys(nerveLearning).length !== verifiedNerveNames.length) throw Error("T65 nerve learning coverage does not match the three supported fibular nerve concepts");

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
  nerveLearning,
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
  const learnerTextKeys = new Set(["label", "korean", "english", "aliases", "explanation", "origin", "insertion", "courseContext", "compressionContext", "functionContext"]);
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
  if (Object.keys(value).sort().join(",") !== "actions,names,nerveLearning,schemaVersion,structure") throw new Error("Unexpected top-level learner projection fields");
  if (Object.keys(value.structure).sort().join(",") !== "byConcept,bySource") throw new Error("Unexpected structure projection fields");
  for (const [name, row] of Object.entries(value.nerveLearning)) {
    if (!["Common fibular nerve", "Deep fibular nerve", "Superficial fibular nerve"].includes(name)
      || Object.keys(row).sort().join(",") !== "compressionContext,courseContext,functionContext") throw new Error(`Invalid learner nerve content at ${name}`);
  }
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
const contextBytes = `${JSON.stringify(attachmentProjection.contexts, null, 2)}\n`;
if (checkOnly) {
  const existing = await readFile(outputPath, "utf8").catch(() => null);
  const existingContexts = await readFile(contextOutputPath, "utf8").catch(() => null);
  if (existing !== bytes || existingContexts !== contextBytes) {
    console.error("Learner card runtime is stale; regenerate with node --experimental-strip-types scripts/buildLearnerCardRuntime.mjs");
    process.exitCode = 1;
  } else {
    console.log(JSON.stringify({ status: "passed", conceptRows: Object.keys(byConcept).length, sourceRows: Object.keys(bySource).length, actionRows: actions.length }));
  }
} else {
  await writeFile(outputPath, bytes);
  await writeFile(contextOutputPath, contextBytes);
  console.log(JSON.stringify({ status: "built", conceptRows: Object.keys(byConcept).length, sourceRows: Object.keys(bySource).length, actionRows: actions.length }));
}
