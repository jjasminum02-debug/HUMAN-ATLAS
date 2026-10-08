# 근육 표시 조정과 Cloudflare Pages 준비 검증

현재 지원 범위를 유지한 채 근육 색을 조금 밝히고, 보기 옵션에 직접 사용할 수 있는 **근육 숨기기**를 추가했다. 선택 집중/집중 관찰 모드와 개별 다시 표시 버튼은 제거했다. 외부 배포는 수행하지 않았다.

## 실제 변경

- 공통 근육 기본색 `#a34b4e → #aa5659`, 작용 강조색 `#bd5047 → #c15b53`: 흰색 방향으로 약 6% 수준의 작은 색 보정. 조명·roughness·texture·geometry·동작 범위는 변경하지 않았다. 선택/신경 강조색은 보존했다.
- 정확한 근육 source/측을 선택하고 보기 옵션의 **근육 숨기기**를 누르면 해당 표면을 숨긴다. 이미 숨긴 표면에는 비활성화하며 뼈/신경 선택에는 적용하지 않는다. 숨김은 안쪽 근육 선택, 검색, 신경 선택, 근육 layer 전환 및 시범 복원에서 유지한다. 기존 부위 카테고리/전신 홈 재선택의 초기화 정책은 유지했다. 새 되돌리기 버튼은 없다.
- 관찰 시점 메뉴에는 앞/뒤/왼쪽/오른쪽 방향 조작만 남겼다. `선택 맞춤`은 카메라 크기 맞춤, `선택 강조`는 선택 색 대비이며 조직을 집중 모드로 분리하는 기능이 아니다. 공통 카메라·attachment 관찰 API는 보존했다.
- 시범 상태 안내에서 제거된 ‘선택 다시 표시’ 버튼을 지시하던 문구를 고쳤다. MotionLearningPanel의 다른 작성자 WIP는 그대로 두고 이 문구 한 행만 소유 변경으로 분리했다.

## 실제 검증

변경 전 `before-home.png`와 변경 후 `after-home-1440.png`는 1440×900에서 기록했다. 최종 패키지에서 외복사근 숨김 → 내복사근 선택/선택 맞춤을 확인했다. 숨김 키가 유지되고 원본 외복사근이 visible 집합에서 제외됐으며, 안쪽 근육이 실제 보인다(`deep-selection-hidden-1440.png`). 한 측의 표면 숨김이며 반대측까지 자동으로 숨기지 않는다.

대퇴직근의 기존 무릎 폄 시범을 재생하고 재클릭 복귀 중 숨김을 확인했다. 동작을 취소하고 숨김을 유지하며, 숨긴 근육의 CTA/스크럽은 비활성화된다. 정중신경 선택에서도 기존 숨김이 보존되고 근육 숨기기 버튼은 비활성화됐다.

최종 패키지의 실제 viewport는 1440×900, 1024×900, 390×844. 직접 보기 버튼의 컨테이너 경계 이탈 및 문서 가로 overflow는 0건. 최초 경계 진단은 닫힌 방향 팝업의 레이아웃 박스도 집계했으므로, 최종 판정은 실제 직접 표시된 버튼/summary를 대상으로 했다. 대표 PNG와 `browser-validation.json`에 원자료를 남겼다. 콘솔 warn/error 0건. CSS 폭 검증이며 아이폰/아이패드 실기기 검증은 아니다.

관련 재질/표시/선택/숨김/취소 계약 21건, 호스팅 압축·무결성·404 회귀 4건, typecheck, production build, `sync_execution.py --check` 통과. 주 JS chunk 500kB 권고 경고는 남아 있고 예산은 상향하지 않았다. 원본/신규 GPU 시간·VRAM 측정은 하지 않았다. 추가 shader/texture/geometry는 없다.

## Cloudflare Pages 판정

