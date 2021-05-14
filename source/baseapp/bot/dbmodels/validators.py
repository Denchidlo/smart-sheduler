import re

def validate_username(username: str) -> bool:
    return True if re.fullmatch(r"^[0-9a-zA-Z]{5, 30}$", username) != None else False

def validate_name(name: str) -> bool:
    return True if re.fullmatch(r"^[a-zA-Z]{5, 30}$", name) != None else False