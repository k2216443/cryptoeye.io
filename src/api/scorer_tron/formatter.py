from __future__ import annotations
import time
from typing import Any, Dict, Tuple

def format_for_tg_trc(addr: str, result: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
    score = result["score"]; tier = result["tier"]; empty = result["empty_wallet"]; m = result["metrics"]
    reasons = [r for r in result["reasons"] if r["delta"] != 0]
    icon = {"critical":"🛑","high":"⚠️","medium":"🟡","low":"🟢","very_low":"✅"}[tier]

    head = f"{icon} <b>Wallet risk (TRON)</b> • <code>{addr}</code>\n"
    line1 = f"<b>Score:</b> <code>{score}</code> — {tier.replace('_',' ')}"
    badge = " • <b>Empty wallet</b>" if empty else ""

    now = int(time.time())
    age_txt = "n/a" if m.get("first_ts_ms") is None else f"{(now - m['first_ts_ms']//1000) // 86400}d"
    last_txt = "n/a" if m.get("last_ts_ms") is None else f"{(now - m['last_ts_ms']//1000) // 86400}d ago"

    stats = [
        f"<b>TRX tx:</b> {m.get('trx_txs_total',0)}",
        f"<b>TRC20 tx:</b> {m.get('trc20_txs_total',0)}",
        f"<b>Age:</b> {age_txt}",
        f"<b>Last activity:</b> {last_txt}",
    ]
    if m.get("trx_balance") is not None:
        stats.append(f"<b>Balance:</b> {m['trx_balance']:.6f} TRX")

    bullets = "\n".join([f"• {r['summary']} ({'+' if r['delta']>0 else ''}{r['delta']})" for r in reasons])
    reasons_txt = f"\n<b>Why:</b>\n{bullets}" if bullets else ""

    advise = ""
    if empty:
        advise = ("\n<blockquote>Unfunded and unused. Treat as untrusted until funded from a known source."
                  "</blockquote>")

    text = (
        head + f"{line1}{badge}\n" +
        " | ".join(stats) +
        reasons_txt + advise
    )
    kb = {"inline_keyboard":[
        [{"text":"Open in Tronscan","url":f"https://tronscan.org/#/address/{addr}"},
         {"text":"Re-check","callback_data":f"recheck_trc:{addr}"}]
    ]}
    return text, kb
