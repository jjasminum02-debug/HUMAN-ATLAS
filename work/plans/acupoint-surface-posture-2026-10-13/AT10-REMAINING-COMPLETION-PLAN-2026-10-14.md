# AT10 실제 미완과 완료 계획 — 2026-10-14

> **현재 실행은 [completion-r2 계획/프롬프트](at10-completion-r2/START-HERE.md)를 따른다.** 아래는 d187148 이전 상태의 계획으로 보존한다. 전체108개 예산 오류와 pose metadata 오류는 이미 수정됐으며 초기 source 확보/옛 수치를 재실행 근거로 쓰지 않는다.

확인 기준 HEAD `c66412364bf655352c997e84f79dc92056fa3caf`. 최신 EXECUTION, AT10 task/r2 계획, 실제 r22/r41/r54 파일 hash, r5 독립 검사/remaining-units/화면, 현재 learner registry를 대조했다. 이번 문서는 **계획과 현재 부분 구현의 점검**이며 skin-fit 또는 skin-runtime 합격 기록이 아니다. 사용자의 후속 요청에 따라 새 모델링·후속 기능 확대를 실행하지 않는다.

## 1. 지금 AT10은 끝나지 않았다

| 구분 | 현재 확인 결과 | 미완 |
|---|---|---|
| 피부 source/권리/단위/export | 확보됨. pinned MakeHuman core, source/helpers/UV/IDs, frame/pose, 재현 경로 존재 | 새 소스 수집을 반복할 이유 없음 |
| portfolio-content | Luna `738316a`, 361 추출 / 116개 사실 비교, 10 review / 2 conflict 보존 | learner 내용 반영과 위치 작성은 별도. 완료 결과 재작성하지 않음 |
| 전신 skin-fit | approvedFittedSkinCount=0, geometry=false | 아래 F1–F6 |
| 양손 contact | r41 양측 native0/self0, original source/field 재현됨 | 손 전체 외관·교육 지표 승인과 전신 합격은 아님 |
| 피부 runtime | 이번 부분 코드 작성·검사. 제품 registry는 null, 피부 버튼은 보이지만 비활성 | 통과 피부 등록·공유 carrier 연결·실제 화면 QA 미완 |
| 기존 실제 위치 | LU22 + LI40 + TE46 = **108** 교육용 개략 instance / 54개 개념 | 새 피부 주소로 migration/접촉 검증 0, 정밀 위치 0 |
| 미표시 package | HT18 + PC18 + SI38 = AT9의74, ST1–25 양측50 = AT10의50 | **124** instance의 위치/경로/내용 reconciliation |
| 취혈자세 | 현재 model pose support=0 | AT10 범위 밖. AT30/31 planned 유지 |

AT10의 본래 ST1–25 50개 위치도 아직0이다. 피부 버튼만 만들거나 기존108개를 등록했다고 AT10을 닫을 수 없다. AT9 74개는 기존 공동 reconciliation의 연계 범위이며 그 기록을 자동 승인하지 않는다.

### 파일별 실제 상태 — 숫자를 섞어 비교하지 않음

| 자산 | native 교차 피부 triangle / self pair | 판정 |
|---|---:|---|
| r22 `53b3a057…34b93` | 3,874 / 1,604, 옛648 reference | 기준 review checkpoint, 미합격 |
| r41 `52b23499…54e4d` | 2,773 / 1,604, 확장834 reference | 양손 local contact만 보존, 전신 미합격 |
| r54 `60a92ef8…1861` | 2,288 / 1,334, 확장834 reference | 미채택. 오른발410/self0, 실제 각진 발끝·잔여 관통 |

r41을 같은 옛648 reference에서 보면 native2,478이다. reference가 다른 수치를 단순 개선율로 비교하지 않는다. r54의 오른발 bone18/accessory406은14개가 중복되므로 합계424를410 대신 쓰지 않는다. accessory가 기본 OFF라는 이유로 검사에서 제외하지 않는다.

## 2. 왜 완성되지 않았나

