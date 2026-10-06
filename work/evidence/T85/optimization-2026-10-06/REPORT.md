# T85 추가 최적화 — 2026-10-06

## 판정

현재 지원 앱의 기능을 보존한 최적화를 구현·검증했다. T85 completed/passed, nextUnit=null과 local_app_ready를 유지한다. contentCompleteness=partial이며 T66/T40/다른 task 상태를 바꾸지 않았다. T40·콘텐츠 제작·배포는 실행하지 않았다.

## 분석과 구현

주요 제품 실행 경로(앱 선택/작용 목록, 학습 데이터 생성, 공유 player/scene/frame loop, 원본 기하 검사, 자산 전달, chunk LRU/취소·late response, 관련 회귀·빌드)를 분석했다. 모든 파일의 모든 동작을 수동 전수 확인한 것으로 쓰지 않는다.

1. **정지 렌더 제거:** 공유 player는 rest/held/paused에서 false를 반환한다. scene은 dirty 또는 실제 동작 업데이트일 때만 그린다. 기존 void 업데이트는 호환을 유지한다. scrub의 같은 phase 변경도 requestRender를 호출하고 최종 복원 프레임과 OrbitControls 감쇠를 보존한다. 단일 frame clock은 유지한다.
2. **한 번 생성한 동작 계약:** 원장 정의/자산을 action·definition별로 색인하고 selector 투영을 빌드 내에서 재사용한다. Wave 등록 옵션도 같은 생성물에 통합하여 선택할 때 raw 등록 원장을 해석하지 않는다. 가족 계약/구성원/반복 ID·해시·설명을 손실 없이 공유한다. 정확한 ID/side/part/pose/members는 유지한다. 현재 작업 트리의 원장 옵션 1,166행/후보 1,159건은 실제 근육 작용 합격 수가 아니다.
3. **작은 전달 색인:** 98 MB motion-learning 원장을 최초 재생 때 JSON.parse하던 경로를 약14 KB local-motion-delivery-index로 바꿨다. 생성기가 전체 원장에서 등록 URI/SHA와 두 원본 입력 bytes/SHA를 만든다. 서버는 원본을 64 KiB 스트림으로 해시 확인하고 실제 GLB containment/hash/byte budget을 확인한다. stale index는503으로 실패하며 예산/권리 조건을 완화하지 않는다. 변경/추가/삭제 시 cache를 무효화한다.
4. **HTTP 캐시:** private/no-cache ETag로 같은 파일의 반복 전송을 줄인다. 304 전에 현재 파일을 검증하여 바뀐 파일을 캐시로 숨기지 않는다. 앱 안에 또 다른 대형 decoded GLB 캐시를 만들어 메모리를 중복 점유하지 않는다.
5. **기하 검사 할당 줄이기:** interleaved 속성을 정리할 때 정점마다 임시 배열을 만들지 않는다. 실제 해시와 변경 감지는 유지한다. 관측된 attach 검사는 작은 시범에서 약8–9ms였으므로 stale 위험을 늘리는 장기 geometry-hash 캐시를 도입하지 않았다.

## 같은 입력 비교

| 측정 | 이전 | 이후 | 범위 |
|---|---:|---:|---|
| 주 App JS | 6,717,611B | 3,633,188B | 45.9% 감소, 같은 자료/기능의 제품 빌드 |
| 동일 알고리즘 gzip(level9) | 700,187B | 463,379B | 실제 전송량 측정은 아님 |
| held 자세의 불필요 렌더 | 20.387초/1,235회 | 34.957초/0회 | 실제 브라우저, 입력 없는 구간 |
| 새 서버 전달 인스턴스 처리 중앙값 | 173.18ms | 48.15ms | 3회씩, 동일3059232B/동일SHA; 브라우저/네트워크 제외 |
| 최초 브라우저 시범 로딩 단일 표본 | 226.9ms | 89.8ms | 같은 견갑거근 GLB, OS/브라우저 캐시·서버 환경 차이가 있으므로 일반 속도 배율로 주장하지 않음 |

원장 + raw Wave JSON의 7,852,278B 입력 배포 경로는 3,285,605B 공유 생성물 하나로 정리했다. 이전 생성물의 267 selector/1,166행은 deep equality를 확인했다. Wave의 455 source-side 조합은 기존 projector의 결과와 대조했다. 새 Wave 경로는 기존 safeCandidate에 따라 비공개 poseSourceRefs를 제거한다(현재 원본은 빈 배열). 기하·동작 결과 계약을 생략하지 않았다.

