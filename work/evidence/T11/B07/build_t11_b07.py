"""Build only T11-B07 term provenance and the existing-ID learner overlay."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
CHECKED = "2026-09-25"
IDS = [*(f"HA-M-{n:06d}" for n in range(42, 49)), *(f"HA-P-{n:06d}" for n in range(1, 4))]
FIPAT = "fipat-ta2-b07-opened-original-pdf"
FIPAT_URL = "https://cdn.dal.ca/content/dam/dalhousie/pdf/library/FIPAT/TA2/FIPAT-TA2-Part-2.pdf"
FIPAT_EDITION = "Terminologia Anatomica, Second Edition (2.07), TA2 Part II; bibliographic citation 2019; approved and adopted by the IFAA General Assembly in 2020."
KMLE_EDITION = "KMLE web aggregation; exact underlying Korean terminology source edition/revision is not exposed."
NAMES_PATH = ROOT / "atlas-data/terminology/learning-names.json"
BATCH_PATH = ROOT / "atlas-data/terminology/term-review-batches.json"

SOURCES = {
    FIPAT: {
        "title": "FIPAT Terminologia Anatomica, Second Edition (2.07), Part II — directly opened official Dalhousie-hosted PDF",
        "url": FIPAT_URL,
        "locator": "Front matter PDF text P0, lines 0–19: Second Edition (2.07), 2019 citation, 2020 IFAA approval/adoption; Chapter 4 table header PDF text P52 / printed p.73, lines 3494–3495: Latin term, Latin synonym, UK English, US English, English synonym, Other. Assigned rows: PDF text P56 / printed p.77 row 2106; P73 / printed p.94 rows 2604–2608; P75 / printed p.96 rows 2658–2659, 2673, 2676. Text layer directly opened; visual page layout not inspected.",
        "edition": FIPAT_EDITION,
        "accessDate": CHECKED,
        "verificationMode": "official_Dalhousie_hosted_original_PDF_directly_opened; front_matter_Ch4_header_and_assigned_text_rows_read; no_visual_page_screenshot",
        "scope": "Term strings and table column roles only; no anatomical identity or human anatomy approval.",
    },
    "kmle-b07-piriformis": {
        "title": "KMLE piriformis name, Hanja and English synonym search result",
        "url": "https://m.kmle.co.kr/search.php?Search=piriformis",
        "locator": "Search-index excerpt: current 대한해부학회 Piriformis m. → 궁둥구멍근 [옛 용어] 이상근; old 대한의협 exact musculus piriformis term → 좌골구멍근, 이상근(梨狀筋); CancerWEB lists piriform muscle and musculus pyriformis synonyms and displays 05 Mar 2000. Direct page open returned an internal error; exact source dictionary edition/revision is not exposed.",
        "edition": "KMLE aggregation; exact Korean dictionary edition/revision is not exposed. CancerWEB result displays 05 Mar 2000.",
        "accessDate": CHECKED,
        "verificationMode": "KMLE_search_index_excerpt_only; direct_HTML_open_returned_internal_error; underlying_Korean_dictionary_edition_unexposed",
        "scope": "Name spellings only; no anatomical description imported.",
    },
    "kmle-b07-obturator-internus": {
        "title": "KMLE obturator internus Korean term search result",
        "url": "https://m.kmle.co.kr/search.php?Search=obturator+internus+m",
        "locator": "Search-index excerpt for 'obturator internus m.': current Korean 속폐쇄근 and old customary Korean 내폐쇄근; the result does not show an exact Hanja string. Direct page open returned an internal error; source edition/revision is not exposed.",
        "edition": KMLE_EDITION,
        "accessDate": CHECKED,
        "verificationMode": "KMLE_search_index_excerpt_only; direct_HTML_open_returned_internal_error; underlying_dictionary_edition_unexposed",
        "scope": "Name spellings only; Hanja intentionally left missing.",
    },
    "kmle-b07-gemellus": {
        "title": "KMLE superior/inferior gemellus terms and Hanja page",
        "url": "https://m.kmle.co.kr/search.php?Search=gemellus",
        "locator": "Opened KMLE aggregate HTML: lines 49–67 show old musculus gemellus inferior/superior term rows with 하쌍자근(下雙子筋)/상쌍자근(上雙子筋); lines 69–75 show musculus gemellus tuberalis; lines 90–98 show current 대한해부학회 아래쌍동이근/위쌍동이근 and old Korean forms. CancerWEB entry dates are displayed as 05 Mar 2000. Exact underlying dictionary edition/revision is not exposed.",
        "edition": "KMLE aggregate HTML; exact Korean dictionary edition/revision is not exposed. CancerWEB entries display 05 Mar 2000.",
        "accessDate": CHECKED,
        "verificationMode": "KMLE_aggregate_HTML_directly_opened; legacy_and_current_term_sections_visible; CancerWEB_display_date_visible; underlying_dictionary_edition_unexposed",
        "scope": "Name strings only; no anatomy description imported.",
    },
    "kmle-b07-quadratus-femoris": {
        "title": "KMLE quadratus femoris term and Hanja search result",
        "url": "https://m.kmle.co.kr/search.php?Search=quadratus+femoris",
        "locator": "Search-index excerpt: current 대한해부학회 Quadratus femoris m. → 넙다리네모근 [옛 용어] 대퇴방형근; old musculus quadratus femoris result shows 대퇴방형근(大槌方形筋), retained as a suspect candidate because the exact characters may be corrupted; the result also lists 'quadrate muscle of thigh'. Direct open returned an internal error; exact edition/revision is not exposed.",
        "edition": KMLE_EDITION,
        "accessDate": CHECKED,
        "verificationMode": "KMLE_search_index_excerpt_only; direct_HTML_open_returned_internal_error; suspect_Hanja_not_adopted; underlying_dictionary_edition_unexposed",
        "scope": "Name strings and a synonym only; no anatomical interpretation.",
    },
    "kmle-b07-flexor-korean": {
        "title": "KMLE flexor hallucis brevis Korean name search result",
        "url": "https://m.kmle.co.kr/search.php?Search=FLEX",
        "locator": "Search-index excerpt under 대한해부학회: Flexor hallucis brevis m. → 짧은엄지굽힘근 [옛 용어] 단무지굴근. Exact source dictionary edition/revision is not exposed; the original dictionary was not opened.",
        "edition": KMLE_EDITION,
        "accessDate": CHECKED,
        "verificationMode": "KMLE_search_index_excerpt_only; underlying_dictionary_edition_unexposed",
        "scope": "Name spellings only.",
    },
    "kmle-b07-flexor-hanja": {
        "title": "KMLE flexor hallucis brevis Hanja candidate search result",
        "url": "https://m.kmle.co.kr/search.php?Search=musculus+flexor+longus+hallucis",
        "locator": "Search-index excerpt for the exact musculus flexor hallucis brevis row shows two different strings: 短足拇趾屈筋 and 短母指屈筋. The same result displays the CancerWEB entry with short flexor muscle of great toe as a synonym and date 05 Mar 2000. The Hanja candidates are preserved, not adopted. Exact underlying Korean dictionary edition/revision is not exposed.",
        "edition": "KMLE web aggregation; exact underlying Korean dictionary edition/revision is not exposed. CancerWEB entry displays 05 Mar 2000.",
        "accessDate": CHECKED,
        "verificationMode": "KMLE_search_index_excerpt_only; competing_exact_row_Hanja_strings_kept_unadopted; underlying_dictionary_edition_unexposed",
        "scope": "Hanja candidates only; no source-preference decision or human review.",
    },
    "kmle-b07-adductor-hallucis": {
        "title": "KMLE adductor hallucis current/legacy terms and CancerWEB synonym page",
        "url": "https://m.kmle.co.kr/search.php?Search=musculus+adductor+hallucis",
        "locator": "Opened KMLE aggregate HTML: lines 170–176 exact old musculus adductor hallucis entries; lines 250–253 current 대한해부학회 엄지모음근 and old 무지내전근; line 172 pairs 무지내전근 with 拇趾內轉筋 and separately lists 모지내전근(母趾內轉筋); CancerWEB lines 446–448 lists adductor muscle of great toe and date 05 Mar 2000. Exact underlying Korean dictionary edition/revision is not exposed.",
        "edition": "KMLE aggregate HTML; exact Korean dictionary edition/revision is not exposed. CancerWEB entry displays 05 Mar 2000.",
        "accessDate": CHECKED,
        "verificationMode": "KMLE_aggregate_HTML_directly_opened; exact_legacy_and_current_sections_and_CancerWEB_synonym_visible; underlying_dictionary_edition_unexposed",
        "scope": "Name spellings and explicit English synonym only; no anatomy description imported.",
    },
    "journal-b07-gastrocnemius-heads": {
        "title": "Lee, Noh, Kim, Intramuscular Baker's Cyst in Plantaris: A Case Report",
        "url": "https://synapse.koreamed.org/upload/synapsedata/pdfdata/0164jkbjts/jkbjts-18-28.pdf",
        "locator": "Directly opened Koreamed-hosted PDF. PDF text page P0 lines 5–7 contains '비복근의 내측 두 (medial head)'; lines 10–13 and 28–36 contain '비복근의 외측두' paired with lateral head. Article header at lines 19–23: J Korean Bone Joint Tumor Soc 2012;18(1):28–31, DOI 10.5292/jkbjts.2012.18.1.28. Term-string observation only.",
        "edition": "Journal article: J Korean Bone Joint Tumor Soc. 2012;18(1):28–31; DOI 10.5292/jkbjts.2012.18.1.28.",
        "accessDate": CHECKED,
        "verificationMode": "Koreamed_hosted_original_article_PDF_directly_opened_text_layer; exact_Korean_and_English_head_phrases_read; no_anatomical_review",
        "scope": "Korean phrase used as learner display label only; article content not ingested.",
    },
    "kmle-b07-masseter-part": {
        "title": "KMLE superficial part of masseter Korean term search result",
        "url": "https://m.kmle.co.kr/search.php?Search=deep+part+of+masseter+muscle",
        "locator": "Search-index excerpt maps 'superficial part of masseter muscle' to '근의 얕은 부분, 교근의 천부'. Direct page open returned an internal error; exact source dictionary edition/revision is not exposed. A parent-muscle Hanja is not treated as evidence for this part.",
        "edition": KMLE_EDITION,
        "accessDate": CHECKED,
        "verificationMode": "KMLE_search_index_excerpt_only; direct_HTML_open_returned_internal_error; underlying_dictionary_edition_unexposed",
        "scope": "Part name string only; parent-only terms are not inherited.",
    },
}

ROWS = {
    "HA-M-000042": {"row": 2604, "page": 94, "pdf": "P73", "cells": {"latinTerm": "Musculus piriformis", "latinSynonym": None, "ukEnglish": "Piriformis muscle", "usEnglish": "Piriformis muscle", "englishSynonym": None, "other": None}},
    "HA-M-000043": {"row": 2605, "page": 94, "pdf": "P73", "cells": {"latinTerm": "Obturator internus", "latinSynonym": "Musculus obturatorius internus", "ukEnglish": "Obturator internus", "usEnglish": "Obturator internus", "englishSynonym": "Obturator internus muscle", "other": None}},
    "HA-M-000044": {"row": 2606, "page": 94, "pdf": "P73", "cells": {"latinTerm": "Musculus gemellus superior", "latinSynonym": None, "ukEnglish": "Superior gemellus muscle", "usEnglish": "Superior gemellus muscle", "englishSynonym": "Gemellus superior muscle", "other": "Musculus gemellus spinalis"}},
    "HA-M-000045": {"row": 2607, "page": 94, "pdf": "P73", "cells": {"latinTerm": "Musculus gemellus inferior", "latinSynonym": None, "ukEnglish": "Inferior gemellus muscle", "usEnglish": "Inferior gemellus muscle", "englishSynonym": "Gemellus inferior muscle", "other": "Musculus gemellus tuberalis"}},
    "HA-M-000046": {"row": 2608, "page": 94, "pdf": "P73", "cells": {"latinTerm": "Musculus quadratus femoris", "latinSynonym": None, "ukEnglish": "Quadratus femoris muscle", "usEnglish": "Quadratus femoris muscle", "englishSynonym": None, "other": None}},
    "HA-M-000047": {"row": 2673, "page": 96, "pdf": "P75", "cells": {"latinTerm": "Flexor brevis hallucis", "latinSynonym": "Musculus flexor hallucis brevis", "ukEnglish": "Flexor hallucis brevis", "usEnglish": "Flexor hallucis brevis", "englishSynonym": "Flexor hallucis brevis muscle", "other": None}},
    "HA-M-000048": {"row": 2676, "page": 96, "pdf": "P75", "cells": {"latinTerm": "Adductor hallucis", "latinSynonym": "Musculus adductor hallucis", "ukEnglish": "Adductor hallucis", "usEnglish": "Adductor hallucis", "englishSynonym": "Adductor hallucis muscle", "other": None}},
    "HA-P-000001": {"row": 2658, "page": 96, "pdf": "P75", "cells": {"latinTerm": "Caput laterale musculi gastrocnemii", "latinSynonym": None, "ukEnglish": "Lateral head of gastrocnemius", "usEnglish": "Lateral head of gastrocnemius", "englishSynonym": None, "other": "Caput fibulare musculi gastrocnemii"}},
    "HA-P-000002": {"row": 2659, "page": 96, "pdf": "P75", "cells": {"latinTerm": "Caput mediale musculi gastrocnemii", "latinSynonym": None, "ukEnglish": "Medial head of gastrocnemius", "usEnglish": "Medial head of gastrocnemius", "englishSynonym": None, "other": "Caput tibiale musculi gastrocnemii"}},
    "HA-P-000003": {"row": 2106, "page": 77, "pdf": "P56", "cells": {"latinTerm": "Pars superficialis masseteris", "latinSynonym": None, "ukEnglish": "Superficial part of masseter", "usEnglish": "Superficial part of masseter", "englishSynonym": None, "other": None}},
}

FIELDS = {
    "HA-M-000042": {
        "label": {"value": "이상근", "state": "attested_customary_name", "source": "kmle-b07-piriformis", "locator": "KMLE piriformis search-index excerpt: old 대한의협 term 'musculus piriformis' → '좌골구멍근, 이상근(梨狀筋)'."},
        "korean": {"value": "궁둥구멍근", "state": "attested_current_korean_name", "source": "kmle-b07-piriformis", "locator": "KMLE search-index excerpt, 대한해부학회 Piriformis m. row: '궁둥구멍근' [옛 용어] '이상근'."},
        "hanja": {"value": "梨狀筋", "state": "attested_source_hanja", "source": "kmle-b07-piriformis", "locator": "KMLE search-index excerpt, exact old musculus piriformis term row: '이상근(梨狀筋)'. The source's printed compatibility character is retained exactly."},
        "labelSourceValue": "이상근", "koreanSourceValue": "궁둥구멍근", "hanjaSourceValue": "梨狀筋",
        "extras": [
            {"value": "piriform muscle", "source": "kmle-b07-piriformis", "state": "CancerWEB_explicit_English_synonym", "locator": "KMLE CancerWEB piriformis search-result entry dated 05 Mar 2000 lists 'piriform muscle' as a synonym."},
            {"value": "musculus pyriformis", "source": "kmle-b07-piriformis", "state": "CancerWEB_explicit_Latin_synonym", "locator": "KMLE CancerWEB piriformis search-result entry dated 05 Mar 2000 lists 'musculus pyriformis' as a synonym."},
        ],
        "unadopted": [],
    },
    "HA-M-000043": {
        "label": {"value": "내폐쇄근", "state": "attested_customary_name", "source": "kmle-b07-obturator-internus", "locator": "KMLE search-index result for 'obturator internus m.': old customary term 내폐쇄근."},
        "korean": {"value": "속폐쇄근", "state": "attested_current_korean_name", "source": "kmle-b07-obturator-internus", "locator": "KMLE search-index result for 'obturator internus m.': current Korean term 속폐쇄근."},
        "hanja": {"value": None, "state": "missing_no_exact_source_hanja", "source": "kmle-b07-obturator-internus", "locator": "The accessed KMLE search result has Korean forms only and exposes no Hanja for this exact term."},
        "hanjaMissingReason": "Accessible KMLE result shows 속폐쇄근 and 내폐쇄근 but no Hanja tied to the exact obturator internus entry; do not generate 內閉鎖筋 from the spelling.",
        "labelSourceValue": "내폐쇄근", "koreanSourceValue": "속폐쇄근",
        "extras": [
            {"value": "Musculus obturatorius internus", "source": FIPAT, "state": "TA2_Latin_synonym_cell", "cell": "latinSynonym"},
            {"value": "Obturator internus muscle", "source": FIPAT, "state": "TA2_English_synonym_cell", "cell": "englishSynonym"},
        ],
        "unadopted": [],
    },
    "HA-M-000044": {
        "label": {"value": "상쌍자근", "state": "attested_customary_name", "source": "kmle-b07-gemellus", "locator": "Opened KMLE HTML lines 61–67: exact musculus gemellus superior row '위쌍둥이근, 상쌍자근(上雙子筋)'."},
        "korean": {"value": "위쌍동이근", "state": "attested_current_korean_name", "source": "kmle-b07-gemellus", "locator": "Opened KMLE HTML lines 95–98: 대한해부학회 Superior gemellus m. → 위쌍동이근 [옛 용어] 상쌍자근."},
        "hanja": {"value": "上雙子筋", "state": "attested_source_hanja", "source": "kmle-b07-gemellus", "locator": "Opened KMLE HTML lines 61–67: exact musculus gemellus superior row pairs 상쌍자근 with 上雙子筋."},
        "labelSourceValue": "상쌍자근", "koreanSourceValue": "위쌍동이근", "hanjaSourceValue": "上雙子筋",
        "extras": [
            {"value": "Gemellus superior muscle", "source": FIPAT, "state": "TA2_English_synonym_cell", "cell": "englishSynonym"},
            {"value": "Musculus gemellus spinalis", "source": FIPAT, "state": "TA2_Other_cell_Latin_synonym", "cell": "other"},
        ],
        "unadopted": [],
    },
    "HA-M-000045": {
        "label": {"value": "하쌍자근", "state": "attested_customary_name", "source": "kmle-b07-gemellus", "locator": "Opened KMLE HTML lines 49–55: exact musculus gemellus inferior row '아래쌍둥이근, 하쌍자근(下雙子筋)'."},
        "korean": {"value": "아래쌍동이근", "state": "attested_current_korean_name", "source": "kmle-b07-gemellus", "locator": "Opened KMLE HTML lines 90–94: 대한해부학회 Inferior gemellus m. → 아래쌍동이근 [옛 용어] 하쌍자근."},
        "hanja": {"value": "下雙子筋", "state": "attested_source_hanja", "source": "kmle-b07-gemellus", "locator": "Opened KMLE HTML lines 49–55: exact musculus gemellus inferior row pairs 하쌍자근 with 下雙子筋."},
        "labelSourceValue": "하쌍자근", "koreanSourceValue": "아래쌍동이근", "hanjaSourceValue": "下雙子筋",
        "extras": [
            {"value": "Gemellus inferior muscle", "source": FIPAT, "state": "TA2_English_synonym_cell", "cell": "englishSynonym"},
            {"value": "Musculus gemellus tuberalis", "source": FIPAT, "state": "TA2_Other_cell_Latin_synonym", "cell": "other"},
        ],
        "unadopted": [],
    },
    "HA-M-000046": {
        "label": {"value": "대퇴방형근", "state": "attested_customary_name", "source": "kmle-b07-quadratus-femoris", "locator": "KMLE search-index excerpt: 대한해부학회 Quadratus femoris m. → 넙다리네모근 [옛 용어] 대퇴방형근."},
        "korean": {"value": "넙다리네모근", "state": "attested_current_korean_name", "source": "kmle-b07-quadratus-femoris", "locator": "KMLE search-index excerpt, 대한해부학회 Quadratus femoris m. row: 넙다리네모근."},
        "hanja": {"value": None, "state": "held_suspect_source_hanja", "source": "kmle-b07-quadratus-femoris", "locator": "An old KMLE search result prints 大槌方形筋 on a musculus quadratus femoris row, while another exact row gives the Korean form without Hanja; the suspicious string is kept unadopted."},
        "hanjaMissingReason": "The only exact-row Hanja surfaced in the accessible result is 大槌方形筋, which may contain source/OCR character damage; no independent exact primary locator establishes a safe form, so Hanja remains null.",
        "labelSourceValue": "대퇴방형근", "koreanSourceValue": "넙다리네모근",
        "extras": [{"value": "quadrate muscle of thigh", "source": "kmle-b07-quadratus-femoris", "state": "KMLE_explicit_English_synonym", "locator": "KMLE search-index excerpt, legacy row headed 'quadrate muscle of thigh ; muscle quadratus femoris' lists 대퇴사각근, 대퇴방형근."}],
        "unadopted": [{"field": "hanja", "value": "大槌方形筋", "state": "suspect_source_character_form_not_adopted", "source": "kmle-b07-quadratus-femoris", "reason": "The search result displays this form, but its character is suspicious and no independent exact source locator confirms it; do not normalize or index it."}],
    },
    "HA-M-000047": {
        "label": {"value": "단무지굴근", "state": "attested_customary_name", "source": "kmle-b07-flexor-korean", "locator": "KMLE FLEX search-index excerpt, 대한해부학회 Flexor hallucis brevis m. row: 짧은엄지굽힘근 [옛 용어] 단무지굴근."},
        "korean": {"value": "짧은엄지굽힘근", "state": "attested_current_korean_name", "source": "kmle-b07-flexor-korean", "locator": "KMLE FLEX search-index excerpt, 대한해부학회 Flexor hallucis brevis m. row: 짧은엄지굽힘근."},
        "hanja": {"value": None, "state": "held_conflicting_source_hanja", "source": "kmle-b07-flexor-hanja", "locator": "Search-index excerpt for the exact musculus flexor hallucis brevis row yields both 短母指屈筋 and 短足拇趾屈筋; neither is promoted to the learner Hanja field."},
        "hanjaMissingReason": "The accessible exact term row exposes two different Hanja strings, 短母指屈筋 and 短足拇趾屈筋. No exact edition or independent primary locator resolves the preferred form, so Hanja remains null.",
        "labelSourceValue": "단무지굴근", "koreanSourceValue": "짧은엄지굽힘근",
        "extras": [
            {"value": "Musculus flexor hallucis brevis", "source": FIPAT, "state": "TA2_Latin_synonym_cell", "cell": "latinSynonym"},
            {"value": "Flexor hallucis brevis muscle", "source": FIPAT, "state": "TA2_English_synonym_cell", "cell": "englishSynonym"},
            {"value": "short flexor muscle of great toe", "source": "kmle-b07-flexor-hanja", "state": "CancerWEB_explicit_English_synonym", "locator": "KMLE search-index excerpt for CancerWEB musculus flexor hallucis brevis entry, dated 05 Mar 2000, lists short flexor muscle of great toe."},
        ],
        "unadopted": [
            {"field": "hanja", "value": "短母指屈筋", "state": "conflicting_exact_row_Hanja_candidate_not_adopted", "source": "kmle-b07-flexor-hanja", "reason": "This string appears on the exact term row, but another distinct Hanja spelling appears for the same term; do not select by inference."},
            {"field": "hanja", "value": "短足拇趾屈筋", "state": "conflicting_exact_row_Hanja_candidate_not_adopted", "source": "kmle-b07-flexor-hanja", "reason": "This distinct string appears on the exact term row alongside 短母指屈筋; preferred source form is unresolved."},
        ],
    },
    "HA-M-000048": {
        "label": {"value": "무지내전근", "state": "attested_customary_name", "source": "kmle-b07-adductor-hallucis", "locator": "Opened KMLE HTML lines 170–172: exact musculus adductor hallucis row includes 무지내전근(拇趾內轉筋)."},
        "korean": {"value": "엄지모음근", "state": "attested_current_korean_name", "source": "kmle-b07-adductor-hallucis", "locator": "Opened KMLE HTML lines 250–253: 대한해부학회 Adductor hallucis m. → 엄지모음근 [옛 용어] 무지내전근."},
        "hanja": {"value": "拇趾內轉筋", "state": "attested_source_hanja", "source": "kmle-b07-adductor-hallucis", "locator": "Opened KMLE HTML lines 170–172: exact musculus adductor hallucis row pairs 무지내전근 with 拇趾內轉筋; a separate string 母趾內轉筋 is paired with 모지내전근."},
        "labelSourceValue": "무지내전근", "koreanSourceValue": "엄지모음근", "hanjaSourceValue": "拇趾內轉筋",
        "extras": [
            {"value": "Musculus adductor hallucis", "source": FIPAT, "state": "TA2_Latin_synonym_cell", "cell": "latinSynonym"},
            {"value": "Adductor hallucis muscle", "source": FIPAT, "state": "TA2_English_synonym_cell", "cell": "englishSynonym"},
            {"value": "adductor muscle of great toe", "source": "kmle-b07-adductor-hallucis", "state": "CancerWEB_explicit_English_synonym", "locator": "Opened KMLE HTML lines 446–448; CancerWEB musculus adductor hallucis entry lists adductor muscle of great toe and displays 05 Mar 2000."},
        ],
        "unadopted": [{"field": "hanja", "value": "母趾內轉筋", "state": "alternate_legacy_Hanja_spelling_not_adopted_as_primary", "source": "kmle-b07-adductor-hallucis", "reason": "The same exact term row associates this string with the distinct Korean form 모지내전근. It is preserved separately and not merged into the primary Hanja field."}],
    },
    "HA-P-000001": {
        "label": {"value": "비복근 · 외측두", "state": "preexisting_display_label_supported_by_source_phrase", "source": "journal-b07-gastrocnemius-heads", "sourceValue": "비복근의 외측두", "locator": "Opened PDF P0 lines 10–13: '비복근의 외측두' paired with lateral head; lines 28–36 repeat the phrase. The pre-existing overlay label is retained verbatim."},
        "korean": {"value": None, "state": "missing_no_source_attested_pure_Korean_head_name", "source": "journal-b07-gastrocnemius-heads", "locator": "The opened article uses the Sino-Korean phrase 비복근의 외측두; no source-attested pure Korean part-specific term was found in this review."},
        "hanja": {"value": None, "state": "missing_no_head_specific_source_hanja", "source": "journal-b07-gastrocnemius-heads", "locator": "The opened article contains no head-specific Hanja spelling; parent-muscle Hanja is not inherited."},
        "koreanMissingReason": "Accessible source uses 비복근의 외측두; no exact source-attested pure Korean head name was found. Do not construct a translation.",
        "preexistingKoreanCandidate": "장딴지근 · 가쪽갈래",
        "hanjaMissingReason": "The article does not print a head-specific Hanja name; do not derive one from the parent gastrocnemius.",
        "extras": [{"value": "Caput fibulare musculi gastrocnemii", "source": FIPAT, "state": "TA2_Other_cell_Latin_alternative", "cell": "other"}],
        "unadopted": [],
    },
    "HA-P-000002": {
        "label": {"value": "비복근 · 내측두", "state": "preexisting_display_label_supported_by_source_phrase", "source": "journal-b07-gastrocnemius-heads", "sourceValue": "비복근의 내측 두", "locator": "Opened PDF P0 lines 5–7: exact phrase '비복근의 내측 두' paired with '(medial head)'. The pre-existing overlay label is retained verbatim."},
        "korean": {"value": None, "state": "missing_no_source_attested_pure_Korean_head_name", "source": "journal-b07-gastrocnemius-heads", "locator": "The opened article uses the Sino-Korean phrase 비복근의 내측 두; no source-attested pure Korean part-specific term was found in this review."},
        "hanja": {"value": None, "state": "missing_no_head_specific_source_hanja", "source": "journal-b07-gastrocnemius-heads", "locator": "The opened article contains no head-specific Hanja spelling; parent-muscle Hanja is not inherited."},
        "koreanMissingReason": "Accessible source uses 비복근의 내측 두; no exact source-attested pure Korean head name was found. Do not construct a translation.",
        "preexistingKoreanCandidate": "장딴지근 · 안쪽갈래",
        "hanjaMissingReason": "The article does not print a head-specific Hanja name; do not derive one from the parent gastrocnemius.",
        "extras": [{"value": "Caput tibiale musculi gastrocnemii", "source": FIPAT, "state": "TA2_Other_cell_Latin_alternative", "cell": "other"}],
        "unadopted": [],
    },
    "HA-P-000003": {
        "label": {"value": "교근의 천부", "state": "attested_Korean_part_name_search_index_excerpt", "source": "kmle-b07-masseter-part", "locator": "KMLE search-index excerpt for 'superficial part of masseter muscle' lists '근의 얕은 부분, 교근의 천부'."},
        "korean": {"value": None, "state": "missing_no_part_specific_pure_Korean_name", "source": "kmle-b07-masseter-part", "locator": "The excerpt has a part-specific Sino-Korean phrase only; it does not provide a current pure Korean part name. Parent name 깨물근 is not expanded into a part label."},
        "hanja": {"value": None, "state": "missing_no_part_specific_source_hanja", "source": "kmle-b07-masseter-part", "locator": "No Hanja string is provided for the part; parent muscle 咬筋 is not inherited."},
        "koreanMissingReason": "No source-attested pure Korean name for this exact part was found. The parent-muscle name is not expanded by construction.",
        "hanjaMissingReason": "No part-specific Hanja form was observed; the parent-muscle Hanja is not treated as evidence for the part.",
        "extras": [],
        "unadopted": [],
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
    coverage = [row for row in ledger["canonicalCoverage"] if row["batchId"] == "T11-B07"]
    if [row["id"] for row in coverage] != IDS:
        raise SystemExit("T11-B07 assignment changed; refusing to touch any other ID")
    if any(row["status"] != "not_started" for row in coverage):
        raise SystemExit("T11-B07 coverage is not untouched; refusing non-idempotent rebuild")
    if any(row["id"] in IDS for row in ledger["entries"]):
        raise SystemExit("B07 evidence entries already exist; refusing duplicates")
    existing_overlay_rows = [row for row in names["entries"] if row["id"] in IDS]
    allowed_existing_overlay_ids = {"HA-P-000001", "HA-P-000002"}
    if {row["id"] for row in existing_overlay_rows} - allowed_existing_overlay_ids:
        raise SystemExit("Unexpected pre-existing B07 overlay; refusing overwrite")
    existing_overlays = {row["id"]: row for row in existing_overlay_rows}

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

        locator["priorT04IndexObservation"] = {
            "edition": old_edition,
            "latinTextObservation": old_latin,
            "englishTextObservation": old_english,
            "state": "preserved_index_observation; B07 direct opened PDF cell mapping takes precedence for this overlay",
        }
        locator.update({
            "edition": FIPAT_EDITION,
            "part": "TA2 Part II, Chapter 4: Muscular system",
            "latinTextObservation": cells["latinTerm"],
            "englishTextObservation": cells["ukEnglish"],
            "observedTableCells": cells,
            "cellRoleStatus": "Chapter_4_column_roles_confirmed_from_opened_PDF_text_header; exact_assigned_text_rows_read; visual_table_layout_not_inspected",
            "existingEvidenceMode": "T04 indexed row retained as prior observation; B07 directly opened the official-hosted original PDF text and mapped the exact row cells; no visual page screenshot.",
        })
        if old_latin != cells["latinTerm"] or old_english != cells["ukEnglish"]:
            locator["T04SelectedCellMismatch"] = {
                "oldLatinObservation": old_latin,
                "oldEnglishObservation": old_english,
                "B07LatinTermCell": cells["latinTerm"],
                "B07UKEnglishCell": cells["ukEnglish"],
                "note": "T04 source-index crosswalk selected a synonym cell for this field; the original crosswalk file is preserved, and this B07 overlay records the opened TA2 preferred term cells plus all observed cells.",
            }

        label, korean, hanja = (spec["label"], spec["korean"], spec["hanja"])
        english = cells["ukEnglish"]
        field_rows = [
            record(identifier, "label", label["value"], label["state"], label["source"], label["locator"], source_value=spec.get("labelSourceValue", label.get("sourceValue"))),
            record(identifier, "korean", korean["value"], korean["state"], korean["source"], korean["locator"], source_value=spec.get("koreanSourceValue"), missing_reason=spec.get("koreanMissingReason")),
        ]
        field_rows.append(record(identifier, "hanja", hanja["value"], hanja["state"], hanja["source"], hanja["locator"], source_value=spec.get("hanjaSourceValue"), missing_reason=spec.get("hanjaMissingReason")))
        field_rows.append(record(identifier, "english", english, "TA2_opened_original_PDF_UK_English_cell", FIPAT, fipat_locator(identifier, "UK English", english), source_value=english))
        field_rows.append(record(identifier, "aliases[0]", cells["latinTerm"], "TA2_opened_original_PDF_Latin_term_cell", FIPAT, fipat_locator(identifier, "Latin term", cells["latinTerm"]), source_value=cells["latinTerm"]))

        alias_values = [cells["latinTerm"]]
        for index, extra in enumerate(spec["extras"], start=1):
            source_id = extra["source"]
            if source_id == FIPAT:
                cell = extra["cell"]
                cell_values = {"latinSynonym": "Latin synonym", "englishSynonym": "English synonym", "other": "Other"}
                value = cells[cell]
                if value != extra["value"]:
                    raise SystemExit(f"Alias cell mismatch {identifier} {cell}")
                field_locator = fipat_locator(identifier, cell_values[cell], value)
            else:
                field_locator = extra["locator"]
            field_rows.append(record(identifier, f"aliases[{index}]", extra["value"], extra["state"], source_id, field_locator, source_value=extra["value"]))
            alias_values.append(extra["value"])

        all_field_evidence.extend(field_rows)
        source_ids = {FIPAT, label["source"], korean["source"], hanja["source"], *(x["source"] for x in spec["extras"])}
        source_ids = {source_id for source_id in source_ids if source_id in SOURCES}
        previous_overlay = existing_overlays.get(identifier)
        if previous_overlay:
            source_ids.update(previous_overlay.get("sourceIds", []))
            alias_values = list(dict.fromkeys([*previous_overlay.get("aliases", []), *alias_values]))
        overlay = {
            **(previous_overlay or {}),
            "id": identifier,
            "label": label["value"],
            "korean": korean["value"],
            "english": english,
            "hanja": hanja["value"],
            "aliases": alias_values,
            "sourceIds": sorted(source_ids),
            "parentId": concept.get("parentId"),
            "entityType": concept["entityType"],
            "lookupOnly": False,
            "status": "web_attested_with_gaps",
            "humanReviewed": False,
            "hanjaNote": spec.get("hanjaMissingReason") or "Source spelling is recorded exactly; underlying KMLE terminology editions are not exposed. Human anatomy review not performed.",
        }
        if spec.get("koreanMissingReason"):
            overlay["koreanNote"] = spec["koreanMissingReason"]
        if previous_overlay:
            overlays.append((identifier, overlay))
        else:
            overlays.append((identifier, overlay))

        unadopted = []
        for candidate in spec["unadopted"]:
            unadopted.append({
                "field": candidate["field"],
                "value": candidate["value"],
                "state": candidate["state"],
                "evidence": [source_evidence(candidate["source"], SOURCES[candidate["source"]]["locator"])],
                "reason": candidate["reason"],
            })
        if spec.get("preexistingKoreanCandidate"):
            unadopted.append({
                "field": "korean",
                "value": spec["preexistingKoreanCandidate"],
                "state": "preexisting_unverified_part_translation_not_promoted_to_search_overlay",
                "evidence": [source_evidence("journal-b07-gastrocnemius-heads", spec["korean"]["locator"])],
                "reason": "This phrase existed in the learner overlay before B07. The reviewed source text uses 비복근의 외측두/내측 두 and does not attest the full pure-Korean head phrase; it is retained here for audit but removed from searchable current-name field pending a direct vocabulary source.",
            })
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
            "unadoptedCandidates": unadopted,
            "webVerificationStatus": "web_checked_with_gaps",
            "humanAnatomyReviewStatus": "not_performed",
            "humanReviewer": None,
            "humanReviewed": False,
            "fieldEvidenceCount": len(field_rows),
        }
        if previous_overlay:
            new_entry["preservedPreviousOverlay"] = previous_overlay
        new_entries.append(new_entry)
        cov["status"] = "web_checked_with_gaps"
        cov["statusReason"] = "The exact assigned TA2 text cells were checked in the directly opened official-hosted PDF text layer. Korean/Hanja name evidence comes from opened KMLE aggregate HTML, search-index excerpts, or a peer-reviewed article phrase as recorded per field. Conflicting or suspect Hanja and part-specific Korean gaps remain explicit. Visual PDF layout and human anatomy review were not performed."

    for source_id, source in SOURCES.items():
        names["sources"][source_id] = source
        ledger["sources"][source_id] = source
    for identifier, overlay in overlays:
        if identifier in existing_overlays:
            position = next(i for i, row in enumerate(names["entries"]) if row["id"] == identifier)
            names["entries"][position] = overlay
        else:
            names["entries"].append(overlay)
    ledger["entries"].extend(new_entries)
    ledger["fieldEvidence"].extend(all_field_evidence)
    names["revision"] = "T11-B07-web-checked-2026-09-25"
    names["accessedAt"] = CHECKED
    ledger["revision"] = "T11-B07-web-checked-2026-09-25"
    ledger["checkedDate"] = CHECKED
    ledger["overallT11Status"] = "in_progress_partial"
    for batch in ledger["batchOrder"]:
        if batch["batchId"] == "T11-B07":
            batch["status"] = "complete_with_gaps"
    ledger["notes"].append(
        "T11-B07 complete with gaps: 10 fixed existing IDs, 50 core field records and "
        f"{len(all_field_evidence) - 50} individually sourced extra-alias records; total B07 field evidence {len(all_field_evidence)}. "
        "TA2 2.07 Part II original PDF text header/rows were directly opened; no rendered table-page inspection. "
        "KMLE underlying Korean dictionary editions are unexposed; B07 Hanja conflicts and head/part term gaps remain explicit. "
        "Human anatomy review was not performed. T11 has nine batches B01–B09; B08/B09 and T12 remain not started."
    )
    write_json(NAMES_PATH, names)
    write_json(BATCH_PATH, ledger)
    print(json.dumps({
        "batchId": "T11-B07",
        "canonicalIds": IDS,
        "requiredCoreFieldEvidence": 50,
        "additionalAliasEvidence": len(all_field_evidence) - 50,
        "batchFieldEvidence": len(all_field_evidence),
        "cumulativeFieldEvidence": len(ledger["fieldEvidence"]),
        "learnerOverlaysTotal": len(names["entries"]),
        "newOverlays": sum(identifier not in existing_overlays for identifier, _overlay in overlays),
        "enrichedPreexistingOverlays": sum(identifier in existing_overlays for identifier, _overlay in overlays),
        "hanjaAttested": sum(item["hanja"]["value"] is not None for item in FIELDS.values()),
        "hanjaMissing": [identifier for identifier, item in FIELDS.items() if item["hanja"]["value"] is None],
        "koreanMissing": [identifier for identifier, item in FIELDS.items() if item["korean"]["value"] is None],
        "batchStatus": "complete_with_gaps",
        "humanReviewed": False,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
