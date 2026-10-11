# 다음 요청용 AC3 프롬프트 — 아직 실행하지 않음

```text
HUMAN ATLAS에서 경혈 학습 AC3만 수행해라.
AGENTS.md, 최신 work/EXECUTION.json와 work/NEXT.md,
design/2026-09-25-muscle-atlas/29-ACUPOINT-AND-CHANNEL-LEARNING.md,
work/reports/acupoint-AC1.md, work/reports/acupoint-AC2.md,
work/evidence/acupoint-AC2/validation.json과 실제 carrier/anchor/화면 evidence를 읽어라.

AC2 기술 검증과 실제 혈위 미확정을 구분해라. 양쪽 22점은 unresolved이고 제품 좌표는 0개다.
기존 점·체표 학습선·전통 유주·분지·내행·경근·피부영역을 같은 자료로 간주하지 마라.
AC3 범위의 영역/연관 학습을 구현하되 Territory와 SinewPath를 별도 schema/data로 유지해라.
실제 carrier와 region coverage를 먼저 확인하고 근거 없는 전신 영역/경근 경계나 피부 정확성을 만들지 마라.
carrier가 실제 지원하지 않는 영역만 구분하여 held로 남기고 fixture를 제품 데이터로 내보내지 마라.
근육 표면이나 mirror 추정만으로 피부/혈위/영역 검증을 대신하지 마라.
교과서 판본·기본 위치 문헌·source 권리·AI 제안·교수 검토·공개 재배포를 분리해라.
교과서가 없으면 해설 준비 상태를 보여주고 환자 진단·치료·침 시뮬레이션을 추가하지 마라.

같은 AnatomySceneRoot/renderer에서 기존 point/route를 보존하고 정지 자세만 지원해라.
기존 근육/뼈 클릭·선택·카메라/관찰 owner·레이어와 정상 motion 복원 흐름을 보존해라.
새 renderer/인체 복사본, 보기옵션·홈·로딩 디자인 변경은 하지 마라.
module/data 지연 로딩·전환 취소·resource 해제·수동 orbit 우선권을 유지해라.
carrier/영역을 포함한 bytes/triangles/GPU 비용을 측정하고 기존 예산을 올리지 마라.
390/1024/1440 실제 화면·원래 카메라 복귀·기존 anatomy click·반복 해제를 검증해라.
원본/OpenSim_Models/T13/사용자 WIP와 AC2의 제외된 전체 복사본/receipt를 보존해라.
work/reports/acupoint-AC3.md와 work/evidence/acupoint-AC3/에 결과를 남기고,
소유 변경만 선별 로컬 커밋하여 해시·포함/제외·남은 변경을 보고해라.
AC4 자동 실행·push·배포는 하지 마라.
```
