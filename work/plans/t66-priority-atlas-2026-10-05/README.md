# T66 우선 근육 Atlas 학습 — 2026-10-05

최신 사용자 요청은 전신 일괄 제작에서 우선7근육군 완성 후 점진 확장으로 바뀌었다. 이 개정은 과거 전체 제작 가능 패키지의 일괄완료 gate보다 우선한다. 근육 전체 원장과 실패 자산/evidence는 그대로 남긴다. 범위 밖 실패는 deferred engineering backlog이며 실제 geometry 부재나 content gap으로 재분류하지 않는다.

## 수동 실행 순서

1. 01-nerve-learning.txt: 현재 신경 표시/주행/지배·관련 근육 학습 연결
2. 02-ankle-knee.txt: 앞정강근·대퇴직근
3. 03-shoulder-scapula.txt: 대흉근·견갑거근·대/소능형근
4. 04-trunk.txt: 복직근·외복사근
5. 05-integration-close.txt: 우선 범위 검증·T66 판정 후 T85 인계

모두 T66 내부 실행이다. 각 파일은 전체 프롬프트이며 합쳐 입력하지 않는다. 현재 writer/common runtime을 같은 checkout에서 병렬 수정하지 않는다. 이 작은 범위에서는 새 manifest/worker dispatch보다 기존family 재사용→근육별 end-to-end 제작·등록·화면 확인을 우선한다. 새 모델만 별도 소유family/input/hash 경계를 고정한 경우에 한해 사용자 승인으로 분리할 수 있다. 자동 병렬/새thread 금지.

## 완료 의미

7근육군의 실제 available source/side/part별 적합한 대표 작용 애니메이션, 동일scene/단일CTA/복원, 현재 지원 신경 주행·관계 카드/강조의 안정성이 필수다. 양측available geometry의 변형 실패를 미확보로 꾸미지 않는다. 향후 추가 작용·전체 근육/뼈/신경 dynamics·턱/얼굴/호흡 실패는 별도 원장에 남긴다. 범위 개정 자체는 제품 pass가 아니며 현 T66은 partial이다.
