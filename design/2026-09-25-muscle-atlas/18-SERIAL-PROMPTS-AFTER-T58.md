# T58 이후 순서별 실행 프롬프트

2026-09-28 · 계획. 아래 프롬프트를 **한 번에 하나만** 실행한다. 첫 실행 T73. 기본 Luna Max, 복잡한 운동/신경 계약은 기존 Sol High, 지정된 UI/판정은 Astra. 모델을 선택해 사용자가 해당 대화에 붙여 넣는다. 자동 위임하지 않는다.

T73이 추가 task를 삽입하면 live registry와 새 보고서 next가 이 문서의 정적 순서보다 우선한다. partial은 무조건 다음으로 넘어가는 신호가 아니다. 공유 계약 오류/필수 자산 누락은 의존 작업을 막고 독립 지역만 명시적으로 계속할 수 있다.

## 실행 순서

| 순서 | ID | 담당 | 작업 |
|---|---|---|---|
| 1 | T73 | Astra · 현재 대화 직접 구현 | 전신 시각 목표·누락 원인·취득 범위 확정 |
| 2 | T74 | Luna Max | 양측 두개골 시각 기반 보완 |
| 3 | T75 | Luna Max | 삼각근·광배근 양측 source 보완 |
| 4 | T76 | Luna Max | 골반·샅 시각 범위 보완 |
| 5 | T77 | Astra · 현재 대화 직접 구현 | 보완 패키지 통합·표시 정책 분리 |
| 6 | T78 | Luna Max | 주요 근육·뼈 선택과 세 이름 연결 파일럿 |
| 7 | T58 재검증 | Astra · 현재 대화 직접 구현 | 전신 그래픽 품질·연속성 합격 |
| 8 | T59 | Sol High | 같은 앞정강근 표면의 교육용 수축 변형 |
| 9 | T60 | Sol High | 동일 viewport에서 운동 재생 연결 |
| 10 | T25 | Luna Max | 같은 전신 모형의 앞정강근 제품 합격 |
| 11 | T61 | Sol High | 신경 레이어·선택·관계 데이터 계약 |
| 12 | T62 | Luna Max | 첫 하지 신경 자료 패키지 |
| 13 | T63 | Sol High | 첫 신경 3D 주행과 지배근 강조 |
| 14 | T64 | Luna Max | 신경 포착·기능 변화의 접힌 설명 UI |
| 15 | T65 | Luna Max | 전신·같은 모형 운동·신경 파일럿 통합 검증 |
| 16 | T26 | Luna Max | 소흉근 구조·작용 학습 자료 |
| 17 | T27 | Luna Max | 전신 안의 소흉근 상세 보강 |
| 18 | T28 | Sol High | 견갑대 운동 기반과 전인 시범 하나 |
| 19 | T45 | Sol High | 소흉근 관련 견갑골 하강 시범 |
| 20 | T46 | Sol High | 소흉근 관련 견갑골 하방회전 시범 |
| 21 | T29 | Luna Max | 소흉근 구조·기능 사용자 흐름 통합 |
| 22 | T30 | Luna Max | 모형 중심 화면과 성능 정리 |
| 23 | T31 | Luna Max | 두 부위 구조·기능 파일럿 합격 검증 |
| 24 | T32 | Luna Max | 전신 목표 목록 동결과 부위 패키지 배정 |
| 25 | T33 | Luna Max | 첫 지역 구조·기능 텍스트 패키지 |
| 26 | T34 | Luna Max | 구조 범위 감사만 수행 |
| 27 | T35 | Luna Max | 작용군 목록과 확장 queue만 확정 |
| 28 | T66 | Luna Max | 첫 기능 확장 batch 하나 |
| 29 | T47 | Luna Max | 전신 구조·기능 완료 판정 |
| 30 | T40 | Luna Max | 구조·기능 로컬 전달과 Git 체크포인트 |

## T73 — 전신 시각 목표·누락 원인·취득 범위 확정 (Astra · 현재 대화 직접 구현)

```text
HUMAN ATLAS에서 T73만 수행해라. 담당 Astra · 현재 대화 직접 구현.
AGENTS.md, 00-START-HERE.md, 03-LUNA-SERIAL-RUNBOOK.md, R15 13/14/15 설계와 16-ASTRA-UI-HANDOFF.md, 17-VISUAL-COVERAGE-REPAIR.md, 18-SERIAL-PROMPTS-AFTER-T58.md, work/STATUS.md와 work/task-registry-r15.json을 읽어라. 상대 설계 파일은 design/2026-09-25-muscle-atlas/ 아래에 있다. 실행할 task 명세와 선행 실제 보고서·manifest·evidence를 확인하고 정확히 요청된 ID만 수행해라. 시작 HEAD/status/hash를 기록하고 기존 코드/원본/OpenSim_Models/사용자 WIP/역사 freeze를 보존해라. 소유 코드·데이터·보고서·검증만 수정하고 최소 필수 검증과 필요한 실제 화면을 확인해라. 기본 숨김·선택 제한·source-only·license/human-review hold는 명세의 명시적 개별 변경 근거 없이 승격하지 마라. 로딩의 로고·인체 그림·슬로건을 복구하지 말고 단일 장면·카메라·최종 미니멀 UI를 유지해라. task별 report/evidence/STATUS/taskStatuses를 갱신하되 계획을 구현 완료로 표시하지 마라. 필수 실패는 partial/blocked로 남기고 독립 후속 허용 여부와 해결 조건을 구분해라. 소유 변경만 staged diff 확인 후 로컬 커밋하고 해시·제외·잔여 WIP·다음 ID/담당/붙여 넣을 프롬프트를 남겨라. 혼합 WIP는 전체 stage하지 말고 소유 hunk 또는 재현 가능한 상태 delta를 기록해라. 자동 다음 task·push·배포·진단·치료·침 시뮬레이션 금지.
상세 명세: work/tasks/T73.md. 선행: existing T58 partial report/artifacts; does not depend on future T58 pass.
T58 partial의 실제 캡처와 T50–T72 source tree/IS-A/part-of/ELEMENT 매핑을 대조한다. 삼각근·광배근·양측 두개골·골반바닥을 필수 점검하고 12부위 모두를 훑어 같은 누락 원인을 찾는다. 기존 region-root descendant 검색이 개념/부분/좌우 표면을 놓쳤는지 재현하되 원인을 미리 단정하지 않는다. 임상 설명 전신 입력이 아니라 전신 시각 최소 목표를 동결한다. target concept/side/region→source concept→exact FJ/member/hash 또는 missing reason을 기록하고, 미확보·확보/숨김·held·source-only·학습연결을 독립 열로 집계한다. T70 26개 gap과 0/11 residual은 별도 분모로 보존한다. 공식 metadata/원문 검색은 AI가 수행하며 사용자에게 이름 찾기를 떠넘기지 않는다. T74–76 exact source freeze와 최대10개 개념/내부5–10개 member batch를 확정한다. 추가 필수 부위가 있으면 T79 이상 미사용 정수 ID로 bounded 명세/프롬프트를 만들고 T77 앞에 삽입한다. 3개 보완 task로 전신이 완성된다고 가정하지 않는다. 취득·모형 변경·binding 구현은 하지 않는다.


다음 기본 ID는 T74이다. 추가 batch가 삽입되었으면 registry 순서를 따르고 이번 요청에서는 다음 task를 실행하지 마라.
```

## T74 — 양측 두개골 시각 기반 보완 (Luna Max)

```text
HUMAN ATLAS에서 T74만 수행해라. 담당 Luna Max.
AGENTS.md, 00-START-HERE.md, 03-LUNA-SERIAL-RUNBOOK.md, R15 13/14/15 설계와 16-ASTRA-UI-HANDOFF.md, 17-VISUAL-COVERAGE-REPAIR.md, 18-SERIAL-PROMPTS-AFTER-T58.md, work/STATUS.md와 work/task-registry-r15.json을 읽어라. 상대 설계 파일은 design/2026-09-25-muscle-atlas/ 아래에 있다. 실행할 task 명세와 선행 실제 보고서·manifest·evidence를 확인하고 정확히 요청된 ID만 수행해라. 시작 HEAD/status/hash를 기록하고 기존 코드/원본/OpenSim_Models/사용자 WIP/역사 freeze를 보존해라. 소유 코드·데이터·보고서·검증만 수정하고 최소 필수 검증과 필요한 실제 화면을 확인해라. 기본 숨김·선택 제한·source-only·license/human-review hold는 명세의 명시적 개별 변경 근거 없이 승격하지 마라. 로딩의 로고·인체 그림·슬로건을 복구하지 말고 단일 장면·카메라·최종 미니멀 UI를 유지해라. task별 report/evidence/STATUS/taskStatuses를 갱신하되 계획을 구현 완료로 표시하지 마라. 필수 실패는 partial/blocked로 남기고 독립 후속 허용 여부와 해결 조건을 구분해라. 소유 변경만 staged diff 확인 후 로컬 커밋하고 해시·제외·잔여 WIP·다음 ID/담당/붙여 넣을 프롬프트를 남겨라. 혼합 WIP는 전체 stage하지 말고 소유 hunk 또는 재현 가능한 상태 delta를 기록해라. 자동 다음 task·push·배포·진단·치료·침 시뮬레이션 금지.
상세 명세: work/tasks/T74.md. 선행: T73.
T73에서 동결한 두개골 concept/side/source member만 취득·검증·변환한다. 이미 있는 이마뼈/아래턱뼈/뒤통수뼈는 재취득하지 않고 재사용 증거를 연결한다. 왼쪽 마루뼈 등 정확한 누락 대상은 T73 실제 매핑으로 결정한다. 중선 구조에 억지 좌우를 만들지 않고 단순 mirror로 반대쪽을 생성하지 않는다. 기존 importer와 공통 frame/rest pose를 재사용하고 새 sibling manifest를 만든다. 옛 freeze와 source byte는 수정하지 않는다. learner default 표시/선택 정책은 T77/T78까지 바꾸지 않는다.


다음 기본 ID는 T75이다. 추가 batch가 삽입되었으면 registry 순서를 따르고 이번 요청에서는 다음 task를 실행하지 마라.
```

## T75 — 삼각근·광배근 양측 source 보완 (Luna Max)

```text
HUMAN ATLAS에서 T75만 수행해라. 담당 Luna Max.
AGENTS.md, 00-START-HERE.md, 03-LUNA-SERIAL-RUNBOOK.md, R15 13/14/15 설계와 16-ASTRA-UI-HANDOFF.md, 17-VISUAL-COVERAGE-REPAIR.md, 18-SERIAL-PROMPTS-AFTER-T58.md, work/STATUS.md와 work/task-registry-r15.json을 읽어라. 상대 설계 파일은 design/2026-09-25-muscle-atlas/ 아래에 있다. 실행할 task 명세와 선행 실제 보고서·manifest·evidence를 확인하고 정확히 요청된 ID만 수행해라. 시작 HEAD/status/hash를 기록하고 기존 코드/원본/OpenSim_Models/사용자 WIP/역사 freeze를 보존해라. 소유 코드·데이터·보고서·검증만 수정하고 최소 필수 검증과 필요한 실제 화면을 확인해라. 기본 숨김·선택 제한·source-only·license/human-review hold는 명세의 명시적 개별 변경 근거 없이 승격하지 마라. 로딩의 로고·인체 그림·슬로건을 복구하지 말고 단일 장면·카메라·최종 미니멀 UI를 유지해라. task별 report/evidence/STATUS/taskStatuses를 갱신하되 계획을 구현 완료로 표시하지 마라. 필수 실패는 partial/blocked로 남기고 독립 후속 허용 여부와 해결 조건을 구분해라. 소유 변경만 staged diff 확인 후 로컬 커밋하고 해시·제외·잔여 WIP·다음 ID/담당/붙여 넣을 프롬프트를 남겨라. 혼합 WIP는 전체 stage하지 말고 소유 hunk 또는 재현 가능한 상태 delta를 기록해라. 자동 다음 task·push·배포·진단·치료·침 시뮬레이션 금지.
상세 명세: work/tasks/T75.md. 선행: T74.
T73이 동결한 삼각근과 광배근 양측 및 실제 source의 부분 구성만 취득·변환한다. deltoid 전체/갈래/부분과 좌우를 분리하고 측면삼각근을 전체 deltoid와 무조건 동일시하지 않는다. 기존 어깨/등/팔과 다중 region membership을 유지하며 한 번만 로드할 stable node를 만든다. 같은 source/frame/pose를 사용하고 새 sibling extension에 기록한다. 새 canonical learner binding·동작 구현은 하지 않는다.


다음 기본 ID는 T76이다. 추가 batch가 삽입되었으면 registry 순서를 따르고 이번 요청에서는 다음 task를 실행하지 마라.
```

## T76 — 골반·샅 시각 범위 보완 (Luna Max)

