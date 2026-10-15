# AT10 / V1 — 재질 시제품 구현, 외관 미달

상태: **partial_visual_quality_rejected**. 재질 패키지와 로더는 구현·검증했지만 사용자가 작업 중 전신 외관을 반려했다. V1이나 전신 피부를 외관 합격으로 처리하지 않는다. 부모 AT10은 partial 그대로다. 다음 독립 실행 단위는 **F3**이며 이번에는 실행하지 않았다.

## 실제 변화

F2 f2c3의 position/index/normal/UV를 그대로 두고 실제 MakeHuman 피부 색상 텍스처와 파생 미세 normal/지역 roughness를 적용했다. 선택 source는 공식 CC0 pack의 `skins/young_asian_male/young_lightskinned_male_diffuse3.png`; source SHA `f50016a5507fc687dc8df06599c8ea48de950cd185de33a71cafc1319ddab4d5`. MHMAT의 명시적 CC0 선언을 함께 보존했다. 비교 취득한 caucasian2는 MHMAT name이 old_caucasian_male_detailed로 디렉터리명과 달라 선택하지 않았다.

산출물은 `atlas-data/anatomy/skin/at10-appearance-v1/material.json` 및 세 WebP다. color 2048² 107700 B, normal 512² 62534 B, roughness 1024² 16942 B. 합계 **187176 B**. GPU RGBA8+mip 보수 계산 **29360124 B (약28MiB)**. color는 sRGB, 보조 맵은 linear. original OBJ UV의 V-up 방향이므로 ImageBitmap decode 시 flipY를 수행한다. normal은 사진의 약한 high-pass 미세 음영 파생이며 측정된 표면 높이나 혈위 지표가 아니다. roughness는 실제 UV triangle에 발/손/얼굴 영역을 구분해 작성했으며 손발톱 색상은 원본 텍스처다. 개별 손발톱 재질 마스크는 V2 잔여다.

원래 검증된 GLB embedded/static geometry 제약은 그대로다. 별도 material manifest로 geometry SHA, UV SHA, map SHA/bytes/dimensions/colorSpace/mip costs를 검사한다. 잘못된 해시/UV/크기면 로드하지 않는다. off/cancel/failure/dispose 시 소유 texture와 ImageBitmap을 해제한다. 추가 renderer/RAF/조명/카메라/레이아웃은 없다. 부위 탐색이 URL의 개발 query를 지우더라도 처음 선택한 후보/외관 옵션을 세션에서 유지하도록 수정했다.

외관 반려 후 새 재질은 `skinReview=1&skinCandidate=f2c3&skinAppearance=v1` 명시적 DEV 시제품에서만 사용한다. 기본 피부/제품 재질로 승격하지 않는다. 비교 중 촬영한 after URL은 당시 V1 기본 개발 설정이며, 최종에서는 같은 결과를 `skinAppearance=v1`로 연다.

## 실제 앱 QA

증거: `work/evidence/AT10/2026-10-15-v1-appearance/`.

- 1280×720, 같은 앱/기존 조명/같은 기준 카메라. `before/after-runtime.json`의 발 카메라 좌표가 정확히 같다. 발 정면과 ArrowDown 8회 발바닥 전후 캡처. 손바닥/손등 상반신 캡처와 손가락 신경의 기존 선택 맞춤을 이용한 근접 캡처. 얼굴 정면 참고 전후 캡처.
- 실제 로더에서 F2 SHA `07ab569e3a3a3453ed825e9bc583869394e5e94babdee7edec6b6c437836586f`, textures 3, skin geometry625080 B/26756tri, material 포함 encoded813752 B 확인. 발 관찰의 로드 소요 약102.7ms 한 표본(기준 단색 약6.8ms), 네트워크/디코드 포함 warm local 관찰값이며 성능 보증이나 FPS 벤치마크가 아니다.
- baseline overview20042516 B + skin/material813752 B =20856268 B. 기존20MiB 예산 이내(여유115252 B). 현재 skin GPU+geometry29985204 B. 예산은 올리지 않았다. 기존108 overlay813096 B와의 결합은 여전히 초과하며 기존 budget gate로 거절한다. R1/R2 별도 해결 대상이다.
- 반복 ON/OFF에서 같은 root/camera 유지, textures 3→0, 피부 OFF 시 기존 뼈/근육/신경 표시. 피부는 picking을 가로채지 않는다. 근접 신경 화면의 일부 황색 선이 피부 위로 보이는 기존 신경 presentation 동작은 확인했고 새 피부 접촉 승인으로 간주하지 않았다.
- 재질 파일이 없는 production 빌드에도 DEV-only appearance asset이 섞이지 않았는지 출력 확인.

