# 결정 기록

## T00 — 2026-09-25

- 프로젝트 작업 경로는 `/Users/daniel/Downloads/SIM /HUMAN ATLAS`로 둔다.
- HUMAN ATLAS 상위 경로에는 기존 Git 저장소가 없으므로 이 폴더에 별도 로컬 Git 저장소를 만든다. 자동 push는 하지 않는다.
- `OpenSim_Models/`는 원본 자료 저장소의 별도 checkout으로 보존하고, 상위 프로젝트 Git에서는 제외한다. 확인한 원본 revision은 `d9b05d470b1a481c222372c85b75772faf8f7792`이며 T00 전후 working tree가 깨끗해야 한다.
- 기존 `README.md`, `design/2026-09-25-muscle-atlas/`와 템플릿은 기존 자료로 취급한다. 내용 변경 없이 유지하고 T00 체크포인트에는 넣지 않는다.
- 현재 프로젝트 폴더에서 웹앱 파일(`package.json`, Vite 설정, 앱 진입 HTML)을 찾지 못했다. OpenSim 앱도 `/Applications`와 실행 경로에서 찾지 못했다. T00에서는 앱이나 데이터 구현을 시작하지 않는다.
- 설계와 템플릿은 요구사항 후보이며 완료 산출물이 아니다. 실제 학습 데이터는 아직 없다.
- 다음 직렬 작업은 T01이며 범위·출처 정책을 먼저 고정한다.
