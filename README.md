# HUMAN ATLAS

OpenSim 기반 해부학 학습자료를 모아 둘 프로젝트 폴더입니다. 이번 단계에서는 OpenSim 팀의 공식 모델 저장소에서 모델과 3D 형상 파일을 받았습니다.

## 받은 자료

- `OpenSim_Models/Models/`: OpenSim 모델 파일(`.osim`)과 관련 설명·예제
- `OpenSim_Models/Geometry/`: 모델이 참조하는 표면 메시 파일(주로 `.vtp`)
- `OpenSim_Models/Models/Rajagopal/`: 전신 근골격 모델 `Rajagopal2016.osim`, 수정 모델 `RajagopalLaiUhlrich2023.osim`, 관련 뼈 메시와 원본 설명
- `OpenSim_Models/Models/Gait2392_Simbody/`, `Gait2354_Simbody/`: 보행과 하지 근골격계를 다루는 대표 모델
- 그 밖에 상지, 손목, 달리기, 보행 교육 예제가 함께 들어 있습니다.

현재 받은 묶음에는 `.osim` 모델 34개와 `Geometry/` 메시 파일 325개가 있습니다. 시작점으로 전신 모델을 열려면 OpenSim에서 `OpenSim_Models/Models/Rajagopal/Rajagopal2016.osim`을 선택하세요. 저장소의 설명에 따르면 이 파일은 OpenSim 4.5 형식으로 갱신된 모델입니다.

## 자료의 범위

여기 담긴 자료는 인체의 모든 해부 구조를 담은 해부도 데이터베이스가 아니라, 움직임과 근골격계를 계산·시각화하기 위한 OpenSim 모델입니다. 장기, 혈관, 신경, 피부 등 전신 해부 구조 전체가 들어 있지는 않으며, 부위와 목적에 따라 구조가 생략되거나 단순화되어 있습니다. OpenSim 응용 프로그램 자체는 이 폴더에 포함하지 않았습니다.

## 출처와 이용 조건

- 공식 저장소: [opensim-org/opensim-models](https://github.com/opensim-org/opensim-models)
- 내려받은 브랜치와 커밋: `master`, `d9b05d470b1a481c222372c85b75772faf8f7792` (커밋 날짜 2025-11-05)
- 내려받은 날짜: 2026-09-25
- 저장소의 `Models/`와 `Geometry/` 경로를 원본 상태로 보관했습니다. 이 안내문 외에 모델 자료를 수정하지 않았습니다.
- 모델마다 이용 조건과 인용 방법이 다를 수 있습니다. 재배포·수정·외부 공개 전에 각 모델의 설명 파일과 [OpenSim 공식 모델 목록](https://opensimconfluence.atlassian.net/wiki/spaces/OpenSim/pages/53090607)을 확인하세요. 예를 들어 공식 목록은 Gait2392에 CC BY 3.0, Rajagopal 모델에 MIT 조건을 표시합니다.

Rajagopal 모델 설명과 참고문헌은 [`OpenSim_Models/Models/Rajagopal/README.txt`](OpenSim_Models/Models/Rajagopal/README.txt)에 있습니다.
