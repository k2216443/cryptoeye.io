from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
from .utils import wei_to_eth, pow10

@dataclass
class Reason:
    key: str
    delta: int
    summary: str
    details: Dict[str, Any]

# ---- individual rules return (delta, Reason) ----
def rule_empty_wallet(has_history: bool, balance_eth: float) -> Tuple[int, Reason]:
    is_empty = (not has_history) and (balance_eth == 0.0)
    d = -10 if is_empty else 0
    return d, Reason("empty_unused", d, "Empty and unused address" if is_empty else "Not empty/unused",
                     {"has_history": has_history, "balance_eth": balance_eth, "empty_wallet": is_empty})

def rule_no_history(has_history: bool) -> Tuple[int, Reason]:
    d = 0 if has_history else -15
    return d, Reason("no_history", d, "No on-chain history" if not has_history else "Has history",
                     {"has_history": has_history})

def rule_age(now: int, first_ts: Optional[int]) -> Tuple[int, Reason]:
    if first_ts is None:
        return 0, Reason("age", 0, "Age unknown", {"age_days": None})
    age_days = (now - first_ts) / 86400
    d = -10 if age_days < 7 else (-5 if age_days < 30 else 0)
    return d, Reason("age", d, "Address age", {"age_days": round(age_days, 2)})

def rule_inactivity(now: int, last_ts: Optional[int]) -> Tuple[int, Reason]:
    if last_ts is None:
        return 0, Reason("inactivity", 0, "Inactivity unknown", {"inactive_days": None})
    inactive_days = (now - last_ts) / 86400
    d = -5 if inactive_days > 180 else 0
    return d, Reason("inactivity", d, "Inactivity window", {"inactive_days": round(inactive_days, 2)})

def rule_fail_ratio(txs: List[Dict[str, Any]]) -> Tuple[int, Reason]:
    if not txs:
        return 0, Reason("failed_tx_ratio", 0, "No external tx", {"ratio": 0.0, "total": 0})
    total = len(txs)
    failed = sum(1 for t in txs if t.get("isError") == "1")
    ratio = failed / total
    d = -10 if ratio > 0.5 else (-5 if ratio > 0.2 else 0)
    return d, Reason("failed_tx_ratio", d, "Failed tx ratio", {"ratio": round(ratio, 3), "failed": failed, "total": total})

def rule_unique_cps(address: str, txs_90d: List[Dict[str, Any]]) -> Tuple[int, Reason]:
    lower = address.lower()
    cps = set()
    for t in txs_90d:
        frm = t.get("from", "").lower(); to = t.get("to", "").lower()
        if frm == lower and to: cps.add(to)
        elif to == lower and frm: cps.add(frm)
    unique = len(cps)
    d = -5 if unique < 3 and len(txs_90d) >= 3 else 0
    return d, Reason("unique_cps_90d", d, "Unique counterparties (90d)", {"unique": unique, "txs_90d": len(txs_90d)})

def rule_dust_eth(address: str, txs_90d: List[Dict[str, Any]]) -> Tuple[int, Reason]:
    lower = address.lower()
    dust = sum(1 for t in txs_90d if t.get("to","").lower()==lower and wei_to_eth(t.get("value","0")) < 0.001)
    d = -5 if dust > 20 else 0
    return d, Reason("dust_incoming_eth_90d", d, "ETH dust incoming (90d)", {"count": dust})

def rule_dust_tokens(address: str, token_txs_90d: List[Dict[str, Any]]) -> Tuple[int, Reason]:
    lower = address.lower()
    tiny = 0
    for t in token_txs_90d:
        if t.get("to","").lower()!=lower: continue
        dec = pow10(t.get("tokenDecimal", 0))
        try: amt = int(t.get("value","0")) / dec
        except Exception: amt = 0.0
        if amt < 0.001: tiny += 1
    d = -5 if tiny > 20 else 0
    return d, Reason("dust_incoming_tokens_90d", d, "Token dust incoming (90d)", {"count": tiny})

def rule_token_only_empty(has_eth_history: bool, eth_balance: float, token_txs: List[Dict[str, Any]]) -> Tuple[int, Reason]:
    token_activity = len(token_txs) > 0
    token_only = (not has_eth_history) and (eth_balance == 0.0) and token_activity
    d = -5 if token_only else 0
    return d, Reason("token_only_empty", d, "Token-only activity without ETH",
                     {"token_activity": token_activity, "eth_balance": eth_balance, "has_eth_history": has_eth_history})

def rule_contract_verified(meta: Dict[str, Any]) -> Tuple[int, Reason]:
    is_contract = bool(meta.get("ContractName"))
    if not is_contract:
        return 0, Reason("contract_verified", 0, "EOA (not a contract)", {"is_contract": False})
    abi = meta.get("ABI",""); src = meta.get("SourceCode","")
    verified = bool(src) and "Contract source code not verified" not in abi
    d = 5 if verified else -20
    return d, Reason("contract_verified", d, "Contract verification", {"verified": verified, "is_contract": True})

def rule_contract_proxy(meta: Dict[str, Any]) -> Tuple[int, Reason]:
    is_contract = bool(meta.get("ContractName"))
    if not is_contract:
        return 0, Reason("contract_proxy", 0, "EOA (not a contract)", {"is_contract": False})
    proxy = meta.get("Proxy","0") == "1"
    d = -5 if proxy else 0
    return d, Reason("contract_proxy", d, "Contract proxy", {"proxy": proxy})