```text
HUMAN ATLAS에서 T76만 수행해라. 담당 Luna Max.
AGENTS.md, 00-START-HERE.md, 03-LUNA-SERIAL-RUNBOOK.md, R15 13/14/15 설계와 16-ASTRA-UI-HANDOFF.md, 17-VISUAL-COVERAGE-REPAIR.md, 18-SERIAL-PROMPTS-AFTER-T58.md, work/STATUS.md와 work/task-registry-r15.json을 읽어라. 상대 설계 파일은 design/2026-09-25-muscle-atlas/ 아래에 있다. 실행할 task 명세와 선행 실제 보고서·manifest·evidence를 확인하고 정확히 요청된 ID만 수행해라. 시작 HEAD/status/hash를 기록하고 기존 코드/원본/OpenSim_Models/사용자 WIP/역사 freeze를 보존해라. 소유 코드·데이터·보고서·검증만 수정하고 최소 필수 검증과 필요한 실제 화면을 확인해라. 기본 숨김·선택 제한·source-only·license/human-review hold는 명세의 명시적 개별 변경 근거 없이 승격하지 마라. 로딩의 로고·인체 그림·슬로건을 복구하지 말고 단일 장면·카메라·최종 미니멀 UI를 유지해라. task별 report/evidence/STATUS/taskStatuses를 갱신하되 계획을 구현 완료로 표시하지 마라. 필수 실패는 partial/blocked로 남기고 독립 후속 허용 여부와 해결 조건을 구분해라. 소유 변경만 staged diff 확인 후 로컬 커밋하고 해시·제외·잔여 WIP·다음 ID/담당/붙여 넣을 프롬프트를 남겨라. 혼합 WIP는 전체 stage하지 말고 소유 hunk 또는 재현 가능한 상태 delta를 기록해라. 자동 다음 task·push·배포·진단·치료·침 시뮬레이션 금지.
상세 명세: work/tasks/T76.md. 선행: T75.
T73이 근거로 동결한 골반바닥/샅 target 최대10개 개념과 관련 뼈 맥락을 취득·검증한다. 현재 7 source 메시/두 이름이 전체 분모가 아님을 유지하고 source가 근육군/개별근/부분을 어떻게 표현하는지 기록한다. 없는 구분을 합쳐 이름을 붙이거나 표면을 그리지 않는다. 기존 identity hold 1개는 임의 해제하지 않는다. 기존 cache 재사용과 새 sibling manifest로 구현하고 learner UI 정책은 변경하지 않는다.


다음 기본 ID는 T77이다. 추가 batch가 삽입되었으면 registry 순서를 따르고 이번 요청에서는 다음 task를 실행하지 마라.
```

## T77 — 보완 패키지 통합·표시 정책 분리 (Astra · 현재 대화 직접 구현)

```text
HUMAN ATLAS에서 T77만 수행해라. 담당 Astra · 현재 대화 직접 구현.
AGENTS.md, 00-START-HERE.md, 03-LUNA-SERIAL-RUNBOOK.md, R15 13/14/15 설계와 16-ASTRA-UI-HANDOFF.md, 17-VISUAL-COVERAGE-REPAIR.md, 18-SERIAL-PROMPTS-AFTER-T58.md, work/STATUS.md와 work/task-registry-r15.json을 읽어라. 상대 설계 파일은 design/2026-09-25-muscle-atlas/ 아래에 있다. 실행할 task 명세와 선행 실제 보고서·manifest·evidence를 확인하고 정확히 요청된 ID만 수행해라. 시작 HEAD/status/hash를 기록하고 기존 코드/원본/OpenSim_Models/사용자 WIP/역사 freeze를 보존해라. 소유 코드·데이터·보고서·검증만 수정하고 최소 필수 검증과 필요한 실제 화면을 확인해라. 기본 숨김·선택 제한·source-only·license/human-review hold는 명세의 명시적 개별 변경 근거 없이 승격하지 마라. 로딩의 로고·인체 그림·슬로건을 복구하지 말고 단일 장면·카메라·최종 미니멀 UI를 유지해라. task별 report/evidence/STATUS/taskStatuses를 갱신하되 계획을 구현 완료로 표시하지 마라. 필수 실패는 partial/blocked로 남기고 독립 후속 허용 여부와 해결 조건을 구분해라. 소유 변경만 staged diff 확인 후 로컬 커밋하고 해시·제외·잔여 WIP·다음 ID/담당/붙여 넣을 프롬프트를 남겨라. 혼합 WIP는 전체 stage하지 말고 소유 hunk 또는 재현 가능한 상태 delta를 기록해라. 자동 다음 task·push·배포·진단·치료·침 시뮬레이션 금지.
상세 명세: work/tasks/T77.md. 선행: T73의 동결 목표 및 T74–76과 추가 필수 취득 패키지.
T73–76 및 T73이 삽입한 필수 자산 task의 실제 산출물을 같은 AnatomySceneRoot/renderer에 통합한다. 옛 T56/T70/T71/T72 manifest를 고치지 않고 새 integration revision을 만든다. 자료 확보/기본 가시성/learner pickability/공개 권리/human review를 독립 상태로 관리한다. 기존 supplement default false를 일괄 true로 바꾸지 않는다. source identity·frame·품질과 로컬 사용 근거가 확인된 항목에만 명시적 per-ID 표시 정책 변경 기록(before/after/reason/evidence)을 적용할 수 있다. 라이선스 로컬 사용 자체가 미해결이면 보류한다. source_only_unbound는 보이더라도 이름·설명 연결이나 선택 가능으로 승격하지 않는다. held 12개와 신규 held는 계속 숨김/선택 금지다. 라이선스·human-review 사실은 변경하지 않는다. 사용자 미니멀 로딩/홈·카메라·레이어를 보존하고 내부 상태 배지는 learner에 나열하지 않는다.


다음 기본 ID는 T78이다. 추가 batch가 삽입되었으면 registry 순서를 따르고 이번 요청에서는 다음 task를 실행하지 마라.
```

## T78 — 주요 근육·뼈 선택과 세 이름 연결 파일럿 (Luna Max)

```text
HUMAN ATLAS에서 T78만 수행해라. 담당 Luna Max.
AGENTS.md, 00-START-HERE.md, 03-LUNA-SERIAL-RUNBOOK.md, R15 13/14/15 설계와 16-ASTRA-UI-HANDOFF.md, 17-VISUAL-COVERAGE-REPAIR.md, 18-SERIAL-PROMPTS-AFTER-T58.md, work/STATUS.md와 work/task-registry-r15.json을 읽어라. 상대 설계 파일은 design/2026-09-25-muscle-atlas/ 아래에 있다. 실행할 task 명세와 선행 실제 보고서·manifest·evidence를 확인하고 정확히 요청된 ID만 수행해라. 시작 HEAD/status/hash를 기록하고 기존 코드/원본/OpenSim_Models/사용자 WIP/역사 freeze를 보존해라. 소유 코드·데이터·보고서·검증만 수정하고 최소 필수 검증과 필요한 실제 화면을 확인해라. 기본 숨김·선택 제한·source-only·license/human-review hold는 명세의 명시적 개별 변경 근거 없이 승격하지 마라. 로딩의 로고·인체 그림·슬로건을 복구하지 말고 단일 장면·카메라·최종 미니멀 UI를 유지해라. task별 report/evidence/STATUS/taskStatuses를 갱신하되 계획을 구현 완료로 표시하지 마라. 필수 실패는 partial/blocked로 남기고 독립 후속 허용 여부와 해결 조건을 구분해라. 소유 변경만 staged diff 확인 후 로컬 커밋하고 해시·제외·잔여 WIP·다음 ID/담당/붙여 넣을 프롬프트를 남겨라. 혼합 WIP는 전체 stage하지 말고 소유 hunk 또는 재현 가능한 상태 delta를 기록해라. 자동 다음 task·push·배포·진단·치료·침 시뮬레이션 금지.
상세 명세: work/tasks/T78.md. 선행: T77.
T73 target에서 실제 geometry와 identity가 준비된 최대10개 canonical concept를 동결해 기존 카드/검색에 연결한다. 삼각근·광배근을 우선하고 관련 두개골/골반 구조는 상한 안에서 고른다. 기존 catalog ID를 먼저 재사용하고 source part/side 다대다 mapping을 검증한다. 우리말명·한자어명(한글)·영어명/alias를 근거로 교차 확인한다. 기본 표시는 삼각근 같은 한자어명이며 어깨세모근/deltoid 검색도 같은 대상으로 간다. 기존 구조/작용 텍스트는 근거가 있는 것만 연결하고 없는 기시정지/작용은 별도 내용 batch로 배정한다. 조용히 humanReviewed=true를 만들지 않는다. source_only 전체 자동 binding 금지; 정확한 identity를 가진 이번 subset에만 별도 버전 mapping과 허용 근거를 남긴다. held 대상을 선택으로 승격하지 않는다. UI에 source 상태/ID/task를 늘어놓지 말고 실제 연결 대상만 검색·클릭 가능하게 한다.


다음 기본 ID는 T58이다. 추가 batch가 삽입되었으면 registry 순서를 따르고 이번 요청에서는 다음 task를 실행하지 마라.
```

## T58 — 전신 그래픽 품질·연속성 합격 (Astra · 현재 대화 직접 구현)

```text
HUMAN ATLAS에서 T58 재검증만 수행해라. 담당 Astra · 현재 대화 직접 구현.
AGENTS.md, 00-START-HERE.md, 03-LUNA-SERIAL-RUNBOOK.md, R15 13/14/15 설계와 16-ASTRA-UI-HANDOFF.md, 17-VISUAL-COVERAGE-REPAIR.md, 18-SERIAL-PROMPTS-AFTER-T58.md, work/STATUS.md와 work/task-registry-r15.json을 읽어라. 상대 설계 파일은 design/2026-09-25-muscle-atlas/ 아래에 있다. 실행할 task 명세와 선행 실제 보고서·manifest·evidence를 확인하고 정확히 요청된 ID만 수행해라. 시작 HEAD/status/hash를 기록하고 기존 코드/원본/OpenSim_Models/사용자 WIP/역사 freeze를 보존해라. 소유 코드·데이터·보고서·검증만 수정하고 최소 필수 검증과 필요한 실제 화면을 확인해라. 기본 숨김·선택 제한·source-only·license/human-review hold는 명세의 명시적 개별 변경 근거 없이 승격하지 마라. 로딩의 로고·인체 그림·슬로건을 복구하지 말고 단일 장면·카메라·최종 미니멀 UI를 유지해라. task별 report/evidence/STATUS/taskStatuses를 갱신하되 계획을 구현 완료로 표시하지 마라. 필수 실패는 partial/blocked로 남기고 독립 후속 허용 여부와 해결 조건을 구분해라. 소유 변경만 staged diff 확인 후 로컬 커밋하고 해시·제외·잔여 WIP·다음 ID/담당/붙여 넣을 프롬프트를 남겨라. 혼합 WIP는 전체 stage하지 말고 소유 hunk 또는 재현 가능한 상태 delta를 기록해라. 자동 다음 task·push·배포·진단·치료·침 시뮬레이션 금지.
상세 명세: work/tasks/T58.md. 선행: T77/T78와 T73의 추가 필수 패키지.
기존 T58 구현은 보존하고 T73 target 및 T74–78/추가 보완 실제 산출물을 기준으로 T58만 재검증·필요한 제한적 UI 수정을 해라. 삼각근/광배근 양측, 두개골 실루엣, 골반·샅과 나머지 12부위의 동결 시각 목표 누락을 확인해라. 실제 전신/머리/종아리/손 캡처, 390/1024/1440 framing/패널/선택/카메라/성능, 제한 회귀를 검증하고 처음 보고서는 보존한 채 새 재검증 보고서로 G58-01의 해소 여부를 기록해라. 필수 누락이 남으면 partial이며 T59를 시작하지 마라.

다음 기본 ID는 T59이다. 추가 batch가 삽입되었으면 registry 순서를 따르고 이번 요청에서는 다음 task를 실행하지 마라.
```

## T59 — 같은 앞정강근 표면의 교육용 수축 변형 (Sol High)

```text
HUMAN ATLAS에서 T59만 수행해라. 담당 Sol High.
AGENTS.md, 00-START-HERE.md, 03-LUNA-SERIAL-RUNBOOK.md, R15 13/14/15 설계와 16-ASTRA-UI-HANDOFF.md, 17-VISUAL-COVERAGE-REPAIR.md, 18-SERIAL-PROMPTS-AFTER-T58.md, work/STATUS.md와 work/task-registry-r15.json을 읽어라. 상대 설계 파일은 design/2026-09-25-muscle-atlas/ 아래에 있다. 실행할 task 명세와 선행 실제 보고서·manifest·evidence를 확인하고 정확히 요청된 ID만 수행해라. 시작 HEAD/status/hash를 기록하고 기존 코드/원본/OpenSim_Models/사용자 WIP/역사 freeze를 보존해라. 소유 코드·데이터·보고서·검증만 수정하고 최소 필수 검증과 필요한 실제 화면을 확인해라. 기본 숨김·선택 제한·source-only·license/human-review hold는 명세의 명시적 개별 변경 근거 없이 승격하지 마라. 로딩의 로고·인체 그림·슬로건을 복구하지 말고 단일 장면·카메라·최종 미니멀 UI를 유지해라. task별 report/evidence/STATUS/taskStatuses를 갱신하되 계획을 구현 완료로 표시하지 마라. 필수 실패는 partial/blocked로 남기고 독립 후속 허용 여부와 해결 조건을 구분해라. 소유 변경만 staged diff 확인 후 로컬 커밋하고 해시·제외·잔여 WIP·다음 ID/담당/붙여 넣을 프롬프트를 남겨라. 혼합 WIP는 전체 stage하지 말고 소유 hunk 또는 재현 가능한 상태 delta를 기록해라. 자동 다음 task·push·배포·진단·치료·침 시뮬레이션 금지.
상세 명세: work/tasks/T59.md. 선행: T58.
T55 전신 모델의 실제 앞정강근과 부착·발목 bone에 대해 model-local 좌표/endpoint·rest pose를 검증하고 skinning 또는 morph/shape-key 기반 변형을 제작한다. 목표 근육의 형태 변화와 발 움직임을 같은 모델에서 결속한다. 주변 근육은 사용자가 숨기지 않았다면 유지하고 관절을 지나는 주변 구조의 수동 변형/관통도 처리한다. 근육 전체 scale이나 선 길이 감소만으로 대체하지 않는다.


다음 기본 ID는 T60이다. 추가 batch가 삽입되었으면 registry 순서를 따르고 이번 요청에서는 다음 task를 실행하지 마라.
```

