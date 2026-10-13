# MV2·AT 순서별 붙여 넣을 프롬프트

**2026-10-13 정정:** MV2와 AT8은 완료했고 AT9/10은 위치가 미완이다. 현재는 [체표·취혈자세 보완 프롬프트](../acupoint-surface-posture-2026-10-13/PROMPTS-IN-ORDER.md)를 우선한다. 아래 MV2 지시를 재실행하지 않는다. AT11 이후 기존 순서는 유지한다.

2026-10-12 Q03 중단 원인 재검토. **현재 실행 프롬프트의 단일 기준**이다.
한 번에 아래 한 코드블록을 사용한다. 현재 시작은 **1번 MV2 Q03 / Sol xhigh**다.
Q01·q01-learning-quality·Q02는 완료했다. AT1–7/20–22도 반복하지 않는다.
현재 실제 상태가 이 문서 작성 시점보다 앞섰다면 EXECUTION과 최종 evidence를 우선한다.
옛 evidence에 저장된 재개 프롬프트보다 이 문서를 우선하며 완료 근거는 수정하지 않는다.

**기본 순서:** 1번 Q03 수리/검증 → 2번 Q04/Q05 검사 → 실제 결함이 있을 때 3번 수정/종료 → AT8–19 → AT23–29.
시간이 아니라 결과물로 작업을 나눈다. 새 task 번호를 만들지 않는다.
2번에서 필수 검증이 모두 끝났으면 3번은 생략한다. 그래도 남은 사실상의 실패를 통과로 바꾸지는 않는다.
모델 역할은 프로젝트 난이도에 따른 배정이지 자동 성공 보장이 아니다.

## 공통 실행 계약 — 이번 재계획이 옛 재개 템플릿보다 우선한다

- 실제 상태는 `work/EXECUTION.json.featureWorkUnits.MV2`와 최종 evidence로 확인한다. 이 문서는 실행 계획이다. 과거 evidence의 next prompt는 당시 기록이며 현재 명령이 아니다.
- 재개는 같은 범위의 중단된 WIP 인수·검증·커밋을 포함한다. 최근 수정/같은 HEAD/프로세스 조회 불가는 다른 writer의 증거가 아니다. 실제 동시 쓰기가 확인된 경로만 보호한다. `RESUME-OWNERSHIP.md`의 소유 원칙을 유지한다.
- 원본/OpenSim_Models/T13/역사 evidence/무관한 WIP를 보존한다. 단일 장면·renderer·camera, source identity/hash/권리 기록을 유지한다. UI 배치·테마·카메라 자동 이동은 보류한다. **기존 버튼의 선택·lazy loading·resolver·재생·복원 결함을 고치는 것은 이번 기능 수리 범위다.**
- 현재 재생 가능한 자세 관찰을 근육 수축으로 일괄 재분류하지 않는다. 근육 작용으로 제공할 항목은 기존 작용 자료·부착 역할·실제 clip phase/변형을 대조해 항목별로 수정할 수 있다. 증거 없는 수축/임상/생리 인증은 만들지 않는다.
- 모든 역사 설계·모든 raw evidence를 다시 읽지 않는다. 현재 명세, EXECUTION의 현재 MV2, 최신 요약과 지정된 실제 입력부터 읽고 실패 원인에 해당하는 코드만 확장해서 읽는다.
- 입력 hash가 같은 기존 GLB 수치 QC는 재사용한다. runtime/loader/material/선택 로직이 바뀌면 영향을 받는 실제 앱 검증은 다시 한다. 자산 hash만 같다고 runtime QA까지 재사용하지 않는다.
- 검사 앱은 현재 checkout의 서버·포트·반환 HTML·필요 chunk/GLB·실행 revision을 먼저 확인한다. 서버를 필요하면 시작하고 준비 응답을 확인한다. **사용자 Chrome의 화면 좌표/오래된 AX 번호 대신, 도구가 지원하는 독립 IAB/브라우저 탭에서 역할·이름 기반 실제 버튼 조작을 우선한다.** 사용자 제어 차단을 우회하지 않는다. 단순 CLI/DOM 상태를 영상 통과로 대체하지 않는다.
- 중단 대비 체크포인트는 같은 evidence 폴더의 compact manifest에 입력 fingerprint·현재 단계·통과한 항목·남은 정확한 항목·재현 명령/화면 경로를 갱신한다. 매번 새 전체 스냅샷/원장/QA viewer를 만들지 않는다. 도구가 허용하는 실제 화면 캡처와 짧은 contact sheet를 보존한다.
- 테스트는 수정 영역 중심으로 실행하고 runtime 변경 때 typecheck/build와 필요한 통합 검증을 한다. 변경이 없는 전체 빌드/전수 MV1 검사를 승인 의식처럼 반복하지 않는다.
- report/evidence와 최신 EXECUTION의 MV2만 갱신하고 `python3 work/tools/sync_execution.py` 및 `--check`를 실행한다. 소유 변경만 선택적으로 로컬 커밋한다. 다른 WIP/비밀자료/임시 산출물은 제외한다. 해시·포함/제외·잔여 변경·다음 단계 하나를 보고한다. 자동 다음 실행/위임/push/배포/진단/치료/침 시뮬레이션은 하지 않는다.

## 판정과 종료 기준

| 항목 | 통과에 필요한 것 | 통과로 바꾸면 안 되는 것 |
|---|---|---|
| 실제 재생 | 선택한 source + actionId + clip/hash가 실제 loader에 연결되고 같은 장면에서 한 주기와 복귀가 보임 | 검색 0건만 보고 자료 없음, CLI QC만 보고 재생 성공 |
| 형태·학습 표현 | 전체 주기 및 준비/중간/최대/복귀에서 부착 관계·윤곽·주변 구조가 이해되며 비정상 돌출/분리/뒤집힘/점프가 없음 | 통째 scale·숨김·각도 축소·색만으로 결함 은폐 |
| 정상 원본 한계 | rest와 motion의 차이, 국소 관찰 및 실측으로 기존 표면 겹침과 새 변형 결함을 구분 | 모든 겹침을 자동 결함 또는 자동 정상으로 일괄 판정 |
| 화면 표현 보류 | 수동으로 실제 변형을 확인한 뒤 자동 framing/배치만 후속 UI로 남김 | 관찰을 못한 항목을 UI 보류로 바꿔 완료 |
| 전체 MV2 | 동결된 Q01–Q05 34매핑의 필수 판정 + q01 학습 표현 + 공통 재생 회귀가 해결됨 | 모든 근육의 새 수축 animation/교수 승인/공개 권리까지 완료라고 주장 |

현재 완료 3매핑(Q01 2 + Q02 1), 미완 31매핑(Q03 3 + Q04 26 + Q05 2)이다. `partial`은 전체 큐의 상태와 unit의 상태를 따로 보고한다. 사람 검토 미수행은 자동 기술 차단 사유가 아니며 선택적 검토/공개 배포 hold는 별도 유지한다. 정당한 필수 실패를 문구만 바꿔 승인하지 않는다.

공통 재생/중단/재시작/원본·선택·레이어 복원/경혈 점·면 재진입 검사는 같은 runtime fingerprint의 대표 경로에서 한 묶음으로 수행한다. 각 매핑은 **정확한 연결·한 주기·중간 자세·국소 형태**를 빠짐없이 확인한다. 공통 검사를 31번 복제하지 않는다. 영향이 다른 loader/clip family가 있으면 그 분기만 추가한다.

## 1. Q03 실제 재생·형태 판정·필요 수리 — Sol xhigh

