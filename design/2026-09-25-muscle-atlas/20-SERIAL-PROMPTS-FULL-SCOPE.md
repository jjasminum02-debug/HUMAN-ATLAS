> **현행 효율화 개정:** 22-EFFICIENT-DELIVERY-AND-PERFORMANCE.md와 work/evidence/2026-09-28-efficient-plan/의 queue/프롬프트 우선. T96을 앞당기고 T110–121은12부위 package, T122–165는 superseded_not_executed다.10개당 새 task 발급은 폐기, 검증 단위로만 유지. T78의 실제 결과/미완은 바뀌지 않는다. 다음 T95 → T96.

> **2026-09-28 T78 개정:** 현재 다음은 T95(Luna Max). 21-WHOLE-BODY-ACQUISITION-T78.md와 work/evidence/T78/PROMPTS-IN-ORDER.md / execution-queue.json을 우선한다. 부위 복수 선택·견갑골 수정 → 실제 누락 표면 취득·광배근 객체/권리/정합/통합 → 전체 target 의미/선택 연결 → T80/T58. 아래 T79→T80 직행 및 취득과 전체 콘텐츠 동시 완료 문구는 새 queue로 대체한다. T78 target 의미 분모는 아직 partial이며 개별근 분모 null, 원래 후반 기시정지→작용→모션→신경 순서는 유지한다.

# T77 이후 새 순서·실행 프롬프트

2026-09-28 · 계획. T73–76은 18 문서 그대로. 아래는 한 task씩 실행한다. 첫 batch 뒤의 전신 잔여 batch는 동적 발급하여 해당 global gate 앞에 넣는다. **모든 근육 기능/움직임 합격 전 신경 착수 금지.**

| 순서 | ID | 담당 | 범위 |
|---|---|---|---|
| 1 | T77 | Astra · 현재 대화 직접 구현 | 기본 전신 장면 통합과 보완자산 UI 제거 |
| 2 | T78 | Astra · 현재 대화 직접 구현 | 전신 근육·뼈 목표 분모와 실제 확장 queue |
| 3 | T79 | Luna Max | 첫 전신 구조 보완·선택 연결 batch |
| 4 | T80 | Luna Max | 전신 구조·선택 coverage 감사 |
| 5 | T58 | Astra · 현재 대화 직접 구현 | 전신 그래픽 재검증 |
| 6 | T81 | Luna Max | 첫 전신 기시·정지 조사 batch |
| 7 | T82 | Luna Max | 전신 기시·정지 프로토타입 합격 |
| 8 | T83 | Luna Max | 첫 전신 근육 기능 조사 batch |
| 9 | T84 | Luna Max | 전신 근육 기능 설명 합격 |
| 10 | T35 | Sol High | 전신 근육 animation 목표와 제작 queue |
| 11 | T59 | Sol High | 같은 앞정강근 표면의 교육용 수축 변형 |
| 12 | T60 | Sol High | 동일 viewport에서 운동 재생 연결 |
| 13 | T25 | Luna Max | 같은 전신 모형의 앞정강근 제품 합격 |
| 14 | T27 | Sol High | 소흉근 동일 모형 변형 준비 |
| 15 | T28 | Sol High | 견갑대 운동 기반과 전인 시범 하나 |
| 16 | T45 | Sol High | 소흉근 관련 견갑골 하강 시범 |
| 17 | T46 | Sol High | 소흉근 관련 견갑골 하방회전 시범 |
| 18 | T29 | Luna Max | 소흉근 구조·기능 사용자 흐름 통합 |
| 19 | T31 | Luna Max | 두 부위 구조·기능 파일럿 합격 검증 |
| 20 | T66 | Luna Max | 첫 기능 확장 batch 하나 |
| 21 | T47 | Luna Max | 전신 구조·기능·운동 자료 감사 |
| 22 | T85 | Astra · 현재 대화 직접 구현 | 모든 근육 움직임 학습 coverage 합격 |
| 23 | T61 | Sol High | 신경 레이어·선택·관계 데이터 계약 |
| 24 | T86 | Sol High | 전신 신경 목표·복수 원문 모델 조사 |
| 25 | T62 | Luna Max | 첫 하지 신경 자료 패키지 |
| 26 | T87 | Luna Max | 전신 신경 조사 확장 첫 batch |
| 27 | T88 | Sol High | 전신 신경 자료 통합·등록 검증 |
| 28 | T63 | Sol High | 첫 신경 3D 주행과 지배근 강조 |
| 29 | T89 | Luna Max | 전신 신경 3D 확장 첫 batch |
| 30 | T90 | Astra · 현재 대화 직접 구현 | 전신 신경 주행·지배근 그래픽 합격 |
| 31 | T64 | Luna Max | 신경 포착·기능 변화의 접힌 설명 UI |
| 32 | T91 | Luna Max | 신경 포착·기능이상 설명 확장 첫 batch |
| 33 | T65 | Luna Max | 전신 근육·신경·기능이상 설명 최종 통합 검증 |
| 34 | T40 | Luna Max | 구조·기능 로컬 전달과 Git 체크포인트 |

## T77 — 기본 전신 장면 통합과 보완자산 UI 제거

```text
HUMAN ATLAS에서 T77만 수행해라. 담당 Astra · 현재 대화 직접 구현.
AGENTS.md와 R15 13/14/15, 16-ASTRA-UI-HANDOFF.md, 최신 19-ALL-MUSCLES-BEFORE-NERVES.md 및 20-SERIAL-PROMPTS-FULL-SCOPE.md(설계 폴더 design/2026-09-25-muscle-atlas/), STATUS/R15 registry, 해당 task 명세와 선행 실제 report/manifest/evidence를 읽어라. 19/20의 T77 이후 순서가 이전 프롬프트보다 우선한다. 정확히 요청된 ID만 수행하고 자동 다음 실행은 하지 마라. 시작 HEAD/status/source hash를 기록하고 기존 WIP·원본/OpenSim_Models·역사 freeze를 보존해라. 실제 source/근거 없이 이름·좌표·형상·승인을 만들지 마라. AI가 조사/대조/표 작성을 수행하며 사용자에게 기본 해부학 조사 숙제를 넘기지 마라. source provenance와 license/human-review는 내부에 보존하고 learner에 JSON/task/보완자산 구분을 노출하지 마라. 로딩의 로고·인체 그림·슬로건을 복구하지 말고 단일 scene/camera와 미니멀 UI를 유지해라. 모든 target coverage gate는 동결한 전체 분모로 판정하고 필수 누락을 passed_with_gaps로 덮지 마라. 실제 의존 gate가 미달이면 해당 후속 단계를 시작하지 말고 bounded 수정 task와 해소 조건을 남겨라. 범위에 맞는 검사·실제 화면 검증과 report/evidence/STATUS/taskStatuses를 남겨라. 소유 변경만 staged diff 확인 후 로컬 커밋하며 혼합 WIP는 소유 hunk 또는 상태 delta만 포함해라. 해시·제외·잔여 WIP·다음 ID/담당/프롬프트를 남기고 멈춰라. push·배포·환자 자동진단·치료·자침 추천/시뮬레이션은 금지한다.
명세 work/tasks/T77.md. 선행: T73–76 실제 산출물.
기존 T77 통합 계약을 유지하되 learner의 보완 모형 보기 및 보완자산 구분을 제거한다. 취득 경로는 내부 provenance이며 학생용 layer가 아니다. 요추 L1–L5/엉치뼈와 모든 로컬 표시 적격 뼈·근육은 기본 scene에서 함께 보이도록 새 manifest 정책을 만든다. 기존 supplement 20개를 출신만으로 숨기지 않되 identity/좌우/frame/local rights 보류는 임의 해제하지 않는다. 항목별 표시 근거와 before/after를 기록하고 source-only는 binding 승격 없이 맥락 모형으로 보인다. 이두근·삼두근 10개 source 후보 및 다른 주요 근육의 missing/hidden/occluded/unbound 원인을 전체 inventory에서 확인한다. 새 geometry 누락은 T78–79 보완 queue에 연결하며 이번 통합을 전신 완성으로 부르지 않는다. 하나의 root/renderer/camera, 기존 미니멀 로딩, 12부위와 보기 옵션의 선택만 보기/맞춤은 유지한다. 사용자 layer-off나 깊이 가림을 asset 부재와 구분한다.
다음 기본 ID는 T78. 단, 미완 batch가 있으면 새 정수 ID의 실제 queue를 따른다. 다음 task는 실행하지 마라.
```

## T78 — 전신 근육·뼈 목표 분모와 실제 확장 queue

```text
HUMAN ATLAS에서 T78만 수행해라. 담당 Astra · 현재 대화 직접 구현.
AGENTS.md와 R15 13/14/15, 16-ASTRA-UI-HANDOFF.md, 최신 19-ALL-MUSCLES-BEFORE-NERVES.md 및 20-SERIAL-PROMPTS-FULL-SCOPE.md(설계 폴더 design/2026-09-25-muscle-atlas/), STATUS/R15 registry, 해당 task 명세와 선행 실제 report/manifest/evidence를 읽어라. 19/20의 T77 이후 순서가 이전 프롬프트보다 우선한다. 정확히 요청된 ID만 수행하고 자동 다음 실행은 하지 마라. 시작 HEAD/status/source hash를 기록하고 기존 WIP·원본/OpenSim_Models·역사 freeze를 보존해라. 실제 source/근거 없이 이름·좌표·형상·승인을 만들지 마라. AI가 조사/대조/표 작성을 수행하며 사용자에게 기본 해부학 조사 숙제를 넘기지 마라. source provenance와 license/human-review는 내부에 보존하고 learner에 JSON/task/보완자산 구분을 노출하지 마라. 로딩의 로고·인체 그림·슬로건을 복구하지 말고 단일 scene/camera와 미니멀 UI를 유지해라. 모든 target coverage gate는 동결한 전체 분모로 판정하고 필수 누락을 passed_with_gaps로 덮지 마라. 실제 의존 gate가 미달이면 해당 후속 단계를 시작하지 말고 bounded 수정 task와 해소 조건을 남겨라. 범위에 맞는 검사·실제 화면 검증과 report/evidence/STATUS/taskStatuses를 남겨라. 소유 변경만 staged diff 확인 후 로컬 커밋하며 혼합 WIP는 소유 hunk 또는 상태 delta만 포함해라. 해시·제외·잔여 WIP·다음 ID/담당/프롬프트를 남기고 멈춰라. push·배포·환자 자동진단·치료·자침 추천/시뮬레이션은 금지한다.
명세 work/tasks/T78.md. 선행: T77 실제 결과 및 T73 inventory.
주요10개 연결 파일럿이라는 이전 범위를 전신 구조 target inventory와 bounded 실행 queue 설계로 교체한다. 사용자 12부위의 골격근과 맥락 뼈를 정의하고 개별근/갈래/근육군/양측/중선/변이를 분리한다. 작은 머리·손·발·골반 근육을 누락해 분모를 줄이지 않는다. 기존 catalog와 공식 source tree, 독립 해부학 목록을 대조하여 concept 단위 분모와 source ELEMENT 분모를 동결한다. source 미제공 항목도 target에서 삭제하지 않는다. 각 target에 geometry/side/frame/region/binding/세 이름/기시정지/기능/animation의 독립 상태를 둔다. 이두근·삼두근과 나머지 부위별 누락·미연결을 exact IDs로 배정한다. T79 첫 batch 최대10개 개념을 동결하고 나머지 모든 구조 batch도 미사용 정수 ID로 task 명세와 프롬프트를 발급하여 T80 앞에 삽입한다. 자료 대안은 실제 조사하고 다른 model 혼합은 별도 registration task로 분리한다. 사용자가 수동으로 근육 목록/출처를 채울 필요가 없다.
다음 기본 ID는 T79. 단, 미완 batch가 있으면 새 정수 ID의 실제 queue를 따른다. 다음 task는 실행하지 마라.
```

## T79 — 첫 전신 구조 보완·선택 연결 batch