## T60 — 동일 viewport에서 운동 재생 연결 (Sol High)

```text
HUMAN ATLAS에서 T60만 수행해라. 담당 Sol High.
AGENTS.md, 00-START-HERE.md, 03-LUNA-SERIAL-RUNBOOK.md, R15 13/14/15 설계와 16-ASTRA-UI-HANDOFF.md, 17-VISUAL-COVERAGE-REPAIR.md, 18-SERIAL-PROMPTS-AFTER-T58.md, work/STATUS.md와 work/task-registry-r15.json을 읽어라. 상대 설계 파일은 design/2026-09-25-muscle-atlas/ 아래에 있다. 실행할 task 명세와 선행 실제 보고서·manifest·evidence를 확인하고 정확히 요청된 ID만 수행해라. 시작 HEAD/status/hash를 기록하고 기존 코드/원본/OpenSim_Models/사용자 WIP/역사 freeze를 보존해라. 소유 코드·데이터·보고서·검증만 수정하고 최소 필수 검증과 필요한 실제 화면을 확인해라. 기본 숨김·선택 제한·source-only·license/human-review hold는 명세의 명시적 개별 변경 근거 없이 승격하지 마라. 로딩의 로고·인체 그림·슬로건을 복구하지 말고 단일 장면·카메라·최종 미니멀 UI를 유지해라. task별 report/evidence/STATUS/taskStatuses를 갱신하되 계획을 구현 완료로 표시하지 마라. 필수 실패는 partial/blocked로 남기고 독립 후속 허용 여부와 해결 조건을 구분해라. 소유 변경만 staged diff 확인 후 로컬 커밋하고 해시·제외·잔여 WIP·다음 ID/담당/붙여 넣을 프롬프트를 남겨라. 혼합 WIP는 전체 stage하지 말고 소유 hunk 또는 재현 가능한 상태 delta를 기록해라. 자동 다음 task·push·배포·진단·치료·침 시뮬레이션 금지.
상세 명세: work/tasks/T60.md. 선행: T59.
MotionLearningPanel의 독립 asset/mixer 소유를 AnatomySceneController 명령으로 연결한다. 실제 main renderer가 가진 T59 target node를 애니메이션하고 UI는 play/pause/seek/reset 명령과 상태만 가진다. 사용자 CTA 클릭 전에는 움직이지 않는다. 기존 camera/background/layers/selection을 snapshot해 보존하고 종료 시 pose/가시성만 정확히 복원한다.


다음 기본 ID는 T25이다. 추가 batch가 삽입되었으면 registry 순서를 따르고 이번 요청에서는 다음 task를 실행하지 마라.
```

## T25 — 같은 전신 모형의 앞정강근 제품 합격 (Luna Max)

```text
HUMAN ATLAS에서 T25만 수행해라. 담당 Luna Max.
AGENTS.md, 00-START-HERE.md, 03-LUNA-SERIAL-RUNBOOK.md, R15 13/14/15 설계와 16-ASTRA-UI-HANDOFF.md, 17-VISUAL-COVERAGE-REPAIR.md, 18-SERIAL-PROMPTS-AFTER-T58.md, work/STATUS.md와 work/task-registry-r15.json을 읽어라. 상대 설계 파일은 design/2026-09-25-muscle-atlas/ 아래에 있다. 실행할 task 명세와 선행 실제 보고서·manifest·evidence를 확인하고 정확히 요청된 ID만 수행해라. 시작 HEAD/status/hash를 기록하고 기존 코드/원본/OpenSim_Models/사용자 WIP/역사 freeze를 보존해라. 소유 코드·데이터·보고서·검증만 수정하고 최소 필수 검증과 필요한 실제 화면을 확인해라. 기본 숨김·선택 제한·source-only·license/human-review hold는 명세의 명시적 개별 변경 근거 없이 승격하지 마라. 로딩의 로고·인체 그림·슬로건을 복구하지 말고 단일 장면·카메라·최종 미니멀 UI를 유지해라. task별 report/evidence/STATUS/taskStatuses를 갱신하되 계획을 구현 완료로 표시하지 마라. 필수 실패는 partial/blocked로 남기고 독립 후속 허용 여부와 해결 조건을 구분해라. 소유 변경만 staged diff 확인 후 로컬 커밋하고 해시·제외·잔여 WIP·다음 ID/담당/붙여 넣을 프롬프트를 남겨라. 혼합 WIP는 전체 stage하지 말고 소유 hunk 또는 재현 가능한 상태 delta를 기록해라. 자동 다음 task·push·배포·진단·치료·침 시뮬레이션 금지.
상세 명세: work/tasks/T25.md. 선행: T60.
T42 공통 카드와 T24 실제 clip을 연결한다. 근육 선택→세 이름/기시·정지→눈에 보이는 '움직임으로 이해하기'→실제 몸 움직임→작용 설명을 연결한다. 클릭은 명시적 재생 요청으로 취급하되 reduced-motion은 정지 자세/수동 단계 선택을 기본으로 한다.

기능 탭 전환과 작용 선택을 동기화하고 pause/resume/처음 자세/느리게/진행 막대를 제공한다. camera reset과 pose reset을 분리한다. 모형 전환이 있으면 학습용 시범 모형임을 짧게 알린다.

선택/부위/탭 전환·로드 실패·unmount 시 loop·mixer·강조를 정리한다. CTA 클릭 전에는 자동 재생하지 않는다.

T59/T60의 실제 같은 모형 mesh 변형을 main learner에서 검증한다. 별도 T24 bone/path 기술 후보는 pass 근거가 아니다. 전신 탐색→앞정강근→기시정지/기능→CTA→표면 수축과 발 움직임→복원을 시험한다. T24 역사 보고서는 blocked 그대로 보존하고 해결 증거를 새 보고서에 연결한다. 다음은 신경 기반 T61이다.
다음 기본 ID는 T61이다. 추가 batch가 삽입되었으면 registry 순서를 따르고 이번 요청에서는 다음 task를 실행하지 마라.
```

## T61 — 신경 레이어·선택·관계 데이터 계약 (Sol High)

```text
HUMAN ATLAS에서 T61만 수행해라. 담당 Sol High.
AGENTS.md, 00-START-HERE.md, 03-LUNA-SERIAL-RUNBOOK.md, R15 13/14/15 설계와 16-ASTRA-UI-HANDOFF.md, 17-VISUAL-COVERAGE-REPAIR.md, 18-SERIAL-PROMPTS-AFTER-T58.md, work/STATUS.md와 work/task-registry-r15.json을 읽어라. 상대 설계 파일은 design/2026-09-25-muscle-atlas/ 아래에 있다. 실행할 task 명세와 선행 실제 보고서·manifest·evidence를 확인하고 정확히 요청된 ID만 수행해라. 시작 HEAD/status/hash를 기록하고 기존 코드/원본/OpenSim_Models/사용자 WIP/역사 freeze를 보존해라. 소유 코드·데이터·보고서·검증만 수정하고 최소 필수 검증과 필요한 실제 화면을 확인해라. 기본 숨김·선택 제한·source-only·license/human-review hold는 명세의 명시적 개별 변경 근거 없이 승격하지 마라. 로딩의 로고·인체 그림·슬로건을 복구하지 말고 단일 장면·카메라·최종 미니멀 UI를 유지해라. task별 report/evidence/STATUS/taskStatuses를 갱신하되 계획을 구현 완료로 표시하지 마라. 필수 실패는 partial/blocked로 남기고 독립 후속 허용 여부와 해결 조건을 구분해라. 소유 변경만 staged diff 확인 후 로컬 커밋하고 해시·제외·잔여 WIP·다음 ID/담당/붙여 넣을 프롬프트를 남겨라. 혼합 WIP는 전체 stage하지 말고 소유 hunk 또는 재현 가능한 상태 delta를 기록해라. 자동 다음 task·push·배포·진단·치료·침 시뮬레이션 금지.
상세 명세: work/tasks/T61.md. 선행: T25.
전신 scene에 nerves layer를 추가할 계약과 선택 priority·불투명도·관계 강조를 구현한다. 근육/뼈/신경은 같은 scene/body frame이며 nerve stable ID·branch·side·course·muscle innervation·sensory territory·root dermatome·possible entrapment site·site-specific finding을 다른 관계로 정의한다. 해부학 용어와 clinical hypothesis를 분리한다. 신경 전체 데이터나 검사 애니메이션은 이번에 채우지 않는다.


다음 기본 ID는 T62이다. 추가 batch가 삽입되었으면 registry 순서를 따르고 이번 요청에서는 다음 task를 실행하지 마라.
```

## T62 — 첫 하지 신경 자료 패키지 (Luna Max)

```text
HUMAN ATLAS에서 T62만 수행해라. 담당 Luna Max.
AGENTS.md, 00-START-HERE.md, 03-LUNA-SERIAL-RUNBOOK.md, R15 13/14/15 설계와 16-ASTRA-UI-HANDOFF.md, 17-VISUAL-COVERAGE-REPAIR.md, 18-SERIAL-PROMPTS-AFTER-T58.md, work/STATUS.md와 work/task-registry-r15.json을 읽어라. 상대 설계 파일은 design/2026-09-25-muscle-atlas/ 아래에 있다. 실행할 task 명세와 선행 실제 보고서·manifest·evidence를 확인하고 정확히 요청된 ID만 수행해라. 시작 HEAD/status/hash를 기록하고 기존 코드/원본/OpenSim_Models/사용자 WIP/역사 freeze를 보존해라. 소유 코드·데이터·보고서·검증만 수정하고 최소 필수 검증과 필요한 실제 화면을 확인해라. 기본 숨김·선택 제한·source-only·license/human-review hold는 명세의 명시적 개별 변경 근거 없이 승격하지 마라. 로딩의 로고·인체 그림·슬로건을 복구하지 말고 단일 장면·카메라·최종 미니멀 UI를 유지해라. task별 report/evidence/STATUS/taskStatuses를 갱신하되 계획을 구현 완료로 표시하지 마라. 필수 실패는 partial/blocked로 남기고 독립 후속 허용 여부와 해결 조건을 구분해라. 소유 변경만 staged diff 확인 후 로컬 커밋하고 해시·제외·잔여 WIP·다음 ID/담당/붙여 넣을 프롬프트를 남겨라. 혼합 WIP는 전체 stage하지 말고 소유 hunk 또는 재현 가능한 상태 delta를 기록해라. 자동 다음 task·push·배포·진단·치료·침 시뮬레이션 금지.
상세 명세: work/tasks/T62.md. 선행: T61.
앞정강근과 연관된 하지 신경 계통 중 원문으로 확인한 한 trunk와 최대2개 branch를 첫 대상으로 동결한다. 이름/주행/지배근/감각 분포/가능한 포착 구간을 직접 문헌 조사한다. 최대10개 지배근 관계를 첫 batch로 제한하고 excess는 별도 ID로 등록한다. 정확한 신경 분지 구조와 부위별 증상을 같은 전체신경 일반값으로 뭉치지 않는다.


다음 기본 ID는 T63이다. 추가 batch가 삽입되었으면 registry 순서를 따르고 이번 요청에서는 다음 task를 실행하지 마라.
```

## T63 — 첫 신경 3D 주행과 지배근 강조 (Sol High)

```text
HUMAN ATLAS에서 T63만 수행해라. 담당 Sol High.
AGENTS.md, 00-START-HERE.md, 03-LUNA-SERIAL-RUNBOOK.md, R15 13/14/15 설계와 16-ASTRA-UI-HANDOFF.md, 17-VISUAL-COVERAGE-REPAIR.md, 18-SERIAL-PROMPTS-AFTER-T58.md, work/STATUS.md와 work/task-registry-r15.json을 읽어라. 상대 설계 파일은 design/2026-09-25-muscle-atlas/ 아래에 있다. 실행할 task 명세와 선행 실제 보고서·manifest·evidence를 확인하고 정확히 요청된 ID만 수행해라. 시작 HEAD/status/hash를 기록하고 기존 코드/원본/OpenSim_Models/사용자 WIP/역사 freeze를 보존해라. 소유 코드·데이터·보고서·검증만 수정하고 최소 필수 검증과 필요한 실제 화면을 확인해라. 기본 숨김·선택 제한·source-only·license/human-review hold는 명세의 명시적 개별 변경 근거 없이 승격하지 마라. 로딩의 로고·인체 그림·슬로건을 복구하지 말고 단일 장면·카메라·최종 미니멀 UI를 유지해라. task별 report/evidence/STATUS/taskStatuses를 갱신하되 계획을 구현 완료로 표시하지 마라. 필수 실패는 partial/blocked로 남기고 독립 후속 허용 여부와 해결 조건을 구분해라. 소유 변경만 staged diff 확인 후 로컬 커밋하고 해시·제외·잔여 WIP·다음 ID/담당/붙여 넣을 프롬프트를 남겨라. 혼합 WIP는 전체 stage하지 말고 소유 hunk 또는 재현 가능한 상태 delta를 기록해라. 자동 다음 task·push·배포·진단·치료·침 시뮬레이션 금지.
상세 명세: work/tasks/T63.md. 선행: T62.
T62 한 trunk와 최대2개 branch를 동일 전신 source의 실제 nerve mesh/path 또는 근거 있는 registration으로 정합한다. 단순 시작/끝 직선으로 실제 주행을 꾸미지 않는다. 교육용 단순 경로라면 표현 범위를 구분한다. nerve 클릭/근육 카드 지배신경 클릭으로 같은 장면에서 주행·지배근만 강조한다. 미검증 animation 대응 신경은 동작 중 고정 경로로 남겨 잘못된 관계를 보이지 말고 운동 시작 조건/휴지 자세 안내를 설계한다.


다음 기본 ID는 T64이다. 추가 batch가 삽입되었으면 registry 순서를 따르고 이번 요청에서는 다음 task를 실행하지 마라.
```

