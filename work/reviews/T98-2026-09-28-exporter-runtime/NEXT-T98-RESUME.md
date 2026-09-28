# T98 재개 — 확인된 실행 경로 사용

2026-09-28 Astra 후속 감사. T98의 partial 판정은 유지한다. 같은 바이너리·같은 기본 장면 명령이 제한된 실행에서는 exit 139, 승인된 권한 실행에서는 exit 0으로 끝났다. 해부학 파일은 이번 감사에서 열거나 변환하지 않았다. 따라서 새 source/Blender 버전을 찾기 전에 이미 확인된 실행 경로로 frozen exporter unit을 진행한다.

현재 `/Volumes/Blender/Blender.app/Contents/MacOS/Blender`는 3.5.0이다. T98의 5.2.2 기록과 다르지만 당시 mount가 무엇이었는지는 단정하지 않는다. 옛 기록을 덮어쓰지 말고 실제 실행 버전과 바이너리 해시를 새 receipt에 기록한다. 상세 근거는 같은 폴더의 `runtime-startup.json`이다.

다음 프롬프트를 사용한다.

```text
HUMAN ATLAS에서 T98만 재개해라. 담당 Luna Max.
AGENTS.md, work/EXECUTION.json, work/NEXT.md, work/tasks/T98.md,
design/2026-09-25-muscle-atlas/25-WHOLE-BODY-BASE-RESET.md,
work/reports/T98.md, T98 progress/exporter-attempts/representative-sample-freeze,
work/reviews/T98-2026-09-28-exporter-runtime/runtime-startup.json과 이 문서를 읽어라.

이번 새 근거: 동일한 Blender 바이너리와 factory-startup 명령이 제한 실행에서는
exit 139, 승인된 require_escalated 실행에서는 exit 0으로 정상 시작했다.
현재 확인된 실행 파일은 3.5.0이며 SHA-256은
23171ca8704539b44c94cb370894cb3b38908530c012267bed079326d7be95b0이다.
실행 전에 현재 경로/버전/hash와 공식 패키지 receipt의 관계를 확인해라.
마운트 경로만 보고 5.2.2라고 기록하거나 역사 결과를 덮어쓰지 마라.

이미 동결한 inventory·542 targets·563 memberships·12 locators를 다시 조사하지 마라.
source archive나 Blender를 재다운로드하거나 버전 탐색을 반복하지 마라.
검토 가능한 최소 exporter 스크립트를 먼저 준비하고, 기존 정상 실행 경로에 대해
필요한 tool 승인을 받아 원본을 읽기 전용으로 열어라.
--background --factory-startup --disable-autoexec를 유지하고, 자동 실행/원본 저장은 금지한다.
호스트 보안 설정을 바꾸지 마라. 승인 거부 시 우회하지 말고 정확한 이유와 필요한 조치를 남겨라.

같은 T98 nextUnit에서 동결한 12개 locator를 실제 evaluated dependency graph와 대조하고,
modifier/shared mesh/negative transform/constraint 결과를 검증해라.
Cross Section X는 helper로 기록하고 해부 구조 수나 coverage에 넣지 마라.
evaluated 결과·변환·preview·geometry hash·크기/삼각형 수를 남겨라.
원본 pointer는 재실행 시 바뀔 수 있으므로 파일 hash와 동결한 source locator의
이름·data·계층 등 대응을 확인하며 런타임 pointer 값의 일치를 요구하지 마라.

단위/frame/rest pose/좌우, exact identity와 권리 상속·예외를 기존 계약대로 검증해라.
source 평가에 필요한 driver가 차단돼 결과가 달라진다면 부분 결과로 기록하고,
기본 장면 시작 성공을 anatomy export/base/rights/learner binding 합격으로 확대하지 마라.
이름 후보를 canonical mapping으로 추정 승격하지 마라.
전신 베이스는 실제 범위·변환·품질·비용·권리 근거가 충족될 때만 선택한다.

원본/OpenSim_Models/T13 drafts/사용자 WIP/역사 freeze를 보존하고 웹 runtime을 수정하지 마라.
T98 report/evidence와 EXECUTION의 T98 record만 실제 결과에 맞게 갱신한 뒤
python3 work/tools/sync_execution.py 및 --check를 수행해라.
필수 gate가 남으면 같은 T98을 유지하되 환경 시작과 export 실패를 구분해 보고해라.
소유 변경만 선별 로컬 커밋하고 해시·포함/제외·잔여 변경·다음 프롬프트를 남겨라.
T99 이상, push, 배포, 진단·치료·침 시뮬레이션은 시작하지 마라.
```

이 후속 감사는 실행 환경의 시작 시험과 재개 지침만 추가한다. T98의 17/17은 당시 inventory/보존 검사이며 evaluated export 성공이 아니다. T98 상태, 기존 보고서와 원본은 변경하지 않는다.
