# 이름·신경·카드 개선 통합 04 — 결과

**판정:** 이번 02/03 검토안과 해당 지원 UI 흐름의 통합은 `passed_with_content_gaps`다. 이는 검토 범위에 대한 로컬 앱 준비 판정이며, 전체 해부학·전신 coverage·사람 승인·공개 재배포 승인이 아니다.

## 반영

- 신경 검토의 N02-P01~P04를 적용했다. 온종아리신경 주행 설명을 현재 모형에서 연결된 깊은·얕은종아리신경 분지로 맞추고, 카드 제목을 **“모형에서 연결된 분지”**로 한정했다. 관계를 연결하지 않은 신경에서 정확히 반복되는 일반 기능 템플릿만 숨겼다. 상태·특정 설명·관계 목록은 남는다.
- N02-P04의 시체해부 결과는 연구 표본에서 네 번째 가슴사이신경이 30개 중 4개 대흉근 표본의 아래가쪽 공급에 참여했다는 문맥으로만 표시한다. 좌우·근육 부분·가지 표면·좌표 관계는 만들지 않았다.
- N02-P05의 네 분지 후보는 TAH 명명 자료만으로 관계를 추가하지 않았다. N02-P06도 문헌 설명만 유지하고 운동관계로 등록하지 않았다. 기존 18개 관계는 그대로다.
- 이름 검토에서 제안한 검색 alias 8개를 exact source key의 add-only delta로 적용했다. 손쪽 엄지 근육 6개에는 손 구분 alias를, 협근 2개에는 `Buccinator muscle` 검색 alias를 추가했다. 이름, 영문 원문, 좌우, 학습 연결, target route, geometry는 바뀌지 않았다. `Bucinator` 표기도 그대로 유지했다.
- 브라우저 통합 중 신경 카드의 텍스트 설명과 실제 재생 후보가 모두 “이 근육의 움직임 보기”로 표시되는 혼동을 고쳤다. 재생 가능한 후보만 “움직임 보기”, 글 설명 전용은 “작용 설명 보기”라고 안내하며, 두 경로 모두 작용 탭으로 이동하고 자동재생은 하지 않는다.
- 추가 요청에 따라 마우스 포인터가 부위 선택기로 들어오면 클릭 없이 전신과 12부위 메뉴가 아래로 열린다. 220ms 아래 방향 fade/slide를 적용하고, 포인터가 벗어나면 닫는다. 키보드 포커스가 메뉴 안에 남아 있으면 닫지 않는다. 키보드 활성화, Escape, 터치/클릭 대체, reduced-motion도 유지한다.

## 실제 브라우저 확인

새 로컬 snapshot `local-20261006101936364-bf4218bb`를 만들고 5183에서 실제 Chrome으로 확인했다. hover만으로 13개 선택 항목이 열리고, 포인터를 벗어나면 닫혔다. Space/Escape와 포커스 복귀도 확인했다. 390 CSS viewport에서는 검색 중에도 선택기가 보였고 메뉴가 화면 안에 머물렀다.

손쪽 단무지신근 검색은 한 그룹만 반환했고, 카드에서 현대 한국어명·한자어명(한글)·영문명과 오른쪽 선택을 확인했다. `Buccinator muscle`도 한 그룹으로 찾아졌으며 카드의 `볼근 / 협근 / Bucinator`가 유지됐다. 깊은종아리신경에서 오른쪽 앞정강근의 실제 관계를 따라가면 정확한 오른쪽 발목 등쪽굽힘 작용이 선택된 기능 탭이 열렸다. CTA를 눌러 반복 시범을 시작하고 재클릭해 rest로 돌아오는 것을 확인했다.

전신 구조 453개 목록을 끝까지 스크롤한 뒤 목으로 전환했다. 실제 viewport는 390×844, 1024×768, 1440×900 CSS 픽셀로 기록했다. 이는 실기기 시험이 아니다. 브라우저 HTTP 200, console/page error 0, failed request 0이었다. 저장한 PNG는 `screenshots/`에 있다.

## 검증 및 로컬 전달

- TypeScript typecheck 통과
- 통합 데이터 테스트 36/36 통과
- whole-body 및 dataset 관련 테스트 83/83 통과, 컴파일된 데이터 chunk 46개 검증
- learner card/motion runtime freshness 검사 통과
- `local:prepare` 및 99개 파일 `local:verify` 통과
- 새 snapshot manifest SHA256: `86caa000ea5cf977c8f58140b946ab5e35f5928ead2dd03b23f35d7a2ac879bf`
- 로컬 확인 주소: <http://127.0.0.1:5183/>

빌드에서 앱 JavaScript chunk가 약 3.65 MB로 500 KB 안내 기준보다 크다는 기존 경고가 있었지만, 빌드와 실제 페이지 확인은 통과했다. 5175 사용자 서버와 고정 5180 전달 snapshot을 바꾸지 않았다. 공개 배포를 하지 않았다.

## 남은 콘텐츠와 보존

신경 195 source 표면·98 native label group은 독립 신경 수가 아니다. 독립 신경 개념 총수는 미확정이며, 기존 18개 운동근 관계는 전체 지배망이 아니다. 관계 미확정 분지 후보, 오른쪽이 없는 발바닥 가지 표본, 애매한 `extensor digitorum pedis` 명칭, 98개 포착 설명의 field-level 근거 부족은 그대로 남겼다.

근육 이름 472 source 행(462 learner/10 inspection)과 429 target 행은 별도 분모다. alias 추가는 직접 용어 근거나 사람 검토가 아니다. target 전용 한국어 용어 locator가 없는 항목, inspection의 traditional name null, 한자 글자 미수집도 유지했다. 기존 상·하부 승모근 교정은 재사용했고 source 충돌 원문은 고치지 않았다.

542 target/563 membership/12 region, 기존 HA 130 연결, 역사 분류 163(6/20/135/2), source-only, 공개 권리 `held`, `humanReview=not_performed`, 원본·OpenSim_Models·T13·기존 WIP를 바꾸지 않았다. `EXECUTION`, product acceptance, NEXT, T40/T66/T85 task 상태와 과거 report를 수정하지 않았다.

세부 hash, 브라우저 계측과 모든 known gaps는 `final-validation.json`, `applied-corrections.json`, `known-content-gaps.json`, `unresolved-product-blockers.json`에 있다.
