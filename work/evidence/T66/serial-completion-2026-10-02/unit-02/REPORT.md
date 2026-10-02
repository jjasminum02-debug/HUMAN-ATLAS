# T66 내부 unit 02 — 고관절·무릎 굽힘

- 담당: Luna Max · 실행일: 2026-10-03
- 결과: **implemented_verified (unit 02 범위)**
- 부모 T66: `in_progress / partial`; `nextUnit=author-and-integrate-normal-motion-bone-and-nerve` 유지
- 다음 수동 내부 입력: `work/plans/t66-serial-completion-2026-10-02/03-T66-shoulder-forearm-wrist.txt` (시작하지 않음)

## 수행 범위

양측 고관절 굽힘 2개와 무릎 굽힘 2개, 총 4개의 source-family 패키지를 unit 01 공통 변형/export 및 단일 scene 계약으로 제작했다. 기존 T66-B1의 hip 접촉 실패와 T66-B4의 knee-context 누락을 이번 패키지에서 다뤘다. 기본 scene/renderer/controller/camera/frame clock은 유지했다.

입력/보존 기준은 시작 HEAD `5d4255ccac2790ef65beeef5b56e4821a43a4f2a`, 시작 dirty entry 230개, hash 기록 regular file 131개다. 입력 ZA compiled manifest SHA256은 `56ffd2d93d9a4c4b0b3954511c471358e3da54f47e6915cb35d4b6111f1b7f42`, ZA overlay SHA256은 `4a5028dd7c1bca3b142d7899cc99a425ad88d5837ca598d2d5f4ad612994be5c`다. 단위 시작 원장은 `start-baseline.json`, 정확 입력과 가족 큐 hash는 `serial-queue.json` 및 `registration.json`에 있다. 기존 task 소유 변경·sync 대상 projection을 제외한 기존 dirty regular file 124개의 hash를 재검사해 모두 불변임을 확인했고 시작/종료 `OpenSim_Models` 변경은 0이다. 실행 원장에 맞춰 generated execution projection은 sync했다; 혼합 사용자 이력 전체는 소유 변경으로 stage하지 않는다.

## 구현 및 표현 경계

- 각 side/family별 재현 가능한 authored motion GLB와 별도 derived reference GLB를 생성하고 동일 learner scene에 등록했다. 패키지 단위 해시/크기와 실제 source identity는 `validation.json`, `registration.json`, 개별 authoring 입력 및 GLB pose 검증에 기록했다.
- hip candidate는 이전 시도에서 새 source containment 최대 3을 보여 실패했다. 교정된 교육용 trajectory에는 해당 contact 검사에 맞춰 authored 8 mm pivot offset을 적용했고, 새 재현 패키지 2개는 9 key pose 및 구간 보간 표본에서 새 containment 0으로 통과했다. 이 offset은 출처의 측정 축/관절 중심/정상 운동범위가 아니다.
- 무릎 양측 package에는 정확한 source Patella를 실제 이동 구조로 넣고 Femur를 고정 기준으로, 관련 source 뼈와 주변 근육 surface를 같은 scene/frame에 두었다. T90 quadriceps 부착 자료는 정성적 문맥으로 재사용했을 뿐, 별도 슬개골 활주나 새 부착 footprint/좌표를 주장하지 않는다.
- 등록 관계는 178 selector rows(근육 50, 뼈 128); 고유 근육 source key 38, 고유 뼈 source key 64다. 이것은 source 관계/instance 합계이며 canonical concept 수가 아니다. 122개 role 행은 moving structure, 6개는 fixed structure, 50개 근육 surface는 `deforming_passive_surface`다. 선택 근육 표면의 수동 변화를 근육 활성·주작용으로 표시하지 않도록 runtime/card 역할도 보존했다.
- source frame `HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR`, 단위 m, 정적 기준 자세 `ZA-9f08a17ea0115fed-frame0-autoexec-off`를 유지했다. 새 HA canonical binding은 0, sourceOnly/local technical use는 true, human review는 `not_performed`, 공개 재배포 권리는 `held`다.

## 실제 재생 및 브라우저 검증

