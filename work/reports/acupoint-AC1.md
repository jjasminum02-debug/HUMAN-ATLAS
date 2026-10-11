# AC1 — 경혈 학습 체표·좌표 연결

2026-10-11. **기술 검토 prototype은 검증됨; 실제 혈위는 LU1·LU9·LU11 각각 미확정. 전체 AC1 acceptance는 partial.** 제품에 내보낸 경혈 좌표는 0개다. AC2는 실행하지 않았다.

이번 명시적 요청을 AC1 구현 착수의 근거로 사용했다. 과거 deferred/다른 task의 미승인 상태를 전역 구현 차단으로 사용하지 않았다. `work/EXECUTION.json`에 숫자 task/기존 queue를 변경하지 않는 `featureWorkUnits.AC1` 기록만 추가했다. NEXT/STATUS 투영은 sync 및 --check로 확인했고 기존 내용은 보존했다.

## 구현과 진입점

기존 앱의 개발 서버에서 `http://127.0.0.1:5183/?acupointReview=1` → **경혈 체표 검토**를 누른다. 기존 화면·renderer·AnatomySceneRoot를 사용한다. 홈·로딩·보기옵션은 변경하지 않았다. 검토 패널의 3점 선택·전면/사선/측면·이전 시점·체표 패치 표시만 제공한다. tour/11점/경맥 선/영역 편집은 구현하지 않았다.

- 공통 계약: PointConcept, PointInstance, ChannelRoute, Territory 및 SinewPath/LearningAssociation/명시적 선택 타입. 위치 문장은 `point-concepts.json`, 모델 anchor는 `prototype.json`에 분리했다. 경로·영역 데이터는 0개이며 세 점을 경맥 유주 선으로 연결하지 않았다.
- Adapter: carrier의 dataset revision/frame/metre/unit/정지 pose/subject side/topology SHA를 검증하고 고정 triangle+barycentric으로 재현한다. LOD의 triangle을 최근접 근육 탐색으로 치환하지 않는다. topology hash는 Float32 positions+Uint32 indices의 고정 byte 표현이다. 렌더 index는 Uint16을 사용한다.
- Overlay: 같은 root 아래 group 1개. 새 renderer/canvas/RAF/인체 복사본 없음. 점 클릭은 실제 보이는 해부 구조보다 앞에 있을 때만 우선한다. carrier 면은 해부 선택을 가로채지 않는다.
- 수명: 취소 가능한 lazy data fetch와 세대 token, 구독/geometry/material/DOM listener 해제. 움직임 시작과 비활성 화면/context loss에서는 정지 체표를 종료한다. 움직임 resource의 늦은 연결도 static overlay를 해제한다.
- 카메라: 선택만으로 이동하지 않는다. 검토 시점 버튼만 이동한다. 종료 시 원래 시점으로 복원하되 사용자 orbit/키보드/기존 관찰 시점·화면 맞춤 명령이 우선한다. 점 클릭 뒤 OrbitControls의 잔여 damping으로 복원 카메라가 미세하게 어긋나는 결함을 수정했다. 공통 카메라 명령 관찰 hook은 renderer/loop를 추가하지 않는다.

## 기존 source 후보와 carrier 결정

현재 runtime은 ZA + 등록된 BP3D 보충 + 신경 합성 dataset이다. frame은 `HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR`, 단위 m, 기준 pose는 `ZA-9f08a17ea0115fed-frame0-autoexec-off`다. 인체 오른쪽은 음의 X이며 전면은 양의 Z다. 외부 경혈 점 좌표를 복사하거나 모델 높이를 임의 정규화하지 않았다.

기존 T98 전체 inventory와 실제 cache를 확인했다. ZA의 Skin → Dermis → Papillary/Reticular layer 컬렉션은 mesh member가 비어 있다. BP3D metadata의 skin 항목은 존재하지만 현재 캐시에 해당 체표 geometry가 확보되어 있지 않다. 이는 원본 전체에 피부가 절대로 없다는 판정이 아니다. ZA Nail plate.r/Perionyx.r은 실제 mesh가 있으며, 원본을 저장하지 않는 Blender probe로 읽었다. Nail plate.r은 여러 손가락을 포함하므로 연결 component와 독립적으로 대응한 오른쪽 엄지 끝마디뼈를 대조했다.

