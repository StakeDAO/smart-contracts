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

    controller = Controller.at(deployed[ENV]['CONTROLLER'])

    DEV = '0x5cAf454Ba92e6F2c929DF14667Ee360eD9fD5b26'

    sender = {'from': '0x9f535E3c63Cd1447164BED4933d1efefBbC97a3f'}

    dev = Contract(DEV)

    devVault = yVault.at('0xd072d3dB1343029087cb9466DE19492b7A1C66FF')

    devStrategy = StrategyBunchyDev.at(
        '0x7D3b52A6ae25545f825bc230f7011Fc97e821911')

    return {"dai": dai, "treasuryVault": treasuryVault, "multisig": multisig, "deployer": deployer, "DAI": DAI, "dev": dev, "SBTC_CRV": SBTC_CRV, "THREE_CRV": THREE_CRV, "EURS_CRV": EURS_CRV, "devVault": devVault, "devStrategy": devStrategy, "sender": sender, "controller": controller}


def test_dev_vault_deposit(deployedContracts):
    dev = deployedContracts['dev']
    devVault = deployedContracts['devVault']
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


def test_dev_vault_earn(deployedContracts):
    deployer = deployedContracts['deployer']
    dev = deployedContracts['dev']
    devVault = deployedContracts['devVault']
    devStrategy = deployedContracts['devStrategy']
    sender = deployedContracts['sender']
    property = devStrategy.property()

    vaultDevBefore = dev.balanceOf(devVault.address)
    propertyDevBefore = dev.balanceOf(property)

    devVault.earn(deployer)

    vaultDevAfter = dev.balanceOf(devVault.address)
    propertyDevAfter = dev.balanceOf(property)

    print("Vault DEV decrease", (vaultDevBefore - vaultDevAfter) / 10**18)

    assert vaultDevBefore - vaultDevAfter > 0
    assert vaultDevBefore - vaultDevAfter == propertyDevAfter - propertyDevBefore


def test_dev_strategy_harvest(deployedContracts):
    deployer = deployedContracts['deployer']
    dev = deployedContracts['dev']
    devVault = deployedContracts['devVault']
    devStrategy = deployedContracts['devStrategy']
    controller = deployedContracts['controller']
    sender = deployedContracts['sender']
    multisig = deployedContracts['multisig']
    property = devStrategy.property()
    DEV_WHALE = '0xe23fe51187a807d56189212591f5525127003bdf'

    chain.sleep(5 * 86400)
    chain.mine(1000)

    vaultDevBefore = dev.balanceOf(devVault.address)
    controllerDevBefore = dev.balanceOf(controller.rewards())
    onlyStratDevB = dev.balanceOf(devStrategy.address)
    strategyDevBefore = devStrategy.balanceOf()

    devStrategy.harvest(multisig)

    vaultDevAfter = dev.balanceOf(devVault.address)
    controllerDevAfter = dev.balanceOf(controller.address)
    onlyStratDevA = dev.balanceOf(devStrategy.address)
    strategyDevAfter = devStrategy.balanceOf()

    assert strategyDevAfter > strategyDevBefore
    assert onlyStratDevB == onlyStratDevA == 0
    assert controllerDevBefore == controllerDevAfter == 0
    assert vaultDevBefore == vaultDevAfter


def test_dev_vault_withdraw(deployedContracts):
    deployer = deployedContracts['deployer']
    dev = deployedContracts['dev']
    devVault = deployedContracts['devVault']
    devStrategy = deployedContracts['devStrategy']
    sender = deployedContracts['sender']
    controller = deployedContracts['controller']
    property = devStrategy.property()
    DEV_WHALE = '0xe23fe51187a807d56189212591f5525127003bdf'

    vaultDevBefore = dev.balanceOf(devVault.address)
    strategyDevBefore = dev.balanceOf(devStrategy.address)
    controllerDevBefore = dev.balanceOf(controller.address)
    senderDevBefore = dev.balanceOf(sender['from'])
    treasuryDevBefore = dev.balanceOf(controller.rewards())

    devVault.withdraw(10000 * 10**18, sender)

    vaultDevAfter = dev.balanceOf(devVault.address)
    strategyDevAfter = dev.balanceOf(devStrategy.address)
    controllerDevAfter = dev.balanceOf(controller.address)
    senderDevAfter = dev.balanceOf(sender['from'])
    treasuryDevAfter = dev.balanceOf(controller.rewards())

    assert treasuryDevAfter > treasuryDevBefore
    assert senderDevAfter > senderDevBefore
    assert controllerDevBefore == controllerDevAfter == 0
    assert strategyDevBefore == strategyDevAfter == 0


