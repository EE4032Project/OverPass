// contracts/OverPass.sol
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.7;
import "./overpass.sol";


contract LCSOverPass is OverPass{

    constructor(uint256 initialSupply) OverPass((initialSupply)) {
    }


    // simulate the verification to estimate the gas fee
    function _simulateVerification(bytes memory s1,  bytes memory s2, bytes memory s3, uint k) private pure returns (bool){
        uint checkI = 0;
        // simulate length check
        if (s3.length != k) {
            return false;
        }
        // simulate check over s1
        for (uint i=0; i<s1.length; i++) {
            if (checkI==s1.length) {
                break;
            }
            if (s1[i]==s1[checkI]) {
                checkI +=1;
            } else {
                continue;
            }
        }
        if (checkI!=s1.length) {
            return false;
        }
        // simulate check over s2
        for (uint i=0; i<s2.length; i++) {
            if (checkI==s2.length) {
                break;
            }
            if (s2[i]==s1[checkI]) {
                checkI +=1;
            } else {
                continue;
            }
        }

        if (checkI!=s2.length) {
            return false;
        }
        return true;
    }

    function _verifyResult(bytes memory s1,  bytes memory s2, bytes memory lcs, uint k) private pure returns (bool){
        require(lcs.length==k, "proof and answers are unmatched.");
        uint checkI = 0;
        for (uint i=0; i<s1.length; i++) {
            if (s1[i]==lcs[checkI]) {
                checkI +=1;
                if (checkI==k) {
                    break;
                }
            }
        }
        if (checkI!=k) {
            return false;
        }
        checkI = 0;
        for (uint i=0; i<s2.length; i++) {
            if (s2[i]==lcs[checkI]) {
                checkI +=1;
                if (checkI==k) {
                    break;
                }
            }
        }
        if (checkI!=k) {
            return false;
        }
        return true;
    }

    // keccak256(abi.encodePacked("LCS"))
    bytes32 private constant _LCS = 0x816a2b01920faffdf630c9d96404a778baf08493254365c589e0d4366da539ed;
    uint MAX_STR_LEN = 1001;
    // called by other smart contract to compute specified algorithm with parameters
    function delegate_compute(string[] memory taskParameters, uint _computePeriod) payable public override returns (uint256) {
        require(taskParameters.length==3 && keccak256(abi.encodePacked((taskParameters[0])))==_LCS, "Wrong delegated task.");
        bytes memory s1  = bytes(taskParameters[1]);
        bytes memory s2 = bytes(taskParameters[2]);
        require(s1.length<MAX_STR_LEN && s2.length<MAX_STR_LEN, "String too long.");
        _simulateVerification(s1, s2, s1, s1.length);
        require(msg.value>tx.gasprice*10, "not enough payment.");
        // set new task

        tasks[nonce] = Task(msg.sender, nonce, taskParameters, address(0), 0,  msg.value, tx.gasprice, block.number, _computePeriod);
        
        emit postNewQuestion(/*taskId*/nonce, /*incentive*/msg.value, /*approxGasFee*/tx.gasprice, _computePeriod);
        nonce += 1;
        return nonce-1;
    }

    // return parameters of a function
    function getTaskParameters(uint256 taskId) public view override returns (string[] memory){
        return tasks[taskId].taskParameters;
    }

    function advise(uint256 taskId, uint256 ans, string[] memory proof) payable public override {
        
        require(ans>tasks[taskId].bestAnswer, "Better solution exists");
        require(proof.length==1, "Invalid proof");
        bytes memory s1 = bytes(tasks[taskId].taskParameters[1]);
        bytes memory s2 = bytes(tasks[taskId].taskParameters[2]);
        
        bool isValidAns = _verifyResult(s1, s2, bytes(proof[0]), ans);
        require(isValidAns, "Invalid proof");
        tasks[taskId].bestAdvisor = msg.sender;
        tasks[taskId].bestAnswer = ans;
        emit updateQuestionAnswer(taskId, ans, msg.sender);

    }

    function getIncentive(uint256 _taskId) public override winnerOnly(_taskId) {
        super.transfer(msg.sender, tasks[_taskId].incentive);
        delete tasks[_taskId];
    }


}

