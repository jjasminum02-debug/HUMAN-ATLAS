# MV2·AT 통합 실행 계획

2026-10-12 Q03 중단 재검토. 새 task 번호·새 원장·새 엔진을 만들지 않는다.
현재 프롬프트는 [PROMPTS-IN-ORDER.md](PROMPTS-IN-ORDER.md) 한 곳에서 관리한다.
바로 실행할 것은 [Q03 / Sol xhigh](NEXT-MV2-Q03.md)다. 실제 상태는 EXECUTION과 최종 evidence가 기준이다.

## 현재 기준선

- 확인 HEAD `88cfb15d4ea9bec54d61d29061f3d0b4ba176e0b`: Q03 partial 기록.
- Q01 engineering·q01-learning-quality·Q02 완료. Q03 3 / Q04 26 / Q05 2매핑 미완. Q03의 이번 전체 주기 검증은 0건이다.
- Q03은 자세 관찰 경로에 등록돼 있으므로 근육 작용 검색 0건은 자료 부재가 아니다. 현재 코드를 호출해 좌우 source의 옵션 297/298/299와 기존 disclosure 경로를 확인했다. 실제 browser 합격은 아직 주장하지 않는다.
- AT1–7/20–22 완료, 다음 AT는 AT8. 명부 361개/예정 670 instance와 실제 표시 범위는 구분한다.
- 미커밋 WIP가 있다는 이유만으로 재개를 막지 않는다. 실제 동시 writer가 확인된 경로만 충돌을 피한다.

## 가장 짧은 완료 경로

**Q03 Sol 수정·검증 → Q04/Q05 Luna 검사 → 필요한 실제 잔여만 Sol 수정·종료 → AT8.**
Luna 단계에서 필수 큐/회귀가 다 통과하면 마지막 Sol 실행을 생략한다.
같은 GLB QC는 재사용하고, 매핑별 실제 형태는 관찰하며, 공통 runtime 복원 검사는 중복하지 않는다.
현재 통과 판정이나 기존 자산을 이번 계획 작성으로 변경하지 않았다.

## 코드에서 확인한 선행 작업

| 위치 | 현재 구현 | 배정 |
|---|---|---|
| `atlas-web/src/viewer/acupoints/learningPackage.ts` | `channel:'LU'`, 11개 개념/22개 상태 검사, `lung-r7.json`·폐경 관찰 context 고정 | **AT8 Sol xhigh**에서 공통 package 계약으로 확장 |
| `AcupointReview.tsx` | LU일 때만 실제 package 로드; allPoints도 폐경 데이터만 사용. 선택 side는 일부 경로에서 right/left만 허용 | AT8에서 경맥 registry·코드/side 식별·정중선·부분 package 합성을 공통 처리. 레이아웃 변경 금지 |
| `tour.ts`·관찰 context | LU 구간 정의와 일반 재생기가 함께 있음 | 경맥 구간·연결 순서는 데이터화. 기존 카메라 정책은 유지하고 실제 기준 구조 data만 추가 |
| `territoryMask.ts`·overlay | 양측 아래팔 LU mask와 공통 renderer가 있음. 사용하는 carrier와 LU 중심 로딩/가용성 연결이 남음 | **AT23 Sol xhigh**에서 다경맥 mask 등록·필요 carrier 로딩을 일반화. 점 위치 유무와 면 가용성 분리 |
| `sourceMotionRepairs.ts`·`plugins/motionAssets.ts` | Q02에서 exact base 기반 공통 예산 계약을 이미 통합 | 같은 계약을 재사용. 재구현/전역 제한 완화 금지 |

공통 compiler·단일 scene·mask renderer의 구조는 재사용한다. 경맥/근육/task별 loader와 UI를 복제하거나 완성된 기존 기능을 다시 만들지 않는다. 전수 재조사보다 **변경된 입력과 실제 예외**에 집중한다.

## 기본 순서와 모델

모델 배정은 현재 코드의 난이도에 대한 프로젝트 판단이다. 추론 설정은 정확성 인증이 아니며 합격 기준은 동일하다. 기존 실행은 Sol High로 마무리해도 된다. **다음 핵심 수정부터 Sol xhigh**, 반복 작업은 **Luna Max**를 권장한다.

