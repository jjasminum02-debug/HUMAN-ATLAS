# Human Anatomy Atlas 공식 자료 조사

조사일: 2026-09-26. 사용자가 특정 제작사나 버전을 지정하지 않아 Visible Body의 Human Anatomy Atlas를 대표 참고로 택했다. 해당 제품 URL은 현재 Visible Body Suite 소개로 이동한다. 아래 Atlas 도움말과 Suite 설명은 제품/시기별 자료로 구분한다. 유료 앱에 로그인하거나 앱 내부 기능을 직접 조작한 것은 아니다. 공식 기능 문서와 공개 화면 이미지를 열어 확인했다.

## 기능과 도입 판단

| 확인한 기능 | 근거 | 이 프로젝트에 반영 |
|---|---|---|
| 구조 선택 후 정보 상자; 근육에서 기시·정지·작용으로 연결 | [공식 구조 정보 도움말](https://help.cengage.com/visible-body/student/visible-body/atlas-structure-info-ipad.html) | 근육 카드의 구조와 작용 연결 |
| 뼈 선택 후 골성 표지와 부착 관련 보기 | 같은 구조 정보 도움말 | 전용 뼈 카드·관련 근육 연결 |
| 부위별 장면, hide/fade/isolate | [공식 시작 안내](https://help.cengage.com/visible-body/instructor/visible-body/atlas-getting-started-ipad.html) | 사용자 지정 12개 부위, 주변 흐리게·격리·복원 |
| 근육 또는 부위에서 작용 장면을 찾고 설명·주동근·협력근 확인 | [공식 Muscle Actions 도움말](https://help.cengage.com/visible-body/student/visible-body/atlas-muscle-actions-ipad.html) | 선택 근육→움직임으로 이해하기→작용 선택 |
| 운동 단계의 색과 원위치 복귀 단계의 흐림 구분 | 같은 Muscle Actions 도움말 | 작용 구간과 시범 복귀를 구분. 역방향 재생을 같은 근육의 반대 작용으로 설명하지 않음 |
| 브라우저/모바일 접근, 학습 카드·투어 | [현재 Suite 제품 소개](https://www.visiblebody.com/anatomy-and-physiology-apps/vb-suite) | 웹·반응형 우선. 투어·AR 등은 현재 필수 범위에 넣지 않음 |

## 그래픽에서 직접 관찰한 것

[공식 근육 학습 글](https://www.visiblebody.com/blog/a-visual-guide-to-muscle-terminology-with-muscles-kinesiology)의 견갑골 거상 정보 화면과 부위별 작용 목록 이미지를 브라우저에서 열었다. 전자는 모델을 크게 두고 우측에 짧은 설명과 재생 조작을 배치한다. 근육의 섬유 방향, 뼈 표면의 미세한 질감과 음영이 보인다. 후자는 부위별 작은 장면 미리보기로 동작을 고른다. 이미지의 검은 배경은 사용자의 밝고 간결한 참고 화면과 다르므로 그대로 채택하지 않는다.

이 관찰은 제품의 공개 이미지에 관한 것이며 최신 유료 앱의 모든 UI를 실측한 결과가 아니다. 사용 엔진·shader·리깅 방식·원본 polygon 수는 공개 자료만으로 확인하지 못했다. 그 기술을 알아냈다고 쓰지 않는다.

## 우리 그래픽의 구현 방향

- 밝은 회색 배경, 아이보리 뼈, 자연스러운 근육색, 선택 강조 한 가지를 기본으로 한다. 섬유 방향과 형태는 실제 모델·허용된 texture에서 제공해야 하며 CSS 변경만으로 생성되지 않는다.
- 모델 품질, light/material, 카메라 구도, 정보 밀도를 따로 검증한다. 전체 모델을 한 화면에 작은 크기로 넣지 않고 선택 부위를 주대상으로 삼는다.
- 작은 근육·깊은 근육은 주변 흐림과 이름표로 접근한다. opacity 정렬 때문에 뼈/근육이 뒤집혀 보이는 현상도 실제 장면으로 검사한다.
- 상용 앱의 모델·texture·animation 파일을 추출하거나 재배포하지 않는다. 기능·학습 흐름을 참고하고 자산은 기존 보유/명시적 라이선스/자체 제작 자료에서 확보한다.
- 기시·정지 핀과 색칠은 학습에 유용하지만, 우리 데이터의 정확한 영역이 없으면 '위치 설명'과 '관련 뼈'만 제공한다. 핀을 임의로 만들어 정밀 위치처럼 표시하지 않는다.

## 소흉근 예제의 문헌 대조

[Elsevier Complete Anatomy 소흉근 자료](https://www.elsevier.com/resources/anatomy/muscular-system/muscles-of-upper-limb/pectoralis-minor-muscle/21327)는 3–5늑골 부위와 견갑골 오훼돌기의 연결, 전인·하방회전·하강 보조를 설명한다. [OpenStax 11.5, Table 11.8](https://openstax.org/books/anatomy-and-physiology-2e/pages/11-5-muscles-of-the-pectoral-girdle-and-upper-limbs)는 오훼돌기 정지와 견갑골 하강을 확인하는 별도 자료이며 기시 늑골 범위를 변이와 함께 다르게 제시한다. 따라서 '모든 필드가 두 출처에서 정확히 일치'로 기록하지 않는다. 하방회전과 전인은 이번 두 원문 중 Elsevier의 직접 지지가 있고, 동작 경로·정상 각도는 이 두 표만으로 정하지 않는다.

세부 예제는 `examples/pectoralis-minor-learning-example.json`에 있다. 이는 검색과 대조를 AI가 할 수 있음을 보이는 설계 예제이며 실제 canonical 자료의 사람 검토 상태는 바꾸지 않았다.
