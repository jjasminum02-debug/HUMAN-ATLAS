# MV1 — 근육 움직임 전수 조사 결과

**판정: partial.** 현재 learner runtime에서 도달 가능한 332개 근육 role/side mapping을 동결하고 기술 검증·다중 시점 시각 검토를 수행했다. 330개는 기록된 화면 조사 범위에서 명확한 결함을 찾지 못했고, 대퇴직근 무릎 시범 좌우 2개는 돌출 형태가 정상 수축인지 과도한 변형인지 판별하지 못해 `not_checked`로 남겼다. 이 상태를 전수 완료나 자연스러운 수축 승인으로 표시하지 않는다.

## 소유 경계와 시작 상태

- 시작 HEAD: `b875cdc050816456850862f03e6b5d87a3b2a999` (`main`).
- 시작 `git status --porcelain=v2 -z`: SHA-256 `af9a0b5deca6f79b2cd554e0e12c1b22b0f4cb8fb2eae540c5e1b5796f66007d`, 53,157 bytes, tracked modified 45개, untracked status entry 583개. 원본 목록은 [`start-status-porcelain-v2.z`](../evidence/MV1/preservation/start-status-porcelain-v2.z), 경계·입력 hash는 [`start.json`](../evidence/MV1/preservation/start.json)에 보존했다.
- 소유 경로는 `work/evidence/MV1/**`, 이 보고서, `work/EXECUTION.json`의 `featureWorkUnits.MV1` 및 모션 plan의 현재 next ID뿐이다. runtime, 기존 motion JSON/GLB/authoring 입력, `OpenSim_Models`, T13 drafts와 시작 시점 사용자 WIP는 수정하지 않았다.

## 동결한 현행 분모

이전 AT6 전달값 1,160 asset record / 46 URI-hash 파일 / 74 index entry는 시작 참고 스냅샷이다. 실제 learner 도달성을 확인한 이번 분모는 [`inventory.json`](../evidence/MV1/2026-10-11-run-01/inventory.json)에 있다.

| 범위 | 동결 결과 |
|---|---:|
| 현재 후보 mapping 전체 | 1,913 (근육 subject 332, bone context 1,581) |
| 조사 대상 근육 sourceKey | 134 unique |
| 근육 source side | left 166, right 166, bilateral/midline 0 |
| role/side를 보존한 근육 mapping | 332 |
| 근육 URI/hash/clip 조합 | 71 |
| hash + clip + transform + playback dedupe 뒤 근육 재생 mapping | 74 |
| 전체 재생 mapping | 76 (이 가운데 bone 전용 2개는 근육 분모에서 제외) |
| 전체 현행 learner 도달 URI/hash 쌍 | 73 |
| 실제 delivery index | 74개 중 현행 미도달 tibialis anterior 1개, 현행 pair 누락 0개 |
| authoring registry 입력 | 56/56 hash 일치 |

현재 muscle row의 선택 role은 `deforming_muscle_surface` 144개, `deforming_passive_surface` 188개다. 여섯 member-role coverage 집합도 inventory에 별도로 보존했고, side·role 차이를 dedupe로 합치지 않았다. 73개 현행 GLB URI/hash 파일은 존재·등록 hash·GLB parse가 모두 통과했다. 전달 index의 미도달 항목은 `atlas-data/assets/motion/t24-right-tibialis-anterior/ankle-dorsiflexion.glb` (`956bb0e3…73596a`)이며 이를 현행 조사 대상으로 간주하지 않았다.

실제 learner runtime의 browser-backed 검증은 2026-10-11 12:49:22.500Z에 수행했다. integration은 HTTP 200, 1,168 objects, SHA-256 `bf4218bb12b1babdcffbb34f42359aec0fc1003aa51628ff768cb652f1164662`; dataset manifest는 HTTP 200, 1,168 instances, SHA-256 `fda7430f2b76eddd852fb9eae7fde9ad624baebdea5427a6672d87436034f17d`였다. 모든 근육 mapping 332/332가 learner route/getter/side 도달성 및 실제 `loadAnimationScene`에서 통과했다. 상세 행은 [`live-binding-validation.json`](../evidence/MV1/2026-10-11-run-01/runtime/live-binding-validation.json)과 [`real-loader-validation.json`](../evidence/MV1/2026-10-11-run-01/runtime/real-loader-validation.json)에 있다.

