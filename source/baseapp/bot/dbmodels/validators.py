import re

def validate_username(username: str) -> bool:
    return re.fullmatch(r"^[0-9A-Za-z]{5,30}$", username) != None

def validate_name(name: str) -> bool:
    return re.fullmatch(r"^[a-zA-Z]{5,30}$", name) != None

def validate_pass(password: str) -> bool:
    reg = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,20}$"
    pat = re.compile(reg)
    return re.search(pat, password) != None