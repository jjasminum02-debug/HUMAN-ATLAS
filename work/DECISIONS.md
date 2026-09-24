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
