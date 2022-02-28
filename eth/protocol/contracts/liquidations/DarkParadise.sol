//SPDX-License-Identifier: UNLICENSED

pragma solidity ^0.6.0;

import "../temp/openzeppelin/IERC20.sol";
import "../temp/openzeppelin/Context.sol";
import "../temp/openzeppelin/SafeMath.sol";
import "../temp/openzeppelin/Address.sol";
import "../temp/openzeppelin/ERC20.sol";
import "../temp/openzeppelin/Ownable.sol";

abstract contract IStratAccessNft {
    function getTotalUseCount(address _account, uint256 _id)
        public
        view
        virtual
        returns (uint256);

    function getStratUseCount(
        address _account,
        uint256 _id,
        address _strategy
    ) public view virtual returns (uint256);

    function startUsingNFT(address _account, uint256 _id) public virtual;

    function endUsingNFT(address _account, uint256 _id) public virtual;
}

contract DarkParadise is ERC20("Liquidation SDT", "liqSDT"), Ownable {
    using SafeMath for uint256;
    IERC20 public sdt;
    address public rewardDistribution;
    IStratAccessNft public nft;

    // common, rare, unique ids considered in range on 1-111
    uint256 public constant rareMinId = 101;
    uint256 public constant uniqueId = 111;

    uint256 public minNFTId = 223;
    uint256 public maxNFTId = 444;

    uint256 public commonLimit = 300 * 10**18;
    uint256 public rareLimit = 1500 * 10**18;
    uint256 public uniqueLimit = 5000 * 10**18;

    mapping(address => uint256) public usedNFT;

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

    constructor(IERC20 _sdt, IStratAccessNft _nft) public {
        sdt = _sdt;
        nft = _nft;
    }

    function getLimit(address user) public view returns (uint256) {
        uint256 nftId = usedNFT[user];
        if (nftId == 0) return 0;

        uint256 effectiveId = ((nftId - 1) % 111) + 1;
        if (effectiveId < rareMinId) return commonLimit;
        if (effectiveId < uniqueId) return rareLimit;
        return uniqueLimit;
    }

    function enter(uint256 _amount, uint256 _nftId) public {
        address sender = _msgSender();

        if (usedNFT[sender] == 0) {
            require(_nftId >= minNFTId && _nftId <= maxNFTId, "Invalid nft");
            usedNFT[sender] = _nftId;
            nft.startUsingNFT(sender, _nftId);
        }

        uint256 totalSdt = sdt.balanceOf(address(this));
        uint256 totalShares = totalSupply();
        if (totalShares == 0 || totalSdt == 0) {
            require(_amount <= getLimit(sender), "Limit hit");
            _mint(sender, _amount);
            emit Stake(sender, _amount);
        } else {
            uint256 effectiveSdtBal =
                balanceOf(sender).mul(totalSdt).div(totalShares);
            require(
                effectiveSdtBal.add(_amount) <= getLimit(sender),
                "Limit hit"
            );
            uint256 sharesToMint = _amount.mul(totalShares).div(totalSdt);
            _mint(sender, sharesToMint);
            emit Stake(sender, sharesToMint);
        }
        sdt.transferFrom(sender, address(this), _amount);
    }

    function leave(uint256 _share) public {
        address sender = _msgSender();
        uint256 totalShares = totalSupply();
        uint256 what =
            _share.mul(sdt.balanceOf(address(this))).div(totalShares);
        _burn(sender, _share);
        sdt.transfer(sender, what);

        if (balanceOf(sender) == 0) {
            uint256 nftId = usedNFT[sender];
            usedNFT[sender] = 0;
            nft.endUsingNFT(sender, nftId);
        }

        emit Unstake(sender, what);
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

    function setNFT(IStratAccessNft _nft) public onlyOwner {
        nft = _nft;
    }

    function setMinMaxNFT(uint256 _min, uint256 _max) external onlyOwner {
        if (minNFTId != _min) minNFTId = _min;
        if (maxNFTId != _max) maxNFTId = _max;
    }

    function setDepositLimits(
        uint256 _common,
        uint256 _rare,
        uint256 _unique
    ) external onlyOwner {
        if (commonLimit != _common) commonLimit = _common;
        if (rareLimit != _rare) rareLimit = _rare;
        if (uniqueLimit != _unique) uniqueLimit = _unique;
    }

    function transfer(address, uint256) public override returns (bool) {
        revert("Restricted");
    }

    function transferFrom(
        address,
        address,
        uint256
    ) public override returns (bool) {
        revert("Restricted");
    }
}
