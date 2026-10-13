# AT9 — 심경·심포경·소장경 위치 조사 및 learner 연결

2026-10-13 · Luna Max · **partial — acceptance not passed**. 이번 실행은 AT9만 다뤘다. 공통 package 등록과 실제 learner 선택·좌우 전환은 확인했으나, AT9의 점 위치를 고정할 해부학적 surface indicator가 부족해 74개 instance 모두 compiler가 미해결로 거부했다. 점을 표시하거나 교육용 위치로 승인하지 않았다.

## 범위와 시작 기준선

- 시작 HEAD: `6cbf333300a285876f39ec04e870ff68a3b448f1`.
- 시작 status snapshot: `work/evidence/AT9/2026-10-13-r1/start.json`의 SHA256 `bff8cb088ad858855892cbf4c461270500aa32e0d7b28de1d97aab7dcae42707`; 전역 기존 status entry 6,595개 중 AT9 소유 경로에서는 registry만 이미 수정 상태였고 report/package/observation은 새 파일이었다. 현재 AT9 소유 경로를 뺀 status set을 시작 snapshot과 비교해 6,595개 모두 status와 경로가 그대로임을 확인했다.
- 입력 hash와 수정 허용 경로: [start.json](../evidence/AT9/2026-10-13-r1/start.json), [frozen-input-hashes-r1.json](../evidence/AT9/2026-10-13-r1/frozen-input-hashes-r1.json). 실제 화면 QA는 격리 localhost 탭에서 진행했고 사용자 learner 탭은 사용하지 않았다.
- AT5·AT6·AT7·AT8의 공통 schema/compiler/loader/overlay/CameraSessions/tour와 단일 learner scene을 재사용했다. 경맥 전용 UI/renderer/camera/3D model은 만들지 않았다.
- 기존 AC1/AC2 및 22개 LU 제안 상태는 건드리지 않았다. 기존 `lung-r7`, `li-r1`, `te-r1` 등록은 그대로 두고 registry에 새 HT/PC/SI 항목만 뒤에 추가했다. LU 제안을 확정 위치로 바꾸지 않았다.

## 원장과 범위 검사

catalog 전체는 14경맥·361 고유 개념·670 계획 instance이며 중복/누락 검사를 통과했다. 아래 원장은 AT9 부분집합이다.

| 경맥 | 코드 범위 | 개념 | 양측 instance | 위치 확정/표시 |
|---|---|---:|---:|---:|
| HT 수소음심경 | HT1–HT9 | 9 | 18 | 0 |
| PC 수궐음심포경 | PC1–PC9 | 9 | 18 | 0 |
| SI 수태양소장경 | SI1–SI19 | 19 | 38 | 0 |
| **AT9 합계** |  | **37** | **74** | **0** |

전체 catalog code 범위 검사 결과는 [code-and-instance-check-r1.json](../evidence/AT9/2026-10-13-r1/code-and-instance-check-r1.json)에 있다. `361 unique concepts`, 309 bilateral / 52 midline / 670 planned instances, `missingTargetCodes=[]`, `duplicateCodeSideKeys=[]`; AT9에는 right 37 / left 37 / midline 0, code 누락·추가·중복 0이다.

