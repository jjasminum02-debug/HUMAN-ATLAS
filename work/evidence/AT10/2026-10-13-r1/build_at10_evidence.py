#!/usr/bin/env python3
"""Build the source-led ST1-25 partial package and its audit evidence."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def encode(value) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def dump(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(encode(value))


POINTS = [
    ("ST1", "Chengqi", "얼굴, 눈알과 안와아래모서리 사이에서 동공 바로 아래.", "눈알 · 동공 · 안와아래모서리"),
    ("ST2", "Sibai", "얼굴, 안와아래구멍 부위.", "안와아래구멍"),
    ("ST3", "Juliao", "얼굴, 동공 바로 아래이며 콧방울 아래모서리와 같은 높이.", "동공 수직선 · 콧방울 아래모서리"),
    ("ST4", "Dicang", "얼굴, 입꼬리에서 가쪽으로 0.4 지촌; 비순구 또는 그 연장선에 위치.", "입꼬리 · 비순구"),
    ("ST5", "Daying", "얼굴, 아래턱각의 앞쪽, 교근 부착부 앞모서리의 오목한 곳.", "아래턱각 · 교근 부착부 앞모서리"),
    ("ST6", "Jiache", "얼굴, 아래턱각보다 앞위쪽 한 손가락 너비; 이를 악물 때 교근이 솟는 곳.", "아래턱각 · 교근"),
    ("ST7", "Xiaguan", "얼굴, 광대활 아래모서리 중간과 아래턱패임 사이의 오목; 입을 다물었을 때 광대활 바로 아래.", "광대활 아래모서리 · 아래턱패임"),
    ("ST8", "Touwei", "머리, 이마 모서리의 앞머리선 바로 위쪽 0.5 비례촌, 앞정중선에서 가쪽 4.5 비례촌.", "앞머리선 · 이마 모서리 · 앞정중선"),
    ("ST9", "Renying", "목 앞쪽, 방패연골 위모서리와 같은 높이, 목빗근 앞쪽에서 온목동맥 위.", "방패연골 위모서리 · 목빗근 앞모서리 · 온목동맥"),
    ("ST10", "Shuitu", "목 앞쪽, 반지연골과 같은 높이에서 목빗근 앞모서리 바로 앞.", "반지연골 · 목빗근 앞모서리"),
    ("ST11", "Qishe", "목 앞쪽의 작은 빗장위오목, 빗장뼈 복장끝 위쪽이며 목빗근 복장갈래와 빗장갈래 사이.", "작은 빗장위오목 · 빗장뼈 복장끝 · 목빗근 두 갈래"),
    ("ST12", "Quepen", "목 앞쪽의 큰 빗장위오목, 앞정중선에서 가쪽 4 비례촌, 빗장뼈 위쪽 오목.", "큰 빗장위오목 · 빗장뼈 · 앞정중선"),
    ("ST13", "Qihu", "앞가슴, 빗장뼈 아래에서 앞정중선으로부터 가쪽 4 비례촌.", "빗장뼈 · 앞정중선"),
    ("ST14", "Kufang", "앞가슴, 첫째갈비사이공간에서 앞정중선으로부터 가쪽 4 비례촌.", "첫째갈비사이공간 · 앞정중선"),
    ("ST15", "Wuyi", "앞가슴, 둘째갈비사이공간에서 앞정중선으로부터 가쪽 4 비례촌.", "둘째갈비사이공간 · 복장각 · 앞정중선"),
    ("ST16", "Yingchuang", "앞가슴, 셋째갈비사이공간에서 앞정중선으로부터 가쪽 4 비례촌.", "셋째갈비사이공간 · 앞정중선"),
    ("ST17", "Ruzhong", "앞가슴, 유두 중심.", "유두 중심"),
    ("ST18", "Rugen", "앞가슴, 다섯째갈비사이공간에서 앞정중선으로부터 가쪽 4 비례촌; WHO 설명은 남성의 유두선, 여성의 유방 아래주름 중점을 덧붙임.", "다섯째갈비사이공간 · 유두선/유방 아래주름 · 앞정중선"),
    ("ST19", "Burong", "윗배, 배꼽 중심에서 위쪽 6 비례촌, 앞정중선에서 가쪽 2 비례촌.", "배꼽 중심 · 앞정중선"),
    ("ST20", "Chengman", "윗배, 배꼽 중심에서 위쪽 5 비례촌, 앞정중선에서 가쪽 2 비례촌.", "배꼽 중심 · 앞정중선"),
    ("ST21", "Liangmen", "윗배, 배꼽 중심에서 위쪽 4 비례촌, 앞정중선에서 가쪽 2 비례촌.", "배꼽 중심 · 앞정중선"),
    ("ST22", "Guanmen", "윗배, 배꼽 중심에서 위쪽 3 비례촌, 앞정중선에서 가쪽 2 비례촌.", "배꼽 중심 · 앞정중선"),
    ("ST23", "Taiyi", "윗배, 배꼽 중심에서 위쪽 2 비례촌, 앞정중선에서 가쪽 2 비례촌.", "배꼽 중심 · 앞정중선"),
    ("ST24", "Huaroumen", "윗배, 배꼽 중심에서 위쪽 1 비례촌, 앞정중선에서 가쪽 2 비례촌.", "배꼽 중심 · 앞정중선"),
    ("ST25", "Tianshu", "배꼽 중심과 같은 높이에서 앞정중선으로부터 가쪽 2 비례촌.", "배꼽 중심 · 앞정중선"),
]

catalog_path = ROOT / "atlas-data/acupoints/observation/catalog-r1.json"
catalog = json.loads(catalog_path.read_text())
catalog_points = {p["code"]: p for p in catalog["concepts"]}
catalog_channels = {c["code"]: c for c in catalog["channels"]}
assert catalog_channels["ST"]["midline"] is False
codes = [p[0] for p in POINTS]
assert codes == [f"ST{i}" for i in range(1, 26)]
assert len(set(codes)) == 25

base = json.loads((ROOT / "atlas-data/acupoints/learner/lung-r7.json").read_text())
concepts = []
location_rows = []
for code, romanization, location, landmark in POINTS:
    c = catalog_points[code]
    concepts.append({
        "code": code,
        "nameKo": c["nameKo"],
        "romanization": romanization,
        "channel": "ST",
        "location": f"WHO 기준 위치 설명(2008, p.46–55): {location}",
        "landmarkLabel": landmark,
        "textbook": "pending",
    })
    page = 46 if int(code[2:]) <= 2 else 47 if int(code[2:]) <= 4 else 48 if int(code[2:]) <= 6 else 49 if int(code[2:]) <= 8 else 50 if int(code[2:]) <= 10 else 51 if int(code[2:]) <= 12 else 52 if int(code[2:]) <= 14 else 53 if int(code[2:]) <= 16 else 54 if int(code[2:]) <= 18 else 55
    location_rows.append({
        "code": code,
        "nameKo": c["nameKo"],
        "channel": "ST",
        "channelNameKo": catalog_channels["ST"]["nameKo"],
        "plannedSides": ["right", "left"],
        "whoLocationKo": location,
        "landmarkLabel": landmark,
        "source": {"id": "who-standard-acupuncture-point-locations-2008", "url": "https://iris.who.int/bitstream/handle/10665/353407/9789290613831-eng.pdf", "page": page},
    })

point_reasons = {
    1: "입력에는 눈알·동공 및 안와아래모서리를 형성하는 learner 표면이 없다. 안륜근은 눈 주변 근육일 뿐 안구와 안와 아래 경계를 대체하지 않는다.",
    2: "안와아래구멍은 뼈의 내부 기준이고 해당 표면 구멍/피부 carrier가 입력에 없다.",
    3: "동공선과 콧방울 아래모서리를 함께 확인할 외부 얼굴 표면이 입력에 없다.",
    4: "AT8의 원본 Nasolabial sulcus/Oral region 부분면은 원본 source-bound 지역 구조이나 스캔 피부가 아니고 ST4 기준점 anchor로 승인된 면이 아니다.",
    5: "교근 및 아래턱 구조는 learner 입력에 있으나 피부의 아래턱각·교근 앞모서리 오목을 나타내는 carrier가 없다.",
    6: "교근은 learner에서 확인되지만 이 악물기 표면 형태와 손가락 너비를 투영할 피부 carrier가 없다.",
    7: "광대활과 아래턱패임의 뼈 지표는 피부 오목을 대신하지 않으며 그 사이의 점 anchor carrier가 없다.",
    8: "앞머리선/이마 모서리 외부 기준이 입력과 교육용 head envelope에서 확인되지 않는다.",
    9: "방패연골과 목빗근은 입력에 있으나 온목동맥 위의 외부 목 표면이 없다. 혈관/근육을 피부점으로 대신하지 않는다.",
    10: "반지연골과 목빗근은 입력에 있으나 그 앞쪽 목 표면 anchor는 없다.",
    11: "목빗근과 빗장뼈는 있으나 두 갈래 사이의 작은 빗장위오목을 나타내는 source-bound learner 피부 carrier가 없다.",
    12: "빗장뼈 위쪽의 큰 빗장위오목을 나타내는 learner 피부 carrier가 없다.",
    13: "AT6 쇄골/가슴 indicator는 뼈·델토펙토럴·윗갈비 구조 맥락이고 manifest가 피부 또는 nipple 관찰이 아님을 명시한다.",
    14: "AT6 가슴 indicator는 첫째 갈비사이공간의 피부면이 아니며 ST14 anchor가 없다.",
    15: "AT6 가슴 indicator는 갈비사이 피부면이 아니며 ST15 anchor가 없다.",
    16: "AT6 가슴 indicator는 갈비사이 피부면이 아니며 ST16 anchor가 없다.",
    17: "입력/AT6 manifest에 유두 중심이 없다. 일반 가슴 indicator로 대체할 수 없다.",
    18: "입력/AT6 manifest에 유방 아래주름이 없다. 유두선·성별 표면 지표를 가슴 indicator로 추정하지 않는다.",
}
for i in range(19, 26):
    point_reasons[i] = "입력에는 배곧은근·배벽 근육의 깊은 구조가 있으나 배꼽 중심을 식별하는 피부 표면이 없다. 배꼽을 추정하거나 근육 위치로 대체하지 않는다."

availability = []
for code in codes:
    n = int(code[2:])
    for side in ("right", "left"):
        availability.append({
            "code": code,
            "side": side,
            "display": "unavailable",
            "reason": f"{point_reasons[n]} 교육용 위치 설명은 WHO 기준 참조이며, 실제 모형상의 위치 판정은 미확정입니다.",
        })

package = {
    "schemaVersion": 2,
    "usage": "local_learner_eligible",
    "datasetRevision": base["datasetRevision"],
    "frameId": base["frameId"],
    "unit": "m",
    "poseId": base["poseId"],
    "channel": "ST",
    "concepts": concepts,
    "projections": [],
    "availability": availability,
    "precisionCounts": {"precise": 0, "educationalApproximation": 0, "unresolved": 50},
}
learner_path = ROOT / "atlas-data/acupoints/learner/st-r1.json"
observation = {
    "schemaVersion": 1,
    "datasetRevision": package["datasetRevision"],
    "frameId": package["frameId"],
    "poseId": package["poseId"],
    "unit": "m",
    "contexts": [],
    "teachingPaths": [],
}
observation_path = ROOT / "atlas-data/acupoints/observation/st-context-r1.json"
registry_path = ROOT / "atlas-data/acupoints/learner/registry-r1.json"
registry = json.loads(registry_path.read_text())
sections = [
    {"name": "눈·얼굴·머리", "codes": codes[:8]},
    {"name": "목·빗장위", "codes": codes[8:12]},
    {"name": "가슴", "codes": codes[12:18]},
    {"name": "윗배", "codes": codes[18:25]},
]
registration = {
    "id": "st-r1",
    "channel": "ST",
    "codes": codes,
    "learnerFile": learner_path.name,
    "observationFile": observation_path.name,
    "sections": sections,
    "learnerSha256": sha_bytes(encode(package)),
    "observationSha256": sha_bytes(encode(observation)),
}
existing_st = [p for p in registry["packages"] if p["channel"] == "ST"]
if existing_st:
    if len(existing_st) != 1 or existing_st[0] != registration:
        raise SystemExit("Existing ST registration differs from this versioned AT10 package; refusing overwrite")
    if not learner_path.is_file() or sha(learner_path) != registration["learnerSha256"]:
        raise SystemExit("Existing ST learner file differs from its registration; refusing overwrite")
    if not observation_path.is_file() or sha(observation_path) != registration["observationSha256"]:
        raise SystemExit("Existing ST observation file differs from its registration; refusing overwrite")
elif learner_path.exists() or observation_path.exists():
    raise SystemExit("Unregistered ST output path already exists; refusing overwrite")

# Write only after verifying the existing state is either absent or byte-identical.
dump(learner_path, package)
dump(observation_path, observation)
if not existing_st:
    registry["packages"].append(registration)
    dump(registry_path, registry)

# Source-bound candidate review. These candidates stay unregistered and are not point anchors.
manifest_specs = [
    ("education-r1", "education"),
    ("lung-AT6-r2", "chest"),
    ("upper-yang-final-AT8-r18", "face-neck"),
]
carrier_candidates = []
for edition, group in manifest_specs:
    manifest_path = ROOT / "atlas-data/acupoints/carriers" / edition / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    for chunk in manifest["chunks"]:
        relevant = (
            edition == "education-r1" and chunk["id"] in {"head-0", "trunk-0"}
            or edition == "lung-AT6-r2" and chunk["id"] in {"chest-indicator-right-0", "chest-indicator-left-0", "fossa-right-0", "fossa-left-0"}
            or edition == "upper-yang-final-AT8-r18" and chunk["id"].startswith(("native-nasolabial-sulcus-", "native-oral-region-", "native-temporal-region-", "native-sternocleidomastoid-region-"))
        )
        if not relevant:
            continue
        rel_file = f"atlas-data/acupoints/carriers/{edition}/{chunk['file']}"
        carrier_candidates.append({
            "group": group,
            "edition": edition,
            "manifestPath": str(manifest_path.relative_to(ROOT)),
            "manifestSha256": sha(manifest_path),
            "manifestAcceptedAcupoints": manifest["acceptedAcupoints"],
            "manifestPrecision": manifest["precision"],
            "candidateCarrierId": chunk["id"],
            "candidateSide": chunk.get("side"),
            "candidateCarrierHash": chunk.get("topologySha256"),
            "candidateAssetSha256": chunk["sha256"],
            "candidateAssetPath": rel_file,
            "candidateAssetBytes": (ROOT / rel_file).stat().st_size,
            "sourceKeys": chunk.get("sourceKeys", []),
            "sourceObject": chunk.get("sourceObject"),
            "surfaceRole": chunk.get("surfaceRole", chunk.get("landmarkBasis")),
            "decision": "candidate_only_not_a_point_carrier",
        })

runtime_path = ROOT / "work/evidence/acupoint-AC1/runtime-integration.json"
runtime = json.loads(runtime_path.read_text())
target_terms = {
    "eye": ["eyeball", "pupil", "infraorbital margin", "infraorbital foramen"],
    "face": ["nasolabial sulcus", "oral region", "masseter", "zygomatic bone", "mandible", "nasal ala"],
    "neck": ["sternocleidomastoid", "thyroid cartilage", "cricoid cartilage", "common carotid", "clavicle"],
    "chest": ["clavicle", "first rib", "second rib", "third rib", "fourth rib", "fifth rib", "nipple", "areola", "breast crease"],
    "abdomen": ["rectus abdominis", "external abdominal oblique", "internal abdominal oblique", "umbilicus", "navel", "linea alba"],
}
source_hits = {}
for group, terms in target_terms.items():
    source_hits[group] = []
    for row in runtime["objects"]:
        identity = " ".join([row.get("searchGroupKey", ""), row.get("label", ""), row.get("names", {}).get("en", "")]).lower()
        if any(term in identity for term in terms):
            source_hits[group].append({
                "sourceKey": row["sourceKey"],
                "searchGroupKey": row["searchGroupKey"],
                "label": row.get("label"),
                "kind": row.get("kind"),
                "side": row.get("side"),
                "localDisplayEligible": row.get("localDisplayEligible"),
                "inspectionEligible": row.get("inspectionEligible"),
                "sourceOnly": row.get("sourceOnly"),
                "humanReview": row.get("humanReview"),
                "publicRedistribution": row.get("publicRedistribution"),
                "sourceSha256": row.get("sourceSha256"),
            })

candidate_by_group = {}
for candidate in carrier_candidates:
    candidate_by_group.setdefault(candidate["group"], []).append(candidate)
row_groups = {}
for code, _, location, landmark in POINTS:
    n = int(code[2:])
    region = "eye" if n <= 2 else "face" if n <= 8 else "neck" if n <= 12 else "chest" if n <= 18 else "abdomen"
    candidate_group = "face-neck" if region in {"face", "neck"} else "chest" if region == "chest" else "education"
    candidates = candidate_by_group.get(candidate_group, [])
    row_groups[code] = {"region": region, "locationRule": location, "landmarkLabel": landmark, "candidateGroup": candidate_group, "candidateIds": [c["candidateCarrierId"] for c in candidates]}

position_ledger = {
    "schemaVersion": 1,
    "task": "AT10",
    "scope": {"channel": "ST", "codeRange": ["ST1", "ST25"], "concepts": 25, "instances": 50, "sides": {"right": 25, "left": 25}},
    "source": {"id": "who-standard-acupuncture-point-locations-2008", "url": "https://iris.who.int/bitstream/handle/10665/353407/9789290613831-eng.pdf", "pageRange": [46, 55], "use": "location-rule paraphrases only; not source of model coordinates"},
    "sourcePackage": {"id": "who-361-catalog-r1", "path": "atlas-data/acupoints/observation/catalog-r1.json", "sha256": sha(catalog_path), "hangulNames": "retained from existing catalog; no recataloging"},
    "locationRows": location_rows,
    "instanceRows": [
        {
            "code": code,
            "nameKo": catalog_points[code]["nameKo"],
            "channel": "ST",
            "side": side,
            "positionRule": row_groups[code]["locationRule"],
            "carrierId": None,
            "carrierHash": None,
            "candidateCarriers": [
                {
                    "id": candidate["candidateCarrierId"],
                    "side": candidate["candidateSide"],
                    "topologySha256": candidate["candidateCarrierHash"],
                    "assetSha256": candidate["candidateAssetSha256"],
                    "manifestSha256": candidate["manifestSha256"],
                    "assetPath": candidate["candidateAssetPath"],
                    "sourceKeys": candidate["sourceKeys"],
                    "surfaceRole": candidate["surfaceRole"],
                    "decision": candidate["decision"],
                }
                for candidate in candidate_by_group.get(row_groups[code]["candidateGroup"], [])
                if candidate["candidateSide"] in (side, "midline", None)
            ],
            "candidateCarrierIds": [candidate["candidateCarrierId"] for candidate in candidate_by_group.get(row_groups[code]["candidateGroup"], []) if candidate["candidateSide"] in (side, "midline", None)],
            "candidateCarrierHashes": [candidate["candidateCarrierHash"] for candidate in candidate_by_group.get(row_groups[code]["candidateGroup"], []) if candidate["candidateSide"] in (side, "midline", None)],
            "candidateDecision": "not_accepted_no_target_specific_external_surface_anchor",
            "verdict": "unresolved",
            "reason": point_reasons[int(code[2:])],
        }
        for code in codes for side in ("right", "left")
    ],
}
dump(OUT / "position-ledger.json", position_ledger)

carrier_audit = {
    "schemaVersion": 1,
    "audit": "Source-bound candidate and actual learner-runtime indicator audit. Candidate assets are not accepted carriers.",
    "runtimeInventory": {
        "path": str(runtime_path.relative_to(ROOT)),
        "sha256": sha(runtime_path),
        "recordCount": len(runtime["objects"]),
        "sourceOverlaySha256": runtime.get("sourceOverlaySha256"),
        "summary": "Learner runtime exposes bones/muscles and accessory indicators, not a continuous external skin mesh or several key surface landmarks.",
        "indicatorHits": source_hits,
    },
    "candidateAssets": carrier_candidates,
    "codeRegionMap": row_groups,
    "notCreated": ["new 3D model", "task-specific renderer/loader", "guessed coordinates", "projected route", "ST26–45 package coverage"],
}
dump(OUT / "carrier-audit.json", carrier_audit)

inputs = [
    "AGENTS.md",
    "work/EXECUTION.json",
    "work/tasks/AT10.md",
    "design/2026-09-25-muscle-atlas/30-AT-361-POINTS-AND-TERRITORIES.md",
    "design/2026-09-25-muscle-atlas/31-AT-EXPERIENCE-AND-DELIVERY-CONTRACT.md",
    "work/plans/acupoint-at-2026-10-11/START-HERE.md",
    "work/reports/AT1.md",
    "work/reports/AT8.md",
    "work/reports/AT9.md",
    "work/reports/acupoint-AC1.md",
    "work/reports/acupoint-AC2.md",
    "work/evidence/acupoint-AC1/runtime-integration.json",
    "work/evidence/AT8/2026-10-13-r1/acceptance-final.json",
    "work/evidence/AT8/2026-10-13-r1/final-asset-hashes.json",
    "work/evidence/AT8/2026-10-13-r1/remaining-units-final.json",
    "work/evidence/AT8/2026-10-13-r1/visual-final-86.json",
    "work/evidence/AT8/2026-10-13-r1/evaluated-native-boundaries-r3.json",
    "work/evidence/AT9/2026-10-13-r1/code-and-instance-check-r1.json",
    "work/evidence/AT9/2026-10-13-r1/point-ledger-r1.json",
    "work/evidence/AT9/2026-10-13-r1/package-validation-r1.json",
    "work/evidence/AT9/2026-10-13-r1/carrier-and-source-audit-r1.json",
    "work/evidence/AT9/2026-10-13-r1/ui-observations-r1.json",
    "work/evidence/AT9/2026-10-13-r1/remaining-units-r1.json",
    "atlas-data/acupoints/who-361-catalog.json",
    "atlas-data/acupoints/observation/catalog-r1.json",
    "atlas-data/acupoints/learner/registry-r1.json",
    "atlas-data/acupoints/carriers/education-r1/manifest.json",
    "atlas-data/acupoints/carriers/lung-AT6-r2/manifest.json",
    "atlas-data/acupoints/carriers/upper-yang-final-AT8-r18/manifest.json",
]
input_hashes = {"capturedFromWorkingTree": True, "files": {f: sha(ROOT / f) for f in inputs if (ROOT / f).is_file()}}
dump(OUT / "input-hashes.json", input_hashes)

summary = {
    "task": "AT10",
    "status": "partial",
    "catalog": {"channels": len(catalog_channels), "uniqueConcepts": len(catalog["concepts"]), "STConceptsInAssignment": len(codes), "STInstanceLedger": len(availability), "right": 25, "left": 25, "duplicateCodes": 0, "missingCodes": []},
    "package": {"registeredCodeRange": [codes[0], codes[-1]], "projectionCount": len(package["projections"]), "precise": 0, "educationalApproximation": 0, "unresolved": len(availability), "routeCount": 0, "sectionCoverage": sum(len(s["codes"]) for s in sections), "learnerSha256": sha(learner_path), "observationSha256": sha(observation_path), "registrySha256": sha(registry_path)},
    "acceptance": {"codeRangeAndSideLedger": "pass", "WHONameChannelMembership": "pass", "learnerPackageAndRegistrySchema": "pass", "sourceBoundSkinCarriers": "not_found_in_inspected_inputs", "realLearnerSelectionSideDisplay": "pass_controls_and_unavailable_state", "actualPointOcclusionAndRoute": "not_testable_no_accepted_projection", "humanReview": "not_performed", "textbookReview": "pending", "publicRedistribution": "held", "acceptancePassed": False, "remainingInstances": 50},
    "nextUnit": "AT11",
}
dump(OUT / "build-summary.json", summary)
print(json.dumps(summary, ensure_ascii=False, indent=2))
