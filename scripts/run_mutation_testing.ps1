#!/usr/bin/env pwsh
# Run cosmic-ray mutation testing end-to-end and generate TESTABLE metrics reports.

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot/..

Write-Host "==> Installing dependencies"
python -m pip install -e ".[dev]" -q

Write-Host "==> Running pytest baseline (must pass before mutating)"
python -m pytest tests -q

Write-Host "==> Cosmic Ray baseline (confirms tests pass unmutated)"
cosmic-ray baseline cosmic-ray.toml

Write-Host "==> Initializing mutation session"
if (Test-Path session.sqlite) { Remove-Item session.sqlite -Force }
cosmic-ray init cosmic-ray.toml session.sqlite

Write-Host "==> Executing mutations (this may take a few minutes)"
cosmic-ray exec cosmic-ray.toml session.sqlite

Write-Host "==> Cosmic Ray summary"
cr-rate session.sqlite
cr-report session.sqlite --surviving-only

Write-Host "==> Generating TESTABLE metrics report (fails the build if any gate is not met)"
python scripts/metrics_reporter.py --session session.sqlite --fail-on-gate

Write-Host "==> Exporting TESTABLE platform gate file (cosmic-ray/0/cosmic_ray.json)"
python scripts/export_testable_cosmic_ray.py --fail-on-gate

Write-Host "==> Done. See reports/metrics-report.md for the full breakdown."
Write-Host "    Commit cosmic-ray/0/cosmic_ray.json so the TESTABLE dashboard picks up the latest scores."
