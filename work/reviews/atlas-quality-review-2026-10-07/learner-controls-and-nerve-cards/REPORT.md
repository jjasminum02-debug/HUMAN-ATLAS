# 부위 선택·보기 옵션·신경 카드와 명칭 교정

사용자 요청의 학습 UI 수정 및 현재 신경 이름 98묶음 형식 감사/표시 교정을 완료했다. 기존 T40/T66/T85 합격, EXECUTION, 다음 task 순서는 변경하지 않았다. 신경 해부학 콘텐츠 전체 검토 완료 또는 새 지배 관계 확보를 뜻하지 않는다.

## 이름 감사와 원인

현재 모형 이름 98묶음 중 75묶음은 koModern/koTraditional/en이 같은 영어다. 한국어가 이미 있는 묶음은 23개다. 해당 75묶음은 신경 표면 195개 중 149개에 대응한다. 98은 source-native label group 수이며 독립 신경 개념/개체 수로 추정하지 않는다.

| 분류 | 영어 반복 이름 묶음 | 예 |
|---|---:|---|
| 팔신경얼기 뿌리·줄기·갈래·다발 | 11 | Inferior trunk, Posterior cord |
| 신경뿌리 | 4 | Anterior root of spinal nerve |
| 손가락·발가락 가지 | 12 | Common palmar digital branches of median nerve |
| 근육가지 | 5 | Muscular branches of axillary nerve |
| 기타 가지 | 16 | Deep branch of ulnar nerve |
| 이름 붙은 신경·교감신경줄기 등 | 27 | Genitofemoral, Thoracodorsal nerve |

원인은 공유 graph의 한국어 필드에 native English 대체값이 들어 있고, 카드/목록은 해당 값을 언어 확인 없이 그대로 표시하는 구조다. 단순 필드 존재 검사는 이 결함을 이름 완성으로 오인할 수 있다. 전체 75개 before/after와 분류는 nerve-name-audit.json에 보존했다.

원본 graph, en, sourceNativeEnglishName, identity/key, branch/supply/geometry 관계는 바꾸지 않았다. learner-nerve-display-names.json과 단일 이름 projection을 카드·목록·검색에 함께 적용했다. 기존 23개 이름은 유지하며 현재 98묶음은 모두 한국어 표시를 갖는다. 영어/한국어 검색이 같은 원본 source를 선택한다.

예: 팔신경얼기 아래줄기 / 상완신경총 하부줄기 / Inferior trunk of brachial plexus. 앞/뒤갈래, 위/중간/아래줄기, 피부/근육/손가락/발가락 가지를 별도로 유지한다.

75개를 사전 직접 표제어라고 주장하지 않는다. source 영어의 정확한 한정어와 기존/확인된 한국어 구성요소를 조합한 학습 표시명이다. 대학 공개 해부 강의의 줄기/갈래/다발 명명과 국립국어원 앞뼈사이신경 등의 용어 구성요소를 대조했다. 직접 자료 접근 제한과 근거 구분은 감사 JSON에 기록했다. anatomy/geometry/사람 검토 승격은 0이다.

## 실제 UI 수정

- 일반 클릭으로 부위를 추가/해제하며 선택 후 메뉴가 열린 채 유지된다. Shift가 필요 없다. 전신은 부위 선택을 비우고 메뉴를 유지한다. Escape/바깥 클릭의 닫힘과 기존 부드러운 전환을 보존했다.
- 전체 보기·선택만 보기·선택 숨기기·되돌리기·보기 복원·별도 주행 보기 버튼을 제거했다. 뼈/근육/신경, 화면 맞춤, 선택 맞춤, 선택 강조/반투명 또는 실제 관계가 있을 때 관련 근육 강조를 남겼다. 선택만 보기 제거로 주변 구조를 사라지게 하는 UI 경로도 제거했다. 신경 layer로 주행 표시를 조절한다.
- 신경 및 근육 카드의 반복 displayNote와 강조 한계 설명은 접힌 ‘관계 안내’에 보존했다. 구조를 바꾸면 다시 접힌다. 근육 링크와 기존 좌우/범위 관계는 유지한다.
- 작용이 없는 근육에는 빈 관련 작용 영역과 ‘현재 연결된 작용 설명이 없습니다’를 만들지 않는다. 관계/분지 자체가 없는 신경도 빈 섹션을 반복하지 않는다. 감각/운동 설명과 실제 주행은 보존한다.
- 유효한 예전 글 설명이 learningIntent 미기입 때문에 누락되던 문제를 수정했다. 공통 intent 규칙을 재사용해 candidate 없는 예전 설명은 text_only로 표시한다. 분류되지 않은 playable clip은 posture_observation으로 남아 근육 작용으로 승격하지 않는다.

## 검증 및 로컬 반영

자동 28개 고유 검사, typecheck, generated card/motion freshness, production build 및 로컬 고정 패키지 검사 통과. 실제 브라우저에서 클릭/키보드 다중 부위 선택, 해제/전신/Escape, 한국어 신경 검색, 좌우 카드, 겨드랑신경→삼각근, 접힌 관계 안내, 반투명 관찰, 깊은종아리신경의 글 설명 및 작용 링크→앞정강근 loop→재클릭 rest를 확인했다. viewport 1440×900, 1024×900, 390×844의 변경 화면을 확인했다. 390은 모바일 실기기가 아니다. 콘솔 오류 0; 단일 canvas 유지.

94개 anatomy/motion/projection 파일 및 private input 3개 hash가 이전 전달본과 같다. 신경 원본 graph와 18개 motor relation을 보존했다. 고정 snapshot은 보존된 실제 작업 트리 기반이며 기존 WIP를 커밋했다고 주장하지 않는다. 원본/OpenSim_Models/T13과 역사 상태는 수정하지 않았다.

검증한 최신 앱은 http://127.0.0.1:5184/ 에 제공한다. 기존 화면은 새로고침해야 수정 bundle을 읽는다. 상세 기록은 validation.json과 browser-validation.json, PNG 3장에 남겼다. 기존 JS chunk 크기 안내는 남아 있고 예산을 변경하지 않았다.

## 이후 개발 순서

1. 이번 이름 표시와 전수 형식/원명 검사 유지. 새 source가 추가되면 한국어 필드에 영어를 복제하지 않고 근거 있는 표시명 또는 미정 상태를 사용한다. 복합 용어의 직접 표제어 대조와 사람 검토는 별도 상태다.
2. 신경→근육 관계 자체의 누락/오류를 현재 source·측·전체/부분 범위로 검토한다. 이번 18관계를 전 지배망으로 세지 않는다.
3. 관계가 있는 근육의 기존 기시정지/작용 근거를 재사용해 글 설명을 확충한다. 설명 지원과 3D 시범 지원을 별도 계산하고, 없는 내용을 버튼 수로 채우지 않는다.
4. 그 다음 검증된 작용별 표면 변형과 주변 뼈/근육 문맥을 확장한다. 이름만으로 주행/지배/활성도나 animation을 만들지 않는다.

이 후속 항목은 인계 계획이며 이번에 새 task를 만들거나 실행하지 않았다.
