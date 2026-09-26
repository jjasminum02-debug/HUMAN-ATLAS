"""Build only the assigned T11-B06 term provenance and search overlay."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
CHECKED = "2026-09-25"
IDS = [f"HA-M-{number:06d}" for number in range(32, 42)]
FIPAT_ID = "fipat-ta2-b06-opened-original-pdf"
FIPAT_URL = "https://cdn.dal.ca/content/dam/dalhousie/pdf/library/FIPAT/TA2/FIPAT-TA2-Part-2.pdf"
FIPAT_EDITION = "Terminologia Anatomica, Second Edition (2.07), TA2 Part II; bibliographic citation 2019; approved and adopted by the IFAA General Assembly in 2020."
KMLE_EDITION = "KMLE web dictionary aggregation; exact underlying dictionary edition/revision is not exposed unless an entry-level display date is noted."
NAMES_PATH = ROOT / "atlas-data/terminology/learning-names.json"
BATCH_PATH = ROOT / "atlas-data/terminology/term-review-batches.json"

ROWS = {
    "HA-M-000032": (2458, 89, "P68"),
    "HA-M-000033": (2459, 89, "P68"),
    "HA-M-000034": (2460, 89, "P68"),
    "HA-M-000035": (2464, 89, "P68"),
    "HA-M-000036": (2468, 89, "P68"),
    "HA-M-000037": (2469, 89, "P68"),
    "HA-M-000038": (2471, 89, "P68"),
    "HA-M-000039": (2598, 94, "P73"),
    "HA-M-000040": (2599, 94, "P73"),
    "HA-M-000041": (2600, 94, "P73"),
}

SOURCES = {
    FIPAT_ID: {
        "title": "FIPAT Terminologia Anatomica, Second Edition (2.07), Part II — directly opened official Dalhousie-hosted PDF",
        "url": FIPAT_URL,
        "locator": "104-page TA2 Part II PDF. Front matter identifies Second Edition (2.07), cites the 2019 publication, and states IFAA General Assembly approval/adoption in 2020. Chapter 4 table header is PDF text page P52 / printed p. 73 and names Latin term, Latin synonym, UK English, US English, English synonym, Other. Assigned rows: printed p. 89 rows 2458–2471 (selected rows 2458, 2459, 2460, 2464, 2468, 2469, 2471) and printed p. 94 rows 2598–2600. Text layer opened and read; no local copy or visual page screenshot created.",
        "edition": FIPAT_EDITION,
        "accessDate": CHECKED,
        "verificationMode": "official_Dalhousie_hosted_original_PDF_directly_opened; front_matter_Ch4_header_and_assigned_text_rows_read; no_visual_page_screenshot",
        "scope": "TA2 term strings and table column roles only; no anatomical identity approval, structure, function, attachment, or clinical claim; human anatomy review not performed.",
    },
    "kmle-b06-infraspinatus": {
        "title": "KMLE infraspinatus / musculus infraspinatus term search result",
        "url": "https://m.kmle.co.kr/search.php?Search=musculus+infraspinatus",
        "locator": "Search-result excerpt: 대한해부학회 Infraspinatus m. → 가시아래근 [옛 용어] 극하근. Old 대한의협 3 exact infraspinatus rows show 극하근(棘下筋); another musculus infraspinatus result shows 극하 근(極下筋), retained separately as a competing candidate. Direct open returned cache miss; exact underlying dictionary edition/revision is not exposed.",
        "edition": KMLE_EDITION,
        "accessDate": CHECKED,
        "verificationMode": "KMLE_search_index_excerpt_only; direct_HTML_open_failed_cache_miss; competing_Hanja_observation_kept_separate; underlying_dictionary_edition_unexposed",
        "scope": "Name spelling only; no anatomical interpretation or human review.",
    },
    "kmle-b06-teres-minor-korean": {
        "title": "KMLE teres minor Korean term search result",
        "url": "https://m.kmle.co.kr/search.php?Search=teres+minor+muscle",
        "locator": "Search-result excerpt: 대한해부학회 Teres minor m. → 작은원근 [옛 용어] 소원근; legacy dictionary results show the same customary/current Korean pair. Exact underlying edition/revision is not exposed; direct HTML was not obtained.",
        "edition": KMLE_EDITION,
        "accessDate": CHECKED,
        "verificationMode": "KMLE_search_index_excerpt_only; underlying_dictionary_edition_unexposed",
        "scope": "Name spelling only; no anatomical interpretation or human review.",
    },
    "kmle-b06-teres-minor-hanja": {
        "title": "KMLE teres minor Hanja result",
        "url": "https://m.kmle.co.kr/search.php?Search=teres+minor+m",
        "locator": "Search-result excerpt, 대한신경외과학회 table: teres minor m. → 작은원근, 소원근(小圓筋). Other legacy results display 小園筋 and 小圓形筋; they are recorded as unadopted candidates, not merged. Direct HTML returned Unicode decoding error; exact underlying edition/revision is not exposed.",
        "edition": KMLE_EDITION,
        "accessDate": CHECKED,
        "verificationMode": "KMLE_search_index_excerpt_only; direct_HTML_open_failed_Unicode_decoding_error; competing_Hanja_forms_kept_separate; underlying_dictionary_edition_unexposed",
        "scope": "Exact displayed term/Hanja string only; no anatomical equivalence approval.",
    },
    "kmle-b06-subscapularis": {
        "title": "KMLE subscapularis term and legacy Hanja search result",
        "url": "https://m.kmle.co.kr/search.php?Search=musculus+subscapularis",
        "locator": "Search-result excerpt: subscapularis muscle → 어깨밑근, 견갑하근; legacy musculus subscapularis item → 견갑오목근, 견갑하근(肩甲下筋). CancerWEB result lists subscapular muscle as a synonym (entry date displayed as 05 Mar 2000). Direct HTML returned Unicode decoding error; exact Korean dictionary edition/revision is not exposed.",
        "edition": "KMLE web aggregation; CancerWEB entry displays 05 Mar 2000; exact underlying Korean dictionary edition/revision is not exposed.",
        "accessDate": CHECKED,
        "verificationMode": "KMLE_search_index_excerpt_only; direct_HTML_open_failed_Unicode_decoding_error; CancerWEB_entry_date_visible_in_excerpt; underlying_Korean_dictionary_edition_unexposed",
        "scope": "Name spellings and explicit synonym only; no anatomy statement imported.",
    },
    "kmle-b06-biceps-brachii": {
        "title": "KMLE biceps brachii term and legacy Hanja search result",
        "url": "https://m.kmle.co.kr/search.php?Search=biceps+brachii+muscle",
        "locator": "Search-result excerpt: 대한해부학회 Biceps brachii m. → 위팔두갈래근 [옛 용어] 상완이두근; old 대한의협 3 musculus biceps brachii item → 상완이두근(上腕二頭筋). KMLE result is a search-index excerpt; the exact underlying dictionary edition/revision is not exposed and the original source dictionary was not opened.",
        "edition": KMLE_EDITION,
        "accessDate": CHECKED,
        "verificationMode": "KMLE_search_index_excerpt_only; underlying_dictionary_edition_unexposed",
        "scope": "Name spelling only; no anatomical interpretation or human review.",
    },
    "kmle-b06-coracobrachialis": {
        "title": "KMLE coracobrachialis term and English synonym page",
        "url": "https://m.kmle.co.kr/search.php?Search=coracobrachialis",
        "locator": "Opened KMLE HTML: lines 18–20, 대한의협 coracobrachialis muscle → 부리위팔근, 오훼완근; lines 67–70, 대한해부학회 Coracobrachialis m. → 부리위팔근 [옛 용어] 오훼완근; CancerWEB lines 84–88 give coracobrachial muscle and Casser's perforated muscle synonyms and display date 05 Mar 2000. KMLE page does not expose a full Hanja form for this exact item.",
        "edition": "KMLE web aggregation; CancerWEB item displays 05 Mar 2000; exact underlying current/legacy dictionary edition/revision is not exposed.",
        "accessDate": CHECKED,
        "verificationMode": "KMLE_aggregate_HTML_opened; specific_dictionary_entries_and_CancerWEB_synonyms_visible; underlying_dictionary_edition_unexposed; no_Hanja_in_exact_entry",
        "scope": "Term spellings and explicit English synonyms only; no anatomy description imported.",
    },
    "secondary-b06-coracobrachialis-hanja-candidate": {
        "title": "Namu wiki coracobrachialis page — unadopted Hanja candidate only",
        "url": "https://d.namu.moe/w/%EB%B6%80%EB%A6%AC%EC%9C%84%ED%8C%94%EA%B7%BC",
        "locator": "Search-result excerpt, overview section: page says prior term 오훼완근(烏喙腕筋), and separately 오구완근(烏口腕筋); footnote [2] underlying primary terminology source was not independently located. No field value is adopted from this candidate.",
        "edition": "Collaboratively edited wiki page; exact revision and cited primary Hanja source edition not verified.",
        "accessDate": CHECKED,
        "verificationMode": "search_index_excerpt_only; secondary_candidate_not_adopted; cited_primary_source_not_verified",
        "scope": "Records a missing-field candidate only; does not support learner hanja or human anatomy review.",
    },
    "kmle-b06-brachialis": {
        "title": "KMLE brachialis term, Hanja, and English synonym page",
        "url": "https://m.kmle.co.kr/search.php?Search=brachialis",
        "locator": "Opened KMLE HTML: lines 14–16, 대한의협 brachialis muscle → 위팔근, 상완근; lines 108–111, 대한해부학회 Brachialis m. → 위팔근 [옛 용어] 상완근; lines 121–125, 대한신경외과학회 brachialis m. → 위팔근, 상완근 / 上腕筋; CancerWEB lines 151–153 explicitly list brachial muscle synonym and date 05 Mar 2000.",
        "edition": "KMLE web aggregation; CancerWEB item displays 05 Mar 2000; exact underlying Korean dictionary edition/revision is not exposed.",
        "accessDate": CHECKED,
        "verificationMode": "KMLE_aggregate_HTML_opened; named_dictionary_sections_and_CancerWEB_synonym_visible; underlying_dictionary_edition_unexposed",
        "scope": "Term spellings and explicit English synonym only; no anatomy description imported.",
    },
    "kmle-b06-triceps-brachii": {
        "title": "KMLE triceps brachii term, legacy Hanja and English synonym search result",
        "url": "https://m.kmle.co.kr/search.php?Search=triceps+brachii",
        "locator": "Search-result excerpt: 대한해부학회 Triceps brachii m. → 위팔세갈래근 [옛 용어] 상완삼두근; old 대한의협 3 result shows 상완삼두근(上腕三頭筋); CancerWEB entry gives `triceps muscle of arm` as a synonym and date 05 Mar 2000. Direct HTML open was inaccessible; exact underlying Korean dictionary edition/revision is not exposed.",
        "edition": "KMLE web aggregation; CancerWEB item displays 05 Mar 2000; exact underlying Korean dictionary edition/revision is not exposed.",
        "accessDate": CHECKED,
        "verificationMode": "KMLE_search_index_excerpt_only; direct_HTML_open_not_accessible; CancerWEB_entry_date_visible_in_excerpt; underlying_Korean_dictionary_edition_unexposed",
        "scope": "Term spellings and explicit English synonym only; no anatomy description imported.",
    },
    "kmle-b06-gluteus": {
        "title": "KMLE gluteus maximus, medius, and minimus page",
        "url": "https://m.kmle.co.kr/search.php?Search=gluteus",
        "locator": "Opened KMLE HTML: old 대한의협 3 term rows at lines 124–145 give musculus gluteus maximus/medius/minimus → 대둔근(大臀筋), 중둔근(中臀筋), 소둔근(小臀筋); 대한해부학회 lines 170–183 give 큰볼기근/중간볼기근/작은볼기근 and legacy names; CancerWEB lines 261–283 show English entries/synonyms, including mesogluteus for medius and date 05 Mar 2000.",
        "edition": "KMLE web aggregation; CancerWEB entries display 05 Mar 2000; exact underlying Korean dictionary edition/revision is not exposed.",
        "accessDate": CHECKED,
        "verificationMode": "KMLE_aggregate_HTML_opened; legacy_Hanja_and_current_Korean_sections_visible; CancerWEB_synonym_visible; underlying_dictionary_edition_unexposed",
        "scope": "Name spellings and explicit synonym only; no anatomy description imported.",
    },
}

TERMS = {
    "HA-M-000032": {
        "label": "극하근", "korean": "가시아래근", "hanja": "棘下筋",
        "labelSource": ["kmle-b06-infraspinatus"], "koreanSource": ["kmle-b06-infraspinatus"], "hanjaSource": ["kmle-b06-infraspinatus"],
        "extraAliases": [],
        "unadopted": [
            {"field": "hanja", "value": "極下筋", "state": "competing_legacy_Hanja_candidate", "sourceIds": ["kmle-b06-infraspinatus"], "reason": "A separate musculus infraspinatus result shows this distinct character string; the exact infraspinatus old-대한의협 3 rows show 棘下筋. Retain the competing display as unresolved instead of adding it as a search alias."},
            {"field": "aliases", "value": "Muculus infra spinam", "state": "TA2_other_cell_not_adopted", "sourceIds": [FIPAT_ID], "reason": "This is the exact TA2 text-layer string in Other, but its irregular form is not corroborated by a second source; do not turn it into an alias."},
        ],
    },
    "HA-M-000033": {
        "label": "소원근", "korean": "작은원근", "hanja": "小圓筋",
        "labelSource": ["kmle-b06-teres-minor-korean"], "koreanSource": ["kmle-b06-teres-minor-korean"], "hanjaSource": ["kmle-b06-teres-minor-hanja"],
        "extraAliases": [],
        "unadopted": [
            {"field": "hanja", "value": "小園筋", "state": "conflicting_legacy_Hanja_candidate", "sourceIds": ["kmle-b06-teres-minor-hanja"], "reason": "A separate KMLE legacy result shows 小園筋 for a teres minor entry; it conflicts by character with 小圓筋 and is not added to the learner overlay."},
            {"field": "hanja", "value": "小圓形筋", "state": "alternate_legacy_Hanja_term_not_adopted", "sourceIds": ["kmle-b06-teres-minor-hanja"], "reason": "KMLE displays this longer form in a distinct legacy result; exact preferred spelling is unresolved and it is not added to the learner overlay."},
        ],
    },
    "HA-M-000034": {
        "label": "견갑하근", "korean": "어깨밑근", "hanja": "肩甲下筋",
        "labelSource": ["kmle-b06-subscapularis"], "koreanSource": ["kmle-b06-subscapularis"], "hanjaSource": ["kmle-b06-subscapularis"],
        "extraAliases": [
            {"field": "aliases[1]", "value": "subscapular muscle", "sourceId": "kmle-b06-subscapularis", "state": "KMLE_CancerWEB_explicit_English_synonym"},
        ],
        "unadopted": [],
    },
    "HA-M-000035": {
        "label": "상완이두근", "korean": "위팔두갈래근", "hanja": "上腕二頭筋",
        "labelSource": ["kmle-b06-biceps-brachii"], "koreanSource": ["kmle-b06-biceps-brachii"], "hanjaSource": ["kmle-b06-biceps-brachii"],
        "extraAliases": [], "unadopted": [],
    },
    "HA-M-000036": {
        "label": "오훼완근", "korean": "부리위팔근", "hanja": None,
        "labelSource": ["kmle-b06-coracobrachialis"], "koreanSource": ["kmle-b06-coracobrachialis"], "hanjaSource": ["kmle-b06-coracobrachialis", "secondary-b06-coracobrachialis-hanja-candidate"],
        "hanjaMissingReason": "KMLE exact coracobrachialis term rows attest 오훼완근/부리위팔근 but expose no full Hanja. A secondary wiki search excerpt shows 烏喙腕筋 and 烏口腕筋 while its cited primary source and edition are not verified; neither candidate is adopted.",
        "extraAliases": [
            {"field": "aliases[1]", "value": "Casserio's muscle", "sourceId": FIPAT_ID, "state": "TA2_Other_cell_synonym"},
            {"field": "aliases[2]", "value": "Casser's perforated muscle", "sourceId": "kmle-b06-coracobrachialis", "state": "KMLE_CancerWEB_explicit_English_synonym"},
            {"field": "aliases[3]", "value": "coracobrachial muscle", "sourceId": "kmle-b06-coracobrachialis", "state": "KMLE_CancerWEB_explicit_English_synonym"},
        ],
        "unadopted": [
            {"field": "hanja", "value": "烏喙腕筋", "state": "secondary_Hanja_candidate_not_adopted", "sourceIds": ["secondary-b06-coracobrachialis-hanja-candidate"], "reason": "Observed only in a secondary wiki excerpt with an unverified footnote source; the exact primary source edition/locator was not established."},
            {"field": "hanja", "value": "烏口腕筋", "state": "secondary_Hanja_candidate_not_adopted", "sourceIds": ["secondary-b06-coracobrachialis-hanja-candidate"], "reason": "Observed only in a secondary wiki excerpt with an unverified footnote source; the exact primary source edition/locator was not established."},
        ],
    },
    "HA-M-000037": {
        "label": "상완근", "korean": "위팔근", "hanja": "上腕筋",
        "labelSource": ["kmle-b06-brachialis"], "koreanSource": ["kmle-b06-brachialis"], "hanjaSource": ["kmle-b06-brachialis"],
        "extraAliases": [
            {"field": "aliases[1]", "value": "brachial muscle", "sourceId": "kmle-b06-brachialis", "state": "KMLE_CancerWEB_explicit_English_synonym"},
        ], "unadopted": [],
    },
    "HA-M-000038": {
        "label": "상완삼두근", "korean": "위팔세갈래근", "hanja": "上腕三頭筋",
        "labelSource": ["kmle-b06-triceps-brachii"], "koreanSource": ["kmle-b06-triceps-brachii"], "hanjaSource": ["kmle-b06-triceps-brachii"],
        "extraAliases": [
            {"field": "aliases[1]", "value": "triceps muscle of arm", "sourceId": "kmle-b06-triceps-brachii", "state": "KMLE_CancerWEB_explicit_English_synonym"},
        ], "unadopted": [],
    },
    "HA-M-000039": {
        "label": "대둔근", "korean": "큰볼기근", "hanja": "大臀筋",
        "labelSource": ["kmle-b06-gluteus"], "koreanSource": ["kmle-b06-gluteus"], "hanjaSource": ["kmle-b06-gluteus"],
        "extraAliases": [
            {"field": "aliases[1]", "value": "Musculus glutaeus maximus", "sourceId": FIPAT_ID, "state": "TA2_Other_cell_Latin_synonym"},
        ], "unadopted": [],
    },
    "HA-M-000040": {
        "label": "중둔근", "korean": "중간볼기근", "hanja": "中臀筋",
        "labelSource": ["kmle-b06-gluteus"], "koreanSource": ["kmle-b06-gluteus"], "hanjaSource": ["kmle-b06-gluteus"],
        "extraAliases": [
            {"field": "aliases[1]", "value": "Musculus glutaeus medius", "sourceId": FIPAT_ID, "state": "TA2_Other_cell_Latin_synonym"},
            {"field": "aliases[2]", "value": "mesogluteus", "sourceId": "kmle-b06-gluteus", "state": "KMLE_CancerWEB_explicit_Latin_synonym"},
        ], "unadopted": [],
    },
    "HA-M-000041": {
        "label": "소둔근", "korean": "작은볼기근", "hanja": "小臀筋",
        "labelSource": ["kmle-b06-gluteus"], "koreanSource": ["kmle-b06-gluteus"], "hanjaSource": ["kmle-b06-gluteus"],
        "extraAliases": [
            {"field": "aliases[1]", "value": "Musculus glutaeus minimus", "sourceId": FIPAT_ID, "state": "TA2_Other_cell_Latin_synonym"},
        ], "unadopted": [],
    },
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


def field_record(identifier: str, field: str, value, state: str, source_ids: list[str], *, source_value=None, missing_reason=None, locators=None):
    return {
        "entryId": identifier,
        "field": field,
        "value": value,
        "state": state,
        "evidence": [evidence(sid, (locators or {}).get(sid)) for sid in source_ids],
        "sourceValue": source_value,
        "missingReason": missing_reason,
        "humanAnatomyReviewStatus": "not_performed",
        "humanReviewed": False,
    }


def main():
    names = read_json(NAMES_PATH)
    batches = read_json(BATCH_PATH)
    coverage = [row for row in batches["canonicalCoverage"] if row["batchId"] == "T11-B06"]
    if [row["id"] for row in coverage] != IDS:
        raise SystemExit("T11-B06 assignment changed; refusing to touch any other IDs")
    if any(row["status"] != "not_started" for row in coverage):
        raise SystemExit("T11-B06 coverage already has a status; refusing a non-idempotent rebuild")
    if any(row["id"] in IDS for row in batches["entries"]):
        raise SystemExit("A T11-B06 evidence entry already exists; refusing duplicates")
    if any(entry["id"] in IDS for entry in names["entries"]):
        raise SystemExit("A T11-B06 learner overlay already exists; refusing to overwrite")

    canonical = {row["id"]: row for row in read_json(ROOT / "atlas-data/catalog/canonical-catalog.json")["entities"]["muscleConcepts"]}
    crosswalk = read_json(ROOT / "atlas-data/catalog/source-crosswalk.json")
    crosswalk_terms = {
        identifier: {
            term["sourceLanguage"]: term
            for term in crosswalk["termRecords"]
            if term["conceptId"] == identifier and term["sourceTextObserved"]
        }
        for identifier in IDS
    }
    assigned_by_id = {row["id"]: row for row in coverage}
    new_entries = []
    flat_field_evidence = []
    overlays = []

    for identifier in IDS:
        concept = canonical[identifier]
        row = assigned_by_id[identifier]
        locator = row["sourceCrosswalkLocator"]
        row_no, printed_page, pdf_page = ROWS[identifier]
        if (locator["tableRow"], locator["printedPage"]) != (row_no, printed_page):
            raise SystemExit(f"TA2 locator changed for {identifier}")
        observed = crosswalk_terms[identifier]
        if observed.get("en", {}).get("sourceTextObserved") != locator["englishTextObservation"]:
            raise SystemExit(f"English source crosswalk observation mismatch for {identifier}")
        if observed.get("la", {}).get("sourceTextObserved") != locator["latinTextObservation"]:
            raise SystemExit(f"Latin source crosswalk observation mismatch for {identifier}")

        terms = TERMS[identifier]
        english = locator["englishTextObservation"]
        latin = locator["latinTextObservation"]
        item_fields = [
            field_record(identifier, "label", terms["label"], "attested_customary_hanja_name", terms["labelSource"]),
            field_record(identifier, "korean", terms["korean"], "attested_current_korean_name", terms["koreanSource"]),
        ]
        if terms["hanja"] is None:
            item_fields.append(field_record(
                identifier, "hanja", None, "held_secondary_candidate_primary_source_unverified",
                terms["hanjaSource"], missing_reason=terms["hanjaMissingReason"],
            ))
        else:
            hanja_state = "attested_source_hanja_with_competing_variant_held" if identifier in {"HA-M-000032", "HA-M-000033"} else "attested_source_hanja"
            item_fields.append(field_record(identifier, "hanja", terms["hanja"], hanja_state, terms["hanjaSource"]))

        english_column = "UK English and US English"
        latin_column = "Latin term"
        english_locator = (
            f"TA2 Chapter 4, PDF text page {pdf_page}, printed p. {printed_page}, table row {row_no}; "
            f"exact English observation '{english}' in the UK English and US English columns. "
            "Chapter 4 header was read from the opened PDF text layer; visual table page not inspected."
        )
        latin_locator = (
            f"TA2 Chapter 4, PDF text page {pdf_page}, printed p. {printed_page}, table row {row_no}; "
            f"exact Latin observation '{latin}' in the Latin term column. "
            "Chapter 4 header was read from the opened PDF text layer; visual table page not inspected."
        )
        item_fields.append(field_record(identifier, "english", english, "TA2_opened_original_PDF_text_observation", [FIPAT_ID], source_value=english, locators={FIPAT_ID: english_locator}))
        item_fields.append(field_record(identifier, "aliases[0]", latin, "TA2_opened_original_PDF_text_observation", [FIPAT_ID], source_value=latin, locators={FIPAT_ID: latin_locator}))

        for extra in terms["extraAliases"]:
            source = SOURCES[extra["sourceId"]]
            if extra["sourceId"] == FIPAT_ID:
                field_locator = (
                    f"TA2 Chapter 4, PDF text page {pdf_page}, printed p. {printed_page}, table row {row_no}; "
                    f"exact Other-column observation '{extra['value']}'. The column name is read from the opened PDF text header; visual table page not inspected."
                )
            elif extra["sourceId"] == "kmle-b06-coracobrachialis":
                field_locator = f"Opened KMLE HTML at {source['url']}; CancerWEB result lines 84–88 explicitly labels '{extra['value']}' as a coracobrachialis synonym."
            elif extra["sourceId"] == "kmle-b06-brachialis":
                field_locator = f"Opened KMLE HTML at {source['url']}; CancerWEB result lines 151–153 explicitly lists '{extra['value']}' as a synonym of brachialis."
            elif extra["sourceId"] == "kmle-b06-triceps-brachii":
                field_locator = f"KMLE search-result excerpt at {source['url']}; CancerWEB triceps brachii result explicitly lists '{extra['value']}' as a synonym; direct HTML did not open."
            elif extra["sourceId"] == "kmle-b06-subscapularis":
                field_locator = f"KMLE search-result excerpt at {source['url']}; CancerWEB subscapularis result explicitly lists '{extra['value']}' as a synonym; direct HTML returned a Unicode decoding error."
            elif extra["sourceId"] == "kmle-b06-gluteus":
                field_locator = f"Opened KMLE HTML at {source['url']}; CancerWEB gluteus medius entry lines 261–262 explicitly lists '{extra['value']}' as a synonym."
            else:
                raise SystemExit(f"No exact alias locator handler for {extra['sourceId']}")
            item_fields.append(field_record(
                identifier, extra["field"], extra["value"], extra["state"], [extra["sourceId"]],
                source_value=extra["value"], locators={extra["sourceId"]: field_locator},
            ))

        flat_field_evidence.extend(item_fields)
        aliases = [latin, *[extra["value"] for extra in terms["extraAliases"]]]
        positive_source_ids = {FIPAT_ID, *terms["labelSource"], *terms["koreanSource"]}
        if terms["hanja"] is not None:
            positive_source_ids.update(terms["hanjaSource"])
        positive_source_ids.update(extra["sourceId"] for extra in terms["extraAliases"])
        overlay = {
            "id": identifier,
            "label": terms["label"],
            "korean": terms["korean"],
            "english": english,
            "hanja": terms["hanja"],
            "aliases": aliases,
            "sourceIds": sorted(positive_source_ids),
            "parentId": concept.get("parentId"),
            "entityType": concept["entityType"],
            "lookupOnly": False,
            "status": "web_attested_with_gaps",
            "humanReviewed": False,
        }
        if terms["hanja"] is None:
            overlay["hanjaNote"] = terms["hanjaMissingReason"]
        elif identifier == "HA-M-000032":
            overlay["hanjaNote"] = "KMLE exact legacy infraspinatus row shows 棘下筋. A separate KMLE result shows 極下筋; the latter is retained as an unadopted conflict, not a search alias. Human review not performed."
        elif identifier == "HA-M-000033":
            overlay["hanjaNote"] = "KMLE exact neurosurgery teres minor row shows 小圓筋. Separate legacy results show 小園筋 and 小圓形筋; they remain unadopted. Human review not performed."
        else:
            overlay["hanjaNote"] = "KMLE source row shows this Hanja; exact underlying Korean dictionary edition/revision is not exposed. Human review not performed."
        overlays.append(overlay)

        unadopted = []
        for candidate in terms["unadopted"]:
            unadopted.append({
                "field": candidate["field"],
                "value": candidate["value"],
                "state": candidate["state"],
                "evidence": [evidence(source_id) for source_id in candidate["sourceIds"]],
                "reason": candidate["reason"],
            })

        if terms["hanja"] is None:
            display_value = terms["label"]
        else:
            display_value = terms["label"]
        new_entries.append({
            "id": identifier,
            "isCanonical": True,
            "entityType": concept["entityType"],
            "parentId": concept.get("parentId"),
            "lookupOnly": False,
            "canonicalStatus": "canonical_existing_id",
            "canonicalSourceRow": {"sourceId": "FIPAT_TA2", "tableRow": row_no, "printedPage": printed_page},
            "displayField": "label",
            "displayValue": display_value,
            "fieldEvidence": item_fields,
            "unadoptedCandidates": unadopted,
            "webVerificationStatus": "web_checked_with_gaps",
            "humanAnatomyReviewStatus": "not_performed",
            "humanReviewer": None,
            "humanReviewed": False,
            "fieldEvidenceCount": len(item_fields),
        })

        row["status"] = "web_checked_with_gaps"
        row["statusReason"] = (
            "The assigned existing TA2 rows were checked against the directly opened official Dalhousie-hosted PDF text. "
            "KMLE Korean/Hanja fields use opened aggregate HTML or indexed excerpts; underlying terminology-book editions are mostly unexposed. "
            "Hanja conflicts and the coracobrachialis Hanja gap are explicit; PDF visual table inspection and human anatomy review were not performed."
        )
        locator["existingEvidenceMode"] = "T04 official search-index observation retained; T11-B06 opened the official Dalhousie-hosted TA2 PDF text and confirmed assigned rows/Chapter 4 header; no visual page screenshot."
        locator["cellRoleStatus"] = "column_role_confirmed_from_opened_PDF_text_header; visual_table_layout_not_inspected"

    for source_id, source in SOURCES.items():
        names["sources"][source_id] = source
        batches["sources"][source_id] = source
    names["entries"].extend(overlays)
    batches["entries"].extend(new_entries)
    batches["fieldEvidence"].extend(flat_field_evidence)
    names["revision"] = "T11-B06-web-checked-2026-09-25"
    names["accessedAt"] = CHECKED
    batches["revision"] = "T11-B06-web-checked-2026-09-25"
    batches["checkedDate"] = CHECKED
    batches["overallT11Status"] = "in_progress_partial"
    for batch in batches["batchOrder"]:
        if batch["batchId"] == "T11-B06":
            batch["status"] = "complete_with_gaps"
    batches["notes"].append(
        "T11-B06 completed with gaps: 10 assigned existing IDs, 50 required core field evidence records plus 10 evidence records for directly attested additional aliases. TA2 Second Edition (2.07) Part II was directly opened from the official Dalhousie host and text rows/table headings were read; no visual page inspection. KMLE underlying Korean dictionary editions are unexposed. Infraspinatus/teres minor Hanja variants remain explicit unadopted candidates, and coracobrachialis Hanja remains null because a secondary candidate lacks a verified primary locator. Human anatomy review was not performed."
    )
    write_json(NAMES_PATH, names)
    write_json(BATCH_PATH, batches)
    print(json.dumps({
        "batchId": "T11-B06",
        "canonicalIds": IDS,
        "requiredCoreFieldEvidence": 50,
        "additionalAliasEvidence": len(flat_field_evidence) - 50,
        "batchFieldEvidence": len(flat_field_evidence),
        "cumulativeFieldEvidence": len(batches["fieldEvidence"]),
        "learnerOverlaysTotal": len(names["entries"]),
        "newOverlays": len(overlays),
        "hanjaAttested": sum(1 for item in TERMS.values() if item["hanja"] is not None),
        "hanjaMissing": [identifier for identifier, item in TERMS.items() if item["hanja"] is None],
        "batchStatus": "complete_with_gaps",
        "humanReviewed": False,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
