# Z-Anatomy 추출 파이프라인 (로드맵 D1)

Z-Anatomy `Startup.blend` 하나에서 뼈·근육·관절/인대·근막·부착 면·신경을 구조당 GLB와 `structures.json`으로 뽑는다.
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

## 범위 밖 (이번 추출에서 제외)
심혈관(5, 곡선 654개 포함)·림프(6)·내장(8)·부위(9) 컬렉션, 라벨 지시선(`.j`·`.i`), 계통 합본(`.g`), 글자 객체.