| 순서 | 기존 ID / 내부 묶음 | 담당 | 끝내야 하는 결과 |
|---|---|---|---|
| 완료 | MV2 `q01-learning-quality` | 완료 보존 | `2d182a6` 근거 재사용 |
| 완료 | MV2 Q02 | 완료 보존 | `5b51ff6` 근거 및 공통 예산 계약 재사용 |
| 3 | MV2 Q03 | Sol xhigh | 이두근 3매핑의 팔꿈치/어깨 움직임·윤곽·부착 검증 및 실제 결함 수정 |
| 4 | MV2 Q04+Q05 검증 | Luna Max | 손 말단 26매핑/깊은 몸통 2매핑을 국소 관찰하여 실제 결함과 UI 문제 분리. 병렬 후보 결과가 있으면 재사용 |
| 5 | MV2 잔여 수정·종료 | Sol xhigh | 고정된 실제 잔여를 공통 원인별로 해결하고 영향 회귀·전체 종료. Luna에서 모두 통과하면 생략 |
| 6 | AT8 | Sol xhigh | 공통 다경맥 package 연결 + LI/TE 43혈·양측 86 instance의 위치·구간 경로. LU 회귀 보존 |
| 7 | AT9 | Luna Max | HT/PC/SI 37혈·74 instance. 손바닥·견갑부·귀 주위의 실제 예외 구분 |
| 8 | AT10 | Sol xhigh | ST1–25 25혈·50 instance. 눈·얼굴·목·몸통 지표와 carrier 경계 |
| 9 | AT11 | Luna Max | ST26–45/SP 41혈·82 instance. ST25/26 구간 연결도 대조 |
| 10 | AT12 | Sol xhigh | BL1–35 35혈·70 instance. 눈·두피·척추·천골 지표 |
| 11 | AT13 | Luna Max | BL36–67 32혈·64 instance. 번호로 하지라고 가정하지 말고 등 쪽 분지 포함 |
| 12 | AT14 | Luna Max | KI/LR 41혈·82 instance. KI는 족소음신경이며 nerve 작업이 아님 |
| 13 | AT15 | Sol xhigh | GB1–20 20혈·40 instance. 귀·두피 촘촘한 지표와 가림 |
| 14 | AT16 | Luna Max | GB21–44 24혈·48 instance. GB20/21 연결과 몸통·하지 가쪽 |
| 15 | AT17 | Sol xhigh | CV1–24 정중 24 instance. CV1은 해당 표면을 확인하며 다른 곳에 옮겨 찍지 않음 |
| 16 | AT18 | Sol xhigh | GV1–28 정중 28 instance. 구강·잇몸 등 특수 표면 예외 |
| 17 | AT19 | Sol xhigh | LU 포함 361개/670 instance의 검색·표시·side·경로·정밀도 대조 및 실제 누락 보완 |
| 18 | AT23 | Sol xhigh, 자료 후보는 Luna | 공통 다경맥 영역 로딩 + LU/LI/HT/SI/PC/TE 6개 전체 범위. 기존 LU 아래팔 부분은 보존·확장 |
| 19 | AT24 | Luna Max; 공통 기하 결함이면 Sol | ST/SP/KI/LR 4개 영역. 위경 폭은 구간별 근거·경계로 수정 |
| 20 | AT25 | Luna Max; 공통 기하 결함이면 Sol | BL/GB 2개 영역. 등·머리·볼기·하지 이음/중첩 검증 |
| 21 | AT26 | Sol xhigh | CV/GV 학습 강조 면 + 기존 제어에서 14영역 비교·선택 강조. 임독맥을 경근으로 창작하지 않음 |
| 22 | AT27 | Luna Max | 교재 importer·코드 연결·기존 카드 설명. 교재 미제공은 해당 내용만 미완으로 남김 |
| 23 | AT28 | Luna Max; 공통 lifecycle 결함은 Sol | 기존 화면의 검색·선택·따라보기·양측·정중·움직임 복귀·반응형 기능 회귀 |
| 24 | AT29 | Sol xhigh | 실측 lazy load/30회 전환/취소·해제/최종 learner 산출물 격리 및 범위 보고. 실제 배포 안 함 |

