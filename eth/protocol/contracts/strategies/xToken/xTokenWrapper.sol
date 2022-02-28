// SPDX-License-Identifier: MIT

pragma solidity ^0.6.0;

import "../../temp/openzeppelin/ERC20.sol";
import "../../temp/openzeppelin/SafeMath.sol";

interface IxAAVEa {
    /*
     * @dev Mint xAAVE using AAVE
     * @notice Must run ERC20 approval first
     * @param aaveAmount: AAVE to contribute
     * @param affiliate: optional recipient of 25% of fees
     */
    function mintWithToken(uint256 aaveAmount, address affiliate) external;

    /*
     * @dev Burn xAAVE tokens
     * @notice Will fail if redemption value exceeds available liquidity
     * @param redeemAmount: xAAVE to redeem
     * @param redeemForEth: if true, redeem xAAVE for ETH
     * @param minRate: Kyber.getExpectedRate AAVE=>ETH if redeemForEth true (no-op if false)
     */
    function burn(
        uint256 tokenAmount,
        bool redeemForEth,
        uint256 minRate
    ) external;

    function getFundHoldings() external view returns (uint256);

    function totalSupply() external view returns (uint256);

    function balanceOf(address) external view returns (uint256);

    function transfer(address recipient, uint256 amount)
        external
        returns (bool);
}

contract xTokenWrapper is ERC20("Stake Dao xAAVEa", "sdxAAVEa") {
    using SafeMath for uint256;

    address public constant aave = 0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9;
    address public xAAVEa = 0x80DC468671316E50D4E9023D3db38D3105c1C146;
    address public governance;

    constructor(address _governance) public {
        governance = _governance;
    }

    modifier onlyGovernance() {
        require(msg.sender == governance);
        _;
    }

    function setxAAVEa(address _xAAVEa) external onlyGovernance {
        xAAVEa = _xAAVEa;
    }

    function setGovernance(address _governance) external onlyGovernance {
        governance = _governance;
    }

    function rescue(uint256 amount) external onlyGovernance {
        IERC20(aave).transfer(governance, amount);
    }

    function mintWithToken(uint256 aaveAmount) external {
        require(aaveAmount > 0, "invalid aaveAmount");
        IERC20(aave).transferFrom(msg.sender, address(this), aaveAmount);

        uint256 _balBefore = IxAAVEa(xAAVEa).balanceOf(address(this));
        IERC20(aave).approve(xAAVEa, aaveAmount);
        IxAAVEa(xAAVEa).mintWithToken(aaveAmount, governance);
        uint256 _balAfter = IxAAVEa(xAAVEa).balanceOf(address(this));

        super._mint(msg.sender, _balAfter.sub(_balBefore));
    }

    function burn(
        uint256 tokenAmount,
        bool redeemForEth,
        uint256 minRate
    ) external {
        require(tokenAmount > 0, "invalid tokenAmount");

        uint256 _xAaveBalBefore;
        uint256 _xAaveBalAfter;
        uint256 _ethBefore;
        uint256 _ethAfter;

        if (redeemForEth) {
            _ethBefore = address(this).balance;
            _xAaveBalBefore = IxAAVEa(xAAVEa).balanceOf(address(this));
            IxAAVEa(xAAVEa).burn(tokenAmount, redeemForEth, minRate);
            _xAaveBalAfter = IxAAVEa(xAAVEa).balanceOf(address(this));
            _ethAfter = address(this).balance;
            (bool success, ) =
                msg.sender.call{value: _ethAfter.sub(_ethBefore)}("");
            require(success, "Eth transfer failed");
        } else {
            _xAaveBalBefore = IxAAVEa(xAAVEa).balanceOf(address(this));
            uint256 _aaveBalBefore = IERC20(aave).balanceOf(address(this));
            IxAAVEa(xAAVEa).burn(tokenAmount, redeemForEth, minRate);
            _xAaveBalAfter = IxAAVEa(xAAVEa).balanceOf(address(this));
            uint256 _aaveBalAfter = IERC20(aave).balanceOf(address(this));

            IERC20(aave).transfer(
                msg.sender,
                _aaveBalAfter.sub(_aaveBalBefore)
            );
        }

        super._burn(msg.sender, _xAaveBalBefore.sub(_xAaveBalAfter));
    }

    function redeemsdxAAVEeaForxAAVEa(uint256 sdxAaveaAmount) external {
        require(sdxAaveaAmount > 0, "invalid sdxAaveaAmount");
        super._burn(msg.sender, sdxAaveaAmount);
        IxAAVEa(xAAVEa).transfer(msg.sender, sdxAaveaAmount);
    }

    function execute(
        address to,
        uint256 value,
        bytes calldata data
    ) external returns (bool, bytes memory) {
        require(msg.sender == governance, "!governance");
        (bool success, bytes memory result) = to.call{value: value}(data);
        return (success, result);
    }

    function pricePerFullShare() external view returns (uint256) {
        return IxAAVEa(xAAVEa).getFundHoldings().div(IxAAVEa(xAAVEa).totalSupply());
    }

    receive() external payable {}
}
