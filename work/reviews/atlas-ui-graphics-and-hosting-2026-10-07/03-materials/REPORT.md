# 03 — 조직 재질·조명·깊이 표현 완료

현재 지원 앱의 이번 그래픽 범위는 **passed / local_supported_materials_ready**입니다. 콘텐츠는 partial입니다. T40/T66/T85 및 EXECUTION 상태를 수정하지 않았습니다. 공개 배포나 사람 검토 승인을 뜻하지 않습니다.

## 화면과 공통 구현

뼈는 밝은 ivory `#e9dfc8`, 근육은 차분한 red `#a34b4e`, 신경은 yellow `#dbbb32`로 통일했습니다. 선택 근육의 teal과 기존 작용/복원 phase tone을 유지하고, 선택 신경은 yellow-green `#d0c42f`와 밝기·roughness 차이 및 카드/범례로 구분합니다. 관련 근육의 파란 강조도 유지했습니다. 실제 신경 관찰에서 관련 근육 opacity를 .82에서 .5로 낮춰 주행이 덜 묻히게 했습니다. 모든 조직/state의 depthTest는 true이며, 불투명 조직은 depthWrite=true입니다. 가려진 신경을 depth 검사 우회로 표시하지 않습니다.

`anatomyMaterials.ts`가 source 계약의 조직 종류와 presentation state를 받아 동일한 MeshStandardMaterial 정책을 제공합니다. DatasetSceneAdapter, DatasetResources, AnatomySceneController가 이를 사용합니다. 각 scene/resource 소유자별 캐시를 사용하며 개별 mesh eviction이 공유 재질을 dispose하지 않도록 고쳤습니다. 기존 normal attribute와 원본 geometry를 그대로 사용하고, per-structure shader·texture·AO·shadow·후처리를 추가하지 않았습니다. 기존 세 조명만 조정했습니다(hemisphere 1.7→1.15, key 2→2.1, rim .9→.85, ACES exposure 1.05→1). render clock·dirty/동작 render·입장 12도/1.4초·reduced-motion·클립 크기를 유지했습니다.

현재 integration snapshot의 eligible source row는 근육 472 / 뼈 213 / 신경 195이고 accessory 288행은 eligible=0입니다. 이는 해부학적 target/개념 분모와 다른 source row 수입니다. 이번 단계의 새 geometry/clip/binding/지원 승격은 0입니다. 따로 식별된 eligible tendon 표면이 없으므로 일반 근육의 끝을 힘줄로 칠하지 않았습니다. 명시적으로 typed tendon을 받는 밝은 재질 정책만 있으며 실제 힘줄 구현 완료로 세지 않습니다. 가짜 섬유 방향도 만들지 않았습니다.

신경 선택 맞춤에는 실제 source 주행·기존 확인된 관련 근육·부착 뼈 bounds를 사용합니다. 일부 신경 source의 region membership가 다리와 몸통까지 넓어 국소 선택 맞춤이 전신처럼 작아지는 문제를 해결했습니다. 표시 문맥은 유지하며 anatomy/identity/region/관계를 수정하지 않았습니다. 또한 방향 전환 직후 선택 맞춤을 누르면 회전 중간 방향에 멈추던 기존 결함을 공통 camera fit에서 수리했습니다. 진행 중 전환의 최종 방향을 이어받습니다.

## 측정과 전후 화면

[실제 비교 원본](matched-profile.json), [측정 요약·한계](performance-metrics.json), [전달 자산 비교](delivery-asset-comparison.json), [PNG 치수와 SHA](screenshots.json).

| 1440×900 전신, 같은 camera/source/DPR=1 | 변경 전 | 변경 후 |
|---|---:|---:|
| render CPU P50 / P95 | 2.4 / 3.3 ms | 1.4 / 2.6 ms |
| frame interval P50 / P95 | 16.6 / 18.6 ms | 16.7 / 18.7 ms |
| draw calls / triangles | 672 / 486,184 | 672 / 486,184 |
| root의 고유 material / shader program | 2 / 1 | 2 / 1 |
| CPU geometry buffer bytes | 6,825,150 | 6,825,150 |

CPU 값은 renderer.render 호출의 한 번 관측한 전후 표본입니다. GPU 완료 시간이나 반복 benchmark의 속도 보장이 아닙니다. frame interval은 idle에서도 기존 frame clock 간격을 기록하며 실제 렌더 비용과 분리합니다. GPU 시간·VRAM·전체 프로세스 메모리·실기기 성능은 관측 불가입니다. 조명/재질 변경을 함께 적용했으므로 각 조명만의 인과적 비용은 따로 확정하지 않습니다. 모형 비용은 geometry/buffer/bytes가 같아 새 데이터 비용 0으로 분리됩니다.

전신 warm GLB 3개 ResourceTiming encoded 합계는 9,051,664 bytes이며 transfer 합계 900 bytes는 재검증/캐시 응답 헤더입니다. cold 다운로드로 부르지 않습니다. 같은 URI/SHA 자료이며 texture/geometry 추가 bytes=0입니다. 최종 App JS는 기존 3,031,823에서 3,032,450 bytes로 **627 bytes 증가**했습니다. 나머지 app 파일과 gzip 수치는 전달 비교 JSON에 있습니다. 큰 JS chunk 경고는 그대로 기록했으며 예산을 바꾸지 않았습니다.

