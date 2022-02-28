import pytest
from brownie import *
import typer
import json
import brownie

# signatures obtained by signing message "Use NFT to access Strategy" using ethersjs
# it is too complicated in python :P

# choose hint drastic fold phone twice inquiry loud when will scheme grunt
COMMON_USER = '0x967e09C8272FFbAD26A3c71E011FEe375E2431f2'
commonUser = {'from': COMMON_USER}
commonSig = {
    "v": 27,
    "r": "0x72b2ace924d2a92769919d31347070d5bc6821f83aec3c1ca8a64fa66c06f493",
    "s": "0x5c43301a003e24866a46d4435dc328135ddf192fb51f036146e2b639ec25254c"
}

# remove delay stool artwork mansion settle layer voice leg shock engage liquid
RARE_USER = '0xD9BFc0fD6797f7f3ce42F12EBC6C11c5d19B757C'
rareUser = {'from': RARE_USER}
rareSig = {
    "v": 27,
    "r": "0xf9978019731cc6f69d4b704c24c1d05f445ef06b74053159278785d76b61a568",
    "s": "0x281b7dc0db807712ab53088411ea323319216efc1a333b90cf71cfe21c1c1fd3"
}

# core comic stage monkey wedding cat rug galaxy grunt hire auto hint
UNIQUE_USER = '0xA30b354F6ed616C20A36E9CB6a5F3324f2fE9349'
uniqueUser = {'from': UNIQUE_USER}
uniqueSig = {
    "v": 28,
    "r": "0x283d3f7f3a84feef87420303ed7f55e715afaf3edc87f43b07b11a0f53d04492",
    "s": "0x35c0382e1fe5e959a0555a6f83bf1c07f9fb202e8b4def540453c0c657fdcdfe"
}

# without NFT
PLEB_USER = '0x283BeabDc7a42FFC4795026B4F902a34E08ef348'
plebUser = {'from': PLEB_USER}

# prod, match with constants on contract
commonNFT = 1
rareNFT = 212
uniqueNFT = 222
createLimit = 223

# test, match with constants on contract
# commonNFT = 1
# rareNFT = 5
# uniqueNFT = 6
# createLimit = 7

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

    deployer = {'from': DEFAULT_DEPLOYER_ACCOUNT}

    multisig = {'from': GNOSIS_SAFE_PROXY}

    controller = Controller.at(deployed[ENV]['CONTROLLER'])

    USDC = '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48'
    usdc = FiatTokenV2_1.at(USDC)

    STKAAVE = '0x4da27a545c0c5B758a6BA100e3a049001de870f5'
    stkAAVE = Contract(STKAAVE)

    WHALE = '0x55fe002aeff02f77364de339a1292923a15844b8'
    whale = {'from': WHALE}

    usdc.transfer(COMMON_USER, usdc.balanceOf(WHALE)/4, whale)
    usdc.transfer(RARE_USER, usdc.balanceOf(WHALE)/3, whale)
    usdc.transfer(UNIQUE_USER, usdc.balanceOf(WHALE)/2, whale)
    usdc.transfer(PLEB_USER, usdc.balanceOf(WHALE), whale)

    proxyRegistry = deployed[ENV]['OPENSEA_PROXY_REGISTRY']
    nft = StakeDaoNFT.deploy(proxyRegistry, deployer)
    for i in range(1, createLimit):
        nft.create(1, 1, "", "", deployer)
    nft.safeTransferFrom(DEFAULT_DEPLOYER_ACCOUNT, COMMON_USER, commonNFT, 1, "", deployer);
    nft.safeTransferFrom(DEFAULT_DEPLOYER_ACCOUNT, RARE_USER, rareNFT, 1, "", deployer);
    nft.safeTransferFrom(DEFAULT_DEPLOYER_ACCOUNT, UNIQUE_USER, uniqueNFT, 1, "", deployer);

    usdcVault = StakeDaoAaveUSDCVault.deploy(
        USDC, controller.address, GNOSIS_SAFE_PROXY, nft.address, deployer)

    usdcStrategy = StrategyAaveUSDCLeverage.deploy(
        GNOSIS_SAFE_PROXY, controller.address, deployer)

    usdcStrategy.maxApprove(multisig)

    controller.approveStrategy(USDC, usdcStrategy.address, multisig)
    controller.setStrategy(USDC, usdcStrategy.address, multisig)
    controller.setVault(USDC, usdcVault.address, multisig)

    return {"treasuryVault": treasuryVault,
            "multisig": multisig,
            "deployer": deployer,
            "DEFAULT_DEPLOYER_ACCOUNT": DEFAULT_DEPLOYER_ACCOUNT,
            "USDC": USDC,
            "usdc": usdc,
            "usdcVault": usdcVault,
            "usdcStrategy": usdcStrategy,
            "controller": controller,
            "nft": nft,
            "STKAAVE": STKAAVE,
            "stkAAVE": stkAAVE,
            "TREASURY_VAULT": TREASURY_VAULT}

