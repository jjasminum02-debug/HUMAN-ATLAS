# 현재 Luna 완료 후 다음 프롬프트

```text
HUMAN ATLAS에서 AT10의 skin-fit만 수행해라. 담당 Sol xhigh.
AGENTS.md, 최신 work/EXECUTION.json, work/tasks/AT10.md,
work/plans/acupoint-surface-posture-2026-10-13/REVIEW-AND-DESIGN.md와 PROMPTS-IN-ORDER.md,
지정 선행 실제 report/evidence 및 현재 package를 읽어라.
현재 Luna portfolio-content가 끝난 결과를 기준선으로 사용한다. 그 결과는 다시 만들지 마라.
execution-amendment.json의 r2 계획 변경은 이미 적용됐다. 최신 EXECUTION과 대조하고 기존 result/acceptance와 Luna 산출물을 보존한다.
AT30/31은 planned로만 등록하고 실행하지 않는다. AT10의 다음 단위는 skin-fit → skin-runtime → existing-package-reconciliation이다.

피부 주 입력은 이미 확보한 MakeHuman core다. skin-source-review/selection.json의 pinned SHA·파일 hash·권리를 확인하고
atlas-data/source-cache/datasets/skin-source-review-2026-10-13/base.obj와 공식 target/license를 재사용해라.
기존 ZA 골격·근육은 고정하고 피부만 체형·rest pose·얼굴·손·발까지 전신 정합해라.
단순 전신 scale/shrinkwrap 또는 몸통 일부 샘플로 끝내지 마라. source body와 helper를 구분하고 기존 vertex/face 대응을 남겨라.
공식 dm→m와 현재 source/derived frame을 구분해 scale·world transform을 중복 적용하지 마라.
현재 제공된 단일 target 미리보기는 생산용 캐릭터 레시피가 아니다. 기존 ZA에 맞춘 성인 체형·자세의 결정적 제작 recipe를 확정해라.
생성기/Blender runtime을 웹 bundle에 넣지 마라. 검증된 Blender 경로와 --factory-startup --disable-autoexec를 사용해라.

얼굴/귀·목·어깨/겨드랑·팔꿈치·손목/손바닥/손가락·흉복부/배꼽·등/천골·샅·무릎·발목/발바닥/발가락을 실제 비교해라.
필요한 교육용 landmark registry를 작성하고 원본 지표·작성 지표를 구분해라. 구강/잇몸은 외피 대신 기존 점막 구조 연결을 준비한다.
정합 피부 GLB, source-to-derived mapping, 지표 manifest, 재현 도구, 부위별 관통/간격 검사와 실제 전신/근접 시각 evidence를 남겨라.
skin-source-review의 MakeHuman 원본 후보와 이미 조사한 ZA Skin/Dermis를 다시 찾는 단계만 반복하지 마라.
후보가 부적합한 정확한 부위만 보완하며 실패한 국소 정합을 전신 입력 부재로 바꾸지 마라.
이번에는 361점 authoring·취혈자세·UI 개편을 하지 않는다. 다음은 AT10/skin-runtime이다.
원본/OpenSim_Models/T13/사용자 WIP와 역사 evidence를 보존해라. 담당 범위만 수행하고 다음 task는 자동 실행하지 마라.
관련 자동 검사와 실제 화면 검증을 남겨라. 이름 등록/실제 표시/위치 등급/자세 지원을 구분하고 문서만으로 완료 처리하지 마라.
최신 EXECUTION을 다시 읽어 담당 결과만 병합하고 sync_execution.py 및 --check 후 소유 변경만 로컬 커밋해라.
해시·포함/제외·잔여 변경·다음 ID와 이 문서의 다음 프롬프트를 남겨라. push·배포·진단·치료·침 시뮬레이션은 하지 마라.
```
