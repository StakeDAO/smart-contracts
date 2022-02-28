pragma solidity ^0.5.17;

pragma experimental ABIEncoderV2;

import "@openzeppelinV2/contracts/token/ERC20/SafeERC20.sol";
import "@openzeppelinV2/contracts/token/ERC20/IERC20.sol";
import "@openzeppelinV2/contracts/utils/Address.sol";
import "../../interfaces/yearn/IController.sol";
import "../../interfaces/dydx/DydxFlashloanBase.sol";
import "../../interfaces/dydx/ICallee.sol";
import "../../interfaces/uniswap/Uni.sol";

interface ILendingPool {
    function deposit(
        address asset,
        uint256 amount,
        address onBehalfOf,
        uint16 referralCode
    ) external;

    function withdraw(
        address asset,
        uint256 amount,
        address to
    ) external;

    function borrow(
        address asset,
        uint256 amount,
        uint256 interestRateMode,
        uint16 referralCode,
        address onBehalfOf
    ) external;

    function repay(
        address asset,
        uint256 amount,
        uint256 rateMode,
        address onBehalfOf
    ) external;
}

interface IStableDebtToken {
    function principalBalanceOf(address user) external view returns (uint256);
}

interface IVariableDebtToken {
    function balanceOf(address user) external view returns (uint256);
}

interface IAToken {
    function balanceOf(address user) external view returns (uint256);

    function scaledBalanceOf(address user) external view returns (uint256);

    function getScaledUserBalanceAndSupply(address user)
        external
        view
        returns (uint256, uint256);
}

interface IStakedTokenIncentivesController {
    function getRewardsBalance(address[] calldata assets, address user)
        external
        view
        returns (uint256);

    function claimRewards(
        address[] calldata assets,
        uint256 amount,
        address to
    ) external returns (uint256);
}

interface IStakedToken {
    function cooldown() external;

    function redeem(address to, uint256 amount) external;
}

