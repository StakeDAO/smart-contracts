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

    # CRV Token mainnet address
    CRV = deployed[ENV]['CRV']

    print("CRV: ", CRV)

    # sbtcCrv Token mainnet address
    SBTC_CRV = deployed[ENV]['SBTC_CRV']

    print("SBTC_CRV: ", SBTC_CRV)

    # 3Crv Token mainnet address
    THREE_CRV = deployed[ENV]['THREE_CRV']

    print("THREE_CRV: ", THREE_CRV)

    # eursCrv Token mainnet address
    EURS_CRV = deployed[ENV]['EURS_CRV']

    print("EURS_CRV: ", EURS_CRV)

    # TODO: Strategist account
    STRATEGIST = deployed[ENV]['STRATEGIST']

    print("STRATEGIST: ", STRATEGIST)

    # TreasuryVault mainnet address
    CONTROLLER = deployed[ENV]['CONTROLLER']

    print("CONTROLLER: ", CONTROLLER)

    # CurveYCRVVoter mainnet address
    CURVE_YCRV_VOTER = deployed[ENV]['CURVE_YCRV_VOTER']

    print("CURVE_YCRV_VOTER: ", CURVE_YCRV_VOTER)

    # VE_CURVE_VAULT
    VE_CURVE_VAULT = deployed[ENV]['VE_CURVE_VAULT']

    print("VE_CURVE_VAULT: ", VE_CURVE_VAULT)

    # CRV mainnet address
    CRV = deployed[ENV]['CRV']

    print("CRV: ", CRV)

    # STRATEGY_CURVE_3CRV_VOTER_PROXY
    STRATEGY_CURVE_3CRV_VOTER_PROXY = deployed[ENV]['STRATEGY_CURVE_3CRV_VOTER_PROXY']

    print("STRATEGY_CURVE_3CRV_VOTER_PROXY: ", STRATEGY_CURVE_3CRV_VOTER_PROXY)

    # STRATEGY_CURVE_BTC_VOTER_PROXY
    STRATEGY_CURVE_BTC_VOTER_PROXY = deployed[ENV]['STRATEGY_CURVE_BTC_VOTER_PROXY']

    print("STRATEGY_CURVE_BTC_VOTER_PROXY: ", STRATEGY_CURVE_BTC_VOTER_PROXY)

    # EURS_CRV_VAULT
    EURS_CRV_VAULT = deployed[ENV]['EURS_CRV_VAULT']

    print("EURS_CRV_VAULT: ", EURS_CRV_VAULT)

    # THREE_POOL_VAULT
    THREE_POOL_VAULT = "0xB17640796e4c27a39AF51887aff3F8DC0daF9567"

    print("THREE_POOL_VAULT: ", THREE_POOL_VAULT)

    # SBTC_VAULT
    SBTC_VAULT = "0x24129B935AfF071c4f0554882C0D9573F4975fEd"

    print("SBTC_VAULT: ", SBTC_VAULT)

    CURVE_DAO = "0x40907540d8a6C65c637785e8f8B742ae6b0b9968"

    SMART_WALLET_WHITELIST = "0xca719728Ef172d0961768581fdF35CB116e0B7a4"

    deployer = {'from': DEFAULT_DEPLOYER_ACCOUNT}

    multisig = {'from': GNOSIS_SAFE_PROXY}

    # Deploy StrategyProxy
    strategyProxy = StrategyProxy.deploy(deployer)

    controller = Controller.at(CONTROLLER)

    # Deploy StrategyCurveEursCrvVoterProxy
    strategyCurveEursCrvVoterProxy = StrategyCurveEursCrvVoterProxy.deploy(
        controller.address, deployer)

    strategyCurveBTCVoterProxy = StrategyCurveBTCVoterProxy.at(
        STRATEGY_CURVE_BTC_VOTER_PROXY)

    strategyCurve3CrvVoterProxy = StrategyCurve3CrvVoterProxy.at(
        STRATEGY_CURVE_3CRV_VOTER_PROXY)

    oldStrategyCurveEursCrvVoterProxy = StrategyCurveEursCrvVoterProxy.at(
        "0xc8a753B38978aDD5bD26A5D1290Abc6f9f2c4f99")

    veCurve = veCurveVault.at(VE_CURVE_VAULT)

    eursCrvVault = yVault.at(EURS_CRV_VAULT)

    threePoolVault = yVault.at(THREE_POOL_VAULT)

    sbtcCrvVault = yVault.at(SBTC_VAULT)

    curveYCRVVoter = CurveYCRVVoter.at(CURVE_YCRV_VOTER)

    eursCrv = VaultToken.at(EURS_CRV)

    threeCrv = VaultToken.at(THREE_CRV)

    sbtcCrv = VaultToken.at(SBTC_CRV)

    crv = Contract(CRV)

    return {"strategyProxy": strategyProxy, "strategyCurveEursCrvVoterProxy": strategyCurveEursCrvVoterProxy, "deployer": deployer, "STRATEGIST": STRATEGIST, "GNOSIS_SAFE_PROXY": GNOSIS_SAFE_PROXY, "STRATEGY_CURVE_BTC_VOTER_PROXY": STRATEGY_CURVE_BTC_VOTER_PROXY, "GNOSIS_SAFE_PROXY": GNOSIS_SAFE_PROXY, "strategyCurveBTCVoterProxy": strategyCurveBTCVoterProxy, "strategyProxy": strategyProxy, "veCurve": veCurve, "controller": controller, "strategyCurveEursCrvVoterProxy": strategyCurveEursCrvVoterProxy, "eursCrvVault": eursCrvVault, "oldStrategyCurveEursCrvVoterProxy": oldStrategyCurveEursCrvVoterProxy, "curveYCRVVoter": curveYCRVVoter, "eursCrv": eursCrv, "multisig": multisig, "EURS_CRV": EURS_CRV, "strategyCurve3CrvVoterProxy": strategyCurve3CrvVoterProxy, "CURVE_DAO": CURVE_DAO, "SMART_WALLET_WHITELIST": SMART_WALLET_WHITELIST, "threeCrv": threeCrv, "sbtcCrv": sbtcCrv, "threePoolVault": threePoolVault, "sbtcCrvVault": sbtcCrvVault, "crv": crv}


