# EE4032 (Project title)

-

## Introduction 

Smart contracts provide trust computing. Once a smart contract has been engaged, it will complete exactly how it was coded and no parties can interfere or change the result. However, the computation is usually expensive and slow. There exists a set of problem where there is sign showing that verification on answer is cheaper than searching the answer.  Hence well-defined incentive mechanism can be applied to delegate searching computation to untrusted computational power (off-chain server) while the completeness and soundness of the computation is still guaranteed: 

- A delegation task is posted on smart contract together with a trusted verification function
- Some untrusted machine would listening to the task event, and provide answers/adivices that could help smart contract solving the problem.
- Smart contract verifies the answer:
    - pass verification: provide the outputs to customers & give incentives to local computers
    - otherwise: reject

Our project can optimize smart contracts based on the functions below.
| function | cons |
| ------ | ------ |
| local conputation | fast  |
| verification  | cheap |





## How to start 
### On Mac Environment
1. Ensures python 3 environment, here we suggest download Anaconda
```sh
brew install --cask anaconda
```
2. Install npm
```sh
brew install node
```
3. Clone githup repo
```sh
git clone https://github.com/EE4032Project/OverPass.git && cd OverPass
```
3. Install python libraries
```sh
pip3 intsall -r requirements.txt
```
4. open another shell and enter `$OVER_PASS/testnet`
```sh
sh start_gananche_testnet.sh 100
```
where 100 means generate 100 accounts
5. run deploy script
```sh
python3 deploy.py
```

## Acknowledgement 



For production environments...

```sh

```