```text
HUMAN ATLAS에서 T79만 수행해라. 담당 Luna Max.
AGENTS.md와 R15 13/14/15, 16-ASTRA-UI-HANDOFF.md, 최신 19-ALL-MUSCLES-BEFORE-NERVES.md 및 20-SERIAL-PROMPTS-FULL-SCOPE.md(설계 폴더 design/2026-09-25-muscle-atlas/), STATUS/R15 registry, 해당 task 명세와 선행 실제 report/manifest/evidence를 읽어라. 19/20의 T77 이후 순서가 이전 프롬프트보다 우선한다. 정확히 요청된 ID만 수행하고 자동 다음 실행은 하지 마라. 시작 HEAD/status/source hash를 기록하고 기존 WIP·원본/OpenSim_Models·역사 freeze를 보존해라. 실제 source/근거 없이 이름·좌표·형상·승인을 만들지 마라. AI가 조사/대조/표 작성을 수행하며 사용자에게 기본 해부학 조사 숙제를 넘기지 마라. source provenance와 license/human-review는 내부에 보존하고 learner에 JSON/task/보완자산 구분을 노출하지 마라. 로딩의 로고·인체 그림·슬로건을 복구하지 말고 단일 scene/camera와 미니멀 UI를 유지해라. 모든 target coverage gate는 동결한 전체 분모로 판정하고 필수 누락을 passed_with_gaps로 덮지 마라. 실제 의존 gate가 미달이면 해당 후속 단계를 시작하지 말고 bounded 수정 task와 해소 조건을 남겨라. 범위에 맞는 검사·실제 화면 검증과 report/evidence/STATUS/taskStatuses를 남겨라. 소유 변경만 staged diff 확인 후 로컬 커밋하며 혼합 WIP는 소유 hunk 또는 상태 delta만 포함해라. 해시·제외·잔여 WIP·다음 ID/담당/프롬프트를 남기고 멈춰라. push·배포·환자 자동진단·치료·자침 추천/시뮬레이션은 금지한다.
명세 work/tasks/T79.md. 선행: T78 동결 batch.
동결한 최대10개 개념의 실제 geometry 취득/검증/변환/scene extension 및 source→canonical mapping/세 이름을 완성한다. 기존 도구/cache를 재사용하고 source member는 내부5–10개 단위로 처리한다. 이두근/삼두근 양측 갈래가 우선 후보이며 정확한 batch는 T78이 정한다. 미확보·held에는 가짜 모형이나 이름 연결을 만들지 않는다. 기본 표시 적격 구조는 같은 learner scene에, source-only와 기존 hold는 근거 없이 선택으로 승격하지 않는다. old freeze 불변, 새 revision을 검증한다. 세 이름 검색/클릭/깊은 구조 접근 및 실제 브라우저를 확인한다. 다음은 T78이 발급한 다음 구조 batch이며 전부 마친 뒤 T80이다.
다음 기본 ID는 T80. 단, 미완 batch가 있으면 새 정수 ID의 실제 queue를 따른다. 다음 task는 실행하지 마라.
```

## T80 — 전신 구조·선택 coverage 감사

```text
HUMAN ATLAS에서 T80만 수행해라. 담당 Luna Max.
AGENTS.md와 R15 13/14/15, 16-ASTRA-UI-HANDOFF.md, 최신 19-ALL-MUSCLES-BEFORE-NERVES.md 및 20-SERIAL-PROMPTS-FULL-SCOPE.md(설계 폴더 design/2026-09-25-muscle-atlas/), STATUS/R15 registry, 해당 task 명세와 선행 실제 report/manifest/evidence를 읽어라. 19/20의 T77 이후 순서가 이전 프롬프트보다 우선한다. 정확히 요청된 ID만 수행하고 자동 다음 실행은 하지 마라. 시작 HEAD/status/source hash를 기록하고 기존 WIP·원본/OpenSim_Models·역사 freeze를 보존해라. 실제 source/근거 없이 이름·좌표·형상·승인을 만들지 마라. AI가 조사/대조/표 작성을 수행하며 사용자에게 기본 해부학 조사 숙제를 넘기지 마라. source provenance와 license/human-review는 내부에 보존하고 learner에 JSON/task/보완자산 구분을 노출하지 마라. 로딩의 로고·인체 그림·슬로건을 복구하지 말고 단일 scene/camera와 미니멀 UI를 유지해라. 모든 target coverage gate는 동결한 전체 분모로 판정하고 필수 누락을 passed_with_gaps로 덮지 마라. 실제 의존 gate가 미달이면 해당 후속 단계를 시작하지 말고 bounded 수정 task와 해소 조건을 남겨라. 범위에 맞는 검사·실제 화면 검증과 report/evidence/STATUS/taskStatuses를 남겨라. 소유 변경만 staged diff 확인 후 로컬 커밋하며 혼합 WIP는 소유 hunk 또는 상태 delta만 포함해라. 해시·제외·잔여 WIP·다음 ID/담당/프롬프트를 남기고 멈춰라. push·배포·환자 자동진단·치료·자침 추천/시뮬레이션은 금지한다.
명세 work/tasks/T80.md. 선행: T79 및 모든 구조 batch.
T78의 전체 target을 exact source/node/side/binding/세 이름/부위로 대조한다. 모든 target의 표시 가능성과 클릭 설명 연결, 깊은 구조의 격리/회전 접근, 요추·엉치뼈 기본 표시를 확인한다. 모든 근육을 같은 시점에 투명하게 겹쳐 보여야 한다는 뜻은 아니다. 누락/미연결/미해결 필수 hold가 남으면 partial이며 기시정지 전신 완료 단계로 넘어가지 않는다. 추가 수정 task를 exact 대상/종료조건으로 배정한다. 분모를 줄이거나 subset 100%를 전신 완료로 쓰지 않는다. 통과 후 Astra T58 실제 그래픽 재검증.
다음 기본 ID는 T58. 단, 미완 batch가 있으면 새 정수 ID의 실제 queue를 따른다. 다음 task는 실행하지 마라.
```

## T58 — 전신 그래픽 재검증

```text
HUMAN ATLAS에서 T58 재검증만 수행해라. 담당 Astra · 현재 대화 직접 구현.
AGENTS.md와 R15 13/14/15, 16-ASTRA-UI-HANDOFF.md, 최신 19-ALL-MUSCLES-BEFORE-NERVES.md 및 20-SERIAL-PROMPTS-FULL-SCOPE.md(설계 폴더 design/2026-09-25-muscle-atlas/), STATUS/R15 registry, 해당 task 명세와 선행 실제 report/manifest/evidence를 읽어라. 19/20의 T77 이후 순서가 이전 프롬프트보다 우선한다. 정확히 요청된 ID만 수행하고 자동 다음 실행은 하지 마라. 시작 HEAD/status/source hash를 기록하고 기존 WIP·원본/OpenSim_Models·역사 freeze를 보존해라. 실제 source/근거 없이 이름·좌표·형상·승인을 만들지 마라. AI가 조사/대조/표 작성을 수행하며 사용자에게 기본 해부학 조사 숙제를 넘기지 마라. source provenance와 license/human-review는 내부에 보존하고 learner에 JSON/task/보완자산 구분을 노출하지 마라. 로딩의 로고·인체 그림·슬로건을 복구하지 말고 단일 scene/camera와 미니멀 UI를 유지해라. 모든 target coverage gate는 동결한 전체 분모로 판정하고 필수 누락을 passed_with_gaps로 덮지 마라. 실제 의존 gate가 미달이면 해당 후속 단계를 시작하지 말고 bounded 수정 task와 해소 조건을 남겨라. 범위에 맞는 검사·실제 화면 검증과 report/evidence/STATUS/taskStatuses를 남겨라. 소유 변경만 staged diff 확인 후 로컬 커밋하며 혼합 WIP는 소유 hunk 또는 상태 delta만 포함해라. 해시·제외·잔여 WIP·다음 ID/담당/프롬프트를 남기고 멈춰라. push·배포·환자 자동진단·치료·자침 추천/시뮬레이션은 금지한다.
명세 work/tasks/T58.md. 선행: T80 pass.
기존 T58 코드와 역사 보고서를 보존하고 전체 동결 구조의 준비 상태를 확인한 뒤 전신/머리/손/종아리 및 새 필수 부위 캡처·단일 scene·camera·패널·390/1024/1440 성능을 재검증한다. 보완자산 UI가 사라지고 요추/엉치뼈 등 맥락 뼈가 기본 표시되는지 확인한다. 실제 필수 누락이 남으면 partial이고 T81로 넘어가지 않는다. 새 재검증 보고서를 남기며 초기 구현을 재작성하지 않는다.
다음 기본 ID는 T81. 단, 미완 batch가 있으면 새 정수 ID의 실제 queue를 따른다. 다음 task는 실행하지 마라.
```

## T81 — 첫 전신 기시·정지 조사 batch

```text
HUMAN ATLAS에서 T81만 수행해라. 담당 Luna Max.
AGENTS.md와 R15 13/14/15, 16-ASTRA-UI-HANDOFF.md, 최신 19-ALL-MUSCLES-BEFORE-NERVES.md 및 20-SERIAL-PROMPTS-FULL-SCOPE.md(설계 폴더 design/2026-09-25-muscle-atlas/), STATUS/R15 registry, 해당 task 명세와 선행 실제 report/manifest/evidence를 읽어라. 19/20의 T77 이후 순서가 이전 프롬프트보다 우선한다. 정확히 요청된 ID만 수행하고 자동 다음 실행은 하지 마라. 시작 HEAD/status/source hash를 기록하고 기존 WIP·원본/OpenSim_Models·역사 freeze를 보존해라. 실제 source/근거 없이 이름·좌표·형상·승인을 만들지 마라. AI가 조사/대조/표 작성을 수행하며 사용자에게 기본 해부학 조사 숙제를 넘기지 마라. source provenance와 license/human-review는 내부에 보존하고 learner에 JSON/task/보완자산 구분을 노출하지 마라. 로딩의 로고·인체 그림·슬로건을 복구하지 말고 단일 scene/camera와 미니멀 UI를 유지해라. 모든 target coverage gate는 동결한 전체 분모로 판정하고 필수 누락을 passed_with_gaps로 덮지 마라. 실제 의존 gate가 미달이면 해당 후속 단계를 시작하지 말고 bounded 수정 task와 해소 조건을 남겨라. 범위에 맞는 검사·실제 화면 검증과 report/evidence/STATUS/taskStatuses를 남겨라. 소유 변경만 staged diff 확인 후 로컬 커밋하며 혼합 WIP는 소유 hunk 또는 상태 delta만 포함해라. 해시·제외·잔여 WIP·다음 ID/담당/프롬프트를 남기고 멈춰라. push·배포·환자 자동진단·치료·자침 추천/시뮬레이션은 금지한다.
명세 work/tasks/T81.md. 선행: T80 및 T58 pass.
T78 전체 근육 target을 대상으로 최대10개 개념의 첫 기시·정지 batch를 실행한다. AI가 해부학 원문/공식 교육 자료를 찾아 교차 검증하고 기존 근거를 재사용한다. 갈래별 차이/비골성 부착/근막·피부·건막과 변이를 구조화하고 충돌은 기록한다. 텍스트 기시정지와 검증된 3D 부착 좌표는 분리하며 좌표를 추정하지 않는다. 모든 batch의 명세와 정수 ID를 T82 앞에 발급하고 첫 batch는 실제 learner 카드에 연결한다. 사용자에게 수동 조사 숙제를 요구하지 않는다. 출처는 내부 evidence/app attribution에 두고 학생 기시정지 칸에는 붙이지 않는다.
다음 기본 ID는 T82. 단, 미완 batch가 있으면 새 정수 ID의 실제 queue를 따른다. 다음 task는 실행하지 마라.
```

## T82 — 전신 기시·정지 프로토타입 합격

```text
HUMAN ATLAS에서 T82만 수행해라. 담당 Luna Max.
AGENTS.md와 R15 13/14/15, 16-ASTRA-UI-HANDOFF.md, 최신 19-ALL-MUSCLES-BEFORE-NERVES.md 및 20-SERIAL-PROMPTS-FULL-SCOPE.md(설계 폴더 design/2026-09-25-muscle-atlas/), STATUS/R15 registry, 해당 task 명세와 선행 실제 report/manifest/evidence를 읽어라. 19/20의 T77 이후 순서가 이전 프롬프트보다 우선한다. 정확히 요청된 ID만 수행하고 자동 다음 실행은 하지 마라. 시작 HEAD/status/source hash를 기록하고 기존 WIP·원본/OpenSim_Models·역사 freeze를 보존해라. 실제 source/근거 없이 이름·좌표·형상·승인을 만들지 마라. AI가 조사/대조/표 작성을 수행하며 사용자에게 기본 해부학 조사 숙제를 넘기지 마라. source provenance와 license/human-review는 내부에 보존하고 learner에 JSON/task/보완자산 구분을 노출하지 마라. 로딩의 로고·인체 그림·슬로건을 복구하지 말고 단일 scene/camera와 미니멀 UI를 유지해라. 모든 target coverage gate는 동결한 전체 분모로 판정하고 필수 누락을 passed_with_gaps로 덮지 마라. 실제 의존 gate가 미달이면 해당 후속 단계를 시작하지 말고 bounded 수정 task와 해소 조건을 남겨라. 범위에 맞는 검사·실제 화면 검증과 report/evidence/STATUS/taskStatuses를 남겨라. 소유 변경만 staged diff 확인 후 로컬 커밋하며 혼합 WIP는 소유 hunk 또는 상태 delta만 포함해라. 해시·제외·잔여 WIP·다음 ID/담당/프롬프트를 남기고 멈춰라. push·배포·환자 자동진단·치료·자침 추천/시뮬레이션은 금지한다.
명세 work/tasks/T82.md. 선행: T81 및 모든 기시정지 batch.
전체 동결 근육의 기시정지/갈래/세 이름/카드 연결과 근거 충돌을 감사한다. 기존 placeholder를 조사 완료로 세지 않는다. 필수 내용 미완은 partial이며 해당 batch를 마무리한 뒤 다음 기능 단계로 간다. 사람 검토는 별도 사실이고 모든 기본 텍스트의 일괄 human approval을 기다리게 하지 않는다. 지식 prototype 완료와 정확한 부착 surface 완성은 구분한다.
다음 기본 ID는 T83. 단, 미완 batch가 있으면 새 정수 ID의 실제 queue를 따른다. 다음 task는 실행하지 마라.
```

