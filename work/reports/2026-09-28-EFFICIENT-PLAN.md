# 실행 계획 효율화 — 사용자 재검토 요청

2026-09-28 · Astra · 계획 정정만 수행. Goal: 기존 계획을 압축하고 제품 완료/중단·성능 기준을 현행 프롬프트와 일치시킨 뒤 소유 변경 커밋. 새로운 앱 기능·task 구현은 시작하지 않음.

## 판단과 변경

T78의 잠정556후보를10개 단위마다 별도 task로 만들어 T110–165까지 미리 발급한 것은 과도했다. 10개 검증 단위와 사용자 실행 task는 다르다. T165는 구조 식별/이름/선택의 마지막 batch였으며 전체 기시정지/기능/모션/신경 완성 번호가 아니었다.

- **새 번호0개**, 구조 확장 활성 작업72→28. T122–165의44개 미실행 계획은 superseded_not_executed, 활성 queue 제외. 원래 문서/대상 목록은 삭제하지 않았다.
- T110–121을12부위 package로 재편. exact target 배정은 앞당긴 T96의 의미 검증/freeze가 필요하며 아직 수행하지 않았다. 모든 후보의 유지/제외/병합 근거와 주 담당1개/여러 제품 지역 소속을 검증해야 한다.
- T95→T96→T79→T97→T101–107→T98–100→T108–109→T110–121→T80→T58. 알려진70source gap의exact 취득 범위와 광배근4gate는 유지.
- 이후 기시정지/기능/신경 내용 단계도 최대10개 검증 workUnits와 package progress manifest를 사용하고 같은 task로 재개한다. 새로운10개마다 새 정수번호를 발급하는 지시는 폐기했다. 다른 모델/공유계약 등 실제 위험 분리가 필요한 때에만 근거·완료조건을 갖춘 추가 작업을 제안한다.
- task 수 대신 제품 단계(구조/설명/움직임/신경)와 실제 target coverage/품질로 완료를 판단한다. 전체 평가와 경혈은 기존 deferred 범위. 이후 작업이 절대로 추가되지 않는다는 보장은 하지 않는다.

## 코드·성능 검토 반영

현재 코드 확인: AnatomySceneController의 단일 scene/renderer/camera, ResourceQueue 동시2개/요청 취소·늦은 응답 해제, 필요 부위 chunk demand, DPR1.75상한, dirty draw 유지. loaded cache는 scene 종료까지 보유하므로 자산 증가에 따른 보유량 증가는 검토 대상이다. idle일 때 draw 생략과 loop callback 중지는 구별했다.

T77 manifest30chunks/68,126,860bytes 및 T58 역사 측정/검토 상한을 참고했다. 새로운 성능 측정을 했다고 주장하지 않는다. 22 설계에 공통 엔진/카드/로더 재사용, offline evidence/runtime 분리, data-only 기본 app 변경0, 관련 검사 선택, cold/warm 구별, 전후 bytes/triangles/draw calls/p95,20회 전환 resource 안정성, 실제 모바일 여부, 예산 초과와20%악화 검토 규칙을 추가했다. 근육을 숨기거나 선택 ID를 잃는 최적화 금지. GPU 전체메모리 미측정은 null.

## 검증·Git

`python3 work/evidence/2026-09-28-efficient-plan/validate.py`: **17/17**, exit0. `git diff --check`: 통과.

활성28/폐기44/신규ID0, source70scope 보존, 광배근gate, 선행/next/전체gate, 미래 planned 상태, T78 보고서/evidence불변, app/runtime 변경0, source-cache650파일과 OpenSim HEAD/clean 보존을 검사했다. 앱 코드를 바꾸지 않았으므로 브라우저/build/typecheck를 재실행하지 않았다.

시작 HEAD4bc83fdd974d1e3f32c64932d56268699a3e78c9. 기존70개 WIP를 보존한다. 소유 설계/미실행 task 명세/queue/프롬프트/검증/보고서만 로컬 커밋한다. 혼합 STATUS와 untracked R15 registry는 작업본을 갱신하고 소유 delta만 커밋한다. OpenSim/기존 source cache/비공개 자료/사용자 코드/전체 혼합 registry는 제외. push·배포 없음. 실제 커밋 해시는 종료 응답에 기록한다.

## 다음

T95 Luna Max만. `work/evidence/2026-09-28-efficient-plan/NEXT-T95.md`와 `PROMPTS-IN-ORDER.md`를 사용한다. 구현을 실행하지 않았으며 이번 Goal은 계획 확정 후 종료한다.
