import pytest
from brownie import *
import typer
import json
import brownie

MAX_SUPPLY = 1
INITIAL_SUPPLY = 1
CREATE_COUNT = 2
NFT_1 = 223
NFT_2 = 224

@pytest.fixture(scope='module', autouse=True)
def deployedContracts():
    # accounts used for executing transactions
    DEPLOYER = accounts[0]
    fromDeployer = {'from': DEPLOYER}

    STRATEGY = accounts[1]
    fromStrategy = {'from': STRATEGY}

    STRATEGY2 = accounts[2]
    fromStrategy2 = {'from': STRATEGY2}

    ALICE = accounts[3]
    fromAlice = {'from': ALICE}

    BOB = accounts[4]
    fromBob = {'from': BOB}

    # deploy NFT contract
    nft = StratAccessNFT.deploy(ZERO_ADDRESS, fromDeployer)

    return {'DEPLOYER': DEPLOYER, 'fromDeployer': fromDeployer, 'nft': nft, 'STRATEGY': STRATEGY, 'fromStrategy': fromStrategy, 'STRATEGY2': STRATEGY2, 'fromStrategy2': fromStrategy2, 'ALICE': ALICE, 'fromAlice': fromAlice, 'BOB': BOB, 'fromBob': fromBob}

def test_add_strategy(deployedContracts):
    fromDeployer = deployedContracts['fromDeployer']
    STRATEGY = deployedContracts['STRATEGY']
    nft = deployedContracts['nft']

    isStrategy = nft.isStrategy(STRATEGY)
    assert isStrategy == False

    nft.addStrategy(STRATEGY, fromDeployer)

    isStrategy = nft.isStrategy(STRATEGY)
    assert isStrategy == True

def test_start_using_without_balance(deployedContracts):
    fromStrategy = deployedContracts['fromStrategy']
    ALICE = deployedContracts['ALICE']
    nft = deployedContracts['nft']

    balance = nft.balanceOf(ALICE, NFT_1)
    assert balance == 0

    with brownie.reverts('StratAccessNFT: user account doesnt have NFT'):
        nft.startUsingNFT(ALICE, NFT_1, fromStrategy)

def test_start_using_with_balance(deployedContracts):
    fromStrategy = deployedContracts['fromStrategy']
    fromDeployer = deployedContracts['fromDeployer']
    DEPLOYER = deployedContracts['DEPLOYER']
    ALICE = deployedContracts['ALICE']
    nft = deployedContracts['nft']

    for i in range(1, CREATE_COUNT + 1):
        tx = nft.create(MAX_SUPPLY, INITIAL_SUPPLY, '', '', fromDeployer)
    nft.safeBatchTransferFrom(DEPLOYER, ALICE, [NFT_1, NFT_2], [1, 1], '', fromDeployer)
    balance = nft.balanceOf(ALICE, NFT_1)
    assert balance == 1

    useCount = nft.getTotalUseCount(ALICE, NFT_1)
    assert useCount == 0

    nft.startUsingNFT(ALICE, NFT_1, fromStrategy)
    useCount = nft.getTotalUseCount(ALICE, NFT_1)
    assert useCount == 1

    nft.startUsingNFT(ALICE, NFT_1, fromStrategy)
    useCount = nft.getTotalUseCount(ALICE, NFT_1)
    assert useCount == 2

def test_transfer_when_in_use(deployedContracts):
    fromAlice = deployedContracts['fromAlice']
    ALICE = deployedContracts['ALICE']
    BOB = deployedContracts['BOB']
    nft = deployedContracts['nft']

    useCount = nft.getTotalUseCount(ALICE, NFT_1)
    assert useCount > 0
    balance = nft.balanceOf(ALICE, NFT_1)
    assert balance == 1

    # Transfer should fail if NFT is in use
    with brownie.reverts('StratAccessNFT: NFT being used in strategy'):
        nft.safeTransferFrom(ALICE, BOB, NFT_1, 1, "", fromAlice)

    # Batch transfer should fail if NFT is in use
    with brownie.reverts('StratAccessNFT: NFT being used in strategy'):
        nft.safeBatchTransferFrom(ALICE, BOB, [NFT_1, NFT_2], [1, 1], "", fromAlice)

