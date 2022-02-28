pragma solidity ^0.5.17;
pragma experimental ABIEncoderV2;

import "@openzeppelinV2/contracts/token/ERC20/IERC20.sol";
import "@openzeppelinV2/contracts/math/SafeMath.sol";
import "@openzeppelinV2/contracts/utils/Address.sol";
import "@openzeppelinV2/contracts/token/ERC20/SafeERC20.sol";

import "../../../interfaces/yearn/IController.sol";
import "../../../interfaces/uniswap/Uni.sol";
import "../../../interfaces/curve/Curve.sol";

interface IMultiFeeDistribution {
    // Withdraw full unlocked balance and claim pending rewards
    function exit() external;
}

interface ILpTokenStaker {
    // Info of each user.
    struct UserInfo {
        uint256 amount;
        uint256 rewardDebt;
    }

    // Deposit LP tokens into the contract. Also triggers a claim.
    function deposit(uint256 _pid, uint256 _amount) external;

    // Withdraw LP tokens. Also triggers a claim.
    function withdraw(uint256 _pid, uint256 _amount) external;

    // Claim pending rewards for one or more pools.
    // Rewards are not received directly, they are minted by the rewardMinter.
    function claim(uint256[] calldata _pids) external;

    function userInfo(uint256 _pid, address _user)
        external
        view
        returns (UserInfo memory);

    function rewardMinter() external view returns (address);
}

contract StrategyEllipsisFusdt {
    using SafeERC20 for IERC20;
    using Address for address;
    using SafeMath for uint256;

    address public constant want = address(
        0x373410A99B64B089DFE16F1088526D399252dacE
    );
    address public constant eps = address(
        0xA7f552078dcC247C2684336020c03648500C6d9F
    );
    address public constant pancake = address(
        0x05fF2B0DB69458A0750badebc4f9e13aDd608C7F
    );
    address public constant wbnb = address(
        0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c
    ); // used for eps <> wbnb <> busd route

    address public constant busd = address(
        0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56
    );
    address public constant pool = address(
        0x556ea0b4c06D043806859c9490072FaadC104b63
    );
    address public constant threeEps = address(
        0xaF4dE8E872131AE328Ce21D909C74705d3Aaf452
    );
    address public constant threePool = address(
        0x160CAed03795365F3A589f10C379FfA7d75d4E76
    );

    address public constant lpTokenStaker = address(
        0xcce949De564fE60e7f96C85e55177F8B9E4CF61b
    );
    //address public constant voter = address(0xF147b8125d2ef93FB6965Db97D6746952a133934);
    /* address public constant voter = address(
        0x52f541764E6e90eeBc5c21Ff570De0e2D63766B6
    ); */

    // uint256 public keepCRV = 1000;
    uint256 public performanceFee = 1500;
    // uint256 public strategistReward = 0;
    uint256 public withdrawalFee = 50;
    uint256 public constant FEE_DENOMINATOR = 10000;

    address public proxy;

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
        return "StrategyEllipsisFusdt";
    }

    function setStrategist(address _strategist) external {
        require(
            msg.sender == governance || msg.sender == strategist,
            "!authorized"
        );
        strategist = _strategist;
    }

    /* function setKeepCRV(uint256 _keepCRV) external onlyGovernance {
        keepCRV = _keepCRV;
    } */

    function setWithdrawalFee(uint256 _withdrawalFee) external onlyGovernance {
        withdrawalFee = _withdrawalFee;
    }

    function setPerformanceFee(uint256 _performanceFee)
        external
        onlyGovernance
    {
        performanceFee = _performanceFee;
    }

    /* function setStrategistReward(uint256 _strategistReward)
        external
        onlyGovernance
    {
        strategistReward = _strategistReward;
    } */

    function setProxy(address _proxy) external onlyGovernance {
        proxy = _proxy;
    }

    function deposit() public {
        uint256 _want = IERC20(want).balanceOf(address(this));
        if (_want > 0) {
            IERC20(want).approve(lpTokenStaker, _want);
            ILpTokenStaker(lpTokenStaker).deposit(2, _want);
        }
    }

    // Controller only function for creating additional rewards from dust
    function withdraw(IERC20 _asset)
        external
        onlyController
        returns (uint256 balance)
    {
        require(want != address(_asset), "want");
        require(eps != address(_asset), "eps");
        balance = _asset.balanceOf(address(this));
        _asset.safeTransfer(controller, balance);
    }

    // Withdraw partial funds, normally used with a vault withdrawal
    function withdraw(uint256 _amount) external onlyController {
        uint256 _balance = IERC20(want).balanceOf(address(this));
        if (_balance < _amount) {
            _withdrawSome(_amount.sub(_balance));
        }

        uint256 _fee = _amount.mul(withdrawalFee).div(FEE_DENOMINATOR);

        IERC20(want).safeTransfer(IController(controller).rewards(), _fee);
        address _vault = IController(controller).vaults(address(want));
        require(_vault != address(0), "!vault"); // additional protection so we don't burn the funds
        IERC20(want).safeTransfer(_vault, _amount.sub(_fee));
    }

    function _withdrawSome(uint256 _amount) internal returns (uint256) {
        ILpTokenStaker(lpTokenStaker).withdraw(2, _amount);
        return _amount;
    }

    // Withdraw all funds, normally used when migrating strategies
    function withdrawAll() external onlyController returns (uint256 balance) {
        _withdrawAll();

        balance = IERC20(want).balanceOf(address(this));

        address _vault = IController(controller).vaults(address(want));
        require(_vault != address(0), "!vault"); // additional protection so we don't burn the funds
        IERC20(want).safeTransfer(_vault, balance);
    }

    function _withdrawAll() internal {
        _withdrawSome(balanceOfPool());
    }

    function harvest() public {
        require(
            msg.sender == strategist || msg.sender == governance,
            "!authorized"
        );

        {
            uint256[] memory _pids = new uint256[](1);
            _pids[0] = 2;

            // Claim all EPS rewards
            ILpTokenStaker(lpTokenStaker).claim(_pids);
        }

        IMultiFeeDistribution(ILpTokenStaker(lpTokenStaker).rewardMinter())
            .exit();

        uint256 _eps = IERC20(eps).balanceOf(address(this));
        if (_eps > 0) {
            IERC20(eps).safeApprove(pancake, 0);
            IERC20(eps).safeApprove(pancake, _eps);

            address[] memory path = new address[](3);
            path[0] = eps;
            path[1] = wbnb;
            path[2] = busd;

            Uni(pancake).swapExactTokensForTokens(
                _eps,
                uint256(0),
                path,
                address(this),
                now.add(1800)
            );
        }
        uint256 _busd = IERC20(busd).balanceOf(address(this));
        if (_busd > 0) {
            IERC20(busd).safeApprove(threePool, 0);
            IERC20(busd).safeApprove(threePool, _busd);
            ICurveFi(threePool).add_liquidity([_busd, 0, 0], 0);

            uint256 _threeEps = IERC20(threeEps).balanceOf(address(this));

            IERC20(threeEps).safeApprove(pool, 0);
            IERC20(threeEps).safeApprove(pool, _threeEps);
            ICurveFi(pool).add_liquidity([0, _threeEps], 0);
        }
        uint256 _want = IERC20(want).balanceOf(address(this));
        if (_want > 0) {
            uint256 _fee = _want.mul(performanceFee).div(FEE_DENOMINATOR);
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
        return ILpTokenStaker(lpTokenStaker).userInfo(2, address(this)).amount;
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
