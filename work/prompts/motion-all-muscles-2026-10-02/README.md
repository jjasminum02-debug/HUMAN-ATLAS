# 전체 근육 움직임 — 실행 순서와 개별 프롬프트

2026-10-02 · 초기 확장 근육 shortlist 없음 · **이번 문서 작성으로 작업/agent를 실행하지 않음**.

1. **T35 통합 담당**: `work/prompts/app-completion-2026-10-01/13-T35.txt`를 별도 실행한다. 현재 다음 ID는 T35다.
2. **동시에 조사 A/B/C 가능**: 이 폴더의 `02-research-A.txt`, `02-research-B.txt`, `02-research-C.txt`를 사람이 서로 다른 대화에 각각 넣는다. 고정 manifest `work/evidence/motion-all-muscles-plan-2026-10-02/run-manifest.json`는 실제 존재하고 검증했다. A/B/C는 전수429 target/232 source/462 표면을 중복 없이 나눠 자기 evidence 폴더만 쓴다. 자동 위임하지 않는다. 전체 source/target이 빠짐없이 배정됐으며 표정근도 제외하지 않는다.
3. **T59 공통 제작 경로**: T35 실제 계획·계약을 확인한 후 `work/prompts/app-completion-2026-10-01/14-T59.txt`. T59는 공통 exporter/player/복원과 T66용 actual authoring manifest/validator를 생성한다. 자료 조사는 공통 코드와 독립적으로 계속할 수 있지만 입력 변경은 writer가 새 revision으로 관리한다.
4. **T25 공통 학습 UI**: `work/prompts/app-completion-2026-10-01/15-T25.txt`. T59의 실제 frozen 계약 뒤 별도 자산 authoring은 자기 후보 폴더에서 병렬 가능하다. 자산 프롬프트는 manifest가 실제 만들어졌음을 확인한 후 사용한다.
5. **자산 제작 A/B/C**: `04-authoring-A.txt`, `04-authoring-B.txt`, `04-authoring-C.txt`를 각각 사용한다. T59 이전에는 실행하지 않는다. common skeleton/rig/player를 여러 사람이 따로 수정하는 병렬 개발은 금지한다.
6. **T66 단일 통합 writer**: `work/prompts/app-completion-2026-10-01/16-T66.txt`에서 전수 패키지를 검사/등록하고 예외/미확보를 처리한다. 필요하면 직접 공통 도구로 전수 제작한다. 각 worker의 candidate 통과와 제품 실제 support는 다르다.
7. **T85 품질 감사 → T40 실제 전달**: 기존 canonical `17-T85.txt`, `18-T40.txt`를 순서대로 사용한다.

현재 바로 병렬 실행 가능한 것은 **T35 계획·통합 + 조사 A/B/C**다. motion assets는 아직 공통 rig/pose 계약이 없으므로 지금 바로 제각각 제작하지 않는다. T35/T59 표본은 엔진 검증 수단이며 목표 대상 목록이 아니다.

목표 원장: 429 muscle-related target records/447 muscle memberships, 현재232 source concepts/462 surfaces, 전체 제품542/563/12. 그룹/갈래/좌우 중복을 실제 근육 수나 clip 수로 합치지 않는다. 전체 목표 완성 여부는 전수 실제 action/side/geometry 지원에서 계산한다.
