# T85 — 등록된 모든 근육 움직임의 주변 구조 검증

## 판정과 실제 문제

현재 working tree에 등록된 **331개 muscle asset/source-action 결속, 133개 source 표면, 70개 고유 실제 GLB**를 자동 검사했다. 기본 뼈/근육 보기에서 선택 표면, 기존 package 근육·뼈, 연결 가능한 기시·정지 뼈, 실제 moving-bone 트랙과 GLB hash/member가 모두 확인되었다. **331/331 core context 검사 통과**는 전수 화면 검사·전체 부착 범위·작용 승인과 다르다. 미지원 option 7행은 지원 근육 7개라는 뜻이 아니다.

긴노쪽손목폄근의 기본 손목 굽힘 시범은 수정 전 새 기본 상태에서도 손목/손의 뼈가 나왔다. 따라서 사용자가 본 뼈 없는 상태의 원인이 입증되었다고 쓰지 않는다. 실제 결함은 기시·정지 문장에 명시된 상완골/제2중수골이 current attachment context에 연결되지 않은 점이었다. bones-off/isolate 상태에서 주변 구조가 빠지는 경우도 명확한 안내가 없었다.

## 수정

- 근육의 검증된 기시·정지 요약문에 **정확히 적힌 기존 whole-bone 이름**을 같은 쪽/midline 표시 적격 source로 연결한다. 기존 curated 목록은 유지하며 이름 중복/반대쪽/hold/근육명 내부 문자열은 제외한다. current working-tree 내용에서 263개 context 항목과 389개 bone-role 연결을 보완했다. 정확한 부착 면/좌표를 만든 것은 아니다.
- 모든 동작이 같은 visibility 계약을 사용해 부위 필터로 움직이는 사지 문맥을 잘라내지 않는다. 선택 근육의 기존 강조와 주변 근육 대비를 유지한다. user hidden/layer-off/isolate는 보존하며, 뼈 꺼짐과 격리로 문맥이 제한되는 상태를 안내한다.
- 기존 짧은갈래 상완이두근 좌우 팔꿈치/어깨 굽힘 4개 source-local 시범에는 native 노뼈와 손 사슬이 빠져 있었다. 실제 GLB의 동일 쪽 moving ulna 변환을 재사용하여 **각 33개 기존 native 뼈/수동 근육**을 함께 이동한다. 근육은 양 role 뼈 연결이 있고 모든 부착이 같은 이동 사슬 안에 있을 때만 동반 이동한다. 고정 상완골에 걸친 근육이나 미확정 부착을 rigid하게 끌고 가지 않는다. 고유 추가 native 구조는 양측 합계66개다. 교육용 강체 동반 이동이며 measured 축·새 GLB·근육 작용·활성도 승인이 아니다.
- native instance matrix와 actual emitted clip의 0/25/50/75/100%에서 상대 배치/강체 determinant/정확 rest 복원을 검사했다. 손목 굽힘 관찰을 선택 폄근의 수축 작용으로 바꾸지 않는다.

## 실제 화면과 검증

긴노쪽손목폄근 양측 손목 굽힘 및 양측 짧은갈래 상완이두근의 팔꿈치/어깨 굽힘을 실제 브라우저에서 확인했다. 손목·손가락, 기시·정지 whole-bone, 선택 근육의 청록 강조와 주변 근육의 분홍 대비를 확인했다. 4개 변경된 팔 시범에서 추가33개 native 구조가 끝 자세에서 모두 이동했고, rest에서 exact matrix 복원을 확인했다. 재생/재클릭smooth-rest/스크럽/side 전환/뼈 layer-off 취소 및 복원이 작동했다. console 오류0이다.

손목 held-end 화면을 실제 **390×844 / 1024×900 / 1440×900 CSS viewport**에서 기록했다. 팔 변경 사례는 기본1280×720에서 확인했다. 390은 desktop browser 검사이고 모바일 실기기 검증이 아니다. 입력과 함께 PNG 대신 도구가 실제 반환한 JPEG와 canvas 상태 JSON을 저장했다. 화면 파일은 별도 합성하지 않았다.

관련 자동 회귀103개, typecheck, production build 통과. 재현 가능한 선택적 checkpoint에서 새/관련 검사9개와 HEAD 기준 card generator/check가 추가 통과했다. Build의 기존 chunk>500KB 안내는 남으며 예산을 완화하지 않았다. 변형 GLB/각도/기하 bytes는 바꾸지 않았다. 추가 native context의 GPU/VRAM/전체 process 메모리와 지연 성능은 이번에 측정하지 않았다.

## 남은 범위와 보존

**141개 결속 행 / 61개 source 표면**은 기시 또는 정지의 whole-bone 연결 목록이 비어 있다. 이 숫자는 뼈가 실제 없거나 애니메이션이141개 실패했다는 뜻이 아니다. 연부조직 부착/옛 용어/아직 정확히 연결하지 않은 문구 등이 포함된다. 행별 빈 role은 `context-audit.json`에 그대로 남겼다. 이미 문장에 정확히 연결된 뼈만 검사했으므로 완전한 해부학적 부착 coverage는 **partial**이며 4요건을 모든 근육에서 완전 충족했다고 주장하지 않는다. 문장에 없는 뼈/footprint를 추정하지 않았다.

T85 기존 우선7그룹/20표면/22 action binding/13GLB scoped acceptance를 바꾸거나 current331개 posture 포함 결속을 모두 muscle-action 승인으로 세지 않는다. T85 후속의 자동·대표 문맥 검증 결과는 `validated_with_known_attachment_gaps`다. 전체429/447/232/462 및542/563/12, HA130, 역사163(6/20/135/2), source-only·local technical selection·rights held·humanReview not_performed를 보존했다. T40/새 task/자동 agent/push/배포는 실행하지 않았다.

이번 live 검증은 기존 미커밋 콘텐츠를 포함한다. **로컬 checkpoint는 HEAD 콘텐츠를 기반으로 소유 코드 변경과 재생성된 투영만 저장**하며 기존 미커밋 field/source content 확장을 가져오지 않는다. HEAD projection62행과 live461행은 다르며 live 새 연결389개를 모두 checkpoint의 새 콘텐츠라고 주장하지 않는다. HEAD context 변경은2개 항목/2개 role-link이다. `checkpoint-scope.json`이 각 입력 경계/hash를 기록한다. 기존 WIP와 generated assets는 그대로 보존한다.

증거: `context-audit.json`, `browser-validation.json`, `metrics.json`, `final-validation.json`, `checkpoint-scope.json`; 실제 화면 `wrist-1440.jpg`, `wrist-390.jpg`, `elbow-left.jpg`, `shoulder-right.jpg`.
