// SPDX-License-Identifier: MIT
pragma solidity 0.6.12;

interface IMultiRewards {
	function balanceOf(address) external returns (uint256);

	function stakeFor(address, uint256) external;

	function withdrawFor(address, uint256) external;

	function notifyRewardAmount(address, uint256) external;

	function getRewardFor(address) external;
}
