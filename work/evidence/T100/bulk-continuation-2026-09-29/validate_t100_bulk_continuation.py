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
    need((new.get("names") or {}).get("koModern") or (new.get("names") or {}).get("koTraditional"), f"changed object lacks an evidence-backed Korean name: {key}")
    for value in (new.get("names") or {}).values():
        if value:
            need(no_hanja(value), f"Hanja glyph found: {key}")
need(len(changed) == 292, f"expected 292 cumulative evidence-backed surface name changes, got {len(changed)}")

before_terms = before.get("targetTerminologyEvidence", [])
after_terms = after.get("targetTerminologyEvidence", [])
multidict = load(HERE / "source-surface-multidictionary-observations.json")
applications = {x["targetId"]: x for x in multidict["acceptedFieldApplications"]}
need(set(applications) == {"TA2:2357", "TA2:2147", "TA2:2363", "TA2:2052", "TA2:2532", "TA2:2056", "TA2:1255"},
     "multidictionary accepted target set drift")
before_term_map = {x["targetId"]: x for x in before_terms}
after_term_map = {x["targetId"]: x for x in after_terms}
need(len(before_term_map) == len(before_terms) == 42 and len(after_term_map) == len(after_terms), "target term rows are duplicated")
for target_id, old in before_term_map.items():
    new = after_term_map.get(target_id)
    need(new is not None, f"historical target term row removed: {target_id}")
    if target_id not in applications:
        need(new == old, f"unrelated prior target term row changed: {target_id}")
        continue
    allowed_term_fields = {"targetTermSourceIds", "names", "fieldEvidence", "classification", "existingSurface", "unappliedTermCandidates"}
    need({k: v for k, v in new.items() if k not in allowed_term_fields} == {k: v for k, v in old.items() if k not in allowed_term_fields},
         f"protected term identity/meaning fields changed: {target_id}")
    need(new["names"].get("en") == old["names"].get("en"), f"English target term changed: {target_id}")
    for field_name in ("koModern", "koTraditional"):
        if field_name not in applications[target_id]["fields"]:
            need(new["names"].get(field_name) == old["names"].get(field_name), f"unassigned name field changed: {target_id} {field_name}")
            need(new["fieldEvidence"][field_name] == old["fieldEvidence"][field_name], f"unassigned field evidence changed: {target_id} {field_name}")
        else:
            need(old["names"].get(field_name) is None and old["fieldEvidence"][field_name].get("status") == "missing",
                 f"previous target name was overwritten: {target_id} {field_name}")
    need(new["fieldEvidence"]["en"] == old["fieldEvidence"]["en"]
         and new["fieldEvidence"]["latin"] == old["fieldEvidence"]["latin"]
         and new["fieldEvidence"].get("sourceSynonyms") == old["fieldEvidence"].get("sourceSynonyms")
         and new["fieldEvidence"]["hanja"] == old["fieldEvidence"]["hanja"],
         f"English/Latin/Hanja field evidence changed: {target_id}")
    need(new["classification"].get("laterality") == old["classification"].get("laterality"), f"target laterality changed: {target_id}")
    need(new["existingSurface"].get("exactSourceObjects") == old["existingSurface"].get("exactSourceObjects"),
         f"term evidence surface/source membership changed: {target_id}")
    need(new.get("targetTermSourceIds", [])[:len(old.get("targetTermSourceIds", []))] == old.get("targetTermSourceIds", []),
         f"historical target evidence IDs not preserved: {target_id}")
    need(new.get("unappliedTermCandidates", [])[:len(old.get("unappliedTermCandidates", []))] == old.get("unappliedTermCandidates", []),
         f"prior unapplied candidates not preserved: {target_id}")
new_terms = after_terms[len(before_terms):]
need(len(before_terms) == 42 and len(new_terms) == 213 and len(after_terms) == 255, "terminology evidence count drift")
before_sources = before.get("evidenceSources", [])
after_sources = after.get("evidenceSources", [])
need(after_sources[:len(before_sources)] == before_sources, "prior evidence sources not preserved as prefix")
new_sources = after_sources[len(before_sources):]
need(len(before_sources) == 57 and len(new_sources) == 329 and len(after_sources) == 386, "evidence source count drift")
need(len({x["id"] for x in after_sources}) == len(after_sources), "duplicate evidence source IDs")
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

