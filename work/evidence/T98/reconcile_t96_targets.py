#!/usr/bin/env python3
"""Freeze a conservative 12-region reconciliation against T96 and T97 names."""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
SCOPE_PATH = ROOT / "atlas-data/catalog/target-scope-t96.json"
T97_PATH = ROOT / "work/evidence/T97/blender-object-inventory.json"
TARGET_PACKAGES = ROOT / "atlas-data/manifests/region-target-packages-t96"
GENERIC = {"musculus", "muscle", "muscles", "bone", "bones", "os", "ossa", "the", "of", "and", "part", "parts", "group", "complex", "series", "right", "left"}


def file_hash(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def norm(value: str) -> str:
    value = unicodedata.normalize("NFKD", value.casefold())
    value = "".join(c for c in value if not unicodedata.combining(c))
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return " ".join(value.split())


def source_name_core(name: str) -> tuple[str, set[str]]:
    # Blender dot suffixes include .l/.r/.el/.er/.ol/.or and group/helper
    # codes. Strip only the final serialized code from this candidate index;
    # never reinterpret it as anatomy side or part.
    base = re.sub(r"\.(?:e\d*[lr]?|o[lr]?|[lr]|g|j|t|s|i)$", "", name, flags=re.I)
    phrase = norm(base)
    return phrase, {token for token in phrase.split() if token not in GENERIC}


def target_terms(target: dict) -> list[str]:
    term = target.get("term", {})
    values = [term.get("english"), term.get("latin")]
    synonyms = term.get("sourceSynonyms", {})
    if isinstance(synonyms, dict):
        for group in synonyms.values():
            if isinstance(group, list):
                values.extend(group)
    return sorted({norm(v) for v in values if isinstance(v, str) and norm(v)})


def main():
    scope = json.loads(SCOPE_PATH.read_text(encoding="utf-8"))
    t97 = json.loads(T97_PATH.read_text(encoding="utf-8"))
    scope_targets = scope["targets"]
    object_names = t97["dataBlockNames"]["Object"]
    source_rows = [(name, *source_name_core(name)) for name in object_names]
    source_names_hash = hashlib.sha256("\n".join(sorted(object_names)).encode()).hexdigest()

    package_rows = []
    memberships = defaultdict(set)
    package_input_hashes = {}
    for target in scope_targets:
        for region_id in target.get("regionIds", []):
            memberships[target["id"]].add(region_id)
    for region in scope["regions"]:
        package_path = ROOT / region["packagePath"]
        package = json.loads(package_path.read_text(encoding="utf-8"))
        package_input_hashes[region["packagePath"]] = file_hash(package_path)
        if package.get("regionId") != region["regionId"]:
            raise SystemExit(f"region/package mismatch: {region['regionId']}")
        package_ids = package.get("targetIds", [])
        if len(package_ids) != region["primaryTargetCount"]:
            raise SystemExit(f"primary target count mismatch in {region['taskId']}")
        expected_primary = {target["id"] for target in scope_targets if target["primaryOwner"] == region["regionId"]}
        if set(package_ids) != expected_primary:
            raise SystemExit(f"package primary owner IDs mismatch in {region['taskId']}")
        membership_count = sum(region["regionId"] in target.get("regionIds", []) for target in scope_targets)
        if membership_count != region["regionMembershipCount"]:
            raise SystemExit(f"scope membership count mismatch in {region['taskId']}")
        package_rows.append({
            "taskId": region["taskId"], "regionId": region["regionId"],
            "labelKo": region["labelKo"], "labelEn": region["labelEn"],
            "primaryTargetCount": region["primaryTargetCount"],
            "regionMembershipCount": region["regionMembershipCount"],
            "packagePath": region["packagePath"],
            "packageSha256": package_input_hashes[region["packagePath"]],
        })

    scope_by_id = {target["id"]: target for target in scope_targets}
    missing = sorted(set(scope_by_id) - set(memberships))
    extra = sorted(set(memberships) - set(scope_by_id))
    owner_counts = Counter(t["primaryOwner"] for t in scope_targets)
    if missing or extra or len(scope_by_id) != 542 or sum(len(v) for v in memberships.values()) != 563:
        raise SystemExit(f"frozen scope/package reconciliation failed: missing={len(missing)} extra={len(extra)} targets={len(scope_by_id)} memberships={sum(len(v) for v in memberships.values())}")

    rows = []
    for target in scope_targets:
        term_values = target_terms(target)
        core_values = [{t for t in value.split() if t not in GENERIC} for value in term_values]
        candidate_hits = []
        for source_name, source_phrase, source_tokens in source_rows:
            if not source_phrase:
                continue
            matched = []
            for term, core in zip(term_values, core_values):
                if not core:
                    continue
                if term and (term in source_phrase or (len(source_tokens) >= 2 and source_phrase in term)):
                    matched.append({"term": term, "basis": "normalized_phrase_contains"})
                elif len(core) >= 2 and core.issubset(source_tokens):
                    matched.append({"term": term, "basis": "all_core_tokens_present"})
            if matched:
                candidate_hits.append({"objectLabel": source_name, "evidence": matched})
        candidate_hits.sort(key=lambda hit: (0 if any(e["basis"] == "normalized_phrase_contains" for e in hit["evidence"]) else 1, len(hit["objectLabel"]), hit["objectLabel"]))
        bp3d_candidates = target.get("existingEvidence", {}).get("sourceLexicalCandidates", [])
        rows.append({
            "targetId": target["id"], "sourceTa2Id": target["ta2Id"],
            "semanticKind": target["semanticKind"],
            "latin": target.get("term", {}).get("latin"), "english": target.get("term", {}).get("english"),
            "primaryOwner": target["primaryOwner"], "regionIds": sorted(memberships[target["id"]]),
            "t96Bp3dLexicalCandidateFjIds": bp3d_candidates,
            "zAnatomyObjectNameCandidates": candidate_hits[:20],
            "zAnatomyCandidateTruncated": len(candidate_hits) > 20,
            "identityStatus": "unresolved_no_exact_target_to_source_object_crosswalk",
            "geometryStatus": "not_evaluated_not_exported",
            "framePoseStatus": "not_reconciled",
            "localUseRights": "not_promoted",
            "redistributionRights": "held_pending_object_lineage_review",
            "learnerBinding": "none_added",
            "humanReview": "not_performed",
        })

    region_summary = []
    for region in scope["regions"]:
        these = [row for row in rows if row["primaryOwner"] == region["regionId"]]
        member_rows = [row for row in rows if region["regionId"] in row["regionIds"]]
        region_summary.append({
            "regionId": region["regionId"], "labelKo": region["labelKo"], "labelEn": region["labelEn"],
            "primaryTargetRecords": len(these), "membershipTargetRecords": len(member_rows),
            "targetsWithZAnatomyNameCandidate": sum(bool(row["zAnatomyObjectNameCandidates"]) for row in these),
            "targetsWithPriorBp3dLexicalCandidate": sum(bool(row["t96Bp3dLexicalCandidateFjIds"]) for row in these),
            "targetsWithExactSourceIdentity": 0,
            "targetsWithEvaluatedGeometry": 0,
        })

    bp3d_candidates_total = sum(bool(row["t96Bp3dLexicalCandidateFjIds"]) for row in rows)
    z_candidates_total = sum(bool(row["zAnatomyObjectNameCandidates"]) for row in rows)
    result = {
        "schemaVersion": "1.0.0",
        "task": "T98",
        "revision": "T98-whole-body-scope-freeze-v1",
        "status": "scope_and_name_candidate_reconciled_evaluated_source_unresolved",
        "sourceInputs": {
            "t96ScopeManifest": {"path": "atlas-data/catalog/target-scope-t96.json", "sha256": file_hash(SCOPE_PATH)},
            "t97ObjectInventory": {"path": "work/evidence/T97/blender-object-inventory.json", "sha256": file_hash(T97_PATH), "objectNameSetSha256": source_names_hash},
            "regionPackages": package_input_hashes,
        },
        "freeze": {
            "canonicalConceptTargetRecords": 542,
            "primaryOwnerAssignments": 542,
            "regionMembershipRows": 563,
            "membershipTargetIds": len(memberships),
            "individualMuscleDenominator": None,
            "individualMuscleDenominatorReason": scope["denominators"]["reasonIndividualMuscleDenominatorNull"],
            "regionRows": package_rows,
            "regionSummary": region_summary,
        },
        "sourceDenominators": {
            "zAnatomyArchiveEntries": 7,
            "zAnatomyArchiveFiles": 6,
            "zAnatomyBlendFiles": 1,
            "zAnatomySerializedObjects": t97.get("objectCount"),
            "zAnatomyUniqueMeshDatablocks": t97.get("meshDataBlockCount"),
            "zAnatomyCollections": t97.get("collectionCount"),
            "zAnatomyScenes": t97.get("sceneCount"),
            "zAnatomyEvaluatedGeometryResources": None,
            "zAnatomySceneInstanceCount": None,
            "bp3dExistingCacheFileCount": 721,
            "bp3dExistingCacheBytes": 430204718,
            "exactTa2ToBp3dFmaOrFjTargetJoins": 0,
            "exactTa2ToZAnatomyObjectTargetJoins": 0,
        },
        "candidateTally": {
            "targetsWithPriorT96Bp3dLexicalCandidate": bp3d_candidates_total,
            "targetsWithZAnatomyObjectNameCandidates": z_candidates_total,
            "candidateMeaning": "search/reconciliation leads only; no identity, laterality, geometry, frame, rights, or learner binding conclusion",
        },
        "rules": {
            "allFrozenTa2TargetsRetained": True,
            "regionPackagesReconciledExactly": True,
            "sourceNameMatching": "normalized phrase containment or all non-generic tokens present; candidate only, no semantic identity inference",
            "blenderSuffixHandling": "last serialized .l/.r/.el/.er/.ol/.or/.eN[lr]/.g/.j/.t/.s/.i suffix stripped only for search normalization; suffix is preserved in output and never interpreted as anatomy side/part",
            "rawDatablockCountsAreNot": ["canonical concept count", "evaluated geometry resource count", "visible scene instance count", "anatomical region coverage"],
        },
        "unresolvedTargetIds": [row["targetId"] for row in rows],
        "targets": rows,
    }
    out = OUT / "target-reconciliation-t98.json"
    out.write_text(json.dumps(result, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "targets": len(rows), "memberships": sum(len(row["regionIds"]) for row in rows), "regionSummary": region_summary, "candidates": result["candidateTally"], "output": str(out), "outputSha256": file_hash(out)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
