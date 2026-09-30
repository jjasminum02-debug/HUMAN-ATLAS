#!/usr/bin/env python3
"""Rebuild and validate the T100 continuation evidence from frozen local inputs.

This script does not edit anatomy data, names, geometry, runtime projection, or UI.
It only writes evidence files beneath this directory.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import unicodedata
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent


def read(rel: str):
    return json.loads((ROOT / rel).read_text())


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(rel: str) -> str:
    return digest((ROOT / rel).read_bytes())


def write(name: str, value) -> None:
    (HERE / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def norm(value: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKC", value).casefold() if c.isalnum())


BASELINE = read("work/evidence/T100/continuation-2026-09-30/start-baseline.json")
SCOPE_REL = "atlas-data/catalog/target-scope-t96.json"
OVERLAY_REL = "atlas-data/overlays/za-local-integration.json"
CATALOG_REL = "work/evidence/T98/astra-resolution-2026-09-29/source-catalog.json"
COMPILED_REL = "atlas-data/source-cache/datasets/za/compiled/manifest.json"
GAP_REL = "work/evidence/T100/semantic-relations-2026-09-30/target-gap-classification.json"
SEMANTIC_REL = "work/evidence/T100/semantic-relations-2026-09-30/semantic-validation.json"
EXCEPTIONS_REL = "work/evidence/T100/bulk-continuation-2026-09-29/exceptions.json"
INPUTS = [SCOPE_REL, OVERLAY_REL, CATALOG_REL, COMPILED_REL, GAP_REL, SEMANTIC_REL, EXCEPTIONS_REL]

scope_raw = (ROOT / SCOPE_REL).read_bytes()
overlay_raw = (ROOT / OVERLAY_REL).read_bytes()
catalog_raw = (ROOT / CATALOG_REL).read_bytes()
compiled_raw = (ROOT / COMPILED_REL).read_bytes()
scope = json.loads(scope_raw)
overlay = json.loads(overlay_raw)
catalog = json.loads(catalog_raw)
compiled = json.loads(compiled_raw)
gap = read(GAP_REL)
semantic_validation = read(SEMANTIC_REL)
exceptions = read(EXCEPTIONS_REL)
targets = scope["targets"]
objects = overlay["objects"]
compiled_instances = {x["sourceKey"]: x for x in compiled["instances"]}
catalog_objects = {x["sourceKey"]: x for x in catalog["objects"]}
overlay_objects = {x["sourceKey"]: x for x in objects}
term_evidence = {x["targetId"]: x for x in overlay.get("targetTerminologyEvidence", [])}

assert len(targets) == 542
assert sum(len(t.get("regionIds", [])) for t in targets) == 563
assert len(scope["regions"]) == 12
assert len(objects) == len(compiled_instances) == len(catalog_objects) == 960
assert set(overlay_objects) == set(compiled_instances) == set(catalog_objects)

# Existing Korean name evidence audit only. No source search is repeated here.
eligible = [x for x in objects if x.get("localDisplayEligible")]
named = [x for x in eligible if (x.get("names") or {}).get("koModern")]
unnamed = [x for x in eligible if not (x.get("names") or {}).get("koModern")]
evidence_terms = {norm(x.get("term", "")) for x in overlay.get("evidenceSources", []) if x.get("term")}
exact_term_matches = []
for obj in unnamed:
    lexical_forms = [obj.get("sourceName", ""), obj.get("label", ""), (obj.get("names") or {}).get("en", "")]
    exact = []
    for form in lexical_forms:
        form = re.sub(r"\.[lr]$", "", form.strip()).strip("()")
        if norm(form) and norm(form) in evidence_terms:
            exact.append(form)
    if exact:
        exact_term_matches.append({"sourceKey": obj["sourceKey"], "exactForms": sorted(set(exact))})
assert len(eligible) == 672 and len(named) == 513 and len(unnamed) == 159
assert len(overlay.get("evidenceSources", [])) == 394
assert not exact_term_matches
assert len(overlay.get("targetTerminologyEvidence", [])) >= 75
term_gaps = exceptions["termGaps"]

name_audit = {
    "schemaVersion": 1,
    "taskId": "T100",
    "workUnit": "existing-evidence exact audit for remaining Korean-name gaps",
    "capturedAtLocal": "2026-09-30",
    "inputs": {rel: sha_file(rel) for rel in [OVERLAY_REL, SCOPE_REL, EXCEPTIONS_REL]},
    "counts": {
        "sourceObjects": len(objects),
        "localDisplayEligible": len(eligible),
        "eligibleWithModernKorean": len(named),
        "eligibleMissingModernKorean": len(unnamed),
        "existingFieldEvidenceSources": len(overlay.get("evidenceSources", [])),
        "exactNormalizedEnglishTermMatchesForMissingRows": len(exact_term_matches),
        "frozenTargetTermGaps": len(term_gaps),
    },
    "method": "Read-only exact equality against term fields already present in the overlay. NFKC + casefold + alphanumeric normalization; removed only a terminal .l/.r and source-name wrapper parentheses. This is a local evidence audit, not a new web search or fuzzy match.",
    "fieldEvidencePolicy": "Search indexes/snippets do not establish an opened source record. Existing KMLE/KAA/KLI provenance and edition visibility remain field-specific. No new name was applied because no existing field source exactly matches any of these 159 source labels.",
    "newSourceQueriesPerformed": 0,
    "appliedNames": 0,
    "exactMatches": exact_term_matches,
    "remainingTermGapTargetIds": sorted(x["targetId"] for x in term_gaps),
    "decision": "Keep 159 eligible surface name fields and 75 target terminology gaps unresolved; do not fill by resemblance or repeat frozen no-result searches.",
}
write("naming-audit.json", name_audit)

# Whole-body candidate inventory; candidate relations are explicitly not anatomy approval.
direct_by_target = defaultdict(dict)
links_by_target = defaultdict(list)
for obj in objects:
    for target_id in set([obj.get("targetId"), *(obj.get("targetIds") or [])]):
        if target_id:
            direct_by_target[target_id][obj["sourceKey"]] = obj
    for link in obj.get("learnerConceptLinks", []):
        for target_id in link.get("targetIds", []):
            links_by_target[target_id].append({"sourceKey": obj["sourceKey"], "object": obj, "link": link})

per_target = []
region_counts = defaultdict(Counter)
targets_with_direct = targets_with_lexical_link = targets_with_evaluated_source_mesh = 0
direct_rows = link_rows = evaluated_rows = 0
for target in targets:
    target_id = target["id"]
    direct = list(direct_by_target.get(target_id, {}).values())
    links = links_by_target.get(target_id, [])
    all_objects = {x["sourceKey"]: x for x in direct}
    for item in links:
        all_objects[item["sourceKey"]] = item["object"]
    evaluated = []
    for source_key, obj in sorted(all_objects.items()):
        instance = compiled_instances[source_key]
        if instance.get("evaluatedGeometrySha256"):
            resource_ids = {lod.get("resource") for lod in (instance.get("lods") or {}).values() if lod.get("resource")}
            evaluated.append({"sourceKey": source_key, "side": obj.get("side"), "kind": obj.get("kind"), "regionIds": obj.get("regionIds", []), "evaluatedGeometrySha256": instance["evaluatedGeometrySha256"], "compiledChunkIds": [c["id"] for c in compiled.get("chunks", []) if resource_ids.intersection(c.get("resources", []))]})
    target_links = [{"sourceKey": x["sourceKey"], "relationKind": x["link"].get("relationKind"), "targetIds": x["link"].get("targetIds", []), "identityStatus": x["link"].get("identityStatus"), "canonicalConceptId": x["object"].get("haConceptId"), "humanReview": x["link"].get("humanReview")} for x in links]
    target_ko = term_evidence.get(target_id, {})
    modern_ev = (target_ko.get("fieldEvidence") or {}).get("koModern", {})
    target_row = {
        "targetId": target_id,
        "english": target["term"]["english"],
        "latin": target["term"].get("latin"),
        "semanticKind": target.get("semanticKind"),
        "regionIds": target.get("regionIds", []),
        "regionMembershipCount": len(target.get("regionIds", [])),
        "directOverlaySourceCandidates": sorted(x["sourceKey"] for x in direct),
        "learnerConceptLinks": target_links,
        "evaluatedSourceMeshes": evaluated,
        "evaluatedSourceMeshCount": len(evaluated),
        "targetTermKoModern": target_ko.get("names", {}).get("koModern"),
        "targetTermKoModernEvidenceStatus": modern_ev.get("status", "no_target_term_evidence_row"),
        "learnerSelectionBrowserQA": "verified_route_card_side_and_focus" if target_id in {"TA2:2198", "TA2:2200", "TA2:2201", "TA2:2204", "TA2:2406", "TA2:2487"} else "not_run_for_this_target",
        "coverageInterpretation": "Source/candidate inventory only. A source relation or evaluated source mesh is not target-specific geometry proof, canonical learner identity, human review, or full browser selection QA.",
    }
    per_target.append(target_row)
    direct_rows += len(direct)
    link_rows += len(links)
    evaluated_rows += len(evaluated)
    targets_with_direct += bool(direct)
    targets_with_lexical_link += bool(links)
    targets_with_evaluated_source_mesh += bool(evaluated)
    for region_id in target.get("regionIds", []):
        c = region_counts[region_id]
        c["targetMemberships"] += 1
        c["targetsWithDirectOverlayCandidate"] += bool(direct)
        c["targetsWithLearnerConceptLink"] += bool(links)
        c["targetsWithEvaluatedCandidateOrLinkedMesh"] += bool(evaluated)
        c["unresolvedModernKoreanTerm"] += modern_ev.get("status") != "evidence_backed"

assert sum(x["regionMembershipCount"] for x in per_target) == 563
assert len(per_target) == 542 and len(region_counts) == 12

coverage = {
    "schemaVersion": 1,
    "taskId": "T100",
    "workUnit": "overlay-aware target/source/mesh candidate inventory",
    "status": "partial_not_visual_coverage_acceptance",
    "capturedAtLocal": "2026-09-30",
    "inputs": {rel: sha_file(rel) for rel in [SCOPE_REL, OVERLAY_REL, CATALOG_REL, COMPILED_REL]},
    "denominators": {"uniqueTargets": len(per_target), "productRegionMemberships": sum(x["regionMembershipCount"] for x in per_target), "regions": len(region_counts)},
    "counts": {
        "targetsWithDirectOverlayCandidate": targets_with_direct,
        "targetsWithoutDirectOverlayCandidate": len(per_target) - targets_with_direct,
        "targetsWithAnyLearnerConceptLinkRelation": targets_with_lexical_link,
        "targetsWithAtLeastOneEvaluatedCandidateOrLinkedSourceMesh": targets_with_evaluated_source_mesh,
        "directOverlaySourceRelationRows": direct_rows,
        "learnerConceptLinkRows": link_rows,
        "evaluatedMeshRowsAcrossDirectOrLinkedSources": evaluated_rows,
        "existingHaCanonicalBoundObjects": sum(x.get("haConceptId") is not None for x in objects),
        "visualSelectionQAForAllTargets": False,
    },
    "regionCounts": {key: dict(value) for key, value in sorted(region_counts.items())},
    "interpretation": "This joins existing overlay candidate relations and learnerConceptLinks to evaluated source instances. It does not prove every target's exact surface, membership completeness, visual picking, anatomical identity, or usability. Region counts are candidate inventory only. The frozen T96 denominator remains unchanged.",
    "policy": {"sourceOnlyNewWork": True, "publicRedistribution": "held", "humanReview": "not_performed", "canonicalBindingsAdded": 0, "geometryChanged": False},
    "targets": per_target,
}
write("overlay-aware-542-coverage.json", coverage)

# Reconcile, but do not erase, the historical 163 candidate-free classifications.
candidate_free_rows = []
for historical in gap["targets"]:
    target_id = historical["targetId"]
    new_links = []
    for item in links_by_target.get(target_id, []):
        link = item["link"]
        if link.get("relationKind") == "normalized_exact_target_term":
            instance = compiled_instances[item["sourceKey"]]
            new_links.append({
                "sourceKey": item["sourceKey"],
                "sourceName": item["object"].get("sourceName"),
                "side": item["object"].get("side"),
                "regionIds": item["object"].get("regionIds", []),
                "relationKind": link.get("relationKind"),
                "identityStatus": link.get("identityStatus"),
                "targetTermMatches": link.get("targetTermMatches", []),
                "evidenceIds": link.get("evidenceIds", []),
                "canonicalConceptId": item["object"].get("haConceptId"),
                "evaluatedGeometrySha256": instance.get("evaluatedGeometrySha256"),
                "targetSpecificGeometryValidated": False,
                "humanReview": link.get("humanReview"),
            })
    candidate_free_rows.append({
        "targetId": target_id,
        "english": historical["english"],
        "historicalCategory": historical["category"],
        "historicalGeometryAssessment": historical["geometryAssessment"],
        "currentExactNormalizedTargetTermLinks": sorted(new_links, key=lambda x: (x["side"] or "", x["sourceKey"])),
        "currentSourceEvaluatedGeometryCount": len([x for x in new_links if x.get("evaluatedGeometrySha256")]),
        "disposition": "exact_source_object_and_evaluated_mesh_available_but_target_specific_anatomical_extent_unvalidated" if new_links else historical["category"],
        "canonicalBindingAdded": False,
        "humanReview": "not_performed",
    })
counts = Counter(x["historicalCategory"] for x in candidate_free_rows)
six = [x for x in candidate_free_rows if x["historicalCategory"] == "exact_source_label_observation_identity_crosswalk_needed"]
assert counts == Counter(gap["categoryCounts"])
assert len(six) == 6 and all(len(x["currentExactNormalizedTargetTermLinks"]) == 2 for x in six)
assert all({l["side"] for l in x["currentExactNormalizedTargetTermLinks"]} == {"left", "right"} for x in six)
assert all(l["evaluatedGeometrySha256"] and l["canonicalConceptId"] is None and l["humanReview"] == "not_performed" for x in six for l in x["currentExactNormalizedTargetTermLinks"])
reconciliation = {
    "schemaVersion": 1,
    "taskId": "T100",
    "workUnit": "candidate-free 163 overlay-aware reconciliation",
    "capturedAtLocal": "2026-09-30",
    "historicalDenominator": 163,
    "historicalCategoryCountsPreserved": dict(counts),
    "currentOverlayFinding": "All six exact source-label observations already have left/right normalized_exact_target_term learnerConceptLinks and evaluated source geometry in the current overlay/compiled dataset. This supplements the historical no-top-level-candidate classification; it does not convert the target to a canonical or human-reviewed binding and does not prove target-specific surface extent.",
    "supplementalCounts": {
        "exactTermLinkedTargets": len(six),
        "pairedSourceSurfaceObjects": sum(len(x["currentExactNormalizedTargetTermLinks"]) for x in six),
        "evaluatedSourceMeshes": sum(x["currentSourceEvaluatedGeometryCount"] for x in six),
        "remainingDescendantRepresentationTargets": counts["descendant_surface_representation_present_target_specific_surface_unresolved"],
        "remainingAncestorOrGroupRepresentationTargets": counts["ancestor_surface_representation_present_target_specific_surface_unresolved"],
        "remainingFrozenPackageHierarchyNonobservations": counts["no_exact_descendant_or_ancestor_surface_evidence_in_frozen_package"],
        "confirmedSourceWideGeometryAbsence": 0,
        "targetSpecificGeometryExtentValidated": 0,
    },
    "holds": {"sourceOnly": True, "publicRedistribution": "held", "humanReview": "not_performed", "canonicalBindingsAdded": 0},
    "targets": candidate_free_rows,
}
write("candidate-free-163-reconciliation.json", reconciliation)

# Browser/active-scene measurements were recorded from the actual local learner session.
browser_targets = [
    ("TA2:2198", "lateral cricoarytenoid muscle", "ZA-c7010a9-fffbd633a2b005f7f0f8b636", "ZA-c7010a9-dff877ef6483ee8c6e97f183", "6dcd9ea5-3349-4b7e-9b57-6510d36f68f7", [-0.0095178504, 1.4746411318, 0.0041305757], 140, 126259),
    ("TA2:2200", "external part of thyroarytenoid muscle", "ZA-c7010a9-8dd74a625b4d0ea102d2b057", "ZA-c7010a9-6a1b4056d714712f6bea1db9", "b669f46a-62d1-47ee-af2f-773f5312ca42", [-0.0053797942, 1.4757414519, 0.0152351095], 149, 143707),
    ("TA2:2201", "thyroepiglottic part of thyroarytenoid muscle", "ZA-c7010a9-e969768f61022bf07e8e5b5e", "ZA-c7010a9-54ef90215ecab2d6beebbabc", "5cd3d945-7231-4ca6-8b17-e2ed129a358a", [-0.0045342552, 1.4903392827, 0.0188657318], 154, 132467),
    ("TA2:2204", "aryepiglottic part of oblique arytenoid muscle", "ZA-c7010a9-539e1a45e0e562f3ee8d92b7", "ZA-c7010a9-9974b47ca8a42000b39b253e", "17bf5419-60b9-4036-80f2-c59084c2218b", [-0.0069206782, 1.4930708920, 0.0131034321], 148, 117949),
    ("TA2:2406", "puboanalis muscle", "ZA-c7010a9-9f38f285dabec98662d9ad76", "ZA-c7010a9-15d98951b62ec44af55da39d", "479d0255-1f3c-4922-a50c-c570cc27f160", [-0.0151680202, 0.8251918384, -0.0215422621], 103, 114611),
    ("TA2:2487", "humeroulnar head of flexor digitorum superficialis", "ZA-c7010a9-9e5c3efa530741ae8f0595ec", "ZA-c7010a9-f04b81d9566c227fb9805995", "2ba08432-f1c9-44d3-b8f2-49ca7b3d20f8", [-0.2499703337, 0.9169828519, 0.0167526193], 297, 293351),
]
browser = {
    "schemaVersion": 1,
    "taskId": "T100",
    "capturedAtLocal": "2026-09-30",
    "browser": "Codex in-app browser; existing local Vite session http://127.0.0.1:5173/",
    "method": "For each left/right source pair, open the left exact source route, activate the right-side control, then invoke the existing selected-region camera focus. Verify route/source key, card side, visible single canvas, pending/failure state, and shared-scene camera/render telemetry.",
    "selectionChecks": [
        {"targetId": tid, "english": english, "leftSourceKey": left, "rightSourceKey": right, "routePattern": f"/?source={left} -> right-side control -> ?source={right}", "selectedSourceKeyMatchedRouteAndCard": True, "cardSide": "오른쪽", "selectedFocusActivated": True, "singleCanvas": True, "pending": 0, "failed": 0, "sharedSceneId": scene, "selectedCameraTarget": target, "cumulativeRendererCallsAfterFocus": calls, "cumulativeTrianglesAfterFocus": tris}
        for tid, english, left, right, scene, target, calls, tris in browser_targets
    ],
    "visualObservation": "A current browser capture visibly showed the selected right forearm source surface highlighted teal, with the right-side card and same shared scene. Other five target checks recorded route/card/side/focus/canvas state and renderer camera targets; a persistent screenshot per target was not saved.",
    "console": {"errors": [], "warnings": [], "captureMethod": "available browser console log API after the six runs"},
    "scopeLimit": "6 of 542 unique targets and 12 of 563 target-region memberships; this is not full visual selection coverage or human anatomy review.",
}
write("browser-selection-validation.json", browser)

performance = {
    "schemaVersion": 1,
    "taskId": "T100",
    "capturedAtLocal": "2026-09-30",
    "measurementContext": {"selectedSourceKey": browser_targets[-1][3], "canvasCssPixels": [1280, 460], "canvasBackingPixels": [2240, 805], "devicePixelRatio": 1.75, "oneCanvas": True, "visibleAndLoadedSourceMeshes": 672, "pending": 0, "failed": 0, "resourceQueueBytes": 16848420},
    "sharedRendererTelemetry": {"cumulativeRenderCalls": 297, "triangles": 293351, "uniqueGeometries": 399, "visibleMeshes": 672, "materials": 3, "geometryBuffersBytes": 7014222, "geometryBuffersMiB": round(7014222 / 1024 / 1024, 3), "renderCpuSampleCount": 9, "renderCpuMsP50": 0.8, "renderCpuMsP95": 8.7, "rafIntervalSampleCount": 240, "rafIntervalMsP50": 16.7, "rafIntervalMsP95": 17.4},
    "interpretationAndLimits": [
        "The animation-frame callback interval is not rendered FPS: the controller renders on demand, so this run did not measure sustained FPS under a camera-motion workload.",
        "GPU VRAM and GPU time were unavailable through the browser evaluation surface; no WebGL timer query or GPU memory claim is made.",
        "geometryBuffersBytes is retained typed-array CPU geometry storage, not total JavaScript heap, browser process memory, or GPU VRAM.",
        "resourceQueueBytes is the dataset adapter's loaded resource byte total, not resident GPU memory.",
        "The legacy controller selection telemetry is empty in dataset mode; dataset selection was verified separately through data-dataset and the visible selected card. Shared-scene renderer telemetry above still reads the active renderer.",
    ],
    "acceptance": "partial; actual whole-body motion FPS and GPU/total-memory budgets remain unmeasured.",
}
write("active-scene-performance.json", performance)

def git(*args, cwd=ROOT):
    return subprocess.check_output(["git", *args], cwd=cwd, text=True).strip()

def tree_hash(rel: str):
    path = ROOT / rel
    if path.is_file():
        return digest(path.read_bytes())
    if path.is_dir():
        h = hashlib.sha256()
        for item in sorted(x for x in path.rglob("*") if x.is_file()):
            name = item.relative_to(ROOT).as_posix().encode()
            h.update(len(name).to_bytes(4, "big")); h.update(name); h.update(bytes.fromhex(digest(item.read_bytes())))
        return h.hexdigest()
    return None

status = subprocess.check_output(["git", "status", "--porcelain=v1", "-z"], cwd=ROOT).decode("utf-8", "surrogateescape")
current_paths = {}
for entry in status.split("\0"):
    if entry:
        current_paths[entry[3:]] = entry[:2]
changed_preexisting = []
for row in BASELINE["preexistingWorktree"]["entries"]:
    current = tree_hash(row["path"])
    if current != row.get("treeSha256"):
        changed_preexisting.append({"path": row["path"], "before": row.get("treeSha256"), "after": current})
opensim_status = git("status", "--porcelain=v1", cwd=ROOT / "OpenSim_Models")
opensim_head = git("rev-parse", "HEAD", cwd=ROOT / "OpenSim_Models")
protected_after = {rel: sha_file(rel) for rel in INPUTS}
preservation = {
    "schemaVersion": 1,
    "taskId": "T100",
    "baselineHead": BASELINE["head"],
    "baselinePreexistingEntryCount": len(BASELINE["preexistingWorktree"]["entries"]),
    "preexistingWorktreeFilesChangedByThisContinuation": changed_preexisting,
    "protectedInputHashesAfter": protected_after,
    "protectedInputsUnchanged": all(protected_after[p] == BASELINE["protectedInputHashes"].get(p) for p in protected_after),
    "openSimModels": {"baselineHead": BASELINE["openSimModels"]["head"], "currentHead": opensim_head, "currentStatus": opensim_status, "unchangedAndClean": opensim_head == BASELINE["openSimModels"]["head"] and not opensim_status},
    "userWipPreserved": not changed_preexisting,
    "taskOwnedAnatomyDataChanged": False,
    "sourceOnlyNewWorkPolicy": "true; this continuation added no source objects or learner bindings",
    "existingSourceOnlyFlagCounts": dict(Counter(str(x.get("sourceOnly")).lower() for x in objects)),
    "publicRedistribution": overlay["policy"]["publicRedistribution"],
    "humanReview": overlay["policy"]["humanReview"],
    "existingCanonicalHaBindings": sum(x.get("haConceptId") is not None for x in objects),
    "frozenT96Denominators": {"targets": len(targets), "memberships": sum(len(t.get("regionIds", [])) for t in targets), "regions": len(scope["regions"])},
}
write("preservation-after.json", preservation)

validation = {
    "schemaVersion": 1,
    "taskId": "T100",
    "status": "pass_partial",
    "checks": {
        "T96_542_563_12_denominator": len(targets) == 542 and sum(len(t.get("regionIds", [])) for t in targets) == 563 and len(scope["regions"]) == 12,
        "159_eligible_name_gaps_retained": len(unnamed) == 159,
        "75_target_term_gaps_retained": len(term_gaps) == 75,
        "no_names_applied_without_existing_exact_field_evidence": len(exact_term_matches) == 0,
        "163_historical_candidate_free_classes_preserved": len(candidate_free_rows) == 163 and dict(counts) == gap["categoryCounts"],
        "six_exact_term_links_have_bilateral_evaluated_source_meshes": len(six) == 6 and all(len(x["currentExactNormalizedTargetTermLinks"]) == 2 and x["currentSourceEvaluatedGeometryCount"] == 2 for x in six),
        "zero_canonical_binding_or_human_review_promotion": all(x.get("haConceptId") is None or x.get("humanReview") == "not_performed" for x in objects),
        "source_rights_and_review_holds_retained": overlay["policy"].get("localOnly") is True and overlay["policy"].get("publicRedistribution") == "held" and overlay["policy"].get("humanReview") == "not_performed" and sum(x.get("sourceOnly") is True for x in objects) == 830,
        "existing_130_HA_bindings_retained": sum(x.get("haConceptId") is not None for x in objects) == 130,
        "preservation_check_passes": preservation["userWipPreserved"] and preservation["protectedInputsUnchanged"] and preservation["openSimModels"]["unchangedAndClean"],
        "six_browser_routes_card_sides_focus_canvas_and_resource_states": len(browser["selectionChecks"]) == 6 and all(x["selectedSourceKeyMatchedRouteAndCard"] and x["cardSide"] == "오른쪽" and x["selectedFocusActivated"] and x["singleCanvas"] and x["pending"] == 0 and x["failed"] == 0 for x in browser["selectionChecks"]),
        "performance_fps_gpu_total_memory_limitations_explicit": performance["acceptance"].startswith("partial") and len(performance["interpretationAndLimits"]) >= 5,
    },
    "openGates": ["159 modern Korean names for locally eligible surfaces", "75 target terminology gaps", "target-specific identity/extent for the remaining candidate-free and grouped surfaces", "selection and visual verification for all 542 targets and 563 memberships", "sustained active-scene FPS during motion, GPU time/VRAM and total-memory measurement"],
    "inputHashes": {rel: sha_file(rel) for rel in INPUTS},
}
assert all(validation["checks"].values()), json.dumps(validation["checks"], indent=2)
write("validation.json", validation)

print(json.dumps({"status": validation["status"], "counts": name_audit["counts"], "coverage": coverage["counts"], "historical163": reconciliation["supplementalCounts"], "allChecks": all(validation["checks"].values())}, ensure_ascii=False, indent=2))
