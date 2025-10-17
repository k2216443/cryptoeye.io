import re
import json
import anyio
import logging
import os

from typing import Any, Dict, Optional
from contextlib import asynccontextmanager
from functools import partial

from fastapi import FastAPI, Query, Request
from fastapi.responses import JSONResponse

from providers.etherscan import Etherscan
from libs.tg import TelegramBot

from pythonjsonlogger import jsonlogger

ADDR_RE = re.compile(r"^0x[a-fA-F0-9]{40}$")

# optional: request-id from proxies / gateways
def get_request_id(request: Request) -> Optional[str]:
    return request.headers.get("x-request-id") or request.headers.get("x-correlation-id")

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.scanner = Etherscan()
    yield

def setup_logging() -> logging.Logger:
    level = os.getenv("LOG_LEVEL", "INFO").upper()
    log_file = os.getenv("LOG_FILE", "/var/log/cryptoeye.json.log")

    # Ensure directory exists
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    root = logging.getLogger()
    root.setLevel(level)

    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s %(event)s %(request_id)s",
        rename_fields={"levelname": "level"},
    )

    # Console
    sh = logging.StreamHandler()
    sh.setFormatter(formatter)

    # File (rotating optional)
    fh = logging.FileHandler(log_file)
    fh.setFormatter(formatter)

    root = logging.getLogger()
    root.handlers = [sh, fh]
    root.setLevel(level)

    # align uvicorn loggers
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        lg = logging.getLogger(name)
        lg.handlers = [sh, fh]
        lg.setLevel(level)
        lg.propagate = False

    lg = logging.getLogger("cryptoeye")

    # inherit handler
    lg.propagate = True 
    return lg

log = setup_logging()
app = FastAPI(title="Wallet Security Evaluator", lifespan=lifespan)

def is_valid_eth_address(addr: str) -> bool:
    return bool(ADDR_RE.fullmatch(addr))

SENSITIVE = {"authorization", "cookie", "set-cookie", "x-api-key"}
def redact_headers(hdrs):
    out = {}
    for k, v in hdrs.items():
        lk = k.lower()
        out[lk] = "***" if lk in SENSITIVE else v
    return out

def redact_dict(d: Dict[str, Any]) -> Dict[str, Any]:
    return {k: ("***" if k.lower() in SENSITIVE else v) for k, v in d.items()}

@app.get("/health")
async def evaluate(request: Request) -> JSONResponse:
    return JSONResponse(
        status_code=200,
        content={"ok": True}
    )

@app.api_route("/t", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def trace(request: Request) -> JSONResponse:
    req_id = get_request_id(request)

    # best-effort JSON body
    body_json: Any = None
    body_text: Optional[str] = None
    try:
        body_json = await request.json()
        if isinstance(body_json, dict):
            body_json = redact_dict(body_json)
    except Exception:
        raw = await request.body()
        body_text = raw.decode("utf-8", "ignore")[:10000] if raw else None  # cap length

    payload = {
        "event": "trace_request",
        "method": request.method,
        "url": str(request.url),
        "client": getattr(request.client, "host", None),
        "headers": redact_headers(request.headers),
        "query": redact_dict(dict(request.query_params)),
        "cookies": redact_dict(request.cookies),
        "path_params": request.path_params,
        "body_json": body_json,
        "body_text": body_text,
    }

    # message kept short; details ride in extra fields for JSON logger
    log.info("trace", extra={**payload, "request_id": req_id})

    addr = body_json["text"]
    if not is_valid_eth_address(addr):
        return JSONResponse(
            status_code=400,
            content={"ok": False, "error": "invalid address format, expected 0x + 40 hex chars"},
        )


    etherscan = Etherscan()
    tg = TelegramBot(bot_token=os.getenv("BOT_TOKEN"))
    security = etherscan.evaluate_address_security(address=addr)
    tg.send_message(chat_id=body_json["chat"]["id"], text=security)

    
    # return JSONResponse(status_code=200, content={"ok": True})


@app.get("/evaluate")
async def evaluate(request: Request, addr: str = Query(..., description="Ethereum address 0x...")) -> JSONResponse:

        
    if not is_valid_eth_address(addr):
        return JSONResponse(
            status_code=400,
            content={"ok": False, "error": "invalid address format, expected 0x + 40 hex chars"},
        )

    scanner: Etherscan = app.state.scanner
    fn = partial(scanner.evaluate_address_security, address=addr, mode="full")
    result: Dict[str, Any] = await anyio.to_thread.run_sync(fn)

    return JSONResponse(content={"ok": True, "address": addr, "result": result})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
