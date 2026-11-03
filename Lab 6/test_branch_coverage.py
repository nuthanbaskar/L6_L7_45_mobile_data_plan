import pytest

from mobile_data_plan import overage_charge, recharge_allowed, validity_status


@pytest.mark.parametrize(
    ("plan", "data_gb", "is_roaming", "is_loyal", "expected"),
    [
        ("standard", 5, False, False, 0),
        ("basic", 2, False, True, 0),
        ("premium", 10, False, True, 0),
        ("basic", 3, False, False, 15),
        ("basic", 3, True, False, 40),
        ("basic", 13, False, False, 275),
        ("basic", 13, True, False, 605),
    ],
)
def test_overage_charge_decision_branches(plan, data_gb, is_roaming, is_loyal, expected):
    assert overage_charge(plan, data_gb, is_roaming, is_loyal) == expected


@pytest.mark.parametrize(
    ("plan", "data_gb", "message"),
    [("unknown", 0, "unknown plan"), ("basic", -1, "invalid data usage")],
)
def test_overage_charge_validation_branches(plan, data_gb, message):
    with pytest.raises(ValueError, match=message):
        overage_charge(plan, data_gb, False, False)


@pytest.mark.parametrize(
    ("amount", "pending_recharges", "is_kyc_pending", "expected"),
    [
        (200, 3, True, True),
        (201, 0, True, False),
        (2001, 0, False, False),
        (2000, 2, False, True),
        (500, 3, False, False),
    ],
)
def test_recharge_allowed_decision_branches(
    amount, pending_recharges, is_kyc_pending, expected
):
    assert recharge_allowed(amount, pending_recharges, is_kyc_pending) is expected


@pytest.mark.parametrize(
    ("days_left", "is_prepaid", "has_addon", "expected"),
    [
        (0, True, False, "active"),
        (-1, True, False, "grace"),
        (-15, True, False, "grace"),
        (-16, True, False, "expired"),
        (3, False, False, "active"),
        (2, False, False, "grace"),
        (5, False, True, "active"),
        (4, False, True, "grace"),
        (-11, False, True, "expired"),
    ],
)
def test_validity_status_decision_branches(days_left, is_prepaid, has_addon, expected):
    assert validity_status(days_left, is_prepaid, has_addon) == expected