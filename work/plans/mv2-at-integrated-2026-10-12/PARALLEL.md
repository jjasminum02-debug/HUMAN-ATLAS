# 병렬로 해도 되는 범위

사용자가 병렬 작업을 선택했을 때 쓰는 인계 계약이다. 이 문서 작성만으로 worker를 시작하거나 다른 대화에 메시지를 보내지 않는다. 새 task 번호는 없다.

## 권장 조합

| 시점 | 통합/수정 담당 | 병렬로 가능한 Luna 작업 | 합류 조건 |
|---|---|---|---|
| 현재 q01 종료 후 | Sol xhigh: MV2 Q02, 이어서 별도 요청의 Q03 | MV2 Q04/Q05 고정 입력 검증; 또는 AT8 문헌·명칭·위치 규칙 후보 | stable snapshot과 실제 GLB hash가 고정돼야 함. 라이브 앱 QA는 독점 또는 별도 고정 서버 |
| AT8 공통 계약 완료 후 | 각 AT 통합 담당 1명 | AT9+AT10, 다음 AT11+AT12, AT13+AT14, AT15+AT16, AT17+AT18의 후보 자료를 각각 작성 | 서로 다른 task 소유 output, 공유 carrier 읽기 전용. 병렬 작성 순서는 통합 순서/완료 판정을 바꾸지 않음 |
| AT23 mask 계약 완료 후 | Sol/Luna: 최신 공식 순서의 한 task 통합 | AT24와 AT25 경계 자료·mask 후보 | 공통 mask schema/carrier topology가 고정, 같은 면을 공유해도 각 mask file은 독립 |
| AT26 작업 중 | Sol: AT26 | AT27 교재 importer 입력 형식/제공 자료 대조 후보 | private 자료는 local, runtime/카드는 단독 통합 |

상위 task를 동시에 완료시키는 지시가 아니다. 한 요청에서는 지정 task의 후보 또는 통합만 수행한다. 서로 다른 기존 대화에 아래 프롬프트를 각각 넣는 방법으로 사용할 수 있다.

## 충돌을 막는 최소 계약

1. 작업 시작 시 통합자가 `work/evidence/<TASK>/<version>/assignment.json`에 base commit, 실제 읽는 파일 path/hash, 배정 code+side 또는 source/clip/role, owned output, 공통 계약 revision을 기록한다. 이미 적합한 고정 큐/manifest가 있으면 재사용한다. task 번호를 새로 만들지 않는다.
2. 같은 task worker끼리는 배정 집합이 겹치지 않아야 한다. worker 출력은 `work/evidence/<TASK>/<version>/workers/<name>/` 한 경로다. 조사 결과에는 근거·실제 좌표 주소·검증 결과를 함께 둔다. runtime/공통 registry·상태·최종 보고서·기존 원본에는 쓰지 않는다.
3. worker는 공통 Git index에 stage/commit하지 않는다. 산출물은 보존하고 통합자가 소유 파일만 검토해 로컬 commit한다. 다른 사람의 staging을 취소하거나 stash/reset하지 않는다.
4. 공유 runtime 변경 중인 서버로 측정하지 않는다. 고정 snapshot의 별도 검증 서버·탭을 사용하거나 통합자가 앱 QA를 직렬 수행한다. 앱의 camera/선택은 세션 상태이므로 같은 탭을 두 사람이 조작하면 안 된다.
5. build/typecheck가 출력·캐시를 쓰는 도구라면 worker 소유 출력 위치로 분리한다. 대용량 GLB 내보내기·브라우저 QA를 여러 개 동시에 돌려 메모리를 소모하지 않는다. 병렬 후보 작업은 기본 2개 이하다.
6. 입력이 바뀌면 해당 산출물만 stale로 기록하고 영향을 받은 항목을 다시 계산한다. 자동 전체 재시작 금지. 통합 시 base commit이 달라도 실제 입력 hash/계약이 같다면 그 근거로 재사용할 수 있다.
7. 통합자는 worker의 결과를 정답으로 간주하지 않는다. code/side 중복·부재·hash·frame·권리·가용성 및 실제 앱을 검증한 뒤 해당 task record만 갱신한다. 선행 partial과 본 task acceptance를 구분한다.

## AT 자료 후보 worker 프롬프트

아래 `<TASK>`와 `<WORKER>`를 실제 배정값으로 바꾼다. assignment가 아직 없다면 후보 담당자가 최신 task에서 **자신의 대상 전체와 입력 hash만** 먼저 고정할 수 있다. 다른 worker 배정이나 product 계약 변경 권한은 없다. 그 결과를 통합자가 검토한다.

