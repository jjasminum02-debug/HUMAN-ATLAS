# AT8 — 공통 package 연결과 대장경·삼초경 양측 교육용 위치

2026-10-13 · Sol xhigh · AT8만 수행. `acceptancePassed=true`.

LI1–20·TE1–23의 43개 개념, 양측 86개 위치를 공통 compiler와 기존 learner scene에서 연결했다. 86개 모두 실제 선택·이름·side·국소 구조·가림을 검사했다. **교육용 개략 위치 86 / 정밀 취혈 위치 0 / 미해결 제품 위치 0**이다. 사람 검토와 공개 재배포 승인은 부여하지 않았다. 다음 순서는 AT9이며 자동 실행하지 않았다.

## 기준선과 보존

- 시작 HEAD: `54d62b77d1181134735a2dfbedeb08dea17e9bd7`. 시작 index는 비어 있었다. 시작 status 5,975개 entry 및 사용자 tracked WIP 45개를 `start.json`, `start-status.z`에 보존했다.
- 최신 EXECUTION에서 AT5·AT6·AT7·AT22 및 MV2 완료 기준선을 확인했다. 옛 통합 계획의 partial snapshot으로 완료 작업을 재실행하지 않았다.
- `preservation-audit-r1.json`: WIP 45개 hash 변화 0, 보호 경로 3,814개 중 소유 코드 예외를 제외한 변화 0. 원본/OpenSim_Models/T13/기존 motion 자산·카메라 구현·LU 데이터·영역 revision을 보존했다.
- 단일 AnatomySceneRoot/renderer/camera, 기존 overlay·PointTour·CameraSessions·AT21 mask·AT22 편집 계약을 재사용했다. 보기옵션·홈·로딩·CSS·카메라 정책을 수정하지 않았다.

## 공통 구현

`learningRegistry.ts`는 catalog의 채널/code+side, 부분 package 합성, 충돌, 구간, 정중 singleton을 검증한다. 361 catalog를 유지한다. ST/BL/GB 부분 package 및 CV 정중 fixture는 자동 검사 전용이며 제품 위치로 등록하지 않았다. 실제 registry에는 LU·LI·TE만 등록했다.

공통 loader가 registry SHA와 actual file SHA, frame/unit/pose, carrier topology, projection binding, 실제 국소 bounds와 지원 경로의 triangle/barycentric를 검증한다. 필요한 carrier ID만 한 번 로딩한다. 경맥/side/전체점 전환은 기존 취소·해제 경로를 사용한다. 카드·검색·실제 marker 클릭은 같은 선택 함수에 연결한다. `sourceId`를 경혈 ID로 사용하지 않는다.

compiler `explicit-landmarks-2.5`는 기존 landmark/B-cun/F-cun을 유지하고, 실제 연결 곡선의 `surface_fraction`을 별도 규칙으로 추가했다. 이를 B-cun으로 바꾸어 부르지 않는다. 공유 정중 native 구조는 원래 side를 유지하고 해당 hemisphere의 주소를 검사한다. posterior surface 방향 검사도 추가했다. bounds 비율/nearest/unresolved/fixture는 자동 승인되지 않는다.

DEV의 `__acupointCarrierReview=1`만 기존 체표 면 토글을 사용할 수 있다. 기본 learner와 production에는 authoring/review/export 메타데이터 조작이 노출되지 않는다.

## 위치 근거와 실제 입력

