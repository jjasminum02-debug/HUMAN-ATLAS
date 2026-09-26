# T15f 분리 후속 — 장면 단위 manifest 검증

T15f를 넘어서는 전신 확장 제약이며 현재 실행에서 수정하지 않았다. 실제 코드 atlas-web/src/viewer/manifest.ts는 canonical 전체 map 크기 20 assets / 6 instances / 7 mappings와 bridge coverage 전체 숫자를 T07/T12 검증에 직접 고정한다. 새 부위의 canonical 자산·instance·mapping이 추가되면 종아리 manifest 검증이 실패할 수 있다.

분리 후속 작업은 work/tasks/T15f-FU01.md에 not_started로 발급했다. 고정 전신 개수를 scene-wide invariant로 두지 말고 다음을 검증해야 한다.

- T07 source model 자체의 GLB SHA-256, byte 수, mesh 수, crosswalk, frame/pose 고정값은 유지한다.
- T12 calf bridge는 T12 scene/model 범위의 mesh, 우측 instance, mapping 및 frame/pose/count로 검증한다.
- 전신 canonical catalog의 총량 변화와 scene별 선택 binding 검증을 분리한다.
- 테스트 전용 추가 region canonical asset/instance/mapping fixture를 주입해도 기존 calf scene 검증은 통과해야 한다. 단, calf scene 안에서 실제 binding/frame/pose/hash를 바꾸면 계속 실패해야 한다.

다음 데이터 배치 실행 전에 별도 후속의 우선순위를 정한다. T15g에서는 inventory/배치 계획을 수행하되 실제 추가 scene asset이나 runtime manifest count 변경은 이 후속 완료 전까지 하지 않는다.