1. **표면 의미 대응을 충분히 작성하지 못했다.** 관절 중심/rig helper/가까운 ray hit만으로 손발의 앞뒤·web·toe-pad·귀의 root/helix/concha가 결정되지 않는다. actual triangle 주소가 있어도 대응의 의미가 맞다는 증거는 아니다. 일부 발 guide는 실제 화면에서 web 대신 발가락 측면을 따랐으므로 미채택이다.
2. **실제 변형 구현 결함이 남았다.** 기존 solver가 국소 수치와 관통을 동시에 닫지 못했다. r5의 collision-aware line search는 손에서 성공했지만 발·머리·겨드랑·샅까지 해결하지 못했다. sampled positive Jacobian·작은 control residual·self0 하나만으로 전신 합격을 줄 수 없다.
3. **입력 해석 오류와 검사 범위 누락이 뒤늦게 발견됐다.** lesser toe의4번째 TIP 누락과 DIP→끝 역할 오류를 수정했고, 옛 이름 필터에서 빠진 근육149/뼈37을 보충했다. 수정 결과는 재사용하되 해당 수정이 모든 발/전신 문제를 해결했다고 해석하지 않는다.
4. **국소 성공을 전신 완료로 조립하지 못했다.** 손을 해결한 뒤에도 얼굴/귀/목, 겨드랑과 몸통, 골반/샅/넙다리 접합이 남았다. 현재 얼굴의 성인 체형·자연스러운 형태도 최종 검사가 필요하다. 전신 파일이 존재하는 것과 맞는 전신 외피가 존재하는 것은 다르다.
5. **runtime 제품 연결은 아직 부분 코드다.** `registeredSkin=null`, 기존 `carrierLoader`는 여전히 세 기존 registry만 읽는다. 원본 GLB를 읽는 class와 버튼만으로 새 피부 anchor/영역의 공유 canonical geometry가 연결되지는 않는다. opacity API, static guard, cancellation은 있어도 실제 피부와108개 접촉 QA는 아직 없다.
6. **실제 예산 미달이 있다.** 현재 앱 ‘전체 경혈’ 입력은 base20,042,516 + overlay931,445 = **20,973,961bytes**, 20MiB보다 **2,441bytes 초과**해 공통 guard가 표시를 거절했다. 현재 자동108개 binding 검사는 통과하지만 이 전체 표시 흐름은 통과하지 않았다. 과거 승인 결과를 삭제하지 않고 이번 실제 회귀 실패를 별도로 해결해야 한다.

교수 검토 대기, 소스 전체 부재 또는 라이선스 불명만으로 멈춘 상태가 아니다. 담당 구현의 표면 대응·변형·전신 검증·제품 전달이 미완인 것이다. 원본 수집/권리 조사/완료한 전수조사를 다시 하는 것으로 해결되지 않는다.

## 3. 실행 순서와 산출물

### F1. 오른발의 연속 표면 대응을 먼저 닫음 — 같은 skin-fit

입력은 r41의 보존 양손과 r54의 **진단**이며 r54 전체를 최종본으로 채택하지 않는다. 현재834 native와 수정된19개 right toe helper 역할을 재사용한다.

- 담당 AI가 dorsal/plantar/heel/MTP/toe-pad/실제 interdigital valley의 **source ordered face/edge band**를 작성한다. 각각 source original face/vertex ID, 해부 역할, native sourceKey/triangle/barycentric, side/pose/hash, boundary 순서·인접 band를 기록한다. 원본 관찰 구조와 작성한 교육용 control을 분리한다.
- 대응은 실제 원본/고정 native의 양측 표면에서 확인한다. nearest/ray는 이미 정한 역할의 band 안에서만 보조한다. extrema 또는 bone-bisector guide를 이름만 바꿔 승인하지 않는다.
- 손에서 검증된 실제 native/self collision 제약을 재사용하되, 발목 공통 경계·접선과 각 digit 소유 구역을 함께 고정/조정한다. 최적화와 독립 검사기를 분리한다. whole normal push/전신 scale을 반복하지 않는다.
- **산출물:** versioned right-foot surface-pair/boundary JSON, recipe delta, emitted GLB, native/self 원시 주소, gap/변형 검사, 발등/발바닥/발목/각 toe의 실제 근접 화면.
- **통과:** 해당 unit과 seam의 의도하지 않은 native/self 관통0, 발끝/발가락 사이 형태의 실제 적합성, 양의 국소3D 변형 검사, 부위별 간격 판정, 양손과 unit 밖 보존. 의도된 접촉은 실제 source 주소로 분류하며 원시 총수도 유지한다.
- 현재 topology로 자연스러운 형태를 만들 수 없는 **확인된 국소 구역만** 별도 derived revision에서 재구성한다. original IDs/face-corner UV 계보와 source↔new triangle mapping을 남기며 원본을 덮지 않는다. 새 전신 조형이나 source 재탐색으로 확대하지 않는다.

