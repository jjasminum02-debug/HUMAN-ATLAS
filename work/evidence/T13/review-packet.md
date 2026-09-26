# T13 사람 검토용 부착 표면 패킷

상태: **검토 대상 목록**. 실제 부착 표면 패치, 선, 점은 0개다. 아래 `표면 후보`는 해당 뼈 전체의 *검색 대상*이며 부착면 위치나 범위를 나타내지 않는다.

- 원문 경계: T05 Gray 1918 요약 claim, 모두 `needs_review`. 현대 독립 대조와 사람 해부학 검토 전이다.
- 자산 경계: BodyParts3D Release 4.0 우측 정적 모델, 출처 구조 교차표는 후보. 뼈 형상이 원문의 세부 부착 위치를 자동 지정하지 않는다.
- 좌표: `HUMAN_ATLAS_RH_M_XLEFT_YHEAD_ZANTERIOR`, 단위 `m`, pose `bodyparts3d-r4-static-reference`. T07/T13 GLB hash는 `attachment-context-t13.json`에 고정되어 있다.
- 검토 절차: `/review`에서 근두·원문·대상 구조를 확인하고 뼈만 격리해 정면·후면·우측 측면 및 자유 회전을 각각 확인한다. 실제 면 범위를 삼각형 패치 또는 경계선으로 표시하고 T09 draft JSON의 asset hash·topology·pose·claim 증거를 재검증한다. 사람 검토 전 canonical SpatialAnnotation으로 승격하지 않는다.
- 현재 실행 확인: 브라우저에서 세 카메라 프리셋, 대퇴골 단독 격리, 표면 pick, 임시 초안 저장·삭제가 동작했다. 항목별 다각도 해부학 판독은 수행하지 않았다.