def test_usdc_vault_deposit_common(deployedContracts):
    usdc = deployedContracts['usdc']
    usdcVault = deployedContracts['usdcVault']
    nft = deployedContracts['nft']

    shareBefore = usdcVault.balanceOf(COMMON_USER)
    senderUSDCBefore = usdc.balanceOf(COMMON_USER)
    vaultUSDCBefore = usdc.balanceOf(usdcVault.address)
    print('senderUSDCBefore', senderUSDCBefore / 10**6)

    usdc.approve(usdcVault.address, usdc.balanceOf(COMMON_USER), commonUser)
    nft.setApprovalForAll(usdcVault.address, True, commonUser)
    usdcVault.deposit(9_000 * 10**6, commonNFT, commonSig['v'], commonSig['r'], commonSig['s'], commonUser)

    shareAfter = usdcVault.balanceOf(COMMON_USER)
    senderUSDCAfter = usdc.balanceOf(COMMON_USER)
    vaultUSDCAfter = usdc.balanceOf(usdcVault.address)

    print("Minted shares", (shareAfter - shareBefore) / 10**6)

    assert shareAfter - shareBefore > 0
    assert senderUSDCBefore - senderUSDCAfter > 0
    assert senderUSDCBefore - senderUSDCAfter == vaultUSDCAfter - vaultUSDCBefore


def test_usdc_vault_deposit_rare(deployedContracts):
    usdc = deployedContracts['usdc']
    usdcVault = deployedContracts['usdcVault']
    nft = deployedContracts['nft']

    shareBefore = usdcVault.balanceOf(RARE_USER)
    senderUSDCBefore = usdc.balanceOf(RARE_USER)
    vaultUSDCBefore = usdc.balanceOf(usdcVault.address)
    print('senderUSDCBefore', senderUSDCBefore / 10**6)

    usdc.approve(usdcVault.address, usdc.balanceOf(RARE_USER), rareUser)
    nft.setApprovalForAll(usdcVault.address, True, rareUser)
    usdcVault.deposit(29_000 * 10**6, rareNFT, rareSig['v'], rareSig['r'], rareSig['s'], rareUser)

    shareAfter = usdcVault.balanceOf(RARE_USER)
    senderUSDCAfter = usdc.balanceOf(RARE_USER)
    vaultUSDCAfter = usdc.balanceOf(usdcVault.address)

    print("Minted shares", (shareAfter - shareBefore) / 10**6)

    assert shareAfter - shareBefore > 0
    assert senderUSDCBefore - senderUSDCAfter > 0
    assert senderUSDCBefore - senderUSDCAfter == vaultUSDCAfter - vaultUSDCBefore


