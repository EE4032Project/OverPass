// contracts/OverPass.sol
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.7;
import "./overpass.sol";


contract LCSOverPass is OverPass{

    constructor(uint256 initialSupply) ERC20("LCSOverPass", "LCSOverPass"){
        _mint(msg.sender, initialSupply);
    }

    mapping (uint256=>uint) results;

    // simulate the verification to estimate the gas fee
    function _simulateVerification(bytes memory s1,  bytes memory s2) private pure returns (bool){
        uint checkI = 0;
        if (s1.length != s1.length) {
            return false;
        }
        if (s2.length != s2.length) {
            return false;
        }
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

    // keccak256(abi.encodePacked("LCS"))
    bytes32 private constant _LCS = 0x816a2b01920faffdf630c9d96404a778baf08493254365c589e0d4366da539ed;
    uint MAX_STR_LEN = 1001;
    // called by other smart contract to compute specified algorithm with parameters
    function delegate_compute(string[] memory taskParameters) payable public override returns (uint256) {
        require(taskParameters.length==3 && keccak256(abi.encodePacked((taskParameters[0])))==_LCS, "Wrong delegated task.");
        bytes memory s1  = bytes(taskParameters[1]);
        bytes memory s2 = bytes(taskParameters[2]);
        require(s1.length<MAX_STR_LEN && s2.length<MAX_STR_LEN, "String too long.");
        _simulateVerification(s1, s2);
        require(msg.value>tx.gasprice*10, "not enough payment.");
        // set new task
        tasks[nonce] = Task(msg.sender, nonce, taskParameters, address(0), 0, msg.value, tx.gasprice, false, false);
        nonce += 1;
        return nonce-1;
    }
    // return parameters of a function
    function getTaskParameters(uint256 taskId) public view override returns (string[] memory){
        return tasks[taskId].taskParameters;
    }
    // get the result of Task
    function completeTask(uint256  taskId) public override {


    }

    function advise(uint256 taskId,string[] calldata functionParameters) payable public override {

    }
}

