# T05 파일럿 구조 자료 검토 대기

확인일: 2026-09-25. 이 queue는 T05의 source-located text 입력 후에도 남아 있는 내용을 구분한다. 이 파일의 미해결 기록은 해부학적으로 확정됐다는 뜻이 아니다.

## 6개 pilot의 명칭

- T04 canonical catalog의 TA2 Part 2 row에서 Latin/English 표기와 page/row evidence를 연결했다. 대상은 gastrocnemius `HA-M-000001`, soleus `HA-M-000002`, tibialis anterior/posterior `HA-M-000003/4`, fibularis longus/brevis `HA-M-000005/6`이다. Gastrocnemius lateral/medial head `HA-P-000001/2`는 별도 part ID다.
- 해당 TA2 PDF 바이너리/checksum과 페이지 시각 대조 및 Errata 전수 확인은 미완료다. TA2 표 열의 official/equivalent/synonym 역할은 아직 검토하지 않았고 관련 term records를 `needs_review`로 둔다.
- 여덟 개 muscle/part의 한국어 Hangul과 Hanja 용어는 null/held로 유지했다. 대한해부학회 용어 자료의 정확한 edition, entry locator 및 Hanja 대응을 확보한 뒤에만 입력한다.

## 기시·정지·관련 구조 claims

- T05 claims는 Henry Gray, Warren H. Lewis 편, *Anatomy of the Human Body*, 20th US edition (1918), section 8c의 muscle subsection locator에 연결된 historical-source summaries다. Tibialis anterior에는 page 480 locator가 있다. Gray 판본은 현행 기준서가 아니다.
- 41 attachment records와 45 claims는 모두 `needs_review`다. 이 task에서 사람의 해부학 검토·승인은 하지 않았다. 독립된 현대 해부학 교재/표준 출처와 claim-by-claim 비교가 필요하다.
- 변이 문장은 별도 변이 concept/claim으로 정규화하지 않았다. Gray section 8c가 서술하는 비복근 바깥 근두·추가 슬립, 가자미근 부속 근두, 앞정강근의 드문 추가 건성 슬립, 긴종아리근의 간헐적 경골 섬유/둘째발허리뼈 슬립, 종아리근의 추가 슬립·별도 근육 기술을 사람 검토 후 분류해야 한다. 원문에는 다른 근육 변이도 있어 전수 목록으로 간주하지 않는다.
- 넓은 부착은 Gray가 지정한 골 표지/면과 구역별로 나눴지만 이를 mesh 위치/좌표 또는 세부 면적 경계로 해석하지 않는다. T02 BodyParts3D crosswalk는 T04에서 provisional로 남아 있고 T05에서 annotation을 만들지 않았다.
- course claims는 힘줄과 관련 구조의 문장 관계만 기록한다. 근육 기능, 동작, 평가 프로토콜, 진단/치료 문장으로 확장하지 않는다.

## 출처·공개 상태

- OpenStax Anatomy and Physiology 2e는 해당 공식 section page의 generative-AI ingestion restriction을 확인해 본문 해부 claim 추출에 사용하지 않았다. 기존 source registry에 restriction과 제외 상태를 보존했다.
- Gray 1918 원본의 미국 내 public-domain 표시는 BHL 서지 레코드로 확인했지만, 세계 각 지역의 재사용 조건은 검토하지 않았다. source registry는 internal/research 사용만 기록하며 공개/재배포는 승인하지 않았다.
- 실제 좌표, 3D annotation, 앱, 전체 근육 목록, 공개 학습 자료, 임상용 콘텐츠는 없다.
