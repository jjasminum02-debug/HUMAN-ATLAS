# Vercel Hobby 크기 적합성 검토

2026-10-07 실제 전달 snapshot `local-20261007115536386-bf4218bb`를 검사했다. MB는10진수1,000,000 bytes다. 구성품 SHA가 같은 완전 중복 그룹은0이다. GLB 내부 geometry 중복까지0이라는 뜻은 아니다.

| 항목 | 파일 수 | decoded/raw MB | 현재 gzip 전달 MB |
|---|---:|---:|---:|
| 앱 JS/CSS/HTML | 5 | 3.30 | 3.30 |
| compact projection | 2 | 3.22 | 3.22 |
| 정상 모형 | 18 | 94.16 | 77.29 |
| 동작 | 74 | 152.48 | 105.81 |
| runtime 합계 | 99 | 253.16 | 189.61 |

_headers/404를 포함한 실제 upload directory는101파일,189,615,168 bytes다. 99파일의 전달 byte 합은189,614,583이다. 가장 큰 raw GLB는31.31MB, 압축 후 최대 단일 파일은17.22MB다. 현재 hosted package는 Cloudflare Pages용이다. _headers는 Vercel 설정으로 자동 적용되지 않는다.

## 결론

Vercel Hobby의 CLI source upload100MB 한도에는 현재 패키지가 들어가지 않는다. 이것은 CLI 업로드 규정이지 모든 빌드 output/저장 크기가100MB로 제한된다는 주장이 아니다. 단일100MB로 축소하려면 현재 압축 상태에서 약47.3%, 여유를 둔90MB 목표에는 약52.5%를 더 줄여야 한다. 실제 압축 실험 없이 무손실·동작 품질 보존으로 달성 가능하다고 확정하지 않는다. [Vercel 공식 limits](https://vercel.com/docs/limits)

JS는 약3.3MB라 JS만 줄이는 해법은 충분하지 않다. 전체 file hash 중복은 없으며 region lazy loading은 사용자가 처음 받는 전송량을 줄이지만 총 upload package 크기를 줄이지 않는다. 일반 gzip은 이미 적용되어 있다. motion 내부의 base/morph/keys/buffers 공유와 지원 parser에서 가능한 무손실 압축을 먼저 조사할 가치가 있다. meshopt/Draco는 현행 raw accessor 파서에도 지원을 구현해야 한다. 감축률은 미측정이다.

Vercel을 사용하려면 frontend/compact projection 약6.52MB를 배포하고 모형·동작을 별도 static storage에서 직접 읽는 구성이 가능하다. 같은 서비스의 Vercel Blob Hobby 포함량은 저장1GB/month, Blob 전송10GB이므로 현재 모형 규모는 저장량에 들어갈 수 있지만 트래픽이 먼저 문제가 될 수 있다. 모든 압축 자산189.61MB를 cache miss로 받는 극단적 예에서는10GB가 약52회분이다. 실제 세션은 지역/작용 lazy load와 캐시 사용량으로 계산해야 하며52명 사용자 한도라는 뜻은 아니다. Blob 무료 포함량을 넘으면 접근 제한이 생길 수 있다. [Vercel Blob 공식 가격·사용량](https://vercel.com/docs/vercel-blob/usage-and-pricing)

Vercel Hobby는 개인·비상업 용도이며 frontend Fast Data Transfer100GB, Fast Origin Transfer10GB 포함량도 구분해야 한다. 저장량이 적합하다고 실제 사용량/용도가 모두 적합한 것은 아니다. [Vercel Hobby 공식 안내](https://vercel.com/docs/plans/hobby)

한 URL, 로그인 UI 없음, 노트북이 꺼져 있어도 사용이라는 목표에는 기존 Cloudflare Pages static package가 구조상 더 간단하다. 현재101파일/최대17.22MB는 Free의20,000파일/개별25MiB 규정에 들어간다. 이는 실제 업로드·브라우저 동작/권리 확인이 끝났다는 뜻은 아니다. [Cloudflare Pages 공식 제한](https://developers.cloudflare.com/pages/platform/limits/)

권고: UI/그래픽을1–5단계로 완성하고6에서 불필요한 바이트·초기 전송을 개선한다.100MB를 맞추기 위해 해부학적 표면과 현재 작용을 삭제하지 않는다. 단일 Hobby CLI 업로드에 고집하지 않으면 기능과 품질을 유지한 공유가 가능하다. Vercel을 선호하면 frontend+storage, 단순성을 우선하면 기존 Pages package를 준비한다. 실제 외부 배포는 이번 계획에 포함하지 않는다. 앱 사용자 로그인창은 필요 없고 운영자 호스팅 계정 인증은 별개다.

source-only/public held/humanReview not_performed와 현재 WIP 기반 snapshot의 의존성을 보존한다. 기술적 적합성은 source 공개 권리 승인이 아니다.