| 근육/근두 | 부착 | 대상 구조 | 표면 후보/상태 | 정면·후면·측면 판독 |
|---|---|---|---|---|
| HA-P-000001 | origin | HA-S-FEMORAL-CONDYLE-LATERAL | HA-MESH-BP3D4-FJ3365 뼈 전체 검색만; patch 미지정; `a5b16cf1e699…` | 미실시 / 미실시 / 미실시 |
| HA-P-000001 | origin | HA-S-FEMUR-POSTERIOR-ABOVE-LATERAL-CONDYLE | HA-MESH-BP3D4-FJ3365 뼈 전체 검색만; patch 미지정; `a5b16cf1e699…` | 미실시 / 미실시 / 미실시 |
| HA-P-000001 | origin | HA-S-KNEE-CAPSULE | 대상 mesh 미확보; 보류 | 미실시 / 미실시 / 미실시 |
| HA-P-000002 | origin | HA-S-FEMORAL-CONDYLE-MEDIAL | HA-MESH-BP3D4-FJ3365 뼈 전체 검색만; patch 미지정; `a5b16cf1e699…` | 미실시 / 미실시 / 미실시 |
| HA-P-000002 | origin | HA-S-FEMUR-ADJACENT-MEDIAL-CONDYLE | HA-MESH-BP3D4-FJ3365 뼈 전체 검색만; patch 미지정; `a5b16cf1e699…` | 미실시 / 미실시 / 미실시 |
| HA-P-000002 | origin | HA-S-KNEE-CAPSULE | 대상 mesh 미확보; 보류 | 미실시 / 미실시 / 미실시 |
| HA-M-000001 | insertion | HA-S-CALCANEUS-POSTERIOR-MIDDLE | HA-MESH-BP3D4-FJ3360 뼈 전체 검색만; patch 미지정; `044450c3230b…` | 미실시 / 미실시 / 미실시 |
| HA-M-000002 | origin | HA-S-FIBULA-HEAD | HA-MESH-BP3D4-FJ3366 뼈 전체 검색만; patch 미지정; `044450c3230b…` | 미실시 / 미실시 / 미실시 |
| HA-M-000002 | origin | HA-S-FIBULA-POSTERIOR-UPPER-THIRD | HA-MESH-BP3D4-FJ3366 뼈 전체 검색만; patch 미지정; `044450c3230b…` | 미실시 / 미실시 / 미실시 |
| HA-M-000002 | origin | HA-S-TIBIA-POPLITEAL-LINE | HA-MESH-BP3D4-FJ3387 뼈 전체 검색만; patch 미지정; `044450c3230b…` | 미실시 / 미실시 / 미실시 |
| HA-M-000002 | origin | HA-S-TIBIA-MEDIAL-BORDER-MIDDLE-THIRD | HA-MESH-BP3D4-FJ3387 뼈 전체 검색만; patch 미지정; `044450c3230b…` | 미실시 / 미실시 / 미실시 |
| HA-M-000002 | origin | HA-S-TENDINOUS-ARCH-SOLEUS | 대상 mesh 미확보; 보류 | 미실시 / 미실시 / 미실시 |
| HA-M-000002 | insertion | HA-S-CALCANEUS-POSTERIOR-MIDDLE | HA-MESH-BP3D4-FJ3360 뼈 전체 검색만; patch 미지정; `044450c3230b…` | 미실시 / 미실시 / 미실시 |
| HA-M-000003 | origin | HA-S-TIBIA-LATERAL-CONDYLE | HA-MESH-BP3D4-FJ3387 뼈 전체 검색만; patch 미지정; `044450c3230b…` | 미실시 / 미실시 / 미실시 |
| HA-M-000003 | origin | HA-S-TIBIA-UPPER-LATERAL-SURFACE | HA-MESH-BP3D4-FJ3387 뼈 전체 검색만; patch 미지정; `044450c3230b…` | 미실시 / 미실시 / 미실시 |
| HA-M-000003 | origin | HA-S-INTEROSSEOUS-MEMBRANE-LEG | 대상 mesh 미확보; 보류 | 미실시 / 미실시 / 미실시 |
| HA-M-000003 | origin | HA-S-CRURAL-FASCIA | 대상 mesh 미확보; 보류 | 미실시 / 미실시 / 미실시 |
| HA-M-000003 | origin | HA-S-TA-EDL-SEPTUM | 대상 mesh 미확보; 보류 | 미실시 / 미실시 / 미실시 |
| HA-M-000003 | insertion | HA-S-MEDIAL-CUNEIFORM-INFEROMEDIAL-SURFACE | HA-MESH-BP3D4-FJ3377 뼈 전체 검색만; patch 미지정; `a5b16cf1e699…` | 미실시 / 미실시 / 미실시 |
| HA-M-000003 | insertion | HA-S-BASE-METATARSAL-1 | HA-MESH-BP3D4-FJ3351 뼈 전체 검색만; patch 미지정; `a5b16cf1e699…` | 미실시 / 미실시 / 미실시 |
| HA-M-000004 | origin | HA-S-INTEROSSEOUS-MEMBRANE-LEG | 대상 mesh 미확보; 보류 | 미실시 / 미실시 / 미실시 |
| HA-M-000004 | origin | HA-S-TIBIA-POSTERIOR-LATERAL-TP-REGION | HA-MESH-BP3D4-FJ3387 뼈 전체 검색만; patch 미지정; `044450c3230b…` | 미실시 / 미실시 / 미실시 |
| HA-M-000004 | origin | HA-S-FIBULA-MEDIAL-UPPER-TWO-THIRDS | HA-MESH-BP3D4-FJ3366 뼈 전체 검색만; patch 미지정; `044450c3230b…` | 미실시 / 미실시 / 미실시 |
| HA-M-000004 | origin | HA-S-DEEP-TRANSVERSE-FASCIA-LEG | 대상 mesh 미확보; 보류 | 미실시 / 미실시 / 미실시 |
| HA-M-000004 | origin | HA-S-TP-ADJACENT-INTERMUSCULAR-SEPTA | 대상 mesh 미확보; 보류 | 미실시 / 미실시 / 미실시 |
| HA-M-000004 | insertion | HA-S-NAVICULAR-TUBEROSITY | HA-MESH-BP3D4-FJ3308 뼈 전체 검색만; patch 미지정; `a5b16cf1e699…` | 미실시 / 미실시 / 미실시 |
| HA-M-000004 | other_attachment | HA-S-SUSTENTACULUM-TALI | HA-MESH-BP3D4-FJ3360 뼈 전체 검색만; patch 미지정; `044450c3230b…` | 미실시 / 미실시 / 미실시 |
| HA-M-000004 | other_attachment | HA-S-CUNEIFORM-BONES | 대상 mesh 미확보; 보류 | 미실시 / 미실시 / 미실시 |
| HA-M-000004 | other_attachment | HA-S-CUBOID | HA-MESH-BP3D4-FJ3364 뼈 전체 검색만; patch 미지정; `a5b16cf1e699…` | 미실시 / 미실시 / 미실시 |
| HA-M-000004 | other_attachment | HA-S-BASE-METATARSAL-2 | HA-MESH-BP3D4-FJ3353 뼈 전체 검색만; patch 미지정; `a5b16cf1e699…` | 미실시 / 미실시 / 미실시 |
| HA-M-000004 | other_attachment | HA-S-BASE-METATARSAL-3 | HA-MESH-BP3D4-FJ3355 뼈 전체 검색만; patch 미지정; `a5b16cf1e699…` | 미실시 / 미실시 / 미실시 |
| HA-M-000004 | other_attachment | HA-S-BASE-METATARSAL-4 | HA-MESH-BP3D4-FJ3357 뼈 전체 검색만; patch 미지정; `a5b16cf1e699…` | 미실시 / 미실시 / 미실시 |
| HA-M-000005 | origin | HA-S-FIBULA-HEAD | HA-MESH-BP3D4-FJ3366 뼈 전체 검색만; patch 미지정; `044450c3230b…` | 미실시 / 미실시 / 미실시 |
| HA-M-000005 | origin | HA-S-FIBULA-LATERAL-UPPER-TWO-THIRDS | HA-MESH-BP3D4-FJ3366 뼈 전체 검색만; patch 미지정; `044450c3230b…` | 미실시 / 미실시 / 미실시 |
| HA-M-000005 | origin | HA-S-CRURAL-FASCIA | 대상 mesh 미확보; 보류 | 미실시 / 미실시 / 미실시 |
| HA-M-000005 | origin | HA-S-LATERAL-LEG-SEPTA | 대상 mesh 미확보; 보류 | 미실시 / 미실시 / 미실시 |
| HA-M-000005 | insertion | HA-S-BASE-METATARSAL-1 | HA-MESH-BP3D4-FJ3351 뼈 전체 검색만; patch 미지정; `a5b16cf1e699…` | 미실시 / 미실시 / 미실시 |
| HA-M-000005 | insertion | HA-S-MEDIAL-CUNEIFORM | HA-MESH-BP3D4-FJ3377 뼈 전체 검색만; patch 미지정; `a5b16cf1e699…` | 미실시 / 미실시 / 미실시 |
| HA-M-000006 | origin | HA-S-FIBULA-LATERAL-LOWER-TWO-THIRDS | HA-MESH-BP3D4-FJ3366 뼈 전체 검색만; patch 미지정; `044450c3230b…` | 미실시 / 미실시 / 미실시 |
| HA-M-000006 | origin | HA-S-LATERAL-LEG-SEPTA | 대상 mesh 미확보; 보류 | 미실시 / 미실시 / 미실시 |
| HA-M-000006 | insertion | HA-S-TUBEROSITY-BASE-METATARSAL-5 | HA-MESH-BP3D4-FJ3359 뼈 전체 검색만; patch 미지정; `a5b16cf1e699…` | 미실시 / 미실시 / 미실시 |

## 원문별 판독 대기 항목

### 1. HA-A-T05-GASTRO-LAT-FEMUR-ORIGIN

- 근육/근두: `HA-P-000001`; 우측 instance `HA-I-R-HA-M-000001`; 부착 `origin`.
- 대상: `HA-S-FEMORAL-CONDYLE-LATERAL`; 뼈 `HA-S-FEMUR`.
- T05 근거 문장: The lateral head arises at an impression on the side of the lateral femoral condyle.
- claim `HA-C-T05-GASTRO-LAT-FEMUR-ORIGIN`; evidence `EV-GRAY1918-GASTRO`.
- 표면 후보: `HA-MESH-BP3D4-FJ3365` 뼈 전체 검색 컨텍스트만. 삼각형 ID/범위는 없음.
- 검토 기록: 정면 [ ] 후면 [ ] 우측 측면 [ ] 자유 회전 [ ] 범위/다른 출처 [ ] 사람 검토 [ ].

