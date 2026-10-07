# HUMAN ATLAS 실행 최적화와 상시 공유 준비

현재 실행 경로에서 확인한 중복 데이터·반복 조회·불필요한 장면 갱신을 수정했습니다. Cloudflare Pages에 올릴 앱과 모형 패키지도 생성하고, 해당 전송 바이트를 로컬 브라우저에서 검증했습니다. **아직 외부에 배포하지 않았으며 고정 주소는 발급되지 않았습니다.** 남은 배포 입력은 배포 관리용 Cloudflare 계정 로그인입니다. 앱 이용자에게 로그인은 요구하지 않습니다.

## 수정과 측정

| 동일 입력의 비교 항목 | 변경 전 | 변경 후 | 감소 |
| --- | ---: | ---: | ---: |
| 동작 생성 TypeScript | 3,285,605 B | 2,603,904 B | 20.75% |
| 생성 데이터 gzip(level 9) | 228,249 B | 189,533 B | 16.96% |
| 주 앱 JavaScript | 3,663,146 B | 3,023,989 B | 17.45% |
| 최적화 후 앱·모형 전송 패키지 | 253,154,184 B 원본 | 189,612,910 B 전송 | 25.10% |

- `text/nodeBindings/instanceMatrix`의 동일 값을 공유하도록 생성 직렬화를 개선했습니다. 267 selector, 1,166 행의 전체 값이 변경 전과 deep-equal입니다. 이 행 수는 검증된 작용이나 실제 지원근육 수가 아닙니다.
- 이름·작용·신경 관계의 인덱스를 한 번 생성합니다. 기존 순서, 첫 일치, 모호한 이름의 미확정 처리, 좌우 필터를 유지합니다. 전체 실제 입력과 이전 조회 결과를 대조했습니다.
- 작용 탐색 목록은 사용자가 해당 탐색을 열 때 생성합니다. 선택 배열 참조를 안정화해 검색·패널 렌더가 불필요한 scene.setView로 이어지는 경로를 줄였습니다.
- 카드의 desktop 복원 breakpoint를 실제 CSS인 1101px에 맞췄습니다. 1024px에서 접은 카드를 1440px로 넓힐 때 다시 열립니다.
- 기존 단일 scene/renderer/camera/player, 프레임 재사용, idle draw 억제, cache/LRU/취소 경로를 유지했습니다. geometry, 동작 각도, 소재 품질, decoder, 승인 상태를 바꾸지 않았습니다.
- Node 평가 7회 중앙값은 7.77→6.25ms였습니다. 이름 조회 100회 전수 순회 중앙값은 1.47→0.123ms입니다. 작은 CPU 구간의 결과이며 앱 전체의 체감 속도나 FPS 증가로 해석하지 않습니다.

## 검증

관련 회귀 77건과 전달 검사 13건, 합계 고유 90건 통과. 정확 source/side 455개 대조, 타입 검사, production build, 생성 freshness, learner distribution audit, sync_execution --check 통과. 빌드의 주 JS chunk 크기 경고는 남아 있으며 예산을 올려 지우지 않았습니다.

실제 업로드 폴더를 HTTP gzip 전송으로 실행했습니다. 대퇴직근 왼쪽 무릎 폄의 원본 뼈·주변 근육 문맥, 반복 재생, 재클릭 smooth rest, scrub 유지, 근육 layer-off 차단과 복원을 확인했습니다. 동작 탐색에서 오른쪽 견갑거근을 선택하고 신경 검색에서 오른쪽 견갑배신경의 대/소능형근·견갑거근 링크와 작용 설명을 확인했습니다. console error/warning 0, canvas 1개였습니다.

실측 1440×900 / 1024×768 / 390×844에서 가로 overflow가 없었습니다. 390px 보기 옵션의 버튼 오른쪽 경계는 369px 이하였습니다. 실제 iPhone/iPad 기기나 모바일 Safari 검증은 아닙니다. GPU/VRAM/총 프로세스 메모리 및 browser FPS 전후는 측정하지 않았습니다. JPEG의 실제 치수와 해시는 screenshots.json에 있습니다. 초기 즉시 캡처 `compact-390.jpg`는 390×244로 잘려 있어 최종 화면 근거에서 제외했고, 별도 `nerve-390.jpg` 390×844를 저장했습니다.

186개 src/scripts/plugins 코드 파일을 목록화하고 실행·선택·신경 관계·애니메이션·renderer·loader/cache·generation·delivery 경로를 검토했습니다. 모든 해부학 상태나 모든 코드 분기의 완전성을 이번 결과로 주장하지 않습니다.

