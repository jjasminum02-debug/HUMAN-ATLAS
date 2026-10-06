# HUMAN ATLAS 이름 검토 03 — 결과

- 범위: 이름·신경·카드 개선 계획 03, 근육 이름 검토만
- runId: `atlas-quality-review-2026-10-06-r1`; 기준 HEAD `786fe55e5f304b434705a9bf66ff7256cdb1444d`; 관찰 HEAD `f3b2113dd8abb3422d6d7b54e251988e72bfe2d1`
- 고정 입력 SHA256: `637e4d079f90e68743f656c07d08244a98521b42baab49b4de1f5ae8975c0996` (manifest와 일치)
- 소유 출력: `work/reviews/atlas-quality-review-2026-10-06/names/`
- 공통 runtime/data/EXECUTION/spec/report, source files, OpenSim/T13/WIP는 수정하지 않았다.

## 전수 disposition

- source **472행**: learner 462행과 inspection 10행을 분리했다. 472는 고유 source key 수이고 개념 수가 아니다. learner는 232 source groups, inspection은 5 groups다.
- target **429행**: named muscle 245, part 94, group 58, repeated family 26, complex 6이다. source 행과 합치지 않았다.
- source group 237개 모두 각 좌우의 label/세 이름/별칭/부위 표시가 일관됐다. 그룹 필드 불일치는 0건이다.
- learner 462행의 현대명·한자어명(한글 표기)·영문명은 모두 표시값이 있다. inspection 10행 중 8행은 세 필드가 있고 BP3D4-FJ2745/FJ2757의 한자어명(한글 표기)은 null이다. 두 건은 inspection 전용이고, 기존 alias “이관인두근”만으로 전통명을 채우지 않았다.
- T96 고정 target 영문은 429/429행에 있다. target term dossier는 179행이며 dossier 내 한국어 직접 locator는 현대명 108개, 한자어명(한글 표기) 109개다. dossier 내 미확정은 각각 71/70개, dossier가 없는 target은 250개다. 전체 429 target에서 target-specific 직접 한국어 근거가 확인되지 않은 수는 현대명 321, 한자어명(한글 표기) 320이다.
- 이전 T100 후보 원장은 75행이다. 이번 고정 429개 근육 target과 겹치는 행은 71개이며, 그중 70개에 AI 표시 후보가 있다. 나머지 4행은 뼈 target이라 이름 후보를 이번 결과에서 제외했다. 근육 후보는 직접 표제어 근거/사람 승인으로 세지 않았다.
- overlay direct learner relation은 316 target에서 확인되고 113 target에는 direct relation이 없다. 이는 geometry 부재나 이름 오류 판정이 아니다. 부분 member 관계를 전체 group 이름/범위로 승격하지 않았다.

## 오류·개선안

1. **손·발 엄지 근육 검색 alias 충돌 5종.** `짧은엄지폄근`, `단무지신근`, `긴엄지폄근`, `긴엄지굽힘근`, `장무지굴근`이 각각 hallucis/pollicis source groups에 함께 나타난다. 각 group의 기본 이름은 서로 구별되지만 이 단어만 입력하면 다중 결과다. 세 손쪽 pollicis 근육의 양측 6 source rows에 “손 · …” 검색 alias를 추가하는 안을 정확한 JSON pointer/before hash와 함께 제안했다. 기존 unqualified alias는 보존해 다중 결과로 두고, 발쪽의 “발 · …” 이름을 유지한다.
2. **Bucinator.** target TA2:2086의 frozen English preferred term “bucinator” 및 synonym “buccinator muscle”이 함께 기록되어 있다. 현재 `Bucinator`는 고정 preferred term과 일치하므로 오명이라고 단정하지 않았다. 양측 source alias에 “Buccinator muscle”을 추가하는 검색 개선안을 제시하고 raw source name/기본 English는 보존한다. 현재 “볼근/협근”은 AI contextual composition으로 표시되며 직접 표제어 근거가 아니다.
3. **승모근 상·하부.** 네 source row의 upstream 이름 충돌은 기존 T100 correction으로 처리되어 있다. 상부는 descending/superior(TA2:2227), 하부는 ascending/inferior(TA2:2229) 표시가 prior evaluated surface와 카드에 맞았다. 이번에는 재수정하지 않았다. 과거 browser 결과는 4개 selection/card/surface 일치지만 저장 PNG와 console capture는 없었다.
4. **삼각근·위팔두갈래근.** 빗장/봉우리/어깨뼈가시 부분은 각각 전면/측면/후면삼각근 검색 별칭에 정확히 대응하며, 전체 삼각근 이름으로 덮지 않는다. 위팔두갈래근 긴·짧은갈래는 장두·단두와 연결된다. 단독 “긴갈래”는 두갈래근과 세갈래근 양쪽에 존재하는 의도된 다중 검색어다. 전체 이름과 구별 결과를 유지한다.

## 표기 차이와 미확정

- modern과 traditional 필드가 다르거나 display label이 달라지는 것은 역할이 다른 표기 변형으로 분류했다. label은 202행에서 traditional과, 264행에서 modern 필드와 다르다. 이 수치는 오명 수가 아니다.
- source 객체 자체의 field locator가 없는 learner 행은 modern 86, traditional 98, English 256개다. 화면 이름 공란과 혼동하지 않았고, `names-review.json`에 field별로 기록했다. `candidate_only` 상태를 의미 정확성 인증으로 바꾸지 않았다.
- 확실한 target 용어/part/alias 근거가 부족한 항목은 미확정으로 유지했다. 이름이 입력됐다는 사실만으로 정확성 verified라 하지 않았다.
- 542/563/12, HA130, 역사 163(6/20/135/2), source-only/local selection, humanReview=`not_performed`, public rights=`held`, 원본/OpenSim_Models/T13/WIP는 변경되지 않았다. 실제 Hanja glyph는 수집하거나 출력하지 않았다.

## 검증과 인계

- manifest의 472 source key/429 target ID와 snapshot SHA를 검증했다.
- field presence, bilateral group consistency, cross-group exact search ambiguity, direct target relation, target term dossier 상태를 자동 대조했다.
- 공통 파일 변경, build, 전체 suite, 전수 PNG, stage/commit은 하지 않았다. 제안 alias의 실제 search-result UX는 04 통합자가 확인해야 한다.
- 이는 이름 검토 산출물이며 전체 해부 용어의 human approval/complete 선언이 아니다.

02 신경 검토 완료 후 04 `integrate-and-deliver.txt`에서 두 검토 결과를 실제 반영하고 UI에서 확인한다. 다른 단계는 시작하지 않았다.
