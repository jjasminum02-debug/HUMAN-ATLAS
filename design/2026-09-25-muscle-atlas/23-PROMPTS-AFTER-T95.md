# 현행 실행 순서와 프롬프트

자동 생성 · 원본: `work/EXECUTION.json` · `python3 work/tools/sync_execution.py --check`로 일치 검증.

이 파일의 과거 T95/T102 시점 안내는 Git 이력으로 보존된다. 현재 next는 [work/NEXT.md](../../work/NEXT.md)에서 확인한다. 완료한 과거 작업은 반복하지 않는다.

현재 기준은 `design/2026-09-25-muscle-atlas/27-APP-COMPLETION-AND-CONTENT-ROADMAP.md`와 task별 acceptanceContract/promptFile이다. task 합격과 전체 contentCompleteness를 분리한다. 기존 T105–109/T110–121/T166은 흡수된 역사이며 별도 실행하지 않는다. T122–165도 미실행 폐기 상태다.

## G1 — 현재 지원 범위의 앱 통합·사용 감사·UI/성능 완성

| ID | 담당 | 결과 |
|---|---|---|
| [T98](#t98) | Astra · current conversation (user-requested resolution) | 전신 source inventory·변환 검증·주 베이스 선택 |
| [T99](#t99) | Sol High | 공통 dataset compiler·일괄 변환·경량 로더 |
| [T100](#t100) | Luna Max | 현재 지원 범위 앱 통합 마무리 |
| [T80](#t80) | Luna Max | 앱 사용 흐름·주요 구조 감사와 결함 보완 |
| [T58](#t58) | Astra · 현재 대화 직접 구현 | 앱 화면·관찰 UX·실측 성능 완성 |

## G2 — 기시정지·기능·짧은 신경 정보

| ID | 담당 | 결과 |
|---|---|---|
| [T81](#t81) | Luna Max | 지원 근육 기시·정지·짧은 신경 정보 연결 |
| [T82](#t82) | Luna Max | 지원 구조 설명·카드 감사와 보완 |
| [T83](#t83) | Luna Max | 지원 근육 한글 기능 설명 연결 |
| [T84](#t84) | Luna Max | 지원 기능 설명·학습 흐름 감사 |

## G3 — 검증된 신경 자료·주행·설명 기능 제공

| ID | 담당 | 결과 |
|---|---|---|
| [T61](#t61) | Sol High | 신경 지원 범위·자료 inventory·공통 계약 |
| [T62](#t62) | Luna Max | 신경 자료 검증·공통 등록 |
| [T63](#t63) | Sol High | 같은 장면의 신경 주행·지배근 선택 |
| [T90](#t90) | Astra · 현재 대화 직접 구현 | 신경 그래픽·선택 품질 완성 |
| [T65](#t65) | Luna Max | 신경 기능 변화 설명·사용 흐름 완성 |

## G4 — 같은 모형 움직임 파일럿·재사용 확장·품질 완성

| ID | 담당 | 결과 |
|---|---|---|
| [T35](#t35) | Sol High | 같은 모형 움직임 지원 범위·제작 계획 |
| [T59](#t59) | Sol High | 앞정강근 실제 변형·공통 재생 연결 |
| [T25](#t25) | Luna Max | 첫 같은 모형 움직임 학습 흐름 완성 |
| [T66](#t66) | Luna Max | 움직임 family 재사용 확장·학습 연결 |
| [T85](#t85) | Astra · 현재 대화 직접 구현 | 지원 움직임·통합 앱 품질 완성 |

## G5 — 최종 로컬 전달

| ID | 담당 | 결과 |
|---|---|---|
| [T40](#t40) | Luna Max | 실행 가능한 로컬 앱 전달 |

## 붙여 넣기 — 한 번에 한 ID

<a id="t98"></a>
### T98 — 전신 source inventory·변환 검증·주 베이스 선택

```text
HUMAN ATLAS에서 T98만 수행해라. 담당 Astra · current conversation (user-requested resolution).
AGENTS.md, work/EXECUTION.json, work/NEXT.md, 최신 STATUS의 generated execution 블록,
design/2026-09-25-muscle-atlas/27-APP-COMPLETION-AND-CONTENT-ROADMAP.md와 해당 task 명세, 실제 선행 report/evidence/manifest를 읽어라.
26-T100-BULK-DELIVERY-PLAN.md의 공통 처리·예외 검토·앱 데이터 분리·변경별 검증 원칙을 적용한다. 고정 10개 처리 후 의무 종료하지 않는다. 역사 evidence는 보존한다.
EXECUTION이 현재 범위/순서의 유일한 원본이다. 역사 queue의 nextTask를 실행하지 마라. 24의 엑셀 검증·한글 기능·짧은 신경·표정근 motion 제외는 유지한다.
이번 범위: 25 설계 3절의 2026-09-29 Astra 정정을 따른다. T98은 전신 소스 inventory/목표 분모를 보존하고, 신뢰 가능한 exporter와 frozen 12개 표본 재현, exact Z-Anatomy source object, 단위·좌표 규약·정적 기준 자세, 권리 그룹과 보류 범위, 전체 source-system 비용으로 로컬 일괄 변환용 베이스를 선택한다. canonical 학습 연결·BP3D 형상 정합·앱 표시/공개 재배포·전신 제품 완료를 이 소스 선택과 혼동하지 않는다. 실제 입력은 work/evidence/T98/astra-resolution-2026-09-29/base-selection.json 및 validation.json이다. source-only/held/hidden/원본/사용자 WIP를 보존한다. 이 task에서 웹 runtime 또는 T99를 구현하지 않는다.
시작 HEAD/status/hash를 기록하고 원본/OpenSim_Models/사용자 WIP/T13 drafts/역사 freeze를 보존한다. source-only/권리/사람검토를 추정 승격하지 않는다.
25 설계의 T100 상태 교정에 따라 과거 not_approved_by_this_task·공개 재배포 held·humanReview 미수행을 로컬 개발의 일괄 차단으로 사용하지 마라. 담당 AI가 source-family 근거/예외와 객체·의미 대응을 검토하여 현재 overlay 결정을 기록하고 진짜 충돌 항목만 보류한다.
공통 도구와 단일 scene/renderer/camera를 재사용한다. 자동 전수처리와 내부 의미검증 unit을 구분하며 미완이면 같은 task/nextUnit으로 재개한다. 새 번호를 반복 발급하지 마라.
관련 실제 검증·progress·report/evidence를 남기고 EXECUTION의 해당 task record만 갱신한다. python3 work/tools/sync_execution.py와 --check로 투영 문서를 동기화한다.
소유 파일/hunk만 선별 로컬 커밋하고 해시·포함/제외·잔여 WIP·다음 프롬프트를 남긴 뒤 멈춰라.
기본 다음 ID: T99. 필수 gate 미달이면 먼저 같은 task를 재개하고 다음 task를 자동 실행하지 마라. push·배포·진단·치료·침 시뮬레이션 금지.
```

<a id="t99"></a>
### T99 — 공통 dataset compiler·일괄 변환·경량 로더

```text
HUMAN ATLAS에서 T99만 수행해라. 담당 Sol High.
AGENTS.md, work/EXECUTION.json, work/NEXT.md, 최신 STATUS의 generated execution 블록,
design/2026-09-25-muscle-atlas/27-APP-COMPLETION-AND-CONTENT-ROADMAP.md와 해당 task 명세, 실제 선행 report/evidence/manifest를 읽어라.
26-T100-BULK-DELIVERY-PLAN.md의 공통 처리·예외 검토·앱 데이터 분리·변경별 검증 원칙을 적용한다. 고정 10개 처리 후 의무 종료하지 않는다. 역사 evidence는 보존한다.
EXECUTION이 현재 범위/순서의 유일한 원본이다. 역사 queue의 nextTask를 실행하지 마라. 24의 엑셀 검증·한글 기능·짧은 신경·표정근 motion 제외는 유지한다.
이번 범위: T98 실제 exporter와 선택된 source snapshot이 선행이다. 25 설계4절대로 source adapter→공통 schema/검증→overview/detail chunk와compact catalog를 생성한다. 기존 BP3D subset 재현과 전체 frozen dataset 변환을 같은 파이프라인으로 검증한다. task별 TypeScript extension/parent-chain/plugin 분기를 추가하지 말고 revision당 검증한 generic manifest로 바꾼다. source namespace/object instance/shared geometry/개념 binding/frame/rest pose와hold를 독립 보존한다. 전신overview와 상세LOD, byte-budget LRU/pin/해제/취소를 구현하고 geometry추가당 runtime 코드0을 검증한다. 원본/역사 cache·freeze는 변경하지 않는다. T98 대표12개만 변환하고 전체compile 완료라 하지 않는다. 새 기준은 manifest·resource·정합·품질·성능 회귀로 검증하며 learner의 전체 이름/선택 연결은 T100에 맡긴다.
시작 HEAD/status/hash를 기록하고 원본/OpenSim_Models/사용자 WIP/T13 drafts/역사 freeze를 보존한다. source-only/권리/사람검토를 추정 승격하지 않는다.
25 설계의 T100 상태 교정에 따라 과거 not_approved_by_this_task·공개 재배포 held·humanReview 미수행을 로컬 개발의 일괄 차단으로 사용하지 마라. 담당 AI가 source-family 근거/예외와 객체·의미 대응을 검토하여 현재 overlay 결정을 기록하고 진짜 충돌 항목만 보류한다.
공통 도구와 단일 scene/renderer/camera를 재사용한다. 자동 전수처리와 내부 의미검증 unit을 구분하며 미완이면 같은 task/nextUnit으로 재개한다. 새 번호를 반복 발급하지 마라.
관련 실제 검증·progress·report/evidence를 남기고 EXECUTION의 해당 task record만 갱신한다. python3 work/tools/sync_execution.py와 --check로 투영 문서를 동기화한다.
소유 파일/hunk만 선별 로컬 커밋하고 해시·포함/제외·잔여 WIP·다음 프롬프트를 남긴 뒤 멈춰라.
기본 다음 ID: T100. 필수 gate 미달이면 먼저 같은 task를 재개하고 다음 task를 자동 실행하지 마라. push·배포·진단·치료·침 시뮬레이션 금지.
```

<a id="t100"></a>
### T100 — 현재 지원 범위 앱 통합 마무리

```text
HUMAN ATLAS에서 T100만 수행해라. 담당 Luna Max.

AGENTS.md, work/EXECUTION.json, design/2026-09-25-muscle-atlas/27-APP-COMPLETION-AND-CONTENT-ROADMAP.md, work/product-acceptance.json,
해당 task의 현재 spec/promptFile, 실제 선행 report/evidence를 읽어라.
목표는 현재 지원 범위에서 정확하고 안정적으로 사용할 수 있는 앱이다. task acceptance와 전체 콘텐츠 completeness를 분리한다.
27 설계/현재 acceptanceContract가 과거 전체 콘텐츠 0-gap·full extent 전수 PNG·10개마다 종료 문구보다 우선한다.
542 target/563 membership/12부위, 기존 HA 130, 역사163(6/20/135/2), 원본/OpenSim_Models/T13/기존 WIP를 보존한다.
source-only, 검증된 로컬 선택, humanReview=not_performed, 공개 권리 held를 독립적으로 유지한다.
지원한다고 표시한 구조의 wrong side/name/scope/placement와 실제 사용자 흐름 결함은 해결한다. 미지원 자료로 geometry/binding/승인을 만들지 않는다.
자동 계약 검사는 전수 수행하고 실제 시각 검증은 대표 유형·12부위·변경/충돌 사례에 집중한다. 동일 입력의 기존 근거는 영향 분석 후 재사용한다.
새 단서 없는 고정 catalog 검색·직접 용어 인용 검색·전체 suite/보고서 반복을 하지 않는다. 의미 검토 묶음은 내부 복구 단위다.
제품 계약을 충족하면 completed/passed, nextUnit=null로 종료하고 contentCompleteness=partial 및 남은 콘텐츠를 별도로 보고한다.
실제 제품 차단 결함이 남으면 실패 기능만 구체적으로 기록해 같은 task에서 고친다. 계획 문서만으로 pass하지 않는다.
해당 report/evidence와 EXECUTION record에 acceptanceScope/contractRevision/productReadiness/contentCompleteness/knownContentGaps/unresolvedProductBlockers를 기록한다.
합격 기록은 progress.productAcceptance에 contractRevision=app-completion-2026-10-01, acceptanceScope, productReadiness, contentCompleteness, knownContentGaps, unresolvedProductBlockers=[], evidence=[실제 보고서/검증 파일 경로]를 남긴다.
python3 work/tools/sync_execution.py 및 --check를 수행하고 소유 변경만 선별 로컬 커밋한다.
다음 task 자동 실행, 새 번호/스레드 발급, 자동 위임, push/배포, 임상 진단·치료·자침 기능은 금지한다.

이번 실행:
1. 최신 T100 보고서와 source-completion-2026-10-01/integration/final-validation-v9.json, final-blocker-list.json, 실제 mixed runtime/overlay를 읽는다. 계획 당시 ZA 409/542·427/563, mixed 415/542·433/563, BP3D 13개 공간 미확정이다. 숫자는 현재 입력에서 확인하며 기대값으로 강제하지 않는다.
2. work/product-scope.json을 공통 pipeline으로 만든다. 현재 유효한 지원 구조 전체를 포함하고 whole/part/member-set/source-observation 범위를 구분한다. 전체 542/563 disposition은 기존 원장을 참조한다. 조작한 작은 대상 집합으로 합격하지 않는다.
3. 공간 정합이 미확정인 BP3D 13개를 일반 학습 기본 표시·검색 선택·직접 target URL·뒤/앞 복원에서 일관되게 격리한다. 개발 관찰과 자료/관계 근거는 보존한다. 별도 제품 viewer를 만들지 않는다. 일반 learner routes와 inspection routes를 분리해 실제 counts를 보고한다. 이 항목을 모두 정합해야 끝나는 조건은 없다.
4. 기존 ZA와 검증된 로컬 경로에서 source identity, 명시 side, 세 이름, 지역, 카드·국소 강조, 반투명·숨김·격리·맞춤·undo/복원의 실제 오류만 수정한다. 그룹 member를 전체 그룹 형상이라고 표시하지 않는다. 실제 명칭 충돌은 보류하되 문맥 조합은 허용하고 직접 인용 73개 재검색을 하지 않는다.
5. 실제 runtime 경로/정책을 자동 전수 검사한다. 기존 증거의 입력·영향 동일성을 확인해 재사용하고 변경된 격리/선택 사례와 주요 흐름만 새 browser로 확인한다. 구형 C3 overview는 국소 강조 합격으로 세지 않는다. 공통 코드 변경 시 whole-body/search/delivery, typecheck/build 등 관련 검증을 마지막에 한 번 실행한다.
6. 이 task 계약을 충족하면 T100 completed/passed, nextUnit=null로 종료한다. contentCompleteness=partial과 기존 gap/권리/사람 검토는 그대로 남긴다. 문서만 바꾸어 통과하지 말고 실제 product-scope와 학습 노출 정책 검증 근거를 남긴다. 다음 T80은 실행하지 않는다.

종료 후 다음 ID는 T80다. 다음 promptFile을 안내하고 멈춰라. 다른 task를 이번에 시작하지 마라.
```

<a id="t80"></a>
### T80 — 앱 사용 흐름·주요 구조 감사와 결함 보완

```text
HUMAN ATLAS에서 T80만 수행해라. 담당 Luna Max.

AGENTS.md, work/EXECUTION.json, design/2026-09-25-muscle-atlas/27-APP-COMPLETION-AND-CONTENT-ROADMAP.md, work/product-acceptance.json,
해당 task의 현재 spec/promptFile, 실제 선행 report/evidence를 읽어라.
목표는 현재 지원 범위에서 정확하고 안정적으로 사용할 수 있는 앱이다. task acceptance와 전체 콘텐츠 completeness를 분리한다.
27 설계/현재 acceptanceContract가 과거 전체 콘텐츠 0-gap·full extent 전수 PNG·10개마다 종료 문구보다 우선한다.
542 target/563 membership/12부위, 기존 HA 130, 역사163(6/20/135/2), 원본/OpenSim_Models/T13/기존 WIP를 보존한다.
source-only, 검증된 로컬 선택, humanReview=not_performed, 공개 권리 held를 독립적으로 유지한다.
지원한다고 표시한 구조의 wrong side/name/scope/placement와 실제 사용자 흐름 결함은 해결한다. 미지원 자료로 geometry/binding/승인을 만들지 않는다.
자동 계약 검사는 전수 수행하고 실제 시각 검증은 대표 유형·12부위·변경/충돌 사례에 집중한다. 동일 입력의 기존 근거는 영향 분석 후 재사용한다.
새 단서 없는 고정 catalog 검색·직접 용어 인용 검색·전체 suite/보고서 반복을 하지 않는다. 의미 검토 묶음은 내부 복구 단위다.
제품 계약을 충족하면 completed/passed, nextUnit=null로 종료하고 contentCompleteness=partial 및 남은 콘텐츠를 별도로 보고한다.
실제 제품 차단 결함이 남으면 실패 기능만 구체적으로 기록해 같은 task에서 고친다. 계획 문서만으로 pass하지 않는다.
해당 report/evidence와 EXECUTION record에 acceptanceScope/contractRevision/productReadiness/contentCompleteness/knownContentGaps/unresolvedProductBlockers를 기록한다.
합격 기록은 progress.productAcceptance에 contractRevision=app-completion-2026-10-01, acceptanceScope, productReadiness, contentCompleteness, knownContentGaps, unresolvedProductBlockers=[], evidence=[실제 보고서/검증 파일 경로]를 남긴다.
python3 work/tools/sync_execution.py 및 --check를 수행하고 소유 변경만 선별 로컬 커밋한다.
다음 task 자동 실행, 새 번호/스레드 발급, 자동 위임, push/배포, 임상 진단·치료·자침 기능은 금지한다.

이번 실행:
1. T100이 새 계약으로 passed이고 product-scope.json과 실제 evidence가 있는지 확인한다. 과거 partial 보고서가 존재한다는 이유만으로 중단하지 않는다. 현재 지원 범위와 콘텐츠 completeness를 구분한다.
2. 전체 542 target/563 membership은 기존 disposition과 실제 runtime을 자동 대조한다. 이미 기록한 127개에 새 후보가 없으면 같은 catalog 검색을 반복하지 않는다. 경로/표현 범위/일반 learner 노출이 정확한지 검사한다.
3. 실제 브라우저에서 전신과 12부위, 합집합/전체 복귀, 이름 검색, 양측 전환, typed card, 국소 강조·주변 흐림, 깊은 구조의 격리/맞춤, 숨김/undo/복원, 뒤/앞 탐색을 연속 사용자 흐름으로 검사한다. 얼굴/광배근/양측 어깨·상완/손발/척추·엉치/골반 맥락은 기존 실제 지원 데이터로 확인한다. 표본마다 새 원장을 만들지 않는다.
4. 클릭되지 않는 유효한 표면, wrong side/card, parent를 exact part로 오인시키는 표시, 지역 맥락 손실, 격리 자료 재노출 등 실제 결함을 수정한다. 주요 부위 자체가 비어 있거나 핵심 조작을 할 수 없다면 제품 차단으로 처리한다. 어려운 결함을 콘텐츠 backlog로 바꿔 통과하지 않는다.
5. 선택 가능한 member가 있는 그룹은 그 제공 범위만 검증한다. 변이/미세 분절/미확보 구조는 정직하게 미지원으로 유지한다. 모든 542개의 full extent pass를 새로 만들 필요는 없다. 기존 side conflict는 근거 없이 해소하지 않는다.
6. 변경에 맞는 관련 회귀·타입·빌드 및 대표/변경 browser 사례를 확인한다. 제품 차단 결함이 없으면 T80 completed/passed, contentCompleteness=partial 허용으로 종료한다. UI polish·프로파일 결과·대표 캡처를 T58에 넘기고 자동 실행하지 않는다.

종료 후 다음 ID는 T58다. 다음 promptFile을 안내하고 멈춰라. 다른 task를 이번에 시작하지 마라.
```

<a id="t58"></a>
### T58 — 앱 화면·관찰 UX·실측 성능 완성

```text
HUMAN ATLAS에서 T58만 수행해라. 담당 Astra · 현재 대화 직접 구현.

AGENTS.md, work/EXECUTION.json, design/2026-09-25-muscle-atlas/27-APP-COMPLETION-AND-CONTENT-ROADMAP.md, work/product-acceptance.json,
해당 task의 현재 spec/promptFile, 실제 선행 report/evidence를 읽어라.
목표는 현재 지원 범위에서 정확하고 안정적으로 사용할 수 있는 앱이다. task acceptance와 전체 콘텐츠 completeness를 분리한다.
27 설계/현재 acceptanceContract가 과거 전체 콘텐츠 0-gap·full extent 전수 PNG·10개마다 종료 문구보다 우선한다.
542 target/563 membership/12부위, 기존 HA 130, 역사163(6/20/135/2), 원본/OpenSim_Models/T13/기존 WIP를 보존한다.
source-only, 검증된 로컬 선택, humanReview=not_performed, 공개 권리 held를 독립적으로 유지한다.
지원한다고 표시한 구조의 wrong side/name/scope/placement와 실제 사용자 흐름 결함은 해결한다. 미지원 자료로 geometry/binding/승인을 만들지 않는다.
자동 계약 검사는 전수 수행하고 실제 시각 검증은 대표 유형·12부위·변경/충돌 사례에 집중한다. 동일 입력의 기존 근거는 영향 분석 후 재사용한다.
새 단서 없는 고정 catalog 검색·직접 용어 인용 검색·전체 suite/보고서 반복을 하지 않는다. 의미 검토 묶음은 내부 복구 단위다.
제품 계약을 충족하면 completed/passed, nextUnit=null로 종료하고 contentCompleteness=partial 및 남은 콘텐츠를 별도로 보고한다.
실제 제품 차단 결함이 남으면 실패 기능만 구체적으로 기록해 같은 task에서 고친다. 계획 문서만으로 pass하지 않는다.
해당 report/evidence와 EXECUTION record에 acceptanceScope/contractRevision/productReadiness/contentCompleteness/knownContentGaps/unresolvedProductBlockers를 기록한다.
합격 기록은 progress.productAcceptance에 contractRevision=app-completion-2026-10-01, acceptanceScope, productReadiness, contentCompleteness, knownContentGaps, unresolvedProductBlockers=[], evidence=[실제 보고서/검증 파일 경로]를 남긴다.
python3 work/tools/sync_execution.py 및 --check를 수행하고 소유 변경만 선별 로컬 커밋한다.
다음 task 자동 실행, 새 번호/스레드 발급, 자동 위임, push/배포, 임상 진단·치료·자침 기능은 금지한다.

이번 실행:
1. T100/T80 새 계약의 passed, 실제 product-scope.json, T80 결함·개선 원장과 최신 UI를 확인한다. 오래된 전체 콘텐츠 gate나 역사 T57→T59 순서를 재실행하지 않는다. 담당 Astra, 현재 대화 직접 구현이며 자동 위임하지 않는다.
2. 현재 UI를 먼저 보고 화면의 큰 문제부터 수정한다. 단일 viewport/scene/camera, 밝은 배경, 뼈·근육 식별, 선택 대비, 카메라 프레이밍, 패널 가림, 깊은 구조 접근, 복원 예측 가능성에 집중한다. 제거한 로딩 로고/인체 그림/슬로건을 복구하지 않는다. 학생 화면에 source/task/evidence 메타데이터를 넣지 않는다.
3. 변경 전 한 번의 실제 프로파일을 잡는다. cold와 warm bytes/loading, render 호출 비용과 frame interval을 구분하고 active triangles/draws/CPU geometry, 20회 지역 전환 후 cache/취소/late-response 상태를 확인한다. GPU/VRAM/total-process 메모리 관측 불가는 한계로 기록한다.
4. 확인된 병목부터 lazy loading·경량 projection·캐시/LRU·중복 render·불필요한 state churn·패널 layout·LOD를 공통 경로에서 최적화한다. 실제 필요 없이 기술을 갈아엎거나 별도 viewer를 만들지 않는다. 구조 삭제/잘못된 좌우/무조건 품질 저하로 빠르게 만들지 않는다. 예산 변경은 근거와 품질 영향으로 명시하고 몰래 상향하지 않는다.
5. 1440/1024/390 실제 브라우저에서 전신·머리·손·하지/등 대표 시점, 검색·양측 선택·카드·키보드·뒤/앞·숨김/복원을 검증한다. 검은 프레임·로딩 실패·카메라 reset·overlap·console error와 성능 회귀를 수정한다. desktop 390px를 모바일 실기기 검증으로 부르지 않는다.
6. 최종 관련 회귀/typecheck/build와 영향받는 실제 흐름을 한 번 검증하고 변경 전후 수치·PNG·한계를 남긴다. 제품 차단 결함 없이 지원 앱이 안정적으로 사용 가능하면 T58 completed/passed 및 local_app_ready를 기록한다. 전체 해부학 완료나 공개 배포 승인을 뜻하지 않는다. 다음 T81은 자동 실행하지 않는다.

종료 후 다음 ID는 T81다. 다음 promptFile을 안내하고 멈춰라. 다른 task를 이번에 시작하지 마라.
```

<a id="t81"></a>
### T81 — 지원 근육 기시·정지·짧은 신경 정보 연결

```text
HUMAN ATLAS에서 T81만 수행해라. 담당 Luna Max.

AGENTS.md, work/EXECUTION.json, design/2026-09-25-muscle-atlas/27-APP-COMPLETION-AND-CONTENT-ROADMAP.md, work/product-acceptance.json,
해당 task의 현재 spec/promptFile, 실제 선행 report/evidence를 읽어라.
목표는 현재 지원 범위에서 정확하고 안정적으로 사용할 수 있는 앱이다. task acceptance와 전체 콘텐츠 completeness를 분리한다.
27 설계/현재 acceptanceContract가 과거 전체 콘텐츠 0-gap·full extent 전수 PNG·10개마다 종료 문구보다 우선한다.
542 target/563 membership/12부위, 기존 HA 130, 역사163(6/20/135/2), 원본/OpenSim_Models/T13/기존 WIP를 보존한다.
source-only, 검증된 로컬 선택, humanReview=not_performed, 공개 권리 held를 독립적으로 유지한다.
지원한다고 표시한 구조의 wrong side/name/scope/placement와 실제 사용자 흐름 결함은 해결한다. 미지원 자료로 geometry/binding/승인을 만들지 않는다.
자동 계약 검사는 전수 수행하고 실제 시각 검증은 대표 유형·12부위·변경/충돌 사례에 집중한다. 동일 입력의 기존 근거는 영향 분석 후 재사용한다.
새 단서 없는 고정 catalog 검색·직접 용어 인용 검색·전체 suite/보고서 반복을 하지 않는다. 의미 검토 묶음은 내부 복구 단위다.
제품 계약을 충족하면 completed/passed, nextUnit=null로 종료하고 contentCompleteness=partial 및 남은 콘텐츠를 별도로 보고한다.
실제 제품 차단 결함이 남으면 실패 기능만 구체적으로 기록해 같은 task에서 고친다. 계획 문서만으로 pass하지 않는다.
해당 report/evidence와 EXECUTION record에 acceptanceScope/contractRevision/productReadiness/contentCompleteness/knownContentGaps/unresolvedProductBlockers를 기록한다.
합격 기록은 progress.productAcceptance에 contractRevision=app-completion-2026-10-01, acceptanceScope, productReadiness, contentCompleteness, knownContentGaps, unresolvedProductBlockers=[], evidence=[실제 보고서/검증 파일 경로]를 남긴다.
python3 work/tools/sync_execution.py 및 --check를 수행하고 소유 변경만 선별 로컬 커밋한다.
다음 task 자동 실행, 새 번호/스레드 발급, 자동 위임, push/배포, 임상 진단·치료·자침 기능은 금지한다.

이번 실행:
1. T58 local_app_ready와 product-scope.json에서 현재 지원 근육 전체를 가져온다. 합격용 작은 표본만 고르지 않는다. 전체 target와 workbook 257행은 disposition을 유지한다.
2. 기존 verified claim/사전/워크북 mapping을 재사용하고 private 원문은 ignore 경로에 보존한다. 원문·정규화 후보·검증 claim을 분리한다. 필요한 기시/정지 내용은 공식/학술 원문을 확인하여 조사하고 카드에는 간결하게 쓴다.
3. 운동신경과 감각/고유수용성 정보를 혼동하지 않는다. 모호한 가지/신경근은 검증된 상위명 또는 미기재를 사용한다. 손/발 동명·whole/part·좌우 조건을 구분한다. 기본 텍스트에 사람이 모두 승인해야 하는 조건은 없다.
4. 현재 지원 근육의 구조 카드 기본 내용을 우선 완성한다. 추가 source가 필요한 세부 claim은 정확한 gap·사용자 영향을 기록하고 독립 작업을 계속한다. 앱에 확인되지 않은 placeholder/기시정지 좌표/새 nerve3D를 넣지 않는다. H열은 후보만 보존한다.
5. 현재 카드의 표시·검색·구조 탭과 provenance/private bundle 제외를 검증한다. 제품 계약을 충족하면 scoped passed로 종료하고 미확보 콘텐츠는 별도 남긴다. 기존 지식의 실질적인 부재로 주요 구조 학습이 불가능하면 해당 제품 문제를 해결한다. 다음 T82는 자동 실행하지 않는다.

종료 후 다음 ID는 T82다. 다음 promptFile을 안내하고 멈춰라. 다른 task를 이번에 시작하지 마라.
```

<a id="t82"></a>
### T82 — 지원 구조 설명·카드 감사와 보완

```text
HUMAN ATLAS에서 T82만 수행해라. 담당 Luna Max.

AGENTS.md, work/EXECUTION.json, design/2026-09-25-muscle-atlas/27-APP-COMPLETION-AND-CONTENT-ROADMAP.md, work/product-acceptance.json,
해당 task의 현재 spec/promptFile, 실제 선행 report/evidence를 읽어라.
목표는 현재 지원 범위에서 정확하고 안정적으로 사용할 수 있는 앱이다. task acceptance와 전체 콘텐츠 completeness를 분리한다.
27 설계/현재 acceptanceContract가 과거 전체 콘텐츠 0-gap·full extent 전수 PNG·10개마다 종료 문구보다 우선한다.
542 target/563 membership/12부위, 기존 HA 130, 역사163(6/20/135/2), 원본/OpenSim_Models/T13/기존 WIP를 보존한다.
source-only, 검증된 로컬 선택, humanReview=not_performed, 공개 권리 held를 독립적으로 유지한다.
지원한다고 표시한 구조의 wrong side/name/scope/placement와 실제 사용자 흐름 결함은 해결한다. 미지원 자료로 geometry/binding/승인을 만들지 않는다.
자동 계약 검사는 전수 수행하고 실제 시각 검증은 대표 유형·12부위·변경/충돌 사례에 집중한다. 동일 입력의 기존 근거는 영향 분석 후 재사용한다.
새 단서 없는 고정 catalog 검색·직접 용어 인용 검색·전체 suite/보고서 반복을 하지 않는다. 의미 검토 묶음은 내부 복구 단위다.
제품 계약을 충족하면 completed/passed, nextUnit=null로 종료하고 contentCompleteness=partial 및 남은 콘텐츠를 별도로 보고한다.
실제 제품 차단 결함이 남으면 실패 기능만 구체적으로 기록해 같은 task에서 고친다. 계획 문서만으로 pass하지 않는다.
해당 report/evidence와 EXECUTION record에 acceptanceScope/contractRevision/productReadiness/contentCompleteness/knownContentGaps/unresolvedProductBlockers를 기록한다.
합격 기록은 progress.productAcceptance에 contractRevision=app-completion-2026-10-01, acceptanceScope, productReadiness, contentCompleteness, knownContentGaps, unresolvedProductBlockers=[], evidence=[실제 보고서/검증 파일 경로]를 남긴다.
python3 work/tools/sync_execution.py 및 --check를 수행하고 소유 변경만 선별 로컬 커밋한다.
다음 task 자동 실행, 새 번호/스레드 발급, 자동 위임, push/배포, 임상 진단·치료·자침 기능은 금지한다.

이번 실행:
T81 실제 지원 근육/claim 원장을 자동 전수 감사하고 기존 근거를 재사용해 주요 카드와 충돌 사례를 실제 UI에서 확인한다. 잘못된 기시정지/갈래/손발 동명/운동·감각 구분은 수정한다. 확인되지 않은 세부 신경은 상위명/미기재 상태를 유지한다. private 원문과 출처 개발 원장이 학생 카드/bundle에 유출되지 않는지 검사한다. 전체 257행 처리 상태와 unsupported 콘텐츠를 보존한다. 주요 구조 학습을 막는 제품 결함이 없고 계약을 충족하면 completed/passed로 종료하며 전체 해부 연구 합격으로 쓰지 않는다. 다음 T83은 실행하지 않는다.

종료 후 다음 ID는 T83다. 다음 promptFile을 안내하고 멈춰라. 다른 task를 이번에 시작하지 마라.
```

<a id="t83"></a>
### T83 — 지원 근육 한글 기능 설명 연결

```text
HUMAN ATLAS에서 T83만 수행해라. 담당 Luna Max.

AGENTS.md, work/EXECUTION.json, design/2026-09-25-muscle-atlas/27-APP-COMPLETION-AND-CONTENT-ROADMAP.md, work/product-acceptance.json,
해당 task의 현재 spec/promptFile, 실제 선행 report/evidence를 읽어라.
목표는 현재 지원 범위에서 정확하고 안정적으로 사용할 수 있는 앱이다. task acceptance와 전체 콘텐츠 completeness를 분리한다.
27 설계/현재 acceptanceContract가 과거 전체 콘텐츠 0-gap·full extent 전수 PNG·10개마다 종료 문구보다 우선한다.
542 target/563 membership/12부위, 기존 HA 130, 역사163(6/20/135/2), 원본/OpenSim_Models/T13/기존 WIP를 보존한다.
source-only, 검증된 로컬 선택, humanReview=not_performed, 공개 권리 held를 독립적으로 유지한다.
지원한다고 표시한 구조의 wrong side/name/scope/placement와 실제 사용자 흐름 결함은 해결한다. 미지원 자료로 geometry/binding/승인을 만들지 않는다.
자동 계약 검사는 전수 수행하고 실제 시각 검증은 대표 유형·12부위·변경/충돌 사례에 집중한다. 동일 입력의 기존 근거는 영향 분석 후 재사용한다.
새 단서 없는 고정 catalog 검색·직접 용어 인용 검색·전체 suite/보고서 반복을 하지 않는다. 의미 검토 묶음은 내부 복구 단위다.
제품 계약을 충족하면 completed/passed, nextUnit=null로 종료하고 contentCompleteness=partial 및 남은 콘텐츠를 별도로 보고한다.
실제 제품 차단 결함이 남으면 실패 기능만 구체적으로 기록해 같은 task에서 고친다. 계획 문서만으로 pass하지 않는다.
해당 report/evidence와 EXECUTION record에 acceptanceScope/contractRevision/productReadiness/contentCompleteness/knownContentGaps/unresolvedProductBlockers를 기록한다.
합격 기록은 progress.productAcceptance에 contractRevision=app-completion-2026-10-01, acceptanceScope, productReadiness, contentCompleteness, knownContentGaps, unresolvedProductBlockers=[], evidence=[실제 보고서/검증 파일 경로]를 남긴다.
python3 work/tools/sync_execution.py 및 --check를 수행하고 소유 변경만 선별 로컬 커밋한다.
다음 task 자동 실행, 새 번호/스레드 발급, 자동 위임, push/배포, 임상 진단·치료·자침 기능은 금지한다.

이번 실행:
T81/T82의 staging·근육 mapping·verified claim을 재사용한다. 현재 지원 근육 전체를 처리하고 각 작용의 움직이는 구조·고정 조건·방향·갈래 차이를 근거로 검증한다. 한자 포함 action cell은 의미/괄호/조건을 보존하며 한글화한다. 손발 동명·얼굴/눈/혀/괄약근 기능을 관절 회전으로 억지 변환하지 않는다. 학생 설명은 간결하게 쓰고 출처·원문·AI 해석·채택은 내부에서 구분한다. 움직임으로 이해하기 버튼 위치와 실제 clip 지원 상태를 분리한다. 표정근 clip/가짜 수축/별도 scene는 만들지 않는다. 현재 기능 카드 전체의 계약과 대표·충돌 UI를 검증하고 scoped passed로 종료한다. 추가 source가 필요한 claim은 별도 콘텐츠 gap으로 남긴다. 다음 T84는 실행하지 않는다.

종료 후 다음 ID는 T84다. 다음 promptFile을 안내하고 멈춰라. 다른 task를 이번에 시작하지 마라.
```

<a id="t84"></a>
### T84 — 지원 기능 설명·학습 흐름 감사

```text
HUMAN ATLAS에서 T84만 수행해라. 담당 Luna Max.

AGENTS.md, work/EXECUTION.json, design/2026-09-25-muscle-atlas/27-APP-COMPLETION-AND-CONTENT-ROADMAP.md, work/product-acceptance.json,
해당 task의 현재 spec/promptFile, 실제 선행 report/evidence를 읽어라.
목표는 현재 지원 범위에서 정확하고 안정적으로 사용할 수 있는 앱이다. task acceptance와 전체 콘텐츠 completeness를 분리한다.
27 설계/현재 acceptanceContract가 과거 전체 콘텐츠 0-gap·full extent 전수 PNG·10개마다 종료 문구보다 우선한다.
542 target/563 membership/12부위, 기존 HA 130, 역사163(6/20/135/2), 원본/OpenSim_Models/T13/기존 WIP를 보존한다.
source-only, 검증된 로컬 선택, humanReview=not_performed, 공개 권리 held를 독립적으로 유지한다.
지원한다고 표시한 구조의 wrong side/name/scope/placement와 실제 사용자 흐름 결함은 해결한다. 미지원 자료로 geometry/binding/승인을 만들지 않는다.
자동 계약 검사는 전수 수행하고 실제 시각 검증은 대표 유형·12부위·변경/충돌 사례에 집중한다. 동일 입력의 기존 근거는 영향 분석 후 재사용한다.
새 단서 없는 고정 catalog 검색·직접 용어 인용 검색·전체 suite/보고서 반복을 하지 않는다. 의미 검토 묶음은 내부 복구 단위다.
제품 계약을 충족하면 completed/passed, nextUnit=null로 종료하고 contentCompleteness=partial 및 남은 콘텐츠를 별도로 보고한다.
실제 제품 차단 결함이 남으면 실패 기능만 구체적으로 기록해 같은 task에서 고친다. 계획 문서만으로 pass하지 않는다.
해당 report/evidence와 EXECUTION record에 acceptanceScope/contractRevision/productReadiness/contentCompleteness/knownContentGaps/unresolvedProductBlockers를 기록한다.
합격 기록은 progress.productAcceptance에 contractRevision=app-completion-2026-10-01, acceptanceScope, productReadiness, contentCompleteness, knownContentGaps, unresolvedProductBlockers=[], evidence=[실제 보고서/검증 파일 경로]를 남긴다.
python3 work/tools/sync_execution.py 및 --check를 수행하고 소유 변경만 선별 로컬 커밋한다.
다음 task 자동 실행, 새 번호/스레드 발급, 자동 위임, push/배포, 임상 진단·치료·자침 기능은 금지한다.

이번 실행:
T83의 현재 지원 카드/claim 전체를 자동 대조하고 작용/갈래/고정 조건의 의미 충돌과 대표 실제 UI를 감사한다. 한자 제거만으로 의미가 검증됐다고 하지 않는다. 구조 설명과 기능의 모순, 손발 동명, 표정근의 unsupported animation 표시를 확인하고 오류를 수정한다. 검증되지 않은 clip·형상·기능을 만들어 통과하지 않는다. 데이터·카드 흐름·runtime 한자0건을 확인하고 제품 계약이 충족되면 completed/passed로 종료한다. 콘텐츠 completeness와 gap을 별도 보고하고 다음 ID는 EXECUTION의 T61이며 자동 실행하지 않는다.

종료 후 다음 ID는 T61다. 다음 promptFile을 안내하고 멈춰라. 다른 task를 이번에 시작하지 마라.
```

<a id="t61"></a>
### T61 — 신경 지원 범위·자료 inventory·공통 계약

```text
HUMAN ATLAS에서 T61만 수행해라. 담당 Sol High.

AGENTS.md, work/EXECUTION.json, design/2026-09-25-muscle-atlas/27-APP-COMPLETION-AND-CONTENT-ROADMAP.md, work/product-acceptance.json,
해당 task의 현재 spec/promptFile, 실제 선행 report/evidence를 읽어라.
목표는 현재 지원 범위에서 정확하고 안정적으로 사용할 수 있는 앱이다. task acceptance와 전체 콘텐츠 completeness를 분리한다.
27 설계/현재 acceptanceContract가 과거 전체 콘텐츠 0-gap·full extent 전수 PNG·10개마다 종료 문구보다 우선한다.
542 target/563 membership/12부위, 기존 HA 130, 역사163(6/20/135/2), 원본/OpenSim_Models/T13/기존 WIP를 보존한다.
source-only, 검증된 로컬 선택, humanReview=not_performed, 공개 권리 held를 독립적으로 유지한다.
지원한다고 표시한 구조의 wrong side/name/scope/placement와 실제 사용자 흐름 결함은 해결한다. 미지원 자료로 geometry/binding/승인을 만들지 않는다.
자동 계약 검사는 전수 수행하고 실제 시각 검증은 대표 유형·12부위·변경/충돌 사례에 집중한다. 동일 입력의 기존 근거는 영향 분석 후 재사용한다.
새 단서 없는 고정 catalog 검색·직접 용어 인용 검색·전체 suite/보고서 반복을 하지 않는다. 의미 검토 묶음은 내부 복구 단위다.
제품 계약을 충족하면 completed/passed, nextUnit=null로 종료하고 contentCompleteness=partial 및 남은 콘텐츠를 별도로 보고한다.
실제 제품 차단 결함이 남으면 실패 기능만 구체적으로 기록해 같은 task에서 고친다. 계획 문서만으로 pass하지 않는다.
해당 report/evidence와 EXECUTION record에 acceptanceScope/contractRevision/productReadiness/contentCompleteness/knownContentGaps/unresolvedProductBlockers를 기록한다.
합격 기록은 progress.productAcceptance에 contractRevision=app-completion-2026-10-01, acceptanceScope, productReadiness, contentCompleteness, knownContentGaps, unresolvedProductBlockers=[], evidence=[실제 보고서/검증 파일 경로]를 남긴다.
python3 work/tools/sync_execution.py 및 --check를 수행하고 소유 변경만 선별 로컬 커밋한다.
다음 task 자동 실행, 새 번호/스레드 발급, 자동 위임, push/배포, 임상 진단·치료·자침 기능은 금지한다.

이번 실행:
이번 범위: T58의 지원 앱과 T84 설명 기능 뒤에 신경 source inventory와 실제 지원 집합을 정리하고 source namespace/frame/pose/curve 또는 mesh/branch/검증된 지배 관계/typed card/layer 계약을 구현한다. T86의 범위 대조를 같은 task에 흡수한다. 전체 원장과 미확보는 유지하지만 전 신경의 source 확보를 계약 완료 조건으로 두지 않는다. 감각영역·피부분절·경락을 혼합하지 않고 source 이름만으로 지배 관계를 만들지 않는다.

현재 확보 자료와 주요 사용 흐름으로 지원/미지원 신경 집합을 정하고 정확한 identity/좌표/pose/지배 관계 계약을 구현한다. 조사 원장은 전수 참조하고 필수 참조의 실제 자료/hash를 검증한다. T86을 별도로 시작하지 않는다. 계약 fixtures와 기존 앱 policy/selection 회귀를 검사하며 새 신경3D를 완성했다고 쓰지 않는다.

종료 후 다음 ID는 T62다. 다음 promptFile을 안내하고 멈춰라. 다른 task를 이번에 시작하지 마라.
```

<a id="t62"></a>
### T62 — 신경 자료 검증·공통 등록

```text
HUMAN ATLAS에서 T62만 수행해라. 담당 Luna Max.

AGENTS.md, work/EXECUTION.json, design/2026-09-25-muscle-atlas/27-APP-COMPLETION-AND-CONTENT-ROADMAP.md, work/product-acceptance.json,
해당 task의 현재 spec/promptFile, 실제 선행 report/evidence를 읽어라.
목표는 현재 지원 범위에서 정확하고 안정적으로 사용할 수 있는 앱이다. task acceptance와 전체 콘텐츠 completeness를 분리한다.
27 설계/현재 acceptanceContract가 과거 전체 콘텐츠 0-gap·full extent 전수 PNG·10개마다 종료 문구보다 우선한다.
542 target/563 membership/12부위, 기존 HA 130, 역사163(6/20/135/2), 원본/OpenSim_Models/T13/기존 WIP를 보존한다.
source-only, 검증된 로컬 선택, humanReview=not_performed, 공개 권리 held를 독립적으로 유지한다.
지원한다고 표시한 구조의 wrong side/name/scope/placement와 실제 사용자 흐름 결함은 해결한다. 미지원 자료로 geometry/binding/승인을 만들지 않는다.
자동 계약 검사는 전수 수행하고 실제 시각 검증은 대표 유형·12부위·변경/충돌 사례에 집중한다. 동일 입력의 기존 근거는 영향 분석 후 재사용한다.
새 단서 없는 고정 catalog 검색·직접 용어 인용 검색·전체 suite/보고서 반복을 하지 않는다. 의미 검토 묶음은 내부 복구 단위다.
제품 계약을 충족하면 completed/passed, nextUnit=null로 종료하고 contentCompleteness=partial 및 남은 콘텐츠를 별도로 보고한다.
실제 제품 차단 결함이 남으면 실패 기능만 구체적으로 기록해 같은 task에서 고친다. 계획 문서만으로 pass하지 않는다.
해당 report/evidence와 EXECUTION record에 acceptanceScope/contractRevision/productReadiness/contentCompleteness/knownContentGaps/unresolvedProductBlockers를 기록한다.
합격 기록은 progress.productAcceptance에 contractRevision=app-completion-2026-10-01, acceptanceScope, productReadiness, contentCompleteness, knownContentGaps, unresolvedProductBlockers=[], evidence=[실제 보고서/검증 파일 경로]를 남긴다.
python3 work/tools/sync_execution.py 및 --check를 수행하고 소유 변경만 선별 로컬 커밋한다.
다음 task 자동 실행, 새 번호/스레드 발급, 자동 위임, push/배포, 임상 진단·치료·자침 기능은 금지한다.

이번 실행:
이번 범위: T61의 실제 지원 신경을 우선순위에 따라 조사·검증·등록한다. T87의 확장 조사와 T88의 등록은 같은 task의 공통 pipeline으로 흡수한다. trunk/branch/지역/좌우/pose/지배 관계와 source 근거를 구분한다. 이미 확보한 자료부터 완성하며 새 source가 필요한 신경은 명시한 확장 backlog로 남긴다. 모든 신경 연구가 끝날 때까지 첫 검증 자료를 제품에서 사용할 수 없게 만드는 조건은 폐기한다.

T61의 지원 후보와 실제 source를 검증하고 같은 schema/registry로 bulk 등록한다. 공식/학술 원문에서 필요한 관계를 확인하고 원문·AI 해석·채택·사람검토를 분리한다. source geometry/좌표/branch와 지배 관계를 각각 검증한다. 실제 통합 가능 자료와 미확보를 보고하며 한 파일럿 또는 자료 수만으로 전 신경 완료라고 하지 않는다. T87/T88 별도 실행·반복 전수 builder를 만들지 않는다.

종료 후 다음 ID는 T63다. 다음 promptFile을 안내하고 멈춰라. 다른 task를 이번에 시작하지 마라.
```

<a id="t63"></a>
### T63 — 같은 장면의 신경 주행·지배근 선택

```text
HUMAN ATLAS에서 T63만 수행해라. 담당 Sol High.

AGENTS.md, work/EXECUTION.json, design/2026-09-25-muscle-atlas/27-APP-COMPLETION-AND-CONTENT-ROADMAP.md, work/product-acceptance.json,
해당 task의 현재 spec/promptFile, 실제 선행 report/evidence를 읽어라.
목표는 현재 지원 범위에서 정확하고 안정적으로 사용할 수 있는 앱이다. task acceptance와 전체 콘텐츠 completeness를 분리한다.
27 설계/현재 acceptanceContract가 과거 전체 콘텐츠 0-gap·full extent 전수 PNG·10개마다 종료 문구보다 우선한다.
542 target/563 membership/12부위, 기존 HA 130, 역사163(6/20/135/2), 원본/OpenSim_Models/T13/기존 WIP를 보존한다.
source-only, 검증된 로컬 선택, humanReview=not_performed, 공개 권리 held를 독립적으로 유지한다.
지원한다고 표시한 구조의 wrong side/name/scope/placement와 실제 사용자 흐름 결함은 해결한다. 미지원 자료로 geometry/binding/승인을 만들지 않는다.
자동 계약 검사는 전수 수행하고 실제 시각 검증은 대표 유형·12부위·변경/충돌 사례에 집중한다. 동일 입력의 기존 근거는 영향 분석 후 재사용한다.
새 단서 없는 고정 catalog 검색·직접 용어 인용 검색·전체 suite/보고서 반복을 하지 않는다. 의미 검토 묶음은 내부 복구 단위다.
제품 계약을 충족하면 completed/passed, nextUnit=null로 종료하고 contentCompleteness=partial 및 남은 콘텐츠를 별도로 보고한다.
실제 제품 차단 결함이 남으면 실패 기능만 구체적으로 기록해 같은 task에서 고친다. 계획 문서만으로 pass하지 않는다.
해당 report/evidence와 EXECUTION record에 acceptanceScope/contractRevision/productReadiness/contentCompleteness/knownContentGaps/unresolvedProductBlockers를 기록한다.
합격 기록은 progress.productAcceptance에 contractRevision=app-completion-2026-10-01, acceptanceScope, productReadiness, contentCompleteness, knownContentGaps, unresolvedProductBlockers=[], evidence=[실제 보고서/검증 파일 경로]를 남긴다.
python3 work/tools/sync_execution.py 및 --check를 수행하고 소유 변경만 선별 로컬 커밋한다.
다음 task 자동 실행, 새 번호/스레드 발급, 자동 위임, push/배포, 임상 진단·치료·자침 기능은 금지한다.

이번 실행:
이번 범위: 검증된 T62 신경을 기존 scene/renderer/camera에서 표시하고 typed 선택/카드/근거 있는 지배근 강조/복원을 연결한다. T89의 같은 방식 확장은 데이터 기반 내부 unit으로 흡수한다. 신경 주행·좌표·pose가 확인된 실제 surface/curve만 사용하고 미확보 신경은 미지원으로 유지한다. source 후보나 이름을 실제 주행으로 조작하지 않는다.

하나의 신경 3D 경로로 검증된 자료 전체를 처리하고 선택/branch/side/region/card 및 지배근 강조/복원을 연결한다. loader 취소·cache·layer-off·pose 지원을 기존 controller와 통합한다. 지원되지 않은 운동 pose에서 정적 신경을 잘못 고정하지 않는다. 데이터 계약 전수 검사와 지역/주행 유형·변경 사례의 실제 UI를 확인한다. T89를 따로 실행하지 않는다.

종료 후 다음 ID는 T90다. 다음 promptFile을 안내하고 멈춰라. 다른 task를 이번에 시작하지 마라.
```

<a id="t90"></a>
### T90 — 신경 그래픽·선택 품질 완성

```text
HUMAN ATLAS에서 T90만 수행해라. 담당 Astra · 현재 대화 직접 구현.

AGENTS.md, work/EXECUTION.json, design/2026-09-25-muscle-atlas/27-APP-COMPLETION-AND-CONTENT-ROADMAP.md, work/product-acceptance.json,
해당 task의 현재 spec/promptFile, 실제 선행 report/evidence를 읽어라.
목표는 현재 지원 범위에서 정확하고 안정적으로 사용할 수 있는 앱이다. task acceptance와 전체 콘텐츠 completeness를 분리한다.
27 설계/현재 acceptanceContract가 과거 전체 콘텐츠 0-gap·full extent 전수 PNG·10개마다 종료 문구보다 우선한다.
542 target/563 membership/12부위, 기존 HA 130, 역사163(6/20/135/2), 원본/OpenSim_Models/T13/기존 WIP를 보존한다.
source-only, 검증된 로컬 선택, humanReview=not_performed, 공개 권리 held를 독립적으로 유지한다.
지원한다고 표시한 구조의 wrong side/name/scope/placement와 실제 사용자 흐름 결함은 해결한다. 미지원 자료로 geometry/binding/승인을 만들지 않는다.
자동 계약 검사는 전수 수행하고 실제 시각 검증은 대표 유형·12부위·변경/충돌 사례에 집중한다. 동일 입력의 기존 근거는 영향 분석 후 재사용한다.
새 단서 없는 고정 catalog 검색·직접 용어 인용 검색·전체 suite/보고서 반복을 하지 않는다. 의미 검토 묶음은 내부 복구 단위다.
제품 계약을 충족하면 completed/passed, nextUnit=null로 종료하고 contentCompleteness=partial 및 남은 콘텐츠를 별도로 보고한다.
실제 제품 차단 결함이 남으면 실패 기능만 구체적으로 기록해 같은 task에서 고친다. 계획 문서만으로 pass하지 않는다.
해당 report/evidence와 EXECUTION record에 acceptanceScope/contractRevision/productReadiness/contentCompleteness/knownContentGaps/unresolvedProductBlockers를 기록한다.
합격 기록은 progress.productAcceptance에 contractRevision=app-completion-2026-10-01, acceptanceScope, productReadiness, contentCompleteness, knownContentGaps, unresolvedProductBlockers=[], evidence=[실제 보고서/검증 파일 경로]를 남긴다.
python3 work/tools/sync_execution.py 및 --check를 수행하고 소유 변경만 선별 로컬 커밋한다.
다음 task 자동 실행, 새 번호/스레드 발급, 자동 위임, push/배포, 임상 진단·치료·자침 기능은 금지한다.

이번 실행:
이번 범위: T63의 실제 지원 신경 주행과 기존 근육·뼈 맥락에서 대비/깊이/선택/지배근 강조/카드/복원 품질을 다듬는다. 대표 지역과 390/1024/1440 흐름을 실제 검증한다. 전체 신경 미확보는 별도 상태이며 지원 경로의 잘못된 pose/좌우/위치는 해결한다. 담당 Astra 현재 대화 직접 구현을 유지한다.

현재 UI와 실제 신경 geometry를 보고 색/깊이/관찰/선택 대비를 조정한다. 기존 scene/camera를 유지하고 기본 상태·신경 layer 전환·선택·복원을 검증한다. source pose 제한을 정확히 처리한다. 지원 집합의 계약과 대표/변경 화면 및 관련 성능을 확인하고 그래픽 scoped acceptance를 남긴다. 다른 task/agent로 자동 위임하지 않는다.

종료 후 다음 ID는 T65다. 다음 promptFile을 안내하고 멈춰라. 다른 task를 이번에 시작하지 마라.
```

<a id="t65"></a>
### T65 — 신경 기능 변화 설명·사용 흐름 완성

```text
HUMAN ATLAS에서 T65만 수행해라. 담당 Luna Max.

AGENTS.md, work/EXECUTION.json, design/2026-09-25-muscle-atlas/27-APP-COMPLETION-AND-CONTENT-ROADMAP.md, work/product-acceptance.json,
해당 task의 현재 spec/promptFile, 실제 선행 report/evidence를 읽어라.
목표는 현재 지원 범위에서 정확하고 안정적으로 사용할 수 있는 앱이다. task acceptance와 전체 콘텐츠 completeness를 분리한다.
27 설계/현재 acceptanceContract가 과거 전체 콘텐츠 0-gap·full extent 전수 PNG·10개마다 종료 문구보다 우선한다.
542 target/563 membership/12부위, 기존 HA 130, 역사163(6/20/135/2), 원본/OpenSim_Models/T13/기존 WIP를 보존한다.
source-only, 검증된 로컬 선택, humanReview=not_performed, 공개 권리 held를 독립적으로 유지한다.
지원한다고 표시한 구조의 wrong side/name/scope/placement와 실제 사용자 흐름 결함은 해결한다. 미지원 자료로 geometry/binding/승인을 만들지 않는다.
자동 계약 검사는 전수 수행하고 실제 시각 검증은 대표 유형·12부위·변경/충돌 사례에 집중한다. 동일 입력의 기존 근거는 영향 분석 후 재사용한다.
새 단서 없는 고정 catalog 검색·직접 용어 인용 검색·전체 suite/보고서 반복을 하지 않는다. 의미 검토 묶음은 내부 복구 단위다.
제품 계약을 충족하면 completed/passed, nextUnit=null로 종료하고 contentCompleteness=partial 및 남은 콘텐츠를 별도로 보고한다.
실제 제품 차단 결함이 남으면 실패 기능만 구체적으로 기록해 같은 task에서 고친다. 계획 문서만으로 pass하지 않는다.
해당 report/evidence와 EXECUTION record에 acceptanceScope/contractRevision/productReadiness/contentCompleteness/knownContentGaps/unresolvedProductBlockers를 기록한다.
합격 기록은 progress.productAcceptance에 contractRevision=app-completion-2026-10-01, acceptanceScope, productReadiness, contentCompleteness, knownContentGaps, unresolvedProductBlockers=[], evidence=[실제 보고서/검증 파일 경로]를 남긴다.
python3 work/tools/sync_execution.py 및 --check를 수행하고 소유 변경만 선별 로컬 커밋한다.
다음 task 자동 실행, 새 번호/스레드 발급, 자동 위임, push/배포, 임상 진단·치료·자침 기능은 금지한다.

이번 실행:
이번 범위: T64/T91의 접힌 설명과 확장 자료를 같은 task에 흡수하여 현재 지원 신경의 주행·지배근·교육용 기능 변화/포착 맥락을 검증된 설명으로 연결한다. 구조·설명·3D 지원 범위는 분리한다. 임상 진단·치료·자침 위치/깊이 추천은 만들지 않는다. 현재 신경 학습 흐름을 완성하고 모든 신경/모든 운동의 자료 확보를 일괄 선행 조건으로 두지 않는다.

기존 verified 신경 claim을 재사용하고 필요한 교육용 기능 변화/포착 설명만 공식/학술 원문으로 대조한다. 위치·관련 구조·가능한 기능 변화를 설명하되 자동 진단·시술 추천으로 전환하지 않는다. 접힌 정보 UI와 신경 선택→주행→지배근→설명→복원을 검증하고 실제 혼동/오류를 수정한다. T64/T91 별도 실행을 하지 않는다. unsupported 텍스트/geometry는 정직하게 분리한다.

종료 후 다음 ID는 T35다. 다음 promptFile을 안내하고 멈춰라. 다른 task를 이번에 시작하지 마라.
```

<a id="t35"></a>
### T35 — 같은 모형 움직임 지원 범위·제작 계획

```text
HUMAN ATLAS에서 T35만 수행해라. 담당 Sol High.

AGENTS.md, work/EXECUTION.json, design/2026-09-25-muscle-atlas/27-APP-COMPLETION-AND-CONTENT-ROADMAP.md, work/product-acceptance.json,
해당 task의 현재 spec/promptFile, 실제 선행 report/evidence를 읽어라.
목표는 현재 지원 범위에서 정확하고 안정적으로 사용할 수 있는 앱이다. task acceptance와 전체 콘텐츠 completeness를 분리한다.
27 설계/현재 acceptanceContract가 과거 전체 콘텐츠 0-gap·full extent 전수 PNG·10개마다 종료 문구보다 우선한다.
542 target/563 membership/12부위, 기존 HA 130, 역사163(6/20/135/2), 원본/OpenSim_Models/T13/기존 WIP를 보존한다.
source-only, 검증된 로컬 선택, humanReview=not_performed, 공개 권리 held를 독립적으로 유지한다.
지원한다고 표시한 구조의 wrong side/name/scope/placement와 실제 사용자 흐름 결함은 해결한다. 미지원 자료로 geometry/binding/승인을 만들지 않는다.
자동 계약 검사는 전수 수행하고 실제 시각 검증은 대표 유형·12부위·변경/충돌 사례에 집중한다. 동일 입력의 기존 근거는 영향 분석 후 재사용한다.
새 단서 없는 고정 catalog 검색·직접 용어 인용 검색·전체 suite/보고서 반복을 하지 않는다. 의미 검토 묶음은 내부 복구 단위다.
제품 계약을 충족하면 completed/passed, nextUnit=null로 종료하고 contentCompleteness=partial 및 남은 콘텐츠를 별도로 보고한다.
실제 제품 차단 결함이 남으면 실패 기능만 구체적으로 기록해 같은 task에서 고친다. 계획 문서만으로 pass하지 않는다.
해당 report/evidence와 EXECUTION record에 acceptanceScope/contractRevision/productReadiness/contentCompleteness/knownContentGaps/unresolvedProductBlockers를 기록한다.
합격 기록은 progress.productAcceptance에 contractRevision=app-completion-2026-10-01, acceptanceScope, productReadiness, contentCompleteness, knownContentGaps, unresolvedProductBlockers=[], evidence=[실제 보고서/검증 파일 경로]를 남긴다.
python3 work/tools/sync_execution.py 및 --check를 수행하고 소유 변경만 선별 로컬 커밋한다.
다음 task 자동 실행, 새 번호/스레드 발급, 자동 위임, push/배포, 임상 진단·치료·자침 기능은 금지한다.

이번 실행:
이번 범위: 현재 실제 전신 base와 구조/설명/신경 지원 범위를 확인하여 첫 앞정강근 시범과 재사용 가능한 다음 움직임 family를 계획한다. 실제 source/frame/pose/부착/rig 가능성과 OpenSim 보조 source 대응을 검증한다. 현재 제작 가능한 범위를 명시하고 나머지는 움직임 backlog로 보존한다. exact 표정근 clip 사용자 제외는 유지하며 전 근육 clip 확보를 첫 움직임 제공의 선행 조건으로 두지 않는다. 계획 task이며 clip 구현은 T59/T66에서 한다.

기존 실제 source와 target/rig 상태를 읽고 제작 입력·좌표·부착 근거·family 재사용/예외·품질 판단을 정한다. 임의로 지원 가능을 선언하지 않는다. 앞정강근 pilot과 후속 소흉근/견갑대 사례의 실제 가능성과 필요 작업을 확인한다. 검증 가능한 계획 산출물로 종료하며 새 clip/원본 geometry 변형을 하지 않는다.

종료 후 다음 ID는 T59다. 다음 promptFile을 안내하고 멈춰라. 다른 task를 이번에 시작하지 마라.
```

<a id="t59"></a>
### T59 — 앞정강근 실제 변형·공통 재생 연결

```text
HUMAN ATLAS에서 T59만 수행해라. 담당 Sol High.

AGENTS.md, work/EXECUTION.json, design/2026-09-25-muscle-atlas/27-APP-COMPLETION-AND-CONTENT-ROADMAP.md, work/product-acceptance.json,
해당 task의 현재 spec/promptFile, 실제 선행 report/evidence를 읽어라.
목표는 현재 지원 범위에서 정확하고 안정적으로 사용할 수 있는 앱이다. task acceptance와 전체 콘텐츠 completeness를 분리한다.
27 설계/현재 acceptanceContract가 과거 전체 콘텐츠 0-gap·full extent 전수 PNG·10개마다 종료 문구보다 우선한다.
542 target/563 membership/12부위, 기존 HA 130, 역사163(6/20/135/2), 원본/OpenSim_Models/T13/기존 WIP를 보존한다.
source-only, 검증된 로컬 선택, humanReview=not_performed, 공개 권리 held를 독립적으로 유지한다.
지원한다고 표시한 구조의 wrong side/name/scope/placement와 실제 사용자 흐름 결함은 해결한다. 미지원 자료로 geometry/binding/승인을 만들지 않는다.
자동 계약 검사는 전수 수행하고 실제 시각 검증은 대표 유형·12부위·변경/충돌 사례에 집중한다. 동일 입력의 기존 근거는 영향 분석 후 재사용한다.
새 단서 없는 고정 catalog 검색·직접 용어 인용 검색·전체 suite/보고서 반복을 하지 않는다. 의미 검토 묶음은 내부 복구 단위다.
제품 계약을 충족하면 completed/passed, nextUnit=null로 종료하고 contentCompleteness=partial 및 남은 콘텐츠를 별도로 보고한다.
실제 제품 차단 결함이 남으면 실패 기능만 구체적으로 기록해 같은 task에서 고친다. 계획 문서만으로 pass하지 않는다.
해당 report/evidence와 EXECUTION record에 acceptanceScope/contractRevision/productReadiness/contentCompleteness/knownContentGaps/unresolvedProductBlockers를 기록한다.
합격 기록은 progress.productAcceptance에 contractRevision=app-completion-2026-10-01, acceptanceScope, productReadiness, contentCompleteness, knownContentGaps, unresolvedProductBlockers=[], evidence=[실제 보고서/검증 파일 경로]를 남긴다.
python3 work/tools/sync_execution.py 및 --check를 수행하고 소유 변경만 선별 로컬 커밋한다.
다음 task 자동 실행, 새 번호/스레드 발급, 자동 위임, push/배포, 임상 진단·치료·자침 기능은 금지한다.

이번 실행:
이번 범위: T35의 현재 base에 실제 앞정강근 변형과 발 움직임을 제작하고 같은 viewport의 공통 재생기로 연결한다. T60의 player/CTA 통합을 같은 task에 흡수한다. source/frame/rest pose/endpoint 근거, 실제 skinning 또는 morph 변형, 주변 구조의 수동 대응/관통을 검증한다. scale-only/뼈나 선 길이만/별도 모형 전환은 제품 수축 시범으로 세지 않는다.

현재 product-scope의 실제 근육/뼈와 T35 제작 입력을 사용하여 derived rig/clip을 별도 소유 경로에 만든다. 원본을 수정하지 않는다. 실제 표면 변형과 관절 움직임, 주변 맥락을 같은 scene에 결속한다. CTA의 명시 재생/pause/속도/진행/처음 자세, reduced-motion, 전환·실패·unmount 정리를 공통 player로 구현한다. 데이터/pose/주변 관통과 실제 전신 탐색→선택→재생→복원을 확인한다. T60 별도 실행을 하지 않는다.

종료 후 다음 ID는 T25다. 다음 promptFile을 안내하고 멈춰라. 다른 task를 이번에 시작하지 마라.
```

<a id="t25"></a>
### T25 — 첫 같은 모형 움직임 학습 흐름 완성

```text
HUMAN ATLAS에서 T25만 수행해라. 담당 Luna Max.

AGENTS.md, work/EXECUTION.json, design/2026-09-25-muscle-atlas/27-APP-COMPLETION-AND-CONTENT-ROADMAP.md, work/product-acceptance.json,
해당 task의 현재 spec/promptFile, 실제 선행 report/evidence를 읽어라.
목표는 현재 지원 범위에서 정확하고 안정적으로 사용할 수 있는 앱이다. task acceptance와 전체 콘텐츠 completeness를 분리한다.
27 설계/현재 acceptanceContract가 과거 전체 콘텐츠 0-gap·full extent 전수 PNG·10개마다 종료 문구보다 우선한다.
542 target/563 membership/12부위, 기존 HA 130, 역사163(6/20/135/2), 원본/OpenSim_Models/T13/기존 WIP를 보존한다.
source-only, 검증된 로컬 선택, humanReview=not_performed, 공개 권리 held를 독립적으로 유지한다.
지원한다고 표시한 구조의 wrong side/name/scope/placement와 실제 사용자 흐름 결함은 해결한다. 미지원 자료로 geometry/binding/승인을 만들지 않는다.
자동 계약 검사는 전수 수행하고 실제 시각 검증은 대표 유형·12부위·변경/충돌 사례에 집중한다. 동일 입력의 기존 근거는 영향 분석 후 재사용한다.
새 단서 없는 고정 catalog 검색·직접 용어 인용 검색·전체 suite/보고서 반복을 하지 않는다. 의미 검토 묶음은 내부 복구 단위다.
제품 계약을 충족하면 completed/passed, nextUnit=null로 종료하고 contentCompleteness=partial 및 남은 콘텐츠를 별도로 보고한다.
실제 제품 차단 결함이 남으면 실패 기능만 구체적으로 기록해 같은 task에서 고친다. 계획 문서만으로 pass하지 않는다.
해당 report/evidence와 EXECUTION record에 acceptanceScope/contractRevision/productReadiness/contentCompleteness/knownContentGaps/unresolvedProductBlockers를 기록한다.
합격 기록은 progress.productAcceptance에 contractRevision=app-completion-2026-10-01, acceptanceScope, productReadiness, contentCompleteness, knownContentGaps, unresolvedProductBlockers=[], evidence=[실제 보고서/검증 파일 경로]를 남긴다.
python3 work/tools/sync_execution.py 및 --check를 수행하고 소유 변경만 선별 로컬 커밋한다.
다음 task 자동 실행, 새 번호/스레드 발급, 자동 위임, push/배포, 임상 진단·치료·자침 기능은 금지한다.

이번 실행:
이번 범위: T59의 실제 같은 모형 clip·player를 구조/기능 카드와 연결하여 전신 탐색→앞정강근→기시정지/기능→움직임으로 이해하기→실제 표면 변형과 발 움직임→복원을 검증하고 오류를 수정한다. 역사 T24 별도 모형/뼈 경로 후보는 그대로 역사로 보존한다. 신경은 이미 선행 지원 기능이며 전 근육 motion 뒤에 다시 시작하는 옛 순서는 폐기한다.

T59 실제 rig/clip/player와 현재 카드/설명을 연결하고 실제 browser에서 재생/중지/속도/처음 자세/부위 변경/선택 변경/실패 복구를 확인한다. camera reset과 pose reset을 구분하고 자동 재생을 하지 않는다. 눈에 보이는 실제 같은 근육 변형과 작용 설명의 동기를 검증한다. clip 부족을 다른 모델·scale-only로 대체하지 않는다. 한 시범 완료와 전체 motion completeness는 별도로 보고한다.

종료 후 다음 ID는 T66다. 다음 promptFile을 안내하고 멈춰라. 다른 task를 이번에 시작하지 마라.
```

<a id="t66"></a>
### T66 — 움직임 family 재사용 확장·학습 연결

```text
HUMAN ATLAS에서 T66만 수행해라. 담당 Luna Max.

AGENTS.md, work/EXECUTION.json, design/2026-09-25-muscle-atlas/27-APP-COMPLETION-AND-CONTENT-ROADMAP.md, work/product-acceptance.json,
해당 task의 현재 spec/promptFile, 실제 선행 report/evidence를 읽어라.
목표는 현재 지원 범위에서 정확하고 안정적으로 사용할 수 있는 앱이다. task acceptance와 전체 콘텐츠 completeness를 분리한다.
27 설계/현재 acceptanceContract가 과거 전체 콘텐츠 0-gap·full extent 전수 PNG·10개마다 종료 문구보다 우선한다.
542 target/563 membership/12부위, 기존 HA 130, 역사163(6/20/135/2), 원본/OpenSim_Models/T13/기존 WIP를 보존한다.
source-only, 검증된 로컬 선택, humanReview=not_performed, 공개 권리 held를 독립적으로 유지한다.
지원한다고 표시한 구조의 wrong side/name/scope/placement와 실제 사용자 흐름 결함은 해결한다. 미지원 자료로 geometry/binding/승인을 만들지 않는다.
자동 계약 검사는 전수 수행하고 실제 시각 검증은 대표 유형·12부위·변경/충돌 사례에 집중한다. 동일 입력의 기존 근거는 영향 분석 후 재사용한다.
새 단서 없는 고정 catalog 검색·직접 용어 인용 검색·전체 suite/보고서 반복을 하지 않는다. 의미 검토 묶음은 내부 복구 단위다.
제품 계약을 충족하면 completed/passed, nextUnit=null로 종료하고 contentCompleteness=partial 및 남은 콘텐츠를 별도로 보고한다.
실제 제품 차단 결함이 남으면 실패 기능만 구체적으로 기록해 같은 task에서 고친다. 계획 문서만으로 pass하지 않는다.
해당 report/evidence와 EXECUTION record에 acceptanceScope/contractRevision/productReadiness/contentCompleteness/knownContentGaps/unresolvedProductBlockers를 기록한다.
합격 기록은 progress.productAcceptance에 contractRevision=app-completion-2026-10-01, acceptanceScope, productReadiness, contentCompleteness, knownContentGaps, unresolvedProductBlockers=[], evidence=[실제 보고서/검증 파일 경로]를 남긴다.
python3 work/tools/sync_execution.py 및 --check를 수행하고 소유 변경만 선별 로컬 커밋한다.
다음 task 자동 실행, 새 번호/스레드 발급, 자동 위임, push/배포, 임상 진단·치료·자침 기능은 금지한다.

이번 실행:
이번 범위: T27/T28/T45/T46/T29/T31의 소흉근·견갑대 준비/시범/설명/감사를 이 task의 내부 unit으로 흡수한다. T35가 실제 지원 가능으로 정한 family를 공통 rig/player/설명 계약으로 확장한다. 현재 base에서 실제 해부학적 이동과 표면 변형이 성립하는 사례만 지원한다. 사용자 제외 표정근 clip은 만들지 않는다. 전 근육 animation 수집을 무제한 종료 조건으로 두지 않고 지원 집합과 나머지 backlog를 명시한다.

T59 공통 rig/player와 T25 학습 흐름을 재사용하여 T35의 후속 family를 제작한다. 소흉근·견갑대의 실제 source/부착/pose/움직이는 뼈·수동 변형 근거를 검증한다. 검증된 clip과 같은 scene의 설명/카드/재생을 함께 연결한다. 모든 이동을 단순 scale로 표현하지 않는다. 실제 family별 의미 검토와 전환/복원/관통/소스 보존 검사를 한다. 흡수된 작은 task를 별도로 실행하거나 batch 전용 runtime 분기를 만들지 않는다. 새 근거 없이는 지원 clip 수를 채우기 위한 모션을 만들지 않는다.

종료 후 다음 ID는 T85다. 다음 promptFile을 안내하고 멈춰라. 다른 task를 이번에 시작하지 마라.
```

<a id="t85"></a>
### T85 — 지원 움직임·통합 앱 품질 완성

```text
HUMAN ATLAS에서 T85만 수행해라. 담당 Astra · 현재 대화 직접 구현.

AGENTS.md, work/EXECUTION.json, design/2026-09-25-muscle-atlas/27-APP-COMPLETION-AND-CONTENT-ROADMAP.md, work/product-acceptance.json,
해당 task의 현재 spec/promptFile, 실제 선행 report/evidence를 읽어라.
목표는 현재 지원 범위에서 정확하고 안정적으로 사용할 수 있는 앱이다. task acceptance와 전체 콘텐츠 completeness를 분리한다.
27 설계/현재 acceptanceContract가 과거 전체 콘텐츠 0-gap·full extent 전수 PNG·10개마다 종료 문구보다 우선한다.
542 target/563 membership/12부위, 기존 HA 130, 역사163(6/20/135/2), 원본/OpenSim_Models/T13/기존 WIP를 보존한다.
source-only, 검증된 로컬 선택, humanReview=not_performed, 공개 권리 held를 독립적으로 유지한다.
지원한다고 표시한 구조의 wrong side/name/scope/placement와 실제 사용자 흐름 결함은 해결한다. 미지원 자료로 geometry/binding/승인을 만들지 않는다.
자동 계약 검사는 전수 수행하고 실제 시각 검증은 대표 유형·12부위·변경/충돌 사례에 집중한다. 동일 입력의 기존 근거는 영향 분석 후 재사용한다.
새 단서 없는 고정 catalog 검색·직접 용어 인용 검색·전체 suite/보고서 반복을 하지 않는다. 의미 검토 묶음은 내부 복구 단위다.
제품 계약을 충족하면 completed/passed, nextUnit=null로 종료하고 contentCompleteness=partial 및 남은 콘텐츠를 별도로 보고한다.
실제 제품 차단 결함이 남으면 실패 기능만 구체적으로 기록해 같은 task에서 고친다. 계획 문서만으로 pass하지 않는다.
해당 report/evidence와 EXECUTION record에 acceptanceScope/contractRevision/productReadiness/contentCompleteness/knownContentGaps/unresolvedProductBlockers를 기록한다.
합격 기록은 progress.productAcceptance에 contractRevision=app-completion-2026-10-01, acceptanceScope, productReadiness, contentCompleteness, knownContentGaps, unresolvedProductBlockers=[], evidence=[실제 보고서/검증 파일 경로]를 남긴다.
python3 work/tools/sync_execution.py 및 --check를 수행하고 소유 변경만 선별 로컬 커밋한다.
다음 task 자동 실행, 새 번호/스레드 발급, 자동 위임, push/배포, 임상 진단·치료·자침 기능은 금지한다.

이번 실행:
이번 범위: T47의 구조/기능/motion 감사를 흡수하여 현재 실제 지원 clip의 같은 surface/scene 변형과 사용자 흐름을 검증하고 화면 품질을 다듬는다. 표정근 exact clip 제외, 나머지 미지원 움직임, 실제 지원 clip을 구분한다. camera/layer/선택/설명·신경 pose의 동기를 확인한다. 전 근육 clip 확보와 지원 앱 품질 합격은 분리한다. 담당 Astra 현재 대화 직접 구현을 유지한다.

지원 clip 전체의 데이터/pose/player 계약과 family별 대표·변경 실제 화면을 감사한다. 움직임 없이 텍스트나 별도 viewer만 보이는 사례를 지원으로 세지 않는다. 실제 주변 관통·camera reset·layer 손실·잘못 고정된 정적 신경·설명 불일치·재생/복원 오류를 수정한다. 현재 앱의 구조/설명/신경/움직임 지원 범위와 콘텐츠 gap을 종합하여 scoped product acceptance를 판정한다. T47 별도 실행 또는 전 근육 제작 재개를 하지 않는다.

종료 후 다음 ID는 T40다. 다음 promptFile을 안내하고 멈춰라. 다른 task를 이번에 시작하지 마라.
```

<a id="t40"></a>
### T40 — 실행 가능한 로컬 앱 전달

```text
HUMAN ATLAS에서 T40만 수행해라. 담당 Luna Max.

AGENTS.md, work/EXECUTION.json, design/2026-09-25-muscle-atlas/27-APP-COMPLETION-AND-CONTENT-ROADMAP.md, work/product-acceptance.json,
해당 task의 현재 spec/promptFile, 실제 선행 report/evidence를 읽어라.
목표는 현재 지원 범위에서 정확하고 안정적으로 사용할 수 있는 앱이다. task acceptance와 전체 콘텐츠 completeness를 분리한다.
27 설계/현재 acceptanceContract가 과거 전체 콘텐츠 0-gap·full extent 전수 PNG·10개마다 종료 문구보다 우선한다.
542 target/563 membership/12부위, 기존 HA 130, 역사163(6/20/135/2), 원본/OpenSim_Models/T13/기존 WIP를 보존한다.
source-only, 검증된 로컬 선택, humanReview=not_performed, 공개 권리 held를 독립적으로 유지한다.
지원한다고 표시한 구조의 wrong side/name/scope/placement와 실제 사용자 흐름 결함은 해결한다. 미지원 자료로 geometry/binding/승인을 만들지 않는다.
자동 계약 검사는 전수 수행하고 실제 시각 검증은 대표 유형·12부위·변경/충돌 사례에 집중한다. 동일 입력의 기존 근거는 영향 분석 후 재사용한다.
새 단서 없는 고정 catalog 검색·직접 용어 인용 검색·전체 suite/보고서 반복을 하지 않는다. 의미 검토 묶음은 내부 복구 단위다.
제품 계약을 충족하면 completed/passed, nextUnit=null로 종료하고 contentCompleteness=partial 및 남은 콘텐츠를 별도로 보고한다.
실제 제품 차단 결함이 남으면 실패 기능만 구체적으로 기록해 같은 task에서 고친다. 계획 문서만으로 pass하지 않는다.
해당 report/evidence와 EXECUTION record에 acceptanceScope/contractRevision/productReadiness/contentCompleteness/knownContentGaps/unresolvedProductBlockers를 기록한다.
합격 기록은 progress.productAcceptance에 contractRevision=app-completion-2026-10-01, acceptanceScope, productReadiness, contentCompleteness, knownContentGaps, unresolvedProductBlockers=[], evidence=[실제 보고서/검증 파일 경로]를 남긴다.
python3 work/tools/sync_execution.py 및 --check를 수행하고 소유 변경만 선별 로컬 커밋한다.
다음 task 자동 실행, 새 번호/스레드 발급, 자동 위임, push/배포, 임상 진단·치료·자침 기능은 금지한다.

이번 실행:
이번 범위: 현재 지원 구조·설명·신경·움직임의 실제 scoped acceptance를 사용하여 로컬 실행/설치/asset 확보/검증/복구 안내와 전달 가능한 실행 경로를 완성한다. dev-server 전용 middleware가 필요한 기능을 dist 단독 실행으로 오인하지 않도록 실제 실행 방식을 검증한다. 권리 held/private 자료/비공개 원문을 배포 허가로 바꾸지 않는다. 평가/퀴즈와 미확보 콘텐츠의 추가 연구는 이번 전달의 선행 조건이 아니다.

실제 새 checkout 또는 독립 실행 조건에서 의존성과 asset locator/해시/서버 실행/복구 절차를 확인한다. source 원본을 무단 bundle하거나 private 원문을 넣지 않는다. 현재 앱의 지원 범위·알려진 한계·필수 실행 서버·라이선스 정보를 정확하게 전달한다. 검증된 콘텐츠와 지원 앱 task 완료를 전체 해부학/모든 신경/모든 clip 완성으로 쓰지 않는다. 로컬 전달만 수행하고 push/배포를 하지 않는다.

종료 후 다음 ID는 없음다. 다음 promptFile을 안내하고 멈춰라. 다른 task를 이번에 시작하지 마라.
```
