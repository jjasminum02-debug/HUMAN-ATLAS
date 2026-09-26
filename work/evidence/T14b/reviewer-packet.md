# T14b 사람 해부학 검토 패킷 — 판독 전 대기
작성일: 2026-09-26. 상태: packet_ready / human_review_pending. 이 문서에 실제 검토 의견은 아직 없다.
검토 packet 식별자: T14b-HUMAN-REVIEW-PACKET-2026-09-26-v1. 파일과 입력 자료의 SHA-256은 review-packet-manifest.json에 기록한다.

## 사용 경계
이 패킷은 6개 우측 하퇴 파일럿의 용어·한국어 기시/정지 요약·좌우/모델 연결을 실제 사람 검토자가 확인하기 위한 자료다. 아래 source comparison은 T14a에서 확인한 자료와 AI 정리이며, 사람 검토나 승인 기록이 아니다. 검토자 입력 전 모든 판정은 pending으로 둔다. 표면좌표 검토가 아니므로 geometry-null 초안에 좌표를 추가하지 않는다.

### 검토자 기록 필드
- 이름/식별 가능한 전문 자격과 해부학 검토 경험: ____________________
- 소속(선택) / 이해상충 또는 자료 접근 제한: ____________________
- 검토일(YYYY-MM-DD): ____________________
- 검토한 packet/데이터 revision hash: ____________________
- 이름·기시·정지·좌우/모형 identity별 결론: accept / revise / hold 중 기록하고 근거·locator를 첨부
- reviewer의 실제 표현을 요약·대신 작성하지 말고, 서명 또는 식별 가능한 provenance를 보존

## 공통 원자료
Anatomy of the Human Body; Henry Gray, Warren H. Lewis (editor); 20th US edition, thoroughly revised and re-edited by Warren H. Lewis; Lea & Febiger, 1918.
Gray URL: https://www.bartleby.com/lit-hub/anatomy-of-the-human-body/8c-the-muscles-and-fasci-of-the-leg/
- Gray는 역사적 요약의 출처다. 판본 locator가 불확실한 항목은 이 packet에서도 미확인으로 둔다.
- 현대 출처는 아래 각 항목에 접근 수준(full text / abstract)을 명시한다. 검색 색인은 발견 용도이며 사람 검토가 아니다.

## 비복근 — HA-M-000001
한글 관용 표시명: 비복근 / 우리말: 장딴지근 / 한자: 미확인 / 영어: Gastrocnemius / 별칭: 등록 별칭 없음
대상: 우측 하퇴 learner model, concept ID HA-M-000001; T14a selected row/detail and 3D route passed. 문헌 표본의 laterality·인구 범위가 우측 GLB와 동일한 것은 아니다.
TA2 label locator: Terminologia Anatomica, 2nd edition (TA2), Part 2; online edition published 2019; row 2657; printed page 96; https://fipat.library.dal.ca/wp-content/uploads/2020/09/FIPAT-TA2-Part-2.pdf
Gray locator: Section 8c, Superficial Group, “The Gastrocnemius”; page not independently verified.
- 현재 화면에 놓인 한국어 구조 요약 (출처: Gray 1918 요약 번역, AI attribution; humanReviewed=false):
  - 전체 origin: 외측두는 대퇴골 외측과의 가쪽 오목한 부위와 그 바로 위 뒤면에서, 내측두는 내측과 뒤위쪽과 인접 대퇴골에서 시작합니다. 원자료는 두 근두의 무릎 관절낭 부착도 기술합니다. [claim IDs: HA-C-T05-GASTRO-LAT-FEMUR-ORIGIN, HA-C-T05-GASTRO-LAT-FEMUR-POSTERIOR-ORIGIN, HA-C-T05-GASTRO-LAT-KNEE-CAPSULE-ORIGIN, HA-C-T05-GASTRO-MED-FEMUR-ORIGIN, HA-C-T05-GASTRO-MED-FEMUR-ADJACENT-ORIGIN, HA-C-T05-GASTRO-MED-KNEE-CAPSULE-ORIGIN]
  - 외측두 origin: 대퇴골 외측과 가쪽의 오목한 부위, 그 위 대퇴골 뒤면 및 아래쪽 무릎 관절낭에서 시작합니다. [claim IDs: HA-C-T05-GASTRO-LAT-FEMUR-ORIGIN, HA-C-T05-GASTRO-LAT-FEMUR-POSTERIOR-ORIGIN, HA-C-T05-GASTRO-LAT-KNEE-CAPSULE-ORIGIN]
  - 내측두 origin: 대퇴골 내측과 뒤위쪽의 오목한 부위와 인접 대퇴골, 아래쪽 무릎 관절낭에서 시작합니다. [claim IDs: HA-C-T05-GASTRO-MED-FEMUR-ORIGIN, HA-C-T05-GASTRO-MED-FEMUR-ADJACENT-ORIGIN, HA-C-T05-GASTRO-MED-KNEE-CAPSULE-ORIGIN]
  - 전체 insertion: 두 근두의 건막이 모여 가자미근의 건과 함께 종골건을 이루고, 종골 뒤면 중간 부위에 부착합니다. [claim IDs: HA-C-T05-GASTRO-CALCANEUS-INSERTION]
