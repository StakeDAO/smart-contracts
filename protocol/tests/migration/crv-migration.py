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

    # Strategist account
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

   # TREASURY_VAULT
    TREASURY_VAULT = deployed[ENV]['TREASURY_VAULT']

    print("TREASURY_VAULT: ", TREASURY_VAULT)

    # CRV mainnet address
    CRV = deployed[ENV]['CRV']

    print("CRV: ", CRV)

    SNX = "0xC011a73ee8576Fb46F5E1c5751cA3B9Fe0af2a6F"

    print("SNX: ", SNX)

    EURS = "0xdB25f211AB05b1c97D595516F45794528a807ad8"

    print("EURS: ", EURS)

    # STRATEGY_CURVE_3CRV_VOTER_PROXY
    STRATEGY_CURVE_3CRV_VOTER_PROXY = deployed[ENV]['STRATEGY_CURVE_3CRV_VOTER_PROXY']

    print("STRATEGY_CURVE_3CRV_VOTER_PROXY: ", STRATEGY_CURVE_3CRV_VOTER_PROXY)

    # STRATEGY_CURVE_BTC_VOTER_PROXY
    STRATEGY_CURVE_BTC_VOTER_PROXY = deployed[ENV]['STRATEGY_CURVE_BTC_VOTER_PROXY']

    print("STRATEGY_CURVE_BTC_VOTER_PROXY: ", STRATEGY_CURVE_BTC_VOTER_PROXY)

    # CONTROLLER
    CONTROLLER = deployed[ENV]['CONTROLLER']

    print("CONTROLLER: ", CONTROLLER)

    # EURS_CRV_VAULT
    EURS_CRV_VAULT = deployed[ENV]['EURS_CRV_VAULT']

    print("EURS_CRV_VAULT: ", EURS_CRV_VAULT)

    # THREE_POOL_VAULT
    THREE_POOL_VAULT = "0xB17640796e4c27a39AF51887aff3F8DC0daF9567"

    print("THREE_POOL_VAULT: ", THREE_POOL_VAULT)

    # SBTC_VAULT
    SBTC_VAULT = "0x24129B935AfF071c4f0554882C0D9573F4975fEd"

    print("SBTC_VAULT: ", SBTC_VAULT)

    OLD_STRATEGY_CURVE_EURS_CRV_VOTER_PROXY = "0xa69cfa7F5e7Bcd9b4862D2660d8C9D336D8Ab900"

    OLD_CURVE_YCRV_VOTER = "0x96032427893A22dd2a8FDb0e5fE09abEfc9E4444"

    VOTING_ESCROW = "0x5f3b5DfEb7B28CDbD7FAba78963EE202a494e2A2"

    # Old StrategyCurve3CrvVoterProxy
    oldStrategyCurveEursCrvVoterProxy = StrategyCurveEursCrvVoterProxy.at(
        OLD_STRATEGY_CURVE_EURS_CRV_VOTER_PROXY)

    print("Old StrategyCurveEursCrvVoterProxy: ",
          oldStrategyCurveEursCrvVoterProxy.address)

    deployer = {'from': DEFAULT_DEPLOYER_ACCOUNT}

    multisig = {'from': GNOSIS_SAFE_PROXY}

    controller = Controller.at(CONTROLLER)

    treasuryVault = TreasuryVault.at(TREASURY_VAULT)

    # Deploy StrategyCurveEursCrvVoterProxy
    strategyCurveEursCrvVoterProxy = StrategyCurveEursCrvVoterProxy.deploy(
        controller.address, deployer)

    # Deploy StrategyProxy
    strategyProxy = StrategyProxy.deploy(deployer)

    # Deploy WhitehatStrategyProxy
    whitehatStrategyProxy = WhitehatStrategyProxy.deploy(deployer)

    strategyCurveBTCVoterProxy = StrategyCurveBTCVoterProxy.at(
        STRATEGY_CURVE_BTC_VOTER_PROXY)

    strategyCurve3CrvVoterProxy = StrategyCurve3CrvVoterProxy.at(
        STRATEGY_CURVE_3CRV_VOTER_PROXY)

    veCurve = veCurveVault.at(VE_CURVE_VAULT)

    eursCrvVault = yVault.at(EURS_CRV_VAULT)

    threePoolVault = yVault.at(THREE_POOL_VAULT)

    sbtcCrvVault = yVault.at(SBTC_VAULT)

    oldCurveYCRVVoter = CurveYCRVVoter.at(OLD_CURVE_YCRV_VOTER)

    curveYCRVVoter = CurveYCRVVoter.at(CURVE_YCRV_VOTER)

    eursCrv = VaultToken.at(EURS_CRV)

    threeCrv = VaultToken.at(THREE_CRV)

    sbtcCrv = VaultToken.at(SBTC_CRV)

    snx = Contract(SNX)

    eurs = Contract(EURS)

    crv = Contract(CRV)

    votingEscrow = Contract(VOTING_ESCROW)

    return {"treasuryVault": treasuryVault, "controller": controller, "votingEscrow": votingEscrow, "snx": snx, "eurs": eurs, "whitehatStrategyProxy": whitehatStrategyProxy, "strategyProxy": strategyProxy, "strategyCurveEursCrvVoterProxy": strategyCurveEursCrvVoterProxy, "deployer": deployer, "STRATEGIST": STRATEGIST, "GNOSIS_SAFE_PROXY": GNOSIS_SAFE_PROXY, "STRATEGY_CURVE_BTC_VOTER_PROXY": STRATEGY_CURVE_BTC_VOTER_PROXY, "GNOSIS_SAFE_PROXY": GNOSIS_SAFE_PROXY, "strategyCurveBTCVoterProxy": strategyCurveBTCVoterProxy, "strategyProxy": strategyProxy, "veCurve": veCurve, "controller": controller, "strategyCurveEursCrvVoterProxy": strategyCurveEursCrvVoterProxy, "eursCrvVault": eursCrvVault, "oldStrategyCurveEursCrvVoterProxy": oldStrategyCurveEursCrvVoterProxy, "oldCurveYCRVVoter": oldCurveYCRVVoter, "eursCrv": eursCrv, "multisig": multisig, "EURS_CRV": EURS_CRV, "strategyCurve3CrvVoterProxy": strategyCurve3CrvVoterProxy, "threeCrv": threeCrv, "sbtcCrv": sbtcCrv, "threePoolVault": threePoolVault, "sbtcCrvVault": sbtcCrvVault, "crv": crv, "curveYCRVVoter": curveYCRVVoter}


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
    vaultBalBefore = eursCrvBal(deployedContracts, eursCrvVault.address)
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


