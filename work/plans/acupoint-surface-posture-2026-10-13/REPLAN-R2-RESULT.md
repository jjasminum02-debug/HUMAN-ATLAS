# 2026-10-13 r2 재설계 결과

## 판단

AT9 74개와 AT10 50개 instance가 실제 표시되지 않았다. 전신 피부/표면 주소/landmark가 없는 상태에서 경맥별 package부터 등록한 순서가 원인이다. 여기에 동적 취혈자세를 선행시킨 이전 계획은 사용자 목표에 맞지 않았다.

최신 순서는 **Luna 내용 대조 → Sol 피부 정합 → Sol 피부 버튼/같은 장면/접촉형 점 → Luna 기존 점 복구 → AT11–19 정지 361혈 → AT23–27 영역·내용 → AT30 자세 전수조사 → AT31 자세 구현 → AT28/29 최종 QA**다. AT31은 고정 네 범주의 유한한 묶음이며 이미 통과한 family를 재조사하지 않는다.

## 이번에 실제 수행한 일

- MakeHuman, MB-Lab의 실제 소스 파일·pinned revision·권리 문구를 확보하고 비교했다. 기존 ZA/BP3D 조사와 Open Anatomy Atlas 코드, Zygote 상용 외피 설명을 대조했다.
- MakeHuman core body를 주 입력으로 선정했다. body만 13,380 vertices / 26,756 triangles이며 source OBJ는 1,749,303 bytes다. 공식 core asset CC0와 생성기 코드 라이선스를 구분했다. source/target/license hash를 검증하고 원본은 ignored cache에 보관했다.
- MakeHuman 형태의 전/측/후 미리보기를 확인했다. MB-Lab은 현재 Blender 3.5에서 face 호환성이 없어 완전한 시각 품질 비교로 주장하지 않았다. Blender 통합 렌더 실패 후 MakeHuman의 실제 geometry를 CPU로 그린 비교용 이미지다. 제품 smoothing/material/ZA 정합 완료를 뜻하지 않는다.
- 현재 Luna는 작업 중 `738316ab5941ca1bb1a3148cba22bd0278f1dffb`로 종료됐다. 361 원문 추출 중 등록 116혈 비교/요약(정합82/대안22/보류10/충돌2), learner import0, pose0 결과를 보존했다.
- Luna 종료·idle 확인 후 EXECUTION에 미래 order/policy와 AT30/31 planned, AT10 다음 `skin-fit`, 별도 contentSupplement를 반영했다. 기존 AT9/10 result/acceptance는 변경하지 않았다. AT30/31은 실행하지 않았다.
- 기존 명세 AT10, 구 통합 프롬프트의 안내, 최신 설계·순서별 프롬프트와 다음 복사용 프롬프트를 수정했다. 진행 중 사용된 Luna 코드블록은 그대로 보존했다.

## 검증과 경계

`replan-r2-validation.json`: 계획·입력 검증 15개 통과. 116+245=361 배정 중복/누락 없음, 자세 단계가 AT19/27 뒤에 위치, source hash 확인, 기존 결과 보존, canonical/다음 프롬프트 일치. `sync_execution.py` 변경0, `--check` 통과. 소유 diff 공백 검사 통과.

이번 변경에는 앱 코드·실제 경혈 좌표·피부 장면 통합이 없다. 그러므로 앱 build/브라우저 합격 또는 AT10 완료라고 기록하지 않는다. runtime/private/source originals/OpenSim_Models/T13/사용자 WIP는 수정하지 않았다. 자료 private 원문, 내려받은 OBJ/BLEND/target/license cache와 실패 로그는 커밋 및 learner bundle에서 제외한다. 소스 URL/hash와 작은 검사/미리보기만 개발 문서에 남긴다.

## 다음

**AT10 / skin-fit — Sol xhigh.** [NEXT-AFTER-CONTENT.md](NEXT-AFTER-CONTENT.md)의 프롬프트를 그대로 사용한다. 전후 단계의 전체 프롬프트는 [PROMPTS-IN-ORDER.md](PROMPTS-IN-ORDER.md)다. 옛 evidence의 `surface-base → locating-posture` 안내는 역사 기록으로만 남긴다. 자동 다음 실행/push/배포 없음.
