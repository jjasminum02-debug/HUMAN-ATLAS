# T66 최종 통합 기록 — 2026-10-04

## 판정

**T66은 `in_progress / partial`로 유지한다.** 이번 실행은 W1 A/B/C/F의 실제 반영분과 W2 D/E 후보를 대조하고, 검증 가능한 W1 구성만 기존 단일 scene/runtime에 둔 상태에서 최종 통합 검증을 수행했다. D/E 후보는 할당 충돌 또는 실제 QC 실패 때문에 등록하지 않았다. 현재 해결되지 않은 제작/통합 결함이 있어 T66 완료, T85 인계, nextUnit 종료 조건을 충족하지 않는다.

- 기준 HEAD: `98f3d88b5c733e7db3a75539680ecc4d15b24a47`
- 시작 시 dirty path 5,441개, staged 0개. 현재 사용자 WIP를 초기화하거나 일괄 stage하지 않았다.
- 기존 `OpenSim_Models/`, `work/evidence/T13/`, 원본 모델/asset, source-only·권리·사람검토 상태를 변경하지 않았다.
- parent `nextUnit`: `author-and-integrate-normal-motion-bone-and-nerve` 유지.
- 상세 기준선: [start-baseline.json](start-baseline.json)

## 현재 runtime과 분모

고정 분모는 542 targets / 563 memberships / 12 regions, 근육 429/447, 232 source muscle concepts / 462 source surfaces, HA canonical binding 130, 역사 분류 163(6/20/135/2)이다. 이 값은 분모이며 전수 동작·extent 승인을 뜻하지 않는다.

단위와 종류를 구분해 실제 현재 입력을 재집계했다.

| 항목 | 현재 통합값 | 해석 |
|---|---:|---|
| 고유 source muscle surfaces | 129 | 기존 runtime 107 + W1에서 새로 연결된 source 22 |
| muscle source-action rows | 311 | 기존 273 + W1 selector 38; 고유 표면 수가 아님 |
| 고유 bone source instances with family roles | 166 | 기존 150 + W1 신규 16; 독립 해부 bone concept 수는 미확정 |
| bone family binding rows | 1,581 | 기존 865 + W1 selector 716 |
| 실제 runtime GLB URI/hash | 62/62 | 기존 34(그 중 역사 T24 text candidate 1개는 재생 불가) + W1 신규 28 |
| W1 registration package templates | 32 | 실제 고유 GLB 파일 수가 아님 |
| W1 selector rows | 754 | source action/role 관계 수이며 개념/자산 수가 아님 |

현재 W1 신규 등록은 34개 정성적 작용 selector(22 source keys, 26 GLB)와 4개 수동 자세 관찰 selector(2 GLB), 716개 뼈 역할 selector다. 기존 역사 main-function clip 1개는 별도다. 새 full-target extent 승인 0개. 계산 및 URI/hash 집합 중복 검사는 [runtime-counts.json](runtime-counts.json)에 있다.

W1에서 실제 등록된 28개 GLB는 manifest SHA256/byte와 현재 파일이 전부 일치했다. W2 D의 후보 22개와 E의 후보 56개도 명시 hash/byte와 모두 일치했으나, **후보 파일 무결성은 통합/해부학 합격이 아니다.** D/E GLB는 runtime에 하나도 등록하지 않았다. 상세 106개 파일 검사는 [candidate-asset-hash-audit.json](candidate-asset-hash-audit.json)에 기록했다.

## W1 A/B/C/F, unit03 및 W2 D/E 인계 대조

- **W1-A:** 34 action rows/26 고유 GLB는 통합에 반영됐다. 92 source-action rows는 실제 제작/접촉 등 engineering 차단, 54 work keys는 source/relation 미확보로 남는다.
- **W1-B:** 29 후보 GLB 모두 geometry/identity/target 관계 문제로 차단되어 등록 0이다. 미해결 action claim 7건은 충돌/근거 gap으로 분리했다.
- **W1-C:** 2개 GLB는 각각 source 범위가 있는 수동 자세 관찰로 통합됐다(4 selector). 호흡 후보 2개는 차단, 157 work keys는 source/relation gap이다.
- **W1-F:** 전체 98 native nerve label rows 중 30 work keys의 텍스트 근거가 검증됐고 68은 미확보다. 7개 learner field를 대조해 실제 값 1개만 delta로 반영했다. 새 독립 신경 개념·GLB·동적 주행은 0이다. 98 label groups는 신경 개념 수가 아니다.
- **unit03:** 66개 책임 중 64 `implemented_verified`, 2 `processed_with_content_gaps`, product defect 0으로 기존 책임 기록을 재사용했다. 남은 내용 gap은 (1) 양측 자쪽머리 손목굽힘근의 방향을 노쪽/자쪽으로 정규화할 근거, (2) 한 출처 내부 뒤침근 방향 충돌, (3) 승모근 전체 작용을 위·중·아래 부분에 상속할 근거 부재다. 18 package/682 selector receipt는 UI 합격이나 전 근육 범위 합격으로 세지 않았다.
- **W2-D:** 16/16 frozen work keys에서 manifest 소유자와 D handoff가 충돌한다. handoff의 두 `candidate_validated` 행도 할당이 충돌하므로 등록하지 않았다. 후보 GLB 22개 hash/byte는 일치하지만 턱 작용 10행에서 실제 Bucinator edge/area 변형 실패, Palatopharyngeus 두 작용 문맥 부재, 가쪽날개근 위갈래 두 action unresolved가 남는다. 목뿔뼈/후두골은 D 배정 밖이다. frozen manifest를 재배정/수정하지 않았다.
- **W2-E:** 66 work keys, 82 action evidence rows, 56 candidate GLB/hash다. local geometry QC 38 pass/18 fail이며, action-outcome QC는 0, candidate validated workkey도 0이다. 실패 18개는 새 bone containment가 확인된 source들이다. geometry pass만으로 작용/통합을 승인하지 않았으며 아무 후보도 등록하지 않았다. 48 work keys는 source/relation missing이다. worker가 제안한 output-root/typed bone-context runner 수정은 제안으로만 보존했다.
- W2 입력의 explicit deferred disposition은 target 276, membership 290, source 60, bone-context 21행이다. 배정 범위를 전체 분모 완료로 해석하지 않았다.

