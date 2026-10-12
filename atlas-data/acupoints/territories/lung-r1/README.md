# 폐경 부분 학습 면 — runtime v1

`masks.json`은 현재 canonical carrier의 **아래팔 부분 영역 양측 2개 mask**다. 전체 폐경 면·피부 스캔·확정 경근 경계가 아니다. LU6/7/8의 확인된 교육용 위치를 포함하고 LU1–5/LU9–11의 위치는 변경하지 않는다.

오른쪽은 AT20의 control/seed를 공통 `replayTerritoryBoundary`로 재현했다. 왼쪽은 실제 left carrier와 native source 주소 4개에서 독립 작성했으며 reflection을 사용하지 않았다. 오른쪽 65 controls, 왼쪽 67 controls, 각 351 faces다. 원래 rejected-face hole과 component seam을 보존한다.

`triangleIds`는 정렬된 face ID, `vertexWeights`는 시각 농도/feather용 `[vertex,weight]`다. weight는 확률·치료 강도·해부학적 확신도가 아니다. 위치/normals는 등록된 carrier를 공유한다. carrier/frame/unit/pose/side/hash가 바뀌면 stale 실패이며 자동 remap하지 않는다.

`scope=real_input`, `kind=teaching_region`, `basisKind=surface_learning_connection`, `interpretation=ai_proposal`, `canonicalBoundaryClaim=false`, `precision=educational_approximation_not_skin`을 유지한다. localObservation supported, professorReview not_performed, publicRedistribution held는 독립 상태다.

상세 annotation·source cache·실패 이력은 `work/evidence/AT21/run-r1/`에 있고 learner bundle에 import하지 않는다. 제품에는 이 compact package만 영역 ON 시 지연 로딩한다. DEV 겹침/revision 표본은 별도 코드이며 제품 JSON·production build에 포함하지 않는다.

다음 mask 편집은 기존 point/route/carrier의 좌표·hash를 보존하며 mask revision/content hash만 갱신한다. AT22의 triangle brush는 아직 구현하지 않았다.
