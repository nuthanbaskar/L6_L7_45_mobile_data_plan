import pytest

from mobile_data_plan import overage_charge, recharge_allowed, validity_status


def test_overage_charge_validation_and_allowance():
    with pytest.raises(ValueError, match="unknown plan"):
        overage_charge("unlimited", 1, False, False)
    with pytest.raises(ValueError, match="invalid data usage"):
        overage_charge("basic", -1, False, False)

    assert overage_charge("standard", 5, False, False) == 0
    assert overage_charge("basic", 3, False, True) == 0
    assert overage_charge("premium", 11, False, True) == 15


def test_overage_charge_roaming_and_high_usage_rates():
    assert overage_charge("basic", 4, True, False) == 80
    assert overage_charge("basic", 13, False, False) == 275
    assert overage_charge("basic", 13, True, False) == 605


def test_recharge_allowed_limits():
    assert recharge_allowed(200, 99, True) is True
    assert recharge_allowed(201, 0, True) is False
    assert recharge_allowed(2001, 0, False) is False
    assert recharge_allowed(2000, 2, False) is True
    assert recharge_allowed(500, 3, False) is False


def test_validity_status_states():
    assert validity_status(0, True, False) == "active"
    assert validity_status(1, False, True) == "grace"
    assert validity_status(-15, True, False) == "grace"
    assert validity_status(-16, True, False) == "expired"