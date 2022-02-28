import pytest
from brownie import *
import brownie
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

    VESTING_ESCROW = deployed[ENV]['VESTING_ESCROW']

    ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"

    deployer = {'from': DEFAULT_DEPLOYER_ACCOUNT}

    multisig = {'from': GNOSIS_SAFE_PROXY}

    controller = Controller.at(deployed[ENV]['CONTROLLER'])

    user = {'from': '0xBE0eB53F46cd790Cd13851d5EFf43D12404d33E8'}

    wrapper = xTokenWrapper.deploy(GNOSIS_SAFE_PROXY, deployer)

    dai = Contract('0x6b175474e89094c44da98b954eedeac495271d0f')
    aave = Contract(wrapper.aave())

    xAAVEa = Contract(wrapper.xAAVEa())

    return {"aave": aave, "treasuryVault": treasuryVault, "multisig": multisig, "deployer": deployer, "wrapper": wrapper, "user": user, "controller": controller, "GNOSIS_SAFE_PROXY": GNOSIS_SAFE_PROXY, "xAAVEa": xAAVEa}


def test_xToken_mintWithToken(deployedContracts):
    aave = deployedContracts['aave']
    wrapper = deployedContracts['wrapper']
    user = deployedContracts['user']
    GNOSIS_SAFE_PROXY = deployedContracts['GNOSIS_SAFE_PROXY']
    xAAVEa = deployedContracts['xAAVEa']

    userAaveBefore = aave.balanceOf(user['from'])
    userSdxAaveBefore = wrapper.balanceOf(user['from'])
    wrapperAaveBefore = aave.balanceOf(wrapper.address)
    wrapperXaaveBefore = xAAVEa.balanceOf(wrapper.address)
    xAaveAaveBefore = aave.balanceOf(wrapper.xAAVEa())
    multisigAaveBefore = aave.balanceOf(GNOSIS_SAFE_PROXY)

    aave.approve(wrapper.address, 10**9 * 10**18, user)
    wrapper.mintWithToken(500 * 10**18, user)

    userAaveAfter = aave.balanceOf(user['from'])
    userSdxAaveAfter = wrapper.balanceOf(user['from'])
    wrapperAaveAfter = aave.balanceOf(wrapper.address)
    wrapperXaaveAfter = xAAVEa.balanceOf(wrapper.address)
    xAaveAaveAfter = aave.balanceOf(wrapper.xAAVEa())
    multisigAaveAfter = aave.balanceOf(GNOSIS_SAFE_PROXY)

    assert userAaveBefore - userAaveAfter > 0
    assert multisigAaveAfter > multisigAaveBefore
    # assert userAaveBefore - userAaveAfter == xAaveAaveAfter - \
    #     xAaveAaveBefore + multisigAaveAfter - multisigAaveBefore
    assert xAaveAaveAfter - xAaveAaveBefore > 0
    assert wrapperXaaveAfter - wrapperXaaveBefore > 0
    assert wrapperXaaveAfter - wrapperXaaveBefore == userSdxAaveAfter - userSdxAaveBefore
    assert wrapperAaveAfter == wrapperAaveBefore == 0

    chain.sleep(30 * 86400)
    chain.mine(1000)
    xAAVEa.claim({'from': '0x38138586aedb29b436eab16105b09c317f5a79dd'})
    chain.snapshot()


