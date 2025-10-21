from __future__ import annotations
import os
import time
import requests
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional, Tuple, Union

# ---------- config ----------
ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")
ETHERSCAN_API_URL = "https://api.etherscan.io/v2/api"
BASE_SCORE = 50

# ---------- util ----------
def clamp(x: int, lo: int = 0, hi: int = 100) -> int:
    return max(lo, min(hi, x))

def wei_to_eth(wei: str) -> float:
    try:
        return int(wei) / 1e18
    except Exception:
        return 0.0

def pow10(n: int) -> int:
    try:
        n = int(n)
        if 0 <= n <= 77:  # safe bound
            return 10 ** n
    except Exception:
        pass
    return 1

@dataclass
class Reason:
    key: str
    delta: int
    summary: str
    details: Dict[str, Any]

# ---------- client ----------
class Etherscan:
    """
    Etherscan-backed wallet scorer with transparent per-rule breakdown.
    Only uses Etherscan endpoints:
      - account.balance
      - account.txlist
      - account.txlistinternal
      - account.tokentx
      - contract.getsourcecode
    """

    def __init__(self, chainid: int = 1, logger=None):
        self.chainid = chainid
        self.log = logger  # optional: your own logger with .debug/.error

    # --- low-level call ---
    def _call(self, params: Dict[str, Any]) -> Dict[str, Any]:
        q = dict(params)
        q["apikey"] = ETHERSCAN_API_KEY
        q["chainid"] = self.chainid
        if self.log:
            self.log.debug("etherscan_call", extra={"params": q})
        r = requests.get(ETHERSCAN_API_URL, params=q, timeout=20)
        data = r.json()
        if data.get("status") != "1":
            # Etherscan often returns status "0" with error in "result"
            err = data.get("result") or data.get("message") or "etherscan error"
            if self.log:
                self.log.error("etherscan_error", extra={"error": err, "action": params.get("action")})
            raise RuntimeError(str(err))
        return data

    # --- primitives ---
    def get_eth_balance(self, address: str) -> str:
        data = self._call({
            "module": "account",
            "action": "balance",
            "address": address,
            "tag": "latest",
        })
        return data["result"]

    def _get_txlist(self, address: str, start_block: int = 0, end_block: int = 99999999) -> List[Dict[str, Any]]:
        data = self._call({
            "module": "account",
            "action": "txlist",
            "address": address,
            "startblock": start_block,
            "endblock": end_block,
            "sort": "asc",
        })

        self.log.debug("_get_txlist")
        return data.get("result", [])

    def _get_internal_tx(self, address: str, start_block: int = 0, end_block: int = 99999999) -> List[Dict[str, Any]]:
        data = self._call({
            "module": "account",
            "action": "txlistinternal",
            "address": address,
            "startblock": start_block,
            "endblock": end_block,
            "sort": "asc",
        })
        return data.get("result", [])

    def _get_token_txs(self, address: str, start_block: int = 0, end_block: int = 99999999) -> List[Dict[str, Any]]:
        """ERC-20 transfers (both directions), ascending."""
        data = self._call({
            "module": "account",
            "action": "tokentx",
            "address": address,
            "startblock": start_block,
            "endblock": end_block,
            "sort": "asc",
        })
        return data.get("result", [])

    def _get_contract_meta(self, address: str) -> Dict[str, Any]:
        data = self._call({"module": "contract", "action": "getsourcecode", "address": address})
        arr = data.get("result", [])
        return arr[0] if arr else {}

    def _now(self) -> int:
        return int(time.time())

    def _slice_recent(self, txs: List[Dict[str, Any]], since_unix: int) -> List[Dict[str, Any]]:
        return [t for t in txs if int(t.get("timeStamp", "0")) >= since_unix]

    # ---------- rules ----------
    def _rule_empty_wallet(self, has_history: bool, balance_eth: float) -> Tuple[int, Reason]:
        """
        Empty + unused: no history AND 0 ETH balance => -10.
        Rationale: common in scam flows where victim is asked to fund first.
        """
        is_empty_unused = (not has_history) and (balance_eth == 0.0)
        delta = -10 if is_empty_unused else 0
        return delta, Reason(
            "empty_unused",
            delta,
            "Empty and unused address" if is_empty_unused else "Not empty/unused",
            {"has_history": has_history, "balance_eth": balance_eth, "empty_wallet": is_empty_unused},
        )

    def _rule_no_history(self, has_history: bool) -> Tuple[int, Reason]:
        delta = 0 if has_history else -15
        return delta, Reason("no_history", delta, "No on-chain history" if not has_history else "Has history",
                            {"has_history": has_history})

    def _rule_age(self, now: int, first_ts: Optional[int]) -> Tuple[int, Reason]:
        if first_ts is None:
            return 0, Reason("age", 0, "Age unknown", {"age_days": None})
        age_days = (now - first_ts) / 86400
        delta = -10 if age_days < 7 else (-5 if age_days < 30 else 0)
        return delta, Reason("age", delta, "Address age", {"age_days": round(age_days, 2)})

    def _rule_inactivity(self, now: int, last_ts: Optional[int]) -> Tuple[int, Reason]:
        if last_ts is None:
            return 0, Reason("inactivity", 0, "Inactivity unknown", {"inactive_days": None})
        inactive_days = (now - last_ts) / 86400
        delta = -5 if inactive_days > 180 else 0
        return delta, Reason("inactivity", delta, "Inactivity window", {"inactive_days": round(inactive_days, 2)})

    def _rule_fail_ratio(self, txs: List[Dict[str, Any]]) -> Tuple[int, Reason]:
        if not txs:
            return 0, Reason("failed_tx_ratio", 0, "No external tx", {"ratio": 0.0, "total": 0})
        total = len(txs)
        failed = sum(1 for t in txs if t.get("isError") == "1")
        ratio = failed / total
        delta = -10 if ratio > 0.5 else (-5 if ratio > 0.2 else 0)
        return delta, Reason("failed_tx_ratio", delta, "Failed tx ratio",
                             {"ratio": round(ratio, 3), "failed": failed, "total": total})

    def _rule_unique_counterparties(self, address: str, txs_90d: List[Dict[str, Any]]) -> Tuple[int, Reason]:
        lower = address.lower()
        cps = set()
        for t in txs_90d:
            frm = t.get("from", "").lower()
            to = t.get("to", "").lower()
            if frm == lower and to:
                cps.add(to)
            elif to == lower and frm:
                cps.add(frm)
        unique = len(cps)
        delta = -5 if unique < 3 and len(txs_90d) >= 3 else 0
        return delta, Reason("unique_cps_90d", delta, "Unique counterparties (90d)",
                             {"unique": unique, "txs_90d": len(txs_90d)})

    def _rule_dust_incoming_eth(self, address: str, txs_90d: List[Dict[str, Any]]) -> Tuple[int, Reason]:
        """
        ETH dusting: incoming < 0.001 ETH, count > 20 in 90d => -5
        """
        lower = address.lower()
        dust = sum(
            1
            for t in txs_90d
            if t.get("to", "").lower() == lower and wei_to_eth(t.get("value", "0")) < 0.001
        )
        delta = -5 if dust > 20 else 0
        return delta, Reason("dust_incoming_eth_90d", delta, "ETH dust incoming (90d)", {"count": dust})

    def _rule_dust_incoming_tokens(self, address: str, token_txs_90d: List[Dict[str, Any]]) -> Tuple[int, Reason]:
        """
        Token dusting: many tiny inbound ERC-20 transfers.
        Threshold: amount < 0.001 token units, count > 20 in 90d => -5
        (Heuristic without prices.)
        """
        lower = address.lower()
        tiny_count = 0
        for t in token_txs_90d:
            if t.get("to", "").lower() != lower:
                continue
            dec = pow10(t.get("tokenDecimal", 0))
            try:
                amt = int(t.get("value", "0")) / dec
            except Exception:
                amt = 0.0
            if amt < 0.001:
                tiny_count += 1
        delta = -5 if tiny_count > 20 else 0
        return delta, Reason("dust_incoming_tokens_90d", delta, "Token dust incoming (90d)", {"count": tiny_count})

    def _rule_token_only_empty(self, has_eth_history: bool, eth_balance: float,
                               token_txs: List[Dict[str, Any]]) -> Tuple[int, Reason]:
        """
        Token-only pattern: 0 ETH, no ETH history, but has token transfers.
        Often used to bait users. => -5
        """
        token_activity = len(token_txs) > 0
        token_only = (not has_eth_history) and (eth_balance == 0.0) and token_activity
        delta = -5 if token_only else 0
        return delta, Reason("token_only_empty", delta, "Token-only activity without ETH",
                             {"token_activity": token_activity, "eth_balance": eth_balance,
                              "has_eth_history": has_eth_history})

    def _rule_contract_verification(self, meta: Dict[str, Any]) -> Tuple[int, Reason]:
        is_contract = bool(meta.get("ContractName"))
        if not is_contract:
            return 0, Reason("contract_verified", 0, "EOA (not a contract)", {"is_contract": False})
        abi = meta.get("ABI", "")
        src = meta.get("SourceCode", "")
        verified = bool(src) and "Contract source code not verified" not in abi
        delta = 5 if verified else -20
        return delta, Reason("contract_verified", delta, "Contract verification",
                             {"verified": verified, "is_contract": True})

    def _rule_contract_proxy(self, meta: Dict[str, Any]) -> Tuple[int, Reason]:
        is_contract = bool(meta.get("ContractName"))
        if not is_contract:
            return 0, Reason("contract_proxy", 0, "EOA (not a contract)", {"is_contract": False})
        proxy_flag = meta.get("Proxy", "0") == "1"
        delta = -5 if proxy_flag else 0
        return delta, Reason("contract_proxy", delta, "Contract proxy", {"proxy": proxy_flag})

    # ---------- scoring ----------
    def evaluate_address_security(
        self,
        address: str,
        mode: str = "score",
        include_balance: bool = True,
    ) -> Union[int, Dict[str, Any]]:
        """
        Returns:
          - if mode == "score": int
          - else dict with score, tier, empty_wallet flag, reasons[], metrics{}
        """
        t0 = time.perf_counter()
        now = self._now()

        # fetch
        try:
            txs = self._get_txlist(address)
            internal = self._get_internal_tx(address)
            tokentx = self._get_token_txs(address)
            meta = self._get_contract_meta(address)
            balance_wei = self.get_eth_balance(address) if include_balance else None
        except Exception as e:
            score = 20
            out = {
                "score": score,
                "tier": self._tier(score),
                "empty_wallet": False,
                "reasons": [asdict(Reason("api_error", 0, "Etherscan fetch failed", {"error": str(e)}))],
                "metrics": {"fetch_ok": False},
                "elapsed_s": round(time.perf_counter() - t0, 3),
            }
            return score if mode == "score" else out

        # basics
        has_eth_history = bool(txs or internal)
        first_ts = int((txs or internal)[0]["timeStamp"]) if has_eth_history else None
        last_ts = int((txs or internal)[-1]["timeStamp"]) if has_eth_history else None
        recent_90d = self._slice_recent(txs, now - 90 * 86400)
        token_recent_90d = self._slice_recent(tokentx, now - 90 * 86400)

        metrics: Dict[str, Any] = {
            "has_eth_history": has_eth_history,
            "first_ts": first_ts,
            "last_ts": last_ts,
            "txs_total": len(txs),
            "internal_total": len(internal),
            "token_txs_total": len(tokentx),
        }
        balance_eth = 0.0
        if include_balance and balance_wei is not None:
            balance_eth = wei_to_eth(str(balance_wei))
            metrics["balance_eth"] = balance_eth

        empty_wallet = (not has_eth_history) and (balance_eth == 0.0)

        # apply rules (ordered)
        score = BASE_SCORE
        reasons: List[Reason] = []
        for rule_fn, args in [
            (self._rule_empty_wallet, (has_eth_history, balance_eth)),
            (self._rule_no_history, (has_eth_history,)),
            (self._rule_age, (now, first_ts)),
            (self._rule_inactivity, (now, last_ts)),
            (self._rule_fail_ratio, (txs,)),
            (self._rule_unique_counterparties, (address, recent_90d)),
            (self._rule_dust_incoming_eth, (address, recent_90d)),
            (self._rule_dust_incoming_tokens, (address, token_recent_90d)),
            (self._rule_token_only_empty, (has_eth_history, balance_eth, tokentx)),
            (self._rule_contract_verification, (meta,)),
            (self._rule_contract_proxy, (meta,)),
        ]:
            delta, reason = rule_fn(*args)
            score += delta
            reasons.append(reason)

        score = clamp(int(round(score)))
        elapsed = round(time.perf_counter() - t0, 3)

        if mode == "score":
            return score

        return {
            "score": score,
            "tier": self._tier(score),
            "empty_wallet": empty_wallet,
            "reasons": [asdict(r) for r in reasons],
            "metrics": metrics,
            "elapsed_s": elapsed,
        }

    @staticmethod
    def _tier(score: int) -> str:
        if score < 20: return "critical"
        if score < 40: return "high"
        if score < 70: return "medium"
        if score < 90: return "low"
        return "very_low"

