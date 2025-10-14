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
