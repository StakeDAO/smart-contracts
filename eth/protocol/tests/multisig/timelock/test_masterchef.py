import pytest
from brownie import *
import typer
import json


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
    DEFAULT_DEPLOYER_ACCOUNT = accounts.load('stakedao-deployer-rug-pull')

    print("DEFAULT_DEPLOYER_ACCOUNT: ", DEFAULT_DEPLOYER_ACCOUNT)

    # Deployed GnosisSafeProxy (mainnet)
    GNOSIS_SAFE_PROXY = deployed[ENV]['GNOSIS_SAFE_PROXY']

    print("GNOSIS_SAFE_PROXY: ", GNOSIS_SAFE_PROXY)

def test_queue_add_pools_to_masterchef(deployedContracts):
    pass


def test_queue_set_pool_alloc_point(deployedContracts):
    pass


def test_exec_set_pool_alloc_point(deployedContracts):
    pass


def test_exec_set_pool_alloc_point(deployedContracts):
    pass
