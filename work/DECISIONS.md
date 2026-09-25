# 결정 기록

## T00 — 2026-09-25

- 프로젝트 작업 경로는 `/Users/daniel/Downloads/SIM /HUMAN ATLAS`로 둔다.
- HUMAN ATLAS 상위 경로에는 기존 Git 저장소가 없으므로 이 폴더에 별도 로컬 Git 저장소를 만든다. 자동 push는 하지 않는다.
- `OpenSim_Models/`는 원본 자료 저장소의 별도 checkout으로 보존하고, 상위 프로젝트 Git에서는 제외한다. 확인한 원본 revision은 `d9b05d470b1a481c222372c85b75772faf8f7792`이며 T00 전후 working tree가 깨끗해야 한다.
- 기존 `README.md`, `design/2026-09-25-muscle-atlas/`와 템플릿은 기존 자료로 취급한다. 내용 변경 없이 유지하고 T00 체크포인트에는 넣지 않는다.
- 현재 프로젝트 폴더에서 웹앱 파일(`package.json`, Vite 설정, 앱 진입 HTML)을 찾지 못했다. OpenSim 앱도 `/Applications`와 실행 경로에서 찾지 못했다. T00에서는 앱이나 데이터 구현을 시작하지 않는다.
- 설계와 템플릿은 요구사항 후보이며 완료 산출물이 아니다. 실제 학습 데이터는 아직 없다.
- 다음 직렬 작업은 T01이며 범위·출처 정책을 먼저 고정한다.

## T01 — 2026-09-25

- 성인 사람의 골격근 전신 범위를 고정하고 머리, 얼굴, 저작, 눈, 혀, 인두, 후두, 목, 등, 흉곽/호흡, 복벽, 골반저/회음, 어깨/상지, 손, 엉덩이/하지, 발을 포함한다. 심근·평활근은 기본 제외한다. 이 정책은 catalog 자체나 전체 항목 수의 확정이 아니다.
- 개념 ID 기준으로 한 번만 세며, 좌우 인스턴스·근두/부분·근군·OpenSim force/actuator/path/mesh 항목·별칭은 개념 분모에 중복 추가하지 않는다. midline/unpaired는 강제로 좌우 복제하지 않는다.
- 명칭 국제 기준 후보는 TA2 2판(2019)으로 기록한다. 한국어 후보는 대한해부학회 해부학용어집 6판(2014) 서지 확인에 한정한다. 현행판/원문 자료·locator가 준비될 때까지 catalog에 표준 용어를 입력하지 않는다.
- 해부 설명 source 후보로 OpenStax Anatomy and Physiology 2e를 기록한다. CC BY-NC-SA 4.0 조건은 페이지 내용/그림에 따라 확인하며, broad education text를 전신 기시·정지의 완전한 근거로 취급하지 않는다.
- 평가 source 후보로 Merck Manual Professional의 muscle-strength page를 기록한다. 일반적인 평가 맥락 후보이며 모든 근육의 검사, 진단 성능, 치료 판단의 근거로 확장하지 않는다.
- T02용 3D 후보는 LSDB Archive의 BodyParts3D Release 4.0으로 한정 등록한다. archive page는 CC BY 4.0(2025-02-27 갱신)과 exact credit string을 표시한다. 배포 데이터 날짜(2013-06-19)와 license 갱신일을 구별한다. live information/API 페이지의 CC BY-SA 2.1 JP 표시는 archive license와 혼합하지 않고 source-specific 검증 대상으로 남긴다.
- BodyParts3D 파일, TA2/KAA/OpenStax/Merck 본문 데이터, OpenSim remote model은 T01에서 다운로드/복사하지 않았다. 레지스트리에는 웹 페이지, 판본 식별, locator, local-file 확보 상태를 분리 기록한다.
- 기존 `README.md`, `design/**`, 템플릿과 `OpenSim_Models`는 변경하지 않는다. T01은 외부 공개·앱·임상 task가 아니다. 다음 직렬 task는 T02이다.

## T02 — 2026-09-25

