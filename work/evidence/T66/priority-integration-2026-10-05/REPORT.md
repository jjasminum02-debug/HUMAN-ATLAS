# T66 우선 Atlas 최종 통합 결과

**completed / passed — 현재 지원 우선 범위.** nextUnit=null, productReadiness=local_app_ready, contentCompleteness=partial. contractRevision=app-completion-2026-10-01 / scopeAmendment=priority-muscle-atlas-2026-10-05. 전신·모든 근육·신경의 완성이나 공개 배포 승인은 아니다.

실제 현재 learner runtime에서 우선 7근육군의 available 양측·부분 표면 20개, exact source/action 연결 22개, 고유 GLB URI/hash 13개를 확인했다. 대흉근 쇄골·흉늑·배부분과 대/소능형근을 각각 검사했다. 서로 다른 표면이 가족 GLB를 공유하므로 연결 수와 자산 수를 혼동하지 않는다. posture 관찰을 선택 근육의 작용으로 세지 않는다.

## 움직임 확대와 실제 수리

|대표 동작|기존|현재|처리|
|---|---:|---:|---|
|대퇴직근 무릎 폄 준비 범위|15°|19.5°|실제 각도 +30%, 양측71개 문맥 표면·슬개골·넙다리네갈래근·하퇴/발 유지|
|대흉근 모음|8°|10.4°|실제 각도 +30%, 양측3부분 각각 연결|
|견갑거근 어깨뼈 올림|5°|6.5°|실제 각도 +30%|
|대/소능형근 어깨뼈 뒤당김|5°|6.5°|실제 각도 +30%, 양측 대/소 분리|
|앞정강근|6.5°|6.5°|이미 확대된 T59 오른쪽 clip 보존, 왼쪽 native 자산 독립|
|대퇴직근 고관절 굽힘 보조 시범|12°|12°|기존 검증된 별도 작용 보존|
|복직근·외복사근 양측 협응 몸통 굽힘|14°|14° + 화면1.3배|실제 표면 변형 유지, 같은 camera의 projection zoom으로 이동의 가시성 +30%|

몸통의 18.2° 후보는 실제 내부사근의 보간 접촉·뒤집힘 검사에 실패했다. 이를 등록하거나 검사를 완화하지 않았다. 화면 확대를 실제 각도/ROM 증가로 보고하지 않으며 실패 후보는 별도 deferred engineering이다. 이전 14° GLB와 source binding은 동일 입력/hash로 재사용했다. 화면 확대는 검증된 morph를 대체하지 않는다.

이번 8개 새 파생 GLB는 emitted key·중간 보간·native frame·측·변형·새 관통·접촉·작용 결과를 검증해 등록했다. 어깨 문맥에서 광배근의 척추 쪽 고정 부착을 보존하는 source별 passive weights를 작성했다. 팔 움직임에 잘못 끌려가던 이복근 뒤힘살을 같은 장면의 고정 문맥으로 수정했다. 모형 제거/단순 scale/라벨 변경으로 통과시키지 않았다. 새 source-specific authored 값은 실측 부착점·정상축·정상 ROM이 아니다.

## 실제 사용자 흐름

측·부분별 선택 → 작용 설명 → 동일 장면 반복 → 재클릭 부드러운 rest → scrub 자세 유지 및 복원 확인. 카메라 수동 회전은 복귀가 덮지 않는다. hidden/muscle layer-off에서는 재생 버튼이 비활성화되고 숨긴 구조가 되살아나지 않는다. 새 projection zoom은 다음 장면 fit에서 초기화된다. 기존 손 작용도 재생/복원했다.

실측1440×900, 1024×900, 390×844 브라우저와12부위 전환을 확인했다. 390은 desktop CSS viewport이며 실기기 검증이 아니다. PNG와 viewport/scene 상태, 실제파일 SHA는 browser-validation.json에 있다. 개발 중 잘못된 posture intent 또는 이전 geometry 화면은 현재 작용 합격 근거에서 제외했다. 최종 콘솔 오류0.

신경 선택 → 정상 주행·문헌 포착 맥락 → 같은 측 관련 근육 → 대표 작용 → rest 흐름을 확인했다. 정적 신경은 비지원 운동 pose에서 가려지고 user nerve-layer 상태대로 rest에서 복원된다. static195표면/98label은 해부 개념 수가 아니다. 관계18행 중 geometry-bound2, literature-concept16이며 동적신경0, 포착좌표0이다. 힘·활성도를 측정하거나 분지 좌표를 새로 확정하지 않는다.

## 검증·한계·보존

데이터 계약 전수, current authoring/outcome/dependency SHA, priority action/nerve/player/selection 계약, whole-body73, delivery4, typecheck 및 production build 통과. 오래된 배열 위치/T63 manifest/고정 bone-row 개수 검사를 실제 ID/현재 manifest/typed moving-fixed 계약으로 수정했다. Python과JS의 JSON 숫자 직렬화 차이를 해부 계약 차이로 오판하지 않도록 source binding 자체를 대조한다.

Build JS chunk6716411bytes(gzip740.45kB) 권고 경고는 남았다. T85에서 현재 지원 앱의 실제 프로파일과 UI 품질을 다룬다. 이번에는 VRAM/GPU/총process memory나 실기기 성능을 관측했다고 쓰지 않는다. 자동 전체 suite 반복 대신 실패 검사의 실제 원인을 수정하고 최종 관련 검증을 수행했다.

542/563/12, muscle429/447/232/462, HA130 및 역사163(6/20/135/2) 보존. 원본/source-cache/OpenSim_Models/T13/WIP와 source-only, technical local selection, humanReview=not_performed, public rights=held 보존. 기존 역사 보고는 덮지 않는다. 범위 밖 jaw/face/breathing/E proposals 실패·외복사근 단측 회전·더 큰 몸통각도 후보는 deferred engineering으로 유지하며 미확보 자료로 재분류하지 않는다. 현재 지원 우선 범위의 unresolvedProductBlockers=[]; 전체 content completeness는 partial.

다음은 수동 T85 UI/성능 품질 검사이며 자동 실행하지 않았다. 현재 product-scope.json을 읽고 우선 지원 범위만 검사한다. 전신 신규 자산 제작을 T85 gate로 추가하지 않는다.