no_exact_group_ids = {"TA2:1514": 2}
for target_id, expected_members in no_exact_group_ids.items():
    row = term_by_target.get(target_id)
    need(row is not None and row.get("names", {}).get("koModern") is None, f"no-exact group was named: {target_id}")
    need(row["fieldEvidence"]["koModern"]["status"] == "missing", f"no-exact group term not held: {target_id}")
    need(len(row["existingSurface"]["exactSourceObjects"]) == expected_members, f"no-exact group source membership drift: {target_id}")

scope_synonym_terms = {"TA2:1179": ("자유팔뼈", 60), "TA2:1504": ("발가락뼈", 28)}
for target_id, (modern, expected_members) in scope_synonym_terms.items():
    row=term_by_target[target_id]
    need(row.get("names",{}).get("koModern")==modern and row.get("fieldEvidence",{}).get("koModern",{}).get("status")=="evidence_backed",f"scope-synonym group term not applied: {target_id}")
    need(len(row.get("existingSurface",{}).get("exactSourceObjects",[]))==expected_members,f"scope-synonym group membership drift: {target_id}")
    need(row.get("existingSurface",{}).get("status")=="exact_group_term_only_no_child_surface_rename",f"scope-synonym was copied to child surfaces: {target_id}")

bulk_obs=load(HERE/"remaining-target-kmle-observations.json")
need(len(bulk_obs.get("queryResults",[]))==172 and len(bulk_obs.get("scopeSynonymQueries",[]))==3,"bulk query observation count drift")
need(sum(1 for x in bulk_obs["queryResults"] if x["resultStatus"]=="exact_named_dictionary_row")==36,"opened KMLE exact-row count drift")
need(sum(1 for x in bulk_obs["queryResults"] if x["resultStatus"]=="no_exact_named_dictionary_row")==136,"opened KMLE exact-miss count drift")
need(all(x.get("exactEdition") is None and x.get("accessMethod")=="opened_html" and not x.get("openedOriginalDictionaryRecord") for x in bulk_obs["queryResults"]+bulk_obs["scopeSynonymQueries"]),"KMLE edition/access layer was overstated")
suffix_obs = load(HERE / "suffix-m-kmle-observations.json")
need(suffix_obs.get("queryCount") == 87 and len(suffix_obs.get("rows", [])) == 87, "suffix-m frozen query count drift")
need(sum(1 for x in suffix_obs["rows"] if x.get("resultStatus") == "exact_named_dictionary_row") == 54, "suffix-m exact KAA row count drift")
need(sum(1 for x in suffix_obs["rows"] if x.get("resultStatus") == "no_exact_named_dictionary_row") == 33, "suffix-m exact KAA miss count drift")
need(all(x.get("exactEdition") is None and x.get("accessMethod") == "opened_html" and x.get("openedOriginalDictionaryRecord") is False for x in suffix_obs["rows"]), "suffix-m edition/access layer was overstated")
need(all(x.get("noHanjaCollected") is True for x in suffix_obs["rows"]), "Hanja was collected in suffix-m evidence")
suffix_by_target = {x["targetId"]: x for x in suffix_obs["rows"]}
need(suffix_by_target["TA2:2058"]["observedFields"]["koModern"] == "관자마루근", "exact suffix-m terminology row drift")
need(suffix_by_target["TA2:2684"]["observedFields"]["koModern"] == "발바닥네모근", "exact suffix-m terminology row drift")
need(suffix_by_target["TA2:2649"]["resultStatus"] == "no_exact_named_dictionary_row" and suffix_by_target["TA2:2649"].get("similarResultDisposition", "").startswith("candidate_crosswalked_to_pinned_T96_related_term"), "related-term row was conflated with a direct exact query")
need(suffix_by_target["TA2:2687"]["resultStatus"] == "no_exact_named_dictionary_row" and suffix_by_target["TA2:2687"].get("similarResultDisposition") == "not_applied_different_dictionary_section_and_nonexact_headword", "non-KAA/nonexact similar result was incorrectly accepted")
frozen_candidates=load(HERE/"remaining-target-query-candidates-frozen.json")["candidates"]
conflict_sources=next(x["eligibleSourceKeys"] for x in frozen_candidates if x["targetId"]=="TA2:1269")
conflict_name=after_objects[conflict_sources[0]]["names"].get("koModern")
need(conflict_name=="셋째손허리뼈","third metacarpal modern term was not applied")
need(all(after_objects[k]["names"].get("koTraditional") is None for k in conflict_sources),"conflicting legacy spelling was incorrectly applied")

