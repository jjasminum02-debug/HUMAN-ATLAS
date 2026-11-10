# 근육 기시·정지 추가 검토 — 2026-10-02

## 입력과 방법

사용자가 제공한 13개 PDF의 실제 파일 SHA-256과 페이지 수는 `source-catalog.json`에 기록했다. 파일은 원래 위치에 두었고 프로젝트에 복사하지 않았다. PDF 텍스트층을 페이지별로 읽고, 기시·정지 표기 페이지를 우선 확인했다. 머리/목, 씹기근, 척추세움근, 등세모근, 손 intrinsic, 볼기·넓적다리, 종아리·발의 관련 페이지는 페이지 이미지도 표본 검토했다. 텍스트층이 비었거나 잘림/오탈자로 구조 범위가 확실하지 않은 경우 그 PDF만으로는 채택하지 않았다. `5강뇌간,소뇌26.pdf`는 기시·정지 근거를 포함하지 않아 첨부 부착 요약에는 쓰지 않았다.

현대 보완 자료는 UAMS Department of Neuroscience의 공개 해부학 표를 웹 리더에서 본문 표까지 열어 대조했다. 표의 `Muscle / Origin / Insertion` 행에 있는 항목을 필드별 locator로 남겼다. 표의 판본 정보는 노출되어 있지 않아 `edition=not_exposed`로 기록했고, 웹 원문 HTML byte를 내려받지 않았으므로 원문 hash는 null이다. 요약은 한국어 바꿔쓰기이며 문장 단위 직접 인용이 아니다. UAMS는 일부 표가 MedCharts Anatomy를 바탕으로 한 과정 자료라고 알리고 무단 사용을 금지하므로 공개 재배포 권리는 계속 `held`다.

## 범위 판단

이번 검토는 T65에 고정된 232개 지원 source muscle concept 중 기시·정지 요약이 없던 201개를 기준으로 했다. 31개 기존 설명/충돌 기록을 다시 쓰지 않았다. 201개에서 직접 이름·부분 또는 근육군 범위가 표/강의자료에 명시된 항목만 learner 요약 후보에 넣는다. 전체 근육 행을 개별 head/part에 그대로 복제하지 않는다. UAMS가 갈래별 시작점을 분리한 경우에는 갈래별 설명을 쓰고, 공통 정지가 표에서 확인되는 경우만 공유 정지로 표현한다. 갈래별 값이 표에 없으면 부모 근육의 범위를 그 갈래만의 근거처럼 바꾸지 않는다.

근육군은 표가 군 전체를 다룬 경우에만 `named_source_group`으로 기록한다. 좌우는 기존 source overlay의 side를 그대로 대조하고, 한쪽만 있는 이름을 반사/복제하지 않는다. `Diaphragm`과 `Transverse arytenoid`는 자료가 중앙 구조로 다루므로 `midline`으로 기록했다. `Iliocostalis colli`의 오른쪽 instance와 side가 비어 있는 instance는 서로 다른 상태로 유지했다. 이번 설명은 기존 형상 좌표·부착점·geometry binding을 추가하지 않는다.

## 사용한 원문 locator 예시

