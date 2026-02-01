import string
import random
import secrets


def generate_manager_password(length=8):
    chars = string.ascii_letters + string.digits
    return "".join(random.choice(chars) for _ in range(length))
def generate_verification_code(length=6):
    return ''.join(str(secrets.randbelow(10)) for _ in range(length))
    