```text
HUMAN ATLAS에서 MV2 Q03만 구현·검증까지 마무리해라. 담당 Sol xhigh.
work/tasks/MV2.md, work/EXECUTION.json의 최신 MV2,
work/plans/mv2-at-integrated-2026-10-12/PROMPTS-IN-ORDER.md의 공통 계약과 1번,
최신 MV2 report 및 record가 가리키는 validation/repairQueue를 읽어라.
이 재개는 Q03 기존 WIP 인수와 필요한 기능 수정을 포함한다.
Q01 engineering·q01-learning-quality·Q02 완료를 보존하고 반복하지 마라.

확인된 원인부터 처리한다. Q03 옵션은 현재 posture_observation이므로
'근육 작용 찾기' 검색 0건은 clip 부재가 아니다.
실제 선택 경로는 source 선택 → 기능 → '자세에서 관찰하기' 펼치기
→ 정확한 동작 선택 → '움직임으로 이해하기'다.
현재 고정 대상은 다음 3개다. 최신 등록과 hash도 대조해라.
- 왼쪽 source ZA-c7010a9-b20b574e456449c5d571c7a1,
  motion-option-298: 팔꿈치 굽힘, group21, elbow-flexion-left-source-frame-r4.
- 같은 왼쪽 source, motion-option-297: 어깨 앞쪽 굽힘,
  group23, shoulder-flexion-left-source-frame-r4.
- 오른쪽 source ZA-c7010a9-a0c2ea00609e874a7faa926d,
  motion-option-299: 어깨 앞쪽 굽힘, group24, shoulder-flexion-right-source-frame-r4.
같은 source의 서로 다른 clip을 하나로 세지 마라.

먼저 기존 경로로 재생해라. 실제 연결/lazy load/선택/재생 결함이 재현되면
관련 공통 코드와 회귀 검사를 수정하여 이번 범위에서 해결해라.
검색 0건이나 disabled 버튼만 기록하고 끝내지 마라.
기존 경로가 정상이라면 UI를 새로 만들지 마라.
근육 작용으로 제공할 항목은 기존 action 근거·부착/phase·실제 변형을 대조해
필요한 해당 항목만 보완한다. 단순 learningIntent 변경은 수축 구현이 아니다.

현재 checkout의 살아 있는 서버와 asset 응답을 확인한 뒤,
도구가 허용하는 독립 브라우저 탭과 실제 버튼으로 세 clip을 재생해라.
사용자 Chrome 포커스/오래된 AX 번호에 의존하지 마라.
1배속 전체 주기 및 필요한 느린 관찰, 준비·중간·최대·작용·복귀를 보고
이두근의 부착·윤곽·주변 구조와 좌우를 실제 화면으로 확인해라.
공통 중단/재시작/선택·레이어·원본 복원/경혈 재진입은 공유 경로 기준 한 번 묶어 검사한다.
기하 결함이 확인되면 source/frame/pivot/weights/보간/접촉 중 원인을 좁혀
기존 offline authoring·source-bound replacement·공통 예산 계약으로 최소 수리하고 재검증해라.
정상이라면 기존 GLB를 보존하고 관찰 근거로 Q03을 닫아라.
수축 기능과 자세 관찰 범위는 보고서에서 정확히 구분한다.

중단돼도 같은 범위의 체크포인트부터 이어가라. 같은 자료를 처음부터 재조사하지 마라.
Q03의 3개 판정과 변경 영향 검증을 마친 뒤 보고서/evidence/EXECUTION의 MV2,
sync 및 --check와 소유 변경의 로컬 커밋까지 마무리해라.
UI·카메라 개편, Q04/Q05·AT 자동 실행, push·배포는 하지 마라.
전체 MV2의 partial과 이번 Q03 통과 여부를 구분해 보고하고 멈춰라.
```

## 2. Q04/Q05 28매핑 검사와 가능한 경우 종료 — Luna Max

```text
HUMAN ATLAS에서 MV2 Q04/Q05의 남은 검증 묶음만 수행해라. 담당 Luna Max.
work/tasks/MV2.md, 최신 EXECUTION의 MV2와 지정된 최종 evidence,
work/plans/mv2-at-integrated-2026-10-12/PROMPTS-IN-ORDER.md의 공통 계약과 2번을 읽어라.
이 요청은 두 기존 검증 그룹을 한 번에 처리하는 범위다. 새 task ID를 만들지 마라.
Q03의 재생 경로/공통 회귀 결과와 같은 unit의 기존 WIP를 인수·재사용해라.
Q01/Q02/Q03가 이미 통과했다면 재조사하지 마라.

Q04 26개와 Q05 2개 중 최신 미판정만 hash·source·action·clip 기준으로 확정한다.
각각 현재 learningIntent에 맞는 실제 UI 경로를 사용한다.
posture_observation은 기능의 '자세에서 관찰하기'에서 선택한다.
근육 작용 검색에 안 나온다는 이유로 absent/blocked 판정하지 마라.
고정 서버/독립 탭의 실제 앱에서 해당 근육·부착·주변 구조가 보이도록 수동 관찰하고
한 주기와 준비·중간·최대·복귀를 확인한다. 필요한 항목만 느리게 다시 본다.
입력이 같은 기존 dense GLB QC는 재사용하고 화면 판정은 항목별로 남긴다.
공통 lifecycle 회귀는 동일 코드 기준 결과를 재사용하고 달라진 분기만 추가한다.

결과를 정상/실제 변형·재생 결함/관찰 후 UI만 보류/검증 불가로 구분해라.
실제 결함은 asset·source·action·clip·발생 시점·기대/관찰·캡처·추정 공통 원인을 기록한다.
정확한 원인을 찾을 수 없으면 추정임을 표시하고 성공으로 바꾸지 마라.
geometry/authoring/repair manifest/기존 UI·카메라를 수정하지 마라.
브라우저가 막혔으면 가능한 코드·파일 판정까지 끝내고 정확한 도구 실패와 미실행 항목을 남긴다.
현재 지원되는 경로를 확인하지 않은 채 '승인 없음'이라는 포괄적 이유로 중단하지 마라.

28개 결과를 compact 표로 통합하고 실제 결함만 공통 원인으로 묶어 Sol에 넘겨라.
모든 필수 mapping 판정과 공통 회귀가 이미 통과했다면 이번 실행에서
Q01–Q05 34개와 q01 학습 표현을 대조하여 MV2 scoped acceptance까지 닫아라.
단순 종료 보고를 위한 별도 Sol 실행은 필요 없다.
그 외에는 정확한 남은 결함 목록을 3번 프롬프트의 고정 입력으로 남긴다.
report/evidence/EXECUTION의 MV2·sync/--check·소유 로컬 커밋을 마치고 멈춰라.
AT 자동 실행·위임·push·배포는 하지 마라.
```

## 3. 실제 잔여 결함이 있을 때만 수정·종료 — Sol xhigh

