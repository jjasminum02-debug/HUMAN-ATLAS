#!/usr/bin/env python3
"""Build AT9's code/side audit and unavailable-only learner packages from frozen inputs."""
from __future__ import annotations

import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
RUN = Path(__file__).resolve().parent
CATALOG = ROOT / "atlas-data/acupoints/observation/catalog-r1.json"
CONTEXT = json.loads((ROOT / "atlas-data/acupoints/learner/li-r1.json").read_text())
FRAME = CONTEXT["frameId"]
POSE = CONTEXT["poseId"]
REVISION = CONTEXT["datasetRevision"]
CHANNELS = {
    "HT": {"file": "ht-r1.json", "obs": "ht-context-r1.bin", "id": "heart-r1"},
    "PC": {"file": "pc-r1.json", "obs": "pc-context-r1.bin", "id": "pericardium-r1"},
    "SI": {"file": "si-r1.json", "obs": "si-context-r1.bin", "id": "small-intestine-r1"},
}
WHO_URL = "https://iris.who.int/bitstream/handle/10665/353407/9789290613831-eng.pdf"
KMCRIC_URL = "https://m.kmcric.com/knowledge/acupoint/{channel}/{code}"

# Korean paraphrases of the standard point-location relationships. These are
# study references only; they do not create a model coordinate or approval.
POINTS = {
    "HT1": ("겨드랑오목의 중심, 위팔을 벌리고 팔꿈치를 굽힌 자세에서 확인하는 점.", "겨드랑오목·겨드랑동맥", "axilla"),
    "HT2": ("위팔 안쪽, HT1과 HT3 사이에서 팔꿈치주름보다 몸쪽 3 B-cun.", "위팔 안쪽·HT1/HT3 축", "upper-arm-medial"),
    "HT3": ("팔꿈치 안쪽주름, 안쪽위관절융기 앞쪽 오목한 곳.", "팔꿈치주름·안쪽위관절융기", "elbow-medial"),
    "HT4": ("손바닥쪽 아래팔, 자쪽손목굽힘근 힘줄의 노쪽에서 손목주름보다 몸쪽 1.5 B-cun.", "자쪽손목굽힘근 힘줄·손목주름", "forearm-palmar"),
    "HT5": ("손바닥쪽 아래팔, 자쪽손목굽힘근 힘줄의 노쪽에서 손목주름보다 몸쪽 1 B-cun.", "자쪽손목굽힘근 힘줄·손목주름", "forearm-palmar"),
    "HT6": ("손바닥쪽 아래팔, 자쪽손목굽힘근 힘줄의 노쪽에서 손목주름보다 몸쪽 0.5 B-cun.", "자쪽손목굽힘근 힘줄·손목주름", "forearm-palmar"),
    "HT7": ("손바닥쪽 손목주름, 자쪽손목굽힘근 힘줄의 노쪽·콩알뼈 몸쪽.", "자쪽손목굽힘근 힘줄·콩알뼈", "wrist-palmar"),
    "HT8": ("손바닥, 넷째·다섯째 손허리뼈 사이에서 다섯째 손허리손가락관절보다 몸쪽.", "손바닥·넷째/다섯째 손허리뼈·다섯째 MCP", "palm"),
    "HT9": ("새끼손가락 손톱뿌리의 노쪽 모서리에서 몸쪽 0.1 F-cun.", "새끼손가락 손톱뿌리 노쪽 모서리", "nail-fifth"),
    "PC1": ("앞가슴 넷째 갈비사이공간, 앞정중선에서 가쪽 5 B-cun.", "넷째 갈비사이공간·앞정중선", "chest"),
    "PC2": ("앞위팔의 위팔두갈래근 긴갈래와 짧은갈래 사이, 앞겨드랑주름보다 먼쪽 2 B-cun.", "위팔두갈래근 두 갈래·앞겨드랑주름", "upper-arm-anterior"),
    "PC3": ("팔꿈치 앞쪽주름, 위팔두갈래근 힘줄의 안쪽 오목한 곳.", "팔꿈치주름·위팔두갈래근 힘줄", "elbow-anterior"),
    "PC4": ("손바닥쪽 아래팔, 긴손바닥근과 노쪽손목굽힘근 힘줄 사이에서 손목주름보다 몸쪽 5 B-cun.", "긴손바닥근/노쪽손목굽힘근 힘줄", "forearm-palmar"),
    "PC5": ("손바닥쪽 아래팔, 두 힘줄 사이에서 손목주름보다 몸쪽 3 B-cun.", "긴손바닥근/노쪽손목굽힘근 힘줄", "forearm-palmar"),
    "PC6": ("손바닥쪽 아래팔, 두 힘줄 사이에서 손목주름보다 몸쪽 2 B-cun.", "긴손바닥근/노쪽손목굽힘근 힘줄", "forearm-palmar"),
    "PC7": ("손바닥쪽 손목주름 중점, 긴손바닥근과 노쪽손목굽힘근 힘줄 사이.", "손목주름·두 굽힘근 힘줄", "wrist-palmar"),
    "PC8": ("손바닥, 둘째·셋째 손허리뼈 사이에서 손허리손가락관절보다 몸쪽.", "손바닥·둘째/셋째 손허리뼈·MCP", "palm"),
    "PC9": ("가운데손가락 끝마디의 중심. 자료에 손톱뿌리 기준 대안이 함께 있어 대조가 필요함.", "가운데손가락 끝 패드 중심·손톱뿌리 대안", "nail-middle"),
    "SI1": ("새끼손가락 손톱뿌리의 자쪽 모서리에서 몸쪽 0.1 F-cun.", "새끼손가락 손톱뿌리 자쪽 모서리", "nail-fifth"),
    "SI2": ("새끼손가락 다섯째 손허리손가락관절 자쪽의 먼쪽 오목, 손바닥 주름의 적백육제.", "다섯째 MCP 자쪽·손바닥주름·적백육제", "mcp5-palmar"),
    "SI3": ("손등, 다섯째 손허리손가락관절 자쪽의 몸쪽 오목.", "다섯째 MCP 자쪽 몸쪽·손등 주름", "mcp5-dorsal"),
    "SI4": ("손목 뒤안쪽, 다섯째 손허리뼈 바닥과 삼각뼈 사이의 적백육제.", "다섯째 손허리뼈 바닥·삼각뼈·적백육제", "wrist-ulnar"),
    "SI5": ("손목 뒤안쪽, 삼각뼈와 자뼈붓돌기 사이의 오목.", "삼각뼈·자뼈붓돌기", "wrist-ulnar"),
    "SI6": ("손목 뒤쪽주름보다 몸쪽 1 B-cun, 자뼈머리의 노쪽.", "자뼈머리·손목뒤주름", "forearm-ulnar"),
    "SI7": ("아래팔 자쪽, 자뼈 안쪽모서리와 자쪽손목굽힘근 사이에서 손목주름보다 몸쪽 5 B-cun.", "자뼈 안쪽모서리·자쪽손목굽힘근", "forearm-ulnar"),
    "SI8": ("팔꿈치 뒤안쪽, 팔꿈치머리와 안쪽위관절융기 사이의 고랑.", "팔꿈치머리·안쪽위관절융기 고랑", "elbow-posteromedial"),
    "SI9": ("어깨관절 뒤아래쪽, 뒤겨드랑주름보다 몸쪽 1 B-cun.", "어깨관절·뒤겨드랑주름", "shoulder-posterior"),
    "SI10": ("뒤겨드랑주름 위쪽, 어깨뼈가시 아래의 오목.", "뒤겨드랑주름·어깨뼈가시", "shoulder-posterior"),
    "SI11": ("어깨뼈가시 중점과 아래각을 잇는 선의 아래쪽 1/3, 어깨뼈오목.", "어깨뼈가시 중점·아래각·어깨뼈오목", "scapula"),
    "SI12": ("어깨뼈가시 중점 바로 위의 가시위오목.", "어깨뼈가시 중점·가시위오목", "scapula"),
    "SI13": ("어깨뼈가시 안쪽끝 위, T2 가시돌기와 잇는 높이.", "어깨뼈가시 안쪽끝·T2", "scapula"),
    "SI14": ("T1 높이에서 뒤정중선 가쪽 3 B-cun, 어깨뼈가시 안쪽끝과 만나는 부위.", "T1·뒤정중선·어깨뼈가시 안쪽끝", "scapula"),
    "SI15": ("C7 높이에서 뒤정중선 가쪽 2 B-cun, 정중선과 어깨뼈 안쪽모서리 사이.", "C7·뒤정중선·어깨뼈 안쪽모서리", "scapula"),
    "SI16": ("목 앞가쪽, 위쪽 방패연골 높이에서 목빗근 뒤쪽.", "방패연골 높이·목빗근 뒤모서리", "neck"),
    "SI17": ("아래턱각 뒤쪽, 목빗근 앞쪽의 오목.", "아래턱각·목빗근 앞모서리", "neck"),
    "SI18": ("광대뼈 아래, 가쪽눈구석에서 아래로 내린 수직선.", "광대뼈·가쪽눈구석 수직선", "face"),
    "SI19": ("이주 앞면 중점과 아래턱관절돌기 사이의 오목; 입을 약간 연 자세 기준.", "이주·아래턱관절돌기·입 벌림 자세", "ear"),
}

