#!/usr/bin/env python3
"""Record opened KMLE query results for the frozen T100 unnamed-target candidate set."""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from urllib.parse import quote_plus

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
INPUT = HERE / "remaining-target-query-candidates-frozen.json"
INPUT_SHA256 = "532d38c79c467c359c310fb1e8d0bfdca92daf1ae7a45ec0513f8db7f5e89e24"
OUTPUT = HERE / "remaining-target-kmle-observations.json"
EDITION = "KMLE shows a Korean Association of Anatomists terminology section but exposes no exact edition or revision. The individual underlying dictionary record was not opened."

# Exact Korean Association of Anatomists rows read from the opened aggregate
# result HTML. Values are kept in Hangul; no Hanja glyph is transcribed.
EXACT: dict[str, tuple[int, str, str, str | None, str]] = {
    "TA2:1092": (1, "Coccyx [First-fourth coccygeal vertebrae]", "꼬리뼈", "미골", "Coccyx [First-fourth coccygeal vertebrae] → 꼬리뼈 [첫째-넷째꼬리(척추)뼈] [미골]; [옛 용어] 미골"),
    "TA2:1129": (1, "Sternum", "복장뼈", "흉골", "Sternum → 복장뼈 [흉골]; [옛 용어] 흉골"),
    "TA2:1168": (1, "Clavicle", "빗장뼈", "쇄골", "Clavicle → 빗장뼈 [쇄골]; [옛 용어] 쇄골"),
    "TA2:1210": (1, "Radius", "노뼈", "요골", "Radius → 노뼈; [옛 용어] 요골"),
    "TA2:1230": (1, "Ulna", "자뼈", "척골", "Ulna → 자뼈 [척골]; [옛 용어] 척골"),
    "TA2:1250": (1, "Scaphoid bone", "손배뼈", "주상골", "Scaphoid bone → 손배뼈; [옛 용어] 주상골"),
    "TA2:1252": (1, "Lunate bone", "반달뼈", "월상골", "Lunate bone → 반달뼈; [옛 용어] 월상골"),
    "TA2:1254": (1, "Pisiform bone", "콩알뼈", "두상골", "Pisiform bone → 콩알뼈; [옛 용어] 두상골"),
    "TA2:1257": (1, "Trapezoid bone", "작은마름뼈", "소능형골", "Trapezoid bone → 작은마름뼈; [옛 용어] 소능형골"),
    "TA2:1258": (1, "Capitate bone", "알머리뼈", "유두골", "Capitate bone → 알머리뼈; [옛 용어] 유두골"),
    "TA2:1259": (1, "Hamate bone", "갈고리뼈", "유구골", "Hamate bone → 갈고리뼈; [옛 용어] 유구골"),
    "TA2:1269": (1, "Third metacarpal bone", "셋째손허리뼈", None, "Third metacarpal bone → 셋째손허리뼈; [옛 용어] 제1중수골 (conflicts with Third; observed but not applied)"),
    "TA2:1307": (1, "Hip bone", "볼기뼈", "관골", "Hip bone → 볼기뼈 [관골]; [옛 용어] 관골"),
    "TA2:1390": (1, "Patella", "무릎뼈", "슬개골", "Patella → 무릎뼈 [슬개골]; [옛 용어] 슬개골"),
    "TA2:1448": (1, "Talus", "목말뼈", "거골", "Talus → 목말뼈; [옛 용어] 거골"),
    "TA2:1487": (1, "Intermediate cuneiform bone", "중간쐐기뼈", "중간설상골", "Intermediate cuneiform bone → 중간쐐기뼈; [옛 용어] 중간설상골"),
    "TA2:1488": (1, "Lateral cuneiform bone", "가쪽쐐기뼈", "외측설상골", "Lateral cuneiform bone → 가쪽쐐기뼈; [옛 용어] 외측설상골"),
    "TA2:2051": (1, "Inferior oblique muscle", "아래빗근", "하사근", "Inferior oblique muscle → 아래빗근; [옛 용어] 하사근"),
    "TA2:2156": (2, "Sternocleidomastoid muscle", "목빗근", "흉쇄유돌근", "Sternocleidomastoid muscle → 목빗근; [옛 용어] 흉쇄유돌근. A separate partial row is not used."),
    "TA2:2161": (1, "Anterior belly of digastric muscle", "두힘살근앞힘살", "악이복근전복", "Anterior belly of digastric muscle → 두힘살근앞힘살; [옛 용어] 악이복근전복"),
    "TA2:2163": (1, "Posterior belly of digastric muscle", "두힘살근뒤힘살", "악이복근후복", "Posterior belly of digastric muscle → 두힘살근뒤힘살; [옛 용어] 악이복근후복"),
    "TA2:2164": (1, "Stylohyoid muscle", "붓목뿔근", "경돌설골근", "Stylohyoid muscle → 붓목뿔근; [옛 용어] 경돌설골근"),
    "TA2:2166": (1, "Geniohyoid muscle", "턱끝목뿔근", "이설골근", "Geniohyoid muscle → 턱끝목뿔근; [옛 용어] 이설골근"),
    "TA2:2192": (1, "Laryngeal muscles", "후두근육", "후두근", "Laryngeal muscles → 후두근육; [옛 용어] 후두근"),
    "TA2:2284": (4, "Rotatores m.", "돌림근", "회선근", "Rotatores m. → 돌림근; [옛 용어] 회선근. Other exact rows name regional subclasses and are not copied to this parent."),
    "TA2:2403": (2, "Levator ani muscle", "항문올림근", "항문거근", "Levator ani muscle → 항문올림근; [옛 용어] 항문거근. The other exact row is the abbreviated same headword."),
    "TA2:2405": (1, "Pubococcygeus muscle", "두덩꼬리근", "치골미골근", "Pubococcygeus muscle → 두덩꼬리근; [옛 용어] 치골미골근"),
    "TA2:2491": (1, "Flexor digitorum profundus m.", "깊은손가락굽힘근", "심지굴근", "Flexor digitorum profundus m. → 깊은손가락굽힘근; [옛 용어] 심지굴근"),
    "TA2:2630": (1, "Adductor magnus m.", "큰모음근", "대내전근", "Adductor magnus m. → 큰모음근; [옛 용어] 대내전근"),
    "TA2:744": (2, "Lacrimal bone", "눈물뼈", "누골", "Lacrimal bone → 눈물뼈; [옛 용어] 누골. A second entry duplicates the headword with a bracketed legacy label."),
    "TA2:751": (9, "Vomer", "보습뼈", "서골", "Vomer → 보습뼈 [서골]; [옛 용어] 서골. Other rows are vomeronasal derivatives and are not assigned to the bone."),
    "TA2:798": (2, "Palatine bone", "입천장뼈", "구개골", "Palatine bone → 입천장뼈; [옛 용어] 구개골. Duplicate bracketed legacy entry omitted."),
    "TA2:818": (2, "Zygomatic bone", "광대뼈", "관골", "Zygomatic bone → 광대뼈; [옛 용어] 관골. Duplicate bracketed alternative omitted."),
    "TA2:881": (2, "Malleus", "망치뼈", "추골", "Malleus → 망치뼈; [옛 용어] 추골. The separate most-part row is not used."),
    "TA2:888": (2, "Incus", "모루뼈", "침골", "Incus → 모루뼈; [옛 용어] 침골. The separate most-part row is not used."),
    "TA2:895": (2, "Stapes", "등자뼈", "등골", "Stapes → 등자뼈; [옛 용어] 등골. The separate partial row is not used."),
}

