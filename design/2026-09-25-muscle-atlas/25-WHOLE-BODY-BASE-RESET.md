# 전신 베이스 우선 재설계와 단일 실행 기준

2026-09-28 · Astra · 사용자 요청에 따른 설계 정정. 이 문서는 전신 모델 구현 완료가 아니다.

**현재 실행 순서와 상태의 유일한 원본은 `work/EXECUTION.json`이다.** `work/NEXT.md`, STATUS의 generated execution 블록, 23 프롬프트의 실행 목록은 `work/tools/sync_execution.py`로 생성한다. R15 registry는 호환용 투영이며 더 이상 독립 순서를 편집하지 않는다. 역사 evidence/과거 handoff는 당시 기록이다. 이 문서가 충돌하는 19–24의 구조 확보 순서·task 분할·신경/운동 선후 조건보다 우선한다. 24의 엑셀 검증·한글 기능·짧은 신경·표정근 motion 제외와 원본/권리 보존은 유지한다.

## 1. 이전 설계의 문제와 보존할 것

이전 설계는 소규모 취득의 안전성을 전신 제품의 개발 단위로 사용했다. 10개 파일 검증은 유용하지만 이를 각각의 취득 스크립트·TypeScript extension·parent hash 체인·사용자 프롬프트로 만드는 것은 전신 모델 확장에 비효율적이다. T166을 먼저 수행해도 관찰 UI가 추가될 뿐 전신 형상/이름/선택이 완성되지 않는다. T98–100을 광배근 하나에만 쓰고 12부위 연결을 뒤로 미룬 것도 전신 우선 목표와 맞지 않았다. 이 문제는 모델의 코딩 실력만으로 설명할 수 없으며 작업을 쪼갠 설계와 합격 지표의 문제다.

현재 재사용할 기반은 단일 AnatomySceneRoot/renderer/camera, 부위 다중 선택, 공통 카드/검색, 취득 취소·늦은 응답 해제·동시성2, 입력 hash와 원본 보존이다. 이를 버리거나 새 프레임워크로 재작성하지 않는다.

실제 코드를 조사한 결과:

| 항목 | 확인 | 판단/수정 책임 |
|---|---|---|
| task별 source extension | T101–104 전용 TS가 80/91/93/103행. plugin이 각각 import하고 이전 task 체인을 검증 | 공통 `DatasetManifest`와 generic compiler/loader로 전환(T99). task ID는 provenance로만 저장 |
| 취득/변환 복제 | T101/T102 acquire 파일 line similarity 94.7%, build 81.4% | source adapter별 공통 CLI + 데이터 manifest. 역사 스크립트 삭제 없이 현행 경로에서 분리 |
| 요청 비용 | GLB 요청마다 12개 manifest 파일을 다시 읽고 parse/hash 및 extension 합성을 반복 | 데이터셋 revision당 한 번 검증/compile, 변경 때 무효화. 검증 생략이나 history hash 덮어쓰기 금지 |
| frame/ID 결합 | 현재 contract가 BP3D node prefix, frame, LOD1에 고정 | 새 versioned contract에서 source namespace와 source→project transform/pose를 명시. 기존 ID를 재사용해 다른 형상으로 바꾸지 않음 |
| 메모리 | ResourceQueue.loaded는 scene 종료까지 보유; byte eviction 없음 | 전신 overview 고정 예산 + 상세 LRU/byte budget, 선택/현재 부위 pin, 비활성 상세 해제(T99) |
| raycast | root 전체 검사 후 첫 visible hit가 learner binding 없으면 선택 불가 | 표시 적격 표면 관찰과 검증된 학습 개념 선택 분리(T100). 카메라/hold 보존 |
| 성능 근거 | T104 후속 evidence도 warm 비교/RAF 간격이다. cold load·실제 draw 비용과 다름 | cold/warm, 실제 render 시간, 활성/정적 상태, 비교 조건을 따로 기록(T58). RAF만으로 60fps 제품 합격 금지 |

