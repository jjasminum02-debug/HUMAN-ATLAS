# T32 입력 메모 — T43 metadata 조사 재사용

- T32는 R14 registry에서 T31 완료 후 실행하며, T43은 입력 자료만 준비했다.
- T31 보고서는 아직 없고 registry 상태는 `planned_not_started`; T32는 시작하지 않았다.
- 전체 분모는 `null` 유지: T15g 85 unique partial IDs 중 48 individual / 16 group / 21 part. 85 또는 12부위 task 수를 전신 분모로 사용하지 않는다.
- 후보 첫 확장: shoulder-scapular (10 partial source IDs; exact routing, source rows, local geometry and rights still pending).
- 부위별 후보 ID와 현재 product memberships는 matrix JSON의 `regionRows`와 이 JSON의 `regionPackagingCandidates`에서 따로 확인한다.
- Lower-extremity source group/part IDs are held, no auto fan-out. Multi-membership may repeat a stable ID; unique count deduplicates it.
- 분모 inclusion/exclusion, region memberships, name triplets, origin/insertion/action text, geometry, sides, rights, rig and clips require separate decisions and status.
- movement group candidates are not clips and do not identify muscle contribution.
- `work/review-queue/region-acquisition-matrix-t43.json` / SHA256: `72f8370afe065730f85e45a53491d75f215a0d5ff02c9708dedece623a7eb1e4`
- `work/review-queue/region-acquisition-gaps-t43.json`
