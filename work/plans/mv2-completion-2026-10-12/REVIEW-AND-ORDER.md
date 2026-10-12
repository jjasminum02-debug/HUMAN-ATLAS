# MV2 완결성과 AT22 이후 실행

2026-10-12 사용자 요청에 따른 코드 검토·설계·프롬프트 정정. 시작 HEAD `e77e7e4dc295e8ba627e5860f361c514154609da`. 이번에는 motion/AT runtime과 실행 상태를 수정하지 않았다. AT22는 진행 중인 WIP이며 최종 결과로 판정하지 않았다.

## 결론

**핵심 변형 설계·수정은 Sol High, 고정된 절차의 반복 검사는 Luna Max**로 한다. 모델 이름이나 추론 설정만으로 품질을 보장하지 않는다. 이 배정은 아래 코드의 난이도에 따른 프로젝트 판단이다. 일반적인 역할 구분에는 [OpenAI Docs 모델 선택 안내](https://developers.openai.com/api/docs/guides/model-selection)를 참고했다.

MV2는 Q01 실패 때문에 partial이 아니다. `lastRun.acceptancePassed=true`이고, 전체에는 Q02–Q05 4묶음·32매핑이 남아 있다. MV1 미관찰은 0이다. 승인 대기로 막힌 상태가 아니다.

## 코드와 실제 기록에서 확인한 것

| 범위 | 확인 결과 | 후속 판단 |
|---|---|---|
| Q01 대퇴직근 | 부착 역할과 회전 가중치가 근복까지 잘못 배정돼 최대 약 82.9mm 돌출했다. 실제 source mask를 교정했고 각도·pivot·재생 방향·다른 70 node는 보존했다. | 원인을 겨냥한 수정이다. 기존 engineering pass를 보존한다. |
| Q01 학습 표현 | `repair-r2.py`는 근복을 고정하고 원위 전환 구간을 변형한다. `candidate-summary-r2.json`의 bodyMaxDisplacementMm는 좌우 모두 0.0이다. | 이 값만으로 잘못된 모델이라고 단정하지 않는다. 다만 돌출 제거 성공만으로 ‘수축이 이해되는 표현’까지 완료했다고 할 수 없다. 새 표현 인수 unit이 필요하다. |
| Q01 검증 | 좌우 각각 97시점, 실제 loader와 독립 replay, 부착 경로/복귀/주변 구조, 실제 화면 기록이 있다. | 과거 자동 검사와 실제 시각 판독을 구분해 재사용한다. 자연스러운 수축의 별도 표현 기준을 추가한다. |
| 교체 구조 | `sourceMotionRepairs.ts`가 exact base URI/hash와 전체 binding을 대조한다. `motionLearningData.ts`는 공통 resolver를 사용한다. | task별 loader나 엔진을 복제하지 않아 방향이 좋다. 후속 수정도 이 경로에 데이터로 등록한다. |
| Q02 예산 불일치 | 실제 trunk GLB는 31,306,820 bytes. `motionAssetByteBudget`는 기존 정확한 URI/hash에만 예외를 허용한다. 새 repair 경로는 plugin과 resolver 모두 8MiB까지만 허용한다. | 같은 규모의 새 Q02 자산은 현재 채택 경로에서 거절된다. Q02 시작 때 공통 예산 계약을 먼저 정리해야 한다. |
| 출력 크기 | Q01은 원본 buffer에 새 morph를 덧붙여 약 220KB씩 증가했다. 새 GLB는 약 3.3MB씩이며 선택 시 로드한다. plugin은 기존 등록 자산도 배포 산출물에 포함한다. | 원본은 보존하되 후속 exporter에서는 미사용 stream 누적을 피한다. 배포 전체 bytes와 현재 활성 geometry 비용은 따로 측정한다. |
| AT20 | 14경맥 정의 원장 + 오른쪽 폐경 아래팔 부분 경계. runtime 추가 비용은 0으로 기록돼 있다. | 모든 경맥 영역이 구현된 것은 아니다. |
| AT21 | 양측 아래팔 부분 mask 2개/702면. position/normal을 공유하고 index/weight/outline만 별도 생성. lazy load, 취소, 해제, raycast 제외가 있다. | 가벼운 공통 구조로 방향이 적절하다. 입력 JSON 10,600 bytes, 새 소유 배열 14,000 bytes. 전체 폐경 및 다른 13개 실제 면은 아직 아니다. |
| AT22 WIP | 원본 불변, stroke undo/redo, revision hash/비동기 epoch 검사, DEV 편집 경로를 확인했다. | 단일 편집 경로를 유지한다. 위경 fixture 편집 성공을 실제 위경 영역 완성으로 세면 안 된다. 진행 중 코드이므로 최종 통과 판정은 하지 않았다. |

읽은 핵심 코드: `atlas-web/src/domain/sourceMotionRepairs.ts`, `src/data/motionLearningData.ts`, `plugins/motionAssets.ts`, `src/viewer/acupoints/{territoryMask,territoryEditor,TerritoryEditorReview}.ts(x)` 및 관련 테스트, `work/evidence/MV2/2026-10-12-q01-r1/repair-r2.py`와 최종 검증. AT20의 근거와 경계 입력 범위는 실제 보고서/검증 기록에서 확인했다. 저장소 전체의 무결함을 주장하는 감사는 아니다.

## 구현 원칙

1. 부착부/경로/가중치/접촉 보정은 offline에서 작성·검증한다. 앱은 검증된 morph/clip과 compact metadata를 재생한다. 실시간 전신 물리 solver나 별도 viewer는 만들지 않는다.
2. 두 번째 실제 사용이 생길 때 필요한 공통 부분만 parameter로 추출한다. Q01의 vertex 번호나 world-Y 절단을 다른 근육에 복사하지 않는다. 새 범용 프레임워크를 먼저 만드는 작업도 피한다.
3. source/frame/topology/clip이 변한 항목만 다시 검사한다. 동일 원인 항목을 내부 loop로 처리하고 task별 runtime 분기를 늘리지 않는다.
4. 최종 파일은 필요한 accessor/bufferView/animation만 갖도록 하되 재생 동등성을 검증한다. 원본은 별도로 보존한다. 이전 수정본에 수정본을 계속 덧붙이는 patch chain은 만들지 않는다.
5. evidence·실패 후보·전체 authoring 원장은 learner bundle에 넣지 않는다. 현재 일부 데이터가 큰 것과 실행 장면이 무거운 것은 구분한다. 배포 목록 최적화는 원본 삭제 없이 가능하다.

## 학습 동작의 완료 기준

최종 결과는 교육용 모형의 설명 가능한 시범이다. 정밀 조직 물성·정상 ROM·임상 유효성 인증을 요구하거나 주장하지 않는다. 문헌의 정성적 작용과 AI가 작성한 모델 경로·가중치를 분리한다.

| 기준 | 필수 증거 |
|---|---|
| 준비·작용·복귀 | 역재생을 포함한 시간/단계를 대응시킨다. 준비 자세의 변화와 실제 작용 구간을 혼동하지 않는다. |
| 근육 표현 | 근육·부착 주변·관절을 같이 보여주는 동일 구도에서 1배속과 필요 시 느린 재생을 판독한다. 색 변화/통째 rigid 이동/고정만으로 수축 완료라고 하지 않는다. |
| 설명 가능한 변형 | source-addressed 부착 영역과 중심 경로 등을 근거로 필요한 길이·윤곽 변화를 작성한다. 모든 근육을 같은 비율로 부풀리거나 정적 mesh 전체 scale로 대체하지 않는다. |
| 기하 품질 | 기존 부착 경로/면적/면 뒤집힘/접촉 검사를 유지한다. 변화가 큰 keyframe 사이도 검사한다. contained vertex 0을 모든 표면 교차 부재의 증거로 확대하지 않는다. |
| 시간 연속성 | 왕복 경계, 빠른 중단/재시작, 좌우/근육 전환에서 튀는 프레임이 없는지 확인한다. 종료 후 원본 geometry/선택/레이어를 복원한다. |
| 모드 전환 | 움직임 종료→경혈 점/AT21 면→닫기와 AT22 검토 종료를 확인한다. 정지 pose용 경혈 좌표를 변형된 pose에 그대로 붙이지 않는다. |
| 비용 | bytes/활성 geometry/draw/지연 로딩/해제 before-after를 기록한다. 제품 카메라/레이아웃은 변경하지 않는다. |

길이·부피는 신뢰 가능한 경로/폐곡면이 있을 때만 측정한다. 결손 표면에 가짜 부피 지표를 강제하지 않는다. volume 보존을 사용한다면 완만한 교육용 변형 제약으로 명시하며 보편적 생리 법칙처럼 하드코딩하지 않는다. 지표 단위·허용 기준·적용 범위를 실제 입력에 맞춰 기록하고 기존 기준을 무작정 완화하지 않는다.

## 실행 순서와 담당

**AT22 종료·검증·소유 로컬 커밋 후** 아래 순서를 사용한다. 모두 기존 MV2 내부 unit이며 새 task 번호는 발급하지 않는다. 한 실행은 한 unit을 끝내고 다음을 자동 실행하지 않는다.

| 순서 | unit | 담당 | 끝내야 할 것 |
|---|---|---|---|
| 1 | `q01-learning-quality` | Sol High | 기존 돌출 수정본을 기준 사례로 삼아 수축·작용의 학습 표현을 검증·필요시 보완. 기존 Q01 engineering resolved는 보존. |
| 2 | 기존 Q02 외복사근 1매핑 | Sol High | 겹침/관통/가림 분리와 원인 해결. 기존 31MB 예외와 새 8MiB repair 제한의 계약 불일치도 이 unit에서 해결. |
| 3 | 기존 Q03 위팔두갈래근 3매핑 | Sol High | 팔꿈치·어깨 짧은갈래 부착/가중치/가림 원인 해결. Q01 수리법을 억지로 적용하지 않음. |
| 4 | 기존 Q04 손 말단 26 + Q05 깊은 몸통 2 검사 | Luna Max | Sol이 고정한 도구·기준으로 실제 국소 관찰과 회귀를 수행. 실제 결함을 재현 가능한 Sol 인계로 변환. |
| 5 | Q04/Q05 실제 결함 수정 및 마지막 인수 | Sol High | 확인된 공통 원인 한 묶음씩 수정. 마지막에는 영향 범위 회귀와 Q01/대흉근 비교, 경혈/영역 왕복 확인. 실제 결함이 없으면 geometry 수리는 생략. |

Luna에 넘길 조건은 알고리즘·기대 형태·검사 도구가 고정됐을 때다. 새 부착 역할/weights/pivot/frame/접촉/예산 계약 판단은 Sol이 맡는다. 반복 캡처 도구라도 scene ownership 변경이 필요하면 Sol로 돌린다. 모델을 자주 바꿔 맥락을 재수집하지 않는다.

동작 완결성을 우선한다면 AT22 다음에 위 MV2 흐름을 정리한 뒤 기존 경혈 순서 **AT8→AT9…**로 복귀한다. 이는 추천 우선순위이며 AT8에 새 MV2 의존성을 추가하는 것은 아니다. 카메라 거리·자동 이동·연출·패널 개편은 사용자가 요청할 후속 UI 작업에 묶는다. AT20/21을 되돌리거나 AT7 카메라를 재실행하지 않는다.

Q04/Q05 검사는 제품 카메라 개선이 아니다. 기존 수동 맞춤으로도 판정하지 못하면 unresolved다. 국소 변형은 확인됐고 자동 framing만 부족하다는 근거가 있을 때에만 UI backlog로 분리한다. 작은 근육이라는 이유로 정상 처리하지 않는다.

## 상태와 종료

기존 MV1 freeze 및 Q01 resolved_engineering은 바꾸지 않는다. MV2 최신 versioned queue에 기술 판정, 학습 표현 판정, UI 보류, evidence를 분리한다. 새 전역 상태 엔진은 필요 없다.

- `passed`: 실제 검사·판독 근거가 있음.
- `needs_repair`: 재현한 결함과 다음 수정 대상이 있음.
- `observed_ambiguous`: 관찰했지만 판단 근거가 부족함.
- `presentation_deferred_to_ui`: 국소 변형은 확인됐고 자동 카메라/배치만 남음. 사용자 요청으로 보류하며 그래픽 전체 완료로 부르지 않음.

각 run의 unit acceptance와 MV2 전체 잔여를 따로 기록한다. 모든 필수 원인·표현 문제가 해결돼야 scoped MV2를 complete로 바꾼다. 남은 UI가 있다면 전체 경험은 미완임을 명시한다. 승인 문구 삭제/일괄 pass로 닫지 않고, 선택적인 정밀 생리 검토 미수행만으로 교육용 그래픽 기술 작업을 영구 partial로 남기지도 않는다.

이번에는 EXECUTION/AT record를 편집하지 않았다. 현재 nextRepairUnit=Q02와 새 표현 unit의 차이는 명세에 명시했으며, 실제 재개자가 자신의 MV2 실행 결과로 갱신한다.

## 이번 검토의 검증

- Q01 새 GLB 2개의 hash·크기를 manifest와 다시 대조: 일치.
- Q02 기존 파일 실제 크기: 31,306,820 bytes.
- 현재 checkout에서 `sourceMotionRepairs.test.ts` + `plugins/motionAssets.test.ts`: **6/6 통과**.
- 기존 MV2 전후 PNG, AT21 최종 LU7 PNG를 직접 열어 확인. 새 브라우저 재생 전수 검사는 수행하지 않음.
- 기존 `emitted-validation.json`과 AT21 `validation-final-r1.json`을 검토. 기존 97시점/66 tests/13 build 결과는 이번에 재실행한 것이 아님.
- AT22 WIP는 읽기만 했으며 build/최종 상태 승격/화면 조작을 하지 않음.

실행에는 [Sol 프롬프트](MV2-SOL-RESUME.md), 고정 검사 인계에는 [Luna 프롬프트](MV2-LUNA-VERIFY.md)를 사용한다.
