# 진행 상태 — HUMAN ATLAS

- LAST_UPDATED: 2026-09-25
- CURRENT_PHASE: 전신 catalog 부분 locator 구축 완료; 전체 목록·언어 출처 검토 대기
- CURRENT_TASK: 없음 (T04 partial 산출물 완료)
- NEXT_TASK: T05 — 파일럿 6개 근육의 명칭·구조 텍스트
- LAST_REPORT: work/reports/T04.md
- SCOPE_REVISION: T01-policy-v1 (전신 부위와 집계 규칙 고정; canonical 전체 목록은 미동결)
- DATA_REVISION: T02-BodyParts3D-R4-calf-pilot-v1 (11개 원본 OBJ 후보 및 manifest; 공개/학습 승인 아님)
- SCHEMA_REVISION: T03-atlas-schema-v1 (Draft 2020-12 schema + project validator)
- CATALOG_REVISION: T04-partial-catalog-v1 (85 indexed row items; 48 individual, 16 groups, 21 parts; whole-body denominator null)
- TECHNICAL_GATE: T03 schema/fixture checks pass; T04 catalog conforms and 17 T04 structural/provenance checks pass. App·실제 구조/기능/부착 claims 없음.
- CATALOG_GATE: BLOCKED — 원본 TA2 Part 2 PDF 미확보, 18 region 전수 추출·term column review 미완료, KAA source missing.
- ANATOMY_GATE: 미검토 (실제 근육 claim/mesh/부착부의 사람 검토 없음)
- ASSESSMENT_GATE: 미검토 (protocol/임상 타당성 검토 없음)

| task | 상태 | 산출물/보고서 | 차단 조건 |
|---|---|---|---|
| T00 | complete | work/tasks/T00.md; work/reports/T00.md | 없음 |
| T01 | complete | atlas-data/manifests/scope.json; atlas-data/sources/registry.json; work/review-queue/source-gaps.md; work/reports/T01.md | 후속 용어·내용·자산 검토 대기; T01 완료를 막지 않음 |
| T02 | complete | `atlas-data/manifests/assets.json`; 11 mesh subset; `work/evidence/T02/`; `work/reports/T02.md` | 해부학자 리뷰 및 공개 전 license 재확인은 후속 게이트 |
| T03 | complete | `atlas-data/schemas/`; validator; 17 synthetic fixtures; `work/reports/T03.md` | reviewer 신원 인증은 별도 시스템 필요 |
| T04 | complete_with_partial_catalog | `atlas-data/catalog/`; `work/review-queue/catalog-gaps.md`; `work/evidence/T04/`; `work/reports/T04.md` | 전체 catalog/분모 gate blocked; 공식 source binary·KAA 용어 source 미확보 |
| T05 | not_started | 파일럿 6개 명칭·구조 텍스트 | 다음 작업; 자동 시작 금지 |

## 다음 직렬 작업

다음은 **T05 — 파일럿 6개 근육의 명칭·구조 텍스트**다. 선행 stable IDs는 `HA-M-000001` gastrocnemius (parts `HA-P-000001` lateral head, `HA-P-000002` medial head), `HA-M-000002` soleus, `HA-M-000003` tibialis anterior, `HA-M-000004` tibialis posterior, `HA-M-000005` fibularis longus, `HA-M-000006` fibularis brevis다. T04 catalog은 partial이며 T05에서도 근거 없는 Korean/Hanja, anatomy claim, review는 추측으로 채우지 않는다. 전체 denominator가 동결됐다는 뜻은 아니다.

> 작업 대상은 현재 폴더 아래 HUMAN ATLAS 프로젝트다. `design/2026-09-25-muscle-atlas/00-START-HERE.md`와 `03-LUNA-SERIAL-RUNBOOK.md`를 읽고 T05만 수행해 줘. 상세 설계는 같은 폴더의 01, 02, 04에서 확인하고 T03 schema/validator 및 T04 partial catalog/crosswalk/gap queue를 실제 파일로 검토해라. pilot stable IDs는 gastrocnemius `HA-M-000001` (lateral head `HA-P-000001`, medial head `HA-P-000002`), soleus `HA-M-000002`, tibialis anterior `HA-M-000003`, tibialis posterior `HA-M-000004`, fibularis longus `HA-M-000005`, fibularis brevis `HA-M-000006`다. 정확한 출처·판본·locator가 확인된 영어/Latin/Korean/Hanja term과 기시·정지 및 관련 구조만 T03 형식으로 기록하고, 확인 못 한 것은 null/미확인으로 둬라. 기능·평가 본문, 앱, 전체 목록 보완, OpenSim 원본 변경, 공개/자동 배포, 환자 진단·치료·침 시뮬레이션은 범위 밖이다. 사용자 파일과 지침을 보존하고 task 명세·결과·검증·진행 상태를 프로젝트 안에 기록해라. T05만 수행하고 다음 task ID와 붙여 넣을 프롬프트를 남긴 뒤 멈춰라. 다음 task를 자동 시작하지 마라.

## 변경하지 말아야 할 경로

- `OpenSim_Models/`: 읽기 전용 원본 checkout, revision `d9b05d470b1a481c222372c85b75772faf8f7792`; T04에서 수정하지 않음
- `design/2026-09-25-muscle-atlas/`: 설계·템플릿 원본; T04 시작/종료 SHA-256 대조
- 기존 사용자 파일 및 지침: README, AGENTS 및 설계 파일 보존 대조 수행

## 검토 대기

- TA2 Part 2는 공식 검색 색인의 일부 행만 구조화했다. PDF 바이너리/hash/화면 대조와 전신 inventory는 미확보다.
- Korean Anatomical Terminology primary file/current edition/locator와 Hanja correspondence는 미확보다.
- FIPAT 표의 term column role 및 Errata 전수 검토가 남아 있다.
- T02 BodyParts3D pilot link는 provisional; mesh identity·attachment·pose 사람 검토 및 공개 전 license 검토가 남아 있다.
- `reviewed` gate는 T03에서 evidence/hash 구조를 검사하지만 reviewer 실제 신원을 증명하지 않는다.
- T04에 근육별 anatomy claim, 실제 사람 review, 앱, 사용자 공개, 임상 적격성은 없다.