- LSDB Archive의 exact BodyParts3D Release 4.0 OBJ archive에서 필요한 11개 member만 HTTP Range로 획득했다. ZIP 전체는 저장하지 않았다. FMA concept→BP representation→FJ mesh crosswalk는 공식 IS-A 테이블의 locator로 기록했다.
- 우측 6개 pilot concept에 대해 7개 mesh 후보를 유지한다. 우측 gastrocnemius는 medial/lateral head가 별도 concept/파일이므로 하나의 whole-muscle mesh라고 합치지 않는다. 우측 tibia/fibula/talus/calcaneus 네 mesh도 확보했다. 추가 5개 뼈는 crosswalk availability만 기록했다.
- 좌표 결정: source mm, +X 환자 좌/음수 X 우, +Y 후방, +Z 상방을 atlas meter, +X 환자 좌, +Y 상방, +Z 전방으로 `atlas[x,y,z]m = source[x,z,-y]mm/1000` 변환한다. determinant 1이며 오른쪽 부호가 유지된다. source는 성인 남성 정적 reference geometry이고 관절 pose를 표준화한 metadata는 없다.
- official current LSDB Archive page와 README는 CC BY 4.0 및 exact credit을 표시한다. 선택된 2013 OBJ header는 과거 CC BY-SA 2.1 Japan 문구를 포함하므로 원문을 그대로 보존하고 manifest에 차이를 기록한다. 이번에는 외부 배포하지 않으며 배포 시점에 조건을 재확인한다.
- 실제 mesh hash/ID/우측 경계, 단일 부위 viewer의 근육+뼈 화면을 확인했다. viewer gate는 이 후보의 방향·공간 정렬/표시 시험으로 한정된다. shape/identity, 부착면, 임상 의미의 사람 검토를 뜻하지 않는다.
- `OpenSim_Models`는 `d9b05d470b1a481c222372c85b75772faf8f7792`에서 clean 상태이며 `.osim` 근육 이름만 비교했다. 파일 내용은 복사·변환·수정하지 않았다. 기존 `README.md`, `AGENTS.md`, `design/**`의 사전·사후 SHA-256은 모두 일치한다.
- T02 완료. 다음 직렬 task는 T03 공통 스키마와 검증기이며 여기서 시작하지 않는다.

## T03 — 2026-09-25

- 실제 프로젝트 데이터 계약을 Draft 2020-12 스키마로 구현하고, 기본 JSON Schema 키워드와 교차 참조·순환·좌우·좌표·asset revision·증거·리뷰 hash·학습 공개 규칙은 Python 표준 라이브러리 기반 검증기가 검사한다. 사용하지 않는 Draft 키워드는 사전 점검에서 실패하도록 해 묵시적으로 건너뛰지 않게 한다. 이는 범용 JSON Schema 엔진 전체를 구현한다는 뜻은 아니다.
- T02 좌표계약을 RH, meters, +X 환자 좌, +Y 머리/상방, +Z 전방의 Atlas frame으로 고정한다. BodyParts3D source frame에서 Atlas frame으로 변환할 때 `atlas[x,y,z]m = source[x,z,-y]mm/1000`, 회전행렬 `[[1,0,0],[0,0,1],[0,-1,0]]`, determinant +1을 검증한다. asset-native frame/units에서 annotation의 frame/units가 다른 경우 이어지는 transformChain을 요구한다. 알려진 표지 오차는 기록된 meter 허용치와 비교한다.
- Claim/Term/SpatialAnnotation/MeshMapping 및 기능·평가 레코드의 reviewed 상태는 evidence와 현재 content hash에 맞는 human/approved Review 레코드가 필요하다. JSON 자체는 실제 사람 신원이나 서명을 인증하지 않으므로 별도 production review access control 없이는 사람 승인으로 간주하지 않는다.
- Hani 결측은 null과 사유로 저장할 수 있다. Hani 문구가 채워졌으면 evidence 및 현재 사람 리뷰 없이 통과하지 않는다. 자동 번역이나 누락 채우기는 구현하지 않는다.
- fixture와 승인 기록은 gate 검증만을 위한 synthetic 데이터이며 실제 학습자료, 해부 claim, 실제 human review가 아니다. fixtures 경로를 실제 catalog 입력으로 쓰지 않는다.
- T03 검증 성공; 다음 직렬 작업은 T04 전체 근육 목록과 언어 정책이다. T03에서는 실제 데이터나 T04 목록을 시작하지 않았다.

## T04 — 2026-09-25

- 국제 nomenclature 기준 candidate는 IFAA 승인 TA2 제2판(온라인 2019), Part 2로 두었다. 공식 PDF 검색 색인에서 확인 가능한 exact 행/인쇄 쪽 locator만 구조화했으며 바이너리와 checksum을 확보하지 못했다. Part 2 원본 시각 검토/전수 추출 전까지 canonical 전체 목록이나 denominator를 동결하지 않는다.
- 부분 catalog에는 85개 안정 ID를 부여했다: 48 `individual_muscle`, 16 `muscle_group`, 21 `muscle_part`. 개별 근육만 partial count에 포함한다. region tree는 T01의 18 scope node를 scope root 아래 보존하며 TA2 전체 region hierarchy라고 주장하지 않는다.
- source-row Latin/English observation은 exact row/page locator와 연결하되 term records는 `needs_review`다. FIPAT term column role의 원본 시각 확인, TA2 Errata 전수 대조, 대한해부학회 primary/current 용어집과 Korean/Hanja locators 전까지 해당 term promotion/translation을 하지 않는다.
- T05 pilot stable IDs: gastrocnemius `HA-M-000001` (lateral head `HA-P-000001`, medial head `HA-P-000002`); soleus `HA-M-000002`; tibialis anterior `HA-M-000003`; tibialis posterior `HA-M-000004`; fibularis longus `HA-M-000005`; fibularis brevis `HA-M-000006`.
- 7개의 T02 FMA→representation→OBJ 관계를 stable IDs에 provisional crosswalk했다. 두 gastroc meshes는 각 head part에만 연결하며 whole muscle mesh로 합치지 않는다. 해부학적 동일성 사람 review는 남았다.
- CC BY-ND 4.0 안내에 따라 부분 파생 인덱스는 내부 작업물로 두고 public release/redistribution을 하지 않는다. Exact file attribution/reuse review remains open.
- T04는 `complete_with_partial_catalog`; `CATALOG_GATE=blocked`, T05 pilot은 Runbook에 따라 다음 진행 가능. T04에서 anatomy claim, attachments, app, release, diagnosis/treatment/acupuncture work를 시작하지 않았다.

