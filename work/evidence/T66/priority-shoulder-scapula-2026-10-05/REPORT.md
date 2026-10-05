# T66 우선 내부 03 — 대흉근·견갑거근·능형근

이번 내부 단계는 **completed / passed**다. 부모 T66은 **in_progress / partial**, `nextUnit=author-and-integrate-normal-motion-bone-and-nerve`를 유지한다. 이번 범위는 실제 확보된 source part/side의 대표 작용이며 전체 TA2 근육군·정상 ROM·전신 콘텐츠 완료를 뜻하지 않는다.

| 근육 / 실제 원본 범위 | 대표 작용 | 양측 표면 | GLB |
|---|---|---:|---:|
| 대흉근 쇄골부·흉늑부·배부분 각각 | 팔 모음: 벌린 준비 자세 → source 기준 자세 | 6 | 신규 2, 세 부분이 같은 가족 자산 재사용 |
| 견갑거근 | 어깨뼈 올림 | 2 | 기존 2의 실제 방향·부착 문맥·기하 확인 후 재사용 |
| 대능형근·소능형근 각각 | 어깨뼈 뒤당김: 앞쪽 준비 자세 → source 기준 자세 | 4 | 기존 2의 역방향 작용 확인 후 재사용 |

정확한 source/action selector **12개**, 고유 GLB **6개(신규2 / 그대로 재사용4)**, package당 원본 주변 표면 **117개**다. 앞선 02와 합쳐 우선7근육군 중 **5개 군**, native source 표면16개, 정확한 작용 연결18개, 고유 GLB12개다. source 표면·작용·GLB·우선 군은 별개 분모다. 복직근·외복사근과 마지막 통합은 남았다.

## 실제 작성과 재사용 판정

UAMS의 각 근육 행에서 정성적 작용·부착을 확인하고 기존 attachment 원장과 대조했다. 새 교육용 masks/weights/trajectories를 실측 footprint·관절축·정상 ROM·힘으로 표현하지 않았다. `qualitative-action-evidence.json`, `reuse-scope-probe.json`, `action-outcome.json`에 locator와 실제 값이 있다.

견갑거근은 실제 어깨뼈가 위로 8.82/9.30 mm 이동하고 source-specific 끝점 문맥이 짧아지는 올림 자산을 재사용했다. 능형근은 앞쪽이동 자산 자체를 작용으로 바꾸지 않았다. 준비 구간을 구별하고 역방향에서 어깨뼈가 뒤·안쪽으로 이동하며 대/소능형근이 각각 짧아지는 실제 결과를 검사했다. 고정 masks의 오차는 1 μm 이하, 작용 방향의 endpoint-span 변화는 모든 65 검사 자세에서 일관된다. 이 수치는 교육용 기하 결과이며 생리적 수축량이 아니다.

대흉근 흉늑부·배부분의 기존 whole-surface TRS를 새 source-specific morph로 교체했다. native 양측의 넓은 몸통 쪽 masks를 유지하고 위팔뼈 쪽 masks와 free weights를 작성했다. 얇은 원본 taper의 국소 weight transition을 수리했다. 8° 준비 자세의 고정 부착 문맥·표면·실제 bone contact를 key/mid 포함65자세에서 검사했다. 새로운 4표면의 flipped-face와 새 bone containment는0이며 최소 면적비는0.265다. 쇄골부의 기존 변형은 실제 shortening과 동일 emitted vertex replay로 재사용했다.

주변 문맥을34개 native 표면씩 확장하는 중 기존 팔 벌림 자산이 Longissimus capitis/Splenius capitis까지 팔과 함께 움직이는 것을 발견했다. **새 priority 시범에서는 이 두 목 표면을 source 위치에 고정**했고 추가 뼈와의 접촉을 재검사했다. 나머지79개 원래 표면은65자세에서 기존 emitted 결과와 최대 오차0으로 일치한다. 원래 generic posture 기록·GLB는 덮지 않았다. 이 단계가 다른 모든 generic posture 가족까지 수정·승인했다는 주장은 하지 않는다.

