# AT10 portfolio-content r1

## 결과

361개 원문 추출 결과(고유 코드 361, 누락·중복 0)를 재사용하고, 현재 등록된 116개 개념(LU 11, LI 20, TE 23, HT 9, PC 9, SI 19, ST1–25 25)의 표준 위치·탐색 순서·자세 후보·학교식 대안을 한국어로 비교 요약했다. 361개 추출과 116개 사실 비교를 별도 집계했으며, 범위 밖 245개는 사실 검토하지 않았다. 전체 OCR/추출기는 재실행하지 않았다.

등록 116개 비교 처분은 정합 82, 대안 탐색법 22, 확인 보류 10, 명시 충돌 2다. 이 처분은 교수 승인이나 학습자 반영을 뜻하지 않는다. 361개에서 자동 추출된 자세 문구 후보는 54개, 등록 116개 안에는 38개가 있으며 실제 model pose binding/support는 0이다. 교수 검토 0, learner import 0이다.

TE2는 탐색 자세 자체와 손가락 쌍을 분리해 기록했다. 가벼운 주먹은 표준과 맞지만 자료의 손가락 쌍은 표준의 약지·새끼손가락 사이와 충돌한다. SI19는 귀구슬 중심 앞모서리와 TE21–GB2 사이, 약간 벌린 입을 기준으로 정리했다. ST7은 입을 다문 자세를 최종 기준으로 두고 입 벌림은 보조 관찰로 구분했다. PC8은 둘째·셋째 손허리뼈 사이의 표준을 유지하고, 손가락 끝 방법과 셋째·넷째 손허리뼈 대안 의견을 병합하지 않았다.

## 산출물 및 검증

- 비공개 구조 자료: `private-sources/acupoint-portfolio/reviewed/portfolio-content-r1.json` (현재 .gitignore 대상, 원문·사진·개인정보 미포함)
- 비공개 요약 검증표: `private-sources/acupoint-portfolio/reviewed/summary-verification-r1.md` (116개 행, 원문 인용 없음)
- 실행 evidence: [review-index.json](../evidence/AT10/2026-10-13-portfolio-content-r1/review-index.json), [page-visual-review.json](../evidence/AT10/2026-10-13-portfolio-content-r1/page-visual-review.json), [validation.json](../evidence/AT10/2026-10-13-portfolio-content-r1/validation.json)
- 우선 사례 원본 시각 확인은 PDF 8, 25, 26, 45, 46쪽에 한정했다. 기존 추출 검증 4/4를 재사용했다. 이미지·원문은 evidence에 복사하지 않았다.
- JSON은 설계서의 공통 content 필드(`locationRule`, `locatingSteps`, `postureRequirement`, `poseBinding`, `contactAnchor`)와 기존 learner code/name/channel identity를 사용한 private importer input이다. 현재 runtime package에는 import하지 않았다.

## 경계 및 남은 상태

AT10 전체는 아직 partial이다. 이번 묶음에서 116개 요약을 작성했지만 10개 불확실 항목과 TE2/ST7의 표준 충돌은 보존했다. 실제 체표 확보·정합, 좌우 anchor/접촉, 자세 재생, learner import, 화면 검증은 수행하지 않았다. `work/EXECUTION.json`은 AT8/9/10 어디도 바꾸지 않았다.

시작 HEAD는 `1b5a3e2e19b81fc173bd296a791e8727095c036d`이며 시작 status snapshot과 입력 SHA는 evidence `start.json`에 있다. 현재 별도 활성 surface worker는 앱 thread/agent 목록에서 확인되지 않았으나 macOS `ps`는 권한 거부로 조회하지 못했다. 기존 AT8 carrier WIP, OpenSim_Models/T13, 타 사용자 WIP는 보존하고 제외했다.

## 다음 프롬프트

다음은 AT10 `surface-base` (Sol xhigh)다. 복사용 전문은 [NEXT-AT10-SURFACE-BASE.md](../evidence/AT10/2026-10-13-portfolio-content-r1/NEXT-AT10-SURFACE-BASE.md)에 남겼다. 자동 실행하지 않는다.