T05 origin claim IDs: HA-C-T05-GASTRO-LAT-FEMUR-ORIGIN, HA-C-T05-GASTRO-LAT-FEMUR-POSTERIOR-ORIGIN, HA-C-T05-GASTRO-LAT-KNEE-CAPSULE-ORIGIN, HA-C-T05-GASTRO-MED-FEMUR-ORIGIN, HA-C-T05-GASTRO-MED-FEMUR-ADJACENT-ORIGIN, HA-C-T05-GASTRO-MED-KNEE-CAPSULE-ORIGIN
T05 insertion claim IDs: HA-C-T05-GASTRO-CALCANEUS-INSERTION
- 현대 근거 대조 (T14a source analyst notes; 사람 검토 아님):
  - Thomas K, Peeler J. A Detailed Anatomical Description of the Gastrocnemius Muscle—Is It Anatomically Positioned to Function as an Antagonist to the Anterior Cruciate Ligament? Anatomia. 2024;3(4):244–255. DOI: 10.3390/anatomia3040021.
    - URL: https://www.mdpi.com/2813-0545/3/4/21
    - 판본/locator/access: Journal article, volume 3 issue 4 (2024); publisher page published 2024-10-16. / Methods §2.2; Discussion §4.4. Publisher full text opened. / Publisher full HTML, methods and discussion inspected.
    - 직접 다룬 필드: origin_lateral_head
    - 기시 대조: Supports a broad proximal attachment at the posterior-superior lateral femoral condyle; no reproducible boundary on the project femur mesh.
    - 정지 대조: The selected study focuses on the proximal gastrocnemius; it does not provide a distal calcaneal footprint comparable to the Gray insertion summary.
- 사람 검토: not_performed; humanReviewed=false; surface review pending.
- 검토 입력란: 용어 [pending] / 기시 [pending] / 정지 [pending] / 우측 적용·모형 identity [pending] / 수정 제안·locator·근거 [빈칸]

