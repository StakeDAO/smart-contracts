// SPDX-License-Identifier: MIT

pragma solidity ^0.5.17;

import "@openzeppelinV2/contracts/token/ERC20/IERC20.sol";
import "@openzeppelinV2/contracts/math/SafeMath.sol";
import "@openzeppelinV2/contracts/utils/Address.sol";
import "@openzeppelinV2/contracts/token/ERC20/SafeERC20.sol";

import "../../interfaces/yearn/IProxy.sol";
import "../../interfaces/curve/Mintr.sol";
import "../../interfaces/curve/FeeDistribution.sol";

contract StrategyProxy {
    using SafeERC20 for IERC20;
    using Address for address;
    using SafeMath for uint256;

    //IProxy public constant proxy = IProxy(0xF147b8125d2ef93FB6965Db97D6746952a133934);
    IProxy public proxy = IProxy(0x52f541764E6e90eeBc5c21Ff570De0e2D63766B6);
    address public mintr = address(0xd061D61a4d941c39E5453435B6345Dc261C2fcE0);
    address public constant crv =
        address(0xD533a949740bb3306d119CC777fa900bA034cd52);
    address public constant snx =
        address(0xC011a73ee8576Fb46F5E1c5751cA3B9Fe0af2a6F);
    address public gauge = address(0x2F50D538606Fa9EDD2B11E2446BEb18C9D5846bB);
    address public y = address(0xFA712EE4788C042e2B7BB55E6cb8ec569C4530c1);
    address public sdveCRV;
    address public CRV3 = address(0x6c3F90f043a72FA612cbac8115EE7e52BDe6E490);
    FeeDistribution public feeDistribution =
        FeeDistribution(0xA464e6DCda8AC41e03616F95f4BC98a13b8922Dc);

    mapping(address => bool) public strategies;
    address public governance;

    // to save gas
    modifier onlyGovernance() {
        require(msg.sender == governance, "!governance");
        _;
    }

    constructor(address _sdveCRV) public {
        governance = msg.sender;
        sdveCRV = _sdveCRV;
    }

    function setGovernance(address _governance) external onlyGovernance {
        governance = _governance;
    }

    function setProxy(IProxy _proxy) external onlyGovernance {
        proxy = _proxy;
    }

    function setMintr(address _mintr) external onlyGovernance {
        mintr = _mintr;
    }

    function setGauge(address _gauge) external onlyGovernance {
        gauge = _gauge;
    }

    function setY(address _y) external onlyGovernance {
        y = _y;
    }

    function setSdveCRV(address _sdveCRV) external onlyGovernance {
        sdveCRV = _sdveCRV;
    }

    function setCRV3(address _CRV3) external onlyGovernance {
        CRV3 = _CRV3;
    }

    function setFeeDistribution(FeeDistribution _feeDistribution)
        external
        onlyGovernance
    {
        feeDistribution = _feeDistribution;
    }

    function approveStrategy(address _strategy) external onlyGovernance {
        strategies[_strategy] = true;
    }

    function revokeStrategy(address _strategy) external onlyGovernance {
        strategies[_strategy] = false;
    }

    function lock() external {
        uint256 amount = IERC20(crv).balanceOf(address(proxy));
        if (amount > 0) proxy.increaseAmount(amount); //
    }

    function vote(address _gauge, uint256 _amount) public {
        require(strategies[msg.sender], "!strategy");
        proxy.execute(
            gauge,
            0,
            abi.encodeWithSignature(
                "vote_for_gauge_weights(address,uint256)",
                _gauge,
                _amount
            )
        );
    }

    function withdraw(
        address _gauge,
        address _token,
        uint256 _amount
    ) public returns (uint256) {
        require(strategies[msg.sender], "!strategy");
        uint256 _before = IERC20(_token).balanceOf(address(proxy));
        uint256 _beforeSnx = IERC20(snx).balanceOf(address(proxy));
        proxy.execute(
            _gauge,
            0,
            abi.encodeWithSignature("withdraw(uint256)", _amount)
        );
        uint256 _after = IERC20(_token).balanceOf(address(proxy));
        uint256 _afterSnx = IERC20(snx).balanceOf(address(proxy));
        uint256 _net = _after.sub(_before);
        proxy.execute(
            _token,
            0,
            abi.encodeWithSignature(
                "transfer(address,uint256)",
                msg.sender,
                _net
            )
        );
        uint256 _snx = _afterSnx.sub(_beforeSnx);
        if (_snx > 0) {
            proxy.execute(
                snx,
                0,
                abi.encodeWithSignature(
                    "transfer(address,uint256)",
                    msg.sender,
                    _snx
                )
            );
        }
        return _net;
    }

    function balanceOf(address _gauge) public view returns (uint256) {
        return IERC20(_gauge).balanceOf(address(proxy));
    }

    // withdraw all
    function withdrawAll(address _gauge, address _token)
        external
        returns (uint256)
    {
        require(strategies[msg.sender], "!strategy");
        return withdraw(_gauge, _token, balanceOf(_gauge));
    }

    function deposit(address _gauge, address _token) external {
        require(strategies[msg.sender], "!strategy");
        uint256 _balance = IERC20(_token).balanceOf(address(this));
        IERC20(_token).safeTransfer(address(proxy), _balance);
        _balance = IERC20(_token).balanceOf(address(proxy));

        proxy.execute(
            _token,
            0,
            abi.encodeWithSignature("approve(address,uint256)", _gauge, 0)
        );
        proxy.execute(
            _token,
            0,
            abi.encodeWithSignature(
                "approve(address,uint256)",
                _gauge,
                _balance
            )
        );
        uint256 _before = IERC20(snx).balanceOf(address(proxy));

        (bool success, ) = proxy.execute(
            _gauge,
            0,
            abi.encodeWithSignature("deposit(uint256)", _balance)
        );
        if (!success) assert(false);

        uint256 _after = IERC20(snx).balanceOf(address(proxy));
        _balance = _after.sub(_before);
        if (_balance > 0) {
            proxy.execute(
                snx,
                0,
                abi.encodeWithSignature(
                    "transfer(address,uint256)",
                    msg.sender,
                    _balance
                )
            );
        }
    }

    function harvest(address _gauge, bool _snxRewards) external {
        require(strategies[msg.sender], "!strategy");
        uint256 _before = IERC20(crv).balanceOf(address(proxy));
        proxy.execute(
            mintr,
            0,
            abi.encodeWithSignature("mint(address)", _gauge)
        );
        uint256 _after = IERC20(crv).balanceOf(address(proxy));
        uint256 _balance = _after.sub(_before);
        proxy.execute(
            crv,
            0,
            abi.encodeWithSignature(
                "transfer(address,uint256)",
                msg.sender,
                _balance
            )
        );
        if (_snxRewards) {
            _before = IERC20(snx).balanceOf(address(proxy));
            proxy.execute(
                _gauge,
                0,
                abi.encodeWithSignature("claim_rewards()")
            );
            _after = IERC20(snx).balanceOf(address(proxy));
            _balance = _after.sub(_before);
            if (_balance > 0) {
                proxy.execute(
                    snx,
                    0,
                    abi.encodeWithSignature(
                        "transfer(address,uint256)",
                        msg.sender,
                        _balance
                    )
                );
            }
        }
    }

    function claim(address recipient) external {
        require(msg.sender == sdveCRV, "!strategy");
        uint256 amount = feeDistribution.claim(address(proxy));
        if (amount > 0) {
            proxy.execute(
                CRV3,
                0,
                abi.encodeWithSignature(
                    "transfer(address,uint256)",
                    recipient,
                    amount
                )
            );
        }
    }

    function ifTokenGetStuckInProxy(address asset, address recipient)
        external
        onlyGovernance
        returns (uint256 balance)
    {
        require(asset != address(0), "invalid asset");
        require(recipient != address(0), "invalid recipient");
        balance = proxy.withdraw(IERC20(asset));
        if (balance > 0) {
            IERC20(asset).safeTransfer(recipient, balance);
        }
    }

    // lets see
    function ifTokenGetStuck(address asset, address recipient)
        external
        onlyGovernance
        returns (uint256 balance)
    {
        require(asset != address(0), "invalid asset");
        require(recipient != address(0), "invalid recipient");
        balance = IERC20(asset).balanceOf(address(this));
        if (balance > 0) {
            IERC20(asset).safeTransfer(recipient, balance);
        }
    }
}