이번 offline 합산: 36 chunks, 593 nodes(기본 표시581), canonical 연결 node10, GLB 71,065,840 bytes, 전체 source triangles2,800,004. 이 수는 현재 보이는 삼각형/실제 draw calls/GPU 메모리와 다르다. 캐시 OBJ는 현재625개로 과거621과 다르며 coverage 분모가 아니다. 기존 dist의 App JS는 약1.20MB(압축 전 관찰값)다. task extension은 Vite 서버에서 쓰이므로 그 복제를 곧바로 브라우저 JS 증가량으로 계산하지 않는다. 검사23/23과 typecheck는 통과했지만 오류 없음/전신/모바일 합격은 아니다.

## 2. 새 목표와 실행 단위 — 새 번호 없음

첫 목표 G1: **정의된 전신 뼈·근육 목록을 같은 모형에서 보고 선택·검색·관찰할 수 있다.** 얼굴, 이두·삼두·삼각·광배근, 양측 견갑골, 요추·엉치뼈를 포함한다. 이후 기시·정지·작용/신경 정보를 붙이고, 근육 애니메이션은 그 다음이다. 공개 배포/환자 판단/치료/자침은 제외한다.

| 기존 ID를 재사용 | 지금부터의 산출물 | 담당 |
|---|---|---|
| T98 | **전신 source inventory + 실제 변환 가능성 검증 + 전신 base 선택** | Luna Max |
| T99 | **source별 공통 일괄 변환/검증/compiler와 가벼운 runtime 로딩 경로** | Sol High |
| T100 | **전신 bones/muscles 실물 통합 + 12부위/좌우/세 이름·선택 + 핵심 관찰 도구** | Luna Max |
| T80 | **전신 필수 구조 전수 누락·중복·선택 감사와 해당 데이터 결함 보완** | Luna Max |
| T58 | **전신 그래픽·미니멀 UX·실측 성능 최종 합격** | Astra 현재 대화 |

T105–109, T110–121, T166은 독립 실행 queue에서 제거하고 필요한 일을 위 task의 입력/내부 work-unit으로 흡수한다. 완료 처리나 삭제가 아니다. 정확한 흡수 대응은 EXECUTION의 `absorbedTasks`에 보존한다. T122–165는 기존대로 superseded_not_executed. 광배근만 별도 정합하는 옛 T98–100 프롬프트를 실행하지 않는다.

T98의 세부 source별 항목 수에 따라 자동 내부 unit을 나누며, T99는 공통 엔진, T100은 같은 엔진으로 전체 frozen dataset을 처리한다. **큰 monolithic 코드 한 번 작성**이라는 뜻이 아니다. 실패한 object/unit만 격리·재개한다. 모든 필수 unit이 끝나기 전 전체 task를 완료 처리하지 않는다. 같은 변환 방식을 10개씩 실행해도 번호는 늘리지 않는다. 실제 중간 산출물과 progress/checkpoint는 같은 ID 안에 기록한다.

G1 이후: T81→T82→T83→T84(전체 설명과 검증된 짧은 운동신경), 기존 신경 queue(T61부터 T65), 기존 motion queue(T35부터 T85), T40 전달. **신경 시작을 전 근육 애니메이션 합격 뒤로 묶은 이전 규칙은 폐기**한다. 초기 source inventory에 신경·내장기도 포함하되 G1 runtime에는 bones/muscles만 필수이고 신경·내장기를 몰래 다운로드/활성화하지 않는다. 내장기 학습·기능 UI는 별도 요청 전 범위 밖이다.

## 3. T98 — 먼저 전신 베이스를 결정

입력은 T97의 pinned archive/Startup.blend/hash와 BP3D 공식 metadata/실제 cache, T96의542개 의미 분류 target, 기존 runtime/hold, T104까지 실제 산출물이다. 원본은 읽기 전용. 이미 가진 archive를 다시 받지 않는다. T104 완료는 사용자 보고와 파일 증거 상태를 구분하고, 아직 report/commit이 없다면 해당 WIP를 무시하거나 T104 완료 보고서를 대신 쓰지 않는다. T98의 독립 source 검토는 진행할 수 있다.

### 전수 인벤토리와 target 대조

