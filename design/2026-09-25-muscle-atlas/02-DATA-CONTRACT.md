# 데이터 계약 v0.1 — T03에서 실제 스키마로 구현

이 문서는 규범적 설계다. JSON Schema 파일이나 검증기가 이미 구현되었다는 뜻은 아니다. T03에서 JSON Schema Draft 2020-12와 런타임 검증을 구현하고, 스키마로 표현하기 어려운 교차 참조·출판 규칙은 독립 검증 코드로 검사한다. ID와 관계를 먼저 고정하고 기능·평가 데이터는 이후 채운다.

## 1. 엔터티와 연결

| 엔터티 | 최소 필드/관계 | 중요한 제약 |
|---|---|---|
| MuscleConcept | id, entityType, regionIds, parentId?, standardRefs, applicability | ID는 이름·언어·메시 파일명과 독립 |
| AnatomicalInstance | id, conceptId, side, variantId? | side = left/right/midline/unpaired, 좌우 없는 것을 임의 복제 금지 |
| MusclePart | id, parentMuscleId, partKind, termIds | head/portion/belly 구분, 상위 개념과 수 집계 분리 |
| Term | id, conceptId, language, script, text, termRole, edition, evidenceIds, reviewState | 언어별 여러 명칭 허용, 출처 없는 한자 생성 금지 |
| Structure | id, kind, parentId?, termIds | bone/landmark/tendon/fascia/aponeurosis/skin/other 등 |
| Attachment | id, muscleOrPartId, role, targetStructureId, landmarkId?, descriptionClaimId, variantContext | 하나의 근육에 기시·정지 여러 개 허용 |
| SpatialAnnotation | id, attachmentId, instanceId, assetRevision, geometry, frameId, poseId, precision, reviewState | 텍스트와 별도로 좌표 검토 |
| MeshAsset | id, revision, sourceId, hash, uri, format, units, axes, pose, licenseId | 에셋마다 라이선스·좌표계 고정 |
| MeshMapping | id, instanceIds, partIds, meshIds, representationType, reviewState | 다대다, 전체/부분/통합 메시 구분 |
| JointAction | id, muscleOrPartIds, jointIds, action, postureConditions, contractionRole, evidenceIds | 자세·과제 없는 전역 역할 단정 금지 |
| Innervation | id, muscleOrPartId, nerveStructureId, rootLevels, context, evidenceIds, reviewState | 분절 표기 차이 보존, 텍스트 관계부터 지원 |
| Assessment | id, targetFunctionIds, relatedMuscleIds, scope, purpose, protocol, observations, interpretations, limitations, safety, evidenceIds | 특정 근육 독립 평가인지 근군/과제 수준인지 구분 |
| Source | id, title, authors, edition, year, urlOrLocalRef, accessDate, license, allowedUses | 자료 접근 가능성과 공개 가능성 분리 |
| Evidence | id, sourceId, locator, supportedClaimIds, excerptHash?, evidenceKind | 페이지/표/절/그림 등 실제 위치 |
| Claim | id, subjectId, field, value, evidenceIds, attribution, reviewState | 근육 전체가 아닌 주장 단위 출처 |
| Review | id, targetId, targetRevisionHash, reviewerKind, reviewerId, decision, reviewedAt, notes | 변경 전 리뷰를 변경 후 데이터에 재사용 금지 |

`entityType`은 individual_muscle / muscle_group / muscle_part / variant로 구분한다. OpenSim actuator는 이 열거형에 억지로 넣지 않고 별도의 ModelElement로 보존한다. ModelElement→MuscleConcept 매핑은 verified/provisional/unmapped를 갖고 모델 버전에 종속된다.

## 2. 다국어 규칙

