# AT10 완료 단계와 실행 프롬프트 — 2026-10-14 r2

기준 HEAD: `d187148cfff2281bb4360fb1a7538c029eeaebc3`.
이 문서는 사용자의 “다음 AT10 완성을 위한 단계를 정리하고 이를 프롬프트로 남길 것” 요청에 따른 **계획**이다. 이번 문서 작성으로 geometry/learner/AT10 acceptance를 올리지 않는다. 구현·자산 생성·다음 단계 실행은 하지 않았다. 실행 상태는 언제나 최신 `work/EXECUTION.json`이 우선한다.

AT10의 기존 `skin-fit → skin-runtime → existing-package-reconciliation` 순서를 유지하면서, 실제 실패 부위를 아래 8개 실행으로 나눈다. F/R/C는 AT10 내부 산출물 구분이며 새 AT task를 만들지 않는다. **현재 붙여 넣을 것은 [01 F1 오른발](01-F1-RIGHT-FOOT.txt) 하나다.** 앞 단계가 실제 통과해야 다음 파일을 사용한다. 실패하면 같은 unit을 구체적 잔여 주소로 재개하며 번호를 넘기지 않는다. 프롬프트를 모두 한 번에 실행하지 않는다.

## 1. 현재 기준과 다시 하지 않을 일

| 항목 | 현재 실제 결과 | 이번 계획에서 보존할 것 |
|---|---|---|
| 전체 피부 | accepted0, geometry=false, product `registeredSkin=null` | r22의 역사648-reference native3,874/self1,604를 그대로 보존 |
| 양손 | r41 양측 국소 contact native0/self0 | 전신/피부 지표 합격과 구분하고 후속 변경 때 영향 범위 회귀 |
| 오른발 r56 | 전체834 raw2,391/self1,334; 오른발 raw513 / 유효 참조21면 | 발끝이 각지고 접혀 **미채택**. 21면만 지우면 끝이라고 해석하지 않음 |
| 오른발 r58 | 전체834 raw2,624/self1,334; 오른발 raw730 / 유효 참조228면 | 원형 prior와 관통의 충돌을 보여 주는 미채택 대안 |
| r60/r61 | dense source-shape 초기장에 비양의 J 표본4개, GLB 없음 | 제5발가락 source query와 인접 centroid는 **실패 진단 주소**, 혈위/landmark가 아님 |
| fascia 분리 | 사용자 승인된 오른쪽 Crural fascia991면 / 나머지9,884면 유지 | 정확한 source/hash/triangle 정책만 적용. raw834 검사·원본은 그대로 |
| loader pose | r41p1/r56p1/r58p1의 canonical frame0 metadata 수정 완료 | 동일 binary geometry의 review 사본이며 정합 합격 아님. 오류 수리를 반복하지 않음 |
| 기존108개 | LU22 + LI40 + TE46, 교육용 개략. 전체점 encoded 합계20,865,643bytes | 기존20MiB 내 여유105,877bytes. 이미 해결한2,441bytes 오류를 다시 수리하지 않음 |
| 피부+108개 | 현재 사본 단순 동시 추가는21,492,219bytes | 20MiB보다520,699bytes 초과. 최종 피부/전달 방식에 따라 다시 실측 |
| 콘텐츠/미표시 | Luna `738316a`의361 추출/116 대조 완료. HT18+PC18+SI38+ST50=124 미표시 | 자료 대조를 다시 만들지 않고 위치·내용 반영을 독립 검증 |

새 MakeHuman/ZA Skin/Dermis 검색, source 재다운로드, MV2/AT1–8/20–22 전수 조사, 완료된 원문 추출을 반복하지 않는다. source/helpers/UV/original IDs/native/OpenSim_Models/T13/기존 WIP와 역사 evidence는 보존한다. 기존59개 기술 검사 통과는 피부 정합 합격이 아니다.

## 2. 순서·산출물·다음으로 넘어가는 조건