## T83 — 첫 전신 근육 기능 조사 batch

```text
HUMAN ATLAS에서 T83만 수행해라. 담당 Luna Max.
AGENTS.md와 R15 13/14/15, 16-ASTRA-UI-HANDOFF.md, 최신 19-ALL-MUSCLES-BEFORE-NERVES.md 및 20-SERIAL-PROMPTS-FULL-SCOPE.md(설계 폴더 design/2026-09-25-muscle-atlas/), STATUS/R15 registry, 해당 task 명세와 선행 실제 report/manifest/evidence를 읽어라. 19/20의 T77 이후 순서가 이전 프롬프트보다 우선한다. 정확히 요청된 ID만 수행하고 자동 다음 실행은 하지 마라. 시작 HEAD/status/source hash를 기록하고 기존 WIP·원본/OpenSim_Models·역사 freeze를 보존해라. 실제 source/근거 없이 이름·좌표·형상·승인을 만들지 마라. AI가 조사/대조/표 작성을 수행하며 사용자에게 기본 해부학 조사 숙제를 넘기지 마라. source provenance와 license/human-review는 내부에 보존하고 learner에 JSON/task/보완자산 구분을 노출하지 마라. 로딩의 로고·인체 그림·슬로건을 복구하지 말고 단일 scene/camera와 미니멀 UI를 유지해라. 모든 target coverage gate는 동결한 전체 분모로 판정하고 필수 누락을 passed_with_gaps로 덮지 마라. 실제 의존 gate가 미달이면 해당 후속 단계를 시작하지 말고 bounded 수정 task와 해소 조건을 남겨라. 범위에 맞는 검사·실제 화면 검증과 report/evidence/STATUS/taskStatuses를 남겨라. 소유 변경만 staged diff 확인 후 로컬 커밋하며 혼합 WIP는 소유 hunk 또는 상태 delta만 포함해라. 해시·제외·잔여 WIP·다음 ID/담당/프롬프트를 남기고 멈춰라. push·배포·환자 자동진단·치료·자침 추천/시뮬레이션은 금지한다.
명세 work/tasks/T83.md. 선행: T82 pass.
최대10개 근육의 첫 기능 batch를 실제 조사/교차 검증하고 카드에 연결한다. T78 전체 target에 대해 나머지 batch 명세/ID를 T84 앞에 발급한다. 작용·움직이는 구조·고정 조건·관절/분절·갈래별 차이·주동/보조 역할을 구분한다. 얼굴/눈/혀/괄약근 등도 관절 회전 모델에 억지로 넣지 않는다. 텍스트 근거와 motion clip 지원 상태를 별도로 저장한다. 모든 근육 기능 연구가 끝나기 전에 clip 제작을 시작하지 않는다.
다음 기본 ID는 T84. 단, 미완 batch가 있으면 새 정수 ID의 실제 queue를 따른다. 다음 task는 실행하지 마라.
```

## T84 — 전신 근육 기능 설명 합격

```text
HUMAN ATLAS에서 T84만 수행해라. 담당 Luna Max.
AGENTS.md와 R15 13/14/15, 16-ASTRA-UI-HANDOFF.md, 최신 19-ALL-MUSCLES-BEFORE-NERVES.md 및 20-SERIAL-PROMPTS-FULL-SCOPE.md(설계 폴더 design/2026-09-25-muscle-atlas/), STATUS/R15 registry, 해당 task 명세와 선행 실제 report/manifest/evidence를 읽어라. 19/20의 T77 이후 순서가 이전 프롬프트보다 우선한다. 정확히 요청된 ID만 수행하고 자동 다음 실행은 하지 마라. 시작 HEAD/status/source hash를 기록하고 기존 WIP·원본/OpenSim_Models·역사 freeze를 보존해라. 실제 source/근거 없이 이름·좌표·형상·승인을 만들지 마라. AI가 조사/대조/표 작성을 수행하며 사용자에게 기본 해부학 조사 숙제를 넘기지 마라. source provenance와 license/human-review는 내부에 보존하고 learner에 JSON/task/보완자산 구분을 노출하지 마라. 로딩의 로고·인체 그림·슬로건을 복구하지 말고 단일 scene/camera와 미니멀 UI를 유지해라. 모든 target coverage gate는 동결한 전체 분모로 판정하고 필수 누락을 passed_with_gaps로 덮지 마라. 실제 의존 gate가 미달이면 해당 후속 단계를 시작하지 말고 bounded 수정 task와 해소 조건을 남겨라. 범위에 맞는 검사·실제 화면 검증과 report/evidence/STATUS/taskStatuses를 남겨라. 소유 변경만 staged diff 확인 후 로컬 커밋하며 혼합 WIP는 소유 hunk 또는 상태 delta만 포함해라. 해시·제외·잔여 WIP·다음 ID/담당/프롬프트를 남기고 멈춰라. push·배포·환자 자동진단·치료·자침 추천/시뮬레이션은 금지한다.
명세 work/tasks/T84.md. 선행: T83 및 모든 기능 batch.
전체 target의 기능 설명과 원문 근거/조건/갈래/기시정지와의 일관성을 대조한다. 누락된 근육이 있으면 부분 완료로 남기고 보완한다. animation이 없다고 기능 텍스트까지 미작성 상태로 두지 않고 설명을 먼저 완성한다. 통과 후 전신 animation 범위/작용군 계획 T35로 간다.
다음 기본 ID는 T35. 단, 미완 batch가 있으면 새 정수 ID의 실제 queue를 따른다. 다음 task는 실행하지 마라.
```

## T35 — 전신 근육 animation 목표와 제작 queue

```text
HUMAN ATLAS에서 T35만 수행해라. 담당 Sol High.
AGENTS.md와 R15 13/14/15, 16-ASTRA-UI-HANDOFF.md, 최신 19-ALL-MUSCLES-BEFORE-NERVES.md 및 20-SERIAL-PROMPTS-FULL-SCOPE.md(설계 폴더 design/2026-09-25-muscle-atlas/), STATUS/R15 registry, 해당 task 명세와 선행 실제 report/manifest/evidence를 읽어라. 19/20의 T77 이후 순서가 이전 프롬프트보다 우선한다. 정확히 요청된 ID만 수행하고 자동 다음 실행은 하지 마라. 시작 HEAD/status/source hash를 기록하고 기존 WIP·원본/OpenSim_Models·역사 freeze를 보존해라. 실제 source/근거 없이 이름·좌표·형상·승인을 만들지 마라. AI가 조사/대조/표 작성을 수행하며 사용자에게 기본 해부학 조사 숙제를 넘기지 마라. source provenance와 license/human-review는 내부에 보존하고 learner에 JSON/task/보완자산 구분을 노출하지 마라. 로딩의 로고·인체 그림·슬로건을 복구하지 말고 단일 scene/camera와 미니멀 UI를 유지해라. 모든 target coverage gate는 동결한 전체 분모로 판정하고 필수 누락을 passed_with_gaps로 덮지 마라. 실제 의존 gate가 미달이면 해당 후속 단계를 시작하지 말고 bounded 수정 task와 해소 조건을 남겨라. 범위에 맞는 검사·실제 화면 검증과 report/evidence/STATUS/taskStatuses를 남겨라. 소유 변경만 staged diff 확인 후 로컬 커밋하며 혼합 WIP는 소유 hunk 또는 상태 delta만 포함해라. 해시·제외·잔여 WIP·다음 ID/담당/프롬프트를 남기고 멈춰라. push·배포·환자 자동진단·치료·자침 추천/시뮬레이션은 금지한다.
명세 work/tasks/T35.md. 선행: T84 pass.
모든 근육이 하나 이상의 자기 기능을 학습할 수 있는 시범을 갖도록 target→근거 있는 작용/고정조건→변형 방식→관련 뼈/주변 구조→clip support를 정의한다. 근육당 대표 시범 최소1개와 추가 작용 미지원 목록을 구분하여 모든 작용 구현이라고 과장하지 않는다. 얼굴/혀/눈/호흡/괄약근 등 비사지 motion family를 누락하지 않는다. 같은 rig를 재사용할 수 있어도 근육별 설명/선택/작용의 검증을 생략하지 않는다. 첫 앞정강근 T59–60/T25와 소흉근 기존 task를 첫 실제 사례로 보존하고 T66 및 나머지 bounded clip/rig 제작 task를 모두 정수 ID로 T47 감사 앞에 배정한다. 계획만 작성, clip 제작 미실행.
다음 기본 ID는 T59. 단, 미완 batch가 있으면 새 정수 ID의 실제 queue를 따른다. 다음 task는 실행하지 마라.
```

## T59 — 같은 앞정강근 표면의 교육용 수축 변형

```text
HUMAN ATLAS에서 T59만 수행해라. 담당 Sol High.
AGENTS.md와 R15 13/14/15, 16-ASTRA-UI-HANDOFF.md, 최신 19-ALL-MUSCLES-BEFORE-NERVES.md 및 20-SERIAL-PROMPTS-FULL-SCOPE.md(설계 폴더 design/2026-09-25-muscle-atlas/), STATUS/R15 registry, 해당 task 명세와 선행 실제 report/manifest/evidence를 읽어라. 19/20의 T77 이후 순서가 이전 프롬프트보다 우선한다. 정확히 요청된 ID만 수행하고 자동 다음 실행은 하지 마라. 시작 HEAD/status/source hash를 기록하고 기존 WIP·원본/OpenSim_Models·역사 freeze를 보존해라. 실제 source/근거 없이 이름·좌표·형상·승인을 만들지 마라. AI가 조사/대조/표 작성을 수행하며 사용자에게 기본 해부학 조사 숙제를 넘기지 마라. source provenance와 license/human-review는 내부에 보존하고 learner에 JSON/task/보완자산 구분을 노출하지 마라. 로딩의 로고·인체 그림·슬로건을 복구하지 말고 단일 scene/camera와 미니멀 UI를 유지해라. 모든 target coverage gate는 동결한 전체 분모로 판정하고 필수 누락을 passed_with_gaps로 덮지 마라. 실제 의존 gate가 미달이면 해당 후속 단계를 시작하지 말고 bounded 수정 task와 해소 조건을 남겨라. 범위에 맞는 검사·실제 화면 검증과 report/evidence/STATUS/taskStatuses를 남겨라. 소유 변경만 staged diff 확인 후 로컬 커밋하며 혼합 WIP는 소유 hunk 또는 상태 delta만 포함해라. 해시·제외·잔여 WIP·다음 ID/담당/프롬프트를 남기고 멈춰라. push·배포·환자 자동진단·치료·자침 추천/시뮬레이션은 금지한다.
명세 work/tasks/T59.md. 선행: 실행 queue의 직전 필수 gate.
T55 전신 모델의 실제 앞정강근과 부착·발목 bone에 대해 model-local 좌표/endpoint·rest pose를 검증하고 skinning 또는 morph/shape-key 기반 변형을 제작한다. 목표 근육의 형태 변화와 발 움직임을 같은 모델에서 결속한다. 주변 근육은 사용자가 숨기지 않았다면 유지하고 관절을 지나는 주변 구조의 수동 변형/관통도 처리한다. 근육 전체 scale이나 선 길이 감소만으로 대체하지 않는다.

다음 기본 ID는 T60. 단, 미완 batch가 있으면 새 정수 ID의 실제 queue를 따른다. 다음 task는 실행하지 마라.
```

## T60 — 동일 viewport에서 운동 재생 연결

