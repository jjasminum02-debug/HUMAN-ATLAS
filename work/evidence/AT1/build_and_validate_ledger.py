#!/usr/bin/env python3
"""Build and validate the AT1 WHO-361 concept and laterality ledger.

The Hangul labels below are transcribed from the linked KMCRIC meridian lists.
This script creates a source catalog only: it never creates PointInstance
anchors, learner projections, routes, territories, geometry, or approvals.
"""
from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "atlas-data/acupoints/who-361-catalog.json"
VALIDATION = ROOT / "work/evidence/AT1/validation.json"

WHO_NOMENCLATURE_URL = "https://www.who.int/publications/i/item/9290611057"
KMCRIC_BASE = "https://www.kmcric.com/database/acupoint/"

# Code range and concept count are the AT-361 design's fixed manifest. Names
# are copied in code order from each KMCRIC Standard Acupuncture Point DB page.
CHANNELS = [
    ("LU", "수태음폐경", "bilateral", ["중부", "운문", "천부", "협백", "척택", "공최", "열결", "경거", "태연", "어제", "소상"]),
    ("LI", "수양명대장경", "bilateral", ["상양", "이간", "삼간", "합곡", "양계", "편력", "온류", "하렴", "상렴", "수삼리", "곡지", "주료", "수오리", "비노", "견우", "거골", "천정", "부돌", "화료", "영향"]),
    ("ST", "족양명위경", "bilateral", ["승읍", "사백", "거료", "지창", "대영", "협거", "하관", "두유", "인영", "수돌", "기사", "결분", "기호", "고방", "옥예", "응창", "유중", "유근", "불용", "승만", "양문", "관문", "태을", "활육문", "천추", "외릉", "대거", "수도", "귀래", "기충", "비관", "복토", "음시", "양구", "독비", "족삼리", "상거허", "조구", "하거허", "풍륭", "해계", "충양", "함곡", "내정", "여태"]),
    ("SP", "족태음비경", "bilateral", ["은백", "대도", "태백", "공손", "상구", "삼음교", "누곡", "지기", "음릉천", "혈해", "기문", "충문", "부사", "복결", "대횡", "복애", "식두", "천계", "흉향", "주영", "대포"]),
    ("HT", "수소음심경", "bilateral", ["극천", "청령", "소해", "영도", "통리", "음극", "신문", "소부", "소충"]),
    ("SI", "수태양소장경", "bilateral", ["소택", "전곡", "후계", "완골", "양곡", "양로", "지정", "소해", "견정", "노수", "천종", "병풍", "곡원", "견외수", "견중수", "천창", "천용", "관료", "청궁"]),
    ("BL", "족태양방광경", "bilateral", ["정명", "찬죽", "미충", "곡차", "오처", "승광", "통천", "낙각", "옥침", "천주", "대저", "풍문", "폐수", "궐음수", "심수", "독수", "격수", "간수", "담수", "비수", "위수", "삼초수", "신수", "기해수", "대장수", "관원수", "소장수", "방광수", "중려수", "백환수", "상료", "차료", "중료", "하료", "회양", "승부", "은문", "부극", "위양", "위중", "부분", "백호", "고황", "신당", "의희", "격관", "혼문", "양강", "의사", "위창", "황문", "지실", "포황", "질변", "합양", "승근", "승산", "비양", "부양", "곤륜", "복삼", "신맥", "금문", "경골", "속골", "족통곡", "지음"]),
    ("KI", "족소음신경", "bilateral", ["용천", "연곡", "태계", "대종", "수천", "조해", "부류", "교신", "축빈", "음곡", "횡골", "대혁", "기혈", "사만", "중주", "황수", "상곡", "석관", "음도", "복통곡", "유문", "보랑", "신봉", "영허", "신장", "욱중", "수부"]),
    ("PC", "수궐음심포경", "bilateral", ["천지", "천천", "곡택", "극문", "간사", "내관", "대릉", "노궁", "중충"]),
    ("TE", "수소양삼초경", "bilateral", ["관충", "액문", "중저", "양지", "외관", "지구", "회종", "삼양락", "사독", "천정", "청랭연", "소락", "노회", "견료", "천료", "천유", "예풍", "계맥", "노식", "각손", "이문", "화료", "사죽공"]),
    ("GB", "족소양담경", "bilateral", ["동자료", "청회", "상관", "함염", "현로", "현리", "곡빈", "솔곡", "천충", "부백", "두규음", "완골", "본신", "양백", "두임읍", "목창", "정영", "승령", "뇌공", "풍지", "견정", "연액", "첩근", "일월", "경문", "대맥", "오추", "유도", "거료", "환도", "풍시", "중독", "슬양관", "양릉천", "양교", "외구", "광명", "양보", "현종", "구허", "족임읍", "지오회", "협계", "족규음"]),
    ("LR", "족궐음간경", "bilateral", ["대돈", "행간", "태충", "중봉", "여구", "중도", "슬관", "곡천", "음포", "족오리", "음렴", "급맥", "장문", "기문"]),
    ("CV", "임맥", "midline", ["회음", "곡골", "중극", "관원", "석문", "기해", "음교", "신궐", "수분", "하완", "건리", "중완", "상완", "거궐", "구미", "중정", "단중", "옥당", "자궁", "화개", "선기", "천돌", "염천", "승장"]),
    ("GV", "독맥", "midline", ["장강", "요수", "요양관", "명문", "현추", "척중", "중추", "근축", "지양", "영대", "신도", "신주", "도도", "대추", "아문", "풍부", "뇌호", "강간", "후정", "백회", "전정", "신회", "상성", "신정", "소료", "수구", "태단", "은교"]),
]

