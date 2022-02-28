// SPDX-License-Identifier: MIT

pragma solidity ^0.5.17;

import "@openzeppelinV2/contracts/token/ERC20/IERC20.sol";
import "@openzeppelinV2/contracts/math/SafeMath.sol";
import "@openzeppelinV2/contracts/utils/Address.sol";
import "@openzeppelinV2/contracts/token/ERC20/SafeERC20.sol";

interface IProxy {
    function withdraw(IERC20 _asset) external returns (uint256 balance);
}

interface StrategyProxy {
    function lock() external;
}

contract WhitehatStrategyProxy {
    using SafeERC20 for IERC20;
    using Address for address;
    using SafeMath for uint256;

    address public owner;

    //IProxy public constant proxy = IProxy(0xF147b8125d2ef93FB6965Db97D6746952a133934);
    IProxy public constant proxy = IProxy(
        0x96032427893A22dd2a8FDb0e5fE09abEfc9E4444
    );
    address public constant crv = address(
        0xD533a949740bb3306d119CC777fa900bA034cd52
    );

    constructor() public {
        owner = msg.sender;
    }

    function rescueCrv(address newProxy, address strategyProxy) external {
        require(msg.sender == owner, "!authorized");
        uint256 balance = proxy.withdraw(IERC20(crv));
        IERC20(crv).safeTransfer(newProxy, balance);
        StrategyProxy(strategyProxy).lock();
    }
}
