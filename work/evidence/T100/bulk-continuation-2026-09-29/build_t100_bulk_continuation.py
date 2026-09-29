#!/usr/bin/env python3
"""Deterministically apply the 2026-09-29 evidence-backed T100 naming continuation."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote_plus

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
OVERLAY_REL = "atlas-data/overlays/za-local-integration.json"
SCOPE_REL = "atlas-data/catalog/target-scope-t96.json"
CATALOG_REL = "work/evidence/T98/astra-resolution-2026-09-29/source-catalog.json"
METADATA_REL = "work/evidence/T100/resolution-2026-09-29/source-metadata.json"
COMPILED_REL = "atlas-data/source-cache/datasets/za/compiled/manifest.json"
BASE_HEAD = "c757c2d9e870c8c403025868024872c1710d56a2"
BASE_OVERLAY_SHA = "78a990ab8c1959a6a81fcd6de29ac97ecca8a49c92e29caaf13bc82dc247660b"
T96_SHA = "dba3f2a2dee6c732515e71082d62506b88375b0f88af392c950356703013ac24"
SOURCE_CATALOG_SHA = "f2f1e98d22fe585b7943ddc0d7963af61cf18cced08b76be6984328a59e12ab7"
SOURCE_METADATA_SHA = "4e1d7a2f4913c846755484634b34e9a6fa5820c491bdab1a8223add541b1df3f"
COMPILED_SHA = "56ffd2d93d9a4c4b0b3954511c471358e3da54f47e6915cb35d4b6111f1b7f42"
FIPAT_ID = "fipat-ta2-t96-frozen-target-terms"
ACCESS_DATE = "2026-09-29"
EDITION_EXPOSURE = "KMLE identifies the Korean Association of Anatomists terminology section but exposes no exact dictionary edition or revision; the individual underlying dictionary record was not opened."
KMLE_BASE = "https://m.kmle.co.kr/search.php?Search="
KMLE_DEFAULTS = "&EbookTerminology=YES&DictAll=YES&DictAbbreviationAll=YES&DictDefAll=YES&DictNownuri=YES&DictWordNet=YES"

# Exact row text was read from the opened KMLE aggregate result page's Korean
# Association of Anatomists section. These records are term observations only.
EXACT_ROWS = [
    ("Abductor hallucis", "Abductor hallucis m.", "엄지벌림근", "무지외전근"),
    ("Abductor pollicis brevis", "Abductor pollicis brevis m.", "짧은엄지벌림근", "단무지외전근"),
    ("Abductor pollicis longus", "Abductor pollicis longus m.", "긴엄지벌림근", "장무지외전근"),
    ("Adductor brevis", "Adductor brevis m.", "짧은모음근", "단내전근"),
    ("Adductor longus", "Adductor longus m.", "긴모음근", "장내전근"),
    ("Depressor anguli oris", "Depressor anguli oris m.", "입꼬리내림근", "구각하체근(삼각근)"),
    ("Depressor labii inferioris", "Depressor labii inferioris m.", "아래입술내림근", "하순하체근"),
    ("Diaphragm", "Diaphragm", "가로막", "횡격막"),
    ("Extensor carpi radialis brevis", "Extensor carpi radialis brevis m.", "짧은노쪽손목폄근", "단요측수근신근"),
    ("Extensor carpi radialis longus", "Extensor carpi radialis longus m.", "긴노쪽손목폄근", "장요측수근신근"),
    ("Extensor digiti minimi", "Extensor digiti minimi m.", "새끼폄근", "소지신근"),
    ("Extensor digitorum", "Extensor digitorum m.", "손가락폄근", "지신근"),
    ("Extensor digitorum brevis", "Extensor digitorum brevis m.", "짧은발가락폄근", "단지신근"),
    ("Extensor digitorum longus", "Extensor digitorum longus m.", "긴발가락폄근", "장지신근"),
    ("Extensor hallucis brevis", "Extensor hallucis brevis m.", "짧은엄지폄근", "단무지신근"),
    ("Extensor hallucis longus", "Extensor hallucis longus m.", "긴엄지폄근", None),
    ("Extensor indicis", "Extensor indicis m.", "집게폄근", "시지신근"),
    ("Extensor pollicis brevis", "Extensor pollicis brevis m.", "짧은엄지폄근", "단무지신근"),
    ("Extensor pollicis longus", "Extensor pollicis longus m.", "긴엄지폄근", "장무지신근"),
    ("External anal sphincter", "External anal sphincter m.", "바깥항문조임근", "외항문괄약근"),
    ("Flexor digitorum brevis", "Flexor digitorum brevis m.", "짧은발가락굽힘근", "단지굴근"),
    ("Flexor digitorum longus", "Flexor digitorum longus m.", "긴발가락굽힘근", "장지굴근"),
    ("Flexor hallucis longus", "Flexor hallucis longus m.", "긴엄지굽힘근", "장무지굴근"),
    ("Flexor pollicis longus", "Flexor pollicis longus m.", "긴엄지굽힘근", "장무지굴근"),
    ("Inferior pharyngeal constrictor", "Inferior pharyngeal constrictor muscle", "아래인두수축근", "하인두수축근"),
    ("Levator anguli oris", "Levator anguli oris m.", "입꼬리올림근", "구각거근"),
    ("Levator labii superioris", "Levator labii superioris m.", "위입술올림근", "상순거근"),
    ("Middle pharyngeal constrictor", "Middle pharyngeal constrictor muscle", "중간인두수축근", "중인두수축근"),
    ("Obturator externus", "Obturator externus m.", "바깥폐쇄근", "외폐쇄근"),
    ("Pronator quadratus", "Pronator quadratus m.", "네모엎침근", "방형회내근"),
    ("Psoas major", "Psoas major m.", "큰허리근", "대요근"),
    ("Superior pharyngeal constrictor", "Superior pharyngeal constrictor muscle", "위인두수축근", "상인두수축근"),
    ("Supinator", "Supinator m.", "손뒤침근", "회외근"),
    ("Tensor fasciae latae", "Tensor fasciae latae m.", "넙다리근막긴장근", "대퇴근막장근"),
    # The exact parent term is recorded, but its four visible source objects
    # are medial/lateral heads and do not receive the parent's display name.
    ("Flexor hallucis brevis", "Flexor hallucis brevis m.", "짧은엄지굽힘근", "단무지굴근"),
]
NO_EXACT = [
    ("Depressor septi nasi", None),
    ("Flexor carpi radialis", "Similar result only: `Fiexor carpi radialis m.`; misspelling is not accepted."),
    ("Levator palpebrae superioris", "Similar result only: `Levator palpebrae muscle`; exact headword row is absent."),
    ("Platysma", None),
    ("Adductor minimus", "Existing source objects are parenthesized `(Adductor minimus).l/.r`; no exact Korean Association of Anatomists term row was found."),
]

# Exact range/group headwords discovered in opened KMLE aggregate HTML. Group
# terms stay on their semantically matching T96 target record. `Rib` is kept
# as a separate range observation for individual ribs; T96:1104 is the broader
# "bones of thorax" group and receives only that exact broader term.
REPEATED_GROUP_EXACT = [
    {"targetId":"TA2:1067","query":"Lumbar vertebra","headword":"Lumbar vertebrae(first-fifth)","modern":"허리(척추)뼈(첫째-다섯째)","traditional":"요추골","expectedMembers":5,"crosswalk":"Exact KAA first-fifth range plus T99 `Vertebra L1`–`Vertebra L5` source names and unchanged T96 target membership."},
    {"targetId":"TA2:1104","query":"bones of thorax","headword":"Bones of thorax","modern":"가슴우리뼈","traditional":"흉곽골","expectedMembers":27,"crosswalk":"Exact KAA thorax-bone group term plus all 27 unchanged T96 group members (24 ribs and 3 sternum components); the separate Rib range observation is used only with exact rib member ordinals."},
    {"targetId":"TA2:1106","query":"true ribs","headword":"True ribs(first-seventh)","modern":"참갈비뼈(첫째-일곱째)","traditional":"진륵","expectedMembers":14,"crosswalk":"Exact KAA first-seventh range plus T96 true-rib membership for bilateral first through seventh rib objects."},
    {"targetId":"TA2:1113","query":"false ribs","headword":"False ribs(eighth-twelfth)","modern":"거짓갈비뼈(여덟째-열두째)","traditional":"가륵","expectedMembers":10,"crosswalk":"Exact KAA eighth-twelfth range plus T96 false-rib membership; floating ribs remain a nested subset."},
    {"targetId":"TA2:1114","query":"floating ribs","headword":"Floating ribs(eleventh-twelfth)","modern":"뜬갈비뼈(열한째-열두째)","traditional":"부유늑","expectedMembers":4,"crosswalk":"Exact KAA eleventh-twelfth range plus bilateral T96 floating-rib membership."},
    {"targetId":"TA2:1495","query":"metatarsal bones","headword":"Metatarsal bones(First-fifth)","modern":"발허리뼈(첫째-다섯째)","traditional":"중족(척)골(제1-제5)","expectedMembers":10,"crosswalk":"Exact KAA first-fifth range plus T96 metatarsal-series membership for the existing first through fifth source objects; four prior learner names are preserved."},
    {"targetId":"TA2:2192","query":"laryngeal muscles","headword":"Laryngeal muscles","modern":"후두근육","traditional":"후두근","expectedMembers":15,"crosswalk":"Exact KAA group term plus unchanged T96 group membership. The group label is not assigned to its distinct component muscles/parts."},
]

REPEATED_GROUP_NO_EXACT = [
    {"targetId":"TA2:1179","query":"bones of free part of upper limb","expectedMembers":60},
    {"targetId":"TA2:1504","query":"phalanges of foot","expectedMembers":28},
    {"targetId":"TA2:1514","query":"sesamoid bones of foot","expectedMembers":2},
]

ORDINALS = {
    "First":"첫째", "Second":"둘째", "Third":"셋째", "Fourth":"넷째", "Fifth":"다섯째",
    "Sixth":"여섯째", "Seventh":"일곱째", "Eighth":"여덟째", "Ninth":"아홉째",
    "Tenth":"열째", "Eleventh":"열한째", "Twelfth":"열두째",
}
ORDINAL_RANGE_OBSERVATIONS = [
    {"query":"Rib","headword":"Ribs(first-twelfth)","modern":"갈비뼈(첫째-열두째)","traditional":"늑골"},
]


def need(ok: bool, message: str) -> None:
    if not ok:
        raise SystemExit(message)


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def norm(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip()).casefold()


def read(rel: str):
    return json.loads((ROOT / rel).read_text())


def base_overlay() -> tuple[bytes, dict]:
    raw = subprocess.check_output(["git", "show", f"{BASE_HEAD}:{OVERLAY_REL}"], cwd=ROOT)
    need(sha(raw) == BASE_OVERLAY_SHA, "T100 continuation frozen overlay changed")
    return raw, json.loads(raw)


def source_id(query: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", query.casefold()).strip("-")
    return f"kmle-t100-bulk-{slug}-opened"


def make_observations() -> list[dict]:
    rows = []
    for english, headword, modern, traditional in EXACT_ROWS:
        query = english
        locator = (
            "Opened KMLE aggregate HTML, 대한해부학회 의학용어 사전 맞춤 검색 결과, "
            f"exact query `{query}`; exact row `{headword}` -> `{modern}`"
        )
        if traditional is not None:
            locator += f"; [옛 용어] `{traditional}`"
        elif english == "Extensor hallucis longus":
            # Preserve the observed text as a conflict without accepting it as
            # the Korean legacy display value.
            locator += "; [옛 용어] `장무지싱근` (observed, not applied: spelling conflicts with the exact term and needs source review)"
        locator += ". The underlying edition/revision is not exposed and the individual dictionary record was not opened."
        rows.append({
            "id": source_id(query), "url": KMLE_BASE + quote_plus(query), "query": query,
            "sourceLabel": "KMLE aggregate HTML; 대한해부학회 의학용어 사전 section",
            "discoveryLayer": "Direct KMLE query URL; search-index excerpts were not used as term values.",
            "retrievalLayer": "Opened KMLE aggregate HTML query result; exact-match result row read in the named dictionary section.",
            "exactEdition": None, "editionExposure": EDITION_EXPOSURE, "accessDate": ACCESS_DATE,
            "accessMethod": "opened_html", "openedOriginalSourcePage": False,
            "openedOriginalDictionaryRecord": False, "locator": locator,
            "resultStatus": "exact_named_dictionary_row",
            "observedFields": {
                "englishHeadword": headword, "koModern": modern,
                "koTraditional": "장무지싱근" if english == "Extensor hallucis longus" else traditional,
            },
        })
    for english, similar in NO_EXACT:
        query = english
        locator = (
            "Opened KMLE aggregate HTML exact query `" + query + "`; the 대한해부학회 dictionary "
            "exact-match section returned zero exact headword rows. Similar/fuzzy rows are not accepted as a name."
        )
        if similar:
            locator += " " + similar
        rows.append({
            "id": source_id(query), "url": KMLE_BASE + quote_plus(query), "query": query,
            "sourceLabel": "KMLE aggregate HTML; 대한해부학회 의학용어 사전 section",
            "discoveryLayer": "Direct KMLE query URL; similar results are recorded only as candidates.",
            "retrievalLayer": "Opened KMLE aggregate HTML query result; exact-match result section inspected.",
            "exactEdition": None, "editionExposure": EDITION_EXPOSURE, "accessDate": ACCESS_DATE,
            "accessMethod": "opened_html", "openedOriginalSourcePage": False,
            "openedOriginalDictionaryRecord": False, "locator": locator,
            "resultStatus": "no_exact_named_dictionary_row",
            "observedFields": {"englishHeadword": None, "koModern": None, "koTraditional": None},
            "similarResultNotAccepted": similar,
        })
    for item in REPEATED_GROUP_EXACT:
        query = item["query"]
        locator = (
            "Opened KMLE aggregate HTML; 대한해부학회 의학용어 사전 맞춤 검색 exact-result section; "
            f"exact row `{item['headword']}` -> `{item['modern']}`; [옛 용어] `{item['traditional']}`. "
            "The exact KAA dictionary edition/revision is not exposed and the underlying dictionary record was not opened."
        )
        rows.append({
            "id": source_id(query), "url": KMLE_BASE + quote_plus(query) + KMLE_DEFAULTS, "query": query,
            "sourceLabel": "KMLE aggregate HTML; 대한해부학회 의학용어 사전 section",
            "discoveryLayer": "Direct visible KMLE search UI using an exact T96 target phrase; search-index excerpts were not used as term values.",
            "retrievalLayer": "Opened KMLE aggregate HTML query result; exact group/range row read in the named dictionary section.",
            "exactEdition": None, "editionExposure": EDITION_EXPOSURE, "accessDate": ACCESS_DATE,
            "accessMethod": "opened_html", "openedOriginalSourcePage": False,
            "openedOriginalDictionaryRecord": False, "locator": locator,
            "resultStatus": "exact_named_dictionary_row",
            "observedFields": {"englishHeadword": item["headword"], "koModern": item["modern"], "koTraditional": item["traditional"]},
        })
    for item in REPEATED_GROUP_NO_EXACT:
        query = item["query"]
        locator = (
            f"Opened KMLE aggregate HTML exact query `{query}`; the 대한해부학회 terminology exact-match section returned zero rows. "
            "No similar/index result is used as a name; the original KAA dictionary record was not opened."
        )
        rows.append({
            "id": source_id(query), "url": KMLE_BASE + quote_plus(query) + KMLE_DEFAULTS, "query": query,
            "sourceLabel": "KMLE aggregate HTML; 대한해부학회 의학용어 사전 section",
            "discoveryLayer": "Direct visible KMLE search UI using an exact T96 target phrase; similar/index results are not accepted.",
            "retrievalLayer": "Opened KMLE aggregate HTML query result; exact-match section inspected and empty.",
            "exactEdition": None, "editionExposure": EDITION_EXPOSURE, "accessDate": ACCESS_DATE,
            "accessMethod": "opened_html", "openedOriginalSourcePage": False,
            "openedOriginalDictionaryRecord": False, "locator": locator,
            "resultStatus": "no_exact_named_dictionary_row",
            "observedFields": {"englishHeadword": None, "koModern": None, "koTraditional": None},
            "similarResultNotAccepted": None,
        })
    for item in ORDINAL_RANGE_OBSERVATIONS:
        query = item["query"]
        locator = (
            "Opened KMLE aggregate HTML; 대한해부학회 의학용어 사전 맞춤 검색 exact-result section; "
            f"exact row `{item['headword']}` -> `{item['modern']}`; [옛 용어] `{item['traditional']}`. "
            "This range observation supports only composition with an exact existing ordinal source member; it is not attached as a term for broader T96:1104 bones-of-thorax group. Exact dictionary edition/revision is not exposed and underlying dictionary record was not opened."
        )
        rows.append({
            "id": source_id(query), "url": KMLE_BASE + quote_plus(query) + KMLE_DEFAULTS, "query": query,
            "sourceLabel": "KMLE aggregate HTML; 대한해부학회 의학용어 사전 section",
            "discoveryLayer": "Direct visible KMLE search UI for an exact ordinal-range phrase; search-index excerpts were not used as term values.",
            "retrievalLayer": "Opened KMLE aggregate HTML query result; exact ordinal-range row read in the named dictionary section.",
            "exactEdition": None, "editionExposure": EDITION_EXPOSURE, "accessDate": ACCESS_DATE,
            "accessMethod": "opened_html", "openedOriginalSourcePage": False,
            "openedOriginalDictionaryRecord": False, "locator": locator,
            "resultStatus": "exact_named_dictionary_row",
            "observedFields": {"englishHeadword": item["headword"], "koModern": item["modern"], "koTraditional": item["traditional"]},
            "targetEvidenceAttached": False,
        })
    return rows


def member_record(obj: dict, catalog: dict, source_revision: str, source_hash: str) -> dict:
    source = catalog[obj["sourceKey"]]
    return {
        "sourceKey": obj["sourceKey"], "sourceObjectName": obj["sourceName"],
        "sourceDataName": source.get("dataName"), "sourceParent": source.get("parent"),
        "sourceCollections": source.get("collections", []), "sourceSide": source.get("sourceLabelSide"),
        "targetId": obj.get("targetId"), "targetIds": obj.get("targetIds", []),
        "regionIds": obj.get("regionIds", []), "evaluatedGeometrySha256": source.get("evaluatedGeometrySha256"),
        "sourceHash": source_hash, "sourceRevision": source_revision,
    }


def create_term_evidence(target: dict, observation: dict, surfaces: list[dict],
                         field_status: str, catalog: dict, source_revision: str, source_hash: str) -> dict:
    term = target["term"]
    src_id = observation["id"]
    modern = observation["observedFields"].get("koModern") if field_status in {"exact", "modern_only"} else None
    traditional = observation["observedFields"].get("koTraditional") if field_status == "exact" else None
    missing_reason = "Exact-name Korean terminology row was not directly confirmed; no similar/fuzzy substitute was applied."
    def evidence(value, ids, locator, status, reason=None):
        return {"value": value, "sourceIds": ids, "locator": locator, "status": status, "missingReason": reason}
    locator = observation["locator"]
    fields = {
        "koModern": evidence(modern, [src_id] if modern else [], locator if modern else None,
                             "evidence_backed" if modern else "missing", None if modern else missing_reason),
        "koTraditional": evidence(traditional, [src_id] if traditional else [], locator if traditional else None,
                                  "evidence_backed" if traditional else "missing",
                                  None if traditional else ("KMLE returned a conflicting/truncated legacy spelling; retained as an exception." if field_status == "modern_only" else missing_reason)),
        "en": evidence(term["english"], [FIPAT_ID], f"Pinned T96 exact English term for {target['id']}: {term['english']}", "evidence_backed"),
        "latin": evidence(term["latin"], [FIPAT_ID], f"Pinned T96 exact Latin term for {target['id']}: {term['latin']}", "evidence_backed"),
        "sourceSynonyms": [],
        "hanja": {"value": None, "sourceIds": [], "locator": None, "status": "not_collected", "missingReason": "Actual Hanja glyphs are not collected in this task."},
    }
    for lang, values in term.get("sourceSynonyms", {}).items():
        for value in values:
            fields["sourceSynonyms"].append({
                "language": lang, "value": value, "sourceIds": [FIPAT_ID],
                "locator": f"Pinned T96 exact {lang} source synonym for {target['id']}: {value}",
                "status": "evidence_backed",
            })
    member_rows = [member_record(o, catalog, source_revision, source_hash) for o in surfaces]
    if field_status == "parent_only":
        surface_status = "parent_name_evidence_only_child_head_surfaces_not_renamed"
        classification = "Whole named muscle; T99 source exposes four separately labelled medial/lateral head surfaces. This parent term is not assigned to any head surface."
    elif field_status in {"exact", "modern_only"}:
        surface_status = "exact_target_source_name_rows_present"
        classification = "Exact T96 target term and exact direct source-name match; one concept-level terminology check shared across side-labelled source objects."
    else:
        surface_status = "exact_source_label_surface_present_term_missing_or_conflicted"
        classification = "Exact source/target name row exists; direct KMLE exact Korean terminology row is absent or field-conflicted. Similar results were not adopted."
    unapplied = []
    if field_status == "modern_only":
        observed = observation["observedFields"].get("koTraditional")
        if observed:
            unapplied.append({"value": observed, "sourceId": src_id, "locator": locator,
                              "status": "conflicted_not_applied", "reason": "Opened row contains a conflicting legacy spelling; do not promote it to the display field."})
    if observation.get("similarResultNotAccepted"):
        unapplied.append({"value": observation["similarResultNotAccepted"], "sourceId": src_id,
                          "locator": locator, "status": "similar_candidate_not_applied",
                          "reason": "The result is not the exact T96/source headword."})
    return {
        "targetId": target["id"], "targetTermSourceIds":[FIPAT_ID, src_id],
        "english": term["english"], "latin": term["latin"],
        "sourceSynonyms": term.get("sourceSynonyms", {}), "relatedTerms": term.get("relatedTerms", []),
        "semanticKind": target["semanticKind"], "primaryOwner": target["primaryOwner"],
        "regionIds": target["regionIds"], "sourceParentId": target.get("sourceParentId"),
        "sourceAncestryIds": target.get("sourceAncestryIds", []), "sourceFlags": target.get("sourceFlags", {}),
        "classification":{"meaningType":target["semanticKind"], "groupPartVariant":classification,
                           "laterality":"Source object side remains independent; no geometry mirror or new learner binding."},
        "names":{"koModern":modern,"koTraditional":traditional,"en":term["english"]},
        "fieldEvidence":fields, "unappliedTermCandidates":unapplied,
        "existingSurface":{"status":surface_status,"exactSourceObjects":member_rows,
                            "exactMemberCrosswalkAdded":False,"note":"This is terminology evidence on existing T99 source rows only; it does not create a canonical HA learner binding."},
        "observedSurfacesNotBound":member_rows,
        "learnerBindingCreated":False,"canonicalHaConceptId":None,"sourceOnly":True,
        "humanReview":"not_performed","publicRedistribution":"held","newGeometryCreated":False,
    }


def build_outputs() -> tuple[dict, dict, dict, dict, dict]:
    baseline = read("work/evidence/T100/bulk-continuation-2026-09-29/start-baseline.json")
    need(baseline["head"] == BASE_HEAD, "continuation baseline HEAD differs")
    need(baseline["rootStatusCount"] == 75, "pre-existing user WIP baseline changed")
    for rel, expected in [(OVERLAY_REL, BASE_OVERLAY_SHA),(SCOPE_REL,T96_SHA),(CATALOG_REL,SOURCE_CATALOG_SHA),
                          (METADATA_REL,SOURCE_METADATA_SHA),(COMPILED_REL,COMPILED_SHA)]:
        if rel == OVERLAY_REL:
            continue
        need(sha((ROOT/rel).read_bytes()) == expected, f"frozen input hash changed: {rel}")
    scope=read(SCOPE_REL); catalog_raw=read(CATALOG_REL); compiled=read(COMPILED_REL)
    need(len(scope["targets"])==542 and scope["denominators"]["productRegionMembershipRows"]==563,"T96 denominator changed")
    need(len(catalog_raw["objects"])==960 and catalog_raw["sourceRevision"]=="c7010a903b75a2fd24a13b1c2c4c3546a9223780","T98 source catalog changed")
    overlay_raw, overlay=base_overlay()
    need(overlay["scope"]=={"targets":542,"memberships":563,"regions":12} and len(overlay["objects"])==960,"overlay scope changed")
    need(overlay["revision"].endswith("B-bulk-verified-names"),"expected B01–B05/A/B checkpoint not found")
    source_hash=catalog_raw["sourceHash"]; source_revision=catalog_raw["sourceRevision"]
    tmap={t["id"]:t for t in scope["targets"]}
    cata={o["sourceKey"]:o for o in catalog_raw["objects"]}
    compiled_by_key={x["sourceKey"]:x for x in compiled.get("instances",[])}
    objmap={o["sourceKey"]:o for o in overlay["objects"]}
    evidence_ids={s["id"] for s in overlay.get("evidenceSources",[])}
    target_evidence_ids={x["targetId"] for x in overlay.get("targetTerminologyEvidence",[])}
    fipat=next((x for x in overlay["evidenceSources"] if x["id"]==FIPAT_ID),None)
    need(fipat is not None,"pinned T96 FIPAT evidence source missing")

    observations=make_observations()
    need(len(observations)==51,"expected 35 direct exact, 5 direct no-exact, 7 exact group, 3 no-exact group, and 1 range-only observation")
    for row in observations:
        need(row["id"] not in evidence_ids,"KMLE evidence ID collision")
        evidence_ids.add(row["id"])
        overlay["evidenceSources"].append({
            "id":row["id"],"url":row["url"],"sourceLabel":row["sourceLabel"],"exactEdition":None,
            "editionExposure":row["editionExposure"],"accessDate":row["accessDate"],"accessMethod":row["accessMethod"],
            "locator":row["locator"],"retrievalLayer":row["retrievalLayer"],
            "openedOriginalDictionaryRecord":False,"openedOriginalSourcePage":False,
        })
    observation_by_english={r["query"]:r for r in observations}
    term_evidence_additions=[]
    structure_rows=[]
    newly_named=[]
    field_exceptions=[]
    for english, headword, modern, traditional in EXACT_ROWS:
        target_matches=[t for t in scope["targets"] if norm(t["term"]["english"])==norm(english)]
        need(len(target_matches)==1, f"T96 exact target not unique for {english}")
        target=target_matches[0]; tid=target["id"]
        need(tid not in target_evidence_ids, f"terminology evidence already exists for {tid}")
        observation=observation_by_english[english]
        if english=="Flexor hallucis brevis":
            related=[o for o in overlay["objects"] if tid in o.get("targetIds",[]) and o.get("localDisplayEligible")]
            need(target["semanticKind"]=="named_muscle" and len(related)==4,"FHB parent/part source representation changed")
            need(all(o["targetId"]!=tid and "head of flexor hallucis brevis" in o["sourceName"].casefold() for o in related),"FHB child surfaces no longer explicit")
            term_evidence_additions.append(create_term_evidence(target,observation,related,"parent_only",cata,source_revision,source_hash))
            structure_rows.append({"targetId":tid,"english":english,"semanticKind":target["semanticKind"],"sourceObjects":[member_record(o,cata,source_revision,source_hash) for o in related],"surfaceApplication":"none_parent_term_only","reason":"Exact whole-muscle name is not reused as a name for the medial/lateral head surfaces."})
            target_evidence_ids.add(tid)
            continue
        source_rows=[o for o in overlay["objects"] if o.get("targetId")==tid and o.get("localDisplayEligible")]
        need(len(source_rows) in (1,2), f"unexpected exact-source surface count for {tid}: {len(source_rows)}")
        need(all(norm(re.sub(r"\.[lr]$","",o["sourceName"],flags=re.I))==norm(english) for o in source_rows),f"exact source-name mismatch for {tid}")
        need(all(tid in o.get("targetIds",[]) and o.get("kind")=="muscle" for o in source_rows),f"existing target relation/kind mismatch for {tid}")
        need(all(any(r in target["regionIds"] for r in o.get("regionIds",[])) for o in source_rows),f"region mismatch for {tid}")
        need(len(source_rows)==1 and english=="Diaphragm" or len(source_rows)==2 and {o.get("side") for o in source_rows}=={"left","right"},f"source-side cardinality mismatch for {tid}")
        need(all(o["names"].get("koModern") is None and o["names"].get("koTraditional") is None for o in source_rows),f"Korean field unexpectedly populated for {tid}")
        status="modern_only" if english=="Extensor hallucis longus" else "exact"
        term_evidence_additions.append(create_term_evidence(target,observation,source_rows,status,cata,source_revision,source_hash))
        for obj in source_rows:
            obj["names"]["koModern"]=modern
            obj["label"]=modern
            if traditional is not None:
                obj["names"]["koTraditional"]=traditional
            obj["nameSourceIds"]=list(dict.fromkeys([*obj.get("nameSourceIds",[]),observation["id"]]))
            if traditional is not None:
                obj["nameEvidence"]={
                    "koModern":{"value":modern,"sourceIds":[observation["id"]],"locator":observation["locator"]},
                    "koTraditional":{"value":traditional,"sourceIds":[observation["id"]],"locator":observation["locator"]},
                    "en":{"value":obj["names"]["en"],"sourceIds":[FIPAT_ID],"locator":f"Pinned T96 exact English term for {tid}: {target['term']['english']}"},
                }
            need(obj["sourceOnly"] is True and obj["haConceptId"] is None and obj["humanReview"]=="not_performed" and obj["publicRedistribution"]=="held","name overlay would promote source/policy state")
            need(obj["localDisplayEligible"] is True and obj["defaultVisible"] is True,"name overlay would change local display")
            comp=compiled_by_key.get(obj["sourceKey"])
            newly_named.append({"targetId":tid,"sourceKey":obj["sourceKey"],"sourceName":obj["sourceName"],"side":obj["side"],"regionIds":obj["regionIds"],"koModern":modern,"koTraditional":traditional,"english":target["term"]["english"],"evaluatedGeometrySha256":cata[obj["sourceKey"]]["evaluatedGeometrySha256"],"compiledInstancePresent":bool(comp)})
        structure_rows.append({"targetId":tid,"english":target["term"]["english"],"semanticKind":target["semanticKind"],"koModern":modern,"koTraditional":traditional,"sourceObjects":[member_record(o,cata,source_revision,source_hash) for o in source_rows],"surfaceApplication":"exact_source_name_target_rows_only","canonicalBindingCreated":False,"targetRelationCreated":False})
        if status=="modern_only":
            field_exceptions.append({"kind":"conflicting_legacy_spelling","targetId":tid,"english":english,"field":"koTraditional","observedButNotApplied":observation["observedFields"].get("koTraditional"),"resolution":"modern name only; keep old field null pending an exact supported correction"})
        target_evidence_ids.add(tid)

    for english, similar in NO_EXACT:
        target_matches=[t for t in scope["targets"] if norm(t["term"]["english"])==norm(english)]
        need(len(target_matches)==1, f"T96 exact target not unique for unresolved {english}")
        target=target_matches[0]; tid=target["id"]
        need(tid not in target_evidence_ids, f"terminology evidence already exists for unresolved {tid}")
        observation=observation_by_english[english]
        if english=="Adductor minimus":
            surfaces=[o for o in overlay["objects"] if o.get("targetId")==tid and o.get("localDisplayEligible")]
            need(target["semanticKind"]=="muscle_part" and len(surfaces)==2 and all(o["sourceName"].startswith("(Adductor minimus).") for o in surfaces),"Adductor minimus part/label exception changed")
        else:
            surfaces=[o for o in overlay["objects"] if o.get("targetId")==tid and o.get("localDisplayEligible")]
            need(len(surfaces)==2 and all(norm(re.sub(r"\.[lr]$","",o["sourceName"],flags=re.I))==norm(english) for o in surfaces),f"unresolved exact surface rows changed for {tid}")
        term_evidence_additions.append(create_term_evidence(target,observation,surfaces,"missing",cata,source_revision,source_hash))
        structure_rows.append({"targetId":tid,"english":target["term"]["english"],"semanticKind":target["semanticKind"],"sourceObjects":[member_record(o,cata,source_revision,source_hash) for o in surfaces],"surfaceApplication":"none_unresolved_korean_term","reason":"No exact KAA row; similar/index candidates are not promoted."})
        target_evidence_ids.add(tid)

    def exact_group_members(target_id: str) -> list[dict]:
        candidates=[o for o in overlay["objects"] if o.get("localDisplayEligible") and target_id in o.get("targetIds",[])]
        if target_id in {"TA2:1106","TA2:1113","TA2:1114"}:
            return [o for o in candidates if re.search(r"\brib\.[lr]$",o.get("sourceName",""),re.I)]
        if target_id=="TA2:1067":
            return [o for o in candidates if re.fullmatch(r"Vertebra L[1-5]",o.get("sourceName",""),re.I)]
        if target_id=="TA2:1495":
            return [o for o in candidates if re.search(r"\bmetatarsal bone\.[lr]$",o.get("sourceName",""),re.I)]
        return candidates

    def exact_ordinal_members(target_id: str, kind: str) -> list[dict]:
        candidates=exact_group_members(target_id)
        if kind=="rib":
            return [o for o in candidates if re.search(r"\brib\.[lr]$",o.get("sourceName",""),re.I)]
        return candidates

    repeated_group_records=[]
    expected_group_english={"TA2:1067":"lumbar vertebrae","TA2:1104":"bones of thorax","TA2:1106":"true ribs","TA2:1113":"false ribs","TA2:1114":"floating ribs","TA2:1495":"metatarsal bones","TA2:2192":"laryngeal muscles"}
    for item in REPEATED_GROUP_EXACT:
        target=tmap.get(item["targetId"])
        need(target is not None,f"repeated group target missing: {item['targetId']}")
        need(norm(target["term"]["english"])==norm(expected_group_english[item["targetId"]]),f"repeated group English target changed: {item['targetId']}")
        tid=item["targetId"]
        need(tid not in target_evidence_ids,f"repeated target evidence already exists for {tid}")
        surfaces=exact_group_members(tid)
        need(len(surfaces)==item["expectedMembers"],f"exact group member count drift for {tid}: {len(surfaces)}")
        observation=observation_by_english[item["query"]]
        need(observation["resultStatus"]=="exact_named_dictionary_row" and observation["observedFields"]["englishHeadword"]==item["headword"],f"KAA group row changed for {tid}")
        record=create_term_evidence(target,observation,surfaces,"exact",cata,source_revision,source_hash)
        record["classification"]={
            "meaningType":target["semanticKind"],
            "groupPartVariant":item["crosswalk"],
            "laterality":"T96 source membership is exact; source object side remains unchanged and is not inferred from the group label.",
        }
        record["existingSurface"]={
            "status":"exact_KAA_group_or_range_term_with_existing_T96_membership",
            "exactSourceObjects":[member_record(o,cata,source_revision,source_hash) for o in surfaces],
            "exactMemberCrosswalkAdded":False,
            "note":"Group/range terminology evidence only. No parent/group term was copied onto distinct member names except where the separate exact ordinal-composition rule records a member display value; no geometry, source identity, or canonical binding was created.",
        }
        term_evidence_additions.append(record)
        structure_rows.append({
            "targetId":tid,"english":target["term"]["english"],"semanticKind":target["semanticKind"],
            "headword":item["headword"],"koModern":item["modern"],"koTraditional":item["traditional"],
            "sourceObjects":[member_record(o,cata,source_revision,source_hash) for o in surfaces],
            "surfaceApplication":"group_term_only_no_individual_rename",
            "exactMemberCrosswalkAdded":False,"canonicalBindingCreated":False,"targetRelationCreated":False,
            "membershipBasis":item["crosswalk"],
        })
        repeated_group_records.append({**item,"sourceId":observation["id"],"url":observation["url"],"exactEdition":None,"accessDate":ACCESS_DATE,"accessMethod":"opened_html","memberSourceKeys":sorted(o["sourceKey"] for o in surfaces)})
        target_evidence_ids.add(tid)

    ordinal_member_rules=[
        {"targetId":"TA2:1067","query":"Lumbar vertebra","expected":5,"kind":"lumbar_vertebra","base":"허리뼈"},
        {"targetId":"TA2:1104","query":"Rib","expected":24,"kind":"rib","base":"갈비뼈"},
        {"targetId":"TA2:1495","query":"metatarsal bones","expected":10,"kind":"metatarsal","base":"발허리뼈"},
    ]
    derived_members=[]
    ordinal_word={1:"First",2:"Second",3:"Third",4:"Fourth",5:"Fifth"}
    for rule in ordinal_member_rules:
        obs=observation_by_english[rule["query"]]
        surfaces=exact_ordinal_members(rule["targetId"],rule["kind"])
        need(len(surfaces)==rule["expected"],f"ordinal source member count drift for {rule['targetId']}")
        touched=0
        for obj in surfaces:
            src_name=obj["sourceName"]
            if rule["kind"]=="lumbar_vertebra":
                match=re.fullmatch(r"Vertebra L([1-5])",src_name,re.I)
                need(match is not None,f"unexpected lumbar member label: {src_name}")
                ordinal=ORDINALS[ordinal_word[int(match.group(1))]]
            elif rule["kind"]=="rib":
                match=re.fullmatch(r"(First|Second|Third|Fourth|Fifth|Sixth|Seventh|Eighth|Ninth|Tenth|Eleventh|Twelfth) rib\.[lr]",src_name,re.I)
                need(match is not None,f"unexpected rib member label: {src_name}")
                english_ordinal=next(k for k in ORDINALS if k.casefold()==match.group(1).casefold())
                ordinal=ORDINALS[english_ordinal]
            else:
                match=re.fullmatch(r"(First|Second|Third|Fourth|Fifth) metatarsal bone\.[lr]",src_name,re.I)
                need(match is not None,f"unexpected metatarsal member label: {src_name}")
                english_ordinal=next(k for k in ORDINALS if k.casefold()==match.group(1).casefold())
                ordinal=ORDINALS[english_ordinal]
            modern=ordinal+rule["base"]
            existing=obj.get("names",{}).get("koModern")
            if existing:
                need(existing==modern,f"existing member name conflicts with exact group-range composition: {obj['sourceKey']} {existing} != {modern}")
                derived_members.append({"targetId":rule["targetId"],"sourceKey":obj["sourceKey"],"sourceName":src_name,"side":obj.get("side"),"koModern":modern,"status":"prior_exact_learning_name_preserved","sourceIds":[obs["id"],FIPAT_ID]})
                continue
            need(obj.get("names",{}).get("koTraditional") is None,f"unnamed member has a conflicting legacy term: {obj['sourceKey']}")
            need(obj.get("localDisplayEligible") is True and obj.get("defaultVisible") is True,f"member is not locally displayable: {obj['sourceKey']}")
            need(obj.get("sourceOnly") is True and obj.get("haConceptId") is None and obj.get("humanReview")=="not_performed" and obj.get("publicRedistribution")=="held",f"member policy differs: {obj['sourceKey']}")
            locator=(f"Composed from the opened KAA exact range row `{obs['observedFields']['englishHeadword']} → {obs['observedFields']['koModern']}` "
                     f"and the unchanged exact T99/T96 source member `{src_name}` in group target {rule['targetId']}; "
                     "ordinal and side are taken from that existing source member. This is a range-member display composition, not a new target relation or canonical binding.")
            obj["names"]["koModern"]=modern
            obj["label"]=modern
            obj["nameSourceIds"]=list(dict.fromkeys([*obj.get("nameSourceIds",[]),obs["id"]]))
            existing_name_evidence=obj.get("nameEvidence") or {}
            need(not existing_name_evidence.get("koModern"),f"pre-existing modern-name evidence would be overwritten: {obj['sourceKey']}")
            existing_name_evidence["koModern"]={"value":modern,"sourceIds":[obs["id"],FIPAT_ID],"locator":locator}
            obj["nameEvidence"]=existing_name_evidence
            touched+=1
            comp=compiled_by_key.get(obj["sourceKey"])
            newly_named.append({"targetId":rule["targetId"],"sourceKey":obj["sourceKey"],"sourceName":src_name,"side":obj.get("side"),"regionIds":obj.get("regionIds",[]),"koModern":modern,"koTraditional":None,"english":obj["names"].get("en"),"evaluatedGeometrySha256":cata[obj["sourceKey"]]["evaluatedGeometrySha256"],"compiledInstancePresent":bool(comp),"nameDerivation":"exact KAA group range + exact existing source member ordinal + exact T96 group membership"})
            derived_members.append({"targetId":rule["targetId"],"sourceKey":obj["sourceKey"],"sourceName":src_name,"side":obj.get("side"),"koModern":modern,"status":"applied_exact_group_range_member_composition","sourceIds":[obs["id"],FIPAT_ID],"evaluatedGeometrySha256":cata[obj["sourceKey"]]["evaluatedGeometrySha256"]})
        expected_new=24 if rule["kind"]=="rib" else 5 if rule["kind"]=="lumbar_vertebra" else 6
        need(touched==expected_new,f"unexpected new ordinal name count for {rule['targetId']}: {touched} != {expected_new}")
        repeated_group_records.append({"targetId":rule["targetId"],"rule":"exact_group_range_to_existing_member_name","baseKorean":rule["base"],"expectedMembers":rule["expected"],"newlyNamedMembers":touched,"sourceQueryId":obs["id"],"status":"applied"})

    for item in REPEATED_GROUP_NO_EXACT:
        target=tmap.get(item["targetId"])
        need(target is not None,f"no-exact group target missing: {item['targetId']}")
        tid=item["targetId"]
        need(tid not in target_evidence_ids,f"no-exact group target evidence already exists: {tid}")
        surfaces=[o for o in overlay["objects"] if o.get("localDisplayEligible") and tid in o.get("targetIds",[])]
        need(len(surfaces)==item["expectedMembers"],f"no-exact group membership count drift for {tid}: {len(surfaces)}")
        observation=observation_by_english[item["query"]]
        need(observation["resultStatus"]=="no_exact_named_dictionary_row",f"expected exact-term miss not observed for {tid}")
        term_evidence_additions.append(create_term_evidence(target,observation,surfaces,"missing",cata,source_revision,source_hash))
        structure_rows.append({"targetId":tid,"english":target["term"]["english"],"semanticKind":target["semanticKind"],"sourceObjects":[member_record(o,cata,source_revision,source_hash) for o in surfaces],"surfaceApplication":"none_unresolved_group_term","reason":"Opened exact KMLE query has no exact KAA row; surface/member existence is independent of the unresolved Korean group term."})
        target_evidence_ids.add(tid)

    overlay["targetTerminologyEvidence"].extend(term_evidence_additions)
    overlay["revision"]="T100-source-taxonomy-local-display-v2-B-bulk-verified-names-2026-09-29"
    need(len(overlay["objects"])==960 and overlay["scope"]=={"targets":542,"memberships":563,"regions":12},"output denominator changed")
    need(len(newly_named)==102 and len(term_evidence_additions)==50,"expected 102 evidence-backed name applications and 50 target evidence rows")

    query_evidence={"schemaVersion":1,"taskId":"T100","workUnit":"B+exception-disposition","accessDate":ACCESS_DATE,"sourceLayerPolicy":{"searchIndex":"discovery only; not used for display value","openedHtml":"KMLE aggregate HTML row or absence recorded per exact query","underlyingDictionary":"original KAA record/page not opened; exact edition not exposed","humanReview":"not performed"},"observations":observations}
    term_ledger={"schemaVersion":1,"taskId":"T100","workUnit":"B+exception-disposition","state":"partial_in_progress","inputs":{"baselineHead":BASE_HEAD,"targetScopeSha256":T96_SHA,"sourceCatalogSha256":SOURCE_CATALOG_SHA,"sourceMetadataSha256":SOURCE_METADATA_SHA,"compiledManifestSha256":COMPILED_SHA,"baselineOverlaySha256":BASE_OVERLAY_SHA},"application":{"directExactKoreanConcepts":34,"targetOnlyWholeNameEvidence":1,"exactRepeatedGroupTerms":7,"exactSourceSurfaceRowsNamed":len(newly_named),"nameSourceRows":{"modernAndTraditional":65,"modernOnlyLegacyConflict":2,"modernOnlyExactGroupOrdinalComposition":35},"preservedPreexistingOrdinalNames":4,"newCanonicalBindings":0,"newGeometry":False},"sourceQueryEvidence":query_evidence,"structureCorrespondence":{"records":structure_rows,"repeatedGroupTerms":repeated_group_records,"derivedMemberNames":derived_members,"historicalB01B05RelationsPreserved":237,"historicalB01B05RelationSourceObjects":155,"historicalB01B05TargetIds":29,"newTargetRelations":0},"candidateReconciliation":{"workbookReferenceHash":"8e10e00e76f5da8e6d1be6a0f9dcab6039d9a3f81d8a3808c0fe28545802ab3c","readOnlyFields":["근육표!B","근육표!C"],"rawWorkbookCopied":False,"priorReported":{"exactNormalizedSourceLabelMatches":137,"unnamedLabels":101,"unnamedRows":201,"evidencePath":"work/evidence/T100/bulk-b-2026-09-29/term-and-repetition-ledger.json"},"recomputedSameNormalizationAtOriginalBStart":{"baselineOverlayHead":"1a45ee5e84d921ce88c279b7226cb249723c9673","normalization":"casefold/whitespace normalization and strip only terminal .l/.r from local sourceName","uniqueWorkbookEnglishLabels":255,"exactLocalSourceBaseMatches":41,"unnamedLabels":39,"unnamedSurfaceRows":77,"fullyNamedLabels":2,"priorMetricReproduced":False,"differenceDisposition":"Historical 137/101/201 metric is preserved but not accepted as reproducible; it overstates exact local-name matches under this explicitly reproduced rule. The remaining mismatch is an evidence correction, not 96 completed structures."},"frozenT96ExactEnglish":{"uniqueWorkbookLabels":255,"exactT96TargetTermMatches":51,"targetsWithoutPriorTerminologyEvidence":50,"directTargetEligibleSurfaceRows":83,"directTargetRowsStillMissingModernNameBeforeThisContinuation":77,"strictExactSourceNameTargetConceptsWithAtLeastOneSurface":41},"exactSourceNameCandidates":{"missingAtBContinuationStart":39,"directKAAExactTermsResolved":34,"KoreanNameAppliedConcepts":34,"noExactKoreanRows":5,"surfaceRowsForResolvedTerms":67,"surfaceRowsInFiveUnresolvedTerms":10},"thisCandidatePoolDoesNotRepresentWholeBodyDenominator":True},"resultCounts":{"scope":{"targets":542,"memberships":563,"regions":12,"historicalRemainder":142},"sourceObjects":960,"locallyDisplayEligibleRows":672,"eligibleRowsWithKoModernAfter":len([o for o in overlay["objects"] if o.get("localDisplayEligible") and o.get("names",{}).get("koModern")]),"eligibleRowsStillWithoutKoModernAfter":len([o for o in overlay["objects"] if o.get("localDisplayEligible") and not o.get("names",{}).get("koModern")]),"targetTerminologyEvidenceRowsBefore":42,"targetTerminologyEvidenceRowsAfter":42+len(overlay["targetTerminologyEvidence"])-42,"newNamedSurfaceRows":len(newly_named),"distinctSourceNameConceptsResolved":41,"sourceOnly":True,"publicRedistribution":"held","humanReview":"not_performed","canonicalBindingAdded":0,"geometryChanged":False},"fieldExceptions":field_exceptions,"unresolved":{"bulkBStillIncomplete":True,"unnamedVisibleSurfaceRows":len([o for o in overlay["objects"] if o.get("localDisplayEligible") and not o.get("names",{}).get("koModern")]),"noExactKAAQueries":len([x for x in observations if x["resultStatus"]=="no_exact_named_dictionary_row"]),"unresolvedTraditionalFieldConflicts":1,"homonymousModernKoreanLabels":[["Extensor hallucis brevis","Extensor pollicis brevis","짧은엄지폄근"],["Extensor hallucis longus","Extensor pollicis longus","긴엄지폄근"],["Flexor hallucis longus","Flexor pollicis longus","긴엄지굽힘근"]],"parentMuscleNotAssignedToDistinctHeads":["Flexor hallucis brevis"],"unresolvedBMetricReconciliation":True,"wholeBodyCompletion":False}}
    repetitions={"schemaVersion":1,"taskId":"T100","unit":"B","rule":"Apply exact target terms as group terminology evidence. Compose individual ordinal names only from an exact KAA group/range row, exact unchanged source member ordinal, and frozen T96 target membership. Preserve sourceKey, side, geometry, and hierarchy; no inferred sibling relation.","records":structure_rows,"namedSourceRows":newly_named,"repeatedGroupTerms":repeated_group_records,"derivedMemberNames":derived_members,"newRelationsCreated":0,"canonicalBindingsCreated":0,"geometryChanged":False}
    return overlay,query_evidence,term_ledger,repetitions,{"termsAdded":term_evidence_additions,"newlyNamed":newly_named,"fieldExceptions":field_exceptions}


def main() -> None:
    overlay, query_evidence, ledger, repetition, detail = build_outputs()
    outputs={
        HERE/"source-query-observations.json":query_evidence,
        HERE/"term-and-repetition-ledger.json":ledger,
        HERE/"structure-correspondence.json":repetition,
    }
    for path,value in outputs.items():
        rendered=json.dumps(value,ensure_ascii=False,indent=2)+"\n"
        if "--check" in sys.argv:
            need(path.read_text()==rendered,f"evidence output differs: {path.name}")
        else:
            path.write_text(rendered)
    overlay_path=ROOT/OVERLAY_REL
    rendered_overlay=json.dumps(overlay,ensure_ascii=False,indent=2)+"\n"
    if "--check" in sys.argv:
        need(overlay_path.read_text()==rendered_overlay,"current overlay differs from deterministic continuation output")
    else:
        overlay_path.write_text(rendered_overlay)
    print(json.dumps({"status":"pass" if "--check" in sys.argv else "written","revision":overlay["revision"],"sourceObjects":len(overlay["objects"]),"namedSurfaceRows":len(detail["newlyNamed"]),"targetEvidenceRowsAdded":len(detail["termsAdded"]),"directTerms":34,"repeatedGroupExactTerms":7,"unresolvedQueries":8,"parentOnlyTerm":1},ensure_ascii=False,indent=2))


if __name__ == "__main__":
    main()
