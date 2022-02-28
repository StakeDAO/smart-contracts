import pytest
from brownie import *
import typer
import json
import brownie

commonId = 223
rareId = 332
uniqueId = 333

@pytest.fixture(scope="module", autouse=True)
def deployedContracts():

    deployed = open("config.json", "r")

    try:
        deployed = json.loads(deployed.read())
    except:
        deployed = {}

    ENV = ""
    if (network.chain.id == 1):
        ENV = "prod"
    else:
        ENV = "dev"

    # account used for executing transactions
    DEFAULT_DEPLOYER_ACCOUNT = accounts[0]
    deployer = {'from': DEFAULT_DEPLOYER_ACCOUNT}

    COMMON_USER = accounts[1]
    commonUser = {'from': COMMON_USER}

    RARE_USER = accounts[2]
    rareUser = {'from': RARE_USER}

    UNIQUE_USER = accounts[3]
    uniqueUser = {'from': UNIQUE_USER}

    PLEB_USER = accounts[4]
    plebUser = {'from': PLEB_USER}

    REWARDER = accounts[5]
    rewarder = {'from': REWARDER}

    SDT = deployed[ENV]['SDT']
    sdt = Contract(SDT)

    WHALE = "0xc78fa2af0ca7990bb5ff32c9a728125be58cf247"
    whale = {'from': WHALE}
    sdt.transfer(REWARDER, sdt.balanceOf(WHALE)/5, whale)
    sdt.transfer(COMMON_USER, sdt.balanceOf(WHALE)/4, whale)
    sdt.transfer(RARE_USER, sdt.balanceOf(WHALE)/3, whale)
    sdt.transfer(UNIQUE_USER, sdt.balanceOf(WHALE)/2, whale)
    sdt.transfer(PLEB_USER, sdt.balanceOf(WHALE), whale)

    nft = StratAccessNFT.deploy(ZERO_ADDRESS, deployer)

    darkParadise = DarkParadise.deploy(SDT, nft.address, deployer)
    darkParadise.setRewardDistribution(REWARDER)
    nft.addStrategy(darkParadise.address, deployer)

    sdt.approve(darkParadise.address, sdt.balanceOf(REWARDER), rewarder)
    sdt.approve(darkParadise.address, sdt.balanceOf(COMMON_USER), commonUser)
    sdt.approve(darkParadise.address, sdt.balanceOf(RARE_USER), rareUser)
    sdt.approve(darkParadise.address, sdt.balanceOf(UNIQUE_USER), uniqueUser)

    return {
      'DEFAULT_DEPLOYER_ACCOUNT': DEFAULT_DEPLOYER_ACCOUNT,
      'deployer': deployer,
      'nft': nft,
      'sdt': sdt,
      'darkParadise': darkParadise,
      'COMMON_USER': COMMON_USER,
      'commonUser': commonUser,
      'RARE_USER': RARE_USER,
      'rareUser': rareUser,
      'UNIQUE_USER': UNIQUE_USER,
      'uniqueUser': uniqueUser,
      'PLEB_USER': PLEB_USER,
      'plebUser': plebUser,
      'REWARDER': REWARDER,
      'rewarder': rewarder
    }

def test_create_nfts(deployedContracts):
    nft = deployedContracts['nft']
    deployer = deployedContracts['deployer']
    DEFAULT_DEPLOYER_ACCOUNT = deployedContracts['DEFAULT_DEPLOYER_ACCOUNT']
    COMMON_USER = deployedContracts['COMMON_USER']
    RARE_USER = deployedContracts['RARE_USER']
    UNIQUE_USER = deployedContracts['UNIQUE_USER']

    for i in range(1, 112):
        tx = nft.create(1, 1, "", "", deployer)
        id = tx.return_value
        assert id == i + 222 # nft ids start from 223 for this version of nft

    nft.safeTransferFrom(DEFAULT_DEPLOYER_ACCOUNT, COMMON_USER, commonId, 1, "", deployer)
    nft.safeTransferFrom(DEFAULT_DEPLOYER_ACCOUNT, RARE_USER, rareId, 1, "", deployer)
    nft.safeTransferFrom(DEFAULT_DEPLOYER_ACCOUNT, UNIQUE_USER, uniqueId, 1, "", deployer)

