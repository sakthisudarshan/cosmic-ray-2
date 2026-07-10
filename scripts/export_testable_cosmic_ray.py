#!/usr/bin/env python3
"""Post-process a cosmic-ray session for the TESTABLE ConfidenceOps platform.

Run this immediately after `cosmic-ray exec`. It writes
`cosmic-ray/0/cosmic_ray.json`, which is the file the TESTABLE Confidence
Engine reads to populate the "Mutation Score Gate" (Mutation Testing
technique) on the dashboard. Without this file present and up to date, the
dashboard falls back to 1/100 FAIL for classifications it cannot resolve.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.metrics_reporter import (  # noqa: E402
    build_gate_report,
    build_platform_cosmic_ray_json,
    compute_metrics,
    load_session_records,
)


def main() -> int:
    fail_on_gate = "--fail-on-gate" in sys.argv
    session = ROOT / "session.sqlite"
    out_dir = ROOT / "cosmic-ray" / "0"
    dump_file = out_dir / "cosmic_ray_dump.jsonl"
    platform_file = out_dir / "cosmic_ray.json"
    out_dir.mkdir(parents=True, exist_ok=True)

    if not session.exists():
        print(f"Missing session: {session}", file=sys.stderr)
        return 2

    try:
        dump_text = subprocess.check_output(
            ["cosmic-ray", "dump", str(session)],
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        dump_file.write_text(dump_text, encoding="utf-8")
    except subprocess.CalledProcessError as exc:
        print(f"cosmic-ray dump failed: {exc}", file=sys.stderr)
        return exc.returncode or 1

    records = load_session_records(session)
    report = compute_metrics(records, session)
    gate_report = build_gate_report(report)
    platform_report = build_platform_cosmic_ray_json(
        Path("session.sqlite"),
        gate_report,
        report,
        dump_path="cosmic-ray/0/cosmic_ray_dump.jsonl",
    )

    (ROOT / "reports").mkdir(parents=True, exist_ok=True)
    (ROOT / "reports" / "mutation-score-gate.json").write_text(
        json.dumps(gate_report, indent=2), encoding="utf-8"
    )
    platform_file.write_text(json.dumps(platform_report, indent=2), encoding="utf-8")

    print(f"Mutation Kill Rate: {report.mutation_kill_rate_percent:.2f}%")
    print(f"All Gates Passed:   {'YES' if report.all_gates_passed else 'NO'}")
    print(f"Platform file:      {platform_file}")

    if fail_on_gate and not report.all_gates_passed:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