def test_usdc_vault_deposit_unique(deployedContracts):
    usdc = deployedContracts['usdc']
    usdcVault = deployedContracts['usdcVault']
    nft = deployedContracts['nft']

    shareBefore = usdcVault.balanceOf(UNIQUE_USER)
    senderUSDCBefore = usdc.balanceOf(UNIQUE_USER)
    vaultUSDCBefore = usdc.balanceOf(usdcVault.address)
    print('senderUSDCBefore', senderUSDCBefore / 10**6)

    usdc.approve(usdcVault.address, usdc.balanceOf(UNIQUE_USER), uniqueUser)
    nft.setApprovalForAll(usdcVault.address, True, uniqueUser)
    usdcVault.deposit(119_000 * 10**6, uniqueNFT, uniqueSig['v'], uniqueSig['r'], uniqueSig['s'], uniqueUser)

    shareAfter = usdcVault.balanceOf(UNIQUE_USER)
    senderUSDCAfter = usdc.balanceOf(UNIQUE_USER)
    vaultUSDCAfter = usdc.balanceOf(usdcVault.address)

    print("Minted shares", (shareAfter - shareBefore) / 10**6)

    assert shareAfter - shareBefore > 0
    assert senderUSDCBefore - senderUSDCAfter > 0
    assert senderUSDCBefore - senderUSDCAfter == vaultUSDCAfter - vaultUSDCBefore


def test_deposit_limits_before_release(deployedContracts):
    usdcVault = deployedContracts['usdcVault']

    with brownie.reverts('Exceeds limit'):
        usdcVault.deposit(2_000 * 10**6, commonUser)

    with brownie.reverts('Exceeds limit'):
        usdcVault.deposit(2_000 * 10**6, rareUser)

    with brownie.reverts('Exceeds limit'):
        usdcVault.deposit(2_000 * 10**6, uniqueUser)

def test_claim_nft_before_release(deployedContracts):
    usdcVault = deployedContracts['usdcVault']

    with brownie.reverts('!publicRelease'):
        usdcVault.claimNFT(commonUser)

    with brownie.reverts('!publicRelease'):
        usdcVault.claimNFT(rareUser)

    with brownie.reverts('!publicRelease'):
        usdcVault.claimNFT(uniqueUser)

def test_usdc_vault_deposit_pleb(deployedContracts):
    usdc = deployedContracts['usdc']
    usdcVault = deployedContracts['usdcVault']

    usdc.approve(usdcVault.address, usdc.balanceOf(PLEB_USER), plebUser)
    with brownie.reverts('NFT not locked'):
        usdcVault.deposit(2_000 * 10**6, plebUser)

    chain.sleep(31 * 86400)
    usdcVault.deposit(2_000 * 10**6, plebUser)

def test_deposit_limits_after_release(deployedContracts):
    usdc = deployedContracts['usdc']
    usdcVault = deployedContracts['usdcVault']
    nft = deployedContracts['nft']

    usdcVault.deposit(2_000 * 10**6, commonUser)
    usdcVault.deposit(2_000 * 10**6, rareUser)
    usdcVault.deposit(2_000 * 10**6, uniqueUser)

def test_claim_nft_after_release(deployedContracts):
    usdcVault = deployedContracts['usdcVault']
    usdcVault.claimNFT(commonUser)
    usdcVault.claimNFT(rareUser)
    usdcVault.claimNFT(uniqueUser)

def test_usdc_vault_earn(deployedContracts):
    USDC = deployedContracts['USDC']
    usdc = deployedContracts['usdc']
    usdcVault = deployedContracts['usdcVault']
    usdcStrategy = deployedContracts['usdcStrategy']
    deployer = deployedContracts['deployer']

    vaultUSDCBefore = usdc.balanceOf(usdcVault.address)

    usdcVault.earn(deployer)

    vaultUSDCAfter = usdc.balanceOf(usdcVault.address)

    print("Vault USDC decrease", (vaultUSDCBefore - vaultUSDCAfter) / 10**6)

    position = usdcStrategy.getCurrentPosition()
    print("dep, borr", position[0] / 10**6, position[1] / 10**6)

    assert vaultUSDCBefore - vaultUSDCAfter > 0
    assert 0.74 <= position[1] / position[0] <= 0.76


