"""Build only the fixed T11-B09 field evidence and existing-ID overlays."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
CHECKED = "2026-09-25"
IDS = [
    "HA-P-000014",
    "HA-P-000016",
    "HA-P-000017",
    "HA-P-000018",
    "HA-P-000019",
    "HA-P-000020",
    "HA-P-000021",
]
FIPAT = "fipat-ta2-b09-opened-original-pdf"
KMLE_BICEPS = "kmle-b09-biceps-opened-html"
KMLE_SHORT = "kmle-b09-short-biceps-index"
KMLE_TRICEPS = "kmle-b09-triceps-lateral-opened-html"
KMLE_MEDIAL = "kmle-b09-medial-head-index"
KMLE_CLAVICULAR = "kmle-b09-clavicular-part-index"
KMLE_DELTOID_GAP = "kmle-b09-deltoid-part-gap-index"
KMLE_SPINAL_GAP = "kmle-b09-spinal-part-gap-index"
FIPAT_URL = "https://cdn.dal.ca/content/dam/dalhousie/pdf/library/FIPAT/TA2/FIPAT-TA2-Part-2.pdf"
FIPAT_EDITION = (
    "FIPAT, Terminologia Anatomica, Second Edition (2.07), TA2 Part II; "
    "bibliographic citation 2019; approved and adopted by IFAA General Assembly in 2020."
)
KMLE_EDITION = (
    "KMLE web aggregation. Named dictionary sections are recorded where visible; "
    "the underlying Korean dictionary edition/revision is not exposed."
)
NAMES_PATH = ROOT / "atlas-data/terminology/learning-names.json"
BATCH_PATH = ROOT / "atlas-data/terminology/term-review-batches.json"
CROSSWALK_PATH = ROOT / "atlas-data/catalog/source-crosswalk.json"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


SOURCES = {
    FIPAT: {
        "title": "FIPAT Terminologia Anatomica Second Edition (2.07), TA2 Part II, official Dalhousie-hosted original PDF directly opened",
        "url": FIPAT_URL,
        "locator": (
            "Front matter PDF text P0 lines 0–18 identifies Second Edition (2.07), 2019 citation, "
            "2020 IFAA approval/adoption, and CC BY-ND 4.0. Chapter 4 header PDF text P52 / printed "
            "p.73 lines 3494–3495 names Latin term, Latin synonym, UK English, US English, English synonym, Other. "
            "Assigned rows 2453, 2455, 2465, 2466, 2472–2474 are on PDF text P68 / printed p.89. "
            "Exact row text was read from the directly opened PDF text layer; rendered page image was not inspected."
        ),
        "edition": FIPAT_EDITION,
        "accessDate": CHECKED,
        "verificationMode": (
            "official_Dalhousie_hosted_original_PDF_directly_opened; front_matter_Ch4_header_and_exact_rows_read_from_text_layer; "
            "no_visual_page_screenshot"
        ),
        "scope": "TA2 Latin/English term cells, aliases, edition, and locators only; no Korean or Hanja translation and no human anatomy review.",
    },
    KMLE_BICEPS: {
        "title": "KMLE long-head of biceps query, directly opened aggregate HTML with legacy and KAA dictionary sections",
        "url": "https://m.kmle.co.kr/search.php?Search=long+head+of+biceps+brachii+muscle",
        "locator": (
            "Directly opened HTML lines 297–318 show old Korean Medical Association dictionary section: "
            "long head of biceps brachii muscle → 상완이두근장두; long head of biceps muscle of arm → "
            "상완 이두근 장 두; short head of biceps muscle of arm → 상완두갈래근짧은갈래, 상완이두박근단두. "
            "Lines 376–384 show named 대한해부학회 section: Biceps brachii m. → 위팔두갈래근 "
            "[old term 상완이두근], Long head → 긴갈래 [old term 장두]. "
            "The page was directly opened, but the underlying dictionary editions/revisions are not exposed."
        ),
        "edition": KMLE_EDITION,
        "accessDate": CHECKED,
        "verificationMode": "KMLE_aggregate_HTML_directly_opened; result_sections_and_exact_term_rows_read; underlying_dictionary_editions_unexposed",
        "scope": "Term-string observations for the existing biceps long-head concept; no parent Hanja inheritance and no anatomy review.",
    },
    KMLE_SHORT: {
        "title": "KMLE short-head of biceps query, search-index excerpts",
        "url": "https://m.kmle.co.kr/search.php?Page=1&Search=short+head+of+biceps+brachii+muscle",
        "locator": (
            "Search-index excerpts show the exact legacy short-head phrase and KMLE current Korean lookup "
            "Short head → 짧은갈래 [old term 단두], plus the named 경북대 치과대학 구강내과 교실 사전 row "
            "caput breve musculi bicipitis brachii → 상완 이두근 단두, 위팔 두 갈래근 짧은 갈래. "
            "Direct HTML for this exact query did not open; underlying dictionary editions/revisions are not exposed."
        ),
        "edition": KMLE_EDITION,
        "accessDate": CHECKED,
        "verificationMode": "KMLE_search_index_excerpt_only; exact_query_HTML_open_returned_Internal_Error; underlying_dictionary_editions_unexposed",
        "scope": "Korean short-head term observations only; no Hanja was shown for the assigned part.",
    },
    KMLE_TRICEPS: {
        "title": "KMLE lateral-head of triceps query, directly opened aggregate HTML with legacy conflict, KAA, dental, and English index sections",
        "url": "https://m.kmle.co.kr/search.php?Search=lateral+head+of+triceps+brachii+muscle",
        "locator": (
            "Directly opened HTML lines 302–312 show a legacy result that incorrectly pairs "
            "'lateral head of triceps muscle of arm' with caput longum and Korean 장두; this is retained as an "
            "unadopted conflict. Lines 368–390 show named 대한해부학회 rows Triceps brachii m. → 위팔세갈래근 "
            "and Lateral head → 가쪽갈래 [old term 외측두]. Lines 663–675 show the named dental-dictionary row "
            "caput laterale musculii tricipitis brachii → 상완 삼두근 외측두, 위팔 세 갈래 근 가쪽 갈래. "
            "The page was directly opened; dictionary editions/revisions are not exposed."
        ),
        "edition": KMLE_EDITION,
        "accessDate": CHECKED,
        "verificationMode": "KMLE_aggregate_HTML_directly_opened; conflicting_legacy_and_current_named_dictionary_rows_read; editions_unexposed",
        "scope": "Term observations for triceps heads only. The legacy lateral-to-long-head mapping is excluded from search aliases.",
    },
    KMLE_MEDIAL: {
        "title": "KMLE medial-head term search-index result",
        "url": "https://m.kmle.co.kr/search.php?Search=medial+canthus",
        "locator": (
            "Search-index excerpt in the named 대한해부학회 medical terminology section shows "
            "Medial head → 안쪽갈래 [old term 내측두]. It is a generic head descriptor, not a full triceps-specific "
            "row. It is linked only with the exact TA2 medial-head row 2474 context; direct HTML was not opened."
        ),
        "edition": KMLE_EDITION,
        "accessDate": CHECKED,
        "verificationMode": "KMLE_search_index_excerpt_only; generic_named_KAA_head_term; direct_HTML_not_opened; edition_unexposed",
        "scope": "Generic Korean translation of the exact Medial head descriptor; not a full anatomy review.",
    },
    KMLE_CLAVICULAR: {
        "title": "KMLE clavicular-part terminology search-index result",
        "url": "https://m.kmle.co.kr/search.php?Search=clav",
        "locator": (
            "Search-index excerpt in the named 대한해부학회 medical terminology section shows "
            "Clavicular part → 빗장부분 [old term 쇄골부]. The term is generic; it is attached only to the "
            "exact clavicular-part phrase in TA2 row 2453. Direct HTML and underlying dictionary edition were not available."
        ),
        "edition": KMLE_EDITION,
        "accessDate": CHECKED,
        "verificationMode": "KMLE_search_index_excerpt_only; generic_named_KAA_part_term; direct_HTML_not_opened; edition_unexposed",
        "scope": "Generic Korean translation of Clavicular part, cross-referenced to exact TA2 row 2453; not a complete deltoid-specific Korean term.",
    },
    KMLE_DELTOID_GAP: {
        "title": "KMLE deltoid part bounded lookup and Hanja gap check",
        "url": "https://m.kmle.co.kr/search.php?Search=deltoid+muscle",
        "locator": (
            "Search-index lookup for deltoid muscle exposed general deltoid results but no exact Korean or Hanja "
            "for clavicular part or scapular spinal part. One nearby clavicular-part result refers to pectoralis major, "
            "not deltoid, and was not transferred. This is the bounded result observed, not proof no such term exists."
        ),
        "edition": KMLE_EDITION,
        "accessDate": CHECKED,
        "verificationMode": "KMLE_search_index_bounded_exact_deltoid_part_lookup; no_attestable_part_specific_result; edition_unexposed",
        "scope": "Missing Korean/Hanja audit for the two deltoid part IDs only; no parent term is inherited.",
    },
    KMLE_SPINAL_GAP: {
        "title": "KMLE spinal-part term search-index ambiguity check",
        "url": "https://m.kmle.co.kr/search.php?Search=spinal",
        "locator": (
            "Search-index result in the named 대한해부학회 section shows generic Spinal part → 척수부분 "
            "[old term 척수부]. This denotes a spinal-cord phrase in the displayed dictionary context; it was "
            "not linked to the scapular spinal portion of deltoid. Exact Korean for that full phrase remains unverified."
        ),
        "edition": KMLE_EDITION,
        "accessDate": CHECKED,
        "verificationMode": "KMLE_search_index_excerpt_only; ambiguous_generic_translation_rejected; edition_unexposed",
        "scope": "Negative/conflict observation for P16; the candidate is not included in learner search.",
    },
}

ROWS = {
    "HA-P-000014": {
        "row": 2453, "page": 89, "cells": {
            "latinTerm": "Pars clavicularis musculi deltoidei",
            "latinSynonym": None,
            "ukEnglish": "Clavicular part of deltoid muscle",
            "usEnglish": "Clavicular part of deltoid muscle",
            "englishSynonym": None,
            "other": None,
        },
    },
    "HA-P-000016": {
        "row": 2455, "page": 89, "cells": {
            "latinTerm": "Pars spinalis scapularis musculi deltoidei",
            "latinSynonym": "Pars spinalis musculi deltoidei",
            "ukEnglish": "Scapular spinal part of deltoid muscle",
            "usEnglish": "Scapular spinal part of deltoid muscle",
            "englishSynonym": "Spinal part of deltoid muscle",
            "other": None,
        },
    },
    "HA-P-000017": {
        "row": 2465, "page": 89, "cells": {
            "latinTerm": "Caput longum musculi bicipitis brachii",
            "latinSynonym": None,
            "ukEnglish": "Long head of biceps brachii",
            "usEnglish": "Long head of biceps brachii",
            "englishSynonym": None,
            "other": None,
        },
    },
    "HA-P-000018": {
        "row": 2466, "page": 89, "cells": {
            "latinTerm": "Caput breve musculi bicipitis brachii",
            "latinSynonym": None,
            "ukEnglish": "Short head of biceps brachii",
            "usEnglish": "Short head of biceps brachii",
            "englishSynonym": None,
            "other": None,
        },
    },
    "HA-P-000019": {
        "row": 2472, "page": 89, "cells": {
            "latinTerm": "Caput longum musculi tricipitis brachii",
            "latinSynonym": None,
            "ukEnglish": "Long head of triceps brachii",
            "usEnglish": "Long head of triceps brachii",
            "englishSynonym": None,
            "other": None,
        },
    },
    "HA-P-000020": {
        "row": 2473, "page": 89, "cells": {
            "latinTerm": "Caput laterale musculi tricipitis brachii",
            "latinSynonym": None,
            "ukEnglish": "Lateral head of triceps brachii",
            "usEnglish": "Lateral head of triceps brachii",
            "englishSynonym": None,
            "other": "Caput radiale musculi tricipitis brachii",
        },
    },
    "HA-P-000021": {
        "row": 2474, "page": 89, "cells": {
            "latinTerm": "Caput mediale musculi tricipitis brachii",
            "latinSynonym": "Caput profundum musculi tricipitis brachii",
            "ukEnglish": "Medial head of triceps brachii",
            "usEnglish": "Medial head of triceps brachii",
            "englishSynonym": "Deep head of triceps brachii",
            "other": "Caput ulnare musculi tricipitis brachii",
        },
    },
}

FIELDS = {
    "HA-P-000014": {
        "label": {
            "value": "쇄골부", "state": "KMLE_indexed_legacy_translation_of_clavicular_part",
            "source": KMLE_CLAVICULAR, "sourceValue": "쇄골부",
            "locator": "Search-index excerpt, named 대한해부학회 section: Clavicular part → 빗장부분 [old term 쇄골부]. Generic descriptor linked to exact deltoid clavicular-part row 2453.",
        },
        "korean": {
            "value": "빗장부분", "state": "KMLE_indexed_current_generic_part_term",
            "source": KMLE_CLAVICULAR, "sourceValue": "빗장부분",
            "locator": "Search-index excerpt, named 대한해부학회 section: Clavicular part → 빗장부분 [old term 쇄골부]. This is a generic part term, not a full deltoid-specific headword.",
        },
        "hanjaSources": [KMLE_DELTOID_GAP, FIPAT],
        "hanjaMissingReason": "No part-specific Hanja was observed in the bounded deltoid lookup or TA2 row. A parent deltoid Hanja, if present elsewhere, is not inherited.",
        "koreanAliases": [],
        "unadoptedCandidates": [],
    },
    "HA-P-000016": {
        "label": {
            "value": "Scapular spinal part of deltoid muscle", "state": "TA2_English_display_fallback_Korean_part_term_missing",
            "source": FIPAT, "sourceValue": "Scapular spinal part of deltoid muscle",
            "locator": "TA2 row 2455 UK English cell, directly opened PDF text layer; no full Korean term was substituted.",
        },
        "korean": {
            "value": None, "state": "missing_no_attestable_full_Korean_term",
            "sources": [KMLE_DELTOID_GAP, KMLE_SPINAL_GAP],
            "sourceValue": None,
            "locator": "Bounded exact deltoid lookup did not expose a Korean part term. Generic Spinal part → 척수부분 is an ambiguous nonmatching result and was withheld.",
            "missingReason": "No Korean term for the full scapular spinal deltoid part was attested. The generic spinal translation points to a different context and is not adopted.",
        },
        "hanjaSources": [KMLE_DELTOID_GAP, FIPAT],
        "hanjaMissingReason": "No part-specific Hanja was observed in the bounded deltoid lookup or TA2 row. A parent deltoid Hanja is not inherited.",
        "koreanAliases": [],
        "unadoptedCandidates": [
            {
                "value": "척수부분",
                "status": "ambiguous_generic_translation_not_linked",
                "sourceIds": [KMLE_SPINAL_GAP],
                "reason": "KMLE shows generic Spinal part → 척수부분; the assigned source phrase is scapular spinal part of deltoid, so the generic translation is contextually ambiguous and excluded from learner search.",
            }
        ],
    },
    "HA-P-000017": {
        "label": {
            "value": "상완이두근장두", "state": "KMLE_indexed_legacy_part_specific_name",
            "source": KMLE_BICEPS, "sourceValue": "상완이두근장두",
            "locator": "Directly opened KMLE HTML lines 297–305, old 대한의협 3 section: long head of biceps brachii muscle → 상완이두근장두.",
        },
        "korean": {
            "value": "긴갈래", "state": "KMLE_indexed_current_generic_head_term",
            "source": KMLE_BICEPS, "sourceValue": "긴갈래",
            "locator": "Directly opened KMLE HTML lines 376–384, named 대한해부학회 section: Biceps brachii m. → 위팔두갈래근 and Long head → 긴갈래 [old term 장두]. Generic head descriptor retained without constructing a combined phrase.",
        },
        "hanjaSources": [KMLE_BICEPS, FIPAT],
        "hanjaMissingReason": "The exact biceps head rows show Korean strings but no head-specific Hanja. Parent 上腕二頭筋, where displayed, is not inherited.",
        "koreanAliases": [
            {
                "value": "상완 이두근 장 두", "source": KMLE_BICEPS,
                "state": "KMLE_indexed_legacy_spaced_variant",
                "locator": "Directly opened KMLE HTML lines 312–314, old 대한의협 3 section: long head of biceps muscle of arm → 상완 이두근 장 두.",
            }
        ],
        "unadoptedCandidates": [],
    },
    "HA-P-000018": {
        "label": {
            "value": "상완두갈래근짧은갈래", "state": "KMLE_indexed_legacy_part_specific_variant",
            "source": KMLE_BICEPS, "sourceValue": "상완두갈래근짧은갈래, 상완이두박근단두",
            "locator": "Directly opened KMLE HTML lines 316–318, old 대한의협 3 section: short head of biceps muscle of arm → 상완두갈래근짧은갈래, 상완이두박근단두.",
        },
        "korean": {
            "value": "위팔 두 갈래근 짧은 갈래", "state": "KMLE_indexed_current_named_dental_dictionary_phrase",
            "source": KMLE_SHORT, "sourceValue": "위팔 두 갈래근 짧은 갈래",
            "locator": "KMLE short-head search-index excerpt, named 경북대 치과대학 구강내과 교실 사전: caput breve musculi bicipitis brachii → 상완 이두근 단두, 위팔 두 갈래근 짧은 갈래.",
        },
        "hanjaSources": [KMLE_BICEPS, KMLE_SHORT, FIPAT],
        "hanjaMissingReason": "No part-specific Hanja was displayed for the short biceps head. Parent 上腕二頭筋, where displayed, is not inherited.",
        "koreanAliases": [
            {
                "value": "상완이두박근단두", "source": KMLE_BICEPS,
                "state": "KMLE_indexed_legacy_part_specific_alias",
                "locator": "Directly opened KMLE HTML lines 316–318, old 대한의협 3 section: short head of biceps muscle of arm → 상완이두박근단두.",
            },
            {
                "value": "짧은갈래", "source": KMLE_SHORT,
                "state": "KMLE_indexed_current_generic_head_term",
                "locator": "KMLE short-head search-index excerpt, named 대한해부학회 section: Short head → 짧은갈래 [old term 단두]. Generic head descriptor retained as a search alias.",
            },
        ],
        "unadoptedCandidates": [],
    },
    "HA-P-000019": {
        "label": {
            "value": "상완삼두근장두", "state": "KMLE_indexed_legacy_part_specific_name",
            "source": KMLE_TRICEPS, "sourceValue": "상완삼두근장두",
            "locator": "Directly opened KMLE HTML lines 306–308, old 대한의협 3 section: long head of triceps brachii muscle → 상완삼두근장두.",
        },
        "korean": {
            "value": "긴갈래", "state": "KMLE_indexed_current_generic_head_term",
            "source": KMLE_BICEPS, "sourceValue": "긴갈래",
            "locator": "Directly opened KMLE HTML lines 381–384, named 대한해부학회 section: Long head → 긴갈래 [old term 장두]. The exact assigned TA2 row 2472 supplies the triceps context; no combined Korean phrase is generated.",
        },
        "hanjaSources": [KMLE_TRICEPS, FIPAT],
        "hanjaMissingReason": "The exact triceps long-head row exposes no head-specific Hanja. Parent 上腕三頭筋, where displayed, is not inherited.",
        "koreanAliases": [
            {
                "value": "상완 삼두근 장 두", "source": KMLE_TRICEPS,
                "state": "KMLE_indexed_legacy_spaced_variant",
                "locator": "Directly opened KMLE HTML lines 317–319, old 대한의협 3 section: long head of triceps muscle of arm → 상완 삼두근 장 두.",
            }
        ],
        "unadoptedCandidates": [],
    },
    "HA-P-000020": {
        "label": {
            "value": "상완 삼두근 외측두", "state": "KMLE_indexed_part_specific_dental_dictionary_phrase",
            "source": KMLE_TRICEPS, "sourceValue": "상완 삼두근 외측두",
            "locator": "Directly opened KMLE HTML lines 663–665, named 경북대 치과대학 구강내과 교실 사전: caput laterale musculii tricipitis brachii → 상완 삼두근 외측두.",
        },
        "korean": {
            "value": "위팔 세 갈래 근 가쪽 갈래", "state": "KMLE_indexed_current_part_specific_dental_dictionary_phrase",
            "source": KMLE_TRICEPS, "sourceValue": "위팔 세 갈래 근 가쪽 갈래",
            "locator": "Directly opened KMLE HTML lines 663–665, same named dental-dictionary row: caput laterale musculii tricipitis brachii → 위팔 세 갈래 근 가쪽 갈래.",
        },
        "hanjaSources": [KMLE_TRICEPS, FIPAT],
        "hanjaMissingReason": "The exact lateral-head row showed Korean spellings but no part-specific Hanja. Parent 上腕三頭筋 is not inherited.",
        "koreanAliases": [
            {
                "value": "가쪽갈래", "source": KMLE_TRICEPS,
                "state": "KMLE_indexed_current_generic_head_term",
                "locator": "Directly opened KMLE HTML lines 387–390, named 대한해부학회 section: Lateral head → 가쪽갈래 [old term 외측두].",
            },
            {
                "value": "외측두", "source": KMLE_TRICEPS,
                "state": "KMLE_indexed_legacy_generic_head_term",
                "locator": "Directly opened KMLE HTML lines 387–390, named 대한해부학회 section: Lateral head → 가쪽갈래 [old term 외측두].",
            },
        ],
        "unadoptedCandidates": [
            {
                "value": "(상완삼두근의) 장두",
                "status": "conflicting_legacy_mapping_not_linked",
                "sourceIds": [KMLE_TRICEPS],
                "reason": "The old KMLE row incorrectly pairs lateral head of triceps muscle of arm with caput longum and labels it 장두. The exact TA2 row 2473 is caput laterale; the conflicting result is excluded from learner search.",
            }
        ],
    },
    "HA-P-000021": {
        "label": {
            "value": "안쪽갈래", "state": "KMLE_indexed_current_generic_head_term",
            "source": KMLE_MEDIAL, "sourceValue": "안쪽갈래",
            "locator": "Search-index excerpt, named 대한해부학회 section: Medial head → 안쪽갈래 [old term 내측두]. The exact TA2 row 2474 supplies the triceps context; no combined phrase is generated.",
        },
        "korean": {
            "value": "안쪽갈래", "state": "KMLE_indexed_current_generic_head_term",
            "source": KMLE_MEDIAL, "sourceValue": "안쪽갈래",
            "locator": "Search-index excerpt, named 대한해부학회 section: Medial head → 안쪽갈래 [old term 내측두]. Generic head descriptor retained without adding parent wording.",
        },
        "hanjaSources": [KMLE_TRICEPS, KMLE_MEDIAL, FIPAT],
        "hanjaMissingReason": "The medial-head search result and exact TA2 row expose no part-specific Hanja. Parent 上腕三頭筋, where displayed, is not inherited.",
        "koreanAliases": [
            {
                "value": "내측두", "source": KMLE_MEDIAL,
                "state": "KMLE_indexed_legacy_generic_head_term",
                "locator": "Search-index excerpt, named 대한해부학회 section: Medial head → 안쪽갈래 [old term 내측두].",
            }
        ],
        "unadoptedCandidates": [],
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


def record(identifier: str, field: str, value, state: str, source_ids: list[str], locator: str,
           *, source_value=None, missing_reason=None):
    return {
        "entryId": identifier,
        "field": field,
        "value": value,
        "state": state,
        "evidence": [source_evidence(source_id, locator if len(source_ids) == 1 else None) for source_id in source_ids],
        "sourceValue": source_value,
        "missingReason": missing_reason,
        "humanAnatomyReviewStatus": "not_performed",
        "humanReviewed": False,
    }


def fipat_locator(identifier: str, cell: str, value: str):
    row = ROWS[identifier]
    return (
        f"TA2 Chapter 4, PDF text page P68, printed p.89, table row {row['row']}; exact text '{value}' "
        f"in the {cell} column named in the opened Chapter 4 header at PDF text P52 / printed p.73. "
        "The table text layer was directly checked; rendered page image was not inspected."
    )


def main():
    names = read_json(NAMES_PATH)
    ledger = read_json(BATCH_PATH)
    coverage = [row for row in ledger["canonicalCoverage"] if row["batchId"] == "T11-B09"]
    if [row["id"] for row in coverage] != IDS:
        raise SystemExit("T11-B09 assignment changed; refusing to touch any other ID")
    if any(row["status"] != "not_started" for row in coverage):
        raise SystemExit("T11-B09 coverage is not untouched; refusing non-idempotent rebuild")
    if any(row["id"] in IDS for row in ledger["entries"]):
        raise SystemExit("B09 evidence entries already exist; refusing duplicate build")
    if any(row["id"] in IDS for row in names["entries"]):
        raise SystemExit("Unexpected pre-existing B09 learner overlays; refusing overwrite")

    batch_map = {row["batchId"]: row for row in ledger["batchOrder"]}
    batch = batch_map["T11-B09"]
    if batch["canonicalIds"] != IDS or batch["size"] != len(IDS) or batch["status"] != "not_started":
        raise SystemExit("B09 batch ledger changed; refusing build")
    concepts = {
        row["id"]: row
        for row in read_json(ROOT / "atlas-data/catalog/canonical-catalog.json")["entities"]["muscleConcepts"]
    }
    crosswalk = read_json(CROSSWALK_PATH)
    crosswalk_sha = sha256(CROSSWALK_PATH.read_bytes())
    crosswalk_items = {row["stableConceptId"]: row for row in crosswalk["catalogItems"]}
    crosswalk_terms = {
        identifier: {
            row["sourceLanguage"]: row
            for row in crosswalk["termRecords"]
            if row["conceptId"] == identifier and row.get("sourceTextObserved")
        }
        for identifier in IDS
    }
    coverage_by_id = {row["id"]: row for row in coverage}
    new_entries = []
    all_field_evidence = []
    overlays = []

    for identifier in IDS:
        spec = FIELDS[identifier]
        row = ROWS[identifier]
        cells = row["cells"]
        concept = concepts[identifier]
        cov = coverage_by_id[identifier]
        locator = cov["sourceCrosswalkLocator"]
        prior_latin = locator.get("latinTextObservation")
        prior_english = locator.get("englishTextObservation")
        if (locator["tableRow"], locator["printedPage"]) != (row["row"], row["page"]):
            raise SystemExit(f"Frozen T04 TA2 locator changed for {identifier}")
        item = crosswalk_items[identifier]
        if item["tableRow"] != row["row"] or item["printedPage"] != row["page"]:
            raise SystemExit(f"T04 source crosswalk row changed for {identifier}")
        if prior_latin != cells["latinTerm"] or prior_english != cells["ukEnglish"]:
            raise SystemExit(f"T04 coverage observation differs from opened TA2 row for {identifier}")
        if crosswalk_terms[identifier].get("la", {}).get("sourceTextObserved") != cells["latinTerm"]:
            raise SystemExit(f"T04 Latin term record differs from opened TA2 row for {identifier}")
        if crosswalk_terms[identifier].get("en", {}).get("sourceTextObserved") != cells["ukEnglish"]:
            raise SystemExit(f"T04 English term record differs from opened TA2 row for {identifier}")

        locator["priorT04IndexObservation"] = {
            "edition": locator.get("edition"),
            "latinTextObservation": prior_latin,
            "englishTextObservation": prior_english,
            "state": "preserved_T04_official_search_index_observation; exact row and table cell text independently confirmed in directly opened official-hosted TA2 PDF text layer",
            "sourceCrosswalkFilePreserved": "atlas-data/catalog/source-crosswalk.json",
            "sourceCrosswalkSha256BeforeBuild": crosswalk_sha,
        }
        locator.update({
            "edition": FIPAT_EDITION,
            "part": "TA2 Part II, Chapter 4: Muscular system",
            "latinTextObservation": cells["latinTerm"],
            "englishTextObservation": cells["ukEnglish"],
            "observedTableCells": cells,
            "cellRoleStatus": "Chapter_4_column_roles_confirmed_from_opened_PDF_text_header; assigned_text_rows_read; visual_table_layout_not_inspected",
            "existingEvidenceMode": "T04_index_row_and_existing_en_la_strings_preserved; direct_official-hosted_PDF_text_cells_confirmed; crosswalk_file_unmodified",
        })

        english = cells["ukEnglish"]
        field_rows = []
        label = spec["label"]
        korean = spec["korean"]
        field_rows.append(record(identifier, "label", label["value"], label["state"], [label["source"]], label["locator"], source_value=label.get("sourceValue")))
        korean_sources = korean.get("sources", [korean.get("source")])
        field_rows.append(record(
            identifier, "korean", korean["value"], korean["state"], korean_sources, korean["locator"],
            source_value=korean.get("sourceValue"), missing_reason=korean.get("missingReason"),
        ))
        field_rows.append(record(
            identifier, "hanja", None, "missing_no_attested_part_specific_hanja", spec["hanjaSources"],
            spec["hanjaMissingReason"], missing_reason=spec["hanjaMissingReason"],
        ))
        field_rows.append(record(
            identifier, "english", english, "TA2_opened_original_PDF_UK_English_cell", [FIPAT],
            fipat_locator(identifier, "UK English", english), source_value=english,
        ))
        field_rows.append(record(
            identifier, "aliases[0]", cells["latinTerm"], "TA2_opened_original_PDF_Latin_term_cell", [FIPAT],
            fipat_locator(identifier, "Latin term", cells["latinTerm"]), source_value=cells["latinTerm"],
        ))
        aliases = [cells["latinTerm"]]
        alias_index = 1
        for cell_key in ("latinSynonym", "englishSynonym", "other"):
            cell_value = cells[cell_key]
            if not cell_value:
                continue
            cell_name = {
                "latinSynonym": "Latin synonym",
                "englishSynonym": "English synonym",
                "other": "Other",
            }[cell_key]
            parts = [part.strip() for part in cell_value.split(";") if part.strip()]
            for value in parts:
                state = f"TA2_opened_original_PDF_{cell_key}_cell"
                field_rows.append(record(
                    identifier, f"aliases[{alias_index}]", value, state, [FIPAT],
                    fipat_locator(identifier, cell_name, value), source_value=cell_value,
                ))
                aliases.append(value)
                alias_index += 1
        for alias in spec["koreanAliases"]:
            field_rows.append(record(
                identifier, f"aliases[{alias_index}]", alias["value"], alias["state"], [alias["source"]],
                alias["locator"], source_value=alias["value"],
            ))
            aliases.append(alias["value"])
            alias_index += 1

        all_field_evidence.extend(field_rows)
        source_ids = sorted({
            FIPAT,
            label["source"],
            *korean_sources,
            *spec["hanjaSources"],
            *(alias["source"] for alias in spec["koreanAliases"]),
        })
        overlay = {
            "id": identifier,
            "label": label["value"],
            "korean": korean["value"],
            "english": english,
            "hanja": None,
            "aliases": aliases,
            "sourceIds": source_ids,
            "parentId": concept.get("parentId"),
            "entityType": concept["entityType"],
            "lookupOnly": False,
            "status": "web_attested_with_gaps",
            "humanReviewed": False,
            "hanjaNote": spec["hanjaMissingReason"],
        }
        if korean.get("missingReason"):
            overlay["koreanNote"] = korean["missingReason"]
        if identifier == "HA-P-000016":
            overlay["koreanNote"] = korean["missingReason"]
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
            "unadoptedCandidates": spec["unadoptedCandidates"],
            "webVerificationStatus": "web_checked_with_gaps",
            "humanAnatomyReviewStatus": "not_performed",
            "humanReviewer": None,
            "humanReviewed": False,
            "fieldEvidenceCount": len(field_rows),
        }
        new_entries.append(new_entry)
        cov["status"] = "web_checked_with_gaps"
        cov["statusReason"] = (
            "Exact assigned TA2 2.07 Part II row/cells were read in the official Dalhousie-hosted PDF text layer. "
            "Korean fields use only the indexed or directly opened KMLE source cells identified in per-field evidence; "
            "P16 full Korean and all seven part-specific Hanja values remain unverified. "
            "A conflicting old lateral-triceps-to-long-head search result was explicitly withheld. "
            "No human anatomy review or visual PDF table audit was performed."
        )

    for source_id, source in SOURCES.items():
        if source_id in names["sources"] or source_id in ledger["sources"]:
            raise SystemExit(f"Unexpected existing source key {source_id}; refusing overwrite")
        names["sources"][source_id] = source
        ledger["sources"][source_id] = source
    names["entries"].extend(overlays)
    ledger["entries"].extend(new_entries)
    ledger["fieldEvidence"].extend(all_field_evidence)
    names["revision"] = "T11-B09-web-checked-2026-09-25"
    names["accessedAt"] = CHECKED
    ledger["revision"] = "T11-B09-web-checked-2026-09-25"
    ledger["checkedDate"] = CHECKED
    ledger["overallT11Status"] = "in_progress_partial"
    batch["status"] = "complete_with_gaps"
    ledger["notes"].append(
        "T11-B09 complete with gaps: seven fixed existing part IDs; 35 required core field records plus "
        f"{len(all_field_evidence) - 35} individually evidenced aliases, {len(all_field_evidence)} B09 records total. "
        "TA2 2.07 Part II exact text rows and Chapter 4 column header were directly checked in the official Dalhousie-hosted PDF text layer; no rendered-page audit. "
        "KMLE source editions/revisions remain unexposed. P16 full Korean, all seven part-specific Hanja values, and the conflicting legacy triceps lateral-head mapping remain unresolved/withheld. "
        "No human anatomy review. B09 is the final T11 batch; T12 remains not started."
    )
    write_json(NAMES_PATH, names)
    write_json(BATCH_PATH, ledger)
    print(json.dumps({
        "batchId": "T11-B09",
        "canonicalIds": IDS,
        "requiredCoreFieldEvidence": 35,
        "additionalAliasEvidence": len(all_field_evidence) - 35,
        "batchFieldEvidence": len(all_field_evidence),
        "cumulativeFieldEvidence": len(ledger["fieldEvidence"]),
        "learnerOverlaysTotal": len(names["entries"]),
        "newOverlays": len(overlays),
        "koreanMissing": [identifier for identifier in IDS if FIELDS[identifier]["korean"]["value"] is None],
        "hanjaMissing": IDS,
        "humanReviewed": False,
        "nextTaskStarted": False,
        "sourceCrosswalkSha256": crosswalk_sha,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
