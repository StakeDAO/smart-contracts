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

    SDT = deployed[ENV]['SDT']
    sdt = Contract(SDT)

    SBTC_CRV = deployed[ENV]['SBTC_CRV']

    THREE_CRV = deployed[ENV]['THREE_CRV']

    EURS_CRV = deployed[ENV]['EURS_CRV']

    DAI = deployed[ENV]['DAI']
    dai = Contract(DAI)

    VESTING_ESCROW = deployed[ENV]['VESTING_ESCROW']

    ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"

    SDT_STAKE_AMOUNT = 100*10**18

    sdt.transfer(DEFAULT_DEPLOYER_ACCOUNT,
                 10**6 * 10**18, {'from': VESTING_ESCROW})
    sdt.transfer(accounts[1], 10**6 * 10**18, {'from': VESTING_ESCROW})
    sdt.transfer(accounts[2], 2 * 10**6 * 10**18, {'from': VESTING_ESCROW})
    sdt.transfer(accounts[3], 10**6 * 10**18, {'from': VESTING_ESCROW})

    deployer = {'from': DEFAULT_DEPLOYER_ACCOUNT}

    multisig = {'from': GNOSIS_SAFE_PROXY}

    # deploy NFT contract
    # cardNft = ERC1155Tradable.deploy("SDT NFT Cards", "SDTC", ZERO_ADDRESS, deployer)

    # deploy SdtPool
    # sdtPool = SdtPool.deploy(cardNft.address, sdt.address, DAI, deployer)

    # deploy Sanctuary
    sanctuary = Sanctuary.deploy(sdt.address, deployer)

    # set setRewardDistribution as TreasuryVault
    # sdtPool.setRewardDistribution(treasuryVault.address, deployer)

    # give sdtPool a minter role
    # cardNft.addMinter(sdtPool.address, deployer)

    # call setGovernanceStaking on Treasury Vault
    treasuryVault.setGovernanceStaking(sanctuary.address, multisig)

    # set multisig as an authorized address for Treasuty Vault
    treasuryVault.setAuthorized(GNOSIS_SAFE_PROXY, multisig)

    return {"dai": dai, "treasuryVault": treasuryVault, "multisig": multisig, "deployer": deployer, "DAI": DAI, "SDT": SDT, "SBTC_CRV": SBTC_CRV, "THREE_CRV": THREE_CRV, "EURS_CRV": EURS_CRV, "SDT_STAKE_AMOUNT": SDT_STAKE_AMOUNT, "sdt": sdt, "sanctuary": sanctuary}


def test_swap_tokens_for_sdt(deployedContracts):
    # swap treasury fees for dai
    treasuryVault = deployedContracts["treasuryVault"]
    deployer = deployedContracts["deployer"]
    multisig = deployedContracts["multisig"]
    SBTC_CRV = deployedContracts["SBTC_CRV"]
    THREE_CRV = deployedContracts["THREE_CRV"]
    EURS_CRV = deployedContracts["EURS_CRV"]
    DAI = deployedContracts["DAI"]
    sanctuary = deployedContracts['sanctuary']
    sdt = deployedContracts['sdt']

    treasuryVault.setRewards(sdt.address, multisig)
    rewardToken = treasuryVault.rewards()

    assert rewardToken == sdt.address

    # beforeSbtcCrvBal = Contract(SBTC_CRV).balanceOf(treasuryVault.address)
    # beforeThreeCrvBal = Contract(THREE_CRV).balanceOf(treasuryVault.address)
    beforeEursCrvBal = Contract(EURS_CRV).balanceOf(treasuryVault.address)

    # assert beforeSbtcCrvBal > 0
    # assert beforeThreeCrvBal > 0
    assert beforeEursCrvBal > 0

    assert Contract(rewardToken).balanceOf(treasuryVault.address) == 0

    # treasuryVault.swapViaZap(SBTC_CRV, rewardToken, beforeSbtcCrvBal, multisig)
    # treasuryVault.swapViaZap(THREE_CRV, rewardToken,
    #                          beforeThreeCrvBal, multisig)
    treasuryVault.swapViaZap(EURS_CRV, rewardToken, beforeEursCrvBal, multisig)
    treasuryVault.convert(EURS_CRV, rewardToken, beforeEursCrvBal, multisig)

    # assert Contract(SBTC_CRV).balanceOf(treasuryVault.address) == 0
    # assert Contract(THREE_CRV).balanceOf(treasuryVault.address) == 0
    assert Contract(EURS_CRV).balanceOf(treasuryVault.address) == 0
    treasurySDTBal = Contract(rewardToken).balanceOf(treasuryVault.address)
    print("treasurySDTBal", treasurySDTBal / 10**18)
    assert treasurySDTBal > 0


