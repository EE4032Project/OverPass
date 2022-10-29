import json
import random
from solcx import compile_standard, install_solc
import traceback
from web3 import Web3, middleware
from web3.gas_strategies.time_based import medium_gas_price_strategy

HTTP_PROVIDER = "http://127.0.0.1:8545"
MIDIUM_GAS_PRICE_ESTIMATOR_ON = False


class OverPassException(Exception):
    def __init__(self, _type="py",_message="OverPassError"):
        self.message = _message
        self.type = _type
        super().__init__(self.message)

     def __str__(self):
        return f'OverPassError: {self.type} -> {self.message}'



class LCSOverPass:
    contract_address = ""
    nonce = 0

    def __init__(self,_http_provider:str, _my_address:str, _private_key:str, _contract_address=""):

        self.private_key = _private_key
        self.my_address = _my_address
        self.contract_address = _contract_address
        self.overpass_instance = None
        self.http_provider = _http_provider



        with open("./overpass/contracts/LCS_overpass.sol", "r") as file:
            LCS_overpass = file.read()
        with open("./overpass/contracts/overpass.sol", "r") as file:
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


        with open("./overpass/compiled_code.json", "w") as file:
            json.dump(compiled_sol, file)

        # get bytecode version
        self.bytecode = compiled_sol["contracts"]["./LCS_overpass.sol"]["LCSOverPass"]["evm"]["bytecode"]["object"]

        # get abi
        self.abi = compiled_sol["contracts"]["./LCS_overpass.sol"]["LCSOverPass"]["abi"]

        # connect to ganache

        self.w3 = Web3(Web3.HTTPProvider(self.http_provider))
        self.nonce = self.w3.eth.getTransactionCount(self.my_address)
        self.chain_id = self.w3.eth.chain_id
        # open to use medium gas price estimation
        #self.w3.eth.set_gas_price_strategy(medium_gas_price_strategy)

        self.w3.middleware_onion.add(middleware.time_based_cache_middleware)
        self.w3.middleware_onion.add(middleware.latest_block_based_cache_middleware)
        self.w3.middleware_onion.add(middleware.simple_cache_middleware)

    def setAddress(self, _contract_address: str, _abi=self.abi):
        self.contract_address = _contract_address
        self.abi = _abi
        try:
            self.overpass_instance  = web3.eth.contract(address=self.contract_address, abi=_abi)
        except:
            raise OverPassException("py", traceback.format_exc())



    def deploy(self):
        if self.overpass_instance == None
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
                raise OverPassException("sol", traceback.format_exc())
        else:
            raise OverPassException("py", "Contract deployed already")


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
            raise OverPassException("solidity", traceback.format_exc())



    def getTaskApproxGasFee(self,taskId:int):
        return self.overpass_instance.functions.getTaskApproxGasFee(taskId).call()





class Miner:
    def __init__(self,_my_address:str, _private_key:str):
        self.private_key = _private_key
        self.my_address = _my_address
        with open("./overpass/compiled_code.json", "w") as file:
            json.dump(compiled_sol, file)
        self.abi = compiled_sol["contracts"]["./LCS_overpass.sol"]["LCSOverPass"]["abi"]

        # define function to handle events and print to the console
    def handle_event(self,event):
        print(Web3.toJSON(event))
        # and whatever




    # asynchronous defined function to loop
    # this loop sets up an event filter and is looking for new entires for the "PairCreated" event
    # this loop runs on a poll interval
    async def log_loop(self, event_filter, poll_interval):
        while True:
            for PairCreated in event_filter.get_new_entries():
                handle_event(PairCreated)
            await asyncio.sleep(poll_interval)



my_address = "0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1"
private_key = "0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d"


oP_LCS = LCSOverPass(my_address,private_key)

print(oP_LCS.deploy())

print(oP_LCS.delegate_compute("jshdikalk","jdhsifnsd", 10**18))

print(oP_LCS.getTaskApproxGasFee(1))

with open("./testnet/key.json", "w") as file:
    json.dump(keys, file)

print("keys:")
print(keys)