def test_strategyCurveEursCrvVoterProxy_approveStrategy(deployedContracts):
    strategyProxy = deployedContracts["strategyProxy"]
    strategyCurveEursCrvVoterProxy = deployedContracts["strategyCurveEursCrvVoterProxy"]
    deployer = deployedContracts["deployer"]

    # Register strategyCurveEursCrvVoterProxy in StrategyProxy
    strategyProxy.approveStrategy(
        strategyCurveEursCrvVoterProxy.address, deployer)

    assert strategyProxy.strategies(
        strategyCurveEursCrvVoterProxy.address) == True


def test_strategyCurveEursCrvVoterProxy_setProxy(deployedContracts):
    strategyProxy = deployedContracts["strategyProxy"]
    strategyCurveEursCrvVoterProxy = deployedContracts["strategyCurveEursCrvVoterProxy"]
    deployer = deployedContracts["deployer"]

    # set proxy to StrategyProxy
    strategyCurveEursCrvVoterProxy.setProxy(
        strategyProxy.address, deployer)

    assert strategyCurveEursCrvVoterProxy.proxy() == strategyProxy.address


def test_strategyCurveEursCrvVoterProxy_setStrategist(deployedContracts):
    STRATEGIST = deployedContracts["STRATEGIST"]
    strategyCurveEursCrvVoterProxy = deployedContracts["strategyCurveEursCrvVoterProxy"]
    deployer = deployedContracts["deployer"]

    # Transfer strategyCurveEursCrvVoterProxy strategist role to Strategist
    strategyCurveEursCrvVoterProxy.setStrategist(
        STRATEGIST, deployer)

    assert strategyCurveEursCrvVoterProxy.strategist() == STRATEGIST


def test_strategyCurveEursCrvVoterProxy_setGovernance(deployedContracts):
    GNOSIS_SAFE_PROXY = deployedContracts["GNOSIS_SAFE_PROXY"]
    strategyCurveEursCrvVoterProxy = deployedContracts["strategyCurveEursCrvVoterProxy"]
    deployer = deployedContracts["deployer"]

    # Transfer strategyCurveEursCrvVoterProxy governance to Governance (GSP)
    strategyCurveEursCrvVoterProxy.setGovernance(
        GNOSIS_SAFE_PROXY, deployer)

    assert strategyCurveEursCrvVoterProxy.governance() == GNOSIS_SAFE_PROXY


def test_strategyCurveBTCVoterProxy_approveStrategy(deployedContracts):
    strategyProxy = deployedContracts["strategyProxy"]
    strategyCurveBTCVoterProxy = deployedContracts["strategyCurveBTCVoterProxy"]
    deployer = deployedContracts["deployer"]

    # Register strategyCurveBTCVoterProxy in StrategyProxy
    strategyProxy.approveStrategy(strategyCurveBTCVoterProxy.address, deployer)

    assert strategyProxy.strategies(
        strategyCurveBTCVoterProxy.address) == True


