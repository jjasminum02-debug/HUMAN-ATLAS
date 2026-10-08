# Cloudflare Pages 전달 절차

이번 결과는 로컬 준비·검증이다. 실제 계정 생성/로그인/업로드/배포는 하지 않았다. source 공개 권리 held 및 사람 검토 미실시 상태는 별개로 유지한다.

## 준비된 폴더

`/Users/daniel/Downloads/SIM /HUMAN ATLAS/atlas-web/dist-hosted/local-20261008051155604-bf4218bb/public`

위 **public 폴더 안의 내용만** 올린다. 상위 hosting-manifest/research/WIP/source-cache/원본/전체 repository를 올리지 않는다. `_headers`와 `404.html`은 함께 포함한다. 101개 파일/약189.63MB, 최대17.22MB이며 현재 Pages 파일 제한에 들어간다.

## 대시보드 방식

1. 호스팅 소유자가 Cloudflare에 로그인하고 Pages의 Direct Upload 프로젝트를 만든다.
2. 위 public 폴더를 선택해 업로드한다. 상위 프로젝트 전체 폴더를 선택하지 않는다.
3. 제공되는 `<프로젝트명>.pages.dev` 주소로 아래 실서버 검증을 수행한 뒤 공유한다. 앱 사용자는 별도 로그인을 하지 않으며 개인 노트북이 꺼져 있어도 Cloudflare가 제공한다.

[공식 Direct Upload 절차](https://developers.cloudflare.com/pages/get-started/direct-upload/)를 따른다. Direct Upload 프로젝트를 나중에 Git integration으로 바로 전환하는 방식은 지원되지 않아 필요하면 다른 프로젝트를 만든다.

## Wrangler 방식

Cloudflare 공식 CLI를 선택할 때 사용할 명령이다. 이번에는 실행하지 않았다.

```sh
npx wrangler login
npx wrangler pages project create
npx wrangler pages deploy '/Users/daniel/Downloads/SIM /HUMAN ATLAS/atlas-web/dist-hosted/local-20261008051155604-bf4218bb/public'
```

## 실제 배포 후 합격 조건

- 최초 홈/근육·뼈·신경 모형 및 무릎 폄 loop/rest가 로드되고 console/네트워크 오류가 없어야 한다.
- GLB의 Content-Type/Content-Encoding을 확인하고 **브라우저가 해제한 response bytes**의 SHA를 상위 `hosting-manifest.json`의 원본 `sha256`과 대조한다. 최소 가장 큰 `t66-priority-s04-flex/motion.glb`와 초기 anatomy 파일을 확인한다. 정상 HTTP header만으로 합격하지 않는다. 로컬 테스트는 Cloudflare edge 테스트의 대체가 아니다.
- HTML/JSON은 변경 시 재검증되고 `/assets/`의 hash 파일만 immutable이어야 한다.
- 누락 경로, `/work/EXECUTION.json`, `/_headers`가 private 내용을 반환하지 않아야 한다. root `404.html`이 SPA fallback으로 누락 자산을 HTML200으로 돌려주는 것을 막는다.
- 아이폰/iPad/Safari 실기기는 후속 실제 공유 URL에서 확인한다. 현재 390/1024 브라우저 폭을 실기기로 기록하지 않는다.
- gzip header 누락/중복 압축/decoded 불일치면 공개 링크 정상 완료로 판정하지 않는다. 원본31.3MB GLB를 그대로 Pages에 넣는 우회는 금지한다. 단계06의 frontend/identity static asset-store 분리 방식과 단일 asset transport config를 사용하면 R2 등 큰 파일 저장소로 이동할 수 있다. Functions를 GLB 프록시로 두지 않는다.

## 다시 준비·검사

저장소 루트에서 bundled Node가 PATH에 있는 상태로 실행한다.

```sh
node --experimental-strip-types atlas-web/scripts/prepareLocalDelivery.ts
node atlas-web/scripts/prepareHostedDelivery.mjs
node atlas-web/scripts/checkCloudflarePackage.mjs
node atlas-web/scripts/previewHostedDelivery.mjs --port 5201
```

새 snapshot을 준비하면 CURRENT가 새 폴더를 가리킨다. 기존 폴더는 덮지 않는다. 다시 업로드할 때는 새 snapshot의 public 폴더만 선택한다. rollback은 검증된 이전 Cloudflare deployment로 되돌리고, 로컬의 이전 snapshot/manifest도 보존한다. 앱 업데이트 후 새 HTML/JSON과 자산 조합을 확인한다.