- 머리/목: UAMS head-and-neck table, `depressor anguli oris` 및 `depressor labii inferioris` 행(31–32), digastric anterior/posterior belly 행(34), lateral pterygoid head별 행(49–50, 95–96), orbit rectus 행(103–108), arytenoid and thyroarytenoid 행(11–13, 131–138), zygomaticus major/minor(140–141). 사용자 제공 `26-2머리근육.pdf` p9–13, `26-3저작,목근육1.pdf` p2–4 및 p13–14는 머리·씹기·목갈래의 한국어 표기와 갈래 범위를 교차 확인하는 데 사용했다.
- 상지: UAMS upper-limb table, `anconeus`(14), arm/forearm muscle rows(15–19, 23–38), hand interossei/lumbricals(21, 40–43, 46, 50), pronator teres heads(57), supinator and shoulder/back muscle rows(65–71). 사용자 제공 `26-9아래팔근육.pdf` p4–28, `26-10손,볼기근육.pdf` p5–9는 손·아래팔 갈래/군 표본을 확인했다.
- 등·가슴우리: UAMS back table, `erector spinae` through `splenius` rows(23–43). 사용자 제공 `26-4목2,척주근.pdf` p13–20은 splenius와 척주세움근/다열근의 지역 범위를 확인했고, `26-5뒤통수,흉곽,뒤배벽.pdf` p9, p14, p20은 갈비사이근·가로막·허리네모근의 요약 범위를 확인했다. UAMS thorax table(18–23)은 external/internal/innermost intercostals, levatores costarum, subcostalis, transversus thoracis를 각각 대조했다.
- 배·골반: UAMS abdominal table(15, 17–33)과 pelvis/perineum table(14, 17–31). 사용자 제공 `26-6배벽,골반.pdf` p2–5, p7, p11–16에서 복벽·골반바닥의 표현 및 성별 구분을 확인했다.
- 하지·발: UAMS lower-limb table의 해당 named row(10–78). 사용자 제공 `26-11볼기,넓적근육.pdf` p3–16, `26-12넙다리2,하퇴근육.pdf` p3–7, p11–12, p20–25, `26-13하퇴2,발근육.pdf` p15–17, p20–31에서 근육/갈래별 한국어 범위를 확인했다.

행 번호는 열람 시의 UAMS page locator이며 웹 검색 색인이나 검색 snippet이 아니다. 학습 요약은 해당 표 행이 실제로 열린 상태에서 만들었다.

## 한계와 보존

UAMS 표는 일반적인 표준 부착을 제공하지만 모든 희귀 변이, 세부 힘줄 부착, 해부 표본 차이 또는 표면 좌표를 설명하지 않는다. PDF 자료도 수업용 개요이며, 판본/저작권/재배포 허가가 파일마다 독립 확인되지 않았다. 따라서 source catalog는 private provenance이고, learner runtime에는 요약문만 투영한다. 부족한 근거는 unresolved ledger에 남기며 빠진 설명을 형상 부재로 바꾸지 않는다.

201개를 검토하는 동안 T65/T90 과거 disposition, 원문 bytes, learner names, 542 target/563 membership/12 region, HA130, 역사 분류 163(6/20/135/2), source-only, rights held, humanReview not_performed를 바꾸지 않는다. 새 HA ID, geometry, 좌표, reviewed 상태는 만들지 않는다.

## 2026-10-02 추가 반영 판단

기존 `claims.json`의 146행을 201개 미설명 source-concept와 정확히 대조했다. 142개의 고유 대상은 이름·부분·군 범위가 현재 source row와 직접 맞아 재사용했다. 중복된 손/발 새끼벌림근과 새끼굽힘근 행은 제공 PDF의 더 구체적인 값을 선택했다. 기존 갈비올림근 일반표 행은 사용자 PDF가 짧은/긴 갈래 부착을 각각 분리하므로 그 직접 갈래 행으로 대체했다.

추가 44행을 구성했고 그중 갈비올림근 2행은 기존 claim 대체이므로 순증은 42개 target이다. 사용자 PDF 22쪽의 자쪽손목폄근 두 갈래는 위팔갈래와 자뼈갈래의 서로 다른 기시 및 공통 정지가 명시되어 둘 다 기존 정확한 갈래 source에 연결했다. 빗장·복장갈비 큰가슴근 갈래는 각 기시와 공통 정지만 연결하고 배갈래를 부모 설명에서 채우지 않았다. `Iliocostalis colli`는 source overlay에 오른쪽으로 표시된 key 한 개에만 투영했으며, side가 비어 있는 동명 key는 그대로 두었다. `Coccygeus muscle.t`는 T65 역사 원장의 이름 오류를 보고서에 남기고 실제 runtime object 명칭으로만 투영했다.