`sourceRelease + archive/member hash + sourceObjectLocator`를 key로 모든 Object를 inventory한다. object instance, 공유 Mesh datablock, curve/nerve, group/collection, label/helper, insertion patch, inactive representation을 구분한다. 이름/좌우 suffix 하나만으로 같은 해부 구조/좌우 확정이라 하지 않는다. Z-Anatomy의7,184 Objects/2,910 Mesh는 근육 개수가 아니다. object/parent/collection 경로·source transform·modifier/instance 여부·시스템·원문 label/외부ID를 보존한다.

BP3D와 Z-Anatomy의 중복은 동일 object/hash, 원래 source ID/계층, 정확한 외부 concept, 검증된 geometry 관계 순으로 대조한다. 이름 유사성은 후보일 뿐이다. 같은 mesh datablock을 쓰는 양측 object는 서로 다른 instance일 수 있어 하나를 버리지 않는다. 전체 근육과 insertion patch, group과 부분도 하나의 근육 수로 더하지 않는다.

status는 한 문자열로 뭉치지 않는다: `acquisition`, `conversion`, `identity`, `localUseRights`, `redistributionRights`, `framePose`, `defaultVisibility`, `inspectionEligibility`, `learnerBinding`, `humanReview`. source만 있음/변환 성공/학습 가능/권리 보류를 독립 집계한다.

T96 target 목록을 원본 그대로 참조하고 named muscle/part/group/bone/serial family/side-instance의 필수 분모를 의미에 맞게 versioned supplement로 동결한다. 확정하지 못한 개별 개수는 null로 둔다. 모든542개 target은 적용·group→member 연결·변이·중복 alias·미확보 중 하나로 설명되어야 하며, 소스에 없다고 필수 근육을 제외하지 않는다. 표정근·손 intrinsic·골반바닥·심부근·양측 뼈는 이름만 있는 항목까지 적극 대조한다.

### 실제 변환 가능성 시험과 중단 조건

먼저 **한 단위, 8–12개 실제 object**를 exact locator로 동결한다. 얼굴 표정근, 광배근, 상지/하지 근육, 양측 견갑골, 요추/엉치뼈 등 서로 다른 형태/위치를 포함한다. 이는 구현 범위를12개로 줄이는 것이 아니라 공통 변환 경로의 대표 시험이다. source instance/shared mesh/negative scale/modifier/constraint가 있는 경우를 포함한다.

T97에서 Blender3.5.0/3.5.1/5.2.2가 Metal 초기화 중 실패한 사실을 재사용한다. 새 근거 없는 버전 변경 반복은 하지 않는다. 공식 headless/background 경로를 한 번 근거 있게 시험하거나 신뢰할 수 있는 upstream export를 확인한다. 원시 BHead 배열 추출은 **그 배열이 evaluated surface를 충실히 재현한다는 검증이 있는 subset**에서만 허용한다. modifier/constraint/instance 결과를 빠뜨린 전신을 export 성공이라 하지 않는다. exporter 부재는 source 부족과 다른 blocker다. 검증된 실행 환경이 없으면 필요한 다른 환경/공식 export를 구체적으로 남기고 같은 T98에서 중단한다. 새 검색 task를 계속 발급하지 않는다.

출력은 실제 static preview/triangle/node/hash, transform 적용 여부, normals/negative determinant, 좌우/pose/부착 주변의 대응이다. 임의 autoexec/addon/driver 실행으로 해결하지 않는다. 웹 앱 변경은 하지 않는다.

### 베이스 선택

**Z-Anatomy를 우선 후보로 조사하지만 지금 채택을 확정하지 않는다.** 전신 포괄성·변환 충실도·좌우/pose·권리 출처·렌더 비용을 비교한 뒤 하나의 주 베이스를 선택한다. 이미 같은 source의 일관된 전신 자세가 있으면 그것을 전체 source→project 변환으로 사용한다. 수백 개 근육을 BP3D에 개별 fitting하는 것을 기본 경로로 삼지 않는다. BP3D/기타 source는 실제 빠진 구조만 보완하며 그 교차 source 관계는 따로 검증한다. 두 전신 모델을 겹쳐놓고 둘 다 기본 표시하지 않는다.