## T05 — 2026-09-25

- T04의 여섯 pilot stable IDs와 비복근 두 head part ID를 그대로 사용했다. T04 TA2 row 용어는 English/Latin 관찰 자료로 유지하며 원본 행 시각 검토와 term-role 대조 전까지 `needs_review`로 남겼다. 여덟 항목의 Korean Hangul/Hanja는 출처 locator가 없어 null/held로 보존했다.
- 역사적 구조 텍스트 출처로 Gray/Lewis, *Anatomy of the Human Body*, 20th US ed. (1918), section 8c의 해당 근육 subsection을 선정했다. Tibialis anterior는 printed p. 480 locator도 확인했다. Gray는 현행 표준이 아니고 미국 외 배포 권리는 확인하지 않아 source registry scope를 `internal`, `research`로 한정했다. 41 attachments와 45 claims 전부 `needs_review`다.
- OpenStax 2e page에 generative-AI ingestion 제한이 있으므로 본문 anatomy 추출에는 사용하지 않았다. License/reuse 상태는 registry에 source-specific으로 남기고 허가된 대체 작업 절차가 마련되기 전까지 제외한다.
- 구조 term 54개와 attachment target structure 54개는 source-bounded historical labels로 추가했다. 넓은 tibia/fibula 표기를 원문에 명시된 head/surface/segment landmark로 분할하고 비복근 condyle/인접 femur, 뒤정강근 인접 septa 관계를 각각 보존했다. 총 41 attachments, 45 claims를 추가했다. 변이, 현대적 용어 선택, 3D 좌표/mesh annotation으로 의미를 넓히지 않았다.
- T05는 부분 catalog 상태에서 pilot 데이터 추출 및 명시적 gap 기록까지 완료했다. Human anatomy review, claims 승격, public release와 전신 denominator freeze는 하지 않았다. 다음 작업은 T06 텍스트 탐색 앱이며 구조 검토 상태는 그대로 전달한다.

## T08 — 2026-09-25

- T06에 Three.js가 포함되어 있지 않고 로컬 pnpm metadata/store에도 패키지가 없으며 네트워크 접근이 제한되어 있다. T08은 dependency 다운로드 대신 T07에서 생성한 고정 단일 GLB의 실제 계약(정점·법선·삼각형 인덱스와 node/mesh ID)을 검증하는 앱 내부 WebGL viewer를 사용한다.
- 이 viewer는 T07 asset에 한정한 로컬 학습 UI로, 범용 glTF 엔진 또는 임상/해부학적 정확성 검토기가 아니다. T07 crosswalk의 `needs_review`, provisional 관계, 기준 포즈의 한계는 표시 상태에서 유지한다. renderer 교체 또는 전체 glTF support는 별도 범위다.

## T09 — 2026-09-25

- T03 canonical `SpatialAnnotation` 스키마를 완화하지 않고, instance가 없는 `draft`를 교환하기 위한 별도 로컬 스키마를 추가했다. `instanceId: null`, `reviewState: draft|stale`로 제한하며 reviewed를 입력할 수 없다.
- point/polyline은 표면 ray hit 위치를 Atlas asset frame의 meter 좌표로 보관한다. surface patch는 mesh-local triangle ID와 topology hash를 함께 보관한다. camera pose에서 좌표를 만들지 않고, rotation/zoom 후 현재 카메라 투영으로 overlay를 다시 그린다.
- 가져오기에서는 T05 attachment/description claim/evidence 연결, T07 mesh target, side, asset revision/hash, frame/units/pose/topology를 함께 확인한다. mesh revision이 달라지면 import는 실패하고 저장본의 revision/topology가 달라진 기존 draft는 stale로 격리한다.
- T09 UI smoke에서 실제 T05 설명에 연결된 draft 3개를 임시 생성해 geometry, 수정, JSON, reload 경로를 확인한 뒤 UI에서 모두 삭제했다. 두 번의 확인에서 final local draft count는 0이다. 해당 smoke 좌표는 anatomical mapping이나 검토 후보로 기록하지 않았다.
- CUA의 브라우저 화면 캡처는 실행 중 시각적으로 확인했다. 이미지 파일을 프로젝트로 저장하려던 data URL 이동이 Codex browser URL policy에 의해 거부되어 우회하지 않았고, 대신 브라우저 상호작용·console 결과를 JSON 로그에 남겼다.
- T09는 local-only draft tooling이다. Canonical catalog/T05 claims/T03 SpatialAnnotation/OpenSim 원본을 수정하지 않았으며 T10 actual mapping과 사람 검토는 시작하지 않았다.
