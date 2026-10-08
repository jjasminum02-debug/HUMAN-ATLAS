# Stage06 재현·전달 운영

이번 결과는 로컬 준비다. 업로드, 계정 연결, 외부 배포, 유료 변경은 수행하지 않았다. 사용자 로그인 UI는 없다.

## 고정 입력과 결과

기준은 HEAD `c45bff1a4fdd7ed42ba39bab4444bbcb625dc9e2` 및 보존된 작업 트리다. commit만 checkout해서 같은 콘텐츠가 생성된다고 주장하지 않는다. `delivery-dependencies.json`의 21개 작업 트리 의존성은 파일·bytes·SHA·소유 구분을 포함한다. 다른 사람 WIP는 이번 커밋에 넣지 않는다.

고정 snapshot: `atlas-web/dist-local/local-20261008042105500-bf4218bb/`
`snapshot.json` SHA: `3637bd69e0540d3b86ee5f363d68669bdd0986746d0743809637577534869e95`.
이 snapshot은 실제 실행에 필요한 모형/compact projection을 복사하므로 repo dev middleware 없이 실행한다. `.internal/`과 snapshot metadata는 공개 업로드에 포함하지 않는다.

## 현재 결과 재검사 / 재시작

프로젝트 루트에서 실행한다. 시스템 Node 대신 번들 Node 경로를 사용했다.

```sh
PATH=/Users/daniel/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin:$PATH node atlas-web/scripts/prepareVercelDelivery.mjs --check atlas-web/dist-vercel/local-20261008042105500-bf4218bb-loopback
PATH=/Users/daniel/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin:$PATH node atlas-web/scripts/previewVercelDelivery.mjs atlas-web/dist-vercel/local-20261008042105500-bf4218bb-loopback 5196 5197
```

5196은 frontend, 5197은 static asset emulator다. 둘 다 loopback에만 bind한다. 검사 전 자산 원본이나 snapshot을 변경하지 않는다. Ctrl-C로 종료하며 다시 실행하면 같은 snapshot을 제공한다. `5196`을 외부 공개 URL로 안내하지 않는다.

현재 Cloudflare 정적 결과:
`atlas-web/dist-hosted/local-20261008042105500-bf4218bb/public/`

```sh
PATH=/Users/daniel/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin:$PATH node atlas-web/scripts/previewHostedDelivery.mjs --port 5198
```

이 명령은 CURRENT 포인터와 같은 revision을 읽는다. 다른 CURRENT로 이동했다면 먼저 해당 새 revision을 준비한다.

## 새 입력으로 재생성

기존 결과 폴더를 덮지 않는다. `local:prepare`는 generated learner runtime/전달 색인 freshness 및 dependency SHA를 확인한 실제 새 snapshot을 만든다. 원장이 바뀌었다면 기존 단일 generated writer로 projection과 전달 색인을 갱신하고 확인한다. 두 번째 원장 파서나 viewer를 추가하지 않는다.

```sh
PATH=/Users/daniel/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin:$PATH npm --prefix atlas-web run local:prepare
PATH=/Users/daniel/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin:$PATH npm --prefix atlas-web run vercel:prepare -- --asset-origin http://127.0.0.1:5197 --output atlas-web/dist-vercel/NEW-REVISION-loopback
PATH=/Users/daniel/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin:$PATH npm --prefix atlas-web run hosted:prepare
```

`NEW-REVISION-loopback`은 기존에 없는 폴더로 바꾼다. `hosted:prepare`는 snapshot ID별 새 폴더를 쓰므로 같은 ID에 다시 실행하면 덮기 대신 중단한다. 단순 파일 timestamp 변화나 새 frontend hash로 동일 GLB의 anatomy QA를 폐기하지 않는다.

## 권고 전달 구조: Cloudflare Pages 단일 정적 사이트

공개 후속 요청이 있을 때 **검사된 `public/` 하나만** 배포 대상으로 사용한다. repo 전체/`dist-local`/조사 자료는 대상이 아니다. `public/_headers`를 함께 전달해야 `.glb`의 gzip bytes에 `Content-Encoding: gzip`이 적용된다. 브라우저는 원래 bytes로 해제하고 기존 source SHA 검사·raw accessor parser·GLTFLoader를 사용한다. 이름이 고정된 GLB는 재검증 캐시를 쓰고 immutable을 붙이지 않는다. HTML과 compact projection은 새 revision을 다시 읽도록 한다.

