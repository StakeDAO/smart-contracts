// SPDX-License-Identifier: MIT
pragma solidity 0.8.2;

import "../BaseStrategy.sol";
import "../interfaces/IAngle.sol";
import "../interfaces/IMultiRewards.sol";

import "hardhat/console.sol";

contract StrategyAngleStakeDao is BaseStrategy {
	address public stableMaster = 0x5adDc89785D75C86aB939E9e15bfBBb7Fc086A87;
	address public poolManager = 0xe9f183FC656656f1F17af1F2b0dF79b8fF9ad8eD;
	address public staking = 0x2Fa1255383364F6e17Be6A6aC7A56C9aCD6850a3;
	address public sanUSDC_EUR = 0x9C215206Da4bf108aE5aEEf9dA7caD3352A36Dad;
	address public angle = 0x31429d1856aD1377A8A0079410B297e1a9e214c2;
	address public gauge;

	constructor(
		address _controller,
		address _want,
		address _gauge
	) BaseStrategy(_controller, _want) {
		gauge = _gauge;
		IERC20(angle).approve(_gauge, type(uint256).max);
		IERC20(want).approve(stableMaster, type(uint256).max);
		IERC20(sanUSDC_EUR).approve(staking, type(uint256).max);
	}

	function name() external pure override returns (string memory) {
		return "StrategyAngleStakeDao";
	}

	function deposit() public override {
		// usdc => sanUSDC_EUR
		uint256 wantBalance = IERC20(want).balanceOf(address(this));
		IStableMaster(stableMaster).deposit(wantBalance, address(this), IPoolManager(poolManager));
		uint256 sanUsdcEurBalance = IERC20(sanUSDC_EUR).balanceOf(address(this));
		IERC20(sanUSDC_EUR).transfer(IController(controller).vaults(want), sanUsdcEurBalance);
	}

	function withdraw(uint256 _amount) external override onlyController {
		// Withdraw san LP from angle yield staking pool
		IStakingRewards(staking).withdraw(_amount);
		uint256 sanLPObtained = IERC20(sanUSDC_EUR).balanceOf(address(this));
		// burn san LP to obtain USDC
		IStableMaster(stableMaster).withdraw(sanLPObtained, address(this), address(this), IPoolManager(poolManager));

		address _vault = IController(controller).vaults(address(want));
		require(_vault != address(0), "!vault"); // additional protection so we don't burn the funds

		uint256 usdcAmount = IERC20(want).balanceOf(address(this));
		IERC20(want).transfer(_vault, usdcAmount);
	}

	function _withdrawSome(uint256 _amount) internal override {
		IStakingRewards(staking).withdraw(_amount);
	}

	function withdrawAll() external override onlyController returns (uint256) {
		uint256 stakedBalance = balanceOfPool();
		_withdrawSome(stakedBalance);
		uint256 sanLPObtained = IERC20(sanUSDC_EUR).balanceOf(address(this));
		IERC20(sanUSDC_EUR).transfer(IController(controller).vaults(want), sanLPObtained); // send funds to vault
		IERC20(sanUSDC_EUR).approve(staking, 0);
		return sanLPObtained;
	}

	function harvest() public onlyAdmin {
		// claim angle from angle
		// send to multi rewards
		IStakingRewards(staking).getReward();
		uint256 angleBalance = IERC20(angle).balanceOf(address(this));
		if (angleBalance > 0) {
			uint256 _fee = (angleBalance * performanceFee) / FEE_DENOMINATOR;
			IERC20(angle).transfer(IController(controller).rewards(), _fee);
			uint256 angleLeft = IERC20(angle).balanceOf(address(this));
			IMultiRewards(gauge).notifyRewardAmount(angle, angleLeft);
		}
	}

	function stake() public {
		uint256 sanUSDC_EURBalance = IERC20(sanUSDC_EUR).balanceOf(address(this));
		IStakingRewards(staking).stake(sanUSDC_EURBalance);
	}

	function balanceOfPool() public view override returns (uint256) {
		return IStakingRewards(staking).balanceOf(address(this));
	}

	function setGauge(address _newGauge) external onlyAdmin {
		IERC20(angle).approve(gauge, 0);
		gauge = _newGauge;
		IERC20(angle).approve(_newGauge, type(uint256).max);
	}

	function setStaking(address _newStaking) external onlyAdmin {
		uint256 stakedBalance = balanceOfPool();
		// withdraw all from the old staking contract
		_withdrawSome(stakedBalance);
		// sett new staking contract
		staking = _newStaking;
		IERC20(sanUSDC_EUR).approve(_newStaking, type(uint256).max);
		// stake all into the new contract
		stake();
	}

	function setPoolManager(address _newPoolManager) external onlyAdmin {
		poolManager = _newPoolManager;
	}

	function refreshApproves() external onlyAdmin {
		IERC20(angle).approve(gauge, type(uint256).max);
		IERC20(want).approve(stableMaster, type(uint256).max);
		IERC20(sanUSDC_EUR).approve(staking, type(uint256).max);
	}
}
