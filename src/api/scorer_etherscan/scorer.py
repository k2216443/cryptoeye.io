from __future__ import annotations
from dataclasses import asdict
from typing import Any, Dict, List, Tuple, Union
from .config import BASE_SCORE
from .utils import now, clamp, wei_to_eth
from .eth_client import EtherscanClient
from .rules import (
    Reason,
    rule_empty_wallet, rule_no_history, rule_age, rule_inactivity,
    rule_fail_ratio, rule_unique_cps, rule_dust_eth, rule_dust_tokens,
    rule_token_only_empty, rule_contract_verified, rule_contract_proxy,
)

class WalletScorer:
    def __init__(self, chainid: int = 1, logger=None):
        self.api = EtherscanClient(chainid=chainid, logger=logger)

    @staticmethod
    def _tier(score: int) -> str:
        if score < 20: return "critical"
        if score < 40: return "high"
        if score < 70: return "medium"
        if score < 90: return "low"
        return "very_low"

    @staticmethod
    def _slice_recent(txs, since_unix: int):
        return [t for t in txs if int(t.get("timeStamp","0")) >= since_unix]

    def evaluate(self, address: str, mode: str = "score", include_balance: bool = True) -> Union[int, Dict[str, Any]]:
        t_now = now()
        try:
            txs = self.api.get_txlist(address)
            internal = self.api.get_internal_tx(address)
            tokentx = self.api.get_token_txs(address)
            meta = self.api.get_contract_meta(address)
            balance_wei = self.api.get_eth_balance(address) if include_balance else None
        except Exception as e:
            score = 20
            out = {
                "score": score, "tier": self._tier(score), "empty_wallet": False,
                "reasons": [asdict(Reason("api_error", 0, "Etherscan fetch failed", {"error": str(e)}))],
                "metrics": {"fetch_ok": False}
            }
            return score if mode == "score" else out

        has_eth_history = bool(txs or internal)
        first_ts = int((txs or internal)[0]["timeStamp"]) if has_eth_history else None
        last_ts  = int((txs or internal)[-1]["timeStamp"]) if has_eth_history else None
        recent_90d = self._slice_recent(txs, t_now - 90*86400)
        token_recent_90d = self._slice_recent(tokentx, t_now - 90*86400)

        metrics: Dict[str, Any] = {
            "has_eth_history": has_eth_history,
            "first_ts": first_ts, "last_ts": last_ts,
            "txs_total": len(txs), "internal_total": len(internal),
            "token_txs_total": len(tokentx),
        }
        balance_eth = 0.0
        if include_balance and balance_wei is not None:
            balance_eth = wei_to_eth(str(balance_wei))
            metrics["balance_eth"] = balance_eth

        empty_wallet = (not has_eth_history) and (balance_eth == 0.0)

        score = BASE_SCORE
        reasons: List[Reason] = []
        for fn, args in [
            (rule_empty_wallet, (has_eth_history, balance_eth)),
            (rule_no_history, (has_eth_history,)),
            (rule_age, (t_now, first_ts)),
            (rule_inactivity, (t_now, last_ts)),
            (rule_fail_ratio, (txs,)),
            (rule_unique_cps, (address, recent_90d)),
            (rule_dust_eth, (address, recent_90d)),
            (rule_dust_tokens, (address, token_recent_90d)),
            (rule_token_only_empty, (has_eth_history, balance_eth, tokentx)),
            (rule_contract_verified, (meta,)),
            (rule_contract_proxy, (meta,)),
        ]:
            delta, reason = fn(*args)
            score += delta
            reasons.append(reason)

        score = clamp(int(round(score)))
        if mode == "score":
            return score

        return {
            "score": score,
            "tier": self._tier(score),
            "empty_wallet": empty_wallet,
            "reasons": [asdict(r) for r in reasons],
            "metrics": metrics,
        }
