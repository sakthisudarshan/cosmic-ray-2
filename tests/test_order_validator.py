import pytest

from testable_demo.order_validator import validate_order, validate_quantity


class TestValidateQuantity:
    @pytest.mark.parametrize("quantity", [0, -1, -10])
    def test_non_positive_rejected(self, quantity):
        assert validate_quantity(quantity) is False

    @pytest.mark.parametrize("quantity", [101, 150])
    def test_over_limit_rejected(self, quantity):
        assert validate_quantity(quantity) is False

    def test_at_lower_boundary(self):
        assert validate_quantity(1) is True

    def test_at_upper_boundary(self):
        assert validate_quantity(100) is True

    def test_mid_range(self):
        assert validate_quantity(50) is True


class TestValidateOrder:
    def test_negative_total_rejected(self):
        assert validate_order(-1, 1, False) == "rejected"

    def test_zero_total_rejected(self):
        assert validate_order(0, 1, False) == "rejected"

    def test_smallest_positive_total_allowed(self):
        assert validate_order(0.01, 1, False) == "pending_review"

    def test_zero_items_rejected(self):
        assert validate_order(10, 0, False) == "rejected"

    def test_negative_item_count_rejected(self):
        assert validate_order(10, -1, False) == "rejected"

    def test_zero_total_and_zero_items_rejected(self):
        assert validate_order(0, 0, False) == "rejected"

    def test_member_below_threshold(self):
        assert validate_order(49.99, 1, True) == "approved_member"

    def test_member_at_threshold_exactly(self):
        assert validate_order(50, 1, True) == "approved_member"

    def test_member_just_above_threshold(self):
        assert validate_order(50.01, 1, True) == "approved_with_discount"

    def test_member_high_total(self):
        assert validate_order(500, 1, True) == "approved_with_discount"

    def test_non_member_below_standard_threshold(self):
        assert validate_order(99.99, 1, False) == "pending_review"

    def test_non_member_at_standard_threshold_exactly(self):
        assert validate_order(100, 1, False) == "pending_review"

    def test_non_member_just_above_standard_threshold(self):
        assert validate_order(100.01, 1, False) == "approved_standard"

    def test_non_member_high_total(self):
        assert validate_order(1000, 1, False) == "approved_standard"
