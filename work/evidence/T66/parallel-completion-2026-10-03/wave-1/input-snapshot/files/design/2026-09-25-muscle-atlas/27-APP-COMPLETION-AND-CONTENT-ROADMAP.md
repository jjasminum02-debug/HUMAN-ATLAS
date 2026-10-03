# 앱 완성과 콘텐츠 확장의 분리

2026-10-01 · 사용자가 기준·순서·프롬프트 개정을 명시적으로 승인함.
계획 개정이며 앱 구현 또는 task 합격 증거가 아니다.

## 1. 현재 효력과 목표

목표는 학습자가 정확하고 편안하게 쓸 수 있는 앱이다. 모든 해부 용어의 세부 형상과 직접 인용을 확보하는 일을 앱 개발 종료의 일괄 선행 조건으로 두지 않는다.

현재 실행 상태·순서는 `work/EXECUTION.json`, 완료 의미는 이 문서와 해당 task의 `acceptanceContract`, 실행 지시는 `promptFile`이 기준이다. 이 개정은 25·26 설계, 기존 task 명세, AGENTS의 충돌 문구보다 우선한다. 역사 보고서·검증·freeze는 당시 판정으로 보존한다. 과거 partial을 소급 passed로 바꾸지 않는다.

다음 실행은 T100이다. 이번 계획 수정만으로 T100/T80/T58을 합격 처리하거나 실행하지 않는다. 새 번호·새 스레드·자동 위임을 만들지 않는다. 요청당 한 ID를 실행하고 완료 후 멈춘다.

## 2. 서로 다른 세 상태

| 상태 | 의미 | 진행 조건 |
|---|---|---|
| task acceptance | 이번 task가 맡은 제품 기능·검증을 끝냈는가 | 해당 acceptanceContract 충족 시 passed |
| product readiness | 현재 지원 범위의 앱을 실제로 안정적으로 사용할 수 있는가 | T100 통합 → T80 사용 감사 → T58 화면·성능 |
| content completeness | 전체 542 target/563 membership의 형상·명칭·범위·근거 확보 수준 | 실제 수치와 null/미확정을 계속 보고; 앱 task 합격과 독립 |

`passed`는 명시한 로컬 제품 범위의 완료다. 해부학 전체 확보·사람 승인·공개 배포 허가를 뜻하지 않는다. T100이 새 기준으로 passed여도 `contentCompleteness=partial`을 유지할 수 있다. source-only, HA canonical binding, 공개 권리, 사람 검토는 각각 독립이다.

분모 542/563/12, 기존 HA 연결 130개, 역사 163 분류(6/20/135/2)는 보존한다. 후보 부재를 실제 geometry 부재로 바꾸지 않는다. 새로운 링크·정합·이름을 근거 없이 만들지 않는다. 130개는 기존 연결의 보존 기준이지 모든 로컬 typed 선택에 HA ID를 강제하는 제한이 아니다.

## 3. 제품 범위와 콘텐츠 원장

T100에서 현재 runtime/overlay와 실제 UI로 `work/product-scope.json`을 생성한다. 이후 T80에서 감사하고 T58에서 재사용한다. 이 계획 단계에서는 지원 target ID를 추정하여 미리 생성하지 않는다.

