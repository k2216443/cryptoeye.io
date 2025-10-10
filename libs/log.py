"""
log.py
-------
Lightweight JSON-based logging utility for structured log output.

Each log entry is printed as a JSON object with keys such as:
{
    "module": "etherscan",
    "level": "debug",
    "message": "Fetched balance",
    "time": "optional_custom_field"
}

Environment variables:
    LOG_DEBUG: controls whether error-level logs are printed.
                - "on":   error logs are printed
                - other:  error logs suppressed (default: "off")
"""

import json
import os
import time

LOG_DEBUG = os.getenv("LOG_DEBUG", "off")


class Log:
    """
    Log provides simple structured logging with module tagging.
    Output is JSON for easy parsing by log aggregators (Fluent Bit, Loki, etc.).
    """

    def __init__(self, module: str):
        """
        Initialize the logger for a specific module.

        Args:
            module (str): Name of the module or component generating logs.
        """
        self.module = module

    def _print(self, level: str, *args, **kwargs):
        """
        Internal helper to print a structured JSON log entry.

        Args:
            level (str): Log level ("debug", "error", etc.).
            *args: Positional arguments concatenated into a single message string.
            **kwargs: Additional key-value pairs to include in the log entry.

        Example:
            self._print("debug", "Fetched data", time="0.123s")
        """        
        payload = {
            "module": self.module,
            "level": level,

             # current UNIX timestamp with milliseconds
            "time": round(time.time(), 3)
        }

        if args:
            payload["message"] = " ".join(str(a) for a in args)

        payload.update(kwargs)
        print(json.dumps(payload, ensure_ascii=False), flush=True)

    def debug(self, *args, **kwargs):
        """
        Print a debug-level log message.

        Args:
            *args: Message components concatenated with spaces.
            **kwargs: Additional fields to include in the log.

        Example:
            log.debug("Fetching balance", address=addr, time="0.045s")
        """
        if LOG_DEBUG != "on":
            return
        self._print("debug", *args, **kwargs)

    def error(self, *args, **kwargs):
        """
        Print an error-level log message if LOG_DEBUG == "on".

        Args:
            *args: Message components concatenated with spaces.
            **kwargs: Additional fields to include in the log.

        Example:
            log.error("Failed to connect", code=500)
        """
        self._print("error", *args, **kwargs)
