# T11-B02 웹 출처 접근 기록

조회일: 2026-09-25. 이 파일은 접근방식 및 근거 한계를 추적한다. 검색 색인은 원문을 열어 읽은 상태가 아니다.

## FIPAT TA2 Part 2

- URL: https://fipat.library.dal.ca/wp-content/uploads/2020/09/FIPAT-TA2-Part-2.pdf
- 판본: *Terminologia Anatomica*, second edition (TA2), Part 2; online edition published 2019. URL 경로에 hosted PDF의 2020-09 날짜가 보인다.
- locator: printed pages/rows `74/2040`, `74/2041`, `77/2104`, `77/2116`, `81/2225`, `83/2299`, `89/2450`, `89/2451`, `89/2456`, `94/2592`.
- 접근: 공식 검색 색인 결과로 위 행들의 English/Latin 문자열을 확인했다. PDF 원문 열기 요청은 HTTP 502 오류였고, 바이너리/hash/페이지 이미지/표 열 역할/정오표를 대조하지 않았다.
- 한계: crosswalk에서 온 exact row locator와 표기 observation이다. 열 이름은 시각 검토가 없어 공식 preferred term 대조로 간주하지 않는다.

## KMLE 통합검색 및 표시 사전 섹션

모든 URL의 확인일은 2026-09-25다. KMLE는 사전별 검색 결과를 한 페이지에 모은다. 페이지의 각 밑줄 사전 이름은 확인할 수 있어도 해당 저작물의 정확한 판본·발행연도·페이지가 미노출된 경우 이를 `not exposed`로 기록했다.

| URL | 접근방법 | locator/관찰 |
|---|---|---|
| https://m.kmle.co.kr/search.php?Page=4&Search=group+of+muscles | search result excerpt | muscles of head / musculi capitis의 머리근육, 두부근(頭部筋) 표기 |
| https://m.kmle.co.kr/search.php?Search=extraocular | opened HTML page text | current section의 바깥눈근육·외안근, legacy section의 외안근(外眼筋); source editions not exposed |
| https://m.kmle.co.kr/search.php?Page=4&Search=transversospinalis+muscles | search result excerpt | muscles of mastication의 저작근(咀嚼筋), lower-limb group의 다리근육; page title query와 결과항목은 별개임을 보존 |
| https://m.kmle.co.kr/search.php?Search=musc | search result excerpt | 대한해부학회로 표시된 결과의 muscles of mastication→씹기근육, muscles of tongue→혀근육/old 설근, pectoralis muscles→가슴근육 |
| https://m.kmle.co.kr/search.php?Search=back | search result excerpt | generic muscles of back / musculi dorsi→등근육, 배부근(背部筋); assigned hypaxial group와 동치로 보지 않음 |
| https://m.kmle.co.kr/search.php?Search=thorax | search result excerpt | old 대한의협 3 entry muscles of thorax / musculi thoracis→가슴근육, 흉부근(胸部筋); KMLE anatomy index의 pectoralis collision 별도 기록 |
| https://m.kmle.co.kr/search.php?Page=2&Search=upper | search result excerpt | muscles of upper limb→팔근육 |
| https://m.kmle.co.kr/search.php?FuzzyTrack=scapula&IsFuzzy=YES&Search=scapulo | search result excerpt | scapulohumeral adjective→어깨위팔-/견갑상완(골)-만 관찰; exact group Korean term 미관찰 |
| https://m.kmle.co.kr/search.php?Search=rotator+cuff | opened HTML page text | rotator cuff→돌림근띠·회전근개; legacy 근육둘레띠 and 回旋腱板 are cuff-term entries, not proven synonym for the whole assigned muscle-group entity |

## 분리된 상태

- Search index/excerpt: 각 evidence row의 `verificationMode` 값으로 표시했다.
- Opened page: extraocular와 rotator cuff만 HTML text를 열어 확인했다. 이 확인은 해당 출처의 페이지 텍스트 확인일 뿐, TA2 표 열 검증이 아니다.
- Human anatomy review: 수행하지 않았다. 모든 B02 field/record는 `not_performed`, `humanReviewed=false`다.
- 부정 검색은 전수 부재 증명이 아니다. 검색 결과에서 정확한 그룹 이름을 확보하지 못한 항목은 미확인으로 남겼다.
