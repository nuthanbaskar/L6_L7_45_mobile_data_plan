import pytest
from hypothesis import given, strategies as st

from processor import overage_charge, recharge_allowed, validity_status


PLANS = {"basic": 2, "standard": 5, "premium": 10}


@given(
    plan=st.sampled_from(tuple(PLANS)),
    data_gb=st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False),
    is_roaming=st.booleans(),
    is_loyal=st.booleans(),
)
def test_overage_charge_matches_plan_rate(plan, data_gb, is_roaming, is_loyal):
    included = PLANS[plan] + int(is_loyal and plan != "premium")
    extra = max(0, data_gb - included)
    rate = 40 if is_roaming else 15
    if extra > 10:
        rate += 10 + (5 if is_roaming else 0)
    expected = 0 if extra == 0 else extra * rate
    assert overage_charge(plan, data_gb, is_roaming, is_loyal) == expected


@given(
    invalid_data=st.one_of(
        st.booleans(),
        st.text(),
        st.sampled_from((float("nan"), float("inf"), float("-inf"))),
    )
)
def test_overage_charge_rejects_invalid_usage(invalid_data):
    with pytest.raises(ValueError):
        overage_charge("basic", invalid_data, False, False)


@given(flag=st.one_of(st.integers(), st.text()))
def test_overage_charge_rejects_non_boolean_flags(flag):
    with pytest.raises(ValueError):
        overage_charge("basic", 1, flag, False)
    with pytest.raises(ValueError):
        overage_charge("basic", 1, False, flag)


@given(
    amount=st.integers(min_value=0, max_value=5000),
    pending_recharges=st.integers(min_value=0, max_value=10),
    is_kyc_pending=st.booleans(),
)
def test_recharge_allowed_matches_limits(amount, pending_recharges, is_kyc_pending):
    expected = (
        amount <= 200
        if is_kyc_pending
        else amount <= 2000 and pending_recharges <= 2
    )
    assert recharge_allowed(amount, pending_recharges, is_kyc_pending) is expected


@given(amount=st.integers(max_value=-1))
def test_recharge_rejects_negative_amount(amount):
    with pytest.raises(ValueError):
        recharge_allowed(amount, 0, False)


@given(pending_recharges=st.integers(max_value=-1))
def test_recharge_rejects_negative_pending_count(pending_recharges):
    with pytest.raises(ValueError):
        recharge_allowed(100, pending_recharges, False)


@given(
    invalid_amount=st.one_of(
        st.booleans(),
        st.text(),
        st.sampled_from((float("nan"), float("inf"), float("-inf"))),
    )
)
def test_recharge_rejects_invalid_amount(invalid_amount):
    with pytest.raises(ValueError):
        recharge_allowed(invalid_amount, 0, False)


@given(pending_recharges=st.one_of(st.booleans(), st.floats()))
def test_recharge_rejects_non_integer_pending_count(pending_recharges):
    with pytest.raises(ValueError):
        recharge_allowed(100, pending_recharges, False)


@given(
    days_left=st.integers(min_value=-1000, max_value=1000),
    is_prepaid=st.booleans(),
    has_addon=st.booleans(),
)
def test_validity_status_matches_cutoffs(days_left, is_prepaid, has_addon):
    cutoff = (0 if is_prepaid else 3) + (2 if has_addon else 0)
    if days_left >= cutoff:
        expected = "active"
    elif days_left >= cutoff - 15:
        expected = "grace"
    else:
        expected = "expired"
    assert validity_status(days_left, is_prepaid, has_addon) == expected


@given(days_left=st.booleans())
def test_validity_rejects_boolean_day_counts(days_left):
    with pytest.raises(ValueError):
        validity_status(days_left, True, False)


@given(days_left=st.floats(allow_nan=False, allow_infinity=False))
def test_validity_rejects_fractional_day_counts(days_left):
    if days_left.is_integer():
        return
    with pytest.raises(ValueError):
        validity_status(days_left, True, False)


@given(flag=st.one_of(st.integers(), st.text()))
def test_validity_rejects_non_boolean_flags(flag):
    with pytest.raises(ValueError):
        validity_status(1, flag, False)
    with pytest.raises(ValueError):
        validity_status(1, True, flag)