```text
HUMAN ATLAS에서 <TASK>의 자료 후보 준비만 수행해라. 담당 Luna Max, worker <WORKER>.
work/plans/mv2-at-integrated-2026-10-12/START-HERE.md와 PARALLEL.md,
AGENTS.md, 최신 EXECUTION의 해당 record, work/tasks/<TASK>.md, 지정 자료와 현재 공통 schema/compiler를 읽어라.
이 task 전체 통합·완료 처리가 아니라 후보 준비다. 배정 code/side와 입력 hash를 먼저 고정해라.
이미 검증된 자료를 재사용하고 해당 경맥의 위치 규칙·해부 지표·구간 경로 또는 영역 경계만 대조해라.
새 자료 조사는 공식/학술/제공 교재 근거를 확인하고 원문·AI 해석·모델 근사를 분리해라.
적용 가능한 native 구조/triangle 주소를 확인하되 없으면 구체적인 누락 지표/표면과 대안을 기록해라.
이름 후보를 위치 확정으로, 그림의 폭을 치료 범위로, 반대쪽 복사를 좌우 검증으로 취급하지 마라.
현재 compiler로 처리 가능한 입력은 소유 출력 폴더에서 일괄 검사하고 실패한 항목만 정리해라.
공통 알고리즘/geometry 변경이 필요하면 재현 입력과 최소 변경 제안으로 통합자에게 넘겨라.
공유 runtime/atlas-data 등록/공통 carrier/EXECUTION/STATUS/최종 report/Git index를 수정하지 마라.
산출물·hash·검사·미완·인계는 배정된 work/evidence/<TASK>/<version>/workers/<WORKER>/에만 남겨라.
고정된 검증 서버가 없으면 실행 중인 다른 작업의 앱/브라우저를 조작하지 마라.
카메라 정책·UI 개편·stage/commit·push·배포·다음 task·자동 위임은 하지 말고 멈춰라.
```

## MV2 Q04/Q05 병렬 검증 worker 프롬프트

직렬 Luna 검증 프롬프트에는 EXECUTION·report·commit 갱신이 있으므로 **병렬에서는 그대로 쓰면 안 된다.** 다음 프롬프트를 쓴다.

```text
HUMAN ATLAS에서 MV2 Q04/Q05의 고정 입력 검증 후보만 수행해라. 담당 Luna Max.
work/plans/mv2-at-integrated-2026-10-12/START-HERE.md와 PARALLEL.md,
work/tasks/MV2.md, 최신 MV2 큐/실제 evidence와 Sol이 고정한 검사 도구/입력 hash를 읽어라.
이미 해결한 매핑은 제외한다. 원래 Q04 26매핑/Q05 2매핑을 최신 큐와 대조해 대상 manifest를 남겨라.
실제 emitted GLB/clip/side/role과 최종 runtime 연결을 확인해라.
기존 수동 확대/회전으로 근육·부착 주변·관절을 함께 보며 준비/작용/중간/복귀를 판독해라.
고정 기준 서버와 별도 탭에서만 실제 앱 QA를 해라. 다른 실행자가 쓰는 mutable 서버/탭을 공유하지 마라.
고정 서버를 쓸 수 없으면 offline 검사를 먼저 끝내고 browser pending 항목을 직렬 통합자로 넘겨라.
고정 검사와 실제 시각 판독을 분리하고 pass/geometry_or_playback_defect/
presentation_deferred_to_ui/observed_ambiguous로 각각 판정해라.
정상 변형을 실제 확인하지 않고 UI 문제로 분류하지 마라.
새 geometry/weights/pivot/repair manifest/runtime/UI/camera/최종 보고서/EXECUTION을 수정하지 마라.
배정된 work/evidence/MV2/<version>/workers/<name>/에 입력·결과·재현·인계만 남겨라.
stage/commit·자동 다음 실행·위임·push·배포는 하지 말고 멈춰라.
```

## 병렬 후보를 받는 통합 프롬프트 추가문

해당 AT 또는 MV2 실행 프롬프트 끝에 붙인다. task/묶음은 원래 요청의 하나를 유지한다.

```text
이번 task의 worker 후보가 있으면 assignment와 입력 hash를 대조하고 재사용해라.
다른 task 후보까지 통합하지 마라. worker 파일을 무조건 승인하지 말고 실제 입력·공통 검사·앱 동작으로 확인해라.
runtime/schema/learner 등록/최종 report/EXECUTION/Git index의 유일한 writer는 너다.
앞선 worker의 browser pending과 영향받은 사례를 실제 앱에서 마무리해라.
동일 검증을 처음부터 반복하지 말고 변경된 입력·실제 예외만 재검사해라.
후보 준비 완료 수와 learner에 실제 통합·검증된 수를 따로 보고해라.
```