## T64 — 신경 포착·기능 변화의 접힌 설명 UI (Luna Max)

```text
HUMAN ATLAS에서 T64만 수행해라. 담당 Luna Max.
AGENTS.md, 00-START-HERE.md, 03-LUNA-SERIAL-RUNBOOK.md, R15 13/14/15 설계와 16-ASTRA-UI-HANDOFF.md, 17-VISUAL-COVERAGE-REPAIR.md, 18-SERIAL-PROMPTS-AFTER-T58.md, work/STATUS.md와 work/task-registry-r15.json을 읽어라. 상대 설계 파일은 design/2026-09-25-muscle-atlas/ 아래에 있다. 실행할 task 명세와 선행 실제 보고서·manifest·evidence를 확인하고 정확히 요청된 ID만 수행해라. 시작 HEAD/status/hash를 기록하고 기존 코드/원본/OpenSim_Models/사용자 WIP/역사 freeze를 보존해라. 소유 코드·데이터·보고서·검증만 수정하고 최소 필수 검증과 필요한 실제 화면을 확인해라. 기본 숨김·선택 제한·source-only·license/human-review hold는 명세의 명시적 개별 변경 근거 없이 승격하지 마라. 로딩의 로고·인체 그림·슬로건을 복구하지 말고 단일 장면·카메라·최종 미니멀 UI를 유지해라. task별 report/evidence/STATUS/taskStatuses를 갱신하되 계획을 구현 완료로 표시하지 마라. 필수 실패는 partial/blocked로 남기고 독립 후속 허용 여부와 해결 조건을 구분해라. 소유 변경만 staged diff 확인 후 로컬 커밋하고 해시·제외·잔여 WIP·다음 ID/담당/붙여 넣을 프롬프트를 남겨라. 혼합 WIP는 전체 stage하지 말고 소유 hunk 또는 재현 가능한 상태 delta를 기록해라. 자동 다음 task·push·배포·진단·치료·침 시뮬레이션 금지.
상세 명세: work/tasks/T64.md. 선행: T63.
T62 범위에서 한 신경의 최대3개 포착 후보 구간과 부위별 지배근/감각/가능한 기능 변화 설명을 연결한다. 기본 카드에는 이름·주행·지배근만, “포착과 기능 변화”는 사용자가 펼쳤을 때만 표시한다. 통증 영역/감각 분포/신경 주행을 동시에 기본 표시하지 않는다. 출처는 내부 관리한다.


다음 기본 ID는 T65이다. 추가 batch가 삽입되었으면 registry 순서를 따르고 이번 요청에서는 다음 task를 실행하지 마라.
```

## T65 — 전신·같은 모형 운동·신경 파일럿 통합 검증 (Luna Max)

```text
HUMAN ATLAS에서 T65만 수행해라. 담당 Luna Max.
AGENTS.md, 00-START-HERE.md, 03-LUNA-SERIAL-RUNBOOK.md, R15 13/14/15 설계와 16-ASTRA-UI-HANDOFF.md, 17-VISUAL-COVERAGE-REPAIR.md, 18-SERIAL-PROMPTS-AFTER-T58.md, work/STATUS.md와 work/task-registry-r15.json을 읽어라. 상대 설계 파일은 design/2026-09-25-muscle-atlas/ 아래에 있다. 실행할 task 명세와 선행 실제 보고서·manifest·evidence를 확인하고 정확히 요청된 ID만 수행해라. 시작 HEAD/status/hash를 기록하고 기존 코드/원본/OpenSim_Models/사용자 WIP/역사 freeze를 보존해라. 소유 코드·데이터·보고서·검증만 수정하고 최소 필수 검증과 필요한 실제 화면을 확인해라. 기본 숨김·선택 제한·source-only·license/human-review hold는 명세의 명시적 개별 변경 근거 없이 승격하지 마라. 로딩의 로고·인체 그림·슬로건을 복구하지 말고 단일 장면·카메라·최종 미니멀 UI를 유지해라. task별 report/evidence/STATUS/taskStatuses를 갱신하되 계획을 구현 완료로 표시하지 마라. 필수 실패는 partial/blocked로 남기고 독립 후속 허용 여부와 해결 조건을 구분해라. 소유 변경만 staged diff 확인 후 로컬 커밋하고 해시·제외·잔여 WIP·다음 ID/담당/붙여 넣을 프롬프트를 남겨라. 혼합 WIP는 전체 stage하지 말고 소유 hunk 또는 재현 가능한 상태 delta를 기록해라. 자동 다음 task·push·배포·진단·치료·침 시뮬레이션 금지.
상세 명세: work/tasks/T65.md. 선행: T64.
첫 실행→전신→앞정강근 선택→기시정지/기능→CTA→같은 근육 변형→reset→신경 켜기→관련 신경/지배근→설명 접기를 실제 브라우저에서 검증한다. 전신 visual coverage와 모든 근육의 완전한 content/motion coverage를 분리한다. 핵심 demo 녹화/캡처와 코드·자료·Git 재현을 남긴다.


다음 기본 ID는 T26이다. 추가 batch가 삽입되었으면 registry 순서를 따르고 이번 요청에서는 다음 task를 실행하지 마라.
```

## T26 — 소흉근 구조·작용 학습 자료 (Luna Max)

```text
HUMAN ATLAS에서 T26만 수행해라. 담당 Luna Max.
AGENTS.md, 00-START-HERE.md, 03-LUNA-SERIAL-RUNBOOK.md, R15 13/14/15 설계와 16-ASTRA-UI-HANDOFF.md, 17-VISUAL-COVERAGE-REPAIR.md, 18-SERIAL-PROMPTS-AFTER-T58.md, work/STATUS.md와 work/task-registry-r15.json을 읽어라. 상대 설계 파일은 design/2026-09-25-muscle-atlas/ 아래에 있다. 실행할 task 명세와 선행 실제 보고서·manifest·evidence를 확인하고 정확히 요청된 ID만 수행해라. 시작 HEAD/status/hash를 기록하고 기존 코드/원본/OpenSim_Models/사용자 WIP/역사 freeze를 보존해라. 소유 코드·데이터·보고서·검증만 수정하고 최소 필수 검증과 필요한 실제 화면을 확인해라. 기본 숨김·선택 제한·source-only·license/human-review hold는 명세의 명시적 개별 변경 근거 없이 승격하지 마라. 로딩의 로고·인체 그림·슬로건을 복구하지 말고 단일 장면·카메라·최종 미니멀 UI를 유지해라. task별 report/evidence/STATUS/taskStatuses를 갱신하되 계획을 구현 완료로 표시하지 마라. 필수 실패는 partial/blocked로 남기고 독립 후속 허용 여부와 해결 조건을 구분해라. 소유 변경만 staged diff 확인 후 로컬 커밋하고 해시·제외·잔여 WIP·다음 ID/담당/붙여 넣을 프롬프트를 남겨라. 혼합 WIP는 전체 stage하지 말고 소유 hunk 또는 재현 가능한 상태 delta를 기록해라. 자동 다음 task·push·배포·진단·치료·침 시뮬레이션 금지.
상세 명세: work/tasks/T26.md. 선행: T65.
HA-M-000025 소흉근/작은가슴근/Pectoralis minor의 이름·기시·정지·작용·고정 조건을 직접 원문 대조로 정리한다. 전인/하강/하방회전 후보를 각각 검증하고 조건·차이·충돌을 기록한다. 단순 세 방향을 무조건 독립 주작용으로 확정하지 않는다.

사용자에게는 짧은 한국어 설명을 제공하고 출처는 내부 필드에만 연결한다. 기존 12부위에서 필요한 어깨·어깨뼈/가슴우리 중복 소속을 근거/제품 결정으로 등록한다. 세 이름이 없는 관련 뼈는 조사 대상에 넣는다.

기존 세부 수행 범위는 유지하되 R15 동일 전신 scene/근육 표면 변형/명확한 CTA/신경 우선 순서를 적용한다. 이전 별도 시범 모델 허용은 폐기하며 아래 이전 next/prerequisite 문구는 R15 queue로 대체한다.
다음 기본 ID는 T27이다. 추가 batch가 삽입되었으면 registry 순서를 따르고 이번 요청에서는 다음 task를 실행하지 마라.
```

## T27 — 전신 안의 소흉근 상세 보강 (Luna Max)

```text
HUMAN ATLAS에서 T27만 수행해라. 담당 Luna Max.
AGENTS.md, 00-START-HERE.md, 03-LUNA-SERIAL-RUNBOOK.md, R15 13/14/15 설계와 16-ASTRA-UI-HANDOFF.md, 17-VISUAL-COVERAGE-REPAIR.md, 18-SERIAL-PROMPTS-AFTER-T58.md, work/STATUS.md와 work/task-registry-r15.json을 읽어라. 상대 설계 파일은 design/2026-09-25-muscle-atlas/ 아래에 있다. 실행할 task 명세와 선행 실제 보고서·manifest·evidence를 확인하고 정확히 요청된 ID만 수행해라. 시작 HEAD/status/hash를 기록하고 기존 코드/원본/OpenSim_Models/사용자 WIP/역사 freeze를 보존해라. 소유 코드·데이터·보고서·검증만 수정하고 최소 필수 검증과 필요한 실제 화면을 확인해라. 기본 숨김·선택 제한·source-only·license/human-review hold는 명세의 명시적 개별 변경 근거 없이 승격하지 마라. 로딩의 로고·인체 그림·슬로건을 복구하지 말고 단일 장면·카메라·최종 미니멀 UI를 유지해라. task별 report/evidence/STATUS/taskStatuses를 갱신하되 계획을 구현 완료로 표시하지 마라. 필수 실패는 partial/blocked로 남기고 독립 후속 허용 여부와 해결 조건을 구분해라. 소유 변경만 staged diff 확인 후 로컬 커밋하고 해시·제외·잔여 WIP·다음 ID/담당/붙여 넣을 프롬프트를 남겨라. 혼합 WIP는 전체 stage하지 말고 소유 hunk 또는 재현 가능한 상태 delta를 기록해라. 자동 다음 task·push·배포·진단·치료·침 시뮬레이션 금지.
상세 명세: work/tasks/T27.md. 선행: T26.
T43 확보 경로와 T26 자료로 소흉근·관련 흉곽·견갑골/쇄골의 coherent 정적 장면 하나를 만든다. 필요한 주변 근육과 bone mapping·names·membership을 패키지 manifest에 명시한다. 기존 calf scene을 보존한다.

소흉근 선택 시 선명, 주변 근육 흐림 기본, 관련 뼈 유지, 흐림 해제/깊은 근육 접근을 구현한다. 뼈 선택은 세 이름과 기본 설명으로 연결한다. 신규 rig/복잡한 정합이 필요하면 해당 작업만 Sol 담당으로 분리한다.

T52–56에서 이미 조립한 전신 모델의 소흉근/흉곽/견갑대 high LOD·이름/설명/선택만 보강한다. 새 독립 정적 장면으로 전환하지 않는다. 필요한 local binding·관련 뼈를 같은 body frame에 둔다.
다음 기본 ID는 T28이다. 추가 batch가 삽입되었으면 registry 순서를 따르고 이번 요청에서는 다음 task를 실행하지 마라.
```

## T28 — 견갑대 운동 기반과 전인 시범 하나 (Sol High)

```text
HUMAN ATLAS에서 T28만 수행해라. 담당 Sol High.
AGENTS.md, 00-START-HERE.md, 03-LUNA-SERIAL-RUNBOOK.md, R15 13/14/15 설계와 16-ASTRA-UI-HANDOFF.md, 17-VISUAL-COVERAGE-REPAIR.md, 18-SERIAL-PROMPTS-AFTER-T58.md, work/STATUS.md와 work/task-registry-r15.json을 읽어라. 상대 설계 파일은 design/2026-09-25-muscle-atlas/ 아래에 있다. 실행할 task 명세와 선행 실제 보고서·manifest·evidence를 확인하고 정확히 요청된 ID만 수행해라. 시작 HEAD/status/hash를 기록하고 기존 코드/원본/OpenSim_Models/사용자 WIP/역사 freeze를 보존해라. 소유 코드·데이터·보고서·검증만 수정하고 최소 필수 검증과 필요한 실제 화면을 확인해라. 기본 숨김·선택 제한·source-only·license/human-review hold는 명세의 명시적 개별 변경 근거 없이 승격하지 마라. 로딩의 로고·인체 그림·슬로건을 복구하지 말고 단일 장면·카메라·최종 미니멀 UI를 유지해라. task별 report/evidence/STATUS/taskStatuses를 갱신하되 계획을 구현 완료로 표시하지 마라. 필수 실패는 partial/blocked로 남기고 독립 후속 허용 여부와 해결 조건을 구분해라. 소유 변경만 staged diff 확인 후 로컬 커밋하고 해시·제외·잔여 WIP·다음 ID/담당/붙여 넣을 프롬프트를 남겨라. 혼합 WIP는 전체 stage하지 말고 소유 hunk 또는 재현 가능한 상태 delta를 기록해라. 자동 다음 task·push·배포·진단·치료·침 시뮬레이션 금지.
상세 명세: work/tasks/T28.md. 선행: T27.
T26에서 확정한 조건의 소흉근 관련 견갑골 전인 시범 1개를 제작한다. 흉곽에 대한 견갑대의 이동/회전과 고정 조건을 모델링하고 T45/T46에서 재사용할 골격·경로 제작 도구를 만든다.

단일 임의 hinge 또는 상완골만 움직이는 것으로 견갑골 작용을 대신하지 않는다. 근육 endpoint/변형 또는 표시된 설명 경로를 함께 제공한다. T44의 좌표 정합 원칙을 재사용하되 발목 좌표를 복제하지 않는다.

기존 세부 수행 범위는 유지하되 R15 동일 전신 scene/근육 표면 변형/명확한 CTA/신경 우선 순서를 적용한다. 이전 별도 시범 모델 허용은 폐기하며 아래 이전 next/prerequisite 문구는 R15 queue로 대체한다.
다음 기본 ID는 T45이다. 추가 batch가 삽입되었으면 registry 순서를 따르고 이번 요청에서는 다음 task를 실행하지 마라.
```