## 가자미근 — HA-M-000002
한글 관용 표시명: 가자미근 / 우리말: 가자미근 / 한자: 미확인 / 영어: Soleus / 별칭: 등록 별칭 없음
대상: 우측 하퇴 learner model, concept ID HA-M-000002; T14a selected row/detail and 3D route passed. 문헌 표본의 laterality·인구 범위가 우측 GLB와 동일한 것은 아니다.
TA2 label locator: Terminologia Anatomica, 2nd edition (TA2), Part 2; online edition published 2019; row 2660; printed page 96; https://fipat.library.dal.ca/wp-content/uploads/2020/09/FIPAT-TA2-Part-2.pdf
Gray locator: Section 8c, Superficial Group, “The Soleus”; page not independently verified.
- 현재 화면에 놓인 한국어 구조 요약 (출처: Gray 1918 요약 번역, AI attribution; humanReviewed=false):
  - 전체 origin: 비골두 뒤면과 비골 몸통 뒤면 위쪽 1/3, 경골의 슬와선과 안쪽모서리 중간 1/3, 경골·비골 기시부 사이의 건성 활에서 시작합니다. [claim IDs: HA-C-T05-SOLEUS-FIBULA-HEAD-ORIGIN, HA-C-T05-SOLEUS-FIBULA-POSTERIOR-UPPER-THIRD-ORIGIN, HA-C-T05-SOLEUS-TIBIA-POPLITEAL-LINE-ORIGIN, HA-C-T05-SOLEUS-TIBIA-MEDIAL-BORDER-ORIGIN, HA-C-T05-SOLEUS-ARCH-ORIGIN]
  - 전체 insertion: 건막이 비복근의 건과 합쳐져 종골건을 이루며, 종골 뒤면 중간 부위에 부착합니다. [claim IDs: HA-C-T05-SOLEUS-CALCANEUS-INSERTION]
T05 origin claim IDs: HA-C-T05-SOLEUS-FIBULA-HEAD-ORIGIN, HA-C-T05-SOLEUS-FIBULA-POSTERIOR-UPPER-THIRD-ORIGIN, HA-C-T05-SOLEUS-TIBIA-POPLITEAL-LINE-ORIGIN, HA-C-T05-SOLEUS-TIBIA-MEDIAL-BORDER-ORIGIN, HA-C-T05-SOLEUS-ARCH-ORIGIN
T05 insertion claim IDs: HA-C-T05-SOLEUS-CALCANEUS-INSERTION
- 현대 근거 대조 (T14a source analyst notes; 사람 검토 아님):
  - Bolsterlee B, Finni T, D’Souza A, Eguchi J, Clarke EC, Herbert RD. Three-dimensional architecture of the whole human soleus muscle in vivo. PeerJ. 2018;6:e4610. DOI: 10.7717/peerj.4610.
    - URL: https://peerj.com/articles/4610/
    - 판본/locator/access: PeerJ volume 6, article e4610 (2018); publisher page published 2018-04-18. / Abstract, Methods and Results. Full article HTML opened. / PeerJ publisher full HTML inspected.
    - 직접 다룬 필드: 기시/정지 footprint를 직접 측정하지 않음
    - 기시 대조: The study measures soleus architecture, not a tibial/fibular origin footprint; any anatomical descriptions in its background are context, not a new attachment measurement.
    - 정지 대조: It does not quantify the Gray-described shared Achilles/calcaneal insertion footprint.
- 사람 검토: not_performed; humanReviewed=false; surface review pending.
- 검토 입력란: 용어 [pending] / 기시 [pending] / 정지 [pending] / 우측 적용·모형 identity [pending] / 수정 제안·locator·근거 [빈칸]

## 전경골근 — HA-M-000003
한글 관용 표시명: 전경골근 / 우리말: 앞정강근 / 한자: 前脛骨筋 / 영어: Tibialis anterior / 별칭: 등록 별칭 없음
대상: 우측 하퇴 learner model, concept ID HA-M-000003; T14a selected row/detail and 3D route passed. 문헌 표본의 laterality·인구 범위가 우측 GLB와 동일한 것은 아니다.
TA2 label locator: Terminologia Anatomica, 2nd edition (TA2), Part 2; online edition published 2019; row 2644; printed page 95; https://fipat.library.dal.ca/wp-content/uploads/2020/09/FIPAT-TA2-Part-2.pdf
Gray locator: Section 8c, “The Tibialis anterior (Tibialis anticus)”, printed p. 480.
- 현재 화면에 놓인 한국어 구조 요약 (출처: Gray 1918 요약 번역, AI attribution; humanReviewed=false):
  - 전체 origin: 경골 외측과와 몸통 가쪽면 위쪽 1/2~2/3, 인접 골간막, 하퇴근막 깊은 면 및 장지신근과의 근간중격에서 시작합니다. [claim IDs: HA-C-T05-TA-TIBIA-CONDYLE-ORIGIN, HA-C-T05-TA-TIBIA-SURFACE-ORIGIN, HA-C-T05-TA-IOM-ORIGIN, HA-C-T05-TA-FASCIA-ORIGIN, HA-C-T05-TA-SEPTUM-ORIGIN]
  - 전체 insertion: 제1설상골의 안쪽면·아랫면과 제1중족골 바닥에 부착합니다. [claim IDs: HA-C-T05-TA-CUNEIFORM-INSERTION, HA-C-T05-TA-MT1-INSERTION]
