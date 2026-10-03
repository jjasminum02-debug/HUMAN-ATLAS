# T66 unit03 이후 병렬 제작·단일 통합 계획

2026-10-03 · Luna Max · 계획/프롬프트 작성만 수행. 현재 앱·공통 코드·EXECUTION/작업 상태를 변경하거나 worker를 실행하지 않았다.

## 현재 결과 판정

unit01은 양측 어깨/팔꿈치4GLB의 exporter/frame/형상 및 등록을 마쳤지만 실제 learner 브라우저는Mac잠금으로blocked_by_environment다. unit02는양측고관절/무릎4GLB·178selector와대표9실제브라우저시나리오·회귀를통과했다. Patella가 source moving context로포함됐지만독립실측활주/정상ROM검증은아니다. 현재지원은교육용source 자세관찰이며전근육주작용시범완료가아니다.

현재motion-learning.json의subjectSourceKey를중복제거한집계는다음과같다. unit03의작업중출력은완료기준선에서제외했다.

| 기준 | 고유 근육source표면 | 근육source-action연결행 | 고유 뼈source | 뼈-family연결행 | 고유motionURI |
|---|---:|---:|---:|---:|---:|
| unit01전 | 75 | 75 | 120 | 199 | 7 |
| unit01후 | 75 | 79 | 120 | 199 | 11 |
| unit02후 | **81** | **129** | **122** | **327** | **15** |

129를고유표면수로기록한현재report/EXECUTION필드는연결행수와혼동됐다. 이계획에서는현재원장을고치지않고CURRENT-REVIEW.json에런타임hash/산출법을남겼다. 00/최종writer가소유기록을정정한다. unit03의추가12GLB/492selector는현재등록receipt가있지만최종실제UI/전체범위합격은아직확인하지않았다. 최신최종보고가작성되면그결과가우선한다.

unit02 verification-commands.json에기록된최종9검사의합계는8.137초다. 여기에는작성/solver/브라우저/전체task시간이포함되지않는다. 반복최종검사가3시간의원인이라고단정할수없다. 공통작성과geometry/contact보정·출처/작용연결·브라우저환경을각각profile해야한다.

기술성과는실제GLB·음의scale보존·같은scene재생·typed뼈선택·복원이다. 학습완성도는별개다. 기존mainFunction시범1개를유지한채passive동작만늘리는것으로사용자의전체근육작용학습목표를충족할수없다. 현재자료가허용하는정성적작용시범을근거·source·방향·실제표면·카드에연결한다. 근활성/힘/실측수축량을계산해야교육용학습이가능하다는불필요한gate는추가하지않는다. 수동관찰을근거없이주작용으로승격하지않는다.

## 순서와 실행 대화

00을현재unit03진행중인대화에추가한다. 01은같은공통writer대화에서실행한다. unit03이공통파일을아직수정하는동안공통exporter/runtime쓰기를겹치지않는다. unit03의미해결content/독립예외는그대로남기되공통checkpoint를확정한다.

01이실제wave1manifest/snapshot/harness를만들고worker-ready라고기록하면02(A)·03(B)·04(C)·05(F)를서로다른대화에동시에입력한다. A/B/C는geometry3명,F는text1명이다. worker는자기output만작성하며manifest를추정하지않는다. manifest없는worker를먼저실행해서다시준비중단을반복하지않는다.

A/B/C/F의handoff가모이면06을기존writer대화에입력한다. 여기에서wave1실제등록과UI확인및wave2snapshot을완성한다. wave2-ready이후07(D)·08(E)를별도대화에서동시에실행한다. 두결과가모이면09를기존writer에입력해전체작용/뼈/신경연결과T66최종판정을한다. 실제T66합격후10(T85),실제T85합격후11(T40)을순서대로입력한다. 자동다음실행/새task번호가없다.

