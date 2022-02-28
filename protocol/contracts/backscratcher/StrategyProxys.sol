// SPDX-License-Identifier: MIT

pragma solidity ^0.5.17;

contract StrategyProxys {
    address public sdveCRV;

    constructor() public {}

    function claim(address _user) external returns (uint256) {
        return 3;
    }

    function setSdveCRV(address _sdveCRV) external {
        sdveCRV = _sdveCRV;
    }
}
