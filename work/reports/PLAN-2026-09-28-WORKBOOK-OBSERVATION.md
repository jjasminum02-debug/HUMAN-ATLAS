# 엑셀·얼굴·관찰 도구 계획 개정 결과

2026-09-28 · Astra · **계획 개정 완료, 앱 구현 및 전수 해부학 검증 미실행**.

## 결과

원본 엑셀을 읽기 전용으로 import/inspect했다. `근육표` 257행, 작용 한자 포함 53셀, 손/발 동명 영어 항목 2쌍을 확인했다. 원본 SHA-256은 `8e10e00e76f5da8e6d1be6a0f9dcab6039d9a3f81d8a3808c0fe28545802ab3c`로 보존됐다. 강의 PDF 12종은 전달받지 않았으며 표의 행별 독립 근거가 없는 상태다. 운동신경 가지의 과도한 단정 가능성은 F23과 공개 원 연구 대조로 사례를 남겼으나 257행 검증 완료로 처리하지 않았다.

현재 머리 package에는 뼈 13개·근육 23개 node가 있고, 근육은 눈·혀·입천장/목젖이다. 얼굴 표정근 surface는 없다. T97의 기존 외부 모델 객체 index에는 얼굴 이름 후보가 있어 실제 추출/좌표·권리 검증/장면 연결이 다음 필요한 작업이다. 이름만으로 identity/정합을 승인하지 않았다. T96의 542개는 뼈·군·부분을 포함한 term target이며 개별 전신 근육 분모는 null이다.

관찰 버튼은 삭제되지 않았으나 canonical 선택이 있어야 표시된다. source-only는 learner pick에서 제한되며 선택 자체의 반투명/숨김은 없다. 따라서 기능 접근 문제와 미구현 기능을 구분했다. 코드/manifest 조사 결과이며 이번 턴의 실제 브라우저 합격 주장은 없다.

## 변경한 계획

- 24-WORKBOOK-FACE-AND-OBSERVATION.md에 입력 검증·짧은 운동/감각 표기·한글 기능·얼굴 우선·관찰 UX와 실제 합격 기준을 작성했다.
- 23-PROMPTS-AFTER-T95.md를 현행 순서/59개 개별 블록으로 동기화했다. 완료된 task는 이력 확인용이다. T101의 실제 완료/다음 T102를 보존했다.
- 새로운 task는 **T166 관찰 도구 한 개**. T107→T166→T98→T99→T100→T110→T108→T109→T111–121. T122–165는 계속 폐기된 미실행 계획이다.
- 엑셀 수집/매핑/기시정지·짧은 신경 검증은 기존 T81, 기능 검증·한글화는 기존 T83에서 처리한다. 신규 import task와 행별 task를 발급하지 않았다.
- 머리 T110은 기존 113개 target/history를 유지하면서 표정근 work-order를 우선한다. 표정근/광배근의 실제 표면과 선택 누락은 T80/T58 전신 구조 합격을 막는다.
- 표정근의 구조/기시정지/기능 설명은 필수이며 애니메이션만 사용자 요청으로 deferred_by_user다. exact ID는 T110에서 확인, T35에서 동결한다. 씹기근/외안근/혀까지 자동 제외하지 않는다. T47/T85와 후속 신경 시작 조건도 이 분리를 적용한다.

## 검증과 한계

`work/evidence/2026-09-28-workbook-observation-plan/validation.json`에서 registry/프롬프트 순서·next 연결·유일 ID/anchor·폐기 ID 유지·보존 검사 152/152를 확인했다. 이는 문서/계약/보존 검사이며 앱 테스트 152개나 해부학 claim 152개 합격이 아니다. 원본 엑셀, OpenSim HEAD/clean 상태, T96/역사 source manifest, 소유 외 파일의 변경 여부를 검사했다. 앱 코드 변경을 하지 않았으므로 typecheck/build/브라우저 재검증은 수행하지 않았다. 초기 포트 5186은 응답하지 않았고 브라우저 탭도 없었다.

검사 도중 다른 작업이 `atlas-web/src/viewer/wholeBody/AnatomySceneController.ts`에 DEV 성능 측정 코드를 추가한 것을 발견했다. 최초 검사는 이를 보존 차이로 감지했으며 `validation-initial-concurrency-detection.json`에 그대로 남겼다. diff와 hash를 `concurrent-wip.json`에 기록했다. pick/sync 메서드는 기준선과 동일함을 확인하여 이번 관찰 분석은 유효하다. 해당 파일을 수정/되돌림/스테이징하지 않았다. 앞으로 T166 실행자는 이 변경을 포함한 최신 기준선을 읽어야 한다.

## Git 및 다음 실행

문서 작성 기준 HEAD: `9612c7582c473e5e62943b948245db8daac1f094` (동시에 진행되던 T101의 실제 커밋). OpenSim: `d9b05d470b1a481c222372c85b75772faf8f7792`, clean.

소유 범위는 설계 22의 우선순위 안내·23 프롬프트·새 24 설계, 관련 미래 task 명세의 개정 안내, 새 T166 명세, 이 보고서와 이번 evidence뿐이다. 기존 변경이 섞인 STATUS/R15 registry는 작업트리에서 소유 필드/append만 갱신했으며 파일 전체는 커밋에서 제외한다. 재현 가능한 `status-registry-delta.json`/`status-append.md`를 커밋한다. 원본 workbook/임시 추출 데이터/source cache/OpenSim/기존 WIP/동시 controller 변경은 제외한다. 정확한 체크포인트 해시는 최종 응답과 이 파일을 수정한 Git commit에서 확인한다.

다음은 **T102 / Luna Max**. `work/evidence/2026-09-28-workbook-observation-plan/START-NEXT.md`에 붙여 넣을 프롬프트를 남겼다. 이미 T102가 시작됐다면 중복 실행하지 않는다. 이후는 23 문서에서 해당 ID 블록 하나씩 사용한다. 다음 task 구현, push, 배포는 하지 않았다.