### 2. HA-A-T05-GASTRO-LAT-FEMUR-POSTERIOR-ORIGIN

- 근육/근두: `HA-P-000001`; 우측 instance `HA-I-R-HA-M-000001`; 부착 `origin`.
- 대상: `HA-S-FEMUR-POSTERIOR-ABOVE-LATERAL-CONDYLE`; 뼈 `HA-S-FEMUR`.
- T05 근거 문장: The lateral head also arises from the posterior femoral surface immediately above the lateral part of the condyle.
- claim `HA-C-T05-GASTRO-LAT-FEMUR-POSTERIOR-ORIGIN`; evidence `EV-GRAY1918-GASTRO`.
- 표면 후보: `HA-MESH-BP3D4-FJ3365` 뼈 전체 검색 컨텍스트만. 삼각형 ID/범위는 없음.
- 검토 기록: 정면 [ ] 후면 [ ] 우측 측면 [ ] 자유 회전 [ ] 범위/다른 출처 [ ] 사람 검토 [ ].

### 3. HA-A-T05-GASTRO-LAT-KNEE-CAPSULE-ORIGIN

- 근육/근두: `HA-P-000001`; 우측 instance `HA-I-R-HA-M-000001`; 부착 `origin`.
- 대상: `HA-S-KNEE-CAPSULE`; 뼈 `mesh 미확보`.
- T05 근거 문장: The source states that both gastrocnemius heads also arise from the subjacent knee-joint capsule.
- claim `HA-C-T05-GASTRO-LAT-KNEE-CAPSULE-ORIGIN`; evidence `EV-GRAY1918-GASTRO`.
- 표면 후보: 없음. 해당 대상 mesh 미확보로 보류.
- 검토 기록: 정면 [ ] 후면 [ ] 우측 측면 [ ] 자유 회전 [ ] 범위/다른 출처 [ ] 사람 검토 [ ].

### 4. HA-A-T05-GASTRO-MED-FEMUR-ORIGIN

- 근육/근두: `HA-P-000002`; 우측 instance `HA-I-R-HA-M-000001`; 부착 `origin`.
- 대상: `HA-S-FEMORAL-CONDYLE-MEDIAL`; 뼈 `HA-S-FEMUR`.
- T05 근거 문장: The medial, larger head arises from a depression at the upper posterior part of the medial femoral condyle.
- claim `HA-C-T05-GASTRO-MED-FEMUR-ORIGIN`; evidence `EV-GRAY1918-GASTRO`.
- 표면 후보: `HA-MESH-BP3D4-FJ3365` 뼈 전체 검색 컨텍스트만. 삼각형 ID/범위는 없음.
- 검토 기록: 정면 [ ] 후면 [ ] 우측 측면 [ ] 자유 회전 [ ] 범위/다른 출처 [ ] 사람 검토 [ ].

### 5. HA-A-T05-GASTRO-MED-FEMUR-ADJACENT-ORIGIN

- 근육/근두: `HA-P-000002`; 우측 instance `HA-I-R-HA-M-000001`; 부착 `origin`.
- 대상: `HA-S-FEMUR-ADJACENT-MEDIAL-CONDYLE`; 뼈 `HA-S-FEMUR`.
- T05 근거 문장: The medial head also arises from the femur adjacent to the upper posterior part of the medial condyle.
- claim `HA-C-T05-GASTRO-MED-FEMUR-ADJACENT-ORIGIN`; evidence `EV-GRAY1918-GASTRO`.
- 표면 후보: `HA-MESH-BP3D4-FJ3365` 뼈 전체 검색 컨텍스트만. 삼각형 ID/범위는 없음.
- 검토 기록: 정면 [ ] 후면 [ ] 우측 측면 [ ] 자유 회전 [ ] 범위/다른 출처 [ ] 사람 검토 [ ].

### 6. HA-A-T05-GASTRO-MED-KNEE-CAPSULE-ORIGIN

- 근육/근두: `HA-P-000002`; 우측 instance `HA-I-R-HA-M-000001`; 부착 `origin`.
- 대상: `HA-S-KNEE-CAPSULE`; 뼈 `mesh 미확보`.
- T05 근거 문장: The source states that both gastrocnemius heads also arise from the subjacent knee-joint capsule.
- claim `HA-C-T05-GASTRO-MED-KNEE-CAPSULE-ORIGIN`; evidence `EV-GRAY1918-GASTRO`.
- 표면 후보: 없음. 해당 대상 mesh 미확보로 보류.
- 검토 기록: 정면 [ ] 후면 [ ] 우측 측면 [ ] 자유 회전 [ ] 범위/다른 출처 [ ] 사람 검토 [ ].

### 7. HA-A-T05-GASTRO-CALCANEUS-INSERTION

- 근육/근두: `HA-M-000001`; 우측 instance `HA-I-R-HA-M-000001`; 부착 `insertion`.
- 대상: `HA-S-CALCANEUS-POSTERIOR-MIDDLE`; 뼈 `HA-S-CALCANEUS`.
- T05 근거 문장: The head aponeuroses converge into the gastrocnemius aponeurosis, which joins the soleus tendon as the calcaneal tendon; the shared tendon attaches to the middle posterior calcaneus.
- claim `HA-C-T05-GASTRO-CALCANEUS-INSERTION`; evidence `EV-GRAY1918-GASTRO`, `EV-GRAY1918-CALCANEAL-TENDON`.
- 표면 후보: `HA-MESH-BP3D4-FJ3360` 뼈 전체 검색 컨텍스트만. 삼각형 ID/범위는 없음.
- 검토 기록: 정면 [ ] 후면 [ ] 우측 측면 [ ] 자유 회전 [ ] 범위/다른 출처 [ ] 사람 검토 [ ].

### 8. HA-A-T05-SOLEUS-FIBULA-HEAD-ORIGIN