**MV2 완료는 모든 근육의 새 애니메이션 제작 완료가 아니다.** 이미 조사한 동작의 정해진 결함·모호성 큐와 q01 표현을 정리하는 범위다. AT29도 정밀 피부 혈위 인증·교과서 전문 입력·공개 재배포 완료를 뜻하지 않는다.

## 산출물과 종료 기준

작업 시간은 중단 조건으로 쓰지 않는다. 묶음의 원인/경맥 package를 끝내고 검증·로컬 커밋 후 멈춘다. 실제 해결 불가능한 지표/표면이 남으면 코드·side·carrier·시도·다음 필요한 입력을 남긴다. 같은 실패 로그만 반복하거나 새 번호를 발급하지 않는다.

### MV2

- 기존 Q01 engineering 통과와 새 learning-visual 판정을 독립 기록한다. 사용자 승인/교수 검토가 없다는 이유만으로 정상적인 로컬 구현을 막지 않는다.
- 최종 emitted GLB의 source/frame/side/clip과 실제 앱 로더를 일치시킨다. 준비·작용·복귀/중간 프레임/양측/주변 구조를 1배속 및 필요한 느린 재생에서 확인한다.
- 원인 수정은 offline authoring에 두고 runtime은 공통 재생·교체 경로를 사용한다. 전체 scale·숨김·각도 축소·기준 완화로 돌출을 감추지 않는다.
- Q04/Q05에서 정상 변형을 국소 관찰로 확인한 뒤 자동 framing만 부족하면 `presentation_deferred_to_ui`로 분리한다. 관찰 자체가 불충분하면 `observed_ambiguous`다.
- 큐의 모든 mapping이 판정되고 실제 기능/변형 결함이 해결돼야 MV2 scoped acceptance를 닫는다. UI 보류 수·선택적 human review는 별도 기록하며 전부 pass로 합치지 않는다. 확인된 결함이 0이고 통합 회귀만 남았다면 그 회귀로 종료하며 억지 새 수리를 만들지 않는다.

### AT8–19

- AT8에서 package registry/검증기/선택 데이터 경로를 공통화한다. LU 이름 검증은 LU 회귀 fixture로 유지하고 전체 validator를 LU에 묶어 두지 않는다. CV/GV는 코드당 정중 1 instance이며 임의의 좌우 복제 금지다.
- ST/BL/GB처럼 두 task에 나뉜 경맥은 **서로 덮어쓰지 않는 partial package**를 합성한다. 키는 code+side이며 conflict/중복/구간 이음을 검사한다. 숫자상 다음 혈을 직선으로 연결하지 않는다.
- worker가 만드는 사실/위치 규칙, 실제 native 지표·triangle 주소, compiler 결과, 앱 표시를 구분한다. 명부·자료 표 작성만으로 task complete 처리하지 않는다.
- AT6의 교육용 지표 작성 방법을 재사용한다. 교육용 근사를 근거 있게 결정할 수 있으면 구현한다. 피부 정밀도 미확정이나 교수 검토 없음이 자동 전체 차단은 아니다. 반대로 실제 표면/지표가 없으면 허위 좌표를 채우지 않는다.
- 각 instance의 코드/side/주소/표시/선택/가용성을 전수 검사한다. 시각 검증은 각 구간·양측·시작/끝·모든 예외를 실제 앱에서 수행하고 sample 수와 전수 검사 수를 분리한다.
- 누락이 있더라도 공통 계약이 정상인 독립 경맥의 자료 준비까지 막지 않는다. 해당 task는 partial로 보존하고 AT19에서 정확한 미완 합계를 확인한다. '361 목록 있음'으로 '361 위치 완료'를 대체하지 않는다.

### AT23–29

