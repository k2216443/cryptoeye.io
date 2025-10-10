import os
import requests
import time

from typing import Union
from libs.log import Log

ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")
ETHERSCAN_API_URL = "https://api.etherscan.io/v2/api"

class Etherscan:

    def __init__(self, chainid = 1):
        self.log = Log(module="etherscan")
        self.chainid = chainid

    def _call(self, params: dict[str, any]) -> dict[str, any]:
        """Thin wrapper around Etherscan GET.

        Raises:
            RuntimeError on non-OK Etherscan response.
        """
        q = dict(params)
        q["apikey"] = ETHERSCAN_API_KEY
        q["chainid"] = self.chainid
        r = requests.get(ETHERSCAN_API_URL, params=q, timeout=20)
        data = r.json()
        if data.get("status") != "1":
            # Etherscan returns status "0" with message in "result"
            self.log.error(api_error=data.get("result", "unknown"), where=params.get("action"))
            raise RuntimeError(data.get("result", "etherscan error"))
        return data

    def get_eth_balance(self, address: str) -> str:
        t0 = time.perf_counter()
        data = self._call(
            {
                "module": "account",
                "action": "balance",
                "address": address,
                "chainid": 1,
                "tag": "latest",
            }
        )
        dt = time.perf_counter() - t0
        self.log.debug(balance=data["result"], elapsed=f"{dt:.6f}")
        return data["result"]

    def _get_txlist(self, address: str, start_block: int = 0, end_block: int = 99999999) -> list[dict[str, any]]:
        """Normal transactions (externals). Sorted ascending by block per Etherscan."""
        data = self._call(
            {
                "module": "account",
                "action": "txlist",
                "address": address,
                "startblock": start_block,
                "endblock": end_block,
                "sort": "asc",
            }
        )
        return data.get("result", [])
    
    def _get_internal_tx(self, address: str, start_block: int = 0, end_block: int = 99999999) -> list[dict[str, any]]:
        """Internal transactions."""
        data = self._call(
            {
                "module": "account",
                "action": "txlistinternal",
                "address": address,
                "startblock": start_block,
                "endblock": end_block,
                "sort": "asc",
            }
        )
        return data.get("result", [])

    def _get_contract_meta(self, address: str) -> dict[str, any]:
        """Returns first item of getsourcecode for an address."""
        data = self._call({"module": "contract", "action": "getsourcecode", "address": address})
        arr = data.get("result", [])
        return arr[0] if arr else {}

    def _now(self) -> int:
        return int(time.time())

    def _slice_recent(self, txs: list[dict[str, any]], since_unix: int) -> list[dict[str, any]]:
        return [t for t in txs if int(t.get("timeStamp", "0")) >= since_unix]

    def evaluate_address_security(
        self,
        address: str,
        mode: str = "score",
    ) -> Union[int, dict[str, any]]:
        """
        Compute a heuristic security score for an ETH address using only Etherscan data.

        Inputs:
            address: checksummed or lowercase address.
            mode:
              - "score": return integer score 0..100
              - "full":  return dict with score and metric breakdown

        Heuristics (weights are simple and transparent):
            - No history: -15
            - Address age < 7d: -10, < 30d: -5
            - Failed tx ratio > 0.5: -10, > 0.2: -5
            - Unique counterparties in 90d < 3: -5
            - Dust incoming in 90d (> 20 tx < 0.001 ETH): -5
            - Contract unverified: -20; verified: +5
            - Contract proxy (upgradable): -5
            - Long inactivity > 180d: -5
            Floor 0, cap 100.

        Returns:
            score or dict{"score": int, "metrics": {...}}
        """
        t_start = time.perf_counter()
        now = self._now()
        try:
            # Pull primitives
            txs = self._get_txlist(address)
            internal = self._get_internal_tx(address)
            meta = self._get_contract_meta(address)
        except Exception as e:
            self.log.error(address=address, error=str(e), step="fetch")
            # return conservative low score on API error
            return {"score": 20, "metrics": {"error": str(e)}} if mode == "full" else 20

        # ----- Metrics -----
        score = 50
        metrics: dict[str, any] = {}

        # History
        has_history = len(txs) > 0 or len(internal) > 0
        metrics["has_history"] = has_history
        if not has_history:
            score -= 15

        # Age and activity
        if has_history:
            first_ts = int((txs or internal)[0]["timeStamp"])
            last_ts = int((txs or internal)[-1]["timeStamp"])
            age_days = max(0, (now - first_ts) / 86400)
            inactive_days = max(0, (now - last_ts) / 86400)
        else:
            age_days = None
            inactive_days = None

        metrics["age_days"] = age_days
        metrics["inactive_days"] = inactive_days

        if age_days is not None:
            if age_days < 7:
                score -= 10
            elif age_days < 30:
                score -= 5

        if inactive_days is not None and inactive_days > 180:
            score -= 5

        # Failed tx ratio on externals
        if txs:
            total_ext = len(txs)
            failed_ext = sum(1 for t in txs if t.get("isError") == "1")
            fail_ratio = failed_ext / total_ext
        else:
            fail_ratio = 0.0

        metrics["failed_tx_ratio"] = round(fail_ratio, 3)
        if fail_ratio > 0.5:
            score -= 10
        elif fail_ratio > 0.2:
            score -= 5

        # Recent window
        win90 = now - 90 * 86400
        recent = self._slice_recent(txs, win90)

        # Unique counterparties in last 90d
        cps = set()
        lower_addr = address.lower()
        for t in recent:
            frm = t.get("from", "").lower()
            to = t.get("to", "").lower()
            if frm == lower_addr and to:
                cps.add(to)
            elif to == lower_addr and frm:
                cps.add(frm)
        unique_cps_90d = len(cps)
        metrics["unique_counterparties_90d"] = unique_cps_90d
        if unique_cps_90d < 3 and len(recent) >= 3:
            score -= 5

        # Dust incoming in 90d (< 0.001 ETH)
        def wei_to_eth(wei: str) -> float:
            try:
                return int(wei) / 1e18
            except Exception:
                return 0.0

        dust_incoming_90d = sum(
            1
            for t in recent
            if t.get("to", "").lower() == lower_addr and wei_to_eth(t.get("value", "0")) < 0.001
        )
        metrics["dust_incoming_90d"] = dust_incoming_90d
        if dust_incoming_90d > 20:
            score -= 5

        # Contract checks
        # If SourceCode field is empty and ABI is "Contract source code not verified", consider unverified.
        # If it is EOA, Etherscan returns empty metadata.
        is_contract = bool(meta.get("ContractName"))
        verified = False
        proxy_flag = False
        if is_contract:
            abi = meta.get("ABI", "")
            src = meta.get("SourceCode", "")
            verified = bool(src) and "Contract source code not verified" not in abi
            proxy_flag = meta.get("Proxy", "0") == "1"

        metrics["is_contract"] = is_contract
        metrics["contract_verified"] = verified
        metrics["contract_proxy"] = proxy_flag

        if is_contract:
            if not verified:
                score -= 20
            else:
                score += 5
            if proxy_flag:
                score -= 5

        # Clamp
        score = max(0, min(100, int(round(score))))

        dt = time.perf_counter() - t_start

        if mode == "full":
            self.log.debug(address=address, score=score, elapsed=f"{dt:.3f}", mode=mode, metrics=metrics)
        else:
            self.log.debug(address=address, score=score, elapsed=f"{dt:.3f}", mode=mode)
        return score