- 근육/근두: `HA-M-000002`; 우측 instance `HA-I-R-HA-M-000002`; 부착 `origin`.
- 대상: `HA-S-FIBULA-HEAD`; 뼈 `HA-S-FIBULA`.
- T05 근거 문장: Tendinous fibers arise from the back of the head of the fibula.
- claim `HA-C-T05-SOLEUS-FIBULA-HEAD-ORIGIN`; evidence `EV-GRAY1918-SOLEUS`.
- 표면 후보: `HA-MESH-BP3D4-FJ3366` 뼈 전체 검색 컨텍스트만. 삼각형 ID/범위는 없음.
- 검토 기록: 정면 [ ] 후면 [ ] 우측 측면 [ ] 자유 회전 [ ] 범위/다른 출처 [ ] 사람 검토 [ ].

### 9. HA-A-T05-SOLEUS-FIBULA-POSTERIOR-UPPER-THIRD-ORIGIN

- 근육/근두: `HA-M-000002`; 우측 instance `HA-I-R-HA-M-000002`; 부착 `origin`.
- 대상: `HA-S-FIBULA-POSTERIOR-UPPER-THIRD`; 뼈 `HA-S-FIBULA`.
- T05 근거 문장: Tendinous fibers arise from the upper third of the posterior surface of the fibular body.
- claim `HA-C-T05-SOLEUS-FIBULA-POSTERIOR-UPPER-THIRD-ORIGIN`; evidence `EV-GRAY1918-SOLEUS`.
- 표면 후보: `HA-MESH-BP3D4-FJ3366` 뼈 전체 검색 컨텍스트만. 삼각형 ID/범위는 없음.
- 검토 기록: 정면 [ ] 후면 [ ] 우측 측면 [ ] 자유 회전 [ ] 범위/다른 출처 [ ] 사람 검토 [ ].

### 10. HA-A-T05-SOLEUS-TIBIA-POPLITEAL-LINE-ORIGIN

- 근육/근두: `HA-M-000002`; 우측 instance `HA-I-R-HA-M-000002`; 부착 `origin`.
- 대상: `HA-S-TIBIA-POPLITEAL-LINE`; 뼈 `HA-S-TIBIA`.
- T05 근거 문장: The source identifies the popliteal line as part of the tibial origin.
- claim `HA-C-T05-SOLEUS-TIBIA-POPLITEAL-LINE-ORIGIN`; evidence `EV-GRAY1918-SOLEUS`.
- 표면 후보: `HA-MESH-BP3D4-FJ3387` 뼈 전체 검색 컨텍스트만. 삼각형 ID/범위는 없음.
- 검토 기록: 정면 [ ] 후면 [ ] 우측 측면 [ ] 자유 회전 [ ] 범위/다른 출처 [ ] 사람 검토 [ ].

### 11. HA-A-T05-SOLEUS-TIBIA-MEDIAL-BORDER-ORIGIN

- 근육/근두: `HA-M-000002`; 우측 instance `HA-I-R-HA-M-000002`; 부착 `origin`.
- 대상: `HA-S-TIBIA-MEDIAL-BORDER-MIDDLE-THIRD`; 뼈 `HA-S-TIBIA`.
- T05 근거 문장: The source identifies the middle third of the medial tibial border as part of the tibial origin.
- claim `HA-C-T05-SOLEUS-TIBIA-MEDIAL-BORDER-ORIGIN`; evidence `EV-GRAY1918-SOLEUS`.
- 표면 후보: `HA-MESH-BP3D4-FJ3387` 뼈 전체 검색 컨텍스트만. 삼각형 ID/범위는 없음.
- 검토 기록: 정면 [ ] 후면 [ ] 우측 측면 [ ] 자유 회전 [ ] 범위/다른 출처 [ ] 사람 검토 [ ].

### 12. HA-A-T05-SOLEUS-ARCH-ORIGIN

- 근육/근두: `HA-M-000002`; 우측 instance `HA-I-R-HA-M-000002`; 부착 `origin`.
- 대상: `HA-S-TENDINOUS-ARCH-SOLEUS`; 뼈 `mesh 미확보`.
- T05 근거 문장: Some fibers arise from a tendinous arch placed between the tibial and fibular origins.
- claim `HA-C-T05-SOLEUS-ARCH-ORIGIN`; evidence `EV-GRAY1918-SOLEUS`.
- 표면 후보: 없음. 해당 대상 mesh 미확보로 보류.
- 검토 기록: 정면 [ ] 후면 [ ] 우측 측면 [ ] 자유 회전 [ ] 범위/다른 출처 [ ] 사람 검토 [ ].

### 13. HA-A-T05-SOLEUS-CALCANEUS-INSERTION

- 근육/근두: `HA-M-000002`; 우측 instance `HA-I-R-HA-M-000002`; 부착 `insertion`.
- 대상: `HA-S-CALCANEUS-POSTERIOR-MIDDLE`; 뼈 `HA-S-CALCANEUS`.
- T05 근거 문장: The soleus aponeurosis joins the gastrocnemius tendon to form the calcaneal tendon, whose insertion is at the middle posterior calcaneus.
- claim `HA-C-T05-SOLEUS-CALCANEUS-INSERTION`; evidence `EV-GRAY1918-SOLEUS`, `EV-GRAY1918-CALCANEAL-TENDON`.
- 표면 후보: `HA-MESH-BP3D4-FJ3360` 뼈 전체 검색 컨텍스트만. 삼각형 ID/범위는 없음.
- 검토 기록: 정면 [ ] 후면 [ ] 우측 측면 [ ] 자유 회전 [ ] 범위/다른 출처 [ ] 사람 검토 [ ].

### 14. HA-A-T05-TA-TIBIA-CONDYLE-ORIGIN

- 근육/근두: `HA-M-000003`; 우측 instance `HA-I-R-HA-M-000003`; 부착 `origin`.
- 대상: `HA-S-TIBIA-LATERAL-CONDYLE`; 뼈 `HA-S-TIBIA`.
- T05 근거 문장: The source places an origin on the lateral condyle of the tibia.
- claim `HA-C-T05-TA-TIBIA-CONDYLE-ORIGIN`; evidence `EV-GRAY1918-TIBIALIS-ANTERIOR`.
- 표면 후보: `HA-MESH-BP3D4-FJ3387` 뼈 전체 검색 컨텍스트만. 삼각형 ID/범위는 없음.
- 검토 기록: 정면 [ ] 후면 [ ] 우측 측면 [ ] 자유 회전 [ ] 범위/다른 출처 [ ] 사람 검토 [ ].

