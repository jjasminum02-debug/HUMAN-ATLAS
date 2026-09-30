#!/usr/bin/env python3
"""Apply only the independently accepted T100 parallel-result deltas.

This is intentionally a one-shot integration over the frozen parallel run.
It refuses a changed starting overlay and does not use the historical resolver's
bulk apply path. TypeScript's shared integration validator remains authoritative.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
RUN = ROOT / "work/evidence/T100/parallel-resolution-2026-09-30"
OUT = RUN / "integration"
OVERLAY = ROOT / "atlas-data/overlays/za-local-integration.json"
BASE_SHA = "e9277ca6f7b2081ce3cf78b3a9ac02bc265207782e0294e82d84847fa0bd2ab4"
SOURCE_HASH = "9f08a17ea0115fed80b2a73ecdf0a1bc2ab2f6956f37c593ce23d513ea35afcd"
SOURCE_REVISION = "c7010a903b75a2fd24a13b1c2c4c3546a9223780"
RUN_ID = "T100-parallel-resolution-2026-09-30-r1"


def read_json(path: Path):
    return json.loads(path.read_text())


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def evidence_source(source: dict, *, access_method: str, exact_edition: str | None,
                    edition_exposure: str, locator: str, retrieval_layer: str) -> dict:
    return {
        "id": source["sourceId"],
        "url": source["url"],
        "sourceLabel": f"{source['authority']}: {source['title']}",
        "exactEdition": exact_edition,
        "editionExposure": edition_exposure,
        "accessDate": source["accessDate"],
        "accessMethod": access_method,
        "locator": locator,
        "retrievalLayer": retrieval_layer,
        "openedOriginalDictionaryRecord": False,
        "openedOriginalSourcePage": True,
    }


def append_once(rows: list, value: dict, key: str) -> None:
    if any(row.get(key) == value[key] for row in rows):
        raise ValueError(f"refusing duplicate {key}: {value[key]}")
    rows.append(value)


def main() -> None:
    manifest = read_json(RUN / "run-manifest.json")
    if manifest.get("runId") != RUN_ID:
        raise ValueError("parallel run id changed")
    pinned_overlay = next(row["sha256"] for row in manifest["inputs"]
                          if row["originalPath"] == "atlas-data/overlays/za-local-integration.json")
    if pinned_overlay != BASE_SHA:
        raise ValueError("manifest does not pin the expected T100 starting overlay")
    if (OUT / "integration-decisions.json").exists():
        raise ValueError("integration evidence already exists; do not overwrite it")

    original = OVERLAY.read_bytes()
    before_sha = sha(original)
    if before_sha != BASE_SHA:
        raise ValueError(f"overlay changed since parallel freeze: {before_sha}")
    overlay = json.loads(original)
    baseline_objects = {row["sourceKey"]: copy.deepcopy(row) for row in overlay["objects"]}

    target_scope = read_json(ROOT / "atlas-data/catalog/target-scope-t96.json")
    target_by_id = {row["id"]: row for row in target_scope["targets"]}
    source_catalog = read_json(ROOT / "work/evidence/T98/astra-resolution-2026-09-29/source-catalog.json")
    source_by_key = {row["sourceKey"]: row for row in source_catalog["objects"]}
    compiled = read_json(ROOT / "atlas-data/source-cache/datasets/za/compiled/manifest.json")
    compiled_by_key = {row["sourceKey"]: row for row in compiled["instances"]}
    object_by_key = {row["sourceKey"]: row for row in overlay["objects"]}
    t78 = read_json(ROOT / "work/evidence/T78/reference/ta2-scope.json")
    t78_by_id = {row["id"]: row for row in t78}
    if source_catalog["sourceHash"] != SOURCE_HASH or source_catalog["sourceRevision"] != SOURCE_REVISION:
        raise ValueError("pinned source catalog identity changed")

    # B: exact member links for ten distal toe surfaces. Preserve each existing
    # generic TA2:1505 link as a separate, broader membership.
    b_rows = read_json(RUN / "representation-b/proposals.json")
    b_target = next(row for row in b_rows if row["targetId"] == "TA2:1512")
    b_relations = b_target["proposedRelations"]
    if len(b_relations) != 10 or {row["proposedMemberCode"] for row in b_relations} != {
        f"distal:{ordinal}" for ordinal in ("first", "second", "third", "fourth", "fifth")
    }:
        raise ValueError("TA2:1512 proposal is not the fixed five-by-two exact member set")
    b_target_record = target_by_id["TA2:1512"]
    if b_target_record["term"]["english"] != "distal phalanx of foot" or b_target_record["semanticKind"] != "bone":
        raise ValueError("frozen TA2:1512 target changed")
    foot_added = []
    for proposal in b_relations:
        key = proposal["sourceKey"]
        row = object_by_key[key]
        source = source_by_key[key]
        compiled_row = compiled_by_key[key]
        if proposal["targetId"] != "TA2:1512" or proposal["extentClaim"] != "unknown":
            raise ValueError("unexpected foot target/extent proposal")
        if row["sourceName"] != proposal["sourceName"] or row["side"] != proposal["side"]:
            raise ValueError(f"proposal/source overlay mismatch: {key}")
        if source["name"] != row["sourceName"] or source["sourceLabelSide"] != row["side"]:
            raise ValueError(f"frozen source identity mismatch: {key}")
        if source["evaluatedGeometrySha256"] != compiled_row["evaluatedGeometrySha256"]:
            raise ValueError(f"frozen evaluated geometry reference mismatch: {key}")
        existing_generic = next((link for link in row.get("learnerConceptLinks", [])
                                 if link["relationKind"] == "verified_class_member"
                                 and link["targetIds"] == ["TA2:1505"]
                                 and link["memberCode"] == proposal["proposedMemberCode"]), None)
        if not existing_generic:
            raise ValueError(f"generic TA2:1505 proof missing for {key}")
        member_code = proposal["proposedMemberCode"]
        class_member_evidence_ids = list(dict.fromkeys(
            existing_generic["evidenceIds"] + ["fipat-ta2-t96-full-target-catalog"]
        ))
        source_side = source["sourceLabelSide"]
        member_with_side = f"{member_code}:{source_side}"
        if row["sourceName"] != f"{member_code.split(':', 1)[1].title()} phalanx of {member_code.split(':', 1)[1]} finger of foot.{ 'l' if source_side == 'left' else 'r' }":
            # The source spelling uses ordinal before "finger"; the regex below
            # is the authoritative exact form and avoids deriving a side from bounds.
            import re
            if not re.fullmatch(r"Distal phalanx of (first|second|third|fourth|fifth) finger of foot\.[lr]", row["sourceName"], re.I):
                raise ValueError(f"not an exact distal toe source label: {key}")
        limb_collection = "Left lower limb" if source_side == "left" else "Right lower limb"
        if source["parent"] != "Phalanges of foot.g" or limb_collection not in source["collections"]:
            raise ValueError(f"foot part/side context mismatch: {key}")
        if member_with_side != f"{member_code}:{'left' if row['sourceName'].endswith('.l') else 'right'}":
            raise ValueError(f"side suffix disagreement: {key}")
        if "TA2:1512" in row["targetIds"]:
            raise ValueError(f"TA2:1512 already present on {key}")
        row["targetIds"].append("TA2:1512")
        link = copy.deepcopy(existing_generic)
        link["targetIds"] = ["TA2:1512"]
        link["evidenceIds"] = class_member_evidence_ids
        row.setdefault("learnerConceptLinks", []).append(link)
        relation = {
            "targetId": "TA2:1512",
            "targetEnglish": b_target_record["term"]["english"],
            "targetLatin": b_target_record["term"]["latin"],
            "targetSemanticKind": b_target_record["semanticKind"],
            "targetPrimaryOwner": b_target_record["primaryOwner"],
            "targetRegionIds": b_target_record["regionIds"],
            "targetLaterality": "not_specified_by_source",
            "sourceKey": key,
            "sourceObjectName": row["sourceName"],
            "sourceDataName": source["dataName"],
            "sourceParent": source["parent"],
            "sourceCollections": source["collections"],
            "sourceSide": source_side,
            "evaluatedGeometrySha256": source["evaluatedGeometrySha256"],
            "sourceHash": SOURCE_HASH,
            "sourceRevision": SOURCE_REVISION,
            "matchBasis": "Exact frozen TA2:1512 distal-foot target plus source object name `Distal phalanx of {ordinal} finger of foot.{l|r}`, parent `Phalanges of foot.g`, and source-declared side. This adds a distal member relation while retaining the distinct existing generic TA2:1505 link; target extent remains unclaimed.",
            "directObjectNameMatch": False,
            "ancestorNameAloneUsed": False,
            "upstreamFjOrTa2IdClaim": False,
            "canonicalHaBindingCreated": False,
            "humanReview": "not_performed",
            "relationKind": "class_member",
            "matchedTargetSynonym": None,
            "sourceSegmentCode": None,
            "memberCode": member_with_side,
            "matchEvidenceSourceIds": class_member_evidence_ids,
        }
        row.setdefault("targetRelationEvidence", []).append(relation)
        foot_added.append({"sourceKey": key, "sourceName": row["sourceName"], "side": source_side,
                           "targetId": "TA2:1512", "memberCode": member_code,
                           "memberRelationCode": member_with_side,
                           "preservedGenericTargetId": "TA2:1505",
                           "evaluatedGeometrySha256": source["evaluatedGeometrySha256"]})

    # A: TA2 2.07 exposes an exact en_GB target synonym for the source label.
    # Restrict this exception to posterior crico-arytenoid muscle and its exact
    # left/right source objects; similar laryngeal names are not accepted.
    a_rows = read_json(RUN / "representation-a/proposals.json")
    a_target = next(row for row in a_rows if row["targetId"] == "TA2:2196")
    context_target = t78_by_id[2196]
    synonym = context_target["term"].get("en_GB")
    if synonym != "posterior crico-arytenoid muscle":
        raise ValueError("frozen T78 en_GB term changed")
    a_candidate_keys = set(a_target["candidateSourceKeys"])
    expected_posterior_labels = {(synonym + ".l").casefold(), (synonym + ".r").casefold()}
    a_sources = [source for source in source_catalog["objects"]
                 if source["name"].casefold() in expected_posterior_labels]
    if len(a_sources) != 2 or {source["name"].casefold() for source in a_sources} != expected_posterior_labels:
        raise ValueError("exact posterior crico-arytenoid source pair not found")
    a_added = []
    for source in a_sources:
        key = source["sourceKey"]
        if key not in a_candidate_keys:
            raise ValueError(f"A candidate ledger did not assign exact source key {key}")
        row = object_by_key[key]
        if source["name"] != row["sourceName"] or source["sourceLabelSide"] != row["side"]:
            raise ValueError(f"laryngeal source label/side mismatch: {key}")
        if source["parent"] != "Laryngeal muscles.g" or not {
            "Laryngeal muscles", "Muscles of neck", "Neck"
        }.issubset(set(source["collections"])):
            raise ValueError(f"laryngeal parent/collection context mismatch: {key}")
        compiled_row = compiled_by_key[key]
        if source["evaluatedGeometrySha256"] != compiled_row["evaluatedGeometrySha256"]:
            raise ValueError(f"frozen laryngeal geometry reference mismatch: {key}")
        pair_link = next((link for link in row.get("learnerConceptLinks", [])
                          if link["relationKind"] == "paired_source_concept"
                          and link["identityStatus"] == "source_label_pair_only"), None)
        if not pair_link or "TA2:2196" in row["targetIds"]:
            raise ValueError(f"exact source pair proof/target baseline mismatch: {key}")
        target = target_by_id["TA2:2196"]
        row["targetIds"].append("TA2:2196")
        row.setdefault("learnerConceptLinks", []).append({
            "conceptKey": pair_link["conceptKey"],
            "relationKind": "verified_source_crosswalk",
            "targetIds": ["TA2:2196"],
            "memberCode": None,
            "targetTermMatches": [],
            "matchRule": "exact frozen target representation: qualified_synonym",
            "evidenceIds": ["fipat-ta2-t96-full-target-catalog", "fipat-ta2-t78-frozen-full-context", "za-t99-frozen-source-objects"],
            "identityStatus": "evidence_backed",
            "humanReview": "not_performed",
        })
        row.setdefault("targetRelationEvidence", []).append({
            "targetId": "TA2:2196",
            "targetEnglish": target["term"]["english"],
            "targetLatin": target["term"]["latin"],
            "targetSemanticKind": target["semanticKind"],
            "targetPrimaryOwner": target["primaryOwner"],
            "targetRegionIds": target["regionIds"],
            "targetLaterality": "not_specified_by_source",
            "sourceKey": key,
            "sourceObjectName": source["name"],
            "sourceDataName": source["dataName"],
            "sourceParent": source["parent"],
            "sourceCollections": source["collections"],
            "sourceSide": source["sourceLabelSide"],
            "evaluatedGeometrySha256": source["evaluatedGeometrySha256"],
            "sourceHash": SOURCE_HASH,
            "sourceRevision": SOURCE_REVISION,
            "matchBasis": "Exact source object label matches the frozen TA2 2.07 en_GB synonym `posterior crico-arytenoid muscle`; exact parent `Laryngeal muscles.g` and Laryngeal muscles/Neck collections disambiguate it from other laryngeal surfaces. Source `.l/.r` label and frozen source side agree. The T96 English field contains a recorded spelling variant; no fuzzy match, side inference, extent assertion, or HA binding is made.",
            "directObjectNameMatch": False,
            "ancestorNameAloneUsed": False,
            "upstreamFjOrTa2IdClaim": False,
            "canonicalHaBindingCreated": False,
            "humanReview": "not_performed",
            "relationKind": "qualified_target_synonym",
            "matchedTargetSynonym": synonym,
            "sourceSegmentCode": None,
            "memberCode": None,
            "matchEvidenceSourceIds": ["fipat-ta2-t96-full-target-catalog", "fipat-ta2-t78-frozen-full-context", "za-t99-frozen-source-objects"],
        })
        a_added.append({"sourceKey": key, "sourceName": source["name"], "side": source["sourceLabelSide"],
                        "targetId": "TA2:2196", "matchedFrozenT78Variant": synonym,
                        "sourceParent": source["parent"], "collections": source["collections"],
                        "evaluatedGeometrySha256": source["evaluatedGeometrySha256"]})

    # C: only the direct Korean fields are copied into the internal target-term
    # ledger. AI-context fields and the unresolved triquetrum conflict remain so.
    term_pack = read_json(RUN / "terminology-c/term-evidence.json")
    term_rows = {row["targetId"]: row for row in term_pack["rows"]}
    register = read_json(RUN / "terminology-c/term-source-register.json")
    sources = {source["sourceId"]: source for source in register["sources"]}
    term_1255 = term_rows["TA2:1255"]["fieldEvidence"]["koModern"]
    term_2481 = term_rows["TA2:2481"]["fieldEvidence"]
    if (term_1255["status"], term_1255["value"], term_1255["sourceIds"]) != (
        "direct_supported", "큰마름뼈", ["nikl-trapezium-565982"]
    ):
        raise ValueError("TA2:1255 direct NIKL term evidence changed")
    if (term_2481["koModern"]["status"], term_2481["koModern"]["value"],
        term_2481["koTraditional"]["status"], term_2481["koTraditional"]["value"]) != (
        "direct_supported", "노쪽손목굽힘근", "direct_supported", "요 수근 굴근"
    ):
        raise ValueError("TA2:2481 direct KSES field evidence changed")
    source_1255 = sources["nikl-trapezium-565982"]
    source_2481 = sources["kses-terms-p60"]
    nikl_evidence = evidence_source(
        source_1255, access_method="opened_html", exact_edition=None,
        edition_exposure="The opened 온용어 record identifies collection `21세기 세종 계획 전문 용어`, period 1998–2008, and record 565982; this is not asserted as current KAA adoption.",
        locator="record 565982; heading 큰마름뼈; English translation trapezium bone",
        retrieval_layer="opened_official_record",
    )
    kses_evidence = evidence_source(
        source_2481, access_method="opened_html", exact_edition=None,
        edition_exposure="The opened table exposes columns 대한의학 용어집 4판, 정형외과 용어집 2판, and 견관절 주관절학; publication years are not exposed.",
        locator="page 60 row `flexor carpi radialis`; recommended term/대한의학 용어집 4판 = 노쪽손목굽힘근; 정형외과 용어집 2판 and 견관절 주관절학 = 요 수근 굴근",
        retrieval_layer="opened_official_table",
    )
    append_once(overlay["evidenceSources"], nikl_evidence, "id")
    append_once(overlay["evidenceSources"], kses_evidence, "id")

    direct_term_updates = []
    for target_id, fields in {
        "TA2:1255": {"koModern": ("큰마름뼈", "nikl-trapezium-565982",
                                    "Opened NIKL record 565982: heading 큰마름뼈 and English translation trapezium bone; collection period 1998–2008 exposed." )},
        "TA2:2481": {
            "koModern": ("노쪽손목굽힘근", "kses-terms-p60",
                         "Opened KSES page 60, exact `flexor carpi radialis` row, 대한의학 용어집 4판 column."),
            "koTraditional": ("요 수근 굴근", "kses-terms-p60",
                              "Opened KSES page 60, exact `flexor carpi radialis` row, 정형외과 용어집 2판 and 견관절 주관절학 columns."),
        },
    }.items():
        term = next(row for row in overlay["targetTerminologyEvidence"] if row["targetId"] == target_id)
        proposal = term_rows[target_id]
        for field, (value, source_id, locator) in fields.items():
            proposed = proposal["fieldEvidence"][field]
            if proposed["status"] != "direct_supported" or proposed["value"] != value or proposed["sourceIds"] != [source_id]:
                raise ValueError(f"non-direct C term not eligible for {target_id}/{field}")
            current = term["fieldEvidence"][field]
            if current["status"] == "evidence_backed" and current["value"] != value:
                raise ValueError(f"conflicting existing term retained for {target_id}/{field}")
            term["names"][field] = value
            term["fieldEvidence"][field] = {
                "value": value, "sourceIds": [source_id], "locator": locator,
                "status": "evidence_backed", "missingReason": None,
            }
            if source_id not in term["targetTermSourceIds"]:
                term["targetTermSourceIds"].append(source_id)
            direct_term_updates.append({"targetId": target_id, "field": field, "value": value,
                                        "sourceId": source_id, "locator": locator})

    # Explicitly ensure the conflict and contextual AI proposals stayed unpromoted.
    term_by_id = {row["targetId"]: row for row in overlay["targetTerminologyEvidence"]}
    if term_by_id["TA2:1253"]["fieldEvidence"]["koModern"]["status"] != "missing" or term_by_id["TA2:1253"]["fieldEvidence"]["koTraditional"]["status"] != "missing":
        raise ValueError("TA2:1253 conflict was unexpectedly promoted")
    for target_id in ("TA2:2056", "TA2:2532"):
        if term_by_id[target_id]["fieldEvidence"]["koModern"]["status"] != "missing":
            raise ValueError(f"AI-only modern proposal unexpectedly promoted: {target_id}")

    # Add a local source context record for the precise frozen T78 variant used.
    t78_evidence = {
        "id": "fipat-ta2-t78-frozen-full-context",
        "url": "https://ta2viewer.openanatomy.org/",
        "sourceLabel": "FIPAT TA2 2.07 full hierarchy context frozen in T78",
        "exactEdition": "Terminologia Anatomica 2nd edition, vocabulary 2.07",
        "editionExposure": "Frozen local full-context file with exact upstream fields; this decision uses TA2 2196 term.en_GB only.",
        "accessDate": "2026-09-30",
        "accessMethod": "local_frozen_metadata",
        "locator": "work/evidence/T78/reference/ta2-scope.json#/id/2196/term/en_GB; `posterior crico-arytenoid muscle`",
        "retrievalLayer": "frozen_local_full_hierarchy_context",
        "openedOriginalDictionaryRecord": False,
        "openedOriginalSourcePage": False,
    }
    append_once(overlay["evidenceSources"], t78_evidence, "id")

    # These row-level gates must not be changed by the integration.
    if len(overlay["objects"]) != len(baseline_objects):
        raise ValueError("object denominator changed")
    for row in overlay["objects"]:
        baseline = baseline_objects[row["sourceKey"]]
        for field in ("haConceptId", "sourceOnly", "humanReview", "publicRedistribution", "localDisplayEligible",
                      "inspectionEligible", "defaultVisible", "sourceHiddenStatePreserved", "regionIds", "side"):
            if row.get(field) != baseline.get(field):
                raise ValueError(f"preservation invariant changed: {field} / {row['sourceKey']}")

    result = (json.dumps(overlay, ensure_ascii=False, indent=2) + "\n").encode()
    OVERLAY.write_bytes(result)
    report = {
        "schemaVersion": 1,
        "taskId": "T100",
        "runId": RUN_ID,
        "integrationRole": "independent adjudication of worker A/B/C deltas; common TypeScript validator is authoritative",
        "baselineOverlaySha256": before_sha,
        "finalOverlaySha256": sha(result),
        "accepted": {
            "TA2:1512": {
                "disposition": "accepted_exact_partial_member_routes_only",
                "why": "Ten source object labels independently specify distal phalanx, toe ordinal, and .l/.r; frozen parent and side metadata agree. Existing generic TA2:1505 evidence remains separate.",
                "extent": "unknown; no complete group extent asserted",
                "links": foot_added,
            },
            "TA2:2196": {
                "disposition": "accepted_exact_frozen_TA2_en_GB_synonym_pair_only",
                "why": "The opened T78 frozen TA2 2.07 entry gives exact en_GB `posterior crico-arytenoid muscle`; the two source labels match after only the explicit .l/.r suffix, and parent/collections identify the laryngeal context. Similar laryngeal names are excluded.",
                "extent": "one source surface per explicit side; no human review or completeness claim",
                "links": a_added,
            },
            "TA2:2261": {
                "disposition": "unresolved_side_conflict_preserved",
                "why": "One exact-name source object is unsided and the other is explicitly right; both carry side_conflicted and conceptKey=null. No side or selectable link is inferred.",
                "overlayMutation": False,
            },
        },
        "directKoreanTermFieldsAppliedToInternalLedgerOnly": direct_term_updates,
        "terminologyExceptions": {
            "TA2:1255": "Applied directly evidenced NIKL modern name `큰마름뼈`; retained the existing old-KMA3 portal traditional field `대능형골` with its edition limitation.",
            "TA2:2481": "Applied exact KSES page-60 modern `노쪽손목굽힘근` and traditional column `요 수근 굴근`; editions are column labels without publication years.",
            "TA2:2056": "Traditional `전두근` remains directly evidenced; AI-only modern `이마근` stays missing/unapplied.",
            "TA2:2532": "Traditional `손의 충양근` remains directly evidenced; AI-only modern `손 벌레근` stays missing/unapplied.",
            "TA2:1253": "Both Korean fields remain missing; synonym/legacy conflict and unopened underlying records prevent selection.",
        },
        "policy": {
            "scope": {"targets": 542, "memberships": 563, "regions": 12},
            "existingHaBindings": 130,
            "historical163": {"preserved": True, "counts": {"exactLabelObservation": 6, "descendantSurfaces": 20, "ancestorGroupSurfaces": 135, "frozenHierarchyNonObservation": 2}},
            "sourceOnly": True,
            "publicRedistribution": "held",
            "humanReview": "not_performed",
            "newCanonicalHaBindings": 0,
            "newGeometry": 0,
            "learnerNameOrAliasChanges": 0,
            "actualVisualQA": "not_performed_by_this_integration",
        },
    }
    (OUT / "integration-decisions.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"status": "applied", "baselineOverlaySha256": before_sha,
                      "finalOverlaySha256": sha(result), "TA2:1512Links": len(foot_added),
                      "TA2:2196Links": len(a_added), "directTermFields": len(direct_term_updates)}, indent=2))


if __name__ == "__main__":
    main()
