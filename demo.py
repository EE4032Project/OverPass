import asyncio
import json
import random
from solcx import compile_standard, install_solc
import traceback
import fcntl
import web3
from web3 import Web3, middleware
from web3.gas_strategies.time_based import medium_gas_price_strategy
from constant import MIDIUM_GAS_PRICE_ESTIMATOR_ON, HTTP_PROVIDER, STD_LOGGING_ON,FILE_LOGGING_ON
import sys
import time
import logging
import queue
from utils import thread_with_trace, lock
import os
import testcase

class OverPassException(Exception):
    def __init__(self, _type="py",_message="OverPassError"):
        self.message = _message
        self.type = _type
        super().__init__(self.message)

    def __str__(self):
        return f'OverPassError: {self.type} -> {self.message}'


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
        with open("./overpass/lcs_overpass_compiled_code.json", "w") as file:
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
            lk = lock.acquire('txn.lock')
            if lk is None:
                raise OverPassException("py", traceback.format_exc())
            transaction = overpassContract.constructor().buildTransaction({"chainId": self.chain_id, "gasPrice": self.w3.eth.gas_price, "from": self.my_address, "nonce": self.nonce})
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
            finally:
                lock.release(lk)
        else:
            raise OverPassException("py", "Contract deployed already")

    # delegate a contract
    def delegate_compute(self, str1:str, str2: str, _incentive: int):
        lk = lock.acquire('txn.lock')
        if lk is None:
            raise OverPassException("py", traceback.format_exc())
        transaction = self.overpass_instance.functions.delegate_compute(['LCS',str1,str2], 2).buildTransaction(
            {"chainId": self.chain_id, "from": self.my_address, "gasPrice": self.w3.eth.gas_price, "nonce":  self.nonce, "gas": 3*10**6, "value":_incentive})
        signed_txn = self.w3.eth.account.sign_transaction(transaction, private_key=self.private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        try:
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            return tx_receipt
        except:
            raise OverPassException("solidity", traceback.format_exc())
        finally:
            lock.release(lk)



    def getTaskApproxGasFee(self,taskId:int):
        return self.overpass_instance.functions.getTaskApproxGasFee(taskId).call()

    def checkAns(self,taskId:int):
        return self.overpass_instance.functions.checkAns(taskId).call()


# An LCSWrapper for user to easily deploy and calculate LCS
class LCS:
    contract_address = ""
    nonce = 0

    def __init__(self,_http_provider:str, _my_address:str, _private_key:str, _contract_address=""):

        self.private_key = _private_key
        self.my_address = _my_address
        self.contract_address = _contract_address
        self.overpass_instance = None
        self.http_provider = _http_provider



        # Compile the solidity

        compiled_sol = self.compileLCS()



        # get bytecode version
        self.bytecode = compiled_sol["contracts"]["./LCS.sol"]["LCS"]["evm"]["bytecode"]["object"]

        # get abi
        self.abi = compiled_sol["contracts"]["./LCS.sol"]["LCS"]["abi"]

        # connect to ganache

        self.w3 = Web3(Web3.HTTPProvider(self.http_provider))

        self.chain_id = self.w3.eth.chain_id
        # open to use medium gas price estimation
        if MIDIUM_GAS_PRICE_ESTIMATOR_ON==True:
            self.w3.eth.set_gas_price_strategy(medium_gas_price_strategy)
        self.w3.middleware_onion.add(middleware.time_based_cache_middleware)
        self.w3.middleware_onion.add(middleware.latest_block_based_cache_middleware)
        self.w3.middleware_onion.add(middleware.simple_cache_middleware)

    @staticmethod
    # Compile LCSOverPass code
    def compileLCS():
        with open("./overpass/contracts/LCS.sol", "r") as file:
            LCS = file.read()
        with open("./overpass/contracts/overpass.sol", "r") as file:
            overpass = file.read()
        install_solc("0.8.7")
        compiled_sol = compile_standard({
                "language": "Solidity",
                # sources should be added here if other .sol is imported
                "sources": {"./LCS.sol": {"content": LCS}},
                "settings": {
                    "outputSelection": {
                        "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
                    }
                },
            },
            solc_version="0.8.7",
        )
        with open("./overpass/lcs_compiled_code.json", "w") as file:
            json.dump(compiled_sol, file)
        return compiled_sol


    def updateNonce(self):
        block = self.w3.eth.get_block('latest')
        if self.blocknumber == block['number']:
            self.nonce += 1
        else:
            self.nonce = self.w3.eth.getTransactionCount(self.my_address)
    
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
            lk = lock.acquire('txn.lock')
            if lk is None:
                raise OverPassException("py", traceback.format_exc())
            self.updateNonce()
            transaction = overpassContract.constructor().buildTransaction({"chainId": self.chain_id, "gasPrice": self.w3.eth.gas_price, "from": self.my_address, "nonce": self.nonce})
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
            finally:
                lock.release(lk)
        else:
            raise OverPassException("py", "Contract deployed already")

    # Compute LCS contract
    def compute_lcs(self, str1:str, str2: str):
        lk = lock.acquire('txn.lock')
        if lk is None:
            raise OverPassException("py", traceback.format_exc())
        self.updateNonce()
        transaction = self.overpass_instance.functions.lcs(str1,str2).buildTransaction(
            {"chainId": self.chain_id, "from": self.my_address, "gasPrice": self.w3.eth.gas_price, "nonce":  self.nonce, "gas": 3*10**6})
        signed_txn = self.w3.eth.account.sign_transaction(transaction, private_key=self.private_key)
        try:
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            return tx_receipt
        except:
            print(traceback.format_exc())
            raise OverPassException("solidity", traceback.format_exc())
        finally:
            lock.release(lk)


    # As there is no function of getTaskApproxFee and checkAns function in LCS.sol, this doesn't need to be included
    # def getTaskApproxGasFee(self,taskId:int):
    #     return self.overpass_instance.functions.getTaskApproxGasFee(taskId).call()

    # def checkAns(self,taskId:int):
    #     return self.overpass_instance.functions.checkAns(taskId).call()



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
        self.nonce = 0
        self.blocknumber =0

        

    def addContract(self,addr: str):
        self.listeningAddresses[addr] = None

    
    def updateNonce(self):

        block = w3.eth.get_block('latest')
        if self.blocknumber == block['number']:
            self.nonce += 1
        else:
            self.nonce = self.w3.eth.getTransactionCount(self.my_address)




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
                lk = lock.acquire('txn.lock')
                op_instance = self.w3.eth.contract(address=contract_address , abi=self.abi)
                self.updateNonce()
                # advise
                # try get lock

                if lk is None:
                    logging.info("failed to get lock to advise task "+str(eventInfo['args']['taskId'])+traceback.format_exc())
                    return


                transaction = op_instance.functions.advise(eventInfo['args']['taskId'], llcs, [lcs]).buildTransaction({"chainId": self.chain_id, "from": self.my_address, "gasPrice": self.w3.eth.gas_price, "nonce":  self.nonce, "gas": 3*10**6})
                signed_txn = self.w3.eth.account.sign_transaction(transaction, private_key=self.private_key)
                tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
                tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
                logging.info("succeed to advise task "+str(eventInfo['args']['taskId'])+" \n"+str(tx_receipt))
                # getIncentive
                self.q.put([contract_address,str(eventInfo['args']['taskId'])])
                lock.release(lk)

            except:
                logging.info("failed to advise task "+str(eventInfo['args']['taskId'])+traceback.format_exc())
                lock.release(lk)

        else:
            logging.info("Not interested task, taskId:"+str(eventInfo['args']['taskId'])+traceback.format_exc())

        # and whatever


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
        while not self.q.empty():
            task = q.get(block=False)
            
            try:
                lk = lock.acquire('txn.lock')
                self.updateNonce()
                contract_address = task[0]
                taskId = int(task[1])
                op_instance = self.w3.eth.contract(address=contract_address , abi=self.abi)
                transaction = op_instance.functions.getIncentive(taskId).buildTransaction({"chainId": self.chain_id, "from": self.my_address, "gasPrice": self.w3.eth.gas_price, "nonce":  self.nonce, "gas": 3*10**6})
                signed_txn = self.w3.eth.account.sign_transaction(transaction, private_key=self.private_key)
                tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
                tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
                logging.info("succeed to get incentive of  task "+contract_address+":"+str(taskId)+" \n"+str(tx_receipt))
                lock.release(lk)
            except:
                q.put(task)
                logging.info("failed to get incentive of  task "+contract_address+":"+str(taskId)+" \n"+str(tx_receipt))
                lock.release(lk)
            
            cnt += 1
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
        elif orders[0] == 'max_duration':
            op_LCS_miner.maximumDuration = int(orders[1])
        elif orders[0] == 'get_incentive':
            cnt = op_LCS_miner.get_incentive()
            print(f"obtained incentive from {cnt} tasks")
        else:
            print("illegal ordering")









if __name__=="__main__":

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    stdout_handler.setFormatter(formatter)

    file_handler = logging.FileHandler('logs.log')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    if STD_LOGGING_ON:
        logger.addHandler(stdout_handler)
    if FILE_LOGGING_ON:
        logger.addHandler(file_handler)


    with open("./testnet/keys.json", "r") as file:
        keys_dict = json.load(file)

    addresses = list(keys_dict["private_keys"].keys())


    if len(sys.argv)>1 and sys.argv[1].strip()== "LCSOverPass":
        my_address = addresses[0]
        my_private_key = keys_dict["private_keys"][my_address]
        my_address = Web3.toChecksumAddress(my_address)

        op_LCS = LCSOverPass(HTTP_PROVIDER,my_address,my_private_key)

        try:
            receipt = op_LCS.deploy()
            print("LCSOverPass is deployed successfully!\ncontract address: {contract_address}".format(contract_address=receipt['contractAddress']))
        except:
            print(traceback.format_exc())
        times_to_delegate = input("times_to_delegate:")
        gas_sum = 0
        for i in range(int(times_to_delegate)):

            test_case = testcase.get_testcase(i)
            response = op_LCS.delegate_compute(test_case[0],test_case[10], 10**18)
            print("Gas used: ",vars(response)['gasUsed'])
            gas_sum += vars(response)['gasUsed']
            #time.sleep(20)
        print(f"Average Overpass Gas Fee for {times_to_delegate} testcases is: {gas_sum/times_to_delegate}")
        print("Approximate Gas Fee for Task: ",op_LCS.getTaskApproxGasFee(1))

    elif len(sys.argv)>1 and sys.argv[1].strip()== "miner":
        my_address = addresses[1]
        my_private_key = keys_dict["private_keys"][my_address]
        my_address = Web3.toChecksumAddress(my_address)
        
        overpass_miner_assistant(my_address, my_private_key)

    elif len(sys.argv)>1 and sys.argv[1].strip()== "LCS":
        my_address = addresses[2]
        my_private_key = keys_dict["private_keys"][my_address]
        my_address = Web3.toChecksumAddress(my_address)

        op_LCS = LCS(HTTP_PROVIDER,my_address,my_private_key)

        try:
            receipt = op_LCS.deploy()
            print("LCS is deployed successfully!\ncontract address: {contract_address}".format(contract_address=receipt['contractAddress']))
        except:
            print(traceback.format_exc())
        times_to_compute = input("times_to_compute:")
        gas_sum = 0
        for i in range(int(times_to_compute)):
            test_case = testcase.get_testcase(i)

            response = op_LCS.compute_lcs(test_case[0],test_case[1])
            print("Gas used: ",vars(response)['gasUsed'])
            gas_sum += vars(response)['gasUsed']
            # print(response)
            #time.sleep(20)
        print(f"Average LCS (non-overpass) Gas Fee for {times_to_compute} testcases is: {gas_sum/times_to_compute}")

        print("Cumulative Gas Used: ", int(vars(response)['gasUsed']) * int(times_to_compute))
        # There is no getTaskApproxGasFee function in LCS.sol
        # print("Approximate Gas Fee for Task: ",op_LCS.getTaskApproxGasFee(1))

    else:
        print("Legal Role:\n  1. 'LCSOverPass'\n  2. 'miner'\n  3. 'LCS'\n")
        print(len(sys.argv), " ",sys.argv[1] )


#print(file)