REASONS = {
    "axilla": "기존 겨드랑오목 후보 면은 위치 규칙에 결합된 HT1의 겨드랑동맥/주름 지표가 없고, 화면에서 해당 instance를 선택해 확인한 근거가 없다.",
    "upper-arm-medial": "위팔 carrier는 구조 기반의 넓은 교육 envelope다. HT1–HT3의 안쪽 위팔 축/국소 표면 지표를 등록하지 않아 면을 선택할 근거가 없다.",
    "elbow-medial": "넓은 팔 carrier만 있고 안쪽위관절융기 앞·팔꿈치주름의 HT3 지표를 등록하지 않았다.",
    "forearm-palmar": "손목/팔 carrier는 기존 AT8의 특정 손등·뒤쪽/가쪽 기준이다. 손바닥쪽 힘줄·손목주름 지표를 이 면으로 대체하지 않는다.",
    "wrist-palmar": "손목 후보의 AT8 등록 범위가 HT/PC가 요구하는 손바닥쪽 힘줄·콩알뼈 기준을 입증하지 않는다.",
    "palm": "현재 runtime 등록 carrier에 해당 손바닥 주름·적백육제의 국소 surface가 없다. 손등 patch나 일반 손 envelope를 손바닥 위치로 바꾸지 않는다.",
    "nail-fifth": "다섯째 손가락의 원본 nail-fold 후보는 존재하지만 HT9/SI1의 해당 모서리를 잇는 point-local runtime indicator와 실제 point selection이 아직 없다. 손끝 패드는 미지원이다.",
    "chest": "가슴 carrier는 쇄골·갈비뼈 문맥의 teaching patch이며 넷째 갈비사이공간의 앞쪽 국소 피부 위치/가쪽 5 B-cun 등록이 없다.",
    "upper-arm-anterior": "위팔 envelope에 앞겨드랑주름과 위팔두갈래근 두 갈래 사이를 잇는 PC2 surface annotation이 없다.",
    "elbow-anterior": "팔 carrier에 앞쪽 팔꿈치주름과 위팔두갈래근 힘줄 안쪽의 PC3 국소 surface registration이 없다.",
    "nail-middle": "가운데손가락 패드 carrier/피부가 없고 중심 패드와 손톱뿌리 대안 중 어느 기준을 쓸지 위치 입력도 미확정이다.",
    "mcp5-palmar": "다섯째 MCP 손바닥 주름·적백육제를 담은 국소 carrier가 없다. 기존 MCP link는 검지 표본이며 새끼손가락 위치로 전용하지 않는다.",
    "mcp5-dorsal": "작은 손등 patch와 뼈 section은 있으나 SI3의 다섯째 MCP 자쪽 몸쪽 오목을 특정하는 registered surface landmark가 없다.",
    "wrist-ulnar": "기존 wrist link의 수용 위치 QA는 AT8의 손목/손등 기준이다. 자쪽 삼각뼈·자뼈붓돌기와 적백육제 위치로 대체하지 않는다.",
    "forearm-ulnar": "팔 envelope는 넓은 구조 면이다. 자뼈머리/안쪽모서리와 자쪽손목굽힘근 기준의 자쪽 면 연결이 등록되지 않았다.",
    "elbow-posteromedial": "팔꿈치 envelope에 팔꿈치머리와 안쪽위관절융기 사이 고랑을 특정하는 source-bound surface가 없다.",
    "shoulder-posterior": "기존 girdle patch는 좁은 어깨뼈가시/빗장뼈 구조 구간이며 뒤겨드랑주름 및 뒤쪽 어깨관절 면을 덮지 않는다. 넓은 팔/몸통 면으로 대체하지 않는다.",
    "scapula": "몸통 envelope와 좁은 girdle link는 어깨뼈가시/아래각의 문맥만 보여준다. 가시위·가시아래오목 등 개별 scapular location을 붙일 해부학 국소 표면 carrier가 없다.",
    "neck": "SCM/neck carrier의 일부 구조는 있지만 SI16/SI17의 각 연골 높이·아래턱각 앞뒤 관계에 대한 target-specific point registration이 없다.",
    "face": "머리 전체 envelope와 코입술고랑 patch는 광대뼈 아래의 SI18 위치를 입증하지 않는다. 코·귀 등 다른 면으로 대체하지 않는다.",
    "ear": "auricular region carrier는 존재하지만 SI19의 이주 앞면 중점·아래턱관절돌기 사이 관계와 입을 약간 연 자세는 등록/재현하지 않았다. 기존 TE 귀 점을 그대로 승인하지 않는다.",
}

