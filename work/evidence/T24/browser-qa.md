# T24 실제 브라우저 검증 — 2026-09-27

- Vite 8.3.1, in-app browser, localhost `127.0.0.1:5173`. T44에서 파생한 실제 `ankle-dorsiflexion.glb`를 `loadAnimationScene`과 `AnimationPlaybackController`로 로드했다. GLB SHA-256은 manifest와 일치했다.
- 격리된 개발 QA 페이지 `t24-motion-preview.html`에서 0.00, 1.00, 2.00초의 실제 GLB 렌더를 시각 확인했다. 발 앞쪽이 위로 회전했고 재생 버튼에서 시간이 증가해 2.00초에 도달했다. 정지와 처음 자세 버튼에서 0.00초 복원을 확인했다. 별도 QA 화면은 학습 화면 산출물이 아니다.
- 처음 구현에서는 메인 학습 화면의 앞정강근 선택만으로 기존 BodyParts3D 그래픽을 검은 배경의 OpenSim 발목 장면으로 자동 교체했다. 사용자가 요구한 원래 근육 그래픽의 CTA 기반 수축 설명에 맞지 않아 그 UI 변경을 모두 제거했다.
- 최종 메인 화면 `/?region=leg&kind=muscle&id=HA-M-000003&side=right`에서 기존 종아리 근육 그래픽, 앞정강근/전경골근/Tibialis anterior 이름, 기시·정지 본문, 비활성 움직임 CTA를 실제 브라우저 AX와 렌더로 확인했다. 검은 OpenSim 장면은 메인 화면에 나타나지 않는다. 콘솔 error/warn 조회 결과 `[]`.
- QA용 별도 화면의 390px 시범 렌더도 확인했으나, 사용자가 메인 화면 방식 자체를 거부했으므로 390/1024/1440의 최종 움직임 UI 합격을 주장하지 않는다. 제품 CTA 재생, 반복, resize, 뒤로가기, 주석 수명도 아직 검증하지 못했다.

## 판정

실제 clip 파일의 로드·세 자세·재생은 확인됐지만, 원래 앞정강근 그래픽의 수축을 근거 있게 표현하고 CTA에서 연속 반복하는 요구는 **미달**이다. T24는 blocked이며 T25 통합의 선행 합격으로 취급할 수 없다.