### 15. HA-A-T05-TA-TIBIA-SURFACE-ORIGIN

- 근육/근두: `HA-M-000003`; 우측 instance `HA-I-R-HA-M-000003`; 부착 `origin`.
- 대상: `HA-S-TIBIA-UPPER-LATERAL-SURFACE`; 뼈 `HA-S-TIBIA`.
- T05 근거 문장: The source places an origin on the upper half or two-thirds of the lateral surface of the tibial body.
- claim `HA-C-T05-TA-TIBIA-SURFACE-ORIGIN`; evidence `EV-GRAY1918-TIBIALIS-ANTERIOR`.
- 표면 후보: `HA-MESH-BP3D4-FJ3387` 뼈 전체 검색 컨텍스트만. 삼각형 ID/범위는 없음.
- 검토 기록: 정면 [ ] 후면 [ ] 우측 측면 [ ] 자유 회전 [ ] 범위/다른 출처 [ ] 사람 검토 [ ].

### 16. HA-A-T05-TA-IOM-ORIGIN

- 근육/근두: `HA-M-000003`; 우측 instance `HA-I-R-HA-M-000003`; 부착 `origin`.
- 대상: `HA-S-INTEROSSEOUS-MEMBRANE-LEG`; 뼈 `mesh 미확보`.
- T05 근거 문장: The source also describes an origin from the adjoining part of the leg interosseous membrane.
- claim `HA-C-T05-TA-IOM-ORIGIN`; evidence `EV-GRAY1918-TIBIALIS-ANTERIOR`.
- 표면 후보: 없음. 해당 대상 mesh 미확보로 보류.
- 검토 기록: 정면 [ ] 후면 [ ] 우측 측면 [ ] 자유 회전 [ ] 범위/다른 출처 [ ] 사람 검토 [ ].

### 17. HA-A-T05-TA-FASCIA-ORIGIN

- 근육/근두: `HA-M-000003`; 우측 instance `HA-I-R-HA-M-000003`; 부착 `origin`.
- 대상: `HA-S-CRURAL-FASCIA`; 뼈 `mesh 미확보`.
- T05 근거 문장: The source describes fibers arising from the deep surface of the leg fascia.
- claim `HA-C-T05-TA-FASCIA-ORIGIN`; evidence `EV-GRAY1918-TIBIALIS-ANTERIOR`.
- 표면 후보: 없음. 해당 대상 mesh 미확보로 보류.
- 검토 기록: 정면 [ ] 후면 [ ] 우측 측면 [ ] 자유 회전 [ ] 범위/다른 출처 [ ] 사람 검토 [ ].

### 18. HA-A-T05-TA-SEPTUM-ORIGIN

- 근육/근두: `HA-M-000003`; 우측 instance `HA-I-R-HA-M-000003`; 부착 `origin`.
- 대상: `HA-S-TA-EDL-SEPTUM`; 뼈 `mesh 미확보`.
- T05 근거 문장: The source describes an origin from the intermuscular septum between tibialis anterior and extensor digitorum longus.
- claim `HA-C-T05-TA-SEPTUM-ORIGIN`; evidence `EV-GRAY1918-TIBIALIS-ANTERIOR`.
- 표면 후보: 없음. 해당 대상 mesh 미확보로 보류.
- 검토 기록: 정면 [ ] 후면 [ ] 우측 측면 [ ] 자유 회전 [ ] 범위/다른 출처 [ ] 사람 검토 [ ].

### 19. HA-A-T05-TA-CUNEIFORM-INSERTION

- 근육/근두: `HA-M-000003`; 우측 instance `HA-I-R-HA-M-000003`; 부착 `insertion`.
- 대상: `HA-S-MEDIAL-CUNEIFORM-INFEROMEDIAL-SURFACE`; 뼈 `HA-S-MEDIAL-CUNEIFORM`.
- T05 근거 문장: The tendon is inserted into the medial and under surface of the first cuneiform.
- claim `HA-C-T05-TA-CUNEIFORM-INSERTION`; evidence `EV-GRAY1918-TIBIALIS-ANTERIOR`.
- 표면 후보: `HA-MESH-BP3D4-FJ3377` 뼈 전체 검색 컨텍스트만. 삼각형 ID/범위는 없음.
- 검토 기록: 정면 [ ] 후면 [ ] 우측 측면 [ ] 자유 회전 [ ] 범위/다른 출처 [ ] 사람 검토 [ ].

### 20. HA-A-T05-TA-MT1-INSERTION

- 근육/근두: `HA-M-000003`; 우측 instance `HA-I-R-HA-M-000003`; 부착 `insertion`.
- 대상: `HA-S-BASE-METATARSAL-1`; 뼈 `HA-S-METATARSAL-1`.
- T05 근거 문장: The tendon is inserted into the base of the first metatarsal bone.
- claim `HA-C-T05-TA-MT1-INSERTION`; evidence `EV-GRAY1918-TIBIALIS-ANTERIOR`.
- 표면 후보: `HA-MESH-BP3D4-FJ3351` 뼈 전체 검색 컨텍스트만. 삼각형 ID/범위는 없음.
- 검토 기록: 정면 [ ] 후면 [ ] 우측 측면 [ ] 자유 회전 [ ] 범위/다른 출처 [ ] 사람 검토 [ ].

### 21. HA-A-T05-TP-IOM-ORIGIN

- 근육/근두: `HA-M-000004`; 우측 instance `HA-I-R-HA-M-000004`; 부착 `origin`.
- 대상: `HA-S-INTEROSSEOUS-MEMBRANE-LEG`; 뼈 `mesh 미확보`.
- T05 근거 문장: The source describes an origin from nearly all of the posterior leg interosseous membrane, except its lowest part.
- claim `HA-C-T05-TP-IOM-ORIGIN`; evidence `EV-GRAY1918-TIBIALIS-POSTERIOR`.
- 표면 후보: 없음. 해당 대상 mesh 미확보로 보류.
- 검토 기록: 정면 [ ] 후면 [ ] 우측 측면 [ ] 자유 회전 [ ] 범위/다른 출처 [ ] 사람 검토 [ ].

