# 진행 상태 — HUMAN ATLAS

- LAST_UPDATED: 2026-09-26
- PLAN_REVISION: T13-audit-next-plan-2026-09-26 (T13b 분리 공간자료 저장·검증·overlay)
- CURRENT_TASK: T13b — technical pass, synthetic browser fixture only; 상위 T13 표면 검토는 미완
- NEXT_TASK: T13c-B01 — 비복근 외측두 대퇴골 기시 한 항목의 근거 기반 draft 검토 (not_started)
- LAST_REPORT: work/reports/T13b.md
- CATALOG: partial85 (individual48/group16/part21); 전신 분모 미동결
- LEARNING_OVERLAY: names81; B01 field evidence57 + B02 50 + B03 50 + B04 50 + B05 51 + B06 60 + B07 67 + B08 56 + B09 48; canonical coverage 85/85 checked_with_gaps (partial catalog only); humanReviewed=false
- GEOMETRY: 오른쪽 종아리6근육, 근육메시7+뼈13(기존4+T13 9). canonical 우측 instance6/meshAsset20/근육 meshMapping7; 구조 mesh는 근육 mapping 제외. spatialAnnotation0
- FUNCTION_AND_ASSESSMENT: 미구현, 학습 탭은 준비 중
- TECHNICAL_GATE: T12b 11 mesh 보존; T13 9개 뼈 파생 GLB와 20 mesh 브라우저 로드, T05 부착 41개 중 뼈 검색 28/대상 mesh 보류 13, 실제 surface 0; T13b spatial draft schema/ref/claim-hash/side/frame/unit/pose/topology gate; spatial 8/8, annotation 12/12, search 38/38, T03 fixtures 17/17, production build 및 learner read-only synthetic-overlay browser check 통과
- ANATOMY_GATE: needs_human_review; 전신 구조 완성 아님
- DEV_URL: http://127.0.0.1:5174/ (이번 세션 서버; 재시작 시 사용 가능 포트 확인)

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
| T10 | technical_pass_content_partial | work/reports/T10.md; work/evidence/T10/; 학습 UI/검색/개정 task명세 | 전체 용어·전신3D·부착면·사람검토 미완 |
| T11-B01 | complete_with_gaps | work/tasks/T11-B01.md; atlas-data/terminology/term-review-batches.json; work/evidence/T11/; work/reports/T11-B01.md | 8/85 canonical terms web-checked with gaps; 77 pending; lookup splenius records not canonical; human anatomy review not performed |
| T11-B02 | complete_with_gaps | work/tasks/T11-B02.md; 10 group IDs; `atlas-data/terminology/term-review-batches.json`; `work/evidence/T11/B02/`; `work/reports/T11-B02.md` | Korean labels 7/10; TA2 PDF visual/column audit, KMLE exact source editions, conflicts, and human review remain open |
| T11-B03 | complete_with_gaps | work/tasks/T11-B03.md; 10 existing IDs; `atlas-data/terminology/term-review-batches.json`; `work/evidence/T11/B03/`; `work/reports/T11-B03.md` | Korean group labels 3/6 withheld; TA2 PDF visual/column audit and human review remain open |
| T11-B04 | complete_with_gaps | `work/tasks/T11-B04.md`; 10 existing IDs; 50 field evidence rows; 10 overlays/9 source Hanja; `work/evidence/T11/B04/`; `work/reports/T11-B04.md` | M16 Hanja withheld; TA2 PDF visual/column audit, KMLE underlying editions, and human review remain open |
| T11-B05 | complete_with_gaps | `work/tasks/T11-B05.md`; 10 existing IDs; 51 field evidence rows (50 required + 1 preserved alias); 9 new overlays/1 existing overlay enriched; `work/evidence/T11/B05/`; `work/reports/T11-B05.md` | TA2 visual layout review, KMLE underlying editions, and human review remain open |
| T11-B06 | complete_with_gaps | `work/tasks/T11-B06.md`; 10 existing IDs; 60 field evidence rows (50 required + 10 sourced aliases); 10 overlays; `work/evidence/T11/B06/`; `work/reports/T11-B06.md` | TA2 visual layout review, KMLE underlying editions, one Hanja gap, and human review remain open |
| T11-B07 | complete_with_gaps | `work/tasks/T11-B07.md`; 10 existing IDs; 67 field evidence rows (50 required + 17 sourced aliases); 8 new overlays/2 prior part overlays enriched; `work/evidence/T11/B07/`; `work/reports/T11-B07.md` | 4 source Hanja adopted; 6 Hanja and 3 part Korean fields remain missing/held; TA2 visual layout, KMLE exact editions, and human review remain open |
| T11-B08 | complete_with_gaps | `work/tasks/T11-B08.md`; 10 existing IDs; 56 field evidence rows (50 core + 6 sourced aliases); 10 overlays; `work/evidence/T11/B08/`; `work/reports/T11-B08.md` | all 10 part Hanja and P4–P8 current Korean fields remain missing; TA2 visual audit, exact KMLE editions, and human review remain open |
| T11-B09 | complete_with_gaps | `work/tasks/T11-B09.md`; 7 existing IDs; 48 field evidence; `work/evidence/T11/B09/`; `work/reports/T11-B09.md` | P16 full Korean and all 7 part-specific Hanja missing; TA2 visual audit, KMLE exact editions, human review remain open |
| T12a | technical_pass | work/reports/T12.md; work/evidence/T12/engine-decision.md; equivalence.json | 브라우저 픽셀/입력 회귀는 T12b |
| T12b | technical_pass_with_anatomy_review_pending | Three.js 어댑터; canonical geometry bridge; work/evidence/T12/; work/reports/T12.md | talus 구조 ID/뼈 mapping 제외, mesh identity·부착면 사람 검토 필요 |
| T13 | technical_partial_surface_review_pending | 뼈 OBJ 9개·파생 GLB; `attachment-context-t13.json`; `work/evidence/T13/`; `work/reports/T13.md` | 정확한 부착 표면 0/41; 적합한 대상 mesh 13개 보류; 사람 검토 없음. T14 미착수 |
| T13a | technical_pass | `work/tasks/T13a.md`; 학습 카메라·요약·선택 초기화; `work/evidence/T13a/`; `work/reports/T13a.md` | T13 표면 후보 0/41; 실제 draft와 사람 검토 미완 |
| T13b | technical_pass_test_fixture_only | `work/tasks/T13b.md`; 별도 spatial draft schema/validator·저장/import/export·learner overlay; `work/evidence/T13b/`; `work/reports/T13b.md` | 실제 source-backed surface draft 0/41, 사람 검토 0/41; 기존 T09 화면 draft 0개였고 raw localStorage hash는 미확인 |

