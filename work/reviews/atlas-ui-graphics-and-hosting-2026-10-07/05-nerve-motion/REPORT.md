# 05 — 신경 주행·지배근 및 기존 근육 작용 강조

현재 지원 범위 **passed**. 새 신경 관계·형상·clip은 추가하지 않았다. 전체 콘텐츠는 partial이며 T40/T66/T85, EXECUTION/NEXT 및 다른 task 상태를 변경하지 않았다. 다음 06은 실행하지 않는다.

## 실제 변경

- 신경 선택/레이어 재활성 시 기존 공통 카메라로 실제 주행·관련 근육·부착 뼈 범위를 한 번 맞춘다. 반복 강조 변경은 사용자의 카메라를 재설정하지 않는다. 초기 deep link는 맞춤을 먼저 적용해 첫 등장 회전이 전환을 취소하던 문제를 해결했다. 부위 필터의 자동 프레이밍이 신경 맞춤을 덮지 않도록 연결했으며 최종 `regions=leg` 신경 링크를 1024×900에서 실제 확인했다.
- 원장에 실제 등록된 같은 측·같은 정적 pose의 분지만 경로에 포함하며, 부위 필터 밖의 실제 분지도 불러오고 밝은 노란 선택 강조를 사용한다. depth/material의 기존 규칙과 user hidden/translucent/layer-off를 보존한다. 이름/근접성으로 분지나 지배근을 추정하지 않는다.
- 지배근 목록은 실제 시범·실제 설명이 있는 근육부터 표시하고 exact source/side/action으로 연결한다. 중복 관계/작용을 제거하며 관계만 있는 근육은 선택 링크로 유지한다. 빈 작용 안내를 반복하지 않는다. 정적 주행의 제한은 한 줄, 관계 차이는 접힌 안내에 남긴다.
- 실제 작용의 부착 뼈 문맥은 04의 검증된 source/side/part 연결을 공통 presentation 경로에서 사용한다. phase의 선택 근육 강조와 주변 조직은 기존 규칙을 유지했다. 단순 자세를 작용으로 바꾸거나 clip 크기를 다시 30% 늘리지 않았다.
- 연속 시범에서 이전 선택의 상세 형상이 캐시에 남아 복직근 시범이 실패했다. 현재 wanted/pinned 자원을 보존하고 사용하지 않는 LRU 항목만 제거해 기존 96 MiB 예산을 동작 버퍼와 공유하도록 고쳤다. 실제 손 시범→복직근 시범의 실패를 재현한 뒤 같은 흐름에서 성공을 확인했다.
- 기존 신경 계약 검사의 오래된 field SHA 불일치는 10월 6일 채택 receipt와 exact proposal text/근거/새 운동관계 0건을 확인하도록 수정했다. 역사 원장을 덮거나 임의 현재 hash를 승인하지 않았다.

## 지원 수와 근거

전수 audit의 현재 런타임 수치는 정적 신경 **195표면**, 표시용 개념 묶음 98개, 기존 운동근 관계 **18건**(exact geometry 2, 문헌 개념 관계 16), 등록된 분지 edge 6이다. 개념 관계의 같은 측 표면 강조는 특정 신경 가지와 정확한 일대일 표면 결속 승인이 아니다. 운동/감각/인접·포착 관계를 합치지 않았다.

실제 muscle_action은 **56 source–action pair / 38표면 / 39고유 GLB**이며, 7우선 근육군은 **20표면 / 22 pair**다. 대흉근 part와 대/소능형근, 좌우를 구별한다. 1,166 runtime 옵션과 1,159 playable candidate는 실제 muscle_action 수가 아니다. 현재 작업 트리 입력을 측정했으며 역사 checkpoint 수를 수정하지 않았다.

[nerve-motion-audit.json](nerve-motion-audit.json)은 전수 신경 identity/side/branch/pose/정책 및 관계 근거, 실제 작용의 exact subject/member matrix/chunk SHA, 움직이는 뼈·부착 뼈·동반 근육 문맥, hidden/layer-off와 손목 굽힘 passive 구분을 검사했다. 오류 0건이다. 이름이나 출처 문장만으로 새로운 관계·footprint를 만들지 않았다.

## 실제 UI 검증