## T45 — 소흉근 관련 견갑골 하강 시범 (Sol High)

```text
HUMAN ATLAS에서 T45만 수행해라. 담당 Sol High.
AGENTS.md, 00-START-HERE.md, 03-LUNA-SERIAL-RUNBOOK.md, R15 13/14/15 설계와 16-ASTRA-UI-HANDOFF.md, 17-VISUAL-COVERAGE-REPAIR.md, 18-SERIAL-PROMPTS-AFTER-T58.md, work/STATUS.md와 work/task-registry-r15.json을 읽어라. 상대 설계 파일은 design/2026-09-25-muscle-atlas/ 아래에 있다. 실행할 task 명세와 선행 실제 보고서·manifest·evidence를 확인하고 정확히 요청된 ID만 수행해라. 시작 HEAD/status/hash를 기록하고 기존 코드/원본/OpenSim_Models/사용자 WIP/역사 freeze를 보존해라. 소유 코드·데이터·보고서·검증만 수정하고 최소 필수 검증과 필요한 실제 화면을 확인해라. 기본 숨김·선택 제한·source-only·license/human-review hold는 명세의 명시적 개별 변경 근거 없이 승격하지 마라. 로딩의 로고·인체 그림·슬로건을 복구하지 말고 단일 장면·카메라·최종 미니멀 UI를 유지해라. task별 report/evidence/STATUS/taskStatuses를 갱신하되 계획을 구현 완료로 표시하지 마라. 필수 실패는 partial/blocked로 남기고 독립 후속 허용 여부와 해결 조건을 구분해라. 소유 변경만 staged diff 확인 후 로컬 커밋하고 해시·제외·잔여 WIP·다음 ID/담당/붙여 넣을 프롬프트를 남겨라. 혼합 WIP는 전체 stage하지 말고 소유 hunk 또는 재현 가능한 상태 delta를 기록해라. 자동 다음 task·push·배포·진단·치료·침 시뮬레이션 금지.
상세 명세: work/tasks/T45.md. 선행: T28.
T28 기반을 재사용해 T26에서 근거/조건이 확인된 하강 시범 clip1개를 만든다. 단순 전인 clip의 축값을 바꿔 해부학 근거 대신 쓰지 않는다. moving/fixed structures·근육 경로와 설명을 연결한다.

기존 세부 수행 범위는 유지하되 R15 동일 전신 scene/근육 표면 변형/명확한 CTA/신경 우선 순서를 적용한다. 이전 별도 시범 모델 허용은 폐기하며 아래 이전 next/prerequisite 문구는 R15 queue로 대체한다.
다음 기본 ID는 T46이다. 추가 batch가 삽입되었으면 registry 순서를 따르고 이번 요청에서는 다음 task를 실행하지 마라.
```

## T46 — 소흉근 관련 견갑골 하방회전 시범 (Sol High)

```text
HUMAN ATLAS에서 T46만 수행해라. 담당 Sol High.
AGENTS.md, 00-START-HERE.md, 03-LUNA-SERIAL-RUNBOOK.md, R15 13/14/15 설계와 16-ASTRA-UI-HANDOFF.md, 17-VISUAL-COVERAGE-REPAIR.md, 18-SERIAL-PROMPTS-AFTER-T58.md, work/STATUS.md와 work/task-registry-r15.json을 읽어라. 상대 설계 파일은 design/2026-09-25-muscle-atlas/ 아래에 있다. 실행할 task 명세와 선행 실제 보고서·manifest·evidence를 확인하고 정확히 요청된 ID만 수행해라. 시작 HEAD/status/hash를 기록하고 기존 코드/원본/OpenSim_Models/사용자 WIP/역사 freeze를 보존해라. 소유 코드·데이터·보고서·검증만 수정하고 최소 필수 검증과 필요한 실제 화면을 확인해라. 기본 숨김·선택 제한·source-only·license/human-review hold는 명세의 명시적 개별 변경 근거 없이 승격하지 마라. 로딩의 로고·인체 그림·슬로건을 복구하지 말고 단일 장면·카메라·최종 미니멀 UI를 유지해라. task별 report/evidence/STATUS/taskStatuses를 갱신하되 계획을 구현 완료로 표시하지 마라. 필수 실패는 partial/blocked로 남기고 독립 후속 허용 여부와 해결 조건을 구분해라. 소유 변경만 staged diff 확인 후 로컬 커밋하고 해시·제외·잔여 WIP·다음 ID/담당/붙여 넣을 프롬프트를 남겨라. 혼합 WIP는 전체 stage하지 말고 소유 hunk 또는 재현 가능한 상태 delta를 기록해라. 자동 다음 task·push·배포·진단·치료·침 시뮬레이션 금지.
상세 명세: work/tasks/T46.md. 선행: T45.
T28 기반으로 T26에서 근거/조건이 확인된 하방회전 시범 clip1개를 만든다. 회전 방향과 흉곽 정합을 검증하며 전인/하강과 작용 ID를 구분한다. 대표 시범을 생체 운동의 정량 재현으로 주장하지 않는다.

기존 세부 수행 범위는 유지하되 R15 동일 전신 scene/근육 표면 변형/명확한 CTA/신경 우선 순서를 적용한다. 이전 별도 시범 모델 허용은 폐기하며 아래 이전 next/prerequisite 문구는 R15 queue로 대체한다.
다음 기본 ID는 T29이다. 추가 batch가 삽입되었으면 registry 순서를 따르고 이번 요청에서는 다음 task를 실행하지 마라.
```

## T29 — 소흉근 구조·기능 사용자 흐름 통합 (Luna Max)

```text
HUMAN ATLAS에서 T29만 수행해라. 담당 Luna Max.
AGENTS.md, 00-START-HERE.md, 03-LUNA-SERIAL-RUNBOOK.md, R15 13/14/15 설계와 16-ASTRA-UI-HANDOFF.md, 17-VISUAL-COVERAGE-REPAIR.md, 18-SERIAL-PROMPTS-AFTER-T58.md, work/STATUS.md와 work/task-registry-r15.json을 읽어라. 상대 설계 파일은 design/2026-09-25-muscle-atlas/ 아래에 있다. 실행할 task 명세와 선행 실제 보고서·manifest·evidence를 확인하고 정확히 요청된 ID만 수행해라. 시작 HEAD/status/hash를 기록하고 기존 코드/원본/OpenSim_Models/사용자 WIP/역사 freeze를 보존해라. 소유 코드·데이터·보고서·검증만 수정하고 최소 필수 검증과 필요한 실제 화면을 확인해라. 기본 숨김·선택 제한·source-only·license/human-review hold는 명세의 명시적 개별 변경 근거 없이 승격하지 마라. 로딩의 로고·인체 그림·슬로건을 복구하지 말고 단일 장면·카메라·최종 미니멀 UI를 유지해라. task별 report/evidence/STATUS/taskStatuses를 갱신하되 계획을 구현 완료로 표시하지 마라. 필수 실패는 partial/blocked로 남기고 독립 후속 허용 여부와 해결 조건을 구분해라. 소유 변경만 staged diff 확인 후 로컬 커밋하고 해시·제외·잔여 WIP·다음 ID/담당/붙여 넣을 프롬프트를 남겨라. 혼합 WIP는 전체 stage하지 말고 소유 hunk 또는 재현 가능한 상태 delta를 기록해라. 자동 다음 task·push·배포·진단·치료·침 시뮬레이션 금지.
상세 명세: work/tasks/T29.md. 선행: T46.
소흉근 선택→주변 흐림→구조 설명→CTA→전인/하강/하방회전 작용 선택→해당 실제 clip과 설명으로 연결한다. 지원하지 않는 작용은 다른 clip으로 대체하지 않는다. 뼈 카드의 세 이름과 근육으로 돌아오는 흐름을 검증한다.

기존 세부 수행 범위는 유지하되 R15 동일 전신 scene/근육 표면 변형/명확한 CTA/신경 우선 순서를 적용한다. 이전 별도 시범 모델 허용은 폐기하며 아래 이전 next/prerequisite 문구는 R15 queue로 대체한다.
다음 기본 ID는 T30이다. 추가 batch가 삽입되었으면 registry 순서를 따르고 이번 요청에서는 다음 task를 실행하지 마라.
```

## T30 — 모형 중심 화면과 성능 정리 (Luna Max)

```text
HUMAN ATLAS에서 T30만 수행해라. 담당 Luna Max.
AGENTS.md, 00-START-HERE.md, 03-LUNA-SERIAL-RUNBOOK.md, R15 13/14/15 설계와 16-ASTRA-UI-HANDOFF.md, 17-VISUAL-COVERAGE-REPAIR.md, 18-SERIAL-PROMPTS-AFTER-T58.md, work/STATUS.md와 work/task-registry-r15.json을 읽어라. 상대 설계 파일은 design/2026-09-25-muscle-atlas/ 아래에 있다. 실행할 task 명세와 선행 실제 보고서·manifest·evidence를 확인하고 정확히 요청된 ID만 수행해라. 시작 HEAD/status/hash를 기록하고 기존 코드/원본/OpenSim_Models/사용자 WIP/역사 freeze를 보존해라. 소유 코드·데이터·보고서·검증만 수정하고 최소 필수 검증과 필요한 실제 화면을 확인해라. 기본 숨김·선택 제한·source-only·license/human-review hold는 명세의 명시적 개별 변경 근거 없이 승격하지 마라. 로딩의 로고·인체 그림·슬로건을 복구하지 말고 단일 장면·카메라·최종 미니멀 UI를 유지해라. task별 report/evidence/STATUS/taskStatuses를 갱신하되 계획을 구현 완료로 표시하지 마라. 필수 실패는 partial/blocked로 남기고 독립 후속 허용 여부와 해결 조건을 구분해라. 소유 변경만 staged diff 확인 후 로컬 커밋하고 해시·제외·잔여 WIP·다음 ID/담당/붙여 넣을 프롬프트를 남겨라. 혼합 WIP는 전체 stage하지 말고 소유 hunk 또는 재현 가능한 상태 delta를 기록해라. 자동 다음 task·push·배포·진단·치료·침 시뮬레이션 금지.
상세 명세: work/tasks/T30.md. 선행: T29.
밝은 배경/절제된 근육색/아이보리 뼈와 큰 모형을 유지한다. 좌우 패널 접기, 선택 구조 fit, 부위 카메라 preset, 모바일 하단 카드로 CTA와 모형을 동시에 접근 가능하게 한다. 검토 상태·출처 설명으로 공간을 채우지 않는다.

learner/review와 부위별 데이터/scene 로딩을 분리한다. 1440/1024/390에서 화면·입력·console·network·프레임 시간을 측정하고 측정 환경/자산 규모를 기록한다. 경고 임계값을 올려 용량 문제를 숨기지 않는다.

기존 세부 수행 범위는 유지하되 R15 동일 전신 scene/근육 표면 변형/명확한 CTA/신경 우선 순서를 적용한다. 이전 별도 시범 모델 허용은 폐기하며 아래 이전 next/prerequisite 문구는 R15 queue로 대체한다.
다음 기본 ID는 T31이다. 추가 batch가 삽입되었으면 registry 순서를 따르고 이번 요청에서는 다음 task를 실행하지 마라.
```

## T31 — 두 부위 구조·기능 파일럿 합격 검증 (Luna Max)

```text
HUMAN ATLAS에서 T31만 수행해라. 담당 Luna Max.
AGENTS.md, 00-START-HERE.md, 03-LUNA-SERIAL-RUNBOOK.md, R15 13/14/15 설계와 16-ASTRA-UI-HANDOFF.md, 17-VISUAL-COVERAGE-REPAIR.md, 18-SERIAL-PROMPTS-AFTER-T58.md, work/STATUS.md와 work/task-registry-r15.json을 읽어라. 상대 설계 파일은 design/2026-09-25-muscle-atlas/ 아래에 있다. 실행할 task 명세와 선행 실제 보고서·manifest·evidence를 확인하고 정확히 요청된 ID만 수행해라. 시작 HEAD/status/hash를 기록하고 기존 코드/원본/OpenSim_Models/사용자 WIP/역사 freeze를 보존해라. 소유 코드·데이터·보고서·검증만 수정하고 최소 필수 검증과 필요한 실제 화면을 확인해라. 기본 숨김·선택 제한·source-only·license/human-review hold는 명세의 명시적 개별 변경 근거 없이 승격하지 마라. 로딩의 로고·인체 그림·슬로건을 복구하지 말고 단일 장면·카메라·최종 미니멀 UI를 유지해라. task별 report/evidence/STATUS/taskStatuses를 갱신하되 계획을 구현 완료로 표시하지 마라. 필수 실패는 partial/blocked로 남기고 독립 후속 허용 여부와 해결 조건을 구분해라. 소유 변경만 staged diff 확인 후 로컬 커밋하고 해시·제외·잔여 WIP·다음 ID/담당/붙여 넣을 프롬프트를 남겨라. 혼합 WIP는 전체 stage하지 말고 소유 hunk 또는 재현 가능한 상태 delta를 기록해라. 자동 다음 task·push·배포·진단·치료·침 시뮬레이션 금지.
상세 명세: work/tasks/T31.md. 선행: T30.
종아리와 소흉근의 실제 data/scene/clip을 전체 사용자 흐름으로 검사한다. 세 이름·기시정지·뼈 카드·클릭·흐림·움직임·설명·복원을 함께 확인한다. 데이터 검증과 실제 화면 검증을 분리 기록한다.

기존 세부 수행 범위는 유지하되 R15 동일 전신 scene/근육 표면 변형/명확한 CTA/신경 우선 순서를 적용한다. 이전 별도 시범 모델 허용은 폐기하며 아래 이전 next/prerequisite 문구는 R15 queue로 대체한다.
다음 기본 ID는 T32이다. 추가 batch가 삽입되었으면 registry 순서를 따르고 이번 요청에서는 다음 task를 실행하지 마라.
```

