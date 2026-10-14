# AT10 / skin-runtime r1 — 부분 코드와 완료 계획 점검

2026-10-14. 시작 HEAD `c66412364bf655352c997e84f79dc92056fa3caf`. 시작 status·45개 기존 WIP hash·실제 r22/r41/r54 입력 hash는 [start](../evidence/AT10/2026-10-14-skin-runtime-r1/start.json)에 고정했다. 새 모델링·원본 조사·다음 task는 실행하지 않았다.

**acceptancePassed=false.** skin-fit의 통과 전신 자산은0이다. r22는 여전히 geometry=false, r41은 양손 local contact만 통과, r54는 미채택이다. 이번 사용자의 후속 요청에 따라 실제 미완/원인을 조사하고 [완료 계획](../plans/acupoint-surface-posture-2026-10-13/AT10-REMAINING-COMPLETION-PLAN-2026-10-14.md)을 작성했다. runtime의 부분 코드를 전신 피부 합격으로 승격하지 않았다.

## 이번에 작성·검사한 부분

- 기존 보기옵션 순서에 **피부** 버튼만 추가했다. 통과 자산이 없으므로 제품에서는 비활성이고 `전신 피부 정합 준비 중`을 표시한다. 다른 버튼·홈·로딩·카메라 정책은 변경하지 않았다.
- lazy `SkinLayer`는 기존 root에 정적 mesh 한 개를 붙이는 경로다. static pose, embedded/file hash·단위/frame·acceptance, decoded 비용과 기존 예산을 검사한다. OFF/취소/late completion/dispose, motion/context-loss 해제와 독립 layer/mode 상태를 구현했다. 별도 renderer/camera/clock/update callback은 없다. 이것은 실제 제품 피부가 등록됐다는 뜻이 아니다.
- r41은 DEV `skinReview=1`에서만 import 가능한 검토 입력이다. source/원본/후보 GLB는 수정하지 않았다. 실제 candidate decode를 자동 검사했지만 이번에는 r41의 실제 앱 ON/OFF/근접 검증을 수행하지 않았다. review 입력을 learner eligible로 바꾸지 않았다.
- triangle+barycentric에서 법선 접촉 glyph/선택 국소 triangle cue를 만드는 공통 helper를 작성했다. 108개 기존 real-input binding의 좌표/주소/AI provenance를 바꾸지 않는 자동 검사를 통과했다. 제품의 기존 구형 marker 표현은 통과 피부가 등록되기 전까지 유지한다. 새 glyph는 DEV 검토 경로의 부분 구현이며 피부 접촉 합격0이다.
- whole-body carrier의 좌우 mask 기술 계약을 추가했다. 기존 AT21/22 renderer/editor를 복제하지 않았다. 새 canonical geometry의 실제 loader/editor 공유 연결과 mask revision fixture는 아직 미완이다. 실제14개 영역은 제작하지 않았다.

## 검증과 실제 미달

관련 자동 검사34개가 통과했다. 거부 자산 learner gate, 실제 r41 GLTFLoader·topology hash·불투명 무광 material·비raycast, bytes 변조/좌표 stale 거부, mode 복원/manual OFF, 늦은 fetch 취소/반복 OFF/dispose/motion guard, 기존108개 binding, 기존 overlay camera guard, AT21 mask 회귀를 포함한다. typecheck와 전체 build를 수행했다. 첫 실행의 strip-only Node 설정/테스트 ledger 경로 오류는 수정했고 시도 로그를 보존했다. 최종 결과는 evidence의 `tests-final.log`, `typecheck.log`, `build-final.log`에 있다.

실제 앱에서 제품 피부 버튼의 비활성과 기존 LU 오른쪽11개 경혈 진입을 확인했다. 한 renderer/root의 기존 장면이 유지되고 오류 console은 검사 시0개였다. [제품 화면](../evidence/AT10/2026-10-14-skin-runtime-r1/actual-learner-disabled-skin.png), [LU 화면](../evidence/AT10/2026-10-14-skin-runtime-r1/actual-learner-lu1.png), [실제 상태](../evidence/AT10/2026-10-14-skin-runtime-r1/actual-lu1-state.json)를 남겼다. LU screenshot은 새 glyph 초안이 잠시 활성인 중간 점검 화면이며 final 제품 glyph 합격으로 세지 않는다. 최종 코드에서는 통과 피부 없이 기존 제품 표현을 변경하지 않게 분리했다.

