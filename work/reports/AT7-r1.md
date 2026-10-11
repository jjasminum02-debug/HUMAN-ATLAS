# AT7 — 국소 구조 문맥 관찰·공통 따라보기·표시 제어

2026-10-12 · 담당 Sol High · **acceptancePassed=true**. AT7만 수행했다. 시작 HEAD는 `bd7dc579f5e8ca69b30a78fdc7b2c04921f2c7ce`, 시작 index는 비어 있었고 기존 WIP는 5,966개(추적 파일 45개, 미추적 5,921개)였다. 최신 AT6 acceptance.passed=true, 실제 교육용 위치 22개와 learner 원본 SHA를 확인해 실행 조건을 충족했다. 과거 AT6의 위치 0개 기록은 최신 결과로 승격하거나 재사용하지 않았다.

## 결과와 소유 범위

기존 AcupunctureOverlay/AcupointReview/PointTour/CameraSessions와 한 AnatomySceneRoot, renderer, camera를 재사용했다. `ObservationContext`가 점과 주변 구조의 실제 국소 bounds, source 주소·SHA, 양측, AT6 anchor binding을 제공한다. 가슴·위팔·팔꿈치·아래팔·손목·무지구·엄지 끝의 22개 문맥에는 원본 삼각형으로 재현되는 86개 국소 구조 부분과 기존 손톱 probe 2개가 있다. 긴 노뼈·위팔근육 전체 bounds를 focus에 사용하지 않는다. 새 해부 mesh, 인체 복사본, renderer, 카메라 서비스는 만들지 않았다.

카드·검색·실제 점 클릭·따라보기·최초 진입이 같은 선택/관찰 함수로 연결된다. 충분한 국소 구도는 그대로 두고 부족하면 실제 가시 영역에 맞춰 target/distance/orientation을 이동한다. DOM에서 카드와 하단 조작부의 교차 영역을 읽으며 CSS가 이미 확보한 공간을 두 번 제외하지 않는다. 기존 화면 맞춤/선택 맞춤 버튼의 위치·모양은 유지하고 현재 관찰 소유자가 있을 때만 같은 fit 함수를 호출한다.

14경맥/361개 코드·이름의 지연 로딩 catalog와 공통 검색·좌우·전체점·점/경로 표시 제어를 연결했다. **실제 표시 가능한 좌표는 AT6의 LU 양측 22개뿐**이다. 전체점에서는 그 22개를 임의 생략하지 않으며 나머지 648개 위치는 준비 중이다. 다른 경맥은 카드와 이름만 제공하고 위치·기준 구조 입력이 없으면 점이나 임의 구조 관찰을 생성하지 않는다. 정중 경맥의 카드 side는 midline이다. 영역은 입력이 없어 비활성으로 남겼다. 새로운 technical fixture를 learner로 내보내지 않았다.

공통 tour의 order/section 입력을 일반화했고 LU 고정 카메라 거리를 제거했다. 선택된 점만 상세 label을 표시한다. 검증된 B/F-cun carrier 구간만 LineSegments로 표시하며 끊어진 carrier 사이에 경로를 만들지 않는다. 이 선은 전통적 전체 유주·분지·내행 자료가 아니다.

CameraSessions에는 기존 원래 복귀값을 전환 중 재진입에도 보존하는 최소 수정을 했다. 이전 요청의 뒤늦은 dispose가 새 같은-owner 세션을 취소하지 않도록 등록된 fit callback 소유권을 검사한다. 복귀 애니메이션 중 닫기, reduced motion 닫기, foreign motion 소유권도 처리한다. pointer/touch 접촉·드래그·휠·키 입력은 tour와 자동 복귀를 중단한다. 정지 frame/pose/hash 검사와 motion guard는 유지했다.

## 실제 검증

| 계약 | 검사와 근거 | 판정 |
|---|---|---|
| G1 | 기존 오른쪽 넙다리곧은근 선택·URL·레이어를 유지한 진입, 최초 LU1도 국소 문맥. 단일 scene/camera | pass |
| G2 | LU1/LU5/LU9/LU11 양측 × 390/1024/1440, 최종 PNG/DOM 24개. 모두 점·국소 bounds가 실제 가시 영역 안, label 1개, 이름/side 일치 | pass |
| G3 | 실제 LU1–11 자동 진행 후 복귀. 드래그·휠·방향키에서 paused/autoReturn=false. 수동 후 닫아도 늦은 복귀 없음 | pass |
| G4 | LI/LU/CV 전환, 빠른 좌우/점 선택, OFF/ON, 실제 다른 경맥에서 태연 검색, 복귀 중 닫기/재진입 | pass |
| G5 | 390px 펼침/접힘과 선택 card, 점과 주변 구조 가림 없음. 마지막 터치 목표 최소 44×44px | pass |
| G6 | reduced motion에서 cameraTransition=false, Enter로 닫기, 기존 근육 클릭이 실제 source 선택으로 연결, layer-off 강제 복구 없음 | pass |

최종 24개 화면의 문맥 점유율은 **58.46–62.00%**다. 전신 유지나 점 하나의 극단적 확대가 아니다. 실제 화면에서 LU1은 빗장뼈/어깨와 가슴근육, LU5는 팔꿈치와 위팔·아래팔 힘줄 구간, LU9는 손목·손바닥 근육과 손 뼈, LU11은 엄지 끝과 손가락 뼈의 주변 문맥을 확인했다. bounds 포함/레이어 visible과 모든 깊은 구조의 표면 노출은 다른 판정이다. 원래 근육에 가려진 깊은 뼈를 강제로 노출하지 않았고, LU11의 probe를 원래 피부/손톱 mesh로 표시하지 않았다.

