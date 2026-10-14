# 피부 완성 실행 계획 — 2026-10-15

**다음은 V1 피부 외관 시제품. F1·F2 재실행 금지.** 현재 부모 AT10은 partial이며, 이 계획은 합격을 부여하지 않는다. 현재 실행 상태는 EXECUTION.featureWorkUnits.AT10.completionExecution에 기록한다. 기존 F/R/C 중 남은 6묶음에 외관 V1/V2 두 묶음을 추가한 **8개 잔여 산출물**이다. 새 AT 번호를 발급하지 않는다. 실패 시 자동으로 새 번호를 늘리거나 다음 작업을 실행하지 않는다.

## Sol 대화와 실제 기준선

`침구 SOL`의 최신 F1/F2 대화·보고서·manifest를 직접 대조했다. 시작 HEAD 5e6c93c294b2e7bf3ee09216a6f8cf2c4987d10f.

- 045227c: Luna F1 조사 partial; cage 표본 검사만으로 피부 연결 실패. 과거 기록이다.
- 9452b0a: Sol이 실제 종아리 경계/발등 축/옆 발가락 loop 오대응을 교정하고 source-bound flow+공통 접촉 보정을 재사용. 오른발 f1c7 국소 valid native0/self0, 최소 표본간격1.003mm. branch cage 자체 구현을 목표에서 제외했다.
- 5e6c93c: Sol F2 왼발 f2c3 국소 valid native0/self0, 최소 표본간격1.012mm; 오른발/양손 보존. 해당 보고서는 static educational contour만 통과했다고 명시한다. 사용자 요구의 최종 피부 재질 품질 통과가 아니다.
- 입력 `atlas-data/anatomy/skin/at10-f2-left-foot-r1/manifest-f2c3.json`, GLB SHA `07ab569e3a3a3453ed825e9bc583869394e5e94babdee7edec6b6c437836586f`; F1 SHA `fd119f927a59e86e66f1fd145b4848e00aa0904a0969ac9d944aafb62fda0bcb`.
- 전체834 raw 교차1712/self1063 및 유효참조983면은 다른 부위 미완이다. 정상/예외/미완의 scope가 다르므로 local pass와 모순되지 않는다. registeredSkin=null, wholeSkin false 유지.
- 피부는 26756 triangles/626576bytes, UV 있음, texture0. runtime이 원본 material을 단색0xc9a080 roughness .94로 교체한다. 양발 실제 앱 캡처에 faceted silhouette와 단색 재질이 남는다. 따라서 재질·노멀·실루엣을 독립 품질 목표로 추가한다.

실제 근거: work/reports/AT10-skin-fit-f1-2026-10-14-r2.md, work/reports/AT10-skin-fit-f2-2026-10-14-r1.md 및 각 evidence/summary/scoped-checks/manifest/screens. 이전 partial 진단을 현재 성공보다 우선하지 않는다. 이 계획 작성은 자체 3D 검사의 재실행이 아니다.

## 실행 순서

| 순서 | 단위 / 담당 | 끝났을 때 실제로 남는 것 |
|---|---|---|
| 1 | [V1 피부 외관 시제품](01-V1-SKIN-APPEARANCE.txt) / Sol xhigh | 발·손에서 질감 개선을 눈으로 확인하는 실제 앱과 재사용 material package |
| 2 | [F3 머리·귀·목 정합](02-F3-HEAD-EAR-NECK.txt) / Sol xhigh | 누적 피부의 머리·귀·목 국소 정합 |
| 3 | [F4 몸통·겨드랑·샅·잔여 연결부](03-F4-BODY-SEAMS.txt) / Sol xhigh | 몸통·팔·넙다리·겨드랑·샅 및 잔여 경계 정합 |
| 4 | [V2 최종 피부 외관 보정](04-V2-FINAL-SKIN-LOOK.txt) / Sol xhigh | 실루엣·피부결·손발톱·UV seam까지 보정한 최종 외관 |
| 5 | [F5-F6 전신 형상·외관 동결](05-F5-F6-FREEZE.txt) / Sol xhigh | geometry+material+지표+재현이 동결된 전신 입력 |
| 6 | [R1 재질 포함 공유 로딩·비용](06-R1-DELIVERY.txt) / Sol xhigh | 최종 피부·texture가 예산 내 로딩/공유/해제되는 공통 경로 |
| 7 | [R2 피부 버튼·108점 접촉·실앱](07-R2-CONTACT-APP.txt) / Sol xhigh | 실앱 피부 버튼·108점 접촉·레이어 회귀 통과 |
| 8 | [C1 기존124점 연결·AT10 마감](08-C1-CLOSE-AT10.txt) / Luna Max | 124개 입력의 실제 연결 및 AT10 최종 판정 |

기본 직렬이다. V1이 실제 geometry 미완 때문에 차단되면 잘못된 선행 조건이다. V1 재질의 외부 자료 등 실제 결함이 있어도 F3/F4 입력과 독립이면 그 geometry 작업은 진행하고 V2에서 재질을 마감한다. 최종 등록을 위해서는 모든 필수 결과가 필요하다. 일반적인 실패를 숨기거나 pass로 바꾸지 않는다.

