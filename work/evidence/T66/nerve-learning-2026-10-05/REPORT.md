# T66 신경 학습 내부 단계 — 2026-10-05

## 수행 범위

지원 중인 신경의 정적 주행과 근거가 확인된 지배·관련 근육을 학습 카드에 연결했다. 기존 신경 색상/선택, 첫 선택 시 표시, 사용자가 명시한 레이어 끔 유지, 같은 쪽 등쪽어깨신경–능형근 맥락 강조는 입력으로 재사용했다. 195개 정적 신경 source 표면과 98개 source label group은 원래 분모로 보존했으며, 98을 독립 신경 개념 수로 해석하지 않았다.

## 구현 결과

- 현재 learner graph에는 관계 행 18개가 있다. 기존 exact side geometry 2행은 깊은종아리신경에서 좌우 앞정강근 표면으로 연결된다. 문헌 개념 관계 16행에는 기존 등쪽어깨신경에서 큰/작은능형근으로 가는 관계 2개가 포함되며, 이번에 추가한 문헌 관계 행은 14개다.
- 관계에 포함된 고유 nerve key는 9개, 대상 sourceKey는 44개다. 이는 독립 해부 개념이나 고유 근육 수가 아니다. 문헌 관계에는 좌우를 부여하지 않았다. 카드에서 현재 표시 가능한 같은 쪽 근육 표면을 선택하는 것은 신경 가지와 근육 표면의 좌표 대응이 아니다.
- 등쪽어깨신경은 큰/작은능형근과 어깨올림근, 겨드랑신경은 삼각근 표시 부분 집합과 작은원근, 안/가쪽가슴근신경은 큰가슴근 표시 부분 집합, 넙다리신경은 넙다리곧은근, 가슴사이신경은 일부 복직근/바깥배빗근, 정중신경은 원엎침근·노쪽손목굽힘근·긴손바닥근·얕은손가락굽힘근 부분 집합, 노신경은 위팔노근·긴노쪽손목폄근의 관계를 연결했다. 각 카드 설명은 문헌 범위와 source mesh 분할의 한계를 밝혀 전체 지배 범위나 가지별 footprint로 오해하지 않게 한다.
- 외측·후방대퇴피신경은 넙다리신경과 분리했다. 운동 관계가 현재 연결되지 않은 감각 주행 사례는 “현재 연결된 관계 없음”으로 표시하며, 해부학적 부재로 단정하지 않는다.
- 신경 카드에는 정적 주행 요약, 근거가 있는 관련 근육 선택, runtime에 검증된 작용 설명을 연결했다. 검증된 `muscle_action`일 때만 기존 재생 경로로 이동한다. 자세 관찰은 작용 목록에서 제외하고, 작용 설명이 연결되지 않은 근육은 그 상태를 알린다.
- 새 신경 mesh/가지 좌표, HA ID, canonical/target binding, 힘·활성도 수치, 포착 좌표는 만들지 않았다. `sourceOnly=true`, 기술적 로컬 선택, 공개 권리 held, `humanReview=not_performed`를 유지했다.

## 근거 확인

기존 T25/T65/T61와 worker F의 검증된 근거 및 locator/hash를 재사용했다. 추가한 개념 관계는 출처와 범위를 `nerve-relation-ledger.json` 및 `input-manifest.json`에 기록했다. 등쪽어깨신경 연구는 사체 70구/140측에서 능형근과 어깨올림근 관계 및 중간목갈비근 주행 변이를 보고했다. 겨드랑신경 해부 연구는 23구에서 작은원근 가지와 삼각근 구역 공급을 살폈다. 큰가슴근 연구는 15구 30 표본에서 안/가쪽가슴근신경 기여와 일부 가슴사이신경 기여를 보고했다. 정중신경 연구는 20개 팔에서 원엎침근·노쪽손목굽힘근·긴손바닥근·얕은손가락굽힘근 관계와 분지 변이를 다뤘다. 복부 문헌은 가슴사이신경과 일부 복벽근 관계 및 복직근의 분절성 주행을 다뤘다. 이 근거는 문헌 수준의 개념 관계이며 source model의 신경 가지 좌표로 변환하지 않았다.

## 검증

- `python3 work/tools/build_t66_nerve_learning.py --check`: 통과. exact geometry 2, 문헌 관계 16, 총 18행, 관계에 포함된 unique nerve key 9개와 target sourceKey 44개.
- `python3 work/tools/validate_t66_nerve_learning.py`: 통과. 195 source 표면/98 label group, relation scope·좌우·field/hash 및 negative-scope 검사, findings 0.
- `node --experimental-strip-types --test src/data/t66NerveLearning.test.ts`: 6/6 통과.
- `tsc -b --pretty false`: 통과.
- Vite production build: 통과. 기존 500 kB 초과 JS chunk 경고가 남는다.
- 실제 브라우저에서 깊은종아리·등쪽어깨·겨드랑·노·정중·넙다리신경과 두 대퇴피부신경의 대표 선택 흐름을 확인했다. 깊은종아리신경 오른쪽에서 오른쪽 앞정강근 표면과 검증된 작용/기존 clip 링크를 열고, 재생 중 표면 변화와 정적 신경의 비지원 움직임 pose 숨김, 재클릭 rest 복귀를 확인했다. 등쪽어깨신경에서 같은 쪽 능형근/어깨올림근 context와 선택 일치도 확인했다. 사용자 신경 layer-off는 좌우 전환 후에도 유지됐고 직접 다시 켤 수 있었다.
- 이번 실제 viewport는 825×807 CSS px, DPR 2, document scroll width 825, canvas 1, console errors 0이다. 이는 모바일 실기기나 390/1024/1440 검증으로 확대하지 않는다. 캡처 SHA-256과 바이트 수를 `browser-validation.json`에 기록했으나 화면은 CUA에서 인라인으로만 확인했고 저장된 PNG/JPEG 파일은 없다.

## 미완 항목과 T66 상태

이번 신경 학습 경로는 구현되고 대표 UI에서 검증됐다. 이는 전체 신경 관계, 독립 신경 개념 목록 또는 신경 가지의 3D 연결이 완성됐다는 뜻이 아니다. worker F의 98개 source row 중 30개 work key는 기존 field evidence가 검증됐고, 68개는 구체적 관계/원문 근거 미확보 상태로 남는다. 전체 신경 text coverage, 동적 신경 자세, spatial entrapment coordinates는 미완이다. 일부 관련 근육에는 현재 근거 있는 작용 문구가 연결되어 있지 않아 UI가 그 사실을 표시한다.

부모 T66은 `in_progress / partial`, `nextUnit=author-and-integrate-normal-motion-bone-and-nerve`로 유지한다. 우선 일곱 근육군 중 실제 작용 재생이 확인된 표면은 현재 오른쪽 앞정강근 하나뿐이며, 나머지 우선 근육의 제작과 마지막 통합이 남아 있다. 이 내부 단계만으로 T66을 complete/pass 처리하지 않는다.

다음 수동 파일은 `work/plans/t66-priority-atlas-2026-10-05/02-ankle-knee.txt`다. 자동 실행하지 않았다.