def test_dev_vault_withdrawAll(deployedContracts):
    deployer = deployedContracts['deployer']
    dev = deployedContracts['dev']
    devVault = deployedContracts['devVault']
    devStrategy = deployedContracts['devStrategy']
    sender = deployedContracts['sender']
    controller = deployedContracts['controller']
    property = devStrategy.property()
    DEV_WHALE = '0xe23fe51187a807d56189212591f5525127003bdf'

    vaultDevBefore = dev.balanceOf(devVault.address)
    strategyDevBefore = dev.balanceOf(devStrategy.address)
    controllerDevBefore = dev.balanceOf(controller.address)
    senderDevBefore = dev.balanceOf(sender['from'])
    treasuryDevBefore = dev.balanceOf(controller.rewards())

    devVault.withdrawAll(sender)

    vaultDevAfter = dev.balanceOf(devVault.address)
    strategyDevAfter = dev.balanceOf(devStrategy.address)
    controllerDevAfter = dev.balanceOf(controller.address)
    senderDevAfter = dev.balanceOf(sender['from'])
    treasuryDevAfter = dev.balanceOf(controller.rewards())

    assert treasuryDevAfter > treasuryDevBefore
    assert senderDevAfter > senderDevBefore
    assert controllerDevBefore == controllerDevAfter == 0
    assert strategyDevBefore == strategyDevAfter == 0


def test_dev_vault_deposit_withdraw_for_whale(deployedContracts):
    deployer = deployedContracts['deployer']
    dev = deployedContracts['dev']
    devVault = deployedContracts['devVault']
    devStrategy = deployedContracts['devStrategy']
    sender = deployedContracts['sender']
    controller = deployedContracts['controller']
    multisig = deployedContracts['multisig']
    property = devStrategy.property()
    DEV_WHALE = '0xe23fe51187a807d56189212591f5525127003bdf'
    dev_whale = {'from': DEV_WHALE}

    strategyDevBefore = dev.balanceOf(devStrategy.address)
    controllerDevBefore = dev.balanceOf(controller.address)
    senderDevBefore = dev.balanceOf(DEV_WHALE)
    treasuryDevBefore = dev.balanceOf(controller.rewards())

    dev.approve(devVault.address, dev.balanceOf(DEV_WHALE), dev_whale)
    devVault.depositAll(dev_whale)
    devVault.earn(deployer)
    chain.sleep(5 * 86400)
    chain.mine(1000)
    devStrategy.harvest(multisig)
    devVault.withdraw(devVault.balanceOf(DEV_WHALE), dev_whale)

    strategyDevAfter = dev.balanceOf(devStrategy.address)
    controllerDevAfter = dev.balanceOf(controller.address)
    senderDevAfter = dev.balanceOf(DEV_WHALE)
    treasuryDevAfter = dev.balanceOf(controller.rewards())

    assert treasuryDevAfter > treasuryDevBefore
    assert senderDevAfter < senderDevBefore
    assert controllerDevBefore == controllerDevAfter == 0
    assert strategyDevBefore == strategyDevAfter == 0


def test_dev_controller_withdrawAll(deployedContracts):
    deployer = deployedContracts['deployer']
    dev = deployedContracts['dev']
    devVault = deployedContracts['devVault']
    devStrategy = deployedContracts['devStrategy']
    sender = deployedContracts['sender']
    controller = deployedContracts['controller']
    multisig = deployedContracts['multisig']
    property = devStrategy.property()
    DEV_WHALE = '0xe23fe51187a807d56189212591f5525127003bdf'

    vaultDevBefore = dev.balanceOf(devVault.address)
    strategyDevBefore = dev.balanceOf(devStrategy.address)
    controllerDevBefore = dev.balanceOf(controller.address)
    treasuryDevBefore = dev.balanceOf(controller.rewards())

    controller.withdrawAll(dev.address, multisig)

    vaultDevAfter = dev.balanceOf(devVault.address)
    strategyDevAfter = dev.balanceOf(devStrategy.address)
    controllerDevAfter = dev.balanceOf(controller.address)
    treasuryDevAfter = dev.balanceOf(controller.rewards())

    assert treasuryDevAfter == treasuryDevBefore
    assert vaultDevAfter > vaultDevBefore
    assert controllerDevBefore == controllerDevAfter == 0
    assert strategyDevBefore == strategyDevAfter == 0


def test_dev_strategy_withdrawToVault(deployedContracts):
    deployer = deployedContracts['deployer']
    dev = deployedContracts['dev']
    devVault = deployedContracts['devVault']
    devStrategy = deployedContracts['devStrategy']
    sender = deployedContracts['sender']
    controller = deployedContracts['controller']
    multisig = deployedContracts['multisig']
    property = devStrategy.property()
    DEV_WHALE = '0xe23fe51187a807d56189212591f5525127003bdf'

    # cannot test due to brownie's internal issue
    # devStrategy.withdrawToVault(10000 * 10**18, multisig)