원시 후보와 예외 ID, exact D 소유 충돌 IDs, E 실패 source keys는 [final-blocker-list.json](final-blocker-list.json), [wave2-reconciliation.json](wave2-reconciliation.json), wave worker 원본 handoff/QC 파일에 있다. 역사 보고서 및 worker evidence를 고치거나 대체하지 않았다.

## 실제 UI와 자동 검증

- 현재 local app에서 오른쪽 짧은엄지벌림근 W1 source/action을 실제 선택했다. 영어 검색, 세 이름 카드, 우측 표시, 키보드 좌우 전환, 단일 action label, CTA 하나, 키보드 재생, smooth rest 복귀를 확인했다. 실제 응답 GLB는 200/1,052,308 bytes, SHA256 `03a4ba7b2a05c8f97b1e9b6e0dab8e3dd496982ec845823625c0a601c90c6bcb`로 manifest와 일치했다.
- Chrome/Playwright에서 12개 부위를 모두 차례로 선택했다. 각 부위가 단일 선택 상태가 되고 structure row와 한 canvas를 유지했으며, 전신 초기화와 키보드 부위 선택도 통과했다. console/page errors 0. 세부 row count/URL은 [region-navigation-validation.json](region-navigation-validation.json)에 있다.
- 390/1024/1440 CSS viewport에서 가로 overflow/다중 canvas가 없었다. 390은 접힌 상세 카드 안을 스크롤하면 CTA를 볼 수 있었다. 이는 desktop viewport emulation이며 실기기 검증은 아니다. 스크린샷: [390](screenshots/w1-hand-390-cta.png), [1024](screenshots/w1-hand-1024.png), [1440](screenshots/w1-hand-1440-rest.png).
- 최종 자동 검증은 13개 check 전체 통과: motion/W1 회귀 42 tests, learner runtimes/content/source contracts, scene decoder, TypeScript project check, Vite build, compiled learner bundle leakage audit 포함. [final-validation.json](final-validation.json).
- Vite 빌드는 통과했지만 현재 app JS chunk 6.2 MB minified/644 KB gzip으로 500 KB 권고를 초과한다는 기존 경고가 있다. 이 실행은 기능 실패로 관찰하지 않았고 분리/예산 수정은 하지 않았다. GPU/VRAM/전체 process memory는 측정하지 않았다.
- `sourceOnly=true`, local selection technical-only, public redistribution `held`, `humanReview=not_performed`, canonical target/membership approval 없음. 학생 화면에 내부 ID/evidence/JSON을 노출하지 않았다.

## 다음에 해결할 필수 항목

T66을 통과시키기 전에 같은 parent nextUnit에서 다음 실제 blockers를 해결해야 한다.

1. W1-A의 92 engineering rows와 W1-B의 29 접촉/정체성 실패를 각 정확한 source/key에 대해 고친다. source/relation 결측과 실제 geometry defect는 분리한다.
2. W1-C 호흡 후보 2건의 engineering 차단을 해결하거나 확인된 교육 범위/근거에 따라 해당 행만 보류한다.
3. W2-D의 16 manifest ownership conflict를 고정 입력 변경 없이 authoritative assignment owner와 reconcile한다. 턱 edge/area 변형, 두 기능 문맥, unresolved pterygoid, 배정 밖 hyoid/larynx를 처리한다.
4. W2-E에서 18개 new-containment source geometry를 수정하고 작용 결과 QC를 실제로 통과시킨 뒤에만 common registration을 검토한다. output-root/assigned-bone-context 공통 runner defect는 별도 patch proposal로 남아 있다.
5. 전수 authoring disposition에서 276 target/290 membership 및 60 source와 기타 wave 밖 항목의 정확한 scope를 이어받는다. 근육/뼈/신경 목표는 partial이며 0-gap 또는 human approval을 만들어내지 않는다.

따라서 `EXECUTION.json`의 T66은 `in_progress / partial`, `nextUnit=author-and-integrate-normal-motion-bone-and-nerve`다. T85를 인계하지 않는다.