- 전체 542 target와 563 membership을 disposition 원장에 남긴다. 전수 disposition은 기존 원장을 재사용하는 데이터 감사이며 모든 행의 새 조사·스크린샷을 요구하지 않는다.
- 제품 지원 집합은 현재 앱에서 접근 가능한 검증된 명명 구조/구성원과 유효한 선택 경로 전체로 정한다. 합격을 위해 임의로 일부 쉬운 target만 골라 분모로 만들지 않는다. source object identity, side, 표시 이름과 표시 범위가 일치해야 한다.
- 지원 scope는 `whole_structure`, `explicit_part`, `declared_member_set`, `source_observation` 등을 구분한다. 하나의 member 경로를 그룹 전체 표면 합격으로 세지 않는다. 부분이나 그룹은 실제 제공 범위를 정확히 표시하면 사용할 수 있으며 미제공 구성원은 내부 원장에 남긴다.
- exact 근거가 없는 세부 target은 미지원/미확정으로 남긴다. 기존 전체 근육/뼈의 유효한 경로까지 함께 막지 않는다. 학생 화면에는 잘못된 parent 대체 선택을 제공하지 않는다. 미지원 작업은 필요한 위치에서 짧은 사용 안내를 제공하되 내부 ID·evidence/review 용어를 노출하지 않는다.
- source-only 자체는 로컬 관찰 금지가 아니다. 좌우·이름·범위·지역 배치가 검증된 경우 기존 typed card/선택을 허용하며 canonical HA 승인으로 세지 않는다.
- BP3D 13개처럼 ZA와의 공통 공간 정합이 미확정인 표면은 일반 학습 경로에서 잘못된 위치로 노출하지 않는다. 개발 관찰용 별도 상태로 격리하고 기존 single-scene/controller를 재사용한다. 새 검수용 제품 viewer를 만들지 않는다. 후속 정합 전까지 콘텐츠 확장 보류로 두며 이 자료를 반드시 통합해야 T100을 끝낼 수 있다는 조건은 폐기한다.
- 일반 사용자 지원 집합과 개발 관찰 집합의 route 수를 따로 보고한다. 계획 시점 mixed route 415/433은 전체 해부학 합격 또는 일반 사용자 지원 범위가 아니다. 격리로 learner route 수가 감소하면 실제 변화와 사유를 적으며 역사 415/433을 조작하지 않는다.

권장 `product-scope.json` 필드: `schemaVersion`, `contractRevision`, `sourceHashes`, `denominators`, `supportedTargetIds`, `supportedMemberships`, `representedScopeByTarget`, `observationOnlySources`, `quarantinedSources`, `unsupportedDispositionRef`, `learnerRouteCounts`, `inspectionRouteCounts`, `contentCompleteness`. 공통 builder/router로 생성하며 수동 카운트 복사나 새 대형 ledger 중복을 피한다.

## 4. 실제 차단 결함과 확장 항목

### 제품을 막는 결함

- 앱 실행/로딩 실패, 검은 화면, uncaught 오류, 무한 대기 또는 교체 실패.
- 지원한다고 표시한 구조의 선택·카드 불일치, 잘못된 좌우·명칭·형상·위치, 부분을 전체로 오인시키는 UI.
- 기본 전신과 12부위의 탐색이 깨지거나 지역 필터가 무관한 표면을 보여 주는 문제. 머리/얼굴, 몸통/등, 양측 어깨·상완, 손발, 골반·샅, 척추·엉치 등 주요 맥락이 제품 관찰에서 접근 불가능한 경우. 기존 데이터가 지원하는 근육·뼈 맥락을 먼저 복구한다. 이 항목은 세부 변이·미세 분절 전부를 요구하지 않는다.
- 선택 강조·주변 흐림·반투명·숨김·격리·맞춤·undo/복원이나 검색·키보드·뒤/앞 탐색이 실제로 깨지는 문제.
- held/hard hold/user layer-off가 복원·검색·선택으로 우회되는 문제, 미정합 자료의 일반 학습 노출.
- 주요 화면에서 패널이 시야/조작을 막거나, 반복 탐색에서 리소스가 계속 증가하거나, 측정으로 확인된 버벅임/성능 회귀.

### 앱 종료를 일괄 막지 않는 콘텐츠 확장

- 경로 없는 127 target/130 membership, 직접 용어 근거 73행을 0으로 만들기.
- 실제 소스에 없는 변이, 세부 분절, 전체 그룹의 미확보 구성원. 전체 542개 원장에 보존하며 지원한다고 광고하지 않는다.
- 직접 사전 인용이 없는 합리적인 문맥 조합명. AI 조합과 직접 인용을 내부에서 구분하고 실제 명칭 충돌은 해결/격리한다.
- 모든 target의 새로운 전체 해부학 extent pass, 모든 membership의 개별 PNG. 자동 계약 전수 검사와 대표·변경·충돌 사례의 실제 시각 검증을 조합한다.
- 사람 검토 미수행, 공개 재배포 held, 관측 불가능한 GPU/VRAM/전체 프로세스 메모리. 관측 한계로 기록하며 가짜 측정치를 만들지 않는다.

