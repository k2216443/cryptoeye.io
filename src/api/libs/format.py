def format_security_message(addr: str, score: int) -> str:
    """
    Return a formatted HTML message for Telegram based on risk score.
    """
    if score < 20:
        icon, label, note = "🛑", "Critical risk", "⚠️ Avoid any interaction."
    elif score < 40:
        icon, label, note = "⚠️", "High risk", "Be cautious."
    elif score < 70:
        icon, label, note = "🟡", "Medium risk", "Use with care."
    elif score < 90:
        icon, label, note = "🟢", "Low risk", "Looks safe, but stay alert."
    else:
        icon, label, note = "✅", "Very low risk", "No issues detected."

    return (
        f"{icon} <b>Wallet Security Report</b>\n"
        f"<b>Address:</b> <code>{addr}</code>\n"
        f"<b>Score:</b> <code>{score}</code> — {label}\n"
        f"{note}\n\n"
        f"<a href='https://etherscan.io/address/{addr}'>View on Etherscan</a>"
    )