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

interface StrategyCurveEursCrvVoterProxy {
    function deposit() external;
}

contract GaugeWhitehat {
    using SafeERC20 for IERC20;
    using Address for address;
    using SafeMath for uint256;

    address public constant uni = address(
        0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D
    );
    address public constant weth = address(
        0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2
    ); // used for crv <> weth <> usdc <> eurs route

    address public constant eurs = address(
        0xdB25f211AB05b1c97D595516F45794528a807ad8
    );
    address public constant usdc = address(
        0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48
    );
    address public constant curve = address(
        0x0Ce6a5fF5217e38315f87032CF90686C96627CAA
    );

    address public constant want = address(
        0x194eBd173F6cDacE046C53eACcE9B953F28411d1
    );

    address public constant snx = address(
        0xC011a73ee8576Fb46F5E1c5751cA3B9Fe0af2a6F
    );

    address public constant strategy = address(
        0xc8a753B38978aDD5bD26A5D1290Abc6f9f2c4f99
    );

    event SnxRecovered(uint256 amount);

    event wantRecovered(uint256 amount);

    function deposit(uint256 amount) external {
        // Swap SNX for EURS
        IERC20(snx).transferFrom(msg.sender, address(this), amount);
        uint256 _snx = IERC20(snx).balanceOf(address(this));
        emit SnxRecovered(_snx);
        if (_snx > 0) {
            IERC20(snx).safeApprove(uni, 0);
            IERC20(snx).safeApprove(uni, _snx);

            address[] memory path = new address[](4);
            path[0] = snx;
            path[1] = weth;
            path[2] = usdc;
            path[3] = eurs;

            Uni(uni).swapExactTokensForTokens(
                _snx,
                uint256(0),
                path,
                address(this),
                now.add(1800)
            );
        }

        uint256 _eurs = IERC20(eurs).balanceOf(address(this));
        if (_eurs > 0) {
            IERC20(eurs).safeApprove(curve, 0);
            IERC20(eurs).safeApprove(curve, _eurs);
            ICurveFi(curve).add_liquidity([_eurs, 0], 0);
        }
        uint256 _want = IERC20(want).balanceOf(address(this));
        IERC20(want).safeTransfer(strategy, _want);
        if (_want > 0) {
            emit wantRecovered(_want);
            StrategyCurveEursCrvVoterProxy(strategy).deposit();
        }
    }
}
