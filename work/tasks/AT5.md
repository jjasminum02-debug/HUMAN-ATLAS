# AT5 — 일괄 anchor compiler와 학습 표시 정책

상태: planned / 구현 미착수. 실행 상태 원본은 work/EXECUTION.json의 featureWorkUnits.AT5.
예상: **55–80분**. 선행: AT4. 기본 실행 순서: AT1→AT29.

## 읽을 자료

AGENTS.md, work/EXECUTION.json, work/NEXT.md, design/2026-09-25-muscle-atlas/30-AT-361-POINTS-AND-TERRITORIES.md, work/reports/acupoint-AC1.md, work/reports/acupoint-AC2.md와 선행 AT report/evidence. AC 역사 자료는 최초 또는 관련 변경 때만 읽고 반복 다운로드하지 않는다.

## 수행 범위

공통 landmark/B-cun/F-cun 규칙 입력→anchor 제안→검증→runtime projection을 만든다. 기술 판정/위치 정밀도/AI 작성 출처/교수 검토/권리를 분리한다. 기존 productInstances의 영구 AI 차단은 근거에 따라 대체하고 schema migration을 만든다.

대상 코드: 별도 point 배정 없음.

## 완료 기준

의미 있는 랜드마크와 좌우·자세·근거가 확인된 교육용 위치만 local learner eligible로 판정한다. AI 작성 provenance는 지우지 않는다. 단순 bounds 비율/nearest projection/unresolved는 자동 승인하지 않는다. 실패 unit 재개와 원문 보존을 검증한다.

## 공통 실행 규칙

- 기존 AC1·AC2 코드와 실제 evidence를 재사용한다. 교수 검토 미수행/과거 미승인만으로 독립 기술 작업을 막지 않는다. 근거 없는 좌표·권리·검토는 만들지 않는다.
- 한 번에 이 task만 실행한다. 20–80분 규모의 계획이며 이 task의 예상 시간은 위 표기다. 60분에 진행률을 점검하고 80분에는 안전한 checkpoint를 남긴다. 시간만 채우지 말고 일찍 끝나면 종료한다. 미달을 pass로 바꾸지 않는다.
- 처음부터 정밀 수작업을 전부 하는 추정이 아니다. 선행 공통 도구와 확인된 입력 재사용을 전제로 한다. 같은 실패가 재현되면 같은 접근을 반복하지 말고 한 가지 구체적 대안/필요 입력을 남긴다. 새 번호를 자동 발급하지 않는다.
- 같은 AnatomySceneRoot/renderer/camera, 기존 frame/metre/static pose, 사용자 layer-off/선택을 보존한다. 관찰 시점 메뉴는 되살리지 않으며 화면 맞춤과 선택 맞춤을 사용한다.
- 읽기 전용 원본/OpenSim_Models/T13 drafts/사용자 WIP와 역사 freeze를 보존한다. private 교재·source cache·실패 이력은 learner bundle에 넣지 않는다.
- 관련 unit/data 검사와 변경한 실제 화면만 우선 검증한다. 모든 단계마다 전체 역사 suite를 반복하지 않는다. 코드/필수 data/작은 evidence·보고서의 소유 변경만 로컬 commit한다.
- 상태는 EXECUTION.featureWorkUnits의 해당 AT record만 갱신한다. featurePlans의 nextUnit은 순서/선행을 확인해 갱신하고, 숫자 T queue와 역사 AC 기록은 바꾸지 않는다. sync_execution.py와 --check를 실행한다.
- 보고서에 elapsed time, 완료/미완, 실제 표시 수/근거/검증 범위, commit hash/포함·제외·잔여 변경, 다음 ID/프롬프트를 남긴다. 다음 task 자동 실행·push·배포·진단·치료·침 시뮬레이션 금지.

## 산출물

이 범위의 코드/자료 + work/reports/AT5.md + work/evidence/AT5/. 계획 파일을 실제 artifact로 세지 않는다.

## 붙여 넣을 프롬프트

```text
HUMAN ATLAS에서 AT5만 수행해라.
AGENTS.md, 최신 work/EXECUTION.json, work/tasks/AT5.md,
design/2026-09-25-muscle-atlas/30-AT-361-POINTS-AND-TERRITORIES.md와 지정된 선행 실제 evidence를 읽어라.
범위: 공통 landmark/B-cun/F-cun 규칙 입력→anchor 제안→검증→runtime projection을 만든다. 기술 판정/위치 정밀도/AI 작성 출처/교수 검토/권리를 분리한다. 기존 productInstances의 영구 AI 차단은 근거에 따라 대체하고 schema migration을 만든다.
필수 결과: 의미 있는 랜드마크와 좌우·자세·근거가 확인된 교육용 위치만 local learner eligible로 판정한다. AI 작성 provenance는 지우지 않는다. 단순 bounds 비율/nearest projection/unresolved는 자동 승인하지 않는다. 실패 unit 재개와 원문 보존을 검증한다.
55–80분 규모로 수행하되 최대 80분에는 안전한 checkpoint를 남겨라.
기존 AC1/AC2를 다시 만들지 말고 미확정 혈위를 자동 승인하지 마라.
단일 장면, 원본/OpenSim_Models/T13/사용자 WIP를 보존해라.
관찰 시점 메뉴를 복구하거나 보기옵션을 다시 디자인하지 마라.
관련 검증·실제 화면·report/evidence를 남기고 EXECUTION의 이 AT 상태와 feature plan 다음 ID만 갱신해라.
sync_execution.py 및 --check를 실행하고 소유 변경만 선별 로컬 커밋해라.
미달이면 정확한 남은 unit을 기록하고 완료를 가장하지 마라.
다음은 AT6이며 자동 실행하지 마라. push·배포·진단·치료·침 시뮬레이션 금지.
```
