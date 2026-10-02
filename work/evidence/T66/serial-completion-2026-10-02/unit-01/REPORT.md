# T66 내부 unit 01 — 상지 rejected deformation 후보 수정

**범위:** 양측 어깨 굽힘·팔꿈치 굽힘의 짧은갈래 위팔두갈래근 source surface 후보 4개와 source-frame exact GLB track 작성 경로. 다른 unit은 실행하지 않았다.

## 기준선과 보존

- 시작 HEAD `253cb9748191b3bb647cb697d453d4c37b09b5d6`; unit 시작 시 dirty entry 1,085개의 경로/hash를 [`start-baseline.json`](start-baseline.json)에 남겼다. [`preservation.json`](preservation.json)은 pinned source manifest hash와 현재 OpenSim_Models clean status를 기록한다. 기존 사용자 WIP와 과거 산출물은 되돌리거나 삭제하지 않았다.
- 542 target/563 membership/12 regions, 근육 429/447/232 source concepts/462 surfaces, HA130, 역사 분류 163(6/20/135/2)을 유지했다. 새 canonical 연결과 whole-target extent 승인은 0이다.
- 원본 source geometry/topology는 불변이다. source-only, 고정 source 판정을 상속하는 local-use, public redistribution held, `humanReview=not_performed`를 유지했다. 축과 pivot은 authored 교육용 값이며 실측 정상축/부착 footprint가 아니다.

## 실제 결함과 수리

이전 팔꿈치 왼쪽 emitted GLB의 실제 중간 sample `1.5498046875 s` (`phase=0.774902`)에서 triangle 118, vertex `[41,49,40]`가 area ratio `0.02695`로 접혔다. 세 정점은 양 끝점 고정/moving mask 어느 쪽에도 없고 변형 전이 구간에 있었다. triangle 191도 area ratio `0.09125`였다. 이는 engineering transition-zone collapse이며 생물학적 부착 footprint 측정이 아니다. 원본은 238 vertices/484 triangles, geometry SHA `ffe0e775daa48c8ecb3141aa67dd0cb169f248a4f880385d1dde6ca83cee2d41`이다. 원본 topology, 끝점, 주변 구조와 기존 geometry/contact 기준을 유지했다.

fractional/ARAP 시도를 이유 없이 반복하지 않고 원본 topology의 triangle seed와 local corrective/transition weights를 사용했다. `rewrite_t66_glb_rigid_tracks.py`는 source-frame authored key를 GLB에 기록하고 실제 Three.js 보간을 검사한다. 각 source family는 자체 authored axis/pivot/weights를 유지하며 단일 rigid pivot/전체 mesh scale을 강제하지 않는다.

## 실제 통합과 검증

4개 r4 GLB를 기존 learner motion bundle/runtime과 단일 scene에 등록했다. 각 항목은 exact short-head source surface 자세 관찰만 지원하며 근육 활성도·힘·개인 ROM·주작용 시범·전체 muscle/group extent 승인이 아니다.

| family / side | sourceKey | 최종 GLB SHA-256 | 중간 GLB 검사 |
|---|---|---|---|
| shoulder flexion / left | `ZA-c7010a9-b20b574e456449c5d571c7a1` | `13cb37b2d1bf048626cb79d46ed28a3c2f6453f1d19444c106e46b6ec2403e86` | 257 samples; min area 0.106928; flips 0; new containment 0 |
| shoulder flexion / right | `ZA-c7010a9-a0c2ea00609e874a7faa926d` | `8f7e3a5ea0a27a4b2a6254ce65c6b8ed01c99dab67f2e2e0266a7fed12225b96` | 257; min area 0.106932; flips 0; new containment 0 |
| elbow flexion / left | same left sourceKey | `a263144376925c2ece792c965347f26911e6c6b9de4cc29dfc398983e8e3844d` | 513; min area 0.100092; flips 0; new containment 0 |
| elbow flexion / right | same right sourceKey | `eeb3924478234b86cfc47c3505ab74e89eaf27c81cba5e12998bee6e1bab5852` | 513; min area 0.100083; flips 0; new containment 0 |

`loadAnimationScene`/Three.js `AnimationMixer`의 실제 GLB authored key와 중간 위상을 원본 frame과 대조했다. r4 source-frame validation 4/4 통과; rigid context 최대 오차 `1.386e-7 m`(허용 `1e-6 m`). 변형 표면은 rigid로 간주하지 않고 같은 geometry/contact hash 기준으로 따로 확인했다. Continuous collision freedom은 주장하지 않는다.

**실제 learner browser 시각 확인은 미완료다.** CUA가 Mac 잠금 오류를 반환하고 탭은 about:blank였다. 선택/카드/좌우/중간 자세 UI 검증을 pass로 세지 않았다. [`browser-verification.json`](browser-verification.json)에 환경 상태와 남은 확인을 기록했다.

## 검사 및 상태

[`validation-2026-10-03.json`](validation-2026-10-03.json)의 motion schema, source policy, loader/mixer focused tests(12/12), TypeScript typecheck, Vite production build가 모두 exit 0이다. 빌드에서 큰 JS chunk 안내가 있었으나 실패는 아니다. 최종 geometry/frame evidence는 [`final-glb-source-frame-validation-r4.json`](final-glb-source-frame-validation-r4.json), 등록 receipt는 [`source-family-registration-r4.json`](source-family-registration-r4.json)이다.

4 rejected work keys는 engineering 결과 `implemented_verified`로 갱신했다. UI 시각 확인은 `blocked_by_environment`다. 등록 family 6→10, source-pose observation surfaces 75→79, unique GLB packages 7→11, remaining candidates 8→4, geometry/contact rejects 6→2; main-function clip remains 1. 겹치는 bilateral/action binding은 고유 물리 표면 수로 중복 계산하지 않았다.

T66-B1은 고관절 굽힘 좌우 2개 contact failure가 남아 미해결이다. B3의 나머지 family/source 큐와 B4 무릎 협응도 미해결. 부모 T66은 계속 `in_progress / partial`, `nextUnit=author-and-integrate-normal-motion-bone-and-nerve`다. **다음 수동 입력:** `work/plans/t66-serial-completion-2026-10-02/02-T66-hip-knee.txt`. 실제 learner browser를 확인하지 못했으므로 Mac 잠금 해제 후 unit02 전에 unit01 browser-only 확인을 먼저 재개해야 한다.