```text
HUMAN ATLAS에서 MV2의 확인된 잔여 결함 수정과 종료만 수행해라. 담당 Sol xhigh.
work/tasks/MV2.md, 최신 EXECUTION의 MV2,
work/plans/mv2-at-integrated-2026-10-12/PROMPTS-IN-ORDER.md의 공통 계약과 3번,
Q03 및 Q04/Q05의 최신 결함 표·실제 입력/evidence를 읽어라.
MV2가 이미 acceptancePassed=true이고 필수 근거가 일치하면 재수리하지 말고 결과를 알려라.

이번 입력은 Q03/Q04/Q05에 남은 구체적 결함 목록이다.
동일 원인들을 묶어 기존 공통 authoring/resolver/player 중 해당 경로를 한 번 고치고,
영향 자산만 재생성·검증해라. 원인 그룹 하나를 고친 뒤 관성적으로 끝내지 말고,
이번에 고정한 잔여 목록의 수정·회귀·종료까지 하나의 MV2 요청으로 수행해라.
새 근육/새 task/전수 재조사로 범위를 늘리지 마라.
기존 정상 GLB/통과 결과를 보존하고 수정된 자산은 versioned replacement로 등록한다.
통째 scale·숨김·정지·각도 축소·임계값 완화로 결함을 감추지 마라.

실제 learner에서 수정된 clip의 정확한 연결, 한 주기·중간·복귀와 주변 구조를 확인한다.
공통 runtime 변경이 있으면 영향 분기의 선택/중단/원본 복원/경혈 점·면 재진입을 회귀한다.
기존 화면을 사용하고 UI·카메라 정책을 개편하지 마라.
같은 입력의 이미 통과한 dense QC/검사는 재사용한다.

34개 기존 매핑과 q01 학습 표현에서 필수 미판정/실패가 0이면
MV2 scoped acceptance를 완료하고 큐·보고서·EXECUTION을 일치시켜라.
선택적 human review/공개 권리 hold/후속 UI/전신 신규 동작 제작은 별도 상태를 유지한다.
필수 기준이 남으면 이유를 은폐하지 말고 정확한 재현/수정 시도/필요 입력만 남긴다.
새 번호나 '승인 없음'만 반복하는 종료는 하지 마라.
검증·evidence·sync/--check와 소유 변경의 로컬 커밋을 마치고 다음 AT8을 알려라.
AT8 자동 시작·push·배포는 하지 마라.
```

## 4. AT8부터 AT29까지

기존 AT 순서를 유지한다. 아래 프롬프트 하나로 해당 task를 끝까지 수행한다.
Luna 작업에서 실제 공통 기하/계약 결함이 확인되면 완료 가능한 입력을 먼저 처리한 뒤,
정확한 재현·영향 코드·최소 필요 수정만 같은 ID의 Sol xhigh 인계로 남긴다.
모델이 Luna라는 이유 또는 교수 검토 없음만으로 미리 partial을 만들지 않는다.

### AT8 — 다경맥 공통 연결과 LI/TE 43혈 · Sol xhigh

```text
HUMAN ATLAS에서 AT8만 수행해라. 담당 Sol xhigh.
AGENTS.md, 최신 EXECUTION의 해당 record와 acupoint-at-361 순서,
work/tasks/AT8.md, work/plans/mv2-at-integrated-2026-10-12/START-HERE.md,
30/31 설계의 해당 범위와 실제 선행 보고서·최종 자산/evidence를 읽어라.
이번 범위: 먼저 LU 고정 schema/loader/선택 side/sections/전체점 경로를 registry 기반으로 일반화한다. 361 catalog를 기준으로 부분 package·code+side·정중·중복 충돌을 검사하고 LU 회귀를 보존한다. 실제 LI/TE 양측 86 instance의 native 지표·위치·구간 경로를 작성·검증한다. 정중 지원의 기술 fixture는 제품 위치로 내보내지 않는다.
시작 HEAD/status/실제 입력 hash와 소유 경계를 기록하고 최신 완료 결과를 재사용해라.
공통 compiler/loader/renderer를 재사용하고 task별 분기를 복제하지 마라.
등록 목록·교육용 실제 표시·정밀 위치·교재 설명·사람 검토·공개 권리를 구분해라.
교육용 근사는 실제 모델 지표로 근거 있게 작성하고 자료 부재를 허위 좌표나 가짜 면으로 채우지 마라.
이번 task의 필수 자동 검사와 실제 앱 선택/side/가림/전환/복귀를 검증해라.
원본/OpenSim_Models/T13/사용자 WIP/역사 evidence를 보존한다.
카메라 정책·UI 디자인·보기옵션·홈·로딩을 개편하지 마라. 기존 기능과 최소 콘텐츠 연결은 유지한다.
최신 EXECUTION을 다시 읽고 AT8 record와 해당 feature plan 다음 ID만 갱신한다.
work/reports/AT8.md와 versioned work/evidence/AT8/에 결과·실제 미완을 남겨라.
sync_execution.py 및 --check 후 소유 변경만 선별 로컬 커밋한다.
해시·포함/제외·잔여 변경과 다음 ID/프롬프트를 적고 멈춰라.
계획상 다음은 AT9. 실제 선행/미완을 대조하고 자동 실행하지 마라.
자동 위임·push·배포·진단·치료·침 시뮬레이션 금지.
```

### AT9 — HT/PC/SI 37혈 · Luna Max

```text
HUMAN ATLAS에서 AT9만 수행해라. 담당 Luna Max.
AGENTS.md, 최신 EXECUTION의 해당 record와 acupoint-at-361 순서,
work/tasks/AT9.md, work/plans/mv2-at-integrated-2026-10-12/START-HERE.md,
30/31 설계의 해당 범위와 실제 선행 보고서·최종 자산/evidence를 읽어라.
이번 범위: AT8 공통 계약으로 양측 74 instance를 처리한다. 손바닥·팔 안쪽·견갑부·귀의 실제 해부 지표를 확인한다. 없는 carrier를 손등이나 다른 면으로 대체하지 않는다.
시작 HEAD/status/실제 입력 hash와 소유 경계를 기록하고 최신 완료 결과를 재사용해라.
공통 compiler/loader/renderer를 재사용하고 task별 분기를 복제하지 마라.
등록 목록·교육용 실제 표시·정밀 위치·교재 설명·사람 검토·공개 권리를 구분해라.
교육용 근사는 실제 모델 지표로 근거 있게 작성하고 자료 부재를 허위 좌표나 가짜 면으로 채우지 마라.
이번 task의 필수 자동 검사와 실제 앱 선택/side/가림/전환/복귀를 검증해라.
원본/OpenSim_Models/T13/사용자 WIP/역사 evidence를 보존한다.
카메라 정책·UI 디자인·보기옵션·홈·로딩을 개편하지 마라. 기존 기능과 최소 콘텐츠 연결은 유지한다.
최신 EXECUTION을 다시 읽고 AT9 record와 해당 feature plan 다음 ID만 갱신한다.
work/reports/AT9.md와 versioned work/evidence/AT9/에 결과·실제 미완을 남겨라.
sync_execution.py 및 --check 후 소유 변경만 선별 로컬 커밋한다.
해시·포함/제외·잔여 변경과 다음 ID/프롬프트를 적고 멈춰라.
계획상 다음은 AT10. 실제 선행/미완을 대조하고 자동 실행하지 마라.
자동 위임·push·배포·진단·치료·침 시뮬레이션 금지.
```

### AT10 — ST1–25 25혈 · Sol xhigh

