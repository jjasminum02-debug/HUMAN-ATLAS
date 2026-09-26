# 진행 상태 — HUMAN ATLAS

- LAST_UPDATED: 2026-09-26
- PLAN_REVISION: R13-2026-09-26 — R12 유지 + AI 원문 대조/작용 설명/교육용 움직임/독립 T16–40
- CURRENT_TASK: T15a — complete_with_gaps; 한글 명칭 투영·검색·Hanja 노출/누락 처리 수정 완료
- NEXT_TASK: T15b — Sol High (not_started); T14b 사람검토는 별도 대기
- LAST_REPORT: work/reports/T15a.md
- CATALOG: partial85 (individual48/group16/part21); 전신 분모 미동결
- LEARNING_OVERLAY: names81; B01 field evidence57 + B02 50 + B03 50 + B04 50 + B05 51 + B06 60 + B07 67 + B08 56 + B09 48; canonical coverage 85/85 checked_with_gaps (partial catalog only); humanReviewed=false
- GEOMETRY: 오른쪽 종아리 6근육, 근육메시 7+뼈 13. canonical spatialAnnotation 0; T13c-B01/B02/B03 context_only geometry:null draft 3건 보존; T05 표면 후보 0/41, text_only 28/41, matching target mesh missing 13/41, human_review_pending 41/41
- FUNCTION_AND_ASSESSMENT: 미구현, 학습 탭은 준비 중
- TECHNICAL_GATE: T15a search 40/40, learning-content validator, typecheck, build, and actual learner/review browser checks passed. deltoid 4 name queries resolve HA-M-000030; Hanja query 0 results; browser visible Hanja 0. Canonical catalog and structure-summary hashes unchanged; OpenSim HEAD/status unchanged. T14b reviewer opinions 0, approval records 0; no anatomy promotion.
- ANATOMY_GATE: needs_human_review; 전신 구조 완성 아님
- DEV_URL: none (T15a temporary verification server stopped after browser verification)

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
| T13c-B01 | complete_with_geometry_held | `work/tasks/T13c-B01.md`; `work/evidence/T13c-B01/`; `work/reports/T13c-B01.md`; modern source + 1 context-only draft; browser save/reload/learner overlay | 외측과 뒤위쪽 영역의 독립 근거는 확인했지만 재현 가능한 triangle/coordinate boundary 미확보. B01 surface 0, 사람 승인 없음; raw localStorage hash는 브라우저 평가환경에서 미노출 |
| T13c-B02 | complete_with_geometry_held | `work/tasks/T13c-B02.md`; `work/evidence/T13c-B02/`; `work/reports/T13c-B02.md`; 우측 경골 외측과 기시 1건 context draft | 현대 근거는 넓은 외측과 기시를 지지하지만 FJ3387에 재현 가능한 footprint 경계 없음; surface 0, human review 0 |
| T13c-B03 | complete_with_geometry_held | `work/tasks/T13c-B03.md`; `work/evidence/T13c-B03/`; `work/reports/T13c-B03.md`; 우측 경골 몸통 가쪽면 기시 1건 context-only draft | Kimata 2022는 넓은 위치/종축 endpoint만 지지; FJ3387의 2D 경계/triangle 대응 없음. surface 0/41, 사람 검토 0/41; T14a 미착수 |
| T14a | complete_with_gaps | work/tasks/T14a.md; work/reports/T14a.md; work/evidence/T14a/; six pilot learner paths checked; source mapping/390px summary fixes | actual surface 0/41; text_only 28; missing target mesh 13; human review pending 41; modern sources not linked in learner panel. T14b state is tracked in its own row; T15 not started |
| T14b | needs_human_review | work/tasks/T14b.md; work/evidence/T14b/reviewer-packet.md + SHA manifest; work/evidence/T14b/; work/reports/T14b.md; Astra context brief | Six-item review packet is ready; actual qualified reviewer identity/date/opinions absent; no promotion; T15 not started |
| T15a | complete_with_gaps | work/reports/T15a.md; work/evidence/T15a/; three-name projection; source-backed deltoid aliases; learner/review Hanja filtering/redaction | Bone search and whole-catalog language completion are not implemented; T14b human anatomy approval still absent |

## 실제 현재 상태와 원본 보존

