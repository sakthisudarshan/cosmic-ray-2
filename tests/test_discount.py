import pytest

from testable_demo.discount import apply_percentage_discount, tiered_shipping


class TestApplyPercentageDiscount:
    def test_no_discount(self):
        assert apply_percentage_discount(100, 0) == 100.0

    def test_full_discount(self):
        assert apply_percentage_discount(100, 100) == 0.0

    def test_half_discount(self):
        assert apply_percentage_discount(80, 50) == 40.0

    def test_third_discount_exact_fraction(self):
        assert apply_percentage_discount(100, 25) == 75.0

    def test_fractional_percent(self):
        assert apply_percentage_discount(200, 12.5) == 175.0

    def test_negative_percent_clamped_to_floor(self):
        assert apply_percentage_discount(80, -0.01) == 80.0

    def test_percent_above_ceiling_clamped(self):
        assert apply_percentage_discount(80, 100.01) == 0.0

    def test_percent_just_below_ceiling(self):
        assert apply_percentage_discount(100, 99) == 1.0

    def test_percent_at_ceiling_exactly(self):
        assert apply_percentage_discount(100, 100) == 0.0

    def test_percent_at_floor_exactly(self):
        assert apply_percentage_discount(100, 0) == 100.0

    def test_zero_price(self):
        assert apply_percentage_discount(0, 50) == 0.0

    def test_small_positive_discount(self):
        assert apply_percentage_discount(200, 1) == 198.0

    def test_negative_price_floors_result_at_zero(self):
        # Guards the "discounted < 0" floor: with a negative price the
        # discount subtraction would otherwise go negative.
        assert apply_percentage_discount(-10, 50) == 0.0

    def test_negative_price_no_discount_stays_negative_free_of_floor(self):
        # percent == 0 -> discount_amount == 0 -> discounted == price (-10),
        # which is < 0, so the floor still applies.
        assert apply_percentage_discount(-10, 0) == 0.0

    def test_slightly_negative_discount_result_still_floored(self):
        # discounted lands strictly between -1 and 0 to distinguish the
        # floor guard from off-by-one comparisons against it.
        assert apply_percentage_discount(-1, 50) == 0.0

    def test_small_positive_discounted_result_not_floored(self):
        # discounted lands strictly between 0 and 1 to distinguish the
        # floor guard from off-by-one comparisons against it.
        assert apply_percentage_discount(1, 50) == 0.5

    def test_non_exact_division_uses_true_division(self):
        # 100 * 33.5 = 3350; true division by 100 gives 33.5, whereas floor
        # division would give 33.0 and change the discounted result.
        assert apply_percentage_discount(100, 33.5) == 66.5


class TestTieredShipping:
    @pytest.mark.parametrize(
        "weight,expected",
        [
            (0, 0.0),
            (-1, 0.0),
            (0.01, 5.0),
            (5, 5.0),
            (5.01, 12.0),
            (20, 12.0),
            (20.01, 25.0),
            (100, 25.0),
        ],
    )
    def test_weight_boundaries(self, weight, expected):
        assert tiered_shipping(weight) == expected
