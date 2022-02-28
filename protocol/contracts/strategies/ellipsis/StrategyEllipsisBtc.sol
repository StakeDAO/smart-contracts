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

contract StrategyEllipsisBtc {
    using SafeERC20 for IERC20;
    using Address for address;
    using SafeMath for uint256;

    address public constant want = address(
        0x2a435Ecb3fcC0E316492Dc1cdd62d0F189be5640
    );
    address public constant eps = address(
        0xA7f552078dcC247C2684336020c03648500C6d9F
    );
    address public constant pancake = address(
        0x05fF2B0DB69458A0750badebc4f9e13aDd608C7F
    );
    address public constant wbnb = address(
        0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c
    ); // used for eps <> wbnb <> btcb route

    address public constant btcb = address(
        0x7130d2A12B9BCbFAe4f2634d864A1Ee1Ce3Ead9c
    );
    address public constant pool = address(
        0x2477fB288c5b4118315714ad3c7Fd7CC69b00bf9
    );

    address public constant lpTokenStaker = address(
        0xcce949De564fE60e7f96C85e55177F8B9E4CF61b
    );

    uint256 public performanceFee = 1500;
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
        return "StrategyEllipsisBtc";
    }

    function setStrategist(address _strategist) external {
        require(
            msg.sender == governance || msg.sender == strategist,
            "!authorized"
        );
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

    function setProxy(address _proxy) external onlyGovernance {
        proxy = _proxy;
    }

    function deposit() public {
        uint256 _want = IERC20(want).balanceOf(address(this));
        if (_want > 0) {
            IERC20(want).approve(lpTokenStaker, _want);
            ILpTokenStaker(lpTokenStaker).deposit(3, _want);
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
        ILpTokenStaker(lpTokenStaker).withdraw(3, _amount);
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
            _pids[0] = 3;

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
            path[2] = btcb;

            Uni(pancake).swapExactTokensForTokens(
                _eps,
                uint256(0),
                path,
                address(this),
                now.add(1800)
            );
        }
        uint256 _btcb = IERC20(btcb).balanceOf(address(this));
        if (_btcb > 0) {
            IERC20(btcb).safeApprove(pool, 0);
            IERC20(btcb).safeApprove(pool, _btcb);
            ICurveFi(pool).add_liquidity([_btcb, 0], 0);
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
        return ILpTokenStaker(lpTokenStaker).userInfo(3, address(this)).amount;
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