def test_end_using(deployedContracts):
    fromStrategy = deployedContracts['fromStrategy']
    ALICE = deployedContracts['ALICE']
    nft = deployedContracts['nft']

    useCount = nft.getTotalUseCount(ALICE, NFT_1)
    assert useCount == 2

    nft.endUsingNFT(ALICE, NFT_1, fromStrategy)
    useCount = nft.getTotalUseCount(ALICE, NFT_1)
    assert useCount == 1

    nft.endUsingNFT(ALICE, NFT_1, fromStrategy)
    useCount = nft.getTotalUseCount(ALICE, NFT_1)
    assert useCount == 0

def test_transfer_when_not_in_use(deployedContracts):
    fromAlice = deployedContracts['fromAlice']
    ALICE = deployedContracts['ALICE']
    BOB = deployedContracts['BOB']
    nft = deployedContracts['nft']

    useCount = nft.getTotalUseCount(ALICE, NFT_1)
    assert useCount == 0
    balance = nft.balanceOf(ALICE, NFT_1)
    assert balance == 1

    # Transfer should work if NFT is not in use and final balance is zero
    nft.safeTransferFrom(ALICE, BOB, NFT_1, 1, "", fromAlice)

def test_remove_strategy(deployedContracts):
    fromDeployer = deployedContracts['fromDeployer']
    STRATEGY = deployedContracts['STRATEGY']
    nft = deployedContracts['nft']

    isStrategy = nft.isStrategy(STRATEGY)
    assert isStrategy == True

    nft.removeStrategy(STRATEGY, fromDeployer)

    isStrategy = nft.isStrategy(STRATEGY)
    assert isStrategy == False

def test_unregistered_strat(deployedContracts):
    fromBob = deployedContracts['fromBob']
    BOB = deployedContracts['BOB']
    ALICE = deployedContracts['ALICE']
    nft = deployedContracts['nft']

    isStrategy = nft.isStrategy(BOB)
    assert isStrategy == False

    # startUsingNFT call from unregistered strategy should fail
    with brownie.reverts('StrategyRole: caller does not have the Strategy role'):
        nft.startUsingNFT(ALICE, NFT_1, fromBob)

    # endUsingNFT call from unregistered strategy should fail
    with brownie.reverts('StrategyRole: caller does not have the Strategy role'):
        nft.endUsingNFT(ALICE, NFT_1, fromBob)

def test_end_using_diff_strat(deployedContracts):
    fromStrategy1 = deployedContracts['fromStrategy']
    STRATEGY1 = deployedContracts['STRATEGY']
    fromStrategy2 = deployedContracts['fromStrategy2']
    STRATEGY2 = deployedContracts['STRATEGY2']
    fromDeployer = deployedContracts['fromDeployer']
    fromBob = deployedContracts['fromBob']
    BOB = deployedContracts['BOB']
    ALICE = deployedContracts['ALICE']
    nft = deployedContracts['nft']

    nft.safeTransferFrom(BOB, ALICE, NFT_1, 1, "", fromBob)

    # add both strategies
    nft.addStrategy(STRATEGY1, fromDeployer)
    nft.addStrategy(STRATEGY2, fromDeployer)

    # start using NFT from strategy 1
    nft.startUsingNFT(ALICE, NFT_1, fromStrategy1)

    # end using NFT from strategy 2
    with brownie.reverts('SafeMath: subtraction overflow'):
        nft.endUsingNFT(ALICE, NFT_1, fromStrategy2)

    # end using NFT from strategy 1
    nft.endUsingNFT(ALICE, NFT_1, fromStrategy1)