학습 `/`와 제작 `/review`를 분리했다. `/review`는 개발 환경만 제공한다. 현재는 정적 앱이며 서버 인증 시스템이 아니다. learner 명칭은 `koTraditional` → `koModern` → `en` 순이며, 실제 한자와 그 provenance는 원자료에 보존하고 learner 입력·검색·표시에서는 제외한다. 라틴어는 출처가 뒷받침하는 검색 보조어로 남긴다. 부분 canonical 85개와 lookup 2개가 검색에 잡히며, overlay는 81개다. T11-B01–B09 누적 통합검색은 38/38 통과했다. 이름이 있는 근육 부분도 learner search projection에 연결되어 있다.

T11 batch sequence는 **총 9개(B01–B09)** 다. B01은 canonical 8개와 lookup 후보 2개, B02–B08은 각 10개 canonical ID, B09는 7개 canonical ID다. B09를 마쳐 현재 partial catalog 85/85 항목을 checked-with-gaps로 기록했다. 이 85개는 전신 분모가 아니며 사람 해부학 검토나 T14 언어 gate가 완료된 것도 아니다. B01 판상근 lookup의 canonical 동결 절차도 별도 확인이 남는다.

OpenSim_Models는 읽기 전용이다. T14a 전후 HEAD d9b05d470b1a481c222372c85b75772faf8f7792 및 clean status가 동일하다. 보호 파일 32개(그중 GLB/OBJ 22개), canonical/T12/T13 파일과 T13c-B01/B02/B03 geometry-null draft의 해시가 전후 동일하다. 비교 evidence는 work/evidence/T14a/preservation-before.json 및 preservation-after.json이다. T09 localStorage 사용자 초안은 열거나 쓰기·가져오기·삭제하지 않았고, 브라우저 저장소 원시 키 해시는 읽지 않아 별도 해시 대조를 주장하지 않는다. 학습 원문 자료의 제한된 변경은 잘못된 이름 출처 연결을 바로잡은 learning-names overlay와 화면의 해당 locator 표시뿐이다. T14b packet/report 생성 중에도 canonical/data/model files와 기존 사용자 초안을 바꾸지 않았다. T14b 보호검사는 work/evidence/T14b/preservation.json에 있다. T15a 시작 HEAD는 `4452411d8a6f52e7a9aacfce003571d8ae53fb6b`; OpenSim은 HEAD `d9b05d470b1a481c222372c85b75772faf8f7792`, clean status가 유지됐다. T15a는 canonical catalog/structure summaries를 수정하지 않았고, 기존 learning-names overlay의 원문 Hanja·sourceIds·근거 locator를 보존했다. `deltoids` 편의 alias만 추가했다. `/review`는 조회만 했고 저장/가져오기/삭제를 실행하지 않았다.

## 계속 유지할 차단 사항

- 전신 TA2/용어 출처 및 분모 동결 미완. T11 용어 검색을 웹 근거 overlay로 보완하되 canonical 검토로 위장하지 않는다.
- T07 provisional 근육 mapping은 canonical instance/meshMapping에 연결했다. talus 구조 ID는 미확정으로 명시적 제외했고 뼈4개 구조 mapping도 T03 계약상 제외했다. 사람 identity review는 남는다.
- T13에서 관련 대퇴골·발 뼈 9개를 출처 확인 후 보강했다. T05 부착 28개는 뼈 전체 검색만 가능하고 정확한 부착 표면은 0/41이다. 적합한 표적 mesh 13개는 보류 중이다. T13c-B01의 비복근 외측두 대퇴골 기시와 B02/B03의 전경골근 경골 외측과/몸통 가쪽면 기시는 독립 현대 근거를 확인했지만 재현 가능한 면 경계가 없어 모두 context-only로 유지한다. 실제 surface 후보는 여전히 0/41이다.
- T13c 근거/mesh 확인과 T14a의 현대 원문 대조는 사람 해부학 검토나 승인을 대신하지 않는다. T14b는 여섯 파일럿 review packet을 준비했으나 실제 reviewer identity/date/opinion은 0건이다. T14b는 needs_human_review로 대기하고 모든 T05 attachments는 human_review_pending이다.
- 기능/평가/퀴즈는 후속 계획이고 현재 구현된 것처럼 표시하지 않는다.

## T15a 결과 및 다음 실행

