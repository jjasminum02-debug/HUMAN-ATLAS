# T66 wave 1 통합 writer 보고서

## 판정

wave 1의 통과 후보와 F 텍스트 delta를 단일 scene/runtime 경로에 연결했고 wave 2 D/E의 고정 manifest·snapshot·preflight를 검증했다. 실패 후보는 등록하지 않았다. 이 결과는 T66 완료가 아니다. 부모 상태는 `in_progress / partial`, nextUnit은 `author-and-integrate-normal-motion-bone-and-nerve`로 유지한다.

## 시작 기준선과 소유 경계

- 시작 HEAD: `754afdc8e89803977c8131d05dd4544aec61e964`.
- wave 1 run: `T66-W1-20261003-5dadff8d782b`, raw manifest SHA-256 `7d12000c2a049d1c2bf09f8349159609a6dd7b5f93f1d0710742ede84aacad95`.
- 기준 dirty snapshot은 `start-baseline.json`에 남겼다. A/B/C/F outputRoot 밖의 worker 작성물은 수정하지 않았다. common runtime, wave 1 registration, UI adapter/asset plugin, wave 2 runner/snapshot correction은 통합 writer 소유 변경이다.
- 원본, source-cache, `OpenSim_Models/`, T13 drafts, 기존 worker outputs와 역사 report/evidence는 그대로 보존했다.

## 통합 수치

- 고정 분모 유지: 542 target, 563 membership, 12 region; 근육 429/447; 232 source concepts/462 surfaces; HA130, 과거 분류 6/20/135/2.
- wave 1 runtime bundle: 32 package template, selector relation 754 (muscle action 38 / bone role 716), unique GLB URI 28, unique GLB SHA-256 28, total bytes 35,892,956. 각 GLB의 파일 hash와 길이를 `integration-summary.json`에 저장했다.
- A: 34 action selectors, 26 unique accepted GLBs (34,923,888 B), 702 bone selector relations. 추가 92 engineering-blocked source/action rows, 56 blocked families와 54 missing source/relation rows는 별도 유지.
- B: 신규 후보 29 GLB 전부 geometry/contact blocked, 등록 0. 152 source/action rows 및 222 target-side-action extent rows를 asset 수로 세지 않는다.
- C: 4 후보 중 lumbar multifidus 제한 신전 및 longus colli 제한 하부경추 굽힘 관찰 2 GLB만 통과(969,068 B); 호흡 후보 2는 blocked, 미등록. 근육 selector 4와 bone role selector 14는 relation 수이며 concept/asset 수가 아니다. C의 157 미확정 work key는 그대로 유지.
- F: native nerve row 98 전수; 문헌 텍스트 30 work key 검증, 68 key는 source/relation 미확보. learner receipt 7개 field 검토, 실제 text hash 변경 1개. 독립 nerve 개념 분모는 null, 동적 nerve geometry/포착 좌표/새 nerve GLB는 0.
- authority: `sourceOnly=true`, 공개 재배포 `held`, `humanReview=not_performed`, canonical target/membership 승인 false, 새 HA canonical ID 0.

## 제품/runtime 연결

`atlas-web/src/data/learning.ts`는 선택된 정확 sourceKey와 side로 wave 1 selector를 공통 learner motion projection에 연결한다. 기존 단일 scene, renderer, camera, player, frame clock를 유지했다. `atlas-web/plugins/motionAssets.ts`는 기존 asset manifest와 wave 1 registration을 합쳐 URI/hash 충돌을 거절하고 파일 SHA·상한·경로 containment를 확인해 lazy serve 및 build 산출한다. 별도 viewer는 없다. Vite build 산출물에서 A/C 28개의 unique GLB가 실제 포함됨을 확인했다.

F nerve fields는 기존 `nerve-learning-t66.json`의 공통 learner card projection을 사용한다. 문헌 주행·압박 맥락과 정적 native nerve geometry, 변이/좌우/신경지배 범위는 분리했다. 표시되는 좌우 근육 surface 목록은 side-specific branch evidence가 아니며, 문헌 위치를 모델 좌표로 바꾸지 않았다.

## 실제 브라우저

Chrome/CUA 1280×720에서 네 유형을 검사했다: 오른쪽 짧은엄지벌림근 action 시범, 왼쪽 긴목근 partial posture observation, 긴목근 candidate의 fixed C1 bone role direct route, 왼쪽 등쪽어깨신경 static route와 expanded course/compression/variation card. exact route·선택 측·세 이름·action scope·CTA slider/rest 또는 정적 nerve warning을 대조했다. 긴목근의 선택만 보기는 teal source surface를 국소적으로 표시했다. 화면 표본은 전체 selector의 시각 인증이 아니다. 실제 UI 값과 제한은 `browser-verification.json`에 남겼고 원래 사용자 route를 복구했다. PNG는 저장하지 않았고 browser console API도 CUA에서 읽을 수 없어 그 한계를 기록했다.

