def validate_password_strength(v: str) -> str:
    if len(v) < 8:
        raise ValueError('Password must be at least 8 characters long')
    
    has_upper = any(c.isupper() for c in v)
    has_lower = any(c.islower() for c in v)
    has_digit = any(c.isdigit() for c in v)
    has_special = any(c in "!@#$%^&*(),.?\":{}|<>" for c in v)

    if not has_upper:
        raise ValueError('Password must contain at least one uppercase letter')
    if not has_lower:
        raise ValueError('Password must contain at least one lowercase letter')
    if not has_digit:
        raise ValueError('Password must contain at least one digit')
    if not has_special:
        raise ValueError('Password must contain at least one special character')        
    return v