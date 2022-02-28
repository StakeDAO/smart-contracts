/**
 *Submitted for verification at Etherscan.io on 2020-09-09
 */

// SPDX-License-Identifier: MIT
// File: @openzeppelin/contracts/token/ERC20/IERC20.sol

pragma solidity ^0.6.0;

import "../temp/openzeppelin/IERC20.sol";
import "../temp/openzeppelin/SafeMath.sol";
import "../temp/openzeppelin/Address.sol";
import "../temp/openzeppelin/SafeERC20.sol";
import "../temp/openzeppelin/EnumerableSet.sol";
import "../temp/openzeppelin/Context.sol";
import "../temp/openzeppelin/Ownable.sol";
import "../temp/openzeppelin/ERC20.sol";

// File: contracts/StakeDaoToken.sol

pragma solidity 0.6.12;

// StakeDaoToken with Governance.
contract StakeDaoToken is ERC20("Stake Dao Token", "SDT"), Ownable {
    /// @notice Creates `_amount` token to `_to`. Must only be called by the owner (MasterChef).
    function mint(address _to, uint256 _amount) public onlyOwner {
        _mint(_to, _amount);
    }
}

// File: contracts/curve/ICurveFiCurve.sol

pragma solidity ^0.6.12;

interface ICurveFiCurve {
    // All we care about is the ratio of each coin
    function balances(int128 arg0) external returns (uint256 out);
}

// File: contracts/MasterChef.sol

pragma solidity 0.6.12;

