#!/usr/bin/env python3
"""Build bounded T100 member links from existing exact leaf and T96 ancestry evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "work/evidence/T100/target-representation-continuation-2026-09-30"
OVERLAY = ROOT / "atlas-data/overlays/za-local-integration.json"
SCOPE = ROOT / "atlas-data/catalog/target-scope-t96.json"
SOURCE = ROOT / "work/evidence/T98/astra-resolution-2026-09-29/source-catalog.json"
COMPILED = ROOT / "atlas-data/source-cache/datasets/za/compiled/manifest.json"
MATRIX = ROOT / "work/evidence/T100/target-representation-2026-09-30/target-representation-matrix.json"
EXCEPTIONS = ROOT / "work/evidence/T100/bulk-continuation-2026-09-29/exceptions.json"
DATE = "2026-09-30"
TARGET_SCOPE_SOURCE = "fipat-ta2-t96-full-target-catalog"
SOURCE_OBJECT_SOURCE = "za-t99-frozen-source-objects"
UNRESOLVED = {
    "direct_target_candidate_without_typed_learner_link",
    "declared_target_crosswalk_candidate_without_typed_learner_link",
    "TA2_ancestry_candidate_only",
    "no_current_pinned_surface_crosswalk_observed",
}


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def opaque(seed: str) -> str:
    return "LC-" + sha(seed.encode("utf-8"))[:20]


def target_id(value: int) -> str:
    return f"TA2:{value}"


def source_side_suffix(name: str) -> str | None:
    m = re.search(r"\.([lr])$", name, re.I)
    return ("left" if m.group(1).lower() == "l" else "right") if m else None


def canonical_member_code(relation: dict) -> str | None:
    code = relation.get("memberCode")
    if code:
        return re.sub(r":(left|right)$", "", code)
    segment = relation.get("sourceSegmentCode")
    if segment and relation.get("targetId") in {"TA2:1032", "TA2:1059"}:
        return "segment:" + segment
    return None


def compatible_kind(target: dict, row: dict) -> bool:
    return row["kind"] in target["semanticKind"]


def route_side_key(row: dict) -> str:
    return row.get("side") or "unsided"


def class_relation_proof(row: dict, relation: dict, target: dict, source: dict, compiled: dict) -> bool:
    if relation.get("relationKind") != "class_member" or relation.get("sourceKey") != row["sourceKey"]:
        return False
    if relation.get("sourceObjectName") != row["sourceName"] or relation.get("sourceSide") != row.get("side"):
        return False
    if relation.get("targetSemanticKind") != target["semanticKind"] or not set(relation.get("targetRegionIds", [])) & set(row["regionIds"]):
        return False
    if relation.get("ancestorNameAloneUsed") or relation.get("upstreamFjOrTa2IdClaim") or relation.get("canonicalHaBindingCreated"):
        return False
    if relation.get("humanReview") != "not_performed" or relation.get("evaluatedGeometrySha256") != source.get("evaluatedGeometrySha256"):
        return False
    if relation.get("evaluatedGeometrySha256") != compiled.get("evaluatedGeometrySha256"):
        return False
    if relation.get("sourceHash") != source.get("sourceLocator", {}).get("sourceFileSha256"):
        return False
    if relation.get("sourceRevision") != "c7010a903b75a2fd24a13b1c2c4c3546a9223780":
        return False
    if source.get("name") != row["sourceName"] or source.get("parent") != relation.get("sourceParent"):
        return False
    if source.get("collections") != relation.get("sourceCollections"):
        return False
    if source.get("sourceLabelSide") != row.get("side"):
        return False
    if not relation.get("matchEvidenceSourceIds"):
        return False
    code = canonical_member_code(relation)
    if not code:
        return False
    suffix_side = source_side_suffix(row["sourceName"])
    return suffix_side is None or suffix_side == row.get("side")


def normalized_link_proof(row: dict, link: dict, targets: dict, source: dict, compiled: dict) -> bool:
    if link.get("relationKind") != "normalized_exact_target_term" or link.get("identityStatus") != "evidence_backed":
        return False
    if len(link.get("targetIds", [])) != 1 or len(link.get("targetTermMatches", [])) != 1:
        return False
    child_id = link["targetIds"][0]
    child = targets.get(child_id)
    match = link["targetTermMatches"][0]
    if not child or match.get("targetId") != child_id or not match.get("matchedValues"):
        return False
    if not compatible_kind(child, row) or not set(child["regionIds"]) & set(row["regionIds"]):
        return False
    if TARGET_SCOPE_SOURCE not in link.get("evidenceIds", []) or SOURCE_OBJECT_SOURCE not in link.get("evidenceIds", []):
        return False
    if row.get("surfaceAssignmentCorrection") or not row.get("localDisplayEligible") or not row.get("inspectionEligible"):
        return False
    suffix_side = source_side_suffix(row["sourceName"])
    if suffix_side and suffix_side != row.get("side"):
        return False
    if source.get("name") != row["sourceName"] or compiled.get("name") != row["sourceName"]:
        return False
    if source.get("evaluatedGeometrySha256") != compiled.get("evaluatedGeometrySha256"):
        return False
    if source.get("sourceLocator", {}).get("sourceFileSha256") != "9f08a17ea0115fed80b2a73ecdf0a1bc2ab2f6956f37c593ce23d513ea35afcd":
        return False
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="validate reproducibility without writing the overlay")
    args = parser.parse_args()

    overlay_bytes = OVERLAY.read_bytes()
    overlay = json.loads(overlay_bytes)
    scope = read(SCOPE)
    source_catalog = read(SOURCE)
    compiled_manifest = read(COMPILED)
    matrix = read(MATRIX)
    exceptions = read(EXCEPTIONS)
    scope_bytes = SCOPE.read_bytes()
    scope_by_id = {target_id(t["ta2Id"]): t for t in scope["targets"]}
    matrix_by_id = {t["targetId"]: t for t in matrix["targets"]}
    unresolved_ids = {tid for tid, t in matrix_by_id.items() if t["disposition"] in UNRESOLVED}
    source_by_key = {row["sourceKey"]: row for row in source_catalog["objects"]}
    compiled_by_key = {row["sourceKey"]: row for row in compiled_manifest["instances"]}
    objects = {row["sourceKey"]: row for row in overlay["objects"]}

    assert len(scope["targets"]) == 542 and overlay["scope"] == {"targets": 542, "memberships": 563, "regions": 12}
    assert sum(len(t["regionIds"]) for t in scope["targets"]) == 563
    assert scope_by_id.keys() == matrix_by_id.keys()
    assert source_catalog["sourceHash"] == overlay["sourceHash"] == compiled_manifest["sourceHash"]
    assert source_catalog["sourceRevision"] == "c7010a903b75a2fd24a13b1c2c4c3546a9223780"
    assert source_catalog["sourceHash"] == "9f08a17ea0115fed80b2a73ecdf0a1bc2ab2f6956f37c593ce23d513ea35afcd"
    assert compiled_manifest["catalogHash"] == overlay["sourceCatalogSha256"]
    assert len(objects) == 960 and len(source_by_key) == 960 and len(compiled_by_key) == 960

    baseline = read(OUT / "start-baseline.json")
    before_hash = baseline["inputSha256"]["atlas-data/overlays/za-local-integration.json"]
    expected_output = baseline.get("outputOverlaySha256")
    if overlay_bytes and sha(overlay_bytes) != before_hash and not (expected_output and sha(overlay_bytes) == expected_output):
        raise SystemExit("current overlay differs from T100 continuation baseline and no matching prior output hash is recorded")

    link_delta = Counter()
    class_updates = []
    class_exclusions = []
    added_class_links: list[dict] = []

    # Stage exact class relations by their immutable member-code grouping. This reuses existing
    # T100 row evidence; no target names, side labels, meshes, or source geometry are inferred.
    for row in overlay["objects"]:
        source = source_by_key.get(row["sourceKey"])
        compiled = compiled_by_key.get(row["sourceKey"])
        if source is None or compiled is None or not row.get("localDisplayEligible") or not row.get("inspectionEligible"):
            continue
        if any(link.get("identityStatus") in {"held", "side_conflicted"} for link in row.get("learnerConceptLinks", [])):
            continue
        rels = [r for r in row.get("targetRelationEvidence", []) if r.get("relationKind") == "class_member"]
        groups: dict[str, list[dict]] = defaultdict(list)
        for relation in rels:
            target = scope_by_id.get(relation.get("targetId"))
            if not target or not class_relation_proof(row, relation, target, source, compiled):
                class_exclusions.append({"sourceKey": row["sourceKey"], "targetId": relation.get("targetId"), "sourceName": row["sourceName"], "reason": "class_member_evidence_did_not_match_frozen_source_and_compiled_geometry"})
                continue
            member = canonical_member_code(relation)
            groups[member].append(relation)
        for member, group in sorted(groups.items()):
            target_ids = sorted({r["targetId"] for r in group})
            evidence_ids = sorted({sid for r in group for sid in r.get("matchEvidenceSourceIds", [])})
            if not evidence_ids:
                continue
            existing = next((link for link in row.get("learnerConceptLinks", [])
                if link.get("relationKind") == "verified_class_member"
                and set(link.get("targetIds", [])) == set(target_ids) and link.get("memberCode") == member), None)
            if existing:
                continue
            side = row.get("side")
            if side not in {"left", "right", None}:
                class_exclusions.append({"sourceKey": row["sourceKey"], "targetIds": target_ids, "sourceName": row["sourceName"], "reason": "unknown_side"})
                continue
            if side is None and not all(r.get("sourceSegmentCode") for r in group):
                class_exclusions.append({"sourceKey": row["sourceKey"], "targetIds": target_ids, "sourceName": row["sourceName"], "reason": "unsided_nonsegment_member"})
                continue
            key_seed = "member|" + "|".join(target_ids) + "|" + member + "|" + row["kind"]
            link = {
                "conceptKey": opaque(key_seed), "relationKind": "verified_class_member",
                "targetIds": target_ids, "memberCode": member, "targetTermMatches": [],
                "matchRule": "exact frozen T96 class_member memberCode or sourceSegmentCode + observed source side + source/compiled geometry hash",
                "evidenceIds": evidence_ids, "identityStatus": "evidence_backed", "humanReview": "not_performed",
            }
            added_class_links.append({"sourceKey": row["sourceKey"], "sourceName": row["sourceName"], "side": side, "targetIds": target_ids, "memberCode": member, "link": link})
            link_delta["verified_class_member_links_added"] += 1

    if not args.check:
        for item in added_class_links:
            objects[item["sourceKey"]].setdefault("learnerConceptLinks", []).append(item["link"])

    # Build child proofs from current exact-target links and the validated class-member plan.
    proofs: dict[str, list[dict]] = defaultdict(list)
    for row in overlay["objects"]:
        source = source_by_key.get(row["sourceKey"])
        compiled = compiled_by_key.get(row["sourceKey"])
        if source is None or compiled is None or row.get("surfaceAssignmentCorrection"):
            continue
        if any(link.get("identityStatus") in {"held", "side_conflicted"} for link in row.get("learnerConceptLinks", [])):
            continue
        for link in [*row.get("learnerConceptLinks", []), *[x["link"] for x in added_class_links if x["sourceKey"] == row["sourceKey"]]]:
            if link.get("relationKind") == "normalized_exact_target_term" and normalized_link_proof(row, link, scope_by_id, source, compiled):
                child = link["targetIds"][0]
                proofs[row["sourceKey"]].append({"childTargetId": child, "memberCode": child, "proofKind": "normalized_exact_target_term", "proofEvidenceIds": link["evidenceIds"]})
            elif link.get("relationKind") == "verified_class_member":
                for child in link.get("targetIds", []):
                    proof_relations = [r for r in row.get("targetRelationEvidence", []) if r.get("targetId") == child and r.get("relationKind") == "class_member"]
                    if any(class_relation_proof(row, r, scope_by_id[child], source, compiled) for r in proof_relations):
                        proofs[row["sourceKey"]].append({"childTargetId": child, "memberCode": link["memberCode"], "proofKind": "verified_class_member", "proofEvidenceIds": sorted({sid for r in proof_relations for sid in r.get("matchEvidenceSourceIds", [])})})

    taxonomy_candidates: dict[tuple[str, str, str, str], list[dict]] = defaultdict(list)
    taxonomy_exclusions = []
    for row in overlay["objects"]:
        if not row.get("localDisplayEligible") or not row.get("inspectionEligible") or row.get("surfaceAssignmentCorrection"):
            continue
        if any(link.get("identityStatus") in {"held", "side_conflicted"} for link in row.get("learnerConceptLinks", [])):
            continue
        for proof in proofs.get(row["sourceKey"], []):
            child = scope_by_id.get(proof["childTargetId"])
            if not child:
                continue
            for raw_ancestor in child.get("sourceAncestryIds", [])[1:]:
                parent_id = target_id(raw_ancestor)
                if parent_id not in unresolved_ids:
                    continue
                parent = scope_by_id[parent_id]
                if parent_id == proof.get("childTargetId"):
                    continue
                if not compatible_kind(parent, row) or not (set(parent["regionIds"]) & set(row["regionIds"])):
                    continue
                parent_side = parent.get("sourceCardinality", {}).get("explicitSourceSide")
                if parent_side and row.get("side") != parent_side:
                    taxonomy_exclusions.append({"sourceKey": row["sourceKey"], "targetId": parent_id, "childTargetId": proof["childTargetId"], "reason": "source_side_does_not_match_frozen_explicit_target_side"})
                    continue
                suffix_side = source_side_suffix(row["sourceName"])
                if suffix_side and suffix_side != row.get("side"):
                    taxonomy_exclusions.append({"sourceKey": row["sourceKey"], "targetId": parent_id, "childTargetId": proof["childTargetId"], "reason": "source_suffix_side_conflict"})
                    continue
                member_code = proof["memberCode"]
                key = (parent_id, proof["childTargetId"], member_code, row["kind"])
                if not any(candidate["row"]["sourceKey"] == row["sourceKey"] for candidate in taxonomy_candidates[key]):
                    taxonomy_candidates[key].append({"row": row, "proof": proof})

    taxonomy_links = []
    for (parent_id, child_id, member_code, kind), candidates in sorted(taxonomy_candidates.items()):
        # A single source object per side (or one explicitly midline object) is required so each
        # opaque selection handle resolves to exactly one surface for that side.
        by_side: dict[str, list[dict]] = defaultdict(list)
        for candidate in candidates:
            by_side[route_side_key(candidate["row"])].append(candidate)
        if any(len(group) != 1 for group in by_side.values()):
            taxonomy_exclusions.extend({"sourceKey": c["row"]["sourceKey"], "targetId": parent_id, "childTargetId": child_id, "reason": "ambiguous_same_side_surface_for_member_route"} for c in candidates)
            continue
        for candidate in candidates:
            row = candidate["row"]
            proof = candidate["proof"]
            if any(link.get("relationKind") == "verified_taxonomy_member" and parent_id in link.get("targetIds", []) and link.get("memberCode") == child_id for link in row.get("learnerConceptLinks", [])):
                continue
            evidence_ids = sorted(set([TARGET_SCOPE_SOURCE, SOURCE_OBJECT_SOURCE, *proof.get("proofEvidenceIds", [])]))
            link = {
                "conceptKey": opaque("taxonomy-member|" + parent_id + "|" + child_id + "|" + member_code + "|" + kind),
                "relationKind": "verified_taxonomy_member", "targetIds": [parent_id], "memberCode": child_id,
                "targetTermMatches": [],
                "matchRule": "exact frozen T96 sourceAncestryIds parent membership from an identity-backed child member; one selectable source member only; not a completeness claim",
                "evidenceIds": evidence_ids, "identityStatus": "evidence_backed", "humanReview": "not_performed",
            }
            taxonomy_links.append({"sourceKey": row["sourceKey"], "sourceName": row["sourceName"], "side": row["side"], "targetId": parent_id, "childTargetId": child_id, "childMemberCode": member_code, "proofKind": proof["proofKind"], "link": link})
            link_delta["verified_taxonomy_member_links_added"] += 1

    # Emit exact evidence-backed rows only. Existing row fields, source geometry, names, IDs,
    # display/rights decisions, and canonical bindings remain byte-semantic peers of the input.
    for item in taxonomy_links:
        objects[item["sourceKey"]].setdefault("learnerConceptLinks", []).append(item["link"])

    unresolved_after = {}
    for target_id_value, base in matrix_by_id.items():
        row_links = []
        for row in overlay["objects"]:
            for link in row.get("learnerConceptLinks", []):
                if target_id_value in link.get("targetIds", []) and link.get("identityStatus") == "evidence_backed" and link.get("conceptKey"):
                    row_links.append((row, link))
        if target_id_value in unresolved_ids:
            unresolved_after[target_id_value] = {
                "baseDisposition": base["disposition"], "semanticKind": base["semanticKind"], "primaryOwner": base["primaryOwner"],
                "regions": base["regionIds"], "candidateSurfaceCountBefore": len(base["candidateSurfaces"]),
                "typedSelectableSurfaceCountAfter": len({row["sourceKey"] for row, _ in row_links}),
                "typedLinkKindsAfter": dict(Counter(link["relationKind"] for _, link in row_links)),
                "status": "member_surfaces_linked_partial_scope" if row_links else "unresolved_no_identity_backed_member_link",
                "memberSources": [{"sourceKey": row["sourceKey"], "sourceName": row["sourceName"], "side": row["side"], "regionIds": row["regionIds"], "relationKind": link["relationKind"], "memberCode": link["memberCode"]} for row, link in row_links],
            }

    # Preserve candidate-free historical reconciliation verbatim.  The matrix is regenerated
    # from link types for the 542 frozen rows; selection evidence remains membership-level.
    target_representation = []
    disposition_counts = Counter()
    category_resolved_counts = Counter()
    for t in scope["targets"]:
        tid = target_id(t["ta2Id"])
        base = matrix_by_id[tid]
        relations = []
        for row in overlay["objects"]:
            if not row.get("localDisplayEligible") or not (set(t["regionIds"]) & set(row["regionIds"])):
                continue
            for link in row.get("learnerConceptLinks", []):
                if tid not in link.get("targetIds", []) or not link.get("conceptKey") or link.get("identityStatus") != "evidence_backed":
                    continue
                relations.append((row, link))
        kinds = Counter(link["relationKind"] for _, link in relations)
        if kinds["normalized_exact_target_term"]:
            disposition = "exact_target_term_source_surface_linked"
        elif kinds["verified_class_member"]:
            disposition = "verified_source_class_members_linked"
        elif kinds["verified_taxonomy_member"]:
            disposition = "verified_T96_ancestor_member_surfaces_linked"
        else:
            disposition = base["disposition"]
        disposition_counts[disposition] += 1
        if tid in unresolved_ids and relations:
            category_resolved_counts[base["disposition"]] += 1
        target_representation.append({
            "targetId": tid, "english": t["term"]["english"], "latin": t["term"]["latin"],
            "semanticKind": t["semanticKind"], "primaryOwner": t["primaryOwner"], "regionIds": t["regionIds"],
            "frozenSourceAncestryIds": t["sourceAncestryIds"], "baselineDisposition": base["disposition"],
            "typedRelationDisposition": disposition, "relationCounts": dict(kinds),
            "selectableSourceObjects": sorted({row["sourceKey"] for row, _ in relations}),
            "selectableSurfaceCount": len({row["sourceKey"] for row, _ in relations}),
            "coverageCompleteness": "not_asserted_from_member_links",
            "interpretation": "A target may resolve to one or more exact selectable member surfaces. This does not assert that the listed surfaces exhaust the target geometry or that the parent target is one mesh.",
        })

    missing_terms = []
    term_by_id = {term["targetId"]: term for term in overlay.get("targetTerminologyEvidence", [])}
    for gap in exceptions["termGaps"]:
        term = term_by_id.get(gap["targetId"])
        missing_terms.append({**gap,
            "semanticKind": term["semanticKind"] if term else None,
            "regionIds": term["regionIds"] if term else [],
            "currentTargetFieldEvidence": term["fieldEvidence"] if term else None,
            "existingSurfaceStatus": term.get("existingSurface", {}).get("status") if term else None,
            "sourceQueryHistoryPreserved": True,
            "decision": "remain_missing_without_new_field-level source locator"})

    memberships = []
    route_failures = []
    for t in scope["targets"]:
        tid = target_id(t["ta2Id"])
        for region in t["regionIds"]:
            member_links = []
            for row in overlay["objects"]:
                if not row.get("localDisplayEligible") or region not in row["regionIds"]:
                    continue
                for link in row.get("learnerConceptLinks", []):
                    if tid not in link.get("targetIds", []) or not link.get("conceptKey") or link.get("identityStatus") != "evidence_backed":
                        continue
                    member_links.append((row, link))
            unique = {}
            for row, link in member_links:
                unique[row["sourceKey"]] = (row, link)
            handles = []
            for row, link in sorted(unique.values(), key=lambda x: (x[0]["side"] or "", x[0]["sourceKey"])):
                handle_rows = [r for r in overlay["objects"] if r.get("localDisplayEligible") and link["conceptKey"] in [x.get("conceptKey") for x in r.get("learnerConceptLinks", [])] and r.get("side") == row.get("side")]
                route_ok = len(handle_rows) == 1 and handle_rows[0]["sourceKey"] == row["sourceKey"] and region in row["regionIds"]
                handles.append({"sourceKey": row["sourceKey"], "sourceName": row["sourceName"], "side": row["side"], "relationKind": link["relationKind"], "memberCode": link["memberCode"], "conceptKey": link["conceptKey"], "routeResolvesToExactSourceAndRegion": route_ok})
                if not route_ok:
                    route_failures.append({"targetId": tid, "regionId": region, "sourceKey": row["sourceKey"], "conceptKey": link["conceptKey"], "matchingRowsOnSide": [r["sourceKey"] for r in handle_rows]})
            memberships.append({"targetId": tid, "regionId": region, "semanticKind": t["semanticKind"], "primaryOwner": t["primaryOwner"],
                "selectedMemberSurfaceCount": len(handles), "selectionRoutes": handles,
                "status": "selectable_member_surfaces_verified" if handles and all(h["routeResolvesToExactSourceAndRegion"] for h in handles)
                    else "selectable_member_routes_with_failures" if handles else "no_exact_selectable_member_surface",
                "coverageCompleteness": "not_asserted_from_member_links"})

    # The 163-source-category history, 542/563/12 freeze, 130 HA bindings, and every source
    # decision are invariants, not outputs recalculated from candidate count.
    baseline_counts = {"scopeTargets": 542, "scopeMemberships": 563, "regions": 12,
        "sourceObjects": 960, "localDisplayEligible": 672, "existingHaBindings": 130,
        "sourceOnly": sum(1 for row in overlay["objects"] if row.get("sourceOnly") is True),
        "publicRedistributionHeld": sum(1 for row in overlay["objects"] if row.get("publicRedistribution") == "held"),
        "humanReviewNotPerformed": sum(1 for row in overlay["objects"] if row.get("humanReview") == "not_performed"),
        "historicalCandidateFree163": matrix["historicalCandidateFree163"]["denominator"]}
    summary = {
        "taskId": "T100", "workUnit": "resolve-target-representation-and-final-scene-qa", "capturedAtLocal": DATE,
        "inputSha256": {"scope": sha(scope_bytes), "overlayBefore": before_hash, "sourceCatalog": sha(SOURCE.read_bytes()), "compiledManifest": sha(COMPILED.read_bytes()), "baseTargetMatrix": sha(MATRIX.read_bytes())},
        "termGapLedgerSha256": sha(EXCEPTIONS.read_bytes()),
        "outputOverlaySha256": None,
        "denominators": baseline_counts,
        "baselineUnresolvedCounts": matrix["dispositionCounts"],
        "addedLinkCounts": dict(link_delta),
        "addedClassMemberLinks": added_class_links,
        "classMemberExcluded": class_exclusions,
        "taxonomyMemberLinks": taxonomy_links,
        "taxonomyExcluded": taxonomy_exclusions,
        "newlyResolvedByBaselineCategory": dict(category_resolved_counts),
        "postLinkDispositionCounts": dict(disposition_counts),
        "postLinkTargetStatusCounts": dict(Counter(x["typedRelationDisposition"] for x in target_representation)),
        "targetRepresentation": target_representation,
        "unresolvedTargetDisposition": unresolved_after,
        "targetRegionMembershipSelection": memberships,
        "targetRegionMembershipStatusCounts": dict(Counter(x["status"] for x in memberships)),
        "routeFailureCount": len(route_failures), "routeFailures": route_failures,
        "termGapCount": len(missing_terms), "termGaps": missing_terms,
        "rightsAndIdentityInvariants": {"newCanonicalHaBindings": 0, "humanReview": "not_performed", "publicRedistribution": "held", "sourceOnlyRowsPreserved": True, "newGeometry": 0, "TA2DenominatorChanged": False},
        "knownQAClaimBoundary": "This file verifies typed target/member selection route relationships and current local surface rows. It is not proof of complete group geometry, a whole-body visual inspection of every target in the browser, publication rights, or human anatomy review.",
    }
    OUT.mkdir(parents=True, exist_ok=True)
    if not args.check:
        if "-T100-target-membership-continuation-2026-09-30-v1" not in overlay["revision"]:
            overlay["revision"] = overlay["revision"] + "-T100-target-membership-continuation-2026-09-30-v1"
        write(OVERLAY, overlay)
        summary["outputOverlaySha256"] = sha(OVERLAY.read_bytes())
        baseline["outputOverlaySha256"] = summary["outputOverlaySha256"]
        write(OUT / "start-baseline.json", baseline)
        write(OUT / "target-membership-plan-and-qa.json", summary)
    else:
        summary["outputOverlaySha256"] = sha(overlay_bytes)
        check_result = {
            "status": "reproducible_current_overlay_matches_recorded_output_hash",
            "currentOverlaySha256": sha(overlay_bytes),
            "recordedOutputOverlaySha256": expected_output,
            "inputScopeSha256": sha(scope_bytes),
            "frozenDenominator": baseline_counts,
            "currentExactTermAndClassLinkCounts": dict(Counter(link["relationKind"] for row in overlay["objects"] for link in row.get("learnerConceptLinks", []))),
            "currentVerifiedTaxonomyMemberLinkCount": sum(1 for row in overlay["objects"] for link in row.get("learnerConceptLinks", []) if link.get("relationKind") == "verified_taxonomy_member"),
            "remainingHistoricalCategoryCounts": dict(Counter(t["disposition"] for t in matrix["targets"] if t["disposition"] in UNRESOLVED)),
            "targetTermEvidenceGapLedgerCount": len(exceptions["termGaps"]),
            "noOverlayRewrite": True,
        }
        write(OUT / "reproducibility-check.json", check_result)
    print(json.dumps({"mode": "check" if args.check else "apply", "addedLinkCounts": summary["addedLinkCounts"],
        "resolvedByCategory": summary["newlyResolvedByBaselineCategory"], "postDisposition": summary["postLinkDispositionCounts"],
        "memberships": summary["targetRegionMembershipStatusCounts"], "routeFailures": summary["routeFailureCount"], "termGaps": summary["termGapCount"],
        "outputOverlaySha256": summary["outputOverlaySha256"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
