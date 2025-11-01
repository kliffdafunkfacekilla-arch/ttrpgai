from rules_engine.app.core import calculate_skill_check
import random


def test_calculate_skill_check_success():
    random.seed(0)  # Set seed for predictable random number
    result = calculate_skill_check(stat_mod=5, skill_rank=5, dc=10)
    assert result.is_success is True
    assert result.roll_value == 13


def test_calculate_skill_check_failure():
    random.seed(1)  # Set seed for predictable random number
    result = calculate_skill_check(stat_mod=0, skill_rank=0, dc=20)
    assert result.is_success is False
    assert result.roll_value == 5
