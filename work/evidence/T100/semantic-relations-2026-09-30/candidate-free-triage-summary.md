# T100 후보 없음 target 표현·형상 분리 요약

이 표는 T96의 고정 542 target 중 현재 ZA overlay candidate count가 0인 163개만을 다룬다. T96 target ancestry와 이미 연결된 source rows를 추가로 대조했다. 계층 경로상의 표면은 target 자체 geometry로 승격하지 않았다.

| 분류 | 수 | 해석 |
|---|---:|---|
| 정확한 source label 관찰, identity crosswalk 필요 | 6 | 문자열은 exact하게 관찰됐지만 target relation은 검증되지 않음 |
| mapped descendant surface 있음 | 20 | 하위 구조 표면은 있으나 target 전체 surface인지 미확인 |
| mapped ancestor/group surface만 있음 | 135 | 부모/상위군 표면은 있으나 target-specific geometry/member가 아님 |
| exact/descendant/ancestor surface 근거 없음 | 2 | 현 frozen package 안에 target 계층 표면이 관찰되지 않음 |

6 + 20 + 135 + 2 = 163. 155개에는 다른 분류 수준의 계층 표면 표현이 있지만, 이를 동의어나 동일 geometry로 취급하지 않는다. 마지막 2개도 frozen package 기준 미관찰일 뿐 외부 source에 실제 형상이 없다는 증명은 아니다. 이번 근거로 확정한 실제 geometry 부재는 0개이며, 실제 geometry 부재 여부가 미확정인 target은 163개다.

## 계층 표면 근거가 없는 2개

- `TA2:356` — facial bones (head): T96 ancestry `TA2:353, TA2:352`에도 현재 mapped surface가 확인되지 않음. source 전체에서 실제 형상이 없다는 결론은 미확정.
- `TA2:1282` — bony pelvis (pelvis-perineum): T96 ancestry `TA2:352`에도 현재 mapped surface가 확인되지 않음. source 전체에서 실제 형상이 없다는 결론은 미확정.

세부 target·sourceKey·side·ancestry locator는 `target-gap-classification.json`에 있다. 같은 무결과 검색은 반복하지 않고 현재 freeze의 ID/ancestry/evidence만 사용했다.