def test_strategy_claim_stkAAVE(deployedContracts):
    USDC = deployedContracts['USDC']
    usdc = deployedContracts['usdc']
    usdcVault = deployedContracts['usdcVault']
    usdcStrategy = deployedContracts['usdcStrategy']
    deployer = deployedContracts['deployer']
    multisig = deployedContracts['multisig']
    stkAAVE = deployedContracts['stkAAVE']

    chain.sleep(5 * 86400)
    chain.mine(100)

    stratStkAAVEBefore = stkAAVE.balanceOf(usdcStrategy.address)
    usdcStrategy.claimStkAAVE(multisig)
    stratStkAAVEAfter = stkAAVE.balanceOf(usdcStrategy.address)

    print("stkAAVE increase", (stratStkAAVEAfter - stratStkAAVEBefore) / 10**18)

    assert stratStkAAVEAfter - stratStkAAVEBefore > 0


def test_strategy_harvest(deployedContracts):
    USDC = deployedContracts['USDC']
    usdc = deployedContracts['usdc']
    usdcVault = deployedContracts['usdcVault']
    usdcStrategy = deployedContracts['usdcStrategy']
    deployer = deployedContracts['deployer']
    multisig = deployedContracts['multisig']
    stkAAVE = deployedContracts['stkAAVE']
    TREASURY_VAULT = deployedContracts['TREASURY_VAULT']

    chain.sleep(11 * 86400)
    chain.mine(100)

    position_1 = usdcStrategy.getCurrentPosition()
    print("dep, borr", position_1[0] / 10**6, position_1[1] / 10**6)
    treasuryUSDCBefore = usdc.balanceOf(TREASURY_VAULT)
    print('treasuryUSDCBefore', treasuryUSDCBefore / 10**6)

    usdcStrategy.harvest(multisig)

    treasuryUSDCAfter = usdc.balanceOf(TREASURY_VAULT)
    print('treasuryUSDCAfter', treasuryUSDCAfter / 10**6)
    position_2 = usdcStrategy.getCurrentPosition()
    print("dep, borr", position_2[0] / 10**6, position_2[1] / 10**6)

    assert treasuryUSDCAfter - treasuryUSDCBefore > 0
    assert position_2[0] > position_1[0]
    assert position_2[1] > position_1[1]
    assert 0.74 <= position_2[1] / position_2[0] <= 0.76
    print("c-ratio", position_2[1] / position_2[0])


def test_vault_withdraw(deployedContracts):
    USDC = deployedContracts['USDC']
    usdc = deployedContracts['usdc']
    usdcVault = deployedContracts['usdcVault']
    usdcStrategy = deployedContracts['usdcStrategy']
    deployer = deployedContracts['deployer']
    multisig = deployedContracts['multisig']
    stkAAVE = deployedContracts['stkAAVE']
    TREASURY_VAULT = deployedContracts['TREASURY_VAULT']

    position_1 = usdcStrategy.getCurrentPosition()
    print("dep, borr", position_1[0] / 10**6, position_1[1] / 10**6)
    treasuryUSDCBefore = usdc.balanceOf(TREASURY_VAULT)
    print('treasuryUSDCBefore', treasuryUSDCBefore / 10**6)
    userUSDCBefore = usdc.balanceOf(UNIQUE_USER)
    print('userUSDCBefore', userUSDCBefore / 10**6)

    print("strat USDC", usdc.balanceOf(usdcStrategy.address))

    usdcVault.withdraw(15_000 * 10**6, uniqueUser)

    userUSDCAfter = usdc.balanceOf(UNIQUE_USER)
    print('userUSDCAfter', userUSDCAfter / 10**6)
    treasuryUSDCAfter = usdc.balanceOf(TREASURY_VAULT)
    print('treasuryUSDCAfter', treasuryUSDCAfter / 10**6)
    position_2 = usdcStrategy.getCurrentPosition()
    print("dep, borr", position_2[0] / 10**6, position_2[1] / 10**6)

    assert userUSDCAfter > userUSDCBefore
    assert treasuryUSDCAfter - treasuryUSDCBefore > 0
    assert position_2[0] < position_1[0]
    assert position_2[1] < position_1[1]
    assert 0.74 <= position_2[1] / position_2[0] <= 0.76
    print("c-ratio", position_2[1] / position_2[0])