```text
HUMAN ATLAS에서 T60만 수행해라. 담당 Sol High.
AGENTS.md와 R15 13/14/15, 16-ASTRA-UI-HANDOFF.md, 최신 19-ALL-MUSCLES-BEFORE-NERVES.md 및 20-SERIAL-PROMPTS-FULL-SCOPE.md(설계 폴더 design/2026-09-25-muscle-atlas/), STATUS/R15 registry, 해당 task 명세와 선행 실제 report/manifest/evidence를 읽어라. 19/20의 T77 이후 순서가 이전 프롬프트보다 우선한다. 정확히 요청된 ID만 수행하고 자동 다음 실행은 하지 마라. 시작 HEAD/status/source hash를 기록하고 기존 WIP·원본/OpenSim_Models·역사 freeze를 보존해라. 실제 source/근거 없이 이름·좌표·형상·승인을 만들지 마라. AI가 조사/대조/표 작성을 수행하며 사용자에게 기본 해부학 조사 숙제를 넘기지 마라. source provenance와 license/human-review는 내부에 보존하고 learner에 JSON/task/보완자산 구분을 노출하지 마라. 로딩의 로고·인체 그림·슬로건을 복구하지 말고 단일 scene/camera와 미니멀 UI를 유지해라. 모든 target coverage gate는 동결한 전체 분모로 판정하고 필수 누락을 passed_with_gaps로 덮지 마라. 실제 의존 gate가 미달이면 해당 후속 단계를 시작하지 말고 bounded 수정 task와 해소 조건을 남겨라. 범위에 맞는 검사·실제 화면 검증과 report/evidence/STATUS/taskStatuses를 남겨라. 소유 변경만 staged diff 확인 후 로컬 커밋하며 혼합 WIP는 소유 hunk 또는 상태 delta만 포함해라. 해시·제외·잔여 WIP·다음 ID/담당/프롬프트를 남기고 멈춰라. push·배포·환자 자동진단·치료·자침 추천/시뮬레이션은 금지한다.
명세 work/tasks/T60.md. 선행: 실행 queue의 직전 필수 gate.
MotionLearningPanel의 독립 asset/mixer 소유를 AnatomySceneController 명령으로 연결한다. 실제 main renderer가 가진 T59 target node를 애니메이션하고 UI는 play/pause/seek/reset 명령과 상태만 가진다. 사용자 CTA 클릭 전에는 움직이지 않는다. 기존 camera/background/layers/selection을 snapshot해 보존하고 종료 시 pose/가시성만 정확히 복원한다.

다음 기본 ID는 T25. 단, 미완 batch가 있으면 새 정수 ID의 실제 queue를 따른다. 다음 task는 실행하지 마라.
```

## T25 — 같은 전신 모형의 앞정강근 제품 합격

```text
HUMAN ATLAS에서 T25만 수행해라. 담당 Luna Max.
AGENTS.md와 R15 13/14/15, 16-ASTRA-UI-HANDOFF.md, 최신 19-ALL-MUSCLES-BEFORE-NERVES.md 및 20-SERIAL-PROMPTS-FULL-SCOPE.md(설계 폴더 design/2026-09-25-muscle-atlas/), STATUS/R15 registry, 해당 task 명세와 선행 실제 report/manifest/evidence를 읽어라. 19/20의 T77 이후 순서가 이전 프롬프트보다 우선한다. 정확히 요청된 ID만 수행하고 자동 다음 실행은 하지 마라. 시작 HEAD/status/source hash를 기록하고 기존 WIP·원본/OpenSim_Models·역사 freeze를 보존해라. 실제 source/근거 없이 이름·좌표·형상·승인을 만들지 마라. AI가 조사/대조/표 작성을 수행하며 사용자에게 기본 해부학 조사 숙제를 넘기지 마라. source provenance와 license/human-review는 내부에 보존하고 learner에 JSON/task/보완자산 구분을 노출하지 마라. 로딩의 로고·인체 그림·슬로건을 복구하지 말고 단일 scene/camera와 미니멀 UI를 유지해라. 모든 target coverage gate는 동결한 전체 분모로 판정하고 필수 누락을 passed_with_gaps로 덮지 마라. 실제 의존 gate가 미달이면 해당 후속 단계를 시작하지 말고 bounded 수정 task와 해소 조건을 남겨라. 범위에 맞는 검사·실제 화면 검증과 report/evidence/STATUS/taskStatuses를 남겨라. 소유 변경만 staged diff 확인 후 로컬 커밋하며 혼합 WIP는 소유 hunk 또는 상태 delta만 포함해라. 해시·제외·잔여 WIP·다음 ID/담당/프롬프트를 남기고 멈춰라. push·배포·환자 자동진단·치료·자침 추천/시뮬레이션은 금지한다.
명세 work/tasks/T25.md. 선행: 실행 queue의 직전 필수 gate.
T42 공통 카드와 T24 실제 clip을 연결한다. 근육 선택→세 이름/기시·정지→눈에 보이는 '움직임으로 이해하기'→실제 몸 움직임→작용 설명을 연결한다. 클릭은 명시적 재생 요청으로 취급하되 reduced-motion은 정지 자세/수동 단계 선택을 기본으로 한다.

기능 탭 전환과 작용 선택을 동기화하고 pause/resume/처음 자세/느리게/진행 막대를 제공한다. camera reset과 pose reset을 분리한다. 모형 전환이 있으면 학습용 시범 모형임을 짧게 알린다.

선택/부위/탭 전환·로드 실패·unmount 시 loop·mixer·강조를 정리한다. CTA 클릭 전에는 자동 재생하지 않는다.
 T59/T60의 실제 같은 모형 mesh 변형을 main learner에서 검증한다. 별도 T24 bone/path 기술 후보는 pass 근거가 아니다. 전신 탐색→앞정강근→기시정지/기능→CTA→표면 수축과 발 움직임→복원을 시험한다. T24 역사 보고서는 blocked 그대로 보존하고 해결 증거를 새 보고서에 연결한다. 다음은 같은 전신 모형의 소흉근 사례 T27이며, 신경은 전신 근육 시범 gate T85 이후다.
다음 기본 ID는 T27. 단, 미완 batch가 있으면 새 정수 ID의 실제 queue를 따른다. 다음 task는 실행하지 마라.
```

## T27 — 소흉근 동일 모형 변형 준비

```text
HUMAN ATLAS에서 T27만 수행해라. 담당 Sol High.
AGENTS.md와 R15 13/14/15, 16-ASTRA-UI-HANDOFF.md, 최신 19-ALL-MUSCLES-BEFORE-NERVES.md 및 20-SERIAL-PROMPTS-FULL-SCOPE.md(설계 폴더 design/2026-09-25-muscle-atlas/), STATUS/R15 registry, 해당 task 명세와 선행 실제 report/manifest/evidence를 읽어라. 19/20의 T77 이후 순서가 이전 프롬프트보다 우선한다. 정확히 요청된 ID만 수행하고 자동 다음 실행은 하지 마라. 시작 HEAD/status/source hash를 기록하고 기존 WIP·원본/OpenSim_Models·역사 freeze를 보존해라. 실제 source/근거 없이 이름·좌표·형상·승인을 만들지 마라. AI가 조사/대조/표 작성을 수행하며 사용자에게 기본 해부학 조사 숙제를 넘기지 마라. source provenance와 license/human-review는 내부에 보존하고 learner에 JSON/task/보완자산 구분을 노출하지 마라. 로딩의 로고·인체 그림·슬로건을 복구하지 말고 단일 scene/camera와 미니멀 UI를 유지해라. 모든 target coverage gate는 동결한 전체 분모로 판정하고 필수 누락을 passed_with_gaps로 덮지 마라. 실제 의존 gate가 미달이면 해당 후속 단계를 시작하지 말고 bounded 수정 task와 해소 조건을 남겨라. 범위에 맞는 검사·실제 화면 검증과 report/evidence/STATUS/taskStatuses를 남겨라. 소유 변경만 staged diff 확인 후 로컬 커밋하며 혼합 WIP는 소유 hunk 또는 상태 delta만 포함해라. 해시·제외·잔여 WIP·다음 ID/담당/프롬프트를 남기고 멈춰라. push·배포·환자 자동진단·치료·자침 추천/시뮬레이션은 금지한다.
명세 work/tasks/T27.md. 선행: T25 pass.
전신 구조 단계에서 준비된 소흉근/흉곽/견갑대와 완료된 기능 설명을 재사용한다. rig/부착/주변 구조 변형 준비만 검증하고 필요할 때만 근거 있는 상세 자산을 보완한다. 다른 모델/고해상도 LOD가 있다고 가정하지 않는다. T28의 동일 모델 운동을 준비한다.
다음 기본 ID는 T28. 단, 미완 batch가 있으면 새 정수 ID의 실제 queue를 따른다. 다음 task는 실행하지 마라.
```

## T28 — 견갑대 운동 기반과 전인 시범 하나

```text
HUMAN ATLAS에서 T28만 수행해라. 담당 Sol High.
AGENTS.md와 R15 13/14/15, 16-ASTRA-UI-HANDOFF.md, 최신 19-ALL-MUSCLES-BEFORE-NERVES.md 및 20-SERIAL-PROMPTS-FULL-SCOPE.md(설계 폴더 design/2026-09-25-muscle-atlas/), STATUS/R15 registry, 해당 task 명세와 선행 실제 report/manifest/evidence를 읽어라. 19/20의 T77 이후 순서가 이전 프롬프트보다 우선한다. 정확히 요청된 ID만 수행하고 자동 다음 실행은 하지 마라. 시작 HEAD/status/source hash를 기록하고 기존 WIP·원본/OpenSim_Models·역사 freeze를 보존해라. 실제 source/근거 없이 이름·좌표·형상·승인을 만들지 마라. AI가 조사/대조/표 작성을 수행하며 사용자에게 기본 해부학 조사 숙제를 넘기지 마라. source provenance와 license/human-review는 내부에 보존하고 learner에 JSON/task/보완자산 구분을 노출하지 마라. 로딩의 로고·인체 그림·슬로건을 복구하지 말고 단일 scene/camera와 미니멀 UI를 유지해라. 모든 target coverage gate는 동결한 전체 분모로 판정하고 필수 누락을 passed_with_gaps로 덮지 마라. 실제 의존 gate가 미달이면 해당 후속 단계를 시작하지 말고 bounded 수정 task와 해소 조건을 남겨라. 범위에 맞는 검사·실제 화면 검증과 report/evidence/STATUS/taskStatuses를 남겨라. 소유 변경만 staged diff 확인 후 로컬 커밋하며 혼합 WIP는 소유 hunk 또는 상태 delta만 포함해라. 해시·제외·잔여 WIP·다음 ID/담당/프롬프트를 남기고 멈춰라. push·배포·환자 자동진단·치료·자침 추천/시뮬레이션은 금지한다.
명세 work/tasks/T28.md. 선행: 실행 queue의 직전 필수 gate.
T81–84의 전신 내용 batch에서 확정한 조건의 소흉근 관련 견갑골 전인 시범 1개를 제작한다. 흉곽에 대한 견갑대의 이동/회전과 고정 조건을 모델링하고 T45/T46에서 재사용할 골격·경로 제작 도구를 만든다.

단일 임의 hinge 또는 상완골만 움직이는 것으로 견갑골 작용을 대신하지 않는다. 근육 endpoint/변형 또는 표시된 설명 경로를 함께 제공한다. T44의 좌표 정합 원칙을 재사용하되 발목 좌표를 복제하지 않는다.
 기존 세부 수행 범위는 유지하되 R15 동일 전신 scene/근육 표면 변형/명확한 CTA/신경 우선 순서를 적용한다. 이전 별도 시범 모델 허용은 폐기하며 아래 이전 next/prerequisite 문구는 R15 queue로 대체한다.
다음 기본 ID는 T45. 단, 미완 batch가 있으면 새 정수 ID의 실제 queue를 따른다. 다음 task는 실행하지 마라.
```

## T45 — 소흉근 관련 견갑골 하강 시범

```text
HUMAN ATLAS에서 T45만 수행해라. 담당 Sol High.
AGENTS.md와 R15 13/14/15, 16-ASTRA-UI-HANDOFF.md, 최신 19-ALL-MUSCLES-BEFORE-NERVES.md 및 20-SERIAL-PROMPTS-FULL-SCOPE.md(설계 폴더 design/2026-09-25-muscle-atlas/), STATUS/R15 registry, 해당 task 명세와 선행 실제 report/manifest/evidence를 읽어라. 19/20의 T77 이후 순서가 이전 프롬프트보다 우선한다. 정확히 요청된 ID만 수행하고 자동 다음 실행은 하지 마라. 시작 HEAD/status/source hash를 기록하고 기존 WIP·원본/OpenSim_Models·역사 freeze를 보존해라. 실제 source/근거 없이 이름·좌표·형상·승인을 만들지 마라. AI가 조사/대조/표 작성을 수행하며 사용자에게 기본 해부학 조사 숙제를 넘기지 마라. source provenance와 license/human-review는 내부에 보존하고 learner에 JSON/task/보완자산 구분을 노출하지 마라. 로딩의 로고·인체 그림·슬로건을 복구하지 말고 단일 scene/camera와 미니멀 UI를 유지해라. 모든 target coverage gate는 동결한 전체 분모로 판정하고 필수 누락을 passed_with_gaps로 덮지 마라. 실제 의존 gate가 미달이면 해당 후속 단계를 시작하지 말고 bounded 수정 task와 해소 조건을 남겨라. 범위에 맞는 검사·실제 화면 검증과 report/evidence/STATUS/taskStatuses를 남겨라. 소유 변경만 staged diff 확인 후 로컬 커밋하며 혼합 WIP는 소유 hunk 또는 상태 delta만 포함해라. 해시·제외·잔여 WIP·다음 ID/담당/프롬프트를 남기고 멈춰라. push·배포·환자 자동진단·치료·자침 추천/시뮬레이션은 금지한다.
명세 work/tasks/T45.md. 선행: 실행 queue의 직전 필수 gate.
T28 기반을 재사용해 T81–84의 전신 내용 batch에서 근거/조건이 확인된 하강 시범 clip1개를 만든다. 단순 전인 clip의 축값을 바꿔 해부학 근거 대신 쓰지 않는다. moving/fixed structures·근육 경로와 설명을 연결한다.
 기존 세부 수행 범위는 유지하되 R15 동일 전신 scene/근육 표면 변형/명확한 CTA/신경 우선 순서를 적용한다. 이전 별도 시범 모델 허용은 폐기하며 아래 이전 next/prerequisite 문구는 R15 queue로 대체한다.
다음 기본 ID는 T46. 단, 미완 batch가 있으면 새 정수 ID의 실제 queue를 따른다. 다음 task는 실행하지 마라.
```

