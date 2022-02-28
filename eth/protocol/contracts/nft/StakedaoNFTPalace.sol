//SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.5.0;

import "./ERC1155Tradable.sol";

contract StakeTokenWrapper {
    using SafeMath for uint256;
    IERC20 public xsdt;

    constructor(IERC20 _xsdt) public {
        xsdt = IERC20(_xsdt);
    }

    uint256 private _totalSupply;
    mapping(address => uint256) private _balances;

    function totalSupply() public view returns (uint256) {
        return _totalSupply;
    }

    function balanceOf(address account) public view returns (uint256) {
        return _balances[account];
    }

    function stake(uint256 amount) public {
        _totalSupply = _totalSupply.add(amount);
        _balances[msg.sender] = _balances[msg.sender].add(amount);
        xsdt.transferFrom(msg.sender, address(this), amount);
    }

    function withdraw(uint256 amount) public {
        _totalSupply = _totalSupply.sub(amount);
        _balances[msg.sender] = _balances[msg.sender].sub(amount);
        xsdt.transfer(msg.sender, amount);
    }
}

contract StakeDaoNFTPalace is StakeTokenWrapper, Ownable {
    ERC1155Tradable public nft;

    mapping(address => uint256) public lastUpdateTime;
    mapping(address => uint256) public points;
    mapping(uint256 => uint256) public cards;

    event CardAdded(uint256 card, uint256 points);
    event Staked(address indexed user, uint256 amount);
    event Withdrawn(address indexed user, uint256 amount);
    event Redeemed(address indexed user, uint256 id);
    event NFTSet(ERC1155Tradable indexed newNFT);

    modifier updateReward(address account) {
        if (account != address(0)) {
            points[account] = earned(account);
            lastUpdateTime[account] = block.timestamp;
        }
        _;
    }

    constructor(ERC1155Tradable _nftAddress, IERC20 _xsdt)
        public
        StakeTokenWrapper(_xsdt)
    {
        nft = _nftAddress;
    }

    function setNFT(ERC1155Tradable _nftAddress) public onlyOwner {
        nft = _nftAddress;
        emit NFTSet(_nftAddress);
    }

    function addCard(uint256 cardId, uint256 amount) public onlyOwner {
        cards[cardId] = amount;
        emit CardAdded(cardId, amount);
    }

    function earned(address account) public view returns (uint256) {
        uint256 timeDifference = block.timestamp.sub(lastUpdateTime[account]);
        uint256 balance = balanceOf(account);
        uint256 decimals = 1e18;
        uint256 x = balance / decimals;
        uint256 ratePerMin = decimals.mul(x).div(x.add(12000)).div(240);
        return points[account].add(ratePerMin.mul(timeDifference));
    }

    // stake visibility is public as overriding StakeTokenWrapper's stake() function
    function stake(uint256 amount) public updateReward(msg.sender) {
        require(amount > 0, "Invalid amount");

        super.stake(amount);
        emit Staked(msg.sender, amount);
    }

    function withdraw(uint256 amount) public updateReward(msg.sender) {
        require(amount > 0, "Cannot withdraw 0");

        super.withdraw(amount);
        emit Withdrawn(msg.sender, amount);
    }

    function exit() external {
        withdraw(balanceOf(msg.sender));
    }

    function redeem(uint256 card) public updateReward(msg.sender) {
        require(cards[card] != 0, "Card not found");
        require(
            points[msg.sender] >= cards[card],
            "Not enough points to redeem for card"
        );
        require(
            nft.totalSupply(card) < nft.maxSupply(card),
            "Max cards minted"
        );

        points[msg.sender] = points[msg.sender].sub(cards[card]);
        nft.mint(msg.sender, card, 1, "");
        emit Redeemed(msg.sender, card);
    }
}
