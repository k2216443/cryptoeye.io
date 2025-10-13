# lambda_function.py
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from mangum import Mangum
import re
from providers.etherscan import Etherscan

ADDR_RE = re.compile(r"^0x[a-fA-F0-9]{40}$")
app = FastAPI()
scanner = Etherscan()


@app.get("/evaluate")
def evaluate(addr: str = Query(..., description="Ethereum address 0x...")):
    if not ADDR_RE.fullmatch(addr):
        return JSONResponse(
            status_code=400,
            content={"ok": False, "error": "invalid address format"},
        )
    result = scanner.evaluate_address_security(address=addr, mode="full")
    return JSONResponse({"ok": True, "address": addr, "result": result})


# Lambda handler
handler = Mangum(app)