def test_xToken_burn_with_eth(deployedContracts):
    aave = deployedContracts['aave']
    wrapper = deployedContracts['wrapper']
    user = deployedContracts['user']
    GNOSIS_SAFE_PROXY = deployedContracts['GNOSIS_SAFE_PROXY']
    xAAVEa = deployedContracts['xAAVEa']

    userSdxAaveBefore = wrapper.balanceOf(user['from'])
    wrapperAaveBefore = aave.balanceOf(wrapper.address)
    wrapperXaaveBefore = xAAVEa.balanceOf(wrapper.address)
    xAaveAaveBefore = aave.balanceOf(wrapper.xAAVEa())
    multisigAaveBefore = aave.balanceOf(GNOSIS_SAFE_PROXY)

    acc = accounts.at(user['from'])
    before = acc.balance()
    wrapper.burn(wrapper.balanceOf(user['from']), True, 0, user)
    after = acc.balance()

    userSdxAaveAfter = wrapper.balanceOf(user['from'])
    wrapperAaveAfter = aave.balanceOf(wrapper.address)
    wrapperXaaveAfter = xAAVEa.balanceOf(wrapper.address)
    xAaveAaveAfter = aave.balanceOf(wrapper.xAAVEa())
    multisigAaveAfter = aave.balanceOf(GNOSIS_SAFE_PROXY)

    print("Eth received", (after - before) / 10**18)

    assert after - before > 0
    assert wrapperXaaveBefore > wrapperXaaveAfter
    assert wrapperXaaveBefore - wrapperXaaveAfter == userSdxAaveBefore - userSdxAaveAfter
    assert wrapperAaveAfter == wrapperAaveBefore == 0
    assert multisigAaveAfter == multisigAaveBefore


def test_xToken_burn_with_aave(deployedContracts):
    chain.revert()
    aave = deployedContracts['aave']
    wrapper = deployedContracts['wrapper']
    user = deployedContracts['user']
    GNOSIS_SAFE_PROXY = deployedContracts['GNOSIS_SAFE_PROXY']
    xAAVEa = deployedContracts['xAAVEa']

    userAaveBefore = aave.balanceOf(user['from'])
    userSdxAaveBefore = wrapper.balanceOf(user['from'])
    wrapperAaveBefore = aave.balanceOf(wrapper.address)
    wrapperXaaveBefore = xAAVEa.balanceOf(wrapper.address)
    xAaveAaveBefore = aave.balanceOf(wrapper.xAAVEa())
    multisigAaveBefore = aave.balanceOf(GNOSIS_SAFE_PROXY)

    wrapper.burn(wrapper.balanceOf(user['from']), False, 0, user)

    userAaveAfter = aave.balanceOf(user['from'])
    userSdxAaveAfter = wrapper.balanceOf(user['from'])
    wrapperAaveAfter = aave.balanceOf(wrapper.address)
    wrapperXaaveAfter = xAAVEa.balanceOf(wrapper.address)
    xAaveAaveAfter = aave.balanceOf(wrapper.xAAVEa())
    multisigAaveAfter = aave.balanceOf(GNOSIS_SAFE_PROXY)

    print("Aave received", (userAaveAfter - userAaveBefore) / 10**18)

    assert userAaveAfter - userAaveBefore > 0
    assert wrapperXaaveBefore > wrapperXaaveAfter
    assert wrapperXaaveBefore - wrapperXaaveAfter == userSdxAaveBefore - userSdxAaveAfter
    assert wrapperAaveAfter == wrapperAaveBefore == 0
    assert multisigAaveAfter == multisigAaveBefore


def test_xToken_redeem_sdxAavea_for_xAavea(deployedContracts):
    chain.revert()
    aave = deployedContracts['aave']
    wrapper = deployedContracts['wrapper']
    user = deployedContracts['user']
    GNOSIS_SAFE_PROXY = deployedContracts['GNOSIS_SAFE_PROXY']
    xAAVEa = deployedContracts['xAAVEa']

    userxAaveBefore = xAAVEa.balanceOf(user['from'])
    userSdxAaveBefore = wrapper.balanceOf(user['from'])
    wrapperAaveBefore = aave.balanceOf(wrapper.address)
    wrapperXaaveBefore = xAAVEa.balanceOf(wrapper.address)

    wrapper.redeemsdxAAVEeaForxAAVEa(wrapper.balanceOf(user['from']), user)

    userxAaveAfter = xAAVEa.balanceOf(user['from'])
    userSdxAaveAfter = wrapper.balanceOf(user['from'])
    wrapperAaveAfter = aave.balanceOf(wrapper.address)
    wrapperXaaveAfter = xAAVEa.balanceOf(wrapper.address)

    print("xAave received", (userxAaveAfter - userxAaveBefore) / 10**18)

    assert userxAaveAfter - userxAaveBefore > 0
    assert userxAaveAfter - userxAaveBefore == wrapperXaaveBefore - wrapperXaaveAfter
    assert userSdxAaveBefore - userSdxAaveAfter == wrapperXaaveBefore - wrapperXaaveAfter
    assert wrapperAaveAfter == wrapperAaveBefore == 0


