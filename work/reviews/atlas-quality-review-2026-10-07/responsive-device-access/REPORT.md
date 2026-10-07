# 반응형 UI와 로그인 없는 링크 공유 준비

화면 개선은 실제 로컬 앱에 반영했다. 로그인 UI는 만들지 않는다. 외부 공유 연결은 아직 열지 않았으며, Cloudflare 임시 공개 범위에 대한 승인 대기 상태다. 이번 변경으로 기존 T40/T66/T85의 상태나 콘텐츠 승인을 변경하지 않았다.

## 실제 변경과 검증

- 1100px 이하에서 탐색/설명 패널을 접을 수 있는 배치로 전환했다. 짧은 가로 화면에서는 설명을 오른쪽에 배치한다.
- 보기 옵션 버튼은 사용 가능한 폭에 맞춰 줄을 바꾸고, 실제 도구 높이를 ResizeObserver로 측정해 모형과 겹치지 않게 한다. 측정은 React 상태나 scene 재생성을 유발하지 않는다.
- 긴 한국어·영문 이름 줄바꿈, 최소 폭, 검색 글자 크기, 동적 화면 높이와 safe area를 처리했다. 사용자 확대는 제한하지 않았다.
- 자료 준비/실패 화면을 새 카드로 바꾸었다. 실제 진행 수가 있을 때만 수치를 표시한다. 타이머나 임의 백분율을 넣지 않았다. reduced-motion에서도 진행 표시가 보인다.
- 320×740, 390×844, 430×932, 768×1024, 820×1180, 1024×1366, 1100×800, 1101×800, 1280×800, 1440×900, 844×390의 실제 브라우저 viewport에서 긴 신경 이름, 도구 버튼, canvas/설명 경계를 검사했다. 최종 원장 11행에 버튼/텍스트 넘침과 패널 겹침이 없으며 canvas는 하나다.
- 휴대폰 크기에서 대퇴직근 선택→기능→단일 CTA 반복→재클릭 복원과 목/종아리 중복 부위 선택을 확인했다. 태블릿/노트북 긴 이름 카드의 실제 화면을 기록했다. 최종 로컬 앱 콘솔 오류는 0건이다.
- 로딩 캡처는 QA 서버에서 GLB 응답을 8초 지연시켜 실제 pending UI를 관찰했다. 로딩 속도 측정값으로 사용하지 않는다.

타입 검사, 기존 로컬 전달 회귀 9/9, production build와 생성 데이터 freshness/스냅샷 검사가 통과했다. sync_execution --check는 무변경 일치를 확인했다. main JS 3.66 MB 경고는 남아 있으며 예산을 올리지 않았다. 새 공유 runner의 문법 검사는 통과했지만 실제 외부 연결 검증은 승인 후 수행해야 한다.

아이폰·아이패드 실기기 및 iOS Safari의 터치/키보드/메모리 검증은 수행하지 않았다. CSS viewport 확인을 실기기 검증으로 부르지 않는다. 구현 근거: [WebKit safe area](https://webkit.org/blog/7929/designing-websites-for-iphone-x/), [WebKit dynamic viewport](https://webkit.org/blog/12445/new-webkit-features-in-safari-15-4/).

## 공유할 구체적인 결과

현재 검증 패키지는 `local-20261007091253333-bf4218bb`, manifest SHA256은 `b0bb98868d92f5874a99bf37264e125e951ac4cadf2996ebf104d991c0402e3a`다. 공개 경로 후보는 앱 5, anatomy 18, motion 74, projection 2의 99개 파일, 253,793,341 bytes다. 전체 URL/해시는 share-manifest.json에 고정했다. 비교 결과 anatomy/motion/projection 94개는 이전 패키지와 동일하다.

이는 보존된 작업 트리 스냅샷이며 commit-only 전달물이 아니다. 기존 WIP 의존 19개를 원본 그대로 패키지에 담되 타인의 소유 파일을 커밋하지 않았다. 비공개 원장 105,085,638 bytes는 서버 검증에만 쓰며 공개 allowlist에 없다. repo, .internal, 원본, OpenSim_Models, T13, 작업 보고서/원장은 웹 제공 대상이 아니다. 기존 전달 서버의 비공개 경로 거부 검사를 재사용했다.

`shareLocalDelivery.mjs`는 이 검증 패키지만 127.0.0.1에 바인딩하고 공식 cloudflared로 연결하도록 준비했다. 로그인/계정/개인 비밀번호를 요구하지 않는다. 실제 공개 연결은 실행하지 않았다. 자동 승인 검토가 “Cloudflare라는 외부 목적지와 인증 없는 공개 범위의 구체적 승인 부족”을 이유로 임시 공개 링크 생성을 거부했다. 우회하지 않았다.

승인 대상은 **Cloudflare trycloudflare.com으로 위 99개 앱·모형 파일을 로그인 없이 제공하는 임시 URL**이다. 링크를 아는 누구나 열 수 있다. 별도 서버/도메인은 필요 없지만 이 노트북과 연결 프로그램이 켜져 있어야 한다. 종료/잠자기에는 중단되며 재시작 시 주소가 바뀐다. 상시 접속 URL의 완료로 보고하지 않는다. [Cloudflare 공식 Quick Tunnel 설명](https://developers.cloudflare.com/tunnel/get-started/quick-tunnels/).

`source-only`, 공개 재배포 권리 `held`, `humanReview=not_performed`, 전체 콘텐츠 `partial`은 독립적으로 보존했다. 이번 기술 준비를 권리/사람 검토 승인으로 변경하지 않는다.

## 증거와 현재 사용 주소

- 로컬 사용: http://127.0.0.1:5184/ (이 컴퓨터에서만 사용 가능)
- final-validation.json: 검사, 스냅샷/불변 파일 비교, 실제 캡처 크기/해시
- nerve-layout-matrix.json: 11개 실측 viewport의 배치 검사
- before-tablet.jpg: 이전 768px 배치의 잘린 보기 옵션
- tablet-768.jpg / laptop-1440.jpg / phone-motion.jpg: 개선한 실제 앱
- loading-phone.jpg: 실제 준비 상태 캡처

외부 링크 생성/외부 기기 검증은 승인 후 남은 작업이다. 기존 번호 task나 다음 개발 단계를 자동 실행하지 않았다.