T15a는 overlay의 label/korean/english를 `koTraditional`/`koModern`/`en`으로 투영하고, 제품 제목은 삼각근 → 어깨세모근 → 영어 순으로 선택한다. 학습 화면에는 우리말명·한자어명(한글 표기)과 영어명을 표시한다. learner 검색 alias에서 Han script와 Hani 용어 행을 제외하고, 출처를 여는 경우 locator의 실제 한자는 `[출처 한자 생략]`으로 표시한다. 기존 원자료 `hanja`, field evidence, source IDs와 locator는 보존했다. deltoid의 `삼각근`, `어깨세모근`, `Deltoid`, `deltoids` 검색 선택은 동일한 `HA-M-000030`에 도착했다.

`T15a` 검증은 search 40/40, learning-content validator, typecheck, production build, learner 및 `/review` 실제 브라우저 확인을 통과했다. 브라우저에서 Hanja 검색은 0건, 보이는 실제 한자 문자는 0건, `표기 대조 중`은 0건이었다. 빌드에는 기존 대형 chunk 경고가 남았다. 브라우저 화면은 작업 당시 1280×720였고, T15a에서는 반응형 전신 장면이나 뼈 검색을 검증/완료로 주장하지 않는다.

T14b는 계속 `needs_human_review`다. 실제 사람 검토자 의견은 0이며 reviewed 승격은 없었다. 미완 사항은 전신 명칭 coverage/누락 한국어 용어, 뼈 검색, 전신 자산과 3D 장면, 해부학 검토다. 이 작업에서 새 명칭이나 해부학 사실을 추정하지 않았다.

다음 작업은 **T15b (Sol High)**다. 자동 시작하지 않는다. 붙여 넣을 프롬프트:

```text
HUMAN ATLAS에서 AGENTS.md, work/STATUS.md, design/2026-09-25-muscle-atlas/00-START-HERE.md,
같은 설계 폴더의 01/02/03/04 및 06-REGION12-MUSCLE-BONE-REVISION.md,
work/reports/R12-DESIGN-REVIEW-2026-09-26.md, work/tasks/T15b.md,
work/reports/T15a.md, work/evidence/T15a/와 실제 canonical/instance/mesh/draft 자료를 읽고
T15b만 수행해라. Sol High 수준으로 계약과 migration 범위를 설계·검증하되 T15c를 시작하지 마라.
먼저 T15b의 시작 HEAD와 기존 변경 기준선을 기록하고, product categories, many-to-many region membership,
StructureInstance, StructureMeshMapping, Selection, scene manifest의 schema/type/runtime validator와
migration/dry-run diff를 구현해라. 기존 canonical ID, 원분류, 사용자 변경, OpenSim_Models,
T13 spatial drafts, T14b needs_human_review 상태를 보존해라. 합성 내폐쇄근 다중소속 회귀는 test-only로 격리하고
실제 해부학 membership이나 새 부착 좌표를 추정하지 마라. 관련 테스트·typecheck·build를 실행하고,
필요한 브라우저 경로가 바뀌면 실제 브라우저로 검증해라. 작업 결과·검증·미완 사항·STATUS와 다음 T15c 프롬프트를
갱신한 뒤 task 소유 변경만 선별 커밋하고 해시·제외/잔여 변경을 남겨라. T15c 이상, 자동 배포, 경혈/Pro mode,
환자 진단·치료·침 시뮬레이션은 범위 밖이며 시작하지 마라.
```


## R13 설계 인계 — 2026-09-26

T15a의 실행 결과는 위 기록과 보고서를 유지한다. 다음 구현은 T15b/Sol High이며 T15b–g 순서는 바꾸지 않았다. T14b 사람 검토는 실제 의견이 없는 별도 대기 경로이고 모든 기본 문헌 설명의 표시 조건은 아니다. 기본 자료는 T16–18의 AI 출처 대조 계약과 작업으로 준비한다.

이후 실행은 07/08/09, work/task-registry-r13.json, 개정 T16–40 task 명세를 사용한다. 구 T16–24는 work/tasks/archive/R12-before-motion-roadmap에 보존했다. 새 계획은 아직 실행하지 않았다. 현재 두 GLB의 skin/animation/morph는 모두 0으로 확인했다. 앱의 움직임 기능이 완성됐다고 표시하지 않는다.

이번 설계 보고서: work/reports/R13-AI-MOTION-ROADMAP-2026-09-26.md. 현재용 T15b 프롬프트는 00-START-HERE.md와 work/evidence/2026-09-26-motion-roadmap/next-prompt.txt에 있다. 누적 체크포인트는 T15a 작업자의 저장/검증/커밋이 끝난 다음, 같은 checkout에 쓰는 다른 작업이 없을 때 수행한다.