| 순서 | AT10 내부 단위 / 기존 담당 | 실제 할 일 | 반드시 남길 산출물과 합격 기준 | 실행 프롬프트 |
|---|---|---|---|---|
| 1 | F1 오른발 / Sol xhigh | source 단면·toe-pad·web와 native 골격/힘줄 경계 관계를 작성하고 국소 변형을 수정 | ordered 대응/경계, recipe delta, emitted GLB/mapping, 유효 참조의 의도하지 않은 교차0·국소 self0·양의3D 변형·자연스러운 발끝·seam/간격·unit 밖 보존을 함께 통과 | [01](01-F1-RIGHT-FOOT.txt) |
| 2 | F2 왼발 / Sol xhigh | 통과한 방법을 실제 left source/native로 실행 | 좌우 별도 주소와 GLB 검사. mirror 결과나 오른쪽991면 목록을 검증으로 대체하지 않음. F1/양손 보존 | [02](02-F2-LEFT-FOOT.txt) |
| 3 | F3 머리·귀·목 / Sol xhigh | 성인 얼굴 recipe, 귀 attachment/helix/concha, 목 collar, eyelid/oral return 정합 | 앞/양측/후면 및 근접; 외피 결함과 의도된 개구부/점막을 분리. 실제 native/self/변형/형태/neck seam 통과. 원본 없는 점막은 지원 목록에 명시 | [03](03-F3-HEAD-EAR-NECK.txt) |
| 4 | F4 겨드랑·샅·잔여 seam / Sol xhigh | 위팔–몸통과 골반–샅–넙다리, 종아리/발목 등 잔여 교차 해결 | 경계 위치·접선/법선·간격·양의 변형·native/self와 자연스러운 형태 통과. 앞서 성공한 손/발/머리 회귀 | [04](04-F4-AXILLA-GROIN-SEAMS.txt) |
| 5 | F5/F6 전신 동결 / Sol xhigh | 국소 delta를 한 피부 자산으로 통합하고 교육 지표/recipe 확정 | final emitted 전체834 raw/유효 참조/self 검사, 전신/필수 근접 실제 앱, fresh-directory 재현, source↔derived/UV/helper/좌우/frame/pose/hash. 부위 합격 수의 합으로 전신 합격을 대신하지 않음 | [05](05-F5-F6-WHOLE-SKIN-FREEZE.txt) |
| 6 | R1 전달·공유 carrier / Sol xhigh | 통과 자산을 공통 loader/overlay/territory에 연결하고 동시 예산 해결 | 한 canonical topology/공유 geometry·버전별 주소 계약, 취소/dispose, 모드별 실제 encoded/CPU/GPU/triangle 비용. 20MiB/96MiB/1M/8MiB 유지 | [06](06-R1-SHARED-CARRIER-DELIVERY.txt) |
| 7 | R2 피부 버튼·접촉·실앱 / Sol xhigh | 기존 부분 UI/상태를 통과 피부에 연결하고108개 피부 anchor를 검증·이행 | 작은 접촉 glyph, 피부 OFF 때 좌표 유지/국소 단서, 선택·레이어·카메라 보존, static/motion guard, G1–G8 관련 회귀와390/1024/1440 실앱. 피부가 실제 연결되기 전 pass 금지 | [07](07-R2-SKIN-CONTACT-APP-QA.txt) |
| 8 | C1 기존124개와 AT10 마감 / Luna Max | AT9 HT/PC/SI74와 ST1–25 양측50의 규칙·피부 주소·경로·카드 연결 | 124개 전수 input/display/unresolved 대조, 기존108개 회귀, ST50 실제 표시·선택·side·경로·내용·최종 예산. 단계별 합격 근거가 모두 있을 때만 AT10 acceptance 변경 | [08](08-C1-PACKAGE-RECONCILIATION-AND-CLOSE.txt) |

담당은 기존 분장을 유지한 것이며 이번 문서가 새 agent 실행이나 위임을 승인하지 않는다. 사용자가 해당 프롬프트를 실행할 때 그 unit만 수행한다. 예정된 다음 AT는 AT11이지만 AT10 미달이면 feature plan nextUnit은 AT10으로 남긴다. AT30/31은 planned를 유지한다.

## 3. F1을 같은 실패의 반복으로 만들지 않기

현재 문제는 입력 전체가 없거나 교수 검토가 없어서가 아니라 **source 단면/경계 대응과 변형 구현이 함께 충족되지 않은 것**이다. r56 접촉 최소화, r58 형태 prior, r59 세분화, r60/r61 dense field의 실패를 서로 다른 원인 후보로 다룬다. r60/r61의4개 음의 J가 r56의21면 전체 관통 원인이라고 단정하지 않는다.