37개 code와 한국어 명칭, 출처 위치 설명, 필수 해부 지표, 양측 source/carrier hash, 판정과 이유는 [point-ledger-r1.json](../evidence/AT9/2026-10-13-r1/point-ledger-r1.json)에 기록했다. 출처 관계는 [WHO acupuncture point standard](https://iris.who.int/bitstream/handle/10665/353407/9789290613831-eng.pdf)를 기준으로 하고 한국어 표기는 KMCRIC 주소를 대조했다. 교육용 설명·정밀 좌표·사람 검토·공개 권리는 별도 상태로 두었다.

## 해부 지표와 compiler 판정

[candidate audit](../evidence/AT9/2026-10-13-r1/carrier-and-source-audit-r1.json)은 AT8 upper-yang r18, AT6 lung r2, education r1 manifest를 hash로 고정해 실제 candidate를 대조했다. 넓은 hand/arm/trunk envelopes, 손목 patch, nail-fold, ear auricular region은 후보 carrier다. point-specific 부착 지표와 side별 surface address가 없으면 위치 규칙을 만족한 면으로 간주하지 않았다.

- 손바닥 및 손목 안쪽: HT8/PC8의 손바닥 주름·적백육제와 손허리뼈/MCP 지표, HT/PC wrist points의 손바닥쪽 힘줄·손목주름·콩알뼈 기준이 현재 runtime carrier에 연결되지 않았다. AT8의 등쪽·뒤쪽·가쪽 면을 손바닥으로 대체하지 않았다.
- 안쪽/뒤쪽 팔: HT1–3의 겨드랑오목/안쪽 위팔/안쪽위관절융기 및 PC2–3의 앞겨드랑·팔꿈치 지표가 넓은 envelope에 등록되지 않았다. SI6–8의 자쪽/팔꿈치머리·안쪽위관절융기 관계도 미등록이다.
- 견갑부: SI9–10 뒤겨드랑주름/어깨관절, SI11–15 견갑가시·오목·안쪽끝·척추 높이는 trunk/girdle candidate의 문맥만으로 점을 지정할 수 없다.
- 귀: SI19에 맞는 이주 앞면 중점·아래턱관절돌기 사이 관계와 입을 약간 연 자세가 없다. 기존 TE 귀 점을 SI19로 복사하지 않았다.
- 손끝: HT9/SI1의 다섯째 손가락 nail-fold 후보는 있으나 지정된 손톱 모서리와 연결된 point-local indicator가 없다. PC9의 패드 대 손톱뿌리 기준은 입력 자체가 미확정이며 손끝 패드 surface는 지원되지 않는다.

예를 들어 오른쪽 HT1 후보 `fossa-right-0`의 hash는 `594000005e9ca4a71ad13dcd4a478f3a3dca3f68a880be8b772bcfd82c5698bb`, 오른쪽 PC8 후보 `hand-right-0`은 `79582de4be7811e7d436b7b3e583507a3878361cbcf79f41571c3cc22e8a5e51`, 오른쪽 SI11 후보 `trunk-2`는 `9cb2dc086fe78b8982741223e7bac9bc2d235fe8e5e4ae59d86744757781dcc9`, 오른쪽 SI19 후보 `native-auricular-region-right-0`은 `558d740d41a0214aaf3eb2fbda1c19bda9ce1512e1bd426786951ac3bdd4d1c7`다. 모두 `candidate_only_not_registered_for_this_location`이며 승인된 projection은 아니다. instance별 해시와 이유는 원장에 있다.

공통 `explicit-landmarks-2.5` compiler와 AT8 `rules-r19.json` (`cadeead0088a30fe9b2d6368267e0f101f8a48be035abd7eec24d8fec43a1b53`)를 재사용했다. 74개를 시도했고 `passed=0`, `unresolved=74`; 전부 “unresolved; explicit anatomical landmarks required”로 거부됐다. 자세한 입력 hash와 결과는 [compiler-disposition-r1.json](../evidence/AT9/2026-10-13-r1/compiler-disposition-r1.json)에 있다. learner package에는 code/name/source location text/필수 지표/candidate hash/reason이 있지만 좌표나 projection은 0이고 observation path segment도 0이다.

## 실제 learner 화면

격리된 `http://127.0.0.1:5200/` learner에서 기존 전신 장면의 `경혈` 버튼으로 들어가 각 경맥을 선택했다. package registration과 code list는 모두 로드됐다.

- HT: HT1 극천을 오른쪽·왼쪽·양측으로 전환; 표시 수는 `0/9`, `0/9`, `0/18`이었다.
- PC: PC8 노궁의 양측 및 왼쪽 선택, PC6 내관 왼쪽 선택을 확인; `0/18`, `0/9`. 화면은 손바닥 지표가 없고 손등 patch/일반 envelope를 대체하지 않는다고 표시했다.
- SI: SI11 천종과 SI19 청궁의 왼쪽 선택, 양측·오른쪽 전환; `0/19`, `0/38`, `0/19`. 각각 견갑부 국소 표면과 SI19 이주/턱관절/입 벌림 지표가 없다는 이유가 화면에 표시됐다.
- 기존 overlay 표시를 끄고 다시 켰다. SI19 선택을 유지했다. SI19 → PC1 → SI19 channel 전환에서 선택은 돌아왔고 side는 오른쪽 기본값으로 바뀌는 것을 확인했다. 경혈 학습 panel을 닫자 기존 `전신 살펴보기` full-body scene으로 돌아왔다.
- CUA screenshot을 각 대표 화면과 panel 닫힘에서 실제로 표시해 육안 확인했다. 이 CUA session에는 이미지 파일을 workspace에 내보내는 지원 API가 없어 PNG 파일은 저장하지 않았다. UI 상태 발췌와 캡처 한계는 [ui-observations-r1.json](../evidence/AT9/2026-10-13-r1/ui-observations-r1.json)에 남겼다. 화면 캡처 파일이 있다고 주장하지 않는다.

모든 예시의 위치 마커가 0이므로 화면에서 점 대 해부 구조의 실제 가림/접촉을 판정할 수 없다. side selector, package selection, overlay off/on, channel 전환 및 panel 닫힘 복귀는 확인했으나 point occlusion은 미검증으로 구분했다. 실제 이미지 파일도 남아 있지 않으므로 AT9 인수 acceptance는 통과로 처리하지 않는다.

## 검증 결과와 남은 unit

- 14경맥/361개 개념/670 계획 instance, AT9 code-side 원장 검사: pass; 누락·중복 0.
- 새 package 검증: HT 9/18, PC 9/18, SI 19/38; 37개 concept와 74개 side instance; package code/name와 registry SHA 검사 통과; unresolved 74; projection 0.
- Shared compiler: 74 attempted / 0 passed / 74 unresolved, expected fail-closed disposition.
- 실제 learner: 세 registry package와 point lists를 로드하고 대표 selection/side/transitions 확인; point marker 0/N. 표시 가능한 위치로 검증된 instance 0.
- Code validation, learning-content validation 및 관련 learner registry/package/native placement tests: evidence 실행 기록 기준 통과. 최종 실행 결과는 [package-validation-r1.json](../evidence/AT9/2026-10-13-r1/package-validation-r1.json) 및 [validation-r1.json](../evidence/AT9/2026-10-13-r1/validation-r1.json)에 둔다.

정확한 남은 항목은 [remaining-units-r1.json](../evidence/AT9/2026-10-13-r1/remaining-units-r1.json)이다. 다음 조사/수정 단위는 미해결 양측 74 instance의 지표·surface address 취득과 shared compiler 재실행, marker가 생긴 항목만 실제 가림/국소 framing 확인, 지원되는 source-bound surface path 작성, versioned 화면 이미지 export다. 74개 모두가 표시 가능한 자연스러운 교육 위치라는 승인도, 정밀 취혈 좌표도 부여되지 않았다.

`professorReview=not_performed`, `textbook=pending`, `publicRedistribution=held`는 위치 판정과 별도다. 기술 입력이 없는 현재 상태를 자료가 존재한다거나 일반 승인 대기라고 쓰지 않는다.

다음 계획 ID는 AT10 (`work/tasks/AT10.md`, 위경 ST1–ST25)다. AT10은 시작하지 않았다. AT9 unresolved 74건이 남아 있으므로 다음 실행 시 AT9 남은 unit과 feature order를 먼저 대조해 결정해야 한다.