추가 Node CLI inventory 재조회는 shell에서 loopback fetch를 하지 못해 `fetch failed`를 냈다. 처음 시도의 출력은 [`inventory-refresh-attempt-2026-10-11.json`](../evidence/MV1/2026-10-11-run-01/runtime/inventory-refresh-attempt-2026-10-11.json)에 보존했다. 조사 도구를 수정해 다음 재시도는 timestamped diagnostic만 기록하고 성공한 freeze를 덮지 않게 했으며, 실제 재현에서도 `inventory.json`이 유지됨을 확인했다([`inventory-refresh-attempt-2026-10-11T13-10-16.507Z.json`](../evidence/MV1/2026-10-11-run-01/runtime/inventory-refresh-attempt-2026-10-11T13-10-16.507Z.json)). 이 shell 제한을 runtime 부재로 해석하지 않았다. learner manifest와 mapping의 유효 근거는 위 성공한 browser-backed 검증이다. bone context 행별 상태는 MV1 근육 pass 판정에 포함하지 않고, 해당 CLI retry에서 재조회되지 않은 행은 inventory 안에서 null로 남겼다.

## 조사·검증 결과

- 재사용 대상으로 기존 learner motion runtime, schema, source binding/anchor 및 `DatasetSceneAdapter`, role/member overlay 처리, `CameraSessions`, 관찰 tour와 기존 authoring manifest/loader를 고정했다. 새 model·tour·runtime content는 만들지 않았다. 조사 도구는 [`work/evidence/MV1/tools`](../evidence/MV1/tools/)에 있다.
- [`target-dispositions.json`](../evidence/MV1/2026-10-11-run-01/target-dispositions.json)은 332개 전체에 `pass` / `not_checked` / `fail` / `error` 중 정확한 상태를 기록한다: **pass 330, not_checked 2, fail 0, error 0**. Pass의 범위는 기록된 defect-screen과 기술 mapping/loader 통과이며 자연스러운 생리적 수축 승인이라는 뜻이 아니다.
- 실제 learner 화면에서 대흉근 `팔 모음 · 어깨 모음`의 준비(66%)·중간·최대·rest와 대퇴직근 `무릎 폄 · 슬관절 신전` 시범의 준비(67%)·중간(50%)·최대(100%)·복귀(0%)를 재현해 저장했다. UI 카메라/관찰 시점 메뉴는 건드리지 않았다. 화면 파일의 byte/hash와 목적은 [`screenshots-index.json`](../evidence/MV1/2026-10-11-run-01/visual/live-runtime/screenshots-index.json)에 기록했다.
- 74개 재생 mapping 전체의 actual emitted GLB를 source transform/role에 맞춘 review scene에서 검사했다. 각 group에 rest·방향 고려 준비·중간·최대·복귀 5 phase, 정면·측면·사선 contact sheet를 생성하고 전부 시각 확인했다. 전체 74-cycle / 242.211초 / 12 fps 재생 영상을 생성해 처음부터 끝까지 4× 화면 검토했다. 이 속도는 눈에 띄는 끊김·분리의 gross screen이며 frame-by-frame slow-motion 판정은 아니다.
- shared muscle/bone mapping에서 representative 선택 오류가 있었던 이전 v1/v2 capture index/contact sheet/video는 삭제하거나 덮지 않고 보존했다. 최종 판단과 completeness 집계에는 representative 선택을 수정한 v3 recording과 별도 `focused-phase`/variant 자료만 사용했다.
- 전체 332 role/side variant를 10장 contact sheet로 보존했다. 각 행에는 정확한 sourceKey/side/role/asset/clip/hash와 rest·middle·end 세 상태의 세 시점이 있고 선택 target을 따로 강조했다. 별도로 keyframe 및 이웃 keyframe midpoint의 정면·측면·사선 image를 220개로 생성했다. 강조 색상은 review harness의 teal이며 learner UI의 action/return 색상 전환과 같지 않다. 실제 UI의 두 필수 demo를 재현했지만 action/return 색상 전환을 332개 모두 runtime 화면으로 개별 확인하지 않았다. 220개 파일은 모두 존재하고 index/hash 무결성이 통과했지만, **220장을 각각 열어 수동 판정하지 않았다**.
- 자동 지표는 74/74 group, **3,682** keyframe/midpoint sample을 처리했다. rest normal flip 0, motion으로 늘어난 degenerate triangle fraction 최대 0, full-cycle return residual 0 m였다. 45 group은 rest에서 이미 degenerate triangle이 있었고 최대 비율은 0.08046으로 움직임 후 증가하지 않았다. 최대 displacement 0.10677 m 자체는 자연스러운 수축의 지표나 승인 기준이 아니다.
- 수치 attachment landmark가 없어 attachment drift를 숫자로 계산하지 못했고, collision oracle이 없어 penetration도 숫자로 측정하지 않았다. 확인 가능한 화면에서 눈에 띄는 fold/면 뒤집힘/주변 구조 분리/복귀 실패는 확정하지 못했다. 수치·영상 검사를 전문가의 생리적 자연스러움 검토로 승격하지 않았다.