## 통과한 기술 검사

- 실제 파일 hash/UV source correspondence 14517/14517. UV seam source vertex군의 shading normal 차이 최대0. position/index/UV/normal 변경0.
- source generator 재실행 결과 map/manifest hash 동일. F1/F2 변환/정합 solver 재실행 없음.
- skin runtime + 새 material 테스트 **13/13**: tamper/UV/colorSpace/dimensions, mip 예산, 취소 중 partial bitmap 해제, 전체 SkinLayer 반복 진입/해제와 기존 회귀.
- TypeScript 및 production Vite build 통과. 기존 >500kB chunk warning 유지, 이번 범위에서 전역 bundle 재설계 없음.

## 외관 실패와 다음 수정

사용자 반려 화면과 인터넷 공식 이미지 비교는 `VISUAL-DIRECTION.md`, 원형과 현재 vertex cohort 범위 비교는 `shape-audit.json`이다. source shape를 보존하는 검사가 부족한 전신 변형과 눈/입 구성 문제가 주원인이다. shape-audit 값은 임상 표준 치수나 목표 비율이 아니다.

- 얼굴/목/어깨: 전신과 얼굴 근접 모두 부자연스러운 윤곽. F3에서 source 얼굴 feature와 ZA 대응, 눈꺼풀/안구 노출/입/귀 및 목 연결을 실제 수정한다.
- 몸통: 늘어진 인상과 어깨·겨드랑·골반 연결의 부풀음. F4에서 source shape와 native frame을 함께 보며 교정한다.
- 손발: 각진 실루엣, 일부 손가락 굴곡/UV 늘어짐, 발바닥 낮은 조도, 원본 사진의 고정 음영/털과 얼룩. V2에서 최종 geometry 위에 질감·손발톱·조명 응답을 정리한다. 원형을 보존하면서 새 revision과 국소 정합 회귀가 필요하다.
- 사용자 만족, 전신 geometry/정확한 혈위/제품 피부/공개 재배포 승인 없음. registeredSkin=null 유지. 전체 피부 미완은 V1 개발 미리보기나 다음 F3의 차단 사유가 아니다.

사용자 최신 요청에 따라 기존 F3/F4/V2 프롬프트에 실제 참고 이미지·큰 형태 보존·중립 재질/전신 시각 검수를 추가했다. 새 task 번호는 추가하지 않았다. 사진 텍스처를 붙였거나 관통0이라는 이유로 다시 합격시키지 않는다.

## 보존과 Git

시작 HEAD `28ae430468c7cddd3e2e75902f19d4f11673e3bb`. 시작 tracked WIP는 baseline.json에 path/hash로 동결했다. F1/F2 원본, OpenSim_Models 및 기존 사용자 WIP를 유지한다. 이번 소유 코드/재질/도구/핵심 QA/보고서/실행 결과/개정 프롬프트만 로컬 커밋한다. 혼합 STATUS/NEXT 및 기존 WIP/원본 PNG source cache는 제외한다. 포함/제외 기준은 commit-scope.json에, 실제 commit hash와 잔여는 최종 응답에 남긴다. push/배포/F3 자동 실행 없음.