// MasterChef was the master of sdt. He now governs over SDT. He can make SDTs and he is a fair guy.
//
// Note that it's ownable and the owner wields tremendous power. The ownership
// will be transferred to a governance smart contract once SDTS is sufficiently
// distributed and the community can show to govern itself.
//
// Have fun reading it. Hopefully it's bug-free. God bless.
contract MasterChef is Ownable {
    using SafeMath for uint256;
    using SafeERC20 for IERC20;

    // Info of each user.
    struct UserInfo {
        uint256 amount; // How many LP tokens the user has provided.
        uint256 rewardDebt; // Reward debt. See explanation below.
        //
        // We do some fancy math here. Basically, any point in time, the amount of SDTs
        // entitled to a user but is pending to be distributed is:
        //
        //   pending reward = (user.amount * pool.accSdtPerShare) - user.rewardDebt
        //
        // Whenever a user deposits or withdraws LP tokens to a pool. Here's what happens:
        //   1. The pool's `accSdtPerShare` (and `lastRewardBlock`) gets updated.
        //   2. User receives the pending reward sent to his/her address.
        //   3. User's `amount` gets updated.
        //   4. User's `rewardDebt` gets updated.
    }

    // Info of each pool.
    struct PoolInfo {
        IERC20 lpToken; // Address of LP token contract.
        uint256 allocPoint; // How many allocation points assigned to this pool. SDTs to distribute per block.
        uint256 lastRewardBlock; // Last block number that SDTs distribution occurs.
        uint256 accSdtPerShare; // Accumulated SDTs per share, times 1e12. See below.
    }

    // The SDT TOKEN!
    StakeDaoToken public sdt;
    // Dev fund (2%, initially)
    uint256 public devFundDivRate = 50;
    // Dev address.
    address public devaddr;
    // Block number when bonus SDT period ends.
    uint256 public bonusEndBlock;
    // SDT tokens created per block.
    uint256 public sdtPerBlock;
    // Bonus muliplier for early sdt makers.
    uint256 public constant BONUS_MULTIPLIER = 2;

    // Info of each pool.
    PoolInfo[] public poolInfo;
    // Info of each user that stakes LP tokens.
    mapping(uint256 => mapping(address => UserInfo)) public userInfo;
    // Total allocation points. Must be the sum of all allocation points in all pools.
    uint256 public totalAllocPoint = 0;
    // The block number when SDT mining starts.
    uint256 public startBlock;

    // Events
    event Recovered(address token, uint256 amount);
    event Deposit(address indexed user, uint256 indexed pid, uint256 amount);
    event Withdraw(address indexed user, uint256 indexed pid, uint256 amount);
    event EmergencyWithdraw(
        address indexed user,
        uint256 indexed pid,
        uint256 amount
    );

    constructor(
        StakeDaoToken _sdt,
        address _devaddr,
        uint256 _sdtPerBlock,
        uint256 _startBlock,
        uint256 _bonusEndBlock
    ) public {
        sdt = _sdt;
        devaddr = _devaddr;
        sdtPerBlock = _sdtPerBlock;
        bonusEndBlock = _bonusEndBlock;
        startBlock = _startBlock;
    }

    function poolLength() external view returns (uint256) {
        return poolInfo.length;
    }

    // Add a new lp to the pool. Can only be called by the owner.
    // XXX DO NOT add the same LP token more than once. Rewards will be messed up if you do.
    function add(
        uint256 _allocPoint,
        IERC20 _lpToken,
        bool _withUpdate
    ) public onlyOwner {
        if (_withUpdate) {
            massUpdatePools();
        }
        uint256 lastRewardBlock =
            block.number > startBlock ? block.number : startBlock;
        totalAllocPoint = totalAllocPoint.add(_allocPoint);
        poolInfo.push(
            PoolInfo({
                lpToken: _lpToken,
                allocPoint: _allocPoint,
                lastRewardBlock: lastRewardBlock,
                accSdtPerShare: 0
            })
        );
    }

    // Update the given pool's SDT allocation point. Can only be called by the owner.
    function set(
        uint256 _pid,
        uint256 _allocPoint,
        bool _withUpdate
    ) public onlyOwner {
        if (_withUpdate) {
            massUpdatePools();
        }
        totalAllocPoint = totalAllocPoint.sub(poolInfo[_pid].allocPoint).add(
            _allocPoint
        );
        poolInfo[_pid].allocPoint = _allocPoint;
    }

    // Return reward multiplier over the given _from to _to block.
    function getMultiplier(uint256 _from, uint256 _to)
        public
        view
        returns (uint256)
    {
        if (_to <= bonusEndBlock) {
            return _to.sub(_from).mul(BONUS_MULTIPLIER);
        } else if (_from >= bonusEndBlock) {
            return _to.sub(_from);
        } else {
            return
                bonusEndBlock.sub(_from).mul(BONUS_MULTIPLIER).add(
                    _to.sub(bonusEndBlock)
                );
        }
    }

    // View function to see pending SDTs on frontend.
    function pendingSdt(uint256 _pid, address _user)
        external
        view
        returns (uint256)
    {
        PoolInfo storage pool = poolInfo[_pid];
        UserInfo storage user = userInfo[_pid][_user];
        uint256 accSdtPerShare = pool.accSdtPerShare;
        uint256 lpSupply = pool.lpToken.balanceOf(address(this));
        if (block.number > pool.lastRewardBlock && lpSupply != 0) {
            uint256 multiplier =
                getMultiplier(pool.lastRewardBlock, block.number);
            uint256 sdtReward =
                multiplier.mul(sdtPerBlock).mul(pool.allocPoint).div(
                    totalAllocPoint
                );
            accSdtPerShare = accSdtPerShare.add(
                sdtReward.mul(1e12).div(lpSupply)
            );
        }
        return user.amount.mul(accSdtPerShare).div(1e12).sub(user.rewardDebt);
    }

    // Update reward vairables for all pools. Be careful of gas spending!
    function massUpdatePools() public {
        uint256 length = poolInfo.length;
        for (uint256 pid = 0; pid < length; ++pid) {
            updatePool(pid);
        }
    }

    // Update reward variables of the given pool to be up-to-date.
    function updatePool(uint256 _pid) public {
        PoolInfo storage pool = poolInfo[_pid];
        if (block.number <= pool.lastRewardBlock) {
            return;
        }
        uint256 lpSupply = pool.lpToken.balanceOf(address(this));
        if (lpSupply == 0) {
            pool.lastRewardBlock = block.number;
            return;
        }
        uint256 multiplier = getMultiplier(pool.lastRewardBlock, block.number);
        uint256 sdtReward =
            multiplier.mul(sdtPerBlock).mul(pool.allocPoint).div(
                totalAllocPoint
            );
        // sdt.transfer(devaddr, sdtReward.div(devFundDivRate));
        sdt.transferFrom(devaddr, address(this), sdtReward);
        pool.accSdtPerShare = pool.accSdtPerShare.add(
            sdtReward.mul(1e12).div(lpSupply)
        );
        pool.lastRewardBlock = block.number;
    }

    // Deposit LP tokens to MasterChef for SDT allocation.
    function deposit(uint256 _pid, uint256 _amount) public {
        PoolInfo storage pool = poolInfo[_pid];
        UserInfo storage user = userInfo[_pid][msg.sender];
        updatePool(_pid);
        if (user.amount > 0) {
            uint256 pending =
                user.amount.mul(pool.accSdtPerShare).div(1e12).sub(
                    user.rewardDebt
                );
            safeSdtTransfer(msg.sender, pending);
        }
        pool.lpToken.safeTransferFrom(
            address(msg.sender),
            address(this),
            _amount
        );
        user.amount = user.amount.add(_amount);
        user.rewardDebt = user.amount.mul(pool.accSdtPerShare).div(1e12);
        emit Deposit(msg.sender, _pid, _amount);
    }

    // Withdraw LP tokens from MasterChef.
    function withdraw(uint256 _pid, uint256 _amount) public {
        PoolInfo storage pool = poolInfo[_pid];
        UserInfo storage user = userInfo[_pid][msg.sender];
        require(user.amount >= _amount, "withdraw: not good");
        updatePool(_pid);
        uint256 pending =
            user.amount.mul(pool.accSdtPerShare).div(1e12).sub(user.rewardDebt);
        safeSdtTransfer(msg.sender, pending);
        user.amount = user.amount.sub(_amount);
        user.rewardDebt = user.amount.mul(pool.accSdtPerShare).div(1e12);
        pool.lpToken.safeTransfer(address(msg.sender), _amount);
        emit Withdraw(msg.sender, _pid, _amount);
    }

    // Withdraw without caring about rewards. EMERGENCY ONLY.
    function emergencyWithdraw(uint256 _pid) public {
        PoolInfo storage pool = poolInfo[_pid];
        UserInfo storage user = userInfo[_pid][msg.sender];
        pool.lpToken.safeTransfer(address(msg.sender), user.amount);
        emit EmergencyWithdraw(msg.sender, _pid, user.amount);
        user.amount = 0;
        user.rewardDebt = 0;
    }

    // Safe sdt transfer function, just in case if rounding error causes pool to not have enough SDTs.
    function safeSdtTransfer(address _to, uint256 _amount) internal {
        uint256 sdtBal = sdt.balanceOf(address(this));
        if (_amount > sdtBal) {
            sdt.transfer(_to, sdtBal);
        } else {
            sdt.transfer(_to, _amount);
        }
    }

    // Update dev address by the owner.
    function setDevAddress(address _devaddr) public onlyOwner {
        devaddr = _devaddr;
    }

    // **** Additional functions separate from the original masterchef contract ****

    function setSdtPerBlock(uint256 _sdtPerBlock) public onlyOwner {
        require(_sdtPerBlock > 0, "!sdtPerBlock-0");

        sdtPerBlock = _sdtPerBlock;
    }

    function setBonusEndBlock(uint256 _bonusEndBlock) public onlyOwner {
        bonusEndBlock = _bonusEndBlock;
    }

    function setDevFundDivRate(uint256 _devFundDivRate) public onlyOwner {
        require(_devFundDivRate > 0, "!devFundDivRate-0");
        devFundDivRate = _devFundDivRate;
    }
}
