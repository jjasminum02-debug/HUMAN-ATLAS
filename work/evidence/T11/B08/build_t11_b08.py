"""Build only the fixed T11-B08 term evidence and existing-ID overlays."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
CHECKED = "2026-09-25"
IDS = [f"HA-P-{number:06d}" for number in range(4, 14)]
FIPAT = "fipat-ta2-b08-opened-original-pdf"
KMLE_MASSETER = "kmle-b08-masseter-index"
KMLE_LATERAL = "kmle-b08-lateral-pterygoid-index"
KMLE_MEDIAL = "kmle-b08-medial-pterygoid-index"
KMLE_TRAPEZIUS = "kmle-b08-trapezius-opened-html"
YES24 = "yes24-b08-2018-textbook-toc-index"
FIPAT_URL = "https://cdn.dal.ca/content/dam/dalhousie/pdf/library/FIPAT/TA2/FIPAT-TA2-Part-2.pdf"
FIPAT_EDITION = (
    "FIPAT, Terminologia Anatomica, Second Edition (2.07), TA2 Part II; "
    "bibliographic citation 2019; approved and adopted by IFAA General Assembly in 2020."
)
KMLE_EDITION = "KMLE web aggregation; exact underlying Korean terminology dictionary edition/revision is not exposed."
NAMES_PATH = ROOT / "atlas-data/terminology/learning-names.json"
BATCH_PATH = ROOT / "atlas-data/terminology/term-review-batches.json"

SOURCES = {
    FIPAT: {
        "title": "FIPAT Terminologia Anatomica, Second Edition (2.07), TA2 Part II — official Dalhousie-hosted original PDF directly opened",
        "url": FIPAT_URL,
        "locator": (
            "PDF text front matter P0 lines 0–15 identifies Second Edition (2.07), 2019 bibliographic citation, "
            "2020 IFAA approval/adoption; Chapter 4 header PDF text P52 / printed p.73 lines 3494–3495 names "
            "Latin term, Latin synonym, UK English, US English, English synonym, Other. Assigned rows: "
            "PDF text P56 / printed p.77 rows 2107, 2110, 2111, 2114, 2115; P60 / printed p.81 rows "
            "2227–2229; P62 / printed p.83 rows 2302–2303. Text layer directly opened and read; no rendered-page inspection."
        ),
        "edition": FIPAT_EDITION,
        "accessDate": CHECKED,
        "verificationMode": "official_Dalhousie_hosted_original_PDF_directly_opened; front_matter_Ch4_header_and_exact_rows_read_from_text_layer; no_visual_page_screenshot",
        "scope": "TA2 source term, UK/US English, synonym cell and table row locator only; not Korean translation or human anatomy review.",
    },
    KMLE_MASSETER: {
        "title": "KMLE search-index result for deep part of masseter muscle",
        "url": "https://m.kmle.co.kr/search.php?Search=deep+part+of+masseter+muscle",
        "locator": (
            "Search-index excerpt headed 'deep part of masseter muscle'; a Korean masseter description contains "
            "the exact phrase '심부 교근은' while describing the deep portion. It is body-text usage, not a dedicated "
            "Korean headword row. No part-specific Hanja is shown. The KMLE page did not open as HTML in this check."
        ),
        "edition": KMLE_EDITION,
        "accessDate": CHECKED,
        "verificationMode": "KMLE_search_index_excerpt_only; direct_HTML_open_failed_with_Unicode_decoding_error; no_underlying_dictionary_edition_exposed",
        "scope": "One Korean phrase occurrence only; no parent-muscle Hanja inherited; no anatomical review.",
    },
    KMLE_LATERAL: {
        "title": "KMLE pterygoid search-index excerpt with dental dictionary head terms",
        "url": "https://m.kmle.co.kr/search.php?Search=pterygoid+muscle%2C+lateral",
        "locator": (
            "Search-index excerpt under '경북대 치과대학 구강내과 교실 사전': 'superior lateral pterygoid muscle' → "
            "외익돌근 상두 and 'inferior lateral pterygoid' → 외익돌근 하두. KMLE underlying dictionary edition/revision "
            "is not exposed. Search-index result only; the page was not opened as HTML. No head-specific Hanja is displayed."
        ),
        "edition": KMLE_EDITION,
        "accessDate": CHECKED,
        "verificationMode": "KMLE_search_index_excerpt_only; underlying_dental_dictionary_edition_unexposed; direct_HTML_not_opened",
        "scope": "Lateral pterygoid head term strings only; source's older English head phrasing is linked to the existing TA2 head IDs, without structure claims.",
    },
    KMLE_MEDIAL: {
        "title": "KMLE medial pterygoid search and part-specific Korean/Hanja gap check",
        "url": "https://m.kmle.co.kr/search.php?Search=medial+pterygoid+m",
        "locator": (
            "Accessible index output shows the parent medial pterygoid name forms but did not show an exact Korean or Hanja "
            "term for either deep or superficial head. Exact part phrase searches did not return a Korean term source. "
            "This records the bounded lookup performed, not proof that no such term exists."
        ),
        "edition": KMLE_EDITION,
        "accessDate": CHECKED,
        "verificationMode": "KMLE_search_index_parent_terms_only; exact_part_name_lookup_no_attestable_result; underlying_dictionary_edition_unexposed",
        "scope": "Missing-field audit for the two medial-pterygoid part IDs; no part name or Hanja inferred from the parent.",
    },
    KMLE_TRAPEZIUS: {
        "title": "KMLE trapezius and descending-part search page, directly opened aggregate HTML",
        "url": "https://m.kmle.co.kr/search.php?Search=descending+part+of+trapezius",
        "locator": (
            "Opened aggregate HTML: lines 282–295 show current Trapezius m. → 등세모근 [옛 용어] 승모근; "
            "lines 302–310 show the generic Descending part → 내림부분 [옛 용어] 고리하행부 / 하행부; "
            "lines 214–240 show parent-level old Korean/Hanja including 승모근(僧帽筋). These are parent or generic-part rows, "
            "not a TA2 trapezius-part Hanja entry; parent Hanja is not inherited by the part IDs."
        ),
        "edition": KMLE_EDITION,
        "accessDate": CHECKED,
        "verificationMode": "KMLE_aggregate_HTML_directly_opened; exact_parent_and_generic_descending_rows_read; underlying_dictionary_edition_unexposed",
        "scope": "Negative evidence boundary for part-specific Hanja; not used to construct a trapezius Korean part label.",
    },
    YES24: {
        "title": "Kuribara Osamu, 실전 근육 기능 평가법 — directly opened YES24 product listing and displayed table of contents",
        "url": "https://www.yes24.com/product/goods/58476950",
        "locator": (
            "Directly opened YES24 product listing, Table of contents content at page lines 535 onward: p.40 '등세모근 위부분(승모근 상부, superior part of trapezius muscle)'; "
            "p.42 '등세모근 중간부분(승모근 중부, middle part of trapezius muscle)'; p.44 '등세모근 아래부분(승모근 하부, "
            "inferior part of trapezius muscle)'; p.22 '큰가슴근 빗장부분(대흉근 쇄골부, clavicular head of pectoralis major muscle)'; "
            "p.24 '큰가슴근 복장갈비부분(대흉근 흉늑부, sternocostal head of pectoralis major muscle)'. Catalog metadata identifies "
            "Korean translation, Shinheung Med Science, 2018-02-15. The product listing itself was opened; the textbook body text was not accessed."
        ),
        "edition": "Kuribara Osamu. 실전 근육 기능 평가법: 그림과 사진으로 배우는 촉진·스트레칭·근육 테스트. Korean translation, 신흥메드싸이언스, 2018-02-15. Catalog/TOC excerpt only; textbook edition details beyond listing are not exposed.",
        "accessDate": CHECKED,
        "verificationMode": "YES24_product_listing_directly_opened; displayed_table_of_contents_excerpt_read; book_text_not_accessed",
        "scope": "Term-string and Korean/English TOC pair observations; not a primary anatomy review, not Hanja evidence, and not source text for attachments/function.",
    },
}

ROWS = {
    "HA-P-000004": {"row": 2107, "page": 77, "pdf": "P56", "cells": {"latinTerm": "Pars profunda masseteris", "latinSynonym": None, "ukEnglish": "Deep part of masseter", "usEnglish": "Deep part of masseter", "englishSynonym": None, "other": None}},
    "HA-P-000005": {"row": 2110, "page": 77, "pdf": "P56", "cells": {"latinTerm": "Caput superius musculi pterygoidei lateralis", "latinSynonym": None, "ukEnglish": "Superior head of lateral pterygoid muscle", "usEnglish": "Superior head of lateral pterygoid muscle", "englishSynonym": None, "other": "Upper head of lateral pterygoid muscle; Sphenomeniscus muscle"}},
    "HA-P-000006": {"row": 2111, "page": 77, "pdf": "P56", "cells": {"latinTerm": "Caput inferius musculi pterygoidei lateralis", "latinSynonym": None, "ukEnglish": "Inferior head of lateral pterygoid muscle", "usEnglish": "Inferior head of lateral pterygoid muscle", "englishSynonym": None, "other": "Lower head of lateral pterygoid muscle"}},
    "HA-P-000007": {"row": 2114, "page": 77, "pdf": "P56", "cells": {"latinTerm": "Caput profundum musculi pterygoidei medialis", "latinSynonym": None, "ukEnglish": "Deep head of medial pterygoid muscle", "usEnglish": "Deep head of medial pterygoid muscle", "englishSynonym": None, "other": None}},
    "HA-P-000008": {"row": 2115, "page": 77, "pdf": "P56", "cells": {"latinTerm": "Caput superficiale musculi pterygoidei medialis", "latinSynonym": None, "ukEnglish": "Superficial head of medial pterygoid muscle", "usEnglish": "Superficial head of medial pterygoid muscle", "englishSynonym": None, "other": None}},
    "HA-P-000009": {"row": 2227, "page": 81, "pdf": "P60", "cells": {"latinTerm": "Pars descendens musculi trapezii", "latinSynonym": None, "ukEnglish": "Descending part of trapezius muscle", "usEnglish": "Descending part of trapezius muscle", "englishSynonym": None, "other": "Superior part of trapezius muscle"}},
    "HA-P-000010": {"row": 2228, "page": 81, "pdf": "P60", "cells": {"latinTerm": "Pars transversa musculi trapezii", "latinSynonym": None, "ukEnglish": "Transverse part of trapezius muscle", "usEnglish": "Transverse part of trapezius muscle", "englishSynonym": None, "other": "Middle part of trapezius muscle"}},
    "HA-P-000011": {"row": 2229, "page": 81, "pdf": "P60", "cells": {"latinTerm": "Pars ascendens musculi trapezii", "latinSynonym": None, "ukEnglish": "Ascending part of trapezius muscle", "usEnglish": "Ascending part of trapezius muscle", "englishSynonym": None, "other": "Inferior part of trapezius muscle"}},
    "HA-P-000012": {"row": 2302, "page": 83, "pdf": "P62", "cells": {"latinTerm": "Pars clavicularis musculi pectoralis majoris", "latinSynonym": None, "ukEnglish": "Clavicular head of pectoralis major muscle", "usEnglish": "Clavicular head of pectoralis major muscle", "englishSynonym": None, "other": None}},
    "HA-P-000013": {"row": 2303, "page": 83, "pdf": "P62", "cells": {"latinTerm": "Pars sternocostalis musculi pectoralis majoris", "latinSynonym": None, "ukEnglish": "Sternocostal head of pectoralis major muscle", "usEnglish": "Sternocostal head of pectoralis major muscle", "englishSynonym": None, "other": None}},
}

FIELDS = {
    "HA-P-000004": {
        "label": {"value": "심부 교근", "state": "KMLE_indexed_Korean_phrase_in_deep_part_description", "source": KMLE_MASSETER, "locator": "KMLE search-index excerpt for the exact query 'deep part of masseter muscle'; Korean masseter description says '심부 교근은'. This is descriptive text, not a dedicated headword row."},
        "korean": {"value": None, "state": "missing_no_part_specific_current_Korean_term", "source": KMLE_MASSETER, "locator": "The excerpt supports the legacy phrase 심부 교근 but exposes no distinct current Korean term for the assigned part; do not synthesize 깊은교근/깊은부분."},
        "hanjaSource": KMLE_MASSETER,
        "hanjaLocator": "KMLE search-index excerpt for the deep-part query contains no part-specific Hanja; the result is descriptive text, not a headword. Parent masseter Hanja is not inherited.",
        "hanjaMissingReason": "No exact part-specific Hanja was observed. Parent masseter Hanja or characters inferred from 교근 are not inherited or generated.",
        "labelSourceValue": "심부 교근",
        "koreanMissingReason": "Only the descriptive phrase 심부 교근 was observed, not a dedicated current Korean part term. A distinct standard/우리말 part term remains unverified.",
        "extras": [],
    },
    "HA-P-000005": {
        "label": {"value": "외익돌근 상두", "state": "KMLE_indexed_customary_Korean_head_term", "source": KMLE_LATERAL, "locator": "KMLE pterygoid search-index excerpt, 경북대 치과대학 구강내과 교실 사전: 'superior lateral pterygoid muscle' → 외익돌근 상두. TA2 row 2110 independently supplies the matching superior head of lateral pterygoid concept."},
        "korean": {"value": None, "state": "missing_no_part_specific_current_Korean_term", "source": KMLE_LATERAL, "locator": "KMLE index attests the older customary form 외익돌근 상두; no current Korean head-specific term was found. The parent modern name 가쪽날개근 is not extended to this head."},
        "hanjaSource": KMLE_LATERAL,
        "hanjaLocator": "KMLE pterygoid search-index excerpt returns the Korean superior-head phrase but shows no head-specific Hanja. Parent pterygoid Hanja is not inherited.",
        "hanjaMissingReason": "No head-specific Hanja was shown for the superior lateral pterygoid head. Parent pterygoid Hanja is not inherited.",
        "labelSourceValue": "외익돌근 상두",
        "koreanMissingReason": "Only the indexed customary term 외익돌근 상두 was observed; a current Korean term for this specific head is not attested by the accessed results.",
        "extras": [
            {"value": "Upper head of lateral pterygoid muscle", "source": FIPAT, "state": "TA2_Other_cell_English_synonym", "cell": "other"},
            {"value": "Sphenomeniscus muscle", "source": FIPAT, "state": "TA2_Other_cell_synonym", "cell": "other"},
        ],
    },
    "HA-P-000006": {
        "label": {"value": "외익돌근 하두", "state": "KMLE_indexed_customary_Korean_head_term", "source": KMLE_LATERAL, "locator": "KMLE pterygoid search-index excerpt, 경북대 치과대학 구강내과 교실 사전: 'inferior lateral pterygoid' → 외익돌근 하두. TA2 row 2111 independently supplies the matching inferior head of lateral pterygoid concept."},
        "korean": {"value": None, "state": "missing_no_part_specific_current_Korean_term", "source": KMLE_LATERAL, "locator": "KMLE index attests the older customary form 외익돌근 하두; no current Korean head-specific term was found. The parent modern name 가쪽날개근 is not extended to this head."},
        "hanjaSource": KMLE_LATERAL,
        "hanjaLocator": "KMLE pterygoid search-index excerpt returns the Korean inferior-head phrase but shows no head-specific Hanja. Parent pterygoid Hanja is not inherited.",
        "hanjaMissingReason": "No head-specific Hanja was shown for the inferior lateral pterygoid head. Parent pterygoid Hanja is not inherited.",
        "labelSourceValue": "외익돌근 하두",
        "koreanMissingReason": "Only the indexed customary term 외익돌근 하두 was observed; a current Korean term for this specific head is not attested by the accessed results.",
        "extras": [{"value": "Lower head of lateral pterygoid muscle", "source": FIPAT, "state": "TA2_Other_cell_English_synonym", "cell": "other"}],
    },
    "HA-P-000007": {
        "label": {"value": "Deep head of medial pterygoid muscle", "state": "TA2_English_display_fallback_Korean_term_missing", "source": FIPAT, "locator": "TA2 row 2114 UK English cell, directly opened original PDF text; no Korean display term was substituted."},
        "korean": {"value": None, "state": "missing_no_part_specific_Korean_term_or_Hanja", "source": KMLE_MEDIAL, "locator": "The bounded KMLE index lookup shows the medial-pterygoid parent terms but no exact Korean for the deep head; exact head-term searches produced no attestable Korean result."},
        "hanjaSource": KMLE_MEDIAL,
        "hanjaLocator": "KMLE bounded medial-pterygoid and exact head-term index lookup did not expose a part-specific Hanja result; parent forms are not inherited.",
        "hanjaMissingReason": "No part-specific Hanja source was located for this head. Parent medial-pterygoid forms are not inherited.",
        "labelSourceValue": "Deep head of medial pterygoid muscle",
        "koreanMissingReason": "Part-specific Korean customary and current name evidence was not found in the accessed index results; no translated form is generated.",
        "extras": [],
    },
    "HA-P-000008": {
        "label": {"value": "Superficial head of medial pterygoid muscle", "state": "TA2_English_display_fallback_Korean_term_missing", "source": FIPAT, "locator": "TA2 row 2115 UK English cell, directly opened original PDF text; no Korean display term was substituted."},
        "korean": {"value": None, "state": "missing_no_part_specific_Korean_term_or_Hanja", "source": KMLE_MEDIAL, "locator": "The bounded KMLE index lookup shows the medial-pterygoid parent terms but no exact Korean for the superficial head; exact head-term searches produced no attestable Korean result."},
        "hanjaSource": KMLE_MEDIAL,
        "hanjaLocator": "KMLE bounded medial-pterygoid and exact head-term index lookup did not expose a part-specific Hanja result; parent forms are not inherited.",
        "hanjaMissingReason": "No part-specific Hanja source was located for this head. Parent medial-pterygoid forms are not inherited.",
        "labelSourceValue": "Superficial head of medial pterygoid muscle",
        "koreanMissingReason": "Part-specific Korean customary and current name evidence was not found in the accessed index results; no translated form is generated.",
        "extras": [],
    },
    "HA-P-000009": {
        "label": {"value": "승모근 상부", "state": "YES24_listing_customary_Korean_equivalent_of_TA2_Other", "source": YES24, "locator": "Directly opened YES24 product listing TOC at page line 535, p.40: 등세모근 위부분(승모근 상부, superior part of trapezius muscle). TA2 row 2227 lists Superior part of trapezius muscle in Other."},
        "korean": {"value": "등세모근 위부분", "state": "YES24_listing_current_Korean_equivalent_of_TA2_Other", "source": YES24, "locator": "Directly opened YES24 product listing TOC at page line 535, p.40: exact paired phrase 등세모근 위부분 / 승모근 상부 / superior part of trapezius muscle; mapped through the TA2 row 2227 Other-cell synonym."},
        "hanjaSource": KMLE_TRAPEZIUS,
        "hanjaLocator": "Opened KMLE aggregate HTML parent rows at lines 214–240 show 僧帽筋 for the parent only; no part-specific Hanja row was present.",
        "hanjaMissingReason": "The opened KMLE HTML shows parent trapezius Hanja 僧帽筋 but no part-specific Hanja. Parent Hanja is not inherited by this part.",
        "labelSourceValue": "승모근 상부",
        "koreanSourceValue": "등세모근 위부분",
        "extras": [{"value": "Superior part of trapezius muscle", "source": FIPAT, "state": "TA2_Other_cell_English_synonym", "cell": "other"}],
    },
    "HA-P-000010": {
        "label": {"value": "승모근 중부", "state": "YES24_listing_customary_Korean_equivalent_of_TA2_Other", "source": YES24, "locator": "Directly opened YES24 product listing TOC at page line 535, p.42: 등세모근 중간부분(승모근 중부, middle part of trapezius muscle). TA2 row 2228 lists Middle part of trapezius muscle in Other."},
        "korean": {"value": "등세모근 중간부분", "state": "YES24_listing_current_Korean_equivalent_of_TA2_Other", "source": YES24, "locator": "Directly opened YES24 product listing TOC at page line 535, p.42: exact paired phrase 등세모근 중간부분 / 승모근 중부 / middle part of trapezius muscle; mapped through the TA2 row 2228 Other-cell synonym."},
        "hanjaSource": KMLE_TRAPEZIUS,
        "hanjaLocator": "Opened KMLE aggregate HTML parent rows at lines 214–240 show 僧帽筋 for the parent only; no part-specific Hanja row was present.",
        "hanjaMissingReason": "The opened KMLE HTML shows parent trapezius Hanja 僧帽筋 but no part-specific Hanja. Parent Hanja is not inherited by this part.",
        "labelSourceValue": "승모근 중부",
        "koreanSourceValue": "등세모근 중간부분",
        "extras": [{"value": "Middle part of trapezius muscle", "source": FIPAT, "state": "TA2_Other_cell_English_synonym", "cell": "other"}],
    },
    "HA-P-000011": {
        "label": {"value": "승모근 하부", "state": "YES24_listing_customary_Korean_equivalent_of_TA2_Other", "source": YES24, "locator": "Directly opened YES24 product listing TOC at page line 535, p.44: 등세모근 아래부분(승모근 하부, inferior part of trapezius muscle). TA2 row 2229 lists Inferior part of trapezius muscle in Other."},
        "korean": {"value": "등세모근 아래부분", "state": "YES24_listing_current_Korean_equivalent_of_TA2_Other", "source": YES24, "locator": "Directly opened YES24 product listing TOC at page line 535, p.44: exact paired phrase 등세모근 아래부분 / 승모근 하부 / inferior part of trapezius muscle; mapped through the TA2 row 2229 Other-cell synonym."},
        "hanjaSource": KMLE_TRAPEZIUS,
        "hanjaLocator": "Opened KMLE aggregate HTML parent rows at lines 214–240 show 僧帽筋 for the parent only; no part-specific Hanja row was present.",
        "hanjaMissingReason": "The opened KMLE HTML shows parent trapezius Hanja 僧帽筋 but no part-specific Hanja. Parent Hanja is not inherited by this part.",
        "labelSourceValue": "승모근 하부",
        "koreanSourceValue": "등세모근 아래부분",
        "extras": [{"value": "Inferior part of trapezius muscle", "source": FIPAT, "state": "TA2_Other_cell_English_synonym", "cell": "other"}],
    },
    "HA-P-000012": {
        "label": {"value": "대흉근 쇄골부", "state": "YES24_listing_customary_Korean_equivalent", "source": YES24, "locator": "Directly opened YES24 product listing TOC at page line 535, p.22: 큰가슴근 빗장부분(대흉근 쇄골부, clavicular head of pectoralis major muscle), matching TA2 row 2302 English term."},
        "korean": {"value": "큰가슴근 빗장부분", "state": "YES24_listing_current_Korean_equivalent", "source": YES24, "locator": "Directly opened YES24 product listing TOC at page line 535, p.22: exact paired phrase 큰가슴근 빗장부분 / 대흉근 쇄골부 / clavicular head of pectoralis major muscle, matching TA2 row 2302."},
        "hanjaSource": YES24,
        "hanjaLocator": "YES24 catalog TOC excerpt p.22 supplies Korean and English terms but no part-specific Hanja; textbook text was not accessed.",
        "hanjaMissingReason": "The accessed catalog/TOC provides no part-specific Hanja; Hanja is not generated from 대흉근 or the clavicular descriptor.",
        "labelSourceValue": "대흉근 쇄골부",
        "koreanSourceValue": "큰가슴근 빗장부분",
        "extras": [],
    },
    "HA-P-000013": {
        "label": {"value": "대흉근 흉늑부", "state": "YES24_listing_customary_Korean_equivalent", "source": YES24, "locator": "Directly opened YES24 product listing TOC at page line 535, p.24: 큰가슴근 복장갈비부분(대흉근 흉늑부, sternocostal head of pectoralis major muscle), matching TA2 row 2303 English term."},
        "korean": {"value": "큰가슴근 복장갈비부분", "state": "YES24_listing_current_Korean_equivalent", "source": YES24, "locator": "Directly opened YES24 product listing TOC at page line 535, p.24: exact paired phrase 큰가슴근 복장갈비부분 / 대흉근 흉늑부 / sternocostal head of pectoralis major muscle, matching TA2 row 2303."},
        "hanjaSource": YES24,
        "hanjaLocator": "YES24 catalog TOC excerpt p.24 supplies Korean and English terms but no part-specific Hanja; textbook text was not accessed.",
        "hanjaMissingReason": "The accessed catalog/TOC provides no part-specific Hanja; Hanja is not generated from 대흉근 or the sternocostal descriptor.",
        "labelSourceValue": "대흉근 흉늑부",
        "koreanSourceValue": "큰가슴근 복장갈비부분",
        "extras": [],
    },
}


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def source_evidence(source_id: str, locator: str | None = None):
    source = SOURCES[source_id]
    return {
        "sourceId": source_id,
        "locator": locator or source["locator"],
        "verificationMode": source["verificationMode"],
        "sourceEdition": source["edition"],
        "checkedDate": CHECKED,
    }


def record(identifier: str, field: str, value, state: str, source_id: str, locator: str, *, source_value=None, missing_reason=None):
    return {
        "entryId": identifier,
        "field": field,
        "value": value,
        "state": state,
        "evidence": [source_evidence(source_id, locator)],
        "sourceValue": source_value,
        "missingReason": missing_reason,
        "humanAnatomyReviewStatus": "not_performed",
        "humanReviewed": False,
    }


def fipat_locator(identifier: str, cell: str, value: str):
    row = ROWS[identifier]
    return (
        f"TA2 Chapter 4, PDF text page {row['pdf']}, printed p.{row['page']}, table row {row['row']}; "
        f"exact text '{value}' in the {cell} column named in the opened Chapter 4 header at PDF text P52/printed p.73. "
        "Text layer directly checked; visual page layout not inspected."
    )


def main():
    names = read_json(NAMES_PATH)
    ledger = read_json(BATCH_PATH)
    coverage = [row for row in ledger["canonicalCoverage"] if row["batchId"] == "T11-B08"]
    if [row["id"] for row in coverage] != IDS:
        raise SystemExit("T11-B08 assignment changed; refusing to touch any other ID")
    if any(row["status"] != "not_started" for row in coverage):
        raise SystemExit("T11-B08 coverage is not untouched; refusing non-idempotent rebuild")
    if any(row["id"] in IDS for row in ledger["entries"]):
        raise SystemExit("B08 evidence entries already exist; refusing duplicate build")
    existing_overlays = {row["id"]: row for row in names["entries"] if row["id"] in IDS}
    if existing_overlays:
        raise SystemExit(f"Unexpected pre-existing B08 overlays; refusing overwrite: {sorted(existing_overlays)}")

    catalog = {row["id"]: row for row in read_json(ROOT / "atlas-data/catalog/canonical-catalog.json")["entities"]["muscleConcepts"]}
    crosswalk = read_json(ROOT / "atlas-data/catalog/source-crosswalk.json")
    crosswalk_terms = {identifier: {row["sourceLanguage"]: row for row in crosswalk["termRecords"] if row["conceptId"] == identifier and row["sourceTextObserved"]} for identifier in IDS}
    assigned = {row["id"]: row for row in coverage}
    new_entries = []
    all_field_evidence = []
    overlays = []

    for identifier in IDS:
        concept = catalog[identifier]
        cov = assigned[identifier]
        locator = cov["sourceCrosswalkLocator"]
        spec = FIELDS[identifier]
        row = ROWS[identifier]
        cells = row["cells"]
        old_latin = locator.get("latinTextObservation")
        old_english = locator.get("englishTextObservation")
        old_edition = locator.get("edition")
        if (locator["tableRow"], locator["printedPage"]) != (row["row"], row["page"]):
            raise SystemExit(f"Frozen TA2 locator changed for {identifier}")
        expected_terms = crosswalk_terms[identifier]
        if set(expected_terms) < {"en", "la"}:
            raise SystemExit(f"Canonical English/Latin crosswalk missing for {identifier}")
        if old_latin != cells["latinTerm"] or old_english != cells["ukEnglish"]:
            raise SystemExit(f"T04 crosswalk row strings do not match direct B08 PDF observations: {identifier}")
        if expected_terms["la"]["sourceTextObserved"] != old_latin or expected_terms["en"]["sourceTextObserved"] != old_english:
            raise SystemExit(f"T04 term crosswalk mismatch for {identifier}")

        locator["priorT04IndexObservation"] = {
            "edition": old_edition,
            "latinTextObservation": old_latin,
            "englishTextObservation": old_english,
            "state": "preserved_index_observation; B08 directly opened PDF text cells independently confirmed the recorded strings",
            "sourceCrosswalkFilePreserved": "atlas-data/catalog/source-crosswalk.json",
        }
        locator.update({
            "edition": FIPAT_EDITION,
            "part": "TA2 Part II, Chapter 4: Muscular system",
            "latinTextObservation": cells["latinTerm"],
            "englishTextObservation": cells["ukEnglish"],
            "observedTableCells": cells,
            "cellRoleStatus": "Chapter_4_column_roles_confirmed_from_opened_PDF_text_header; assigned_text_rows_read; visual_table_layout_not_inspected",
            "existingEvidenceMode": "T04 official index locator preserved; T04 row and English/Latin observations were confirmed against exact cells in the directly opened official-hosted original PDF text layer; no page screenshot.",
        })

        label = spec["label"]
        korean = spec["korean"]
        english = cells["ukEnglish"]
        hanja_source = spec["hanjaSource"]
        field_rows = [
            record(identifier, "label", label["value"], label["state"], label["source"], label["locator"], source_value=spec.get("labelSourceValue", label.get("sourceValue"))),
            record(identifier, "korean", korean["value"], korean["state"], korean["source"], korean["locator"], source_value=spec.get("koreanSourceValue"), missing_reason=spec.get("koreanMissingReason")),
            record(identifier, "hanja", None, "missing_no_attested_part_specific_hanja", hanja_source, spec["hanjaLocator"], missing_reason=spec["hanjaMissingReason"]),
            record(identifier, "english", english, "TA2_opened_original_PDF_UK_English_cell", FIPAT, fipat_locator(identifier, "UK English", english), source_value=english),
            record(identifier, "aliases[0]", cells["latinTerm"], "TA2_opened_original_PDF_Latin_term_cell", FIPAT, fipat_locator(identifier, "Latin term", cells["latinTerm"]), source_value=cells["latinTerm"]),
        ]
        alias_values = [cells["latinTerm"]]
        for index, extra in enumerate(spec["extras"], start=1):
            if extra["source"] != FIPAT:
                raise SystemExit(f"B08 alias extra must be sourced from a checked TA2 cell: {identifier}")
            value = cells[extra["cell"]]
            if extra["value"] not in [part.strip() for part in value.split(";") if part.strip()]:
                raise SystemExit(f"TA2 alias cell mismatch {identifier} {extra['cell']}")
            cell_name = "Other" if extra["cell"] == "other" else "English synonym"
            field_rows.append(record(identifier, f"aliases[{index}]", extra["value"], extra["state"], FIPAT, fipat_locator(identifier, cell_name, extra["value"]), source_value=value))
            alias_values.append(extra["value"])

        all_field_evidence.extend(field_rows)
        source_ids = {FIPAT, label["source"], korean["source"], hanja_source, *(x["source"] for x in spec["extras"])}
        source_ids = sorted(source_ids)
        overlay = {
            "id": identifier,
            "label": label["value"],
            "korean": korean["value"],
            "english": english,
            "hanja": None,
            "aliases": alias_values,
            "sourceIds": source_ids,
            "parentId": concept.get("parentId"),
            "entityType": concept["entityType"],
            "lookupOnly": False,
            "status": "web_attested_with_gaps",
            "humanReviewed": False,
            "hanjaNote": spec["hanjaMissingReason"],
        }
        if spec.get("koreanMissingReason"):
            overlay["koreanNote"] = spec["koreanMissingReason"]
        overlays.append(overlay)

        new_entry = {
            "id": identifier,
            "isCanonical": True,
            "entityType": concept["entityType"],
            "parentId": concept.get("parentId"),
            "lookupOnly": False,
            "canonicalStatus": "canonical_existing_id",
            "canonicalSourceRow": {"sourceId": "FIPAT_TA2", "tableRow": row["row"], "printedPage": row["page"]},
            "displayField": "label",
            "displayValue": label["value"],
            "fieldEvidence": field_rows,
            "unadoptedCandidates": [],
            "webVerificationStatus": "web_checked_with_gaps",
            "humanAnatomyReviewStatus": "not_performed",
            "humanReviewer": None,
            "humanReviewed": False,
            "fieldEvidenceCount": len(field_rows),
        }
        new_entries.append(new_entry)
        cov["status"] = "web_checked_with_gaps"
        cov["statusReason"] = (
            "Exact assigned TA2 Latin and English cells were directly checked in the official-hosted original PDF text layer. "
            "Korean customary/current terms are based only on the per-field KMLE index or YES24 table-of-contents excerpt noted in evidence. "
            "No part-specific Hanja was verified; gaps remain null. Human anatomy review and visual PDF table inspection were not performed."
        )

    for source_id, source in SOURCES.items():
        names["sources"][source_id] = source
        ledger["sources"][source_id] = source
    names["entries"].extend(overlays)
    ledger["entries"].extend(new_entries)
    ledger["fieldEvidence"].extend(all_field_evidence)
    names["revision"] = "T11-B08-web-checked-2026-09-25"
    names["accessedAt"] = CHECKED
    ledger["revision"] = "T11-B08-web-checked-2026-09-25"
    ledger["checkedDate"] = CHECKED
    ledger["overallT11Status"] = "in_progress_partial"
    for batch in ledger["batchOrder"]:
        if batch["batchId"] == "T11-B08":
            batch["status"] = "complete_with_gaps"
    ledger["notes"].append(
        "T11-B08 complete with gaps: 10 fixed existing part IDs; five required core field records each plus "
        f"{len(all_field_evidence) - 50} separately evidenced TA2 alias records, {len(all_field_evidence)} B08 records total. "
        "Exact TA2 2.07 Part II original PDF text cells and Chapter 4 column roles were directly opened and checked; no rendered-page audit. "
        "KMLE exact Korean dictionary edition is not exposed; the YES24 product-listing TOC was directly opened but the textbook body was not accessed. "
        "Part-specific Hanja and medial-pterygoid head Korean terms remain missing; no human anatomy review. "
        "T11 has nine batches B01–B09; B09 and T12 remain not started."
    )
    write_json(NAMES_PATH, names)
    write_json(BATCH_PATH, ledger)
    print(json.dumps({
        "batchId": "T11-B08",
        "canonicalIds": IDS,
        "requiredCoreFieldEvidence": 50,
        "additionalAliasEvidence": len(all_field_evidence) - 50,
        "batchFieldEvidence": len(all_field_evidence),
        "cumulativeFieldEvidence": len(ledger["fieldEvidence"]),
        "learnerOverlaysTotal": len(names["entries"]),
        "newOverlays": len(overlays),
        "hanjaAttested": 0,
        "koreanCurrentTermMissing": [identifier for identifier in IDS if FIELDS[identifier]["korean"]["value"] is None],
        "humanReviewed": False,
        "nextBatchStarted": False,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
