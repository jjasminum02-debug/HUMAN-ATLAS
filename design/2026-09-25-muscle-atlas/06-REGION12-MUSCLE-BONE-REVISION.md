> R13 보완: AI 자료 대조/사람 검토의 분리, 작용 설명·교육용 움직임, T16 이후 실행 및 Git은 07/08/09를 우선한다. 06의 12부위와 T15 흐름은 유지한다.

# R12 — 12부위 근육·뼈 Atlas 설계 개정

날짜 2026-09-26. 사용자 요구에 따른 현행 우선 설계. 이 파일은 구현 완료 증거가 아니다. 00–04의 이전 한자문자 필수/세부부위 메뉴/사람검토 전 전체개발 중단 지침과 충돌하면 이 개정이 우선한다. T00–T14b 보고서는 역사 기록으로 보존한다.

## 제품 목표와 이번 범위

학생이 부위를 선택하면 그 부위의 근육과 뼈를 함께 탐색하고, 근육 또는 뼈 클릭에 맞는 정보 카드가 열린다. 처음에는 실제 자산이 있는 종아리에서 이 흐름을 완성하고 나머지 부위를 순차적으로 채운다. 사용자가 말한 Atlas는 부위→장면→구조선택이라는 탐색 방식으로 해석한다. 특정 상용 앱/버전을 확인하거나 그대로 복제했다고 주장하지 않는다.

경혈학·신경 기반 MPS·통증사냥법·Pro mode는 미래 별도 설계다. 이번에 탭/스키마/침 궤적/치료규칙을 미리 만들지 않는다. 현 구조 ID, 자산 revision, 좌표계가 명확하면 이후 별도 레이어로 연결할 수 있으므로 이것만 보존한다.

## 1. 정확히 12개 기본 분류

| 순서 | 부위 | 영어 | 장면 뼈 범위 제안 |
|---|---|---|---|
| 1 | 머리 | Head | 두개골·하악골 |
| 2 | 목 | Neck | 경추·목뿔뼈 및 필요한 인접 뼈 |
| 3 | 등 | Back | 척추·갈비뼈·어깨뼈 문맥 |
| 4 | 어깨·어깨뼈 | Shoulder/Scapular | 어깨뼈·빗장뼈·위팔뼈 문맥 |
| 5 | 가슴우리 | Thorax | 갈비뼈·복장뼈·흉추 문맥 |
| 6 | 배·허리 | Abdomen/Lumbar | 요추·아래쪽 갈비뼈·골반 문맥 |
| 7 | 골반·샅 | Pelvis/Perineum | 골반뼈·엉치뼈·꼬리뼈 문맥 |
| 8 | 볼기·깊은엉덩이 | Gluteal/Hip | 골반뼈·대퇴골 근위부 문맥 |
| 9 | 넙다리 | Thigh | 대퇴골·무릎뼈·인접 골반/하퇴뼈 문맥 |
| 10 | 종아리 | Leg | 경골·비골·필요한 대퇴골 원위부와 발뼈 문맥 |
| 11 | 발 | Foot | 발목뼈·중족골·발가락뼈 문맥 |
| 12 | 팔·손 | Upper limb | 위팔뼈·노뼈·자뼈·손뼈 및 인접 어깨 문맥 |

분류 수는12로 고정한다. 표정근/씹기근/외안근/혀근육/근군/앞칸 등의 하위 탐색 메뉴를 만들지 않는다. 이런 해부학 개념과 개별근 자체를 데이터에서 삭제하는 것은 아니다. 근육 부분(삼각근 견봉부 등)은 해당 근육 상세에서 선택 가능하다. layer/좌우/근육·뼈 표시 필터도 부위 분류와 별개다.

위 뼈 목록은 장면 제작 범위 제안이며 실제 존재하는 mesh/정확한 해부학 연결을 주장하지 않는다. 부위별 실제 자산 목록은 출처·라이선스·정합 확인 후 scene manifest로 기록한다.

## 2. 다중 소속: 동일 구조 한 개, 여러 탐색 입구

- MuscleConcept/Structure의 안정 ID는 유지하고 `RegionMembership(categoryId, entityKind, entityId)`를 별도 다대다 관계로 둔다. 같은 근육을 카테고리별 새 ID로 복제하지 않는다.
- 사용자가 제시한 내폐쇄근은 골반·샅과 볼기·깊은엉덩이 양쪽에서 같은 개념으로 탐색한다. 대요근은 배·허리에서 반드시 찾을 수 있어야 한다. 기타 경계근 다중 소속은 제품 탐색 정책+근거를 기록해 결정한다.
- 소속과 장면 문맥을 분리한다. 종아리 장면에 대퇴골이 보인다고 넙다리 근육 전체가 종아리 소속이 되는 것은 아니다.
- 전신 개별근 수는 unique concept ID. 부위별 수 합계를 전신 분모로 사용하지 않는다. 근군·부분·좌우인스턴스·메시도 별도 집계.
- 기존18개 source region + root(19 records)는 삭제/개명하지 않는다. source taxonomy와 product category를 분리하고 crosswalk를 둔다. face/mastication/eye/tongue는 head로 합치되 source lower_extremity는 thigh/leg/foot으로 단순복제하지 않고 개별개념 대조한다. 인두/후두 등 경계도 개별 판정. 매핑이 안 되면 내부 unassigned 큐이며13번째 사용자 부위를 만들지 않는다.

