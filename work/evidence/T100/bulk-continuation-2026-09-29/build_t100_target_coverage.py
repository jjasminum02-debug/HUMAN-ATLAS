#!/usr/bin/env python3
"""Build a candidate-only 542-target coverage view without promoting identities."""
from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent


def read(rel: str):
    return json.loads((ROOT / rel).read_text())


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


scope_raw = (ROOT / "atlas-data/catalog/target-scope-t96.json").read_bytes()
catalog_raw = (ROOT / "work/evidence/T98/astra-resolution-2026-09-29/source-catalog.json").read_bytes()
compiled_raw = (ROOT / "atlas-data/source-cache/datasets/za/compiled/manifest.json").read_bytes()
overlay_raw = (ROOT / "atlas-data/overlays/za-local-integration.json").read_bytes()
scope = json.loads(scope_raw)
catalog = json.loads(catalog_raw)
compiled = json.loads(compiled_raw)
overlay = json.loads(overlay_raw)
targets = scope["targets"]
objects = overlay["objects"]
terms = {x["targetId"]: x for x in overlay.get("targetTerminologyEvidence", [])}
compiled_keys = {x["sourceKey"] for x in compiled.get("instances", [])}
by_target = defaultdict(list)
for obj in objects:
    for tid in set([obj.get("targetId"), *(obj.get("targetIds") or [])]):
        if tid:
            by_target[tid].append(obj)

assert len(targets) == 542
assert scope["denominators"]["productRegionMembershipRows"] == 563
assert len(scope["regions"]) == 12
assert len({x["id"] for x in targets}) == 542
assert sum(len(x.get("regionIds", [])) for x in targets) == 563
assert len(objects) == len(compiled_keys) == len(catalog["objects"]) == 960
assert {x["sourceKey"] for x in objects} == compiled_keys

target_rows = []
region = defaultdict(Counter)
for target in targets:
    tid = target["id"]
    candidates = sorted({x["sourceKey"]: x for x in by_target.get(tid, [])}.values(), key=lambda x: x["sourceKey"])
    eligible = [x for x in candidates if x.get("localDisplayEligible")]
    named = [x for x in eligible if (x.get("names") or {}).get("koModern")]
    term = terms.get(tid)
    modern_status = ((term or {}).get("fieldEvidence") or {}).get("koModern", {}).get("status")
    if not term:
        modern_status = "no_target_term_evidence_row"
    row = {
        "targetId": tid,
        "english": target["term"]["english"],
        "latin": target["term"].get("latin"),
        "semanticKind": target.get("semanticKind"),
        "primaryOwner": target.get("primaryOwner"),
        "regionIds": target.get("regionIds", []),
        "targetTermKoModern": (term or {}).get("names", {}).get("koModern"),
        "targetTermKoTraditional": (term or {}).get("names", {}).get("koTraditional"),
        "targetTermKoModernStatus": modern_status,
        "candidateSourceSurfaceCount": len(candidates),
        "locallyDisplayEligibleSurfaceCount": len(eligible),
        "namedLocallyDisplayableSurfaceCount": len(named),
        "unnamedLocallyDisplayableSurfaceCount": len(eligible) - len(named),
        "compiledCandidateSurfaceCount": sum(x["sourceKey"] in compiled_keys for x in candidates),
        "existingBoundSurfaceCount": sum(x.get("haConceptId") is not None for x in candidates),
        "candidateSourceKeys": [x["sourceKey"] for x in candidates],
        "identityMeaning": "Existing overlay targetId/targetIds are source-taxonomy candidates; they are not asserted as verified canonical learner identity by this matrix.",
    }
    if not candidates:
        row["gapClass"] = "no_source_surface_candidate_in_frozen_ZA_package"
    elif len(eligible) < len(candidates):
        row["gapClass"] = "some_source_surfaces_remain_held_or_not_locally_eligible"
    elif len(named) < len(eligible):
        row["gapClass"] = "eligible_source_surface_name_gap"
    elif modern_status != "evidence_backed":
        row["gapClass"] = "surface_names_exist_but_target_term_or_identity_evidence_not_closed"
    else:
        row["gapClass"] = "candidate_surfaces_and_target_term_evidence_present_identity_still_separate"
    target_rows.append(row)
    for region_id in target.get("regionIds", []):
        c = region[region_id]
        c["targetMemberships"] += 1
        c["targetsWithCandidateSurface"] += bool(candidates)
        c["targetsWithoutCandidateSurface"] += not bool(candidates)
        c["targetTermsWithModernEvidence"] += modern_status == "evidence_backed"
        c["eligibleSurfaceRows"] += len(eligible)
        c["namedEligibleSurfaceRows"] += len(named)
        c["unnamedEligibleSurfaceRows"] += len(eligible) - len(named)

