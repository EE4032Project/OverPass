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
        uint bestAnswer;
        uint incentive;
        uint approxGasFee;
        uint startBlock;
        uint computePeriod;
    }

    event postNewQuestion(uint256 taskId, uint incentive, uint approxGasFee, uint computePeriod);
    event updateQuestionAnswer(uint256 taskId, uint bestAnswer, address bestAdvisor);

    // Store the information of tasks
    mapping(uint256=>Task) internal tasks;

    uint internal nonce;

    constructor(uint256 initialSupply) ERC20("OverPass", "OP") {
        _mint(msg.sender, initialSupply);
    }

    modifier winnerOnly(uint256 _taskId) {
        require(
            block.number>tasks[_taskId].startBlock+tasks[_taskId].computePeriod&&msg.sender == tasks[_taskId].bestAdvisor ,
            "winner only function"
        );
        _;
    }

    

    // called by other smart contract to compute specified algorithm with parameters
    function delegate_compute(string[] memory taskParameters, uint _computePeriod) payable public virtual returns (uint256);
    // return parameters of a function
    function getTaskParameters(uint256 taskId) public view virtual returns(string[] memory);
    function advise(uint256 taskId, uint256 ans, string[] memory proof) payable public virtual;
    function getIncentive(uint256 _taskId) public virtual;
}

