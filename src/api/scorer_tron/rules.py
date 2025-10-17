from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
from .utils import sun_to_trx, pow10

@dataclass
class Reason:
    key: str
    delta: int
    summary: str
    details: Dict[str, Any]

# ---- TRC rules (same semantics as ETH version) ----
def rule_empty_wallet(has_history: bool, trx_balance: float) -> Tuple[int, Reason]:
    is_empty = (not has_history) and (trx_balance == 0.0)
    d = -10 if is_empty else 0
    return d, Reason("empty_unused", d, "Empty and unused address" if is_empty else "Not empty/unused",
                     {"has_history": has_history, "trx_balance": trx_balance, "empty_wallet": is_empty})

def rule_no_history(has_history: bool) -> Tuple[int, Reason]:
    d = 0 if has_history else -15
    return d, Reason("no_history", d, "No on-chain history" if not has_history else "Has history",
                     {"has_history": has_history})

def rule_age(now: int, first_ts_ms: Optional[int]) -> Tuple[int, Reason]:
    if first_ts_ms is None:
        return 0, Reason("age", 0, "Age unknown", {"age_days": None})
    age_days = (now - (first_ts_ms // 1000)) / 86400
    d = -10 if age_days < 7 else (-5 if age_days < 30 else 0)
    return d, Reason("age", d, "Address age", {"age_days": round(age_days, 2)})

def rule_inactivity(now: int, last_ts_ms: Optional[int]) -> Tuple[int, Reason]:
    if last_ts_ms is None:
        return 0, Reason("inactivity", 0, "Inactivity unknown", {"inactive_days": None})
    inactive_days = (now - (last_ts_ms // 1000)) / 86400
    d = -5 if inactive_days > 180 else 0
    return d, Reason("inactivity", d, "Inactivity window", {"inactive_days": round(inactive_days, 2)})

def rule_fail_ratio_trx(txs: List[Dict[str, Any]]) -> Tuple[int, Reason]:
    if not txs:
        return 0, Reason("failed_tx_ratio", 0, "No TRX tx", {"ratio": 0.0, "total": 0})
    total = len(txs)
    failed = sum(1 for t in txs if str(t.get("ret", [{}])[0].get("contractRet", "")).upper() not in ("SUCCESS",))
    ratio = failed / total
    d = -10 if ratio > 0.5 else (-5 if ratio > 0.2 else 0)
    return d, Reason("failed_tx_ratio", d, "Failed tx ratio", {"ratio": round(ratio, 3), "failed": failed, "total": total})

def rule_unique_cps(address: str, txs_90d: List[Dict[str, Any]]) -> Tuple[int, Reason]:
    lower = address
    cps = set()
    for t in txs_90d:
        frm = t.get("ownerAddress", "")
        to = t.get("toAddress", "") or t.get("contractData", {}).get("to_address", "")
        if frm == lower and to: cps.add(to)
        elif to == lower and frm: cps.add(frm)
    unique = len(cps)
    d = -5 if unique < 3 and len(txs_90d) >= 3 else 0
    return d, Reason("unique_cps_90d", d, "Unique counterparties (90d)", {"unique": unique, "txs_90d": len(txs_90d)})

def rule_dust_trx(address: str, txs_90d: List[Dict[str, Any]]) -> Tuple[int, Reason]:
    # TransferContract 'amount' in SUN; consider < 1000 SUN (~0.001 TRX) as dust
    lower = address
    dust = 0
    for t in txs_90d:
        to = t.get("toAddress", "") or t.get("contractData", {}).get("to_address", "")
        if to != lower: continue
        amt_sun = t.get("contractData", {}).get("amount", None)
        if amt_sun is None: continue
        try:
            amt_trx = sun_to_trx(int(amt_sun))
            if amt_trx < 0.001: dust += 1
        except Exception:
            pass
    d = -5 if dust > 20 else 0
    return d, Reason("dust_incoming_trx_90d", d, "TRX dust incoming (90d)", {"count": dust})

def rule_dust_trc20(address: str, trc20_90d: List[Dict[str, Any]]) -> Tuple[int, Reason]:
    lower = address
    tiny = 0
    for t in trc20_90d:
        if t.get("to", "") != lower: continue
        dec = pow10(t.get("token_info", {}).get("decimals", 0))
        try:
            amt = int(t.get("value", "0")) / dec
        except Exception:
            amt = 0.0
        if amt < 0.001: tiny += 1
    d = -5 if tiny > 20 else 0
    return d, Reason("dust_incoming_trc20_90d", d, "TRC20 dust incoming (90d)", {"count": tiny})

def rule_token_only_empty(has_trx_history: bool, trx_balance: float, trc20_txs: List[Dict[str, Any]]) -> Tuple[int, Reason]:
    token_activity = len(trc20_txs) > 0
    token_only = (not has_trx_history) and (trx_balance == 0.0) and token_activity
    d = -5 if token_only else 0
    return d, Reason("token_only_empty", d, "Token-only activity without TRX",
                     {"token_activity": token_activity, "trx_balance": trx_balance, "has_trx_history": has_trx_history})

def rule_contract_verified(verified: bool | None) -> Tuple[int, Reason]:
    if verified is None:
        return 0, Reason("contract_verified", 0, "Verification unknown", {"verified": None})
    d = 5 if verified else -20
    return d, Reason("contract_verified", d, "Contract verification", {"verified": verified})

def rule_contract_proxy(_meta: Dict[str, Any]) -> Tuple[int, Reason]:
    # Proxy detection is not standardized on Tron via public APIs; neutral.
    return 0, Reason("contract_proxy", 0, "Proxy unknown", {})
