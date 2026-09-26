> R13 보완: AI 자료 대조/사람 검토의 분리, 작용 설명·교육용 움직임, T16 이후 실행 및 Git은 07/08/09를 우선한다. 06의 12부위와 T15 흐름은 유지한다.

# 출처와 결정 기록

> R12 개정(2026-09-26): 현행 우선설계는 **06-REGION12-MUSCLE-BONE-REVISION.md**. 사용자화면은12부위/다중소속/근육+뼈선택. 이름은우리말명·한자어명(한글)·영어이며실제한자문자필수정책은폐기. T14b미승인은review승격만차단하고독립기술개발을막지않음. 이전내용중상충부분은역사적설계로읽는다.


확인일: 2026-09-25. 아래는 설계 근거이며 근육별 해부학 데이터 전체를 검증한 자료 목록이 아니다.

## 1. 직접 확인한 로컬 상태

- 작업 폴더: `/Users/daniel/Downloads/SIM /HUMAN ATLAS`.
- `README.md`와 `OpenSim_Models/README.md`, `Models/Rajagopal/README.txt`를 열람했다.
- `.osim` 파일 34개, 공용 `Geometry/` 바로 아래 파일 325개를 현재 파일로 집계했다.
- `Rajagopal2016.osim`의 `ForceSet/objects`에서 근육 요소 80개를 확인했다. XML 기본값의 `default`는 제외했다.
- 종아리 파일럿과 대응 가능한 모델 이름 gaslat/gasmed, soleus, tibant/tibpost, perlong/perbrev의 좌우 항목 존재를 확인했다. 이것은 해부학 대응 또는 부착면 정확성 검증이 아니다.
- 조회한 폴더에서는 기존 웹앱을 발견하지 못했고, 현재 작업 폴더는 Git 저장소가 아니었다. T00에서 프로젝트 루트와 추적 범위를 설정해야 한다.
- 참고 이미지의 중앙 3D+좌측 목록+우측 카드 배치는 사용자 경험 참고로 사용했다. 스크린샷만으로 해당 원본 앱의 코드를 확인한 것은 아니다.

## 2. 공식 자료와 쓰임