**‘전체 경혈’ 실제 진입은 실패했다.** 기존108개 데이터/좌표 검사는 통과하지만, actual base20,042,516 + encoded overlay931,445 =20,973,961bytes가 기존20MiB를2,441bytes 넘어서 공통 guard가 표시를 중단했다. [실제 budget](../evidence/AT10/2026-10-14-skin-runtime-r1/actual-all-points-budget.json)에 기록했다. 이 encoded 계산·거부식은 변경하지 않았다. 새 glyph의 삼각형 감소로 encoded 초과를 해결한 것으로 쓰지 않았다. 역사 AT8의 pass를 덮지 않고 현재 전체 표시 회귀의 미달로 남긴다.

기존 r5의 overview+education carrier+skin 합계21,482,184bytes/964,488triangles/18,875,724 decoded bytes도 재사용했다. 피부까지 넣으려면 단순 geometry 동시 추가가 아니라 공통 전달/공유 비용을 해결해야 한다. 실제 현재 전체점 묶음과는 데이터 구성이 다르므로 같은 합계라고 주장하지 않는다. 읽기 전용 in-memory gzip probe상 education813,096→505,232bytes, 후보 GLB626,572→514,776bytes, 일부 JSON도 감소하지만 이는 **전달 구현/예산 통과가 아니다.** [probe](../evidence/AT10/2026-10-14-skin-runtime-r1/lossless-delivery-feasibility.json)에 항목별 수치가 있다.

피부 ON/OFF/표식 접촉/얼굴·귀·손발/390·1024·1440 actual QA, final driver GPU/FPS/idle 측정, 대표 새 point compiler→learner 표시, canonical carrier 공유/LOD 주소/AT21·22 새 mask 검증은 수행 완료가 아니다. automatic108개를 실제 피부 접촉108개로 세지 않는다. 실제 fit 승인/신규 위치/361점 완성/자세 지원/교수 승인/공개 권리도 추가하지 않았다.

## 다음과 보존

남은 것은 **전신 skin-fit의 실제 국소 대응/변형 → skin-runtime 제품 연결·예산·실화면 QA → existing-package-reconciliation124개**다. 구체 산출물/통과 기준/다음 프롬프트는 완료 계획에 있다. immediate 다음 구현 입력은 같은 `AT10/skin-fit/right-foot-continuous-surface-bands`다. F1 오른발 이후의 묶음이나 runtime/reconciliation을 이번 요청에서 자동 실행하지 않는다.

EXECUTION은 AT10.skinRuntime의 부분 결과와 계획 링크만 추가하고 parent acceptance/result, resumeUnit=skin-fit, skinFit의 모든 기존 판정, Luna 결과, AT30/31 planned, 다른 AT/MV 기록과 feature plan nextUnit=AT10을 보존한다. `sync_execution.py`와 `--check`를 실행한다. 소유 코드/보고서/계획/versioned evidence만 로컬 커밋하고45개 기존 tracked WIP 및 수천개 source/cache/역사 untracked는 제외·보존한다. 위임/push/배포는 하지 않는다.


## 2026-10-14 completion-r1 후속 실제 결과

[후속 보고서](AT10-completion-2026-10-14-r1.md)와 [versioned summary](../evidence/AT10/2026-10-14-completion-r1/summary.json)를 확인한다. 승인된 오른발 fascia991면의 주소별 참조 분리, 전체108개 예산 회귀 및 실제 loader pose metadata 오류는 해결했다. r56/r58 및 dense/분할 대안은 실제 geometry/형태 미달로 채택하지 않았다. AT10 acceptance=false, r22 primary/양손 r41 성공/Luna 산출물을 보존하고 같은 AT10/F1이 남는다. 새 피부 product import·접촉·다음 AT 실행은0이다. 이 후속 결과는 앞의 역사 수치를 덮지 않는다.
