# T95 이후 전체 실행 프롬프트

2026-09-28 · 기존 queue의 실행 안내만 정리. 새 task 발급/순서 변경/다음 구현 없음. T95는 사용자가 현재 진행 중이라고 알려 준 상태이며 이 문서가 완료를 승인하지 않는다.

## 사용 방법

1. 현재 T95를 마친 뒤 실제 보고서/검증/커밋을 확인한다. 다음 기본 ID는 T96이다. 번호 오름차순으로 실행하지 않는다.
2. 아래에서 요청할 task의 코드블록 하나만 붙여 넣는다. 각 블록은 이 문서의 공통 규칙과 해당 명세를 읽도록 되어 있다.
3. 담당은 기존 registry의 배정 그대로다. 기본 Luna Max, 복잡한 motion/신경 계약은 표기된 Sol High, T58/T85/T90은 Astra 현재 대화다. 자동 모델 전환/위임은 하지 않는다.
4. T122–T165는 superseded_not_executed다. 실행하지 않는다. 내부10개 완료는 전체 task 완료가 아니다.
5. 지역/계통 자료 작업의 미완은 같은 ID/nextUnit으로 재개한다. 자료·권리처럼 입력 부재로 막힌 경우 동일 검색만 반복하지 않는다. 실제로 독립적인 다음 작업만 보고서에 제안하며 자동 실행하지 않는다.
6. 아래는 조건부 기본 순서다. 선행 필수 gate가 미달이면 의존 구현을 시작하지 않는다. 특히 T110–121은 T96 exact package freeze, T98–100은 실제 광배근 객체/권리/정합, T47/T85는 전체 필수 운동, T90은 전체 필수 신경3D를 요구한다.
7. 새 자료/권리/rig 문제가 발견되면 최신 검증 결과와 명세가 우선한다. 현재 프롬프트가 존재한다고 미래 입력이 확보된 것으로 간주하지 않는다.

## 공통 실행 규칙

- AGENTS.md, 00-START-HERE.md, 03-LUNA-SERIAL-RUNBOOK.md, 최신 STATUS/R15 registry, 22-EFFICIENT-DELIVERY-AND-PERFORMANCE.md, 해당 task의 최신 명세와 선행 실제 보고서/evidence/manifest를 먼저 확인한다. 다른 상세 설계는 해당 명세에 지정된 부분만 읽고 역사 문서 전부를 매번 반복하지 않는다.
- 22 효율화 설계가 충돌하는 과거 자동 task 발급/10개당 번호 추가 문구보다 우선한다. 이 문서는 이를 각 실행 프롬프트에 적용한 안내이며 해부학적 합격 기준을 낮추지 않는다.
- 시작 HEAD/status/입력 hash와 사용자 WIP를 기록하고 원본/OpenSim_Models/T13 drafts/역사 freeze를 보존한다. 근거 없는 명칭/좌표/geometry/binding/권리/사람 승인을 만들지 않는다.
- 한 AnatomySceneRoot/renderer/camera와 미니멀 UI를 유지한다. 근육/task별 loader·카드·컴포넌트 복제 대신 공통 도구+데이터를 재사용한다. source-only/held/user layer-off/rights/human-review는 개별 증거 없이 승격하지 않는다.
- 요청한 task 범위만 수행한다. 내부 최대10 target 검증, clip1개/검증된 family 상한을 지킨다. 미완이면 progress manifest와 nextUnit으로 같은 task를 재개한다. 새 기술 위험을 수백 개 반복 task로 변환하지 않는다.
- 데이터만 바꾸면 관련 schema/ID/hash/정책 검증, UI/geometry를 바꾸면 필요한 실제 브라우저/회귀/typecheck/build 및22의 전후 성능 검증을 한다. 과거 모든 검사를 이유 없이 반복하지 않는다. 테스트 통과와 해부학/권리/전체 제품 완료를 구분한다.
- work/reports/<ID>.md, work/evidence/<ID>/, progress manifest, STATUS/R15 taskStatuses에 실제 범위·검증·미완을 기록한다. 소유 파일/hunk만 staged diff 확인 후 로컬 커밋한다. 기존 staged/WIP를 임의 포함하지 않는다.
- 종료 시 해시·포함/제외·잔여 변경·같은 task 재개 조건 또는 다음 실행 가능한 ID/프롬프트를 적고 멈춘다. 다음 task 자동 실행·push·배포·환자 진단·치료·자침 추천/시뮬레이션은 금지한다.
- 완료 gate 미달을 passed_with_gaps로 덮지 않는다. 기초 자료가 이미 있다면 확인 후 재사용하며 완성된 단계를 다시 구현하지 않는다.

## 같은 task 재개용

```text
HUMAN ATLAS에서 <현재 미완 ID>만 재개해라.
design/2026-09-25-muscle-atlas/23-PROMPTS-AFTER-T95.md의 공통 실행 규칙과 해당 ID 절, 최신 명세·보고서·progress manifest를 읽어라.
이미 통과한 산출물은 보존하고 기록된 nextUnit/필수 실패 범위만 이어서 해결해라. 입력이 바뀌지 않은 자료 부재를 같은 검색으로 반복하지 마라.
완료 기준을 낮추거나 새 반복 task를 발급하지 말고, 검증 후 소유 변경만 로컬 커밋하고 멈춰라.
다음 task 자동 실행·push·배포 금지.
```

## 전체 순서


### 1. 목표 동결·실제 누락 모형 확보

