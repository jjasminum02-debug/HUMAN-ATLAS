# 진행 상태 — HUMAN ATLAS

- LAST_UPDATED: 2026-09-25
- CURRENT_PHASE: 우측 종아리 3D 자산 소량 파일럿 및 공간 좌표 계약 완료
- CURRENT_TASK: 없음 (T02 완료; T03 미착수)
- NEXT_TASK: T03 — 공통 스키마와 검증기
- LAST_REPORT: work/reports/T02.md
- SCOPE_REVISION: T01-policy-v1 (전신 부위와 집계 규칙 고정; canonical 전체 목록은 T04에서 작성)
- DATA_REVISION: T02-BodyParts3D-R4-calf-pilot-v1 (11개 원본 OBJ 후보 및 manifest; 공개/학습 승인 아님)
- TECHNICAL_GATE: T02 source ID/hash, mesh parse, right-side coordinate, transform, local viewer trial 검증 통과. 앱/공통 schema validator는 아직 없음.
- ANATOMY_GATE: 미검토 (실제 근육 claim/mesh/부착부의 사람 검토 없음)
- ASSESSMENT_GATE: 미검토 (protocol/임상 타당성 검토 없음)

| task | 상태 | 산출물/보고서 | 차단 조건 |
|---|---|---|---|
| T00 | complete | work/tasks/T00.md; work/reports/T00.md | 없음 |
| T01 | complete | atlas-data/manifests/scope.json; atlas-data/sources/registry.json; work/review-queue/source-gaps.md; work/reports/T01.md | 후속 용어·내용·자산 검토 대기; T01 완료를 막지 않음 |
| T02 | complete | `atlas-data/manifests/assets.json`; 11 mesh subset; `work/evidence/T02/`; `work/reports/T02.md` | task blocker 없음. 해부학자 리뷰 및 공개 전 license 재확인은 후속 게이트 |
| T03 | not_started | 공통 엔터티 schema, cross-reference/review/publication validator, positive/negative fixture | T01/T02 좌표 계약 완료를 선행으로 사용 |

## 다음 직렬 작업

T03만 다음 순서다. `design/2026-09-25-muscle-atlas/03-LUNA-SERIAL-RUNBOOK.md`의 T03와 `02-DATA-CONTRACT.md`를 기준으로 schema, 교차 참조/review/publication 규칙 validator, 양성·음성 fixture를 만든다. 좌표 계약은 T02 manifest의 mm→m 변환을 따른다. 사용 데이터 입력, 앱 구축, T04 전체 목록 작성은 별도 task 전까지 시작하지 않는다.

## 변경하지 말아야 할 경로

- `OpenSim_Models/`: 읽기 전용 원본 checkout, revision `d9b05d470b1a481c222372c85b75772faf8f7792`; T02 비교 후에도 working tree clean
- `design/2026-09-25-muscle-atlas/`: 설계·템플릿 원본; 기존 SHA-256 대조 결과 변경 없음
- 기존 사용자 파일과 지침: T02 시작 전후 README, AGENTS, design 파일 SHA-256 일치

## 검토 대기

- Korean Anatomical Terminology 6판은 2014 edition 후보만 2차 서지에서 확인됨; 현행 edition·primary file·근육 locator 미확보.
- TA2 2019 edition page/link는 확인했으나 고정판/근육 row locator와 파일 미확보.
- OpenStax·Merck는 교육용 내용/평가 근거의 후보이며 전체 근육·평가 데이터베이스가 아님.
- BodyParts3D Release 4.0의 6개 pilot mesh 후보와 네 우측 뼈 mesh는 확보. 5개 뼈는 공식 표상 ID만 확인했다. 2013 OBJ 내부 이전 license notice와 current archive license 차이를 보존·기록했으며 외부 공개 전에 재검토한다.
- 실제 mesh의 해부학적 identity, origin/insertion, attachment 영역/좌표, 전신 목록, 평가 protocol 및 사람 검토는 미완료.
- T02 범위에서 앱, 사용자 공개, 임상 적격성 판정은 수행하지 않았다.