def test_strategyProxy_ifTokenGetStuckInProxy(deployedContracts):
    curveYCRVVoter = deployedContracts["curveYCRVVoter"]
    strategyProxy = deployedContracts["strategyProxy"]
    strategyCurveEursCrvVoterProxy = deployedContracts["strategyCurveEursCrvVoterProxy"]
    snx = deployedContracts["snx"]
    multisig = deployedContracts["multisig"]

    strategyBalBefore = snxBal(
        deployedContracts, strategyCurveEursCrvVoterProxy)
    curveYCRVVoterBalBefore = snxBal(
        deployedContracts, curveYCRVVoter)

    assert strategyBalBefore == 0
    assert curveYCRVVoterBalBefore > 0
    assert snxBal(deployedContracts, strategyProxy) == 0

    strategyProxy.ifTokenGetStuckInProxy(
        snx.address, strategyCurveEursCrvVoterProxy.address, multisig)

    strategyBalAfter = snxBal(
        deployedContracts, strategyCurveEursCrvVoterProxy)
    curveYCRVVoterBalAfter = snxBal(
        deployedContracts, curveYCRVVoter)

    assert curveYCRVVoterBalAfter == 0
    assert curveYCRVVoterBalBefore == strategyBalAfter
    assert snxBal(deployedContracts, strategyProxy) == 0

    log("SNX Rescued: "+str(strategyBalAfter/10**18))


def test_eursCrvVault_earn(deployedContracts):
    strategyCurveEursCrvVoterProxy = deployedContracts["strategyCurveEursCrvVoterProxy"]
    deployer = deployedContracts["deployer"]
    eursCrvVault = deployedContracts["eursCrvVault"]
    EURS_CRV = deployedContracts["EURS_CRV"]
    eursCrv = deployedContracts["eursCrv"]
    strategyProxy = deployedContracts["strategyProxy"]
    curveYCRVVoter = deployedContracts["curveYCRVVoter"]
    controller = deployedContracts["controller"]

    totalBalBefore = eursCrvVault.balance()
    vaultBalBefore = eursCrvBal(deployedContracts, eursCrvVault.address)
    stratBalBefore = strategyCurveEursCrvVoterProxy.balanceOf()

    assert stratBalBefore == 0
    assert totalBalBefore == vaultBalBefore

    # Call earn on eursCrv Vault to transfer the funds to the new strategy
    eursCrvVault.earn(deployer)

    totalBalAfter = eursCrvVault.balance()
    vaultBalAfter = eursCrvBal(deployedContracts, eursCrvVault.address)
    stratBalAfter = strategyCurveEursCrvVoterProxy.balanceOf()

    assert totalBalBefore == totalBalAfter
    assert stratBalAfter > 0
    assert vaultBalBefore > vaultBalAfter
    assert vaultBalBefore == vaultBalAfter + stratBalAfter

    assert crvBal(deployedContracts, strategyCurveEursCrvVoterProxy) == 0
    assert eursCrvBal(deployedContracts, strategyCurveEursCrvVoterProxy) == 0
    assert eursBal(deployedContracts, strategyCurveEursCrvVoterProxy) == 0
    assert snxBal(deployedContracts, strategyCurveEursCrvVoterProxy) > 0

    assert crvBal(deployedContracts, strategyProxy) == 0
    assert eursCrvBal(deployedContracts, strategyProxy) == 0
    assert eursBal(deployedContracts, strategyProxy) == 0
    assert snxBal(deployedContracts, strategyProxy) == 0

    assert crvBal(deployedContracts, curveYCRVVoter) == 0
    assert eursCrvBal(deployedContracts, curveYCRVVoter) == 0
    assert eursBal(deployedContracts, curveYCRVVoter) == 0
    assert snxBal(deployedContracts, curveYCRVVoter) == 0

    assert crvBal(deployedContracts, controller) == 0
    assert eursCrvBal(deployedContracts, controller) == 0
    assert eursBal(deployedContracts, controller) == 0
    assert snxBal(deployedContracts, controller) == 0