def test_strategyCurve3CrvVoterProxy_approveStrategy(deployedContracts):
    strategyProxy = deployedContracts["strategyProxy"]
    strategyCurve3CrvVoterProxy = deployedContracts["strategyCurve3CrvVoterProxy"]
    deployer = deployedContracts["deployer"]

    # Register strategyCurve3CrvVoterProxy in StrategyProxy
    strategyProxy.approveStrategy(
        strategyCurve3CrvVoterProxy.address, deployer)

    assert strategyProxy.strategies(
        strategyCurve3CrvVoterProxy.address) == True


def test_strategyProxy_setGovernance(deployedContracts):
    strategyProxy = deployedContracts["strategyProxy"]
    GNOSIS_SAFE_PROXY = deployedContracts["GNOSIS_SAFE_PROXY"]
    deployer = deployedContracts["deployer"]

    # Transfer StrategyProxy governance to Governance (GSP)
    strategyProxy.setGovernance(GNOSIS_SAFE_PROXY, deployer)

    assert strategyProxy.governance() == GNOSIS_SAFE_PROXY


def test_veCurve_acceptGovernance(deployedContracts):
    veCurve = deployedContracts["veCurve"]
    GNOSIS_SAFE_PROXY = deployedContracts["GNOSIS_SAFE_PROXY"]
    multisig = deployedContracts["multisig"]

    # multisig accept Governance of veCurve vault
    veCurve.acceptGovernance(multisig)

    assert veCurve.governance() == GNOSIS_SAFE_PROXY


def test_veCurve_setFeeDistribution(deployedContracts):
    veCurve = deployedContracts["veCurve"]
    strategyProxy = deployedContracts["strategyProxy"]
    multisig = deployedContracts["multisig"]

    # Set Curve FeeDistribution contract to new strategyProxy
    veCurve.setFeeDistribution(strategyProxy.address, multisig)

    assert veCurve.feeDistribution() == strategyProxy.address


def test_veCurve_setProxy(deployedContracts):
    veCurve = deployedContracts["veCurve"]
    strategyProxy = deployedContracts["strategyProxy"]
    multisig = deployedContracts["multisig"]

    # Set new StrategyProxy
    veCurve.setProxy(strategyProxy.address, multisig)

    assert veCurve.proxy() == strategyProxy.address


def test_strategyCurve3CrvVoterProxy_setProxy(deployedContracts):
    strategyCurve3CrvVoterProxy = deployedContracts["strategyCurve3CrvVoterProxy"]
    strategyProxy = deployedContracts["strategyProxy"]
    multisig = deployedContracts["multisig"]

    # set proxy to new StrategyProxy
    strategyCurve3CrvVoterProxy.setProxy(strategyProxy.address, multisig)

    assert strategyCurve3CrvVoterProxy.proxy() == strategyProxy.address


def test_strategyCurveBTCVoterProxy_setProxy(deployedContracts):
    strategyCurveBTCVoterProxy = deployedContracts["strategyCurveBTCVoterProxy"]
    strategyProxy = deployedContracts["strategyProxy"]
    multisig = deployedContracts["multisig"]

    # set proxy to new StrategyProxy
    strategyCurveBTCVoterProxy.setProxy(strategyProxy.address, multisig)

    assert strategyCurveBTCVoterProxy.proxy() == strategyProxy.address


def test_controller_approveStrategy(deployedContracts):
    controller = deployedContracts["controller"]
    strategyCurveEursCrvVoterProxy = deployedContracts["strategyCurveEursCrvVoterProxy"]
    multisig = deployedContracts["multisig"]
    EURS_CRV = deployedContracts["EURS_CRV"]

    # Approve the strategyCurveEursCrvVoterProxy strategy in Controller
    controller.approveStrategy(
        EURS_CRV, strategyCurveEursCrvVoterProxy.address, multisig)

    assert controller.approvedStrategies(
        EURS_CRV, strategyCurveEursCrvVoterProxy.address) == True