T05 origin claim IDs: HA-C-T05-TA-TIBIA-CONDYLE-ORIGIN, HA-C-T05-TA-TIBIA-SURFACE-ORIGIN, HA-C-T05-TA-IOM-ORIGIN, HA-C-T05-TA-FASCIA-ORIGIN, HA-C-T05-TA-SEPTUM-ORIGIN
T05 insertion claim IDs: HA-C-T05-TA-CUNEIFORM-INSERTION, HA-C-T05-TA-MT1-INSERTION
- 현대 근거 대조 (T14a source analyst notes; 사람 검토 아님):
  - Kimata K, Otsuka S, Yokota H, Shan X, Hatayama N, Naito M. Relationship between attachment site of tibialis anterior muscle and shape of tibia: anatomical study of cadavers. Journal of Foot and Ankle Research. 2022;15:54. DOI: 10.1186/s13047-022-00559-y.
    - URL: https://link.springer.com/article/10.1186/s13047-022-00559-y
    - 판본/locator/access: Journal article, volume 15, article 54 (2022); version of record published 2022-07-12. / Methods and Results, tibial attachment site; publisher HTML full text opened. / Springer Nature publisher full HTML inspected.
    - 직접 다룬 필드: origin_tibia
    - 기시 대조: Direct cadaveric measurements support a broad tibial origin and sex-related distal endpoint variation; the measured longitudinal endpoint is not a 2D footprint boundary.
    - 정지 대조: The medial cuneiform/first metatarsal insertion is described as background and cites prior work; this study does not experimentally measure that insertion.
- 사람 검토: not_performed; humanReviewed=false; surface review pending.
- 검토 입력란: 용어 [pending] / 기시 [pending] / 정지 [pending] / 우측 적용·모형 identity [pending] / 수정 제안·locator·근거 [빈칸]

## 후경골근 — HA-M-000004
한글 관용 표시명: 후경골근 / 우리말: 뒤정강근 / 한자: 後脛骨筋 / 영어: Tibialis posterior / 별칭: 등록 별칭 없음
대상: 우측 하퇴 learner model, concept ID HA-M-000004; T14a selected row/detail and 3D route passed. 문헌 표본의 laterality·인구 범위가 우측 GLB와 동일한 것은 아니다.
TA2 label locator: Terminologia Anatomica, 2nd edition (TA2), Part 2; online edition published 2019; row 2666; printed page 96; https://fipat.library.dal.ca/wp-content/uploads/2020/09/FIPAT-TA2-Part-2.pdf
Gray locator: Section 8c, Deep Group, “The Tibialis posterior (Tibialis posticus)”; page not independently verified.
- 현재 화면에 놓인 한국어 구조 요약 (출처: Gray 1918 요약 번역, AI attribution; humanReviewed=false):
  - 전체 origin: 가장 아래쪽을 제외한 하퇴골간막 뒤면, 경골 뒤면 가쪽부, 비골 안쪽면 위쪽 2/3에서 시작합니다. 일부 섬유는 깊은 횡근막과 인접 근간중격에서도 시작합니다. [claim IDs: HA-C-T05-TP-IOM-ORIGIN, HA-C-T05-TP-TIBIA-ORIGIN, HA-C-T05-TP-FIBULA-ORIGIN, HA-C-T05-TP-TRANSVERSE-FASCIA-ORIGIN, HA-C-T05-TP-SEPTA-ORIGIN]
  - 전체 insertion: 주상골 결절에 부착합니다. 원자료는 종골 재거돌기, 세 설상골, 입방골, 제2~4중족골 바닥으로 이어지는 섬유성 확장도 기술합니다. [claim IDs: HA-C-T05-TP-NAVICULAR-INSERTION]