SPECIAL_NO_EXACT = {
    "TA2:1269": "The modern exact row was applied, but its legacy field says `제1중수골`, inconsistent with the third metacarpal target; retained only as a conflict.",
}

ALTERNATE = [
    {
        "targetId": "TA2:1179", "query": "Bones of free upper limb", "resultLayer": "exact",
        "resultCount": 1, "headword": "Bones of free upper limb", "koModern": "자유팔뼈", "koTraditional": "자유상지골",
        "locator": "Opened KMLE aggregate HTML; 대한해부학회 의학용어 사전 맞춤 검색 exact-result section; `Bones of free upper limb` → `자유팔뼈`; [옛 용어] `자유상지골`. This broader English headword is a semantic synonym for the frozen `bones of free part of upper limb` target; exact target phrase itself returned zero rows.",
        "disposition": "applied_group_term_only"
    },
    {
        "targetId": "TA2:1504", "query": "Phalanges Toes", "resultLayer": "similar",
        "resultCount": 1, "headword": "Phalanges [Toes]", "koModern": "발가락뼈", "koTraditional": "지골",
        "locator": "Opened KMLE aggregate HTML; 대한해부학회 의학용어 사전 유사 검색 section contains the named KAA row `Phalanges [Toes]` → `발가락뼈`; [옛 용어] `지골`. This is not an exact-result query row. Its scope matches the frozen 28-member phalanges-of-foot target; applied only as group terminology, not to child members.",
        "disposition": "applied_group_term_only_from_opened_similar_section"
    },
    {
        "targetId": "TA2:1514", "query": "Sesamoid bones", "resultLayer": "exact",
        "resultCount": 1, "headword": "Sesamoid bones", "koModern": "종자뼈", "koTraditional": "종자골",
        "locator": "Opened KMLE aggregate HTML; 대한해부학회 의학용어 사전 맞춤 검색 exact-result section contains `Sesamoid bones` → `종자뼈`; [옛 용어] `종자골`. The row is generic and does not specify the foot; not applied to the foot-specific target.",
        "disposition": "candidate_not_applied_broader_scope"
    }
]


