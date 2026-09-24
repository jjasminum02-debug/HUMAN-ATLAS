# T02 — BodyParts3D 자산 검토 대기/누락 목록

확인일: 2026-09-25. 이 문서는 메시 가용성/출처 crosswalk 기록이며, 해부학적 부착 claim이나 사람 리뷰가 아니다.

## 우측 종아리 pilot 6개

| Pilot | BodyParts3D IS-A row / source IDs | 자산 상태 | 남은 확인 |
|---|---|---|---|
| gastrocnemius | 우측 medial head FMA45957 / BP5539 / FJ1397; lateral head FMA45960 / BP5541 / FJ1394 | 두 head mesh 획득. 단일 whole-right muscle 파일이 아니라 head별 표현 | 두 메시를 한 pilot 개념에 대응시키는 Atlas crosswalk은 후보 상태; 사람 검토 전 verified 아님 |
| soleus | FMA22558 / BP4999 / FJ1437 | 획득·shape trial 표시 | 부착면·형태 적합성 사람 검토 대기 |
| tibialis anterior | FMA22544 / BP5018 / FJ1439 | 획득·ID 확인 | 시각 shape 검토/부착면 사람 검토 대기 |
| tibialis posterior | FMA65018 / BP5004 / FJ1440 | 획득·ID 확인 | 시각 shape 검토/부착면 사람 검토 대기 |
| fibularis longus | FMA22552 / BP5013 / FJ1410 | 획득·ID 확인 | 시각 shape 검토/부착면 사람 검토 대기 |
| fibularis brevis | FMA22554 / BP5015 / FJ1409 | 획득·ID 확인 | 시각 shape 검토/부착면 사람 검토 대기 |

## 연결 영역에서 찾은 우측 뼈 ID

IS-A `isa_parts_list_e.txt` 및 `isa_element_parts.txt`에서 아래 FMA/BP/FJ 대응을 확인했다. 메시를 로컬 취득한 것은 네 항목뿐이다. 나머지는 표상 가용성만 기록한다. 이 목록은 특정 pilot muscle의 기시/정지 또는 부착 claim이 아니다.

| 구조 | FMA / BP / FJ | 로컬 상태 |
|---|---|---|
| femur (right) | FMA24474 / BP8920 / FJ3365 | 표상만 확인; 미취득 |
| tibia (right) | FMA24477 / BP8031 / FJ3387 | 취득 및 trial |
| fibula (right) | FMA24480 / BP8009 / FJ3366 | 취득 및 trial |
| talus (right) | FMA24482 / BP8033 / FJ3385 | 취득 및 trial |
| calcaneus (right) | FMA24497 / BP9040 / FJ3360 | 취득 및 trial |
| navicular (right) | FMA24500 / BP9133 / FJ3308 | 표상만 확인; 미취득 |
| first metatarsal (right) | FMA24507 / BP8230 / FJ3351 | 표상만 확인; 미취득 |
| fifth metatarsal (right) | FMA24515 / BP7912 / FJ3359 | 표상만 확인; 미취득 |
| medial cuneiform (right) | FMA24521 / BP8830 / FJ3377 | 표상만 확인; 미취득 |

전체 crosswalk와 official table locator row는 `work/evidence/T02/source-crosswalk.json`을 보라. 취득 파일 해시와 원본 헤더/경계값은 `work/evidence/T02/geometry-inspection.json`에 있다.

## 해석 및 이용 한계

- BodyParts3D의 형태 후보가 기시·정지 영역의 근거가 되지는 않는다. 이 task에서 부착점/면을 생성하지 않았다.
- 원본 archive의 current README/license는 CC BY 4.0과 지정 귀속을 기록한다. OBJ 내부 코멘트에는 이전 CC BY-SA 2.1 Japan 안내가 남아 있어 제거하지 않았다. 이번 작업에서는 현재 LSDB Archive notice와 exact credit을 manifest에 기록했으며, 외부 공개는 하지 않았다.
- archive release가 경고한 데이터 누락/형태 오류, 성인 남성 한 reference model, 99%-reduction 자료의 모형 충실도 한계는 해부학 정확성 검토가 아니다.
- 남은 사람 확인: 6 pilot 각각의 mesh identity/shape, gastrocnemius 두 head와 전체 표시 관계, 관련 뼈의 선택 범위, 이후 T10에서 별도로 수행할 부착면 검토.
