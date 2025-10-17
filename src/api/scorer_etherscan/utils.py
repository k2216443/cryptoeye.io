from __future__ import annotations
import time
from typing import Any

def now() -> int:
    return int(time.time())

def clamp(x: int, lo: int = 0, hi: int = 100) -> int:
    return max(lo, min(hi, x))

def wei_to_eth(wei: str) -> float:
    try: return int(wei) / 1e18
    except Exception: return 0.0

def pow10(n: Any) -> int:
    try:
        n = int(n)
        return 10 ** n if 0 <= n <= 77 else 1
    except Exception:
        return 1

