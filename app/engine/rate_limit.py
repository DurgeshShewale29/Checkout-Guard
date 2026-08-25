import time
from typing import Dict, Tuple

# In-memory store: {order_id: (timestamp, attempt_count)}
_rate_limits: Dict[str, Tuple[float, int]] = {}

MAX_ATTEMPTS_PER_ORDER = 5
COOLDOWN_SECONDS = 60

def check_rate_limit(order_id: str) -> bool:
    """
    Checks if the given order_id has exceeded the maximum allowed retry attempts.
    Returns True if rate limited (blocked), False otherwise.
    """
    now = time.time()
    if order_id in _rate_limits:
        last_attempt, count = _rate_limits[order_id]
        
        # If cooldown has passed, reset the count
        if now - last_attempt > COOLDOWN_SECONDS:
            _rate_limits[order_id] = (now, 1)
            return False
            
        if count >= MAX_ATTEMPTS_PER_ORDER:
            return True # Rate limited!
            
        _rate_limits[order_id] = (now, count + 1)
        return False
        
    _rate_limits[order_id] = (now, 1)
    return False

def reset_rate_limit(order_id: str):
    """Resets the limit for testing purposes."""
    if order_id in _rate_limits:
        del _rate_limits[order_id]