## T46 — 소흉근 관련 견갑골 하방회전 시범

```text
HUMAN ATLAS에서 T46만 수행해라. 담당 Sol High.
AGENTS.md와 R15 13/14/15, 16-ASTRA-UI-HANDOFF.md, 최신 19-ALL-MUSCLES-BEFORE-NERVES.md 및 20-SERIAL-PROMPTS-FULL-SCOPE.md(설계 폴더 design/2026-09-25-muscle-atlas/), STATUS/R15 registry, 해당 task 명세와 선행 실제 report/manifest/evidence를 읽어라. 19/20의 T77 이후 순서가 이전 프롬프트보다 우선한다. 정확히 요청된 ID만 수행하고 자동 다음 실행은 하지 마라. 시작 HEAD/status/source hash를 기록하고 기존 WIP·원본/OpenSim_Models·역사 freeze를 보존해라. 실제 source/근거 없이 이름·좌표·형상·승인을 만들지 마라. AI가 조사/대조/표 작성을 수행하며 사용자에게 기본 해부학 조사 숙제를 넘기지 마라. source provenance와 license/human-review는 내부에 보존하고 learner에 JSON/task/보완자산 구분을 노출하지 마라. 로딩의 로고·인체 그림·슬로건을 복구하지 말고 단일 scene/camera와 미니멀 UI를 유지해라. 모든 target coverage gate는 동결한 전체 분모로 판정하고 필수 누락을 passed_with_gaps로 덮지 마라. 실제 의존 gate가 미달이면 해당 후속 단계를 시작하지 말고 bounded 수정 task와 해소 조건을 남겨라. 범위에 맞는 검사·실제 화면 검증과 report/evidence/STATUS/taskStatuses를 남겨라. 소유 변경만 staged diff 확인 후 로컬 커밋하며 혼합 WIP는 소유 hunk 또는 상태 delta만 포함해라. 해시·제외·잔여 WIP·다음 ID/담당/프롬프트를 남기고 멈춰라. push·배포·환자 자동진단·치료·자침 추천/시뮬레이션은 금지한다.
명세 work/tasks/T46.md. 선행: 실행 queue의 직전 필수 gate.
T28 기반으로 T81–84의 전신 내용 batch에서 근거/조건이 확인된 하방회전 시범 clip1개를 만든다. 회전 방향과 흉곽 정합을 검증하며 전인/하강과 작용 ID를 구분한다. 대표 시범을 생체 운동의 정량 재현으로 주장하지 않는다.
 기존 세부 수행 범위는 유지하되 R15 동일 전신 scene/근육 표면 변형/명확한 CTA/신경 우선 순서를 적용한다. 이전 별도 시범 모델 허용은 폐기하며 아래 이전 next/prerequisite 문구는 R15 queue로 대체한다.
다음 기본 ID는 T29. 단, 미완 batch가 있으면 새 정수 ID의 실제 queue를 따른다. 다음 task는 실행하지 마라.
```

## T29 — 소흉근 구조·기능 사용자 흐름 통합

```text
HUMAN ATLAS에서 T29만 수행해라. 담당 Luna Max.
AGENTS.md와 R15 13/14/15, 16-ASTRA-UI-HANDOFF.md, 최신 19-ALL-MUSCLES-BEFORE-NERVES.md 및 20-SERIAL-PROMPTS-FULL-SCOPE.md(설계 폴더 design/2026-09-25-muscle-atlas/), STATUS/R15 registry, 해당 task 명세와 선행 실제 report/manifest/evidence를 읽어라. 19/20의 T77 이후 순서가 이전 프롬프트보다 우선한다. 정확히 요청된 ID만 수행하고 자동 다음 실행은 하지 마라. 시작 HEAD/status/source hash를 기록하고 기존 WIP·원본/OpenSim_Models·역사 freeze를 보존해라. 실제 source/근거 없이 이름·좌표·형상·승인을 만들지 마라. AI가 조사/대조/표 작성을 수행하며 사용자에게 기본 해부학 조사 숙제를 넘기지 마라. source provenance와 license/human-review는 내부에 보존하고 learner에 JSON/task/보완자산 구분을 노출하지 마라. 로딩의 로고·인체 그림·슬로건을 복구하지 말고 단일 scene/camera와 미니멀 UI를 유지해라. 모든 target coverage gate는 동결한 전체 분모로 판정하고 필수 누락을 passed_with_gaps로 덮지 마라. 실제 의존 gate가 미달이면 해당 후속 단계를 시작하지 말고 bounded 수정 task와 해소 조건을 남겨라. 범위에 맞는 검사·실제 화면 검증과 report/evidence/STATUS/taskStatuses를 남겨라. 소유 변경만 staged diff 확인 후 로컬 커밋하며 혼합 WIP는 소유 hunk 또는 상태 delta만 포함해라. 해시·제외·잔여 WIP·다음 ID/담당/프롬프트를 남기고 멈춰라. push·배포·환자 자동진단·치료·자침 추천/시뮬레이션은 금지한다.
명세 work/tasks/T29.md. 선행: 실행 queue의 직전 필수 gate.
소흉근 선택→주변 흐림→구조 설명→CTA→전인/하강/하방회전 작용 선택→해당 실제 clip과 설명으로 연결한다. 지원하지 않는 작용은 다른 clip으로 대체하지 않는다. 뼈 카드의 세 이름과 근육으로 돌아오는 흐름을 검증한다.
 기존 세부 수행 범위는 유지하되 R15 동일 전신 scene/근육 표면 변형/명확한 CTA/신경 우선 순서를 적용한다. 이전 별도 시범 모델 허용은 폐기하며 아래 이전 next/prerequisite 문구는 R15 queue로 대체한다.
다음 기본 ID는 T31. 단, 미완 batch가 있으면 새 정수 ID의 실제 queue를 따른다. 다음 task는 실행하지 마라.
```

## T31 — 두 부위 구조·기능 파일럿 합격 검증

```text
HUMAN ATLAS에서 T31만 수행해라. 담당 Luna Max.
AGENTS.md와 R15 13/14/15, 16-ASTRA-UI-HANDOFF.md, 최신 19-ALL-MUSCLES-BEFORE-NERVES.md 및 20-SERIAL-PROMPTS-FULL-SCOPE.md(설계 폴더 design/2026-09-25-muscle-atlas/), STATUS/R15 registry, 해당 task 명세와 선행 실제 report/manifest/evidence를 읽어라. 19/20의 T77 이후 순서가 이전 프롬프트보다 우선한다. 정확히 요청된 ID만 수행하고 자동 다음 실행은 하지 마라. 시작 HEAD/status/source hash를 기록하고 기존 WIP·원본/OpenSim_Models·역사 freeze를 보존해라. 실제 source/근거 없이 이름·좌표·형상·승인을 만들지 마라. AI가 조사/대조/표 작성을 수행하며 사용자에게 기본 해부학 조사 숙제를 넘기지 마라. source provenance와 license/human-review는 내부에 보존하고 learner에 JSON/task/보완자산 구분을 노출하지 마라. 로딩의 로고·인체 그림·슬로건을 복구하지 말고 단일 scene/camera와 미니멀 UI를 유지해라. 모든 target coverage gate는 동결한 전체 분모로 판정하고 필수 누락을 passed_with_gaps로 덮지 마라. 실제 의존 gate가 미달이면 해당 후속 단계를 시작하지 말고 bounded 수정 task와 해소 조건을 남겨라. 범위에 맞는 검사·실제 화면 검증과 report/evidence/STATUS/taskStatuses를 남겨라. 소유 변경만 staged diff 확인 후 로컬 커밋하며 혼합 WIP는 소유 hunk 또는 상태 delta만 포함해라. 해시·제외·잔여 WIP·다음 ID/담당/프롬프트를 남기고 멈춰라. push·배포·환자 자동진단·치료·자침 추천/시뮬레이션은 금지한다.
명세 work/tasks/T31.md. 선행: 실행 queue의 직전 필수 gate.
종아리와 소흉근의 실제 data/scene/clip을 전체 사용자 흐름으로 검사한다. 세 이름·기시정지·뼈 카드·클릭·흐림·움직임·설명·복원을 함께 확인한다. 데이터 검증과 실제 화면 검증을 분리 기록한다.
 기존 세부 수행 범위는 유지하되 R15 동일 전신 scene/근육 표면 변형/명확한 CTA/신경 우선 순서를 적용한다. 이전 별도 시범 모델 허용은 폐기하며 아래 이전 next/prerequisite 문구는 R15 queue로 대체한다.
다음 기본 ID는 T66. 단, 미완 batch가 있으면 새 정수 ID의 실제 queue를 따른다. 다음 task는 실행하지 마라.
```

## T66 — 첫 기능 확장 batch 하나

```text
HUMAN ATLAS에서 T66만 수행해라. 담당 Luna Max.
AGENTS.md와 R15 13/14/15, 16-ASTRA-UI-HANDOFF.md, 최신 19-ALL-MUSCLES-BEFORE-NERVES.md 및 20-SERIAL-PROMPTS-FULL-SCOPE.md(설계 폴더 design/2026-09-25-muscle-atlas/), STATUS/R15 registry, 해당 task 명세와 선행 실제 report/manifest/evidence를 읽어라. 19/20의 T77 이후 순서가 이전 프롬프트보다 우선한다. 정확히 요청된 ID만 수행하고 자동 다음 실행은 하지 마라. 시작 HEAD/status/source hash를 기록하고 기존 WIP·원본/OpenSim_Models·역사 freeze를 보존해라. 실제 source/근거 없이 이름·좌표·형상·승인을 만들지 마라. AI가 조사/대조/표 작성을 수행하며 사용자에게 기본 해부학 조사 숙제를 넘기지 마라. source provenance와 license/human-review는 내부에 보존하고 learner에 JSON/task/보완자산 구분을 노출하지 마라. 로딩의 로고·인체 그림·슬로건을 복구하지 말고 단일 scene/camera와 미니멀 UI를 유지해라. 모든 target coverage gate는 동결한 전체 분모로 판정하고 필수 누락을 passed_with_gaps로 덮지 마라. 실제 의존 gate가 미달이면 해당 후속 단계를 시작하지 말고 bounded 수정 task와 해소 조건을 남겨라. 범위에 맞는 검사·실제 화면 검증과 report/evidence/STATUS/taskStatuses를 남겨라. 소유 변경만 staged diff 확인 후 로컬 커밋하며 혼합 WIP는 소유 hunk 또는 상태 delta만 포함해라. 해시·제외·잔여 WIP·다음 ID/담당/프롬프트를 남기고 멈춰라. push·배포·환자 자동진단·치료·자침 추천/시뮬레이션은 금지한다.
명세 work/tasks/T66.md. 선행: 실행 queue의 직전 필수 gate.
T35에서 동결한 단일 action-family를 대상으로 검증된 동일 rig의 공유 clip 연결 최대10관계 또는 기존 rig 기반 clip1개만 구현한다. 새 관절/rig 정합이 필요하면 Sol task로 따로 배정하고 이 task를 확장하지 않는다.

다음 기본 ID는 T47. 단, 미완 batch가 있으면 새 정수 ID의 실제 queue를 따른다. 다음 task는 실행하지 마라.
```

## T47 — 전신 구조·기능·운동 자료 감사