def test_vault_withdraw_2(deployedContracts):
    USDC = deployedContracts['USDC']
    usdc = deployedContracts['usdc']
    usdcVault = deployedContracts['usdcVault']
    usdcStrategy = deployedContracts['usdcStrategy']
    deployer = deployedContracts['deployer']
    multisig = deployedContracts['multisig']
    stkAAVE = deployedContracts['stkAAVE']
    TREASURY_VAULT = deployedContracts['TREASURY_VAULT']

    position_1 = usdcStrategy.getCurrentPosition()
    print("dep, borr", position_1[0] / 10**6, position_1[1] / 10**6)
    treasuryUSDCBefore = usdc.balanceOf(TREASURY_VAULT)
    print('treasuryUSDCBefore', treasuryUSDCBefore / 10**6)
    userUSDCBefore = usdc.balanceOf(UNIQUE_USER)
    print('userUSDCBefore', userUSDCBefore / 10**6)

    usdcVault.withdraw(30_000 * 10**6, uniqueUser)

    userUSDCAfter = usdc.balanceOf(UNIQUE_USER)
    print('userUSDCAfter', userUSDCAfter / 10**6)
    treasuryUSDCAfter = usdc.balanceOf(TREASURY_VAULT)
    print('treasuryUSDCAfter', treasuryUSDCAfter / 10**6)
    position_2 = usdcStrategy.getCurrentPosition()
    print("dep, borr", position_2[0] / 10**6, position_2[1] / 10**6)

    assert userUSDCAfter > userUSDCBefore
    assert treasuryUSDCAfter - treasuryUSDCBefore > 0
    assert position_2[0] < position_1[0]
    assert position_2[1] < position_1[1]
    print("c-ratio", position_2[1] / position_2[0])
    assert 0.74 <= position_2[1] / position_2[0] <= 0.76
    # chain.snapshot()


def test_vault_withdraw_3(deployedContracts):
    USDC = deployedContracts['USDC']
    usdc = deployedContracts['usdc']
    usdcVault = deployedContracts['usdcVault']
    usdcStrategy = deployedContracts['usdcStrategy']
    deployer = deployedContracts['deployer']
    multisig = deployedContracts['multisig']
    stkAAVE = deployedContracts['stkAAVE']
    TREASURY_VAULT = deployedContracts['TREASURY_VAULT']

    position_1 = usdcStrategy.getCurrentPosition()
    print("dep, borr", position_1[0] / 10**6, position_1[1] / 10**6)
    treasuryUSDCBefore = usdc.balanceOf(TREASURY_VAULT)
    print('treasuryUSDCBefore', treasuryUSDCBefore / 10**6)
    userUSDCBefore = usdc.balanceOf(UNIQUE_USER)
    print('userUSDCBefore', userUSDCBefore / 10**6)

    usdcVault.withdraw(54_000 * 10**6, uniqueUser)

    userUSDCAfter = usdc.balanceOf(UNIQUE_USER)
    print('userUSDCAfter', userUSDCAfter / 10**6)
    treasuryUSDCAfter = usdc.balanceOf(TREASURY_VAULT)
    print('treasuryUSDCAfter', treasuryUSDCAfter / 10**6)
    position_2 = usdcStrategy.getCurrentPosition()
    print("dep, borr", position_2[0] / 10**6, position_2[1] / 10**6)

    assert userUSDCAfter > userUSDCBefore
    assert treasuryUSDCAfter - treasuryUSDCBefore > 0
    assert position_2[0] < position_1[0]
    assert position_2[1] < position_1[1]
    print("c-ratio", position_2[1] / position_2[0])
    assert 0.74 <= position_2[1] / position_2[0] <= 0.82
    chain.snapshot()