원래6 authoring record의 **126개 고정 dependency hash**가 실제 파일과 일치한다. 기존 견갑대 GLB4개와 그 QC를 반복 제작하지 않았다. 대흉근의 바뀐4표면, 추가 native 문맥, 수정한 목 표면 및 실제 작용 결과만 집중 검사했고 재사용 receipt를 명시했다. 새 GLB 전체 hash와 일부 unchanged-buffer QC 재사용을 구별했다.

## 화면과 공유 player

한 scene/renderer/camera/clock/player에서 정확한 source part/side로 등록했다. 한 CTA의 반복 왕복·재클릭 smooth rest·scrub 및 준비/작용 구분을 유지했다. slow/pause/reset 버튼이나 별도 viewer는 추가하지 않았다. 깊은 견갑거근·능형근은 주변 근육을 관찰용 반투명으로 유지하고 뒤쪽에 가까이 잡는다. 표면을 삭제하거나 force/activation처럼 표시하지 않는다. 팔·손 등117개 문맥은 계속 존재하며, 초기 관찰 프레임만 해당 움직임 주변으로 잡는다. 수동으로 고른 방향은 우선하며 재생·scrub 중 계속 camera를 재설정하지 않는다.

실제 **1280×720 CSS 브라우저**에서12 source/part/side 모두 rest/mid/end, loop, 재클릭→완전 rest를 확인했다. 한 canvas를 유지했다. 선택 숨김과 근육 layer-off는 시범을 중단하고 자동 재표시하지 않았다. 보기 복원, 키보드 카메라, 뒤/앞 이력도 확인했다. 기존 견갑배신경 카드의 대/소능형근·견갑거근 links에 새 대표 작용 설명이 나타나고 동일 근육 선택으로 이어진다. 관계 좌표/신경 동적 pose/실제 힘을 새로 승인하지 않았다. console error/warning0. `browser/observations.json`과 capture hash 원장에 실제 화면 근거를 남겼다. 390/1024/1440 또는 모바일 실기기 QA로 확대하지 않는다.

관련 회귀 **33/33**, 실제6개 GLB loader, typecheck, 전수 production motion schema/policy 및 production build/learner 배포물 audit가 통과했다. 기존 JS chunk 경고는 남는다(App6,430,954bytes, gzip682.96KB). 예산을 상향하거나 GPU/VRAM/전체 성능을 이번에 다시 측정했다고 쓰지 않았다. reduced-motion·공유 clock·취소는 동일 player 회귀 근거를 재사용했으며 OS 설정을 바꾼 실기기 검증은 아니다.

## 보존과 남은 범위

542/563/12, 근육429/447/232source concepts/462surfaces, HA130, 역사163(6/20/135/2), source-only, 공개권리held, humanReview=not_performed 및 canonical/whole-target extent 미승인을 유지했다. 원본/source-cache/OpenSim_Models/T13, 다른 task 상태와 원조사·worker WIP를 변경하지 않았다. 기존 공통 원장 행은 ID별로 동일하며 새 소유 행만 추가했다. 소유 변경만 선별한 로컬 커밋은 현재 workspace의 checkpoint다. 선행 U03-r5 및 validator WIP를 임의로 포함하지 않았으므로 HEAD만의 깨끗한 checkout이 선행 전체 산출물을 포함한다는 주장은 하지 않는다.

다른 대흉근·견갑대 작용, full physiological ROM/activation/force, 전체 target/group extent는 별도 콘텐츠 gap이다. 우선 범위 밖 턱/얼굴/호흡/E-index 수리는 deferred engineering backlog로 유지했으며 이번 단위의 gate로 재도입하지 않았다.

다음 수동 파일: `work/plans/t66-priority-atlas-2026-10-05/04-trunk.txt`. 이 단계만 실행했고 다음 파일/T85/push/배포는 시작하지 않았다.
