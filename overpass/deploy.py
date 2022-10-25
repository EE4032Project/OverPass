import json
import random
from solcx import compile_standard, install_solc
import traceback
from web3 import Web3, middleware
from web3.gas_strategies.time_based import medium_gas_price_strategy






class LCSOverPass:
    contract_address = ""
    nonce = 0

    def __init__(self, _my_address:str, _private_key:str, _contract_address=""):

        self.private_key = _private_key
        self.my_address = _my_address
        self.contract_address = _contract_address



        with open("./contracts/LCS_overpass.sol", "r") as file:
            LCS_overpass = file.read()
        with open("./contracts/overpass.sol", "r") as file:
            overpass = file.read()

        # Compile the solidity

        install_solc("0.8.7")
        compiled_sol = compile_standard({
                "language": "Solidity",
                "sources": {"./LCS_overpass.sol": {"content": LCS_overpass}, "./overpass.sol":{"content": overpass}},
                "settings": {
                    "outputSelection": {
                        "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
                    }
                },
            },
            solc_version="0.8.7",
        )


        with open("compiled_code.json", "w") as file:
            json.dump(compiled_sol, file)

        # get bytecode version
        self.bytecode = compiled_sol["contracts"]["./LCS_overpass.sol"]["LCSOverPass"]["evm"]["bytecode"]["object"]

        # get abi
        self.abi = compiled_sol["contracts"]["./LCS_overpass.sol"]["LCSOverPass"]["abi"]

        # connect to ganache

        self.w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
        self.nonce = self.w3.eth.getTransactionCount(self.my_address)
        self.chain_id = self.w3.eth.chain_id
        self.w3.eth.set_gas_price_strategy(medium_gas_price_strategy)

        self.w3.middleware_onion.add(middleware.time_based_cache_middleware)
        self.w3.middleware_onion.add(middleware.latest_block_based_cache_middleware)
        self.w3.middleware_onion.add(middleware.simple_cache_middleware)

    def deploy(self):
        # 1.  Build a transaction
        overpassContract = self.w3.eth.contract(abi=self.abi, bytecode=self.bytecode)
        transaction = overpassContract.constructor().buildTransaction({"chainId": self.chain_id, "gasPrice": self.w3.eth.gas_price, "from": self.my_address, "nonce": self.nonce})
        # 2. Sign a transaction
        signed_txn = self.w3.eth.account.sign_transaction( transaction, private_key=self.private_key)
        # 3. Send a transaction
        tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        try:
            contract_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

            # Working with contracts
            # 1. Contract addresses
            # 2. Contract ABI
            self.overpass_instance = self.w3.eth.contract( address=contract_receipt.contractAddress, abi=self.abi)
            self.contract_address = "0x5f8e26fAcC23FA4cbd87b8d9Dbbd33D5047abDE1"
            return contract_receipt

        except:
            return traceback.format_exc()

    def delegate_compute(self, str1:str, str2: str, _incentive: int):
        transaction = self.overpass_instance.functions.delegate_compute(['LCS',str1,str2], 2).buildTransaction(
            {"chainId": self.chain_id, "from": self.my_address, "gasPrice": self.w3.eth.gas_price, "nonce": self.nonce+1, "gas": 3*10**6, "value":_incentive})
        signed_txn = self.w3.eth.account.sign_transaction(transaction, private_key=self.private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        try:
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            self.nonce =self.nonce + 1
            return tx_receipt
        except:
            return traceback.format_exc()

    

    def getTaskApproxGasFee(self,taskId:int):
        return self.overpass_instance.functions.getTaskApproxGasFee(taskId).call()







my_address = "0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1"
private_key = "0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d"


oP_LCS = LCSOverPass(my_address,private_key)

print(oP_LCS.deploy())

print(oP_LCS.delegate_compute("jshdikalk","jdhsifnsd", 10**18))

print(oP_LCS.getTaskApproxGasFee(1))

other_addresses = ["0xFFcf8FDEE72ac11b5c542428B35EEF5769C409f0",
                   "0x22d491Bde2303f2f43325b2108D26f1eAbA1e32b",
                   "0xE11BA2b4D45Eaed5996Cd0823791E0C93114882d",
                   "0xd03ea8624C8C5987235048901fB614fDcA89b117",
                   "0x95cED938F7991cd0dFcb48F0a06a40FA1aF46EBC",
                   "0x3E5e9111Ae8eB78Fe1CC3bb8915d5D461F3Ef9A9",
                   "0x28a8746e75304c0780E011BEd21C72cD78cd535E",
                   "0xACa94ef8bD5ffEE41947b4585a84BdA5a3d3DA6E",
                   "0x1dF62f291b2E969fB0849d99D9Ce41e2F137006e"
                   ]
other_private_keys = [
    "0x6cbed15c793ce57650b9877cf6fa156fbef513c4e6134f022a85b1ffdd59b2a1",
    "0x6370fd033278c143179d81c5526140625662b8daa446c22ee2d73db3707e620c",
    "0x646f1ce2fdad0e6deeeb5c7e8e5543bdde65e86029e2fd9fc169899c440a7913",
    "0xadd53f9a7e588d003326d1cbf9e4a43c061aadd9bc938c843a79e7b4fd2ad743",
    "0x395df67f0c2d2d9fe1ad08d1bc8b6627011959b79c53d7dd6a3536a33ab8a4fd",
    "0xe485d098507f54e7733a205420dfddbe58db035fa577fc294ebd14db90767a52",
    "0xa453611d9419d0e56f499079478fd72c37b251a94bfde4d19872c44cf65386e3",
    "0x829e924fdf021ba3dbbc4225edfece9aca04b929d6e75613329ca6f1d31c0bb4",
    "0xb0057716d5917badaf911b193b12b910811c1497b5bada8d7711f758981c3773"
]