GROUP_CANDIDATES = {
    "axilla": [("lung-AT6-r2", "fossa-{side}-0")],
    "upper-arm-medial": [("education-r1", "arm-{side}-1")],
    "elbow-medial": [("education-r1", "arm-{side}-1")],
    "forearm-palmar": [("education-r1", "arm-{side}-0"), ("lung-AT6-r2", "wrist-link-{side}-0")],
    "wrist-palmar": [("lung-AT6-r2", "wrist-link-{side}-0")],
    "palm": [("education-r1", "hand-{side}-0"), ("upper-yang-final-AT8-r18", "hand-link-{side}-0")],
    "nail-fifth": [("education-r1", "nail-fold-{side}-4-0"), ("education-r1", "nail-plate-{side}-4-0")],
    "chest": [("lung-AT6-r2", "chest-indicator-{side}-0")],
    "upper-arm-anterior": [("education-r1", "arm-{side}-1")],
    "elbow-anterior": [("education-r1", "arm-{side}-1")],
    "nail-middle": [("education-r1", "finger-{side}-3-0"), ("education-r1", "nail-fold-{side}-2-0")],
    "mcp5-palmar": [("education-r1", "finger-{side}-5-0"), ("upper-yang-final-AT8-r18", "mcp-link-{side}-0")],
    "mcp5-dorsal": [("upper-yang-final-AT8-r18", "native-dorsum-of-hand-{side}-0"), ("upper-yang-final-AT8-r18", "hand-link-{side}-0")],
    "wrist-ulnar": [("lung-AT6-r2", "wrist-link-{side}-0"), ("upper-yang-final-AT8-r18", "hand-link-{side}-0")],
    "forearm-ulnar": [("education-r1", "arm-{side}-0")],
    "elbow-posteromedial": [("education-r1", "arm-{side}-1")],
    "shoulder-posterior": [("education-r1", "arm-{side}-1"), ("upper-yang-final-AT8-r18", "girdle-link-0")],
    "scapula": [("education-r1", "trunk-2"), ("upper-yang-final-AT8-r18", "girdle-link-0")],
    "neck": [("upper-yang-final-AT8-r18", "native-sternocleidomastoid-region-{side}-0"), ("upper-yang-final-AT8-r18", "neck-link-0")],
    "face": [("education-r1", "head-0"), ("upper-yang-final-AT8-r18", "native-nasolabial-sulcus-{side}-0")],
    "ear": [("upper-yang-final-AT8-r18", "native-auricular-region-{side}-0")],
}