누락이 주요 학습 흐름의 실제 공백을 만들면 T80의 제품 결함으로 처리한다. 어려운 항목이라는 이유만으로 확장으로 밀지 않는다. 반대로 새 임상/해부학 자료의 무제한 수집을 기존 UI 버그의 선행 조건으로 늘리지 않는다.

## 5. 종료 가능한 작업 순서

| 순서 | task | 맡는 일 | 종료 기준 |
|---|---|---|---|
| 1 | T100 · Luna Max | 기존 앱 통합 마무리, 지원 범위 원장, 미정합 자산 격리, 관찰·선택 경로 정리 | 현재 지원 구조의 유효한 route/card/정책, 기본 전신·12부위·핵심 controller 기능 동작; 콘텐츠 gap은 별도 backlog |
| 2 | T80 · Luna Max | 사용자가 겪는 누락·선택·명칭·지역 맥락 결함 감사와 수정 | 주요 학습 흐름의 제품 차단 결함 0; 전수 disposition 및 콘텐츠 backlog 분리; 같은 127개를 조사 없이 재차단하지 않음 |
| 3 | T58 · Astra, 현재 대화 | 화면 다듬기와 실제 성능 최적화 | 단일 scene/camera, 대표 화면과 390/1024/1440 흐름, 실제 cold/warm·render/cache 확인, 발견된 핵심 회귀 수정 |
| 4 | T81 → T82 · Luna Max | 현재 앱의 지원 근육에 기시·정지·짧은 신경 정보를 연결하고 감사 | 실제 카드 텍스트·근거·미지원 처리 일치; 전체 source 연구 완료와 분리 |
| 5 | T83 → T84 · Luna Max | 한글 기능 설명을 연결하고 감사 | 작용/조건/갈래 의미, 화면 가독성, text와 clip 지원 분리 |
| 6 | T61 → T62 → T63 → T90 → T65 | 신경 계약·자료·주행·화면·설명을 완성 | task별 지원 범위를 검증하고 미확보는 명시; 전 신경 확보를 첫 기능의 선행 조건으로 두지 않음 |
| 7 | T35 → T59 → T25 → T66 → T85 | 움직임 계획·실제 변형/재생·파일럿·family 확장·품질 완성 | 실제 변형·scene 연속성; 전체 근육 애니메이션 완성 전에도 검증된 기능 사용 가능 |
| 8 | T40 | 실행 가능한 로컬 앱 전달 | 실제 실행 절차·최종 제품 상태·남은 콘텐츠·권리 한계 전달 |

T98/T99는 이미 완료한 입력이며 다시 실행하지 않는다. 새 ID를 발급하지 않고 기존 G3/G4의 반복적인 조사 batch·등록·검수 단계를 아래처럼 내부 unit으로 흡수했다. 향후 실행은 32개에서 18개 제품 작업으로 정리했다. 흡수된 task는 완료가 아니며 이전 실행 record/spec/report/evidence를 보존한다.

| 실행 task | 흡수하는 이전 task | 책임 |
|---|---|---|
| T61 | T86 | 신경 inventory/지원 범위/계약 |
| T62 | T87, T88 | 신경 자료 조사·등록 |
| T63 | T89 | 신경 주행 공통 구현·확장 |
| T65 | T64, T91 | 기능 변화 설명·접힌 정보·통합 |
| T59 | T60 | 실제 근육 변형과 player/CTA |
| T66 | T27, T28, T45, T46, T29, T31 | 소흉근/견갑대 family 준비·제작·학습 연결·내부 감사 |
| T85 | T47 | 지원 motion/구조/설명의 최종 감사 |

모든 미래 task에도 제품 지원 범위와 전체 콘텐츠 completeness를 분리하는 원칙이 적용된다. task별 구조/기능/신경/clip 의미 검증은 유지하되 과거의 전수 자료 확보·10개마다 강제 종료 문구는 이 개정에 맞춰 해석한다. task 수 축소는 실제 clip 제작 시간을 보장하는 약속이 아니다.

