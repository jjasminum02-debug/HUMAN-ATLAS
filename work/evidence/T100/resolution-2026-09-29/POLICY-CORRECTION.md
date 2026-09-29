# T98 이후 반복 중단의 원인과 교정

2026-09-29 · T100 내부 수정 · 현재 대화

문제는 Luna의 코딩 능력이나 OpenSim 정합 실패가 아니라 **단계별 미실행 상태를 영구 금지로 읽은 설계·실행 경로**였다. 기존 AGENTS R13에는 사람 검토가 선택 사항이라고 이미 적혀 있었지만, 이후의 광범위한 hold 보존 문구와 재개 프롬프트가 이를 가렸다. 이번 대화에서도 처음에는 동일하게 QA 표시만 허용하는 구현을 만들었고, 사용자의 지적 후 아래와 같이 교정했다. 그 초기 QA 증거는 당시 기록이며 현재 완료 판정의 근거가 아니다.

## 원인 → 코드와 지침 교정

1. T98/T99 `held_not_approved_by_this_task`는 선행 task가 표시 결정을 하지 않았다는 뜻인데 T100의 영구 차단으로 해석했다. 원본 상태는 변경하지 않고 **T100 현재 local-use decision overlay**를 추가했다. 고정된 ZA 원본 객체와 family를 pinned README의 파생 이용 근거/예외에 연결한다.
2. `source_only_unbound`, 사람 검토 미수행, 공개 배포 보류를 같은 조건처럼 사용했다. 현재 `canDisplayLocally`는 로컬 이용 근거, 실제 hard hold, source viewport hide, 구조 분류를 본다. humanReview/public release 상태는 그 predicate의 차단 조건이 아니다. `DatasetResources`는 검증한 현재 로컬 표시 key를 별도로 받는다.
3. 원본에 없는 공식 FJ/TA2 ID를 찾기 전에는 의미 연결을 못 한다는 해석이 생겼다. **source Object/parent/collection/evaluated hash**가 exact source identity다. HA 학습 의미는 기존 표준 row, exact term, system, side, source identity를 교차 확인한 AI project crosswalk로 연결한다. provider가 TA2 ID를 선언했다거나 사람이 승인했다고 만들지 않는다. parent/part 혼동·fuzzy 이름 후보는 연결하지 않는다.
4. 현재 코드 검사에 T102 당시 AGENTS.md hash freeze가 들어 있어 올바른 지침 정정도 실패로 나타났다. `test:whole-body`는 현재 runtime, 공통 dataset, 검증된 BP3D/ZA compiled dependency와 **46개 실제 chunk hash**를 검사한다. 원래 검사는 `test:whole-body:historical`로 그대로 보존했다. 과거 실패를 pass로 변경하거나 과거 hash를 덮어쓰지 않았다.
5. QA 전용 모형만 만들고 실제 앱 연결을 미뤘다. 일반 `/` 앱이 같은 WholeBodyViewer/AnatomySceneController를 통해 ZA를 기본 표시한다. BP3D를 겹치지 않고 기존 compiled BP3D subset 회귀는 유지한다. 별도 T100 QA UI는 제거하고 동일 제품 경로를 검증한다.

## 현재 범위

- 960 원본 표면을 보존. 원본 분류 509 muscle/part, 277 skeletal, 174 accessory는 역사 그대로.
- 실제 분류에서 힘줄/인대/연골/치아/근막 등을 근육·뼈로 오인하지 않도록 분리. **672개 표면(근육/부분 462, 뼈 210)**을 로컬 기본 표시한다. 고유 근육 개수가 아니다. 나머지 288개는 삭제하지 않았다.
- 기존 검증 명칭·표준 참조에 **130 surface instances / 65 HA concepts**를 연결. 세 이름을 모두 가진 표시 표면은 123개다. 그 밖에는 확인된 영어 source label을 제공한다.
- TA2 target 360개에 source-taxonomy 대응 후보가 있다. 130개 instance의 HA 연결과 360개 target 후보는 다른 단위다. 182개 target은 변이·부분/묶음·동의어·누락을 더 정리해야 한다. 이를 182개 누락 근육이라고 부르지 않는다.
- `Iliocostalis colli muscle`은 현재 표시 source 목록에서 오른쪽만 확인된다. 대칭 복제하지 않고 실제 반대쪽 source/분류를 확인할 항목으로 남긴다.
- 기존 T98/T99 manifest, 공개 재배포 hold, 사람 검토 미수행 기록은 그대로다. 로컬 사용 결정이 공개 배포 승인이라는 뜻은 아니다.

## 이후 Luna 실행 규칙

25 설계 마지막 정정과 현재 `work/NEXT.md`를 따른다. `not_approved_by_this_task`를 다시 조사 대기로 적는 대신, 현재 overlay/근거와 실제 hard hold를 확인한다. 이미 검토된 source family·객체·단위·compiler를 처음부터 재조사하지 않는다. 남은 target·이름·실제 형상 누락 unit만 처리한다. 사람 검토 미수행이나 공개 배포 보류만으로 중단하지 않는다.

**승인 대기 설계 결함은 교정했지만, 실제 target·명칭 미완까지 완료로 바꾸지는 않았다.** T100의 전신 학습 완성은 아직 partial이며 T80/T58은 시작하지 않았다.
