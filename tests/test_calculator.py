import pytest

from testable_demo.calculator import clamp, classify_score, safe_divide


class TestClamp:
    def test_below_minimum(self):
        assert clamp(-5, 0, 10) == 0

    def test_above_maximum(self):
        assert clamp(15, 0, 10) == 10

    def test_within_range(self):
        assert clamp(5, 0, 10) == 5

    def test_at_minimum_boundary(self):
        assert clamp(0, 0, 10) == 0

    def test_at_maximum_boundary(self):
        assert clamp(10, 0, 10) == 10

    def test_just_below_minimum(self):
        assert clamp(-0.01, 0, 10) == 0

    def test_just_above_maximum(self):
        assert clamp(10.01, 0, 10) == 10

    def test_fractional_within_range(self):
        assert clamp(5.5, 5, 10) == 5.5

    def test_negative_range(self):
        assert clamp(-10, -5, 0) == -5
        assert clamp(-3, -5, 0) == -3
        assert clamp(1, -5, 0) == 0


class TestSafeDivide:
    def test_normal_division(self):
        assert safe_divide(10, 2) == 5.0

    def test_non_integer_quotient(self):
        assert safe_divide(7, 2) == 3.5

    def test_zero_numerator(self):
        assert safe_divide(0, 5) == 0.0

    def test_zero_denominator(self):
        assert safe_divide(10, 0) == 0.0

    def test_negative_denominator(self):
        assert safe_divide(10, -2) == -5.0

    def test_negative_numerator(self):
        assert safe_divide(-9, 3) == -3.0

    def test_both_negative(self):
        assert safe_divide(-9, -3) == 3.0


class TestClassifyScore:
    @pytest.mark.parametrize(
        "score,expected",
        [
            (-1, "invalid"),
            (0, "fail"),
            (1, "fail"),
            (49, "fail"),
            (50, "pass"),
            (51, "pass"),
            (69, "pass"),
            (70, "merit"),
            (71, "merit"),
            (89, "merit"),
            (90, "distinction"),
            (91, "distinction"),
            (100, "distinction"),
        ],
    )
    def test_boundaries(self, score, expected):
        assert classify_score(score) == expected
