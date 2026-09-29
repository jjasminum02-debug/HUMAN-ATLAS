#!/usr/bin/env python3
"""Record the opened T100 KMLE `m.` query continuation for the frozen gap set."""
from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from urllib.parse import quote_plus

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
GAPS = HERE / "remaining-target-term-gaps-before-m-queries.json"
EXPECTED_GAPS_SHA256 = "83f07e95715b42732ef4f4c83dac5f14723a627a25dd12b2be3afd3c23703283"
OUT = HERE / "suffix-m-kmle-observations.json"
KMLE = "https://m.kmle.co.kr/search.php?Search="

# Values are the Korean modern/old fields read from opened aggregate KMLE
# pages. The source's original dictionary page/version was not exposed/opened.
EXACT: dict[str, tuple[str, str | None]] = {
    "TA2:2058": ("관자마루근", "측두두정근"),
    "TA2:2061": ("눈살근", "비근근"),
    "TA2:2062": ("코근", "비근"),
    "TA2:2073": ("입둘레근", "구윤근"),
    "TA2:2078": ("입꼬리당김근", "소근"),
    "TA2:2079": ("큰광대근", "대관골근"),
    "TA2:2080": ("작은광대근", "소관골근"),
    "TA2:2087": ("턱끝근", "이(턱)근"),
    "TA2:2132": ("입천장인두근", "구개인두근"),
    "TA2:2148": ("긴목근", "경장근"),
    "TA2:2149": ("긴머리근", "두장근"),
    "TA2:2152": ("앞목갈비근", "전사각근"),
    "TA2:2153": ("중간목갈비근", "중사각근"),
    "TA2:2154": ("뒤목갈비근", "후사각근"),
    "TA2:2165": ("턱목뿔근", "악설골근"),
    "TA2:2168": ("복장목뿔근", "흉골설골근"),
    "TA2:2169": ("어깨목뿔근", "견갑설골근"),
    "TA2:2173": ("복장방패근", "흉골갑상근"),
    "TA2:2174": ("방패목뿔근", "갑상설골근"),
    "TA2:2205": ("가로모뿔근", "횡피열근"),
    "TA2:2235": ("아래뒤톱니근", "하후거근"),
    "TA2:2236": ("위뒤톱니근", "상후거근"),
    "TA2:2258": ("허리엉덩갈비근", "요장륵근"),
    "TA2:2260": ("등엉덩갈비근", "흉장륵근"),
    "TA2:2263": ("등가장긴근", "흉최장근"),
    "TA2:2266": ("머리가장긴근", "두최장근"),
    "TA2:2268": ("등가시근", "흉극근"),
    "TA2:2270": ("머리가시근", "두극근"),
    "TA2:2281": ("등반가시근", "흉반극근"),
    "TA2:2291": ("허리가시사이근", "요극간근"),
    "TA2:2292": ("등가시사이근", "흉극간근"),
    "TA2:2311": ("바깥갈비사이근", "외늑간근"),
    "TA2:2312": ("속갈비사이근", "내늑간근"),
    "TA2:2313": ("맨속갈비사이근", "최내늑간근"),
    "TA2:2382": ("허리네모근", "요방형근"),
    "TA2:2404": ("엉덩꼬리근", "장골미골근"),
    "TA2:2462": ("큰원근", "대원근"),
    "TA2:2482": ("긴손바닥근", "장장근"),
    "TA2:2496": ("위팔노근", "완요골근"),
    "TA2:2510": ("팔꿈치근", "주근"),
    "TA2:2525": ("엄지맞섬근", "무지대립근"),
    "TA2:2594": ("엉덩근", "장골근"),
    "TA2:2610": ("넙다리빗근", "봉공근"),
    "TA2:2614": ("넙다리곧은근", "대퇴직근"),
    "TA2:2618": ("가쪽넓은근", "외측광근"),
    "TA2:2619": ("중간넓은근", "중간광근"),
    "TA2:2620": ("안쪽넓은근", "내측광근"),
    "TA2:2627": ("두덩근", "치골근"),
    "TA2:2635": ("두덩정강근", "박근"),
    "TA2:2641": ("반힘줄모양근", "반건상근"),
    "TA2:2642": ("반막모양근", "반막상근"),
    "TA2:2663": ("장딴지빗근", "족척근"),
    "TA2:2665": ("오금근", "슬와근"),
    "TA2:2684": ("발바닥네모근", "족척방형근"),
}

