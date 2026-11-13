# AT20 영역 정의와 경계 입력 v1

이 폴더는 **offline authoring input**이다. learner import/renderer에 등록한 face mask가 아니다.
`territoryBoundary.ts`는 기존 `Territory` 어휘와 `anchorAdapter`의 hash/frame/unit/pose/side/rights 검사를 재사용한다. AT5 위치 compiler의 실제 landmark 입력과 AT6 성공 projection을 읽으며 경혈 재승인·재배치·별도 compiler/overlay/CameraSessions를 만들지 않는다.

`definitions-r1.json`은 14경맥 각각의 지표·전후측 학습 면 계획·분지 정책·불확실성을 고정한다. `sourceRelations`는 읽은 공적 자료의 **점 위치 관계**이며 `viewDrafts`는 AI의 추가 작성 계획이다. `types`의 경근, 피부, 교수 해석, 학습 연결 면은 독립이다. 임독맥 경근은 `not_applicable`다. 원문 전체 유주나 14개 완성 mask로 세지 않는다.

`lung-forearm-right-boundary-r1.json`은 현재 오른쪽 아래팔 carrier의 실제 boundary 입력이다. 해부학적 근거는 AT6의 source-addressed 팔오금/요골 수근/힘줄 관계와 KMCRIC LU6/LU8 위치 서술이다. AT3 grid의 폭과 양끝 선택은 **AI가 작성한 부분 학습 구간**이며 문헌의 확정 외곽선이 아니다. LU6/7/8을 포함하고 LU5/LU9/엄지·흉부는 이 표본 밖이다. 두 결손을 구멍으로 남겼으며 피부가 없다는 이유로 다른 표면에 옮기지 않았다.

## AT21 입력 방법

1. `carrierBinding.manifestSha256` 및 해당 chunk binary SHA, topology SHA, dataset/frame/metre/static pose/right를 검사한다. 원본 geometry를 복제하지 않는다. carrier 교체는 stale 실패이며 자동 remap하지 않는다.
2. 공통 `validateTerritoryBoundary(draft, carrier, context)`로 loop와 seed를 재현한다. 결과 face-set hash를 `handoff.candidateFaceSetSha256`, count를 `expectedFaceCountForReplay`와 대조한다. 확인된 수는 **351 faces / 65 controls / outer 1 + holes 2**다.
3. 각 loop의 연속 vertex pair와 마지막→첫 pair를 barrier로 삼는다. 같은 carrier의 face adjacency에서 seed triangle1174로 연결된 내부를 채운다. 구멍과 component 경계를 유지한다. 여기에는 최종 `triangleMask`, weight 또는 GPU geometry가 없다.
4. AT21에서 compact `triangleIds/weights`를 저장하고 기존 overlay·scene/camera에서 점/카드/따라보기와 함께 색 면을 표시·검사한다. 새 body mesh/renderer나 근육 material 영구 변경은 하지 않는다. weight·alpha·feather는 시각 값이다.
5. 교수 검토와 공개 재배포는 held/not_performed를 보존한다. 오른쪽을 반사해 왼쪽 검증이라고 부르지 않는다. 이 부분 표본 외의 LU 영역과 다른 13개 영역은 별도 실제 annotation이 필요하다.

개발 evidence/source summaries/private 교재는 learner bundle에 import하지 않는다. AT21은 필요한 compact 경계/출처 ID만 공통 projection으로 연결한다. 현재 source register와 원문 대조 기록은 `work/evidence/AT20/run-r1/`에 있다. 본 task에 첨부 사진/교수 교재 원문은 제공되지 않았다.

검사 명령(저장소 root):

```sh
python3 work/evidence/AT20/run-r1/validate-evidence.py
```

NumPy/Pillow가 있는 Python으로 `inspect-boundary.py`를 실행한다. Node 검사 명령은 `atlas-web`에서 `node --experimental-strip-types --test src/viewer/acupoints/territoryBoundary.test.ts`다. 역사 authoring 원본을 실행하거나 carrier binary를 다시 만들지 않는다.
