// SPDX-License-Identifier: MIT
pragma solidity 0.8.2;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/utils/Address.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

import "./interfaces/IStrategy.sol";

contract Controller {
	using SafeERC20 for IERC20;
	using Address for address;
	//using SafeMath for uint256;

	address public governance;
	address public strategist;

	address public rewards;
	mapping(address => address) public vaults;
	mapping(address => address) public strategies;

	mapping(address => mapping(address => bool)) public approvedStrategies;

	uint256 public constant max = 10000;

	event SetStrategy(address indexed asset, address indexed strategy);
	event ApproveStrategy(address indexed asset, address indexed strategy);
	event SetVault(address indexed asset, address indexed vault);

	constructor(address _rewards) {
		governance = msg.sender;
		strategist = msg.sender;
		rewards = _rewards;
	}

	modifier onlyGovernance() {
		require(msg.sender == governance, "!gov");
		_;
	}

	modifier onlyAdmin() {
		require(msg.sender == governance || msg.sender == strategist, "!(gov||strategist)");
		_;
	}

	function setRewards(address _rewards) public onlyGovernance {
		rewards = _rewards;
	}

	function setStrategist(address _strategist) public onlyGovernance {
		strategist = _strategist;
	}

	function setGovernance(address _governance) public onlyGovernance {
		governance = _governance;
	}

	function setVault(address _token, address _vault) public {
		require(msg.sender == strategist || msg.sender == governance, "!strategist");
		require(vaults[_token] == address(0), "vault");
		vaults[_token] = _vault;
		emit SetVault(_token, _vault);
	}

	function approveStrategy(address _token, address _strategy) public onlyGovernance {
		approvedStrategies[_token][_strategy] = true;
		emit ApproveStrategy(_token, _strategy);
	}

	function revokeStrategy(address _token, address _strategy) public onlyGovernance {
		approvedStrategies[_token][_strategy] = false;
	}

	function setStrategy(address _token, address _strategy) public onlyAdmin {
		require(approvedStrategies[_token][_strategy] == true, "!approved");

		address _current = strategies[_token];
		if (_current != address(0)) {
			IStrategy(_current).withdrawAll();
		}
		strategies[_token] = _strategy;
		emit SetStrategy(_token, _strategy);
	}

	function earn(address _token, uint256 _amount) public {
		address _strategy = strategies[_token];
		IERC20(_token).safeTransfer(_strategy, _amount);
		IStrategy(_strategy).deposit();
	}

	function balanceOf(address _token) external view returns (uint256) {
		return IStrategy(strategies[_token]).balanceOf();
	}

	function withdrawAll(address _token) public onlyAdmin {
		IStrategy(strategies[_token]).withdrawAll();
	}

	function inCaseTokensGetStuck(address _token, uint256 _amount) public onlyAdmin {
		IERC20(_token).safeTransfer(msg.sender, _amount);
	}

	function inCaseStrategyTokenGetStuck(address _strategy, address _token) public onlyAdmin {
		IStrategy(_strategy).withdraw(_token);
	}

	function withdraw(address _token, uint256 _amount) public {
		require(msg.sender == vaults[_token], "!vault");
		IStrategy(strategies[_token]).withdraw(_amount);
	}
}