def test_stake_sdt_on_empty_sanctuary(deployedContracts):
    sdt = deployedContracts["sdt"]
    sanctuary = deployedContracts['sanctuary']
    deployer = deployedContracts["deployer"]
    SDT_STAKE_AMOUNT = deployedContracts["SDT_STAKE_AMOUNT"]
    treasuryVault = deployedContracts["treasuryVault"]

    user0xSDTBefore = sanctuary.balanceOf(deployer["from"])
    user0SDTBefore = sdt.balanceOf(deployer['from'])
    user1xSDTBefore = sanctuary.balanceOf(accounts[1])
    user1SDTBefore = sdt.balanceOf(accounts[1])
    user2xSDTBefore = sanctuary.balanceOf(accounts[2])
    user2SDTBefore = sdt.balanceOf(accounts[2])
    sanctuaryxSDTBefore = sanctuary.totalSupply()
    sanctuarySDTBefore = sdt.balanceOf(sanctuary.address)
    print()
    print("STAKE")
    print('user0xSDTBefore', user0xSDTBefore / 10**18)
    print('user0SDTBefore', user0SDTBefore / 10**18)
    print('user1xSDTBefore', user1xSDTBefore / 10**18)
    print('user1SDTBefore', user1SDTBefore / 10**18)
    print('user2xSDTBefore', user2xSDTBefore / 10**18)
    print('user2SDTBefore', user2SDTBefore / 10**18)
    print('sanctuaryxSDTBefore', sanctuaryxSDTBefore / 10**18)
    print('sanctuarySDTBefore', sanctuarySDTBefore / 10**18)
    print()
    # approve and stake sdt
    sdt.approve(sanctuary.address, 10**9 * 10**18, deployer)
    sdt.approve(sanctuary.address, 10**9 * 10**18, {'from': accounts[1]})
    sdt.approve(sanctuary.address, 10**9 * 10**18, {'from': accounts[2]})
    sanctuary.enter(SDT_STAKE_AMOUNT, deployer)
    sanctuary.enter(1000 * 10**18, {'from': accounts[1]})
    sanctuary.enter(1000000 * 10**18, {'from': accounts[2]})

    user0xSDTAfter = sanctuary.balanceOf(deployer["from"])
    user0SDTAfter = sdt.balanceOf(deployer['from'])
    user1xSDTAfter = sanctuary.balanceOf(accounts[1])
    user1SDTAfter = sdt.balanceOf(accounts[1])
    user2xSDTAfter = sanctuary.balanceOf(accounts[2])
    user2SDTAfter = sdt.balanceOf(accounts[2])
    sanctuaryxSDTAfter = sanctuary.totalSupply()
    sanctuarySDTAfter = sdt.balanceOf(sanctuary.address)
    print()
    print('user0xSDTAfter', user0xSDTAfter / 10**18)
    print('user0SDTAfter', user0SDTAfter / 10**18)
    print('user1xSDTAfter', user1xSDTAfter / 10**18)
    print('user1SDTAfter', user1SDTAfter / 10**18)
    print('user2xSDTAfter', user2xSDTAfter / 10**18)
    print('user2SDTAfter', user2SDTAfter / 10**18)
    print('sanctuaryxSDTAfter', sanctuaryxSDTAfter / 10**18)
    print('sanctuarySDTAfter', sanctuarySDTAfter / 10**18)
    print()

    assert sanctuaryxSDTAfter - sanctuaryxSDTBefore == user0xSDTAfter - \
        user0xSDTBefore + user1xSDTAfter - \
        user1xSDTBefore + user2xSDTAfter - user2xSDTBefore
    assert user0SDTBefore - user0SDTAfter + user1SDTBefore - user1SDTAfter + \
        user2SDTBefore - user2SDTAfter == sanctuarySDTAfter - sanctuarySDTBefore


