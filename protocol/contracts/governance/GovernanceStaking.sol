/**
 *Submitted for verification at Etherscan.io on 2020-07-29
 */

/*
   ____            __   __        __   _
  / __/__ __ ___  / /_ / /  ___  / /_ (_)__ __
 _\ \ / // // _ \/ __// _ \/ -_)/ __// / \ \ /
/___/ \_, //_//_/\__//_//_/\__/ \__//_/ /_\_\
     /___/

* Synthetix: YFIRewards.sol
*
* Docs: https://docs.synthetix.io/
*
*
* MIT License
* ===========
*
* Copyright (c) 2020 Synthetix
*
* Permission is hereby granted, free of charge, to any person obtaining a copy
* of this software and associated documentation files (the "Software"), to deal
* in the Software without restriction, including without limitation the rights
* to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
* copies of the Software, and to permit persons to whom the Software is
* furnished to do so, subject to the following conditions:
*
* The above copyright notice and this permission notice shall be included in all
* copies or substantial portions of the Software.
*
* THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
* IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
* FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
* AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
* LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
* OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
*/

// File: contracts/IRewardDistributionRecipient.sol

pragma solidity ^0.5.0;

import "@openzeppelinV2/contracts/math/Math.sol";
import "@openzeppelinV2/contracts/math/SafeMath.sol";
import "@openzeppelinV2/contracts/GSN/Context.sol";
import "@openzeppelinV2/contracts/ownership/Ownable.sol";
import "@openzeppelinV2/contracts/utils/Address.sol";
import "@openzeppelinV2/contracts/token/ERC20/IERC20.sol";
import "@openzeppelinV2/contracts/token/ERC20/SafeERC20.sol";

contract IRewardDistributionRecipient is Ownable {
    address rewardDistribution;

    function notifyRewardAmount(uint256 reward) external;

    modifier onlyRewardDistribution() {
        require(
            _msgSender() == rewardDistribution,
            "Caller is not reward distribution"
        );
        _;
    }

    function setRewardDistribution(address _rewardDistribution)
        external
        onlyOwner
    {
        rewardDistribution = _rewardDistribution;
    }
}

// File: contracts/CurveRewards.sol

pragma solidity ^0.5.0;

contract LPTokenWrapper {
    using SafeMath for uint256;
    using SafeERC20 for IERC20;

    IERC20 public vote; //sdt token

    uint256 private _totalSupply;
    mapping(address => uint256) private _balances;

    function setVote(address _vote) public {
        vote = IERC20(_vote);
    }

    function totalSupply() public view returns (uint256) {
        return _totalSupply;
    }

    function balanceOf(address account) public view returns (uint256) {
        return _balances[account];
    }

    function stake(uint256 amount) public {
        _totalSupply = _totalSupply.add(amount);
        _balances[msg.sender] = _balances[msg.sender].add(amount);
        vote.safeTransferFrom(msg.sender, address(this), amount);
    }

    function withdraw(uint256 amount) public {
        _totalSupply = _totalSupply.sub(amount);
        _balances[msg.sender] = _balances[msg.sender].sub(amount);
        vote.safeTransfer(msg.sender, amount);
    }
}

interface Executor {
    function execute(
        uint256,
        uint256,
        uint256,
        uint256
    ) external;
}

