from __future__ import annotations
from dataclasses import asdict
from typing import Any, Dict, List, Union
from .config import BASE_SCORE
from .utils import now, clamp, sun_to_trx
from .trc_client import TronClient
from .rules import (
    Reason,
    rule_empty_wallet, rule_no_history, rule_age, rule_inactivity,
    rule_fail_ratio_trx, rule_unique_cps, rule_dust_trx, rule_dust_trc20,
    rule_token_only_empty, rule_contract_verified, rule_contract_proxy,
)

class WalletScorerTRC:
    def __init__(self, logger=None):
        self.api = TronClient(logger=logger)

    @staticmethod
    def _tier(score: int) -> str:
        if score < 20: return "critical"
        if score < 40: return "high"
        if score < 70: return "medium"
        if score < 90: return "low"
        return "very_low"

    @staticmethod
    def _slice_recent_ms(txs, since_unix: int):
        cutoff_ms = since_unix * 1000
        return [t for t in txs if int(t.get("block_timestamp", 0)) >= cutoff_ms]

    def evaluate(self, address: str, mode: str = "score", include_balance: bool = True) -> Union[int, Dict[str, Any]]:
        t_now = now()

        try:
            trx_txs = self.api.get_trx_txs(address)           # ascending list
            trc20_txs = self.api.get_trc20_txs(address)       # ascending list
            contract_info = self.api.get_contract(address)    # may be {}
            ver_flag = self.api.get_contract_verification(address)  # bool|None
            acct = self.api.get_account(address) if include_balance else {}
        except Exception as e:
            score = 20
            out = {
                "score": score, "tier": self._tier(score), "empty_wallet": False,
                "reasons": [asdict(Reason("api_error", 0, "Tron API fetch failed", {"error": str(e)}))],
                "metrics": {"fetch_ok": False},
            }
            return score if mode == "score" else out

        has_trx_history = bool(trx_txs)
        first_ts_ms = int(trx_txs[0]["block_timestamp"]) if has_trx_history else None
        last_ts_ms  = int(trx_txs[-1]["block_timestamp"]) if has_trx_history else None
        recent_90d = self._slice_recent_ms(trx_txs, t_now - 90*86400)
        trc20_recent_90d = self._slice_recent_ms(trc20_txs, t_now - 90*86400)

        trx_balance = 0.0
        if include_balance:
            # TronGrid account format: balances as list or 'balance' in SUN in some responses
            bal = 0
            try:
                # prefer top-level 'balance' if present
                bal = int(acct.get("balance", 0))
            except Exception:
                pass
            trx_balance = sun_to_trx(bal)

        metrics: Dict[str, Any] = {
            "has_trx_history": has_trx_history,
            "first_ts_ms": first_ts_ms,
            "last_ts_ms": last_ts_ms,
            "trx_txs_total": len(trx_txs),
            "trc20_txs_total": len(trc20_txs),
            "trx_balance": trx_balance if include_balance else None,
        }

        empty_wallet = (not has_trx_history) and (trx_balance == 0.0)

        score = BASE_SCORE
        reasons: List[Reason] = []
        for fn, args in [
            (rule_empty_wallet, (has_trx_history, trx_balance)),
            (rule_no_history, (has_trx_history,)),
            (rule_age, (t_now, first_ts_ms)),
            (rule_inactivity, (t_now, last_ts_ms)),
            (rule_fail_ratio_trx, (trx_txs,)),
            (rule_unique_cps, (address, recent_90d)),
            (rule_dust_trx, (address, recent_90d)),
            (rule_dust_trc20, (address, trc20_recent_90d)),
            (rule_token_only_empty, (has_trx_history, trx_balance, trc20_txs)),
            (rule_contract_verified, (ver_flag,)),
            (rule_contract_proxy, (contract_info,)),
        ]:
            d, reason = fn(*args)
            score += d
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
