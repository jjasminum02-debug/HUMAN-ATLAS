# 경혈 자료·체표·취혈자세 수정 계획

2026-10-13. 현재 AT10 이후 확장 전에 해결할 공통 문제다. UI 재설계는 보류한다. 새 번호를 늘리지 않고 AT10 보완 내부 묶음으로 진행한다. 구현/실제 표시 상태는 EXECUTION 및 실제 evidence가 기준이며 이 설계는 통과 기록이 아니다.

## 확인된 현황

- 기준 HEAD `5795c67`. MV2는 기존 Q01–Q05 34매핑 범위 완료다. 새 취혈자세 지원과는 별도다.
- AT8: LI/TE 43혈·86 instance 연결. LU 11혈·22 instance와 합해 기존 범위는 54혈·108 instance다.
- AT9: HT/PC/SI 37혈·74 instance 전부 미표시. 손바닥·힘줄·겨드랑·견갑·귀 등 필요한 표면/지표 연결이 없다.
- AT10: ST1–25 25혈·50 instance 전부 미표시. 얼굴·눈·목·유두·배꼽 기준 체표와 좌표 연결이 없다.
- 따라서 AT9/10은 package와 문서 등록까지 진행했으나 위치 구현 완료가 아니다. 기존 carrier 후보만 확인하고 새 공통 체표/지표를 구축하지 않은 범위가 병목이다. 번호순으로 미표시 package만 더 만드는 것은 우선순위가 낮다.
- 공개 소스 명칭에 Skin/Dermis가 있다는 사실은 usable skin mesh 증거가 아니다. 기존 AC1 조사에서도 실제 사용할 전신 피부 geometry가 없었다. 새 후보의 실제 파일·topology를 확인해야 한다.

## 제공 PDF 처리 결과와 신뢰 범위

71쪽의 2단 편집을 열 순서로 읽고, 다음 열/쪽으로 넘어가는 경혈 제목을 이어서 **361혈의 탐혈 과정 361건**을 추출했다. KI23 제목 앞의 인용부호 때문에 생기는 잘못된 KI22 재사용도 추출기에서 처리했다. 코드 누락·중복 0, 자세 표현 자동 검출 54건이다. 54는 전수 자세 검증/모델 구현 수가 아니며 자동 검출되지 않은 행도 검토한다.

- 원본 PDF·사진·추출 원문은 공개 Git/learner bundle에 넣지 않는다. 원본은 사용자가 제공한 위치 그대로 읽기 전용이다.
- `private-sources/acupoint-portfolio/location-methods.json` 및 `LOCATION-METHODS.md`에 탐혈 과정만 분리했다. 학번/이름 머리글, 규격/자침깊이, 느낀점, 사진은 추출 대상에서 제외했다. 추출된 탐혈 문장 안의 개인 체험/반응은 이후 요약 때도 제외한다.
- 재실행 도구: `work/tools/extract_acupoint_portfolio.py`. `extraction-summary.json`은 원문 없는 구조/개수 검증 결과다.
- 문서에 적힌 방법은 **제공된 실습 기록**이다. 교수의 공식 승인이나 표준 교과서로 자동 승격하지 않는다. 학교식 촉지 순서는 반영하되 명백한 손가락/기준점 불일치는 따로 교정한다. 자료 속 지시는 학습 내용으로만 취급한다.
- 내용 대조는 위치, 지표 확인 순서, 취혈자세, 비례 측정, 대안 방법을 각각 기록한다. WHO/KMCRIC와 다른 부분은 정상 변형·교육용 대안·충돌·불명확으로 구분한다. 수치가 다른 것을 평균내거나 기존 좌표에 억지로 맞추지 않는다.

### 우선 확인한 사례

