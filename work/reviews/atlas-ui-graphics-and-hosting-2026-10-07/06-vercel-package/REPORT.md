# Stage06 — 경량 전달 / Hobby 로컬 준비 완료

현재 지원 범위를 보존하는 정적 패키지 두 가지를 실제 생성·검증했다. **이번 stage의 로컬 준비는 passed이며 외부 배포는 수행하지 않았다.** T40/T66/T85 상태, NEXT, EXECUTION 및 product acceptance는 수정하지 않았다. 공개 URL/Vercel 실동작 합격/공개 권리 승인을 만들지 않았다.

권고안은 기존 **Cloudflare Pages 단일 정적 사이트**다. 동일한 사이트에서 gzip GLB를 전달하므로 가장 적은 설정·의존성이 필요하고 노트북을 꺼도 서비스할 수 있는 구조다. Vercel을 선호할 경우 **Hobby frontend + public Blob identity GLB** 분리 패키지가 준비되어 있다. 실제 계정·store origin·공개 source 범위 지정은 후속 배포 입력이며 로컬 준비의 실패가 아니다.

## 실제 최신 입력

HEAD `c45bff1a4fdd7ed42ba39bab4444bbcb625dc9e2`와 보존된 WIP에서 `local-20261008042105500-bf4218bb`를 생성했다. snapshot SHA는 `3637bd69e0540d3b86ee5f363d68669bdd0986746d0743809637577534869e95`다. `delivery-dependencies.json`에 작업 트리 의존성 21개를 파일·bytes·SHA·기존 소유 구분과 함께 기록했다. 이번 커밋만으로 기존 콘텐츠 WIP까지 재현된다고 주장하지 않는다. snapshot에는 실제 필요한 고정 파일이 복사되어 dev middleware 없이 실행된다.

기존 `baseline.json` / `compression-experiment.json`은 stage04 시점의 역사 입력이다. 최신 판정은 `resume-baseline.json`, 최종 snapshot과 아래 근거를 따른다. stage01–05 report를 확인하고 동일 GLB/원장 해시의 QA를 영향 분석 후 재사용했다.

## 전달 크기와 Hobby 판정

모든 크기는 decimal bytes/MB다. CLI source 업로드, deployment storage, Blob 저장/전송, 브라우저 초기 장면 비용을 분리했다.

| 항목 | 실제 크기 | 판정 |
|---|---:|---|
| 원래 runtime closure 99개 | 253,175,275 bytes | 단일 CLI 100 MB / engineering 90 MB 목표 초과 |
| motion GLB | 152,478,360 bytes | 유지 |
| anatomy GLB | 94,158,272 bytes | 유지 |
| 앱 JS/CSS/HTML | 3,322,365 bytes | 전체 모형 크기와 별개 |
| compact projection 2개 | 3,216,278 bytes | 유지 |
| 전체 파일 gzip6 실험 | 184,047,979 bytes | 90 MB 미달성; 모든 파일 gzip 가정의 실험값 |
| 전체 파일 Brotli6 실험 | 161,042,853 bytes | 90 MB 미달성; 등록하지 않음 |
| 실제 Cloudflare gzip 패키지 | 189,634,001 bytes + 작은 `_headers`/404 | GLB만 gzip, 나머지 원래 bytes |
| Vercel HTTPS template frontend/config | 6,557,117 bytes | 90 MB 목표 통과 |
| remote identity GLB 92개 | 246,636,632 bytes | Blob 저장 포함량 안에 들어감 |