def dump(path: Path, value: object, pretty: bool = True) -> bytes:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(value, ensure_ascii=False, indent=2 if pretty else None, separators=None if pretty else (",", ":")) + "\n"
    raw = text.encode()
    path.write_bytes(raw)
    return raw


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def read_manifest(name: str) -> tuple[dict, Path, str]:
    path = ROOT / "atlas-data/acupoints/carriers" / name / "manifest.json"
    raw = path.read_bytes()
    return json.loads(raw), path, sha(raw)


def main() -> None:
    catalog_bytes = CATALOG.read_bytes()
    catalog = json.loads(catalog_bytes)
    catalog_by_code = {c["code"]: c for c in catalog["concepts"]}
    catalog_channels = {c["code"]: c for c in catalog["channels"]}
    expected = [f"HT{i}" for i in range(1, 10)] + [f"PC{i}" for i in range(1, 10)] + [f"SI{i}" for i in range(1, 20)]
    if len(expected) != 37 or len(set(expected)) != 37 or set(expected) != set(POINTS):
        raise SystemExit("AT9 fixed target mismatch")
    if sum(1 for c in catalog["channels"]) != 14 or len(catalog["concepts"]) != 361:
        raise SystemExit("WHO 361 catalog denominator mismatch")

    manifests = {}
    chunk_index = {}
    for name in ("education-r1", "lung-AT6-r2", "upper-yang-final-AT8-r18"):
        doc, path, manifest_sha = read_manifest(name)
        manifests[name] = {"path": str(path.relative_to(ROOT)), "sha256": manifest_sha, "revision": doc["revision"]}
        for chunk in doc["chunks"]:
            chunk_index[(name, chunk["id"])] = {**chunk, "manifest": name, "manifestSha256": manifest_sha}

    ledger = []
    candidate_missing = []
    for code in expected:
        detail, landmark, group = POINTS[code]
        concept = catalog_by_code[code]
        channel = concept["channel"]
        if channel != code.rstrip("0123456789"):
            raise SystemExit(f"channel/code mismatch: {code}")
        for side in ("right", "left"):
            candidates = []
            for edition, pattern in GROUP_CANDIDATES[group]:
                carrier_id = pattern.format(side=side)
                chunk = chunk_index.get((edition, carrier_id))
                if not chunk:
                    candidate_missing.append({"code": code, "side": side, "carrierId": carrier_id, "edition": edition})
                    continue
                candidates.append({
                    "carrierId": carrier_id,
                    "carrierRevision": chunk["revision"],
                    "carrierSide": chunk["side"],
                    "edition": edition,
                    "file": chunk["file"],
                    "binarySha256": chunk["sha256"],
                    "carrierHash": chunk["topologySha256"],
                    "manifest": manifests[edition]["path"],
                    "manifestSha256": chunk["manifestSha256"],
                    "fit": "candidate_only_not_registered_for_this_location",
                })
            if not candidates:
                raise SystemExit(f"no auditable carrier candidate for {code}:{side}")
            ledger.append({
                "code": code,
                "nameKo": concept["nameKo"],
                "channel": channel,
                "side": side,
                "sourceRuleKo": detail,
                "requiredIndicatorKo": landmark,
                "source": {
                    "id": f"who-kmcric-{code}",
                    "standard": "WHO Standard Acupuncture Point Locations in the Western Pacific Region, 2008/2009; Korean description cross-check",
                    "whoUrl": WHO_URL,
                    "kmcricUrl": KMCRIC_URL.format(channel=channel.lower(), code=code),
                    "rights": {"localObservation": "supported", "publicRedistribution": "held"},
                },
                "ruleKind": "source_landmark_relation_requires_registered_surface_and_landmark_address",
                "candidateCarrierId": candidates[0]["carrierId"],
                "carrierHash": candidates[0]["carrierHash"],
                "candidateCarriers": candidates,
                "verdict": "unresolved",
                "reason": REASONS[group],
                "precision": "unresolved",
                "professorReview": "not_performed",
                "publicRedistribution": "held",
                "positionCoordinate": None,
            })

    if candidate_missing:
        raise SystemExit("candidate carrier ids missing from pinned manifests: " + json.dumps(candidate_missing, ensure_ascii=False))

    registry_path = ROOT / "atlas-data/acupoints/learner/registry-r1.json"
    registry_raw_at_input = registry_path.read_bytes()
    start_input_hashes = json.loads((RUN / "start.json").read_text()).get("inputSha256", {})
    if start_input_hashes.get("atlas-data/acupoints/learner/registry-r1.json") != sha(registry_raw_at_input):
        raise SystemExit("learner registry does not match the AT9 start snapshot")
    registry = json.loads(registry_raw_at_input)
    before_existing = {p["id"]: p for p in registry["packages"]}
    additions = []
    for channel, names in CHANNELS.items():
        codes = [c for c in expected if c.startswith(channel)]
        sections = []
        current = []
        current_name = None
        for code in codes:
            _, _, group = POINTS[code]
            section_name = {
                "axilla": "겨드랑·위팔", "upper-arm-medial": "겨드랑·위팔", "upper-arm-anterior": "위팔·팔꿈치",
                "elbow-medial": "팔꿈치", "elbow-anterior": "위팔·팔꿈치", "forearm-palmar": "손목·아래팔",
                "wrist-palmar": "손목·아래팔", "palm": "손바닥", "nail-fifth": "손가락 끝", "nail-middle": "손가락 끝",
                "chest": "가슴", "mcp5-palmar": "손가락·손등", "mcp5-dorsal": "손가락·손등",
                "wrist-ulnar": "손목·아래팔", "forearm-ulnar": "손목·아래팔", "elbow-posteromedial": "팔꿈치·위팔",
                "shoulder-posterior": "어깨·견갑부", "scapula": "견갑부·등", "neck": "목", "face": "얼굴", "ear": "귀",
            }[group]
            if current_name is None:
                current_name = section_name
            if section_name != current_name:
                sections.append({"name": current_name, "codes": current})
                current_name, current = section_name, []
            current.append(code)
        if current:
            sections.append({"name": current_name, "codes": current})

        concepts = []
        for code in codes:
            detail, landmark, group = POINTS[code]
            concepts.append({
                "code": code,
                "nameKo": catalog_by_code[code]["nameKo"],
                "romanization": "",
                "channel": channel,
                "location": detail,
                "landmarkLabel": landmark,
                "textbook": "pending",
            })
        availability = []
        for code in codes:
            group = POINTS[code][2]
            for side in ("right", "left"):
                availability.append({"code": code, "side": side, "display": "unavailable", "reason": REASONS[group]})
        package = {
            "schemaVersion": 2,
            "usage": "local_learner_eligible",
            "datasetRevision": REVISION,
            "frameId": FRAME,
            "unit": "m",
            "poseId": POSE,
            "channel": channel,
            "concepts": concepts,
            "projections": [],
            "availability": availability,
            "precisionCounts": {"precise": 0, "educationalApproximation": 0, "unresolved": len(availability)},
        }
        raw_package = dump(ROOT / "atlas-data/acupoints/learner" / names["file"], package)
        obs = {
            "schemaVersion": 1,
            "datasetRevision": REVISION,
            "frameId": FRAME,
            "unit": "m",
            "poseId": POSE,
            "contexts": [],
            "teachingPaths": [],
        }
        raw_obs = (json.dumps(obs, ensure_ascii=False, separators=(",", ":")) + "\n").encode()
        encoded_obs = gzip.compress(raw_obs, mtime=0)
        (ROOT / "atlas-data/acupoints/observation" / names["obs"]).write_bytes(encoded_obs)
        registration = {
            "id": names["id"],
            "channel": channel,
            "codes": codes,
            "learnerFile": names["file"],
            "observationFile": names["obs"],
            "sections": sections,
            "learnerSha256": sha(raw_package),
            "observationSha256": sha(encoded_obs),
            "observationEncoding": "gzip",
        }
        additions.append(registration)

    registry["packages"] = [*registry["packages"], *additions]
    if before_existing != {p["id"]: p for p in registry["packages"] if p["id"] in before_existing}:
        raise SystemExit("pre-existing registry package changed")
    dump(registry_path, registry)

    manifest_index = {
        "schemaVersion": 1,
        "run": "2026-10-13-r1",
        "headAtStart": json.loads((RUN / "start.json").read_text()).get("startHead"),
        "targetCodes": expected,
        "concepts": len(expected),
        "instances": len(ledger),
        "uniqueCodes": len({r["code"] for r in ledger}),
        "sideCounts": {side: sum(r["side"] == side for r in ledger) for side in ("right", "left")},
        "verdictCounts": {"resolved": 0, "unresolved": len(ledger), "duplicate": 0, "missing": 0},
        "candidates": manifests,
        "packageRegistrations": additions,
        "existingRegistryPackagesPreserved": list(before_existing),
        "locationDataSource": {"who": WHO_URL, "kmcricTemplate": KMCRIC_URL},
        "pathSegments": 0,
        "note": "Source location relationships and candidate carrier hashes are recorded. No candidate is bound as a point projection; missing target-specific surface annotations stay unresolved.",
    }
    dump(RUN / "point-ledger-r1.json", {"schemaVersion": 1, "instances": ledger})
    dump(RUN / "carrier-and-source-audit-r1.json", manifest_index)

    codes_by_channel = {ch: [c["code"] for c in catalog["concepts"] if c["channel"] == ch] for ch in catalog_channels}
    expected_counts = {"LU": 11, "LI": 20, "ST": 45, "SP": 21, "HT": 9, "SI": 19, "BL": 67, "KI": 27, "PC": 9, "TE": 23, "GB": 44, "LR": 14, "CV": 24, "GV": 28}
    computed_counts = {ch: len(codes) for ch, codes in codes_by_channel.items()}
    if computed_counts != expected_counts or sum(computed_counts.values()) != 361:
        raise SystemExit("14-channel catalog count/range audit failed")
    if sum(1 for c in catalog["concepts"] if catalog_channels[c["channel"]]["midline"]) != 52:
        raise SystemExit("midline denominator mismatch")
    check = {
        "schemaVersion": 1,
        "catalogRevision": catalog["schemaVersion"],
        "channelCounts": computed_counts,
        "channelRanges": {ch: [codes[0], codes[-1]] for ch, codes in codes_by_channel.items()},
        "totalUniqueConcepts": len(catalog["concepts"]),
        "bilateralConcepts": 309,
        "midlineConcepts": 52,
        "targetConcepts": len(expected),
        "targetInstances": len(ledger),
        "targetCodesUnique": len(set(r["code"] for r in ledger)) == 37,
        "targetCodeSequenceMatchesPlan": expected == [f"HT{i}" for i in range(1, 10)] + [f"PC{i}" for i in range(1, 10)] + [f"SI{i}" for i in range(1, 20)],
        "rightInstances": sum(r["side"] == "right" for r in ledger),
        "leftInstances": sum(r["side"] == "left" for r in ledger),
        "midlineTargetInstances": sum(r["side"] == "midline" for r in ledger),
        "missingTargetCodes": sorted(set(expected) - {r["code"] for r in ledger}),
        "unexpectedTargetCodes": sorted({r["code"] for r in ledger} - set(expected)),
        "duplicateCodeSideKeys": [],
        "ac1Ac2Preserved": True,
        "allPositionalApprovals": False,
        "pathSegments": 0,
    }
    seen = set()
    duplicates = []
    for r in ledger:
        key = f"{r['code']}:{r['side']}"
        if key in seen:
            duplicates.append(key)
        seen.add(key)
    check["duplicateCodeSideKeys"] = duplicates
    check["catalogSchemaVersion"] = catalog["schemaVersion"]
    dump(RUN / "code-and-instance-check-r1.json", check)

    inputs = {
        "schemaVersion": 1,
        "headAtStart": json.loads((RUN / "start.json").read_text()).get("startHead"),
        "statusSnapshotSha256": json.loads((RUN / "start.json").read_text()).get("startStatusSha256"),
        "startingInputSha256": json.loads((RUN / "start.json").read_text()).get("inputSha256", {}),
        "files": {},
    }
    paths = [
        "AGENTS.md", "work/EXECUTION.json", "work/tasks/AT9.md",
        "work/plans/acupoint-at-2026-10-11/START-HERE.md", "work/plans/mv2-at-integrated-2026-10-12/START-HERE.md",
        "design/2026-09-25-muscle-atlas/30-AT-361-POINTS-AND-TERRITORIES.md",
        "design/2026-09-25-muscle-atlas/31-AT-EXPERIENCE-AND-DELIVERY-CONTRACT.md",
        "work/reports/AT5.md", "work/reports/AT6.md", "work/reports/AT7.md", "work/reports/AT8.md",
        "work/evidence/AT8/2026-10-13-r1/acceptance-final.json",
        "work/evidence/AT8/2026-10-13-r1/rules-r19.json",
        "work/evidence/AT8/2026-10-13-r1/visual-final-86.json",
        "atlas-data/acupoints/observation/catalog-r1.json",
        "atlas-web/src/viewer/acupoints/learningPackage.ts",
        "atlas-web/src/viewer/acupoints/learningRegistry.ts",
        "atlas-web/src/viewer/acupoints/anchorCompiler.ts",
        "atlas-web/src/viewer/acupoints/AcupunctureOverlay.ts",
        "atlas-web/src/viewer/acupoints/AcupointReview.tsx",
        "atlas-web/src/viewer/acupoints/tour.ts",
    ]
    for rel in paths:
        p = ROOT / rel
        if p.is_file():
            inputs["files"][rel] = sha(p.read_bytes())
    inputs["carrierManifests"] = manifests
    for rel, expected_hash in inputs["startingInputSha256"].items():
        p = ROOT / rel
        if rel == "atlas-data/acupoints/learner/registry-r1.json":
            continue  # This owned registry is checked against its pre-write bytes above.
        if p.is_file() and expected_hash and sha(p.read_bytes()) != expected_hash:
            raise SystemExit(f"frozen starting input changed before AT9 use: {rel}")
    dump(RUN / "frozen-input-hashes-r1.json", inputs)

    if len(ledger) != 74 or len(seen) != 74 or check["missingTargetCodes"] or check["unexpectedTargetCodes"] or duplicates:
        raise SystemExit("AT9 code/instance uniqueness audit failed")
    print(json.dumps({"concepts": len(expected), "instances": len(ledger), "allUnresolved": len(ledger), "registrations": [r["id"] for r in additions]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
