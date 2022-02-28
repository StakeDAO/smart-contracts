import pytest
from brownie import *
import typer
import json
import requests


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
    DEFAULT_DEPLOYER_ACCOUNT = accounts.load('stakedao-deployer-rug-pull-2')
    GNOSIS_SAFE_PROXY = deployed[ENV]['GNOSIS_SAFE_PROXY']

    DAI = '0x8f3Cf7ad23Cd3CaDbD9735AFf958023239c6A063'
    # dai = Contract('0x8f3Cf7ad23Cd3CaDbD9735AFf958023239c6A063')
    WBTC = '0x1BFD67037B42Cf73acF2047067bd4F2C47D9BfD6'
    # wbtc = WMATIC.at(WBTC)

    VESTING_ESCROW = deployed[ENV]['VESTING_ESCROW']
    ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"
    deployer = {'from': DEFAULT_DEPLOYER_ACCOUNT}
    multisig = {'from': GNOSIS_SAFE_PROXY}
    PROXY = '0xF34Ae3C7515511E29d8Afe321E67Bdf97a274f1A'

    sender = {'from': '0x9f535E3c63Cd1447164BED4933d1efefBbC97a3f'}

    WANT = '0xf8a57c1d3b9629b77b6726a042ca48990A84Fb49'
    want = WMATIC.at(WANT)

    # vault = yVault.at('0x7d60F21072b585351dFd5E8b17109458D97ec120')
    vault = Vault.deploy(
        WANT, '0x91aE00aaC6eE0D7853C8F92710B641F68Cd945Df', DEFAULT_DEPLOYER_ACCOUNT, deployer)
    # 0x91aE00aaC6eE0D7853C8F92710B641F68Cd945Df
    controller = Controller.at('0x91aE00aaC6eE0D7853C8F92710B641F68Cd945Df')
    old_strat = StrategyCurveAm3Crv.at(
        '0x552DAd974da30D67f25BE444991E22CbaE357851')

    new_strat = StrategyBtcCurve.deploy(controller.address, deployer)

    WHALE = '0x1dDc97E6Ce44Dd86E88844861dC4525E50F316C0'
    whale = {'from': WHALE}
    # vault.deposit(100_000 * 10**18, whale)
    GAUGE = '0xffbACcE0CC7C19d46132f1258FC16CF6871D153c'
    gauge = GaugeV2.at(GAUGE)
    _WMATIC = '0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270'
    wmatic = WMATIC.at(_WMATIC)
    CRV = '0x172370d5Cd63279eFa6d502DAB29171933a610AF'
    crv = WMATIC.at(CRV)

    controller.setVault(WANT, vault.address, deployer)
    controller.approveStrategy(WANT, new_strat.address, deployer)
    controller.setStrategy(WANT, new_strat.address, deployer)

    return {"vault": vault, "controller": controller, "old_strat": old_strat, "want": want,
            "multisig": multisig, "deployer": deployer, "wmatic": wmatic, "gauge": gauge,
            "sender": sender, "controller": controller, "DAI": DAI, 'new_strat': new_strat,
            'crv': crv, 'whale': whale, 'WBTC': WBTC}


def test_new_strat_earn(deployedContracts):
    want = deployedContracts['want']
    vault = deployedContracts['vault']
    old_strat = deployedContracts['old_strat']
    multisig = deployedContracts['multisig']
    wmatic = deployedContracts['wmatic']
    gauge = deployedContracts['gauge']
    DAI = deployedContracts['DAI']
    deployer = deployedContracts['deployer']
    controller = deployedContracts['controller']
    new_strat = deployedContracts['new_strat']
    whale = deployedContracts['whale']

    # want.transfer(vault.address, 3 * 10**18, whale)
    want.approve(vault.address, 100 * 10**18, whale)
    vault.deposit(3 * 10**18, whale)

    vaultBefore = want.balanceOf(vault.address)
    oldStratBefore = old_strat.balanceOf()

    vault.earn(deployer)
    # vault.earn(deployer)
    # vault.earn(deployer)

    vaultAfter = want.balanceOf(vault.address)
    newStratAfter = new_strat.balanceOf()

    assert vaultBefore == newStratAfter + vaultAfter