```text
HUMAN ATLAS에서 AT10만 수행해라. 담당 Sol xhigh.
AGENTS.md, 최신 EXECUTION의 해당 record와 acupoint-at-361 순서,
work/tasks/AT10.md, work/plans/mv2-at-integrated-2026-10-12/START-HERE.md,
30/31 설계의 해당 범위와 실제 선행 보고서·최종 자산/evidence를 읽어라.
이번 범위: 양측 50 instance의 눈·얼굴·목·흉복부 지표를 확인하고 필요한 국소 carrier 예외를 source-bound 방식으로 해결한다. ST1–25 부분 package로 내보내 후속 ST26–45를 덮지 않는다.
시작 HEAD/status/실제 입력 hash와 소유 경계를 기록하고 최신 완료 결과를 재사용해라.
공통 compiler/loader/renderer를 재사용하고 task별 분기를 복제하지 마라.
등록 목록·교육용 실제 표시·정밀 위치·교재 설명·사람 검토·공개 권리를 구분해라.
교육용 근사는 실제 모델 지표로 근거 있게 작성하고 자료 부재를 허위 좌표나 가짜 면으로 채우지 마라.
이번 task의 필수 자동 검사와 실제 앱 선택/side/가림/전환/복귀를 검증해라.
원본/OpenSim_Models/T13/사용자 WIP/역사 evidence를 보존한다.
카메라 정책·UI 디자인·보기옵션·홈·로딩을 개편하지 마라. 기존 기능과 최소 콘텐츠 연결은 유지한다.
최신 EXECUTION을 다시 읽고 AT10 record와 해당 feature plan 다음 ID만 갱신한다.
work/reports/AT10.md와 versioned work/evidence/AT10/에 결과·실제 미완을 남겨라.
sync_execution.py 및 --check 후 소유 변경만 선별 로컬 커밋한다.
해시·포함/제외·잔여 변경과 다음 ID/프롬프트를 적고 멈춰라.
계획상 다음은 AT11. 실제 선행/미완을 대조하고 자동 실행하지 마라.
자동 위임·push·배포·진단·치료·침 시뮬레이션 금지.
```

### AT11 — ST26–45와 SP 41혈 · Luna Max

```text
HUMAN ATLAS에서 AT11만 수행해라. 담당 Luna Max.
AGENTS.md, 최신 EXECUTION의 해당 record와 acupoint-at-361 순서,
work/tasks/AT11.md, work/plans/mv2-at-integrated-2026-10-12/START-HERE.md,
30/31 설계의 해당 범위와 실제 선행 보고서·최종 자산/evidence를 읽어라.
이번 범위: 양측 82 instance의 복부·하지 앞안쪽·발·비경 몸통을 확인한다. AT10의 ST 입력을 보존하고 ST25/26 구간과 채널 합성 중복을 검사한다.
시작 HEAD/status/실제 입력 hash와 소유 경계를 기록하고 최신 완료 결과를 재사용해라.
공통 compiler/loader/renderer를 재사용하고 task별 분기를 복제하지 마라.
등록 목록·교육용 실제 표시·정밀 위치·교재 설명·사람 검토·공개 권리를 구분해라.
교육용 근사는 실제 모델 지표로 근거 있게 작성하고 자료 부재를 허위 좌표나 가짜 면으로 채우지 마라.
이번 task의 필수 자동 검사와 실제 앱 선택/side/가림/전환/복귀를 검증해라.
원본/OpenSim_Models/T13/사용자 WIP/역사 evidence를 보존한다.
카메라 정책·UI 디자인·보기옵션·홈·로딩을 개편하지 마라. 기존 기능과 최소 콘텐츠 연결은 유지한다.
최신 EXECUTION을 다시 읽고 AT11 record와 해당 feature plan 다음 ID만 갱신한다.
work/reports/AT11.md와 versioned work/evidence/AT11/에 결과·실제 미완을 남겨라.
sync_execution.py 및 --check 후 소유 변경만 선별 로컬 커밋한다.
해시·포함/제외·잔여 변경과 다음 ID/프롬프트를 적고 멈춰라.
계획상 다음은 AT12. 실제 선행/미완을 대조하고 자동 실행하지 마라.
자동 위임·push·배포·진단·치료·침 시뮬레이션 금지.
```

### AT12 — BL1–35 35혈 · Sol xhigh

```text
HUMAN ATLAS에서 AT12만 수행해라. 담당 Sol xhigh.
AGENTS.md, 최신 EXECUTION의 해당 record와 acupoint-at-361 순서,
work/tasks/AT12.md, work/plans/mv2-at-integrated-2026-10-12/START-HERE.md,
30/31 설계의 해당 범위와 실제 선행 보고서·최종 자산/evidence를 읽어라.
이번 범위: 양측 70 instance의 눈·두피·척추·천골 기준을 확인한다. BL 부분 package와 실제 분지 순서를 남기고 번호만 보고 직선 연결하지 않는다.
시작 HEAD/status/실제 입력 hash와 소유 경계를 기록하고 최신 완료 결과를 재사용해라.
공통 compiler/loader/renderer를 재사용하고 task별 분기를 복제하지 마라.
등록 목록·교육용 실제 표시·정밀 위치·교재 설명·사람 검토·공개 권리를 구분해라.
교육용 근사는 실제 모델 지표로 근거 있게 작성하고 자료 부재를 허위 좌표나 가짜 면으로 채우지 마라.
이번 task의 필수 자동 검사와 실제 앱 선택/side/가림/전환/복귀를 검증해라.
원본/OpenSim_Models/T13/사용자 WIP/역사 evidence를 보존한다.
카메라 정책·UI 디자인·보기옵션·홈·로딩을 개편하지 마라. 기존 기능과 최소 콘텐츠 연결은 유지한다.
최신 EXECUTION을 다시 읽고 AT12 record와 해당 feature plan 다음 ID만 갱신한다.
work/reports/AT12.md와 versioned work/evidence/AT12/에 결과·실제 미완을 남겨라.
sync_execution.py 및 --check 후 소유 변경만 선별 로컬 커밋한다.
해시·포함/제외·잔여 변경과 다음 ID/프롬프트를 적고 멈춰라.
계획상 다음은 AT13. 실제 선행/미완을 대조하고 자동 실행하지 마라.
자동 위임·push·배포·진단·치료·침 시뮬레이션 금지.
```

### AT13 — BL36–67 32혈 · Luna Max

```text
HUMAN ATLAS에서 AT13만 수행해라. 담당 Luna Max.
AGENTS.md, 최신 EXECUTION의 해당 record와 acupoint-at-361 순서,
work/tasks/AT13.md, work/plans/mv2-at-integrated-2026-10-12/START-HERE.md,
30/31 설계의 해당 범위와 실제 선행 보고서·최종 자산/evidence를 읽어라.
이번 범위: 양측 64 instance를 처리한다. BL41 이후를 모두 다리로 간주하지 말고 등 쪽 경로와 두 줄을 포함한다. AT12 package를 보존하고 분지/구간 합성을 검증한다.
시작 HEAD/status/실제 입력 hash와 소유 경계를 기록하고 최신 완료 결과를 재사용해라.
공통 compiler/loader/renderer를 재사용하고 task별 분기를 복제하지 마라.
등록 목록·교육용 실제 표시·정밀 위치·교재 설명·사람 검토·공개 권리를 구분해라.
교육용 근사는 실제 모델 지표로 근거 있게 작성하고 자료 부재를 허위 좌표나 가짜 면으로 채우지 마라.
이번 task의 필수 자동 검사와 실제 앱 선택/side/가림/전환/복귀를 검증해라.
원본/OpenSim_Models/T13/사용자 WIP/역사 evidence를 보존한다.
카메라 정책·UI 디자인·보기옵션·홈·로딩을 개편하지 마라. 기존 기능과 최소 콘텐츠 연결은 유지한다.
최신 EXECUTION을 다시 읽고 AT13 record와 해당 feature plan 다음 ID만 갱신한다.
work/reports/AT13.md와 versioned work/evidence/AT13/에 결과·실제 미완을 남겨라.
sync_execution.py 및 --check 후 소유 변경만 선별 로컬 커밋한다.
해시·포함/제외·잔여 변경과 다음 ID/프롬프트를 적고 멈춰라.
계획상 다음은 AT14. 실제 선행/미완을 대조하고 자동 실행하지 마라.
자동 위임·push·배포·진단·치료·침 시뮬레이션 금지.
```

