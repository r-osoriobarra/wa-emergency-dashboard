"""
Helper functions used across modules
"""

def to_float(value):
    if value is None or value == '':
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None