def test_strategyCurveEursCrvVoterProxy_harvest(deployedContracts):
    strategyCurveEursCrvVoterProxy = deployedContracts["strategyCurveEursCrvVoterProxy"]
    deployer = deployedContracts["deployer"]
    eursCrvVault = deployedContracts["eursCrvVault"]
    multisig = deployedContracts["multisig"]
    strategyProxy = deployedContracts["strategyProxy"]
    curveYCRVVoter = deployedContracts["curveYCRVVoter"]
    votingEscrow = deployedContracts["votingEscrow"]
    controller = deployedContracts["controller"]
    treasuryVault = deployedContracts["treasuryVault"]

    chain.mine(1000)

    totalBalBefore = eursCrvVault.balance()
    stratBalBefore = strategyCurveEursCrvVoterProxy.balanceOf()
    earnedBefore = strategyCurveEursCrvVoterProxy.earned()
    lockedBefore = votingEscrow.balanceOf(curveYCRVVoter.address)
    treasuryVaultBalBefore = eursCrvBal(
        deployedContracts, treasuryVault.address)

    assert earnedBefore == 0

    strategyCurveEursCrvVoterProxy.harvest(multisig)

    totalBalAfter = eursCrvVault.balance()
    stratBalAfter = strategyCurveEursCrvVoterProxy.balanceOf()
    earnedAfter = strategyCurveEursCrvVoterProxy.earned()
    lockedAfter = votingEscrow.balanceOf(curveYCRVVoter.address)
    treasuryVaultBalAfter = eursCrvBal(
        deployedContracts, treasuryVault.address)

    log("Total eursCrv Earned in 1000 blocks: " +
        str((earnedAfter-earnedBefore)/10**18))
    log("Change in total eursCrv in Vault+Strategy+Gauge: " +
        str((totalBalAfter-totalBalBefore)/10**18))
    log("Change in total eursCrv in Strategy+Gauge: " +
        str((stratBalAfter-stratBalBefore)/10**18))

    assert earnedAfter > 0
    assert totalBalAfter > totalBalBefore
    assert stratBalAfter > stratBalBefore
    assert lockedAfter > lockedBefore
    assert treasuryVaultBalAfter > treasuryVaultBalBefore

    assert crvBal(deployedContracts, strategyCurveEursCrvVoterProxy) == 0
    assert eursCrvBal(deployedContracts, strategyCurveEursCrvVoterProxy) == 0
    assert eursBal(deployedContracts, strategyCurveEursCrvVoterProxy) == 0
    assert snxBal(deployedContracts, strategyCurveEursCrvVoterProxy) == 0

    assert crvBal(deployedContracts, strategyProxy) == 0
    assert eursCrvBal(deployedContracts, strategyProxy) == 0
    assert eursBal(deployedContracts, strategyProxy) == 0
    assert snxBal(deployedContracts, strategyProxy) == 0

    assert crvBal(deployedContracts, curveYCRVVoter) == 0
    assert eursCrvBal(deployedContracts, curveYCRVVoter) == 0
    assert eursBal(deployedContracts, curveYCRVVoter) == 0
    assert snxBal(deployedContracts, curveYCRVVoter) == 0

    assert crvBal(deployedContracts, controller) == 0
    assert eursCrvBal(deployedContracts, controller) == 0
    assert eursBal(deployedContracts, controller) == 0
    assert snxBal(deployedContracts, controller) == 0


def test_strategyCurve3CrvVoterProxy_harvest(deployedContracts):
    strategyCurve3CrvVoterProxy = deployedContracts["strategyCurve3CrvVoterProxy"]
    deployer = deployedContracts["deployer"]
    threePoolVault = deployedContracts["threePoolVault"]
    multisig = deployedContracts["multisig"]
    strategyProxy = deployedContracts["strategyProxy"]
    curveYCRVVoter = deployedContracts["curveYCRVVoter"]
    votingEscrow = deployedContracts["votingEscrow"]
    controller = deployedContracts["controller"]
    treasuryVault = deployedContracts["treasuryVault"]

    chain.mine(1000)

    totalBalBefore = threePoolVault.balance()
    stratBalBefore = strategyCurve3CrvVoterProxy.balanceOf()
    earnedBefore = strategyCurve3CrvVoterProxy.earned()
    lockedBefore = votingEscrow.balanceOf(curveYCRVVoter.address)
    treasuryVaultBalBefore = threeCrvBal(
        deployedContracts, treasuryVault.address)

    strategyCurve3CrvVoterProxy.harvest(multisig)

    totalBalAfter = threePoolVault.balance()
    stratBalAfter = strategyCurve3CrvVoterProxy.balanceOf()
    earnedAfter = strategyCurve3CrvVoterProxy.earned()
    lockedAfter = votingEscrow.balanceOf(curveYCRVVoter.address)
    treasuryVaultBalAfter = threeCrvBal(
        deployedContracts, treasuryVault.address)

    log("Total 3Crv Earned in 1000 blocks: " +
        str((earnedAfter-earnedBefore)/10**18))
    log("Change in total 3Crv in Vault+Strategy+Gauge: " +
        str((totalBalAfter-totalBalBefore)/10**18))
    log("Change in total 3Crv in Strategy+Gauge: " +
        str((stratBalAfter-stratBalBefore)/10**18))

    assert earnedAfter > 0
    assert totalBalAfter > totalBalBefore
    assert stratBalAfter > stratBalBefore
    assert treasuryVaultBalAfter > treasuryVaultBalBefore

    assert crvBal(deployedContracts, strategyCurve3CrvVoterProxy) == 0
    assert threeCrvBal(deployedContracts, strategyCurve3CrvVoterProxy) == 0
    assert snxBal(deployedContracts, strategyCurve3CrvVoterProxy) == 0

    assert crvBal(deployedContracts, strategyProxy) == 0
    assert threeCrvBal(deployedContracts, strategyProxy) == 0
    assert snxBal(deployedContracts, strategyProxy) == 0

    assert crvBal(deployedContracts, curveYCRVVoter) == 0
    assert threeCrvBal(deployedContracts, curveYCRVVoter) == 0
    assert snxBal(deployedContracts, curveYCRVVoter) == 0
    assert lockedAfter > lockedBefore

    assert crvBal(deployedContracts, controller) == 0
    assert eursCrvBal(deployedContracts, controller) == 0
    assert eursBal(deployedContracts, controller) == 0
    assert snxBal(deployedContracts, controller) == 0


