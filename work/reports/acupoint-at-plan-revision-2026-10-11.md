# AT 프롬프트·그래픽 인수 계획 정정

2026-10-11 · 사용자 요청에 따른 설계/프롬프트 수정 완료. AT 후속 기능 구현은 수행하지 않았다.

## 발견한 문제와 교정

1. 작업 크기 추정이 실행 중단 규칙으로 변질됐다. 전체 AT 프롬프트에서 예상 분, 정해진 시각의 중단, elapsed time 보고 의무를 제거했다. 산출물·인수 기준으로 종료한다.
2. 실제 AT1 완료에도 안내가 모두 미착수/다음 AT1이라고 했다. 완료 AT1은 재사용하고 현재 AT2 진행이라는 사용자 알림을 표시했다. AT2의 실행 record는 담당 실행자가 갱신하도록 원문 보존했다.
3. 전체 위치 데이터를 작성한 뒤에야 영역 표현을 확인하는 순서였다. AT20–22를 AT7 뒤에 배치해 실제 폐경 점·선·면·카메라를 먼저 검사한다. 새 task 번호는 추가하지 않았다.
4. task 크기가 개수/시간 위주여서 경계가 모호했다. AT3/4는 채택된 경로의 carrier 등록, AT5는 명시 입력 compiler, AT22는 triangle brush 하나로 한정했다. 새 전신 수작업·범용 자동 지표 인식·동시 UV/control-point 편집기를 제외했다.
5. 자연스럽다는 표현만으로는 합격 여부를 판단하기 어려웠다. 같은 장면 유지, 최소 카메라 이동, 수동 입력 우선, 로딩 취소, 모바일 패널 가림, 색 영역 깊이/대비, 경계 수정 불변성을 G1–G8로 정의했다. 화면 검사를 AT28까지 미루지 않는다.

## 저장한 결과

- design/2026-09-25-muscle-atlas/30-AT-361-POINTS-AND-TERRITORIES.md: 범위 보존, 순서/작업 크기 정책 교정.
- design/2026-09-25-muscle-atlas/31-AT-EXPERIENCE-AND-DELIVERY-CONTRACT.md: UI/graphics/성능/인수 계약.
- work/tasks/AT1.md–AT29.md: 범위·산출물·검사·전체 실행 프롬프트.
- work/plans/acupoint-at-2026-10-11/START-HERE.md: 현재 진입점/순서/각 프롬프트 링크.
- work/plans/acupoint-at-2026-10-11/AT2-CONTINUE-CORRECTION.md: 진행 중 AT2 대화에 추가할 지시. 재시작하지 않는다.
- work/EXECUTION.json: 해당 feature plan 순서/정책과 계획 task 메타데이터만 수정. AT1/AT2 record는 전체 보존했다. 그 안의 estimateMinutes는 역사값으로만 해석한다.

## 검증과 한계

14개 문서/데이터 일관성 검사 통과: 기존 AT 29개 ID 유지, 의존성 순서, 361개 코드 중복/누락 없음, 코드 배정 보존, AT1/AT2 및 다른 task 기록 보존, 시간 중단 프롬프트 제거, 다음 프롬프트 연결, 로컬 링크, 시작 시 기존 tracked WIP hash 보존.
sync_execution.py는 Updated 0, --check는 일치했다. 기존 projection은 숫자 T queue만 투영하므로 AT 흐름은 featurePlans 및 AT START-HERE가 기준이다.

앱 runtime을 수정하지 않았으므로 새로운 화면/성능 합격이나 361혈 구현 완료를 주장하지 않는다. 실제 화면 인수는 각 구현 task의 산출물이다. 작업 소요시간이나 의학적 위치 정확도를 이 계획으로 보장하지 않는다. 원문 자료·특수 부위 carrier의 실제 부재는 해당 실행에서 구체적으로 해결해야 한다.

## Git·보존·다음

시작 HEAD: f19268f39b99603cfba969c5e71e43e3da082f4e. 시작 시 tracked WIP 45개는 hash가 모두 유지됐다. 원본/OpenSim_Models/T13 drafts/기존 UI/AC·AT1 역사 report/evidence를 수정하지 않았다.

이번 로컬 커밋에는 위 설계/명세/계획/EXECUTION의 소유 변경과 이 보고서, 작은 baseline/validation만 포함한다. 기존 사용자 변경, 원본/source cache, AT2 실행 산출물, private 자료는 제외한다. 커밋 해시는 최종 응답 및 Git 이력에서 제공한다. 기존 파일을 복구/삭제하거나 history를 재작성하지 않는다. push·배포 없음.

**현재 진행 ID는 AT2 유지.** 보정 프롬프트를 같은 실행 대화에 전달하고 AT2 결과 후 AT3만 요청한다. 이후 AT3→AT4→AT5→AT6→AT7→AT20→AT21→AT22→AT8…AT19→AT23…AT29. 자동 실행 없음.
