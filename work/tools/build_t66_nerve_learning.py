#!/usr/bin/env python3
"""Rebuild the bounded T66 learner nerve relation projection and its private evidence ledger."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GRAPH_PATH = ROOT / "atlas-data/terminology/learner-nerve-graph-t66.json"
COURSE_PATH = ROOT / "atlas-data/terminology/nerve-learning-t66.json"
INTEGRATION_PATH = ROOT / "atlas-data/overlays/za-local-integration.json"
SUPPORT_PATH = ROOT / "atlas-data/overlays/nerve-support-t66.json"
EVIDENCE_DIR = ROOT / "work/evidence/T66/nerve-learning-2026-10-05"
INPUT_DIR = EVIDENCE_DIR / "input"
GRAPH_SEED_PATH = INPUT_DIR / "learner-nerve-graph-t66.json"
COURSE_SEED_PATH = INPUT_DIR / "nerve-learning-t66.json"

SOURCES = {
    "T61_EXISTING_EXACT_GEOMETRY": {
        "url": "internal:work/evidence/T61/verification.json;work/evidence/T61/learner_runtime_check.log",
        "edition": "Existing T61 verified runtime relation; frozen source instance and side",
        "access": "Prior exact runtime and source-geometry verification reused",
        "locator": "Exact deep fibular nerve to left/right tibialis anterior source instance relation only; not a complete nerve supply claim",
    },
    "T66_AXILLARY_2018": {
        "url": "https://pubmed.ncbi.nlm.nih.gov/30428810/",
        "edition": "2018 Dec;23(4):533-538; PMID 30428810; DOI 10.1142/S2424835518500546",
        "access": "PubMed record and abstract opened",
        "locator": "Abstract, Methods/Results/Conclusions; 23 dissections; deltoid regional distribution and teres minor branch",
    },
    "T66_DSN_2018": {
        "url": "https://pubmed.ncbi.nlm.nih.gov/30461656/",
        "edition": "2018 Nov;97(47):e13349; PMID 30461656; PMCID PMC6392864; DOI 10.1097/MD.0000000000013349",
        "access": "PubMed record and abstract opened",
        "locator": "Abstract; 70 Japanese cadavers / 140 sides; rhomboid major, rhomboid minor, levator scapulae; middle-scalene path variants",
    },
    "T66_PECTORAL_2011": {
        "url": "https://pubmed.ncbi.nlm.nih.gov/21587039/",
        "edition": "2012 Feb;68(2):209-214; PMID 21587039; DOI 10.1097/SAP.0b013e318212f3d9",
        "access": "PubMed record and abstract opened",
        "locator": "Abstract; 30 pectoral specimens from 15 cadavers; lateral and medial pectoral innervation and variable fourth-intercostal contribution",
    },
    "T66_RF_2019": {
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC6662958/",
        "edition": "2019; PMID 31660203; PMCID PMC6662958",
        "access": "PMC primary article abstract and methods/results opened from indexed full-text page; PubMed direct page unavailable",
        "locator": "Abstract and Methods/Results; seven cadaveric specimens; femoral motor branches entering rectus femoris; branch-count variation",
    },
    "T66_INTERCOSTAL_ABDOMINAL_1992": {
        "url": "https://pubmed.ncbi.nlm.nih.gov/1600882/",
        "edition": "1992 Apr-May;32(4-5):171-185; PMID 1600882",
        "access": "PubMed indexed abstract; direct page returned a verification challenge",
        "locator": "Abstract; lower intercostal mixed branches include external-oblique muscle branch and deep branch to rectus abdominis / other muscles",
    },
    "T66_EAO_1985": {
        "url": "https://pubmed.ncbi.nlm.nih.gov/3160258/",
        "edition": "1985;158(3):285-292; PMID 3160258",
        "access": "PubMed indexed abstract",
        "locator": "Abstract; one-cadaver report of upper external-oblique slips with fifth/sixth intercostal motor branches; narrow variant evidence only",
    },
    "T66_RA_2008": {
        "url": "https://pubmed.ncbi.nlm.nih.gov/18428988/",
        "edition": "2008; PMID 18428988",
        "access": "PubMed indexed abstract; direct page unavailable in this session",
        "locator": "Abstract; 20 human cadaveric hemi-abdominal walls; rectus abdominis T6-L1 segmental innervation and widespread communications",
    },
    "T66_MEDIAN_2020": {
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC7580294/",
        "edition": "2020; PMID 33144842; PMCID PMC7580294",
        "access": "PMC primary article text opened via indexed full-text page",
        "locator": "Methods/Results; 20 upper limbs from 10 cadavers; branches to pronator teres, FCR, palmaris longus, FDS; variable branch patterns",
    },
    "T66_RADIAL_2020": {
        "url": "https://pubmed.ncbi.nlm.nih.gov/32498404/",
        "edition": "2020 Jun 2;10(6):366; PMID 32498404; PMCID PMC7345276; DOI 10.3390/diagnostics10060366",
        "access": "PubMed record and abstract opened",
        "locator": "Abstract; 35 cadavers; typical motor branch order includes brachioradialis and extensor carpi radialis longus; variations noted",
    },
    "T66_PFCN_2020": {
        "url": "https://pubmed.ncbi.nlm.nih.gov/31973825/",
        "edition": "2020 Mar;124(3):308-313; PMID 31973825; DOI 10.1016/j.bja.2019.10.026",
        "access": "PubMed record and abstract opened",
        "locator": "Abstract; 83 human lower extremities; subgluteal fold to distal terminus; sensory lower-leg contribution and course variation",
    },
    "T66_LFCN_2025": {
        "url": "internal:work/evidence/T66/parallel-completion-2026-10-03/wave-1/workers/F/field-evidence-sources.json",
        "edition": "2025 Mar 28;40(1):12-17; PMID 40152087; PMCID PMC11974468",
        "access": "Existing worker F field claim/provenance and value hash reused",
        "locator": "Measurement details; Results; Discussion; LFCN around inguinal ligament/ASIS with variable branching; distinct from PFCN",
    },
    "T66_MEDIAN_COURSE_2014": {
        "url": "internal:work/evidence/T66/parallel-completion-2026-10-03/wave-1/workers/F/field-evidence-sources.json",
        "edition": "2014 May 15;9(4):466-470; PMID 25414606; PMCID PMC4235925",
        "access": "Existing worker F course field claim/provenance and value hash reused",
        "locator": "Abstract; Anatomy; Discussion; proximal forearm FDS arch / median nerve / AIN takeoff; 38 cadavers",
    },
}

# Nerve source label, target display concept, exact existing muscle names, scope, learner-safe limit, source rows.
CONCEPT_LINKS = [
    ("dorsal-scapular", "Levator scapulae", ["Levator scapulae"], "unsided_named_whole_muscle_concept", "해부 연구에서 어깨올림근과의 운동 관계가 보고되었습니다. 아래는 같은 쪽에 선택 가능한 근육 표면이며, 모형의 신경 가지에 직접 연결된 좌표는 아닙니다.", ["T66_DSN_2018"]),
    ("nerve-source-axillary-nerve", "Deltoid muscle", ["Acromial part of deltoid muscle", "Clavicular part of deltoid muscle", "Scapular spinal part of deltoid muscle"], "unsided_named_muscle_part_set", "해부 연구는 겨드랑신경과 삼각근 여러 구역의 관계를 보고합니다. 아래 세분 표면은 모형의 표시 단위이며 각 신경 가지와 일대일로 대응하지 않습니다.", ["T66_AXILLARY_2018"]),
    ("nerve-source-axillary-nerve", "Teres minor muscle", ["Teres minor muscle"], "unsided_named_whole_muscle_concept", "해부 연구에서 소원근으로 향하는 겨드랑신경 가지가 확인되었습니다. 아래는 같은 쪽 선택 표면이며, 개별 가지를 잇는 모형 좌표는 아닙니다.", ["T66_AXILLARY_2018"]),
    ("nerve-source-lateral-pectoral-nerve", "Pectoralis major muscle", ["(Abdominal part of pectoralis major muscle)", "Clavicular head of pectoralis major muscle", "Sternocostal head of pectoralis major muscle"], "unsided_named_muscle_part_set", "문헌은 가쪽가슴근신경이 대흉근의 주요 운동 공급에 참여한다고 보고합니다. 아래 모형의 세 부분은 선택 가능한 표시 단위이며 문헌의 가지별 구획과 일대일로 대응하지 않습니다.", ["T66_PECTORAL_2011"]),
    ("nerve-source-medial-pectoral-nerve", "Pectoralis major muscle", ["(Abdominal part of pectoralis major muscle)", "Clavicular head of pectoralis major muscle", "Sternocostal head of pectoralis major muscle"], "unsided_named_muscle_part_set", "문헌은 안쪽가슴근신경이 대흉근 일부 구간에 기여한다고 보고합니다. 아래 모형의 세 부분은 선택 가능한 표시 단위이며 정확한 신경가지 분포 경계가 아닙니다.", ["T66_PECTORAL_2011"]),
    ("nerve-source-femoral-nerve", "Rectus femoris muscle", ["Rectus femoris muscle"], "unsided_named_whole_muscle_concept", "해부 연구에서 넙다리신경 운동가지가 넙다리곧은근에 들어가는 관계를 확인했습니다. 가지 수와 진입 양상에 변이가 있으며, 모형 신경 가지의 좌표 연결은 아닙니다.", ["T66_RF_2019"]),
    ("nerve-source-intercostal-nerves", "Rectus abdominis muscle", ["Rectus abdominis muscle"], "unsided_partial_muscle_concept", "문헌은 여러 분절의 가슴배신경이 복직근에 기여한다고 보고합니다. 현재 신경 묶음·근육 표면에서 특정 분절이나 전체 범위를 일대일로 지정하지 않습니다.", ["T66_INTERCOSTAL_ABDOMINAL_1992", "T66_RA_2008"]),
    ("nerve-source-intercostal-nerves", "External abdominal oblique muscle", ["External abdominal oblique muscle"], "unsided_partial_muscle_concept", "해부 문헌은 가슴사이신경의 근육가지를 바깥배빗근 일부에 기술합니다. 아래는 한 선택 가능 표면이며, 모든 섬유·분절의 완전한 범위나 좌표 연결을 뜻하지 않습니다.", ["T66_INTERCOSTAL_ABDOMINAL_1992", "T66_EAO_1985"]),
    ("nerve-source-median-nerve", "Pronator teres", ["Superficial head of pronator teres", "Deep head of pronator teres"], "unsided_named_muscle_part_set", "해부 연구에서 정중신경의 원엎침근 운동가지가 보고되었습니다. 아래 두 모형 부분은 분할 표면이며, 각 부분별 신경 가지의 정확한 경계를 뜻하지 않습니다.", ["T66_MEDIAN_2020"]),
    ("nerve-source-median-nerve", "Flexor carpi radialis", ["Flexor carpi radialis"], "unsided_named_whole_muscle_concept", "해부 연구에서 정중신경과 노쪽손목굽힘근의 운동 관계가 보고되었습니다. 아래는 같은 쪽 선택 표면이며 개별 가지 좌표는 연결하지 않았습니다.", ["T66_MEDIAN_2020"]),
    ("nerve-source-median-nerve", "Palmaris longus muscle", ["Palmaris longus muscle"], "unsided_named_whole_muscle_concept", "해부 연구에서 정중신경과 긴손바닥근의 운동 관계가 보고되었습니다. 아래는 같은 쪽 선택 표면이며 개인별 존재·분지 변이를 모두 나타내지 않습니다.", ["T66_MEDIAN_2020"]),
    ("nerve-source-median-nerve", "Flexor digitorum superficialis", ["Humero-ulnar head of flexor digitorum superficialis", "Radial head of flexor digitorum superficialis"], "unsided_named_muscle_part_set", "해부 연구에서 정중신경과 얕은손가락굽힘근의 운동 관계가 보고되었습니다. 두 모형 부분은 표시 단위이며 문헌의 가지와 부위가 일대일 대응하지 않습니다.", ["T66_MEDIAN_2020"]),
    ("nerve-source-radial-nerve", "Brachioradialis muscle", ["Brachioradialis muscle"], "unsided_named_whole_muscle_concept", "아래팔 해부 연구에서 위팔노근으로 향하는 노신경 가지가 전형적 분지 순서에 포함되며 변이도 보고되었습니다. 개별 가지의 모형 좌표 연결은 아닙니다.", ["T66_RADIAL_2020"]),
    ("nerve-source-radial-nerve", "Extensor carpi radialis longus", ["Extensor carpi radialis longus"], "unsided_named_whole_muscle_concept", "아래팔 해부 연구에서 긴노쪽손목폄근으로 향하는 노신경 가지가 전형적 분지 순서에 포함됩니다. 분지 순서에는 변이가 있으며, 모형 가지의 직접 좌표 연결은 아닙니다.", ["T66_RADIAL_2020"]),
]

def load(path: Path):
    return json.loads(path.read_text())

def dump(path: Path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main() -> None:
    check = "--check" in sys.argv[1:]
    graph = load(GRAPH_SEED_PATH)
    course = load(COURSE_SEED_PATH)
    integration = load(INTEGRATION_PATH)
    support = load(SUPPORT_PATH)
    muscles = [r for r in integration["objects"] if r.get("kind") == "muscle" and r.get("localDisplayEligible")]
    muscles_by_name: dict[str, list[dict]] = {}
    for row in muscles:
        muscles_by_name.setdefault(row["names"]["en"], []).append(row)
    concepts = {c["key"]: c for c in graph["concepts"]}
    ids = set()
    for row in graph["motorRelations"]:
        nerve = concepts[row["nerveKey"]]
        if row["nerveKey"] == "deep-fibular":
            side = row.get("targetSide")
            row["relationId"] = f"nerve-motor-deep-fibular-{side}"
            row["basis"] = "exact_geometry_motor_relation"
            row["displayNote"] = f"현재 확인한 모형 연결은 {'왼쪽' if side == 'left' else '오른쪽'} 깊은종아리신경 표면과 같은 쪽 앞정강근 표면에 한정됩니다. 전체 지배 범위를 뜻하지 않습니다."
        elif nerve["key"] == "dorsal-scapular":
            label = "rhomboid-major" if row.get("targetEnglishConcept") == "Rhomboid major muscle" else "rhomboid-minor"
            row["relationId"] = f"nerve-motor-dorsal-scapular-{label}"
            row["basis"] = "literature_concept_motor_relation"
        if row["relationId"] in ids:
            raise ValueError(f"duplicate relation id: {row['relationId']}")
        ids.add(row["relationId"])
    for nerve_key, target, names, scope, note, source_ids in CONCEPT_LINKS:
        target_rows = []
        for name in names:
            matched = muscles_by_name.get(name, [])
            if not matched:
                raise ValueError(f"no existing eligible target surface: {name}")
            sides = {row.get("side") for row in matched}
            if sides != {"left", "right"}:
                raise ValueError(f"expected existing left/right target surfaces for {name}, got {sides}")
            target_rows.extend(sorted(matched, key=lambda row: (row["side"], row["sourceKey"])))
        relation_id = "nerve-motor-" + nerve_key.removeprefix("nerve-source-") + "-" + target.lower().replace(" ", "-")
        if relation_id in ids:
            raise ValueError(f"duplicate relation id: {relation_id}")
        ids.add(relation_id)
        graph["motorRelations"].append({
            "relationId": relation_id,
            "nerveKey": nerve_key,
            "basis": "literature_concept_motor_relation",
            "targetEnglishConcept": target,
            "targetSourceKeys": [row["sourceKey"] for row in target_rows],
            "targetSide": None,
            "scope": scope,
            "displayNote": note,
        })
    relation_nerve_keys = {row["nerveKey"] for row in graph["motorRelations"]}
    for concept in graph["concepts"]:
        if concept["key"] in {"nerve-source-lateral-femoral-cutaneous-nerve", "nerve-source-posterior-femoral-cutaneous-nerve"}:
            concept["functionEvidenceClass"] = "sensory_course_documented_no_motor_relation"
        elif concept["key"] in {"nerve-source-axillary-nerve", "nerve-source-intercostal-nerves"}:
            concept["functionEvidenceClass"] = "mixed_motor_sensory_evidence_and_motor_relation"
        elif concept["key"] in relation_nerve_keys:
            concept["functionEvidenceClass"] = "motor_relation_documented_sensory_class_not_assessed"
        else:
            concept["functionEvidenceClass"] = "relationship_not_linked"
    dorsal = concepts["dorsal-scapular"]["summary"]
    dorsal["motorRelation"] = "문헌은 등쪽어깨신경과 큰·작은마름근 및 어깨올림근의 운동 관계를 보고합니다. 아래 근육 표면은 같은 쪽 선택을 돕는 개념 연결이며, 좌우별 신경 가지나 부착 좌표를 뜻하지 않습니다."
    dorsal["variation"] = "등쪽어깨신경은 중간목갈비근을 뚫거나 앞쪽을 지나는 경로 변이가 보고되었습니다. 어깨올림근 관계는 문헌 수준에서 연결했으며, 정적 모형의 좌표나 모든 개인의 분지 범위를 확정하지 않습니다."

    course["Posterior femoral cutaneous nerve"]["courseContext"] = "해부 연구는 엉덩이 아래주름에서 시작한 후대퇴피신경을 오금 아래까지 추적했습니다. 83개 표본에서 종말점이 오금에 머물거나 종아리 근위·원위부까지 이어지는 차이가 관찰되었습니다."
    course["Posterior femoral cutaneous nerve"]["functionContext"] = "후대퇴피신경은 피부 감각 경로입니다. 인용한 해부 연구에서는 종아리까지 이어지는 변이가 관찰되었으며, 이를 특정 모형의 좌표나 운동근 연결로 해석하지 않습니다."
    course["Posterior femoral cutaneous nerve"]["variationContext"] = "표본의 원위 종말점은 오금·종아리 근위부·종아리 원위부로 달랐습니다. 외측대퇴피신경이나 넙다리신경과 같은 구조로 합치지 않으며, 실제 압박 지점을 지정하지 않습니다."
    course["Femoral nerve"]["functionContext"] = "해부 연구에서 넙다리신경의 운동가지가 넙다리곧은근에 들어가는 것을 확인했고, 가지 수와 진입 양상에는 변이가 있었습니다. 문헌 관계는 개념 수준이며 정적 모형의 가지 좌표를 뜻하지 않습니다."
    course["Lateral pectoral nerve"]["functionContext"] = "해부 연구는 가쪽가슴근신경을 대흉근의 주요 운동 공급으로, 안쪽가슴근신경 가지를 보충 경로로 보고했습니다. 선택 가능한 대흉근 부분 표면은 표시 단위이며 개별 신경 가지의 경계와 일치한다고 확정하지 않습니다."
    course["Medial pectoral nerve"]["functionContext"] = "해부 연구는 안쪽가슴근신경이 작은가슴근을 지나 대흉근 일부 구간에도 가지를 보내는 양상을 보고했습니다. 문헌의 구획과 현재 모형의 세 부분 표면을 일대일로 대응하지 않습니다."
    course["Intercostal nerves"]["courseContext"] = "앞배벽의 분절 신경은 여러 가지와 연결을 이루며 근육 가지와 피부 가지를 냅니다. 현재 표시는 정적 묶음 표본으로, 개별 분절의 좌우·주행을 완전히 구분한 모형은 아닙니다."
    course["Intercostal nerves"]["functionContext"] = "문헌은 여러 가슴배 분절의 운동 가지가 복직근에, 가슴사이신경의 일부 가지가 바깥배빗근에 기여한다고 보고합니다. 현재 연결은 부분 개념 수준이며 특정 분절이나 전체 근육을 대표하지 않습니다."
    course["Radial nerve"]["functionContext"] = "해부 연구에서 위팔노근과 긴노쪽손목폄근으로 향하는 가지가 전형적 아래팔 분지 순서에 포함되지만, 가지 순서와 일부 근육의 신경 기원에는 변이가 보고됩니다. 현재 관계는 근육 개념 수준입니다."
    course["Median nerve"]["functionContext"] = "해부 연구의 20개 팔 표본에서 원엎침근·노쪽손목굽힘근·긴손바닥근·얕은손가락굽힘근의 정중신경 운동 관계가 보고되었고 가지 배열은 변이가 컸습니다. 현재 모형의 머리·부분을 특정 가지와 일대일로 연결하지 않습니다."

    instances = support["instances"]
    label_groups: dict[str, list[dict]] = {}
    for row in instances:
        label_groups.setdefault(row["names"]["en"], []).append(row)
    if len(instances) != 195 or len(label_groups) != 98:
        raise ValueError(f"nerve support input drift: {len(instances)} surfaces / {len(label_groups)} label groups")
    concepts_by_source = {c.get("sourceNativeEnglishName"): c for c in graph["concepts"] if c.get("sourceNativeEnglishName")}
    concepts_by_name = {c["names"]["en"]: c for c in graph["concepts"]}
    relations_by_nerve: dict[str, list[dict]] = {}
    for row in graph["motorRelations"]:
        relations_by_nerve.setdefault(row["nerveKey"], []).append(row)
    groups = []
    for english_name, group in sorted(label_groups.items()):
        concept = concepts_by_source.get(english_name) or concepts_by_name.get(english_name)
        related = relations_by_nerve.get(concept["key"], []) if concept else []
        groups.append({
            "labelGroupEnglishName": english_name,
            "sourceSurfaceCount": len(group),
            "sourceInstanceIds": [row["id"] for row in group],
            "sides": sorted({row.get("side") for row in group if row.get("side")}),
            "graphConceptKey": concept["key"] if concept else None,
            "motorRelationStatus": "documented" if related else "not_linked",
            "sensoryCourseStatus": "documented" if concept and concept.get("functionEvidenceClass") == "sensory_course_documented_no_motor_relation" else "not_assessed",
            "functionEvidenceClass": concept.get("functionEvidenceClass", "unmapped_source_label") if concept else "unmapped_source_label",
            "relationIds": [row["relationId"] for row in related],
        })

    relation_sources = {
        "nerve-motor-deep-fibular-left": ["T61_EXISTING_EXACT_GEOMETRY"],
        "nerve-motor-deep-fibular-right": ["T61_EXISTING_EXACT_GEOMETRY"],
        "nerve-motor-dorsal-scapular-rhomboid-major": ["T66_DSN_2018"],
        "nerve-motor-dorsal-scapular-rhomboid-minor": ["T66_DSN_2018"],
        "nerve-motor-dorsal-scapular-levator-scapulae": ["T66_DSN_2018"],
    }
    for nerve_key, target, _, _, _, source_ids in CONCEPT_LINKS:
        safe_nerve = nerve_key.removeprefix("nerve-source-")
        target_slug = target.lower().replace(" ", "-")
        relation_sources[f"nerve-motor-{safe_nerve}-{target_slug}"] = source_ids
    relation_rows = []
    muscle_by_key = {row["sourceKey"]: row for row in muscles}
    for row in graph["motorRelations"]:
        is_exact = row["basis"] == "exact_geometry_motor_relation"
        source_ids = relation_sources.get(row["relationId"], [])
        relation_rows.append({
            "relationId": row["relationId"],
            "nerveKey": row["nerveKey"],
            "targetEnglishConcept": row.get("targetEnglishConcept"),
            "targetSourceKeys": row["targetSourceKeys"],
            "targetSides": sorted({muscle_by_key[key].get("side") for key in row["targetSourceKeys"]}),
            "basis": row["basis"],
            "scope": row["scope"],
            "displayLimit": row["displayNote"],
            "sourceIds": source_ids,
            "identityLimit": "existing exact same-side geometry relation; limited to this source instance" if is_exact else "literature relation does not establish a source nerve-branch-to-muscle-mesh coordinate binding",
            "displayNoteSha256": hashlib.sha256(row["displayNote"].encode()).hexdigest(),
        })
    learner_fields = {}
    field_sources = {
        ("Posterior femoral cutaneous nerve", "courseContext"): ["T66_PFCN_2020"],
        ("Posterior femoral cutaneous nerve", "functionContext"): ["T66_PFCN_2020"],
        ("Posterior femoral cutaneous nerve", "variationContext"): ["T66_PFCN_2020"],
        ("Femoral nerve", "functionContext"): ["T66_RF_2019"],
        ("Lateral pectoral nerve", "functionContext"): ["T66_PECTORAL_2011"],
        ("Medial pectoral nerve", "functionContext"): ["T66_PECTORAL_2011"],
        ("Intercostal nerves", "courseContext"): ["T66_RA_2008"],
        ("Intercostal nerves", "functionContext"): ["T66_INTERCOSTAL_ABDOMINAL_1992", "T66_RA_2008", "T66_EAO_1985"],
        ("Radial nerve", "functionContext"): ["T66_RADIAL_2020"],
        ("Median nerve", "functionContext"): ["T66_MEDIAN_2020"],
    }
    for (name, field), source_ids in field_sources.items():
        learner_fields[f"{name}:{field}"] = {
            "valueSha256": hashlib.sha256(course[name][field].encode()).hexdigest(),
            "sourceIds": source_ids,
            "scope": "paraphrased field summary; not a source quotation",
        }
    supported_by_source: dict[str, dict[str, dict[str, set[str]]]] = {}
    for relation in relation_rows:
        for source_id in relation["sourceIds"]:
            entry = supported_by_source.setdefault(source_id, {}).setdefault(relation["nerveKey"], {"relationIds": set(), "fields": set()})
            entry["relationIds"].add(relation["relationId"])
    for (name, field), source_ids in field_sources.items():
        concept = concepts_by_name.get(name)
        if not concept:
            continue
        for source_id in source_ids:
            supported_by_source.setdefault(source_id, {}).setdefault(concept["key"], {"relationIds": set(), "fields": set()})["fields"].add(field)
    for source_id, record in SOURCES.items():
        record["supports"] = [
            {"conceptKey": concept_key, "relationIds": sorted(values["relationIds"]), "fields": sorted(values["fields"])}
            for concept_key, values in sorted(supported_by_source.get(source_id, {}).items())
        ]
    ledger = {
        "schemaVersion": "t66-nerve-learning-evidence-v1",
        "recordedAt": "2026-10-05",
        "sourceSnapshot": {
            "nerveSupportSha256": sha(SUPPORT_PATH),
            "zaIntegrationSha256": sha(INTEGRATION_PATH),
            "learnerGraphSeedSha256": sha(GRAPH_SEED_PATH),
            "nerveCourseSeedSha256": sha(COURSE_SEED_PATH),
        },
        "denominators": {"staticSourceSurfaces": len(instances), "uniqueSourceLabelGroups": len(label_groups), "independentAnatomyConceptCount": "not inferred from label groups"},
        "preservedPolicy": {"sourceOnly": True, "localSelection": "verified_geometry_only", "humanReview": "not_performed", "publicRedistribution": "held", "newCanonicalBindings": 0, "newNerveGeometry": 0, "newBranchCoordinates": 0},
        "sourceRecords": SOURCES,
        "relationSummary": {
            "exactGeometryMotorRows": sum(row["basis"] == "exact_geometry_motor_relation" for row in graph["motorRelations"]),
            "literatureConceptRows": sum(row["basis"] == "literature_concept_motor_relation" for row in graph["motorRelations"]),
            "totalRows": len(graph["motorRelations"]),
            "uniqueNerveConceptKeys": len({row["nerveKey"] for row in graph["motorRelations"]}),
            "uniqueTargetSourceKeys": len({key for row in graph["motorRelations"] for key in row["targetSourceKeys"]}),
        },
        "relations": relation_rows,
        "labelGroupDisposition": groups,
        "learnerFieldEvidence": learner_fields,
    }
    generated = {
        GRAPH_PATH: json.dumps(graph, ensure_ascii=False, indent=2) + "\n",
        COURSE_PATH: json.dumps(course, ensure_ascii=False, indent=2) + "\n",
        EVIDENCE_DIR / "nerve-relation-ledger.json": json.dumps(ledger, ensure_ascii=False, indent=2) + "\n",
    }
    if check:
        mismatches = [str(path.relative_to(ROOT)) for path, content in generated.items()
                      if not path.exists() or path.read_text() != content]
        if mismatches:
            raise SystemExit("generated T66 nerve outputs differ: " + ", ".join(mismatches))
        print("T66 nerve projection check passed")
    else:
        for path, content in generated.items():
            path.write_text(content)
    print(json.dumps(ledger["relationSummary"], ensure_ascii=False))
    print(f"surface groups: {len(instances)} / {len(label_groups)}; mapped groups: {sum(row['graphConceptKey'] is not None for row in groups)}")


if __name__ == "__main__":
    main()
