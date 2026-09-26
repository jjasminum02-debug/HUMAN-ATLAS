# 진행 상태 — HUMAN ATLAS

- LAST_UPDATED: 2026-09-25
- CURRENT_PHASE: T09 annotation draft 도구 기술 검증 완료; anatomy review는 대기
- CURRENT_TASK: T09 — 부착부 annotation 검토 도구 (완료; 브라우저 화면 캡처 파일은 보존되지 않음)
- NEXT_TASK: T10 — 실제 파일럿 기시·정지 매핑 (사용자 요청으로 아직 시작하지 않음)
- LAST_REPORT: work/reports/T09.md
- SCOPE_REVISION: T01-policy-v1 (전신 부위와 집계 규칙 고정; canonical 전체 목록은 미동결)
- DATA_REVISION: T05-pilot-structure-text-v1 (6 muscles + 2 gastroc head parts; 54 structure terms, 41 attachments, 45 claims; all claims unreviewed)
- SCHEMA_REVISION: T03-atlas-schema-v1 (Draft 2020-12 schema + project validator)
- CATALOG_REVISION: T04-partial-catalog-v1 (85 indexed row items; 48 individual, 16 groups, 21 parts; whole-body denominator null)
- TECHNICAL_GATE: T03 schema/fixture/dataset checks, T05 structure/provenance/coverage checks, T06 type/build/basic browser checks, T07 GLB/source geometry/coordinate/repeatability checks, T08 selection/camera checks, T09 draft schema/11 unit cases/build/browser interaction log pass. T09 screenshot binary was visually inspected in CUA but not saved after browser URL-policy rejection. Catalog remains partial; broader T13 end-to-end gate outstanding.
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
| T09 | complete_with_ui_log_screenshot_not_saved | `atlas-data/schemas/annotation-draft-exchange.schema.json`; `atlas-web/src/viewer/AnnotationWorkbench.tsx`; `work/evidence/T09/`; `work/reports/T09.md` | draft는 instance 미생성·미검토. 해부학적 좌표 채택·review 승격 없음 |

## 진행 중 작업

T09 검토 도구 구현과 기술 검증을 완료했다. 실제 T05 문장에 연결된 표면 입력은 브라우저 smoke test에서만 사용했고, 임시 초안 3개는 삭제 후 재접속에서 0개를 확인했다. 실제 부착면 후보 입력·해부학 확정은 수행하지 않았다. 화면 캡처는 CUA에서 육안 확인했지만 이미지 파일을 프로젝트에 저장하지 못한 제한이 `work/reports/T09.md`에 기록돼 있다.

## 변경하지 말아야 할 경로

- `OpenSim_Models/`: 읽기 전용 원본 checkout, revision `d9b05d470b1a481c222372c85b75772faf8f7792`; T09 전후 clean/hash 동일
- `design/2026-09-25-muscle-atlas/`: 설계·템플릿 원본; T09 전후 SHA-256 대조
- 기존 사용자 파일 및 지침: README, AGENTS 및 설계 파일 T09 전후 보존 대조 수행

## 검토 대기

- TA2 Part 2는 공식 검색 색인의 일부 행만 구조화했다. PDF 바이너리/hash/화면 대조와 전신 inventory는 미확보다.
- Korean Anatomical Terminology primary file/current edition/locator와 Hanja correspondence는 미확보다.
- FIPAT 표의 term column role 및 Errata 전수 검토가 남아 있다.
- T02 BodyParts3D pilot link는 provisional; mesh identity·attachment·pose 사람 검토 및 공개 전 license 검토가 남아 있다.
- `reviewed` gate는 T03에서 evidence/hash 구조를 검사하지만 reviewer 실제 신원을 증명하지 않는다.
- T05 anatomy claims는 역사적 출처 summary다. T06 앱과 T08 viewer는 검토 대기 상태로 표시하며, 실제 사람 review·공개 배포·임상 적격성은 없다. WebGL canvas에서의 선택·렌더링은 mesh의 해부학적 동일성이나 부착 위치를 검증하지 않는다.
- T09 draft는 현재 anatomical instances가 0개여서 canonical `SpatialAnnotation`이 아니며, 브라우저 저장은 해당 기기의 localStorage에만 둔다.

## 다음 작업 프롬프트 — T10

```text
작업 대상은 현재 폴더 아래의 HUMAN ATLAS 프로젝트다.

design/2026-09-25-muscle-atlas/00-START-HERE.md와
03-LUNA-SERIAL-RUNBOOK.md를 읽고, work/STATUS.md의 선행 조건과
T05/T09 명세·보고서·실제 데이터 및 T09 검증기를 확인해라.
실행서에 정의된 T10만 수행해라.

T05 근거 문장별로 파일럿 근육/근두의 부착 annotation 후보와 사람 검토용
정면·후면·측면 장면/목록을 만든다. 넓은 영역을 대표점 하나로 완료 처리하지
말고, 근거·좌우·mesh 대상·revision·pose·범위를 함께 남겨라. 자료가 연결되지
않거나 위치를 확인할 수 없으면 추측하지 말고 미확인으로 기록해라.

모든 후보는 needs_review/draft로 남기고 해부학적 검토 완료나 정답 상태로
승격하지 마라. 기존 OpenSim_Models는 읽기 전용이며 원본·사용자 파일·지침을
보존해라. T10 작업 명세·결과·검증·상태·다음 작업을 프로젝트 파일로 남겨라.
자동 배포, 환자 진단, 치료, 침 시뮬레이션은 범위 밖이다. T10만 마친 뒤 멈추고,
다음 task ID와 붙여 넣을 프롬프트만 안내해라.
```