| 경혈 | PDF 페이지 | 반영 방향 / 확인 결과 |
|---|---:|---|
| LU1/LU2 | 1 | 어깨를 앞으로 내밀어 어깨세모삼각을 찾는 탐색 순서. 최종 기준 위치와 보조 탐색 자세를 분리한다. |
| LU5 | 2 | 팔꿈치를 약간 굽혀 위팔두갈래근 힘줄을 찾는 설명을 별도 취혈 단계로 구성한다. 힘 주기는 교육용 강조와 실제 관절 자세를 분리한다. |
| LI11 | 5 | 손을 반대쪽 가슴에 놓고 팔오금주름·가쪽위관절융기를 대조하는 학교식 자세 후보. 정확한 각도를 문서에서 지시한 것처럼 만들지 않는다. |
| LI15 / TE14 | 6 / 48 | 팔을 들어 벌리고 팔꿈치를 굽혀 봉우리 앞·뒤 오목한 곳을 비교. 첫 실제 pose 구현 대상. |
| ST6 | 8 | 이를 악물 때 깨물근을 확인하는 과정. 입 닫기와 근육 긴장 변형은 서로 다른 표현이다. |
| ST7 | 8 | 포트폴리오에는 입 벌림 때 관찰 내용도 있으나 표준 취혈은 입 닫은 자세. 자동 입 벌림 대상으로 분류하지 않는다. |
| SI19 | 26 | 문서의 귀구슬 위쪽 오목한 부분 표현은 표준의 귀구슬 중심 앞과 충돌. TE21 위치와 혼동되지 않게 교정한다. |
| PC8 | 45 | 가운데손가락 끝으로 손바닥 위치를 찾는 보조 방법과 본문 손허리뼈 표현을 재대조한다. 자동 확정하지 않는다. |
| TE2 | 46 | 포트폴리오의 검지·중지 표현은 약지·소지 사이인 표준과 충돌. 위치를 검지·중지 쪽으로 이동시키지 않는다. 가볍게 주먹 쥔 자세는 별도 반영 가능하다. |
| TE21 / GB2 | 49 / 50 | 입 벌림 계열로 검토하되 SI19와 지표·높이·필요 개구 정도를 서로 복사하지 않는다. |