- 면은 점/선과 별도 data package다. 점에서 일정 반경으로 넓힌 tube를 경근 영역으로 간주하지 않는다. 원본 그림/문헌의 확인 범위와 AI 경계 제안을 나누고 보이지 않는 뒤쪽을 임의 복제하지 않는다.
- 동일 carrier의 position/normal은 공유하고 mask는 index/weight/outline만 소유한다. 경계 수정이 point/route hash를 바꾸지 않아야 한다. 공통 편집기·mask renderer를 재사용한다.
- 영역을 보는 데 필요한 carrier는 **영역의 참조 집합**으로 로드한다. 점이 아직 없다는 이유로 검증된 면까지 영구 차단하거나 가짜 point를 만들지 않는다. 모드가 바뀌면 기존 취소·해제 정책을 따른다.
- AT27은 새 카드 디자인 작업이 아니다. 기존 카드에 확인된 한글 콘텐츠를 연결한다. private 원문·판본/쪽·검증 기록은 학습 화면과 bundle에서 분리한다.
- 전체 경혈/영역 사용량이 늘 때마다 비용을 측정한다. AT29까지 문제를 미루지 않는다. 필요 chunk만 lazy load, carrier 중복 해제 방지, 선택/전환 cancellation을 유지한다. 수백 점/label 때문에 실제 draw·DOM 비용이 커지면 공통 batching/label 갱신을 측정 결과에 따라 개선한다.
- 전신 물리 엔진·대형 신규 프레임워크·경맥별 컴포넌트 복제는 금지한다. 실패 후보·원본·전체 evidence는 보존하되 제품 번들에는 compact 승인 projection만 포함한다.

## 이번에 하지 않을 UI 작업

카메라 거리/자동 회전/줌 연출/패널 배치/보기옵션/색상 테마/홈·로딩/브랜딩 개편은 사용자 후속 요청까지 보류한다. 이미 구현된 AT7 동작을 롤백하지 않는다. 새 점에 기존 카메라가 사용할 실제 국소 구조 context를 제공하는 것은 데이터 연결이다. camera controller의 정책·거리·연출을 바꾸는 작업과 구분한다.

기능 추가에 필요한 최소 데이터 바인딩과 실제 입력·취소·선택·복귀 결함 수정은 계속한다. 디자인상 불편은 코드/재현/화면과 함께 후속 UI 목록에 기록한다. AT26/27은 기존 제어·카드의 기능 연결, AT28은 현재 UI의 기능 회귀로 한정한다. 사용자 요청으로 미룬 UI 개편을 이 작업들의 필수 미완으로 취급하지 않으며 **UI 최종 완성이라고도 선언하지 않는다.**

## 병렬 실행과 사용 방법

기본은 위 표대로 한 번에 한 task/unit이다. 속도가 필요하면 [병렬 지침](PARALLEL.md)에 따라 **자료 후보/검증 1–2명 + 통합자 1명**으로 제한한다. 공유 코드·EXECUTION·최종 report·Git index에는 통합자만 쓴다. 다른 task의 후보 준비는 그 task 완료가 아니다.

- Q01/Q02 완료를 재실행하지 않는다. 현재는 [순서별 프롬프트](PROMPTS-IN-ORDER.md) 1번 Q03부터 시작하며, 이후 최신 실제 결과에 따라 2번/필요한 3번을 사용한다.
- MV2 필수 수정이 진행되는 동안 AT의 독립 자료 준비는 가능하다. 실제 앱 통합을 둘이 같은 작업트리에서 동시에 하지 않는다.
- MV2의 unresolved가 완전히 독립된 입력 부재로 남는다면, 그 상태를 숨기지 않은 채 안정된 AT 작업을 진행할 수 있다. 무조건 모든 AT를 막는 전역 승인 대기를 만들지 않는다.
- 동시 작업을 원하지 않으면 별도 준비/통합 호출 없이 각 AT를 끝까지 한 번 실행하면 된다. 모든 task를 의무적으로 둘로 쪼개지 않는다.
- 후속 실행자는 최신 EXECUTION과 실제 입력 hash를 다시 확인한다. 이 문서의 과거 수치나 후보 경로를 최종 상태로 고정하지 않는다.