def test_xToken_whale_mint_burn_fail(deployedContracts):
    aave = deployedContracts['aave']
    wrapper = deployedContracts['wrapper']
    user = deployedContracts['user']
    GNOSIS_SAFE_PROXY = deployedContracts['GNOSIS_SAFE_PROXY']
    xAAVEa = deployedContracts['xAAVEa']

    AAVE_WHALE = '0x26a78d5b6d7a7aceedd1e6ee3229b372a624d8b7'
    aave_whale = {'from': AAVE_WHALE}

    # mint
    userAaveBefore = aave.balanceOf(AAVE_WHALE)
    userSdxAaveBefore = wrapper.balanceOf(AAVE_WHALE)
    wrapperAaveBefore = aave.balanceOf(wrapper.address)
    wrapperXaaveBefore = xAAVEa.balanceOf(wrapper.address)
    xAaveAaveBefore = aave.balanceOf(wrapper.xAAVEa())
    multisigAaveBefore = aave.balanceOf(GNOSIS_SAFE_PROXY)

    aave.approve(wrapper.address, 10**9 * 10**18, aave_whale)
    wrapper.mintWithToken(100000 * 10**18, aave_whale)

    userAaveAfter = aave.balanceOf(AAVE_WHALE)
    userSdxAaveAfter = wrapper.balanceOf(AAVE_WHALE)
    wrapperAaveAfter = aave.balanceOf(wrapper.address)
    wrapperXaaveAfter = xAAVEa.balanceOf(wrapper.address)
    xAaveAaveAfter = aave.balanceOf(wrapper.xAAVEa())
    multisigAaveAfter = aave.balanceOf(GNOSIS_SAFE_PROXY)

    assert userAaveBefore - userAaveAfter > 0
    assert multisigAaveAfter > multisigAaveBefore
    assert xAaveAaveAfter - xAaveAaveBefore > 0
    assert wrapperXaaveAfter - wrapperXaaveBefore > 0
    assert wrapperXaaveAfter - wrapperXaaveBefore == userSdxAaveAfter - userSdxAaveBefore
    assert wrapperAaveAfter == wrapperAaveBefore == 0

    chain.sleep(30 * 86400)
    chain.mine(1000)
    xAAVEa.claim({'from': '0x38138586aedb29b436eab16105b09c317f5a79dd'})

    # burn fail
    userAaveBefore = aave.balanceOf(AAVE_WHALE)
    userSdxAaveBefore = wrapper.balanceOf(AAVE_WHALE)
    wrapperAaveBefore = aave.balanceOf(wrapper.address)
    wrapperXaaveBefore = xAAVEa.balanceOf(wrapper.address)

    with brownie.reverts("Insufficient exit liquidity"):
        wrapper.burn(wrapper.balanceOf(AAVE_WHALE), False, 0, aave_whale)


def test_xToken_whale_redeem_fail(deployedContracts):
    aave = deployedContracts['aave']
    wrapper = deployedContracts['wrapper']
    user = deployedContracts['user']
    GNOSIS_SAFE_PROXY = deployedContracts['GNOSIS_SAFE_PROXY']
    xAAVEa = deployedContracts['xAAVEa']

    AAVE_WHALE = '0x26a78d5b6d7a7aceedd1e6ee3229b372a624d8b7'
    aave_whale = {'from': AAVE_WHALE}

    with brownie.reverts("ERC20: burn amount exceeds balance"):
        wrapper.redeemsdxAAVEeaForxAAVEa(
            wrapper.balanceOf(AAVE_WHALE) + 1, aave_whale)