### AT14 — KI/LR 41혈 · Luna Max

```text
HUMAN ATLAS에서 AT14만 수행해라. 담당 Luna Max.
AGENTS.md, 최신 EXECUTION의 해당 record와 acupoint-at-361 순서,
work/tasks/AT14.md, work/plans/mv2-at-integrated-2026-10-12/START-HERE.md,
30/31 설계의 해당 범위와 실제 선행 보고서·최종 자산/evidence를 읽어라.
이번 범위: 양측 82 instance의 발바닥·발목 안쪽·다리 안쪽·몸통 지표를 확인한다. KI는 족소음신경이며 nerve 구현 범위가 아니다. 발바닥 표면 지지가 없으면 해당 실제 예외를 해결하거나 정확히 남긴다.
시작 HEAD/status/실제 입력 hash와 소유 경계를 기록하고 최신 완료 결과를 재사용해라.
공통 compiler/loader/renderer를 재사용하고 task별 분기를 복제하지 마라.
등록 목록·교육용 실제 표시·정밀 위치·교재 설명·사람 검토·공개 권리를 구분해라.
교육용 근사는 실제 모델 지표로 근거 있게 작성하고 자료 부재를 허위 좌표나 가짜 면으로 채우지 마라.
이번 task의 필수 자동 검사와 실제 앱 선택/side/가림/전환/복귀를 검증해라.
원본/OpenSim_Models/T13/사용자 WIP/역사 evidence를 보존한다.
카메라 정책·UI 디자인·보기옵션·홈·로딩을 개편하지 마라. 기존 기능과 최소 콘텐츠 연결은 유지한다.
최신 EXECUTION을 다시 읽고 AT14 record와 해당 feature plan 다음 ID만 갱신한다.
work/reports/AT14.md와 versioned work/evidence/AT14/에 결과·실제 미완을 남겨라.
sync_execution.py 및 --check 후 소유 변경만 선별 로컬 커밋한다.
해시·포함/제외·잔여 변경과 다음 ID/프롬프트를 적고 멈춰라.
계획상 다음은 AT15. 실제 선행/미완을 대조하고 자동 실행하지 마라.
자동 위임·push·배포·진단·치료·침 시뮬레이션 금지.
```

### AT15 — GB1–20 20혈 · Sol xhigh

```text
HUMAN ATLAS에서 AT15만 수행해라. 담당 Sol xhigh.
AGENTS.md, 최신 EXECUTION의 해당 record와 acupoint-at-361 순서,
work/tasks/AT15.md, work/plans/mv2-at-integrated-2026-10-12/START-HERE.md,
30/31 설계의 해당 범위와 실제 선행 보고서·최종 자산/evidence를 읽어라.
이번 범위: 양측 40 instance의 눈가·귀·두피·뒤목을 검증한다. 촘촘한 점 순서·carrier seam·가림을 실제 구도로 확인하며 GB21–44와 합성 가능한 부분 package를 작성한다.
시작 HEAD/status/실제 입력 hash와 소유 경계를 기록하고 최신 완료 결과를 재사용해라.
공통 compiler/loader/renderer를 재사용하고 task별 분기를 복제하지 마라.
등록 목록·교육용 실제 표시·정밀 위치·교재 설명·사람 검토·공개 권리를 구분해라.
교육용 근사는 실제 모델 지표로 근거 있게 작성하고 자료 부재를 허위 좌표나 가짜 면으로 채우지 마라.
이번 task의 필수 자동 검사와 실제 앱 선택/side/가림/전환/복귀를 검증해라.
원본/OpenSim_Models/T13/사용자 WIP/역사 evidence를 보존한다.
카메라 정책·UI 디자인·보기옵션·홈·로딩을 개편하지 마라. 기존 기능과 최소 콘텐츠 연결은 유지한다.
최신 EXECUTION을 다시 읽고 AT15 record와 해당 feature plan 다음 ID만 갱신한다.
work/reports/AT15.md와 versioned work/evidence/AT15/에 결과·실제 미완을 남겨라.
sync_execution.py 및 --check 후 소유 변경만 선별 로컬 커밋한다.
해시·포함/제외·잔여 변경과 다음 ID/프롬프트를 적고 멈춰라.
계획상 다음은 AT16. 실제 선행/미완을 대조하고 자동 실행하지 마라.
자동 위임·push·배포·진단·치료·침 시뮬레이션 금지.
```

### AT16 — GB21–44 24혈 · Luna Max

```text
HUMAN ATLAS에서 AT16만 수행해라. 담당 Luna Max.
AGENTS.md, 최신 EXECUTION의 해당 record와 acupoint-at-361 순서,
work/tasks/AT16.md, work/plans/mv2-at-integrated-2026-10-12/START-HERE.md,
30/31 설계의 해당 범위와 실제 선행 보고서·최종 자산/evidence를 읽어라.
이번 범위: 양측 48 instance의 어깨·옆구리·볼기·다리 가쪽·발을 확인한다. GB20/21 구간과 AT15 package 합성을 검증한다.
시작 HEAD/status/실제 입력 hash와 소유 경계를 기록하고 최신 완료 결과를 재사용해라.
공통 compiler/loader/renderer를 재사용하고 task별 분기를 복제하지 마라.
등록 목록·교육용 실제 표시·정밀 위치·교재 설명·사람 검토·공개 권리를 구분해라.
교육용 근사는 실제 모델 지표로 근거 있게 작성하고 자료 부재를 허위 좌표나 가짜 면으로 채우지 마라.
이번 task의 필수 자동 검사와 실제 앱 선택/side/가림/전환/복귀를 검증해라.
원본/OpenSim_Models/T13/사용자 WIP/역사 evidence를 보존한다.
카메라 정책·UI 디자인·보기옵션·홈·로딩을 개편하지 마라. 기존 기능과 최소 콘텐츠 연결은 유지한다.
최신 EXECUTION을 다시 읽고 AT16 record와 해당 feature plan 다음 ID만 갱신한다.
work/reports/AT16.md와 versioned work/evidence/AT16/에 결과·실제 미완을 남겨라.
sync_execution.py 및 --check 후 소유 변경만 선별 로컬 커밋한다.
해시·포함/제외·잔여 변경과 다음 ID/프롬프트를 적고 멈춰라.
계획상 다음은 AT17. 실제 선행/미완을 대조하고 자동 실행하지 마라.
자동 위임·push·배포·진단·치료·침 시뮬레이션 금지.
```

### AT17 — CV1–24 정중 24혈 · Sol xhigh

