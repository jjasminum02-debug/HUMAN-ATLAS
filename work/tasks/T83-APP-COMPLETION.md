# T83 — 지원 근육 한글 기능 설명 연결

2026-10-01 · 현재 계획 · 담당 Luna Max.

이 명세는 [27-APP-COMPLETION-AND-CONTENT-ROADMAP.md](../../design/2026-09-25-muscle-atlas/27-APP-COMPLETION-AND-CONTENT-ROADMAP.md)와 EXECUTION의 계약을 따른다. 계획 수정은 구현 합격이 아니다. 이전 명세 `work/tasks/T83.md`와 보고서는 역사로 보존된다.

## 범위

현재 지원 근육 전체에 검증된 한글 기능 설명을 연결한다. 기존 workbook staging/claim을 재사용하고 한자 정규화뿐 아니라 작용/움직이는 구조/고정 조건/갈래 의미를 대조한다. 표정근은 텍스트를 제공하고 애니메이션 미지원은 유지한다. 확인되지 않은 세부 작용은 unsupported로 분리하되 미지원 clip 때문에 텍스트를 막지 않는다. 전체 변이/모든 clip 연구는 이번 기능 종료 조건이 아니다.

## 합격 기준

- 현재 지원 근육 전체의 기능 claim과 카드 채택/미지원 상태를 연결한다.
- runtime 기능 텍스트의 한자 0건 및 의미/방향/조건/갈래 보존을 검증한다.
- 구조·기능·clip 지원을 구분하고 실제 기능 카드 흐름을 확인한다.

해당 제품 계약을 실제로 검증한 경우 completed/passed, nextUnit=null로 종료한다. 전체 콘텐츠 completeness는 별도 partial이어도 된다. 지원한다고 표시한 구조의 잘못된 이름/좌우/범위/위치는 허용하지 않는다. 문서 수정만으로 합격하지 않는다.

## 실행과 산출물

AGENTS, EXECUTION, 27 설계, 이 명세, 지정 promptFile, 실제 선행 보고·evidence를 읽는다. 기존 25·26의 보존·공통 처리 원칙은 유지하되 충돌하는 전체 콘텐츠 gate/10개 종료 규칙은 적용하지 않는다.

task 소유 코드/자료 수정, 관련 검사와 필요한 실제 UI 검증, 보고서 및 작은 evidence를 남긴다. 원본/OpenSim_Models/T13/기존 WIP/source-only/public held/humanReview를 보존한다. 기존 542/563/12와 HA 130/역사163을 유지한다. source/hash와 제품 route 실제 숫자를 보고하며 전체 해부학 완료라고 쓰지 않는다.

해당 task record 갱신 후 sync_execution.py와 --check로 문서를 동기화한다. 소유 변경만 로컬 커밋한다. 다음 task 자동 실행·push·배포·자동 위임·임상 기능 구현은 하지 않는다.
