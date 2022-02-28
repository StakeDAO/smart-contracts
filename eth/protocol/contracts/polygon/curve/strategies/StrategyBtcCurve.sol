// SPDX-License-Identifier: MIT

pragma solidity ^0.5.17;
pragma experimental ABIEncoderV2;

import "@openzeppelinV2/contracts/token/ERC20/IERC20.sol";
import "@openzeppelinV2/contracts/math/SafeMath.sol";
import "@openzeppelinV2/contracts/utils/Address.sol";
import "@openzeppelinV2/contracts/token/ERC20/SafeERC20.sol";

interface IController {
    function withdraw(address, uint256) external;

    function balanceOf(address) external view returns (uint256);

    function earn(address, uint256) external;

    function want(address) external view returns (address);

    function rewards() external view returns (address);

    function vaults(address) external view returns (address);

    function strategies(address) external view returns (address);
}

interface ICurveFi {
    function add_liquidity(
        uint256[2] calldata amounts,
        uint256 min_mint_amount,
        bool use_underlying
    ) external returns (uint256);
}

interface Gauge {
    function deposit(uint256) external;

    function balanceOf(address) external view returns (uint256);

    function withdraw(uint256) external;

    function claim_rewards() external;
}

contract StrategyBtcCurve {
    using SafeERC20 for IERC20;
    using Address for address;
    using SafeMath for uint256;

    address public constant want =
        address(0xf8a57c1d3b9629b77b6726a042ca48990A84Fb49);

    address public constant paraswap =
        address(0x90249ed4d69D70E709fFCd8beE2c5A566f65dADE);

    address public constant wmatic =
        address(0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270);

    address public constant crv =
        address(0x172370d5Cd63279eFa6d502DAB29171933a610AF);

    address public constant wbtc =
        address(0x1BFD67037B42Cf73acF2047067bd4F2C47D9BfD6);

    address public constant pool =
        address(0xC2d95EEF97Ec6C17551d45e77B590dc1F9117C67);

    address public constant gauge =
        address(0xffbACcE0CC7C19d46132f1258FC16CF6871D153c);

    address public paraswapProxy =
        address(0xCD52384e2A96F6E91e4e420de2F9a8C0f1FFB449);

    uint256 public performanceFee = 1500;
    uint256 public constant performanceMax = 10000;

    uint256 public withdrawalFee = 50;
    uint256 public constant withdrawalMax = 10000;

    address public governance;
    address public controller;
    address public strategist;

    uint256 public earned; // lifetime strategy earnings denominated in `want` token

    event Harvested(uint256 wantEarned, uint256 lifetimeEarned);

    modifier onlyGovernance() {
        require(msg.sender == governance, "!governance");
        _;
    }

    modifier onlyController() {
        require(msg.sender == controller, "!controller");
        _;
    }

    constructor(address _controller) public {
        governance = msg.sender;
        strategist = msg.sender;
        controller = _controller;
    }

    function getName() external pure returns (string memory) {
        return "StrategyBtcCurve";
    }

    function setStrategist(address _strategist) external onlyGovernance {
        strategist = _strategist;
    }

    function setWithdrawalFee(uint256 _withdrawalFee) external onlyGovernance {
        withdrawalFee = _withdrawalFee;
    }

    function setPerformanceFee(uint256 _performanceFee)
        external
        onlyGovernance
    {
        performanceFee = _performanceFee;
    }

    function setParaswapProxy(address _paraswapProxy) external onlyGovernance {
        paraswapProxy = _paraswapProxy;
    }

    function deposit() public {
        uint256 _want = IERC20(want).balanceOf(address(this));
        if (_want > 0) {
            IERC20(want).approve(gauge, _want);
            Gauge(gauge).deposit(_want);
        }
    }

    // Controller only function for creating additional rewards from dust
    function withdraw(IERC20 _asset)
        external
        onlyController
        returns (uint256 balance)
    {
        require(want != address(_asset), "want");
        require(wbtc != address(_asset), "wbtc");
        require(wmatic != address(_asset), "wmatic");
        balance = _asset.balanceOf(address(this));
        _asset.safeTransfer(controller, balance);
    }

    // Withdraw partial funds, normally used with a vault withdrawal
    function withdraw(uint256 _amount) external onlyController {
        uint256 _balance = IERC20(want).balanceOf(address(this));
        if (_balance < _amount) {
            _withdrawSome(_amount.sub(_balance));
        }

        uint256 _fee = _amount.mul(withdrawalFee).div(withdrawalMax);

        IERC20(want).safeTransfer(IController(controller).rewards(), _fee);
        address _vault = IController(controller).vaults(address(want));
        require(_vault != address(0), "!vault"); // additional protection so we don't burn the funds

        IERC20(want).safeTransfer(_vault, _amount.sub(_fee));
    }

    function _withdrawSome(uint256 _amount) internal {
        Gauge(gauge).withdraw(_amount);
    }

    // Withdraw all funds, normally used when migrating strategies
    function withdrawAll() external onlyController returns (uint256 balance) {
        _withdrawAll();

        balance = balanceOfWant();

        address _vault = IController(controller).vaults(address(want));
        require(_vault != address(0), "!vault"); // additional protection so we don't burn the funds
        IERC20(want).safeTransfer(_vault, balance);
    }

    function _withdrawAll() internal {
        uint256 _before = balanceOf();
        _withdrawSome(balanceOfPool());
        require(_before == balanceOf(), "!slippage");
    }

    function harvest(bytes memory swapDataWmatic, bytes memory swapDataCrv)
        public
    {
        require(
            msg.sender == strategist || msg.sender == governance,
            "!authorized"
        );

        Gauge(gauge).claim_rewards();

        uint256 _crv = IERC20(crv).balanceOf(address(this));
        if (_crv > 0) {
            IERC20(crv).approve(paraswapProxy, _crv);
            (bool success, ) = paraswap.call(swapDataCrv);
            if (!success) {
                // Copy revert reason from call
                assembly {
                    returndatacopy(0, 0, returndatasize())
                    revert(0, returndatasize())
                }
            }
        }

        uint256 _wmatic = IERC20(wmatic).balanceOf(address(this));
        if (_wmatic > 0) {
            IERC20(wmatic).approve(paraswapProxy, _wmatic);
            (bool success, ) = paraswap.call(swapDataWmatic);
            if (!success) {
                // Copy revert reason from call
                assembly {
                    returndatacopy(0, 0, returndatasize())
                    revert(0, returndatasize())
                }
            }
        }
        uint256 _wbtc = IERC20(wbtc).balanceOf(address(this));
        if (_wbtc > 0) {
            IERC20(wbtc).approve(pool, _wbtc);
            ICurveFi(pool).add_liquidity([_wbtc, 0], 0, true);
        }
        uint256 _want = IERC20(want).balanceOf(address(this));
        if (_want > 0) {
            uint256 _fee = _want.mul(performanceFee).div(performanceMax);
            IERC20(want).safeTransfer(IController(controller).rewards(), _fee);
            deposit();
        }

        earned = earned.add(_want);
        emit Harvested(_want, earned);
    }

    function balanceOfWant() public view returns (uint256) {
        return IERC20(want).balanceOf(address(this));
    }

    function balanceOfPool() public view returns (uint256) {
        return Gauge(gauge).balanceOf(address(this));
    }

    function balanceOf() public view returns (uint256) {
        return balanceOfWant().add(balanceOfPool());
    }

    function setGovernance(address _governance) external onlyGovernance {
        governance = _governance;
    }

    function setController(address _controller) external onlyGovernance {
        controller = _controller;
    }
}