SIMILAR_CANDIDATES = {
    "TA2:2649": {
        "headword": "Peroneus tertius m.",
        "koModern": "셋째종아리근",
        "koTraditional": "제삼비골근",
        "resultLayer": "KAA similar-result section",
        "targetCrosswalk": "Pinned T96 sourceFlags.relatedTerms includes `musculus peroneus tertius` and `peroneus tertius muscle`; the visible KAA similar-result row is that listed synonym, not the direct `fibularis tertius m.` exact row.",
        "apply": True,
    },
    "TA2:2687": {
        "headword": "musculus interossei plantares",
        "koModern": "발바닥쪽뼈사이근",
        "koTraditional": "족측골간근",
        "resultLayer": "separate 옛 대한의협 3 similar-result section",
        "targetCrosswalk": "The row was visible in the separate `옛 대한의협 3` similar-results section; it is not an exact KAA headword/result for this target and is not applied. T96 target Latin remains the term gap.",
        "apply": False,
    },
}

def main() -> None:
    raw = GAPS.read_bytes()
    if hashlib.sha256(raw).hexdigest() != EXPECTED_GAPS_SHA256:
        raise SystemExit("frozen gap candidate input hash changed")
    frozen = json.loads(raw)
    candidates = frozen["candidates"]
    rows = []
    for c in candidates:
        tid = c["targetId"]
        query = c["variantQuery"]
        exact = EXACT.get(tid)
        row = {
            "id": f"kmle-t100-suffixm-{tid.lower().replace(':','-')}-opened",
            "targetId": tid,
            "query": query,
            "url": KMLE + quote_plus(query),
            "sourceLabel": "KMLE aggregate HTML; 대한해부학회 의학용어 사전 section",
            "discoveryLayer": "Mechanical abbreviation of the frozen exact T96 English target label (terminal `muscle(s)` to `m.`); opened through the visible KMLE search UI.",
            "retrievalLayer": "Opened aggregate HTML and inspected the named KAA exact-result section; underlying original dictionary record was not opened.",
            "exactEdition": None,
            "editionExposure": "The aggregate page identifies the KAA terminology section but exposes no exact edition/revision; the individual underlying dictionary record was not opened.",
            "accessDate": "2026-09-29",
            "accessMethod": "opened_html",
            "openedOriginalSourcePage": False,
            "openedOriginalDictionaryRecord": False,
            "resultLayer": "exact",
            "resultCount": 1 if exact else 0,
            "resultStatus": "exact_named_dictionary_row" if exact else "no_exact_named_dictionary_row",
            "observedFields": ({"koModern": exact[0], "koTraditional": exact[1]} if exact else {"koModern": None, "koTraditional": None}),
            "noHanjaCollected": True,
        }
        if exact:
            row["locator"] = f"Opened KMLE aggregate query `{query}`; exact KAA-result row showed modern Korean `{exact[0]}` and legacy field `{exact[1]}`. Exact KAA edition/revision and original record are not exposed/opened."
        else:
            row["locator"] = f"Opened KMLE aggregate query `{query}`; KAA exact-result section returned zero matching rows. This is an exact-query miss only, not proof that no other edition/source has a term."
        if tid in SIMILAR_CANDIDATES:
            row["separatelyObservedSimilarResult"] = SIMILAR_CANDIDATES[tid]
            if tid == "TA2:2649":
                row["similarResultDisposition"] = "candidate_crosswalked_to_pinned_T96_related_term; applied as synonym evidence, not reported as a direct exact-query hit"
                row["acceptedRelatedTermEvidence"] = {
                    "headword": "Peroneus tertius m.",
                    "koModern": "셋째종아리근",
                    "koTraditional": "제삼비골근",
                    "resultLayer": "KAA similar-result section",
                    "locator": "Opened KMLE aggregate HTML, 대한해부학회 의학용어 사전 유사-result section: `Peroneus tertius m.` -> `셋째종아리근`; [옛 용어] `제삼비골근`. Crosswalk is supported by the frozen T96 TA2:2649 related terms `musculus peroneus tertius` and `peroneus tertius muscle`; the direct `fibularis tertius m.` exact section was empty. The underlying dictionary record and exact edition were not exposed/opened.",
                    "targetCrosswalk": SIMILAR_CANDIDATES[tid]["targetCrosswalk"],
                }
            else:
                row["similarResultDisposition"] = "not_applied_different_dictionary_section_and_nonexact_headword"
        rows.append(row)
    exact_count = sum(x["resultStatus"] == "exact_named_dictionary_row" for x in rows)
    if len(rows) != 87 or exact_count != 54:
        raise SystemExit(f"unexpected suffix query tally: {len(rows)} total / {exact_count} exact")
    output = {
        "schemaVersion": 1,
        "taskId": "T100",
        "workUnit": "B suffix-abbreviation terminology continuation",
        "frozenCandidateInput": GAPS.relative_to(ROOT).as_posix(),
        "frozenCandidateInputSha256": EXPECTED_GAPS_SHA256,
        "openedAtLocalDate": "2026-09-29",
        "queryCount": len(rows),
        "exactKaaRows": exact_count,
        "exactKaaMisses": len(rows) - exact_count,
        "rows": rows,
        "relatedEvidenceSources": [
            {
                "id": "kmle-t100-suffixm-ta2-2649-kaa-similar-opened",
                "targetId": "TA2:2649",
                "url": KMLE + quote_plus("fibularis tertius m."),
                "sourceLabel": "KMLE aggregate HTML; 대한해부학회 의학용어 사전 similar-result section",
                "exactEdition": None,
                "editionExposure": "The aggregate page identifies the KAA section but exposes no exact edition/revision; the individual record was not opened.",
                "accessDate": "2026-09-29",
                "accessMethod": "opened_html",
                "locator": SIMILAR_CANDIDATES["TA2:2649"]["targetCrosswalk"],
                "retrievalLayer": "Opened KMLE aggregate HTML; visible KAA similar-result row read and matched only to a pinned T96 listed related term.",
                "openedOriginalDictionaryRecord": False,
                "openedOriginalSourcePage": False,
                "appliedToTargetTerm": True,
            },
            {
                "id": "kmle-t100-suffixm-ta2-2687-old-kma3-similar-opened",
                "targetId": "TA2:2687",
                "url": KMLE + quote_plus("plantar interossei m."),
                "sourceLabel": "KMLE aggregate HTML; 옛 대한의협 3 dictionary similar-result section",
                "exactEdition": None,
                "editionExposure": "The aggregate page exposes no exact underlying dictionary edition/revision; the individual record was not opened.",
                "accessDate": "2026-09-29",
                "accessMethod": "opened_html",
                "locator": "Separate old KMA-3 similar-result section displayed `musculus interossei plantares` -> `발바닥쪽뼈사이근, 족측골간근`; not a KAA row or exact query hit and not applied.",
                "retrievalLayer": "Opened KMLE aggregate HTML; non-KAA similar-result row read as an unapplied candidate.",
                "openedOriginalDictionaryRecord": False,
                "openedOriginalSourcePage": False,
                "appliedToTargetTerm": False,
            },
        ],
        "policy": {
            "searchIndex": "discovery only; no result snippet was used as the displayed term value",
            "openedAggregatePage": "KMLE HTML section rows/count were inspected",
            "originalDictionaryRecord": "not opened",
            "exactEdition": None,
            "hanja": "not collected",
            "humanAnatomyReview": "not_performed",
            "surfaceApplication": "only exact existing source-name/target matches; no child/parent, side, geometry, identity, canonical binding, rights, or visibility inference",
        },
        "note": "This is a continuation of the fixed set of 87 previously recorded target terminology gaps. It does not reduce the T96 542-target / 563-membership / 12-region denominator and does not imply complete Korean naming.",
    }
    OUT.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"queryCount": len(rows), "exactKaaRows": exact_count, "exactMisses": len(rows)-exact_count, "output": OUT.relative_to(ROOT).as_posix()}, ensure_ascii=False))

if __name__ == "__main__":
    main()
