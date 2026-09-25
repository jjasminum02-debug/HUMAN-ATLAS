# T04 용어 정책 — 부분 카탈로그

- 국제 명칭의 기준 후보는 IFAA가 승인한 FIPAT `Terminologia Anatomica`, 제2판(TA2, 온라인 2019)이다. 이번 작업은 공식 Part 2 PDF의 검색 색인에서 확인된 행만 기록했다. 원본 PDF 바이너리와 고정판 checksum은 확보하지 못했다.
- 각 관찰 문자열은 지정된 TA2 행/인쇄 쪽에 연결하고 `needs_review`로 둔다. 원본 PDF 화면을 확인하지 못해 공식 Latin term, 언어별 equivalent, synonym, related term 중 어느 열인지 확인되지 않은 문자열에는 source-crosswalk에 `cell role unverified`를 표시했다. 어휘의 preferred 상태는 승인하지 않았다.
- 정확한 Korean Anatomical Terminology 원본과 현행 판본, 근육별 항목 locator가 없으므로 Hangul과 Hanja 용어는 모든 catalog node에서 null과 사유로 둔다. 영어/라틴어 표현을 한국어 또는 한자로 번역하지 않는다.
- ID는 이름·언어·외부 FMA ID·메시 파일명과 독립된 프로젝트 발급 불투명 ID다. 발급된 ID를 이름 변경이나 새 판본 때문에 바꾸거나 재사용하지 않고 새 항목은 새 ID를 추가한다. group은 `HA-G-*`, denominator muscle은 `HA-M-*`, head/part는 `HA-P-*`, 확인된 variant는 향후 `HA-V-*` namespace를 사용한다.
- denominator에는 `individual_muscle`만 한 번씩 포함한다. 좌우는 instance에 두며 별도 개념으로 세지 않는다. muscle group과 head/part는 트리 노드로 남기고 denominator에서 제외한다. variant는 standard concept와 별도 유형이지만 이번 excerpt만으로 확인한 variant는 없다. `variants=0`은 부재 증명이 아니다.
- T02 BodyParts3D FMA/representation/OBJ 연결은 보조 crosswalk이며, 이름 일치만으로 해부학적 동일성을 검토 완료하지 않는다. 우측 gastrocnemius OBJ 두 개는 `HA-P-*`의 근두 mesh 후보에만 연결하고 whole gastrocnemius의 mesh로 합치지 않는다.
- FIPAT/IFAA 페이지가 TA2에 대해 안내하는 이용 조건은 CC BY-ND 4.0이다. 이 부분 catalog는 내부 검토용 파생 인덱스로 취급한다. 정확한 파일별 attribution과 파생 목록의 외부 재배포 권리는 별도 검토 전까지 미승인이다.
- 상태는 `partial_source_index_extract`; 전신 분모는 null이며 전체 목록 gate는 차단 상태다. 이 파일은 근육별 기능·기시·정지 주장이나 리뷰 승인을 담지 않는다.
