# 01 UI 단계 결과

## 결과

소스 UI의 구조/기능 탭, 작용 선택, 부위 탐색 흐름을 개선했다. 일반 근육 선택·검색·좌우·뒤/앞 복원은 구조 탭으로 돌아오며, 작용 탐색이나 신경 카드에서 동작을 명시적으로 선택한 경우에만 정확한 `actionId`로 기능 탭을 연다. 기능 목록은 한 줄씩 표시하고 글 설명만 있는 항목도 유지한다. 행 선택은 재생을 시작하지 않는다.

움직임 패널은 기능 화면 안에 한 번만 마운트한다. 자세 관찰은 접힌 별도 영역으로 분리했고 근육 작용과 다른 관찰임을 설명한다. 재생 중 구조 탭으로 이동하면 기존 player/controller가 rest 복원을 시작한다. 카메라와 숨김 설정을 건드리지 않는다.

왼쪽 탐색 상단에 전신/12부위 선택기를 고정하고 긴 구조·작용 목록만 스크롤하도록 했다. 검색 중에도 선택기를 유지한다. Enter/Space, Escape, 바깥 클릭, 포커스 복원 및 Shift 다중 부위 선택을 확인했다. 다중 선택의 `aria-pressed` 표기도 실제 선택 집합과 맞도록 보완했다.

## 실제 브라우저 확인

개발 화면 `http://127.0.0.1:5175/`에서 390×844, 1024×768, 1440×900 CSS viewport를 확인했다. 이 값은 브라우저 viewport이며 실기기 검증으로 표현하지 않는다. 453개 구조 행의 끝까지 스크롤한 뒤 목 부위로 전환했고, 검색 중 부위 변경도 확인했다. 키보드와 포인터 입력, 다중 선택 및 선택 표시를 확인했다.

전경골근의 일반/좌우/뒤·앞 선택은 구조 탭과 카드/URL이 일치했다. 기능 화면에는 세로 작용 목록과 단일 player가 있었으며, 작용 행 선택만으로 재생되지 않았다. 작용 탐색에서 선택한 항목 및 신경 카드에서 연결한 항목은 정확한 기능 행을 선택했다. CTA 반복 재생, 재클릭 rest 복원, 기능→구조 전환 시 rest 복원, 숨김 상태 보존과 단일 canvas/player를 확인했다. `posture_observation`은 접힌 “자세에서 관찰하기”로 남고, 근육 작용이라고 표시되지 않았다. 현재 브라우저 console error는 0건이다.

부위 선택기와 모형/카드의 배치를 1024 및 1440 폭에서 확인했다. 390 폭에서는 탐색 패널을 열어 선택기와 목록 분리를 확인했다. 실제 실기기 터치 검증은 하지 않았다.

## 검증 결과와 제한

- `pnpm typecheck`: 통과.
- `pnpm test:search`: 44/44 통과.
- `pnpm test:motion-player`: 39/39 통과(주 테스트 36, 직렬화 3; 정확 source-side 사례 455).
- `pnpm test:navigation`: JavaScript 17/17 통과. 이어지는 Python 12개 중 11개 통과, 1개는 기존 `baseline.atlas-data/catalog/canonical-catalog.json`의 T15b 보호 입력 hash 불일치를 보고했다. 이는 이번 UI 변경과 무관하며 해당 입력은 수정하지 않았다.
- `git diff --check`: 통과. 최종 production build는 이번 단계 범위가 아니며 04 전달 단계에 남겼다.

대표 부위 선택기 화면은 브라우저에서 캡처해 확인했다. 다만 캡처 파일을 evidence 경로에 저장하는 브라우저 동작이 보안 정책으로 차단되어 `screenshots/`의 PNG 산출물은 남기지 못했다. 따라서 화면 자체의 실제 검증은 수행했지만 PNG 전달 기준은 미완이며, 04에서 같은 변경 소스를 기준으로 저장 가능한 캡처를 생성해야 한다.

## 보존 및 소유 경계

T40의 `completed/passed`, 제품 상태, 기존 보고서와 5180 고정 snapshot은 변경하지 않았다. 이번 단계는 이름·신경·해부학 데이터, 분모, 권리, 사람 검토 상태를 수정하지 않았다. `styles.css`도 그대로다. `MotionLearningPanel.tsx`에는 시작 시 이미 있던 profiler/asset timing 변경이 있어 보존했으며, 이번 `active` 처리만 선택 커밋 대상이다. 새 전달본 생성과 최종 build는 04의 책임이다.

## 변경 파일

- `atlas-web/src/ui/App.tsx`
- `atlas-web/src/ui/atlasShell.css`
- `atlas-web/src/ui/MotionLearningPanel.tsx`의 `active` prop 및 비활성 시 rest 복원 hunk
- `work/reviews/atlas-quality-review-2026-10-06/ui/baseline.json`
- `work/reviews/atlas-quality-review-2026-10-06/ui/validation.json`
- 본 보고서

02 신경 검토와 03 근육 이름 검토는 각각 지정된 출력 폴더에서 병렬로 수행할 수 있다. 이 단계에서는 실행하지 않았다.