def test_new_strat_harvest(deployedContracts):
    want = deployedContracts['want']
    vault = deployedContracts['vault']
    old_strat = deployedContracts['old_strat']
    multisig = deployedContracts['multisig']
    wmatic = deployedContracts['wmatic']
    gauge = deployedContracts['gauge']
    DAI = deployedContracts['DAI']
    deployer = deployedContracts['deployer']
    controller = deployedContracts['controller']
    new_strat = deployedContracts['new_strat']
    crv = deployedContracts['crv']
    WBTC = deployedContracts['WBTC']

    chain.sleep(5 * 86400)
    chain.mine(100)

    # send old_strat's crv rewards to new_strat for compounding
    # crv.transfer(new_strat.address, crv.balanceOf(
    #     '0xb36a0671B3D49587236d7833B01E79798175875f'), deployer)

    stratWmaticInside = wmatic.balanceOf(new_strat.address)
    stratWmaticClaimable = gauge.reward_integral_for(
        wmatic.address, new_strat.address)

    stratCrvInside = crv.balanceOf(new_strat.address)
    stratCrvClaimable = gauge.reward_integral_for(
        crv.address, new_strat.address)

    print("Wmatic: Inside, Claimable", stratWmaticInside,
          stratWmaticClaimable / 10**18)
    print("Crv: Inside, Claimable", stratCrvInside, stratCrvClaimable / 10**18)

    data_wmatic = create_swapdata(wmatic.address, WBTC, stratWmaticInside +
                                  stratWmaticClaimable, new_strat.address)
    data_crv = create_swapdata(crv.address, WBTC, stratCrvInside +
                               stratCrvClaimable, new_strat.address)

    totalAm3CrvBefore = new_strat.balanceOf()
    poolAm3CrvBefore = new_strat.balanceOfPool()

    new_strat.harvest(data_wmatic, data_crv, deployer)

    totalAm3CrvAfter = new_strat.balanceOf()
    poolAm3CrvAfter = new_strat.balanceOfPool()

    print("Total btcCrv increase", (totalAm3CrvAfter - totalAm3CrvBefore) / 10**18)
    print("Pool btcCrv increase", (poolAm3CrvAfter - poolAm3CrvBefore) / 10**18)


def test_new_strat_withdraw(deployedContracts):
    want = deployedContracts['want']
    vault = deployedContracts['vault']
    old_strat = deployedContracts['old_strat']
    multisig = deployedContracts['multisig']
    wmatic = deployedContracts['wmatic']
    gauge = deployedContracts['gauge']
    DAI = deployedContracts['DAI']
    deployer = deployedContracts['deployer']
    controller = deployedContracts['controller']
    new_strat = deployedContracts['new_strat']
    crv = deployedContracts['crv']

    WHALE = '0x1dDc97E6Ce44Dd86E88844861dC4525E50F316C0'
    USER = '0xf10806C57b21F89A60ac5b743532fd3d4efcE18A'

    userBefore = want.balanceOf(WHALE)
    vault.withdraw(vault.balanceOf(WHALE), {'from': WHALE})
    userAfter = want.balanceOf(WHALE)

    print("User increase", (userAfter - userBefore) / 10**18)


def create_swapdata(_from, to, amount, strat):
    # be wary that if someone withdraws right before harvest,
    # then stratWmaticInside + stratWmaticClaimable might change
    URL = "https://apiv4.paraswap.io/v2/prices/"
    PARAMS = {
        'from': _from,
        'to': to,
        'fromDecimals': 18,
        'toDecimals': 18,
        'amount': amount,
        'side': 'SELL',
        'network': 137
    }
    r = requests.get(url=URL, params=PARAMS)
    data = r.json()
    # print('PRICE_ROUTE', data['priceRoute'])
    priceRoute = data['priceRoute']

    print('tokenFrom ', 'tokenTo ', 'priceWithSlippage ',
          priceRoute['details']['tokenFrom'], priceRoute['details']['tokenTo'], priceRoute['priceWithSlippage'])

    POST_URL = "https://apiv4.paraswap.io/v2/transactions/137?skipChecks=true"
    POST_DATA = {
        'userAddress': strat,
        'srcToken': priceRoute['details']['tokenFrom'],
        'destToken': priceRoute['details']['tokenTo'],
        'srcAmount': priceRoute['details']['srcAmount'],
        'destAmount': priceRoute['priceWithSlippage'],
        'toDecimals': 18,
        'fromDecimals': 18,
        'referrer': 'stakedao',
        'priceRoute': priceRoute
    }
    r = requests.post(url=POST_URL, json=POST_DATA)
    print("RRRR", r)
    response = r.json()
    return response['data']