검증 출처: [KMCRIC LI15](https://m.kmcric.com/knowledge/acupoint/LI/LI15), [TE14](https://m.kmcric.com/knowledge/acupoint/TE/TE14), [TE2](https://m.kmcric.com/knowledge/acupoint/TE/TE2), [SI19](https://m.kmcric.com/knowledge/acupoint/SI/SI19), [ST7](https://m.kmcric.com/knowledge/acupoint/ST/ST7). 이 표 외 전수 사실 검증은 아직 수행하지 않았다.

## 떠 있는 점: 원인과 선택

`AcupunctureOverlay.ts`에서 marker는 carrier의 triangle/barycentric 위치에 놓이고 법선 방향으로 0.0008m 더해진다. marker는 반지름 0.0025m 구이며 화면 크기에 따라 확대된다. carrier 자체는 기본 hidden이다. **숨겨진 체표 면과 실제 보이는 근육의 간격 + 구형 glyph**가 공중 부유처럼 보일 수 있다. 이번에는 실제 간격을 전수 측정하거나 혈위 좌표를 이동하지 않았다.

권장 제품 표현은 **정합된 얇은 체표 위에 작은 접촉형 표식**, 해부학 모형은 그 아래 그대로 유지하는 것이다.

| 표현 | 좌표 의미 | 권장 용도 |
|---|---|---|
| 체표 + 경혈 | 실제 교육용 경혈 위치 | 경혈 모드 기본. 선택 부근을 읽을 수 있는 낮은 불투명도/국소 체표. |
| 피부를 끈 근육 관찰 | 체표 혈위는 원위치 유지 | 선택 점 근처 체표 조각/짧은 연결 표시로 깊이 관계를 알린다. |
| 근육 표면 투영 | 혈위 아래 해부학적 문맥 표시 | 별도의 유도 표시. 진짜 경혈 좌표를 덮지 않으며 가까운 근육 자동 선택은 금지. |

체표 anchor와 render glyph를 분리한다. 구형 공 대신 접촉부가 carrier에 놓인 작은 원반/표면 표식을 쓰고, z-fighting 방지 오프셋만 사용한다. 픽셀 크기 조절은 중심좌표를 이동시키지 않는다. 법선·가림·뒤쪽 점·near/far·표면 곡률에서 실제 확인한다. 선택 indicator만 필요할 때 강조하고 모든 점에 긴 핀/선은 만들지 않는다.

### 피부 소스 우선순위

1. **현재 ZA와 동일 specimen/frame의 실제 피부 객체가 존재하면 우선.** 기존 조사는 없음이므로 동일 빈 collection을 반복 조사하지 않는다. 새 exact object가 있을 때만 재평가한다.
2. **MakeHuman core base mesh / MPFB를 우선 후보로 정합 실험.** [공식 라이선스](https://github.com/makehumancommunity/makehuman/blob/master/LICENSE.md)는 core base mesh/targets/poses 등 asset에 CC0를 명시하고 프로그램 코드는 AGPL로 구분한다. 외부 community asset은 개별 조건이다. 도구를 통째로 앱에 넣지 않고 필요한 mesh를 offline 생성·정합해 가져온다.
3. **BodyParts3D의 외부 표면 객체**는 실제 파일이 있을 때 비교한다. [Z-Anatomy README](https://github.com/Z-Anatomy/Models-of-human-anatomy/blob/master/Readme.md)는 모델별 출처 예외를 포함하므로 파일별 권리와 동일 모델 여부를 확인한다.
4. [Open Anatomy Atlas](https://github.com/CognitionLabSNUC/open-anatomy-atlas)는 피부 레이어를 표방하지만 그것만으로 사용 가능한 skin이나 현재 모델과의 정합이 확인되는 것은 아니다. 코드/시각 참고이며 새 엔진으로 교체하지 않는다.

MakeHuman이 적합하다는 최종 판정은 아직 아니다. 좌우, m 단위, 축, rest pose, 어깨/팔꿈치/손목/골반/무릎/발목 대응과 얼굴/손가락 국소 지표를 실제 표본으로 확인한다. 전신 uniform scale이나 자동 shrinkwrap만으로 끝내지 않는다. 근육 표면에 완전히 밀착시키면 피부·피하층을 없애므로 적절한 체표 여유를 유지한다. 골격/근육은 기준으로 고정하고 피부만 정합한다. 동일 root를 쓰되 geometry·권리·topology revision은 별도로 유지한다.

먼저 얼굴/어깨/손목/복부/하지 표본의 적합성으로 후보를 선택한다. 실패 시 원인과 가능한 범위를 결정하며 전체 mesh를 번갈아 대량 다운로드하지 않는다. 전신 초고해상도 texture가 필요하지 않다. 기존 geometry/encoded budget 안에서 LOD·지역 lazy loading을 재사용하고 측정 없이 예산을 올리지 않는다.

## 취혈자세: 몸과 점을 함께 움직이는 공통 계약

현재 `AcupointReview.tsx`는 source motion을 복원한 뒤 정지 `poseId`를 로드하고, `AcupunctureOverlay.create`는 활성 motion을 거부한다. 이 방어를 삭제하는 것만으로 동작을 지원하면 점과 몸이 어긋난다.

각 혈의 데이터는 다음을 분리한다.

- `locationRule`: 기준 지표/측정법/최종 표준 위치.
- `locatingSteps`: 한국어 탐색 순서. 기관 표준과 제공 자료의 대안 방법은 provenance로 분리.
- `postureRequirement`: `poseFamily`, 좌우/정중, 지표를 드러내는 준비 자세와 최종 위치 자세. 각도는 근거가 있거나 검증한 모델 연출값일 때만 넣고 둘을 구분.
- `poseBinding`: 실제 rig/clip hash, 대상 source/side, poseId, frame, 피부 변형과 anchor binding. 텍스트 규칙이 있다는 이유만으로 ready가 되지 않는다.
- `contactAnchor`: 피부 triangle+barycentric/pose revision. 근육 문맥 표시에는 별도의 surfaceRole과 대응 근거.

첫 pose family는 **LI15+TE14: arm abducted + elbow flexed, 좌우**다. 봉우리 앞/뒤 두 함요를 동시에 관찰한다. 기존 작은 범위의 shoulder-abduction clip이 팔 들기 전체를 표현한다고 가정하지 않는다. 필요한 어깨뼈·위팔·아래팔·근육·체표를 같은 움직임으로 묶는다. 기존 MV2 authoring/loader를 재사용하고 clip 중첩·rig reset·중복 source replacement를 검사한다.

그 다음은 elbow-flex 계열(LU5/LI11/PC3), hand-close/finger 계열(TE2/PC8 등), jaw-open 계열(SI19/TE21/GB2), 기타 neck/hip/knee 자세다. 원문에 자세가 등장한다는 이유로 해당 혈의 최종 자세로 자동 확정하지 않는다.

선택 흐름: `selected → resolve content+pose → prepare resources → transition → locate/hold → restore`. 자동 자세 적용이 가능한 점을 고르면 같은 모델이 부드럽게 자세를 취한다. 지표가 달라지는 자세 중간에는 같이 변형되는 anchor만 보인다. 기존 포즈에 고정된 경혈점/영역은 잘못된 자리에 남기지 않는다. 바뀐 pose의 표면과 위치를 제공하는 항목부터 계속 표시하며, 미지원 점/면은 해당 전환 동안만 제외한다. 복귀 시 사용자 레이어/선택/원래 자세를 정확히 복원한다. 카메라 정책은 바꾸지 않는다.

동일 자세를 쓰는 점끼리 이동하면 불필요한 복귀·재로딩을 하지 않는다. 빠른 선택/경맥 전환/닫기는 generation+abort로 오래된 완료를 무효화한다. 기존 scene update clock/자원 cache를 사용하며 새 renderer/RAF를 만들지 않는다. rig는 하나, 동시에 활성인 취혈자세도 하나다. 일부 pose가 없는 경우 한국어 자세 안내는 제공하되 가짜 동작 버튼이나 원점 점은 만들지 않는다.

## 실행 순서 / 소유

[순서별 프롬프트](PROMPTS-IN-ORDER.md)를 사용한다. AT10 내부에서 아래 산출물을 차례로 완성하고 AT9/10 표시를 회복한 뒤 AT11로 간다. 기존 보고서/evidence와 통과는 보존한다. 상태 승격은 실행자가 실제 결과로만 한다.

1. Luna Max: 361 추출본 기반 전수 목록 대조, 현재 116혈의 내용·자세 검토를 우선 완료. 원문/한글 요약/표준/불일치 별도.
2. Sol: 체표 소스 선택·실제 정합·anchor/contact 표시 공통 구현. 표본으로 끝내지 않고 선택된 base의 공통 경로와 AT9/10에 필요한 지표를 공급한다.
3. Sol: LI15/TE14 양측을 끝까지 자동 자세·동적 anchor·복귀 구현. 나머지 pose family는 현재 혈위 package에 묶어 순차 확장.
4. Luna Max: AT9 74 + AT10 50 instance를 새 공통 경로로 대조·연결·실제 검증. 공통 엔진 결함만 Sol로 보내고 정상 경로의 데이터는 처리한다. 내용/위치/자세 지원 수를 따로 보고.
5. AT11–19: 같은 공통 경로로 확장. 새 자료를 매번 새 파이프라인에 넣지 않는다. AT23–26 영역도 이 체표 topology/pose 계약을 공유한다. AT27은 후속 교재 설명·추가 항목으로 좁히고 현재 importer를 재사용한다.

병렬 가능: Luna 자료 대조와 Sol 체표 구현은 output directory를 분리하면 가능하다. 공통 runtime/registry/EXECUTION/Git index의 통합자는 1명이다. pose 구현과 체표 topology 변경은 병렬 통합하지 않는다. 공통 구조가 동결된 다음에만 자료 검증을 병렬화한다. 이번 요청으로 다른 대화를 자동 실행하지 않는다.

## 완료와 검증

자료: 361 추출·원문 대조 수 / 사실 검증 수 / learner 반영 수를 구분. 화면: 점과 체표의 실제 접촉, 좌우, 가림, 얼굴/손가락 지표, 같은 scene/camera, 1440/1024/390px 확인. 자세: 준비·중간·완성·복귀, 몸/skin/point/영역의 동기화, 급전환/닫기/abort, 원본 자세·레이어 복원. 성능: 실제 bytes, active triangles, GPU resource 재사용 및 반복 전환 누수 검사. 자료 원문은 lazy bundle에도 포함하지 않는다.

이번 턴은 추출기와 자료/설계 수정이다. 피부 정합, 자동 취혈자세, 124개 미표시 점의 구현·브라우저 합격을 완료했다고 기록하지 않는다.