### F2. 왼발 — 실제 left 입력으로 같은 방식 검증

F1 방식이 통과한 뒤 actual left chain/native band를 작성한다. mirror는 초기 제안까지만 허용한다. baseline left native877/self271 및 ankle seam을 독립 검사한다. right/양손 성공을 byte/hash 또는 명시된 영향 범위로 보존한다. 산출물과 통과 기준은 F1과 같으며 양측 모두 실제 화면이 필요하다.

### F3. 머리·귀·목과 eyelid/oral return

outer cranial/face, pinna attachment/root/helix/concha/lobule, neck collar를 연결된 구역으로 작성한다. baseline head461/self527 주소를 실제 외피, source return, 의도된 개구부/접촉으로 나누되 가짜 제외를 금지한다. r27의 작은 control 오차나 r48의 self 개선을 귀 전체 성공으로 쓰지 않는다. 성인 체형 recipe를 확정하고 얼굴 외관도 검사한다. 구강/잇몸은 실제 기존 점막 구조 연결 계약을 만들며 외피에 대신 놓지 않는다.

**산출물/통과:** ordered surface pairs·return support 목록, 고정 native 위 actual emitted 정면/양측/귀·얼굴·목 근접, native/self·변형·목 seam 검사. 미지원 점막은 정확한 영역과 source 구조를 남긴다. 외피 결함을 점막 예외로 숨기지 않는다.

### F4. 겨드랑·위팔–몸통 / 골반·샅–상부 넙다리

두 묶음을 같은 native collision/boundary 계약으로 차례로 해결한다. arm L54/R54/trunk262의 native와 arm/trunk self272, groin30/leg L79/R79의 native와 self264를 실제 주소로 재개한다. 경계 위치뿐 아니라 접선/법선·피부 접촉·인접 구역의 변형까지 검사한다. 손/발의 이미 통과한 위치를 독립 보존한다.

**산출물/통과:** 각 연결부 공동 surface/boundary recipe, 원시/분류 교차 주소, front/back/oblique 실제 화면, 간격·양의3D 변형·unit 밖 회귀. 두 묶음 모두 실제 관통과 형태가 통과해야 F5로 간다.

### F5–F6. 한 전신 자산으로 통합·교육 지표 동결

- 성공한 local delta를 한 recipe로 조립하고 **최종 emitted GLB**를834 고정 reference 전체에서 검사한다. local patch 숫자의 합을 전신 검사로 대체하지 않는다.
- source body/helper 분리, original IDs/face-corner UV, mapping, dm→m 한 번, world transform 한 번, side/frame/reference pose/hash를 확인한다. logical source topology hash와 UV로 분할된 emitted topology hash를 혼동하지 않는다.
- 배꼽·유두·손톱·관절/주름 모형 지표를 original observation / AI-authored educational indicator / unsupported로 분리한 manifest를 작성한다. 없는 주름의 모형 지표 작성은 허용하지만 원본에 관찰됐다고 쓰지 않는다.
- 전신 정면/뒤/양측, 얼굴·귀·겨드랑·손목/손바닥/손가락·샅·무릎·발목/발바닥/발가락을 비교한다. 부위별 gap tolerance는 모델 QA 기준으로 먼저 적고 해부학적 피부 두께라고 부르지 않는다.
- 모든 geometry·형태·지표 검사가 통과한 **한 자산만** 새 디렉터리에서 독립 recipe 재현 후 GLB/manifest/mapping/landmark hash를 동결한다. 626,572bytes/26,756triangles는 현재 후보 비용이며 최종 비용은 다시 측정한다.
- 그때만 skinFit.geometryValidationPassed/learnerEligible을 실제 근거대로 변경한다. 지금은 둘 다 false를 유지한다.