- 1440×900: 정중신경→손가락 시범→재클릭 smooth rest→뒤로 신경, 온종아리신경 양측→실제 분지, 깊은종아리신경→오른쪽 앞정강근 loop/scrub held/layer-off/rest를 확인했다.
- 1024×900: 견갑배신경→견갑거근 및 대/소능형근의 개별 작용, 대흉근 흉늑부의 실제 부착·주변 구조를 확인했다.
- 390×844: 대퇴직근 무릎 폄의 대퇴사두근·무릎·아래다리·발, 복직근/외복사근 대표 작용, 정중신경 카드/관련 시범, 긴노쪽손목폄근 손목 굽힘의 손·손목·위팔뼈·주변 근육을 확인했다. 손목 굽힘은 posture_observation이며 근육 작용으로 승격하지 않았다.
- 외복사근 숨김 뒤 복직근 선택에서도 숨김을 유지했다. 콘솔 error 0, 단일 canvas, 페이지 수평 overflow 없음. 폭 변경은 카메라를 리셋하지 않으며 명시적 선택 맞춤을 사용할 수 있다. 실제 아이폰/아이패드 검증은 아니다.

`browser-observations.json`에 실제 viewport/canvas 치수·선택·visible/hidden/layer·motion phase·cache 상태와 검증 빌드를 기록했다. `screenshots.json`에 JPEG 원캡처와 8 PNG의 실제 치수/hash를 남겼다. 수리 전 실패 PNG/원장도 보존했으며 이를 합격 시범으로 세지 않았다.

## 수치·검증 재사용

연속 손→몸통 전환에서 캐시 71,317,368 bytes + 동작 추정 61,882,524 bytes가 예산을 초과했다. 수리 후 사용하지 않는 6 chunk를 제거하여 정적 캐시 33,709,100 bytes + 동작 61,882,524 bytes = **95,591,624 bytes**로 기존 100,663,296 bytes(96 MiB) 안에서 재생된다. 구조 삭제/예산 상향은 없다. CPU 자원 추정치이며 GPU/VRAM/total-process 메모리로 해석하지 않는다.

최종 공개 파일 bytes는 253,170,065→253,172,495(+2,430), UI 파일은 3,317,155→3,319,585이다. 보존된 이전 transport WIP를 포함한 실제 snapshot 간 값으로, 단계별 비용 귀속을 과장하지 않는다. **94 non-app 파일 및 92 GLB의 bytes/hash가 동일**하다. geometry/frame/member 계약을 다시 확인했고 기존 emitted key/mid/contact/outcome QA는 의존성 변화가 없어 재사용했다. 큰 JS chunk 경고는 그대로이며 예산을 올리지 않았다.

관련 검사 **17/17**, ResourceQueue/기존 body 정책 회귀 **13/13**, 전수 audit, typecheck, production build, learner 배포 projection 검사(274개 내부 marker, leak 0), `sync_execution.py --check`가 통과했다. 전체 역사 suite나 고정 catalog 검색을 반복하지 않았다.

## 보존·한계·인계

542/563/12, HA130·역사163, source-only/local selection/public rights held/humanReview=not_performed를 보존했다. EXECUTION/product acceptance/신경 graph·원문 원장/overlay/generated motion runtime SHA는 입력과 동일하다. 원본/source-cache/OpenSim_Models/T13을 수정하지 않았다. 기시정지 정확 영역 미확보는 별도 gap이며 본 단계 blocker가 아니다.

현재 supported app의 이 단계 제품 blocker는 0이다. 미확보 신경 3D·dynamic pose·새 작용 자산·정확 footprint와 기존 deferred engineering은 별도로 남는다. 전 신경/전신 동작 완료나 사람 검토/공개 배포 승인으로 쓰지 않는다.

검증 대상은 `preserved_working_tree_snapshot_not_commit_only`이며 `preservation-and-size.json`에 WIP dependency 29개를 명시했다. 다른 WIP 및 잠시 시작했던 06 transport 수정은 이번 checkpoint에 포함하지 않는다. shared DatasetSceneAdapter는 이번 변경 hunk만 stage한다. 이 commit만으로 WIP 포함 전체 앱의 clean checkout 재현을 주장하지 않는다.

다음 프롬프트: `work/plans/atlas-ui-graphics-and-hosting-2026-10-07/06-vercel-hobby-package.txt`. 이번 단계에서는 hosting/push/외부 배포를 실행하지 않았다.
