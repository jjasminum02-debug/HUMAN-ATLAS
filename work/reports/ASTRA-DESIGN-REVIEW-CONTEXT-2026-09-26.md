# HUMAN ATLAS — Astra 설계 검토용 진행 메모

작성일: 2026-09-26
범위: 현재 checkout의 T14a 완료 상태와 T14b 사람 검토 gate. 이 메모는 검토 요청용 현황이며 새 설계 결정이나 승인 기록이 아니다.

## 한눈에 보는 상태

- 프로젝트: /Users/daniel/Downloads/SIM /HUMAN ATLAS
- 현재: T14a complete_with_gaps. T14b 검토 패킷을 준비했으나 실제 사람 해부학 검토자가 없어 needs_human_review에서 대기한다.
- 다음 실행 경계: T14b의 실제 사람 의견 반영. T15는 시작하지 않았다.
- DEV_URL: 없음. T14a 브라우저 확인 뒤 local Vite 서버를 종료했다.
- OpenSim_Models: 읽기 전용 원본, HEAD d9b05d470b1a481c222372c85b75772faf8f7792, clean.
- 범위 제외: 자동 배포, 환자 진단, 치료, 침 시뮬레이션.

## 진행 단계와 근거

| 구간 | 결과 | 현재 한계 |
|---|---|---|
| T00–T04 | 작업 기반, provenance/schema, partial canonical catalog/region 구조 | 전신 목록 85개는 부분 catalog이지 전신 분모가 아님 |
| T05–T10 | 오른쪽 종아리 6근육의 source-linked terms/claims/summary, learner UI와 viewer, review 경로 감사 | claim/source coverage가 review/승인을 뜻하지 않음 |
| T11-B01–B09 | 용어 overlay batch 완료 | complete_with_gaps; TA2 시각 레이아웃·다수 Korean/Hanja·검토 공백이 남음 |
| T12a/b | viewer/geometry 기반 전환·매핑 | identity 및 표면 사람 검토 대기 |
| T13a/b | 학습 UX·별도 spatial draft layer 검증 | canonical spatialAnnotation 0 |
| T13c-B01/B02/B03 | 독립 현대 자료 확인 후 context-only, geometry:null draft 3건 | 재현 가능한 surface 경계 없음; reviewed 아님 |
| T14a | 6개 학습 경로 실제 브라우저 검증, 현대/Gray 비교, 링크/390px UI 수정 | human review 0; 현대 papers learner UI에 연결되지 않음; 모바일 3D 첫 화면 아래 |

기본 인계 기록: work/STATUS.md. T14a detail: work/reports/T14a.md 및 work/evidence/T14a/. T13c context: work/evidence/T13c-B01–B03/와 각 reports.

## 현재 데이터와 승인 경계

- Catalog: partial85 (individual48/group16/part21); 전신 분모 미동결. learner name overlay 81.
- 오른쪽 하퇴 pilot: 6개 근육. T05 attachment 41건, canonical spatial annotations 0.
- T14a 집계: 실제 surface 후보 0/41, whole-bone context text_only 28/41, matching target mesh missing 13/41, human_review_pending 41/41.
- T14b reviewer packet: ID T14b-HUMAN-REVIEW-PACKET-2026-09-26-v1, SHA-256 02ffd14768e889748776b93b0b1387288fe35dd194beab132ea0855204dad322; input snapshot 16 files; 실제 reviewer opinion 0.
- T13c B01–B03는 각각 별도 context_only, geometry:null, reviewId:null 기록이다. geometry 후보·좌표로 세지 않는다.
- Gray 1918은 번역 요약의 역사적 source. 현대 primary sources 일부는 원문, 일부는 abstract; 직접 다룬 origin/insertion field를 구분했다. 문헌 열람은 credentialed human review가 아니다.
- 2026-09-26 T14a의 learner UI 수정은 잘못된 TA2 name-source mapping과 단비골근 KMLE 목적지 교정, 390px에서 한국어 O/I 요약 우선 노출이다. canonical anatomical claims는 수정하지 않았다.
- T14a 최종 validation: search 38/38, annotation 12/12, spatial drafts 8/8, T03 schema fixtures 17/17, learning validator, typecheck, build, diff-check 통과. Build에 bundle 크기 경고. Desktop viewport의 최종 source-panel 수정 뒤 재측정은 도구 제약으로 못했으며 수정 전 1440/1024, 수정 후 390 확인을 구분해 기록했다.
- T14a preservation: protected 32 files/22 GLB-OBJ and T13c drafts unchanged; OpenSim HEAD/status unchanged. T09 raw localStorage key was not read/written/imported/deleted; no raw hash claim.

## 검토할 설계 질문

1. T14b의 판정 단위를 근육 하나가 아니라 term, origin claim, insertion claim, laterality/mesh identity별로 고정할 것인가? Reviewer identity/date/content hash를 각각 어떻게 연결할 것인가?
2. 실제 사람 검토자의 최소 자격·이해상충·검토 기록 서명/보존 요건을 어떻게 둘 것인가? AI/source analyst의 정보는 독립 검토와 시각적으로 분리되어야 한다.
3. 현재 learning UI에는 Gray link/TA2/name sources가 있지만 근거 register의 현대 paper 비교는 없다. 다음에 현대 출처를 학습 화면에 노출할 것인지, review-only evidence로 유지할 것인지 결정이 필요하다.
4. 현대 연구가 한 부착 field만 직접 다루거나 population sample/longitudinal endpoint만 제공할 때 claim status와 학습 문구에 적용할 source adequacy 기준은 무엇인가?
5. T13c 3건 및 전체 41건에서 geometry-null/context-only/text-only/missing 을 UX와 release manifest에서 어떤 단계별 gate로 집계할 것인가? 실제 surface와 사람 검토를 분리해야 한다.
6. T14a 화면에는 한국어 요약이 390px 첫 화면에 들어오지만 3D는 아래로 밀린다. 좁은 화면에서 text-first layout과 3D visibility를 어떻게 우선순위화할지 결정이 필요하다.
7. TA2 web-published terms와 derived catalog를 재배포할 때의 attribution/permission 검토, 현 KMLE aggregate edition 미노출을 어떻게 release gate에 반영할 것인가?

## Astra 검토 요청의 경계

기술적으로 통과한 validators나 브라우저 표시를 해부학적 정답/사람 승인으로 재해석하지 말 것. Reviewer packet은 T14b에서 실제 자격 있는 사람이 확인하고 자신의 언어로 수정·보류 의견을 기록하도록 준비한다. 별도 결정 전에는 T15, surface generation, public release를 진행하지 않는다.

## Git 및 역할 판단

이번 T14b는 문서 기반 검토 패킷 준비라 코드 아키텍처 변경은 하지 않았다. Sol의 별도 구현 설계가 필요한 단계는 아니다. 실제 사람 해부학 판정은 설계 검토로 대체할 수 없다. Astra에게 reviewer provenance/hash 단위, 현대 근거를 learner 화면에 노출할지, 부분 파일럿의 release gate와 라이선스 처리만 자문하면 된다. 현재 checkout HEAD는 4452411d8a6f52e7a9aacfce003571d8ae53fb6b이며 기존 변경과 T14a/T14b 산출물은 미커밋 상태로 보존한다. reset/rebase/push/deploy는 하지 않았다.
