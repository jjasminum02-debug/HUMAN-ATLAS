# 전신 베이스 우선 감사·계획 정정

2026-09-28 · Astra · 설계/실행관리 도구 완료, 전신 모델 구현 미실행.

## 판단

기존 task 순서는 전신 제품을 먼저 완성하는 데 비효율적이었다. 작은 source subset의 기술 성공을 계속 쌓았지만 canonical 이름/선택 연결은 뒤로 밀렸다. 자료 하나 추가할 때 새 TS extension, Python wrapper, parent hash field와 plugin 분기가 늘어나는 구조가 실제 코드에 나타났다. 같은 공통 renderer를 유지하는 장점은 있지만 data-driven 확장에는 충분하지 않다.

Luna의 코딩 능력이 문제라는 결론을 낼 근거는 없다. 명세가 매 task의 exact subset과 모든 이전 parent chain을 요구했기 때문에 구현도 그 형태로 커졌다. 근육별 작업을 더 잘게 쪼개는 것으로 해결되지 않는다. 현재 React/Three 기반과 scene lifecycle은 유지하고, source 준비/일괄 compiler/runtime 전달과 실제 학습 연결의 경계를 바꾸는 것이 적절하다.

## 실제 근거

| 발견 | 근거 | 조치 |
|---|---|---|
| 작업 번호가 runtime 경로에 들어감 | `atlas-web/plugins/wholeBody.ts`, `t101SceneExtension.ts`부터 `t104SceneExtension.ts` | T99 generic dataset compiler/loader. 새10개마다 새 TS 파일 금지 |
| 같은 파일 재검증 반복 | plugin이 매 chunk HTTP 요청 때 source/overlay/extension12개를 읽고 합성 | revision 단위 검증 cache와 content-hash chunk index. 검증 자체는 유지 |
| 복제 비용 | T101/T102 acquire line similarity94.7%, build81.4% | adapter별 공통 CLI와 데이터 manifest. 기존 스크립트는 역사 재현용으로 보존 |
| 전신 크기 대비 학습 연결 부족 | 593nodes/36chunks, 기본표시581, canonical 연결node10 | T100에서 source/instance/concept/지역/세이름/선택을 같이 대조 |
| 상세 데이터가 누적 보유됨 | `resources.ts`의 loaded Map은 dispose까지 유지 | overview pin + active detail byte-budget LRU/eviction |
| 현재 contract가 특정source/LOD에 고정 | `contract.ts:29`, BP3D prefix/frame, LOD1 | 명시적 versioned contract migration과 source namespace/instance transforms |
| 전신 raycast와 주기적 보고 비용 | controller의 root 전체 raycast,500ms마다 notify | visible/eligible candidate 제한, dirty progress, 실제 병목 계측 |
| 전신 모델 변환 feasibility 미확인 | T97: Blender 3개 버전 초기화 실패, 일부 raw arrays 추출 | T98에서 전신 source inventory와 실제 exporter 대표단위 검증을 함께 수행 |

GLB 합계는 **71,065,840 bytes**, 전체 파일 source triangles는 **2,800,004**이며 visible triangles나GPU 메모리가 아니다. 파일별 GLB hash를 확인했다. 감사 후 확보된 T104 실측 evidence는 warm1440×900/DPR1에서 visible581/draw581, triangle2,495,056, CPU geometry66,367,056bytes, RAF interval p95관측16.8ms(별도17.5ms)다. cold load/실제 draw CPU 시간/실제 모바일 합격을 뜻하지 않는다. 기존 dist의 App JS1,203,309bytes도 압축 전 관찰값이며 이번에 재빌드한 값이 아니다. task 전용 extension은 Vite 서버측 경로이므로 이 코드 길이를 브라우저bundle 무게로 혼동하지 않는다.

JS whole-body 회귀23/23과 typecheck를 직접 실행해 통과를 확인했다. 새로운 코드 오류가 재현된 것은 아니며, 전체 기능·해부학·기기별 성능을 전부 검증한 것도 아니다. 이번 턴은 실제 브라우저를 새로 조작하지 않았다. T104 browser/performance는 해당 완료 evidence를 읽고 인용했다.

## 새 실행 계획

