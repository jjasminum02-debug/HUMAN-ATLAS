# 차단 항목

## T00

- 없음. 작업 기반을 만들고 원본 보존을 확인할 수 있었다.

## 후속 작업에 넘긴 자료 공백

- 근육별 해부학·용어·평가 근거, BodyParts3D 배포본과 자산별 이용 조건은 아직 확보·검증하지 않았다. T01에서 출처 후보와 확인 상태를 분리해 기록한다.
- 이 공백은 T00을 막지 않는다. 근거가 확보되기 전까지 학습 데이터로 추측 입력하지 않는다.

## T01

- T01 차단 항목 없음. 지정된 전신 부위와 분류/집계 정책, 출처 후보·판본·license·locator 확보 상태를 기록했고 machine-readable validation을 실행했다.
- 후속 단계 공백은 `work/review-queue/source-gaps.md`에 출처별로 세분화했다. 이 공백은 T01을 막지 않았으며 현재 T02를 자동으로 막는 것으로 판정하지 않았다.
- 다음 단계에서 실제 파일 접근이 실패하거나 해당 구조/권리를 확인할 수 없으면, 이유와 독립적으로 가능한 일을 T02 보고서에 기록한다. 파일 내용과 license를 확인하지 않은 상태에서 메시나 부착 데이터가 지원된다고 주장하지 않는다.

## T02

- T02 blocker 없음. archive source file과 현재 archive 사용 조건/귀속을 확인했고 소량 mesh, source ID, shape/좌표, viewer trial을 기록했다.
- 선택된 OBJ의 embedded comments에는 이전 CC BY-SA 2.1 Japan 문구가 남아 있다. 변형하지 않았고 current LSDB Archive notice와 요구 귀속을 manifest에 기록했다. 이번 task에서 외부 공개하지 않았다. 이후 공개 전에 archive 조건/필요 귀속을 다시 확인한다.
- 6 pilot의 해부학적 identity/shape, gastrocnemius head 관계, attachment 영역, joint pose는 사람 검토 대상이다. 다섯 연결 뼈 mesh는 교차표에서만 확인했다. 이는 T02 범위를 통과시키지 못하는 blocker로 분류하지 않고 다음 review gate에 보낸다.
- 다음 직렬 task T03은 schema/validator 작업이며 이 task에서 시작하지 않았다.

## T03

- T03 blocker 없음. 스키마/검증기와 1 positive + 16 negative synthetic fixtures의 지정된 검증 결과가 통과했다.
- 실제 reviewer 신원/서명은 JSON validator에서 확인할 수 없다. `reviewed`는 기록된 human-kind 결정, evidence, revision hash의 구조적 gate로만 취급하며 실제 사람 검토로 주장하지 않는다.
- fixture의 source/term/mesh/claim/coordinate/approval 값은 synthetic test data다. 실제 해부학 입력, 실제 메시의 승인, license 공개 권리 또는 임상 타당성을 뜻하지 않는다.
- T04 입력 전에 필요한 정확한 TA2/Korean terminology edition, 실제 항목 locator와 완전한 목록은 여전히 확보되지 않았다. 기존 `work/review-queue/source-gaps.md`를 이어받아 확보/결측 상태를 명시한다.
- 다음 직렬 task는 T04이며 이 task에서 시작하지 않았다.