```text
HUMAN ATLAS에서 T47만 수행해라. 담당 Luna Max.
AGENTS.md와 R15 13/14/15, 16-ASTRA-UI-HANDOFF.md, 최신 19-ALL-MUSCLES-BEFORE-NERVES.md 및 20-SERIAL-PROMPTS-FULL-SCOPE.md(설계 폴더 design/2026-09-25-muscle-atlas/), STATUS/R15 registry, 해당 task 명세와 선행 실제 report/manifest/evidence를 읽어라. 19/20의 T77 이후 순서가 이전 프롬프트보다 우선한다. 정확히 요청된 ID만 수행하고 자동 다음 실행은 하지 마라. 시작 HEAD/status/source hash를 기록하고 기존 WIP·원본/OpenSim_Models·역사 freeze를 보존해라. 실제 source/근거 없이 이름·좌표·형상·승인을 만들지 마라. AI가 조사/대조/표 작성을 수행하며 사용자에게 기본 해부학 조사 숙제를 넘기지 마라. source provenance와 license/human-review는 내부에 보존하고 learner에 JSON/task/보완자산 구분을 노출하지 마라. 로딩의 로고·인체 그림·슬로건을 복구하지 말고 단일 scene/camera와 미니멀 UI를 유지해라. 모든 target coverage gate는 동결한 전체 분모로 판정하고 필수 누락을 passed_with_gaps로 덮지 마라. 실제 의존 gate가 미달이면 해당 후속 단계를 시작하지 말고 bounded 수정 task와 해소 조건을 남겨라. 범위에 맞는 검사·실제 화면 검증과 report/evidence/STATUS/taskStatuses를 남겨라. 소유 변경만 staged diff 확인 후 로컬 커밋하며 혼합 WIP는 소유 hunk 또는 상태 delta만 포함해라. 해시·제외·잔여 WIP·다음 ID/담당/프롬프트를 남기고 멈춰라. push·배포·환자 자동진단·치료·자침 추천/시뮬레이션은 금지한다.
명세 work/tasks/T47.md. 선행: 모든 근육 animation batch.
전체 구조/기시정지/기능/대표 motion 분모를 데이터/파일/실제 binding으로 전수 감사한다. 첫 batch/pilot 완료를 전신 완료로 쓰지 않는다. 필수 누락은 수정 작업으로 배정하고 T85 시각·사용자 흐름 합격과 분리한다.
다음 기본 ID는 T85. 단, 미완 batch가 있으면 새 정수 ID의 실제 queue를 따른다. 다음 task는 실행하지 마라.
```

## T85 — 모든 근육 움직임 학습 coverage 합격

```text
HUMAN ATLAS에서 T85만 수행해라. 담당 Astra · 현재 대화 직접 구현.
AGENTS.md와 R15 13/14/15, 16-ASTRA-UI-HANDOFF.md, 최신 19-ALL-MUSCLES-BEFORE-NERVES.md 및 20-SERIAL-PROMPTS-FULL-SCOPE.md(설계 폴더 design/2026-09-25-muscle-atlas/), STATUS/R15 registry, 해당 task 명세와 선행 실제 report/manifest/evidence를 읽어라. 19/20의 T77 이후 순서가 이전 프롬프트보다 우선한다. 정확히 요청된 ID만 수행하고 자동 다음 실행은 하지 마라. 시작 HEAD/status/source hash를 기록하고 기존 WIP·원본/OpenSim_Models·역사 freeze를 보존해라. 실제 source/근거 없이 이름·좌표·형상·승인을 만들지 마라. AI가 조사/대조/표 작성을 수행하며 사용자에게 기본 해부학 조사 숙제를 넘기지 마라. source provenance와 license/human-review는 내부에 보존하고 learner에 JSON/task/보완자산 구분을 노출하지 마라. 로딩의 로고·인체 그림·슬로건을 복구하지 말고 단일 scene/camera와 미니멀 UI를 유지해라. 모든 target coverage gate는 동결한 전체 분모로 판정하고 필수 누락을 passed_with_gaps로 덮지 마라. 실제 의존 gate가 미달이면 해당 후속 단계를 시작하지 말고 bounded 수정 task와 해소 조건을 남겨라. 범위에 맞는 검사·실제 화면 검증과 report/evidence/STATUS/taskStatuses를 남겨라. 소유 변경만 staged diff 확인 후 로컬 커밋하며 혼합 WIP는 소유 hunk 또는 상태 delta만 포함해라. 해시·제외·잔여 WIP·다음 ID/담당/프롬프트를 남기고 멈춰라. push·배포·환자 자동진단·치료·자침 추천/시뮬레이션은 금지한다.
명세 work/tasks/T85.md. 선행: 모든 동결 animation batch 및 T47 감사.
T78/T35의 모든 근육 target이 기시정지·기능 설명과 실제 같은 model surface 시범 최소1개를 갖는지 검사한다. 전신→근육→움직임으로 이해하기→수축/관련 신체 운동→복원을 실제 scene에서 검증한다. scale-only/뼈만/다른 viewer/근육 숨김 대체는 실패다. 주변 구조의 수동 변형과 부착·관통·camera/layer/선택 연속성, 설명 동기를 확인한다. 미지원 근육/형상이 남으면 partial이며 신경 단계로 자동 진입하지 않는다. 모든 가능한 작용/정량 생리 시뮬레이션 완료로 과장하지 않는다.
다음 기본 ID는 T61. 단, 미완 batch가 있으면 새 정수 ID의 실제 queue를 따른다. 다음 task는 실행하지 마라.
```

## T61 — 신경 레이어·선택·관계 데이터 계약

```text
HUMAN ATLAS에서 T61만 수행해라. 담당 Sol High.
AGENTS.md와 R15 13/14/15, 16-ASTRA-UI-HANDOFF.md, 최신 19-ALL-MUSCLES-BEFORE-NERVES.md 및 20-SERIAL-PROMPTS-FULL-SCOPE.md(설계 폴더 design/2026-09-25-muscle-atlas/), STATUS/R15 registry, 해당 task 명세와 선행 실제 report/manifest/evidence를 읽어라. 19/20의 T77 이후 순서가 이전 프롬프트보다 우선한다. 정확히 요청된 ID만 수행하고 자동 다음 실행은 하지 마라. 시작 HEAD/status/source hash를 기록하고 기존 WIP·원본/OpenSim_Models·역사 freeze를 보존해라. 실제 source/근거 없이 이름·좌표·형상·승인을 만들지 마라. AI가 조사/대조/표 작성을 수행하며 사용자에게 기본 해부학 조사 숙제를 넘기지 마라. source provenance와 license/human-review는 내부에 보존하고 learner에 JSON/task/보완자산 구분을 노출하지 마라. 로딩의 로고·인체 그림·슬로건을 복구하지 말고 단일 scene/camera와 미니멀 UI를 유지해라. 모든 target coverage gate는 동결한 전체 분모로 판정하고 필수 누락을 passed_with_gaps로 덮지 마라. 실제 의존 gate가 미달이면 해당 후속 단계를 시작하지 말고 bounded 수정 task와 해소 조건을 남겨라. 범위에 맞는 검사·실제 화면 검증과 report/evidence/STATUS/taskStatuses를 남겨라. 소유 변경만 staged diff 확인 후 로컬 커밋하며 혼합 WIP는 소유 hunk 또는 상태 delta만 포함해라. 해시·제외·잔여 WIP·다음 ID/담당/프롬프트를 남기고 멈춰라. push·배포·환자 자동진단·치료·자침 추천/시뮬레이션은 금지한다.
명세 work/tasks/T61.md. 선행: T85 pass.
전신 근육 기능/animation 합격 후 신경의 typed selection, branch graph, 다중 지배근 관계, source/frame/pose/registration, 레이어와 카드 계약만 구현한다. 전신 조사/3D는 T86 이후다. 같은 scene에 확장하며 감각분포·피부분절·경락을 혼합하지 않는다.
다음 기본 ID는 T86. 단, 미완 batch가 있으면 새 정수 ID의 실제 queue를 따른다. 다음 task는 실행하지 마라.
```

## T86 — 전신 신경 목표·복수 원문 모델 조사

```text
HUMAN ATLAS에서 T86만 수행해라. 담당 Sol High.
AGENTS.md와 R15 13/14/15, 16-ASTRA-UI-HANDOFF.md, 최신 19-ALL-MUSCLES-BEFORE-NERVES.md 및 20-SERIAL-PROMPTS-FULL-SCOPE.md(설계 폴더 design/2026-09-25-muscle-atlas/), STATUS/R15 registry, 해당 task 명세와 선행 실제 report/manifest/evidence를 읽어라. 19/20의 T77 이후 순서가 이전 프롬프트보다 우선한다. 정확히 요청된 ID만 수행하고 자동 다음 실행은 하지 마라. 시작 HEAD/status/source hash를 기록하고 기존 WIP·원본/OpenSim_Models·역사 freeze를 보존해라. 실제 source/근거 없이 이름·좌표·형상·승인을 만들지 마라. AI가 조사/대조/표 작성을 수행하며 사용자에게 기본 해부학 조사 숙제를 넘기지 마라. source provenance와 license/human-review는 내부에 보존하고 learner에 JSON/task/보완자산 구분을 노출하지 마라. 로딩의 로고·인체 그림·슬로건을 복구하지 말고 단일 scene/camera와 미니멀 UI를 유지해라. 모든 target coverage gate는 동결한 전체 분모로 판정하고 필수 누락을 passed_with_gaps로 덮지 마라. 실제 의존 gate가 미달이면 해당 후속 단계를 시작하지 말고 bounded 수정 task와 해소 조건을 남겨라. 범위에 맞는 검사·실제 화면 검증과 report/evidence/STATUS/taskStatuses를 남겨라. 소유 변경만 staged diff 확인 후 로컬 커밋하며 혼합 WIP는 소유 hunk 또는 상태 delta만 포함해라. 해시·제외·잔여 WIP·다음 ID/담당/프롬프트를 남기고 멈춰라. push·배포·환자 자동진단·치료·자침 추천/시뮬레이션은 금지한다.
명세 work/tasks/T86.md. 선행: T85 pass 및 T61 계약.
전신 신경 target 분모를 명시한다. 뇌신경·척수신경/신경총·말초 분지·관련 자율신경을 항목별로 포함/별도 scope 판정하고 이름 없는 미세 말단을 유한한 모두 목록으로 위장하지 않는다. 사용자 전신 목표를 하지 pilot로 축소하지 않는다. 복수의 공식/원문 해부학 모델과 자료에서 source identity/분지/좌우/주행/지배/감각/pose/frame/권리를 비교하고 차이/변이를 보존한다. 모델 자료의 기본 mesh와 여러 자료의 관계 근거를 분리해 통합 전략을 정한다. 좌표를 눈대중으로 포개거나 평균해 주행을 만들지 않는다. 모든 조사 batch를 최대10개 nerve concept, trunk/branch별로 정수 task 배정하고 T62/T87부터 시작해 T88 전에 완료하도록 한다.
다음 기본 ID는 T62. 단, 미완 batch가 있으면 새 정수 ID의 실제 queue를 따른다. 다음 task는 실행하지 마라.
```

## T62 — 첫 하지 신경 자료 패키지

```text
HUMAN ATLAS에서 T62만 수행해라. 담당 Luna Max.
AGENTS.md와 R15 13/14/15, 16-ASTRA-UI-HANDOFF.md, 최신 19-ALL-MUSCLES-BEFORE-NERVES.md 및 20-SERIAL-PROMPTS-FULL-SCOPE.md(설계 폴더 design/2026-09-25-muscle-atlas/), STATUS/R15 registry, 해당 task 명세와 선행 실제 report/manifest/evidence를 읽어라. 19/20의 T77 이후 순서가 이전 프롬프트보다 우선한다. 정확히 요청된 ID만 수행하고 자동 다음 실행은 하지 마라. 시작 HEAD/status/source hash를 기록하고 기존 WIP·원본/OpenSim_Models·역사 freeze를 보존해라. 실제 source/근거 없이 이름·좌표·형상·승인을 만들지 마라. AI가 조사/대조/표 작성을 수행하며 사용자에게 기본 해부학 조사 숙제를 넘기지 마라. source provenance와 license/human-review는 내부에 보존하고 learner에 JSON/task/보완자산 구분을 노출하지 마라. 로딩의 로고·인체 그림·슬로건을 복구하지 말고 단일 scene/camera와 미니멀 UI를 유지해라. 모든 target coverage gate는 동결한 전체 분모로 판정하고 필수 누락을 passed_with_gaps로 덮지 마라. 실제 의존 gate가 미달이면 해당 후속 단계를 시작하지 말고 bounded 수정 task와 해소 조건을 남겨라. 범위에 맞는 검사·실제 화면 검증과 report/evidence/STATUS/taskStatuses를 남겨라. 소유 변경만 staged diff 확인 후 로컬 커밋하며 혼합 WIP는 소유 hunk 또는 상태 delta만 포함해라. 해시·제외·잔여 WIP·다음 ID/담당/프롬프트를 남기고 멈춰라. push·배포·환자 자동진단·치료·자침 추천/시뮬레이션은 금지한다.
명세 work/tasks/T62.md. 선행: T86.
T86 전신 조사 queue의 첫 하지 신경 trunk1개/branch최대2개 자료를 조사한다. 기존 명세의 상세 근거·검증은 유지하고 이 pilot 하나로 전체 신경 조사 완료를 선언하지 않는다. 다음 T87과 나머지 전체 조사 batch다.
다음 기본 ID는 T87. 단, 미완 batch가 있으면 새 정수 ID의 실제 queue를 따른다. 다음 task는 실행하지 마라.
```

