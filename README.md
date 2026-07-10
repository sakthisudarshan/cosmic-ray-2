# TESTABLE Cosmic Ray — Mutation Testing Metrics Verification

Python mutation-testing repository built to **verify and maintain** the
`Testable_Strategy_Metrics_Mapping_v0.2` metrics for the **White Box → Mutation
Testing → Mutation Score** technique, whose Python primary tool is
[**cosmic-ray**](https://github.com/sixty-north/cosmic-ray).

This repo is the source of truth for that mapping row: any time the metric
formulas, thresholds, or the tool's behaviour change, re-running this repo
(locally or via CI) re-verifies whether the metrics still compute correctly
and still hit their gates — currently **100/100 on all 7 metrics**.

## Mapping Summary (from the Excel sheet)

| Field | Value |
|---|---|
| L1 Strategy | White Box |
| L2 Testing Type | Mutation Testing |
| L3 Technique | Mutation Score |
| Primary Tool (Python) | **cosmic-ray** (secondary: `mutmut`) |
| Metric emitted directly? | No — derived from session results |

Full row-by-row formulas/thresholds are in
[`docs/metrics-mapping.md`](docs/metrics-mapping.md); the original workbook is
archived at
[`docs/Testable_Strategy_Metrics_Mapping_v0.2.xlsx`](docs/Testable_Strategy_Metrics_Mapping_v0.2.xlsx).

## The 7 Metrics Verified Here

| ID | Classification | Metric | Gate | Current Score |
|----|-----------------|--------|------|----------------|
| M1 | Fault Detection Capability | Logic Error Sensitivity | ≥ 70% | **100/100** |
| M2 | Test Coverage Quality Validation | Test Rigor Assessment | ≥ 70% | **100/100** |
| M3 | Test Case Improvement Identification | Weak Spot Localization | 0 weak modules | **100/100** |
| M4 | Edge Case Detection | Boundary Mutant Analysis | ≥ 80% | **100/100** |
| M5 | Fault Detection Capability | Change Resilience Testing | ≥ 95% | **100/100** |
| M6 | Test Coverage Quality Validation | Semantic Integrity Check | ≥ 75% | **100/100** |
| M7 | Fault Detection Capability | Mutation Kill Rate % | ≥ 70% | **100/100** |

`scripts/metrics_reporter.py` computes all 7 rows from a cosmic-ray session
and writes them to `reports/mutation-score-gate.json` /
`reports/metrics-report.md`, so scores can be checked independently of this
README at any time.

## Why It Hits 100/100

- `src/testable_demo/` contains small, boundary-heavy modules
  (`calculator.py`, `discount.py`, `order_validator.py`).
- `tests/` pins down every branch **and every boundary value** (`n-1`, `n`,
  `n+1`) with exact (non-approximate) assertions, so cosmic-ray's
  comparison/number/arithmetic mutants cannot survive.
- Clamping logic uses `min()`/`max()` instead of hand-rolled `if`/`elif`
  chains, which avoids **equivalent mutants** at the exact boundary value
  (e.g. clamping a value that already equals the boundary can't produce a
  behavioural difference no matter how the comparison is mutated — a known,
  documented limitation of mutation testing). Removing that redundancy from
  the source is what lets the kill rate reach a genuine 100%, instead of
  reporting a false "FAIL" against an unkillable mutant.

## Quick Start

### Prerequisites

- Python 3.10+
- Git

### Install

```powershell
cd cosmic-ray-2
python -m pip install -e ".[dev]"
```

### Run mutation testing + metrics (Windows)

```powershell
.\scripts\run_mutation_testing.ps1
```

### Run mutation testing + metrics (Linux/macOS)

```bash
chmod +x scripts/run_mutation_testing.sh
./scripts/run_mutation_testing.sh
```

### Manual step-by-step

```powershell
python -m pytest tests -q
cosmic-ray baseline cosmic-ray.toml
cosmic-ray init cosmic-ray.toml session.sqlite
cosmic-ray exec cosmic-ray.toml session.sqlite
cr-rate session.sqlite
cr-report session.sqlite --surviving-only
python scripts/metrics_reporter.py --session session.sqlite --fail-on-gate
```

## Output

After a run, reports are written to:

- `reports/metrics-report.json` — full metrics detail (machine-readable)
- `reports/metrics-report.md` — human-readable summary with module kill rates
- `reports/mutation-score-gate.json` — compact dashboard gate summary
  (`overall_score_out_of_100`, per-metric PASS/FAIL)

`metrics_reporter.py --fail-on-gate` exits non-zero if **any** of the 7 gates
is not met, which is what CI uses to fail the build.

## Project Layout

```
src/testable_demo/     # Code under test (calculator, discount, order validator)
tests/                  # Pytest suite designed for a 100% mutation kill rate
cosmic-ray.toml         # Cosmic Ray configuration
scripts/
  metrics_reporter.py   # Maps a cosmic-ray session -> the 7 TESTABLE metrics
  run_mutation_testing.ps1 / .sh
docs/
  metrics-mapping.md                          # Row-by-row formula reference
  Testable_Strategy_Metrics_Mapping_v0.2.xlsx  # Source workbook
.github/workflows/mutation-testing.yml         # CI: reruns everything on every push/PR
```

## Maintaining This Repo (Regression Checking)

Whenever the source modules, tests, or `cosmic-ray.toml` change:

1. `.\scripts\run_mutation_testing.ps1` (or the `.sh` equivalent) locally, **or**
   push/open a PR — GitHub Actions runs the identical pipeline.
2. Open `reports/metrics-report.md` and confirm all 7 metrics still show
   **PASS** and the mutation kill rate is still 100%.
3. If a change introduces a surviving mutant, `cr-report session.sqlite
   --surviving-only --show-diff` shows exactly which line/operator survived;
   add a test that pins the boundary it exposes, then re-run.
4. If the Excel mapping (`docs/Testable_Strategy_Metrics_Mapping_v0.2.xlsx`)
   changes — new thresholds, new classifications, a different tool — update
   `docs/metrics-mapping.md` and `scripts/metrics_reporter.py` to match, then
   re-run to re-verify the new gates.

This gives a repeatable, version-controlled way to prove the `cosmic-ray`
row of the metrics mapping still executes correctly after any modification.

## License

MIT — verification/reference project for TESTABLE Strategy Metrics Mapping v0.2.
