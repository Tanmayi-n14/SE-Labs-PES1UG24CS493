import pytest
from blood_donation_screening import process_donor_cohort, verify_storage_centrifuge


# ==========================================
# Tests for process_donor_cohort
# ==========================================

def test_invalid_cohorts_input():
    # Not a list
    with pytest.raises(ValueError, match="Invalid cohort list or volume"):
        process_donor_cohort("not a list", 450)
    # Invalid volume <= 0
    with pytest.raises(ValueError, match="Invalid cohort list or volume"):
        process_donor_cohort([], 0)


def test_clinic_not_registered():
    cohorts = [
        {"clinic_registered": False, "donors": [{"age": 25, "weight_kg": 65, "hb": 14.0}]}
    ]
    result = process_donor_cohort(cohorts, 450)
    assert result == {"collected_ml": 0, "status": "ZERO_YIELD"}


def test_age_and_weight_deferrals():
    cohorts = [
        {
            "clinic_registered": True,
            "fast_track": False,
            "donors": [
                {"age": 16, "weight_kg": 60, "hb": 14.0},  # age < 17
                {"age": 25, "weight_kg": 45, "hb": 14.0},  # weight < 50
            ],
        }
    ]
    result = process_donor_cohort(cohorts, 450)
    assert result == {"collected_ml": 0, "status": "ZERO_YIELD"}


def test_hemoglobin_high_altitude_and_fast_track():
    cohorts = [
        {
            "clinic_registered": True,
            "type": "high_altitude",
            "fast_track": True,
            "donors": [
                {"age": 30, "weight_kg": 70, "hb": 15.0},  # accepted -> 450
                {"age": 28, "weight_kg": 65, "hb": 11.0},  # hb < 12.5 -> breaks & resets total to 0
                {"age": 40, "weight_kg": 80, "hb": 14.0},  # skipped due to break
            ],
        }
    ]
    result = process_donor_cohort(cohorts, 450)
    # total collected resets to 0, then fast_track adds 50
    assert result == {"collected_ml": 50, "status": "ACCEPTED"}


def test_hemoglobin_low_standard_and_high_hb():
    cohorts = [
        {
            "clinic_registered": True,
            "type": "standard",
            "fast_track": False,
            "donors": [
                {"age": 30, "weight_kg": 70, "hb": 11.5},  # hb < 12.5 in standard cohort
                {"age": 32, "weight_kg": 65, "hb": 19.0},  # hb > 18.0
                {"age": 25, "weight_kg": 60, "hb": 14.0},  # accepted
            ],
        }
    ]
    result = process_donor_cohort(cohorts, 450)
    assert result == {"collected_ml": 450, "status": "ACCEPTED"}


def test_high_deferral_status():
    # 5 donors deferred -> deferred_count > 4
    cohorts = [
        {
            "clinic_registered": True,
            "donors": [
                {"age": 15, "weight_kg": 60, "hb": 14.0},
                {"age": 15, "weight_kg": 60, "hb": 14.0},
                {"age": 15, "weight_kg": 60, "hb": 14.0},
                {"age": 15, "weight_kg": 60, "hb": 14.0},
                {"age": 15, "weight_kg": 60, "hb": 14.0},
            ],
        }
    ]
    result = process_donor_cohort(cohorts, 450)
    assert result == {"collected_ml": 0, "status": "HIGH_DEFERRAL"}


# ==========================================
# Tests for verify_storage_centrifuge
# ==========================================

def test_centrifuge_no_data():
    assert verify_storage_centrifuge([]) == "NO_DATA"


def test_centrifuge_abort_spin():
    # Two consecutive RPMs < 3000
    runs = [[3200, 2800, 2900, 3100]]
    assert verify_storage_centrifuge(runs) == "ABORT_SPIN"


def test_centrifuge_stable_with_isolated_drop():
    # Single drop reset by recovery >= 3000
    runs = [
        [3100, 2900, 3200, 2800, 3500],
        [3400, 3300]
    ]
    assert verify_storage_centrifuge(runs) == "STABLE"