| 파일번호 | 책임 | 순서/묶음 | 독립프롬프트 |
|---|---|---|---|
| 00 | 진행 중 unit3 마무리·병렬 인계 | serial-0 | [00-unit03-finish-and-handoff.txt](00-unit03-finish-and-handoff.txt) |
| 01 | 공통 작성 경로 최적화·wave1 고정 입력 | serial-1 | [01-writer-freeze-and-optimize.txt](01-writer-freeze-and-optimize.txt) |
| 02 | 손·손가락 제작 | wave-1 | [02-worker-A-hand.txt](02-worker-A-hand.txt) |
| 03 | 하지·발 제작 | wave-1 | [03-worker-B-leg-foot.txt](03-worker-B-leg-foot.txt) |
| 04 | 척추·갈비뼈·호흡 제작 | wave-1 | [04-worker-C-spine-ribs.txt](04-worker-C-spine-ribs.txt) |
| 05 | 전수 신경 주행·포착 설명 | wave-1 | [05-worker-F-nerve-text.txt](05-worker-F-nerve-text.txt) |
| 06 | wave1 통합·wave2 준비 | serial-2 | [06-writer-integrate-wave1-and-freeze-wave2.txt](06-writer-integrate-wave1-and-freeze-wave2.txt) |
| 07 | 턱·목뿔·후두·인두 제작 | wave-2 | [07-worker-D-jaw-hyoid-pharynx.txt](07-worker-D-jaw-hyoid-pharynx.txt) |
| 08 | 눈·얼굴·혀·골반바닥 제작 | wave-2 | [08-worker-E-eye-face-tongue-pelvic.txt](08-worker-E-eye-face-tongue-pelvic.txt) |
| 09 | 최종 자산·작용·뼈·신경 통합과 T66 판정 | serial-3 | [09-writer-final-action-integration-and-close.txt](09-writer-final-action-integration-and-close.txt) |
| 10 | UI·실측 성능 완성 | serial-4 | [10-T85-ui-performance.txt](10-T85-ui-performance.txt) |
| 11 | 로컬 실행·전달 | serial-5 | [11-T40-local-delivery.txt](11-T40-local-delivery.txt) |

기존serial04~11은이새분업으로대체한다. 과거파일/완료unit01/02/진행중unit03은보존한다. A/B/C가각각기존04/05/06, D/E가기존07/08, F가기존10을담당한다. 기존09/11의전수작용·뼈선택/최종통합은새09가수행한다. 병리editor는이후별도사용자요청전에는시작하지않는다.

## 병렬에서 공유해도 되는 것과 쓰기 경계

읽기는fixed source/cache,metadata/근거/frozen exporter/QC를공유한다. 실제output은wave/runId/worker별로분리한다. 작업키에family/side/action/sourceKey/part를넣어다관절source의정당한중복과이중배정을구분한다. 새로운family는localnamespace데이터/authoring함수로작성한다. 공통코드개선은patchproposal로인계한다.

공통renderer/controller/runtime/axis기준/scene등록/EXECUTION/검증된제품상태/Gitindex는writer만쓴다. worker가각각commonGLB출력·registry·build/dist·report를덮지않는다. 각worker가전체빌드/타입/12부위PNG를반복하지않고자기실제GLB/QC/hash/meaning을전수검사한다. 최종등록후writer가영향UI와관련회귀를묶어서검사한다.

초기geometry각1process·BLAS1thread로시작해CPU/메모리와처리시간을관찰한다. 모든worker가모든코어를동시에사용하면병렬이느려질수있다. wall time단축은측정후보고하며2배/3배개선을미리보장하지않는다.

## 반복을 줄이는 운영 규칙

통과bytes/입력/sourceframe/weights/pose/validator hash기준QC를재사용한다. 실패부근만적응형세분하고일반자산에unit01초고밀도키설정을복사하지않는다. 한실패에구별되는engineering가설3개후정체면재현case/최근실패를남기고다른작업키를진행한다. 공통writer가예외를유형별로묶어한번수정한다. 실패를pass/contentgap으로바꾸는규칙은아니다.

60분단위의짧은중간handoff로작업량·실패·실제시간을보이게한다. 최종완료전부터실제GLB/QC를저장해컨텍스트교체/재시작후재조사를줄인다. 보고서/전수해시/동일문헌검색의무의미한반복을피한다. 원본권리·source-only·humanReview·전체분모는그대로보존한다.

## 완료 기준

worker는candidate_validated이며앱pass가아니다. 전체배정큐에서제작가능한항목은실제GLB/입력/QC를제출해야한다. F는실제검증된문헌field/card delta가책임이며없는GLB를생성하지않는다. engineering예외·실제자료부족·미연결은별도다.

09에서현재자료의가능한제작/연결책임과지원제품차단결함을해결했을때T66completed/passed를기록한다. contentCompleteness및전체근육/뼈/신경목표는남은수에따라partial일수있다. 미완engineering이나unit01시각gap을삭제한채pass하지않는다. T85는지원앱의실제UI/성능,T40은재현가능한로컬전달이다.

실행manifest는이계획작성에서만들지않았다. unit03공통작성종료후01writer가정확한현재입력을직접동결하고만드는필수구현이다. prompt-plan.json은계획목록이며실제worker배정manifest가아니다.