def test_deposit_sdt_to_sanctuary(deployedContracts):
    # call toGovernanceStaking from treasury
    deployer = deployedContracts["deployer"]
    multisig = deployedContracts["multisig"]
    treasuryVault = deployedContracts["treasuryVault"]
    dai = deployedContracts["dai"]
    sanctuary = deployedContracts['sanctuary']
    sdt = deployedContracts['sdt']

    chain.sleep(7 * 86400)
    treasuryVaultSDTBefore = sdt.balanceOf(treasuryVault.address)
    sanctuarySDTBefore = sdt.balanceOf(sanctuary.address)

    # treasuryVault.toGovernance(sdt.address, treasuryVaultSDTBefore, multisig)
    # sdt.transfer(sanctuary.address, treasuryVaultSDTBefore, multisig)
    sanctuary.setRewardDistribution(treasuryVault.address, deployer)
    treasuryVault.toGovernanceStaking(multisig)

    treasuryVaultSDTAfter = sdt.balanceOf(treasuryVault.address)
    sanctuarySDTAfter = sdt.balanceOf(sanctuary.address)
    print("SDT Sanctuary receives:",
          (sanctuarySDTAfter - sanctuarySDTBefore) / 10**18)
    assert treasuryVaultSDTBefore - \
        treasuryVaultSDTAfter == sanctuarySDTAfter - sanctuarySDTBefore
    chain.snapshot()


def test_unstake_sdt(deployedContracts):
    sdt = deployedContracts["sdt"]
    sanctuary = deployedContracts['sanctuary']
    deployer = deployedContracts["deployer"]
    SDT_STAKE_AMOUNT = deployedContracts["SDT_STAKE_AMOUNT"]
    treasuryVault = deployedContracts["treasuryVault"]
    multisig = deployedContracts["multisig"]

    user0xSDTBefore = sanctuary.balanceOf(deployer["from"])
    user0SDTBefore = sdt.balanceOf(deployer['from'])
    user1xSDTBefore = sanctuary.balanceOf(accounts[1])
    user1SDTBefore = sdt.balanceOf(accounts[1])
    user2xSDTBefore = sanctuary.balanceOf(accounts[2])
    user2SDTBefore = sdt.balanceOf(accounts[2])
    sanctuaryxSDTBefore = sanctuary.totalSupply()
    sanctuarySDTBefore = sdt.balanceOf(sanctuary.address)
    print()
    print("UNSTAKE")
    print('user0xSDTBefore', user0xSDTBefore / 10**18)
    print('user0SDTBefore', user0SDTBefore / 10**18)
    print('user1xSDTBefore', user1xSDTBefore / 10**18)
    print('user1SDTBefore', user1SDTBefore / 10**18)
    print('user2xSDTBefore', user2xSDTBefore / 10**18)
    print('user2SDTBefore', user2SDTBefore / 10**18)
    print('sanctuaryxSDTBefore', sanctuaryxSDTBefore / 10**18)
    print('sanctuarySDTBefore', sanctuarySDTBefore / 10**18)
    print()
    # sdt.transfer(sanctuary.address, 10**5 * 10**18, multisig)
    sanctuary.leave(SDT_STAKE_AMOUNT, deployer)
    sanctuary.leave(1000 * 10**18, {'from': accounts[1]})
    sanctuary.leave(1000000 * 10**18, {'from': accounts[2]})

    user0xSDTAfter = sanctuary.balanceOf(deployer["from"])
    user0SDTAfter = sdt.balanceOf(deployer['from'])
    user1xSDTAfter = sanctuary.balanceOf(accounts[1])
    user1SDTAfter = sdt.balanceOf(accounts[1])
    user2xSDTAfter = sanctuary.balanceOf(accounts[2])
    user2SDTAfter = sdt.balanceOf(accounts[2])
    sanctuaryxSDTAfter = sanctuary.totalSupply()
    sanctuarySDTAfter = sdt.balanceOf(sanctuary.address)
    print()
    print('user0xSDTAfter', user0xSDTAfter / 10**18)
    print('user0SDTAfter', user0SDTAfter / 10**18)
    print('user1xSDTAfter', user1xSDTAfter / 10**18)
    print('user1SDTAfter', user1SDTAfter / 10**18)
    print('user2xSDTAfter', user2xSDTAfter / 10**18)
    print('user2SDTAfter', user2SDTAfter / 10**18)
    print('sanctuaryxSDTAfter', sanctuaryxSDTAfter / 10**18)
    print('sanctuarySDTAfter', sanctuarySDTAfter / 10**18)
    print()

    assert sanctuaryxSDTBefore - sanctuaryxSDTAfter == user0xSDTBefore - \
        user0xSDTAfter + user1xSDTBefore - \
        user1xSDTAfter + user2xSDTBefore - user2xSDTAfter
    assert user0SDTAfter - user0SDTBefore + user1SDTAfter - user1SDTBefore + \
        user2SDTAfter - user2SDTBefore == sanctuarySDTBefore - sanctuarySDTAfter