## T87 — 전신 신경 조사 확장 첫 batch

```text
HUMAN ATLAS에서 T87만 수행해라. 담당 Luna Max.
AGENTS.md와 R15 13/14/15, 16-ASTRA-UI-HANDOFF.md, 최신 19-ALL-MUSCLES-BEFORE-NERVES.md 및 20-SERIAL-PROMPTS-FULL-SCOPE.md(설계 폴더 design/2026-09-25-muscle-atlas/), STATUS/R15 registry, 해당 task 명세와 선행 실제 report/manifest/evidence를 읽어라. 19/20의 T77 이후 순서가 이전 프롬프트보다 우선한다. 정확히 요청된 ID만 수행하고 자동 다음 실행은 하지 마라. 시작 HEAD/status/source hash를 기록하고 기존 WIP·원본/OpenSim_Models·역사 freeze를 보존해라. 실제 source/근거 없이 이름·좌표·형상·승인을 만들지 마라. AI가 조사/대조/표 작성을 수행하며 사용자에게 기본 해부학 조사 숙제를 넘기지 마라. source provenance와 license/human-review는 내부에 보존하고 learner에 JSON/task/보완자산 구분을 노출하지 마라. 로딩의 로고·인체 그림·슬로건을 복구하지 말고 단일 scene/camera와 미니멀 UI를 유지해라. 모든 target coverage gate는 동결한 전체 분모로 판정하고 필수 누락을 passed_with_gaps로 덮지 마라. 실제 의존 gate가 미달이면 해당 후속 단계를 시작하지 말고 bounded 수정 task와 해소 조건을 남겨라. 범위에 맞는 검사·실제 화면 검증과 report/evidence/STATUS/taskStatuses를 남겨라. 소유 변경만 staged diff 확인 후 로컬 커밋하며 혼합 WIP는 소유 hunk 또는 상태 delta만 포함해라. 해시·제외·잔여 WIP·다음 ID/담당/프롬프트를 남기고 멈춰라. push·배포·환자 자동진단·치료·자침 추천/시뮬레이션은 금지한다.
명세 work/tasks/T87.md. 선행: T86 분모·조사 queue 및 T62 첫 패키지.
T86이 정한 다음 최대10개 신경 개념의 이름/분지/주행/좌우/지배근/감각/원문 차이를 조사하고 source 모델 간 대조표를 실제 작성한다. 다음 조사 batch들을 순차 진행하며 T88 전에 전체 동결 target을 채운다. geometry 획득과 교육 설명의 출처/허가를 독립 기록하고 아직 learner 3D를 구현하지 않는다.
다음 기본 ID는 T88. 단, 미완 batch가 있으면 새 정수 ID의 실제 queue를 따른다. 다음 task는 실행하지 마라.
```

## T88 — 전신 신경 자료 통합·등록 검증

```text
HUMAN ATLAS에서 T88만 수행해라. 담당 Sol High.
AGENTS.md와 R15 13/14/15, 16-ASTRA-UI-HANDOFF.md, 최신 19-ALL-MUSCLES-BEFORE-NERVES.md 및 20-SERIAL-PROMPTS-FULL-SCOPE.md(설계 폴더 design/2026-09-25-muscle-atlas/), STATUS/R15 registry, 해당 task 명세와 선행 실제 report/manifest/evidence를 읽어라. 19/20의 T77 이후 순서가 이전 프롬프트보다 우선한다. 정확히 요청된 ID만 수행하고 자동 다음 실행은 하지 마라. 시작 HEAD/status/source hash를 기록하고 기존 WIP·원본/OpenSim_Models·역사 freeze를 보존해라. 실제 source/근거 없이 이름·좌표·형상·승인을 만들지 마라. AI가 조사/대조/표 작성을 수행하며 사용자에게 기본 해부학 조사 숙제를 넘기지 마라. source provenance와 license/human-review는 내부에 보존하고 learner에 JSON/task/보완자산 구분을 노출하지 마라. 로딩의 로고·인체 그림·슬로건을 복구하지 말고 단일 scene/camera와 미니멀 UI를 유지해라. 모든 target coverage gate는 동결한 전체 분모로 판정하고 필수 누락을 passed_with_gaps로 덮지 마라. 실제 의존 gate가 미달이면 해당 후속 단계를 시작하지 말고 bounded 수정 task와 해소 조건을 남겨라. 범위에 맞는 검사·실제 화면 검증과 report/evidence/STATUS/taskStatuses를 남겨라. 소유 변경만 staged diff 확인 후 로컬 커밋하며 혼합 WIP는 소유 hunk 또는 상태 delta만 포함해라. 해시·제외·잔여 WIP·다음 ID/담당/프롬프트를 남기고 멈춰라. push·배포·환자 자동진단·치료·자침 추천/시뮬레이션은 금지한다.
명세 work/tasks/T88.md. 선행: 모든 T86 신경 조사 batch.
전체 target의 조사 결과를 공통 graph에 통합하고 중복/동의어/좌우/branch/지배근 mapping/출처 차이를 검증한다. 모델별 registration과 변형/pose 차이에 대한 정량 기준을 명시한다. registration이 필요한 경우 작은 별도 기술 task를 T63 앞에 넣는다. 실제 source surface/path가 없으면 두 endpoint 직선으로 대체하지 않는다. 충분한 조사/통합이 끝난 뒤에만 3D 구현 단계로 이동한다.
다음 기본 ID는 T63. 단, 미완 batch가 있으면 새 정수 ID의 실제 queue를 따른다. 다음 task는 실행하지 마라.
```

## T63 — 첫 신경 3D 주행과 지배근 강조

```text
HUMAN ATLAS에서 T63만 수행해라. 담당 Sol High.
AGENTS.md와 R15 13/14/15, 16-ASTRA-UI-HANDOFF.md, 최신 19-ALL-MUSCLES-BEFORE-NERVES.md 및 20-SERIAL-PROMPTS-FULL-SCOPE.md(설계 폴더 design/2026-09-25-muscle-atlas/), STATUS/R15 registry, 해당 task 명세와 선행 실제 report/manifest/evidence를 읽어라. 19/20의 T77 이후 순서가 이전 프롬프트보다 우선한다. 정확히 요청된 ID만 수행하고 자동 다음 실행은 하지 마라. 시작 HEAD/status/source hash를 기록하고 기존 WIP·원본/OpenSim_Models·역사 freeze를 보존해라. 실제 source/근거 없이 이름·좌표·형상·승인을 만들지 마라. AI가 조사/대조/표 작성을 수행하며 사용자에게 기본 해부학 조사 숙제를 넘기지 마라. source provenance와 license/human-review는 내부에 보존하고 learner에 JSON/task/보완자산 구분을 노출하지 마라. 로딩의 로고·인체 그림·슬로건을 복구하지 말고 단일 scene/camera와 미니멀 UI를 유지해라. 모든 target coverage gate는 동결한 전체 분모로 판정하고 필수 누락을 passed_with_gaps로 덮지 마라. 실제 의존 gate가 미달이면 해당 후속 단계를 시작하지 말고 bounded 수정 task와 해소 조건을 남겨라. 범위에 맞는 검사·실제 화면 검증과 report/evidence/STATUS/taskStatuses를 남겨라. 소유 변경만 staged diff 확인 후 로컬 커밋하며 혼합 WIP는 소유 hunk 또는 상태 delta만 포함해라. 해시·제외·잔여 WIP·다음 ID/담당/프롬프트를 남기고 멈춰라. push·배포·환자 자동진단·치료·자침 추천/시뮬레이션은 금지한다.
명세 work/tasks/T63.md. 선행: T88 pass 및 필요한 registration task.
전체 신경 조사·통합 후 첫 검증된 신경 주행을 같은 scene에 구현한다. 원래 명세의 실제 주행/좌표/pose 검증을 유지한다. 클릭 시 근거 있는 지배근을 강조하고 다른 근육을 흐리며 복원 가능하게 한다. 신경 기본 설명 카드와 세 이름을 연결한다. 다음 나머지 전신 nerve 3D batch이며 포착 설명을 먼저 구현하지 않는다.
다음 기본 ID는 T89. 단, 미완 batch가 있으면 새 정수 ID의 실제 queue를 따른다. 다음 task는 실행하지 마라.
```

## T89 — 전신 신경 3D 확장 첫 batch

```text
HUMAN ATLAS에서 T89만 수행해라. 담당 Luna Max.
AGENTS.md와 R15 13/14/15, 16-ASTRA-UI-HANDOFF.md, 최신 19-ALL-MUSCLES-BEFORE-NERVES.md 및 20-SERIAL-PROMPTS-FULL-SCOPE.md(설계 폴더 design/2026-09-25-muscle-atlas/), STATUS/R15 registry, 해당 task 명세와 선행 실제 report/manifest/evidence를 읽어라. 19/20의 T77 이후 순서가 이전 프롬프트보다 우선한다. 정확히 요청된 ID만 수행하고 자동 다음 실행은 하지 마라. 시작 HEAD/status/source hash를 기록하고 기존 WIP·원본/OpenSim_Models·역사 freeze를 보존해라. 실제 source/근거 없이 이름·좌표·형상·승인을 만들지 마라. AI가 조사/대조/표 작성을 수행하며 사용자에게 기본 해부학 조사 숙제를 넘기지 마라. source provenance와 license/human-review는 내부에 보존하고 learner에 JSON/task/보완자산 구분을 노출하지 마라. 로딩의 로고·인체 그림·슬로건을 복구하지 말고 단일 scene/camera와 미니멀 UI를 유지해라. 모든 target coverage gate는 동결한 전체 분모로 판정하고 필수 누락을 passed_with_gaps로 덮지 마라. 실제 의존 gate가 미달이면 해당 후속 단계를 시작하지 말고 bounded 수정 task와 해소 조건을 남겨라. 범위에 맞는 검사·실제 화면 검증과 report/evidence/STATUS/taskStatuses를 남겨라. 소유 변경만 staged diff 확인 후 로컬 커밋하며 혼합 WIP는 소유 hunk 또는 상태 delta만 포함해라. 해시·제외·잔여 WIP·다음 ID/담당/프롬프트를 남기고 멈춰라. push·배포·환자 자동진단·치료·자침 추천/시뮬레이션은 금지한다.
명세 work/tasks/T89.md. 선행: T88 통합 gate 및 T63 첫 실제 주행.
T63에서 검증한 adapter로 다음 한 nerve trunk/제한된 branch package를 같은 AnatomySceneRoot에 구현한다. 새로운 복잡한 registration/rig가 필요한 항목은 Sol High의 별도 task로 나눈다. 전체 target의 나머지 3D 작업을 작은 정수 task로 T90 앞에 배정한다. 클릭한 신경과 지배근을 강조하고 나머지 근육은 은은하게 흐리며 복원 토글을 제공한다. 지배근은 실제 relation 근거로 선택하고 단순 근접거리로 추정하지 않는다. 카드에는 해당 신경 설명을 보여주고 아직 포착/기능이상 설명은 후속 단계로 둔다.
다음 기본 ID는 T90. 단, 미완 batch가 있으면 새 정수 ID의 실제 queue를 따른다. 다음 task는 실행하지 마라.
```

## T90 — 전신 신경 주행·지배근 그래픽 합격

