# MV2·AT 순서별 붙여 넣을 프롬프트

2026-10-12. 아래는 실행 지시 템플릿이다. 이 문서를 생성했다고 각 작업을 실행하거나 완료한 것이 아니다.
**한 코드블록만 복사한다.** 현재 다른 대화의 MV2 q01 작업은 종료를 기다리고 결과를 읽는다.
현재 실행 중인 Sol High를 바꿀 필요는 없다. 이후 핵심 변경은 Sol xhigh, 반복 작업은 Luna Max로 선택한다.
후속 UI 개편은 하지 않는다. 검사용 수동 맞춤과 기존 기능의 연결/회귀는 유지한다.

## 1. MV2 다음 한 묶음 — Sol xhigh

현재 q01이 partial이면 같은 q01의 실제 미완만, 통과하면 Q02, 다음 요청에서 Q03을 수행한다.
매번 아래 하나를 재사용하되 이미 통과한 묶음을 다시 수행하지 않는다. Q03 뒤에는 아래 Luna 검증으로 넘긴다.

```text
HUMAN ATLAS에서 MV2의 다음 한 수정 묶음만 수행해라. 담당 Sol xhigh.
AGENTS.md, 최신 EXECUTION의 MV2, work/tasks/MV2.md,
work/plans/mv2-at-integrated-2026-10-12/START-HERE.md,
work/plans/mv2-completion-2026-10-12/MV2-SOL-RESUME.md,
최신 MV2 report/repairQueue/remainingUnits와 실제 최종 GLB·검증 evidence를 읽어라.
현재 다른 실행자가 같은 MV2를 수정 중이면 중복 구현하지 마라. 종료된 기준선/실제 hash로 시작해라.
선택 순서는 q01-learning-quality의 남은 필수 결과 → Q02 → Q03이다.
이들이 끝났으면 Q04/Q05 검증 결과에서 확인된 공통 원인 하나만 수행한다.
단순 not_performed/옛 nextScheduledTask=AT22를 현재 승인 대기나 재실행 이유로 쓰지 마라.
Q01 돌출 수정 통과와 이후 learning-quality 결과를 보존하고 완료한 전수조사를 반복하지 마라.
Q02 자산 수정이 필요하면 31,306,820-byte exact base와 새 repair 8MiB 계약 충돌을
resolver/delivery/실제 파일 검증의 공통 계약으로 해결해라. 전역 제한 완화나 주변 구조 삭제는 금지한다.
부착 역할·source/frame/side·pivot·weights·보간·접촉을 분리해 실제 원인을 수정해라.
offline authoring과 공통 replacement를 재사용하고 기존 원본 GLB를 덮지 마라.
통째 scale/고정/색 변화/각도 축소만으로 수축 표현을 대신하지 마라.
최종 emitted GLB를 실제 앱에서 준비·작용·복귀·중간 프레임·양측·주변 구조와 함께 검증해라.
1배속/필요한 느린 재생, 빠른 중단·전환·반복·원본 복귀와 경혈/영역 재진입을 확인해라.
실제 bytes/geometry 비용과 관련 tests/typecheck/build를 남겨라. 문서·수치만으로 pass하지 마라.
카메라 정책·UI 개편은 하지 마라. 선택적 human review와 기술/학습 표현 합격을 구분해라.
최신 EXECUTION을 다시 읽고 이번 MV2 record/관련 plan만 갱신해라. AT 기록/다른 WIP를 덮지 마라.
versioned report/evidence와 다음 정확한 unit을 남기고 sync_execution.py 및 --check를 실행해라.
원본/OpenSim_Models/T13/역사 freeze/기존 사용자 변경을 보존한다.
소유 변경만 선별 로컬 커밋하고 hash·포함/제외·잔여 변경을 보고한 뒤 멈춰라.
자동 다음 묶음·AT 실행·위임·push·배포·진단·치료·침 시뮬레이션 금지.
```

## 2. MV2 Q04/Q05 직렬 검증 — Luna Max

Q02/Q03과 **병렬**로 검사하려면 이 코드블록 대신 [PARALLEL.md](PARALLEL.md)의 worker 프롬프트를 쓴다.

```text
HUMAN ATLAS에서 MV2 Q04/Q05 검증 묶음만 수행해라. 담당 Luna Max.
work/plans/mv2-at-integrated-2026-10-12/START-HERE.md,
work/plans/mv2-completion-2026-10-12/MV2-LUNA-VERIFY.md와 지정 최신 입력을 읽어라.
단독 실행이며 다른 runtime/EXECUTION writer가 없는 기준선을 사용해라.
원래 Q04 26매핑/Q05 2매핑 중 최신 evidence로 완료한 항목은 제외한다.
병렬 worker 결과가 있으면 입력 hash를 대조해 재사용하고 browser pending만 마무리해라.
실제 앱에서 근육·관절·주변을 수동 관찰하여 준비/작용/중간/복귀를 확인해라.
pass/실제 기하·재생 결함/UI만 보류/관찰 근거 부족을 구분하고 검증 수를 정확히 보고해라.
geometry/pivot/weights/GLB/repair manifest/카메라 정책/UI를 바꾸지 마라.
실제 결함의 hash·clip·시점·구도·기대와 관찰을 Sol에 인계해라.
이번 검증 evidence/report와 MV2의 해당 판정만 갱신하고 sync_execution.py 및 --check를 실행해라.
원본·기존 WIP를 보존하고 소유 변경만 로컬 커밋한 뒤 다음 한 unit을 적고 멈춰라.
다음 구현·위임·push·배포는 하지 마라.
```

## 3. MV2 최종 대조 — Sol xhigh

남은 실제 결함이 있으면 위 1번으로 해당 공통 원인만 수정한다. 이미 모든 필수 판정과 회귀가 완료됐다면
새 종료 task를 만들거나 의미 없이 다시 실행할 필요 없다. 다음은 AT8이다.

```text
HUMAN ATLAS에서 MV2의 최종 대조/통합 검증만 수행해라. 담당 Sol xhigh.
work/plans/mv2-at-integrated-2026-10-12/START-HERE.md,
최신 MV2 record/report/repairQueue와 Q01–Q05 및 q01-learning-quality 최종 evidence를 읽어라.
매핑별 최신 GLB/hash와 해결/실제 미완/UI만 보류를 대조하고 숫자가 빠지지 않도록 해라.
수정 자산의 같은 장면 재생/종료/전환/경혈 점·면 복귀를 실제 앱에서 회귀 확인해라.
변경 없는 전체 MV1 조사를 반복하지 마라. 미확인 항목을 정상이나 UI 보류로 돌리지 마라.
필수 결함이 남으면 정확한 동일 MV2 unit으로 남기고 이번에 다른 원인 묶음까지 자동 수정하지 마라.
필수 기술·학습 표현 기준을 충족하면 MV2 scoped acceptance를 닫되
모든 근육의 동작 제작·교수 승인·UI 개편 완료라고 하지 마라.
현재 카메라/UI와 원본/사용자 WIP를 보존해라.
최신 EXECUTION의 MV2만 반영하고 보고서/evidence·sync_execution.py 및 --check를 남겨라.
소유 변경만 로컬 커밋하고 해시·범위·잔여 변경·다음 AT8 프롬프트를 적고 멈춰라.
AT8 자동 실행·push·배포 금지.
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
