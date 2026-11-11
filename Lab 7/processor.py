import math
from numbers import Real


INCLUDED_GB = {"basic": 2, "standard": 5, "premium": 10}


def _is_finite_number(value):
    return (
        isinstance(value, Real)
        and not isinstance(value, bool)
        and math.isfinite(value)
    )


def overage_charge(plan, data_gb, is_roaming, is_loyal):
    if not isinstance(plan, str) or plan not in INCLUDED_GB:
        raise ValueError("unknown plan")
    if not _is_finite_number(data_gb) or data_gb < 0:
        raise ValueError("data usage must be a finite non-negative number")
    if type(is_roaming) is not bool or type(is_loyal) is not bool:
        raise ValueError("roaming and loyalty flags must be booleans")

    included = INCLUDED_GB[plan]
    if is_loyal and plan != "premium":
        included += 1
    extra = data_gb - included
    if extra <= 0:
        return 0
    if is_roaming:
        rate = 40
    else:
        rate = 15
    if extra > 10:
        rate = rate + 10
        if is_roaming:
            rate += 5
    return extra * rate


def recharge_allowed(amount, pending_recharges, is_kyc_pending):
    if not _is_finite_number(amount) or amount < 0:
        raise ValueError("amount must be a finite non-negative number")
    if type(pending_recharges) is not int or pending_recharges < 0:
        raise ValueError("pending recharges must be a non-negative integer")
    if type(is_kyc_pending) is not bool:
        raise ValueError("KYC pending flag must be a boolean")

    if is_kyc_pending:
        return amount <= 200
    if amount > 2000:
        return False
    return pending_recharges <= 2


def validity_status(days_left, is_prepaid, has_addon):
    if type(days_left) is not int:
        raise ValueError("days left must be an integer")
    if type(is_prepaid) is not bool or type(has_addon) is not bool:
        raise ValueError("prepaid and add-on flags must be booleans")

    if is_prepaid:
        cutoff = 0
    else:
        cutoff = 3
    if has_addon:
        cutoff += 2
    if days_left >= cutoff:
        return "active"
    elif days_left >= cutoff - 15:
        return "grace"
    return "expired"