같은 전신 앞 시점 PNG는 [전](material-before-front.png) / [후](material-after-front.png)입니다. 초기 재질 변경 직후 촬영한 후 PNG를 재사용했습니다. 이후 변경은 신경 선택 cue/문맥 opacity, legend, 신경 맞춤 및 방향 전환 중 맞춤이므로 이 기본 전신의 조직/조명/geometry에는 영향이 없습니다. 비교 CPU 표본은 별도의 동일 입장 완료 camera 표본입니다. 복구된 브라우저의 일부 DPR=1.75 표본은 이 DPR=1 비교에서 제외했습니다. 신경/동작 PNG는 화면 상태 검증이며, 카메라가 다른 동작 PNG를 같은 시점의 성능 비교로 주장하지 않습니다.

## 실제 흐름과 회귀

[브라우저 원장](browser-validation.json), [최종 수리 production 원장](final-production-validation.json), [관련 계약 31/31](contract-tests.txt), [수리 관련 camera 3/3](camera-repair-tests.txt).

- 실제 viewport **1440×900 / 1024×768 / 390×844**에서 전신, 정중신경·관련 근육, 대퇴직근 무릎 폄, 대흉근 흉늑부, 등 대능형근, 손목/손 자세 문맥을 확인했습니다. CSS 폭 검증이며 아이폰/아이패드 실기기 검증은 아닙니다.
- 전신 기본 상태, 선택 대비, 사용자 반투명, 집중 관찰, hidden, layer-off 및 motion 준비/작용/복원/held를 대조했습니다. 정중신경 선택→관련 근육→뒤로, 사용자 반투명 유지, 신경 layer-off/on을 확인했습니다. 데이터 viewer에는 기존 mesh-hover handler가 없으므로 hover는 공통/legacy 정책 계약 검사이며 실제 dataset hover 화면 합격으로 쓰지 않습니다.
- 외복사근 숨김→내복사근 선택→집중 관찰에서도 숨긴 외복사근이 나타나지 않았습니다. 신경 depthTest는 모든 sampled material에서 true였습니다.
- 대퇴직근 시범의 기존 **71개** 동반 표면을 유지합니다. loop→작용 phase→재클릭 부드러운 rest→scrub/held, muscle layer-off에 따른 취소·복원, opacity 변경 시 기존 정책의 시범 취소를 확인했습니다. 작용 phase의 기존 선택근 강조를 지우지 않았습니다.
- 긴노쪽손목폄근의 기존 **37개** 손목 굽힘 문맥은 자세 관찰입니다. 뼈·손·손목·주변 근육이 보이며 실제 근육 작용으로 승격하지 않았습니다. 비지원 운동 pose에서 정적 신경을 가리는 기존 정책도 유지합니다.
- 기존 대흉근/능형근 clip 및 source/part를 그대로 사용했습니다. 뒤 시점→즉시 선택 맞춤 수리 후 실제 camera x=target.x, z<target.z를 확인했고 최종 고정 production 화면에서도 재검증했습니다.
- 동일 개발 root에서 resize/선택 흐름 유지, 단일 canvas와 overflow 없음, console error/warning 0. 코드 변경/HMR 시 새 root는 지속성 근거로 쓰지 않습니다. 최종 held의 renderedFrames **125→125**, 추가 idle render 없음.

Typecheck, generated card/motion freshness, scene decoder, production/local build, 배포물 learner metadata audit, sync_execution.py --check가 통과했습니다. 처음 build 확인 뒤 로컬 준비 도구가 자체 build를 수행했고, 실제 camera 결함 발견 후에는 해당 camera 계약/typecheck와 최종 고정 snapshot build를 다시 수행했습니다. 동일 geometry QC나 전체 suite는 재실행하지 않았습니다. 마지막 camera 수정은 재질·CSS·원장·자산에 영향이 없으므로 앞선 세 폭·신경·동작 화면은 영향 분석 후 재사용하고 최종 뒤 시점 흐름만 추가 검증했습니다.

최종 로컬 snapshot: `local-20261007164328940-bf4218bb`, manifest SHA `3a7c7166484576a211a88870d6d77de85b50f83d995963433eca0a3bd8438ac9`. 보존된 WIP의 실제 snapshot이며 commit만으로 전체 원본/자산이 확보된다고 주장하지 않습니다. localhost 검증만 수행했습니다.

## 보존·남은 범위

기존 94개 non-app URI/bytes/SHA가 모두 동일합니다. EXECUTION/product-acceptance hash도 시작과 같습니다. 542 targets/563 memberships/12부위, HA130, 역사163, source-only/local selection/public held/humanReview not_performed를 유지했습니다. 원본/source-cache/OpenSim_Models/T13을 변경하지 않았습니다. DatasetSceneAdapter의 기존 midline bone WIP는 보존하고 이번 재질/신경 맞춤 변경만 분리해 커밋합니다.

이번 지원 재질 범위의 제품 blocker는 없습니다. 기존 미확보 anatomy/신경 pose/정확 footprint/미지원 motion과 범위 밖 engineering backlog는 별도로 유지합니다. 모든 근육의 texture나 힘줄 경계가 완성됐다고 쓰지 않습니다. 다음은 `work/plans/atlas-ui-graphics-and-hosting-2026-10-07/04-attachment-visualization.txt`이며 자동 실행하지 않습니다.
