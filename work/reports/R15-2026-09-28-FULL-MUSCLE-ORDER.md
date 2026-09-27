# 전신 근육 선행·신경 후행 계획 개정

2026-09-28 · Astra · 계획 완료, 구현 미착수

T73/T74/T75/T76의 task 파일과 18 문서 내 해당 네 프롬프트는 보존했다. 현재 다음 T73도 유지한다. 사용자는 이 네 개를 원래대로 실행하고 T77부터 20-SERIAL-PROMPTS-FULL-SCOPE.md를 사용하면 된다.

실제 검사: 캐시 원본 isa_element_parts.txt의 상완이두근 갈래/양측 4개 및 상완삼두근 6개 FJ ID가 runtime manifest에 모두 없다. 요추1–5/엉치뼈는 이미 있지만 defaultVisible=false이다. 추가 38개 이름 query 후보를 exact source ID로 join했고 승모근 6개·대퇴이두근 4개 후보가 장면에서 빠진 것을 확인했다. 비복근은 원본 후보4개 중2개만 있다. 이것은 전신 canonical 근육 개수/완전성 감사가 아니라 누락 원인 조사에 사용할 candidate audit다. 광배근 영어 query는 이 metadata 파일에 일치하는 row가 없으므로 여기서 확보 불가라고 단정하지 않는다. 다른 원문/part-of tree까지 T73/T78이 대조해야 한다. 이번에는 실제 화면을 새로 조작하지 않았으며 geometry 자체의 취득/검증을 했다는 주장도 하지 않는다.

기존 보완자산 checkbox는 취득/provenance 구분을 사용자에게 노출한 상태다. T77에 learner에서 이 조작을 제거하고 로컬 표시 적격 뼈·근육은 기본 전신에 함께 두도록 명세를 수정했다. 실제 hold/공개 권리/source-only binding 승격은 별도이며 임의 승인하지 않는다. 단일 장면과 최종 미니멀 로딩 유지.

새 단계: T77 기본 통합 → T78 전신 target/전체 batch 계획 → T79 및 전체 구조 batch → T80/T58 → T81 및 전체 기시정지 batch/T82 → T83 및 전체 기능 batch/T84 → T35 motion 전체 계획 → 앞정강근/소흉근/나머지 전체 animation batch/T47/T85 → T61/T86 이후 전신 신경 조사·통합 → 실제 주행·지배근 강조 → 포착/수준별 기능이상 설명 → T65/T40. 독립 신경 pilot를 근육 전체보다 앞에 두던 순서는 폐기했다.

새 task T79–91은 계획이다. 동결 범위를 실제 처리하는 추가 batch는 T92 이후 미사용 ID로 각 global gate 앞에 삽입한다. 모든 근육의 representative motion 최소1개를 기준으로 하되 추가 작용 지원과 생리학적 시뮬레이션을 혼동하지 않는다. 모든 신경은 명명/분지/해상도 분모를 먼저 정의하고 여러 모델을 단순히 포개지 않는다.

산출물: 19 설계, 20의 34개 실행 프롬프트, T77 이후 개정 명세와 T79–91 새 명세, live STATUS/registry/안내 우선순위, evidence. 기존 WIP가 섞인 기존 task/안내/상태 전체는 stage하지 않고 before hash+이번 prepend/state delta를 커밋한다. 이미 버전 관리된 T77/T78 소유 수정과 신규 문서·task·report/evidence는 포함한다. runtime/OpenSim/source/T58 실제 이력 변경 없음. 문서/queue/hash 검증만 수행했고 새 제품 pass/브라우저 검증을 주장하지 않는다. push/배포/다음 task 실행 없음.