## 3. 세 이름: 실제 한자는 요구하지 않음

| UI 명칭 | 새 projection 필드 | 예시 |
|---|---|---|
| 한글명(우리말명) | koModern | 어깨세모근 |
| 한자어명(한글 표기) | koTraditional | 삼각근 |
| 영어명 | en | deltoid |

기본 제목/검색 결과는 koTraditional → koModern → en 순의 첫 사용가능값. '한자명'이라는 사용자의 표현은 삼각근이라는 한글 표기를 뜻한다. 실제 문자 三角筋은 요구하지 않는다. 두 한국어 이름이 같은 경우 새 이름을 만들지 않고 같은값/비해당 이유를 허용한다. '우리말' 필드가 항상 순우리말이라는 주장도 하지 않는다.

현재 overlay의 label→koTraditional, korean→koModern, english→en은 **항목별 검토 후** migration한다. label에 영어가 들어간 항목을 한국어로 오인하지 않는다. 기존 canonical text/alias/claim ID와 사람검토 상태는 보존한다. 실제 Hanja 값과 provenance는 legacy 데이터로 남겨도 되지만 기본 카드/입력란/필수조건/누락 경고/개발할당량에서 제외한다. 한자 조사는 더 하지 않는다. 과거 한자 테스트는 보존용과 제품 수용검사로 분리한다. Hani evidence 보존 규칙은 삭제하지 않고 필수 coverage만 제거한다.

검색은 양쪽 한국어 이름·영어 정규명/구용어/확인한 별칭을 같은 ID로 연결한다. deltoids 입력은 deltoid의 검색 편의 별칭으로 사용할 수 있지만 원문 표준명 필드를 덮어쓰지 않는다. spleinus는 후보2개, 측면삼각근은 견봉부. 검색 범위는 근육+뼈. 동일어는 entity kind/부위를 함께 보여준다.

## 4. 사용 흐름과 화면

데스크톱: 상단 구조검색 / 왼쪽12부위 및 선택부위 구조목록 / 중앙 큰3D / 오른쪽 선택한 구조 정보. 첫 화면은 최근 부위 또는 실제자산이 있는 종아리를 사용하고12부위 전체로 이동 가능. 머리를 선택하면 머리 근육과 뼈 장면을 로드해야 하며 미확보 시 현재 종아리를 머리처럼 보여주지 않는다. 해당 부위 사전과 '3D 준비 중'을 표시한다.

부위를 선택했을 때 근육은 자연스러운 갈색, 뼈는 아이보리. 선택 구조는 식별 가능한 강조와 이름표. 부위 전체/선택 확대/주변 투명/근육·뼈 표시/초기화만 기본 조작에 둔다. 기본 카메라는 화면의 사용 가능한 영역에서 선택부위가 주대상이 되도록 맞춘다. context 뼈의 긴 전체 bounds 때문에 근육이 작아지는 문제를 되살리지 않는다.

근육 카드: 기본명+세 이름, 구조의 기시/정지 요약, 상세 위치/근거는 펼치기. 기능/평가는 기존 계획에 맞춰 확장. 뼈 카드: 세 이름(있는 경우), 좌우, 간결한 형태/주요 표지, 관련 근육과 부착 관계, 출처. 뼈에 근육용 기시/정지·기능평가 탭을 그대로 적용하지 않는다. 표지 클릭은 부모뼈와 관계를 표시하며 표지와 전체뼈의 ID를 합치지 않는다.

모바일: 부위 선택은 한 개의 '부위 선택' 버튼으로12개 목록을 열고, 기본 화면은3D와 접을 수 있는 상세 카드 중심. 긴 목록+긴 설명이 모형을 화면 아래로 밀지 않도록 한다. 텍스트로 공부하기와3D 보기 전환 제공. 키보드 구조목록은 canvas 클릭과 같은 선택 상태를 만든다.

## 5. 런타임 데이터 계약 — T15b에서 실제 구현

