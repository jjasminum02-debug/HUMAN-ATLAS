# 다음 작업: T78 · Astra · 현재 대화

T77 기술 통합은 통과했지만 시각 목표 gate는 partial이다. T78의 누락 포함 목표 목록/queue 설계는 독립 진행 가능하며, T80/T58 또는 animation gate의 합격을 뜻하지 않는다. 아래는 인계이며 자동 실행하지 않았다.

```text
HUMAN ATLAS에서 T78만 수행해라. 담당 Astra · 현재 대화 직접 구현.
AGENTS.md, 최신 STATUS/R15 registry, design/2026-09-25-muscle-atlas의 13/14/15/16 및 19/20, work/tasks/T78.md, T73–T77/T92/T93/T94의 실제 report/evidence/manifest와 work/evidence/T77/NEXT-T78.md를 읽어라. 먼저 시작 HEAD, 사용자 WIP와 실제 입력 hash를 기록해라.

T77 technical integration은 통과했지만 visual coverage는 partial, whole-body denominator는 null이다. 543개 source 표면은 근육 개수나 전신 완성 분모가 아니다. 531개 기본 표시, held hidden 12개, 기존 binding 10개이며 source-only·license·human-review hold는 유지됐다.

12부위의 모든 골격근과 맥락 뼈 target을 source tree 및 독립 해부학 목록과 대조하고 개별근/갈래/군/양측/중선/변이를 분리해 concept/source-element 분모를 동결해라. geometry/좌우/frame/region/binding/세 이름/기시정지/기능/animation 상태를 독립 기록해라. T77 current-inventory.json의 38개 substring query는 탐색 후보일 뿐 분모나 canonical identity가 아니다.

이두근·삼두근의 미통합 10개 exact source 후보와 다른 누락/미연결을 bounded task에 배정해라. 광배근도 사용자가 최종 구현 대상으로 명시했다. T94 no_exact_source_found를 이력으로 보존하되 광배근을 목표에서 삭제하거나 영구 누락으로 종료하지 마라. 메타데이터 재검색만 반복하지 말고, 필요하면 공식 aggregate 후보의 실제 객체 inventory를 격리된 도구로 제한 취득·검사하는 별도 task를 설계해라. exact object ID/path/hash, ancestry, 좌우/부분, unit/frame/rest pose와 개별 권리를 확인하는 gate, 다른 모델일 때 별도 registration gate, 마지막 단일 장면 통합/선택 검증을 각각 배정해라. aggregate 파일명·TA2ID·검색 snippet만으로 geometry/binding/T50 호환성을 승인하지 마라. 불명확한 경우 해당 항목은 missing/held로 유지해라.

T79 첫 batch 최대10개 개념과 나머지 구조 취득/연결 batch 전체를 미사용 정수 ID로 명세·프롬프트화하여 T80 앞에 삽입해라. 기존 사용된 번호와 역사 freeze는 변경하지 마라. T78은 조사·분모·명세·queue 설계 범위이며 새 geometry 취득/변형/통합 구현은 배정한 별도 task에서 수행한다. 사용자에게 기본 조사 숙제를 넘기지 마라.

원본/OpenSim_Models/T13 drafts/사용자 WIP와 단일 scene/camera·미니멀 UI를 보존해라. report/evidence/STATUS/taskStatuses를 갱신하고 검증 후 task 소유 변경만 선별 로컬 커밋해라. 혼합 WIP는 소유 hunk 또는 재현 가능한 상태 delta만 포함해라. 해시·포함/제외·잔여 WIP·다음 ID/담당/프롬프트를 남기고 멈춰라. T79나 삽입 task의 구현을 자동 실행하지 마라. push·배포·환자 진단/치료·자침 추천/시뮬레이션은 하지 마라.
```