## 공유 방식과 구체적 산출물

Cloudflare Quick Tunnel은 노트북이 켜진 동안만 사용할 수 있어 이번 조건과 맞지 않습니다. Cloudflare Pages Direct Upload로 하나의 `.pages.dev` 주소에서 앱과 모형을 제공하는 방식을 준비했습니다. 도메인 구매, 앱 사용자 로그인, 별도 viewer, 별도 자산 저장소가 필요하지 않습니다.

Vercel Hobby의 CLI source upload 한도는 합계 100MB입니다. 이번 189.6MB 전송 폴더를 그 방식으로 바로 올리기 어렵습니다. Cloudflare Pages 파일당 25MiB 한도에 맞춰 GLB의 **전송만 무손실 gzip**으로 만들었습니다. 가장 큰 전송 파일은 17,220,355 B이며 모든 파일이 한도 이내입니다. `_headers`가 Content-Encoding을 지정하므로 브라우저가 기존 원본 바이트로 풀어 loader/hash/기하 검증에 전달합니다. 모든 anatomy/motion/projection 파일 94개는 이전 snapshot과 원본 bytes/SHA가 같습니다.

- 입력: `atlas-web/dist-local/local-20261007103011979-bf4218bb`
- 업로드 폴더: `atlas-web/dist-hosted/local-20261007103011979-bf4218bb/public`
- 대시보드용 ZIP: `atlas-web/dist-hosted/local-20261007103011979-bf4218bb/HUMAN-ATLAS-Pages.zip`
- 앱·모형 파일 99개 + `_headers`, `404.html` 2개 = 업로드 101개
- 내부 검증 manifest는 public 밖에 두었습니다. `.internal`, 개발 원장, work/evidence, 소스 저장소를 업로드하지 않습니다. 실제 필요한 learner projection/모형만 포함합니다.
- ZIP 101개 항목과 CRC 확인. public path allowlist, SHA/bytes, 해제 SHA, symlink 탈출, private URL 404, 변조 후 캐시 응답 차단을 검사했습니다.
- `npm run hosted:prepare`는 고정 local CURRENT의 SHA를 확인한 뒤 신규 전송 폴더를 만듭니다. `npm run hosted:preview`는 127.0.0.1:5194 QA 전용입니다.

현재 Cloudflare dashboard는 로그인 화면입니다. 배포 소유자가 직접 로그인/계정 생성 후 public ZIP만 Direct Upload하면 됩니다. 실제 배포 뒤에는 gzip header·최대 GLB 원본 SHA·대표 장면·private path 404를 외부 주소에서 다시 확인해야 합니다. 로컬 preview 결과를 Cloudflare 운영 결과로 대신하지 않았습니다.

## 입력 소유권과 보존

실제 전달물은 기존 WIP 19개 의존성을 포함하는 고정 작업 트리 snapshot입니다. Git HEAD 단독으로 같은 1,166행을 재현한다고 쓰지 않습니다. 이번 소유 코드만 커밋하고, 생성 runtime은 HEAD 입력을 임시 복제한 경로에서 새 serializer로 생성·freshness 확인한 223 selector/484행 버전만 커밋합니다. 현재 작업 트리의 267 selector/1,166행 생성 파일과 기존 WIP는 그대로 보존합니다. 이 두 수치를 구별합니다.

542 target / 563 membership / 12부위, source-only, public rights held, humanReview not_performed를 보존했습니다. OpenSim_Models, 원본 geometry, T13, 다른 task의 상태·EXECUTION은 변경하지 않았습니다. sync_execution.py는 --check만 수행해 쓰기를 발생시키지 않았습니다.

## 후속 순서

1. 배포용 Cloudflare 계정 연결 → 고정 public 폴더 업로드 → 실제 URL에서 header/모형/선택/복원 검증 → 사용자에게 주소 전달.
2. 실제 아이폰 Safari와 아이패드에서 터치·텍스트·메모리/로딩을 확인하고 관측된 결함만 수정.
3. 안정된 기준선에서 우선 근육의 작용을 하나씩 확대. 공통 가족/scene/player를 재사용하고 근육·뼈 문맥과 신경 링크를 함께 검증. 병리 편집기는 별도 범위 승인 후 진행.

공식 확인: [Cloudflare Direct Upload](https://developers.cloudflare.com/pages/get-started/direct-upload/), [파일 한도](https://developers.cloudflare.com/pages/platform/limits/), [정적 HTTP headers](https://developers.cloudflare.com/pages/configuration/headers/), [Vercel upload 한도](https://vercel.com/docs/limits).
