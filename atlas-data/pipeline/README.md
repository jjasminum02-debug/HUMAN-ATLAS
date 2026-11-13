# Z-Anatomy 추출 파이프라인 (로드맵 D1)

Z-Anatomy `Startup.blend` 하나에서 뼈·근육·관절/인대·근막·부착 면·신경·혈관(Q2-1)을 구조당 GLB와 `structures.json`으로 뽑는다.
원본 .blend는 저장하지 않는다. 출력은 `atlas-data/source-cache/datasets/za-full/`(git 제외, 약 105MB).

```bash
# 1. 추출 (Blender 5.2, 약 90초. 끝난 구조는 다시 쓰지 않음)
blender --background --factory-startup --disable-autoexec \
  atlas-data/source-cache/z-anatomy/t97/extracted/Z-Anatomy/Startup.blend \
  --python atlas-data/pipeline/extract_za.py
# 2. 검증
python3 atlas-data/pipeline/validate_za_full.py
python3 -m unittest atlas-data/pipeline/test_za_classify.py
# 3. 눈으로 확인: pnpm dev 후 http://127.0.0.1:5173/qa/za-full.html
```

## 파일
- `za_classify.py` — 분류 규칙(Blender 없음). ZA 번호 컬렉션 → Bonus 컬렉션 경로 → 이름 키워드 순.
- `extract_za.py` — Blender 스크립트. 평가된 형상(모디파이어·곡선 bevel 적용), detail/overview LOD, 부착 면 ↔ 근육·뼈 연결.
- `validate_za_full.py` — 파일·hash·GLB, 종류별 최소 개수, 키·좌표계, 좌우 대칭, 부착 면 위치, 이전 추출과 변환 일치.

## 출력 형식
- `structures.json` → `structures[]`: `id`(`za:<slug>`), `sourceName`, `name`, `system`(skeletal·attachment·joint·muscular·nervous),
  `kind`(bone·ligament·capsule·fascia·origin·insertion·nerve …), `side`(left·right·unpaired), `regions`, `bonusPaths`,
  `matrix`(열 우선 4×4, 원본 world 변환 후 축 변환 [x, z, −y]), `mirrored`, `bounds`(앱 좌표, m), `lods.detail/overview`.
  부착 면은 `ownerIds`(근육·인대·근육의 갈래들)와 `boneId`를 가진다.
- `exceptions.json` — 형상 없음 5, 주인 구조 없는 부착 면 20(대퇴사두근·하퇴삼두근·척추세움근 같은 묶음 개념, 메시 없는 공통 힘줄 등).
- 좌표: 앱 좌표계 HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR, 미터. 형상은 객체 로컬, 같은 형상은 파일 하나를 공유한다.

## v2 런타임 자료 (로드맵 D2)

```bash
python3 atlas-data/pipeline/build_runtime_v2.py   # D1 추출 + 동결 스냅샷 → runtime v2
cd atlas-web && node --experimental-strip-types --test src/data/atlasV2.test.ts
```
- 결과: `atlas-data/runtime/structures.json`(구조 2,660개: 이름·부위·표시 여부·내용 연결·좌표·LOD),
  `atlas-data/runtime/relations.json`(기시/정지 705, 신경 가지·지배, 관련 근육),
  `source-cache/datasets/za-v2/`(형상 chunk + `geometry.json`, git 제외).
- 앱은 `atlas-web/plugins/atlasV2.ts`가 이 세 파일만 읽어 `/__atlas/integration.json`과 manifest를 만든다.
  변환 코드는 `atlas-web/src/data/atlasV2.ts`(`projectLegacyRuntime`). 이전 합성(BodyParts3D 보충·증거 hash 검사)은 쓰지 않는다.