def test_strategyCurveBTCVoterProxy_harvest(deployedContracts):
    strategyCurveBTCVoterProxy = deployedContracts["strategyCurveBTCVoterProxy"]
    deployer = deployedContracts["deployer"]
    sbtcCrvVault = deployedContracts["sbtcCrvVault"]
    multisig = deployedContracts["multisig"]
    strategyProxy = deployedContracts["strategyProxy"]
    curveYCRVVoter = deployedContracts["curveYCRVVoter"]
    votingEscrow = deployedContracts["votingEscrow"]
    controller = deployedContracts["controller"]
    treasuryVault = deployedContracts["treasuryVault"]

    chain.mine(1000)

    totalBalBefore = sbtcCrvVault.balance()
    stratBalBefore = strategyCurveBTCVoterProxy.balanceOf()
    earnedBefore = strategyCurveBTCVoterProxy.earned()
    lockedBefore = votingEscrow.balanceOf(curveYCRVVoter.address)
    treasuryVaultBalBefore = sbtcCrvBal(
        deployedContracts, treasuryVault.address)

    strategyCurveBTCVoterProxy.harvest(multisig)

    totalBalAfter = sbtcCrvVault.balance()
    stratBalAfter = strategyCurveBTCVoterProxy.balanceOf()
    earnedAfter = strategyCurveBTCVoterProxy.earned()
    lockedAfter = votingEscrow.balanceOf(curveYCRVVoter.address)
    treasuryVaultBalAfter = sbtcCrvBal(
        deployedContracts, treasuryVault.address)

    log("Total sbtcCrv Earned in 1000 blocks: " +
        str((earnedAfter-earnedBefore)/10**18))
    log("Change in total sbtcCrv in Vault+Strategy+Gauge: " +
        str((totalBalAfter-totalBalBefore)/10**18))
    log("Change in total sbtcCrv in Strategy+Gauge: " +
        str((stratBalAfter-stratBalBefore)/10**18))

    assert earnedAfter > 0
    assert totalBalAfter > totalBalBefore
    assert stratBalAfter > stratBalBefore
    assert treasuryVaultBalAfter > treasuryVaultBalBefore

    assert crvBal(deployedContracts, strategyCurveBTCVoterProxy) == 0
    assert sbtcCrvBal(deployedContracts, strategyCurveBTCVoterProxy) == 0
    assert snxBal(deployedContracts, strategyCurveBTCVoterProxy) == 0

    assert crvBal(deployedContracts, strategyProxy) == 0
    assert sbtcCrvBal(deployedContracts, strategyProxy) == 0
    assert snxBal(deployedContracts, strategyProxy) == 0

    assert crvBal(deployedContracts, curveYCRVVoter) == 0
    assert sbtcCrvBal(deployedContracts, curveYCRVVoter) == 0
    assert snxBal(deployedContracts, curveYCRVVoter) == 0
    assert lockedAfter > lockedBefore

    assert crvBal(deployedContracts, controller) == 0
    assert eursCrvBal(deployedContracts, controller) == 0
    assert eursBal(deployedContracts, controller) == 0
    assert snxBal(deployedContracts, controller) == 0


def test_eursCrvVault_deposit(deployedContracts):
    strategyCurveEursCrvVoterProxy = deployedContracts["strategyCurveEursCrvVoterProxy"]
    deployer = deployedContracts["deployer"]
    eursCrvVault = deployedContracts["eursCrvVault"]
    EURS_CRV = deployedContracts["EURS_CRV"]
    eursCrv = deployedContracts["eursCrv"]
    strategyProxy = deployedContracts["strategyProxy"]
    curveYCRVVoter = deployedContracts["curveYCRVVoter"]
    controller = deployedContracts["controller"]

    totalBalBefore = eursCrvVault.balance()
    vaultBalBefore = eursCrvBal(deployedContracts, eursCrvVault.address)
    stratBalBefore = strategyCurveEursCrvVoterProxy.balanceOf()

    DEPOSIT_AMOUNT = 50 * (10**6) * (10**18)

    eursCrv.transfer(deployer["from"].address, DEPOSIT_AMOUNT, {
                     "from": "0xc0d8994Cd78eE1980885DF1A0C5470fC977b5cFe"})

    eursCrv.approve(eursCrvVault.address, DEPOSIT_AMOUNT, deployer)

    # Call deposit on eursCrv Vault
    eursCrvVault.deposit(DEPOSIT_AMOUNT, deployer)

    totalBalAfter = eursCrvVault.balance()
    vaultBalAfter = eursCrvBal(deployedContracts, eursCrvVault.address)
    stratBalAfter = strategyCurveEursCrvVoterProxy.balanceOf()

    assert eursCrvVault.balanceOf(deployer["from"].address) > 0

    assert stratBalAfter == stratBalBefore
    assert totalBalAfter == totalBalBefore + DEPOSIT_AMOUNT
    assert vaultBalAfter == vaultBalBefore + DEPOSIT_AMOUNT

    assert crvBal(deployedContracts, strategyCurveEursCrvVoterProxy) == 0
    assert eursCrvBal(deployedContracts, strategyCurveEursCrvVoterProxy) == 0
    assert eursBal(deployedContracts, strategyCurveEursCrvVoterProxy) == 0
    assert snxBal(deployedContracts, strategyCurveEursCrvVoterProxy) == 0

    assert crvBal(deployedContracts, strategyProxy) == 0
    assert eursCrvBal(deployedContracts, strategyProxy) == 0
    assert eursBal(deployedContracts, strategyProxy) == 0
    assert snxBal(deployedContracts, strategyProxy) == 0

    assert crvBal(deployedContracts, curveYCRVVoter) == 0
    assert eursCrvBal(deployedContracts, curveYCRVVoter) == 0
    assert eursBal(deployedContracts, curveYCRVVoter) == 0
    assert snxBal(deployedContracts, curveYCRVVoter) == 0

    assert crvBal(deployedContracts, controller) == 0
    assert eursCrvBal(deployedContracts, controller) == 0
    assert eursBal(deployedContracts, controller) == 0
    assert snxBal(deployedContracts, controller) == 0