def test_stake_sdt_on_nonempty_sanctuary(deployedContracts):
    sdt = deployedContracts["sdt"]
    sanctuary = deployedContracts['sanctuary']
    deployer = deployedContracts["deployer"]
    SDT_STAKE_AMOUNT = deployedContracts["SDT_STAKE_AMOUNT"]
    treasuryVault = deployedContracts["treasuryVault"]
    multisig = deployedContracts["multisig"]
    # depositing 100k SDT to sanctuary, making it non-empty
    sdt.transfer(sanctuary.address, 10**5 * 10**18, multisig)
    # sdt.approve(sanctuary.address, 10**9 * 10**18, multisig)
    # sanctuary.enter(10**5 * 10**18, multisig)

    user0xSDTBefore = sanctuary.balanceOf(deployer["from"])
    user0SDTBefore = sdt.balanceOf(deployer['from'])
    user1xSDTBefore = sanctuary.balanceOf(accounts[1])
    user1SDTBefore = sdt.balanceOf(accounts[1])
    user2xSDTBefore = sanctuary.balanceOf(accounts[2])
    user2SDTBefore = sdt.balanceOf(accounts[2])
    sanctuaryxSDTBefore = sanctuary.totalSupply()
    sanctuarySDTBefore = sdt.balanceOf(sanctuary.address)
    print()
    print("STAKE ON NON-EMPTY SCENE #1")
    print('user0xSDTBefore', user0xSDTBefore / 10**18)
    print('user0SDTBefore', user0SDTBefore / 10**18)
    print('user1xSDTBefore', user1xSDTBefore / 10**18)
    print('user1SDTBefore', user1SDTBefore / 10**18)
    print('user2xSDTBefore', user2xSDTBefore / 10**18)
    print('user2SDTBefore', user2SDTBefore / 10**18)
    print('sanctuaryxSDTBefore', sanctuaryxSDTBefore / 10**18)
    print('sanctuarySDTBefore', sanctuarySDTBefore / 10**18)
    print()
    # approve and stake sdt
    sdt.approve(sanctuary.address, 10**9 * 10**18, deployer)
    sdt.approve(sanctuary.address, 10**9 * 10**18, {'from': accounts[1]})
    sdt.approve(sanctuary.address, 10**9 * 10**18, {'from': accounts[2]})
    sanctuary.enter(SDT_STAKE_AMOUNT, deployer)
    sanctuary.enter(1000 * 10**18, {'from': accounts[1]})
    sanctuary.enter(1000000 * 10**18, {'from': accounts[2]})

    user0xSDTAfter = sanctuary.balanceOf(deployer["from"])
    user0SDTAfter = sdt.balanceOf(deployer['from'])
    user1xSDTAfter = sanctuary.balanceOf(accounts[1])
    user1SDTAfter = sdt.balanceOf(accounts[1])
    user2xSDTAfter = sanctuary.balanceOf(accounts[2])
    user2SDTAfter = sdt.balanceOf(accounts[2])
    sanctuaryxSDTAfter = sanctuary.totalSupply()
    sanctuarySDTAfter = sdt.balanceOf(sanctuary.address)
    print()
    print('user0xSDTAfter', user0xSDTAfter / 10**18)
    print('user0SDTAfter', user0SDTAfter / 10**18)
    print('user1xSDTAfter', user1xSDTAfter / 10**18)
    print('user1SDTAfter', user1SDTAfter / 10**18)
    print('user2xSDTAfter', user2xSDTAfter / 10**18)
    print('user2SDTAfter', user2SDTAfter / 10**18)
    print('sanctuaryxSDTAfter', sanctuaryxSDTAfter / 10**18)
    print('sanctuarySDTAfter', sanctuarySDTAfter / 10**18)
    print()

    assert sanctuaryxSDTAfter - sanctuaryxSDTBefore == user0xSDTAfter - \
        user0xSDTBefore + user1xSDTAfter - \
        user1xSDTBefore + user2xSDTAfter - user2xSDTBefore
    assert user0SDTBefore - user0SDTAfter + user1SDTBefore - user1SDTAfter + \
        user2SDTBefore - user2SDTAfter == sanctuarySDTAfter - sanctuarySDTBefore