T05 origin claim IDs: HA-C-T05-TP-IOM-ORIGIN, HA-C-T05-TP-TIBIA-ORIGIN, HA-C-T05-TP-FIBULA-ORIGIN, HA-C-T05-TP-TRANSVERSE-FASCIA-ORIGIN, HA-C-T05-TP-SEPTA-ORIGIN
T05 insertion claim IDs: HA-C-T05-TP-NAVICULAR-INSERTION
- 현대 근거 대조 (T14a source analyst notes; 사람 검토 아님):
  - Willegger M, Seyidova N, Schuh R, Windhager R, Hirtler L. The tibialis posterior tendon footprint: an anatomical dissection study. Journal of Foot and Ankle Research. 2020;13:25. DOI: 10.1186/s13047-020-00392-1.
    - URL: https://link.springer.com/article/10.1186/s13047-020-00392-1
    - 판본/locator/access: Journal article, volume 13, article 25 (2020); version of record published 2020-05-19. / Methods and Results, distal tendon footprints; publisher HTML full text opened. / Springer Nature publisher full HTML inspected.
    - 직접 다룬 필드: insertion_navicular_and_expansions
    - 기시 대조: The study addresses distal tendon footprints, not tibialis posterior origin.
    - 정지 대조: Main navicular insertion was present in 41/41 specimens, with additional distal tendon footprints; supports distal complexity but not a project-mesh triangle boundary.
- 사람 검토: not_performed; humanReviewed=false; surface review pending.
- 검토 입력란: 용어 [pending] / 기시 [pending] / 정지 [pending] / 우측 적용·모형 identity [pending] / 수정 제안·locator·근거 [빈칸]

## 장비골근 — HA-M-000005
한글 관용 표시명: 장비골근 / 우리말: 긴종아리근 / 한자: 미확인 / 영어: Fibularis longus / 별칭: Peroneus longus
대상: 우측 하퇴 learner model, concept ID HA-M-000005; T14a selected row/detail and 3D route passed. 문헌 표본의 laterality·인구 범위가 우측 GLB와 동일한 것은 아니다.
TA2 label locator: Terminologia Anatomica, 2nd edition (TA2), Part 2; online edition published 2019; row 2652; printed page 95; https://fipat.library.dal.ca/wp-content/uploads/2020/09/FIPAT-TA2-Part-2.pdf
Gray locator: Section 8c, Lateral Crural Muscles, “The Peronæus longus”; page not independently verified.
- 현재 화면에 놓인 한국어 구조 요약 (출처: Gray 1918 요약 번역, AI attribution; humanReviewed=false):
  - 전체 origin: 비골두, 비골 몸통 가쪽면 위쪽 2/3, 하퇴근막의 깊은 면 및 인접 앞·뒤 근육과의 근간중격에서 시작합니다. [claim IDs: HA-C-T05-FL-FIBULA-HEAD-ORIGIN, HA-C-T05-FL-FIBULA-LATERAL-UPPER-TWO-THIRDS-ORIGIN, HA-C-T05-FL-FASCIA-ORIGIN, HA-C-T05-FL-SEPTA-ORIGIN]
  - 전체 insertion: 제1중족골 바닥과 제1설상골의 가쪽에 부착합니다. [claim IDs: HA-C-T05-FL-MT1-INSERTION, HA-C-T05-FL-CUNEIFORM-INSERTION]
