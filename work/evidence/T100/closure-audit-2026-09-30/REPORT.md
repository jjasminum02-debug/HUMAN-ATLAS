# T100 반복 병목 교정과 현재 판정

T100은 아직 **in_progress / partial**이다. 현재 nextUnit은 `resolve-target-representation-and-final-scene-qa`다. 현재 경로는 **409/542 target, 427/563 membership**이다. 133 target과 136 membership에는 경로가 없다. 경로가 있는 target도 부분 멤버만 연결됐을 수 있으며 전체 범위 합격률로 계산하지 않는다.

## 안 끝난 이유

1. 고정 source/교차표 안에서 이미 실패한 조사를 계속하는 작업 범위였다. A/B 135개 중 133개는 조사 결과만으로 해소되지 않았다. 다른 자료, 원본 부분 segmentation, 변이 표본, 그룹 전체 범위 또는 명시 좌우 근거가 필요하다. 후보 또는 route 없음은 실제 형상 부재 증명이 아니다.
2. QA가 전수 계획 대신 6–9개 표본 관찰과 긴 원장 작성으로 반복됐다. 최신 별도 visual-qa 작업도 6개 표본만 관찰했고 이미지 파일과 브라우저 응답 바이트 해시를 저장하지 못했다. 원장 전체를 출력하는 과정도 컨텍스트 재읽기 비용을 늘렸다.
3. 서로 다른 지표를 완료 조건처럼 섞었다. 현재 표시 가능 672/672 표면의 세 이름은 이미 있다. 남은 73개는 직접 한국어 용어 인용의 gap이다. 사람 검토 미수행, 공개 재배포 held, 정확한 GPU/VRAM/전체 프로세스 memory를 브라우저에서 읽지 못하는 상태를 로컬 표시 또는 새 반복 측정의 자동 차단 조건으로 삼지 않는다. 25/26 설계의 실제 frame/CPU geometry/cache 예산과 관찰된 결함은 계속 유지한다.
4. TA2:2261에서는 한 원본 객체의 좌우가 미확정이라는 이유로 독립적으로 오른쪽을 명시한 원본 객체까지 막혀 있었다. 원본·compiled object identity와 선언 좌우가 일치하는 한 표면의 제한된 경로는 독립적으로 처리할 수 있다.

앞선 고정 자료 조사·소량 QA 중심의 재개 프롬프트도 반복에 기여했다. 같은 입력을 계속 조사하는 추가 프롬프트는 이 잔여 문제를 해결하지 못한다.

## 이번 실제 변경과 검증

- `captureTargetSelection.mjs`는 실제 Chrome의 별도 임시 프로필에서 모든 concept/side/region 경로를 실행하고 세 이름 카드, selected/visible 상태, 단독 보기·맞춤, 실제 선택 색 raster와 PNG 해시를 기록한다. UI의 녹색 버튼을 제외한 pixel mask와 선택 숨김 음성 대조를 사용한다. 케이스마다 저장하며 동일 입력의 완료 케이스는 재개 시 건너뛴다.
- 기존 overlay의 2,026개 경로가 공유하는 695개 region/source 사례를 모두 실행했다. 첫 선택 14:24:04 UTC부터 마지막 14:27:07 UTC까지 약 3분이다. 695/695 render observed, 경로 실패 0, 카드 불일치 0, pageerror 관찰 0. PNG 695개와 숨김 대조 1개를 저장했다. 실제 응답의 SHA256와 889,304 bytes가 기존 QA 기준선과 일치했다. software WebGL에서의 기능 검증이며 실기기 성능 합격으로 사용하지 않는다.
- TA2:2261의 원본 `.r`, source catalog, compiled sourceLabelSide, 동일 evaluated geometry hash, kind/region/정확한 frozen target term을 대조하여 **독립적인 오른쪽 경로 1개**만 추가했다. 기존 두 `side_conflicted / conceptKey=null` 기록은 삭제하거나 바꾸지 않았다. unsided 표본을 왼쪽으로 추론하지 않았다. canonical HA 연결·geometry·명칭·권리·사람 승격은 추가하지 않았다.
- 새 오른쪽 경로는 실제 새 overlay 응답 해시를 확인하고 별도로 선택·단독 강조를 캡처했다. 원본·변환 자료가 선언한 오른쪽을 연결했으며 양측 전체 표현 또는 인간 해부학 검토 합격을 주장하지 않는다. 오른쪽 card와 강조 표면, 현재 C3 단독 표면의 PNG를 직접 시각 확인했다. 과거 C3 overview는 계속 합격 근거에서 제외한다.
- 현재 총 2,027개 alias, 696개 region/source 사례에 대해 선택·카드·단독 raster 근거가 있다. 종전 695개 이미지는 원본 revision에 그대로 두고, compiled geometry/resources, rights, source별 runtime 객체, renderer/UI 57개 파일이 동일함을 대조하여 재사용했다. 542/563의 **전체 해부학적 대응·그룹/부분/양측 범위 합격은 여전히 미완**이다. 자동 raster 검사를 그 합격으로 승격하지 않았다. 세부 판정은 `selection-render-ledger.json`의 모든 563 membership에 있다.
- dataset 계약 테스트 **37/37** 통과. 기존 시험의 “두 표본 모두 항상 연결 불가” 기대를 명시 오른쪽 route 통과/반대쪽 route 거부/unsided 미승격으로 교정했다. typecheck/build/12부위 route 및 성능 측정은 새 앱 구현 변경이 없으므로 선행 검증을 재사용하고 반복하지 않았다.
- runtime response는 889,304 → **889,329 bytes**, 25 bytes 증가했다. 실제 형상과 renderer/buffer/scene은 동일하다. 기존 성능 증거의 입력 범위와 미측정 한계를 보존한다. 전체 overlay의 숫자 직렬화 형태가 일부 달라졌으나 JSON 값으로 비교한 비관계 객체 필드 변경은 0이다.

