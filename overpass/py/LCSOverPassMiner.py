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
from overpass.py.LCSOverPass import LCSOverPass

# OverPass miner
class LCSOverPassMiner:
    def __init__(self,_http_provider:str, _my_address:str, _private_key:str):
        self.http_provider = _http_provider
        self.private_key = _private_key
        self.my_address = _my_address
        compiled_sol = LCSOverPass.compileLCSOverPass()
        self.abi = compiled_sol["contracts"]["./LCS_overpass.sol"]["LCSOverPass"]["abi"]
        self.w3 = Web3(Web3.HTTPProvider(self.http_provider))
        self.chain_id = self.w3.eth.chain_id
        # open to use medium gas price estimation
        if MIDIUM_GAS_PRICE_ESTIMATOR_ON==True:
            self.w3.eth.set_gas_price_strategy(medium_gas_price_strategy)
        self.w3.middleware_onion.add(middleware.time_based_cache_middleware)
        self.w3.middleware_onion.add(middleware.latest_block_based_cache_middleware)
        self.w3.middleware_onion.add(middleware.simple_cache_middleware)
        self.minIncentive = 1000
        self.maximumDuration = 5
        self.listeningAddresses = {}
        self.q = queue.Queue()
        self.nonce = self.w3.eth.getTransactionCount(self.my_address) -1
        self.blocknumber =0
        self.feePerGas = self.estimateGasPrice() if GAS_PRICE_STRATEGY_ON else self.w3.eth.gas_price
        self.incentiveGot = 0
    

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


        

    def addContract(self,addr: str):
        self.listeningAddresses[addr] = None

    
    def updateNonce(self):
        self.nonce += 1
        

    # define function to handle events and print to the console
    def handle_event(self,event):
        eventInfo = json.loads(Web3.toJSON(event))
        #print(taskInfo)
        taskInfoStr = "<new task begin>\n taskId:{taskId}\n incentive:{incentive}\n approxGasFee:{approxGasFee}\n taskParameters:{taskParameters}\n<new task end>\n\n\n".format(taskId=str(eventInfo['args']["taskId"]),incentive=str(eventInfo['args']["incentive"]),approxGasFee=str(eventInfo['args']["approxGasFee"]),taskParameters=str(eventInfo['args']["taskParameters"]))

        logging.info(taskInfoStr)
        if int(eventInfo['args']["incentive"]) >= self.minIncentive and int(eventInfo['args']["computePeriod"]) < self.maximumDuration:
            llcs, lcs = self.lcs(eventInfo['args']["taskParameters"][1],eventInfo['args']["taskParameters"][2])
            logging.info("answer: \n llcs:{llcs}\n lcs:{lcs}".format(llcs=llcs, lcs=lcs))
            contract_address = eventInfo['address']
            try:
                self.updateNonce()
                op_instance = self.w3.eth.contract(address=contract_address , abi=self.abi)
                transaction = op_instance.functions.advise(eventInfo['args']['taskId'], llcs, [lcs]).buildTransaction({"chainId": self.chain_id, "from": self.my_address, "gasPrice": int(self.feePerGas), "nonce":  self.nonce, "gas": 3*10**6})
                signed_txn = self.w3.eth.account.sign_transaction(transaction, private_key=self.private_key)
                tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
                tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
                logging.info("succeed to advise task "+str(eventInfo['args']['taskId'])+" \n"+str(tx_receipt))
                self.q.put([contract_address,str(eventInfo['args']['taskId'])])
                self.incentiveGot += int(eventInfo['args']["incentive"])
            except:
                print(traceback.format_exc())
                self.feePerGas*=1.5
                logging.info("failed to advise task "+str(eventInfo['args']['taskId'])+traceback.format_exc())

        else:
            logging.info("Not interested task, taskId:"+str(eventInfo['args']['taskId'])+traceback.format_exc())



    # asynchronous defined function to loop
    # this loop sets up an event filter and is looking for new entires for the "PairCreated" event
    # this loop runs on a poll interval
    def log_loop(self, event_filter, poll_interval):
        while True:
            for newQuestion in event_filter.get_new_entries():
                self.handle_event(newQuestion)
            time.sleep(poll_interval)

    # listen to postNewQuestion event of contract _addr
    def listen(self, _addr:str):
        
        if _addr not in self.listeningAddresses or self.listeningAddresses[_addr] == None:
            try:
                op_instance = self.w3.eth.contract(address=_addr, abi=self.abi)
                event_filter= op_instance.events.postNewQuestion.createFilter(fromBlock='latest')
                self.listeningAddresses[_addr]=thread_with_trace(target=self.log_loop, args=(event_filter, 2))
                self.listeningAddresses[_addr].start()
                print("Start listening on address:", _addr)

            except:
                raise OverPassException("py", traceback.format_exc())

    # unlisten to postNewQuestion event of contract _addr 
    def unlisten(self, _addr:str):
        if _addr in self.listeningAddresses and self.listeningAddresses[_addr]!=None:
            try:
                self.listeningAddresses[_addr].kill()
                self.listeningAddresses[_addr].join()
                self.listeningAddresses[_addr] = None
                if not t1.isAlive():
                    print('thread killed')
            except:
                raise OverPassException("py", traceback.format_exc())

    def get_incentive(self):
        cnt = 0
        print("totalIncentiveGot:", self.incentiveGot)
        while not self.q.empty():
            task = self.q.get(block=False)
            try:
                self.updateNonce()
                contract_address = task[0]
                taskId = int(task[1])
                op_instance = self.w3.eth.contract(address=contract_address , abi=self.abi)
                transaction = op_instance.functions.getIncentive(taskId).buildTransaction({"chainId": self.chain_id, "from": self.my_address, "gasPrice": int(self.feePerGas), "nonce":  self.nonce, "gas": 3*10**6})
                signed_txn = self.w3.eth.account.sign_transaction(transaction, private_key=self.private_key)
                tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
                tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
                logging.info("succeed to get incentive of  task "+contract_address+":"+str(taskId)+" \n"+str(tx_receipt))
                cnt += 1
                break
            except:
                self.q.put(task)
                self.feePerGas *= 1.5
                logging.info("failed to get incentive of  task "+contract_address+":"+str(taskId)+" \n")
                print(traceback.format_exc())
        return cnt



    def lcs(self,str1, str2):
        m = len(str1)
        n = len(str2)

        dp = [[0]*(n+1) for i in range(m+1)]

        for i in range(m+1):
            for j in range(n+1):
                if (i==0 or j==0):
                    dp[i][j] = 0
                elif (str1[i-1]==str2[j-1]):
                    dp[i][j] = dp[i-1][j-1]+1
                else:
                    dp[i][j] = max(dp[i-1][j],dp[i][j-1])
        llcs = dp[m][n]
        i = m
        j = n
        slcs = ""

        while i>0 and j>0:
            if (str1[i-1]==str2[j-1]):
                slcs = str1[i-1]+slcs;
                i-=1
                j-=1
            elif (dp[i-1][j]>dp[i][j-1]):
                i-=1
            else:
                j-=1

        return dp[m][n], slcs


# frank test and optimize
def overpass_miner_assistant(_my_address:str, _my_private_key:str):
    op_LCS_miner =LCSOverPassMiner(HTTP_PROVIDER,_my_address,_my_private_key)
    while 1:
        print("Available orders:\n 1. listen <contract_address>\n 2. unlisten <contract_address>\n 3. min_incentive <min_incentive>\n 4. maximum_duration <maximum_duration>\n 5. get_incentive\n\n")
        order=input("Order:")
        orders=list(order.strip().split(' '))
            
        if orders[0] == 'listen':
            try:
                op_LCS_miner.listen(orders[1])
            except:
                print(traceback.format_exc())
        elif orders[0] == 'unlisten':
            try:
                op_LCS_miner.unlisten(orders[1])
            except:
                print(traceback.format_exc())
        elif orders[0] == 'min_incentive':
            op_LCS_miner.minIncentive = int(orders[1])
        elif orders[0] == 'min_incentive':
            op_LCS_miner.maximumDuration = int(orders[1])
        elif orders[0] == 'get_incentive':
            cnt = op_LCS_miner.get_incentive()
        else:
            print("illegal order")

