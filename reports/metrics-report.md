# TESTABLE Mutation Testing Metrics Report

- **Tool:** cosmic-ray
- **Session:** `session.sqlite`
- **Total Mutants:** 191
- **Killed:** 191  |  **Survived:** 0  |  **Incompetent (excluded):** 0
- **Mutation Kill Rate:** 100.00%
- **All Gates Passed:** YES

## Metrics (Testable_Strategy_Metrics_Mapping_v0.2 — White Box > Mutation Testing)

| ID | Classification | Metric | Score /100 | Gate | Status |
|----|-----------------|--------|-----------|------|--------|
| M1 | Fault Detection Capability | Logic Error Sensitivity | 100.00 | >= 70% | PASS |
| M2 | Test Coverage Quality Validation | Test Rigor Assessment | 100.00 | >= 70% | PASS |
| M3 | Test Case Improvement Identification | Weak Spot Localization | 100.00 | 0 modules with mutation kill rate below 50% | PASS |
| M4 | Edge Case Detection | Boundary Mutant Analysis | 100.00 | >= 80% | PASS |
| M5 | Fault Detection Capability | Change Resilience Testing | 100.00 | >= 95% | PASS |
| M6 | Test Coverage Quality Validation | Semantic Integrity Check | 100.00 | >= 75% | PASS |
| M7 | Fault Detection Capability | Mutation Kill Rate % | 100.00 | >= 70% | PASS |

## Module Kill Rates

- `calculator.py`: 100.00%
- `discount.py`: 100.00%
- `order_validator.py`: 100.00%

## Surviving Mutants (Weak Spots)

None — all mutants were killed.
