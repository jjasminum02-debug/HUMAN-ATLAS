# T15e 실제 브라우저 검증 — 2026-09-26

대상: Codex in-app browser, 로컬 Vite `127.0.0.1:4173` 및 빌드 정적 서버 `127.0.0.1:4174`. 테스트 후 서버를 종료한다. 브라우저 localStorage의 T09/T13b 원시 사용자 초안은 읽기·저장·삭제하지 않았다.

| 동작 | 관찰 |
|---|---|
| 기본 종아리 → 머리 → 뒤로가기 | 머리에는 준비 중 상태와 3D canvas 부재, 뒤로가면 종아리 근육 카드/장면 복귀. console error/warning 0. |
| 근육 재선택·선택 해제·뒤로가기·새로고침 | Soleus 선택 URL/카드 일치. 해제 후 `?region=leg&side=right`와 빈 카드, 새로고침에도 빈 선택 유지, 뒤로가면 전 근육 카드 복귀. |
| annotation 문맥 수명 | Soleus의 기시 문맥 선택 시 관련 뼈 강조 안내. 선택 해제 뒤에는 문맥 안내와 근육 설명이 사라짐. 학습 화면은 읽기 전용. |
| T13 뼈 | femur 직접 typed URL에서 오른쪽 Femur 카드, Gray 1918 근거 요약 및 대퇴골 모델 표시. 최종 빌드 console error/warning 0. |
| resize | 390×720에서 canvas 374×165 CSS/실제 pixel, 1024×720에서 488×382. 기능 버튼과 선택 상태 유지, console error/warning 0. 뷰포트 override는 reset. |
| 없는 asset·로딩 실패·복구 | 정적 빌드의 두 GLB만 404를 반환하는 로컬 시험 서버에서 `3D를 불러오지 못했습니다` 경고와 Soleus 텍스트 카드 유지. 같은 포트에서 정상 서버로 바꾼 뒤 머리→뒤로가기에서 장면 재시도 성공. 이는 실제 원본 asset을 수정하지 않은 네트워크 실패 시험이다. |
| 빠른 부위 전환 | 종아리→머리 연속 클릭 뒤 머리 안내와 카드 비움 유지, 늦은 종아리 응답의 화면 덮어쓰기 없음, console error/warning 0. |
| 빈 부위 자산 범위 | 첫 구현에서 `?region=head` 직접 진입 시 기본 종아리 GLB가 선요청되는 문제를 발견했다. route 해석 완료 전 viewer 마운트를 막아 수정했다. 수정 후 정적 빌드 서버 로그의 머리 직접 진입에는 HTML/JS/CSS 요청만 있고 GLB 요청 0. 종아리 선택 시 T07/T13 GLB 각 1회 요청. |

경계: 실제 GPU 메모리 양은 계측하지 않았다. geometry/material disposal, WebGL context loss, ResizeObserver/OrbitControls/canvas listener cleanup은 코드 경로와 위 브라우저 전환·오류 회귀로 확인했다. 합성 빠른 응답/늦은 응답은 `sceneCache.test.ts`에서 검증했다. 실제 사용자 초안의 raw localStorage hash는 브라우저 평가 범위에서 얻지 못해 해시 일치를 주장하지 않는다.
