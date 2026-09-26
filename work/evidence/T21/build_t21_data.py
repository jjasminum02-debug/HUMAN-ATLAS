#!/usr/bin/env python3
"""Build the bounded, source-linked T21 calf action overlay and learner bundle."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
OVERLAY = ROOT / "atlas-data/terminology/ai-evidence-overlay.json"
MOTION = ROOT / "atlas-data/motion/motion-learning.json"
REGISTRY = ROOT / "atlas-data/sources/registry.json"
INPUT_FINGERPRINT = ROOT / "work/evidence/T21/input-snapshot.json"


def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def digest(value: bytes | str) -> str:
    if isinstance(value, str):
        value = value.encode("utf-8")
    return hashlib.sha256(value).hexdigest()


def with_hash(row: dict[str, Any], field: str) -> dict[str, Any]:
    result = copy.deepcopy(row)
    result[field] = digest(canonical({key: value for key, value in result.items() if key != field}))
    return result


DATE = "2026-09-27"
ACCESS = "repository_full_text"
TEXT_ACCESS = "full_text_opened"
WORK_TABLE = "WORK-STATPEARLS-CARD-BORDONI-2025"
WORK_MMT = "WORK-LIM-WONG-IDRIS-GHANI-ETAL-2023"
WORK_POSTERIOR = "WORK-STATPEARLS-ABUQUBO-GRAEFE-LAROSE-2026"
TABLE_URL = "https://www.ncbi.nlm.nih.gov/books/NBK539705/table/article-32230.table1/"
MMT_URL = "https://pmc.ncbi.nlm.nih.gov/articles/PMC10624435/?report=reader"
POSTERIOR_URL = "https://www.ncbi.nlm.nih.gov/books/NBK537340/?report=printable"

SOURCES: dict[str, dict[str, Any]] = {
    "T21-STATPEARLS-FOOT-MUSCLES-2025": {
        "id": "T21-STATPEARLS-FOOT-MUSCLES-2025", "underlyingWorkId": WORK_TABLE,
        "title": "Table 1. Overview of the Extrinsic Foot Muscles | StatPearls",
        "url": TABLE_URL, "editionStatus": "verified",
        "edition": "Card RK, Bordoni B. Anatomy, Bony Pelvis and Lower Limb, Foot Muscles. Updated 2025-12-09. In: StatPearls [Internet], 2026 Jan-. Table 1.",
        "accessedOn": DATE, "accessMethod": ACCESS, "textAccess": TEXT_ACCESS,
    },
    "T21-MJMS-STRUCTURED-MMT-2023": {
        "id": "T21-MJMS-STRUCTURED-MMT-2023", "underlyingWorkId": WORK_MMT,
        "title": "Structured Manual Muscle Testing of the Lower Limbs",
        "url": MMT_URL, "editionStatus": "verified",
        "edition": "Lim XY, Wong JKC, Idris Z, Ghani ARI, Abdul Halim S, Abdullah JM. Malays J Med Sci. 2023 Oct 30;30(5):206–220. doi:10.21315/mjms2023.30.5.17. CC BY 4.0.",
        "accessedOn": DATE, "accessMethod": ACCESS, "textAccess": TEXT_ACCESS,
    },
    "T21-STATPEARLS-LEG-POSTERIOR-2026": {
        "id": "T21-STATPEARLS-LEG-POSTERIOR-2026", "underlyingWorkId": WORK_POSTERIOR,
        "title": "Anatomy, Bony Pelvis and Lower Limb: Leg Posterior Compartment",
        "url": POSTERIOR_URL, "editionStatus": "verified",
        "edition": "Abuqubo R, Graefe SB, La Rose J. StatPearls [Internet], 2026 Jan-. Last update 2026-05-13.",
        "accessedOn": DATE, "accessMethod": ACCESS, "textAccess": TEXT_ACCESS,
    },
}

REGISTRY_SOURCES = [
    {
        "id": "T21-STATPEARLS-FOOT-MUSCLES-2025", "category": "modern_anatomy_reference",
        "title": SOURCES["T21-STATPEARLS-FOOT-MUSCLES-2025"]["title"], "organization": "StatPearls Publishing / NCBI Bookshelf",
        "edition": SOURCES["T21-STATPEARLS-FOOT-MUSCLES-2025"]["edition"], "edition_status": "parent article citation and update date preserved from T18; current Table 1 route opened and checked on 2026-09-27",
        "primary_locator": TABLE_URL, "license": {"name": "CC BY-NC-ND 4.0", "status": "opened table footer identifies this license", "url": "https://creativecommons.org/licenses/by-nc-nd/4.0/", "note": "T21 stores short independent Korean summaries and links only; no table text or images are copied. External redistribution or adaptation is not authorized by this task."},
        "access_state": "table1_opened_in_browser_2026-09-27; previous T18 table0 URL now returns page-not-available; see work/evidence/T21/source-manifest.json",
        "artifact_state": "no remote source file downloaded; source metadata and locator hashes only",
        "intended_use_candidate": "Narrow action-summary cross-check and citation-only context; not a human review or movement asset.",
        "limitations": ["Compact action table; it does not give posture, contraction mode, or a full action model.", "Do not count the StatPearls table and other StatPearls chapters as independent primary research."]
    },
    {
        "id": "T21-MJMS-STRUCTURED-MMT-2023", "category": "movement_test_context_reference",
        "title": SOURCES["T21-MJMS-STRUCTURED-MMT-2023"]["title"], "organization": "Malaysian Journal of Medical Sciences / Universiti Sains Malaysia",
        "edition": SOURCES["T21-MJMS-STRUCTURED-MMT-2023"]["edition"], "edition_status": "article metadata and full text opened on PMC",
        "primary_locator": MMT_URL, "license": {"name": "Creative Commons Attribution 4.0 International (CC BY 4.0)", "status": "article copyright/license block states CC BY 4.0", "url": "https://creativecommons.org/licenses/by/4.0/", "note": "T21 paraphrases the relevant movement-test context with attribution; no article figures or video copied."},
        "access_state": "full_text_reader_opened_in_browser_2026-09-27; exact ankle headings and passages recorded in field observations",
        "artifact_state": "no remote source file downloaded; no article text or media copied",
        "intended_use_candidate": "Movement labels and example test positions only; not patient instructions, diagnosis, strength grading, or an exhaustive muscle-function taxonomy.",
        "limitations": ["Manual muscle testing identifies test targets and procedures, not the complete physiological role of each muscle.", "Examiner hand support is test setup and is not converted to a muscle stabilization claim."]
    },
    {
        "id": "T21-STATPEARLS-LEG-POSTERIOR-2026", "category": "modern_anatomy_reference",
        "title": SOURCES["T21-STATPEARLS-LEG-POSTERIOR-2026"]["title"], "organization": "StatPearls Publishing / NCBI Bookshelf",
        "edition": SOURCES["T21-STATPEARLS-LEG-POSTERIOR-2026"]["edition"], "edition_status": "full text states authors, current edition and last update",
        "primary_locator": POSTERIOR_URL, "license": {"name": "CC BY-NC-ND 4.0", "status": "opened full-text footer states this license", "url": "https://creativecommons.org/licenses/by-nc-nd/4.0/", "note": "T21 uses short independent Korean summaries and links only; no source text or image copied. External redistribution or adaptation is not authorized by this task."},
        "access_state": "full_text_opened_2026-09-27; Structure and Function lines 26-31, 55 and citation metadata inspected",
        "artifact_state": "no remote source file downloaded; metadata and field locators only",
        "intended_use_candidate": "Narrow context for posterior-compartment function; not a clip or individual gait contribution measurement.",
        "limitations": ["A narrative StatPearls chapter, not a primary gait experiment.", "Group-level gait statements are not allocated to individual muscles in T21."]
    },
]

MUSCLES = [
    {"id":"HA-M-000001","name":"비복근","row":"Gastrocnemius","movement":"발목 발바닥굽힘","testHeading":"i) Ankle plantar flexion","posture":"문헌의 검사 예시: 검사할 다리에 서고 무릎을 편 자세.","extra":{"field":"functional_context","source":"T21-STATPEARLS-LEG-POSTERIOR-2026","locator":"Structure and Function > superficial posterior muscles; lines 26-27","value":"문헌은 무릎이 편 때 발목 발바닥굽힘에 기여하고 무릎 굽힘도 돕는다고 설명합니다.","contextId":"T21-C-HA-M-000001-KNEE-FLEXION"}},
    {"id":"HA-M-000002","name":"가자미근","row":"Soleus","movement":"발목 발바닥굽힘","testHeading":"i) Ankle plantar flexion","posture":"문헌의 검사 예시: 검사할 다리에 서고 무릎을 편 자세.","extra":{"field":"functional_context","source":"T21-STATPEARLS-LEG-POSTERIOR-2026","locator":"Structure and Function > superficial posterior muscles; line 26","value":"문헌은 가자미근의 발목 발바닥굽힘이 무릎 위치와 관계없이 이뤄진다고 설명합니다.","contextId":"T21-C-HA-M-000002-KNEE-INDEPENDENCE"}},
    {"id":"HA-M-000003","name":"앞정강근","row":"Tibialis anterior","movement":"발목 등쪽굽힘과 발 안쪽번짐","testHeading":"ii) Foot dorsiflexion and inversion","posture":"문헌의 검사 예시: 반듯이 누워 뒤꿈치를 지지면에 댄 자세.","extra":None},
    {"id":"HA-M-000004","name":"뒤정강근","row":"Tibialis posterior","movement":"발 안쪽번짐","testHeading":"iii) Foot inversion","posture":"문헌의 검사 예시: 반듯이 누워 발목을 약간 발바닥굽힘 위치에 둔 자세.","extra":{"field":"functional_context","source":"T21-STATPEARLS-LEG-POSTERIOR-2026","locator":"Structure and Function > tibialis posterior; lines 28 and 55","value":"문헌은 뒤정강근이 발목 발바닥굽힘에 기여하고 중간발 안쪽번짐과 안쪽세로발바닥활 지지에 관여한다고 설명합니다. 보행 중 중간입각기의 중간발 엎침 조절도 언급합니다.","contextId":"T21-C-HA-M-000004-ARCH-SUPPORT"},"tableDetail":"표는 뒤정강근에 발 모음·발바닥굽힘과 회외 보조도 적습니다.","tableDetailLocator":"Table 1, Tibialis posterior row, Action column"},
    {"id":"HA-M-000005","name":"긴종아리근","row":"Fibularis longus","movement":"발 가쪽번짐과 발목 발바닥굽힘","testHeading":"iv) Foot eversion with plantar flexion","posture":"문헌의 검사 예시: 앉거나 반듯이 누워 발목을 중립에 둔 자세.","extra":None,"tableDetail":"표는 긴종아리근의 가로발바닥활 지지도 적습니다.","tableDetailLocator":"Table 1, Fibularis longus row, Action column"},
    {"id":"HA-M-000006","name":"짧은종아리근","row":"Fibularis brevis","movement":"발 가쪽번짐과 발목 발바닥굽힘","testHeading":"iv) Foot eversion with plantar flexion","posture":"문헌의 검사 예시: 앉거나 반듯이 누워 발목을 중립에 둔 자세.","extra":None},
]


def source_row(source_id: str) -> dict[str, Any]:
    return with_hash(SOURCES[source_id], "sourceHash")


def evidence_row(evidence_id: str, source_id: str, locator: str, claim_ids: list[str]) -> dict[str, Any]:
    return with_hash({
        "id": evidence_id, "sourceId": source_id, "locator": locator, "accessedOn": DATE,
        "accessMethod": ACCESS, "textAccess": TEXT_ACCESS, "supportsClaimIds": claim_ids,
    }, "evidenceHash")


def claim_row(claim_id: str, value: Any, evidence_ids: list[str]) -> dict[str, Any]:
    return {"id": claim_id, "value": value, "valueHash": digest(canonical(value)), "evidenceIds": evidence_ids, "attribution": "ai_source_summary"}


def field_item(muscle: dict[str, Any], field: str, value: Any, source_ids: list[str], locators: list[str], state: str = "single_source", *, unavailable_reason: str | None = None, no_claim: bool = False) -> dict[str, Any]:
    base = f"T21-FIELD-{muscle['id']}-{field}"
    claim_id = f"T21-C-{muscle['id']}-{field}"
    claim_ids = [] if no_claim else [claim_id]
    evidences = [evidence_row(f"T21-E-{muscle['id']}-{field}-{index + 1}", source_id, locator, claim_ids) for index, (source_id, locator) in enumerate(zip(source_ids, locators))]
    result = {
        "id": base, "subjectId": muscle["id"], "field": field, "evidenceState": state,
        "claims": [] if no_claim else [claim_row(claim_id, value, [row["id"] for row in evidences])],
        "sources": [source_row(source_id) for source_id in source_ids], "evidence": evidences,
        "geometryState": "absent", "motionState": "text_ready" if field != "contraction_mode" else "absent",
    }
    if unavailable_reason:
        result["unavailableReason"] = unavailable_reason
    return result


def make_item_rows(muscle: dict[str, Any]) -> list[dict[str, Any]]:
    action_claim = f"T21-C-{muscle['id']}-action"
    mmt_locator = f"Ankle > {muscle['testHeading']} > named test movement and primary muscle(s)"
    table_locator = f"Table 1, {muscle['row']} row, Action column"
    action = field_item(muscle, "action", muscle["movement"], ["T21-STATPEARLS-FOOT-MUSCLES-2025", "T21-MJMS-STRUCTURED-MMT-2023"], [table_locator, mmt_locator], "cross_checked")
    posture = field_item(muscle, "action_context", muscle["posture"], ["T21-MJMS-STRUCTURED-MMT-2023"], [f"Ankle > {muscle['testHeading']} > Grading; position statement"])
    role_value = f"이 문헌은 해당 근육을 {muscle['movement']} 검사에서 주 검사 근육으로 지정합니다. 이는 검사 맥락의 지정이며, 일반 움직임에서 작용근·협력근 역할이나 기여 비중을 따로 분류하지 않습니다."
    role = field_item(muscle, "context_role", role_value, ["T21-MJMS-STRUCTURED-MMT-2023"], [mmt_locator])
    stabilization_value = "문헌의 자세 설정과 검사자 손/지지면은 검사 방법으로만 남겼습니다. 이를 이 근육이 고정하는 해부학적 구조나 일반 안정화 작용으로 바꾸지 않았습니다."
    stabilization_locator = f"Ankle > {muscle['testHeading']} > Grading; external support/stabilization setup"
    stabilization = field_item(muscle, "stabilization_note", stabilization_value, ["T21-MJMS-STRUCTURED-MMT-2023"], [stabilization_locator])
    contraction_reason = "열람한 작용 표와 검사 절은 해당 근육의 동적 작용을 동심성·편심성 등 수축 형태로 구분하지 않습니다. 검사 자세를 유지하거나 저항을 받는 지시만으로 수축 유형을 추정하지 않았습니다."
    contraction = field_item(muscle, "contraction_mode", None, ["T21-STATPEARLS-FOOT-MUSCLES-2025", "T21-MJMS-STRUCTURED-MMT-2023"], [table_locator, mmt_locator], "unavailable", unavailable_reason=contraction_reason, no_claim=True)
    rows = [action, posture, role, stabilization, contraction]
    if muscle.get("extra"):
        extra = muscle["extra"]
        rows.append(field_item(muscle, extra["field"], extra["value"], [extra["source"]], [extra["locator"]]))
    if muscle.get("tableDetail"):
        rows.append(field_item(muscle, "action_detail", muscle["tableDetail"], ["T21-STATPEARLS-FOOT-MUSCLES-2025"], [muscle["tableDetailLocator"]]))
    return rows


def evidence_ref(item: dict[str, Any], evidence: dict[str, Any], applies_to: str, context_id: str | None = None) -> dict[str, Any]:
    claim = next((row for row in item["claims"] if evidence["id"] in row["evidenceIds"]), None)
    if claim is None:
        raise ValueError(f"No supporting claim for source ref {item['id']} / {evidence['id']}")
    return {
        "layer": "ai_field", "field": item["field"], "appliesTo": applies_to, "contextId": context_id,
        "claimId": claim["id"], "valueHash": claim["valueHash"], "evidenceId": evidence["id"], "fieldEvidenceId": item["id"],
    }


def make_action(muscle: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_field = {row["field"]: row for row in rows if row["subjectId"] == muscle["id"]}
    action_field = by_field["action"]
    refs = [evidence_ref(action_field, e, "action_explanation") for e in action_field["evidence"]]
    posture_field = by_field["action_context"]
    refs.append(evidence_ref(posture_field, posture_field["evidence"][0], "posture_condition"))
    role_field = by_field["context_role"]
    mmt_context = f"T21-CONTEXT-{muscle['id']}-MANUAL-TEST"
    refs.append(evidence_ref(role_field, role_field["evidence"][0], "context_role", mmt_context))
    stabilization_field = by_field["stabilization_note"]
    refs.append(evidence_ref(stabilization_field, stabilization_field["evidence"][0], "stabilization_condition"))
    context_roles = [{
        "contextId": mmt_context, "role": "unspecified", "contractionRole": "unspecified",
        "explanation": role_field["claims"][0]["value"],
    }]
    extra = muscle.get("extra")
    if extra:
        extra_field = by_field[extra["field"]]
        context_id = extra["contextId"]
        if muscle["id"] == "HA-M-000004":
            context_roles.append({"contextId": context_id, "role": "stabilizer", "contractionRole": "unspecified", "explanation": extra["value"]})
        else:
            context_roles.append({"contextId": context_id, "role": "unspecified", "contractionRole": "unspecified", "explanation": extra["value"]})
        refs.append(evidence_ref(extra_field, extra_field["evidence"][0], "context_role", context_id))
    if muscle.get("tableDetail"):
        detail_field = by_field["action_detail"]
        detail_context = f"T21-C-{muscle['id']}-TABLE-DETAIL"
        detail_role = "stabilizer" if muscle["id"] == "HA-M-000005" else "unspecified"
        context_roles.append({"contextId": detail_context, "role": detail_role, "contractionRole": "unspecified", "explanation": muscle["tableDetail"]})
        refs.append(evidence_ref(detail_field, detail_field["evidence"][0], "context_role", detail_context))
    return {
        "id": f"T21-ACTION-{muscle['id']}", "subjectIds": [muscle["id"]], "sideApplicability": "bilateral",
        "jointBindingState": "unmapped", "jointBindingNote": "현재 canonical catalog에 대응 joint ID가 없어 텍스트 작용만 연결합니다.", "targetJointIds": [],
        "actionLabel": muscle["movement"],
        "explanation": f"해당 근육은 {muscle['movement']}에 관여합니다. 이 요약은 해당 작용을 다룬 출처에 한정되며, 이 근육 하나가 움직임 전체를 단독으로 만든다는 뜻은 아닙니다.",
        "postureConditions": [muscle["posture"]], "stabilizationConditions": [],
        "stabilizationNote": stabilization_field["claims"][0]["value"], "contextRoles": context_roles,
        "sourceRefs": refs,
    }


def write_source_evidence(overlay: dict[str, Any]) -> None:
    evidence_dir = ROOT / "work/evidence/T21"
    sources_by_id = {source_id: source_row(source_id) for source_id in SOURCES}
    source_manifest = {
        "task": "T21", "accessedOn": DATE,
        "searchUse": "Search results were used only to locate the original pages and identify metadata. No search snippet/index text is counted as the final field evidence.",
        "openedSources": [
            {"id":"T21-STATPEARLS-FOOT-MUSCLES-2025","url":TABLE_URL,"openedAs":"visible NCBI Bookshelf Table 1 in the Codex in-app browser","accessMethod":ACCESS,"textAccess":TEXT_ACCESS,"editionBasis":"The current Table 1 path was opened; exact Card/Bordoni article citation and 2025-12-09 update were preserved from the prior T18 source registry record for the same Bookshelf article. The old T18 table0 locator was directly tried and now returns Page not available; T21 uses the current table1 locator.","license":"CC BY-NC-ND 4.0, shown in opened table footer."},
            {"id":"T21-MJMS-STRUCTURED-MMT-2023","url":MMT_URL,"openedAs":"full PMC reader with ankle section and exact method text visible in the in-app browser","accessMethod":ACCESS,"textAccess":TEXT_ACCESS,"editionBasis":"Article title, author list, issue, pages, DOI and license metadata visible in opened full text.","license":"CC BY 4.0, shown in the article copyright/license block."},
            {"id":"T21-STATPEARLS-LEG-POSTERIOR-2026","url":POSTERIOR_URL,"openedAs":"full NCBI Bookshelf printable text opened and inspected","accessMethod":ACCESS,"textAccess":TEXT_ACCESS,"editionBasis":"Opened full text gives authors, StatPearls edition and last update date.","license":"CC BY-NC-ND 4.0, shown in opened full-text footer."},
        ],
        "failedOrOutdatedAttempts": [
            {"url":"https://www.ncbi.nlm.nih.gov/books/NBK539705/table/article-32230.table0/","outcome":"The browser returned Page not available; it was not used as T21 evidence.","treatment":"Retained the older T18 locator unchanged; opened and cited the current table1 page instead."}
        ],
        "sourceWorkIndependence": {
            "actionCrossCheck": "The StatPearls foot-muscle table and Lim et al. 2023 Malaysian Journal of Medical Sciences article are separately authored works in different publications. They overlap on the movement used for each named test muscle. This is a bibliographic work-level cross-check for the shared movement only, not evidence from two independent primary experiments or a complete action inventory.",
            "posteriorChapter": "The 2026 StatPearls posterior-compartment chapter is a separately authored chapter in the same StatPearls series as the foot-muscle table. It is used for narrower contextual statements only and is not counted as independent primary anatomy research.",
        },
        "sourceMetadataHashes": {source_id: sources_by_id[source_id]["sourceHash"] for source_id in SOURCES},
        "hashMeaning": "sourceHash binds the source metadata row; evidenceHash binds the locator/access record; claim valueHash binds the exact saved field value. No source file or full text was downloaded, and none of these hashes is represented as a remote source-file checksum.",
        "humanAnatomyReview": "not performed by this task; AI source comparison is not expert review or a reviewed state.",
        "externalReuse": "No public release or deployment. Table/chapter pages are CC BY-NC-ND 4.0; only short independent paraphrases and source links are kept, and no external adaptation/reuse permission is claimed.",
    }
    observations = []
    for muscle in MUSCLES:
        section = f"Ankle > {muscle['testHeading']}"
        action_locators = [f"Table 1, {muscle['row']} row, Action column", f"{section} > named test movement and primary muscle(s)"]
        row = {
            "subjectId": muscle["id"], "existingName": muscle["name"],
            "action": {"value": muscle["movement"], "fieldEvidenceId": f"T21-FIELD-{muscle['id']}-action", "evidenceState": "cross_checked", "accessedOn": DATE,
                "sources": [
                    {"sourceId":"T21-STATPEARLS-FOOT-MUSCLES-2025","underlyingWorkId":WORK_TABLE,"locator":action_locators[0],"accessMethod":ACCESS,"textAccess":TEXT_ACCESS},
                    {"sourceId":"T21-MJMS-STRUCTURED-MMT-2023","underlyingWorkId":WORK_MMT,"locator":action_locators[1],"accessMethod":ACCESS,"textAccess":TEXT_ACCESS},
                ],
                "comparison":"Both opened works support the shared movement label for the muscle(s) named in this test. The test article is not treated as an exhaustive action list.",
            },
            "testPosture": {"value":muscle["posture"],"fieldEvidenceId":f"T21-FIELD-{muscle['id']}-action_context","sourceId":"T21-MJMS-STRUCTURED-MMT-2023","underlyingWorkId":WORK_MMT,"locator":f"{section} > Grading; position statement","accessMethod":ACCESS,"textAccess":TEXT_ACCESS,"interpretation":"One published test example only; not a required posture for ordinary movement and not clinical guidance."},
            "testRole": {"fieldEvidenceId":f"T21-FIELD-{muscle['id']}-context_role","sourceId":"T21-MJMS-STRUCTURED-MMT-2023","locator":f"{section} > sentence naming the muscle(s) tested","value":"The source names the muscle as a primary test target; T21 does not convert that wording into a general agonist/synergist rank or allocate relative contribution."},
            "stabilization": {"fieldEvidenceId":f"T21-FIELD-{muscle['id']}-stabilization_note","sourceId":"T21-MJMS-STRUCTURED-MMT-2023","locator":f"{section} > Grading; external support/stabilization setup","value":"Examiner support or table position remains test setup and is not interpreted as an anatomical stabilizer or fixed-structure relationship."},
            "contractionMode": {"fieldEvidenceId":f"T21-FIELD-{muscle['id']}-contraction_mode","evidenceState":"unavailable","sources":["T21-STATPEARLS-FOOT-MUSCLES-2025","T21-MJMS-STRUCTURED-MMT-2023"],"reason":"The opened passages do not assign an individual concentric/eccentric/isometric mode; none was inferred."},
            "geometryState":"absent", "motionState":"text_ready", "jointBindingState":"unmapped", "motionAsset":"absent",
            "additionalSourceContext": muscle.get("extra"), "singleSourceTableDetail": muscle.get("tableDetail"),
        }
        observations.append(row)
    (evidence_dir / "source-manifest.json").write_text(json.dumps(source_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (evidence_dir / "field-observations.json").write_text(json.dumps({"task":"T21","accessedOn":DATE,"subjects":observations,"comparisonPolicy":"Shared movement agreement is separated from source-specific details; missing action roles, fixed structures and contraction modes remain unassigned."}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
    motion = json.loads(MOTION.read_text(encoding="utf-8"))
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    fingerprint = json.loads(INPUT_FINGERPRINT.read_text(encoding="utf-8"))
    prior_ids = {row["id"] for row in fingerprint["items"]}
    prior_by_id = {row["id"]: row["canonicalSha256"] for row in fingerprint["items"]}
    current_prior = [row for row in overlay["items"] if row["id"] in prior_ids]
    if len(current_prior) != fingerprint["itemCount"] or any(digest(canonical(row)) != prior_by_id[row["id"]] for row in current_prior):
        raise SystemExit("T18 overlay input changed; refusing to overwrite or merge unknown rows.")
    if len([row for row in overlay["items"] if row["id"].startswith("T21-")]) not in (0, len(overlay["items"]) - fingerprint["itemCount"]):
        raise SystemExit("Unexpected T21 overlay rows found; inspect them before rebuilding.")
    if any(row["id"] not in prior_ids and not row["id"].startswith("T21-") for row in overlay["items"]):
        raise SystemExit("Foreign overlay changes detected; refusing to drop or reorder them.")
    if motion.get("motionDefinitions") or motion.get("motionAssets"):
        raise SystemExit("Motion definitions/assets appeared; T21 will not overwrite them.")
    if motion.get("muscleActions") and not all(row.get("id", "").startswith("T21-ACTION-") for row in motion["muscleActions"]):
        raise SystemExit("Existing non-T21 action rows found; refusing to overwrite them.")

    registry_by_id = {row["id"]: row for row in registry.get("sources", [])}
    for source in REGISTRY_SOURCES:
        existing = registry_by_id.get(source["id"])
        if existing is None:
            registry["sources"].append(source)
        elif existing != source:
            raise SystemExit(f"Source registry row {source['id']} differs from the T21 record; inspect before editing.")
    registry["revision"] = "T21-2026-09-27-calf-action-sources"

    generated = [row for muscle in MUSCLES for row in make_item_rows(muscle)]
    action_by_muscle = {muscle["id"]: make_action(muscle, generated) for muscle in MUSCLES}
    overlay["revision"] = "T21-2026-09-27-calf-actions"
    overlay["items"] = current_prior + generated
    motion["revision"] = "T21-2026-09-27-calf-actions-v1"
    motion["muscleActions"] = [action_by_muscle[muscle["id"]] for muscle in MUSCLES]

    OVERLAY.write_text(json.dumps(overlay, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    MOTION.write_text(json.dumps(motion, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    REGISTRY.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_source_evidence(overlay)
    print(json.dumps({"written": [str(OVERLAY.relative_to(ROOT)), str(MOTION.relative_to(ROOT)), str(REGISTRY.relative_to(ROOT))], "preservedT18Rows": len(current_prior), "addedOverlayRows": len(generated), "muscleActions": len(action_by_muscle), "motionDefinitions": len(motion["motionDefinitions"]), "motionAssets": len(motion["motionAssets"])}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