def test_enter_leave(deployedContracts):
    sdt = deployedContracts['sdt']
    darkParadise = deployedContracts['darkParadise']
    COMMON_USER = deployedContracts['COMMON_USER']
    commonUser = deployedContracts['commonUser']

    shareBefore = darkParadise.balanceOf(COMMON_USER)
    senderSDTBefore = sdt.balanceOf(COMMON_USER)
    paradiseSDTBefore = sdt.balanceOf(darkParadise.address)

    darkParadise.enter(4_000 * 10**18, commonId, commonUser)

    shareMiddle = darkParadise.balanceOf(COMMON_USER)
    senderSDTMiddle = sdt.balanceOf(COMMON_USER)
    paradiseSDTMiddle = sdt.balanceOf(darkParadise.address)

    assert shareMiddle - shareBefore == 4_000 * 10**18
    assert senderSDTBefore - senderSDTMiddle == 4_000 * 10**18
    assert paradiseSDTMiddle - paradiseSDTBefore == 4_000 * 10**18

    darkParadise.leave(4_000 * 10**18, commonUser)

    shareAfter = darkParadise.balanceOf(COMMON_USER)
    senderSDTAfter = sdt.balanceOf(COMMON_USER)
    paradiseSDTAfter = sdt.balanceOf(darkParadise.address)

    assert shareAfter == 0
    assert senderSDTAfter - senderSDTMiddle == 4_000 * 10**18
    assert paradiseSDTMiddle - paradiseSDTAfter == 4_000 * 10**18

def test_common_limit(deployedContracts):
    darkParadise = deployedContracts['darkParadise']
    commonUser = deployedContracts['commonUser']

    darkParadise.enter(9_000 * 10**18, commonId, commonUser)

    with brownie.reverts('Limit hit'):
        darkParadise.enter(2_000 * 10**18, commonId, commonUser)

    darkParadise.leave(9_000 * 10**18, commonUser)

def test_rare_limit(deployedContracts):
    darkParadise = deployedContracts['darkParadise']
    rareUser = deployedContracts['rareUser']

    darkParadise.enter(29_000 * 10**18, rareId, rareUser)

    with brownie.reverts('Limit hit'):
        darkParadise.enter(2_000 * 10**18, rareId, rareUser)

    darkParadise.leave(29_000 * 10**18, rareUser)

def test_unique_limit(deployedContracts):
    darkParadise = deployedContracts['darkParadise']
    uniqueUser = deployedContracts['uniqueUser']

    darkParadise.enter(119_000 * 10**18, uniqueId, uniqueUser)

    with brownie.reverts('Limit hit'):
        darkParadise.enter(2_000 * 10**18, uniqueId, uniqueUser)

    darkParadise.leave(119_000 * 10**18, uniqueUser)

def test_transfer_restrictions(deployedContracts):
    nft = deployedContracts['nft']
    darkParadise = deployedContracts['darkParadise']
    COMMON_USER = deployedContracts['COMMON_USER']
    commonUser = deployedContracts['commonUser']
    PLEB_USER = deployedContracts['PLEB_USER']
    plebUser = deployedContracts['plebUser']

    darkParadise.enter(9_000 * 10**18, commonId, commonUser)

    with brownie.reverts('StratAccessNFT: NFT being used in strategy'):
        nft.safeTransferFrom(COMMON_USER, PLEB_USER, commonId, 1, "", commonUser)

    with brownie.reverts('Restricted'):
        darkParadise.transfer(PLEB_USER, 1_000 * 10**18, commonUser)

    with brownie.reverts('Restricted'):
        darkParadise.transferFrom(COMMON_USER, PLEB_USER, 1_000 * 10**18, plebUser)

    darkParadise.leave(9_000 * 10**18, commonUser)

    nft.safeTransferFrom(COMMON_USER, PLEB_USER, commonId, 1, "", commonUser)
    nft.safeTransferFrom(PLEB_USER, COMMON_USER, commonId, 1, "", plebUser)