contract StrategyAaveUSDCLeverage is DydxFlashloanBase, ICallee {
    using SafeERC20 for IERC20;
    using Address for address;
    using SafeMath for uint256;

    address public constant want = address(
        0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48
    );

    address public constant aave = address(
        0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9
    );

    address public constant weth = address(
        0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2
    );

    address public constant uni = address(
        0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D
    );

    address public constant treasury = address(
        0x9D75C85f864Ab9149E23F27C35addaE09B9B909C
    );

    address public constant aaveLendingPool = address(
        0x7d2768dE32b0b80b7a3454c06BdAc94A69DDc7A9
    );

    address public constant aUSDC = address(
        0xBcca60bB61934080951369a648Fb03DF4F96263C
    );

    address public constant stableDebtUSDC = address(
        0xE4922afAB0BbaDd8ab2a88E0C79d884Ad337fcA6
    );

    address public constant variableDebtUSDC = address(
        0x619beb58998eD2278e08620f97007e1116D5D25b
    );

    address public constant stkAAVE = address(
        0x4da27a545c0c5B758a6BA100e3a049001de870f5
    );

    address public constant stkAAVEController = address(
        0xd784927Ff2f95ba542BfC824c8a8a98F3495f6b5
    );

    address private constant SOLO = address(
        0x1E0447b19BB6EcFdAe1e4AE1694b0C3659614e4e
    );

    uint256 public performanceFee = 1500;
    uint256 public withdrawalFee = 50;
    uint256 public constant FEE_DENOMINATOR = 10000;
    uint256 public flashLoanleverage = 3;

    address public governance;
    address public controller;
    address public strategist;

    uint256 public earned; // lifetime strategy earnings denominated in `want` token

    event Harvested(uint256 wantEarned, uint256 lifetimeEarned);

    constructor(address _governance, address _controller) public {
        governance = _governance;
        strategist = msg.sender;
        controller = _controller;
    }

    function getName() external pure returns (string memory) {
        return "StrategyAaveUSDCLeverage";
    }

    // Returns the current lending position of the strategy in AAVE
    function getCurrentPosition()
        public
        view
        returns (uint256 deposits, uint256 borrows)
    {
        deposits = IAToken(aUSDC).balanceOf(address(this));
        borrows = IVariableDebtToken(variableDebtUSDC).balanceOf(address(this));
    }

    function balanceOfWant() public view returns (uint256) {
        return IERC20(want).balanceOf(address(this));
    }

    function balanceOfPool() public view returns (uint256) {
        (uint256 deposits, uint256 borrows) = getCurrentPosition();
        return deposits.sub(borrows);
    }

    function balanceOf() public view returns (uint256) {
        return balanceOfWant().add(balanceOfPool());
    }

    function maxApprove() external {
        require(msg.sender == governance, "!governance");
        IERC20(aave).safeApprove(uni, uint256(-1));
        IERC20(want).safeApprove(SOLO, uint256(-1));
        IERC20(want).safeApprove(aaveLendingPool, uint256(-1));
    }

    function setStrategist(address _strategist) external {
        require(
            msg.sender == governance || msg.sender == strategist,
            "!authorized"
        );
        strategist = _strategist;
    }

    function setGovernance(address _governance) external {
        require(msg.sender == governance, "!governance");
        governance = _governance;
    }

    function setController(address _controller) external {
        require(msg.sender == governance, "!governance");
        controller = _controller;
    }

    function setWithdrawalFee(uint256 _withdrawalFee) external {
        require(msg.sender == governance, "!governance");
        withdrawalFee = _withdrawalFee;
    }

    function setPerformanceFee(uint256 _performanceFee) external {
        require(msg.sender == governance, "!governance");
        performanceFee = _performanceFee;
    }

    function setFlashLoanLeverage(uint256 _leverage) external {
        require(msg.sender == governance, "!governance");
        flashLoanleverage = _leverage;
    }

    function deposit() public {
        uint256 _want = IERC20(want).balanceOf(address(this));
        // _want = _want.sub(1e6);
        if (_want > 0) {
            // depositing n
            ILendingPool(aaveLendingPool).deposit(
                want,
                _want,
                address(this),
                0
            );
        }
        // 4x leverage on deposit amount
        doDyDxFlashLoan(false, _want.mul(flashLoanleverage), 0);
    }

    function doDyDxFlashLoan(
        bool deficit,
        uint256 amountDesired,
        uint256 ask
    ) private returns (uint256) {
        uint256 amount = amountDesired;
        ISoloMargin solo = ISoloMargin(SOLO);
        uint256 marketId = _getMarketIdFromTokenAddress(SOLO, address(want));
        // Not enough USDC in DyDx. So we take all we can
        uint256 amountInSolo = IERC20(want).balanceOf(SOLO);
        if (amountInSolo < amount) {
            amount = amountInSolo;
        }
        uint256 repayAmount = _getRepaymentAmountInternal(amount);
        bytes memory data = abi.encode(deficit, amount, repayAmount, ask);
        // 1. Withdraw $
        // 2. Call callFunction(...)
        // 3. Deposit back $
        Actions.ActionArgs[] memory operations = new Actions.ActionArgs[](3);
        operations[0] = _getWithdrawAction(marketId, amount);
        operations[1] = _getCallAction(
            // Encode custom data for callFunction
            data
        );
        operations[2] = _getDepositAction(marketId, repayAmount);
        Account.Info[] memory accountInfos = new Account.Info[](1);
        accountInfos[0] = _getAccountInfo();
        solo.operate(accountInfos, operations);
        return amount;
    }

    function callFunction(
        address sender,
        Account.Info memory account,
        bytes memory data
    ) public {
        (bool deficit, uint256 amount, uint256 repayAmount, uint256 ask) = abi
            .decode(data, (bool, uint256, uint256, uint256));

        _loanLogic(deficit, amount, repayAmount, ask);
    }

    function _loanLogic(
        bool deficit,
        uint256 amount,
        uint256 repayAmount,
        uint256 ask
    ) internal {
        uint256 bal = IERC20(want).balanceOf(address(this));
        require(bal >= amount, "FLASH_FAILED"); // to stop malicious calls
        // in deficit we repay amount and then withdraw
        if (deficit) {
            // repaying yn
            uint256 poolBalance = balanceOfPool();
            ILendingPool(aaveLendingPool).repay(want, amount, 2, address(this));
            // need to read balanceOfPool() before repay()
            if (ask == poolBalance) {
                ILendingPool(aaveLendingPool).withdraw(
                    want,
                    uint256(-1),
                    address(this)
                );
            } else {
                // withdrawing yn + n
                ILendingPool(aaveLendingPool).withdraw(
                    want,
                    amount.add(amount.div(flashLoanleverage)).add(2),
                    address(this)
                );
            }
        } else {
            // depositing yn
            ILendingPool(aaveLendingPool).deposit(
                want,
                amount,
                address(this),
                0
            );
            // borrowing yn + 2
            // fee is so low for dydx that it does not effect our liquidation risk.
            // DONT USE FOR AAVE FLASH LOAN
            ILendingPool(aaveLendingPool).borrow(
                want,
                repayAmount,
                2,
                0,
                address(this)
            );
        }
    }

    function claimStkAAVE() public {
        require(
            msg.sender == strategist || msg.sender == governance,
            "!authorized"
        );

        address[] memory assets = new address[](2);
        assets[0] = aUSDC;
        assets[1] = variableDebtUSDC;

        uint256 rewards = IStakedTokenIncentivesController(stkAAVEController)
            .getRewardsBalance(assets, address(this));
        // claim stkAAVE
        IStakedTokenIncentivesController(stkAAVEController).claimRewards(
            assets,
            rewards,
            address(this)
        );
        // activate 10 day cooldown
        IStakedToken(stkAAVE).cooldown();
    }

    function harvest() public {
        require(
            msg.sender == strategist || msg.sender == governance,
            "!authorized"
        );
        // burn stkAAVE for AAVE
        IStakedToken(stkAAVE).redeem(address(this), uint256(-1));

        uint256 _aave = IERC20(aave).balanceOf(address(this));
        address[] memory path = new address[](3);
        path[0] = aave;
        path[1] = weth;
        path[2] = want;

        Uni(uni).swapExactTokensForTokens(
            _aave,
            uint256(0),
            path,
            address(this),
            now.add(1800)
        );

        uint256 _want = IERC20(want).balanceOf(address(this));
        uint256 perfFees = _want.mul(performanceFee).div(FEE_DENOMINATOR);
        IERC20(want).safeTransfer(treasury, perfFees);

        earned = earned.add(balanceOfWant());
        emit Harvested(balanceOfWant(), earned);

        deposit();
    }

    function _withdrawSome(uint256 _amount) internal returns (uint256) {
        require(
            _amount <= balanceOfPool(),
            "Withdraw amount exceeds pool balance"
        );
        (uint256 deposits, uint256 borrows) = getCurrentPosition();

        if (_amount == balanceOfPool()) {
            doDyDxFlashLoan(true, borrows, _amount);
        } else {
            doDyDxFlashLoan(true, _amount.mul(flashLoanleverage), 0);
        }
        return balanceOfWant();
    }

    // Withdraw partial funds, normally used with a vault withdrawal
    function withdraw(uint256 _amount) external {
        require(msg.sender == controller, "!controller");
        uint256 _balance = IERC20(want).balanceOf(address(this));
        if (_balance < _amount) {
            uint256 diff;

            uint256 usdcBefore = IERC20(want).balanceOf(address(this));
            _withdrawSome(_amount.sub(_balance));
            uint256 usdcAfter = IERC20(want).balanceOf(address(this));

            diff = usdcAfter.sub(usdcBefore);
            if (diff < _amount.sub(_balance)) {
                _amount = _balance.add(diff);
            }
        }

        uint256 _fee = _amount.mul(withdrawalFee).div(FEE_DENOMINATOR);
        IERC20(want).safeTransfer(IController(controller).rewards(), _fee);

        address _vault = IController(controller).vaults(address(want));
        require(_vault != address(0), "!vault"); // additional protection so we don't burn the funds
        IERC20(want).safeTransfer(_vault, _amount.sub(_fee));
    }

    // Exit entire position, in case c-ratio is in danger. Call withdrawAll() on controller
    function withdrawAll() external returns (uint256 balance) {
        require(msg.sender == controller, "!controller");
        _withdrawSome(balanceOfPool());

        balance = IERC20(want).balanceOf(address(this));

        address _vault = IController(controller).vaults(address(want));
        require(_vault != address(0), "!vault"); // additional protection so we don't burn the funds
        IERC20(want).safeTransfer(_vault, balance);
    }

    // Controller only function for creating additional rewards from dust
    function withdraw(IERC20 _asset) external returns (uint256 balance) {
        require(msg.sender == controller, "!controller");
        require(want != address(_asset), "want");
        balance = _asset.balanceOf(address(this));
        _asset.safeTransfer(controller, balance);
    }
}
