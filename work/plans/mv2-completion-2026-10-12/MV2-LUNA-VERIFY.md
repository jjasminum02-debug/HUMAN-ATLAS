# MV2 Luna 검증 프롬프트

Sol이 고정된 검사 도구·기대 형태·입력 인계를 남긴 뒤 사용한다. 핵심 변형 설계를 Luna로 바꾸는 지시가 아니다. 새 task 번호 없이 MV2 내부 검증 unit이다.

```text
HUMAN ATLAS에서 MV2의 Q04/Q05 국소 관찰·회귀 검증 unit만 수행해라. 담당 Luna Max.
AGENTS.md, 최신 EXECUTION의 MV2와 report/repairQueue,
work/plans/mv2-completion-2026-10-12/REVIEW-AND-ORDER.md,
Sol이 남긴 검사 도구·기대 형태·입력 hash·완료 기준을 읽어라.
work/plans/mv2-at-integrated-2026-10-12/RESUME-OWNERSHIP.md를 적용한다.
최신 완료 기록을 확인하고 이번 검증 unit의 기존 WIP는 diff/hash를 기록해 인수한다.
미커밋/최근 evidence/동일 HEAD/프로세스 조회 불가만으로 중단하지 마라.
실제 동일 소유 파일의 별도 활성 writer가 확인된 경우만 충돌을 피한다. 병렬 후보 모드에서는 그 별도 소유 경계를 유지한다.

대상은 최신 큐의 Q04 손 말단 26매핑과 Q05 깊은 몸통 2매핑이다.
이미 해결된 매핑은 최신 evidence로 제외하고 전신을 다시 조사하지 마라.
공통 검사 절차가 없으면 재사용 가능한 MV1 capture 도구와 기존 수동 맞춤으로 실제 재현 절차를 고정해라.
새 geometry 설계나 변형 알고리즘을 추정해서 만들지 마라.
기존 수동 확대/회전/선택 맞춤으로 근육·부착 주변·관절을 함께 보이게 해라.
전신 화면에서 작아서 안 보인다는 이유만으로 끝내지 마라.
actual GLB/clip/side/role을 확인하고 준비→작용→복귀를 1배속과 필요한 느린 재생으로 판독해라.
같은 도구로 반복 캡처·hash·복귀 검사를 처리하고 동일 자산을 무의미하게 중복 조사하지 마라.
수치 0 또는 파일 존재만으로 시각 판독을 대체하지 마라.

각 매핑을 구분해 기록한다:
- engineering_and_learning_visual_pass: 고정된 검사와 국소 시각 판독 통과.
- geometry_or_playback_defect: 실제 변형/시간/부착/복귀 결함. GLB/hash/시점/구도/기대와 관찰을 기록해 Sol에 인계.
- presentation_deferred_to_ui: 변형은 확인됐고 자동 framing/대비/배치만 부족. 제품 UI 변경 없이 backlog 기록.
- observed_ambiguous: 충분한 국소 관찰 후에도 판단 근거 부족. 빠진 근거와 재현을 기록.

Q01–Q03 완료 입력을 보존하고 카메라 정책·레이아웃·보기옵션을 수정하지 마라.
authoring/weights/pivot/frame/GLB/수리 manifest를 직접 변경하지 마라.
조사 도구의 작은 개선, evidence/큐의 해당 unit 판정만 소유한다.
교수 검토 미수행을 이유로 교육용 검사를 중단하거나 정상으로 추정하지 마라.
versioned report/evidence, 실제 판독 수·오류 수, Sol 인계와 다음 unit을 남겨라.
최신 EXECUTION의 MV2 관련 기록만 갱신하고 sync_execution.py 및 --check 후 소유 변경만 로컬 커밋해라.
원본/OpenSim_Models/T13/AT20–22/사용자 WIP/역사 evidence를 보존한다.
다음 작업 자동 실행·새 task ID·위임·push·배포·진단·치료·침 시뮬레이션 금지.
```
