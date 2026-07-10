# Metrics Mapping Reference

Extracted from `Testable_Strategy_Metrics_Mapping_v0.2.xlsx`, sheet **White Box**,
`L2 Testing Type = Mutation Testing`, `L3 Technique = Mutation Score`,
**Python primary tool = `cosmic-ray`** (secondary Python tool in the sheet: `mutmut`).

| Row | L4 Classification | L5 Metric | Derivation (Python / cosmic-ray) | Raw Measurement Formula | Expected Value / Threshold | Normalisation Formula (0–100) | Execution Frequency |
|-----|--------------------|-----------|-----------------------------------|--------------------------|------------------------------|--------------------------------|----------------------|
| 1 | Fault Detection Capability | Logic Error Sensitivity | `(total jobs - surviving mutants) / total jobs` | Sensitivity Score = (Survived Mutants caught by assertion-only tests / Total Survived Mutants) × 100 | >= 70% of survived mutants caught by targeted assertion tests | Score = Sensitivity Score % [gate at 70%] | Daily / Per Sprint |
| 2 | Test Coverage Quality Validation | Test Rigor Assessment | `(total jobs - surviving mutants) / total jobs` | Rigor Score = (Killed Mutants / Total Mutants Generated) × 100 | >= 70% overall mutant kill rate | Score = Rigor Score % [gate at 70%] | Daily / Per Sprint |
| 3 | Test Case Improvement Identification | Weak Spot Localization | `surviving mutants` | Weak Spot Count = Count(Modules where Mutation Kill Rate < 50%) | 0 modules with mutation kill rate below 50% | MAX(0, 100 − (Weak_Spot_Count × 15)) | Daily / Per Sprint |
| 4 | Edge Case Detection | Boundary Mutant Analysis | `count(mutation where mutator contains "Conditionals") / total_mutations` | Boundary Kill Rate % = (Boundary Operator Mutants Killed / Total Boundary Mutants) × 100 | >= 80% of boundary operator mutants killed | Score = Boundary Kill Rate % [gate at 80%] | Daily / Per Sprint |
| 5 | Fault Detection Capability | Change Resilience Testing | `(total jobs - surviving mutants) / total jobs` | Resilience Score = (Post-Change Mutation Kill Rate / Pre-Change Mutation Kill Rate) × 100 | Resilience Score >= 95% (< 5% kill rate degradation after change) | Score = MIN(100, Resilience_Score) | Daily / Per Sprint |
| 6 | Test Coverage Quality Validation | Semantic Integrity Check | `killed_mutations / total_mutations` | Semantic Pass Rate % = (Mutants testing semantic behavior killed / Total Semantic Mutants) × 100 | >= 75% semantic mutant kill rate | Score = Semantic Pass Rate % [gate at 75%] | Daily / Per Sprint |
| 7 | Fault Detection Capability | Mutation Kill Rate % | `(killed_mutations / total_mutations) * 100` | Mutation Kill Rate % = (Killed Mutants / Total Non-Equivalent Mutants) × 100 | >= 70% mutation kill rate | Score = Mutation Kill Rate % [gate at 70%] | Daily / Per Sprint |

`scripts/metrics_reporter.py` implements all 7 rows above as metrics `M1`–`M7`
and writes `reports/mutation-score-gate.json` / `reports/metrics-report.md`
each time it runs against a cosmic-ray session, so every gate can be
independently re-verified against this table.
