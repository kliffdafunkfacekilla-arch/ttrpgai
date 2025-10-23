import random

def perform_skill_check(stat_modifier: int, skill_rank: int, dc: int) -> tuple[bool, int]:
    """
    Performs a skill check by rolling a d20, adding modifiers, and comparing to a DC.
    """
    roll = random.randint(1, 20)
    total = roll + stat_modifier + skill_rank
    success = total >= dc
    return success, roll
