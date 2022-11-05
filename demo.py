'''
MIT License

Copyright (c) 2022 EE4032 Group 8

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
from overpass.py.LCS import LCS
from overpass.py.LCSOverPass import LCSOverPass
from overpass.py.LCSOverPassMiner import LCSOverPassMiner,overpass_miner_assistant








if __name__=="__main__":

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    stdout_handler.setFormatter(formatter)
    path = "log"
    # Check whether the specified path exists or not
    isExist = os.path.exists(path)
    if not isExist:
        # Create a new directory because it does not exist
        os.makedirs(path)
        print(f"The new directory {path} is created!")

    file_handler = logging.FileHandler('log/output.log')
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
        times_to_delegate = int(input("times_to_delegate:"))
        gas_sum = 0
        # TODO: the task ID should be fetched from receipt
        for i in range(int(times_to_delegate)):

            test = get_testcase(i)
            print("test case:", i+1)
            print("s1 len:", len(test[0]))
            print("s2 len:", len(test[1]))
            response = op_LCS.delegate_compute(test[0],test[1],10**17)
            print("Gas used: ",vars(response)['gasUsed'])
            gas_sum += int(vars(response)['gasUsed'])

        print(f"LCSOverPass: Average Gas Used for {times_to_delegate} testcases is: {gas_sum/times_to_delegate}")
        print(f"Approximate Weis for one test one testcast is: {gas_sum*op_LCS.feePerGas/times_to_delegate}")
        

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
        times_to_compute = int(input("times_to_compute:"))

        gas_sum = 0
        for i in range(int(times_to_compute)):
            test = get_testcase(i)
            print("test case:", i+1)
            print("s1 len:", len(test[0]))
            print("s2 len:", len(test[1]))
            response = op_LCS.compute_lcs(test[0],test[1])
            print("Gas used: ",vars(response)['gasUsed'])
            gas_sum += int(vars(response)['gasUsed'])

        print(f"LCS: Average Gas Used for {times_to_compute} testcases is: {gas_sum/times_to_compute}")
        print(f"Approximate Weis for one test one testcast is: {gas_sum*op_LCS.feePerGas/times_to_compute}")

        # There is no getTaskApproxGasFee function in LCS.sol

    else:
        print("Legal Role:\n  1. 'LCSOverPass'\n  2. 'miner'\n  3. 'LCS'\n")
        print(len(sys.argv), " ",sys.argv[1] )

