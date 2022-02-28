/**
 *Submitted for verification at Etherscan.io on 2020-07-17
 */

pragma solidity 0.6.7;

import "../temp/openzeppelin/ERC20.sol";
import "../temp/openzeppelin/Ownable.sol";

// StakeDaoToken with Governance.
contract SDT is ERC20("Stake DAO Token", "SDT"), Ownable {
    /// @notice Creates `_amount` token to `_to`. Must only be called by the owner (MasterChef).
    function mint(address _to, uint256 _amount) public onlyOwner {
        _mint(_to, _amount);
    }
}
