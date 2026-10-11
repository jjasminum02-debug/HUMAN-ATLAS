# AT1 — WHO 361혈 코드·한글명·소속·laterality 원장

2026-10-11 · **AT1 catalog/laterality 범위 완료.** AT1은 14경맥의 361개 고유 코드와 KMCRIC 한글명·소속을 source-only 원장으로 고정했다. 위치 anchor·좌표·경로·영역·learner projection은 만들지 않았다. 경혈 기능 전체나 361개가 실제 장면에서 표시된 것으로 보고하지 않는다.

## 결과와 계수

| 경맥 | 코드 범위 | 개념 | instance 규칙 | 계획 instance |
|---|---|---:|---|---:|
| 폐경 LU | LU1–11 | 11 | 양측 | 22 |
| 대장경 LI | LI1–20 | 20 | 양측 | 40 |
| 위경 ST | ST1–45 | 45 | 양측 | 90 |
| 비경 SP | SP1–21 | 21 | 양측 | 42 |
| 심경 HT | HT1–9 | 9 | 양측 | 18 |
| 소장경 SI | SI1–19 | 19 | 양측 | 38 |
| 방광경 BL | BL1–67 | 67 | 양측 | 134 |
| 신경 KI | KI1–27 | 27 | 양측 | 54 |
| 심포경 PC | PC1–9 | 9 | 양측 | 18 |
| 삼초경 TE | TE1–23 | 23 | 양측 | 46 |
| 담경 GB | GB1–44 | 44 | 양측 | 88 |
| 간경 LR | LR1–14 | 14 | 양측 | 28 |
| 임맥 CV | CV1–24 | 24 | 정중 | 24 |
| 독맥 GV | GV1–28 | 28 | 정중 | 28 |
| **합계** | **14경맥** | **361 고유 코드** | **309 양측 + 52 정중** | **670 계획 side instance** |