## 실제 현재 상태와 원본 보존

학습 `/`와 제작 `/review`를 분리했다. `/review`는 개발 환경만 제공한다. 현재는 정적 앱이며 서버 인증 시스템이 아니다. 이름의 label은 출처에서 확인한 한글 관용명 우선이고 우리말/실제 한자/영어/라틴어는 같은 기존 이름 ID에 연결된다. 부분 canonical 85개와 lookup 2개가 검색에 잡히며, overlay는 81개다. T11-B01–B09 누적 통합검색은 38/38 통과했다. 이름이 있는 근육 부분도 learner search projection에 연결되어 있다.

T11 batch sequence는 **총 9개(B01–B09)** 다. B01은 canonical 8개와 lookup 후보 2개, B02–B08은 각 10개 canonical ID, B09는 7개 canonical ID다. B09를 마쳐 현재 partial catalog 85/85 항목을 checked-with-gaps로 기록했다. 이 85개는 전신 분모가 아니며 사람 해부학 검토나 T14 언어 gate가 완료된 것도 아니다. B01 판상근 lookup의 canonical 동결 절차도 별도 확인이 남는다.

OpenSim_Models는 읽기 전용이며 T13a/T13b 전후 HEAD/status가 동일하다. T13b는 보호된 canonical catalog, T12/T13 manifests, 기존 annotation schema, 기존 GLB를 수정하지 않았다. 기존 dirty working tree와 T13b 시작 전 diff는 보존 증거에 기록했다. T09 초안 화면은 0개였고 초기 hydration write를 건너뛰도록 했다. 이전 task의 기술 통과는 제품의 해부학/전신 완료가 아니다.

