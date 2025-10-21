from __future__ import annotations
import requests
from typing import Any, Dict, List
from .config import ETHERSCAN_API_KEY, ETHERSCAN_API_URL

class EtherscanClient:
    def __init__(self, chainid: int = 1, logger=None):
        self.chainid = chainid
        self.log = logger

    def _call(self, params: Dict[str, Any]) -> Dict[str, Any]:
        q = dict(params)
        q["apikey"] = ETHERSCAN_API_KEY
        q["chainid"] = self.chainid
        if self.log: self.log.debug("etherscan_call", extra={"params": q})
        r = requests.get(ETHERSCAN_API_URL, params=q, timeout=20)
        data = r.json()
        if data.get("status") != "1":
            err = data.get("result") or data.get("message") or "etherscan error"
            if self.log: self.log.error("etherscan_error", extra={"error": err, "action": params.get("action")})
            raise RuntimeError(str(err))
        return data

    def get_eth_balance(self, address: str) -> str:
        return self._call({"module":"account","action":"balance","address":address,"tag":"latest"})["result"]

    def get_txlist(self, address: str, start_block: int = 0, end_block: int = 99999999):
        result = self._call({
            "module":"account","action":"txlist","address":address,
            "startblock":start_block,"endblock":end_block,"sort":"asc"
        }).get("result", [])
        return result if isinstance(result, list) else []

    def get_internal_tx(self, address: str, start_block: int = 0, end_block: int = 99999999):
        result = self._call({
            "module":"account","action":"txlistinternal","address":address,
            "startblock":start_block,"endblock":end_block,"sort":"asc"
        }).get("result", [])
        return result if isinstance(result, list) else []

    def get_token_txs(self, address: str, start_block: int = 0, end_block: int = 99999999):
        result = self._call({
            "module":"account","action":"tokentx","address":address,
            "startblock":start_block,"endblock":end_block,"sort":"asc"
        }).get("result", [])
        return result if isinstance(result, list) else []

    def get_contract_meta(self, address: str):
        arr = self._call({"module":"contract","action":"getsourcecode","address":address}).get("result", [])
        return arr[0] if arr else {}
