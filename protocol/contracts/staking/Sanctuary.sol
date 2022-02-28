//SPDX-License-Identifier: UNLICENSED

pragma solidity ^0.6.0;

import "../temp/openzeppelin/IERC20.sol";
import "../temp/openzeppelin/Context.sol";
import "../temp/openzeppelin/SafeMath.sol";
import "../temp/openzeppelin/Address.sol";
import "../temp/openzeppelin/ERC20.sol";
import "../temp/openzeppelin/Ownable.sol";

contract Sanctuary is ERC20("Staked SDT", "xSDT"), Ownable {
    using SafeMath for uint256;
    IERC20 public sdt;
    address public rewardDistribution;

    event Stake(address indexed staker, uint256 xsdtReceived);
    event Unstake(address indexed unstaker, uint256 sdtReceived);
    event RewardDistributorSet(address indexed newRewardDistributor);
    event SdtFeeReceived(address indexed from, uint256 sdtAmount);

    modifier onlyRewardDistribution() {
        require(
            _msgSender() == rewardDistribution,
            "Caller is not reward distribution"
        );
        _;
    }

    constructor(IERC20 _sdt) public {
        sdt = _sdt;
    }

    // Enter the Sanctuary. Pay some SDTs. Earn some shares.
    function enter(uint256 _amount) public {
        uint256 totalSdt = sdt.balanceOf(address(this));
        uint256 totalShares = totalSupply();
        if (totalShares == 0 || totalSdt == 0) {
            _mint(_msgSender(), _amount);
            emit Stake(_msgSender(), _amount);
        } else {
            uint256 what = _amount.mul(totalShares).div(totalSdt);
            _mint(_msgSender(), what);
            emit Stake(_msgSender(), what);
        }
        sdt.transferFrom(_msgSender(), address(this), _amount);
    }

    // Leave the Sanctuary. Claim back your SDTs.
    function leave(uint256 _share) public {
        uint256 totalShares = totalSupply();
        uint256 what =
            _share.mul(sdt.balanceOf(address(this))).div(totalShares);
        _burn(_msgSender(), _share);
        sdt.transfer(_msgSender(), what);
        emit Unstake(_msgSender(), what);
    }

    function setRewardDistribution(address _rewardDistribution)
        external
        onlyOwner
    {
        rewardDistribution = _rewardDistribution;
        emit RewardDistributorSet(_rewardDistribution);
    }

    function notifyRewardAmount(uint256 _balance)
        external
        onlyRewardDistribution
    {
        sdt.transferFrom(_msgSender(), address(this), _balance);
        emit SdtFeeReceived(_msgSender(), _balance);
    }
}
