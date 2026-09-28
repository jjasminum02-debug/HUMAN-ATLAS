# 현행 실행 순서와 프롬프트

자동 생성 · 원본: `work/EXECUTION.json` · `python3 work/tools/sync_execution.py --check`로 일치 검증.

이 파일의 과거 T95/T102 시점 안내는 Git 이력으로 보존된다. 현재 next는 [work/NEXT.md](../../work/NEXT.md)에서 확인한다. 완료한 과거 작업은 반복하지 않는다.

25-WHOLE-BODY-BASE-RESET.md가 변경한 범위가 우선한다. 기존 T105–109/T110–121/T166의 필요한 내용은 새 범위의 T98/T99/T100/T80/T58로 흡수됐으며 별도 실행하지 않는다. T122–165도 미실행 폐기 상태다.

## G1 — 전신 구조·선택·관찰

| ID | 담당 | 결과 |
|---|---|---|
| [T98](#t98) | Luna Max | 전신 source inventory·변환 검증·주 베이스 선택 |
| [T99](#t99) | Sol High | 공통 dataset compiler·일괄 변환·경량 로더 |
| [T100](#t100) | Luna Max | 전신 근육·뼈 통합·지역/좌우·선택·핵심 관찰 |
| [T80](#t80) | Luna Max | 전신 구조·선택 전수 감사와 누락 보완 |
| [T58](#t58) | Astra · 현재 대화 직접 구현 | 전신 그래픽·관찰 UX·성능 합격 |

## G2 — 기시정지·기능·짧은 신경 정보

| ID | 담당 | 결과 |
|---|---|---|
| [T81](#t81) | Luna Max | 전체 기시·정지 및 짧은 신경 표기 검증·카드 연결 |
| [T82](#t82) | Luna Max | 전신 기시·정지 프로토타입 합격 |
| [T83](#t83) | Luna Max | 전체 한글 기능 설명 검증·카드 연결 |
| [T84](#t84) | Luna Max | 전신 근육 기능 설명 합격 |

## G3 — 신경 조사·지배·주행·기능이상 교육

| ID | 담당 | 결과 |
|---|---|---|
| [T61](#t61) | Sol High | 신경 레이어·좌표·관계 공통 계약 |
| [T86](#t86) | Sol High | 전체 신경 목표·기존 source 전수 대조 |
| [T62](#t62) | Luna Max | 첫 하지 신경 자료 패키지 |
| [T87](#t87) | Luna Max | 전신 신경 조사 확장 첫 batch |
| [T88](#t88) | Sol High | 전신 신경 자료 통합·등록 검증 |
| [T63](#t63) | Sol High | 첫 신경 3D 주행과 지배근 강조 |
| [T89](#t89) | Luna Max | 전신 신경 3D 확장 첫 batch |
| [T90](#t90) | Astra · 현재 대화 직접 구현 | 전신 신경 주행·지배근 그래픽 합격 |
| [T64](#t64) | Luna Max | 신경 포착·기능 변화의 접힌 설명 UI |
| [T91](#t91) | Luna Max | 신경 포착·기능이상 설명 확장 첫 batch |
| [T65](#t65) | Luna Max | 전체 신경·지배·기능이상 교육 통합 합격 |

## G4 — 같은 모형의 근육 움직임

| ID | 담당 | 결과 |
|---|---|---|
| [T35](#t35) | Sol High | 근육 움직임 제작 범위와 재사용 family 동결 |
| [T59](#t59) | Sol High | 같은 앞정강근 표면의 교육용 수축 변형 |
| [T60](#t60) | Sol High | 동일 viewport에서 운동 재생 연결 |
| [T25](#t25) | Luna Max | 같은 전신 모형의 앞정강근 제품 합격 |
| [T27](#t27) | Sol High | 소흉근 동일 모형 변형 준비 |
| [T28](#t28) | Sol High | 견갑대 운동 기반과 전인 시범 하나 |
| [T45](#t45) | Sol High | 소흉근 관련 견갑골 하강 시범 |
| [T46](#t46) | Sol High | 소흉근 관련 견갑골 하방회전 시범 |
| [T29](#t29) | Luna Max | 소흉근 구조·기능 사용자 흐름 통합 |
| [T31](#t31) | Luna Max | 두 부위 구조·기능 파일럿 합격 검증 |
| [T66](#t66) | Luna Max | 첫 기능 확장 batch 하나 |
| [T47](#t47) | Luna Max | 전신 구조·기능·운동 자료 감사 |
| [T85](#t85) | Astra · 현재 대화 직접 구현 | 필수 근육 움직임 합격·표정근 제외 별도 |

## G5 — 최종 로컬 전달

| ID | 담당 | 결과 |
|---|---|---|
| [T40](#t40) | Luna Max | 구조·기능 로컬 전달과 Git 체크포인트 |

## 붙여 넣기 — 한 번에 한 ID

<a id="t98"></a>
### T98 — 전신 source inventory·변환 검증·주 베이스 선택

```text
HUMAN ATLAS에서 T98만 수행해라. 담당 Luna Max.
AGENTS.md, work/EXECUTION.json, work/NEXT.md, 최신 STATUS의 generated execution 블록,
design/2026-09-25-muscle-atlas/25-WHOLE-BODY-BASE-RESET.md와 해당 task 명세, 실제 선행 report/evidence/manifest를 읽어라.
EXECUTION이 현재 범위/순서의 유일한 원본이다. 역사 queue의 nextTask를 실행하지 마라. 24의 엑셀 검증·한글 기능·짧은 신경·표정근 motion 제외는 유지한다.
이번 범위: T97 pinned archive/BP3D metadata/cache/T96 전체 target 및 T104까지 최신 WIP·evidence를 읽는다. 25 설계 3절의 전체 Object/Mesh/Collection/curve/helper/instance와 source 권리 상속·예외를 대조한다. canonical concept·geometry·instance·file 분모를 구분하고12부위 필수 전체 목록을 freeze한다. Z-Anatomy는 우선 후보이며 actual evaluated geometry 변환/좌우·pose/권리/포괄성/비용으로 주 베이스를 선택한다. 정확히 동결한8–12개 대표 object의 실제 exporter spike와 preview/hash를 남긴다. T97 Metal 실패를 같은 방식으로 반복하지 않고 검증된 headless/export 경로를 확인한다. raw 배열을 modifier/instance 결과로 오인하지 않는다. 모든 source를 다시 다운로드하거나 광배근만 검사하고 완료하지 않는다. source inventory만 있고 exporter가 미검증이면 partial. 웹 runtime/다음 task를 구현하지 않는다.
시작 HEAD/status/hash를 기록하고 원본/OpenSim_Models/사용자 WIP/T13 drafts/역사 freeze를 보존한다. source-only/권리/사람검토를 추정 승격하지 않는다.
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
design/2026-09-25-muscle-atlas/25-WHOLE-BODY-BASE-RESET.md와 해당 task 명세, 실제 선행 report/evidence/manifest를 읽어라.
EXECUTION이 현재 범위/순서의 유일한 원본이다. 역사 queue의 nextTask를 실행하지 마라. 24의 엑셀 검증·한글 기능·짧은 신경·표정근 motion 제외는 유지한다.
이번 범위: T98 실제 exporter와 선택된 source snapshot이 선행이다. 25 설계4절대로 source adapter→공통 schema/검증→overview/detail chunk와compact catalog를 생성한다. 기존 BP3D subset 재현과 전체 frozen dataset 변환을 같은 파이프라인으로 검증한다. task별 TypeScript extension/parent-chain/plugin 분기를 추가하지 말고 revision당 검증한 generic manifest로 바꾼다. source namespace/object instance/shared geometry/개념 binding/frame/rest pose와hold를 독립 보존한다. 전신overview와 상세LOD, byte-budget LRU/pin/해제/취소를 구현하고 geometry추가당 runtime 코드0을 검증한다. 원본/역사 cache·freeze는 변경하지 않는다. T98 대표12개만 변환하고 전체compile 완료라 하지 않는다. 새 기준은 manifest·resource·정합·품질·성능 회귀로 검증하며 learner의 전체 이름/선택 연결은 T100에 맡긴다.
시작 HEAD/status/hash를 기록하고 원본/OpenSim_Models/사용자 WIP/T13 drafts/역사 freeze를 보존한다. source-only/권리/사람검토를 추정 승격하지 않는다.
공통 도구와 단일 scene/renderer/camera를 재사용한다. 자동 전수처리와 내부 의미검증 unit을 구분하며 미완이면 같은 task/nextUnit으로 재개한다. 새 번호를 반복 발급하지 마라.
관련 실제 검증·progress·report/evidence를 남기고 EXECUTION의 해당 task record만 갱신한다. python3 work/tools/sync_execution.py와 --check로 투영 문서를 동기화한다.
소유 파일/hunk만 선별 로컬 커밋하고 해시·포함/제외·잔여 WIP·다음 프롬프트를 남긴 뒤 멈춰라.
기본 다음 ID: T100. 필수 gate 미달이면 먼저 같은 task를 재개하고 다음 task를 자동 실행하지 마라. push·배포·진단·치료·침 시뮬레이션 금지.
```

<a id="t100"></a>
### T100 — 전신 근육·뼈 통합·지역/좌우·선택·핵심 관찰

```text
HUMAN ATLAS에서 T100만 수행해라. 담당 Luna Max.
AGENTS.md, work/EXECUTION.json, work/NEXT.md, 최신 STATUS의 generated execution 블록,
design/2026-09-25-muscle-atlas/25-WHOLE-BODY-BASE-RESET.md와 해당 task 명세, 실제 선행 report/evidence/manifest를 읽어라.
EXECUTION이 현재 범위/순서의 유일한 원본이다. 역사 queue의 nextTask를 실행하지 마라. 24의 엑셀 검증·한글 기능·짧은 신경·표정근 motion 제외는 유지한다.
이번 범위: T98 전체 target와 T99 실제 전체dataset 산출물을 사용한다. 25 설계5절에 따라 하나의 scene에 전신bones/muscles를 넣고12부위/복수region/좌우/세 이름/검색/typed card를 전체coverage matrix로 연결한다. T105–121의 exact 대상/보류/지역자료를 내부workUnits로 흡수하고 historical source나 ID를 삭제하지 않는다. 얼굴표정근/광배근/양측상완/견갑골/요추·엉치뼈/손발·골반바닥을 빠뜨리지 않는다. source-only 관찰과 canonical 학습 선택은 별도이며 이름만으로binding을 만들지 않는다. 기존controller를 재사용해 주변흐림·선택반투명·숨김·격리·맞춤·undo/복원 핵심을 함께 구현한다. held/layer-off를 복원으로 노출하지 않는다. 전체overview에서 시작하고 camera연속성/미니멀UI를 지킨다. 표정근motion은disabled, 새애니메이션·신경3D·검증전엑셀본문은 넣지 않는다. 내부최대10개 의미검증 단위/같은T100 재개이며 첫부위를 전신완료로 부르지 않는다. 실제12부위·선택·성능evidence가필수다.
시작 HEAD/status/hash를 기록하고 원본/OpenSim_Models/사용자 WIP/T13 drafts/역사 freeze를 보존한다. source-only/권리/사람검토를 추정 승격하지 않는다.
공통 도구와 단일 scene/renderer/camera를 재사용한다. 자동 전수처리와 내부 의미검증 unit을 구분하며 미완이면 같은 task/nextUnit으로 재개한다. 새 번호를 반복 발급하지 마라.
관련 실제 검증·progress·report/evidence를 남기고 EXECUTION의 해당 task record만 갱신한다. python3 work/tools/sync_execution.py와 --check로 투영 문서를 동기화한다.
소유 파일/hunk만 선별 로컬 커밋하고 해시·포함/제외·잔여 WIP·다음 프롬프트를 남긴 뒤 멈춰라.
기본 다음 ID: T80. 필수 gate 미달이면 먼저 같은 task를 재개하고 다음 task를 자동 실행하지 마라. push·배포·진단·치료·침 시뮬레이션 금지.
```

<a id="t80"></a>
### T80 — 전신 구조·선택 전수 감사와 누락 보완

```text
HUMAN ATLAS에서 T80만 수행해라. 담당 Luna Max.
AGENTS.md, work/EXECUTION.json, work/NEXT.md, 최신 STATUS의 generated execution 블록,
design/2026-09-25-muscle-atlas/25-WHOLE-BODY-BASE-RESET.md와 해당 task 명세, 실제 선행 report/evidence/manifest를 읽어라.
EXECUTION이 현재 범위/순서의 유일한 원본이다. 역사 queue의 nextTask를 실행하지 마라. 24의 엑셀 검증·한글 기능·짧은 신경·표정근 motion 제외는 유지한다.
이번 범위: 25 설계6절에 따라 전체 frozen mandatory target의geometry/side/part/세이름/학습선택/지역맥락을 전수 대조한다. 파일수나object수가 아니라target mapping으로 합격을 판정한다. 모든542개 기존 target의 포함/그룹/변이/alias/미확보 처분을 설명하고 필수누락을 제외해서합격률을올리지않는다. 얼굴/광배근/양측견갑골/요추·엉치/손발/샅에 실제표면과선택이 있어야한다. 관찰source-only는학습완료가아니다. 데이터수정은공통pipeline으로해당unit을보완하고 exporter/geometry문제는같은T99/T100 미완에연결한다. 필수결함이남으면partial이고T58제품합격을예고하지않는다.
시작 HEAD/status/hash를 기록하고 원본/OpenSim_Models/사용자 WIP/T13 drafts/역사 freeze를 보존한다. source-only/권리/사람검토를 추정 승격하지 않는다.
공통 도구와 단일 scene/renderer/camera를 재사용한다. 자동 전수처리와 내부 의미검증 unit을 구분하며 미완이면 같은 task/nextUnit으로 재개한다. 새 번호를 반복 발급하지 마라.
관련 실제 검증·progress·report/evidence를 남기고 EXECUTION의 해당 task record만 갱신한다. python3 work/tools/sync_execution.py와 --check로 투영 문서를 동기화한다.
소유 파일/hunk만 선별 로컬 커밋하고 해시·포함/제외·잔여 WIP·다음 프롬프트를 남긴 뒤 멈춰라.
기본 다음 ID: T58. 필수 gate 미달이면 먼저 같은 task를 재개하고 다음 task를 자동 실행하지 마라. push·배포·진단·치료·침 시뮬레이션 금지.
```

<a id="t58"></a>
### T58 — 전신 그래픽·관찰 UX·성능 합격

```text
HUMAN ATLAS에서 T58만 수행해라. 담당 Astra · 현재 대화 직접 구현.
AGENTS.md, work/EXECUTION.json, work/NEXT.md, 최신 STATUS의 generated execution 블록,
design/2026-09-25-muscle-atlas/25-WHOLE-BODY-BASE-RESET.md와 해당 task 명세, 실제 선행 report/evidence/manifest를 읽어라.
EXECUTION이 현재 범위/순서의 유일한 원본이다. 역사 queue의 nextTask를 실행하지 마라. 24의 엑셀 검증·한글 기능·짧은 신경·표정근 motion 제외는 유지한다.
이번 범위: T80의 실제전신구조gate가선행이다. 25 설계4–6절의overview/detail전환·같은scene/camera·핵심관찰도구·패널가림을1440/1024/390px에서실제로검증하고필요한공통UI수정만한다. 얼굴/광배근/양측부위/손발/샅의빈형상을감추지않는다. cold/warm bytes, frameinterval과실제render시간, triangles/draws/geometrybytes,20회지역전환LRU안정성,키보드·터치·콘솔을검증한다. 설계성능예산과기준대비20%악화guard를자동상향하지않는다.390pxdesktop은실제모바일합격이아니다. 로딩의로고·인체그림·슬로건제거유지. source/publicrights/humanreview와제품gate를구분하고prototype완료를공개배포허가로쓰지않는다.
시작 HEAD/status/hash를 기록하고 원본/OpenSim_Models/사용자 WIP/T13 drafts/역사 freeze를 보존한다. source-only/권리/사람검토를 추정 승격하지 않는다.
공통 도구와 단일 scene/renderer/camera를 재사용한다. 자동 전수처리와 내부 의미검증 unit을 구분하며 미완이면 같은 task/nextUnit으로 재개한다. 새 번호를 반복 발급하지 마라.
관련 실제 검증·progress·report/evidence를 남기고 EXECUTION의 해당 task record만 갱신한다. python3 work/tools/sync_execution.py와 --check로 투영 문서를 동기화한다.
소유 파일/hunk만 선별 로컬 커밋하고 해시·포함/제외·잔여 WIP·다음 프롬프트를 남긴 뒤 멈춰라.
기본 다음 ID: T81. 필수 gate 미달이면 먼저 같은 task를 재개하고 다음 task를 자동 실행하지 마라. push·배포·진단·치료·침 시뮬레이션 금지.
```

<a id="t81"></a>
### T81 — 전체 기시·정지 및 짧은 신경 표기 검증·카드 연결

```text
HUMAN ATLAS에서 T81만 수행해라. 담당 Luna Max.
AGENTS.md, work/EXECUTION.json, work/NEXT.md, 최신 STATUS의 generated execution 블록,
design/2026-09-25-muscle-atlas/25-WHOLE-BODY-BASE-RESET.md와 해당 task 명세, 실제 선행 report/evidence/manifest를 읽어라.
EXECUTION이 현재 범위/순서의 유일한 원본이다. 역사 queue의 nextTask를 실행하지 마라. 24의 엑셀 검증·한글 기능·짧은 신경·표정근 motion 제외는 유지한다.
이번 범위: 24 설계 3절에 따라 사용자 엑셀을 원본 hash/시트/셀 위치와 함께 한 번 import한다. 근육표 A6:H262 257행을 T96/T80의 전체 학습 target과 매핑하고 원문·정규화 후보·검증 claim을 분리한다. private 원본/전체 staging은 ignore 경로, 공개 근거로 검증한 필요한 overlay만 제품/저장소에 반영한다. 첫 내부 단위는 6,12,22,23,44,133,139,229,186,246행이며 표본 합격을 전체 검증으로 세지 않는다. 이후 전체 근육의 기시정지와 workbook의 운동/감각 신경란을 기존 근거 재사용·독립 대조로 조사한다. 운동과 감각을 구분하고 모호한 가지/신경근은 생략, 미확인은 미기재/빈칸, 검증된 상위 신경명만 간결하게 쓴다. 감각 단일 이름 부재를 운동신경 미확인 대체값으로 쓰지 않는다. 동명 손/발·전체/갈래·8개 원본 영역 대12제품 지역을 정확히 구분한다. 엑셀 밖 target도 빠뜨리지 않는다. 내부 ≤10개 workUnits/같은 T81 재개, 모든 행 처리 상태와 claim별 근거/충돌/채택을 남긴다. 기시정지 칸의 출처 노출 금지, 3D 부착좌표/애니메이션/신경3D 추정 금지. 기능 H열은 원본/후보만 보관하며 최종 검증/공개는 T83에서 수행한다.
시작 HEAD/status/hash를 기록하고 원본/OpenSim_Models/사용자 WIP/T13 drafts/역사 freeze를 보존한다. source-only/권리/사람검토를 추정 승격하지 않는다.
공통 도구와 단일 scene/renderer/camera를 재사용한다. 자동 전수처리와 내부 의미검증 unit을 구분하며 미완이면 같은 task/nextUnit으로 재개한다. 새 번호를 반복 발급하지 마라.
관련 실제 검증·progress·report/evidence를 남기고 EXECUTION의 해당 task record만 갱신한다. python3 work/tools/sync_execution.py와 --check로 투영 문서를 동기화한다.
소유 파일/hunk만 선별 로컬 커밋하고 해시·포함/제외·잔여 WIP·다음 프롬프트를 남긴 뒤 멈춰라.
기본 다음 ID: T82. 필수 gate 미달이면 먼저 같은 task를 재개하고 다음 task를 자동 실행하지 마라. push·배포·진단·치료·침 시뮬레이션 금지.
```

<a id="t82"></a>
### T82 — 전신 기시·정지 프로토타입 합격

```text
HUMAN ATLAS에서 T82만 수행해라. 담당 Luna Max.
AGENTS.md, work/EXECUTION.json, work/NEXT.md, 최신 STATUS의 generated execution 블록,
design/2026-09-25-muscle-atlas/25-WHOLE-BODY-BASE-RESET.md와 해당 task 명세, 실제 선행 report/evidence/manifest를 읽어라.
EXECUTION이 현재 범위/순서의 유일한 원본이다. 역사 queue의 nextTask를 실행하지 마라. 24의 엑셀 검증·한글 기능·짧은 신경·표정근 motion 제외는 유지한다.
이번 범위: 24 설계의 T81 전체 target 기시정지/명칭/카드 및 257행 mapping/처리 상태를 감사한다. 표본10행만으로 전체를 승인하지 않는다. 운동신경/감각 분리, 미확인 short/null, 기존 출처 내부 보존과 private 원본 bundle 제외를 확인한다. 검증 못한 신경 세부 가지는 짧은 상위명 또는 미기재로 허용하되 이를 검증된 지배 관계로 세지 않고 후반 신경 조사 queue에 명시한다. 얼굴 포함 필수 기시정지 누락은 실패, human review는 독립 상태다.
시작 HEAD/status/hash를 기록하고 원본/OpenSim_Models/사용자 WIP/T13 drafts/역사 freeze를 보존한다. source-only/권리/사람검토를 추정 승격하지 않는다.
공통 도구와 단일 scene/renderer/camera를 재사용한다. 자동 전수처리와 내부 의미검증 unit을 구분하며 미완이면 같은 task/nextUnit으로 재개한다. 새 번호를 반복 발급하지 마라.
관련 실제 검증·progress·report/evidence를 남기고 EXECUTION의 해당 task record만 갱신한다. python3 work/tools/sync_execution.py와 --check로 투영 문서를 동기화한다.
소유 파일/hunk만 선별 로컬 커밋하고 해시·포함/제외·잔여 WIP·다음 프롬프트를 남긴 뒤 멈춰라.
기본 다음 ID: T83. 필수 gate 미달이면 먼저 같은 task를 재개하고 다음 task를 자동 실행하지 마라. push·배포·진단·치료·침 시뮬레이션 금지.
```

<a id="t83"></a>
### T83 — 전체 한글 기능 설명 검증·카드 연결

```text
HUMAN ATLAS에서 T83만 수행해라. 담당 Luna Max.
AGENTS.md, work/EXECUTION.json, work/NEXT.md, 최신 STATUS의 generated execution 블록,
design/2026-09-25-muscle-atlas/25-WHOLE-BODY-BASE-RESET.md와 해당 task 명세, 실제 선행 report/evidence/manifest를 읽어라.
EXECUTION이 현재 범위/순서의 유일한 원본이다. 역사 queue의 nextTask를 실행하지 마라. 24의 엑셀 검증·한글 기능·짧은 신경·표정근 motion 제외는 유지한다.
이번 범위: 24 설계 3/6절에 따라 T81의 workbook staging/매핑/검증 기록을 재사용하고 전체 target의 기능을 조사·교차 검증한다. H열 한자 포함53셀은 한글만으로 정규화하되 의미/방향/고정 조건/괄호 설명을 보존한다. 한자 제거만으로 정확성 확인이라 하지 않는다. 손/발 동명 근육과 부분별 작용을 대조한다. 표정근도 기능 설명은 필수이며 버튼은 움직임으로 이해하기 위치에 disabled 현재 미지원으로 둔다. 지원하지 않는 얼굴 clip/가짜 움직임/별도 scene는 만들지 않는다. 엑셀 밖 근육도 조사하고 기존 검증 claim은 재사용한다. CJK 한자 0건, claim 출처와 UI 채택 상태 분리, 전체 카드 표시를 검증한다. 내부 ≤10개 workUnits로 같은 T83 재개, 전체 설명 완료 전 T84로 넘기지 않는다.
시작 HEAD/status/hash를 기록하고 원본/OpenSim_Models/사용자 WIP/T13 drafts/역사 freeze를 보존한다. source-only/권리/사람검토를 추정 승격하지 않는다.
공통 도구와 단일 scene/renderer/camera를 재사용한다. 자동 전수처리와 내부 의미검증 unit을 구분하며 미완이면 같은 task/nextUnit으로 재개한다. 새 번호를 반복 발급하지 마라.
관련 실제 검증·progress·report/evidence를 남기고 EXECUTION의 해당 task record만 갱신한다. python3 work/tools/sync_execution.py와 --check로 투영 문서를 동기화한다.
소유 파일/hunk만 선별 로컬 커밋하고 해시·포함/제외·잔여 WIP·다음 프롬프트를 남긴 뒤 멈춰라.
기본 다음 ID: T84. 필수 gate 미달이면 먼저 같은 task를 재개하고 다음 task를 자동 실행하지 마라. push·배포·진단·치료·침 시뮬레이션 금지.
```

<a id="t84"></a>
### T84 — 전신 근육 기능 설명 합격

```text
HUMAN ATLAS에서 T84만 수행해라. 담당 Luna Max.
AGENTS.md, work/EXECUTION.json, work/NEXT.md, 최신 STATUS의 generated execution 블록,
design/2026-09-25-muscle-atlas/25-WHOLE-BODY-BASE-RESET.md와 해당 task 명세, 실제 선행 report/evidence/manifest를 읽어라.
EXECUTION이 현재 범위/순서의 유일한 원본이다. 역사 queue의 nextTask를 실행하지 마라. 24의 엑셀 검증·한글 기능·짧은 신경·표정근 motion 제외는 유지한다.
이번 범위: 전체 target의 한글 기능 설명/갈래/조건과 구조의 일관성을 감사한다. 53개 한자 포함 action cell의 의미 보존 및 runtime action 한자0건, 검증 원문과 짧은 UI 분리를 확인한다. 표정근은 설명/구조 필수, 애니메이션만 사용자 제외임을 확인한다. 단순 문자 변환이나 첫 batch를 전수 해부학 검증으로 세지 않는다. 필수 내용 미완이면 해당 unit을 보완하고 T35로 자동 진입하지 않는다.
시작 HEAD/status/hash를 기록하고 원본/OpenSim_Models/사용자 WIP/T13 drafts/역사 freeze를 보존한다. source-only/권리/사람검토를 추정 승격하지 않는다.
공통 도구와 단일 scene/renderer/camera를 재사용한다. 자동 전수처리와 내부 의미검증 unit을 구분하며 미완이면 같은 task/nextUnit으로 재개한다. 새 번호를 반복 발급하지 마라.
관련 실제 검증·progress·report/evidence를 남기고 EXECUTION의 해당 task record만 갱신한다. python3 work/tools/sync_execution.py와 --check로 투영 문서를 동기화한다.
소유 파일/hunk만 선별 로컬 커밋하고 해시·포함/제외·잔여 WIP·다음 프롬프트를 남긴 뒤 멈춰라.
기본 다음 ID: T61. 필수 gate 미달이면 먼저 같은 task를 재개하고 다음 task를 자동 실행하지 마라. push·배포·진단·치료·침 시뮬레이션 금지.
```

<a id="t61"></a>
### T61 — 신경 레이어·좌표·관계 공통 계약

```text
HUMAN ATLAS에서 T61만 수행해라. 담당 Sol High.
AGENTS.md, work/EXECUTION.json, work/NEXT.md, 최신 STATUS의 generated execution 블록,
design/2026-09-25-muscle-atlas/25-WHOLE-BODY-BASE-RESET.md와 해당 task 명세, 실제 선행 report/evidence/manifest를 읽어라.
EXECUTION이 현재 범위/순서의 유일한 원본이다. 역사 queue의 nextTask를 실행하지 마라. 24의 엑셀 검증·한글 기능·짧은 신경·표정근 motion 제외는 유지한다.
이번 범위: G1 전신 구조/선택과T84 기능설명 합격후 신경계약을 구현한다. 전근육motion완료를 기다리지 않는다. T98에서확보한신경inventory/sourceIDs/namespace/frame를재사용한다. sourcecurve/mesh와canonical nerve/branch, verified muscle-innervation관계를분리하며같은scene의layer와typed selection/card계약을 만든다. 감각영역/피부분절/경락을혼합하지않는다. 신경3D자료의정확성/지배관계를단순source이름으로추정하지않는다. 후속T86의동결범위와T62파일럿을준비한다.
시작 HEAD/status/hash를 기록하고 원본/OpenSim_Models/사용자 WIP/T13 drafts/역사 freeze를 보존한다. source-only/권리/사람검토를 추정 승격하지 않는다.
공통 도구와 단일 scene/renderer/camera를 재사용한다. 자동 전수처리와 내부 의미검증 unit을 구분하며 미완이면 같은 task/nextUnit으로 재개한다. 새 번호를 반복 발급하지 마라.
관련 실제 검증·progress·report/evidence를 남기고 EXECUTION의 해당 task record만 갱신한다. python3 work/tools/sync_execution.py와 --check로 투영 문서를 동기화한다.
소유 파일/hunk만 선별 로컬 커밋하고 해시·포함/제외·잔여 WIP·다음 프롬프트를 남긴 뒤 멈춰라.
기본 다음 ID: T86. 필수 gate 미달이면 먼저 같은 task를 재개하고 다음 task를 자동 실행하지 마라. push·배포·진단·치료·침 시뮬레이션 금지.
```

<a id="t86"></a>
### T86 — 전체 신경 목표·기존 source 전수 대조

```text
HUMAN ATLAS에서 T86만 수행해라. 담당 Sol High.
AGENTS.md, work/EXECUTION.json, work/NEXT.md, 최신 STATUS의 generated execution 블록,
design/2026-09-25-muscle-atlas/25-WHOLE-BODY-BASE-RESET.md와 해당 task 명세, 실제 선행 report/evidence/manifest를 읽어라.
EXECUTION이 현재 범위/순서의 유일한 원본이다. 역사 queue의 nextTask를 실행하지 마라. 24의 엑셀 검증·한글 기능·짧은 신경·표정근 motion 제외는 유지한다.
이번 범위: T61계약과T98의전신신경inventory를재사용하여전체신경목표/분지·지배근·감각관계/복수원문source를대조하고같은T87/T89 내부package를동결한다. 이미확보한같은source를다시취득/색인하지않는다. 엑셀T81의미확인짧은신경record를참고하되근거없이정확한주행/지배로승격하지않는다. prototype감각영역·피부분절·경락을분리한다.
시작 HEAD/status/hash를 기록하고 원본/OpenSim_Models/사용자 WIP/T13 drafts/역사 freeze를 보존한다. source-only/권리/사람검토를 추정 승격하지 않는다.
공통 도구와 단일 scene/renderer/camera를 재사용한다. 자동 전수처리와 내부 의미검증 unit을 구분하며 미완이면 같은 task/nextUnit으로 재개한다. 새 번호를 반복 발급하지 마라.
관련 실제 검증·progress·report/evidence를 남기고 EXECUTION의 해당 task record만 갱신한다. python3 work/tools/sync_execution.py와 --check로 투영 문서를 동기화한다.
소유 파일/hunk만 선별 로컬 커밋하고 해시·포함/제외·잔여 WIP·다음 프롬프트를 남긴 뒤 멈춰라.
기본 다음 ID: T62. 필수 gate 미달이면 먼저 같은 task를 재개하고 다음 task를 자동 실행하지 마라. push·배포·진단·치료·침 시뮬레이션 금지.
```

<a id="t62"></a>
### T62 — 첫 하지 신경 자료 패키지

```text
HUMAN ATLAS에서 T62만 수행해라. 담당 Luna Max.
AGENTS.md, work/EXECUTION.json, work/NEXT.md, 최신 STATUS의 generated execution 블록,
design/2026-09-25-muscle-atlas/25-WHOLE-BODY-BASE-RESET.md와 해당 task 명세, 실제 선행 report/evidence/manifest를 읽어라.
EXECUTION이 현재 범위/순서의 유일한 원본이다. 역사 queue의 nextTask를 실행하지 마라. 24의 엑셀 검증·한글 기능·짧은 신경·표정근 motion 제외는 유지한다.
이번 범위: T86 전신 조사 queue의 첫 하지 신경 trunk1개/branch최대2개 자료를 조사한다. 기존 명세의 상세 근거·검증은 유지하고 이 pilot 하나로 전체 신경 조사 완료를 선언하지 않는다. 다음 T87과 나머지 전체 조사 batch다.
시작 HEAD/status/hash를 기록하고 원본/OpenSim_Models/사용자 WIP/T13 drafts/역사 freeze를 보존한다. source-only/권리/사람검토를 추정 승격하지 않는다.
공통 도구와 단일 scene/renderer/camera를 재사용한다. 자동 전수처리와 내부 의미검증 unit을 구분하며 미완이면 같은 task/nextUnit으로 재개한다. 새 번호를 반복 발급하지 마라.
관련 실제 검증·progress·report/evidence를 남기고 EXECUTION의 해당 task record만 갱신한다. python3 work/tools/sync_execution.py와 --check로 투영 문서를 동기화한다.
소유 파일/hunk만 선별 로컬 커밋하고 해시·포함/제외·잔여 WIP·다음 프롬프트를 남긴 뒤 멈춰라.
기본 다음 ID: T87. 필수 gate 미달이면 먼저 같은 task를 재개하고 다음 task를 자동 실행하지 마라. push·배포·진단·치료·침 시뮬레이션 금지.
```

<a id="t87"></a>
### T87 — 전신 신경 조사 확장 첫 batch

```text
HUMAN ATLAS에서 T87만 수행해라. 담당 Luna Max.
AGENTS.md, work/EXECUTION.json, work/NEXT.md, 최신 STATUS의 generated execution 블록,
design/2026-09-25-muscle-atlas/25-WHOLE-BODY-BASE-RESET.md와 해당 task 명세, 실제 선행 report/evidence/manifest를 읽어라.
EXECUTION이 현재 범위/순서의 유일한 원본이다. 역사 queue의 nextTask를 실행하지 마라. 24의 엑셀 검증·한글 기능·짧은 신경·표정근 motion 제외는 유지한다.
이번 범위: T86이 정한 다음 최대10개 신경 개념의 이름/분지/주행/좌우/지배근/감각/원문 차이를 조사하고 source 모델 간 대조표를 실제 작성한다. 다음 조사 batch들을 순차 진행하며 T88 전에 전체 동결 target을 채운다. geometry 획득과 교육 설명의 출처/허가를 독립 기록하고 아직 learner 3D를 구현하지 않는다.
시작 HEAD/status/hash를 기록하고 원본/OpenSim_Models/사용자 WIP/T13 drafts/역사 freeze를 보존한다. source-only/권리/사람검토를 추정 승격하지 않는다.
공통 도구와 단일 scene/renderer/camera를 재사용한다. 자동 전수처리와 내부 의미검증 unit을 구분하며 미완이면 같은 task/nextUnit으로 재개한다. 새 번호를 반복 발급하지 마라.
관련 실제 검증·progress·report/evidence를 남기고 EXECUTION의 해당 task record만 갱신한다. python3 work/tools/sync_execution.py와 --check로 투영 문서를 동기화한다.
소유 파일/hunk만 선별 로컬 커밋하고 해시·포함/제외·잔여 WIP·다음 프롬프트를 남긴 뒤 멈춰라.
기본 다음 ID: T88. 필수 gate 미달이면 먼저 같은 task를 재개하고 다음 task를 자동 실행하지 마라. push·배포·진단·치료·침 시뮬레이션 금지.
```

<a id="t88"></a>
### T88 — 전신 신경 자료 통합·등록 검증

```text
HUMAN ATLAS에서 T88만 수행해라. 담당 Sol High.
AGENTS.md, work/EXECUTION.json, work/NEXT.md, 최신 STATUS의 generated execution 블록,
design/2026-09-25-muscle-atlas/25-WHOLE-BODY-BASE-RESET.md와 해당 task 명세, 실제 선행 report/evidence/manifest를 읽어라.
EXECUTION이 현재 범위/순서의 유일한 원본이다. 역사 queue의 nextTask를 실행하지 마라. 24의 엑셀 검증·한글 기능·짧은 신경·표정근 motion 제외는 유지한다.
이번 범위: 전체 target의 조사 결과를 공통 graph에 통합하고 중복/동의어/좌우/branch/지배근 mapping/출처 차이를 검증한다. 모델별 registration과 변형/pose 차이에 대한 정량 기준을 명시한다. registration이 필요한 경우 작은 별도 기술 task를 T63 앞에 넣는다. 실제 source surface/path가 없으면 두 endpoint 직선으로 대체하지 않는다. 충분한 조사/통합이 끝난 뒤에만 3D 구현 단계로 이동한다.
시작 HEAD/status/hash를 기록하고 원본/OpenSim_Models/사용자 WIP/T13 drafts/역사 freeze를 보존한다. source-only/권리/사람검토를 추정 승격하지 않는다.
공통 도구와 단일 scene/renderer/camera를 재사용한다. 자동 전수처리와 내부 의미검증 unit을 구분하며 미완이면 같은 task/nextUnit으로 재개한다. 새 번호를 반복 발급하지 마라.
관련 실제 검증·progress·report/evidence를 남기고 EXECUTION의 해당 task record만 갱신한다. python3 work/tools/sync_execution.py와 --check로 투영 문서를 동기화한다.
소유 파일/hunk만 선별 로컬 커밋하고 해시·포함/제외·잔여 WIP·다음 프롬프트를 남긴 뒤 멈춰라.
기본 다음 ID: T63. 필수 gate 미달이면 먼저 같은 task를 재개하고 다음 task를 자동 실행하지 마라. push·배포·진단·치료·침 시뮬레이션 금지.
```

<a id="t63"></a>
### T63 — 첫 신경 3D 주행과 지배근 강조

```text
HUMAN ATLAS에서 T63만 수행해라. 담당 Sol High.
AGENTS.md, work/EXECUTION.json, work/NEXT.md, 최신 STATUS의 generated execution 블록,
design/2026-09-25-muscle-atlas/25-WHOLE-BODY-BASE-RESET.md와 해당 task 명세, 실제 선행 report/evidence/manifest를 읽어라.
EXECUTION이 현재 범위/순서의 유일한 원본이다. 역사 queue의 nextTask를 실행하지 마라. 24의 엑셀 검증·한글 기능·짧은 신경·표정근 motion 제외는 유지한다.
이번 범위: 전체 신경 조사·통합 후 첫 검증된 신경 주행을 같은 scene에 구현한다. 원래 명세의 실제 주행/좌표/pose 검증을 유지한다. 클릭 시 근거 있는 지배근을 강조하고 다른 근육을 흐리며 복원 가능하게 한다. 신경 기본 설명 카드와 세 이름을 연결한다. 다음 나머지 전신 nerve 3D batch이며 포착 설명을 먼저 구현하지 않는다.
시작 HEAD/status/hash를 기록하고 원본/OpenSim_Models/사용자 WIP/T13 drafts/역사 freeze를 보존한다. source-only/권리/사람검토를 추정 승격하지 않는다.
공통 도구와 단일 scene/renderer/camera를 재사용한다. 자동 전수처리와 내부 의미검증 unit을 구분하며 미완이면 같은 task/nextUnit으로 재개한다. 새 번호를 반복 발급하지 마라.
관련 실제 검증·progress·report/evidence를 남기고 EXECUTION의 해당 task record만 갱신한다. python3 work/tools/sync_execution.py와 --check로 투영 문서를 동기화한다.
소유 파일/hunk만 선별 로컬 커밋하고 해시·포함/제외·잔여 WIP·다음 프롬프트를 남긴 뒤 멈춰라.
기본 다음 ID: T89. 필수 gate 미달이면 먼저 같은 task를 재개하고 다음 task를 자동 실행하지 마라. push·배포·진단·치료·침 시뮬레이션 금지.
```

<a id="t89"></a>
### T89 — 전신 신경 3D 확장 첫 batch

```text
HUMAN ATLAS에서 T89만 수행해라. 담당 Luna Max.
AGENTS.md, work/EXECUTION.json, work/NEXT.md, 최신 STATUS의 generated execution 블록,
design/2026-09-25-muscle-atlas/25-WHOLE-BODY-BASE-RESET.md와 해당 task 명세, 실제 선행 report/evidence/manifest를 읽어라.
EXECUTION이 현재 범위/순서의 유일한 원본이다. 역사 queue의 nextTask를 실행하지 마라. 24의 엑셀 검증·한글 기능·짧은 신경·표정근 motion 제외는 유지한다.
이번 범위: T63에서 검증한 adapter로 다음 한 nerve trunk/제한된 branch package를 같은 AnatomySceneRoot에 구현한다. 새로운 복잡한 registration/rig가 필요한 항목은 Sol High의 별도 task로 나눈다. 전체 target의 나머지 3D 작업을 작은 정수 task로 T90 앞에 배정한다. 클릭한 신경과 지배근을 강조하고 나머지 근육은 은은하게 흐리며 복원 토글을 제공한다. 지배근은 실제 relation 근거로 선택하고 단순 근접거리로 추정하지 않는다. 카드에는 해당 신경 설명을 보여주고 아직 포착/기능이상 설명은 후속 단계로 둔다.
시작 HEAD/status/hash를 기록하고 원본/OpenSim_Models/사용자 WIP/T13 drafts/역사 freeze를 보존한다. source-only/권리/사람검토를 추정 승격하지 않는다.
공통 도구와 단일 scene/renderer/camera를 재사용한다. 자동 전수처리와 내부 의미검증 unit을 구분하며 미완이면 같은 task/nextUnit으로 재개한다. 새 번호를 반복 발급하지 마라.
관련 실제 검증·progress·report/evidence를 남기고 EXECUTION의 해당 task record만 갱신한다. python3 work/tools/sync_execution.py와 --check로 투영 문서를 동기화한다.
소유 파일/hunk만 선별 로컬 커밋하고 해시·포함/제외·잔여 WIP·다음 프롬프트를 남긴 뒤 멈춰라.
기본 다음 ID: T90. 필수 gate 미달이면 먼저 같은 task를 재개하고 다음 task를 자동 실행하지 마라. push·배포·진단·치료·침 시뮬레이션 금지.
```

<a id="t90"></a>
### T90 — 전신 신경 주행·지배근 그래픽 합격

```text
HUMAN ATLAS에서 T90만 수행해라. 담당 Astra · 현재 대화 직접 구현.
AGENTS.md, work/EXECUTION.json, work/NEXT.md, 최신 STATUS의 generated execution 블록,
design/2026-09-25-muscle-atlas/25-WHOLE-BODY-BASE-RESET.md와 해당 task 명세, 실제 선행 report/evidence/manifest를 읽어라.
EXECUTION이 현재 범위/순서의 유일한 원본이다. 역사 queue의 nextTask를 실행하지 마라. 24의 엑셀 검증·한글 기능·짧은 신경·표정근 motion 제외는 유지한다.
이번 범위: 동결 신경 target의 실제 주행/선택/지배근 강조/카드/복원/pose를 전수 데이터 감사하고 region별 화면을 검증한다. 모든 muscle motion 중 정적 신경을 잘못 고정해 표시하지 않는다. pose 지원이 없으면 사용자에게 명확히 알리고 rest pose 탐색으로 복원한다. 자료 부족을 전신 완료로 세지 않는다. 신경 기본 설명과 그래픽 통합이 합격한 뒤 T64/T91 포착·기능이상 내용으로 간다.
시작 HEAD/status/hash를 기록하고 원본/OpenSim_Models/사용자 WIP/T13 drafts/역사 freeze를 보존한다. source-only/권리/사람검토를 추정 승격하지 않는다.
공통 도구와 단일 scene/renderer/camera를 재사용한다. 자동 전수처리와 내부 의미검증 unit을 구분하며 미완이면 같은 task/nextUnit으로 재개한다. 새 번호를 반복 발급하지 마라.
관련 실제 검증·progress·report/evidence를 남기고 EXECUTION의 해당 task record만 갱신한다. python3 work/tools/sync_execution.py와 --check로 투영 문서를 동기화한다.
소유 파일/hunk만 선별 로컬 커밋하고 해시·포함/제외·잔여 WIP·다음 프롬프트를 남긴 뒤 멈춰라.
기본 다음 ID: T64. 필수 gate 미달이면 먼저 같은 task를 재개하고 다음 task를 자동 실행하지 마라. push·배포·진단·치료·침 시뮬레이션 금지.
```

<a id="t64"></a>
### T64 — 신경 포착·기능 변화의 접힌 설명 UI

```text
HUMAN ATLAS에서 T64만 수행해라. 담당 Luna Max.
AGENTS.md, work/EXECUTION.json, work/NEXT.md, 최신 STATUS의 generated execution 블록,
design/2026-09-25-muscle-atlas/25-WHOLE-BODY-BASE-RESET.md와 해당 task 명세, 실제 선행 report/evidence/manifest를 읽어라.
EXECUTION이 현재 범위/순서의 유일한 원본이다. 역사 queue의 nextTask를 실행하지 마라. 24의 엑셀 검증·한글 기능·짧은 신경·표정근 motion 제외는 유지한다.
이번 범위: 신경 3D와 지배근 그래픽 완성 후 첫 trunk1/branch≤2의 포착 가능 구간과 병변 수준별 기능 변화 설명을 실제 근거로 작성한다. 처음부터 모든 정보를 펼치지 않는다. T91/후속 batch로 전신 내용 범위를 확장하고 치료/자침 추천은 넣지 않는다.
시작 HEAD/status/hash를 기록하고 원본/OpenSim_Models/사용자 WIP/T13 drafts/역사 freeze를 보존한다. source-only/권리/사람검토를 추정 승격하지 않는다.
공통 도구와 단일 scene/renderer/camera를 재사용한다. 자동 전수처리와 내부 의미검증 unit을 구분하며 미완이면 같은 task/nextUnit으로 재개한다. 새 번호를 반복 발급하지 마라.
관련 실제 검증·progress·report/evidence를 남기고 EXECUTION의 해당 task record만 갱신한다. python3 work/tools/sync_execution.py와 --check로 투영 문서를 동기화한다.
소유 파일/hunk만 선별 로컬 커밋하고 해시·포함/제외·잔여 WIP·다음 프롬프트를 남긴 뒤 멈춰라.
기본 다음 ID: T91. 필수 gate 미달이면 먼저 같은 task를 재개하고 다음 task를 자동 실행하지 마라. push·배포·진단·치료·침 시뮬레이션 금지.
```

<a id="t91"></a>
### T91 — 신경 포착·기능이상 설명 확장 첫 batch

```text
HUMAN ATLAS에서 T91만 수행해라. 담당 Luna Max.
AGENTS.md, work/EXECUTION.json, work/NEXT.md, 최신 STATUS의 generated execution 블록,
design/2026-09-25-muscle-atlas/25-WHOLE-BODY-BASE-RESET.md와 해당 task 명세, 실제 선행 report/evidence/manifest를 읽어라.
EXECUTION이 현재 범위/순서의 유일한 원본이다. 역사 queue의 nextTask를 실행하지 마라. 24의 엑셀 검증·한글 기능·짧은 신경·표정근 motion 제외는 유지한다.
이번 범위: 전체 신경 target 중 근거가 있는 포착/병변 수준별 내용에 대해 다음 최대10개 개념 batch를 조사·검증·연결한다. 가능한 구간/주변 구조·운동/감각 변화·분지/병변 수준·조건·변이/감별 한계를 분리한다. 모든 신경에 알려진 포착점이 반드시 있다고 가정하지 않고 근거 미확인은 명시적인 내용 상태로 둔다. 남은 batch를 정수 ID로 T65 앞에 배정한다. 신경 클릭 때 기본 주행/지배 설명만 보이고 포착과 기능 변화는 접힌 항목으로 표시한다. 환자 자동진단/자침점·깊이·치료 추천은 만들지 않는다.
시작 HEAD/status/hash를 기록하고 원본/OpenSim_Models/사용자 WIP/T13 drafts/역사 freeze를 보존한다. source-only/권리/사람검토를 추정 승격하지 않는다.
공통 도구와 단일 scene/renderer/camera를 재사용한다. 자동 전수처리와 내부 의미검증 unit을 구분하며 미완이면 같은 task/nextUnit으로 재개한다. 새 번호를 반복 발급하지 마라.
관련 실제 검증·progress·report/evidence를 남기고 EXECUTION의 해당 task record만 갱신한다. python3 work/tools/sync_execution.py와 --check로 투영 문서를 동기화한다.
소유 파일/hunk만 선별 로컬 커밋하고 해시·포함/제외·잔여 WIP·다음 프롬프트를 남긴 뒤 멈춰라.
기본 다음 ID: T65. 필수 gate 미달이면 먼저 같은 task를 재개하고 다음 task를 자동 실행하지 마라. push·배포·진단·치료·침 시뮬레이션 금지.
```

<a id="t65"></a>
### T65 — 전체 신경·지배·기능이상 교육 통합 합격

```text
HUMAN ATLAS에서 T65만 수행해라. 담당 Luna Max.
AGENTS.md, work/EXECUTION.json, work/NEXT.md, 최신 STATUS의 generated execution 블록,
design/2026-09-25-muscle-atlas/25-WHOLE-BODY-BASE-RESET.md와 해당 task 명세, 실제 선행 report/evidence/manifest를 읽어라.
EXECUTION이 현재 범위/순서의 유일한 원본이다. 역사 queue의 nextTask를 실행하지 마라. 24의 엑셀 검증·한글 기능·짧은 신경·표정근 motion 제외는 유지한다.
이번 범위: 전신신경자료/3D주행/검증된지배근강조/부위별기능이상설명을기존gate와25의같은scene계약으로전수검증한다. 구조·설명·신경의분모를별도로보고하고임상진단/치료·자침추천은만들지않는다. 전근육motion을이번신경gate의선행조건으로두지않는다. 합격후별도요청으로T35의근육motion계획에진입한다.
시작 HEAD/status/hash를 기록하고 원본/OpenSim_Models/사용자 WIP/T13 drafts/역사 freeze를 보존한다. source-only/권리/사람검토를 추정 승격하지 않는다.
공통 도구와 단일 scene/renderer/camera를 재사용한다. 자동 전수처리와 내부 의미검증 unit을 구분하며 미완이면 같은 task/nextUnit으로 재개한다. 새 번호를 반복 발급하지 마라.
관련 실제 검증·progress·report/evidence를 남기고 EXECUTION의 해당 task record만 갱신한다. python3 work/tools/sync_execution.py와 --check로 투영 문서를 동기화한다.
소유 파일/hunk만 선별 로컬 커밋하고 해시·포함/제외·잔여 WIP·다음 프롬프트를 남긴 뒤 멈춰라.
기본 다음 ID: T35. 필수 gate 미달이면 먼저 같은 task를 재개하고 다음 task를 자동 실행하지 마라. push·배포·진단·치료·침 시뮬레이션 금지.
```

<a id="t35"></a>
### T35 — 근육 움직임 제작 범위와 재사용 family 동결

```text
HUMAN ATLAS에서 T35만 수행해라. 담당 Sol High.
AGENTS.md, work/EXECUTION.json, work/NEXT.md, 최신 STATUS의 generated execution 블록,
design/2026-09-25-muscle-atlas/25-WHOLE-BODY-BASE-RESET.md와 해당 task 명세, 실제 선행 report/evidence/manifest를 읽어라.
EXECUTION이 현재 범위/순서의 유일한 원본이다. 역사 queue의 nextTask를 실행하지 마라. 24의 엑셀 검증·한글 기능·짧은 신경·표정근 motion 제외는 유지한다.
이번 범위: G1/G2/G3의실제구조·설명·신경이완료된뒤 기존앞정강근/소흉근시범과T66공통family확장순서를동결한다.24설계의exact 표정근deferred_by_user를motion분모에서만제외하고구조/설명은유지한다. 전체머리/외안/씹기/혀를자동제외하지않는다. 지금선택한전신base의source/frame/pose와OpenSim지원관계를검증하고과거BP3D에기존clip이맞는다고가정하지않는다. 새같은모형변형family만bounded범위로설계하며10개마다새task를발급하지않는다. 이번task는계획이며clip제작은하지않는다.
시작 HEAD/status/hash를 기록하고 원본/OpenSim_Models/사용자 WIP/T13 drafts/역사 freeze를 보존한다. source-only/권리/사람검토를 추정 승격하지 않는다.
공통 도구와 단일 scene/renderer/camera를 재사용한다. 자동 전수처리와 내부 의미검증 unit을 구분하며 미완이면 같은 task/nextUnit으로 재개한다. 새 번호를 반복 발급하지 마라.
관련 실제 검증·progress·report/evidence를 남기고 EXECUTION의 해당 task record만 갱신한다. python3 work/tools/sync_execution.py와 --check로 투영 문서를 동기화한다.
소유 파일/hunk만 선별 로컬 커밋하고 해시·포함/제외·잔여 WIP·다음 프롬프트를 남긴 뒤 멈춰라.
기본 다음 ID: T59. 필수 gate 미달이면 먼저 같은 task를 재개하고 다음 task를 자동 실행하지 마라. push·배포·진단·치료·침 시뮬레이션 금지.
```

<a id="t59"></a>
### T59 — 같은 앞정강근 표면의 교육용 수축 변형

```text
HUMAN ATLAS에서 T59만 수행해라. 담당 Sol High.
AGENTS.md, work/EXECUTION.json, work/NEXT.md, 최신 STATUS의 generated execution 블록,
design/2026-09-25-muscle-atlas/25-WHOLE-BODY-BASE-RESET.md와 해당 task 명세, 실제 선행 report/evidence/manifest를 읽어라.
EXECUTION이 현재 범위/순서의 유일한 원본이다. 역사 queue의 nextTask를 실행하지 마라. 24의 엑셀 검증·한글 기능·짧은 신경·표정근 motion 제외는 유지한다.
이번 범위: T55 전신 모델의 실제 앞정강근과 부착·발목 bone에 대해 model-local 좌표/endpoint·rest pose를 검증하고 skinning 또는 morph/shape-key 기반 변형을 제작한다. 목표 근육의 형태 변화와 발 움직임을 같은 모델에서 결속한다. 주변 근육은 사용자가 숨기지 않았다면 유지하고 관절을 지나는 주변 구조의 수동 변형/관통도 처리한다. 근육 전체 scale이나 선 길이 감소만으로 대체하지 않는다.

시작 HEAD/status/hash를 기록하고 원본/OpenSim_Models/사용자 WIP/T13 drafts/역사 freeze를 보존한다. source-only/권리/사람검토를 추정 승격하지 않는다.
공통 도구와 단일 scene/renderer/camera를 재사용한다. 자동 전수처리와 내부 의미검증 unit을 구분하며 미완이면 같은 task/nextUnit으로 재개한다. 새 번호를 반복 발급하지 마라.
관련 실제 검증·progress·report/evidence를 남기고 EXECUTION의 해당 task record만 갱신한다. python3 work/tools/sync_execution.py와 --check로 투영 문서를 동기화한다.
소유 파일/hunk만 선별 로컬 커밋하고 해시·포함/제외·잔여 WIP·다음 프롬프트를 남긴 뒤 멈춰라.
기본 다음 ID: T60. 필수 gate 미달이면 먼저 같은 task를 재개하고 다음 task를 자동 실행하지 마라. push·배포·진단·치료·침 시뮬레이션 금지.
```

<a id="t60"></a>
### T60 — 동일 viewport에서 운동 재생 연결

```text
HUMAN ATLAS에서 T60만 수행해라. 담당 Sol High.
AGENTS.md, work/EXECUTION.json, work/NEXT.md, 최신 STATUS의 generated execution 블록,
design/2026-09-25-muscle-atlas/25-WHOLE-BODY-BASE-RESET.md와 해당 task 명세, 실제 선행 report/evidence/manifest를 읽어라.
EXECUTION이 현재 범위/순서의 유일한 원본이다. 역사 queue의 nextTask를 실행하지 마라. 24의 엑셀 검증·한글 기능·짧은 신경·표정근 motion 제외는 유지한다.
이번 범위: MotionLearningPanel의 독립 asset/mixer 소유를 AnatomySceneController 명령으로 연결한다. 실제 main renderer가 가진 T59 target node를 애니메이션하고 UI는 play/pause/seek/reset 명령과 상태만 가진다. 사용자 CTA 클릭 전에는 움직이지 않는다. 기존 camera/background/layers/selection을 snapshot해 보존하고 종료 시 pose/가시성만 정확히 복원한다.

시작 HEAD/status/hash를 기록하고 원본/OpenSim_Models/사용자 WIP/T13 drafts/역사 freeze를 보존한다. source-only/권리/사람검토를 추정 승격하지 않는다.
공통 도구와 단일 scene/renderer/camera를 재사용한다. 자동 전수처리와 내부 의미검증 unit을 구분하며 미완이면 같은 task/nextUnit으로 재개한다. 새 번호를 반복 발급하지 마라.
관련 실제 검증·progress·report/evidence를 남기고 EXECUTION의 해당 task record만 갱신한다. python3 work/tools/sync_execution.py와 --check로 투영 문서를 동기화한다.
소유 파일/hunk만 선별 로컬 커밋하고 해시·포함/제외·잔여 WIP·다음 프롬프트를 남긴 뒤 멈춰라.
기본 다음 ID: T25. 필수 gate 미달이면 먼저 같은 task를 재개하고 다음 task를 자동 실행하지 마라. push·배포·진단·치료·침 시뮬레이션 금지.
```

<a id="t25"></a>
### T25 — 같은 전신 모형의 앞정강근 제품 합격

```text
HUMAN ATLAS에서 T25만 수행해라. 담당 Luna Max.
AGENTS.md, work/EXECUTION.json, work/NEXT.md, 최신 STATUS의 generated execution 블록,
design/2026-09-25-muscle-atlas/25-WHOLE-BODY-BASE-RESET.md와 해당 task 명세, 실제 선행 report/evidence/manifest를 읽어라.
EXECUTION이 현재 범위/순서의 유일한 원본이다. 역사 queue의 nextTask를 실행하지 마라. 24의 엑셀 검증·한글 기능·짧은 신경·표정근 motion 제외는 유지한다.
이번 범위: T42 공통 카드와 T24 실제 clip을 연결한다. 근육 선택→세 이름/기시·정지→눈에 보이는 '움직임으로 이해하기'→실제 몸 움직임→작용 설명을 연결한다. 클릭은 명시적 재생 요청으로 취급하되 reduced-motion은 정지 자세/수동 단계 선택을 기본으로 한다.

기능 탭 전환과 작용 선택을 동기화하고 pause/resume/처음 자세/느리게/진행 막대를 제공한다. camera reset과 pose reset을 분리한다. 모형 전환이 있으면 학습용 시범 모형임을 짧게 알린다.

선택/부위/탭 전환·로드 실패·unmount 시 loop·mixer·강조를 정리한다. CTA 클릭 전에는 자동 재생하지 않는다.
 T59/T60의 실제 같은 모형 mesh 변형을 main learner에서 검증한다. 별도 T24 bone/path 기술 후보는 pass 근거가 아니다. 전신 탐색→앞정강근→기시정지/기능→CTA→표면 수축과 발 움직임→복원을 시험한다. T24 역사 보고서는 blocked 그대로 보존하고 해결 증거를 새 보고서에 연결한다. 다음은 같은 전신 모형의 소흉근 사례 T27이며, 신경은 전신 근육 시범 gate T85 이후다.
시작 HEAD/status/hash를 기록하고 원본/OpenSim_Models/사용자 WIP/T13 drafts/역사 freeze를 보존한다. source-only/권리/사람검토를 추정 승격하지 않는다.
공통 도구와 단일 scene/renderer/camera를 재사용한다. 자동 전수처리와 내부 의미검증 unit을 구분하며 미완이면 같은 task/nextUnit으로 재개한다. 새 번호를 반복 발급하지 마라.
관련 실제 검증·progress·report/evidence를 남기고 EXECUTION의 해당 task record만 갱신한다. python3 work/tools/sync_execution.py와 --check로 투영 문서를 동기화한다.
소유 파일/hunk만 선별 로컬 커밋하고 해시·포함/제외·잔여 WIP·다음 프롬프트를 남긴 뒤 멈춰라.
기본 다음 ID: T27. 필수 gate 미달이면 먼저 같은 task를 재개하고 다음 task를 자동 실행하지 마라. push·배포·진단·치료·침 시뮬레이션 금지.
```

<a id="t27"></a>
### T27 — 소흉근 동일 모형 변형 준비

```text
HUMAN ATLAS에서 T27만 수행해라. 담당 Sol High.
AGENTS.md, work/EXECUTION.json, work/NEXT.md, 최신 STATUS의 generated execution 블록,
design/2026-09-25-muscle-atlas/25-WHOLE-BODY-BASE-RESET.md와 해당 task 명세, 실제 선행 report/evidence/manifest를 읽어라.
EXECUTION이 현재 범위/순서의 유일한 원본이다. 역사 queue의 nextTask를 실행하지 마라. 24의 엑셀 검증·한글 기능·짧은 신경·표정근 motion 제외는 유지한다.
이번 범위: 전신 구조 단계에서 준비된 소흉근/흉곽/견갑대와 완료된 기능 설명을 재사용한다. rig/부착/주변 구조 변형 준비만 검증하고 필요할 때만 근거 있는 상세 자산을 보완한다. 다른 모델/고해상도 LOD가 있다고 가정하지 않는다. T28의 동일 모델 운동을 준비한다.
시작 HEAD/status/hash를 기록하고 원본/OpenSim_Models/사용자 WIP/T13 drafts/역사 freeze를 보존한다. source-only/권리/사람검토를 추정 승격하지 않는다.
공통 도구와 단일 scene/renderer/camera를 재사용한다. 자동 전수처리와 내부 의미검증 unit을 구분하며 미완이면 같은 task/nextUnit으로 재개한다. 새 번호를 반복 발급하지 마라.
관련 실제 검증·progress·report/evidence를 남기고 EXECUTION의 해당 task record만 갱신한다. python3 work/tools/sync_execution.py와 --check로 투영 문서를 동기화한다.
소유 파일/hunk만 선별 로컬 커밋하고 해시·포함/제외·잔여 WIP·다음 프롬프트를 남긴 뒤 멈춰라.
기본 다음 ID: T28. 필수 gate 미달이면 먼저 같은 task를 재개하고 다음 task를 자동 실행하지 마라. push·배포·진단·치료·침 시뮬레이션 금지.
```

<a id="t28"></a>
### T28 — 견갑대 운동 기반과 전인 시범 하나

```text
HUMAN ATLAS에서 T28만 수행해라. 담당 Sol High.
AGENTS.md, work/EXECUTION.json, work/NEXT.md, 최신 STATUS의 generated execution 블록,
design/2026-09-25-muscle-atlas/25-WHOLE-BODY-BASE-RESET.md와 해당 task 명세, 실제 선행 report/evidence/manifest를 읽어라.
EXECUTION이 현재 범위/순서의 유일한 원본이다. 역사 queue의 nextTask를 실행하지 마라. 24의 엑셀 검증·한글 기능·짧은 신경·표정근 motion 제외는 유지한다.
이번 범위: T81–84의 전신 내용 batch에서 확정한 조건의 소흉근 관련 견갑골 전인 시범 1개를 제작한다. 흉곽에 대한 견갑대의 이동/회전과 고정 조건을 모델링하고 T45/T46에서 재사용할 골격·경로 제작 도구를 만든다.

단일 임의 hinge 또는 상완골만 움직이는 것으로 견갑골 작용을 대신하지 않는다. 근육 endpoint/변형 또는 표시된 설명 경로를 함께 제공한다. T44의 좌표 정합 원칙을 재사용하되 발목 좌표를 복제하지 않는다.
 기존 세부 수행 범위는 유지하되 R15 동일 전신 scene/근육 표면 변형/명확한 CTA/신경 우선 순서를 적용한다. 이전 별도 시범 모델 허용은 폐기하며 아래 이전 next/prerequisite 문구는 R15 queue로 대체한다.
시작 HEAD/status/hash를 기록하고 원본/OpenSim_Models/사용자 WIP/T13 drafts/역사 freeze를 보존한다. source-only/권리/사람검토를 추정 승격하지 않는다.
공통 도구와 단일 scene/renderer/camera를 재사용한다. 자동 전수처리와 내부 의미검증 unit을 구분하며 미완이면 같은 task/nextUnit으로 재개한다. 새 번호를 반복 발급하지 마라.
관련 실제 검증·progress·report/evidence를 남기고 EXECUTION의 해당 task record만 갱신한다. python3 work/tools/sync_execution.py와 --check로 투영 문서를 동기화한다.
소유 파일/hunk만 선별 로컬 커밋하고 해시·포함/제외·잔여 WIP·다음 프롬프트를 남긴 뒤 멈춰라.
기본 다음 ID: T45. 필수 gate 미달이면 먼저 같은 task를 재개하고 다음 task를 자동 실행하지 마라. push·배포·진단·치료·침 시뮬레이션 금지.
```

<a id="t45"></a>
### T45 — 소흉근 관련 견갑골 하강 시범

```text
HUMAN ATLAS에서 T45만 수행해라. 담당 Sol High.
AGENTS.md, work/EXECUTION.json, work/NEXT.md, 최신 STATUS의 generated execution 블록,
design/2026-09-25-muscle-atlas/25-WHOLE-BODY-BASE-RESET.md와 해당 task 명세, 실제 선행 report/evidence/manifest를 읽어라.
EXECUTION이 현재 범위/순서의 유일한 원본이다. 역사 queue의 nextTask를 실행하지 마라. 24의 엑셀 검증·한글 기능·짧은 신경·표정근 motion 제외는 유지한다.
이번 범위: T28 기반을 재사용해 T81–84의 전신 내용 batch에서 근거/조건이 확인된 하강 시범 clip1개를 만든다. 단순 전인 clip의 축값을 바꿔 해부학 근거 대신 쓰지 않는다. moving/fixed structures·근육 경로와 설명을 연결한다.
 기존 세부 수행 범위는 유지하되 R15 동일 전신 scene/근육 표면 변형/명확한 CTA/신경 우선 순서를 적용한다. 이전 별도 시범 모델 허용은 폐기하며 아래 이전 next/prerequisite 문구는 R15 queue로 대체한다.
시작 HEAD/status/hash를 기록하고 원본/OpenSim_Models/사용자 WIP/T13 drafts/역사 freeze를 보존한다. source-only/권리/사람검토를 추정 승격하지 않는다.
공통 도구와 단일 scene/renderer/camera를 재사용한다. 자동 전수처리와 내부 의미검증 unit을 구분하며 미완이면 같은 task/nextUnit으로 재개한다. 새 번호를 반복 발급하지 마라.
관련 실제 검증·progress·report/evidence를 남기고 EXECUTION의 해당 task record만 갱신한다. python3 work/tools/sync_execution.py와 --check로 투영 문서를 동기화한다.
소유 파일/hunk만 선별 로컬 커밋하고 해시·포함/제외·잔여 WIP·다음 프롬프트를 남긴 뒤 멈춰라.
기본 다음 ID: T46. 필수 gate 미달이면 먼저 같은 task를 재개하고 다음 task를 자동 실행하지 마라. push·배포·진단·치료·침 시뮬레이션 금지.
```

<a id="t46"></a>
### T46 — 소흉근 관련 견갑골 하방회전 시범

```text
HUMAN ATLAS에서 T46만 수행해라. 담당 Sol High.
AGENTS.md, work/EXECUTION.json, work/NEXT.md, 최신 STATUS의 generated execution 블록,
design/2026-09-25-muscle-atlas/25-WHOLE-BODY-BASE-RESET.md와 해당 task 명세, 실제 선행 report/evidence/manifest를 읽어라.
EXECUTION이 현재 범위/순서의 유일한 원본이다. 역사 queue의 nextTask를 실행하지 마라. 24의 엑셀 검증·한글 기능·짧은 신경·표정근 motion 제외는 유지한다.
이번 범위: T28 기반으로 T81–84의 전신 내용 batch에서 근거/조건이 확인된 하방회전 시범 clip1개를 만든다. 회전 방향과 흉곽 정합을 검증하며 전인/하강과 작용 ID를 구분한다. 대표 시범을 생체 운동의 정량 재현으로 주장하지 않는다.
 기존 세부 수행 범위는 유지하되 R15 동일 전신 scene/근육 표면 변형/명확한 CTA/신경 우선 순서를 적용한다. 이전 별도 시범 모델 허용은 폐기하며 아래 이전 next/prerequisite 문구는 R15 queue로 대체한다.
시작 HEAD/status/hash를 기록하고 원본/OpenSim_Models/사용자 WIP/T13 drafts/역사 freeze를 보존한다. source-only/권리/사람검토를 추정 승격하지 않는다.
공통 도구와 단일 scene/renderer/camera를 재사용한다. 자동 전수처리와 내부 의미검증 unit을 구분하며 미완이면 같은 task/nextUnit으로 재개한다. 새 번호를 반복 발급하지 마라.
관련 실제 검증·progress·report/evidence를 남기고 EXECUTION의 해당 task record만 갱신한다. python3 work/tools/sync_execution.py와 --check로 투영 문서를 동기화한다.
소유 파일/hunk만 선별 로컬 커밋하고 해시·포함/제외·잔여 WIP·다음 프롬프트를 남긴 뒤 멈춰라.
기본 다음 ID: T29. 필수 gate 미달이면 먼저 같은 task를 재개하고 다음 task를 자동 실행하지 마라. push·배포·진단·치료·침 시뮬레이션 금지.
```

<a id="t29"></a>
### T29 — 소흉근 구조·기능 사용자 흐름 통합

```text
HUMAN ATLAS에서 T29만 수행해라. 담당 Luna Max.
AGENTS.md, work/EXECUTION.json, work/NEXT.md, 최신 STATUS의 generated execution 블록,
design/2026-09-25-muscle-atlas/25-WHOLE-BODY-BASE-RESET.md와 해당 task 명세, 실제 선행 report/evidence/manifest를 읽어라.
EXECUTION이 현재 범위/순서의 유일한 원본이다. 역사 queue의 nextTask를 실행하지 마라. 24의 엑셀 검증·한글 기능·짧은 신경·표정근 motion 제외는 유지한다.
이번 범위: 소흉근 선택→주변 흐림→구조 설명→CTA→전인/하강/하방회전 작용 선택→해당 실제 clip과 설명으로 연결한다. 지원하지 않는 작용은 다른 clip으로 대체하지 않는다. 뼈 카드의 세 이름과 근육으로 돌아오는 흐름을 검증한다.
 기존 세부 수행 범위는 유지하되 R15 동일 전신 scene/근육 표면 변형/명확한 CTA/신경 우선 순서를 적용한다. 이전 별도 시범 모델 허용은 폐기하며 아래 이전 next/prerequisite 문구는 R15 queue로 대체한다.
시작 HEAD/status/hash를 기록하고 원본/OpenSim_Models/사용자 WIP/T13 drafts/역사 freeze를 보존한다. source-only/권리/사람검토를 추정 승격하지 않는다.
공통 도구와 단일 scene/renderer/camera를 재사용한다. 자동 전수처리와 내부 의미검증 unit을 구분하며 미완이면 같은 task/nextUnit으로 재개한다. 새 번호를 반복 발급하지 마라.
관련 실제 검증·progress·report/evidence를 남기고 EXECUTION의 해당 task record만 갱신한다. python3 work/tools/sync_execution.py와 --check로 투영 문서를 동기화한다.
소유 파일/hunk만 선별 로컬 커밋하고 해시·포함/제외·잔여 WIP·다음 프롬프트를 남긴 뒤 멈춰라.
기본 다음 ID: T31. 필수 gate 미달이면 먼저 같은 task를 재개하고 다음 task를 자동 실행하지 마라. push·배포·진단·치료·침 시뮬레이션 금지.
```

<a id="t31"></a>
### T31 — 두 부위 구조·기능 파일럿 합격 검증

```text
HUMAN ATLAS에서 T31만 수행해라. 담당 Luna Max.
AGENTS.md, work/EXECUTION.json, work/NEXT.md, 최신 STATUS의 generated execution 블록,
design/2026-09-25-muscle-atlas/25-WHOLE-BODY-BASE-RESET.md와 해당 task 명세, 실제 선행 report/evidence/manifest를 읽어라.
EXECUTION이 현재 범위/순서의 유일한 원본이다. 역사 queue의 nextTask를 실행하지 마라. 24의 엑셀 검증·한글 기능·짧은 신경·표정근 motion 제외는 유지한다.
이번 범위: 종아리와 소흉근의 실제 data/scene/clip을 전체 사용자 흐름으로 검사한다. 세 이름·기시정지·뼈 카드·클릭·흐림·움직임·설명·복원을 함께 확인한다. 데이터 검증과 실제 화면 검증을 분리 기록한다.
 기존 세부 수행 범위는 유지하되 R15 동일 전신 scene/근육 표면 변형/명확한 CTA/신경 우선 순서를 적용한다. 이전 별도 시범 모델 허용은 폐기하며 아래 이전 next/prerequisite 문구는 R15 queue로 대체한다.
시작 HEAD/status/hash를 기록하고 원본/OpenSim_Models/사용자 WIP/T13 drafts/역사 freeze를 보존한다. source-only/권리/사람검토를 추정 승격하지 않는다.
공통 도구와 단일 scene/renderer/camera를 재사용한다. 자동 전수처리와 내부 의미검증 unit을 구분하며 미완이면 같은 task/nextUnit으로 재개한다. 새 번호를 반복 발급하지 마라.
관련 실제 검증·progress·report/evidence를 남기고 EXECUTION의 해당 task record만 갱신한다. python3 work/tools/sync_execution.py와 --check로 투영 문서를 동기화한다.
소유 파일/hunk만 선별 로컬 커밋하고 해시·포함/제외·잔여 WIP·다음 프롬프트를 남긴 뒤 멈춰라.
기본 다음 ID: T66. 필수 gate 미달이면 먼저 같은 task를 재개하고 다음 task를 자동 실행하지 마라. push·배포·진단·치료·침 시뮬레이션 금지.
```

<a id="t66"></a>
### T66 — 첫 기능 확장 batch 하나

```text
HUMAN ATLAS에서 T66만 수행해라. 담당 Luna Max.
AGENTS.md, work/EXECUTION.json, work/NEXT.md, 최신 STATUS의 generated execution 블록,
design/2026-09-25-muscle-atlas/25-WHOLE-BODY-BASE-RESET.md와 해당 task 명세, 실제 선행 report/evidence/manifest를 읽어라.
EXECUTION이 현재 범위/순서의 유일한 원본이다. 역사 queue의 nextTask를 실행하지 마라. 24의 엑셀 검증·한글 기능·짧은 신경·표정근 motion 제외는 유지한다.
이번 범위: T35의 required motion family와 exact 대상만 기존 rig/공통 재생 경로로 확장한다. clip1개 또는 검증된 family의 최대10관계 검증 상한과 같은 T66 progress 재개를 유지한다. 24에서 exact ID로 deferred_by_user인 표정근의 clip은 만들지 않는다. 그 근육의 구조/기능 데이터는 유지한다. 나머지 필수 운동 누락을 제외 목록에 추가하지 않는다. scale-only/다른 viewer 대체 금지.
시작 HEAD/status/hash를 기록하고 원본/OpenSim_Models/사용자 WIP/T13 drafts/역사 freeze를 보존한다. source-only/권리/사람검토를 추정 승격하지 않는다.
공통 도구와 단일 scene/renderer/camera를 재사용한다. 자동 전수처리와 내부 의미검증 unit을 구분하며 미완이면 같은 task/nextUnit으로 재개한다. 새 번호를 반복 발급하지 마라.
관련 실제 검증·progress·report/evidence를 남기고 EXECUTION의 해당 task record만 갱신한다. python3 work/tools/sync_execution.py와 --check로 투영 문서를 동기화한다.
소유 파일/hunk만 선별 로컬 커밋하고 해시·포함/제외·잔여 WIP·다음 프롬프트를 남긴 뒤 멈춰라.
기본 다음 ID: T47. 필수 gate 미달이면 먼저 같은 task를 재개하고 다음 task를 자동 실행하지 마라. push·배포·진단·치료·침 시뮬레이션 금지.
```

<a id="t47"></a>
### T47 — 전신 구조·기능·운동 자료 감사

```text
HUMAN ATLAS에서 T47만 수행해라. 담당 Luna Max.
AGENTS.md, work/EXECUTION.json, work/NEXT.md, 최신 STATUS의 generated execution 블록,
design/2026-09-25-muscle-atlas/25-WHOLE-BODY-BASE-RESET.md와 해당 task 명세, 실제 선행 report/evidence/manifest를 읽어라.
EXECUTION이 현재 범위/순서의 유일한 원본이다. 역사 queue의 nextTask를 실행하지 마라. 24의 엑셀 검증·한글 기능·짧은 신경·표정근 motion 제외는 유지한다.
이번 범위: T96/T35의 전체 구조/기시정지/기능/운동 mapping을 감사한다. 24의 exact 표정근 deferred_by_user와 필수 운동을 분리하고 지원+명시 제외+미지원=전체 동결 대상을 대조한다. 제외는 완료 수가 아니다. 비제외 필수 근육의 실제 같은 surface/rig/clip 및 설명을 전수 확인한다. T66 첫 unit/상태 문자열만으로 T85 gate 합격을 예고하지 않는다.
시작 HEAD/status/hash를 기록하고 원본/OpenSim_Models/사용자 WIP/T13 drafts/역사 freeze를 보존한다. source-only/권리/사람검토를 추정 승격하지 않는다.
공통 도구와 단일 scene/renderer/camera를 재사용한다. 자동 전수처리와 내부 의미검증 unit을 구분하며 미완이면 같은 task/nextUnit으로 재개한다. 새 번호를 반복 발급하지 마라.
관련 실제 검증·progress·report/evidence를 남기고 EXECUTION의 해당 task record만 갱신한다. python3 work/tools/sync_execution.py와 --check로 투영 문서를 동기화한다.
소유 파일/hunk만 선별 로컬 커밋하고 해시·포함/제외·잔여 WIP·다음 프롬프트를 남긴 뒤 멈춰라.
기본 다음 ID: T85. 필수 gate 미달이면 먼저 같은 task를 재개하고 다음 task를 자동 실행하지 마라. push·배포·진단·치료·침 시뮬레이션 금지.
```

<a id="t85"></a>
### T85 — 필수 근육 움직임 합격·표정근 제외 별도

```text
HUMAN ATLAS에서 T85만 수행해라. 담당 Astra · 현재 대화 직접 구현.
AGENTS.md, work/EXECUTION.json, work/NEXT.md, 최신 STATUS의 generated execution 블록,
design/2026-09-25-muscle-atlas/25-WHOLE-BODY-BASE-RESET.md와 해당 task 명세, 실제 선행 report/evidence/manifest를 읽어라.
EXECUTION이 현재 범위/순서의 유일한 원본이다. 역사 queue의 nextTask를 실행하지 마라. 24의 엑셀 검증·한글 기능·짧은 신경·표정근 motion 제외는 유지한다.
이번 범위: 24/T35의동결필수motion을현재전신base의같은surface/scene에서전수검증한다. 표정근exact제외와그밖의미지원은구분하며얼굴구조/설명/세이름은필수다. 별도viewer/검정화면/뼈만/scale-only대체금지. 사용자선택·카메라·레이어·관찰override와움직임/설명동기를확인한다. 신경은이미G3에서검증된것으로회귀확인하되다시처음부터실행하지않는다. 다음은T40로컬전달이다.
시작 HEAD/status/hash를 기록하고 원본/OpenSim_Models/사용자 WIP/T13 drafts/역사 freeze를 보존한다. source-only/권리/사람검토를 추정 승격하지 않는다.
공통 도구와 단일 scene/renderer/camera를 재사용한다. 자동 전수처리와 내부 의미검증 unit을 구분하며 미완이면 같은 task/nextUnit으로 재개한다. 새 번호를 반복 발급하지 마라.
관련 실제 검증·progress·report/evidence를 남기고 EXECUTION의 해당 task record만 갱신한다. python3 work/tools/sync_execution.py와 --check로 투영 문서를 동기화한다.
소유 파일/hunk만 선별 로컬 커밋하고 해시·포함/제외·잔여 WIP·다음 프롬프트를 남긴 뒤 멈춰라.
기본 다음 ID: T40. 필수 gate 미달이면 먼저 같은 task를 재개하고 다음 task를 자동 실행하지 마라. push·배포·진단·치료·침 시뮬레이션 금지.
```

<a id="t40"></a>
### T40 — 구조·기능 로컬 전달과 Git 체크포인트

```text
HUMAN ATLAS에서 T40만 수행해라. 담당 Luna Max.
AGENTS.md, work/EXECUTION.json, work/NEXT.md, 최신 STATUS의 generated execution 블록,
design/2026-09-25-muscle-atlas/25-WHOLE-BODY-BASE-RESET.md와 해당 task 명세, 실제 선행 report/evidence/manifest를 읽어라.
EXECUTION이 현재 범위/순서의 유일한 원본이다. 역사 queue의 nextTask를 실행하지 마라. 24의 엑셀 검증·한글 기능·짧은 신경·표정근 motion 제외는 유지한다.
이번 범위: T47 실제 결과 기준으로 실행/설치/자료 추가/검증/복구 안내와 로컬 전달 빌드를 만든다. 평가·퀴즈 구현을 이번 전달의 필수 선행으로 두지 않는다. 재현 가능한 checkout과 asset 확보 방법을 검증한다.
 기존 세부 수행 범위는 유지하되 R15 동일 전신 scene/근육 표면 변형/명확한 CTA/신경 우선 순서를 적용한다. 이전 별도 시범 모델 허용은 폐기하며 아래 이전 next/prerequisite 문구는 R15 queue로 대체한다.
시작 HEAD/status/hash를 기록하고 원본/OpenSim_Models/사용자 WIP/T13 drafts/역사 freeze를 보존한다. source-only/권리/사람검토를 추정 승격하지 않는다.
공통 도구와 단일 scene/renderer/camera를 재사용한다. 자동 전수처리와 내부 의미검증 unit을 구분하며 미완이면 같은 task/nextUnit으로 재개한다. 새 번호를 반복 발급하지 마라.
관련 실제 검증·progress·report/evidence를 남기고 EXECUTION의 해당 task record만 갱신한다. python3 work/tools/sync_execution.py와 --check로 투영 문서를 동기화한다.
소유 파일/hunk만 선별 로컬 커밋하고 해시·포함/제외·잔여 WIP·다음 프롬프트를 남긴 뒤 멈춰라.
기본 다음 ID: 없음. 필수 gate 미달이면 먼저 같은 task를 재개하고 다음 task를 자동 실행하지 마라. push·배포·진단·치료·침 시뮬레이션 금지.
```