주요 검증은 다음과 같다.

- `node --experimental-strip-types atlas-web/scripts/buildLearnerMotionRuntime.mjs --check` — pass, selectors 267 / actions 1,166 / source-bound candidates 1,159.
- `python3 atlas-data/schemas/validate_motion_learning.py --check` — pass, 1,166 actions / 1,160 definitions / 1,160 assets / issue 0.
- `node --experimental-strip-types work/evidence/MV1/tools/validate-loader.mjs` — pass, 332/332 target / 71 GLB / error 0.
- `work/evidence/MV1/tools/validate_frozen_artifacts.py` — pass, evidence/hash/count failures 0.
- Frozen product/runtime/registration/authoring input hashes — pass, 17/17; authoring registry records — pass, 56/56.
- browser-backed runtime binding validation — pass, 332/332, fail 0, error 0; capture details/timestamp above.
- `python3 work/tools/sync_execution.py` and `python3 work/tools/sync_execution.py --check` — pass; the generated execution views already matched after the MV1 state update (0 writes, no projection drift).

기계 확인 요약은 [`frozen-artifact-check.json`](../evidence/MV1/2026-10-11-run-01/runtime/frozen-artifact-check.json), 실행 명령·결과는 [`validation-log.json`](../evidence/MV1/2026-10-11-run-01/runtime/validation-log.json), 실제 시각 확인 범위와 제한은 [`visual-review.json`](../evidence/MV1/2026-10-11-run-01/runtime/visual-review.json)에 있다.

## 미확정 관찰 및 queue

확정 결함은 없다. [`defects.json`](../evidence/MV1/2026-10-11-run-01/defects.json)은 이를 비워 두고, 좌우 대퇴직근 무릎 시범에서 보인 smooth outward contour를 **의심 시각 검토 후보**로 따로 기록한다. 두 asset/clip은 각각의 sourceKey·URI·SHA·transform/playback fingerprint·phase sheet·full-cycle recording에 연결돼 있다. 관찰 중 tear/fold/separation/복귀 실패는 없었으며, 돌출이 정상 형태 변화인지 과도한 protrusion인지 현재 화면만으로 결정할 수 없다. severity 표기는 확정 손상 등급이 아니라 medium review priority다.

[`repair-queue.json`](../evidence/MV1/2026-10-11-run-01/repair-queue.json)의 단일 candidate group은 **공통 원인을 확인하기 전 수정 금지** 상태다. 좌우의 endpoint/마스크 정책이 공통 원인인지 별도 authored contour인지 아직 모른다. MV1은 source data/runtime/GLB/authoring을 수정하지 않았다.

## 잔여 unit과 handoff 경계

현재 MV1은 partial이며 다음 정확한 unit을 남긴다.

