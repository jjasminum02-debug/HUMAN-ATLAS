# 현재 바로 실행할 MV2 프롬프트

현재 기준: [PROMPTS-IN-ORDER.md](PROMPTS-IN-ORDER.md) 1번. Q03 실패 원인을 반영한 동일 프롬프트다.

```text
HUMAN ATLAS에서 MV2 Q03만 구현·검증까지 마무리해라. 담당 Sol xhigh.
work/tasks/MV2.md, work/EXECUTION.json의 최신 MV2,
work/plans/mv2-at-integrated-2026-10-12/PROMPTS-IN-ORDER.md의 공통 계약과 1번,
최신 MV2 report 및 record가 가리키는 validation/repairQueue를 읽어라.
이 재개는 Q03 기존 WIP 인수와 필요한 기능 수정을 포함한다.
Q01 engineering·q01-learning-quality·Q02 완료를 보존하고 반복하지 마라.

확인된 원인부터 처리한다. Q03 옵션은 현재 posture_observation이므로
'근육 작용 찾기' 검색 0건은 clip 부재가 아니다.
실제 선택 경로는 source 선택 → 기능 → '자세에서 관찰하기' 펼치기
→ 정확한 동작 선택 → '움직임으로 이해하기'다.
현재 고정 대상은 다음 3개다. 최신 등록과 hash도 대조해라.
- 왼쪽 source ZA-c7010a9-b20b574e456449c5d571c7a1,
  motion-option-298: 팔꿈치 굽힘, group21, elbow-flexion-left-source-frame-r4.
- 같은 왼쪽 source, motion-option-297: 어깨 앞쪽 굽힘,
  group23, shoulder-flexion-left-source-frame-r4.
- 오른쪽 source ZA-c7010a9-a0c2ea00609e874a7faa926d,
  motion-option-299: 어깨 앞쪽 굽힘, group24, shoulder-flexion-right-source-frame-r4.
같은 source의 서로 다른 clip을 하나로 세지 마라.

먼저 기존 경로로 재생해라. 실제 연결/lazy load/선택/재생 결함이 재현되면
관련 공통 코드와 회귀 검사를 수정하여 이번 범위에서 해결해라.
검색 0건이나 disabled 버튼만 기록하고 끝내지 마라.
기존 경로가 정상이라면 UI를 새로 만들지 마라.
근육 작용으로 제공할 항목은 기존 action 근거·부착/phase·실제 변형을 대조해
필요한 해당 항목만 보완한다. 단순 learningIntent 변경은 수축 구현이 아니다.

현재 checkout의 살아 있는 서버와 asset 응답을 확인한 뒤,
도구가 허용하는 독립 브라우저 탭과 실제 버튼으로 세 clip을 재생해라.
사용자 Chrome 포커스/오래된 AX 번호에 의존하지 마라.
1배속 전체 주기 및 필요한 느린 관찰, 준비·중간·최대·작용·복귀를 보고
이두근의 부착·윤곽·주변 구조와 좌우를 실제 화면으로 확인해라.
공통 중단/재시작/선택·레이어·원본 복원/경혈 재진입은 공유 경로 기준 한 번 묶어 검사한다.
기하 결함이 확인되면 source/frame/pivot/weights/보간/접촉 중 원인을 좁혀
기존 offline authoring·source-bound replacement·공통 예산 계약으로 최소 수리하고 재검증해라.
정상이라면 기존 GLB를 보존하고 관찰 근거로 Q03을 닫아라.
수축 기능과 자세 관찰 범위는 보고서에서 정확히 구분한다.

중단돼도 같은 범위의 체크포인트부터 이어가라. 같은 자료를 처음부터 재조사하지 마라.
Q03의 3개 판정과 변경 영향 검증을 마친 뒤 보고서/evidence/EXECUTION의 MV2,
sync 및 --check와 소유 변경의 로컬 커밋까지 마무리해라.
UI·카메라 개편, Q04/Q05·AT 자동 실행, push·배포는 하지 마라.
전체 MV2의 partial과 이번 Q03 통과 여부를 구분해 보고하고 멈춰라.
```