- `ko` 한글 표준명과 관용명/구용어를 termRole로 구분한다.
- 한자 표기는 한국어 용어의 한자 표기임을 `language=ko, script=Hani`처럼 기록한다. 중국어 번역과 혼동하지 않는다.
- 영어는 preferred/synonym을 구분하고 영미 철자·관용명·이전 명칭을 별칭으로 수용한다.
- 라틴어와 TA/FMA 등 외부 식별자는 내부 교차 확인에 사용하되 대조가 안 된 ID는 넣지 않는다.
- NFC 정규화, 영문 대소문자·공백 처리를 적용한다. 원표기는 보존한다.
- 한글 초성 검색은 후순위지만 검색 인터페이스가 교체 가능하도록 만든다.
- 이름이 같거나 비슷한 서로 다른 구조는 부위/좌우/근두를 함께 보여 주고 자동 병합하지 않는다.
- 한자명 미확인 시 null + missingReason으로 남긴다. 영어/한글만으로 학습을 계속할 수 있지만 “세 언어 완성”에는 포함하지 않는다.

예시 화면의 문자열도 처음에는 fixtures로 분리한다. 교과서나 용어집의 정확한 판본과 대응을 확인한 뒤 실제 학습 데이터로 승격한다. 자동 번역은 후보 생성에만 사용한다.

## 3. 기시·정지와 부착부

`Attachment.role`은 origin / insertion / other_attachment / undifferentiated로 한다. 기시·정지 구분이 해당 근육에 적절하지 않거나 출처마다 다른 경우 undifferentiated + 이유를 허용한다. 억지로 빈 기시·정지를 만들어서는 안 된다.

부착부에는 다음 정보를 담는다.

- 표적 구조 및 구체적인 표지: 뼈 이름만 적는 것으로 완료하지 않는다.
- 범위 설명, 근두/부분, 건·건막을 통한 연결 여부.
- 출처별 기술 차이와 채택한 설명, 적용 범위.
- 부착이 넓거나 여러 구조에 걸치는 경우 각각의 관계와 전체 연결.

텍스트 근거와 좌표는 분리한다. `Attachment`가 확인되어도 `SpatialAnnotation`이 없을 수 있다. 이때 문장은 표시하지만 가짜 좌표를 생성하지 않는다. 반대로 보기 좋은 메시가 있어도 기시·정지 근거가 없으면 정확한 부착 위치라고 표시하지 않는다.

## 4. 공간 좌표 계약

제품 내부 단위는 meter로 통일하고 임포트 시 원본 단위와 변환을 보존한다. 표시용 mm 변환은 UI에서 명시적으로 수행한다. 축은 예를 들어 right-handed, +X=환자 왼쪽, +Y=머리 방향, +Z=앞쪽으로 고정하고 카메라·라벨까지 일관되게 사용한다. 최종 축 결정은 T02의 DECISIONS에 고정한다.

`geometry.kind`는 point / polyline / surface_patch. 권장 필드:

```text
frameId, assetId, assetRevisionHash, topologyHash, instanceId, poseId
geometry: point(position) | polyline(vertices) | surface_patch(triangleIds/barycentricAnchors)
precision: representative | approximate_extent | reviewed_extent
method: source_annotation | manual_mapping | model_derived
transformChain, landmarkChecks, reviewState
```

- 가능한 한 대상 뼈/구조의 로컬 좌표에 부착하고 세계 좌표는 변환 결과로 계산한다.
- 부착점을 카메라 좌표에 저장하지 않는다.
- 표면 face index는 리메시/LOD/압축으로 바뀔 수 있다. 기준 메시 topology hash를 고정하고 LOD용 재투영 매핑을 따로 검증한다.
- 원본 업데이트로 메시·단위·축·정합이 바뀌면 관련 annotation을 stale로 처리한다.
- 좌우 반사로 생성한 좌표는 derived/provisional이며 자동으로 reviewed가 되지 않는다.
- 같은 축·단위여도 다른 인체의 형태가 일치하지 않는다. OpenSim↔표면 Atlas 등록은 별도 변환과 표지 오차 검증이 필요하다.
- 구조 V1에서는 정해진 기준 포즈에서만 부착영역 정확도를 주장한다. 임의 포즈 변형은 하지 않는다.