### R1. skin-runtime 전달·공유 topology·예산

기존 부분 코드의 `SkinLayer`, `SkinLayerState`, contract, 공통 glyph/helper·territory schema를 재사용한다. 새 renderer/camera/clock 또는 경맥별 loader를 만들지 않는다.

1. 통과 F6 manifest를 제품 registry에 등록한다. 실제 GLB의 embedded acceptance, file hash, frame/unit/pose, 비용을 loader가 확인한다. 개발 r41 preview를 등록 슬롯에 복사하지 않는다.
2. `carrierLoader`와 overlay/editor가 **하나의 canonical reference geometry**를 빌리도록 연결한다. emitted triangle+barycentric를 고정하고 source/LOD mapping을 명시한다. LOD를 끄고 reference 한 벌을 유지하는 것도 유효하다. 기존108개 anchor를 새 carrier ID로 이름만 바꿔 재사용하지 않는다.
3. 전체점 2,441bytes 초과부터 실제 해결한다. 선택된 carrier만 읽기, manifest/learner/context의 중복 필드와 무손실 전달을 먼저 측정한다. gzip한다고 무조건 예산이 닫힌다고 가정하지 않는다. 이번 in-memory probe상 education813,096→505,232bytes이며 **이 절감만으로 피부까지 추가하기에는 부족**하다.
4. 추가 피부와 모든108개 data까지 필요한 mode별 합계를 다시 계산한다. topology/address를 그대로 보존하는 무손실 packing·필요 reference subset 전달·공유 GPU buffer를 적용한다. 부족하면 공통 delivery의 overview chunk 무손실 압축/해제·전송/복원 hash 계약을 같은 R1에서 해결한다. native 구조 삭제/예산 증액은 금지한다. encoded transfer, decoded CPU/GPU, active triangles를 별도 집계한다.
5. 기존20MiB overview /96MiB geometry /1M active triangles /8MiB chunk를 모두 통과해야 R2로 간다. old carrier와 피부 전체를 무조건 동시에 initial bundle에 넣지 않는다. 수학적 합계와 실제 transfer/residency를 구분한다.

### R2. 피부 버튼·상태·접촉·실제 앱 검증

- 기존 뼈/근육/신경 옆의 피부 버튼을 실제 통과 자산에 연결한다. 독립 ON/OFF, 경혈 첫 진입, 사용자 OFF 지속, 모드 종료 원래 상태, 선택/다른 레이어/카메라 보존을 검사한다.
- natural opaque matte, 필요 투명도는 기존 흐름과 연결한다. motion 시작 시 static 피부/anchor는 즉시 해제하며 fixed 좌표를 변형 모델 위에 두지 않는다. 취혈자세 구현은 이 단계에 추가하지 않는다.
- 공통 접촉 glyph의 실제 anchor/법선/작은 offset을 검증한다. 피부 OFF에서는 동일 anchor와 선택된 국소 체표/깊이 단서로 설명하며 nearest muscle로 이동시키지 않는다. 새 대표 point는 native/문헌/landmark→compiler→learner까지 검증하고 fixture는 제품 데이터에서 제외한다.
- AT21/22 mask/editor는 새 공유 carrier를 실제로 빌리는 기술 fixture로 검사한다. 기존 LU 제품 mask와108개 점은 자체 hash/좌표를 유지한다. 새14영역 제작은 범위 밖이다.
- **실제 앱 인수 표:** 390/1024/1440 각각 피부 전신/얼굴/귀/양손/양발; ON→OFF→ON; 경혈/지역/side 변경; 선택과 카드 가림; 빠른 취소/재진입; motion 시작/원상복귀; 경혈 종료/해부 선택 복원. 대표 LU1/LU5/LU9/LU11 양측과 LI/TE 시작·끝/예외, 전체108개 표시/선택 목록을 대조한다. `자동 binding108`과 `실제 화면 검사N`을 따로 기록한다.
- 실제 리소스 해제, 반복 전환, late completion, context loss와 OFF idle 비용을 측정한다. Blender 화면/수치검사를 learner 화면으로 대체하지 않는다.