### 22. HA-A-T05-TP-TIBIA-ORIGIN

- 근육/근두: `HA-M-000004`; 우측 instance `HA-I-R-HA-M-000004`; 부착 `origin`.
- 대상: `HA-S-TIBIA-POSTERIOR-LATERAL-TP-REGION`; 뼈 `HA-S-TIBIA`.
- T05 근거 문장: The source places fibers on the lateral portion of the posterior tibial surface, from the popliteal-line region to the junction of the middle and lower thirds.
- claim `HA-C-T05-TP-TIBIA-ORIGIN`; evidence `EV-GRAY1918-TIBIALIS-POSTERIOR`.
- 표면 후보: `HA-MESH-BP3D4-FJ3387` 뼈 전체 검색 컨텍스트만. 삼각형 ID/범위는 없음.
- 검토 기록: 정면 [ ] 후면 [ ] 우측 측면 [ ] 자유 회전 [ ] 범위/다른 출처 [ ] 사람 검토 [ ].

### 23. HA-A-T05-TP-FIBULA-ORIGIN

- 근육/근두: `HA-M-000004`; 우측 instance `HA-I-R-HA-M-000004`; 부착 `origin`.
- 대상: `HA-S-FIBULA-MEDIAL-UPPER-TWO-THIRDS`; 뼈 `HA-S-FIBULA`.
- T05 근거 문장: The source places fibers on the upper two-thirds of the medial fibular surface.
- claim `HA-C-T05-TP-FIBULA-ORIGIN`; evidence `EV-GRAY1918-TIBIALIS-POSTERIOR`.
- 표면 후보: `HA-MESH-BP3D4-FJ3366` 뼈 전체 검색 컨텍스트만. 삼각형 ID/범위는 없음.
- 검토 기록: 정면 [ ] 후면 [ ] 우측 측면 [ ] 자유 회전 [ ] 범위/다른 출처 [ ] 사람 검토 [ ].

### 24. HA-A-T05-TP-TRANSVERSE-FASCIA-ORIGIN

- 근육/근두: `HA-M-000004`; 우측 instance `HA-I-R-HA-M-000004`; 부착 `origin`.
- 대상: `HA-S-DEEP-TRANSVERSE-FASCIA-LEG`; 뼈 `mesh 미확보`.
- T05 근거 문장: The source notes some fibers from the deep transverse fascia of the leg.
- claim `HA-C-T05-TP-TRANSVERSE-FASCIA-ORIGIN`; evidence `EV-GRAY1918-TIBIALIS-POSTERIOR`.
- 표면 후보: 없음. 해당 대상 mesh 미확보로 보류.
- 검토 기록: 정면 [ ] 후면 [ ] 우측 측면 [ ] 자유 회전 [ ] 범위/다른 출처 [ ] 사람 검토 [ ].

### 25. HA-A-T05-TP-SEPTA-ORIGIN

- 근육/근두: `HA-M-000004`; 우측 instance `HA-I-R-HA-M-000004`; 부착 `origin`.
- 대상: `HA-S-TP-ADJACENT-INTERMUSCULAR-SEPTA`; 뼈 `mesh 미확보`.
- T05 근거 문장: The source notes some fibers from intermuscular septa separating the muscle from adjacent muscles.
- claim `HA-C-T05-TP-SEPTA-ORIGIN`; evidence `EV-GRAY1918-TIBIALIS-POSTERIOR`.
- 표면 후보: 없음. 해당 대상 mesh 미확보로 보류.
- 검토 기록: 정면 [ ] 후면 [ ] 우측 측면 [ ] 자유 회전 [ ] 범위/다른 출처 [ ] 사람 검토 [ ].

### 26. HA-A-T05-TP-NAVICULAR-INSERTION

- 근육/근두: `HA-M-000004`; 우측 instance `HA-I-R-HA-M-000004`; 부착 `insertion`.
- 대상: `HA-S-NAVICULAR-TUBEROSITY`; 뼈 `HA-S-NAVICULAR`.
- T05 근거 문장: The tendon inserts into the tuberosity of the navicular bone.
- claim `HA-C-T05-TP-NAVICULAR-INSERTION`; evidence `EV-GRAY1918-TIBIALIS-POSTERIOR`.
- 표면 후보: `HA-MESH-BP3D4-FJ3308` 뼈 전체 검색 컨텍스트만. 삼각형 ID/범위는 없음.
- 검토 기록: 정면 [ ] 후면 [ ] 우측 측면 [ ] 자유 회전 [ ] 범위/다른 출처 [ ] 사람 검토 [ ].

### 27. HA-A-T05-TP-SUSTENTACULUM-EXPANSION

- 근육/근두: `HA-M-000004`; 우측 instance `HA-I-R-HA-M-000004`; 부착 `other_attachment`.
- 대상: `HA-S-SUSTENTACULUM-TALI`; 뼈 `HA-S-CALCANEUS`.
- T05 근거 문장: A fibrous expansion passes backward to the sustentaculum tali of the calcaneus.
- claim `HA-C-T05-TP-SUSTENTACULUM-EXPANSION`; evidence `EV-GRAY1918-TIBIALIS-POSTERIOR`.
- 표면 후보: `HA-MESH-BP3D4-FJ3360` 뼈 전체 검색 컨텍스트만. 삼각형 ID/범위는 없음.
- 검토 기록: 정면 [ ] 후면 [ ] 우측 측면 [ ] 자유 회전 [ ] 범위/다른 출처 [ ] 사람 검토 [ ].

### 28. HA-A-T05-TP-CUNEIFORM-EXPANSION