| 순서 | ID | 담당 | 내용 |
|---:|---|---|---|
| 1 | [T96](#t96) | Luna Max | 전체 목표 분류·반복근·뼈 분모 의미 검증 |
| 2 | [T79](#t79) | Luna Max | 양측 이두근·삼두근 10개 표면 확보·장면 통합 |
| 3 | [T97](#t97) | Luna Max | 광배근 공식 aggregate 실제 객체 확인 |
| 4 | [T101](#t101) | Luna Max | 근육 부분 누락 표면 1 취득·통합 |
| 5 | [T102](#t102) | Luna Max | 근육 부분 누락 표면 2 취득·통합 |
| 6 | [T103](#t103) | Luna Max | 근육 부분 누락 표면 3 취득·통합 |
| 7 | [T104](#t104) | Luna Max | 근육 부분 누락 표면 4 취득·통합 |
| 8 | [T105](#t105) | Luna Max | 근육 부분 누락 표면 5 취득·통합 |
| 9 | [T106](#t106) | Luna Max | 뼈 누락 표면 1 취득·통합 |
| 10 | [T107](#t107) | Luna Max | 뼈 누락 표면 2 취득·통합 |
| 11 | [T98](#t98) | Luna Max | 광배근 객체 권리·좌표·정적 자세 검증 |
| 12 | [T99](#t99) | Luna Max | 광배근 실제 모형 정합 |
| 13 | [T100](#t100) | Luna Max | 광배근 단일 장면 통합 |
| 14 | [T108](#t108) | Luna Max | 기존 보류 표면 개별 재검증 1 |
| 15 | [T109](#t109) | Luna Max | 기존 보류 표면 개별 재검증 2 |

### 2. 12부위 구조·이름·선택 연결

| 순서 | ID | 담당 | 내용 |
|---:|---|---|---|
| 16 | [T110](#t110) | Luna Max | 머리 구조 식별·이름·선택 연결 패키지 |
| 17 | [T111](#t111) | Luna Max | 목 구조 식별·이름·선택 연결 패키지 |
| 18 | [T112](#t112) | Luna Max | 등 구조 식별·이름·선택 연결 패키지 |
| 19 | [T113](#t113) | Luna Max | 어깨·어깨뼈 구조 식별·이름·선택 연결 패키지 |
| 20 | [T114](#t114) | Luna Max | 가슴우리 구조 식별·이름·선택 연결 패키지 |
| 21 | [T115](#t115) | Luna Max | 배·허리 구조 식별·이름·선택 연결 패키지 |
| 22 | [T116](#t116) | Luna Max | 골반·샅 구조 식별·이름·선택 연결 패키지 |
| 23 | [T117](#t117) | Luna Max | 볼기·깊은엉덩이 구조 식별·이름·선택 연결 패키지 |
| 24 | [T118](#t118) | Luna Max | 넙다리 구조 식별·이름·선택 연결 패키지 |
| 25 | [T119](#t119) | Luna Max | 종아리 구조 식별·이름·선택 연결 패키지 |
| 26 | [T120](#t120) | Luna Max | 발 구조 식별·이름·선택 연결 패키지 |
| 27 | [T121](#t121) | Luna Max | 팔·손 구조 식별·이름·선택 연결 패키지 |

### 3. 전신 구조·그래픽 합격

| 순서 | ID | 담당 | 내용 |
|---:|---|---|---|
| 28 | [T80](#t80) | Luna Max | 전신 구조·선택 coverage 감사 |
| 29 | [T58](#t58) | Astra · 현재 대화 직접 구현 | 전신 그래픽 재검증 |

### 4. 전체 기시정지·기능 설명

| 순서 | ID | 담당 | 내용 |
|---:|---|---|---|
| 30 | [T81](#t81) | Luna Max | 첫 전신 기시·정지 조사 batch |
| 31 | [T82](#t82) | Luna Max | 전신 기시·정지 프로토타입 합격 |
| 32 | [T83](#t83) | Luna Max | 첫 전신 근육 기능 조사 batch |
| 33 | [T84](#t84) | Luna Max | 전신 근육 기능 설명 합격 |

### 5. 같은 모형의 실제 움직임

| 순서 | ID | 담당 | 내용 |
|---:|---|---|---|
| 34 | [T35](#t35) | Sol High | 전신 근육 animation 목표와 제작 queue |
| 35 | [T59](#t59) | Sol High | 같은 앞정강근 표면의 교육용 수축 변형 |
| 36 | [T60](#t60) | Sol High | 동일 viewport에서 운동 재생 연결 |
| 37 | [T25](#t25) | Luna Max | 같은 전신 모형의 앞정강근 제품 합격 |
| 38 | [T27](#t27) | Sol High | 소흉근 동일 모형 변형 준비 |
| 39 | [T28](#t28) | Sol High | 견갑대 운동 기반과 전인 시범 하나 |
| 40 | [T45](#t45) | Sol High | 소흉근 관련 견갑골 하강 시범 |
| 41 | [T46](#t46) | Sol High | 소흉근 관련 견갑골 하방회전 시범 |
| 42 | [T29](#t29) | Luna Max | 소흉근 구조·기능 사용자 흐름 통합 |
| 43 | [T31](#t31) | Luna Max | 두 부위 구조·기능 파일럿 합격 검증 |
| 44 | [T66](#t66) | Luna Max | 첫 기능 확장 batch 하나 |
| 45 | [T47](#t47) | Luna Max | 전신 구조·기능·운동 자료 감사 |
| 46 | [T85](#t85) | Astra · 현재 대화 직접 구현 | 모든 근육 움직임 학습 coverage 합격 |

### 6. 신경 자료·3D·지배근·기능이상 설명

| 순서 | ID | 담당 | 내용 |
|---:|---|---|---|
| 47 | [T61](#t61) | Sol High | 신경 레이어·선택·관계 데이터 계약 |
| 48 | [T86](#t86) | Sol High | 전신 신경 목표·복수 원문 모델 조사 |
| 49 | [T62](#t62) | Luna Max | 첫 하지 신경 자료 패키지 |
| 50 | [T87](#t87) | Luna Max | 전신 신경 조사 확장 첫 batch |
| 51 | [T88](#t88) | Sol High | 전신 신경 자료 통합·등록 검증 |
| 52 | [T63](#t63) | Sol High | 첫 신경 3D 주행과 지배근 강조 |
| 53 | [T89](#t89) | Luna Max | 전신 신경 3D 확장 첫 batch |
| 54 | [T90](#t90) | Astra · 현재 대화 직접 구현 | 전신 신경 주행·지배근 그래픽 합격 |
| 55 | [T64](#t64) | Luna Max | 신경 포착·기능 변화의 접힌 설명 UI |
| 56 | [T91](#t91) | Luna Max | 신경 포착·기능이상 설명 확장 첫 batch |
| 57 | [T65](#t65) | Luna Max | 전신 근육·신경·기능이상 설명 최종 통합 검증 |

### 7. 로컬 전달과 최종 체크포인트

| 순서 | ID | 담당 | 내용 |
|---:|---|---|---|
| 58 | [T40](#t40) | Luna Max | 구조·기능 로컬 전달과 Git 체크포인트 |

## 개별 붙여 넣기 프롬프트

<a id="t96"></a>
### T96 — 전체 목표 분류·반복근·뼈 분모 의미 검증

담당: **Luna Max** · [최신 명세](../../work/tasks/T96.md)

```text
HUMAN ATLAS에서 T96만 수행해라. 담당 Luna Max.
design/2026-09-25-muscle-atlas/23-PROMPTS-AFTER-T95.md의 공통 실행 규칙과 이 ID 절,
22 효율화 설계, 최신 STATUS/R15 registry, work/tasks/T96.md와 선행 실제 보고서·evidence를 읽어라.
T78 후보와 제외 ledger를 의미 검증하고 12부위의 exact target/primary owner/workUnits manifest를 동결한다. 필수 누락을 빼서 분모를 줄이지 않는다. T110–T121의 실제 입력은 이 결과이며 아직 임의 배정하지 않는다.
기본 다음 ID: T79. 필수 미완이면 같은 ID로 재개하고 다음 단계로 자동 진행하지 마라.
소유 변경만 검증·로컬 커밋하고 해시·잔여 변경·다음 프롬프트를 남긴 뒤 멈춰라. push·배포 금지.
```

<a id="t79"></a>
### T79 — 양측 이두근·삼두근 10개 표면 확보·장면 통합

담당: **Luna Max** · [최신 명세](../../work/tasks/T79.md)

```text
HUMAN ATLAS에서 T79만 수행해라. 담당 Luna Max.
design/2026-09-25-muscle-atlas/23-PROMPTS-AFTER-T95.md의 공통 실행 규칙과 이 ID 절,
22 효율화 설계, 최신 STATUS/R15 registry, work/tasks/T79.md와 선행 실제 보고서·evidence를 읽어라.
동결한 source IDs만 기존 R4 취득·검증·변환 도구로 취득한다. ID/OBJ header/hash/side/part/units/frame/bounds와 T50/T69 변환을 개별 검증하고 실제 GLB surface를 같은 장면의 새 manifest revision에 통합한다. 기존 root/renderer를 재사용한다. parent whole-muscle surface와 part의 중첩이 있으면 geometry 범위를 확인해 product representation 정책으로 중복 표면을 막고 원본은 보존한다. ancestor 이름만으로 동일 개념 binding을 만들지 않는다. local display 적격성과 공개 재배포 권리를 별도 판정한다. source-only 기본 정책 유지, 보류는 항목별 격리. 새 전체 취득/archive 금지. 정확한 task subset의 정상 표시·좌우·근접/전신·layer-off·중복node·실제 브라우저가 필수. 3이름/canonical 연결은 뒤의 target batch에 맡겨 먼저 모형 외형을 확보한다.
기본 다음 ID: T97. 필수 미완이면 같은 ID로 재개하고 다음 단계로 자동 진행하지 마라.
소유 변경만 검증·로컬 커밋하고 해시·잔여 변경·다음 프롬프트를 남긴 뒤 멈춰라. push·배포 금지.
```

<a id="t97"></a>
### T97 — 광배근 공식 aggregate 실제 객체 확인

담당: **Luna Max** · [최신 명세](../../work/tasks/T97.md)

```text
HUMAN ATLAS에서 T97만 수행해라. 담당 Luna Max.
design/2026-09-25-muscle-atlas/23-PROMPTS-AFTER-T95.md의 공통 실행 규칙과 이 ID 절,
22 효율화 설계, 최신 STATUS/R15 registry, work/tasks/T97.md와 선행 실제 보고서·evidence를 읽어라.
T93/T94 no_exact_source_found를 보존한다. Z-Anatomy/Models-of-human-anatomy commit c7010a903b75a2fd24a13b1c2c4c3546a9223780의 Z-Anatomy.zip 단일 후보를 먼저 실제 취득·격리 검사한다. 전송 상한120MB, 해제 누적1GB, 파일10000개, 경로 탈출/symlink 금지; 예상 초과는 멈추고 별도 bounded 계획을 남긴다. 정확한 URL/commit/응답/크기/SHA256과 내부 파일·Blender object/data-block 이름 및 객체 경로 목록을 저장한다. Blender 자동실행 스크립트/드라이버 실행을 끈다. 최대 양측 광배근 객체/부분만 별도 추출하여 source ancestry, 오브젝트 ID/path, geometry hash, 좌우·부분 근거와 실제 표면 preview를 남긴다. 명칭 일치만으로 승인하지 않는다. 없으면 실제 archive 전체 객체 inventory와 부재 범위를 남기고 1개의 다음 실제 파일 후보에 대한 새로운 bounded 취득 task를 발급한다. 이름 검색을 반복하고 종료하는 대체는 불합격이다. 전체 archive/대용량 source는 ignore cache에 두고 이번 task는 장면/선택/권리를 승인하지 않는다.
기본 다음 ID: T101. 필수 미완이면 같은 ID로 재개하고 다음 단계로 자동 진행하지 마라.
소유 변경만 검증·로컬 커밋하고 해시·잔여 변경·다음 프롬프트를 남긴 뒤 멈춰라. push·배포 금지.
```

<a id="t101"></a>
### T101 — 근육 부분 누락 표면 1 취득·통합

담당: **Luna Max** · [최신 명세](../../work/tasks/T101.md)

```text
HUMAN ATLAS에서 T101만 수행해라. 담당 Luna Max.
design/2026-09-25-muscle-atlas/23-PROMPTS-AFTER-T95.md의 공통 실행 규칙과 이 ID 절,
22 효율화 설계, 최신 STATUS/R15 registry, work/tasks/T101.md와 선행 실제 보고서·evidence를 읽어라.
동결한 source IDs만 기존 R4 취득·검증·변환 도구로 취득한다. ID/OBJ header/hash/side/part/units/frame/bounds와 T50/T69 변환을 개별 검증하고 실제 GLB surface를 같은 장면의 새 manifest revision에 통합한다. 기존 root/renderer를 재사용한다. parent whole-muscle surface와 part의 중첩이 있으면 geometry 범위를 확인해 product representation 정책으로 중복 표면을 막고 원본은 보존한다. ancestor 이름만으로 동일 개념 binding을 만들지 않는다. local display 적격성과 공개 재배포 권리를 별도 판정한다. source-only 기본 정책 유지, 보류는 항목별 격리. 새 전체 취득/archive 금지. 정확한 task subset의 정상 표시·좌우·근접/전신·layer-off·중복node·실제 브라우저가 필수. 3이름/canonical 연결은 뒤의 target batch에 맡겨 먼저 모형 외형을 확보한다.
기본 다음 ID: T102. 필수 미완이면 같은 ID로 재개하고 다음 단계로 자동 진행하지 마라.
소유 변경만 검증·로컬 커밋하고 해시·잔여 변경·다음 프롬프트를 남긴 뒤 멈춰라. push·배포 금지.
```

<a id="t102"></a>
### T102 — 근육 부분 누락 표면 2 취득·통합

담당: **Luna Max** · [최신 명세](../../work/tasks/T102.md)

```text
HUMAN ATLAS에서 T102만 수행해라. 담당 Luna Max.
design/2026-09-25-muscle-atlas/23-PROMPTS-AFTER-T95.md의 공통 실행 규칙과 이 ID 절,
22 효율화 설계, 최신 STATUS/R15 registry, work/tasks/T102.md와 선행 실제 보고서·evidence를 읽어라.
동결한 source IDs만 기존 R4 취득·검증·변환 도구로 취득한다. ID/OBJ header/hash/side/part/units/frame/bounds와 T50/T69 변환을 개별 검증하고 실제 GLB surface를 같은 장면의 새 manifest revision에 통합한다. 기존 root/renderer를 재사용한다. parent whole-muscle surface와 part의 중첩이 있으면 geometry 범위를 확인해 product representation 정책으로 중복 표면을 막고 원본은 보존한다. ancestor 이름만으로 동일 개념 binding을 만들지 않는다. local display 적격성과 공개 재배포 권리를 별도 판정한다. source-only 기본 정책 유지, 보류는 항목별 격리. 새 전체 취득/archive 금지. 정확한 task subset의 정상 표시·좌우·근접/전신·layer-off·중복node·실제 브라우저가 필수. 3이름/canonical 연결은 뒤의 target batch에 맡겨 먼저 모형 외형을 확보한다.
기본 다음 ID: T103. 필수 미완이면 같은 ID로 재개하고 다음 단계로 자동 진행하지 마라.
소유 변경만 검증·로컬 커밋하고 해시·잔여 변경·다음 프롬프트를 남긴 뒤 멈춰라. push·배포 금지.
```

<a id="t103"></a>
### T103 — 근육 부분 누락 표면 3 취득·통합

담당: **Luna Max** · [최신 명세](../../work/tasks/T103.md)

```text
HUMAN ATLAS에서 T103만 수행해라. 담당 Luna Max.
design/2026-09-25-muscle-atlas/23-PROMPTS-AFTER-T95.md의 공통 실행 규칙과 이 ID 절,
22 효율화 설계, 최신 STATUS/R15 registry, work/tasks/T103.md와 선행 실제 보고서·evidence를 읽어라.
동결한 source IDs만 기존 R4 취득·검증·변환 도구로 취득한다. ID/OBJ header/hash/side/part/units/frame/bounds와 T50/T69 변환을 개별 검증하고 실제 GLB surface를 같은 장면의 새 manifest revision에 통합한다. 기존 root/renderer를 재사용한다. parent whole-muscle surface와 part의 중첩이 있으면 geometry 범위를 확인해 product representation 정책으로 중복 표면을 막고 원본은 보존한다. ancestor 이름만으로 동일 개념 binding을 만들지 않는다. local display 적격성과 공개 재배포 권리를 별도 판정한다. source-only 기본 정책 유지, 보류는 항목별 격리. 새 전체 취득/archive 금지. 정확한 task subset의 정상 표시·좌우·근접/전신·layer-off·중복node·실제 브라우저가 필수. 3이름/canonical 연결은 뒤의 target batch에 맡겨 먼저 모형 외형을 확보한다.
기본 다음 ID: T104. 필수 미완이면 같은 ID로 재개하고 다음 단계로 자동 진행하지 마라.
소유 변경만 검증·로컬 커밋하고 해시·잔여 변경·다음 프롬프트를 남긴 뒤 멈춰라. push·배포 금지.
```

<a id="t104"></a>
### T104 — 근육 부분 누락 표면 4 취득·통합

담당: **Luna Max** · [최신 명세](../../work/tasks/T104.md)

```text
HUMAN ATLAS에서 T104만 수행해라. 담당 Luna Max.
design/2026-09-25-muscle-atlas/23-PROMPTS-AFTER-T95.md의 공통 실행 규칙과 이 ID 절,
22 효율화 설계, 최신 STATUS/R15 registry, work/tasks/T104.md와 선행 실제 보고서·evidence를 읽어라.
동결한 source IDs만 기존 R4 취득·검증·변환 도구로 취득한다. ID/OBJ header/hash/side/part/units/frame/bounds와 T50/T69 변환을 개별 검증하고 실제 GLB surface를 같은 장면의 새 manifest revision에 통합한다. 기존 root/renderer를 재사용한다. parent whole-muscle surface와 part의 중첩이 있으면 geometry 범위를 확인해 product representation 정책으로 중복 표면을 막고 원본은 보존한다. ancestor 이름만으로 동일 개념 binding을 만들지 않는다. local display 적격성과 공개 재배포 권리를 별도 판정한다. source-only 기본 정책 유지, 보류는 항목별 격리. 새 전체 취득/archive 금지. 정확한 task subset의 정상 표시·좌우·근접/전신·layer-off·중복node·실제 브라우저가 필수. 3이름/canonical 연결은 뒤의 target batch에 맡겨 먼저 모형 외형을 확보한다.
기본 다음 ID: T105. 필수 미완이면 같은 ID로 재개하고 다음 단계로 자동 진행하지 마라.
소유 변경만 검증·로컬 커밋하고 해시·잔여 변경·다음 프롬프트를 남긴 뒤 멈춰라. push·배포 금지.
```

<a id="t105"></a>
### T105 — 근육 부분 누락 표면 5 취득·통합

담당: **Luna Max** · [최신 명세](../../work/tasks/T105.md)

```text
HUMAN ATLAS에서 T105만 수행해라. 담당 Luna Max.
design/2026-09-25-muscle-atlas/23-PROMPTS-AFTER-T95.md의 공통 실행 규칙과 이 ID 절,
22 효율화 설계, 최신 STATUS/R15 registry, work/tasks/T105.md와 선행 실제 보고서·evidence를 읽어라.
동결한 source IDs만 기존 R4 취득·검증·변환 도구로 취득한다. ID/OBJ header/hash/side/part/units/frame/bounds와 T50/T69 변환을 개별 검증하고 실제 GLB surface를 같은 장면의 새 manifest revision에 통합한다. 기존 root/renderer를 재사용한다. parent whole-muscle surface와 part의 중첩이 있으면 geometry 범위를 확인해 product representation 정책으로 중복 표면을 막고 원본은 보존한다. ancestor 이름만으로 동일 개념 binding을 만들지 않는다. local display 적격성과 공개 재배포 권리를 별도 판정한다. source-only 기본 정책 유지, 보류는 항목별 격리. 새 전체 취득/archive 금지. 정확한 task subset의 정상 표시·좌우·근접/전신·layer-off·중복node·실제 브라우저가 필수. 3이름/canonical 연결은 뒤의 target batch에 맡겨 먼저 모형 외형을 확보한다.
기본 다음 ID: T106. 필수 미완이면 같은 ID로 재개하고 다음 단계로 자동 진행하지 마라.
소유 변경만 검증·로컬 커밋하고 해시·잔여 변경·다음 프롬프트를 남긴 뒤 멈춰라. push·배포 금지.
```

<a id="t106"></a>
### T106 — 뼈 누락 표면 1 취득·통합

담당: **Luna Max** · [최신 명세](../../work/tasks/T106.md)

```text
HUMAN ATLAS에서 T106만 수행해라. 담당 Luna Max.
design/2026-09-25-muscle-atlas/23-PROMPTS-AFTER-T95.md의 공통 실행 규칙과 이 ID 절,
22 효율화 설계, 최신 STATUS/R15 registry, work/tasks/T106.md와 선행 실제 보고서·evidence를 읽어라.
동결한 source IDs만 기존 R4 취득·검증·변환 도구로 취득한다. ID/OBJ header/hash/side/part/units/frame/bounds와 T50/T69 변환을 개별 검증하고 실제 GLB surface를 같은 장면의 새 manifest revision에 통합한다. 기존 root/renderer를 재사용한다. parent whole-muscle surface와 part의 중첩이 있으면 geometry 범위를 확인해 product representation 정책으로 중복 표면을 막고 원본은 보존한다. ancestor 이름만으로 동일 개념 binding을 만들지 않는다. local display 적격성과 공개 재배포 권리를 별도 판정한다. source-only 기본 정책 유지, 보류는 항목별 격리. 새 전체 취득/archive 금지. 정확한 task subset의 정상 표시·좌우·근접/전신·layer-off·중복node·실제 브라우저가 필수. 3이름/canonical 연결은 뒤의 target batch에 맡겨 먼저 모형 외형을 확보한다.
기본 다음 ID: T107. 필수 미완이면 같은 ID로 재개하고 다음 단계로 자동 진행하지 마라.
소유 변경만 검증·로컬 커밋하고 해시·잔여 변경·다음 프롬프트를 남긴 뒤 멈춰라. push·배포 금지.
```

<a id="t107"></a>
### T107 — 뼈 누락 표면 2 취득·통합

담당: **Luna Max** · [최신 명세](../../work/tasks/T107.md)

```text
HUMAN ATLAS에서 T107만 수행해라. 담당 Luna Max.
design/2026-09-25-muscle-atlas/23-PROMPTS-AFTER-T95.md의 공통 실행 규칙과 이 ID 절,
22 효율화 설계, 최신 STATUS/R15 registry, work/tasks/T107.md와 선행 실제 보고서·evidence를 읽어라.
동결한 source IDs만 기존 R4 취득·검증·변환 도구로 취득한다. ID/OBJ header/hash/side/part/units/frame/bounds와 T50/T69 변환을 개별 검증하고 실제 GLB surface를 같은 장면의 새 manifest revision에 통합한다. 기존 root/renderer를 재사용한다. parent whole-muscle surface와 part의 중첩이 있으면 geometry 범위를 확인해 product representation 정책으로 중복 표면을 막고 원본은 보존한다. ancestor 이름만으로 동일 개념 binding을 만들지 않는다. local display 적격성과 공개 재배포 권리를 별도 판정한다. source-only 기본 정책 유지, 보류는 항목별 격리. 새 전체 취득/archive 금지. 정확한 task subset의 정상 표시·좌우·근접/전신·layer-off·중복node·실제 브라우저가 필수. 3이름/canonical 연결은 뒤의 target batch에 맡겨 먼저 모형 외형을 확보한다.
기본 다음 ID: T98. 필수 미완이면 같은 ID로 재개하고 다음 단계로 자동 진행하지 마라.
소유 변경만 검증·로컬 커밋하고 해시·잔여 변경·다음 프롬프트를 남긴 뒤 멈춰라. push·배포 금지.
```

<a id="t98"></a>
### T98 — 광배근 객체 권리·좌표·정적 자세 검증

담당: **Luna Max** · [최신 명세](../../work/tasks/T98.md)

```text
HUMAN ATLAS에서 T98만 수행해라. 담당 Luna Max.
design/2026-09-25-muscle-atlas/23-PROMPTS-AFTER-T95.md의 공통 실행 규칙과 이 ID 절,
22 효율화 설계, 최신 STATUS/R15 registry, work/tasks/T98.md와 선행 실제 보고서·evidence를 읽어라.
T97 실제 객체가 있어야 한다. exact object별 BodyParts3D ancestry와 수정자/라이선스 적용을 공식 repo 기록·포함 LICENSE/객체 metadata로 추적하고 로컬 사용/변형/공개재배포를 각각 판정한다. 단위, 축/handedness, object와parent transform, rest pose, 좌우/부분, bounding box·좌표표지·거울변환 여부를 실제 vertex로 검증한다. TA2 2231나 일반 README만으로 개별 권리를 승인하지 않는다. rights 불명확하면 해당 gate held와 필요한 증거를 기록한다. 다른 모델 정합 필요 여부를 실제 비교로 판정한다. 기술 검증은 humanReviewed=true가 아니다. 다른 모델이면 T99 전에는 scene에 넣지 않는다.
기본 다음 ID: T99. 필수 미완이면 같은 ID로 재개하고 다음 단계로 자동 진행하지 마라.
소유 변경만 검증·로컬 커밋하고 해시·잔여 변경·다음 프롬프트를 남긴 뒤 멈춰라. push·배포 금지.
```

<a id="t99"></a>
### T99 — 광배근 실제 모형 정합

담당: **Luna Max** · [최신 명세](../../work/tasks/T99.md)

```text
HUMAN ATLAS에서 T99만 수행해라. 담당 Luna Max.
design/2026-09-25-muscle-atlas/23-PROMPTS-AFTER-T95.md의 공통 실행 규칙과 이 ID 절,
22 효율화 설계, 최신 STATUS/R15 registry, work/tasks/T99.md와 선행 실제 보고서·evidence를 읽어라.
T98에서 파생/정합에 필요한 사용 권리와 객체 identity/frame이 확인된 부분만 처리한다. T50 현재 해부학적 정적 자세와 공통 landmark의 의미·좌표를 대조한다. fitting 전 기준 landmark, 독립 평가 landmark, mm 오차 한계와 시각 허용 기준을 근거와 함께 동결한다. 실제 좌표계 변환 및 필요한 registration 결과·잔차·좌우·shape 보존·몸통/상완 관계를 검증한다. min/max 크기맞춤, 좌우 임의복제, 이름/ancestry 기반 호환 추정 금지. 부적합 affine/nonrigid로 해부구조가 망가지면 통합하지 말고 구체적인 수정 범위를 남긴다. 결과 transform/derivation hash 및 before/after preview를 저장한다. 동일 frame 증명이 있으면 identity transform도 검증 artifact로 남기며 그냥 생략 완료하지 않는다. rig/animation 없음.
기본 다음 ID: T100. 필수 미완이면 같은 ID로 재개하고 다음 단계로 자동 진행하지 마라.
소유 변경만 검증·로컬 커밋하고 해시·잔여 변경·다음 프롬프트를 남긴 뒤 멈춰라. push·배포 금지.
```

<a id="t100"></a>
### T100 — 광배근 단일 장면 통합

담당: **Luna Max** · [최신 명세](../../work/tasks/T100.md)

```text
HUMAN ATLAS에서 T100만 수행해라. 담당 Luna Max.
design/2026-09-25-muscle-atlas/23-PROMPTS-AFTER-T95.md의 공통 실행 규칙과 이 ID 절,
22 효율화 설계, 최신 STATUS/R15 registry, work/tasks/T100.md와 선행 실제 보고서·evidence를 읽어라.
T97–99의 실제 객체·권리·좌표·정합 통과 subset만 기존 root/renderer/camera에 통합한다. 기존 source ID 불변, 신규 object instance ID와 hash/ancestry를 별도 저장한다. back/shoulder 맥락 membership, layer-off, 양측/후면/상완과의 경계·깊은 구조·중복표면을 실제 브라우저 검증한다. 정확한 canonical identity와 검증된 이름 overlay가 있을 때만 선택 연결하며 없으면 source_only_unbound. 광배근 표면이 등장한 것과 기시정지/작용/모션 완성은 별개다. 한쪽만 있으면 양측 완료 금지. held는 유지하고 새 전신 denominator를 주장하지 않는다.
기본 다음 ID: T108. 필수 미완이면 같은 ID로 재개하고 다음 단계로 자동 진행하지 마라.
소유 변경만 검증·로컬 커밋하고 해시·잔여 변경·다음 프롬프트를 남긴 뒤 멈춰라. push·배포 금지.
```

<a id="t108"></a>
### T108 — 기존 보류 표면 개별 재검증 1

담당: **Luna Max** · [최신 명세](../../work/tasks/T108.md)

```text
HUMAN ATLAS에서 T108만 수행해라. 담당 Luna Max.
design/2026-09-25-muscle-atlas/23-PROMPTS-AFTER-T95.md의 공통 실행 규칙과 이 ID 절,
22 효율화 설계, 최신 STATUS/R15 registry, work/tasks/T108.md와 선행 실제 보고서·evidence를 읽어라.
지정 source ID의 기존 hold 원인과 실제 source header/양측 geometry/공식 관계를 대조한다. AABB 중앙면 교차만으로 잘못된 좌우라 단정하지 않는다. 항목별 해소 증거가 있으면 별도 versioned overlay로 정정·표시하고 역사 freeze는 보존한다. 증거 없는 human approval/자동좌우교체 금지. 해결되지 않은 것은 held 유지, 실제 geometry 검사 결과와 추가로 필요한 자료를 명확히 남긴다. identity가 불명인 표면에 근육명을 만들어 붙이지 않는다. 해결된 항목이 있으면 실제 장면/정책 회귀가 필수.
기본 다음 ID: T109. 필수 미완이면 같은 ID로 재개하고 다음 단계로 자동 진행하지 마라.
소유 변경만 검증·로컬 커밋하고 해시·잔여 변경·다음 프롬프트를 남긴 뒤 멈춰라. push·배포 금지.
```

<a id="t109"></a>
### T109 — 기존 보류 표면 개별 재검증 2

담당: **Luna Max** · [최신 명세](../../work/tasks/T109.md)

```text
HUMAN ATLAS에서 T109만 수행해라. 담당 Luna Max.
design/2026-09-25-muscle-atlas/23-PROMPTS-AFTER-T95.md의 공통 실행 규칙과 이 ID 절,
22 효율화 설계, 최신 STATUS/R15 registry, work/tasks/T109.md와 선행 실제 보고서·evidence를 읽어라.
지정 source ID의 기존 hold 원인과 실제 source header/양측 geometry/공식 관계를 대조한다. AABB 중앙면 교차만으로 잘못된 좌우라 단정하지 않는다. 항목별 해소 증거가 있으면 별도 versioned overlay로 정정·표시하고 역사 freeze는 보존한다. 증거 없는 human approval/자동좌우교체 금지. 해결되지 않은 것은 held 유지, 실제 geometry 검사 결과와 추가로 필요한 자료를 명확히 남긴다. identity가 불명인 표면에 근육명을 만들어 붙이지 않는다. 해결된 항목이 있으면 실제 장면/정책 회귀가 필수.
기본 다음 ID: T110. 필수 미완이면 같은 ID로 재개하고 다음 단계로 자동 진행하지 마라.
소유 변경만 검증·로컬 커밋하고 해시·잔여 변경·다음 프롬프트를 남긴 뒤 멈춰라. push·배포 금지.
```

<a id="t110"></a>
### T110 — 머리 구조 식별·이름·선택 연결 패키지

담당: **Luna Max** · [최신 명세](../../work/tasks/T110.md)

```text
HUMAN ATLAS에서 T110만 수행해라. 담당 Luna Max.
design/2026-09-25-muscle-atlas/23-PROMPTS-AFTER-T95.md의 공통 실행 규칙과 이 ID 절,
22 효율화 설계, 최신 STATUS/R15 registry, work/tasks/T110.md와 선행 실제 보고서·evidence를 읽어라.
T96 region-packages.json의 head primary-owner subset만 수행한다. 실행 전에 exact target IDs/버전/hash와 내부 최대10개 workUnits를 확인한다. T96 manifest가 없거나 누락/중복 owner가 있으면 임의 분류로 시작하지 않는다. 기존 geometry를 우선 재사용하여 각 target의 실제 object/side/part identity, 세 이름과 alias, typed card/검색/선택을 공통 adapter로 연결한다. source-only/held 승격은 항목별 증거가 있어야 한다. missing은 exact 실제 파일/객체 검사와 권리/frame 근거로 처리하며 다른 source family 정합이 필요하면 별도 의존 gate로 남겨 추정 통합하지 않는다. 이 package는 머리 구조 단계이며 기시정지 신규 집필·기능·모션은 후반 단계다. 전체 package를 완료하지 못하면 같은 ID와 nextUnit으로 재개하고 새 번호를 만들지 않는다. 기존 공통 도구를 재사용하고 부위별 엔진을 복제하지 않는다. 모든 필수 subset 결과·누락·최종 화면·성능을 기록한다. 이전 이 파일의 TA2순서10개 scope는 역사 계획이다.
기본 다음 ID: T111. 필수 미완이면 같은 ID로 재개하고 다음 단계로 자동 진행하지 마라.
소유 변경만 검증·로컬 커밋하고 해시·잔여 변경·다음 프롬프트를 남긴 뒤 멈춰라. push·배포 금지.
```

<a id="t111"></a>
### T111 — 목 구조 식별·이름·선택 연결 패키지

담당: **Luna Max** · [최신 명세](../../work/tasks/T111.md)

```text
HUMAN ATLAS에서 T111만 수행해라. 담당 Luna Max.
design/2026-09-25-muscle-atlas/23-PROMPTS-AFTER-T95.md의 공통 실행 규칙과 이 ID 절,
22 효율화 설계, 최신 STATUS/R15 registry, work/tasks/T111.md와 선행 실제 보고서·evidence를 읽어라.
T96 region-packages.json의 neck primary-owner subset만 수행한다. 실행 전에 exact target IDs/버전/hash와 내부 최대10개 workUnits를 확인한다. T96 manifest가 없거나 누락/중복 owner가 있으면 임의 분류로 시작하지 않는다. 기존 geometry를 우선 재사용하여 각 target의 실제 object/side/part identity, 세 이름과 alias, typed card/검색/선택을 공통 adapter로 연결한다. source-only/held 승격은 항목별 증거가 있어야 한다. missing은 exact 실제 파일/객체 검사와 권리/frame 근거로 처리하며 다른 source family 정합이 필요하면 별도 의존 gate로 남겨 추정 통합하지 않는다. 이 package는 목 구조 단계이며 기시정지 신규 집필·기능·모션은 후반 단계다. 전체 package를 완료하지 못하면 같은 ID와 nextUnit으로 재개하고 새 번호를 만들지 않는다. 기존 공통 도구를 재사용하고 부위별 엔진을 복제하지 않는다. 모든 필수 subset 결과·누락·최종 화면·성능을 기록한다. 이전 이 파일의 TA2순서10개 scope는 역사 계획이다.
기본 다음 ID: T112. 필수 미완이면 같은 ID로 재개하고 다음 단계로 자동 진행하지 마라.
소유 변경만 검증·로컬 커밋하고 해시·잔여 변경·다음 프롬프트를 남긴 뒤 멈춰라. push·배포 금지.
```

<a id="t112"></a>
### T112 — 등 구조 식별·이름·선택 연결 패키지

담당: **Luna Max** · [최신 명세](../../work/tasks/T112.md)

```text
HUMAN ATLAS에서 T112만 수행해라. 담당 Luna Max.
design/2026-09-25-muscle-atlas/23-PROMPTS-AFTER-T95.md의 공통 실행 규칙과 이 ID 절,
22 효율화 설계, 최신 STATUS/R15 registry, work/tasks/T112.md와 선행 실제 보고서·evidence를 읽어라.
T96 region-packages.json의 back primary-owner subset만 수행한다. 실행 전에 exact target IDs/버전/hash와 내부 최대10개 workUnits를 확인한다. T96 manifest가 없거나 누락/중복 owner가 있으면 임의 분류로 시작하지 않는다. 기존 geometry를 우선 재사용하여 각 target의 실제 object/side/part identity, 세 이름과 alias, typed card/검색/선택을 공통 adapter로 연결한다. source-only/held 승격은 항목별 증거가 있어야 한다. missing은 exact 실제 파일/객체 검사와 권리/frame 근거로 처리하며 다른 source family 정합이 필요하면 별도 의존 gate로 남겨 추정 통합하지 않는다. 이 package는 등 구조 단계이며 기시정지 신규 집필·기능·모션은 후반 단계다. 전체 package를 완료하지 못하면 같은 ID와 nextUnit으로 재개하고 새 번호를 만들지 않는다. 기존 공통 도구를 재사용하고 부위별 엔진을 복제하지 않는다. 모든 필수 subset 결과·누락·최종 화면·성능을 기록한다. 이전 이 파일의 TA2순서10개 scope는 역사 계획이다.
기본 다음 ID: T113. 필수 미완이면 같은 ID로 재개하고 다음 단계로 자동 진행하지 마라.
소유 변경만 검증·로컬 커밋하고 해시·잔여 변경·다음 프롬프트를 남긴 뒤 멈춰라. push·배포 금지.
```

<a id="t113"></a>
### T113 — 어깨·어깨뼈 구조 식별·이름·선택 연결 패키지

담당: **Luna Max** · [최신 명세](../../work/tasks/T113.md)

```text
HUMAN ATLAS에서 T113만 수행해라. 담당 Luna Max.
design/2026-09-25-muscle-atlas/23-PROMPTS-AFTER-T95.md의 공통 실행 규칙과 이 ID 절,
22 효율화 설계, 최신 STATUS/R15 registry, work/tasks/T113.md와 선행 실제 보고서·evidence를 읽어라.
T96 region-packages.json의 shoulder-scapular primary-owner subset만 수행한다. 실행 전에 exact target IDs/버전/hash와 내부 최대10개 workUnits를 확인한다. T96 manifest가 없거나 누락/중복 owner가 있으면 임의 분류로 시작하지 않는다. 기존 geometry를 우선 재사용하여 각 target의 실제 object/side/part identity, 세 이름과 alias, typed card/검색/선택을 공통 adapter로 연결한다. source-only/held 승격은 항목별 증거가 있어야 한다. missing은 exact 실제 파일/객체 검사와 권리/frame 근거로 처리하며 다른 source family 정합이 필요하면 별도 의존 gate로 남겨 추정 통합하지 않는다. 이 package는 어깨·어깨뼈 구조 단계이며 기시정지 신규 집필·기능·모션은 후반 단계다. 전체 package를 완료하지 못하면 같은 ID와 nextUnit으로 재개하고 새 번호를 만들지 않는다. 기존 공통 도구를 재사용하고 부위별 엔진을 복제하지 않는다. 모든 필수 subset 결과·누락·최종 화면·성능을 기록한다. 이전 이 파일의 TA2순서10개 scope는 역사 계획이다.
기본 다음 ID: T114. 필수 미완이면 같은 ID로 재개하고 다음 단계로 자동 진행하지 마라.
소유 변경만 검증·로컬 커밋하고 해시·잔여 변경·다음 프롬프트를 남긴 뒤 멈춰라. push·배포 금지.
```

<a id="t114"></a>
### T114 — 가슴우리 구조 식별·이름·선택 연결 패키지

담당: **Luna Max** · [최신 명세](../../work/tasks/T114.md)

```text
HUMAN ATLAS에서 T114만 수행해라. 담당 Luna Max.
design/2026-09-25-muscle-atlas/23-PROMPTS-AFTER-T95.md의 공통 실행 규칙과 이 ID 절,
22 효율화 설계, 최신 STATUS/R15 registry, work/tasks/T114.md와 선행 실제 보고서·evidence를 읽어라.
T96 region-packages.json의 thorax primary-owner subset만 수행한다. 실행 전에 exact target IDs/버전/hash와 내부 최대10개 workUnits를 확인한다. T96 manifest가 없거나 누락/중복 owner가 있으면 임의 분류로 시작하지 않는다. 기존 geometry를 우선 재사용하여 각 target의 실제 object/side/part identity, 세 이름과 alias, typed card/검색/선택을 공통 adapter로 연결한다. source-only/held 승격은 항목별 증거가 있어야 한다. missing은 exact 실제 파일/객체 검사와 권리/frame 근거로 처리하며 다른 source family 정합이 필요하면 별도 의존 gate로 남겨 추정 통합하지 않는다. 이 package는 가슴우리 구조 단계이며 기시정지 신규 집필·기능·모션은 후반 단계다. 전체 package를 완료하지 못하면 같은 ID와 nextUnit으로 재개하고 새 번호를 만들지 않는다. 기존 공통 도구를 재사용하고 부위별 엔진을 복제하지 않는다. 모든 필수 subset 결과·누락·최종 화면·성능을 기록한다. 이전 이 파일의 TA2순서10개 scope는 역사 계획이다.
기본 다음 ID: T115. 필수 미완이면 같은 ID로 재개하고 다음 단계로 자동 진행하지 마라.
소유 변경만 검증·로컬 커밋하고 해시·잔여 변경·다음 프롬프트를 남긴 뒤 멈춰라. push·배포 금지.
```

<a id="t115"></a>
### T115 — 배·허리 구조 식별·이름·선택 연결 패키지

담당: **Luna Max** · [최신 명세](../../work/tasks/T115.md)

```text
HUMAN ATLAS에서 T115만 수행해라. 담당 Luna Max.
design/2026-09-25-muscle-atlas/23-PROMPTS-AFTER-T95.md의 공통 실행 규칙과 이 ID 절,
22 효율화 설계, 최신 STATUS/R15 registry, work/tasks/T115.md와 선행 실제 보고서·evidence를 읽어라.
T96 region-packages.json의 abdomen-lumbar primary-owner subset만 수행한다. 실행 전에 exact target IDs/버전/hash와 내부 최대10개 workUnits를 확인한다. T96 manifest가 없거나 누락/중복 owner가 있으면 임의 분류로 시작하지 않는다. 기존 geometry를 우선 재사용하여 각 target의 실제 object/side/part identity, 세 이름과 alias, typed card/검색/선택을 공통 adapter로 연결한다. source-only/held 승격은 항목별 증거가 있어야 한다. missing은 exact 실제 파일/객체 검사와 권리/frame 근거로 처리하며 다른 source family 정합이 필요하면 별도 의존 gate로 남겨 추정 통합하지 않는다. 이 package는 배·허리 구조 단계이며 기시정지 신규 집필·기능·모션은 후반 단계다. 전체 package를 완료하지 못하면 같은 ID와 nextUnit으로 재개하고 새 번호를 만들지 않는다. 기존 공통 도구를 재사용하고 부위별 엔진을 복제하지 않는다. 모든 필수 subset 결과·누락·최종 화면·성능을 기록한다. 이전 이 파일의 TA2순서10개 scope는 역사 계획이다.
기본 다음 ID: T116. 필수 미완이면 같은 ID로 재개하고 다음 단계로 자동 진행하지 마라.
소유 변경만 검증·로컬 커밋하고 해시·잔여 변경·다음 프롬프트를 남긴 뒤 멈춰라. push·배포 금지.
```

<a id="t116"></a>
### T116 — 골반·샅 구조 식별·이름·선택 연결 패키지

담당: **Luna Max** · [최신 명세](../../work/tasks/T116.md)

```text
HUMAN ATLAS에서 T116만 수행해라. 담당 Luna Max.
design/2026-09-25-muscle-atlas/23-PROMPTS-AFTER-T95.md의 공통 실행 규칙과 이 ID 절,
22 효율화 설계, 최신 STATUS/R15 registry, work/tasks/T116.md와 선행 실제 보고서·evidence를 읽어라.
T96 region-packages.json의 pelvis-perineum primary-owner subset만 수행한다. 실행 전에 exact target IDs/버전/hash와 내부 최대10개 workUnits를 확인한다. T96 manifest가 없거나 누락/중복 owner가 있으면 임의 분류로 시작하지 않는다. 기존 geometry를 우선 재사용하여 각 target의 실제 object/side/part identity, 세 이름과 alias, typed card/검색/선택을 공통 adapter로 연결한다. source-only/held 승격은 항목별 증거가 있어야 한다. missing은 exact 실제 파일/객체 검사와 권리/frame 근거로 처리하며 다른 source family 정합이 필요하면 별도 의존 gate로 남겨 추정 통합하지 않는다. 이 package는 골반·샅 구조 단계이며 기시정지 신규 집필·기능·모션은 후반 단계다. 전체 package를 완료하지 못하면 같은 ID와 nextUnit으로 재개하고 새 번호를 만들지 않는다. 기존 공통 도구를 재사용하고 부위별 엔진을 복제하지 않는다. 모든 필수 subset 결과·누락·최종 화면·성능을 기록한다. 이전 이 파일의 TA2순서10개 scope는 역사 계획이다.
기본 다음 ID: T117. 필수 미완이면 같은 ID로 재개하고 다음 단계로 자동 진행하지 마라.
소유 변경만 검증·로컬 커밋하고 해시·잔여 변경·다음 프롬프트를 남긴 뒤 멈춰라. push·배포 금지.
```

<a id="t117"></a>
### T117 — 볼기·깊은엉덩이 구조 식별·이름·선택 연결 패키지

담당: **Luna Max** · [최신 명세](../../work/tasks/T117.md)

```text
HUMAN ATLAS에서 T117만 수행해라. 담당 Luna Max.
design/2026-09-25-muscle-atlas/23-PROMPTS-AFTER-T95.md의 공통 실행 규칙과 이 ID 절,
22 효율화 설계, 최신 STATUS/R15 registry, work/tasks/T117.md와 선행 실제 보고서·evidence를 읽어라.
T96 region-packages.json의 gluteal-hip primary-owner subset만 수행한다. 실행 전에 exact target IDs/버전/hash와 내부 최대10개 workUnits를 확인한다. T96 manifest가 없거나 누락/중복 owner가 있으면 임의 분류로 시작하지 않는다. 기존 geometry를 우선 재사용하여 각 target의 실제 object/side/part identity, 세 이름과 alias, typed card/검색/선택을 공통 adapter로 연결한다. source-only/held 승격은 항목별 증거가 있어야 한다. missing은 exact 실제 파일/객체 검사와 권리/frame 근거로 처리하며 다른 source family 정합이 필요하면 별도 의존 gate로 남겨 추정 통합하지 않는다. 이 package는 볼기·깊은엉덩이 구조 단계이며 기시정지 신규 집필·기능·모션은 후반 단계다. 전체 package를 완료하지 못하면 같은 ID와 nextUnit으로 재개하고 새 번호를 만들지 않는다. 기존 공통 도구를 재사용하고 부위별 엔진을 복제하지 않는다. 모든 필수 subset 결과·누락·최종 화면·성능을 기록한다. 이전 이 파일의 TA2순서10개 scope는 역사 계획이다.
기본 다음 ID: T118. 필수 미완이면 같은 ID로 재개하고 다음 단계로 자동 진행하지 마라.
소유 변경만 검증·로컬 커밋하고 해시·잔여 변경·다음 프롬프트를 남긴 뒤 멈춰라. push·배포 금지.
```

<a id="t118"></a>
### T118 — 넙다리 구조 식별·이름·선택 연결 패키지

담당: **Luna Max** · [최신 명세](../../work/tasks/T118.md)

```text
HUMAN ATLAS에서 T118만 수행해라. 담당 Luna Max.
design/2026-09-25-muscle-atlas/23-PROMPTS-AFTER-T95.md의 공통 실행 규칙과 이 ID 절,
22 효율화 설계, 최신 STATUS/R15 registry, work/tasks/T118.md와 선행 실제 보고서·evidence를 읽어라.
T96 region-packages.json의 thigh primary-owner subset만 수행한다. 실행 전에 exact target IDs/버전/hash와 내부 최대10개 workUnits를 확인한다. T96 manifest가 없거나 누락/중복 owner가 있으면 임의 분류로 시작하지 않는다. 기존 geometry를 우선 재사용하여 각 target의 실제 object/side/part identity, 세 이름과 alias, typed card/검색/선택을 공통 adapter로 연결한다. source-only/held 승격은 항목별 증거가 있어야 한다. missing은 exact 실제 파일/객체 검사와 권리/frame 근거로 처리하며 다른 source family 정합이 필요하면 별도 의존 gate로 남겨 추정 통합하지 않는다. 이 package는 넙다리 구조 단계이며 기시정지 신규 집필·기능·모션은 후반 단계다. 전체 package를 완료하지 못하면 같은 ID와 nextUnit으로 재개하고 새 번호를 만들지 않는다. 기존 공통 도구를 재사용하고 부위별 엔진을 복제하지 않는다. 모든 필수 subset 결과·누락·최종 화면·성능을 기록한다. 이전 이 파일의 TA2순서10개 scope는 역사 계획이다.
기본 다음 ID: T119. 필수 미완이면 같은 ID로 재개하고 다음 단계로 자동 진행하지 마라.
소유 변경만 검증·로컬 커밋하고 해시·잔여 변경·다음 프롬프트를 남긴 뒤 멈춰라. push·배포 금지.
```

<a id="t119"></a>
### T119 — 종아리 구조 식별·이름·선택 연결 패키지

담당: **Luna Max** · [최신 명세](../../work/tasks/T119.md)

```text
HUMAN ATLAS에서 T119만 수행해라. 담당 Luna Max.
design/2026-09-25-muscle-atlas/23-PROMPTS-AFTER-T95.md의 공통 실행 규칙과 이 ID 절,
22 효율화 설계, 최신 STATUS/R15 registry, work/tasks/T119.md와 선행 실제 보고서·evidence를 읽어라.
T96 region-packages.json의 leg primary-owner subset만 수행한다. 실행 전에 exact target IDs/버전/hash와 내부 최대10개 workUnits를 확인한다. T96 manifest가 없거나 누락/중복 owner가 있으면 임의 분류로 시작하지 않는다. 기존 geometry를 우선 재사용하여 각 target의 실제 object/side/part identity, 세 이름과 alias, typed card/검색/선택을 공통 adapter로 연결한다. source-only/held 승격은 항목별 증거가 있어야 한다. missing은 exact 실제 파일/객체 검사와 권리/frame 근거로 처리하며 다른 source family 정합이 필요하면 별도 의존 gate로 남겨 추정 통합하지 않는다. 이 package는 종아리 구조 단계이며 기시정지 신규 집필·기능·모션은 후반 단계다. 전체 package를 완료하지 못하면 같은 ID와 nextUnit으로 재개하고 새 번호를 만들지 않는다. 기존 공통 도구를 재사용하고 부위별 엔진을 복제하지 않는다. 모든 필수 subset 결과·누락·최종 화면·성능을 기록한다. 이전 이 파일의 TA2순서10개 scope는 역사 계획이다.
기본 다음 ID: T120. 필수 미완이면 같은 ID로 재개하고 다음 단계로 자동 진행하지 마라.
소유 변경만 검증·로컬 커밋하고 해시·잔여 변경·다음 프롬프트를 남긴 뒤 멈춰라. push·배포 금지.
```

<a id="t120"></a>
### T120 — 발 구조 식별·이름·선택 연결 패키지

담당: **Luna Max** · [최신 명세](../../work/tasks/T120.md)

```text
HUMAN ATLAS에서 T120만 수행해라. 담당 Luna Max.
design/2026-09-25-muscle-atlas/23-PROMPTS-AFTER-T95.md의 공통 실행 규칙과 이 ID 절,
22 효율화 설계, 최신 STATUS/R15 registry, work/tasks/T120.md와 선행 실제 보고서·evidence를 읽어라.
T96 region-packages.json의 foot primary-owner subset만 수행한다. 실행 전에 exact target IDs/버전/hash와 내부 최대10개 workUnits를 확인한다. T96 manifest가 없거나 누락/중복 owner가 있으면 임의 분류로 시작하지 않는다. 기존 geometry를 우선 재사용하여 각 target의 실제 object/side/part identity, 세 이름과 alias, typed card/검색/선택을 공통 adapter로 연결한다. source-only/held 승격은 항목별 증거가 있어야 한다. missing은 exact 실제 파일/객체 검사와 권리/frame 근거로 처리하며 다른 source family 정합이 필요하면 별도 의존 gate로 남겨 추정 통합하지 않는다. 이 package는 발 구조 단계이며 기시정지 신규 집필·기능·모션은 후반 단계다. 전체 package를 완료하지 못하면 같은 ID와 nextUnit으로 재개하고 새 번호를 만들지 않는다. 기존 공통 도구를 재사용하고 부위별 엔진을 복제하지 않는다. 모든 필수 subset 결과·누락·최종 화면·성능을 기록한다. 이전 이 파일의 TA2순서10개 scope는 역사 계획이다.
기본 다음 ID: T121. 필수 미완이면 같은 ID로 재개하고 다음 단계로 자동 진행하지 마라.
소유 변경만 검증·로컬 커밋하고 해시·잔여 변경·다음 프롬프트를 남긴 뒤 멈춰라. push·배포 금지.
```

<a id="t121"></a>
### T121 — 팔·손 구조 식별·이름·선택 연결 패키지

담당: **Luna Max** · [최신 명세](../../work/tasks/T121.md)

```text
HUMAN ATLAS에서 T121만 수행해라. 담당 Luna Max.
design/2026-09-25-muscle-atlas/23-PROMPTS-AFTER-T95.md의 공통 실행 규칙과 이 ID 절,
22 효율화 설계, 최신 STATUS/R15 registry, work/tasks/T121.md와 선행 실제 보고서·evidence를 읽어라.
T96 region-packages.json의 upper-limb primary-owner subset만 수행한다. 실행 전에 exact target IDs/버전/hash와 내부 최대10개 workUnits를 확인한다. T96 manifest가 없거나 누락/중복 owner가 있으면 임의 분류로 시작하지 않는다. 기존 geometry를 우선 재사용하여 각 target의 실제 object/side/part identity, 세 이름과 alias, typed card/검색/선택을 공통 adapter로 연결한다. source-only/held 승격은 항목별 증거가 있어야 한다. missing은 exact 실제 파일/객체 검사와 권리/frame 근거로 처리하며 다른 source family 정합이 필요하면 별도 의존 gate로 남겨 추정 통합하지 않는다. 이 package는 팔·손 구조 단계이며 기시정지 신규 집필·기능·모션은 후반 단계다. 전체 package를 완료하지 못하면 같은 ID와 nextUnit으로 재개하고 새 번호를 만들지 않는다. 기존 공통 도구를 재사용하고 부위별 엔진을 복제하지 않는다. 모든 필수 subset 결과·누락·최종 화면·성능을 기록한다. 이전 이 파일의 TA2순서10개 scope는 역사 계획이다.
기본 다음 ID: T80. 필수 미완이면 같은 ID로 재개하고 다음 단계로 자동 진행하지 마라.
소유 변경만 검증·로컬 커밋하고 해시·잔여 변경·다음 프롬프트를 남긴 뒤 멈춰라. push·배포 금지.
```

<a id="t80"></a>
### T80 — 전신 구조·선택 coverage 감사

담당: **Luna Max** · [최신 명세](../../work/tasks/T80.md)

```text
HUMAN ATLAS에서 T80만 수행해라. 담당 Luna Max.
design/2026-09-25-muscle-atlas/23-PROMPTS-AFTER-T95.md의 공통 실행 규칙과 이 ID 절,
22 효율화 설계, 최신 STATUS/R15 registry, work/tasks/T80.md와 선행 실제 보고서·evidence를 읽어라.
T96 확정 목록과 28개 구조 작업의 실제 결과를 대조한다. T122–T165는 폐기 계획이므로 선행 완료로 요구하지 않는다. 전체 필수 구조/세 이름/클릭/지역 접근/미해결 hold를 검사하고 누락이 있으면 pass하지 않는다.
기본 다음 ID: T58. 필수 미완이면 같은 ID로 재개하고 다음 단계로 자동 진행하지 마라.
소유 변경만 검증·로컬 커밋하고 해시·잔여 변경·다음 프롬프트를 남긴 뒤 멈춰라. push·배포 금지.
```

<a id="t58"></a>
### T58 — 전신 그래픽 재검증

담당: **Astra · 현재 대화 직접 구현** · [최신 명세](../../work/tasks/T58.md)

```text
HUMAN ATLAS에서 T58만 재개·검증해라. 담당 Astra · 현재 대화 직접 구현.
design/2026-09-25-muscle-atlas/23-PROMPTS-AFTER-T95.md의 공통 실행 규칙과 이 ID 절,
22 효율화 설계, 최신 STATUS/R15 registry, work/tasks/T58.md와 선행 실제 보고서·evidence를 읽어라.
기존 T58 WIP와 보고서를 보존하며 재개한다. 최신 통합 장면에서 그래픽/프레이밍/패널 가림/카메라 연속성/선택을 직접 검증·개선한다. 22 설계의 전후 성능, cold/warm 구분, 반복 전환과 실제 모바일 측정 여부를 기록한다. 로딩 로고·인체 그림·슬로건을 되살리지 않는다.
기본 다음 ID: T81. 필수 미완이면 같은 ID로 재개하고 다음 단계로 자동 진행하지 마라.
소유 변경만 검증·로컬 커밋하고 해시·잔여 변경·다음 프롬프트를 남긴 뒤 멈춰라. push·배포 금지.
```

<a id="t81"></a>
### T81 — 전체 기시·정지 조사·카드 연결

담당: **Luna Max** · [최신 명세](../../work/tasks/T81.md)

```text
HUMAN ATLAS에서 T81만 수행해라. 담당 Luna Max.
design/2026-09-25-muscle-atlas/23-PROMPTS-AFTER-T95.md의 공통 실행 규칙과 이 ID 절,
22 효율화 설계, 최신 STATUS/R15 registry, work/tasks/T81.md와 선행 실제 보고서·evidence를 읽어라.
전체 확정 근육의 기시정지 조사/근거 대조/learner 카드 연결을 지역 package와 최대10개 검증 workUnits로 진행한다. 갈래 차이와 비골성 부착을 구분하고 실제 3D 부착 좌표는 추정하지 않는다. 출처는 내부에 보존하며 기시정지 칸에 늘어놓지 않는다. 첫10개 후 새 번호를 발급하지 말고 같은 T81 progress manifest를 재개한다. 전체 완료 전 T82에 넘기지 않는다.
기본 다음 ID: T82. 필수 미완이면 같은 ID로 재개하고 다음 단계로 자동 진행하지 마라.
소유 변경만 검증·로컬 커밋하고 해시·잔여 변경·다음 프롬프트를 남긴 뒤 멈춰라. push·배포 금지.
```

<a id="t82"></a>
### T82 — 전신 기시·정지 프로토타입 합격

담당: **Luna Max** · [최신 명세](../../work/tasks/T82.md)

```text
HUMAN ATLAS에서 T82만 수행해라. 담당 Luna Max.
design/2026-09-25-muscle-atlas/23-PROMPTS-AFTER-T95.md의 공통 실행 규칙과 이 ID 절,
22 효율화 설계, 최신 STATUS/R15 registry, work/tasks/T82.md와 선행 실제 보고서·evidence를 읽어라.
전체 동결 근육의 기시정지/갈래/세 이름/카드 연결과 근거 충돌을 감사한다. 기존 placeholder를 조사 완료로 세지 않는다. 필수 내용 미완은 partial이며 해당 batch를 마무리한 뒤 다음 기능 단계로 간다. 사람 검토는 별도 사실이고 모든 기본 텍스트의 일괄 human approval을 기다리게 하지 않는다. 지식 prototype 완료와 정확한 부착 surface 완성은 구분한다.
기본 다음 ID: T83. 필수 미완이면 같은 ID로 재개하고 다음 단계로 자동 진행하지 마라.
소유 변경만 검증·로컬 커밋하고 해시·잔여 변경·다음 프롬프트를 남긴 뒤 멈춰라. push·배포 금지.
```

<a id="t83"></a>
### T83 — 전체 근육 기능 조사·카드 연결

담당: **Luna Max** · [최신 명세](../../work/tasks/T83.md)

```text
HUMAN ATLAS에서 T83만 수행해라. 담당 Luna Max.
design/2026-09-25-muscle-atlas/23-PROMPTS-AFTER-T95.md의 공통 실행 규칙과 이 ID 절,
22 효율화 설계, 최신 STATUS/R15 registry, work/tasks/T83.md와 선행 실제 보고서·evidence를 읽어라.
전체 확정 근육의 작용·움직이는 구조·고정 조건·갈래 차이를 근거로 조사하고 설명 카드에 연결한다. 비사지 근육을 관절회전으로 억지 표현하지 않는다. 지역 package/최대10개 workUnits로 같은 T83을 재개한다. 텍스트와 clip 지원을 구분하고 전체 설명 완료 전 T84로 넘기지 않는다.
기본 다음 ID: T84. 필수 미완이면 같은 ID로 재개하고 다음 단계로 자동 진행하지 마라.
소유 변경만 검증·로컬 커밋하고 해시·잔여 변경·다음 프롬프트를 남긴 뒤 멈춰라. push·배포 금지.
```

<a id="t84"></a>
### T84 — 전신 근육 기능 설명 합격

담당: **Luna Max** · [최신 명세](../../work/tasks/T84.md)

```text
HUMAN ATLAS에서 T84만 수행해라. 담당 Luna Max.
design/2026-09-25-muscle-atlas/23-PROMPTS-AFTER-T95.md의 공통 실행 규칙과 이 ID 절,
22 효율화 설계, 최신 STATUS/R15 registry, work/tasks/T84.md와 선행 실제 보고서·evidence를 읽어라.
전체 target의 기능 설명과 원문 근거/조건/갈래/기시정지와의 일관성을 대조한다. 누락된 근육이 있으면 부분 완료로 남기고 보완한다. animation이 없다고 기능 텍스트까지 미작성 상태로 두지 않고 설명을 먼저 완성한다. 통과 후 전신 animation 범위/작용군 계획 T35로 간다.
기본 다음 ID: T35. 필수 미완이면 같은 ID로 재개하고 다음 단계로 자동 진행하지 마라.
소유 변경만 검증·로컬 커밋하고 해시·잔여 변경·다음 프롬프트를 남긴 뒤 멈춰라. push·배포 금지.
```

<a id="t35"></a>
### T35 — 전신 근육 animation 목표와 제작 queue

담당: **Sol High** · [최신 명세](../../work/tasks/T35.md)

```text
HUMAN ATLAS에서 T35만 수행해라. 담당 Sol High.
design/2026-09-25-muscle-atlas/23-PROMPTS-AFTER-T95.md의 공통 실행 규칙과 이 ID 절,
22 효율화 설계, 최신 STATUS/R15 registry, work/tasks/T35.md와 선행 실제 보고서·evidence를 읽어라.
전체 확정 근육의 대표 움직임 target→작용/고정조건→변형 family→실제 model/clip 지원을 동결한다. 앞정강근과 소흉근 기존 단계를 유지하고 재사용 가능한 family를 묶는다. 설명/근육 선택별 검증은 생략하지 않는다. 22 설계에 따라 같은 검증 방식의 반복을 새 정수 task로 양산하지 않는다. 새로운 rig/좌표계 등 독립 기술 위험만 bounded 별도 작업으로 제안하고 전체 운동 gate 전에 필요한 미완을 명시한다. 이번에는 계획만 작성하고 clip 제작은 하지 않는다.
기본 다음 ID: T59. 필수 미완이면 같은 ID로 재개하고 다음 단계로 자동 진행하지 마라.
소유 변경만 검증·로컬 커밋하고 해시·잔여 변경·다음 프롬프트를 남긴 뒤 멈춰라. push·배포 금지.
```

<a id="t59"></a>
### T59 — 같은 앞정강근 표면의 교육용 수축 변형

담당: **Sol High** · [최신 명세](../../work/tasks/T59.md)

```text
HUMAN ATLAS에서 T59만 수행해라. 담당 Sol High.
design/2026-09-25-muscle-atlas/23-PROMPTS-AFTER-T95.md의 공통 실행 규칙과 이 ID 절,
22 효율화 설계, 최신 STATUS/R15 registry, work/tasks/T59.md와 선행 실제 보고서·evidence를 읽어라.
최신 검증된 전신 장면의 실제 앞정강근 표면/부착/발목 bone을 기준으로 한 수축·배측굴곡 사례를 skinning 또는 morph 등 검증 가능한 변형으로 제작한다. 원본과 source IDs/frame/rest pose를 보존한다. 기존 T55 표기만 보고 역사 패키지로 되돌리지 않는다. 주변 근육·뼈와 연결/관통/처음·중간·끝 자세를 검증하고 scale-only나 다른 모델로 대체하지 않는다.
기본 다음 ID: T60. 필수 미완이면 같은 ID로 재개하고 다음 단계로 자동 진행하지 마라.
소유 변경만 검증·로컬 커밋하고 해시·잔여 변경·다음 프롬프트를 남긴 뒤 멈춰라. push·배포 금지.
```

<a id="t60"></a>
### T60 — 동일 viewport에서 운동 재생 연결

담당: **Sol High** · [최신 명세](../../work/tasks/T60.md)

```text
HUMAN ATLAS에서 T60만 수행해라. 담당 Sol High.
design/2026-09-25-muscle-atlas/23-PROMPTS-AFTER-T95.md의 공통 실행 규칙과 이 ID 절,
22 효율화 설계, 최신 STATUS/R15 registry, work/tasks/T60.md와 선행 실제 보고서·evidence를 읽어라.
MotionLearningPanel의 독립 asset/mixer 소유를 AnatomySceneController 명령으로 연결한다. 실제 main renderer가 가진 T59 target node를 애니메이션하고 UI는 play/pause/seek/reset 명령과 상태만 가진다. 사용자 CTA 클릭 전에는 움직이지 않는다. 기존 camera/background/layers/selection을 snapshot해 보존하고 종료 시 pose/가시성만 정확히 복원한다.
기본 다음 ID: T25. 필수 미완이면 같은 ID로 재개하고 다음 단계로 자동 진행하지 마라.
소유 변경만 검증·로컬 커밋하고 해시·잔여 변경·다음 프롬프트를 남긴 뒤 멈춰라. push·배포 금지.
```

<a id="t25"></a>
### T25 — 같은 전신 모형의 앞정강근 제품 합격

담당: **Luna Max** · [최신 명세](../../work/tasks/T25.md)

```text
HUMAN ATLAS에서 T25만 수행해라. 담당 Luna Max.
design/2026-09-25-muscle-atlas/23-PROMPTS-AFTER-T95.md의 공통 실행 규칙과 이 ID 절,
22 효율화 설계, 최신 STATUS/R15 registry, work/tasks/T25.md와 선행 실제 보고서·evidence를 읽어라.
T42 공통 카드와 T24 실제 clip을 연결한다. 근육 선택→세 이름/기시·정지→눈에 보이는 '움직임으로 이해하기'→실제 몸 움직임→작용 설명을 연결한다. 클릭은 명시적 재생 요청으로 취급하되 reduced-motion은 정지 자세/수동 단계 선택을 기본으로 한다.

기능 탭 전환과 작용 선택을 동기화하고 pause/resume/처음 자세/느리게/진행 막대를 제공한다. camera reset과 pose reset을 분리한다. 모형 전환이 있으면 학습용 시범 모형임을 짧게 알린다.

선택/부위/탭 전환·로드 실패·unmount 시 loop·mixer·강조를 정리한다. CTA 클릭 전에는 자동 재생하지 않는다.
 T59/T60의 실제 같은 모형 mesh 변형을 main learner에서 검증한다. 별도 T24 bone/path 기술 후보는 pass 근거가 아니다. 전신 탐색→앞정강근→기시정지/기능→CTA→표면 수축과 발 움직임→복원을 시험한다. T24 역사 보고서는 blocked 그대로 보존하고 해결 증거를 새 보고서에 연결한다. 다음은 같은 전신 모형의 소흉근 사례 T27이며, 신경은 전신 근육 시범 gate T85 이후다.
기본 다음 ID: T27. 필수 미완이면 같은 ID로 재개하고 다음 단계로 자동 진행하지 마라.
소유 변경만 검증·로컬 커밋하고 해시·잔여 변경·다음 프롬프트를 남긴 뒤 멈춰라. push·배포 금지.
```

<a id="t27"></a>
### T27 — 소흉근 동일 모형 변형 준비

담당: **Sol High** · [최신 명세](../../work/tasks/T27.md)

```text
HUMAN ATLAS에서 T27만 수행해라. 담당 Sol High.
design/2026-09-25-muscle-atlas/23-PROMPTS-AFTER-T95.md의 공통 실행 규칙과 이 ID 절,
22 효율화 설계, 최신 STATUS/R15 registry, work/tasks/T27.md와 선행 실제 보고서·evidence를 읽어라.
전신 구조 단계에서 준비된 소흉근/흉곽/견갑대와 완료된 기능 설명을 재사용한다. rig/부착/주변 구조 변형 준비만 검증하고 필요할 때만 근거 있는 상세 자산을 보완한다. 다른 모델/고해상도 LOD가 있다고 가정하지 않는다. T28의 동일 모델 운동을 준비한다.
기본 다음 ID: T28. 필수 미완이면 같은 ID로 재개하고 다음 단계로 자동 진행하지 마라.
소유 변경만 검증·로컬 커밋하고 해시·잔여 변경·다음 프롬프트를 남긴 뒤 멈춰라. push·배포 금지.
```

<a id="t28"></a>
### T28 — 견갑대 운동 기반과 전인 시범 하나

담당: **Sol High** · [최신 명세](../../work/tasks/T28.md)

```text
HUMAN ATLAS에서 T28만 수행해라. 담당 Sol High.
design/2026-09-25-muscle-atlas/23-PROMPTS-AFTER-T95.md의 공통 실행 규칙과 이 ID 절,
22 효율화 설계, 최신 STATUS/R15 registry, work/tasks/T28.md와 선행 실제 보고서·evidence를 읽어라.
T81–84의 전신 내용 batch에서 확정한 조건의 소흉근 관련 견갑골 전인 시범 1개를 제작한다. 흉곽에 대한 견갑대의 이동/회전과 고정 조건을 모델링하고 T45/T46에서 재사용할 골격·경로 제작 도구를 만든다.

단일 임의 hinge 또는 상완골만 움직이는 것으로 견갑골 작용을 대신하지 않는다. 근육 endpoint/변형 또는 표시된 설명 경로를 함께 제공한다. T44의 좌표 정합 원칙을 재사용하되 발목 좌표를 복제하지 않는다.
기본 다음 ID: T45. 필수 미완이면 같은 ID로 재개하고 다음 단계로 자동 진행하지 마라.
소유 변경만 검증·로컬 커밋하고 해시·잔여 변경·다음 프롬프트를 남긴 뒤 멈춰라. push·배포 금지.
```

<a id="t45"></a>
### T45 — 소흉근 관련 견갑골 하강 시범

담당: **Sol High** · [최신 명세](../../work/tasks/T45.md)

```text
HUMAN ATLAS에서 T45만 수행해라. 담당 Sol High.
design/2026-09-25-muscle-atlas/23-PROMPTS-AFTER-T95.md의 공통 실행 규칙과 이 ID 절,
22 효율화 설계, 최신 STATUS/R15 registry, work/tasks/T45.md와 선행 실제 보고서·evidence를 읽어라.
T28 기반을 재사용해 T81–84의 전신 내용 batch에서 근거/조건이 확인된 하강 시범 clip1개를 만든다. 단순 전인 clip의 축값을 바꿔 해부학 근거 대신 쓰지 않는다. moving/fixed structures·근육 경로와 설명을 연결한다.
기본 다음 ID: T46. 필수 미완이면 같은 ID로 재개하고 다음 단계로 자동 진행하지 마라.
소유 변경만 검증·로컬 커밋하고 해시·잔여 변경·다음 프롬프트를 남긴 뒤 멈춰라. push·배포 금지.
```

<a id="t46"></a>
### T46 — 소흉근 관련 견갑골 하방회전 시범

담당: **Sol High** · [최신 명세](../../work/tasks/T46.md)

```text
HUMAN ATLAS에서 T46만 수행해라. 담당 Sol High.
design/2026-09-25-muscle-atlas/23-PROMPTS-AFTER-T95.md의 공통 실행 규칙과 이 ID 절,
22 효율화 설계, 최신 STATUS/R15 registry, work/tasks/T46.md와 선행 실제 보고서·evidence를 읽어라.
T28 기반으로 T81–84의 전신 내용 batch에서 근거/조건이 확인된 하방회전 시범 clip1개를 만든다. 회전 방향과 흉곽 정합을 검증하며 전인/하강과 작용 ID를 구분한다. 대표 시범을 생체 운동의 정량 재현으로 주장하지 않는다.
기본 다음 ID: T29. 필수 미완이면 같은 ID로 재개하고 다음 단계로 자동 진행하지 마라.
소유 변경만 검증·로컬 커밋하고 해시·잔여 변경·다음 프롬프트를 남긴 뒤 멈춰라. push·배포 금지.
```

<a id="t29"></a>
### T29 — 소흉근 구조·기능 사용자 흐름 통합

담당: **Luna Max** · [최신 명세](../../work/tasks/T29.md)

```text
HUMAN ATLAS에서 T29만 수행해라. 담당 Luna Max.
design/2026-09-25-muscle-atlas/23-PROMPTS-AFTER-T95.md의 공통 실행 규칙과 이 ID 절,
22 효율화 설계, 최신 STATUS/R15 registry, work/tasks/T29.md와 선행 실제 보고서·evidence를 읽어라.
소흉근 선택→주변 흐림→구조 설명→CTA→전인/하강/하방회전 작용 선택→해당 실제 clip과 설명으로 연결한다. 지원하지 않는 작용은 다른 clip으로 대체하지 않는다. 뼈 카드의 세 이름과 근육으로 돌아오는 흐름을 검증한다.
기본 다음 ID: T31. 필수 미완이면 같은 ID로 재개하고 다음 단계로 자동 진행하지 마라.
소유 변경만 검증·로컬 커밋하고 해시·잔여 변경·다음 프롬프트를 남긴 뒤 멈춰라. push·배포 금지.
```

<a id="t31"></a>
### T31 — 두 부위 구조·기능 파일럿 합격 검증

담당: **Luna Max** · [최신 명세](../../work/tasks/T31.md)

```text
HUMAN ATLAS에서 T31만 수행해라. 담당 Luna Max.
design/2026-09-25-muscle-atlas/23-PROMPTS-AFTER-T95.md의 공통 실행 규칙과 이 ID 절,
22 효율화 설계, 최신 STATUS/R15 registry, work/tasks/T31.md와 선행 실제 보고서·evidence를 읽어라.
종아리와 소흉근의 실제 data/scene/clip을 전체 사용자 흐름으로 검사한다. 세 이름·기시정지·뼈 카드·클릭·흐림·움직임·설명·복원을 함께 확인한다. 데이터 검증과 실제 화면 검증을 분리 기록한다.
기본 다음 ID: T66. 필수 미완이면 같은 ID로 재개하고 다음 단계로 자동 진행하지 마라.
소유 변경만 검증·로컬 커밋하고 해시·잔여 변경·다음 프롬프트를 남긴 뒤 멈춰라. push·배포 금지.
```

<a id="t66"></a>
### T66 — 첫 기능 확장 batch 하나

담당: **Luna Max** · [최신 명세](../../work/tasks/T66.md)

```text
HUMAN ATLAS에서 T66만 수행해라. 담당 Luna Max.
design/2026-09-25-muscle-atlas/23-PROMPTS-AFTER-T95.md의 공통 실행 규칙과 이 ID 절,
22 효율화 설계, 최신 STATUS/R15 registry, work/tasks/T66.md와 선행 실제 보고서·evidence를 읽어라.
T35에서 동결하고 T31 실제 사례로 검증한 action-family의 이번 bounded 작업만 수행한다. 검증된 rig의 clip1개 또는 공유 clip 연결 최대10관계라는 상한을 유지한다. 반복 가능한 후속 unit은 같은 manifest/ID로 재개하되 새 rig나 미등록 변형 family는 Luna 범위에 조용히 섞지 않는다. 전체 남은 운동 작업의 상태를 별도로 보존하고 첫 batch 하나로 T47/T85 진입 조건을 충족했다고 선언하지 않는다.
기본 다음 ID: T47. 필수 미완이면 같은 ID로 재개하고 다음 단계로 자동 진행하지 마라.
소유 변경만 검증·로컬 커밋하고 해시·잔여 변경·다음 프롬프트를 남긴 뒤 멈춰라. push·배포 금지.
```

<a id="t47"></a>
### T47 — 전신 구조·기능·운동 자료 감사

담당: **Luna Max** · [최신 명세](../../work/tasks/T47.md)

```text
HUMAN ATLAS에서 T47만 수행해라. 담당 Luna Max.
design/2026-09-25-muscle-atlas/23-PROMPTS-AFTER-T95.md의 공통 실행 규칙과 이 ID 절,
22 효율화 설계, 최신 STATUS/R15 registry, work/tasks/T47.md와 선행 실제 보고서·evidence를 읽어라.
전체 확정 근육의 구조/기시정지/기능/대표 motion을 실제 data/asset/binding으로 감사한다. T66 한 batch 완료를 전체 운동 완료로 세지 않는다. 누락을 같은 미완 package 또는 구체적 독립 위험에 연결하고 모든 필수 motion 완료 전 T85 합격을 예고하지 않는다.
기본 다음 ID: T85. 필수 미완이면 같은 ID로 재개하고 다음 단계로 자동 진행하지 마라.
소유 변경만 검증·로컬 커밋하고 해시·잔여 변경·다음 프롬프트를 남긴 뒤 멈춰라. push·배포 금지.
```

<a id="t85"></a>
### T85 — 모든 근육 움직임 학습 coverage 합격

담당: **Astra · 현재 대화 직접 구현** · [최신 명세](../../work/tasks/T85.md)

```text
HUMAN ATLAS에서 T85만 수행해라. 담당 Astra · 현재 대화 직접 구현.
design/2026-09-25-muscle-atlas/23-PROMPTS-AFTER-T95.md의 공통 실행 규칙과 이 ID 절,
22 효율화 설계, 최신 STATUS/R15 registry, work/tasks/T85.md와 선행 실제 보고서·evidence를 읽어라.
T78/T35의 모든 근육 target이 기시정지·기능 설명과 실제 같은 model surface 시범 최소1개를 갖는지 검사한다. 전신→근육→움직임으로 이해하기→수축/관련 신체 운동→복원을 실제 scene에서 검증한다. scale-only/뼈만/다른 viewer/근육 숨김 대체는 실패다. 주변 구조의 수동 변형과 부착·관통·camera/layer/선택 연속성, 설명 동기를 확인한다. 미지원 근육/형상이 남으면 partial이며 신경 단계로 자동 진입하지 않는다. 모든 가능한 작용/정량 생리 시뮬레이션 완료로 과장하지 않는다.
기본 다음 ID: T61. 필수 미완이면 같은 ID로 재개하고 다음 단계로 자동 진행하지 마라.
소유 변경만 검증·로컬 커밋하고 해시·잔여 변경·다음 프롬프트를 남긴 뒤 멈춰라. push·배포 금지.
```

<a id="t61"></a>
### T61 — 신경 레이어·선택·관계 데이터 계약

담당: **Sol High** · [최신 명세](../../work/tasks/T61.md)

```text
HUMAN ATLAS에서 T61만 수행해라. 담당 Sol High.
design/2026-09-25-muscle-atlas/23-PROMPTS-AFTER-T95.md의 공통 실행 규칙과 이 ID 절,
22 효율화 설계, 최신 STATUS/R15 registry, work/tasks/T61.md와 선행 실제 보고서·evidence를 읽어라.
전신 근육 기능/animation 합격 후 신경의 typed selection, branch graph, 다중 지배근 관계, source/frame/pose/registration, 레이어와 카드 계약만 구현한다. 전신 조사/3D는 T86 이후다. 같은 scene에 확장하며 감각분포·피부분절·경락을 혼합하지 않는다.
기본 다음 ID: T86. 필수 미완이면 같은 ID로 재개하고 다음 단계로 자동 진행하지 마라.
소유 변경만 검증·로컬 커밋하고 해시·잔여 변경·다음 프롬프트를 남긴 뒤 멈춰라. push·배포 금지.
```

<a id="t86"></a>
### T86 — 전신 신경 목표·복수 원문 모델 조사

담당: **Sol High** · [최신 명세](../../work/tasks/T86.md)

```text
HUMAN ATLAS에서 T86만 수행해라. 담당 Sol High.
design/2026-09-25-muscle-atlas/23-PROMPTS-AFTER-T95.md의 공통 실행 규칙과 이 ID 절,
22 효율화 설계, 최신 STATUS/R15 registry, work/tasks/T86.md와 선행 실제 보고서·evidence를 읽어라.
전신 신경의 유한한 목표 범위와 포함/제외 기준을 확정하고 복수 공식/원문 모델의 identity/분지/좌우/주행/지배/감각/pose/frame/권리를 비교한다. 이름 없는 미세 말단까지 완료라고 위장하지 않는다. 조사 package와 최대10개 검증 unit을 manifest로 고정하고 T62/T87에 연결한다.10개마다 새 정수 ID를 발급하지 않는다. 자료를 눈대중으로 포개거나 평균해 실제 주행을 만들지 않는다.
기본 다음 ID: T62. 필수 미완이면 같은 ID로 재개하고 다음 단계로 자동 진행하지 마라.
소유 변경만 검증·로컬 커밋하고 해시·잔여 변경·다음 프롬프트를 남긴 뒤 멈춰라. push·배포 금지.
```

<a id="t62"></a>
### T62 — 첫 하지 신경 자료 패키지

담당: **Luna Max** · [최신 명세](../../work/tasks/T62.md)

```text
HUMAN ATLAS에서 T62만 수행해라. 담당 Luna Max.
design/2026-09-25-muscle-atlas/23-PROMPTS-AFTER-T95.md의 공통 실행 규칙과 이 ID 절,
22 효율화 설계, 최신 STATUS/R15 registry, work/tasks/T62.md와 선행 실제 보고서·evidence를 읽어라.
T86 전신 조사 queue의 첫 하지 신경 trunk1개/branch최대2개 자료를 조사한다. 기존 명세의 상세 근거·검증은 유지하고 이 pilot 하나로 전체 신경 조사 완료를 선언하지 않는다. 다음 T87과 나머지 전체 조사 batch다.
기본 다음 ID: T87. 필수 미완이면 같은 ID로 재개하고 다음 단계로 자동 진행하지 마라.
소유 변경만 검증·로컬 커밋하고 해시·잔여 변경·다음 프롬프트를 남긴 뒤 멈춰라. push·배포 금지.
```

<a id="t87"></a>
### T87 — 전체 신경 조사 package 확장

담당: **Luna Max** · [최신 명세](../../work/tasks/T87.md)

```text
HUMAN ATLAS에서 T87만 수행해라. 담당 Luna Max.
design/2026-09-25-muscle-atlas/23-PROMPTS-AFTER-T95.md의 공통 실행 규칙과 이 ID 절,
22 효율화 설계, 최신 STATUS/R15 registry, work/tasks/T87.md와 선행 실제 보고서·evidence를 읽어라.
T86이 동결한 전체 신경 조사 package를 T62 결과부터 이어서 검증한다. 이름/분지/좌우/주행/지배근/감각/원문 차이를 최대10개씩 조사하고 같은 T87 manifest를 재개한다. 모든 필수 조사 미완을 해결하기 전 T88 통합 gate로 넘기지 않는다. 새 geometry나 임상 추천을 이번에 만들지 않는다.
기본 다음 ID: T88. 필수 미완이면 같은 ID로 재개하고 다음 단계로 자동 진행하지 마라.
소유 변경만 검증·로컬 커밋하고 해시·잔여 변경·다음 프롬프트를 남긴 뒤 멈춰라. push·배포 금지.
```

<a id="t88"></a>
### T88 — 전신 신경 자료 통합·등록 검증

담당: **Sol High** · [최신 명세](../../work/tasks/T88.md)

```text
HUMAN ATLAS에서 T88만 수행해라. 담당 Sol High.
design/2026-09-25-muscle-atlas/23-PROMPTS-AFTER-T95.md의 공통 실행 규칙과 이 ID 절,
22 효율화 설계, 최신 STATUS/R15 registry, work/tasks/T88.md와 선행 실제 보고서·evidence를 읽어라.
전체 target의 조사 결과를 공통 graph에 통합하고 중복/동의어/좌우/branch/지배근 mapping/출처 차이를 검증한다. 모델별 registration과 변형/pose 차이에 대한 정량 기준을 명시한다. registration이 필요한 경우 작은 별도 기술 task를 T63 앞에 넣는다. 실제 source surface/path가 없으면 두 endpoint 직선으로 대체하지 않는다. 충분한 조사/통합이 끝난 뒤에만 3D 구현 단계로 이동한다.
기본 다음 ID: T63. 필수 미완이면 같은 ID로 재개하고 다음 단계로 자동 진행하지 마라.
소유 변경만 검증·로컬 커밋하고 해시·잔여 변경·다음 프롬프트를 남긴 뒤 멈춰라. push·배포 금지.
```

<a id="t63"></a>
### T63 — 첫 신경 3D 주행과 지배근 강조

담당: **Sol High** · [최신 명세](../../work/tasks/T63.md)

```text
HUMAN ATLAS에서 T63만 수행해라. 담당 Sol High.
design/2026-09-25-muscle-atlas/23-PROMPTS-AFTER-T95.md의 공통 실행 규칙과 이 ID 절,
22 효율화 설계, 최신 STATUS/R15 registry, work/tasks/T63.md와 선행 실제 보고서·evidence를 읽어라.
전체 신경 조사·통합 후 첫 검증된 신경 주행을 같은 scene에 구현한다. 원래 명세의 실제 주행/좌표/pose 검증을 유지한다. 클릭 시 근거 있는 지배근을 강조하고 다른 근육을 흐리며 복원 가능하게 한다. 신경 기본 설명 카드와 세 이름을 연결한다. 다음 나머지 전신 nerve 3D batch이며 포착 설명을 먼저 구현하지 않는다.
기본 다음 ID: T89. 필수 미완이면 같은 ID로 재개하고 다음 단계로 자동 진행하지 마라.
소유 변경만 검증·로컬 커밋하고 해시·잔여 변경·다음 프롬프트를 남긴 뒤 멈춰라. push·배포 금지.
```

<a id="t89"></a>
### T89 — 전체 신경3D package 확장

담당: **Luna Max** · [최신 명세](../../work/tasks/T89.md)

```text
HUMAN ATLAS에서 T89만 수행해라. 담당 Luna Max.
design/2026-09-25-muscle-atlas/23-PROMPTS-AFTER-T95.md의 공통 실행 규칙과 이 ID 절,
22 효율화 설계, 최신 STATUS/R15 registry, work/tasks/T89.md와 선행 실제 보고서·evidence를 읽어라.
T88/T63에서 검증한 adapter로 동결된 다음 nerve trunk/제한된 branch package의 실제 주행과 지배근 강조를 같은 scene에 연결한다. 같은 T89의 내부 package로 재개하며 매 package마다 새 정수 ID를 만들지 않는다. 새 정합/rig 위험은 근거와 bounded 범위를 제시하고 추정 통합하지 않는다. 전체 필수 신경3D 미완이면 T90으로 자동 넘기지 않는다.
기본 다음 ID: T90. 필수 미완이면 같은 ID로 재개하고 다음 단계로 자동 진행하지 마라.
소유 변경만 검증·로컬 커밋하고 해시·잔여 변경·다음 프롬프트를 남긴 뒤 멈춰라. push·배포 금지.
```

<a id="t90"></a>
### T90 — 전신 신경 주행·지배근 그래픽 합격

담당: **Astra · 현재 대화 직접 구현** · [최신 명세](../../work/tasks/T90.md)

```text
HUMAN ATLAS에서 T90만 수행해라. 담당 Astra · 현재 대화 직접 구현.
design/2026-09-25-muscle-atlas/23-PROMPTS-AFTER-T95.md의 공통 실행 규칙과 이 ID 절,
22 효율화 설계, 최신 STATUS/R15 registry, work/tasks/T90.md와 선행 실제 보고서·evidence를 읽어라.
동결 신경 target의 실제 주행/선택/지배근 강조/카드/복원/pose를 전수 데이터 감사하고 region별 화면을 검증한다. 모든 muscle motion 중 정적 신경을 잘못 고정해 표시하지 않는다. pose 지원이 없으면 사용자에게 명확히 알리고 rest pose 탐색으로 복원한다. 자료 부족을 전신 완료로 세지 않는다. 신경 기본 설명과 그래픽 통합이 합격한 뒤 T64/T91 포착·기능이상 내용으로 간다.
기본 다음 ID: T64. 필수 미완이면 같은 ID로 재개하고 다음 단계로 자동 진행하지 마라.
소유 변경만 검증·로컬 커밋하고 해시·잔여 변경·다음 프롬프트를 남긴 뒤 멈춰라. push·배포 금지.
```

<a id="t64"></a>
### T64 — 신경 포착·기능 변화의 접힌 설명 UI

담당: **Luna Max** · [최신 명세](../../work/tasks/T64.md)

```text
HUMAN ATLAS에서 T64만 수행해라. 담당 Luna Max.
design/2026-09-25-muscle-atlas/23-PROMPTS-AFTER-T95.md의 공통 실행 규칙과 이 ID 절,
22 효율화 설계, 최신 STATUS/R15 registry, work/tasks/T64.md와 선행 실제 보고서·evidence를 읽어라.
신경 3D와 지배근 그래픽 완성 후 첫 trunk1/branch≤2의 포착 가능 구간과 병변 수준별 기능 변화 설명을 실제 근거로 작성한다. 처음부터 모든 정보를 펼치지 않는다. T91/후속 batch로 전신 내용 범위를 확장하고 치료/자침 추천은 넣지 않는다.
기본 다음 ID: T91. 필수 미완이면 같은 ID로 재개하고 다음 단계로 자동 진행하지 마라.
소유 변경만 검증·로컬 커밋하고 해시·잔여 변경·다음 프롬프트를 남긴 뒤 멈춰라. push·배포 금지.
```

<a id="t91"></a>
### T91 — 신경 포착·기능이상 설명 package 확장

담당: **Luna Max** · [최신 명세](../../work/tasks/T91.md)

```text
HUMAN ATLAS에서 T91만 수행해라. 담당 Luna Max.
design/2026-09-25-muscle-atlas/23-PROMPTS-AFTER-T95.md의 공통 실행 규칙과 이 ID 절,
22 효율화 설계, 최신 STATUS/R15 registry, work/tasks/T91.md와 선행 실제 보고서·evidence를 읽어라.
확정 신경 범위의 근거 있는 포착 구간/병변 수준별 운동·감각 기능 변화 설명을 최대10개 검증 unit으로 조사·연결한다. 같은 T91 manifest로 이어가고 새 batch 번호를 자동 발급하지 않는다. 모든 신경에 알려진 포착점이 있다고 가정하지 않는다. 근거 없음과 미조사를 구분하고 설명은 접힌 UI에 둔다. 환자 진단/자침점·깊이·치료 추천은 만들지 않는다.
기본 다음 ID: T65. 필수 미완이면 같은 ID로 재개하고 다음 단계로 자동 진행하지 마라.
소유 변경만 검증·로컬 커밋하고 해시·잔여 변경·다음 프롬프트를 남긴 뒤 멈춰라. push·배포 금지.
```

<a id="t65"></a>
### T65 — 전신 근육·신경·기능이상 설명 최종 통합 검증

담당: **Luna Max** · [최신 명세](../../work/tasks/T65.md)

```text
HUMAN ATLAS에서 T65만 수행해라. 담당 Luna Max.
design/2026-09-25-muscle-atlas/23-PROMPTS-AFTER-T95.md의 공통 실행 규칙과 이 ID 절,
22 효율화 설계, 최신 STATUS/R15 registry, work/tasks/T65.md와 선행 실제 보고서·evidence를 읽어라.
동결한 전신 근육 구조/기시정지/기능/대표 움직임과 전신 신경 조사/주행/지배근/포착·수준별 설명의 연결을 통합 감사한다. coverage 수치와 실제 지역별 화면을 모두 검증한다. 미해결/근거 없음은 정확히 표시하고 전신 완료로 과장하지 않는다. 평가/경혈/치료 기능은 별도 보류한다.
기본 다음 ID: T40. 필수 미완이면 같은 ID로 재개하고 다음 단계로 자동 진행하지 마라.
소유 변경만 검증·로컬 커밋하고 해시·잔여 변경·다음 프롬프트를 남긴 뒤 멈춰라. push·배포 금지.
```

<a id="t40"></a>
### T40 — 구조·기능 로컬 전달과 Git 체크포인트

담당: **Luna Max** · [최신 명세](../../work/tasks/T40.md)

```text
HUMAN ATLAS에서 T40만 수행해라. 담당 Luna Max.
design/2026-09-25-muscle-atlas/23-PROMPTS-AFTER-T95.md의 공통 실행 규칙과 이 ID 절,
22 효율화 설계, 최신 STATUS/R15 registry, work/tasks/T40.md와 선행 실제 보고서·evidence를 읽어라.
T65 최종 통합 및 T47/T85/T90 실제 결과를 기준으로 설치/실행/자료 추가/검증/복구·로컬 전달 안내와 재현 가능한 빌드/체크포인트를 만든다. 공개 권리가 보류된 원본을 배포 파일에 포함하지 않는다. 지원/미지원과 필수 gap을 정확히 적으며 평가/경혈을 임의 구현하지 않는다. 다음은 사용자 요청 대기, push·배포는 하지 않는다.
기본 다음 ID: 없음 — 사용자 후속 요청 대기. 필수 미완이면 같은 ID로 재개하고 다음 단계로 자동 진행하지 마라.
소유 변경만 검증·로컬 커밋하고 해시·잔여 변경·다음 프롬프트를 남긴 뒤 멈춰라. push·배포 금지.
```

## 여기서 수행하지 않는 범위

T67/T36/T37/T48/T49/T38의 평가 애니메이션과 T68의 경혈/경락·중재 설계는 별도 후속 요청이다. 이번 목록은 이를 포함한 모든 미래 기능 완성 약속이 아니다.
