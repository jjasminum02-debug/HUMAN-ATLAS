#!/usr/bin/env python3
"""Generate current execution views from EXECUTION.json; never edit history evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "work/EXECUTION.json"
START = "<!-- BEGIN GENERATED EXECUTION -->"
END = "<!-- END GENERATED EXECUTION -->"


def load_and_validate():
    raw = SOURCE.read_bytes()
    data = json.loads(raw)
    order = data["activeOrder"]
    if len(order) != len(set(order)) or set(order) != set(data["tasks"]):
        raise ValueError("Active tasks must be unique and have exactly one record")
    if any(t in order for t in [*data["absorbedTasks"], *data["retiredIds"]]):
        raise ValueError("Absorbed/retired task cannot be active")
    if [t for p in data["phases"] for t in p["taskIds"]] != order:
        raise ValueError("Phase order differs from activeOrder")
    for tid, task in data["tasks"].items():
        if task["acceptance"] not in {"pending", "partial", "blocked", "passed"}:
            raise ValueError(f"Invalid acceptance for {tid}")
        if not (ROOT / task["spec"]).is_file():
            raise ValueError(f"Missing spec for {tid}")
        if task["acceptance"] == "passed" and not (ROOT / task["report"]).is_file():
            raise ValueError(f"Passed task needs an actual report: {tid}")
    return data, raw


def prompt(data, tid):
    task = data["tasks"][tid]
    index = data["activeOrder"].index(tid)
    next_id = data["activeOrder"][index + 1] if index + 1 < len(data["activeOrder"]) else "없음"
    return (
        f"HUMAN ATLAS에서 {tid}만 수행해라. 담당 {task['owner']}.\n"
        "AGENTS.md, work/EXECUTION.json, work/NEXT.md, 최신 STATUS의 generated execution 블록,\n"
        "design/2026-09-25-muscle-atlas/25-WHOLE-BODY-BASE-RESET.md와 해당 task 명세, 실제 선행 report/evidence/manifest를 읽어라.\n"
        "EXECUTION이 현재 범위/순서의 유일한 원본이다. 역사 queue의 nextTask를 실행하지 마라. 24의 엑셀 검증·한글 기능·짧은 신경·표정근 motion 제외는 유지한다.\n"
        f"이번 범위: {task['scope']}\n"
        "시작 HEAD/status/hash를 기록하고 원본/OpenSim_Models/사용자 WIP/T13 drafts/역사 freeze를 보존한다. source-only/권리/사람검토를 추정 승격하지 않는다.\n"
        "25 설계의 T100 상태 교정에 따라 과거 not_approved_by_this_task·공개 재배포 held·humanReview 미수행을 로컬 개발의 일괄 차단으로 사용하지 마라. 담당 AI가 source-family 근거/예외와 객체·의미 대응을 검토하여 현재 overlay 결정을 기록하고 진짜 충돌 항목만 보류한다.\n"
        "공통 도구와 단일 scene/renderer/camera를 재사용한다. 자동 전수처리와 내부 의미검증 unit을 구분하며 미완이면 같은 task/nextUnit으로 재개한다. 새 번호를 반복 발급하지 마라.\n"
        "관련 실제 검증·progress·report/evidence를 남기고 EXECUTION의 해당 task record만 갱신한다. python3 work/tools/sync_execution.py와 --check로 투영 문서를 동기화한다.\n"
        "소유 파일/hunk만 선별 로컬 커밋하고 해시·포함/제외·잔여 WIP·다음 프롬프트를 남긴 뒤 멈춰라.\n"
        f"기본 다음 ID: {next_id}. 필수 gate 미달이면 먼저 같은 task를 재개하고 다음 task를 자동 실행하지 마라. push·배포·진단·치료·침 시뮬레이션 금지.\n"
    )


def render(data):
    order = data["activeOrder"]
    next_id = next((t for t in order if data["tasks"][t]["acceptance"] != "passed"), None)
    observation = data["observedWork"]
    passed = [t for t in order if data["tasks"][t]["acceptance"] == "passed"]
    current = [t for t in order if data["tasks"][t]["executionStatus"] == "in_progress"]
    latest = passed[-1] + " / accepted" if passed else observation["taskId"] + " / " + observation["state"]
    next_text = (
        "# 현재 다음 실행\n\n"
        "자동 생성. 편집 원본은 [EXECUTION.json](EXECUTION.json). 역사 handoff/자료 개수로 다음 작업을 결정하지 않는다.\n\n"
        f"- 확인된 최근 진행: {latest}\n"
        f"- 다음 ID: **{next_id or '없음'}**\n"
        "- 먼저 전신 구조 G1을 완성한다. 새 task 번호 없이 T98→T99→T100→T80→T58.\n\n"
    )
    if next_id:
        next_text += "```text\n" + prompt(data, next_id) + "```\n"
    book = (
        "# 현행 실행 순서와 프롬프트\n\n"
        "자동 생성 · 원본: `work/EXECUTION.json` · `python3 work/tools/sync_execution.py --check`로 일치 검증.\n\n"
        "이 파일의 과거 T95/T102 시점 안내는 Git 이력으로 보존된다. 현재 next는 [work/NEXT.md](../../work/NEXT.md)에서 확인한다. 완료한 과거 작업은 반복하지 않는다.\n\n"
        "25-WHOLE-BODY-BASE-RESET.md가 변경한 범위가 우선한다. 기존 T105–109/T110–121/T166의 필요한 내용은 새 범위의 T98/T99/T100/T80/T58로 흡수됐으며 별도 실행하지 않는다. T122–165도 미실행 폐기 상태다.\n\n"
    )
    for phase in data["phases"]:
        book += f"## {phase['id']} — {phase['goal']}\n\n| ID | 담당 | 결과 |\n|---|---|---|\n"
        for tid in phase["taskIds"]:
            t = data["tasks"][tid]
            book += f"| [{tid}](#{tid.lower()}) | {t['owner']} | {t['title']} |\n"
        book += "\n"
    book += "## 붙여 넣기 — 한 번에 한 ID\n\n"
    for tid in order:
        book += f'<a id="{tid.lower()}"></a>\n### {tid} — {data["tasks"][tid]["title"]}\n\n```text\n{prompt(data, tid)}```\n\n'
    book = "\n".join(line.rstrip() for line in book.splitlines()).rstrip() + "\n"
    status_path = ROOT / "work/STATUS.md"
    status = status_path.read_text()
    if START in status:
        status = status[:status.index(START)] + status[status.index(END) + len(END):]
        status = status.lstrip("\n")
    # Old top-of-file snapshots stay readable, but cannot impersonate current execution fields.
    lines = status.splitlines()
    for i, line in enumerate(lines[:24]):
        if line.startswith(("- CURRENT_TASK:", "- NEXT_TASK:", "- PLAN_REVISION:", "- LAST_REPORT:")):
            lines[i] = line.replace("- ", "- HISTORICAL_", 1)
    status = "\n".join(lines) + "\n"
    block = (
        f"{START}\n# 현재 실행 — 단일 기준\n\n"
        "- SOURCE_OF_TRUTH: work/EXECUTION.json\n"
        f"- PLAN_REVISION: {data['revision']}\n"
        f"- CURRENT_TASK: {current[0] if current else 'none recorded as running'}\n"
        f"- LAST_OBSERVED_TASK: {latest}\n"
        f"- LEGACY_T104_OBSERVATION_AT_RESET: {observation['note']}\n"
        f"- NEXT_TASK: {next_id or '없음'} / {data['tasks'][next_id]['owner'] if next_id else 'none'}\n"
        "- NEXT_PROMPT: work/NEXT.md\n"
        "- CURRENT_GOAL: G1 전신 뼈·근육의 실제 표시/세 이름/선택/관찰 합격. 이후 설명→신경→모션.\n"
        "- HISTORY: 아래 기존 보고/상태와 work/evidence/*의 nextTask는 당시 snapshot이며 실행 지시가 아니다.\n"
        f"{END}\n\n"
    )
    registry_path = ROOT / "work/task-registry-r15.json"
    reg = json.loads(registry_path.read_text())
    reg["statusSource"] = "derived current projection of work/EXECUTION.json; historical records preserved"
    reg["executionAuthority"] = "work/EXECUTION.json"
    reg["taskStatusesRole"] = "historical observations; currentTaskStates is the current derived execution state"
    reg["currentTaskStates"] = {tid: {"executionStatus": task["executionStatus"], "acceptance": task["acceptance"]} for tid, task in data["tasks"].items()}
    reg["nextTask"] = next_id
    reg["activeQueue"] = order
    existing = {t["id"]: t for t in reg["tasks"]}
    for tid, task in data["tasks"].items():
        index = order.index(tid)
        row = existing[tid]
        row.update({"title": task["title"], "model": task["owner"], "scopeOverride": task["scope"],
                    "executionAmendment": data["revision"], "amendmentDesign": data["design"],
                    "defaultNext": order[index+1] if index+1 < len(order) else None,
                    "prerequisite": "EXECUTION phase/order and actual predecessor acceptance; 25 design supersedes historical ordering",
                    "prerequisiteIds": [order[index-1]] if index else ["T97", "T96"], "mode": "active"})
        if "resumePrerequisiteIds" in row:
            row["resumePrerequisiteIds"] = row["prerequisiteIds"]
        row["currentAcceptance"] = task["acceptance"]
        # taskStatuses records observed historical execution; planning is not an execution rewrite.
    for tid, record in data["absorbedTasks"].items():
        existing[tid].update({"mode": "absorbed_not_executed", "absorbedInto": record["into"],
                             "defaultNext": None, "executionAuthority": "work/EXECUTION.json"})
        reg["taskStatuses"][tid] = "absorbed_not_executed"
    reg["productGates"]["nerveStart"] = "G1/T58 + T84 accepted; no full-muscle-animation prerequisite; EXECUTION G3"
    reg["productGates"]["motionStart"] = "G1/G2/G3 accepted; EXECUTION G4; facial-expression exact deferral retained"
    reg["wholeBodyBaseAmendment"] = {"design": data["design"], "executionAuthority": "work/EXECUTION.json", "newTaskIds": []}
    return {
        ROOT / "work/NEXT.md": next_text,
        ROOT / "design/2026-09-25-muscle-atlas/23-PROMPTS-AFTER-T95.md": book,
        status_path: block + status,
        registry_path: json.dumps(reg, ensure_ascii=False, indent=2) + "\n",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    data, source_raw = load_and_validate()
    paths = [ROOT / "work/STATUS.md", ROOT / "work/task-registry-r15.json"]
    before = {p: p.read_bytes() for p in paths}
    outputs = render(data)
    if SOURCE.read_bytes() != source_raw or any(p.read_bytes() != raw for p, raw in before.items()):
        raise SystemExit("Concurrent execution/status edit detected. Re-read before syncing.")
    drift = [p for p, text in outputs.items() if not p.exists() or p.read_text() != text]
    if args.check:
        if drift:
            raise SystemExit("Execution projection drift: " + ", ".join(str(p.relative_to(ROOT)) for p in drift))
        print("Execution projections match; no writes.")
        return
    for path in drift:
        path.write_text(outputs[path])
    print(f"Updated {len(drift)} execution views from {hashlib.sha256(source_raw).hexdigest()[:12]}")


if __name__ == "__main__":
    main()
