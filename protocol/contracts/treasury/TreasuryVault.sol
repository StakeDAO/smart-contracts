/**
 *Submitted for verification at Etherscan.io on 2020-08-23
 */

// SPDX-License-Identifier: MIT

pragma solidity >=0.5.16 <0.7.0;

import "../temp/openzeppelin/IERC20.sol";
import "../temp/openzeppelin/SafeMath.sol";
import "../temp/openzeppelin/Address.sol";
import "../temp/openzeppelin/SafeERC20.sol";

import "../../interfaces/yearn/IOneSplitAudit.sol";

interface Governance {
    function notifyRewardAmount(uint256) external;
}

interface TreasuryZap {
    function swap(
        address token_in,
        address token_out,
        uint256 amount_in
    ) external returns (uint256 amount_out);
}

contract TreasuryVault {
    using SafeERC20 for IERC20;

    address public governance;
    address public onesplit;
    address public rewards;
    address public governanceStaking;
    address public treasuryZap;

    mapping(address => bool) authorized;

    constructor(
        address _governanceStaking,
        address _rewards,
        address _treasuryZap
    ) public {
        governance = msg.sender;
        onesplit = address(0x50FDA034C0Ce7a8f7EFDAebDA7Aa7cA21CC1267e);
        treasuryZap = address(_treasuryZap);
        governanceStaking = address(_governanceStaking);
        rewards = address(_rewards);
    }

    function setOnesplit(address _onesplit) external {
        require(msg.sender == governance, "!governance");
        onesplit = _onesplit;
    }

    function setTreasuryZap(address _treasuryZap) external {
        require(msg.sender == governance, "!governance");
        treasuryZap = _treasuryZap;
    }

    function setRewards(address _rewards) external {
        require(msg.sender == governance, "!governance");
        rewards = _rewards;
    }

    function setGovernanceStaking(address _governanceStaking) external {
        require(msg.sender == governance, "!governance");
        governanceStaking = _governanceStaking;
    }

    function setAuthorized(address _authorized) external {
        require(msg.sender == governance, "!governance");
        authorized[_authorized] = true;
    }

    function revokeAuthorized(address _authorized) external {
        require(msg.sender == governance, "!governance");
        authorized[_authorized] = false;
    }

    function setGovernance(address _governance) external {
        require(msg.sender == governance, "!governance");
        governance = _governance;
    }

    function toGovernance(address _token, uint256 _amount) external {
        require(msg.sender == governance, "!governance");
        IERC20(_token).safeTransfer(governance, _amount);
    }

    function toGovernanceStaking() external {
        require(authorized[msg.sender] == true, "!authorized");
        uint256 _balance = IERC20(rewards).balanceOf(address(this));
        IERC20(rewards).safeApprove(governanceStaking, 0);
        IERC20(rewards).safeApprove(governanceStaking, _balance);
        Governance(governanceStaking).notifyRewardAmount(_balance);
    }

    function getExpectedReturn(
        address _from,
        address _to,
        uint256 parts
    ) external view returns (uint256 expected) {
        uint256 _balance = IERC20(_from).balanceOf(address(this));
        (expected, ) = IOneSplitAudit(onesplit).getExpectedReturn(
            _from,
            _to,
            _balance,
            parts,
            0
        );
    }

    // Only allows to withdraw non-core strategy tokens ~ this is over and above normal yield
    function convert(
        address _from,
        address _to,
        uint256 parts
    ) external {
        require(authorized[msg.sender] == true, "!authorized");
        uint256 _amount = IERC20(_from).balanceOf(address(this));
        uint256[] memory _distribution;
        uint256 _expected;
        IERC20(_from).safeApprove(onesplit, 0);
        IERC20(_from).safeApprove(onesplit, _amount);
        (_expected, _distribution) = IOneSplitAudit(onesplit).getExpectedReturn(
            _from,
            _to,
            _amount,
            parts,
            0
        );
        IOneSplitAudit(onesplit).swap(
            _from,
            _to,
            _amount,
            _expected,
            _distribution,
            0
        );
    }

    function swapViaZap(
        address token_in,
        address token_out,
        uint256 amount_in
    ) public returns (uint256 amount_out) {
        require(authorized[msg.sender] == true, "!authorized");
        uint256 _balance = IERC20(token_in).balanceOf(address(this));
        require(_balance >= amount_in, "!balance");
        IERC20(token_in).safeApprove(treasuryZap, 0);
        IERC20(token_in).safeApprove(treasuryZap, amount_in);
        return TreasuryZap(treasuryZap).swap(token_in, token_out, amount_in);
    }
}
