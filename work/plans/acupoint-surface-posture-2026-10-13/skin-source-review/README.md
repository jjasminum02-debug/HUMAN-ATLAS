# 피부 입력 선택 evidence

선택/권리/hash/실제 검사 범위는 `selection.json`을 읽는다. 주 입력은 pinned MakeHuman core body다. 이 폴더는 개발 evidence이며 runtime asset 디렉터리가 아니다.

실물은 `atlas-data/source-cache/datasets/skin-source-review-2026-10-13/`(Git ignore)에 있다. `base.obj`의 body만 사용한다. 원본을 직접 변형하지 않는다. 같은 폴더의 공식 target/license를 읽고 source-to-derived recipe를 만든다.

`makehuman-shape-preview.png`는 source shape의 전/측/후 비교용이다. smoothing·제품 재질·ZA 정합·임상적 정밀도를 검증한 화면이 아니다. 별도 앱/이미지 생성 모델로 인체를 창작하지 않았다.

재현: 승인된 Blender에 `--factory-startup --disable-autoexec --python extract_comparison.py -- <cache absolute path>`를 사용하고, numpy/Pillow가 있는 Python으로 `software_preview.py <cache absolute path>`를 실행한다. MB-Lab face는 Blender3.5에서 부정합이므로 그 추출 결과는 표시/생산에 쓰지 않는다. MakeHuman mesh-0만 비교용으로 렌더한다.