1. keyframe/midpoint dense contact sheets 220장의 미열람 수동 시각 판단과 필요 시 느린 재생 확인.
2. 좌우 대퇴직근 무릎 시범 2개 `not_checked` contour의 정상 형태 변화/과도 돌출 판별 및 공통 원인 여부 확인.
3. 332 role/side learner mapping의 UI action/return 강조 전환 확인. 이번 highlight contact sheet는 review harness 표시만 확인했다.

이 세 항목을 넘겨 확인하기 전에는 전수 완료라고 하지 않는다. 이후 예정된 다음 task는 **MV2 (Sol High, frozen repair queue의 공통 원인 group 하나 수정)**이나 이번 요청에서 실행하지 않았다. 다음 사용자 요청 없이 MV2를 시작하지 않는다. 다음 MV1 재개 프롬프트는 `work/tasks/MV1.md`에 따라 dense interframe sheet 전부 수동 판정, 좌우 무릎 contour 두 건 해결, 332 role/side learner action/return 강조 전환 확인을 하고 MV1 record만 갱신하는 것이다.

## 상태·보존 기록

이 task에서 추가한 파일은 `work/evidence/MV1/**`, 이 보고서, `work/EXECUTION.json`의 MV1/모션 plan 상태만이다. 시작 시점부터 있던 45 modified tracked files, 583 untracked status entries 및 기타 WIP는 보존했고 commit 대상에서 제외한다. 다음 commit receipt는 included/excluded path·commit hash·잔여 WIP·다음 프롬프트를 별도로 남긴다.

## MV1 후속 조사 — 2026-10-12

### 판정

**MV1은 partial로 유지한다.** 이전 report의 미검사 분량을 다시 조사하지 않고 `2026-10-11-run-01`의 동결 원장, emitted-GLB, 220개 중간 프레임 시트와 기존 actual learner screenshots를 재사용했다. 이번 보충에서 220/220 시트를 직접 판독하고 332/332 learner action/return/emphasis 흐름을 실제 화면에서 확인했다. 다만 34개 대상 매핑에서 형태 판정이 모호해 `not_checked`로 유지했고, 이를 정상 수축으로 승인하지 않았다. 실제 결함으로 확정된 사례는 0개다.

이번 report는 기존 2026-10-11 결과를 보존하며, 후속판의 target-level 판정은 [`target-visual-dispositions.json`](../evidence/MV1/2026-10-12-followup-01/target-visual-dispositions.json)에 별도로 남긴다. 이전 frozen `target-dispositions.json`의 pass 330 / not_checked 2 기록을 수정하지 않았다.

### 기준선·보존 경계

- 후속 기준선 HEAD: `87678fd7d2874d30cbb068317ecfa38e07cbecfd`.
- follow-up 시작 `git status --porcelain=v2 -z`: SHA-256 `ee8eaa1edf8ea5f4fd0d5b921b6ab9bd4c0a5d1c95bdad6e3aa83bced39847fd`, 54,391 bytes; tracked status 50건, untracked status 593건. 원본은 [`start-status-porcelain-v2.z`](../evidence/MV1/2026-10-12-followup-01/start-status-porcelain-v2.z)에 저장했다.
- 17/17 product/runtime/registration/authoring 입력 hash가 동결 inventory와 일치했다. 기존 frozen `inventory.json`, `target-dispositions.json`, `capture-index-v3.json` hash도 각각 `fdb28f…58e6`, `7d1b79…249c`, `6ce444…f0f44`로 시작 시점 값을 보존했다.
- follow-up 소유 경계는 `work/evidence/MV1/2026-10-12-followup-01/**`, 이 report, `work/EXECUTION.json`의 MV1 record와 `motion-quality-review` plan next ID에 한정한다. `AT6` record/파일, frozen 2026-10-11 run, learner runtime·motion authoring·GLB, `OpenSim_Models`, T13 drafts, 기존 사용자 WIP는 보존한다.
- 시작 snapshot과 커밋 전 status 비교에서 AT6 관련 untracked 경로 8개가 사라지고 3개가 나타난 차이를 발견했다. 이 후속 작업에서는 해당 경로를 읽거나 수정·복구·삭제·stage하지 않았고, 모두 커밋에서 제외했다. 다른 소유 외 status 631건은 시작 snapshot과 동일하다. 경로별 차이는 [`out-of-scope-status-delta.json`](../evidence/MV1/2026-10-12-followup-01/out-of-scope-status-delta.json)에 남긴다.
- **검증 경로 복구 기록:** 공용 `validate-loader.mjs`의 첫 실행이 기본 출력 경로인 frozen run-01의 `real-loader-validation.json`에 새 timestamp를 썼다. 시작 snapshot에서 해당 tracked 파일이 clean이었음을 확인하고 즉시 HEAD blob으로 복구했다. 이후 같은 검증기를 follow-up 경로에만 쓰는 사본으로 실행해 결과를 새 versioned directory에 저장했다. 현재 frozen 파일은 시작 HEAD와 일치한다. 상세 기록은 [`validation-record.json`](../evidence/MV1/2026-10-12-followup-01/validation-record.json)에 남긴다.