OpenSim을 가져올 때는 body/frame 변환, joint의 기본 coordinate, mesh scale factors, fixed/via/moving/wrap point를 구별한다. 첫 점과 끝점을 무조건 해부학적 기시·정지 영역으로 승격하지 않는다. 공식적으로 근육 경로는 여러 종류의 점과 wrapping으로 표현된다. [OpenSim Muscle Editor](https://opensimconfluence.atlassian.net/wiki/spaces/OpenSim/pages/53090145)

## 5. 출처와 검토 상태

독립적으로 저장할 상태:

```text
technicalStatus: valid | invalid | unchecked
evidenceStatus: missing | located | conflicting
reviewState: draft | needs_review | reviewed | held | stale
attribution: source_summary | source_quote | ai_interpretation | user_note
reviewerKind: human | ai
publicationScope: internal | learning
```

`humanReviewed=true` 같은 값은 모델이 스스로 설정하지 못하게 한다. 사람 리뷰는 실제 사람의 확인 기록과 대상 hash가 필요하다. AI의 재검토는 ai로 기록한다. reviewed만으로 임상 사용 가능성을 뜻하지 않는다. 이번 제품에는 clinical_eligible 승격 경로가 없다.

한 개의 `confidence=0.95`로 정확도·검토·임상 유효성을 대신하지 않는다. 구체적인 부족 정보를 보여 준다: “한자명 미확인”, “텍스트 검토 완료·좌표 검토 대기”, “모델 경로”, “3D 미지원”.

학습 화면의 기본 필터는 검토된 자료다. 사용자가 명시적으로 “검토 중 자료 보기”를 선택하면 후보 자료를 구분해 볼 수 있다. 미완료 근육의 존재와 누락 상태는 목록에서 항상 드러나게 한다. 검토되지 않은 위치를 기본 정답이나 퀴즈 채점 기준으로 사용하지 않는다.

내용을 고치면 해당 field claim의 hash와 의존 review를 stale로 만든다. 관련 퀴즈 정답·검사 연결·공간 annotation까지 영향 범위를 추적한다. 문구 수정이 항상 모든 근육 리뷰를 무효화하지 않도록 의존성을 세분화한다.

## 6. 기능 계약

JointAction은 최소한 다음을 갖는다.

```text
muscleOrPartIds, jointIds, actionTermId,
postureConditions, taskContext, contractionRole,
roleInTask, explanationClaimIds, evidenceIds
```

근육·기능 관계는 다대다다. 구조만 있는 근육의 functionIds는 비어 있을 수 있고 UI는 “기능 준비 중”을 표시한다. 임의 일반 문장으로 채우지 않는다. 기능 입력 시 구조 및 부착부의 관련 claim revision을 기록한다.

## 7. 평가 계약

Assessment는 다음 구조를 권장한다.

```text
purpose / construct / scope(individual|group|movement_task)
relatedMuscleIds / targetFunctionIds / otherRelevantStructures
patientPosition / examinerPosition / stabilization
movement / resistanceSite / resistanceDirection / equipment
procedureSteps / stopConditions
observations: 측정 항목, 단위, 기록 양식
interpretations: 해석 가능한 범위, 대체 원인, 확정 불가 사항
compensations / confounders / nextChecks
measurementProperties: protocolVariant, population, referenceStandard,
  reliability?, sensitivity?, specificity?, uncertainty?, evidenceIds
```

여기에 값이 없다고 임의의 정상 반복 수나 각도를 넣지 않는다. 검사명만 같아도 절차가 다르면 별도 protocolVariant를 만든다. 수기 근력 등급 척도는 검사 프로토콜과 분리한 공통 Scale 엔터티로 관리하고 출처를 붙인다. 통증·약화·긴장·단축·운동 조절 문제를 동의어처럼 저장하지 않는다.

## 8. 코드로 반드시 검증할 불변 조건

1. ID 유일, 모든 참조 존재, 부모 관계 순환 없음.
2. 양측 인스턴스·근두·모델 액추에이터가 근육 개념 수에 중복 계산되지 않음.
3. verified term에는 출처·판본·locator 존재. 한자 결측 허용하지만 세 언어 완성 집계 제외.
4. 공개 학습 claim에는 근거와 해당 revision 리뷰 존재. conflicting/held/stale는 정답으로 승격 불가.
5. spatial annotation의 side·instance·asset revision·좌표계·단위가 일치.
6. annotation이 사용한 메시가 바뀌면 stale 또는 재검토 없이 표시 승인 불가.
7. 매핑이 다대다여도 출처 메시를 이중 렌더해 중복 선택을 만들지 않음.
8. 공개 빌드 에셋에는 출처·라이선스·귀속·변경 표기 기록 존재. 불명확한 것은 공개 빌드 제외.
9. assessment가 없는 근육에는 “평가 준비 중”; 독립 검사가 불가능한 경우 group/task 범위를 유지.
10. 치료/진단 자동 규칙·환자 개인정보 저장 기능이 없고 fixtures는 실제 학습 데이터에 섞이지 않음.

스키마 검사만으로 출처의 내용이나 3D 위치가 정확함을 증명할 수 없다. 검증기는 잘못된 형식/연결/상태를 막고, 의미·해부 위치 검토는 별도로 남긴다.

## 9. 반드시 실패해야 하는 테스트

고아 ID, 같은 ID 중복, left 데이터를 right 메시로 연결, 단위 누락, 1000배 scale 오류를 탐지하는 알려진 표지 fixture, 리메시 후 오래된 annotation, 출처 없는 reviewed claim, AI를 human reviewer로 위장, 한자 결측을 번역으로 자동 보충, 비공개 원문 public 포함, 모델 액추에이터를 전체 근육 수로 집계하는 오류를 각각 차단한다. 실제 임상 수치를 지어낸 fixture는 쓰지 않는다.

검사 과정에서 테스트 결과가 false여야 하는 항목은 `expected=false`와 실제값 일치를 검사한다. 모든 bool을 무조건 all()로 통과 판정하지 않는다.

## T10 개정 — 사용자 표시명·웹 근거·검색 보조 사전

기본 표시는 승모근/전경골근처럼 **한자어를 한글로 적은 관용명**이다. 실제 한자 문자열(僧帽筋)과 우리말 명칭(등세모근), 영어(Trapezius)는 별도 필드다. 어느 이름으로 검색해도 stable concept ID로 합류한다. 부분(견봉부)·근군(판상근)·개별근(두판상근/경판상근)은 합치지 않는다. 라틴 철자 오타는 제한적 유사검색으로 후보라고 표시하며 임의 단일 자동확정하지 않는다.

공식 용어집 접근 실패만으로 이미 웹 출처에서 확인한 관용명까지 숨기지 않는다. `atlas-data/terminology/learning-names.json`은 출처 있는 **표시/검색 overlay**이며 canonical reviewed claim이 아니다. 원문·검색색인 근거 수준, URL/locator/조회일, 충돌, humanReviewed=false를 유지한다. T11에서 field별 evidence와 범위를 강화하고 장기 canonical 계약으로 migration한다. 역사적 한자 표기 오류는 그대로 채택하지 않는다. 순우리말 명칭에 임의 한자를 붙이지 않는다.

한국어 구조 요약 overlay는 기존 claim ID와 내용 hash를 참조하고 원문 변경 시 검증을 실패시킨다. AI 번역/요약과 현대 문헌 검토·사람 검토를 구분한다. 이 보조사전과 요약은 T03 schema를 통과한 canonical 정답으로 표시하지 않는다. production build는 별도 overlay validator를 실행한다.
