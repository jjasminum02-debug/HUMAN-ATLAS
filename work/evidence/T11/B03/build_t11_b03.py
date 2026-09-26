"""Build the bounded T11-B03 terminology evidence and learner name overlay."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
CHECKED = "2026-09-25"
FIPAT_ID = "fipat-ta2-b03-index"
FIPAT_URL = "https://fipat.library.dal.ca/wp-content/uploads/2020/09/FIPAT-TA2-Part-2.pdf"
FIPAT_EDITION = "Terminologia Anatomica, second edition (TA2), Part 2; online edition published 2019; hosted PDF path dated 2020-09."
KMLE_EDITION = "KMLE web aggregation; exact underlying dictionary edition/revision is not exposed on the checked page."

NAMES_PATH = ROOT / "atlas-data/terminology/learning-names.json"
BATCH_PATH = ROOT / "atlas-data/terminology/term-review-batches.json"

IDS = [f"HA-G-{number:06d}" for number in range(11, 17)] + [f"HA-M-{number:06d}" for number in range(7, 11)]
WIKI_BASE = "https://ko.wikipedia.org/w/index.php?title="

SOURCES = {
    FIPAT_ID: {
        "title": "FIPAT Terminologia Anatomica, second edition, Part 2 — B03 rows",
        "url": FIPAT_URL,
        "locator": "Part 2 printed pp. 74, 94–96; rows 2042–2045, 2597, 2603, 2643, 2651, 2654, 2669. Search-result text extraction exposes the row terms. Direct PDF open returned an internal/HTTP fetch error in this check; no local file, page image, column role or errata was inspected.",
        "edition": FIPAT_EDITION,
        "accessDate": CHECKED,
        "verificationMode": "official_hosted_PDF_search_result_text_only; direct_PDF_open_failed; no_visual_inspection",
        "scope": "TA2 nomenclature observation only. English/Latin table-cell roles and anatomical equivalence remain unreviewed.",
    },
    "kmle-b03-gluteus-near-match": {
        "title": "KMLE: generic gluteus term (near-match only)",
        "url": "https://m.kmle.co.kr/search.php?Search=gluteus",
        "locator": "Opened HTML: 대한의협 entry 'gluteus muscle' → 볼기근, 둔근 (page lines 26–28); old 대한의협 3 entry 'gluteus = glutaeus' → 둔근(臀筋) (lines 79–81); neurosurgery dictionary entry 'gluteus m.' → 볼기근, 둔근 / 臀筋 (lines 218–222). These are generic gluteus terms, not the superficial/deep gluteal groups.",
        "edition": KMLE_EDITION,
        "accessDate": CHECKED,
        "verificationMode": "opened_HTML_page_text; source_section_labels_visible_but_underlying_revisions_unexposed",
        "scope": "Negative/near-match evidence only; no generic gluteus Korean/Hanja term is assigned to either layer-specific group.",
    },
    "kmle-b03-intrinsic-foot-near-match": {
        "title": "KMLE: intrinsic muscles of foot (near-match only)",
        "url": "https://m.kmle.co.kr/search.php?Search=intrinsic+muscles+of+foot",
        "locator": "Search-result excerpt shows a CancerWEB definition for 'intrinsic muscles of foot' limited to muscles fully contained in the foot/toes, and generic 'foot' → 발/족. No Korean term for the complete TA2 'Muscles of foot' group is exposed. Direct open of the query page failed in this check.",
        "edition": "KMLE web aggregation; underlying CancerWEB entry is dated 2000-03-05 in the displayed excerpt, but exact dictionary edition/revision is not exposed.",
        "accessDate": CHECKED,
        "verificationMode": "search_result_excerpt_only; direct_HTML_open_failed; near_match_not_adopted",
        "scope": "Negative/near-match evidence only; intrinsic-only group is not equated to the TA2 whole muscles-of-foot row.",
    },
    "ko-wiki-b03-anterior-leg-compartment": {
        "title": "한국어 위키백과: 종아리앞칸",
        "url": WIKI_BASE + "종아리앞칸&oldid=39701799",
        "locator": "Opened fixed revision oldid=39701799: article title '종아리앞칸'; identification block names Latin 'compartimentum cruris anterius', English 'anterior compartment of the leg', and TA2 row 2643 (page lines 115–130). Last edited 2025-05-07. Used as a Korean string attestation, not a human-reviewed anatomy source.",
        "edition": "Living community-edited article; no edition is published. Exact captured revision oldid=39701799, last edited 2025-05-07.",
        "accessDate": CHECKED,
        "verificationMode": "opened_HTML_at_fixed_revision; title_and_identification_block_read",
        "scope": "Korean name/string cross-reference only. No human anatomy review performed.",
    },
    "ko-wiki-b03-lateral-leg-compartment": {
        "title": "한국어 위키백과: 종아리가쪽칸",
        "url": WIKI_BASE + "종아리가쪽칸&oldid=39701801",
        "locator": "Opened fixed revision oldid=39701801: article title '종아리가쪽칸'; identification block names Latin 'compartimentum cruris laterale', English 'lateral compartment of leg', and TA2 row 2651 (page lines 116–131). Last edited 2025-05-07. Used as a Korean string attestation, not a human-reviewed anatomy source.",
        "edition": "Living community-edited article; no edition is published. Exact captured revision oldid=39701801, last edited 2025-05-07.",
        "accessDate": CHECKED,
        "verificationMode": "opened_HTML_at_fixed_revision; title_and_identification_block_read",
        "scope": "Korean name/string cross-reference only. No human anatomy review performed.",
    },
    "ko-wiki-b03-posterior-leg-compartment": {
        "title": "한국어 위키백과: 종아리뒤칸",
        "url": WIKI_BASE + "종아리뒤칸&oldid=39701625",
        "locator": "Opened fixed revision oldid=39701625: article title '종아리뒤칸'; identification block names Latin 'compartimentum cruris posterius', English 'posterior compartment of leg', and TA2 row 2654 (page lines 119–137). Last edited 2025-05-07. Article text notes superficial and deep layers; the term is not narrowed to the deep layer. Used as a Korean string attestation, not a human-reviewed anatomy source.",
        "edition": "Living community-edited article; no edition is published. Exact captured revision oldid=39701625, last edited 2025-05-07.",
        "accessDate": CHECKED,
        "verificationMode": "opened_HTML_at_fixed_revision; title_and_identification_block_read",
        "scope": "Korean name/string cross-reference only. No human anatomy review performed.",
    },
    "nikl-b03-superior-rectus": {
        "title": "국립국어원 온용어: 상직근",
        "url": "https://kli.korean.go.kr/term/trgtWord/indexTrgtWord.do?trgtWordNo=2251777",
        "locator": "Opened entry '상직근': source Hanja 上直筋; English equivalents 'superior rectus' and 'superior rectus muscle'; synonym '위^곧은근' (page lines 187–228). Page states the underlying 우리말샘 terminology data is as of June 2023.",
        "edition": "우리말샘 specialist terminology snapshot 2023-06, as stated by the National Institute of Korean Language OnTerm page; OnTerm page revision date is not exposed.",
        "accessDate": CHECKED,
        "verificationMode": "opened_HTML_primary_terminology_entry",
        "scope": "Terminology string attestation only; the page's definition is not imported as an anatomy claim.",
    },
    "kmle-b03-inferior-rectus": {
        "title": "KMLE: inferior rectus terms",
        "url": "https://m.kmle.co.kr/search.php?Search=rectus+muscle+of+thigh",
        "locator": "Opened HTML: inferior rectus result shows '아래곧은선, 하직근(下直筋)' and '아래곧은근' (lines 275–285); named 대한해부학회 section gives '아래곧은근' and old term '하직근' (lines 378–381). The query is broad; each noted result is the exact inferior-rectus item. Source dictionary revision is not exposed.",
        "edition": KMLE_EDITION,
        "accessDate": CHECKED,
        "verificationMode": "opened_HTML_page_text; named_dictionary_sections_visible_but_source_revisions_unexposed",
        "scope": "Terminology spelling only; no anatomy claim imported.",
    },
    "kmle-b03-medial-rectus": {
        "title": "KMLE: medial rectus terms",
        "url": "https://m.kmle.co.kr/search.php?Search=medial+rectus",
        "locator": "Opened HTML: 대한신경외과학회 entry 'medial rectus m.' → 안쪽곧은근, 내직근 / 內直筋 (lines 421–433); 대한해부학회 entry gives '안쪽곧은근' with old term '내측직근' (lines 329–338). The source dictionary revision is not exposed.",
        "edition": KMLE_EDITION,
        "accessDate": CHECKED,
        "verificationMode": "opened_HTML_page_text; named_dictionary_sections_visible_but_source_revisions_unexposed",
        "scope": "Terminology spelling only; no anatomy claim imported.",
    },
    "kmle-b03-lateral-rectus": {
        "title": "KMLE: lateral rectus terms",
        "url": "https://m.kmle.co.kr/search.php?Search=lateral+rectus+muscle",
        "locator": "Opened HTML: old 대한의협 3 entry 'lateral rectus muscle' → 외직근(外直筋) and '가쪽곧은근' (lines 296–320); 대한해부학회 section gives '가쪽곧은근' and old term '외측직근' (lines 388–397). The source dictionary revision is not exposed.",
        "edition": KMLE_EDITION,
        "accessDate": CHECKED,
        "verificationMode": "opened_HTML_page_text; named_dictionary_sections_visible_but_source_revisions_unexposed",
        "scope": "Terminology spelling only; no anatomy claim imported.",
    },
}

TERMS = {
    "HA-G-000011": {"label": None, "korean": None, "hanja": None, "labelSource": ["kmle-b03-gluteus-near-match"], "koreanSource": ["kmle-b03-gluteus-near-match"], "hanjaSource": ["kmle-b03-gluteus-near-match"], "missing": "The checked KMLE entry attests only generic gluteus / 볼기근 / 둔근(臀筋), not the superficial gluteal group. No group name was inferred.", "candidates": ["볼기근", "둔근", "臀筋"]},
    "HA-G-000012": {"label": None, "korean": None, "hanja": None, "labelSource": ["kmle-b03-gluteus-near-match"], "koreanSource": ["kmle-b03-gluteus-near-match"], "hanjaSource": ["kmle-b03-gluteus-near-match"], "missing": "The checked KMLE entry attests only generic gluteus / 볼기근 / 둔근(臀筋), not the deep gluteal group. No group name was inferred.", "candidates": ["볼기근", "둔근", "臀筋"]},
    "HA-G-000013": {"label": "종아리앞칸", "korean": "종아리앞칸", "hanja": None, "labelSource": ["ko-wiki-b03-anterior-leg-compartment"], "koreanSource": ["ko-wiki-b03-anterior-leg-compartment"], "hanjaSource": ["ko-wiki-b03-anterior-leg-compartment"], "missing": "The checked Korean article provides no Hanja form for this group; no characters were generated.", "labelState": "attested_korean_page_title", "koreanState": "attested_korean_page_title"},
    "HA-G-000014": {"label": "종아리가쪽칸", "korean": "종아리가쪽칸", "hanja": None, "labelSource": ["ko-wiki-b03-lateral-leg-compartment"], "koreanSource": ["ko-wiki-b03-lateral-leg-compartment"], "hanjaSource": ["ko-wiki-b03-lateral-leg-compartment"], "missing": "The checked Korean article provides no Hanja form for this group; no characters were generated.", "labelState": "attested_korean_page_title", "koreanState": "attested_korean_page_title"},
    "HA-G-000015": {"label": "종아리뒤칸", "korean": "종아리뒤칸", "hanja": None, "labelSource": ["ko-wiki-b03-posterior-leg-compartment"], "koreanSource": ["ko-wiki-b03-posterior-leg-compartment"], "hanjaSource": ["ko-wiki-b03-posterior-leg-compartment"], "missing": "The checked Korean article provides no Hanja form for this group; no characters were generated.", "labelState": "attested_korean_page_title", "koreanState": "attested_korean_page_title"},
    "HA-G-000016": {"label": None, "korean": None, "hanja": None, "labelSource": ["kmle-b03-intrinsic-foot-near-match"], "koreanSource": ["kmle-b03-intrinsic-foot-near-match"], "hanjaSource": ["kmle-b03-intrinsic-foot-near-match"], "missing": "The checked KMLE excerpt describes intrinsic muscles of foot and generic 발/족, not the complete TA2 muscles-of-foot group. No whole-group Korean/Hanja term was inferred.", "candidates": ["intrinsic muscles of foot"]},
    "HA-M-000007": {"label": "상직근", "korean": "위곧은근", "hanja": "上直筋", "labelSource": ["nikl-b03-superior-rectus"], "koreanSource": ["nikl-b03-superior-rectus"], "hanjaSource": ["nikl-b03-superior-rectus"], "labelState": "attested_customary_hanja_name", "koreanState": "attested_korean_synonym", "hanjaState": "attested_source_hanja"},
    "HA-M-000008": {"label": "하직근", "korean": "아래곧은근", "hanja": "下直筋", "labelSource": ["kmle-b03-inferior-rectus"], "koreanSource": ["kmle-b03-inferior-rectus"], "hanjaSource": ["kmle-b03-inferior-rectus"], "labelState": "attested_customary_hanja_name", "koreanState": "attested_current_korean_name", "hanjaState": "attested_source_hanja"},
    "HA-M-000009": {"label": "내직근", "korean": "안쪽곧은근", "hanja": "內直筋", "labelSource": ["kmle-b03-medial-rectus"], "koreanSource": ["kmle-b03-medial-rectus"], "hanjaSource": ["kmle-b03-medial-rectus"], "labelState": "attested_customary_hanja_name", "koreanState": "attested_current_korean_name", "hanjaState": "attested_source_hanja"},
    "HA-M-000010": {"label": "외직근", "korean": "가쪽곧은근", "hanja": "外直筋", "labelSource": ["kmle-b03-lateral-rectus"], "koreanSource": ["kmle-b03-lateral-rectus"], "hanjaSource": ["kmle-b03-lateral-rectus"], "labelState": "attested_customary_hanja_name", "koreanState": "attested_current_korean_name", "hanjaState": "attested_source_hanja"},
}


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def evidence(source_id: str, locator: str | None = None):
    source = SOURCES[source_id]
    return {
        "sourceId": source_id,
        "locator": locator or source["locator"],
        "verificationMode": source["verificationMode"],
        "sourceEdition": source["edition"],
        "checkedDate": CHECKED,
    }


def field_record(identifier: str, field: str, value, state: str, source_ids: list[str], *, source_value=None, missing_reason=None, source_locators=None):
    return {
        "entryId": identifier,
        "field": field,
        "value": value,
        "state": state,
        "evidence": [evidence(source_id, (source_locators or {}).get(source_id)) for source_id in source_ids],
        "sourceValue": source_value,
        "missingReason": missing_reason,
        "humanAnatomyReviewStatus": "not_performed",
        "humanReviewed": False,
    }


def main():
    names = read_json(NAMES_PATH)
    batches = read_json(BATCH_PATH)
    rows = [row for row in batches["canonicalCoverage"] if row["batchId"] == "T11-B03"]
    if [row["id"] for row in rows] != IDS:
        raise SystemExit("T11-B03 assignment changed; refusing to touch any other IDs")
    if any(row["status"] != "not_started" for row in rows):
        raise SystemExit("T11-B03 already has status; refusing a non-idempotent rebuild")
    if any(row["id"] in {entry["id"] for entry in batches["entries"]} for row in rows):
        raise SystemExit("A T11-B03 evidence entry already exists; refusing duplicate data")
    if any(entry["id"] in set(IDS) for entry in names["entries"]):
        raise SystemExit("A T11-B03 overlay entry already exists; refusing duplicate data")

    crosswalk = read_json(ROOT / "atlas-data/catalog/source-crosswalk.json")
    canonical_data = read_json(ROOT / "atlas-data/catalog/canonical-catalog.json")["entities"]
    canonical = {row["id"]: row for row in canonical_data["muscleConcepts"]}
    crosswalk_terms = {identifier: {term["sourceLanguage"]: term for term in crosswalk["termRecords"] if term["conceptId"] == identifier and term["sourceTextObserved"]} for identifier in IDS}

    new_entries = []
    flat_field_evidence = []
    overlay = []
    for row in rows:
        identifier = row["id"]
        concept = canonical[identifier]
        loc = row["sourceCrosswalkLocator"]
        terms = crosswalk_terms[identifier]
        if terms.get("en", {}).get("sourceTextObserved") != loc["englishTextObservation"]:
            raise SystemExit(f"English observation mismatch for {identifier}")
        if terms.get("la", {}).get("sourceTextObserved") != loc["latinTextObservation"]:
            raise SystemExit(f"Latin observation mismatch for {identifier}")

        value = TERMS[identifier]
        display_english = loc["englishTextObservation"]
        latin = loc["latinTextObservation"]
        english_locator = f"TA2 Part 2 printed p. {loc['printedPage']}, table row {loc['tableRow']}: English text observation '{display_english}' in official hosted-PDF search-result text; table-cell role remains unverified and original PDF was not visually checked."
        latin_locator = f"TA2 Part 2 printed p. {loc['printedPage']}, table row {loc['tableRow']}: Latin text observation '{latin}' in official hosted-PDF search-result text; table-cell role remains unverified and original PDF was not visually checked."
        item_fields = [
            field_record(identifier, "label", value["label"], value.get("labelState", "missing_unverified_scope_mismatch" if value["label"] is None else "attested_web_korean_name"), value["labelSource"], missing_reason=value.get("missing") if value["label"] is None else None),
            field_record(identifier, "korean", value["korean"], value.get("koreanState", "missing_unverified_scope_mismatch" if value["korean"] is None else "attested_web_korean_name"), value["koreanSource"], missing_reason=value.get("missing") if value["korean"] is None else None),
            field_record(identifier, "hanja", value["hanja"], value.get("hanjaState", "missing_not_observed" if value["hanja"] is None else "attested_source_hanja"), value["hanjaSource"], missing_reason=value.get("missing") if value["hanja"] is None else None),
            field_record(identifier, "english", display_english, "TA2_search_index_observation_cell_role_unverified", [FIPAT_ID], source_value=loc["englishTextObservation"], source_locators={FIPAT_ID: english_locator}),
            field_record(identifier, "aliases[0]", latin, "TA2_search_index_observation_cell_role_unverified", [FIPAT_ID], source_value=loc["latinTextObservation"], source_locators={FIPAT_ID: latin_locator}),
        ]
        flat_field_evidence.extend(item_fields)
        name_record = {
            "id": identifier,
            "label": value["label"],
            "korean": value["korean"],
            "english": display_english,
            "hanja": value["hanja"],
            "aliases": [latin],
            "sourceIds": sorted({FIPAT_ID, *value["labelSource"], *value["koreanSource"], *value["hanjaSource"]}),
            "parentId": concept.get("parentId"),
            "entityType": concept["entityType"],
            "lookupOnly": False,
            "status": "web_attested_with_gaps",
            "humanReviewed": False,
            "hanjaNote": "출처에서 확인된 표기만 기록했다. 사람의 해부학 검토는 수행하지 않았다." if value["hanja"] else value.get("missing"),
        }
        if value["label"] is not None:
            overlay.append(name_record)
        else:
            name_record["withheldFromLearnerOverlay"] = True

        entry = {
            "id": identifier,
            "isCanonical": True,
            "entityType": concept["entityType"],
            "parentId": concept.get("parentId"),
            "lookupOnly": False,
            "canonicalStatus": "canonical_existing_id",
            "canonicalSourceRow": {"sourceId": "FIPAT_TA2", "tableRow": loc["tableRow"], "printedPage": loc["printedPage"]},
            "displayField": "label",
            "displayValue": value["label"],
            "fieldEvidence": item_fields,
            "webVerificationStatus": "web_checked_with_gaps",
            "humanAnatomyReviewStatus": "not_performed",
            "humanReviewer": None,
            "humanReviewed": False,
            "fieldEvidenceCount": len(item_fields),
        }
        if value.get("candidates"):
            entry["unadoptedCandidates"] = [
                {"value": candidate, "status": "near_match_not_linked", "sourceIds": value["labelSource"], "reason": value["missing"]}
                for candidate in value["candidates"]
            ]
        new_entries.append(entry)
        row["status"] = "web_checked_with_gaps"
        row["statusReason"] = "TA2 indexed English/Latin terms and field-level web term evidence recorded; Korean/Hanja gaps and source limitations remain explicit; human anatomy review was not performed."

    for source_id, source in SOURCES.items():
        names["sources"][source_id] = source
    batches["sources"].update(SOURCES)
    names["entries"].extend(overlay)
    batches["entries"].extend(new_entries)
    batches["fieldEvidence"].extend(flat_field_evidence)
    batches["checkedDate"] = CHECKED
    batches["revision"] = "T11-B03-web-checked-2026-09-25"
    batches["overallT11Status"] = "in_progress_partial"
    for batch in batches["batchOrder"]:
        if batch["batchId"] == "T11-B03":
            batch["status"] = "complete_with_gaps"
    batches["notes"].append("T11-B03 completed with gaps: 10 assigned existing IDs; 50 field evidence rows; 7 learner display overlays; TA2 terms remain search-index/crosswalk observations without local visual PDF review; three group Korean labels withheld on scope mismatch; human anatomy review was not performed.")
    names["revision"] = "T11-B03-web-checked-2026-09-25"
    names["accessedAt"] = CHECKED

    write_json(NAMES_PATH, names)
    write_json(BATCH_PATH, batches)
    print(json.dumps({
        "batchId": "T11-B03",
        "canonicalIds": IDS,
        "batchFieldEvidence": len(flat_field_evidence),
        "totalFieldEvidence": len(batches["fieldEvidence"]),
        "newLearnerNames": len(overlay),
        "totalLearnerNames": len(names["entries"]),
        "withheldLabels": [identifier for identifier in IDS if TERMS[identifier]["label"] is None],
        "batchStatus": "complete_with_gaps",
        "humanReviewed": False,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