실제 점 클릭은 왼쪽 LU9를 선택했고 URL을 경혈 source ID로 바꾸지 않았다. 점 밖의 위팔근육 클릭은 기존 `ZA-c7010a9-b79c7d0ed5f3e42439fa6d34` 해부 선택으로 연결되어 overlay가 종료되었다. 마지막에는 원래 오른쪽 넙다리곧은근 URL과 layer 상태를 복원했고 viewport override를 해제했다.

tour 복귀의 최대 camera 오차는 부동소수점 연산 수준인 1.11e-16m이다. 빠른 재진입·복귀 중 닫기의 원래 camera/target 오차는 0이다. 수동 조작 후에는 해당 구도를 유지한다. 닫은 후 camera owner=null, registeredUpdates=0, label/overlay 제거, geometry buffers가 native 기준 6,947,334 bytes로 돌아왔다. 최종 console warn/error 0개다. 더 짧은 390×844 화면에서도 양측 LU9/LU11 4개 추가 구도가 가시 영역 안이며 점유율 약 60%임을 확인했다. 물리 터치 기기는 사용하지 않았으며 pointer/touch 접촉의 즉시 중단 경로는 자동 검사로 검증했다.

관련 검사 **64/64 pass**, TypeScript 검사 pass, package build **13/13 단계 pass**. `validate-evidence.py`는 원본 캐시의 86개 삼각형 집합·국소 bounds와 22개 AT6 anchor binding을 다시 읽어 재현했고 실제 화면/복귀/자원 판정을 검사했다. 개발 중 r1–r4 화면과 실패한 test harness/Node strip-types 로그는 보존했으며 최종 판정은 `context-final-*`, `responsive-cases-final.json`, `tests-final-r2.log`, `build-final-r2.json`이다. HMR로 재생성된 개발 scene UUID를 같은 세션으로 합산하지 않는다. 최종 24개 화면은 하나의 root `c347a8f6-920c-4006-9d0c-0ffd87b0579d`를 공유한다.

## 비용과 위치·권한의 한계

| 항목 | 오른쪽 11점 | 양측 22점 |
|---|---:|---:|
| encoded 입력 bytes (carrier/learner/context/catalog 포함) | 465,585 | 631,821 |
| geometry buffer bytes (숨긴 carrier 포함, 공유 geometry 중복 제외) | 180,796 | 353,464 |
| 할당 mesh triangles (숨긴 carrier 포함) | 10,194 | 20,252 |
| route buffer bytes | 6,288 | 12,720 |
| carrier OFF 최대 draw calls | 13 | 24 |
| DEV carrier ON 최대 draw calls | 20 | 38 |
| textures | 0 | 0 |

새 context metadata는 139,176 bytes, catalog는 18,587 bytes이며 context용 인체 geometry는 0개다. native 렌더 기준은 492,972 triangles, queue encoded bytes 17,437,548이다. 추가 carrier까지 기존 overview 20MiB / geometry 96MiB / triangles 1,000,000 / chunk 8MiB 한도 안이다. 예산 파일은 변경하지 않았다. buffer bytes는 GPU에 전달하는 배열 용량이며 드라이버 VRAM 실측값이 아니다. 마지막 native render CPU P50 1ms / P95 3.2ms는 기존 진단의 관측값이며 전체 장치 성능 보증이 아니다.

AT6 위치 22개는 **교육용 개략 22 / 정밀 피부 위치 0**이며 이 task가 위치를 새 승인하거나 바꾸지 않았다. AI provenance 22개·교수 검토 0개·공개 재배포 held를 유지한다. 피부 스캔, 정밀 취혈, 임상 사용을 주장하지 않는다. 구조 문맥의 source-derived bounds와 AI가 선택한 국소 crop 창/카메라 방향을 구분한다. nearest/raycast는 가림/정합 도구로만 사용하고 혈위 의미 근거로 사용하지 않았다. 교과서 설명은 준비 중이다.

## 보존·기록·다음 작업

추적 WIP 45개, 원본 source GLB 23개, 선행 education carrier 85개의 해시가 동일하다. AT6 learner SHA는 `cac0de7048c443b36cfcfcb0c07443add241f1ab43bf5ac77badefeebd6bceee`, 규칙 입력 SHA는 `4b672b8cca8aecd7962a26233c8da71052f53b46b7bad65411a81e3f279909a4` 그대로다. 원본/OpenSim_Models/T13 drafts/기존 사용자 WIP·역사 evidence를 편집하거나 삭제하지 않았다. 소유 경계는 시작 baseline와 ownership-r1.json에 기록했다. WholeBodyViewer 변경은 기존 fit 버튼 handler 2개에 한정된다.

최신 EXECUTION을 다시 읽어 AT7 record와 feature plan nextUnit만 갱신한다. sync_execution.py 및 --check 결과와 semantic scope 검사, 선별 staging 목록은 evidence에 남긴다. 로컬 commit의 최종 hash·포함/제외·잔여 변경은 작업 완료 답변 및 로컬 Git 기록으로 확인한다. 기존 WIP는 staging에서 제외한다.

**AT7 remaining unit은 없다.** 미확보 다른 혈의 648개 위치, 361개 개념의 정밀 위치, 영역 mask, 교과서·교수 검토는 각 후속 배정/권한의 입력이며 AT7 위치 완료 수로 세지 않는다. 최신 order에서 AT7 다음은 AT20이고 AT20 선행은 AT1/AT4 complete이다. [다음 AT20 프롬프트](../evidence/AT7/run-r1/next-prompt-AT20.txt)를 남겼으며 실행·위임하지 않았다. push·배포·진단·치료·침 시뮬레이션도 하지 않았다.