### C1. existing-package-reconciliation — 별도 실행, 자동 실행 금지

F6/R1/R2 통과 후 Luna의 기존 portfolio 결과를 재사용한다. AT9 HT/PC/SI74와 AT10 ST1–25 50 =124개 instance에 native 지표·문헌 관계·공통 피부 주소·구간 경로를 작성한다. 기존108개를 함께 회귀하고 한국어 위치/탐색 방법을 기존 카드에 반영한다. 10 review/2 conflict는 각 코드의 실제 근거로 정리하며 일괄 승인·영구 전역 차단을 피한다.

입력124 / 실제 표시 / 교육용 개략 / 정밀 / 근거 부족을 각각 집계한다. AT10의50개와 공통 피부/runtime 인수 결과가 실제 충족되었을 때만 AT10 parent acceptance를 닫는다. genuine 미달 코드는 정확한 input/지표/지원 구조를 남기며 다른 외피로 옮기지 않는다.

## 4. 다음 한 실행과 중단 조건

**지금 가장 먼저 필요한 것은 F1 `AT10/skin-fit/right-foot-continuous-surface-bands`다.** 이번 계획 요청에서 실행하지 않는다. R1의 기존 전체점 예산 오류는 독립 기술 수리가 가능하지만, 그것을 피부 정합 완료로 세거나 C1을 앞당길 수 없다.

실행은 성공 단위별로 보존하고 새 실패가 기존 손·발 성공을 덮지 않게 한다. 종료는 실제 산출물/인수 검사로 판단하며 시간, 후보 revision 증가, 형식 재현 또는 사람 승인 대기를 완료 사유로 사용하지 않는다. 공통 원인이 달라진 증거 없이 같은 normal push/ray 자동 배정을 반복하지 않는다.

복사용 다음 프롬프트:

```text
HUMAN ATLAS에서 AT10/skin-fit의 right-foot-continuous-surface-bands만 수행해라.
AGENTS.md, 최신 AT10.skinFit/resumeUnit, AT10-skin-fit.md r5와
AT10-REMAINING-COMPLETION-PLAN-2026-10-14.md의 F1, r41/r54 실제 입력과 remaining 주소를 읽어라.
r41 양손 native0/self0을 보존하고 r54는 실패 진단으로만 재사용해라.
실제 source face/edge와 native sourceKey/triangle/barycentric에 dorsal/plantar/heel/MTP/toe-pad/진짜 web valley의 ordered surface-pair와 공통 ankle boundary를 작성해라.
기존19개 right toe helper 역할 수정과834 native를 재사용하고 source 재수집/전신 후보 자동 생성을 반복하지 마라.
관찰 구조와 AI control을 구분하고 native/self 관통·양의3D 변형·seam/간격·자연스러운 발끝을 함께 해결해라.
actual emitted GLB와 고정 native 근접 검증·versioned recipe/mapping/evidence·소유 변경 로컬 commit을 남겨라.
한 국소 성공을 전신 승인으로 바꾸지 마라. 원본/UV/helpers/IDs/native/WIP/역사 evidence를 보존해라.
피부 runtime/다른 fit 묶음/361점/취혈자세/카메라/UI/자동 위임/다음 실행/push/배포는 하지 마라.
```

## 근거

- `work/EXECUTION.json` AT10, `work/reports/AT10-skin-fit.md` r5, `work/evidence/AT10/2026-10-14-skin-fit-r5/{summary,remaining-units,scoped-checks-r41-r54}.json`
- r41 actual emitted screen sheets, r54 right-foot native role classification 및 실제 source/native guide 미채택 기록
- `work/evidence/AT10/2026-10-14-skin-runtime-r1/current-package-counts.json`, `actual-all-points-budget.json`, `lossless-delivery-feasibility.json`, 실제 앱 screenshot와 부분 구현 검사
- `PROMPTS-IN-ORDER.md` skin-fit → skin-runtime → existing-package-reconciliation. AT30/31 planned와 후속 순서는 유지한다.