contract StakeDaoGovernance is LPTokenWrapper, IRewardDistributionRecipient {
    /* Fee collection for any other token */

    function seize(IERC20 _token, uint256 amount) external {
        require(msg.sender == governance, "!governance");
        require(_token != token, "reward");
        require(_token != vote, "vote");
        _token.safeTransfer(governance, amount);
    }

    /* Fees breaker, to protect withdraws if anything ever goes wrong */

    bool public breaker = false;

    function setBreaker(bool _breaker) external {
        require(msg.sender == governance, "!governance");
        breaker = _breaker;
    }

    /* Modifications for proposals */

    mapping(address => uint256) public voteLock; // period that your sake it locked to keep it for voting

    struct Proposal {
        uint256 id;
        address proposer;
        mapping(address => uint256) forVotes;
        mapping(address => uint256) againstVotes;
        uint256 totalForVotes;
        uint256 totalAgainstVotes;
        uint256 start; // block start;
        uint256 end; // start + period
        address executor;
        string hash;
        uint256 totalVotesAvailable;
        uint256 quorum;
        uint256 quorumRequired;
        bool open;
    }

    mapping(uint256 => Proposal) public proposals;
    uint256 public proposalCount;
    uint256 public period = 17280; // voting period in blocks ~ 17280 3 days for 15s/block
    uint256 public lock = 17280; // vote lock in blocks ~ 17280 3 days for 15s/block
    uint256 public minimum = 1e18;
    uint256 public quorum = 2000;
    bool public config = true;

    address public governance;

    function setGovernance(address _governance) public {
        require(msg.sender == governance, "!governance");
        governance = _governance;
    }

    function setQuorum(uint256 _quorum) public {
        require(msg.sender == governance, "!governance");
        quorum = _quorum;
    }

    function setMinimum(uint256 _minimum) public {
        require(msg.sender == governance, "!governance");
        minimum = _minimum;
    }

    function setPeriod(uint256 _period) public {
        require(msg.sender == governance, "!governance");
        period = _period;
    }

    function setLock(uint256 _lock) public {
        require(msg.sender == governance, "!governance");
        lock = _lock;
    }

    function setToken(address _token) public {
        require(msg.sender == governance, "!governance");
        token = IERC20(_token);
    }

    function initialize(
        uint256 id,
        address _governance,
        address _token,
        address _vote
    ) public {
        require(config == true, "!config");
        setVote(_vote);
        config = false;
        proposalCount = id;
        governance = _governance; //govGSP
        token = IERC20(_token);
    }

    event NewProposal(
        uint256 id,
        address creator,
        uint256 start,
        uint256 duration,
        address executor
    );
    event Vote(
        uint256 indexed id,
        address indexed voter,
        bool vote,
        uint256 weight
    );

    function propose(address executor, string memory hash) public {
        require(votesOf(msg.sender) > minimum, "<minimum");
        proposals[proposalCount++] = Proposal({
            id: proposalCount,
            proposer: msg.sender,
            totalForVotes: 0,
            totalAgainstVotes: 0,
            start: block.number,
            end: period.add(block.number),
            executor: executor,
            hash: hash,
            totalVotesAvailable: totalVotes,
            quorum: 0,
            quorumRequired: quorum,
            open: true
        });

        emit NewProposal(
            proposalCount,
            msg.sender,
            block.number,
            period,
            executor
        );
        voteLock[msg.sender] = lock.add(block.number);
    }

    function execute(uint256 id) public {
        (uint256 _for, uint256 _against, uint256 _quorum) = getStats(id);
        require(proposals[id].quorumRequired < _quorum, "!quorum");
        require(proposals[id].end < block.number, "!end");
        if (proposals[id].open == true) {
            tallyVotes(id);
        }
        Executor(proposals[id].executor).execute(id, _for, _against, _quorum);
    }

    function getStats(uint256 id)
        public
        view
        returns (
            uint256 _for,
            uint256 _against,
            uint256 _quorum
        )
    {
        _for = proposals[id].totalForVotes;
        _against = proposals[id].totalAgainstVotes;

        uint256 _total = _for.add(_against);
        _for = _for.mul(10000).div(_total);
        _against = _against.mul(10000).div(_total);

        _quorum = _total.mul(10000).div(proposals[id].totalVotesAvailable);
    }

    event ProposalFinished(
        uint256 indexed id,
        uint256 _for,
        uint256 _against,
        bool quorumReached
    );

    function tallyVotes(uint256 id) public {
        require(proposals[id].open == true, "!open");
        require(proposals[id].end < block.number, "!end");

        (uint256 _for, uint256 _against, ) = getStats(id);
        bool _quorum = false;
        if (proposals[id].quorum >= proposals[id].quorumRequired) {
            _quorum = true;
        }
        proposals[id].open = false;
        emit ProposalFinished(id, _for, _against, _quorum);
    }

    function votesOf(address voter) public view returns (uint256) {
        return votes[voter];
    }

    uint256 public totalVotes;
    mapping(address => uint256) public votes;
    event RegisterVoter(address voter, uint256 votes, uint256 totalVotes);
    event RevokeVoter(address voter, uint256 votes, uint256 totalVotes);

    function register() public {
        require(voters[msg.sender] == false, "voter");
        voters[msg.sender] = true;
        votes[msg.sender] = balanceOf(msg.sender);
        totalVotes = totalVotes.add(votes[msg.sender]);
        emit RegisterVoter(msg.sender, votes[msg.sender], totalVotes);
    }

    function revoke() public {
        require(voters[msg.sender] == true, "!voter");
        voters[msg.sender] = false;
        if (totalVotes < votes[msg.sender]) {
            //edge case, should be impossible, but this is defi
            totalVotes = 0;
        } else {
            totalVotes = totalVotes.sub(votes[msg.sender]);
        }
        emit RevokeVoter(msg.sender, votes[msg.sender], totalVotes);
        votes[msg.sender] = 0;
    }

    mapping(address => bool) public voters;

    function voteFor(uint256 id) public {
        require(proposals[id].start < block.number, "<start");
        require(proposals[id].end > block.number, ">end");

        uint256 _against = proposals[id].againstVotes[msg.sender];
        if (_against > 0) {
            proposals[id].totalAgainstVotes = proposals[id]
                .totalAgainstVotes
                .sub(_against);
            proposals[id].againstVotes[msg.sender] = 0;
        }

        uint256 vote = votesOf(msg.sender).sub(
            proposals[id].forVotes[msg.sender]
        );
        proposals[id].totalForVotes = proposals[id].totalForVotes.add(vote);
        proposals[id].forVotes[msg.sender] = votesOf(msg.sender);

        proposals[id].totalVotesAvailable = totalVotes;
        uint256 _votes = proposals[id].totalForVotes.add(
            proposals[id].totalAgainstVotes
        );
        proposals[id].quorum = _votes.mul(10000).div(totalVotes);

        voteLock[msg.sender] = lock.add(block.number);

        emit Vote(id, msg.sender, true, vote);
    }

    function voteAgainst(uint256 id) public {
        require(proposals[id].start < block.number, "<start");
        require(proposals[id].end > block.number, ">end");

        uint256 _for = proposals[id].forVotes[msg.sender];
        if (_for > 0) {
            proposals[id].totalForVotes = proposals[id].totalForVotes.sub(_for);
            proposals[id].forVotes[msg.sender] = 0;
        }

        uint256 vote = votesOf(msg.sender).sub(
            proposals[id].againstVotes[msg.sender]
        );
        proposals[id].totalAgainstVotes = proposals[id].totalAgainstVotes.add(
            vote
        );
        proposals[id].againstVotes[msg.sender] = votesOf(msg.sender);

        proposals[id].totalVotesAvailable = totalVotes;
        uint256 _votes = proposals[id].totalForVotes.add(
            proposals[id].totalAgainstVotes
        );
        proposals[id].quorum = _votes.mul(10000).div(totalVotes);

        voteLock[msg.sender] = lock.add(block.number);

        emit Vote(id, msg.sender, false, vote);
    }

    /* Default rewards contract */

    IERC20 public token; //yCRV token

    uint256 public constant DURATION = 7 days;

    uint256 public periodFinish = 0;
    uint256 public rewardRate = 0;
    uint256 public lastUpdateTime;
    uint256 public rewardPerTokenStored;
    mapping(address => uint256) public userRewardPerTokenPaid;
    mapping(address => uint256) public rewards;

    event RewardAdded(uint256 reward);
    event Staked(address indexed user, uint256 amount);
    event Withdrawn(address indexed user, uint256 amount);
    event RewardPaid(address indexed user, uint256 reward);

    modifier updateReward(address account) {
        rewardPerTokenStored = rewardPerToken();
        lastUpdateTime = lastTimeRewardApplicable();
        if (account != address(0)) {
            rewards[account] = earned(account);
            userRewardPerTokenPaid[account] = rewardPerTokenStored;
        }
        _;
    }

    function lastTimeRewardApplicable() public view returns (uint256) {
        return Math.min(block.timestamp, periodFinish);
    }

    function rewardPerToken() public view returns (uint256) {
        if (totalSupply() == 0) {
            return rewardPerTokenStored;
        }
        return
            rewardPerTokenStored.add(
                lastTimeRewardApplicable()
                    .sub(lastUpdateTime)
                    .mul(rewardRate)
                    .mul(1e18)
                    .div(totalSupply())
            );
    }

    function earned(address account) public view returns (uint256) {
        return
            balanceOf(account)
                .mul(rewardPerToken().sub(userRewardPerTokenPaid[account]))
                .div(1e18)
                .add(rewards[account]);
    }

    // stake visibility is public as overriding LPTokenWrapper's stake() function
    function stake(uint256 amount) public updateReward(msg.sender) {
        require(amount > 0, "Cannot stake 0");
        if (voters[msg.sender] == true) {
            votes[msg.sender] = votes[msg.sender].add(amount);
            totalVotes = totalVotes.add(amount);
        }
        super.stake(amount);
        emit Staked(msg.sender, amount);
    }

    function withdraw(uint256 amount) public updateReward(msg.sender) {
        require(amount > 0, "Cannot withdraw 0");
        if (voters[msg.sender] == true) {
            votes[msg.sender] = votes[msg.sender].sub(amount);
            totalVotes = totalVotes.sub(amount);
        }
        if (breaker == false) {
            require(voteLock[msg.sender] < block.number, "!locked");
        }
        super.withdraw(amount);
        emit Withdrawn(msg.sender, amount);
    }

    function exit() external {
        withdraw(balanceOf(msg.sender));
        getReward();
    }

    function getReward() public updateReward(msg.sender) {
        if (breaker == false) {
            require(voteLock[msg.sender] > block.number, "!voted");
        }
        uint256 reward = earned(msg.sender);
        if (reward > 0) {
            rewards[msg.sender] = 0;
            token.safeTransfer(msg.sender, reward);
            emit RewardPaid(msg.sender, reward);
        }
    }

    function notifyRewardAmount(uint256 reward)
        external
        onlyRewardDistribution
        updateReward(address(0))
    {
        IERC20(token).safeTransferFrom(msg.sender, address(this), reward);
        if (block.timestamp >= periodFinish) {
            rewardRate = reward.div(DURATION);
        } else {
            uint256 remaining = periodFinish.sub(block.timestamp);
            uint256 leftover = remaining.mul(rewardRate);
            rewardRate = reward.add(leftover).div(DURATION);
        }
        lastUpdateTime = block.timestamp;
        periodFinish = block.timestamp.add(DURATION);
        emit RewardAdded(reward);
    }
}
