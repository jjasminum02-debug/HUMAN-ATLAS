# 진행 상태 — HUMAN ATLAS

- LAST_UPDATED: 2026-09-25
- CURRENT_PHASE: T08 정적 3D 선택·카메라 통합 완료; anatomy review는 대기
- CURRENT_TASK: 없음 (T08 구현·브라우저 상호작용 검증 완료; T07 crosswalk와 모든 anatomy claim은 needs_review)
- NEXT_TASK: T09 — 부착부 annotation 검토 도구
- LAST_REPORT: work/reports/T08.md
- SCOPE_REVISION: T01-policy-v1 (전신 부위와 집계 규칙 고정; canonical 전체 목록은 미동결)
- DATA_REVISION: T05-pilot-structure-text-v1 (6 muscles + 2 gastroc head parts; 54 structure terms, 41 attachments, 45 claims; all claims unreviewed)
- SCHEMA_REVISION: T03-atlas-schema-v1 (Draft 2020-12 schema + project validator)
- CATALOG_REVISION: T04-partial-catalog-v1 (85 indexed row items; 48 individual, 16 groups, 21 parts; whole-body denominator null)
- TECHNICAL_GATE: T03 schema/fixture/dataset checks, T05 structure/provenance/coverage checks, T06 type/build/basic browser checks, T07 GLB/source geometry/coordinate/repeatability checks, T08 type/build and browser selection/visibility/camera checks pass. Catalog remains partial; broader T13 end-to-end gate outstanding.
- CATALOG_GATE: BLOCKED — 원본 TA2 Part 2 PDF 미확보, 18 region 전수 추출·term column review 미완료, KAA source missing.
- ANATOMY_GATE: needs_human_review (T05 historical-source claims and T07 mesh identity/pose/attachment surfaces have no independent human review)
- ASSESSMENT_GATE: 미검토 (protocol/임상 타당성 검토 없음)

| task | 상태 | 산출물/보고서 | 차단 조건 |
|---|---|---|---|
| T00 | complete | work/tasks/T00.md; work/reports/T00.md | 없음 |
| T01 | complete | atlas-data/manifests/scope.json; atlas-data/sources/registry.json; work/review-queue/source-gaps.md; work/reports/T01.md | 후속 용어·내용·자산 검토 대기; T01 완료를 막지 않음 |
| T02 | complete | `atlas-data/manifests/assets.json`; 11 mesh subset; `work/evidence/T02/`; `work/reports/T02.md` | 해부학자 리뷰 및 공개 전 license 재확인은 후속 게이트 |
| T03 | complete | `atlas-data/schemas/`; validator; 17 synthetic fixtures; `work/reports/T03.md` | reviewer 신원 인증은 별도 시스템 필요 |
| T04 | complete_with_partial_catalog | `atlas-data/catalog/`; `work/review-queue/catalog-gaps.md`; `work/evidence/T04/`; `work/reports/T04.md` | 전체 catalog/분모 gate blocked; 공식 source binary·KAA 용어 source 미확보 |
| T05 | complete_with_unreviewed_claims_and_language_gaps | T05 terms, structures, attachments, claims, evidence; `work/review-queue/pilot-structure-gaps.md`; `work/reports/T05.md` | anatomy/human review, KAA terms, TA2 visual audit, variants remain open |
| T06 | complete_with_partial_catalog_and_review_pending | work/tasks/T06.md; atlas-web/; work/evidence/T06/; work/reports/T06.md | anatomy claim review, TA2 visual audit, Korean/Hanja source gaps |
| T07 | complete_with_anatomy_review_pending | `atlas-data/assets/derived-glb/bodyparts3d-r4-right-lower-leg/right-lower-leg.glb`; T07 manifest/crosswalk; `work/evidence/T07/`; `work/reports/T07.md` | talus internal ID missing; T03 anatomical instance/MeshMapping data absent; all mesh relations need human review |
| T08 | complete_with_anatomy_review_pending | `atlas-web/src/viewer/`; T08 browser evidence; `work/reports/T08.md` | T07 mesh crosswalk, anatomical identity, pose and attachment surfaces remain unreviewed; not a clinical or public release |

