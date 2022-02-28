// SPDX-License-Identifier: MIT
pragma solidity 0.6.12;

import '@openzeppelin/contracts/token/ERC20/IERC20.sol';
import '@openzeppelin/contracts/math/SafeMath.sol';
import '@openzeppelin/contracts/utils/Address.sol';
import '@openzeppelin/contracts/token/ERC20/SafeERC20.sol';

interface IStrategy {
  function want() external view returns (address);

  function deposit() external;

  function withdraw(address) external;

  function withdraw(uint256) external;

  function withdrawAll() external returns (uint256);

  function balanceOf() external view returns (uint256);
}

contract Controller {
  using SafeERC20 for IERC20;
  using Address for address;
  using SafeMath for uint256;

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

  constructor(address _rewards) public {
    governance = msg.sender;
    strategist = msg.sender;
    rewards = _rewards;
  }

  function setRewards(address _rewards) public {
    require(msg.sender == governance, '!governance');
    rewards = _rewards;
  }

  function setStrategist(address _strategist) public {
    require(msg.sender == governance, '!governance');
    strategist = _strategist;
  }

  function setGovernance(address _governance) public {
    require(msg.sender == governance, '!governance');
    governance = _governance;
  }

  function setVault(address _token, address _vault) public {
    require(
      msg.sender == strategist || msg.sender == governance,
      '!strategist'
    );
    require(vaults[_token] == address(0), 'vault');
    vaults[_token] = _vault;
    emit SetVault(_token, _vault);
  }

  function approveStrategy(address _token, address _strategy) public {
    require(msg.sender == governance, '!governance');
    approvedStrategies[_token][_strategy] = true;
    emit ApproveStrategy(_token, _strategy);
  }

  function revokeStrategy(address _token, address _strategy) public {
    require(msg.sender == governance, '!governance');
    approvedStrategies[_token][_strategy] = false;
  }

  function setStrategy(address _token, address _strategy) public {
    require(
      msg.sender == strategist || msg.sender == governance,
      '!strategist'
    );
    require(approvedStrategies[_token][_strategy] == true, '!approved');

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

  function withdrawAll(address _token) public {
    require(
      msg.sender == strategist || msg.sender == governance,
      '!strategist'
    );
    IStrategy(strategies[_token]).withdrawAll();
  }

  function inCaseTokensGetStuck(address _token, uint256 _amount) public {
    require(
      msg.sender == strategist || msg.sender == governance,
      '!governance'
    );
    IERC20(_token).safeTransfer(msg.sender, _amount);
  }

  function inCaseStrategyTokenGetStuck(address _strategy, address _token)
    public
  {
    require(
      msg.sender == strategist || msg.sender == governance,
      '!governance'
    );
    IStrategy(_strategy).withdraw(_token);
  }

  function withdraw(address _token, uint256 _amount) public {
    require(msg.sender == vaults[_token], '!vault');
    IStrategy(strategies[_token]).withdraw(_amount);
  }
}
