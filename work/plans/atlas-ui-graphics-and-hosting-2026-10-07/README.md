# Atlas UI·그래픽 개선과 Hobby 전달 준비

2026-10-07. 이 문서는 실행 프롬프트이며 실제 구현 완료 증거가 아니다. 이번 계획 작성에서는 앱 코드를 변경하거나 외부 배포하지 않는다. 최근 첫 등장 카메라 효과는 이미 구현되어 있으므로 재구현하지 않는다. 기존 task queue의 새 번호/상태는 발급·변경하지 않는다.

한 단계씩 같은 checkout의 최신 결과를 읽고 직렬 실행한다. 공통 camera/presentation/material/selection/loader를 수정하므로 동시 writer는 충돌 위험이 크다. 새 agent나 자동 병렬을 만들지 않는다. 보고서가 아니라 코드·실제 화면과 영향 검증으로 완료를 판정한다.

| 순서 | 입력 파일 | 구체적 결과 |
|---|---|---|
| 1 | 01-layout-and-framing.txt | 큰 모형 영역, 안정적인 설명 카드/보기 옵션/resize |
| 2 | 02-observation-and-camera.txt | 깊은 구조 관찰, 앞/뒤/좌/우, 숨김·카메라 복원 |
| 3 | 03-materials-and-lighting.txt | 조직/선택/신경의 재질·깊이와 성능 검증 |
| 4 | 04-attachment-visualization.txt | 기시정지→관련 뼈, 근거가 있는 부착 영역 |
| 5 | 05-nerve-and-motion-emphasis.txt | 신경→지배근→기존 작용의 정확한 문맥·강조 |
| 6 | 06-vercel-hobby-package.txt | 최종 자산 경량화, Hobby 적합 패키지/대안의 실제 준비 |

4의 정확한 footprint 미확보나5의 미래 근육/신경 미확보는 다음 단계 실행을 막는 제품 결함이 아니다. 구현된 지원 기능의 wrong side/frame/복원 결함은 해당 영향 경로를 수리한다. 전체0-gap·전체 신경 동적pose·전체 근육 제작을 이 개선의 gate로 가져오지 않는다. 4에서 footprint가0이면 영역 시각화는 미구현으로 정확히 보고하면서 확보된 뼈 문맥 기능을 완료하고5로 진행한다.

모든 .txt는 보존·검증·종료 조건을 포함한 독립 프롬프트다. 파일 경로를 붙여 넣고 해당 파일만 수행하도록 요청하면 된다. 각 단계는 다음 파일을 안내하고 멈춘다. Luna Max 사용을 전제로 작성했다.

현재 근거: work/reviews/atlas-visible-body-comparison-2026-10-07/REPORT.md. 호스팅 판정: HOSTING-ASSESSMENT.md. 현재 실행 주소는 로컬이며 공개 배포 주소가 아니다. 실제 실행 시 snapshot/수치를 재확인한다.