def test_eursCrvVault_earn_2(deployedContracts):
    strategyCurveEursCrvVoterProxy = deployedContracts["strategyCurveEursCrvVoterProxy"]
    deployer = deployedContracts["deployer"]
    eursCrvVault = deployedContracts["eursCrvVault"]
    EURS_CRV = deployedContracts["EURS_CRV"]
    eursCrv = deployedContracts["eursCrv"]
    strategyProxy = deployedContracts["strategyProxy"]
    curveYCRVVoter = deployedContracts["curveYCRVVoter"]
    controller = deployedContracts["controller"]

    chain.mine(1000)

    totalBalBefore = eursCrvVault.balance()
    vaultBalBefore = eursCrvBal(deployedContracts, eursCrvVault.address)
    stratBalBefore = strategyCurveEursCrvVoterProxy.balanceOf()

    # Call earn on eursCrv Vault to transfer the funds to the new strategy
    eursCrvVault.earn(deployer)

    totalBalAfter = eursCrvVault.balance()
    vaultBalAfter = eursCrvBal(deployedContracts, eursCrvVault.address)
    stratBalAfter = strategyCurveEursCrvVoterProxy.balanceOf()

    assert totalBalBefore == totalBalAfter
    assert stratBalAfter - stratBalBefore == vaultBalBefore - vaultBalAfter

    assert crvBal(deployedContracts, strategyCurveEursCrvVoterProxy) == 0
    assert eursCrvBal(deployedContracts, strategyCurveEursCrvVoterProxy) == 0
    assert eursBal(deployedContracts, strategyCurveEursCrvVoterProxy) == 0
    assert snxBal(deployedContracts, strategyCurveEursCrvVoterProxy) > 0

    assert crvBal(deployedContracts, strategyProxy) == 0
    assert eursCrvBal(deployedContracts, strategyProxy) == 0
    assert eursBal(deployedContracts, strategyProxy) == 0
    assert snxBal(deployedContracts, strategyProxy) == 0

    assert crvBal(deployedContracts, curveYCRVVoter) == 0
    assert eursCrvBal(deployedContracts, curveYCRVVoter) == 0
    assert eursBal(deployedContracts, curveYCRVVoter) == 0
    assert snxBal(deployedContracts, curveYCRVVoter) == 0

    assert crvBal(deployedContracts, controller) == 0
    assert eursCrvBal(deployedContracts, controller) == 0
    assert eursBal(deployedContracts, controller) == 0
    assert snxBal(deployedContracts, controller) == 0


def test_eursCrvVault_withdraw(deployedContracts):
    strategyCurveEursCrvVoterProxy = deployedContracts["strategyCurveEursCrvVoterProxy"]
    deployer = deployedContracts["deployer"]
    eursCrvVault = deployedContracts["eursCrvVault"]
    EURS_CRV = deployedContracts["EURS_CRV"]
    eursCrv = deployedContracts["eursCrv"]
    strategyProxy = deployedContracts["strategyProxy"]
    curveYCRVVoter = deployedContracts["curveYCRVVoter"]
    controller = deployedContracts["controller"]

    chain.mine(1000)

    totalBalBefore = eursCrvVault.balance()
    vaultBalBefore = eursCrvBal(deployedContracts, eursCrvVault.address)
    stratBalBefore = strategyCurveEursCrvVoterProxy.balanceOf()

    TOTAL_BAL = eursCrvVault.balanceOf(deployer["from"].address)

    WITHDRAW_AMOUNT = TOTAL_BAL*(4/5)

    # Call withdraw on eursCrv Vault
    eursCrvVault.withdraw(WITHDRAW_AMOUNT, deployer)

    totalBalAfter = eursCrvVault.balance()
    vaultBalAfter = eursCrvBal(deployedContracts, eursCrvVault.address)
    stratBalAfter = strategyCurveEursCrvVoterProxy.balanceOf()

    assert eursCrvVault.balanceOf(deployer["from"].address) > 0

    assert stratBalAfter < stratBalBefore
    assert totalBalAfter < totalBalBefore
    assert vaultBalAfter < vaultBalBefore
    assert vaultBalAfter == 0

    assert crvBal(deployedContracts, strategyCurveEursCrvVoterProxy) == 0
    assert eursCrvBal(deployedContracts, strategyCurveEursCrvVoterProxy) == 0
    assert eursBal(deployedContracts, strategyCurveEursCrvVoterProxy) == 0
    assert snxBal(deployedContracts, strategyCurveEursCrvVoterProxy) > 0

    assert crvBal(deployedContracts, strategyProxy) == 0
    assert eursCrvBal(deployedContracts, strategyProxy) == 0
    assert eursBal(deployedContracts, strategyProxy) == 0
    assert snxBal(deployedContracts, strategyProxy) == 0

    assert crvBal(deployedContracts, curveYCRVVoter) == 0
    assert eursCrvBal(deployedContracts, curveYCRVVoter) == 0
    assert eursBal(deployedContracts, curveYCRVVoter) == 0
    assert snxBal(deployedContracts, curveYCRVVoter) == 0

    assert crvBal(deployedContracts, controller) == 0
    assert eursCrvBal(deployedContracts, controller) == 0
    assert eursBal(deployedContracts, controller) == 0
    assert snxBal(deployedContracts, controller) == 0


