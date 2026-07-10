"""Arithmetic helpers with boundary-sensitive logic."""

INVALID_SCORE_CEILING = 0
FAIL_CEILING = 50
PASS_CEILING = 70
MERIT_CEILING = 90


def clamp(value: float, minimum: float, maximum: float) -> float:
    """Restrict value to the inclusive range [minimum, maximum]."""
    return min(max(value, minimum), maximum)


def safe_divide(numerator: float, denominator: float) -> float:
    """Divide two numbers, returning 0.0 when denominator is zero."""
    if denominator == 0:
        return 0.0
    return numerator / denominator


def classify_score(score: int) -> str:
    """Map a numeric score to a letter grade using boundary thresholds."""
    if score < INVALID_SCORE_CEILING:
        return "invalid"
    if score < FAIL_CEILING:
        return "fail"
    if score < PASS_CEILING:
        return "pass"
    if score < MERIT_CEILING:
        return "merit"
    return "distinction"
