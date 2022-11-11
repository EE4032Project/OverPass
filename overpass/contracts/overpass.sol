// contracts/OverPass.sol
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.7;

abstract contract OverPass {

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


    event postNewQuestion(uint256 taskId, uint incentive, uint approxGasFee, uint computePeriod, string[] taskParameters);
    event updateQuestionAnswer(uint256 taskId, uint bestAnswer, address bestAdvisor);
    event complateQuestion(uint256 taskId, uint bestAnswer, address bestAdvisor);


    // Store the information of tasks
    mapping(uint256=>Task) internal tasks;

    uint internal nonce=1;

    // First eight hex of keccak-256(problemName(<problem input data types>))
    bytes problemSig;

    constructor(bytes memory _problemSig) {
        require(_problemSig.length==8, "Illegal length of problemSig");
        problemSig = _problemSig;

    }

    modifier winnerOnly(uint256 _taskId) {
        require(
            block.number>tasks[_taskId].startBlock+tasks[_taskId].computePeriod&&msg.sender == tasks[_taskId].bestAdvisor ,
            "winner only function"
        );
        _;
    }

    

    // Called by user to delegate compute specific problem
    function delegate_compute(string[] memory taskParameters, uint _computePeriod) payable public virtual returns (uint256);

    // Called by miner to advise hint/answer/proof
    function advise(uint256 taskId, uint256 ans, string[] memory proof) payable public virtual;

    // Called by winner miner to get the incentive
    function getIncentive(uint256 _taskId) public virtual;
        function getTaskIncentive(uint256 taskId) public view returns(uint) {
        return tasks[taskId].incentive;
    }

    // Called by miner to get the estimated gas fee
    function getTaskApproxGasFee(uint256 taskId) public view returns(uint){
        return tasks[taskId].approxGasFee;
    }
    
    // Called by miner return parameters of a function
    function getTaskParameters(uint256 taskId) public view returns (string[] memory){
        return tasks[taskId].taskParameters;
    }
}