## 계속 유지할 차단 사항

- 전신 TA2/용어 출처 및 분모 동결 미완. T11 용어 검색을 웹 근거 overlay로 보완하되 canonical 검토로 위장하지 않는다.
- T07 provisional 근육 mapping은 canonical instance/meshMapping에 연결했다. talus 구조 ID는 미확정으로 명시적 제외했고 뼈4개 구조 mapping도 T03 계약상 제외했다. 사람 identity review는 남는다.
- T13에서 관련 대퇴골·발 뼈 9개를 출처 확인 후 보강했다. T05 부착 28개는 뼈 전체 검색만 가능하고 정확한 부착 표면은 0/41이다. 적합한 표적 mesh 13개는 보류 중이다. T13 실제 표면 판독/입력이 남아 있다.
- 역사적 Gray 요약의 현대 근거 대조와 사람이 확인한 구조 검토가 없다(T14).
- 기능/평가/퀴즈는 후속 계획이고 현재 구현된 것처럼 표시하지 않는다.

## 다음 실행

이번에 수행한 **T13b**는 별도 draft spatial layer와 `/review` 검증·교환·상태 경로, learner 읽기 전용 overlay를 연결했다. 1280×720 in-app browser에서 test-only 표면 fixture의 저장→새로고침→overlay 표시, 오류 거부·topology stale, 일반 learner 경로의 분리를 확인했다. typecheck, spatial/annotation/search regressions, T03 17 fixture, build, preservation 확인이 통과했다. 합성 도형은 test key에서 확인 후 지웠다. 실제 source-backed 표면 후보 0/41, 사람 표면 검토 0/41이고 T13은 technical partial 상태다. **다음 작업은 T13c-B01** 한 건이며 아래 프롬프트로 시작한다.

```text
HUMAN ATLAS 프로젝트에서 `AGENTS.md`, `work/STATUS.md`,
`work/reports/T13-AUDIT-NEXT-PLAN-2026-09-26.md`, `work/reports/T13b.md`,
`work/tasks/T13b.md`, `work/review-queue/attachment-surfaces-t13.md`,
T03 SpatialAnnotation 계약, T12 instance/mesh, T13 context manifest를 읽고
T13c-B01만 수행해라. 먼저 `work/tasks/T13c-B01.md`에 입력·수정범위·산출물·
합격 기준을 기록해라. 대상은 `HA-A-T05-GASTRO-LAT-FEMUR-ORIGIN`
(우측 비복근 외측두의 대퇴골 기시) 한 항목으로 제한한다. 원문 claim 외에
독립된 현대 해부학 근거를 확인하고, 현재 femur mesh를 다각도로 검토해
실제 근거가 뒷받침하는 표면 범위만 `/review` draft 공간자료 계층에 기록해라.
뼈 전체를 부착 영역으로 제출하거나 mesh 시각만으로 좌표를 추정하지 마라.
범위를 재현할 근거가 없으면 geometry를 비워두고 보류 사유를 남겨라.
source/instance/side/frame/unit/pose/asset/topology/hash 검증을 통과시키고
읽기 전용 learner overlay를 확인해라. 자동으로 `reviewed`로 승격하지 마라.
실제 데이터·GLB/OBJ·사용자 초안·OpenSim_Models를 보존하고 검증 결과·미완
항목·STATUS를 갱신한 뒤 멈춰라. 다음 T13c batch, T14 및 자동 배포,
환자 진단·치료·침 시뮬레이션은 시작하지 마라.
```