def test_strategyCurveEursCrvVoterProxy_withdrawToVault(deployedContracts):
    strategyCurveEursCrvVoterProxy = deployedContracts["strategyCurveEursCrvVoterProxy"]
    multisig = deployedContracts["multisig"]
    eursCrvVault = deployedContracts["eursCrvVault"]
    EURS_CRV = deployedContracts["EURS_CRV"]
    eursCrv = deployedContracts["eursCrv"]
    strategyProxy = deployedContracts["strategyProxy"]
    curveYCRVVoter = deployedContracts["curveYCRVVoter"]
    controller = deployedContracts["controller"]

    chain.mine(1000)

    totalBalBefore = eursCrvVault.balance()
    vaultBalBefore = eursCrvBal(deployedContracts, eursCrvVault.address)
    stratBalBefore = strategyCurveEursCrvVoterProxy.balanceOf()

    WITHDRAW_AMOUNT = stratBalBefore/10

    # Call withdraw on eursCrv Vault
    strategyCurveEursCrvVoterProxy.withdrawToVault(WITHDRAW_AMOUNT, multisig)

    totalBalAfter = eursCrvVault.balance()
    vaultBalAfter = eursCrvBal(deployedContracts, eursCrvVault.address)
    stratBalAfter = strategyCurveEursCrvVoterProxy.balanceOf()

    assert totalBalAfter == totalBalBefore
    assert vaultBalAfter == vaultBalBefore + WITHDRAW_AMOUNT
    assert stratBalAfter == stratBalBefore - WITHDRAW_AMOUNT

    assert crvBal(deployedContracts, strategyCurveEursCrvVoterProxy) == 0
    assert eursCrvBal(deployedContracts, strategyCurveEursCrvVoterProxy) == 0
    assert eursBal(deployedContracts, strategyCurveEursCrvVoterProxy) == 0
    assert snxBal(deployedContracts, strategyCurveEursCrvVoterProxy) > 0

    assert crvBal(deployedContracts, strategyProxy) == 0
    assert eursCrvBal(deployedContracts, strategyProxy) == 0
    assert eursBal(deployedContracts, strategyProxy) == 0
    assert snxBal(deployedContracts, strategyProxy) == 0

    assert crvBal(deployedContracts, curveYCRVVoter) == 0
    assert eursCrvBal(deployedContracts, curveYCRVVoter) == 0
    assert eursBal(deployedContracts, curveYCRVVoter) == 0
    assert snxBal(deployedContracts, curveYCRVVoter) == 0

    assert crvBal(deployedContracts, controller) == 0
    assert eursCrvBal(deployedContracts, controller) == 0
    assert eursBal(deployedContracts, controller) == 0
    assert snxBal(deployedContracts, controller) == 0


def test_strategyCurveEursCrvVoterProxy_harvest_2(deployedContracts):
    strategyCurveEursCrvVoterProxy = deployedContracts["strategyCurveEursCrvVoterProxy"]
    deployer = deployedContracts["deployer"]
    eursCrvVault = deployedContracts["eursCrvVault"]
    multisig = deployedContracts["multisig"]
    strategyProxy = deployedContracts["strategyProxy"]
    curveYCRVVoter = deployedContracts["curveYCRVVoter"]
    votingEscrow = deployedContracts["votingEscrow"]
    controller = deployedContracts["controller"]
    treasuryVault = deployedContracts["treasuryVault"]

    chain.mine(1000)

    totalBalBefore = eursCrvVault.balance()
    stratBalBefore = strategyCurveEursCrvVoterProxy.balanceOf()
    earnedBefore = strategyCurveEursCrvVoterProxy.earned()
    lockedBefore = votingEscrow.balanceOf(curveYCRVVoter.address)
    treasuryVaultBalBefore = eursCrvBal(
        deployedContracts, treasuryVault.address)

    strategyCurveEursCrvVoterProxy.harvest(multisig)

    totalBalAfter = eursCrvVault.balance()
    stratBalAfter = strategyCurveEursCrvVoterProxy.balanceOf()
    earnedAfter = strategyCurveEursCrvVoterProxy.earned()
    lockedAfter = votingEscrow.balanceOf(curveYCRVVoter.address)
    treasuryVaultBalAfter = eursCrvBal(
        deployedContracts, treasuryVault.address)

    log("Total eursCrv Earned in 1000 blocks: " +
        str((earnedAfter-earnedBefore)/10**18))
    log("Change in total eursCrv in Vault+Strategy+Gauge: " +
        str((totalBalAfter-totalBalBefore)/10**18))
    log("Change in total eursCrv in Strategy+Gauge: " +
        str((stratBalAfter-stratBalBefore)/10**18))

    assert earnedAfter > earnedBefore
    assert totalBalAfter > totalBalBefore
    assert stratBalAfter > stratBalBefore
    assert treasuryVaultBalAfter > treasuryVaultBalBefore

    assert crvBal(deployedContracts, strategyCurveEursCrvVoterProxy) == 0
    assert eursCrvBal(deployedContracts, strategyCurveEursCrvVoterProxy) == 0
    assert eursBal(deployedContracts, strategyCurveEursCrvVoterProxy) == 0
    assert snxBal(deployedContracts, strategyCurveEursCrvVoterProxy) == 0

    assert crvBal(deployedContracts, strategyProxy) == 0
    assert eursCrvBal(deployedContracts, strategyProxy) == 0
    assert eursBal(deployedContracts, strategyProxy) == 0
    assert snxBal(deployedContracts, strategyProxy) == 0

    assert crvBal(deployedContracts, curveYCRVVoter) == 0
    assert eursCrvBal(deployedContracts, curveYCRVVoter) == 0
    assert eursBal(deployedContracts, curveYCRVVoter) == 0
    assert snxBal(deployedContracts, curveYCRVVoter) == 0
    assert lockedAfter > lockedBefore

    assert crvBal(deployedContracts, controller) == 0
    assert eursCrvBal(deployedContracts, controller) == 0
    assert eursBal(deployedContracts, controller) == 0
    assert snxBal(deployedContracts, controller) == 0


