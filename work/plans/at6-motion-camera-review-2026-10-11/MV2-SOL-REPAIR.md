# MV2-SOL-REPAIR 실행 프롬프트

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
