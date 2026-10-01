<!-- BEGIN GENERATED EXECUTION -->
# 현재 실행 — 단일 기준

- SOURCE_OF_TRUTH: work/EXECUTION.json
- PLAN_REVISION: app-completion-2026-10-01
- CURRENT_TASK: none recorded as running
- LAST_OBSERVED_TASK: T90 / accepted
- LEGACY_T104_OBSERVATION_AT_RESET: 감사 도중 T104 report/browser/performance evidence와 로컬커밋67d8b79가 확인됨. exact10 source 표면 기술 통합 passed_with_gaps, 전신/새학습binding 완료 아님. 과거 T105 handoff 대신 현재 전신베이스 queue T98 적용.
- NEXT_TASK: T65 / Luna Max
- NEXT_PROMPT: work/NEXT.md
- CURRENT_GOAL: 현재 지원 앱 통합 → 사용 감사/보완 → UI·실측 성능 완성. 전체 콘텐츠 completeness는 별도 보고. 이후 설명→신경→모션.
- HISTORY: 아래 기존 보고/상태와 work/evidence/*의 nextTask는 당시 snapshot이며 실행 지시가 아니다.
<!-- END GENERATED EXECUTION -->

# 진행 상태 — HUMAN ATLAS

- LAST_UPDATED: 2026-09-27
- HISTORICAL_PLAN_REVISION: R14-2026-09-27 — 구조·기능 우선; 실행 순서는 work/task-registry-r14.json
- HISTORICAL_CURRENT_TASK: T24 — blocked; T44 기반 오른쪽 발목 clip·설명용 경로의 기술 후보는 생성·검증했으나 사용자 요구인 원래 앞정강근 그래픽의 CTA 기반 연속 수축 시범은 미달. 초기 별도 모형 메인 전환은 되돌림.
- HISTORICAL_NEXT_TASK: T24 해결 작업 / Sol High. R14 후속 T25 / Luna Max는 T24 실제 합격 전 실행 금지.
- HISTORICAL_LAST_REPORT: work/reports/T24.md
- CATALOG: partial85 (individual48/group16/part21); 전신 분모 미동결
- LEARNING_OVERLAY: entries81; current canonical overlap 79/85, six group IDs lack overlay entries, two lookup-only IDs are extra; T11 B01-B09 field work covered the current partial catalog with gaps; humanReviewed=false. T42 bone-name overlay adds names/search for the 9 currently selectable bones; actual Hanja not collected; humanAnatomyReview=not_reviewed.
- AI_EVIDENCE_OVERLAY: T16 schema/types/validator/learner adapter + T18 origin/insertion rows 16 + T21 action/context rows 35; 14 legacy rows remain test-only preview; canonical human review unchanged; T21 claims remain source-derived and geometry absent
- GEOMETRY: 기존 오른쪽 종아리 6근육, 근육메시 7+뼈 13 및 9개 needs_review bone mapping 유지. T44는 OpenSim Gait2392의 별도 오른쪽 tibia/talus/foot/toes 정적 GLB 1개를 생성했고 BodyParts3D 장면과 좌표를 섞지 않음. canonical spatialAnnotation 0; T13c-B01/B02/B03 context_only geometry:null draft 3건 보존; T05 표면 후보 0/41, text_only 28/41, matching target mesh missing 13/41, human_review_pending 41/41
- FUNCTION_AND_ASSESSMENT: 기존 T21 pilot 6개 text action card와 T22/T23 player 유지. T44 joint/action과 별도로 T24 오른쪽 앞정강근 배측굴곡 action 1건, MotionDefinition 1건, MotionAsset/clip 기술 후보 1건(`candidate`) 등록. OpenSim 경로 길이 감소는 확인했지만 기존 BodyParts3D 근육 mesh 수축 형태나 메인 CTA 시범은 없음. 기존 양측 T21 action unmapped 및 사람 검토 대기 유지.
- TECHNICAL_GATE: T24 GLB source/output 재현 hash, 3자세 관절·endpoint·새 교차 0, 실제 로더/플레이어, schema/참조/source/타입검사/빌드, 격리 브라우저 렌더/재생 통과. 메인 학습 화면은 기존 그래픽으로 복원·콘솔 error/warn 0 확인. 사용자 요구의 메인 그래픽 연속 수축 시범은 blocked. 기존 T15g drift와 App >500 kB 경고 유지.
- ANATOMY_GATE: needs_human_review; 전신 구조 완성 아님
- DEV_URL: none (T24 제품 UI 전환을 되돌렸고 임시 localhost QA만 사용)

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
| T14b | needs_human_review | work/tasks/T14b.md; work/evidence/T14b/reviewer-packet.md + SHA manifest; work/evidence/T14b/; work/reports/T14b.md; Astra context brief | Six-item review packet is ready; actual qualified reviewer identity/date/opinions absent; no promotion; remains a separate human-review gate |
| T15a | complete_with_gaps | work/reports/T15a.md; work/evidence/T15a/; three-name projection; source-backed deltoid aliases; learner/review Hanja filtering/redaction | Bone search and whole-catalog language completion are not implemented; T14b human anatomy approval still absent |
| T15b | complete_with_gaps | `work/tasks/T15b.md`; `atlas-data/schemas/navigation.schema.json`; `atlas-data/navigation/`; `atlas-web/src/domain/navigation.ts`; `work/evidence/T15b/`; `work/reports/T15b.md` | Six leg product memberships only; 4 source meshes unbound; T13 model not merged into leg scene; learner UI and remaining memberships await T15c–g; no human review/attachment surface/motion |
| T15c | complete_with_gaps | `work/tasks/T15c.md`; learner 12-region navigation/list UI; typed/legacy route adapter; `work/evidence/T15c/`; `work/reports/T15c.md` | Only six leg memberships have source-backed scene/list entries; 11 categories have no assigned structures/scene; T15e scene lifecycle not started; no anatomy review/promotion |
| T15d | complete_with_gaps | `work/tasks/T15d.md`; typed bone route/card for 9 existing source-linked right pilot bones; `work/evidence/T15d/`; `work/reports/T15d.md` | 4 meshes remain unbound; English/Gray 1918 summaries only; no modern bone-name review or human anatomy approval; other scenes wait for later work |
| T15e | complete_with_gaps | `work/tasks/T15e.md`; 2 leg scene manifests, revision cache/abort/GPU cleanup, decoder build QA; `work/evidence/T15e/`; `work/reports/T15e.md` | 11 other regions lack scenes; numeric GPU memory and raw browser draft hash unavailable; T14b review and attachment surfaces remain open |
| T15f | complete_with_gaps | work/tasks/T15f.md; source-linked learner crosschecks for 14 summary rows; cache completion-capacity regression; work/evidence/T15f/; work/reports/T15f.md | 4 meshes unbound; surfaces 0/41; nine bone mappings needs_review/not_reviewed; T14b human review pending; global manifest counts tracked as separate FU01 |
| T15f-FU01 | not_started (backlog) | work/tasks/T15f-FU01.md; scene-scoped manifest validation migration plan | global canonical count checks must be separated before new regional runtime data |
| T15g | complete_with_gaps | work/tasks/T15g.md; partial whole-body inventory, 18-region candidate crosswalk, bounded expansion plan; work/evidence/T15g/; work/reports/T15g.md | authoritative whole-body denominator, missing concept IDs, per-concept product memberships, 11 regional scenes/assets, terminology and human review remain open; T15f-FU01 remains prerequisite before T33 runtime expansion |
| T16 | complete_with_gaps | work/tasks/T16.md; AI evidence schema/types/validator/learner adapter; empty production overlay; work/evidence/T16/; work/reports/T16.md | Actual field-by-field AI evidence rows remain unpopulated; legacy migration was preview-only; human review and whole-body denominator remain open |
| T17 | complete_with_gaps | work/tasks/T17.md; atlas-data/schemas/source-research-manifest.schema.json; atlas-data/sources/source_research.py; work/evidence/T17/; work/reports/T17.md | Tool is tested only with synthetic fixture data; no actual anatomy source was researched or written to production overlay |
| T18 | complete_with_gaps | work/tasks/T18.md; 16 field-level origin/insertion AI evidence rows; source comparison, learner citations and browser QA; work/evidence/T18/; work/reports/T18.md | fibularis longus origin conflict unresolved; name comparison not performed per T17 handoff; human review, exact surface, motion and external redistribution rights remain open |
| T19 | technical_pass | work/tasks/T19.md; focus fade/isolation/pick policy; mobile toolbar wrap; work/evidence/T19/; work/reports/T19.md | T18 source conflict, human anatomy review, exact surface geometry, motion and whole-body denominator remain unchanged |
| T20 | complete_with_gaps | work/tasks/T20.md; motion-learning schema/types/validator; empty production bundle; preview-only JointAction adapter; work/evidence/T20/; work/reports/T20.md | canonical joint IDs and source-backed action rows absent; real motion assets/playback and human review remain open |
| T21 | complete_with_gaps | `work/tasks/T21.md`; six source-linked calf action cards; `atlas-data/motion/motion-learning.json`; 35 AI evidence overlay rows; `work/evidence/T21/`; `work/reports/T21.md` | canonical joint ID/clip 0; contraction type unavailable; human anatomy review pending; no 3D motion; action summaries do not establish individual contribution or clinical guidance |
| T22 | complete_with_gaps | `work/tasks/T22.md`; animation GLTFLoader adapter; representation/source manifest schema and validator; `work/evidence/T22/`; `work/reports/T22.md` | canonical joint binding, MotionDefinition, compatible licensed clip, joint frame/pivot/pose range, real motion asset and human review remain unavailable; production assets 0 |
| T41 | passed | `work/tasks/T41.md`; loader/static-scene corrective; `work/evidence/T41/`; `work/reports/T41.md` | R2 수정 검증 통과; T23 의존 완료. 실제 관절 좌표·motion clip은 후속 T44/T24 |
| T23 | passed | `work/tasks/T23.md`; motion player/UI WIP; `work/evidence/T23/`; `work/reports/T23.md` | player 필수 상태·빈 자산 경계 통과. production MotionDefinition/MotionAsset 0건으로 실제 clip 재생은 미검증이며 T24 자산 경로에서 다룸; 다음 R14 task T42 |
| T42 | passed_with_gaps | `atlas-data/terminology/bone-name-overlay-t42.json`; 학습 카드/search 정리; `work/evidence/T42/`; `work/reports/T42.md` | 9 selectable bones와 6 calf learner paths 검증. KMLE 판본 미노출, 사람 해부학 검토 미수행, Korean landmark data 미확보라 해당 영문 표지는 UI에서 보류; 실제 clip 0은 요구대로 CTA disabled |
| T43 | passed_with_gaps | `work/review-queue/region-acquisition-matrix-t43.json/.md`; gaps/T32 input; `work/evidence/T43/`; `work/reports/T43.md` | 12부위 metadata 행과 공식 index/model 접근 경로 완료; T15g generator `--check`는 시작 입력과 기존 snapshot 간 drift로 실패. 분모·자산·사람 검토는 미완 |
| T44 | passed_with_gaps | `atlas-data/assets/derived-glb/opensim-gait2392-t44-right-ankle/`; canonical joint/action migration; `work/evidence/T44/`; `work/reports/T44.md` | 별도 OpenSim 정적 입력·원본 대응·렌더 검증 완료. 실제 clip/제품 UI 전환·사람 해부학 검토는 T24/T25 이후; BodyParts3D 교차 정합·FJ3385 ID는 보류 |
| T24 | blocked | `atlas-data/assets/motion/t24-right-tibialis-anterior/`; motion bundle/scene/scripts; `work/evidence/T24/`; `work/reports/T24.md` | 기술 clip은 있으나 원래 BodyParts3D 앞정강근 그래픽의 검증된 수축 변형·CTA 연속 재생 없음. 모델 간 정합 또는 coherent muscle surface input 필요; T25 gate 닫힘 |

## 실제 현재 상태와 원본 보존

학습 `/`와 제작 `/review`를 분리했다. `/review`는 개발 환경만 제공한다. 현재는 정적 앱이며 서버 인증 시스템이 아니다. learner 명칭은 `koTraditional` → `koModern` → `en` 순이며, 실제 한자와 그 provenance는 원자료에 보존하고 learner 입력·검색·표시에서는 제외한다. 라틴어는 출처가 뒷받침하는 검색 보조어로 남긴다. 부분 canonical 85개와 lookup 2개가 검색에 잡히며, overlay는 81개다. T11-B01–B09 누적 통합검색은 38/38 통과했다. 이름이 있는 근육 부분도 learner search projection에 연결되어 있다.

T11 batch sequence는 **총 9개(B01–B09)** 다. B01은 canonical 8개와 lookup 후보 2개, B02–B08은 각 10개 canonical ID, B09는 7개 canonical ID다. B09를 마쳐 현재 partial catalog 85/85 항목을 checked-with-gaps로 기록했다. 이 85개는 전신 분모가 아니며 사람 해부학 검토나 T14 언어 gate가 완료된 것도 아니다. B01 판상근 lookup의 canonical 동결 절차도 별도 확인이 남는다.

OpenSim_Models는 읽기 전용이다. T14a 전후 HEAD d9b05d470b1a481c222372c85b75772faf8f7792 및 clean status가 동일하다. 보호 파일 32개(그중 GLB/OBJ 22개), canonical/T12/T13 파일과 T13c-B01/B02/B03 geometry-null draft의 해시가 전후 동일하다. 비교 evidence는 work/evidence/T14a/preservation-before.json 및 preservation-after.json이다. T09 localStorage 사용자 초안은 열거나 쓰기·가져오기·삭제하지 않았고, 브라우저 저장소 원시 키 해시는 읽지 않아 별도 해시 대조를 주장하지 않는다. 학습 원문 자료의 제한된 변경은 잘못된 이름 출처 연결을 바로잡은 learning-names overlay와 화면의 해당 locator 표시뿐이다. T14b packet/report 생성 중에도 canonical/data/model files와 기존 사용자 초안을 바꾸지 않았다. T14b 보호검사는 work/evidence/T14b/preservation.json에 있다. T15a 시작 HEAD는 `4452411d8a6f52e7a9aacfce003571d8ae53fb6b`; OpenSim은 HEAD `d9b05d470b1a481c222372c85b75772faf8f7792`, clean status가 유지됐다. T15a는 canonical catalog/structure summaries를 수정하지 않았고, 기존 learning-names overlay의 원문 Hanja·sourceIds·근거 locator를 보존했다. `deltoids` 편의 alias만 추가했다. `/review`는 조회만 했고 저장/가져오기/삭제를 실행하지 않았다.

T15b 시작 HEAD는 `f3cef7031b2685d1d255d3e00e3ea4997cea6099`였다. `work/evidence/T15b/start-baseline.json`에는 기존 untracked 47개(이전 `before/` 스냅샷 두 폴더), canonical/T12/T13 입력 11개와 3D 자산 22개의 시작 hash, OpenSim HEAD/clean 상태를 기록했다. T15b는 canonical catalog, 원분류, 기존 GLB/OBJ, T13 공간 draft, `/review` localStorage를 읽거나 수정하지 않았다. 종료 대조는 `work/evidence/T15b/preservation-after.json`에 있다. 시작부터 있던 두 `before/` 폴더는 보존하고 커밋에서 제외한다.

## 계속 유지할 차단 사항

- 전신 TA2/용어 출처 및 분모 동결 미완. T11 용어 검색을 웹 근거 overlay로 보완하되 canonical 검토로 위장하지 않는다.
- T07 provisional 근육 mapping은 canonical instance/meshMapping에 연결했다. talus 구조 ID는 미확정으로 명시적 제외했고 뼈4개 구조 mapping도 T03 계약상 제외했다. 사람 identity review는 남는다.
- T13에서 관련 대퇴골·발 뼈 9개를 출처 확인 후 보강했다. T05 부착 28개는 뼈 전체 검색만 가능하고 정확한 부착 표면은 0/41이다. 적합한 표적 mesh 13개는 보류 중이다. T13c-B01의 비복근 외측두 대퇴골 기시와 B02/B03의 전경골근 경골 외측과/몸통 가쪽면 기시는 독립 현대 근거를 확인했지만 재현 가능한 면 경계가 없어 모두 context-only로 유지한다. 실제 surface 후보는 여전히 0/41이다.
- T13c 근거/mesh 확인과 T14a의 현대 원문 대조는 사람 해부학 검토나 승인을 대신하지 않는다. T14b는 여섯 파일럿 review packet을 준비했으나 실제 reviewer identity/date/opinion은 0건이다. T14b는 needs_human_review로 대기하고 모든 T05 attachments는 human_review_pending이다.
- 기능/평가/퀴즈는 후속 계획이고 현재 구현된 것처럼 표시하지 않는다.

## T15a 결과 (이력)

T15a는 overlay의 label/korean/english를 `koTraditional`/`koModern`/`en`으로 투영하고, 제품 제목은 삼각근 → 어깨세모근 → 영어 순으로 선택한다. 학습 화면에는 우리말명·한자어명(한글 표기)과 영어명을 표시한다. learner 검색 alias에서 Han script와 Hani 용어 행을 제외하고, 출처를 여는 경우 locator의 실제 한자는 `[출처 한자 생략]`으로 표시한다. 기존 원자료 `hanja`, field evidence, source IDs와 locator는 보존했다. deltoid의 `삼각근`, `어깨세모근`, `Deltoid`, `deltoids` 검색 선택은 동일한 `HA-M-000030`에 도착했다.

`T15a` 검증은 search 40/40, learning-content validator, typecheck, production build, learner 및 `/review` 실제 브라우저 확인을 통과했다. 브라우저에서 Hanja 검색은 0건, 보이는 실제 한자 문자는 0건, `표기 대조 중`은 0건이었다. 빌드에는 기존 대형 chunk 경고가 남았다. 브라우저 화면은 작업 당시 1280×720였고, T15a에서는 반응형 전신 장면이나 뼈 검색을 검증/완료로 주장하지 않는다.

T14b는 계속 `needs_human_review`다. 실제 사람 검토자 의견은 0이며 reviewed 승격은 없었다. 미완 사항은 전신 명칭 coverage/누락 한국어 용어, 뼈 검색, 전신 자산과 3D 장면, 해부학 검토다. 이 작업에서 새 명칭이나 해부학 사실을 추정하지 않았다.

T15a 당시 다음 작업은 T15b였다. 해당 과거 인계 프롬프트는 이력 보존용이며, 현재 다음 작업은 아래 T15b 결과 및 다음 실행을 따른다.

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


## T15b 결과 및 다음 실행 (과거 인계 기록)

이 섹션은 T15c 실행 전의 이력이다. T15c는 완료됐으며 현재 인계는 문서 끝의 T15c 결과 및 다음 실행 섹션을 따른다.

T15b는 `atlas-data/schemas/navigation.schema.json`, `atlas-data/navigation/atlas-navigation.json`, 재현 가능한 migration builder/validator, TypeScript navigation domain/route adapter와 회귀 테스트를 추가했다. 12개 제품 부위는 18개 source region+root와 분리되어 있다. product decision `T15b-D01`로 T12 파일럿에 실재하는 여섯 근육만 `leg`에 연결했다. 이는 해부학적 유일 소속이 아니다. 오른쪽 뼈 `StructureInstance` 9개와 `StructureMeshMapping` 9개는 기존 crosswalk를 새 별도 overlay로 옮기고 모두 `needs_review`/`not_reviewed`로 유지했다. canonical ID, 기존 근육 Instance/MeshMapping, 원분류는 변경하지 않았다.

유효 mesh asset 11개 중 현재 T12 종아리 partial scene에는 근육 7개 + 뼈 3개의 typed selectable binding과 미확정 talus context 1개가 있다. 다른 source model T13의 뼈 mesh를 임의로 합치지 않았다. talus `FJ3385`, 제2–4중족골 `FJ3353/3355/3357` 네 mesh는 canonical 전체뼈 ID가 확인되지 않아 계속 unbound context다.

소스 연결, 사람 해부학 검토, 정적 형태 후보, 부착 위치, 움직임은 각기 다른 상태로 기록했다. 이 task에서 AI 원문 독립 대조나 사람 review는 하지 않았고, 실제 spatialAnnotation/부착면/움직임 asset을 추가하지 않았다. 사람 검토는 0건이며 T14b는 `needs_human_review`로 계속 대기한다. T15c UI 및 나머지 region membership 입력은 미완이다.

검증: navigation Node 6/6 + Python 12/12; 기존 search 40/40, annotation 12/12, spatial-draft 8/8; T03 schema/dataset와 fixture 17/17; learning validator, typecheck, production build, migration `--dry-run/--check`, navigation provenance/frame/pose/hash validator, `git diff --check` 통과. 빌드에는 기존 대형 chunk (>500 kB) 경고가 있다. UI 파일을 바꾸지 않았으므로 실제 브라우저는 열지 않았다. 자세한 결과는 `work/evidence/T15b/`와 `work/reports/T15b.md`에 있다.

다음 task는 **T15c / Luna Max**이며 자동 시작하지 않는다. 붙여 넣을 프롬프트:

```text
HUMAN ATLAS에서 AGENTS.md, work/STATUS.md, work/tasks/T15c.md,
work/reports/T15b.md와 work/evidence/T15b/, design/2026-09-25-muscle-atlas/00-START-HERE.md,
같은 폴더의 01/02/03/04/06/07/08/09 및 현재 navigation data/domain 구현을 읽고
T15c만 수행해라. 담당은 Luna Max다.
12개 제품 부위 탐색과 구조 목록 UI를 구현하고 12개만 기본 메뉴로 표시해라.
T15b overlay에 있는 여섯 종아리 근육 membership만 출처와 함께 사용하고,
미할당 항목을 추정해 채우지 마라. 장면이 없는 부위는 준비 중/빈 자료 상태로 보여주고
현재 종아리를 다른 부위 장면처럼 표시하지 마라. typed selection·URL route·legacy muscle 링크,
뒤로/앞으로를 연결하되 T15d 뼈 정보 카드나 T15e 장면 수명관리는 당겨 구현하지 마라.
OpenSim_Models, canonical ID/원분류, 실제 자산, 사용자 변경과 T13 spatial drafts를 보존해라.
1440/1024/390 폭의 실제 브라우저에서 category switching, deep link, back/forward,
미지원 부위와 키보드/모바일 흐름을 검증해라. work/tasks/T15c.md의 완료 기준을 따르고
결과·검증·미완·STATUS·다음 T15d 프롬프트를 남긴 뒤 T15c 소유 변경만 선택해 로컬 커밋해라.
T15d 이상·자동 배포·경혈/Pro mode·환자 진단·치료·침 시뮬레이션은 시작하지 마라.
```

## R13 설계 인계 — 2026-09-26

T15a 및 T15b의 실행 결과는 위 기록과 각 보고서를 유지한다. 당시 다음 구현은 T15c/Luna Max였으며, T15c는 완료됐다. 현재 인계는 아래 T15c 결과를 따른다. T14b 사람 검토는 실제 의견이 없는 별도 대기 경로이고 모든 기본 문헌 설명의 표시 조건은 아니다. 기본 자료는 T16–18의 AI 출처 대조 계약과 작업으로 준비한다.

이후 실행은 07/08/09, work/task-registry-r13.json, 개정 T16–40 task 명세를 사용한다. 구 T16–24는 work/tasks/archive/R12-before-motion-roadmap에 보존했다. 새 계획은 아직 실행하지 않았다. 현재 두 GLB의 skin/animation/morph는 모두 0으로 확인했다. 앱의 움직임 기능이 완성됐다고 표시하지 않는다.

이번 설계 보고서: work/reports/R13-AI-MOTION-ROADMAP-2026-09-26.md. 과거 T15c 인계는 이 파일의 `T15b 결과 및 다음 실행` 섹션에 보존했다. 당시 다음 task는 T15d였고 현재 완료됐다. 누적 체크포인트는 별도 사용자 요청으로 수행한다.

## T15c 결과 및 다음 실행

T15c는 12개 product region 선택과 부위별 구조 목록을 learner `/`에 연결했다. 기본 category menu는 12개로 고정했고 category 아래 근군 메뉴는 만들지 않았다. 현재 product membership은 기존 T15b 오른쪽 종아리 pilot 여섯 근육뿐이다. 나머지 11개 부위는 미할당/자료 준비 상태이고 category 이름을 근거로 구조를 추정하지 않았다. 지원되지 않는 부위와 category-mismatch URL에서 calf viewer가 표시되지 않는다. typed `region/kind/id/side`와 `part`, legacy `?muscle=`, browser back/forward를 연결했다.

실제 browser 검증은 1440×900, 1024×768, 390×844에서 category switch, deep link, history, keyboard, mobile selector/list 및 빈 자료 흐름을 확인했다. 탐색 domain Node 10/10, navigation Python 12/12, search 40/40, annotation 12/12, spatial draft 8/8, learning validator, typecheck, build와 diff check가 통과했다. OpenSim_Models, canonical 원분류, 실제 mesh, T13 drafts와 기존 47개 미커밋 스냅샷은 보존했다. 빌드의 큰 chunk 경고는 남는다. T14b 사람 검토는 계속 `needs_human_review`다.

미완: 다른 category memberships와 장면, 뼈 카드, 장면 수명관리, 사람 해부학 검토. T15d 뼈 카드와 T15e loader를 당겨 구현하지 않았다. 자세한 결과와 evidence는 `work/reports/T15c.md`, `work/evidence/T15c/`에 있다.

당시 다음 task는 **T15d / Luna Max**였으며 현재 완료됐다. 아래는 T15d 실행 전 이력이다. 현재 handoff는 파일 끝의 T15d 결과 섹션을 따른다. 과거 붙여 넣기 프롬프트:

```text
HUMAN ATLAS에서 AGENTS.md, work/STATUS.md, work/tasks/T15d.md,
work/reports/T15c.md와 work/evidence/T15c/, work/tasks/T15c.md,
T15b navigation overlay/evidence, 기존 structure/catalog/asset manifests와 viewer selection 구현을 읽고
T15d만 수행해라. 먼저 시작 HEAD와 기존 사용자 변경 기준선을 기록해라.
T15b/T15c overlay에서 출처 및 안정 ID가 확인되는 종아리 pilot 뼈만 typed bone binding으로 연결하고,
미확정 mesh는 미매핑으로 유지해라. 뼈 정보 카드에 출처가 뒷받침하는 이름, 좌우, 주요 표지,
근거 있는 연결 근육만 표시해라. 근육→뼈→근육 선택, URL 및 카드 일치와 미매핑 클릭에서
이전 근육 카드 제거를 실제 브라우저로 검증해라. landmark와 whole-bone ID를 합치지 마라.
기존 사용자 초안·canonical ID/원분류·실제 자산·T13 spatial drafts·OpenSim_Models를 보존하고
사람 검토 없이 reviewed 승격이나 해부학 claim 추가를 하지 마라.
관련 테스트·typecheck·build·실제 브라우저를 검증하고 결과·미완·STATUS 및 다음 T15e 프롬프트를
남겨라. 검증한 T15d 소유 변경만 선별 로컬 커밋하고 해시·포함 범위·제외/잔여 변경을 보고해라.
T15e 이상·자동 배포·경혈/Pro mode·환자 진단·치료·침 시뮬레이션은 시작하지 마라.
```

## T15d 결과 및 다음 실행 — 2026-09-26

T15d는 기존 source/stable-ID가 확인된 우측 pilot 뼈 9개만 typed bone route와 learner card에 연결했다. 기존 T12/T13 navigation overlay는 그대로 두고 런타임에서 읽었다. Tibia, fibula, calcaneus는 T12 scene manifest의 기존 context crosswalk를, cuboid/femur/medial cuneiform/1st·5th metatarsal/navicular는 T13의 source crosswalk를 사용했다. 9개 모두 review state는 `needs_review`/`not_reviewed` 유지다. Talus 및 2–4번째 중족골 mesh 네 개는 unbound 그대로이며, 클릭하면 selection URL와 이전 근육 설명을 비우는 것을 실제 브라우저에서 확인했다. landmark ID는 whole-bone selection과 구분했다.

뼈 이름·landmark·연결 근육은 기존 source/evidence-backed catalog claim만 사용한다. 현재 카드에는 역사적 Gray 1918 영문 요약과 해당 source 링크가 표시되며 현대 독립 근거 검토, 한글 뼈명 원문 및 사람 검토/승인은 미완이다. T14b는 별도 `needs_human_review`다. canonical ID/원분류·asset·T13c spatial drafts·OpenSim_Models는 보존했고 `/review` localStorage는 건드리지 않았다.

검증: bone/navigation 집중 테스트 14/14, navigation Node/Python 12/12씩, search 40/40, annotations 12/12, spatial drafts 8/8, navigation validator, typecheck, build, `git diff --check` pass. 실제 learner browser에서 deep link/card 일치, muscle→bone→muscle, unbound talus click의 muscle-card 제거를 확인했고 신선한 브라우저 console error/warning은 0건이다. Production build는 기존 500 kB 초과 chunk warning이 있다. 상세 결과는 `work/reports/T15d.md`, 증거는 `work/evidence/T15d/`.

다음 task는 **T15e / Sol High (not_started)**다. scene-manifest loader와 cache/revision, 취소·늦은 응답, GPU release, frame/pose 및 typed selection/annotation 수명을 다룬다. 자동 진행하지 않는다. 붙여 넣을 프롬프트:

```text
HUMAN ATLAS에서 AGENTS.md, work/STATUS.md, work/tasks/T15e.md,
work/reports/T15d.md와 work/evidence/T15d/, work/tasks/T15d.md,
design/2026-09-25-muscle-atlas/00-START-HERE.md와 같은 설계 폴더의 01/02/03/04/06/07/08/09,
현재 scene manifests·viewer loader·typed selection 및 사용자 초안을 읽고 T15e만 수행해라.
담당 모델은 Sol High다. 먼저 시작 HEAD와 기존 사용자 변경 기준선을 기록하고 work/tasks/T15e.md에
실행 범위·산출물·합격 기준을 확인해라. 고정된 전역 T07/T13 로딩을 scene-manifest 기반 loader로 전환하고
공유 cache/revision, 취소·늦은 응답 폐기, GPU 자원 해제, frame/pose 일치 및 typed selection/URL/annotation
수명 규칙을 구현해라. 런타임 decoder 이중화 여부는 측정 근거로 결정해라.
부위 전환·로딩 실패·재선택·뒤로가기·resize·선택 초기화·없는 asset 회귀를 관련 테스트와 실제 브라우저에서
검증해라. 각 부위 scene만 로딩하고 서로 다른 모델 좌표를 섞지 마라.
OpenSim_Models, canonical ID/원분류, 기존 자산·사용자 초안·T13 spatial drafts, 현재 nine bone mappings와
그 needs_review 상태를 보존해라. 근육/뼈 claim이나 reviewed 승격을 추정하지 마라.
결과·검증·미완·보존 대조·STATUS와 다음 T15f 프롬프트를 남겨라. 검증한 T15e 소유 변경만 선별 로컬 커밋하고
hash/포함·제외·잔여 변경을 보고해라. T15f 이상, 배포, 환자 진단·치료, 경혈/Pro mode 및 침 시뮬레이션은
범위 밖이며 시작하지 마라.
```

## T15e 결과 및 다음 실행 — 2026-09-26

T15e는 기존 T12 leg scene을 유지하고 T13 뼈 9 mesh의 별도 같은 좌표계/pose leg scene을 manifest에 등록했다. 활성 부위의 scene만 가져오는 revision CPU cache·취소/늦은 응답 폐기·실패 재시도·GPU geometry/material/context 해제와 typed 선택/URL/annotation 수명을 연결했다. 이전 9개 뼈 mapping의 `needs_review`/`not_reviewed`, unbound 4개와 정확한 부착 표면 0/41은 그대로다. 런타임 이중 decoder는 측정 후 하나로 줄이고 독립 parser 동등성 검사를 build QA에 포함했다.

검증은 scene lifecycle 8/8, navigation Node/Python 14/14·12/12, search 40/40, annotation 12/12, spatial drafts 8/8, navigation schema/generator, decoder QA, typecheck/build pass. 실제 브라우저에서 부위 전환, 빠른 전환, 404 GLB 실패/복구, 재선택, 뒤로가기, 390/1024 resize, 선택 해제/새로고침 및 T13 femur 카드가 작동했다. 빈 부위 첫 진입의 잘못된 종아리 GLB 선요청은 수정 후 정적 서버 로그에서 0으로 확인했다. 정상 최종 탭 console error/warning 0, 기존 대형 chunk 경고는 남는다. 상세 결과는 `work/reports/T15e.md`, evidence는 `work/evidence/T15e/`.

OpenSim_Models, canonical ID/원분류, source manifest·GLB/OBJ, T13c spatial draft 3건과 시작 시점의 기존 스냅샷 47파일은 hash/상태 대조에서 보존됐다. 실제 브라우저 localStorage raw 사용자 초안 hash와 GPU 메모리 수치는 확보하지 못했으며 읽기/쓰기/삭제를 실행하지 않았다. T14b는 `needs_human_review` 별도 대기, 다른 11부위 scene 미확보다. T15f는 시작하지 않았다.

다음 task는 **T15f / Luna Max (not_started)**. 붙여 넣을 프롬프트는 `work/reports/T15e.md`의 끝부분에 있다. 자동 진행하지 않는다.

## T15f 결과 및 당시 T15g 인계 — 2026-09-26 (이력)

T15f 결과는 work/reports/T15f.md, evidence는 work/evidence/T15f/에 있다. scene cache 동시 완료 회귀, 6 muscle/9 bone learner 카드, 14개 기시·정지 summary 근거 비교 행을 검증했다. 실제 브라우저에서 요청된 isolate→clear→다른 근육→back→reset 순서의 URL/card/selection/isolation 상태가 일치했다. OpenSim_Models와 보호 대상 98개 데이터·자산, 48개 T13 공간자료/evidence, 시작부터 미커밋이던 47개 스냅샷은 시작 hash와 동일하다. OpenSim HEAD와 clean 상태도 유지했다. /review 및 localStorage 초안은 읽거나 쓰지 않았다.

T15f는 complete_with_gaps다. 표면 후보 0/41이며 4개 mesh는 unbound, 뼈 9개 mapping은 needs_review/not_reviewed, T14b 사람 해부학 검토는 계속 대기다. Build에는 기존 >500 kB chunk warning이 있다.

### 별도 후속 FU01

work/tasks/T15f-FU01.md는 not_started인 별도 backlog다. atlas-web/src/viewer/manifest.ts canonical 전체 개수 20/6/7 고정은 새 지역 canonical data가 들어올 때 종아리 검증을 깨뜨릴 수 있다. T07/T12 source-asset 고정 검증은 보존하면서 전체 catalog count와 scene별 검증을 분리하고, test-only 다른 지역 data 추가 후 종아리 invariant가 통과하는 회귀가 필요하다. FU01을 T15g 또는 T16으로 자동 합치지 않는다.

T15f 종료 당시 다음 serial task는 **T15g / Luna Max (not_started)**였다. 아래 prompt는 완료 전 이력이다.

    HUMAN ATLAS에서 AGENTS.md, work/STATUS.md, work/tasks/T15g.md,
    work/reports/T15f.md와 work/evidence/T15f/, work/tasks/T15f-FU01.md,
    design/2026-09-25-muscle-atlas/00-START-HERE.md 및 같은 폴더의 01/02/03/04/06/07/08/09,
    현재 canonical catalog, source crosswalk, navigation memberships, asset manifests를 읽고
    T15g만 수행해라. 담당은 Luna Max다.
    기존 catalog의 부분 분모와 누락 전신 항목을 대조해 근육·뼈 각각의 안정 ID inventory,
    다중 부위 membership, 출처, 기존 자산 가능 여부와 누락 자료를 기록하고 작업 배치 계획을 작성해라.
    전신 분모가 동결되지 않으면 coverage 백분율을 쓰지 말고 group/part/instance/mesh 수를 분리해라.
    미할당 구조 membership이나 mesh를 해부학적 추정으로 채우지 마라.
    이번 T15g는 inventory와 계획 범위다. 실제 새 부위 GLB/OBJ, 새 scene runtime binding,
    attachment/surface claim, 사람 검토 또는 T16은 시작하지 마라.
    T15f-FU01의 manifest.ts 전신 개수 고정과 scene별 검증 전환 요구를 의존성으로 표시해라.
    새 canonical data/scene 변경이 생기면 FU01 완료 전 runtime validation에 추가하지 말고,
    선행 의존성 결정을 T15g 산출물에 명시해라. T15g에서 FU01 구현을 당겨 하지 마라.
    OpenSim_Models, 원분류·canonical ID, 기존 GLB/OBJ, 사용자 변경, /review 초안과 T13 spatial drafts를 보존해라.
    task 명세·결과·검증·미완·STATUS와 다음 실행 프롬프트를 남겨라.
    확인된 T15g task 소유 변경만 선별 로컬 커밋하고 포함·제외·잔여 변경을 보고해라.
    push·배포·다음 task 자동 실행·경혈/Pro mode·환자 진단·치료·침 시뮬레이션은 하지 마라.

## T15g 결과 및 현재 인계 — 2026-09-26

T15g는 complete_with_gaps다. 허용된 inventory·source-region 후보 crosswalk·batch 계획 범위를 수행했다. machine-readable 출력은 `atlas-data/catalog/whole-body-inventory-t15g.json`, `work/review-queue/region-crosswalk-t15g.json`, `work/review-queue/expansion-batches-t15g.json`; 생성/검증 도구는 `atlas-data/catalog/build_t15g_inventory.py`다. 전체 분모와 누락 concept ID는 미동결/미확정이며 coverage percentage는 기록하지 않았다.

확인값: partial catalog 85 IDs(개별근 48/근군 16/부분 21), source rows 85; name overlay canonical overlap 79/85, missing group overlay 6, lookup-only 2; canonical bone IDs 10, scene-bound 9; 12 categories 중 현재 membership 6개(모두 종아리 근육), partial scene 2개(모두 종아리), 4 unbound context; local raw OBJ 20 및 scene GLB 2. source crosswalk는 partial이며 TA2 PDF 원문 visual audit는 미완이다. 실제 membership·canonical ID·asset·UI·attachment, 사람 검토와 motion을 추가하지 않았다.

T33 전 dependency: `T15f-FU01`의 `manifest.ts` 전체 개수 가정을 scene-scoped validation으로 전환해야 한다. 이는 T15g에서 구현하지 않은 별도 backlog이며 현재 T16을 막지는 않고 새 지역 runtime data 전에 확인한다. T14b 사람 검토는 계속 대기다.

검증: T15g planning regression 7/7, inventory generator/hash check, schema check, canonical dataset validator, typecheck, production build pass. Build는 기존 500 kB 초과 App chunk warning을 유지한다. UI 변경이 없어 실제 브라우저 검증은 해당 없음. 상세 command, hash preservation와 커밋 범위는 `work/reports/T15g.md` 및 `work/evidence/T15g/`에 기록한다.

다음 serial task는 **T16 / Sol High / planned_not_started**다. 다음 prompt:

```text
HUMAN ATLAS에서 AGENTS.md, work/STATUS.md, work/task-registry-r13.json,
design/2026-09-25-muscle-atlas/00-START-HERE.md 및 같은 폴더의 06/07/08/09,
work/tasks/T16.md, work/reports/T15g.md, work/evidence/T15g/,
atlas-data/catalog/whole-body-inventory-t15g.json,
work/review-queue/region-crosswalk-t15g.json와 실제 기존 evidence/review 자료를 읽고
오직 T16만 수행해라. 담당은 Sol High다.
필드별 AI evidence overlay와 학습 표시 정책을 schema/types/validator/adapter에 반영하되
기존 reviewed/human review 의미, canonical IDs, 사용자 초안과 source/hash를 보존해라.
cross_checked가 사람 승인을 만들지 않게 하고 single_source/conflicted/unavailable,
geometry 및 motion 상태를 서로 독립적으로 유지해라. 같은 원문을 재인용한 두 사이트 fixture,
충돌 필드, legacy migration과 ref/hash 검증을 추가해라.
T15g의 전신 denominator는 여전히 미동결이다. whole-body coverage를 완성으로 표시하거나
T32/T33/FU01을 당겨 실행하지 마라. OpenSim_Models와 기존 사용자 변경을 보존하고,
학습 화면에 내부 상태 코드나 제작 JSON을 노출하지 마라.
작업 기준선, 관련 테스트·typecheck·build 및 필요한 실제 브라우저 검증, 결과·미완·STATUS를
기록해라. 검증한 T16 소유 변경만 선별 로컬 커밋하고 hash/포함·제외/잔여 변경을 보고해라.
T17 이상·push·배포·경혈/Pro mode·환자 진단·치료·침 시뮬레이션은 시작하지 마라.
```

## T16 결과 및 현재 인계 — 2026-09-27

T16은 field-level AI evidence schema/types/validator/learner projection을 구현해 **complete_with_gaps**로 기록한다. production `ai-evidence-overlay.json`은 task 명세대로 빈 상태다. 14개 기존 legacy summary와 canonical claim/review/source/hash는 변경하지 않았고, 정확한 입력을 대상으로 만든 migration preview를 메모리에서 검증했다. cross-check는 독립 underlying work를 요구하며 사람 해부학 검토·3D 위치 검토와 분리된다. conflicted 값은 대안으로 표시하며 geometry/motion 상태는 evidence 상태와 독립이다.

검증과 보존 결과는 `work/reports/T16.md` 및 `work/evidence/T16/`에 있다. AI evidence fixtures 8/8, adapter Node 7/7, migration preview 14개 row, T03 schema/catalog, learning validator, attachment crosscheck 2/2, typecheck/build, 실제 local learner browser, preservation 및 diff check가 통과했다. 기존 App chunk >500 kB 경고는 남는다. 시작 시 미커밋 사용자 evidence 47개, T13 spatial evidence 48개, OpenSim_Models HEAD/clean 상태를 보존했다. `/review`와 localStorage 초안은 읽거나 쓰지 않았다. T15g denominator `false/null/null`, T14b human review pending 유지. production field-by-field AI evidence, whole-body coverage, T32/T33/FU01은 미완/미착수다.

다음 task는 **T17 / Luna Max / planned_not_started**다. 아래 prompt를 붙여 넣고 별도 지시 전 시작하지 않는다.

```text
HUMAN ATLAS에서 AGENTS.md, work/STATUS.md, work/task-registry-r13.json,
design/2026-09-25-muscle-atlas/00-START-HERE.md 및 같은 폴더의 06/07/08/09,
work/tasks/T17.md, work/reports/T16.md와 work/evidence/T16/를 읽고 T17만 수행해라.
담당은 Luna Max다. 작은 입력 manifest로 원문 접근 기록→필드 추출→비교표→예외 목록을 만드는
로컬 도구를 구현해라. 검색 API나 계정이 없으면 실제 열어 본 자료를 명시적으로 입력하는 경로를 제공하고,
검색 snippet/index, 열린 원문, 서로 독립된 underlying work, 사람 해부학 검토를 구분해라.
URL·판본 또는 판본 미노출·locator·조회일·접근방식, field/value hash와 ref를 검증해라.
변이·표현 차이·실질 충돌·unavailable을 나누고 실패한 접근을 성공으로 처리하지 마라.
6개 근육 이하 입력으로 재실행·중복·캐시 변경 회귀를 검증해라. AI evidence를 사람이 승인한 것으로 바꾸지 마라.
T16의 빈 production overlay, 기존 canonical claim/review/hash, 사용자 초안, T13 spatial draft,
OpenSim_Models와 T15g denominator false/null을 보존하고 실제 학습 자료에 합성 fixture를 넣지 마라.
관련 테스트·typecheck·build와 UI 변경 시 실제 브라우저를 검증하고 결과·미완·STATUS·다음 T18 prompt를 남겨라.
검증한 T17 소유 변경만 선별 로컬 커밋하고 hash·포함/제외·잔여 변경을 보고해라.
T18 이상, T32/T33/FU01, push·배포, 경혈/Pro mode, 환자 진단·치료·침 시뮬레이션은 시작하지 마라.
```

## T17 결과 및 현재 인계 — 2026-09-27

T17은 manifest schema, offline/manual-entry source workflow CLI, 비교표·예외 리포터, cache 및 provenance validation으로 **complete_with_gaps**다. 18/18 새 source workflow regression, T16 AI evidence 7/7 + fixture 8/8 + 14-row migration preview, attachment comparison 2/2, T03 schema/catalog, learning validator, typecheck/build와 preservation check가 통과했다. synthetic fixture만 실행했으며 실제 anatomy source/claim은 입력하지 않았다. UI 변경이 없어 browser QA는 해당하지 않는다. Build에는 기존 >500 kB App chunk 경고가 남는다.

Production AI evidence overlay는 0 rows, canonical claims/reviews/source hashes는 보존, T13 spatial draft evidence 48개 hash와 기존 untracked 사용자 파일 47개 hash는 시작과 동일하다. OpenSim_Models는 같은 HEAD/clean이며 T15g denominator는 `false/null/null`이다. 사람 해부학 검토/승인은 기록하지 않았고 도구 출력도 승인 자료가 아니다. 상세 결과는 `work/reports/T17.md`, 검증 및 기준선은 `work/evidence/T17/`에 있다.

현재 다음은 **T18 / Luna Max / planned_not_started**이며 자동으로 시작하지 않는다. T18에서 실제 열린 출처를 사용해 종아리 여섯 근육의 기시·정지 필드만 조사하고, 결측·충돌을 추정으로 메우지 않는다. 붙여 넣을 전체 프롬프트는 `work/reports/T17.md`의 마지막 섹션에 있다.


## T18 결과 및 현재 인계 — 2026-09-27

T18은 실제로 연 두 문헌의 locator를 이용해 현재 여섯 개인 근육의 기시·정지와 비복근 두 근두의 출처가 뒷받침하는 head-specific origin/shared insertion 제한을 16개 AI evidence field로 기록했다. 24 field accesses/extractions와 12 comparisons를 재현했다. 11건은 표현·상세도 차이, 긴종아리근 기시 1건은 위쪽 종아리뼈 범위의 실질 충돌로 남겼다. 충돌 해결, 새 name claim, canonical claim/review 수정은 없다. T17 handoff가 기시·정지 조사로 제한했기 때문에 task 템플릿의 이름 대조 요구는 미완으로 명시했다.

검증: source workflow 18/18, T16 fixtures 8/8, AI evidence/adapter/T18 node tests 9/9, search 40/40, learning validator 81 names/14 summaries, typecheck/build, learner browser 및 보존 대조 pass. 요약·출처 표시는 실제 browser에서 봤다. 빌드의 기존 >500 kB App chunk 경고는 유지된다. 보호 입력 101개 중 AI overlay를 제외한 100개, 선행 user snapshots 47개, OpenSim_Models는 보존됐다. StatPearls CC BY-NC-ND 요약의 외부 배포 권한은 이 작업에서 부여하지 않았으며 별도 권리 검토 전에는 공개 배포하지 않는다.

사람 해부학 검토는 계속 `needs_human_review`; exact attachment geometry는 0/41; motion은 absent; T15g 전신 denominator는 `false/null/null`이다. 자세한 제한은 `work/reports/T18.md`에 있다.

다음은 **T19 / Luna Max / planned_not_started**다. 이번 작업에서 T19를 시작하지 않았다. 붙여 넣을 구체 prompt는 `work/reports/T18.md`의 `다음 작업` 섹션에 있다.

## T19 결과 및 현재 인계 — 2026-09-27

T19 선택 근육 focus fade, 기본 ON 토글, 선택 근육+확인된 관련 뼈 isolate, target-follow selection, 학습 base visibility 보존 복원을 구현했다. 투명/흐림 표면 아래의 불투명 또는 가장 깊은 서로 다른 mesh를 pointer로 선택한다. 모바일에서 7개 조작이 문서 폭을 450px로 확장하던 문제는 툴바 wrap으로 고쳤고 390px 폭/가로 넘침 없음으로 확인했다.

검증: focus/pick policy 5/5, scene lifecycle 9/9, navigation Node 14/14 + Python 12/12, search 40/40, typecheck/build pass. 실제 dev 및 production browser에서 1440×1000, 1024×900, 390×844, muscle↔bone 카드/URL, toggle OFF 지속, isolation 중 재선택, 뼈 숨김 후 view reset, history, 비지원 부위, 키보드와 투명층 뒤 pointer를 확인했다. 최종 production 재검에서 390px 뼈 숨김→격리→초기화 후 격리 해제/뼈 숨김 지속도 확인했다. Console error/warning 없음. Build의 기존 1,419 kB App chunk 경고는 유지된다. 보호 파일 102개, 미커밋 사용자 snapshot 47개 hash와 OpenSim_Models HEAD/clean 상태는 시작과 동일하다. evidence/report는 `work/evidence/T19/`, `work/reports/T19.md`에 있다.

T18의 긴종아리근 기시 충돌과 출처 상태, T14b 사람 검토 대기, surface 0/41, T15g denominator `false/null/null`은 변경하지 않았다. AI 비교는 사람 승인이나 부착 surface 좌표가 아니다.

T19 종료 당시 다음은 **T20 / Sol High / planned_not_started**였다. 실행 완료와 현재 인계는 아래 `T20 결과 및 현재 인계` 섹션을 따른다.

## T20 결과 및 현재 인계 — 2026-09-27

T20은 `MuscleAction`, `MotionDefinition`, `MotionAsset` 계약/검증과 runtime-only `MotionSession` type을 별도 계층에 추가했다. 기존 T03 JointAction/review semantics와 Assessment reference는 보존했다. source claim field/hash/evidence 및 purpose/context 연결, canonical subject/joint/instance, 좌우, 정적 scene revision/hash/frame/unit/pose, rig 또는 trajectory와 clip을 검사한다. action text는 joint ID가 아직 없을 경우 명시적 `unmapped` 상태로 둘 수 있지만 MotionDefinition 연결은 차단된다. 역할과 contraction mode는 action context별이다. legacy JointAction adapter는 원본 review/hash/evidence를 유지하는 non-persistable preview다.

검증은 motion contract synthetic fixture 16/16, Node 6/6, 기존 AI/T18 regression 9/9, T16 fixture 8/8, T03 canonical validation, typecheck/build 및 preservation 통과다. 프로덕션 action, motion definition, motion asset은 모두 0건이다. `OpenSim_Models` 동일 HEAD/clean, 기존 사용자 snapshot 47개, T19 protected input 102개는 보존됐다. T14b 사람 검토는 `needs_human_review`, T15g denominator `false/null/null`, T18 긴종아리근 기시 충돌, surface 0/41 상태를 유지했다. build의 기존 1,419 kB chunk 경고가 남는다. 실제 UI를 바꾸지 않아 브라우저 검증은 하지 않았다.

다음은 **T21 / Luna Max / planned_not_started**다. 종아리 6근육의 source-backed action text와 learner card만 다룬다. canonical joint ID가 없으면 텍스트는 source ref와 `unmapped` reason을 연결하고 구조 ID·MotionDefinition·clip을 추정하지 않는다. 전체 붙여 넣기 prompt는 `work/reports/T20.md` 마지막 섹션에 있다. T21 이상은 시작하지 않았다.

## T22 결과 및 이전 인계 — 2026-09-27

T22는 별도 `GLTFLoader` adapter와 asset source/derivation gate를 구현해 **complete_with_gaps**로 마쳤다. 기존 static decoder는 변경하지 않았다. rigged mesh, path-only, bone-motion+illustrative-path 표현을 분리하고 합성 fixture에서 hierarchy/skin/clip binding, frame·meter·hash reject, 공유 자원 dispose를 검증했다. BodyParts3D GLB는 정적 자산이며, 로컬 Gait2392 model 파일에는 motion sample/export가 없다. 첫 demo method는 ankle plantarflexion bone motion + illustrative path로 정했지만 source-backed joint ID/frame/pivot/pose와 적합 clip이 없어 생산 자산은 만들지 않았다. motionAssets는 0건이고 사람 검토/학습 release 승인도 없다.

검증: loader 7/7, representation fixtures 3/3, motion-learning 7/7 + Python 16/16, scene lifecycle 9/9, typecheck/build, preservation, diff check 통과. UI 변경이 없어 browser 검증은 해당 없다. 시작 시 선행 미추적 snapshot 47개와 보호 입력/자산 21개, OpenSim_Models 같은 HEAD/clean을 보존했다. Build의 기존 1,507.24 kB chunk 경고는 남는다. 전체 근거는 `work/reports/T22.md`, `work/evidence/T22/`에 있다.

당시 다음 task는 **T23 / Luna Max / planned_not_started**였다. 아래의 T23 중단 기록이 현재 상태다.

## T23 재개 완료 및 현재 인계 — 2026-09-27

기존 T23 미커밋 WIP를 삭제하거나 다시 만들지 않고 T41 이후 HEAD `6425a0fe37b76d5a18f74d6cff496d78323bc54b`에서 재개했다. T41 보고서와 실제 validation 결과에서 R2 active-scene 결함 수정이 통과했고, 재실행한 animation-loader 회귀도 10/10 통과했다. 이전 중단 사유는 해결됐다.

player/state·단일 RAF·늦은 응답 무효화·reduced-motion·pose/camera reset 분리 및 합성 전용 경계가 통과했다. 실제 production `MotionDefinition`/`MotionAsset`은 0건이다. 브라우저에서 1440×1000, 1024×900, 390×844 폭에 가로 넘침 없이 빈 시범 메시지와 비활성 재생 조작을 확인했다. 키보드로 움직임 disclosure를 열고 다음 action control에 포커스할 수 있었다. 전경골근 전환과 URL, 목 부위의 0개 구조·빈 상태 및 종아리 장면 비표시, 뒤로 가기 복원을 확인했으며 console error/warning은 0건이다. 실제 clip 재생은 확인하지 않았다. 브라우저 reduced-motion emulation은 제공되지 않아 해당 전이는 테스트로 확인했다.

검증: motion player 16/16, motion learning 7/7 + Python fixture 16/16, animation loader 10/10 + 표현 fixture 3/3, scene/cache 9/9, typecheck, build, `git diff --check` 통과. Build의 기존 큰 chunk 경고(App 1,623.72 kB)는 남는다. OpenSim_Models는 HEAD `d9b05d470b1a481c222372c85b75772faf8f7792`/clean, GLB 및 T13 자료 hash는 재개 기준과 일치한다. 전체 결과는 `work/reports/T23.md`, 재개 검증·보존 근거는 `work/evidence/T23/resumption-validation-results.json`과 `resume-preservation.json`에 있다.

**현재 다음 task는 T42 / Luna Max**다. T24는 T44 이후 작업이며 자동으로 시작하지 않는다. T42의 학습 출처 문구·뼈 이름·CTA 개편은 이번 범위에서 구현하지 않았다. 붙여 넣을 T42 prompt는 `work/reports/T23.md` 마지막 섹션에 있다.

## T41 결과 및 당시 인계 — 2026-09-27

T22 감사 R1/R2/R3를 수정했다. 반환 `gltf.scene` 밖 rig/path/skin 및 clip track target, 외부 buffer/image URI를 거부하고 정상 단일 scene을 유지한다. 정적 종아리 로더는 해당 scene의 일곱 근육 mesh mapping만 검증하며 전역 canonical 개수와 모든 mapping의 우측/needs_review 고정을 제거했다. 원본 hash/revision/frame/pose와 FJ3385 보류는 유지한다. 현행 첫 시범 후보는 `HA-M-000003` 전경골근/앞정강근/Tibialis anterior 오른쪽 발목 배측굴곡이다. T22 역사 보고서는 변경하지 않았다.

검증: loader 10/10, 실제 종아리 catalog 변형 scene subset 3/3, T23 player WIP 16/16, scene/cache 9/9, 표현 fixture 3/3, data/source 검증, typecheck/build 통과. 실제 브라우저에서 종아리 GLB 표시·전경골근 선택·자산 없는 머리 부위·뒤로가기·선택 해제와 console error 0을 확인했다. 실제 clip은 0건이므로 실재생을 주장하지 않는다. 상세는 `work/reports/T41.md`, `work/evidence/T41/`에 있다.

당시 다음은 R14 registry의 T23 재개 / Luna Max였다. 이후 위 T23 재개 완료 기록으로 끝났고 현재 next는 T42다. 해당 T23 재개 prompt의 과거 사본은 `work/tasks/T23-R14-RESUME.md`에 보존한다.

## T42 결과 및 당시 인계 — 2026-09-27

T42는 learner 표시와 선택 가능한 9개 뼈 이름 overlay/search를 구현하고 acceptance를 통과했다. 기시·정지 source disclosure와 기능 문장 안의 source-scope 설명을 learner 투영에서만 숨겼다. 원본 motion/action text, canonical claim/evidence/source/hash는 보존했다. 근육·뼈 카드는 우리말명/한자어명(한글)/영어명 3행을 공유한다. 실제 Hanja는 수집하지 않았다. KMLE 판본 미노출, anatomy review 대기와 bone landmark Korean source gap은 분리해 기록했다. 영문 landmark는 한국어를 추정하지 않고 학습 화면에서 보류했다.

검증은 search 44/44, motion-player 20/20, typecheck/build/data validators와 실제 브라우저 1440×900/1024×768/390×844에서 통과했다. 9개 bone alias→stable ID/카드 세 이름/right selection, generic 중족골 ambiguity 2 results, keyboard Enter 선택, origin/insertion/function disclosure 부재, disabled no-clip CTA, 평가 탭 부재, console error/warning 0을 확인했다. Build의 기존 >500 kB App chunk warning은 남는다. 보호 입력 18개 hash와 `OpenSim_Models` HEAD/clean 상태는 시작 기준선과 동일하다. 세부 결과는 `work/reports/T42.md`, 증거는 `work/evidence/T42/`에 있다.

당시 다음은 **T43 / Luna Max / planned_not_started**였다. 그 이후 실제 실행 결과와 현재 queue는 아래 T43 섹션을 따른다.

## T43 결과 및 현재 인계 — 2026-09-27

T43은 12개 top-level region 모두의 source candidate, 구조 텍스트/이름 상태, 근육·뼈 geometry acquisition path, laterality 범위, rights, rig/motion 후보와 gaps를 조사해 `passed_with_gaps`로 기록했다. 12개 대분류 아래 하위 메뉴는 추가하지 않았다. T15g snapshot의 85 unique IDs(48 individual/16 group/21 part), 현재 종아리 6 membership, 0 bone product membership을 membership과 분리했고, 4 group + 2 part lower-extremity ID를 자동으로 thigh/leg/foot에 배정하지 않았다. T15g whole-body denominator는 `false/null/null`로 유지한다.

BodyParts3D 원문 README, IS-A index, download inventory와 license를 확인했다. 이는 acquisition metadata 후보이며 mesh를 내려받거나 지역 membership/해부학 검토를 승인하지 않는다. OpenSim은 각 모델의 독립적인 부위·license·frame을 가진 후보로만 기록했으며 production rig/clip은 0이다. T32 input은 준비자료만 작성했고 선행 T31은 아직 `planned_not_started`이므로 T32를 시작하지 않는다.

검증 결과는 `work/evidence/T43/verification-results.json`, 구조 검사는 `validation-results.json`, 보존 대조는 `preservation-after.json`에 있다. T15g의 `build_t15g_inventory.py --check`는 generated artifact/input drift로 실패했으며 T43은 해당 inventory나 입력을 수정하지 않았다. Typecheck/build와 범위별 schema/navigation validation은 통과했다. 사람 해부학 검토는 수행하지 않았다.

현재 다음 task는 **T44 / Sol High / planned_not_started**이며 T43 보고서 마지막의 붙여 넣기 프롬프트를 따른다. T44를 시작하지 않았다. T43은 전신 구현 완료나 coverage 완료가 아니다.

## T44 결과 및 현재 인계 — 2026-09-27

T44는 `OpenSim_Models` Gait2392 `.osim`의 오른쪽 `ankle_r`·`subtalar_r`·`mtp_r`와 tibia/talus/foot/toes VTP, `tib_ant_r` 모델 경로를 읽어 별도 q=0 정적 GLB를 생성했다. Source→scene 행렬은 `(-z,y,x)`이며 m 단위를 유지한다. 이 같은 원모델 내부 변환의 6개 표지 잔차는 0 m, GLB float32 경로 잔차 최댓값은 9.47e-9 m다. BodyParts3D와 정합됐다는 주장은 하지 않는다. 변환 스크립트·모델/geometry·산출물 hash, 피벗/축/계층, rest pose와 경로점은 joint-binding manifest 및 `work/evidence/T44/ADR-001-coherent-opensim-scene.md`에 있다.

Canonical 오른쪽 발목 joint와 전경골근 오른쪽 배측굴곡 action을 `needs_review`로 migration했다. T21의 양측 등쪽굽힘·안쪽번짐 레코드는 그대로 unmapped이며, FJ3385 ID는 추정하지 않았다. 새 경로선은 원본 모델의 설명용 경로이지 부착 표면이 아니다. 제품 UI/clip은 변경하지 않았다. 별도 OpenSim 기준 자세 preview는 실제 브라우저에서 로드·시각 확인했고 console error/warning이 없었다. 입력 검증·catalog schema/17 fixtures·typecheck/build가 통과했다. 모델 수준 CC BY 3.0 귀속은 남겼으나 VTP 개별 권리 표기가 없어 공개 배포 전 파일별 권리 확인이 필요하다.

현재 다음 task는 **T24 / Sol High / planned_not_started**다. T44 정적 입력을 사용해 실제 교육용 clip을 만들고 세 자세/재생·정지·복원/경로 결속을 검증하는 것은 T24 범위다. T44의 결과만으로 motion-ready나 해부학 승인으로 올리지 않는다. 붙여 넣을 T24 프롬프트는 `work/reports/T44.md` 마지막 섹션에 있다.

## T24 결과 및 현재 인계 — 2026-09-27

T44 정적 GLB에서 발목 node 회전과 전경골근 설명용 경로 morph를 가진 2초 clip을 생성했다. 파생 GLB와 stable ID/hash/license를 motion bundle에 `candidate`로 등록했고, 동일 source 내부의 0/1/2초 발 앞쪽 상승·경로 끝점 일치·경로 길이 감소·신규 주요 관통 0건을 검증했다. 격리된 개발 브라우저에서 실제 로드·렌더·재생·정지·복원을 확인했다.

초기 메인 페이지 실험은 선택만으로 기존 BodyParts3D 근육 그래픽을 별도 검은 OpenSim 발목 장면으로 바꿨다. 사용자가 원한 것은 원래 근육 그래픽에서 **움직임으로 이해하기 CTA를 눌렀을 때 앞정강근의 수축과 몸 움직임을 연속 표시**하는 것이다. 초기 실험은 해당 요구에 맞지 않아 전부 되돌렸다. T44에는 검증된 근육 표면 변형이나 BodyParts3D 간 registration이 없으므로 원래 mesh 수축처럼 위장하지 않는다. 메인 페이지는 기존 그래픽과 비활성 CTA로 유지하고 T24를 **blocked**로 기록한다. 상세 gap·재현·검증·보존 대조는 `work/reports/T24.md`, `work/evidence/T24/`에 있다.

R14 registry의 형식상 후속은 T25 / Luna Max지만 `previous_actual_acceptance`가 충족되지 않아 실행할 수 없다. T24 해결 작업 / Sol High가 먼저 필요하다. 다음 프롬프트는 T24 보고서 끝에 남겼으며 자동 실행하지 않는다.
