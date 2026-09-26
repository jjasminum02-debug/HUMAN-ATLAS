#!/usr/bin/env python3
"""Build the bounded T11-B01 terminology overlay and field-level evidence ledger."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OVERLAY = ROOT / "atlas-data/terminology/learning-names.json"
CROSSWALK = ROOT / "atlas-data/catalog/source-crosswalk.json"
CATALOG = ROOT / "atlas-data/catalog/canonical-catalog.json"
STATUS = ROOT / "atlas-data/catalog/catalog-status.json"
OUT = ROOT / "atlas-data/terminology/term-review-batches.json"
CHECKED = "2026-09-25"
PDF = "https://fipat.library.dal.ca/wp-content/uploads/2020/09/FIPAT-TA2-Part-2.pdf"

names = json.loads(OVERLAY.read_text())
crosswalk = json.loads(CROSSWALK.read_text())
catalog = json.loads(CATALOG.read_text())
catalog_status = json.loads(STATUS.read_text())

added_sources = {
    "kmle-splenius": {
        "title": "KMLE: Splenius capitis/cervicis entries",
        "url": "https://m.kmle.co.kr/search.php?Search=splenius+capitis+m",
        "locator": "KMLE page sections for KAA current entries, old KMA dictionary and Korean Neurosurgery terminology: capitis/cervicis rows; generic Musculus splenius row.",
        "edition": "KMLE web aggregation; underlying dictionary editions and publication years are not exposed on the entry.",
        "accessDate": CHECKED,
        "verificationMode": "opened_html_page_text",
        "scope": "terminology only; no anatomical claims imported",
    },
    "fipat-ta2-index": {
        "title": "FIPAT Terminologia Anatomica, second edition, Part 2",
        "url": PDF,
        "locator": "Official indexed table rows 2272-2274 (printed page 82): Musculi splenii; Musculus splenius capitis; Musculus splenius colli / alternative Latin Musculus splenius cervicis; English Splenius colli/cervicis forms.",
        "edition": "Terminologia Anatomica, second edition (TA2), Part 2; online edition published 2019; hosted PDF path dated 2020-09.",
        "accessDate": CHECKED,
        "verificationMode": "official_pdf_search_index_only; original PDF visual inspection unavailable",
        "scope": "nomenclature crosswalk only; exact column role remains unverified",
    },
    "ncbi-statpearls-deltoid": {
        "title": "NCBI Bookshelf StatPearls: Anatomy, Shoulder and Upper Limb, Deltoid Muscle",
        "url": "https://www.ncbi.nlm.nih.gov/books/NBK537056/",
        "locator": "Anatomical division list: anterior (clavicular), lateral (acromial), posterior (spinal); result excerpt only.",
        "edition": "StatPearls [Internet]. Treasure Island (FL): StatPearls Publishing; 2024 Jan-. Page last update: January 30, 2024.",
        "accessDate": CHECKED,
        "verificationMode": "search_result_excerpt_for_parts_and_edition_metadata; direct page is access-gated",
        "scope": "terminology corroboration only; no clinical interpretation imported",
    },
}
for source_id, source in added_sources.items():
    names["sources"][source_id] = source

def by_id(identifier):
    return next(entry for entry in names["entries"] if entry["id"] == identifier)

capitis = by_id("LOOKUP-SPLENIUS-CAPITIS")
capitis["hanja"] = "頭板狀筋"
capitis["hanjaNote"] = None
for alias in ["Splenius capitis muscle", "musculus splenius capitis"]:
    if alias not in capitis["aliases"]:
        capitis["aliases"].append(alias)
for source_id in ["kmle-splenius", "fipat-ta2-index"]:
    if source_id not in capitis["sourceIds"]:
        capitis["sourceIds"].append(source_id)

cervicis = by_id("LOOKUP-SPLENIUS-CERVICIS")
cervicis["hanja"] = "頸板狀筋"
cervicis["hanjaNote"] = None
for alias in ["Splenius cervicis muscle", "Splenius colli muscle",
              "musculus splenius cervicis", "musculus splenius colli"]:
    if alias not in cervicis["aliases"]:
        cervicis["aliases"].append(alias)
for source_id in ["kmle-splenius", "fipat-ta2-index"]:
    if source_id not in cervicis["sourceIds"]:
        cervicis["sourceIds"].append(source_id)

deltoid_part = by_id("HA-P-000015")
deltoid_part["aliases"] = [alias for alias in deltoid_part["aliases"] if alias != "middle deltoid"]
if "ncbi-statpearls-deltoid" not in deltoid_part["sourceIds"]:
    deltoid_part["sourceIds"].append("ncbi-statpearls-deltoid")
for identifier in [
    "HA-M-000001", "HA-M-000002", "HA-M-000003", "HA-M-000004",
    "HA-M-000005", "HA-M-000006", "HA-M-000019", "HA-P-000015",
]:
    entry = by_id(identifier)
    if "fipat-ta2-index" not in entry["sourceIds"]:
        entry["sourceIds"].append("fipat-ta2-index")
names["revision"] = "T11-B01-web-attested-terms-v2"
OVERLAY.write_text(json.dumps(names, ensure_ascii=False, indent=2) + "\n")

crosswalk_items = crosswalk["catalogItems"]
all_canonical = [row["stableConceptId"] for row in crosswalk_items]
b01_canonical = [
    "HA-M-000001", "HA-M-000002", "HA-M-000003", "HA-M-000004",
    "HA-M-000005", "HA-M-000006", "HA-M-000019", "HA-P-000015",
]
lookup_ids = ["LOOKUP-SPLENIUS-CAPITIS", "LOOKUP-SPLENIUS-CERVICIS"]
remaining = [identifier for identifier in all_canonical if identifier not in b01_canonical]
chunks = [remaining[i:i + 10] for i in range(0, len(remaining), 10)]
batches = [{
    "batchId": "T11-B01",
    "canonicalIds": b01_canonical,
    "lookupEntryIds": lookup_ids,
    "size": len(b01_canonical) + len(lookup_ids),
    "status": "complete_with_gaps",
}]
for number, chunk in enumerate(chunks, start=2):
    batches.append({
        "batchId": f"T11-B{number:02d}",
        "canonicalIds": chunk,
        "lookupEntryIds": [],
        "size": len(chunk),
        "status": "not_started",
    })

canonical_entities = {
    item["id"]: item["entityType"]
    for entity_name in ("muscleConcepts", "muscleParts")
    for item in catalog["entities"][entity_name]
}
canonical_coverage = []
for row in crosswalk_items:
    identifier = row["stableConceptId"]
    in_b01 = identifier in b01_canonical
    canonical_coverage.append({
        "id": identifier,
        "entityType": row["entityType"],
        "batchId": "T11-B01" if in_b01 else next(
            batch["batchId"] for batch in batches if identifier in batch["canonicalIds"]
        ),
        "status": "web_checked_with_gaps" if in_b01 else "not_started",
        "sourceCrosswalkLocator": {
            "sourceId": "FIPAT_TA2",
            "edition": row["edition"],
            "part": row["part"],
            "printedPage": row["printedPage"],
            "tableRow": row["tableRow"],
            "latinTextObservation": row["latinTextObservation"],
            "englishTextObservation": row["englishTextObservation"],
            "cellRoleStatus": row["termCellRoleStatus"],
            "existingEvidenceMode": "T04 official search-index excerpt; no original-PDF visual review",
        },
        "statusReason": (
            "B01 terminology fields checked from the named web sources; unresolved items remain explicit."
            if in_b01 else
            "Assigned for a later serial batch; not reviewed by T11-B01. This is not evidence of absence."
        ),
    })

sources = {
    "fipat-ta2-index": added_sources["fipat-ta2-index"],
    "kmle-gastro": {
        "title": "KMLE: gastrocnemius muscle",
        "url": "https://m.kmle.co.kr/search.php?Page=1&Search=gastrocnemius",
        "edition": "KMLE web aggregation; underlying dictionary editions and years are not exposed.",
        "accessDate": CHECKED,
        "verificationMode": "opened_html_page_text_and_indexed_dictionary_sections",
    },
    "kmle-soleus": {
        "title": "KMLE: soleus muscle",
        "url": "https://m.kmle.co.kr/search.php?Search=soleus+m",
        "edition": "KMLE web aggregation; underlying dictionary editions and years are not exposed.",
        "accessDate": CHECKED,
        "verificationMode": "opened_html_page_text",
    },
    "kmle-tibialis": {
        "title": "KMLE: tibialis anterior and posterior entries",
        "url": "https://m.kmle.co.kr/search.php?Search=tibialis+anterior",
        "edition": "KMLE web aggregation; underlying dictionary editions and years are not exposed.",
        "accessDate": CHECKED,
        "verificationMode": "opened_html_page_text; posterior Hanja in legacy dictionary section",
    },
    "nikom-ta": {
        "title": "족관절 염좌 한의표준임상진료지침",
        "url": "https://nikom.or.kr/nckm/module/practiceGuide/download.do?file_type=pdf&guide_idx=208",
        "edition": "Exact issue/revision date not exposed in this check.",
        "accessDate": CHECKED,
        "verificationMode": "opened_pdf_text; one lexical occurrence only",
    },
    "kmle-peroneus": {
        "title": "KMLE: peroneus/fibularis longus and brevis entries",
        "url": "https://m.kmle.co.kr/search.php?Search=musculus+peroneus+longus",
        "edition": "KMLE web aggregation; underlying dictionary editions and years are not exposed.",
        "accessDate": CHECKED,
        "verificationMode": "opened_html_page_text",
    },
    "nikl-trapezius": {
        "title": "국립국어원 온용어: 승모근",
        "url": "https://kli.korean.go.kr/term/trgtWord/indexTrgtWord.do?trgtWordNo=2296115",
        "edition": "OnTerm classifies the entry from 우리말샘 as of June 2023; OnTerm page revision date is not exposed.",
        "accessDate": CHECKED,
        "verificationMode": "opened_html_page_text",
    },
    "kmle-deltoid": {
        "title": "KMLE: deltoid muscle",
        "url": "https://m.kmle.co.kr/search.php?Search=deltoid",
        "edition": "KMLE web aggregation; underlying dictionary editions and years are not exposed.",
        "accessDate": CHECKED,
        "verificationMode": "opened_html_page_text",
    },
    "user-search": {
        "title": "사용자 검색어 기록",
        "url": None,
        "edition": "Not applicable; user query, not a published source.",
        "accessDate": CHECKED,
        "verificationMode": "user_query_only; not an independent anatomy term source",
    },
    "kmle-splenius": added_sources["kmle-splenius"],
    "ncbi-statpearls-deltoid": added_sources["ncbi-statpearls-deltoid"],
}

evidence_rows = []
def field(identifier, field_name, value, state, refs=None, reason=None, source_value=None):
    refs = refs or []
    evidence_rows.append({
        "entryId": identifier,
        "field": field_name,
        "value": value,
        "state": state,
        "evidence": [
            {
                "sourceId": source_id,
                "locator": locator,
                "verificationMode": mode,
                "sourceEdition": sources[source_id]["edition"],
                "checkedDate": CHECKED,
            }
            for source_id, locator, mode in refs
        ],
        "sourceValue": source_value,
        "missingReason": reason,
        "humanAnatomyReviewStatus": "not_performed",
        "humanReviewed": False,
    })

ta2_locator = {
    row["stableConceptId"]: (
        f"TA2 Part 2 printed page {row['printedPage']}, table row {row['tableRow']}; "
        f"Latin observation {row['latinTextObservation']}; English observation {row['englishTextObservation']}"
    )
    for row in crosswalk_items
}
fipat_ref = lambda identifier: ("fipat-ta2-index", ta2_locator[identifier], "T04_official_PDF_search_index_record")
kmle_ref = lambda source_id, locator, mode="opened_page_text": (source_id, locator, mode)

field_specs = {
    "HA-M-000001": {
        "label": ("attested_legacy_customary_name", [kmle_ref("kmle-gastro", "gastrocnemius muscle item: 장딴지근, 비복근; legacy KMA2/3 entries", "opened_page_text")], None),
        "korean": ("attested_current_and_legacy_forms", [kmle_ref("kmle-gastro", "KMLE current dictionary and KAA sections: gastrocnemius muscle; 장딴지근, 비복근", "opened_page_text")], None),
        "english": ("TA2_source_observation_cell_role_unverified", [fipat_ref("HA-M-000001")], None),
        "hanja": ("missing_conflicting_glyphs", [kmle_ref("kmle-gastro", "Neurosurgery dictionary: 비腹筋; legacy variants include 排/비 mixed glyphs", "opened_page_text")], "The checked page contains corrupted or conflicting mixed-script forms; no complete, trustworthy Hanja form is selected."),
    },
    "HA-M-000002": {
        "label": ("attested_current_name", [kmle_ref("kmle-soleus", "KAA current dictionary item Soleus m.: 가자미근", "opened_page_text")], None),
        "korean": ("attested_same_hangul_form", [kmle_ref("kmle-soleus", "KAA current dictionary item Soleus m.: 가자미근", "opened_page_text")], None),
        "english": ("TA2_source_observation_cell_role_unverified", [fipat_ref("HA-M-000002")], None),
        "hanja": ("missing_no_source", [kmle_ref("kmle-soleus", "Current and legacy KMLE entries show 가자미근; no paired Hanja entry located", "opened_page_text")], "No paired Hanja form with a reliable item locator was found; none is inferred from etymology."),
    },
    "HA-M-000003": {
        "label": ("attested_legacy_customary_name", [kmle_ref("kmle-tibialis", "legacy KMA3 entry musculus tibialis anterior: 전경골근; old glyph variant 前頸骨筋 is not adopted", "opened_page_text")], None),
        "korean": ("attested_current_name", [kmle_ref("kmle-tibialis", "KAA current dictionary item Tibialis anterior m.: 앞정강근; old term 전경골근", "opened_page_text")], None),
        "english": ("TA2_source_observation_cell_role_unverified", [fipat_ref("HA-M-000003")], None),
        "hanja": ("attested_lexical_occurrence_only", [kmle_ref("nikom-ta", "PDF viewer page 165, printed page 159, VII appendix, 해계(ST41): 前脛骨筋; lexical occurrence only, no treatment content used", "opened_pdf_text")], None),
    },
    "HA-M-000004": {
        "label": ("attested_legacy_customary_name", [kmle_ref("kmle-tibialis", "KAA current entry Tibialis posterior m.: 뒤정강근; old term 후경골근", "opened_page_text")], None),
        "korean": ("attested_current_name", [kmle_ref("kmle-tibialis", "KAA current entry Tibialis posterior m.: 뒤정강근; old term 후경골근", "opened_page_text")], None),
        "english": ("TA2_source_observation_cell_role_unverified", [fipat_ref("HA-M-000004")], None),
        "hanja": ("attested_legacy_dictionary_form", [kmle_ref("kmle-tibialis", "legacy dictionary item posterior tibial muscle / musculus tibialis posterior: 後脛骨筋", "opened_page_text")], None),
    },
    "HA-M-000005": {
        "label": ("attested_legacy_customary_name", [kmle_ref("kmle-peroneus", "KAA current entry Peroneus longus m.: 긴종아리근; old term 장비골근", "opened_page_text")], None),
        "korean": ("attested_current_name", [kmle_ref("kmle-peroneus", "KAA current entry Peroneus longus m.: 긴종아리근; old term 장비골근", "opened_page_text")], None),
        "english": ("TA2_source_observation_cell_role_unverified", [fipat_ref("HA-M-000005")], None),
        "hanja": ("missing_conflicting_glyphs", [kmle_ref("kmle-peroneus", "Legacy rows show 長鼻骨筋, 長排骨筋, 長批骨筋 variants", "opened_page_text")], "Legacy Hanja spellings conflict and include likely encoding/transcription variants; no form is promoted."),
        "aliases": {
            "Peroneus longus": ("attested_synonym", [kmle_ref("kmle-peroneus", "KMLE current/legacy items identify Peroneus longus with Fibularis longus", "opened_page_text")], None),
        },
    },
    "HA-M-000006": {
        "label": ("attested_legacy_customary_name", [kmle_ref("kmle-peroneus", "KAA current entry Peroneus brevis m.: 짧은종아리근; old term 단비골근", "opened_page_text")], None),
        "korean": ("attested_current_name", [kmle_ref("kmle-peroneus", "KAA current entry Peroneus brevis m.: 짧은종아리근; old term 단비골근", "opened_page_text")], None),
        "english": ("TA2_source_observation_cell_role_unverified", [fipat_ref("HA-M-000006")], None),
        "hanja": ("missing_conflicting_glyphs", [kmle_ref("kmle-peroneus", "Legacy brevis form 短鼻骨筋 and inconsistent fibular/peroneal Hanja forms", "opened_page_text")], "The checked legacy forms conflict; no Hanja form is selected."),
        "aliases": {
            "Peroneus brevis": ("attested_synonym", [kmle_ref("kmle-peroneus", "KMLE current and legacy items list Peroneus brevis m.", "opened_page_text")], None),
        },
    },
    "HA-M-000019": {
        "label": ("attested_customary_name", [kmle_ref("nikl-trapezius", "entry 승모근; 원어 僧帽筋", "opened_page_text")], None),
        "korean": ("attested_korean_synonym", [kmle_ref("nikl-trapezius", "관련 용어명: 동의어 등세모근", "opened_page_text")], None),
        "english": ("TA2_source_observation_cell_role_unverified", [fipat_ref("HA-M-000019")], None),
        "hanja": ("attested_exact_hanja", [kmle_ref("nikl-trapezius", "entry 승모근, 원어 僧帽筋; 우리말샘 snapshot 2023-06", "opened_page_text")], None),
    },
    "HA-P-000015": {
        "label": ("existing_composite_display_needs_part_term_review", [
            kmle_ref("kmle-deltoid", "KAA current and legacy deltoid muscle name: 어깨세모근 / 삼각근", "opened_page_text"),
            fipat_ref("HA-P-000015"),
        ], "The whole-muscle Korean form and TA2 part locator are attested, but the combined Korean label for the part is a project composite, not a sourced Korean part term."),
        "korean": ("part_component_unverified_localization", [
            kmle_ref("kmle-deltoid", "KAA current deltoid m.: 어깨세모근", "opened_page_text"),
            fipat_ref("HA-P-000015"),
        ], "견봉부분 is a Korean rendering of the English/Latin part name; no Korean part-name source was located."),
        "english": ("TA2_source_observation_cell_role_unverified", [fipat_ref("HA-P-000015")], None),
        "hanja": ("missing_no_part_specific_source", [kmle_ref("kmle-deltoid", "Whole deltoid Hanja 三角筋 is not a part-specific Hanja record", "opened_page_text")], "No source with a Hanja term for the acromial part was found; do not derive one from the whole-muscle Hanja."),
        "aliases": {
            "측면삼각근": ("user_search_intent_only", [kmle_ref("user-search", "User search-intent alias recorded in T10 overlay; not an independent anatomical source", "user_query_only")], "Preserved as search intent; equivalence to acromial part awaits human anatomy review."),
            "측면삼각극": ("user_search_typo_only", [kmle_ref("user-search", "User search typo recorded in T10 overlay; not an independent anatomical source", "user_query_only")], "Preserved as search intent; not presented as an anatomical term."),
            "lateral deltoid": ("search_index_part_synonym", [kmle_ref("ncbi-statpearls-deltoid", "Anatomy division list: lateral (acromial); search-result excerpt only", "search_result_excerpt_only")], None),
        },
    },
    "LOOKUP-SPLENIUS-CAPITIS": {
        "label": ("attested_legacy_customary_name", [kmle_ref("kmle-splenius", "old KMA3 entry musculus splenius capitis: 머리널판근, 두판상근(頭板狀筋)", "opened_page_text")], None),
        "korean": ("attested_current_name", [kmle_ref("kmle-splenius", "KAA current dictionary item Splenius capitis m.: 머리널판근; old term 두판상근", "opened_page_text")], None),
        "english": ("TA2_indexed_synonym_with_exact_row", [kmle_ref("fipat-ta2-index", "Part 2 printed page 82, row 2273: Musculus splenius capitis / Splenius capitis muscle", "official_pdf_search_index_only")], None),
        "hanja": ("attested_legacy_dictionary_form", [kmle_ref("kmle-splenius", "Korean Neurosurgery terminology entry: 頭板狀筋", "opened_page_text")], None),
        "aliases": {
            "판상근": ("ambiguous_group_search_alias", [kmle_ref("kmle-splenius", "old KMA3 generic Musculus splenius row: 판상근", "opened_page_text")], "Generic group term; intentionally resolves to both splenius candidates."),
            "널판근": ("ambiguous_group_search_alias", [kmle_ref("kmle-splenius", "KMLE generic Musculus splenius row and current Hangul term root", "opened_page_text")], "Generic group term; intentionally resolves to both splenius candidates."),
            "splenius": ("ambiguous_group_search_alias", [kmle_ref("fipat-ta2-index", "Part 2 printed page 82, row 2272: Musculi splenii / Splenius muscles", "official_pdf_search_index_only")], "Generic group term; intentionally resolves to both splenius candidates."),
            "Splenius capitis muscle": ("attested_english_synonym", [kmle_ref("fipat-ta2-index", "Part 2 printed page 82, row 2273, English observation", "official_pdf_search_index_only")], None),
            "musculus splenius capitis": ("attested_latin_term", [kmle_ref("fipat-ta2-index", "Part 2 printed page 82, row 2273, Latin observation", "official_pdf_search_index_only")], None),
        },
    },
    "LOOKUP-SPLENIUS-CERVICIS": {
        "label": ("attested_legacy_customary_name", [kmle_ref("kmle-splenius", "old KMA3 entry musculus splenius cervicis: 목널판근, 경판상근(頸板狀筋)", "opened_page_text")], None),
        "korean": ("attested_current_name", [kmle_ref("kmle-splenius", "KAA current dictionary item Splenius cervicis m.: 목널판근; old term 경판상근", "opened_page_text")], None),
        "english": ("TA2_indexed_english_synonym", [kmle_ref("fipat-ta2-index", "Part 2 printed page 82, row 2274: English observation Splenius colli muscle; English synonym Splenius cervicis muscle", "official_pdf_search_index_only")], None),
        "hanja": ("attested_legacy_dictionary_form", [kmle_ref("kmle-splenius", "old KMA3 entry musculus splenius cervicis: 頸板狀筋", "opened_page_text")], None),
        "aliases": {
            "판상근": ("ambiguous_group_search_alias", [kmle_ref("kmle-splenius", "old KMA3 generic Musculus splenius row: 판상근", "opened_page_text")], "Generic group term; intentionally resolves to both splenius candidates."),
            "널판근": ("ambiguous_group_search_alias", [kmle_ref("kmle-splenius", "KMLE generic Musculus splenius row and current Hangul term root", "opened_page_text")], "Generic group term; intentionally resolves to both splenius candidates."),
            "splenius": ("ambiguous_group_search_alias", [kmle_ref("fipat-ta2-index", "Part 2 printed page 82, row 2272: Musculi splenii / Splenius muscles", "official_pdf_search_index_only")], "Generic group term; intentionally resolves to both splenius candidates."),
            "Splenius cervicis muscle": ("attested_english_synonym", [kmle_ref("fipat-ta2-index", "Part 2 printed page 82, row 2274, English synonym", "official_pdf_search_index_only")], None),
            "Splenius colli muscle": ("attested_english_term", [kmle_ref("fipat-ta2-index", "Part 2 printed page 82, row 2274, English observation", "official_pdf_search_index_only")], None),
            "musculus splenius cervicis": ("attested_latin_alternative", [kmle_ref("fipat-ta2-index", "Part 2 printed page 82, row 2274, Latin alternative", "official_pdf_search_index_only")], None),
            "musculus splenius colli": ("attested_latin_term", [kmle_ref("fipat-ta2-index", "Part 2 printed page 82, row 2274, Latin observation", "official_pdf_search_index_only")], None),
        },
    },
}

entries = []
for identifier in b01_canonical + lookup_ids:
    overlay_entry = by_id(identifier)
    canonical = identifier in canonical_entities
    if canonical:
        row = next(x for x in crosswalk_items if x["stableConceptId"] == identifier)
        entity_type = row["entityType"]
        canonical_status = "canonical_existing_id"
        source_row = {"sourceId": "FIPAT_TA2", "tableRow": row["tableRow"], "printedPage": row["printedPage"]}
    else:
        entity_type = "lookup_candidate"
        canonical_status = "no_matching_id_in_current_partial_catalog"
        source_row = None
    entry = {
        "id": identifier,
        "isCanonical": canonical,
        "entityType": entity_type,
        "parentId": overlay_entry.get("parentId"),
        "lookupOnly": overlay_entry.get("lookupOnly", False),
        "canonicalStatus": canonical_status,
        "canonicalSourceRow": source_row,
        "displayField": "label",
        "displayValue": overlay_entry["label"],
        "fieldEvidence": [],
        "webVerificationStatus": "checked_with_gaps",
        "humanAnatomyReviewStatus": "not_performed",
        "humanReviewer": None,
        "humanReviewed": False,
    }
    specs = field_specs[identifier]
    for field_name in ("label", "korean", "english", "hanja"):
        value = overlay_entry.get(field_name)
        state, refs, reason = specs[field_name]
        if field_name == "english" and identifier not in lookup_ids:
            source_value = next(x["englishTextObservation"] for x in crosswalk_items if x["stableConceptId"] == identifier)
        else:
            source_value = None
        field(identifier, field_name, value, state, refs, reason, source_value)
    aliases = specs.get("aliases", {})
    for index, alias_value in enumerate(overlay_entry.get("aliases", [])):
        if alias_value in aliases:
            state, refs, reason = aliases[alias_value]
        elif identifier.startswith("LOOKUP-SPLENIUS") and alias_value in {"판상근", "널판근", "splenius"}:
            state = "ambiguous_group_search_alias"
            refs = [kmle_ref("kmle-splenius", "Generic splenius muscle-group form", "opened_page_text")]
            reason = "Generic group term; intentionally resolves to both splenius candidates."
        else:
            state = "existing_alias_requires_field_audit"
            refs = []
            reason = "Retained from T10; B01 did not independently establish an external term source."
        field(identifier, f"aliases[{index}]", alias_value, state, refs, reason)
    entry["fieldEvidence"] = [row for row in evidence_rows if row["entryId"] == identifier]
    entry["fieldEvidenceCount"] = len(entry["fieldEvidence"])
    entries.append(entry)

result = {
    "schemaVersion": "1.0",
    "revision": "T11-B01-field-evidence-v1",
    "checkedDate": CHECKED,
    "overallT11Status": "in_progress_partial",
    "catalogScope": {
        "currentPartialCatalogItems": len(all_canonical),
        "counts": catalog_status["partialEntryCounts"],
        "denominatorFrozen": catalog_status["denominatorFrozen"],
        "wholeBodyGate": catalog_status["wholeBodyGate"],
        "statement": "85 is the current partial source-index catalog, not a whole-body muscle denominator.",
    },
    "batchOrder": batches,
    "canonicalCoverage": canonical_coverage,
    "sources": sources,
    "entries": entries,
    "fieldEvidence": evidence_rows,
    "notes": [
        "Web term verification and human anatomy review are independent states.",
        "No human anatomy reviewer participated; every B01 entry has humanReviewed=false.",
        "The two splenius lookup entries are not in the 85-item canonical catalog. Their exact TA2 search-index rows were found, but the partial catalog is not frozen; no canonical ID was minted or guessed.",
        "FIPAT row locators inherited from T04 are search-index observations. The original PDF binary/page rendering and table-column roles remain unverified.",
        "A source locator can support a spelling observation without supporting anatomical identity, attachment, function, or clinical meaning.",
    ],
}
OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({
    "overlay": str(OVERLAY.relative_to(ROOT)),
    "overlayEntries": len(names["entries"]),
    "canonicalCoverage": len(canonical_coverage),
    "batchCount": len(batches),
    "batchSizes": {batch["batchId"]: batch["size"] for batch in batches},
    "b01Entries": len(entries),
    "fieldEvidenceRows": len(evidence_rows),
    "output": str(OUT.relative_to(ROOT)),
}, ensure_ascii=False))