- 근육/근두: `HA-M-000004`; 우측 instance `HA-I-R-HA-M-000004`; 부착 `other_attachment`.
- 대상: `HA-S-CUNEIFORM-BONES`; 뼈 `mesh 미확보`.
- T05 근거 문장: The source describes a forward and lateral fibrous expansion to the three cuneiform bones.
- claim `HA-C-T05-TP-CUNEIFORM-EXPANSION`; evidence `EV-GRAY1918-TIBIALIS-POSTERIOR`.
- 표면 후보: 없음. 해당 대상 mesh 미확보로 보류.
- 검토 기록: 정면 [ ] 후면 [ ] 우측 측면 [ ] 자유 회전 [ ] 범위/다른 출처 [ ] 사람 검토 [ ].

### 29. HA-A-T05-TP-CUBOID-EXPANSION

- 근육/근두: `HA-M-000004`; 우측 instance `HA-I-R-HA-M-000004`; 부착 `other_attachment`.
- 대상: `HA-S-CUBOID`; 뼈 `HA-S-CUBOID`.
- T05 근거 문장: The source describes a forward and lateral fibrous expansion to the cuboid.
- claim `HA-C-T05-TP-CUBOID-EXPANSION`; evidence `EV-GRAY1918-TIBIALIS-POSTERIOR`.
- 표면 후보: `HA-MESH-BP3D4-FJ3364` 뼈 전체 검색 컨텍스트만. 삼각형 ID/범위는 없음.
- 검토 기록: 정면 [ ] 후면 [ ] 우측 측면 [ ] 자유 회전 [ ] 범위/다른 출처 [ ] 사람 검토 [ ].

### 30. HA-A-T05-TP-MT2-EXPANSION

- 근육/근두: `HA-M-000004`; 우측 instance `HA-I-R-HA-M-000004`; 부착 `other_attachment`.
- 대상: `HA-S-BASE-METATARSAL-2`; 뼈 `canonical ID 미확정 · source FJ3353`.
- T05 근거 문장: The source describes a forward and lateral fibrous expansion to the base of the second metatarsal.
- claim `HA-C-T05-TP-MT2-EXPANSION`; evidence `EV-GRAY1918-TIBIALIS-POSTERIOR`.
- 표면 후보: `HA-MESH-BP3D4-FJ3353` 뼈 전체 검색 컨텍스트만. 삼각형 ID/범위는 없음.
- 검토 기록: 정면 [ ] 후면 [ ] 우측 측면 [ ] 자유 회전 [ ] 범위/다른 출처 [ ] 사람 검토 [ ].

### 31. HA-A-T05-TP-MT3-EXPANSION

- 근육/근두: `HA-M-000004`; 우측 instance `HA-I-R-HA-M-000004`; 부착 `other_attachment`.
- 대상: `HA-S-BASE-METATARSAL-3`; 뼈 `canonical ID 미확정 · source FJ3355`.
- T05 근거 문장: The source describes a forward and lateral fibrous expansion to the base of the third metatarsal.
- claim `HA-C-T05-TP-MT3-EXPANSION`; evidence `EV-GRAY1918-TIBIALIS-POSTERIOR`.
- 표면 후보: `HA-MESH-BP3D4-FJ3355` 뼈 전체 검색 컨텍스트만. 삼각형 ID/범위는 없음.
- 검토 기록: 정면 [ ] 후면 [ ] 우측 측면 [ ] 자유 회전 [ ] 범위/다른 출처 [ ] 사람 검토 [ ].

### 32. HA-A-T05-TP-MT4-EXPANSION

- 근육/근두: `HA-M-000004`; 우측 instance `HA-I-R-HA-M-000004`; 부착 `other_attachment`.
- 대상: `HA-S-BASE-METATARSAL-4`; 뼈 `canonical ID 미확정 · source FJ3357`.
- T05 근거 문장: The source describes a forward and lateral fibrous expansion to the base of the fourth metatarsal.
- claim `HA-C-T05-TP-MT4-EXPANSION`; evidence `EV-GRAY1918-TIBIALIS-POSTERIOR`.
- 표면 후보: `HA-MESH-BP3D4-FJ3357` 뼈 전체 검색 컨텍스트만. 삼각형 ID/범위는 없음.
- 검토 기록: 정면 [ ] 후면 [ ] 우측 측면 [ ] 자유 회전 [ ] 범위/다른 출처 [ ] 사람 검토 [ ].

### 33. HA-A-T05-FL-FIBULA-HEAD-ORIGIN

- 근육/근두: `HA-M-000005`; 우측 instance `HA-I-R-HA-M-000005`; 부착 `origin`.
- 대상: `HA-S-FIBULA-HEAD`; 뼈 `HA-S-FIBULA`.
- T05 근거 문장: The source describes an origin from the head of the fibula.
- claim `HA-C-T05-FL-FIBULA-HEAD-ORIGIN`; evidence `EV-GRAY1918-FIBULARIS-LONGUS`.
- 표면 후보: `HA-MESH-BP3D4-FJ3366` 뼈 전체 검색 컨텍스트만. 삼각형 ID/범위는 없음.
- 검토 기록: 정면 [ ] 후면 [ ] 우측 측면 [ ] 자유 회전 [ ] 범위/다른 출처 [ ] 사람 검토 [ ].

### 34. HA-A-T05-FL-FIBULA-LATERAL-UPPER-TWO-THIRDS-ORIGIN

- 근육/근두: `HA-M-000005`; 우측 instance `HA-I-R-HA-M-000005`; 부착 `origin`.
- 대상: `HA-S-FIBULA-LATERAL-UPPER-TWO-THIRDS`; 뼈 `HA-S-FIBULA`.
- T05 근거 문장: The source describes an origin from the upper two-thirds of the lateral surface of the fibular body.
- claim `HA-C-T05-FL-FIBULA-LATERAL-UPPER-TWO-THIRDS-ORIGIN`; evidence `EV-GRAY1918-FIBULARIS-LONGUS`.
- 표면 후보: `HA-MESH-BP3D4-FJ3366` 뼈 전체 검색 컨텍스트만. 삼각형 ID/범위는 없음.
- 검토 기록: 정면 [ ] 후면 [ ] 우측 측면 [ ] 자유 회전 [ ] 범위/다른 출처 [ ] 사람 검토 [ ].

### 35. HA-A-T05-FL-FASCIA-ORIGIN