**선택: 같은 ZA에 맞춘 국소 학습용 체표 패치 작성.** 다른 인체의 전신/손 자세/표면을 새로 정합하는 방법은 추가 모델 취득, 비강체 손 정합, 손톱·주름 재검증 및 용량 비용이 커서 이번 3점 범위에 채택하지 않았다. 기존 정합 geometry에서 쇄골/늑골, 노뼈/주상골, 엄지/손톱 기준을 재사용하는 국소 패치는 867 vertices/1,536 triangles로 작성할 수 있었다. 전신 skin을 확보했다고 보고하지 않는다.

`build_carrier.py`는 hash가 확인된 기존 detail GLB의 source matrix를 한 번 적용하고, 앞쪽 envelope+명시적 clearance로 17×17 패치 3개를 작성한다. envelope를 찾지 못한 vertex에는 가장 가까운 source vertex의 높이를 사용한다. 그 수와 입력 SHA는 `carrier-validation.json`에 남겼다. 이 보간과 4mm/1mm clearance는 작성용 근사이며 피하조직 두께나 경혈의 정확성 근거가 아니다. 위치 제안 XY는 원래 모델의 골성/손톱 기준 bounds에서 명시적 비율로 계산했고, 비례촌/손가락촌을 고정 mm로 환산하지 않았다.

캐리어 SHA: `1f0cc8012af79a9f849946bd9739e8725c72009e61783d13a6672ae106935793`.

## 대상별 실제 위치 상태

