# 진행 상태 — HUMAN ATLAS

- LAST_UPDATED: 2026-09-25
- CURRENT_PHASE: T05 파일럿 구조 텍스트 입력 완료; 사람 검토·언어 출처 보완 대기
- CURRENT_TASK: 없음 (T05 입력/기술 검증 완료, 내용은 review 대기)
- NEXT_TASK: T06 — 웹 앱과 텍스트 탐색
- LAST_REPORT: work/reports/T05.md
- SCOPE_REVISION: T01-policy-v1 (전신 부위와 집계 규칙 고정; canonical 전체 목록은 미동결)
- DATA_REVISION: T05-pilot-structure-text-v1 (6 muscles + 2 gastroc head parts; 54 structure terms, 41 attachments, 45 claims; all claims unreviewed)
- SCHEMA_REVISION: T03-atlas-schema-v1 (Draft 2020-12 schema + project validator)
- CATALOG_REVISION: T04-partial-catalog-v1 (85 indexed row items; 48 individual, 16 groups, 21 parts; whole-body denominator null)
- TECHNICAL_GATE: T03 schema/fixture/dataset checks pass; T04 partial catalog and T05 structure/provenance/coverage checks pass. UI app 없음.
- CATALOG_GATE: BLOCKED — 원본 TA2 Part 2 PDF 미확보, 18 region 전수 추출·term column review 미완료, KAA source missing.
- ANATOMY_GATE: needs_human_review (T05 historical-source claims are unreviewed; mesh identity/attachment surface review is absent)
- ASSESSMENT_GATE: 미검토 (protocol/임상 타당성 검토 없음)

| task | 상태 | 산출물/보고서 | 차단 조건 |
|---|---|---|---|
| T00 | complete | work/tasks/T00.md; work/reports/T00.md | 없음 |
| T01 | complete | atlas-data/manifests/scope.json; atlas-data/sources/registry.json; work/review-queue/source-gaps.md; work/reports/T01.md | 후속 용어·내용·자산 검토 대기; T01 완료를 막지 않음 |
| T02 | complete | `atlas-data/manifests/assets.json`; 11 mesh subset; `work/evidence/T02/`; `work/reports/T02.md` | 해부학자 리뷰 및 공개 전 license 재확인은 후속 게이트 |
| T03 | complete | `atlas-data/schemas/`; validator; 17 synthetic fixtures; `work/reports/T03.md` | reviewer 신원 인증은 별도 시스템 필요 |
| T04 | complete_with_partial_catalog | `atlas-data/catalog/`; `work/review-queue/catalog-gaps.md`; `work/evidence/T04/`; `work/reports/T04.md` | 전체 catalog/분모 gate blocked; 공식 source binary·KAA 용어 source 미확보 |
| T05 | complete_with_unreviewed_claims_and_language_gaps | T05 terms, structures, attachments, claims, evidence; `work/review-queue/pilot-structure-gaps.md`; `work/reports/T05.md` | anatomy/human review, KAA terms, TA2 visual audit, variants remain open |
| T06 | todo | 웹 앱과 텍스트 탐색 | T03/T05 outputs available; task not started |

## 다음 직렬 작업

다음은 **T06 — 웹 앱과 텍스트 탐색**이다. T05의 6개 근육과 두 비복근 근두의 관찰 용어·구조 claims·historical evidence 및 미확인 상태를 카탈로그에서 읽어 보여 주되, 모든 claim은 `needs_review`로 남아 있다. Korean/Hanja는 null/held이고 전신 목록은 partial이다. T06은 이 상태들을 표시해야 하며 anatomy gate를 올리는 작업이 아니다.

> 작업 대상은 현재 폴더 아래 HUMAN ATLAS 프로젝트다. `design/2026-09-25-muscle-atlas/00-START-HERE.md`, `03-LUNA-SERIAL-RUNBOOK.md`, `work/STATUS.md`를 읽고 T06만 수행해 줘. T03 schema/validator와 T05 실제 terms, attachments, claims, evidence, 미확인 큐를 파일로 검토하고 `work/tasks/T06.md`의 허용 경로와 완료 기준을 먼저 기록해라. React/TypeScript/Vite 앱, 데이터 로더, 오류·미완료 상태, 근육 목록과 구조 카드, URL 선택 상태만 구현해라. 6개 데이터는 catalog에서 불러오고 이름/기시·정지 문장을 앱 코드에 하드코딩하지 마라. 3D 에셋 없이 텍스트/출처/미확인 상태가 동작해야 한다. 모바일과 키보드 탐색을 실제 브라우저에서 검증하고 evidence를 남겨라. 기존 사용자 파일과 지침, OpenSim_Models 읽기 전용 원본을 보존하고, 공개 배포·기능/평가 콘텐츠·진단·치료·침 시뮬레이션은 범위 밖이다. 작업 명세·결과·검증·상태 및 다음 작업을 프로젝트 안에 남겨라. T06만 완료한 후 다음 task ID와 붙여 넣을 프롬프트를 기록하고 멈춰라. 다음 task를 자동 시작하지 마라.

## 변경하지 말아야 할 경로

- `OpenSim_Models/`: 읽기 전용 원본 checkout, revision `d9b05d470b1a481c222372c85b75772faf8f7792`; T05에서 수정하지 않음
- `design/2026-09-25-muscle-atlas/`: 설계·템플릿 원본; T05 전후 SHA-256 대조
- 기존 사용자 파일 및 지침: README, AGENTS 및 설계 파일 T05 전후 보존 대조 수행

## 검토 대기

- TA2 Part 2는 공식 검색 색인의 일부 행만 구조화했다. PDF 바이너리/hash/화면 대조와 전신 inventory는 미확보다.
- Korean Anatomical Terminology primary file/current edition/locator와 Hanja correspondence는 미확보다.
- FIPAT 표의 term column role 및 Errata 전수 검토가 남아 있다.
- T02 BodyParts3D pilot link는 provisional; mesh identity·attachment·pose 사람 검토 및 공개 전 license 검토가 남아 있다.
- `reviewed` gate는 T03에서 evidence/hash 구조를 검사하지만 reviewer 실제 신원을 증명하지 않는다.
- T05 anatomy claims는 역사적 출처 summary이고 실제 사람 review·앱·사용자 공개·임상 적격성은 없다.