공식 문서를 2026-10-08 확인했다. [Direct Upload](https://developers.cloudflare.com/pages/get-started/direct-upload/)는 사전 생성한 폴더를 Wrangler 또는 대시보드로 전달하며 `pages.dev` 주소를 제공한다. 앱 사용자의 로그인 화면이나 개인 노트북을 서버로 켜둘 필요가 없다. [Pages limits](https://developers.cloudflare.com/pages/platform/limits/)의 Free 20,000파일/개별 25MiB, Direct Upload 대시보드 1,000파일 기준에 현재 패키지가 들어간다. Vercel CLI 100MB를 Cloudflare 전체 패키지 한도로 적용하지 않았다.

최종 업로드 폴더: `atlas-web/dist-hosted/local-20261008051155604-bf4218bb/public/`

| 항목 | 실제 값 |
| --- | ---: |
| 런타임 파일 | 99 |
| `_headers`, `404.html` 포함 업로드 파일 | 101 |
| 업로드 bytes | 189,634,162 |
| 가장 큰 파일 | 17,220,355 bytes (16.42MiB) |
| 압축 해제 SHA가 원본과 일치한 GLB | 92/92 |
| decoded 런타임 bytes | 253,174,851 |
| 배포·Cloudflare 실서버 검증 | 미수행 |

`checkCloudflarePackage.mjs`를 추가해 실제 allowlist, symlink 차단, 파일 수·최대 크기, transport/decoded SHA, 6개 헤더 규칙의 경로 매칭, JSON/HTML 재검증 캐시, GLB 압축 헤더를 검사했다. [Headers 문서](https://developers.cloudflare.com/pages/configuration/headers/)의 wildcard 의미를 적용한 **오프라인 검사**이며 Cloudflare edge 구현을 실행한 검사가 아니다. 로컬 HTTP 브라우저 검증은 별도 gzip preview에서 수행했다.

이 패키지는 gzip GLB를 `_headers`의 Content-Encoding으로 전달한다. [Serving Pages](https://developers.cloudflare.com/pages/configuration/serving-pages/)는 자체 압축·캐시 동작도 설명하므로, 실제 배포 후에는 반드시 GLB 응답을 브라우저가 해제한 bytes/SHA로 대조해야 한다. ‘Cloudflare 실동작 합격’으로 기록하지 않았다. 헤더 누락/이중 압축이 있으면 성공 처리하지 않고, 기존 단계06 분리 frontend/identity asset-store 방식(Cloudflare R2 등의 저장소 연결)을 사용한다. 31.3MB 원본 GLB를 압축 해제해서 Pages에 그대로 올리는 것은 25MiB 제한을 넘는다.

업로드 방법·배포 후 확인·rollback은 `DEPLOY-CLOUDFLARE.md`에 있다. 가장 단순한 첫 전달 방식은 위 public 폴더의 Direct Upload이고, 기존 GLB/URL/loader를 보존한다. 실제 edge 확인은 후속 배포 범위다.

## 보존·입력 기준

최종 전달은 **보존된 작업 트리 snapshot**이며 commit-only 재현이라고 쓰지 않는다. private 입력은 public 폴더에 포함되지 않는다. 17개의 WIP runtime dependency는 snapshot 원장에 명시돼 있다. 이전 snapshot 대비 92개 GLB의 URL/decoded SHA가 전부 동일하므로 기존 해부학 geometry/track QC를 재사용했고 UI 변경을 새 패키지에서 검증했다. 전체 콘텐츠는 기존 partial이며 콘텐츠 수를 이번 변경의 합격 수로 확대하지 않았다.

542/563/12, HA130, 역사163, source-only·public rights held·humanReview=not_performed는 유지했다. EXECUTION/NEXT/근육 motion 원장/ZA integration 입력 SHA가 동일하다. task 상태를 다시 작성하지 않았다. OpenSim_Models/T13/원본/source-cache와 기존 WIP는 변경하거나 묶어서 stage하지 않았다. 공개 기술 준비는 권리 held를 공개 승인으로 승격하지 않는다.

증거: `baseline.json`, `cloudflare-package-audit.json`, `browser-validation.json`, `final-validation.json`, `build-validation.log`, `png-hashes.json`, `owned-motion-copy.patch`.
