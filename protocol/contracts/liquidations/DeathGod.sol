pragma solidity ^0.5.17;

pragma experimental ABIEncoderV2;

import "@openzeppelinV2/contracts/token/ERC20/IERC20.sol";
import "@openzeppelinV2/contracts/math/SafeMath.sol";
import "@openzeppelinV2/contracts/utils/Address.sol";
import "@openzeppelinV2/contracts/token/ERC20/SafeERC20.sol";
import "@openzeppelinV2/contracts/token/ERC20/ERC20.sol";
import "@openzeppelinV2/contracts/token/ERC20/ERC20Detailed.sol";
import "@openzeppelinV2/contracts/ownership/Ownable.sol";

import "../../interfaces/uniswap/Uni.sol";
import "../../interfaces/flashLoan/IERC3156FlashBorrower.sol";
import "../../interfaces/flashLoan/IERC3156FlashLender.sol";
import "../../interfaces/archer/ITipJar.sol";

interface ILendingPool {
    function liquidationCall(
        address _collateral,
        address _reserve,
        address _user,
        uint256 _purchaseAmount,
        bool _receiveAToken
    ) external payable;
}

interface ILendingPoolAddressesProvider {
    function getLendingPool() external view returns (address);
}

contract DeathGod is IERC3156FlashBorrower {
    using SafeERC20 for IERC20;
    using Address for address;
    using SafeMath for uint256;

    enum Action {
        NORMAL,
        OTHER
    }

    address public governance;
    mapping(address => bool) public keepers;
    address public darkParadise;
    address public constant uni =
        address(0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D);
    address public constant weth =
        address(0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2);
    address public constant sdt =
        address(0x73968b9a57c6E53d41345FD57a6E6ae27d6CDB2F);
    address public lendingPoolAddressProvider =
        address(0xB53C1a33016B2DC2fF3653530bfF1848a515c8c5);
    address public treasury =
        address(0x9D75C85f864Ab9149E23F27C35addaE09B9B909C);

    uint256 public performanceFee = 2000;
    uint256 public constant FEE_DENOMINATOR = 10000;

    IERC3156FlashLender lender;
    ITipJar public tipJar;

    modifier onlyGovernance() {
        require(msg.sender == governance, "!governance");
        _;
    }

    function() external payable {}

    constructor(
        address _keeper,
        address _darkParadise,
        IERC3156FlashLender _lender,
        address _tipJar
    ) public {
        governance = msg.sender;
        keepers[_keeper] = true;
        darkParadise = _darkParadise;
        lender = _lender;
        tipJar = ITipJar(_tipJar);
    }

    function setPerformanceFee(uint256 _performanceFee)
        external
        onlyGovernance
    {
        performanceFee = _performanceFee;
    }

    function setAaveLendingPoolAddressProvider(
        address _lendingPoolAddressProvider
    ) external onlyGovernance {
        lendingPoolAddressProvider = _lendingPoolAddressProvider;
    }

    function setLender(IERC3156FlashLender _lender) external onlyGovernance {
        lender = _lender;
    }

    function setTipJar(address _tipJar) external onlyGovernance {
        tipJar = ITipJar(_tipJar);
    }

    function setDarkParadise(address _darkParadise) external onlyGovernance {
        darkParadise = _darkParadise;
    }

    function setGovernance(address _governance) external onlyGovernance {
        governance = _governance;
    }

    function addKeeper(address _keeper) external onlyGovernance {
        keepers[_keeper] = true;
    }

    function removeKeeper(address _keeper) external onlyGovernance {
        keepers[_keeper] = false;
    }

    function sendSDTToDarkParadise(address _token, uint256 _amount)
        public
        payable
    {
        require(
            msg.sender == governance || keepers[msg.sender] == true,
            "Not authorised"
        );
        require(msg.value > 0, "tip amount must be > 0");
        require(
            _amount <= IERC20(_token).balanceOf(address(this)),
            "Not enough tokens"
        );
        // pay tip in ETH to miner
        tipJar.tip.value(msg.value)();

        IERC20(_token).safeApprove(uni, _amount);
        address[] memory path = new address[](3);
        path[0] = _token;
        path[1] = weth;
        path[2] = sdt;

        uint256 _sdtBefore = IERC20(sdt).balanceOf(address(this));
        Uni(uni).swapExactTokensForTokens(
            _amount,
            uint256(0),
            path,
            address(this),
            now.add(1800)
        );
        uint256 _sdtAfter = IERC20(sdt).balanceOf(address(this));

        IERC20(sdt).safeTransfer(darkParadise, _sdtAfter.sub(_sdtBefore));
    }

    /// @dev ERC-3156 Flash loan callback
    function onFlashLoan(
        address initiator,
        address token,
        uint256 amount,
        uint256 fee,
        bytes calldata data
    ) external returns (bytes32) {
        require(
            msg.sender == address(lender),
            "FlashBorrower: Untrusted lender"
        );
        require(
            initiator == address(this),
            "FlashBorrower: Untrusted loan initiator"
        );
        // Action action = abi.decode(data, (Action));
        (
            Action action,
            address _collateralAsset,
            address _debtAsset,
            address _user,
            uint256 _debtToCover,
            bool _receiveaToken,
            uint256 _minerTipPct
        ) = abi.decode(
            data,
            (Action, address, address, address, uint256, bool, uint256)
        );
        if (action == Action.NORMAL) {
            useFlashLoan(
                _collateralAsset,
                _debtAsset,
                _user,
                _debtToCover,
                _receiveaToken,
                _minerTipPct
            );
        } else if (action == Action.OTHER) {
            // do another
        }
        return keccak256("ERC3156FlashBorrower.onFlashLoan");
    }

    function useFlashLoan(
        address _collateralAsset,
        address _debtAsset,
        address _user,
        uint256 _debtToCover,
        bool _receiveaToken,
        uint256 _minerTipPct
    ) private {
        ILendingPool lendingPool = ILendingPool(
            ILendingPoolAddressesProvider(lendingPoolAddressProvider)
            .getLendingPool()
        );
        require(
            IERC20(_debtAsset).approve(address(lendingPool), _debtToCover),
            "Approval error"
        );

        // uint256 _ethBefore = address(this).balance;
        uint256 collateralBefore = IERC20(_collateralAsset).balanceOf(
            address(this)
        );
        // Calling liquidate() on AAVE. Assumes this contract already has `_debtToCover` amount of `_debtAsset`
        lendingPool.liquidationCall(
            _collateralAsset,
            _debtAsset,
            _user,
            _debtToCover,
            _receiveaToken
        );
        uint256 collateralAfter = IERC20(_collateralAsset).balanceOf(
            address(this)
        );
        // uint256 _ethAfter = address(this).balance;

        // Swapping ETH to USDC
        IERC20(_collateralAsset).safeApprove(
            uni,
            collateralAfter.sub(collateralBefore)
        );
        address[] memory path = new address[](2);
        path[0] = _collateralAsset;
        path[1] = _debtAsset;

        uint256 _debtAssetBefore = IERC20(_debtAsset).balanceOf(address(this));
        Uni(uni).swapExactTokensForTokens(
            collateralAfter.sub(collateralBefore),
            uint256(0),
            path,
            address(this),
            now.add(1800)
        );
        uint256 _debtAssetAfter = IERC20(_debtAsset).balanceOf(address(this));

        // liquidation profit = Net USDC later - FlashLoaned USDC - FlashFee
        uint256 profit = _debtAssetAfter
        .sub(_debtAssetBefore)
        .sub(_debtToCover)
        .sub(lender.flashFee(_debtAsset, _debtToCover));
        // _minerTipPct % of liquidation profit to miner
        tipMinerInToken(
            _debtAsset,
            profit.mul(_minerTipPct).div(10000),
            _collateralAsset
        );
        // sending performance fees to treasury
        sendFeeToTreasury(_debtAsset);
    }

    // _minerTipPct: 2500 for 25% of liquidation profits
    function liquidateOnAave(
        address _collateralAsset,
        address _debtAsset,
        address _user,
        uint256 _debtToCover,
        bool _receiveaToken,
        uint256 _minerTipPct
    ) public payable {
        require(keepers[msg.sender] == true, "Not a keeper");
        // taking flash-loan
        // bytes memory data = abi.encode(_collateralAsset, _debtAsset, _user, _debtToCover, _receiveaToken, _minerTipPct);
        flashBorrow(
            _debtAsset,
            _debtToCover,
            _collateralAsset,
            _user,
            _receiveaToken,
            _minerTipPct
        );
    }

    /// @dev Initiate a flash loan
    function flashBorrow(
        address _token,
        uint256 _amount,
        address _collateralAsset,
        address _user,
        bool _receiveaToken,
        uint256 _minerTipPct
    ) private {
        bytes memory data = abi.encode(
            Action.NORMAL,
            _collateralAsset,
            _token,
            _user,
            _amount,
            _receiveaToken,
            _minerTipPct
        );
        uint256 _allowance = IERC20(_token).allowance(
            address(this),
            address(lender)
        );
        uint256 _fee = lender.flashFee(_token, _amount);
        uint256 _repayment = _amount + _fee;
        IERC20(_token).approve(address(lender), _allowance + _repayment);
        lender.flashLoan(this, _token, _amount, data);
    }

    function tipMinerInToken(
        address _tipToken,
        uint256 _tipAmount,
        address _collateralAsset
    ) private {
        // swapping miner's profit USDC to ETH
        IERC20(_tipToken).safeApprove(uni, _tipAmount);
        address[] memory path = new address[](2);
        path[0] = _tipToken;
        path[1] = _collateralAsset;

        uint256 _ethBefore = address(this).balance;
        Uni(uni).swapExactTokensForETH(
            _tipAmount,
            uint256(0),
            path,
            address(this),
            now.add(1800)
        );
        uint256 _ethAfter = address(this).balance;
        // sending tip in ETH to miner
        tipJar.tip.value(_ethAfter.sub(_ethBefore))();
    }

    function sendFeeToTreasury(address _debtAsset) private {
        uint256 _debtAssetRemaining = IERC20(_debtAsset).balanceOf(
            address(this)
        );
        uint256 _fee = _debtAssetRemaining.mul(performanceFee).div(
            FEE_DENOMINATOR
        );
        IERC20(_debtAsset).safeTransfer(treasury, _fee);
    }
}
