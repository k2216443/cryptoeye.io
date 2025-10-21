from __future__ import annotations
import os
import time
import requests
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional, Tuple, Union
from datetime import datetime

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
        """
        Low-level Etherscan API call with comprehensive logging.

        Logs:
        - Request parameters (API key redacted)
        - Response status and timing
        - Errors with full context

        Args:
            params: API parameters (module, action, address, etc.)

        Returns:
            API response data

        Raises:
            RuntimeError: If API returns error status
        """
        import time
        call_start = time.time()

        # Build request parameters
        q = dict(params)
        q["apikey"] = ETHERSCAN_API_KEY
        q["chainid"] = self.chainid

        # Log request details (with redacted API key)
        if self.log:
            log_params = {k: ("***REDACTED***" if k == "apikey" else v) for k, v in q.items()}
            self.log.info(
                f"📡 Etherscan API Call: {params.get('module')}.{params.get('action')}",
                extra={
                    "event": "etherscan_request",
                    "module": params.get("module"),
                    "action": params.get("action"),
                    "address": params.get("address", "N/A"),
                    "params": log_params,
                }
            )

        # Make API request
        try:
            r = requests.get(ETHERSCAN_API_URL, params=q, timeout=20)
            call_duration = time.time() - call_start
            data = r.json()

            # Log response summary
            if self.log:
                result_preview = str(data.get("result", ""))[:100]  # First 100 chars
                result_type = type(data.get("result")).__name__
                result_length = len(data.get("result", [])) if isinstance(data.get("result"), list) else "N/A"

                self.log.info(
                    f"✅ Etherscan Response: {params.get('action')} ({call_duration:.2f}s)",
                    extra={
                        "event": "etherscan_response",
                        "action": params.get("action"),
                        "status": data.get("status"),
                        "message": data.get("message"),
                        "duration_seconds": round(call_duration, 3),
                        "result_type": result_type,
                        "result_length": result_length,
                        "result_preview": result_preview,
                    }
                )

            # Check for API errors
            if data.get("status") != "1":
                # Etherscan often returns status "0" with error in "result"
                err = data.get("result") or data.get("message") or "etherscan error"

                if self.log:
                    self.log.error(
                        f"❌ Etherscan Error: {params.get('action')} - {err}",
                        extra={
                            "event": "etherscan_error",
                            "action": params.get("action"),
                            "error": str(err),
                            "status": data.get("status"),
                            "full_response": data,
                        }
                    )
                raise RuntimeError(str(err))

            return data

        except requests.exceptions.RequestException as e:
            call_duration = time.time() - call_start
            if self.log:
                self.log.error(
                    f"🔌 Network Error: {params.get('action')} - {str(e)}",
                    extra={
                        "event": "network_error",
                        "action": params.get("action"),
                        "error": str(e),
                        "duration_seconds": round(call_duration, 3),
                    }
                )
            raise

    # --- primitives ---
    def get_eth_balance(self, address: str) -> str:
        """
        Fetch ETH balance for an address.

        Args:
            address: Ethereum address (0x...)

        Returns:
            Balance in Wei as string
        """
        data = self._call({
            "module": "account",
            "action": "balance",
            "address": address,
            "tag": "latest",
        })
        balance_wei = data["result"]

        if self.log:
            balance_eth = wei_to_eth(balance_wei)
            self.log.debug(
                f"💰 Balance: {balance_eth:.6f} ETH ({balance_wei} Wei)",
                extra={"event": "balance_fetched", "address": address, "balance_wei": balance_wei, "balance_eth": balance_eth}
            )

        return balance_wei

    def _get_txlist(self, address: str, start_block: int = 0, end_block: int = 99999999) -> List[Dict[str, Any]]:
        """
        Fetch normal (external) transactions for an address.

        Args:
            address: Ethereum address
            start_block: Starting block number (default: 0)
            end_block: Ending block number (default: latest)

        Returns:
            List of transaction dictionaries
        """
        data = self._call({
            "module": "account",
            "action": "txlist",
            "address": address,
            "startblock": start_block,
            "endblock": end_block,
            "sort": "asc",
        })

        result = data.get("result", [])

        # Ensure result is always a list (Etherscan sometimes returns strings on errors)
        if not isinstance(result, list):
            if self.log:
                self.log.warning(
                    f"⚠️  Expected list for txlist, got {type(result).__name__}: {str(result)[:100]}",
                    extra={"event": "unexpected_response_type", "expected": "list", "got": type(result).__name__}
                )
            return []

        if self.log:
            failed_count = sum(1 for tx in result if tx.get("isError") == "1")
            self.log.info(
                f"📜 Normal Transactions: {len(result)} total, {failed_count} failed",
                extra={"event": "txlist_fetched", "total": len(result), "failed": failed_count}
            )

        return result

    def _get_internal_tx(self, address: str, start_block: int = 0, end_block: int = 99999999) -> List[Dict[str, Any]]:
        """
        Fetch internal transactions for an address.
        Internal transactions are ETH transfers triggered by smart contracts.

        Args:
            address: Ethereum address
            start_block: Starting block number
            end_block: Ending block number

        Returns:
            List of internal transaction dictionaries
        """
        data = self._call({
            "module": "account",
            "action": "txlistinternal",
            "address": address,
            "startblock": start_block,
            "endblock": end_block,
            "sort": "asc",
        })

        result = data.get("result", [])

        if not isinstance(result, list):
            if self.log:
                self.log.warning(
                    f"⚠️  Expected list for internal tx, got {type(result).__name__}",
                    extra={"event": "unexpected_response_type", "action": "txlistinternal"}
                )
            return []

        if self.log:
            self.log.info(
                f"🔄 Internal Transactions: {len(result)} total",
                extra={"event": "internal_tx_fetched", "total": len(result)}
            )

        return result

    def _get_token_txs(self, address: str, start_block: int = 0, end_block: int = 99999999) -> List[Dict[str, Any]]:
        """
        Fetch ERC-20 token transfers for an address.
        Returns both incoming and outgoing token transfers.

        Args:
            address: Ethereum address
            start_block: Starting block number
            end_block: Ending block number

        Returns:
            List of token transfer dictionaries
        """
        data = self._call({
            "module": "account",
            "action": "tokentx",
            "address": address,
            "startblock": start_block,
            "endblock": end_block,
            "sort": "asc",
        })

        result = data.get("result", [])

        if not isinstance(result, list):
            if self.log:
                self.log.warning(
                    f"⚠️  Expected list for token tx, got {type(result).__name__}",
                    extra={"event": "unexpected_response_type", "action": "tokentx"}
                )
            return []

        if self.log:
            # Count unique tokens
            unique_tokens = len(set(tx.get("tokenSymbol", "UNKNOWN") for tx in result))
            self.log.info(
                f"🪙 Token Transfers: {len(result)} transfers, {unique_tokens} unique tokens",
                extra={"event": "token_tx_fetched", "total": len(result), "unique_tokens": unique_tokens}
            )

        return result

    def _get_contract_meta(self, address: str) -> Dict[str, Any]:
        """
        Fetch contract metadata (source code, ABI, verification status).

        Args:
            address: Ethereum address

        Returns:
            Contract metadata dictionary (empty dict if not a contract)
        """
        data = self._call({"module": "contract", "action": "getsourcecode", "address": address})
        arr = data.get("result", [])
        meta = arr[0] if arr else {}

        if self.log:
            is_contract = bool(meta.get("ContractName"))
            if is_contract:
                is_verified = bool(meta.get("SourceCode"))
                is_proxy = meta.get("Proxy", "0") == "1"
                self.log.info(
                    f"📋 Contract: {meta.get('ContractName', 'Unknown')} (Verified: {is_verified}, Proxy: {is_proxy})",
                    extra={
                        "event": "contract_meta_fetched",
                        "is_contract": True,
                        "name": meta.get("ContractName"),
                        "verified": is_verified,
                        "proxy": is_proxy
                    }
                )
            else:
                self.log.info(
                    "👤 Address Type: EOA (Externally Owned Account)",
                    extra={"event": "contract_meta_fetched", "is_contract": False}
                )

        return meta

    def _now(self) -> int:
        return int(time.time())

    def _slice_recent(self, txs: List[Dict[str, Any]], since_unix: int) -> List[Dict[str, Any]]:
        return [t for t in txs if int(t.get("timeStamp", "0")) >= since_unix]

    # ========================================
    # RISK SCORING RULES
    # ========================================
    # Each rule examines a specific risk factor and returns:
    # - delta: Points to add/subtract from base score (negative = risk, positive = safety)
    # - reason: Explanation with metadata for transparency
    # ========================================

    def _rule_empty_wallet(self, has_history: bool, balance_eth: float) -> Tuple[int, Reason]:
        """
        Rule: Empty & Unused Wallet Detection

        Checks if the wallet has never been used and has zero balance.

        Risk: HIGH (-10 points)
        Rationale: Empty, unused wallets are commonly used in phishing and scam flows
                   where the victim is asked to "fund" or "activate" the address first.

        Triggers when:
        - No transaction history (no normal or internal txs)
        - AND ETH balance = 0

        Args:
            has_history: Whether wallet has any on-chain transactions
            balance_eth: Current ETH balance

        Returns:
            (delta, reason) tuple
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
        """
        Rule: Transaction History Check

        Checks if the wallet has any on-chain activity.

        Risk: CRITICAL (-15 points)
        Rationale: Wallets with zero history cannot be trusted. No track record means
                   no way to verify legitimacy. Often used in scams.

        Triggers when:
        - No normal (external) transactions
        - AND no internal transactions

        Args:
            has_history: Whether wallet has transaction history

        Returns:
            (delta, reason) tuple
        """
        delta = 0 if has_history else -15
        return delta, Reason(
            "no_history",
            delta,
            "No on-chain history" if not has_history else "Has history",
            {"has_history": has_history}
        )

    def _rule_age(self, now: int, first_ts: Optional[int]) -> Tuple[int, Reason]:
        """
        Rule: Wallet Age Assessment

        Evaluates how long the wallet has existed based on first transaction.

        Risk Levels:
        - Very New (<7 days): -10 points - HIGH RISK
        - New (7-30 days): -5 points - MODERATE RISK
        - Established (>30 days): 0 points - ACCEPTABLE

        Rationale: Newly created wallets are often used in scams and rug pulls.
                   Scammers typically create fresh wallets to avoid reputation damage.
                   Older wallets have more credibility.

        Args:
            now: Current Unix timestamp
            first_ts: Timestamp of first transaction (None if no history)

        Returns:
            (delta, reason) tuple
        """
        if first_ts is None:
            return 0, Reason("age", 0, "Age unknown", {"age_days": None})

        age_days = (now - first_ts) / 86400

        if age_days < 7:
            delta = -10  # Very new wallet
        elif age_days < 30:
            delta = -5   # Fairly new wallet
        else:
            delta = 0    # Established wallet

        return delta, Reason("age", delta, "Address age", {"age_days": round(age_days, 2)})

    def _rule_inactivity(self, now: int, last_ts: Optional[int]) -> Tuple[int, Reason]:
        """
        Rule: Inactivity Period Check

        Measures time since last transaction activity.

        Risk: MODERATE (-5 points)
        Rationale: Wallets inactive for extended periods (>180 days) may be:
                   - Abandoned/compromised and reactivated by attackers
                   - Dormant wallets being sold/transferred

        Triggers when:
        - Last activity was more than 180 days ago

        Args:
            now: Current Unix timestamp
            last_ts: Timestamp of last transaction (None if no history)

        Returns:
            (delta, reason) tuple
        """
        if last_ts is None:
            return 0, Reason("inactivity", 0, "Inactivity unknown", {"inactive_days": None})

        inactive_days = (now - last_ts) / 86400
        delta = -5 if inactive_days > 180 else 0

        return delta, Reason(
            "inactivity",
            delta,
            "Inactivity window",
            {"inactive_days": round(inactive_days, 2)}
        )

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
        Comprehensive wallet security evaluation with transparent scoring.

        This method:
        1. Fetches blockchain data from Etherscan (txs, balance, tokens, contract info)
        2. Analyzes activity patterns and applies risk rules
        3. Calculates a security score (0-100, higher = safer)
        4. Returns detailed breakdown of scoring factors

        Args:
            address: Ethereum address to evaluate
            mode: "score" (returns int) or "full" (returns detailed dict)
            include_balance: Whether to fetch current ETH balance

        Returns:
            If mode="score": int score (0-100)
            If mode="full": dict with score, tier, reasons, metrics, wallet_details

        Risk Tiers:
            - critical: score < 20 (🛑)
            - high: score < 40 (⚠️)
            - medium: score < 70 (🟡)
            - low: score < 90 (🟢)
            - very_low: score >= 90 (✅)
        """
        t0 = time.perf_counter()
        now = self._now()

        if self.log:
            self.log.info(
                f"🔍 Starting wallet evaluation for {address}",
                extra={
                    "event": "evaluation_start",
                    "address": address,
                    "mode": mode,
                    "include_balance": include_balance,
                }
            )

        # ========== STEP 1: Fetch blockchain data ==========
        if self.log:
            self.log.info("📊 Step 1/3: Fetching blockchain data from Etherscan", extra={"event": "fetch_start"})

        try:
            txs = self._get_txlist(address)
            internal = self._get_internal_tx(address)
            tokentx = self._get_token_txs(address)
            meta = self._get_contract_meta(address)
            balance_wei = self.get_eth_balance(address) if include_balance else None

            if self.log:
                self.log.info(
                    "✅ Data fetch complete",
                    extra={
                        "event": "fetch_complete",
                        "tx_count": len(txs),
                        "internal_count": len(internal),
                        "token_tx_count": len(tokentx),
                        "has_balance": balance_wei is not None,
                    }
                )

        except Exception as e:
            if self.log:
                self.log.error(
                    f"❌ Fatal: Failed to fetch blockchain data - {str(e)}",
                    extra={"event": "fetch_failed", "error": str(e), "address": address}
                )

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

        # ========== STEP 2: Analyze blockchain data ==========
        if self.log:
            self.log.info("🧮 Step 2/3: Analyzing transaction patterns", extra={"event": "analysis_start"})

        # Calculate basic metrics
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

        # Log analysis summary
        if self.log:
            age_str = "N/A" if first_ts is None else f"{(now - first_ts) // 86400} days"
            last_activity_str = "N/A" if last_ts is None else f"{(now - last_ts) // 86400} days ago"

            self.log.info(
                f"📈 Analysis: {'Empty' if empty_wallet else 'Active'} wallet, Age: {age_str}, Last activity: {last_activity_str}",
                extra={
                    "event": "analysis_summary",
                    "empty_wallet": empty_wallet,
                    "has_history": has_eth_history,
                    "balance_eth": balance_eth,
                    "age_days": (now - first_ts) // 86400 if first_ts else None,
                    "inactive_days": (now - last_ts) // 86400 if last_ts else None,
                }
            )

        # ========== STEP 3: Apply risk scoring rules ==========
        if self.log:
            self.log.info(
                f"⚖️  Step 3/3: Applying {11} security rules (Base score: {BASE_SCORE})",
                extra={"event": "scoring_start", "base_score": BASE_SCORE}
            )

        score = BASE_SCORE
        reasons: List[Reason] = []

        # Define all risk rules in order
        rules = [
            ("Empty Wallet Check", self._rule_empty_wallet, (has_eth_history, balance_eth)),
            ("Transaction History", self._rule_no_history, (has_eth_history,)),
            ("Wallet Age", self._rule_age, (now, first_ts)),
            ("Inactivity Period", self._rule_inactivity, (now, last_ts)),
            ("Failed Transaction Ratio", self._rule_fail_ratio, (txs,)),
            ("Unique Counterparties", self._rule_unique_counterparties, (address, recent_90d)),
            ("ETH Dust Detection", self._rule_dust_incoming_eth, (address, recent_90d)),
            ("Token Dust Detection", self._rule_dust_incoming_tokens, (address, token_recent_90d)),
            ("Token-Only Pattern", self._rule_token_only_empty, (has_eth_history, balance_eth, tokentx)),
            ("Contract Verification", self._rule_contract_verification, (meta,)),
            ("Proxy Contract", self._rule_contract_proxy, (meta,)),
        ]

        # Apply each rule and log results
        for rule_name, rule_fn, args in rules:
            delta, reason = rule_fn(*args)
            score += delta
            reasons.append(reason)

            # Log each rule application
            if self.log and delta != 0:  # Only log rules that affected the score
                emoji = "🔴" if delta < 0 else "🟢"
                self.log.info(
                    f"{emoji} Rule: {rule_name} ({delta:+d}) → Score: {score}",
                    extra={
                        "event": "rule_applied",
                        "rule": rule_name,
                        "delta": delta,
                        "new_score": score,
                        "reason": reason.summary,
                    }
                )

        # Clamp score to valid range (0-100)
        score = clamp(int(round(score)))
        elapsed = round(time.perf_counter() - t0, 3)
        tier = self._tier(score)

        # Log final evaluation result
        if self.log:
            tier_emoji = {"critical":"🛑","high":"⚠️","medium":"🟡","low":"🟢","very_low":"✅"}[tier]
            rules_triggered = sum(1 for r in reasons if r.delta != 0)
            self.log.info(
                f"{tier_emoji} Evaluation Complete: Score {score}/100 ({tier.replace('_', ' ').title()}) - {rules_triggered} rules triggered in {elapsed:.2f}s",
                extra={
                    "event": "evaluation_complete",
                    "address": address,
                    "final_score": score,
                    "tier": tier,
                    "empty_wallet": empty_wallet,
                    "rules_triggered": rules_triggered,
                    "elapsed_seconds": elapsed,
                }
            )

        if mode == "score":
            return score

        # Build human-friendly wallet details
        wallet_details = self._build_wallet_details(
            address, balance_eth, txs, internal, tokentx,
            first_ts, last_ts, has_eth_history
        )

        return {
            "score": score,
            "tier": tier,
            "empty_wallet": empty_wallet,
            "reasons": [asdict(r) for r in reasons],
            "metrics": metrics,
            "wallet_details": wallet_details,
            "elapsed_s": elapsed,
        }

    @staticmethod
    def _tier(score: int) -> str:
        if score < 20: return "critical"
        if score < 40: return "high"
        if score < 70: return "medium"
        if score < 90: return "low"
        return "very_low"

    def _build_wallet_details(
        self,
        address: str,
        balance_eth: float,
        txs: List[Dict[str, Any]],
        internal: List[Dict[str, Any]],
        tokentx: List[Dict[str, Any]],
        first_ts: Optional[int],
        last_ts: Optional[int],
        has_eth_history: bool,
    ) -> Dict[str, Any]:
        """Build human-friendly wallet details."""

        def format_timestamp(ts: Optional[int]) -> str:
            if ts is None:
                return "N/A"
            return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S UTC")

        def format_age(ts: Optional[int]) -> str:
            if ts is None:
                return "N/A"
            age_seconds = int(time.time()) - ts
            days = age_seconds // 86400
            if days == 0:
                hours = age_seconds // 3600
                return f"{hours} hours"
            elif days < 30:
                return f"{days} days"
            elif days < 365:
                months = days // 30
                return f"{months} months"
            else:
                years = days // 365
                return f"{years} years"

        # Get recent transactions (last 5)
        recent_txs = []
        all_txs = sorted(txs + internal, key=lambda x: int(x.get("timeStamp", "0")), reverse=True)
        for tx in all_txs[:5]:
            recent_txs.append({
                "hash": tx.get("hash", ""),
                "from": tx.get("from", ""),
                "to": tx.get("to", ""),
                "value_eth": wei_to_eth(tx.get("value", "0")),
                "timestamp": format_timestamp(int(tx.get("timeStamp", "0"))),
                "is_error": tx.get("isError") == "1",
            })

        # Get token summary
        token_summary = {}
        for tx in tokentx:
            symbol = tx.get("tokenSymbol", "UNKNOWN")
            if symbol not in token_summary:
                token_summary[symbol] = {
                    "name": tx.get("tokenName", "Unknown Token"),
                    "contract": tx.get("contractAddress", ""),
                    "tx_count": 0,
                }
            token_summary[symbol]["tx_count"] += 1

        return {
            "address": address,
            "balance": {
                "eth": balance_eth,
                "eth_formatted": f"{balance_eth:.6f} ETH",
            },
            "activity": {
                "first_seen": format_timestamp(first_ts),
                "last_seen": format_timestamp(last_ts),
                "wallet_age": format_age(first_ts),
                "inactive_for": format_age(last_ts) if last_ts else "N/A",
                "has_history": has_eth_history,
            },
            "transactions": {
                "total": len(txs),
                "internal": len(internal),
                "token_transfers": len(tokentx),
                "recent": recent_txs,
            },
            "tokens": {
                "unique_tokens": len(token_summary),
                "summary": list(token_summary.values())[:10],  # Top 10 tokens
            },
        }

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
