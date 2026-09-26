import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import test from "node:test";
import { attachmentCrosscheckFor } from "./attachmentCrosschecks.ts";

const summaries = JSON.parse(readFileSync(new URL("../../../atlas-data/terminology/learning-structure-summaries.json", import.meta.url), "utf8")) as Array<{
  conceptId: string;
  role: "origin" | "insertion";
  summary: string;
}>;
const payload = JSON.parse(readFileSync(new URL("../../../atlas-data/terminology/learning-attachment-crosschecks.json", import.meta.url), "utf8")) as {
  humanAnatomyReview: string;
  items: Array<{ conceptId: string; role: string; sourceIds: string[]; comparison: string; displayedSummarySha256: string }>;
  sources: Array<{ id: string; url: string; edition: string; locator: string; accessDate: string; accessMethod: string; textAccess: string }>;
};

test("each displayed pilot origin/insertion sentence has exact modern-source comparison and locator", () => {
  assert.equal(payload.items.length, summaries.length);
  const keys = new Set<string>();
  for (const summary of summaries) {
    const key = `${summary.conceptId}:${summary.role}`;
    assert.equal(keys.has(key), false, `duplicate comparison ${key}`);
    keys.add(key);
    const result = attachmentCrosscheckFor(summary.conceptId, summary.role);
    assert.ok(result, `missing comparison for ${key}`);
    assert.ok(result.item.comparison.length > 35, `empty comparison for ${key}`);
    assert.ok(result.sources.length > 0, `missing source link for ${key}`);
    for (const source of result.sources) {
      assert.match(source.url, /^https:\/\//);
      assert.ok(source.edition);
      assert.ok(source.locator);
      assert.match(source.accessDate, /^2026-09-26$/);
      assert.ok(source.accessMethod);
    }
    const summaryHash = createHash("sha256").update(summary.summary, "utf8").digest("hex");
    const boundItem = payload.items.find((row) => row.conceptId === summary.conceptId && row.role === summary.role);
    assert.equal(boundItem?.displayedSummarySha256, summaryHash, `stale displayed sentence binding for ${key}`);
  }
  assert.equal(payload.humanAnatomyReview, "not_performed");
});

test("comparison sources resolve and record access limitations instead of implying full-text review", () => {
  const sourceIds = new Set(payload.sources.map((source) => source.id));
  for (const item of payload.items) {
    for (const sourceId of item.sourceIds) assert.ok(sourceIds.has(sourceId), `missing source ${sourceId}`);
  }
  assert.ok(payload.sources.some((source) => source.accessMethod.includes("HTTP 429")));
  assert.ok(payload.sources.some((source) => source.textAccess === "abstract_only_full_text_not_opened"));
  assert.ok(payload.sources.some((source) => source.textAccess === "abstract_opened_full_text_not_opened"));
});