**T98 → T99 → T100 → T80 → T58**을 첫 목표인 전신 근육·뼈 구조/선택 완성에 집중시킨다. 광배근 전용이었던 미착수 T98–100의 범위를 명시적으로 바꾸고 새 task 번호는 발급하지 않았다. T105–109/T110–121/T166의18개 독립 작업은 필요한 exact 대상/hold/지역/관찰 요구를 위 작업에 흡수했다. 이들은 완료/삭제가 아니며 `absorbed_not_executed`로 기록했다. T122–165도 계속 superseded다.

전신 source inventory는 근육·뼈·신경·내장기를 구분하지만 첫 runtime은 뼈와 근육이다. Z-Anatomy를 우선 후보로 검사하되 자동 채택하지 않는다. 실제 exporter와 권리·자세·좌우·범위를 확인한 뒤 하나의 주 베이스를 선택하고 부족분만 보완한다. 전체 자료를 일괄 처리하는 것과 브라우저에 전부 동시에 올리는 것은 다르다. 전신 overview와 상세 LOD, byte 예산과 cache 해제로 runtime을 제한한다.

각 task는 독립 산출물과 내부 재개 단위를 갖는다. T99는 공통 엔진과 전체 변환, T100은 전신 데이터와 선택 연결, T80/T58은 전수 검사와 제품 합격이다. 대표 12개 시험이나 첫 부위만으로 전체 완료를 선언하지 않는다. exporter 입력이 없으면 필요한 실행 환경이나 공식 export를 구체적으로 남기고 같은 T98을 재개한다.

그다음은 설명(T81–84) → 신경(T61–65의 기존 queue) → 근육 움직임(T35–T85의 기존 queue) → T40 전달이다. 모든 근육의 움직임을 신경 구현의 선행 조건으로 삼았던 규칙을 폐기했다. 엑셀 검증·한글 기능·짧은 운동/감각 표기·표정근 애니메이션 제외는 유지한다. 내장기 학습·경혈·치료는 추가하지 않았다.

## 단일 실행 기준

`work/EXECUTION.json`을 현재 순서·상태·범위의 유일한 원본으로 만들었다. 다음 ID는 첫 acceptance 미통과 task에서 계산한다. `work/tools/sync_execution.py`가 NEXT, 23 프롬프트, STATUS 현재 블록, R15 현재 투영을 생성한다. R15의 기존 taskStatuses는 역사 관찰값으로 표시하고 현재 상태는 currentTaskStates에 명확히 구분한다. AGENTS와 시작 문서, 흡수된 작업 명세에도 현행 기준을 안내했다.

역사 evidence의 nextTask는 덮어쓰지 않았다. 현재 지시로 따르지 않도록 진입 문서에서 구분한다. 다음은 **T98 / Luna Max**다. T104 보고서의 당시 T105 handoff를 현재 순서로 사용하지 않는다.

생성 도구의 일치·멱등성, 잘못된 NEXT 검출과 복구, 보고서 없는 pass 거부, 흡수 task 재활성화 거부를 격리된 임시 fixture에서 검증했다. 이는 실행 관리 도구 검사이며 앱 성능 검증이 아니다.

## 동시 작업과 Git 보존

시작 HEAD는 4aae135였고 감사 중 T104가 67d8b79로 커밋됐다. T104 보고서와 browser/performance/source 산출물을 다시 확인했으며 그 구현과 과거 handoff는 수정하지 않았다. 처음 증거가 없었던 상태와 이후 확인 기록을 모두 보존했다. T104의 passed_with_gaps는 정확한 10개 표면의 기술 통합 범위이며 전신 완료가 아니다.

이번 커밋에는 설계·명세 정정·EXECUTION·생성 도구·프롬프트·감사 기록과 AGENTS/시작 문서의 소유 안내 hunk만 포함한다. 사용자 변경이 섞인 STATUS/R15 파일 전체는 제외하고 소유 투영 delta를 기록한다. 원본 archive·엑셀·OpenSim·기존 WIP·앱 runtime은 포함하지 않는다. 커밋 해시와 잔여 변경은 최종 응답과 Git 기록에 남긴다. push·배포·T98 구현은 시작하지 않았다.

상세 설계: `design/2026-09-25-muscle-atlas/25-WHOLE-BODY-BASE-RESET.md`.
다음 프롬프트: `work/NEXT.md`. 전체 현행 프롬프트: `design/2026-09-25-muscle-atlas/23-PROMPTS-AFTER-T95.md`.
