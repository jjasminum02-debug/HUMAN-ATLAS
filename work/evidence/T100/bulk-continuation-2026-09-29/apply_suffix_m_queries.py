#!/usr/bin/env python3
"""Apply evidence-backed `m.` terminology to exact existing T96/source rows."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent


def need(ok: bool, message: str) -> None:
    if not ok:
        raise SystemExit(message)


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def load(path: Path):
    return json.loads(path.read_text())


def apply_suffix_m_query_batch(overlay: dict, query_evidence: dict, term_ledger: dict,
                               repetitions: dict, detail: dict):
    suffix_path = HERE / "suffix-m-kmle-observations.json"
    gap_path = HERE / "remaining-target-term-gaps-before-m-queries.json"
    suffix = load(suffix_path)
    gap_raw = gap_path.read_bytes()
    gaps = json.loads(gap_raw)
    need(sha(gap_raw) == suffix["frozenCandidateInputSha256"], "suffix-query frozen target input changed")
    need(len(gaps["candidates"]) == suffix["queryCount"] == 87, "suffix-query target count drift")
    need(suffix["exactKaaRows"] == 54 and suffix["exactKaaMisses"] == 33, "suffix-query exact-result tally drift")

    scope = load(ROOT / "atlas-data/catalog/target-scope-t96.json")
    target_map = {x["id"]: x for x in scope["targets"]}
    catalog = {x["sourceKey"]: x for x in load(ROOT / "work/evidence/T98/astra-resolution-2026-09-29/source-catalog.json")["objects"]}
    compiled = {x["sourceKey"]: x for x in load(ROOT / "atlas-data/source-cache/datasets/za/compiled/manifest.json")["instances"]}
    object_map = {x["sourceKey"]: x for x in overlay["objects"]}
    term_map = {x["targetId"]: x for x in overlay["targetTerminologyEvidence"]}
    need(all(x["targetId"] in term_map for x in suffix["rows"]), "suffix target term row missing")
    query_map = {x["targetId"]: x for x in suffix["rows"]}

    existing_source_ids = {x["id"] for x in overlay.get("evidenceSources", [])}
    added_evidence_sources = []
    for row in suffix["rows"]:
        need(row["id"] not in existing_source_ids, f"duplicate evidence source: {row['id']}")
        existing_source_ids.add(row["id"])
        added_evidence_sources.append({
            "id": row["id"], "url": row["url"], "sourceLabel": row["sourceLabel"],
            "exactEdition": None, "editionExposure": row["editionExposure"],
            "accessDate": row["accessDate"], "accessMethod": row["accessMethod"],
            "locator": row["locator"], "retrievalLayer": row["retrievalLayer"],
            "openedOriginalDictionaryRecord": False, "openedOriginalSourcePage": False,
        })
    related_source_by_target = {}
    for row in suffix.get("relatedEvidenceSources", []):
        need(row["id"] not in existing_source_ids, f"duplicate related evidence source: {row['id']}")
        existing_source_ids.add(row["id"])
        added_evidence_sources.append({
            "id": row["id"], "url": row["url"], "sourceLabel": row["sourceLabel"],
            "exactEdition": None, "editionExposure": row["editionExposure"],
            "accessDate": row["accessDate"], "accessMethod": row["accessMethod"],
            "locator": row["locator"], "retrievalLayer": row["retrievalLayer"],
            "openedOriginalDictionaryRecord": False, "openedOriginalSourcePage": False,
        })
        related_source_by_target[row["targetId"]] = row
    overlay["evidenceSources"].extend(added_evidence_sources)

    def normalized(value: str) -> str:
        value = re.sub(r"\.[lr]$", "", value.strip(), flags=re.I)
        value = re.sub(r"\s+muscle(?:s)?$", "", value, flags=re.I)
        return re.sub(r"\s+", " ", value.strip()).casefold()

    applied_targets, named_surfaces, unresolved = [], [], []
    for candidate in gaps["candidates"]:
        tid = candidate["targetId"]
        target, obs, term = target_map[tid], query_map[tid], term_map[tid]
        need(term.get("fieldEvidence", {}).get("koModern", {}).get("status") == "missing", f"term already resolved before suffix stage: {tid}")
        need(term.get("names", {}).get("koModern") is None and term.get("names", {}).get("koTraditional") is None, f"suffix stage would overwrite target names: {tid}")
        accepted_related = obs.get("acceptedRelatedTermEvidence")
        direct_exact = obs["resultStatus"] == "exact_named_dictionary_row"
        accepted = accepted_related if accepted_related else (obs["observedFields"] if direct_exact else None)
        term_source_id = related_source_by_target[tid]["id"] if accepted_related else obs["id"]

        if accepted:
            modern, traditional = accepted["koModern"], accepted.get("koTraditional")
            locator = accepted.get("locator") or obs["locator"]
            if accepted_related:
                related = set((target.get("sourceFlags") or {}).get("relatedTerms", []))
                need({"musculus peroneus tertius", "peroneus tertius muscle"} <= related, "TA2:2649 pinned related-term crosswalk changed")
                need(accepted_related.get("headword") == "Peroneus tertius m.", "unexpected nonexact KAA row for TA2:2649")
                term["classification"]["groupPartVariant"] = "Direct Fibularis query was empty. The KAA similar-result row `Peroneus tertius m.` is used only through the exact related-term strings frozen in T96 for this target; it is recorded as a synonym crosswalk, not a direct exact-query hit or geometry relation."
            else:
                need(direct_exact, f"nonexact search result cannot fill target term: {tid}")
                term["classification"]["groupPartVariant"] = "Opened KAA exact-result row from the conventional `m.` form of the frozen T96 target phrase; no member or parent relation was inferred."
            need(modern and not re.search(r"[\u3400-\u9fff]", modern), f"invalid modern Korean field: {tid}")
            need(traditional is None or not re.search(r"[\u3400-\u9fff]", traditional), f"Hanja glyph present: {tid}")
            term["names"]["koModern"], term["names"]["koTraditional"] = modern, traditional
            term["targetTermSourceIds"] = list(dict.fromkeys([*term.get("targetTermSourceIds", []), obs["id"], term_source_id]))
            term["fieldEvidence"]["koModern"] = {"value": modern, "sourceIds": [term_source_id], "locator": locator, "status": "evidence_backed", "missingReason": None}
            term["fieldEvidence"]["koTraditional"] = ({"value": traditional, "sourceIds": [term_source_id], "locator": locator, "status": "evidence_backed", "missingReason": None} if traditional else {"value": None, "sourceIds": [], "locator": None, "status": "missing", "missingReason": "The opened row exposed no legacy Korean value."})
            term["queryResultContext"]["suffixVariantQuery"] = {
                "queryId": obs["id"], "resultStatus": obs["resultStatus"], "resultLayer": obs["resultLayer"],
                "appliedEvidenceSourceId": term_source_id,
                "application": "exact_target_term" if not accepted_related else "frozen_T96_related_term_synonym",
            }

            all_surfaces = [o for o in overlay["objects"] if o.get("localDisplayEligible") and o.get("targetId") == tid]
            exact_surfaces = [o for o in all_surfaces if normalized(o.get("sourceName", "")) == normalized(target["term"]["english"])]
            group_kinds = {"bone_group", "bone_series", "muscle_group", "repeated_muscle_family", "muscle_complex"}
            can_name = bool(exact_surfaces) and len(exact_surfaces) == len(all_surfaces)
            if target["semanticKind"] in group_kinds:
                can_name = can_name and all(normalized(o["sourceName"]) == normalized(target["term"]["english"]) for o in exact_surfaces)
            named_keys = []
            if can_name:
                for obj in exact_surfaces:
                    key = obj["sourceKey"]
                    need(key in catalog and key in compiled, f"existing source/compiled mesh is absent: {key}")
                    need(obj.get("names", {}).get("koModern") is None and obj.get("names", {}).get("koTraditional") is None, f"surface term already present: {key}")
                    need(obj.get("sourceOnly") is True and obj.get("haConceptId") is None and obj.get("humanReview") == "not_performed" and obj.get("publicRedistribution") == "held", f"policy state changed: {key}")
                    need(obj.get("localDisplayEligible") is True and obj.get("defaultVisible") is True, f"visibility state changed: {key}")
                    obj["names"]["koModern"] = modern
                    obj["label"] = modern
                    if traditional:
                        obj["names"]["koTraditional"] = traditional
                    evidence = obj.get("nameEvidence") or {}
                    need(not evidence.get("koModern"), f"surface name evidence already exists: {key}")
                    evidence["koModern"] = {"value": modern, "sourceIds": [term_source_id], "locator": locator}
                    if traditional:
                        evidence["koTraditional"] = {"value": traditional, "sourceIds": [term_source_id], "locator": locator}
                    evidence["en"] = {"value": obj["names"].get("en"), "sourceIds": ["fipat-ta2-t96-frozen-target-terms"], "locator": f"Pinned T96 exact English target for {tid}: {target['term']['english']}"}
                    obj["nameEvidence"] = evidence
                    obj["nameSourceIds"] = list(dict.fromkeys([*obj.get("nameSourceIds", []), term_source_id]))
                    named_surfaces.append({
                        "targetId": tid, "sourceKey": key, "sourceName": obj["sourceName"],
                        "side": obj.get("side"), "regionIds": obj.get("regionIds", []),
                        "koModern": modern, "koTraditional": traditional, "english": obj["names"].get("en"),
                        "evaluatedGeometrySha256": catalog[key]["evaluatedGeometrySha256"], "compiledInstancePresent": True,
                        "sourceQueryId": term_source_id,
                    })
                    named_keys.append(key)
            term["existingSurface"]["suffixQueryApplication"] = {
                "status": "exact_source_name_rows_named" if can_name else "target_term_only_no_surface_rename",
                "sourceKeysNamed": named_keys,
                "note": "Only a complete exact target/source-name match was applied to existing rows. Group terms were not copied to distinct members; source identity, side, geometry, visibility, rights, review, and canonical binding were preserved.",
            }
            applied_targets.append({
                "targetId": tid, "queryId": obs["id"], "acceptedEvidenceSourceId": term_source_id,
                "resultType": "exact_abbreviation_row" if not accepted_related else "listed_T96_related_term_in_KAA_similar_section",
                "koModern": modern, "koTraditional": traditional, "surfaceRowsNamed": len(named_keys),
            })
        else:
            term["targetTermSourceIds"] = list(dict.fromkeys([*term.get("targetTermSourceIds", []), obs["id"]]))
            miss = "The opened KAA exact-result section for the frozen m.-abbreviation query returned zero exact rows."
            for field in ("koModern", "koTraditional"):
                current = term["fieldEvidence"][field]
                current["sourceIds"] = list(dict.fromkeys([*current.get("sourceIds", []), obs["id"]]))
                current["locator"] = None
                current["missingReason"] = miss + " A separately observed similar row remains an internal candidate and was not applied."
            term["queryResultContext"]["suffixVariantQuery"] = {"queryId": obs["id"], "resultStatus": obs["resultStatus"], "resultLayer": obs["resultLayer"], "application": "missing_candidate_not_promoted"}
            similar = obs.get("separatelyObservedSimilarResult")
            if similar:
                alternate_source = related_source_by_target.get(tid)
                term["unappliedTermCandidates"].append({
                    "value": similar.get("koModern"), "legacyValue": similar.get("koTraditional"),
                    "sourceId": alternate_source["id"] if alternate_source else obs["id"],
                    "locator": similar.get("targetCrosswalk"), "status": "similar_candidate_not_applied",
                    "reason": "The observed row is not an exact target term or a sufficiently exact frozen synonym crosswalk; it is retained as a candidate only.",
                })
            unresolved.append({"targetId": tid, "query": obs["query"], "sourceId": obs["id"], "status": "no_exact_KAA_row", "similarCandidateOnly": bool(similar)})

    overlay["revision"] = "T100-source-taxonomy-local-display-v2-B-bulk-verified-names-2026-09-29-round3"
    query_evidence["suffixMQueryBatch"] = {
        "path": suffix_path.relative_to(ROOT).as_posix(), "candidateCount": 87,
        "exactKaaRows": 54, "directExactMisses": 33,
        "appliedRelatedTermRows": ["TA2:2649"], "notAppliedSimilarRows": ["TA2:2687"],
        "sourceIds": [x["id"] for x in suffix["rows"]] + [x["id"] for x in suffix.get("relatedEvidenceSources", [])],
        "sourceLayers": "Opened KMLE aggregate HTML; KAA exact/similar rows and misses are distinguished; original dictionary records not opened; exact edition not exposed.",
    }
    term_ledger["suffixMQueryBatch"] = {
        "candidateCount": 87, "exactKaaRows": 54, "directExactMisses": 33,
        "targetTermsResolved": len(applied_targets), "newlyNamedSurfaceRows": len(named_surfaces),
        "appliedTargets": applied_targets, "unresolvedTargets": unresolved,
        "surfaceApplicationRule": "Exact T96 term or listed T96 related term only; names go to complete exact target/source-name matches. No anatomy relation, child, side, geometry, visibility, review, rights, or canonical-binding inference.",
    }
    repetitions["suffixMQueryCorrespondence"] = {
        "candidateCount": 87, "exactKaaRows": 54, "directExactMisses": 33,
        "appliedTargetTerms": applied_targets, "namedSurfaceRows": named_surfaces,
        "unresolvedTargets": unresolved, "newSourceTargetRelations": 0,
        "canonicalBindingsCreated": 0, "geometryChanged": False,
    }
    detail["newlyNamed"].extend(named_surfaces)
    detail["suffixMQueryTargetsUpdated"] = applied_targets
    detail["suffixMQueryUnresolved"] = unresolved
    return overlay, query_evidence, term_ledger, repetitions, detail