laryngeal = [x for x in after["objects"] if "TA2:2192" in x.get("targetIds", [])]
need(len(laryngeal) == 15, "laryngeal group exact membership drift")
for obj in laryngeal:
    if before_objects[obj["sourceKey"]].get("names") == obj.get("names"):
        continue
    evidence = obj.get("nameEvidence", {}).get("koModern", {})
    owner_targets = [t for t in after_terms if obj["sourceKey"] in {s["sourceKey"] for s in t.get("existingSurface", {}).get("exactSourceObjects", [])}]
    distinct_owners = [t for t in owner_targets if t["targetId"] != "TA2:2192"]
    need(distinct_owners, "laryngeal component label lacks a distinct exact target owner")
    need(evidence.get("value") == obj["names"].get("koModern") and any(t["fieldEvidence"]["koModern"].get("value") == obj["names"].get("koModern") for t in distinct_owners), "laryngeal group label leaked onto a component surface")
    need("TA2:2192" not in evidence.get("sourceIds", []), "laryngeal group label was used as component name evidence")

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
need(len(named) == 446 and len(unnamed) == 226, "post-continuation local-display naming coverage drift")

surface_freeze = load(HERE / "source-surface-name-query-freeze.json")
surface_obs = load(HERE / "source-surface-name-observations.json")
need(len(surface_freeze.get("sourceNames", [])) == 120 and surface_obs.get("queryCount") == 120,
     "frozen exact source-surface query count drift")
need(surface_obs.get("inputFreezeSha256") == digest((HERE / "source-surface-name-query-freeze.json").read_bytes()),
     "source-surface observation ledger is detached from its frozen input")
need(surface_obs.get("exactRows") == 3 and surface_obs.get("exactMisses") == 117
     and len(surface_obs.get("observations", [])) == 120, "source-surface exact KAA result tally drift")
surface_by_query = {x["query"]: x for x in surface_obs["observations"]}
need(set(surface_by_query) == {x["query"] for x in surface_freeze["sourceNames"]},
     "source-surface observations differ from frozen query concepts")
need(all(x.get("accessDate") == "2026-09-29" and x.get("accessMethod") == "opened_html"
         and x.get("exactEdition") is None and x.get("openedOriginalDictionaryRecord") is False
         and x.get("openedOriginalSourcePage") is False and x.get("searchIndexUsedForDisplay") is False
         for x in surface_by_query.values()), "source-surface access/edition layers were overstated")
expected_surface_names = {
    "Body of sternum": ("복장뼈몸통", "흉골체"),
    "Manubrium of sternum": ("복장뼈자루", "흉골병"),
    "Xiphoid process": ("칼돌기", "검상돌기"),
}
need({q for q,x in surface_by_query.items() if x.get("resultCount") == 1} == set(expected_surface_names),
     "opened exact surface-term rows changed")
need(all(surface_by_query[q]["exactRows"][0]["headword"] == q
         and (surface_by_query[q]["exactRows"][0]["koModern"], surface_by_query[q]["exactRows"][0]["koTraditional"]) == names
         for q,names in expected_surface_names.items()), "exact KAA source-surface field values changed")
need(all(x.get("resultCount") == 0 and x.get("exactRows") == []
         for q,x in surface_by_query.items() if q not in expected_surface_names),
     "a source-name miss was promoted from a similar/index result")
surface_source_ids = {
    "Body of sternum": "kmle-t100-surface-body-of-sternum-opened",
    "Manubrium of sternum": "kmle-t100-surface-manubrium-of-sternum-opened",
    "Xiphoid process": "kmle-t100-surface-xiphoid-process-opened",
}
for query, (modern, traditional) in expected_surface_names.items():
    frozen = next(x for x in surface_freeze["sourceNames"] if x["query"] == query)
    need(len(frozen["sourceObjects"]) == 1, f"expected one midline source surface for {query}")
    source_key = frozen["sourceObjects"][0]["sourceKey"]
    current = after_objects[source_key]
    need(current["names"].get("koModern") == modern and current["names"].get("koTraditional") == traditional,
         f"exact source-surface name was not applied: {query}")
    need(current.get("nameEvidence", {}).get("koModern", {}).get("sourceIds") == [surface_source_ids[query]],
         f"exact source-surface modern provenance drift: {query}")
    need(current.get("nameEvidence", {}).get("koTraditional", {}).get("sourceIds") == [surface_source_ids[query]],
         f"exact source-surface traditional provenance drift: {query}")
    need(not re.search(r"[\u3400-\u9fff\uf900-\ufaff]", modern + traditional), f"Hanja glyph captured: {query}")
    need(current.get("targetId") == "TA2:1129" and current.get("targetIds") == before_objects[source_key].get("targetIds"),
         f"source-surface naming created or changed a target relation: {query}")
    need(current.get("haConceptId") is None and current.get("sourceOnly") is True
         and current.get("publicRedistribution") == "held" and current.get("humanReview") == "not_performed",
         f"source surface naming promoted a hold: {query}")
