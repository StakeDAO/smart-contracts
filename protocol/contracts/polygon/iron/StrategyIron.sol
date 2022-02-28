pragma solidity ^0.5.17;
pragma experimental ABIEncoderV2;

// yarn add @openzeppelin/contracts@2.5.1
import "@openzeppelinV2/contracts/token/ERC20/IERC20.sol";
import "@openzeppelinV2/contracts/math/SafeMath.sol";
import "@openzeppelinV2/contracts/utils/Address.sol";
import "@openzeppelinV2/contracts/token/ERC20/SafeERC20.sol";

// import "hardhat/console.sol";

interface Sushi {
    function swapExactTokensForTokens(
        uint256 amountIn,
        uint256 amountOutMin,
        address[] calldata path,
        address to,
        uint256 deadline
    ) external returns (uint256[] memory amounts);

    function addLiquidity(
        address tokenA,
        address tokenB,
        uint256 amountADesired,
        uint256 amountBDesired,
        uint256 amountAMin,
        uint256 amountBMin,
        address to,
        uint256 deadline
    )
        external
        returns (
            uint256 amountA,
            uint256 amountB,
            uint256 liquidity
        );

    function removeLiquidity(
        address tokenA,
        address tokenB,
        uint256 liquidity,
        uint256 amountAMin,
        uint256 amountBMin,
        address to,
        uint256 deadline
    ) external returns (uint256 amountA, uint256 amountB);

    function getAmountsOut(uint256, address[] calldata)
        external
        returns (uint256[] memory);

    function quote(
        uint256 amountA,
        uint256 reserveA,
        uint256 reserveB
    ) external view returns (uint256 amountB);
}

interface IMasterChef {
    struct UserInfo {
        uint256 amount;
        uint256 rewardDebt;
    }

    function deposit(uint256 _pid, uint256 _amount) external;

    function withdraw(uint256 _pid, uint256 _amount) external;

    function userInfo(uint256 pid, address userAddress)
        external
        view
        returns (UserInfo memory);
}

interface IPair {
    function getReserves()
        external
        view
        returns (
            uint256 reserve0,
            uint256 reserve1,
            uint32 blockTimestampLast
        );

    function totalSupply() external view returns (uint256);
}

interface IController {
    function withdraw(address, uint256) external;

    function balanceOf(address) external view returns (uint256);

    function earn(address, uint256) external;

    function want(address) external view returns (address);

    function rewards() external view returns (address);

    function vaults(address) external view returns (address);

    function strategies(address) external view returns (address);
}

