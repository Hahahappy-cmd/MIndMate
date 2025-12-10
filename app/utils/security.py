import secrets
import string
from datetime import datetime, timedelta

def generate_reset_token(length=32):
    
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def is_token_expired(expires_at: datetime) -> bool:
    
    return datetime.utcnow() > expires_at

def validate_password_strength(password: str) -> bool:
    
    if len(password) < 8:
        return False
    return True