def test_controller_setStrategy(deployedContracts):
    controller = deployedContracts["controller"]
    strategyCurveEursCrvVoterProxy = deployedContracts["strategyCurveEursCrvVoterProxy"]
    oldStrategyCurveEursCrvVoterProxy = deployedContracts["oldStrategyCurveEursCrvVoterProxy"]
    multisig = deployedContracts["multisig"]
    eursCrvVault = deployedContracts["eursCrvVault"]
    EURS_CRV = deployedContracts["EURS_CRV"]
    eursCrv = deployedContracts["eursCrv"]

    totalBalBefore = eursCrvVault.balance()
    vaultBalBefore = eursCrv.balanceOf(eursCrvVault.address)
    oldStratBalBefore = oldStrategyCurveEursCrvVoterProxy.balanceOf()

    # Register strategyCurveEursCrvVoterProxy in Controller
    controller.setStrategy(
        EURS_CRV, strategyCurveEursCrvVoterProxy.address, multisig)

    totalBalAfter = eursCrvVault.balance()
    vaultBalAfter = eursCrv.balanceOf(eursCrvVault.address)
    oldStratBalAfter = oldStrategyCurveEursCrvVoterProxy.balanceOf()

    assert totalBalBefore == totalBalAfter
    assert vaultBalAfter == vaultBalBefore + oldStratBalBefore
    assert vaultBalAfter == totalBalBefore
    assert oldStratBalAfter == 0


def test_controller_revokeStrategy(deployedContracts):
    controller = deployedContracts["controller"]
    strategyCurveEursCrvVoterProxy = deployedContracts["strategyCurveEursCrvVoterProxy"]
    oldStrategyCurveEursCrvVoterProxy = deployedContracts["oldStrategyCurveEursCrvVoterProxy"]
    multisig = deployedContracts["multisig"]
    eursCrvVault = deployedContracts["eursCrvVault"]
    EURS_CRV = deployedContracts["EURS_CRV"]
    eursCrv = deployedContracts["eursCrv"]

    # Revoke old strategyCurveEursCrvVoterProxy in Controller
    controller.revokeStrategy(
        EURS_CRV, oldStrategyCurveEursCrvVoterProxy.address, multisig)

    assert oldStrategyCurveEursCrvVoterProxy.balanceOf() == 0
    assert controller.approvedStrategies(
        EURS_CRV, oldStrategyCurveEursCrvVoterProxy.address) == False


def test_curveYCRVVoter_setStrategy(deployedContracts):
    curveYCRVVoter = deployedContracts["curveYCRVVoter"]
    strategyProxy = deployedContracts["strategyProxy"]
    multisig = deployedContracts["multisig"]

    # Set CurveYCRVVoter strategy to new StrategyProxy
    curveYCRVVoter.setStrategy(strategyProxy.address, multisig)

    assert curveYCRVVoter.strategy() == strategyProxy.address


def test_eursCrvVault_earn(deployedContracts):
    strategyCurveEursCrvVoterProxy = deployedContracts["strategyCurveEursCrvVoterProxy"]
    deployer = deployedContracts["deployer"]
    eursCrvVault = deployedContracts["eursCrvVault"]
    EURS_CRV = deployedContracts["EURS_CRV"]
    eursCrv = deployedContracts["eursCrv"]

    totalBalBefore = eursCrvVault.balance()
    vaultBalBefore = eursCrv.balanceOf(eursCrvVault.address)
    stratBalBefore = strategyCurveEursCrvVoterProxy.balanceOf()

    assert stratBalBefore == 0
    assert totalBalBefore == vaultBalBefore

    # Call earn on eursCrv Vault to transfer the funds to the new strategy
    eursCrvVault.earn(deployer)

    totalBalAfter = eursCrvVault.balance()
    vaultBalAfter = eursCrv.balanceOf(eursCrvVault.address)
    stratBalAfter = strategyCurveEursCrvVoterProxy.balanceOf()

    assert totalBalBefore == totalBalAfter
    assert stratBalAfter > 0
    assert vaultBalBefore > vaultBalAfter
    assert vaultBalBefore == vaultBalAfter + stratBalAfter


def test_strategyCurveEursCrvVoterProxy_harvest(deployedContracts):
    strategyCurveEursCrvVoterProxy = deployedContracts["strategyCurveEursCrvVoterProxy"]
    deployer = deployedContracts["deployer"]
    eursCrvVault = deployedContracts["eursCrvVault"]
    multisig = deployedContracts["multisig"]

    totalBalBefore = eursCrvVault.balance()
    stratBalBefore = strategyCurveEursCrvVoterProxy.balanceOf()
    earnedBefore = strategyCurveEursCrvVoterProxy.earned()

    assert earnedBefore == 0

    chain.mine(1000)

    strategyCurveEursCrvVoterProxy.harvest(multisig)

    totalBalAfter = eursCrvVault.balance()
    stratBalAfter = strategyCurveEursCrvVoterProxy.balanceOf()
    earnedAfter = strategyCurveEursCrvVoterProxy.earned()

    log("Total eursCrv Earned in 1000 blocks: " + str(earnedAfter))
    log("Change in total eursCrv in Vault+Strategy+Gauge: " +
        str(totalBalAfter-totalBalBefore))
    log("Change in total eursCrv in Strategy+Gauge: " +
        str(stratBalAfter-stratBalBefore))

    assert earnedAfter > 0
    assert totalBalAfter > totalBalBefore
    assert stratBalAfter > stratBalBefore