최종 201개 미설명 기준으로 근거가 있는 184개 target에 learner 요약을 연결하고 17개는 정확한 갈래 부착 또는 source identity 부족으로 미확인 유지했다. 그 17개는 복장갈비근 배갈래, 발 새끼맞섬근, 빗장후두개갈래/갑상피열근 바깥갈래, 허리가로돌기사이근 등쪽·배쪽갈래, 부위별 가시사이근 3개, 관자마루근, 부위별 뭇갈래근 3개, 두 갈래 반지방패근, 두덩항문근이다. 표준군 설명이 있더라도 이름이 지정한 갈래/부위의 기시·정지를 직접 특정하지 않으면 적용하지 않았다.

위 수치는 source-summary를 제공할 수 있는 target 범위다. 모든 표본 변이·부착 좌표·부착 면적의 완전성은 주장하지 않는다. 이 데이터는 source-only이고 사람 검토는 수행하지 않았으며 공개 재배포 권리는 held다. 학습 런타임에는 한국어 바꿔쓰기만 투영하고 URL, locator, source/review 상태와 원문은 노출하지 않는다.


## 2026-10-02 추가 원문 대조 — 잔여 갈래/변이 17개

고정 catalog만 재검색하는 대신 이름과 갈래 범위가 직접 확인 가능한 원문을 열어, T65의 잔여 17개 target에 다시 대조했다. 16개는 이름·지역·갈래별 기시/정지를 직접 적은 페이지 또는 표에서 요약했다. 1개(발 새끼맞섬근)는 IMAIOS e-Anatomy 본문이 “짧은새끼굽힘근 깊은 섬유에서 가끔 분리”라고 하면서 같은 페이지의 다른 항목에서는 제5중족골 바닥/긴발바닥인대를 기시로 적어 원문 자체가 일치하지 않는다. 이 값은 한 쪽을 골라 확정하지 않고 learner text에도 불일치를 그대로 표시했으며 record evidenceState를 conflicted_source_summary로 남겼다. 해당 근육은 별도 구조가 항상 존재하는 정상 표준근이라고 표현하지 않았다.

추가로 연 원문은 Complete Anatomy/Elsevier의 큰가슴근 복부갈래, 빗모뿔근의 후두덮개모뿔 부분, 가쪽 허리가로돌기사이근, 외측 갑상피열근 부분, 관자마루근; IMAIOS e-Anatomy의 위입술올림근(콧방울올림근) 및 외측 갑상피열근; Kenhub의 목·등·허리 가시사이근, 부위별 뭇갈래근, 반지방패근 갈래, 허리가쪽가로돌기사이근 앞/뒤갈래; 그리고 Kearney et al. (2004) levator ani origin-insertion review이다. source catalog는 URL, 판본 노출 여부, 조회일, 열린 원문 접근방식과 권리 held를 필드별로 기록한다. 이 웹 자료의 원문 HTML bytes/hash는 내려받지 않아 null 상태로 둔다.

적용 규칙: (1) 큰가슴근 복부갈래는 가쪽배빗근 널힘줄 기시와 큰가슴근 공통 힘줄 정지를 표시하되 갈래 자체의 정지 범위를 세부 확대하지 않는다. (2) 후두덮개모뿔갈래와 외측 갑상피열근은 각 정확한 갈래 page locator만 적용한다. (3) 가시사이근은 경추/흉추/요추별 분절쌍을 분리하고 흉추의 저발달·결여/변이를 그대로 적는다. (4) 뭇갈래근은 경추/흉추/요추별 값으로 분리하며 척추 전체 요약을 개별 부위에 복사하지 않는다. (5) 허리가쪽가로돌기사이근 등쪽/배쪽 target은 실제 source가 각각 accessory process-to-transverse process와 인접 횡돌기사이를 구분한 값만 쓴다. (6) 두덩항문근은 review article이 여성 해부표본에 관해 TA 용어와 연구별 불일치를 설명하므로 해당 exact source-name 범위만 기록하고 두덩꼬리근/두덩곧창자근 전체로 확장하지 않는다.

새 원문은 비공개 provenance catalog에만 넣었다. 요약은 한국어 바꿔쓰기이고 직접 인용/사람 승인 주장이 아니다. 새 부착좌표·뼈 binding·canonical ID를 만들지 않았다. 모든 새 요약은 sourceOnly=true, humanReview=not_performed, publicRedistribution=held이며 HTML/raw source는 저장하지 않았다.