외부 점 좌표를 복사하지 않았다. [WHO 위치 표준](https://medbox.org/index.php/dl/627a4de115110145a1723f64)의 LI·TE 관계와 현재 원본의 native triangle 주소를 연결했다. 한국어 이름과 기본 위치, 교재 설명 준비 상태를 분리했다. `basic-locations-r1.json`, 최종 `rules-r19.json`, `coverage-final-r19.json`에 모든 원문 관계·source locator·좌우·pose·hash·규칙·모형 지표·한계를 남겼다.

원본 `Startup.blend` SHA256은 `9f08a17ea0115fed80b2a73ecdf0a1bc2ab2f6956f37c593ce23d513ea35afcd`이다. frame0, autoexec OFF, 실제 object world matrix를 한 번 적용하고 `[X,Z,-Y]`로 프로젝트 frame에 정합했다. probe 전후 원본 hash가 일치한다. pose는 `ZA-9f08a17ea0115fed-frame0-autoexec-off`, 단위 m이다. 좌우 각각의 source object를 평가했으며 mirror를 검증으로 대체하지 않았다.

원본 T98 `allObjects`에는 runtime에서 빠진 Auricular region/Lobule/Apex/Tragus/Anterior notch/Helix/Philtrum/Nasolabial sulcus/Oral region/Temporal region 등 실제 geometry가 있었다. 초기 inventory lookup에서 잘못된 필드를 사용한 빈 결과는 원본 부재의 증거로 사용하지 않았다. `original-ear-inventory-check-r3.json`과 `evaluated-native-boundaries-r1/r2/r3.json`이 실제 근거다. 손톱은 기존 AT4 probe를 재사용했다.

- 손·팔: 실제 손톱/말절골/F-cun 지표, MC2·MC4/5·MCP, EPL/EPB, 노뼈/자뼈/팔꿈치머리, 위관절융기, 봉우리·큰결절·어깨뼈가시의 native 주소.
- 목·얼굴·귀: 후방 SCM·아래턱각, 반지/방패연골 높이, 원본 인중/콧방울/코입술고랑, 귓불·이첨·이주 패임·귓바퀴 뿌리와 temporal artery 관계.
- 피부 주름·피부색 경계·머리털 경계·열린 입/접힌 귀 자세가 관찰되지 않은 곳은 **AI 교육용 모형 지표**로 명시했다. 원본에서 관찰한 구조와 모형 지표를 섞지 않았다. 원본 regional surface와 bounded 국소 면은 피부 스캔이 아니다.

원본 oral region은 일부 vertex가 정중선을 넘으므로 ipsilateral original triangle subset과 원래 주소 map을 사용했다. world Float32 값은 바꾸지 않았다. 해부 관계를 유지한 정합과 source/native gap 20mm 제한을 지켰다.

## 후보 오류와 수정

후보를 최신이라는 이유로 통과시키지 않았다. r12의 왼쪽 TE7은 원래의 posterior 관계와 달리 palmar 면을 선택했다. 해당 실패 화면/input을 보존하고 원본 posterior fascia의 같은 해부 plane을 읽어 수정했다. 방향 검사에 기존 실패 입력을 넣으면 거부된다.

r18 실제 선택 화면에서 왼쪽 LI5–7 가림을 발견했다. 비스듬한 ray가 EPL/EPB 사이 목표를 지나 손목 안쪽 면을 선택한 원인이었다. 실제 EPL/EPB 및 radial styloid plane을 유지하고 바깥 radial 면에 정합한 LI5를 r19에 기록했다. 동일 endpoint를 사용하는 왼쪽 LI6–10만 재계산했다. 카메라 변경/전체 mesh scale/다른 부위 이동으로 해결하지 않았다. 실제 재검사 6/6 모두 가림 없음. 나머지 80개 위치는 유지했다.

최종 compiler receipt: 86 eligible, 실패 0, fixture export 0. 실패-only resume와 원문 보존, 잘못된 side/frame/pose/hash/권리/방향/분모/불연속 path의 거부도 검사했다. 실제 최종 자산 hash는 `final-asset-hashes.json`에 있다.

## 경로와 한계

LI·TE의 양측 인접 82쌍 중 실제 지원 표면이 연결된 **50쌍, 843개 triangle 구간**을 렌더한다. 32쌍은 seam·서로 다른 patch·분지 경계에 연결 표면이 없으므로 직선으로 관통시키지 않았다. 목록은 `route-audit-r19.json`, `remaining-units-final.json`에 있다. 전체 전통 유주/분지/내행을 같은 자료라고 주장하지 않는다. 이는 미해결 제품 점 수가 아니라 그리지 않은 구간 목록이다.

정밀 위치 86개 미확정, 교수 검토 `not_performed`, 교재 설명 43개 `pending`, 공개 권리 `held`는 별도 상태다. 기술/교육용 위치의 합격이 이들을 승인한 것은 아니다.

## 비용과 전달

처음 전체점 로딩은 1,354,379-byte 추가 전달로 기존 overview 예산에서 실제 거부됐다. 제한을 올리지 않았다. LI/TE observation JSON을 공통 loader의 무손실 gzip binary 전달로 바꾸었다. 전달된 byte SHA를 먼저 검사하고 압축을 푼다. `.gz`는 개발 서버가 자동으로 해제하는 헤더를 붙이므로 explicit encoding을 갖는 `.bin`을 사용한다. 압축 전/후 JSON의 byte·좌표·근거는 일치한다. decoded document 비용도 별도로 기록했다. 학습 위치를 낮은 정밀도로 quantize하지 않았다.

최종 108점(LU22+LI40+TE46) 전체 로딩의 실제 측정:

| 항목 | 추가 | 기존 + 추가 | 기존 한도 |
|---|---:|---:|---:|
| encoded overview bytes | 864,686 | 20,907,202 | 20,971,520 |
| GPU geometry buffer bytes | 454,576 | 17,892,124 | 100,663,296 |
| triangles | 38,432 | 935,644 | 1,000,000 |
| 기존 LU 영역 동시 ON bytes | 10,600 | 20,917,802 | 20,971,520 |
| 기존 LU 영역 동시 ON triangles | 702 | 936,346 | 1,000,000 |

신규 carrier 23개 chunk는 20,928 bytes / 820 triangles이다. 실제 사용 face와 두 edge-neighbour ring을 lossless subset으로 남겼고 source vertex/face map을 보존했다. smoothing/fill/새 전신 조형은 하지 않았다. decoded document 844,822 bytes, texture 0, 전체 overlay geometry 42개, carrier OFF 예상 draw calls 110을 기록했다. 세션 종료 후 overlay geometry·projection diagnostic·camera ownership 해제를 확인했다.

## 실제 화면 및 검사

- 1440: 86개 실제 점 선택·side·이름·국소 구조/label/가림 전수 검사. `visual-final-86.json`은 r18의 유지된 80개와 r19b 수정 6개를 연결한다. 8개 contact sheet와 원본 PNG를 직접 판독했다. 과거 실패 화면은 덮지 않았다.
- 390/1024: 각각 양측 LI 특수 4혈·TE 특수 8혈, 총 24개씩 검사. point와 주변 native 구조가 카드/하단 조작부를 제외한 가시 영역에 있었다. 모바일 접기/펼치기도 확인했다.
- LU1/LU9/LU11 양측 6개 회귀 검사. 태연·소상 명칭 유지. 전체점 108개, 기존 LU 면·점·경로·카드 동시 표시와 빠른 OFF 확인.
- 카드/검색/실제 3D marker 클릭, 좌우/경맥/전체점 전환, 로딩 중 닫기와 재진입, bone OFF 보존, 원래 대퇴직근 카드 복귀 확인. CV catalog는 정중 선택만 있고 제품 point/geometry/camera ownership 0임을 확인했다.
- 일반 이동과 reduced motion을 검사했고, 따라보기 도중 ArrowLeft 수동 입력 후 `tour=paused`, `userMoved=true`, `autoReturn=false`를 실제 확인했다.
- 변경 관련 **57 tests 통과**, typecheck 통과, production build 통과. 초기 JS 1,327,531 bytes이며 acupoint module은 지연 entry다. bundle manifest의 private evidence/source cache entry 0. 최종 console errors/warnings 0. 기존 큰 motion chunk의 build 경고는 한도 완화 없이 보존했다.

최종 인수 결과는 `acceptance-final.json`. 이번 AT8 필수 잔여 unit은 없다. 지원되지 않는 32개 경로 연결, 정밀 위치·교재·교수 검토·공개 권리는 명시한 별도 한계다. 이후 요청 없이 이를 자동 승인하거나 다음 작업을 시작하지 않는다.

## 기록과 로컬 commit 경계

최신 EXECUTION을 다시 읽어 AT8 record와 `featurePlans.acupoint-at-361.nextUnit=AT9`만 갱신했다. 다른 AT/MV/T/AC record는 deep-equal 확인했다. `sync_execution.py` 및 `--check` 결과를 evidence에 기록한다.

선별 commit 대상은 공통 registry/loader/compiler/선택 연결과 관련 검사·offline 도구, 최종 LI/TE package와 carrier, AT8 최종·실패 판정 evidence와 report, 위 EXECUTION 변경이다. 시작 WIP 45개, 기존 원본/역사 evidence, AT/MV 다른 작업과 대형 build 출력·중복 compiler input 사본·사용하지 않는 후보 carrier는 제외하고 로컬에 보존한다. 정확한 포함/제외 경로는 `owned-stage-paths.json`, commit 후 hash와 잔여 status는 `local-commit-receipt.json`을 따른다. push/배포는 하지 않았다.

다음 프롬프트: `work/evidence/AT8/2026-10-13-r1/NEXT-AT9.md`. AT9 자동 실행·위임은 하지 않았다.
