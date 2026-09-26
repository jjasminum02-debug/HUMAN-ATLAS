"""Build the itemized, multi-view human review queue from the T13 context."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CONTEXT = ROOT / "atlas-data/manifests/attachment-context-t13.json"
CATALOG = ROOT / "atlas-data/catalog/canonical-catalog.json"
OUT = ROOT / "work/evidence/T13/review-packet.md"


def main() -> None:
    context = json.loads(CONTEXT.read_text())
    entities = json.loads(CATALOG.read_text())["entities"]
    claims = {row["id"]: row for row in entities["claims"]}
    concepts = {row["id"]: row for row in entities["muscleConcepts"]}
    structures = {row["id"]: row for row in entities["structures"]}
    nodes = {row["id"]: row for row in entities["meshAssets"]}
    assert len(context["records"]) == 41
    lines = [
        "# T13 사람 검토용 부착 표면 패킷",
        "",
        "상태: **검토 대상 목록**. 실제 부착 표면 패치, 선, 점은 0개다. 아래 `표면 후보`는 해당 뼈 전체의 *검색 대상*이며 부착면 위치나 범위를 나타내지 않는다.",
        "",
        "- 원문 경계: T05 Gray 1918 요약 claim, 모두 `needs_review`. 현대 독립 대조와 사람 해부학 검토 전이다.",
        "- 자산 경계: BodyParts3D Release 4.0 우측 정적 모델, 출처 구조 교차표는 후보. 뼈 형상이 원문의 세부 부착 위치를 자동 지정하지 않는다.",
        f"- 좌표: `{context['frameId']}`, 단위 `{context['units']}`, pose `{context['poseId']}`. T07/T13 GLB hash는 `attachment-context-t13.json`에 고정되어 있다.",
        "- 검토 절차: `/review`에서 근두·원문·대상 구조를 확인하고 뼈만 격리해 정면·후면·우측 측면 및 자유 회전을 각각 확인한다. 실제 면 범위를 삼각형 패치 또는 경계선으로 표시하고 T09 draft JSON의 asset hash·topology·pose·claim 증거를 재검증한다. 사람 검토 전 canonical SpatialAnnotation으로 승격하지 않는다.",
        "- 현재 실행 확인: 브라우저에서 세 카메라 프리셋, 대퇴골 단독 격리, 표면 pick, 임시 초안 저장·삭제가 동작했다. 항목별 다각도 해부학 판독은 수행하지 않았다.",
        "",
        "| 근육/근두 | 부착 | 대상 구조 | 표면 후보/상태 | 정면·후면·측면 판독 |",
        "|---|---|---|---|---|",
    ]
    for row in context["records"]:
        owner = concepts[row["ownerConceptId"]]
        target = structures[row["targetStructureId"]]
        if row["contextMeshAssetId"]:
            asset = nodes[row["contextMeshAssetId"]]
            surface = f"{row['contextMeshAssetId']} 뼈 전체 검색만; patch 미지정; `{asset['hash'][:12]}…`"
        else:
            surface = "대상 mesh 미확보; 보류"
        label = owner["id"]
        lines.append(f"| {label} | {row['role']} | {target['id']} | {surface} | 미실시 / 미실시 / 미실시 |")
    lines.extend(["", "## 원문별 판독 대기 항목", ""])
    for index, row in enumerate(context["records"], 1):
        claim = claims[row["descriptionClaimId"]]
        lines.extend([
            f"### {index}. {row['attachmentId']}", "",
            f"- 근육/근두: `{row['ownerConceptId']}`; 우측 instance `{row['instanceId']}`; 부착 `{row['role']}`.",
            f"- 대상: `{row['targetStructureId']}`; 뼈 `{row['targetBoneId'] or ('canonical ID 미확정 · source '+row['sourceBoneFileId'] if row['sourceBoneFileId'] else 'mesh 미확보')}`.",
            f"- T05 근거 문장: {claim['value']['summary']}",
            f"- claim `{row['descriptionClaimId']}`; evidence {', '.join('`'+item+'`' for item in row['claimEvidenceIds'])}.",
            f"- 표면 후보: `{row['contextMeshAssetId']}` 뼈 전체 검색 컨텍스트만. 삼각형 ID/범위는 없음." if row["contextMeshAssetId"] else "- 표면 후보: 없음. 해당 대상 mesh 미확보로 보류.",
            "- 검토 기록: 정면 [ ] 후면 [ ] 우측 측면 [ ] 자유 회전 [ ] 범위/다른 출처 [ ] 사람 검토 [ ].",
            "",
        ])
    OUT.write_text("\n".join(lines))
    print(json.dumps({"records": len(context["records"]), "path": str(OUT.relative_to(ROOT))}))


if __name__ == "__main__":
    main()
