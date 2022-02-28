// SPDX-License-Identifier: MIT
pragma solidity 0.6.12;
pragma experimental ABIEncoderV2;

import "@openzeppelin/contracts/math/SafeMath.sol";
import "@openzeppelin/contracts/utils/Address.sol";
import "@openzeppelin/contracts/token/ERC20/SafeERC20.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

interface IController {
	function withdraw(address, uint256) external;

	function balanceOf(address) external view returns (uint256);

	function earn(address, uint256) external;

	function want(address) external view returns (address);

	function rewards() external view returns (address);

	function vaults(address) external view returns (address);

	function strategies(address) external view returns (address);
}

contract Vault is ERC20 {
	using SafeERC20 for ERC20;
	using Address for address;
	using SafeMath for uint256;

	ERC20 public token;

	uint256 public min = 10000;
	uint256 public constant max = 10000;

	address public governance;
	address public controller;

	event Deposit(address indexed _from, uint256 _shares, uint256 _amount, uint256 pps);

	event Withdraw(address indexed _from, uint256 _shares, uint256 _amount, uint256 pps);

	event Earn(address indexed _from, uint256 _amount);

	constructor(
		address _token,
		address _controller,
		address _governance,
		string memory _namePrefix,
		string memory _symbolPrefix
	)
		public
		ERC20(
			string(abi.encodePacked(_namePrefix, ERC20(_token).name())),
			string(abi.encodePacked(_symbolPrefix, ERC20(_token).symbol()))
		)
	{
		token = ERC20(_token);
		controller = _controller;
		governance = _governance;
	}

	modifier onlyGovernance() {
		require(msg.sender == governance, "!governance");
		_;
	}

	function decimals() public view virtual override returns (uint8) {
		return token.decimals();
	}

	function balance() public view returns (uint256) {
		return token.balanceOf(address(this)).add(IController(controller).balanceOf(address(token)));
	}

	function setMin(uint256 _min) external onlyGovernance {
		min = _min;
	}

	function setGovernance(address _governance) public onlyGovernance {
		governance = _governance;
	}

	function setController(address _controller) public onlyGovernance {
		controller = _controller;
	}

	function available() public view returns (uint256) {
		return token.balanceOf(address(this)).mul(min).div(max);
	}

	function earn() public {
		uint256 _bal = available();
		token.safeTransfer(controller, _bal);
		IController(controller).earn(address(token), _bal);
		emit Earn(msg.sender, _bal);
	}

	function depositAll() external {
		deposit(token.balanceOf(msg.sender));
	}

	function deposit(uint256 _amount) public {
		uint256 _pool = balance();
		uint256 _before = token.balanceOf(address(this));

		token.safeTransferFrom(msg.sender, address(this), _amount);
		uint256 _after = token.balanceOf(address(this));

		_amount = _after.sub(_before);
		uint256 shares = 0;
		if (totalSupply() == 0) {
			shares = _amount;
		} else {
			shares = (_amount.mul(totalSupply())).div(_pool);
		}
		_mint(msg.sender, shares);

		emit Deposit(msg.sender, shares, _amount, getPricePerFullShare());
	}

	function withdrawAll() external {
		withdraw(balanceOf(msg.sender));
	}

	function withdraw(uint256 _shares) public {
		uint256 r = (balance().mul(_shares)).div(totalSupply());
		_burn(msg.sender, _shares);

		uint256 b = token.balanceOf(address(this));

		if (b < r) {
			uint256 _withdraw = r.sub(b);
			IController(controller).withdraw(address(token), _withdraw);
			uint256 _after = token.balanceOf(address(this));
			uint256 _diff = _after.sub(b);
			if (_diff < _withdraw) {
				r = b.add(_diff);
			}
		}

		token.safeTransfer(msg.sender, r);
		emit Withdraw(msg.sender, _shares, r, getPricePerFullShare());
	}

	function getPricePerFullShare() public view returns (uint256) {
		return totalSupply() == 0 ? 1e18 : balance().mul(1e18).div(totalSupply());
	}
}