SOURCE_REGISTRY = [
    {
        "id": "who-361-classical-nomenclature",
        "title": "Standard acupuncture nomenclature: a brief explanation of 361 classical acupuncture point names and their multilingual comparative list",
        "organization": "World Health Organization, Regional Office for the Western Pacific",
        "url": WHO_NOMENCLATURE_URL,
        "factsUsed": "The 361-classical-point naming and code-set context; this page does not supply the Hangul transcription used below.",
        "retrievedDate": "2026-10-11",
    },
    {
        "id": "design-at-361",
        "title": "AT1–AT29 — 361혈 전체와 체표 영역",
        "path": "design/2026-09-25-muscle-atlas/30-AT-361-POINTS-AND-TERRITORIES.md",
        "factsUsed": "The 14 channel code ranges, 309 bilateral concepts, 52 midline concepts, and 670 planned side instances.",
    },
    *[
        {
            "id": f"kmcric-{code.lower()}",
            "title": f"KMCRIC 표준경혈 DB — {name}",
            "url": KMCRIC_BASE + code,
            "factsUsed": f"Hangul point labels and channel membership for {code} codes.",
            "retrievedDate": "2026-10-11",
        }
        for code, name, _laterality, _names in CHANNELS
    ],
]


def fail(message: str) -> None:
    raise SystemExit(message)