한글 표기는 2026-10-11에 확인한 [KMCRIC 표준경혈 DB](https://www.kmcric.com/knowledge/acupoint_map)의 경맥별 code list에서 옮겼다. 그 DB는 WHO/WPRO 표준 위치를 바탕으로 한다고 설명하며 각 경맥 페이지를 연결한다. 코드/361 명명 체계는 [WHO의 361 classical acupuncture point names 자료](https://www.who.int/publications/i/item/9290611057)와 AT-361 설계의 선언 범위를 함께 참조했다. 경맥별 직접 URL은 `atlas-data/acupoints/who-361-catalog.json`의 `sourceRegistry`에 있다. 이름의 source transcription은 혈위 위치나 인체 해부학 검토를 뜻하지 않으며, 재배포 권리는 held로 두었다.

## 기존 AC1·AC2 이관

AC1/AC2 보고서와 실제 validation/learning JSON을 대조했다. AC2의 11개 오른쪽과 11개 왼쪽 proposal을 각 `code × side`로 이관표에 기록했다. AC1의 오른쪽 LU1/LU9/LU11 세 기록은 역사 predecessor로 연결했다. 기존 좌표와 geometry를 새 catalog에 복제하지 않고 원본 evidence path, revision, carrier hash만 참조한다.

| 선행 | proposal | 위치 검증 | 교수 검토 | 제품 승인 |
|---|---:|---|---|---:|
| AC1 우측 LU1/LU9/LU11 | 3 | unresolved | not performed | 0 |
| AC2 우측 LU1–11 | 11 | unresolved | not performed | 0 |
| AC2 좌측 LU1–11 | 11 | unresolved | not performed | 0 |
| **AC2 이관 합계** | **22** | **22 unresolved 유지** | **not performed** | **0** |

AC2 carrier hash는 오른쪽 `82991216229e5332bdd53c5e092341373a8b9b7ad8482ebfe99fe4194487a69a`, 왼쪽 `23c60b5d92a4b4370d40150496470ddffcf7b4e4a132bb1fccf3969188f9a42c`다. 이관표의 22개 모두 `aiProposal=true`, `locationValidation=unresolved`, `professorReview=not_performed`, `acceptedProductPoint=false`이며 원래 AC2 evidence는 수정하지 않았다. AC2 validation도 `acceptedProductPointCount=0`, `reviewProposalPointCount=22`로 남아 있다.

## 재사용과 화면 evidence

- 기존 `schema.ts`의 `PointConcept`, `PointInstance`, `ChannelRoute`, `Territory`, `Side`와 `anchorAdapter.ts`의 frame/hash/triangle anchor 규칙을 재사용 대상으로 확정했다. AT1 catalog는 위치가 없는 개념 원장이므로 완전한 `PointConcept`나 가짜 anchor를 만들지 않는다.
- `AcupunctureOverlay.ts`의 기존 single-root overlay와 `CameraSessions` camera ownership을 유지한다. `tour.ts`의 기존 `PointTour`도 재사용 대상으로 보존한다. 현재 overlay/tour의 실제 순서는 LU1–11 전용이므로 AT1에서 일반화하지 않았다. 새 scene, renderer, 모델, tour는 없다.
- 현행 보기옵션의 실제 화면은 `work/evidence/acupoint-at-plan-2026-10-11/view-tools.png`를 참조한다. 연결된 validation은 `observationMenuRemoved=true`, `screenFitKept=true`다. AT1은 관찰 시점 메뉴를 되살리거나 보기옵션을 다시 디자인하지 않았다. 기존 AC2 실제 LU1 화면도 reuse evidence로 연결했으며, 메뉴 제거 전 캡처임과 현재 361 UI를 입증하지 않는다는 제한을 분명히 기록했다.

## 검증, 미완과 다음 경계

`work/evidence/AT1/build_and_validate_ledger.py`가 원장을 만들고 실행 시점의 AC1/AC2 evidence 및 재사용 계약 파일을 검사한다. 결과는 `work/evidence/AT1/validation.json`이다.

- 경맥 코드 범위 14개, 총 361개 코드, unique 361, 누락 0, 중복 0, 예상 밖 코드 0: **pass**.
- laterality: 양측 개념 309개, 오른쪽 309·왼쪽 309, 정중 개념/instance 52개, 합계 **670 계획 side instance**: **pass**.
- AC1/AC2 이관: 22 proposal crosswalk, 누락·중복 0, 승인 0, unresolved 22: **pass**.
- 기존 schema/anchor/overlay/CameraSessions/tour의 실제 파일과 핵심 symbol 확인: **pass**. app runtime code는 바꾸지 않았다.
- `python3 work/tools/sync_execution.py`: `Updated 0 execution views`; `python3 work/tools/sync_execution.py --check`: **pass**. 현재 EXECUTION 투영 문서는 이미 일치했다.
- 범위 밖 실제 배치 상태: AT1에서 생성한 anchor 0, 제품으로 승인된 경혈 0, 이번 ledger의 learner 표시 0/670. AC2 개발 검토 제안은 22개이며 실제 위치 검증은 미해결이다. 이는 AT1 원장 완료와 별개다.
- 미완 위치/표시 unit은 다음 task의 대상이다. 특히 AT2는 전신 체표 취득·정합 경로 결정이며 아직 실행하지 않았다.

**경과 시간:** 약 20분으로 추정. 시작 시각을 별도 계측하지 않아 정확한 분 단위는 보장하지 않는다. 80분 상한에 도달하지 않았고, 시간만 채우기 위해 대기하지 않았다.

**다음 ID: AT2. 자동 실행하지 않았다.** 다음 프롬프트는 `work/tasks/AT2.md`다. push·배포·진단·치료·침 시뮬레이션은 없었다.

## 보존과 커밋

시작 HEAD와 5,965개 기존 Git status 항목의 요약은 `work/evidence/AT1/preservation-before.json`에 기록했다. 이 task는 그 이전 변경을 staging하지 않는다. OpenSim_Models, source cache, T13 drafts, AC1/AC2 역사 evidence, 보기옵션 UI, 그 밖의 기존 사용자 WIP를 수정하지 않았다.

- **Primary artifact/EXECUTION commit:** selective commit 후 hash를 여기에 기록한다.
- 포함 예정: WHO 361 source catalog, AT1 validator와 evidence, 이 보고서, `work/EXECUTION.json`의 AT1 record와 feature plan nextUnit 변경.
- 제외: 시작 시점의 나머지 사용자 WIP, 기존 `OpenSim_Models`/source cache/T13 및 AC1·AC2 history.
- 다음 프롬프트: `work/tasks/AT2.md` (미실행).

전체 `git diff --check`는 이 task 시작 전부터 수정 상태였던 `work/NEXT.md:8`의 EOF 빈 줄을 보고했다. 해당 생성 파일은 AT1 소유 변경이 아니어서 보존했다. AT1 소유 파일은 staged diff에서 별도로 공백 검사를 한다.
