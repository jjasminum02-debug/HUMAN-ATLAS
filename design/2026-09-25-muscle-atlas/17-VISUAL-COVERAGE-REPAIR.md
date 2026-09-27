> **2026-09-28 전신 범위 개정:** T73–76 내용/프롬프트는 그대로다. T77 이후는 19-ALL-MUSCLES-BEFORE-NERVES.md와 20-SERIAL-PROMPTS-FULL-SCOPE.md 우선. 전신 구조→모든 근육 기시정지→기능→모든 근육 대표 움직임→전신 신경 조사/통합→3D→포착 설명 순서. 아래 충돌하는 순서는 이력이다.

# T58 이후 전신 시각 범위 보완 설계

2026-09-28 · 계획만 작성, 신규 task 구현/취득 미착수. 충돌하는 13/14의 순서 및 이전 T58 재개 프롬프트보다 이 문서와 18 문서/현행 registry가 우선한다.

## 재시작 안내

사용자가 파일·Git·원본을 직접 만질 필요는 없다. T58 작업을 삭제하거나 초기화하지 않는다. 이전 재개 프롬프트는 누락 조사/계획을 다시 요청하는 것이므로 이제 중복이다. **다음은 T73 한 번 실행**이다. 소유자는 Astra 현재 대화. 이후 한 프롬프트씩 실행하고 보고서의 next와 실제 registry를 따른다. 숫자 오름차순이 아니다. T58은 T77/T78 이후 기존 코드를 유지한 재검증이며 처음부터 다시 구현하는 task가 아니다.

현재 checkout에서 STATUS/registry T58=partial, HEAD=13f5a7b402b89548cbcc0b9e570558ca08a4c378를 확인했다. Luna 인용문의 T58 미착수 주장은 이 상태에는 맞지 않는다. 다른 checkout/이전 시점 여부는 확인하지 않았으므로 원인을 단정하지 않는다. 공유 STATUS/registry의 기존 WIP는 보존하며 이번 계획 delta를 별도 기록한다.

## 무엇이 잘못됐고 무엇을 바꾸나

현재 T53/T54 manifest meshRecords에 deltoid/latissimus 이름이 없고 기존 보고서들은 source subset임을 명시한다. 현재 runtime manifest는 이름이 아니라 source ID 중심이므로 이름 문자열 검색만으로 전신 부재를 최종 판정하지 않는다. T73이 canonical concept→원본 관계→exact ELEMENT를 조인해 확정한다. 사용자/Luna 관찰의 삼각근·광배근·한쪽 두개골·샅 범위는 우선 확인 대상으로 채택한다. T72 report의 frontal/mandible/occipital은 확보됐지만 default false인 보완 자료다. 모두 같은 종류의 '없음'이 아니다.

핵심 설계 결함은 취득한 subset의 100%와 제품에서 필요한 구조의 coverage를 분리해 정의하지 않은 것이다. region root 탐색 누락인지 source 자체 부재인지는 아직 조사 항목이다. Luna의 코딩 능력이나 OpenSim 정합 문제라고 단정할 근거가 없다. 현재 정적 모델 보완은 BodyParts3D 내부 범위/표시/mapping 문제를 먼저 확인한다. OpenSim registration은 동일 모델 운동에서 별도로 검증한다.

26개 bone-root gap만 메워도 주요 근육 누락이 자동 해결되는 것은 아니다. 0/11 residual은 작은 동결 취득 목록 완료일 뿐이다. T73에서 12부위 시각 목표를 앞당겨 정의한다. 이후 T32는 전체 학습 개념·세 이름·기시정지/기능 분모를 확장/확정하는 작업이며 이번 시각 분모를 덮어쓰지 않는다.

## 데이터와 화면의 계약

독립 필드: product target 및 side/part, source availability/identity/frame, acquired/converted, local default visibility, pickability/learner binding, text support, motion support, license/public redistribution, human review. 한 enum을 '검증됨'으로 바꾸며 전부 승인하지 않는다. 검증된 로컬 source-only는 배경 구조로 표시할 수 있지만 자동 선택·학습 연결·공개배포 권한이 생기지 않는다.

T77에서 기존 supplement를 기본 화면에 넣으려면 해당 ID별 local display 사용 근거/identity/frame/시각 QA와 before/after 정책을 새 revision에 남긴다. 기존 역사 manifest를 덮지 않는다. identity/laterality/rights 관련 실제 hold는 유지한다. 라이선스의 로컬 사용과 공개 재배포도 별도 판단한다. '숨김 20개 모두 켜기'는 해결책이 아니다.

학생 화면에는 source-only/held/JSON/task 번호를 나열하지 않는다. 기본 모형·12부위·검색·선택 카드만 유지한다. 연결 안 된 모형은 배경으로 남고, 검색/목록은 연결 대상만 보여준다. 필요할 때만 짧은 준비 중 안내를 쓴다. 상세 누락표는 내부 QA다. T78에서 제한된 주요 구조를 실제 클릭/세 이름으로 연결하고 전신 내용 완성이라고 부르지 않는다.

## 실행 순서와 gate

T73(Astra) → T74(Luna Max, 두개골) → T75(Luna Max, 삼각근·광배근) → T76(Luna Max, 골반·샅) → 추가 필수 자산 task(필요 시 T79부터) → T77(Astra, 통합·표시 정책) → T78(Luna Max, 주요 선택/이름) → T58(Astra 재검증) → 기존 운동/신경 queue.

T74–76은 T73이 exact IDs와 개념 상한을 동결한 뒤 실행한다. 신규 일반 내용은 최대10개 개념, 파생 source 파일은 내부5–10개 단위로 처리한다. 초과는 미사용 정수 ID로 분할해 T77 앞에 넣는다. 모든 부위를 한 거대 task로 재수집하지 않는다. 기존 cache/importer/hash를 재사용한다. 다른 source가 필요한 경우 별도 source/registration 설계 task로 분리한다.

실제 자산을 확보할 수 없는 필수 형상이 있으면 T58을 억지 합격시키지 않는다. 정확한 후보/공식 자료 조사 결과와 대체 가능성, 다음 실행 책임을 남긴다. 자료 부재 문서만 반복하는 무한 task는 금지한다. task plan 및 단위검사 통과는 actual surface/visual pass가 아니다.

후속 번호 전체와 독립 복사용 프롬프트는 18 문서. T33 이후 지역 학습자료 확장과 T66 이후 동작 확장은 첫 배치만 예약돼 있다. 이를 한 번 실행했다고 전신 완성으로 넘어가지 말고 동결 분모의 미완 항목마다 작은 실제 실행 batch를 queue에 넣는다. T34/T47은 해당 분모가 충족돼야 pass한다. 평가/경혈 queue는 별도 사용자 요청까지 deferred다.

## 보존과 기록

이번에는 계획·명세·상태만 수정한다. runtime code, 모형, 기존 T58 보고서/evidence/commit은 그대로다. 기존 WIP 섞인 파일 전체는 stage하지 않고 이번 상태/안내 delta를 기록한다. 로컬 소유 문서 커밋, push/배포 없음. 실작업자는 최신 checkout의 STATUS와 registry를 확인하고 오래된 문서의 next는 이력으로 취급한다.