## T32 — 전신 목표 목록 동결과 부위 패키지 배정 (Luna Max)

```text
HUMAN ATLAS에서 T32만 수행해라. 담당 Luna Max.
AGENTS.md, 00-START-HERE.md, 03-LUNA-SERIAL-RUNBOOK.md, R15 13/14/15 설계와 16-ASTRA-UI-HANDOFF.md, 17-VISUAL-COVERAGE-REPAIR.md, 18-SERIAL-PROMPTS-AFTER-T58.md, work/STATUS.md와 work/task-registry-r15.json을 읽어라. 상대 설계 파일은 design/2026-09-25-muscle-atlas/ 아래에 있다. 실행할 task 명세와 선행 실제 보고서·manifest·evidence를 확인하고 정확히 요청된 ID만 수행해라. 시작 HEAD/status/hash를 기록하고 기존 코드/원본/OpenSim_Models/사용자 WIP/역사 freeze를 보존해라. 소유 코드·데이터·보고서·검증만 수정하고 최소 필수 검증과 필요한 실제 화면을 확인해라. 기본 숨김·선택 제한·source-only·license/human-review hold는 명세의 명시적 개별 변경 근거 없이 승격하지 마라. 로딩의 로고·인체 그림·슬로건을 복구하지 말고 단일 장면·카메라·최종 미니멀 UI를 유지해라. task별 report/evidence/STATUS/taskStatuses를 갱신하되 계획을 구현 완료로 표시하지 마라. 필수 실패는 partial/blocked로 남기고 독립 후속 허용 여부와 해결 조건을 구분해라. 소유 변경만 staged diff 확인 후 로컬 커밋하고 해시·제외·잔여 WIP·다음 ID/담당/붙여 넣을 프롬프트를 남겨라. 혼합 WIP는 전체 stage하지 말고 소유 hunk 또는 재현 가능한 상태 delta를 기록해라. 자동 다음 task·push·배포·진단·치료·침 시뮬레이션 금지.
상세 명세: work/tasks/T32.md. 선행: T31.
T43 조사와 T31 결과를 재사용해 전신 포함/제외 규칙·unique 근육/부분/군/뼈 분모·12부위 다중 소속을 확정한다. T43 조사 전체를 반복하지 않는다. 불명확한 분모는 unknown으로 두고 전신 complete를 금지한다.

각 부위 패키지에 ID 목록/목표 scene/세 이름/기시정지/작용 텍스트/동작 연결/누락을 명시한다. T33 대상 하나를 선정하고 나머지는 다음 미사용 숫자 task로 등록한다. 구조 패키지는 T33과 T34 사이, 동작 패키지는 T35와 T47 사이에 삽입한다.

R14 package manifest에 대상 ID·상한·내부 batch·source revision·합격 조건·출력을 고정한다. task마다 공통 스키마를 재설계하지 않는다.

기존 세부 수행 범위는 유지하되 R15 동일 전신 scene/근육 표면 변형/명확한 CTA/신경 우선 순서를 적용한다. 이전 별도 시범 모델 허용은 폐기하며 아래 이전 next/prerequisite 문구는 R15 queue로 대체한다.
다음 기본 ID는 T33이다. 추가 batch가 삽입되었으면 registry 순서를 따르고 이번 요청에서는 다음 task를 실행하지 마라.
```

## T33 — 첫 지역 구조·기능 텍스트 패키지 (Luna Max)

```text
HUMAN ATLAS에서 T33만 수행해라. 담당 Luna Max.
AGENTS.md, 00-START-HERE.md, 03-LUNA-SERIAL-RUNBOOK.md, R15 13/14/15 설계와 16-ASTRA-UI-HANDOFF.md, 17-VISUAL-COVERAGE-REPAIR.md, 18-SERIAL-PROMPTS-AFTER-T58.md, work/STATUS.md와 work/task-registry-r15.json을 읽어라. 상대 설계 파일은 design/2026-09-25-muscle-atlas/ 아래에 있다. 실행할 task 명세와 선행 실제 보고서·manifest·evidence를 확인하고 정확히 요청된 ID만 수행해라. 시작 HEAD/status/hash를 기록하고 기존 코드/원본/OpenSim_Models/사용자 WIP/역사 freeze를 보존해라. 소유 코드·데이터·보고서·검증만 수정하고 최소 필수 검증과 필요한 실제 화면을 확인해라. 기본 숨김·선택 제한·source-only·license/human-review hold는 명세의 명시적 개별 변경 근거 없이 승격하지 마라. 로딩의 로고·인체 그림·슬로건을 복구하지 말고 단일 장면·카메라·최종 미니멀 UI를 유지해라. task별 report/evidence/STATUS/taskStatuses를 갱신하되 계획을 구현 완료로 표시하지 마라. 필수 실패는 partial/blocked로 남기고 독립 후속 허용 여부와 해결 조건을 구분해라. 소유 변경만 staged diff 확인 후 로컬 커밋하고 해시·제외·잔여 WIP·다음 ID/담당/붙여 넣을 프롬프트를 남겨라. 혼합 WIP는 전체 stage하지 말고 소유 hunk 또는 재현 가능한 상태 delta를 기록해라. 자동 다음 task·push·배포·진단·치료·침 시뮬레이션 금지.
상세 명세: work/tasks/T33.md. 선행: T32.
T32가 고정한 한 지역/한 scene 패키지를 구현한다. 모든 패키지 대상의 이름·기시정지·핵심 작용·근육/뼈 mapping·다중 소속·검색·카드를 연결한다. 내부 5–10개 검증 batch를 재사용해 처리한다.

기존 지원 clip은 호환 frame/pose/의미가 확인된 경우만 연결한다. 새 rig/clip 제작은 별도 작업이며 지원 없는 CTA는 준비 중이다. 다른 부위/예외를 조용히 추가하지 않는다.

기존 세부 수행 범위는 유지하되 R15 동일 전신 scene/근육 표면 변형/명확한 CTA/신경 우선 순서를 적용한다. 이전 별도 시범 모델 허용은 폐기하며 아래 이전 next/prerequisite 문구는 R15 queue로 대체한다.
다음 기본 ID는 T34이다. 추가 batch가 삽입되었으면 registry 순서를 따르고 이번 요청에서는 다음 task를 실행하지 마라.
```

## T34 — 구조 범위 감사만 수행 (Luna Max)

```text
HUMAN ATLAS에서 T34만 수행해라. 담당 Luna Max.
AGENTS.md, 00-START-HERE.md, 03-LUNA-SERIAL-RUNBOOK.md, R15 13/14/15 설계와 16-ASTRA-UI-HANDOFF.md, 17-VISUAL-COVERAGE-REPAIR.md, 18-SERIAL-PROMPTS-AFTER-T58.md, work/STATUS.md와 work/task-registry-r15.json을 읽어라. 상대 설계 파일은 design/2026-09-25-muscle-atlas/ 아래에 있다. 실행할 task 명세와 선행 실제 보고서·manifest·evidence를 확인하고 정확히 요청된 ID만 수행해라. 시작 HEAD/status/hash를 기록하고 기존 코드/원본/OpenSim_Models/사용자 WIP/역사 freeze를 보존해라. 소유 코드·데이터·보고서·검증만 수정하고 최소 필수 검증과 필요한 실제 화면을 확인해라. 기본 숨김·선택 제한·source-only·license/human-review hold는 명세의 명시적 개별 변경 근거 없이 승격하지 마라. 로딩의 로고·인체 그림·슬로건을 복구하지 말고 단일 장면·카메라·최종 미니멀 UI를 유지해라. task별 report/evidence/STATUS/taskStatuses를 갱신하되 계획을 구현 완료로 표시하지 마라. 필수 실패는 partial/blocked로 남기고 독립 후속 허용 여부와 해결 조건을 구분해라. 소유 변경만 staged diff 확인 후 로컬 커밋하고 해시·제외·잔여 WIP·다음 ID/담당/붙여 넣을 프롬프트를 남겨라. 혼합 WIP는 전체 stage하지 말고 소유 hunk 또는 재현 가능한 상태 delta를 기록해라. 자동 다음 task·push·배포·진단·치료·침 시뮬레이션 금지.
상세 명세: work/tasks/T34.md. 선행: T33.
T32에 등록한 모든 구조 패키지 실제 결과를 분모와 대조한다. 근육/뼈 세 이름, 기시정지, scene mapping, 중복 소속, orphan ID, unbound mesh와 부착 표면 준비를 독립 집계한다. 미구현 지역을 숨기거나 분모에서 자동 삭제하지 않는다.

동결한 분모와 실제 패키지 결과를 자동 집계·대조하는 read-only audit다. 전신 자료 입력/대규모 UI 수정/누락 mesh 제작을 이 task에서 하지 않는다. 지역별 누락/오류를 재현하고 대상 ID·담당·합격 기준을 가진 별도 수정 task로 배정한다. 집계 오류의 작은 감사 도구 수정만 허용한다. 누락이 없을 때만 structure gate pass.
다음 기본 ID는 T35이다. 추가 batch가 삽입되었으면 registry 순서를 따르고 이번 요청에서는 다음 task를 실행하지 마라.
```

## T35 — 작용군 목록과 확장 queue만 확정 (Luna Max)

```text
HUMAN ATLAS에서 T35만 수행해라. 담당 Luna Max.
AGENTS.md, 00-START-HERE.md, 03-LUNA-SERIAL-RUNBOOK.md, R15 13/14/15 설계와 16-ASTRA-UI-HANDOFF.md, 17-VISUAL-COVERAGE-REPAIR.md, 18-SERIAL-PROMPTS-AFTER-T58.md, work/STATUS.md와 work/task-registry-r15.json을 읽어라. 상대 설계 파일은 design/2026-09-25-muscle-atlas/ 아래에 있다. 실행할 task 명세와 선행 실제 보고서·manifest·evidence를 확인하고 정확히 요청된 ID만 수행해라. 시작 HEAD/status/hash를 기록하고 기존 코드/원본/OpenSim_Models/사용자 WIP/역사 freeze를 보존해라. 소유 코드·데이터·보고서·검증만 수정하고 최소 필수 검증과 필요한 실제 화면을 확인해라. 기본 숨김·선택 제한·source-only·license/human-review hold는 명세의 명시적 개별 변경 근거 없이 승격하지 마라. 로딩의 로고·인체 그림·슬로건을 복구하지 말고 단일 장면·카메라·최종 미니멀 UI를 유지해라. task별 report/evidence/STATUS/taskStatuses를 갱신하되 계획을 구현 완료로 표시하지 마라. 필수 실패는 partial/blocked로 남기고 독립 후속 허용 여부와 해결 조건을 구분해라. 소유 변경만 staged diff 확인 후 로컬 커밋하고 해시·제외·잔여 WIP·다음 ID/담당/붙여 넣을 프롬프트를 남겨라. 혼합 WIP는 전체 stage하지 말고 소유 hunk 또는 재현 가능한 상태 delta를 기록해라. 자동 다음 task·push·배포·진단·치료·침 시뮬레이션 금지.
상세 명세: work/tasks/T35.md. 선행: T34.
T34 구조 결과로 action-family와 조건·움직이는 뼈·근육별 역할을 정리한다. 실제 의미·frame/pose가 같은 clip을 공유하고 근육별 설명은 별도로 둔다. 한 근육의 여러 작용을 누락시키는 find-first API가 있으면 collection 기반으로 정리한다.

첫 기존 rig 기반 action-family 한 개만 구현한다. 새 관절/정합/rig는 Sol 담당 별도 숫자 task로 등록한다. 나머지 기능 패키지 전부를 T47 앞 queue에 배정한다.

planning-only task다. 현재 모델에서 재사용 가능한 action-family·고정 조건·모델/frame/pose·clip 지원을 정리하고 bounded 작업으로 나눈다. 첫 clip 제작/전신 기능 자료 입력까지 같이 하지 않는다. 실제 첫 batch는 T66이다. T66 이후 필요한 작업을 T47 앞에 넣는다.
다음 기본 ID는 T66이다. 추가 batch가 삽입되었으면 registry 순서를 따르고 이번 요청에서는 다음 task를 실행하지 마라.
```

## T66 — 첫 기능 확장 batch 하나 (Luna Max)

