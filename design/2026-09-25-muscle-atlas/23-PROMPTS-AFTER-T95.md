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
| [T58](#t58) | SOL 6.1 · 현재 대화 직접 구현 | 앱 화면·관찰 UX·실측 성능 완성 |

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
| [T35](#t35) | Sol High | 전체 근육 움직임 범위·공통 제작 계약 |
| [T59](#t59) | Sol High | 전체 근육용 공통 변형·제작·재생 경로 |
| [T25](#t25) | Luna Max | 전체 근육 공통 움직임 학습 흐름 |
| [T66](#t66) | Luna Max | 전체 근육 변형 자산 제작·통합 |
| [T85](#t85) | Astra · 현재 대화 직접 구현 | 전체 지원 움직임·통합 앱 품질 감사 |

## G5 — 최종 로컬 전달

| ID | 담당 | 결과 |
|---|---|---|
| [T40](#t40) | Luna Max | 실행 가능한 로컬 앱과 전체 움직임 범위 전달 |

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
HUMAN ATLAS에서 T58만 수행해라. 담당 SOL 6.1 · 현재 대화 직접 구현.

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
1. T100/T80 새 계약의 passed, 실제 product-scope.json, T80 결함·개선 원장과 최신 UI를 확인한다. 오래된 전체 콘텐츠 gate나 역사 T57→T59 순서를 재실행하지 않는다. 담당 SOL 6.1, 현재 대화 직접 구현이며 자동 위임하지 않는다.
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


## T90에서 추가된 근육 기시·정지 후속 범위

T90 report와 work/evidence/T90/muscle-attachment-coverage.json, muscle-attachment-content-t90.json, learner-attachment-context.json을 먼저 읽는다. 현재 232개 지원 source 근육 중 22개(44 표면)에 설명 또는 충돌 안내가 있고, 210개(418 표면)의 기시·정지 설명과 긴종아리근 origin 충돌 1개가 남는다. T90의 새 15개 근육 설명·기시정지 뼈 문맥과 12부위 선택/숨김/복원은 유지한다.

신경 설명과 함께 주요 사용 흐름의 근육 기시·정지를 실제 카드에 더 채운다. 어깨·위팔의 자주 선택하는 근육/분절, 등 근육을 우선하고 기존 source별 projection을 확장한다. 신뢰할 수 있는 새 공식/학술 원문이 있는 묶음부터 직접 읽고 field locator/hash·정확한 source/side/part를 대조한다. 전체 근육 설명을 분절에 무조건 상속하지 않는다. 기존 고정 후보/용어 검색은 새 단서 없으면 반복하지 않는다. 나머지 210개의 0-gap 확보는 이 task의 일괄 완료 조건이 아니다.

새 설명의 명시한 부착 뼈만 같은 쪽 existing whole-bone context로 연결하고 부착점·좌표를 만들지 않는다. source-only·humanReview=not_performed·권리 held와 기존 HA130을 유지한다. 추가한 설명의 정확성·카드 접근·뼈 이동·지역 유지·숨김·복원을 실제 검사하고 미확보/충돌을 전수 원장으로 정리한다. 새 geometry나 임상 기능은 만들지 않는다. 이 추가 범위는 T65 한 task에 포함하며 다른 task 번호를 발급하지 않는다.

종료 후 다음 ID는 T35다. 다음 promptFile을 안내하고 멈춰라. 다른 task를 이번에 시작하지 마라.
```

<a id="t35"></a>
### T35 — 전체 근육 움직임 범위·공통 제작 계약

```text
HUMAN ATLAS에서 T35만 수행해라. 담당 Sol High.

AGENTS.md, work/EXECUTION.json, design/2026-09-25-muscle-atlas/27-APP-COMPLETION-AND-CONTENT-ROADMAP.md, work/product-acceptance.json,
해당 task의 현재 spec/promptFile, 실제 선행 report/evidence 및 design/2026-09-25-muscle-atlas/28-ALL-MUSCLE-MOTION-PIPELINE.md를 읽어라.
2026-10-02 최신 사용자 지시: 초기 확장 근육 목록 없이 전체 근육을 대상으로 한다. 28 설계가 미래 motion의 소수 파일럿/소흉근 중심 범위와 과거 표정근 제외 문구보다 우선한다. 27의 제품 acceptance/content completeness 분리는 유지한다.
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
이번 범위: 전체 근육 관련 429 target/447 membership과 현재 232 source 개념/462 표면을 빠짐없이 움직임 제작 대상으로 계획한다. 별도 초기 근육 목록을 두지 않는다. 실제 source/side/part/frame/rest pose/부착·작용/rig 가능성을 전수 disposition으로 연결한다. 관절·다관절·넓은 부착·반복/분절·비관절 연조직 family를 공통 같은-scene 계약으로 정리한다. 과거 표정근 제외는 최신 전 근육 지시로 대체하되 자료 없는 형상을 만들지 않는다. 계획 task이며 새 clip 제작은 T59/T66에서 한다.

1. 실제 T65 passed/report/evidence, 현재 App/정적 dataset loader/animation adapter/공통 controller를 읽어 현재 실제 motion 지원 0과 역사 T24 기술 candidate를 구분한다. 과거 blocked T24를 재실행하지 않는다.
2. 준비된 run-manifest 및 snapshots를 읽고 python3 work/tools/validate_motion_parallel_plan.py로 해시·429/232/462 전수 배정·중복 0을 검증한다. 입력이 같으면 배정을 다시 만들지 않는다. A/B/C는 사람이 별도 프롬프트로 실행할 수 있는 같은 T35 자료 준비 작업이다. 자동 위임/새 thread를 만들지 않는다.
3. 전체 target/source/part/group/side/action/pose의 움직임 원장을 만든다. 기시·정지31개 설명/201개 gap을 재사용하고 원문 locator와 source geometry/rig 입력의 부족을 구체적으로 연결한다. 전체 원장에서 임의로 쉬운 근육만 제외/선정하거나 몇 개 예시를 목표로 고정하지 않는다. 그룹/반복 family의 일부 구현을 전체로 세지 않는다.
4. 원문·좌표·pose·부착 근거와 source-derived authoring 선택을 구분한다. OpenSim은 해당 frame/관절/path를 검증할 수 있을 때 보조로 쓰며 전 근육 solver 설치를 일괄 선행 조건으로 만들지 않는다. 기존 source-only와 null canonical binding을 지원 제작의 일괄 차단으로 쓰지 않는다.
5. work/evidence/T35/motion-contract.json에 native source identity/hash/rest pose, sourceKey 기반 결속, derived skin/morph/corrective 변형, 움직이는 뼈·고정 구조·주변 수동 변형·관통 위험, 부분/좌우/동작 조건과 비관절 변형 유형의 계약을 정한다. 수치·pivot·정합을 근거 없이 채우지 않는다. 부족한 입력은 정확한 재개 조건으로 둔다. pipeline 표본은 전체 원장에서 검증 가능성에 따라 정하며 초기 확장 리스트가 아니다.
6. A/B/C 결과가 실제 있으면 --results 검사로 검증한 전수 결과만 통합한다. worker 실행은 선택 사항이며 없으면 같은 manifest 전수 규칙으로 현재 입력/제작 가능성 계획을 직접 처리한다. 아직 조사중인 필드는 unknown·필요 입력으로 남기고 없는 근거를 만들지 않는다. 전체 원장의 현재 상태/필요 작업과 검증된 공통 제작 계약을 완성하면 계획 task를 종료할 수 있으며, 모든 근육의 원문/clip 확보를 T59 시작의 일괄 조건으로 만들지 않는다. 실제 계획/공통 계약 자체가 미완이면 그 unit만 같은 T35에서 해결한다. 공통 작성자는 이 담당자 하나다.
7. T59가 공통 제작/player를 만들고 authoring-run-manifest를 실제 생성한 후 전체 자산을 병렬 제작하는 순서를 구체화한다. T35 합격은 전수 제작 계획/계약 완료이지 새 motion 구현 합격이 아니다. 전체 근육 목표를 소수의 clip 지원으로 축소하지 않는다.

종료 후 다음 ID는 T59다. 현재 promptFile을 안내하고 멈춰라. 다른 task를 이번에 시작하지 마라.
```

<a id="t59"></a>
### T59 — 전체 근육용 공통 변형·제작·재생 경로

```text
HUMAN ATLAS에서 T59만 수행해라. 담당 Sol High.

AGENTS.md, work/EXECUTION.json, design/2026-09-25-muscle-atlas/27-APP-COMPLETION-AND-CONTENT-ROADMAP.md, work/product-acceptance.json,
해당 task의 현재 spec/promptFile, 실제 선행 report/evidence 및 design/2026-09-25-muscle-atlas/28-ALL-MUSCLE-MOTION-PIPELINE.md를 읽어라.
2026-10-02 최신 사용자 지시: 초기 확장 근육 목록 없이 전체 근육을 대상으로 한다. 28 설계가 미래 motion의 소수 파일럿/소흉근 중심 범위와 과거 표정근 제외 문구보다 우선한다. 27의 제품 acceptance/content completeness 분리는 유지한다.
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
이번 범위: T35의 전체 근육 계약에 따라 같은 전신 scene에서 원본 source 표면의 derived 변형/관절 움직임을 제작하고 공통 player/CTA/취소/복원을 구현한다. 근육별 runtime 코드나 별도 viewer를 만들지 않는다. T60를 흡수한다. 실제 검증 표본은 공통 경로 검증 수단이며 전체 429 target/232 source 제작 범위를 축소하지 않는다. T66용 전수 authoring manifest와 hash/validator를 실제 남긴다.

1. T35 실제 report/전수 원장/motion-contract, 준비된 research manifest와 실제 A/B/C 근거를 읽는다. 전체 근육 목표와 현재 실제 제작 가능한 입력을 구분한다. 원본/OpenSim_Models을 수정하지 않는다.
2. 기존 static loader가 animation graph를 거부하고 geometry만 캐시하는 지점을 실제로 해결한다. 전체 glTF skeleton/skin/morph/clip graph를 유지하는 공통 motion adapter를 기존 scene 아래에 결속하고 sourceKey/frame/rest-pose/hash를 검증한다. AnimationSceneAdapter/player 정책과 controller.addUpdate를 재사용해 한 renderer/camera/frame clock을 유지한다.
3. reproducible exporter/derivation 경로와 source별 weights/morph/corrective 입력·관절/pose/family 패키지 계약을 구현한다. source geometry 공유 cache는 불변이며 instance별 deformation state를 분리한다. 관절 동작 재사용과 source별 부착/변형을 분리해 전체에 같은 scale 효과를 복사하지 않는다.
4. 전체 원장에서 선택한 실제 계약 검증 사례로 rest/중간/끝 pose·표면 변형·동반 뼈/수동 주변 근육·관통·좌우/part·원본 복귀를 확인한다. 희소/부채꼴/다관절/비관절 유형은 계약이 실제 지원하는 것과 미지원인 것을 명시한다. 이 표본 선택으로 제품 scope를 제한하지 않는다.
5. 명시 CTA 재생/pause/scrub/속도/reduced-motion, 선택/부위 변경·취소/late response/실패/unmount/context loss, user hidden/layer/selection/camera 복원을 구현한다. 움직이는 pose에서 정적 신경을 잘못 고정하지 않는다. 필요한 family만 lazy load하고 motion buffers/skin/morph를 cache 예산에 포함한다.
6. T66의 전체 source/target 제작을 위해 work/evidence/T59/authoring-run-manifest.json과 실제 manifest validator를 생성한다. 실제 계약·exporter·입력 hash, 모든 패키지의 owner/assigned IDs/dependency/출력 경로·미확보 작업을 기록한다. common rig/관절/sourceKey 정의는 단일 writer가 고정하고 A/B/C는 candidate package만 쓰게 한다. 이 파일과 전수 배정/입력 검사가 없으면 T59 인계를 완료로 쓰지 않는다.
7. 관련 자동 회귀·type/build·실제 현재 앱 재생→복원을 한 번 검증하고 측정/한계를 남긴다. 공통 경로 pass를 전체 근육 제작 완료로 쓰지 않는다. 다음은 T25, 전체 자산 제작/등록은 T66이다.

종료 후 다음 ID는 T25다. 현재 promptFile을 안내하고 멈춰라. 다른 task를 이번에 시작하지 마라.
```

<a id="t25"></a>
### T25 — 전체 근육 공통 움직임 학습 흐름

```text
HUMAN ATLAS에서 T25만 수행해라. 담당 Luna Max.

AGENTS.md, work/EXECUTION.json, design/2026-09-25-muscle-atlas/27-APP-COMPLETION-AND-CONTENT-ROADMAP.md, work/product-acceptance.json,
해당 task의 현재 spec/promptFile, 실제 선행 report/evidence 및 design/2026-09-25-muscle-atlas/28-ALL-MUSCLE-MOTION-PIPELINE.md를 읽어라.
2026-10-02 최신 사용자 지시: 초기 확장 근육 목록 없이 전체 근육을 대상으로 한다. 28 설계가 미래 motion의 소수 파일럿/소흉근 중심 범위와 과거 표정근 제외 문구보다 우선한다. 27의 제품 acceptance/content completeness 분리는 유지한다.
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
이번 범위: T59 공통 변형/player를 source별 구조/기능 카드와 연결하고 전체 원장의 motion 가용성을 정확히 표시한다. 현재 실제 자산의 탐색→선택→작용→재생→pause/scrub/처음 자세→복원을 검증한다. 자료/clip 미확보와 실제 지원을 분리한다. 한 파일럿의 성공을 전체 범위 완료로 세지 않는다.

1. T35/T59 실제 계약·자산·report/evidence 및 전수 motion 원장을 읽고 source/side/part/action 지원과 learner CTA의 상태를 데이터로 연결한다. HA ID가 없는 검증된 source muscle도 공통 sourceKey 경로를 사용하며 canonical binding을 만들지 않는다.
2. 같은 동작 family에서 선택 근육과 정확한 source 표면/설명이 바뀌는 흐름을 만들고, 작용 조건/여러 작용을 일반화하지 않는다. 내부 source/task/evidence 메타데이터를 학생 UI에 넣지 않는다.
3. 같은 scene의 근육 선택→기시/정지·작용→명시 CTA→몸 움직임과 실제 표면 변형→재생/정지/scrub/속도→rest 복원, 검색·양측·카드·키보드·뒤/앞·숨김을 확인한다. 지원되지 않은 신경 pose는 정확히 가리고 복원은 user layer 상태를 따른다.
4. 390/1024/1440 실제 UI와 관련 공통 계약을 검사하고 발견된 문제를 고친다. T66 자산 workers가 frozen contract 아래 candidate 폴더에서 작업할 수 있게 UI 입력 계약을 유지한다. common code는 이 writer만 변경한다.
5. 전체 target/source 원장과 잔여 제작 작업을 유지하고 실제 현재 공통 UI responsibility acceptance를 보고한다. 전체 근육 움직임 구현 완료를 선언하지 않는다. 다음 T66을 자동 실행하지 않는다.

종료 후 다음 ID는 T66다. 현재 promptFile을 안내하고 멈춰라. 다른 task를 이번에 시작하지 마라.
```

<a id="t66"></a>
### T66 — 전체 근육 변형 자산 제작·통합

```text
HUMAN ATLAS에서 T66 내부 unit 03만 수행해라. 담당 Luna Max · 현재 대화 직접 구현.

이번 입력 파일: work/plans/t66-serial-completion-2026-10-02/03-T66-shoulder-forearm-wrist.txt
계획: work/plans/t66-serial-completion-2026-10-02/README.md
직전 파일 work/plans/t66-serial-completion-2026-10-02/02-T66-hip-knee.txt의 실제 결과를 읽는다. 선행 산출이 없으면 완료로 추정하지 말고 누락된 구현을 먼저 이어받는다. 실패가 이번 입력/공통 계약을 막으면 해당 수정부터 수행하고, 의존하지 않는 콘텐츠 gap은 종료를 막지 않는다.

AGENTS.md, work/EXECUTION.json, work/product-acceptance.json, 해당 task 현재 spec/promptFile, design/2026-09-25-muscle-atlas/27-APP-COMPLETION-AND-CONTENT-ROADMAP.md와28-ALL-MUSCLE-MOTION-PIPELINE.md를 읽어라. 이번 직렬 계획 README와 실제 선행 unit REPORT/validation, work/reports/T66.md 및 work/evidence/T66/implementation-2026-10-02/{final-validation.json,final-blockers.json,family-queue.json}를 확인한다. T25/T59/A/B/C는 필요한 정확한 근거만 재사용한다. 자산 A/B/C의 JSON661개를 GLB661개로 세지 않는다.

최신 사용자 지정은 Luna Max·현재 대화 직접 구현·직렬이다. 과거 Astra/병렬 지시보다 우선한다. 계획/내부 unit은 새 task ID가 아니다. 새 agent/thread/자동 위임/다음 unit 자동 실행/push/배포/임상 기능/병리 editor를 금지한다. 작업 시작 시 dirty 파일/hash를 기록하고 다른 소유 WIP·과거 evidence를 덮지 않는다. 입력이 달라졌으면 영향 dependency만 재검증한다. r13 evidence/원본은 보존하고 새 명시 revision에 출력한다.

전체 근육/뼈/신경 목표와 현재 지원 범위의 제품 acceptance를 분리한다. 542target/563membership/12부위, 근육429/447/232source concepts/462surfaces, HA130·역사163(6/20/135/2), 원본/source-cache/OpenSim_Models/T13/기존 WIP를 보존한다. source-only/local selection/humanReview=not_performed/public rights held는 독립 상태다. source 행/label group을 독립 해부 개념으로 세지 않는다. 없는 mesh/좌우/관계/정확한 footprint/실측 정상축을 만들지 않는다. 실제 원본 관찰+검토된 정성 근거에 따른 재현 가능한 authored 교육용 masks/weights/pivots/trajectory/correctives는 직접 작성한다. native rig 부재만으로 engineering 책임을 자료 gap으로 돌리지 않는다.

기존 단일 viewport/scene/renderer/camera/controller/frame clock 및 common pose state를 유지한다. '움직임으로 이해하기' 하나: 클릭 반복 왕복, 재클릭 부드러운 rest 복원. 느리게/별도 pause/reset 버튼은 넣지 않는다. slider는 autoplay 중단/자세 유지, reduced-motion을 보존한다. 숨김/투명/layer/selection/history/카메라/취소를 재생이 덮지 않는다. T59 기존+30%를 다시 확대하지 않는다. 학생 화면에 task/source/evidence/내부 ID를 넣지 않는다. 필요한 권리 attribution은 기존 정책대로 유지한다.

자동 계약은 이번 지원/변경 집합 전체에 검사한다. 실제 UI는 가족 유형·좌우·변경/충돌·중간 pose를 확인하고 동일 입력 근거는 재사용한다. 전체 suite/12부위 전수 PNG/문헌 검색을 매 unit 반복하지 않는다. 관측하지 않은 GPU/VRAM/메모리는 추정치와 구분한다.

이번 실행은 T66 내부 unit 03만이다. shoulder-girdle/shoulder/elbow/forearm/wrist 가족의 현재 확보 source와 근거 있는 action 전체를 처리한다. 기존 굽힘·가쪽돌림·손목 굽힘 성공을 재사용하고 남은 action/좌우/갈래를 작성한다. 손가락 자체 가족은 unit 04가 맡는다.

1. fullSourceQueue와 검토된 기시·정지·작용 claims를 family/side/action에 연결한다. 예시 근육 몇 개로 범위를 제한하지 않는다. 관절 위상/견갑골·빗장뼈 협응, 전완 회내·회외에서 실제 source 맥락을 관찰하고 교육용 coupled trajectory/DOF/조합 범위를 작성한다. 모든 axis를 발목 r2에서 복사하지 않는다.
2. 가족 계약→source별 weights/masks/correctives→GLB→기하/부착/주변 조직 및 실제 export pose 검증→같은 scene 등록을 배정 큐 전체에 수행한다. 정확한 source identity/side/part에 결속 가능한 시범을 전체 target/group extent 승인까지 기다리게 하지 않는다.
3. 각 muscle action binding의 시범과 카드가 맞아야 한다. 관절 자세에 동반되는 수동 변형을 해당 근육의 주작용 시범으로 제공하지 않는다. 직접 근거 있는 작용을 보여줄 때 방향/부착/의미를 검사한다. 원문 근거 부족이면 작용 설명·자세 관찰·주작용 시범의 지원 상태를 나눈다.
4. 뼈 직접 선택→관절/역할/지원 action→재생/각도 관찰→복원을 같은 family로 연결한다. 한 뼈에 여러 family가 있으면 관련 action을 선택할 수 있게 한다. fixed support는 고정 역할을 안내하고 독립 DOF를 만들지 않는다.
5. 신규 협응/회내회외/변형 유형·좌우·변경 사례를 실제 브라우저에서 확인한다. 기존 동일 입력 화면과 전체 suite는 반복하지 않는다.

이번 성공 조건: 해당 5가족의 전수 책임 큐에서 engineering으로 제작 가능한 항목을 실제 생성·등록·연결하고 지원 결함을 해결한다. 실제 원본/관계 부족만 구체적 content gap으로 남긴다. 단순 미작성은 gap이 아니다.

작업 기록: work/evidence/T66/serial-completion-2026-10-02/unit-03/에 REPORT.md, 실제 validation 결과·자산/QC/화면 경로·입력 영향/hash를 남긴다. serial-queue.json의 해당 unit 책임 키에 implemented_verified / processed_with_content_gaps / blocked_by_product_defect를 실제 증거로 기록한다. 자료 gap은 missing source/identity/qualitative relation 등 구체적 자료 부족 근거가 있어야 한다. 단순 exporter/mask/trajectory/연결 미구현이나 기하 실패는 engineering blocker다. 원장만 작성하고 unit 성공으로 끝내지 않는다.

T66 내부 unit 01~10의 성공은 T66 전체 passed가 아니다. EXECUTION T66의 progress에 내부 진척과 제품 차단/콘텐츠 gap을 갱신하고 부모 nextUnit=author-and-integrate-normal-motion-bone-and-nerve 및 partial을 유지한다. spec에는 이번 책임을 내부 unit으로 명시하고 promptFile을 이번 파일로 기록하되 다른 task 상태는 바꾸지 않는다. T66 report는 짧은 진척/현재 차단 링크로 갱신하고 전면 재작성/전체 보고 반복은 unit11까지 하지 않는다. unit11은 본문의 최종 판정 규칙을 따른다. python3 work/tools/sync_execution.py와 --check를 수행하고 소유 변경만 선별 로컬 커밋한다.

종료 시 이번 실제 구현/지원 수와 unresolved engineering/content gap을 구분해 보고하고 멈춘다. 다음 수동 실행 파일은 work/plans/t66-serial-completion-2026-10-02/04-T66-hand-digits.txt이다. 실제 남은 선행 구현 차단이 있으면 재개할 파일도 명시한다. 다음 파일을 자동 실행하지 않는다.
```

<a id="t85"></a>
### T85 — 전체 지원 움직임·통합 앱 품질 감사

```text
HUMAN ATLAS에서 T85만 수행해라. 담당 Astra · 현재 대화 직접 구현.

AGENTS.md, work/EXECUTION.json, design/2026-09-25-muscle-atlas/27-APP-COMPLETION-AND-CONTENT-ROADMAP.md, work/product-acceptance.json,
해당 task의 현재 spec/promptFile, 실제 선행 report/evidence 및 design/2026-09-25-muscle-atlas/28-ALL-MUSCLE-MOTION-PIPELINE.md를 읽어라.
2026-10-02 최신 사용자 지시: 초기 확장 근육 목록 없이 전체 근육을 대상으로 한다. 28 설계가 미래 motion의 소수 파일럿/소흉근 중심 범위와 과거 표정근 제외 문구보다 우선한다. 27의 제품 acceptance/content completeness 분리는 유지한다.
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
이번 범위: T47 감사를 흡수해 전체 motion 원장에서 실제 지원하는 모든 clip/side/part/action 계약을 자동 검사하고 같은 source surface/scene 변형·신경 pose·카메라/선택/설명/복원/성능을 다듬는다. 미제작 전체 대상과 실제 지원을 분리하며 소수 예시 성공을 전체 근육 완성으로 표시하지 않는다. 담당 Astra 현재 대화 직접 구현을 유지한다.

1. T66의 전수 처리 결과와 지원 clip 목록을 실제 assets/runtime으로 대조한다. target429/source232를 보존하고 예시 clip/registry entry/부분 group을 전체 muscle support로 잘못 세는 오류를 수정한다.
2. 실제 같은 source graph/frame/rest pose, deformation/bones/passive context·중간 pose/관통·part·side·layer-off/held·취소/전환/복원·신경 pose를 전수 자동 계약 검사한다. 필요한 변경 사례의 실제 시각 검증에 집중하고 동일 입력 근거를 재사용한다.
3. 390/1024/1440에서 여러 deformation 유형과 전체 12지역 탐색→근육→작용→재생→설명→복원을 실제 검증한다. 전신 renderer/camera를 유지하고 선택 대비/깊이/가림/카메라 reset·검은 frame/console errors를 고친다.
4. cold/warm bytes/loading, render CPU/frame interval, active triangles/draws/geometry+animation bytes, 반복 clip/region 전환 후 cache/cancel/late response를 확인한다. 관측 불가 GPU/VRAM은 한계로 남기고 실제 budget을 몰래 상향하지 않는다.
5. 현재 지원 기능의 제품 blocker를 해결한다. 전체 근육 움직임 목표의 진짜 구현율·남은 anatomy/source/rig/clip 작업과 local_app_ready를 별도 기록한다. 전체가 실제 구현되지 않았다면 wholeMuscleMotionGoal=complete로 쓰지 않는다. 다음 T40은 실행하지 않는다.

종료 후 다음 ID는 T40다. 현재 promptFile을 안내하고 멈춰라. 다른 task를 이번에 시작하지 마라.
```

<a id="t40"></a>
### T40 — 실행 가능한 로컬 앱과 전체 움직임 범위 전달

```text
HUMAN ATLAS에서 T40만 수행해라. 담당 Luna Max.

AGENTS.md, work/EXECUTION.json, design/2026-09-25-muscle-atlas/27-APP-COMPLETION-AND-CONTENT-ROADMAP.md, work/product-acceptance.json,
해당 task의 현재 spec/promptFile, 실제 선행 report/evidence 및 design/2026-09-25-muscle-atlas/28-ALL-MUSCLE-MOTION-PIPELINE.md를 읽어라.
2026-10-02 최신 사용자 지시: 초기 확장 근육 목록 없이 전체 근육을 대상으로 한다. 28 설계가 미래 motion의 소수 파일럿/소흉근 중심 범위와 과거 표정근 제외 문구보다 우선한다. 27의 제품 acceptance/content completeness 분리는 유지한다.
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
이번 범위: 현재 지원 구조·설명·신경·움직임의 실제 scoped acceptance를 사용해 로컬 실행/설치/asset 확보/검증/복구 경로를 완성한다. 전체 근육 motion 목표의 전수 구현·미확보/미구현 원장을 함께 전달하며 sample 기능을 전체 완성으로 오인하지 않는다. dev middleware/asset 확보와 dist 단독 실행을 실제 구분한다. held/private/humanReview 상태를 보존한다.

1. T85 실제 report/evidence와 모든 지원 asset의 실행 입력을 읽고 재현 가능한 로컬 앱 실행·asset 확보·검증/복구 절차를 완성한다. dev middleware가 필요한 상태를 dist만 실행하면 되는 것으로 전달하지 않는다.
2. 실제 구조/설명/신경/움직임의 지원 경로와 전체 target/source/side/action 원장을 대조한다. 429 muscle target/232 source 전수 목표에 남은 작업을 삭제하거나 첫 표본 성공으로 전체 지원이라고 광고하지 않는다.
3. 기존 제품 acceptance를 이유 없이 반복하지 않고 전달 실행 방식의 실제 차단 결함을 해결한다. private 원문/원본/OpenSim_Models·T13/WIP·held권리·humanReview를 보존하며 push/배포하지 않는다.
4. 해당 로컬 전달 책임을 끝내면 정확한 readiness/contentCompleteness/wholeMuscleMotionGoal와 근거를 남기고 멈춘다. 새 task/전체 완료 추정/임상 기능은 만들지 않는다.

종료 후 자동 실행할 task는 없다. 실제 전달 상태를 보고하고 멈춰라.
```