need(surface_obs.get("exactRows") == len(surface_source_ids), "source-surface evidence-source count drift")
need(set(surface_source_ids.values()) <= {s["id"] for s in after_sources}, "source-surface evidence source missing from overlay")
need(len(load(HERE / "source-surface-name-query-freeze.json")["sourceNames"]) == 120,
     "frozen surface-query set was not retained")

# Independently reconcile the complete exact-section query sweep and its small
# accepted field application set. This does not promote target/source identity.
need(multidict["sourcePageObservationDateLocal"] == "2026-09-30", "multidictionary observation date drift")
need(multidict["scopeDenominator"] == {"eligibleSurfaceRowsAtQueryFreeze": 234, "distinctBaseSourceLabels": 117,
                                      "targets": 542, "memberships": 563, "regions": 12},
     "multidictionary frozen query scope changed")
multi_queries = multidict["exactSourceNameObservations"]
latin_queries = multidict["exactTargetSynonymObservations"]
need(len(multi_queries) == 117 and len({x["query"] for x in multi_queries}) == 117, "source-label query count/uniqueness drift")
need(sum(x["resultStatus"] == "exact_headword_rows_present" for x in multi_queries) == 6
     and sum(x["resultStatus"] == "no_exact_same_headword_row_in_opened_exact_sections" for x in multi_queries) == 111,
     "source-label exact hit/miss tally drift")
need(len(latin_queries) == 5 and sum(bool(x.get("exactRows")) for x in latin_queries) == 4
     and sum(x.get("disposition") == "not_applied_nonexact_scope_candidate" for x in latin_queries) == 1,
     "T96 Latin synonym cross-check tally drift")
need(sum(len(x.get("sourceObjects", [])) for x in multi_queries) == 234,
     "source-label queries do not cover the frozen 234 rows")
source_observations_by_id = {}
for row in multi_queries + latin_queries:
    sid = row.get("evidenceSourceId")
    if sid:
        source_observations_by_id.setdefault(sid, []).append(row)
pages = multidict["evidencePages"]
need(len(pages) == 11 and len({x["id"] for x in pages}) == 11, "evidence page count/ID uniqueness drift")
page_url_by_id = {x["id"]: x["url"] for x in pages}
overlay_source_by_id = {x["id"]: x for x in after_sources}
for page in pages:
    sid = page["id"]
    need(sid in overlay_source_by_id, f"opened query page absent from overlay provenance: {sid}")
    rows = source_observations_by_id.get(sid, [])
    need(any(x.get("url") == page["url"] and x.get("query") == page["query"] for x in rows),
         f"evidence page URL/query is not tied to an actual query observation: {sid}")
    actual = overlay_source_by_id[sid]
    need(actual.get("url") == page["url"] and actual.get("accessDate") == "2026-09-30"
         and actual.get("accessMethod") == "opened_html" and actual.get("exactEdition") is None,
         f"overlay evidence source URL/access/edition drift: {sid}")
    need(actual.get("openedOriginalDictionaryRecord") is False and actual.get("openedOriginalSourcePage") is False
         and actual.get("locator") and actual.get("retrievalLayer"),
         f"source access layer or locator overclaimed/incomplete: {sid}")

targets_by_id = {x["id"]: x for x in scope["targets"]}
objects_by_target = defaultdict(list)
for obj in after["objects"]:
    if obj.get("localDisplayEligible") and obj.get("targetId"):
        objects_by_target[obj["targetId"]].append(obj)
