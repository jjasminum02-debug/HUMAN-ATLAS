# MV2 — 공통 원인별 근육 변형 수정

현재 상태는 EXECUTION의 MV2 record와 실제 보고서를 따른다. 후속 핵심 수정 담당 Sol xhigh.

## 2026-10-12 재개 정정 — 기존 작업 인수

[인수·재개 규칙](../plans/mv2-at-integrated-2026-10-12/RESUME-OWNERSHIP.md)을 먼저 적용한다. 미커밋 결과·최근 evidence·동일 HEAD·프로세스 목록 확인 불가는 다른 실행자가 현재 작업 중이라는 증거가 아니다. 재개 요청은 같은 unit의 기존 WIP 검토·인수·검증·소유 커밋을 포함한다. 실제 동시 실행/충돌이 확인되지 않으면 같은 승인 질문 없이 이어간다. 무관한 사용자 변경과 원본은 보존한다.

확인된 Q02 완료 커밋은 `5b51ff627ea048ee4d0c0f9e526a46268d96d094`이며 다음은 Q03이다. [Q03 현재 프롬프트](../plans/mv2-at-integrated-2026-10-12/NEXT-MV2-Q03.md)를 사용한다. 아래 q01/Q02 대기 문구는 작성 당시 상태이며, 최신 EXECUTION·최종 evidence·커밋을 대신하지 않는다. 이 문서 수정은 MV2 구현/검증 재실행이나 새 acceptance가 아니다.

## 2026-10-12 사용자 후속 요청 — 작용 표현의 완결성

Q01 좌우 돌출 수정은 engineering acceptance를 통과했고, 전체 MV2는 Q02–Q05 4묶음·32매핑이 남아 partial이다. 역사 Q01 통과를 취소하거나 MV1 전수 조사를 반복하지 않는다.

사용자는 오류 제거를 넘어 수축·작용이 이해되는 그래픽을 요청했다. 다음 명시적 실행에서는 **q01-learning-quality**로 기존 수정본의 학습 표현을 검증·필요시 보완하고, 그 뒤 최신 큐의 다음 한 묶음을 처리한다. 이것은 기존 Q01 결함 수리의 재실행이 아니라 새 표현 인수 기준이다. EXECUTION의 기존 nextRepairUnit=Q02는 보존하며, 다음 실행자가 새 unit과 실제 결과를 MV2 record에 명시한다. 계획 작성만으로 상태를 승격하지 않는다.

- [현재 검토·실행 순서](../plans/mv2-completion-2026-10-12/REVIEW-AND-ORDER.md)
- [현재 Sol 재개 프롬프트](../plans/mv2-completion-2026-10-12/MV2-SOL-RESUME.md)
- [고정 검사 인계 후 사용할 Luna 프롬프트](../plans/mv2-completion-2026-10-12/MV2-LUNA-VERIFY.md)

AT22 종료·검증·소유 커밋 이후에 수행한다. 카메라 거리·자동 이동·연출과 UI 개편은 사용자가 미룬 후속 UI 작업이다. 기존 동작은 보존하고 검사용 수동 회전/확대는 허용한다. 새 task ID를 만들지 않는다.

아래 기존 프롬프트는 역사 범위 참고다. **재개에는 위 현재 Sol 프롬프트를 우선 사용한다.** 공통 보존·검증 규칙은 유지한다.

설계: [32-AT6-PLACEMENT-CONTEXT-CAMERA-AND-MOTION-QA.md](../../design/2026-09-25-muscle-atlas/32-AT6-PLACEMENT-CONTEXT-CAMERA-AND-MOTION-QA.md)

```text
HUMAN ATLAS에서 MV2만 수행해라. 담당 Sol High.
AGENTS.md, 최신 EXECUTION, work/tasks/MV2.md, design/2026-09-25-muscle-atlas/32-AT6-PLACEMENT-CONTEXT-CAMERA-AND-MOTION-QA.md 4절,
MV1 report/inventory/defects/repair-queue와 지정 실제 GLB/hash/authoring/runtime evidence를 읽어라.
queue에서 가장 우선인 공통 원인 묶음 하나를 선택하고 영향 파일·재현 사례를 고정해라. MV1 미실행이면 조사 완료라고 가정하지 마라.
대퇴직근과 대흉근의 문제가 같은 원인인지부터 검증해라. 변형 가중치/endpoint·pivot·좌표계·접촉 보정·morph 보간·역재생 매핑을 분리해서 확인해라.
대표 사례에서 최소 원인 수정을 한 뒤 같은 원인에 해당하는 자산만 공통 경로로 재생성하고 회귀 검사해라.
전체 mesh scale, 투명화/숨김, 검증 임계값 완화, 각도 축소만으로 결함을 감추지 마라. 무관한 새 엔진으로 전면 교체하지 마라.
최종 emitted GLB를 실제 loader/동일 장면에서 재생해 부착/주변 구조/모든 중간 자세/양측/원상복귀와 전후 화면을 검증해라.
수정한 원인 묶음, 영향을 받은 모든 runtime 참조, 남은 별개 원인을 repair queue에 기록해라. 해결한 일부를 전체 완료라고 하지 마라.
work/reports/MV2.md 및 work/evidence/MV2/ 아래 versioned 실행 결과를 남겨라. 이후 재개는 최신 queue와 변경된 hash만 읽고 같은 조사를 반복하지 마라.
시작 HEAD/status/hash와 소유 경계를 남겨라. 원본/OpenSim_Models/T13 drafts/기존 사용자 WIP를 보존해라.
기존 증거/원본을 덮지 말고 versioned 결과를 남겨라. 관련 검사와 실제 화면, 보고서/evidence를 작성해라.
최신 EXECUTION을 다시 읽고 해당 record만 갱신하며 sync_execution.py 및 --check를 수행해라.
소유 변경만 선별 로컬 커밋하고 hash·포함/제외·잔여 변경·다음 프롬프트를 남겨라.
시간 경과를 종료 조건으로 쓰지 말고 합격 기준과 실제 남은 unit으로 판단해라.
다음 작업 자동 실행·위임·push·배포·진단·치료·침 시뮬레이션 금지.
남은 묶음이 있으면 다음은 같은 MV2의 명시된 다음 unit이며, 모두 해결되면 종료하고 사용자 요청을 기다려라.
```