def test_multiple_enter_leave(deployedContracts):
    darkParadise = deployedContracts['darkParadise']
    sdt = deployedContracts['sdt']
    commonUser = deployedContracts['commonUser']
    COMMON_USER = deployedContracts['COMMON_USER']
    rareUser = deployedContracts['rareUser']
    RARE_USER = deployedContracts['RARE_USER']
    uniqueUser = deployedContracts['uniqueUser']
    UNIQUE_USER = deployedContracts['UNIQUE_USER']
    rewarder = deployedContracts['rewarder']

    startCommonBal = sdt.balanceOf(COMMON_USER)
    startRareBal = sdt.balanceOf(RARE_USER)
    startUniqueBal = sdt.balanceOf(UNIQUE_USER)

    darkParadise.enter(6_000, commonId, commonUser)
    darkParadise.enter(16_000, rareId, rareUser)
    darkParadise.enter(61_000, uniqueId, uniqueUser)
    assert darkParadise.balanceOf(COMMON_USER) == 6_000
    assert darkParadise.balanceOf(RARE_USER) == 16_000
    assert darkParadise.balanceOf(UNIQUE_USER) == 61_000
    assert darkParadise.totalSupply() == 83_000
    assert sdt.balanceOf(darkParadise.address) == 83_000

    darkParadise.notifyRewardAmount(10_000, rewarder)
    assert sdt.balanceOf(darkParadise.address) == 93_000

    darkParadise.enter(3_000, commonId, commonUser)
    darkParadise.enter(12_000, rareId, rareUser)
    darkParadise.enter(50_000, uniqueId, uniqueUser)
    assert darkParadise.balanceOf(COMMON_USER) == 8_677 # 6000 + 3000 * (83000 / 93000)
    assert darkParadise.balanceOf(RARE_USER) == 26_709 # 16000 + 12000 * (83000 / 93000)
    assert darkParadise.balanceOf(UNIQUE_USER) == 105_623 # 61000 + 50000 * (83000 / 93000)
    assert darkParadise.totalSupply() == 141_009
    assert sdt.balanceOf(darkParadise.address) == 158_000

    darkParadise.notifyRewardAmount(22_000, rewarder)
    assert sdt.balanceOf(darkParadise.address) == 180_000

    darkParadise.leave(4_000, commonUser)
    darkParadise.leave(11_000, rareUser)
    darkParadise.leave(40_000, uniqueUser)
    assert darkParadise.balanceOf(COMMON_USER) == 4_677 # 8677 - 4000
    assert darkParadise.balanceOf(RARE_USER) == 15_709 # 26709 - 11000
    assert darkParadise.balanceOf(UNIQUE_USER) == 65_623 # 105623 - 40000
    assert darkParadise.totalSupply() == 86_009
    assert sdt.balanceOf(COMMON_USER) == startCommonBal - 6000 - 3000 + 5106 # 4000 * 180000 / 141009
    assert sdt.balanceOf(RARE_USER) == startRareBal - 16000 - 12000 + 14041 # 11000 * 180000 / 141009
    assert sdt.balanceOf(UNIQUE_USER) == startUniqueBal - 61000 - 50000 + 51060 # 40000 * 180000 / 141009

def test_burn(deployedContracts):
    darkParadise = deployedContracts['darkParadise']
    deployer = deployedContracts['deployer']
    nft = deployedContracts['nft']
    commonUser = deployedContracts['commonUser']
    COMMON_USER = deployedContracts['COMMON_USER']

    darkParadise.enter(3_000, commonId, commonUser)

    oldNFTSupply = nft.totalSupply(commonId)

    with brownie.reverts('Ownable: caller is not the owner'):
        nft.burn(COMMON_USER, commonId, 1, commonUser)

    with brownie.reverts('StratAccessNFT: NFT being used in strategy'):
        nft.burn(COMMON_USER, commonId, 1, deployer)

    shares = darkParadise.balanceOf(COMMON_USER)
    darkParadise.leave(shares, commonUser)

    nft.burn(COMMON_USER, commonId, 1, deployer)

    assert nft.totalSupply(commonId) == oldNFTSupply - 1