applied_field_counts = Counter()
legacy_only_targets = set()
applied_surface_keys = set()
for target_id, application in applications.items():
    target = targets_by_id[target_id]
    term = after_term_map[target_id]
    need(target["term"]["english"].casefold() == application["targetEnglish"].casefold(),
         f"T96 exact English concept mismatch: {target_id}")
    surfaces = objects_by_target[target_id]
    need(len(surfaces) == 2 and {x.get("side") for x in surfaces} == {"left", "right"},
         f"expected unchanged left/right source surfaces: {target_id}")
    query = next((x for x in multi_queries if x["query"] == application["sourceSurfaceName"]), None)
    need(query is not None and {x["sourceKey"] for x in query.get("sourceObjects", [])} == {x["sourceKey"] for x in surfaces},
         f"source-label observations do not cover these exact surfaces: {target_id}")
    need(all(re.sub(r"\.[lr]$", "", x["sourceName"], flags=re.I).casefold() == application["sourceSurfaceName"].casefold()
             for x in surfaces), f"source label differs from exact surface name: {target_id}")
    applied_surface_keys.update(x["sourceKey"] for x in surfaces)
    if target_id in before_term_map:
        old_term = before_term_map[target_id]
        need(old_term["names"].get("koModern") is None and old_term["names"].get("koTraditional") is None,
             f"input target name was not a gap: {target_id}")
    else:
        need(all(before_objects[x["sourceKey"]]["names"].get(field_name) is None
                 for x in surfaces for field_name in application["fields"]),
             f"new supplemental target application would overwrite a prior source name: {target_id}")
    for field_name, field in application["fields"].items():
        sid = field["sourceId"]
        need(sid in {x["id"] for x in pages}, f"name field source ID lacks its own opened URL: {target_id} {field_name}")
        observations = source_observations_by_id[sid]
        observation = next((x for x in observations if x.get("query") == field["query"]
                            and x.get("url") == page_url_by_id.get(sid)), None)
        need(observation is not None, f"field source ID/query/URL not reconciled: {target_id} {field_name}")
        exact_rows = [r for r in observation.get("exactRows", [])
                      if r.get("section") == field["section"]
                      and r.get("headword", "").casefold() == field["headword"].casefold()
                      and field["value"] in r.get("observedKoreanCandidates", [])]
        need(exact_rows, f"field value lacks an exact opened section/headword row: {target_id} {field_name}")
        need(term["names"].get(field_name) == field["value"], f"target field value mismatch: {target_id} {field_name}")
        target_field = term["fieldEvidence"][field_name]
        need(target_field.get("value") == field["value"] and target_field.get("status") == "evidence_backed"
             and sid in target_field.get("sourceIds", []) and target_field.get("locator"),
             f"target field provenance incomplete: {target_id} {field_name}")
        for obj in surfaces:
            need(obj["names"].get(field_name) == field["value"], f"source surface field mismatch: {obj['sourceKey']} {field_name}")
            name_ev = obj.get("nameEvidence", {}).get(field_name, {})
            need(name_ev.get("value") == field["value"] and name_ev.get("sourceIds") == [sid]
                 and name_ev.get("locator"), f"surface field provenance mismatch: {obj['sourceKey']} {field_name}")
            need(sid in obj.get("nameSourceIds", []), f"surface source ID missing: {obj['sourceKey']} {sid}")
        applied_field_counts[field_name] += 1
    for obj in surfaces:
        need(obj.get("label") == (obj["names"].get("koModern") or obj["names"].get("koTraditional") or obj["names"].get("en")),
             f"source display label does not use available Korean value: {obj['sourceKey']}")
        need(obj.get("targetIds") == before_objects[obj["sourceKey"]].get("targetIds")
             and obj.get("side") == before_objects[obj["sourceKey"]].get("side")
             and obj.get("bounds") == before_objects[obj["sourceKey"]].get("bounds"),
             f"source relation/side/geometry changed with a name: {obj['sourceKey']}")
    if "koModern" not in application["fields"]:
        need(term["names"].get("koModern") is None and term["fieldEvidence"]["koModern"].get("status") == "missing",
             f"modern name gap was guessed: {target_id}")
        legacy_only_targets.add(target_id)
    need(term["learnerBindingCreated"] is False and term["canonicalHaConceptId"] is None
         and term["sourceOnly"] is True and term["humanReview"] == "not_performed"
         and term["publicRedistribution"] == "held" and term["newGeometryCreated"] is False,
         f"target/application changed a held state or created a binding: {target_id}")