eligible_all = [x for x in objects if x.get("localDisplayEligible")]
named_all = [x for x in eligible_all if (x.get("names") or {}).get("koModern")]
held_accessories = [x for x in objects if not x.get("localDisplayEligible")]
assert len(eligible_all) == 672 and len(named_all) == 446 and len(held_accessories) == 288
assert all(x.get("kind") == "accessory" and x.get("targetId") is None and not x.get("targetIds")
           and "accessory-or-original-hidden-or-exception" in x.get("hardHoldReasons", [])
           for x in held_accessories)

matrix = {
    "schemaVersion": 1,
    "taskId": "T100",
    "workUnit": "C/D current whole-body candidate coverage snapshot",
    "status": "partial_not_whole_body_complete",
    "inputs": {
        "targetScopeSha256": sha(scope_raw),
        "sourceCatalogSha256": sha(catalog_raw),
        "compiledManifestSha256": sha(compiled_raw),
        "currentOverlaySha256": sha(overlay_raw),
        "denominators": {"targets": 542, "regionMemberships": 563, "regions": 12, "sourceObjects": 960},
    },
    "candidateSemantics": "A candidate surface relation is counted from the existing overlay targetId/targetIds. This is not proof of exact T96 canonical identity, learner binding, or human approval.",
    "globalCounts": {
        "eligibleSurfaceRows": len(eligible_all),
        "eligibleRowsWithModernKorean": len(named_all),
        "eligibleRowsWithoutModernKorean": len(eligible_all) - len(named_all),
        "uniqueExistingHaBoundSurfaceRows": sum(x.get("haConceptId") is not None for x in objects),
        "targetsWithAnySourceSurfaceCandidate": sum(bool(by_target.get(t["id"])) for t in targets),
        "targetsWithoutAnySourceSurfaceCandidate": sum(not bool(by_target.get(t["id"])) for t in targets),
        "targetTermRowsWithModernEvidence": sum(((terms.get(t["id"]) or {}).get("fieldEvidence") or {}).get("koModern", {}).get("status") == "evidence_backed" for t in targets),
        "sourceObjectsHeldOutsideLocalDisplay": len(held_accessories),
        "heldObjectsDisposition": "All 288 are source kind accessory, have no T96 targetId/targetIds, remain defaultHidden/inspection-ineligible/source-only/rights-held under the inherited accessory-or-original-hidden-or-exception hold. They are excluded from the 542 muscle/bone target denominator and were not promoted.",
    },
    "regionCoverage": {k: dict(v) for k, v in sorted(region.items())},
    "targets": target_rows,
    "holds": {"sourceOnly": True, "publicRedistribution": "held", "humanReview": "not_performed", "canonicalBindingsAdded": 0, "geometryChanged": False, "wholeBodyComplete": False},
}
assert len(matrix["targets"]) == matrix["inputs"]["denominators"]["targets"]
assert sum(row["targetMemberships"] for row in matrix["regionCoverage"].values()) == 563
assert len(matrix["regionCoverage"]) == matrix["inputs"]["denominators"]["regions"]
(HERE / "target-coverage-snapshot.json").write_text(json.dumps(matrix, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"status": matrix["status"], "globalCounts": matrix["globalCounts"], "regionCount": len(matrix["regionCoverage"]), "targetRows": len(matrix["targets"])}, ensure_ascii=False, indent=2))
