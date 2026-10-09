# 근육 색·표면 결 개선 — 2026-10-09

결과: 현재 로컬 앱에 밝은 산호색과 은은한 표면 결을 적용했습니다. 사용자 참고 화면은 색/질감 방향에만 사용했고 상용 이미지나 texture를 복제하지 않았습니다.

## 변경

- 기본 근육색 `#aa5659` → `#d48b78`, 작용 강조색 `#c15b53` → `#df8065`, roughness 0.68 → 0.64. 뼈·신경·선택/관계 색 및 조명/노출은 유지했습니다.
- 원본 표면의 기하 디테일에 작은 절차적 요철과 명암을 더했습니다. 실제 근섬유 방향/힘줄 경계는 새로 만들지 않았습니다. UV 없는 source도 사용하며 추가 texture/vertex attribute/모델 파일은 없습니다.
- morph/skinning 전 rest 좌표를 사용해 변형 중 결이 표면에 따라 움직이도록 했습니다. 픽셀보다 작아지면 결을 줄이고, 정적/선택/반투명/작용/복원 재질에서 공통 적용합니다. 재질 상태마다 고유 shader를 생성하지 않습니다.

## 검증

재질 검사 3/3, 최종 typecheck, production build, EXECUTION projection check 통과. 실제 브라우저의 머리 확대, 전신, 대퇴직근 선택·반투명·loop·재클릭 rest·scrub·숨기기 흐름에서 셰이더/console 오류 0. 390×844, 1024×768, 1440×900은 실제 브라우저 viewport이며 아이폰/아이패드 실기기 검증이 아닙니다. PNG 및 validation.json 참조.

개발 브라우저 표본: 머리 101 draws / 62,395 triangles / material 2 / shader program 2, render CPU P50 1.1ms·P95 2.9ms. 대퇴직근 작용 71 draws / 37,087 triangles / material 6 / shader program 3, render CPU P50 0.2ms·P95 0.3ms. 두 표본 frame interval P50 약16.7ms. GPU 시간/VRAM은 관측하지 않았고, 변경 전 동일 조건 CPU 표본이 없으므로 성능 개선이나 무회귀 수치로 주장하지 않습니다.

## 보존·전달

기존 GLB 92개의 decoded SHA/URI가 모두 동일합니다. EXECUTION/NEXT의 입력 SHA도 그대로입니다. 지원 범위, 단일 scene, 기존 동작 크기, source-only/public redistribution held/human review not_performed를 변경하지 않았습니다. 기존 WIP와 다른 task 상태는 보존했습니다.

새 로컬 전달 snapshot: `local-20261009141757582-bf4218bb` (보존 WIP 기준). hosted package는 runtime 101파일, 지원 파일 포함103파일, upload189,639,277bytes, 최대17,220,355bytes. 로컬 allowlist/decoded SHA/header 검사 통과이며 외부 배포나 Cloudflare edge 검증은 수행하지 않았습니다. 이전 delivery에는 현재 HEAD의 별도 UI 최적화가 없으므로 전체 번들 차이를 이 재질 수정의 효과로 계산하지 않습니다. JS chunk 경고는 유지합니다.

실제 근육별 섬유 방향/texture/정확 부착 영역의 미확보는 콘텐츠 상태로 남습니다. 이번 색·표면 표현 범위의 확인된 제품 blocker는 없습니다.