# ---------- Telegram formatter (HTML) ----------
def format_for_tg(addr: str, result: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
    score = result["score"]
    tier = result["tier"]
    empty = result["empty_wallet"]
    m = result["metrics"]
    reasons = [r for r in result["reasons"] if r["delta"] != 0]

    icon = {"critical":"🛑","high":"⚠️","medium":"🟡","low":"🟢","very_low":"✅"}[tier]

    # headline
    head = f"{icon} <b>Wallet risk</b> • <code>{addr}</code>\n"
    line1 = f"<b>Score:</b> <code>{score}</code> — {tier.replace('_',' ')}"
    badge = " • <b>Empty wallet</b>" if empty else ""

    # quick stats
    now = int(time.time())
    age_txt = "n/a" if m.get("first_ts") is None else f"{(now - m['first_ts']) // 86400}d"
    last_txt = "n/a" if m.get("last_ts") is None else f"{(now - m['last_ts']) // 86400}d ago"

    stats = [
        f"<b>Tx:</b> {m.get('txs_total',0)}",
        f"<b>Token tx:</b> {m.get('token_txs_total',0)}",
        f"<b>Age:</b> {age_txt}",
        f"<b>Last activity:</b> {last_txt}",
    ]
    if "balance_eth" in m:
        stats.append(f"<b>Balance:</b> {m['balance_eth']:.6f} ETH")

    # reasons
    bullets = "\n".join([f"• {r['summary']} ({'+' if r['delta']>0 else ''}{r['delta']})" for r in reasons])
    reasons_txt = f"\n<b>Why:</b>\n{bullets}" if bullets else ""

    advise = ""
    if empty:
        advise = ("\n<blockquote>Unfunded and unused. Treat as untrusted until funded from a known source."
                  "</blockquote>")

    text = (
        head +
        f"{line1}{badge}\n" +
        " | ".join(stats) +
        reasons_txt +
        advise +
        f"\n\n<a href='https://etherscan.io/address/{addr}'>Etherscan</a>"
    )
    kb = {"inline_keyboard":[[{"text":"Re-check","callback_data":f"recheck:{addr}"}]]}
    return text, kb

# ---------- example usage ----------
if __name__ == "__main__":
    # Example only; wire into your FastAPI handler.
    es = Etherscan(chainid=1)
    address = "0xde0B295669a9FD93d5F28D9Ec85E40f4cb697BAe"
    result = es.evaluate_address_security(address, mode="full")
    msg, kb = format_for_tg(address, result)
    print(msg)
    print(kb)