def verify_predecessors(concepts_by_code: dict[str, dict]) -> list[dict]:
    ac2_validation = json.loads((ROOT / "work/evidence/acupoint-AC2/validation.json").read_text())
    if ac2_validation.get("acceptedProductPointCount") != 0 or ac2_validation.get("reviewProposalPointCount") != 22:
        fail("AC2 validation no longer records 22 proposals and zero accepted points")
    if ac2_validation.get("professorReview") != "not_performed":
        fail("AC2 professor review state changed")

    entries: list[dict] = []
    for side in ("right", "left"):
        path = f"work/evidence/acupoint-AC2/{side}-learning.json"
        learning = json.loads((ROOT / path).read_text())
        source_concepts = {x["code"]: x for x in learning["concepts"]}
        source_instances = {x["code"]: x for x in learning["instances"]}
        if len(source_concepts) != 11 or len(source_instances) != 11:
            fail(f"AC2 {side} learning file is not exactly 11 concepts and 11 instances")
        for number in range(1, 12):
            code = f"LU{number}"
            concept, instance = source_concepts.get(code), source_instances.get(code)
            if not concept or not instance or code not in concepts_by_code:
                fail(f"AC2 migration source is missing {code}:{side}")
            if concept["nameKo"] != concepts_by_code[code]["nameKo"]:
                fail(f"AC2 name mismatch for {code}:{side}")
            if instance.get("side") != side or instance.get("locationValidation") != "unresolved":
                fail(f"AC2 location/side state changed for {code}:{side}")
            if instance.get("aiProposal") is not True or instance.get("professorReview") != "not_performed":
                fail(f"AC2 proposal/review state changed for {code}:{side}")
            entries.append({
                "migrationId": f"{code}-{side}",
                "ledgerCode": code,
                "nameKo": concept["nameKo"],
                "channelCode": "LU",
                "side": side,
                "legacyConceptRevision": concept["revision"],
                "legacyInstanceRevision": instance["revision"],
                "legacyConceptFile": "work/evidence/acupoint-AC2/point-concepts.json",
                "legacyLearningFile": path,
                "carrierId": learning["carrier"]["id"],
                "carrierRevision": learning["carrier"]["revision"],
                "carrierHash": learning["carrier"]["topologySha256"],
                "locationValidation": "unresolved",
                "aiProposal": True,
                "professorReview": "not_performed",
                "acceptedProductPoint": False,
                "coordinatesCopiedIntoAT1Catalog": False,
                "ac1RightSidePredecessor": side == "right" and code in {"LU1", "LU9", "LU11"},
                "migrationAction": "retain_as_unresolved_proposal_reference",
            })

    ac1_concepts = json.loads((ROOT / "work/evidence/acupoint-AC1/point-concepts.json").read_text())
    ac1_codes = {x["code"] for x in ac1_concepts}
    if ac1_codes != {"LU1", "LU9", "LU11"}:
        fail("AC1's three historical concept records changed")
    if sum(1 for x in entries if x["ac1RightSidePredecessor"]) != 3:
        fail("AC1 → AC2 right-side history crosswalk is incomplete")
    return entries


def build_catalog() -> dict:
    concepts: list[dict] = []
    channels: list[dict] = []
    for code, name, laterality, names in CHANNELS:
        source_id = f"kmcric-{code.lower()}"
        sides = ["right", "left"] if laterality == "bilateral" else ["midline"]
        channels.append({
            "code": code,
            "nameKo": name,
            "firstCode": f"{code}1",
            "lastCode": f"{code}{len(names)}",
            "conceptCount": len(names),
            "lateralityRule": laterality,
            "plannedSides": sides,
            "plannedInstanceCountPerConcept": len(sides),
            "nameSourceId": source_id,
        })
        for number, name_ko in enumerate(names, start=1):
            point_code = f"{code}{number}"
            concepts.append({
                "code": point_code,
                "nameKo": name_ko,
                "channelCode": code,
                "channelNameKo": name,
                "lateralityRule": laterality,
                "plannedSides": sides,
                "nameSourceId": source_id,
                "anchorState": "not_created_by_AT1",
                "locationApproval": "not_decided_by_AT1",
            })

    concepts_by_code = {x["code"]: x for x in concepts}
    migration = verify_predecessors(concepts_by_code)
    bilateral = sum(1 for x in concepts if x["lateralityRule"] == "bilateral")
    midline = sum(1 for x in concepts if x["lateralityRule"] == "midline")
    side_counts = Counter(side for x in concepts for side in x["plannedSides"])
    return {
        "schemaVersion": 1,
        "catalogId": "who-361-acupoint-concepts",
        "revision": "AT1-r1",
        "usage": "source_catalog_only_not_runtime_or_location_approval",
        "standard": "WHO 361 classical acupuncture point code set; AT1 design ranges",
        "hangulLabelLineage": "Transcribed from the KMCRIC Standard Acupuncture Point DB meridian lists.",
        "instanceSemantics": "planned side memberships only; no PointInstance anchors, coordinates, routes, territories, 3D geometry, or learner projection are created by this catalog.",
        "publicRedistribution": "held",
        "professorReview": "not_performed",
        "sourceRegistry": SOURCE_REGISTRY,
        "channelCount": len(channels),
        "conceptCount": len(concepts),
        "channels": channels,
        "concepts": concepts,
        "lateralitySummary": {
            "bilateralConcepts": bilateral,
            "rightPlannedInstances": side_counts["right"],
            "leftPlannedInstances": side_counts["left"],
            "midlineConcepts": midline,
            "midlinePlannedInstances": side_counts["midline"],
            "plannedInstanceCount": sum(side_counts.values()),
            "actualAnchoredInstanceCountCreatedByAT1": 0,
        },
        "legacyProposalMigration": {
            "sourceFeatureRecords": ["AC1", "AC2"],
            "proposalCount": len(migration),
            "acceptedCount": 0,
            "entries": migration,
        },
        "placementState": {
            "ac1Ac2ProposalInstances": 22,
            "acceptedProductInstances": 0,
            "unresolvedProposalInstances": 22,
            "humanReview": "not_performed",
        },
    }