- 4개의 GLB 모두 key-pose signed-frame replay가 통과했다. 양측 hip은 각 9 key poses, 보간 포함 65 samples; 양측 knee는 각 9 key poses와 보간 표본을 검증했다. 검사한 muscle surface 50개는 segment당 8개 보간 subdivision에서 face flip 0, 새 containment 0, 최소 sampled area ratio 0.1231287 이상이었다. 연속 충돌 자유는 입증하지 않았다.
- 실제 로컬 앱 `http://127.0.0.1:5174/`을 Chrome 154 headless / Playwright 1.62.1로 확인했다. Psoas, hip bone, patella, femur의 좌우 선택과 역할별 한국어 카드 안내, 재생/50% scrub/rest 복원, 숨김 상태 유지 및 숨김 중 재생 차단, 오른쪽 vastus intermedius 390 px 흐름을 포함해 9개 시나리오가 통과했다. 1440×1000 및 390×844에서 확인했고 390 px 수평 overflow는 0이었다. 9개 motion GLB 응답은 HTTP 200과 파일 hash가 일치하고 console/page error는 0이었다. 선택된 왼쪽 무릎뼈와 주변 넙다리뼈·정강뼈를 fit한 국소 캡처는 `browser/knee-patella-left-fit.png`, 해시와 관찰 범위는 `fit-sample.json`에 있다.
- 캡처 표본은 주변 위치·선택·카드·좌우의 실제 장면 일치 증거다. 전체 target/group extent, 정상 운동범위, 연속 collision-free, 모든 selector의 전수 시각 확인은 아니다. 브라우저의 초기 4개 bootstrap 요청 취소는 화면 전환 중 abort였으며 motion GLB 요청 실패가 아니다.

## 검증

`verification-commands.json`과 개별 로그에 재실행 명령/종료 코드를 보관한다.

- unit data contract 및 GLB/registration validator: 통과
- 집중 회귀: 14/14 통과
- motion schema: 463 actions / 457 definitions / 457 assets, 통과
- source asset policy/hash: 통과, source bytes 변경 없음
- runtime projection: 208 selectors / 463 actions / 456 playable candidates, 통과
- TypeScript typecheck 및 production build: 통과 (비차단 500 kB chunk 경고)
- `sync_execution.py` 및 `--check`: 통과
- actual browser: 9 scenarios, response hash/card/role/side/scrub/restore/hidden/mobile, 통과
- fixture GLTF accessor min/max 경고는 테스트 fixture 경고이며 이번 자산 실패가 아니다.

## 상태 및 남은 범위

이번 unit에서 hip B1의 접촉 결함 및 knee B4의 patella/context engineering 요구는 실제 등록 패키지로 해소했다. 이 unit은 양측 가족 책임 4/4 package를 처리했다. T66 전체 family 전수 작업은 아니다. T66-B3에는 견갑대·전완·손/발가락·척추/호흡·턱/목뿔/후두·눈/얼굴/혀/인두·골반바닥 계열의 공통 family 구현이 남아 있다. 429 muscle targets / 447 memberships / 232 source concepts / 462 surfaces, 210 eligible bone instances, 신경 정적 자산/설명 coverage의 전체 completeness를 이번 숫자로 축소하거나 완료 처리하지 않았다.

이 unit으로 unit 01의 실제 browser 차단 상태를 소급 변경하지 않는다. unit 01 learner UI status는 `blocked_by_environment` 그대로이며 별도 재검증이 필요하다. 근육 주작용·정상 관절축·정상 ROM·사람 해부 검토·공개 재배포 승인은 이번 자료로 확정되지 않았다. 자료 gap과 남은 family engineering을 구분하며, exporter/mask/trajectory 등 미구현을 자료 부족으로 분류하지 않았다.

상세 검증 산출물:
- `validation.json`, `registration.json`, `registration-preflight.json`
- `trials-r1/summary.json`, `candidate-interpolation-r1.json`
- `browser/browser-checks.json`, `browser/*.png`, `fit-sample.json`
- `serial-queue.json`, `start-baseline.json`, `verification-commands.json`, `verification/*.log`
