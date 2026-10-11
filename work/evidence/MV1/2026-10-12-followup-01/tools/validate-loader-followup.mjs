#!/usr/bin/env node
// Follow-up-safe copy of the shared MV1 loader audit; output only under this versioned run.
/** Execute the repository's real animation scene loader against every learner-reachable muscle asset contract. */
import { createHash } from "node:crypto";
import { readFile, writeFile, mkdir } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import runtime from "../../../../../atlas-web/src/data/learnerMotionRuntime.generated.ts";
import { loadAnimationScene } from "../../../../../atlas-web/src/viewer/animationSceneAdapter.ts";

const here = dirname(fileURLToPath(import.meta.url));
const root = resolve(here, "../../../../..");
const run = resolve(here, "..");
const output = resolve(run, "runtime/real-loader-validation.json");
const sha = (bytes) => createHash("sha256").update(bytes).digest("hex");
const all = [];
for (const collectionName of ["actions", "wave1Actions"]) {
  const collection = runtime[collectionName] ?? {};
  for (const [selector, rows] of Object.entries(collection)) {
    for (const option of rows) {
      const candidate = option.candidate;
      if (!candidate || (candidate.asset.sourceBinding?.subjectKind ?? "muscle") !== "muscle") continue;
      all.push({ collectionName, selector, option, candidate });
    }
  }
}
const bytesByFile = new Map();
const results = [];
for (let index = 0; index < all.length; index++) {
  const { collectionName, selector, option, candidate } = all[index];
  const asset = candidate.asset;
  const sourceKey = asset.sourceBinding?.subjectSourceKey ?? null;
  const targetId = collectionName + "|" + selector + "|" + asset.id + "|" + (sourceKey ?? "missing-subject");
  try {
    const fileKey = asset.uri + "|" + asset.sha256;
    let bytes = bytesByFile.get(fileKey);
    if (!bytes) {
      const loaded = await readFile(resolve(root, asset.uri));
      bytes = loaded.buffer.slice(loaded.byteOffset, loaded.byteOffset + loaded.byteLength);
      bytesByFile.set(fileKey, bytes);
    }
    const actualSha = sha(Buffer.from(bytes));
    if (actualSha !== asset.sha256) throw new Error("registered_asset_sha_mismatch:" + actualSha);
    const resource = await loadAnimationScene(bytes, asset);
    const result = { targetId, selector, optionId: option.actionKey ?? option.id ?? null, assetId: asset.id,
      sourceKey, side: asset.sourceBinding?.members?.find(row => row.sourceKey === sourceKey)?.side ?? null,
      uri: asset.uri, sha256: asset.sha256, clipId: asset.clip.id, status: "pass",
      representationType: asset.representationType, sourceNodeCount: resource.sourceNodes.size,
      rigNodeCount: resource.rigNodes.size, pathNodeCount: resource.pathNodes.size,
      skinnedMeshCount: resource.skinnedMeshCount, morphMeshCount: resource.morphMeshCount };
    resource.dispose();
    results.push(result);
  } catch (error) {
    results.push({ targetId, selector, assetId: asset.id, sourceKey, uri: asset.uri,
      sha256: asset.sha256, clipId: asset.clip?.id ?? null, status: "error", error: String(error?.stack ?? error) });
  }
  if ((index + 1) % 10 === 0) console.log(JSON.stringify({ checked: index + 1, total: all.length, pass: results.filter(r => r.status === "pass").length, error: results.filter(r => r.status === "error").length }));
}
const report = { capturedAt: new Date().toISOString(), validator: "atlas-web/src/viewer/animationSceneAdapter.ts#loadAnimationScene",
  scope: "all live learner-reachable source-bound muscle candidates from actions and wave1Actions",
  targets: all.length, uniqueGlbFiles: bytesByFile.size, pass: results.filter(r => r.status === "pass").length,
  error: results.filter(r => r.status === "error").length, results };
await mkdir(dirname(output), { recursive: true });
await writeFile(output, JSON.stringify(report, null, 2) + "\n");
console.log(JSON.stringify({ status: report.error ? "partial" : "pass", output, targets: report.targets,
  uniqueGlbFiles: report.uniqueGlbFiles, pass: report.pass, error: report.error }, null, 2));
