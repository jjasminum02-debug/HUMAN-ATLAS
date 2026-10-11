# AT7 run-r1 evidence

판정은 work/reports/AT7-r1.md와 validation-r1.json. 기존 원본/AT6 evidence를 덮지 않은 새 디렉터리다.

- 시작 상태: baseline.json / baseline-status.bin / execution-before.json. ownership-r1.json은 기존 버튼 2개 handler를 포함한 실제 최소 소유 경계.
- native geometry: build-contexts.py는 AC1의 GLB reader 함수만 재사용하며 실행된 과거 main/downloader를 호출하지 않는다. context-geometry-audit-r1.json의 86개 source-local 삼각형 집합/행렬/국소 bounds와 AT6 손톱 probe 2개. 생성물은 피부 scan/새 위치가 아니다.
- 최종 실제 화면: context-final-*.png/json 24개와 responsive-cases-final.json. 개발 r1/r2/r3/r4 화면은 수정 과정이며 최종 승인에 중복 합산하지 않는다. HMR UUID 변경과 실제 동일 장면 사용을 구분한다.
- 초기 선택/검색/실제 클릭: initial-local-context-r1, cross-channel-search-r1, search-select-r2, actual-point-click-r2, native-anatomy-click-r1.
- 공통 기능: all-points-r1 (22 실제/648 준비 중), display-toggles-r1, midline-unresolved-r1, rapid-channel-side-r1, fast-off-on-r1, rapid-point-selection-r1.
- 카메라/소유권: adequate-framing-retained-r2, rapid-reentry-return-r1, close-during-return-r1, tour-complete-r3, manual-inputs-r2, manual-close-r1, layer-off-preserved-r1.
- 모바일/키보드: mobile-final-r2 (44px 이상), keyboard-close-r1, mobile-final-collapse-r1. 최종 min-width 수정 전 header collapse width 39px 관측은 mobile-final-collapse-r1에 보존하고 mobile-final-r2를 최종 목표 크기로 사용한다.
- resource 종료: final-native.json, console-final.json. native 원래 선택/URL 복원, viewport override 해제, owner/update/overlay 없음.
- 검사: tests-final-r2.log 64 pass; build-final-r2.json 13 pass. typecheck-final.log와 build tsc 단계. tests-r2의 mock arrow-field 접근 실패와 tests-r3의 strip-types flag 오류는 수정된 harness/transform-types 실행으로 대체되며 보존한다.
- validate-evidence.py는 실제 입력·원본 native geometry·스크린 증거를 읽어 판정을 재현한다. bundled Python NumPy 필요.
- preservation-r1.json, execution-scope-r1.json, sync-*.log, commit-scope-r1.json은 소유·보존·실행 상태·선별 commit 검사.

fixture/publication/professor approval이나 다른 경맥의 위치 완료를 주장하지 않는다. 다음 프롬프트 파일은 전달용이며 AT20 실행 산출물이 아니다.
