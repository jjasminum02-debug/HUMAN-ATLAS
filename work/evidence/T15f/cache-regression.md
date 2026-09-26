# SceneRequestCache capacity 회귀

재현 조건은 capacity=2인 SceneRequestCache에 서로 다른 키 a–e 요청을 모두 시작한 뒤 다섯 promise를 같은 microtask 구간에서 완료하는 것이다.

기존 동작에서는 응답 완료 시점에 모든 entry가 아직 subscriber 수 1이라 trim()이 용량을 줄이지 못했다. 완료 subscriber의 마지막 해제 뒤 다시 trim하지 않아, 다섯 결과가 확정되고도 5개가 남았다. 재획득한 가장 오래된 a가 두 번째 요청을 하지 않고 first-a를 재사용하는 것으로 회귀를 재현했다.

수정은 각 acquire subscriber의 finish가 subscriber 수를 낮춘 직후 trim()을 호출하도록 했다. 취소·실패 및 pending 마지막 subscriber 제거 동작은 유지했다. 회귀 테스트는 다섯 동시 완료 뒤 a 재획득이 second-a를 반환하고 request 횟수가 2인지 확인한다. 최신 실행에서 scene lifecycle 테스트 9/9 통과했다.

테스트 파일: atlas-web/src/viewer/sceneCache.test.ts
구현: atlas-web/src/viewer/sceneCache.ts