## 다음 직렬 작업

다음은 **T09 — 부착부 annotation 검토 도구**다. 여기서는 시작하지 않았다. T09는 검토 모드에서 point/polyline/surface patch를 만들고·편집하고·삭제하며 JSON import/export를 제공한다. annotation은 T05 부착 문장과 연결할 수 있지만 원본 GLB/OBJ를 고치지 않고 독립 overlay data로 보관한다. 먼저 synthetic fixture로 회전·확대 후 위치 유지, 재로딩, 좌우·asset revision mismatch 거부, topology 변경 시 stale 표시를 확인한다. 실제 파일럿 기시·정지 부착 표면 지정은 T10 범위로 남긴다.

> 작업 대상은 현재 폴더 아래 HUMAN ATLAS 프로젝트다. `design/2026-09-25-muscle-atlas/00-START-HERE.md`, `03-LUNA-SERIAL-RUNBOOK.md`, `work/STATUS.md`를 읽고 실행서의 T09만 수행해 줘. 상세 설계는 같은 폴더의 01, 02, 04와 T05/T08 작업·결과에서 확인해라. 검토 모드의 point/polyline/surface patch 생성·편집·삭제, annotation schema, JSON import/export를 구현해라. annotation은 T05 부착 문장과 연결할 수 있으나 원본 mesh를 변경하지 않는 overlay data여야 한다. 처음에는 synthetic fixture로 회전·확대 후 위치 고정, 재로딩 동일성, 좌우 및 asset revision mismatch 거부, topology revision 변경 시 stale 처리를 검증해라. 실제 파일럿 기시·정지 영역 매핑, anatomy `reviewed` 승격, 원본 OBJ/GLB/OpenSim 변경, 공개·자동 배포는 하지 마라. 기존 사용자 파일·지침과 T08 결과를 보존하고, 작업 명세·결과·검증·상태·다음 작업을 HUMAN ATLAS 안에 기록해라. 자동 배포, 환자 진단·치료·침 시뮬레이션은 범위 밖이다. T09만 완료한 뒤 다음 task ID와 붙여 넣을 프롬프트를 적고 멈춰라. 다음 task를 자동 시작하지 마라.

## 변경하지 말아야 할 경로

- `OpenSim_Models/`: 읽기 전용 원본 checkout, revision `d9b05d470b1a481c222372c85b75772faf8f7792`; T08 작업에서도 수정하지 않음
- `design/2026-09-25-muscle-atlas/`: 설계·템플릿 원본; T08 작업 전후 SHA-256 대조
- 기존 사용자 파일 및 지침: README, AGENTS 및 설계 파일 T08 작업 전후 보존 대조 수행

## 검토 대기

- TA2 Part 2는 공식 검색 색인의 일부 행만 구조화했다. PDF 바이너리/hash/화면 대조와 전신 inventory는 미확보다.
- Korean Anatomical Terminology primary file/current edition/locator와 Hanja correspondence는 미확보다.
- FIPAT 표의 term column role 및 Errata 전수 검토가 남아 있다.
- T02 BodyParts3D pilot link는 provisional; mesh identity·attachment·pose 사람 검토 및 공개 전 license 검토가 남아 있다.
- `reviewed` gate는 T03에서 evidence/hash 구조를 검사하지만 reviewer 실제 신원을 증명하지 않는다.
- T05 anatomy claims는 역사적 출처 summary다. T06 앱과 T08 viewer는 검토 대기 상태로 표시하며, 실제 사람 review·공개 배포·임상 적격성은 없다. WebGL canvas에서의 선택·렌더링은 mesh의 해부학적 동일성이나 부착 위치를 검증하지 않는다.