```text
HUMAN ATLAS에서 T66만 수행해라. 담당 Luna Max.
AGENTS.md, 00-START-HERE.md, 03-LUNA-SERIAL-RUNBOOK.md, R15 13/14/15 설계와 16-ASTRA-UI-HANDOFF.md, 17-VISUAL-COVERAGE-REPAIR.md, 18-SERIAL-PROMPTS-AFTER-T58.md, work/STATUS.md와 work/task-registry-r15.json을 읽어라. 상대 설계 파일은 design/2026-09-25-muscle-atlas/ 아래에 있다. 실행할 task 명세와 선행 실제 보고서·manifest·evidence를 확인하고 정확히 요청된 ID만 수행해라. 시작 HEAD/status/hash를 기록하고 기존 코드/원본/OpenSim_Models/사용자 WIP/역사 freeze를 보존해라. 소유 코드·데이터·보고서·검증만 수정하고 최소 필수 검증과 필요한 실제 화면을 확인해라. 기본 숨김·선택 제한·source-only·license/human-review hold는 명세의 명시적 개별 변경 근거 없이 승격하지 마라. 로딩의 로고·인체 그림·슬로건을 복구하지 말고 단일 장면·카메라·최종 미니멀 UI를 유지해라. task별 report/evidence/STATUS/taskStatuses를 갱신하되 계획을 구현 완료로 표시하지 마라. 필수 실패는 partial/blocked로 남기고 독립 후속 허용 여부와 해결 조건을 구분해라. 소유 변경만 staged diff 확인 후 로컬 커밋하고 해시·제외·잔여 WIP·다음 ID/담당/붙여 넣을 프롬프트를 남겨라. 혼합 WIP는 전체 stage하지 말고 소유 hunk 또는 재현 가능한 상태 delta를 기록해라. 자동 다음 task·push·배포·진단·치료·침 시뮬레이션 금지.
상세 명세: work/tasks/T66.md. 선행: T35.
T35에서 동결한 단일 action-family를 대상으로 검증된 동일 rig의 공유 clip 연결 최대10관계 또는 기존 rig 기반 clip1개만 구현한다. 새 관절/rig 정합이 필요하면 Sol task로 따로 배정하고 이 task를 확장하지 않는다.


다음 기본 ID는 T47이다. 추가 batch가 삽입되었으면 registry 순서를 따르고 이번 요청에서는 다음 task를 실행하지 마라.
```

## T47 — 전신 구조·기능 완료 판정 (Luna Max)

```text
HUMAN ATLAS에서 T47만 수행해라. 담당 Luna Max.
AGENTS.md, 00-START-HERE.md, 03-LUNA-SERIAL-RUNBOOK.md, R15 13/14/15 설계와 16-ASTRA-UI-HANDOFF.md, 17-VISUAL-COVERAGE-REPAIR.md, 18-SERIAL-PROMPTS-AFTER-T58.md, work/STATUS.md와 work/task-registry-r15.json을 읽어라. 상대 설계 파일은 design/2026-09-25-muscle-atlas/ 아래에 있다. 실행할 task 명세와 선행 실제 보고서·manifest·evidence를 확인하고 정확히 요청된 ID만 수행해라. 시작 HEAD/status/hash를 기록하고 기존 코드/원본/OpenSim_Models/사용자 WIP/역사 freeze를 보존해라. 소유 코드·데이터·보고서·검증만 수정하고 최소 필수 검증과 필요한 실제 화면을 확인해라. 기본 숨김·선택 제한·source-only·license/human-review hold는 명세의 명시적 개별 변경 근거 없이 승격하지 마라. 로딩의 로고·인체 그림·슬로건을 복구하지 말고 단일 장면·카메라·최종 미니멀 UI를 유지해라. task별 report/evidence/STATUS/taskStatuses를 갱신하되 계획을 구현 완료로 표시하지 마라. 필수 실패는 partial/blocked로 남기고 독립 후속 허용 여부와 해결 조건을 구분해라. 소유 변경만 staged diff 확인 후 로컬 커밋하고 해시·제외·잔여 WIP·다음 ID/담당/붙여 넣을 프롬프트를 남겨라. 혼합 WIP는 전체 stage하지 말고 소유 hunk 또는 재현 가능한 상태 delta를 기록해라. 자동 다음 task·push·배포·진단·치료·침 시뮬레이션 금지.
상세 명세: work/tasks/T47.md. 선행: T66.
동결한 대상 전체와 T34 구조/T35 이후 기능 패키지 결과를 합쳐 release checklist를 검증한다. 이름/구조/작용 텍스트/실제 움직임 지원/정밀 표면을 각각 집계한다. 12부위의 실제 사용자 경로를 검증한다.

전체 포함 근육의 약속한 작용이 실제 clip 또는 검증된 공유 clip으로 연결되어야 structure_function_complete다. 설명용 경로는 근육 변형과 구분하지만 해당 뼈가 실제로 움직이면 교육용 시범으로 인정한다. 생리적 수축 시뮬레이션 완료로 확대하지 않는다.

기존 세부 수행 범위는 유지하되 R15 동일 전신 scene/근육 표면 변형/명확한 CTA/신경 우선 순서를 적용한다. 이전 별도 시범 모델 허용은 폐기하며 아래 이전 next/prerequisite 문구는 R15 queue로 대체한다.
다음 기본 ID는 T40이다. 추가 batch가 삽입되었으면 registry 순서를 따르고 이번 요청에서는 다음 task를 실행하지 마라.
```

## T40 — 구조·기능 로컬 전달과 Git 체크포인트 (Luna Max)

```text
HUMAN ATLAS에서 T40만 수행해라. 담당 Luna Max.
AGENTS.md, 00-START-HERE.md, 03-LUNA-SERIAL-RUNBOOK.md, R15 13/14/15 설계와 16-ASTRA-UI-HANDOFF.md, 17-VISUAL-COVERAGE-REPAIR.md, 18-SERIAL-PROMPTS-AFTER-T58.md, work/STATUS.md와 work/task-registry-r15.json을 읽어라. 상대 설계 파일은 design/2026-09-25-muscle-atlas/ 아래에 있다. 실행할 task 명세와 선행 실제 보고서·manifest·evidence를 확인하고 정확히 요청된 ID만 수행해라. 시작 HEAD/status/hash를 기록하고 기존 코드/원본/OpenSim_Models/사용자 WIP/역사 freeze를 보존해라. 소유 코드·데이터·보고서·검증만 수정하고 최소 필수 검증과 필요한 실제 화면을 확인해라. 기본 숨김·선택 제한·source-only·license/human-review hold는 명세의 명시적 개별 변경 근거 없이 승격하지 마라. 로딩의 로고·인체 그림·슬로건을 복구하지 말고 단일 장면·카메라·최종 미니멀 UI를 유지해라. task별 report/evidence/STATUS/taskStatuses를 갱신하되 계획을 구현 완료로 표시하지 마라. 필수 실패는 partial/blocked로 남기고 독립 후속 허용 여부와 해결 조건을 구분해라. 소유 변경만 staged diff 확인 후 로컬 커밋하고 해시·제외·잔여 WIP·다음 ID/담당/붙여 넣을 프롬프트를 남겨라. 혼합 WIP는 전체 stage하지 말고 소유 hunk 또는 재현 가능한 상태 delta를 기록해라. 자동 다음 task·push·배포·진단·치료·침 시뮬레이션 금지.
상세 명세: work/tasks/T40.md. 선행: T47.
T47 실제 결과 기준으로 실행/설치/자료 추가/검증/복구 안내와 로컬 전달 빌드를 만든다. 평가·퀴즈 구현을 이번 전달의 필수 선행으로 두지 않는다. 재현 가능한 checkout과 asset 확보 방법을 검증한다.

기존 세부 수행 범위는 유지하되 R15 동일 전신 scene/근육 표면 변형/명확한 CTA/신경 우선 순서를 적용한다. 이전 별도 시범 모델 허용은 폐기하며 아래 이전 next/prerequisite 문구는 R15 queue로 대체한다.
다음 기본 ID는 없음 — 종료이다. 추가 batch가 삽입되었으면 registry 순서를 따르고 이번 요청에서는 다음 task를 실행하지 마라.
```

## 별도 착수 요청까지 보류

주요 평가: T67 → T36 → T37 → T48 → T49 → T38. 경혈·경락: T68 별도 설계. 아래는 예약 프롬프트이며 현재 active queue에 넣지 않는다.

### T67 — 주요 근육 평가법 선정 목록 (Luna Max)

```text
주요 평가 착수(또는 T68 경혈 후속 설계)를 명시적으로 요청한다. HUMAN ATLAS에서 T67만 수행해라. 담당 Luna Max.
AGENTS.md, 00-START-HERE.md, 03-LUNA-SERIAL-RUNBOOK.md, R15 13/14/15 설계와 16-ASTRA-UI-HANDOFF.md, 17-VISUAL-COVERAGE-REPAIR.md, 18-SERIAL-PROMPTS-AFTER-T58.md, work/STATUS.md와 work/task-registry-r15.json을 읽어라. 상대 설계 파일은 design/2026-09-25-muscle-atlas/ 아래에 있다. 실행할 task 명세와 선행 실제 보고서·manifest·evidence를 확인하고 정확히 요청된 ID만 수행해라. 시작 HEAD/status/hash를 기록하고 기존 코드/원본/OpenSim_Models/사용자 WIP/역사 freeze를 보존해라. 소유 코드·데이터·보고서·검증만 수정하고 최소 필수 검증과 필요한 실제 화면을 확인해라. 기본 숨김·선택 제한·source-only·license/human-review hold는 명세의 명시적 개별 변경 근거 없이 승격하지 마라. 로딩의 로고·인체 그림·슬로건을 복구하지 말고 단일 장면·카메라·최종 미니멀 UI를 유지해라. task별 report/evidence/STATUS/taskStatuses를 갱신하되 계획을 구현 완료로 표시하지 마라. 필수 실패는 partial/blocked로 남기고 독립 후속 허용 여부와 해결 조건을 구분해라. 소유 변경만 staged diff 확인 후 로컬 커밋하고 해시·제외·잔여 WIP·다음 ID/담당/붙여 넣을 프롬프트를 남겨라. 혼합 WIP는 전체 stage하지 말고 소유 hunk 또는 재현 가능한 상태 delta를 기록해라. 자동 다음 task·push·배포·진단·치료·침 시뮬레이션 금지.
명세 work/tasks/T67.md, 선행 T65 + evaluation start request.
신경 파일럿 후 평가 착수가 필요할 때 주요 근육/기능 최대6개와 평가 후보를 교육 가치·빈도·3D표현 난도로 우선순위화한다. 근육마다 평가법 하나를 억지 배정하지 않는다. 정형외과 special test/신경 검사/근력 검사 목적을 구분하고 첫 animation은 검사1개만 고른다.


다음 기본 ID T36. 자동 실행하지 마라.
```

### T36 — 주요 평가 시범에 한정한 계약 (Sol High)

```text
주요 평가 착수(또는 T68 경혈 후속 설계)를 명시적으로 요청한다. HUMAN ATLAS에서 T36만 수행해라. 담당 Sol High.
AGENTS.md, 00-START-HERE.md, 03-LUNA-SERIAL-RUNBOOK.md, R15 13/14/15 설계와 16-ASTRA-UI-HANDOFF.md, 17-VISUAL-COVERAGE-REPAIR.md, 18-SERIAL-PROMPTS-AFTER-T58.md, work/STATUS.md와 work/task-registry-r15.json을 읽어라. 상대 설계 파일은 design/2026-09-25-muscle-atlas/ 아래에 있다. 실행할 task 명세와 선행 실제 보고서·manifest·evidence를 확인하고 정확히 요청된 ID만 수행해라. 시작 HEAD/status/hash를 기록하고 기존 코드/원본/OpenSim_Models/사용자 WIP/역사 freeze를 보존해라. 소유 코드·데이터·보고서·검증만 수정하고 최소 필수 검증과 필요한 실제 화면을 확인해라. 기본 숨김·선택 제한·source-only·license/human-review hold는 명세의 명시적 개별 변경 근거 없이 승격하지 마라. 로딩의 로고·인체 그림·슬로건을 복구하지 말고 단일 장면·카메라·최종 미니멀 UI를 유지해라. task별 report/evidence/STATUS/taskStatuses를 갱신하되 계획을 구현 완료로 표시하지 마라. 필수 실패는 partial/blocked로 남기고 독립 후속 허용 여부와 해결 조건을 구분해라. 소유 변경만 staged diff 확인 후 로컬 커밋하고 해시·제외·잔여 WIP·다음 ID/담당/붙여 넣을 프롬프트를 남겨라. 혼합 WIP는 전체 stage하지 말고 소유 hunk 또는 재현 가능한 상태 delta를 기록해라. 자동 다음 task·push·배포·진단·치료·침 시뮬레이션 금지.
명세 work/tasks/T36.md, 선행 T67.
보류된 미래 단계다. 구조·기능 단계 종료 후 사용자가 평가 착수를 요청한 경우에만 실행한다. 검사명을 선택하고 근육과 검사 관계, 검사 목적/관찰/한계, 검사자·피검사자, 자세/고정 손/저항 손/접촉/방향/단계 계약을 정의한다.

AssessmentDefinition/AssessmentScene/AssessmentStep와 공통 시간축을 MotionDefinition과 분리한다. 기존 근육 작용 clip을 검사 수행 영상으로 그대로 쓰지 않는다. 환자 입력·자동 진단·치료 추천은 없다.

T67이 선정한 주요 근육/기능 목록과 첫 검사1개만 위한 두 actor/단계/관찰 계약을 만든다. 전신 모든 근육 검사 schema 콘텐츠를 채우지 않는다. 구조·기능·신경 scene core를 재사용하고 환자 자동 판정은 만들지 않는다.
다음 기본 ID T37. 자동 실행하지 마라.
```

### T37 — 주요 근육의 첫 검사 하나만 정리 (Luna Max)