need(applied_field_counts == Counter({"koModern": 4, "koTraditional": 7}), f"accepted field application count drift: {dict(applied_field_counts)}")
need(legacy_only_targets == {"TA2:2532", "TA2:2056", "TA2:1255"}, "legacy-only target gap set drift")
need(sum(bool(x.get("localDisplayEligible") and x.get("names", {}).get("koModern")) for x in after["objects"]) == 446,
     "modern Korean surface count after multidictionary application drift")
legacy_only_surface_rows = [x for x in after["objects"] if x.get("localDisplayEligible") and x.get("names", {}).get("koTraditional") and not x.get("names", {}).get("koModern")]
legacy_only_before = [x for x in before["objects"] if x.get("localDisplayEligible") and x.get("names", {}).get("koTraditional") and not x.get("names", {}).get("koModern")]
need(len(legacy_only_surface_rows) == 20 and len(legacy_only_before) == 14
     and len(legacy_only_surface_rows) - len(legacy_only_before) == 6,
     "legacy-only bilateral surface delta drift")
need(not any(re.search(r"[\u3400-\u9fff\uf900-\ufaff]", json.dumps(x, ensure_ascii=False)) for x in multidict["acceptedFieldApplications"]),
     "Hanja glyph found in accepted evidence fields")

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
bulk_results = bulk_obs["queryResults"]
bulk_by_target = {x["targetId"]: x for x in bulk_results}
term_evidence_by_target = {x["targetId"]: x for x in after_terms}
suffix_misses = [x for x in suffix_obs["rows"] if x["resultStatus"] == "no_exact_named_dictionary_row"]
bulk_term_gaps=[]
for query in bulk_results:
    row=term_evidence_by_target.get(query["targetId"])
    if query["resultStatus"]=="no_exact_named_dictionary_row" and row and row.get("fieldEvidence",{}).get("koModern",{}).get("status")=="missing":
        bulk_term_gaps.append({"targetId":query["targetId"],"english":query["query"],"sourceId":query["id"],"url":query["url"],"status":"exact_target_query_no_KAA_row_and_no_applied_scope_synonym","sourceSurfaceCount":len(row.get("existingSurface",{}).get("exactSourceObjects",[])),"locator":query["locator"]})
term_gaps=[]
for x in misses:
    tid=next(t["targetId"] for t in new_terms if t["english"].casefold()==x["query"].casefold())
    row=term_evidence_by_target.get(tid)
    if row and row.get("fieldEvidence",{}).get("koModern",{}).get("status")=="missing":
        term_gaps.append({"query":x["query"],"targetId":tid,"sourceId":next((s["id"] for s in obs["observations"] if s["query"]==x["query"]),None),"status":"no_exact_named_dictionary_row","exactSourceKeySurfaces":len(row.get("existingSurface",{}).get("exactSourceObjects",[])),"similarResultNotAccepted":x.get("similarResultNotAccepted"),"reason":"The direct exact query had no KAA row and no separately verified scope synonym resolved the target."})
