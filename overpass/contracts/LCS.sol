// contracts/OverPass.sol
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.7;

contract LCS {

    function lcs(string memory _XS, string memory _YS) public pure returns (uint256){
        bytes memory _X= bytes(_XS);
        bytes memory _Y= bytes(_YS);


        uint256 r = bytes(_X).length+1;
        uint256 c = bytes(_Y).length+1;
    
        uint[] memory dp = new uint[](r*c);
         for (uint i = 1; i < r; i++){
            for (uint j = 1; j < c; j++){
                if (_X[i-1]==_Y[j-1]){
                    // array[i][j] = array[i-1][j-1] + 1;
                    dp[i*c+j] = dp[(i-1)*c+j-1] + 1;
                }
                else {
                    dp[i*c+j] = dp[(i-1)*c+j]>dp[i*c+j-1]? dp[(i-1)*c+j]:dp[i*c+j-1];
                }
            }
        }
        return dp[(r-1)*c+c-1];
    }
}