```text
주요 평가 착수(또는 T68 경혈 후속 설계)를 명시적으로 요청한다. HUMAN ATLAS에서 T37만 수행해라. 담당 Luna Max.
AGENTS.md, 00-START-HERE.md, 03-LUNA-SERIAL-RUNBOOK.md, R15 13/14/15 설계와 16-ASTRA-UI-HANDOFF.md, 17-VISUAL-COVERAGE-REPAIR.md, 18-SERIAL-PROMPTS-AFTER-T58.md, work/STATUS.md와 work/task-registry-r15.json을 읽어라. 상대 설계 파일은 design/2026-09-25-muscle-atlas/ 아래에 있다. 실행할 task 명세와 선행 실제 보고서·manifest·evidence를 확인하고 정확히 요청된 ID만 수행해라. 시작 HEAD/status/hash를 기록하고 기존 코드/원본/OpenSim_Models/사용자 WIP/역사 freeze를 보존해라. 소유 코드·데이터·보고서·검증만 수정하고 최소 필수 검증과 필요한 실제 화면을 확인해라. 기본 숨김·선택 제한·source-only·license/human-review hold는 명세의 명시적 개별 변경 근거 없이 승격하지 마라. 로딩의 로고·인체 그림·슬로건을 복구하지 말고 단일 장면·카메라·최종 미니멀 UI를 유지해라. task별 report/evidence/STATUS/taskStatuses를 갱신하되 계획을 구현 완료로 표시하지 마라. 필수 실패는 partial/blocked로 남기고 독립 후속 허용 여부와 해결 조건을 구분해라. 소유 변경만 staged diff 확인 후 로컬 커밋하고 해시·제외·잔여 WIP·다음 ID/담당/붙여 넣을 프롬프트를 남겨라. 혼합 WIP는 전체 stage하지 말고 소유 hunk 또는 재현 가능한 상태 delta를 기록해라. 자동 다음 task·push·배포·진단·치료·침 시뮬레이션 금지.
명세 work/tasks/T37.md, 선행 T36.
T36 후 한 가지 근육 기능 검사만 고른다. 목적·대상·초기 자세·고정/저항 위치·지시·관찰·보상동작·해석 한계의 직접 원문을 대조한다. 근력검사와 통증유발/신경 검사 등 목적이 다른 검사를 혼동하지 않는다.

3개 문헌 읽기 수를 합격 기준으로 삼지 않고 한 검사를 애니메이션으로 제작 가능한 단계표·카메라/손 위치 storyboard로 완성한다. 모호한 절차는 대충 그리지 않는다.

T67에서 고른 검사 한 개를 원문 대조해 검사자/피검사자의 자세·손 위치·고정·저항 방향·관찰/한계 storyboard로 만든다. 모든 근육 평가나 서로 다른 검사들을 한 batch에 넣지 않는다. 후속 주요 검사도 한 검사 또는 작은 묶음씩 배정한다.
다음 기본 ID T48. 자동 실행하지 마라.
```

### T48 — 검사자·피검사자 2인 애니메이션 기반 (Sol High)

```text
주요 평가 착수(또는 T68 경혈 후속 설계)를 명시적으로 요청한다. HUMAN ATLAS에서 T48만 수행해라. 담당 Sol High.
AGENTS.md, 00-START-HERE.md, 03-LUNA-SERIAL-RUNBOOK.md, R15 13/14/15 설계와 16-ASTRA-UI-HANDOFF.md, 17-VISUAL-COVERAGE-REPAIR.md, 18-SERIAL-PROMPTS-AFTER-T58.md, work/STATUS.md와 work/task-registry-r15.json을 읽어라. 상대 설계 파일은 design/2026-09-25-muscle-atlas/ 아래에 있다. 실행할 task 명세와 선행 실제 보고서·manifest·evidence를 확인하고 정확히 요청된 ID만 수행해라. 시작 HEAD/status/hash를 기록하고 기존 코드/원본/OpenSim_Models/사용자 WIP/역사 freeze를 보존해라. 소유 코드·데이터·보고서·검증만 수정하고 최소 필수 검증과 필요한 실제 화면을 확인해라. 기본 숨김·선택 제한·source-only·license/human-review hold는 명세의 명시적 개별 변경 근거 없이 승격하지 마라. 로딩의 로고·인체 그림·슬로건을 복구하지 말고 단일 장면·카메라·최종 미니멀 UI를 유지해라. task별 report/evidence/STATUS/taskStatuses를 갱신하되 계획을 구현 완료로 표시하지 마라. 필수 실패는 partial/blocked로 남기고 독립 후속 허용 여부와 해결 조건을 구분해라. 소유 변경만 staged diff 확인 후 로컬 커밋하고 해시·제외·잔여 WIP·다음 ID/담당/붙여 넣을 프롬프트를 남겨라. 혼합 WIP는 전체 stage하지 말고 소유 hunk 또는 재현 가능한 상태 delta를 기록해라. 자동 다음 task·push·배포·진단·치료·침 시뮬레이션 금지.
명세 work/tasks/T48.md, 선행 T37.
T36/T37 후 라이선스가 확인된 중립 인체 mannequin 두 개와 검사대/의자를 구성한다. 필요한 손가락/팔/다리 rig, actor namespace, 단일 시간축, 손-신체 접촉 anchor와 자세 전환을 구현한다.

첫 버전은 사전 제작한 동기화 clip을 사용한다. 자유 물리/임의 신체크기 대응/실시간 IK는 별도 요구가 생길 때만 확장한다. 이 기반의 synthetic pose는 실제 검사 교육 자료로 공개하지 않는다.

기존 세부 수행 범위는 유지하되 R15 동일 전신 scene/근육 표면 변형/명확한 CTA/신경 우선 순서를 적용한다. 이전 별도 시범 모델 허용은 폐기하며 아래 이전 next/prerequisite 문구는 R15 queue로 대체한다.
다음 기본 ID T49. 자동 실행하지 마라.
```

### T49 — 첫 기능검사 2인 교육용 시범 제작 (Sol High)

```text
주요 평가 착수(또는 T68 경혈 후속 설계)를 명시적으로 요청한다. HUMAN ATLAS에서 T49만 수행해라. 담당 Sol High.
AGENTS.md, 00-START-HERE.md, 03-LUNA-SERIAL-RUNBOOK.md, R15 13/14/15 설계와 16-ASTRA-UI-HANDOFF.md, 17-VISUAL-COVERAGE-REPAIR.md, 18-SERIAL-PROMPTS-AFTER-T58.md, work/STATUS.md와 work/task-registry-r15.json을 읽어라. 상대 설계 파일은 design/2026-09-25-muscle-atlas/ 아래에 있다. 실행할 task 명세와 선행 실제 보고서·manifest·evidence를 확인하고 정확히 요청된 ID만 수행해라. 시작 HEAD/status/hash를 기록하고 기존 코드/원본/OpenSim_Models/사용자 WIP/역사 freeze를 보존해라. 소유 코드·데이터·보고서·검증만 수정하고 최소 필수 검증과 필요한 실제 화면을 확인해라. 기본 숨김·선택 제한·source-only·license/human-review hold는 명세의 명시적 개별 변경 근거 없이 승격하지 마라. 로딩의 로고·인체 그림·슬로건을 복구하지 말고 단일 장면·카메라·최종 미니멀 UI를 유지해라. task별 report/evidence/STATUS/taskStatuses를 갱신하되 계획을 구현 완료로 표시하지 마라. 필수 실패는 partial/blocked로 남기고 독립 후속 허용 여부와 해결 조건을 구분해라. 소유 변경만 staged diff 확인 후 로컬 커밋하고 해시·제외·잔여 WIP·다음 ID/담당/붙여 넣을 프롬프트를 남겨라. 혼합 WIP는 전체 stage하지 말고 소유 hunk 또는 재현 가능한 상태 delta를 기록해라. 자동 다음 task·push·배포·진단·치료·침 시뮬레이션 금지.
명세 work/tasks/T49.md, 선행 T48.
T37 단계표와 T48 두 인물 기반으로 실제 검사 한 개를 제작한다. 준비→자세→손 고정/접촉→지시/저항 방향→관찰→복원 단계별 clip과 카메라를 연결한다. 단계 이동/재생/느리게/손 위치 확대를 제공할 입력을 만든다.

접촉·겹침·비의도 관절 움직임과 설명 불일치를 처음/중간/끝 및 단계 경계에서 검사한다. 힘 크기를 애니메이션만으로 정량 측정한다고 표현하지 않는다.

기존 세부 수행 범위는 유지하되 R15 동일 전신 scene/근육 표면 변형/명확한 CTA/신경 우선 순서를 적용한다. 이전 별도 시범 모델 허용은 폐기하며 아래 이전 next/prerequisite 문구는 R15 queue로 대체한다.
다음 기본 ID T38. 자동 실행하지 마라.
```

### T38 — 평가 단계 UI와 검사 시범 통합 (Luna Max)

```text
주요 평가 착수(또는 T68 경혈 후속 설계)를 명시적으로 요청한다. HUMAN ATLAS에서 T38만 수행해라. 담당 Luna Max.
AGENTS.md, 00-START-HERE.md, 03-LUNA-SERIAL-RUNBOOK.md, R15 13/14/15 설계와 16-ASTRA-UI-HANDOFF.md, 17-VISUAL-COVERAGE-REPAIR.md, 18-SERIAL-PROMPTS-AFTER-T58.md, work/STATUS.md와 work/task-registry-r15.json을 읽어라. 상대 설계 파일은 design/2026-09-25-muscle-atlas/ 아래에 있다. 실행할 task 명세와 선행 실제 보고서·manifest·evidence를 확인하고 정확히 요청된 ID만 수행해라. 시작 HEAD/status/hash를 기록하고 기존 코드/원본/OpenSim_Models/사용자 WIP/역사 freeze를 보존해라. 소유 코드·데이터·보고서·검증만 수정하고 최소 필수 검증과 필요한 실제 화면을 확인해라. 기본 숨김·선택 제한·source-only·license/human-review hold는 명세의 명시적 개별 변경 근거 없이 승격하지 마라. 로딩의 로고·인체 그림·슬로건을 복구하지 말고 단일 장면·카메라·최종 미니멀 UI를 유지해라. task별 report/evidence/STATUS/taskStatuses를 갱신하되 계획을 구현 완료로 표시하지 마라. 필수 실패는 partial/blocked로 남기고 독립 후속 허용 여부와 해결 조건을 구분해라. 소유 변경만 staged diff 확인 후 로컬 커밋하고 해시·제외·잔여 WIP·다음 ID/담당/붙여 넣을 프롬프트를 남겨라. 혼합 WIP는 전체 stage하지 말고 소유 hunk 또는 재현 가능한 상태 delta를 기록해라. 자동 다음 task·push·배포·진단·치료·침 시뮬레이션 금지.
명세 work/tasks/T38.md, 선행 T49.
T49와 평가 착수 요청이 충족된 후에만 평가 탭을 노출한다. 검사 선택→목적→두 인물 준비 자세→단계별 시범→관찰과 한계로 연결한다. 명칭은 검사자/피검사자를 사용하고 자동 진단·시술/치료 흐름은 만들지 않는다.

기존 세부 수행 범위는 유지하되 R15 동일 전신 scene/근육 표면 변형/명확한 CTA/신경 우선 순서를 적용한다. 이전 별도 시범 모델 허용은 폐기하며 아래 이전 next/prerequisite 문구는 R15 queue로 대체한다.
다음 기본 ID 없음. 자동 실행하지 마라.
```

### T68 — 경혈·경락 영역 및 중재 지식의 후속 설계 (Sol High)

```text
주요 평가 착수(또는 T68 경혈 후속 설계)를 명시적으로 요청한다. HUMAN ATLAS에서 T68만 수행해라. 담당 Sol High.
AGENTS.md, 00-START-HERE.md, 03-LUNA-SERIAL-RUNBOOK.md, R15 13/14/15 설계와 16-ASTRA-UI-HANDOFF.md, 17-VISUAL-COVERAGE-REPAIR.md, 18-SERIAL-PROMPTS-AFTER-T58.md, work/STATUS.md와 work/task-registry-r15.json을 읽어라. 상대 설계 파일은 design/2026-09-25-muscle-atlas/ 아래에 있다. 실행할 task 명세와 선행 실제 보고서·manifest·evidence를 확인하고 정확히 요청된 ID만 수행해라. 시작 HEAD/status/hash를 기록하고 기존 코드/원본/OpenSim_Models/사용자 WIP/역사 freeze를 보존해라. 소유 코드·데이터·보고서·검증만 수정하고 최소 필수 검증과 필요한 실제 화면을 확인해라. 기본 숨김·선택 제한·source-only·license/human-review hold는 명세의 명시적 개별 변경 근거 없이 승격하지 마라. 로딩의 로고·인체 그림·슬로건을 복구하지 말고 단일 장면·카메라·최종 미니멀 UI를 유지해라. task별 report/evidence/STATUS/taskStatuses를 갱신하되 계획을 구현 완료로 표시하지 마라. 필수 실패는 partial/blocked로 남기고 독립 후속 허용 여부와 해결 조건을 구분해라. 소유 변경만 staged diff 확인 후 로컬 커밋하고 해시·제외·잔여 WIP·다음 ID/담당/붙여 넣을 프롬프트를 남겨라. 혼합 WIP는 전체 stage하지 말고 소유 hunk 또는 재현 가능한 상태 delta를 기록해라. 자동 다음 task·push·배포·진단·치료·침 시뮬레이션 금지.
명세 work/tasks/T68.md, 선행 separate user request.
현재는 보류다. 사용자가 별도로 설계를 시작하라고 하면 표면 landmark/비례 기준/자세/좌우/경혈 점/전통 경락 선/영역의 출처·판본·표현 계약을 만든다. 신경·감각 영역·피부분절과 별도 layer/관계로 둔다. 담경/위경 영역을 경계가 확정된 신경 해부학 면으로 표시하지 않는다. 치료 지식은 별도 evidence-backed module 설계로 제한한다.


다음 기본 ID 없음. 자동 실행하지 마라.
```