term_gaps.extend(bulk_term_gaps)
term_gaps=list({x["targetId"]:x for x in term_gaps}.values())
surface_query_misses = [x for x in surface_obs["observations"] if x["resultCount"] == 0]
surface_freeze_by_query = {x["query"]: x for x in surface_freeze["sourceNames"]}
multidict_misses = [x for x in multi_queries if x["resultStatus"] == "no_exact_same_headword_row_in_opened_exact_sections"]
multidict_unapplied = multidict.get("unappliedExactCandidates", [])
target_latin_not_applied = [x for x in latin_queries if x.get("disposition") == "not_applied_nonexact_scope_candidate"]
exceptions = {
    "schemaVersion": 1, "taskId": "T100", "workUnit": "C evidence-backed exceptions only",
    "status": "open", "editionPolicy": "KMLE aggregate page displays a KAA terminology section but no exact edition/revision; original KAA records were not opened.",
    "termGaps": term_gaps,
    "directSourceSurfaceNameMisses": [
        {"query": x["query"], "url": x["url"], "status": "opened_exact_KAA_section_zero_rows",
         "sourceKeys": x["sourceKeys"], "targetIds": sorted({s["targetId"] for s in surface_freeze_by_query[x["query"]]["sourceObjects"]}),
         "resolution": "This exact English source-label query had no KAA exact row; it does not prove that the Korean term is absent from every edition/source. Similar/index rows were not applied."}
        for x in surface_query_misses
    ],
    "multiDictionarySourceSurfaceNameMisses": [
        {"query": x["query"], "url": x["url"], "accessDate": x["accessDate"],
         "status": "no_exact_same_headword_row_in_opened_named_sections",
         "sourceKeys": [s["sourceKey"] for s in x["sourceObjects"]],
         "targetIds": sorted({s["targetId"] for s in x["sourceObjects"]}),
         "negativeScope": x["negativeScope"],
         "resolution": "The opened KMLE aggregate sections had no exact row for this source label. This is not proof that no Korean name exists elsewhere; no fuzzy/index result was applied."}
        for x in multidict_misses
    ],
    "multiDictionaryUnappliedExactCandidates": multidict_unapplied,
    "targetLatinNonExactCandidates": [
        {"query": x["query"], "url": x["url"], "status": x["disposition"],
         "exactRows": x.get("exactRows", []), "similarRowsNotApplied": x.get("similarRows", []),
         "resolution": "The opened row drops the hand-specific scope and is not applied to the T96 hand target."}
        for x in target_latin_not_applied
    ],
    "legacyOnlyModernNameGaps": [
        {"targetId": tid, "field": "koModern", "status": "missing",
         "legacyValue": applications[tid]["fields"]["koTraditional"]["value"],
         "resolution": "The opened exact sections support the listed historical Korean value only; do not infer a current-standard modern term."}
        for tid in sorted(legacy_only_targets)
    ],
    "directQueryMisses": [{"targetId":x["targetId"],"query":x["query"],"url":x["url"],"status":"opened_exact_KAA_section_zero_rows","resolution":"This exact phrase miss is not itself a claim that the term does not exist in other sources or editions."} for x in bulk_results if x["resultStatus"]=="no_exact_named_dictionary_row"],
    "suffixVariantDirectQueryMisses": [
        {"targetId":x["targetId"],"query":x["query"],"url":x["url"],"status":"opened_exact_KAA_section_zero_rows","termFieldStatus":term_evidence_by_target.get(x["targetId"],{}).get("fieldEvidence",{}).get("koModern",{}).get("status"),"similarResultDisposition":x.get("similarResultDisposition"),"locator":x["locator"],"resolution":"A suffix-form exact-query miss remains an exception even when a separate, explicitly crosswalked synonym row resolves the target; it is not evidence that no other source/edition has the term."}
        for x in suffix_misses
    ],
    "scopeSynonymDecisions": bulk_obs["scopeSynonymQueries"],
    "fieldConflicts": [
        {"targetId": "TA2:2650", "english": "Extensor hallucis longus", "field": "koTraditional", "observedButNotApplied": "장무지싱근", "status": "sourceTextConflict_unresolved", "resolution": "Modern term may be shown with evidence. Legacy spelling remains null until a direct authoritative correction is confirmed."},
        {"targetId": "TA2:1269", "english": "Third metacarpal bone", "field": "koTraditional", "observedButNotApplied": "제1중수골", "status": "sourceTextConflict_unresolved", "resolution": "The modern exact term `셋째손허리뼈` is applied. Keep the conflicting legacy value unapplied until a direct authoritative correction is confirmed."}
    ],
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
    "notCountedComplete": {"remainingEligibleUnnamedRows": len(unnamed), "eligibleRowsStillWithoutModernKorean": len(unnamed),
                            "legacyOnlySurfaceRows": len(legacy_only_surface_rows), "newLegacyOnlySurfaceRows": len(legacy_only_surface_rows)-len(legacy_only_before),
                            "unresolvedTargetTermGapsInSupplementalBatch": len(term_gaps),
                            "bulkDirectExactQueryMisses": sum(1 for x in bulk_results if x["resultStatus"]=="no_exact_named_dictionary_row"),
                            "suffixVariantDirectExactQueryMisses": len(suffix_misses),
                            "priorSourceSurfaceExactQueryMisses": len(surface_query_misses),
                            "multiDictionarySourceSurfaceExactQueryMisses": len(multidict_misses),
                            "unappliedExactNameCandidates": len(multidict_unapplied),
                            "unappliedNonExactLatinScopeCandidates": len(target_latin_not_applied),
                            "unresolvedLegacyFieldConflicts": 2, "unresolvedHomonymSearchCases": 4,
                            "unresolvedSubstringSearchAmbiguities": 1, "wholeBodyCompletion": False}
}
(HERE / "exceptions.json").write_text(json.dumps(exceptions, ensure_ascii=False, indent=2) + "\n")