다음 구현의 권고 방향은 **source 발의 ordered 단면과 ankle boundary를 보존하는 국소 cage/patch 정합**이다. 이는 아직 구현·검증된 해법이라는 주장이 아니다. 제5발가락–MTP/web처럼 실제 실패 주소가 있는 작은 구역에서 먼저 변형·접촉·형태를 함께 검증하고 같은 국소 방법을 오른발에 확장한다. 현재 sparse joint RBF의 weight/normal push만 바꾼 새 revision을 반복 생성하지 않는다.

source 피부는 피부 구조/단면의 근거이고, native 뼈·힘줄은 자세·축·포함/간격 제약의 근거다. 서로 다른 조직을 동종 피부 표면으로 주장하지 않는다. source의 dorsal/plantar/heel/MTP/toe-pad/web별 original face/edge 순서와 각 native 경계 sourceKey/triangle/barycentric·역할·side·frame·pose·hash를 기록한다. 원본에 없는 주름/web 기준은 근거 있는 AI 교육 지표로 작성할 수 있지만 원본 관찰로 바꾸지 않는다. nearest/ray는 이미 정한 역할 안의 정합 도구다.

새 방법은 선택한 체적 cell 또는 실제 3D field derivative, 경계 위치/접선, source 내부와 경계 근처의 적응 표본, emitted native/self 검사를 함께 갖춰야 한다. 유한 표본 양성·surface-prism 수치만으로 전역 양의 변형을 주장하지 않는다. non-finite, QP 잔여 위반/미수렴, 뒤늦은 self 증가를 거부·보고한다. 검사기는 후보를 수정하지 않는다.

기본은 현재 source topology 보존이다. 실제 topology/대응 결함이 입증된 **국소** 구역만 derived revision에서 재구성할 수 있다. source face/barycentric 계보·UV corner·original IDs mapping과 비용을 남긴다. r59 실패를 “해상도만 올리면 된다”의 근거로 쓰거나 새 전신 조형으로 확대하지 않는다. 실패 원인 분류 없이 normal push/nearest/세분화/숨김/전신 scale을 되풀이하지 않는다.

## 4. 합격과 참조 분류

모든 geometry unit은 동일한 검사 계약을 쓴다. `raw834 전체 교차`, `승인 정책으로 분리한 면의 교차`, `나머지 유효 참조의 의도하지 않은 교차`, `self`, `3D 변형`, `seam/간격`, `실제 외관`을 별도 수치/주소로 저장한다. raw 교차가 남았다는 이유로 승인된991면 분리를 무효화하지도, 그 분리를 이용해 다른 뼈/힘줄/fascia 결함을 감추지도 않는다.

오른쪽 정책은 정확한991면에 한정된다. 왼쪽은 실제 source/native와 기존 승인 범위를 대조해야 하며 자동 대칭 예외를 만들지 않는다. 범위 밖의 새 참조 예외는 구체적 주소·화면·근거와 별도 결정으로 남긴다. 그것을 전신 입력 부재나 모든 기능의 사람 승인 대기로 확대하지 않는다. 성공 위치/국소 자산은 다른 unit 실패와 독립 보존한다.

피부 geometry 통과와 경혈 위치 통과도 별개다. F5/F6의 통과는 runtime에 사용할 피부 입력을 확정하는 단계이며 제품 import·경혈 위치 수를 올리지 않는다. 기존 p1 metadata 사본을 이름만 바꿔 통과 자산으로 쓰지 않는다.

## 5. Runtime과 콘텐츠의 구체적 경계

