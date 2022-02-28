// SPDX-License-Identifier: MIT
pragma solidity 0.6.12;
pragma experimental ABIEncoderV2;

import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import "@openzeppelin/contracts/utils/Pausable.sol";
import "@openzeppelin/contracts/math/SafeMath.sol";
import "@openzeppelin/contracts/math/Math.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/SafeERC20.sol";

contract MultiRewards is ReentrancyGuard, Pausable, Ownable {
	using SafeMath for uint256;
	using SafeERC20 for IERC20;

	/* ========== STATE VARIABLES ========== */

	struct Reward {
		address rewardsDistributor;
		uint256 rewardsDuration;
		uint256 periodFinish;
		uint256 rewardRate;
		uint256 lastUpdateTime;
		uint256 rewardPerTokenStored;
	}
	IERC20 public stakingToken;
	mapping(address => Reward) public rewardData;
	address[] public rewardTokens;

	// user -> reward token -> amount
	mapping(address => mapping(address => uint256)) public userRewardPerTokenPaid;
	mapping(address => mapping(address => uint256)) public rewards;

	uint256 private _totalSupply;
	mapping(address => uint256) private _balances;

	/* ========== CONSTRUCTOR ========== */

	constructor(address _stakingToken) public {
		stakingToken = IERC20(_stakingToken);
	}

	function addReward(
		address _rewardsToken,
		address _rewardsDistributor,
		uint256 _rewardsDuration
	) public onlyOwner {
		require(rewardData[_rewardsToken].rewardsDuration == 0);
		rewardTokens.push(_rewardsToken);
		rewardData[_rewardsToken].rewardsDistributor = _rewardsDistributor;
		rewardData[_rewardsToken].rewardsDuration = _rewardsDuration;
	}

	/* ========== VIEWS ========== */

	function totalSupply() external view returns (uint256) {
		return _totalSupply;
	}

	function balanceOf(address account) external view returns (uint256) {
		return _balances[account];
	}

	function lastTimeRewardApplicable(address _rewardsToken)
		public
		view
		returns (uint256)
	{
		return Math.min(block.timestamp, rewardData[_rewardsToken].periodFinish);
	}

	function rewardPerToken(address _rewardsToken) public view returns (uint256) {
		if (_totalSupply == 0) {
			return rewardData[_rewardsToken].rewardPerTokenStored;
		}
		return
			rewardData[_rewardsToken].rewardPerTokenStored.add(
				lastTimeRewardApplicable(_rewardsToken)
					.sub(rewardData[_rewardsToken].lastUpdateTime)
					.mul(rewardData[_rewardsToken].rewardRate)
					.mul(1e18)
					.div(_totalSupply)
			);
	}

	function earned(address account, address _rewardsToken)
		public
		view
		returns (uint256)
	{
		return
			_balances[account]
				.mul(
					rewardPerToken(_rewardsToken).sub(
						userRewardPerTokenPaid[account][_rewardsToken]
					)
				)
				.div(1e18)
				.add(rewards[account][_rewardsToken]);
	}

	function getRewardForDuration(address _rewardsToken)
		external
		view
		returns (uint256)
	{
		return
			rewardData[_rewardsToken].rewardRate.mul(
				rewardData[_rewardsToken].rewardsDuration
			);
	}

	/* ========== MUTATIVE FUNCTIONS ========== */

	function setRewardsDistributor(
		address _rewardsToken,
		address _rewardsDistributor
	) external onlyOwner {
		rewardData[_rewardsToken].rewardsDistributor = _rewardsDistributor;
	}

	function _stake(uint256 amount, address account)
		internal
		nonReentrant
		whenNotPaused
		updateReward(account)
	{
		require(amount > 0, "Cannot stake 0");
		_totalSupply = _totalSupply.add(amount);
		_balances[account] = _balances[account].add(amount);
		stakingToken.safeTransferFrom(msg.sender, address(this), amount);
		emit Staked(account, amount);
	}

	function stakeFor(address account, uint256 amount) external {
		_stake(amount, account);
	}

	function _withdraw(uint256 amount, address account)
		internal
		nonReentrant
		updateReward(account)
	{
		require(amount > 0, "Cannot withdraw 0");
		_totalSupply = _totalSupply.sub(amount);
		_balances[account] = _balances[account].sub(amount);
		stakingToken.safeTransfer(msg.sender, amount);
		emit Withdrawn(account, amount);
	}

	function withdraw(uint256 amount, address account) external {
		_withdraw(amount, msg.sender);
	}

	function withdrawFor(address account, uint256 amount) external {
		require(tx.origin == account, "withdrawFor: account != tx.origin");
		_withdraw(amount, account);
	}

	function getReward() public nonReentrant updateReward(msg.sender) {
		for (uint256 i; i < rewardTokens.length; i++) {
			address _rewardsToken = rewardTokens[i];
			uint256 reward = rewards[msg.sender][_rewardsToken];
			if (reward > 0) {
				rewards[msg.sender][_rewardsToken] = 0;
				IERC20(_rewardsToken).safeTransfer(msg.sender, reward);
				emit RewardPaid(msg.sender, _rewardsToken, reward);
			}
		}
	}

	function getRewardFor(address account)
		public
		nonReentrant
		updateReward(account)
	{
		for (uint256 i; i < rewardTokens.length; i++) {
			address _rewardsToken = rewardTokens[i];
			uint256 reward = rewards[account][_rewardsToken];
			if (reward > 0) {
				rewards[account][_rewardsToken] = 0;
				IERC20(_rewardsToken).safeTransfer(account, reward);
				emit RewardPaid(account, _rewardsToken, reward);
			}
		}
	}

	function exit() external {
		_withdraw(_balances[msg.sender], msg.sender);
		getReward();
	}

	/* ========== RESTRICTED FUNCTIONS ========== */

	function notifyRewardAmount(address _rewardsToken, uint256 reward)
		external
		updateReward(address(0))
	{
		require(rewardData[_rewardsToken].rewardsDistributor == msg.sender);
		// handle the transfer of reward tokens via `transferFrom` to reduce the number
		// of transactions required and ensure correctness of the reward amount
		IERC20(_rewardsToken).safeTransferFrom(msg.sender, address(this), reward);

		if (block.timestamp >= rewardData[_rewardsToken].periodFinish) {
			rewardData[_rewardsToken].rewardRate = reward.div(
				rewardData[_rewardsToken].rewardsDuration
			);
		} else {
			uint256 remaining = rewardData[_rewardsToken].periodFinish.sub(
				block.timestamp
			);
			uint256 leftover = remaining.mul(rewardData[_rewardsToken].rewardRate);
			rewardData[_rewardsToken].rewardRate = reward.add(leftover).div(
				rewardData[_rewardsToken].rewardsDuration
			);
		}

		rewardData[_rewardsToken].lastUpdateTime = block.timestamp;
		rewardData[_rewardsToken].periodFinish = block.timestamp.add(
			rewardData[_rewardsToken].rewardsDuration
		);
		emit RewardAdded(reward);
	}

	// Added to support recovering LP Rewards from other systems such as BAL to be distributed to holders
	function recoverERC20(address tokenAddress, uint256 tokenAmount)
		external
		onlyOwner
	{
		require(
			tokenAddress != address(stakingToken),
			"Cannot withdraw staking token"
		);
		require(
			rewardData[tokenAddress].lastUpdateTime == 0,
			"Cannot withdraw reward token"
		);
		IERC20(tokenAddress).safeTransfer(owner(), tokenAmount);
		emit Recovered(tokenAddress, tokenAmount);
	}

	function setRewardsDuration(address _rewardsToken, uint256 _rewardsDuration)
		external
	{
		require(
			block.timestamp > rewardData[_rewardsToken].periodFinish,
			"Reward period still active"
		);
		require(rewardData[_rewardsToken].rewardsDistributor == msg.sender);
		require(_rewardsDuration > 0, "Reward duration must be non-zero");
		rewardData[_rewardsToken].rewardsDuration = _rewardsDuration;
		emit RewardsDurationUpdated(
			_rewardsToken,
			rewardData[_rewardsToken].rewardsDuration
		);
	}

	/* ========== MODIFIERS ========== */

	modifier updateReward(address account) {
		for (uint256 i; i < rewardTokens.length; i++) {
			address token = rewardTokens[i];
			rewardData[token].rewardPerTokenStored = rewardPerToken(token);
			rewardData[token].lastUpdateTime = lastTimeRewardApplicable(token);
			if (account != address(0)) {
				rewards[account][token] = earned(account, token);
				userRewardPerTokenPaid[account][token] = rewardData[token]
					.rewardPerTokenStored;
			}
		}
		_;
	}

	/* ========== EVENTS ========== */

	event RewardAdded(uint256 reward);
	event Staked(address indexed user, uint256 amount);
	event Withdrawn(address indexed user, uint256 amount);
	event RewardPaid(
		address indexed user,
		address indexed rewardsToken,
		uint256 reward
	);
	event RewardsDurationUpdated(address token, uint256 newDuration);
	event Recovered(address token, uint256 amount);
}
