#!/usr/bin/env bash
# Run cosmic-ray mutation testing end-to-end and generate TESTABLE metrics reports.
set -euo pipefail
cd "$(dirname "$0")/.."

echo "==> Installing dependencies"
python -m pip install -e ".[dev]" -q

echo "==> Running pytest baseline (must pass before mutating)"
python -m pytest tests -q

echo "==> Cosmic Ray baseline (confirms tests pass unmutated)"
cosmic-ray baseline cosmic-ray.toml

echo "==> Initializing mutation session"
rm -f session.sqlite
cosmic-ray init cosmic-ray.toml session.sqlite

echo "==> Executing mutations (this may take a few minutes)"
cosmic-ray exec cosmic-ray.toml session.sqlite

echo "==> Cosmic Ray summary"
cr-rate session.sqlite
cr-report session.sqlite --surviving-only

echo "==> Generating TESTABLE metrics report (fails the build if any gate is not met)"
python scripts/metrics_reporter.py --session session.sqlite --fail-on-gate

echo "==> Exporting TESTABLE platform gate file (cosmic-ray/0/cosmic_ray.json)"
python scripts/export_testable_cosmic_ray.py --fail-on-gate

echo "==> Done. See reports/metrics-report.md for the full breakdown."
echo "    Commit cosmic-ray/0/cosmic_ray.json so the TESTABLE dashboard picks up the latest scores."
