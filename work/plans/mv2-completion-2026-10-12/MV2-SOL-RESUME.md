# MV2 Sol 재개 프롬프트

AT22 검증·소유 로컬 커밋 이후 사용한다. 이후 같은 프롬프트에서 완료한 unit은 건너뛰고 다음 한 묶음만 수행한다.

2026-10-12 인수 정정: [인수·재개 규칙](../mv2-at-integrated-2026-10-12/RESUME-OWNERSHIP.md)을 우선 적용한다. Q01 학습 표현과 Q02는 현재 완료 기록이 있다. 아래 기술 지침은 해당 unit을 실제 수행할 때만 적용하며, 완료한 예산 계약/기하 수정/검사를 재실행하지 않는다. 특정 Q03 실행은 [현재 프롬프트](../mv2-at-integrated-2026-10-12/NEXT-MV2-Q03.md)를 사용한다.

```text
HUMAN ATLAS에서 MV2만 재개해라. 담당 Sol xhigh.
목표는 단순 오류 제거를 넘어, 선택한 근육의 작용이 같은 해부 장면에서 이해되는 교육용 움직임이다.

AGENTS.md, 최신 work/EXECUTION.json와 NEXT/STATUS, work/tasks/MV2.md,
work/plans/mv2-completion-2026-10-12/REVIEW-AND-ORDER.md,
design/2026-09-25-muscle-atlas/32-AT6-PLACEMENT-CONTEXT-CAMERA-AND-MOTION-QA.md 4절,
최신 MV2 report와 record가 지정한 repairQueue/remainingUnits,
MV1 2026-10-12-followup-01 summary/원래 inventory 연결,
AT21/AT22 최신 실제 보고서·mask/editor 계약을 읽어라.

work/plans/mv2-at-integrated-2026-10-12/RESUME-OWNERSHIP.md를 적용해라.
AT22 완료 여부는 최신 record/최종 evidence/커밋으로 확인한다. 옛 진행 중 문구로 중단하지 마라.
같은 unit의 미커밋 결과는 diff/hash를 기록하고 인수해 남은 수정·검증·커밋까지 이어가라.
미커밋/최근 시간/동일 HEAD/프로세스 조회 불가만으로 동시 실행을 추정하거나 재승인을 요구하지 마라.
현재 동일 소유 파일을 쓰는 별도 활성 실행이 직접 확인된 경우만 그 충돌 경로의 중복 쓰기를 보류한다.
시작 HEAD/status/hash와 소유 경계를 남기고 AT22 완료 변경을 보존해라.
MV1 미관찰은 0이다. partial/observed_ambiguous/humanReview=not_performed를 미조사나 사용자 승인 대기로 해석해 중단하지 마라.
이를 일괄 pass로 바꾸지도 마라. 바뀐 입력만 재검증하고 MV1 전수 조사·완료한 AT task를 반복하지 마라.

[이번 unit]
첫 실행은 q01-learning-quality다. 기존 Q01 돌출 수정의 engineering pass는 보존한다.
해당 unit이 실제 evidence로 통과했다면 최신 큐의 Q02, 다음 Q03, 이후 고정된 실제 결함 중 다음 한 묶음을 선택한다.
EXECUTION의 기존 nextRepairUnit=Q02는 기술 수리 큐다. 새 요청의 표현 unit을 수행하면 MV2 record에 구분해서 명시한다.
한 묶음 안에서 진단→필요한 수정→검증→앱 연결을 끝내라. 보고서만 반복하거나 다음 묶음을 자동 시작하지 마라.

[q01-learning-quality]
기준은 work/evidence/MV2/2026-10-12-q01-r1/와
atlas-data/assets/motion/mv2-q01-r1-left/motion.glb,
atlas-data/assets/motion/mv2-q01-r1-right/motion.glb,
atlas-data/motion/source-motion-repairs-r1.json이다.
현재 bodyMaxDisplacementMm=0.0은 검사에서 정의한 근복 고정이다.
그 값만으로 틀렸다고 단정하지 말되 돌출 제거만으로 수축 표현 완료라고 하지 마라.
기존 수동 회전/확대/선택 맞춤으로 근육·부착 주변·관절을 함께 보이고 양측을 같은 구도에서 재생해라.
준비/작용/복귀 및 역재생을 실제 시간에 대응시키고, 작용 구간의 길이·경로·윤곽이 설명과 맞는지 확인해라.
표현이 부족하면 source-addressed 부착 영역과 중심 경로에 근거한 국소 변형을 작성해라.
원위부만 움직이고 주요 근복이 고정된 기존 근사로 학습 목표를 충족하는지 구체적으로 판정해라.
색 변화·통째 rigid 이동·전체 scale·임의 부풀리기·각도 축소로 수축 표현을 대신하지 마라.
길이/단면 등은 신뢰 가능한 지표가 있을 때 측정하고 결손 mesh의 가짜 부피를 기준으로 삼지 마라.
이미 충분하다면 실제 작용 구간의 근거를 남기고 불필요하게 geometry를 바꾸지 마라.

[공통 구현]
frame/side/topology, attachment 역할, pivot, weights, 보간, 접촉 보정을 분리해 진단한다.
복잡한 변형은 offline에서 작성하고 runtime은 검증된 morph/clip을 재생한다.
기존 authoring·sourceMotionRepairs·loader를 재사용하고 새 엔진/별도 viewer/근육별 runtime 분기를 늘리지 마라.
Q01 vertex 번호·world-Y mask를 다른 근육에 복사하지 마라. 필요한 공통 부분만 parameter로 추출해라.
새 수정본은 원본에 대한 명확한 교체 항목으로 등록하고 patch chain을 만들지 마라.
이전 morph buffer 누적을 피하며 compact export 시 실제 replay 동등성을 검증해라.

[Q02에 들어갈 때]
기존 trunk GLB는 31,306,820 bytes다. motionAssets.ts의 기존 자산 예외와
sourceMotionRepairs.ts/plugin의 새 repair 8MiB 제한이 충돌한다.
기존 exact source에 연결되는 공통 예산 계약으로 resolver/delivery를 일치시키는 최소 수정을 해라.
승인된 예산 안의 미사용 buffer 정리 등을 먼저 확인한다.
범용 상한 완화·무관 자산 허용·필수 주변 구조 삭제로 통과시키지 마라.
예산 변경이 실제 필요하면 증가 원인·전후 비용을 기록해 좁은 source-bound 결정으로 처리해라.
이 Q02 작업을 첫 q01-learning-quality에 섞어 선행 구현하지 마라.

[필수 인수 검사]
최종 emitted GLB를 실제 앱 loader와 기존 scene/root/renderer에서 재생해라.
rest/준비/작용 중간/최대/복귀, 변화가 큰 keyframe 사이, 양측, 반복,
빠른 중단/재시작/다른 근육 선택, 원본 geometry/선택/레이어 복귀를 확인해라.
기존 부착/면 뒤집힘/면적/접촉 기준을 유지한다. contained vertex 0을 모든 교차 부재로 확대하지 마라.
수치 통과와 실제 1배속 시각 판독을 별도로 남기고 의심 구간은 느리게 재생해라.
Q01 돌출 수정과 무관한 대흉근 등 비교 대상을 회귀 확인하되 같은 원인이라고 가정하지 마라.
움직임 종료→경혈 점/AT21 면→닫기 및 AT22 검토 종료의 원본 복원을 확인해라.
정지 pose의 경혈 좌표를 변형 pose에 그대로 노출하지 마라.
실제 bytes/geometry 배열/draw·지연 로딩·해제 before/after와 관련 tests/typecheck/build를 남겨라.
큰 evidence·실패 후보·전체 authoring ledger는 learner bundle에 넣지 마라.

[UI·기록·종료]
제품 카메라 거리·자동 회전·전환 연출·레이아웃·보기옵션은 이후 UI 개선이다. 기존 동작을 보존한다.
검사용 수동 맞춤은 허용한다. 국소 관찰에서도 판단이 안 되면 unresolved와 빠진 근거를 남겨라.
정상 변형은 확인됐고 자동 framing만 부족할 때에만 presentation_deferred_to_ui로 분리해라.
기술 통과/학습 표현 통과/UI 보류/선택적 human review를 구분한다.
교수 승인·생체역학 인증을 새 필수 종료 조건으로 만들지 마라.

work/reports/MV2.md에 실제 결과를 추가하고 work/evidence/MV2/ 새 versioned 폴더에 입력·전후·검증·큐를 남겨라.
이번 unit acceptance와 MV2 전체 remaining을 분리한다. 실제 해결 범위만 완료 처리해라.
원본/OpenSim_Models/T13/AT20–22/사용자 WIP/역사 freeze를 보존한다.
최신 EXECUTION을 다시 읽고 MV2 record와 해당 motion plan만 갱신한다. AT record/다른 실행자 변경을 덮지 마라.
sync_execution.py 및 --check 후 소유 변경만 선별 로컬 커밋해라.
해시·포함/제외·잔여 변경·다음 한 unit과 붙여 넣을 프롬프트를 남기고 멈춰라.
시간 경과로 중단하거나 새 task ID를 발급하지 마라.
자동 위임·다음 unit/AT 실행·push·배포·진단·치료·침 시뮬레이션 금지.
```