```text
HUMAN ATLAS에서 AT17만 수행해라. 담당 Sol xhigh.
AGENTS.md, 최신 EXECUTION의 해당 record와 acupoint-at-361 순서,
work/tasks/AT17.md, work/plans/mv2-at-integrated-2026-10-12/START-HERE.md,
30/31 설계의 해당 범위와 실제 선행 보고서·최종 자산/evidence를 읽어라.
이번 범위: 정중 24 instance를 작성한다. right/left로 중복하지 않는다. 회음·전정중선·목·턱의 실제 지표와 접근 가능한 표면을 확인한다. CV1을 다른 표면으로 이동해 완료하지 않는다.
시작 HEAD/status/실제 입력 hash와 소유 경계를 기록하고 최신 완료 결과를 재사용해라.
공통 compiler/loader/renderer를 재사용하고 task별 분기를 복제하지 마라.
등록 목록·교육용 실제 표시·정밀 위치·교재 설명·사람 검토·공개 권리를 구분해라.
교육용 근사는 실제 모델 지표로 근거 있게 작성하고 자료 부재를 허위 좌표나 가짜 면으로 채우지 마라.
이번 task의 필수 자동 검사와 실제 앱 선택/side/가림/전환/복귀를 검증해라.
원본/OpenSim_Models/T13/사용자 WIP/역사 evidence를 보존한다.
카메라 정책·UI 디자인·보기옵션·홈·로딩을 개편하지 마라. 기존 기능과 최소 콘텐츠 연결은 유지한다.
최신 EXECUTION을 다시 읽고 AT17 record와 해당 feature plan 다음 ID만 갱신한다.
work/reports/AT17.md와 versioned work/evidence/AT17/에 결과·실제 미완을 남겨라.
sync_execution.py 및 --check 후 소유 변경만 선별 로컬 커밋한다.
해시·포함/제외·잔여 변경과 다음 ID/프롬프트를 적고 멈춰라.
계획상 다음은 AT18. 실제 선행/미완을 대조하고 자동 실행하지 마라.
자동 위임·push·배포·진단·치료·침 시뮬레이션 금지.
```

### AT18 — GV1–28 정중 28혈 · Sol xhigh

```text
HUMAN ATLAS에서 AT18만 수행해라. 담당 Sol xhigh.
AGENTS.md, 최신 EXECUTION의 해당 record와 acupoint-at-361 순서,
work/tasks/AT18.md, work/plans/mv2-at-integrated-2026-10-12/START-HERE.md,
30/31 설계의 해당 범위와 실제 선행 보고서·최종 자산/evidence를 읽어라.
이번 범위: 정중 28 instance를 작성한다. 후정중선·두피·얼굴과 구강/잇몸 특수 표면을 구분한다. GV28 등 미지지 지점을 외피로 옮겨 찍지 않는다.
시작 HEAD/status/실제 입력 hash와 소유 경계를 기록하고 최신 완료 결과를 재사용해라.
공통 compiler/loader/renderer를 재사용하고 task별 분기를 복제하지 마라.
등록 목록·교육용 실제 표시·정밀 위치·교재 설명·사람 검토·공개 권리를 구분해라.
교육용 근사는 실제 모델 지표로 근거 있게 작성하고 자료 부재를 허위 좌표나 가짜 면으로 채우지 마라.
이번 task의 필수 자동 검사와 실제 앱 선택/side/가림/전환/복귀를 검증해라.
원본/OpenSim_Models/T13/사용자 WIP/역사 evidence를 보존한다.
카메라 정책·UI 디자인·보기옵션·홈·로딩을 개편하지 마라. 기존 기능과 최소 콘텐츠 연결은 유지한다.
최신 EXECUTION을 다시 읽고 AT18 record와 해당 feature plan 다음 ID만 갱신한다.
work/reports/AT18.md와 versioned work/evidence/AT18/에 결과·실제 미완을 남겨라.
sync_execution.py 및 --check 후 소유 변경만 선별 로컬 커밋한다.
해시·포함/제외·잔여 변경과 다음 ID/프롬프트를 적고 멈춰라.
계획상 다음은 AT19. 실제 선행/미완을 대조하고 자동 실행하지 마라.
자동 위임·push·배포·진단·치료·침 시뮬레이션 금지.
```

### AT19 — 361혈·670 instance 통합 대조 · Sol xhigh

```text
HUMAN ATLAS에서 AT19만 수행해라. 담당 Sol xhigh.
AGENTS.md, 최신 EXECUTION의 해당 record와 acupoint-at-361 순서,
work/tasks/AT19.md, work/plans/mv2-at-integrated-2026-10-12/START-HERE.md,
30/31 설계의 해당 범위와 실제 선행 보고서·최종 자산/evidence를 읽어라.
이번 범위: AT6/8–18의 실제 package·등록·evidence를 재사용해 361 code와 670 예정 instance를 대조한다. 표시/선택/side/정밀도/내용을 구분하고 모든 실제 누락을 보완한다. 전체 처음부터 재조사하지 말고 바뀐 입력과 예외를 검사한다. 구강·회음·발바닥 미완이 있으면 정확히 남기고 전체 위치 완료로 선언하지 않는다.
시작 HEAD/status/실제 입력 hash와 소유 경계를 기록하고 최신 완료 결과를 재사용해라.
공통 compiler/loader/renderer를 재사용하고 task별 분기를 복제하지 마라.
등록 목록·교육용 실제 표시·정밀 위치·교재 설명·사람 검토·공개 권리를 구분해라.
교육용 근사는 실제 모델 지표로 근거 있게 작성하고 자료 부재를 허위 좌표나 가짜 면으로 채우지 마라.
이번 task의 필수 자동 검사와 실제 앱 선택/side/가림/전환/복귀를 검증해라.
원본/OpenSim_Models/T13/사용자 WIP/역사 evidence를 보존한다.
카메라 정책·UI 디자인·보기옵션·홈·로딩을 개편하지 마라. 기존 기능과 최소 콘텐츠 연결은 유지한다.
최신 EXECUTION을 다시 읽고 AT19 record와 해당 feature plan 다음 ID만 갱신한다.
work/reports/AT19.md와 versioned work/evidence/AT19/에 결과·실제 미완을 남겨라.
sync_execution.py 및 --check 후 소유 변경만 선별 로컬 커밋한다.
해시·포함/제외·잔여 변경과 다음 ID/프롬프트를 적고 멈춰라.
계획상 다음은 AT23. 실제 선행/미완을 대조하고 자동 실행하지 마라.
자동 위임·push·배포·진단·치료·침 시뮬레이션 금지.
```

### AT23 — 손의 6경맥 전체 범위와 공통 영역 연결 · Sol xhigh

```text
HUMAN ATLAS에서 AT23만 수행해라. 담당 Sol xhigh.
AGENTS.md, 최신 EXECUTION의 해당 record와 acupoint-at-361 순서,
work/tasks/AT23.md, work/plans/mv2-at-integrated-2026-10-12/START-HERE.md,
30/31 설계의 해당 범위와 실제 선행 보고서·최종 자산/evidence를 읽어라.
이번 범위: LU/LI/HT/SI/PC/TE의 mask 자료를 작성한다. 기존 LU 아래팔 양측 부분을 보존·확장하며 흉부·견갑부·목·얼굴까지 해당 근거 범위를 확인한다. 처음에는 다경맥 registry와 독립 mask 가용성/필요 carrier 집합을 공통화한다. 점이 미확정인 곳에 가짜 점을 만들지 말고 면의 독립 검증으로 표시한다. 공통 renderer/DEV 편집기와 공유 geometry·취소·해제를 재사용한다.
시작 HEAD/status/실제 입력 hash와 소유 경계를 기록하고 최신 완료 결과를 재사용해라.
공통 compiler/loader/renderer를 재사용하고 task별 분기를 복제하지 마라.
등록 목록·교육용 실제 표시·정밀 위치·교재 설명·사람 검토·공개 권리를 구분해라.
교육용 근사는 실제 모델 지표로 근거 있게 작성하고 자료 부재를 허위 좌표나 가짜 면으로 채우지 마라.
이번 task의 필수 자동 검사와 실제 앱 선택/side/가림/전환/복귀를 검증해라.
원본/OpenSim_Models/T13/사용자 WIP/역사 evidence를 보존한다.
카메라 정책·UI 디자인·보기옵션·홈·로딩을 개편하지 마라. 기존 기능과 최소 콘텐츠 연결은 유지한다.
최신 EXECUTION을 다시 읽고 AT23 record와 해당 feature plan 다음 ID만 갱신한다.
work/reports/AT23.md와 versioned work/evidence/AT23/에 결과·실제 미완을 남겨라.
sync_execution.py 및 --check 후 소유 변경만 선별 로컬 커밋한다.
해시·포함/제외·잔여 변경과 다음 ID/프롬프트를 적고 멈춰라.
계획상 다음은 AT24. 실제 선행/미완을 대조하고 자동 실행하지 마라.
자동 위임·push·배포·진단·치료·침 시뮬레이션 금지.
```