### 보완 조사 결과

| 항목 | 후속 결과 |
|---|---:|
| 동결된 dense interframe sheet 수동 열람 | 220/220 |
| 실제 emitted-GLB playback group 확인 | 74/74 |
| playback group 중 관찰했으나 판정이 어려운 그룹 | 34 |
| 실제 learner sourceKey/side route | 134/134 |
| 실제 learner mapping의 선택·강조·재생·복귀·rest 확인 | 332/332 |
| 확정 결함 / 자연수축 승인 | 0 / 0 |
| 추가 시각 검토 대상 | pass 298 / not_checked 34 / fail 0 / error 0 |

위 34개의 `not_checked`는 미관찰이 아니다. 모든 대상의 dense sheet를 열어 관찰했고, 구분 필드 `observationState=observed_ambiguous`로 기록했다. 이번 보충의 미관찰 target은 0개다. `pass`는 관찰 범위에서 gross temporal fault를 찾지 못했다는 뜻일 뿐 해부학적 적합성이나 자연스러운 근수축 승인과 다르다. 모든 332 learner-flow 행은 별도 `flowCheckStatus=pass`이며, 이는 버튼/선택/강조/복귀 동작만 통과했다는 뜻이다.

332개 실제 learner UI option의 정규화된 `(sourceKey, side, label, intent)` 집합 SHA-256은 동결 inventory의 기대 집합과 일치했다: `ac570fd46cb9267be948d9490ab6a1291c2d3a968bdd29ec6f0aed77a3e701af`. 134개 route에서 실제 화면 option 수를 모두 대조했고 합계 332였다. 여기서 56개는 learner가 `muscle_action`으로 표시한 작용이고, 276개는 `posture_observation`이다. 후자를 실제 근육 작용으로 부풀리지 않았다. 각 항목은 선택 강조 enabled, 반복 재생 진행, 복귀 조작, progress 0% rest까지 확인했다.

동결 74-group emitted-GLB 영상을 0.25배속으로 그룹 9, 11, 18, 21, 23, 24에서 추가 관찰했다. 각 화면의 74개 그룹 헤더·좌우·clip을 확인했다. 영상 시간 query가 capture index의 nominal clip 누적 시간과 어긋나는 구간은 화면 헤더를 다시 대조했으며, 헤더가 대상과 다르면 그 시간을 대상 증거로 사용하지 않았다. 그룹 21에서는 좌측 팔꿈치 굽힘 action/return을, 그룹 23→24에서는 좌측 어깨 굽힘 action에서 우측 action으로 넘어가는 구간을 확인했다. 느린 재생에서 확인한 것은 gross pop/tear 여부와 화면 가독성뿐이며 생리적 자연스러움은 판정하지 않았다. 자세한 재현 지시·frame 경로는 [`slow-playback-observations.json`](../evidence/MV1/2026-10-12-followup-01/slow-playback-observations.json)과 [`playback-group-review.json`](../evidence/MV1/2026-10-12-followup-01/playback-group-review.json)에 있다.

### 관찰된 모호 사례와 MV2 인계

각 queue entry는 sourceKey, side, asset URI/SHA-256, clip, 정확한 dense-sheet 시간/경로, 재현 순서, 기대 형태, 실제 관찰, 심각도와 영향 target ID를 포함한다. 전체는 [`ambiguous-observations.json`](../evidence/MV1/2026-10-12-followup-01/ambiguous-observations.json) 및 [`repair-queue.json`](../evidence/MV1/2026-10-12-followup-01/repair-queue.json)에 있다.