문헌 위치와 3D 위치를 구별했다. [KMCRIC](https://www.kmcric.com/database/acupoint/LU)로 이름/코드를 확인하고 [WHO 2008, 2009 재인쇄 원문](https://www.medbox.org/index.php/dl/627a4de115110145a1723f64)의 인쇄 p.26/30/31과 기준 구조를 대조했다. 공식 WHO PDF URL은 403이어서 동일 WHO 저작의 보관본을 열었으며, 책 전체를 다운로드하거나 외부 좌표를 채택하지 않았다. 사용자 교재 판본은 미입력이다.

| 대상 | 현재 모델에서 확인한 기준 | 아직 확인하지 못한 것 | 처리 |
|---|---|---|---|
| 오른쪽 LU1 중부 | 쇄골, 첫째/둘째늑골 및 늑연골, 대흉근/근막 주변 | 실제 외측 첫째늑간 체표, 앞정중선에서 6 비례촌의 개인 비율, 피부/피하 두께 | 위치 제안만; unresolved |
| 오른쪽 LU9 태연 | 노뼈 말단, 주상골, 긴엄지벌림근 주변 | 손목 주름, 노동맥, 정확한 건의 자쪽 함요·체표 자세 대응 | 위치 제안만; unresolved |
| 오른쪽 LU11 소상 | 엄지 끝마디뼈와 원본 손톱/손톱주위 component | 실제 피부 외피, 손톱 요측 모서리의 방향/몸쪽 기준 및 0.1 손가락촌 | 위치 제안만; unresolved |

LU11 전면에서는 제안점이 현재 보이는 뼈 표면보다 가쪽에 놓인다. 손톱 source와 뼈의 관계를 조사했지만 그 사이의 피부 외피를 검증한 결과가 아니며, 해당 patch의 빈 구역 보간도 많다. 이 결과를 정확한 소상 위치로 채택하지 않았다. LU1/LU9도 근육/골성 기준 표면에 붙은 사실만으로 피부 혈위가 맞다고 주장하지 않는다.

권리와 검토는 독립 상태다. 원본 ZA SHA와 pinned README/기존 rights-scope의 CC BY-SA 4.0·상류 attribution을 보존한 비공개 로컬 기술 관찰/파생 작성은 supported로 기록했다. 출처 예외/상류 object 계보를 새로 승인하지 않았다. **혈위 검증 unresolved / AI placement proposal true / 교수 검토 not_performed / 공개 재배포 held**를 유지한다. 표준 위치 문헌 대조는 모델 좌표 승인이나 교재·교수 검토가 아니다.

## 실제 검증과 비용

`validation.json`에 관련 자동 검사와 화면 evidence를 연결했다. 3점 × 전면/사선/측면의 9개 screenshot은 하나의 root `d836a64c-bbb0-4c10-8402-cb979117d33c`에서 남겼다. 각 camera transition 종료와 target 일치를 확인했다. 별도 세션의 동일 카메라 OFF/ON 비용 benchmark와 마지막 카메라 우선권 검증은 서로 다른 root ID로 구별해 기록했다.

- anchor/frame/unit/pose/side/hash/index/barycentric/degenerate triangle/제품 projection/예산 음성 검사 + 기존 camera/picking 회귀: **9/9 pass**. TypeScript typecheck와 production Vite build pass.
- 실제 LU11 점 클릭, 뒤쪽 LU1의 가림 클릭 차단, 원시점 복원, 기존 관찰 방향 우선권 확인.
- 오른쪽 쇄골 선택·뼈 ON·근육 OFF 보존. 3회 ON/OFF 후 geometry 수가 동일하게 반환되고 OFF update=0. 기존 움직임 시작 시 overlay 제거와 정상 원자세 복원 확인. 이는 AC5의 30회/3해상도 전수 검증으로 확장해 부르지 않는다.
- production output에서 검토 module/carrier/prototype JSON/경혈 UI가 없는 것을 검사했다. 위치 제안 3개는 개발 검토 evidence에만 존재한다.

| 비용 | 측정 |
|---|---:|
| prototype data bytes | 72,427 |
| carrier topology | 867 vertices / 1,536 triangles |
| carrier 렌더 position/normal/index buffers | 30,024 bytes |
| 점 포함 추가 GPU attribute/index buffer 추정 | 44,280 bytes |
| 점 포함 실제 추가 render triangles | 2,040 |
| 같은 카메라 draw calls | 672 → 676 (+4) |
| 같은 카메라 render triangles | 486,184 → 488,224 |
| GPU geometry 객체 | 397 → 401 → 397 (해제) |
| shader programs | 2 → 4 → 2 (해제) |
| 추가 texture | 0 |
| carrier 포함 보수적 overview bytes 상한 | 20,114,943 / 20,971,520 |
| carrier 포함 overview triangles 상한 | 899,252 / 1,000,000 |

20MiB overview / 96MiB geometry / 1M active triangles / 8MiB chunk 예산은 변경하지 않았다. 캐시 bytes에 overlay buffer 비용을 더해 guard를 수행한다. GPU driver 전체 heap이나 elapsed GPU time은 측정하지 않았다. GPU bytes는 실제 typed-array buffer의 upload 비용 추정이며 CPU JSON heap/driver overhead와 구별한다. 투명 양면 material의 불필요한 두 pass를 `forceSinglePass`로 수정한 뒤 위 수치를 측정했다.

## 보존과 로컬 커밋

시작 HEAD와 전체 status/5,956개 기존 WIP file hash는 `before/baseline.json`에 있다. 원본 .blend SHA 불변을 다시 확인했다. 기존 WIP 중 byte 변화가 있는 경로는 DatasetSceneAdapter뿐이며 AC1 hook 3개를 제거하면 시작 파일과 byte 단위로 동일하다. OpenSim_Models/원본/T13/기존 task·디자인에는 쓰지 않았다.

커밋 포함: AC1 schema/adapter/개발 overlay·검토 UI, 기존 viewer의 개발 진입 연결, 카메라 명령 구독 hook, DatasetSceneAdapter의 AC1 motion-start hook만, EXECUTION의 AC1 feature record, 이 보고서와 선별 evidence. 기존 DatasetSceneAdapter WIP는 HEAD에 AC1 추가분만 적용한 별도 index snapshot으로 제외한다.

커밋 제외: 모든 기존 사용자 WIP, 원본/source-cache/OpenSim_Models/T13, 기존 acupoint 설계·계획 문서, `before/`의 원본 코드/EXECUTION 전체 복사본, 최종 커밋 뒤 작성할 receipt. 포함/제외 경로는 `commit-scope.json`; 해시/잔여 변경은 로컬 `commit-receipt.json` 및 최종 응답에 기록한다.

남은 작업은 세 혈위의 대상별 체표·landmark 정합과 사용자 교재 대조다. 전신 skin/11점/tour/경맥·영역 확장이나 AC2는 이 보고서의 완료 범위가 아니다. 다음 작업은 자동 실행하지 않는다. push/배포/환자 진단·치료·침 시뮬레이션 없음.