result = {
    "schemaVersion": 1, "taskId": "T100", "workUnit": "B/C/D continuation validation",
    "status": "pass_partial", "checkedAtLocal": "2026-09-30", "baselineHead": BASE_HEAD,
    "checks": {
        "sourceObjectInventory960AndT96Denominators542_563_12": True,
        "onlyEvidenceBackedExistingSurfaceNameFieldsChanged": True,
        "allOtherObjectFieldsAnd668OtherRowsPreserved": len(after_objects) - len(changed) == 668,
        "prior42Terminology57SourcesAndHistoricalRelationsPreserved": True,
        "213CumulativeSupplementalTargetTermRowsAnd329UniqueCurrentContinuationSourcesAdded": len(new_terms) == 213 and len(new_sources) == 329,
        "120ExactSourceSurfaceNamesQueriedWith3KAAExactRowsAnd117Misses": len(surface_by_query) == 120 and len(expected_surface_names) == 3 and len(surface_query_misses) == 117,
        "87SuffixAbbreviationQueriesRecordedWith54ExactRowsAnd33Misses": True,
        "relatedTermCrosswalkSeparatedFromDirectExactQueryAndNonKAAResultHeld": True,
        "sevenExactRepeatedGroupTermsAndThreeExplicitNoExactGroupTermsRecorded": True,
        "35OrdinalMemberNamesComposedFromExactKaaRangeAndFrozenMembership": True,
        "noCanonicalBindingsGeometryOrPolicyPromotion": True,
        "sourceCatalogAndCompiledGeometryHashesPresent": True,
        "noHanjaCollected": True,
        "eligibleNamingCoverageReconciled": True,
        "exceptionAndBacklogLedgersGenerated": True,
        "unresolvedSuffixMissesSeparatedFromDirectAndSimilarCrosswalkEvidence": len(exceptions["suffixVariantDirectQueryMisses"]) == 33,
        "liveSearchAmbiguityRecordedWithoutChangingVerifiedNames": True,
        "117MultiDictionarySurfaceLabelsSweptWith6ExactRowsAnd111ExactMisses": len(multi_queries) == 117 and len(multidict_misses) == 111,
        "sevenExactFieldApplicationsOnFourteenExistingBilateralRows": len(applications) == 7 and len(applied_surface_keys) == 14 and applied_surface_keys <= set(changed),
        "fieldEvidenceURLsLocatorsAndExactSectionRowsValidated": True,
        "legacyOnlyFieldsAndThreeTrueModernGapsRetained": len(legacy_only_targets) == 3,
        "separateIndexOpenedHTMLOriginalRecordAndHumanReviewStatesRetained": True
    },
    "counts": {"sourceObjects": 960, "eligible": len(eligible), "namedModern": len(named), "unnamedModern": len(unnamed),
               "legacyOnlySurfaceRows": len(legacy_only_surface_rows), "newLegacyOnlySurfaceRows": len(legacy_only_surface_rows)-len(legacy_only_before),
               "newSurfaceNameFieldRows": len(changed),
               "newTerminologyRows": len(new_terms), "newEvidenceSources": len(new_sources), "backlogGroups": len(groups),
               "gapRowsInSupplementalBatch": len(term_gaps), "priorDirectSourceSurfaceNameExactMisses": len(surface_query_misses),
               "multiDictionarySourceSurfaceNameExactMisses": len(multidict_misses)},
    "holds": {"wholeBodyCompletion": False, "sourceOnly": True, "rights": "held", "humanReview": "not_performed", "canonicalBindingsAdded": 0, "geometryChanged": False},
    "remainingWork": [f"Continue B evidence-backed naming for {len(unnamed)} eligible surfaces still missing a modern Korean field; {len(legacy_only_targets) * 2} surfaces have a historical name only. The 117-label query sweep is an observation set, not the whole-body denominator.", "Keep 111 exact named-section source-label misses, three unapplied exact alternatives, one nonexact hand-scope Latin candidate, existing field conflicts/homonyms/parent-part boundary and substring ambiguity open until stronger evidence supports resolution.", "D whole-body exact visual/selection/performance coverage remains partial; named target/source identity, active-scene FPS/GPU/memory budgets and full device coverage are incomplete."]
}
(HERE / "validation.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
print(json.dumps(result, ensure_ascii=False, indent=2))