def test_unstake_sdt_on_nonempty_sanctuary(deployedContracts):
    # A receives 100k SDT as he was first to stake, after SDT fee deposit
    sdt = deployedContracts["sdt"]
    sanctuary = deployedContracts['sanctuary']
    deployer = deployedContracts["deployer"]
    SDT_STAKE_AMOUNT = deployedContracts["SDT_STAKE_AMOUNT"]
    treasuryVault = deployedContracts["treasuryVault"]
    multisig = deployedContracts["multisig"]

    user0xSDTBefore = sanctuary.balanceOf(deployer["from"])
    user0SDTBefore = sdt.balanceOf(deployer['from'])
    user1xSDTBefore = sanctuary.balanceOf(accounts[1])
    user1SDTBefore = sdt.balanceOf(accounts[1])
    user2xSDTBefore = sanctuary.balanceOf(accounts[2])
    user2SDTBefore = sdt.balanceOf(accounts[2])
    sanctuaryxSDTBefore = sanctuary.totalSupply()
    sanctuarySDTBefore = sdt.balanceOf(sanctuary.address)
    print()
    print("UNSTAKE ON NON_EMPTY SCENE #1")
    print('user0xSDTBefore', user0xSDTBefore / 10**18)
    print('user0SDTBefore', user0SDTBefore / 10**18)
    print('user1xSDTBefore', user1xSDTBefore / 10**18)
    print('user1SDTBefore', user1SDTBefore / 10**18)
    print('user2xSDTBefore', user2xSDTBefore / 10**18)
    print('user2SDTBefore', user2SDTBefore / 10**18)
    print('sanctuaryxSDTBefore', sanctuaryxSDTBefore / 10**18)
    print('sanctuarySDTBefore', sanctuarySDTBefore / 10**18)
    print()
    # sdt.transfer(sanctuary.address, 10**5 * 10**18, multisig)
    sanctuary.leave(user1xSDTBefore, {'from': accounts[1]})
    sanctuary.leave(user0xSDTBefore, deployer)
    sanctuary.leave(user2xSDTBefore, {'from': accounts[2]})

    user0xSDTAfter = sanctuary.balanceOf(deployer["from"])
    user0SDTAfter = sdt.balanceOf(deployer['from'])
    user1xSDTAfter = sanctuary.balanceOf(accounts[1])
    user1SDTAfter = sdt.balanceOf(accounts[1])
    user2xSDTAfter = sanctuary.balanceOf(accounts[2])
    user2SDTAfter = sdt.balanceOf(accounts[2])
    sanctuaryxSDTAfter = sanctuary.totalSupply()
    sanctuarySDTAfter = sdt.balanceOf(sanctuary.address)
    print()
    print('user0xSDTAfter', user0xSDTAfter / 10**18)
    print('user0SDTAfter', user0SDTAfter / 10**18)
    print('user1xSDTAfter', user1xSDTAfter / 10**18)
    print('user1SDTAfter', user1SDTAfter / 10**18)
    print('user2xSDTAfter', user2xSDTAfter / 10**18)
    print('user2SDTAfter', user2SDTAfter / 10**18)
    print("SDT 0 rakes", (user0SDTAfter - user0SDTBefore) / 10**18)
    print("SDT 1 rakes", (user1SDTAfter - user1SDTBefore) / 10**18)
    print("SDT 2 rakes", (user2SDTAfter - user2SDTBefore) / 10**18)
    print('sanctuaryxSDTAfter', sanctuaryxSDTAfter / 10**18)
    print('sanctuarySDTAfter', sanctuarySDTAfter / 10**18)
    print()

    assert sanctuaryxSDTBefore - sanctuaryxSDTAfter == user0xSDTBefore - \
        user0xSDTAfter + user1xSDTBefore - \
        user1xSDTAfter + user2xSDTBefore - user2xSDTAfter
    assert user0SDTAfter - user0SDTBefore + user1SDTAfter - user1SDTBefore + \
        user2SDTAfter - user2SDTBefore == sanctuarySDTBefore - sanctuarySDTAfter
    # A makes 100100 SDT i.e. gets all SDT
    assert user0SDTAfter - user0SDTBefore > 100000 * 10**18
    assert user1SDTAfter - user1SDTBefore > (1000 - 1) * 10**18
    assert user2SDTAfter - user2SDTBefore > (10**6 - 1) * 10**18