### AT24 — ST/SP/KI/LR 4개 영역 · Luna Max

```text
HUMAN ATLAS에서 AT24만 수행해라. 담당 Luna Max.
AGENTS.md, 최신 EXECUTION의 해당 record와 acupoint-at-361 순서,
work/tasks/AT24.md, work/plans/mv2-at-integrated-2026-10-12/START-HERE.md,
30/31 설계의 해당 범위와 실제 선행 보고서·최종 자산/evidence를 읽어라.
이번 범위: AT23 공통 경로를 사용해 근거 범위의 몸통·머리·하지·발 mask를 작성한다. 위경 폭은 구간별 해부 지표와 경계 수정으로 보완하고 전후 비교를 남긴다. 전체 폭 비율 축소나 점 반경을 영역 근거로 쓰지 않는다.
시작 HEAD/status/실제 입력 hash와 소유 경계를 기록하고 최신 완료 결과를 재사용해라.
공통 compiler/loader/renderer를 재사용하고 task별 분기를 복제하지 마라.
등록 목록·교육용 실제 표시·정밀 위치·교재 설명·사람 검토·공개 권리를 구분해라.
교육용 근사는 실제 모델 지표로 근거 있게 작성하고 자료 부재를 허위 좌표나 가짜 면으로 채우지 마라.
이번 task의 필수 자동 검사와 실제 앱 선택/side/가림/전환/복귀를 검증해라.
원본/OpenSim_Models/T13/사용자 WIP/역사 evidence를 보존한다.
카메라 정책·UI 디자인·보기옵션·홈·로딩을 개편하지 마라. 기존 기능과 최소 콘텐츠 연결은 유지한다.
최신 EXECUTION을 다시 읽고 AT24 record와 해당 feature plan 다음 ID만 갱신한다.
work/reports/AT24.md와 versioned work/evidence/AT24/에 결과·실제 미완을 남겨라.
sync_execution.py 및 --check 후 소유 변경만 선별 로컬 커밋한다.
해시·포함/제외·잔여 변경과 다음 ID/프롬프트를 적고 멈춰라.
계획상 다음은 AT25. 실제 선행/미완을 대조하고 자동 실행하지 마라.
자동 위임·push·배포·진단·치료·침 시뮬레이션 금지.
```

### AT25 — BL/GB 2개 영역 · Luna Max

```text
HUMAN ATLAS에서 AT25만 수행해라. 담당 Luna Max.
AGENTS.md, 최신 EXECUTION의 해당 record와 acupoint-at-361 순서,
work/tasks/AT25.md, work/plans/mv2-at-integrated-2026-10-12/START-HERE.md,
30/31 설계의 해당 범위와 실제 선행 보고서·최종 자산/evidence를 읽어라.
이번 범위: 등·허리·머리·옆구리·볼기·하지·발의 실제 근거 구간 mask를 작성한다. 방광경 두 경로·독맥 중앙 영역을 구분하며 모든 면을 하나의 넓은 띠로 채우지 않는다. carrier 이음과 overlap을 확인한다.
시작 HEAD/status/실제 입력 hash와 소유 경계를 기록하고 최신 완료 결과를 재사용해라.
공통 compiler/loader/renderer를 재사용하고 task별 분기를 복제하지 마라.
등록 목록·교육용 실제 표시·정밀 위치·교재 설명·사람 검토·공개 권리를 구분해라.
교육용 근사는 실제 모델 지표로 근거 있게 작성하고 자료 부재를 허위 좌표나 가짜 면으로 채우지 마라.
이번 task의 필수 자동 검사와 실제 앱 선택/side/가림/전환/복귀를 검증해라.
원본/OpenSim_Models/T13/사용자 WIP/역사 evidence를 보존한다.
카메라 정책·UI 디자인·보기옵션·홈·로딩을 개편하지 마라. 기존 기능과 최소 콘텐츠 연결은 유지한다.
최신 EXECUTION을 다시 읽고 AT25 record와 해당 feature plan 다음 ID만 갱신한다.
work/reports/AT25.md와 versioned work/evidence/AT25/에 결과·실제 미완을 남겨라.
sync_execution.py 및 --check 후 소유 변경만 선별 로컬 커밋한다.
해시·포함/제외·잔여 변경과 다음 ID/프롬프트를 적고 멈춰라.
계획상 다음은 AT26. 실제 선행/미완을 대조하고 자동 실행하지 마라.
자동 위임·push·배포·진단·치료·침 시뮬레이션 금지.
```

### AT26 — CV/GV 면과 14경맥 비교 기능 · Sol xhigh

```text
HUMAN ATLAS에서 AT26만 수행해라. 담당 Sol xhigh.
AGENTS.md, 최신 EXECUTION의 해당 record와 acupoint-at-361 순서,
work/tasks/AT26.md, work/plans/mv2-at-integrated-2026-10-12/START-HERE.md,
30/31 설계의 해당 범위와 실제 선행 보고서·최종 자산/evidence를 읽어라.
이번 범위: 근거가 확인된 CV/GV 학습 강조 면과 14경맥 mask 선택/비교 연결을 기존 제어에 적용한다. 임독맥에 고유 경근을 창작하지 않는다. 위치가 미완인 점과 면 표시를 독립 처리하고 점·근육 윤곽이 읽히는지 확인한다. 버튼 배치/색상 체계/패널/카메라를 재설계하지 않는다.
시작 HEAD/status/실제 입력 hash와 소유 경계를 기록하고 최신 완료 결과를 재사용해라.
공통 compiler/loader/renderer를 재사용하고 task별 분기를 복제하지 마라.
등록 목록·교육용 실제 표시·정밀 위치·교재 설명·사람 검토·공개 권리를 구분해라.
교육용 근사는 실제 모델 지표로 근거 있게 작성하고 자료 부재를 허위 좌표나 가짜 면으로 채우지 마라.
이번 task의 필수 자동 검사와 실제 앱 선택/side/가림/전환/복귀를 검증해라.
원본/OpenSim_Models/T13/사용자 WIP/역사 evidence를 보존한다.
카메라 정책·UI 디자인·보기옵션·홈·로딩을 개편하지 마라. 기존 기능과 최소 콘텐츠 연결은 유지한다.
최신 EXECUTION을 다시 읽고 AT26 record와 해당 feature plan 다음 ID만 갱신한다.
work/reports/AT26.md와 versioned work/evidence/AT26/에 결과·실제 미완을 남겨라.
sync_execution.py 및 --check 후 소유 변경만 선별 로컬 커밋한다.
해시·포함/제외·잔여 변경과 다음 ID/프롬프트를 적고 멈춰라.
계획상 다음은 AT27. 실제 선행/미완을 대조하고 자동 실행하지 마라.
자동 위임·push·배포·진단·치료·침 시뮬레이션 금지.
```