```text
HUMAN ATLAS에서 T90만 수행해라. 담당 Astra · 현재 대화 직접 구현.
AGENTS.md와 R15 13/14/15, 16-ASTRA-UI-HANDOFF.md, 최신 19-ALL-MUSCLES-BEFORE-NERVES.md 및 20-SERIAL-PROMPTS-FULL-SCOPE.md(설계 폴더 design/2026-09-25-muscle-atlas/), STATUS/R15 registry, 해당 task 명세와 선행 실제 report/manifest/evidence를 읽어라. 19/20의 T77 이후 순서가 이전 프롬프트보다 우선한다. 정확히 요청된 ID만 수행하고 자동 다음 실행은 하지 마라. 시작 HEAD/status/source hash를 기록하고 기존 WIP·원본/OpenSim_Models·역사 freeze를 보존해라. 실제 source/근거 없이 이름·좌표·형상·승인을 만들지 마라. AI가 조사/대조/표 작성을 수행하며 사용자에게 기본 해부학 조사 숙제를 넘기지 마라. source provenance와 license/human-review는 내부에 보존하고 learner에 JSON/task/보완자산 구분을 노출하지 마라. 로딩의 로고·인체 그림·슬로건을 복구하지 말고 단일 scene/camera와 미니멀 UI를 유지해라. 모든 target coverage gate는 동결한 전체 분모로 판정하고 필수 누락을 passed_with_gaps로 덮지 마라. 실제 의존 gate가 미달이면 해당 후속 단계를 시작하지 말고 bounded 수정 task와 해소 조건을 남겨라. 범위에 맞는 검사·실제 화면 검증과 report/evidence/STATUS/taskStatuses를 남겨라. 소유 변경만 staged diff 확인 후 로컬 커밋하며 혼합 WIP는 소유 hunk 또는 상태 delta만 포함해라. 해시·제외·잔여 WIP·다음 ID/담당/프롬프트를 남기고 멈춰라. push·배포·환자 자동진단·치료·자침 추천/시뮬레이션은 금지한다.
명세 work/tasks/T90.md. 선행: 전체 신경 3D batch.
동결 신경 target의 실제 주행/선택/지배근 강조/카드/복원/pose를 전수 데이터 감사하고 region별 화면을 검증한다. 모든 muscle motion 중 정적 신경을 잘못 고정해 표시하지 않는다. pose 지원이 없으면 사용자에게 명확히 알리고 rest pose 탐색으로 복원한다. 자료 부족을 전신 완료로 세지 않는다. 신경 기본 설명과 그래픽 통합이 합격한 뒤 T64/T91 포착·기능이상 내용으로 간다.
다음 기본 ID는 T64. 단, 미완 batch가 있으면 새 정수 ID의 실제 queue를 따른다. 다음 task는 실행하지 마라.
```

## T64 — 신경 포착·기능 변화의 접힌 설명 UI

```text
HUMAN ATLAS에서 T64만 수행해라. 담당 Luna Max.
AGENTS.md와 R15 13/14/15, 16-ASTRA-UI-HANDOFF.md, 최신 19-ALL-MUSCLES-BEFORE-NERVES.md 및 20-SERIAL-PROMPTS-FULL-SCOPE.md(설계 폴더 design/2026-09-25-muscle-atlas/), STATUS/R15 registry, 해당 task 명세와 선행 실제 report/manifest/evidence를 읽어라. 19/20의 T77 이후 순서가 이전 프롬프트보다 우선한다. 정확히 요청된 ID만 수행하고 자동 다음 실행은 하지 마라. 시작 HEAD/status/source hash를 기록하고 기존 WIP·원본/OpenSim_Models·역사 freeze를 보존해라. 실제 source/근거 없이 이름·좌표·형상·승인을 만들지 마라. AI가 조사/대조/표 작성을 수행하며 사용자에게 기본 해부학 조사 숙제를 넘기지 마라. source provenance와 license/human-review는 내부에 보존하고 learner에 JSON/task/보완자산 구분을 노출하지 마라. 로딩의 로고·인체 그림·슬로건을 복구하지 말고 단일 scene/camera와 미니멀 UI를 유지해라. 모든 target coverage gate는 동결한 전체 분모로 판정하고 필수 누락을 passed_with_gaps로 덮지 마라. 실제 의존 gate가 미달이면 해당 후속 단계를 시작하지 말고 bounded 수정 task와 해소 조건을 남겨라. 범위에 맞는 검사·실제 화면 검증과 report/evidence/STATUS/taskStatuses를 남겨라. 소유 변경만 staged diff 확인 후 로컬 커밋하며 혼합 WIP는 소유 hunk 또는 상태 delta만 포함해라. 해시·제외·잔여 WIP·다음 ID/담당/프롬프트를 남기고 멈춰라. push·배포·환자 자동진단·치료·자침 추천/시뮬레이션은 금지한다.
명세 work/tasks/T64.md. 선행: T90 pass.
신경 3D와 지배근 그래픽 완성 후 첫 trunk1/branch≤2의 포착 가능 구간과 병변 수준별 기능 변화 설명을 실제 근거로 작성한다. 처음부터 모든 정보를 펼치지 않는다. T91/후속 batch로 전신 내용 범위를 확장하고 치료/자침 추천은 넣지 않는다.
다음 기본 ID는 T91. 단, 미완 batch가 있으면 새 정수 ID의 실제 queue를 따른다. 다음 task는 실행하지 마라.
```

## T91 — 신경 포착·기능이상 설명 확장 첫 batch

```text
HUMAN ATLAS에서 T91만 수행해라. 담당 Luna Max.
AGENTS.md와 R15 13/14/15, 16-ASTRA-UI-HANDOFF.md, 최신 19-ALL-MUSCLES-BEFORE-NERVES.md 및 20-SERIAL-PROMPTS-FULL-SCOPE.md(설계 폴더 design/2026-09-25-muscle-atlas/), STATUS/R15 registry, 해당 task 명세와 선행 실제 report/manifest/evidence를 읽어라. 19/20의 T77 이후 순서가 이전 프롬프트보다 우선한다. 정확히 요청된 ID만 수행하고 자동 다음 실행은 하지 마라. 시작 HEAD/status/source hash를 기록하고 기존 WIP·원본/OpenSim_Models·역사 freeze를 보존해라. 실제 source/근거 없이 이름·좌표·형상·승인을 만들지 마라. AI가 조사/대조/표 작성을 수행하며 사용자에게 기본 해부학 조사 숙제를 넘기지 마라. source provenance와 license/human-review는 내부에 보존하고 learner에 JSON/task/보완자산 구분을 노출하지 마라. 로딩의 로고·인체 그림·슬로건을 복구하지 말고 단일 scene/camera와 미니멀 UI를 유지해라. 모든 target coverage gate는 동결한 전체 분모로 판정하고 필수 누락을 passed_with_gaps로 덮지 마라. 실제 의존 gate가 미달이면 해당 후속 단계를 시작하지 말고 bounded 수정 task와 해소 조건을 남겨라. 범위에 맞는 검사·실제 화면 검증과 report/evidence/STATUS/taskStatuses를 남겨라. 소유 변경만 staged diff 확인 후 로컬 커밋하며 혼합 WIP는 소유 hunk 또는 상태 delta만 포함해라. 해시·제외·잔여 WIP·다음 ID/담당/프롬프트를 남기고 멈춰라. push·배포·환자 자동진단·치료·자침 추천/시뮬레이션은 금지한다.
명세 work/tasks/T91.md. 선행: T90 및 T64 첫 설명 패키지.
전체 신경 target 중 근거가 있는 포착/병변 수준별 내용에 대해 다음 최대10개 개념 batch를 조사·검증·연결한다. 가능한 구간/주변 구조·운동/감각 변화·분지/병변 수준·조건·변이/감별 한계를 분리한다. 모든 신경에 알려진 포착점이 반드시 있다고 가정하지 않고 근거 미확인은 명시적인 내용 상태로 둔다. 남은 batch를 정수 ID로 T65 앞에 배정한다. 신경 클릭 때 기본 주행/지배 설명만 보이고 포착과 기능 변화는 접힌 항목으로 표시한다. 환자 자동진단/자침점·깊이·치료 추천은 만들지 않는다.
다음 기본 ID는 T65. 단, 미완 batch가 있으면 새 정수 ID의 실제 queue를 따른다. 다음 task는 실행하지 마라.
```

## T65 — 전신 근육·신경·기능이상 설명 최종 통합 검증

```text
HUMAN ATLAS에서 T65만 수행해라. 담당 Luna Max.
AGENTS.md와 R15 13/14/15, 16-ASTRA-UI-HANDOFF.md, 최신 19-ALL-MUSCLES-BEFORE-NERVES.md 및 20-SERIAL-PROMPTS-FULL-SCOPE.md(설계 폴더 design/2026-09-25-muscle-atlas/), STATUS/R15 registry, 해당 task 명세와 선행 실제 report/manifest/evidence를 읽어라. 19/20의 T77 이후 순서가 이전 프롬프트보다 우선한다. 정확히 요청된 ID만 수행하고 자동 다음 실행은 하지 마라. 시작 HEAD/status/source hash를 기록하고 기존 WIP·원본/OpenSim_Models·역사 freeze를 보존해라. 실제 source/근거 없이 이름·좌표·형상·승인을 만들지 마라. AI가 조사/대조/표 작성을 수행하며 사용자에게 기본 해부학 조사 숙제를 넘기지 마라. source provenance와 license/human-review는 내부에 보존하고 learner에 JSON/task/보완자산 구분을 노출하지 마라. 로딩의 로고·인체 그림·슬로건을 복구하지 말고 단일 scene/camera와 미니멀 UI를 유지해라. 모든 target coverage gate는 동결한 전체 분모로 판정하고 필수 누락을 passed_with_gaps로 덮지 마라. 실제 의존 gate가 미달이면 해당 후속 단계를 시작하지 말고 bounded 수정 task와 해소 조건을 남겨라. 범위에 맞는 검사·실제 화면 검증과 report/evidence/STATUS/taskStatuses를 남겨라. 소유 변경만 staged diff 확인 후 로컬 커밋하며 혼합 WIP는 소유 hunk 또는 상태 delta만 포함해라. 해시·제외·잔여 WIP·다음 ID/담당/프롬프트를 남기고 멈춰라. push·배포·환자 자동진단·치료·자침 추천/시뮬레이션은 금지한다.
명세 work/tasks/T65.md. 선행: T91 및 모든 기능이상 설명 batch.
동결한 전신 근육 구조/기시정지/기능/대표 움직임과 전신 신경 조사/주행/지배근/포착·수준별 설명의 연결을 통합 감사한다. coverage 수치와 실제 지역별 화면을 모두 검증한다. 미해결/근거 없음은 정확히 표시하고 전신 완료로 과장하지 않는다. 평가/경혈/치료 기능은 별도 보류한다.
다음 기본 ID는 T40. 단, 미완 batch가 있으면 새 정수 ID의 실제 queue를 따른다. 다음 task는 실행하지 마라.
```

## T40 — 구조·기능 로컬 전달과 Git 체크포인트

```text
HUMAN ATLAS에서 T40만 수행해라. 담당 Luna Max.
AGENTS.md와 R15 13/14/15, 16-ASTRA-UI-HANDOFF.md, 최신 19-ALL-MUSCLES-BEFORE-NERVES.md 및 20-SERIAL-PROMPTS-FULL-SCOPE.md(설계 폴더 design/2026-09-25-muscle-atlas/), STATUS/R15 registry, 해당 task 명세와 선행 실제 report/manifest/evidence를 읽어라. 19/20의 T77 이후 순서가 이전 프롬프트보다 우선한다. 정확히 요청된 ID만 수행하고 자동 다음 실행은 하지 마라. 시작 HEAD/status/source hash를 기록하고 기존 WIP·원본/OpenSim_Models·역사 freeze를 보존해라. 실제 source/근거 없이 이름·좌표·형상·승인을 만들지 마라. AI가 조사/대조/표 작성을 수행하며 사용자에게 기본 해부학 조사 숙제를 넘기지 마라. source provenance와 license/human-review는 내부에 보존하고 learner에 JSON/task/보완자산 구분을 노출하지 마라. 로딩의 로고·인체 그림·슬로건을 복구하지 말고 단일 scene/camera와 미니멀 UI를 유지해라. 모든 target coverage gate는 동결한 전체 분모로 판정하고 필수 누락을 passed_with_gaps로 덮지 마라. 실제 의존 gate가 미달이면 해당 후속 단계를 시작하지 말고 bounded 수정 task와 해소 조건을 남겨라. 범위에 맞는 검사·실제 화면 검증과 report/evidence/STATUS/taskStatuses를 남겨라. 소유 변경만 staged diff 확인 후 로컬 커밋하며 혼합 WIP는 소유 hunk 또는 상태 delta만 포함해라. 해시·제외·잔여 WIP·다음 ID/담당/프롬프트를 남기고 멈춰라. push·배포·환자 자동진단·치료·자침 추천/시뮬레이션은 금지한다.
명세 work/tasks/T40.md. 선행: 실행 queue의 직전 필수 gate.
T47 실제 결과 기준으로 실행/설치/자료 추가/검증/복구 안내와 로컬 전달 빌드를 만든다. 평가·퀴즈 구현을 이번 전달의 필수 선행으로 두지 않는다. 재현 가능한 checkout과 asset 확보 방법을 검증한다.
 기존 세부 수행 범위는 유지하되 R15 동일 전신 scene/근육 표면 변형/명확한 CTA/신경 우선 순서를 적용한다. 이전 별도 시범 모델 허용은 폐기하며 아래 이전 next/prerequisite 문구는 R15 queue로 대체한다.
다음 기본 ID는 없음. 단, 미완 batch가 있으면 새 정수 ID의 실제 queue를 따른다. 다음 task는 실행하지 마라.
```

평가/경혈 예약 프롬프트는 18 문서에 남겨두지만 별도 사용자 착수 요청까지 실행하지 않는다.
