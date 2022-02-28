//SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.5.0;

import "@openzeppelinV2/contracts/math/SafeMath.sol";
import "@openzeppelinV2/contracts/ownership/Ownable.sol";
import {IERC1155TokenReceiver, IERC1155} from "./ERC1155Tradable.sol";

contract NFTBoosterVault is IERC1155TokenReceiver, Ownable {
    using SafeMath for uint256;

    IERC1155 private nft;
    mapping(address => uint256) private stakedNFT;

    event Staked(address indexed user, uint256 indexed nftId);
    event Unstaked(address indexed user, uint256 indexed nftId);

    constructor(address _nft) public {
        nft = IERC1155(_nft);
    }

    function getNFTAddress() external view returns (address) {
        return address(nft);
    }

    function getStakedNFT(address user) external view returns (uint256) {
        return stakedNFT[user];
    }

    function stake(uint256 _nftId) external {
        require(stakedNFT[msg.sender] == 0, "already staked");
        stakedNFT[msg.sender] = _nftId;
        emit Staked(msg.sender, _nftId);
        nft.safeTransferFrom(msg.sender, address(this), _nftId, 1, "");
    }

    function unstake() external {
        uint256 nftId = stakedNFT[msg.sender];
        require(nftId != 0, "not staked");
        stakedNFT[msg.sender] = 0;
        emit Unstaked(msg.sender, nftId);
        nft.safeTransferFrom(address(this), msg.sender, nftId, 1, "");
    }

    function claimLockedNFTs(
        uint256[] calldata _ids,
        uint256[] calldata _amounts
    ) external onlyOwner {
        nft.safeBatchTransferFrom(
            address(this),
            msg.sender,
            _ids,
            _amounts,
            ""
        );
    }

    function onERC1155Received(
        address,
        address,
        uint256,
        uint256,
        bytes calldata
    ) external returns (bytes4) {
        // Accept only StakeDAO NFT
        if (msg.sender == address(nft)) {
            return 0xf23a6e61;
        }
        revert("nft not accepted");
    }

    function onERC1155BatchReceived(
        address,
        address,
        uint256[] calldata,
        uint256[] calldata,
        bytes calldata
    ) external returns (bytes4) {
        revert("batch transfer not accepted");
    }

    function supportsInterface(bytes4 interfaceID)
        external
        view
        returns (bool)
    {
        if (interfaceID == 0x4e2312e0) {
            return true;
        }
        return false;
    }
}