# def test_old_strat_harvest(deployedContracts):
#     want = deployedContracts['want']
#     vault = deployedContracts['vault']
#     old_strat = deployedContracts['old_strat']
#     multisig = deployedContracts['multisig']
#     wmatic = deployedContracts['wmatic']
#     gauge = deployedContracts['gauge']
#     DAI = deployedContracts['DAI']
#     deployer = deployedContracts['deployer']

#     totalAm3CrvBefore = old_strat.balanceOf()
#     poolAm3CrvBefore = old_strat.balanceOfPool()

#     stratWmaticInside = wmatic.balanceOf(old_strat.address)
#     stratWmaticClaimable = gauge.reward_integral_for(
#         wmatic.address, old_strat.address)

#     print("Inside, Claimable", stratWmaticInside, stratWmaticClaimable)

#     data = create_swapdata(wmatic.address, DAI, stratWmaticInside +
#                            stratWmaticClaimable, old_strat.address)

#     old_strat.harvest(data, deployer)

#     totalAm3CrvAfter = old_strat.balanceOf()
#     poolAm3CrvAfter = old_strat.balanceOfPool()

#     print("Total am3Crv increase", (totalAm3CrvAfter - totalAm3CrvBefore) / 10**18)
#     print("Pool am3Crv increase", (poolAm3CrvAfter - poolAm3CrvBefore) / 10**18)

#     assert totalAm3CrvAfter - totalAm3CrvBefore > 0
#     assert poolAm3CrvAfter - poolAm3CrvBefore > 0


# def test_crv_rescue(deployedContracts):
#     want = deployedContracts['want']
#     vault = deployedContracts['vault']
#     old_strat = deployedContracts['old_strat']
#     multisig = deployedContracts['multisig']
#     wmatic = deployedContracts['wmatic']
#     gauge = deployedContracts['gauge']
#     DAI = deployedContracts['DAI']
#     deployer = deployedContracts['deployer']
#     controller = deployedContracts['controller']
#     crv = deployedContracts['crv']

#     oldStratCrvBefore = crv.balanceOf(old_strat.address)
#     deployerCrvBefore = crv.balanceOf(
#         '0xb36a0671B3D49587236d7833B01E79798175875f')

#     controller.inCaseStrategyTokenGetStuck(
#         old_strat.address, crv.address, deployer)
#     controller.inCaseTokensGetStuck(
#         crv.address, crv.balanceOf(controller.address), deployer)

#     oldStratCrvAfter = crv.balanceOf(old_strat.address)
#     deployerCrvAfter = crv.balanceOf(
#         '0xb36a0671B3D49587236d7833B01E79798175875f')

#     print("strat diff", (oldStratCrvAfter - oldStratCrvBefore) / 10**18)
#     print("deployer diff", (deployerCrvAfter - deployerCrvBefore) / 10**18)


# def test_migrate_strat(deployedContracts):
#     want = deployedContracts['want']
#     vault = deployedContracts['vault']
#     old_strat = deployedContracts['old_strat']
#     multisig = deployedContracts['multisig']
#     wmatic = deployedContracts['wmatic']
#     gauge = deployedContracts['gauge']
#     DAI = deployedContracts['DAI']
#     deployer = deployedContracts['deployer']
#     controller = deployedContracts['controller']
#     new_strat = deployedContracts['new_strat']

#     vaultBefore = want.balanceOf(vault.address)
#     oldStratBefore = old_strat.balanceOf()

#     controller.approveStrategy(want.address, new_strat.address, deployer)
#     controller.setStrategy(want.address, new_strat.address, deployer)

#     vaultAfter = want.balanceOf(vault.address)

#     assert vaultAfter == vaultBefore + oldStratBefore