T05 origin claim IDs: HA-C-T05-FL-FIBULA-HEAD-ORIGIN, HA-C-T05-FL-FIBULA-LATERAL-UPPER-TWO-THIRDS-ORIGIN, HA-C-T05-FL-FASCIA-ORIGIN, HA-C-T05-FL-SEPTA-ORIGIN
T05 insertion claim IDs: HA-C-T05-FL-MT1-INSERTION, HA-C-T05-FL-CUNEIFORM-INSERTION
- 현대 근거 대조 (T14a source analyst notes; 사람 검토 아님):
  - da Rocha Gomes M, Pinto AP, Fabián AA, Mota Gomes TJ, Navarro A, Martin Oliva X. Insertional anatomy of peroneal brevis and longus tendon — a cadaveric study. Foot and Ankle Surgery. 2019;25(5):636–639. DOI: 10.1016/j.fas.2018.07.005.
    - URL: https://pubmed.ncbi.nlm.nih.gov/30321932/
    - 판본/locator/access: Journal article, volume 25 issue 5 (2019); epub 2018-07-23. Publisher full text was not opened. / PubMed indexed abstract, Methods/Results; abstract opened in browser. / PubMed abstract HTML opened; publisher page was not available in this check.
    - 직접 다룬 필드: insertion_first_metatarsal
    - 기시 대조: Study examines distal tendon insertions, not the longus origin.
    - 정지 대조: Abstract reports usual first-metatarsal insertion in 13/20 feet and variants in 7/20; it does not verify the Gray cuneiform extension.
- 사람 검토: not_performed; humanReviewed=false; surface review pending.
- 검토 입력란: 용어 [pending] / 기시 [pending] / 정지 [pending] / 우측 적용·모형 identity [pending] / 수정 제안·locator·근거 [빈칸]

## 단비골근 — HA-M-000006
한글 관용 표시명: 단비골근 / 우리말: 짧은종아리근 / 한자: 미확인 / 영어: Fibularis brevis / 별칭: Peroneus brevis
대상: 우측 하퇴 learner model, concept ID HA-M-000006; T14a selected row/detail and 3D route passed. 문헌 표본의 laterality·인구 범위가 우측 GLB와 동일한 것은 아니다.
TA2 label locator: Terminologia Anatomica, 2nd edition (TA2), Part 2; online edition published 2019; row 2653; printed page 95; https://fipat.library.dal.ca/wp-content/uploads/2020/09/FIPAT-TA2-Part-2.pdf
Gray locator: Section 8c, Lateral Crural Muscles, “The Peronæus brevis”; page not independently verified.
- 현재 화면에 놓인 한국어 구조 요약 (출처: Gray 1918 요약 번역, AI attribution; humanReviewed=false):
  - 전체 origin: 비골 몸통 가쪽면 아래쪽 2/3와 인접 앞·뒤 근육과의 근간중격에서 시작합니다. [claim IDs: HA-C-T05-FB-FIBULA-LATERAL-LOWER-TWO-THIRDS-ORIGIN, HA-C-T05-FB-SEPTA-ORIGIN]
  - 전체 insertion: 제5중족골 바닥 거친면의 가쪽에 부착합니다. [claim IDs: HA-C-T05-FB-MT5-INSERTION]