def test_unstake_sdt_scene_2(deployedContracts):
    # reverting to state on line 208
    # B, C unstaking 50% of their shares, to stay inside pool for next Fee deposit
    chain.revert()
    sdt = deployedContracts["sdt"]
    sanctuary = deployedContracts['sanctuary']
    deployer = deployedContracts["deployer"]
    SDT_STAKE_AMOUNT = deployedContracts["SDT_STAKE_AMOUNT"]
    treasuryVault = deployedContracts["treasuryVault"]
    multisig = deployedContracts["multisig"]

    user0xSDTBefore = sanctuary.balanceOf(deployer["from"])
    user0SDTBefore = sdt.balanceOf(deployer['from'])
    user1xSDTBefore = sanctuary.balanceOf(accounts[1])
    user1SDTBefore = sdt.balanceOf(accounts[1])
    user2xSDTBefore = sanctuary.balanceOf(accounts[2])
    user2SDTBefore = sdt.balanceOf(accounts[2])
    sanctuaryxSDTBefore = sanctuary.totalSupply()
    sanctuarySDTBefore = sdt.balanceOf(sanctuary.address)
    print()
    print("UNSTAKE SCENE #2")
    print('user0xSDTBefore', user0xSDTBefore / 10**18)
    print('user0SDTBefore', user0SDTBefore / 10**18)
    print('user1xSDTBefore', user1xSDTBefore / 10**18)
    print('user1SDTBefore', user1SDTBefore / 10**18)
    print('user2xSDTBefore', user2xSDTBefore / 10**18)
    print('user2SDTBefore', user2SDTBefore / 10**18)
    print('sanctuaryxSDTBefore', sanctuaryxSDTBefore / 10**18)
    print('sanctuarySDTBefore', sanctuarySDTBefore / 10**18)
    print()
    # sdt.transfer(sanctuary.address, 10**5 * 10**18, multisig)
    sanctuary.leave(SDT_STAKE_AMOUNT, deployer)
    sanctuary.leave((1000 / 2) * 10**18, {'from': accounts[1]})
    sanctuary.leave((1000000 / 2) * 10**18, {'from': accounts[2]})

    user0xSDTAfter = sanctuary.balanceOf(deployer["from"])
    user0SDTAfter = sdt.balanceOf(deployer['from'])
    user1xSDTAfter = sanctuary.balanceOf(accounts[1])
    user1SDTAfter = sdt.balanceOf(accounts[1])
    user2xSDTAfter = sanctuary.balanceOf(accounts[2])
    user2SDTAfter = sdt.balanceOf(accounts[2])
    sanctuaryxSDTAfter = sanctuary.totalSupply()
    sanctuarySDTAfter = sdt.balanceOf(sanctuary.address)
    print()
    print('user0xSDTAfter', user0xSDTAfter / 10**18)
    print('user0SDTAfter', user0SDTAfter / 10**18)
    print('user1xSDTAfter', user1xSDTAfter / 10**18)
    print('user1SDTAfter', user1SDTAfter / 10**18)
    print('user2xSDTAfter', user2xSDTAfter / 10**18)
    print('user2SDTAfter', user2SDTAfter / 10**18)
    print('sanctuaryxSDTAfter', sanctuaryxSDTAfter / 10**18)
    print('sanctuarySDTAfter', sanctuarySDTAfter / 10**18)
    print()

    assert sanctuaryxSDTBefore - sanctuaryxSDTAfter == user0xSDTBefore - \
        user0xSDTAfter + user1xSDTBefore - \
        user1xSDTAfter + user2xSDTBefore - user2xSDTAfter
    assert user0SDTAfter - user0SDTBefore + user1SDTAfter - user1SDTBefore + \
        user2SDTAfter - user2SDTBefore == sanctuarySDTBefore - sanctuarySDTAfter


