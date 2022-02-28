import pytest
from brownie import *
import typer
import json
import brownie


@pytest.fixture(scope="module", autouse=True)
def deployedContracts():

    deployed = open("config.json", "r")
    try:
        deployed = json.loads(deployed.read())
    except:
        deployed = {}

    merkleDistribution = open("merkle-distribution.json", "r")
    try:
        merkleDistribution = json.loads(merkleDistribution.read())
    except:
        merkleDistribution = {}

    ENV = ""
    if (network.chain.id == 1):
        ENV = "prod"
    else:
        ENV = "dev"

    # account used for executing transactions
    DEFAULT_DEPLOYER_ACCOUNT = accounts[0]
    deployer = {'from': DEFAULT_DEPLOYER_ACCOUNT}

    distributor = MerkleDistributorSdt.deploy(
      DEFAULT_DEPLOYER_ACCOUNT,
      DEFAULT_DEPLOYER_ACCOUNT,
      deployer
    )
    distributor.proposeMerkleRoot(merkleDistribution["merkleRoot"], deployer)
    distributor.reviewPendingMerkleRoot(True, deployer)

    SDT = deployed[ENV]['SDT']
    sdt = Contract(SDT)

    SDT_WHALE = '0xc78fa2af0ca7990bb5ff32c9a728125be58cf247'
    sdtWhale = {'from': SDT_WHALE}

    bal = sdt.balanceOf(SDT_WHALE)
    print('SDT_WHALE', bal)
    print('tokenTotal', merkleDistribution["tokenTotal"])

    sdt.transfer(distributor.address, merkleDistribution["tokenTotal"], sdtWhale)

    return {
      "deployer": deployer,
      "SDT": SDT,
      "sdt": sdt,
      "distributor": distributor,
      "merkleDistribution": merkleDistribution
    }


def test_claim(deployedContracts):
    sdt = deployedContracts['sdt']
    distributor = deployedContracts['distributor']
    merkleDistribution = deployedContracts['merkleDistribution']

    CLAIM0 = merkleDistribution["claims"][0]
    CLAIMER = CLAIM0["address"]
    claimer = {"from": CLAIMER}

    bal = sdt.balanceOf(CLAIMER)

    distributor.claim(0, CLAIM0["index"], CLAIM0["amount"], CLAIM0["proof"], claimer)

    bal2 = sdt.balanceOf(CLAIMER)
    print(bal2 - bal, CLAIM0["amount"])
    assert (bal2 - bal == CLAIM0["amount"])
