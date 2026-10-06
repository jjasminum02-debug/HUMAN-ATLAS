# 신경 검토 02 — 결과

- 실행: `atlas-quality-review-2026-10-06-r1`
- 고정 입력: `input-snapshot/nerve.json` SHA256 `da878d82a8f990f5066c482b40a5dd8a304bf38753fb49427c0536bbfebd90c3` (manifest와 일치)
- 검토 범위: source 표면 195행, native label group 98개, concept 설명 98개(각 4필드, 총 392행), 기존 운동근 관계 18행
- 기록 상태: source-only 유지, human review `not_performed`, 공개 재배포 `held`; 공통 데이터/runtime은 수정하지 않음

## 확인 결과

정확한 source key→모형 instance와 native label→concept 대응은 195/195, 98/98이다. 98 label group 중 97개는 양측 표면이 있고, `Common plantar digital branches of medial plantar nerve`는 왼쪽 표면만 있다. 반대쪽을 복제하거나 추론하지 않았다. 이 수치는 표면·label group 수이며 독립 신경 개념 수가 아니다.

기존 18개 관계는 target identity/kind, side, part 범위와 근육 역관계가 일치했다. 2개는 앞정강근에 대한 좌우별 exact source geometry 관계이고, 16개는 문헌 개념 관계다. 18개는 9개 신경 concept 및 44개 target source key에 걸쳐 있다. exact geometry 관계만 분지 표면의 정확한 side pair를 가리킨다. 문헌 관계는 분지 좌표나 전 범위 지배를 입증하지 않는다. 대흉근의 가쪽/안쪽가슴신경 중복 관계는 보존했으며 분지 경계 증거로 확대하지 않았다. 검사한 기존 관계에서 side 오류, 감각 전용 신경의 운동 연결, part를 whole로 과장한 관계, 역관계 불일치는 발견하지 못했다.

신경 설명의 필드별 검토는 392행이다. 기존 field hash가 있는 10행은 값과 hash가 일치했고 stale hash는 0이다. snapshot 설명의 검토 disposition은 `courseContext` 90행, `functionContext` 95행, `variationContext` 93행이 `확인`이며, 이는 해당 문장과 기존 범위 근거를 대조한 결과이지 field별 직접 원문 인용 278건을 뜻하지 않는다. field별 hash/locator가 없는 구체 설명은 직접 근거 coverage가 미확정으로 남는다. `compressionContext` 98행은 연결된 근거가 없어 미확정이고, 나머지 미확정 disposition은 course 8, function 3, variation 5행이다. 확인된 course 문장도 상당수는 정적 모형의 지역적 관찰이지 문헌상 주행 전부를 보여주는 문장이 아니다.

같은 조건문을 반복하는 일반 기능 설명은 관계 근거가 없다는 상태를 중복 표현한다. 이는 해부학 오류로 판정하지 않았다. 90개의 일반 압박 문구는 포착 근거가 연결되지 않았다는 뜻이지 포착이 없다는 뜻이 아니다. 92개의 변이 문구는 동적 신경 변형 미지원 상태이지 변이가 없다는 뜻이 아니다. 운동 관계 18행은 전체 지배망 완성을 의미하지 않는다.

## 통합 제안

`proposals.json`에 정정·한정안 3건, 연구 소견 설명 후보 1건, 미등록 관계 후보 2건을 구분해 기록했다.

- 온종아리신경의 “앞·뒤 가지” 설명을 현재 연결된 깊은·얕은종아리신경 분지명과 일치시키고, 표시 범위가 부분적임을 드러낸다.
- UI 제목 “분지”를 “모형에서 연결된 분지”로 한정한다. 연결되지 않은 분지를 전부 없다고 읽지 않게 한다.
- `relationship_not_linked`인 경우에만 반복되는 일반 기능 템플릿을 숨기고, 기능 상태와 실제 관계 목록은 계속 표시한다.
- 제한된 시체해부 연구에서 네 번째 가슴사이신경이 대흉근 아래가쪽 공급에 관여한 결과(30 표본 중 4)를 연구 한정 설명 후보로 제시한다. 통합 시 적용 여부를 결정하고 좌우·세부 표면·분지 좌표에는 연결하지 않는다.
- 공식 TAH의 얕은/깊은종아리신경 branch 명칭 4건은 WIP 공식 명명 자료의 후보일 뿐이다. 1차 해부 근거 대조 전까지 graph에 등록하지 않는다. TAH U12899/U12901의 중복 표기 “extensor digitorum pedis”는 장·단지신근으로 추정 매핑하지 않는다.

새로 확인한 원문·범위는 개별 locator와 한계를 JSON에 기록했다: [TAH U6731](https://ifaa.unifr.ch/Public/TNAEntryPage/auto/unit/LAEN/TAH6731%20Unit%20EN.htm), [TAH U6734](https://ifaa.unifr.ch/Public/TNAEntryPage/auto/unit/EN/TAH6734%20Unit%20EN.htm), [TAH U6739](https://ifaa.unifr.ch/Public/TNAEntryPage/auto/unit/LAFR/TAH6739%20Unit%20EN.htm), [Beheiry 2012 PubMed 초록](https://pubmed.ncbi.nlm.nih.gov/21587039/). TAH 페이지는 work in progress 공식 명명 자료이며 해부 표본 연구나 geometry 결속 근거로 쓰지 않았다. PubMed에서는 초록을 열어 확인했으며 전문을 확인한 것으로 기록하지 않았다.

## 미해결 및 UI 주의

미해결은 (1) 18개 관계로 전 신경 지배 범위를 증명할 수 없음, (2) 왼쪽만 있는 발바닥 공통 발가락 신경 표면의 오른쪽 자료 부재, (3) 네 개 종아리신경 분지 후보의 독립적인 1차 해부 교차 확인, (4) TAH의 U12899/U12901 표기 모호성, (5) 98개 compressionContext의 field별 근거 부재다. 이들은 서로 다른 종류의 미확정이며 오류나 해부학적 부재로 바꾸지 않았다.

앱의 exact label/concept resolve와 forward/reverse relation은 같은 graph 행을 사용한다. 선택 side 필터는 문헌의 unsided concept 관계를 보여주기 위한 UI 조건일 뿐, 그쪽 분지·좌표의 증거가 아니다. UI의 “분지” 문구는 등록된 subset만 보여 주므로 한정 제안이 필요하다. 전체 전수 PNG·브라우저 검증·빌드·공통 코드 반영은 수행하지 않았다.

## 산출물

- `relation-review.json`: 배정된 195 source row, 98 native group/concept, 18 relation 검토
- `description-review.json`: 98개 concept의 392 field row 검토
- `proposals.json`: 변경 전 값/hash, 대상 pointer/code 위치, evidence locator, 적용 범위·제한을 포함한 6개 통합 제안

03 이름 검토가 끝난 뒤 04 통합 단계에서 이 검토와 03의 결과를 함께 반영한다. 이 단계에서는 실제 source/관계 고정 입력만 읽었고, 고정되지 않은 learner UI는 01의 공통 변경이 있다는 이유만으로 stale 처리하지 않았다.