- 이미 있는 `skin/SkinLayer`, `SkinLayerState`, `skinContract`, `skinReviewAsset`, `acupoints/carrierLoader`, compiler/anchor adapter/overlay/territory editor/tour/CameraSessions를 재사용한다. DEV preview 동작만으로 제품 완료를 세지 않는다.
- R1은 520,699bytes를 임의로 빼는 문제가 아니다. 최종 자산 기준으로 모드별 중복 canonical/legacy carrier를 제거·지연 전달하고 기존 공통 무손실 전달/공유 cache/ref-count 해제를 해결한다. decoded hash/address를 보존하고 최종 C1의 추가 데이터까지 다시 측정한다. 근육/뼈 삭제·전체 예산 증액은 금지한다.
- R2에서 기존108개를 새 carrier ID로 일괄 치환하거나 nearest muscle/피부 ray hit만으로 위치를 승인하지 않는다. 기존 package를 보존한 새 migration revision에서 각 code+side의 landmark/문헌 관계와 새 triangle+barycentric를 검증하고 old→new 위치/주소 차이를 기록한다. 새로운 근거가 없으면 정밀 위치로 올리지 않는다. 피부 ON/OFF 사이에는 이 검증된 동일 anchor를 유지한다.
- skin anchor migration으로 주소가 바뀌는 작업과 AT22 mask 편집 회귀를 구분한다. **같은 carrier revision에서 mask만 수정할 때** point/route/carrier hash가 불변이어야 한다. 새 carrier 이행에는 별도 mapping과 새 mask revision을 작성하고 기존 LU mask도 실제로 함께 확인한다. 14개 영역을 새로 제작하지 않는다.
- 피부 버튼은 이미 자리만 존재한다. 통과 자산으로 활성화하는 것은 요구사항이다. 기존 보기옵션 배치·홈·로딩·카메라 정책은 바꾸지 않는다. static reference pose만 지원하고 motion 시작 시 고정 피부/점을 해제한다. 취혈자세 구현은 하지 않는다.
- C1은 기존 Luna 자료를 재사용한다. 원문 추출361/사실 대조116, 설명 반영, 실제 표시 instance, 교육용 개략/정밀, 교수 검토, 공개 권리, 자세 지원을 분리한다. 기존108+신규124가 모두 통과해도 이 범위는232 instance이며 361혈/670 instance 완성이 아니다.

## 6. 모든 실행의 기록과 AT10 최종 마감

각 실행은 시작 HEAD/status/입력 hash·소유 경계를 남긴다. 앞 unit의 최종 manifest/hash와 실제 통과 evidence를 입력으로 쓰며 최신 결과가 이미 합격이면 재실행하지 않는다. 변경된 입력만 영향 범위 회귀한다. 새 versioned report/evidence에 적용/미적용 후보, before/after 실제 앱, raw 주소·비용, 정확한 remaining unit을 남긴다. 현 단계 밖 작업으로 자동 이동하지 않는다.

종료 전에 최신 EXECUTION을 다시 읽고 담당 하위 결과/연결만 병합한다. 숫자 T/AC/MV·다른 AT·기존 result/Luna/역사 acceptance를 덮지 않는다. C1의 AT9 연계 갱신은 그 기존 지정 범위만 실제 근거와 함께 병합한다. `sync_execution.py`와 `--check` 후 소유 파일만 로컬 commit하고 hash·포함/제외·잔여 변경을 기록한다. 시간 경과나 후보 수를 합격·종료 기준으로 쓰지 않는다.

AT10 최종 acceptance는 다음이 모두 실제로 충족될 때만 true로 바꾼다: F1–F6 전신 피부/지표/재현, R1/R2 단일 장면 제품 피부·108접촉/회귀·예산/상태, C1의124개 지정 입력 대조와 ST50 실제 위치/경로/카드·최종 회귀. 미확정 geometry/위치가 있으면 해당 unit과 AT10을 partial로 남긴다. 선택적 교수 검토/public held/동적 자세 미지원은 자동 기술 차단도 자동 승인도 아니다.

## 근거와 기존 문서

- [최신 실제 보고서](../../../reports/AT10-completion-2026-10-14-r1.md)
- [summary](../../../evidence/AT10/2026-10-14-completion-r1/summary.json), [remaining units](../../../evidence/AT10/2026-10-14-completion-r1/remaining-units.json), [승인된991면 분리](../../../evidence/AT10/2026-10-14-completion-r1/authorization-r1.json)
- [r56 실제 앱](../../../evidence/AT10/2026-10-14-completion-r1/screens/actual-r56p1-feet.png), [r58 실제 앱](../../../evidence/AT10/2026-10-14-completion-r1/screens/actual-r58p1-feet.png), [field 실패 ledger](../../../evidence/AT10/2026-10-14-completion-r1/attempt-ledger.json)
- [기존 r2 상위 설계](../REVIEW-AND-DESIGN.md), [후속 AT 순서](../PROMPTS-IN-ORDER.md), [이전 완료 계획 — 역사 상태](../AT10-REMAINING-COMPLETION-PLAN-2026-10-14.md)

이 r2가 AT10의 현재 재개 단계/프롬프트를 구체화한다. 이전 계획·실제 report/evidence를 삭제하거나 합격 상태를 바꾸지 않는다. push/배포/자동 위임/다음 AT/진단·치료·침 시뮬레이션은 금지한다.
