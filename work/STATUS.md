# 진행 상태 — HUMAN ATLAS

- LAST_UPDATED: 2026-09-25
- CURRENT_PHASE: 공통 해부학 데이터 계약 및 검증 기반 완료
- CURRENT_TASK: 없음 (T03 완료; 다음 단계는 T04)
- NEXT_TASK: T04 — 전체 근육 목록과 언어 정책
- LAST_REPORT: work/reports/T03.md
- SCOPE_REVISION: T01-policy-v1 (전신 부위와 집계 규칙 고정; canonical 전체 목록은 T04에서 작성)
- DATA_REVISION: T02-BodyParts3D-R4-calf-pilot-v1 (11개 원본 OBJ 후보 및 manifest; 공개/학습 승인 아님)
- SCHEMA_REVISION: T03-atlas-schema-v1 (Draft 2020-12 schema + project validator; synthetic fixtures only)
- TECHNICAL_GATE: T03 schema, cross-reference, coordinate conversion, review hash, evidence and learning-manifest validator passed 17 synthetic fixtures. 앱·실제 학습 데이터는 아직 없음.
- ANATOMY_GATE: 미검토 (실제 근육 claim/mesh/부착부의 사람 검토 없음)
- ASSESSMENT_GATE: 미검토 (protocol/임상 타당성 검토 없음)

| task | 상태 | 산출물/보고서 | 차단 조건 |
|---|---|---|---|
| T00 | complete | work/tasks/T00.md; work/reports/T00.md | 없음 |
| T01 | complete | atlas-data/manifests/scope.json; atlas-data/sources/registry.json; work/review-queue/source-gaps.md; work/reports/T01.md | 후속 용어·내용·자산 검토 대기; T01 완료를 막지 않음 |
| T02 | complete | `atlas-data/manifests/assets.json`; 11 mesh subset; `work/evidence/T02/`; `work/reports/T02.md` | 해부학자 리뷰 및 공개 전 license 재확인은 후속 게이트 |
| T03 | complete | `atlas-data/schemas/`; `work/evidence/T03/`; `work/reports/T03.md` | reviewer 신원 인증은 별도 시스템 필요 |
| T04 | not_started | 전체 근육 목록, region tree, 용어 정책 및 source crosswalk | 기준 판본의 실제 항목 locator 미확보 상태를 task 안에서 표시 |

## 다음 직렬 작업

다음은 **T04 — 전체 근육 목록과 언어 정책**이다. `design/2026-09-25-muscle-atlas/03-LUNA-SERIAL-RUNBOOK.md`의 T04와 01/02/04 설계, T01 범위 정책 및 `work/review-queue/source-gaps.md`, T03 스키마/검증 결과를 읽는다. 접근 가능한 정확한 표준 판본에서 항목 목록과 locator를 추적하고 확보하지 못한 이름·판본·항목은 미확인으로 남긴다. 실제 근육별 주장/기시·정지 본문(T05), 앱, 전체 메시 다운로드, 공개, 진단·치료·침 시뮬레이션은 이 작업에서 시작하지 않는다.

## 변경하지 말아야 할 경로

- `OpenSim_Models/`: 읽기 전용 원본 checkout, revision `d9b05d470b1a481c222372c85b75772faf8f7792`; T03에서도 변경하지 않음
- `design/2026-09-25-muscle-atlas/`: 설계·템플릿 원본; 기존 SHA-256 대조 결과 변경 없음
- 기존 사용자 파일과 지침: T03 시작 전후 README, AGENTS, design 파일 SHA-256 일치

## 검토 대기

- Korean Anatomical Terminology 6판은 2014 edition 후보만 2차 서지에서 확인됨; 현행 edition·primary file·근육 locator 미확보.
- TA2 2019 edition page/link는 확인했으나 고정판/근육 row locator와 파일 미확보.
- OpenStax·Merck는 교육용 내용/평가 근거의 후보이며 전체 근육·평가 데이터베이스가 아님.
- BodyParts3D Release 4.0의 6개 pilot mesh 후보와 네 우측 뼈 mesh는 확보. 5개 뼈는 공식 표상 ID만 확인했다. 실제 mesh 해부학 검토·attachment·pose 검증 및 공개 전 license 재확인은 남아 있다.
- 실제 근육 목록, 용어/해부 claim, origin/insertion, attachment 좌표, 평가 protocol 및 사람 검토는 미완료.
- `reviewed` gate는 입력된 reviewerKind와 hash를 검사하지만 실제 신원을 증명하지 않는다.
- T03 범위에서 실제 데이터, 앱, 사용자 공개, 임상 적격성 판정은 수행하지 않았다.