def test_strategyProxy_ifTokenGetStuck(deployedContracts):
    strategyCurveEursCrvVoterProxy = deployedContracts["strategyCurveEursCrvVoterProxy"]
    deployer = deployedContracts["deployer"]
    eursCrvVault = deployedContracts["eursCrvVault"]
    multisig = deployedContracts["multisig"]
    strategyProxy = deployedContracts["strategyProxy"]
    curveYCRVVoter = deployedContracts["curveYCRVVoter"]
    votingEscrow = deployedContracts["votingEscrow"]

    # Send some assets to StrategyProxy
    crv = Contract("0xD533a949740bb3306d119CC777fa900bA034cd52")
    snx = Contract("0xC011a73ee8576Fb46F5E1c5751cA3B9Fe0af2a6F")
    eursCrv = Contract("0x194eBd173F6cDacE046C53eACcE9B953F28411d1")
    threeCrv = Contract("0x6c3F90f043a72FA612cbac8115EE7e52BDe6E490")

    AMOUNT = 10 ** 18

    crv.transfer(strategyProxy.address, AMOUNT,
                 {"from": "0xD533a949740bb3306d119CC777fa900bA034cd52"})
    snx.transfer(strategyProxy.address, AMOUNT,
                 {"from": "0xDA4eF8520b1A57D7d63f1E249606D1A459698876"})
    eursCrv.transfer(strategyProxy.address, AMOUNT,
                     {"from": "0xc0d8994Cd78eE1980885DF1A0C5470fC977b5cFe"})
    threeCrv.transfer(strategyProxy.address, AMOUNT,
                      {"from": "0x6c3F90f043a72FA612cbac8115EE7e52BDe6E490"})

    assert crv.balanceOf(strategyProxy.address) >= AMOUNT
    assert snx.balanceOf(strategyProxy.address) >= AMOUNT
    assert eursCrv.balanceOf(strategyProxy.address) >= AMOUNT
    assert threeCrv.balanceOf(strategyProxy.address) >= AMOUNT

    beforeCrvBal = crv.balanceOf(multisig["from"])
    beforeSnxBal = snx.balanceOf(multisig["from"])
    beforeEursCrvBal = eursCrv.balanceOf(multisig["from"])
    beforeThreeCrvBal = threeCrv.balanceOf(multisig["from"])

    # Get assets out from the StrategyProxy
    strategyProxy.ifTokenGetStuck(crv.address, multisig["from"], multisig)
    strategyProxy.ifTokenGetStuck(snx.address, multisig["from"], multisig)
    strategyProxy.ifTokenGetStuck(eursCrv.address, multisig["from"], multisig)
    strategyProxy.ifTokenGetStuck(threeCrv.address, multisig["from"], multisig)

    afterCrvBal = crv.balanceOf(multisig["from"])
    afterSnxBal = snx.balanceOf(multisig["from"])
    afterEursCrvBal = eursCrv.balanceOf(multisig["from"])
    afterThreeCrvBal = threeCrv.balanceOf(multisig["from"])

    assert crv.balanceOf(strategyProxy.address) == 0
    assert snx.balanceOf(strategyProxy.address) == 0
    assert eursCrv.balanceOf(strategyProxy.address) == 0
    assert threeCrv.balanceOf(strategyProxy.address) == 0

    assert afterCrvBal - beforeCrvBal >= AMOUNT
    assert afterSnxBal - beforeSnxBal >= AMOUNT
    assert afterEursCrvBal - beforeEursCrvBal >= AMOUNT
    assert afterThreeCrvBal - beforeThreeCrvBal >= AMOUNT


