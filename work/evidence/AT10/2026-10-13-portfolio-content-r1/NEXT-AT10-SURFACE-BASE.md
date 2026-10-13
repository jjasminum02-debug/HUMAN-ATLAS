# 다음 AT10 묶음: surface-base (담당 Sol xhigh)

HUMAN ATLAS의 AT10 공통 보완 중 surface-base 묶음만 수행해라. 담당 Sol xhigh.
AGENTS.md, 최신 EXECUTION, work/tasks/AT10.md,
work/plans/acupoint-surface-posture-2026-10-13/REVIEW-AND-DESIGN.md,
AT8/9/10 실제 package·carrier·source manifest와 portfolio-content-r1의 내용 대조 결과를 읽어라.

AT9 74/AT10 50 미표시의 공통 원인은 표면과 지표 부족이다.
기존 후보가 없다는 보고만 반복하지 말고 사용할 체표를 실제 확보·정합·통합해라.
이미 없다고 확인한 ZA Skin/Dermis를 재검색하는 것으로 끝내지 마라.
먼저 MakeHuman core mesh/MPFB 등 기존 공개 자산을 조사한 근거를 활용한다.
실제 객체/파일 hash·개별 권리·unit/frame/좌우/rest pose를 확인하고
얼굴·어깨·손목·복부·하지 표본의 정합 오차와 대응 지표로 후보를 선택해라.
새 전신 mesh를 처음부터 만들거나 기존 해부학 엔진을 교체하지 마라.
기존 골격/근육을 기준으로 피부만 정합하며, scale 하나나 무검증 shrinkwrap으로 끝내지 마라.

선택한 피부를 단일 AnatomySceneRoot의 공통 carrier로 연결한다.
체표 anchor와 glyph를 분리하고 작은 표면 접촉 표식으로 구현해라.
근육에 임의로 점을 당겨서 실제 혈위 좌표를 덮지 마라.
체표를 숨기는 관찰에서는 선택 부근 체표/깊이 단서를 유지하여 공중 점처럼 보이지 않게 해라.
동일 carrier의 geometry/LOD/cache를 공유하고 실제 예산·부위별 lazy load를 확인한다.
얼굴/손/복부 지표를 다음 점 authoring에서 쓰도록 주소와 판정 근거를 공급해라.

실제 앱에서 양측·여러 거리·가림·표면 접촉·지역/레이어 전환·반응형과
원본 모델 보존을 검증한다. UI 배치·보기옵션·카메라 정책은 개편하지 마라.
기존 사용자 WIP·원본·역사 evidence를 보존하고 소유 변경만 로컬 커밋해라.
AT10 report/evidence 및 이 보완 단위의 실제 상태를 기록하고 sync/--check 후 멈춰라.
다음은 같은 AT10 locating-posture다. 자동 실행·push·배포는 하지 마라.