### AT27 — 교재 importer와 기존 카드 콘텐츠 · Luna Max

```text
HUMAN ATLAS에서 AT27만 수행해라. 담당 Luna Max.
AGENTS.md, 최신 EXECUTION의 해당 record와 acupoint-at-361 순서,
work/tasks/AT27.md, work/plans/mv2-at-integrated-2026-10-12/START-HERE.md,
30/31 설계의 해당 범위와 실제 선행 보고서·최종 자산/evidence를 읽어라.
이번 범위: 제공된 교재 표를 코드 기준으로 연결하는 importer와 기존 한글 카드 바인딩을 구현한다. 입력 없음/코드 오류/단위 오류/내용 충돌을 검사한다. 원문·판본·쪽·AI 정리와 learner 문장을 분리한다. 미제공 교과서 해설을 창작하지 않으며 importer 완료와 내용 입력 완료를 구분한다. 카드 레이아웃은 개편하지 않는다.
시작 HEAD/status/실제 입력 hash와 소유 경계를 기록하고 최신 완료 결과를 재사용해라.
공통 compiler/loader/renderer를 재사용하고 task별 분기를 복제하지 마라.
등록 목록·교육용 실제 표시·정밀 위치·교재 설명·사람 검토·공개 권리를 구분해라.
교육용 근사는 실제 모델 지표로 근거 있게 작성하고 자료 부재를 허위 좌표나 가짜 면으로 채우지 마라.
이번 task의 필수 자동 검사와 실제 앱 선택/side/가림/전환/복귀를 검증해라.
원본/OpenSim_Models/T13/사용자 WIP/역사 evidence를 보존한다.
카메라 정책·UI 디자인·보기옵션·홈·로딩을 개편하지 마라. 기존 기능과 최소 콘텐츠 연결은 유지한다.
최신 EXECUTION을 다시 읽고 AT27 record와 해당 feature plan 다음 ID만 갱신한다.
work/reports/AT27.md와 versioned work/evidence/AT27/에 결과·실제 미완을 남겨라.
sync_execution.py 및 --check 후 소유 변경만 선별 로컬 커밋한다.
해시·포함/제외·잔여 변경과 다음 ID/프롬프트를 적고 멈춰라.
계획상 다음은 AT28. 실제 선행/미완을 대조하고 자동 실행하지 마라.
자동 위임·push·배포·진단·치료·침 시뮬레이션 금지.
```

### AT28 — 현재 UI 기능 통합 회귀 · Luna Max

```text
HUMAN ATLAS에서 AT28만 수행해라. 담당 Luna Max.
AGENTS.md, 최신 EXECUTION의 해당 record와 acupoint-at-361 순서,
work/tasks/AT28.md, work/plans/mv2-at-integrated-2026-10-12/START-HERE.md,
30/31 설계의 해당 범위와 실제 선행 보고서·최종 자산/evidence를 읽어라.
이번 범위: AT19/26/27의 실제 결과로 검색·경맥·양측·정중·전체점·영역·따라보기·키보드·reduced motion·해부 복귀를 390/1024/1440에서 검증한다. 움직임 시작 시 정지 경혈이 종료되고 복귀 후 다시 연결되는지도 확인한다. 클릭/취소/상태 복원 등 기능 결함만 수정한다. 미적 배치/카메라 연출 불편은 후속 UI로 기록한다. 최종 UI 개편 완료라고 하지 않는다.
시작 HEAD/status/실제 입력 hash와 소유 경계를 기록하고 최신 완료 결과를 재사용해라.
공통 compiler/loader/renderer를 재사용하고 task별 분기를 복제하지 마라.
등록 목록·교육용 실제 표시·정밀 위치·교재 설명·사람 검토·공개 권리를 구분해라.
교육용 근사는 실제 모델 지표로 근거 있게 작성하고 자료 부재를 허위 좌표나 가짜 면으로 채우지 마라.
이번 task의 필수 자동 검사와 실제 앱 선택/side/가림/전환/복귀를 검증해라.
원본/OpenSim_Models/T13/사용자 WIP/역사 evidence를 보존한다.
카메라 정책·UI 디자인·보기옵션·홈·로딩을 개편하지 마라. 기존 기능과 최소 콘텐츠 연결은 유지한다.
최신 EXECUTION을 다시 읽고 AT28 record와 해당 feature plan 다음 ID만 갱신한다.
work/reports/AT28.md와 versioned work/evidence/AT28/에 결과·실제 미완을 남겨라.
sync_execution.py 및 --check 후 소유 변경만 선별 로컬 커밋한다.
해시·포함/제외·잔여 변경과 다음 ID/프롬프트를 적고 멈춰라.
계획상 다음은 AT29. 실제 선행/미완을 대조하고 자동 실행하지 마라.
자동 위임·push·배포·진단·치료·침 시뮬레이션 금지.
```

### AT29 — 성능과 로컬 전달 산출물 · Sol xhigh

```text
HUMAN ATLAS에서 AT29만 수행해라. 담당 Sol xhigh.
AGENTS.md, 최신 EXECUTION의 해당 record와 acupoint-at-361 순서,
work/tasks/AT29.md, work/plans/mv2-at-integrated-2026-10-12/START-HERE.md,
30/31 설계의 해당 범위와 실제 선행 보고서·최종 자산/evidence를 읽어라.
이번 범위: 현재 기능 회귀 이후 cold load·경혈/전체점/영역 ON/OFF·30회 전환을 측정한다. 중복 carrier/상시 update/늦은 fetch 재연결/누수/불필요 초기 모듈과 bundle evidence 포함을 확인하고 관련 공통 경로를 최적화한다. 기존 예산을 조용히 올리지 않는다. 361 위치·14영역·설명·정밀도·UI 보류·공개권리를 각각 결론내고 로컬 산출물로 끝낸다.
시작 HEAD/status/실제 입력 hash와 소유 경계를 기록하고 최신 완료 결과를 재사용해라.
공통 compiler/loader/renderer를 재사용하고 task별 분기를 복제하지 마라.
등록 목록·교육용 실제 표시·정밀 위치·교재 설명·사람 검토·공개 권리를 구분해라.
교육용 근사는 실제 모델 지표로 근거 있게 작성하고 자료 부재를 허위 좌표나 가짜 면으로 채우지 마라.
이번 task의 필수 자동 검사와 실제 앱 선택/side/가림/전환/복귀를 검증해라.
원본/OpenSim_Models/T13/사용자 WIP/역사 evidence를 보존한다.
카메라 정책·UI 디자인·보기옵션·홈·로딩을 개편하지 마라. 기존 기능과 최소 콘텐츠 연결은 유지한다.
최신 EXECUTION을 다시 읽고 AT29 record와 해당 feature plan 다음 ID만 갱신한다.
work/reports/AT29.md와 versioned work/evidence/AT29/에 결과·실제 미완을 남겨라.
sync_execution.py 및 --check 후 소유 변경만 선별 로컬 커밋한다.
해시·포함/제외·잔여 변경과 다음 ID/프롬프트를 적고 멈춰라.
계획상 다음은 없음 — 사용자 후속 UI 요청 대기. 실제 선행/미완을 대조하고 자동 실행하지 마라.
자동 위임·push·배포·진단·치료·침 시뮬레이션 금지.
```
