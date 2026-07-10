"""Discount calculation with operator-sensitive comparisons."""

PERCENT_FLOOR = 0.0
PERCENT_CEILING = 100.0
LIGHT_TIER_MAX_KG = 5.0
MEDIUM_TIER_MAX_KG = 20.0
LIGHT_TIER_COST = 5.0
MEDIUM_TIER_COST = 12.0
HEAVY_TIER_COST = 25.0


def apply_percentage_discount(price: float, percent: float) -> float:
    """Apply a percentage discount to price, clamping percent to [0, 100]."""
    clamped_percent = min(max(percent, PERCENT_FLOOR), PERCENT_CEILING)
    discount_amount = price * clamped_percent / PERCENT_CEILING
    discounted = price - discount_amount
    return max(0.0, discounted)


def tiered_shipping(weight_kg: float) -> float:
    """Return shipping cost based on weight boundaries."""
    if weight_kg <= 0:
        return 0.0
    if weight_kg <= LIGHT_TIER_MAX_KG:
        return LIGHT_TIER_COST
    if weight_kg <= MEDIUM_TIER_MAX_KG:
        return MEDIUM_TIER_COST
    return HEAVY_TIER_COST
