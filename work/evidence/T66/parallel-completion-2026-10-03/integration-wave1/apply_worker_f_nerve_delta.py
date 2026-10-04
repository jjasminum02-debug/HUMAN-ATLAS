#!/usr/bin/env python3
"""Apply only the worker-F field-backed learner text delta to existing nerve cards."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
WAVE = ROOT / "work/evidence/T66/parallel-completion-2026-10-03/wave-1/workers/F"
OUT = ROOT / "work/evidence/T66/parallel-completion-2026-10-03/integration-wave1"
DELTA_PATH = WAVE / "learner-card-delta.json"
SOURCES_PATH = WAVE / "field-evidence-sources.json"
TARGET_PATH = ROOT / "atlas-data/terminology/nerve-learning-t66.json"
RECEIPT_PATH = OUT / "nerve-card-delta-receipt.json"

def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

def sha_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()

if RECEIPT_PATH.exists():
    raise SystemExit(f"refusing to overwrite existing integration receipt: {RECEIPT_PATH}")

delta = load(DELTA_PATH)
source_catalog = load(SOURCES_PATH)
cards = load(TARGET_PATH)
source_by_id = source_catalog["sources"]
changed = []
excluded = []

for row in delta["candidateCards"]:
    candidate = row["candidateRecord"]
    nerve_name = candidate.get("nerveName")
    if not isinstance(nerve_name, str) or "group context" in nerve_name.lower() or "no new canonical id" in nerve_name.lower():
        excluded.append({"candidate": nerve_name, "reason": "group context is not a new learner nerve concept/card"})
        continue
    current = cards.get(nerve_name)
    if current is None:
        excluded.append({"candidate": nerve_name, "reason": "no exact existing learner card key; no alias/card created"})
        continue
    for field in ("courseContext", "compressionContext", "variationContext", "functionContext"):
        value = candidate.get(field)
        proof = candidate.get("fieldEvidence", {}).get(field)
        if value is None or proof is None:
            continue
        actual_value_hash = sha_text(value)
        if proof.get("learnerValueSha256") != actual_value_hash:
            raise ValueError(f"candidate value hash mismatch: {nerve_name}.{field}")
        source_ids = proof.get("sourceIds", [])
        if not source_ids or any(source_id not in source_by_id for source_id in source_ids):
            raise ValueError(f"field evidence references missing source rows: {nerve_name}.{field}")
        access = [source_by_id[source_id].get("accessMethod", "unknown") for source_id in source_ids]
        if any(not method for method in access):
            raise ValueError(f"field evidence has no recorded access method: {nerve_name}.{field}")
        # Variation text is explicitly evidence-only in this worker package and lacks field-level proof.
        if field == "variationContext":
            excluded.append({"candidate": nerve_name, "field": field, "reason": "variation is evidence-only; no field claim proof"})
            continue
        prior_value = current.get(field)
        changed.append({
            "nerveName": nerve_name,
            "field": field,
            "priorValueSha256": sha_text(prior_value) if isinstance(prior_value, str) else None,
            "learnerValueSha256": actual_value_hash,
            "sourceIds": source_ids,
            "locators": proof.get("locator"),
            "accessMethods": access,
            "accessedOn": [source_by_id[source_id].get("accessedOn") for source_id in source_ids],
            "valueDisposition": "direct_field_delta" if all(method == "opened_primary_fulltext" for method in access)
                else "field_delta_with_frozen_prior_opened_source_or_scope_note",
        })
        current[field] = value

# Axillary compression was not field-supported by this worker and remains unchanged.
for name in ("Dorsal scapular nerve", "Median nerve", "Lateral femoral cutaneous nerve", "Axillary nerve"):
    if name not in cards:
        raise ValueError(f"required exact learner card key missing: {name}")

TARGET_PATH.write_text(json.dumps(cards, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
receipt = {
    "schemaVersion": "t66-wave1-nerve-card-integration-v1",
    "runId": delta["runId"],
    "workerFDeltaSha256": hashlib.sha256(DELTA_PATH.read_bytes()).hexdigest(),
    "workerFSourceCatalogSha256": hashlib.sha256(SOURCES_PATH.read_bytes()).hexdigest(),
    "learnerTargetPath": str(TARGET_PATH.relative_to(ROOT)),
    "learnerTargetSha256": hashlib.sha256(TARGET_PATH.read_bytes()).hexdigest(),
    "appliedFieldCount": len(changed),
    "appliedFields": changed,
    "excludedOrUnchanged": excluded + [{"candidate": "Axillary nerve", "field": "compressionContext", "reason": "F supplied course field only; preserve existing compression context"}],
    "authority": {"sourceOnly": True, "publicRedistribution": "held", "humanReview": "not_performed",
        "sourceInstanceOrSideCreated": False, "newAnatomicalNerveIdentityCreated": False,
        "newNerveGeometryOrCoordinatesCreated": False},
}
RECEIPT_PATH.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"appliedFieldCount": len(changed), "applied": [{"nerveName": row["nerveName"], "field": row["field"]} for row in changed],
    "excluded": excluded, "receipt": str(RECEIPT_PATH.relative_to(ROOT)), "targetSha256": receipt["learnerTargetSha256"]}, ensure_ascii=False, indent=2))