def test_vault_withdraw_4(deployedContracts):
    USDC = deployedContracts['USDC']
    usdc = deployedContracts['usdc']
    usdcVault = deployedContracts['usdcVault']
    usdcStrategy = deployedContracts['usdcStrategy']
    deployer = deployedContracts['deployer']
    multisig = deployedContracts['multisig']
    stkAAVE = deployedContracts['stkAAVE']
    TREASURY_VAULT = deployedContracts['TREASURY_VAULT']

    position_1 = usdcStrategy.getCurrentPosition()
    print("dep, borr", position_1[0] / 10**6, position_1[1] / 10**6)
    treasuryUSDCBefore = usdc.balanceOf(TREASURY_VAULT)
    print('treasuryUSDCBefore', treasuryUSDCBefore / 10**6)
    userUSDCBefore = usdc.balanceOf(UNIQUE_USER)
    print('userUSDCBefore', userUSDCBefore / 10**6)

    print("balance(), _shares, totalSupply()", usdcVault.balance(),
          usdcVault.balanceOf(UNIQUE_USER), usdcVault.totalSupply())
    print("balanceOfPool()", usdcStrategy.balanceOfPool())

    usdcVault.withdraw(usdcVault.balanceOf(UNIQUE_USER), uniqueUser)

    userUSDCAfter = usdc.balanceOf(UNIQUE_USER)
    print('userUSDCAfter', userUSDCAfter / 10**6)
    treasuryUSDCAfter = usdc.balanceOf(TREASURY_VAULT)
    print('treasuryUSDCAfter', treasuryUSDCAfter / 10**6)
    position_2 = usdcStrategy.getCurrentPosition()
    print("dep, borr", position_2[0] / 10**6, position_2[1] / 10**6)

    assert userUSDCAfter > userUSDCBefore
    assert treasuryUSDCAfter - treasuryUSDCBefore > 0
    assert position_2[0] < position_1[0]
    assert position_2[1] < position_1[1]
    assert position_2[1] == position_2[0] == 0


def test_controller_emergency_withdrawAll_to_vault(deployedContracts):
    chain.revert()
    USDC = deployedContracts['USDC']
    usdc = deployedContracts['usdc']
    usdcVault = deployedContracts['usdcVault']
    usdcStrategy = deployedContracts['usdcStrategy']
    deployer = deployedContracts['deployer']
    multisig = deployedContracts['multisig']
    stkAAVE = deployedContracts['stkAAVE']
    TREASURY_VAULT = deployedContracts['TREASURY_VAULT']
    controller = deployedContracts['controller']

    position_1 = usdcStrategy.getCurrentPosition()
    print("dep, borr", position_1[0] / 10**6, position_1[1] / 10**6)
    vaultUSDCBefore = usdc.balanceOf(usdcVault.address)
    print('vaultUSDCBefore', vaultUSDCBefore / 10**6)
    print("balanceOfPool() before", usdcStrategy.balanceOfPool())

    # usdcStrategy.withdrawToVault(usdcStrategy.balanceOfPool(), multisig)
    controller.withdrawAll(USDC, multisig)

    print("balanceOfPool() after", usdcStrategy.balanceOfPool())
    vaultUSDCAfter = usdc.balanceOf(usdcVault.address)
    print('vaultUSDCAfter', vaultUSDCAfter / 10**6)
    position_2 = usdcStrategy.getCurrentPosition()
    print("dep, borr", position_2[0] / 10**6, position_2[1] / 10**6)

    assert vaultUSDCAfter > vaultUSDCBefore
    assert vaultUSDCAfter - vaultUSDCBefore >= usdcStrategy.balanceOfPool()
    assert position_2[0] < position_1[0]
    assert position_2[1] < position_1[1]
    assert position_2[1] == position_2[0] == 0