def test_stake_sdt_on_nonempty_sanctuary_scene_2(deployedContracts):
    # only A approves and stakes sdt
    sdt = deployedContracts["sdt"]
    sanctuary = deployedContracts['sanctuary']
    deployer = deployedContracts["deployer"]
    SDT_STAKE_AMOUNT = deployedContracts["SDT_STAKE_AMOUNT"]
    treasuryVault = deployedContracts["treasuryVault"]
    multisig = deployedContracts["multisig"]
    # depositing 100k SDT to sanctuary
    sdt.transfer(sanctuary.address, 10**5 * 10**18, multisig)
    # sdt.approve(sanctuary.address, 10**9 * 10**18, multisig)
    # sanctuary.enter(10**5 * 10**18, multisig)
    print("SDT Sanctuary receives:", 100000.0)

    user0xSDTBefore = sanctuary.balanceOf(deployer["from"])
    user0SDTBefore = sdt.balanceOf(deployer['from'])
    user1xSDTBefore = sanctuary.balanceOf(accounts[1])
    user1SDTBefore = sdt.balanceOf(accounts[1])
    user2xSDTBefore = sanctuary.balanceOf(accounts[2])
    user2SDTBefore = sdt.balanceOf(accounts[2])
    sanctuaryxSDTBefore = sanctuary.totalSupply()
    sanctuarySDTBefore = sdt.balanceOf(sanctuary.address)
    print()
    print("STAKE ON NON-EMPTY SCENE #2")
    print('user0xSDTBefore', user0xSDTBefore / 10**18)
    print('user0SDTBefore', user0SDTBefore / 10**18)
    print('user1xSDTBefore', user1xSDTBefore / 10**18)
    print('user1SDTBefore', user1SDTBefore / 10**18)
    print('user2xSDTBefore', user2xSDTBefore / 10**18)
    print('user2SDTBefore', user2SDTBefore / 10**18)
    print('sanctuaryxSDTBefore', sanctuaryxSDTBefore / 10**18)
    print('sanctuarySDTBefore', sanctuarySDTBefore / 10**18)
    print()
    # only A approves and stakes sdt
    sdt.approve(sanctuary.address, 10**9 * 10**18, deployer)
    # sdt.approve(sanctuary.address, 10**9 * 10**18, {'from': accounts[1]})
    # sdt.approve(sanctuary.address, 10**9 * 10**18, {'from': accounts[2]})
    sanctuary.enter(SDT_STAKE_AMOUNT, deployer)
    # sanctuary.enter(1000 * 10**18, {'from': accounts[1]})
    # sanctuary.enter(1000000 * 10**18, {'from': accounts[2]})

    user0xSDTAfter = sanctuary.balanceOf(deployer["from"])
    user0SDTAfter = sdt.balanceOf(deployer['from'])
    user1xSDTAfter = sanctuary.balanceOf(accounts[1])
    user1SDTAfter = sdt.balanceOf(accounts[1])
    user2xSDTAfter = sanctuary.balanceOf(accounts[2])
    user2SDTAfter = sdt.balanceOf(accounts[2])
    sanctuaryxSDTAfter = sanctuary.totalSupply()
    sanctuarySDTAfter = sdt.balanceOf(sanctuary.address)
    print()
    print('user0xSDTAfter', user0xSDTAfter / 10**18)
    print('user0SDTAfter', user0SDTAfter / 10**18)
    print('user1xSDTAfter', user1xSDTAfter / 10**18)
    print('user1SDTAfter', user1SDTAfter / 10**18)
    print('user2xSDTAfter', user2xSDTAfter / 10**18)
    print('user2SDTAfter', user2SDTAfter / 10**18)
    print('sanctuaryxSDTAfter', sanctuaryxSDTAfter / 10**18)
    print('sanctuarySDTAfter', sanctuarySDTAfter / 10**18)
    print()

    assert sanctuaryxSDTAfter - sanctuaryxSDTBefore == user0xSDTAfter - \
        user0xSDTBefore
    assert user0SDTBefore - user0SDTAfter == sanctuarySDTAfter - sanctuarySDTBefore