def obs_id(target_id: str) -> str:
    return "kmle-t100-round2-" + target_id.lower().replace(":", "-") + "-opened"


def build() -> dict:
    import hashlib
    if hashlib.sha256(INPUT.read_bytes()).hexdigest() != INPUT_SHA256:
        raise SystemExit("frozen query-candidate input hash changed")
    raw = json.loads(INPUT.read_text())
    candidates = raw["candidates"]
    rows = []
    for target in candidates:
        tid = target["targetId"]
        query = target["english"]
        url = "https://m.kmle.co.kr/search.php?" + "Search=" + quote_plus(query)
        value = EXACT.get(tid)
        if value:
            count, headword, modern, traditional, row_text = value
            status = "exact_named_dictionary_row"
            locator = f"Opened KMLE aggregate HTML; 대한해부학회 의학용어 사전 맞춤 검색 exact-result section; {row_text}. The source edition/revision is not exposed and the underlying dictionary record was not opened."
            observed = {"englishHeadword": headword, "koModern": modern, "koTraditional": traditional}
        else:
            count = 0
            status = "no_exact_named_dictionary_row"
            observed = {"englishHeadword": None, "koModern": None, "koTraditional": None}
            locator = f"Opened KMLE aggregate HTML exact query `{query}`; the 대한해부학회 의학용어 사전 맞춤 section reports 0 rows. This records only the exact-result section; it does not assert that no related/similar term exists. The source edition/revision is not exposed and the underlying dictionary record was not opened."
        if tid in SPECIAL_NO_EXACT:
            locator += " " + SPECIAL_NO_EXACT[tid]
        rows.append({
            "id": obs_id(tid), "targetId": tid, "query": query, "url": url,
            "sourceLabel": "KMLE aggregate HTML; 대한해부학회 의학용어 사전 section",
            "discoveryLayer": "Direct target English query URL opened in the browser; search index used only to locate the rendered result section.",
            "retrievalLayer": "Opened KMLE aggregate HTML; exact KAA result rows inspected, not the underlying original KAA dictionary page.",
            "resultLayer": "exact", "resultCount": count, "resultStatus": status,
            "exactEdition": None, "editionExposure": EDITION, "accessDate": date.today().isoformat(),
            "accessMethod": "opened_html", "openedOriginalSourcePage": False,
            "openedOriginalDictionaryRecord": False, "locator": locator,
            "observedFields": observed,
            "fieldConflict": ("koTraditional" if tid == "TA2:1269" else None),
            "observedLegacyConflict": ("제1중수골" if tid == "TA2:1269" else None),
            "sourceSynonyms": {"english": [target["english"]], "latin": [target["latin"]]},
            "noHanjaCollected": True,
        })
    alternates = []
    for row in ALTERNATE:
        query = row["query"]
        alternates.append({
            "id": "kmle-t100-round2-alt-" + row["targetId"].lower().replace(":", "-") + "-opened",
            "targetId": row["targetId"], "query": query,
            "url": "https://m.kmle.co.kr/search.php?" + "Search=" + quote_plus(query),
            "sourceLabel": "KMLE aggregate HTML; 대한해부학회 의학용어 사전 section",
            "discoveryLayer": "Direct target-scope synonym query opened in the browser; not a search-index snippet value.",
            "retrievalLayer": "Opened KMLE aggregate HTML; exact or similar KAA result section and displayed term row read.",
            "resultLayer": row["resultLayer"], "resultCount": row["resultCount"],
            "resultStatus": "exact_named_dictionary_row" if row["resultLayer"] == "exact" else "similar_named_dictionary_row",
            "exactEdition": None, "editionExposure": EDITION, "accessDate": date.today().isoformat(),
            "accessMethod": "opened_html", "openedOriginalSourcePage": False,
            "openedOriginalDictionaryRecord": False, "locator": row["locator"],
            "observedFields": {"englishHeadword": row["headword"], "koModern": row["koModern"], "koTraditional": row["koTraditional"]},
            "disposition": row["disposition"], "noHanjaCollected": True,
        })
    return {
        "schemaVersion": 1, "taskId": "T100", "workUnit": "B-bulk-target-name-query-round-2",
        "openedAtLocalDate": date.today().isoformat(),
        "frozenCandidateInput": "work/evidence/T100/bulk-continuation-2026-09-29/remaining-target-query-candidates.json",
        "candidateCount": len(rows), "queryResults": rows, "scopeSynonymQueries": alternates,
        "sourceLayerPolicy": {
            "searchIndex": "discovery only; not directly assigned as a learner term",
            "openedAggregateHtml": "The named KAA result heading/count and each recorded row/absence were read in the opened KMLE HTML.",
            "originalDictionaryRecord": "not opened",
            "exactEdition": None,
            "editionExposure": EDITION,
            "humanAnatomyReview": "not_performed",
            "hanja": "not_collected",
        },
        "candidateTermDisposition": {
            "exactRows": sum(1 for x in rows if x["resultStatus"] == "exact_named_dictionary_row"),
            "exactMisses": sum(1 for x in rows if x["resultStatus"] == "no_exact_named_dictionary_row"),
            "scopeSynonymRows": {x["targetId"]: x["disposition"] for x in alternates},
        },
        "note": "Query results document this exact finite B candidate pool. A zero exact section does not prove that a term is absent from all editions or sources. No result generated Hanja, an anatomy claim, geometry, canonical ID, or review state.",
    }


if __name__ == "__main__":
    path = HERE / "remaining-target-kmle-observations.json"
    rendered = json.dumps(build(), ensure_ascii=False, indent=2) + "\n"
    path.write_text(rendered)
    print(json.dumps({"written": str(path), "candidates": len(json.loads(rendered)["queryResults"]), "exactRows": sum(1 for x in json.loads(rendered)["queryResults"] if x["resultStatus"] == "exact_named_dictionary_row")}, ensure_ascii=False))
