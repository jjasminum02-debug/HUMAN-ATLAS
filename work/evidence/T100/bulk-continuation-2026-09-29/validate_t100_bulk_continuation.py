#!/usr/bin/env python3
"""Independent preservation/provenance validator for the T100 bulk continuation."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
BASE_HEAD = "c757c2d9e870c8c403025868024872c1710d56a2"
OVERLAY = "atlas-data/overlays/za-local-integration.json"
T96 = "atlas-data/catalog/target-scope-t96.json"
BASELINE = json.loads((HERE / "start-baseline.json").read_text())


def need(ok: bool, message: str) -> None:
    if not ok:
        raise SystemExit(message)


def load(path: Path):
    return json.loads(path.read_text())


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def no_hanja(value: str) -> bool:
    return not any(0x3400 <= ord(ch) <= 0x9FFF or 0xF900 <= ord(ch) <= 0xFAFF for ch in value)


before = json.loads(subprocess.check_output(["git", "show", f"{BASE_HEAD}:{OVERLAY}"], cwd=ROOT))
after = load(ROOT / OVERLAY)
scope = load(ROOT / T96)
catalog = load(ROOT / "work/evidence/T98/astra-resolution-2026-09-29/source-catalog.json")
compiled = load(ROOT / "atlas-data/source-cache/datasets/za/compiled/manifest.json")
need(len(before["objects"]) == len(after["objects"]) == 960, "source object count changed")
need(after["scope"] == before["scope"] == {"targets": 542, "memberships": 563, "regions": 12}, "whole-body scope drift")
need(len(scope["targets"]) == 542 and scope["denominators"]["productRegionMembershipRows"] == 563, "T96 denominator drift")
need(after["sourceHash"] == before["sourceHash"] and after["datasetRevision"] == before["datasetRevision"], "source identity revision drift")
need(after["targetScopeSha256"] == before["targetScopeSha256"] and after["sourceCatalogSha256"] == before["sourceCatalogSha256"], "frozen inputs changed")
need(after["policy"] == before["policy"], "global source policy changed")
need(after.get("targetRelationEvidence", []) == before.get("targetRelationEvidence", []), "historical relation rows changed")

before_objects = {x["sourceKey"]: x for x in before["objects"]}
after_objects = {x["sourceKey"]: x for x in after["objects"]}
need(set(before_objects) == set(after_objects), "sourceKey inventory changed")
allowed = {"label", "names", "nameSourceIds", "nameEvidence"}
changed = []
for key, old in before_objects.items():
    new = after_objects[key]
    if old == new:
        continue
    changed.append(key)
    need(set(new) - set(old) <= {"nameEvidence"} and set(old) - set(new) == set(), f"object shape changed: {key}")
    need({k: v for k, v in old.items() if k not in allowed} == {k: v for k, v in new.items() if k not in allowed}, f"protected object fields changed: {key}")
    need(new.get("targetId") is not None and new.get("targetId") == old.get("targetId"), f"target identity changed: {key}")
    need(old.get("targetIds") == new.get("targetIds"), f"target relations changed: {key}")
    need(old.get("side") == new.get("side") and old.get("regionIds") == new.get("regionIds"), f"side/region changed: {key}")
    need(old.get("sourceOnly") is True and new.get("sourceOnly") is True, f"sourceOnly changed: {key}")
    need(old.get("humanReview") == new.get("humanReview") == "not_performed", f"human review changed: {key}")
    need(old.get("publicRedistribution") == new.get("publicRedistribution") == "held", f"rights changed: {key}")
    need(old.get("haConceptId") is None and new.get("haConceptId") is None, f"canonical binding added: {key}")
    need(old.get("bounds") == new.get("bounds"), f"geometry/bounds changed: {key}")
    need((new.get("names") or {}).get("koModern"), f"changed object lacks modern name: {key}")
    need(no_hanja(new["names"]["koModern"]), f"Hanja glyph found: {key}")
need(len(changed) == 102, f"expected 102 surface name changes, got {len(changed)}")

before_terms = before.get("targetTerminologyEvidence", [])
after_terms = after.get("targetTerminologyEvidence", [])
need(after_terms[:len(before_terms)] == before_terms, "prior terminology evidence not preserved as prefix")
new_terms = after_terms[len(before_terms):]
need(len(before_terms) == 42 and len(new_terms) == 50 and len(after_terms) == 92, "terminology evidence count drift")
before_sources = before.get("evidenceSources", [])
after_sources = after.get("evidenceSources", [])
need(after_sources[:len(before_sources)] == before_sources, "prior evidence sources not preserved as prefix")
new_sources = after_sources[len(before_sources):]
need(len(before_sources) == 57 and len(new_sources) == 51 and len(after_sources) == 108, "evidence source count drift")
need(not any(x.get("targetRelationEvidence") for x in new_terms), "relation evidence added under term overlay")
need(not any(x.get("learnerBindingCreated") for x in new_terms), "learner binding asserted")
for row in new_terms:
    need(row.get("sourceOnly") is True and row.get("humanReview") == "not_performed" and row.get("publicRedistribution") == "held", f"term policy promoted: {row['targetId']}")
for row in new_sources:
    need(row.get("accessMethod") == "opened_html" and row.get("exactEdition") is None, "opened source/edition falsely claimed")
    need(row.get("openedOriginalSourcePage") is False and row.get("openedOriginalDictionaryRecord") is False, "aggregate source misreported as original")

group_expected = {
    "TA2:1067": 5, "TA2:1104": 27, "TA2:1106": 14, "TA2:1113": 10,
    "TA2:1114": 4, "TA2:1495": 10, "TA2:2192": 15,
}
term_by_target = {x["targetId"]: x for x in new_terms}
need(len(term_by_target) == len(new_terms), "duplicate target terminology evidence was introduced")
for target_id, expected_members in group_expected.items():
    row = term_by_target.get(target_id)
    need(row is not None, f"missing exact group evidence: {target_id}")
    need(row.get("fieldEvidence", {}).get("koModern", {}).get("status") == "evidence_backed", f"group modern term lacks exact evidence: {target_id}")
    need(len(row.get("existingSurface", {}).get("exactSourceObjects", [])) == expected_members, f"exact group member list drift: {target_id}")
    need(row.get("learnerBindingCreated") is False and row.get("canonicalHaConceptId") is None, f"group term created a learner binding: {target_id}")

obs = load(HERE / "source-query-observations.json")
range_row = next((x for x in obs["observations"] if x["query"] == "Rib"), None)
need(range_row is not None and range_row.get("targetEvidenceAttached") is False, "Rib range observation was attached to broader bones-of-thorax target")
need(range_row["observedFields"] == {"englishHeadword": "Ribs(first-twelfth)", "koModern": "갈비뼈(첫째-열두째)", "koTraditional": "늑골"}, "exact rib range observation drift")
thorax_term = term_by_target["TA2:1104"]
need(thorax_term["english"] == "bones of thorax" and thorax_term["names"]["koModern"] == "가슴우리뼈", "thorax target received a semantically narrower label")
need({x["sourceObjectName"] for x in thorax_term["existingSurface"]["exactSourceObjects"]} >= {"Body of sternum", "Manubrium of sternum", "Xiphoid process"}, "bones-of-thorax group omitted exact sternum members")

repetitions = load(HERE / "structure-correspondence.json")
derived = [x for x in repetitions["derivedMemberNames"] if x.get("status") == "applied_exact_group_range_member_composition"]
need(len(derived) == 35, f"expected 35 exact ordinal member compositions, got {len(derived)}")
derived_counts = Counter(x["targetId"] for x in derived)
need(derived_counts == Counter({"TA2:1067": 5, "TA2:1104": 24, "TA2:1495": 6}), f"ordinal composition counts drift: {dict(derived_counts)}")
for row in derived:
    current = after_objects[row["sourceKey"]]
    need(current["names"].get("koModern") == row["koModern"], f"composed member name missing from overlay: {row['sourceKey']}")
    need(current.get("nameEvidence", {}).get("koModern", {}).get("sourceIds") == row["sourceIds"], f"composed member provenance mismatch: {row['sourceKey']}")

no_exact_group_ids = {"TA2:1179": 60, "TA2:1504": 28, "TA2:1514": 2}
for target_id, expected_members in no_exact_group_ids.items():
    row = term_by_target.get(target_id)
    need(row is not None and row.get("names", {}).get("koModern") is None, f"no-exact group was named: {target_id}")
    need(row["fieldEvidence"]["koModern"]["status"] == "missing", f"no-exact group term not held: {target_id}")
    need(len(row["existingSurface"]["exactSourceObjects"]) == expected_members, f"no-exact group source membership drift: {target_id}")

laryngeal = [x for x in after["objects"] if "TA2:2192" in x.get("targetIds", [])]
need(len(laryngeal) == 15 and all(after_objects[x["sourceKey"]]["names"] == before_objects[x["sourceKey"]]["names"] for x in laryngeal), "laryngeal group name leaked onto distinct member names")

need(catalog.get("sourceRevision") == "c7010a903b75a2fd24a13b1c2c4c3546a9223780" and len(catalog["objects"]) == 960, "source catalog changed")
compiled_rows = {x["sourceKey"]: x for x in compiled.get("instances", [])}
need(len(compiled_rows) == 960, "compiled identity/instance set changed")
for key, cat_obj in {x["sourceKey"]: x for x in catalog["objects"]}.items():
    need(cat_obj.get("evaluatedGeometrySha256"), f"missing frozen evaluated geometry hash: {key}")
    need(key in compiled_rows, f"compiled sourceKey missing: {key}")

eligible = [x for x in after["objects"] if x.get("localDisplayEligible")]
need(len(eligible) == 672, "locally display eligible count drift")
named = [x for x in eligible if (x.get("names") or {}).get("koModern")]
unnamed = [x for x in eligible if not (x.get("names") or {}).get("koModern")]
need(len(named) == 262 and len(unnamed) == 410, "post-continuation local-display naming coverage drift")

# Preserve an exhaustive, non-inferential ledger of remaining visible rows.
groups = defaultdict(list)
for row in unnamed:
    key = (row.get("targetId"), row.get("sourceName"), row.get("kind"), row.get("side"), tuple(row.get("regionIds", [])))
    groups[key].append(row["sourceKey"])
backlog = {
    "schemaVersion": 1, "taskId": "T100", "workUnit": "B remaining eligible source surfaces",
    "status": "incomplete", "generatedFromRevision": after["revision"],
    "denominator": {"eligibleSurfaceRows": len(eligible), "namedWithModernKorean": len(named), "unnamedSurfaceRows": len(unnamed), "targets": 542, "memberships": 563, "regions": 12},
    "groupingRule": "Exact existing sourceName/targetId/kind/side/region tuple only; no parent/child, synonym, mirror, or learner binding inferred.",
    "groups": [{"targetId": key[0], "sourceName": key[1], "kind": key[2], "side": key[3], "regionIds": list(key[4]), "surfaceRows": len(values), "sourceKeys": sorted(values), "status": "unreviewed_name_gap"} for key, values in sorted(groups.items(), key=lambda item: (str(item[0][0]), str(item[0][1]), str(item[0][3])))],
    "note": "This is a B work ledger, not a T96 target denominator, source identity crosswalk, or evidence that a Korean term exists."
}
(HERE / "unnamed-surface-backlog.json").write_text(json.dumps(backlog, ensure_ascii=False, indent=2) + "\n")

targets_by_id = {t["id"]: t for t in scope["targets"]}
query_groups = defaultdict(list)
for row in unnamed:
    if row.get("targetId"):
        query_groups[row["targetId"]].append(row["sourceKey"])
query_candidates = []
for target_id, source_keys in sorted(query_groups.items()):
    target = targets_by_id[target_id]
    query_candidates.append({
        "targetId": target_id, "english": target["term"]["english"],
        "latin": target["term"].get("latin"), "semanticKind": target.get("semanticKind"),
        "regionIds": target.get("regionIds", []), "eligibleSourceKeys": sorted(source_keys),
    })
(HERE / "remaining-target-query-candidates.json").write_text(json.dumps({
    "schemaVersion": 1, "taskId": "T100", "workUnit": "B exact headword query candidate set",
    "scopeDenominator": {"targets": 542, "memberships": 563, "regions": 12},
    "distinctPrimaryTargets": len(query_candidates), "candidateEligibleSurfaceRows": len(unnamed),
    "method": "Read exact existing primary targetId and frozen T96 English/Latin label for each unnamed locally displayable object; no lexical crosswalk or new ID is created.",
    "candidates": query_candidates,
}, ensure_ascii=False, indent=2) + "\n")

obs = load(HERE / "source-query-observations.json")
misses = [x for x in obs["observations"] if x["resultStatus"] == "no_exact_named_dictionary_row"]
need(len(misses) == 8, "exact query exception count drift")
fhb_term = next(t for t in new_terms if t["english"].casefold() == "Flexor hallucis brevis".casefold())
fhb_source_target_ids = sorted({tid for source in fhb_term["existingSurface"]["exactSourceObjects"] for tid in source.get("targetIds", []) if tid != fhb_term["targetId"]})
exceptions = {
    "schemaVersion": 1, "taskId": "T100", "workUnit": "C evidence-backed exceptions only",
    "status": "open", "editionPolicy": "KMLE aggregate page displays a KAA terminology section but no exact edition/revision; original KAA records were not opened.",
    "termGaps": [{"query": x["query"], "targetId": next(t["targetId"] for t in new_terms if t["english"].casefold() == x["query"].casefold()), "status": "no_exact_named_dictionary_row", "exactSourceKeySurfaces": len(next(t for t in new_terms if t["english"].casefold() == x["query"].casefold())["existingSurface"]["exactSourceObjects"]), "similarResultNotAccepted": x.get("similarResultNotAccepted"), "reason": "No exact KAA named term row was observed; no fuzzy substitute applied."} for x in misses],
    "fieldConflicts": [{"targetId": "TA2:2650", "english": "Extensor hallucis longus", "field": "koTraditional", "observedButNotApplied": "장무지싱근", "status": "sourceTextConflict_unresolved", "resolution": "Modern term may be shown with evidence. Legacy spelling remains null until a direct authoritative correction is confirmed."}],
    "parentPartBoundaries": [{"targetId": fhb_term["targetId"], "parentEnglish": "Flexor hallucis brevis", "childTargetIds": fhb_source_target_ids, "status": "parentTerm_only", "resolution": "Parent terminology is recorded; medial/lateral head surface rows are not named with the whole-muscle term."}],
    "searchHomonyms": [
        {"targetEnglish": ["Extensor hallucis brevis", "Extensor pollicis brevis"], "koModern": "짧은엄지폄근", "status": "accurate_terms_search_disambiguation_needed", "resolution": "Do not invent differentiating Korean aliases; retain distinct English/Latin and anatomy context."},
        {"targetEnglish": ["Extensor hallucis longus", "Extensor pollicis longus"], "koModern": "긴엄지폄근", "status": "accurate_terms_search_disambiguation_needed", "resolution": "Do not invent differentiating Korean aliases; retain distinct English/Latin and anatomy context."},
        {"targetEnglish": ["Flexor hallucis longus", "Flexor pollicis longus"], "koModern": "긴엄지굽힘근", "status": "accurate_terms_search_disambiguation_needed", "resolution": "Do not invent differentiating Korean aliases; retain distinct English/Latin and anatomy context."},
        {"targetEnglish": ["Depressor anguli oris", "deltoid"], "koModern": "구각하체근(삼각근)", "status": "parenthetical-search-collision_review", "resolution": "The full observed KAA legacy string remains preserved as evidence; never register the parenthetical substring as an alias."}
    ],
    "searchAmbiguities": [
        {"query": "허리뼈", "resultCount": 10, "lumbarVertebraResults": 5, "metatarsalResults": 5, "status": "substring-overlap-observed-in-live-app", "resolution": "The exact query is a meaningful lumbar name but also matches `발허리뼈` and the pre-existing generic `중족골` first/fifth rows. Keep all verified names and IDs; do not invent an alias. Track a future token-boundary search rule separately from this T100 naming evidence."}
    ],
    "historicalMetricDiscrepancy": load(HERE / "candidate-reconciliation.json")["interpretation"],
    "notCountedComplete": {"remainingEligibleUnnamedRows": len(unnamed), "unresolvedExactKaaQueries": len(misses), "unresolvedLegacyFieldConflicts": 1, "unresolvedHomonymSearchCases": 4, "unresolvedSubstringSearchAmbiguities": 1, "wholeBodyCompletion": False}
}
(HERE / "exceptions.json").write_text(json.dumps(exceptions, ensure_ascii=False, indent=2) + "\n")

result = {
    "schemaVersion": 1, "taskId": "T100", "workUnit": "B/C preservation and provenance validation",
    "status": "pass_partial", "checkedAtLocal": "2026-09-29", "baselineHead": BASE_HEAD,
    "checks": {
        "sourceObjectInventory960AndT96Denominators542_563_12": True,
        "only102ExistingSurfaceNameFieldsChanged": True,
        "allOtherObjectFieldsAnd893OtherRowsPreserved": True,
        "prior42Terminology57SourcesAndHistoricalRelationsPreserved": True,
        "exactly50TermRowsAnd51QuerySourcesAdded": True,
        "sevenExactRepeatedGroupTermsAndThreeExplicitNoExactGroupTermsRecorded": True,
        "35OrdinalMemberNamesComposedFromExactKaaRangeAndFrozenMembership": True,
        "noCanonicalBindingsGeometryOrPolicyPromotion": True,
        "sourceCatalogAndCompiledGeometryHashesPresent": True,
        "noHanjaCollected": True,
        "eligibleNamingCoverageReconciled": True,
        "exceptionAndBacklogLedgersGenerated": True,
        "liveSearchAmbiguityRecordedWithoutChangingVerifiedNames": True
    },
    "counts": {"sourceObjects": 960, "eligible": len(eligible), "named": len(named), "unnamed": len(unnamed), "newSurfaceNames": len(changed), "newTerminologyRows": len(new_terms), "newEvidenceSources": len(new_sources), "backlogGroups": len(groups), "gapRows": len(misses)},
    "holds": {"wholeBodyCompletion": False, "sourceOnly": True, "rights": "held", "humanReview": "not_performed", "canonicalBindingsAdded": 0, "geometryChanged": False},
    "remainingWork": ["Continue B evidence-backed naming/repeated-structure processing for 410 eligible unnamed surfaces and additional unnamed exact source groups; this verified continuation is not an exhaustive B pass.", "Resolve eight exact-query term gaps, one legacy-field conflict, four existing homonym cases, and the live 허리뼈 substring ambiguity only with exact source-backed resolution.", "D whole-body visual/selection/performance coverage remains partial; this browser run covers 12 region transitions, 3 viewports, one new-name selection, controls, and search exception behavior."]
}
(HERE / "validation.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
print(json.dumps(result, ensure_ascii=False, indent=2))
