# V1 외관 반려와 수정 기준 — 2026-10-15

사용자는 작업 중 전신 화면을 보고 “사람 같지 않다, 다른 해부학 모형 사진을 찾아 그렇게 구성”을 요청했다. V1의 기술 구현/발 질감 변화는 전체 외관 합격이 아니다. 현재 외관은 반려 상태로 남긴다. 기존 F1/F2 수치/국소 정합 결과는 보존하지만 미적 품질 승인을 의미하지 않는다.

## 실제 확인한 참고

- Complete Anatomy 공식 표면해부/골격/근육 모델: https://3d4medical.com/blog/female-atlas-update
- 직접 브라우저로 확인한 공식 이미지: https://cdn.3d4medical.com/media/blog/december2022/female-atlas-3.jpg
  - 관찰: 전신에서 목·어깨·흉곽과 허리/골반/사지 윤곽이 연속적이고, 피부의 잔무늬보다 큰 해부학 형태가 먼저 읽힌다. 이것을 외관 방향으로 채택한다. 이 작은 스크린샷만으로 세밀한 형상 정확도를 보증하지 않는다.
- Visible Body의 실제 피부 선택/관찰 흐름: https://www.visiblebody.com/blog/how-to-use-visible-body-to-lecture-in-3d
- MakeHuman 공식 body controls: https://static.makehumancommunity.org/makehuman/docs/modeling_the_body.html
  - 성별/나이/근육/체중/키/비율 등이 별도 조절된다. 단일 target를 적용했다고 완성된 제품형 인체가 되는 것은 아니다.
- 상용 비교 후보: https://3dmolier.com/3d-model/realistic-skin-young-man-with-full-body-anatomy
  - 상세 사진 피부/내부 구조를 갖춘 상용 자산. 구매/다운로드/권리 승인은 하지 않았고 앱에 복제하지 않았다. 현재 source를 버리고 즉시 대체할 정합 근거가 아니다.

## 코드와 형상에서 확인한 원인

`fit_at10_skin.py`는 MakeHuman base+단일 asian male young target에서 source를 만들고, native bone/cap 및 authored offset에 polyharmonic 변형을 맞춘다. 이것은 관통과 대응을 해결하는 출발점이지 자연스러운 피부 실루엣을 보증하지 않는다. 현재 r-series → f2c3는 이 전신 기반 위에 손발의 국소 수정이 누적된 자산이다.

`shape-audit.json`은 같은 source vertex cohort의 변형 전후 extents다. 머리 cohort 깊이 약1.15배, 목 주변 cohort 폭 약1.76배, 몸통 cohort 높이 약1.36배다. cohort는 단순 source 좌표 mask이므로 표준 목 둘레/정상 체형 비율이 아니다. 다른 자세, 경계 영향이 섞이므로 단순 역스케일로 교정하면 안 된다. 자연스러운 source shape와 pose 대응을 추가 검수해야 한다는 진단 근거다.

현재 피부는 단일 mesh이고 안구/치아 같은 별도 표면은 추가하지 않았다. 피부 텍스처만으로 안구와 입안을 만들 수 없다. 원형/ZA 실제 구성과 노출을 F3에서 해결해야 한다. 사진의 고정 음영/털이 저해상도 화면에서 얼룩처럼 보이는 문제는 V2 지역별 재질 검토 대상이다.

## 실행 범위와 다음 작업

- 이번 V1: 고정 F2 geometry에 실제 texture package와 공통 검증/비용/해제 경로, 전후 화면, 실패/반려 기록. geometry 원본 보존.
- F3: 얼굴/귀/목의 대응 및 자연스러운 형상, 필요한 눈/입 구성. 전신·상반신에서도 검수. 자동 실행하지 않음.
- F4: 몸통/어깨/사지 연결의 형태와 정합. 관통 0만으로 통과 금지.
- V2: 최종 silhouette/UV/normal/roughness/색/손발톱의 실제 외관. 큰 체형 오류를 재질로 숨기지 않음.
- 새 task 번호나 원본 전체 재조사 대신 기존 F3/F4/V2 프롬프트에 이 조건을 추가했다.

사용자 요청의 최종 품질은 아직 달성하지 못했다. 기존 앱의 카메라/레이아웃 변경, 상용 자산 무단 복제, F1/F2 재실행으로 우회하지 않는다.
