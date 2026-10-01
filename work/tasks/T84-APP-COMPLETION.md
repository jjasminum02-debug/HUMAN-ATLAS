# T84 — 지원 기능 설명·학습 흐름 감사

2026-10-01 · 현재 계획 · 담당 Luna Max.

이 명세는 [27-APP-COMPLETION-AND-CONTENT-ROADMAP.md](../../design/2026-09-25-muscle-atlas/27-APP-COMPLETION-AND-CONTENT-ROADMAP.md)와 EXECUTION의 계약을 따른다. 계획 수정은 구현 합격이 아니다. 이전 명세 `work/tasks/T84.md`와 보고서는 역사로 보존된다.

## 범위

T83의 현재 지원 기능 카드 전체를 구조/갈래/고정 조건과 대조하여 오류를 수정한다. 한글 의미와 runtime 한자0건, 텍스트 지원과 clip 미지원의 구분, 표정근 설명을 감사한다. 전체 변이/미지원 target의 자료 확보를 일괄 gate로 만들지 않는다. 검증한 기능만 제품 채택하고 콘텐츠 completeness는 별도로 유지한 뒤 기존 G3 신경 순서로 인계한다.

## 합격 기준

- 현재 지원 기능 설명 전체의 데이터 계약과 의미/구조 일관성을 감사한다.
- 실제 카드/clip 상태의 misleading UI와 기능 텍스트 오류를 수정한다.
- 설명 기능의 scoped acceptance와 남은 콘텐츠 및 G3 인계를 구분한다.

해당 제품 계약을 실제로 검증한 경우 completed/passed, nextUnit=null로 종료한다. 전체 콘텐츠 completeness는 별도 partial이어도 된다. 지원한다고 표시한 구조의 잘못된 이름/좌우/범위/위치는 허용하지 않는다. 문서 수정만으로 합격하지 않는다.

## 실행과 산출물

AGENTS, EXECUTION, 27 설계, 이 명세, 지정 promptFile, 실제 선행 보고·evidence를 읽는다. 기존 25·26의 보존·공통 처리 원칙은 유지하되 충돌하는 전체 콘텐츠 gate/10개 종료 규칙은 적용하지 않는다.

task 소유 코드/자료 수정, 관련 검사와 필요한 실제 UI 검증, 보고서 및 작은 evidence를 남긴다. 원본/OpenSim_Models/T13/기존 WIP/source-only/public held/humanReview를 보존한다. 기존 542/563/12와 HA 130/역사163을 유지한다. source/hash와 제품 route 실제 숫자를 보고하며 전체 해부학 완료라고 쓰지 않는다.

해당 task record 갱신 후 sync_execution.py와 --check로 문서를 동기화한다. 소유 변경만 로컬 커밋한다. 다음 task 자동 실행·push·배포·자동 위임·임상 기능 구현은 하지 않는다.
