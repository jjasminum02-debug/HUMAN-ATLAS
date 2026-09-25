# T01 출처 공백과 검토 대기

확인일: 2026-09-25. 이 목록은 `atlas-data/sources/registry.json`과 함께 읽는다. 웹 페이지를 열람한 사실은 원본 파일이나 근육별 내용을 확보했다는 뜻이 아니다.

## T04 전에 해소할 용어 공백

- **TA2 근육 목록:** FIPAT/IFAA의 TA2 온라인 2판(2019)과 CC BY-ND 4.0 안내 페이지, 공식 publication link를 확인했다. 실제 고정판 파일, 근육별 항목/행 locator, 로컬 파일은 확보하지 않았다. T04에서 사용할 정확한 데이터나 근육 항목 범위를 정하고 필요한 경우 이용 조건을 다시 확인한다.
- **한국어 해부학용어:** 대한해부학회 `Korean Anatomical Terminology` 6판(2014) 후보를 논문 참고문헌과 KCI 논문 서지에서 확인했다. 원 책/공식 최신 파일은 확보하지 못했고 현행판 여부와 재사용 조건도 확인하지 않았다. 의학용어집과 혼용하지 않는다.
- **한자/중국어 용어:** 근육별 한자 또는 중국어 대응표와 판본이 없다. 확인 전에는 값을 생성하거나 번역 결과를 표준명으로 승격하지 않는다.
- **완전한 분모:** 성인 골격근 전체 항목의 canonical list는 아직 없다. scope 정책은 T01에서 고정했지만 실제 목록과 항목 수, 판본 locator는 T04에서 만든다.

## 해부학 주장 공백

- OpenStax Anatomy and Physiology 2e의 선택된 Chapter 11 페이지와 책 라이선스를 확인했다. 교육용 범위는 넓으나 모든 근육의 기시·정지·부착 범위를 다루는 완전한 원자료로 검증하지 않았다.
- 접근 가능한 해부학 atlas/교과서의 판본, 장·쪽/표/그림 locator, 실제 소장/접근 여부를 아직 결정하지 않았다. 유료 자료는 구매하지 않는다.
- BodyParts3D의 근육 개념·표현 ID, 실제 메시, 골격 구조, pilot 6개 지원 여부, 누락/오류/표현 방식은 파일 내용으로 확인하지 않았다. Release 4.0 아카이브에 OBJ 목록과 ID 테이블이 게시되어 있다.
- 3D 근복은 기시·정지 면의 검증과 같지 않다. 별도 주장 근거, 공간 annotation, 사람 검토가 필요하다.

## 평가 근거 공백

- Merck Manual Professional의 근력 평가 안내 페이지와 2025년 8월 업데이트 문구는 확인했다. 이는 일반 근력평가 설명 후보이며 모든 근육의 표준화 검사, 신뢰도/타당도, 민감도·특이도, 임상 해석 범위를 제공하는 전체 목록이 아니다.
- 향후 사용할 검사 교재/원저/가이드라인의 정확한 판본과 검증 자료를 아직 선정하지 않았다. 임의의 정상값·진단 기준을 만들거나 검사 결과로 원인 근육을 확정하지 않는다.
- 검사 자료의 라이선스/재사용 조건은 확인하지 않았다. 후속 작업에서는 원문 복사 없이 locator와 claim 요약을 연결하거나 권리를 별도 검토한다.

## 3D 이용 조건과 귀속

- **검증됨(정확히 LSDB Archive Release 4.0 파일에 한정):** 다운로드 페이지에 IS-A/PART-OF OBJ 및 concept/representation table 파일명이 게시됨. archive license page는 2025-02-27 갱신, CC BY 4.0, 지정 credit을 안내한다. 해당 exact files는 다운로드하지 않았다.
- **경계:** BodyParts3D live information page에는 CC BY-SA 2.1 JP 표기가 남아 있다. 이 표기를 archive의 2025 license와 섞지 않는다. live API, 다른 mirror, 다른 릴리스의 자료는 별도 확인한다.
- **미확인:** archive listing이 현재 실제 파일 다운로드, checksum, file contents, 배포본과 README 간 일치, 종아리 대상 mesh coverage를 보증하는지 확인하지 않았다.
- T02가 파일을 얻으면 해당 릴리스의 README/license snapshot과 함께 정확한 파일명, URL, retrieved date, SHA-256, concept ID, representation/file ID, tree, 변환 내역, 화면 귀속 문자열을 기록한다. 본문 필드가 빠진 asset은 앱 배포 후보에 넣지 않는다.
- Archive가 제시한 exact credit: `BodyParts3D, © The Database Center for Life Science licensed under CC Attribution 4.0 International`. 이 문자열은 이번에 파일을 내려받거나 배포했다는 뜻이 아니다.

## 다음 단계별 처리

