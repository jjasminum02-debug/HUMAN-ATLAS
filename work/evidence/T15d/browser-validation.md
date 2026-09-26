# T15d 실제 브라우저 확인

- Browser: Codex in-app browser, localhost Vite learner, 1280×720.
- Console: 마지막 깨끗한 브라우저 탭에서 error 0, warning 0.
- 시작 direct route로 right Tibia bone card와 deep-link card 일치를 확인했다.
- Tibia card의 `가자미근` action → `?region=leg&kind=muscle&id=HA-M-000002&side=right` → 가자미근 card.
- 장면 canvas에서 Tibia 선택 → `?region=leg&kind=bone&id=HA-S-TIBIA&side=right&instance=HA-SI-R-HA-S-TIBIA&mesh=HA-MESH-BP3D4-FJ3387` → 오른쪽 Tibia 카드.
- Tibia card의 `가자미근` action으로 다시 근육 카드에 복귀.
- 가자미근 카드가 보이는 상태에서 측면으로 돌린 뒤 unbound right talus를 선택: URL은 `?region=leg&side=right`, 안내 heading은 `이 메시의 뼈 연결은 확인되지 않았습니다`, 본문은 `right talus`에 안정된 전체 뼈 ID/crosswalk가 없다고 표시. 이전 근육 선택은 제거됨.
- Tibia의 source disclosure는 Gray 1918 링크 1개와 판본 설명을 보였다. 별도 moderne-source/사람-review 주장 없음.
- 최종 미매핑 화면은 learner overlay에만 상태를 표시했고 authoring storage를 수정하지 않았다.
