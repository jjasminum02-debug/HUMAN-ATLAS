# T66 실제 검토·신경 표시 수정·우선 범위 개정 — 2026-10-05

루나 commit 8fb1b3b의 writer 정정은 보고와 일치한다. final-validation의16개 파일 hash가 현재 bytes와 모두 일치한다. 원본 manifest를 보존하고 receipt로 owner82행을 교정한 것은 타당하며 E nonempty root/readonly bone context 계약 오류는 해결했다. 실제 신규 animation authoring/runtime 등록은0이다. D22/E56 미등록 및 E aggregate integrity mismatch, geometry38pass/18fail/action-outcome0은 그대로 남았다. 전신 실제 제작까지 요구한 과거 프롬프트의 일부만 완료한 실행이다. contract tests 통과를 자산 제작/앱 기능 완료로 볼 수 없다.

최신 사용자는 모든 근육 일괄 완성 대신 앞정강근·대흉근·견갑거근·대퇴직근·복직근·외복사근·능형근을 우선 완성하고 점진 확장하기로 변경했다. T66 소유 record/spec/standalone prompts에 이 개정을 명시했다. 전체542/563/12와 전수 근육 원장·HA130·역사163, 원본/WIP 및 engineering 실패는 삭제/미확보로 재분류하지 않았다. 턱/얼굴/호흡/손 전체 후보 수리를 이 우선 범위의 gate로 두지 않는다. 다만 우선 근육에 해당하는 B/U03/척추의 실제 실패는 이번 책임이다. 계획 개정은 pass가 아니며 T66은 partial, 같은 nextUnit이다.

## 현재 우선 근육의 실제 지원

priority-motion-audit.json은 현재 learner runtime과 wave1 정확 selector/learningIntent를 대조하고 sourceBinding.subjectSourceKey로 필터했다. 오른쪽 앞정강근만 muscle_action1개다. 왼쪽 앞정강근에 오른쪽 canonical clip을 잘못 상속하지 않았다. 대흉근(쇄골/흉늑/배부분), 견갑거근, 대/소능형근과 대퇴직근은 주변 posture 경로가 있으나 작용 animation으로 등록돼 있지 않다. 복직근·외복사근은 playable route0이다. 기존13labels/35exactlinks/19surfaces 전체 지표는 우선7근육의 완료를 뜻하지 않는다. 새 GLB/animation 제작0.

## 신경 실제 문제와 이번 수정

현재 nerve-scene/support에는195 정적source 표면,98 label group이 있다. 고유 신경 개념 분모와 다르다. geometry motor 관계는 깊은종아리신경→앞정강근 좌우2개뿐이다. learner graph의4행에는 여기에 견갑배신경→큰/작은마름근 unsided concept2행이 더 있다. 이전에는 카드 버튼만 연결돼서 그 concept 관계가 renderer 강조에는 반영되지 않았다. 액와/요골/정중/대퇴 등 운동근 card는 아직 미연결이며 3D 주행 존재와 구분한다. 신경 선택 시 기본 nerve layer가off라서 카드만 열리고 selected focus/관찰도disabled인 것을 실제 UI에서 재현했다. 이름98개 전체와 geometry195개를 재검증했다는 주장은 하지 않는다.

이번 구현:
- 첫 신경 선택 시 layer-on. 사용자가 직접off한 레이어는 좌우/선택 변경이 켜지게 하지 않는다.
- 기본 신경 gold (#d7ac20), 선택 green (#208b3a), 주행 관찰 주변 반투명은 유지. 일반 dim에서 신경색을 희게 섞지 않는다. 원본 두께/좌표/geometry는 그대로다.
- 기존 문헌 concept 관계를 같은side의 eligible muscle context로 전달해 능형근을 파랑으로 더 선명하게 강조한다(opacity .82). exact nerve branch motor binding을 늘리지 않는다. 카드·역관계는 기존 근거를 사용하며 새 anatomy/지배 관계0이다.
- 관련 근육 강조·지배 근육 카드와 실제 힘/활성도 측정이 아님을 명시. 감각신경에 운동근을 만들지 않는다.
- context는 hidden/layer/isolate/pose/신경 region/side/local eligibility 검사를 통과해야 한다. 개념 context 때문에 held asset을 켜지 않는다.

## 검증 및 한계

관련 신경/지역/정책 회귀28/28, typecheck, production Vite build 통과. 기존 chunk warning은 유지하며 예산을 상향하지 않았다. 실제 browser1280×720에서 처음선택/신경off후좌우변경/숨김/undo/근육layer-off/동일side능형근강조/선택맞춤 확인, console errors0, canvas1. browser-validation.json 및 nerve-related-muscles.png가 근거다. 390/1024/1440 전체 QA나 모바일실기기 검증이 아니다. 신경 동적pose·힘/활성도·포착 좌표·새 source geometry·canonical HA/human/권리 승격0. 지원 운동pose의 정적 신경 숨김은 기존 경로를 유지했다.

다음 수동 실행은 work/plans/t66-priority-atlas-2026-10-05/README.md의 독립5프롬프트다. 신경학습 연결→앞정강근/대퇴직근→대흉근/견갑거근/능형근→복직근/외복사근→최종통합. 새 병렬 manifest/worker launch를 만들지 않는다. 지정7근육의 실제 대표 작용/side/part와 지원 신경 흐름이 통과하면 T66을 scoped passed로 닫고 전체콘텐츠partial/engineeringbacklog를 별도로 유지해 T85 UI/성능으로 인계한다.

기존 DatasetSceneAdapter.ts에는 선행 WIP가 있으므로 현재 세션 before→after 변경만 부분 staging한다. 기타 WIP·원본/OpenSim/T13를 보존한다. 검증은 현재 보존된 working tree 기준이며 clean HEAD 독립빌드 주장과 구분한다.
