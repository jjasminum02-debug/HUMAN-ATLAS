# T66 내부 02 — 양측 앞정강근·대퇴직근 실제 작용

**이번 내부 단계 completed/passed. 부모 T66은 in_progress/partial이며 nextUnit은 그대로다.** 실제 지원은 근육군 2개, 원본 표면 4개, 정확한 source/action 연결 6개, GLB 6개다. 기존 오른쪽 앞정강근 1개를 그대로 재사용하고 5개를 새로 제작했다. 전신 근육 완성이나 전체 target extent 승인은 아니다.

| 근육 | 측 | 작용 | 교육용 자세 범위 | 주변 구조 |
|---|---|---|---|---|
| 앞정강근 | 좌·우 | 발목 등쪽굽힘 | 기존 6.5° | 각 58개 원본 표면 |
| 대퇴직근 | 좌·우 | 무릎 폄 / 슬관절 신전 | 15° 굽힌 준비 자세 → 원본 시작 자세 | 각 71개 원본 표면 |
| 대퇴직근 | 좌·우 | 고관절 굽힘, 무릎 유지 | 12° | 각 88개 원본 표면 |

무릎 폄은 준비 굽힘과 실제 폄의 의미를 구분해 같은 player의 역방향 구간에서 보여 준다. 대퇴직근과 나머지 넙다리네갈래근, 햄스트링·무릎을 지나는 근육을 실제 표면으로 변형한다. 슬개골·정강뼈·종아리뼈·발뼈와 확보된 종아리/발 근육 전체가 함께 표시된다. 고관절 굽힘에도 누락된 실제 원본 종아리/발 근육 16개씩을 추가했다. 새 접촉 보정은 5개 표면씩의 최대 약 39.5µm 수동 corrective이며 활성도나 힘의 표시가 아니다. 선택 근육만 색이나 길이를 바꾸는 시범이 아니다.

30° 후보는 대퇴직근 면 뒤집힘 29건, 20° 후보는 반막근 면 뒤집힘 1건으로 채택하지 않았다. 엄격한 기하 기준을 유지한 15° 후보를 사용한다. 발꿈치의 실제 이동 약 103mm를 확인했다. 카메라는 전체 움직이는 다리를 처음 한 번 맞추며, 정면 기본 시점에서 무릎 동작을 숨기지 않도록 비스듬한 관찰 방향을 쓴다. 사용자가 이미 고른 방향은 보존한다. 재생 중 주변 근육의 기본 색과 전체 모양을 유지하고, 데스크톱 장면 높이를 312→352px로 확보했다. 반복/진행 조절/복원마다 카메라를 재설정하지 않는다.

실제 GLB의 key와 중간 보간에서 앞정강근 33 samples, 무릎 각 변형 표면 49 samples를 검사했다. 고관절의 기존 72개 노드/동작은 65 자세에서 오차 0으로 재사용했다. 새 종아리 문맥과 뼈의 접촉은 측당 241쌍/65 자세, 수동 보정 표면은 129 자세에서 검사해 새 containment와 면 뒤집힘 없이 통과했다. 필수 morph accessor min/max를 보완한 마지막 변경은 binary equality를 확인했으므로 기하 검사를 재사용했다. 접촉 보정은 명시된 동반 표면의 작은 상대 morph만 허용하며, 실제 로더도 변위 상한을 검사한다. 미확인 morph 및 상한 초과는 실패한다.

실제 브라우저 1280×720 CSS viewport, canvas 1개에서 양측 선택→작용 선택→반복→재클릭 smooth rest→scrub→숨김/근육 layer-off/복원, 검색과 뒤/앞, 수동 카메라를 확인했다. 기존 +30% 오른쪽 앞정강근은 다시 확대하지 않았다. 최종 수정 이후 console error/warning 0. 중간 고관절 로더 실패와 accessor warning은 숨기지 않고 원 로그와 수리 기록을 남겼다. 이번 단계에서 390/1024/1440 또는 모바일 실기기 검증을 했다고 주장하지 않는다.

관련 회귀 50/50, typecheck, 전수 motion schema/policy 검사(1150 action rows /1144 assets), Vite production build 통과. 이 큰 행 수는 기존 WIP 포함 원장이며 실제 근육 작용 개수가 아니다. 빌드의 큰 JS 청크 안내는 남았다. 확대 검사에서 역사 신경 fixture가 bone binding 199를 기대하지만 시작 기준선도 이미 865여서 한 건 실패했다. 이 검사를 통과로 쓰지 않았고, 이번 단계를 위해 역사 fixture나 다른 작업 데이터를 덮지 않았다.

542/563/12, 근육429/447/232 concepts/462 surfaces, HA130, 역사163(6/20/135/2), source-only·공개 held·humanReview not_performed, 원본/OpenSim/T13 및 기존 WIP를 보존했다. 기존 공통 데이터 행 전부와 재사용 자산 179개의 동일성을 확인했다. 소유 변경만 선별 커밋하며 이번 자산에 필수적인 기존 per-surface emitted QC 검증 부분은 검토하여 채택했고, 그 외 공통 코드/authoring 도구/worker WIP는 제외한다. 이 체크포인트는 현재 작업공간에서 검증한 내부 단계이며, 미커밋 선행 의존성까지 clean checkout에 포함했다는 뜻이 아니다.

남은 콘텐츠: 앞정강근 안쪽번짐, 전체 정상 ROM, 실제 측정 부착 footprint/슬개골 활주/생리적 힘·활성도. 부모의 다음 필수 내부 범위는 대흉근·견갑거근·능형근, 그 뒤 복직근·외복사근 및 최종 통합이다. 범위 밖 얼굴/턱/호흡과 E index 문제는 기존 deferred engineering backlog로 유지한다.

상세 근거: `scoped-acceptance.json`, `supported-actions.json`, `final-validation.json`, `action-outcome.json`, `knee-action-outcome.json`, `hip-context-outcome.json`, `hip-metadata-reuse-receipt.json`, `browser/observations.json`, `browser/capture-manifest.json`, `common-input-preservation.json`, `reuse-and-preservation.json`.

다음 수동 프롬프트: `work/plans/t66-priority-atlas-2026-10-05/03-shoulder-scapula.txt`. 이번 실행에서 다음 단계는 시작하지 않았다.
