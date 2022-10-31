# EE4032 (Project title)

## Table of Contents

1. [Introduction](#section-1-introduction)
2. [Prerequisites](#section-2-prerequisites)
3. [How to interact](#section-3-how-to-interact)

## Section 1: Introduction <a name="section-1-introduction"></a>

Smart contracts provide trust computing. Once a smart contract has been engaged, it will complete exactly how it was coded and no parties can interfere or change the result. However, the computation is usually expensive and slow. There exists a set of problem where there is sign showing that verification on answer is cheaper than searching the answer. Hence well-defined incentive mechanism can be applied to delegate searching computation to untrusted computational power (off-chain server) while the completeness and soundness of the computation is still guaranteed:

- A delegation task is posted on smart contract together with a trusted verification function
- Some untrusted machine would listening to the task event, and provide answers/adivices that could help smart contract solving the problem.
- Smart contract verifies the answer:
  - pass verification: provide the outputs to customers & give incentives to local computers
  - otherwise: reject

Our project can optimize smart contracts based on the functions below.

|     Function      | Cons  |
| :---------------: | :---: |
| local conputation | fast  |
|   verification    | cheap |

## Section 2: Prerequisites <a name="#section-2-prerequisites"></a>

1. Homebrew (Mac Users only)
2. Python 3 environment
3. Node 16
4. Ganache CLI

### Section 3: How to interact <a name="#section-3-how-to-interact"></a>

1. Clone the github repository and enter into the directory.

```sh
git clone https://github.com/EE4032Project/OverPass.git && cd OverPass
```

2. Even though it is optional, we recommend activating a virtual environment to
   localise all the installation of the python libraries into the folder. Refer to the
   remarks for instructions on how to activate a virtual environment.

3. Install the required python libraries

```sh

pip3 install -r requirements.txt

```

4. Open up 4 terminals.

#### Terminal 1:

```sh

cd testnet # Enter the testnet directory


```

use terminal 1 and enter `$OVER_PASS/testnet`

```sh

sh start_gananche_testnet.sh 100
```

where 100 means generate 100 accounts 5. use terminal 2 to deploy LCSOverPass on Truffle network

```sh
python3 demo.py LCSOverPass
```

You can enter number of questions to model 6. use terminal 3 to play the role in miner and listen to the contract deployed by terminal 2

```sh
python3 python3 deploy.py LCSOverPassMiner
```

7. use terminal 4 to track the log

```sh
tail -f logs.log
```

## Section 4: Remarks

### Section 4.1. Installing Python3 Environment

If you do not have a Python3 environment, we recommend installing anaconda using the following command.

```sh
brew install --cask anaconda # Mac Environment: Installed using homebrew
```

### Section 4.2. Installing Node16

```sh
brew install node # Mac Environment: Installed using homebrew
```

### Section 4.3. Installing Virtual Environment

```sh

python3 -m venv venv # Create a virtual environment in the directory called venv
. venv/bin/activate # Activate the virtual environment. You should see a (venv) in terminal

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
