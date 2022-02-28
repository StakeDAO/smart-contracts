pragma solidity ^0.5.17;

import "@openzeppelinV2/contracts/token/ERC20/IERC20.sol";
import "@openzeppelinV2/contracts/math/SafeMath.sol";
import "@openzeppelinV2/contracts/utils/Address.sol";
import "@openzeppelinV2/contracts/token/ERC20/SafeERC20.sol";

import "../../../interfaces/yearn/IController.sol";
import "../../../interfaces/curve/Gauge.sol";
import "../../../interfaces/curve/Mintr.sol";
import "../../../interfaces/uniswap/Uni.sol";
import "../../../interfaces/curve/Curve.sol";
import "../../../interfaces/yearn/IToken.sol";
import "../../../interfaces/yearn/IVoterProxy.sol";

interface StrategyProxy {
    function deposit(address _gauge, address _token) external;
}

contract StrategySNXWhitehat {
    using SafeERC20 for IERC20;
    using Address for address;
    using SafeMath for uint256;

    address public constant snx = address(
        0xC011a73ee8576Fb46F5E1c5751cA3B9Fe0af2a6F
    );

    address public proxy;
    address public gauge;
    address public owner;

    constructor(address _proxy, address _gauge) public {
        proxy = _proxy;
        gauge = _gauge;
        owner = msg.sender;
    }

    function deposit() external {
        require(msg.sender == owner);
        StrategyProxy(proxy).deposit(gauge, snx);
    }
}
