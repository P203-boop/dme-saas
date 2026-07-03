def check_eligibility(insurance_id: str) -> bool:
    """
    Simple rules engine (MVP version)
    Later this becomes API + AI scoring layer
    """
    if not insurance_id:
        return False

    if insurance_id[-1].isdigit():
        return int(insurance_id[-1]) % 2 == 0

    return False
