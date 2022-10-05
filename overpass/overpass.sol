// contracts/OverPass.sol
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.7;
import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/token/ERC20/ERC20.sol";

abstract contract OverPass is ERC20 {

    struct Task {
        address taskOwner;
        uint256 taskId;
        string [] taskParameters;
        address bestAdvisor;
    }
    // Store the information of tasks
    mapping(uint256=>Task) private tasks;

    constructor(uint256 initialSupply) ERC20("OverPass", "OP") {
        _mint(msg.sender, initialSupply);
    }

    // called by other smart contract to compute specified algorithm with parameters
    function delegate_compute(string[] calldata taskParameters) payable public virtual;
    // return parameters of a function
    function getTaskParameters(string calldata taskId)public view virtual;
    // get the result of Task
    function completeTask(string calldata functionId) public virtual;
    function advise(string calldata functionId,string[] calldata functionParameters) payable public virtual;
}

