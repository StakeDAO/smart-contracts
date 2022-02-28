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

    SDT = deployed[ENV]['SDT']
    sdt = Contract(SDT)

    DAI = deployed[ENV]['DAI']
    dai = Contract(DAI)

    USDC = '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48'
    usdc = FiatTokenV2_1.at(USDC)

    USDC_WHALE = '0x55fe002aeff02f77364de339a1292923a15844b8'
    usdc_whale = {'from': USDC_WHALE}

    ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"

    DYDXERC3156 = "0x6bdC1FCB2F13d1bA9D26ccEc3983d5D4bf318693"
    TIP_JAR = "0x5312B0d160E16feeeec13437a0053009e7564287"

    deployer = {'from': DEFAULT_DEPLOYER_ACCOUNT}

    multisig = {'from': GNOSIS_SAFE_PROXY}
    # random 2nd argument for testing
    darkParadise = DarkParadise.deploy(
        SDT, '0x87535b160E251167FB7abE239d2467d1127219E4', deployer)

    deathGod = DeathGod.deploy(
        DEFAULT_DEPLOYER_ACCOUNT, darkParadise.address, DYDXERC3156, TIP_JAR, deployer)

    # set governance to multisig later

    usdc.transfer(deathGod.address, 3000 * 10**6, usdc_whale)

    return {"dai": dai, "treasuryVault": treasuryVault, "multisig": multisig, "deployer": deployer, "DAI": DAI, "SDT": SDT, "darkParadise": darkParadise, "deathGod": deathGod, "USDC_WHALE": USDC_WHALE, "usdc_whale": usdc_whale, "sdt": sdt, "usdc": usdc, "ZERO_ADDRESS": ZERO_ADDRESS}


def test_liquidateOnAave(deployedContracts):
    deployer = deployedContracts["deployer"]
    darkParadise = deployedContracts["darkParadise"]
    deathGod = deployedContracts['deathGod']
    usdc = deployedContracts['usdc']
    sdt = deployedContracts['sdt']
    usdc_whale = deployedContracts['usdc_whale']
    ZERO_ADDRESS = deployedContracts['ZERO_ADDRESS']

    WETH = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
    PLEB = "0x23f7c7d09f1d9fb6d182e910ccaaed37ddd87429"
    DEBT_TO_COVER = "2533977845"

    zeroAddress = accounts.at(ZERO_ADDRESS, force=True)
    # usdc.transfer(deathGod.address, 100_000 * 10**6, usdc_whale)

    ethB = zeroAddress.balance()
    usdcBefore = usdc.balanceOf(deathGod.address)
    deathGod.liquidateOnAave(
        WETH, usdc.address, PLEB, DEBT_TO_COVER, False, 10, deployer)

    usdcAfter = usdc.balanceOf(deathGod.address)
    ethA = zeroAddress.balance()

    print("DIFF", (usdcAfter - usdcBefore) / 10**6)
    print("MINER_DIFF_ETH", (ethA - ethB) / 10**18)


# def test_sendSDTToDarkParadise(deployedContracts):
#     deployer = deployedContracts["deployer"]
#     darkParadise = deployedContracts["darkParadise"]
#     deathGod = deployedContracts['deathGod']
#     usdc = deployedContracts['usdc']
#     sdt = deployedContracts['sdt']
#     usdc_whale = deployedContracts['usdc_whale']
#     ZERO_ADDRESS = deployedContracts['ZERO_ADDRESS']

#     zeroAddress = accounts.at(ZERO_ADDRESS, force=True)
#     usdc.transfer(deathGod.address, 100_000 * 10**6, usdc_whale)

#     eth0B = accounts[0].balance()
#     ethB = zeroAddress.balance()
#     sdtBefore = sdt.balanceOf(darkParadise.address)
#     deathGod.sendSDTToDarkParadise(
#         usdc.address, 100_000 * 10**6, {'from': accounts[0], 'value': 3 * 10**18})
#     sdtAfter = sdt.balanceOf(darkParadise.address)
#     ethA = zeroAddress.balance()
#     eth0A = accounts[0].balance()

#     print("DIFF", (sdtAfter - sdtBefore) / 10**18)
#     print("DIFF_ETH", (ethA - ethB) / 10**18)
#     print("DIFF_ETH_0", (eth0A - eth0B) / 10**18)
    # print("CHAIN", chain[12470918])


# def test_flashBorrow(deployedContracts):
#     deployer = deployedContracts["deployer"]
#     deathGod = deployedContracts['deathGod']
#     usdc = deployedContracts['usdc']

#     usdcBefore = usdc.balanceOf(deathGod.address)
#     deathGod.flashBorrow(usdc.address, 100_000 * 10**6, deployer)
#     usdcAfter = usdc.balanceOf(deathGod.address)

#     print("DIFF", usdcBefore - usdcAfter)
#     assert usdcBefore - usdcAfter == 2


# def test_tipMinerInToken(deployedContracts):
#     deployer = deployedContracts["deployer"]
#     darkParadise = deployedContracts["darkParadise"]
#     deathGod = deployedContracts['deathGod']
#     usdc = deployedContracts['usdc']
#     sdt = deployedContracts['sdt']
#     usdc_whale = deployedContracts['usdc_whale']
#     ZERO_ADDRESS = deployedContracts['ZERO_ADDRESS']

#     zeroAddress = accounts.at(ZERO_ADDRESS, force=True)
#     usdc.transfer(deathGod.address, 100_000 * 10**6, usdc_whale)

#     eth0B = accounts[0].balance()
#     ethB = zeroAddress.balance()
#     deathGod.tipMinerInToken(
#         usdc.address, 5000 * 10**6, "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", {'from': accounts[0]})
#     ethA = zeroAddress.balance()
#     eth0A = accounts[0].balance()

#     print("DIFF_ETH", (ethA - ethB) / 10**18)
#     print("DIFF_ETH_0", (eth0A - eth0B) / 10**18)
    # print("CHAIN", chain[12470918])
