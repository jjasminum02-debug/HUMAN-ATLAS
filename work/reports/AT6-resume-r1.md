# AT6 재개 결과 — Sol High, 2026-10-12

AT6 필수 인수는 **통과**다. LU1–11 양측 **22개 교육용 모형 위치**를 기존 learner 카드/overlay에서 실제 선택·표시했다. 정밀 피부 취혈 위치는 **0개**, 그 정밀도 미확정은 **22개**다. 이 결과는 교수 검토나 공개 재배포 승인이 아니다. 역사 AT6의 `acceptancePassed=false`, 실제 위치 0/22와 이전 원문/evidence는 덮지 않았다.

최종 입력은 `work/evidence/AT6/resume-r1/bilateral-rules-r9.json`, compiler는 `explicit-landmarks-2.2` 및 `bilateral-compiler-r8/`, 실제 learner는 `atlas-data/acupoints/learner/lung-r7.json`, 등록 표면은 `carrier/lung-AT6-r2/`다. 22개 AC2 proposal 좌표를 가져오지 않았다. AC2의 기존 코드·이름·기본 설명만 보존하고 native source triangle/barycentric와 문헌 관계를 AI가 작성했다.

## 기준선과 소유

- 시작 HEAD: `87678fd7d2874d30cbb068317ecfa38e07cbecfd`. 시작 WIP status 5,966 entries, tracked WIP 45개 hash, index empty. `baseline.json`, NUL `baseline-status.bin`, `execution-before.json`에 기록했다.
- 소유: 공통 compiler의 명시적 교육 지표/참조 carrier/비례 측정 최소 확장, 국소 carrier 출력 옵션, 공통 loader의 추가 registry, 실제 learner import, 관련 검사, 새 `resume-r1/` evidence, 이 versioned report, EXECUTION의 AT6 record와 feature nextUnit.
- 제외: 원본/source cache/OpenSim_Models/T13 drafts, 역사 AC1/AC2/AT1–5/AT6, 근육 움직임·UI WIP, 디자인/기존 task 문서, 기존 보기옵션/홈/로딩, AT7 구현. 기존 source loader/renderer/CameraSessions/카드/overlay/tour는 복제하지 않았다.
- `preservation-r1.json`: 실제 읽은 native 파일 521개 hash와 baseline tracked WIP 45개가 동일하다. 동결 235개 중 233개 동일. 실행 중 다른 작성자가 31 설계와 AT6 task 문서를 바꿨다. 두 파일을 다시 읽었고 변경은 소유하지 않으며 커밋에서 제외한다. 최신 EXECUTION도 다시 읽고 다른 record를 보존한다.

## 위치 작성과 표면

프레임은 `HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR`, m, native dataset pose `ZA-9f08a17ea0115fed-frame0-autoexec-off`다. runtime의 `za-c7010a9-9f08a17ea011-frame0-static`와 문자열을 혼용하지 않는다. native ZA revision `c7010a903b75a2fd24a13b1c2c4c3546a9223780`, 원본 blend SHA `9f08a17ea0115fed80b2a73ecdf0a1bc2ab2f6956f37c593ce23d513ea35afcd`를 유지했다. 각 side의 실제 source 주소/transform/hash/topology를 독립적으로 읽었으며 left를 right mirror로 승인하지 않았다.

기존 AC1/AC2의 손톱 probe와 AT2 제작 경로, AT3/4 공통 carrier를 재사용했다. 먼저 오른쪽 **LU9**의 native styloid/scaphoid/APL 관계에서 compiler→learner 점까지 완성하고 `first-learner-LU9.png`에 남겼다. 이후 같은 공통 경로로 22개를 처리했다. 최종 46개 native landmark annotation과 42개 고유 native 주소는 원본에서 관찰한 구조, AI가 만든 모형 지표, 표면 정합을 분리한다. 모두 AI 출처를 유지한다.

