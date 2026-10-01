# 전체 근육 움직임 — 현재 구조 판단과 실행 계획 변경

2026-10-02 · 사용자 요청에 따른 **계획·프롬프트 개정 완료**. T35/T59 또는 parallel worker를 실행/합격 처리하지 않았다. 현재 다음 task는 **T35**, 선행 T65는 실제 `completed/passed`다.

최신 요구는 특정 주요 근육 shortlist가 아니라 **프로젝트 전체 근육을 대상으로 제작·검증을 진행**하는 것이다. 초기 예시/파일럿은 공통 경로 검증 수단이며 전체 확장 대상의 제한이 아니다. 전체 목표로 계획과 future spec/prompt/acceptance scope를 바꿨다.

## 판단

현재 전신 화면·선택·source identity·지역/카드/controller는 재사용할 수 있다. 그러나 현재 근육은 정적 geometry이고 App의 movement CTA는 disabled다. 실제 같은-model muscle motion 지원은 0이다. 역사 T24의 asset 1개는 OpenSim 뼈+작용선 후보이며 원래 근육 표면 수축에 미달했던 과거 결과다.

따라서 필요한 개발은 ‘각 근육 버튼에 애니메이션 하나 추가’가 아니다. 현재 선택한 source 표면이 관절/몸 움직임과 함께 변형되고 원래 상태로 복원되는 **공통 제작 경로**를 만들어야 한다. 정적 dataset loader는 skin/animation을 거부하고 geometry만 추출하므로 기존 GLTFLoader/player 코드를 재사용하더라도 dynamic graph/instance weights/source 결속을 명시적으로 보존해야 한다. 기존 단일 scene/renderer/camera/controller는 유지한다.

움직임 자체는 관절/family 단위로 공유하지만 source별 부착·갈래·좌우·작용 조건과 실제 deformation은 개별 자료다. 소원근과 대원근처럼 가까운 근육도 같은 작용/같은 변형을 통째로 복사할 수 없다. 넓은 부채꼴·다관절·반복/분절·비관절 soft-tissue는 같은 데이터 계약의 다른 유형으로 다뤄야 한다. skinning과 morph/corrective deformation을 유형별로 사용하고 정량 힘·환자별 수축량을 추정하는 biomechanical solver는 일괄 선행 조건으로 늘리지 않는다.

