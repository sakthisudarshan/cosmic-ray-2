#!/usr/bin/env python3
"""Compute TESTABLE Strategy Metrics from a Cosmic Ray mutation testing session.

Source mapping: Testable_Strategy_Metrics_Mapping_v0.2.xlsx
  Sheet: White Box | L2 Testing Type: Mutation Testing | L3 Technique: Mutation Score
  Primary Tool (Python): cosmic-ray

This script parses `cosmic-ray dump <session>` output and derives the 7
metric rows tied to cosmic-ray in the mapping sheet, normalised to a 0-100
scale, together with pass/fail status against each documented gate.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

# Cosmic-ray operator names whose mutations alter comparison/boundary logic.
BOUNDARY_OPERATOR_KEYWORDS = (
    "ReplaceComparisonOperator",
    "NumberReplacer",
    "ReplaceBinaryOperator",
    "Conditional",
    "Boundary",
)


@dataclass
class MetricResult:
    metric_id: str
    classification: str
    metric: str
    formula: str
    score: float  # 0-100 scale
    gate: str
    passed: bool
    details: dict[str, Any]


@dataclass
class MetricsReport:
    tool: str
    session_file: str
    total_mutants: int
    killed_mutants: int
    survived_mutants: int
    incompetent_mutants: int
    mutation_kill_rate_percent: float
    metrics: list[MetricResult]
    weak_spots: list[dict[str, Any]]
    module_kill_rates: dict[str, float]
    all_gates_passed: bool


def _is_boundary_operator(operator_name: str) -> bool:
    return any(keyword.lower() in operator_name.lower() for keyword in BOUNDARY_OPERATOR_KEYWORDS)


def _normalize_module(module_path: str) -> str:
    return Path(module_path.replace("\\", "/")).name


def _parse_dump_lines(lines: list[str]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        payload = json.loads(line)
        if len(payload) != 2:
            continue
        work_item, work_result = payload
        if work_result is None:
            continue
        mutation = work_item["mutations"][0]
        records.append(
            {
                "job_id": work_item["job_id"],
                "module_path": mutation["module_path"],
                "module_name": _normalize_module(mutation["module_path"]),
                "operator_name": mutation["operator_name"],
                "occurrence": mutation["occurrence"],
                "definition_name": mutation.get("definition_name", ""),
                "test_outcome": (work_result.get("test_outcome") or "unknown"),
                "worker_outcome": (work_result.get("worker_outcome") or "unknown"),
                "is_boundary": _is_boundary_operator(mutation["operator_name"]),
            }
        )
    return records


def load_session_records(session_file: Path) -> list[dict[str, Any]]:
    result = subprocess.run(
        ["cosmic-ray", "dump", str(session_file)],
        capture_output=True,
        text=True,
        check=True,
    )
    return _parse_dump_lines(result.stdout.splitlines())


def load_records_from_dump_file(dump_file: Path) -> list[dict[str, Any]]:
    return _parse_dump_lines(dump_file.read_text(encoding="utf-8-sig").splitlines())


def compute_metrics(records: list[dict[str, Any]], session_file: Path) -> MetricsReport:
    valid_records = [r for r in records if r["test_outcome"] in ("killed", "survived")]
    incompetent = sum(1 for r in records if r["test_outcome"] == "incompetent")
    total = len(valid_records)
    killed = sum(1 for r in valid_records if r["test_outcome"] == "killed")
    survived = sum(1 for r in valid_records if r["test_outcome"] == "survived")

    kill_rate = (killed / total) if total else 0.0

    by_module: dict[str, dict[str, int]] = defaultdict(lambda: {"killed": 0, "total": 0})
    for record in valid_records:
        stats = by_module[record["module_name"]]
        stats["total"] += 1
        if record["test_outcome"] == "killed":
            stats["killed"] += 1

    module_kill_rates = {
        module: (stats["killed"] / stats["total"] if stats["total"] else 0.0)
        for module, stats in by_module.items()
    }
    weak_spot_modules = {m: r for m, r in module_kill_rates.items() if r < 0.5}

    boundary_records = [r for r in valid_records if r["is_boundary"]]
    boundary_total = len(boundary_records)
    boundary_killed = sum(1 for r in boundary_records if r["test_outcome"] == "killed")
    boundary_kill_rate = (boundary_killed / boundary_total) if boundary_total else 1.0

    weak_spots = [
        {
            "module": r["module_name"],
            "function": r["definition_name"],
            "operator": r["operator_name"],
            "occurrence": r["occurrence"],
            "job_id": r["job_id"],
        }
        for r in valid_records
        if r["test_outcome"] == "survived"
    ]

    kill_score = round(kill_rate * 100, 2)
    boundary_score = round(boundary_kill_rate * 100, 2)
    weak_spot_score = round(max(0.0, 100.0 - (len(weak_spot_modules) * 15)), 2)
    # Single-run session (no separate pre-change baseline to diff against):
    # resilience is reported as the current kill rate, i.e. "no regression".
    resilience_score = kill_score
    semantic_score = kill_score

    metrics = [
        MetricResult(
            metric_id="M1",
            classification="Fault Detection Capability",
            metric="Logic Error Sensitivity",
            formula="(total jobs - surviving mutants) / total jobs",
            score=kill_score,
            gate=">= 70%",
            passed=kill_rate >= 0.70,
            details={"killed": killed, "survived": survived, "total": total},
        ),
        MetricResult(
            metric_id="M2",
            classification="Test Coverage Quality Validation",
            metric="Test Rigor Assessment",
            formula="(total jobs - surviving mutants) / total jobs",
            score=kill_score,
            gate=">= 70%",
            passed=kill_rate >= 0.70,
            details={"killed": killed, "survived": survived, "total": total},
        ),
        MetricResult(
            metric_id="M3",
            classification="Test Case Improvement Identification",
            metric="Weak Spot Localization",
            formula="Count(modules where kill rate < 50%); Score = MAX(0, 100 - count*15)",
            score=weak_spot_score,
            gate="0 modules with mutation kill rate below 50%",
            passed=len(weak_spot_modules) == 0,
            details={
                "surviving_mutants": len(weak_spots),
                "weak_spot_module_count": len(weak_spot_modules),
                "weak_spot_modules": weak_spot_modules,
            },
        ),
        MetricResult(
            metric_id="M4",
            classification="Edge Case Detection",
            metric="Boundary Mutant Analysis",
            formula="boundary mutants killed / total boundary mutants",
            score=boundary_score,
            gate=">= 80%",
            passed=boundary_kill_rate >= 0.80,
            details={
                "boundary_killed": boundary_killed,
                "boundary_total": boundary_total,
                "boundary_survived": boundary_total - boundary_killed,
            },
        ),
        MetricResult(
            metric_id="M5",
            classification="Regression Testing Validation",
            metric="Change Resilience Testing",
            formula="(Post-Change Mutation Kill Rate / Pre-Change Mutation Kill Rate) * 100",
            score=resilience_score,
            gate=">= 95%",
            passed=resilience_score >= 95.0,
            details={"note": "Single-run session baseline; resilience reported as current kill rate."},
        ),
        MetricResult(
            metric_id="M6",
            classification="Code Logic Validation",
            metric="Semantic Integrity Check",
            formula="killed mutations / total mutations",
            score=semantic_score,
            gate=">= 75%",
            passed=kill_rate >= 0.75,
            details={"killed": killed, "total": total},
        ),
        MetricResult(
            metric_id="M7",
            classification="Test Suite Effectiveness Evaluation",
            metric="Mutation Kill Rate %",
            formula="(killed_mutations / total_mutations) * 100",
            score=kill_score,
            gate=">= 70%",
            passed=kill_rate >= 0.70,
            details={"killed": killed, "total": total},
        ),
    ]

    return MetricsReport(
        tool="cosmic-ray",
        session_file=str(session_file),
        total_mutants=total,
        killed_mutants=killed,
        survived_mutants=survived,
        incompetent_mutants=incompetent,
        mutation_kill_rate_percent=round(kill_rate * 100, 2),
        metrics=metrics,
        weak_spots=weak_spots,
        module_kill_rates={m: round(r * 100, 2) for m, r in module_kill_rates.items()},
        all_gates_passed=all(m.passed for m in metrics),
    )


def build_gate_report(report: MetricsReport) -> dict[str, Any]:
    """Dashboard-shaped payload. Field names mirror the "Mutation Score Gate"
    table columns on the TESTABLE Confidence Engine exactly: CLASSIFICATION,
    VALUE, EXECUTION STATUS, RESULT, COVERAGE.
    """
    overall_score = round(
        sum(m.score for m in report.metrics) / len(report.metrics), 2
    ) if report.metrics else 0.0
    return {
        "gate_name": "Mutation Score Gate",
        "tool": report.tool,
        "execution_status": "COMPLETED",
        "total_mutants": report.total_mutants,
        "killed_mutants": report.killed_mutants,
        "survived_mutants": report.survived_mutants,
        "mutation_kill_rate_percent": report.mutation_kill_rate_percent,
        "overall_score": overall_score,
        "overall_score_out_of_100": round(overall_score),
        "all_gates_passed": report.all_gates_passed,
        "metrics": [
            {
                "id": m.metric_id,
                "classification": m.classification,
                "metric": m.metric,
                "value": round(m.score),
                "execution_status": "COMPLETED",
                "result": "PASS" if m.passed else "FAIL",
                "coverage": round(m.score),
                "gate": m.gate,
            }
            for m in report.metrics
        ],
    }


def build_platform_cosmic_ray_json(
    session_file: Path,
    gate_report: dict[str, Any],
    report: MetricsReport,
    dump_path: str = "cosmic-ray/0/cosmic_ray_dump.jsonl",
) -> dict[str, Any]:
    """Build the payload the TESTABLE ConfidenceOps platform reads for this
    repo's Mutation Score gate (Mutation Testing technique).

    The platform's Confidence Engine expects this exact file at
    ``cosmic-ray/0/cosmic_ray.json`` with each of the 7 classification scores
    embedded on a 0-100 scale (see the "Mutation Score Gate" table on the
    dashboard: Fault Detection Capability, Test Coverage Quality Validation,
    Test Case Improvement Identification, Edge Case Detection, Regression
    Testing Validation, Code Logic Validation, Test Suite Effectiveness
    Evaluation). If this file is missing/stale, the dashboard falls back to
    1/100 FAIL for classifications it cannot resolve.
    """

    def score_for(metric_id: str) -> float:
        return round(next(m.score for m in report.metrics if m.metric_id == metric_id), 2)

    kill_pct = round(report.mutation_kill_rate_percent, 2)
    return {
        "exit": 0,
        "dump_ok": True,
        "dump_path": dump_path,
        "session_file": str(session_file),
        "totalMutants": report.total_mutants,
        "killedMutants": report.killed_mutants,
        "survivedMutants": report.survived_mutants,
        "incompetentMutants": report.incompetent_mutants,
        "LogicErrorSensitivity": score_for("M1"),
        "TestRigorAssessment": score_for("M2"),
        "WeakSpotLocalization": score_for("M3"),
        "BoundaryMutantAnalysis": score_for("M4"),
        "ChangeResilienceTesting": score_for("M5"),
        "SemanticIntegrityCheck": score_for("M6"),
        "MutationKillRatePercent": kill_pct,
        **gate_report,
    }


def render_markdown(report: MetricsReport) -> str:
    lines = [
        "# TESTABLE Mutation Testing Metrics Report",
        "",
        f"- **Tool:** {report.tool}",
        f"- **Session:** `{report.session_file}`",
        f"- **Total Mutants:** {report.total_mutants}",
        f"- **Killed:** {report.killed_mutants}  |  **Survived:** {report.survived_mutants}  "
        f"|  **Incompetent (excluded):** {report.incompetent_mutants}",
        f"- **Mutation Kill Rate:** {report.mutation_kill_rate_percent:.2f}%",
        f"- **All Gates Passed:** {'YES' if report.all_gates_passed else 'NO'}",
        "",
        "## Metrics (Testable_Strategy_Metrics_Mapping_v0.2 — White Box > Mutation Testing)",
        "",
        "| ID | Classification | Metric | Score /100 | Gate | Status |",
        "|----|-----------------|--------|-----------|------|--------|",
    ]
    for m in report.metrics:
        status = "PASS" if m.passed else "FAIL"
        lines.append(f"| {m.metric_id} | {m.classification} | {m.metric} | {m.score:.2f} | {m.gate} | {status} |")

    lines.extend(["", "## Module Kill Rates", ""])
    for module, rate in sorted(report.module_kill_rates.items()):
        lines.append(f"- `{module}`: {rate:.2f}%")

    if report.weak_spots:
        lines.extend(["", "## Surviving Mutants (Weak Spots)", ""])
        for spot in report.weak_spots:
            lines.append(f"- `{spot['module']}::{spot['function']}` ({spot['operator']} #{spot['occurrence']})")
    else:
        lines.extend(["", "## Surviving Mutants (Weak Spots)", "", "None — all mutants were killed."])

    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--session", default="session.sqlite", help="Path to Cosmic Ray session SQLite file")
    parser.add_argument("--dump-file", default="", help="Optional pre-generated cosmic-ray dump .jsonl file")
    parser.add_argument("--output-json", default="reports/metrics-report.json")
    parser.add_argument("--output-md", default="reports/metrics-report.md")
    parser.add_argument("--output-gate", default="reports/mutation-score-gate.json")
    parser.add_argument(
        "--output-platform",
        default="cosmic-ray/0/cosmic_ray.json",
        help="Path for the TESTABLE platform's Mutation Score Gate file",
    )
    parser.add_argument("--fail-on-gate", action="store_true", help="Exit 1 if any metric gate fails")
    args = parser.parse_args()

    session_file = Path(args.session)
    if args.dump_file:
        records = load_records_from_dump_file(Path(args.dump_file))
    elif session_file.exists():
        records = load_session_records(session_file)
    else:
        print(f"Session file not found: {session_file}", file=sys.stderr)
        return 2

    report = compute_metrics(records, session_file)
    gate_report = build_gate_report(report)

    output_json = Path(args.output_json)
    output_md = Path(args.output_md)
    output_gate = Path(args.output_gate)
    output_platform = Path(args.output_platform)
    for p in (output_json, output_md, output_gate, output_platform):
        p.parent.mkdir(parents=True, exist_ok=True)

    dump_path = args.dump_file or "cosmic-ray/0/cosmic_ray_dump.jsonl"
    platform_report = build_platform_cosmic_ray_json(session_file, gate_report, report, dump_path=dump_path)

    output_json.write_text(json.dumps(asdict(report), indent=2), encoding="utf-8")
    output_md.write_text(render_markdown(report), encoding="utf-8")
    output_gate.write_text(json.dumps(gate_report, indent=2), encoding="utf-8")
    output_platform.write_text(json.dumps(platform_report, indent=2), encoding="utf-8")

    print(render_markdown(report))
    print(f"JSON report:      {output_json}")
    print(f"Gate report:      {output_gate}")
    print(f"MD report:        {output_md}")
    print(f"Platform report:  {output_platform}  (read by the TESTABLE Confidence Engine)")

    if args.fail_on_gate and not report.all_gates_passed:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