| 자료 | 확인한 사실 / 설계에 쓸 부분 | 한계 |
|---|---|---|
| [BodyParts3D 소개](https://lifesciencedb.jp/bp3d/info_en/index.html) | 형태 기반 해부학 사전·3D 데이터 후보, 누락/오류 가능성과 버전별 좌표 차이 공지 | 전신 기시·정지의 검증된 부착면을 제공한다고 확인한 것이 아님 |
| [BodyParts3D 이용 안내](https://lifesciencedb.jp/bp3d/info_en/license/index.html) | 사이트 기본 이용 조건으로 CC BY-SA 2.1 Japan 및 귀속 문구 안내 | 실제 내려받을 배포본·구성 에셋 조건을 T01/T02에서 기록해야 함 |
| [IFAA/FIPAT 용어 안내](https://ifaa.net/committees/anatomical-terminology-fipat/fipat-ifaa-terminologies/) | TA2와 표준명/동의어·관련어 구분, 판본 기반 명칭 구조 | 한국어/한자 전수 대응·근육 목록 추출은 아직 미수행 |
| [OpenSim 입문](https://opensimconfluence.atlassian.net/wiki/spaces/OpenSim/pages/53088700) | 근육은 여러 경로/분절로 표현 가능하고 모델 단순화가 존재 | 모델 요소 수=근육 종수로 셀 수 없음 |
| [OpenSim Muscle Editor](https://opensimconfluence.atlassian.net/wiki/spaces/OpenSim/pages/53090145) | fixed/via/moving/wrap point와 body frame | 경로를 실제 해부학적 부착 영역으로 간주할 수 없음 |
| [Three.js](https://threejs.org/docs/) / [glTF](https://www.khronos.org/gltf/) | 웹 3D 구현·전달 형식의 기술 문서 | 실제 버전 조합과 변환 품질은 구현 때 검증 |
| [Merck Manual 근력 평가](https://www.merckmanuals.com/professional/neurologic-disorders/neurologic-examination/how-to-assess-muscle-strength) | 근력·수행의 관찰, 저항·좌우 비교, 통증 등의 해석 맥락 | 모든 개별 근육 검사 및 진단 정확도 데이터베이스가 아님 |
| [Codex 공식 가이드](https://learn.chatgpt.com/guides/best-practices) | 작업 맥락·범위·프로젝트 지침을 제공하는 운용 참고 | 특정 Luna 버전의 성능·가격을 검증하는 근거가 아님 |

표준 명칭 문헌의 이용 조건도 별도로 확인한다. IFAA 안내는 웹 출판물에 CC BY-ND 4.0을 설명한다. 원문을 수정·번역해 통째로 재배포하는 권한을 자동으로 가정하지 않는다. 앱 내부 식별자 대응, 자체 설명, 원문 자료의 재배포를 구분하고 실제 사용하는 판본의 조건을 기록한다. [IFAA 안내](https://ifaa.net/committees/anatomical-terminology-fipat/fipat-ifaa-terminologies/)

## 3. 아직 확보하지 않은 것

1. **한글·한자 기준 판본:** 대한해부학회 또는 사용자가 학습에 사용하는 공인 용어집의 정확한 판본·대응표를 T01에서 확보한다. 이번 조회에서는 학회 사이트 내용을 확인하지 못했다. 따라서 전수 표준 용어를 확보했다고 주장하지 않는다.
2. **근육별 기시·정지 원자료:** 사용 가능한 해부학 교과서/atlas 판본과 페이지를 선정한다. 실제 소유·접근 가능한 자료만 사용한다. 사용자 자료가 없으면 접근 가능한 신뢰할 수 있는 자료를 조사하고 누락을 남긴다.
3. **부착면 좌표:** BodyParts3D의 근복 형상과 정확한 부착영역은 별도다. annotation 도구와 사람 검토가 필요하다.
4. **평가 프로토콜:** 검증된 검사 교재·원저·가이드라인에서 각 절차와 해석 한계를 확보해야 한다. 정상 범위·진단 성능은 문헌 확인 없이 생성하지 않는다.
5. **전신 에셋 완전성:** 아직 BodyParts3D 실제 배포본을 내려받아 전수 검사하지 않았다. T02의 자산 파일럿이 필요하다.

## 4. 자동 진행할 수 있는 결정

- 구조 우선, 기능·평가 후속; 치료는 제외.
- 오른쪽 종아리 6개를 파일럿으로 사용하되 전신 목록은 먼저 관리.
- React/TypeScript/Vite + Three.js, JSON + Git. 버전은 구현 시 고정.
- 내부 ID를 공통 키로 사용하고 외부 모델 ID는 adapter로 연결.
- 텍스트 근거/3D 좌표/사람 리뷰/기술 검증을 독립 관리.
- 자료 결측은 명시적으로 보존하고 독립 작업 계속.
- OpenSim 원본은 읽기 전용. BodyParts3D는 우선 조사 후보이며 전체 자료의 자동 채택을 뜻하지 않음.

## 5. 사람의 판단이 필요한 결정

- 학습에 사용할 한글/한자 용어집과 교재의 판본 선택. 지정 전에는 확보 가능한 출처로 후보 목록 작성 가능.
- 근거가 충돌하는 부착 범위·명칭을 어떻게 표시할지.
- 실제 3D 부착면 검토와 검사 내용의 타당성 검토.
- 유료 자산 구매 또는 서비스 공개를 실제 수행할지.

이 항목들은 설계를 다시 물어봐야 한다는 뜻이 아니다. Luna는 구체적인 검토 패킷을 만들어 사용자가 필요한 부분만 확인하게 하고, 확인되지 않은 데이터의 상태는 그대로 유지한다.

## 6. 설계 변경 정책

새 출처나 에셋 때문에 설계 변경이 필요하면 `work/DECISIONS.md`에 문제, 선택지, 결정, 영향을 받는 task/데이터, migration 및 검증을 기록한다. 단순 파일 이름/컴포넌트 분리는 자율적으로 결정 가능하다. 전신 범위 축소, 근거 없는 내용 승격, 원본 변경, 치료 추가는 일상적 구현 선택으로 처리하지 않는다.

## T10 추가 조사 — 용어와 오픈소스 (2026-09-25)

용어별 근거는 `atlas-data/terminology/learning-names.json` sources에 기록한다. 국립국어원 온용어, KMLE의 대한해부학회/의협 용어 항목, 디지털집현전, KOCW를 교차 참조했다. 학회 출처를 재수록한 페이지와 원 학회 파일을 구별한다. 원문 글자 손상이 있는 한자는 보류한다. 검색 색인만 확인한 PDF는 원문 검토 완료로 세지 않는다. 전신 용어를 모두 조사한 것은 아니다.

- [Three.js](https://github.com/mrdoob/three.js): 공식 WebGL 라이브러리, [MIT](https://threejs.org/license/). GLTFLoader/OrbitControls 기반으로 T12 어댑터 도입을 우선 검토. 현 T09 표면 picking/좌표/triangle regression이 조건.
- [glTF Transform](https://github.com/donmccurdy/glTF-Transform): glTF 처리/최적화 도구. T16 부위별 자산 파이프라인 후보. 단순 파일 압축과 topology 변경을 구별하며 annotation hash를 갱신해야 한다.
- [Fuse.js](https://github.com/krisk/Fuse): 큰 용어 사전의 유사 검색 후보. T10은 작은 순수 함수 검색기로 요구를 먼저 검증했다. 동의어 사전 자체를 만들어주지는 않는다.
- [Z-Anatomy Unity project](https://github.com/LluisV/Z-Anatomy): 별도 해부학 자산 조사 후보. Unity 프로젝트이므로 웹 앱에 그대로 붙일 수 없다. 코드와 모델 각각의 출처·라이선스·개별근 분리·부착면을 확인해야 한다. `github.com/Z-Anatomy/Models`는 이번 확인에서 404여서 실행 의존성으로 삼지 않는다.

오픈소스는 렌더링·검색·변환 시간을 줄이지만 전신 한국어/한자 근거, 해부학적으로 검토된 부착영역, 평가 내용을 자동 완성하지 않는다. 이번 T10은 새 외부 패키지를 설치하지 않았다.
