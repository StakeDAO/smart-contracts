import pytest
from brownie import *
import typer
import json
import brownie

commonNFT = 1
rareNFT = 212
uniqueNFT = 222

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
    DEPLOYER = accounts[0]
    deployer = {'from': DEPLOYER}

    SD_NFT = deployed[ENV]['SD_NFT']
    nft = StakeDaoNFT.at(SD_NFT)

    PROXY_REGISTRY = deployed[ENV]['OPENSEA_PROXY_REGISTRY']

    nftBoosterVault = NFTBoosterVault.deploy(nft.address, deployer)

    COMMON_OWNER = '0x4b502a08bc54c05772b2c63469e366c2e78459ed'
    commonOwner = {'from': COMMON_OWNER}

    RARE_OWNER = '0xb19d9d2949918867340605a971774fe8b7e52c2c'
    rareOwner = {'from': RARE_OWNER}

    UNIQUE_OWNER = '0xb19d9d2949918867340605a971774fe8b7e52c2c'
    uniqueOwner = {'from': UNIQUE_OWNER}

    TESTER_1 = accounts[1]
    tester1 = {'from': TESTER_1}

    TESTER_2 = accounts[2]
    tester2 = {'from': TESTER_2}

    nft.safeTransferFrom(COMMON_OWNER, TESTER_1, commonNFT, 1, "", commonOwner)
    nft.safeTransferFrom(RARE_OWNER, TESTER_1, rareNFT, 1, "", rareOwner)
    nft.safeTransferFrom(UNIQUE_OWNER, TESTER_2, uniqueNFT, 1, "", uniqueOwner)

    nft.setApprovalForAll(nftBoosterVault.address, True, tester1)
    nft.setApprovalForAll(nftBoosterVault.address, True, tester2)

    return {"deployer": deployer,
            "DEPLOYER": DEPLOYER,
            "TESTER_1": TESTER_1,
            "tester1": tester1,
            "TESTER_2": TESTER_2,
            "tester2": tester2,
            "PROXY_REGISTRY": PROXY_REGISTRY,
            "nft": nft,
            "nftBoosterVault": nftBoosterVault}

def test_constructor(deployedContracts):
    nft = deployedContracts["nft"]
    nftBoosterVault = deployedContracts["nftBoosterVault"]
    DEPLOYER = deployedContracts["DEPLOYER"]

    nftAddress = nftBoosterVault.getNFTAddress()
    assert nftAddress == nft.address

    owner = nftBoosterVault.owner()
    assert owner == DEPLOYER

def test_normal_stake_unstake(deployedContracts):
    nft = deployedContracts["nft"]
    nftBoosterVault = deployedContracts["nftBoosterVault"]
    TESTER_1 = deployedContracts["TESTER_1"]
    tester1 = deployedContracts["tester1"]
    TESTER_2 = deployedContracts["TESTER_2"]
    tester2 = deployedContracts["tester2"]

    nftBoosterVault.stake(commonNFT, tester1)
    stakedNFT = nftBoosterVault.getStakedNFT(TESTER_1)
    assert stakedNFT == commonNFT

    nftBoosterVault.stake(uniqueNFT, tester2)
    stakedNFT = nftBoosterVault.getStakedNFT(TESTER_2)
    assert stakedNFT == uniqueNFT

    nftBoosterVault.unstake(tester1)
    stakedNFT = nftBoosterVault.getStakedNFT(TESTER_1)
    assert stakedNFT == 0

    nftBoosterVault.unstake(tester2)
    stakedNFT = nftBoosterVault.getStakedNFT(TESTER_2)
    assert stakedNFT == 0

def test_double_stake(deployedContracts):
    nft = deployedContracts["nft"]
    nftBoosterVault = deployedContracts["nftBoosterVault"]
    tester1 = deployedContracts["tester1"]

    nftBoosterVault.stake(commonNFT, tester1)

    with brownie.reverts("already staked"):
        nftBoosterVault.stake(rareNFT, tester1)

    nftBoosterVault.unstake(tester1)

def test_unstake_before_stake(deployedContracts):
    nft = deployedContracts["nft"]
    nftBoosterVault = deployedContracts["nftBoosterVault"]
    tester1 = deployedContracts["tester1"]

    with brownie.reverts("not staked"):
        nftBoosterVault.unstake(tester1)

def test_claim_locked(deployedContracts):
    nft = deployedContracts["nft"]
    nftBoosterVault = deployedContracts["nftBoosterVault"]
    tester1 = deployedContracts["tester1"]
    TESTER_1 = deployedContracts["TESTER_1"]
    tester2 = deployedContracts["tester2"]
    TESTER_2 = deployedContracts["TESTER_2"]
    deployer = deployedContracts["deployer"]
    DEPLOYER = deployedContracts["DEPLOYER"]

    nft.safeTransferFrom(TESTER_1, nftBoosterVault.address, commonNFT, 1, "", tester1)
    nft.safeTransferFrom(TESTER_1, nftBoosterVault.address, rareNFT, 1, "", tester1)
    nft.safeTransferFrom(TESTER_2, nftBoosterVault.address, uniqueNFT, 1, "", tester2)

    nftBoosterVault.claimLockedNFTs([commonNFT, rareNFT, uniqueNFT], [1, 1, 1], deployer)

    nft.safeTransferFrom(DEPLOYER, TESTER_1, commonNFT, 1, "", deployer)
    nft.safeTransferFrom(DEPLOYER, TESTER_1, rareNFT, 1, "", deployer)
    nft.safeTransferFrom(DEPLOYER, TESTER_2, uniqueNFT, 1, "", deployer)

def test_send_random_nft(deployedContracts):
    nft = deployedContracts["nft"]
    nftBoosterVault = deployedContracts["nftBoosterVault"]
    tester1 = deployedContracts["tester1"]
    TESTER_1 = deployedContracts["TESTER_1"]
    PROXY_REGISTRY = deployedContracts["PROXY_REGISTRY"]

    randNFT = StakeDaoNFT.deploy(PROXY_REGISTRY, tester1)
    randNFT.create(1, 1, "", "", tester1)

    with brownie.reverts("nft not accepted"):
        randNFT.safeTransferFrom(TESTER_1, nftBoosterVault.address, 1, 1, "", tester1)