def test_unstake_sdt_on_nonempty_sanctuary_scene_2(deployedContracts):
    # A doesn't receive a share from 100k SDT, only B, C do as they stayed during the deposit
    sdt = deployedContracts["sdt"]
    sanctuary = deployedContracts['sanctuary']
    deployer = deployedContracts["deployer"]
    SDT_STAKE_AMOUNT = deployedContracts["SDT_STAKE_AMOUNT"]
    treasuryVault = deployedContracts["treasuryVault"]
    multisig = deployedContracts["multisig"]

    user0xSDTBefore = sanctuary.balanceOf(deployer["from"])
    user0SDTBefore = sdt.balanceOf(deployer['from'])
    user1xSDTBefore = sanctuary.balanceOf(accounts[1])
    user1SDTBefore = sdt.balanceOf(accounts[1])
    user2xSDTBefore = sanctuary.balanceOf(accounts[2])
    user2SDTBefore = sdt.balanceOf(accounts[2])
    sanctuaryxSDTBefore = sanctuary.totalSupply()
    sanctuarySDTBefore = sdt.balanceOf(sanctuary.address)
    print()
    print("UNSTAKE ON NON_EMPTY SCENE #2")
    print('user0xSDTBefore', user0xSDTBefore / 10**18)
    print('user0SDTBefore', user0SDTBefore / 10**18)
    print('user1xSDTBefore', user1xSDTBefore / 10**18)
    print('user1SDTBefore', user1SDTBefore / 10**18)
    print('user2xSDTBefore', user2xSDTBefore / 10**18)
    print('user2SDTBefore', user2SDTBefore / 10**18)
    print('sanctuaryxSDTBefore', sanctuaryxSDTBefore / 10**18)
    print('sanctuarySDTBefore', sanctuarySDTBefore / 10**18)
    print()
    # sdt.transfer(sanctuary.address, 10**5 * 10**18, multisig)
    sanctuary.leave(user1xSDTBefore, {'from': accounts[1]})
    sanctuary.leave(user0xSDTBefore, deployer)
    sanctuary.leave(user2xSDTBefore, {'from': accounts[2]})

    user0xSDTAfter = sanctuary.balanceOf(deployer["from"])
    user0SDTAfter = sdt.balanceOf(deployer['from'])
    user1xSDTAfter = sanctuary.balanceOf(accounts[1])
    user1SDTAfter = sdt.balanceOf(accounts[1])
    user2xSDTAfter = sanctuary.balanceOf(accounts[2])
    user2SDTAfter = sdt.balanceOf(accounts[2])
    sanctuaryxSDTAfter = sanctuary.totalSupply()
    sanctuarySDTAfter = sdt.balanceOf(sanctuary.address)
    print()
    print('user0xSDTAfter', user0xSDTAfter / 10**18)
    print('user0SDTAfter', user0SDTAfter / 10**18)
    print('user1xSDTAfter', user1xSDTAfter / 10**18)
    print('user1SDTAfter', user1SDTAfter / 10**18)
    print('user2xSDTAfter', user2xSDTAfter / 10**18)
    print('user2SDTAfter', user2SDTAfter / 10**18)
    print("SDT 0 rakes", (user0SDTAfter - user0SDTBefore) / 10**18)
    print("SDT 1 rakes", (user1SDTAfter - user1SDTBefore) / 10**18)
    print("SDT 2 rakes", (user2SDTAfter - user2SDTBefore) / 10**18)
    print('sanctuaryxSDTAfter', sanctuaryxSDTAfter / 10**18)
    print('sanctuarySDTAfter', sanctuarySDTAfter / 10**18)
    print()

    assert sanctuaryxSDTBefore - sanctuaryxSDTAfter == user0xSDTBefore - \
        user0xSDTAfter + user1xSDTBefore - \
        user1xSDTAfter + user2xSDTBefore - user2xSDTAfter
    assert user0SDTAfter - user0SDTBefore + user1SDTAfter - user1SDTBefore + \
        user2SDTAfter - user2SDTBefore == sanctuarySDTBefore - sanctuarySDTAfter
    # A receiving max 100 SDT (their original deposit) on claiming
    assert user0SDTAfter - user0SDTBefore <= 100 * 10**18
    assert user1SDTAfter - user1SDTBefore > 0
    assert user2SDTAfter - user2SDTBefore > 0


def test_xSDT_fungibility(deployedContracts):
    sdt = deployedContracts["sdt"]
    sanctuary = deployedContracts['sanctuary']
    deployer = deployedContracts["deployer"]
    SDT_STAKE_AMOUNT = deployedContracts["SDT_STAKE_AMOUNT"]
    treasuryVault = deployedContracts["treasuryVault"]

    # approve and stake sdt
    sdt.approve(sanctuary.address, 10**9 * 10**18, {'from': accounts[3]})
    sanctuary.enter(1000000 * 10**18, {'from': accounts[3]})

    user3xSDTBefore = sanctuary.balanceOf(accounts[3])
    user2xSDTBefore = sanctuary.balanceOf(accounts[2])
    print()
    print("TRANSFER")
    print('user3xSDTBefore', user3xSDTBefore / 10**18)
    print('user2xSDTBefore', user2xSDTBefore / 10**18)
    print()

    sanctuary.transfer(accounts[2], 300000 * 10**18, {'from': accounts[3]})

    user3xSDTAfter = sanctuary.balanceOf(accounts[3])
    user2xSDTAfter = sanctuary.balanceOf(accounts[2])
    print()
    print('user3xSDTAfter', user3xSDTAfter / 10**18)
    print('user2xSDTAfter', user2xSDTAfter / 10**18)
    print()

    assert user3xSDTBefore - user3xSDTAfter == user2xSDTAfter - user2xSDTBefore