- `NavigationCategory`: id/order/labelKo/labelEn. design JSON의12개 고정 순서를 사용.
- `RegionMembership`: categoryId, entityKind(muscle|bone), entityId, reason, evidenceRefs 또는 productDecisionRef, status. unique(categoryId,kind,id). source region에서 무조건 추론하지 않음.
- 뼈는 기존 `Structure(kind=bone)`를 재사용. 좌우 실제표현에는 `StructureInstance` 또는 기존 Instance 일반화 중 하나를 T15b ADR로 결정. 권장: 기존 근육 Instance를 깨지 않는 별도 StructureInstance. 전체뼈 없는 landmark-only ID는 whole-bone으로 재활용 금지.
- `StructureMeshMapping`: structureInstanceId, meshIds, representationType, evidenceIds, reviewState. 기존 muscle MeshMapping과 별도. 실제 sourced bone identity에 내부 stable ID 신규발급 가능; 외부 표준 ID 날조 금지.
- `SceneManifest`: categoryId, revision, assetRefs, selectableBindings, contextBindings, defaultView, availability, frame/pose/modelId. available/partial/unavailable 명시. 매핑없는 mesh는 '정보 연결 준비 중'이며 이전 근육 카드가 남아서는 안 됨.
- `Selection`: kind(muscle|bone|landmark), conceptId, instanceId?, partId?, meshId?. mesh pick→binding→typed selection→카드의 한 방향 흐름. 잘못된 유형 참조 거부.
- URL은 `?region=leg&kind=muscle&id=...&side=right`. 기존 `?muscle=...` 링크는 호환 adapter. 현 부위가 선택근육의 소속이면 유지; 다른부위에서 검색한 경우 소속부위 중 사용자 선택 또는 정해진 우선순위(임의 유일소속 강제금지). 없는3D 상태 명시. Back/Forward가 부위/선택/카메라 컨텍스트를 일치시킴.
- 장면 로드 경쟁: 뒤늦게 도착한 이전부위 응답을 폐기. shared asset cache는 revision별, 참조 수/예산을 두고 GPU 자원 해제. 같은 모델·좌표·pose 아니면 임의로 장면에 섞지 않음. 부착 후보는 기존 topology/pose/hash 검증 유지.

## 6. 완료 상태와 검토 병목 분리

T14b는 needs_human_review 그대로. 사람검토 대기는 해당 내용의 reviewed 승격을 막는다. 명칭 정책/12부위 UI/뼈 카드/장면 로더/전신 목록 작업을 일괄 중단시키지 않는다. 0/41 surface를 완료로 바꾸지 않는다.

구조 데이터에는 이름 준비/텍스트 근거/모형 매핑/위치 후보/사람 검토의 서로 다른 상태를 둔다. 자료가 없어도 일부검증 앱을 개인 학습 초안으로 탐색할 수 있고, 확인되지 않은 위치는 정확한 기시·정지로 표시하지 않는다. T13c처럼 geometry:null인 문맥을 여러 번 생성하는 것만으로 공간개발 진전으로 세지 않는다.

## 7. 검증 기준

정확히12개 부위, 외안근 등 하위 메뉴0. 내폐쇄근 다중부위 동일ID; 카테고리 합계와 전신 unique 집계 분리. 두 한국어 이름+영어 동일결과; 실제 한자0개인 데이터도 유효. 근육 클릭→근육카드, 뼈 클릭→뼈카드, 미매핑 클릭→명시적 준비중. 하퇴→머리빠른전환→이전응답폐기, 뒤로가기, resize, context뼈, 기존부착초안 보존. 1440/1024/390 실제장면 검증. 12개 메뉴의 존재를12개3D 장면완성으로 보고하지 않는다.

## 8. 모델과 Git 운용

모델 배분은 사용자 선호와 계약 복잡도를 기준으로 한 프로젝트 운영안이며 모델 성능 벤치마크가 아니다. Luna Max는 고정된 명세의 UI/용어/매핑/배치와 검증. Sol High는 T15b 유형·ID·migration 계약과 T15e 장면수명/비동기 로더만 우선 담당. 실패 두 번 뒤에도 같은 계약/상태 문제면 재현과 실패테스트를 남겨 Sol에 그 부분만 넘긴다. 전체 task를 매번 Sol로 돌리지 않는다.

각 작업 전 git status와 HEAD, 기존 변경 보존 기준선을 기록한다. 종료 후 검증한 task 소유파일을 선별하여 로컬 커밋하고 해시/포함범위/잔여변경을 보고한다. 기존 미커밋과 같은 파일에 섞이면 부분 스테이징으로 분리하거나 커밋 불가 사유와 명확한 포함 승인을 요청한다. git add .로 무차별 추가하지 않는다. 원본/비밀/비공개/임시/불필요 대용량 제외. push/배포는 별도 요청 전 금지. 기술커밋은 의료승인이나 제품완성 선언이 아니다.

[OpenAI의 작업 완료 조건·검증 범위 안내](https://developers.openai.com/cookbook/examples/codex/using_goals_in_codex)를 참고했다. 여기의 Luna/Sol 배분은 사용자 지정 운용안이며 공식 모델 비교 결과로 제시하지 않는다. Goal/자동화/새 task를 자동 생성하지 않는다.