- 기존 1,155개 구조는 key·이름·내용 연결·chunk bytes·resource key·matrix가 이전과 완전히 같다(움직임 시범의 hash 검사 때문).
  새 구조(인대·관절낭·부착 면·중추신경 등 1,505개)는 2MB 이하 on-demand chunk로 따로 묶여 기본 로딩에 포함되지 않는다.
- `freeze_legacy_runtime.py`는 이전 dev 서버 출력을 한 번 동결하는 이관용 스크립트다(`atlas-data/runtime/legacy/`). 다시 실행할 필요 없다.

## 한국어 이름 (로드맵 C1)

```bash
python3 atlas-data/pipeline/verify_names_kmle.py   # KMLE 대한해부학회 사전 대조(캐시 재사용, 처음엔 약 40분)
python3 atlas-data/pipeline/names_ko.py            # 초안 + 사전 값 → terminology/structure-names-ko.json
python3 atlas-data/pipeline/build_runtime_v2.py    # 이름이 없던 구조에만 채움
```
- 우선순위: 사전 값(정리: 괄호 주석 제거, [대체어]는 별칭) → 기존 신경 표 → KAA 규칙 초안(주머니/낭, 바닥쪽/척측 관례 적용) → 번호 규칙.
- 사전과 다른 초안은 검색 별칭으로 남긴다. 사전 오류로 판단한 행은 `SOURCE_REJECTED`에 이유와 함께 둔다.

## 인대·관절·근막 카드 (로드맵 C3)

```bash
blender --background --factory-startup --python atlas-data/pipeline/contacts_za.py   # 표면 접촉 → za-full/contacts.json
python3 atlas-data/pipeline/build_cards.py                                              # → runtime/structure-cards.json
```
- 관절 소속·종류: ZA `Arthrology` 계층. 잇는 뼈·감싸는 근육: 표면 접촉(4% 이상 차지한 대상만).
- 설명 문장: `joint_content.py`(AI 작성, 사람 검토 전). 관절 이름 사전 대조: `terminology/joint-names-kmle.json`.
- 앱은 `/__atlas/v2/cards.json`을 인대·관절·근막·힘줄 선택 시에만 불러온다(`src/ui/StructureCard.tsx`).

## 뼈대와 연조직 변형 (로드맵 M1·M2)

```bash
blender --background --factory-startup --python atlas-data/pipeline/build_rig.py    # → runtime/rig.json (약 12초)
blender --background --factory-startup --python atlas-data/pipeline/build_skin.py   # → za-v2/skin/*.bin (git 제외, 약 18초)
```
- `build_rig.py`: 분절 22개·관절 21개. 계층·범위는 OpenSim Rajagopal2016, 중심·축은 ZA 뼈 표면 맞춤(주석에 방법·접촉 실측).
- `build_skin.py`: 연조직(근육·힘줄·인대·근막·혈관·신경) 정점마다 두 분절 가중치. 실제 런타임 chunk를 읽으므로 형상 chunk를 다시 만들면 이것도 다시 실행한다.
- 앱: `src/viewer/rig.ts`(자세 → 분절 변환), `src/viewer/skin.ts`(CPU 선형 블렌드). 개발용 콘솔: `window.__atlasRig`.

## 근육 작용 (로드맵 M3)

```bash
python3 atlas-data/pipeline/build_actions.py   # → runtime/muscle-actions.json + anatomy/muscle-action-checks.json (1초 미만)
```
- 표: `muscle_actions.py`(`ACTIONS` 근육 → rig 자유도·방향·주/보조, `OUTSIDE` rig에 없는 움직임, `OPENSIM` 대조용 모델 근육 이름).
- 대조: `opensim_moment_arms.py`가 `OpenSim_Models/`(읽기만)의 경로점으로 모멘트 팔을 계산. 근육 전체 평균, 모형의 한 부분, 엉덩 45° 굽힘 중 하나라도
  부호가 맞으면 일치(근거는 sidecar `agreedBy`). 어느 쪽도 안 맞는 작용은 런타임에서 빠진다.