## 이번에 바꾸는 기준

- geometryPassed / appearancePassed / runtimePassed / locationValidated를 분리한다. F1/F2는 재질 통과로 승격하지 않으며 재질 불만 때문에 성공 geometry를 폐기하지도 않는다.
- 대표 화면의 조기 시제품을 먼저 본다. 무채색 비교와 최종재질 비교를 같은 시점·배율로 수행한다. 피부색 차이·손발톱 식별·약한 미세 피부결과 자연스러운 윤곽이 목표다. 거친 모공/얼룩/강한 광택은 기본값이 아니다.
- V1 기본 geometry 보존, V2 필요한 국소 silhouette 보정 허용. topology 변경은 필요 근거·원본 계보·비용·점 주소 mapping을 남기고 영향 범위 검증한다. 질감만 바꿔 좌표계/경혈 주소를 흔들지 않는다.
- 현재 UV에 맞는 MakeHuman core 피부 자산을 우선 활용한다. 자산 자체의 권리/UV 검증과 실제 적용이 필요하다. core assets CC0 안내는 사용자 제공 third-party texture까지 일괄 승인하지 않는다.
- 기본 PBR 색/normal/roughness로 먼저 품질을 얻는다. real-time SSS/전신 고해상도 geometry 확대는 입증된 필요와 성능 측정 후에만 검토한다.
- V1 재질 preview는 개발 경로이며 accepted 피부가 없어도 실행할 수 있다. 기존 hash/frame/rights 검사 자체를 제거하지 않는다. R1이 제품 delivery 예산과 최종 공유 경로를 마감한다.
- 개발용 실패 JSON·원본·작업 로그는 runtime 의존성에서 분리한다. 이미 있는 원본/실패 evidence는 삭제하지 않되 후속 Git에는 재현 recipe·핵심 검사·대표 화면과 선택 자산 위주로 선별한다.

## 더 이상 같은 이유로 멈추지 않도록

COMMON.md의 의존성·재개 규칙을 따른다. 과거 실패 기록을 current blocker로 재사용하지 않는다. 부모 partial/선택적 교수검토/public held와 실제 기술 실패를 구분한다. 변경 없는 전체 입력 재조사 대신 실패 주소에 대한 원인 교정과 영향 검사를 한다. 새로운 알고리즘명 달성이 목표가 아니다. 실제 실패 없이 preflight 보고만 남기지 않는다. 필요한 권한/자료가 진짜 없으면 정직하게 해당 범위를 분리한다. 실제 미해결을 무조건 통과시키거나 실패가 절대 없다고 약속하지 않는다.

## AT10 이후

기존 work/plans/acupoint-surface-posture-2026-10-13/PROMPTS-IN-ORDER.md의 AT11 이후 대상 범위는 유지한다.

1. AT11–19: 나머지 정지 경혈 위치·경로. Luna Max, 공통 pipeline 결함만 Sol. 각 혈별 runtime 코드 복제 없이 데이터 묶음으로 구현한다. 완료 때 14경맥361개 개념/현재 계획670 instances의 표시·미해결을 분리해 대조한다.
2. AT23–27: 경맥 영역/경근 설명/학교 자료 반영. 데이터·검증 Luna, 공통 surface/mask 렌더러 문제가 있으면 해당 구현만 Sol. 신경 감각 영역과 전통 경맥 영역을 혼동하지 않는다.
3. AT30: 특수 취혈자세 전수조사·분류(Luna). 이미 추출한 자세 후보 재사용.
4. AT31: 필요한 공통 자세 rig/변형/점 추적 구현(Sol). 자세별 shader/renderer를 복제하지 않는다.
5. AT28/29: 최종 회귀·비용/범위 감사(Luna, 결함 수정 Sol). 사용자 전체 UI 개편은 별도 요청으로 남긴다.

해당 단계의 실제 남은 작업을 완료하면서 진행한다. 이 파일의 순서가 자동 실행 권한이나 전신/361혈 완료 주장은 아니다.

## 문서 사용법

지금은 01-V1만 실행한다. 각 단계 뒤 최신 completionExecution.nextPrompt를 사용한다. historical r2/evidence handoff는 보존하지만 현재 실행의 우선순위는 이 r3 계획이다. 모든 실행은 소유 변경만 로컬 commit 후 멈춘다. 보고서와 사용자 시각적 피드백을 다음 단계에 반영한다.

참고: https://static.makehumancommunity.org/mpfb/docs/characters/skin.html (피부 자산/웹 export 방향), https://threejs.org/docs/pages/MeshStandardMaterial.html (PBR 맵), https://threejs.org/docs/pages/MeshPhysicalMaterial.html (기능별 성능 비용). 이번 계획은 해당 자산의 실제 시각 품질을 미리 승인하지 않는다.

역사 NEXT 복사본의 상대 링크 기준 디렉터리는 원래 `work/plans/acupoint-surface-posture-2026-10-13/`이다. 현재 실행 링크로 사용하지 않는다.
