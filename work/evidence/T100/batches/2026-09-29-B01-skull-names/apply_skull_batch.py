"""Apply one bounded Korean-name and exact taxonomy-crosswalk overlay to frozen ZA rows."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
HERE = Path(__file__).resolve().parent
LEDGER_PATH = HERE / "term-and-correspondence-ledger.json"
OVERLAY_PATH = ROOT / "atlas-data/overlays/za-local-integration.json"
SOURCE_PATH = ROOT / "work/evidence/T98/astra-resolution-2026-09-29/source-catalog.json"
TARGET_PATH = ROOT / "atlas-data/catalog/target-scope-t96.json"
SOURCE_META_PATH = ROOT / "work/evidence/T100/resolution-2026-09-29/source-metadata.json"
BASELINE_PATH = HERE / "start-baseline.json"


def read(path: Path):
    return json.loads(path.read_text())


def sha(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_source_term(name: str) -> str:
    return re.sub(r"\.(?:l|r)$", "", name, flags=re.IGNORECASE).strip().casefold()


def main():
    ledger = read(LEDGER_PATH)
    overlay = read(OVERLAY_PATH)
    source = read(SOURCE_PATH)
    target_scope = read(TARGET_PATH)
    source_meta = read(SOURCE_META_PATH)
    baseline = read(BASELINE_PATH)
    overlay_rel = "atlas-data/overlays/za-local-integration.json"
    if baseline["inputSha256"][overlay_rel] != sha(OVERLAY_PATH):
        raise SystemExit("current overlay is not the captured batch baseline")
    rows = {row["sourceKey"]: row for row in overlay["objects"]}
    source_rows = {row["sourceKey"]: row for row in source["objects"]}
    source_meta_rows = {row["name"]: row for row in source_meta["objects"]}
    targets = {row["id"]: row for row in target_scope["targets"]}
    sources = {row["id"]: row for row in ledger["sourceEvidence"]}
    term_ids = {row["kmleSourceId"] for row in ledger["targets"]}
    if len(ledger["targets"]) != 10 or len(term_ids) != 10:
        raise SystemExit("B01 must contain exactly ten unique target/name source records")
    if overlay["scope"] != {"targets": 542, "memberships": 563, "regions": 12}:
        raise SystemExit("frozen task denominator changed")
    if overlay["sourceHash"] != ledger["scope"]["zaSourceFileSha256"]:
        raise SystemExit("ZA source hash changed")
    if baseline["inputSha256"]["work/evidence/T98/astra-resolution-2026-09-29/source-catalog.json"] != sha(SOURCE_PATH):
        raise SystemExit("frozen source catalog changed since batch baseline")
    if baseline["inputSha256"]["atlas-data/catalog/target-scope-t96.json"] != sha(TARGET_PATH):
        raise SystemExit("frozen T96 target scope changed since batch baseline")

    seen_members = set()
    crosswalk = []
    for entry in ledger["targets"]:
        target = targets.get(entry["targetId"])
        if not target or target["semanticKind"] != "bone":
            raise SystemExit(f"unknown/non-bone frozen target: {entry['targetId']}")
        english = target["term"]["english"]
        latin = target["term"]["latin"]
        if english.casefold() != entry["sourceObjectNames"][0].split(".")[0].casefold():
            raise SystemExit(f"target/source term mismatch: {entry['targetId']}")
        if latin != entry["latin"]:
            raise SystemExit(f"TA2 Latin term mismatch: {entry['targetId']}")
        if entry["kmleSourceId"] not in sources:
            raise SystemExit(f"missing Korean term evidence: {entry['targetId']}")
        term_source = sources[entry["kmleSourceId"]]
        if term_source["term"].casefold() != english.casefold():
            raise SystemExit(f"Korean source/search term mismatch: {entry['targetId']}")
        if (term_source["koModern"], term_source["koTraditional"]) != (entry["koModern"], entry["koTraditional"]):
            raise SystemExit(f"Korean field evidence mismatch: {entry['targetId']}")
        for source_key in entry["sourceMembers"]:
            if source_key in seen_members:
                raise SystemExit(f"source member appears twice: {source_key}")
            seen_members.add(source_key)
            frozen = source_rows.get(source_key)
            row = rows.get(source_key)
            if not frozen or not row:
                raise SystemExit(f"frozen member or integration row missing: {source_key}")
            name = frozen["name"]
            meta = source_meta_rows.get(name)
            if not meta or row["sourceName"] != name or row["kind"] != "bone":
                raise SystemExit(f"source identity mismatch: {source_key}")
            if canonical_source_term(name) != english.casefold():
                raise SystemExit(f"not an exact direct source term match: {source_key}")
            if row["targetId"] != entry["targetId"] or entry["targetId"] not in row["targetIds"]:
                raise SystemExit(f"existing target candidate does not match batch: {source_key}")
            if meta["parent"] != frozen["parent"] or sorted(meta["collections"]) != frozen["collections"]:
                raise SystemExit(f"parent/collection identity mismatch: {source_key}")
            if row["side"] != frozen["sourceLabelSide"]:
                raise SystemExit(f"side provenance mismatch: {source_key}")
            if frozen["sourceLabelSide"] not in {None, "left", "right"}:
                raise SystemExit(f"invalid side state: {source_key}")
            source_suffix = ".l" if name.lower().endswith(".l") else ".r" if name.lower().endswith(".r") else None
            suffix_side = {".l": "left", ".r": "right"}.get(source_suffix)
            if suffix_side != frozen["sourceLabelSide"]:
                raise SystemExit(f"source suffix/side label disagreement: {source_key}")
            if row["haConceptId"] is not None or row["sourceOnly"] is not True:
                raise SystemExit(f"canonical learner binding/source-only state changed: {source_key}")
            if row["humanReview"] != "not_performed" or row["publicRedistribution"] != "held":
                raise SystemExit(f"review or public rights hold changed: {source_key}")

            english_source = "za-t99-frozen-source-objects"
            fipat_source = "fipat-ta2-t96-frozen-target-terms"
            row["label"] = entry["koModern"]
            row["names"]["koModern"] = entry["koModern"]
            row["names"]["koTraditional"] = entry["koTraditional"]
            row["aliases"] = sorted(set(row["aliases"] + [entry["latin"]]))
            row["nameSourceIds"] = sorted(set(row["nameSourceIds"] + [entry["kmleSourceId"], english_source, fipat_source]))
            row["nameEvidence"] = {
                "koModern": {"value": entry["koModern"], "sourceIds": [entry["kmleSourceId"]], "locator": term_source["locator"]},
                "koTraditional": {"value": entry["koTraditional"], "sourceIds": [entry["kmleSourceId"]], "locator": term_source["locator"]},
                "en": {
                    "value": row["names"]["en"],
                    "sourceIds": [english_source, fipat_source],
                    "locator": f"Exact source object {name}; sourceKey {source_key}; evaluated geometry SHA256 {frozen['evaluatedGeometrySha256']}; exact frozen target {entry['targetId']} English term {english}.",
                },
            }
            relation = {
                "targetId": entry["targetId"],
                "targetEnglish": english,
                "targetLatin": latin,
                "targetSemanticKind": target["semanticKind"],
                "targetPrimaryOwner": target["primaryOwner"],
                "targetRegionIds": target["regionIds"],
                "targetLaterality": target["sourceCardinality"]["lateralityState"],
                "sourceKey": source_key,
                "sourceObjectName": name,
                "sourceDataName": frozen["sourceLocator"].get("dataName", frozen.get("dataName")),
                "sourceParent": frozen["parent"],
                "sourceCollections": frozen["collections"],
                "sourceSide": frozen["sourceLabelSide"],
                "evaluatedGeometrySha256": frozen["evaluatedGeometrySha256"],
                "sourceHash": source["sourceHash"],
                "sourceRevision": source["sourceRevision"],
                "matchBasis": "exact source object base-name equals frozen target English term; only exact .l/.r source suffix is removed",
                "directObjectNameMatch": True,
                "ancestorNameAloneUsed": False,
                "upstreamFjOrTa2IdClaim": False,
                "canonicalHaBindingCreated": False,
                "humanReview": "not_performed",
            }
            row["targetRelationEvidence"] = [relation]
            crosswalk.append(relation)

    overlay["evidenceSources"] = ledger["sourceEvidence"]
    overlay["revision"] = "T100-source-taxonomy-local-display-v1-B01-skull-names"
    OVERLAY_PATH.write_text(json.dumps(overlay, ensure_ascii=False, indent=2) + "\n")
    out = {
        "schemaVersion": 1,
        "batchId": ledger["batchId"],
        "sourceCatalogSha256": sha(SOURCE_PATH),
        "targetScopeSha256": sha(TARGET_PATH),
        "sourceHash": source["sourceHash"],
        "overlaySha256": sha(OVERLAY_PATH),
        "targetCount": len(ledger["targets"]),
        "sourceObjectCount": len(seen_members),
        "relations": crosswalk,
        "unresolvedTargetsBeforeAndAfter": 182,
        "note": "These ten direct target relations were already inside the 360 source-taxonomy candidate count. The batch adds explicit per-object evidence and Korean name fields; it does not reduce the 182 unresolved target count or create canonical HA bindings.",
    }
    (HERE / "structure-correspondence.json").write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"overlaySha256": out["overlaySha256"], "targets": out["targetCount"], "sourceObjects": out["sourceObjectCount"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
