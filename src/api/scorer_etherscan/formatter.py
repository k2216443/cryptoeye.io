from __future__ import annotations
import time
from typing import Any, Dict, Tuple

def format_for_tg(addr: str, result: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
    score = result["score"]; tier = result["tier"]; empty = result["empty_wallet"]; m = result["metrics"]
    reasons = [r for r in result["reasons"] if r["delta"] != 0]
    icon = {"critical":"🛑","high":"⚠️","medium":"🟡","low":"🟢","very_low":"✅"}[tier]

    head = f"{icon} <b>Wallet risk</b> • <code>{addr}</code>\n"
    line1 = f"<b>Score:</b> <code>{score}</code> — {tier.replace('_',' ')}"
    badge = " • <b>Empty wallet</b>" if empty else ""

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

    bullets = "\n".join([f"• {r['summary']} ({'+' if r['delta']>0 else ''}{r['delta']})" for r in reasons])
    reasons_txt = f"\n<b>Why:</b>\n{bullets}" if bullets else ""

    advise = ""
    if empty:
        advise = ("\n<blockquote>Unfunded and unused. Treat as untrusted until funded from a known source."
                  "</blockquote>")

    text = (
        head + f"{line1}{badge}\n" +
        " | ".join(stats) +
        reasons_txt + advise +
        f"\n\n<a href='https://etherscan.io/address/{addr}'>Etherscan</a>"
    )
    kb = {"inline_keyboard":[[{"text":"Re-check","callback_data":f"recheck:{addr}"}]]}
    return text, kb