## 검증

- wave 1 domain projection, emitted GLB replay, common integrity route: 3/3 pass.
- wave-1 only learner test filter: pass.
- TypeScript `tsc -b --pretty false`: pass.
- Vite production build: pass. 앱 JS chunk 500 kB 초과 경고 있음.
- full `learning.test.ts` 실행은 현재 시작 기준선에 이미 존재하던 generated runtime과 오래된 exact-count expectation 불일치로 2 failures: actual 1,145 vs expected 281; actual verified asset rows 1,138 vs expected 274. 시작 시 hash가 같은 `learnerMotionRuntime.generated.ts`는 이번 writer가 수정하지 않았다. 이 통합으로 발생한 wave 1 전용 실패는 아니며, stale count assertion을 이 task에서 바꾸지 않았다.
- wave2 freeze/preflight validator: corrected r2 manifest 및 D/E preflight 통과.

## Wave 2 고정·수정 기록

최초 wave2 D preflight는 `validate_schema_instance` import 누락으로 실패했다. worker 시작이나 D/E authoring은 없었다. 최초 raw manifest `T66-W2-20261004-9f5926a80312` SHA `7642942ada7718b9673c757939d17a00e18a092cbd56513859235822c9065a70` 및 기존 snapshot을 보존했다. writer runner import를 수정하고 corrected snapshot/manifest r2를 생성했다. 수정 run `T66-W2-20261004-r2-5735b81b7626` SHA `d6ad4413da2beb44508715f1e48b8389c29071d2cad28fb28c2254a3f0c1a600`; D 16 work/source keys, 1 bone context; E 66 work/source keys, 16 bone context; 60개 deferred. 두 `--preflight-only` 실행은 authoring 없이 통과, probe는 제거, A/B/C/F는 read-only carry-forward. 상세는 `../wave-2/prelaunch-correction-r2.json`, `../wave-2/run-manifest.json`, `wave2-freeze-validation.json`에 있다. D/E는 자동 시작하지 않는다.

## 남은 제한

B 후보 29개와 C 호흡 2개의 source-relative geometry/contact 결함, A 미완 작용/관계 행, F 미확정 68 nerve text work keys, 754 relation 전체의 개별 visual QA, 전체 motion family 제작 및 기존 T66-B3는 해결되지 않았다. 실제 제품 blocker를 자료 gap으로 바꾸거나 통과한 부분의 범위를 전신/target 전체로 확장하지 않는다. 따라서 T66 partial을 유지한다.

다음 수동 입력 파일은 `work/plans/t66-parallel-completion-2026-10-03/07-worker-D-jaw-hyoid-pharynx.txt`와 `08-worker-E-eye-face-tongue-pelvic.txt`이며 이 실행에서는 시작하지 않았다.

## 집계 정합 보충

- 통합 writer 시작 HEAD는 `start-baseline.json`의 `754afdc8e89803977c8131d05dd4544aec61e964`다. wave-1 manifest와 worker handoff의 `baselineHead=ae993a8a455632d738b2141f50ad09789bf5ee7c`는 manifest가 명시한 메타데이터 기준선이다. 두 값을 분리해 기록했고, 고정 snapshot/input hash를 freshness 근거로 사용했다.
- 최초 summary의 A 배정 비교는 42개 scope-disposition key와 파생 action child key를 같은 집합으로 비교한 오류였다. handoff의 `assignedWorkKeyCoverage.allMatch`와 `sourceActionCoverage.allMatch`가 모두 true이며 A/B/C/F 전체의 정확 배정 확인도 true다. 정정 내용은 `integration-summary.json`과 `worker-reconciliation.json`에 남겼다.
- 등록 manifest에서 재계산한 wave-1 추가치는 package template 32, 근육 action relation 38행/고유 source key 22개, bone role relation 716행/고유 bone source instance 68개, 고유 GLB URI/hash 28개(35,892,956 bytes)다. 관계 행은 개념·target extent 수가 아니다.

최종 자동 검증 evidence: `work/evidence/T66/parallel-completion-2026-10-03/integration-wave1/final-validation.json`. 등록된 고유 GLB URI 28개의 저장 hash/byte 행과 실제 파일을 다시 대조했다.