## 남은 실제 작업

현재 경로 없는 133개를 `action-queue.json`에 target/part/group/side 범위와 다음 실제 조치로 나눴다. 같은 이름 검색을 다시 수행하는 대상은 없다.

| 다음 실제 조치 | 경로 없는 target |
|---|---:|
| 새로운 정확 대응 근거 또는 적절한 source 확보 | 43 |
| 변이 표본의 구체적인 근거 | 21 |
| 그룹·반복 family의 멤버와 전체 범위 근거 | 20 |
| 이미 캐시된 다른 dataset 후보의 대응·좌표 정합 | 6 |
| 부분 segmentation 또는 정확한 부분 source | 31 |
| 명시 좌우 또는 좌우별 source | 12 |
| 합계 | 133 |

캐시된 후보 6개는 TA2:1282(뼈골반), 2128/2129(입천장올림근/긴장근), 2191(귀관인두근), 2202(성대근), 2283(머리반가시근)이다. 후보 FMA/FJ ID, GLB 위치, source/chunk hash와 지역/좌우/기존 local-display 상태를 원장에 기록했다. 이름 대응 후보를 확정 교차표로 승격하지 않았다. BP3D의 axes/metres 표기가 ZA와 호환된다고 실제 정합이 입증된 것은 아니며, 현재 runtime은 ZA namespace에 묶인 부분이 있어 공통 source adapter/frame 검증을 거쳐야 한다. 새로운 source 취득을 일괄 금지하는 과거 재개 프롬프트는 이 조치에 적용하지 않는다. 26 설계 C에 따라 실제 필수 gap만 근거 있게 보완한다.

TA2:2261의 unsided 표본과 양측 전체 범위는 별도 미완이다. 133개의 경로 없는 대상에서 빠졌다는 이유로 이 충돌을 잊지 않도록 `heldSourceIdentityExceptions`에 보존했다. 직접 한국어 인용 gap 73개와 AI 제안, 명칭 충돌도 독립 원장에 계속 남아 있다.

## 유지한 경계

542 target / 563 membership / 12 부위, 원래 HA 130개, source-only 830행, rights held 960행, humanReview not_performed 960행을 유지했다. historical 163은 원래 6/20/135/2 분류 그대로이며 source-wide geometry absence 증명으로 바꾸지 않았다. 기존 A/B/C와 별도 visual-qa 원조사, 원본, OpenSim_Models 및 다른 미커밋 WIP를 수정하지 않았다. T80/T58·push·배포는 시작하지 않았다.

## 이후 실행 시 사용할 현재 자료

현재 요약: `python3 work/tools/inspect_t100_progress.py`

현재 단일 QA 기준선: 이 폴더의 `qa-baseline.json`. 현재 범위·이미지 참조: `selection-render-ledger.json`. 다음 source 조치: `action-queue.json`. 역사 builder는 해당 역사 출력의 재현에만 사용한다. 이전 Git overlay로부터 다시 만드는 과거 builder를 현재 overlay에 덮어쓰기용으로 실행하면 이후 연결이 소실될 수 있다. 현재 데이터를 읽는 공통 validator/snapshot과 delta를 사용하며, 이미 증명한 선택 사례와 성능을 반복하지 않는다.
