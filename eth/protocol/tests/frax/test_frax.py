import pytest
from brownie import *
import typer
import json

# tests written in /sd-convex repo

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

    GNOSIS_SAFE_PROXY = deployed[ENV]['GNOSIS_SAFE_PROXY']

    TREASURY_VAULT = deployed[ENV]['TREASURY_VAULT']
    treasuryVault = Contract(TREASURY_VAULT)

    SBTC_CRV = deployed[ENV]['SBTC_CRV']

    THREE_CRV = deployed[ENV]['THREE_CRV']

    EURS_CRV = deployed[ENV]['EURS_CRV']

    DAI = deployed[ENV]['DAI']
    dai = Contract(DAI)

    VESTING_ESCROW = deployed[ENV]['VESTING_ESCROW']

    ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"

    deployer = {'from': DEFAULT_DEPLOYER_ACCOUNT}

    multisig = {'from': GNOSIS_SAFE_PROXY}

    CONTROLLER = deployed[ENV]['CONTROLLER']
    controller = Controller.at(CONTROLLER)

    DEV = '0x5cAf454Ba92e6F2c929DF14667Ee360eD9fD5b26'
    PROXY = '0xF34Ae3C7515511E29d8Afe321E67Bdf97a274f1A'

    sender = {'from': '0x9f535E3c63Cd1447164BED4933d1efefBbC97a3f'}

    dev = Contract(DEV)

    vault = Vault.at('0x99780beAdd209cc3c7282536883Ef58f4ff4E52F')
    strat = StrategyFrxConvex.deploy(CONTROLLER, PROXY, deployer)
    WHALE = '0x07A75Ba044cDAaa624aAbAD27CB95C42510AF4B5'
    whale = {'from': WHALE}
    vault.deposit(100_000 * 10**18, whale)

    return {"dai": dai, "treasuryVault": treasuryVault, "multisig": multisig, "deployer": deployer, "DAI": DAI, "vault": vault, "SBTC_CRV": SBTC_CRV, "THREE_CRV": THREE_CRV, "EURS_CRV": EURS_CRV, "devVault": devVault, "devStrategy": devStrategy, "sender": sender, "controller": controller}


def test_frax_vault_deposit(deployedContracts):
    dev = deployedContracts['dev']
    vault = deployedContracts['vault']
    devStrategy = deployedContracts['devStrategy']
    sender = deployedContracts['sender']

    shareBefore = devVault.balanceOf(sender['from'])
    senderDevBefore = dev.balanceOf(sender['from'])
    vaultDevBefore = dev.balanceOf(devVault.address)

    dev.approve(devVault.address, dev.balanceOf(sender['from']), sender)
    devVault.deposit(dev.balanceOf(sender['from']), sender)

    shareAfter = devVault.balanceOf(sender['from'])
    senderDevAfter = dev.balanceOf(sender['from'])
    vaultDevAfter = dev.balanceOf(devVault.address)

    print("Minted shares", (shareAfter - shareBefore) / 10**18)

    assert shareAfter - shareBefore > 0
    assert senderDevBefore - senderDevAfter > 0
    assert senderDevBefore - senderDevAfter == vaultDevAfter - vaultDevBefore

    # tests written in /sd-convex repo
