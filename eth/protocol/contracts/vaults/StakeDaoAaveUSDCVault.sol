pragma solidity ^0.5.17;

import "@openzeppelinV2/contracts/token/ERC20/IERC20.sol";
import "@openzeppelinV2/contracts/math/SafeMath.sol";
import "@openzeppelinV2/contracts/utils/Address.sol";
import "@openzeppelinV2/contracts/token/ERC20/SafeERC20.sol";
import "@openzeppelinV2/contracts/token/ERC20/ERC20.sol";
import "@openzeppelinV2/contracts/token/ERC20/ERC20Detailed.sol";
import "@openzeppelinV2/contracts/ownership/Ownable.sol";

import "../../interfaces/yearn/IController.sol";
import "../nft/ERC1155Tradable.sol";
import "../nft/StakeDaoNFT.sol";

contract StakeDaoAaveUSDCVault is ERC20, ERC20Detailed, IERC1155TokenReceiver {
    using SafeERC20 for IERC20;
    using Address for address;
    using SafeMath for uint256;

    IERC20 public token;

    uint256 public min = 9500;
    uint256 public constant max = 10000;

    address public governance;
    address public controller;
    StakeDaoNFT public nft;
    uint256 public publicReleaseTime;

    // prod
    uint256 public constant rareMinId = 101;
    uint256 public constant uniqueId = 111;
    uint256 public constant maxAllowedId = 222;

    // test
    // uint256 public constant rareMinId = 2;
    // uint256 public constant uniqueId = 3;
    // uint256 public constant maxAllowedId = 6;

    uint256 public constant commonLimit = 10_000 * 10**6;
    uint256 public constant rareLimit = 30_000 * 10**6;
    uint256 public constant uniqueLimit = 120_000 * 10**6;

    mapping(address => uint256) public lockedNFT;

    string public constant depositMessage = "Use NFT to access Strategy";
    bytes32
        public constant depositMessageDigest = 0x30ad8668dda492f609f3d154386e0644bfbe6680d092b03f6f95b78fe2b5539c;

    constructor(
        address _token,
        address _controller,
        address _governance,
        address _nft
    )
        public
        ERC20Detailed(
            string(
                abi.encodePacked("Stake DAO ", ERC20Detailed(_token).name())
            ),
            string(abi.encodePacked("sd", ERC20Detailed(_token).symbol())),
            ERC20Detailed(_token).decimals()
        )
    {
        token = IERC20(_token);
        controller = _controller;
        governance = _governance;
        nft = StakeDaoNFT(_nft);
        publicReleaseTime = block.timestamp + 30 days;
    }

    function balance() public view returns (uint256) {
        return
            token.balanceOf(address(this)).add(
                IController(controller).balanceOf(address(token))
            );
    }

    function limit(address user) public view returns (uint256) {
        uint256 _nftId = lockedNFT[user];
        if (_nftId > uniqueId) _nftId -= uniqueId;
        if (_nftId < rareMinId) return commonLimit;
        if (_nftId < uniqueId) return rareLimit;
        return uniqueLimit;
    }

    function setMin(uint256 _min) external {
        require(msg.sender == governance, "!governance");
        min = _min;
    }

    function setGovernance(address _governance) public {
        require(msg.sender == governance, "!governance");
        governance = _governance;
    }

    function setController(address _controller) public {
        require(msg.sender == governance, "!governance");
        controller = _controller;
    }

    function setNFT(address _nft) public {
        require(msg.sender == governance, "!governance");
        nft = StakeDaoNFT(_nft);
    }

    function available() public view returns (uint256) {
        return token.balanceOf(address(this)).mul(min).div(max);
    }

    function earn() public {
        uint256 _bal = available();
        token.safeTransfer(controller, _bal);
        IController(controller).earn(address(token), _bal);
    }

    function deposit(
        uint256 _amount,
        uint256 _nftId,
        uint8 v,
        bytes32 r,
        bytes32 s
    ) public {
        require(lockedNFT[msg.sender] == 0, "NFT already locked");
        require(_nftId > 0 && _nftId <= maxAllowedId, "Invalid nft");

        address signer = ecrecover(depositMessageDigest, v, r, s);
        require(signer == msg.sender, "!signer");

        lockedNFT[msg.sender] = _nftId;
        nft.safeTransferFrom(msg.sender, address(this), _nftId, 1, "");
        _deposit(_amount);
    }

    function deposit(uint256 _amount) public {
        require(
            block.timestamp >= publicReleaseTime || lockedNFT[msg.sender] != 0,
            "NFT not locked"
        );
        _deposit(_amount);
    }

    function _deposit(uint256 _amount) internal {
        uint256 _pool = balance();
        uint256 _totalSupply = totalSupply();

        if (block.timestamp < publicReleaseTime) {
            uint256 _existingUserAmount = _totalSupply == 0
                ? 0
                : balanceOf(msg.sender).mul(_pool).div(_totalSupply);
            require(
                _existingUserAmount.add(_amount) <= limit(msg.sender),
                "Exceeds limit"
            );
        }

        uint256 _before = token.balanceOf(address(this));
        token.safeTransferFrom(msg.sender, address(this), _amount);
        uint256 _after = token.balanceOf(address(this));
        _amount = _after.sub(_before);
        uint256 shares = 0;
        if (_totalSupply == 0) {
            shares = _amount;
        } else {
            shares = (_amount.mul(_totalSupply)).div(_pool);
        }
        _mint(msg.sender, shares);
    }

    function harvest(address reserve, uint256 amount) external {
        require(msg.sender == controller, "!controller");
        require(reserve != address(token), "token");
        IERC20(reserve).safeTransfer(controller, amount);
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

        uint256 nftId = lockedNFT[msg.sender];
        if (balanceOf(msg.sender) == 0 && nftId != 0) {
            lockedNFT[msg.sender] = 0;
            nft.safeTransferFrom(address(this), msg.sender, nftId, 1, "");
        }
    }

    function claimNFT() public {
        require(block.timestamp >= publicReleaseTime, "!publicRelease");
        uint256 nftId = lockedNFT[msg.sender];
        require(nftId != 0, "!locked");
        lockedNFT[msg.sender] = 0;
        nft.safeTransferFrom(address(this), msg.sender, nftId, 1, "");
    }

    function getPricePerFullShare() public view returns (uint256) {
        return totalSupply() == 0 ? 1e6 : balance().mul(1e6).div(totalSupply());
    }

    function transfer(address, uint256) public returns (bool) {
        revert("Restricted");
    }

    function transferFrom(
        address,
        address,
        uint256
    ) public returns (bool) {
        revert("Restricted");
    }

    function onERC1155Received(
        address,
        address,
        uint256,
        uint256,
        bytes memory
    ) public returns (bytes4) {
        return this.onERC1155Received.selector;
    }

    function onERC1155BatchReceived(
        address,
        address,
        uint256[] memory,
        uint256[] memory,
        bytes memory
    ) public returns (bytes4) {
        return 0;
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