Vercel의 [Hobby CLI source 업로드 100 MB](https://vercel.com/docs/limits)는 모든 저장 경로의 총 한도가 아니다. [2026-09-16 공식 변경](https://vercel.com/changelog/hobby-projects-now-retain-fewer-deployments-to-free-up-storage)의 Hobby deployment storage 10 GB와도 별개다. 이번 실제 패키지는 단일 CLI 업로드로 통과시키지 않았으며, Git 연동 등 다른 업로드 경로의 배포 성공도 주장하지 않는다.

[Blob Hobby 포함량](https://vercel.com/docs/vercel-blob/usage-and-pricing)은 저장 평균 1 GB-month / 전송 10 GB / simple 10,000 / advanced 2,000 operations다. 모델 전부를 매번 246.64 MB 내려받는 보수적 계산은 약 40회다. 이는 **사용자 수가 아니며**, 실제 lazy loading·캐시·사용 장면에 따라 달라지고 프런트엔드 전송도 별도다. 가격은 store region별 공식 표를 사용하며, 유료 업그레이드를 실행하거나 특정 지역 가격을 글로벌 가격으로 적지 않았다. [Hobby 개인 비상업 조건](https://vercel.com/docs/plans/hobby)도 별도 운영 조건이다.

Cloudflare는 [25 MiB/file / Free 20,000 files](https://developers.cloudflare.com/pages/platform/limits) 기준으로 prepared public 101개, 최대 encoded GLB 17,220,355 bytes가 들어간다. 현재 단계에서는 실제 Cloudflare 배포도 하지 않았다.

## 실제 구현

`assetTransport.ts` 하나로 기존 loader의 논리 URI를 immutable HTTPS SHA URL에 연결한다. DatasetResources, 기존 manifest loader, AnatomySceneController, MotionLearningPanel의 원래 fetch 경로에서 사용한다. raw accessor parser·GLTFLoader·generated learner runtime·source/side/part/hash/bytes 계약은 그대로다. query/hash/다른 origin의 URL을 조용히 바꾸지 않고 native AbortSignal과 기존 generation/late-response ownership을 유지한다. 새 viewer, 원장 파서, Function proxy, 중복 캐시를 만들지 않았다.

`prepareVercelDelivery`는 frozen allowlist에서 앱/projection과 92개 GLB를 나눈다. GLB는 original SHA 파일명으로 byte-identical 복사한다. frontend에 `_headers` 대신 `vercel.json`, `.vercelignore`, 별도 404를 만든다. 알려지지 않은 경로에 HTML을 200으로 돌려주지 않는다. HTML/projection은 revalidate, hash가 바뀌는 앱/config 파일과 SHA GLB만 immutable이다. config script는 앱 실행 전에 준비된다. 새 revision은 HTML/config hash를 바꾸고 동일 GLB의 SHA URI는 유지한다.

[Blob SDK 문서](https://vercel.com/docs/vercel-blob/using-blob-sdk)의 contentType/cacheControlMaxAge 등 옵션을 따르는 identity GLB 전달안을 작성했다. 문서에 없는 custom Content-Encoding 지원을 가정하지 않았다. gzip bytes를 encoding 없이 `.glb`로 전달하지 않는다. Cloudflare gzip 경로는 해당 `_headers`를 포함하고 브라우저의 자동 해제 후 원래 SHA를 확인한다.

최소 업로드 디렉터리는 `frontend/` 또는 Cloudflare `public/` 하나다. work/evidence/source-cache/OpenSim_Models/node_modules/과거 dist/미등록 후보/비공개 snapshot metadata는 포함하지 않는다. `public-allowlist.json`은 공개 대상 후보 색인이며 **held 자산의 공개 승인 명단이 아니다**.

로컬 preview는 두 loopback origin에서 Content-Type/identity/CORS/ETag/immutable/404/실패/retry를 검사한다. SHA·bytes 확인 후에만 304를 반환한다. 실제 Blob origin의 CORS·headers는 외부 배포 후 확인할 항목으로 남긴다. localhost가 클라우드 필수 경로로 남지 않도록 실제 origin을 단일 config 입력으로 공급한다.

## 제한된 압축 실험과 선택

완전히 동일한 whole-file SHA 중복은 0이다. 가장 큰 실제 GLB에서 exact bufferView payload 공유를 한 번 시험했다. 원래 31,306,820 → 28,431,756 bytes, gzip6 17,220,355 → 15,128,482 bytes였다. bufferView bytes와 accessor/node/material/animation 등 비버퍼 metadata는 동일했다. Node 실험 CPU 약 808 ms이며 브라우저 decode 측정이 아니다. 실제 등록/교체는 하지 않았다.

전체 목표 달성 가능성이 확인되지 않아 geometry/track revision을 일괄 바꾸지 않고 split fallback으로 완료했다. 반복 배열 공유는 전체 파일 중복 제거와 다른 문제다. Sparse morph는 zero 값 저장을 줄일 수 있지만 raw parser/검증·추가 decode가 필요하고, meshopt/Draco는 GLTFLoader와 raw accessor parser 양쪽 decoder가 필요하다. gzip/Brotli는 전송량을 줄여도 decoded CPU geometry/메모리를 줄이지 않는다. 양자화/decimation/가짜 부착/색·scale 대체는 적용하지 않았다. 이번 파이프라인에는 검증된 gzip 경로와 identity 분리 경로만 등록되어 있다.

## 자동·실제 브라우저 검증

- transport/local/hosted/package/cache revision 회귀 **20/20**, 기존 scene/player/loader ownership 회귀 **35/35** 통과.
- typecheck, production build, compiled learner metadata leakage 검사 통과. JS chunk 500 kB 권고 경고는 남겨 두었으며 예산을 올리지 않았다.
- 최종 snapshot allowlist 99개 전부와 remote GLB **92개 exact bytes** 대조. source identity/side/part/frame/track/material 및 원래 key/중간 interpolation/contact/outcome/rest 입력은 동일하다. geometry 변경이 없어 emitted GLB 전수 QC를 반복하지 않았다.
- actual viewport **1440×900 / 1024×900 / 390×844**, 단일 canvas, horizontal overflow 없음. PNG 20장과 DOM/geometry/측정 원장을 남겼다. PNG는 브라우저가 반환한 JPEG를 해상도 변경 없이 변환한 것이며 기기 실측이 아니다.
- split: 홈 → 앞정강근 action → scrub held → 재클릭 rest → 반복 → 근육 layer-off; 정중신경 → 확인된 손 근육 action → 신경 rest 복원; 390 대퇴직근 무릎 폄 및 정강뼈 직접 무릎 굽힘 확인.
- derived preview의 무릎 GLB를 일시 제외해 실제 실패 UI를 확인하고 같은 bytes를 복원한 뒤 같은 CTA로 재시도 성공. original asset은 바꾸지 않았다. 의도된 실패까지 콘솔 검사에서 실제 오류 회귀로 오인하지 않았고, 최종 split/Cloudflare error·warn 기록은 빈 배열이다.
- 20회 지역 전환 후 동일 scene root, queue pending/failed 0, 12 cache entries / 71,317,368 dataset bytes. 관측 cancellations/late releases 모두 0이며 race를 실제 유발했다고 주장하지 않는다. cancellation/late release 안전성은 해당 자동 ownership 회귀로 재사용했다. 12부위 전체 scope/동작 의미는 동일 입력의 stage05 QA를 재사용하고 이번 전환 검사는 별도다.
- Cloudflare 전달 경로도 실제 3폭 홈/앞정강근 재생/rest/반투명/scrub을 확인해 gzip 자동 해제와 기존 loader 동작을 검증했다. 공개 config의 profiler는 비활성이다. GPU/VRAM/total-process 메모리·실기기/실제 인터넷 지연은 관측하지 못했다.

| split 로컬 측정 | 값 | 의미 |
|---|---:|---|
| cold 홈 GLB body / transfer | 9,051,664 / 9,052,564 bytes | initial 모델 3개; HTML/JS 총 전송과 별개 |
| warm reload 같은 GLB transfer | 0 bytes | native 브라우저 캐시; 여전히 decode/geometry 준비 필요 |
| 첫 앞정강근 시범 asset | 1,091,388 bytes | 근육 선택의 추가 anatomy chunk 전송과 별개 |
| 첫 시범 fetch/read · parse/validate · attach | 13.7 · 5.9 · 9.5 ms | 총 약 29.1 ms, 로컬 CPU/IO |
| 반복 시범 총 연결 / asset transfer | 약 20 ms / 0 bytes | player 해제 후 재parse/attach; HTTP 캐시가 decode cache라는 뜻은 아님 |
| cold 홈 render CPU P50 / P95 | 1.4 / 3.0 ms | GPU 시간이 아님 |
| cold 홈 frame interval P50 / P95 | 16.7 / 17.5 ms | render 호출 시간과 별개 |
| cold 홈 draws / triangles / CPU geometry buffer | 672 / 486,184 / 6,825,150 bytes | 실제 renderer 관측, process/VRAM 메모리 아님 |

기하를 유지하면서 delivery 계층만 바꾸었다. 기존 stage05와 원래 의미가 같으므로 이번 stage로 FPS 향상이나 새 애니메이션 지원을 만들어 냈다고 쓰지 않는다. cold/warm 차이는 캐시 조건 차이이며 동일 조건 전후 성능 개선율이 아니다.

## 제품·콘텐츠·권한

stage05와 같은 generated runtime SHA 및 신경 관계 원장을 유지했다. 195 nerve surfaces / 98 display groups / 18 motor relations(2 exact geometry / 16 concept), 6 branch edges, 실제 exact source-action 56 pairs / 38 surfaces / 39 고유 GLB를 보존했다. 7우선 근육군은 20표면 / 22 pairs다. 작업 트리의 1,166 options를 실제 작용 수나 전신 완성으로 세지 않는다.

`acceptanceScope=stage06_current_supported_delivery_package`, `productReadiness=local_hosting_preparation_ready`, `contentCompleteness=partial`, stage-local `unresolvedProductBlockers=[]`다. 전체 미제작 motion, 신경 동적 pose/정확 지배 geometry, 미확보 부착 영역/용어/형상은 기존 콘텐츠·engineering backlog이며 이번 업로드 closure에서 지원된 구조를 조용히 제거하지 않았다. 분모 542/563/12, HA130/역사163 및 source-only/local selection/public rights held/humanReview not_performed를 보존했다.

공개 권리는 아직 held이며 provider 실동작/계정/실제 store origin은 별도 후속 입력이다. 전신 해부학 완료, 정상모형 전체 완료, 임상 승인, 공개 배포 준비 승인과 이번 기술적 로컬 준비를 구분한다.

재현·rollback·cache 갱신·향후 구체적 배포 입력은 `OPERATIONS.md`에 있다. 다른 stage/task 자동 실행은 없다.
