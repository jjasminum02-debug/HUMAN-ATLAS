import { createHash } from "node:crypto";
import { readFile, readdir, stat, writeFile } from "node:fs/promises";
import { dirname, resolve, relative } from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = dirname(fileURLToPath(import.meta.url));
const projectRoot = resolve(scriptDir, "../..");
const webRoot = resolve(projectRoot, "atlas-web");
const bundleRoot = resolve(webRoot, "dist");
const runtimePath = resolve(projectRoot, "atlas-data/terminology/learner-card-runtime.json");
const evidenceRoot = resolve(projectRoot, "work/evidence/T82");
const baselinePath = resolve(evidenceRoot, "baseline.json");
const aiOverlayPath = resolve(projectRoot, "atlas-data/terminology/ai-evidence-overlay.json");
const workbookDispositionPath = resolve(projectRoot, "work/evidence/T81/workbook-row-dispositions.json");

const argv = process.argv.slice(2);
const reportArgument = argv.find((arg) => arg.startsWith("--report="));
const reportPath = reportArgument ? resolve(projectRoot, reportArgument.slice("--report=".length)) : null;

async function readJson(path) {
  return JSON.parse(await readFile(path, "utf8"));
}

async function walk(path) {
  const results = [];
  for (const entry of await readdir(path, { withFileTypes: true })) {
    const absolute = resolve(path, entry.name);
    if (entry.isDirectory()) results.push(...await walk(absolute));
    else if (entry.isFile()) results.push(absolute);
  }
  return results;
}

function sha256(bytes) {
  return createHash("sha256").update(bytes).digest("hex");
}

function collectProvenanceStrings(value, key = "", parentKey = "", result = new Set()) {
  if (Array.isArray(value)) {
    for (const child of value) collectProvenanceStrings(child, key, parentKey, result);
    return result;
  }
  if (value && typeof value === "object") {
    for (const [childKey, child] of Object.entries(value)) collectProvenanceStrings(child, childKey, key, result);
    return result;
  }
  if (typeof value !== "string") return result;

  const isSourceReference = parentKey === "sources" || parentKey === "claims";
  const keyIsProvenance = /^(?:id|underlyingWorkId|evidenceIds|valueHash|evidenceHash|sourceHash|url|locator|title|attribution)$/i.test(key);
  const valueLooksInternal = /^(?:T18[-:]|WORK-)/i.test(value)
    || /^[a-f0-9]{64}$/i.test(value)
    || /^https?:\/\//i.test(value);
  if (value.length >= 6 && ((isSourceReference && keyIsProvenance) || valueLooksInternal)) result.add(value);
  return result;
}

const [runtime, baseline, aiOverlay, workbookDisposition] = await Promise.all([
  readJson(runtimePath),
  readJson(baselinePath),
  readJson(aiOverlayPath),
  readJson(workbookDispositionPath),
]);
const learnerText = new Set();
for (const row of runtime.names) {
  for (const key of ["label", "korean", "english"]) if (row[key]) learnerText.add(row[key]);
  for (const alias of row.aliases) learnerText.add(alias);
}
for (const row of Object.values(runtime.structure.byConcept)) for (const text of Object.values(row)) learnerText.add(text);
for (const row of Object.values(runtime.structure.bySource)) for (const text of Object.values(row)) learnerText.add(text);
for (const row of runtime.actions) {
  learnerText.add(row.label);
  learnerText.add(row.explanation);
}

const staticMarkers = [
  "T18-FIELD-", "T18-E-", "T18-C-", "T18-HANDS-ON-ANATOMY", "T18-STATPEARLS",
  "WORK-HANDS-ON-ANATOMY", "WORK-STATPEARLS", "Hands-on Anatomy, 2024 publication",
  "Card RK, Bordoni B.", "ai_source_summary", "ai_source_summary_translation",
];
const provenanceMarkers = new Set([...collectProvenanceStrings(aiOverlay), ...staticMarkers]);
for (const text of learnerText) provenanceMarkers.delete(text);

const scanFiles = (await walk(bundleRoot)).filter((path) => /\.(?:js|html|css|json)$/i.test(path));
const bundles = [];
const leaks = [];
for (const path of scanFiles) {
  const bytes = await readFile(path);
  const text = bytes.toString("utf8");
  const matchingMarkers = [];
  for (const marker of provenanceMarkers) {
    if (marker.length >= 6 && text.includes(marker)) matchingMarkers.push(marker);
  }
  if (matchingMarkers.length) leaks.push({ path: relative(projectRoot, path), markerCount: matchingMarkers.length, markers: matchingMarkers.slice(0, 12) });
  if (path.endsWith(".js")) bundles.push({ path: relative(projectRoot, path), bytes: bytes.length, sha256: sha256(bytes) });
}

const result = {
  schemaVersion: "t82-learner-distribution-audit-v1",
  status: leaks.length ? "failed" : "passed",
  scope: "compiled learner distribution; development evidence remains in source files and is not copied to learner JS/HTML/CSS/JSON",
  checkedAt: new Date().toISOString(),
  inputs: {
    learnerRuntimeSha256: sha256(await readFile(runtimePath)),
    aiEvidenceOverlaySha256: sha256(await readFile(aiOverlayPath)),
    t81WorkbookDispositionSha256: sha256(await readFile(workbookDispositionPath)),
    t81PrivateWorkbookRows: workbookDisposition.rowsProcessed,
    t81PrivateWorkbookHashReference: workbookDisposition.source?.sha256 ?? null,
  },
  priorBundle: baseline.preFixLearnerBundleEvidenceStrings?.[0] ?? null,
  learnerRuntimeRows: {
    names: runtime.names.length,
    conceptStructureRows: Object.keys(runtime.structure.byConcept).length,
    sourceStructureRows: Object.keys(runtime.structure.bySource).length,
    actions: runtime.actions.length,
  },
  distribution: { scannedFiles: scanFiles.length, bundles },
  provenanceMarkersChecked: provenanceMarkers.size,
  leaks,
  limitations: [
    "The private workbook bytes were not reopened or copied; only the existing T81 disposition/hash record was checked.",
    "This validates absence of development provenance markers from compiled learner assets, not public redistribution permission or human review.",
  ],
};

if (reportPath) await writeFile(reportPath, `${JSON.stringify(result, null, 2)}\n`);
console.log(JSON.stringify(result));
if (leaks.length) process.exitCode = 1;
