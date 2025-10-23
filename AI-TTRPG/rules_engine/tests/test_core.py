from rules_engine.core import perform_skill_check
import random

def test_perform_skill_check_success():
    random.seed(0)  # Set seed for predictable random number
    success, roll = perform_skill_check(stat_modifier=5, skill_rank=5, dc=10)
    assert success is True
    assert roll == 13

def test_perform_skill_check_failure():
    random.seed(1)  # Set seed for predictable random number
    success, roll = perform_skill_check(stat_modifier=0, skill_rank=0, dc=20)
    assert success is False
    assert roll == 5