T100/T80/T58은 서로 다른 책임이다. 다음 task가 맡을 UI polish·성능 목표를 앞 task의 새 의무로 추가하지 않는다. T80에서 새 exporter 등 실제 선행 결함을 발견하면 근거와 영향 범위만 지정하여 해당 결함을 고친다. 기존 전체 콘텐츠 gap 목록만으로 과거 passed를 일괄 취소하지 않는다. 새 회귀는 현재 task에서 처리하고 task scope 밖의 큰 개편은 별도 요청으로 남긴다.

## 6. 콘텐츠 확장 backlog와 재개 조건

`work/content-backlog.json`은 기존 final-blocker-list/원장을 참조하는 작은 색인이다. 개별 anatomy 근거를 다시 복사하지 않는다. 항목군은 exact correspondence 43, variant 21, group extent 20, part segmentation 31, explicit side 12와 직접 용어 근거 73, BP3D 정합 13을 시작 관찰값으로 유지한다. 현재 분류와 counts는 실행 시 재검증한다. 역사 163 분류와 독립이다.

각 미지원 항목은 필요 source/분절/정합/명칭 근거, 현재 표현 범위, 실제 사용자 영향, 다음 행동·재개 조건을 가진다. 새로운 실제 자료/locator/segmentation evidence, 특정 구조 추가의 사용자 요청, 또는 T80에서 확인한 주요 제품 공백이 있을 때 관련 항목만 재개한다. 새 단서 없는 고정 catalog 재검색은 하지 않는다. 배치 크기는 내부 복구 단위이며 새 task 발급/전체 빌드/사용자 재입력의 이유가 아니다.

## 7. 검증과 실행 상태

자동 검사: 현재 실제 runtime의 route/side/region/name/정책을 전수 확인한다. 시각 검사: 12부위와 주요 구조/선택 유형·모바일 폭·변경 사례를 기존 근거와 실제 browser로 확인한다. 기존 C3 overview는 국소 강조 합격으로 세지 않는다. 입력 동일성/영향 분석이 있으면 기존 증거를 재사용하며 새 hash가 필요하면 한 번 새 기준선을 잡는다.

공통 코드/schema/loader 변경 후 관련 회귀·typecheck/build, 데이터만 바꾸면 해당 builder/contract 검사를 한다. 최종 제품 검증은 task당 한 번 실행한다. 실패·새 수정이 없으면 동일 suite/PNG/보고서를 반복하지 않는다. 자동 성공만으로 실제 UI 성공을 선언하지 않는다.

T58은 cold/warm과 실제 renderer 시간, frame interval, draw/triangle/geometry bytes, 반복 지역 전환 후 cache 안정성을 측정하고 큰 비용부터 최적화한다. 기존 20MiB overview/8MiB chunk/1M active triangles/96MiB CPU geometry는 공학 목표로 유지한다. 제품에 필요한 품질·장치 조건을 근거로 예산 조정이 필요하면 측정 전후·이유를 기록해 변경하며 기준을 몰래 올려 통과시키지 않는다. desktop 390px 검사를 실기기 모바일 합격으로 부르지 않는다.

task passed 기록에는 `acceptanceScope`, `contractRevision`, `productReadiness`, `contentCompleteness`, `knownContentGaps`, `unresolvedProductBlockers`, 실제 evidence가 있어야 한다. 콘텐츠 gap만 남고 해당 제품 계약을 만족하면 `executionStatus=completed`, `acceptance=passed`, `nextUnit=null`로 종료한다. 이때 전체 해부학 완료라고 쓰지 않는다. 실제 제품 차단 결함이 남으면 해당 task partial이고 실패 기능만 재개한다.

## 8. 보존과 이번 계획의 한계

OpenSim_Models, T13, 원본 mesh/archive/cache, 기존 WIP, 역사 freeze·보고·분류는 보존한다. private 자료를 upload하거나 source/public rights/human review를 승격하지 않는다. 학생 UI에 task/JSON/검토 원장을 노출하지 않는다. 표정근 animation, 신경3D, 새 움직임, 환자 진단·치료·자침 시뮬레이션은 지정 task 이전에 추가하지 않는다. push/배포는 이번 범위 밖이다.

이번 개정은 유한한 제품 작업을 가능하게 한다. 실제 앱은 후속 실행과 검증을 거쳐야 완료되며 현재 미검증 항목을 문서 수정으로 합격 처리하지 않는다.