| gap | 후속 처리 | 현재 영향 |
|---|---|---|
| 정확한 TA2 항목/판본 locator | T04에서 catalog source/edition 결정 및 목록 추출 가능성 확인 | T02 자산 가용성 조사 차단 사유는 아님 |
| KAA 최신 용어판과 원본 | T04 또는 첫 용어 입력 전 확인 | 한국어 표준/한자명을 검증된 값으로 입력하지 못함 |
| 기시·정지 교재와 항목 locator | T05의 근육 claims 작성 전에 접근 가능한 판본 선택 | 지금 해부학 데이터 입력 없음 |
| assessment protocol 및 권리 | 평가 입력 task 전 선정 | 지금 검사 설명이나 임상 해석 입력 없음 |
| BodyParts3D pilot 파일과 mesh/hash | T02에서 승인된 소량 파일로 검사 | 3D 지원/형태/좌우를 아직 주장할 수 없음 |
| OpenSim 개별 모델의 file-level rights | 해당 모델을 실제로 인용/변환할 task에서 확인 | T01에서 OpenSim 원본을 열거나 수정하지 않음 |

T01은 이 공백을 드러내고 범위/정책/출처 레지스트리를 작성하는 task이므로, 이 공백 자체는 T01을 막지 않는다. 기술 상태와 사람 해부학 검토 상태는 별도로 유지한다.

## T04 업데이트 — 2026-09-25

- **TA2:** IFAA 공식 안내는 TA2 제2판(온라인 2019, IFAA 승인)과 CC BY-ND 4.0을 확인해 준다. FIPAT 공식 Part 2 PDF 검색 색인에서 `work/evidence/T04/source-locator-register.json`에 적은 일부 근육/근군 행 및 인쇄 쪽 locator 85개를 확인했다. 원본 PDF 바이너리는 현재 환경에서 DNS 실패로 내려받지 못했고 로컬 파일·checksum·전체 표 시각 검토는 없다. 따라서 이 locator 모음은 전신 명칭 목록이나 고정판 확보로 승격하지 않는다.
- 공식 TA2 Part 2 PDF에 머리/눈·저작·혀·등·흉곽·복벽·골반 머리말·어깨/상지·엉덩이/하지·발의 일부가 잡혔고, `face`, `pharynx`, `larynx`, `neck`, `hand`의 T04 캡처 행은 없다. 다른 영역도 일부 항목만 확인했다. 영역별 범위와 남은 작업은 `work/review-queue/catalog-gaps.md`에서 관리한다.
- TA2의 7열 term role을 설명하는 IFAA 안내는 읽었지만 원본 Part 2 행을 화면으로 보지 못했다. 개별 Latin/English 값의 official/equivalent/synonym 열 역할은 확인 전까지 미승인이다. 공식 Errata PDF 링크는 식별했으나 사용 행 전부를 대조하지 않았다.
- 대한해부학회 용어집 제6판(2014) 원본, 현행판 확인, 근육별 용어/한자 locator와 재사용 조건은 여전히 미확보다. Hangul/Hanja 값은 null로 둔다.
- T04 단계에서 우측 BodyParts3D 파일과 TA2 행의 이름/계층 crosswalk를 provisional 상태로 기록했다. 해부학적 동일성에 대한 사람 검토는 하지 않았다.

## T05 업데이트 — 2026-09-25

- **Gray 1918 역사 해부학 출처:** 정확한 서지는 Henry Gray, Warren H. Lewis 편, *Anatomy of the Human Body*, 20th US ed., Lea & Febiger, 1918이다. Section 8c의 해당 근육 subsection과 tibialis anterior p. 480 온라인 텍스트를 확인했다. Gray는 현행 해부학 표준이 아니며 source file/hash와 현대 독립 출처 대조가 없다. T05 구조 요약은 모두 `needs_review`; registry 사용 범위는 internal/research로 제한했다.
- **OpenStax 2e:** 공식 11.6 페이지에서 책 본문을 LLM/생성형 AI 서비스에 사전 허가 없이 ingestion하는 제한을 확인했다. T05에서 본문을 이용한 claim 추출은 하지 않았다. 권리 조건과 허가를 별도 확인하기 전에는 source 후보로만 둔다.
- **T05 pilot 용어:** 여섯 muscle concept와 gastrocnemius 두 head part의 TA2 row/page records는 T04에서 연결됐다. TA2 Part 2 바이너리/시각 검토/Errata 대조, 표 용어열 역할 확정, Korean Anatomical Terminology 정확한 판본·항목 locator·Hanja 대응이 여전히 필요하다. 현재 term rows는 `needs_review`; Korean/Hanja는 null/held다.
- **T05 해부 구조 텍스트:** Gray section 8c claims/evidence locator를 등록했으나 현대 독립 출처 대조와 사람 검토는 없다. 변이 설명은 별도 개념으로 정규화하지 않았다. `work/review-queue/pilot-structure-gaps.md`를 참조한다. 좌표와 mesh annotation은 입력하지 않았다.
