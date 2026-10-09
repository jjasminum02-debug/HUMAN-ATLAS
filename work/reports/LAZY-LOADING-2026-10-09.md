# 기능별 지연 로딩 개선

사용자의 JavaScript 최적화 요청에 따른 유지보수. 기준 HEAD `fb0741289603fdacbc54f21bef22963fb9b40707`.

## 반영 결과

홈에서 움직임 runtime과 재생 UI를 즉시 읽던 연결을 제거했다. 이름·검색·기시/정지·모형 렌더는 기존 기본 경로를 유지한다. 근육 기능 탭, 작용 탐색, 뼈/신경 설명처럼 움직임 자료가 필요한 시점에 `motionFeature`를 동적 import한다. 동일 세션의 요청은 하나의 Promise를 공유하고 성공한 모듈을 재사용한다. 모형 renderer/camera를 다시 만들거나 전체 화면 Suspense로 감싸지 않는다. 빠르게 다른 구조로 이동해도 로드된 모듈은 현재 선택의 exact source/side로 다시 계산한다.

기존 동작 resolver를 `motionLearningData.ts`로 이동했으며 sourceKey/side/intent/candidate 판단은 유지했다. 대용량 생성 파일과 사용자 motion WIP는 수정하지 않았다.

홈의 JS: **3,264,635 → 1,321,415 bytes**, 약 **59.5% 감소**. App 본체는 3,041,963 → 1,098,592 bytes. 움직임 기능 1,944,237 bytes는 후속 필요 시 로드한다. 이는 비압축 JS 기준이며 geometry와 전체 배포 용량, 다운로드 시간/FPS 측정값이 아니다. 전체 기능을 모두 열면 총량은 대체로 이전과 비슷하다. 기존 500KB chunk 경고는 3D와 지연 기능 묶음에 남고 경고 임계치를 높이지 않았다.

빌드 manifest를 생성하고 정적 import 그래프에서 움직임 feature가 홈에 포함되지 않는지 검사한다. 홈 JS 합계 2MiB 미만 회귀 기준도 build에 추가했다. 기존 모형 예산을 변경한 것이 아니다.

## 보기 옵션 원상복구

작업 중 보기 도구를 재배치했으나, 사용자가 직접 고치겠다고 요청하여 **이번 재배치와 새 표시 복원 조작을 모두 철회했다**. `WholeBodyViewer.tsx`는 시작 커밋과 byte 단위로 같다. 기존 보기 옵션 CSS도 복원했다. CSS에 남은 네 줄은 기능 자료 로딩/실패 안내 스타일뿐이며 보기 옵션과 무관하다. 이전 커밋의 카메라/검색 개선은 유지한다.

## 실패 처리

로딩 중과 연결된 자료가 없는 상태를 구분한다. 실패해도 해부학 장면과 구조 설명은 유지한다. 실제 503 테스트에서 브라우저가 실패한 module import를 캐시해 같은 URL 재시도만으로 복구되지 않는 것을 확인했다. 따라서 반복해 실패하는 재시도 버튼 대신 사용자가 명시적으로 누르는 `앱 새로고침`을 제공한다. 자동 새로고침하지 않는다. 새로고침은 URL의 선택 구조를 유지하지만 카메라/탭의 일시 상태까지 보존하는 기능은 아니다.

## 검증

- 지연 로딩/전체 source-side resolver 검사 6개, 기존 motion player/serializer 40개, dataset 76개: **122개 통과**.
- 기존 runtime source/side 대응 455건 검증 통과.
- production build, TypeScript, 배포 provenance 유출 검사, 새 import/용량 검사 통과.
- production JS로 홈→앞정강근 구조 카드까지 움직임 chunk 요청이 없음을 서버 로그로 확인. 기능 탭에서만 첫 요청.
- QA 서버의 의도적 503에서도 모형과 선택을 유지하고 실패 안내 표시. 명시적 새로고침 후 기능 로딩과 앞정강근 실제 반복 재생 확인.
- 구조/기능 전환, 뼈의 움직임 선택 목록, 21개 작용 범주 탐색 확인. 캐시된 기능 재사용, 같은 canvas 유지.
- 1280×800, 390×844 실제 화면 확인 및 캡처. 브라우저 도구의 console error/warning 목록은 비어 있었으며, 의도적 503 두 건은 요청 로그에 별도로 남았다.
- QA 서버는 빌드 JS/CSS를 제공하고 모형 endpoint만 동일 체크아웃의 로컬 Vite로 연결했다. 배포 검증이나 모든 근육 애니메이션 전수 검사라고 부르지 않는다.

## 보존 및 Git

기존 tracked WIP는 기준선 hash와 일치한다. OpenSim 원본 clean 유지. EXECUTION/STATUS/registry, 콘텐츠, 자산과 task 순서는 바꾸지 않았다. 이번 기능 분리와 검사, 보고서 및 필요한 evidence만 로컬 커밋한다. 원래 미커밋 사용자 변경은 제외하고 그대로 둔다. push/배포 없음. 최종 hash와 잔여 변경 목록은 evidence의 `commit-receipt.json`에 기록한다.

증거: `work/evidence/lazy-view-options-2026-10-09/validation.json`, `bundle-split.json`, `structure-before-motion.json`, `preview-requests-frozen.jsonl`, 최종 화면 캡처와 검사 로그.
