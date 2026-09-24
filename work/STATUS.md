# 진행 상태 — HUMAN ATLAS

- LAST_UPDATED: 2026-09-25
- CURRENT_PHASE: 전신 범위 정책 및 출처 후보 레지스트리 작성 완료
- CURRENT_TASK: 없음
- NEXT_TASK: T02
- LAST_REPORT: work/reports/T01.md
- SCOPE_REVISION: T01-policy-v1 (전신 부위와 집계 규칙 고정; canonical 전체 목록은 T04에서 작성)
- DATA_REVISION: 없음 (실제 학습 데이터 및 3D asset 미작성/미수집)
- TECHNICAL_GATE: T01 JSON·정책 무결성 검증 통과; 앱 게이트 미실행 (앱 없음)
- ANATOMY_GATE: 미검토 (실제 근육 claim/메시/부착부의 사람 검토 없음)
- ASSESSMENT_GATE: 미검토 (출처 후보만 등록, protocol/임상 타당성 검토 없음)

| task | 상태 | 산출물/보고서 | 차단 조건 |
|---|---|---|---|
| T00 | complete | work/tasks/T00.md; work/reports/T00.md | 없음 |
| T01 | complete | atlas-data/manifests/scope.json; atlas-data/sources/registry.json; work/review-queue/source-gaps.md; work/reports/T01.md | 후속 용어·내용·자산 검토 대기; T01 완료를 막지 않음 |
| T02 | todo | T01 출처 레지스트리의 3D 후보로 우측 종아리 pilot 자산 가용성/권리/형태를 제한 확인 | 정확한 파일 가용성, 파일별 license/mesh/ID 확인 전에는 geometry 지원 주장 금지 |

## 독립적으로 진행할 수 있는 다음 작업

T02가 NEXT_TASK이며 T01 완료를 선행 조건으로 가진다. 먼저 `work/reports/T01.md`와 asset registry/gap queue를 확인한다. T02에서는 whole-body bulk download가 아니라 우측 종아리 pilot의 소량 파일 접근성·표현 ID·license를 조사한다. `OpenSim_Models/`는 읽기 전용 비교 원본이다.

## 변경하지 말아야 할 경로

- OpenSim_Models/: 읽기 전용 원본 checkout, revision d9b05d470b1a481c222372c85b75772faf8f7792
- design/2026-09-25-muscle-atlas/: 설계·템플릿 원본; 구현 완료 증거로 사용하지 않음
- 기존 사용자 파일과 변경: task 시작 전 확인하고 내용·작업 상태를 보존

## 검토 대기

- Korean Anatomical Terminology 6판은 2014 edition 후보만 2차 서지에서 확인됨; 현행 edition·primary file·근육 locator 미확보.
- TA2 2019 edition page/link는 확인했으나 고정판/근육 row locator와 파일 미확보.
- OpenStax·Merck는 교육용 내용/평가 근거의 후보이며 전체 근육·평가 데이터베이스가 아님.
- BodyParts3D LSDB Archive Release 4.0 파일 목록/2025 CC BY 4.0 조건/귀속 문자열을 확인함; actual asset file/hash/pilot coverage 미확인.
- 해부학 claims, 부착 영역/좌표, assessment protocol 및 사람 검토는 미작성.
- T01에서 앱 구현, 다운로드, 자료 변환, 사용자 공개, 임상 적격성 판정을 수행하지 않음.