def test_whitelist(deployedContracts):
    curveYCRVVoter = deployedContracts["curveYCRVVoter"]
    crv = deployedContracts["crv"]
    SMART_WALLET_WHITELIST = deployedContracts["SMART_WALLET_WHITELIST"]
    CURVE_DAO = deployedContracts["CURVE_DAO"]
    multisig = deployedContracts["multisig"]

    # Whitelist CurveYCRVVoter
    smartWalletWhitelist = Contract(SMART_WALLET_WHITELIST)
    smartWalletWhitelist.approveWallet(
        curveYCRVVoter.address, {'from': CURVE_DAO})

    # Send some Crv to CurveYCRVVoter (if no CRV in CurveYCRVVoter)
    crv.transfer(curveYCRVVoter.address, 10**18,
                 {'from': '0xe3997288987E6297Ad550A69B31439504F513267'})

    FOUR_YEARS_IN_SEC = 4 * 365 * 86400

    # Create a CRV lock
    curveYCRVVoter.createLock(10**18, chain.time()+FOUR_YEARS_IN_SEC, multisig)


def test_strategyCurve3CrvVoterProxy_harvest(deployedContracts):
    strategyCurve3CrvVoterProxy = deployedContracts["strategyCurve3CrvVoterProxy"]
    deployer = deployedContracts["deployer"]
    threePoolVault = deployedContracts["threePoolVault"]
    multisig = deployedContracts["multisig"]

    totalBalBefore = threePoolVault.balance()
    stratBalBefore = strategyCurve3CrvVoterProxy.balanceOf()
    earnedBefore = strategyCurve3CrvVoterProxy.earned()

    assert earnedBefore == 0

    chain.mine(1000)

    strategyCurve3CrvVoterProxy.harvest(multisig)

    totalBalAfter = threePoolVault.balance()
    stratBalAfter = strategyCurve3CrvVoterProxy.balanceOf()
    earnedAfter = strategyCurve3CrvVoterProxy.earned()

    log("Total 3Crv Earned in 1000 blocks: " + str(earnedAfter))
    log("Change in total 3Crv in Vault+Strategy+Gauge: " +
        str(totalBalAfter-totalBalBefore))
    log("Change in total 3Crv in Strategy+Gauge: " +
        str(stratBalAfter-stratBalBefore))

    assert earnedAfter > 0
    assert totalBalAfter > totalBalBefore
    assert stratBalAfter > stratBalBefore


def test_strategyCurveBTCVoterProxy_harvest(deployedContracts):
    strategyCurveBTCVoterProxy = deployedContracts["strategyCurveBTCVoterProxy"]
    deployer = deployedContracts["deployer"]
    sbtcCrvVault = deployedContracts["sbtcCrvVault"]
    multisig = deployedContracts["multisig"]

    totalBalBefore = sbtcCrvVault.balance()
    stratBalBefore = strategyCurveBTCVoterProxy.balanceOf()
    earnedBefore = strategyCurveBTCVoterProxy.earned()

    assert earnedBefore == 0

    chain.mine(1000)

    strategyCurveBTCVoterProxy.harvest(multisig)

    totalBalAfter = sbtcCrvVault.balance()
    stratBalAfter = strategyCurveBTCVoterProxy.balanceOf()
    earnedAfter = strategyCurveBTCVoterProxy.earned()

    log("Total sbtcCrv Earned in 1000 blocks: " + str(earnedAfter))
    log("Change in total sbtcCrv in Vault+Strategy+Gauge: " +
        str(totalBalAfter-totalBalBefore))
    log("Change in total sbtcCrv in Strategy+Gauge: " +
        str(stratBalAfter-stratBalBefore))

    assert earnedAfter > 0
    assert totalBalAfter > totalBalBefore
    assert stratBalAfter > stratBalBefore


def log(msg):
    msg = typer.style(msg, fg=typer.colors.GREEN, bold=True)
    typer.echo(msg)