Z-Anatomy 원문은 BodyParts3D 파생 및 CC BY-SA4.0 안내와 함께 내이·신장 등 별도 구성 권리도 명시한다. [pinned README](https://github.com/Z-Anatomy/Models-of-human-anatomy/blob/c7010a903b75a2fd24a13b1c2c4c3546a9223780/Readme.md). 파일마다 동일 라이선스 조사를 복사하지 말고 문서로 입증된 **source family/collection 상속 + 예외**를 한 번 만든다. 각 object는 어느 근거를 상속하는지 기록한다. 일치하지 않는 외부 구성은 별도 held, 한 예외 때문에 독립된 전체 근육까지 일괄 보류하지 않는다. 일반 README만으로 예외 mesh의 공개 권리를 승인하지 않는다. 공개 재배포 hold와 허용되는 로컬 검토를 분리한다.

합격: 전수 inventory/reconciliation/rights groups와 **실제로 재현되는 exporter spike**, 선택된 base의 근거, 잔여 exact gaps, 전체 manifest 입력 hash가 있어야 한다. 이름 목록만으로 T99에 넘기지 않는다.

## 4. T99 — 일괄 처리와 runtime의 경량화

단일 거대 GLB 하나를 만들거나 작업 번호마다 별도 loader를 복제하지 않는다. `source adapter → normalized inventory → validation/identity overlays → dataset compiler → overview/detail chunks + compact catalog` 경로 하나를 만든다. BodyParts3D와 Z-Anatomy 파서는 별개지만 결과 schema/compiler/renderer는 공통이다. Blender/Python·원자료·권리 판정·hash lineage는 오프라인에 두고 웹 요청 중 source 조사/전체 history 검증을 하지 않는다.

최소 계약:

- `datasetId/revision`, `sourceRelease/hash`, opaque `objectId`, `geometryResourceId`, `instanceTransform`, `sourceFrame/unit/restPose`, 검증된 `projectTransform`, `kind/system`, `primaryRegion/regionIds`, `side`, exact `conceptIds`와 mapping status.
- `renderEligibility`, `inspectionEligibility`, `learnerBinding` 분리. 이름만 확인된 후보를 학습 선택으로 승격하지 않는다. 원문 검토와 human review는 별도이며 모든 기본 이름을 사람이 승인할 때까지 앱 전체를 막지 않는다.
- `source namespace`는 BP3D와 Z-Anatomy를 구분한다. 기존 HA stable concept ID/원본 source ID/hash와 역사 데이터는 유지. dataset 교체를 old mesh ID에 새 geometry를 덮어쓰는 방식으로 하지 않는다.
- `chunk/LOD/error bounds/byte estimate` 및 선택 ID 대응. 공유 mesh resource는 재사용하되 identity/side/instance와 disposal 참조 수를 보존한다. 같은 구조가 여러 지역에 있어도 scene node를 복제하지 않는다.

전체 dataset은 한 source snapshot에서 일괄 compile하되 운영은 chunk와 재개 manifest로 한다. 검증 결과를 snapshot/tool-version/hash에 묶어 재사용한다. 새로운10개마다 runtime 코드0줄이 목표다. 새 pipeline은 현재 검증된 BP3D subset을 그대로 재현하는 회귀부터 통과시킨 뒤 T98 전신 snapshot을 처리한다. T101–104의 결과/evidence는 유지하고 기존 task-specific entrypoints는 역사 재현용으로 남긴다. 전환 후 live plugin은 generic manifest 하나와 검증된 chunk index만 읽는다.

신경/내장 inventory는 schema가 보존하지만 bones/muscles runtime manifest에 넣지 않는다. nerve curves를 임의 굵기의 muscle triangle로 바꾸거나 source-only 신경을 임상 지배 관계로 추정하지 않는다. 후속 신경 adapter는 같은 source namespace/좌표를 재사용한다.

### 성능 합격 기준

- **전신 overview + 선택 부위 detail** 두 단계. overview도 필수 표면을 빼서 가볍게 만들지 않는다. source에서 재현 가능한 decimation/검증 LOD를 사용하고 node/개념 선택은 유지한다. 상세 요청 시 같은 camera/identity로 교체하며 이전 응답 취소/늦은 완료를 처리한다.
- 첫 검토 예산: overview 합계 전송20MiB 이내, active triangle1M 이내, CPU geometry buffer96MiB 이내, detail chunk8MiB 이내. 이는 현재 실측 합격값이 아니라 새 목표다. T98 비용 예측과 T58 실기기 근거 없이 상향하지 않는다. 품질/예산 중 하나가 실패하면 둘 다 미달로 기록한다.
- `ResourceQueue`에 source bytes/decoded geometry bytes 기준 budget과 LRU를 둔다. overview/선택/현재 부위만 pin, 비활성 상세 eviction. 강제 GC 수치나 정확한 GPU 사용량을 추정하지 않는다.20회 순환 뒤 resource가 안정된 상한에 수렴하는지 확인한다.
- hash 검증은 제거하지 않는다. build 시 source lineage 검증, revision당 manifest 검증, 최초 chunk 취득 시 content hash. 모든 GLB HTTP 요청마다 역사 task manifest12개를 다시 검증하지 않는다. 변경된 revision을 옛 검증 cache로 승인하지 않는다.
- picking은 현재 visible+eligible 후보를 먼저 줄인다. 매 hover에서 held/hidden/all-loaded geometry 전체를 대상으로 하지 않는다. 실제 병목이 측정되면 BVH 등을 검토하되 의존성을 선제 추가하지 않는다.
- 정적일 때 dirty draw를 유지하며 숨은 탭/정지 상태의 불필요한 React progress 갱신·트리 순회를 줄인다. 현재500ms마다 새 progress 객체를 보내는 비용도 계측한다. 프레임 중 material/배열 반복 allocation을 피한다.
- 동일 조건에서 frame interval과 render CPU 시간을 분리하여 p50/p95, cold load/warm region switch, bytes/materials/draw calls/resources를 기록한다. 데스크톱390px를 실제 휴대폰이라 부르지 않는다. T58 목표 interaction frame p95≤33.3ms, 기준 대비20% 이상 악화는 원인/대응 없이 pass 불가. 가능한 target 기기/브라우저를 명시한다.

## 5. T100 — 전신을 실제로 보고 누를 수 있게

T98에서 동결한 전체 근육/뼈 target과 T99 변환 결과를 공통 경로로 통합한다. 12부위는 별도 외부 task가 아니라 **하나의 coverage matrix와 내부 workUnits**다. 기존 T110–121 exact target 목록542개와563개 membership은 역사로 보존하고 새 mapping revision에 연결한다. 이전 source 차이 때문에 바뀐 소속은 이유/전후 대응을 남긴다.

뼈·근육의 검증된 세 이름/검색 alias, 다대다 지역, 좌우와 part/group 대응을 함께 연결한다. `목+머리` 합집합, 재클릭 해제, 빈 선택은 전신. 팔에는 양측 견갑골 맥락, 허리에는 요추/엉치뼈 등 검증된 제품 context를 적용한다. 이름이 없으면 영어 source label까지 검증한 수준만 제공하고 미확인을 꾸미지 않는다. 단, 이 상태를 전체 세 이름 학습 연결 완료로 세지는 않는다.

부위 안의 모든 필수 named muscle/side에 실제 surface와 typed selection이 있는지 자동 대조한다. source-only가 클릭은 되지만 정보가 없는 관찰 상태와 verified 이름 카드가 있는 상태를 따로 센다. unresolved 대상을 시야 밖으로 숨겨 완성처럼 보이지 않게 한다. 표정근·광배근 등 대표 누락은 필수 항목이다.

T166의 핵심은 이 integration 안에 포함한다: 관찰/학습 선택 분리, 주변 흐리게, **선택 반투명·숨김**, 격리, 맞춤, undo/복원. held/layer-off/region 정책이 override보다 우선한다. 카메라 연속성과 미니멀 UI 유지. 부가 다중 선택·클릭마다 숨기는 전용 mode·redo 확장은 G1 필수 핵심이 끝난 뒤 같은 관찰 backlog에 두며 전신 base 수용을 지연시키지 않는다. 이들은 취소/완료가 아니라 명시적 후속 옵션이다.

첫 화면은 검증된 전신 overview와 최소 도구이며 시작부터 종아리 전용 화면으로 돌아가지 않는다. 로딩 로고/인체 그림/슬로건 제거는 유지한다. 24의 엑셀은 여기서 명칭 참고 후보로만 사용하고 기시정지·기능 검증/신경 내용을 무검증 복사하지 않는다. 얼굴 표정근의 움직임 버튼은 미지원/disabled, 애니메이션 제작0건.

## 6. T80/T58와 완료 지표

진도는 번호/문서/다운로드 파일 개수로 말하지 않는다. 동일 frozen target에 대해 `필수 / geometry 있음 / 기본 표시 / 관찰 선택 / 학습 선택·세 이름 / 보류 / 미확보`를 부위/시스템별로 보고한다. geometry object, mesh resource, canonical concept, anatomical instance를 구분한다. 입·눈 주위/양측 어깨/척추/샅/손발의 비어 있는 부분을 별도 대표 검수로 확인한다.

T80은 전체 누락·중복·side/part·held·세 이름·선택을 전수 감사한다. 알려진 필수 누락이 있으면 해당 T100 unit으로 돌아가며 passed_with_gaps로 G1 합격시키지 않는다. T58은 새 화면/관찰 흐름/모바일 폭/키보드와 실제 성능을 확인한다. 공개 redistribution hold가 남는 경우 로컬 prototype 합격과 공개 배포 가능성을 분리한다. **G1 합격은 구조/탐색 완성이지 기시정지/모든 작용/신경/모션 완성이 아니다.**

구조 합격 뒤 설명→신경→모션 순서에서 기존 검증 자료/공통 엔진을 재사용한다. OpenSim은 후속 검증된 움직임의 보조 source이며 정적 표면 전신 수집의 의존 조건으로 만들지 않는다. 외부 source가 다른 pose라면 당시 motion adapter/rig에서 관계를 검증한다. source geometry에 없는 수축/힘줄/신경을 임의 생성하지 않는다.

## 7. 문서와 Git 운영

`work/EXECUTION.json`만 실행상태/active order/default next/task scope의 편집 원본이다. task 종료 시 그 task record만 바꾸고 `python3 work/tools/sync_execution.py`를 실행한다. `--check`는 생성물 drift를 검출한다. 변경 전 최신 파일을 읽고 같은 field가 동시 변경됐으면 덮어쓰지 않는다. STATUS 아래 역사 내용과 R15의 과거 task record는 삭제하지 않는다. generator가 바꾸는 현재 투영 영역만 소유 delta로 취급한다.

모든 실제 보고서는 범위/검증/미완을 담고 task 종료 시 같은 task 미완 재개인지 다음 ID인지를 기록한다. 사용자 완료 보고와 실제 report/commit 상태가 어긋나면 둘 다 적고, 확인 없이 과거 task pass를 만들지 않는다. 초기 감사 시 T104의 보고서/브라우저 evidence/커밋은 없었으나, 감사 도중 로컬 커밋67d8b79와 해당 보고서/검증 기록이 확인됐다. T104는 exact10 표면의 passed_with_gaps이며 전신 완료가 아니다. 이 문서가 T104를 다시 실행하거나 자체 완료 처리한 것은 아니다. 당시 T105 handoff는 새 EXECUTION의 T98로 대체한다.

진행 중 사용자 WIP와 T13 drafts, OpenSim 원본, 모든 과거 freeze/실제 evidence는 보존한다. 관련 검증을 마친 소유 변경만 로컬 체크포인트에 넣는다. 원본 archive/개인 엑셀/임시 파일은 제외. push/배포/진단·치료·침 시뮬레이션/신규 task 자동 실행 없음. 이번에는 계획·감사·문서 동기화 도구만 만들고 T98의 source 구현을 시작하지 않는다.