def validate_catalog(catalog: dict) -> dict:
    expected = [(code, name, laterality, len(names)) for code, name, laterality, names in CHANNELS]
    expected_codes = [f"{code}{number}" for code, _name, _laterality, count in expected for number in range(1, count + 1)]
    actual = catalog["concepts"]
    actual_codes = [row.get("code") for row in actual]
    counts = Counter(actual_codes)
    duplicates = sorted(code for code, count in counts.items() if count > 1)
    missing = sorted(set(expected_codes) - set(actual_codes))
    unexpected = sorted(set(actual_codes) - set(expected_codes))
    code_is_canonical = re.compile(r"^(LU|LI|ST|SP|HT|SI|BL|KI|PC|TE|GB|LR|CV|GV)([1-9][0-9]*)$")
    malformed = [code for code in actual_codes if not isinstance(code, str) or not code_is_canonical.fullmatch(code)]

    channels_by_code = {x["code"]: x for x in catalog["channels"]}
    concepts_by_code = {x["code"]: x for x in actual if isinstance(x.get("code"), str)}
    channel_rows_ok = len(catalog["channels"]) == 14 and len(channels_by_code) == 14
    affiliation_errors = []
    name_errors = []
    laterality_errors = []
    for code, name, laterality, count in expected:
        channel = channels_by_code.get(code)
        if not channel or channel.get("nameKo") != name or channel.get("conceptCount") != count:
            channel_rows_ok = False
        for number in range(1, count + 1):
            point_code = f"{code}{number}"
            row = concepts_by_code.get(point_code)
            if not row:
                continue
            if row.get("channelCode") != code or row.get("channelNameKo") != name:
                affiliation_errors.append(point_code)
            if not isinstance(row.get("nameKo"), str) or not row["nameKo"].strip():
                name_errors.append(point_code)
            sides = ["right", "left"] if laterality == "bilateral" else ["midline"]
            if row.get("lateralityRule") != laterality or row.get("plannedSides") != sides:
                laterality_errors.append(point_code)

    concept_laterality = Counter(x.get("lateralityRule") for x in actual)
    planned_side_counts = Counter(side for row in actual for side in row.get("plannedSides", []))
    migration = catalog.get("legacyProposalMigration", {}).get("entries", [])
    migration_keys = [f"{x.get('ledgerCode')}:{x.get('side')}" for x in migration]
    migration_key_counts = Counter(migration_keys)
    migration_duplicates = sorted(key for key, count in migration_key_counts.items() if count > 1)
    expected_migration = {f"LU{number}:{side}" for number in range(1, 12) for side in ("right", "left")}
    migration_missing = sorted(expected_migration - set(migration_keys))
    migration_unexpected = sorted(set(migration_keys) - expected_migration)
    migration_approved = [x.get("migrationId") for x in migration if x.get("acceptedProductPoint") is not False or x.get("locationValidation") != "unresolved" or x.get("aiProposal") is not True or x.get("professorReview") != "not_performed" or x.get("coordinatesCopiedIntoAT1Catalog") is not False]

    reusable_components = {
        "atlas-web/src/viewer/acupoints/schema.ts": ["PointConcept", "PointInstance", "ChannelRoute", "Territory", "right' | 'left' | 'midline"],
        "atlas-web/src/viewer/acupoints/anchorAdapter.ts": ["validateCarrier", "resolveAnchor", "verifyCarrierHash"],
        "atlas-web/src/viewer/acupoints/AcupunctureOverlay.ts": ["class AcupunctureOverlay", "scene.root.add(this.group)", "scene.beginObservation('acupoint'"],
        "atlas-web/src/viewer/wholeBody/cameraSessions.ts": ["class CameraSessions"],
        "atlas-web/src/viewer/acupoints/tour.ts": ["class PointTour", "LUNG_ORDER"],
    }
    component_checks = {}
    for path, needles in reusable_components.items():
        content = (ROOT / path).read_text()
        component_checks[path] = {"present": all(needle in content for needle in needles), "sha256": hashlib.sha256(content.encode()).hexdigest(), "requiredSymbols": needles}

    screen_refs = json.loads((ROOT / "work/evidence/AT1/actual-screen-reference.json").read_text())
    current_screen_path = ROOT / screen_refs["currentViewOptionsScreen"]["path"]
    review_screen_path = ROOT / screen_refs["existingAcupointReviewScreen"]["path"]
    plan_screen_validation = json.loads((ROOT / screen_refs["currentViewOptionsScreen"]["sourceValidation"]).read_text())
    ac2_screen_validation = json.loads((ROOT / screen_refs["existingAcupointReviewScreen"]["sourceValidation"]).read_text())
    def image_size(path: Path) -> list[int]:
        raw = path.read_bytes()
        if len(raw) >= 24 and raw[:8] == b"\x89PNG\r\n\x1a\n":
            return [int.from_bytes(raw[16:20], "big"), int.from_bytes(raw[20:24], "big")]
        if raw[:2] == b"\xff\xd8":
            position = 2
            frame_markers = {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}
            while position + 4 < len(raw):
                if raw[position] != 0xFF:
                    position += 1
                    continue
                while position < len(raw) and raw[position] == 0xFF:
                    position += 1
                if position >= len(raw):
                    break
                marker = raw[position]
                position += 1
                if marker in {0xD8, 0xD9, 0x01} or 0xD0 <= marker <= 0xD7:
                    continue
                if position + 2 > len(raw):
                    break
                segment_length = int.from_bytes(raw[position:position + 2], "big")
                if marker in frame_markers and position + 7 <= len(raw):
                    height = int.from_bytes(raw[position + 3:position + 5], "big")
                    width = int.from_bytes(raw[position + 5:position + 7], "big")
                    return [width, height]
                if segment_length < 2:
                    break
                position += segment_length
        return []

    screen_checks = {
        "currentViewOptionsImageHashMatches": current_screen_path.is_file() and hashlib.sha256(current_screen_path.read_bytes()).hexdigest() == screen_refs["currentViewOptionsScreen"]["sha256"],
        "currentViewOptionsImageDimensionsMatch": image_size(current_screen_path) == screen_refs["currentViewOptionsScreen"]["resolution"],
        "currentViewOptionsValidationPassed": plan_screen_validation.get("passed") is True,
        "observationMenuRemainsRemoved": plan_screen_validation.get("checks", {}).get("observationMenuRemoved") is True,
        "screenFitPreserved": plan_screen_validation.get("checks", {}).get("screenFitKept") is True,
        "historicalAcupointImageHashMatches": review_screen_path.is_file() and hashlib.sha256(review_screen_path.read_bytes()).hexdigest() == screen_refs["existingAcupointReviewScreen"]["sha256"],
        "historicalAcupointImageDimensionsMatch": image_size(review_screen_path) == screen_refs["existingAcupointReviewScreen"]["resolution"],
        "historicalAcupointScreenIsNotTreatedAs361Ui": screen_refs.get("current361LearnerDisplay") == "not_implemented_or_claimed_by_AT1",
    }

    checks = {
        "channelCount14": channel_rows_ok,
        "allDeclaredChannelRangesMatchDesign": not missing and not unexpected and not malformed,
        "conceptCount361": len(actual) == 361,
        "uniqueConceptCodeCount361": len(counts) == 361 and not duplicates,
        "missingCodes": missing,
        "unexpectedCodes": unexpected,
        "duplicateCodes": duplicates,
        "malformedCodes": malformed,
        "all361HaveHangulNames": not name_errors,
        "wrongAffiliations": affiliation_errors,
        "lateralityCounts309Bilateral52Midline": concept_laterality["bilateral"] == 309 and concept_laterality["midline"] == 52,
        "plannedInstances670": sum(planned_side_counts.values()) == 670 and planned_side_counts == Counter({"right": 309, "left": 309, "midline": 52}),
        "lateralityErrors": laterality_errors,
        "migrationContainsExactly22UniqueLUInstances": len(migration) == 22 and not migration_duplicates and not migration_missing and not migration_unexpected,
        "migrationMissing": migration_missing,
        "migrationUnexpected": migration_unexpected,
        "migrationDuplicateKeys": migration_duplicates,
        "all22ProposalsRemainUnresolvedAndUnaccepted": not migration_approved and catalog["placementState"]["acceptedProductInstances"] == 0,
        "existingSchemaAnchorOverlayCameraSessionsTourReusable": all(x["present"] for x in component_checks.values()),
        "reusableComponentChecks": component_checks,
        "actualScreenEvidenceReferencesVerified": all(screen_checks.values()),
        "actualScreenEvidenceChecks": screen_checks,
        "catalogContainsNoCoordinatesOrAnchors": all("anchorState" in row and row["anchorState"] == "not_created_by_AT1" and "coordinates" not in row for row in actual),
        "redistributionHeld": catalog.get("publicRedistribution") == "held",
    }
    required = [key for key, value in checks.items() if isinstance(value, bool)]
    failed = [key for key in required if checks[key] is not True]
    return {
        "status": "passed_for_AT1_ledger_scope" if not failed else "failed",
        "conceptCount": len(actual),
        "uniqueConceptCodeCount": len(counts),
        "channelCount": len(catalog["channels"]),
        "lateralityConceptCounts": dict(concept_laterality),
        "plannedSideInstanceCounts": dict(planned_side_counts),
        "plannedInstanceCount": sum(planned_side_counts.values()),
        "migrationProposalCount": len(migration),
        "acceptedProposalCount": 0 if not migration_approved else None,
        "locationReview": "not_performed; all 22 predecessor proposals remain unresolved",
        "screenEvidenceScope": "existing AC2 and AT-plan actual screens are referenced separately; AT1 adds no learner UI or runtime placement",
        "checks": checks,
        "failedChecks": failed,
    }


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    catalog = build_catalog()
    validation = validate_catalog(catalog)
    OUT.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n")
    VALIDATION.write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n")
    if validation["status"] != "passed_for_AT1_ledger_scope":
        fail("AT1 validation failed: " + ", ".join(validation["failedChecks"]))
    print(json.dumps({"ledger": str(OUT.relative_to(ROOT)), "validation": str(VALIDATION.relative_to(ROOT)), "summary": {k: validation[k] for k in ("status", "conceptCount", "uniqueConceptCodeCount", "channelCount", "lateralityConceptCounts", "plannedSideInstanceCounts", "plannedInstanceCount", "migrationProposalCount", "acceptedProposalCount")}}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
