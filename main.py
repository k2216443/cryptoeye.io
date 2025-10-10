
from providers.etherscan import Etherscan


if __name__ == "__main__":

    etherscan = Etherscan()
    etherscan.get_eth_balance(address="0x4838B106FCe9647Bdf1E7877BF73cE8B0BAD5f97")
    etherscan.evaluate_address_security(address="0x4838B106FCe9647Bdf1E7877BF73cE8B0BAD5f97", mode="full")