- 앱: `src/viewer/movement.ts`, `src/viewer/wholeBody/MovementPanel.tsx`(관절 움직임 창), `src/ui/MuscleRigActions.tsx`(근육 기능 탭).

## 부착 면 (로드맵 C4)

```bash
python3 atlas-data/pipeline/build_attachments.py                                                   # ZA 패치 → runtime/attachments.json
blender --background --factory-startup --python atlas-data/pipeline/build_attachment_contacts.py   # 접촉 추정 면 추가 (약 50초)
```
- 두 번째는 첫 번째 결과에 행을 더하므로 항상 순서대로 실행한다. 형상 chunk를 다시 만들면 둘 다 다시 실행한다.
- 앱: `DatasetSceneAdapter`(뼈 위 면), `src/ui/AttachmentAreas.tsx`(근육 카드 목록).

## 근육 카드 (로드맵 C2)

```bash
python3 atlas-data/pipeline/build_muscle_cards.py   # → runtime/muscle-cards.json + anatomy/muscle-card-checks.json (처음엔 Wikipedia 약 190쪽 받음, 이후 캐시)
```
- 표: `muscle_content.py`(`NERVES`·`ARTERIES` 용어표와 정보상자 문구 패턴, `CONCEPTS` 근육별 신경·분절·동맥·작용, `PARTS` ZA 이름 → 근육, `TENDONS`).
- 비교: Wikipedia 근육 정보상자의 nerve·blood·action 칸. 두 출처가 함께 말한 값만 런타임에 넣고 나머지는 checks 파일의 `exceptions`.
  초안을 Wikipedia에 맞춰 고치지 않는다(독립성). 고칠 수 있는 것은 문구 패턴·쪽 제목 같은 읽기 문제뿐.
- 앱: `src/ui/MuscleCardFacts.tsx`(운동신경·혈액공급·작용 요약).

## 혈관 (로드맵 Q2-1)

```bash
blender ... --python atlas-data/pipeline/extract_za.py        # 위 1번과 같음(심혈관 컬렉션 5 포함, 약 100초)
python3 atlas-data/pipeline/build_runtime_v2.py
python3 atlas-data/pipeline/verify_names_kmle.py && python3 atlas-data/pipeline/names_ko.py && python3 atlas-data/pipeline/build_runtime_v2.py
blender --background --factory-startup --python atlas-data/pipeline/build_skin.py   # 혈관도 rig를 따라감
python3 atlas-data/pipeline/build_muscle_cards.py                                    # 근육 혈액공급 → 혈관 연결
```
- 분류(`za_classify.py`): Bonus 컬렉션의 동맥·정맥 묶음, 이름(정맥굴·대정맥 등) → `artery`·`vein`, 심장 방·실·판막·꼭지근 → `heart`,
  심장 표면 표지(고랑·끝·모서리) → `heart_landmark`(표시 안 함). 곡선은 신경처럼 bevel 관(굵기 = bevel 0.5mm × 점 반지름).
- ZA 혈관 관은 지나치게 잘게 나뉘어 있어 혈관만 낮은 비율(overview 3–12%, detail 15–60%, detail은 허용 오차의 1/3)로 줄인다.
  다른 계통의 형상·chunk는 바뀌지 않는다(재추출 후 2,660개 전부 동일 확인).
- 한국어 이름: `vessel_names_ko.py`(혈관 이름 표 + 좌우·허파 구역·'~의 ~가지' 조합 규칙), KMLE 사전 대조 후 사전 값 우선.
- 앱: 층 `혈관`(동맥 빨강·정맥 파랑·심장), `src/ui/MuscleCardFacts.tsx` `VesselCard`(혈액을 받는 근육).

## 범위 밖 (이번 추출에서 제외)
림프(6)·내장(8)·부위(9) 컬렉션, 라벨 지시선(`.j`·`.i`), 계통 합본(`.g`), 글자 객체.