contract StrategyIronUsdc {
    using SafeERC20 for IERC20;
    using Address for address;
    using SafeMath for uint256;

    //usdc
    address public constant want =
        address(0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174);

    address public constant iron =
        address(0xD86b5923F3AD7b585eD81B448170ae026c65ae9a);

    address public constant titan =
        address(0xaAa5B9e6c589642f98a1cDA99B9D024B8407285A);

    address public constant slp =
        address(0x85dE135fF062Df790A5f20B79120f17D3da63b2d);

    address public constant masterchef =
        address(0x65430393358e55A658BcdE6FF69AB28cF1CbB77a);

    address public constant sushiRouter =
        address(0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506);

    uint256 public performanceFee = 1500;
    uint256 public withdrawalFee = 50;
    uint256 public constant FEE_DENOMINATOR = 10000;

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
        return "StrategyIron";
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

    function getBestAddLiquidity() internal view returns (uint256, uint256) {
        uint256 amUSDC;
        uint256 amIRON;

        (uint256 res0, uint256 res1, ) = IPair(slp).getReserves();
        uint256 totalSupply = IPair(slp).totalSupply();

        uint256 _usdc = IERC20(want).balanceOf(address(this)); // token0
        uint256 _iron = IERC20(iron).balanceOf(address(this)); // token1

        uint256 lp0 = _usdc.mul(1e12).mul(totalSupply).div(res0.mul(1e12)); // usdc is decimal 6
        uint256 lp1 = _iron.mul(totalSupply).div(res1);

        if (lp0 > lp1) {
            amUSDC = Sushi(sushiRouter).quote(_iron, res1, res0);
            amIRON = _iron;
        } else {
            amUSDC = _usdc;
            amIRON = Sushi(sushiRouter).quote(_usdc, res0, res1);
        }

        return (amUSDC, amIRON);
    }

    // return correct amount of usdc to swap based on usdc and iron balance
    function getBestSwapAmount() internal view returns (uint256) {
        uint256 _usdc = IERC20(want).balanceOf(address(this));
        uint256 _iron = IERC20(iron).balanceOf(address(this));
        (uint256 res0, uint256 res1, ) = IPair(slp).getReserves();
        uint256 ratio = res0.mul(1e12).mul(1e18).div(res1);
        uint256 ironInUSDC = _iron.mul(ratio).div(1e18).div(1e12);

        uint256 allUSDC = _usdc.add(ironInUSDC);
        uint256 halfUSDC = allUSDC.div(2).mul(ratio).div(1e18);
        uint256 expectedIRONinUSDC = allUSDC.sub(halfUSDC);

        if (ironInUSDC >= expectedIRONinUSDC) {
            return 0;
        }

        return expectedIRONinUSDC.sub(ironInUSDC);
    }

    function deposit() public {
        uint256 _amount = getBestSwapAmount();

        if (_amount > 0) {
            swapAsset(want, iron, _amount);
        }

        uint256 _iron = IERC20(iron).balanceOf(address(this));

        if (_iron > 0) {
            // here we are supposed to have approximately the good usdc iron ratio before calling that
            (uint256 amUSDC, uint256 amIRON) = getBestAddLiquidity();

            IERC20(want).safeApprove(sushiRouter, 0);
            IERC20(iron).safeApprove(sushiRouter, 0);
            IERC20(iron).safeApprove(sushiRouter, amIRON);
            IERC20(want).safeApprove(sushiRouter, amUSDC);

            uint256 _amountIronMin = amIRON.mul(995).div(1000);
            uint256 _amountUsdcMin = amUSDC.mul(995).div(1000);

            // console.log("amIRON", amIRON);
            // console.log("amUSDC", amUSDC);
            // console.log("_amountIronMin", _amountIronMin);
            // console.log("_amountUsdcMin", _amountUsdcMin);

            Sushi(sushiRouter).addLiquidity(
                iron,
                want,
                amIRON,
                amUSDC,
                _amountIronMin,
                _amountUsdcMin,
                address(this),
                now.add(1800)
            );
        }

        uint256 _slp = IERC20(slp).balanceOf(address(this));

        if (_slp > 0) {
            IERC20(slp).safeApprove(masterchef, _slp);
            IMasterChef(masterchef).deposit(1, _slp);
        }
    }

    function withdraw(IERC20 _asset)
        external
        onlyController
        returns (uint256 balance)
    {
        require(want != address(_asset), "want");
        require(iron != address(_asset), "iron");
        require(titan != address(_asset), "titan");
        require(slp != address(_asset), "slp");

        balance = _asset.balanceOf(address(this));
        _asset.safeTransfer(controller, balance);
    }

    function swapAsset(
        address assetFrom,
        address assetTo,
        uint256 amount
    ) internal returns (uint256 output) {
        IERC20(assetFrom).safeApprove(sushiRouter, 0);
        IERC20(assetFrom).safeApprove(sushiRouter, amount);

        address[] memory path = new address[](2);
        path[0] = assetFrom;
        path[1] = assetTo;

        uint256[] memory _amounts =
            Sushi(sushiRouter).getAmountsOut(amount, path);
        uint256 _minimalAmount = _amounts[1].mul(995).div(1000);

        uint256[] memory outputs =
            Sushi(sushiRouter).swapExactTokensForTokens(
                amount,
                _minimalAmount,
                path,
                address(this),
                now.add(1800)
            );

        return outputs[1];
    }

    function swapTitanToWant() internal returns (uint256 output) {
        uint256 _titan = IERC20(titan).balanceOf(address(this));

        if (_titan > 0) {
            return swapAsset(titan, want, _titan);
        }
    }

    function swapIronToWant() internal {
        uint256 _iron = IERC20(iron).balanceOf(address(this));

        if (_iron > 0) {
            swapAsset(iron, want, _iron);
        }
    }

    function swapAssetsToWant() internal {
        swapTitanToWant();
        swapIronToWant();
    }

    function withdraw(uint256 _amount) external onlyController {
        uint256 _balance = IERC20(want).balanceOf(address(this));

        if (_balance < _amount) {
            _withdrawSome(_amount.sub(_balance));
        }

        uint256 _usdc = IERC20(want).balanceOf(address(this));

        // due to slippage you can have less than desired, especially at launch
        if (_amount > _usdc) {
            _amount = _usdc;
        }

        uint256 _fee = _amount.mul(withdrawalFee).div(FEE_DENOMINATOR);
        IERC20(want).safeTransfer(IController(controller).rewards(), _fee);
        address _vault = IController(controller).vaults(address(want));
        require(_vault != address(0), "!vault");
        IERC20(want).safeTransfer(_vault, _amount.sub(_fee));
    }

    function _withdrawSome(uint256 _amount) internal {
        uint256 balanceOfPoolInUSDC = balanceOfPool();
        (uint256 res0, uint256 res1, ) = IPair(slp).getReserves();
        uint256 totalSupply = IPair(slp).totalSupply();

        IMasterChef.UserInfo memory userInfo =
            IMasterChef(masterchef).userInfo(1, address(this));

        uint256 lpAmount =
            _amount.mul(userInfo.amount).div(balanceOfPoolInUSDC);
        uint256 amountAMin =
            lpAmount.mul(res1).div(totalSupply).mul(995).div(1000);
        uint256 amountBMin =
            lpAmount.mul(res0).div(totalSupply).mul(995).div(1000);

        IMasterChef(masterchef).withdraw(1, lpAmount);

        IERC20(slp).safeApprove(sushiRouter, 0);
        IERC20(slp).safeApprove(sushiRouter, lpAmount);

        Sushi(sushiRouter).removeLiquidity(
            iron,
            want,
            lpAmount,
            amountAMin,
            amountBMin,
            address(this),
            now.add(1800)
        );

        swapAssetsToWant();
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
        (uint256 res0, uint256 res1, ) = IPair(slp).getReserves();
        uint256 totalSupply = IPair(slp).totalSupply();

        IMasterChef.UserInfo memory userInfo =
            IMasterChef(masterchef).userInfo(1, address(this));

        uint256 lpAmount = userInfo.amount;
        uint256 amountAMin =
            lpAmount.div(totalSupply).div(res1).mul(995).div(1000);
        uint256 amountBMin =
            lpAmount.div(totalSupply).div(res0).mul(995).div(1000);

        IMasterChef(masterchef).withdraw(1, lpAmount);

        IERC20(slp).safeApprove(sushiRouter, 0);
        IERC20(slp).safeApprove(sushiRouter, lpAmount);

        Sushi(sushiRouter).removeLiquidity(
            iron,
            want,
            lpAmount,
            amountAMin,
            amountBMin,
            address(this),
            now.add(1800)
        );

        swapAssetsToWant();
    }

    function harvest() public {
        require(
            msg.sender == strategist || msg.sender == governance,
            "!authorized"
        );

        IMasterChef(masterchef).deposit(1, 0);
        uint256 output = swapTitanToWant();

        if (output > 0) {
            uint256 _fee = output.mul(performanceFee).div(FEE_DENOMINATOR);
            IERC20(want).safeTransfer(IController(controller).rewards(), _fee);
            deposit();
        }

        earned = earned.add(output);
        emit Harvested(output, earned);
    }

    function balanceOfWant() public view returns (uint256) {
        return IERC20(want).balanceOf(address(this));
    }

    function balanceOfPool() public view returns (uint256) {
        (uint256 res0, uint256 res1, ) = IPair(slp).getReserves();
        uint256 totalSupply = IPair(slp).totalSupply();

        IMasterChef.UserInfo memory userInfo =
            IMasterChef(masterchef).userInfo(1, address(this));

        uint256 _usdc = userInfo.amount.mul(res0).div(totalSupply);
        uint256 _iron = userInfo.amount.mul(res1).div(totalSupply);

        uint256 ratio = res0.mul(1e12).mul(1e18).div(res1);
        uint256 ironInUSDC = _iron.mul(ratio).div(1e18).div(1e12);

        return _usdc.add(ironInUSDC);
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