## 검증

- 관련 최종 자동 회귀180건, 추가 모호한 자산/변경된 좌우 검사2건, compact delivery/cache/integrity 검사2건: 고유184건 통과. 전달 관련 기존4건은 후속 서버 변경 뒤에도 재확인했다.
- exact source-side455건, typecheck, production build 및 학습 배포 provenance 검사 통과.
- 실측 CSS390×844,1024×900,1440×900에서 견갑거근/대퇴직근/복직근의 대표 재생·진행 막대·재클릭 복원/근육 layer-off·검색과 카드 흐름을 확인했다. 팔·손 및 하퇴·발을 포함한 기존 문맥을 보존한다.
- 12개 부위 포함20회 전환 후 pending0/failed0/cache4entries/17,437,548B, 취소·late release0. 취소 동작을 매번 실제 발생시킨다는 뜻은 아니다. 취소·late-disposal 계약은 자동 회귀에서 검사했다.
- 신경→확인된 관련 근육→작용 연결과 정적 신경의 비지원 pose 처리 근거는 변형 입력이 같아 기존 T66/T85 근거를 재사용했다. 이번 실제 카드 연결도 확인했다. 신경 동적 pose/힘/활성도/포착 좌표를 새로 승인하지 않았다.
- 개발 중 메타데이터 회귀, HMR 전환 오류 및 잘못 적용된 viewport 요청을 수정/제외했다. 최신 새 브라우저 세션 오류0. 잘못된 요청 크기 캡처는 actual390으로 이름을 고쳐 전폭 QA에서 제외했다.

기존 7우선 근육군 20 available source surfaces/22 exact action bindings/13 unique GLB 및 분모542/563/12, HA130, 역사163(6/20/135/2)을 보존한다. 원본/source-cache/OpenSim_Models/T13/기존 WIP를 수정·승격하지 않았다. source-only/humanReview=not_performed/public rights held는 그대로다.

## 한계와 다음 순서

주 JS chunk500KB 권고 초과는 아직 남는다. 새 viewer/기술 교체/무조건 LOD 하향/몰래 예산 증가 없이 실제 비용을 줄였다. GPU/VRAM/전체 프로세스 메모리와 모바일 실기기 성능은 관측하지 않았다. 큰 몸통 GLB31,306,820B의 actual geometry/QC는 변경하지 않았다.

이번 수치와 검증은 보존된 WIP가 있는 작업 트리 기준이다. 최적화 checkpoint는 같은 코드 변경만 HEAD에 적용하고 생성 runtime/index는 HEAD 입력으로 재생성한다. 기존 미커밋 원장/자산을 소유 변경으로 커밋하지 않는다. clean 전달과 현재 WIP 전달의 차이는 T40이 확인해야 한다.

다음은 **T40 로컬 전달**이며 자동 시작하지 않는다. 자세한 제안 일정/종료 조건은 work/plans/t85-optimization-2026-10-06/README.md, 보충 인계는 T40-ADDENDUM.txt를 읽는다. 정상 앱의 실제 사용 확인→기존 가족을 재사용한 근육 확장→신경·뼈 설명/주행 확장→필요한 정상 조직 검증 뒤 병리 모형 순서다. 전체 콘텐츠 부족을 지금 지원 앱 완료의 전수0-gap gate로 되돌리지 않는다.

## 독립 저장본 확인

기존 미커밋 콘텐츠를 제외한 HEAD 입력에서도 새 생성기와 --check, Wave455 source-side 및 주 투영484행/223 selector의 deep equality가 통과했다. 커밋할 코드만으로 타입 검사와 관련19 회귀를 추가 확인했다(앞선184 고유 검사와 중복). 전달 색인과 생성물은 이 확정 입력으로 저장하며 현재 작업 트리의1,166행 생성물은 그대로 보존한다. 이전 HEAD의 DatasetSceneAdapter에 이미 존재하던 괄호 위치 오류는 독립 타입 검사에서 발견해 최소 수정만 포함했다. 기존 WIP의 뼈 지원 확대는 포함하지 않았다.
