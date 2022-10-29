# EE4032 (Project title)

## Introduction

Smart contracts provide trust computing. Once a smart contract has been engaged, it will complete exactly how it was coded and no parties can interfere or change the result. However, the computation is usually expensive and slow. There exists a set of problem where there is sign showing that verification on answer is cheaper than searching the answer. Hence well-defined incentive mechanism can be applied to delegate searching computation to untrusted computational power (off-chain server) while the completeness and soundness of the computation is still guaranteed:

- A delegation task is posted on smart contract together with a trusted verification function
- Some untrusted machine would listening to the task event, and provide answers/adivices that could help smart contract solving the problem.
- Smart contract verifies the answer:
  - pass verification: provide the outputs to customers & give incentives to local computers
  - otherwise: reject

Our project can optimize smart contracts based on the functions below.
| function | cons |
| ------ | ------ |
| local conputation | fast |
| verification | cheap |

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

3. Clone github repo

```sh
git clone https://github.com/EE4032Project/OverPass.git && cd OverPass
```

3. Install python libraries

```sh
pip3 install -r requirements.txt
```

4. use terminal 1 and enter `$OVER_PASS/testnet`

```sh

sh start_gananche_testnet.sh 100
```

where 100 means generate 100 accounts 5. use terminal 2 to deploy LCSOverPass on Truffle network

```sh
python3 demo.py LCSOverPass
```

You can enter number of questions to model
6. use terminal 3 to play the role in miner and listen to the contract deployed by terminal 2
```sh
python3 python3 deploy.py LCSOverPassMiner 
```

7. use terminal 4 to track the log

```sh
tail -f logs.log
```

## Remarks

Suppose you are only using the python files solely for this project, we recommend that you
create a virtual environment using the following command. You would need to activate the
virtual environment everytime you would like to run the files.

```sh

python3 -m venv venv
. venv/bin/activate


```

If you encounter an issue where the `ganache-cli` is not found, execute the following command on
your terminal.

```sh

sudo yarn global add ganache # If you are using yarn
sudo npm install -g ganache # If you are installing npm

```

## Acknowledgement

For production environments...

```sh

```
