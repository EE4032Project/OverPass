'''
MIT License

Copyright (c) 2022 OverPass-Project

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


'''

from Crypto.Hash import keccak
import json
import logging
import os
import queue
import random
import requests
from solcx import compile_standard, install_solc
import sys
import time
import traceback

import web3
from web3 import Web3, middleware
from web3.gas_strategies.time_based import medium_gas_price_strategy

from overpass.py.constant import MIDIUM_GAS_PRICE_ESTIMATOR_ON, HTTP_PROVIDER, STD_LOGGING_ON,FILE_LOGGING_ON, GAS_PRICE_STRATEGY_ON, API_KEY
from overpass.py.utils import thread_with_trace, lock, get_testcase, OverPassException



# An LCSOverPass Wrapper for user to easily deploy and calculate LCS
class LCSOverPass:
    contract_address = ""
    nonce = 0

    def __init__(self,_http_provider:str, _my_address:str, _private_key:str, _contract_address=""):

        self.private_key = _private_key
        self.my_address = _my_address
        self.contract_address = _contract_address
        self.overpass_instance = None
        self.http_provider = _http_provider



        # Compile the solidity

        compiled_sol = self.compileLCSOverPass()



        # get bytecode version
        self.bytecode = compiled_sol["contracts"]["./LCS_overpass.sol"]["LCSOverPass"]["evm"]["bytecode"]["object"]

        # get abi
        self.abi = compiled_sol["contracts"]["./LCS_overpass.sol"]["LCSOverPass"]["abi"]

        # connect to ganache

        self.w3 = Web3(Web3.HTTPProvider(self.http_provider))

        self.chain_id = self.w3.eth.chain_id
        # open to use medium gas price estimation
        if MIDIUM_GAS_PRICE_ESTIMATOR_ON==True:
            self.w3.eth.set_gas_price_strategy(medium_gas_price_strategy)
        self.w3.middleware_onion.add(middleware.time_based_cache_middleware)
        self.w3.middleware_onion.add(middleware.latest_block_based_cache_middleware)
        self.w3.middleware_onion.add(middleware.simple_cache_middleware)
        self.nonce = self.w3.eth.getTransactionCount(self.my_address) -1
        self.feePerGas = self.estimateGasPrice() if GAS_PRICE_STRATEGY_ON else self.w3.eth.gas_price

        keccak_hash = keccak.new(digest_bits=256)
        keccak_hash.update(b'lcs(string,string)')
        self.problemSig=keccak_hash.hexdigest()[0:8]

    @staticmethod
    def estimateGasPrice():
        url = "https://api.owlracle.info/v3/eth/gas?apikey="+API_KEY if API_KEY!="" else 'https://api.owlracle.info/v3/eth/gas'
        res = requests.get(url)
        data = res.json()
        # average price 2022
        feePerGas = 20*(10**9)
        try:
            feePerGas = int(data['speeds'][0]["maxFeePerGas"])*(10**9)
        except:
            print(traceback.format_exc())
            # average price 2022
            feePerGas = 20*(10**9)
        return feePerGas
        # the unit is GWei

    def updateNonce(self):
        self.nonce += 1
        
        

    @staticmethod
    # Compile LCSOverPass code
    def compileLCSOverPass():
        with open("./overpass/contracts/LCS_overpass.sol", "r") as file:
            LCS_overpass = file.read()
        with open("./overpass/contracts/overpass.sol", "r") as file:
            overpass = file.read()
        install_solc("0.8.7")
        compiled_sol = compile_standard({
                "language": "Solidity",
                # sources should be added here if other .sol is imported
                "sources": {"./LCS_overpass.sol": {"content": LCS_overpass}, "./overpass.sol":{"content": overpass}},
                "settings": {
                    "outputSelection": {
                        "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
                    }
                },
            },
            solc_version="0.8.7",
        )

        path = "build"
        # Check whether the specified path exists or not
        isExist = os.path.exists(path)
        if not isExist:
            # Create a new directory because it does not exist
            os.makedirs(path)
        print(f"The new directory {path} is created!")

        with open("./build/lcs_overpass_compiled_code.json", "w") as file:
            json.dump(compiled_sol, file)
        return compiled_sol
    
    # set contract address for a Contracts
    def setAddress(self, _contract_address: str, _abi:str):
        self.contract_address = _contract_address
        self.abi = _abi
        try:
            self.overpass_instance  = web3.eth.contract(address=self.contract_address, abi=_abi)
        except:
            raise OverPassException("py", traceback.format_exc())

    # depoy contract
    def deploy(self):
        if self.overpass_instance == None:
            # 1.  Build a transaction
            overpassContract = self.w3.eth.contract(abi=self.abi, bytecode=self.bytecode)
            self.updateNonce()
            transaction = overpassContract.constructor().buildTransaction({"chainId": self.chain_id, "gasPrice": int(self.feePerGas), "from": self.my_address, "nonce": self.nonce})
            # 2. Sign a transaction
            signed_txn = self.w3.eth.account.sign_transaction( transaction, private_key=self.private_key)
            # 3. Send a transaction
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            try:
                contract_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
                self.overpass_instance = self.w3.eth.contract( address=contract_receipt.contractAddress, abi=self.abi)
                self.contract_address = contract_receipt.contractAddress
                return contract_receipt

            except:
                raise OverPassException("sol", traceback.format_exc())
        else:
            raise OverPassException("py", "Contract deployed already")

    # delegate a contract
    def delegate_compute(self, str1:str, str2: str, _incentive: int):
        self.updateNonce()
        gasLimit = int(min((max(len(str1),len(str2))*2/10000+1)*3*10**6, self.w3.eth.get_block('latest')['gasLimit']))
        transaction = self.overpass_instance.functions.delegate_compute([self.problemSig,str1,str2], 2).buildTransaction(
            {"chainId": self.chain_id, "from": self.my_address, "gasPrice": int(self.feePerGas), "nonce":  self.nonce, "gas": gasLimit, "value":_incentive})
        signed_txn = self.w3.eth.account.sign_transaction(transaction, private_key=self.private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        try:
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            return tx_receipt
        except:
            raise OverPassException("solidity", traceback.format_exc())


    def getTaskApproxGasFee(self,taskId:int):
        return self.overpass_instance.functions.getTaskApproxGasFee(taskId).call()

    def checkAns(self,taskId:int):
        return self.overpass_instance.functions.checkAns(taskId).call()
