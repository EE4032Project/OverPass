# EE4032 (Project title)

## Table of Contents

1. [Introduction](#section-1-introduction)
2. [Prerequisites](#section-2-prerequisites)
3. [How to interact](#section-3-how-to-interact)
4. [Remarks](#section-4-remarks)

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

## Section 3: How to interact <a name="#section-3-how-to-interact"></a>

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

5. On `Terminal 1`, start up the ganachetest net. You may specify the number of accounts that you
   would like to generate which, for our case, is 100.

```sh

$ cd testnet # Enter the testnet directory
$ sh start_gananche_testnet.sh 100 # Start up the ganache test net


```

Upon successful set up, you should see the following

<img width="752" alt="Screenshot 2022-10-31 at 12 44 18 PM" src="https://user-images.githubusercontent.com/88195289/198932873-3322aa4c-c60e-418b-92f0-5bd38d89884e.png">

6. On `Terminal 2`, to log down the information, execute the following command.

```sh

$ tail -f logs.log

```

7. On `Terminal 3`, deploy the LCSOverPass on Truffle network

```sh
$ python3 demo.py LCSOverPass

```

You should see the following after you have executed the command successfully.

```sh

contract address: 0xe78A0F7E598Cc8b0Bb87894B0F60dD2a88d6a8Ab
times_to_delegate:

```

8. On `Terminal 4`, we can play the role of a miner and listen to the
   contracct deployed on `Terminal 2` using the following command.

```sh

$ python3 demo.py LCSOverPassMiner

```

You should see the following:

```sh

Available orders:
1. listen <contract_address>
2. unlisten <contract_address>
3. min_incentive <min_incentive>
4. maximum_duration <maximum_duration>

```

We can set the configurations, such as listening to the
contract address using the following

```sh

Order: listen 0xe78A0F7E598Cc8b0Bb87894B0F60dD2a88d6a8Ab # The address is from Terminal 3

```

After this, we should see the following:

```sh

Start listening on address: 0xe78A0F7E598Cc8b0Bb87894B0F60dD2a88d6a8Ab

```

9. Specify the number of questions that you would like to model on `Terminal 3`,
   which for our case is 1.

```sh

contract address: 0xe78A0F7E598Cc8b0Bb87894B0F60dD2a88d6a8Ab
times_to_delegate: 1

```

After you press enter, you should see something like this on `Terminal 3`.

<img width="814" alt="Screenshot 2022-10-31 at 12 40 25 PM" src="https://user-images.githubusercontent.com/88195289/198932572-a0f523c3-e85b-4d21-bd4f-5bd911e2c806.png">

On `Terminal 1`, you should see the following.

<img width="623" alt="Screenshot 2022-10-31 at 12 43 32 PM" src="https://user-images.githubusercontent.com/88195289/198932724-cd448ee9-5b12-4bf4-a485-7bcdce10deb4.png">

## Section 4: Remarks<a name="section-4-remarks"></a>

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

sudo npm install -g ganache # If you are installing npm

```

## Acknowledgement

For production environments...

```sh

```