준비된 101개 파일의 최대 encoded asset은 17,220,355 bytes로 [Pages 25 MiB/file 및 Free 20,000개 파일 한도](https://developers.cloudflare.com/pages/platform/limits)에 들어간다. 노트북을 켜 둘 필요 없는 구조이며 최종 URL은 실제 별도 배포가 있어야 생긴다.

## 대안: Vercel Hobby frontend + public Blob

현재 HTTPS template:
`atlas-web/dist-vercel/local-20261008042105500-bf4218bb-template/`
`https://assets.example.invalid`는 placeholder다. 실제 Blob store URL을 입력해 새 revision을 준비해야 한다.

- frontend upload directory는 **`frontend/`만**: 약 6.56 MB. `.vercelignore`, `vercel.json`, `public/` 포함. Other / framework null / output public / build·install command 없음. `_headers`를 Vercel 설정으로 오인하지 않는다.
- `assets-store/`는 Vercel CLI frontend upload에 포함하지 않는다. 92개 원래 GLB bytes, 총 246,636,632 bytes다. `public-allowlist.json`으로 SHA를 확인한다.
- 후속으로 계정과 공개 가능한 자산 범위가 정해지면 Blob SDK `put`의 `access: 'public'`, `addRandomSuffix: false`, `allowOverwrite: false`, `contentType: 'model/gltf-binary'`, `cacheControlMaxAge: 31536000`으로 **SHA.glb**를 저장한다. 이는 실행한 업로드가 아니라 명시적인 인계다. secret은 frontend에 넣지 않는다.
- [SDK의 documented options](https://vercel.com/docs/vercel-blob/using-blob-sdk)에 임의 Content-Encoding 설정을 가정하지 않는다. Blob 안에는 gzip 대신 identity GLB를 넣는다. Function으로 파일을 매번 프록시하지 않는다.
- 반환된 실제 public store origin을 한 곳에 공급한다. SDK random suffix 또는 URL 경로가 계획과 다르면 명시적 색인 계약을 고쳐 검증하며 임의 URL 추측으로 등록하지 않는다.

```sh
PATH=/Users/daniel/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin:$PATH npm --prefix atlas-web run vercel:prepare -- --asset-origin https://ACTUAL-STORE.public.blob.vercel-storage.com --output atlas-web/dist-vercel/NEW-REVISION-public
```

이 명령 자체는 로컬 파일만 생성한다. origin은 실제 확인한 store로 바꾼다. 새 파일의 CORS·Content-Type·ETag/Cache-Control·404·실제 SHA를 외부 배포 후 검사하고, 해당 provider에서 390/1024/1440 실제 UI를 확인해야 Vercel 실동작 합격이다. 로컬 emulator의 CORS 성공으로 실제 Blob CORS 성공을 주장하지 않는다.

## 캐시·복구·rollback

SHA URL은 내용 불변일 때만 immutable이다. 자산 내용이 변하면 SHA와 config script hash, HTML 참조를 함께 바꾼다. 기존 SHA를 overwrite하지 않는다. HTML/projection은 revalidate이며 새 HTML이 새 map을 읽는다. 실패 응답은 cache하지 않고 같은 CTA의 재시도를 유지한다. 해시/크기 검사는 캐시 응답으로 우회하지 않는다.

Rollback은 **이전 frontend revision + 그 revision이 참조하는 자산**을 함께 복원한다. 이전 자산을 retained revision이 사용하는 동안 제거하지 않는다. prepared package 검사 실패면 source snapshot SHA부터 확인하고 새 폴더로 재생성한다. 자동으로 held 정책이나 hash를 완화하지 않는다.

## 외부 배포 전에 필요한 실제 입력

계정/프로젝트와 실제 asset origin은 이번 독립 로컬 준비의 blocker가 아니다. 공개 권리는 별도다. `atlas-data/overlays/za-local-integration.json`, dataset registry 및 고정 snapshot authority의 `publicRedistribution=held`는 이번에 바꾸지 않았다. 이 결과를 포괄 공개 승인으로 사용하지 않는다. 공개 대상 source와 예외를 정한 후 구체적 패키지에 대한 사용자 후속 요청으로 배포한다. Hobby는 [개인 비상업 용도](https://vercel.com/docs/plans/hobby)라는 조건도 실제 사용 목적과 대조한다.