def test_strategyProxy_ifTokenGetStuckInProxy_2(deployedContracts):
    strategyCurveEursCrvVoterProxy = deployedContracts["strategyCurveEursCrvVoterProxy"]
    deployer = deployedContracts["deployer"]
    eursCrvVault = deployedContracts["eursCrvVault"]
    multisig = deployedContracts["multisig"]
    strategyProxy = deployedContracts["strategyProxy"]
    curveYCRVVoter = deployedContracts["curveYCRVVoter"]
    votingEscrow = deployedContracts["votingEscrow"]

    # Send some assets to StrategyProxy
    crv = Contract("0xD533a949740bb3306d119CC777fa900bA034cd52")
    snx = Contract("0xC011a73ee8576Fb46F5E1c5751cA3B9Fe0af2a6F")
    eursCrv = Contract("0x194eBd173F6cDacE046C53eACcE9B953F28411d1")
    threeCrv = Contract("0x6c3F90f043a72FA612cbac8115EE7e52BDe6E490")

    AMOUNT = 10 ** 18

    crv.transfer(curveYCRVVoter.address, AMOUNT,
                 {"from": "0xD533a949740bb3306d119CC777fa900bA034cd52"})
    snx.transfer(curveYCRVVoter.address, AMOUNT,
                 {"from": "0xDA4eF8520b1A57D7d63f1E249606D1A459698876"})
    eursCrv.transfer(curveYCRVVoter.address, AMOUNT,
                     {"from": "0xc0d8994Cd78eE1980885DF1A0C5470fC977b5cFe"})
    threeCrv.transfer(curveYCRVVoter.address, AMOUNT,
                      {"from": "0x6c3F90f043a72FA612cbac8115EE7e52BDe6E490"})

    assert crv.balanceOf(curveYCRVVoter.address) >= AMOUNT
    assert snx.balanceOf(curveYCRVVoter.address) >= AMOUNT
    assert eursCrv.balanceOf(curveYCRVVoter.address) >= AMOUNT
    assert threeCrv.balanceOf(curveYCRVVoter.address) >= AMOUNT

    beforeCrvBal = crv.balanceOf(multisig["from"])
    beforeSnxBal = snx.balanceOf(multisig["from"])
    beforeEursCrvBal = eursCrv.balanceOf(multisig["from"])
    beforeThreeCrvBal = threeCrv.balanceOf(multisig["from"])

    # Get assets out from the StrategyProxy
    strategyProxy.ifTokenGetStuckInProxy(
        crv.address, multisig["from"], multisig)
    strategyProxy.ifTokenGetStuckInProxy(
        snx.address, multisig["from"], multisig)
    strategyProxy.ifTokenGetStuckInProxy(
        eursCrv.address, multisig["from"], multisig)
    strategyProxy.ifTokenGetStuckInProxy(
        threeCrv.address, multisig["from"], multisig)

    afterCrvBal = crv.balanceOf(multisig["from"])
    afterSnxBal = snx.balanceOf(multisig["from"])
    afterEursCrvBal = eursCrv.balanceOf(multisig["from"])
    afterThreeCrvBal = threeCrv.balanceOf(multisig["from"])

    assert crv.balanceOf(curveYCRVVoter.address) == 0
    assert snx.balanceOf(curveYCRVVoter.address) == 0
    assert eursCrv.balanceOf(curveYCRVVoter.address) == 0
    assert threeCrv.balanceOf(curveYCRVVoter.address) == 0

    assert afterCrvBal - beforeCrvBal >= AMOUNT
    assert afterSnxBal - beforeSnxBal >= AMOUNT
    assert afterEursCrvBal - beforeEursCrvBal >= AMOUNT
    assert afterThreeCrvBal - beforeThreeCrvBal >= AMOUNT


def test_oldCurveYCrvVoter_setStrategy(deployedContracts):
    oldCurveYCRVVoter = deployedContracts["oldCurveYCRVVoter"]
    whitehatStrategyProxy = deployedContracts["whitehatStrategyProxy"]
    multisig = deployedContracts["multisig"]

    # set whitehatStrategyProxy as strategy for oldCurveYCrvVoter
    oldCurveYCRVVoter.setStrategy(whitehatStrategyProxy.address, multisig)

    assert oldCurveYCRVVoter.strategy() == whitehatStrategyProxy.address


def test_whitehatStrategyProxy_rescueCrv(deployedContracts):
    oldCurveYCRVVoter = deployedContracts["oldCurveYCRVVoter"]
    curveYCRVVoter = deployedContracts["curveYCRVVoter"]
    strategyProxy = deployedContracts["strategyProxy"]
    whitehatStrategyProxy = deployedContracts["whitehatStrategyProxy"]
    deployer = deployedContracts["deployer"]
    votingEscrow = deployedContracts["votingEscrow"]

    oldCurveYCRVVoterBalBefore = crvBal(deployedContracts, oldCurveYCRVVoter)
    lockedBefore = votingEscrow.balanceOf(curveYCRVVoter.address)

    assert oldCurveYCRVVoterBalBefore > 0

    # Withdraw and transfer CRV from oldCurveYCrvVoter to the new strategyCurveEursCrvVoterProxy
    whitehatStrategyProxy.rescueCrv(
        curveYCRVVoter.address, strategyProxy.address, deployer)

    oldCurveYCRVVoterBalAfter = crvBal(deployedContracts, oldCurveYCRVVoter)
    lockedAfter = votingEscrow.balanceOf(curveYCRVVoter.address)

    log("CRV Rescued: "+str((lockedAfter-lockedBefore)/10**18))

    assert oldCurveYCRVVoterBalAfter == 0
    assert lockedAfter - lockedBefore > 0


def crvBal(deployedContracts, address):
    crv = deployedContracts["crv"]
    return crv.balanceOf(address)


def eursCrvBal(deployedContracts, address):
    eursCrv = deployedContracts["eursCrv"]
    return eursCrv.balanceOf(address)


def eursBal(deployedContracts, address):
    eurs = deployedContracts["eurs"]
    return eurs.balanceOf(address)


def threeCrvBal(deployedContracts, address):
    threeCrv = deployedContracts["threeCrv"]
    return threeCrv.balanceOf(address)


def sbtcCrvBal(deployedContracts, address):
    sbtcCrvBal = deployedContracts["sbtcCrv"]
    return sbtcCrvBal.balanceOf(address)


def snxBal(deployedContracts, address):
    snx = deployedContracts["snx"]
    return snx.balanceOf(address)


def log(msg):
    msg = typer.style(msg, fg=typer.colors.GREEN, bold=True)
    typer.echo(msg)
