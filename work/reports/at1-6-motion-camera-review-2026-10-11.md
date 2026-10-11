# AT1–6 구현 검토와 후속 교정

2026-10-11. 검토·명세 수정 완료이며 AT6 실제 위치 구현, AT7 카메라 코드, MV1 전수 조사/MV2 변형 수정은 실행하지 않았다. 다음 AT는 AT6 재개 그대로다.

## 결론

AT1–5의 원장/공통 표면/자료 compiler는 재사용할 가치가 있다. 단일 scene, lazy loading, 명시적 좌표계/side, 원본 보존 구조는 유지한다. 그러나 기술 인프라의 완료와 학생이 볼 수 있는 위치의 완료가 분리되어 AT6에서는 22개 카드에 실제 점 0개가 연결됐다. 단순 승인 정책 문제가 아니라 실제 모델 annotation·표면 연결을 만드는 작업이 부족한 설계/구현 공백이다. 전체 피부를 재제작하거나 다음 경맥 입력으로 넘어가기 전에 첫 실제 위치를 연결해야 한다.

AT6 report와 validation은 acceptancePassed=false를 명확히 기록했고 EXECUTION도 partial/nextUnit=AT6다. 이것은 부분 승인이나 완료가 아니다. 검사 47개 통과는 당시 기술 검사이며 22개 실제 위치 합격을 뜻하지 않는다. 이번 관련 acupoints test glob 재실행은 별도의 **41/41 통과**다. 과거 47개 전체 suite를 재실행했다고 주장하지 않는다.

## 확인 자료

- AT1–6 report, EXECUTION records, AT6 validation/learner data/코드, AT3/4 실제 생성 범위, AT5 compiler/policy, 공통 overlay/tour/card 연결을 읽었다.
- 실제 learner lung.json projections=[]; 11개 명칭·양측 22개 unavailable와 AT6 기록 일치.
- localhost 5183에서 경혈→LU9를 실제 선택했다. 0/11 표시와 위치 미지원 안내, 카메라가 점에 맞춰지지 않는 흐름을 확인했다. 캡처: `work/evidence/at6-motion-camera-review-2026-10-11/learner-LU9.png`.
- 동일 앱에서 오른쪽 대퇴직근 source route, 무릎 폄/고관절 굽힘 선택, 실제 무릎 asset의 재생 및 slider 0/50/100을 확인했다. 사용자 첨부의 정확한 순간/시점을 재현 완료한 것은 아니다. 대흉근과 다른 근육의 전수 재생은 수행하지 않았다.
- 공통 변형은 pivot/axis/vertex weight 기반 blend/rotation와 접촉/ARAP/morph 보정이다. 수축의 물리적 정확성 검증이 아니다. 돌출의 단일 원인은 MV1에서 asset/phase 단위로 구분해야 한다.
- motion-learning working tree: 1,166 action rows, 1,160 asset rows, 고유 URI/hash 46개. 실제 46개 GLB hash 모두 등록과 일치. status는 1,159 binding_verified/1 candidate. delivery index는 74개. 이 수는 실제 learner 도달 가능 clip 분모나 자연스러운 변형 합격 수가 아니다.

## 수정한 계획

[32 설계](../../design/2026-09-25-muscle-atlas/32-AT6-PLACEMENT-CONTEXT-CAMERA-AND-MOTION-QA.md)에 상세 결론·작업 방법·인수 기준을 남겼다.

1. AT6: 실제 구조를 읽어 모형용 landmark annotation을 작성하고 필요한 손목 등 국소 carrier를 보완한다. 원본 관찰과 AI 모형 지표를 분리한다. 첫 실제 compiler→learner 연결 후 22개로 확장한다. 허위 좌표/승인·전체 gate 해제는 허용하지 않는다.
2. AT7: 경혈 점들만의 Box3/고정 거리를 대신할 context bounds를 정의했다. 주변 근육·힘줄과 뼈/관절의 국소 구간, 실제 패널 가림과 fov/aspect로 중간 거리 framing을 계산한다. 카드/검색/3D 클릭의 호출을 통일한다. 화면 안의 작은 점이라는 이유만으로 전신샷을 유지하지 않는다.
3. MV1 Luna Max: 실제 재생 분모 동결 → 고유 자산/clip/변환/재생 매핑 중복 제거 → 전수 자동+시각 검사 → 원인별 queue. 조사 도구/evidence만 소유한다.
4. MV2 Sol High: 고정 queue의 우선 공통 원인 묶음 하나 → 대표 사례 원인 수정 → 영향 자산 일괄 재생성 → 최종 GLB/runtime 회귀. 남은 원인은 같은 queue에서 이어간다. 원인마다 새 번호를 만들지 않는다.

현재 AT 순서는 바꾸지 않았다. AT1–5 완료, AT6 재개라는 최신 안내로 START-HERE의 오래된 AT2 진행 문구를 교정했다. 전체 경혈 UI 디자인/보기옵션 변경은 보류했다. 31 설계와 AT6/AT7 task prompt에 새 기준을 연결했다. MV1/MV2 planned record만 추가했고 AT6 acceptance/partial·기존 feature plan order/nextUnit은 보존했다.

## 검증

- 기존 tracked WIP 45개 hash 모두 보존, 원본/OpenSim_Models/T13/기존 자산에 쓰기 없음.
- 46개 motion 파일 실제 hash 일치, 등록 중복 집계와 새로운 조사 분모 구분.
- acupoints tests 41/41. 첫 strip-only 실행은 기존 TS parameter property를 지원하지 않아 실패했고 cwd를 바꿔도 같았다. --experimental-transform-types로 정상 실행했다. 코드 수정 없이 해결했으며 세 로그를 보존했다.
- 계획 링크/상태/소유 범위/실제 learner 배열 대조 8개 검사 통과.
- sync_execution.py Updated 0 및 --check 통과. 현재 sync는 숫자 T projection이며 feature plan은 EXECUTION의 해당 항목에서 읽는다.
- runtime 수정이 없어 신규 build나 전체 motion 품질 합격을 주장하지 않는다.

## 인계·Git

[AT6 재개](../plans/at6-motion-camera-review-2026-10-11/AT6-RESUME.md) · [AT7 카메라](../plans/at6-motion-camera-review-2026-10-11/AT7-CAMERA.md) · [Luna 전수 조사](../plans/at6-motion-camera-review-2026-10-11/MV1-LUNA-AUDIT.md) · [Sol 수정](../plans/at6-motion-camera-review-2026-10-11/MV2-SOL-REPAIR.md).

이 보고서, 설계/명세/프롬프트, 해당 EXECUTION 계획 변경, 작은 검사/화면 evidence만 로컬 커밋한다. 기존 motion 관련 사용자 WIP를 포함하지 않는다. 최종 hash는 Git 이력과 응답에 기록한다. 다음 task 자동 실행·다른 대화 메시지 전송·push·배포 없음.
