import logging
import os

from pythonjsonlogger import jsonlogger

from providers.etherscan2 import Etherscan

def setup_logging() -> logging.Logger:
    level = os.getenv("LOG_LEVEL", "INFO").upper()
    log_file = os.getenv("LOG_FILE", "/Volumes/touch/github.com/k2216443/chaineye.io/composer/etherscan_2.json.log")

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

if __name__ == "__main__":

    etherscan = Etherscan(logger=log)

    address = "0xde0B295669a9FD93d5F28D9Ec85E40f4cb697BAe"
    result = etherscan.evaluate_address_security(address, mode="full")
    print("Hi")