T05 origin claim IDs: HA-C-T05-FB-FIBULA-LATERAL-LOWER-TWO-THIRDS-ORIGIN, HA-C-T05-FB-SEPTA-ORIGIN
T05 insertion claim IDs: HA-C-T05-FB-MT5-INSERTION
- 현대 근거 대조 (T14a source analyst notes; 사람 검토 아님):
  - Kim D, Cho J, Lee M, Kwon HW, Choi YJ, Park KR, Park SB, Park J. Morphological Study of the Fibularis Brevis Tendon and Plantar Aponeurosis Lateral Band Insertion on the Fifth Metatarsal Base in Korean Cadavers. Anatomy & Biological Anthropology. 2022;35(3):75–83. DOI: 10.11637/aba.2022.35.3.75.
    - URL: https://www.kci.go.kr/kciportal/ci/sereArticleSearch/ciSereArtiView.kci?sereArticleSearchBean.artiId=ART002879102
    - 판본/locator/access: Journal article, volume 35 issue 3 (2022), pp. 75–83. Full-text PDF was not opened. / KCI article record/abstract, Korean and English abstract; PDF attempt was blocked by the browser client. / KCI record/abstract HTML opened; journal PDF not opened.
    - 직접 다룬 필드: insertion_fifth_metatarsal
    - 기시 대조: Study examines distal tendon insertion, not fibularis brevis origin.
    - 정지 대조: Abstract reports three insertion types among 96 feet and mean tendon-footprint length; supports variable attachment at the fifth metatarsal base but not a project-mesh boundary.
  - da Rocha Gomes M, Pinto AP, Fabián AA, Mota Gomes TJ, Navarro A, Martin Oliva X. Insertional anatomy of peroneal brevis and longus tendon — a cadaveric study. Foot and Ankle Surgery. 2019;25(5):636–639. DOI: 10.1016/j.fas.2018.07.005.
    - URL: https://pubmed.ncbi.nlm.nih.gov/30321932/
    - 판본/locator/access: Journal article, volume 25 issue 5 (2019); epub 2018-07-23. Publisher full text was not opened. / PubMed indexed abstract, Methods/Results; abstract opened in browser. / PubMed abstract HTML opened.
    - 직접 다룬 필드: insertion_fifth_metatarsal
    - 기시 대조: Study examines distal tendon insertions, not the brevis origin.
    - 정지 대조: Abstract reports usual fifth-metatarsal insertion in 11/20 feet and variants in 9/20.
- 사람 검토: not_performed; humanReviewed=false; surface review pending.
- 검토 입력란: 용어 [pending] / 기시 [pending] / 정지 [pending] / 우측 적용·모형 identity [pending] / 수정 제안·locator·근거 [빈칸]

## T13c 별도 context-only 기록
- B01: HA-A-T05-GASTRO-LAT-FEMUR-ORIGIN — source supports broad posterior-superior lateral femoral condyle wording; no reproducible mesh boundary; context_only, geometry:null, reviewId:null.
- B02: HA-A-T05-TA-TIBIA-CONDYLE-ORIGIN — Kimata 2022 broad condylar origin, but no FJ3387 footprint boundary; context_only, geometry:null, reviewId:null.
- B03: HA-A-T05-TA-TIBIA-SURFACE-ORIGIN — Kimata longitudinal distal endpoint is not a 2D mesh boundary; context_only, geometry:null, reviewId:null.
- 이 세 건은 별도 draft layer records다. 표면 후보로 계산하거나 사람 검토된 것으로 기록하지 않는다.

## 이 검토에서 사람이 결정할 사항
1. 각 표시 용어와 등록된 우리말/한자/영어가 해당 concept ID에 맞는지 확인하고, 바꿀 때는 사용한 표준·국내 용어 출처와 정확한 locator를 남긴다.
2. Gray 번역 요약이 해당 원문 항목을 충실히 반영하는지, 누락/모호성/현대 용어 차이가 있는지 근거 절/페이지와 함께 판정한다.
3. 현대 연구의 표본·방법·직접 측정 필드가 각 O/I claim을 지지하는 범위를 판정한다. 배경 인용과 직접 결과를 구분한다.
4. 우측 model identity와 source specimen의 적용 범위를 검토한다. 왼쪽/오른쪽 대칭이나 mesh attachment를 추정하지 않는다.
5. 각 claim을 accept/revise/hold로 결정하고 실제 검토자의 표현·날짜·revision hash를 입력한다. 좌표/표면 geometry는 이 packet만으로 만들지 않는다.

## 남은 기술/근거 범위
- T05 부착 41건: source-backed surface 0, whole-bone context text_only 28, matching target mesh missing 13, human_review_pending 41.
- T13c B01–B03 geometry-null draft 3건; canonical spatialAnnotation 0. 새 geometry 없음.
- 현대 비교 자료는 learner panel에 연결되지 않았다. 이 packet은 work evidence 전용이다.
- 외부 사람 의견 없이 reviewed 또는 reviewed_structure_release로 승격 금지.
