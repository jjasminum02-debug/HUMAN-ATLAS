# 다음 ID: T100 · Luna Max

```text
HUMAN ATLAS에서 T100만 수행해라. 담당 Luna Max.
AGENTS.md, work/EXECUTION.json, work/NEXT.md, STATUS의 generated 블록,
work/tasks/T100.md, design/2026-09-25-muscle-atlas/25-WHOLE-BODY-BASE-RESET.md,
T98 최신 결과와 T99 보고서, work/evidence/T99의 validation.json,
compiled-receipt.json, browser-cycles.json, preservation.json,
atlas-data/tools/datasets/README.md를 읽어라. 실제 compiled manifest와 시작 입력 hash도 확인해라.

T99는 로컬 compiler/loader 기술 합격이다. 960은 고유 근육 수가 아니라
509 근육/부분 + 277 골격 + 174 부속 표면이다. 542 targets/563 memberships/12부위,
unresolved 후보, source-only/원본 숨김/권리·human-review hold를 보존해라.
로컬 QA에 보였다고 learner binding이나 기본 표시·공개 배포를 승인하지 마라.

검증된 indexed overview/detail과 공통 DatasetResources/ResourceQueue 및 단일
AnatomySceneRoot/renderer/camera를 재사용해 T100 범위의 전신 통합, 12부위 다대다 소속,
좌우·세 이름/검색·typed selection, 핵심 관찰 도구를 구현해라.
근육과 골격을 우선하고 부속 표면은 별도 레이어/분류로 보존하되 삭제하지 마라.
source-only 관찰과 canonical 학습 선택을 구분하고 exact mapping을 검증해라.
기본 표시 적격은 별도 근거로 기록하고 held/user layer-off를 복원으로 노출하지 마라.
BP3D와 ZA는 정합되지 않았다. ZA 1unit=1m, local geometry + [x,z,-y] 포함 instance matrix를
한 번만 적용하며 이미 굽힌 world transform을 중복 적용하지 마라.
기존 BP3D는 검증된 byte-preserving compatibility adapter이며 원본 해시와 회귀를 보존해라.
새 task 전용 loader/extension/parent-chain을 만들지 마라.

목+머리 합집합·재클릭 해제·빈 선택 전신, 양측 어깨/위팔/견갑골, 얼굴, 광배근,
요추·엉치뼈, 손발·골반바닥을 coverage matrix로 검증해라. 주변 흐림·선택 반투명/숨김·격리·맞춤·undo/복원을
같은 카메라에서 구현하고 미니멀 UI와 로딩의 로고/인체 그림/슬로건 제거를 유지해라.
표정근 motion은 disabled이며 새 애니메이션·신경 3D·미검증 엑셀 본문은 넣지 마라.

파생 캐시가 유효하면 재취득·Blender 재평가를 반복하지 마라.
Blender 신선 재평가는 비트 동일하지 않을 수 있으므로 frozen resource hash와 revision을 확인하고,
필요한 경우만 승인된 Blender --factory-startup --disable-autoexec로 같은 unit을 재개해라.
20MiB overview / 1M active triangles / 96MiB geometry / 8MiB chunk 예산을 유지해라.
상세 요청이 triangle 예산을 넘으면 overview를 유지하는 정상 fallback을 보존해라.

시작 HEAD/status/hash를 기록하고 원본/OpenSim_Models/T13 drafts/사용자 WIP를 보존해라.
실제 12부위·선택·관찰·성능 evidence와 내부 bounded work-unit progress를 남겨라.
모든 필수 unit 전에는 전체 T100/G1 완료라고 하지 말고 미완 unit만 같은 T100으로 재개해라.
EXECUTION의 T100 record만 갱신하고 sync_execution.py와 --check를 실행해라.
소유 변경만 선별 로컬 커밋하고 해시·포함/제외·잔여 변경·다음 프롬프트를 남겨라.
T80/T58 및 다른 task 자동 실행, push, 배포, 진단·치료·침 시뮬레이션은 하지 마라.
```