1. **좌우 대퇴직근 무릎 시범:** playback group 11/18. part 02의 2.25초 이후 준비/말단 샘플에서 매끄러운 외향 contour가 보이지만 정상 형태 변화인지 과도 돌출인지 결정할 수 없다.
2. **좌측 바깥배빗근:** group 9, 1.406–2.500초. 측면의 지속적인 층/톱니 모양 contour가 접촉·관통인지 겹쳐진 이웃 mesh인지 모호하다.
3. **위팔두갈래근 짧은갈래:** group 21, 23, 24. 팔꿈치/어깨 움직임 중 측면의 어두운 층과 target 부착 관계를 판별하기 어렵다. 우측 팔꿈치 group 22는 비교 화면에서 명확한 gross fault가 보이지 않아 queue defect로 넣지 않았다.
4. **손가락·엄지 말단 26개 asset/clip:** groups 45–70. 각 작용은 learner UI에서 재생·복귀되지만 전신 scale에서 미세한 target deformation을 확인하기 어렵다. 작은 관절 excursion이나 layer visibility를 정상으로 추정하지 않았다.
5. **깊은 몸통 저대비 target:** 좌측 longus colli와 우측 lumbar multifidus groups 71/72. gross temporal pop은 보이지 않았으나 target 변형을 분리해 판단하기 어려웠다.

다음은 **MV2 (Sol High)**다. 다섯 ambiguity 중 한 공통 원인 묶음만 선택해 원인을 진단하고 해당 묶음만 수정하는 단계다. 이번 run에서는 MV2를 시작하지 않았고 자동 시작하지 않는다.

### 실제 화면과 검증

- Actual learner screenshots 8개와 screenshots index는 frozen run에서 재사용했다([`visual-evidence-index.json`](../evidence/MV1/2026-10-12-followup-01/visual-evidence-index.json)). 대흉근과 대퇴직근의 기존 rest·준비·중간·최대·복귀 화면을 덮어쓰지 않았다. 새 quarter-speed CUA replay frame은 도구 화면에서 판독했지만 이미지 payload 자체는 별도 파일로 저장되지 않았으므로 persistent screenshot이라고 주장하지 않는다. 대신 변경하지 않은 frozen continuous video와 220개 indexed sheets에 대상·frame 재현 정보를 연결했다.
- `buildLearnerMotionRuntime.mjs --check`: pass (267 selectors, 1,166 actions, 1,159 playable source-bound candidates).
- `validate_motion_learning.py --check`: pass (1,166 actions / 1,160 definitions / 1,160 assets / issue 0).
- follow-up 위치에 출력한 실제 `loadAnimationScene` loader 검사: pass 332/332, unique GLB 71, error 0 ([`real-loader-validation.json`](../evidence/MV1/2026-10-12-followup-01/runtime/real-loader-validation.json)).
- 후속 evidence validator: pass; 17 frozen hashes, 332 UI identities, 220 sheets, 74 groups, 332 visual dispositions와 5 queue group을 대조했다 ([`validate_followup.py`](../evidence/MV1/2026-10-12-followup-01/tools/validate_followup.py)).
- `python3 work/tools/sync_execution.py`는 0 execution view를 갱신했고 `--check`는 projection 일치로 통과했다. 명령별 결과와 AT6/동결 경계 검증은 [`validation-record.json`](../evidence/MV1/2026-10-12-followup-01/validation-record.json)에 보존한다. local commit receipt는 같은 후속 evidence 디렉터리에 남긴다.

### 현재 잔여 unit

MV1은 220장·74 group·332 learner flow를 전수 조사했지만, 34 target의 시각적 형태 판정이 남아 **partial**이다. 미조사 항목은 없다. 다섯 `observed_ambiguous` queue를 자연 형태나 결함으로 임의 판정하지 말고, 사용자 요청이 있을 때 다음 MV2가 그중 하나의 공통 원인만 진단하도록 넘긴다.
