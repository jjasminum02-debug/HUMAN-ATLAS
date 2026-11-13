# HUMAN ATLAS — 출처와 이용 조건 (NOTICE)

교육용 해부학 학습 앱의 시제품이다. 진단·치료·침 시술 안내가 아니다.

## 이 저장소의 코드
아직 라이선스를 정하지 않았다. 따로 허락하기 전까지 코드는 저작권자가 모든 권리를 가진다(All rights reserved).
아래 제3자 자료는 각 자료의 조건을 따른다.

## 3D 모형
- **Z-Anatomy** — The libre 3D atlas of anatomy, CC BY-SA 4.0.
  원본: https://github.com/Z-Anatomy/Models-of-human-anatomy (커밋 c7010a9).
  이 프로젝트는 원본을 웹용 GLB로 바꾸고, 상세 단계·rig 가중치·부착 면·경혈/경근 위치를 계산했다.
  이렇게 고친 형상과 그 파생 데이터(`atlas-data/runtime`, 빌드에 들어가는 형상)는 **CC BY-SA 4.0**으로 공개한다.
  원본 `Startup.blend`는 저장소에 넣지 않는다(`atlas-data/source-cache`, git 제외).
- **BodyParts3D** — The Database Center for Life Science, CC BY-SA 2.1 Japan.
- **MakeHuman** 피부 재질(`atlas-data/anatomy/skin/at10-appearance-v1`) — CC0 (파일 안 표기).
- **OpenSim models** (opensim-org/opensim-models: Rajagopal2016, Arm26, WristModel) — 근육 작용을 모멘트 팔로 확인하는 데만 썼다.
  모델 파일은 저장소에 넣지 않는다. 각 모델의 이용 조건을 따른다.

## 내용 출처 (해부·경혈·경근)
- **Wikipedia** (en, CC BY-SA 4.0): 근육 신경·혈관·작용 정보상자 값과 혈관 가지 관계를 대조. 확인 기록 `atlas-data/anatomy/*-checks.json`.
- **UAMS** Department of Neuroscience 근육 표, **Kenhub** "Key facts": 두 번째·세 번째 대조 출처. 값만 대조하고 문장은 옮기지 않았다.
- **acupuncture.com** 경혈 위치 문장, **acupuncture-notes.com** 경근 경로 문장: 대조어 일치만 확인했다. 원문은 저장소에 넣지 않는다(확인 기록에는 주소만).
- **『靈樞』經筋** (공유 저작물): Wikisource 『靈樞經』 四庫全書本 권4.
- **WHO Standard Acupuncture Point Locations (2008)**의 위치 관례를 따라 AI가 규칙 초안을 썼다(`atlas-data/pipeline/acupoint_locations.py`).
- 기시·정지 설명은 사용자가 제공한 강의 자료와 위 출처를 대조해 새로 쓴 한국어 요약이다. 강의 자료는 저장소에 넣지 않았고,
  2026-11-13에 저장소·빌드의 모든 한국어 문장을 강의 자료 본문과 비교해 그대로 옮긴 문장이 없음을 확인했다(가장 긴 일치는 해부 용어 18자).

## English summary
Code: no license granted yet (all rights reserved). Modified Z-Anatomy geometry and derived data: CC BY-SA 4.0.
BodyParts3D: CC BY-SA 2.1 JP. MakeHuman material: CC0. Wikipedia-derived checks: CC BY-SA 4.0.
Other sources (UAMS, Kenhub, acupuncture.com, acupuncture-notes.com, lecture notes) were used for fact checks only; their wording is not included.
Educational prototype; not medical, diagnostic or needling guidance.