OpenSim의 geometry path는 작용선이다. 실제 근육 표면이나 ZA 모델과의 정합을 자동 제공하지 않는다. 이는 [공식 Muscle Editor 문서](https://opensimconfluence.atlassian.net/wiki/spaces/OpenSim/pages/53090145)와 역사 T24의 관찰이 일치한다. 웹 전달 형식은 기존 self-contained GLB를 재사용하고 skin/morph animation은 [glTF 2.0 공식 계약](https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html)에 맞춰 보존한다.

## 전체 범위와 준비 상태

| 원장 | 실제 범위 | 의미 |
|---|---:|---|
| 전체 제품 | 542 target / 563 membership / 12부위 | 기존 분모 보존 |
| 근육 관련 target | 429 / muscle membership 447 | whole/part/group/complex/repeated family가 섞임; 서로 다른 실제 근육 429개가 아님 |
| 현재 지원 source 근육 | 232 source 개념 / 462 표면 | 기존 source별 근육 표면 전수 제작 대상 |
| 현재 기시·정지 카드 | 31 개념 / 62 표면 | 설명 또는 기존 충돌 안내; T65 실제 결과 재사용 |
| 남은 기시·정지 설명 | 201 개념 / 400 표면, origin conflict 1개 | 실제 자료 부족이며 geometry 부재가 아님 |
| 현재 같은-model 움직임 | 0 | legacy technical candidate를 제품 지원으로 세지 않음 |

245 named muscle, 94 part, 58 group, 26 repeated family, 6 complex의 429개 target을 전수 작업 범위로 유지한다. 현재 없는 target도 제작 대상/미확보 과제에서 삭제하지 않는다. source-only 항목에 HA ID를 강제하거나 기존 HA130을 바꾸지 않는다. 전체 개인 근육 분모는 기존처럼 null이다. 최신 전체 근육 지시에 따라 과거 **미래 표정근 clip 제외 문구도 대체**했으며, 표정/안구/혀 등 비관절 운동의 자료/변형 계약을 별도로 확인하도록 했다.

고정 research manifest는 `work/evidence/motion-all-muscles-plan-2026-10-02/run-manifest.json`에 실제 생성했다. source HEAD/hash, 원본 전체 입력 SHA, 최소 projection snapshot hash, 최종 배정 IDs/output ownership이 있다. 일부 예시만 넣은 manifest가 아니다. 정적 입력 11개 전체 hash를 고정하고 대형 overlay 전체를 복제하는 대신 필요한 전수 필드 snapshot만 저장했다.

| worker | 지역 소유 | target | source 개념 | 표면 |
|---|---|---:|---:|---:|
| A | 머리·목 | 144 | 66 | 131 |
| B | 어깨·팔/손·가슴우리·배허리·골반샅 | 139 | 76 | 151 |
| C | 등·볼기·넙다리·종아리·발 | 146 | 90 | 180 |
| 합계 | 전체 12부위 | 429 | 232 | 462 |

지역은 writer 배정 기준이며 다지역 membership이나 실제 움직임 family를 줄이는 기준이 아니다. 다른 worker의 source/target은 읽기 교차 참조만 하고 group/관절 dependency는 통합자가 조정한다. 조사 출력은 candidate/계획 입력이며 runtime acceptance가 아니다.

## 가장 효율적인 순서

1. **T35 + 조사 A/B/C**: 전수 identity/geometry/부착/작용/pose/제작 필요 입력을 확인하고 공통 motion-contract를 만든다. 조사 3개는 준비된 manifest를 기준으로 서로 다른 evidence 폴더만 쓰므로 동시에 진행할 수 있다.
2. **T59**: common source-preserving exporter·rig/deformation adapter·same-scene player·lazy load/cache·취소·복원 경로를 구현한다. 기존 static renderer와 animation parser/player를 연결한다. 실제 계약 검증 표본은 전체 원장에서 선택하며 초기 확장 목록으로 고정하지 않는다. 자산 worker용 실제 authoring manifest와 validator를 만드는 것을 완료 조건에 넣었다.
3. **T25**: 같은 앱의 전신 탐색→source muscle/작용→실제 movement→설명/숨김/복원 flow를 연결한다. 이때 frozen authoring contract 아래 candidate assets는 parallel 제작할 수 있다.
4. **T66 + 자산 A/B/C**: 전수 원장의 제작 가능 패키지를 같은 exporter로 제작한다. worker는 자기 asset candidate만 작성한다. 통합 writer 하나가 hash/계약/상태를 검사해 등록한다. 몇 개 예시 성공으로 끝내지 않고 실제 제작 가능으로 확정한 모든 패키지를 처리한다.
5. **T85**: 지원된 모든 clip/side/part/action을 자동 검사하고 유형/변경 화면·12부위·390/1024/1440에서 실제 흐름과 성능을 다듬는다.
6. **T40**: 실제 로컬 실행과 전체 목표의 구현/미확보/미구현 원장을 전달한다. 전체 목표가 partial이면 실제로 그렇게 표기한다.

다른 source/family 자료와 자산의 독립 작업은 병렬화할 수 있다. 동일 skeleton/관절/pose·player·App·EXECUTION을 여러 writer가 동시에 바꾸면 충돌/정합/복원 QA를 재작업하므로 그 부분은 단일 작성자다. 요청한 앱의 주요 작업 비용은 **source별 입력과 실제 변형·주변 맥락 검증**에 있으며 코드 병렬화만으로 없앨 수는 없다. 근거 없는 제작 일수·전체 지원 수를 약속하지 않고 실제 유형별 제작/QA 비용을 측정하게 했다.

전체 목표와 task responsibility acceptance를 분리한다. 계획 pass는 clip 구현이 아니고, 공통 player의 표본 pass도 전 근육 지원이 아니다. T66은 제작 가능으로 확인한 패키지가 남았으면 미구현 unit으로 계속 처리한다. source/정확한 anatomy 입력이 실제 미확보인 경우에는 전수 원장에 구체적 필요한 자료/다음 행동을 남긴다. 단순 ‘힘든 근육’이나 쉬운 표본의 성공만으로 나머지 근육을 범위에서 빼지 않는다.

## 개별 실행 프롬프트와 변경 파일

- T35: `work/prompts/app-completion-2026-10-01/13-T35.txt`
- 동시에 가능한 조사: `work/prompts/motion-all-muscles-2026-10-02/02-research-A.txt`, `02-research-B.txt`, `02-research-C.txt`
- T59 공통 제작: `work/prompts/app-completion-2026-10-01/14-T59.txt`
- T25 학습 UI: `work/prompts/app-completion-2026-10-01/15-T25.txt`
- **T59 actual authoring manifest 검증 뒤** 자산 제작: `work/prompts/motion-all-muscles-2026-10-02/04-authoring-A.txt`, `04-authoring-B.txt`, `04-authoring-C.txt`
- T66 통합: `work/prompts/app-completion-2026-10-01/16-T66.txt`
- T85 품질: `work/prompts/app-completion-2026-10-01/17-T85.txt`
- T40 전달: `work/prompts/app-completion-2026-10-01/18-T40.txt`

각 prompt는 별도 파일이며 합치지 않았다. `work/prompts/motion-all-muscles-2026-10-02/README.md`에 적용 시점을 적었다. 단계2 authoring manifest는 아직 실제 motion 계약이 없으므로 지금 만들어진 것으로 쓰지 않았다. 대신 T59 출력/합격 계약에 필수로 넣어 미래 담당자가 manifest 없이 배정받는 문제를 막았다.

동일 ID/순서를 유지하며 여섯 future spec·canonical promptFile, EXECUTION scope/acceptanceContract의 추가 요건, product-acceptance future motion amendment를 갱신했다. 27의 acceptance revision과 완료한 task 결과는 그대로다. 상세 설계는 `28-ALL-MUSCLE-MOTION-PIPELINE.md`다. 자동 생성 NEXT/prompt book/registry는 sync 도구로 투영했다. 과거 T24/T35 역사 파일 및 기존 WIP는 수정하지 않았다.

## 검증·보존

전수 manifest validator가 입력/snapshot SHA, 429 target/447 membership/232 source/462 표면의 **누락·중복 0**, 12부위 및 배정 output ownership을 검사했다. sync_execution.py와 --check를 수행했다. future task의 acceptance/executionStatus/completedUnits는 이전과 같으며 아직 T35를 시작하거나 passed 처리하지 않았다. 코드 변경은 계획 manifest validator뿐이고 제품 runtime/geometry/기존 accepted evidence는 바꾸지 않아 앱 전체 suite/browser를 다시 실행하지 않았다.

원본/OpenSim_Models/T13/WIP, 기존 HA130, 역사163(6/20/135/2), product542/563/12, source-only/held/not_performed를 보존한다. 실제 보존/계획 검증은 `work/evidence/motion-all-muscles-plan-2026-10-02/planning-validation.json`에 남긴다. 다른 task/agent/thread, 자산 제작, push·배포·임상 기능은 이번 요청에서 실행하지 않았다.
