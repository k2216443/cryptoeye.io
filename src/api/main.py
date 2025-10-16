import re
from typing import Any, Dict
from contextlib import asynccontextmanager
from functools import partial

import json

import anyio
from fastapi import FastAPI, Query, Request
from fastapi.responses import JSONResponse

from providers.etherscan import Etherscan

ADDR_RE = re.compile(r"^0x[a-fA-F0-9]{40}$")


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.scanner = Etherscan()
    yield


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
    # best-effort JSON body
    body_json: Any = None
    body_text: str | None = None
    try:
        body_json = await request.json()
        if isinstance(body_json, dict):
            body_json = redact_dict(body_json)
    except Exception:
        raw = await request.body()
        body_text = raw.decode("utf-8", "ignore")[:10000] if raw else None  # cap length

    log_payload = {
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
    print(json.dumps(log_payload, ensure_ascii=False))

    return JSONResponse(status_code=200, content={"ok": True})

@app.get("/evaluate")
async def evaluate(request: Request, addr: str = Query(..., description="Ethereum address 0x...")) -> JSONResponse:

    print(json.dumps({
        "event": "evaluate_start",
        "addr": addr,
        "headers": redact_headers(request.headers)
    }))
        
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