일차 위치 기준은 기존에 조사한 [WHO Standard Acupuncture Point Locations (AC2에서 확보한 원문)](https://www.medbox.org/index.php/dl/627a4de115110145a1723f64)이다. p12–13 측정 원칙과 p26–31 폐경 위치를 원문 페이지로 대조했고 다시 다운로드하지 않았다. 고정 mm나 전신 bounds 비율을 비례촌으로 승인하지 않았다.

| 개념·양측 | 실제 native 주소의 주요 근거 | 교육 모형 작성·한계 |
|---|---|---|
| LU1 중부 | 쇄골616, 제1늑골960/제2늑골1072, 상부 대흉근330 | LU2 아래 1 model B-cun, 첫 늑간 높이의 외측 모형 전이. 실제 외측 늑간/피부가 있다는 주장은 아님 |
| LU2 운문 | 상부 대흉근375/388, 삼각근1897/2462/2294, 오훼돌기12916 | 실제 deltopectoral 경계의 작은 fossa membrane. 쇄골 아래·오훼돌기 안쪽 관계 검사 |
| LU3 천부·LU4 협백 | 대흉근 상완 삽입45, 표층 삼각근199, 이두근 원위건351 | native 삽입면에 대응하는 axillary 모형 지표→cubital 지표의 9 B-cun, 3/9·4/9. 피부 주름 관찰 아님 |
| LU5 척택 | 이두근 원위건351 | 현재 extended pose의 건 가쪽 cubital 지표. 굴곡 주름을 관찰했다는 주장 아님 |
| LU6 공최·LU8 경거 | 위의 cubital 지표와 검증한 wrist 기준점 | native endpoint 축의 12 B-cun에서 7/12·1/12. 연결된 표면 path는 정합 도구만 사용 |
| LU7 열결 | APL397·EPB487의 native groove | 독립 tendon 높이와 wrist–cubital 1.5/12 수준 차 약 0.067mm. 고정 pose 구조 대응이며 피부/촉지 정밀도 아님 |
| LU9 태연 | 노뼈 styloid93, 주상골120, APL260, APB488 표층 대응 | native interval의 palmar/radial 표면 대응. 원본에 radial artery/손목 피부 주름이 있다고 주장하지 않음 |
| LU10 어제 | 제1중수골407, base518/head185 및 thenar 근육 | native midshaft·radial contour에 만든 모형 red-white 전환 지표. 피부 색 경계 관찰 아님 |
| LU11 소상 | thumb nail-fold151, distal phalanx49/92, proximal phalanx10/140 | 원본 조갑 요측 근위 모서리 + native IP 폭 F-cun + 요측/근위 축. 작은 지표 막에서 0.1 F-cun; 실제 피부/환자 정확도 아님 |

기준 구조를 직접 대조하기 쉬운 LU7/9/10/11도 실제 피부 위치로 승격하지 않았다. LU1–6/8은 주름·흉부 측정면 등을 AI 교육 지표로 작성했다. 원래 손목 seam·흉부 fossa·얇은 조갑 모서리의 지지 표면은 부족했지만 필요한 국소 부분을 보완해 현재 교육용 표시의 실제 무지원 unit은 0개다. 원본에 없는 주름·혈관·피부색·조갑 스캔은 미지원 그대로다.

흉부 6촌선은 WHO의 흉부 측정/중쇄골선 참고를 native 쇄골616에 적용한 **AI 4촌 teaching template**다. 관찰한 유두 좌표나 개체의 피부 측정이 아니다. 제1/2늑골 수준도 외측 모형 전이이며 literal rib surface가 해당 점에 있다고 주장하지 않는다. `chest-morphology-audit-r3.json`에서 쇄골 아래·오훼돌기 안쪽·fossa triangle 내부·전이 rib plane·LU1–LU2 관계를 따로 확인했다. 개별 신체 및 정밀 취혈은 미확정이다.

원본 education-r1 83 chunks /813,096 bytes /40,520 triangles는 변경하지 않았다. 새 registry는 손목 연결·thenar·상흉부·fossa·조갑의 10개 국소 chunks만 등록한다. 최종 조갑 지표는 양측 합 216 bytes/4 triangles다. coarse thumb 후보는 compiler의 IP 폭 calibration에만 사용하며 제품 target/bundle에 넣지 않는다. 새 전신 mesh·인체 복사본·renderer는 없다. 새 면은 모두 authored teaching geometry이고 skin scan이 아니다.

## 실제 실패와 교정

근육·힘줄 경계를 원본 피부로 바꾸지 않았다. FCR/PL/ED 구조를 대조해 palmar가 +Z임을 확인했고 이전 음의 Z 조사 후보는 폐기했다. 깊은 axillary insertion을 표면 점처럼 직접 투사했을 때 gap/path가 실패해, 원본 insertion 면과 별개의 표층 지표를 작성하고 source context를 compiler에 결합했다. LU2의 처음 +Z ray가 posterior 면을 선택한 경우도 승인하지 않았다. source-addressed fossa membrane으로 실제 anterior support를 만들었다.

소상은 facet50의 surface detour가 원위로 진행한 오류, facet151을 coarse envelope로 매핑하면 native 모서리보다 안쪽으로 옮겨지는 오류를 실제로 찾았다. annotation 방향과 **native** 요측·근위 방향 검사에서 두 실패를 보존했다. native 축으로 작은 조갑 지표를 작성해 실패한 둘만 교정하고 성공 20개는 byte-identical로 재사용했다. 교수 승인이나 fixture enum 변경으로 pass하지 않았다.

비례촌도 추가로 대조했다. 표면의 circumferential detour를 1 B-cun으로 계산한 기존 경거는 너무 손목 쪽이었다. native 측정축과 정합 path를 분리하고 anatomical plane의 유일한 연결 표면 교차를 계산했다. 1/12 plane은 기존 AT3 arm chunk에 있어 old wrist target 두 개를 compiler가 실패시켰다. 실제 target/hash/evidence를 그 chunk에 결합해 두 항목만 재개했다. `native-proportion-validation-r1.json`의 8개 값과 양측 LU9 < LU8 < LU7 높이 순서를 확인했다. nearest/raycast나 bounds는 혈위 의미 근거로 사용하지 않았다.

## 인수 검사와 비용

`validation-r1.json`은 actual renderedFrames 증가를 기다린 **최종** 22개 PNG/DOM 증거를 검사한다. 초기에 repaint 이전/전환 중 캡처한 조사 화면은 인수 자료로 사용하지 않는다. 최종 root는 `8e55008c-4142-4ed5-b514-23f356feb7fe`, canvas/renderer 각 1개이며 점의 parent는 같은 AnatomySceneRoot다. 각 code·side·이름·기본 위치 카드·선택 label 1개가 일치한다. LU9=태연, LU11=소상이다.

390×844, 1024×1000, 1440×1000에서 LU1/LU5/LU9/LU11 양측을 실제 확인했다. 모바일 상세는 아래 패널의 스크롤 문맥이다. 점/라벨은 가시 canvas에 있으며 기존 패널/보기옵션을 재설계하지 않았다. **AT7의 주변 구조 bounds/가림/터치 목표/자연스러운 문맥 framing 전체 인수는 이번 합격에 포함하지 않는다.** 모델에 없는 조갑/피부를 화면에 새로 스캔처럼 제시하지 않았다. 카드의 교과서 설명은 여전히 준비 중이다.

- 관련 검사 **48/48** 통과: 원본/AI/model indicator 구분, 실제 22개 replay, side/frame/pose/hash/rights 변조 실패, 다중 carrier seam, native direction, B-cun 측정축과 wrong target, failed-only resume·성공 20개 보존, motion active 차단, foreign camera owner의 late dispose, 기존 tour 등. 2.2 version에서 최종 fresh replay가 동일 runtime projection을 산출했다. fixture export 0.
- package build의 기존 **13단계** 통과(타입·Vite·data checks·배포 카드/lazy feature 검사 포함). 버전 상수 확정 후 타입 검사 및 최종 48개를 다시 확인했다. compiler/native evidence/private 교재/개발 proposal은 learner import에 없다.
- 최종 추가 active carrier: **153,534 encoded binary bytes /6,989 triangles**. 기존 carrier를 포함한 registry 합은 966,630 bytes /47,509 triangles다. 실제 요청은 선택 side의 필요한 chunk만 한다.
- 오른쪽 표시 package+manifest+requested bytes **307,822**; overlay geometry buffer capacity **172,620 bytes**, 10,146 triangles, geometry 8, carrier OFF 11 draw calls /ON의 계산 비용 18, texture 0. 왼쪽 **306,190 /170,988 bytes**, 10,058 triangles. 숨긴 carrier도 capacity 계산에는 포함한다. 이는 geometry attribute/index capacity이며 driver VRAM 실측이라고 주장하지 않는다. carrier ON 계산값은 learner의 새 토글 구현/시각 승인을 의미하지 않는다.
- local chunks의 실제 native proper intersection **0**. 양측 wrist seam은 AT3와 byte-identical Float32 vertex 각 40개, virtual bridge 0. 원본/참조/topology hash·frame·unit·pose·side·clearance를 검사했다.
- 예산은 **20MiB overview /96MiB geometry /1M active triangles /8MiB chunk** 그대로다. 새 budgets 수정 없음. local IAB/macOS 조건에서 최종 선택 화면 render CPU p95의 최대 관측은 약 **1.60ms**다. FPS/GPU 실행시간 보장은 아니다.
- 닫기 후 geometry buffer는 **6,947,334 bytes→6,947,334 bytes**, 원래 camera/target exact return, native 오른쪽 넙다리곧은근 URL/선택/hidden/translucent/nerve/region/pose 보존, owner null, overlay/projection 제거. 수동 Arrow orbit은 tour paused/autoReturn false, native 노뼈·근육 선택 흐름과 빠른 열기/닫기 자원 정리도 확인했다. source ID로 경혈 선택을 위장하지 않았다.

## 범위 밖 상태와 다음

정밀 피부 위치 22개, 원본의 피부 주름/혈관/색 경계, 교수 검토, 공개 재배포는 승인하지 않는다. ZA CC BY-SA 4.0 및 BP3D source 권리 분리는 유지하며 localObservation만 근거 있는 현재 사용을 허용한다. AI provenance는 22개 모두 유지한다. 이 한계는 교육용 표시 22개 완료와 별개다.

다음은 최신 feature order의 **AT7**이며 자동 실행하지 않는다. 문맥 camera와 빠른 닫기→복귀 도중 재진입의 중간 camera snapshot 위험은 `next-prompt-AT7.txt`에 구체적으로 넘겼다. AT6 교육용 표시의 남은 unit은 0개다. 다음 UI/motion 작업이나 AT1–5 재실행은 하지 않았다.

로컬 커밋 포함 대상은 위 소유 파일과 versioned 증거/이 보고서/AT6 EXECUTION hunk다. 기존 WIP·externally edited record/디자인·원본·역사 기록은 제외한다. 최종 commit hash와 실제 잔여 status는 최종 응답에 보고하며 staged path 목록을 evidence에 남긴다. push·배포·위임·진단·치료·침 시뮬레이션 없음. 자동 승인 검토가 선택적인 브라우저 탭 고정을 거부해 고정은 생략했고, 화면 파일/임시 viewport 원복은 완료했다.

커밋 직전 재확인에서 다른 작업의 MV1 커밋 `84d6128`, `0477e59`가 시작 HEAD 이후 추가됐다. 이를 보존하여 AT6 커밋의 parent는 `0477e59dcce436eee914f2040653c52e2cf92f60`이다. 최신 HEAD 대비 EXECUTION의 변경은 AT6 record와 feature nextUnit 두 경로뿐이다. 시작 시 tracked WIP 45개 hash는 그대로다. `sync_execution.py`는 뷰 변경 0개, `--check` 일치로 완료됐다. 최종 22개 화면 contact sheet도 직접 확인해 `visual-inspection-accepted-r1.json`에 남겼다.