- 근육/근두: `HA-M-000005`; 우측 instance `HA-I-R-HA-M-000005`; 부착 `origin`.
- 대상: `HA-S-CRURAL-FASCIA`; 뼈 `mesh 미확보`.
- T05 근거 문장: The source also describes an origin from the deep surface of the leg fascia.
- claim `HA-C-T05-FL-FASCIA-ORIGIN`; evidence `EV-GRAY1918-FIBULARIS-LONGUS`.
- 표면 후보: 없음. 해당 대상 mesh 미확보로 보류.
- 검토 기록: 정면 [ ] 후면 [ ] 우측 측면 [ ] 자유 회전 [ ] 범위/다른 출처 [ ] 사람 검토 [ ].

### 36. HA-A-T05-FL-SEPTA-ORIGIN

- 근육/근두: `HA-M-000005`; 우측 instance `HA-I-R-HA-M-000005`; 부착 `origin`.
- 대상: `HA-S-LATERAL-LEG-SEPTA`; 뼈 `mesh 미확보`.
- T05 근거 문장: The source also describes origins from the septa separating the lateral muscle from adjacent anterior and posterior muscles.
- claim `HA-C-T05-FL-SEPTA-ORIGIN`; evidence `EV-GRAY1918-FIBULARIS-LONGUS`.
- 표면 후보: 없음. 해당 대상 mesh 미확보로 보류.
- 검토 기록: 정면 [ ] 후면 [ ] 우측 측면 [ ] 자유 회전 [ ] 범위/다른 출처 [ ] 사람 검토 [ ].

### 37. HA-A-T05-FL-MT1-INSERTION

- 근육/근두: `HA-M-000005`; 우측 instance `HA-I-R-HA-M-000005`; 부착 `insertion`.
- 대상: `HA-S-BASE-METATARSAL-1`; 뼈 `HA-S-METATARSAL-1`.
- T05 근거 문장: The tendon inserts on the lateral side of the base of the first metatarsal.
- claim `HA-C-T05-FL-MT1-INSERTION`; evidence `EV-GRAY1918-FIBULARIS-LONGUS`.
- 표면 후보: `HA-MESH-BP3D4-FJ3351` 뼈 전체 검색 컨텍스트만. 삼각형 ID/범위는 없음.
- 검토 기록: 정면 [ ] 후면 [ ] 우측 측면 [ ] 자유 회전 [ ] 범위/다른 출처 [ ] 사람 검토 [ ].

### 38. HA-A-T05-FL-CUNEIFORM-INSERTION

- 근육/근두: `HA-M-000005`; 우측 instance `HA-I-R-HA-M-000005`; 부착 `insertion`.
- 대상: `HA-S-MEDIAL-CUNEIFORM`; 뼈 `HA-S-MEDIAL-CUNEIFORM`.
- T05 근거 문장: The tendon inserts on the lateral side of the first cuneiform.
- claim `HA-C-T05-FL-CUNEIFORM-INSERTION`; evidence `EV-GRAY1918-FIBULARIS-LONGUS`.
- 표면 후보: `HA-MESH-BP3D4-FJ3377` 뼈 전체 검색 컨텍스트만. 삼각형 ID/범위는 없음.
- 검토 기록: 정면 [ ] 후면 [ ] 우측 측면 [ ] 자유 회전 [ ] 범위/다른 출처 [ ] 사람 검토 [ ].

### 39. HA-A-T05-FB-FIBULA-LATERAL-LOWER-TWO-THIRDS-ORIGIN

- 근육/근두: `HA-M-000006`; 우측 instance `HA-I-R-HA-M-000006`; 부착 `origin`.
- 대상: `HA-S-FIBULA-LATERAL-LOWER-TWO-THIRDS`; 뼈 `HA-S-FIBULA`.
- T05 근거 문장: The source describes an origin from the lower two-thirds of the lateral surface of the fibular body.
- claim `HA-C-T05-FB-FIBULA-LATERAL-LOWER-TWO-THIRDS-ORIGIN`; evidence `EV-GRAY1918-FIBULARIS-BREVIS`.
- 표면 후보: `HA-MESH-BP3D4-FJ3366` 뼈 전체 검색 컨텍스트만. 삼각형 ID/범위는 없음.
- 검토 기록: 정면 [ ] 후면 [ ] 우측 측면 [ ] 자유 회전 [ ] 범위/다른 출처 [ ] 사람 검토 [ ].

### 40. HA-A-T05-FB-SEPTA-ORIGIN

- 근육/근두: `HA-M-000006`; 우측 instance `HA-I-R-HA-M-000006`; 부착 `origin`.
- 대상: `HA-S-LATERAL-LEG-SEPTA`; 뼈 `mesh 미확보`.
- T05 근거 문장: The source also describes origins from septa separating the muscle from adjacent anterior and posterior muscles.
- claim `HA-C-T05-FB-SEPTA-ORIGIN`; evidence `EV-GRAY1918-FIBULARIS-BREVIS`.
- 표면 후보: 없음. 해당 대상 mesh 미확보로 보류.
- 검토 기록: 정면 [ ] 후면 [ ] 우측 측면 [ ] 자유 회전 [ ] 범위/다른 출처 [ ] 사람 검토 [ ].

### 41. HA-A-T05-FB-MT5-INSERTION

- 근육/근두: `HA-M-000006`; 우측 instance `HA-I-R-HA-M-000006`; 부착 `insertion`.
- 대상: `HA-S-TUBEROSITY-BASE-METATARSAL-5`; 뼈 `HA-S-METATARSAL-5`.
- T05 근거 문장: The tendon inserts on the lateral side of the tuberosity at the base of the fifth metatarsal.
- claim `HA-C-T05-FB-MT5-INSERTION`; evidence `EV-GRAY1918-FIBULARIS-BREVIS`.
- 표면 후보: `HA-MESH-BP3D4-FJ3359` 뼈 전체 검색 컨텍스트만. 삼각형 ID/범위는 없음.
- 검토 기록: 정면 [ ] 후면 [ ] 우측 측면 [ ] 자유 회전 [ ] 범위/다른 출처 [ ] 사람 검토 [ ].
