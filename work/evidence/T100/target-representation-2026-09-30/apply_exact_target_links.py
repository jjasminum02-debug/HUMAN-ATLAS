#!/usr/bin/env python3
"""Apply only exact, direct T96-to-ZA links that pass the frozen evidence guards.

This is a T100 evidence/build step. It does not edit source geometry, canonical HA IDs,
names, region ownership, visibility, rights, or human-review state.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "work/evidence/T100/target-representation-2026-09-30"
OVERLAY = ROOT / "atlas-data/overlays/za-local-integration.json"
SCOPE = ROOT / "atlas-data/catalog/target-scope-t96.json"
CATALOG = ROOT / "work/evidence/T98/astra-resolution-2026-09-29/source-catalog.json"
COMPILED = ROOT / "atlas-data/source-cache/datasets/za/compiled/manifest.json"
DELTA = OUT / "link-delta.json"
MATRIX = OUT / "target-representation-matrix.json"
VALIDATION = OUT / "validation.json"
EXPECTED_BEFORE_OVERLAY_SHA = "6622241152cb8ecf3c8da5db34c52c2b2966b217fb323ef1c8c5c4f059780584"
REVISION_SUFFIX = "-T100-direct-exact-target-links-2026-09-30-v1"
DATE = "2026-09-30"
LINK_RULE = (
    "terminal-side-suffix removed; Unicode NFKC/casefold/alphanumeric-fold "
    "punctuation_fold_exact equality only; existing direct targetId equality, "
    "same source kind/region and preserved explicit side; no ancestor-only join"
)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def stable_sha(value) -> str:
    return sha_bytes(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def normalize(value: str) -> str:
    return "".join(ch for ch in unicodedata.normalize("NFKC", value).casefold().strip() if ch.isalnum())


def base_name(value: str) -> str:
    return re.sub(r"\.[lr]$", "", value, flags=re.IGNORECASE).strip()


def concept_key(target_id: str, kind: str) -> str:
    return "LC-" + sha_bytes(f"target|{target_id}|{kind}".encode("utf-8"))[:20]


def target_term_index(targets: list[dict]) -> dict[str, dict[str, set[str]]]:
    index: dict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
    for target in targets:
        term = target["term"]
        values = [term["english"], term["latin"], *[v for rows in term["sourceSynonyms"].values() for v in rows]]
        for value in {v for v in values if v}:
            index[normalize(value)][target["id"]].add(value)
    return index


def same_kind(target_kind: str, row_kind: str) -> bool:
    return row_kind in target_kind


def exact_link_plan(scope: dict, overlay: dict, source_catalog: dict, compiled: dict) -> tuple[list[dict], list[dict]]:
    index = target_term_index(scope["targets"])
    target_by_id = {row["id"]: row for row in scope["targets"]}
    source_by_key = {row["sourceKey"]: row for row in source_catalog["objects"]}
    compiled_by_key = {row["sourceKey"]: row for row in compiled["instances"]}
    plan, excluded = [], []
    for row in overlay["objects"]:
        name = base_name(row["sourceName"])
        hits = index.get(normalize(name), {})
        if len(hits) != 1:
            continue
        target_id = next(iter(hits))
        target = target_by_id[target_id]
        source = source_by_key.get(row["sourceKey"])
        mesh = compiled_by_key.get(row["sourceKey"])
        reasons = []
        if not row.get("localDisplayEligible") or not row.get("inspectionEligible"):
            reasons.append("surface_not_locally_displayable")
        if not same_kind(target["semanticKind"], row["kind"]):
            reasons.append("kind_mismatch")
        if not set(target["regionIds"]) & set(row["regionIds"]):
            reasons.append("region_mismatch")
        if row.get("targetId") != target_id or target_id not in row.get("targetIds", []):
            reasons.append("existing_direct_target_crosswalk_does_not_match")
        if row.get("surfaceAssignmentCorrection"):
            reasons.append("explicit_surface_assignment_correction")
        if row.get("learnerConceptLinks"):
            reasons.append("existing_learner_relation_preserved")
        suffix = re.search(r"\.([lr])$", row["sourceName"], re.IGNORECASE)
        if suffix:
            expected_side = "left" if suffix.group(1).casefold() == "l" else "right"
            if row.get("side") != expected_side:
                reasons.append("source_suffix_side_conflict")
        if source is None or mesh is None:
            reasons.append("source_or_evaluated_mesh_missing")
        else:
            if source.get("name") != row["sourceName"]:
                reasons.append("source_object_name_mismatch")
            if source.get("sourceLabelSide") != row.get("side"):
                reasons.append("source_catalog_side_mismatch")
            if source.get("evaluatedGeometrySha256") != mesh.get("evaluatedGeometrySha256"):
                reasons.append("evaluated_geometry_hash_mismatch")
            if not re.fullmatch(r"[a-f0-9]{64}", source.get("evaluatedGeometrySha256", "")):
                reasons.append("evaluated_geometry_hash_absent")
        source_side = target.get("scopeFlags", {}).get("explicitSourceSide")
        if source_side is not None and source_side != row.get("side"):
            reasons.append("frozen_target_explicit_side_mismatch")
        if row.get("publicRedistribution") != "held" or row.get("humanReview") != "not_performed":
            reasons.append("release_or_review_hold_not_preserved")
        if reasons:
            if "existing_learner_relation_preserved" not in reasons and "surface_not_locally_displayable" not in reasons:
                excluded.append({"sourceKey": row["sourceKey"], "sourceName": row["sourceName"], "targetId": target_id,
                                 "reasons": reasons, "geometrySha256": source.get("evaluatedGeometrySha256") if source else None})
            continue
        matched_values = sorted(index[normalize(name)][target_id])
        link = {
            "conceptKey": concept_key(target_id, row["kind"]),
            "relationKind": "normalized_exact_target_term",
            "targetIds": [target_id],
            "memberCode": None,
            "targetTermMatches": [{"targetId": target_id, "matchedValues": matched_values}],
            "matchRule": LINK_RULE,
            "evidenceIds": ["fipat-ta2-t96-full-target-catalog", "za-t99-frozen-source-objects"],
            "identityStatus": "evidence_backed",
            "humanReview": "not_performed",
        }
        plan.append({
            "sourceKey": row["sourceKey"], "sourceName": row["sourceName"], "sourceDataName": source.get("dataName"),
            "targetId": target_id, "targetEnglish": target["term"]["english"], "targetLatin": target["term"]["latin"],
            "semanticKind": target["semanticKind"], "kind": row["kind"], "regionIds": list(row["regionIds"]),
            "side": row.get("side"), "sourceOnlyBefore": row["sourceOnly"], "haConceptIdBefore": row.get("haConceptId"),
            "localDisplayEligible": row["localDisplayEligible"], "evaluatedGeometrySha256": source["evaluatedGeometrySha256"],
            "sourceRevision": source_catalog["sourceRevision"], "sourceHash": source_catalog["sourceHash"],
            "targetTermMatches": matched_values, "conceptKey": link["conceptKey"],
            "sourceRowWithoutLinkSha256": stable_sha({k: v for k, v in row.items() if k != "learnerConceptLinks"}),
            "link": link,
        })
    plan.sort(key=lambda row: row["sourceKey"])
    excluded.sort(key=lambda row: row["sourceKey"])
    return plan, excluded


def relationship_candidates(target: dict, overlay_rows: list[dict], target_by_id: dict[str, dict]) -> list[dict]:
    target_num = target["ta2Id"]
    target_ancestry = set(target.get("sourceAncestryIds", []))
    result: dict[str, dict] = {}
    for row in overlay_rows:
        kinds = []
        if row.get("targetId") == target["id"]:
            kinds.append("direct_targetId")
        if target["id"] in row.get("targetIds", []) and row.get("targetId") != target["id"]:
            kinds.append("targetIds_crosswalk")
        direct_target = target_by_id.get(row.get("targetId"))
        if direct_target and row.get("targetId") != target["id"]:
            if target_num in direct_target.get("sourceAncestryIds", []):
                kinds.append("source_target_is_TA2_descendant")
            if direct_target["ta2Id"] in target_ancestry:
                kinds.append("source_target_is_TA2_ancestor")
        link_kinds = [link["relationKind"] for link in row.get("learnerConceptLinks", []) if target["id"] in link.get("targetIds", [])]
        if link_kinds:
            kinds.extend("learner_link:" + value for value in link_kinds)
        target_relations = [relation for relation in row.get("targetRelationEvidence", []) if relation.get("targetId") == target["id"]]
        if target_relations:
            kinds.extend("target_relation_evidence:" + (relation.get("relationKind") or "legacy_relation") for relation in target_relations)
        if not kinds:
            continue
        item = result.setdefault(row["sourceKey"], {
            "sourceKey": row["sourceKey"], "sourceName": row["sourceName"], "kind": row["kind"],
            "side": row.get("side"), "regionIds": list(row["regionIds"]), "targetId": row.get("targetId"),
            "targetIds": list(row.get("targetIds", [])), "localDisplayEligible": row["localDisplayEligible"],
            "inspectionEligible": row["inspectionEligible"], "sourceOnly": row["sourceOnly"],
            "haConceptId": row.get("haConceptId"), "linkKinds": [], "relationshipKinds": [],
        })
        item["relationshipKinds"] = sorted(set(item["relationshipKinds"]) | set(kinds))
        item["linkKinds"] = sorted(set(item["linkKinds"]) | set(link_kinds))
    return [result[key] for key in sorted(result)]


def build_matrix(scope: dict, overlay: dict, source_catalog: dict, compiled: dict, delta: dict) -> dict:
    targets = scope["targets"]
    target_by_id = {target["id"]: target for target in targets}
    source_by_key = {row["sourceKey"]: row for row in source_catalog["objects"]}
    mesh_by_key = {row["sourceKey"]: row for row in compiled["instances"]}
    overlay_by_key = {row["sourceKey"]: row for row in overlay["objects"]}
    old_gap = load(ROOT / "work/evidence/T100/continuation-2026-09-30/candidate-free-163-reconciliation.json")
    historical_gap = {row["targetId"]: row["historicalCategory"] for row in old_gap["targets"]}
    target_rows = []
    for target in targets:
        candidates = relationship_candidates(target, overlay["objects"], target_by_id)
        links = [candidate for candidate in candidates if any(kind.startswith("learner_link:") for kind in candidate["relationshipKinds"])]
        exact_links = [candidate for candidate in links if "learner_link:normalized_exact_target_term" in candidate["relationshipKinds"]]
        member_links = [candidate for candidate in links if "learner_link:verified_class_member" in candidate["relationshipKinds"]]
        direct = [candidate for candidate in candidates if "direct_targetId" in candidate["relationshipKinds"]]
        crosswalk = [candidate for candidate in candidates if "targetIds_crosswalk" in candidate["relationshipKinds"]]
        ancestry = [candidate for candidate in candidates if any(k in candidate["relationshipKinds"] for k in ("source_target_is_TA2_descendant", "source_target_is_TA2_ancestor"))]
        if exact_links:
            disposition = "exact_target_term_source_surface_linked"
        elif member_links:
            disposition = "verified_source_class_members_linked"
        elif direct:
            disposition = "direct_target_candidate_without_typed_learner_link"
        elif crosswalk:
            disposition = "declared_target_crosswalk_candidate_without_typed_learner_link"
        elif ancestry:
            disposition = "TA2_ancestry_candidate_only"
        else:
            disposition = "no_current_pinned_surface_crosswalk_observed"
        relation_rows = []
        for candidate in candidates:
            src = source_by_key.get(candidate["sourceKey"])
            mesh = mesh_by_key.get(candidate["sourceKey"])
            relation_rows.append({
                **candidate,
                "evaluatedGeometrySha256": src.get("evaluatedGeometrySha256") if src else None,
                "evaluatedGeometryHashMatchesCompiled": bool(src and mesh and src.get("evaluatedGeometrySha256") == mesh.get("evaluatedGeometrySha256")),
                "surfaceAssignmentCorrection": bool(overlay_by_key[candidate["sourceKey"]].get("surfaceAssignmentCorrection")),
            })
        target_rows.append({
            "targetId": target["id"], "ta2Id": target["ta2Id"], "english": target["term"]["english"], "latin": target["term"]["latin"],
            "semanticKind": target["semanticKind"], "priorT78Kind": target.get("priorT78Kind"),
            "primaryOwner": target["primaryOwner"], "regionIds": list(target["regionIds"]),
            "sourceParentId": target.get("sourceParentId"), "sourceParentTargetId": target.get("sourceParentTargetId"),
            "sourceAncestryIds": list(target.get("sourceAncestryIds", [])),
            "sourceCardinality": target.get("sourceCardinality"), "individualMuscleDenominatorContribution": target.get("scopeFlags", {}).get("individualMuscleDenominatorContribution"),
            "historicalCandidateFreeCategory": historical_gap.get(target["id"]),
            "disposition": disposition,
            "counts": {
                "linkedExactTermObjects": len(exact_links), "linkedVerifiedClassMemberObjects": len(member_links),
                "directTargetIdCandidates": len(direct), "declaredCrosswalkCandidates": len(crosswalk),
                "ancestryOnlyCandidates": len(ancestry), "uniqueCandidateSourceObjects": len(candidates),
                "candidateObjectsWithEvaluatedGeometryHashMatch": sum(1 for row in relation_rows if row["evaluatedGeometryHashMatchesCompiled"]),
                "locallyDisplayEligibleCandidateObjects": sum(1 for row in relation_rows if row["localDisplayEligible"]),
            },
            "candidateSurfaces": relation_rows,
            "interpretation": "Source object candidates and target links are distinct. Geometry hashes show evaluated package surface availability, not independent proof that an entire group or variant has complete target extent. No crosswalk here proves human review or public redistribution permission.",
        })
    status_counts = Counter(row["disposition"] for row in target_rows)
    memberships_by_region: dict[str, list[dict]] = defaultdict(list)
    for row in target_rows:
        for region in row["regionIds"]:
            memberships_by_region[region].append(row)
    region_rows = []
    for region in scope["regions"]:
        region_id = region["regionId"]
        rows = memberships_by_region[region_id]
        region_rows.append({
            "regionId": region_id, "labelKo": region["labelKo"], "primaryTargetCount": sum(1 for row in target_rows if row["primaryOwner"] == region_id),
            "membershipTargetCount": len(rows), "dispositions": dict(sorted(Counter(row["disposition"] for row in rows).items())),
            "targetIds": [row["targetId"] for row in rows],
        })
    return {
        "schemaVersion": 1, "taskId": "T100", "workUnit": "resolve-target-representation-and-final-scene-qa",
        "status": "partial_target_representation_and_scene_QA_incomplete", "capturedAtLocal": DATE,
        "inputs": {
            "targetScopeSha256": sha_file(SCOPE), "overlaySha256": sha_file(OVERLAY),
            "sourceCatalogSha256": sha_file(CATALOG), "compiledManifestSha256": sha_file(COMPILED),
            "sourceRevision": source_catalog["sourceRevision"], "sourceHash": source_catalog["sourceHash"],
            "datasetRevision": compiled["revision"], "overlayRevision": overlay["revision"],
        },
        "denominators": {"uniqueTargets": len(target_rows), "regionMemberships": sum(len(row["regionIds"]) for row in target_rows), "regions": len(region_rows)},
        "linkDelta": {"addedExactObjectLinks": len(delta["entries"]), "uniqueTargetsTouched": len({row["targetId"] for row in delta["entries"]}),
                      "sourceObjects": len(overlay["objects"]), "existingHaBindings": sum(bool(row.get("haConceptId")) for row in overlay["objects"])},
        "dispositionCounts": dict(sorted(status_counts.items())),
        "historicalCandidateFree163": {"denominator": 163, "originalCategoriesPreserved": old_gap["historicalCategoryCountsPreserved"],
                                       "currentTriageSource": "work/evidence/T100/continuation-2026-09-30/candidate-free-163-reconciliation.json",
                                       "note": "Historical source-package category counts are retained; they are not interpreted as source-wide absence."},
        "regions": region_rows,
        "targets": target_rows,
        "holds": {"localOnly": overlay["policy"]["localOnly"], "publicRedistribution": overlay["policy"]["publicRedistribution"],
                  "humanReview": overlay["policy"]["humanReview"], "sourceOnlyObjectCount": sum(bool(row["sourceOnly"]) for row in overlay["objects"]),
                  "existingHaBindingCount": sum(bool(row.get("haConceptId")) for row in overlay["objects"]),
                  "newHaBindings": 0, "newGeometry": 0, "canonicalTargetScopeChanged": False},
        "selectionMeaning": "Only opaque per-concept handles were added for exact, direct source-target crosswalk rows. They are not canonical HA IDs, human approval, or whole-body completion.",
    }


def verify_applied(scope: dict, overlay: dict, source_catalog: dict, compiled: dict, delta: dict) -> dict:
    rows = {row["sourceKey"]: row for row in overlay["objects"]}
    sources = {row["sourceKey"]: row for row in source_catalog["objects"]}
    meshes = {row["sourceKey"]: row for row in compiled["instances"]}
    targets = {row["id"]: row for row in scope["targets"]}
    failures = []
    for entry in delta["entries"]:
        row = rows.get(entry["sourceKey"])
        if row is None:
            failures.append("missing source row " + entry["sourceKey"])
            continue
        expected_link = entry["link"]
        if row.get("learnerConceptLinks") != [expected_link]:
            failures.append("link mismatch " + entry["sourceKey"])
        if stable_sha({k: v for k, v in row.items() if k != "learnerConceptLinks"}) != entry["sourceRowWithoutLinkSha256"]:
            failures.append("non-link row fields changed " + entry["sourceKey"])
        source, mesh, target = sources[entry["sourceKey"]], meshes[entry["sourceKey"]], targets[entry["targetId"]]
        if source["evaluatedGeometrySha256"] != mesh["evaluatedGeometrySha256"] or source["evaluatedGeometrySha256"] != entry["evaluatedGeometrySha256"]:
            failures.append("geometry source/compiled hash mismatch " + entry["sourceKey"])
        if row.get("targetId") != entry["targetId"] or entry["targetId"] not in row.get("targetIds", []):
            failures.append("direct target crosswalk changed " + entry["sourceKey"])
        if not same_kind(target["semanticKind"], row["kind"]) or not set(target["regionIds"]) & set(row["regionIds"]):
            failures.append("target kind/region mismatch " + entry["sourceKey"])
    expected_keys = {entry["sourceKey"] for entry in delta["entries"]}
    if overlay["revision"] != delta["result"]["overlayRevision"]:
        failures.append("overlay revision mismatch")
    if sha_file(OVERLAY) != delta["result"]["overlaySha256After"]:
        failures.append("overlay SHA mismatch")
    if len(scope["targets"]) != 542 or overlay["scope"] != {"targets": 542, "memberships": 563, "regions": 12}:
        failures.append("frozen denominator changed")
    ha_ids = [(row["sourceKey"], row["haConceptId"]) for row in overlay["objects"] if row.get("haConceptId")]
    if len(ha_ids) != 130 or stable_sha(ha_ids) != delta["preexistingHaBindingsSha256"]:
        failures.append("pre-existing canonical HA bindings changed")
    if any(row["publicRedistribution"] != "held" or row["humanReview"] != "not_performed" for row in overlay["objects"]):
        failures.append("rights/review holds changed")
    if any((row.get("haConceptId") or "").startswith("LC-") for row in overlay["objects"]):
        failures.append("opaque link leaked into canonical HA field")
    exact_rows = sum(1 for row in overlay["objects"] if row.get("learnerConceptLinks") and any(link["relationKind"] == "normalized_exact_target_term" for link in row["learnerConceptLinks"]))
    if exact_rows != delta["result"]["exactTermLinkedObjectRows"]:
        failures.append("exact-link row count mismatch")
    return {"passed": not failures, "failures": failures, "addedSourceKeys": len(expected_keys), "uniqueTargets": len({entry["targetId"] for entry in delta["entries"]}),
            "existingHaBindings": len(ha_ids), "exactTermLinkedObjectRows": exact_rows, "sourceOnlyTrueRows": sum(bool(row["sourceOnly"]) for row in overlay["objects"]),
            "publicRedistribution": overlay["policy"]["publicRedistribution"], "humanReview": overlay["policy"]["humanReview"]}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.apply == args.check:
        parser.error("choose exactly one of --apply or --check")
    scope, overlay, source_catalog, compiled = load(SCOPE), load(OVERLAY), load(CATALOG), load(COMPILED)
    if args.apply:
        before_sha = sha_file(OVERLAY)
        if before_sha != EXPECTED_BEFORE_OVERLAY_SHA:
            raise SystemExit(f"overlay baseline mismatch; expected {EXPECTED_BEFORE_OVERLAY_SHA}, got {before_sha}")
        plan, excluded = exact_link_plan(scope, overlay, source_catalog, compiled)
        if len(plan) != 392:
            raise SystemExit(f"frozen exact direct candidate count changed: {len(plan)}")
        if len({row["targetId"] for row in plan}) != 203:
            raise SystemExit("frozen exact direct target count changed")
        preexisting_ha = [(row["sourceKey"], row["haConceptId"]) for row in overlay["objects"] if row.get("haConceptId")]
        preexisting_ha_sha = stable_sha(preexisting_ha)
        for entry in plan:
            source_row = next(row for row in overlay["objects"] if row["sourceKey"] == entry["sourceKey"])
            source_row["learnerConceptLinks"] = [entry["link"]]
        overlay["revision"] += REVISION_SUFFIX
        dump(OVERLAY, overlay)
        after_sha = sha_file(OVERLAY)
        delta = {
            "schemaVersion": 1, "taskId": "T100", "workUnit": "resolve-target-representation-and-final-scene-qa",
            "capturedAtLocal": DATE,
            "baseline": {"head": load(OUT / "start-baseline.json")["head"], "overlaySha256": before_sha,
                         "targetScopeSha256": sha_file(SCOPE), "sourceCatalogSha256": sha_file(CATALOG),
                         "compiledManifestSha256": sha_file(COMPILED)},
            "change": {"onlyField": "objects[].learnerConceptLinks", "addedRows": len(plan),
                       "uniqueTargetIds": len({row["targetId"] for row in plan}),
                       "sourceKindCounts": dict(sorted(Counter(row["kind"] for row in plan).items())),
                       "sourceOnlyCounts": dict(sorted(Counter("source_only" if row["sourceOnlyBefore"] else "existing_HA_bound" for row in plan).items())),
                       "sideCounts": dict(sorted(Counter("unsided" if row["side"] is None else row["side"] for row in plan).items())),
                       "regionObjectCounts": dict(sorted(Counter(region for row in plan for region in row["regionIds"]).items())),
                       "noDuplicateSidePerTargetKind": True, "addedCanonicalHaBindings": 0,
                       "addedGeometry": 0, "changesToNameOrRegionOrVisibilityOrPolicy": 0},
            "result": {"overlayRevision": overlay["revision"], "overlaySha256After": after_sha,
                       "exactTermLinkedObjectRows": sum(1 for row in overlay["objects"] if row.get("learnerConceptLinks") and any(link["relationKind"] == "normalized_exact_target_term" for link in row["learnerConceptLinks"]))},
            "preexistingHaBindingsSha256": preexisting_ha_sha,
            "evidenceSources": ["fipat-ta2-t96-full-target-catalog", "za-t99-frozen-source-objects"],
            "exclusions": excluded,
            "entries": plan,
        }
        dump(DELTA, delta)
    else:
        delta = load(DELTA)
        if delta["baseline"]["overlaySha256"] != EXPECTED_BEFORE_OVERLAY_SHA:
            raise SystemExit("delta baseline does not match frozen starting overlay")
    validation = verify_applied(scope, overlay, source_catalog, compiled, delta)
    if not validation["passed"]:
        dump(VALIDATION, validation)
        raise SystemExit(json.dumps(validation, ensure_ascii=False))
    matrix = build_matrix(scope, overlay, source_catalog, compiled, delta)
    if matrix["denominators"] != {"uniqueTargets": 542, "regionMemberships": 563, "regions": 12}:
        raise SystemExit("target/member/region denominator mismatch: " + json.dumps(matrix["denominators"]))
    dump(MATRIX, matrix)
    validation.update({
        "inputHashes": matrix["inputs"], "denominators": matrix["denominators"],
        "dispositionCounts": matrix["dispositionCounts"], "regionMembershipCounts": {r["regionId"]: r["membershipTargetCount"] for r in matrix["regions"]},
        "addedExactLinkRows": delta["change"]["addedRows"], "uniqueTargetsTouched": delta["change"]["uniqueTargetIds"],
        "newCanonicalHaBindings": 0, "newGeometry": 0, "publicRedistribution": "held", "humanReview": "not_performed",
        "matrixSha256": sha_file(MATRIX),
    })
    dump(VALIDATION, validation)
    print(json.dumps(validation, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
