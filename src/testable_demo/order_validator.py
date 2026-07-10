"""Order validation with nested conditions and edge-case handling."""

MAX_QUANTITY = 100
MEMBER_DISCOUNT_THRESHOLD = 50.0
STANDARD_APPROVAL_THRESHOLD = 100.0


def validate_quantity(quantity: int) -> bool:
    """Return True when quantity is within the allowed purchase limits."""
    return 0 < quantity <= MAX_QUANTITY


def validate_order(total: float, item_count: int, is_member: bool) -> str:
    """Validate an order and return its approval status."""
    if item_count <= 0 or total <= 0:
        return "rejected"

    if is_member:
        if total > MEMBER_DISCOUNT_THRESHOLD:
            return "approved_with_discount"
        return "approved_member"

    if total > STANDARD_APPROVAL_THRESHOLD:
        return "approved_standard"
    return "pending_review"
