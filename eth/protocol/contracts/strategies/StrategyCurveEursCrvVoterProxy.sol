pragma solidity ^0.5.17;

import "@openzeppelinV2/contracts/token/ERC20/IERC20.sol";
import "@openzeppelinV2/contracts/math/SafeMath.sol";
import "@openzeppelinV2/contracts/utils/Address.sol";
import "@openzeppelinV2/contracts/token/ERC20/SafeERC20.sol";

import "../../interfaces/yearn/IController.sol";
import "../../interfaces/curve/Gauge.sol";
import "../../interfaces/curve/Mintr.sol";
import "../../interfaces/uniswap/Uni.sol";
import "../../interfaces/curve/Curve.sol";
import "../../interfaces/yearn/IToken.sol";
import "../../interfaces/yearn/IVoterProxy.sol";

contract StrategyCurveEursCrvVoterProxy {
    using SafeERC20 for IERC20;
    using Address for address;
    using SafeMath for uint256;

    address public constant want = address(
        0x194eBd173F6cDacE046C53eACcE9B953F28411d1
    );
    address public constant crv = address(
        0xD533a949740bb3306d119CC777fa900bA034cd52
    );
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
    address public constant snx = address(
        0xC011a73ee8576Fb46F5E1c5751cA3B9Fe0af2a6F
    );
    address public constant curve = address(
        0x0Ce6a5fF5217e38315f87032CF90686C96627CAA
    );

    address public constant gauge = address(
        0x90Bb609649E0451E5aD952683D64BD2d1f245840
    );
    //address public constant voter = address(0xF147b8125d2ef93FB6965Db97D6746952a133934);
    address public constant voter = address(
        0x52f541764E6e90eeBc5c21Ff570De0e2D63766B6
    );

    uint256 public keepCRV = 2000;
    uint256 public performanceFee = 1500;
    uint256 public withdrawalFee = 50;
    uint256 public constant FEE_DENOMINATOR = 10000;

    address public proxy;

    address public governance;
    address public controller;
    address public strategist;

    uint256 public earned; // lifetime strategy earnings denominated in `want` token

    event Harvested(uint256 wantEarned, uint256 lifetimeEarned);

    constructor(address _controller) public {
        governance = msg.sender;
        strategist = msg.sender;
        controller = _controller;
    }

    function getName() external pure returns (string memory) {
        return "StrategyCurveEursCrvVoterProxy";
    }

    function setStrategist(address _strategist) external {
        require(
            msg.sender == governance || msg.sender == strategist,
            "!authorized"
        );
        strategist = _strategist;
    }

    function setKeepCRV(uint256 _keepCRV) external {
        require(msg.sender == governance, "!governance");
        keepCRV = _keepCRV;
    }

    function setWithdrawalFee(uint256 _withdrawalFee) external {
        require(msg.sender == governance, "!governance");
        withdrawalFee = _withdrawalFee;
    }

    function setPerformanceFee(uint256 _performanceFee) external {
        require(msg.sender == governance, "!governance");
        performanceFee = _performanceFee;
    }

    function setProxy(address _proxy) external {
        require(msg.sender == governance, "!governance");
        proxy = _proxy;
    }

    function deposit() public {
        uint256 _want = IERC20(want).balanceOf(address(this));
        if (_want > 0) {
            IERC20(want).safeTransfer(proxy, _want);
            IVoterProxy(proxy).deposit(gauge, want);
        }
    }

    // Controller only function for creating additional rewards from dust
    function withdraw(IERC20 _asset) external returns (uint256 balance) {
        require(msg.sender == controller, "!controller");
        require(want != address(_asset), "want");
        require(crv != address(_asset), "crv");
        require(eurs != address(_asset), "eurs");
        require(snx != address(_asset), "snx");
        balance = _asset.balanceOf(address(this));
        _asset.safeTransfer(controller, balance);
    }

    // Withdraw partial funds, normally used with a vault withdrawal
    function withdraw(uint256 _amount) external {
        require(msg.sender == controller, "!controller");
        uint256 _balance = IERC20(want).balanceOf(address(this));
        if (_balance < _amount) {
            _amount = _withdrawSome(_amount.sub(_balance));
            _amount = _amount.add(_balance);
        }

        uint256 _fee = _amount.mul(withdrawalFee).div(FEE_DENOMINATOR);

        IERC20(want).safeTransfer(IController(controller).rewards(), _fee);
        address _vault = IController(controller).vaults(address(want));
        require(_vault != address(0), "!vault"); // additional protection so we don't burn the funds
        IERC20(want).safeTransfer(_vault, _amount.sub(_fee));
    }

    function _withdrawSome(uint256 _amount) internal returns (uint256) {
        return IVoterProxy(proxy).withdraw(gauge, want, _amount);
    }

    function withdrawToVault(uint256 amount) external {
        require(msg.sender == governance, "!governance");
        amount = _withdrawSome(amount);

        address _vault = IController(controller).vaults(address(want));
        require(_vault != address(0), "!vault"); // additional protection so we don't burn the funds

        IERC20(want).safeTransfer(_vault, amount);
    }

    // Withdraw all funds, normally used when migrating strategies
    function withdrawAll() external returns (uint256 balance) {
        require(msg.sender == controller, "!controller");
        _withdrawAll();

        balance = IERC20(want).balanceOf(address(this));

        address _vault = IController(controller).vaults(address(want));
        require(_vault != address(0), "!vault"); // additional protection so we don't burn the funds
        IERC20(want).safeTransfer(_vault, balance);
    }

    function _withdrawAll() internal {
        IVoterProxy(proxy).withdrawAll(gauge, want);
    }

    function harvest() public {
        require(
            msg.sender == strategist || msg.sender == governance,
            "!authorized"
        );
        IVoterProxy(proxy).harvest(gauge, true);

        //Swap some fraction of CRV for EURS
        uint256 _crv = IERC20(crv).balanceOf(address(this));
        if (_crv > 0) {
            uint256 _keepCRV = _crv.mul(keepCRV).div(FEE_DENOMINATOR);
            IERC20(crv).safeTransfer(voter, _keepCRV);
            _crv = _crv.sub(_keepCRV);

            IERC20(crv).safeApprove(uni, 0);
            IERC20(crv).safeApprove(uni, _crv);

            address[] memory path = new address[](4);
            path[0] = crv;
            path[1] = weth;
            path[2] = usdc;
            path[3] = eurs;

            Uni(uni).swapExactTokensForTokens(
                _crv,
                uint256(0),
                path,
                address(this),
                now.add(1800)
            );
        }

        // Swap SNX for EURS
        uint256 _snx = IERC20(snx).balanceOf(address(this));
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
        if (_want > 0) {
            uint256 _fee = _want.mul(performanceFee).div(FEE_DENOMINATOR);
            IERC20(want).safeTransfer(IController(controller).rewards(), _fee);
            deposit();
        }
        IVoterProxy(proxy).lock();
        earned = earned.add(_want);
        emit Harvested(_want, earned);
    }

    function balanceOfWant() public view returns (uint256) {
        return IERC20(want).balanceOf(address(this));
    }

    function balanceOfPool() public view returns (uint256) {
        return IVoterProxy(proxy).balanceOf(gauge);
    }

    function balanceOf() public view returns (uint256) {
        return balanceOfWant().add(balanceOfPool());
    }

    function setGovernance(address _governance) external {
        require(msg.sender == governance, "!governance");
        governance = _governance;
    }

    function setController(address _controller) external {
        require(msg.sender == governance, "!governance");
        controller = _controller;
    }
}
